import os
import re
import json
import time
from github import Github
from dotenv import load_dotenv
from google import genai
from models import (
    FileReview, BugIssue,
    SecurityIssue, PerformanceIssue,
    StyleIssue, PRSummary, PRReview
)
from prompts import (
    FILE_REVIEW_PROMPT,
    PR_SUMMARY_PROMPT
)

load_dotenv()

# ── Clients ──
github_client = Github(
    os.getenv("GITHUB_TOKEN")
)
gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
GEMINI_MODEL = "gemini-3.1-flash-lite-preview"


# ──────────────────────────────────────────
# CORE UTILITIES
# ──────────────────────────────────────────

def clean_gemini_response(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = [
            l for l in lines
            if not l.strip().startswith("```")
        ]
        raw = "\n".join(lines).strip()
    return raw


def call_gemini(
    prompt: str,
    retries: int = 3
) -> str:
    last_error = None
    for attempt in range(retries + 1):
        try:
            response = (
                gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt
                )
            )
            return response.text
        except Exception as e:
            error_str = str(e)
            last_error = error_str
            if "429" in error_str or \
               "RESOURCE_EXHAUSTED" in error_str:
                if attempt < retries:
                    print(
                        "⏳ Rate limit. Waiting 40s..."
                    )
                    time.sleep(40)
                    continue
            if attempt < retries:
                time.sleep(2)
                continue
    raise RuntimeError(
        f"Gemini failed: {last_error}"
    )


# ──────────────────────────────────────────
# URL PARSER
# ──────────────────────────────────────────

def parse_pr_url(url: str) -> tuple:
    url = url.strip()
    url = re.sub(r'https?://', '', url)
    url = re.sub(r'github\.com/', '', url)

    pattern = r'^([^/]+)/([^/]+)/pull/(\d+)'
    match = re.match(pattern, url)

    if not match:
        raise ValueError(
            f"Invalid GitHub PR URL.\n"
            f"Expected: "
            f"https://github.com/owner/repo/pull/123\n"
            f"Got: {url}"
        )

    return (
        match.group(1),
        match.group(2),
        int(match.group(3))
    )


# ──────────────────────────────────────────
# PR FETCHER
# ──────────────────────────────────────────

def fetch_pr_data(pr_url: str) -> dict:
    owner, repo_name, pr_num = parse_pr_url(
        pr_url
    )

    print(
        f"📦 Fetching PR #{pr_num} from "
        f"{owner}/{repo_name}..."
    )

    try:
        repo = github_client.get_repo(
            f"{owner}/{repo_name}"
        )
        pr   = repo.get_pull(pr_num)

    except Exception as e:
        error_str = str(e)
        if "401" in error_str:
            raise RuntimeError(
                "GitHub authentication failed. "
                "Check GITHUB_TOKEN in .env — "
                "make sure it has 'repo' scope."
            )
        elif "404" in error_str:
            raise RuntimeError(
                f"PR not found: "
                f"{owner}/{repo_name}#{pr_num}. "
                f"Check the URL. If the repo is "
                f"private, ensure your token "
                f"has access."
            )
        elif "403" in error_str:
            raise RuntimeError(
                "GitHub rate limit exceeded. "
                "Wait a few minutes and try again. "
                "Authenticated requests get "
                "5000/hour limit."
            )
        else:
            raise RuntimeError(
                f"GitHub API error: {error_str}"
            )

    # Check PR state
    if pr.state == "closed" and not pr.merged:
        print(
            "  ⚠️  PR is closed but not merged — "
            "reviewing anyway"
        )

    files = list(pr.get_files())

    if not files:
        raise ValueError(
            "This PR has no changed files."
        )

    if len(files) > 50:
        print(
            f"  ⚠️  Large PR: {len(files)} files. "
            f"Will review first 10 only."
        )

    print(
        f"  ✅ PR: '{pr.title}' "
        f"by {pr.user.login}"
    )
    print(
        f"     Files   : {len(files)} changed"
    )
    print(
        f"     +{pr.additions} / -{pr.deletions}"
    )

    return {
        "pr_number":   pr_num,
        "pr_title":    pr.title,
        "pr_body":     pr.body or "",
        "pr_author":   pr.user.login,
        "base_branch": pr.base.ref,
        "head_branch": pr.head.ref,
        "additions":   pr.additions,
        "deletions":   pr.deletions,
        "files":       files,
        "repo":        f"{owner}/{repo_name}",
        "pr_url":      pr_url
    }


# ──────────────────────────────────────────
# DIFF PARSER
# ──────────────────────────────────────────

