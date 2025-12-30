"""ORM-based Student Repository - Database Implementation

Replaces in-memory storage with PostgreSQL backend using SQLAlchemy ORM.
"""

from typing import Dict, Optional, List, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import uuid

# Import Phase 1 database models
from database import SessionLocal, PracticeSession, StudentSessionState, get_practice_session
from models.student_progress import StudentProgress, AttemptResult, MisconceptionEncounter
from models.distractor import MisconceptionType
from models.cognitive_levels import BloomLevel


# Legacy imports (for backward compatibility - will be refactored in Phase 3)
try:
    from database import Student, StudentMastery, QuestionAttempt, StudentProgressRecord, Chapter, get_session
except ImportError:
    # These old models don't exist in Phase 1 database, using placeholder
    Student = None
    StudentMastery = None
    QuestionAttempt = None
    StudentProgressRecord = None
    Chapter = None
    get_session = SessionLocal


class ORMStudentRepository:
    """ORM-based Repository for StudentProgress data persistence using PostgreSQL."""
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize repository with database session.
        
        Args:
            db_session: SQLAlchemy session (if None, creates new one)
        """
        self.db = db_session or get_session()
    
    # ============================================================================
    # STUDENT PROFILE OPERATIONS
    # ============================================================================
    
    def create_student(self, student_name: str, chapter: str = "Ch1: The Fish Tale") -> str:
        """
        Create a new student profile in database.
        
        Args:
            student_name: Name of the student
            chapter: Starting chapter (default: Ch1)
            
        Returns:
            student_id (UUID string)
        """
        try:
            user_id = str(uuid.uuid4())
            
            # Create student in database
            student = Student(
                user_id=user_id,
                email=f"{student_name.lower().replace(' ', '.')}_{user_id[:8]}@edtech.local",
                name=student_name,
                total_xp=0,
                current_streak=0,
                best_streak=0,
                created_at=datetime.utcnow()
            )
            
            self.db.add(student)
            self.db.commit()
            self.db.refresh(student)
            
            print(f"✅ Student created in database: {student_name} (ID: {student.id})")
            return str(student.id)
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error creating student: {e}")
            raise
    
    def get_student(self, student_id: str) -> Optional[StudentProgress]:
        """
        Get student profile by ID.
        
        Args:
            student_id: Student ID (database ID)
            
        Returns:
            StudentProgress object or None
        """
        try:
            student = self.db.query(Student).filter(Student.id == int(student_id)).first()
            
            if not student:
                return None
            
            # Get chapter info
            chapter_name = self._get_current_chapter(student.id)
            
            # Get progress
            attempts = self.db.query(QuestionAttempt).filter(
                QuestionAttempt.student_id == student.id
            ).all()
            
            correct_count = len([a for a in attempts if a.is_correct])
            
            # Calculate Bloom level (returns lowercase enum value)
            bloom_level = self._calculate_bloom_level(correct_count, len(attempts))
            # Convert to lowercase for enum
            bloom_level_lower = bloom_level.lower()
            
            return StudentProgress(
                student_id=str(student.id),
                chapter=chapter_name,
                total_attempts=len(attempts),
                total_correct=correct_count,
                overall_percentage=(correct_count / len(attempts) * 100) if attempts else 0.0,
                current_bloom_level=bloom_level_lower
            )
            
        except Exception as e:
            print(f"❌ Error getting student: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def record_attempt(
        self,
        student_id: str,
        question_id: int,
        concept_id: int,
        chapter_id: int,
        is_correct: bool,
        selected_option: Optional[str] = None,
        difficulty_level: int = 1,
        time_taken_seconds: Optional[int] = None
    ) -> str:
        """
        Record a question attempt in database.
        
        Args:
            student_id: Student ID
            question_id: Question ID
            concept_id: Concept ID
            chapter_id: Chapter ID
            is_correct: Whether answer was correct
            selected_option: Selected option (A, B, C, D)
            difficulty_level: Difficulty level (1-3)
            time_taken_seconds: Time taken in seconds
            
        Returns:
            attempt_id
        """
        try:
            was_guess = time_taken_seconds and time_taken_seconds < 5
            
            attempt = QuestionAttempt(
                student_id=int(student_id),
                question_id=question_id,
                concept_id=concept_id,
                chapter_id=chapter_id,
                is_correct=is_correct,
                selected_option=selected_option,
                difficulty_attempted=difficulty_level,
                time_taken_seconds=time_taken_seconds,
                was_guess=was_guess or False,
                answered_at=datetime.utcnow()
            )
            
            self.db.add(attempt)
            self.db.commit()
            self.db.refresh(attempt)
            
            # Update student progress for chapter
            self._update_chapter_progress(int(student_id), chapter_id, is_correct)
            
            # Update mastery score for concept
            self._update_mastery(int(student_id), concept_id, is_correct)
            
            return str(attempt.id)
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error recording attempt: {e}")
            raise
    
    # ============================================================================
    # MISCONCEPTION & PERFORMANCE TRACKING
    # ============================================================================
    
    def _get_misconceptions(self, student_id: int) -> List[str]:
        """Get list of misconception types encountered by student"""
        try:
            mistakes = self.db.query(QuestionAttempt.mistake_type).filter(
                QuestionAttempt.student_id == student_id,
                QuestionAttempt.is_correct == False,
                QuestionAttempt.mistake_type != None
            ).distinct().all()
            
            return [m[0] for m in mistakes if m[0]]
            
        except Exception as e:
            print(f"❌ Error getting misconceptions: {e}")
            return []
    
    def _calculate_bloom_level(self, correct: int, total: int) -> str:
        """Calculate Bloom's taxonomy level based on accuracy"""
        if total == 0:
            return "Remember"
        
        accuracy = correct / total
        
        if accuracy < 0.4:
            return "remember"
        elif accuracy < 0.55:
            return "understand"
        elif accuracy < 0.7:
            return "apply"
        elif accuracy < 0.85:
            return "analyze"
        elif accuracy < 0.95:
            return "evaluate"
        else:
            return "create"
    
    def _get_current_chapter(self, student_id: int) -> str:
        """Get the most recent chapter the student worked on"""
        try:
            attempt = self.db.query(QuestionAttempt).filter(
                QuestionAttempt.student_id == student_id
            ).order_by(desc(QuestionAttempt.answered_at)).first()
            
            if attempt:
                chapter = self.db.query(Chapter).filter(
                    Chapter.id == attempt.chapter_id
                ).first()
                return chapter.name if chapter else "Unknown"
            
            return "Ch1: The Fish Tale"
            
        except Exception as e:
            print(f"❌ Error getting current chapter: {e}")
            return "Ch1: The Fish Tale"
    
    def _update_chapter_progress(self, student_id: int, chapter_id: int, is_correct: bool):
        """Update chapter-level progress"""
        try:
            progress = self.db.query(StudentProgressRecord).filter(
                StudentProgressRecord.user_id == student_id,
                StudentProgressRecord.chapter_id == chapter_id
            ).first()
            
            if not progress:
                progress = StudentProgressRecord(
                    user_id=student_id,
                    chapter_id=chapter_id,
                    mastery_score=0,
                    questions_completed=0,
                    questions_correct=0,
                    created_at=datetime.utcnow()
                )
                self.db.add(progress)
            
            progress.questions_completed += 1
            if is_correct:
                progress.questions_correct += 1
            
            progress.mastery_score = (progress.questions_correct / progress.questions_completed) * 100 if progress.questions_completed > 0 else 0
            progress.last_answered_at = datetime.utcnow()
            progress.updated_at = datetime.utcnow()
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error updating chapter progress: {e}")
    
    def _update_mastery(self, student_id: int, concept_id: int, is_correct: bool):
        """Update concept mastery using EMA algorithm"""
        try:
            mastery = self.db.query(StudentMastery).filter(
                StudentMastery.user_id == student_id,
                StudentMastery.concept_id == concept_id
            ).first()
            
            if not mastery:
                mastery = StudentMastery(
                    user_id=student_id,
                    concept_id=concept_id,
                    mastery_score=0.0,
                    leitner_box=1,
                    next_review_date=date.today(),
                    last_practiced_at=datetime.utcnow()
                )
                self.db.add(mastery)
            
            # EMA calculation: alpha = 0.3
            alpha = 0.3
            current_score = 1.0 if is_correct else 0.0
            mastery.mastery_score = alpha * current_score + (1 - alpha) * mastery.mastery_score
            mastery.last_practiced_at = datetime.utcnow()
            
            # Update Leitner box based on mastery score
            if mastery.mastery_score > 0.8:
                mastery.leitner_box = 4
                mastery.next_review_date = date.today() + timedelta(days=30)
            elif mastery.mastery_score > 0.6:
                mastery.leitner_box = 3
                mastery.next_review_date = date.today() + timedelta(days=7)
            elif mastery.mastery_score > 0.4:
                mastery.leitner_box = 2
                mastery.next_review_date = date.today() + timedelta(days=3)
            else:
                mastery.leitner_box = 1
                mastery.next_review_date = date.today() + timedelta(days=1)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error updating mastery: {e}")
    
    # ============================================================================
    # QUERY OPERATIONS
    # ============================================================================
    
    def get_all_students(self) -> List[StudentProgress]:
        """Get all registered students"""
        try:
            students = self.db.query(Student).all()
            results = []
            
            for student in students:
                progress = self.get_student(str(student.id))
                if progress:
                    results.append(progress)
            
            return results
            
        except Exception as e:
            print(f"❌ Error getting all students: {e}")
            return []
    
    def get_student_statistics(self, student_id: str) -> Dict:
        """Get detailed statistics for a student"""
        try:
            student = self.db.query(Student).filter(Student.id == int(student_id)).first()
            
            if not student:
                return {}
            
            attempts = self.db.query(QuestionAttempt).filter(
                QuestionAttempt.student_id == student.id
            ).all()
            
            correct = len([a for a in attempts if a.is_correct])
            total = len(attempts)
            
            return {
                "student_id": student.id,
                "student_name": student.name,
                "total_xp": student.total_xp,
                "current_streak": student.current_streak,
                "best_streak": student.best_streak,
                "total_attempts": total,
                "correct_answers": correct,
                "accuracy_percentage": (correct / total * 100) if total > 0 else 0,
                "current_bloom_level": self._calculate_bloom_level(correct, total),
                "misconceptions": self._get_misconceptions(student.id),
                "created_at": student.created_at.isoformat(),
                "last_updated": student.updated_at.isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    
    def close(self):
        """Close database session"""
        try:
            self.db.close()
        except Exception as e:
            print(f"⚠️ Error closing session: {e}")


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
