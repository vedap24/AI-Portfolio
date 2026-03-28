from pydantic import BaseModel
from typing import List

class SourceCitation(BaseModel):
    file_name: str
    relevant_quote: str

class QAResponse(BaseModel):
    answer: str
    confidence: str
    sources: List[SourceCitation]
    found_in_docs: bool
    follow_up_suggestions: List[str]

class DocumentMeta(BaseModel):
    file_name: str
    file_type: str
    chunks_added: int
    total_in_db: int
    char_count: int
    title_guess: str
    main_topics: List[str]
    one_line_summary: str

class KnowledgeBaseStatus(BaseModel):
    total_documents: int
    total_chunks: int
    document_names: List[str]