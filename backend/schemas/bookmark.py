"""Bookmark request/response schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BookmarkCreate(BaseModel):
    provision_id: str = Field(..., max_length=255)
    country: str = Field(..., pattern="^(nepal|india)$")
    document_type: Optional[str] = None
    article_number: Optional[str] = None
    title: Optional[str] = None
    note: Optional[str] = ""


class BookmarkResponse(BaseModel):
    id: int
    user_id: int
    provision_id: str
    country: str
    document_type: Optional[str]
    article_number: Optional[str]
    title: Optional[str]
    note: str
    created_at: datetime

    class Config:
        from_attributes = True
