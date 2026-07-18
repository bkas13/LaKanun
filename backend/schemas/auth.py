"""Auth request/response schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: "UserBrief"


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class UserBrief(BaseModel):
    id: int
    email: str
    name: str
    role: str
    language_pref: str

    class Config:
        from_attributes = True
