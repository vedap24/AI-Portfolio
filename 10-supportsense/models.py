from pydantic import BaseModel
from typing import List, Optional

class SupportAnswer(BaseModel):
    answer: str
    confidence: str
    answered_fully: bool
    source_sections: List[str]
    follow_up_suggestions: List[str]
    missing_info: str

class EscalationTicket(BaseModel):
    ticket_summary: str
    priority: str
    department: str
    customer_sentiment: str
    issue_type: str
    suggested_resolution: str
    context_for_agent: str
    estimated_resolution_time: str

class SupportResponse(BaseModel):
    query: str
    response_type: str      # "answer" | "escalation"
    intent: str
    intent_confidence: float
    # For answers
    answer: Optional[SupportAnswer] = None
    # For escalations
    escalation: Optional[EscalationTicket] = None
    # Shared
    retrieved_docs: List[dict]
    doc_count: int
    product_name: str