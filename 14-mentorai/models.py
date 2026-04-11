from pydantic import BaseModel
from typing import List, Optional

class Phase(BaseModel):
    phase_number: int
    phase_title: str
    duration_weeks: int
    focus_area: str
    skills: List[str]
    projects: List[str]
    resources: List[str]
    milestone: str
    why_this_phase: str

class PortfolioProject(BaseModel):
    project_name: str
    description: str
    techniques_demonstrated: List[str]
    difficulty: str
    impact: str

class WeeklySchedule(BaseModel):
    monday: str
    tuesday: str
    wednesday: str
    thursday: str
    friday: str
    saturday: str
    sunday: str

class LearningCurriculum(BaseModel):
    headline: str
    total_weeks: int
    weekly_hours: int
    readiness_score: int
    readiness_label: str
    phases: List[Phase]
    immediate_next_step: str
    skills_to_skip: List[str]
    biggest_gap: str
    salary_unlock: str
    time_to_first_job: str
    portfolio_projects: List[PortfolioProject]
    weekly_schedule: WeeklySchedule
    motivational_insight: str

class MentorResult(BaseModel):
    background: str
    goal: str
    time_available: str
    curriculum: LearningCurriculum
    retrieved_doc_count: int
    topics_covered: List[str]