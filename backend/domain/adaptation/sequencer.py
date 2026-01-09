"""
Sequencer - Chooses next concept + difficulty based on learning state.

This is the core adaptive learning logic that:
1. Loads the concept graph (prerequisites)
2. Tracks student mastery
3. Recommends the optimal next concept and difficulty

Sequencing Strategies:
- MASTERY_FIRST: Focus on mastering prerequisites before advancing
- EXPLORATION: Balanced exposure to new concepts
- STRUGGLING_FOCUS: Prioritize concepts with low accuracy
- SPACED_REVIEW: Revisit mastered concepts to prevent decay
"""

import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

from .concept_graph import ConceptGraph
from .mastery import MasteryTracker, MasteryLevel


class SequencingStrategy(str, Enum):
    """Strategies for choosing the next concept."""
    MASTERY_FIRST = "mastery_first"     # Complete prerequisites before advancing
    EXPLORATION = "exploration"          # Balance new concepts with practice
    STRUGGLING_FOCUS = "struggling"      # Prioritize weak areas
    SPACED_REVIEW = "spaced_review"      # Mix mastered concepts for retention
    RANDOM = "random"                    # Random selection (for testing)


@dataclass
class SequencingTarget:
    """The recommended next question target."""
    concept_key: str          # Short key (e.g., "gcd")
    concept_id: str           # Full ID (e.g., "math.class5.factors_multiples.gcd")
    difficulty: int           # 1-5
    bloom_level: str          # "REMEMBER", "UNDERSTAND", "APPLY", etc.
    reason: str               # Why this was chosen
    priority: float           # 0.0 to 1.0 (higher = more urgent)
    
    def to_dict(self) -> Dict:
        return {
            "concept_key": self.concept_key,
            "concept_id": self.concept_id,
            "difficulty": self.difficulty,
            "bloom_level": self.bloom_level,
            "reason": self.reason,
            "priority": self.priority,
        }


