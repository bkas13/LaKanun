"""Law search request/response schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


class LawSearchRequest(BaseModel):
    q: str = Field(..., min_length=2, max_length=1000, description="Search query")
    country: Optional[str] = Field(None, pattern="^(nepal|india)$")
    category: Optional[str] = None
    document_type: Optional[str] = None
    top_k: int = Field(default=10, ge=1, le=100)


class LawSearchResult(BaseModel):
    id: str
    title: str
    full_text: str
    country: str
    category: str
    document_type: str
    article_number: str
    source_document: str
    score: float
    enactment_year: int = 0
    language: str = "en"
    # Accuracy safeguards
    confidence: str = "low"
    citation: str = ""
    last_verified: str = ""
    source_url: str = ""
    effective_date: str = ""

    model_config = {"populate_by_name": True}


class LawSearchResponse(BaseModel):
    query: str
    results: List[LawSearchResult]
    total: int
    detected_lang: str = "en"
    translated_query: Optional[str] = None


class LawDetail(BaseModel):
    id: str
    country: str
    source_document: str
    document_type: str
    article_number: str
    title: str
    full_text: str
    category: str
    subcategory: str = ""
    part: str = ""
    chapter: Optional[str] = None
    schedule: Optional[str] = None
    cross_references: List[str] = []
    language: str = "en"


class LawBrowseRequest(BaseModel):
    country: Optional[str] = Field(None, pattern="^(nepal|india)$")
    document_type: Optional[str] = None
    category: Optional[str] = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)


class LawBrowseResponse(BaseModel):
    articles: List[LawDetail]
    total: int
    offset: int
    limit: int


class LawPopularResponse(BaseModel):
    provision_id: str
    title: str
    country: str
    category: str
    view_count: int
    article_number: str = ""
    source_document: str = ""


class LawCategoryResponse(BaseModel):
    name: str
    count: int
    country_breakdown: dict = {}


class LawRecentResponse(BaseModel):
    provision_id: str
    title: str
    country: str
    category: str
    enactment_year: int
    article_number: str = ""
    source_document: str = ""


class LawBookmarkRequest(BaseModel):
    provision_id: str
    country: str
    category: str = ""
    title: str = ""
    note: str = ""


class LawBookmarkResponse(BaseModel):
    id: int
    provision_id: str
    country: str
    title: str
    note: str
    created_at: str
