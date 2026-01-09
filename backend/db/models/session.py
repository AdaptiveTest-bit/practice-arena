"""DB models for SessionAdapter runtime sessions.

MVP goal: remove in-memory session state from SessionAdapter.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, JSON, String

from db.base import Base


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(String(36), primary_key=True)  # UUID
    student_id = Column(String(64), nullable=False, index=True)
    grade_level = Column(Integer, nullable=False)
    mode = Column(String(20), nullable=False, default="practice")
    chapter = Column(String(100), nullable=False)

    # Store light-weight session counters (avoid big JSON in MVP)
    attempted_count = Column(Integer, nullable=False, default=0)
    correct_count = Column(Integer, nullable=False, default=0)
    current_streak = Column(Integer, nullable=False, default=0)

    # Optional tracking
    chapter_transitions = Column(JSON, nullable=False, default=list)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    ended_at = Column(DateTime, nullable=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    __table_args__ = (
        Index("idx_quiz_sessions_student_active", "student_id", "is_active"),
    )
