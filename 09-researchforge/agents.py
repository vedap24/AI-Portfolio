import json
import time
from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


# ──────────────────────────────────────────
# AGENT STATE
# Shared state passed between all agents.
# Each agent reads from state and writes back.
# This is the manual equivalent of LangGraph
# StateGraph — same concept, no framework.
# ──────────────────────────────────────────

def create_initial_state(query: str) -> dict:
    """
    Initialize shared agent state.
    Every agent reads and writes to this dict.
    """
    return {
        "query":          query,
        "sub_questions":  [],
        "search_results": [],
        "verified_facts": [],
        "final_report":   None,
        "agent_logs":     [],
        "status":         "initialized",
        "error":          None
    }


def log_agent(
    state: dict,
    agent: str,
    message: str
) -> None:
    """Add a log entry to state for UI display."""
    entry = {
        "agent":     agent,
        "message":   message,
        "timestamp": time.time()
    }
    state["agent_logs"].append(entry)
    print(f"  [{agent}] {message}")


# ──────────────────────────────────────────
# AGENT 1 — PLANNER
# Breaks the query into sub-questions
# ──────────────────────────────────────────

def run_planner_agent(
    state: dict,
    gemini_call_fn
) -> dict:
    """
    Planner Agent:
    Takes the user's query and breaks it into
    3-5 specific sub-questions that together
    fully answer the main question.

    Why this matters:
    A single search for "LLMs in production"
    returns generic results.
    5 targeted searches return specific,
    complementary information that can be
    synthesized into a real answer.

    This is the agent's intelligence —
    knowing WHAT to search is more valuable
    than knowing HOW to search.
    """
    log_agent(
        state, "PLANNER",
        f"Breaking down query: '{state['query']}'"
    )
    state["status"] = "planning"

    prompt = f"""
You are a research planning agent.

A user wants to research this topic:
"{state['query']}"

Your job: break this into exactly 4 specific
sub-questions that together give a complete
answer to the main query.

Return JSON ONLY. No explanation.

{{
  "sub_questions": [
    {{
      "question": "<specific sub-question>",
      "search_query": "<optimized search query>",
      "purpose": "<what this reveals>"
    }}
  ],
  "research_angle": "<overall approach to this research>"
}}

Rules:
- Sub-questions must be SPECIFIC not generic
- Each covers a different angle
- Together they fully answer the main query
- Search queries should be 4-8 words
- Avoid yes/no questions
"""

    try:
        raw = gemini_call_fn(prompt)
        raw = raw.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            lines = [
                l for l in lines
                if not l.strip().startswith("```")
            ]
            raw = "\n".join(lines).strip()

        data = json.loads(raw)

        questions = data.get("sub_questions", [])

        # Validate each question
        valid_questions = []
        for q in questions:
            if isinstance(q, dict) and \
               q.get("question") and \
               q.get("search_query"):
                q.setdefault(
                    "purpose", "General research"
                )
                valid_questions.append(q)

        if not valid_questions:
            raise ValueError(
                "No valid sub-questions generated"
            )

        state["sub_questions"] = \
            valid_questions[:4]
        state["research_angle"] = data.get(
            "research_angle", "General research"
        )

        log_agent(
            state, "PLANNER",
            f"Generated {len(state['sub_questions'])}"
            f" sub-questions"
        )

        for i, q in enumerate(
            state["sub_questions"], 1
        ):
            log_agent(
                state, "PLANNER",
                f"Q{i}: {q['question']}"
            )

        return state

    except (json.JSONDecodeError, ValueError) as e:
        # Fallback: create basic sub-questions
        log_agent(
            state, "PLANNER",
            f"⚠️ Planning failed: {e} — "
            f"using fallback questions"
        )

        query = state["query"]
        state["sub_questions"] = [
            {
                "question": f"What is {query}?",
                "search_query": (
                    f"{query} overview explanation"
                ),
                "purpose": "Background"
            },
            {
                "question": (
                    f"What are the key challenges "
                    f"with {query}?"
                ),
                "search_query": (
                    f"{query} challenges problems"
                ),
                "purpose": "Pain points"
            },
            {
                "question": (
                    f"What are best practices "
                    f"for {query}?"
                ),
                "search_query": (
                    f"{query} best practices 2025"
                ),
                "purpose": "Solutions"
            },
            {
                "question": (
                    f"What is the future of {query}?"
                ),
                "search_query": (
                    f"{query} future trends 2025 2026"
                ),
                "purpose": "Future outlook"
            }
        ]
        state["research_angle"] = (
            "General overview research"
        )
        return state


# ──────────────────────────────────────────
# AGENT 2 — RESEARCHER
# Executes searches for each sub-question
# ──────────────────────────────────────────

