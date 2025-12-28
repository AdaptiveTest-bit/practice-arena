"""Database Configuration & ORM Models

Sets up PostgreSQL connection with SQLAlchemy ORM.
Defines all database models for the adaptive learning system.
"""

from sqlalchemy import create_engine, event, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Text, Date, NUMERIC, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.pool import QueuePool
from datetime import datetime, date
import os

# Database URL
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://kunalranjan@localhost:5432/edtech_mvp'
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False,  # Set to True for SQL debugging
    connect_args={"connect_timeout": 10}
)

# Register event listener for schema search path
@event.listens_for(engine, "connect")
def set_search_path(dbapi_conn, connection_record):
    """Set search_path for cross-schema queries"""
    cursor = dbapi_conn.cursor()
    try:
        cursor.execute("SET search_path TO users,curriculum,analytics,public")
        cursor.close()
    except Exception as e:
        print(f"⚠️ Warning: Could not set search_path: {e}")

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Base class for all ORM models
Base = declarative_base()

# ============================================================================
# ORM MODELS - USERS SCHEMA
# ============================================================================

class Student(Base):
    """Student account information and gamification tracking"""
    __tablename__ = "students"
    __table_args__ = {"schema": "users"}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    grade_level = Column(Integer, nullable=True)
    
    # Gamification
    total_xp = Column(Integer, nullable=False, default=0)
    current_streak = Column(Integer, nullable=False, default=0)
    best_streak = Column(Integer, nullable=False, default=0)
    
    # Profile
    avatar_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mastery_records = relationship("StudentMastery", back_populates="student", cascade="all, delete-orphan")
    attempts = relationship("QuestionAttempt", back_populates="student", cascade="all, delete-orphan")
    progress = relationship("StudentProgressRecord", back_populates="student", cascade="all, delete-orphan")


