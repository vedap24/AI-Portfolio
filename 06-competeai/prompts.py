SYNTHESIS_PROMPT = """
You are a senior competitive intelligence analyst
at a top-tier strategy consulting firm.

You have collected raw search results about
a company and its competitors.

Your job is to synthesize this into a
structured competitive brief.
Return JSON ONLY. No explanation. Just JSON.

{{
  "executive_summary": "<3-4 sentence overview of the competitive landscape>",
  "company_snapshots": [
    {{
      "company_name": "<name>",
      "is_your_company": <true or false>,
      "current_position": "<one sentence on where they stand>",
      "recent_moves": ["<move 1>", "<move 2>"],
      "strengths": ["<strength 1>", "<strength 2>"],
      "weaknesses": ["<weakness 1>", "<weakness 2>"],
      "threat_level": "<HIGH | MEDIUM | LOW>",
      "momentum": "<Growing | Stable | Declining>"
    }}
  ],
  "key_signals": [
    {{
      "signal": "<important competitive signal>",
      "company": "<which company>",
      "implication": "<what this means for the market>",
      "urgency": "<HIGH | MEDIUM | LOW>"
    }}
  ],
  "market_trends": [
    "<trend 1 observed across all companies>",
    "<trend 2>",
    "<trend 3>"
  ],
  "recommended_actions": [
    {{
      "action": "<specific action to take>",
      "reason": "<why this matters>",
      "timeframe": "<immediately | this month | this quarter>"
    }}
  ],
  "watch_list": [
    "<thing to monitor closely 1>",
    "<thing to monitor closely 2>"
  ],
  "data_freshness": "<how recent the data appears to be>"
}}

Rules:
- Base analysis ONLY on provided search results
- Do not invent information not in the results
- If data is insufficient for a field,
  say "Insufficient data" — do not guess
- threat_level is relative to YOUR company
- momentum is based on recent activity signals

YOUR COMPANY: {your_company}
COMPETITORS: {competitors}
RESEARCH FOCUS: {research_focus}

RAW SEARCH RESULTS:
{results}
"""

COMPANY_PROFILE_PROMPT = """
Based on these search results, write a
one-paragraph company profile.
Return JSON ONLY.

{{
  "profile": "<2-3 sentence company profile>",
  "founded_or_stage": "<when founded or funding stage if mentioned>",
  "key_product": "<their main product or service>",
  "target_market": "<who they sell to>"
}}

COMPANY: {company}
SEARCH RESULTS: {results}
"""