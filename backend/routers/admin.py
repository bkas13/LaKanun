"""Admin router — user management, analytics, audit logs."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.dependencies import require_admin
from backend.models.user import User, Role
from backend.models.audit import AuditLog
from backend.schemas.user import UserResponse, AdminUserUpdate

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    role: Optional[str] = Query(None, pattern="^(public|lawyer|judge|admin)$"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)
    if role:
        query = query.where(User.role == Role(role))
    result = await db.execute(query)
    return [UserResponse.model_validate(u) for u in result.scalars().all()]


@router.get("/users/count")
async def user_count(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(func.count(User.id)))
    total = result.scalar()
    by_role = {}
    for r in Role:
        result = await db.execute(select(func.count(User.id)).where(User.role == r))
        by_role[r.value] = result.scalar()
    return {"total": total, "by_role": by_role}


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    body: AdminUserUpdate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        if field == "role":
            setattr(user, field, Role(value))
        else:
            setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.get("/audit", response_model=List[dict])
async def list_audit_logs(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AuditLog).order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit)
    )
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "timestamp": log.timestamp.isoformat(),
        }
        for log in logs
    ]


@router.get("/stats")
async def corpus_stats(
    _admin: User = Depends(require_admin),
):
    from backend.services.law import law_service
    law_service._ensure_loaded()
    from collections import Counter
    countries = Counter(a.get("country") for a in law_service._articles)
    doc_types = Counter(a.get("document_type") for a in law_service._articles)
    categories = Counter(a.get("category") for a in law_service._articles)
    return {
        "total_provisions": len(law_service._articles),
        "by_country": dict(countries),
        "by_document_type": dict(doc_types),
        "by_category": dict(categories.most_common(20)),
    }
