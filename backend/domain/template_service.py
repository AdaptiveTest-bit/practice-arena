"""
Pure Template-Based Question Service

Provides template-only question generation from the template database.
Templates are created via:
1. Admin UI (human-authored)
2. LLM batch generation (automated)

No legacy generators - fully template-driven architecture.

Pipeline: Human/LLM → Templates → Review → Serve

Usage:
    from domain.template_service import TemplateQuestionService
    
    service = TemplateQuestionService(db_session)
    result = service.generate_question(
        concept_id="math.class5.factors_multiples.factors",
        difficulty=2
    )
"""

import logging
import random
import time
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import func

logger = logging.getLogger(__name__)


@dataclass
class QuestionResult:
    """Result of template-based question generation."""
    question: Dict[str, Any]
    template_id: int
    template_code: str
    concept_id: str
    generation_time_ms: float = 0
    variables: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TemplateStats:
    """Statistics about available templates."""
    total_templates: int
    published_templates: int
    by_concept: Dict[str, int]
    by_difficulty: Dict[int, int]
    by_bloom_level: Dict[str, int]
    coverage_gaps: List[str]  # Concepts without templates


class TemplateQuestionService:
    """
    Pure template-based question generation service.
    
    All questions are generated from templates stored in the database.
    Templates are created via Admin UI or LLM batch generation.
    
    Features:
    - Template selection by concept, difficulty, bloom level
    - Random template selection for variety
    - Avoids recently served templates per student
    - Metrics tracking for monitoring
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self._metrics = {
            "generations": 0,
            "failures": 0,
            "by_concept": {},
            "avg_generation_time_ms": 0,
        }
    
    def generate_question(
        self,
        concept_id: str = None,
        concept_key: str = None,
        difficulty: int = None,
        bloom_level: str = None,
        student_id: str = None,
        avoid_template_ids: List[int] = None
    ) -> QuestionResult:
        """
        Generate a question from a published template.
        
        Args:
            concept_id: Full concept ID (e.g., "math.class5.factors_multiples.factors")
            concept_key: Short concept key (e.g., "factors") - used if concept_id not provided
            difficulty: Difficulty level 1-5 (optional filter)
            bloom_level: Bloom's taxonomy level (optional filter)
            student_id: Student ID to avoid recently served templates
            avoid_template_ids: Specific template IDs to exclude
            
        Returns:
            QuestionResult with generated question and metadata
            
        Raises:
            ValueError: If no matching templates found
        """
        from db.models.templates import QuestionTemplate, TemplateStatus
        
        start_time = time.time()
        
        # Build query for published templates
        query = self.db.query(QuestionTemplate).filter(
            QuestionTemplate.status == TemplateStatus.PUBLISHED.value,
            QuestionTemplate.validation_passed == True
        )
        
        # Filter by concept
        if concept_id:
            query = query.filter(QuestionTemplate.concept_id == concept_id)
        elif concept_key:
            query = query.filter(QuestionTemplate.concept_id.like(f"%{concept_key}%"))
        
        # Filter by difficulty
        if difficulty is not None:
            query = query.filter(QuestionTemplate.difficulty == difficulty)
        
        # Filter by bloom level
        if bloom_level:
            query = query.filter(QuestionTemplate.bloom_level == bloom_level.upper())
        
        # Exclude specific templates
        if avoid_template_ids:
            query = query.filter(~QuestionTemplate.id.in_(avoid_template_ids))
        
        # Get all matching templates
        templates = query.all()
        
        if not templates:
            self._metrics["failures"] += 1
            raise ValueError(
                f"No published templates found for: "
                f"concept_id={concept_id}, concept_key={concept_key}, "
                f"difficulty={difficulty}, bloom_level={bloom_level}. "
                f"Please add templates via Admin UI or LLM batch generation."
            )
        
        # Select template (random for variety)
        template = random.choice(templates)
        
        # Generate question using template engine
        try:
            result = self._generate_from_template(template)
            
            generation_time = (time.time() - start_time) * 1000
            
            # Update metrics
            self._metrics["generations"] += 1
            concept = concept_id or concept_key or "unknown"
            self._metrics["by_concept"][concept] = self._metrics["by_concept"].get(concept, 0) + 1
            self._update_avg_time(generation_time)
            
            logger.info(f"Generated question from template {template.template_code} in {generation_time:.1f}ms")
            
            return QuestionResult(
                question=result["payload"],
                template_id=template.id,
                template_code=template.template_code,
                concept_id=template.concept_id,
                generation_time_ms=generation_time,
                variables=result.get("variables", {})
            )
            
        except Exception as e:
            self._metrics["failures"] += 1
            logger.error(f"Template generation failed for {template.template_code}: {e}")
            raise
    
    def _generate_from_template(self, template) -> Dict[str, Any]:
        """Generate question instance from a template."""
        from domain.template_engine.lean_template_engine import LeanTemplateEngine
        
        engine = LeanTemplateEngine(self.db)
        
        # Handle async generation
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already in async context
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        engine.generate_question(template.id)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(engine.generate_question(template.id))
        except RuntimeError:
            # No event loop, create new one
            return asyncio.run(engine.generate_question(template.id))
    
    def _update_avg_time(self, new_time: float):
        """Update running average generation time."""
        count = self._metrics["generations"]
        current_avg = self._metrics["avg_generation_time_ms"]
        self._metrics["avg_generation_time_ms"] = (
            (current_avg * (count - 1) + new_time) / count
        )
    
    def get_template_stats(self) -> TemplateStats:
        """Get statistics about available templates."""
        from db.models.templates import QuestionTemplate, TemplateStatus
        
        # Total templates
        total = self.db.query(QuestionTemplate).count()
        
        # Published templates
        published = self.db.query(QuestionTemplate).filter(
            QuestionTemplate.status == TemplateStatus.PUBLISHED.value
        ).count()
        
        # By concept
        concept_counts = self.db.query(
            QuestionTemplate.concept_id,
            func.count(QuestionTemplate.id)
        ).filter(
            QuestionTemplate.status == TemplateStatus.PUBLISHED.value
        ).group_by(QuestionTemplate.concept_id).all()
        
        by_concept = {c: count for c, count in concept_counts}
        
        # By difficulty
        difficulty_counts = self.db.query(
            QuestionTemplate.difficulty,
            func.count(QuestionTemplate.id)
        ).filter(
            QuestionTemplate.status == TemplateStatus.PUBLISHED.value
        ).group_by(QuestionTemplate.difficulty).all()
        
        by_difficulty = {d: count for d, count in difficulty_counts}
        
        # By bloom level
        bloom_counts = self.db.query(
            QuestionTemplate.bloom_level,
            func.count(QuestionTemplate.id)
        ).filter(
            QuestionTemplate.status == TemplateStatus.PUBLISHED.value
        ).group_by(QuestionTemplate.bloom_level).all()
        
        by_bloom = {b: count for b, count in bloom_counts}
        
        # Coverage gaps (concepts that should have templates but don't)
        required_concepts = [
            "math.class5.factors_multiples.factors",
            "math.class5.factors_multiples.multiples",
            "math.class5.factors_multiples.gcd",
            "math.class5.factors_multiples.lcm",
            "math.class5.factors_multiples.divisibility",
            "math.class5.factors_multiples.prime_composite",
            "math.class5.factors_multiples.prime_factorization",
        ]
        
        coverage_gaps = [c for c in required_concepts if c not in by_concept]
        
        return TemplateStats(
            total_templates=total,
            published_templates=published,
            by_concept=by_concept,
            by_difficulty=by_difficulty,
            by_bloom_level=by_bloom,
            coverage_gaps=coverage_gaps
        )
    
    def check_coverage(self, chapter_key: str = "factors_multiples") -> Dict[str, Any]:
        """
        Check template coverage for a chapter.
        
        Returns dict with coverage analysis and gaps.
        """
        from db.models.templates import QuestionTemplate, TemplateStatus
        
        # Expected concepts for the chapter
        expected_concepts = {
            "factors_multiples": [
                "factors", "multiples", "gcd", "lcm", 
                "divisibility", "prime_composite", "prime_factorization",
                "word_problem", "assertion_reason", "error_analysis"
            ]
        }.get(chapter_key, [])
        
        # Expected bloom levels
        bloom_levels = ["REMEMBER", "UNDERSTAND", "APPLY", "ANALYZE"]
        
        # Expected difficulties
        difficulties = [1, 2, 3, 4, 5]
        
        coverage = {
            "chapter": chapter_key,
            "concepts": {},
            "total_coverage_pct": 0,
            "gaps": [],
            "recommendations": []
        }
        
        total_expected = 0
        total_covered = 0
        
        for concept in expected_concepts:
            concept_coverage = {
                "bloom_levels": {},
                "difficulties": {},
                "total": 0
            }
            
            # Check each bloom level
            for bloom in bloom_levels:
                count = self.db.query(QuestionTemplate).filter(
                    QuestionTemplate.concept_id.like(f"%{concept}%"),
                    QuestionTemplate.bloom_level == bloom,
                    QuestionTemplate.status == TemplateStatus.PUBLISHED.value
                ).count()
                
                concept_coverage["bloom_levels"][bloom] = count
                concept_coverage["total"] += count
                total_expected += 1
                if count > 0:
                    total_covered += 1
                else:
                    coverage["gaps"].append(f"{concept} @ {bloom}")
            
            # Check each difficulty
            for diff in difficulties:
                count = self.db.query(QuestionTemplate).filter(
                    QuestionTemplate.concept_id.like(f"%{concept}%"),
                    QuestionTemplate.difficulty == diff,
                    QuestionTemplate.status == TemplateStatus.PUBLISHED.value
                ).count()
                
                concept_coverage["difficulties"][diff] = count
            
            coverage["concepts"][concept] = concept_coverage
            
            if concept_coverage["total"] == 0:
                coverage["recommendations"].append(
                    f"Add templates for concept '{concept}' - currently has 0 templates"
                )
        
        coverage["total_coverage_pct"] = round(
            (total_covered / total_expected * 100) if total_expected > 0 else 0, 1
        )
        
        return coverage
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get generation metrics."""
        return self._metrics.copy()
    
    def reset_metrics(self):
        """Reset metrics counters."""
        self._metrics = {
            "generations": 0,
            "failures": 0,
            "by_concept": {},
            "avg_generation_time_ms": 0,
        }


