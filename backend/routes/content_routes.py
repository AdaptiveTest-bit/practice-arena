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


@router.get(
    "/cache/stats",
    summary="Get Cache Statistics",
    description="Monitor skeleton cache performance and hit rates"
)
async def get_cache_stats():
    """Get caching statistics."""
    from core.skeleton_cache import get_skeleton_cache
    from datetime import datetime

    cache = get_skeleton_cache()
    stats = cache.stats()

    return {
        "status": "operational",
        "skeleton_cache": stats,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/cache/story-stats",
    summary="Get Story Cache Statistics",
    description="Monitor story cache performance and hit rates"
)
async def get_story_cache_stats():
    """Get story cache statistics."""
    try:
        from core.story_cache import get_story_cache
        from datetime import datetime
        
        cache = get_story_cache()
        stats = cache.stats()
        
        return {
            "status": "operational",
            "story_cache": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@router.get(
    "/cache/options-stats",
    summary="Get Options Cache Statistics",
    description="Monitor options/distractors cache performance and hit rates"
)
async def get_options_cache_stats():
    """Get options cache statistics."""
    try:
        from core.options_cache import get_options_cache
        from datetime import datetime
        
        cache = get_options_cache()
        stats = cache.stats()
        
        return {
            "status": "operational",
            "options_cache": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@router.get(
    "/cache/all-stats",
    summary="Get All Cache Statistics",
    description="Monitor all caching layers (skeleton, story, options)"
)
async def get_all_cache_stats():
    """Get statistics for all cache layers."""
    try:
        from core.skeleton_cache import get_skeleton_cache
        from core.story_cache import get_story_cache
        from core.options_cache import get_options_cache
        from datetime import datetime
        
        skeleton_cache = get_skeleton_cache()
        story_cache = get_story_cache()
        options_cache = get_options_cache()
        
        return {
            "status": "operational",
            "caches": {
                "skeleton": skeleton_cache.stats(),
                "story": story_cache.stats(),
                "options": options_cache.stats()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@router.get(
    "/cache/question-stats",
    summary="Get Question Cache Statistics",
    description="Monitor full question cache performance (Redis + PostgreSQL)"
)
async def get_question_cache_stats():
    """Get question cache statistics."""
    try:
        from services.question_cache_service import get_question_cache_service
        from datetime import datetime
        
        service = get_question_cache_service()
        stats = service.stats()
        
        return {
            "status": "operational",
            "question_cache": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }