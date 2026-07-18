"""Feedback models — search feedback + general user feedback."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from backend.database import Base


class SearchFeedback(Base):
    __tablename__ = "search_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    session_id = Column(String(64), nullable=False, index=True)

    query = Column(String(500), nullable=False)
    result_id = Column(String(200), nullable=False)
    result_title = Column(String(500), nullable=True)
    result_country = Column(String(20), nullable=True)
    result_category = Column(String(100), nullable=True)
    result_score = Column(Float, nullable=True)
    position = Column(Integer, nullable=True)

    feedback = Column(String(10), nullable=True)
    clicked = Column(Boolean, default=False)
    clicked_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class GeneralFeedback(Base):
    __tablename__ = "general_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    session_id = Column(String(64), nullable=True, index=True)

    feedback_type = Column(String(50), nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    email = Column(String(200), nullable=True)
    page_url = Column(String(500), nullable=True)
    locale = Column(String(10), nullable=True)

    status = Column(String(20), default="new")
    admin_reply = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
