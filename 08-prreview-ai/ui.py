import streamlit as st
from app import review_pull_request

# ── Page config ──
st.set_page_config(
    page_title="PRReview AI",
    page_icon="🔍",
    layout="wide"
)

# ── Custom CSS ──
st.markdown("""
<style>
    .stApp { background-color: #080d14; }

    .main-title {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(
            90deg, #60a5fa, #a78bfa
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

    .verdict-APPROVE {
        background: rgba(52,211,153,0.08);
        border: 2px solid rgba(52,211,153,0.35);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .verdict-REQUEST_CHANGES {
        background: rgba(251,191,36,0.06);
        border: 2px solid rgba(251,191,36,0.3);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .verdict-NEEDS_DISCUSSION {
        background: rgba(96,165,250,0.06);
        border: 2px solid rgba(96,165,250,0.3);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .verdict-label-APPROVE {
        font-size: 1.6rem;
        font-weight: 900;
        color: #34d399;
    }

    .verdict-label-REQUEST_CHANGES {
        font-size: 1.6rem;
        font-weight: 900;
        color: #fbbf24;
    }

    .verdict-label-NEEDS_DISCUSSION {
        font-size: 1.6rem;
        font-weight: 900;
        color: #60a5fa;
    }

    .stat-box {
        background: #0d1520;
        border: 1px solid #1e2d3d;
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
        margin-top: 2px;
    }

    .file-card {
        background: #0d1520;
        border: 1px solid #1e2d3d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 14px;
    }

    .file-name {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.88rem;
        font-weight: 700;
        color: #60a5fa;
        margin-bottom: 6px;
    }

    .rating-LGTM {
        background: rgba(52,211,153,0.1);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.25);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
    }

    .rating-NEEDS_CHANGES {
        background: rgba(251,191,36,0.1);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.25);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
    }

    .rating-CRITICAL {
        background: rgba(239,68,68,0.1);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.25);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
    }

    .issue-CRITICAL {
        background: rgba(239,68,68,0.06);
        border-left: 3px solid #ef4444;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin-bottom: 8px;
    }

    .issue-HIGH {
        background: rgba(251,107,36,0.06);
        border-left: 3px solid #f97316;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin-bottom: 8px;
    }

    .issue-MEDIUM {
        background: rgba(251,191,36,0.05);
        border-left: 3px solid #fbbf24;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin-bottom: 8px;
    }

    .issue-LOW {
        background: rgba(100,116,139,0.05);
        border-left: 3px solid #64748b;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin-bottom: 8px;
    }

    .issue-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 4px;
    }

    .issue-suggestion {
        font-size: 0.8rem;
        color: #64748b;
        line-height: 1.6;
        margin-top: 4px;
    }

    .sev-badge-CRITICAL {
        background: rgba(239,68,68,0.15);
        color: #f87171;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-right: 6px;
    }

    .sev-badge-HIGH {
        background: rgba(249,115,22,0.15);
        color: #fb923c;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-right: 6px;
    }

    .sev-badge-MEDIUM {
        background: rgba(251,191,36,0.12);
        color: #fbbf24;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-right: 6px;
    }

    .sev-badge-LOW {
        background: rgba(100,116,139,0.12);
        color: #94a3b8;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-right: 6px;
    }

    .positive-item {
        font-size: 0.82rem;
        color: #34d399;
        padding: 5px 0;
        border-bottom: 1px solid #1e2d3d;
    }

    .positive-item:last-child {
        border-bottom: none;
    }

    .concern-item {
        font-size: 0.85rem;
        color: #94a3b8;
        padding: 6px 0;
        border-bottom: 1px solid #1e2d3d;
        line-height: 1.6;
    }

    .concern-item:last-child {
        border-bottom: none;
    }

    .comment-box {
        background: #0a0f18;
        border: 1px solid #1e2d3d;
        border-radius: 8px;
        padding: 16px;
        font-family: monospace;
        font-size: 0.82rem;
        color: #94a3b8;
        line-height: 1.8;
        white-space: pre-wrap;
    }

    .diff-add {
        color: #34d399;
        font-family: monospace;
        font-size: 0.78rem;
    }

    .diff-remove {
        color: #f87171;
        font-family: monospace;
        font-size: 0.78rem;
    }

    .section-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 12px;
    }

    .pr-meta {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        margin-bottom: 16px;
    }

    .pr-meta-item {
        font-size: 0.8rem;
        color: #64748b;
    }

    .pr-meta-item strong {
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown(
    '<div class="main-title">🔍 PRReview AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">'
    'Paste a GitHub PR URL → get an AI code review '
    'covering bugs, security, performance, and style. '
    'Powered by Gemini 2.0 Flash + GitHub API.'
    '</div>',
    unsafe_allow_html=True
)

# ── Real world stat ──
st.info(
    "📊 **GitHub Octoverse, 2025** — "
    "teams with high AI adoption merge 98% more PRs "
    "but PR review time increases 91%. "
    "Code review is now the #1 engineering bottleneck. "
    "**PRReview AI cuts review time for every PR.**"
)

st.divider()

# ── Input ──
st.markdown("### Paste GitHub PR URL")

pr_url = st.text_input(
    label="pr_url",
    label_visibility="collapsed",
    placeholder=(
        "https://github.com/owner/repo/pull/123"
    )
)

col1, col2 = st.columns([3, 1])
with col1:
    max_files = st.slider(
        "Max files to review",
        min_value=1,
        max_value=10,
        value=5,
        help="More files = more thorough but slower"
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    review_btn = st.button(
        "🚀 Review PR",
        use_container_width=True,
        type="primary",
        disabled=not pr_url.strip()
    )

st.divider()

# ── Review ──
if review_btn and pr_url.strip():
    progress_bar = st.progress(0)
    status_text  = st.empty()

    def on_progress(current, total, filename):
        pct = int((current / total) * 100)
        progress_bar.progress(pct)
        status_text.markdown(
            f"🔍 Reviewing file "
            f"({current}/{total}): "
            f"`{filename}`"
        )

    try:
        with st.spinner(""):
            review = review_pull_request(
                pr_url,
                on_progress=on_progress
            )
            st.session_state["review"] = review

        progress_bar.progress(100)
        status_text.markdown(
            "✅ Review complete!"
        )

    except ValueError as e:
        st.warning(f"⚠️ {e}")
        st.stop()
    except RuntimeError as e:
        st.error(f"❌ {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        st.stop()

# ── Display review ──
if "review" in st.session_state:
    review  = st.session_state["review"]
    summary = review.pr_summary
    verdict = summary.overall_verdict

    st.success("✅ Code review complete!")
    st.divider()

    # ── PR Meta ──
    st.markdown(
        f'<div class="pr-meta">'
        f'<span class="pr-meta-item">'
        f'<strong>PR:</strong> '
        f'#{review.pr_number} — {review.pr_title}'
        f'</span>'
        f'<span class="pr-meta-item">'
        f'<strong>Author:</strong> '
        f'{review.pr_author}'
        f'</span>'
        f'<span class="pr-meta-item">'
        f'<strong>Repo:</strong> {review.repo}'
        f'</span>'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Stats row ──
    s1, s2, s3, s4, s5 = st.columns(5)

    stats = [
        (s1, review.files_reviewed,
         "#60a5fa", "Files Reviewed"),
        (s2, review.total_bugs,
         "#f87171", "Bugs Found"),
        (s3, review.total_security_issues,
         "#fbbf24", "Security Issues"),
        (s4, review.total_additions,
         "#34d399", "Lines Added"),
        (s5, review.total_deletions,
         "#f87171", "Lines Removed"),
    ]

    for col, num, color, label in stats:
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

    # ── Verdict card ──
    verdict_icons = {
        "APPROVE":          "✅",
        "REQUEST_CHANGES":  "🔄",
        "NEEDS_DISCUSSION": "💬"
    }
    verdict_desc = {
        "APPROVE": "This PR looks good to merge.",
        "REQUEST_CHANGES": (
            "Changes needed before merging."
        ),
        "NEEDS_DISCUSSION": (
            "Discuss with the team before merging."
        )
    }

    icon  = verdict_icons.get(verdict, "🔍")
    desc  = verdict_desc.get(verdict, "")
    color_map = {
        "APPROVE":          "#34d399",
        "REQUEST_CHANGES":  "#fbbf24",
        "NEEDS_DISCUSSION": "#60a5fa"
    }
    v_color = color_map.get(verdict, "#94a3b8")

    st.markdown(
        f'<div class="verdict-{verdict}">',
        unsafe_allow_html=True
    )

    v_left, v_right = st.columns([1, 2])

    with v_left:
        st.markdown(
            f'<div class="verdict-label-{verdict}">'
            f'{icon} {verdict.replace("_", " ")}'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<p style="color:#94a3b8;'
            f'font-size:0.85rem">{desc}</p>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<p style="font-size:0.75rem;'
            f'color:#475569">Confidence: '
            f'{summary.confidence}</p>',
            unsafe_allow_html=True
        )

    with v_right:
        st.markdown(
            f'<p style="color:#cbd5e1;'
            f'font-size:0.9rem;line-height:1.8">'
            f'{summary.summary}</p>',
            unsafe_allow_html=True
        )

        if summary.top_concerns:
            concerns_html = "".join([
                f'<div class="concern-item">'
                f'⚠️ {c}</div>'
                for c in summary.top_concerns
            ])
            st.markdown(
                f'<div style="margin-top:12px">'
                f'<div class="section-label" '
                f'style="color:#fbbf24">'
                f'Top Concerns</div>'
                f'{concerns_html}</div>',
                unsafe_allow_html=True
            )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    # ── Main layout ──
    left, right = st.columns([3, 2])

    with left:
        st.markdown(
            '<div class="section-label" '
            'style="color:#60a5fa">'
            '📁 File Reviews'
            '</div>',
            unsafe_allow_html=True
        )

        for file_review in review.file_reviews:
            rating    = file_review.overall_rating
            badge_cls = f"rating-{rating}"

            with st.expander(
                f"{file_review.file_name} "
                f"— {rating}",
                expanded=(
                    rating == "CRITICAL"
                )
            ):
                # File header
                st.markdown(
                    f'<span class="{badge_cls}">'
                    f'{rating}</span>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<p style="color:#94a3b8;'
                    f'font-size:0.85rem;'
                    f'margin-top:8px">'
                    f'{file_review.summary}'
                    f'</p>',
                    unsafe_allow_html=True
                )

                st.divider()

                # Bugs
                if file_review.bugs:
                    st.markdown(
                        "**🐛 Bugs**"
                    )
                    for bug in file_review.bugs:
                        sev_cls = (
                            f"sev-badge-{bug.severity}"
                        )
                        issue_cls = (
                            f"issue-{bug.severity}"
                        )
                        st.markdown(
                            f'<div class="{issue_cls}">'
                            f'<div class="issue-title">'
                            f'<span class="{sev_cls}">'
                            f'{bug.severity}</span>'
                            f'{bug.description}'
                            f'</div>'
                            f'<div class='
                            f'"issue-suggestion">'
                            f'💡 {bug.suggestion}'
                            f'</div>'
                            f'<div style="font-size:'
                            f'0.72rem;color:#475569;'
                            f'margin-top:4px">'
                            f'Line: '
                            f'{bug.line_reference}'
                            f'</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                # Security issues
                if file_review.security_issues:
                    st.markdown(
                        "**🔐 Security**"
                    )
                    for sec in \
                            file_review.security_issues:
                        sev_cls = (
                            f"sev-badge-{sec.severity}"
                        )
                        issue_cls = (
                            f"issue-{sec.severity}"
                        )
                        st.markdown(
                            f'<div class="{issue_cls}">'
                            f'<div class="issue-title">'
                            f'<span class="{sev_cls}">'
                            f'{sec.severity}</span>'
                            f'[{sec.type}] '
                            f'{sec.description}'
                            f'</div>'
                            f'<div class='
                            f'"issue-suggestion">'
                            f'💡 {sec.suggestion}'
                            f'</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                # Performance
                if file_review.performance_issues:
                    st.markdown(
                        "**⚡ Performance**"
                    )
                    for perf in \
                       file_review.performance_issues:
                        st.markdown(
                            f'<div class="issue-LOW">'
                            f'<div class="issue-title">'
                            f'{perf.description}'
                            f'</div>'
                            f'<div class='
                            f'"issue-suggestion">'
                            f'💡 {perf.suggestion}'
                            f'</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                # Style
                if file_review.style_issues:
                    st.markdown(
                        "**✏️ Style**"
                    )
                    for style in \
                            file_review.style_issues:
                        st.markdown(
                            f'<div class="issue-LOW">'
                            f'<div class="issue-title">'
                            f'{style.description}'
                            f'</div>'
                            f'<div class='
                            f'"issue-suggestion">'
                            f'💡 {style.suggestion}'
                            f'</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                # Missing tests
                if file_review.missing_tests:
                    st.markdown(
                        "**🧪 Missing Tests**"
                    )
                    for test in \
                            file_review.missing_tests:
                        st.markdown(
                            f"- {test}"
                        )

                # Positive feedback
                if file_review.positive_feedback:
                    st.markdown(
                        "**👍 What's Good**"
                    )
                    feedback_html = "".join([
                        f'<div class="positive-item">'
                        f'✓ {f}</div>'
                        for f in
                        file_review.positive_feedback
                    ])
                    st.markdown(
                        f'<div>{feedback_html}</div>',
                        unsafe_allow_html=True
                    )

    with right:
        # Strengths
        if summary.strengths:
            st.markdown(
                '<div class="section-label" '
                'style="color:#34d399">'
                '💪 PR Strengths'
                '</div>',
                unsafe_allow_html=True
            )
            for strength in summary.strengths:
                st.markdown(
                    f'<div class="positive-item">'
                    f'✓ {strength}</div>',
                    unsafe_allow_html=True
                )

            st.markdown(
                "<br>", unsafe_allow_html=True
            )

        # Suggested comment
        st.markdown(
            '<div class="section-label" '
            'style="color:#a78bfa">'
            '💬 Ready-to-Paste Review Comment'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="comment-box">'
            f'{summary.suggested_comment}'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            "<br>", unsafe_allow_html=True
        )

        # Copy button
        with st.expander(
            "📋 Copy review comment"
        ):
            st.code(
                summary.suggested_comment,
                language="markdown"
            )

    st.divider()

    st.caption(
        f"🔍 PRReview AI — {review.files_reviewed} "
        f"files reviewed · "
        f"Powered by GitHub API + Gemini 2.0 Flash · "
        f"Day 8 of 14"
    )