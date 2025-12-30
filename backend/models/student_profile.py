"""
Student Learning Profile Model
Tracks student's cognitive level, misconceptions, and learning trajectory
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime
from models.cognitive_levels import BloomLevel
from models.distractor import MisconceptionType


class PerformanceStatus(str, Enum):
    """Student performance classification"""
    STRUGGLING = "struggling"      # < 50% accuracy
    DEVELOPING = "developing"      # 50-70% accuracy
    PROFICIENT = "proficient"      # 70-85% accuracy
    ADVANCED = "advanced"          # > 85% accuracy


class LearningPhase(str, Enum):
    """Bloom's cognitive progression phases"""
    FOUNDATIONAL = "foundational"       # REMEMBER + UNDERSTAND
    INTERMEDIATE = "intermediate"       # APPLY + ANALYZE
    ADVANCED = "advanced"               # EVALUATE + CREATE


@dataclass
class BloomLevelProgress:
    """Tracks progress within a Bloom's level"""
    bloom_level: BloomLevel
    questions_attempted: int = 0
    questions_correct: int = 0
    misconceptions_detected: List[MisconceptionType] = field(default_factory=list)
    
    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage"""
        if self.questions_attempted == 0:
            return 0.0
        return (self.questions_correct / self.questions_attempted) * 100
    
    @property
    def mastery(self) -> bool:
        """Student has mastered this level (accuracy > 80%)"""
        return self.accuracy > 80.0


@dataclass
class ChapterProgress:
    """Tracks progress within a chapter"""
    chapter_name: str
    bloom_progress: Dict[BloomLevel, BloomLevelProgress] = field(default_factory=dict)
    questions_attempted: int = 0
    questions_correct: int = 0
    topics_covered: List[str] = field(default_factory=list)
    
    @property
    def accuracy(self) -> float:
        """Overall chapter accuracy"""
        if self.questions_attempted == 0:
            return 0.0
        return (self.questions_correct / self.questions_attempted) * 100


@dataclass
class StudentProfile:
    """
    Complete student learning profile
    Tracks knowledge, misconceptions, and learning trajectory
    """
    student_id: str
    name: str
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    
    # Learning progress
    chapter_progress: Dict[str, ChapterProgress] = field(default_factory=dict)
    total_questions: int = 0
    total_correct: int = 0
    
    # Misconception tracking
    detected_misconceptions: Dict[MisconceptionType, int] = field(default_factory=dict)
    misconception_traps: Dict[MisconceptionType, List[str]] = field(default_factory=dict)
    
    # Learning preferences
    current_chapter: Optional[str] = None
    current_bloom_level: BloomLevel = BloomLevel.REMEMBER
    
    # Adaptive settings
    difficulty_adjustment: float = 1.0  # 0.5 = easier, 1.0 = normal, 1.5 = harder
    hint_level: int = 2  # 0 = no hints, 1 = basic, 2 = detailed, 3 = solution
    
    @property
    def overall_accuracy(self) -> float:
        """Overall accuracy across all questions"""
        if self.total_questions == 0:
            return 0.0
        return (self.total_correct / self.total_questions) * 100
    
    @property
    def performance_status(self) -> PerformanceStatus:
        """Classify student's overall performance"""
        accuracy = self.overall_accuracy
        if accuracy < 50:
            return PerformanceStatus.STRUGGLING
        elif accuracy < 70:
            return PerformanceStatus.DEVELOPING
        elif accuracy < 85:
            return PerformanceStatus.PROFICIENT
        else:
            return PerformanceStatus.ADVANCED
    
    @property
    def learning_phase(self) -> LearningPhase:
        """Determine current learning phase"""
        if self.current_bloom_level in [BloomLevel.REMEMBER, BloomLevel.UNDERSTAND]:
            return LearningPhase.FOUNDATIONAL
        elif self.current_bloom_level in [BloomLevel.APPLY, BloomLevel.ANALYZE]:
            return LearningPhase.INTERMEDIATE
        else:
            return LearningPhase.ADVANCED
    
    def record_attempt(
        self,
        chapter: str,
        bloom_level: BloomLevel,
        is_correct: bool,
        topic: str = "general",
        misconceptions_found: List[MisconceptionType] = None
    ) -> None:
        """Record a question attempt and update profile"""
        self.total_questions += 1
        if is_correct:
            self.total_correct += 1
        
        self.last_active = datetime.now()
        
        # Update chapter progress
        if chapter not in self.chapter_progress:
            self.chapter_progress[chapter] = ChapterProgress(chapter_name=chapter)
        
        ch_prog = self.chapter_progress[chapter]
        ch_prog.questions_attempted += 1
        if is_correct:
            ch_prog.questions_correct += 1
        
        if topic not in ch_prog.topics_covered:
            ch_prog.topics_covered.append(topic)
        
        # Update Bloom's level progress
        if bloom_level not in ch_prog.bloom_progress:
            ch_prog.bloom_progress[bloom_level] = BloomLevelProgress(bloom_level=bloom_level)
        
        bloom_prog = ch_prog.bloom_progress[bloom_level]
        bloom_prog.questions_attempted += 1
        if is_correct:
            bloom_prog.questions_correct += 1
        
        # Track misconceptions
        if misconceptions_found:
            for misconception in misconceptions_found:
                self.detected_misconceptions[misconception] = \
                    self.detected_misconceptions.get(misconception, 0) + 1
                
                if misconception not in self.misconception_traps:
                    self.misconception_traps[misconception] = []
                if topic not in self.misconception_traps[misconception]:
                    self.misconception_traps[misconception].append(topic)
                
                bloom_prog.misconceptions_detected.append(misconception)
    
    def get_top_misconceptions(self, limit: int = 5) -> List[tuple]:
        """Get most frequently detected misconceptions"""
        sorted_miscon = sorted(
            self.detected_misconceptions.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_miscon[:limit]
    
    def recommend_difficulty_adjustment(self) -> float:
        """Recommend difficulty adjustment based on performance"""
        accuracy = self.overall_accuracy
        
        if accuracy < 40:
            return 0.5  # Much easier
        elif accuracy < 60:
            return 0.75  # Easier
        elif accuracy > 90:
            return 1.5  # Harder
        elif accuracy > 80:
            return 1.25  # Slightly harder
        else:
            return 1.0  # Normal
