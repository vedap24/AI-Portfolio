import streamlit as st
import tempfile
import os
from app import transcribe_audio, extract_meeting_brief
# Add Path import at top
from pathlib import Path

# ── Page config ──
st.set_page_config(
    page_title="MeetingMind AI",
    page_icon="🎙️",
    layout="wide"
)

# ── Custom CSS ──
st.markdown("""
<style>
    .stApp { background-color: #0a0a0f; }

    .main-title {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #818cf8, #38bdf8);
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

    .stat-box {
        background: #13131e;
        border: 1px solid #1e1e2e;
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
    }

    .stat-num {
        font-size: 1.8rem;
        font-weight: 900;
        color: #818cf8;
    }

    .stat-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 2px;
    }

    .section-card {
        background: #13131e;
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

    .action-row {
        background: #0d0d18;
        border: 1px solid #1e1e2e;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }

    .task-text {
        font-size: 0.9rem;
        color: #e2e8f0;
        font-weight: 600;
    }

    .task-meta {
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 4px;
    }

    .topic-pill {
        display: inline-block;
        background: rgba(129,140,248,0.1);
        border: 1px solid rgba(129,140,248,0.2);
        color: #818cf8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        margin: 3px;
    }

    .sentiment-productive {
        color: #34d399;
        background: rgba(52,211,153,0.1);
        border: 1px solid rgba(52,211,153,0.2);
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
    }

    .sentiment-unresolved {
        color: #f87171;
        background: rgba(248,113,113,0.1);
        border: 1px solid rgba(248,113,113,0.2);
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
    }

    .sentiment-mixed {
        color: #fbbf24;
        background: rgba(251,191,36,0.1);
        border: 1px solid rgba(251,191,36,0.2);
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
    }

    .transcript-box {
        background: #0d0d18;
        border: 1px solid #1e1e2e;
        border-radius: 8px;
        padding: 16px;
        font-size: 0.85rem;
        color: #94a3b8;
        line-height: 1.8;
        max-height: 200px;
        overflow-y: auto;
    }

    .outcome-box {
        background: rgba(129,140,248,0.06);
        border-left: 3px solid #818cf8;
        border-radius: 0 8px 8px 0;
        padding: 14px 18px;
        font-size: 0.95rem;
        color: #c7d2fe;
        font-style: italic;
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ──
st.markdown('<div class="main-title">🎙️ MeetingMind AI</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Upload a meeting recording → get a structured brief '
    'in seconds. Powered by Whisper + Gemini 2.5 Flash.</div>',
    unsafe_allow_html=True
)

# ── Real world stat ──
st.info(
    "📊 **Atlassian found workers spend 31 hours/month in unproductive meetings."
    " Microsoft reports 64% of workers don't have enough time for actual work "
    "because of meetings.** MeetingMind fixes the follow-up problem."
)

st.divider()

# ── File uploader ──
st.markdown("**📁 Upload Meeting Recording**")
audio_file = st.file_uploader(
    label="audio",
    label_visibility="collapsed",
    type=["mp3", "wav", "m4a", "ogg"],
    help="Supports MP3, WAV, M4A, OGG. Max 100MB."
)

if audio_file:
    st.audio(audio_file)
    st.caption(f"File: {audio_file.name} · "
               f"Size: {audio_file.size / (1024*1024):.1f}MB")

st.divider()

# ── Analyze button ──
if st.button("🚀 Generate Meeting Brief",
             use_container_width=True,
             type="primary",
             disabled=not audio_file):

    with st.spinner("Step 1/2 — Transcribing audio with Whisper..."):
        try:
            # Save uploaded file to temp location
            suffix = Path(audio_file.name).suffix \
                if hasattr(audio_file, 'name') else '.mp3'

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=suffix
            ) as tmp:
                tmp.write(audio_file.read())
                tmp_path = tmp.name

            transcription = transcribe_audio(tmp_path)
            os.unlink(tmp_path)  # clean up temp file

        except Exception as e:
            st.error(f"❌ Transcription failed: {e}")
            st.stop()

    with st.spinner("Step 2/2 — Extracting brief with Gemini..."):
        try:
            brief = extract_meeting_brief(transcription["transcript"])
        except Exception as e:
            st.error(f"❌ Extraction failed: {e}")
            st.stop()

    # ── Results ──
    st.success("✅ Meeting brief generated!")
    st.divider()

    # Stats row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="stat-box">
            <div class="stat-num">{len(brief.decisions)}</div>
            <div class="stat-label">Decisions</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="stat-box">
            <div class="stat-num">{len(brief.action_items)}</div>
            <div class="stat-label">Action Items</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="stat-box">
            <div class="stat-num">{len(brief.follow_up_questions)}</div>
            <div class="stat-label">Follow-ups</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        sentiment_class = f"sentiment-{brief.meeting_sentiment.lower()}"
        st.markdown(f"""<div class="stat-box">
            <div class="stat-num" style="font-size:1.2rem;padding-top:6px">
                <span class="{sentiment_class}">{brief.meeting_sentiment}</span>
            </div>
            <div class="stat-label">Sentiment</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # One-line outcome
    st.markdown(
        f'<div class="outcome-box">🎯 {brief.one_line_outcome}</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Main content columns
    left, right = st.columns(2)

    with left:
        # Summary
        st.markdown(f"""<div class="section-card">
            <div class="section-label" style="color:#818cf8">
                📝 Summary
            </div>
            <p style="color:#cbd5e1;font-size:0.9rem;
                      line-height:1.75;margin:0">
                {brief.summary}
            </p>
        </div>""", unsafe_allow_html=True)

        # Decisions
        if brief.decisions:
            decisions_html = "".join([
                f'<li style="color:#cbd5e1;font-size:0.88rem;'
                f'padding:6px 0;border-bottom:1px solid #1e1e2e">{d}</li>'
                for d in brief.decisions
            ])
            st.markdown(f"""<div class="section-card">
                <div class="section-label" style="color:#34d399">
                    ✅ Decisions Made
                </div>
                <ul style="padding-left:18px;margin:0">
                    {decisions_html}
                </ul>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="section-card">
                <div class="section-label" style="color:#34d399">
                    ✅ Decisions Made
                </div>
                <p style="color:#64748b;font-size:0.85rem">
                    No explicit decisions recorded.
                </p>
            </div>""", unsafe_allow_html=True)

        # Key topics
        topics_html = "".join([
            f'<span class="topic-pill">{t}</span>'
            for t in brief.key_topics
        ])
        st.markdown(f"""<div class="section-card">
            <div class="section-label" style="color:#38bdf8">
                🏷️ Key Topics
            </div>
            <div>{topics_html}</div>
        </div>""", unsafe_allow_html=True)

    with right:
        # Action items
        if brief.action_items:
            action_html = "".join([
                f"""<div class="action-row">
                    <div class="task-text">→ {item.task}</div>
                    <div class="task-meta">
                        👤 {item.owner} &nbsp;·&nbsp;
                        ⏰ {item.deadline}
                    </div>
                </div>"""
                for item in brief.action_items
            ])
            st.markdown(f"""<div class="section-card">
                <div class="section-label" style="color:#fbbf24">
                    ⚡ Action Items
                </div>
                {action_html}
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="section-card">
                <div class="section-label" style="color:#fbbf24">
                    ⚡ Action Items
                </div>
                <p style="color:#64748b;font-size:0.85rem">
                    No action items identified.
                </p>
            </div>""", unsafe_allow_html=True)

        # Follow-up questions
        if brief.follow_up_questions:
            followup_html = "".join([
                f'<li style="color:#cbd5e1;font-size:0.88rem;'
                f'padding:6px 0;border-bottom:1px solid #1e1e2e">{q}</li>'
                for q in brief.follow_up_questions
            ])
            st.markdown(f"""<div class="section-card">
                <div class="section-label" style="color:#f87171">
                    ❓ Follow-up Questions
                </div>
                <ul style="padding-left:18px;margin:0">
                    {followup_html}
                </ul>
            </div>""", unsafe_allow_html=True)

        # Raw transcript (collapsed)
        with st.expander("📄 View Raw Transcript"):
            st.markdown(
                f'<div class="transcript-box">'
                f'{transcription["transcript"]}'
                f'</div>',
                unsafe_allow_html=True
            )
            st.caption(
                f"Language: {transcription['language']} · "
                f"Processed in {transcription['duration_seconds']}s"
            )

