"""FastAPI application for K.C. Nag Mathematics Question Generator.

This refactored version uses:
- Strategy Pattern: Chapter-specific generators inherit from BaseChapterStrategy
- Factory Pattern: QuestionGeneratorFactory creates appropriate strategies
- Separation of Concerns: Business logic in QuestionService, models in Pydantic
- Session Management: Per-user deduplication tracking
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Optional, List, Dict, Any

from models.question import (
    ChapterEnum, Question, QuestionResponse, 
    CheckAnswerRequest, CheckAnswerResponse, RevealAnswerResponse
)
from factory import QuestionGeneratorFactory
from services.question_service import QuestionService
from services.adaptive_learning_service import AdaptiveLearningService
from services.orm_student_repository import get_repository, ORMStudentRepository
from database import init_db, SessionLocal
from pydantic import BaseModel
from strategies.base import BaseChapterStrategy
from routes.practice_routes import router as practice_router

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


# ============================================================================
# PYDANTIC REQUEST/RESPONSE MODELS FOR ADAPTIVE ENDPOINTS
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
# APPLICATION INITIALIZATION WITH ADAPTIVE SERVICE
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chapter metadata for API responses
CHAPTER_METADATA = {
    ChapterEnum.DICE_LOGIC: {
        'name': 'Dice Logic',
        'icon': '🎲',
        'chapter': 'Boxes & Sketches',
        'description': 'Opposite faces sum to 7'
    },
    ChapterEnum.CUBE_COUNTING: {
        'name': 'Cube Counting',
        'icon': '📦',
        'chapter': 'Boxes & Sketches',
        'description': '3D spatial reasoning'
    },
    ChapterEnum.NETS: {
        'name': 'Nets',
        'icon': '📐',
        'chapter': 'Boxes & Sketches',
        'description': 'Mental folding exercises'
    },
    ChapterEnum.DATA_HANDLING: {
        'name': 'Data Handling',
        'icon': '📊',
        'chapter': 'Data Handling',
        'description': 'Tables, scales & comparisons'
    },
    ChapterEnum.CLOCK_ANGLES: {
        'name': 'Clock Angles',
        'icon': '🕐',
        'chapter': 'Shapes & Angles',
        'description': 'Angles & fractions of rotation'
    },
    ChapterEnum.SYMMETRY: {
        'name': 'Symmetry',
        'icon': '🪞',
        'chapter': 'Shapes & Angles',
        'description': 'Letter & word symmetry'
    },
    ChapterEnum.ROTATION: {
        'name': 'Rotations',
        'icon': '🔄',
        'chapter': 'Shapes & Angles',
        'description': 'Turns & direction changes'
    },
    ChapterEnum.LARGE_NUMBERS: {
        'name': 'Large Numbers',
        'icon': '🔢',
        'chapter': 'Number Systems',
        'description': 'Place value, profit & loss'
    },
    ChapterEnum.FACTORS_MULTIPLES: {
        'name': 'Factors & Multiples',
        'icon': '🎯',
        'chapter': 'Number Systems',
        'description': 'HCF, LCM & divisibility'
    },
    ChapterEnum.FRACTIONS_DECIMALS: {
        'name': 'Fractions & Decimals',
        'icon': '📏',
        'chapter': 'Fractions & Decimals',
        'description': 'The "remaining" trap & conversions'
    },
    ChapterEnum.GEOMETRY_MEASUREMENT: {
        'name': 'Geometry & Measurement',
        'icon': '📐',
        'chapter': 'Geometry & Measurement',
        'description': 'Area vs Perimeter, volume, scale'
    },
    ChapterEnum.DATA_PATTERNS: {
        'name': 'Data & Patterns',
        'icon': '🧩',
        'chapter': 'Data & Patterns',
        'description': 'Sequences, missing data & pictographs'
    }
}


# ============================================================================
# INITIALIZATION & LIFECYCLE
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup/shutdown events."""
    # STARTUP: Initialize database
    logger.info("Initializing PostgreSQL database...")
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    # Register all chapter strategies with the factory
    logger.info("Registering HYBRID NEURO-SYMBOLIC integrated strategies...")
    
    # COMPLETE: All 14+ chapters now use integrated hybrid approach
    QuestionGeneratorFactory.register(ChapterEnum.LARGE_NUMBERS, LargeNumbersIntegrated)
    QuestionGeneratorFactory.register(ChapterEnum.CLOCK_ANGLES, ClockAnglesIntegrated)
    QuestionGeneratorFactory.register(ChapterEnum.SYMMETRY, SymmetryIntegrated)
    QuestionGeneratorFactory.register(ChapterEnum.ROTATION, RotationIntegrated)
    QuestionGeneratorFactory.register(ChapterEnum.FRACTION_AREA, FractionAreaIntegrated)
    QuestionGeneratorFactory.register(ChapterEnum.FACTORS_MULTIPLES, FactorsMultiplesIntegrated)
    QuestionGeneratorFactory.register(ChapterEnum.FRACTIONS_DECIMALS, FractionsDecimalsIntegrated)
    QuestionGeneratorFactory.register(ChapterEnum.DICE_LOGIC, DiceLogicIntegrated)
    QuestionGeneratorFactory.register(ChapterEnum.NETS, NetsIntegrated)
    QuestionGeneratorFactory.register(ChapterEnum.CUBE_COUNTING, CubeCountingIntegrated)
    QuestionGeneratorFactory.register(ChapterEnum.GEOMETRY_MEASUREMENT, GeometryMeasurementIntegrated)
    QuestionGeneratorFactory.register(ChapterEnum.DATA_PATTERNS, DataPatternsIntegrated)
    QuestionGeneratorFactory.register(ChapterEnum.MAPPING, MappingIntegrated)
    QuestionGeneratorFactory.register(ChapterEnum.DATA_HANDLING, DataHandlingIntegrated)
    QuestionGeneratorFactory.register(ChapterEnum.MEASUREMENT, MeasurementIntegrated)
    QuestionGeneratorFactory.register(ChapterEnum.MULTIPLICATION_DIVISION, MultiplicationDivisionIntegrated)
    
    logger.info(f"Registered {len(QuestionGeneratorFactory.list_chapters())} chapters")
    logger.info("✅ INTEGRATED SYSTEM ACTIVE: All 14+ chapters using hybrid neuro-symbolic + adaptive engine")
    
    # Initialize global question service
    app.state.question_service = QuestionService()
    
    # Initialize adaptive learning service with ORM repository
    orm_repository = get_repository()
    app.state.adaptive_service = AdaptiveLearningService(repository=orm_repository)
    logger.info("✅ Initialized AdaptiveLearningService with PostgreSQL backend")
    
    yield
    
    # SHUTDOWN: Clean up
    logger.info("Shutting down adaptive learning service...")
    if orm_repository:
        orm_repository.close()



