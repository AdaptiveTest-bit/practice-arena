"""ORM-based Student Repository - Database Implementation

Replaces in-memory storage with PostgreSQL backend using SQLAlchemy ORM.
"""

from typing import Dict, Optional, List, Tuple, Any
from datetime import datetime, date, timedelta
import uuid

# Use the single, shared database session/engine
from core.database import SessionLocal

# NOTE: The legacy `backend/database.py` module defined its own engine + models.
# That caused dual-DB drift and multi-worker inconsistencies.
# The production codebase should use `backend/core/database.py` + `backend/db/models/*`.
from db.models.session import QuizSession

from api.models.student_progress import StudentProgress, AttemptResult, MisconceptionEncounter
from api.models.distractor import MisconceptionType
from api.models.cognitive_levels import BloomLevel


# Legacy imports (for backward compatibility - will be removed)
StudentMastery = None
QuestionAttempt = None
StudentProgressRecord = None
Chapter = None
get_session = SessionLocal


class ORMStudentRepository:
    """ORM-based Repository for StudentProgress data persistence using PostgreSQL.

    Week-1 scope: keep this repository *minimal* and aligned with the
    DB-backed session system (QuizSession + served_questions + learning_events).

    Anything that depended on legacy analytics models in `backend/database.py`
    is intentionally removed to avoid dual-engine drift.
    """

    def __init__(self, db_session: Optional[Any] = None):
        """Initialize repository with database session."""
        self.db = db_session or get_session()

    # ============================================================================
    # STUDENT VIEW (minimal)
    # ============================================================================

    def get_student(self, student_id: str) -> Optional[StudentProgress]:
        """Return a minimal StudentProgress view from DB-backed quiz session counters.

        This avoids relying on the legacy analytics schema in `backend/database.py`.
        """
        try:
            # Aggregate from QuizSession rows for this student.
            rows = (
                self.db.query(QuizSession)
                .filter(QuizSession.student_id == str(student_id))
                .all()
            )
            if not rows:
                return None

            total_attempts = sum(int(r.attempted_count or 0) for r in rows)
            total_correct = sum(int(r.correct_count or 0) for r in rows)

            overall_percentage = ((total_correct / total_attempts) * 100) if total_attempts > 0 else 0.0

            # Use last active session chapter as current chapter
            active = next((r for r in rows if bool(r.is_active)), None)
            last = active or sorted(rows, key=lambda r: r.created_at or datetime.min)[-1]

            bloom_level = self._calculate_bloom_level(total_correct, total_attempts)

            return StudentProgress(
                student_id=str(student_id),
                chapter=str(getattr(last, "chapter", "")) or "",
                current_bloom_level=str(bloom_level).lower(),
                total_attempts=total_attempts,
                total_correct=total_correct,
                overall_percentage=overall_percentage,
            )
        except Exception:
            return None

    # ============================================================================
    # SESSION LOOKUP (compat for legacy hint fallback)
    # ============================================================================

    def get_session(self, session_id: int):
        """Legacy compatibility method.

        The modern code uses `db.models.session.QuizSession` (UUID string ids).
        Some older fallback code paths attempted to fetch an integer session.

        Week-1: return None to force callers onto the DB-first QuizSession paths.
        """
        return None

    def close(self):
        """Close database session."""
        try:
            self.db.close()
        except Exception:
            pass

    # ============================================================================
    # STUDENT REGISTRATION
    # ============================================================================

    def register_student(self, name: str, chapter: str = "large_numbers") -> Dict[str, Any]:
        """Register a new student and return their ID.

        This creates a minimal student record by creating an initial (inactive) session
        placeholder, since students are identified by their quiz session history.

        Args:
            name: Student's name
            chapter: Initial chapter (defaults to large_numbers)

        Returns:
            Dict with studentId, name, chapter keys
        """
        try:
            student_id = str(uuid.uuid4())

            # Create an initial placeholder session (inactive) to register the student
            # This ensures the student exists in the system and can be looked up later
            placeholder_session = QuizSession(
                id=str(uuid.uuid4()),
                student_id=student_id,
                grade_level=5,  # Default grade level
                mode="practice",
                chapter=chapter,
                attempted_count=0,
                correct_count=0,
                current_streak=0,
                chapter_transitions=[],
                is_active=False,  # Placeholder, not an active session
            )

            with SessionLocal() as db:
                db.add(placeholder_session)
                db.commit()

            return {
                "success": True,
                "studentId": student_id,
                "name": name,
                "chapter": chapter,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


# Global repository instance
_repository_instance: Optional[ORMStudentRepository] = None


def get_repository() -> ORMStudentRepository:
    """Get or create global repository instance"""
    global _repository_instance
    
    if _repository_instance is None:
        _repository_instance = ORMStudentRepository()
    
    return _repository_instance


def reset_repository():
    """Reset repository instance (useful for testing)"""
    global _repository_instance
    if _repository_instance:
        _repository_instance.close()
    _repository_instance = None