def run_researcher_agent(
    state: dict,
    on_search_progress=None
) -> dict:
    """
    Researcher Agent:
    Takes the sub-questions from the Planner
    and executes web searches for each one.

    Collects raw search results with metadata.
    Does NOT synthesize — that's the Writer's job.
    Single responsibility principle.
    """
    log_agent(
        state, "RESEARCHER",
        f"Executing "
        f"{len(state['sub_questions'])} searches"
    )
    state["status"] = "researching"

    all_results = []

    for i, sub_q in enumerate(
        state["sub_questions"]
    ):
        search_query = sub_q["search_query"]
        question     = sub_q["question"]
        purpose      = sub_q["purpose"]

        log_agent(
            state, "RESEARCHER",
            f"Searching ({i+1}/"
            f"{len(state['sub_questions'])}): "
            f"{search_query}"
        )

        if on_search_progress:
            on_search_progress(
                i + 1,
                len(state["sub_questions"]),
                search_query
            )

        try:
            results = tavily.search(
                query=search_query,
                max_results=4,
                search_depth="basic"
            )

            for result in results.get(
                "results", []
            ):
                content = result.get(
                    "content", ""
                )
                if len(content) < 50:
                    continue

                all_results.append({
                    "sub_question": question,
                    "purpose":      purpose,
                    "title":  result.get(
                        "title", ""
                    ),
                    "content": content[:600],
                    "url":    result.get(
                        "url", ""
                    ),
                    "score":  round(
                        result.get("score", 0), 3
                    )
                })

            time.sleep(0.5)

        except Exception as e:
            log_agent(
                state, "RESEARCHER",
                f"⚠️ Search failed for "
                f"'{search_query}': {e}"
            )
            continue

    if not all_results:
        state["error"] = (
            "No search results returned. "
            "Check your Tavily API key."
        )
        state["status"] = "failed"
        return state

    state["search_results"] = all_results

    log_agent(
        state, "RESEARCHER",
        f"Collected {len(all_results)} "
        f"raw results"
    )

    return state


# ──────────────────────────────────────────
# AGENT 3 — FACT CHECKER
# Filters and verifies search results
# ──────────────────────────────────────────

def run_fact_checker_agent(
    state: dict,
    gemini_call_fn
) -> dict:
    """
    Fact Checker Agent:
    Reviews the raw search results and:
    1. Removes duplicates and noise
    2. Identifies contradicting information
    3. Rates source reliability
    4. Flags uncertain claims

    Why this matters:
    Web search returns noisy, sometimes
    contradictory results.
    A research brief built on bad data
    is worse than no brief at all.
    The fact checker is the quality gate.
    """
    log_agent(
        state, "FACT_CHECKER",
        f"Verifying {len(state['search_results'])}"
        f" search results"
    )
    state["status"] = "fact_checking"

    if not state["search_results"]:
        state["error"] = (
            "No search results to verify."
        )
        return state

    # Format results for prompt
    results_text = ""
    for i, r in enumerate(
        state["search_results"][:12], 1
    ):
        results_text += (
            f"\n[Result {i}]\n"
            f"Sub-question: {r['sub_question']}\n"
            f"Title: {r['title']}\n"
            f"Content: {r['content']}\n"
            f"Source: {r['url']}\n"
            f"Relevance: {r['score']}\n"
        )

    prompt = f"""
You are a fact-checking agent reviewing
research results for accuracy and reliability.

Original query: "{state['query']}"

Review these search results and identify:
1. The most reliable and relevant facts
2. Any contradictions between sources
3. Claims that need more verification

Return JSON ONLY.

{{
  "verified_facts": [
    {{
      "fact": "<verified factual claim>",
      "confidence": "<HIGH | MEDIUM | LOW>",
      "source_url": "<url this came from>",
      "sub_question": "<which sub-question this answers>"
    }}
  ],
  "contradictions": [
    "<contradiction found between sources>"
  ],
  "knowledge_gaps": [
    "<topic not well covered by results>"
  ],
  "overall_source_quality": "<HIGH | MEDIUM | LOW>"
}}

SEARCH RESULTS:
{results_text}
"""

    try:
        raw = gemini_call_fn(prompt)
        raw = raw.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            lines = [
                l for l in lines
                if not l.strip().startswith("```")
            ]
            raw = "\n".join(lines).strip()

        data = json.loads(raw)

        facts = data.get("verified_facts", [])
        valid_facts = []
        for f in facts:
            if isinstance(f, dict) and \
               f.get("fact"):
                f.setdefault(
                    "confidence", "MEDIUM"
                )
                f.setdefault("source_url", "")
                f.setdefault(
                    "sub_question", "General"
                )
                valid_facts.append(f)

        state["verified_facts"] = valid_facts
        state["contradictions"] = data.get(
            "contradictions", []
        )
        state["knowledge_gaps"] = data.get(
            "knowledge_gaps", []
        )
        state["source_quality"] = data.get(
            "overall_source_quality", "MEDIUM"
        )

        log_agent(
            state, "FACT_CHECKER",
            f"Verified {len(valid_facts)} facts | "
            f"Source quality: "
            f"{state['source_quality']}"
        )

        if state.get("contradictions"):
            log_agent(
                state, "FACT_CHECKER",
                f"⚠️ Found "
                f"{len(state['contradictions'])} "
                f"contradictions"
            )

        return state

    except json.JSONDecodeError:
        # Fallback: use raw results as facts
        log_agent(
            state, "FACT_CHECKER",
            "⚠️ Fact check parse failed — "
            "using raw results directly"
        )

        fallback_facts = []
        for r in state["search_results"][:8]:
            if r.get("score", 0) > 0.3:
                fallback_facts.append({
                    "fact": r["content"][:200],
                    "confidence": "MEDIUM",
                    "source_url": r["url"],
                    "sub_question": r["sub_question"]
                })

        state["verified_facts"] = fallback_facts
        state["contradictions"] = []
        state["knowledge_gaps"] = []
        state["source_quality"] = "MEDIUM"
        return state


