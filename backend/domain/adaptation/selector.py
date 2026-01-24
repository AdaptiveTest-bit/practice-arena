"""Adaptive Question Selector - Orchestrates intelligent question selection.

This service combines:
- ConceptGraph: Knows prerequisite relationships
- MasteryTracker: Tracks student mastery per concept
- Sequencer: Chooses optimal next target
- LeanTemplateEngine: Generates questions from database templates

All questions are generated from the QuestionTemplate database.
No legacy Python generators are used.

Usage:
    selector = AdaptiveQuestionSelector("factors_multiples", db_session)
    question_payload, metadata = await selector.select_question(student_id="abc123")
"""

from typing import Dict, Any, Tuple, Optional
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import func

from config.logging_config import get_logger
# Use relative imports to avoid circular import through __init__.py
from .concept_graph import ConceptGraph
from .mastery import MasteryTracker, MasteryLevel
from .sequencer import Sequencer, SequencingStrategy, SequencingTarget
from db.models import QuestionTemplate

logger = get_logger(__name__)


class AdaptiveQuestionSelector:
    """Orchestrates adaptive question selection using mastery tracking and templates.
    
    All questions are generated from QuestionTemplate database entries.
    Templates are selected based on:
    - concept_id: Matches the sequencer's target concept
    - difficulty: Matches the target difficulty level
    - status: Must be PUBLISHED
    
    Each template generates unique question instances through variable randomization.
    """

    # Map short concept keys (from graph YAML) to concept_id patterns in templates
    # Graph uses: fm_gcd, fm_factors, etc.
    # Templates use: math.class5.factors_multiples.gcd, etc.
    CONCEPT_KEY_TO_PATTERN = {
        "fm_divisibility": "divisibility",
        "fm_factors": "factors",
        "fm_multiples": "multiples",
        "fm_prime_composite": "prime_composite",
        "fm_factor_pairs": "factor_pairs",
        "fm_prime_factorization": "prime_factorization",
        "fm_common_factors": "common_factors",
        "fm_common_multiples": "common_multiples",
        "fm_gcd": "gcd",
        "fm_lcm": "lcm",
        "fm_word_problems": "word_problem",
    }

    def __init__(self, chapter_key: str = "factors_multiples", db_session: Session = None):
        """Initialize selector for a specific chapter.

        Args:
            chapter_key: Chapter to select questions for (e.g., "factors_multiples")
            db_session: SQLAlchemy session for template queries (required for select_question)
        """
        self.chapter_key = chapter_key
        self.db = db_session
        self._template_engine = None  # Lazy-loaded

        # Load concept graph
        try:
            self.graph = ConceptGraph.load(
                subject="math",
                grade=5,
                chapter_id=chapter_key,
            )
        except FileNotFoundError:
            logger.warning(f"No concept graph found for {chapter_key}, using empty graph")
            self.graph = ConceptGraph()

        # Per-student mastery trackers (in-memory cache)
        self._mastery_cache: Dict[str, MasteryTracker] = {}

        logger.info(f"✅ AdaptiveQuestionSelector initialized for '{chapter_key}' (template-based)")
        logger.info(f"   Concepts: {self.graph.get_all_concept_ids()}")

    @property
    def template_engine(self):
        """Lazy-load the template engine."""
        if self._template_engine is None:
            from domain.template_engine.lean_template_engine import LeanTemplateEngine
            self._template_engine = LeanTemplateEngine(self.db)
        return self._template_engine

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

    async def select_question(
        self,
        student_id: str,
        strategy: SequencingStrategy = SequencingStrategy.MASTERY_FIRST,
        difficulty_override: Optional[int] = None,
        concept_override: Optional[str] = None,
        excluded_template_ids: Optional[list] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Select the optimal next question for a student.

        Uses the sequencer to determine the best concept and difficulty,
        then finds a matching template and generates a unique question instance.

        Args:
            student_id: Student identifier
            strategy: Sequencing strategy to use
            difficulty_override: Force specific difficulty (1-4)
            concept_override: Force specific concept ID
            excluded_template_ids: Template IDs to exclude (already served in session)

        Returns:
            Tuple of (question_payload dict, metadata dict)
        
        Raises:
            ValueError: If no published template is found for the target concept
            ValueError: If db_session was not provided during initialization
        """
        if self.db is None:
            raise ValueError("db_session is required for select_question. Pass it to __init__.")
        
        mastery = self.get_mastery_tracker(student_id)
        sequencer = Sequencer(self.graph, mastery, strategy=strategy)

        # Get sequencing recommendation
        if concept_override:
            target = SequencingTarget(
                concept_key=concept_override.split(".")[-1] if "." in concept_override else concept_override,
                concept_id=concept_override,
                difficulty=difficulty_override or 2,
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

        # Find matching template from database
        template = self._find_template_for_target(target, excluded_template_ids)
        
        # Generate unique question instance from template
        result = await self.template_engine.generate_question(template.id)
        question_payload = result["payload"]
        
        # Add template_id for tracking
        question_payload["template_id"] = template.id

        # Build selection metadata
        concept_mastery = mastery.get_mastery(target.concept_id)
        metadata = {
            "selection": {
                "concept_id": target.concept_id,
                "concept_key": target.concept_key,
                "difficulty": target.difficulty,
                "bloom_level": target.bloom_level,
                "reason": target.reason,
                "strategy": strategy.value,
                "template_id": template.id,
            },
            "mastery": {
                "current_level": concept_mastery.level.name,
                "attempts": concept_mastery.total_attempts,
                "accuracy": concept_mastery.accuracy,
            },
            "progress": self._get_progress_summary(mastery, include_concept_lists=False),
            "correct_index": result.get("correct_index"),
            "variables": result.get("variables", {}),
        }

        logger.info(
            f"🎯 Selected template-based question for student {student_id[:8]}...: "
            f"concept={target.concept_id}, difficulty={target.difficulty}, "
            f"template_id={template.id}, reason='{target.reason}'"
        )

        return question_payload, metadata

    def _find_template_for_target(
        self, 
        target: SequencingTarget,
        excluded_ids: Optional[list] = None,
    ) -> QuestionTemplate:
        """Find a published template matching the sequencing target.
        
        Args:
            target: Sequencing target with concept and difficulty
            excluded_ids: Template IDs to exclude (for variety)
            
        Returns:
            QuestionTemplate from database
            
        Raises:
            ValueError: If no matching published template found
        """
        # Build concept pattern for matching
        # Templates may use: math.class5.factors_multiples.gcd or just gcd
        concept_key = self.CONCEPT_KEY_TO_PATTERN.get(target.concept_key, target.concept_key)
        
        # Try multiple patterns for flexibility
        patterns = [
            f"%{concept_key}",  # Ends with concept key
            f"%.{concept_key}",  # Has .concept_key
            f"math.class5.{self.chapter_key}.{concept_key}",  # Full path
        ]
        
        for pattern in patterns:
            query = self.db.query(QuestionTemplate).filter(
                QuestionTemplate.concept_id.like(pattern),
                QuestionTemplate.status == "PUBLISHED",
                QuestionTemplate.difficulty == target.difficulty,
            )
            
            # Exclude already-served templates for variety
            if excluded_ids:
                query = query.filter(~QuestionTemplate.id.in_(excluded_ids))
            
            # Random selection for variety
            template = query.order_by(func.random()).first()
            
            if template:
                return template
        
        # Try without difficulty constraint as fallback
        for pattern in patterns:
            query = self.db.query(QuestionTemplate).filter(
                QuestionTemplate.concept_id.like(pattern),
                QuestionTemplate.status == "PUBLISHED",
            )
            
            if excluded_ids:
                query = query.filter(~QuestionTemplate.id.in_(excluded_ids))
            
            template = query.order_by(func.random()).first()
            
            if template:
                logger.warning(
                    f"No template for difficulty={target.difficulty}, "
                    f"using template with difficulty={template.difficulty}"
                )
                return template
        
        raise ValueError(
            f"No published template found for concept='{target.concept_id}', "
            f"difficulty={target.difficulty}. Please create and publish templates in Admin UI."
        )

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
            "level_changed": True,
        }

    def _get_progress_summary(self, mastery: MasteryTracker, include_concept_lists: bool = True) -> Dict[str, Any]:
        """Generate progress summary for frontend display."""
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

        result = {
            "total_concepts": total,
            "mastered_count": len(mastered),
            "learning_count": len(learning),
            "not_started_count": len(not_started),
            "completion_percentage": round(len(mastered) / total * 100, 1),
        }
        
        if include_concept_lists:
            result["concepts_mastered"] = mastered
            result["concepts_learning"] = learning
            result["concepts_not_started"] = not_started
        
        return result

    def get_student_progress(self, student_id: str) -> Dict[str, Any]:
        """Get full progress report for a student."""
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
            "progress": self._get_progress_summary(mastery, include_concept_lists=True),
            "concepts": concept_details,
        }

    def get_template_coverage(self) -> Dict[str, Any]:
        """Get template coverage report for this chapter.
        
        Returns:
            Coverage info including concepts with/without templates
        """
        all_concepts = self.graph.get_all_concept_ids()
        coverage = {}
        
        for concept_id in all_concepts:
            concept_key = self.CONCEPT_KEY_TO_PATTERN.get(concept_id, concept_id)
            
            published_count = self.db.query(QuestionTemplate).filter(
                QuestionTemplate.concept_id.like(f"%{concept_key}"),
                QuestionTemplate.status == "PUBLISHED",
            ).count()
            
            draft_count = self.db.query(QuestionTemplate).filter(
                QuestionTemplate.concept_id.like(f"%{concept_key}"),
                QuestionTemplate.status.in_(["DRAFT", "REVIEW", "APPROVED"]),
            ).count()
            
            coverage[concept_id] = {
                "published": published_count,
                "draft": draft_count,
                "total": published_count + draft_count,
                "ready": published_count > 0,
            }
        
        total_concepts = len(all_concepts)
        ready_concepts = sum(1 for c in coverage.values() if c["ready"])
        
        return {
            "chapter": self.chapter_key,
            "total_concepts": total_concepts,
            "concepts_with_templates": ready_concepts,
            "coverage_percentage": round(ready_concepts / total_concepts * 100, 1) if total_concepts > 0 else 0,
            "concepts": coverage,
        }


# Factory function
def get_adaptive_selector(chapter_key: str = "factors_multiples", db_session: Session = None) -> AdaptiveQuestionSelector:
    """Create an AdaptiveQuestionSelector for a chapter.

    Args:
        chapter_key: Chapter key (e.g., "factors_multiples")
        db_session: SQLAlchemy session (REQUIRED)

    Returns:
        AdaptiveQuestionSelector instance
        
    Note: Unlike before, selectors are not cached because they require db_session.
    """
    return AdaptiveQuestionSelector(chapter_key, db_session)
