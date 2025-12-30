"""
Rich Question API Routes

Endpoints for rich question generation and retrieval.
Integrates hybrid neuro-symbolic pipeline into practice routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from content.models import RichQuestionRequest, RichQuestionResponse, DifficultyLevel, BloomLevel
from content.service import RichQuestionService


# Initialize router
router = APIRouter(prefix="/api/content", tags=["content"])

# Service dependency
def get_rich_question_service() -> RichQuestionService:
    """Dependency injection for RichQuestionService"""
    return RichQuestionService()


@router.post(
    "/question/rich",
    response_model=RichQuestionResponse,
    summary="Generate a Rich Question (Hybrid Neuro-Symbolic)",
    description="""
    Generate a complete rich question combining:
    - Deterministic mathematical skeleton (SymPy)
    - K.C. Nag story context (LLM)
    - Beautifully rendered output (Jinja2)
    """,
)
async def generate_rich_question(
    request: RichQuestionRequest,
    service: RichQuestionService = Depends(get_rich_question_service),
) -> RichQuestionResponse:
    """
    Generate a single rich question.
    
    Request parameters:
    - chapter_id: Chapter identifier (e.g., 'ch5')
    - concept: Specific concept (e.g., 'factors', 'multiples')
    - difficulty: Difficulty level (easy, medium, hard, expert)
    - bloom_level: Cognitive level (remember, understand, apply, analyze, evaluate, create)
    - theme: Optional narrative theme (e.g., 'cooking', 'sports')
    
    Response includes:
    - Complete RichQuestion with skeleton + story + rendered HTML/LaTeX
    - Generation time in milliseconds
    - Validation status
    """
    
    response = service.generate_rich_question(request)
    
    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)
    
    return response


@router.get(
    "/question/rich/{question_id}",
    response_model=dict,
    summary="Get a Rich Question by ID",
)
async def get_rich_question(
    question_id: str,
    service: RichQuestionService = Depends(get_rich_question_service),
) -> dict:
    """
    Retrieve a previously generated rich question.
    
    Note: Currently generates on-demand. In production, would fetch from database.
    """
    
    return {
        "error": "This endpoint requires database persistence. Use POST /api/content/question/rich to generate new questions.",
        "question_id": question_id,
    }


@router.post(
    "/question/batch",
    response_model=dict,
    summary="Generate a Batch of Rich Questions",
)
async def generate_question_batch(
    chapter_id: str,
    concept: str,
    difficulty: DifficultyLevel,
    count: int = 5,
    service: RichQuestionService = Depends(get_rich_question_service),
) -> dict:
    """
    Generate multiple rich questions for a concept.
    
    Useful for creating comprehensive question banks.
    Returns a batch of validated, unique questions.
    """
    
    questions = service.generate_batch(
        chapter_id=chapter_id,
        concept=concept,
        difficulty=difficulty,
        count=count,
    )
    
    return {
        "success": len(questions) > 0,
        "chapter_id": chapter_id,
        "concept": concept,
        "difficulty": difficulty.value,
        "requested_count": count,
        "generated_count": len(questions),
        "questions": [
            {
                "id": q.id,
                "concept": q.skeleton.concept,
                "difficulty": q.skeleton.difficulty.value,
                "answer": str(q.skeleton.solution),
            }
            for q in questions
        ],
    }


@router.get(
    "/chapter/{chapter_id}/concepts",
    response_model=dict,
    summary="List Available Concepts for a Chapter",
)
async def get_chapter_concepts(chapter_id: str) -> dict:
    """
    List all available concepts for a given chapter.
    
    Example response for ch5:
    {
        "chapter_id": "ch5",
        "title": "Factors & Multiples",
        "concepts": ["factors", "multiples", "gcd", "lcm", "prime", "composite"]
    }
    """
    
    # Chapter definitions
    chapters = {
        "ch5": {
            "title": "Factors & Multiples",
            "concepts": ["factors", "multiples", "gcd", "lcm", "prime", "composite"],
        },
        # More chapters coming...
    }
    
    if chapter_id not in chapters:
        raise HTTPException(
            status_code=404,
            detail=f"Chapter {chapter_id} not found. Available: {list(chapters.keys())}",
        )
    
    chapter = chapters[chapter_id]
    
    return {
        "chapter_id": chapter_id,
        "title": chapter["title"],
        "concepts": chapter["concepts"],
        "status": "Available",
    }


@router.get(
    "/health",
    summary="Health Check for Content Generation Pipeline",
)
async def health_check(
    service: RichQuestionService = Depends(get_rich_question_service),
) -> dict:
    """
    Verify that the content generation pipeline is healthy.
    
    Tests:
    - SymPy skeleton generator working
    - Story generator accessible (LLM or local fallback)
    - Renderer functional
    """
    
    try:
        # Quick test: generate a simple question
        request = RichQuestionRequest(
            chapter_id="ch5",
            concept="factors",
            difficulty=DifficultyLevel.EASY,
        )
        
        response = service.generate_rich_question(request)
        
        return {
            "status": "healthy",
            "pipeline": "hybrid_neuro_symbolic",
            "generators": {
                "skeleton": "SymPy (FactorsMultiplesGenerator)",
                "story": "K.C. Nag Pedagogical Context",
                "renderer": "Jinja2",
            },
            "test_generation": {
                "success": response.success,
                "generation_time_ms": response.generation_time_ms,
                "question_id": response.question.id if response.question else None,
            },
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }
