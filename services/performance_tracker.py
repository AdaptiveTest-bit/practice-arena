"""Performance Tracker - Calculate student mastery and learning metrics.

Analyzes student attempts to calculate:
- Mastery at each difficulty level (1-5)
- Mastery at each Bloom's cognitive level
- Misconception patterns
- Learning velocity and trends
- Readiness for advancement
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from models.student_progress import (
    StudentProgress,
    AttemptResult,
    DifficultyMastery,
    BloomMastery,
    MisconceptionEncounter
)
from models.distractor import MisconceptionType
from models.cognitive_levels import BloomLevel


class PerformanceTracker:
    """
    Tracks and calculates student performance metrics.
    
    Uses these calculations:
    
    1. **Mastery Score** = (Correct Attempts / Total Attempts) × 100
       - Requires minimum 3 attempts for reliability
       - Mastered = 80%+ correct
    
    2. **Learning Velocity** = Recent performance vs Historical performance
       - Shows if student improving or declining
       - Calculated over last 5-10 attempts
    
    3. **Misconception Frequency** = How many times student made each error
       - Triggers remediation at 2+ encounters
       - Tracked across all attempts
    
    4. **Cognitive Level Readiness** = Mastery at current level + no problem misconceptions
       - Must have 80%+ at current level
       - Must have solved recent problems with no new errors
    """
    
    @staticmethod
    def process_attempt(
        student_progress: StudentProgress,
        attempt: AttemptResult
    ) -> Tuple[StudentProgress, Dict]:
        """
        Process a new attempt and update all metrics.
        
        Returns: (updated StudentProgress, metrics_summary)
        """
        
        # Record the attempt
        student_progress.record_attempt(attempt)
        
        # Calculate additional metrics
        metrics = {
            "difficulty_mastery": PerformanceTracker._get_difficulty_mastery_metrics(
                student_progress
            ),
            "bloom_mastery": PerformanceTracker._get_bloom_mastery_metrics(
                student_progress
            ),
            "misconception_analysis": PerformanceTracker._get_misconception_analysis(
                student_progress
            ),
            "learning_velocity": PerformanceTracker._calculate_learning_velocity(
                student_progress, attempt
            ),
            "readiness_assessment": PerformanceTracker._assess_readiness(
                student_progress
            )
        }
        
        return student_progress, metrics
    
    @staticmethod
    def _get_difficulty_mastery_metrics(
        progress: StudentProgress
    ) -> Dict:
        """Calculate mastery metrics for each difficulty level."""
        
        metrics = {}
        
        for level, mastery in progress.difficulty_mastery.items():
            metrics[level] = {
                "percentage_correct": mastery.percentage_correct,
                "attempts": mastery.attempts,
                "correct": mastery.correct,
                "mastered": mastery.mastered,
                "status": PerformanceTracker._get_mastery_status(mastery),
                "last_attempted": mastery.last_attempted.isoformat() if mastery.last_attempted else None
            }
        
        return metrics
    
    @staticmethod
    def _get_bloom_mastery_metrics(
        progress: StudentProgress
    ) -> Dict:
        """Calculate mastery metrics for each Bloom's level."""
        
        metrics = {}
        
        for level_str, mastery in progress.bloom_mastery.items():
            metrics[level_str] = {
                "percentage_correct": mastery.percentage_correct,
                "attempts": mastery.attempts,
                "correct": mastery.correct,
                "mastered": mastery.mastered,
                "status": PerformanceTracker._get_mastery_status(mastery),
                "last_attempted": mastery.last_attempted.isoformat() if mastery.last_attempted else None
            }
        
        return metrics
    
    @staticmethod
    def _get_mastery_status(mastery) -> str:
        """Convert mastery data to human-readable status."""
        
        if mastery.attempts < 3:
            return "🟡 Building foundation"
        elif mastery.mastered:
            return "🟢 Mastered"
        elif mastery.percentage_correct >= 60:
            return "🟡 Developing"
        else:
            return "🔴 Needs help"
    
    @staticmethod
    def _get_misconception_analysis(
        progress: StudentProgress
    ) -> Dict:
        """Analyze misconception patterns."""
        
        # Sort by frequency
        sorted_misconceptions = sorted(
            progress.misconceptions.items(),
            key=lambda x: x[1].encounter_count,
            reverse=True
        )
        
        return {
            "total_unique_misconceptions": len(progress.misconceptions),
            "misconceptions_needing_remediation": len(
                [m for m in progress.misconceptions.values() if m.encounter_count >= 2]
            ),
            "details": [
                {
                    "type": misc_type,
                    "encounters": misc.encounter_count,
                    "needs_remediation": misc.encounter_count >= 2 and not misc.remediation_effective,
                    "remediation_provided": misc.remediation_provided,
                    "remediation_effective": misc.remediation_effective,
                    "first_encountered": misc.first_encountered.isoformat() if misc.first_encountered else None,
                    "last_encountered": misc.last_encountered.isoformat() if misc.last_encountered else None
                }
                for misc_type, misc in sorted_misconceptions
            ]
        }
    
    @staticmethod
    def _calculate_learning_velocity(
        progress: StudentProgress,
        latest_attempt: AttemptResult
    ) -> Dict:
        """
        Calculate learning velocity: is student improving?
        
        Compares recent performance to historical performance.
        """
        
        # For this basic version, compare first 3 to last 3 attempts
        # In production, would track attempt history separately
        
        total = progress.total_attempts
        if total < 6:
            return {
                "status": "insufficient_data",
                "message": f"Need at least 6 attempts to calculate velocity (current: {total})"
            }
        
        # Estimate: if improving, recent attempts should have higher success rate
        current_percentage = progress.overall_percentage
        historical_average = progress.total_correct / progress.total_attempts
        
        # Calculate trend (positive = improving)
        trend = "improving" if latest_attempt.is_correct else "variable"
        
        return {
            "current_percentage": current_percentage,
            "total_attempts": total,
            "trend": trend,
            "message": (
                "Student is improving! Keep up the momentum!" if trend == "improving"
                else "Performance is fluctuating. Consistent practice needed."
            )
        }
    
    @staticmethod
    def _assess_readiness(
        progress: StudentProgress
    ) -> Dict:
        """Assess readiness for advancement."""
        
        current_diff = progress.current_difficulty
        current_bloom = progress.current_bloom_level
        
        diff_mastery = progress.difficulty_mastery[current_diff]
        bloom_mastery = progress.bloom_mastery.get(current_bloom.value)
        
        # Check readiness criteria
        difficulty_ready = diff_mastery.mastered and diff_mastery.percentage_correct >= 85
        
        bloom_ready = (
            bloom_mastery and bloom_mastery.mastered 
            and bloom_mastery.percentage_correct >= 85
        ) if bloom_mastery else False
        
        misconception_free = len(progress.get_problem_misconceptions()) == 0
        
        return {
            "ready_for_difficulty_advancement": difficulty_ready,
            "ready_for_bloom_advancement": bloom_ready,
            "misconceptions_clear": misconception_free,
            "overall_readiness": difficulty_ready or bloom_ready,
            "blockers": PerformanceTracker._identify_blockers(progress),
            "next_steps": PerformanceTracker._recommend_next_steps(progress)
        }
    
    @staticmethod
    def _identify_blockers(progress: StudentProgress) -> List[str]:
        """Identify what's preventing advancement."""
        
        blockers = []
        
        # Check difficulty blocker
        diff_mastery = progress.difficulty_mastery[progress.current_difficulty]
        if diff_mastery.percentage_correct < 80:
            blockers.append(
                f"Difficulty {progress.current_difficulty} not yet mastered "
                f"({diff_mastery.percentage_correct:.0f}% correct)"
            )
        
        # Check misconceptions
        problem_misconceptions = progress.get_problem_misconceptions()
        if problem_misconceptions:
            blockers.append(
                f"Recurring misconceptions: {', '.join([m.value for m in problem_misconceptions[:3]])}"
            )
        
        return blockers if blockers else ["None identified"]
    
    @staticmethod
    def _recommend_next_steps(progress: StudentProgress) -> List[str]:
        """Recommend actions to help student progress."""
        
        recommendations = []
        
        # Current status
        if progress.overall_percentage < 50:
            recommendations.append(
                "Focus on foundational questions. Consider 1-on-1 support."
            )
        elif progress.overall_percentage < 70:
            recommendations.append("Continue practice. Most students improve with consistent effort.")
        else:
            recommendations.append("You're on track! Keep practicing.")
        
        # Misconceptions
        problem_misconceptions = progress.get_problem_misconceptions()
        if problem_misconceptions:
            recommendations.append(
                f"Remediation needed for: {problem_misconceptions[0].value}"
            )
        
        # Advancement
        if progress.should_advance_difficulty():
            recommendations.append("📚 Ready for more challenging problems!")
        elif progress.should_advance_bloom_level():
            recommendations.append("🧠 Ready for higher-order thinking questions!")
        
        return recommendations


