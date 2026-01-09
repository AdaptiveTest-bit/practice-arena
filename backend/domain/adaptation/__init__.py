"""
Adaptation Layer - Intelligent Question Sequencing

This module provides adaptive learning capabilities:
- ConceptGraph: Loads and queries prerequisite relationships
- MasteryTracker: Estimates student mastery per concept
- Sequencer: Chooses next concept + difficulty based on learning state
- AdaptiveQuestionSelector: Orchestrates full adaptive question selection

Usage:
    from domain.adaptation import get_adaptive_selector
    
    selector = get_adaptive_selector("factors_multiples")
    question, metadata = selector.select_question(student_id="student_123")
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
