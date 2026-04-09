# ──────────────────────────────────────────
# EXTRACTION PROMPTS
# One prompt per report type.
# Each extracts domain-specific fields
# from free-form spoken text.
# ──────────────────────────────────────────

SITE_INSPECTION_PROMPT = """
You are extracting structured data from
a field inspector's voice report.

Extract ALL relevant information and return
JSON ONLY. No explanation. Just JSON.

{{
  "location":           "<site location or address>",
  "inspector_name":     "<inspector name if mentioned>",
  "inspection_date":    "<date mentioned or 'Not specified'>",
  "inspection_type":    "<type of inspection>",
  "findings": [
    "<key finding 1>",
    "<key finding 2>"
  ],
  "issues": [
    {{
      "description": "<issue description>",
      "severity":    "<CRITICAL | HIGH | MEDIUM | LOW>",
      "location":    "<where on site>"
    }}
  ],
  "action_items": [
    {{
      "task":     "<what needs to be done>",
      "priority": "<URGENT | HIGH | MEDIUM | LOW>",
      "deadline": "<when if mentioned>"
    }}
  ],
  "safety_rating":       "<PASS | FAIL | CONDITIONAL>",
  "follow_up_required":  <true or false>,
  "follow_up_date":      "<date if mentioned>",
  "overall_condition":   "<EXCELLENT | GOOD | FAIR | POOR>",
  "additional_notes":    "<anything else mentioned>"
}}

Rules:
- Extract ONLY what was actually said
- Use "Not specified" for missing fields
- Be precise about severity levels
- If no issues mentioned, return []

TRANSCRIPT:
{transcript}
"""


SALES_VISIT_PROMPT = """
You are extracting structured data from
a sales representative's field visit report.

Extract ALL relevant information and return
JSON ONLY. No explanation. Just JSON.

{{
  "client_name":      "<company or client name>",
  "contact_person":   "<person met with>",
  "contact_role":     "<their job title if mentioned>",
  "meeting_date":     "<date of visit>",
  "meeting_duration": "<how long if mentioned>",
  "discussion_points": [
    "<topic discussed 1>",
    "<topic discussed 2>"
  ],
  "pain_points": [
    "<problem client mentioned>"
  ],
  "objections": [
    "<objection raised>"
  ],
  "next_steps": [
    {{
      "action":    "<what needs to happen>",
      "owner":     "<who does it>",
      "deadline":  "<when>"
    }}
  ],
  "deal_stage":    "<Prospect | Discovery | Proposal | Negotiation | Closed Won | Closed Lost>",
  "deal_value":    "<estimated value if mentioned>",
  "follow_up_date": "<next meeting or call date>",
  "sentiment":     "<POSITIVE | NEUTRAL | NEGATIVE>",
  "notes":         "<anything else relevant>"
}}

Rules:
- Extract ONLY what was said in the report
- Infer deal stage from context
- Use "Not specified" for missing fields

TRANSCRIPT:
{transcript}
"""


DELIVERY_LOG_PROMPT = """
You are extracting structured data from
a delivery driver's end-of-day report.

Extract ALL relevant information and return
JSON ONLY. No explanation. Just JSON.

{{
  "driver_name":    "<driver name if mentioned>",
  "vehicle_id":     "<truck or vehicle ID if mentioned>",
  "delivery_date":  "<date of deliveries>",
  "route":          "<route or area covered>",
  "stops": [
    {{
      "stop_number":  <integer>,
      "location":     "<delivery address or name>",
      "status":       "<Delivered | Failed | Partial>",
      "notes":        "<any issue at this stop>"
    }}
  ],
  "total_stops":         <integer or 0>,
  "successful_deliveries": <integer or 0>,
  "failed_deliveries":   <integer or 0>,
  "issues": [
    {{
      "type":        "<Vehicle | Route | Customer | Package | Other>",
      "description": "<what happened>",
      "severity":    "<HIGH | MEDIUM | LOW>"
    }}
  ],
  "start_time":     "<when started if mentioned>",
  "end_time":       "<when finished if mentioned>",
  "mileage":        "<miles driven if mentioned>",
  "fuel_used":      "<fuel if mentioned>",
  "completion_rate": "<percentage as string e.g. '95%'>",
  "notes":          "<anything else mentioned>"
}}

Rules:
- Count stops carefully from the transcript
- Calculate completion_rate from
  successful / total if not stated
- Use 0 for numeric fields if not mentioned

TRANSCRIPT:
{transcript}
"""


PROMPT_MAP = {
    "site_inspection": SITE_INSPECTION_PROMPT,
    "sales_visit":     SALES_VISIT_PROMPT,
    "delivery_log":    DELIVERY_LOG_PROMPT
}

REPORT_LABELS = {
    "site_inspection": "🏗️ Site Inspection",
    "sales_visit":     "💼 Sales Visit",
    "delivery_log":    "🚚 Delivery Log"
}