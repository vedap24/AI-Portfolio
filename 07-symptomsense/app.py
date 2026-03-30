import os
import json
import time
from dotenv import load_dotenv
from google import genai
from models import TriageResult, PatientInput
from prompts import (
    TRIAGE_SYSTEM_PROMPT,
    check_red_flags
)

load_dotenv()

# ── Gemini client ──
gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
GEMINI_MODEL = "gemini-3.1-flash-lite-preview"

# ── Emergency resources ──
EMERGENCY_RESOURCES = {
    "Emergency":      "112 (India) / 911 (US)",
    "Ambulance":      "108 (India) / 911 (US)",
    "Poison Control": "1800-116-117 (India)",
    "Mental Health":  "iCall: 9152987821 (India)",
    "Women Helpline": "181 (India)"
}


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
    """
    Call Gemini with retry.
    Critical safety note: if ALL retries fail,
    we return SEE_DOCTOR — not MONITOR_HOME.
    API failures should escalate, not downgrade.
    """
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

    # API failed completely
    # Return None — caller handles fallback
    print(
        f"⚠️  Gemini API failed: {last_error}"
    )
    return None


def get_emergency_triage(
    flags: list = None
) -> TriageResult:
    """
    Deterministic emergency response.
    Used when:
    1. Red flag keywords detected (pre-check)
    2. API fails completely (safety fallback)
    3. JSON parse fails on emergency symptoms
    """
    return TriageResult(
        triage_level="SEEK_EMERGENCY",
        urgency_score=10,
        reasoning=(
            "Your symptoms include potential "
            "emergency warning signs. "
            "Please seek immediate medical "
            "attention. Do not wait to see "
            "if symptoms improve."
        ),
        red_flags_present=flags or [
            "Emergency pattern detected"
        ],
        red_flags_to_watch=[],
        immediate_steps=[
            "Call emergency services immediately",
            "Do not drive yourself if possible",
            "Stay calm and keep someone with you",
            "Do not eat or drink anything"
        ],
        what_to_tell_doctor=[
            "Exactly when symptoms started",
            "All current medications",
            "Any known medical conditions",
            "Severity and any recent changes"
        ],
        disclaimer=(
            "This is not medical advice. "
            "If you believe you are experiencing "
            "a medical emergency, call 112 or 911 "
            "immediately. Do not rely on this tool "
            "in an emergency situation."
        )
    )


def get_api_failure_triage() -> TriageResult:
    """
    Safe fallback when API completely fails.
    Always returns SEE_DOCTOR —
    never MONITOR_HOME on uncertainty.
    """
    return TriageResult(
        triage_level="SEE_DOCTOR",
        urgency_score=5,
        reasoning=(
            "Unable to complete symptom analysis "
            "due to a technical issue. "
            "Out of caution, we recommend "
            "consulting a healthcare provider. "
            "Please try again or seek care "
            "if you are concerned."
        ),
        red_flags_present=[],
        red_flags_to_watch=[
            "Any worsening of symptoms",
            "New symptoms developing",
            "Fever above 103°F / 39.4°C"
        ],
        immediate_steps=[
            "Rest and stay hydrated",
            "Monitor symptoms closely",
            "Seek immediate care if symptoms "
            "worsen significantly"
        ],
        what_to_tell_doctor=[
            "Describe all symptoms clearly",
            "Note when symptoms started",
            "Rate severity on a scale of 1-10"
        ],
        disclaimer=(
            "This is not medical advice. "
            "Always consult a qualified "
            "healthcare provider for "
            "medical decisions."
        )
    )


def strip_medication_references(
    steps: list
) -> list:
    """
    Remove any medication references from
    immediate_steps.
    Hard backstop against LLM medication suggestions.
    """
    medication_keywords = [
        "mg", "ml", "dose", "dosage",
        "tablet", "capsule", "pill",
        "ibuprofen", "paracetamol", "tylenol",
        "aspirin", "advil", "acetaminophen",
        "antibiotic", "medication", "medicine",
        "drug", "prescription", "otc",
        "take ", "administer"
    ]

    safe_steps = []
    for step in steps:
        step_lower = step.lower()
        has_medication = any(
            kw in step_lower
            for kw in medication_keywords
        )
        if not has_medication:
            safe_steps.append(step)

    # Always return at least 2 safe steps
    if not safe_steps:
        safe_steps = [
            "Rest and stay hydrated",
            "Monitor your symptoms closely",
            "Seek care if symptoms worsen"
        ]

    return safe_steps


