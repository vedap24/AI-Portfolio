import os
import json
import time
import tempfile
from dotenv import load_dotenv
from google import genai
from faster_whisper import WhisperModel
from models import (
    SiteInspectionReport,
    SalesVisitReport,
    DeliveryLogReport,
    FieldReportResult
)
from prompts import (
    PROMPT_MAP,
    REPORT_LABELS
)

load_dotenv()

# ── Gemini client ──
gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
GEMINI_MODEL = "gemini-3.1-flash-lite-preview"

# ── Whisper model ──
print("⏳ Loading Whisper model...")
whisper_model = WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8"
)
print("✅ Whisper ready")

# ── Constants ──
MAX_AUDIO_SIZE_MB  = 25
MAX_TEXT_LENGTH    = 5000
MIN_TEXT_LENGTH    = 10
VALID_AUDIO_EXTS   = [
    ".mp3", ".wav", ".m4a",
    ".ogg", ".flac", ".mp4"
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
                        "⏳ Rate limit. "
                        "Waiting 40s..."
                    )
                    time.sleep(40)
                    continue
            if attempt < retries:
                time.sleep(2)
                continue
    raise RuntimeError(
        f"Gemini API failed after "
        f"{retries + 1} attempts: {last_error}"
    )


# ──────────────────────────────────────────
# INPUT VALIDATORS
# ──────────────────────────────────────────

def validate_report_type(
    report_type: str
) -> None:
    if report_type not in PROMPT_MAP:
        raise ValueError(
            f"Invalid report type: '{report_type}'. "
            f"Must be one of: "
            f"{', '.join(PROMPT_MAP.keys())}"
        )


def validate_text_input(text: str) -> str:
    if not text or not text.strip():
        raise ValueError(
            "Report text cannot be empty."
        )

    cleaned = text.strip()

    if len(cleaned.split()) < 5:
        raise ValueError(
            "Report too short. Please provide "
            "at least 5 words of detail."
        )

    if len(cleaned) > MAX_TEXT_LENGTH:
        raise ValueError(
            f"Report too long. "
            f"Max {MAX_TEXT_LENGTH} characters. "
            f"Currently: {len(cleaned)} characters."
        )

    return cleaned


def validate_audio_input(
    audio_bytes: bytes,
    file_extension: str
) -> None:
    if not audio_bytes:
        raise ValueError(
            "No audio data received. "
            "Please upload a valid audio file."
        )

    # File size check
    size_mb = len(audio_bytes) / (1024 * 1024)
    if size_mb > MAX_AUDIO_SIZE_MB:
        raise ValueError(
            f"Audio file too large: "
            f"{size_mb:.1f}MB. "
            f"Max {MAX_AUDIO_SIZE_MB}MB. "
            f"Try a shorter recording."
        )

    # Extension check
    ext = file_extension.lower()
    if not ext.startswith("."):
        ext = "." + ext

    if ext not in VALID_AUDIO_EXTS:
        raise ValueError(
            f"Unsupported audio format: {ext}. "
            f"Supported: "
            f"{', '.join(VALID_AUDIO_EXTS)}"
        )


# ──────────────────────────────────────────
# TRANSCRIPTION ENGINE
# ──────────────────────────────────────────

def transcribe_audio(
    audio_path: str
) -> dict:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    file_size = os.path.getsize(audio_path)
    if file_size == 0:
        raise ValueError(
            "Audio file is empty (0 bytes)."
        )

    print(
        f"  🎙️ Transcribing: "
        f"{os.path.basename(audio_path)}"
    )

    try:
        segments, info = \
            whisper_model.transcribe(
                audio_path,
                beam_size=5,
                language=None,
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=500
                )
            )

        all_segments = list(segments)

    except Exception as e:
        raise RuntimeError(
            f"Transcription failed: {e}. "
            f"Please check audio quality "
            f"and format."
        )

    full_text = " ".join([
        seg.text.strip()
        for seg in all_segments
        if seg.text.strip()
    ]).strip()

    if not full_text:
        raise ValueError(
            "No speech detected. "
            "Please ensure audio has clear "
            "speech and is not muted."
        )

    if len(full_text.split()) < 3:
        raise ValueError(
            f"Transcript too short "
            f"({len(full_text.split())} words). "
            f"Please speak more clearly "
            f"or move closer to the microphone."
        )

    # Confidence from log probability
    if all_segments:
        avg_logprob = sum(
            seg.avg_logprob
            for seg in all_segments
        ) / len(all_segments)
        confidence = min(
            1.0, max(0.0, (avg_logprob + 1))
        )
    else:
        confidence = 0.5

    print(
        f"  ✅ Transcribed: "
        f"{len(full_text.split())} words "
        f"({info.duration:.1f}s)"
    )

    return {
        "text":       full_text,
        "confidence": round(confidence, 3),
        "duration":   round(info.duration, 2),
        "language":   info.language,
        "word_count": len(full_text.split())
    }


