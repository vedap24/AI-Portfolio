import os
import json
import time
from dotenv import load_dotenv
from google import genai
from models import ResumeScore
from prompts import RESUME_SCORER_PROMPT

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def clean_gemini_response(raw: str) -> str:
    """Strip markdown code fences Gemini sometimes wraps around JSON."""
    raw = raw.strip()

    # Handle ```json ... ```
    if raw.startswith("```"):
        lines = raw.split("\n")
        # Remove first line (```json or ```) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        raw = "\n".join(lines).strip()

    return raw


def validate_score(data: dict) -> dict:
    """Fix common issues in Gemini's returned data before Pydantic parsing."""

    # Ensure fit_score is an int between 0-100
    score = data.get("fit_score", 0)
    if isinstance(score, str):
        score = int("".join(filter(str.isdigit, score)) or 0)
    data["fit_score"] = max(0, min(100, int(score)))

    # Ensure fit_label is one of the 3 valid values
    label = data.get("fit_label", "")
    if data["fit_score"] >= 75:
        data["fit_label"] = "Strong Match"
    elif data["fit_score"] >= 45:
        data["fit_label"] = "Partial Match"
    else:
        data["fit_label"] = "Weak Match"

    # Ensure all list fields are actually lists
    list_fields = ["matched_skills", "missing_skills", "top_strengths", "improvement_tips"]
    for field in list_fields:
        if not isinstance(data.get(field), list):
            data[field] = [str(data[field])] if data.get(field) else ["N/A"]

    # Ensure string fields are not empty
    string_fields = ["experience_gap", "summary"]
    for field in string_fields:
        if not data.get(field) or not isinstance(data[field], str):
            data[field] = "No information available."

    return data


def score_resume(jd: str, resume: str, retries: int = 2) -> ResumeScore:
    """
    Call Gemini to score resume against JD.
    Retries up to 2 times on failure.
    """

    # Basic input validation
    if not jd.strip():
        raise ValueError("Job description cannot be empty.")
    if not resume.strip():
        raise ValueError("Resume cannot be empty.")
    if len(jd) < 50:
        raise ValueError("Job description seems too short. Please paste the full JD.")
    if len(resume) < 100:
        raise ValueError("Resume seems too short. Please paste the full resume text.")

    filled_prompt = RESUME_SCORER_PROMPT.format(jd=jd, resume=resume)

    last_error = None

    for attempt in range(retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=filled_prompt
            )

            raw_text = clean_gemini_response(response.text)
            data = json.loads(raw_text)
            data = validate_score(data)

            return ResumeScore(**data)

        except json.JSONDecodeError as e:
            last_error = f"Gemini returned invalid JSON (attempt {attempt + 1}): {e}"
            if attempt < retries:
                time.sleep(1)  # wait 1 second before retry
            continue

        except Exception as e:
            last_error = str(e)
            if attempt < retries:
                time.sleep(1)
            continue

    # All retries failed
    raise RuntimeError(
        f"Failed to analyze resume after {retries + 1} attempts. "
        f"Last error: {last_error}"
    )


# ───── Quick test ─────
if __name__ == "__main__":

    # Test 1: Normal case
    print("\n🧪 Test 1: Normal resume vs JD")
    result = score_resume(
        jd="Python Backend Engineer. FastAPI, PostgreSQL, Docker. 2+ years required.",
        resume="Veda — Frontend dev, React, JS, Python basics. 6 months experience."
    )
    print(f"  ✅ Score: {result.fit_score}/100 — {result.fit_label}")

    # Test 2: Empty JD
    print("\n🧪 Test 2: Empty JD — should raise ValueError")
    try:
        score_resume(jd="", resume="some resume text here that is long enough")
    except ValueError as e:
        print(f"  ✅ Caught correctly: {e}")

    # Test 3: Too short resume
    print("\n🧪 Test 3: Too short resume — should raise ValueError")
    try:
        score_resume(jd="Python developer needed with FastAPI skills", resume="Dev")
    except ValueError as e:
        print(f"  ✅ Caught correctly: {e}")

    print("\n✅ All tests passed.")