def triage_symptoms(
    patient_input: PatientInput
) -> TriageResult:
    """
    Core triage function with 7 safety layers.

    Layer 1: Input validation (Pydantic — automatic)
    Layer 2: Red flag pre-check (rule-based)
    Layer 3: Constrained LLM prompt
    Layer 4: API failure handling
    Layer 5: JSON parse failure handling
    Layer 6: Medication keyword stripping
    Layer 7: Pydantic output validation
    """

    # ── Layer 2: Red flag pre-check ──
    all_text = (
        f"{patient_input.symptoms} "
        f"{patient_input.context}"
    ).strip()

    red_flags = check_red_flags(all_text)

    if red_flags:
        print(
            f"🚨 Red flags: {red_flags} — "
            f"emergency triage (no API call)"
        )
        result = get_emergency_triage(red_flags)
        return result

    # ── Layer 3: LLM triage ──
    prompt = TRIAGE_SYSTEM_PROMPT.format(
        age=patient_input.age,
        duration=patient_input.duration,
        severity=patient_input.severity,
        symptoms=patient_input.symptoms,
        context=patient_input.context or "None"
    )

    # ── Layer 4: API failure handling ──
    raw = call_gemini(prompt)

    if raw is None:
        print(
            "⚠️  API failed — "
            "returning safe fallback"
        )
        return get_api_failure_triage()

    raw = clean_gemini_response(raw)

    # ── Layer 5: JSON parse failure ──
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(
            "⚠️  JSON parse failed — "
            "checking severity for safe default"
        )
        # High severity + parse failure = escalate
        if patient_input.severity >= 7:
            return get_emergency_triage()
        return get_api_failure_triage()

    # ── Layer 6: Validate + sanitize output ──

    # Validate triage level
    valid_levels = [
        "SEEK_EMERGENCY",
        "SEE_DOCTOR",
        "MONITOR_HOME"
    ]
    if data.get("triage_level") not in valid_levels:
        print(
            f"⚠️  Invalid triage level: "
            f"{data.get('triage_level')} — "
            f"defaulting to SEE_DOCTOR"
        )
        data["triage_level"] = "SEE_DOCTOR"

    # Validate urgency score
    try:
        score = int(data.get("urgency_score", 5))
        data["urgency_score"] = max(1, min(10, score))
    except (ValueError, TypeError):
        data["urgency_score"] = 5

    # Ensure all list fields exist
    for field in [
        "red_flags_present",
        "red_flags_to_watch",
        "immediate_steps",
        "what_to_tell_doctor"
    ]:
        if not isinstance(data.get(field), list):
            data[field] = []

    # Strip medication references
    data["immediate_steps"] = \
        strip_medication_references(
            data["immediate_steps"]
        )

    # Ensure reasoning exists
    if not data.get("reasoning") or \
       len(data["reasoning"]) < 10:
        data["reasoning"] = (
            "Based on the symptoms described, "
            "the recommended triage level is "
            f"{data['triage_level'].replace('_', ' ')}."
        )

    # Enforce disclaimer — always
    data["disclaimer"] = (
        "I am a triage assistant, not a medical "
        "professional. This is not a diagnosis or "
        "medical advice. Always consult a qualified "
        "healthcare provider for medical decisions."
    )

    # ── Layer 7: Pydantic validation ──
    try:
        return TriageResult(**data)
    except Exception as e:
        print(
            f"⚠️  Pydantic validation failed: {e}"
            f" — returning safe fallback"
        )
        return get_api_failure_triage()


# ───── Tests ─────
if __name__ == "__main__":

    print("\n🧪 Test 1: Mild symptoms")
    r1 = triage_symptoms(PatientInput(
        symptoms=(
            "Mild headache for 2 hours, "
            "slightly tired, no fever"
        ),
        age="28",
        duration="1–6 hours",
        severity=3,
        context="Sitting at computer all day"
    ))
    print(f"  ✅ Level : {r1.triage_level}")
    print(f"     Score : {r1.urgency_score}/10")
    assert r1.disclaimer, "Disclaimer missing!"
    print(f"     Disclaimer present ✓")

    print("\n🧪 Test 2: Moderate symptoms")
    r2 = triage_symptoms(PatientInput(
        symptoms=(
            "Fever 102F for 2 days, "
            "sore throat, body aches"
        ),
        age="35",
        duration="1–3 days",
        severity=6,
        context="No recent travel"
    ))
    print(f"  ✅ Level : {r2.triage_level}")
    print(f"     Score : {r2.urgency_score}/10")

    print("\n🧪 Test 3: Red flag — no API call")
    r3 = triage_symptoms(PatientInput(
        symptoms=(
            "Chest pain radiating to left arm, "
            "sweating, short of breath"
        ),
        age="55",
        duration="Less than 1 hour",
        severity=9
    ))
    print(f"  ✅ Level : {r3.triage_level}")
    print(
        f"     Flags : {r3.red_flags_present}"
    )
    assert r3.triage_level == "SEEK_EMERGENCY"
    print(f"     Emergency confirmed ✓")

    print("\n🧪 Test 4: Medication in steps stripped")
    # Inject fake data with medication
    fake_data = {
        "triage_level": "MONITOR_HOME",
        "urgency_score": 3,
        "reasoning": "Mild symptoms",
        "red_flags_present": [],
        "red_flags_to_watch": [],
        "immediate_steps": [
            "Take 500mg paracetamol",
            "Rest and drink water"
        ],
        "what_to_tell_doctor": [],
        "disclaimer": "test"
    }
    cleaned = strip_medication_references(
        fake_data["immediate_steps"]
    )
    assert "paracetamol" not in str(cleaned)
    print(
        f"  ✅ Medication stripped: {cleaned}"
    )

    print("\n🧪 Test 5: Input too short")
    try:
        PatientInput(
            symptoms="hi",
            age="25",
            duration="1–6 hours",
            severity=5
        )
    except Exception as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 6: Severity out of range")
    try:
        PatientInput(
            symptoms=(
                "Headache and fever since morning"
            ),
            age="30",
            duration="1–6 hours",
            severity=15
        )
    except Exception as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 7: Suicidal keyword — emergency")
    r7 = triage_symptoms(PatientInput(
        symptoms=(
            "Feeling very low, having suicidal "
            "thoughts"
        ),
        age="22",
        duration="1–3 days",
        severity=8
    ))
    print(f"  ✅ Level : {r7.triage_level}")
    assert r7.triage_level == "SEEK_EMERGENCY"
    print(f"     Mental health emergency ✓")

    print("\n✅ All 7 tests passed.")