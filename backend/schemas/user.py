"""User request/response schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    is_active: bool
    language_pref: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    language_pref: Optional[str] = Field(None, pattern="^(en|ne|hi)$")


class AdminUserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    role: Optional[str] = Field(None, pattern="^(public|lawyer|judge|admin)$")
    is_active: Optional[bool] = None
    language_pref: Optional[str] = Field(None, pattern="^(en|ne|hi)$")
