"""User model with role-based access control."""

import enum
from datetime import datetime, timezone

from sqlalchemy import String, Enum, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Role(str, enum.Enum):
    PUBLIC = "public"
    LAWYER = "lawyer"
    JUDGE = "judge"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.PUBLIC, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    language_pref: Mapped[str] = mapped_column(String(5), default="en", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    case_notes = relationship("CaseNote", back_populates="user", cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.email} role={self.role.value}>"
