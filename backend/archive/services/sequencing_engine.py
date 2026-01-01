"""Adaptive Sequencing Engine - Phase 4 Core Intelligence

Recommends the next question based on student performance across three dimensions:
1. Difficulty level (1-5)
2. Bloom's cognitive level (Remember → Create)
3. Misconception patterns

This is the "intelligent librarian" that decides what question to show next.
"""

from typing import Optional, Tuple
from models.student_progress import StudentProgress, SequencingRecommendation
from models.distractor import MisconceptionType
from models.cognitive_levels import BloomLevel


class AdaptiveSequencingEngine:
    """
    Intelligent question sequencing based on student performance.
    
    Algorithm considers:
    - Current difficulty mastery (0-100%)
    - Bloom's level readiness
    - Misconception history
    - Time spent (pacing)
    - Error patterns
    """
    
    # Constants for decision logic
    MASTERY_THRESHOLD = 80  # % correct to consider mastered
    MIN_ATTEMPTS = 3  # Minimum attempts before considering mastery
    RETREAT_THRESHOLD = 50  # % correct to consider retreat
    REMEDIATION_TRIGGER = 2  # Number of errors to trigger remediation
    
    @staticmethod
    def get_next_recommendation(student_progress: StudentProgress) \
            -> SequencingRecommendation:
        """
        Main entry point: Get sequencing recommendation for student.
        
        Returns: SequencingRecommendation with:
        - action: 'advance', 'retreat', 'reinforce', or 'remediate'
        - next_difficulty: Recommended difficulty (1-5)
        - next_bloom_level: Recommended cognitive level
        - target_misconception: If remediation needed
        - reason: Human-readable explanation
        - urgency: 'low', 'normal', or 'high'
        """
        
        # Step 1: Check for problem misconceptions (highest priority)
        problem_misconceptions = student_progress.get_problem_misconceptions()
        if problem_misconceptions:
            return AdaptiveSequencingEngine._create_remediation_recommendation(
                student_progress,
                problem_misconceptions[0]
            )
        
        # Step 2: Check difficulty progression
        if student_progress.should_retreat_difficulty():
            return AdaptiveSequencingEngine._create_retreat_recommendation(
                student_progress
            )
        
        if student_progress.should_advance_difficulty():
            return AdaptiveSequencingEngine._create_advance_difficulty_recommendation(
                student_progress
            )
        
        # Step 3: Check Bloom's level progression
        if student_progress.should_advance_bloom_level():
            return AdaptiveSequencingEngine._create_advance_bloom_recommendation(
                student_progress
            )
        
        # Step 4: Default: Reinforce current level
        return AdaptiveSequencingEngine._create_reinforce_recommendation(
            student_progress
        )
    
    @staticmethod
    def _create_remediation_recommendation(
        progress: StudentProgress,
        misconception: MisconceptionType
    ) -> SequencingRecommendation:
        """Create remediation recommendation for specific misconception."""
        
        misconception_obj = progress.misconceptions[misconception.value]
        
        return SequencingRecommendation(
            action="remediate",
            next_difficulty=max(1, progress.current_difficulty - 1),  # Easier questions
            next_bloom_level=BloomLevel.UNDERSTAND,  # Simpler cognitive level
            target_misconception=misconception,
            reason=f"Student made {misconception_obj.encounter_count} errors in "
                   f"{misconception.value.replace('_', ' ')} concept. "
                   f"Need targeted remediation.",
            urgency="high" if misconception_obj.encounter_count >= 3 else "normal"
        )
    
    @staticmethod
    def _create_retreat_recommendation(
        progress: StudentProgress
    ) -> SequencingRecommendation:
        """Create recommendation to go back to easier difficulty."""
        
        current_mastery = progress.difficulty_mastery[progress.current_difficulty]
        
        return SequencingRecommendation(
            action="retreat",
            next_difficulty=max(1, progress.current_difficulty - 1),
            next_bloom_level=progress.current_bloom_level,
            reason=f"Student struggling at difficulty {progress.current_difficulty} "
                   f"({current_mastery.percentage_correct:.0f}% correct after "
                   f"{current_mastery.attempts} attempts). "
                   f"Moving to easier difficulty to rebuild confidence.",
            urgency="high"
        )
    
    @staticmethod
    def _create_advance_difficulty_recommendation(
        progress: StudentProgress
    ) -> SequencingRecommendation:
        """Create recommendation to advance difficulty."""
        
        next_difficulty = min(5, progress.current_difficulty + 1)
        current_mastery = progress.difficulty_mastery[progress.current_difficulty]
        
        return SequencingRecommendation(
            action="advance",
            next_difficulty=next_difficulty,
            next_bloom_level=progress.current_bloom_level,
            reason=f"Student mastered difficulty {progress.current_difficulty} "
                   f"({current_mastery.percentage_correct:.0f}% correct over "
                   f"{current_mastery.attempts} attempts). "
                   f"Ready for challenge!",
            urgency="low"
        )
    
    @staticmethod
    def _create_advance_bloom_recommendation(
        progress: StudentProgress
    ) -> SequencingRecommendation:
        """Create recommendation to advance Bloom's level."""
        
        # Find next Bloom's level
        bloom_sequence = [
            BloomLevel.REMEMBER,
            BloomLevel.UNDERSTAND,
            BloomLevel.APPLY,
            BloomLevel.ANALYZE,
            BloomLevel.EVALUATE,
            BloomLevel.CREATE
        ]
        
        current_index = bloom_sequence.index(progress.current_bloom_level)
        next_bloom = bloom_sequence[min(current_index + 1, len(bloom_sequence) - 1)]
        
        current_mastery = progress.bloom_mastery[progress.current_bloom_level]
        
        return SequencingRecommendation(
            action="advance",
            next_difficulty=progress.current_difficulty,
            next_bloom_level=next_bloom,
            reason=f"Student mastered {progress.current_bloom_level} level "
                   f"({current_mastery.percentage_correct:.0f}% correct). "
                   f"Ready for higher-order thinking!",
            urgency="low"
        )
    
    @staticmethod
    def _create_reinforce_recommendation(
        progress: StudentProgress
    ) -> SequencingRecommendation:
        """Create recommendation to reinforce current level."""
        
        current_diff = progress.current_difficulty
        current_bloom = progress.current_bloom_level
        current_mastery = progress.difficulty_mastery[current_diff]
        
        return SequencingRecommendation(
            action="reinforce",
            next_difficulty=current_diff,
            next_bloom_level=current_bloom,
            reason=f"Continuing practice at difficulty {current_diff}, "
                   f"{current_bloom.value} level. "
                   f"Current mastery: {current_mastery.percentage_correct:.0f}% "
                   f"({current_mastery.attempts} attempts). "
                   f"Keep building confidence!",
            urgency="normal"
        )


