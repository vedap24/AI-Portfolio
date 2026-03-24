import os
import json
import time
from pathlib import Path
from faster_whisper import WhisperModel
from dotenv import load_dotenv
from google import genai
from models import MeetingBrief
from prompts import MEETING_EXTRACTOR_PROMPT

load_dotenv()

# ── Load Whisper model ──
print("⏳ Loading Whisper model...")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
print("✅ Whisper model ready")

# ── Gemini client ──
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def clean_gemini_response(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        raw = "\n".join(lines).strip()
    return raw


def validate_meeting_brief(data: dict) -> dict:
    list_fields = ["decisions", "follow_up_questions", "key_topics"]
    for field in list_fields:
        if not isinstance(data.get(field), list):
            data[field] = [data[field]] if data.get(field) else []

    if not isinstance(data.get("action_items"), list):
        data["action_items"] = []

    for item in data["action_items"]:
        if not isinstance(item, dict):
            continue
        item.setdefault("owner", "Unassigned")
        item.setdefault("deadline", "Not specified")
        item.setdefault("task", "")

    valid_sentiments = ["Productive", "Unresolved", "Mixed"]
    if data.get("meeting_sentiment") not in valid_sentiments:
        data["meeting_sentiment"] = "Mixed"

    for field in ["summary", "one_line_outcome"]:
        if not data.get(field):
            data[field] = "Not available."

    return data


def transcribe_audio(audio_path: str) -> dict:
    path = Path(audio_path)

    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    allowed = [".mp3", ".wav", ".m4a", ".ogg", ".flac"]
    if path.suffix.lower() not in allowed:
        raise ValueError(
            f"Unsupported file type: {path.suffix}. "
            f"Allowed: {', '.join(allowed)}"
        )

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 100:
        raise ValueError(
            f"File too large: {size_mb:.1f}MB. Maximum allowed: 100MB."
        )

    if size_mb < 0.001:
        raise ValueError("Audio file is empty or corrupted.")

    print(f"🎙️ Transcribing: {path.name} ({size_mb:.1f}MB)")
    start = time.time()

    try:
        segments, info = whisper_model.transcribe(
            str(path),
            beam_size=5,
            language=None,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        full_transcript = ""
        segment_list = []

        for segment in segments:
            text = segment.text.strip()
            full_transcript += text + " "
            segment_list.append({
                "start": round(segment.start, 1),
                "end": round(segment.end, 1),
                "text": text
            })

    except Exception as e:
        raise RuntimeError(
            f"Whisper transcription failed: {str(e)}. "
            f"Try converting audio to MP3 format."
        )

    duration = time.time() - start
    full_transcript = full_transcript.strip()

    if not full_transcript:
        raise ValueError(
            "No speech detected in audio file. "
            "Make sure the recording contains clear speech."
        )

    if len(full_transcript) < 20:
        raise ValueError(
            "Transcript too short — audio may be too brief or unclear. "
            "Minimum 10 seconds of clear speech recommended."
        )

    print(f"✅ Transcribed in {duration:.1f}s — {len(full_transcript)} chars")

    return {
        "transcript": full_transcript,
        "language": info.language,
        "confidence": round(info.language_probability, 2),
        "segments": segment_list,
        "duration_seconds": round(duration, 1)
    }


def extract_meeting_brief(
    transcript: str,
    retries: int = 2
) -> MeetingBrief:

    if not transcript or len(transcript.strip()) < 20:
        raise ValueError(
            "Transcript too short to extract a meaningful brief."
        )

    filled_prompt = MEETING_EXTRACTOR_PROMPT.format(
        transcript=transcript
    )
    last_error = None

    for attempt in range(retries + 1):
        try:
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=filled_prompt
            )

            raw = clean_gemini_response(response.text)
            data = json.loads(raw)
            data = validate_meeting_brief(data)
            return MeetingBrief(**data)

        except json.JSONDecodeError as e:
            last_error = f"JSON parse error (attempt {attempt + 1}): {e}"
            if attempt < retries:
                time.sleep(1)
            continue

        except Exception as e:
            last_error = str(e)
            if attempt < retries:
                time.sleep(1)
            continue

    raise RuntimeError(
        f"Failed after {retries + 1} attempts. Last error: {last_error}"
    )


# ───── Tests ─────
if __name__ == "__main__":

    print("\n🧪 Test 1: Full pipeline with real audio")
    result = transcribe_audio("test_meeting.mp3")
    brief = extract_meeting_brief(result["transcript"])
    print(f"  ✅ Score: {brief.meeting_sentiment} | "
          f"{len(brief.action_items)} actions | "
          f"{len(brief.decisions)} decisions")

    print("\n🧪 Test 2: File not found")
    try:
        transcribe_audio("ghost.mp3")
    except FileNotFoundError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 3: Wrong file type")
    try:
        transcribe_audio("resume.pdf")
    except (FileNotFoundError, ValueError) as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 4: Empty transcript")
    try:
        extract_meeting_brief("   ")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n✅ All tests passed.")