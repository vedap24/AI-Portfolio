import os
import json
import time
import pandas as pd
from models import (
    JobSearchInsights, KeyInsight,
    ChangeRecommendation, BenchmarkComparison
)
from prompts import (
    INSIGHTS_PROMPT,
    FOLLOWUP_PROMPT,
    build_data_summary
)
from io import StringIO
from dotenv import load_dotenv
from google import genai

load_dotenv()

# ── Gemini client ──
gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
GEMINI_MODEL = "gemini-3.1-flash-lite-preview"

# ── Expected columns ──
REQUIRED_COLUMNS = [
    "company", "role", "source",
    "status", "date_applied"
]

OPTIONAL_COLUMNS = [
    "company_size", "industry",
    "notes", "salary_range"
]

# ── Status definitions ──
POSITIVE_STATUSES = [
    "Phone Screen",
    "Technical Interview",
    "Final Round",
    "Offer"
]

NEGATIVE_STATUSES = [
    "Rejected",
    "No Response",
    "Withdrawn"
]

NEUTRAL_STATUSES = [
    "Applied",
    "Pending"
]


# ──────────────────────────────────────────
# CORE UTILITIES
# ──────────────────────────────────────────

def clean_gemini_response(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = [
            l for l in lines
            if not l.strip().startswith("```")
        ]
        raw = "\n".join(lines).strip()
    return raw


def call_gemini(
    prompt: str,
    retries: int = 3
) -> str:
    last_error = None
    for attempt in range(retries + 1):
        try:
            response = (
                gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt
                )
            )
            return response.text
        except Exception as e:
            error_str = str(e)
            last_error = error_str
            if "429" in error_str or \
               "RESOURCE_EXHAUSTED" in error_str:
                if attempt < retries:
                    print(
                        "⏳ Rate limit. Waiting 40s..."
                    )
                    time.sleep(40)
                    continue
            if attempt < retries:
                time.sleep(2)
                continue
    raise RuntimeError(
        f"Gemini failed: {last_error}"
    )


# ──────────────────────────────────────────
# DATA LOADER + VALIDATOR
# ──────────────────────────────────────────

def load_csv(csv_content: str) -> pd.DataFrame:
    """
    Load and validate CSV data.
    Handles both file uploads and string content.
    """
    try:
        df = pd.read_csv(StringIO(csv_content))
    except Exception as e:
        raise ValueError(
            f"Could not parse CSV: {e}. "
            f"Make sure it's a valid CSV file."
        )

    if df.empty:
        raise ValueError(
            "CSV file is empty. "
            "Please add your application data."
        )

    if len(df) < 3:
        raise ValueError(
            f"Only {len(df)} rows found. "
            f"Please add at least 3 applications."
        )

    # Check required columns
    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]
    if missing:
        raise ValueError(
            f"Missing required columns: "
            f"{', '.join(missing)}.\n"
            f"Required: "
            f"{', '.join(REQUIRED_COLUMNS)}"
        )

    # Clean data
    df = df.copy()

    # Normalize string columns
    str_cols = [
        "company", "role", "source", "status"
    ]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(
                str
            ).str.strip()

    # Parse dates
    try:
        df["date_applied"] = pd.to_datetime(
            df["date_applied"],
            errors="coerce"
        )
    except Exception:
        pass

    # Add optional columns if missing
    for col in OPTIONAL_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # Fill NaN with empty string
    df = df.fillna("")

    return df


# ──────────────────────────────────────────
# METRICS ENGINE
# ──────────────────────────────────────────

def calculate_funnel_metrics(
    df: pd.DataFrame
) -> dict:
    """
    Calculate application funnel metrics.

    Funnel stages:
    Applied → Phone Screen → Technical →
    Final Round → Offer

    Response rate = any positive status / total
    """
    total = len(df)

    # Count by status
    status_counts = df["status"].value_counts(
    ).to_dict()

    # Funnel stages
    applied = total
    phone_screen = sum(
        df["status"].isin([
            "Phone Screen",
            "Technical Interview",
            "Final Round",
            "Offer"
        ])
    )
    technical = sum(
        df["status"].isin([
            "Technical Interview",
            "Final Round",
            "Offer"
        ])
    )
    final_round = sum(
        df["status"].isin([
            "Final Round", "Offer"
        ])
    )
    offers = sum(df["status"] == "Offer")

    # Response rate = got any response
    # (not "No Response" or "Applied")
    got_response = sum(
        ~df["status"].isin([
            "No Response", "Applied", "Pending"
        ])
    )
    response_rate = round(
        (got_response / total) * 100, 1
    ) if total > 0 else 0

    # Interview rate
    interview_rate = round(
        (phone_screen / total) * 100, 1
    ) if total > 0 else 0

    # Offer rate
    offer_rate = round(
        (offers / total) * 100, 1
    ) if total > 0 else 0

    # Ghosted rate
    ghosted = sum(df["status"] == "No Response")
    ghost_rate = round(
        (ghosted / total) * 100, 1
    ) if total > 0 else 0

    return {
        "total":           total,
        "applied":         applied,
        "phone_screen":    phone_screen,
        "technical":       technical,
        "final_round":     final_round,
        "offers":          offers,
        "got_response":    got_response,
        "response_rate":   response_rate,
        "interview_rate":  interview_rate,
        "offer_rate":      offer_rate,
        "ghost_rate":      ghost_rate,
        "status_counts":   status_counts
    }


