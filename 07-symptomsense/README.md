# 🏥 SymptomSense AI

> Not a diagnosis tool. A triage tool.
> One question answered: should you go to the ER,
> see a doctor, or rest at home?
> Powered by Gemini 2.0 Flash +
> rule-based safety layers.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-orange)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)
![Safety](https://img.shields.io/badge/Safety-7%20Layers-green)

---

## 🎯 Real World Problem

> **JAMA Network Open, 2024** — up to 60% of all
> ER visits are considered non-urgent and
> potentially unnecessary.
>
> **Healthcare Cost Institute, 2024** — average
> ER visit costs $2,400–$2,600 without insurance.
> Average urgent care visit: $185.
> More than 10x cheaper for non-emergencies.
>
> **Estimated $8.3 billion** spent annually on
> ER care that could have been provided in a
> less costly setting.

People Google symptoms at 2am and either panic
into an expensive ER visit or ignore something
that needs attention. SymptomSense answers
the one question that actually matters first:
what level of care do you need right now?

---

## 🛡️ Safety Design

This project is built around responsible AI
design — not just capability.

**7 Safety Layers:**
1. Input validation (Pydantic)
2. Red flag pre-check (rule-based, no LLM)
3. Constrained system prompt
4. API failure fallback (escalate, never downgrade)
5. JSON parse failure handling
6. Medication keyword stripping
7. Pydantic output validation

**Key design decision:**
Emergency detection runs BEFORE the API call.
Rule-based keyword matching is deterministic —
it cannot hallucinate. LLMs are probabilistic.
For life-critical detection, deterministic wins.

See [SAFETY_DESIGN.md](./SAFETY_DESIGN.md)
for full documentation of every decision.

---

## ✨ Features

- 🚨 Always-visible emergency numbers
- 🔍 Real-time red flag detection
  (before form submission)
- 🏥 3 triage levels:
  SEEK_EMERGENCY / SEE_DOCTOR / MONITOR_HOME
- 📊 Urgency score 1–10 with color-coded bar
- ⚠️ Red flags present + watch list
- 📋 Immediate steps (medication-free)
- 👨‍⚕️ What to tell your doctor
- ⚠️ Mandatory disclaimer on every result

---

## 🏗️ Architecture
```
Patient Input (symptoms, age, duration, severity)
          ↓
Layer 1: Pydantic Input Validation
          ↓
Layer 2: Red Flag Pre-Check (rule-based)
   → If flags found: SEEK_EMERGENCY immediately
          ↓
Layer 3: Gemini 2.0 Flash (constrained prompt)
          ↓
Layer 4: API Failure Check
   → If failed: SEE_DOCTOR fallback
          ↓
Layer 5: JSON Parse Check
          ↓
Layer 6: Medication Keyword Stripping
          ↓
Layer 7: Pydantic Output Validation
          ↓
Streamlit UI
```

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| LLM | Gemini 3.1 Flash Instant preview |
| Safety Pre-check | Rule-based (Python) |
| Validation | Pydantic |
| UI | Streamlit |
| Language | Python 3.14 |

---

## 🚀 Run Locally
```bash
git clone https://github.com/vedap24/ai-portfolio
cd 07-symptomsense

source ../venv/bin/activate  # Mac/Linux
..\venv\Scripts\activate     # Windows

pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key" > .env

streamlit run ui.py
```

---

## ⚠️ Disclaimer

SymptomSense is an AI triage assistant for
educational and demonstration purposes.
It is NOT a substitute for professional
medical advice, diagnosis, or treatment.
Always consult a qualified healthcare
provider for medical decisions.
In an emergency, call 112 (India) or
911 (US) immediately.

---

## 📅 Day 7 of 14 — AI Build in Public Challenge

Follow the journey →
[LinkedIn](https://linkedin.com/in/vedapraneeth)