import os
import json
import time
import re
from dotenv import load_dotenv
from google import genai
from models import SQLResult, QueryResult
from prompts import (
    SQL_GENERATION_PROMPT,
    SQL_CORRECTION_PROMPT,
    RESULT_EXPLANATION_PROMPT
)
from database import (
    get_schema,
    execute_query,
    build_database,
    DB_PATH
)

load_dotenv()

# ── Gemini client ──
gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
GEMINI_MODEL = "gemini-3.1-flash-lite-preview"
MAX_RETRIES  = 2

# ── Safety: blocked SQL keywords ──
BLOCKED_KEYWORDS = [
    "DROP", "DELETE", "UPDATE",
    "INSERT", "TRUNCATE", "ALTER",
    "CREATE", "REPLACE", "MERGE",
    "EXEC", "EXECUTE", "GRANT",
    "REVOKE", "ATTACH", "DETACH"
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
        f"Gemini API failed: {last_error}"
    )


# ──────────────────────────────────────────
# INPUT + SQL SAFETY VALIDATORS
# ──────────────────────────────────────────

def validate_question(question: str) -> str:
    """Validate and clean user question."""
    if not question or \
       not question.strip():
        raise ValueError(
            "Please enter a question."
        )

    cleaned = question.strip()

    if len(cleaned.split()) < 2:
        raise ValueError(
            "Question too short. "
            "Please be more specific."
        )

    if len(cleaned) > 500:
        raise ValueError(
            "Question too long. "
            "Max 500 characters."
        )

    return cleaned


def validate_sql_safety(sql: str) -> str:
    """
    Multi-layer SQL safety check.

    Layer 1: Must start with SELECT
    Layer 2: No dangerous keywords anywhere
    Layer 3: No semicolons mid-query
             (prevents stacked queries)
    Layer 4: Reasonable length

    Why this matters:
    Even with prompt constraints, LLMs can
    occasionally generate dangerous SQL.
    Defense in depth — validate the output
    regardless of what the prompt says.
    """
    if not sql or not sql.strip():
        raise ValueError(
            "Empty SQL generated."
        )

    sql_clean = sql.strip()

    # Layer 1: Must be SELECT
    first_word = sql_clean.split()[0].upper() \
        if sql_clean.split() else ""

    if first_word != "SELECT":
        raise ValueError(
            f"Generated query must start with "
            f"SELECT, got '{first_word}'. "
            f"Only read operations allowed."
        )

    # Layer 2: No dangerous keywords
    # Use word boundaries to avoid false positives
    # e.g. "update" in column name
    sql_upper = sql_clean.upper()
    for keyword in BLOCKED_KEYWORDS:
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, sql_upper):
            raise ValueError(
                f"Query contains blocked "
                f"keyword: {keyword}. "
                f"Only SELECT queries allowed."
            )

    # Layer 3: Single statement only
    # Allow semicolon only at very end
    sql_no_end = sql_clean.rstrip(";").rstrip()
    if ";" in sql_no_end:
        raise ValueError(
            "Query contains multiple statements. "
            "Only single SELECT allowed."
        )

    # Layer 4: Reasonable length
    if len(sql_clean) > 3000:
        raise ValueError(
            "Generated SQL too long. "
            "Please simplify your question."
        )

    return sql_clean


# ──────────────────────────────────────────
# SQL GENERATION
# ──────────────────────────────────────────

