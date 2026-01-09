"""Question bank runtime service (Option A).

Purpose:
- Serve pre-generated questions from Postgres to SessionAdapter.
- Track which items were served per session/student.
- Avoid YAML parsing and generation on the student request path.
- Support "same concept, different question" for remediation.

This is intentionally simple and "boring".
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import and_, exists, not_, select

from core.database import SessionLocal
from db.models.question_bank import QuestionBankItem, ServedQuestion


class QuestionBankService:
    """Runtime service to fetch next unseen question from the bank."""

    def __init__(self):
        # NOTE: keep SessionLocal usage local to methods in case we later switch to DI.
        pass

    def get_next_unseen(
        self,
        *,
        session_id: str,
        student_id: str,
        chapter: str,
        concept: str = "general",
        difficulty: int = 1,
        bloom_level: str = "UNDERSTAND",
        exclude_item_id: Optional[str] = None,  # For "same concept, different question"
    ) -> dict:
        """Return a question payload and create a ServedQuestion record.

        Args:
            session_id: Current session ID
            student_id: Student ID
            chapter: Chapter key
            concept: Concept ID
            difficulty: Difficulty level (1-3)
            bloom_level: Bloom's taxonomy level
            exclude_item_id: Exclude this specific question (for retry scenarios)

        Raises:
            ValueError if no question is available.
        """
        bloom_level = str(bloom_level or "UNDERSTAND").strip().upper()

        with SessionLocal() as db:
            # Subquery: items already served in this session
            served_subq = (
                select(ServedQuestion.id)
                .where(
                    and_(
                        ServedQuestion.session_id == session_id,
                        ServedQuestion.question_bank_item_id == QuestionBankItem.id,
                    )
                )
                .exists()
            )

            # Base conditions
            conditions = [
                QuestionBankItem.active.is_(True),
                QuestionBankItem.chapter == chapter,
                QuestionBankItem.concept == concept,
                QuestionBankItem.difficulty == difficulty,
                QuestionBankItem.bloom_level == bloom_level,
                ~served_subq,
            ]

            # Exclude specific question if provided (for "same concept, different question")
            if exclude_item_id:
                conditions.append(QuestionBankItem.id != exclude_item_id)

            stmt = (
                select(QuestionBankItem)
                .where(and_(*conditions))
                .order_by(QuestionBankItem.created_at.asc())
                .limit(1)
            )

            item = db.execute(stmt).scalar_one_or_none()
            if not item:
                raise ValueError(
                    f"No bank question available for chapter={chapter}, concept={concept}, "
                    f"difficulty={difficulty}, bloom={bloom_level}. "
                    f"Import YAML / generate bank items first."
                )

            served = ServedQuestion(
                id=str(uuid.uuid4()),
                session_id=session_id,
                student_id=student_id,
                question_bank_item_id=item.id,
                served_at=datetime.utcnow(),
            )
            db.add(served)
            db.commit()

            # Return payload *and* stable ids for answer submission
            payload = dict(item.payload or {})
            payload["bank_item_id"] = item.id
            payload["served_id"] = served.id
            payload["template_id"] = item.template_id  # For tracking variations

            return payload

    def get_same_concept_different_question(
        self,
        *,
        session_id: str,
        student_id: str,
        last_wrong_item_id: str,
    ) -> dict:
        """
        Get a different question for the SAME concept after wrong answer.
        
        This is the key feature for effective learning:
        - Student answers wrong on "factors of 24"
        - Give them "factors of 36" (same concept, different numbers)
        - They practice until they understand, not memorize
        
        Args:
            session_id: Current session
            student_id: Student ID
            last_wrong_item_id: The question they got wrong
            
        Returns:
            Question payload for a different variation of the same concept
        """
        with SessionLocal() as db:
            # Get the last wrong question details
            wrong_item = db.get(QuestionBankItem, last_wrong_item_id)
            if not wrong_item:
                raise ValueError(f"Question {last_wrong_item_id} not found")
            
            # Find another question with:
            # - Same chapter
            # - Same concept
            # - Same or lower difficulty (don't make it harder after wrong)
            # - Not already served in this session
            served_subq = (
                select(ServedQuestion.id)
                .where(
                    and_(
                        ServedQuestion.session_id == session_id,
                        ServedQuestion.question_bank_item_id == QuestionBankItem.id,
                    )
                )
                .exists()
            )

            stmt = (
                select(QuestionBankItem)
                .where(
                    and_(
                        QuestionBankItem.active.is_(True),
                        QuestionBankItem.chapter == wrong_item.chapter,
                        QuestionBankItem.concept == wrong_item.concept,
                        QuestionBankItem.difficulty <= wrong_item.difficulty,
                        QuestionBankItem.id != last_wrong_item_id,
                        ~served_subq,
                    )
                )
                .order_by(QuestionBankItem.difficulty.asc(), QuestionBankItem.created_at.asc())
                .limit(1)
            )

            item = db.execute(stmt).scalar_one_or_none()
            if not item:
                # Fallback: get ANY unseen question in this chapter
                fallback_stmt = (
                    select(QuestionBankItem)
                    .where(
                        and_(
                            QuestionBankItem.active.is_(True),
                            QuestionBankItem.chapter == wrong_item.chapter,
                            QuestionBankItem.id != last_wrong_item_id,
                            ~served_subq,
                        )
                    )
                    .order_by(QuestionBankItem.difficulty.asc())
                    .limit(1)
                )
                item = db.execute(fallback_stmt).scalar_one_or_none()
                
            if not item:
                raise ValueError(
                    f"No alternative question available for concept={wrong_item.concept}. "
                    f"Generate more variations."
                )

            served = ServedQuestion(
                id=str(uuid.uuid4()),
                session_id=session_id,
                student_id=student_id,
                question_bank_item_id=item.id,
                served_at=datetime.utcnow(),
            )
            db.add(served)
            db.commit()

            payload = dict(item.payload or {})
            payload["bank_item_id"] = item.id
            payload["served_id"] = served.id
            payload["template_id"] = item.template_id
            payload["retry_for_concept"] = wrong_item.concept

            return payload

    def mark_answered(
        self,
        *,
        served_id: str,
        selected_index: int,
        is_correct: bool,
    ) -> None:
        with SessionLocal() as db:
            served = db.get(ServedQuestion, served_id)
            if not served:
                raise ValueError("served_id not found")
            served.answered_at = datetime.utcnow()
            served.selected_index = int(selected_index)
            served.is_correct = bool(is_correct)
            db.commit()

    def get_served_with_item(self, *, served_id: str) -> tuple[ServedQuestion, QuestionBankItem]:
        """Load ServedQuestion and its linked QuestionBankItem.

        Used by SessionAdapter answer submission so we don't rely on in-memory caches.
        """
        with SessionLocal() as db:
            served = db.get(ServedQuestion, served_id)
            if not served:
                raise ValueError("served_id not found")

            item = db.get(QuestionBankItem, served.question_bank_item_id)
            if not item:
                raise ValueError("question_bank_item_id not found for served_id")

            # Returned objects are detached on context exit; SessionAdapter only reads fields.
            return served, item

    def get_correct_index_from_payload(self, *, payload: dict) -> int:
        """Best-effort extraction of the correct option index from a bank payload."""
        # SessionAdapter legacy expects an int index. Prefer the canonical field set by generators.
        for key in ("correct_option_index", "correctAnswerId", "correct_answer_id"):
            if key in payload and payload[key] is not None:
                try:
                    return int(payload[key])
                except (TypeError, ValueError):
                    pass
        return 0