class ClassroomAnalytics:
    """Analyze performance across entire classroom."""
    
    @staticmethod
    def get_class_statistics(
        student_progresses: List[StudentProgress]
    ) -> Dict:
        """Generate class-wide statistics for teacher dashboard."""
        
        if not student_progresses:
            return {"error": "No student data"}
        
        overall_percentages = [s.overall_percentage for s in student_progresses]
        
        return {
            "class_size": len(student_progresses),
            "average_percentage": sum(overall_percentages) / len(overall_percentages),
            "min_percentage": min(overall_percentages),
            "max_percentage": max(overall_percentages),
            "total_attempts": sum(s.total_attempts for s in student_progresses),
            "students_above_80": sum(1 for p in student_progresses if p.overall_percentage >= 80),
            "students_between_60_80": sum(1 for p in student_progresses if 60 <= p.overall_percentage < 80),
            "students_below_60": sum(1 for p in student_progresses if p.overall_percentage < 60)
        }
    
    @staticmethod
    def get_misconception_hot_spots(
        student_progresses: List[StudentProgress]
    ) -> Dict:
        """Identify misconceptions affecting multiple students."""
        
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
            "hot_spot_misconceptions": [
                {
                    "type": misc,
                    "affected_students": count,
                    "percentage_of_class": (count / len(student_progresses) * 100)
                }
                for misc, count in sorted_misconceptions[:5]  # Top 5
            ],
            "recommendation": (
                "These misconceptions affect multiple students. "
                "Consider whole-class mini-lesson on these topics."
                if sorted_misconceptions else "No widespread misconception patterns detected."
            )
        }
    
    @staticmethod
    def get_difficulty_distribution(
        student_progresses: List[StudentProgress]
    ) -> Dict:
        """Show where students are in difficulty levels."""
        
        difficulty_counts = {i: 0 for i in range(1, 6)}
        
        for progress in student_progresses:
            difficulty_counts[progress.current_difficulty] += 1
        
        return {
            "distribution": difficulty_counts,
            "summary": f"Most students working at difficulty {max(difficulty_counts, key=difficulty_counts.get)}"
        }
    
    @staticmethod
    def get_bloom_distribution(
        student_progresses: List[StudentProgress]
    ) -> Dict:
        """Show where students are in cognitive levels."""
        
        bloom_counts = {level: 0 for level in BloomLevel}
        
        for progress in student_progresses:
            bloom_counts[progress.current_bloom_level] += 1
        
        return {
            "distribution": {level.value: count for level, count in bloom_counts.items()},
            "summary": f"Most students working at {max(bloom_counts, key=bloom_counts.get).value} level"
        }