def calculate_source_metrics(
    df: pd.DataFrame
) -> dict:
    """
    Break down performance by source.

    Key insight for job seekers:
    Which channel gives the best
    response rate?
    """
    if "source" not in df.columns:
        return {}

    source_stats = {}
    for source in df["source"].unique():
        if not source or source == "":
            continue

        subset = df[df["source"] == source]
        total  = len(subset)

        if total == 0:
            continue

        responses = sum(
            ~subset["status"].isin([
                "No Response",
                "Applied",
                "Pending"
            ])
        )
        interviews = sum(
            subset["status"].isin(
                POSITIVE_STATUSES
            )
        )
        offers = sum(
            subset["status"] == "Offer"
        )

        source_stats[source] = {
            "total":         total,
            "responses":     responses,
            "interviews":    interviews,
            "offers":        offers,
            "response_rate": round(
                (responses / total) * 100, 1
            ),
            "interview_rate": round(
                (interviews / total) * 100, 1
            )
        }

    return source_stats


def calculate_timeline_metrics(
    df: pd.DataFrame
) -> dict:
    """
    Analyze application volume over time.
    Helps identify pacing and momentum.
    """
    if "date_applied" not in df.columns:
        return {}

    df_dated = df[
        df["date_applied"].notna()
    ].copy()

    if df_dated.empty:
        return {}

    # Weekly application counts
    df_dated["week"] = df_dated[
        "date_applied"
    ].dt.to_period("W")

    weekly = df_dated.groupby(
        "week"
    ).size().reset_index(name="count")

    weekly_data = [
        {
            "week":  str(row["week"]),
            "count": int(row["count"])
        }
        for _, row in weekly.iterrows()
    ]

    # Days since first application
    first_app = df_dated["date_applied"].min()
    last_app  = df_dated["date_applied"].max()
    days_searching = (
        last_app - first_app
    ).days if first_app != last_app else 0

    # Average applications per week
    avg_per_week = round(
        len(df_dated) / max(
            days_searching / 7, 1
        ), 1
    )

    return {
        "weekly_data":     weekly_data,
        "days_searching":  days_searching,
        "avg_per_week":    avg_per_week,
        "first_applied":   str(
            first_app.date()
        ) if pd.notna(first_app) else "",
        "last_applied":    str(
            last_app.date()
        ) if pd.notna(last_app) else ""
    }


def calculate_company_size_metrics(
    df: pd.DataFrame
) -> dict:
    """
    Break down performance by company size.
    Large vs Mid vs Small — where do
    you get better traction?
    """
    if "company_size" not in df.columns:
        return {}

    size_stats = {}
    for size in df["company_size"].unique():
        if not size or size == "":
            continue

        subset = df[df["company_size"] == size]
        total  = len(subset)

        if total == 0:
            continue

        responses = sum(
            ~subset["status"].isin([
                "No Response",
                "Applied",
                "Pending"
            ])
        )

        size_stats[size] = {
            "total":         total,
            "responses":     responses,
            "response_rate": round(
                (responses / total) * 100, 1
            )
        }

    return size_stats


def run_full_analysis(
    df: pd.DataFrame
) -> dict:
    """
    Run all metric calculations.
    Returns comprehensive analysis dict.
    """
    return {
        "funnel":       calculate_funnel_metrics(df),
        "by_source":    calculate_source_metrics(df),
        "timeline":     calculate_timeline_metrics(df),
        "by_size":      calculate_company_size_metrics(df),
        "total_apps":   len(df),
        "df":           df  # Keep for charting
    }

