"""Concept taxonomy and spaced repetition state (Leitner).

MVP principles:
- Concept identity is curated (concept_id) and stable across time.
- Leitner is concept-level only: (student_id, concept_id).
- Bloom level is treated as UX/progression metadata, not the core SR key.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String, Text

from db.base import Base


class ConceptCatalog(Base):
    __tablename__ = "concept_catalog"

    concept_id = Column(String(64), primary_key=True)  # e.g. MATH_C05_CH05_C001

    subject = Column(String(32), nullable=False, index=True)  # math/science
    grade_level = Column(Integer, nullable=False, index=True)
    chapter_key = Column(String(100), nullable=False, index=True)  # canonical

    order_index = Column(Integer, nullable=False, default=0, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    active = Column(Boolean, nullable=False, default=True, index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_concept_catalog_chapter_order", "chapter_key", "order_index"),
    )


class StudentConceptState(Base):
    __tablename__ = "student_concept_state"

    # Composite PK (simple, fast)
    student_id = Column(String(64), primary_key=True)
    concept_id = Column(String(64), primary_key=True)

    leitner_box = Column(Integer, nullable=False, default=1, index=True)  # 1..5

    due_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    last_seen_at = Column(DateTime, nullable=True, index=True)

    attempts = Column(Integer, nullable=False, default=0)
    correct = Column(Integer, nullable=False, default=0)

    # UX continuity only (optional)
    last_bloom_served = Column(String(20), nullable=True)

    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_student_concept_due", "student_id", "due_at"),
        Index("idx_student_concept_box", "student_id", "leitner_box"),
    )


class StudentBreakpoint(Base):
    __tablename__ = "student_breakpoints"

    student_id = Column(String(64), primary_key=True)
    concept_id = Column(String(64), primary_key=True)

    severity = Column(Integer, nullable=False, default=1, index=True)  # 1..5
    reason = Column(String(64), nullable=False, default="LOW_ACCURACY")
    wrong_streak = Column(Integer, nullable=False, default=0)

    active = Column(Boolean, nullable=False, default=True, index=True)

    last_triggered_at = Column(DateTime, nullable=True, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_breakpoints_student_active", "student_id", "active"),
    )
