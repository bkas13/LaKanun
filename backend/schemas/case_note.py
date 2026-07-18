"""CaseNote request/response schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CaseNoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = ""
    tags: Optional[List[str]] = []
    linked_provisions: Optional[List[str]] = []


class CaseNoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    linked_provisions: Optional[List[str]] = None


class CaseNoteResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    tags: Optional[List[str]]
    linked_provisions: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
