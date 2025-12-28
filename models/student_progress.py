"""Student progress tracking and mastery calculation models.

Tracks student performance across three dimensions:
1. Difficulty levels (1-5)
2. Bloom's cognitive levels (Remember → Create)
3. Misconceptions encountered

Used by the adaptive sequencing engine to recommend next question.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime
from models.distractor import MisconceptionType
from models.cognitive_levels import BloomLevel


class AttemptResult(BaseModel):
    """Record of a single student attempt at a question."""
    
    attempt_id: str = Field(..., description="Unique attempt identifier")
    student_id: str = Field(..., description="Student ID")
    question_id: str = Field(..., description="Question ID")
    chapter: str = Field(..., description="Chapter name")
    
    # Response Details
    response_selected: int = Field(..., ge=0, le=3, description="Option index (0-3)")
    is_correct: bool = Field(..., description="Whether answer was correct")
    time_spent_seconds: int = Field(..., ge=0, description="Time to answer")
    
    # Metadata about the question
    difficulty_level: int = Field(..., ge=1, le=5, description="Question difficulty (1-5)")
    bloom_level: BloomLevel = Field(..., description="Cognitive level")
    misconceptions_targeted: List[MisconceptionType] = Field(
        default_factory=list,
        description="Misconceptions targeted by question"
    )
    
    # Analysis
    misconception_revealed: Optional[MisconceptionType] = Field(
        None,
        description="If incorrect, which misconception was revealed"
    )
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True


class DifficultyMastery(BaseModel):
    """Mastery level for a specific difficulty (1-5)."""
    
    difficulty_level: int = Field(..., ge=1, le=5)
    attempts: int = Field(default=0, description="Number of attempts at this difficulty")
    correct: int = Field(default=0, description="Number of correct answers")
    percentage_correct: float = Field(default=0.0, ge=0, le=100)
    mastered: bool = Field(
        default=False,
        description="True if >= 80% correct (min 3 attempts)"
    )
    last_attempted: Optional[datetime] = None
    
    def update_from_attempt(self, is_correct: bool):
        """Update mastery after a new attempt."""
        self.attempts += 1
        if is_correct:
            self.correct += 1
        self.percentage_correct = (self.correct / self.attempts * 100) if self.attempts > 0 else 0
        self.mastered = self.percentage_correct >= 80 and self.attempts >= 3
        self.last_attempted = datetime.utcnow()


class BloomMastery(BaseModel):
    """Mastery level for a specific Bloom's cognitive level."""
    
    bloom_level: BloomLevel = Field(...)
    attempts: int = Field(default=0)
    correct: int = Field(default=0)
    percentage_correct: float = Field(default=0.0, ge=0, le=100)
    mastered: bool = Field(default=False)
    last_attempted: Optional[datetime] = None
    
    def update_from_attempt(self, is_correct: bool):
        """Update mastery after a new attempt."""
        self.attempts += 1
        if is_correct:
            self.correct += 1
        self.percentage_correct = (self.correct / self.attempts * 100) if self.attempts > 0 else 0
        self.mastered = self.percentage_correct >= 80 and self.attempts >= 3
        self.last_attempted = datetime.utcnow()


class MisconceptionEncounter(BaseModel):
    """Tracks encounters with a specific misconception."""
    
    misconception_type: MisconceptionType = Field(...)
    encounter_count: int = Field(default=0, description="How many times student made this error")
    first_encountered: Optional[datetime] = None
    last_encountered: Optional[datetime] = None
    remediation_provided: bool = Field(default=False)
    remediation_effective: bool = Field(default=False)
    
    def record_encounter(self):
        """Record that student made this error."""
        if self.encounter_count == 0:
            self.first_encountered = datetime.utcnow()
        self.encounter_count += 1
        self.last_encountered = datetime.utcnow()
    
    def mark_remediation_complete(self, effective: bool):
        """Mark remediation provided and whether it worked."""
        self.remediation_provided = True
        self.remediation_effective = effective


