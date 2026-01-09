"""DB models for pre-generated question bank (Option A).

These tables are intended to be the runtime source of truth:
- YAML is an authoring/import format.
- SessionAdapter should serve questions from these tables.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)

from db.base import Base


class QuestionBankItem(Base):
    __tablename__ = "question_bank_items"

    id = Column(String(36), primary_key=True)  # UUID

    # Partition keys
    chapter = Column(String(100), nullable=False, index=True)
    concept = Column(String(100), nullable=False, index=True)

    # Template tracking for "same concept, different numbers" feature
    template_id = Column(String(64), nullable=True, index=True)

    # Use int difficulty for now to match current mental model (1-5)
    difficulty = Column(Integer, nullable=False, index=True)

    # Keep bloom level as normalized uppercase string (REMEMBER/UNDERSTAND/...)
    bloom_level = Column(String(20), nullable=False, index=True)

    # Source of item
    source = Column(String(20), nullable=False, default="yaml")  # yaml|generated

    # Canonical question payload consumed by SessionAdapter/frontend
    payload = Column(JSON, nullable=False)

    # Operational flags
    active = Column(Boolean, nullable=False, default=True, index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index(
            "idx_qbank_lookup",
            "chapter",
            "concept",
            "difficulty",
            "bloom_level",
            "active",
        ),
    )


class ServedQuestion(Base):
    __tablename__ = "served_questions"

    id = Column(String(36), primary_key=True)  # UUID

    session_id = Column(String(36), nullable=False, index=True)
    student_id = Column(String(64), nullable=False, index=True)

    question_bank_item_id = Column(
        String(36), ForeignKey("question_bank_items.id"), nullable=False, index=True
    )

    served_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Answering
    answered_at = Column(DateTime, nullable=True, index=True)
    selected_index = Column(Integer, nullable=True)
    is_correct = Column(Boolean, nullable=True)

    __table_args__ = (
        Index("idx_served_session_student", "session_id", "student_id"),
    )
