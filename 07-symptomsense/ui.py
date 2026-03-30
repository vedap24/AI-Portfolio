import streamlit as st
from app import (
    triage_symptoms,
    EMERGENCY_RESOURCES
)
from models import PatientInput
from prompts import check_red_flags

# ── Page config ──
st.set_page_config(
    page_title="SymptomSense AI",
    page_icon="🏥",
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
            90deg, #34d399, #06b6d4
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

    .emergency-banner {
        background: rgba(239,68,68,0.08);
        border: 1px solid rgba(239,68,68,0.25);
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 20px;
    }

    .emergency-title {
        font-size: 0.75rem;
        font-weight: 700;
        color: #f87171;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .emergency-numbers {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
    }

    .emergency-num {
        font-size: 0.82rem;
        color: #fca5a5;
    }

    .triage-SEEK_EMERGENCY {
        background: rgba(239,68,68,0.08);
        border: 2px solid rgba(239,68,68,0.4);
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 20px;
    }

    .triage-SEE_DOCTOR {
        background: rgba(251,191,36,0.06);
        border: 2px solid rgba(251,191,36,0.35);
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 20px;
    }

    .triage-MONITOR_HOME {
        background: rgba(52,211,153,0.06);
        border: 2px solid rgba(52,211,153,0.3);
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 20px;
    }

    .triage-label-SEEK_EMERGENCY {
        font-size: 1.6rem;
        font-weight: 900;
        color: #f87171;
        margin-bottom: 8px;
    }

    .triage-label-SEE_DOCTOR {
        font-size: 1.6rem;
        font-weight: 900;
        color: #fbbf24;
        margin-bottom: 8px;
    }

    .triage-label-MONITOR_HOME {
        font-size: 1.6rem;
        font-weight: 900;
        color: #34d399;
        margin-bottom: 8px;
    }

    .urgency-bar-wrap {
        background: #1e1e2e;
        border-radius: 8px;
        height: 10px;
        width: 100%;
        margin: 12px 0;
        overflow: hidden;
    }

    .reasoning-box {
        font-size: 0.9rem;
        color: #cbd5e1;
        line-height: 1.8;
        margin: 14px 0;
    }

    .info-block {
        background: #0d1020;
        border: 1px solid #1e1e2e;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }

    .info-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }

    .info-item {
        font-size: 0.85rem;
        color: #94a3b8;
        line-height: 1.7;
        padding: 5px 0;
        border-bottom: 1px solid #1e1e2e;
        display: flex;
        gap: 8px;
    }

    .info-item:last-child {
        border-bottom: none;
    }

    .disclaimer-box {
        background: rgba(100,116,139,0.08);
        border: 1px solid rgba(100,116,139,0.2);
        border-radius: 8px;
        padding: 14px 16px;
        font-size: 0.78rem;
        color: #64748b;
        line-height: 1.7;
        margin-top: 16px;
    }

    .red-flag-pill {
        display: inline-block;
        background: rgba(239,68,68,0.1);
        border: 1px solid rgba(239,68,68,0.25);
        color: #f87171;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        margin: 3px;
    }

    .watch-pill {
        display: inline-block;
        background: rgba(251,191,36,0.08);
        border: 1px solid rgba(251,191,36,0.2);
        color: #fbbf24;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        margin: 3px;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown(
    '<div class="main-title">🏥 SymptomSense AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">'
    'Not a diagnosis tool. A triage tool. '
    'One question: should you go to the ER, '
    'see a doctor, or rest at home?'
    '</div>',
    unsafe_allow_html=True
)

# ── Always-visible emergency numbers ──
numbers_html = "".join([
    f'<span class="emergency-num">'
    f'<strong>{k}:</strong> {v}'
    f'</span>'
    for k, v in EMERGENCY_RESOURCES.items()
])
st.markdown(
    f'<div class="emergency-banner">'
    f'<div class="emergency-title">'
    f'🚨 Emergency Numbers — Always Available'
    f'</div>'
    f'<div class="emergency-numbers">'
    f'{numbers_html}'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True
)

# ── Real world stat ──
st.info(
    "📊 **JAMA Network Open, 2024** — "
    "up to 60% of all ER visits are considered "
    "non-urgent and potentially unnecessary. "
    "Average ER visit cost: $2,400–$2,600. "
    "Average urgent care visit: $185. "
    "**SymptomSense helps you decide before you go.**"
)

st.divider()

# ── Input form ──
st.markdown("### Describe Your Symptoms")

col1, col2 = st.columns([2, 1])

with col1:
    symptoms = st.text_area(
        label="symptoms",
        label_visibility="collapsed",
        height=150,
        placeholder=(
            "Describe your symptoms in detail...\n"
            "Example: Headache on the right side "
            "for 3 hours, mild nausea, "
            "sensitive to light."
        )
    )

with col2:
    age = st.text_input(
        "Age",
        placeholder="e.g. 28 or Child (8 years)"
    )

    duration = st.selectbox(
        "Duration of symptoms",
        options=[
            "Less than 1 hour",
            "1–6 hours",
            "6–24 hours",
            "1–3 days",
            "More than 3 days"
        ]
    )

    severity = st.slider(
        "Severity (1 = mild, 10 = worst ever)",
        min_value=1,
        max_value=10,
        value=5
    )

context = st.text_input(
    "Additional context (optional)",
    placeholder=(
        "e.g. recent travel, known conditions, "
        "medications, pregnancy..."
    )
)

# ── Red flag preview ──
if symptoms:
    flags = check_red_flags(
        symptoms + " " + context
    )
    if flags:
        st.error(
            "🚨 Emergency keywords detected in "
            "your description. If this is a "
            "medical emergency, call 112 or 911 NOW. "
            "Do not wait for the triage result."
        )

st.divider()

# ── Triage button ──
if st.button(
    "🔍 Get Triage Assessment",
    use_container_width=True,
    type="primary",
    disabled=not (symptoms and age)
):
    try:
        patient = PatientInput(
            symptoms=symptoms,
            age=age,
            duration=duration,
            severity=severity,
            context=context
        )
    except Exception as e:
        st.warning(f"⚠️ Input issue: {e}")
        st.stop()

    with st.spinner(
        "Analyzing symptoms..."
    ):
        try:
            result = triage_symptoms(patient)
            st.session_state["result"] = result
        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")
            st.stop()

# ── Display result ──
if "result" in st.session_state:
    result = st.session_state["result"]
    level  = result.triage_level

    st.divider()

    # Triage level display
    level_labels = {
        "SEEK_EMERGENCY": "🚨 Seek Emergency Care",
        "SEE_DOCTOR":     "👨‍⚕️ See a Doctor",
        "MONITOR_HOME":   "🏠 Monitor at Home"
    }

    level_descriptions = {
        "SEEK_EMERGENCY": (
            "Go to the ER or call emergency "
            "services immediately."
        ),
        "SEE_DOCTOR": (
            "Schedule an appointment within "
            "1–3 days. If symptoms worsen, "
            "seek care sooner."
        ),
        "MONITOR_HOME": (
            "Rest at home. Monitor for changes. "
            "Seek care if symptoms worsen "
            "or new symptoms develop."
        )
    }

    urgency_colors = {
        "SEEK_EMERGENCY": "#ef4444",
        "SEE_DOCTOR":     "#fbbf24",
        "MONITOR_HOME":   "#34d399"
    }

    color = urgency_colors.get(level, "#94a3b8")

    st.markdown(
        f'<div class="triage-{level}">',
        unsafe_allow_html=True
    )

    # Left + right layout inside result
    r1, r2 = st.columns([1, 2])

    with r1:
        st.markdown(
            f'<div class="triage-label-{level}">'
            f'{level_labels.get(level, level)}'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<p style="color:#94a3b8;'
            f'font-size:0.85rem">'
            f'{level_descriptions.get(level, "")}'
            f'</p>',
            unsafe_allow_html=True
        )

        # Urgency score bar
        st.markdown(
            f'<div style="font-size:0.72rem;'
            f'color:#64748b;margin-top:12px">'
            f'URGENCY SCORE: '
            f'{result.urgency_score}/10</div>',
            unsafe_allow_html=True
        )
        pct = result.urgency_score * 10
        st.markdown(
            f'<div class="urgency-bar-wrap">'
            f'<div style="height:100%;'
            f'width:{pct}%;'
            f'background:{color};'
            f'border-radius:8px"></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Red flags present
        if result.red_flags_present:
            st.markdown(
                '<div style="font-size:0.72rem;'
                'color:#64748b;margin-top:12px;'
                'margin-bottom:6px">'
                'RED FLAGS DETECTED'
                '</div>',
                unsafe_allow_html=True
            )
            pills = "".join([
                f'<span class="red-flag-pill">'
                f'{f}</span>'
                for f in result.red_flags_present
            ])
            st.markdown(
                f'<div>{pills}</div>',
                unsafe_allow_html=True
            )

    with r2:
        # Reasoning
        st.markdown(
            f'<div class="reasoning-box">'
            f'{result.reasoning}'
            f'</div>',
            unsafe_allow_html=True
        )

        # Three info blocks
        b1, b2 = st.columns(2)

        with b1:
            # Immediate steps
            steps_html = "".join([
                f'<div class="info-item">'
                f'<span style="color:{color}">→</span>'
                f'{step}</div>'
                for step in result.immediate_steps
            ])
            st.markdown(
                f'<div class="info-block">'
                f'<div class="info-label" '
                f'style="color:{color}">'
                f'Immediate Steps</div>'
                f'{steps_html}'
                f'</div>',
                unsafe_allow_html=True
            )

            # Watch for
            if result.red_flags_to_watch:
                watch_pills = "".join([
                    f'<span class="watch-pill">'
                    f'{w}</span>'
                    for w in result.red_flags_to_watch
                ])
                st.markdown(
                    f'<div class="info-block">'
                    f'<div class="info-label" '
                    f'style="color:#fbbf24">'
                    f'Watch For</div>'
                    f'<div>{watch_pills}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        with b2:
            # What to tell doctor
            if result.what_to_tell_doctor:
                doctor_html = "".join([
                    f'<div class="info-item">'
                    f'<span style="color:#818cf8">'
                    f'•</span>{d}</div>'
                    for d in result.what_to_tell_doctor
                ])
                st.markdown(
                    f'<div class="info-block">'
                    f'<div class="info-label" '
                    f'style="color:#818cf8">'
                    f'Tell Your Doctor</div>'
                    f'{doctor_html}'
                    f'</div>',
                    unsafe_allow_html=True
                )

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Disclaimer ──
    st.markdown(
        f'<div class="disclaimer-box">'
        f'⚠️ {result.disclaimer}'
        f'</div>',
        unsafe_allow_html=True
    )