"""
Content Generation Module - Hybrid Neuro-Symbolic Architecture

This module implements the complete pipeline for generating rich questions:
1. Deterministic mathematical skeletons (SymPy)
2. K.C. Nag pedagogical story contexts (LLM or local templates)
3. Beautiful HTML/LaTeX rendering (Jinja2)

Architecture:
- models.py: Pydantic data models
- generators/: Question generation strategies
  - factors_multiples.py: Chapter 5 deterministic generators
  - kc_nag_story.py: Story context generation (LLM + fallback)
- renderer.py: Jinja2-based rendering
- service.py: Orchestration service
- templates/: Jinja2 HTML/LaTeX templates
"""

from .models import (
    RichQuestion,
    RichQuestionRequest,
    RichQuestionResponse,
    MathSkeleton,
    KCNagStoryContext,
    DifficultyLevel,
    BloomLevel,
)
from .service import RichQuestionService

__all__ = [
    "RichQuestion",
    "RichQuestionRequest",
    "RichQuestionResponse",
    "MathSkeleton",
    "KCNagStoryContext",
    "DifficultyLevel",
    "BloomLevel",
    "RichQuestionService",
]
