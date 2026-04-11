# 🎓 MentorAI

> Tell me your background and goal →
> get a personalized AI engineering curriculum
> with phases, projects, weekly schedule,
> and salary milestones.
> Powered by RAG + Gemini 2.0 Flash.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-orange)
![ChromaDB](https://img.shields.io/badge/RAG-ChromaDB-purple)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)

---

## 🎯 Real World Problem

> **AI Talent Report, 2026** —
> AI talent demand exceeds supply 3.2:1 globally.
> 1.6M open positions, only 518K qualified candidates.
> LLM development, MLOps, and AI ethics show
> the most severe shortages.
>
> **IDC, 2026** — Skills gaps risk $5.5 trillion
> in global losses. Only a third of employees
> received any AI training in the past year.
>
> **PwC, 2025** — AI roles command a 56% wage
> premium over standard data science roles.
> Job postings requiring AI skills skyrocketed
> nearly 200-fold between 2021 and 2025.

Everyone wants to become an AI engineer.
Nobody gives them a personalized roadmap
based on where they are right now.
Generic courses ignore your background.
MentorAI fixes that.

---

## ✨ Features

- 👤 Profile-based personalization
  (8 backgrounds × 7 goals × 4 time options)
- 📊 Readiness score 1–100 with label
- 📚 Phase-by-phase learning curriculum
- ⚡ "Do this today" immediate next step
- 🎯 Biggest gap identification
- 💰 Salary unlock milestone
- ⏱️ Realistic time-to-first-job estimate
- ⏭️ Skills to skip (you already know them)
- 📅 Day-by-day weekly schedule
- 🏗️ Portfolio projects with difficulty + impact
- 🤖 AI mentor chat for follow-up questions
- 📚 RAG on curated AI engineering roadmap

---

## 🏗️ Architecture

User Profile (background + goal + time)
↓
RAG Retrieval (ChromaDB + sentence-transformers)
→ 7 most relevant roadmap sections retrieved
↓
Gemini 2.0 Flash
→ Personalized curriculum generation
→ Phase breakdown
→ Portfolio projects
→ Weekly schedule
↓
Pydantic Validation
→ Field-by-field cleaning
→ Safe defaults for missing fields
→ Type coercion
↓
Streamlit Dashboard

---

## 📚 Knowledge Base

13 curated roadmap documents covering:

| Topic | Level |
|---|---|
| Python & Programming Foundations | Beginner |
| APIs and LLM Integration | Beginner |
| Prompt Engineering | Beginner |
| Structured Output with Pydantic | Beginner |
| RAG — Retrieval Augmented Generation | Intermediate |
| AI Agents and Tool Use | Intermediate |
| Vector Databases | Intermediate |
| Fine-Tuning and Model Customization | Advanced |
| MLOps and Production Deployment | Advanced |
| LLM Evaluation and Testing | Advanced |
| Multimodal AI — Vision + Audio | Advanced |
| AI System Design | Advanced |
| AI Engineering Career Strategy | All levels |

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Knowledge Retrieval | ChromaDB + sentence-transformers |
| Curriculum Generation | Gemini 2.0 Flash |
| Validation | Pydantic |
| UI | Streamlit |
| Language | Python 3.12 |

---

## 🚀 Run Locally

```bash
git clone https://github.com/vedap24/ai-portfolio
cd 14-mentorai

source ../venv/bin/activate  # Mac/Linux
..\venv\Scripts\activate     # Windows

pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key" > .env

streamlit run ui.py
```

---

## 🧠 What I Learned

- RAG on structured knowledge produces
  dramatically better personalization
  than stuffing everything in one prompt —
  retrieval finds what's relevant
  to THIS learner's profile
- Pydantic safe defaults are critical
  for LLM output — always provide fallbacks
  for every field
- The capstone pattern: build a tool
  that uses every technique from your
  portfolio in one project —
  RAG, structured output, agents,
  Streamlit, Pydantic, vector DB
- Don't write brittle assertions on
  LLM output values — test shape
  and type, not specific content
- The product insight: everyone wants
  a learning path but nobody wants
  a generic one — personalization
  is the product

---

## 📅 Day 14 of 14 — AI Build in Public Challenge

The capstone. 14 projects in 14 days.

Follow the journey →
[LinkedIn](https://linkedin.com/in/vedapraneeth)