class StudentProgress(BaseModel):
    """Complete progress profile for a student."""
    
    student_id: str = Field(...)
    chapter: str = Field(description="Current chapter")
    
    # Attempt History
    total_attempts: int = Field(default=0)
    total_correct: int = Field(default=0)
    overall_percentage: float = Field(default=0.0, ge=0, le=100)
    
    # Difficulty Progression
    difficulty_mastery: Dict[int, DifficultyMastery] = Field(
        default_factory=lambda: {
            i: DifficultyMastery(difficulty_level=i) for i in range(1, 6)
        },
        description="Mastery at each difficulty level"
    )
    current_difficulty: int = Field(default=1, ge=1, le=5)
    
    # Bloom's Level Progression
    bloom_mastery: Dict[str, BloomMastery] = Field(
        default_factory=lambda: {
            level.value: BloomMastery(bloom_level=level) 
            for level in BloomLevel
        },
        description="Mastery at each cognitive level"
    )
    current_bloom_level: BloomLevel = Field(default=BloomLevel.REMEMBER)
    
    # Misconceptions
    misconceptions: Dict[str, MisconceptionEncounter] = Field(
        default_factory=dict,
        description="Tracked misconceptions"
    )
    
    # Timeline
    session_start: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
    
    def record_attempt(self, attempt: AttemptResult):
        """Record a new attempt and update all mastery metrics."""
        self.total_attempts += 1
        if attempt.is_correct:
            self.total_correct += 1
        self.overall_percentage = (self.total_correct / self.total_attempts * 100)
        self.last_activity = datetime.utcnow()
        
        # Update difficulty mastery
        diff_mastery = self.difficulty_mastery[attempt.difficulty_level]
        diff_mastery.update_from_attempt(attempt.is_correct)
        
        # Update Bloom mastery
        bloom_key = attempt.bloom_level
        if bloom_key not in self.bloom_mastery:
            self.bloom_mastery[bloom_key] = BloomMastery(bloom_level=bloom_key)
        self.bloom_mastery[bloom_key].update_from_attempt(attempt.is_correct)
        
        # Track misconceptions if incorrect
        if not attempt.is_correct and attempt.misconception_revealed:
            misc_key = attempt.misconception_revealed
            if misc_key not in self.misconceptions:
                self.misconceptions[misc_key] = MisconceptionEncounter(
                    misconception_type=misc_key
                )
            self.misconceptions[misc_key].record_encounter()
    
    def get_mastery_summary(self) -> Dict:
        """Get human-readable mastery summary."""
        return {
            "overall_percentage": self.overall_percentage,
            "total_attempts": self.total_attempts,
            "difficulty_levels": {
                level: {
                    "percentage": mastery.percentage_correct,
                    "mastered": mastery.mastered,
                    "attempts": mastery.attempts
                }
                for level, mastery in self.difficulty_mastery.items()
            },
            "bloom_levels": {
                level: {
                    "percentage": mastery.percentage_correct,
                    "mastered": mastery.mastered,
                    "attempts": mastery.attempts
                }
                for level, mastery in self.bloom_mastery.items()
            },
            "problem_misconceptions": [
                {
                    "type": misc.misconception_type,
                    "count": misc.encounter_count,
                    "needs_remediation": misc.encounter_count >= 2 and not misc.remediation_effective
                }
                for misc in self.misconceptions.values()
                if misc.encounter_count > 0
            ]
        }
    
    def should_advance_difficulty(self) -> bool:
        """Check if student is ready to advance difficulty."""
        mastery = self.difficulty_mastery[self.current_difficulty]
        # Advance if >= 80% correct with at least 3 attempts
        return mastery.mastered
    
    def should_retreat_difficulty(self) -> bool:
        """Check if student needs easier questions."""
        mastery = self.difficulty_mastery[self.current_difficulty]
        # Retreat if < 50% correct after 3+ attempts
        return mastery.percentage_correct < 50 and mastery.attempts >= 3
    
    def should_advance_bloom_level(self) -> bool:
        """Check if student is ready for higher cognitive level."""
        current_bloom_key = self.current_bloom_level
        mastery = self.bloom_mastery.get(current_bloom_key)
        if not mastery:
            return False
        # Only advance if current level is mastered
        return mastery.mastered
    
    def get_problem_misconceptions(self) -> List[MisconceptionType]:
        """Get list of misconceptions that need remediation."""
        return [
            MisconceptionType(misc_type)
            for misc_type, misc in self.misconceptions.items()
            if misc.encounter_count >= 2 and not misc.remediation_effective
        ]


class SequencingRecommendation(BaseModel):
    """Recommendation from sequencing engine for next question."""
    
    action: str = Field(
        ...,
        description="Action: 'advance', 'retreat', 'reinforce', 'remediate'"
    )
    next_difficulty: int = Field(..., ge=1, le=5)
    next_bloom_level: BloomLevel = Field(...)
    target_misconception: Optional[MisconceptionType] = Field(None)
    reason: str = Field(..., description="Explanation for recommendation")
    urgency: str = Field(
        default="normal",
        description="'low', 'normal', 'high' (for misconceptions)"
    )
    
    class Config:
        use_enum_values = True
