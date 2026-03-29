import streamlit as st
from app import generate_competitive_brief

# ── Page config ──
st.set_page_config(
    page_title="CompeteAI",
    page_icon="🎯",
    layout="wide"
)

# ── Custom CSS ──
st.markdown("""
<style>
    .stApp { background-color: #070b12; }

    .main-title {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #f59e0b, #ef4444);
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

    .company-card {
        background: #0d1117;
        border: 1px solid #1e2a3a;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 14px;
        position: relative;
    }

    .your-company-card {
        border-color: rgba(245,158,11,0.3);
        background: rgba(245,158,11,0.04);
    }

    .company-name {
        font-size: 1.1rem;
        font-weight: 800;
        color: #e2e8f0;
        margin-bottom: 6px;
    }

    .company-position {
        font-size: 0.85rem;
        color: #94a3b8;
        line-height: 1.6;
        margin-bottom: 12px;
    }

    .threat-HIGH {
        background: rgba(239,68,68,0.1);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.25);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        display: inline-block;
    }

    .threat-MEDIUM {
        background: rgba(251,191,36,0.1);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.25);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        display: inline-block;
    }

    .threat-LOW {
        background: rgba(52,211,153,0.1);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.25);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        display: inline-block;
    }

    .momentum-Growing {
        color: #34d399;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .momentum-Stable {
        color: #fbbf24;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .momentum-Declining {
        color: #f87171;
        font-size: 0.78rem;
        font-weight: 600;
    }

    .signal-card {
        background: #0d1117;
        border: 1px solid #1e2a3a;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 10px;
    }

    .signal-HIGH { border-left: 3px solid #ef4444; }
    .signal-MEDIUM { border-left: 3px solid #fbbf24; }
    .signal-LOW { border-left: 3px solid #34d399; }

    .signal-text {
        font-size: 0.88rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 4px;
    }

    .signal-impl {
        font-size: 0.8rem;
        color: #64748b;
        line-height: 1.6;
    }

    .action-card {
        background: #0d1117;
        border: 1px solid #1e2a3a;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 10px;
    }

    .action-text {
        font-size: 0.88rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 4px;
    }

    .action-reason {
        font-size: 0.8rem;
        color: #64748b;
        line-height: 1.6;
        margin-bottom: 6px;
    }

    .timeframe-immediately {
        background: rgba(239,68,68,0.1);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.2);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
    }

    .timeframe-this-month {
        background: rgba(251,191,36,0.1);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.2);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
    }

    .timeframe-this-quarter {
        background: rgba(52,211,153,0.1);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.2);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
    }

    .summary-box {
        background: rgba(245,158,11,0.05);
        border: 1px solid rgba(245,158,11,0.15);
        border-left: 3px solid #f59e0b;
        border-radius: 0 10px 10px 0;
        padding: 16px 20px;
        font-size: 0.9rem;
        color: #cbd5e1;
        line-height: 1.8;
        margin-bottom: 20px;
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
        color: #f59e0b;
    }

    .stat-label {
        font-size: 0.65rem;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .trend-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 10px 0;
        border-bottom: 1px solid #1e2a3a;
        font-size: 0.85rem;
        color: #94a3b8;
        line-height: 1.6;
    }

    .trend-item:last-child {
        border-bottom: none;
    }

    .watch-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 8px 0;
        font-size: 0.85rem;
        color: #94a3b8;
        border-bottom: 1px solid #1e2a3a;
    }

    .watch-item:last-child {
        border-bottom: none;
    }

    .section-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 14px;
    }

    .pill-list {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
    }

    .pill-strength {
        background: rgba(52,211,153,0.08);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.2);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
    }

    .pill-weakness {
        background: rgba(248,113,113,0.08);
        color: #f87171;
        border: 1px solid rgba(248,113,113,0.2);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
    }

    .pill-move {
        background: rgba(139,92,246,0.08);
        color: #a78bfa;
        border: 1px solid rgba(139,92,246,0.2);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown(
    '<div class="main-title">🎯 CompeteAI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">'
    'Enter your company + competitors → '
    'an AI agent searches the web in real-time '
    'and generates a structured competitive brief. '
    'Powered by Tavily + Gemini 2.0 Flash.'
    '</div>',
    unsafe_allow_html=True
)

# ── Real world stat ──
st.info(
    "📊 **Crayon Competitive Intelligence Report, 2024**"
    " — 77% of businesses say competitive intelligence "
    "is important, but only 29% do it consistently. "
    "The gap is time and tooling. "
    "**CompeteAI closes that gap in 90 seconds.**"
)

st.divider()

# ── Input section ──
st.markdown("### 01 — Enter Companies")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**🏢 Your Company**")
    your_company = st.text_input(
        label="your_company",
        label_visibility="collapsed",
        placeholder="e.g. Notion"
    )

with col2:
    st.markdown("**🎯 Competitors (max 3)**")
    comp1 = st.text_input(
        label="comp1",
        label_visibility="collapsed",
        placeholder="Competitor 1 e.g. Obsidian"
    )
    comp2 = st.text_input(
        label="comp2",
        label_visibility="collapsed",
        placeholder="Competitor 2 (optional)"
    )
    comp3 = st.text_input(
        label="comp3",
        label_visibility="collapsed",
        placeholder="Competitor 3 (optional)"
    )

# Build competitors list
competitors = [
    c for c in [comp1, comp2, comp3]
    if c.strip()
]

st.divider()

# ── Run button ──
can_run = bool(your_company.strip() and competitors)

if st.button(
    "🚀 Generate Competitive Brief",
    use_container_width=True,
    type="primary",
    disabled=not can_run
):
    # Progress tracking
    progress_bar = st.progress(0)
    status_text  = st.empty()

    def on_progress(current, total, query, company):
        pct = int((current / total) * 100)
        progress_bar.progress(pct)
        status_text.markdown(
            f"🔍 Searching ({current}/{total}): "
            f"**{company}** — `{query[:50]}...`"
        )

    try:
        with st.spinner(""):
            brief = generate_competitive_brief(
                your_company=your_company,
                competitors=competitors,
                on_progress=on_progress
            )
            st.session_state["brief"] = brief

        progress_bar.progress(100)
        status_text.markdown(
            "✅ Research complete — synthesizing..."
        )

    except ValueError as e:
        st.warning(f"⚠️ {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Failed: {e}")
        st.stop()

# ── Display brief ──
if "brief" in st.session_state:
    brief = st.session_state["brief"]

    st.success("✅ Competitive brief generated!")
    st.divider()

    # ── Stats row ──
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-num">'
            f'{brief.queries_run}</div>'
            f'<div class="stat-label">'
            f'Searches Run</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with s2:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-num">'
            f'{brief.results_analyzed}</div>'
            f'<div class="stat-label">'
            f'Results Analyzed</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with s3:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-num">'
            f'{len(brief.key_signals)}</div>'
            f'<div class="stat-label">'
            f'Key Signals</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with s4:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-num">'
            f'{len(brief.recommended_actions)}</div>'
            f'<div class="stat-label">'
            f'Actions</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.divider()

    # ── Executive summary ──
    st.markdown(
        f'<div class="summary-box">'
        f'📋 <strong>Executive Summary</strong><br><br>'
        f'{brief.executive_summary}'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Main layout ──
    left, right = st.columns([1, 1])

    with left:
        # Company snapshots
        st.markdown(
            '<div class="section-label" '
            'style="color:#f59e0b">'
            '🏢 Company Snapshots'
            '</div>',
            unsafe_allow_html=True
        )

        for snap in brief.company_snapshots:
            card_cls = (
                "company-card your-company-card"
                if snap.is_your_company
                else "company-card"
            )
            you_badge = (
                ' <span style="font-size:0.7rem;'
                'color:#f59e0b">← YOU</span>'
                if snap.is_your_company else ""
            )

            threat_cls = f"threat-{snap.threat_level}"
            momentum_cls = (
                f"momentum-{snap.momentum}"
            )
            momentum_icon = (
                "📈" if snap.momentum == "Growing"
                else "➡️" if snap.momentum == "Stable"
                else "📉"
            )

            moves_html = "".join([
                f'<span class="pill-move">{m}</span>'
                for m in snap.recent_moves[:2]
            ])
            strengths_html = "".join([
                f'<span class="pill-strength">{s}</span>'
                for s in snap.strengths[:2]
            ])
            weaknesses_html = "".join([
                f'<span class="pill-weakness">{w}</span>'
                for w in snap.weaknesses[:2]
            ])

            st.markdown(f"""
            <div class="{card_cls}">
                <div class="company-name">
                    {snap.company_name}{you_badge}
                </div>
                <div class="company-position">
                    {snap.current_position}
                </div>
                <div style="margin-bottom:8px">
                    <span class="{threat_cls}">
                        THREAT: {snap.threat_level}
                    </span>
                    &nbsp;
                    <span class="{momentum_cls}">
                        {momentum_icon} {snap.momentum}
                    </span>
                </div>
                <div style="font-size:0.7rem;
                     color:#475569;margin-bottom:4px">
                     RECENT MOVES
                </div>
                <div class="pill-list">
                    {moves_html}
                </div>
                <div style="font-size:0.7rem;
                     color:#475569;margin-top:10px;
                     margin-bottom:4px">
                     STRENGTHS
                </div>
                <div class="pill-list">
                    {strengths_html}
                </div>
                <div style="font-size:0.7rem;
                     color:#475569;margin-top:10px;
                     margin-bottom:4px">
                     WEAKNESSES
                </div>
                <div class="pill-list">
                    {weaknesses_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Market trends
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="section-label" '
            'style="color:#818cf8">'
            '📊 Market Trends'
            '</div>',
            unsafe_allow_html=True
        )
        trends_html = "".join([
            f'<div class="trend-item">'
            f'<span style="color:#818cf8">→</span>'
            f'{t}</div>'
            for t in brief.market_trends
        ])
        st.markdown(
            f'<div style="background:#0d1117;'
            f'border:1px solid #1e2a3a;'
            f'border-radius:10px;padding:16px">'
            f'{trends_html}</div>',
            unsafe_allow_html=True
        )

    with right:
        # Key signals
        st.markdown(
            '<div class="section-label" '
            'style="color:#ef4444">'
            '⚡ Key Signals'
            '</div>',
            unsafe_allow_html=True
        )

        for sig in brief.key_signals:
            urgency_colors = {
                "HIGH":   "#ef4444",
                "MEDIUM": "#fbbf24",
                "LOW":    "#34d399"
            }
            color = urgency_colors.get(
                sig.urgency, "#94a3b8"
            )
            st.markdown(f"""
            <div class="signal-card
                 signal-{sig.urgency}">
                <div style="display:flex;
                     justify-content:space-between;
                     margin-bottom:6px">
                    <span style="font-size:0.7rem;
                         color:{color};
                         font-weight:700">
                        {sig.urgency} URGENCY
                    </span>
                    <span style="font-size:0.7rem;
                         color:#475569">
                        {sig.company}
                    </span>
                </div>
                <div class="signal-text">
                    {sig.signal}
                </div>
                <div class="signal-impl">
                    → {sig.implication}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Recommended actions
        st.markdown(
            "<br>"
            '<div class="section-label" '
            'style="color:#34d399">'
            '🎯 Recommended Actions'
            '</div>',
            unsafe_allow_html=True
        )

        for act in brief.recommended_actions:
            tf_key = act.timeframe.replace(" ", "-")
            tf_cls = f"timeframe-{tf_key}"
            st.markdown(f"""
            <div class="action-card">
                <div class="action-text">
                    → {act.action}
                </div>
                <div class="action-reason">
                    {act.reason}
                </div>
                <span class="{tf_cls}">
                    ⏰ {act.timeframe}
                </span>
            </div>
            """, unsafe_allow_html=True)

        # Watch list
        st.markdown(
            "<br>"
            '<div class="section-label" '
            'style="color:#fbbf24">'
            '👁️ Watch List'
            '</div>',
            unsafe_allow_html=True
        )
        watch_html = "".join([
            f'<div class="watch-item">'
            f'<span style="color:#fbbf24">◉</span>'
            f'{w}</div>'
            for w in brief.watch_list
        ])
        st.markdown(
            f'<div style="background:#0d1117;'
            f'border:1px solid #1e2a3a;'
            f'border-radius:10px;padding:16px">'
            f'{watch_html}</div>',
            unsafe_allow_html=True
        )

    st.divider()

    # ── Data freshness footer ──
    st.caption(
        f"📅 Data freshness: {brief.data_freshness} · "
        f"Powered by Tavily Search + "
        f"Gemini 2.0 Flash · "
        f"CompeteAI — Day 6 of 14"
    )