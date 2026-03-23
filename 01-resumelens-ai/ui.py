import streamlit as st
from app import score_resume

# ── Page config ──
st.set_page_config(
    page_title="ResumeLens AI",
    page_icon="🔍",
    layout="wide"
)

# ── Custom CSS ──
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }

    /* Title styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #06d6a0, #118ab2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }

    .subtitle {
        color: #888;
        font-size: 1rem;
        margin-top: 4px;
        margin-bottom: 24px;
    }

    /* Score card */
    .score-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #0f3460;
        border-radius: 16px;
        padding: 28px;
        text-align: center;
        margin-bottom: 16px;
    }

    .score-number {
        font-size: 4rem;
        font-weight: 900;
        line-height: 1;
    }

    .score-label {
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 8px;
        padding: 6px 18px;
        border-radius: 20px;
        display: inline-block;
    }

    .strong  { background: #06d6a020; color: #06d6a0; border: 1px solid #06d6a0; }
    .partial { background: #ffd16620; color: #ffd166; border: 1px solid #ffd166; }
    .weak    { background: #ef476f20; color: #ef476f; border: 1px solid #ef476f; }

    /* Skill pills */
    .skill-pill {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 4px;
    }

    .matched-pill { background: #06d6a020; color: #06d6a0; border: 1px solid #06d6a040; }
    .missing-pill { background: #ef476f20; color: #ef476f; border: 1px solid #ef476f40; }

    /* Section cards */
    .section-card {
        background: #1a1a2e;
        border: 1px solid #222244;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }

    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #aaa;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }

    /* Progress bar container */
    .progress-wrap {
        background: #1a1a2e;
        border-radius: 10px;
        height: 14px;
        width: 100%;
        margin: 12px 0;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ──
st.markdown('<div class="main-title">🔍 ResumeLens AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Paste a Job Description + Resume → get an instant AI fit score powered by Gemini 2.5 Flash</div>', unsafe_allow_html=True)
st.divider()

# ── Input columns ──
col1, col2 = st.columns(2)

with col1:
    st.markdown("**📋 Job Description**")
    jd = st.text_area(
        label="jd",
        label_visibility="collapsed",
        height=280,
        placeholder="Paste the full job description here..."
    )

with col2:
    st.markdown("**📄 Your Resume**")
    resume = st.text_area(
        label="resume",
        label_visibility="collapsed",
        height=280,
        placeholder="Paste your resume text here..."
    )

st.divider()

if st.button("🚀 Analyze Resume Fit", use_container_width=True, type="primary"):

    if not jd.strip() or not resume.strip():
        st.warning("Please paste both the Job Description and your Resume.")
    else:
        with st.spinner("Gemini is analyzing your resume..."):
            try:
                result = score_resume(jd, resume)

                # ── Score color logic ──
                if result.fit_label == "Strong Match":
                    css_class = "strong"
                    bar_color = "#06d6a0"
                elif result.fit_label == "Partial Match":
                    css_class = "partial"
                    bar_color = "#ffd166"
                else:
                    css_class = "weak"
                    bar_color = "#ef476f"

                st.divider()

                # ── Score card ──
                c1, c2 = st.columns([1, 2])

                with c1:
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="score-number" style="color:{bar_color}">{result.fit_score}</div>
                        <div style="color:#888; font-size:0.9rem">out of 100</div>
                        <div class="score-label {css_class}">{result.fit_label}</div>
                        <div>
                            <div class="progress-wrap">
                                <div style="height:100%; width:{result.fit_score}%;
                                     background:{bar_color};
                                     border-radius:10px;
                                     transition: width 1s ease;">
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with c2:
                    st.markdown(f"""
                    <div class="section-card">
                        <div class="section-title">📝 AI Summary</div>
                        <p style="color:#ddd; line-height:1.7">{result.summary}</p>
                    </div>
                    <div class="section-card">
                        <div class="section-title">⚠️ Experience Gap</div>
                        <p style="color:#ffd166; line-height:1.7">{result.experience_gap}</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.divider()

                # ── Skills ──
                s1, s2 = st.columns(2)

                with s1:
                    st.markdown("**✅ Matched Skills**")
                    pills = " ".join([f'<span class="skill-pill matched-pill">{s}</span>'
                                      for s in result.matched_skills])
                    st.markdown(f'<div>{pills}</div>', unsafe_allow_html=True)

                with s2:
                    st.markdown("**❌ Missing Skills**")
                    pills = " ".join([f'<span class="skill-pill missing-pill">{s}</span>'
                                      for s in result.missing_skills])
                    st.markdown(f'<div>{pills}</div>', unsafe_allow_html=True)

                st.divider()

                # ── Strengths + Tips ──
                t1, t2 = st.columns(2)

                with t1:
                    items = "".join([f"<li style='margin-bottom:8px;color:#ccc'>{s}</li>"
                                     for s in result.top_strengths])
                    st.markdown(f"""
                    <div class="section-card">
                        <div class="section-title">💪 Top Strengths</div>
                        <ul style="padding-left:18px">{items}</ul>
                    </div>""", unsafe_allow_html=True)

                with t2:
                    items = "".join([f"<li style='margin-bottom:8px;color:#ccc'>{t}</li>"
                                     for t in result.improvement_tips])
                    st.markdown(f"""
                    <div class="section-card">
                        <div class="section-title">📈 Improvement Tips</div>
                        <ul style="padding-left:18px">{items}</ul>
                    </div>""", unsafe_allow_html=True)

            except ValueError as e:
                st.warning(f"⚠️ Input issue: {e}")
            except RuntimeError as e:
                st.error(f"❌ Analysis failed: {e}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")