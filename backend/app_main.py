"""Production-ready FastAPI application for K.C. Nag Mathematics Question Generator.

This version includes:
- Comprehensive configuration management
- Structured logging with JSON support
- Redis caching layer
- Error handling & middleware
- Proper database connection pooling
- Lifecycle management
- Performance monitoring
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any

from config.settings import settings, get_settings
from config.logging_config import get_logger
from core.middleware import (
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
    PerformanceMonitoringMiddleware
)
from core.lifecycle import lifespan_context
from core.database import init_db
from core.cache import get_cache_manager
from core.exceptions import NotFoundError, ValidationError

from pydantic import BaseModel

logger = get_logger(__name__)


# ============================================================================
# DB BOOTSTRAP (BANK + CONCEPT CATALOG)
# ============================================================================

async def ensure_db_schema():
    """Ensure required tables exist for the bank-first runtime.

    This keeps local/dev and fresh deploys working without manual Alembic steps.
    In production you can rely on migrations; in dev we can safely create missing
    tables because models are small and stable.
    """
    try:
        from db.base import Base as DbBase
        from db import models as _models  # noqa: F401 (ensure model import side-effects)
        init_db(DbBase.metadata)
    except Exception as e:
        raise RuntimeError(f"Failed to ensure DB schema: {e}")


async def bootstrap_bank_and_concepts():
    """Idempotently seed concept_catalog and import bundled YAML banks.

    MVP MODE (single chapter): this runtime is currently pinned to a single
    chapter (`factors_multiples`) to keep one source of truth while iterating.

    This implements the build plan:
    - Pre-generate question bank (YAML is just an authoring format)
    - Import into Postgres question_bank_items
    - Seed curated concept_catalog for scheduler

    Safe to run on every startup (uses deterministic ids / upserts).
    """
    try:
        from pathlib import Path

        # 1) Seed curated concept taxonomy (single chapter MVP)
        try:
            from tools.seed_concepts import seed as seed_concepts

            seed_concepts(subject="math", chapter_key="factors_multiples", grade_level=5)
        except Exception as e:
            logger.warning(f"Concept seeding skipped/failed: {e}")

        # 2) Import bank into question_bank_items (single chapter MVP)
        data_dir = Path(__file__).resolve().parent / "data"
        archive_dir = data_dir / "archive"

        lean_bank = data_dir / "factors_multiples_lean.yaml"

        try:
            from tools.import_lean_bank import import_lean_yaml

            total = 0
            if lean_bank.exists():
                total += int(import_lean_yaml(lean_bank, chapter="factors_multiples") or 0)
            if total:
                logger.info(f"✅ Imported/updated {total} lean questions into question_bank_items")
        except Exception as e:
            logger.warning(f"Lean bank import skipped/failed: {e}")

        # Optional: also import the archived premium class5_chapter5_bank.yaml into chapter 'factors_multiples'
        # (kept for backward compatibility during MVP; can be removed once lean bank is complete)
        try:
            from tools.import_question_bank import import_yaml_bank

            premium = archive_dir / "class5_chapter5_bank.yaml"
            if premium.exists():
                # This YAML uses the older nested bank format. Import into the canonical chapter key.
                count = import_yaml_bank(premium, chapter="factors_multiples")
                logger.info(f"✅ Imported/updated {count} premium questions (class5_chapter5_bank.yaml)")
        except Exception as e:
            logger.warning(f"Premium bank import skipped/failed: {e}")

    except Exception as e:
        # Do not kill the app on bootstrap; API should still come up (health endpoints)
        logger.warning(f"Bank/concept bootstrap failed: {e}")


# ============================================================================
# PYDANTIC REQUEST/RESPONSE MODELS FOR STUDENT MANAGEMENT
# ============================================================================

class StudentRegistrationRequest(BaseModel):
    """Request to register a new student."""
    name: str
    chapter: Optional[str] = "Ch1: The Fish Tale"


class StudentProgressResponse(BaseModel):
    """Response with student progress information."""
    success: bool
    studentId: str
    name: str
    chapter: str
    currentBloomLevel: str
    attemptCount: int
    correctCount: int
    accuracyRate: float
    misconceptionsEncountered: List[str]


class MisconceptionReportResponse(BaseModel):
    """Response with misconception analysis."""
    success: bool
    studentId: str
    totalAttempts: int
    misconceptionsDetected: Dict[str, int]
    frequentMisconceptions: List[Dict[str, Any]]
    recommendedTopics: List[str]


# ============================================================================
# INITIALIZE FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan_context
)


# ============================================================================
# MIDDLEWARE SETUP
# ============================================================================

# Add middleware in order (last added = first executed)
app.add_middleware(PerformanceMonitoringMiddleware, slow_request_threshold_ms=1000)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"]
)


# ============================================================================
# STARTUP HOOKS
# ============================================================================

async def init_database():
    """Initialize database on startup."""
    # Database tables already exist in production
    # Just verify connection and health
    success = init_db()
    if not success:
        raise RuntimeError("Database initialization failed")


async def register_question_strategies():
    """Register question generation strategies.
    
    NOTE: Strategies have been replaced by YAML-based question bank.
    This function is kept for backward compatibility but is now a no-op.
    Questions are served from question_bank_items table via QuestionBankService.
    """
    logger.info("📦 Using YAML-based question bank (strategies disabled)")


async def init_services():
    """Initialize core services."""
    from services.question_service import QuestionService
    from domain.adaptive_learning.service import AdaptiveLearningService
    from domain.session_management.student.repository import get_repository
    
    # Initialize question service
    app.state.question_service = QuestionService()
    logger.info("✅ QuestionService initialized")
    
    # Initialize adaptive learning service with ORM repository
    orm_repository = get_repository()
    app.state.adaptive_service = AdaptiveLearningService(repository=orm_repository)
    logger.info("✅ AdaptiveLearningService initialized with PostgreSQL backend")


# Register startup hooks
from core.lifecycle import lifecycle_manager

lifecycle_manager.register_startup("Database", init_database)
lifecycle_manager.register_startup("DB Schema", ensure_db_schema)
lifecycle_manager.register_startup("Bank + Concept Bootstrap", bootstrap_bank_and_concepts)
lifecycle_manager.register_startup("Question Strategies", register_question_strategies)
lifecycle_manager.register_startup("Core Services", init_services)


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health")
async def health_check(settings: Dict = Depends(get_settings)):
    """Health check endpoint.
    
    Returns:
        Health status and service information
    """
    return {
        "status": "healthy",
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "debug": settings.DEBUG
    }


@app.get("/api/health/startup")
async def startup_status():
    """Check if all services are initialized correctly.

    Returns:
        Status of each initialization component
    """
    try:
        from domain.adaptive_learning.service import AdaptiveLearningService
        service: AdaptiveLearningService = app.state.adaptive_service
        question_service = app.state.question_service

        # Verify services exist
        services_ready = {
            "adaptive_service": service is not None,
            "question_service": question_service is not None,
            "repository": service.repository is not None if service else False,
        }

        all_ready = all(services_ready.values())

        return {
            "status": "ready" if all_ready else "initializing",
            "services": services_ready,
            "message": "All services initialized" if all_ready else "Some services not yet initialized"
        }
    except AttributeError as e:
        logger.error(f"Service not initialized: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Service initialization error"
        }
    except Exception as e:
        logger.error(f"Error checking startup status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Error checking service status"
        }


# ============================================================================
# API ROUTES
# ============================================================================

@app.get("/api/info")
async def get_api_info(settings = Depends(get_settings)):
    """Get API information and configuration.
    
    Returns:
        API metadata
    """
    return {
        "title": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "endpoints": {
            "health": "/health",
            "api_info": "/api/info",
            "categories": "/api/categories"
        }
    }


@app.get("/api/categories")
async def get_categories(cache = Depends(get_cache_manager)):
    """Get list of all available question categories.

    MVP MODE: expose only the single chapter (`factors_multiples`) while we
    stabilize ingestion + metadata + analytics.

    Returns:
        List of chapters with metadata
    """
    # Try to get from cache
    cached = cache.get("categories:all")
    if cached is not None:
        logger.debug("Serving categories from cache")
        return cached

    # Single-source-of-truth: one chapter for MVP
    chapters = [
        {
            "id": "factors_multiples",
            "name": "Factors Multiples",
            "icon": "📚",
        }
    ]

    response = {
        "success": True,
        "categories": chapters,
    }

    # Cache for 24 hours
    cache.set("categories:all", response, ttl=86400)

    return response


# ============================================================================
# QUIZ SESSION ENDPOINTS
# ============================================================================

from pydantic import BaseModel
from domain.session_management.service import get_session_adapter


class SessionStartRequest(BaseModel):
    """Request to start a quiz session."""
    student_id: str
    grade_level: int
    mode: str
    chapter: Optional[str] = None


class SubmitAnswerRequest(BaseModel):
    """Request to submit an answer."""
    question_id: str
    selected_index: int
    time_taken_seconds: Optional[int] = None


@app.post("/api/quiz/session/start")
async def start_quiz_session(request: SessionStartRequest):
    """Start a new quiz session.
    
    Args:
        request: Session start request with student_id, grade_level, mode, optional chapter
    
    Returns:
        Session configuration with questions metadata
    """
    try:
        adapter = get_session_adapter()
        response = adapter.start_session(
            student_id=request.student_id,
            grade_level=request.grade_level,
            mode=request.mode,
            chapter=request.chapter
        )
        logger.info(f"Started session for student {request.student_id}")
        return response
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/quiz/{session_id}/question")
async def get_quiz_question(session_id: str):
    """Get the next question in the quiz.
    
    Args:
        session_id: The session ID
    
    Returns:
        Question with options, difficulty, and metadata
    """
    try:
        adapter = get_session_adapter()
        response = adapter.get_next_question(session_id)
        logger.info(f"Retrieved question for session {session_id}")
        return response
    except ValueError as e:
        logger.warning(f"Question retrieval error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quiz/{session_id}/answer")
async def submit_quiz_answer(session_id: str, request: SubmitAnswerRequest):
    """Submit an answer and get feedback.
    
    Args:
        session_id: The session ID
        request: Answer submission with question_id, selected_index, time_taken_seconds
    
    Returns:
        Feedback with correctness, mastery score, and misconceptions
    """
    try:
        adapter = get_session_adapter()
        response = adapter.submit_answer(
            session_id=session_id,
            question_id=request.question_id,
            answer_id=request.selected_index,
            time_spent=request.time_taken_seconds or 0
        )
        logger.info(f"Processed answer for session {session_id}")
        return response
    except ValueError as e:
        logger.warning(f"Answer processing error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/quiz/{session_id}/hint")
async def get_quiz_hint(session_id: str, question_id: str, hint_index: int = 0):
    """Get a hint for the current question.
    
    Args:
        session_id: The session ID
        question_id: The question ID
        hint_index: Which hint to return (0-2)
    
    Returns:
        Hint text and metadata
    """
    try:
        adapter = get_session_adapter()
        response = adapter.get_hint(session_id, question_id, hint_index)
        logger.info(f"Retrieved hint for question {question_id}")
        return response
    except ValueError as e:
        logger.warning(f"Hint retrieval error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving hint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quiz/{session_id}/end")
async def end_quiz_session(session_id: str):
    """End a quiz session and get final results.
    
    Args:
        session_id: The session ID
    
    Returns:
        Final results with score, accuracy, and performance metrics
    """
    try:
        adapter = get_session_adapter()
        response = adapter.end_session(session_id)
        logger.info(f"Ended session {session_id}")
        return response
    except ValueError as e:
        logger.warning(f"Session end error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STUDENT MANAGEMENT ENDPOINTS (NEW)
# ============================================================================

@app.post("/api/student/register")
async def register_student(request: StudentRegistrationRequest):
    """Register a new student.
    
    Request body:
    {
        "name": "Student Name",
        "chapter": "Ch1: The Fish Tale"
    }
    
    Returns:
        {"student_id": "uuid", "name": "Student Name", "chapter": "Ch1: The Fish Tale"}
    """
    from domain.adaptive_learning.service import AdaptiveLearningService
    service: AdaptiveLearningService = app.state.adaptive_service
    
    try:
        # Validate request
        if not request.name or request.name.strip() == "":
            logger.warning("Registration attempt with empty name")
            raise ValueError("Student name cannot be empty")
        
        # Register student
        result = service.repository.register_student(
            name=request.name.strip(),
            chapter=request.chapter or "Ch1: The Fish Tale"
        )
        
        # Check if registration succeeded
        if isinstance(result, dict) and result.get("success") is False:
            error_msg = result.get("error", "Unknown error")
            logger.error(f"Registration failed for {request.name}: {error_msg}")
            raise HTTPException(
                status_code=400,
                detail=f"Registration failed: {error_msg}"
            )
        
        # Extract student_id from result (could be dict or string)
        student_id = result.get("studentId") if isinstance(result, dict) else result
        
        logger.info(f"✅ Registered new student {student_id}: {request.name}")
        
        return {
            "success": True,
            "student_id": str(student_id),
            "studentId": str(student_id),  # camelCase for frontend compatibility
            "name": request.name,
            "chapter": request.chapter or "Ch1: The Fish Tale"
        }
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error registering student {request.name}: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {type(e).__name__}"
        )


@app.get("/api/student/{student_id}/progress", response_model=StudentProgressResponse)
async def get_student_progress(student_id: str):
    """Get detailed progress report for a student (event-first).

    This endpoint is aligned with the production DB-first session flow:
    it derives progress from the `learning_events` spine instead of the legacy
    in-memory AdaptiveLearningService repository.
    """
    try:
        from core.database import SessionLocal
        from db.models.events import LearningEvent

        with SessionLocal() as db:
            total_attempts = (
                db.query(LearningEvent)
                .filter(
                    LearningEvent.student_id == str(student_id),
                    LearningEvent.event_type == "ANSWERED",
                )
                .count()
            )
            total_correct = (
                db.query(LearningEvent)
                .filter(
                    LearningEvent.student_id == str(student_id),
                    LearningEvent.event_type == "ANSWERED",
                    LearningEvent.payload["is_correct"].as_boolean() == True,  # noqa: E712
                )
                .count()
            )

            # Most recent chapter context, if available
            last_answered = (
                db.query(LearningEvent)
                .filter(
                    LearningEvent.student_id == str(student_id),
                    LearningEvent.event_type == "ANSWERED",
                )
                .order_by(LearningEvent.timestamp.desc())
                .first()
            )

        accuracy = (total_correct / total_attempts) if total_attempts > 0 else 0.0
        chapter = getattr(last_answered, "chapter_key", None) if last_answered else None

        return StudentProgressResponse(
            success=True,
            studentId=str(student_id),
            name="Student",
            chapter=chapter or "unknown",
            currentBloomLevel=None,
            attemptCount=int(total_attempts),
            correctCount=int(total_correct),
            accuracyRate=float(accuracy),
            misconceptionsEncountered=[],
        )

    except Exception as e:
        logger.error(f"Error retrieving student progress (event-first): {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/student/{student_id}/misconceptions", response_model=MisconceptionReportResponse)
async def get_misconception_report(student_id: str):
    """Get detailed misconception analysis for a student (event-first).

    Derives misconception counts from `LearningEvent.payload.misconception_type`.
    This aligns the endpoint with the DB-first quiz flow.
    """
    try:
        from core.database import SessionLocal
        from db.models.events import LearningEvent

        misconceptions_map: dict[str, int] = {}
        total_attempts = 0

        with SessionLocal() as db:
            answered = (
                db.query(LearningEvent)
                .filter(
                    LearningEvent.student_id == str(student_id),
                    LearningEvent.event_type == "ANSWERED",
                )
                .all()
            )

        total_attempts = len(answered)

        for ev in answered:
            payload = getattr(ev, "payload", None) or {}
            misc_type = payload.get("misconception_type")
            if not misc_type or misc_type == "UNKNOWN":
                continue
            key = str(misc_type)
            misconceptions_map[key] = misconceptions_map.get(key, 0) + 1

        return MisconceptionReportResponse(
            success=True,
            studentId=str(student_id),
            totalAttempts=int(total_attempts),
            misconceptionsDetected=misconceptions_map,
            frequentMisconceptions=[
                {"misconception": k, "count": v}
                for k, v in sorted(misconceptions_map.items(), key=lambda x: x[1], reverse=True)[:5]
            ],
            recommendedTopics=[],
        )

    except Exception as e:
        logger.error(f"Error retrieving misconception report (event-first): {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ADAPTIVE MASTERY ENDPOINTS
# ============================================================================

class ConceptMasteryResponse(BaseModel):
    """Mastery data for a single concept."""
    concept_id: str
    concept_name: str
    level: str  # novice, developing, proficient, mastered
    accuracy: float
    total_attempts: int
    correct_attempts: int


class StudentMasteryResponse(BaseModel):
    """Full mastery report for a student in a chapter."""
    success: bool
    student_id: str
    chapter_id: str
    overall_accuracy: float
    concepts: list[ConceptMasteryResponse]
    recommendations: list[str]


@app.get("/api/student/{student_id}/mastery/{chapter_id}", response_model=StudentMasteryResponse)
async def get_student_mastery(student_id: str, chapter_id: str):
    """Get adaptive mastery progress for a student in a chapter.
    
    This endpoint provides real-time mastery data from the adaptation layer,
    showing per-concept progress and recommendations.
    """
    try:
        from domain.adaptation import get_adaptive_selector
        
        selector = get_adaptive_selector(chapter_id)
        if not selector:
            raise HTTPException(
                status_code=404, 
                detail=f"Chapter '{chapter_id}' does not support adaptive mastery tracking"
            )
        
        progress = selector.get_student_progress(student_id)
        
        # Build concept list with human-readable names
        concepts = []
        for concept_id, mastery_data in progress.get("concepts", {}).items():
            concepts.append(ConceptMasteryResponse(
                concept_id=concept_id,
                concept_name=concept_id.split(".")[-1].replace("_", " ").title(),
                level=mastery_data.get("mastery_level", "NOT_STARTED").lower(),
                accuracy=mastery_data.get("accuracy", 0.0),
                total_attempts=mastery_data.get("attempts", 0),
                correct_attempts=mastery_data.get("correct", 0),
            ))
        
        # Sort by accuracy (lowest first = needs most work)
        concepts.sort(key=lambda c: c.accuracy)
        
        # Compute overall accuracy from concept data
        total_attempts = sum(c.total_attempts for c in concepts)
        total_correct = sum(c.correct_attempts for c in concepts)
        overall_accuracy = (total_correct / total_attempts) if total_attempts > 0 else 0.0
        
        # Generate recommendations based on mastery
        recommendations = []
        weak_concepts = [c for c in concepts if c.level in ("not_started", "learning")]
        if weak_concepts:
            recommendations.append(f"Focus on: {weak_concepts[0].concept_name}")
        if overall_accuracy < 0.6:
            recommendations.append("Keep practicing! Accuracy below 60%")
        elif overall_accuracy >= 0.8:
            recommendations.append("Great progress! You're mastering this chapter")
        
        return StudentMasteryResponse(
            success=True,
            student_id=student_id,
            chapter_id=chapter_id,
            overall_accuracy=overall_accuracy,
            concepts=concepts,
            recommendations=recommendations,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving mastery for student {student_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/student/{student_id}/mastery/{chapter_id}/reset")
async def reset_student_mastery(student_id: str, chapter_id: str):
    """Reset mastery tracking for a student in a chapter.
    
    Useful for testing or when a student wants to start fresh.
    """
    try:
        from domain.adaptation import get_adaptive_selector
        
        selector = get_adaptive_selector(chapter_id)
        if not selector:
            raise HTTPException(
                status_code=404,
                detail=f"Chapter '{chapter_id}' does not support adaptive mastery tracking"
            )
        
        # Get a fresh mastery tracker (clears cached one)
        tracker = selector.get_mastery_tracker(student_id)
        # Reset all concepts
        for concept_id in selector.concept_graph.get_all_concept_ids():
            tracker._mastery[concept_id] = tracker._mastery.get(concept_id).__class__(
                total_attempts=0, correct_attempts=0
            ) if concept_id in tracker._mastery else None
        
        return {"success": True, "message": f"Mastery reset for student {student_id} in {chapter_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting mastery for student {student_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROUTE REGISTRATION
# ============================================================================

# MVP MODE: Rich content generation routes removed.
# The single source of truth is the DB-first quiz/session flow +
# `backend/domain/content_generation/generators/*`.


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"Listening on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
