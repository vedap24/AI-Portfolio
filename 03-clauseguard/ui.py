import streamlit as st
import tempfile
import os
from pathlib import Path
from app import scan_full_contract

# ── Page config ──
st.set_page_config(
    page_title="ClauseGuard AI",
    page_icon="⚖️",
    layout="wide"
)

# ── Custom CSS ──
st.markdown("""
<style>
    .stApp { background-color: #080810; }

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

    .risk-high {
        background: rgba(239,68,68,0.08);
        border: 1px solid rgba(239,68,68,0.3);
        border-left: 4px solid #ef4444;
        border-radius: 0 10px 10px 0;
        padding: 18px 20px;
        margin-bottom: 12px;
    }

    .risk-medium {
        background: rgba(251,191,36,0.06);
        border: 1px solid rgba(251,191,36,0.25);
        border-left: 4px solid #fbbf24;
        border-radius: 0 10px 10px 0;
        padding: 18px 20px;
        margin-bottom: 12px;
    }

    .risk-low {
        background: rgba(52,211,153,0.05);
        border: 1px solid rgba(52,211,153,0.2);
        border-left: 4px solid #34d399;
        border-radius: 0 10px 10px 0;
        padding: 18px 20px;
        margin-bottom: 12px;
    }

    .risk-none {
        background: rgba(100,116,139,0.05);
        border: 1px solid rgba(100,116,139,0.15);
        border-left: 4px solid #475569;
        border-radius: 0 10px 10px 0;
        padding: 18px 20px;
        margin-bottom: 12px;
    }

    .risk-badge-HIGH {
        background: rgba(239,68,68,0.15);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.3);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
        display: inline-block;
    }

    .risk-badge-MEDIUM {
        background: rgba(251,191,36,0.12);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.3);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
        display: inline-block;
    }

    .risk-badge-LOW {
        background: rgba(52,211,153,0.1);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.25);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
        display: inline-block;
    }

    .risk-badge-NONE {
        background: rgba(100,116,139,0.1);
        color: #94a3b8;
        border: 1px solid rgba(100,116,139,0.2);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
        display: inline-block;
    }

    .category-pill {
        background: rgba(139,92,246,0.1);
        color: #a78bfa;
        border: 1px solid rgba(139,92,246,0.2);
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        display: inline-block;
        margin-left: 8px;
    }

    .clause-text {
        font-size: 0.8rem;
        color: #475569;
        font-style: italic;
        line-height: 1.6;
        margin: 8px 0;
        padding: 8px 12px;
        background: rgba(0,0,0,0.2);
        border-radius: 6px;
    }

    .info-row {
        display: flex;
        gap: 8px;
        margin-top: 10px;
        flex-wrap: wrap;
    }

    .info-chip {
        font-size: 0.75rem;
        color: #94a3b8;
        background: rgba(15,15,25,0.8);
        border: 1px solid #1e1e2e;
        padding: 4px 10px;
        border-radius: 6px;
    }

    .info-chip strong { color: #e2e8f0; }

    .stat-box {
        background: #0f0f1a;
        border: 1px solid #1e1e2e;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
    }

    .stat-num {
        font-size: 2.2rem;
        font-weight: 900;
        line-height: 1;
    }

    .stat-label {
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }

    .section-card {
        background: #0f0f1a;
        border: 1px solid #1e1e2e;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 14px;
    }

    .section-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 12px;
    }

    .negotiation-box {
        background: rgba(245,158,11,0.06);
        border: 1px solid rgba(245,158,11,0.2);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.82rem;
        color: #fcd34d;
        line-height: 1.6;
        margin-top: 8px;
    }

    .plain-english-box {
        background: rgba(99,102,241,0.05);
        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.82rem;
        color: #a5b4fc;
        line-height: 1.6;
        margin-top: 8px;
    }

    .filter-active {
        background: rgba(239,68,68,0.15) !important;
        border-color: rgba(239,68,68,0.4) !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ──
st.markdown(
    '<div class="main-title">⚖️ ClauseGuard AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Upload any contract PDF → '
    'get an instant AI risk dashboard. '
    'Know what you\'re signing before you sign it.</div>',
    unsafe_allow_html=True
)

# ── Real world stat ──
st.info(
    "📊 **DocuSign State of the Agreement Report, 2023** — "
    "businesses lose $2 trillion annually to poor contract management. "
    "62% of companies have signed contracts they later regretted. "
    "**ClauseGuard gives you the legal intelligence you can't afford to skip.**"
)

st.divider()

# ── File uploader ──
st.markdown("**📁 Upload Contract PDF**")
pdf_file = st.file_uploader(
    label="contract",
    label_visibility="collapsed",
    type=["pdf"],
    help="Supports text-based PDFs. Max 50MB."
)

if pdf_file:
    st.caption(
        f"📄 {pdf_file.name} · "
        f"{pdf_file.size / 1024:.0f}KB"
    )

st.divider()

# ── Scan button ──
if st.button(
    "🔍 Scan Contract for Risk",
    use_container_width=True,
    type="primary",
    disabled=not pdf_file
):
    with st.spinner(
        "Parsing PDF → Chunking → Embedding → "
        "Scanning clauses with Gemini..."
    ):
        try:
            # Save to temp file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".pdf"
            ) as tmp:
                tmp.write(pdf_file.read())
                tmp_path = tmp.name

            report = scan_full_contract(tmp_path)
            os.unlink(tmp_path)
            st.session_state["report"] = report

        except Exception as e:
            st.error(f"❌ Scan failed: {e}")
            st.stop()

# ── Display report ──
if "report" in st.session_state:
    report = st.session_state["report"]

    st.success("✅ Contract scan complete!")
    st.divider()

    # ── Stats row ──
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(f"""<div class="stat-box">
            <div class="stat-num" style="color:#94a3b8">
                {report.total_clauses_scanned}
            </div>
            <div class="stat-label">Clauses Scanned</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""<div class="stat-box">
            <div class="stat-num" style="color:#f87171">
                {report.high_risk_count}
            </div>
            <div class="stat-label">High Risk</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""<div class="stat-box">
            <div class="stat-num" style="color:#fbbf24">
                {report.medium_risk_count}
            </div>
            <div class="stat-label">Medium Risk</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""<div class="stat-box">
            <div class="stat-num" style="color:#34d399">
                {report.low_risk_count}
            </div>
            <div class="stat-label">Low / Safe</div>
        </div>""", unsafe_allow_html=True)

    with c5:
        overall = report.summary.overall_risk
        color = (
            "#f87171" if overall == "HIGH"
            else "#fbbf24" if overall == "MEDIUM"
            else "#34d399"
        )
        st.markdown(f"""<div class="stat-box">
            <div class="stat-num" style="color:{color};
                 font-size:1.4rem;padding-top:8px">
                {overall}
            </div>
            <div class="stat-label">Overall Risk</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Two column layout ──
    left, right = st.columns([1, 2])

    with left:
        # Contract summary
        obligations_html = "".join([
            f'<li style="color:#cbd5e1;font-size:0.85rem;'
            f'padding:5px 0;border-bottom:1px solid #1e1e2e">'
            f'{o}</li>'
            for o in report.summary.key_obligations
        ])

        parties_html = " · ".join([
            f'<span style="color:#a78bfa">{p}</span>'
            for p in report.summary.parties
        ])

        st.markdown(f"""
        <div class="section-card">
            <div class="section-label" style="color:#818cf8">
                📋 Contract Summary
            </div>
            <div style="margin-bottom:12px">
                <span style="font-size:0.78rem;color:#64748b">
                    TYPE
                </span><br>
                <span style="font-size:0.95rem;font-weight:700;
                      color:#e2e8f0">
                    {report.summary.contract_type}
                </span>
            </div>
            <div style="margin-bottom:12px">
                <span style="font-size:0.78rem;color:#64748b">
                    PARTIES
                </span><br>
                <span style="font-size:0.85rem">{parties_html}</span>
            </div>
            <div style="margin-bottom:12px">
                <span style="font-size:0.78rem;color:#64748b">
                    DURATION
                </span><br>
                <span style="font-size:0.85rem;color:#cbd5e1">
                    {report.summary.contract_duration}
                </span>
            </div>
            <div style="margin-bottom:12px">
                <span style="font-size:0.78rem;color:#64748b">
                    GOVERNING LAW
                </span><br>
                <span style="font-size:0.85rem;color:#cbd5e1">
                    {report.summary.governing_law}
                </span>
            </div>
            <div>
                <span style="font-size:0.78rem;color:#64748b">
                    KEY OBLIGATIONS
                </span>
                <ul style="padding-left:16px;margin-top:8px">
                    {obligations_html}
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Risk breakdown
        total = report.total_clauses_scanned or 1
        high_pct  = int(report.high_risk_count / total * 100)
        med_pct   = int(report.medium_risk_count / total * 100)
        low_pct   = 100 - high_pct - med_pct

        st.markdown(f"""
        <div class="section-card">
            <div class="section-label" style="color:#f87171">
                📊 Risk Breakdown
            </div>
            <div style="margin-bottom:10px">
                <div style="display:flex;justify-content:space-between;
                     font-size:0.8rem;margin-bottom:4px">
                    <span style="color:#f87171">HIGH</span>
                    <span style="color:#f87171">{high_pct}%</span>
                </div>
                <div style="background:#1e1e2e;border-radius:4px;height:8px">
                    <div style="width:{high_pct}%;height:100%;
                         background:#ef4444;border-radius:4px"></div>
                </div>
            </div>
            <div style="margin-bottom:10px">
                <div style="display:flex;justify-content:space-between;
                     font-size:0.8rem;margin-bottom:4px">
                    <span style="color:#fbbf24">MEDIUM</span>
                    <span style="color:#fbbf24">{med_pct}%</span>
                </div>
                <div style="background:#1e1e2e;border-radius:4px;height:8px">
                    <div style="width:{med_pct}%;height:100%;
                         background:#fbbf24;border-radius:4px"></div>
                </div>
            </div>
            <div>
                <div style="display:flex;justify-content:space-between;
                     font-size:0.8rem;margin-bottom:4px">
                    <span style="color:#34d399">LOW/SAFE</span>
                    <span style="color:#34d399">{low_pct}%</span>
                </div>
                <div style="background:#1e1e2e;border-radius:4px;height:8px">
                    <div style="width:{low_pct}%;height:100%;
                         background:#34d399;border-radius:4px"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        # Risk filter
        st.markdown("**🔍 Filter by Risk Level**")
        filter_col = st.columns(4)
        filters = {
            "ALL":    filter_col[0].checkbox("All",    value=True),
            "HIGH":   filter_col[1].checkbox("🔴 High",   value=False),
            "MEDIUM": filter_col[2].checkbox("🟡 Medium", value=False),
            "LOW":    filter_col[3].checkbox("🟢 Low",    value=False),
        }

        # Determine which risks to show
        show_all = filters["ALL"]
        show_levels = []
        if show_all:
            show_levels = ["HIGH", "MEDIUM", "LOW", "NONE"]
        else:
            if filters["HIGH"]:   show_levels.append("HIGH")
            if filters["MEDIUM"]: show_levels.append("MEDIUM")
            if filters["LOW"]:
                show_levels.append("LOW")
                show_levels.append("NONE")

        if not show_levels:
            show_levels = ["HIGH", "MEDIUM", "LOW", "NONE"]

        # Display clauses
        filtered = [
            r for r in report.clause_risks
            if r.risk_level in show_levels
        ]

        st.caption(
            f"Showing {len(filtered)} of "
            f"{report.total_clauses_scanned} clauses"
        )

        for risk in filtered:
            risk_colors = {
                "HIGH":   "#ef4444",
                "MEDIUM": "#fbbf24",
                "LOW":    "#34d399",
                "NONE":   "#475569"
            }
            color = risk_colors.get(risk.risk_level, "#475569")

            with st.expander(
                f"{'🔴' if risk.risk_level == 'HIGH' else '🟡' if risk.risk_level == 'MEDIUM' else '🟢'} "
                f"{risk.risk_category} — {risk.risk_summary[:70]}...",
                expanded=(risk.risk_level == "HIGH")
            ):
                # Risk badge row
                badge_col1, badge_col2, badge_col3 = st.columns([1,1,3])
                with badge_col1:
                    st.markdown(
                        f'<span style="background:rgba(0,0,0,0.3);'
                        f'color:{color};border:1px solid {color};'
                        f'padding:3px 12px;border-radius:20px;'
                        f'font-size:0.75rem;font-weight:700">'
                        f'{risk.risk_level}</span>',
                        unsafe_allow_html=True
                    )
                with badge_col2:
                    st.markdown(
                        f'<span style="background:rgba(139,92,246,0.1);'
                        f'color:#a78bfa;border:1px solid rgba(139,92,246,0.2);'
                        f'padding:3px 10px;border-radius:20px;'
                        f'font-size:0.72rem">'
                        f'{risk.risk_category}</span>',
                        unsafe_allow_html=True
                    )
                with badge_col3:
                    if not risk.is_standard:
                        st.markdown(
                            '<span style="color:#f87171;'
                            'font-size:0.78rem">⚠️ Non-standard clause</span>',
                            unsafe_allow_html=True
                        )

                st.divider()

                # Clause text
                st.markdown("**📄 Original Clause**")
                st.markdown(
                    f'<div style="background:#0d0d18;border:1px solid #1e1e2e;'
                    f'border-radius:8px;padding:12px 16px;font-size:0.82rem;'
                    f'color:#64748b;font-style:italic;line-height:1.7">'
                    f'"{risk.clause_text}'
                    f'{"..." if len(risk.clause_text) >= 300 else ""}"'
                    f'</div>',
                    unsafe_allow_html=True
                )

                st.markdown("<br>", unsafe_allow_html=True)

                # Three info columns
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**💬 Plain English**")
                    st.info(risk.plain_english)

                with col2:
                    st.markdown("**⚠️ What to Watch**")
                    st.warning(risk.what_to_watch)

                with col3:
                    st.markdown("**💡 Negotiation Tip**")
                    st.success(risk.negotiation_tip)
    # ── Disclaimer ──
    st.caption(
        "⚠️ ClauseGuard is an AI assistant for contract awareness, "
        "not a substitute for professional legal advice. "
        "Always consult a qualified lawyer before signing "
        "significant agreements."
    )