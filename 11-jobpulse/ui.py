import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
from app import (
    analyze_job_search,
    ask_followup,
    load_csv,
    run_full_analysis
)
from sample_data import get_sample_csv

# ── Page config ──
st.set_page_config(
    page_title="JobPulse AI",
    page_icon="📊",
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
            90deg, #f59e0b, #ec4899
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

    .score-ring {
        text-align: center;
        padding: 20px;
    }

    .score-num {
        font-size: 3.5rem;
        font-weight: 900;
        line-height: 1;
    }

    .score-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 4px;
    }

    .headline-box {
        background: rgba(245,158,11,0.06);
        border: 1px solid rgba(245,158,11,0.2);
        border-left: 3px solid #f59e0b;
        border-radius: 0 10px 10px 0;
        padding: 16px 20px;
        font-size: 0.95rem;
        color: #fcd34d;
        line-height: 1.7;
        margin-bottom: 20px;
        font-style: italic;
    }

    .insight-card {
        background: #0d1520;
        border: 1px solid #1e2a3a;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 10px;
    }

    .insight-text {
        font-size: 0.88rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 4px;
    }

    .insight-data {
        font-size: 0.8rem;
        color: #64748b;
        font-family: monospace;
    }

    .impact-HIGH {
        background: rgba(239,68,68,0.1);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.2);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 700;
        display: inline-block;
        margin-right: 6px;
    }

    .impact-MEDIUM {
        background: rgba(251,191,36,0.1);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.2);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 700;
        display: inline-block;
        margin-right: 6px;
    }

    .impact-LOW {
        background: rgba(100,116,139,0.1);
        color: #94a3b8;
        border: 1px solid rgba(100,116,139,0.2);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 700;
        display: inline-block;
        margin-right: 6px;
    }

    .change-card {
        background: #0d1520;
        border: 1px solid #1e2a3a;
        border-left: 3px solid #ec4899;
        border-radius: 0 10px 10px 0;
        padding: 16px 20px;
        margin-bottom: 12px;
    }

    .change-problem {
        font-size: 0.9rem;
        font-weight: 700;
        color: #f87171;
        margin-bottom: 4px;
    }

    .change-evidence {
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 8px;
        font-style: italic;
    }

    .change-action {
        font-size: 0.85rem;
        color: #34d399;
        line-height: 1.6;
    }

    .working-item {
        font-size: 0.85rem;
        color: #34d399;
        padding: 6px 0;
        border-bottom: 1px solid #1e2a3a;
        line-height: 1.6;
    }

    .working-item:last-child {
        border-bottom: none;
    }

    .action-item {
        font-size: 0.85rem;
        color: #94a3b8;
        padding: 7px 0;
        border-bottom: 1px solid #1e2a3a;
        line-height: 1.6;
        display: flex;
        gap: 8px;
    }

    .action-item:last-child {
        border-bottom: none;
    }

    .stat-box {
        background: #0d1520;
        border: 1px solid #1e2a3a;
        border-radius: 10px;
        padding: 16px;
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
        margin-top: 2px;
    }

    .bench-box {
        background: #0d1520;
        border: 1px solid #1e2a3a;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }

    .timeline-pill {
        background: rgba(236,72,153,0.1);
        border: 1px solid rgba(236,72,153,0.2);
        color: #f472b6;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ──
if "analysis" not in st.session_state:
    st.session_state.analysis  = None
if "insights" not in st.session_state:
    st.session_state.insights  = None
if "df" not in st.session_state:
    st.session_state.df        = None
if "chat" not in st.session_state:
    st.session_state.chat      = []

# ── Header ──
st.markdown(
    '<div class="main-title">📊 JobPulse AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">'
    'Upload your job application data → '
    'get AI-powered insights on what\'s working, '
    'what to change, and your predicted timeline.'
    '</div>',
    unsafe_allow_html=True
)

st.info(
    "📊 **Upplai Research, March 2026** — "
    "Indeed response rates: 20–25%. "
    "LinkedIn: 3–13%. "
    "Referrals: 8x more likely to get hired. "
    "Most job seekers never track which "
    "channel works. **JobPulse shows you.**"
)

st.divider()

# ── Upload section ──
st.markdown("### 📁 Upload Your Application Data")

up_col, demo_col = st.columns([3, 1])

with up_col:
    uploaded = st.file_uploader(
        label="csv",
        label_visibility="collapsed",
        type=["csv"],
        help=(
            "CSV with columns: company, role, "
            "source, status, date_applied. "
            "Optional: company_size, industry, "
            "notes, salary_range"
        )
    )

with demo_col:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(
        "🎯 Use Sample Data",
        use_container_width=True
    ):
        csv_str = get_sample_csv()
        analysis, insights, df = \
            analyze_job_search(csv_str)
        st.session_state.analysis = analysis
        st.session_state.insights = insights
        st.session_state.df       = df
        st.rerun()

# Handle file upload
if uploaded:
    csv_str = uploaded.read().decode("utf-8")
    if st.button(
        "🚀 Analyze My Data",
        use_container_width=True,
        type="primary"
    ):
        with st.spinner(
            "Analyzing your job search data..."
        ):
            try:
                analysis, insights, df = \
                    analyze_job_search(csv_str)
                st.session_state.analysis = \
                    analysis
                st.session_state.insights = \
                    insights
                st.session_state.df = df
                st.rerun()
            except ValueError as e:
                st.warning(f"⚠️ {e}")
            except Exception as e:
                st.error(f"❌ {e}")

# ── CSV format helper ──
with st.expander("📋 Required CSV format"):
    st.code(
        "company,role,source,status,"
        "date_applied,company_size,"
        "industry,notes,salary_range\n"
        "Google,AI Engineer,LinkedIn,"
        "Phone Screen,2025-01-15,"
        "Large,Tech,,\n"
        "Stripe,ML Engineer,Referral,"
        "Offer,2025-01-20,Mid,"
        "Fintech,,",
        language="csv"
    )
    st.caption(
        "Required: company, role, source, "
        "status, date_applied. "
        "Status values: Applied, Phone Screen, "
        "Technical Interview, Final Round, "
        "Offer, Rejected, No Response"
    )

st.divider()

# ── Main dashboard ──
if st.session_state.analysis and \
   st.session_state.insights and \
   st.session_state.df is not None:

    analysis = st.session_state.analysis
    insights = st.session_state.insights
    df       = st.session_state.df
    funnel   = analysis["funnel"]

    st.success(
        f"✅ Analyzed {funnel['total']} applications"
    )

    # ── Score + headline ──
    score = insights.performance_score
    score_color = (
        "#34d399" if score >= 70
        else "#fbbf24" if score >= 40
        else "#f87171"
    )

    sc1, sc2 = st.columns([1, 3])

    with sc1:
        st.markdown(
            f'<div class="score-ring">'
            f'<div class="score-num" '
            f'style="color:{score_color}">'
            f'{score}</div>'
            f'<div class="score-label">'
            f'Performance Score</div>'
            f'<div style="font-size:0.75rem;'
            f'color:#475569;margin-top:6px">'
            f'{insights.score_reasoning[:60]}'
            f'...</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with sc2:
        st.markdown(
            f'<div class="headline-box">'
            f'💡 {insights.headline_insight}'
            f'</div>',
            unsafe_allow_html=True
        )

        # Predicted timeline
        st.markdown(
            f'<span class="timeline-pill">'
            f'⏱️ {insights.predicted_timeline}'
            f'</span>',
            unsafe_allow_html=True
        )

    st.divider()

    # ── Stats row ──
    s1, s2, s3, s4, s5 = st.columns(5)
    stat_data = [
        (s1, funnel['total'],
         "#f59e0b", "Total Apps"),
        (s2, f"{funnel['response_rate']}%",
         "#34d399", "Response Rate"),
        (s3, f"{funnel['interview_rate']}%",
         "#818cf8", "Interview Rate"),
        (s4, f"{funnel['ghost_rate']}%",
         "#f87171", "Ghost Rate"),
        (s5, funnel['offers'],
         "#34d399", "Offers"),
    ]
    for col, num, color, label in stat_data:
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

    # ── Charts row ──
    ch1, ch2 = st.columns(2)

    with ch1:
        # Funnel chart
        st.markdown("**📉 Application Funnel**")
        funnel_data = {
            "Stage": [
                "Applied",
                "Phone Screen",
                "Technical",
                "Final Round",
                "Offer"
            ],
            "Count": [
                funnel["applied"],
                funnel["phone_screen"],
                funnel["technical"],
                funnel["final_round"],
                funnel["offers"]
            ]
        }
        fig_funnel = go.Figure(
            go.Funnel(
                y=funnel_data["Stage"],
                x=funnel_data["Count"],
                textinfo="value+percent initial",
                marker=dict(
                    color=[
                        "#f59e0b",
                        "#818cf8",
                        "#06b6d4",
                        "#34d399",
                        "#10b981"
                    ]
                )
            )
        )
        fig_funnel.update_layout(
            paper_bgcolor="#0d1520",
            plot_bgcolor="#0d1520",
            font=dict(color="#94a3b8"),
            margin=dict(l=20,r=20,t=20,b=20),
            height=280
        )
        st.plotly_chart(
            fig_funnel,
            use_container_width=True
        )

    with ch2:
        # Source comparison
        st.markdown("**📊 Response Rate by Source**")
        sources = analysis["by_source"]
        if sources:
            src_df = pd.DataFrame([
                {
                    "Source": src,
                    "Response Rate": stats[
                        "response_rate"
                    ],
                    "Total Apps": stats["total"]
                }
                for src, stats in sources.items()
            ]).sort_values(
                "Response Rate",
                ascending=True
            )

            fig_src = px.bar(
                src_df,
                x="Response Rate",
                y="Source",
                orientation="h",
                color="Response Rate",
                color_continuous_scale=[
                    "#1e2a3a",
                    "#f59e0b"
                ],
                text="Response Rate"
            )
            fig_src.update_traces(
                texttemplate="%{text}%",
                textposition="outside"
            )
            fig_src.update_layout(
                paper_bgcolor="#0d1520",
                plot_bgcolor="#0d1520",
                font=dict(color="#94a3b8"),
                margin=dict(l=20,r=20,t=20,b=20),
                height=280,
                showlegend=False,
                coloraxis_showscale=False,
                xaxis=dict(
                    gridcolor="#1e2a3a",
                    title=""
                ),
                yaxis=dict(title="")
            )
            st.plotly_chart(
                fig_src,
                use_container_width=True
            )

    # Status breakdown pie
    ch3, ch4 = st.columns(2)

    with ch3:
        st.markdown("**🍩 Status Distribution**")
        status_counts = funnel["status_counts"]
        if status_counts:
            fig_pie = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                color_discrete_sequence=[
                    "#f59e0b", "#818cf8",
                    "#06b6d4", "#34d399",
                    "#f87171", "#94a3b8",
                    "#ec4899"
                ],
                hole=0.4
            )
            fig_pie.update_layout(
                paper_bgcolor="#0d1520",
                font=dict(color="#94a3b8"),
                margin=dict(l=20,r=20,t=20,b=20),
                height=260,
                legend=dict(
                    bgcolor="#0d1520",
                    font=dict(size=11)
                )
            )
            st.plotly_chart(
                fig_pie,
                use_container_width=True
            )

    with ch4:
        # Weekly timeline
        st.markdown("**📅 Applications Over Time**")
        timeline = analysis["timeline"]
        if timeline.get("weekly_data"):
            weeks = timeline["weekly_data"]
            fig_time = px.bar(
                x=[w["week"] for w in weeks],
                y=[w["count"] for w in weeks],
                color_discrete_sequence=[
                    "#818cf8"
                ]
            )
            fig_time.update_layout(
                paper_bgcolor="#0d1520",
                plot_bgcolor="#0d1520",
                font=dict(color="#94a3b8"),
                margin=dict(l=20,r=20,t=20,b=20),
                height=260,
                xaxis=dict(
                    gridcolor="#1e2a3a",
                    title="",
                    tickangle=45
                ),
                yaxis=dict(
                    gridcolor="#1e2a3a",
                    title="Apps"
                )
            )
            st.plotly_chart(
                fig_time,
                use_container_width=True
            )

    st.divider()

    # ── AI Insights ──
    left, right = st.columns([1, 1])

    with left:
        # Key insights
        st.markdown(
            '<div style="font-size:0.7rem;'
            'font-weight:700;letter-spacing:2px;'
            'text-transform:uppercase;'
            'color:#f59e0b;margin-bottom:14px">'
            '🔍 Key Insights'
            '</div>',
            unsafe_allow_html=True
        )

        for ki in insights.key_insights:
            imp_cls = f"impact-{ki.impact}"
            st.markdown(
                f'<div class="insight-card">'
                f'<div class="insight-text">'
                f'<span class="{imp_cls}">'
                f'{ki.impact}</span>'
                f'{ki.insight}'
                f'</div>'
                f'<div class="insight-data">'
                f'📊 {ki.data_point}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # What is working
        if insights.what_is_working:
            st.markdown(
                '<div style="font-size:0.7rem;'
                'font-weight:700;letter-spacing:2px;'
                'text-transform:uppercase;'
                'color:#34d399;margin-bottom:12px">'
                '✅ What Is Working'
                '</div>',
                unsafe_allow_html=True
            )
            items_html = "".join([
                f'<div class="working-item">'
                f'✓ {w}</div>'
                for w in insights.what_is_working
            ])
            st.markdown(
                f'<div style="background:#0d1520;'
                f'border:1px solid #1e2a3a;'
                f'border-radius:10px;'
                f'padding:16px">'
                f'{items_html}</div>',
                unsafe_allow_html=True
            )

    with right:
        # What to change
        st.markdown(
            '<div style="font-size:0.7rem;'
            'font-weight:700;letter-spacing:2px;'
            'text-transform:uppercase;'
            'color:#ec4899;margin-bottom:14px">'
            '🔄 What To Change'
            '</div>',
            unsafe_allow_html=True
        )

        for ch in insights.what_to_change:
            st.markdown(
                f'<div class="change-card">'
                f'<div class="change-problem">'
                f'⚠️ {ch.problem}</div>'
                f'<div class="change-evidence">'
                f'Evidence: {ch.evidence}'
                f'</div>'
                f'<div class="change-action">'
                f'→ {ch.action}</div>'
                f'<div style="font-size:0.75rem;'
                f'color:#475569;margin-top:6px">'
                f'Impact: {ch.expected_impact}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Weekly action plan
        if insights.weekly_action_plan:
            st.markdown(
                '<div style="font-size:0.7rem;'
                'font-weight:700;letter-spacing:2px;'
                'text-transform:uppercase;'
                'color:#818cf8;margin-bottom:12px">'
                '📅 This Week\'s Action Plan'
                '</div>',
                unsafe_allow_html=True
            )
            actions_html = "".join([
                f'<div class="action-item">'
                f'<span style="color:#818cf8">'
                f'{i+1}.</span>{a}'
                f'</div>'
                for i, a in enumerate(
                    insights.weekly_action_plan
                )
            ])
            st.markdown(
                f'<div style="background:#0d1520;'
                f'border:1px solid #1e2a3a;'
                f'border-radius:10px;'
                f'padding:16px">'
                f'{actions_html}</div>',
                unsafe_allow_html=True
            )

    st.divider()

    # ── Benchmark ──
    bc = insights.benchmark_comparison
    st.markdown(
        '<div style="font-size:0.7rem;'
        'font-weight:700;letter-spacing:2px;'
        'text-transform:uppercase;'
        'color:#06b6d4;margin-bottom:14px">'
        '📈 Benchmark Comparison'
        '</div>',
        unsafe_allow_html=True
    )

    b1, b2 = st.columns(2)
    with b1:
        st.markdown(
            f'<div class="bench-box">'
            f'<div style="font-size:0.72rem;'
            f'color:#475569;margin-bottom:8px">'
            f'YOUR RESPONSE RATE</div>'
            f'<div style="font-size:2rem;'
            f'font-weight:900;color:#f59e0b">'
            f'{bc.your_response_rate}</div>'
            f'<div style="font-size:0.82rem;'
            f'color:#64748b;margin-top:4px">'
            f'vs industry avg: '
            f'{bc.industry_average}</div>'
            f'<div style="font-size:0.85rem;'
            f'color:#e2e8f0;margin-top:8px">'
            f'{bc.interpretation}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with b2:
        st.markdown(
            f'<div class="bench-box">'
            f'<div style="font-size:0.72rem;'
            f'color:#475569;margin-bottom:8px">'
            f'VS INDUSTRY AVERAGE</div>'
            f'<div style="font-size:1.4rem;'
            f'font-weight:900;color:#34d399;'
            f'padding-top:8px">'
            f'{bc.your_vs_average.upper()}'
            f'</div>'
            f'<div style="font-size:0.82rem;'
            f'color:#64748b;margin-top:12px">'
            f'Predicted timeline:</div>'
            f'<div style="font-size:0.9rem;'
            f'color:#f472b6;font-weight:600">'
            f'{insights.predicted_timeline}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.divider()

    # ── AI Coach Chat ──
    st.markdown(
        '<div style="font-size:0.7rem;'
        'font-weight:700;letter-spacing:2px;'
        'text-transform:uppercase;'
        'color:#ec4899;margin-bottom:14px">'
        '🤖 Ask Your AI Career Coach'
        '</div>',
        unsafe_allow_html=True
    )

    coach_q = st.text_input(
        label="coach",
        label_visibility="collapsed",
        placeholder=(
            "Which source should I focus on? "
            "/ Am I applying to enough companies? "
            "/ What's my biggest bottleneck?"
        )
    )

    # Quick questions
    qc_cols = st.columns(3)
    quick_coach = [
        "Which source should I double down on?",
        "What's my biggest bottleneck?",
        "How do I improve my ghost rate?"
    ]
    for i, qq in enumerate(quick_coach):
        with qc_cols[i]:
            if st.button(
                qq,
                key=f"cq_{i}",
                use_container_width=True
            ):
                with st.spinner("Thinking..."):
                    try:
                        ans = ask_followup(
                            qq, analysis, df
                        )
                        st.session_state.chat\
                            .insert(0, {
                                "q": qq,
                                "a": ans
                            })
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")

    if coach_q.strip():
        if st.button(
            "💬 Ask",
            type="primary"
        ):
            with st.spinner("Analyzing..."):
                try:
                    ans = ask_followup(
                        coach_q, analysis, df
                    )
                    st.session_state.chat.insert(
                        0, {
                            "q": coach_q,
                            "a": ans
                        }
                    )
                    st.rerun()
                except ValueError as e:
                    st.warning(f"⚠️ {e}")
                except Exception as e:
                    st.error(f"❌ {e}")

    # Show chat history
    for item in st.session_state.chat:
        st.markdown(
            f'<div style="background:'
            f'rgba(236,72,153,0.05);'
            f'border:1px solid rgba(236,72,153,0.15);'
            f'border-radius:10px;padding:14px;'
            f'margin-bottom:10px">'
            f'<div style="font-size:0.8rem;'
            f'font-weight:700;color:#f472b6;'
            f'margin-bottom:8px">'
            f'Q: {item["q"]}</div>'
            f'<div style="font-size:0.85rem;'
            f'color:#94a3b8;line-height:1.75">'
            f'{item["a"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.caption(
        f"📊 JobPulse AI — "
        f"{funnel['total']} applications analyzed · "
        f"Powered by Gemini 2.0 Flash · "
        f"Day 11 of 14"
    )