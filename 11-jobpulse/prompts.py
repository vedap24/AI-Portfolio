INSIGHTS_PROMPT = """
You are a career coach and data analyst
specializing in job search strategy.

A job seeker has shared their application data.
Analyze the patterns and give personalized,
data-driven advice.

Return JSON ONLY. No explanation. Just JSON.

{{
  "headline_insight": "<single most important finding>",
  "performance_score": <integer 1-100>,
  "score_reasoning": "<why this score>",
  "key_insights": [
    {{
      "insight": "<specific pattern found>",
      "data_point": "<the number that proves it>",
      "impact": "<HIGH | MEDIUM | LOW>",
      "category": "<Source | Timing | Volume | Company | Role>"
    }}
  ],
  "what_is_working": [
    "<specific thing working well with evidence>"
  ],
  "what_to_change": [
    {{
      "problem": "<specific problem>",
      "evidence": "<data that shows this>",
      "action": "<exact action to take>",
      "expected_impact": "<what will improve>"
    }}
  ],
  "weekly_action_plan": [
    "<specific action for this week>"
  ],
  "benchmark_comparison": {{
    "your_response_rate": "<X%>",
    "industry_average": "3-13% (LinkedIn 2025)",
    "your_vs_average": "<above/below/at average>",
    "interpretation": "<what this means>"
  }},
  "predicted_timeline": "<realistic estimate to first offer based on current pace>"
}}

Rules:
- Be brutally honest — this person needs
  real feedback, not encouragement
- Every insight must cite specific numbers
  from the data
- Actions must be specific and actionable
  (not "apply more" — say exactly what to do)
- Compare to real industry benchmarks

JOB SEARCH DATA SUMMARY:
{data_summary}
"""


FOLLOWUP_PROMPT = """
You are a career coach reviewing job
search data.

The user is asking a follow-up question
about their job search strategy.

Answer concisely and specifically,
referencing their actual data where possible.
Return plain text — not JSON.

USER DATA SUMMARY:
{data_summary}

QUESTION:
{question}
"""


def build_data_summary(
    analysis: dict,
    df
) -> str:
    """
    Build a concise text summary of
    the analysis data for the LLM prompt.
    Converts numbers into readable context.
    """
    funnel   = analysis["funnel"]
    sources  = analysis["by_source"]
    timeline = analysis["timeline"]
    sizes    = analysis["by_size"]

    summary = f"""
OVERALL STATS:
- Total applications: {funnel['total']}
- Response rate: {funnel['response_rate']}%
- Interview rate: {funnel['interview_rate']}%
- Offer rate: {funnel['offer_rate']}%
- Ghost rate (no response): {funnel['ghost_rate']}%
- Got to phone screen: {funnel['phone_screen']}
- Got to technical: {funnel['technical']}
- Got to final round: {funnel['final_round']}
- Offers received: {funnel['offers']}

APPLICATION FUNNEL:
Applied: {funnel['applied']}
→ Phone Screen: {funnel['phone_screen']} ({round(funnel['phone_screen']/max(funnel['total'],1)*100,1)}%)
→ Technical: {funnel['technical']} ({round(funnel['technical']/max(funnel['total'],1)*100,1)}%)
→ Final Round: {funnel['final_round']} ({round(funnel['final_round']/max(funnel['total'],1)*100,1)}%)
→ Offer: {funnel['offers']} ({round(funnel['offers']/max(funnel['total'],1)*100,1)}%)
"""

    if sources:
        summary += "\nBY SOURCE:\n"
        for src, stats in sources.items():
            summary += (
                f"- {src}: {stats['total']} apps, "
                f"{stats['response_rate']}% response, "
                f"{stats['interview_rate']}% interview\n"
            )

    if timeline:
        summary += f"""
TIMELINE:
- Days searching: {timeline.get('days_searching', 0)}
- Avg applications/week: {timeline.get('avg_per_week', 0)}
- First applied: {timeline.get('first_applied', 'Unknown')}
- Last applied: {timeline.get('last_applied', 'Unknown')}
"""

    if sizes:
        summary += "\nBY COMPANY SIZE:\n"
        for size, stats in sizes.items():
            summary += (
                f"- {size}: {stats['total']} apps, "
                f"{stats['response_rate']}% response\n"
            )

    # Status breakdown
    status_counts = funnel.get(
        "status_counts", {}
    )
    if status_counts:
        summary += "\nSTATUS BREAKDOWN:\n"
        for status, count in sorted(
            status_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            summary += f"- {status}: {count}\n"

    # Top companies that responded
    if "status" in df.columns and \
       "company" in df.columns:
        responded = df[
            df["status"].isin(
                ["Phone Screen",
                 "Technical Interview",
                 "Final Round",
                 "Offer"]
            )
        ]["company"].tolist()

        if responded:
            summary += (
                f"\nCOMPANIES THAT RESPONDED:\n"
                f"{', '.join(responded[:8])}\n"
            )

    return summary