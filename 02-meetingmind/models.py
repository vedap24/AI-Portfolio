from pydantic import BaseModel
from typing import List

class ActionItem(BaseModel):
    task: str
    owner: str
    deadline: str

class MeetingBrief(BaseModel):
    summary: str
    decisions: List[str]
    action_items: List[ActionItem]
    follow_up_questions: List[str]
    key_topics: List[str]
    meeting_sentiment: str
    one_line_outcome: str