class LearningPathOptimization:
    """Suggestions for optimizing student learning paths."""
    
    @staticmethod
    def estimate_mastery_time(
        student_progress: StudentProgress,
        target_percentage: float = 80.0
    ) -> Dict:
        """Estimate time to reach mastery."""
        
        current_percentage = student_progress.overall_percentage
        total_attempts = student_progress.total_attempts
        
        if current_percentage >= target_percentage:
            return {"status": "already_mastered", "attempts_to_mastery": 0}
        
        if total_attempts < 3:
            return {
                "status": "insufficient_data",
                "message": "Need more attempts to estimate trajectory"
            }
        
        # Very rough estimate: linear interpolation
        # In production, would use more sophisticated learning curve models
        attempts_per_point = total_attempts / current_percentage if current_percentage > 0 else 0
        points_needed = target_percentage - current_percentage
        estimated_attempts = int(attempts_per_point * points_needed)
        
        return {
            "current_percentage": current_percentage,
            "target_percentage": target_percentage,
            "estimated_additional_attempts": max(1, estimated_attempts),
            "estimated_additional_minutes": max(1, estimated_attempts * 2),  # ~2 min per attempt
            "confidence": "low" if total_attempts < 10 else "medium"
        }
    
    @staticmethod
    def get_personalized_strategy(
        student_progress: StudentProgress
    ) -> Dict:
        """Get personalized learning strategy for student."""
        
        overall = student_progress.overall_percentage
        problem_misconceptions = student_progress.get_problem_misconceptions()
        
        if overall < 30:
            strategy = "Foundation Building"
            description = (
                "Focus on REMEMBER and UNDERSTAND levels with very simple problems. "
                "Build confidence with easy wins before advancing."
            )
        elif overall < 60:
            strategy = "Skill Development"
            description = (
                "Practice applying concepts. Work through mistakes carefully. "
                "Misconceptions should be addressed through targeted remediation."
            )
        elif overall < 80:
            strategy = "Consolidation"
            description = (
                "Strengthen weaker areas. Push toward mastery at current difficulty. "
                "Prepare for advancement to next level."
            )
        else:
            strategy = "Advancement"
            description = (
                "Ready for new challenges! Move to harder problems and higher-order thinking. "
                "Mentor other students to deepen understanding."
            )
        
        return {
            "strategy": strategy,
            "description": description,
            "focus_areas": (
                [m.value for m in problem_misconceptions[:3]] if problem_misconceptions
                else "General practice"
            ),
            "recommended_question_types": LearningPathOptimization._get_recommended_questions(
                student_progress
            )
        }
    
    @staticmethod
    def _get_recommended_questions(progress: StudentProgress) -> List[str]:
        """Recommend types of questions for this student."""
        
        recommendations = []
        
        if progress.overall_percentage < 50:
            recommendations.append("Very simple (difficulty 1-2)")
            recommendations.append("Focus on REMEMBER level")
        elif progress.overall_percentage < 70:
            recommendations.append("Simple-moderate (difficulty 2-3)")
            recommendations.append("Mix of REMEMBER and UNDERSTAND")
        elif progress.overall_percentage < 85:
            recommendations.append("Moderate (difficulty 3-4)")
            recommendations.append("UNDERSTAND and APPLY levels")
        else:
            recommendations.append("Challenging (difficulty 4-5)")
            recommendations.append("APPLY and ANALYZE levels")
        
        return recommendations
