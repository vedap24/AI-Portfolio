# 🔍 ResumeLens AI

> AI-powered resume fit scorer — paste a Job Description + Resume, get an instant match score powered by Gemini 2.5 Flash.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)

---

## 🎯 Problem It Solves

Recruiters spend 7 seconds per resume. Job seekers apply blindly.
80% of applications fail due to keyword mismatches — not skill gaps.

ResumeLens AI gives candidates instant, honest feedback before they apply.

---

## ✨ Features

- ✅ Fit score out of 100 with color-coded label
- ✅ Matched vs missing skills breakdown
- ✅ Top 3 strengths + improvement tips
- ✅ Experience gap analysis
- ✅ Auto-retry on API failures
- ✅ Input validation with friendly error messages

---

## 🏗️ Architecture
```
User Input (JD + Resume)
        ↓
  Input Validation
        ↓
  Prompt Builder (prompts.py)
        ↓
  Gemini 2.5 Flash API
        ↓
  JSON Parser + Validator
        ↓
  Pydantic Model (models.py)
        ↓
  Streamlit UI (ui.py)
```

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| LLM | Google Gemini 2.5 Flash |
| Backend | Python 3.12 |
| Data validation | Pydantic |
| Frontend | Streamlit |
| API client | google-genai |

---

## 🚀 Run Locally
```bash
# Clone the repo
git clone https://github.com/vedap24/resumelens-ai
cd resumelens-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Add your Gemini API key
echo "GEMINI_API_KEY=your_key_here" > .env

# Run the app
streamlit run ui.py
```

---

## 📸 Demo


[Demo Screenshot]
(demo.png)
(demo1.png)

---

## 🧠 What I Learned Building This

- Prompt engineering for structured JSON output
- Pydantic for LLM output validation
- Handling Gemini response edge cases (markdown fences, type mismatches)
- Auto-retry logic for API flakiness

---

## 📅 Built as part of my 14-Day AI Build-in-Public Challenge

Follow the journey on [LinkedIn](https://www.linkedin.com/in/vedapraneeth/)

> Day 1 of 14 — ResumeLens AI