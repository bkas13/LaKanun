"""Auth router — register, login, refresh, me."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, TokenRefreshRequest, UserBrief
from backend.services import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    try:
        user = await svc.register(body.email, body.name, body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    tokens = svc.create_tokens(user)
    return TokenResponse(**tokens, user=UserBrief.model_validate(user))


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    try:
        user = await svc.authenticate(body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    tokens = svc.create_tokens(user)
    return TokenResponse(**tokens, user=UserBrief.model_validate(user))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    try:
        tokens = await svc.refresh(body.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    # Re-fetch user for response
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == int(tokens["access_token"].split(".")[0] if False else 0)))
    # Simplified: decode the token to get user_id
    from backend.utils import decode_token
    payload = decode_token(tokens["access_token"])
    user_result = await db.execute(select(User).where(User.id == int(payload["sub"])))
    user = user_result.scalar_one()

    return TokenResponse(**tokens, user=UserBrief.model_validate(user))


@router.get("/me", response_model=UserBrief)
async def me(current_user: User = Depends(get_current_user)):
    return UserBrief.model_validate(current_user)