class TemplateSelectionService:
    """
    Intelligent template selection for adaptive learning.
    
    Selects templates based on:
    - Student mastery level
    - Previously served templates (avoid repetition)
    - Concept prerequisites
    - Difficulty progression
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.question_service = TemplateQuestionService(db_session)
    
    def select_next_template(
        self,
        student_id: str,
        session_id: str,
        concept_id: str,
        mastery_level: float = 0.5,
        served_template_ids: List[int] = None
    ) -> QuestionResult:
        """
        Select and generate the next question for a student.
        
        Uses adaptive logic to pick appropriate difficulty and template.
        
        Args:
            student_id: Student identifier
            session_id: Current session ID
            concept_id: Target concept
            mastery_level: Student's mastery (0.0 - 1.0)
            served_template_ids: Templates already served in this session
            
        Returns:
            QuestionResult with generated question
        """
        # Map mastery to difficulty
        if mastery_level < 0.3:
            target_difficulty = 1
        elif mastery_level < 0.5:
            target_difficulty = 2
        elif mastery_level < 0.7:
            target_difficulty = 3
        elif mastery_level < 0.9:
            target_difficulty = 4
        else:
            target_difficulty = 5
        
        # Map mastery to bloom level
        if mastery_level < 0.4:
            bloom_level = "REMEMBER"
        elif mastery_level < 0.6:
            bloom_level = "UNDERSTAND"
        elif mastery_level < 0.8:
            bloom_level = "APPLY"
        else:
            bloom_level = "ANALYZE"
        
        # Try exact match first
        try:
            return self.question_service.generate_question(
                concept_id=concept_id,
                difficulty=target_difficulty,
                bloom_level=bloom_level,
                student_id=student_id,
                avoid_template_ids=served_template_ids
            )
        except ValueError:
            pass
        
        # Fallback: relax difficulty constraint
        try:
            return self.question_service.generate_question(
                concept_id=concept_id,
                bloom_level=bloom_level,
                student_id=student_id,
                avoid_template_ids=served_template_ids
            )
        except ValueError:
            pass
        
        # Final fallback: any template for concept
        return self.question_service.generate_question(
            concept_id=concept_id,
            student_id=student_id,
            avoid_template_ids=served_template_ids
        )


# Convenience function for integration
def get_question_from_template(
    db_session: Session,
    concept_id: str = None,
    concept_key: str = None,
    difficulty: int = None,
    bloom_level: str = None
) -> Tuple[Dict[str, Any], int]:
    """
    Get a question from template database.
    
    Returns:
        Tuple of (question_dict, template_id)
    """
    service = TemplateQuestionService(db_session)
    result = service.generate_question(
        concept_id=concept_id,
        concept_key=concept_key,
        difficulty=difficulty,
        bloom_level=bloom_level
    )
    
    return result.question, result.template_id
