import os
import json
import time
from dotenv import load_dotenv
from tavily import TavilyClient
from google import genai
from models import (
    CompetitiveBrief, CompanySnapshot,
    KeySignal, RecommendedAction
)
from prompts import (
    SYNTHESIS_PROMPT,
    COMPANY_PROFILE_PROMPT
)

load_dotenv()

# ── Clients ──
tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)
gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
GEMINI_MODEL = "gemini-3.1-flash-lite-preview"


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
        f"Gemini failed after {retries + 1} "
        f"attempts: {last_error}"
    )


def validate_inputs(
    your_company: str,
    competitors: list
) -> None:
    """Validate all inputs before running agent."""

    if not your_company or \
       not your_company.strip():
        raise ValueError(
            "Please enter your company name."
        )

    if len(your_company.strip()) < 2:
        raise ValueError(
            "Company name too short. "
            "Please enter a valid company name."
        )

    if len(your_company.strip()) > 100:
        raise ValueError(
            "Company name too long. "
            "Max 100 characters."
        )

    if not competitors:
        raise ValueError(
            "Please add at least one competitor."
        )

    if len(competitors) > 4:
        raise ValueError(
            "Maximum 4 competitors at a time "
            "to stay within API limits."
        )

    for comp in competitors:
        if len(comp.strip()) < 2:
            raise ValueError(
                f"Competitor name '{comp}' is too short. "
                f"Please enter a valid company name."
            )

    # Check for duplicates
    all_names = [your_company.strip().lower()] + [
        c.strip().lower() for c in competitors
    ]
    if len(all_names) != len(set(all_names)):
        raise ValueError(
            "Your company and competitors must "
            "all be different names."
        )


# ──────────────────────────────────────────
# STEP 1 — QUERY PLANNER
# ──────────────────────────────────────────

def plan_search_queries(
    your_company: str,
    competitors: list
) -> dict:
    competitors_str = ", ".join(competitors)
    prompt = f"""
You are a competitive intelligence analyst.
You need to research these companies:

Your company: {your_company}
Competitors: {competitors_str}

Plan exactly 8 search queries that will give
the most useful competitive intelligence.

Return JSON ONLY. No explanation. Just JSON.

{{
  "queries": [
    {{
      "query": "<exact search query to run>",
      "purpose": "<what intelligence this reveals>",
      "target_company": "<which company this is about>"
    }}
  ],
  "research_focus": [
    "<key area 1>",
    "<key area 2>",
    "<key area 3>"
  ]
}}

Include queries about:
- Recent product launches or updates
- Pricing changes
- Funding or business news
- Customer feedback
- Strategic moves or partnerships
"""

    try:
        raw = call_gemini(prompt)
        raw = clean_gemini_response(raw)
        data = json.loads(raw)

        if not isinstance(data.get("queries"), list):
            data["queries"] = []
        if not isinstance(
            data.get("research_focus"), list
        ):
            data["research_focus"] = []

        # Ensure max 8 queries
        data["queries"] = data["queries"][:8]

        # Validate each query
        valid_queries = []
        for q in data["queries"]:
            if isinstance(q, dict) and q.get("query"):
                q.setdefault(
                    "purpose", "General research"
                )
                q.setdefault(
                    "target_company", your_company
                )
                valid_queries.append(q)

        data["queries"] = valid_queries

        if not data["queries"]:
            raise ValueError("No valid queries planned")

        print(
            f"🧠 Agent planned "
            f"{len(data['queries'])} search queries"
        )
        return data

    except (json.JSONDecodeError, ValueError):
        # Fallback queries
        print("⚠️  Using fallback queries")
        basic = []
        for comp in [your_company] + competitors:
            basic.append({
                "query": f"{comp} latest news 2025",
                "purpose": "Recent updates",
                "target_company": comp
            })
            basic.append({
                "query": (
                    f"{comp} product features pricing"
                ),
                "purpose": "Product intelligence",
                "target_company": comp
            })
        return {
            "queries": basic[:8],
            "research_focus": [
                "Recent news",
                "Pricing",
                "Product features"
            ]
        }


# ──────────────────────────────────────────
# STEP 2 — WEB RESEARCHER
# ──────────────────────────────────────────

def execute_searches(
    queries: list,
    on_progress=None
) -> list:
    all_results = []

    for i, query_plan in enumerate(queries):
        query  = query_plan.get("query", "")
        purpose = query_plan.get("purpose", "")
        target = query_plan.get(
            "target_company", "Unknown"
        )

        if not query:
            continue

        if on_progress:
            on_progress(
                i + 1, len(queries),
                query, target
            )

        print(
            f"🔍 ({i+1}/{len(queries)}): "
            f"{query[:50]}..."
        )

        try:
            results = tavily.search(
                query=query,
                max_results=3,
                search_depth="basic"
            )

            for result in results.get(
                "results", []
            ):
                content = result.get("content", "")
                if len(content) < 30:
                    continue
                all_results.append({
                    "query": query,
                    "purpose": purpose,
                    "target_company": target,
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": content[:500],
                    "score": round(
                        result.get("score", 0), 3
                    )
                })

            time.sleep(0.5)

        except Exception as e:
            error_str = str(e)
            if "401" in error_str or \
               "unauthorized" in error_str.lower():
                raise RuntimeError(
                    "Invalid Tavily API key. "
                    "Check your .env file."
                )
            elif "429" in error_str:
                print(
                    "⚠️  Tavily rate limit — "
                    "waiting 5s..."
                )
                time.sleep(5)
                continue
            else:
                print(f"⚠️  Search failed: {e}")
                continue

    if not all_results:
        raise RuntimeError(
            "No search results returned. "
            "Check your Tavily API key and "
            "internet connection."
        )

    print(
        f"✅ Collected {len(all_results)} results "
        f"from {len(queries)} searches"
    )
    return all_results


# ──────────────────────────────────────────
# STEP 3 — FILTER
# ──────────────────────────────────────────

def filter_relevant_results(
    results: list,
    your_company: str,
    competitors: list
) -> list:
    all_companies = [your_company] + competitors
    all_lower = [c.lower() for c in all_companies]

    filtered = []
    seen_urls = set()

    for result in results:
        url = result.get("url", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)

        content = result.get("content", "")
        if len(content) < 50:
            continue

        if result.get("score", 0) < 0.05:
            continue

        content_lower = content.lower()
        title_lower = result.get(
            "title", ""
        ).lower()

        mentions = any(
            c in content_lower or c in title_lower
            for c in all_lower
        )

        if mentions or result.get("score", 0) > 0.4:
            filtered.append(result)

    print(
        f"✅ Filtered: {len(filtered)} relevant "
        f"(removed {len(results) - len(filtered)})"
    )

    # If filtering too aggressive, return all
    if len(filtered) < 3 and results:
        print(
            "⚠️  Too few after filter — "
            "using all results"
        )
        return results[:15]

    return filtered


# ──────────────────────────────────────────
# STEP 4 — SYNTHESIS
# ──────────────────────────────────────────

def format_results_for_prompt(
    results: list,
    max_results: int = 15
) -> str:
    sorted_results = sorted(
        results,
        key=lambda x: x.get("score", 0),
        reverse=True
    )[:max_results]

    formatted = []
    for i, r in enumerate(sorted_results, 1):
        formatted.append(
            f"[Result {i}]\n"
            f"Company: {r.get('target_company', '')}\n"
            f"Title: {r.get('title', '')}\n"
            f"Content: {r.get('content', '')}\n"
            f"Source: {r.get('url', '')}"
        )
    return "\n\n---\n\n".join(formatted)


def validate_company_snapshot(data: dict) -> dict:
    valid_threats = ["HIGH", "MEDIUM", "LOW"]
    valid_momentum = ["Growing", "Stable", "Declining"]

    if data.get("threat_level") not in valid_threats:
        data["threat_level"] = "MEDIUM"
    if data.get("momentum") not in valid_momentum:
        data["momentum"] = "Stable"

    for field in [
        "recent_moves", "strengths", "weaknesses"
    ]:
        if not isinstance(data.get(field), list):
            data[field] = []

    if not isinstance(
        data.get("is_your_company"), bool
    ):
        data["is_your_company"] = False

    for f in ["company_name", "current_position"]:
        if not data.get(f):
            data[f] = "Unknown"

    return data


