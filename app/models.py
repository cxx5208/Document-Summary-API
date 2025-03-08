from pydantic import BaseModel, Field
from typing import List, Optional


class SearchQuery(BaseModel):
    """Model for search queries"""
    query: str
    top_k: int = Field(5, description="Number of results to return", ge=1, le=20)


class SearchResult(BaseModel):
    """Model for search results"""
    text: str
    relevance_score: float
    page_number: Optional[int] = None
    position: Optional[str] = None


class DocumentMetadata(BaseModel):
    """Model for document metadata"""
    id: str
    filename: str
    upload_date: str
    status: str = "processing"  # processing, completed, failed
    summary: Optional[str] = None
    chunk_count: Optional[int] = None
    error: Optional[str] = None