def transcribe_from_bytes(
    audio_bytes: bytes,
    file_extension: str = ".wav"
) -> dict:
    ext = file_extension
    if not ext.startswith("."):
        ext = "." + ext

    with tempfile.NamedTemporaryFile(
        suffix=ext,
        delete=False
    ) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        result = transcribe_audio(tmp_path)
    except Exception:
        raise
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return result


# ──────────────────────────────────────────
# FIELD VALIDATORS
# ──────────────────────────────────────────

def validate_severity(
    val: str,
    valid: list = None
) -> str:
    if valid is None:
        valid = [
            "CRITICAL", "HIGH",
            "MEDIUM", "LOW"
        ]
    return val if val in valid else "MEDIUM"


def safe_int(val, default: int = 0) -> int:
    try:
        return max(0, int(val))
    except (ValueError, TypeError):
        return default


def safe_str(
    val,
    default: str = "Not specified"
) -> str:
    if not val or str(val).strip() in [
        "", "nan", "None", "null"
    ]:
        return default
    return str(val).strip()


def safe_list(val) -> list:
    if isinstance(val, list):
        return val
    return []


# ──────────────────────────────────────────
# EXTRACTION ENGINE
# ──────────────────────────────────────────

def extract_site_inspection(data: dict) -> dict:

    if data.get("safety_rating") not in \
       ["PASS", "FAIL", "CONDITIONAL"]:
        data["safety_rating"] = "CONDITIONAL"

    if data.get("overall_condition") not in \
       ["EXCELLENT", "GOOD", "FAIR", "POOR"]:
        data["overall_condition"] = "FAIR"

    if not isinstance(
        data.get("follow_up_required"), bool
    ):
        raw = str(
            data.get("follow_up_required", "")
        ).lower()
        data["follow_up_required"] = (
            raw in ["true", "yes", "1"]
        )

    for field in ["findings", "issues",
                  "action_items"]:
        data[field] = safe_list(data.get(field))

    clean_issues = []
    for issue in data.get("issues", []):
        if not isinstance(issue, dict):
            continue
        desc = safe_str(
            issue.get("description"), ""
        )
        if not desc:
            continue
        clean_issues.append({
            "description": desc,
            "severity": validate_severity(
                issue.get("severity", "MEDIUM")
            ),
            "location": safe_str(
                issue.get("location")
            )
        })
    data["issues"] = clean_issues

    clean_actions = []
    for action in data.get("action_items", []):
        if not isinstance(action, dict):
            continue
        task = safe_str(
            action.get("task"), ""
        )
        if not task:
            continue
        clean_actions.append({
            "task": task,
            "priority": validate_severity(
                action.get("priority", "MEDIUM"),
                ["URGENT", "HIGH", "MEDIUM", "LOW"]
            ),
            "deadline": safe_str(
                action.get("deadline")
            )
        })
    data["action_items"] = clean_actions

    for field in [
        "location", "inspector_name",
        "inspection_date", "inspection_type",
        "follow_up_date", "additional_notes"
    ]:
        data[field] = safe_str(data.get(field))

    data["findings"] = [
        f for f in data.get("findings", [])
        if f and str(f).strip()
    ]

    return data


def extract_sales_visit(data: dict) -> dict:

    valid_stages = [
        "Prospect", "Discovery", "Proposal",
        "Negotiation", "Closed Won",
        "Closed Lost"
    ]
    if data.get("deal_stage") not in valid_stages:
        data["deal_stage"] = "Discovery"

    if data.get("sentiment") not in \
       ["POSITIVE", "NEUTRAL", "NEGATIVE"]:
        data["sentiment"] = "NEUTRAL"

    for field in [
        "discussion_points", "pain_points",
        "objections", "next_steps"
    ]:
        data[field] = safe_list(data.get(field))

    clean_steps = []
    for step in data.get("next_steps", []):
        if not isinstance(step, dict):
            continue
        action = safe_str(
            step.get("action"), ""
        )
        if not action:
            continue
        clean_steps.append({
            "action":   action,
            "owner":    safe_str(step.get("owner")),
            "deadline": safe_str(
                step.get("deadline")
            )
        })
    data["next_steps"] = clean_steps

    for field in [
        "client_name", "contact_person",
        "contact_role", "meeting_date",
        "meeting_duration", "deal_value",
        "follow_up_date", "notes"
    ]:
        data[field] = safe_str(data.get(field))

    for field in [
        "discussion_points",
        "pain_points", "objections"
    ]:
        data[field] = [
            str(i) for i in data.get(field, [])
            if i and str(i).strip()
        ]

    return data


