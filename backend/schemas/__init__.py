"""Pydantic schemas package."""

from backend.schemas.auth import TokenResponse, RegisterRequest, LoginRequest
from backend.schemas.user import UserResponse, UserUpdate
from backend.schemas.law import LawSearchRequest, LawSearchResult, LawSearchResponse, LawDetail
from backend.schemas.bookmark import BookmarkCreate, BookmarkResponse
from backend.schemas.case_note import CaseNoteCreate, CaseNoteUpdate, CaseNoteResponse

__all__ = [
    "TokenResponse", "RegisterRequest", "LoginRequest",
    "UserResponse", "UserUpdate",
    "LawSearchRequest", "LawSearchResult", "LawSearchResponse", "LawDetail",
    "BookmarkCreate", "BookmarkResponse",
    "CaseNoteCreate", "CaseNoteUpdate", "CaseNoteResponse",
]
