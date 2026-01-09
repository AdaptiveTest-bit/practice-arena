"""Scheduler service (Leitner + breakpoints) for concept selection.

Design:
- Select concept_id first (due/breakpoint priority)
- Bloom is derived later (UX), not a scheduling key.
- Supports "same concept after wrong" for remediation.

MVP assumptions:
- student_id is a stable string.
- concept_catalog contains the chapter roadmap.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import and_, select

from core.database import SessionLocal
from db.models.concepts import ConceptCatalog, StudentBreakpoint, StudentConceptState


@dataclass(frozen=True)
class ScheduledConcept:
    concept_id: str
    reason: str  # breakpoint|due|new|wrong_retry|fallback
    force_same_concept: bool = False  # If True, prioritize same concept after wrong answer


class SchedulerService:
    """Pick next concept to serve.
    
    Supports:
    - Leitner spaced repetition
    - Breakpoint priority
    - Same-concept retry after wrong answer
    """

    # Simple Leitner intervals (tweak later)
    LEITNER_INTERVALS_DAYS = {
        1: 1,
        2: 3,
        3: 7,
        4: 14,
        5: 30,
    }

    def pick_next_concept(
        self,
        *,
        student_id: str,
        chapter_key: str,
        now: datetime | None = None,
        last_wrong_concept: Optional[str] = None,
    ) -> ScheduledConcept:
        """
        Pick next concept to serve.
        
        Args:
            student_id: Student ID
            chapter_key: Chapter key (e.g., "factors_multiples")
            now: Current time (for testing)
            last_wrong_concept: If provided, prioritize this concept for retry
            
        Returns:
            ScheduledConcept with concept_id and reason
        """
        now = now or datetime.utcnow()

        # Priority 0: If student just got a concept wrong, give them another question
        # on the SAME concept (with different numbers)
        if last_wrong_concept:
            return ScheduledConcept(
                concept_id=str(last_wrong_concept),
                reason="wrong_retry",
                force_same_concept=True,
            )

        with SessionLocal() as db:
            # 1) Active breakpoints in this chapter (highest severity first)
            bp_stmt = (
                select(StudentBreakpoint.concept_id)
                .select_from(StudentBreakpoint)
                .join(
                    ConceptCatalog,
                    and_(
                        ConceptCatalog.concept_id == StudentBreakpoint.concept_id,
                        ConceptCatalog.chapter_key == chapter_key,
                        ConceptCatalog.active.is_(True),
                    ),
                )
                .where(
                    and_(
                        StudentBreakpoint.student_id == str(student_id),
                        StudentBreakpoint.active.is_(True),
                    )
                )
                .order_by(StudentBreakpoint.severity.desc(), StudentBreakpoint.updated_at.desc())
                .limit(1)
            )
            bp_concept = db.execute(bp_stmt).scalar_one_or_none()
            if bp_concept:
                return ScheduledConcept(concept_id=str(bp_concept), reason="breakpoint")

            # 2) Due concepts (due_at <= now) in this chapter
            due_stmt = (
                select(StudentConceptState.concept_id)
                .select_from(StudentConceptState)
                .join(
                    ConceptCatalog,
                    and_(
                        ConceptCatalog.concept_id == StudentConceptState.concept_id,
                        ConceptCatalog.chapter_key == chapter_key,
                        ConceptCatalog.active.is_(True),
                    ),
                )
                .where(
                    and_(
                        StudentConceptState.student_id == str(student_id),
                        StudentConceptState.due_at <= now,
                    )
                )
                .order_by(StudentConceptState.due_at.asc(), StudentConceptState.leitner_box.asc())
                .limit(1)
            )
            due_concept = db.execute(due_stmt).scalar_one_or_none()
            if due_concept:
                return ScheduledConcept(concept_id=str(due_concept), reason="due")

            # 3) New concept: next in chapter roadmap that student has never seen
            seen_subq = (
                select(StudentConceptState.concept_id)
                .where(StudentConceptState.student_id == str(student_id))
                .subquery()
            )

            new_stmt = (
                select(ConceptCatalog.concept_id)
                .where(
                    and_(
                        ConceptCatalog.chapter_key == chapter_key,
                        ConceptCatalog.active.is_(True),
                        ~ConceptCatalog.concept_id.in_(select(seen_subq.c.concept_id)),
                    )
                )
                .order_by(ConceptCatalog.order_index.asc())
                .limit(1)
            )
            new_concept = db.execute(new_stmt).scalar_one_or_none()
            if new_concept:
                return ScheduledConcept(concept_id=str(new_concept), reason="new")

            # 4) Fallback: earliest due concept even if not yet due
            any_stmt = (
                select(StudentConceptState.concept_id)
                .select_from(StudentConceptState)
                .join(
                    ConceptCatalog,
                    and_(
                        ConceptCatalog.concept_id == StudentConceptState.concept_id,
                        ConceptCatalog.chapter_key == chapter_key,
                        ConceptCatalog.active.is_(True),
                    ),
                )
                .where(StudentConceptState.student_id == str(student_id))
                .order_by(StudentConceptState.due_at.asc())
                .limit(1)
            )
            any_concept = db.execute(any_stmt).scalar_one_or_none()
            if any_concept:
                return ScheduledConcept(concept_id=str(any_concept), reason="fallback")

        raise ValueError(f"No concepts found for chapter_key={chapter_key}. Seed concept_catalog first.")

    def compute_next_due_at(self, *, leitner_box: int, now: datetime | None = None) -> datetime:
        now = now or datetime.utcnow()
        days = int(self.LEITNER_INTERVALS_DAYS.get(int(leitner_box), 1))
        return now + timedelta(days=days)
