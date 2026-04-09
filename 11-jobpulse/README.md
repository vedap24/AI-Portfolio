# 📊 JobPulse AI

> Upload your job application CSV →
> get AI-powered insights on response rates,
> funnel drop-off, source performance,
> and a personalized action plan.
> Powered by Pandas + Plotly + Gemini 2.0 Flash.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-orange)
![Pandas](https://img.shields.io/badge/Data-Pandas-green)
![Plotly](https://img.shields.io/badge/Charts-Plotly-purple)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)

---

## 🎯 Real World Problem

> **Upplai Research, March 2026** —
> Indeed response rates: 20–25%.
> LinkedIn: 3–13%.
> Referrals: 8x more likely to get hired.
> Most job seekers never track which
> channel actually works for them.
>
> **Ashby Recruiting Benchmarks, 2025** —
> Average job posting receives 340 applicants,
> a 182% increase from 2021.
> Only 2% of applicants reach interview stage.
> It takes 42 applications on average
> to land one interview.
>
> **Pathrise Analysis, 2025** —
> Average tech job seeker needed 294
> applications to land one offer.

Most job seekers apply blindly.
No tracking. No pattern recognition.
No data on what's working.
JobPulse turns your spreadsheet into
a strategic coaching session.

---

## ✨ Features

- 📉 Visual application funnel
  (Applied → Phone → Technical → Final → Offer)
- 📊 Response rate by source
  (LinkedIn vs Referral vs Direct vs AngelList)
- 🍩 Status distribution chart
- 📅 Weekly application volume timeline
- 🧠 AI performance score (1–100)
- 💡 Headline insight + key pattern analysis
- 🔄 Specific "what to change" recommendations
- 📈 Benchmark vs industry averages
- ⏱️ Predicted timeline to first offer
- 🤖 AI career coach chat (ask follow-up questions)

---

## 🏗️ Architecture

CSV Upload
↓
Data Validation + Cleaning (Pandas)
↓
Metrics Engine
→ Funnel metrics
→ Source breakdown
→ Timeline analysis
→ Company size analysis
↓
Data Summary (text format for LLM)
↓
Gemini 2.0 Flash
→ Performance score
→ Key insights
→ Change recommendations
→ Weekly action plan
→ Benchmark comparison
→ Timeline prediction
↓
Pydantic Validation → Plotly Charts → Streamlit
---

## 📋 CSV Format

Required columns:
company, role, source, status, date_applied

Optional columns:
company_size, industry, notes, salary_range

Valid status values:
Applied, Phone Screen, Technical Interview,
Final Round, Offer, Rejected, No Response

Example:
```csv
company,role,source,status,date_applied
Google,AI Engineer,LinkedIn,Phone Screen,2025-01-15
Stripe,ML Engineer,Referral,Offer,2025-01-20
Meta,Engineer,Direct,No Response,2025-01-22
```

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Data Processing | Pandas |
| Charts | Plotly |
| AI Insights | Gemini 2.0 Flash |
| Validation | Pydantic |
| UI | Streamlit |
| Language | Python 3.12 |

---

## 🚀 Run Locally

```bash
git clone https://github.com/vedap24/ai-portfolio
cd 11-jobpulse

source ../venv/bin/activate  # Mac/Linux
..\venv\Scripts\activate     # Windows

pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key" > .env

streamlit run ui.py
```

Click **"Use Sample Data"** to see
the full dashboard instantly.

---

## 🧠 What I Learned

- Pandas groupby + value_counts is all
  you need for 80% of data analysis —
  no need for complex ML pipelines
- Plotly funnel charts are built for
  exactly this use case — one line of code
- LLMs are better at insight synthesis
  than threshold rules — "referral rate
  is high but volume is low, so prioritize
  networking" requires reasoning
- Graph traversal (DSA) maps directly
  to funnel analysis — tracking nodes
  and transitions between stages
- The "eat your own dog food" principle:
  I used JobPulse on my own job search
  data while building it

---

## 📅 Day 11 of 14 — AI Build in Public Challenge

Follow the journey →
[LinkedIn](https://linkedin.com/in/vedapraneeth)