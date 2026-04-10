# 🔍 QueryMind AI

> Ask your database a question in plain English →
> get the SQL query, results, and an explanation.
> Self-correcting agent — if the query fails,
> it reads the error and retries automatically.
> Powered by Gemini 2.0 Flash + SQLite.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-orange)
![SQLite](https://img.shields.io/badge/DB-SQLite-green)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)

---

## 🎯 Real World Problem

> **NL2SQL Research, 2025** —
> Data analysts spend 60–80% of their time
> writing and debugging SQL queries.
> Frontier LLMs now reach 70–85% accuracy
> on clean databases.
>
> **Salesforce acquired Wanii in August 2025**
> — a company specializing in natural language
> for data management — signaling major
> enterprise commitment to conversational
> analytics.
>
> **Snowflake announced a $200 million
> partnership with Anthropic** specifically
> to drive agentic AI in enterprise
> data platforms.

Every company has a database.
Most people who need data can't write SQL.
The gap between "I have a question"
and "I have an answer" is a SQL query.
QueryMind bridges that gap —
with self-correction built in.

---

## 🔄 Self-Correction Architecture

Question → Generate SQL → Execute
↓ (if error)
Read Error Message
↓
Correct SQL with
error context
↓
Execute again
(up to 2 retries)

Most NL-to-SQL tools fail silently.
QueryMind reads the database error,
sends it back to the LLM with full context,
and retries — exactly like a developer
debugging SQL.

---

## ✨ Features

- 💬 Natural language → SQL → Results
- 🔧 Self-correction on query failure
- 💡 Plain-English result explanation
- 📊 Confidence scoring per query
- 🔒 SQL safety validation
  (SELECT only, blocked keywords,
  stacked query detection)
- 📋 Schema browser in sidebar
- 📜 Query history with replay
- ⬇️ Download results as CSV
- 🗄️ Demo e-commerce DB
  (6 tables, 500+ rows)

---

## 🛡️ Safety Design

QueryMind enforces read-only access
at multiple layers:

**Layer 1:** Prompt constraints
→ LLM instructed to generate SELECT only

**Layer 2:** First-word check
→ Rejects any query not starting with SELECT

**Layer 3:** Keyword regex scan
→ Word-boundary detection for DROP, DELETE,
UPDATE, INSERT, TRUNCATE, ALTER, CREATE,
EXEC, GRANT, REVOKE

**Layer 4:** Semicolon detection
→ Prevents stacked queries
(SELECT ...; DELETE ...)

**Why 4 layers:**
Defense in depth — don't trust the
prompt alone. LLMs occasionally generate
dangerous SQL even with constraints.
Validate the output independently.

---

## 🗄️ Demo Database Schema

customers (200 rows)
id, name, email, city, country,
plan, joined_date, ltv

products (32 rows)
id, name, category, price,
cost, stock, rating

orders (500 rows)
id, customer_id, order_date,
status, total_amount, shipping_city

order_items (~1200 rows)
id, order_id, product_id,
quantity, unit_price

reviews (300 rows)
id, product_id, customer_id,
rating, review_date, sentiment

support_tickets (200 rows)
id, customer_id, created_at,
category, status, priority, resolved_at

---

## 💡 Example Questions
What are the top 5 products by revenue?
Which customers placed more than 3 orders?
What is the average order value by country?
How many open high priority support tickets?
What products have a rating above 4.5?
Which city generates the most orders?
What is our refund rate?
Show customers who joined in the last 90 days?

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Natural Language → SQL | Gemini 2.0 Flash |
| Database | SQLite (built-in Python) |
| Safety Validation | Python regex |
| Data Display | Pandas + Streamlit |
| Validation | Pydantic |
| UI | Streamlit |
| Language | Python 3.12 |

---

## 🚀 Run Locally

```bash
git clone https://github.com/vedap24/ai-portfolio
cd 13-querymind

source ../venv/bin/activate  # Mac/Linux
..\venv\Scripts\activate     # Windows

pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key" > .env

streamlit run ui.py
```

Database seeds automatically on first run.

---

## 🧠 What I Learned

- Self-correction is a pattern, not a hack —
  send the error back to the LLM with
  context and it usually fixes it.
  Same as how a developer actually debugs.
- SQL safety requires defense in depth —
  prompt constraints alone are not enough.
  Validate the output independently.
- Schema context is everything for accuracy —
  the more precise the schema description,
  the better the SQL generation.
- Binary search (DSA) maps directly to
  SQL query optimization — narrowing
  down data with WHERE clauses is
  the same divide-and-conquer logic.
- SQLite is underrated for demos —
  zero setup, built-in Python, fast,
  and SQL-compatible enough for
  realistic query generation.

---

## 📅 Day 13 of 14 — AI Build in Public Challenge

Follow the journey →
[LinkedIn](https://linkedin.com/in/vedapraneeth)