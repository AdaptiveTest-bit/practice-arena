"""Database configuration and ORM models for the question generator.

This module provides:
1. Database connection management using SQLAlchemy
2. ORM models for core entities (PracticeSession, etc.)
3. Session management for CRUD operations
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
from typing import Optional, Dict, List, Any

# Database connection string
DATABASE_URL = "postgresql://kunalranjan@localhost:5432/edtech_mvp"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


# ============================================================================
# ORM MODELS
# ============================================================================

class Student(Base):
    """
    Represents a student user in the system.
    
    Tracks:
    - Student name and registration info
    - Currently active chapter
    - Registration timestamp
    - Profile data for personalization
    """
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), unique=True, index=True, nullable=True)  # UUID
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    chapter = Column(String(255), default="Factors & Multiples")
    total_xp = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=lambda: datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=lambda: datetime.utcnow())
    
    # Relationships
    sessions = relationship("PracticeSession", back_populates="student", lazy="select")
    
    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.name}', chapter='{self.chapter}')>"


class PracticeSession(Base):
    """
    Represents a single practice session for a student on a chapter.
    
    A session tracks:
    - When the student started and ended
    - Which chapter they're practicing
    - Progress through Bloom's levels
    - Accuracy per concept
    - Misconceptions encountered
    - Break points (where student struggled)
    """
    __tablename__ = "practice_sessions"
    __table_args__ = {"schema": "analytics"}
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Student & Course Info
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    chapter_id = Column(Integer, nullable=False, index=True)  # FK to curriculum.chapters
    class_level = Column(Integer, nullable=False, default=5)  # Class level (e.g., 5)
    subject = Column(String(50), nullable=False, default="Mathematics")  # Subject name
    
    # Session Timing
    session_start_time = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    session_end_time = Column(DateTime, nullable=True)  # NULL until session ends
    total_duration_minutes = Column(Integer, nullable=True)  # Calculated at end
    
    # Progress Tracking
    completion_percentage = Column(Float, nullable=False, default=0.0)
    
    # JSON Fields for Flexibility
    # ===========================
    
    # Concepts covered in this session (list of concept names)
    concepts_covered = Column(JSON, nullable=False, default=list)  # ["place_value", "rounding"]
    
    # Concepts the student has mastered (>= 80% accuracy)
    concepts_mastered = Column(JSON, nullable=False, default=list)  # ["place_value"]
    
    # Concepts with weak performance (< 70% accuracy)
    concepts_weak = Column(JSON, nullable=False, default=list)  # ["rounding"]
    
    # Accuracy per concept
    # Format: {"concept_name": 0.85, "concept_name2": 0.65}
    accuracy_by_concept = Column(JSON, nullable=False, default=dict)
    
    # Bloom's Level Progress
    # Format: {
    #   "remember": {"status": "completed", "accuracy": 0.90},
    #   "understand": {"status": "in_progress", "accuracy": 0.70},
    #   "apply": {"status": "locked", "accuracy": 0},
    #   ...
    # }
    bloom_levels_completed = Column(JSON, nullable=False, default=dict)
    
    # Misconceptions Detected
    # Format: {"place_value_confusion": 3, "rounding_error": 1}
    misconceptions_detected = Column(JSON, nullable=False, default=dict)
    
    # Performance Summary
    total_questions_attempted = Column(Integer, nullable=False, default=0)
    total_questions_correct = Column(Integer, nullable=False, default=0)
    overall_accuracy = Column(Float, nullable=False, default=0.0)
    
    # Break Points (where student struggles significantly)
    # Format: [
    #   {
    #     "concept": "rounding",
    #     "bloom_level": "understand",
    #     "accuracy": 0.40,
    #     "timestamp": "2025-12-28T10:30:00",
    #     "questions_attempted": 5,
    #     "questions_correct": 2
    #   }
    # ]
    break_points = Column(JSON, nullable=False, default=list)
    
    # Session Status
    status = Column(String(20), nullable=False, default="in_progress")  # in_progress, completed, paused
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="sessions", lazy="select")
    
    def __repr__(self):
        return f"<PracticeSession(id={self.id}, student={self.student_id}, chapter={self.chapter_id}, status={self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "chapter_id": self.chapter_id,
            "class_level": self.class_level,
            "subject": self.subject,
            "session_start_time": self.session_start_time.isoformat() if self.session_start_time else None,
            "session_end_time": self.session_end_time.isoformat() if self.session_end_time else None,
            "total_duration_minutes": self.total_duration_minutes,
            "completion_percentage": self.completion_percentage,
            "concepts_covered": self.concepts_covered,
            "concepts_mastered": self.concepts_mastered,
            "concepts_weak": self.concepts_weak,
            "accuracy_by_concept": self.accuracy_by_concept,
            "bloom_levels_completed": self.bloom_levels_completed,
            "misconceptions_detected": self.misconceptions_detected,
            "total_questions_attempted": self.total_questions_attempted,
            "total_questions_correct": self.total_questions_correct,
            "overall_accuracy": self.overall_accuracy,
            "break_points": self.break_points,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class StudentSessionState(Base):
    """
    Tracks the current state of a student's practice session.
    Used to resume sessions or provide real-time feedback.
    """
    __tablename__ = "student_session_state"
    __table_args__ = {"schema": "analytics"}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False, index=True)
    session_id = Column(Integer, nullable=False, index=True)
    
    # Current state
    current_bloom_level = Column(String(50), nullable=False, default="remember")  # Current Bloom level
    current_concept = Column(String(255), nullable=True)  # Current concept being practiced
    
    # Question counter
    questions_in_current_bloom = Column(Integer, nullable=False, default=0)
    questions_needed_for_bloom = Column(Integer, nullable=False, default=5)
    
    # Last action
    last_question_id = Column(String(255), nullable=True)
    last_question_timestamp = Column(DateTime, nullable=True)
    
    # Session state
    is_active = Column(Boolean, nullable=False, default=True)
    paused_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Create all tables in the database if they don't exist."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables initialized successfully")


def get_db():
    """Dependency injection for database session in FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# HELPER FUNCTIONS FOR PRACTICE SESSIONS
