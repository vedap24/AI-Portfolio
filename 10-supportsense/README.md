# 🎧 SupportSense AI

> AI-powered customer support with
> intelligent escalation logic.
> Answers from KB instantly —
> escalates to humans when needed.
> Powered by RAG + Gemini 2.0 Flash.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-orange)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)

---

## 🎯 Real World Problem

> **Gartner, 2026** — 98% of customer service
> leaders say smooth AI-to-human transitions
> are essential. 90% admit they struggle
> with handoffs. Getting escalation right
> matters more than the AI itself.
>
> **AI Customer Service Market, 2026** —
> $15.12 billion market. Companies see
> $3.50 return for every $1 invested.
> Klarna's AI handled 2/3 of all support
> conversations — equivalent to 700 agents.
>
> **Cost per interaction dropped 68%** —
> from $4.60 to $1.45 after AI implementation.
> (2025 industry benchmarks)

The problem isn't building a chatbot.
Every company has a chatbot.
The problem is knowing when NOT to answer —
and handing off with full context
when escalation is needed.
That's what SupportSense solves.

---

## 🏗️ Architecture

Customer Query
↓
Input Validation
↓
RAG Retrieval (ChromaDB + sentence-transformers)
↓
Intent Classifier
→ Keyword pre-check (fast, deterministic)
→ LLM classification (nuanced)
↓
┌─────────────────┬──────────────────────┐
│   ANSWERABLE    │     ESCALATE         │
│                 │                      │
│ Generate answer │ Create ticket        │
│ from KB only    │ with priority,       │
│                 │ department,          │
│ If LOW conf →   │ sentiment,           │
│ re-escalate     │ context for agent    │
└─────────────────┴──────────────────────┘
↓
Pydantic Validation → Streamlit UI

---

## ✨ Features

- 📚 RAG from custom knowledge base
  (runs locally, zero cost)
- 🎯 Intent classification:
  answerable / billing / complaint /
  technical / unknown
- ✅ Cited answers with source sections
- 🔺 Structured escalation tickets with:
  priority, department, sentiment,
  suggested resolution, agent context
- 📊 Auto-resolution rate tracker
- 💡 Follow-up question suggestions
- ⚡ Keyword pre-check before LLM call
- 🔄 Low-confidence answers auto-escalate

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| KB Embeddings | sentence-transformers (local) |
| Vector Store | ChromaDB (local) |
| Intent + Answer | Gemini 2.0 Flash |
| Validation | Pydantic |
| UI | Streamlit |
| Language | Python 3.12 |

---

## 🚀 Run Locally
```bash
git clone https://github.com/vedap24/ai-portfolio
cd 10-supportsense

source ../venv/bin/activate  # Mac/Linux
..\venv\Scripts\activate     # Windows

pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key" > .env

streamlit run ui.py
```

---

## 🧠 What I Learned

- The escalation logic is more valuable
  than the answer logic —
  knowing when NOT to answer is the
  senior engineering insight
- Two-step intent classification:
  keyword check first (no API cost),
  LLM second (nuanced cases only)
- Confidence threshold routing —
  LOW confidence answers auto-escalate
  rather than risk giving wrong info
- RAG without source citation = guessing.
  RAG with source citation = trust.
- Pydantic's Optional fields let
  one model handle both answer
  and escalation responses cleanly

---

## 📅 Day 10 of 14 — AI Build in Public Challenge

Follow the journey →
[LinkedIn](https://linkedin.com/in/vedapraneeth)