"""
Adaptation Layer - Intelligent Question Sequencing (Template-Based)

This module provides adaptive learning capabilities:
- ConceptGraph: Loads and queries prerequisite relationships
- MasteryTracker: Estimates student mastery per concept
- Sequencer: Chooses next concept + difficulty based on learning state
- AdaptiveQuestionSelector: Orchestrates full adaptive question selection from templates

All questions are generated from QuestionTemplate database entries.
No legacy Python generators are used.

Usage:
    from domain.adaptation import get_adaptive_selector
    from core.database import SessionLocal
    
    with SessionLocal() as db:
        selector = get_adaptive_selector("factors_multiples", db)
        question_payload, metadata = await selector.select_question(student_id="student_123")
"""

from .concept_graph import ConceptGraph
from .mastery import MasteryTracker, MasteryLevel
from .sequencer import Sequencer, SequencingStrategy, SequencingTarget
from .selector import AdaptiveQuestionSelector, get_adaptive_selector

__all__ = [
    "ConceptGraph",
    "MasteryTracker", 
    "MasteryLevel",
    "Sequencer",
    "SequencingStrategy",
    "SequencingTarget",
    "AdaptiveQuestionSelector",
    "get_adaptive_selector",
]
