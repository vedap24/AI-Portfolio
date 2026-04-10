import streamlit as st
import json
from app import (
    process_field_report,
    process_text_report,
    REPORT_LABELS
)
from prompts import REPORT_LABELS

# ── Page config ──
st.set_page_config(
    page_title="FieldReport AI",
    page_icon="🎙️",
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
            90deg, #f97316, #eab308
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

    .transcript-box {
        background: #0d1117;
        border: 1px solid #1e2a3a;
        border-left: 3px solid #f97316;
        border-radius: 0 10px 10px 0;
        padding: 16px 20px;
        font-size: 0.88rem;
        color: #94a3b8;
        line-height: 1.85;
        font-style: italic;
        margin-bottom: 20px;
    }

    .report-section {
        background: #0d1117;
        border: 1px solid #1e2a3a;
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

    .field-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #1e2a3a;
        font-size: 0.85rem;
    }

    .field-row:last-child {
        border-bottom: none;
    }

    .field-label {
        color: #475569;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        min-width: 160px;
    }

    .field-value {
        color: #e2e8f0;
        text-align: right;
        flex: 1;
    }

    .severity-CRITICAL {
        background: rgba(239,68,68,0.12);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.25);
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
        margin-right: 6px;
    }

    .severity-HIGH {
        background: rgba(249,115,22,0.12);
        color: #fb923c;
        border: 1px solid rgba(249,115,22,0.25);
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
        margin-right: 6px;
    }

    .severity-MEDIUM {
        background: rgba(234,179,8,0.1);
        color: #facc15;
        border: 1px solid rgba(234,179,8,0.2);
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
        margin-right: 6px;
    }

    .severity-LOW {
        background: rgba(100,116,139,0.1);
        color: #94a3b8;
        border: 1px solid rgba(100,116,139,0.2);
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
        margin-right: 6px;
    }

    .status-PASS {
        color: #34d399;
        font-weight: 700;
    }

    .status-FAIL {
        color: #f87171;
        font-weight: 700;
    }

    .status-CONDITIONAL {
        color: #fbbf24;
        font-weight: 700;
    }

    .status-POSITIVE {
        color: #34d399;
        font-weight: 700;
    }

    .status-NEGATIVE {
        color: #f87171;
        font-weight: 700;
    }

    .status-NEUTRAL {
        color: #94a3b8;
        font-weight: 700;
    }

    .list-item {
        font-size: 0.85rem;
        color: #94a3b8;
        padding: 6px 0;
        border-bottom: 1px solid #1e2a3a;
        line-height: 1.6;
    }

    .list-item:last-child {
        border-bottom: none;
    }

    .issue-card {
        background: #060a12;
        border: 1px solid #1e2a3a;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
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

    .demo-text {
        background: #060a12;
        border: 1px solid #1e2a3a;
        border-radius: 8px;
        padding: 14px 16px;
        font-size: 0.82rem;
        color: #64748b;
        font-style: italic;
        line-height: 1.75;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ──
if "result" not in st.session_state:
    st.session_state.result = None

# ── Header ──
st.markdown(
    '<div class="main-title">'
    '🎙️ FieldReport AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">'
    'Speak your field report → '
    'get structured data instantly. '
    'Site inspections, sales visits, '
    'delivery logs — all extracted automatically.'
    '</div>',
    unsafe_allow_html=True
)

st.info(
    "📊 **Voice AI Research, 2026** — "
    "Production voice agent deployments grew "
    "340% year-over-year. Companies report "
    "3-year ROI between 331% and 391%. "
    "**FieldReport AI eliminates manual "
    "data entry for field workers.**"
)

st.divider()

# ── Input section ──
st.markdown("### 📋 Select Report Type")

report_type = st.selectbox(
    label="report_type",
    label_visibility="collapsed",
    options=list(REPORT_LABELS.keys()),
    format_func=lambda x: REPORT_LABELS[x]
)

st.markdown("### 🎙️ Input Method")

tab1, tab2 = st.tabs([
    "📁 Upload Audio File",
    "⌨️ Type Report (Demo)"
])

with tab1:
    st.markdown(
        "Upload an audio recording of your "
        "field report. Supported formats: "
        "MP3, WAV, M4A, OGG, FLAC"
    )

    audio_file = st.file_uploader(
        label="audio",
        label_visibility="collapsed",
        type=["mp3", "wav", "m4a",
              "ogg", "flac"]
    )

    if audio_file:
        st.audio(audio_file)

        if st.button(
            "🚀 Process Audio Report",
            use_container_width=True,
            type="primary",
            key="process_audio"
        ):
            ext = "." + audio_file.name\
                .rsplit(".", 1)[-1].lower()

            with st.spinner(
                "🎙️ Transcribing audio..."
            ):
                try:
                    result = process_field_report(
                        audio_file.read(),
                        report_type,
                        ext
                    )
                    st.session_state.result = \
                        result
                    st.rerun()
                except ValueError as e:
                    st.warning(f"⚠️ {e}")
                except Exception as e:
                    st.error(f"❌ {e}")

with tab2:
    # Demo text examples per report type
    demo_texts = {
        "site_inspection": (
            "Site inspection at 450 Industrial "
            "Boulevard, Warehouse C. This is "
            "Sarah Chen reporting. Found a major "
            "structural crack in the east wall, "
            "critical severity. The fire suppression "
            "system on level 2 is non-functional, "
            "high severity issue. Roof drainage "
            "blocked causing water pooling, medium "
            "severity. Action items: emergency wall "
            "repair within 24 hours urgent priority, "
            "fix fire suppression within 48 hours "
            "high priority. Safety rating is FAIL. "
            "Follow-up inspection required in 3 days. "
            "Overall condition is poor."
        ),
        "sales_visit": (
            "Just finished a meeting with TechFlow "
            "Inc. Met with David Park, their CTO. "
            "We discussed their current data pipeline "
            "bottlenecks and integration challenges. "
            "They are spending 20 hours a week on "
            "manual data processing. Main pain point "
            "is the lack of real-time visibility. "
            "They raised concerns about data security "
            "and implementation timeline. Next steps: "
            "I will send a technical proposal by "
            "Thursday, they will review with their "
            "board by end of month. The deal looks "
            "very promising, estimated value around "
            "150k annually. Follow up scheduled "
            "for next Monday."
        ),
        "delivery_log": (
            "Driver James Wilson, truck TRK-089. "
            "Completed downtown route today. "
            "Stop 1 at City Medical Center, "
            "delivered successfully. Stop 2 at "
            "250 Commerce Street, delivered. "
            "Stop 3 at Riverside Apartments, "
            "failed, customer not available. "
            "Stop 4 at Harbor View Office, "
            "delivered. Stop 5 at 88 Oak Lane, "
            "partial delivery, package damaged. "
            "Had a GPS malfunction for 2 hours "
            "causing route delays, medium severity. "
            "Started 7:30am, finished 4:45pm. "
            "Total mileage 112 miles."
        )
    }

    st.markdown(
        f'<div class="demo-text">'
        f'💡 Demo text for '
        f'{REPORT_LABELS[report_type]}:'
        f'<br><br>'
        f'{demo_texts[report_type]}'
        f'</div>',
        unsafe_allow_html=True
    )

    text_input = st.text_area(
        label="text_report",
        label_visibility="collapsed",
        height=160,
        value=demo_texts[report_type],
        placeholder="Type or paste your "
                    "field report here..."
    )

    if st.button(
        "🚀 Process Text Report",
        use_container_width=True,
        type="primary",
        key="process_text"
    ):
        with st.spinner(
            "🤖 Extracting structured data..."
        ):
            try:
                result = process_text_report(
                    text_input,
                    report_type
                )
                st.session_state.result = result
                st.rerun()
            except ValueError as e:
                st.warning(f"⚠️ {e}")
            except Exception as e:
                st.error(f"❌ {e}")

st.divider()

# ── Display result ──
if st.session_state.result:
    result = st.session_state.result
    report = result.report
    rtype  = result.report_type

    st.success(
        f"✅ {REPORT_LABELS[rtype]} processed "
        f"in {result.processing_time_seconds}s"
    )

    # ── Meta stats ──
    m1, m2, m3, m4 = st.columns(4)
    meta = [
        (m1, result.word_count,
         "#f97316", "Words Spoken"),
        (m2, f"{result.audio_duration_seconds:.1f}s"
         if result.audio_duration_seconds > 0
         else "Text",
         "#eab308", "Audio Duration"),
        (m3, f"{result.transcript_confidence:.0%}",
         "#34d399", "Confidence"),
        (m4, result.processing_time_seconds,
         "#818cf8", "Process Time (s)")
    ]
    for col, val, color, label in meta:
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

    # ── Transcript ──
    st.markdown("**🎙️ Transcript**")
    st.markdown(
        f'<div class="transcript-box">'
        f'"{result.transcript}"'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Report display ──
    st.markdown(
        f"**📋 Extracted Report — "
        f"{REPORT_LABELS[rtype]}**"
    )

    left, right = st.columns([1, 1])

    # ════════════════════════════════════
    # SITE INSPECTION DISPLAY
    # ════════════════════════════════════
    if rtype == "site_inspection":

        with left:
            # Core fields
            safety = report.get(
                "safety_rating", "N/A"
            )
            safety_cls = f"status-{safety}"
            condition  = report.get(
                "overall_condition", "N/A"
            )

            st.markdown(
                f'<div class="report-section">'
                f'<div class="section-label" '
                f'style="color:#f97316">'
                f'Core Details</div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Location</span>'
                f'<span class="field-value">'
                f'{report.get("location","N/A")}'
                f'</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Inspector</span>'
                f'<span class="field-value">'
                f'{report.get("inspector_name","N/A")}'
                f'</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Date</span>'
                f'<span class="field-value">'
                f'{report.get("inspection_date","N/A")}'
                f'</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Safety Rating</span>'
                f'<span class="field-value '
                f'{safety_cls}">'
                f'{safety}</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Condition</span>'
                f'<span class="field-value">'
                f'{condition}</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Follow-up Required</span>'
                f'<span class="field-value">'
                f'{"Yes" if report.get("follow_up_required") else "No"}'
                f'</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )

            # Findings
            if report.get("findings"):
                st.markdown(
                    '<div class="report-section">'
                    '<div class="section-label" '
                    'style="color:#34d399">'
                    'Findings</div>',
                    unsafe_allow_html=True
                )
                for f in report["findings"]:
                    st.markdown(
                        f'<div class="list-item">'
                        f'→ {f}</div>',
                        unsafe_allow_html=True
                    )
                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

        with right:
            # Issues
            if report.get("issues"):
                st.markdown(
                    '<div class="section-label" '
                    'style="color:#f87171">'
                    '⚠️ Issues Found</div>',
                    unsafe_allow_html=True
                )
                for issue in report["issues"]:
                    sev = issue.get(
                        "severity", "MEDIUM"
                    )
                    st.markdown(
                        f'<div class="issue-card">'
                        f'<span class="severity-{sev}">'
                        f'{sev}</span>'
                        f'<strong style="color:#e2e8f0">'
                        f'{issue.get("description","")}'
                        f'</strong>'
                        f'<div style="font-size:0.78rem;'
                        f'color:#475569;margin-top:4px">'
                        f'📍 '
                        f'{issue.get("location","")}'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            # Action items
            if report.get("action_items"):
                st.markdown(
                    '<div class="section-label" '
                    'style="color:#818cf8;'
                    'margin-top:16px">'
                    '📋 Action Items</div>',
                    unsafe_allow_html=True
                )
                for action in \
                        report["action_items"]:
                    pri = action.get(
                        "priority", "MEDIUM"
                    )
                    st.markdown(
                        f'<div class="issue-card">'
                        f'<span class="severity-'
                        f'{pri}">{pri}</span>'
                        f'<strong style="color:#e2e8f0">'
                        f'{action.get("task","")}'
                        f'</strong>'
                        f'<div style="font-size:0.78rem;'
                        f'color:#475569;margin-top:4px">'
                        f'⏰ '
                        f'{action.get("deadline","")}'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

    # ════════════════════════════════════
    # SALES VISIT DISPLAY
    # ════════════════════════════════════
    elif rtype == "sales_visit":

        with left:
            sentiment = report.get(
                "sentiment", "NEUTRAL"
            )
            sent_cls = f"status-{sentiment}"

            st.markdown(
                f'<div class="report-section">'
                f'<div class="section-label" '
                f'style="color:#f97316">'
                f'Visit Details</div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Client</span>'
                f'<span class="field-value">'
                f'{report.get("client_name","N/A")}'
                f'</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Contact</span>'
                f'<span class="field-value">'
                f'{report.get("contact_person","N/A")}'
                f'</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Role</span>'
                f'<span class="field-value">'
                f'{report.get("contact_role","N/A")}'
                f'</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Deal Stage</span>'
                f'<span class="field-value">'
                f'{report.get("deal_stage","N/A")}'
                f'</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Deal Value</span>'
                f'<span class="field-value">'
                f'{report.get("deal_value","N/A")}'
                f'</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Sentiment</span>'
                f'<span class="field-value '
                f'{sent_cls}">'
                f'{sentiment}</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Follow-up Date</span>'
                f'<span class="field-value">'
                f'{report.get("follow_up_date","N/A")}'
                f'</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )

            # Pain points
            if report.get("pain_points"):
                st.markdown(
                    '<div class="report-section">'
                    '<div class="section-label" '
                    'style="color:#f87171">'
                    '😤 Pain Points</div>',
                    unsafe_allow_html=True
                )
                for pp in report["pain_points"]:
                    st.markdown(
                        f'<div class="list-item">'
                        f'→ {pp}</div>',
                        unsafe_allow_html=True
                    )
                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )

        with right:
            # Discussion points
            if report.get("discussion_points"):
                st.markdown(
                    '<div class="section-label" '
                    'style="color:#34d399">'
                    '💬 Discussion Points</div>',
                    unsafe_allow_html=True
                )
                for dp in \
                        report["discussion_points"]:
                    st.markdown(
                        f'<div class="list-item">'
                        f'→ {dp}</div>',
                        unsafe_allow_html=True
                    )

            # Next steps
            if report.get("next_steps"):
                st.markdown(
                    '<div class="section-label" '
                    'style="color:#818cf8;'
                    'margin-top:16px">'
                    '📋 Next Steps</div>',
                    unsafe_allow_html=True
                )
                for step in report["next_steps"]:
                    st.markdown(
                        f'<div class="issue-card">'
                        f'<strong style="color:#e2e8f0">'
                        f'{step.get("action","")}'
                        f'</strong>'
                        f'<div style="font-size:0.78rem;'
                        f'color:#475569;margin-top:4px">'
                        f'👤 {step.get("owner","")} · '
                        f'⏰ {step.get("deadline","")}'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            # Objections
            if report.get("objections"):
                st.markdown(
                    '<div class="section-label" '
                    'style="color:#fbbf24;'
                    'margin-top:16px">'
                    '🚧 Objections</div>',
                    unsafe_allow_html=True
                )
                for obj in report["objections"]:
                    st.markdown(
                        f'<div class="list-item">'
                        f'⚠️ {obj}</div>',
                        unsafe_allow_html=True
                    )

    # ════════════════════════════════════
    # DELIVERY LOG DISPLAY
    # ════════════════════════════════════
    elif rtype == "delivery_log":

        with left:
            success = report.get(
                "successful_deliveries", 0
            )
            total   = report.get(
                "total_stops", 0
            )
            failed  = report.get(
                "failed_deliveries", 0
            )

            # Delivery stats
            d1, d2, d3 = st.columns(3)
            for col, num, color, label in [
                (d1, total, "#f97316", "Total"),
                (d2, success, "#34d399", "Success"),
                (d3, failed, "#f87171", "Failed")
            ]:
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

            st.markdown(
                "<br>", unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="report-section">'
                f'<div class="section-label" '
                f'style="color:#f97316">'
                f'Driver Details</div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Driver</span>'
                f'<span class="field-value">'
                f'{report.get("driver_name","N/A")}'
                f'</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Vehicle</span>'
                f'<span class="field-value">'
                f'{report.get("vehicle_id","N/A")}'
                f'</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Route</span>'
                f'<span class="field-value">'
                f'{report.get("route","N/A")}'
                f'</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Start Time</span>'
                f'<span class="field-value">'
                f'{report.get("start_time","N/A")}'
                f'</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'End Time</span>'
                f'<span class="field-value">'
                f'{report.get("end_time","N/A")}'
                f'</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Mileage</span>'
                f'<span class="field-value">'
                f'{report.get("mileage","N/A")}'
                f'</span></div>'
                f'<div class="field-row">'
                f'<span class="field-label">'
                f'Completion Rate</span>'
                f'<span class="field-value" '
                f'style="color:#34d399;'
                f'font-weight:700">'
                f'{report.get("completion_rate","N/A")}'
                f'</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )

        with right:
            # Stops
            if report.get("stops"):
                st.markdown(
                    '<div class="section-label" '
                    'style="color:#34d399">'
                    '📍 Delivery Stops</div>',
                    unsafe_allow_html=True
                )
                for stop in report["stops"]:
                    status = stop.get(
                        "status", "Delivered"
                    )
                    status_colors = {
                        "Delivered": "#34d399",
                        "Failed":    "#f87171",
                        "Partial":   "#fbbf24"
                    }
                    sc = status_colors.get(
                        status, "#94a3b8"
                    )
                    notes = stop.get("notes", "")
                    st.markdown(
                        f'<div class="issue-card">'
                        f'<div style="display:flex;'
                        f'justify-content:space-between">'
                        f'<span style="color:#e2e8f0;'
                        f'font-weight:600">'
                        f'Stop {stop.get("stop_number","")} '
                        f'— {stop.get("location","")}'
                        f'</span>'
                        f'<span style="color:{sc};'
                        f'font-size:0.75rem;'
                        f'font-weight:700">'
                        f'{status}</span>'
                        f'</div>'
                        + (
                            f'<div style="font-size:'
                            f'0.75rem;color:#475569;'
                            f'margin-top:4px">'
                            f'{notes}</div>'
                            if notes else ""
                        ) +
                        f'</div>',
                        unsafe_allow_html=True
                    )

            # Issues
            if report.get("issues"):
                st.markdown(
                    '<div class="section-label" '
                    'style="color:#f87171;'
                    'margin-top:16px">'
                    '⚠️ Issues</div>',
                    unsafe_allow_html=True
                )
                for issue in report["issues"]:
                    sev = issue.get(
                        "severity", "MEDIUM"
                    )
                    st.markdown(
                        f'<div class="issue-card">'
                        f'<span class="severity-{sev}">'
                        f'{sev}</span>'
                        f'<span style="color:#94a3b8;'
                        f'font-size:0.8rem">'
                        f'[{issue.get("type","")}] '
                        f'{issue.get("description","")}'
                        f'</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

    st.divider()

    # ── Download JSON ──
    st.markdown(
        '<div style="font-size:0.7rem;'
        'font-weight:700;letter-spacing:2px;'
        'text-transform:uppercase;'
        'color:#475569;margin-bottom:12px">'
        '📥 Export Report'
        '</div>',
        unsafe_allow_html=True
    )

    export_data = {
        "report_type":   result.report_type,
        "processed_at":  str(
            __import__("datetime")
            .datetime.now().isoformat()
        ),
        "transcript":    result.transcript,
        "confidence":    result.transcript_confidence,
        "report":        result.report
    }

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="⬇️ Download JSON",
            data=json.dumps(
                export_data, indent=2
            ),
            file_name=(
                f"fieldreport_"
                f"{result.report_type}.json"
            ),
            mime="application/json",
            use_container_width=True
        )

    with col2:
        with st.expander("📋 View raw JSON"):
            st.json(result.report)

    st.caption(
        f"🎙️ FieldReport AI — "
        f"{REPORT_LABELS[result.report_type]} · "
        f"Powered by faster-whisper + "
        f"Gemini 2.0 Flash · Day 12 of 14"
    )