import streamlit as st
import tempfile
import os
from pathlib import Path
from app import (
    ingest_document,
    answer_question,
    get_kb_status,
    clear_knowledge_base,
    get_document_summary,
    extract_text
)

# ── Page config ──
st.set_page_config(
    page_title="BrainBase AI",
    page_icon="🧠",
    layout="wide"
)

# ── Custom CSS ──
st.markdown("""
<style>
    .stApp { background-color: #07080f; }

    .main-title {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
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

    .doc-card {
        background: #0f1020;
        border: 1px solid #1e1e3a;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }

    .doc-name {
        font-size: 0.88rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 4px;
    }

    .doc-meta {
        font-size: 0.75rem;
        color: #475569;
    }

    .answer-card {
        background: #0f1020;
        border: 1px solid #1e1e3a;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
    }

    .answer-text {
        font-size: 0.95rem;
        color: #e2e8f0;
        line-height: 1.85;
    }

    .confidence-HIGH {
        background: rgba(52,211,153,0.1);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.25);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1px;
        display: inline-block;
    }

    .confidence-MEDIUM {
        background: rgba(251,191,36,0.1);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.25);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1px;
        display: inline-block;
    }

    .confidence-LOW {
        background: rgba(248,113,113,0.1);
        color: #f87171;
        border: 1px solid rgba(248,113,113,0.25);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1px;
        display: inline-block;
    }

    .source-pill {
        display: inline-block;
        background: rgba(56,189,248,0.08);
        border: 1px solid rgba(56,189,248,0.2);
        color: #38bdf8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        margin: 3px;
    }

    .quote-box {
        background: rgba(129,140,248,0.05);
        border-left: 3px solid #818cf8;
        border-radius: 0 6px 6px 0;
        padding: 10px 14px;
        font-size: 0.82rem;
        color: #a5b4fc;
        font-style: italic;
        line-height: 1.6;
        margin-top: 6px;
    }

    .followup-chip {
        display: inline-block;
        background: #0f1020;
        border: 1px solid #1e1e3a;
        color: #94a3b8;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.78rem;
        margin: 4px;
        cursor: pointer;
    }

    .stat-box {
        background: #0f1020;
        border: 1px solid #1e1e3a;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }

    .stat-num {
        font-size: 1.8rem;
        font-weight: 900;
        color: #38bdf8;
    }

    .stat-label {
        font-size: 0.65rem;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #334155;
    }

    .empty-icon {
        font-size: 3rem;
        margin-bottom: 12px;
    }

    .history-q {
        font-size: 0.82rem;
        color: #38bdf8;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .history-a {
        font-size: 0.82rem;
        color: #94a3b8;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# ── Init session state ──
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []
if "current_question" not in st.session_state:
    st.session_state.current_question = ""

# ── Header ──
st.markdown(
    '<div class="main-title">🧠 BrainBase AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">'
    'Upload your notes, PDFs, and docs → '
    'ask questions in plain English → '
    'get cited answers from your own knowledge base.'
    '</div>',
    unsafe_allow_html=True
)

# ── Real world stat ──
st.info(
    "📊 **IDC Research** — the average knowledge worker "
    "spends 2.5 hours per day searching for information. "
    "**Asana State of Work Innovation, 2025** — 60% of "
    "work time is spent on 'work about work', not actual "
    "skilled work. BrainBase gives you instant answers "
    "from your own documents."
)

st.divider()

# ── Two column layout ──
left_col, right_col = st.columns([1, 2])

# ════════════════════════════════
# LEFT — Upload + KB Status
# ════════════════════════════════
with left_col:
    st.markdown("### 📁 Knowledge Base")

    # File uploader
    uploaded_files = st.file_uploader(
        label="Upload documents",
        label_visibility="collapsed",
        type=["pdf", "txt", "docx", "md"],
        accept_multiple_files=True,
        help="Supports PDF, TXT, DOCX, MD. Max 50MB each."
    )

    # Process uploaded files
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Check not already uploaded this session
            if uploaded_file.name not in \
               st.session_state.uploaded_docs:
                with st.spinner(
                    f"Ingesting {uploaded_file.name}..."
                ):
                    try:
                        suffix = Path(
                            uploaded_file.name
                        ).suffix

                        with tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=suffix
                        ) as tmp:
                            tmp.write(uploaded_file.read())
                            tmp_path = tmp.name

                        # Get summary before ingesting
                        extracted = extract_text(tmp_path)
                        summary = get_document_summary(
                            extracted["text"]
                        )

                        # Ingest
                        meta = ingest_document(tmp_path)
                        os.unlink(tmp_path)

                        st.session_state.uploaded_docs\
                            .append(uploaded_file.name)

                        st.success(
                            f"✅ {uploaded_file.name} "
                            f"ingested — "
                            f"{meta['chunks_added']} chunks"
                        )

                        # Show summary
                        st.markdown(
                            f'<div class="doc-card">'
                            f'<div class="doc-name">'
                            f'📄 {uploaded_file.name}'
                            f'</div>'
                            f'<div class="doc-meta">'
                            f'{summary["one_line_summary"]}'
                            f'</div>'
                            f'<div class="doc-meta" '
                            f'style="margin-top:4px">'
                            f'Topics: '
                            f'{", ".join(summary["main_topics"][:3])}'
                            f'</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    except Exception as e:
                        st.error(
                            f"❌ Failed to ingest "
                            f"{uploaded_file.name}: {e}"
                        )

    # KB Status
    status = get_kb_status()

    if status.total_documents > 0:
        st.markdown("<br>", unsafe_allow_html=True)

        # Stats
        s1, s2 = st.columns(2)
        with s1:
            st.markdown(
                f'<div class="stat-box">'
                f'<div class="stat-num">'
                f'{status.total_documents}</div>'
                f'<div class="stat-label">Documents</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with s2:
            st.markdown(
                f'<div class="stat-box">'
                f'<div class="stat-num">'
                f'{status.total_chunks}</div>'
                f'<div class="stat-label">Chunks</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Document list
        st.markdown(
            "**📚 Loaded Documents**"
        )
        for doc_name in status.document_names:
            st.markdown(
                f'<div class="doc-card">'
                f'<div class="doc-name">📄 {doc_name}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        # Clear KB button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(
            "🗑️ Clear Knowledge Base",
            use_container_width=True
        ):
            clear_knowledge_base()
            st.session_state.uploaded_docs = []
            st.session_state.chat_history = []
            st.rerun()

    else:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-icon">📭</div>'
            '<div style="font-size:0.85rem">'
            'No documents loaded yet.<br>'
            'Upload files above to get started.'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

# ════════════════════════════════
# RIGHT — Q&A Interface
# ════════════════════════════════
with right_col:
    st.markdown("### 💬 Ask Your Documents")

    # Question input
    question = st.text_input(
        label="question",
        label_visibility="collapsed",
        placeholder=(
            "Ask anything about your uploaded documents..."
        ),
        value=st.session_state.current_question
    )

    ask_col, clear_col = st.columns([3, 1])

    with ask_col:
        ask_btn = st.button(
            "🔍 Ask",
            use_container_width=True,
            type="primary",
            disabled=not question.strip()
        )

    with clear_col:
        if st.button(
            "Clear History",
            use_container_width=True
        ):
            st.session_state.chat_history = []
            st.session_state.current_question = ""
            st.rerun()

    # Handle question
    if ask_btn and question.strip():
        if status.total_documents == 0:
            st.warning(
                "⚠️ Upload at least one document first."
            )
        else:
            with st.spinner(
                "Searching your knowledge base..."
            ):
                try:
                    response = answer_question(question)
                    st.session_state.chat_history.insert(
                        0,
                        {
                            "question": question,
                            "response": response
                        }
                    )
                    st.session_state.current_question = ""
                    st.rerun()

                except ValueError as e:
                    st.warning(f"⚠️ {e}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    # Display chat history
    if st.session_state.chat_history:
        for i, item in enumerate(
            st.session_state.chat_history
        ):
            q = item["question"]
            r = item["response"]

            with st.expander(
                f"Q: {q[:70]}{'...' if len(q) > 70 else ''}",
                expanded=(i == 0)
            ):
                # Confidence badge
                conf_class = f"confidence-{r.confidence}"
                found_icon = (
                    "✅ Found in docs"
                    if r.found_in_docs
                    else "❌ Not in docs"
                )

                st.markdown(
                    f'<span class="{conf_class}">'
                    f'{r.confidence} CONFIDENCE'
                    f'</span>'
                    f'&nbsp;&nbsp;'
                    f'<span style="font-size:0.75rem;'
                    f'color:#64748b">{found_icon}</span>',
                    unsafe_allow_html=True
                )

                st.markdown("<br>", unsafe_allow_html=True)

                # Answer
                st.markdown(
                    f'<div class="answer-text">'
                    f'{r.answer}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Sources
                if r.sources:
                    st.markdown(
                        "<br>**📎 Sources**",
                        unsafe_allow_html=True
                    )
                    for src in r.sources:
                        st.markdown(
                            f'<span class="source-pill">'
                            f'📄 {src.file_name}'
                            f'</span>',
                            unsafe_allow_html=True
                        )
                        if src.relevant_quote:
                            st.markdown(
                                f'<div class="quote-box">'
                                f'"{src.relevant_quote}"'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                # Follow-up suggestions
                if r.follow_up_suggestions:
                    st.markdown(
                        "<br>**💡 You might also ask**"
                    )
                    for suggestion in \
                            r.follow_up_suggestions[:3]:
                        if st.button(
                            f"→ {suggestion}",
                            key=f"followup_{i}_{suggestion[:20]}"
                        ):
                            st.session_state\
                                .current_question \
                                = suggestion
                            st.rerun()

    else:
        if status.total_documents > 0:
            # Show example questions
            st.markdown(
                '<div class="empty-state">'
                '<div class="empty-icon">💬</div>'
                '<div style="font-size:0.85rem;'
                'color:#475569">'
                'Ask anything about your documents.<br>'
                'Try questions like:<br><br>'
                '"What are the main topics covered?"<br>'
                '"Summarize the key points"<br>'
                '"What does it say about [topic]?"'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="empty-state">'
                '<div class="empty-icon">🧠</div>'
                '<div style="font-size:0.85rem;'
                'color:#475569">'
                'Upload documents on the left<br>'
                'to start asking questions.'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )
            