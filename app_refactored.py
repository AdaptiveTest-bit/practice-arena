"""FastAPI application for K.C. Nag Mathematics Question Generator.

This refactored version uses:
- Strategy Pattern: Chapter-specific generators inherit from BaseChapterStrategy
- Factory Pattern: QuestionGeneratorFactory creates appropriate strategies
- Separation of Concerns: Business logic in QuestionService, models in Pydantic
- Session Management: Per-user deduplication tracking
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from models.question import (
    ChapterEnum, Question, QuestionResponse, 
    CheckAnswerRequest, CheckAnswerResponse, RevealAnswerResponse
)
from factory import QuestionGeneratorFactory
from services.question_service import QuestionService
from strategies.base import BaseChapterStrategy
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


# ============================================================================
# CONFIGURATION
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
    # STARTUP: Register all chapter strategies with the factory
    logger.info("Registering chapter strategies with factory...")
    QuestionGeneratorFactory.register(ChapterEnum.LARGE_NUMBERS, LargeNumbersStrategy)
    QuestionGeneratorFactory.register(ChapterEnum.DICE_LOGIC, DiceLogicStrategy)
    QuestionGeneratorFactory.register(ChapterEnum.CUBE_COUNTING, CubeCountingStrategy)
    QuestionGeneratorFactory.register(ChapterEnum.NETS, NetsStrategy)
    QuestionGeneratorFactory.register(ChapterEnum.DATA_HANDLING, DataHandlingStrategy)
    QuestionGeneratorFactory.register(ChapterEnum.CLOCK_ANGLES, ClockAnglesStrategy)
    QuestionGeneratorFactory.register(ChapterEnum.SYMMETRY, SymmetryStrategy)
    QuestionGeneratorFactory.register(ChapterEnum.ROTATION, RotationStrategy)
    QuestionGeneratorFactory.register(ChapterEnum.FACTORS_MULTIPLES, FactorsMultiplesStrategy)
    QuestionGeneratorFactory.register(ChapterEnum.FRACTIONS_DECIMALS, FractionsDecimalsStrategy)
    QuestionGeneratorFactory.register(ChapterEnum.GEOMETRY_MEASUREMENT, GeometryMeasurementStrategy)
    QuestionGeneratorFactory.register(ChapterEnum.DATA_PATTERNS, DataPatternsStrategy)
    logger.info(f"Registered {len(QuestionGeneratorFactory.list_chapters())} chapters")
    
    # Initialize global question service
    app.state.question_service = QuestionService()
    
    yield
    
    # SHUTDOWN: Clean up (if needed)
    logger.info("Shutting down question generator service...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="K.C. Nag Question Generator",
    description="CBSE Class 5 Mathematics with K.C. Nag pedagogical approach",
    version="2.0.0",
    lifespan=lifespan
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")


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

@app.get("/")
async def index():
    """Serve the main dashboard HTML."""
    return FileResponse("templates/index.html", media_type="text/html")


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
    
    Request body:
    {
        "sessionId": "session-uuid",
        "chapter": "large_numbers" | "dice_logic" | ... (optional, random if omitted)
    }
    
    Returns:
        QuestionResponse with all question details
    """
    service: QuestionService = app.state.question_service
    body = await request.json()
    
    session_id = body.get("sessionId")
    chapter_str = body.get("chapter")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing sessionId")
    
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
        question, question_id = service.generate_question(session_id, chapter)
        
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
            correctOptionIndex=question.correct_option_index
        )
    
    except ValueError as e:
        logger.error(f"Question generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/check-answer/{question_id}", response_model=CheckAnswerResponse)
async def check_answer(question_id: str, body: CheckAnswerRequest):
    """Check if the selected MCQ option is correct.
    
    Path parameters:
        question_id: The question ID from the generation response
    
    Request body:
    {
        "selectedIndex": 0-3
    }
    
    Returns:
        CheckAnswerResponse with correctness, solution steps, and answer
    """
    service: QuestionService = app.state.question_service
    question = service.get_question_by_id(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    is_correct = body.selectedIndex == question.correct_option_index
    
    logger.info(f"Answer check for {question_id}: {body.selectedIndex} vs {question.correct_option_index} = {is_correct}")
    
    return CheckAnswerResponse(
        success=True,
        isCorrect=is_correct,
        correctIndex=question.correct_option_index,
        solutionSteps=question.solution_steps,
        answer=question.answer
    )


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