def synthesize_brief(
    research_data: dict
) -> CompetitiveBrief:
    your_company = research_data["your_company"]
    competitors  = research_data["competitors"]
    filtered     = research_data["filtered_results"]
    focus        = research_data.get(
        "research_focus", []
    )

    if not filtered:
        raise ValueError(
            "No search results to synthesize. "
            "Try different company names."
        )

    results_text = format_results_for_prompt(filtered)
    prompt = SYNTHESIS_PROMPT.format(
        your_company=your_company,
        competitors=", ".join(competitors),
        research_focus=", ".join(focus),
        results=results_text
    )

    print("🤖 Synthesizing brief...")

    try:
        raw = call_gemini(prompt)
        raw = clean_gemini_response(raw)
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError(
            "Failed to parse synthesis. "
            "Please try again."
        )

    # Validate all fields
    if not data.get("executive_summary"):
        data["executive_summary"] = (
            "Insufficient data for analysis."
        )

    # Company snapshots
    if not isinstance(
        data.get("company_snapshots"), list
    ):
        data["company_snapshots"] = []

    validated_snaps = []
    for snap in data["company_snapshots"]:
        if isinstance(snap, dict):
            snap = validate_company_snapshot(snap)
            try:
                validated_snaps.append(
                    CompanySnapshot(**snap)
                )
            except Exception:
                continue
    data["company_snapshots"] = validated_snaps

    # Key signals
    if not isinstance(
        data.get("key_signals"), list
    ):
        data["key_signals"] = []

    validated_signals = []
    for sig in data["key_signals"]:
        if isinstance(sig, dict):
            if sig.get("urgency") not in \
               ["HIGH", "MEDIUM", "LOW"]:
                sig["urgency"] = "MEDIUM"
            for f in [
                "signal", "company", "implication"
            ]:
                if not sig.get(f):
                    sig[f] = "Unknown"
            try:
                validated_signals.append(
                    KeySignal(**sig)
                )
            except Exception:
                continue
    data["key_signals"] = validated_signals

    # Recommended actions
    if not isinstance(
        data.get("recommended_actions"), list
    ):
        data["recommended_actions"] = []

    valid_tf = [
        "immediately",
        "this month",
        "this quarter"
    ]
    validated_actions = []
    for act in data["recommended_actions"]:
        if isinstance(act, dict):
            if act.get("timeframe") not in valid_tf:
                act["timeframe"] = "this month"
            for f in ["action", "reason"]:
                if not act.get(f):
                    act[f] = "Review manually."
            try:
                validated_actions.append(
                    RecommendedAction(**act)
                )
            except Exception:
                continue
    data["recommended_actions"] = validated_actions

    # List fields
    for f in ["market_trends", "watch_list"]:
        if not isinstance(data.get(f), list):
            data[f] = []

    if not data.get("data_freshness"):
        data["data_freshness"] = "Recent"

    return CompetitiveBrief(
        your_company=your_company,
        competitors=competitors,
        executive_summary=data["executive_summary"],
        company_snapshots=data["company_snapshots"],
        key_signals=data["key_signals"],
        market_trends=data["market_trends"],
        recommended_actions=data[
            "recommended_actions"
        ],
        watch_list=data["watch_list"],
        data_freshness=data["data_freshness"],
        queries_run=research_data.get(
            "queries_run", 0
        ),
        results_analyzed=research_data.get(
            "filtered_count", 0
        )
    )


# ──────────────────────────────────────────
# FULL PIPELINE
# ──────────────────────────────────────────

def run_research_agent(
    your_company: str,
    competitors: list,
    on_progress=None
) -> dict:
    print(f"\n🤖 CompeteAI Agent Starting...")
    print(f"   Company     : {your_company}")
    print(
        f"   Competitors : {', '.join(competitors)}"
    )

    # Step 1: Plan
    print("\n📋 Step 1/3 — Planning queries...")
    plan = plan_search_queries(
        your_company, competitors
    )

    # Step 2: Search
    print("\n🔍 Step 2/3 — Executing searches...")
    raw_results = execute_searches(
        plan["queries"],
        on_progress=on_progress
    )

    # Step 3: Filter
    print("\n🔎 Step 3/3 — Filtering results...")
    filtered = filter_relevant_results(
        raw_results, your_company, competitors
    )

    return {
        "your_company": your_company,
        "competitors": competitors,
        "research_focus": plan.get(
            "research_focus", []
        ),
        "queries_run": len(plan["queries"]),
        "raw_results_count": len(raw_results),
        "filtered_results": filtered,
        "filtered_count": len(filtered)
    }


def generate_competitive_brief(
    your_company: str,
    competitors: list,
    on_progress=None
) -> CompetitiveBrief:

    # Validate
    validate_inputs(your_company, competitors)

    # Run agent
    research = run_research_agent(
        your_company.strip(),
        [c.strip() for c in competitors
         if c.strip()],
        on_progress=on_progress
    )

    # Synthesize
    return synthesize_brief(research)


# ───── Tests ─────
if __name__ == "__main__":

    print("\n🧪 Test 1: Input validation — empty company")
    try:
        validate_inputs("", ["Obsidian"])
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 2: Input validation — no competitors")
    try:
        validate_inputs("Notion", [])
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 3: Input validation — duplicate")
    try:
        validate_inputs("Notion", ["notion"])
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 4: Too many competitors")
    try:
        validate_inputs(
            "Notion",
            ["A", "B", "C", "D", "E"]
        )
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 5: Full pipeline")
    brief = generate_competitive_brief(
        your_company="Notion",
        competitors=["Obsidian", "Coda"]
    )
    print(f"  ✅ Snapshots : "
          f"{len(brief.company_snapshots)}")
    print(f"  ✅ Signals   : "
          f"{len(brief.key_signals)}")
    print(f"  ✅ Actions   : "
          f"{len(brief.recommended_actions)}")
    print(f"  ✅ Queries   : {brief.queries_run}")

    print("\n✅ All tests passed.")