class Parent(Base):
    """Parent/guardian accounts for monitoring student progress"""
    __tablename__ = "parents"
    __table_args__ = {"schema": "users"}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class StudentParentLink(Base):
    """Many-to-many relationship between students and parents"""
    __tablename__ = "student_parent_link"
    __table_args__ = (
        UniqueConstraint('student_id', 'parent_id', name='uq_student_parent'),
        {"schema": "users"}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.students.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("users.parents.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


# ============================================================================
# ORM MODELS - CURRICULUM SCHEMA
# ============================================================================

class Chapter(Base):
    """High-level learning units (chapters)"""
    __tablename__ = "chapters"
    __table_args__ = {"schema": "curriculum"}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    sequence_order = Column(Integer, nullable=False)
    unit_tag = Column(String(50), nullable=True)
    
    # Relationships
    topics = relationship("Topic", back_populates="chapter", cascade="all, delete-orphan")
    progress_records = relationship("StudentProgressRecord", back_populates="chapter", cascade="all, delete-orphan")


class Topic(Base):
    """Sub-sections within chapters"""
    __tablename__ = "topics"
    __table_args__ = {"schema": "curriculum"}
    
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("curriculum.chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    chapter = relationship("Chapter", back_populates="topics")
    concepts = relationship("Concept", back_populates="topic", cascade="all, delete-orphan")


class Concept(Base):
    """Atomic learning units"""
    __tablename__ = "concepts"
    __table_args__ = {"schema": "curriculum"}
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("curriculum.topics.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    misconception_guide = Column(Text, nullable=True)
    
    # Relationships
    topic = relationship("Topic", back_populates="concepts")
    questions = relationship("CurriculumQuestion", back_populates="concept", cascade="all, delete-orphan")
    mastery = relationship("StudentMastery", back_populates="concept", cascade="all, delete-orphan")


class CurriculumQuestion(Base):
    """Quiz questions with options and difficulty levels"""
    __tablename__ = "questions"
    __table_args__ = (
        CheckConstraint('difficulty_level BETWEEN 1 AND 3', name='check_difficulty_level'),
        {"schema": "curriculum"}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(Integer, ForeignKey("curriculum.concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(JSON, nullable=False)  # {"text": "...", "options": {"A": "...", "B": "..."}}
    difficulty_level = Column(Integer, nullable=False, default=1)
    correct_option_key = Column(String(10), nullable=False)
    explanation = Column(Text, nullable=False)
    
    # Relationships
    concept = relationship("Concept", back_populates="questions")
    attempts = relationship("QuestionAttempt", back_populates="question", cascade="all, delete-orphan")


# ============================================================================
# ORM MODELS - ANALYTICS SCHEMA
# ============================================================================

class StudentMastery(Base):
    """Concept mastery tracking using Leitner system + EMA"""
    __tablename__ = "student_mastery"
    __table_args__ = {"schema": "analytics"}
    
    user_id = Column(Integer, ForeignKey("users.students.id", ondelete="CASCADE"), nullable=False, primary_key=True, index=True)
    concept_id = Column(Integer, ForeignKey("curriculum.concepts.id", ondelete="CASCADE"), nullable=False, primary_key=True, index=True)
    
    mastery_score = Column(Float, nullable=False, default=0.0)
    leitner_box = Column(Integer, nullable=False, default=1)
    next_review_date = Column(Date, nullable=False, default=date.today)
    last_practiced_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="mastery_records")
    concept = relationship("Concept", back_populates="mastery")


class QuestionAttempt(Base):
    """Every single question attempt with detailed metadata"""
    __tablename__ = "question_attempts"
    __table_args__ = (
        CheckConstraint('difficulty_attempted BETWEEN 1 AND 3', name='check_difficulty_attempted'),
        CheckConstraint('time_taken_seconds >= 0', name='check_time_positive'),
        CheckConstraint("mistake_type IN ('CARELESS', 'KNOWLEDGE_GAP', 'UNCERTAIN')", name='check_mistake_type'),
        CheckConstraint('mistake_confidence IS NULL OR (mistake_confidence BETWEEN 0.5 AND 1.0)', name='check_confidence'),
        {"schema": "analytics"}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.students.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("curriculum.questions.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(Integer, ForeignKey("curriculum.concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id = Column(Integer, ForeignKey("curriculum.chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Answer Data
    is_correct = Column(Boolean, nullable=False)
    selected_option = Column(String(1), nullable=True)
    difficulty_attempted = Column(Integer, nullable=False, default=1)
    time_taken_seconds = Column(Integer, nullable=True)
    
    # Mistake Analysis
    was_guess = Column(Boolean, nullable=False, default=False)
    mistake_type = Column(String(50), nullable=True)
    mistake_confidence = Column(Float, nullable=True)
    
    # Timestamps
    answered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="attempts")
    question = relationship("CurriculumQuestion", back_populates="attempts")


class QuizSubmission(Base):
    """Quiz answer submissions with XP tracking"""
    __tablename__ = "quiz_submissions"
    __table_args__ = {"schema": "analytics"}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.students.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("curriculum.questions.id", ondelete="CASCADE"), nullable=False, index=True)
    is_correct = Column(Boolean, nullable=False)
    time_taken_seconds = Column(Integer, nullable=True)
    selected_option = Column(String(10), nullable=True)
    xp_earned = Column(Integer, nullable=False, default=0)
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class StudentProgressRecord(Base):
    """Chapter-level mastery and progress tracking"""
    __tablename__ = "student_progress"
    __table_args__ = {"schema": "analytics"}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.students.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id = Column(Integer, ForeignKey("curriculum.chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Mastery Metrics
    mastery_score = Column(NUMERIC(5, 2), nullable=False, default=0)
    questions_completed = Column(Integer, nullable=False, default=0)
    questions_correct = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    last_answered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'chapter_id', name='uq_user_chapter'),
        {"schema": "analytics"}
    )
    
    # Relationships
    student = relationship("Student", back_populates="progress")
    chapter = relationship("Chapter", back_populates="progress_records")


class DailyAnalytic(Base):
    """Daily aggregated statistics for dashboard"""
    __tablename__ = "daily_analytics"
    __table_args__ = (
        UniqueConstraint('user_id', 'analytics_date', name='uq_user_date'),
        {"schema": "analytics"}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.students.id", ondelete="CASCADE"), nullable=False, index=True)
    analytics_date = Column(Date, nullable=False)
    
    questions_answered = Column(Integer, nullable=False, default=0)
    questions_correct = Column(Integer, nullable=False, default=0)
    xp_earned = Column(Integer, nullable=False, default=0)
    time_spent_minutes = Column(Integer, nullable=False, default=0)
    streak_count = Column(Integer, nullable=False, default=0)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# DATABASE UTILITIES
# ============================================================================

def get_db():
    """Dependency for getting database session in FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise


def drop_db():
    """Drop all tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️ All database tables dropped")


def get_session():
    """Get a new database session"""
    return SessionLocal()
