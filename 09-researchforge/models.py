from pydantic import BaseModel
from typing import List, Optional

class KeyFinding(BaseModel):
    finding: str
    detail: str
    confidence: str

class ReportSection(BaseModel):
    section_title: str
    content: str
    sub_question_answered: str

class VerifiedFact(BaseModel):
    fact: str
    confidence: str
    source_url: str
    sub_question: str

class SubQuestion(BaseModel):
    question: str
    search_query: str
    purpose: str

class FinalReport(BaseModel):
    executive_summary: str
    key_findings: List[KeyFinding]
    section_breakdown: List[ReportSection]
    conclusions: List[str]
    follow_up_questions: List[str]
    confidence_score: int
    word_count_estimate: int

class ResearchResult(BaseModel):
    query: str
    research_angle: str
    sub_questions: List[SubQuestion]
    verified_facts: List[VerifiedFact]
    contradictions: List[str]
    knowledge_gaps: List[str]
    source_quality: str
    final_report: FinalReport
    agent_logs: list
    search_result_count: int
    fact_count: int