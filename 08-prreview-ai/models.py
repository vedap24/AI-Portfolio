from pydantic import BaseModel
from typing import List, Optional

class BugIssue(BaseModel):
    severity: str
    line_reference: str
    description: str
    suggestion: str

class SecurityIssue(BaseModel):
    severity: str
    type: str
    description: str
    suggestion: str

class PerformanceIssue(BaseModel):
    severity: str
    description: str
    suggestion: str

class StyleIssue(BaseModel):
    description: str
    suggestion: str

class FileReview(BaseModel):
    file_name: str
    overall_rating: str
    bugs: List[BugIssue]
    security_issues: List[SecurityIssue]
    performance_issues: List[PerformanceIssue]
    style_issues: List[StyleIssue]
    missing_tests: List[str]
    positive_feedback: List[str]
    summary: str
    # Not from LLM — added by our code
    is_test_file: bool = False
    is_config_file: bool = False

class PRSummary(BaseModel):
    overall_verdict: str
    confidence: str
    critical_issues_count: int
    high_issues_count: int
    summary: str
    top_concerns: List[str]
    strengths: List[str]
    suggested_comment: str

class PRReview(BaseModel):
    pr_number: int
    pr_title: str
    pr_author: str
    repo: str
    pr_url: str
    file_reviews: List[FileReview]
    pr_summary: PRSummary
    files_reviewed: int
    total_bugs: int
    total_security_issues: int
    total_additions: int
    total_deletions: int