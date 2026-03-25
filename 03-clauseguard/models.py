from pydantic import BaseModel
from typing import List

class ClauseRisk(BaseModel):
    risk_level: str
    risk_category: str
    risk_summary: str
    plain_english: str
    what_to_watch: str
    negotiation_tip: str
    is_standard: bool
    clause_text: str      # original clause text
    chunk_index: int      # which chunk this came from

class ContractSummary(BaseModel):
    contract_type: str
    parties: List[str]
    key_obligations: List[str]
    contract_duration: str
    governing_law: str
    overall_risk: str

class ContractReport(BaseModel):
    file_name: str
    summary: ContractSummary
    clause_risks: List[ClauseRisk]
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    total_clauses_scanned: int