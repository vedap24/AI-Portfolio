# 🎙️ FieldReport AI

> Speak your field report →
> get structured JSON data instantly.
> Site inspections, sales visits, delivery logs.
> Powered by faster-whisper + Gemini 2.0 Flash.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Whisper](https://img.shields.io/badge/ASR-faster--whisper-orange)
![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-yellow)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)

---

## 🎯 Real World Problem

> **Voice AI Research, 2026** —
> Production voice agent deployments grew
> 340% year-over-year. Companies using
> voice AI report 3-year ROI between
> 331% and 391% (Forrester/PolyAI).
>
> Field workers — inspectors, sales reps,
> delivery drivers — spend 30–40% of their
> time on manual data entry after completing
> fieldwork. They do the work, then type it up.
>
> **Voice recognition market: $18.39 billion
> in 2025, projected $61.71 billion by 2031.**

FieldReport AI eliminates the typing step.
Speak naturally. Get structured data.
No forms. No keyboard. No delay.

---

## ✨ Features

- 🎙️ Audio upload → auto-transcription
  via faster-whisper (runs locally)
- 🤖 Structured extraction via Gemini 2.0 Flash
- 📋 3 report types with domain-specific schemas:
  - 🏗️ Site Inspection
    (safety rating, issues, action items)
  - 💼 Sales Visit
    (deal stage, sentiment, next steps)
  - 🚚 Delivery Log
    (stops, completion rate, issues)
- ⬇️ Download report as JSON
- ⌨️ Text input mode for demo/testing
- 🔒 All audio processed locally
  (no audio sent to cloud)

---

## 🏗️ Architecture

Audio File Upload
↓
faster-whisper (local, CPU)
→ Transcription
→ Confidence score
→ Duration
↓
Gemini 2.0 Flash
→ Domain-specific extraction prompt
→ Structured JSON output
↓
Pydantic Validation
→ Field-by-field cleaning
→ Severity normalization
→ Default filling
↓
Streamlit Dashboard
→ Formatted report display
→ JSON download

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Speech Recognition | faster-whisper (local) |
| Structured Extraction | Gemini 2.0 Flash |
| Validation | Pydantic |
| UI | Streamlit |
| Language | Python 3.12 |

---

## 📋 Report Schemas

### Site Inspection
```json
{
  "location": "123 Main Street",
  "safety_rating": "FAIL",
  "overall_condition": "POOR",
  "issues": [{"severity": "CRITICAL", ...}],
  "action_items": [{"priority": "URGENT", ...}]
}
```

### Sales Visit
```json
{
  "client_name": "Acme Corp",
  "deal_stage": "Proposal",
  "sentiment": "POSITIVE",
  "next_steps": [{"action": "...", ...}]
}
```

### Delivery Log
```json
{
  "driver_name": "Mike Chen",
  "total_stops": 8,
  "completion_rate": "87%",
  "stops": [{"status": "Delivered", ...}]
}
```

---

## 🚀 Run Locally

```bash
git clone https://github.com/vedap24/ai-portfolio
cd 12-fieldreport-ai

source ../venv/bin/activate  # Mac/Linux
..\venv\Scripts\activate     # Windows

pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key" > .env

streamlit run ui.py
```

First run downloads the Whisper tiny model
(~75MB). Subsequent runs are instant.

---

## 🧠 What I Learned

- Audio processing requires temp file
  management — bytes → file → transcribe
  → cleanup. Always use try/finally.
- Whisper's VAD filter removes silence
  automatically — huge improvement
  for real-world recordings
- Domain-specific prompts extract
  dramatically better data than
  generic extraction — the schema
  in the prompt IS the product
- Queue data structure (DSA) maps directly
  to sequential audio segment processing —
  FIFO order matters for transcription
- Pydantic's default handling is critical
  for voice data — speakers often omit
  fields that forms would require

---

## 📅 Day 12 of 14 — AI Build in Public Challenge

Follow the journey →
[LinkedIn](https://linkedin.com/in/vedapraneeth)