def generate_insights(
    analysis: dict,
    df: pd.DataFrame
) -> JobSearchInsights:
    """
    Send analysis data to Gemini
    and get personalized insights.

    Why LLM for insights not just rules:
    Patterns interact in complex ways.
    "Referral rate is high but volume is low"
    requires reasoning, not just thresholds.
    LLM synthesizes multiple signals
    into coherent, prioritized advice.
    """
    data_summary = build_data_summary(
        analysis, df
    )

    prompt = INSIGHTS_PROMPT.format(
        data_summary=data_summary
    )

    raw = call_gemini(prompt)
    raw = clean_gemini_response(raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError(
            "Failed to parse insights. "
            "Please try again."
        )

    # Validate performance score
    try:
        score = int(
            data.get("performance_score", 50)
        )
        data["performance_score"] = max(
            1, min(100, score)
        )
    except (ValueError, TypeError):
        data["performance_score"] = 50

    # Validate strings
    for field in [
        "headline_insight",
        "score_reasoning",
        "predicted_timeline"
    ]:
        if not data.get(field):
            data[field] = "Insufficient data."

    # Validate lists
    for field in [
        "what_is_working",
        "weekly_action_plan"
    ]:
        if not isinstance(data.get(field), list):
            data[field] = []

    # Validate key insights
    key_insights = []
    valid_impacts = ["HIGH", "MEDIUM", "LOW"]
    valid_cats = [
        "Source", "Timing", "Volume",
        "Company", "Role"
    ]
    for ki in data.get("key_insights", []):
        if not isinstance(ki, dict):
            continue
        if ki.get("impact") not in valid_impacts:
            ki["impact"] = "MEDIUM"
        if ki.get("category") not in valid_cats:
            ki["category"] = "Source"
        for f in ["insight", "data_point"]:
            if not ki.get(f):
                ki[f] = "No data"
        try:
            key_insights.append(
                KeyInsight(**ki)
            )
        except Exception:
            continue
    data["key_insights"] = key_insights

    # Validate change recommendations
    changes = []
    for ch in data.get("what_to_change", []):
        if not isinstance(ch, dict):
            continue
        for f in [
            "problem", "evidence",
            "action", "expected_impact"
        ]:
            if not ch.get(f):
                ch[f] = "Review manually."
        try:
            changes.append(
                ChangeRecommendation(**ch)
            )
        except Exception:
            continue
    data["what_to_change"] = changes

    # Validate benchmark
    bc = data.get(
        "benchmark_comparison", {}
    )
    if not isinstance(bc, dict):
        bc = {}
    for f in [
        "your_response_rate",
        "industry_average",
        "your_vs_average",
        "interpretation"
    ]:
        if not bc.get(f):
            bc[f] = "Unknown"
    data["benchmark_comparison"] = \
        BenchmarkComparison(**bc)

    return JobSearchInsights(**data)


def ask_followup(
    question: str,
    analysis: dict,
    df: pd.DataFrame
) -> str:
    """
    Answer a follow-up question about
    the job search data.
    Returns plain text answer.
    """
    if not question or \
       len(question.strip()) < 5:
        raise ValueError(
            "Please ask a specific question."
        )

    data_summary = build_data_summary(
        analysis, df
    )

    prompt = FOLLOWUP_PROMPT.format(
        data_summary=data_summary,
        question=question
    )

    return call_gemini(prompt)


def analyze_job_search(
    csv_content: str
) -> tuple:
    """
    Full pipeline:
    CSV → Load → Analyze → Insights
    Returns (analysis_dict, insights, df)
    """
    # Load and validate
    df = load_csv(csv_content)

    # Run analysis
    analysis = run_full_analysis(df)

    # Generate AI insights
    insights = generate_insights(analysis, df)

    return analysis, insights, df


# ───── Quick tests ─────
if __name__ == "__main__":

    print("\n🧪 Test 1: Full pipeline")
    from sample_data import get_sample_csv
    csv_str = get_sample_csv()

    analysis, insights, df = \
        analyze_job_search(csv_str)

    print(
        f"  ✅ Score    : "
        f"{insights.performance_score}/100"
    )
    print(
        f"     Headline : "
        f"{insights.headline_insight[:80]}..."
    )
    print(
        f"     Insights : "
        f"{len(insights.key_insights)}"
    )
    print(
        f"     Actions  : "
        f"{len(insights.what_to_change)}"
    )
    print(
        f"     Timeline : "
        f"{insights.predicted_timeline}"
    )

    print(
        f"\n  Benchmark:"
    )
    bc = insights.benchmark_comparison
    print(
        f"     Your rate   : "
        f"{bc.your_response_rate}"
    )
    print(
        f"     Industry avg: "
        f"{bc.industry_average}"
    )
    print(
        f"     vs Average  : "
        f"{bc.your_vs_average}"
    )

    if insights.what_to_change:
        print(
            f"\n  Top action:"
        )
        top = insights.what_to_change[0]
        print(f"     Problem: {top.problem}")
        print(f"     Action : {top.action}")

    print("\n🧪 Test 2: Follow-up question")
    answer = ask_followup(
        "Which source should I focus on most?",
        analysis,
        df
    )
    print(
        f"  ✅ Answer: {answer[:120]}..."
    )

    print("\n🧪 Test 3: Input validation")
    try:
        load_csv(
            "company,role\nGoogle,Engineer"
        )
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n✅ All tests passed.")

