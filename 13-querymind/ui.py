import streamlit as st
import pandas as pd
from app import run_query, call_gemini
from database import (
    build_database,
    get_schema,
    DB_PATH
)
from prompts import SUGGESTED_QUESTIONS

# ── Ensure DB exists ──
build_database()
SCHEMA = get_schema()

# ── Page config ──
st.set_page_config(
    page_title="QueryMind AI",
    page_icon="🔍",
    layout="wide"
)

# ── Custom CSS ──
st.markdown("""
<style>
    .stApp { background-color: #07090f; }

    .main-title {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(
            90deg, #22d3ee, #818cf8
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }

    .subtitle {
        color: #64748b;
        font-size: 0.95rem;
        margin-top: 4px;
        margin-bottom: 24px;
    }

    .sql-box {
        background: #0d1117;
        border: 1px solid #1e2a3a;
        border-left: 3px solid #22d3ee;
        border-radius: 0 10px 10px 0;
        padding: 16px 20px;
        font-family: 'JetBrains Mono',
                     'Fira Code', monospace;
        font-size: 0.82rem;
        color: #67e8f9;
        line-height: 1.75;
        white-space: pre-wrap;
        overflow-x: auto;
        margin-bottom: 12px;
    }

    .explain-box {
        background: rgba(129,140,248,0.05);
        border: 1px solid rgba(129,140,248,0.15);
        border-radius: 10px;
        padding: 14px 18px;
        font-size: 0.88rem;
        color: #c7d2fe;
        line-height: 1.8;
        margin-bottom: 16px;
    }

    .result-explain-box {
        background: rgba(34,211,238,0.04);
        border: 1px solid rgba(34,211,238,0.15);
        border-radius: 10px;
        padding: 14px 18px;
        font-size: 0.88rem;
        color: #a5f3fc;
        line-height: 1.8;
        margin-bottom: 16px;
    }

    .stat-box {
        background: #0d1117;
        border: 1px solid #1e2a3a;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }

    .stat-num {
        font-size: 1.8rem;
        font-weight: 900;
    }

    .stat-label {
        font-size: 0.65rem;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .confidence-HIGH {
        background: rgba(52,211,153,0.1);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.25);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
    }

    .confidence-MEDIUM {
        background: rgba(251,191,36,0.1);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.25);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
    }

    .confidence-LOW {
        background: rgba(248,113,113,0.1);
        color: #f87171;
        border: 1px solid rgba(248,113,113,0.25);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
    }

    .retry-badge {
        background: rgba(251,191,36,0.1);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.25);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
        margin-left: 8px;
    }

    .table-pill {
        display: inline-block;
        background: rgba(34,211,238,0.08);
        border: 1px solid rgba(34,211,238,0.2);
        color: #22d3ee;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        margin: 3px;
    }

    .history-item {
        background: #0d1117;
        border: 1px solid #1e2a3a;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 6px;
        cursor: pointer;
        font-size: 0.82rem;
        color: #94a3b8;
    }

    .schema-table {
        background: #060a12;
        border: 1px solid #1e2a3a;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        font-size: 0.78rem;
    }

    .schema-table-name {
        color: #22d3ee;
        font-weight: 700;
        font-family: monospace;
        margin-bottom: 4px;
    }

    .schema-cols {
        color: #475569;
        font-family: monospace;
        line-height: 1.7;
    }

    .error-box {
        background: rgba(239,68,68,0.06);
        border: 1px solid rgba(239,68,68,0.2);
        border-radius: 10px;
        padding: 14px 18px;
        font-size: 0.85rem;
        color: #f87171;
        line-height: 1.7;
    }

    .suggested-q {
        background: #0d1117;
        border: 1px solid #1e2a3a;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 0.8rem;
        color: #64748b;
        cursor: pointer;
        margin-bottom: 4px;
        transition: border-color 0.2s;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ──
if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = None
if "prefill" not in st.session_state:
    st.session_state.prefill = ""

# ── Header ──
st.markdown(
    '<div class="main-title">'
    '🔍 QueryMind AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">'
    'Ask a question in plain English → '
    'get SQL + results + explanation instantly. '
    'Self-correcting agent powered by '
    'Gemini 2.0 Flash + SQLite.'
    '</div>',
    unsafe_allow_html=True
)

st.info(
    "📊 **NL2SQL Research, 2025** — "
    "Data analysts spend 60–80% of their time "
    "writing and debugging SQL. "
    "Frontier LLMs now reach 70–85% accuracy "
    "on clean databases. "
    "**QueryMind adds self-correction to "
    "push accuracy higher.**"
)

st.divider()

# ── Two column layout ──
main_col, side_col = st.columns([3, 1])

with main_col:
    st.markdown("### 💬 Ask Your Database")

    question = st.text_input(
        label="question",
        label_visibility="collapsed",
        value=st.session_state.prefill,
        placeholder=(
            "What are the top 5 products "
            "by revenue?"
        )
    )

    # Suggested questions
    st.markdown("**Try these:**")
    sq_cols = st.columns(2)
    for i, sq in enumerate(
        SUGGESTED_QUESTIONS[:6]
    ):
        with sq_cols[i % 2]:
            if st.button(
                f"→ {sq}",
                key=f"sq_{i}",
                use_container_width=True
            ):
                st.session_state.prefill = sq
                st.rerun()

    st.markdown(
        "<br>", unsafe_allow_html=True
    )

    submit = st.button(
        "🚀 Run Query",
        use_container_width=True,
        type="primary",
        disabled=not question.strip()
    )

    if submit and question.strip():
        with st.spinner(
            "🤖 Generating SQL..."
        ):
            try:
                result = run_query(
                    question, SCHEMA
                )
                st.session_state.result = result
                # Add to history
                st.session_state.history.insert(
                    0, {
                        "question": question,
                        "rows":     result.row_count,
                        "error":    result.error
                    }
                )
                st.session_state.prefill = ""
                st.rerun()
            except ValueError as e:
                st.warning(f"⚠️ {e}")
            except Exception as e:
                st.error(f"❌ {e}")

    # ── Display result ──
    if st.session_state.result:
        result = st.session_state.result

        st.divider()

        # ── Meta row ──
        m1, m2, m3, m4 = st.columns(4)
        for col, val, color, label in [
            (m1, result.row_count,
             "#22d3ee", "Rows Returned"),
            (m2, len(result.columns),
             "#818cf8", "Columns"),
            (m3, result.retry_count,
             "#fbbf24", "Corrections Made"),
            (m4, result.confidence,
             "#34d399", "Confidence")
        ]:
            with col:
                st.markdown(
                    f'<div class="stat-box">'
                    f'<div class="stat-num" '
                    f'style="color:{color}">'
                    f'{val}</div>'
                    f'<div class="stat-label">'
                    f'{label}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown(
            "<br>", unsafe_allow_html=True
        )

        # ── SQL display ──
        conf_cls = (
            f"confidence-{result.confidence}"
        )
        retry_badge = (
            f'<span class="retry-badge">'
            f'🔧 Self-corrected '
            f'{result.retry_count}x</span>'
        ) if result.retried else ""

        st.markdown(
            f'<div style="display:flex;'
            f'align-items:center;'
            f'gap:10px;margin-bottom:10px">'
            f'<span style="font-size:0.7rem;'
            f'font-weight:700;'
            f'text-transform:uppercase;'
            f'letter-spacing:2px;'
            f'color:#22d3ee">Generated SQL</span>'
            f'<span class="{conf_cls}">'
            f'{result.confidence}</span>'
            f'{retry_badge}'
            f'</div>',
            unsafe_allow_html=True
        )

        # SQL code block
        st.code(
            result.sql,
            language="sql"
        )

        # SQL explanation
        st.markdown(
            f'<div class="explain-box">'
            f'💡 {result.sql_explanation}'
            f'</div>',
            unsafe_allow_html=True
        )

        # Tables used pills
        if result.tables_used:
            pills = " ".join([
                f'<span class="table-pill">'
                f'📋 {t}</span>'
                for t in result.tables_used
            ])
            st.markdown(
                f'<div style="margin-bottom:16px">'
                f'{pills}</div>',
                unsafe_allow_html=True
            )

        # ── Error display ──
        if result.error:
            st.markdown(
                f'<div class="error-box">'
                f'❌ Query failed after '
                f'{result.retry_count} '
                f'correction attempt(s).<br>'
                f'Error: {result.error}<br><br>'
                f'Try rephrasing your question.'
                f'</div>',
                unsafe_allow_html=True
            )

        # ── Results table ──
        elif result.rows:
            st.markdown(
                '<div style="font-size:0.7rem;'
                'font-weight:700;'
                'text-transform:uppercase;'
                'letter-spacing:2px;'
                'color:#22d3ee;'
                'margin-bottom:10px">'
                '📊 Results'
                '</div>',
                unsafe_allow_html=True
            )

            # Result explanation
            st.markdown(
                f'<div class="result-explain-box">'
                f'🧠 {result.result_explanation}'
                f'</div>',
                unsafe_allow_html=True
            )

            # DataFrame table
            df = pd.DataFrame(
                result.rows,
                columns=result.columns
            )
            st.dataframe(
                df,
                use_container_width=True,
                height=min(
                    400,
                    (len(df) + 1) * 35 + 40
                )
            )

            # Download
            st.download_button(
                label="⬇️ Download CSV",
                data=df.to_csv(index=False),
                file_name="querymind_result.csv",
                mime="text/csv",
                use_container_width=True
            )

        else:
            st.info(
                "ℹ️ Query executed successfully "
                "but returned no results. "
                "Try adjusting your filters."
            )

with side_col:
    # ── Schema browser ──
    st.markdown("### 🗄️ Database Schema")
    st.markdown(
        f"**Demo:** E-Commerce DB"
    )

    schema_data = {
        "customers":      [
            "id", "name", "email",
            "city", "country",
            "plan", "joined_date", "ltv"
        ],
        "products":       [
            "id", "name", "category",
            "price", "cost",
            "stock", "rating"
        ],
        "orders":         [
            "id", "customer_id",
            "order_date", "status",
            "total_amount", "shipping_city"
        ],
        "order_items":    [
            "id", "order_id",
            "product_id", "quantity",
            "unit_price"
        ],
        "reviews":        [
            "id", "product_id",
            "customer_id", "rating",
            "review_date", "sentiment"
        ],
        "support_tickets": [
            "id", "customer_id",
            "created_at", "category",
            "status", "priority",
            "resolved_at"
        ]
    }

    for table, cols in schema_data.items():
        st.markdown(
            f'<div class="schema-table">'
            f'<div class="schema-table-name">'
            f'📋 {table}</div>'
            f'<div class="schema-cols">'
            f'{chr(10).join(cols)}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.divider()

    # ── Query history ──
    if st.session_state.history:
        st.markdown("### 📜 Query History")

        for i, item in enumerate(
            st.session_state.history[:8]
        ):
            status = (
                "✅" if not item["error"]
                else "❌"
            )
            if st.button(
                f"{status} {item['question'][:40]}",
                key=f"hist_{i}",
                use_container_width=True
            ):
                st.session_state.prefill = \
                    item["question"]
                st.rerun()

        if st.button(
            "🗑️ Clear History",
            use_container_width=True
        ):
            st.session_state.history = []
            st.session_state.result  = None
            st.rerun()

    st.divider()

    st.caption(
        "🔍 QueryMind AI — "
        "NL→SQL with self-correction · "
        "Powered by Gemini 2.0 Flash · "
        "Day 13 of 14"
    )