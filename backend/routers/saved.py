"""Saved router — bookmarks, case notes, search history."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.dependencies import require_current_user, require_lawyer, require_judge
from backend.models.user import User, Role
from backend.models.bookmark import Bookmark
from backend.models.case_note import CaseNote
from backend.models.search_history import SearchHistory
from backend.schemas.bookmark import BookmarkCreate, BookmarkResponse
from backend.schemas.case_note import CaseNoteCreate, CaseNoteUpdate, CaseNoteResponse

router = APIRouter(prefix="/saved", tags=["Saved"])


# ── Bookmarks ──────────────────────────────────────────────────────────

@router.get("/bookmarks", response_model=List[BookmarkResponse])
async def list_bookmarks(
    user: User = Depends(require_lawyer),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bookmark).where(Bookmark.user_id == user.id).order_by(Bookmark.created_at.desc())
    )
    return [BookmarkResponse.model_validate(b) for b in result.scalars().all()]


@router.post("/bookmarks", response_model=BookmarkResponse, status_code=201)
async def create_bookmark(
    body: BookmarkCreate,
    user: User = Depends(require_lawyer),
    db: AsyncSession = Depends(get_db),
):
    bookmark = Bookmark(user_id=user.id, **body.model_dump())
    db.add(bookmark)
    await db.flush()
    await db.refresh(bookmark)
    return BookmarkResponse.model_validate(bookmark)


@router.delete("/bookmarks/{bookmark_id}", status_code=204)
async def delete_bookmark(
    bookmark_id: int,
    user: User = Depends(require_lawyer),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bookmark).where(Bookmark.id == bookmark_id, Bookmark.user_id == user.id)
    )
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    await db.delete(bookmark)


# ── Case Notes ─────────────────────────────────────────────────────────

@router.get("/notes", response_model=List[CaseNoteResponse])
async def list_notes(
    user: User = Depends(require_lawyer),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CaseNote).where(CaseNote.user_id == user.id).order_by(CaseNote.updated_at.desc())
    )
    return [CaseNoteResponse.model_validate(n) for n in result.scalars().all()]


@router.post("/notes", response_model=CaseNoteResponse, status_code=201)
async def create_note(
    body: CaseNoteCreate,
    user: User = Depends(require_lawyer),
    db: AsyncSession = Depends(get_db),
):
    note = CaseNote(user_id=user.id, **body.model_dump())
    db.add(note)
    await db.flush()
    await db.refresh(note)
    return CaseNoteResponse.model_validate(note)


@router.put("/notes/{note_id}", response_model=CaseNoteResponse)
async def update_note(
    note_id: int,
    body: CaseNoteUpdate,
    user: User = Depends(require_lawyer),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CaseNote).where(CaseNote.id == note_id, CaseNote.user_id == user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(note, field, value)

    await db.flush()
    await db.refresh(note)
    return CaseNoteResponse.model_validate(note)


@router.delete("/notes/{note_id}", status_code=204)
async def delete_note(
    note_id: int,
    user: User = Depends(require_lawyer),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CaseNote).where(CaseNote.id == note_id, CaseNote.user_id == user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    await db.delete(note)


# ── Search History ───────────────────────────────────────────────────

class SearchHistoryCreate(BaseModel):
    query: str
    country: Optional[str] = None
    category: Optional[str] = None
    results_count: int = 0


class SearchHistoryResponse(BaseModel):
    id: int
    query: str
    country: Optional[str]
    category: Optional[str]
    results_count: int
    timestamp: str

    model_config = {"from_attributes": True}


@router.get("/search-history", response_model=List[SearchHistoryResponse])
async def list_search_history(
    limit: int = 20,
    user: User = Depends(require_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SearchHistory)
        .where(SearchHistory.user_id == user.id)
        .order_by(SearchHistory.timestamp.desc())
        .limit(limit)
    )
    rows = result.scalars().all()
    return [
        SearchHistoryResponse(
            id=r.id, query=r.query, country=r.country,
            category=r.category, results_count=r.results_count,
            timestamp=r.timestamp.isoformat(),
        )
        for r in rows
    ]


@router.post("/search-history", response_model=SearchHistoryResponse, status_code=201)
async def create_search_history(
    body: SearchHistoryCreate,
    user: User = Depends(require_current_user),
    db: AsyncSession = Depends(get_db),
):
    entry = SearchHistory(user_id=user.id, **body.model_dump())
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return SearchHistoryResponse(
        id=entry.id, query=entry.query, country=entry.country,
        category=entry.category, results_count=entry.results_count,
        timestamp=entry.timestamp.isoformat(),
    )


@router.get("/search-suggestions", response_model=List[str])
async def search_suggestions(
    limit: int = 5,
    user: User = Depends(require_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SearchHistory.query, func.count(SearchHistory.id).label("cnt"))
        .where(SearchHistory.user_id == user.id)
        .group_by(SearchHistory.query)
        .order_by(func.count(SearchHistory.id).desc())
        .limit(limit)
    )
    return [row.query for row in result.all()]


@router.delete("/search-history/{history_id}", status_code=204)
async def delete_search_history(
    history_id: int,
    user: User = Depends(require_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SearchHistory).where(SearchHistory.id == history_id, SearchHistory.user_id == user.id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Search history entry not found")
    await db.delete(entry)
