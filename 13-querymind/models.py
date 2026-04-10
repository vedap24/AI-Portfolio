from pydantic import BaseModel
from typing import List, Optional

class SQLResult(BaseModel):
    sql: str
    explanation: str
    tables_used: List[str]
    confidence: str

class QueryResult(BaseModel):
    question: str
    sql: str
    sql_explanation: str
    columns: List[str]
    rows: List[tuple]
    row_count: int
    result_explanation: str
    tables_used: List[str]
    confidence: str
    retried: bool
    retry_count: int
    error: Optional[str] = None