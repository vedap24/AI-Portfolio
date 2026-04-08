import os
import json
import time
import pandas as pd
from io import StringIO
from dotenv import load_dotenv
from google import genai
from models import (
    JobSearchInsights, KeyInsight,
    ChangeRecommendation, BenchmarkComparison
)
from prompts import (
    INSIGHTS_PROMPT,
    FOLLOWUP_PROMPT,
    build_data_summary
)

load_dotenv()

# ── Gemini client ──
gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
GEMINI_MODEL = "gemini-3.1-flash-lite-preview"

# ── Column definitions ──
REQUIRED_COLUMNS = [
    "company", "role", "source",
    "status", "date_applied"
]
OPTIONAL_COLUMNS = [
    "company_size", "industry",
    "notes", "salary_range"
]

# ── Status categories ──
POSITIVE_STATUSES = [
    "Phone Screen",
    "Technical Interview",
    "Final Round",
    "Offer"
]
NEGATIVE_STATUSES = [
    "Rejected", "No Response", "Withdrawn"
]
NEUTRAL_STATUSES = ["Applied", "Pending"]


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

    if not csv_content or \
       not csv_content.strip():
        raise ValueError(
            "CSV content is empty."
        )

    try:
        df = pd.read_csv(
            StringIO(csv_content)
        )
    except Exception as e:
        raise ValueError(
            f"Could not parse CSV: {e}. "
            f"Make sure it's valid CSV format."
        )

    if df.empty:
        raise ValueError(
            "CSV file is empty. "
            "Please add your application data."
        )

    if len(df) < 3:
        raise ValueError(
            f"Only {len(df)} row(s) found. "
            f"Please add at least 3 applications "
            f"for meaningful analysis."
        )

    # Check required columns
    # Case-insensitive check
    df.columns = [
        c.strip().lower()
        for c in df.columns
    ]
    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]
    if missing:
        raise ValueError(
            f"Missing required columns: "
            f"{', '.join(missing)}.\n"
            f"Required columns: "
            f"{', '.join(REQUIRED_COLUMNS)}"
        )

    df = df.copy()

    # Normalize strings
    str_cols = [
        "company", "role",
        "source", "status"
    ]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(
                str
            ).str.strip()

    # Remove completely empty rows
    df = df.dropna(
        subset=["company", "status"],
        how="all"
    )

    if len(df) == 0:
        raise ValueError(
            "No valid data rows found after "
            "cleaning. Check your CSV format."
        )

    # Parse dates safely
    if "date_applied" in df.columns:
        df["date_applied"] = pd.to_datetime(
            df["date_applied"],
            errors="coerce"
        )

    # Add optional columns if missing
    for col in OPTIONAL_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # Fill NaN
    df = df.fillna("")

    # Warn about unknown statuses
    known_statuses = (
        POSITIVE_STATUSES +
        NEGATIVE_STATUSES +
        NEUTRAL_STATUSES
    )
    unknown = df[
        ~df["status"].isin(known_statuses)
    ]["status"].unique()
    if len(unknown) > 0:
        print(
            f"  ⚠️  Unknown statuses: "
            f"{list(unknown)} — "
            f"treating as neutral"
        )

    return df


# ──────────────────────────────────────────
# METRICS ENGINE
# ──────────────────────────────────────────

def calculate_funnel_metrics(
    df: pd.DataFrame
) -> dict:
    total = len(df)
    if total == 0:
        return {
            "total": 0,
            "applied": 0,
            "phone_screen": 0,
            "technical": 0,
            "final_round": 0,
            "offers": 0,
            "got_response": 0,
            "response_rate": 0,
            "interview_rate": 0,
            "offer_rate": 0,
            "ghost_rate": 0,
            "status_counts": {}
        }

    status_counts = df[
        "status"
    ].value_counts().to_dict()

    phone_screen = int(sum(
        df["status"].isin([
            "Phone Screen",
            "Technical Interview",
            "Final Round",
            "Offer"
        ])
    ))
    technical = int(sum(
        df["status"].isin([
            "Technical Interview",
            "Final Round",
            "Offer"
        ])
    ))
    final_round = int(sum(
        df["status"].isin([
            "Final Round", "Offer"
        ])
    ))
    offers = int(sum(
        df["status"] == "Offer"
    ))
    got_response = int(sum(
        ~df["status"].isin([
            "No Response",
            "Applied",
            "Pending"
        ])
    ))
    ghosted = int(sum(
        df["status"] == "No Response"
    ))

    return {
        "total":          total,
        "applied":        total,
        "phone_screen":   phone_screen,
        "technical":      technical,
        "final_round":    final_round,
        "offers":         offers,
        "got_response":   got_response,
        "response_rate":  round(
            (got_response / total) * 100, 1
        ),
        "interview_rate": round(
            (phone_screen / total) * 100, 1
        ),
        "offer_rate":     round(
            (offers / total) * 100, 1
        ),
        "ghost_rate":     round(
            (ghosted / total) * 100, 1
        ),
        "status_counts":  status_counts
    }