def parse_file_diff(file) -> dict:
    filename = file.filename
    ext = filename.rsplit(".", 1)[-1] \
          if "." in filename else "unknown"
    patch = file.patch or ""

    # Handle binary files
    is_binary = "Binary files" in patch
    if is_binary:
        patch = "[Binary file — skipped]"

    # Truncate large diffs
    max_chars  = 3000
    truncated  = False
    if len(patch) > max_chars:
        patch     = patch[:max_chars]
        truncated = True

    return {
        "filename":  filename,
        "extension": ext,
        "status":    file.status,
        "additions": file.additions,
        "deletions": file.deletions,
        "patch":     patch,
        "truncated": truncated,
        "is_binary": is_binary,
        "is_test": any(
            kw in filename.lower()
            for kw in [
                "test", "spec",
                "_test", ".test"
            ]
        ),
        "is_config": ext in [
            "json", "yaml", "yml",
            "toml", "env", "cfg", "ini"
        ]
    }


def extract_reviewable_files(
    pr_data: dict,
    max_files: int = 10
) -> list:
    skip_names = [
        "package-lock.json",
        "yarn.lock",
        "poetry.lock",
        "Pipfile.lock",
        ".min.js",
        ".min.css",
        ".map",
        "dist/",
        "build/",
        "__pycache__"
    ]

    reviewable = []

    for file in pr_data["files"]:
        filename = file.filename

        # Skip generated/lock files
        if any(
            skip in filename
            for skip in skip_names
        ):
            print(
                f"  ⏭️  Skip: {filename}"
            )
            continue

        # Skip no-diff files
        if not file.patch:
            print(
                f"  ⏭️  No diff: {filename}"
            )
            continue

        parsed = parse_file_diff(file)
        reviewable.append(parsed)

        if len(reviewable) >= max_files:
            print(
                f"  ℹ️  Limit: {max_files} files"
            )
            break

    if not reviewable:
        raise ValueError(
            "No reviewable files found. "
            "All files may be binary, "
            "generated, or lock files."
        )

    print(
        f"  ✅ {len(reviewable)} files "
        f"ready for review"
    )
    return reviewable


def fetch_and_parse_pr(
    pr_url: str,
    max_files: int = 10
) -> dict:
    # Validate URL first
    parse_pr_url(pr_url)

    pr_data    = fetch_pr_data(pr_url)
    reviewable = extract_reviewable_files(
        pr_data, max_files
    )

    return {
        "pr_number":   pr_data["pr_number"],
        "pr_title":    pr_data["pr_title"],
        "pr_body":     pr_data["pr_body"],
        "pr_author":   pr_data["pr_author"],
        "base_branch": pr_data["base_branch"],
        "head_branch": pr_data["head_branch"],
        "additions":   pr_data["additions"],
        "deletions":   pr_data["deletions"],
        "repo":        pr_data["repo"],
        "pr_url":      pr_url,
        "files":       reviewable,
        "file_count":  len(reviewable)
    }


# ──────────────────────────────────────────
# REVIEW ENGINE
# ──────────────────────────────────────────

def validate_severity(
    severity: str,
    valid: list = None
) -> str:
    if valid is None:
        valid = [
            "CRITICAL", "HIGH",
            "MEDIUM", "LOW"
        ]
    return severity if severity in valid \
        else "MEDIUM"


