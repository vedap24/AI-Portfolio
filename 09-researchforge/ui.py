import streamlit as st
from app import (
    run_research_pipeline,
    format_report_as_markdown
)
from prompts import format_report_as_markdown

# ── Page config ──
st.set_page_config(
    page_title="ResearchForge AI",
    page_icon="🔬",
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
            90deg, #818cf8, #34d399
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

    .agent-card {
        background: #0d1117;
        border: 1px solid #1e2a3a;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .agent-idle {
        border-left: 3px solid #334155;
    }

    .agent-active {
        border-left: 3px solid #818cf8;
        background: rgba(129,140,248,0.05);
    }

    .agent-done {
        border-left: 3px solid #34d399;
        background: rgba(52,211,153,0.04);
    }

    .agent-name {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .agent-status {
        font-size: 0.8rem;
        color: #64748b;
    }

    .finding-card {
        background: #0d1117;
        border: 1px solid #1e2a3a;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .finding-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 8px;
    }

    .finding-detail {
        font-size: 0.85rem;
        color: #94a3b8;
        line-height: 1.75;
    }

    .confidence-HIGH {
        background: rgba(52,211,153,0.1);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.25);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.68rem;
        font-weight: 700;
        display: inline-block;
        margin-left: 8px;
    }

    .confidence-MEDIUM {
        background: rgba(251,191,36,0.1);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.25);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.68rem;
        font-weight: 700;
        display: inline-block;
        margin-left: 8px;
    }

    .confidence-LOW {
        background: rgba(248,113,113,0.1);
        color: #f87171;
        border: 1px solid rgba(248,113,113,0.25);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.68rem;
        font-weight: 700;
        display: inline-block;
        margin-left: 8px;
    }

    .section-card {
        background: #0d1117;
        border: 1px solid #1e2a3a;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 14px;
    }

    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #818cf8;
        margin-bottom: 12px;
    }

    .section-content {
        font-size: 0.88rem;
        color: #94a3b8;
        line-height: 1.85;
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

    .summary-box {
        background: rgba(129,140,248,0.05);
        border: 1px solid rgba(129,140,248,0.15);
        border-left: 3px solid #818cf8;
        border-radius: 0 10px 10px 0;
        padding: 18px 20px;
        font-size: 0.92rem;
        color: #cbd5e1;
        line-height: 1.85;
        margin-bottom: 20px;
    }

    .subq-item {
        background: #0d1117;
        border: 1px solid #1e2a3a;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }

    .subq-question {
        font-size: 0.85rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 4px;
    }

    .subq-meta {
        font-size: 0.75rem;
        color: #475569;
    }

    .source-pill {
        display: inline-block;
        background: rgba(52,211,153,0.08);
        border: 1px solid rgba(52,211,153,0.2);
        color: #34d399;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        margin: 3px;
        text-decoration: none;
    }

    .gap-item {
        font-size: 0.82rem;
        color: #fbbf24;
        padding: 5px 0;
        border-bottom: 1px solid #1e2a3a;
    }

    .gap-item:last-child { border-bottom: none; }

    .conclusion-item {
        font-size: 0.85rem;
        color: #94a3b8;
        padding: 6px 0;
        border-bottom: 1px solid #1e2a3a;
        line-height: 1.6;
    }

    .conclusion-item:last-child {
        border-bottom: none;
    }

    .log-entry {
        font-family: monospace;
        font-size: 0.75rem;
        color: #475569;
        padding: 3px 0;
        border-bottom: 1px solid #111827;
    }

    .log-PLANNER { color: #818cf8; }
    .log-RESEARCHER { color: #34d399; }
    .log-FACT_CHECKER { color: #fbbf24; }
    .log-WRITER { color: #60a5fa; }

    .quality-HIGH { color: #34d399; }
    .quality-MEDIUM { color: #fbbf24; }
    .quality-LOW { color: #f87171; }

    .followup-item {
        font-size: 0.82rem;
        color: #64748b;
        padding: 6px 0;
        border-bottom: 1px solid #1e2a3a;
        cursor: pointer;
        transition: color 0.2s;
    }

    .followup-item:hover { color: #818cf8; }
    .followup-item:last-child {
        border-bottom: none;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state init ──
if "result" not in st.session_state:
    st.session_state["result"] = None
if "agent_statuses" not in st.session_state:
    st.session_state["agent_statuses"] = {
        "PLANNER":      ("idle", "Waiting..."),
        "RESEARCHER":   ("idle", "Waiting..."),
        "FACT_CHECKER": ("idle", "Waiting..."),
        "WRITER":       ("idle", "Waiting...")
    }

# ── Header ──
st.markdown(
    '<div class="main-title">'
    '🔬 ResearchForge AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">'
    'Enter any research question → '
    '4 specialized AI agents plan, search, '
    'verify, and synthesize a full research brief.'
    '</div>',
    unsafe_allow_html=True
)

st.info(
    "📊 **Asana State of Work Innovation, 2025** — "
    "60% of work time is spent on 'work about work.' "
    "Writing a research brief takes 3–5 hours manually. "
    "**ResearchForge does it in under 4 minutes.**"
)

st.divider()

# ── Input ──
st.markdown("### Your Research Question")

query = st.text_area(
    label="query",
    label_visibility="collapsed",
    height=100,
    placeholder=(
        "What are the key challenges in "
        "deploying LLMs at production scale in 2025?\n\n"
        "Or try: How does RAG improve LLM accuracy? "
        "/ What is the future of AI agents?"
    )
)

run_btn = st.button(
    "🚀 Start Research",
    use_container_width=True,
    type="primary",
    disabled=not query.strip()
)

st.divider()

# ── Agent Status Panel ──
st.markdown("### 🤖 Agent Pipeline")

agent_cols = st.columns(4)
agent_names = [
    "PLANNER", "RESEARCHER",
    "FACT_CHECKER", "WRITER"
]
agent_icons = {
    "PLANNER":      "🧠",
    "RESEARCHER":   "🔍",
    "FACT_CHECKER": "🔎",
    "WRITER":       "✍️"
}
agent_descs = {
    "PLANNER":      "Breaks query into sub-questions",
    "RESEARCHER":   "Searches the web",
    "FACT_CHECKER": "Verifies and filters results",
    "WRITER":       "Synthesizes final report"
}

# Agent status placeholders
agent_placeholders = {}
for i, name in enumerate(agent_names):
    with agent_cols[i]:
        agent_placeholders[name] = st.empty()


def render_agent_card(
    placeholder,
    name: str,
    status: str,
    message: str
):
    icon  = agent_icons[name]
    desc  = agent_descs[name]
    color_map = {
        "idle":   "#334155",
        "active": "#818cf8",
        "done":   "#34d399",
        "error":  "#f87171"
    }
    status_icons = {
        "idle":   "⭕",
        "active": "🔄",
        "done":   "✅",
        "error":  "❌"
    }
    color  = color_map.get(status, "#334155")
    s_icon = status_icons.get(status, "⭕")

    placeholder.markdown(
        f'<div style="background:#0d1117;'
        f'border:1px solid #1e2a3a;'
        f'border-left:3px solid {color};'
        f'border-radius:10px;padding:14px;">'
        f'<div style="font-size:1.4rem;'
        f'margin-bottom:6px">{icon}</div>'
        f'<div style="font-size:0.78rem;'
        f'font-weight:700;color:{color};'
        f'letter-spacing:1px;'
        f'text-transform:uppercase">'
        f'{name.replace("_", " ")}</div>'
        f'<div style="font-size:0.72rem;'
        f'color:#475569;margin-top:2px">'
        f'{desc}</div>'
        f'<div style="font-size:0.78rem;'
        f'color:#64748b;margin-top:8px">'
        f'{s_icon} {message}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


# Render initial idle state
for name in agent_names:
    render_agent_card(
        agent_placeholders[name],
        name, "idle", "Waiting..."
    )

# ── Run pipeline ──
if run_btn and query.strip():

    progress_bar  = st.progress(0)
    status_text   = st.empty()
    search_status = st.empty()

    # Reset agent cards to idle
    for name in agent_names:
        render_agent_card(
            agent_placeholders[name],
            name, "idle", "Waiting..."
        )

    def on_agent_update(agent_name, message):
        # Mark previous agents as done
        idx = agent_names.index(agent_name)
        for prev in agent_names[:idx]:
            render_agent_card(
                agent_placeholders[prev],
                prev, "done", "Complete ✓"
            )
        # Mark current as active
        render_agent_card(
            agent_placeholders[agent_name],
            agent_name, "active", message
        )
        # Update progress bar
        pct = int((idx / len(agent_names)) * 100)
        progress_bar.progress(pct)
        status_text.markdown(
            f"**{agent_name.replace('_',' ')}** "
            f"— {message}"
        )

    def on_search_progress(
        current, total, query_text
    ):
        pct = int(
            (1 / len(agent_names)) * 100 +
            (current / total) *
            (1 / len(agent_names)) * 100
        )
        progress_bar.progress(min(pct, 75))
        search_status.markdown(
            f"🔍 Searching ({current}/{total}): "
            f"`{query_text[:50]}...`"
        )

    try:
        result = run_research_pipeline(
            query,
            on_search_progress=on_search_progress,
            on_agent_update=on_agent_update
        )

        # Mark all agents done
        for name in agent_names:
            render_agent_card(
                agent_placeholders[name],
                name, "done", "Complete ✓"
            )

        progress_bar.progress(100)
        status_text.markdown(
            "✅ Research complete!"
        )
        search_status.empty()

        st.session_state["result"] = result

    except ValueError as e:
        st.warning(f"⚠️ {e}")
        for name in agent_names:
            render_agent_card(
                agent_placeholders[name],
                name, "idle", "Waiting..."
            )
    except Exception as e:
        st.error(f"❌ {e}")
        for name in agent_names:
            render_agent_card(
                agent_placeholders[name],
                name, "error", "Failed"
            )

# ── Display results ──
if st.session_state["result"]:
    result = st.session_state["result"]
    report = result.final_report

    st.divider()
    st.success("✅ Research brief generated!")

    # ── Stats row ──
    s1, s2, s3, s4, s5 = st.columns(5)
    stats = [
        (s1, len(result.sub_questions),
         "#818cf8", "Sub-Questions"),
        (s2, result.search_result_count,
         "#34d399", "Results Searched"),
        (s3, result.fact_count,
         "#fbbf24", "Facts Verified"),
        (s4, len(report.key_findings),
         "#60a5fa", "Key Findings"),
        (s5, f"{report.confidence_score}/10",
         "#34d399", "Confidence"),
    ]
    for col, num, color, label in stats:
        with col:
            st.markdown(
                f'<div class="stat-box">'
                f'<div class="stat-num" '
                f'style="color:{color}">'
                f'{num}</div>'
                f'<div class="stat-label">'
                f'{label}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.divider()

    # ── Executive summary ──
    st.markdown(
        f'<div class="summary-box">'
        f'📋 <strong>Executive Summary</strong>'
        f'<br><br>{report.executive_summary}'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Main content ──
    left, right = st.columns([3, 2])

    with left:
        # Key findings
        st.markdown(
            '<div style="font-size:0.7rem;'
            'font-weight:700;letter-spacing:2px;'
            'text-transform:uppercase;'
            'color:#818cf8;margin-bottom:14px">'
            '🔑 Key Findings'
            '</div>',
            unsafe_allow_html=True
        )

        for i, finding in enumerate(
            report.key_findings, 1
        ):
            conf_cls = (
                f"confidence-{finding.confidence}"
            )
            st.markdown(
                f'<div class="finding-card">'
                f'<div class="finding-title">'
                f'{i}. {finding.finding}'
                f'<span class="{conf_cls}">'
                f'{finding.confidence}'
                f'</span>'
                f'</div>'
                f'<div class="finding-detail">'
                f'{finding.detail}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            "<br>", unsafe_allow_html=True
        )

        # Detailed sections
        if report.section_breakdown:
            st.markdown(
                '<div style="font-size:0.7rem;'
                'font-weight:700;letter-spacing:2px;'
                'text-transform:uppercase;'
                'color:#60a5fa;margin-bottom:14px">'
                '📖 Detailed Analysis'
                '</div>',
                unsafe_allow_html=True
            )

            for section in report.section_breakdown:
                with st.expander(
                    section.section_title,
                    expanded=False
                ):
                    st.markdown(
                        section.content
                    )

    with right:
        # Conclusions
        if report.conclusions:
            st.markdown(
                '<div style="font-size:0.7rem;'
                'font-weight:700;letter-spacing:2px;'
                'text-transform:uppercase;'
                'color:#34d399;margin-bottom:12px">'
                '✅ Conclusions'
                '</div>',
                unsafe_allow_html=True
            )
            conc_html = "".join([
                f'<div class="conclusion-item">'
                f'→ {c}</div>'
                for c in report.conclusions
            ])
            st.markdown(
                f'<div style="background:#0d1117;'
                f'border:1px solid #1e2a3a;'
                f'border-radius:10px;'
                f'padding:16px">'
                f'{conc_html}</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            "<br>", unsafe_allow_html=True
        )

        # Knowledge gaps
        if result.knowledge_gaps:
            st.markdown(
                '<div style="font-size:0.7rem;'
                'font-weight:700;letter-spacing:2px;'
                'text-transform:uppercase;'
                'color:#fbbf24;margin-bottom:12px">'
                '⚠️ Knowledge Gaps'
                '</div>',
                unsafe_allow_html=True
            )
            gaps_html = "".join([
                f'<div class="gap-item">⚡ {g}'
                f'</div>'
                for g in result.knowledge_gaps
            ])
            st.markdown(
                f'<div style="background:#0d1117;'
                f'border:1px solid #1e2a3a;'
                f'border-radius:10px;'
                f'padding:16px">'
                f'{gaps_html}</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            "<br>", unsafe_allow_html=True
        )

        # Follow-up questions
        if report.follow_up_questions:
            st.markdown(
                '<div style="font-size:0.7rem;'
                'font-weight:700;letter-spacing:2px;'
                'text-transform:uppercase;'
                'color:#a78bfa;margin-bottom:12px">'
                '💡 Follow-up Questions'
                '</div>',
                unsafe_allow_html=True
            )
            for fq in report.follow_up_questions:
                if st.button(
                    f"→ {fq}",
                    key=f"fq_{fq[:20]}",
                    use_container_width=True
                ):
                    st.session_state[
                        "prefill_query"
                    ] = fq
                    st.rerun()

        st.markdown(
            "<br>", unsafe_allow_html=True
        )

        # Sub-questions used
        with st.expander(
            "🧠 Research Plan Used"
        ):
            for i, sq in enumerate(
                result.sub_questions, 1
            ):
                st.markdown(
                    f'<div class="subq-item">'
                    f'<div class="subq-question">'
                    f'Q{i}: {sq.question}'
                    f'</div>'
                    f'<div class="subq-meta">'
                    f'Search: `{sq.search_query}` '
                    f'— {sq.purpose}'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        # Agent logs
        with st.expander(
            "📋 Agent Logs"
        ):
            for log in result.agent_logs:
                agent = log.get("agent", "")
                msg   = log.get("message", "")
                color_map = {
                    "PLANNER":      "#818cf8",
                    "RESEARCHER":   "#34d399",
                    "FACT_CHECKER": "#fbbf24",
                    "WRITER":       "#60a5fa"
                }
                color = color_map.get(
                    agent, "#475569"
                )
                st.markdown(
                    f'<div class="log-entry">'
                    f'<span style="color:{color};'
                    f'font-weight:700">'
                    f'[{agent}]</span> {msg}'
                    f'</div>',
                    unsafe_allow_html=True
                )

    st.divider()

    # ── Download report ──
    st.markdown(
        '<div style="font-size:0.7rem;'
        'font-weight:700;letter-spacing:2px;'
        'text-transform:uppercase;'
        'color:#475569;margin-bottom:12px">'
        '📥 Export Report'
        '</div>',
        unsafe_allow_html=True
    )

    md_report = format_report_as_markdown(
        result.final_report.__dict__,
        result.query
    )

    dl_col, copy_col = st.columns(2)

    with dl_col:
        st.download_button(
            label="⬇️ Download as Markdown",
            data=md_report,
            file_name="research_report.md",
            mime="text/markdown",
            use_container_width=True
        )

    with copy_col:
        with st.expander(
            "📋 Copy report markdown"
        ):
            st.code(
                md_report[:2000] + "...",
                language="markdown"
            )

    st.caption(
        f"🔬 ResearchForge AI — "
        f"Source quality: {result.source_quality} · "
        f"Powered by Tavily + Gemini 2.0 Flash · "
        f"Day 9 of 14"
    )