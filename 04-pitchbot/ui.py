import streamlit as st
from app import generate_pitch

# ── Page config ──
st.set_page_config(
    page_title="PitchBot AI",
    page_icon="📧",
    layout="wide"
)

# ── Custom CSS ──
st.markdown("""
<style>
    .stApp { background-color: #080812; }

    .main-title {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #34d399, #059669);
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

    .step-badge {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #34d399;
        margin-bottom: 6px;
    }

    .email-card {
        background: #0f0f1a;
        border: 1px solid #1e1e2e;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 16px;
        position: relative;
    }

    .email-card-short {
        border-top: 3px solid #34d399;
    }

    .email-card-medium {
        border-top: 3px solid #3b82f6;
    }

    .email-card-detailed {
        border-top: 3px solid #8b5cf6;
    }

    .variant-badge {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        padding: 3px 10px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 10px;
    }

    .badge-short {
        background: rgba(52,211,153,0.1);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.25);
    }

    .badge-medium {
        background: rgba(59,130,246,0.1);
        color: #60a5fa;
        border: 1px solid rgba(59,130,246,0.25);
    }

    .badge-detailed {
        background: rgba(139,92,246,0.1);
        color: #a78bfa;
        border: 1px solid rgba(139,92,246,0.25);
    }

    .subject-line {
        font-size: 1rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 4px;
    }

    .best-for {
        font-size: 0.75rem;
        color: #64748b;
        margin-bottom: 14px;
        font-style: italic;
    }

    .email-body {
        background: #080812;
        border: 1px solid #1e1e2e;
        border-radius: 8px;
        padding: 16px;
        font-size: 0.88rem;
        color: #cbd5e1;
        line-height: 1.85;
        white-space: pre-wrap;
        margin-bottom: 12px;
    }

    .word-count {
        font-size: 0.72rem;
        color: #475569;
        text-align: right;
    }

    .angle-box {
        background: rgba(52,211,153,0.05);
        border: 1px solid rgba(52,211,153,0.15);
        border-left: 3px solid #34d399;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        font-size: 0.85rem;
        color: #6ee7b7;
        line-height: 1.7;
        margin-bottom: 14px;
    }

    .personalization-pill {
        display: inline-block;
        background: rgba(59,130,246,0.08);
        border: 1px solid rgba(59,130,246,0.2);
        color: #60a5fa;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        margin: 3px;
    }

    .followup-box {
        background: rgba(251,191,36,0.05);
        border: 1px solid rgba(251,191,36,0.15);
        border-radius: 8px;
        padding: 14px 16px;
        font-size: 0.85rem;
        color: #fcd34d;
        line-height: 1.7;
    }

    .recipient-card {
        background: #0f0f1a;
        border: 1px solid #1e1e2e;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 16px;
    }

    .stat-row {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 20px;
    }

    .stat-chip {
        background: #0f0f1a;
        border: 1px solid #1e1e2e;
        border-radius: 8px;
        padding: 10px 16px;
        text-align: center;
        min-width: 100px;
    }

    .stat-chip-num {
        font-size: 1.4rem;
        font-weight: 800;
        color: #34d399;
    }

    .stat-chip-label {
        font-size: 0.65rem;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ──
st.markdown(
    '<div class="main-title">📧 PitchBot AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">'
    'Paste a LinkedIn profile → get 3 personalized cold emails '
    'that actually reference real details. '
    'Powered by Gemini 2.0 Flash.</div>',
    unsafe_allow_html=True
)

# ── Real world stat ──
st.info(
    "📊 **Instantly Cold Email Benchmark Report, "
    "January 2026** — average cold email reply rate "
    "is just 3.43%. Campaigns with deep personalization "
    "see up to 18% reply rates. "
    "Only 5% of senders personalize every message. "
    "**PitchBot puts you in that 5%.**"
)

st.divider()

# ── Input section ──
st.markdown("### 01 — Who are you reaching out to?")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**📋 Paste LinkedIn Profile Text**")
    st.caption(
        "Open their LinkedIn → select all text "
        "on the page → paste here"
    )
    profile_text = st.text_area(
        label="profile",
        label_visibility="collapsed",
        height=250,
        placeholder=(
            "Paste the person's LinkedIn profile text here...\n\n"
            "Include: name, role, company, about section, "
            "recent experience, skills."
        )
    )

with col2:
    st.markdown("**🌐 Company Website (Optional)**")
    st.caption(
        "Adds extra context about what they do"
    )
    company_url = st.text_input(
        label="url",
        label_visibility="collapsed",
        placeholder="https://theircompany.com"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**🎯 Your Outreach Purpose**")
    st.caption(
        "Be specific — the more detail, "
        "the better the personalization"
    )
    your_purpose = st.text_area(
        label="purpose",
        label_visibility="collapsed",
        height=120,
        placeholder=(
            "Example: I'm an AI engineer who built a code "
            "review automation tool. I want to connect with "
            "engineering leaders to get feedback and "
            "explore if their team has this problem."
        )
    )

st.divider()

# ── Tone selector ──
st.markdown("### 02 — Pick your tone")
tone_col = st.columns(3)
with tone_col[0]:
    tone_professional = st.checkbox(
        "💼 Professional",
        value=True
    )
with tone_col[1]:
    tone_casual = st.checkbox("😊 Casual")
with tone_col[2]:
    tone_peer = st.checkbox("🤝 Peer-to-Peer")

# Determine selected tone
if tone_casual:
    selected_tone = "casual"
elif tone_peer:
    selected_tone = "peer-to-peer"
else:
    selected_tone = "professional"

st.divider()

# ── Generate button ──
if st.button(
    "🚀 Generate Personalized Emails",
    use_container_width=True,
    type="primary",
    disabled=not (profile_text and your_purpose)
):
    with st.spinner(
        "Step 1/3 — Extracting profile insights... "
        "Step 2/3 — Finding connection angles... "
        "Step 3/3 — Writing email variations..."
    ):
        try:
            result = generate_pitch(
                profile_text=profile_text,
                your_purpose=your_purpose,
                company_url=company_url
            )
            st.session_state["pitch_result"] = result

        except ValueError as e:
            st.warning(f"⚠️ Input issue: {e}")
            st.stop()
        except Exception as e:
            st.error(f"❌ Generation failed: {e}")
            st.stop()

# ── Display results ──
if "pitch_result" in st.session_state:
    result = st.session_state["pitch_result"]

    st.success("✅ Emails generated!")
    st.divider()

    # ── Recipient + stats row ──
    left, right = st.columns([1, 2])

    with left:
        st.markdown(f"""
        <div class="recipient-card">
            <div style="font-size:0.7rem;color:#64748b;
                 letter-spacing:2px;text-transform:uppercase;
                 margin-bottom:8px">Recipient</div>
            <div style="font-size:1.1rem;font-weight:700;
                 color:#e2e8f0;margin-bottom:4px">
                {result.recipient_name}
            </div>
            <div style="font-size:0.85rem;color:#94a3b8;
                 margin-bottom:2px">
                {result.recipient_role}
            </div>
            <div style="font-size:0.85rem;color:#64748b">
                {result.recipient_company}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Primary angle
        st.markdown("**🎯 Primary Connection Angle**")
        st.markdown(
            f'<div class="angle-box">'
            f'{result.primary_angle}'
            f'</div>',
            unsafe_allow_html=True
        )

        # Personalization elements
        if result.personalization_elements:
            st.markdown("**🔍 Personalization Used**")
            pills = " ".join([
                f'<span class="personalization-pill">{p}</span>'
                for p in result.personalization_elements
            ])
            st.markdown(
                f'<div style="margin-bottom:16px">{pills}</div>',
                unsafe_allow_html=True
            )

        # Follow-up tip
        st.markdown("**📅 Follow-up Strategy**")
        st.markdown(
            f'<div class="followup-box">'
            f'💡 {result.follow_up_tip}'
            f'</div>',
            unsafe_allow_html=True
        )

    with right:
        st.markdown("### 3 Email Variants")
        st.caption(
            "Each variant is independently crafted — "
            "not just a shorter/longer version of the same email."
        )

        variant_colors = {
            "short":    ("badge-short",    "email-card-short"),
            "medium":   ("badge-medium",   "email-card-medium"),
            "detailed": ("badge-detailed", "email-card-detailed"),
        }

        for email in result.emails:
            badge_cls, card_cls = variant_colors.get(
                email.variant,
                ("badge-short", "email-card-short")
            )

            st.markdown(
                f'<div class="email-card {card_cls}">',
                unsafe_allow_html=True
            )

            # Variant badge + subject
            st.markdown(
                f'<span class="variant-badge {badge_cls}">'
                f'{email.variant.upper()}'
                f'</span>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="subject-line">'
                f'✉️ {email.subject}'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="best-for">'
                f'Best for: {email.best_for}'
                f'</div>',
                unsafe_allow_html=True
            )

            # Email body
            st.markdown(
                f'<div class="email-body">'
                f'{email.body}'
                f'</div>',
                unsafe_allow_html=True
            )

            # Word count + copy button
            # Word count
            st.markdown(
                f'<div class="word-count">'
                f'{email.word_count} words</div>',
                unsafe_allow_html=True
            )

            # Copy block — full width, clearly labeled
            with st.expander("📋 Copy this email"):
                st.code(
                    f"Subject: {email.subject}"
                    f"\n\n{email.body}",
                    language=None
                )

            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)