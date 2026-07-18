"""SearchHistory model — tracks user search queries for recommendations."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class SearchHistory(Base):
    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query: Mapped[str] = mapped_column(String(1000), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    results_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user = relationship("User", back_populates="search_history")

    def __repr__(self) -> str:
        return f"<SearchHistory query='{self.query[:30]}' user={self.user_id}>"
