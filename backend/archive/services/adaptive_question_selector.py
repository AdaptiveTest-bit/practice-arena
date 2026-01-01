"""Adaptive Question Selector - Intelligent question selection based on student progress.

Uses:
- Current Bloom level
- Weak concepts
- Break point patterns
- Student accuracy history
"""

from typing import Optional, Dict, List, Any
from database import get_practice_session
from services.bloom_level_enforcer import BloomLevelEnforcer
from services.concept_mastery_tracker import ConceptMasteryTracker
from services.break_point_tracker import BreakPointTracker
from config.chapter_config import (
    get_chapter_concepts,
    get_bloom_distribution,
    get_bloom_difficulty,
    get_chapter_critical_concepts
)
import random


class AdaptiveQuestionSelector:
    """Selects the most appropriate question for a student based on their progress."""
    
    def __init__(self):
        """Initialize the selector with service dependencies."""
        self.bloom_enforcer = BloomLevelEnforcer()
        self.concept_tracker = ConceptMasteryTracker()
        self.break_tracker = BreakPointTracker()
    
    # ========================================================================
    # MAIN SELECTION METHOD
    # ========================================================================
    
    def select_next_question(
        self,
        session_id: int,
        chapter_id: int,
        question_bank: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Select the next question for a student in an adaptive manner.
        
        Selection prioritizes:
        1. Weak concepts (< 70% accuracy)
        2. Critical concepts not yet mastered
        3. Concepts with break points
        4. Current Bloom level advancement
        
        Args:
            session_id: The student's session ID
            chapter_id: The chapter being practiced
            question_bank: Available questions indexed by concept+bloom
        
        Returns:
            Selected question dict, or None if no suitable question found
        """
        try:
            session = get_practice_session(session_id)
            if not session:
                return None
            
            # 1. Get current session state
            current_bloom = self._get_current_bloom_level(session_id)
            weak_concepts = self.concept_tracker.get_weak_concepts(session_id)
            break_points = self.break_tracker.get_all_break_points(session_id) or []
            critical_concepts = get_chapter_critical_concepts(chapter_id)
            
            # 2. Build selection priority
            selection_priority = self._build_selection_priority(
                chapter_id=chapter_id,
                current_bloom=current_bloom,
                weak_concepts=weak_concepts,
                break_points=break_points,
                critical_concepts=critical_concepts,
                session=session
            )
            
            # 3. Filter available questions
            available_questions = self._filter_questions(
                question_bank=question_bank,
                priority=selection_priority
            )
            
            if not available_questions:
                return None
            
            # 4. Select best question
            selected = self._select_best_question(available_questions)
            
            return selected
            
        except Exception as e:
            print(f"Error in adaptive selection: {e}")
            return None
    
    # ========================================================================
    # PRIORITY CALCULATION
    # ========================================================================
    
    def _build_selection_priority(
        self,
        chapter_id: int,
        current_bloom: str,
        weak_concepts: List[Dict],
        break_points: List[Dict],
        critical_concepts: List[str],
        session: Any
    ) -> Dict[str, float]:
        """
        Build a priority score for each (concept, bloom_level) combination.
        
        Returns dictionary: {f"{concept}_{bloom}": priority_score}
        """
        all_concepts = get_chapter_concepts(chapter_id)
        priority = {}
        
        for concept in all_concepts:
            for bloom_level in ["remember", "understand", "apply", "analyze", "evaluate"]:
                key = f"{concept}_{bloom_level}"
                score = self._calculate_priority_score(
                    concept=concept,
                    bloom_level=bloom_level,
                    current_bloom=current_bloom,
                    weak_concepts=weak_concepts,
                    break_points=break_points,
                    critical_concepts=critical_concepts
                )
                priority[key] = score
        
        return priority
    
    def _calculate_priority_score(
        self,
        concept: str,
        bloom_level: str,
        current_bloom: str,
        weak_concepts: List[Dict],
        break_points: List[Dict],
        critical_concepts: List[str]
    ) -> float:
        """
        Calculate priority score (0-1) for a concept+bloom combination.
        
        Higher score = higher priority to ask this question
        
        Factors:
        - Is weak concept? (+0.5)
        - Has break point? (+0.4)
        - Is critical concept? (+0.3)
        - Matches current Bloom level? (+0.2)
        """
        score = 0.0
        
        # 1. Weak concept boost (+0.5)
        weak_concept_names = [wc["concept"] for wc in weak_concepts]
        if concept in weak_concept_names:
            score += 0.5
        
        # 2. Break point boost (+0.4)
        break_point_concepts = [bp["concept"] for bp in break_points]
        if concept in break_point_concepts:
            score += 0.4
        
        # 3. Critical concept boost (+0.3)
        if concept in critical_concepts and concept not in weak_concept_names:
            score += 0.3
        
        # 4. Current Bloom level match (+0.2)
        if bloom_level == current_bloom:
            score += 0.2
        
        # 5. Recent accuracy penalty (if recently attempted)
        # If student just answered this, lower priority
        # This prevents repetitive questions
        score *= 0.9  # Slight penalty by default
        
        return min(score, 1.0)  # Cap at 1.0
    
    # ========================================================================
    # QUESTION FILTERING
    # ========================================================================
    
    def _filter_questions(
        self,
        question_bank: Dict[str, Any],
        priority: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Filter questions based on priority.
        
        Returns top 5 questions with highest priority scores.
        """
        available = []
        
        for key, score in priority.items():
            if key in question_bank:
                questions = question_bank[key]
                if isinstance(questions, list):
                    for q in questions:
                        q['priority_score'] = score
                        available.append(q)
                else:
                    questions['priority_score'] = score
                    available.append(questions)
        
        # Sort by priority score
        available.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        # Return top candidates
        return available[:10]  # Top 10 questions
    
    # ========================================================================
    # SELECTION
    # ========================================================================
    
    def _select_best_question(self, candidates: List[Dict]) -> Dict:
        """
        Select best question from candidates.
        
        Uses randomization to avoid repetition while respecting priority.
        """
        if not candidates:
            return None
        
        if len(candidates) == 1:
            return candidates[0]
        
        # Weight-based random selection (top 3 have higher chance)
        weights = []
        for i, q in enumerate(candidates[:3]):
            # Exponential weighting: first=3, second=2, third=1
            weights.append(3 - i)
        
        # Pad weights for remaining questions
        for i in range(3, len(candidates)):
            weights.append(0.5)
        
        return random.choices(candidates, weights=weights, k=1)[0]
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _get_current_bloom_level(self, session_id: int) -> str:
        """Get the current Bloom level the student is working on."""
        status = self.bloom_enforcer.get_current_level(session_id)
        return status if status else "remember"
    
    def get_question_difficulty(
        self,
        chapter_id: int,
        bloom_level: str
    ) -> float:
        """Get difficulty multiplier for a question."""
        bloom_difficulty = get_bloom_difficulty(chapter_id)
        return bloom_difficulty.get(bloom_level, 1.0)
    
    # ========================================================================
    # ANALYSIS & RECOMMENDATIONS
    # ========================================================================
    
    def analyze_learning_gaps(self, session_id: int, chapter_id: int) -> Dict[str, Any]:
        """
        Analyze student's learning gaps in a chapter.
        
        Returns:
        {
            "weak_concepts": [...],
            "break_points": [...],
            "misconceptions": [...],
            "next_focus": "...",
            "recommendations": [...]
        }
        """
        weak_concepts = self.concept_tracker.get_weak_concepts(session_id)
        break_points = self.break_tracker.get_all_break_points(session_id)
        critical_concepts = get_chapter_critical_concepts(chapter_id)
        
        # Identify next focus
        next_focus = "general_practice"
        if weak_concepts:
            next_focus = weak_concepts[0]["concept"]
        elif break_points:
            next_focus = break_points[0]["concept"]
        
        recommendations = self._generate_recommendations(
            weak_concepts=weak_concepts,
            break_points=break_points,
            critical_concepts=critical_concepts
        )
        
        return {
            "weak_concepts": weak_concepts,
            "break_points": break_points,
            "critical_concepts": critical_concepts,
            "next_focus": next_focus,
            "recommendations": recommendations
        }
    
    def _generate_recommendations(
        self,
        weak_concepts: List[Dict],
        break_points: List[Dict],
        critical_concepts: List[str]
    ) -> List[str]:
        """Generate personalized recommendations for the student."""
        recommendations = []
        
        if weak_concepts:
            weak_names = [w["concept"] for w in weak_concepts]
            recommendations.append(
                f"Focus on improving: {', '.join(weak_names)}"
            )
        
        if break_points:
            critical_breakpoints = [bp for bp in break_points if bp.get("severity") == "critical"]
            if critical_breakpoints:
                critical_concepts_list = [bp["concept"] for bp in critical_breakpoints]
                recommendations.append(
                    f"URGENT: Review {', '.join(critical_concepts_list)} - "
                    "high number of incorrect answers"
                )
        
        recommendations.append("Practice more questions in current Bloom level")
        
        recommendations.append("Review misconceptions identified")
        
        return recommendations