# Create FastAPI app with lifespan
app = FastAPI(
    title="K.C. Nag Question Generator",
    description="CBSE Class 5 Mathematics with K.C. Nag pedagogical approach",
    version="2.0.0",
    lifespan=lifespan
)

# Include practice engine routes (Phase 2)
app.include_router(practice_router)

# ============================================================================
# CORS MIDDLEWARE - Allow cross-origin requests
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:5002",
        "*"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ============================================================================
# MIDDLEWARE - Add no-cache headers for dynamic content
# ============================================================================

@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    """Add cache-control headers to responses."""
    response = await call_next(request)
    # Don't cache API responses
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# ============================================================================
# MIDDLEWARE - Add no-cache headers for dynamic content
# ============================================================================

@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    """Add cache-control headers to responses."""
    response = await call_next(request)
    # Don't cache HTML or API responses
    if request.url.path == "/" or request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# ============================================================================
# ROUTES
# ============================================================================

@app.post("/api/session", response_model=dict)
async def create_session():
    """Create a new session for deduplication tracking.
    
    Returns:
        {
            "success": true,
            "sessionId": "uuid-string"
        }
    """
    service: QuestionService = app.state.question_service
    session_id = service.create_session()
    
    logger.info(f"Created new session: {session_id}")
    
    return {
        "success": True,
        "sessionId": session_id
    }