def extract_delivery_log(data: dict) -> dict:

    data["total_stops"] = safe_int(
        data.get("total_stops")
    )
    data["successful_deliveries"] = safe_int(
        data.get("successful_deliveries")
    )
    data["failed_deliveries"] = safe_int(
        data.get("failed_deliveries")
    )

    for field in ["stops", "issues"]:
        data[field] = safe_list(data.get(field))

    clean_stops = []
    for i, stop in enumerate(
        data.get("stops", [])
    ):
        if not isinstance(stop, dict):
            continue
        location = safe_str(
            stop.get("location"), ""
        )
        if not location or location == \
           "Not specified":
            continue
        clean_stops.append({
            "stop_number": safe_int(
                stop.get("stop_number", i + 1),
                i + 1
            ),
            "location": location,
            "status": stop.get("status")
            if stop.get("status") in [
                "Delivered", "Failed", "Partial"
            ] else "Delivered",
            "notes": safe_str(
                stop.get("notes"), ""
            )
        })
    data["stops"] = clean_stops

    clean_issues = []
    for issue in data.get("issues", []):
        if not isinstance(issue, dict):
            continue
        desc = safe_str(
            issue.get("description"), ""
        )
        if not desc:
            continue
        issue_type = issue.get("type")
        if issue_type not in [
            "Vehicle", "Route", "Customer",
            "Package", "Other"
        ]:
            issue_type = "Other"
        clean_issues.append({
            "type": issue_type,
            "description": desc,
            "severity": validate_severity(
                issue.get("severity", "MEDIUM"),
                ["HIGH", "MEDIUM", "LOW"]
            )
        })
    data["issues"] = clean_issues

    # Calculate completion rate
    total   = data["total_stops"]
    success = data["successful_deliveries"]

    existing_rate = safe_str(
        data.get("completion_rate"), ""
    )
    if not existing_rate or \
       existing_rate == "Not specified":
        if total > 0:
            rate = round((success / total) * 100)
            data["completion_rate"] = f"{rate}%"
        else:
            data["completion_rate"] = "N/A"
    else:
        data["completion_rate"] = existing_rate

    for field in [
        "driver_name", "vehicle_id",
        "delivery_date", "route",
        "start_time", "end_time",
        "mileage", "fuel_used", "notes"
    ]:
        data[field] = safe_str(data.get(field))

    return data


VALIDATORS = {
    "site_inspection": extract_site_inspection,
    "sales_visit":     extract_sales_visit,
    "delivery_log":    extract_delivery_log
}


def extract_structured_report(
    transcript: str,
    report_type: str
) -> dict:
    validate_report_type(report_type)

    prompt = PROMPT_MAP[report_type].format(
        transcript=transcript
    )

    try:
        raw = call_gemini(prompt)
        raw = clean_gemini_response(raw)
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(
            f"  ⚠️  JSON parse error: {e} — "
            f"returning empty report"
        )
        data = {}
    except Exception as e:
        raise RuntimeError(
            f"Extraction failed: {e}"
        )

    if not isinstance(data, dict):
        data = {}

    validator = VALIDATORS[report_type]
    data = validator(data)

    return data


# ──────────────────────────────────────────
# MAIN PIPELINE
# ──────────────────────────────────────────

def process_field_report(
    audio_bytes: bytes,
    report_type: str,
    file_extension: str = ".wav"
) -> FieldReportResult:
    start = time.time()

    validate_report_type(report_type)
    validate_audio_input(
        audio_bytes, file_extension
    )

    print(
        f"\n🎙️ Processing audio "
        f"({report_type})..."
    )

    transcription = transcribe_from_bytes(
        audio_bytes, file_extension
    )

    print(
        f"  🤖 Extracting fields..."
    )
    report_data = extract_structured_report(
        transcription["text"],
        report_type
    )

    processing_time = round(
        time.time() - start, 2
    )
    print(
        f"  ✅ Done in {processing_time}s"
    )

    return FieldReportResult(
        report_type=report_type,
        transcript=transcription["text"],
        transcript_confidence=transcription[
            "confidence"
        ],
        audio_duration_seconds=transcription[
            "duration"
        ],
        report=report_data,
        word_count=transcription["word_count"],
        processing_time_seconds=processing_time
    )