def calculate_source_metrics(
    df: pd.DataFrame
) -> dict:
    if "source" not in df.columns:
        return {}

    source_stats = {}
    for source in df["source"].unique():
        if not source or source == "nan":
            continue

        subset = df[df["source"] == source]
        total  = len(subset)
        if total == 0:
            continue

        responses = int(sum(
            ~subset["status"].isin([
                "No Response",
                "Applied",
                "Pending"
            ])
        ))
        interviews = int(sum(
            subset["status"].isin(
                POSITIVE_STATUSES
            )
        ))
        offers = int(sum(
            subset["status"] == "Offer"
        ))

        source_stats[source] = {
            "total":          total,
            "responses":      responses,
            "interviews":     interviews,
            "offers":         offers,
            "response_rate":  round(
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
    if "date_applied" not in df.columns:
        return {}

    df_dated = df[
        df["date_applied"].notna() &
        (df["date_applied"] != "")
    ].copy()

    # Filter valid dates
    if hasattr(
        df_dated["date_applied"], "dt"
    ):
        df_dated = df_dated[
            pd.to_datetime(
                df_dated["date_applied"],
                errors="coerce"
            ).notna()
        ]

    if df_dated.empty:
        return {
            "weekly_data":    [],
            "days_searching": 0,
            "avg_per_week":   0,
            "first_applied":  "",
            "last_applied":   ""
        }

    try:
        df_dated["week"] = pd.to_datetime(
            df_dated["date_applied"]
        ).dt.to_period("W")

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

        first = pd.to_datetime(
            df_dated["date_applied"]
        ).min()
        last  = pd.to_datetime(
            df_dated["date_applied"]
        ).max()

        days = (last - first).days \
            if first != last else 0
        avg  = round(
            len(df_dated) / max(
                days / 7, 1
            ), 1
        )

        return {
            "weekly_data":    weekly_data,
            "days_searching": days,
            "avg_per_week":   avg,
            "first_applied":  str(
                first.date()
            ) if pd.notna(first) else "",
            "last_applied":   str(
                last.date()
            ) if pd.notna(last) else ""
        }

    except Exception as e:
        print(
            f"  ⚠️  Timeline error: {e}"
        )
        return {
            "weekly_data":    [],
            "days_searching": 0,
            "avg_per_week":   0,
            "first_applied":  "",
            "last_applied":   ""
        }


def calculate_company_size_metrics(
    df: pd.DataFrame
) -> dict:
    if "company_size" not in df.columns:
        return {}

    size_stats = {}
    for size in df["company_size"].unique():
        if not size or size in ["", "nan"]:
            continue

        subset = df[df["company_size"] == size]
        total  = len(subset)
        if total == 0:
            continue

        responses = int(sum(
            ~subset["status"].isin([
                "No Response",
                "Applied",
                "Pending"
            ])
        ))

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
    return {
        "funnel":    calculate_funnel_metrics(df),
        "by_source": calculate_source_metrics(df),
        "timeline":  calculate_timeline_metrics(df),
        "by_size":   calculate_company_size_metrics(df),
        "total_apps": len(df),
        "df":         df
    }


# ──────────────────────────────────────────
# INSIGHT ENGINE
# ──────────────────────────────────────────

def generate_insights(
    analysis: dict,
    df: pd.DataFrame
) -> JobSearchInsights:

    data_summary = build_data_summary(
        analysis, df
    )
    prompt = INSIGHTS_PROMPT.format(
        data_summary=data_summary
    )

    try:
        raw = call_gemini(prompt)
        raw = clean_gemini_response(raw)
        data = json.loads(raw)
    except json.JSONDecodeError:
        return _fallback_insights(analysis)
    except Exception as e:
        raise RuntimeError(
            f"Insight generation failed: {e}"
        )

    # Validate score
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
        if not isinstance(
            data.get(field), list
        ):
            data[field] = []

    # Validate key insights
    key_insights = []
    for ki in data.get("key_insights", []):
        if not isinstance(ki, dict):
            continue
        if ki.get("impact") not in \
           ["HIGH", "MEDIUM", "LOW"]:
            ki["impact"] = "MEDIUM"
        if ki.get("category") not in [
            "Source", "Timing", "Volume",
            "Company", "Role"
        ]:
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

    # Validate changes
    changes = []
    for ch in data.get(
        "what_to_change", []
    ):
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

    try:
        return JobSearchInsights(**data)
    except Exception:
        return _fallback_insights(analysis)


def _fallback_insights(
    analysis: dict
) -> JobSearchInsights:
    """Safe fallback when parsing fails."""
    funnel = analysis.get("funnel", {})
    rate   = funnel.get("response_rate", 0)

    return JobSearchInsights(
        headline_insight=(
            "Analysis complete. "
            "Review your data below."
        ),
        performance_score=max(
            1, min(100, int(rate))
        ),
        score_reasoning=(
            f"Based on {rate}% response rate."
        ),
        key_insights=[],
        what_is_working=[
            "You are tracking your applications — "
            "most job seekers don't."
        ],
        what_to_change=[],
        weekly_action_plan=[
            "Review your source breakdown",
            "Follow up on pending applications",
            "Increase referral outreach"
        ],
        benchmark_comparison=BenchmarkComparison(
            your_response_rate=f"{rate}%",
            industry_average="3-13% (LinkedIn 2025)",
            your_vs_average=(
                "above average"
                if rate > 13
                else "at average"
                if rate >= 3
                else "below average"
            ),
            interpretation=(
                "Keep tracking to improve."
            )
        ),
        predicted_timeline=(
            "Continue applying consistently."
        )
    )


def ask_followup(
    question: str,
    analysis: dict,
    df: pd.DataFrame
) -> str:
    if not question or \
       len(question.strip()) < 5:
        raise ValueError(
            "Please ask a specific question "
            "(at least 5 characters)."
        )

    if len(question) > 500:
        raise ValueError(
            "Question too long. Max 500 chars."
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
    df       = load_csv(csv_content)
    analysis = run_full_analysis(df)
    insights = generate_insights(analysis, df)
    return analysis, insights, df


# ───── Tests ─────
if __name__ == "__main__":

    print("\n🧪 Test 1: Full pipeline")
    from sample_data import get_sample_csv
    csv_str = get_sample_csv()
    analysis, insights, df = \
        analyze_job_search(csv_str)
    assert insights.performance_score > 0
    assert len(df) == 35
    print(
        f"  ✅ Score : "
        f"{insights.performance_score}/100"
    )
    print(
        f"     Apps  : {len(df)}"
    )

    print("\n🧪 Test 2: Empty CSV")
    try:
        load_csv("")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 3: Too few rows")
    try:
        load_csv(
            "company,role,source,"
            "status,date_applied\n"
            "Google,Engineer,LinkedIn,"
            "Applied,2025-01-01"
        )
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 4: Missing columns")
    try:
        load_csv(
            "company,role\n"
            "Google,Engineer\n"
            "Meta,Engineer\n"
            "Apple,Engineer"
        )
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 5: Fallback insights")
    fallback = _fallback_insights(
        analysis
    )
    assert fallback.performance_score >= 1
    assert fallback.benchmark_comparison
    print(
        f"  ✅ Fallback score: "
        f"{fallback.performance_score}"
    )

    print("\n🧪 Test 6: Follow-up question")
    ans = ask_followup(
        "Which source is working best?",
        analysis,
        df
    )
    assert len(ans) > 10
    print(
        f"  ✅ Answer: {ans[:80]}..."
    )

    print("\n🧪 Test 7: Short follow-up")
    try:
        ask_followup("hi", analysis, df)
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 8: Source metrics")
    sources = analysis["by_source"]
    assert len(sources) > 0
    best = max(
        sources.items(),
        key=lambda x: x[1]["response_rate"]
    )
    print(
        f"  ✅ Best source: {best[0]} "
        f"({best[1]['response_rate']}%)"
    )

    print("\n✅ All 8 tests passed.")