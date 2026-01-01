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
from routes.content_routes import router as content_router

from models.question import ChapterEnum
from pydantic import BaseModel

logger = get_logger(__name__)


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
    """Register all question generation strategies - INTEGRATED with K.C. Nag & Adaptive."""
    from factory import QuestionGeneratorFactory
    # ============================================================================
    # INTEGRATED HYBRID NEURO-SYMBOLIC STRATEGIES (All 16 chapters)
    # ============================================================================
    from strategies.factors_multiples_integrated import FactorsMultiplesIntegrated
    from strategies.large_numbers_integrated import LargeNumbersIntegrated
    from strategies.clock_angles_integrated import ClockAnglesIntegrated
    from strategies.symmetry_integrated import SymmetryIntegrated
    from strategies.rotation_integrated import RotationIntegrated
    from strategies.fraction_area_integrated import FractionAreaIntegrated
    from strategies.fractions_decimals_integrated import FractionsDecimalsIntegrated
    from strategies.dice_logic_integrated import DiceLogicIntegrated
    from strategies.nets_integrated import NetsIntegrated
    from strategies.cube_counting_integrated import CubeCountingIntegrated
    from strategies.geometry_measurement_integrated import GeometryMeasurementIntegrated
    from strategies.data_patterns_integrated import DataPatternsIntegrated
    from strategies.mapping_integrated import MappingIntegrated
    from strategies.data_handling_integrated import DataHandlingIntegrated
    from strategies.measurement_integrated import MeasurementIntegrated
    from strategies.multiplication_division_integrated import MultiplicationDivisionIntegrated
    
    chapters = [
        (ChapterEnum.FACTORS_MULTIPLES, FactorsMultiplesIntegrated),
        (ChapterEnum.LARGE_NUMBERS, LargeNumbersIntegrated),
        (ChapterEnum.CLOCK_ANGLES, ClockAnglesIntegrated),
        (ChapterEnum.SYMMETRY, SymmetryIntegrated),
        (ChapterEnum.ROTATION, RotationIntegrated),
        (ChapterEnum.FRACTION_AREA, FractionAreaIntegrated),
        (ChapterEnum.FRACTIONS_DECIMALS, FractionsDecimalsIntegrated),
        (ChapterEnum.DICE_LOGIC, DiceLogicIntegrated),
        (ChapterEnum.NETS, NetsIntegrated),
        (ChapterEnum.CUBE_COUNTING, CubeCountingIntegrated),
        (ChapterEnum.GEOMETRY_MEASUREMENT, GeometryMeasurementIntegrated),
        (ChapterEnum.DATA_PATTERNS, DataPatternsIntegrated),
        (ChapterEnum.MAPPING, MappingIntegrated),
        (ChapterEnum.DATA_HANDLING, DataHandlingIntegrated),
        (ChapterEnum.MEASUREMENT, MeasurementIntegrated),
        (ChapterEnum.MULTIPLICATION_DIVISION, MultiplicationDivisionIntegrated),
    ]
    
    for chapter, strategy in chapters:
        QuestionGeneratorFactory.register(chapter, strategy)
    
    logger.info(f"✅ Registered {len(chapters)} INTEGRATED question generation strategies (K.C. Nag + Adaptive)")


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


@app.get("/api/health/startup")
async def startup_status():
    """Check if all services are initialized correctly.
    
    Returns:
        Status of each initialization component
    """
    try:
        from services.adaptive_learning_service import AdaptiveLearningService
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
            "message": "Services not initialized - check backend logs"
        }
    except Exception as e:
        logger.error(f"Unexpected error in startup check: {e}")
        return {
            "status": "error",
            "error": type(e).__name__,
            "message": str(e)
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
    from services.adaptive_learning_service import AdaptiveLearningService
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
    """Get detailed progress report for a student.
    
    Path parameters:
        student_id: The student ID
    
    Returns:
        StudentProgressResponse with learning metrics and progress
    """
    from services.adaptive_learning_service import AdaptiveLearningService
    service: AdaptiveLearningService = app.state.adaptive_service
    
    try:
        student = service.repository.get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
        
        logger.info(f"Retrieved progress for student {student_id}")
        
        return StudentProgressResponse(
            success=True,
            studentId=student_id,
            name="Student",
            chapter=student.chapter or "Ch1: The Fish Tale",
            currentBloomLevel=student.current_bloom_level,
            attemptCount=student.total_attempts,
            correctCount=student.total_correct,
            accuracyRate=student.overall_percentage / 100 if student.overall_percentage > 0 else 0,
            misconceptionsEncountered=[]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving student progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/student/{student_id}/misconceptions", response_model=MisconceptionReportResponse)
async def get_misconception_report(student_id: str):
    """Get detailed misconception analysis for a student.
    
    Path parameters:
        student_id: The student UUID
    
    Returns:
        MisconceptionReportResponse with misconception patterns and recommendations
    """
    from services.adaptive_learning_service import AdaptiveLearningService
    service: AdaptiveLearningService = app.state.adaptive_service
    
    try:
        student = service.repository.get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
        
        # Get misconception report
        dashboard = service.get_student_dashboard(student_id)
        report = dashboard.get("report", {})
        
        # Count misconceptions
        misconceptions_map = {}
        for attempt in service.repository.get_student_attempts(student_id):
            if attempt.misconception_revealed:
                key = attempt.misconception_revealed.value
                misconceptions_map[key] = misconceptions_map.get(key, 0) + 1
        
        logger.info(f"Retrieved misconception report for student {student_id}")
        
        return MisconceptionReportResponse(
            success=True,
            studentId=student_id,
            totalAttempts=student.total_attempts,
            misconceptionsDetected=misconceptions_map,
            frequentMisconceptions=[
                {"misconception": k, "count": v} 
                for k, v in sorted(misconceptions_map.items(), key=lambda x: x[1], reverse=True)[:5]
            ],
            recommendedTopics=dashboard.get("recommended_interventions", [])
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving misconception report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROUTE REGISTRATION
# ============================================================================

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
