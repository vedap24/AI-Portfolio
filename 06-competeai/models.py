from pydantic import BaseModel
from typing import List

class CompanySnapshot(BaseModel):
    company_name: str
    is_your_company: bool
    current_position: str
    recent_moves: List[str]
    strengths: List[str]
    weaknesses: List[str]
    threat_level: str
    momentum: str

class KeySignal(BaseModel):
    signal: str
    company: str
    implication: str
    urgency: str

class RecommendedAction(BaseModel):
    action: str
    reason: str
    timeframe: str

class CompetitiveBrief(BaseModel):
    your_company: str
    competitors: List[str]
    executive_summary: str
    company_snapshots: List[CompanySnapshot]
    key_signals: List[KeySignal]
    market_trends: List[str]
    recommended_actions: List[RecommendedAction]
    watch_list: List[str]
    data_freshness: str
    queries_run: int
    results_analyzed: int