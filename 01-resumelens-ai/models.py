from pydantic import BaseModel
from typing import List

class ResumeScore(BaseModel):
    fit_score: int
    fit_label: str
    matched_skills: List[str]
    missing_skills: List[str]
    experience_gap: str
    top_strengths: List[str]
    improvement_tips: List[str]
    summary: str