# ──────────────────────────────────────────
# AGENT 4 — WRITER
# Synthesizes everything into final report
# ──────────────────────────────────────────

def run_writer_agent(
    state: dict,
    gemini_call_fn
) -> dict:
    """
    Writer Agent:
    Takes verified facts from the Fact Checker
    and synthesizes them into a structured
    research brief.

    This agent does NOT search —
    it only writes from verified facts.
    Clean separation of concerns.
    """
    log_agent(
        state, "WRITER",
        f"Writing report from "
        f"{len(state['verified_facts'])} "
        f"verified facts"
    )
    state["status"] = "writing"

    if not state["verified_facts"]:
        state["error"] = (
            "No verified facts to write from."
        )
        state["status"] = "failed"
        return state

    # Format facts for prompt
    facts_text = ""
    for i, f in enumerate(
        state["verified_facts"][:15], 1
    ):
        facts_text += (
            f"\n[Fact {i}] "
            f"(Confidence: {f['confidence']})\n"
            f"{f['fact']}\n"
            f"Source: {f['source_url']}\n"
            f"Answers: {f['sub_question']}\n"
        )

    gaps_text = ""
    if state.get("knowledge_gaps"):
        gaps_text = "\n".join(
            state["knowledge_gaps"]
        )

    prompt = f"""
You are a professional research writer.

Write a comprehensive research brief on:
"{state['query']}"

Research angle: {state.get(
    'research_angle', 'General overview'
)}

Return JSON ONLY. No explanation.

{{
  "executive_summary": "<3-4 sentence overview>",
  "key_findings": [
    {{
      "finding": "<important finding>",
      "detail": "<supporting detail>",
      "confidence": "<HIGH | MEDIUM | LOW>"
    }}
  ],
  "section_breakdown": [
    {{
      "section_title": "<section name>",
      "content": "<2-3 paragraph section content>",
      "sub_question_answered": "<which question>"
    }}
  ],
  "conclusions": [
    "<conclusion 1>",
    "<conclusion 2>",
    "<conclusion 3>"
  ],
  "follow_up_questions": [
    "<question for deeper research>"
  ],
  "confidence_score": <integer 1-10>,
  "word_count_estimate": <integer>
}}

Rules:
- Base ONLY on provided verified facts
- Do not invent information
- Cite source URLs where relevant
- If data is insufficient, say so explicitly

VERIFIED FACTS:
{facts_text}

KNOWLEDGE GAPS TO ACKNOWLEDGE:
{gaps_text or 'None identified'}
"""

    try:
        raw = gemini_call_fn(prompt)
        raw = raw.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            lines = [
                l for l in lines
                if not l.strip().startswith("```")
            ]
            raw = "\n".join(lines).strip()

        data = json.loads(raw)

        # Validate all fields
        if not data.get("executive_summary"):
            data["executive_summary"] = (
                "Research completed. "
                "See findings below."
            )

        for field in [
            "key_findings",
            "section_breakdown",
            "conclusions",
            "follow_up_questions"
        ]:
            if not isinstance(
                data.get(field), list
            ):
                data[field] = []

        try:
            data["confidence_score"] = max(
                1, min(
                    10,
                    int(
                        data.get(
                            "confidence_score", 5
                        )
                    )
                )
            )
        except (ValueError, TypeError):
            data["confidence_score"] = 5

        state["final_report"] = data
        state["status"] = "complete"

        log_agent(
            state, "WRITER",
            f"Report complete — "
            f"{len(data['key_findings'])} findings | "
            f"Confidence: "
            f"{data['confidence_score']}/10"
        )

        return state

    except json.JSONDecodeError:
        state["error"] = (
            "Failed to generate report. "
            "Please try again."
        )
        state["status"] = "failed"
        log_agent(
            state, "WRITER",
            "⚠️ Report generation failed"
        )
        return state


# ───── Quick test ─────
if __name__ == "__main__":
    print("\n🧪 Test: Agent state initialization")

    state = create_initial_state(
        "What are the key challenges in "
        "deploying LLMs at production scale?"
    )

    print(f"  ✅ State created")
    print(f"     Query  : {state['query'][:50]}")
    print(f"     Status : {state['status']}")
    print(f"     Logs   : {len(state['agent_logs'])}")

    print("\n✅ State test passed.")
    print(
        "\nFull agent pipeline tested in app.py"
    )