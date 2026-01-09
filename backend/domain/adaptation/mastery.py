"""
Mastery Tracker - Estimates student mastery per concept.

This module provides:
- Tracking correct/incorrect attempts per concept
- Simple mastery estimation (percentage-based)
- Mastery levels (NOT_STARTED, LEARNING, PRACTICED, MASTERED)
- Decay over time (optional)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple


class MasteryLevel(str, Enum):
    """Mastery levels for a concept."""
    NOT_STARTED = "not_started"    # No attempts yet
    LEARNING = "learning"          # < 50% correct
    PRACTICED = "practiced"        # 50-79% correct
    MASTERED = "mastered"          # >= 80% correct with minimum attempts


@dataclass
class ConceptAttempt:
    """A single attempt at a concept."""
    concept_id: str
    is_correct: bool
    difficulty: int
    timestamp: datetime = field(default_factory=datetime.now)
    time_taken_sec: Optional[float] = None


@dataclass
class ConceptMastery:
    """Mastery state for a single concept."""
    concept_id: str
    total_attempts: int = 0
    correct_attempts: int = 0
    last_attempt: Optional[datetime] = None
    
    # Track by difficulty
    attempts_by_difficulty: Dict[int, Tuple[int, int]] = field(default_factory=dict)  # difficulty -> (correct, total)
    
    @property
    def accuracy(self) -> float:
        """Current accuracy (0.0 to 1.0)."""
        if self.total_attempts == 0:
            return 0.0
        return self.correct_attempts / self.total_attempts
    
    @property
    def level(self) -> MasteryLevel:
        """Current mastery level."""
        if self.total_attempts == 0:
            return MasteryLevel.NOT_STARTED
        
        accuracy = self.accuracy
        
        # Require minimum attempts for mastery
        if accuracy >= 0.8 and self.total_attempts >= 5:
            return MasteryLevel.MASTERED
        elif accuracy >= 0.5:
            return MasteryLevel.PRACTICED
        else:
            return MasteryLevel.LEARNING
    
    @property
    def is_mastered(self) -> bool:
        """Check if concept is mastered."""
        return self.level == MasteryLevel.MASTERED


class MasteryTracker:
    """
    Tracks and estimates student mastery across concepts.
    
    Usage:
        tracker = MasteryTracker(student_id="student_123")
        tracker.record_attempt("gcd", is_correct=True, difficulty=2)
        mastery = tracker.get_mastery("gcd")
        print(f"GCD mastery: {mastery.accuracy:.0%} ({mastery.level.value})")
    """
    
    # Thresholds for mastery calculation
    MASTERY_THRESHOLD = 0.80       # 80% correct for mastery
    PRACTICED_THRESHOLD = 0.50    # 50% correct for practiced
    MIN_ATTEMPTS_FOR_MASTERY = 5  # Minimum attempts before declaring mastery
    
    # Time decay settings
    DECAY_ENABLED = True
    DECAY_HALF_LIFE_DAYS = 14     # Mastery decays to 50% after 14 days without practice
    
    def __init__(self, student_id: str, chapter_id: str = ""):
        self.student_id = student_id
        self.chapter_id = chapter_id
        self._mastery: Dict[str, ConceptMastery] = {}
        self._attempts: List[ConceptAttempt] = []
    
    def _get_or_create_mastery(self, concept_id: str) -> ConceptMastery:
        """Get or create mastery record for a concept."""
        if concept_id not in self._mastery:
            self._mastery[concept_id] = ConceptMastery(concept_id=concept_id)
        return self._mastery[concept_id]
    
    def record_attempt(
        self, 
        concept_id: str, 
        is_correct: bool, 
        difficulty: int = 2,
        time_taken_sec: Optional[float] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Record a student attempt at a concept.
        
        Args:
            concept_id: The concept being practiced (can be short key like "gcd")
            is_correct: Whether the answer was correct
            difficulty: Question difficulty (1-5)
            time_taken_sec: Time taken to answer
            timestamp: When the attempt occurred (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Record attempt
        attempt = ConceptAttempt(
            concept_id=concept_id,
            is_correct=is_correct,
            difficulty=difficulty,
            timestamp=timestamp,
            time_taken_sec=time_taken_sec,
        )
        self._attempts.append(attempt)
        
        # Update mastery
        mastery = self._get_or_create_mastery(concept_id)
        mastery.total_attempts += 1
        if is_correct:
            mastery.correct_attempts += 1
        mastery.last_attempt = timestamp
        
        # Track by difficulty
        if difficulty not in mastery.attempts_by_difficulty:
            mastery.attempts_by_difficulty[difficulty] = (0, 0)
        correct, total = mastery.attempts_by_difficulty[difficulty]
        mastery.attempts_by_difficulty[difficulty] = (
            correct + (1 if is_correct else 0),
            total + 1
        )
    
    def get_mastery(self, concept_id: str) -> ConceptMastery:
        """Get mastery state for a concept."""
        return self._get_or_create_mastery(concept_id)
    
    def get_mastery_level(self, concept_id: str) -> MasteryLevel:
        """Get mastery level for a concept."""
        return self.get_mastery(concept_id).level
    
    def is_mastered(self, concept_id: str) -> bool:
        """Check if concept is mastered."""
        return self.get_mastery(concept_id).is_mastered
    
    def get_mastered_concepts(self) -> List[str]:
        """Get list of mastered concept IDs."""
        return [cid for cid, m in self._mastery.items() if m.is_mastered]
    
    def get_struggling_concepts(self, threshold: float = 0.4) -> List[str]:
        """Get concepts where student is struggling (low accuracy with attempts)."""
        struggling = []
        for concept_id, mastery in self._mastery.items():
            if mastery.total_attempts >= 3 and mastery.accuracy < threshold:
                struggling.append(concept_id)
        return struggling
    
    def get_accuracy(self, concept_id: str) -> float:
        """Get accuracy for a concept (0.0 to 1.0)."""
        return self.get_mastery(concept_id).accuracy
    
    def get_accuracy_at_difficulty(self, concept_id: str, difficulty: int) -> Optional[float]:
        """Get accuracy at a specific difficulty level."""
        mastery = self.get_mastery(concept_id)
        if difficulty not in mastery.attempts_by_difficulty:
            return None
        correct, total = mastery.attempts_by_difficulty[difficulty]
        if total == 0:
            return None
        return correct / total
    
    def get_recommended_difficulty(self, concept_id: str) -> int:
        """
        Get recommended difficulty for next question.
        
        Strategy:
        - If accuracy > 80% at current level, increase difficulty
        - If accuracy < 50% at current level, decrease difficulty
        - Otherwise, stay at current level
        """
        mastery = self.get_mastery(concept_id)
        
        if mastery.total_attempts < 3:
            return 2  # Start at medium
        
        # Find current working difficulty
        current_difficulty = 2
        for diff in sorted(mastery.attempts_by_difficulty.keys(), reverse=True):
            correct, total = mastery.attempts_by_difficulty[diff]
            if total >= 2:
                accuracy = correct / total
                if accuracy >= 0.5:
                    current_difficulty = diff
                    break
        
        # Adjust based on recent performance
        overall_accuracy = mastery.accuracy
        if overall_accuracy >= 0.8 and current_difficulty < 4:
            return current_difficulty + 1
        elif overall_accuracy < 0.5 and current_difficulty > 1:
            return current_difficulty - 1
        
        return current_difficulty
    
    def get_recent_attempts(self, concept_id: str = None, limit: int = 10) -> List[ConceptAttempt]:
        """Get recent attempts, optionally filtered by concept."""
        attempts = self._attempts
        if concept_id:
            attempts = [a for a in attempts if a.concept_id == concept_id]
        return sorted(attempts, key=lambda a: a.timestamp, reverse=True)[:limit]
    
    def get_session_summary(self) -> Dict:
        """Get summary of current session."""
        if not self._attempts:
            return {
                "total_attempts": 0,
                "correct": 0,
                "accuracy": 0.0,
                "concepts_practiced": [],
            }
        
        correct = sum(1 for a in self._attempts if a.is_correct)
        concepts = list(set(a.concept_id for a in self._attempts))
        
        return {
            "total_attempts": len(self._attempts),
            "correct": correct,
            "accuracy": correct / len(self._attempts),
            "concepts_practiced": concepts,
        }
    
    def apply_time_decay(self):
        """Apply time decay to mastery estimates (optional)."""
        if not self.DECAY_ENABLED:
            return
        
        now = datetime.now()
        half_life = timedelta(days=self.DECAY_HALF_LIFE_DAYS)
        
        for concept_id, mastery in self._mastery.items():
            if mastery.last_attempt is None:
                continue
            
            days_since_practice = (now - mastery.last_attempt).days
            if days_since_practice <= 0:
                continue
            
            # Apply exponential decay factor
            decay_factor = 0.5 ** (days_since_practice / self.DECAY_HALF_LIFE_DAYS)
            
            # Decay the "effective" correct count (keep total the same)
            # This effectively reduces accuracy over time
            effective_correct = mastery.correct_attempts * decay_factor
            mastery.correct_attempts = int(effective_correct)
    
    def export_state(self) -> Dict:
        """Export tracker state for persistence."""
        return {
            "student_id": self.student_id,
            "chapter_id": self.chapter_id,
            "mastery": {
                cid: {
                    "total_attempts": m.total_attempts,
                    "correct_attempts": m.correct_attempts,
                    "last_attempt": m.last_attempt.isoformat() if m.last_attempt else None,
                    "attempts_by_difficulty": m.attempts_by_difficulty,
                }
                for cid, m in self._mastery.items()
            }
        }
    
    @classmethod
    def from_state(cls, state: Dict) -> "MasteryTracker":
        """Restore tracker from exported state."""
        tracker = cls(
            student_id=state["student_id"],
            chapter_id=state.get("chapter_id", ""),
        )
        
        for cid, mdata in state.get("mastery", {}).items():
            mastery = ConceptMastery(
                concept_id=cid,
                total_attempts=mdata["total_attempts"],
                correct_attempts=mdata["correct_attempts"],
                last_attempt=datetime.fromisoformat(mdata["last_attempt"]) if mdata["last_attempt"] else None,
                attempts_by_difficulty=mdata.get("attempts_by_difficulty", {}),
            )
            tracker._mastery[cid] = mastery
        
        return tracker
    
    def __repr__(self) -> str:
        mastered = len(self.get_mastered_concepts())
        return f"MasteryTracker(student={self.student_id}, {len(self._mastery)} concepts, {mastered} mastered)"
