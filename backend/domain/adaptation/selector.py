"""Adaptive Question Selector - Orchestrates intelligent question selection.

This service combines:
- ConceptGraph: Knows prerequisite relationships
- MasteryTracker: Tracks student mastery per concept
- Sequencer: Chooses optimal next target
- Generator: Creates the actual question

Usage:
    selector = AdaptiveQuestionSelector("factors_multiples")
    question = selector.select_question(student_id="abc123")
"""

from typing import Dict, Any, Tuple
from typing import Optional

from config.logging_config import get_logger
from domain.adaptation.concept_graph import ConceptGraph
from domain.adaptation.mastery import MasteryTracker, MasteryLevel
from domain.adaptation.sequencer import Sequencer, SequencingStrategy, SequencingTarget
from domain.content_generation.generators.factors_multiples import FactorsMultiplesIntegrated
from api.models.quiz import Question

logger = get_logger(__name__)


# Alias for clarity
FactorsMultiplesGenerator = FactorsMultiplesIntegrated


class AdaptiveQuestionSelector:
    """Orchestrates adaptive question selection using mastery tracking and sequencing."""

    # Map chapter keys to generator classes
    # Note: Deprecated Notion CMS experiment removed in Phase 0 cleanup.
    GENERATORS = {
        "factors_multiples": FactorsMultiplesGenerator,
    }

    # Map concept IDs (from graph YAML) to generator concept keys
    # Graph uses: fm_divisibility, fm_factors, etc.
    # Generator uses: divisibility, factors, etc.
    CONCEPT_ID_TO_KEY = {
        "fm_divisibility": "divisibility",
        "fm_factors": "factors",
        "fm_multiples": "multiples",
        "fm_prime_composite": "prime_composite",
        "fm_factor_pairs": "factor_pairs",
        "fm_prime_factorization": "prime_factorization",
        "fm_common_factors": "factors",  # Uses factors generator
        "fm_common_multiples": "multiples",  # Uses multiples generator
        "fm_gcd": "gcd",
        "fm_lcm": "lcm",
        "fm_word_problems": "word_problem",
    }

    def __init__(self, chapter_key: str = "factors_multiples"):
        """Initialize selector for a specific chapter.

        Args:
            chapter_key: Chapter to select questions for (e.g., "factors_multiples")
        """
        self.chapter_key = chapter_key

        # Load concept graph using the class method
        try:
            self.graph = ConceptGraph.load(
                subject="math",
                grade=5,
                chapter_id=chapter_key,
            )
        except FileNotFoundError:
            logger.warning(f"No concept graph found for {chapter_key}, using empty graph")
            self.graph = ConceptGraph()

        # Create generator for this chapter
        generator_class = self.GENERATORS.get(chapter_key, FactorsMultiplesGenerator)
        self.generator = generator_class()

        # Per-student mastery trackers (in-memory cache, will be persisted to DB)
        self._mastery_cache: Dict[str, MasteryTracker] = {}

        logger.info(f"✅ AdaptiveQuestionSelector initialized for '{chapter_key}'")
        logger.info(f"   Concepts: {self.graph.get_all_concept_ids()}")

    def get_mastery_tracker(self, student_id: str) -> MasteryTracker:
        """Get or create mastery tracker for a student.

        Args:
            student_id: Student identifier

        Returns:
            MasteryTracker instance for this student
        """
        if student_id not in self._mastery_cache:
            self._mastery_cache[student_id] = MasteryTracker(
                student_id=student_id,
                chapter_id=self.chapter_key,
            )
            # TODO: Load from DB if exists
        return self._mastery_cache[student_id]

    def select_question(
        self,
        student_id: str,
        strategy: SequencingStrategy = SequencingStrategy.MASTERY_FIRST,
        difficulty_override: Optional[int] = None,
        concept_override: Optional[str] = None,
    ) -> Tuple[Question, Dict[str, Any]]:
        """Select the optimal next question for a student.

        Uses the sequencer to determine the best concept and difficulty,
        then generates a question targeting those parameters.

        Args:
            student_id: Student identifier
            strategy: Sequencing strategy to use
            difficulty_override: Force specific difficulty (1-3)
            concept_override: Force specific concept ID

        Returns:
            Tuple of (Question, metadata dict with selection info)
        """
        mastery = self.get_mastery_tracker(student_id)
        sequencer = Sequencer(self.graph, mastery, strategy=strategy)

        # Get sequencing recommendation
        if concept_override:
            # Teacher/admin forced a specific concept
            target = SequencingTarget(
                concept_key=concept_override.split(".")[-1] if "." in concept_override else concept_override,
                concept_id=concept_override,
                difficulty=difficulty_override or 1,
                bloom_level="APPLY",
                reason=f"Concept override: {concept_override}",
                priority=1.0
            )
        else:
            target = sequencer.get_next_target()

        # Override difficulty if specified
        if difficulty_override and target:
            target = SequencingTarget(
                concept_key=target.concept_key,
                concept_id=target.concept_id,
                difficulty=difficulty_override,
                bloom_level=target.bloom_level,
                reason=target.reason,
                priority=target.priority
            )

        # Use the concept_key directly from the target - it's already the short key
        # (e.g., "prime_composite", "factors", etc.)
        concept_key = target.concept_key

        # Generate question using the generator's generate() method
        question = self.generator.generate(
            concept_key=concept_key,
            difficulty=target.difficulty,
            bloom_level=None,  # Let generator pick appropriate bloom level
        )

        # Build selection metadata for frontend
        concept_mastery = mastery.get_mastery(target.concept_id)
        metadata = {
            "selection": {
                "concept_id": target.concept_id,
                "concept_key": target.concept_key,
                "difficulty": target.difficulty,
                "bloom_level": target.bloom_level,
                "reason": target.reason,
                "strategy": strategy.value,
            },
            "mastery": {
                "current_level": concept_mastery.level.name,
                "attempts": concept_mastery.total_attempts,
                "accuracy": concept_mastery.accuracy,
            },
            # Phase 1: Lean progress payload (no concept lists) for question responses
            "progress": self._get_progress_summary(mastery, include_concept_lists=False),
        }

        logger.info(
            f"🎯 Selected question for student {student_id[:8]}...: "
            f"concept={target.concept_id}, difficulty={target.difficulty}, "
            f"reason='{target.reason}'"
        )

        return question, metadata

    def record_attempt(
        self,
        student_id: str,
        concept_id: str,
        is_correct: bool,
        time_spent: int = 0,
    ) -> Dict[str, Any]:
        """Record an attempt and update mastery state.

        Args:
            student_id: Student identifier
            concept_id: Concept that was tested
            is_correct: Whether the answer was correct
            time_spent: Time spent in seconds

        Returns:
            Updated mastery info for this concept
        """
        mastery = self.get_mastery_tracker(student_id)
        mastery.record_attempt(concept_id, is_correct)

        # TODO: Persist to DB

        new_level = mastery.get_mastery_level(concept_id)
        concept_mastery = mastery.get_mastery(concept_id)

        logger.info(
            f"📊 Recorded attempt for {student_id[:8]}...: "
            f"concept={concept_id}, correct={is_correct}, new_level={new_level.name}"
        )

        return {
            "concept_id": concept_id,
            "mastery_level": new_level.name,
            "attempts": concept_mastery.total_attempts,
            "correct": concept_mastery.correct_attempts,
            "accuracy": concept_mastery.accuracy,
            "level_changed": True,  # TODO: Track actual level changes
        }

    def _get_progress_summary(self, mastery: MasteryTracker, include_concept_lists: bool = True) -> Dict[str, Any]:
        """Generate progress summary for frontend display.
        
        Args:
            mastery: MasteryTracker instance
            include_concept_lists: If True, include full concept lists (for full progress endpoint).
                                   If False, return lean payload (for question responses).
        """
        all_concepts = self.graph.get_all_concept_ids()

        mastered = []
        learning = []
        not_started = []

        for concept_id in all_concepts:
            level = mastery.get_mastery_level(concept_id)
            if level == MasteryLevel.MASTERED:
                mastered.append(concept_id)
            elif level in (MasteryLevel.LEARNING, MasteryLevel.PRACTICED):
                learning.append(concept_id)
            else:
                not_started.append(concept_id)

        total = len(all_concepts) if all_concepts else 1

        # Base lean payload (always returned)
        result = {
            "total_concepts": total,
            "mastered_count": len(mastered),
            "learning_count": len(learning),
            "not_started_count": len(not_started),
            "completion_percentage": round(len(mastered) / total * 100, 1),
        }
        
        # Phase 1: Only include full concept lists when explicitly requested
        # This reduces question payload by ~40% for chapters with many concepts
        if include_concept_lists:
            result["concepts_mastered"] = mastered
            result["concepts_learning"] = learning
            result["concepts_not_started"] = not_started
        
        return result

    def get_student_progress(self, student_id: str) -> Dict[str, Any]:
        """Get full progress report for a student.

        Args:
            student_id: Student identifier

        Returns:
            Detailed progress including mastery per concept
        """
        mastery = self.get_mastery_tracker(student_id)

        concept_details = {}
        for concept_id in self.graph.get_all_concept_ids():
            level = mastery.get_mastery_level(concept_id)
            concept_mastery = mastery.get_mastery(concept_id)
            prereqs = self.graph.get_prerequisites(concept_id)

            concept_details[concept_id] = {
                "mastery_level": level.name,
                "mastery_value": level.value,
                "attempts": concept_mastery.total_attempts,
                "correct": concept_mastery.correct_attempts,
                "accuracy": concept_mastery.accuracy,
                "prerequisites": list(prereqs),
            }

        return {
            "student_id": student_id,
            "chapter": self.chapter_key,
            # Full progress endpoint: include concept lists for dashboard/summary views
            "progress": self._get_progress_summary(mastery, include_concept_lists=True),
            "concepts": concept_details,
        }


# Singleton instance for the MVP chapter
_selector_cache: Dict[str, AdaptiveQuestionSelector] = {}


def get_adaptive_selector(chapter_key: str = "factors_multiples") -> AdaptiveQuestionSelector:
    """Get or create an AdaptiveQuestionSelector for a chapter.

    Args:
        chapter_key: Chapter key (e.g., "factors_multiples")

    Returns:
        AdaptiveQuestionSelector instance
    """
    if chapter_key not in _selector_cache:
        _selector_cache[chapter_key] = AdaptiveQuestionSelector(chapter_key)
    return _selector_cache[chapter_key]
