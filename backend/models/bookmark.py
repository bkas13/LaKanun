"""Bookmark model — saved law provisions."""

from datetime import datetime, timezone

from sqlalchemy import String, ForeignKey, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provision_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(10), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=True)
    article_number: Mapped[str] = mapped_column(String(50), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=True)
    note: Mapped[str] = mapped_column(Text, nullable=True, default="")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user = relationship("User", back_populates="bookmarks")

    def __repr__(self) -> str:
        return f"<Bookmark {self.provision_id} by user={self.user_id}>"
