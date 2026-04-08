from pydantic import BaseModel
from typing import List, Optional

class KeyInsight(BaseModel):
    insight: str
    data_point: str
    impact: str
    category: str

class ChangeRecommendation(BaseModel):
    problem: str
    evidence: str
    action: str
    expected_impact: str

class BenchmarkComparison(BaseModel):
    your_response_rate: str
    industry_average: str
    your_vs_average: str
    interpretation: str

class JobSearchInsights(BaseModel):
    headline_insight: str
    performance_score: int
    score_reasoning: str
    key_insights: List[KeyInsight]
    what_is_working: List[str]
    what_to_change: List[ChangeRecommendation]
    weekly_action_plan: List[str]
    benchmark_comparison: BenchmarkComparison
    predicted_timeline: str