def process_text_report(
    text: str,
    report_type: str
) -> FieldReportResult:
    start = time.time()

    validate_report_type(report_type)
    cleaned = validate_text_input(text)

    print(
        f"\n📝 Processing text "
        f"({report_type})..."
    )

    report_data = extract_structured_report(
        cleaned, report_type
    )

    processing_time = round(
        time.time() - start, 2
    )

    return FieldReportResult(
        report_type=report_type,
        transcript=cleaned,
        transcript_confidence=1.0,
        audio_duration_seconds=0.0,
        report=report_data,
        word_count=len(cleaned.split()),
        processing_time_seconds=processing_time
    )


# ───── Tests ─────
if __name__ == "__main__":

    print("\n🧪 Test 1: Site inspection")
    r1 = process_text_report(
        "Inspection at 123 Main Street. "
        "John Smith reporting. Critical roof "
        "leak north corner needs immediate "
        "repair. Exposed wiring second floor "
        "high severity. Safety rating FAIL. "
        "Follow-up required next week. "
        "Overall condition poor.",
        "site_inspection"
    )
    assert r1.report_type == "site_inspection"
    assert r1.report.get("safety_rating") == "FAIL"
    assert isinstance(
        r1.report.get("issues"), list
    )
    print(
        f"  ✅ Safety   : "
        f"{r1.report.get('safety_rating')}"
    )
    print(
        f"     Issues   : "
        f"{len(r1.report.get('issues', []))}"
    )
    print(
        f"     Location : "
        f"{r1.report.get('location', 'N/A')}"
    )

    print("\n🧪 Test 2: Sales visit")
    r2 = process_text_report(
        "Meeting with Acme Corp. "
        "Spoke with Sarah Johnson VP Operations. "
        "Discussed inventory management issues. "
        "Pain point is lack of real-time data. "
        "Objection: implementation cost. "
        "Next step send proposal by Friday. "
        "Deal looks very positive. "
        "Follow up next Tuesday.",
        "sales_visit"
    )
    assert r2.report.get("sentiment") in \
        ["POSITIVE", "NEUTRAL", "NEGATIVE"]
    assert r2.report.get("deal_stage") in [
        "Prospect", "Discovery", "Proposal",
        "Negotiation", "Closed Won", "Closed Lost"
    ]
    print(
        f"  ✅ Client   : "
        f"{r2.report.get('client_name','N/A')}"
    )
    print(
        f"     Stage    : "
        f"{r2.report.get('deal_stage','N/A')}"
    )
    print(
        f"     Sentiment: "
        f"{r2.report.get('sentiment','N/A')}"
    )

    print("\n🧪 Test 3: Delivery log")
    r3 = process_text_report(
        "Driver Mike Chen truck TRK-042. "
        "Downtown route. Stop 1 City Hall "
        "delivered. Stop 2 Oak Avenue delivered. "
        "Stop 3 Pine Street failed nobody home. "
        "Had flat tire causing 2 hour delay. "
        "Started 8am finished 5pm. 87 miles.",
        "delivery_log"
    )
    assert r3.report.get("driver_name") != \
        "Not specified"
    assert isinstance(
        r3.report.get("stops"), list
    )
    assert isinstance(
        r3.report.get("issues"), list
    )
    print(
        f"  ✅ Driver   : "
        f"{r3.report.get('driver_name','N/A')}"
    )
    print(
        f"     Stops    : "
        f"{len(r3.report.get('stops', []))}"
    )
    print(
        f"     Issues   : "
        f"{len(r3.report.get('issues', []))}"
    )

    print("\n🧪 Test 4: Invalid report type")
    try:
        validate_report_type("invalid_type")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 5: Text too short")
    try:
        validate_text_input("hi there")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 6: Empty text")
    try:
        validate_text_input("")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 7: Audio too large")
    try:
        validate_audio_input(
            b"x" * (26 * 1024 * 1024),
            ".wav"
        )
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 8: Invalid audio format")
    try:
        validate_audio_input(
            b"some audio data",
            ".xyz"
        )
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 9: safe_int helper")
    assert safe_int("5")   == 5
    assert safe_int("abc") == 0
    assert safe_int(None)  == 0
    assert safe_int(-3)    == 0
    print("  ✅ safe_int all cases correct")

    print("\n🧪 Test 10: safe_str helper")
    assert safe_str("hello") == "hello"
    assert safe_str("") == "Not specified"
    assert safe_str(None) == "Not specified"
    assert safe_str("nan") == "Not specified"
    print("  ✅ safe_str all cases correct")

    print("\n✅ All 10 tests passed.")