def parse_file_review(
    data: dict,
    file_meta: dict
) -> FileReview:
    valid_ratings = [
        "LGTM", "NEEDS_CHANGES", "CRITICAL"
    ]
    if data.get("overall_rating") \
       not in valid_ratings:
        data["overall_rating"] = "NEEDS_CHANGES"

    bugs = []
    for b in data.get("bugs", []):
        if not isinstance(b, dict):
            continue
        try:
            bugs.append(BugIssue(
                severity=validate_severity(
                    b.get("severity", "MEDIUM")
                ),
                line_reference=str(
                    b.get("line_reference", "?")
                ),
                description=b.get(
                    "description", "No description"
                ),
                suggestion=b.get(
                    "suggestion", "Review manually"
                )
            ))
        except Exception:
            continue

    security = []
    for s in data.get("security_issues", []):
        if not isinstance(s, dict):
            continue
        try:
            security.append(SecurityIssue(
                severity=validate_severity(
                    s.get("severity", "HIGH")
                ),
                type=s.get("type", "Other"),
                description=s.get(
                    "description", "No description"
                ),
                suggestion=s.get(
                    "suggestion", "Review manually"
                )
            ))
        except Exception:
            continue

    performance = []
    for p in data.get("performance_issues", []):
        if not isinstance(p, dict):
            continue
        try:
            performance.append(PerformanceIssue(
                severity=validate_severity(
                    p.get("severity", "LOW"),
                    ["HIGH", "MEDIUM", "LOW"]
                ),
                description=p.get(
                    "description", "No description"
                ),
                suggestion=p.get(
                    "suggestion", "Review manually"
                )
            ))
        except Exception:
            continue

    style = []
    for st in data.get("style_issues", []):
        if not isinstance(st, dict):
            continue
        try:
            style.append(StyleIssue(
                description=st.get(
                    "description", "No description"
                ),
                suggestion=st.get(
                    "suggestion", "Review manually"
                )
            ))
        except Exception:
            continue

    missing = data.get("missing_tests", [])
    if not isinstance(missing, list):
        missing = []

    positive = data.get("positive_feedback", [])
    if not isinstance(positive, list):
        positive = []

    return FileReview(
        file_name=data.get(
            "file_name",
            file_meta["filename"]
        ),
        overall_rating=data["overall_rating"],
        bugs=bugs,
        security_issues=security,
        performance_issues=performance,
        style_issues=style,
        missing_tests=missing,
        positive_feedback=positive,
        summary=data.get(
            "summary",
            "No summary available."
        ),
        is_test_file=file_meta.get(
            "is_test", False
        ),
        is_config_file=file_meta.get(
            "is_config", False
        )
    )


def review_single_file(
    file_data: dict
) -> FileReview:
    # Skip binary files
    if file_data.get("is_binary"):
        return FileReview(
            file_name=file_data["filename"],
            overall_rating="LGTM",
            bugs=[],
            security_issues=[],
            performance_issues=[],
            style_issues=[],
            missing_tests=[],
            positive_feedback=[],
            summary="Binary file — skipped.",
            is_test_file=False,
            is_config_file=False
        )

    prompt = FILE_REVIEW_PROMPT.format(
        filename=file_data["filename"],
        extension=file_data["extension"],
        status=file_data["status"],
        additions=file_data["additions"],
        deletions=file_data["deletions"],
        patch=file_data["patch"]
    )

    try:
        raw = call_gemini(prompt)
        raw = clean_gemini_response(raw)
        data = json.loads(raw)
        return parse_file_review(
            data, file_data
        )

    except json.JSONDecodeError:
        return FileReview(
            file_name=file_data["filename"],
            overall_rating="NEEDS_CHANGES",
            bugs=[],
            security_issues=[],
            performance_issues=[],
            style_issues=[],
            missing_tests=[],
            positive_feedback=[],
            summary=(
                "Could not analyze this file. "
                "Please review manually."
            ),
            is_test_file=file_data.get(
                "is_test", False
            ),
            is_config_file=file_data.get(
                "is_config", False
            )
        )

    except Exception as e:
        print(
            f"  ⚠️  Failed to review "
            f"{file_data['filename']}: {e}"
        )
        return FileReview(
            file_name=file_data["filename"],
            overall_rating="NEEDS_CHANGES",
            bugs=[],
            security_issues=[],
            performance_issues=[],
            style_issues=[],
            missing_tests=[],
            positive_feedback=[],
            summary=f"Review failed: {str(e)[:100]}",
            is_test_file=False,
            is_config_file=False
        )


def generate_pr_summary(
    pr_data: dict,
    file_reviews: list
) -> PRSummary:
    summaries = []
    for r in file_reviews:
        summaries.append(
            f"File: {r.file_name}\n"
            f"Rating: {r.overall_rating}\n"
            f"Bugs: {len(r.bugs)} | "
            f"Security: {len(r.security_issues)}\n"
            f"Summary: {r.summary}"
        )

    prompt = PR_SUMMARY_PROMPT.format(
        pr_title=pr_data["pr_title"],
        pr_body=(
            pr_data["pr_body"][:500] or "None"
        ),
        file_count=pr_data["file_count"],
        additions=pr_data["additions"],
        deletions=pr_data["deletions"],
        file_summaries="\n\n---\n\n".join(
            summaries
        )
    )

    try:
        raw = call_gemini(prompt)
        raw = clean_gemini_response(raw)
        data = json.loads(raw)

        valid_verdicts = [
            "APPROVE",
            "REQUEST_CHANGES",
            "NEEDS_DISCUSSION"
        ]
        if data.get("overall_verdict") \
           not in valid_verdicts:
            data["overall_verdict"] = \
                "REQUEST_CHANGES"

        if data.get("confidence") not in \
           ["HIGH", "MEDIUM", "LOW"]:
            data["confidence"] = "MEDIUM"

        for field in [
            "critical_issues_count",
            "high_issues_count"
        ]:
            try:
                data[field] = int(
                    data.get(field, 0)
                )
            except (ValueError, TypeError):
                data[field] = 0

        for field in [
            "top_concerns", "strengths"
        ]:
            if not isinstance(
                data.get(field), list
            ):
                data[field] = []

        for field in [
            "summary", "suggested_comment"
        ]:
            if not data.get(field):
                data[field] = "Not available."

        return PRSummary(**data)

    except (json.JSONDecodeError, Exception):
        return PRSummary(
            overall_verdict="REQUEST_CHANGES",
            confidence="LOW",
            critical_issues_count=0,
            high_issues_count=0,
            summary=(
                "Could not generate PR summary. "
                "Review individual file results."
            ),
            top_concerns=[],
            strengths=[],
            suggested_comment=(
                "## PR Review\n\n"
                "Automated review incomplete. "
                "Please review manually."
            )
        )


