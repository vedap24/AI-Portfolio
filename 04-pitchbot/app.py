import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai
from models import PitchResult, EmailVariant
from prompts import EMAIL_WRITER_PROMPT

load_dotenv()

# ── Gemini client ──
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
GEMINI_MODEL  = "gemini-3.1-flash-lite-preview"


def clean_gemini_response(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = [l for l in lines
                 if not l.strip().startswith("```")]
        raw = "\n".join(lines).strip()
    return raw


def call_gemini(prompt: str, retries: int = 3) -> str:
    last_error = None
    for attempt in range(retries + 1):
        try:
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            return response.text
        except Exception as e:
            error_str = str(e)
            last_error = error_str
            if "429" in error_str or \
               "RESOURCE_EXHAUSTED" in error_str:
                if attempt < retries:
                    print(f"⏳ Rate limit. Waiting 60s...")
                    time.sleep(62)
                    continue
            if attempt < retries:
                time.sleep(5)
                continue
    raise RuntimeError(
        f"Gemini failed after {retries+1} attempts: "
        f"{last_error}"
    )


def scrape_company_page(url: str) -> str:
    if not url or not url.strip():
        return ""
    if not url.startswith("http"):
        url = "https://" + url
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                " AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(
            url, headers=headers, timeout=10
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        for tag in soup(["script", "style", "nav",
                          "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:2000]
    except requests.exceptions.Timeout:
        print("  ⚠️  Company page timed out — skipping")
        return ""
    except requests.exceptions.ConnectionError:
        print("  ⚠️  Could not connect — skipping")
        return ""
    except requests.exceptions.HTTPError as e:
        print(f"  ⚠️  HTTP error {e} — skipping")
        return ""
    except Exception:
        return ""


def validate_inputs(
    profile_text: str,
    your_purpose: str
) -> None:
    if not profile_text or \
       len(profile_text.strip()) < 50:
        raise ValueError(
            "Profile text too short. Paste at least "
            "the person's name, role, company, "
            "and one line about their work."
        )
    if len(profile_text.strip()) > 8000:
        raise ValueError(
            "Profile text too long (max 8000 chars). "
            "Paste only: name, role, company, "
            "about section, recent experience."
        )
    if not your_purpose or \
       len(your_purpose.strip()) < 20:
        raise ValueError(
            "Purpose too short. Describe what you're "
            "reaching out about in at least 20 characters."
        )
    if len(your_purpose.strip()) > 1000:
        raise ValueError(
            "Purpose too long (max 1000 chars). "
            "Keep it to 2-3 sentences."
        )


def extract_profile_insights(
    profile_text: str,
    company_context: str = ""
) -> dict:
    company_section = (
        f"\nCOMPANY WEBPAGE CONTEXT:\n{company_context}"
        if company_context else ""
    )
    prompt = f"""
You are an expert at reading professional profiles
and extracting actionable insights for outreach.

Read this LinkedIn profile and extract insights.
Return JSON ONLY. No explanation. Just JSON.

{{
  "full_name": "<person's full name>",
  "current_role": "<their current job title>",
  "current_company": "<company they work at>",
  "years_experience": "<estimated years>",
  "key_skills": ["skill1", "skill2", "skill3"],
  "recent_focus": "<what they seem focused on recently>",
  "career_trajectory": "<how their career has progressed>",
  "likely_challenges": ["challenge1", "challenge2"],
  "interests_or_passions": ["interest1", "interest2"],
  "notable_achievements": ["achievement1", "achievement2"],
  "communication_style": "<formal | casual | technical>",
  "seniority_level": "<junior | mid | senior | executive>"
}}

LINKEDIN PROFILE:
{profile_text}
{company_section}
"""
    raw = call_gemini(prompt)
    raw = clean_gemini_response(raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {
            "full_name": "the recipient",
            "current_role": "professional",
            "current_company": "their company",
            "years_experience": "several years",
            "key_skills": [],
            "recent_focus": "their work",
            "career_trajectory": "progressive",
            "likely_challenges": [],
            "interests_or_passions": [],
            "notable_achievements": [],
            "communication_style": "formal",
            "seniority_level": "mid"
        }

    # Ensure all required fields exist
    defaults = {
        "full_name": "the recipient",
        "current_role": "professional",
        "current_company": "their company",
        "years_experience": "several years",
        "key_skills": [],
        "recent_focus": "their work",
        "career_trajectory": "progressive",
        "likely_challenges": [],
        "interests_or_passions": [],
        "notable_achievements": [],
        "communication_style": "formal",
        "seniority_level": "mid"
    }
    for key, default in defaults.items():
        if not data.get(key):
            data[key] = default

    return data


def find_connection_angles(
    insights: dict,
    your_purpose: str
) -> dict:
    prompt = f"""
You are an expert at finding genuine connection angles
for professional outreach.

Given profile insights and sender's purpose,
find the best angles.
Return JSON ONLY.

{{
  "primary_angle": "<strongest connection angle>",
  "secondary_angles": ["<angle 2>", "<angle 3>"],
  "shared_interests": ["<shared interest if any>"],
  "pain_point_addressed": "<their challenge your purpose addresses>",
  "value_proposition": "<one sentence: what value you offer>",
  "avoid_topics": ["<topic to avoid>"],
  "best_tone": "<professional | conversational | peer-to-peer>"
}}

PROFILE INSIGHTS:
{json.dumps(insights, indent=2)}

SENDER PURPOSE:
{your_purpose}
"""
    raw = call_gemini(prompt)
    raw = clean_gemini_response(raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {
            "primary_angle": "shared professional interests",
            "secondary_angles": [],
            "shared_interests": [],
            "pain_point_addressed": "professional growth",
            "value_proposition": your_purpose[:100],
            "avoid_topics": [],
            "best_tone": "professional"
        }

    # Ensure lists
    for field in ["secondary_angles", "shared_interests",
                  "avoid_topics"]:
        if not isinstance(data.get(field), list):
            data[field] = []

    # Ensure best_tone is valid
    valid_tones = [
        "professional", "conversational", "peer-to-peer"
    ]
    if data.get("best_tone") not in valid_tones:
        data["best_tone"] = "professional"

    return data


def write_emails(
    insights: dict,
    angles: dict,
    your_purpose: str
) -> tuple:
    tone = angles.get("best_tone", "professional")
    prompt = EMAIL_WRITER_PROMPT.format(
        insights=json.dumps(insights, indent=2),
        angles=json.dumps(angles, indent=2),
        purpose=your_purpose,
        tone=tone
    )
    raw = call_gemini(prompt)
    raw = clean_gemini_response(raw)

    try:
        data = json.loads(raw)
        emails = data.get("emails", [])
        validated = []

        for email in emails:
            if not isinstance(
                email.get("word_count"), int
            ):
                email["word_count"] = len(
                    email.get("body", "").split()
                )
            if not email.get("best_for"):
                email["best_for"] = "General outreach"
            if not email.get("subject"):
                email["subject"] = "Quick question"
            if not email.get("body"):
                email["body"] = "Could not generate."
            if email.get("variant") not in \
               ["short", "medium", "detailed"]:
                email["variant"] = "medium"
            validated.append(EmailVariant(**email))

        # Force all 3 variants
        existing = {e.variant for e in validated}
        required = ["short", "medium", "detailed"]

        for variant in required:
            if variant not in existing:
                base = next(
                    (e for e in validated
                     if e.variant == "medium"),
                    validated[0] if validated else None
                )
                if base:
                    if variant == "short":
                        short_body = ". ".join(
                            base.body.split(". ")[:3]
                        ) + "."
                        validated.insert(0, EmailVariant(
                            variant="short",
                            subject=base.subject,
                            body=short_body,
                            word_count=len(
                                short_body.split()
                            ),
                            best_for=(
                                "Quick intro, "
                                "busy recipients"
                            )
                        ))
                    elif variant == "detailed":
                        detailed_body = (
                            base.body + "\n\n"
                            "Happy to share more context "
                            "or a quick demo if helpful."
                            "\n\nBest"
                        )
                        validated.append(EmailVariant(
                            variant="detailed",
                            subject=(
                                "More context — "
                                + base.subject
                            ),
                            body=detailed_body,
                            word_count=len(
                                detailed_body.split()
                            ),
                            best_for=(
                                "When you need "
                                "to show more proof"
                            )
                        ))

        # Sort: short → medium → detailed
        order = {"short": 0, "medium": 1, "detailed": 2}
        validated.sort(
            key=lambda x: order.get(x.variant, 1)
        )

        return (
            validated,
            data.get("personalization_elements", []),
            data.get(
                "follow_up_tip",
                "Follow up after 3-4 business days."
            )
        )

    except json.JSONDecodeError:
        fallback = EmailVariant(
            variant="medium",
            subject="Quick question for you",
            body=(
                f"Hi "
                f"{insights.get('full_name', 'there')},\n\n"
                f"{your_purpose}\n\n"
                f"Worth a quick chat?\n\nBest"
            ),
            word_count=20,
            best_for="Fallback"
        )
        return (
            [fallback],
            [],
            "Follow up after 3-4 business days."
        )


def generate_pitch(
    profile_text: str,
    your_purpose: str,
    company_url: str = ""
) -> PitchResult:

    # Validate
    validate_inputs(profile_text, your_purpose)

    # Optional scrape
    company_context = ""
    if company_url.strip():
        print("🌐 Scraping company page...")
        company_context = scrape_company_page(company_url)
        if company_context:
            print(
                f"  ✅ {len(company_context)} chars scraped"
            )
        else:
            print("  ⚠️  Skipping — could not scrape")

    # Step 1
    print("🔍 Step 1/3 — Extracting insights...")
    insights = extract_profile_insights(
        profile_text, company_context
    )

    # Step 2
    print("🎯 Step 2/3 — Finding angles...")
    angles = find_connection_angles(insights, your_purpose)

    # Step 3
    print("✍️  Step 3/3 — Writing emails...")
    emails, personalization, follow_up = write_emails(
        insights, angles, your_purpose
    )

    return PitchResult(
        emails=emails,
        personalization_elements=personalization,
        follow_up_tip=follow_up,
        recipient_name=insights.get(
            "full_name", "Recipient"
        ),
        recipient_role=insights.get("current_role", ""),
        recipient_company=insights.get(
            "current_company", ""
        ),
        primary_angle=angles.get("primary_angle", "")
    )


# ───── Tests ─────
if __name__ == "__main__":

    print("\n🧪 Test 1: Full pipeline")
    sample_profile = """
    Sarah Chen — VP of Engineering at BuildFast Inc.
    15 years in software engineering.
    Previously at Google and Stripe.
    Led migration from monolith to microservices.
    Passionate about developer experience.
    Recently posted about AI adoption challenges.
    Skills: Python, Kubernetes, System Design
    """
    sample_purpose = (
        "I'm an AI engineer who built a code review "
        "tool using LLMs. Reduces review time by 60%. "
        "Looking to connect with engineering leaders."
    )
    result = generate_pitch(
        profile_text=sample_profile,
        your_purpose=sample_purpose
    )
    print(f"  ✅ Variants  : "
          f"{[e.variant for e in result.emails]}")
    print(f"  ✅ Recipient : {result.recipient_name}")
    print(f"  ✅ Angle     : {result.primary_angle[:60]}")

    print("\n🧪 Test 2: Short profile")
    try:
        generate_pitch("too short", "some purpose here ok")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 3: Short purpose")
    try:
        generate_pitch(sample_profile, "too short")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 4: Bad URL — should not crash")
    result2 = generate_pitch(
        profile_text=sample_profile,
        your_purpose=sample_purpose,
        company_url="https://thisdoesnotexist12345.com"
    )
    print(f"  ✅ Handled bad URL — "
          f"{len(result2.emails)} emails generated")

    print("\n✅ All tests passed.")