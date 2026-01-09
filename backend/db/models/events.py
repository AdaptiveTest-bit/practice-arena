"""Learning event log.

This is the debugging + analytics spine.
Keep payloads small; store references to large content separately.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Index, JSON, String

from db.base import Base


class LearningEvent(Base):
    __tablename__ = "learning_events"

    id = Column(String(36), primary_key=True)

    student_id = Column(String(64), nullable=False, index=True)
    session_id = Column(String(36), nullable=True, index=True)

    event_type = Column(String(40), nullable=False, index=True)  # SERVED/ANSWERED/HINT_USED/SESSION_ENDED
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Context for grouping/filtering
    subject = Column(String(32), nullable=True, index=True)
    chapter_key = Column(String(100), nullable=True, index=True)
    concept_id = Column(String(100), nullable=True, index=True)  # Extended for full concept IDs like "math.class5.factors_multiples.prime_composite"
    bloom_level = Column(String(20), nullable=True)
    difficulty = Column(String(20), nullable=True)

    served_question_id = Column(String(100), nullable=True, index=True)  # Extended for adaptive IDs like "adaptive_uuid_count"

    payload = Column(JSON, nullable=False, default=dict)

    __table_args__ = (
        Index("idx_events_student_time", "student_id", "timestamp"),
    )