# ============================================================================

def create_practice_session(
    student_id: int,
    chapter_id: int,
    class_level: int = 5,
    subject: str = "Mathematics"
) -> PracticeSession:
    """Create a new practice session."""
    db = SessionLocal()
    try:
        session = PracticeSession(
            student_id=student_id,
            chapter_id=chapter_id,
            class_level=class_level,
            subject=subject,
            status="in_progress"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    finally:
        db.close()


def get_practice_session(session_id: int) -> Optional[PracticeSession]:
    """Retrieve a practice session by ID."""
    db = SessionLocal()
    try:
        return db.query(PracticeSession).filter(PracticeSession.id == session_id).first()
    finally:
        db.close()


def get_active_session_for_student(student_id: int, chapter_id: int) -> Optional[PracticeSession]:
    """Get the active (in_progress) session for a student on a chapter."""
    db = SessionLocal()
    try:
        return db.query(PracticeSession).filter(
            PracticeSession.student_id == student_id,
            PracticeSession.chapter_id == chapter_id,
            PracticeSession.status == "in_progress"
        ).first()
    finally:
        db.close()


def update_practice_session(session_id: int, updates: Dict[str, Any]) -> Optional[PracticeSession]:
    """Update a practice session with the given updates."""
    db = SessionLocal()
    try:
        session = db.query(PracticeSession).filter(PracticeSession.id == session_id).first()
        if session:
            for key, value in updates.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            session.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(session)
        return session
    finally:
        db.close()


def end_practice_session(session_id: int) -> Optional[PracticeSession]:
    """End a practice session and calculate final statistics."""
    db = SessionLocal()
    try:
        session = db.query(PracticeSession).filter(PracticeSession.id == session_id).first()
        if session and session.status == "in_progress":
            session.session_end_time = datetime.utcnow()
            
            # Calculate total duration
            if session.session_start_time and session.session_end_time:
                duration = (session.session_end_time - session.session_start_time).total_seconds()
                session.total_duration_minutes = int(duration / 60)
            
            # Calculate overall accuracy
            if session.total_questions_attempted > 0:
                session.overall_accuracy = session.total_questions_correct / session.total_questions_attempted
            
            session.status = "completed"
            session.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(session)
        return session
    finally:
        db.close()
