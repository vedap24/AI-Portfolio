import streamlit as st
from app import (
    generate_curriculum,
    ask_mentor,
    KB_COLLECTION
)
from knowledge import (
    BACKGROUND_OPTIONS,
    GOAL_OPTIONS,
    TIME_OPTIONS
)

# ── Page config ──
st.set_page_config(
    page_title="MentorAI",
    page_icon="🎓",
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
            90deg, #a78bfa, #34d399
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

    .headline-box {
        background: rgba(167,139,250,0.06);
        border: 1px solid rgba(167,139,250,0.2);
        border-left: 3px solid #a78bfa;
        border-radius: 0 10px 10px 0;
        padding: 16px 20px;
        font-size: 1rem;
        color: #ddd6fe;
        line-height: 1.75;
        font-style: italic;
        margin-bottom: 16px;
    }

    .score-ring {
        text-align: center;
        padding: 16px;
    }

    .score-num {
        font-size: 3.5rem;
        font-weight: 900;
        line-height: 1;
    }

    .score-label {
        font-size: 0.72rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 4px;
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

    .phase-card {
        background: #0d1520;
        border: 1px solid #1e2a3a;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        border-left: 3px solid #a78bfa;
    }

    .phase-number {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #a78bfa;
        margin-bottom: 4px;
    }

    .phase-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 8px;
    }

    .phase-focus {
        font-size: 0.85rem;
        color: #64748b;
        margin-bottom: 12px;
        font-style: italic;
    }

    .skill-pill {
        display: inline-block;
        background: rgba(167,139,250,0.08);
        border: 1px solid rgba(167,139,250,0.2);
        color: #a78bfa;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        margin: 3px;
    }

    .project-item {
        font-size: 0.85rem;
        color: #34d399;
        padding: 5px 0;
        border-bottom: 1px solid #1e2a3a;
    }

    .project-item:last-child {
        border-bottom: none;
    }

    .resource-item {
        font-size: 0.82rem;
        color: #94a3b8;
        padding: 4px 0;
    }

    .milestone-box {
        background: rgba(52,211,153,0.05);
        border: 1px solid rgba(52,211,153,0.15);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.82rem;
        color: #6ee7b7;
        margin-top: 12px;
    }

    .portfolio-card {
        background: #0d1520;
        border: 1px solid #1e2a3a;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }

    .portfolio-name {
        font-size: 0.95rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 6px;
    }

    .portfolio-desc {
        font-size: 0.82rem;
        color: #64748b;
        margin-bottom: 10px;
        line-height: 1.6;
    }

    .difficulty-Beginner {
        background: rgba(52,211,153,0.1);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.25);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.68rem;
        font-weight: 700;
        display: inline-block;
    }

    .difficulty-Intermediate {
        background: rgba(251,191,36,0.1);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.25);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.68rem;
        font-weight: 700;
        display: inline-block;
    }

    .difficulty-Advanced {
        background: rgba(239,68,68,0.1);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.25);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.68rem;
        font-weight: 700;
        display: inline-block;
    }

    .technique-pill {
        display: inline-block;
        background: rgba(6,182,212,0.08);
        border: 1px solid rgba(6,182,212,0.2);
        color: #22d3ee;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.68rem;
        margin: 2px;
    }

    .schedule-row {
        display: flex;
        gap: 10px;
        padding: 7px 0;
        border-bottom: 1px solid #1e2a3a;
        font-size: 0.83rem;
    }

    .schedule-row:last-child {
        border-bottom: none;
    }

    .schedule-day {
        color: #a78bfa;
        font-weight: 700;
        min-width: 90px;
        text-transform: uppercase;
        font-size: 0.72rem;
        letter-spacing: 1px;
        padding-top: 2px;
    }

    .schedule-task {
        color: #94a3b8;
        flex: 1;
        line-height: 1.5;
    }

    .gap-box {
        background: rgba(239,68,68,0.05);
        border: 1px solid rgba(239,68,68,0.15);
        border-left: 3px solid #ef4444;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        font-size: 0.85rem;
        color: #fca5a5;
        margin-bottom: 12px;
    }

    .next-step-box {
        background: rgba(52,211,153,0.06);
        border: 1px solid rgba(52,211,153,0.2);
        border-radius: 10px;
        padding: 16px 20px;
        font-size: 0.9rem;
        color: #6ee7b7;
        line-height: 1.75;
        margin-bottom: 16px;
    }

    .insight-box {
        background: rgba(251,191,36,0.05);
        border: 1px solid rgba(251,191,36,0.15);
        border-radius: 10px;
        padding: 14px 18px;
        font-size: 0.88rem;
        color: #fcd34d;
        line-height: 1.75;
        font-style: italic;
    }

    .topic-pill {
        display: inline-block;
        background: rgba(167,139,250,0.08);
        border: 1px solid rgba(167,139,250,0.15);
        color: #c4b5fd;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        margin: 3px;
    }

    .mentor-q {
        background: rgba(167,139,250,0.06);
        border: 1px solid rgba(167,139,250,0.15);
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
    }

    .skip-pill {
        display: inline-block;
        background: rgba(100,116,139,0.1);
        border: 1px solid rgba(100,116,139,0.2);
        color: #64748b;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        margin: 3px;
        text-decoration: line-through;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ──
if "result" not in st.session_state:
    st.session_state.result = None
if "mentor_chat" not in st.session_state:
    st.session_state.mentor_chat = []
if "profile" not in st.session_state:
    st.session_state.profile = {}

# ── Header ──
st.markdown(
    '<div class="main-title">🎓 MentorAI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">'
    'Tell me your background and goal → '
    'get a personalized AI engineering '
    'curriculum with phases, projects, '
    'weekly schedule, and salary milestones.'
    '</div>',
    unsafe_allow_html=True
)

st.info(
    "📊 **AI Talent Report, 2026** — "
    "AI talent demand exceeds supply 3.2:1 globally. "
    "1.6M open positions, only 518K qualified candidates. "
    "AI roles command a 56% wage premium. "
    "**MentorAI gives you the exact roadmap "
    "to close that gap.**"
)

st.divider()

# ── Profile input ──
st.markdown("### 👤 Your Profile")

col1, col2, col3 = st.columns(3)

with col1:
    background = st.selectbox(
        "Your current background",
        options=BACKGROUND_OPTIONS
    )

with col2:
    goal = st.selectbox(
        "Your goal",
        options=GOAL_OPTIONS
    )

with col3:
    time_available = st.selectbox(
        "Time available per day",
        options=TIME_OPTIONS
    )

generate_btn = st.button(
    "🚀 Generate My Learning Path",
    use_container_width=True,
    type="primary"
)

if generate_btn:
    with st.spinner(
        "🤖 Building your personalized "
        "curriculum..."
    ):
        try:
            result = generate_curriculum(
                background=background,
                goal=goal,
                time_available=time_available,
                collection=KB_COLLECTION
            )
            st.session_state.result = result
            st.session_state.profile = {
                "background":     background,
                "goal":           goal,
                "time_available": time_available
            }
            st.session_state.mentor_chat = []
            st.rerun()
        except Exception as e:
            st.error(f"❌ {e}")

st.divider()

# ── Display curriculum ──
if st.session_state.result:
    result = st.session_state.result
    curr   = result.curriculum

    st.success(
        f"✅ Curriculum generated for: "
        f"{result.background}"
    )

    # ── Headline ──
    st.markdown(
        f'<div class="headline-box">'
        f'🎯 {curr.headline}'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Score + stats ──
    score = curr.readiness_score
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
            f'Readiness Score</div>'
            f'<div style="font-size:0.8rem;'
            f'color:{score_color};'
            f'margin-top:6px;font-weight:700">'
            f'{curr.readiness_label}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with sc2:
        s1, s2, s3, s4 = st.columns(4)
        for col, val, color, label in [
            (s1, curr.total_weeks,
             "#a78bfa", "Total Weeks"),
            (s2, curr.weekly_hours,
             "#34d399", "Hours/Week"),
            (s3, len(curr.phases),
             "#22d3ee", "Phases"),
            (s4, len(curr.portfolio_projects),
             "#f59e0b", "Portfolio Projects")
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

    st.divider()

    # ── Key callouts ──
    k1, k2 = st.columns(2)

    with k1:
        # Immediate next step
        st.markdown(
            '<div style="font-size:0.7rem;'
            'font-weight:700;letter-spacing:2px;'
            'text-transform:uppercase;'
            'color:#34d399;margin-bottom:10px">'
            '⚡ Do This Today'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="next-step-box">'
            f'{curr.immediate_next_step}'
            f'</div>',
            unsafe_allow_html=True
        )

        # Biggest gap
        st.markdown(
            '<div style="font-size:0.7rem;'
            'font-weight:700;letter-spacing:2px;'
            'text-transform:uppercase;'
            'color:#f87171;margin-bottom:10px">'
            '🎯 Biggest Gap to Close'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="gap-box">'
            f'{curr.biggest_gap}'
            f'</div>',
            unsafe_allow_html=True
        )

    with k2:
        # Salary + timeline
        st.markdown(
            f'<div class="stat-box" '
            f'style="margin-bottom:12px;'
            f'text-align:left;padding:20px">'
            f'<div style="font-size:0.7rem;'
            f'color:#475569;text-transform:uppercase;'
            f'letter-spacing:1px;'
            f'margin-bottom:8px">'
            f'Salary Unlocked</div>'
            f'<div style="font-size:1.4rem;'
            f'font-weight:900;color:#34d399">'
            f'{curr.salary_unlock}</div>'
            f'<div style="font-size:0.7rem;'
            f'color:#475569;text-transform:uppercase;'
            f'letter-spacing:1px;'
            f'margin-top:14px;margin-bottom:8px">'
            f'Time to First Job</div>'
            f'<div style="font-size:1.1rem;'
            f'font-weight:700;color:#a78bfa">'
            f'{curr.time_to_first_job}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Skills to skip
        if curr.skills_to_skip:
            st.markdown(
                '<div style="font-size:0.7rem;'
                'font-weight:700;letter-spacing:2px;'
                'text-transform:uppercase;'
                'color:#475569;margin-bottom:8px">'
                '⏭️ Skip These (You Know Them)'
                '</div>',
                unsafe_allow_html=True
            )
            pills = "".join([
                f'<span class="skip-pill">'
                f'{s}</span>'
                for s in curr.skills_to_skip
            ])
            st.markdown(
                f'<div>{pills}</div>',
                unsafe_allow_html=True
            )

    st.divider()

    # ── Main content ──
    left, right = st.columns([3, 2])

    with left:
        # Learning phases
        st.markdown(
            '<div style="font-size:0.7rem;'
            'font-weight:700;letter-spacing:2px;'
            'text-transform:uppercase;'
            'color:#a78bfa;margin-bottom:16px">'
            '📚 Your Learning Path'
            '</div>',
            unsafe_allow_html=True
        )

        for phase in curr.phases:
            st.markdown(
                f'<div class="phase-card">',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="phase-number">'
                f'Phase {phase.phase_number} · '
                f'{phase.duration_weeks} weeks'
                f'</div>'
                f'<div class="phase-title">'
                f'{phase.phase_title}'
                f'</div>'
                f'<div class="phase-focus">'
                f'{phase.focus_area}'
                f'</div>',
                unsafe_allow_html=True
            )

            # Skills
            if phase.skills:
                pills = "".join([
                    f'<span class="skill-pill">'
                    f'{s}</span>'
                    for s in phase.skills
                ])
                st.markdown(
                    f'<div style="margin-bottom:12px">'
                    f'{pills}</div>',
                    unsafe_allow_html=True
                )

            p1, p2 = st.columns(2)

            with p1:
                if phase.projects:
                    st.markdown(
                        '<div style="font-size:'
                        '0.68rem;color:#475569;'
                        'text-transform:uppercase;'
                        'letter-spacing:1px;'
                        'margin-bottom:6px">'
                        'Projects</div>',
                        unsafe_allow_html=True
                    )
                    for proj in phase.projects:
                        st.markdown(
                            f'<div class="project-item">'
                            f'→ {proj}</div>',
                            unsafe_allow_html=True
                        )

            with p2:
                if phase.resources:
                    st.markdown(
                        '<div style="font-size:'
                        '0.68rem;color:#475569;'
                        'text-transform:uppercase;'
                        'letter-spacing:1px;'
                        'margin-bottom:6px">'
                        'Resources</div>',
                        unsafe_allow_html=True
                    )
                    for res in phase.resources:
                        st.markdown(
                            f'<div class="resource-item">'
                            f'📖 {res}</div>',
                            unsafe_allow_html=True
                        )

            # Milestone
            st.markdown(
                f'<div class="milestone-box">'
                f'🏆 Milestone: {phase.milestone}'
                f'</div>',
                unsafe_allow_html=True
            )

            # Why this phase
            if phase.why_this_phase:
                st.markdown(
                    f'<div style="font-size:0.78rem;'
                    f'color:#475569;margin-top:10px;'
                    f'font-style:italic">'
                    f'Why now: {phase.why_this_phase}'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )

    with right:
        # Weekly schedule
        st.markdown(
            '<div style="font-size:0.7rem;'
            'font-weight:700;letter-spacing:2px;'
            'text-transform:uppercase;'
            'color:#22d3ee;margin-bottom:14px">'
            '📅 Weekly Schedule'
            '</div>',
            unsafe_allow_html=True
        )

        schedule = curr.weekly_schedule
        days = [
            ("Monday",    schedule.monday),
            ("Tuesday",   schedule.tuesday),
            ("Wednesday", schedule.wednesday),
            ("Thursday",  schedule.thursday),
            ("Friday",    schedule.friday),
            ("Saturday",  schedule.saturday),
            ("Sunday",    schedule.sunday)
        ]

        schedule_html = "".join([
            f'<div class="schedule-row">'
            f'<span class="schedule-day">'
            f'{day}</span>'
            f'<span class="schedule-task">'
            f'{task}</span>'
            f'</div>'
            for day, task in days
        ])
        st.markdown(
            f'<div style="background:#0d1520;'
            f'border:1px solid #1e2a3a;'
            f'border-radius:10px;padding:16px">'
            f'{schedule_html}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            "<br>", unsafe_allow_html=True
        )

        # Motivational insight
        st.markdown(
            '<div style="font-size:0.7rem;'
            'font-weight:700;letter-spacing:2px;'
            'text-transform:uppercase;'
            'color:#fbbf24;margin-bottom:10px">'
            '💡 Mentor Insight'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="insight-box">'
            f'"{curr.motivational_insight}"'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            "<br>", unsafe_allow_html=True
        )

        # Topics retrieved
        with st.expander(
            "📚 Roadmap sections used"
        ):
            for topic in result.topics_covered:
                st.markdown(
                    f'<span class="topic-pill">'
                    f'{topic}</span>',
                    unsafe_allow_html=True
                )

    st.divider()

    # ── Portfolio projects ──
    st.markdown(
        '<div style="font-size:0.7rem;'
        'font-weight:700;letter-spacing:2px;'
        'text-transform:uppercase;'
        'color:#f59e0b;margin-bottom:16px">'
        '🏗️ Portfolio Projects to Build'
        '</div>',
        unsafe_allow_html=True
    )

    proj_cols = st.columns(
        min(
            len(curr.portfolio_projects), 3
        )
    )

    for i, proj in enumerate(
        curr.portfolio_projects
    ):
        with proj_cols[i % len(proj_cols)]:
            diff_cls = (
                f"difficulty-{proj.difficulty}"
            )
            techniques = " ".join([
                f'<span class="technique-pill">'
                f'{t}</span>'
                for t in
                proj.techniques_demonstrated[:4]
            ])
            st.markdown(
                f'<div class="portfolio-card">'
                f'<div class="portfolio-name">'
                f'{proj.project_name}</div>'
                f'<span class="{diff_cls}">'
                f'{proj.difficulty}</span>'
                f'<div class="portfolio-desc" '
                f'style="margin-top:8px">'
                f'{proj.description}</div>'
                f'<div style="margin-bottom:8px">'
                f'{techniques}</div>'
                f'<div style="font-size:0.78rem;'
                f'color:#475569;'
                f'border-top:1px solid #1e2a3a;'
                f'padding-top:8px;margin-top:4px">'
                f'💼 {proj.impact}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.divider()

    # ── AI Mentor chat ──
    st.markdown(
        '<div style="font-size:0.7rem;'
        'font-weight:700;letter-spacing:2px;'
        'text-transform:uppercase;'
        'color:#a78bfa;margin-bottom:14px">'
        '🤖 Ask Your AI Mentor'
        '</div>',
        unsafe_allow_html=True
    )

    # Quick questions
    profile = st.session_state.profile
    quick_qs = [
        "Should I learn LangChain or "
        "build agents from scratch?",
        "What should I put on my GitHub "
        "to impress recruiters?",
        "How do I explain this career gap "
        "in interviews?",
    ]

    q_cols = st.columns(3)
    for i, qq in enumerate(quick_qs):
        with q_cols[i]:
            if st.button(
                qq,
                key=f"mq_{i}",
                use_container_width=True
            ):
                with st.spinner("Thinking..."):
                    try:
                        ans = ask_mentor(
                            qq,
                            profile.get(
                                "background", ""
                            ),
                            profile.get(
                                "goal", ""
                            )
                        )
                        st.session_state\
                            .mentor_chat.insert(
                                0, {
                                    "q": qq,
                                    "a": ans
                                }
                            )
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")

    # Custom question
    mentor_q = st.text_input(
        label="mentor_q",
        label_visibility="collapsed",
        placeholder=(
            "Ask anything about your "
            "learning path..."
        )
    )

    if mentor_q.strip():
        if st.button(
            "💬 Ask Mentor",
            type="primary"
        ):
            with st.spinner("Thinking..."):
                try:
                    ans = ask_mentor(
                        mentor_q,
                        profile.get(
                            "background", ""
                        ),
                        profile.get("goal", "")
                    )
                    st.session_state\
                        .mentor_chat.insert(
                            0, {
                                "q": mentor_q,
                                "a": ans
                            }
                        )
                    st.rerun()
                except ValueError as e:
                    st.warning(f"⚠️ {e}")
                except Exception as e:
                    st.error(f"❌ {e}")

    # Render chat
    for item in st.session_state.mentor_chat:
        st.markdown(
            f'<div class="mentor-q">'
            f'<div style="font-size:0.75rem;'
            f'font-weight:700;color:#a78bfa;'
            f'margin-bottom:8px">'
            f'Q: {item["q"]}</div>'
            f'<div style="font-size:0.85rem;'
            f'color:#94a3b8;line-height:1.75">'
            f'{item["a"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.caption(
        f"🎓 MentorAI — "
        f"Personalized AI Engineering Roadmap · "
        f"Powered by RAG + Gemini 2.0 Flash · "
        f"Day 14 of 14"
    )