"""Feedback router — search feedback + general user feedback."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.database import get_db
from backend.dependencies import optional_user
from backend.models.user import User
from backend.models.feedback import SearchFeedback, GeneralFeedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=64)
    query: str = Field(..., min_length=1, max_length=500)
    result_id: str
    result_title: Optional[str] = None
    result_country: Optional[str] = None
    result_category: Optional[str] = None
    result_score: Optional[float] = None
    position: Optional[int] = None
    feedback: str = Field(..., pattern="^(up|down)$")


class ClickRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=64)
    query: str = Field(..., min_length=1, max_length=500)
    result_id: str
    result_title: Optional[str] = None
    result_country: Optional[str] = None
    result_category: Optional[str] = None
    result_score: Optional[float] = None
    position: Optional[int] = None


@router.post("/vote")
async def vote_feedback(
    req: FeedbackRequest,
    user: Optional[User] = Depends(optional_user),
    db: AsyncSession = Depends(get_db),
):
    existing = (
        await db.execute(
            select(SearchFeedback).where(
                SearchFeedback.session_id == req.session_id,
                SearchFeedback.result_id == req.result_id,
                SearchFeedback.query == req.query,
                SearchFeedback.feedback.isnot(None),
            )
        )
    ).scalar_one_or_none()

    if existing:
        existing.feedback = req.feedback
        existing.created_at = datetime.utcnow()
    else:
        fb = SearchFeedback(
            user_id=user.id if user else None,
            session_id=req.session_id,
            query=req.query,
            result_id=req.result_id,
            result_title=req.result_title,
            result_country=req.result_country,
            result_category=req.result_category,
            result_score=req.result_score,
            position=req.position,
            feedback=req.feedback,
        )
        db.add(fb)

    await db.commit()
    return {"ok": True, "feedback": req.feedback}


@router.post("/click")
async def track_click(
    req: ClickRequest,
    user: Optional[User] = Depends(optional_user),
    db: AsyncSession = Depends(get_db),
):
    fb = SearchFeedback(
        user_id=user.id if user else None,
        session_id=req.session_id,
        query=req.query,
        result_id=req.result_id,
        result_title=req.result_title,
        result_country=req.result_country,
        result_category=req.result_category,
        result_score=req.result_score,
        position=req.position,
        clicked=True,
        clicked_at=datetime.utcnow(),
    )
    db.add(fb)
    await db.commit()
    return {"ok": True}


@router.get("/stats")
async def feedback_stats(
    db: AsyncSession = Depends(get_db),
):
    total = (await db.execute(select(func.count(SearchFeedback.id)))).scalar() or 0
    upvotes = (await db.execute(
        select(func.count(SearchFeedback.id)).where(SearchFeedback.feedback == "up")
    )).scalar() or 0
    downvotes = (await db.execute(
        select(func.count(SearchFeedback.id)).where(SearchFeedback.feedback == "down")
    )).scalar() or 0
    clicks = (await db.execute(
        select(func.count(SearchFeedback.id)).where(SearchFeedback.clicked == True)
    )).scalar() or 0

    return {
        "total_feedback": total,
        "upvotes": upvotes,
        "downvotes": downvotes,
        "clicks": clicks,
    }


class GeneralFeedbackRequest(BaseModel):
    feedback_type: str = Field(..., pattern="^(ui|general|objection|bug|suggestion)$")
    subject: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=10, max_length=5000)
    email: Optional[str] = Field(None, max_length=200)
    page_url: Optional[str] = Field(None, max_length=500)
    locale: Optional[str] = Field(None, max_length=10)
    session_id: Optional[str] = Field(None, max_length=64)


@router.post("/submit")
async def submit_general_feedback(
    req: GeneralFeedbackRequest,
    user: Optional[User] = Depends(optional_user),
    db: AsyncSession = Depends(get_db),
):
    fb = GeneralFeedback(
        user_id=user.id if user else None,
        session_id=req.session_id,
        feedback_type=req.feedback_type,
        subject=req.subject,
        message=req.message,
        email=req.email,
        page_url=req.page_url,
        locale=req.locale,
    )
    db.add(fb)
    await db.commit()
    return {"ok": True, "id": fb.id}


@router.get("/all")
async def list_all_feedback(
    user: User = Depends(optional_user),
    db: AsyncSession = Depends(get_db),
):
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    result = await db.execute(
        select(GeneralFeedback).order_by(GeneralFeedback.created_at.desc()).limit(100)
    )
    rows = result.scalars().all()

    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "feedback_type": r.feedback_type,
            "subject": r.subject,
            "message": r.message,
            "email": r.email,
            "page_url": r.page_url,
            "locale": r.locale,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