@app.post("/api/question", response_model=QuestionResponse)
async def generate_question(request: Request):
    """Generate a new question for the given chapter.
    
    Request body (Session-based):
    {
        "sessionId": "session-uuid",
        "chapter": "large_numbers" | "dice_logic" | ... (optional, random if omitted)
    }
    
    OR Request body (Student-adaptive):
    {
        "studentId": "student-uuid",
        "chapter": "large_numbers" (optional, uses adaptive engine if omitted)
    }
    
    Returns:
        QuestionResponse with all question details
    """
    question_service: QuestionService = app.state.question_service
    adaptive_service: AdaptiveLearningService = app.state.adaptive_service
    body = await request.json()
    
    student_id = body.get("studentId")
    session_id = body.get("sessionId")
    chapter_str = body.get("chapter")
    
    # If student_id provided, use adaptive learning flow
    if student_id:
        try:
            # Get next adaptive question
            student = adaptive_service.repository.get_student(student_id)
            if not student:
                raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
            
            # If chapter not specified, use adaptive engine recommendation
            if not chapter_str:
                recommendation = adaptive_service.adaptive_engine.get_next_recommendation(student)
                chapter_str = recommendation.get("next_chapter", student.chapter)
            
            try:
                chapter = ChapterEnum(chapter_str)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid chapter: {chapter_str}. Available: {[c.value for c in ChapterEnum]}"
                )
            
            # Ensure we have a session ID for this adaptive learner
            adaptive_session_id = f"adaptive-{student_id}"
            if adaptive_session_id not in question_service._dedup_service._sessions:
                question_service._dedup_service.create_session()  # Create a new session
                # Reassign to the created session ID
                adaptive_session_id = list(question_service._dedup_service._sessions.keys())[-1]
            
            # Generate question
            question, question_id = question_service.generate_question(adaptive_session_id, chapter)
            
            # Cache the question for later answer checking
            adaptive_service._question_cache[question_id] = {
                "question": question,
                "student_id": student_id,
                "chapter": chapter_str
            }
            
            metadata = CHAPTER_METADATA.get(chapter, {})
            
            logger.info(f"Generated adaptive question {question_id} for student {student_id}")
            
            return QuestionResponse(
                success=True,
                questionId=question_id,
                chapter=chapter_str,
                chapterName=metadata.get('name', chapter_str),
                topic=question.topic,
                logicalTrap=question.logical_trap,
                dataRepresentation=question.data_representation,
                question=question.question_text,
                options=question.options,
                correctOptionIndex=question.correct_option_index,
                richNarrative=getattr(question, 'rich_narrative', None),
                richHtmlContent=getattr(question, 'rich_html_content', None),
                visualHints=getattr(question, 'visual_hints', None)
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating adaptive question: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Otherwise use session-based flow (original behavior)
    elif session_id:
        if not session_id:
            raise HTTPException(status_code=400, detail="Missing sessionId or studentId")
        
        # Choose random chapter if not specified
        if not chapter_str:
            import random
            chapter_str = random.choice([c.value for c in ChapterEnum])
        
        # Validate chapter
        try:
            chapter = ChapterEnum(chapter_str)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid chapter: {chapter_str}. Available: {[c.value for c in ChapterEnum]}"
            )
        
        try:
            # Generate question with deduplication
            question, question_id = question_service.generate_question(session_id, chapter)
            
            # Get metadata for this chapter
            metadata = CHAPTER_METADATA.get(chapter, {})
            
            logger.info(f"Generated question {question_id} for chapter {chapter_str}")
            
            return QuestionResponse(
                success=True,
                questionId=question_id,
                chapter=chapter_str,
                chapterName=metadata.get('name', chapter_str),
                topic=question.topic,
                logicalTrap=question.logical_trap,
                dataRepresentation=question.data_representation,
                question=question.question_text,
                options=question.options,
                correctOptionIndex=question.correct_option_index,
                richNarrative=getattr(question, 'rich_narrative', None),
                richHtmlContent=getattr(question, 'rich_html_content', None),
                visualHints=getattr(question, 'visual_hints', None)
            )
        
        except ValueError as e:
            logger.error(f"Question generation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    else:
        raise HTTPException(status_code=400, detail="Missing studentId or sessionId")


@app.post("/api/check-answer/{question_id}", response_model=CheckAnswerResponse)
async def check_answer(question_id: str, body: CheckAnswerRequest):
    """Check if the selected MCQ option is correct.
    
    Path parameters:
        question_id: The question ID from the generation response
    
    Request body:
    {
        "selectedIndex": 0-3,
        "studentId": "uuid-string" (optional, for adaptive learning)
    }
    
    Returns:
        CheckAnswerResponse with correctness, solution steps, and answer.
        If studentId provided, also includes misconception analysis.
    """
    question_service: QuestionService = app.state.question_service
    adaptive_service: AdaptiveLearningService = app.state.adaptive_service
    
    question = question_service.get_question_by_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    is_correct = body.selectedIndex == question.correct_option_index
    
    # Check if this is an adaptive learning request (has studentId)
    student_id = body.studentId if hasattr(body, 'studentId') else None
    misconception_detected = None
    teaching_points = []
    
    if student_id:
        try:
            # Check if question is in adaptive cache
            cached_q = adaptive_service._question_cache.get(question_id)
            if cached_q:
                # Process answer through adaptive learning service
                result = adaptive_service.process_student_answer(
                    student_id=student_id,
                    question_id=question_id,
                    selected_option_index=body.selectedIndex
                )
                
                if result.get("success"):
                    feedback = result.get("feedback", {})
                    is_correct = feedback.get("is_correct", is_correct)
                    misconception_detected = feedback.get("misconception", {}).get("type") if feedback.get("misconception") else None
                    teaching_points = feedback.get("misconception", {}).get("explanation", []) if feedback.get("misconception") else []
                    
                    logger.info(f"Recorded answer for student {student_id}: "
                              f"Question {question_id}, Correct: {is_correct}, "
                              f"Misconception: {misconception_detected}")
        except Exception as e:
            logger.error(f"Error recording adaptive learning attempt: {e}")
            # Fall through to non-adaptive answer checking
    
    logger.info(f"Answer check for {question_id}: {body.selectedIndex} vs {question.correct_option_index} = {is_correct}")
    
    response = CheckAnswerResponse(
        success=True,
        isCorrect=is_correct,
        correctIndex=question.correct_option_index,
        solutionSteps=question.solution_steps,
        answer=question.answer
    )
    
    return response


@app.get("/api/reveal/{question_id}", response_model=RevealAnswerResponse)
async def reveal_answer(question_id: str):
    """Reveal the solution and answer for a question.
    
    Path parameters:
        question_id: The question ID from the generation response
    
    Returns:
        RevealAnswerResponse with solution steps and answer
    """
    service: QuestionService = app.state.question_service
    question = service.get_question_by_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    logger.info(f"Revealing answer for {question_id}")
    
    return RevealAnswerResponse(
        success=True,
        solutionSteps=question.solution_steps,
        answer=question.answer
    )


@app.get("/api/categories", response_model=dict)
async def get_categories():
    """Get list of all available categories with metadata.
    
    Returns:
        {
            "success": true,
            "categories": [
                {
                    "id": "large_numbers",
                    "name": "Large Numbers",
                    "icon": "🔢",
                    "chapter": "Number Systems",
                    "description": "Place value, profit & loss"
                },
                ...
            ]
        }
    """
    categories = []
    for chapter in ChapterEnum:
        metadata = CHAPTER_METADATA.get(chapter, {})
        categories.append({
            "id": chapter.value,
            "name": metadata.get('name', chapter.value),
            "icon": metadata.get('icon', '📚'),
            "chapter": metadata.get('chapter', 'Uncategorized'),
            "description": metadata.get('description', '')
        })
    
    return {
        "success": True,
        "categories": categories
    }


@app.get("/api/session/{session_id}/stats", response_model=dict)
async def get_session_stats(session_id: str):
    """Get deduplication statistics for a session.
    
    Path parameters:
        session_id: The session ID
    
    Returns:
        {
            "success": true,
            "stats": {
                "unique_questions": 42,
                "duplicates_regenerated": 3,
                "success_rate": 93.3
            }
        }
    """
    service: QuestionService = app.state.question_service
    
    try:
        stats = service.get_session_stats(session_id)
        return {
            "success": True,
            "stats": stats
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/api/session/{session_id}")
async def end_session(session_id: str):
    """End a session and clean up resources.
    
    Path parameters:
        session_id: The session ID
    
    Returns:
        {
            "success": true,
            "message": "Session ended"
        }
    """
    service: QuestionService = app.state.question_service
    
    try:
        service.end_session(session_id)
        logger.info(f"Ended session: {session_id}")
        return {
            "success": True,
            "message": "Session ended"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "K.C. Nag Question Generator",
        "version": "2.0.0"
    }


# ============================================================================
# ADAPTIVE LEARNING ENDPOINTS - Student Management & Progress Tracking
# ============================================================================

@app.post("/api/student/register", response_model=Dict)
async def register_student(request: StudentRegistrationRequest):
    """Register a new student for adaptive learning.
    
    Request body:
    {
        "name": "Aditya",
        "chapter": "Ch1: The Fish Tale" (optional)
    }
    
    Returns:
        {
            "success": true,
            "studentId": "uuid-string",
            "name": "Aditya",
            "message": "Student registered successfully"
        }
    """
    service: AdaptiveLearningService = app.state.adaptive_service
    
    try:
        student_id = service.register_student(
            name=request.name,
            chapter=request.chapter or "Ch1: The Fish Tale"
        )
        
        logger.info(f"Registered new student: {request.name} ({student_id})")
        
        return {
            "success": True,
            "studentId": student_id,
            "name": request.name,
            "message": "Student registered successfully"
        }
    except Exception as e:
        logger.error(f"Error registering student: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/student/{student_id}/progress", response_model=StudentProgressResponse)
async def get_student_progress(student_id: str):
    """Get student learning progress and analytics.
    
    Path parameters:
        student_id: The student ID
    
    Returns:
        StudentProgressResponse with learning metrics and progress
    """
    service: AdaptiveLearningService = app.state.adaptive_service
    
    try:
        student = service.repository.get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
        
        logger.info(f"Retrieved progress for student {student_id}")
        
        return StudentProgressResponse(
            success=True,
            studentId=student_id,
            name="Student",  # Placeholder - student object doesn't store name in repository
            chapter=student.chapter or "Ch1: The Fish Tale",
            currentBloomLevel=student.current_bloom_level,  # Already lowercase from repository
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
# SESSION-BASED QUIZ ENDPOINTS (Frontend Integration)
# ============================================================================

from services.session_adapter import get_session_adapter


class SessionStartRequest(BaseModel):
    """Request to start a new quiz session."""
    student_id: str
    grade_level: int
    mode: str = "practice"  # "practice" or "assessment"
    chapter: Optional[str] = None


class SubmitAnswerRequest(BaseModel):
    """Request to submit an answer."""
    question_id: str
    answer_id: str
    time_spent: int = 0


@app.post("/api/quiz/session/start", response_model=Dict[str, Any])
async def start_quiz_session(request: SessionStartRequest):
    """Start a new quiz session.
    
    Request body:
    {
        "student_id": "uuid-string",
        "grade_level": 6,
        "mode": "practice",
        "chapter": "Ch1: The Fish Tale" (optional)
    }
    
    Returns:
        SessionStartResponse {
            sessionId: str,
            mode: str,
            classLevel: int,
            uiConfig: dict,
            student: dict,
            chapters: list
        }
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
    
    Path parameters:
        session_id: The session ID
    
    Returns:
        NextQuestionResponse with rich content fields
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


@app.post("/api/quiz/{session_id}/answer", response_model=Dict[str, Any])
async def submit_quiz_answer(session_id: str, request: SubmitAnswerRequest):
    """Submit an answer and get feedback.
    
    Path parameters:
        session_id: The session ID
    
    Request body:
    {
        "question_id": "uuid-string",
        "answer_id": "0",
        "time_spent": 30
    }
    
    Returns:
        SubmitAnswerResponse {
            isCorrect: bool,
            correctAnswerId: str,
            selectedAnswerId: str,
            feedback: dict,
            masteryScore: dict,
            streakUpdate: dict,
            solution: dict,
            misconceptionDetected: dict,
            logicalTrapTriggered: bool,
            trapDetails: dict,
            attemptNumber: int
        }
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


@app.get("/api/quiz/{session_id}/hint", response_model=Dict[str, Any])
async def get_quiz_hint(session_id: str, question_id: str, hint_index: int = 0):
    """Get a hint for the current question.
    
    Query parameters:
        question_id: The question ID
        hint_index: Which hint level (0, 1, 2, etc.)
    
    Returns:
        HintResponse {
            hintContent: str,
            hintType: str,
            hintIndex: int,
            remainingHints: int,
            maxHints: int,
            severity: int,
            displayFormat: str
        }
    """
    try:
        adapter = get_session_adapter()
        response = adapter.get_hint(
            session_id=session_id,
            question_id=question_id,
            hint_index=hint_index
        )
        logger.info(f"Retrieved hint for session {session_id}")
        return response
    except ValueError as e:
        logger.warning(f"Hint retrieval error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving hint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/quiz/{session_id}/state", response_model=Dict[str, Any])
async def get_quiz_session_state(session_id: str):
    """Get current session state (for resuming).
    
    Path parameters:
        session_id: The session ID
    
    Returns:
        SessionStartResponse with current progress
    """
    try:
        adapter = get_session_adapter()
        response = adapter.get_session_state(session_id)
        logger.info(f"Retrieved state for session {session_id}")
        return response
    except ValueError as e:
        logger.warning(f"Session state retrieval error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving session state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quiz/{session_id}/end", response_model=Dict[str, Any])
async def end_quiz_session(session_id: str):
    """End a quiz session and get final results.
    
    Path parameters:
        session_id: The session ID
    
    Returns:
        {
            sessionId: str,
            finalScore: int,
            totalQuestions: int,
            correctAnswers: int,
            accuracy: float,
            streak: int,
            masteryGains: dict,
            completedAt: str,
            recommendations: list
        }
    """
    try:
        adapter = get_session_adapter()
        response = adapter.end_session(session_id)
        logger.info(f"Ended session {session_id}")
        return response
    except ValueError as e:
        logger.warning(f"Session completion error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