def review_pull_request(
    pr_url: str,
    on_progress=None,
    max_files: int = 10
) -> PRReview:

    # Validate
    if not pr_url or not pr_url.strip():
        raise ValueError(
            "Please enter a GitHub PR URL."
        )

    # Fetch
    print("\n🔍 Fetching PR...")
    pr_data = fetch_and_parse_pr(
        pr_url, max_files
    )

    print(
        f"\n📋 Reviewing "
        f"{pr_data['file_count']} files..."
    )

    # Review each file
    file_reviews = []
    for i, file_data in enumerate(
        pr_data["files"]
    ):
        print(
            f"  [{i+1}/{pr_data['file_count']}] "
            f"{file_data['filename']}"
        )

        if on_progress:
            on_progress(
                i + 1,
                pr_data["file_count"],
                file_data["filename"]
            )

        review = review_single_file(file_data)
        file_reviews.append(review)
        time.sleep(1.5)

    # Summarize
    print("\n🤖 Generating summary...")
    pr_summary = generate_pr_summary(
        pr_data, file_reviews
    )

    total_bugs = sum(
        len(r.bugs) for r in file_reviews
    )
    total_sec  = sum(
        len(r.security_issues)
        for r in file_reviews
    )

    return PRReview(
        pr_number=pr_data["pr_number"],
        pr_title=pr_data["pr_title"],
        pr_author=pr_data["pr_author"],
        repo=pr_data["repo"],
        pr_url=pr_url,
        file_reviews=file_reviews,
        pr_summary=pr_summary,
        files_reviewed=len(file_reviews),
        total_bugs=total_bugs,
        total_security_issues=total_sec,
        total_additions=pr_data["additions"],
        total_deletions=pr_data["deletions"]
    )


# ───── Tests ─────
if __name__ == "__main__":

    print("\n🧪 Test 1: Valid URL parse")
    o, r, n = parse_pr_url(
        "https://github.com/microsoft/vscode/pull/1"
    )
    print(f"  ✅ {o}/{r} #{n}")

    print("\n🧪 Test 2: Invalid URL")
    try:
        parse_pr_url("not-a-valid-url")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 3: Short URL format")
    o2, r2, n2 = parse_pr_url(
        "owner/repo/pull/42"
    )
    print(f"  ✅ {o2}/{r2} #{n2}")

    print("\n🧪 Test 4: Empty URL")
    try:
        review_pull_request("")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 5: severity validator")
    assert validate_severity("HIGH") == "HIGH"
    assert validate_severity("INVALID") == "MEDIUM"
    assert validate_severity("") == "MEDIUM"
    print("  ✅ Severity validation correct")

    print("\n🧪 Test 6: Full PR review")
    test_url = input(
        "\n  Paste your test PR URL "
        "(or Enter to skip): "
    ).strip()

    if test_url:
        review = review_pull_request(test_url)
        print(
            f"\n  ✅ Verdict   : "
            f"{review.pr_summary.overall_verdict}"
        )
        print(
            f"     Files    : "
            f"{review.files_reviewed}"
        )
        print(
            f"     Bugs     : {review.total_bugs}"
        )
        print(
            f"     Security : "
            f"{review.total_security_issues}"
        )
        assert review.pr_summary.suggested_comment
        print(
            "     Comment  : present ✓"
        )
    else:
        print("  ⏭️  Skipped")

    print("\n✅ All tests passed.")