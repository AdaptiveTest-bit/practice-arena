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
from routes.practice_routes import router as practice_router
from routes.content_routes import router as content_router

from models.question import ChapterEnum

logger = get_logger(__name__)


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
    """Register all question generation strategies."""
    from factory import QuestionGeneratorFactory
    from strategies.large_numbers import LargeNumbersStrategy
    from strategies.dice_logic import DiceLogicStrategy
    from strategies.cube_counting import CubeCountingStrategy
    from strategies.nets import NetsStrategy
    from strategies.data_handling import DataHandlingStrategy
    from strategies.clock_angles import ClockAnglesStrategy
    from strategies.symmetry import SymmetryStrategy
    from strategies.rotation import RotationStrategy
    from strategies.factors_multiples import FactorsMultiplesStrategy
    from strategies.fractions_decimals import FractionsDecimalsStrategy
    from strategies.geometry_measurement import GeometryMeasurementStrategy
    from strategies.data_patterns import DataPatternsStrategy
    
    chapters = [
        (ChapterEnum.LARGE_NUMBERS, LargeNumbersStrategy),
        (ChapterEnum.DICE_LOGIC, DiceLogicStrategy),
        (ChapterEnum.CUBE_COUNTING, CubeCountingStrategy),
        (ChapterEnum.NETS, NetsStrategy),
        (ChapterEnum.DATA_HANDLING, DataHandlingStrategy),
        (ChapterEnum.CLOCK_ANGLES, ClockAnglesStrategy),
        (ChapterEnum.SYMMETRY, SymmetryStrategy),
        (ChapterEnum.ROTATION, RotationStrategy),
        (ChapterEnum.FACTORS_MULTIPLES, FactorsMultiplesStrategy),
        (ChapterEnum.FRACTIONS_DECIMALS, FractionsDecimalsStrategy),
        (ChapterEnum.GEOMETRY_MEASUREMENT, GeometryMeasurementStrategy),
        (ChapterEnum.DATA_PATTERNS, DataPatternsStrategy),
    ]
    
    for chapter, strategy in chapters:
        QuestionGeneratorFactory.register(chapter, strategy)
    
    logger.info(f"✅ Registered {len(chapters)} question generation strategies")


async def init_services():
    """Initialize core services."""
    from services.question_service import QuestionService
    from services.adaptive_learning_service import AdaptiveLearningService
    from services.orm_student_repository import get_repository
    
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
    
    Returns:
        List of chapters with metadata
    """
    # Try to get from cache
    cached = cache.get("categories:all")
    if cached is not None:
        logger.debug("Serving categories from cache")
        return cached
    
    chapters = []
    for chapter in ChapterEnum:
        chapters.append({
            "id": chapter.value,
            "name": chapter.value.replace("_", " ").title(),
            "icon": "📚"
        })
    
    response = {
        "success": True,
        "categories": chapters
    }
    
    # Cache for 24 hours
    cache.set("categories:all", response, ttl=86400)
    
    return response


# ============================================================================
# QUIZ SESSION ENDPOINTS
# ============================================================================

from pydantic import BaseModel
from services.session_adapter import get_session_adapter


class SessionStartRequest(BaseModel):
    """Request to start a quiz session."""
    student_id: str
    grade_level: int
    mode: str
    chapter: Optional[str] = None


class SubmitAnswerRequest(BaseModel):
    """Request to submit an answer."""
    question_id: str
    answer_id: str
    time_spent: int


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
        request: Answer submission with question_id, answer_id, time_spent
    
    Returns:
        Feedback with correctness, mastery score, and misconceptions
    """
    try:
        adapter = get_session_adapter()
        response = adapter.submit_answer(
            session_id=session_id,
            question_id=request.question_id,
            answer_id=request.answer_id,
            time_spent=request.time_spent
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
# ROUTE REGISTRATION
# ============================================================================

# Register practice routes
app.include_router(practice_router)
logger.info("✅ Practice routes registered")

# Register content generation routes (Rich Questions via Hybrid Neuro-Symbolic)
app.include_router(content_router)
logger.info("✅ Content generation routes registered (Hybrid Neuro-Symbolic)")


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
