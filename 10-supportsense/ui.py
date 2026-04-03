import streamlit as st
from app import handle_support_query, PRODUCT_NAME

# ── Page config ──
st.set_page_config(
    page_title=f"SupportSense — {PRODUCT_NAME}",
    page_icon="🎧",
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
            90deg, #06b6d4, #6366f1
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

    .answer-card {
        background: rgba(6,182,212,0.05);
        border: 2px solid rgba(6,182,212,0.3);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 16px;
    }

    .escalation-card {
        background: rgba(239,68,68,0.05);
        border: 2px solid rgba(239,68,68,0.3);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 16px;
    }

    .answer-text {
        font-size: 0.95rem;
        color: #e2e8f0;
        line-height: 1.85;
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

    .priority-URGENT {
        background: rgba(239,68,68,0.15);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        display: inline-block;
    }

    .priority-HIGH {
        background: rgba(249,115,22,0.12);
        color: #fb923c;
        border: 1px solid rgba(249,115,22,0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        display: inline-block;
    }

    .priority-MEDIUM {
        background: rgba(251,191,36,0.1);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.25);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        display: inline-block;
    }

    .priority-LOW {
        background: rgba(100,116,139,0.1);
        color: #94a3b8;
        border: 1px solid rgba(100,116,139,0.2);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        display: inline-block;
    }

    .source-pill {
        display: inline-block;
        background: rgba(6,182,212,0.08);
        border: 1px solid rgba(6,182,212,0.2);
        color: #06b6d4;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        margin: 3px;
    }

    .ticket-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 10px 0;
        border-bottom: 1px solid #1e2a3a;
        font-size: 0.85rem;
    }

    .ticket-row:last-child {
        border-bottom: none;
    }

    .ticket-label {
        color: #475569;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        min-width: 160px;
    }

    .ticket-value {
        color: #e2e8f0;
        text-align: right;
        flex: 1;
    }

    .chat-bubble-user {
        background: rgba(99,102,241,0.1);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 12px 12px 4px 12px;
        padding: 12px 16px;
        font-size: 0.88rem;
        color: #c7d2fe;
        margin-bottom: 8px;
        max-width: 80%;
        margin-left: auto;
    }

    .chat-bubble-ai {
        background: #0d1520;
        border: 1px solid #1e2a3a;
        border-radius: 4px 12px 12px 12px;
        padding: 12px 16px;
        font-size: 0.88rem;
        color: #94a3b8;
        margin-bottom: 8px;
        max-width: 80%;
    }

    .intent-badge {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 4px;
        display: inline-block;
    }

    .stat-box {
        background: #0d1520;
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

    .followup-btn {
        background: #0d1520;
        border: 1px solid #1e2a3a;
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 0.8rem;
        color: #64748b;
        cursor: pointer;
        margin: 4px;
        display: inline-block;
    }

    .doc-preview {
        background: #060a12;
        border: 1px solid #1e2a3a;
        border-radius: 8px;
        padding: 12px;
        font-size: 0.78rem;
        color: #475569;
        line-height: 1.7;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ──
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "stats" not in st.session_state:
    st.session_state.stats = {
        "total":     0,
        "answered":  0,
        "escalated": 0
    }
if "prefill" not in st.session_state:
    st.session_state.prefill = ""

# ── Header ──
st.markdown(
    '<div class="main-title">🎧 SupportSense AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    f'<div class="subtitle">'
    f'AI-powered support for {PRODUCT_NAME} — '
    f'answers from KB instantly, '
    f'escalates when humans are needed.'
    f'</div>',
    unsafe_allow_html=True
)

st.info(
    "📊 **Gartner, 2026** — "
    "98% of customer service leaders say "
    "smooth AI-to-human transitions are essential. "
    "90% admit they struggle with handoffs. "
    "**SupportSense solves the escalation problem.**"
)

st.divider()

# ── Two column layout ──
left_col, right_col = st.columns([2, 1])

with left_col:
    st.markdown("### 💬 Ask a Support Question")

    # Query input
    query = st.text_area(
        label="query",
        label_visibility="collapsed",
        height=100,
        value=st.session_state.prefill,
        placeholder=(
            "How do I upgrade to Pro?\n"
            "Does FlowDesk integrate with Slack?\n"
            "I was charged twice this month..."
        )
    )

    # Quick question buttons
    st.markdown("**Try these:**")
    q_cols = st.columns(3)
    quick_qs = [
        "How much is the Pro plan?",
        "Does it work with Slack?",
        "How do I add team members?",
        "I want a refund",
        "What storage do I get?",
        "HIPAA compliance?"
    ]
    for i, qq in enumerate(quick_qs):
        with q_cols[i % 3]:
            if st.button(
                qq,
                key=f"qq_{i}",
                use_container_width=True
            ):
                st.session_state.prefill = qq
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    submit = st.button(
        "🚀 Submit",
        use_container_width=True,
        type="primary",
        disabled=not query.strip()
    )

    if submit and query.strip():
        with st.spinner(
            "Searching knowledge base..."
        ):
            try:
                response = handle_support_query(
                    query
                )
                st.session_state.chat_history\
                    .insert(0, {
                        "query":    query,
                        "response": response
                    })

                # Update stats
                st.session_state.stats["total"] += 1
                if response.response_type == "answer":
                    st.session_state\
                        .stats["answered"] += 1
                else:
                    st.session_state\
                        .stats["escalated"] += 1

                st.session_state.prefill = ""
                st.rerun()

            except ValueError as e:
                st.warning(f"⚠️ {e}")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    # ── Chat history ──
    if st.session_state.chat_history:
        st.divider()
        for item in st.session_state.chat_history:
            q    = item["query"]
            resp = item["response"]

            # User bubble
            st.markdown(
                f'<div class="chat-bubble-user">'
                f'👤 {q}'
                f'</div>',
                unsafe_allow_html=True
            )

            # AI response
            if resp.response_type == "answer" \
               and resp.answer:
                ans = resp.answer

                conf_cls = (
                    f"confidence-{ans.confidence}"
                )

                st.markdown(
                    f'<div class="answer-card">',
                    unsafe_allow_html=True
                )

                # Answer header
                a_col1, a_col2 = st.columns([3,1])
                with a_col1:
                    st.markdown(
                        "✅ **Answered from KB**"
                    )
                with a_col2:
                    st.markdown(
                        f'<span class="{conf_cls}">'
                        f'{ans.confidence} CONFIDENCE'
                        f'</span>',
                        unsafe_allow_html=True
                    )

                # Answer text
                st.markdown(
                    f'<div class="answer-text">'
                    f'{ans.answer}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Sources
                if ans.source_sections:
                    st.markdown(
                        "<br>**📚 Sources:**",
                        unsafe_allow_html=True
                    )
                    pills = " ".join([
                        f'<span class="source-pill">'
                        f'📄 {s}</span>'
                        for s in ans.source_sections
                    ])
                    st.markdown(
                        f'<div>{pills}</div>',
                        unsafe_allow_html=True
                    )

                # Follow-ups
                if ans.follow_up_suggestions:
                    st.markdown(
                        "<br>**💡 You might also ask:**"
                    )
                    for fq in \
                            ans.follow_up_suggestions:
                        if st.button(
                            f"→ {fq}",
                            key=f"fq_{q[:10]}_{fq[:15]}"
                        ):
                            st.session_state\
                                .prefill = fq
                            st.rerun()

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

            elif resp.response_type == \
                    "escalation" and \
                    resp.escalation:
                esc = resp.escalation
                pri = esc.priority
                pri_cls = f"priority-{pri}"

                st.markdown(
                    '<div class="escalation-card">',
                    unsafe_allow_html=True
                )

                e_col1, e_col2 = st.columns([3,1])
                with e_col1:
                    st.markdown(
                        "🔺 **Escalating to Human Team**"
                    )
                with e_col2:
                    st.markdown(
                        f'<span class="{pri_cls}">'
                        f'{pri} PRIORITY'
                        f'</span>',
                        unsafe_allow_html=True
                    )

                st.markdown(
                    f'<p style="color:#94a3b8;'
                    f'font-size:0.85rem;margin:8px 0">'
                    f'{esc.ticket_summary}</p>',
                    unsafe_allow_html=True
                )

                t1, t2 = st.columns(2)

                with t1:
                    st.markdown(
                        f'<div class="ticket-row">'
                        f'<span class="ticket-label">'
                        f'Department</span>'
                        f'<span class="ticket-value">'
                        f'{esc.department}</span>'
                        f'</div>'
                        f'<div class="ticket-row">'
                        f'<span class="ticket-label">'
                        f'Issue Type</span>'
                        f'<span class="ticket-value">'
                        f'{esc.issue_type}</span>'
                        f'</div>'
                        f'<div class="ticket-row">'
                        f'<span class="ticket-label">'
                        f'Sentiment</span>'
                        f'<span class="ticket-value">'
                        f'{esc.customer_sentiment}'
                        f'</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                with t2:
                    st.markdown(
                        f'<div class="ticket-row">'
                        f'<span class="ticket-label">'
                        f'Est. Resolution</span>'
                        f'<span class="ticket-value">'
                        f'{esc.estimated_resolution_time}'
                        f'</span>'
                        f'</div>'
                        f'<div class="ticket-row">'
                        f'<span class="ticket-label">'
                        f'Suggested Action</span>'
                        f'<span class="ticket-value">'
                        f'{esc.suggested_resolution[:60]}'
                        f'...</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                st.markdown(
                    f'<p style="color:#64748b;'
                    f'font-size:0.82rem;'
                    f'margin-top:10px">'
                    f'⏳ A human agent will follow up. '
                    f'Expected: '
                    f'{esc.estimated_resolution_time}'
                    f'</p>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

            st.markdown(
                "<br>", unsafe_allow_html=True
            )

with right_col:
    st.markdown("### 📊 Session Stats")

    stats = st.session_state.stats
    total = stats["total"] or 1

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-num" '
            f'style="color:#06b6d4">'
            f'{stats["total"]}</div>'
            f'<div class="stat-label">Total</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with s2:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-num" '
            f'style="color:#34d399">'
            f'{stats["answered"]}</div>'
            f'<div class="stat-label">Answered</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with s3:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-num" '
            f'style="color:#f87171">'
            f'{stats["escalated"]}</div>'
            f'<div class="stat-label">Escalated</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Auto-resolution rate
    rate = int(
        (stats["answered"] / total) * 100
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="stat-box">'
        f'<div style="font-size:0.72rem;'
        f'color:#475569;text-transform:uppercase;'
        f'letter-spacing:1px;margin-bottom:6px">'
        f'Auto-Resolution Rate</div>'
        f'<div style="background:#1e2a3a;'
        f'border-radius:8px;height:12px;'
        f'overflow:hidden">'
        f'<div style="width:{rate}%;height:100%;'
        f'background:#34d399;'
        f'border-radius:8px"></div>'
        f'</div>'
        f'<div style="font-size:0.85rem;'
        f'color:#34d399;margin-top:6px;'
        f'font-weight:700">{rate}%</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # KB coverage
    st.markdown("### 📚 KB Coverage")
    kb_topics = [
        ("💰", "Pricing Plans"),
        ("⚡", "Core Features"),
        ("🔗", "Integrations"),
        ("💳", "Billing"),
        ("👥", "Team Management"),
        ("🔧", "Technical Limits"),
        ("🎧", "Support Channels"),
        ("🔒", "Security"),
        ("🚀", "Getting Started"),
        ("🛠️", "Troubleshooting"),
    ]
    for icon, topic in kb_topics:
        st.markdown(
            f'<div style="font-size:0.78rem;'
            f'color:#475569;padding:4px 0;'
            f'border-bottom:1px solid #1e2a3a">'
            f'{icon} {topic}</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Clear history
    if st.button(
        "🗑️ Clear History",
        use_container_width=True
    ):
        st.session_state.chat_history = []
        st.session_state.stats = {
            "total": 0,
            "answered": 0,
            "escalated": 0
        }
        st.rerun()