class Sequencer:
    """
    Adaptive sequencer that chooses the next concept and difficulty.
    
    Usage:
        graph = ConceptGraph.load("math", 5, "factors_multiples")
        tracker = MasteryTracker(student_id="student_123")
        sequencer = Sequencer(graph, tracker)
        
        target = sequencer.get_next_target()
        print(f"Next: {target.concept_key} at difficulty {target.difficulty}")
        
        # After student answers
        tracker.record_attempt(target.concept_key, is_correct=True, difficulty=target.difficulty)
    """
    
    # Configuration
    DEFAULT_STRATEGY = SequencingStrategy.MASTERY_FIRST
    
    # Weights for concept selection
    STRUGGLING_WEIGHT = 2.0      # Weight for struggling concepts
    READY_WEIGHT = 1.5           # Weight for ready-to-learn concepts
    REVIEW_WEIGHT = 0.5          # Weight for mastered concepts (review)
    NEW_WEIGHT = 1.0             # Weight for never-attempted concepts
    
    # Spaced review settings
    REVIEW_INTERVAL_DAYS = 3     # Review mastered concepts every N days
    
    def __init__(
        self, 
        graph: ConceptGraph, 
        tracker: MasteryTracker,
        strategy: SequencingStrategy = None
    ):
        self.graph = graph
        self.tracker = tracker
        self.strategy = strategy or self.DEFAULT_STRATEGY
        
        # Session state
        self._session_concepts: List[str] = []  # Concepts served this session
        self._last_concept: Optional[str] = None
    
    def get_next_target(self) -> SequencingTarget:
        """
        Get the recommended next concept and difficulty.
        
        This is the main entry point for adaptive sequencing.
        """
        # Get candidate concepts with scores
        candidates = self._score_candidates()
        
        if not candidates:
            # Fallback: random from all concepts
            concept_key = random.choice(self.graph.get_all_concept_keys())
            return self._build_target(concept_key, reason="Random fallback (no candidates)")
        
        # Select best candidate (with some randomization to avoid monotony)
        selected = self._select_from_candidates(candidates)
        
        # Track for session diversity
        self._session_concepts.append(selected)
        self._last_concept = selected
        
        return self._build_target(selected, reason=candidates[selected]["reason"])
    
    def _score_candidates(self) -> Dict[str, Dict]:
        """
        Score all concepts for selection priority.
        
        Returns:
            Dict mapping concept_key -> {"score": float, "reason": str}
        """
        candidates = {}
        mastered_ids = set(self.tracker.get_mastered_concepts())
        struggling = set(self.tracker.get_struggling_concepts())
        
        # Convert concept_ids to keys for easier comparison
        mastered_keys = {self.graph.get_concept_key(cid) for cid in mastered_ids if self.graph.get_concept_key(cid)}
        struggling_keys = {self.graph.get_concept_key(cid) for cid in struggling if self.graph.get_concept_key(cid)}
        
        # Get concepts ready to learn (prerequisites met)
        ready_ids = self.graph.get_ready_concepts(mastered_ids)
        ready_keys = {self.graph.get_concept_key(cid) for cid in ready_ids}
        
        # Foundation concepts (no prerequisites)
        foundation_ids = self.graph.get_foundation_concepts()
        foundation_keys = {self.graph.get_concept_key(cid) for cid in foundation_ids}
        
        for concept_id in self.graph.get_all_concept_ids():
            concept_key = self.graph.get_concept_key(concept_id)
            # IMPORTANT: Use full concept_id for mastery lookup, not concept_key
            mastery = self.tracker.get_mastery(concept_id)
            
            score = 0.0
            reason = ""
            
            # Strategy-specific scoring
            if self.strategy == SequencingStrategy.STRUGGLING_FOCUS:
                if concept_key in struggling_keys:
                    score = self.STRUGGLING_WEIGHT
                    reason = "Struggling - needs practice"
                elif concept_key in ready_keys and concept_key not in mastered_keys:
                    score = self.READY_WEIGHT
                    reason = "Ready to learn (prereqs met)"
                elif concept_key in foundation_keys and mastery.total_attempts == 0:
                    score = self.NEW_WEIGHT
                    reason = "Foundation concept - start here"
                else:
                    score = 0.1
                    reason = "Low priority"
                    
            elif self.strategy == SequencingStrategy.MASTERY_FIRST:
                # PRIORITY 1: Continue with concepts already in progress (not mastered yet)
                # This keeps students on the same concept until they master it
                if mastery.total_attempts > 0 and concept_key not in mastered_keys:
                    # Concept has been started but not mastered - highest priority
                    if concept_key in struggling_keys:
                        score = self.STRUGGLING_WEIGHT * 2  # Very high priority for struggling
                        reason = "In progress - struggling (needs practice)"
                    else:
                        score = self.READY_WEIGHT * 2  # High priority for in-progress concepts
                        reason = "In progress - continue until mastery"
                        
                # PRIORITY 2: Foundation concepts not yet attempted
                elif concept_key in foundation_keys and concept_key not in mastered_keys:
                    if mastery.total_attempts == 0:
                        score = self.NEW_WEIGHT * 1.5
                        reason = "Foundation - start here"
                    else:
                        score = self.READY_WEIGHT
                        reason = "Foundation - needs mastery"
                        
                # PRIORITY 3: Ready to learn (prereqs met) but not started
                elif concept_key in ready_keys and concept_key not in mastered_keys:
                    if mastery.total_attempts == 0:
                        score = self.NEW_WEIGHT
                        reason = "Ready to learn (prereqs mastered)"
                    else:
                        score = self.READY_WEIGHT
                        reason = "In progress"
                        
                # PRIORITY 4: Mastered concepts - only for review
                elif concept_key in mastered_keys:
                    if self._needs_review(mastery):
                        score = self.REVIEW_WEIGHT
                        reason = "Spaced review"
                    else:
                        score = 0.1
                        reason = "Already mastered"
                else:
                    score = 0.1
                    reason = "Prerequisites not met"
                    
            elif self.strategy == SequencingStrategy.EXPLORATION:
                # Balance new concepts with practice
                if mastery.total_attempts == 0:
                    score = self.NEW_WEIGHT
                    reason = "New concept to explore"
                elif concept_key in struggling_keys:
                    score = self.STRUGGLING_WEIGHT * 0.8
                    reason = "Needs practice"
                elif concept_key not in mastered_keys:
                    score = self.READY_WEIGHT
                    reason = "In progress"
                else:
                    score = self.REVIEW_WEIGHT
                    reason = "Review"
                    
            elif self.strategy == SequencingStrategy.SPACED_REVIEW:
                if self._needs_review(mastery):
                    score = self.REVIEW_WEIGHT * 2
                    reason = "Due for review"
                elif concept_key in struggling_keys:
                    score = self.STRUGGLING_WEIGHT
                    reason = "Needs practice"
                else:
                    score = 0.5
                    reason = "Recent practice"
                    
            else:  # RANDOM
                score = 1.0
                reason = "Random selection"
            
            # Penalize if just served this session (variety)
            if concept_key in self._session_concepts[-3:]:
                score *= 0.3
                reason += " (recent, deprioritized)"
            
            if score > 0:
                candidates[concept_key] = {"score": score, "reason": reason}
        
        return candidates
    
    def _select_from_candidates(self, candidates: Dict[str, Dict]) -> str:
        """
        Select a concept from scored candidates.
        
        If there's a clear winner (score 2x higher than next), select deterministically.
        Otherwise use weighted random selection for variety.
        """
        if not candidates:
            return random.choice(self.graph.get_all_concept_keys())
        
        # Sort by score descending
        items = sorted(candidates.items(), key=lambda x: x[1]["score"], reverse=True)
        
        if len(items) == 1:
            return items[0][0]
        
        top_score = items[0][1]["score"]
        second_score = items[1][1]["score"]
        
        # If top score is significantly higher (2x or more), pick deterministically
        # This ensures we stay on "in progress" concepts rather than jumping around
        if second_score > 0 and top_score >= second_score * 2:
            return items[0][0]
        
        # Otherwise use weighted random selection
        weights = [c["score"] for _, c in items]
        total = sum(weights)
        
        if total == 0:
            return items[0][0]
        
        # Normalize weights
        weights = [w / total for w in weights]
        
        # Random selection
        r = random.random()
        cumulative = 0
        for (concept_key, _), weight in zip(items, weights):
            cumulative += weight
            if r <= cumulative:
                return concept_key
        
        return items[-1][0]
    
    def _needs_review(self, mastery) -> bool:
        """Check if a mastered concept needs spaced review."""
        if mastery.total_attempts == 0:
            return False
        if not mastery.is_mastered:
            return False
        if mastery.last_attempt is None:
            return True
        
        days_since = (datetime.now() - mastery.last_attempt).days
        return days_since >= self.REVIEW_INTERVAL_DAYS
    
    def _build_target(self, concept_key: str, reason: str) -> SequencingTarget:
        """Build a SequencingTarget from a concept key."""
        concept_id = self.graph.get_full_concept_id(concept_key)
        if concept_id is None:
            concept_id = f"math.class{self.graph.grade}.{self.graph.chapter_id}.{concept_key}"
        
        node = self.graph.get_node(concept_id)
        
        # Determine difficulty - use full concept_id for mastery lookup
        difficulty = self.tracker.get_recommended_difficulty(concept_id)
        
        # Determine bloom level
        if node and node.bloom_targets:
            bloom_level = node.bloom_targets[0]  # Use first target
        else:
            bloom_level = "APPLY"  # Default
        
        # Calculate priority - use full concept_id for mastery lookup
        mastery = self.tracker.get_mastery(concept_id)
        if mastery.total_attempts == 0:
            priority = 0.8  # High priority for new concepts
        elif mastery.accuracy < 0.5:
            priority = 0.9  # Highest priority for struggling
        elif mastery.is_mastered:
            priority = 0.3  # Low priority for mastered
        else:
            priority = 0.6  # Medium for in-progress
        
        return SequencingTarget(
            concept_key=concept_key,
            concept_id=concept_id,
            difficulty=difficulty,
            bloom_level=bloom_level,
            reason=reason,
            priority=priority,
        )
    
    def get_learning_path(self, target_concepts: List[str] = None) -> List[SequencingTarget]:
        """
        Generate a recommended learning path.
        
        Args:
            target_concepts: Optional list of concept keys to include
        
        Returns:
            Ordered list of SequencingTargets
        """
        path = []
        
        # Use topological order from graph
        ordered = self.graph.get_topological_order()
        
        for concept_id in ordered:
            concept_key = self.graph.get_concept_key(concept_id)
            
            # Filter by target if specified
            if target_concepts and concept_key not in target_concepts:
                continue
            
            # Skip already mastered - use full concept_id for mastery lookup
            if self.tracker.is_mastered(concept_id):
                continue
            
            target = self._build_target(concept_key, reason="Learning path")
            path.append(target)
        
        return path
    
    def get_session_plan(self, question_count: int = 10) -> List[SequencingTarget]:
        """
        Generate a session plan with specified number of questions.
        
        This pre-plans the session considering variety and progression.
        """
        plan = []
        temp_session = []
        
        for _ in range(question_count):
            # Temporarily track session for variety
            self._session_concepts = temp_session
            target = self.get_next_target()
            plan.append(target)
            temp_session.append(target.concept_key)
        
        # Restore session state
        self._session_concepts = []
        
        return plan
    
    def reset_session(self):
        """Reset session state for a new practice session."""
        self._session_concepts = []
        self._last_concept = None
    
    def set_strategy(self, strategy: SequencingStrategy):
        """Change the sequencing strategy."""
        self.strategy = strategy
    
    def get_progress_summary(self) -> Dict:
        """Get summary of student progress."""
        all_concepts = self.graph.get_all_concept_keys()
        mastered = self.tracker.get_mastered_concepts()
        struggling = self.tracker.get_struggling_concepts()
        
        return {
            "total_concepts": len(all_concepts),
            "mastered_count": len(mastered),
            "struggling_count": len(struggling),
            "mastery_percentage": len(mastered) / len(all_concepts) * 100 if all_concepts else 0,
            "mastered_concepts": [self.graph.get_concept_key(c) for c in mastered],
            "struggling_concepts": [self.graph.get_concept_key(c) for c in struggling],
            "session_attempts": self.tracker.get_session_summary(),
        }
    
    def __repr__(self) -> str:
        return f"Sequencer(strategy={self.strategy.value}, graph={self.graph}, tracker={self.tracker})"
