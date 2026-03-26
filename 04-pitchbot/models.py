from pydantic import BaseModel
from typing import List

class EmailVariant(BaseModel):
    variant: str
    subject: str
    body: str
    word_count: int
    best_for: str

class PitchResult(BaseModel):
    emails: List[EmailVariant]
    personalization_elements: List[str]
    follow_up_tip: str
    recipient_name: str
    recipient_role: str
    recipient_company: str
    primary_angle: str