def parse_sql_result(
    raw: str,
    question: str
) -> SQLResult:
    """
    Parse Gemini's SQL generation response.
    Handles JSON parse failures gracefully.
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract SQL directly
        sql_match = re.search(
            r'SELECT\s+.+?(?=\n\n|\Z)',
            raw,
            re.DOTALL | re.IGNORECASE
        )
        if sql_match:
            sql = sql_match.group(0).strip()
            return SQLResult(
                sql=sql,
                explanation=(
                    "SQL extracted from response."
                ),
                tables_used=[],
                confidence="LOW"
            )
        raise RuntimeError(
            "Could not parse SQL generation "
            "response. Please try again."
        )

    sql = str(data.get("sql", "")).strip()
    if not sql:
        raise RuntimeError(
            "No SQL in generated response. "
            "Please rephrase your question."
        )

    # Validate confidence
    confidence = str(
        data.get("confidence", "MEDIUM")
    ).upper()
    if confidence not in [
        "HIGH", "MEDIUM", "LOW"
    ]:
        confidence = "MEDIUM"

    # Validate tables list
    tables = data.get("tables_used", [])
    if not isinstance(tables, list):
        tables = []
    tables = [
        str(t) for t in tables if t
    ]

    explanation = str(
        data.get(
            "explanation",
            "Query generated."
        )
    )

    return SQLResult(
        sql=sql,
        explanation=explanation,
        tables_used=tables,
        confidence=confidence
    )


def generate_sql(
    question: str,
    schema: str
) -> SQLResult:
    """Generate SQL from natural language."""
    prompt = SQL_GENERATION_PROMPT.format(
        schema=schema,
        question=question
    )

    raw = call_gemini(prompt)
    raw = clean_gemini_response(raw)

    result = parse_sql_result(raw, question)

    # Safety validate the generated SQL
    result.sql = validate_sql_safety(
        result.sql
    )

    return result


def correct_sql(
    question: str,
    failed_sql: str,
    error: str,
    schema: str
) -> SQLResult:
    """
    Self-correction with error context.

    Key insight: send the EXACT error
    message back to Gemini. LLMs are
    surprisingly good at reading database
    error messages and fixing the query.

    This mirrors how a developer would
    actually debug SQL:
    run it → read the error → fix it.
    """
    # Truncate long errors for prompt
    error_truncated = error[:300] \
        if len(error) > 300 else error

    prompt = SQL_CORRECTION_PROMPT.format(
        schema=schema,
        question=question,
        failed_sql=failed_sql,
        error=error_truncated
    )

    try:
        raw = call_gemini(prompt)
        raw = clean_gemini_response(raw)
        result = parse_sql_result(raw, question)
        result.sql = validate_sql_safety(
            result.sql
        )
        return result

    except ValueError as e:
        # Safety validation failed on correction
        raise ValueError(
            f"Corrected SQL failed safety "
            f"check: {e}"
        )
    except Exception as e:
        raise RuntimeError(
            f"Self-correction failed: {e}"
        )


def explain_results(
    question: str,
    sql: str,
    columns: list,
    rows: list
) -> str:
    """Plain-English result explanation."""
    if not rows:
        return (
            "The query returned no results. "
            "The filters may be too specific, "
            "or this data may not exist in "
            "the database."
        )

    if not columns:
        return (
            f"Query returned {len(rows)} row(s)."
        )

    results_preview = str(rows[:10])

    prompt = RESULT_EXPLANATION_PROMPT.format(
        question=question,
        sql=sql,
        columns=columns,
        results=results_preview,
        total_rows=len(rows)
    )

    try:
        return call_gemini(prompt)
    except Exception:
        return (
            f"Query returned {len(rows)} "
            f"result(s) with columns: "
            f"{', '.join(columns[:5])}."
        )


# ──────────────────────────────────────────
# MAIN AGENT
# ──────────────────────────────────────────

def run_query(
    question: str,
    schema: str = None
) -> QueryResult:
    """
    Full NL→SQL agent pipeline with
    self-correction loop.

    Flow:
    Validate → Generate → Execute →
    [Error? → Correct → Execute] × MAX_RETRIES
    → Explain → Return
    """

    # Validate input
    question = validate_question(question)

    # Load schema
    if schema is None:
        schema = get_schema()

    if not schema:
        raise RuntimeError(
            "Database schema is empty. "
            "Ensure database is initialized."
        )

    print(
        f"\n🔍 Query: {question[:60]}..."
    )

    # ── Generate SQL ──
    print("  🤖 Generating SQL...")
    try:
        sql_result = generate_sql(
            question, schema
        )
    except ValueError as e:
        # Safety validation failed
        return QueryResult(
            question=question,
            sql="",
            sql_explanation=str(e),
            columns=[],
            rows=[],
            row_count=0,
            result_explanation=str(e),
            tables_used=[],
            confidence="LOW",
            retried=False,
            retry_count=0,
            error=str(e)
        )

    print(
        f"  📝 {sql_result.sql[:80]}..."
    )

    # ── Execute with self-correction loop ──
    retry_count = 0
    retried     = False

    cols, rows, error = execute_query(
        sql_result.sql
    )

    while error and retry_count < MAX_RETRIES:
        print(
            f"  ⚠️  Error (attempt "
            f"{retry_count + 1}): "
            f"{error[:50]}..."
        )

        retried = True
        retry_count += 1

        try:
            sql_result = correct_sql(
                question,
                sql_result.sql,
                error,
                schema
            )
            print(
                f"  🔧 Corrected: "
                f"{sql_result.sql[:60]}..."
            )
            cols, rows, error = execute_query(
                sql_result.sql
            )

        except (ValueError, RuntimeError) as e:
            error = str(e)
            break

    if error:
        print(
            f"  ❌ Failed after "
            f"{retry_count} correction(s)"
        )
        return QueryResult(
            question=question,
            sql=sql_result.sql,
            sql_explanation=sql_result.explanation,
            columns=[],
            rows=[],
            row_count=0,
            result_explanation=(
                f"Query failed after "
                f"{retry_count} correction "
                f"attempt(s). "
                f"Try rephrasing your question."
            ),
            tables_used=sql_result.tables_used,
            confidence="LOW",
            retried=retried,
            retry_count=retry_count,
            error=error
        )

    print(
        f"  ✅ {len(rows)} rows returned"
    )

    # ── Explain results ──
    explanation = explain_results(
        question, sql_result.sql, cols, rows
    )

    return QueryResult(
        question=question,
        sql=sql_result.sql,
        sql_explanation=sql_result.explanation,
        columns=cols,
        rows=rows,
        row_count=len(rows),
        result_explanation=explanation,
        tables_used=sql_result.tables_used,
        confidence=sql_result.confidence,
        retried=retried,
        retry_count=retry_count,
        error=None
    )


# ───── Tests ─────
if __name__ == "__main__":

    build_database()
    schema = get_schema()

    print("\n🧪 Test 1: Simple count")
    r1 = run_query(
        "How many customers do we have?",
        schema
    )
    assert r1.error is None, r1.error
    assert r1.row_count >= 1
    assert r1.confidence in [
        "HIGH", "MEDIUM", "LOW"
    ]
    print(
        f"  ✅ Rows       : {r1.row_count}"
    )
    print(
        f"     Result    : {r1.rows[0]}"
    )
    print(
        f"     Confidence: {r1.confidence}"
    )

    print("\n🧪 Test 2: Aggregation query")
    r2 = run_query(
        "What are the top 5 products "
        "by total revenue?",
        schema
    )
    assert r2.error is None, r2.error
    assert r2.row_count > 0
    print(
        f"  ✅ Rows    : {r2.row_count}"
    )
    print(
        f"     Tables : {r2.tables_used}"
    )

    print("\n🧪 Test 3: Filter + join")
    r3 = run_query(
        "Show me all open high priority "
        "support tickets",
        schema
    )
    assert r3.error is None, r3.error
    print(
        f"  ✅ Rows    : {r3.row_count}"
    )
    print(
        f"     Columns: {r3.columns[:4]}"
    )

    print("\n🧪 Test 4: SQL safety — DROP")
    try:
        validate_sql_safety(
            "DROP TABLE customers"
        )
        print("  ❌ Should have raised!")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 5: SQL safety — stacked")
    try:
        validate_sql_safety(
            "SELECT * FROM customers; "
            "DELETE FROM orders"
        )
        print("  ❌ Should have raised!")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 6: SQL safety — UPDATE")
    try:
        validate_sql_safety(
            "UPDATE customers SET plan='Free'"
        )
        print("  ❌ Should have raised!")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 7: Short question")
    try:
        validate_question("hi")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 8: Empty question")
    try:
        validate_question("")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 9: Result explanation")
    expl = explain_results(
        "How many customers?",
        "SELECT COUNT(*) FROM customers",
        ["total"],
        [(200,)]
    )
    assert len(expl) > 10
    print(
        f"  ✅ Explanation: {expl[:80]}..."
    )

    print("\n🧪 Test 10: Valid SELECT passes")
    try:
        sql = validate_sql_safety(
            "SELECT * FROM customers LIMIT 10"
        )
        print(f"  ✅ Valid SQL passed: {sql[:40]}")
    except ValueError as e:
        print(f"  ❌ Should not raise: {e}")

    print("\n✅ All 10 tests passed.")