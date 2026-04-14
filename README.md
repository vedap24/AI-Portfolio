# 🤖 AI Portfolio — 14 Projects in 14 Days

> Built by **Veda Praneeth** · MS CS (USA) · AI Engineer  
> **14 production-ready AI systems** shipped in 14 consecutive days.  
> Every project is deployed, documented, and explained from first principles.

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)](https://python.org)
[![Gemini](https://img.shields.io/badge/LLM-Gemini%202.0%20Flash-orange?style=flat-square)](https://ai.google.dev)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?style=flat-square)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## 👤 About

I am an AI engineer who spent 14 days building and shipping one production-quality AI system per day — documented publicly on LinkedIn. Every project covers a different technique: RAG, multi-agent orchestration, voice pipelines, NL-to-SQL, responsible AI safety design, and more.

- 📧 vedapraneeth9@gmail.com
- 💼 [LinkedIn](https://linkedin.com/in/vedapraneeth)

---

## 🗂️ Project Index

| # | Project | Techniques | Stack |
|---|---------|------------|-------|
| 01 | [ResumeLens AI](#01---resumelens-ai) | Prompt Engineering, Structured Output | Gemini, Pydantic, Streamlit |
| 02 | [MeetingMind](#02---meetingmind) | Audio Pipeline, Whisper | faster-whisper, Gemini, Streamlit |
| 03 | [ClauseGuard](#03---clauseguard) | RAG, PDF Parsing | ChromaDB, sentence-transformers, Gemini |
| 04 | [PitchBot](#04---pitchbot) | Prompt Chaining, Web Scraping | Gemini, BeautifulSoup, Streamlit |
| 05 | [BrainBase](#05---brainbase) | Multi-doc RAG, Citation | ChromaDB, PyMuPDF, python-docx |
| 06 | [CompeteAI](#06---competeai) | ReAct Agent, Web Search | Tavily, Gemini, Streamlit |
| 07 | [SymptomSense](#07---symptomsense) | Responsible AI, Safety Design | Gemini, Pydantic, Streamlit |
| 08 | [PRReview AI](#08---prreview-ai) | GitHub API, Map-Reduce | PyGitHub, Gemini, Pydantic |
| 09 | [ResearchForge](#09---researchforge) | Multi-Agent, State Machine | Tavily, Gemini, Pydantic |
| 10 | [SupportSense](#10---supportsense) | RAG + Routing, Intent Classification | ChromaDB, Gemini, Streamlit |
| 11 | [JobPulse](#11---jobpulse) | Data Analysis, LLM Insights | Pandas, Plotly, Gemini |
| 12 | [FieldReport AI](#12---fieldreport-ai) | Voice Pipeline, Structured Extraction | faster-whisper, Gemini, Pydantic |
| 13 | [QueryMind](#13---querymind) | NL-to-SQL, Self-Correction | SQLite, Gemini, Pydantic |
| 14 | [MentorAI](#14---mentorai) | RAG, Personalized Curriculum | ChromaDB, Gemini, Streamlit |

---

## 🛠️ Shared Tech Stack

All 14 projects share a single Python 3.12 virtual environment with these core packages:

```
google-genai          # Gemini 2.0 Flash API
streamlit             # UI for all projects
pydantic              # Output validation (used in every project)
python-dotenv         # Environment variable management
faster-whisper        # Local speech-to-text (Days 2, 12)
pymupdf               # PDF parsing (Days 3, 5)
sentence-transformers # Text embeddings (Days 3, 5, 10, 14)
chromadb              # Vector database (Days 3, 5, 10, 14)
python-docx           # Word document parsing (Day 5)
requests              # HTTP requests (Day 4)
beautifulsoup4        # Web scraping (Day 4)
tavily-python         # Web search API (Days 6, 9)
PyGithub              # GitHub API (Day 8)
pandas                # Data analysis (Day 11)
plotly                # Charts (Day 11)
```

---

## 📁 Repository Structure

```
ai-portfolio/
├── 01-resumelens-ai/
├── 02-meetingmind/
├── 03-clauseguard/
├── 04-pitchbot/
├── 05-brainbase/
├── 06-competeai/
├── 07-symptomsense/
│   └── SAFETY_DESIGN.md
├── 08-prreview-ai/
├── 09-researchforge/
├── 10-supportsense/
├── 11-jobpulse/
├── 12-fieldreport-ai/
├── 13-querymind/
├── 14-mentorai/
└── README.md
```

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/vedap24/AI-Portfolio
cd AI-Portfolio

# Create shared virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install all dependencies
pip install google-genai streamlit pydantic python-dotenv faster-whisper \
            pymupdf sentence-transformers chromadb python-docx requests \
            beautifulsoup4 tavily-python PyGithub pandas plotly

# Add your API key (required for all projects)
echo "GEMINI_API_KEY=your_key_here" > .env

# Run any project
cd 01-resumelens-ai
streamlit run ui.py
```

**Free API keys needed:**
- [Gemini API](https://ai.google.dev) — 1500 requests/day free
- [Tavily API](https://tavily.com) — 1000 searches/month free (Days 6, 9)
- [GitHub Token](https://github.com/settings/tokens) — free (Day 8)

---

## Project Details

---

### 01 — ResumeLens AI

**What it does:** Scores a resume against a job description and returns structured fit analysis with gap identification.

**Key technique:** Prompt engineering with Pydantic-validated JSON output. The system prompt specifies exact JSON schema — the LLM fills it, Pydantic validates it.

**What I learned:** Escaping `{{}}` in Python `.format()` strings when the prompt itself contains JSON template syntax.

**Stack:** `Gemini 2.0 Flash · Pydantic · Streamlit`

```bash
cd 01-resumelens-ai && streamlit run ui.py
```

---

### 02 — MeetingMind

**What it does:** Uploads an audio recording of a meeting and returns a structured brief — summary, action items, decisions, follow-ups.

**Key technique:** Local speech-to-text with faster-whisper (Systran), then structured extraction with Gemini. Audio never leaves the machine.

**What I learned:** faster-whisper model weights download from HuggingFace Hub on first run. The unauthenticated download warning is harmless.

**Stack:** `faster-whisper · Gemini 2.0 Flash · Streamlit · Pydantic`

```bash
cd 02-meetingmind && streamlit run ui.py
```

---

### 03 — ClauseGuard

**What it does:** Uploads a legal contract PDF and scans every clause for risk — flagging severity, explanation, and recommended action.

**Key technique:** Paragraph-level RAG chunking (beats token chunking for legal docs). Each clause embedded separately, retrieved by semantic similarity to risk-pattern queries.

**What I learned:** Paragraph chunking preserves legal clause context far better than fixed-size token chunks. The chunk boundary IS the clause boundary.

**Stack:** `PyMuPDF · sentence-transformers · ChromaDB · Gemini 2.0 Flash · Pydantic · Streamlit`

> ⚠️ Not legal advice. For educational demonstration only.

```bash
cd 03-clauseguard && streamlit run ui.py
```

---

### 04 — PitchBot

**What it does:** Takes a prospect's LinkedIn profile text and generates 3 personalized cold email variants — short, medium, and detailed.

**Key technique:** 3-step prompt chain. Step 1 extracts profile signals. Step 2 maps signals to value props. Step 3 writes the email. Each step builds on the previous.

**What I learned:** LinkedIn scraping is blocked — paste-the-profile-text approach is faster and more reliable than scraping. Chaining prompts beats one large prompt for quality.

**Stack:** `requests · BeautifulSoup · Gemini 2.0 Flash · Streamlit · Pydantic`

```bash
cd 04-pitchbot && streamlit run ui.py
```

---

### 05 — BrainBase

**What it does:** Upload multiple documents (PDF, DOCX, TXT) and ask questions across all of them — with source citations per answer.

**Key technique:** Multi-format RAG with paragraph + 50-word overlap chunking. Overlap prevents context loss at chunk boundaries. Source citation is enforced at the prompt level.

**What I learned:** Overlap chunking is critical — without it, answers that span two chunks get cut off mid-reasoning.

**Stack:** `PyMuPDF · python-docx · sentence-transformers · ChromaDB · Gemini 2.0 Flash · Streamlit`

```bash
cd 05-brainbase && streamlit run ui.py
```

---

### 06 — CompeteAI

**What it does:** Enter your company and up to 3 competitors — an AI agent searches the web in real-time and generates a structured competitive intelligence brief in under 90 seconds.

**Key technique:** ReAct agent pattern. Step 1: Gemini plans 8 strategic search queries. Step 2: Tavily executes searches. Step 3: Filter noise. Step 4: Gemini synthesizes brief.

**What I learned:** The planning step matters more than the execution step. A well-designed query plan beats fast search execution every time.

**Stack:** `Tavily Search API · Gemini 2.0 Flash · Pydantic · Streamlit`

**Extra API needed:** `TAVILY_API_KEY` in `.env`

```bash
cd 06-competeai && streamlit run ui.py
```

---

### 07 — SymptomSense

**What it does:** Describes symptoms → returns triage level (ER / See Doctor / Monitor at Home) with reasoning, red flags, and immediate steps. Never diagnoses.

**Key technique:** 7-layer safety architecture. Emergency detection runs **before** the API call using deterministic keyword matching — rule-based systems cannot hallucinate.

**Safety layers:**
1. Pydantic input validation
2. Rule-based red flag pre-check (no API call)
3. Constrained system prompt (positive + negative)
4. API failure fallback (escalates, never downgrades)
5. JSON parse failure handler
6. Medication keyword stripper (post-LLM)
7. Pydantic output validation + disclaimer enforcement

**What I learned:** For life-critical detection, deterministic always beats probabilistic. The most important safety layer is the one that runs before the LLM.

**Stack:** `Gemini 2.0 Flash · Pydantic · Streamlit`

> See [`07-symptomsense/SAFETY_DESIGN.md`](07-symptomsense/SAFETY_DESIGN.md) for full safety documentation.

```bash
cd 07-symptomsense && streamlit run ui.py
```

---

### 08 — PRReview AI

**What it does:** Paste a GitHub PR URL → get a full AI code review with bugs, security issues, performance problems, style feedback, and a ready-to-paste GitHub review comment.

**Key technique:** Map-reduce pattern. Map: each changed file reviewed independently by Gemini. Reduce: all file reviews synthesized into one PR-level verdict + suggested comment.

**What I learned:** Diff parsing is messier than expected. Binary files, lock files, truncation — all need explicit handling before the LLM ever sees the code.

**Stack:** `PyGitHub · Gemini 2.0 Flash · Pydantic · Streamlit`

**Extra API needed:** `GITHUB_TOKEN` in `.env` (needs `repo` scope)

```bash
cd 08-prreview-ai && streamlit run ui.py
```

---

### 09 — ResearchForge

**What it does:** Enter any research question → 4 specialized AI agents plan, search, verify, and synthesize a full research brief in under 4 minutes.

**Agent pipeline:**
- **Planner** — breaks query into 4 targeted sub-questions
- **Researcher** — executes web searches via Tavily
- **Fact Checker** — verifies, scores confidence, detects contradictions
- **Writer** — synthesizes verified facts into structured report

**Key technique:** Manual state machine (no LangGraph). Shared state dict passed between agents. Dependency injection — `call_gemini` passed as function reference for testability.

**What I learned:** The Fact Checker is the most valuable agent. Without it, the Writer synthesizes garbage from noisy web results. Quality gate before synthesis — not after.

**Stack:** `Tavily Search API · Gemini 2.0 Flash · Pydantic · Streamlit · Python`

**Extra API needed:** `TAVILY_API_KEY` in `.env`

```bash
cd 09-researchforge && streamlit run ui.py
```

---

### 10 — SupportSense

**What it does:** AI customer support agent for a demo SaaS product (FlowDesk). Answers from KB instantly — escalates to humans with a structured ticket when needed.

**Key technique:** Two-step intent classification. Step 1: keyword pre-check (no API call) — handles 60% of cases instantly. Step 2: LLM classification for nuanced cases. RAG retrieval on 10-document knowledge base with confidence gating.

**Escalation ticket includes:** priority, department routing, customer sentiment, suggested resolution, full context for the human agent.

**What I learned:** The escalation logic is more valuable than the answer logic. Knowing when NOT to answer is the senior engineering insight.

**Stack:** `sentence-transformers · ChromaDB · Gemini 2.0 Flash · Pydantic · Streamlit`

```bash
cd 10-supportsense && streamlit run ui.py
```

---

### 11 — JobPulse

**What it does:** Upload your job application CSV → get AI-powered insights on response rates, funnel drop-off, source performance, and a personalized weekly action plan.

**Metrics calculated:**
- Response rate by source (LinkedIn vs Referral vs Direct)
- Application funnel (Applied → Phone → Technical → Final → Offer)
- Ghost rate, interview rate, offer rate
- Benchmark vs industry averages

**What I learned:** Referral response rate is typically 3-5x higher than LinkedIn cold applications. The data makes this visible. Most job seekers never measure it.

**Stack:** `Pandas · Plotly · Gemini 2.0 Flash · Pydantic · Streamlit`

```bash
cd 11-jobpulse && streamlit run ui.py
```

---

### 12 — FieldReport AI

**What it does:** Speak a field report → get structured JSON data instantly. Supports 3 report types: site inspection, sales visit, delivery log.

**Key technique:** Local audio transcription with faster-whisper (runs on CPU, no cloud) → domain-specific structured extraction with Gemini. Audio never leaves the machine.

**What I learned:** Domain-specific prompts with explicit JSON schemas extract dramatically better data than generic extraction. The schema in the prompt IS the product.

**Stack:** `faster-whisper · Gemini 2.0 Flash · Pydantic · Streamlit`

```bash
cd 12-fieldreport-ai && streamlit run ui.py
```

---

### 13 — QueryMind

**What it does:** Ask your database a question in plain English → get the SQL query, results, and a plain-English explanation. Self-corrects on failure.

**Self-correction loop:**
```
Generate SQL → Execute → Error?
→ Send error back to Gemini with context
→ Gemini reads error and fixes query
→ Execute again (up to 2 retries)
```

**Safety layers:**
1. Prompt constraint (SELECT only)
2. First-word check (rejects non-SELECT)
3. Keyword regex scan (blocks DROP/DELETE/UPDATE/INSERT etc.)
4. Semicolon detection (prevents stacked queries)

**Demo database:** E-commerce SQLite DB with 6 tables, 500+ rows (customers, products, orders, reviews, support tickets).

**Stack:** `SQLite · Gemini 2.0 Flash · Pydantic · Streamlit`

```bash
cd 13-querymind && streamlit run ui.py
```

---

### 14 — MentorAI

**What it does:** Select your background and goal → get a personalized AI engineering curriculum with phases, projects, weekly schedule, salary milestones, and an AI mentor chat.

**Key technique:** RAG on 13 curated roadmap documents. Retrieval query built from learner profile — different backgrounds retrieve different sections. Pydantic validates every field with safe defaults for missing data.

**Output includes:** readiness score, phase-by-phase path, skills to skip, biggest gap, salary unlock, time-to-first-job estimate, portfolio project recommendations, day-by-day weekly schedule.

**Stack:** `ChromaDB · sentence-transformers · Gemini 2.0 Flash · Pydantic · Streamlit`

```bash
cd 14-mentorai && streamlit run ui.py
```

---

## 🧠 Key Patterns Across All 14 Projects

**RAG (used in Days 3, 5, 10, 14)**
Embed documents → store in ChromaDB → embed query → retrieve top-k → send to LLM as context. The LLM answers only from retrieved content.

**Pydantic validation (used in every project)**
LLM output is unreliable. Pydantic validates every field, provides safe defaults, and prevents runtime crashes. Never trust raw LLM JSON without validation.

**Defense in depth (Days 7, 13)**
Never rely on a single safety layer. Prompt constraints + output validation + post-processing. Each layer catches what the previous missed.

**Self-correction (Day 13)**
When a query fails, send the error back to the LLM as context. LLMs are surprisingly good at reading error messages and fixing their own output.

**Map-reduce for AI (Day 8)**
Process N items independently (map), then synthesize results (reduce). Scales better than trying to process everything in one prompt.

**Two-step classification (Day 10)**
Keyword scan first (no API cost, catches obvious cases), LLM second (handles nuanced cases). Cuts API calls by 60%.

---

## 📊 Build-in-Public Stats

- **14 projects** shipped in **14 consecutive days**
- **6 projects** deployed on Streamlit Cloud
- **8 projects** run locally (use local models — faster-whisper, sentence-transformers)
- **4 external APIs** used: Gemini, Tavily, GitHub, HuggingFace
- **0 paid API calls** — all APIs used on free tiers

---

## 📄 License

MIT License — use any code for learning, personal projects, or commercial work.

---

## 🤝 Connect

Building in public. Every project documented on LinkedIn with the architecture decisions, stats, and what I learned.


[![LinkedIn](https://img.shields.io/badge/LinkedIn-vedapraneeth-blue?style=flat-square&logo=linkedin)](https://linkedin.com/in/vedapraneeth)
[![GitHub](https://img.shields.io/badge/GitHub-vedap24-black?style=flat-square&logo=github)](https://github.com/vedap24)
[![Email](https://img.shields.io/badge/Email-vedapraneeth9@gmail.com-red?style=flat-square)](mailto:vedapraneeth9@gmail.com)

---

*14 projects. 14 days. One portfolio that didn't exist two weeks ago.*
