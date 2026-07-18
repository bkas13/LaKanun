"""Auth service — register, login, refresh."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User, Role
from backend.utils import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from backend.config import settings


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, email: str, name: str, password: str) -> User:
        """Create a new user. Raises ValueError on duplicate email."""
        existing = await self.db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            raise ValueError("Email already registered")

        user = User(
            email=email,
            name=name,
            hashed_password=hash_password(password),
            role=Role.PUBLIC,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> User:
        """Verify credentials. Raises ValueError on failure."""
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is deactivated")

        return user

    def create_tokens(self, user: User) -> dict:
        """Generate access + refresh token pair."""
        payload = {"sub": str(user.id), "role": user.role.value}
        access = create_access_token(payload)
        refresh = create_refresh_token(payload)
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
        }

    async def refresh(self, refresh_token: str) -> dict:
        """Validate refresh token and return new token pair."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        user_id = payload.get("sub")
        result = await self.db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        return self.create_tokens(user)