class QuestionSelector:
    """
    Selects specific question matching sequencing recommendation.
    
    This works with the question generation system to find/create
    a question that matches:
    - Recommended difficulty
    - Recommended Bloom's level
    - Optional misconception target
    """
    
    @staticmethod
    def get_selection_criteria(
        recommendation: SequencingRecommendation
    ) -> dict:
        """
        Convert recommendation to question selection criteria.
        
        Returns: Dict with filters for question generation
        Example:
        {
            'difficulty': 3,
            'bloom_level': 'APPLY',
            'misconception_target': None,  # or MisconceptionType
            'chapter': 'fractions_decimals'
        }
        """
        
        criteria = {
            'difficulty': recommendation.next_difficulty,
            'bloom_level': recommendation.next_bloom_level,
            'misconception_target': recommendation.target_misconception,
            'action': recommendation.action
        }
        
        return criteria
    
    @staticmethod
    def generate_context_message(
        recommendation: SequencingRecommendation
    ) -> str:
        """
        Generate encouraging message for student.
        
        Shows progress, explains recommendation, motivates next step.
        """
        
        emoji_map = {
            'advance': '🚀',
            'retreat': '🌱',
            'reinforce': '💪',
            'remediate': '🔧'
        }
        
        emoji = emoji_map.get(recommendation.action, '📚')
        
        messages = {
            'advance': f"{emoji} Excellent! You're ready for a tougher challenge!",
            'retreat': f"{emoji} No worries! Let's build a stronger foundation first.",
            'reinforce': f"{emoji} Great progress! Keep practicing this level.",
            'remediate': f"{emoji} Let's clear up this concept with a focused question."
        }
        
        return (
            f"{messages.get(recommendation.action, '📚')}\n\n"
            f"{recommendation.reason}"
        )


class StudentAnalytics:
    """Generate insights and reports for teachers."""
    
    @staticmethod
    def get_class_misconception_summary(
        student_progresses: list[StudentProgress]
    ) -> dict:
        """Analyze misconceptions across entire class."""
        
        misconception_counts = {}
        
        for progress in student_progresses:
            for misconception in progress.get_problem_misconceptions():
                key = misconception.value
                misconception_counts[key] = misconception_counts.get(key, 0) + 1
        
        # Sort by frequency
        sorted_misconceptions = sorted(
            misconception_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "total_students": len(student_progresses),
            "misconceptions": [
                {
                    "type": misc_type,
                    "affected_students": count,
                    "percentage_of_class": (count / len(student_progresses) * 100)
                }
                for misc_type, count in sorted_misconceptions
            ],
            "recommendation": (
                "Focus remediation on most common misconceptions first"
                if sorted_misconceptions else "No major misconceptions detected"
            )
        }
    
    @staticmethod
    def get_at_risk_students(
        student_progresses: list[StudentProgress],
        threshold_percentage: float = 50.0
    ) -> list[dict]:
        """Identify students who might need additional support."""
        
        at_risk = []
        
        for progress in student_progresses:
            if progress.overall_percentage < threshold_percentage:
                at_risk.append({
                    "student_id": progress.student_id,
                    "overall_percentage": progress.overall_percentage,
                    "problem_areas": [
                        misc.misconception_type
                        for misc in progress.misconceptions.values()
                        if misc.encounter_count >= 2
                    ],
                    "recommendation": "Consider 1-on-1 support or additional practice"
                })
        
        return sorted(
            at_risk,
            key=lambda x: x['overall_percentage']
        )
