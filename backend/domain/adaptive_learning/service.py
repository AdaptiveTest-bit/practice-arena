"""Adaptive Learning Service - Orchestrates the complete learning workflow.

This service coordinates:
1. Question selection from adaptive engine
2. Attempt recording and storage
3. Misconception detection and analysis
4. Remediation recommendations
"""

from typing import Optional, Dict, Tuple, Union
from api.models.quiz import Question
from api.models.student_progress import StudentProgress, AttemptResult
from api.models.cognitive_levels import BloomLevel
from api.models.distractor import MisconceptionType
from engines.adaptive_engine import AdaptiveEngine
# Support both in-memory and ORM repositories
try:
    from domain.session_management.student.repository import ORMStudentRepository, get_repository
except ImportError:
    from domain.session_management.student.repository import StudentRepository as ORMStudentRepository
    from domain.session_management.student.repository import get_repository

from domain.adaptive_learning.misconceptions.detector import (
    MisconceptionDetector,
    RemediationRecommender,
    PerformanceAnalyzer,
    MisconceptionReport
)
from datetime import datetime
import uuid


class AdaptiveLearningService:
    """Main service orchestrating adaptive learning workflow."""
    
    def __init__(
        self,
        repository: Optional[Union[ORMStudentRepository, 'StudentRepository']] = None,
        adaptive_engine: Optional[AdaptiveEngine] = None
    ):
        """
        Initialize the service.
        
        Args:
            repository: StudentRepository instance (default: get_repository())
            adaptive_engine: AdaptiveEngine instance (default: new instance)
        """
        self.repository = repository or get_repository()
        self.adaptive_engine = adaptive_engine or AdaptiveEngine()
        self.misconception_detector = MisconceptionDetector()
        self.remediation_recommender = RemediationRecommender()
        self.performance_analyzer = PerformanceAnalyzer()
        
        # Cache for in-flight questions
        self._question_cache = {}
    
    def register_student(self, name: str, chapter: str) -> str:
        """
        Register a new student for the learning session.
        
        Args:
            name: Student's name
            chapter: Chapter to start with
            
        Returns:
            student_id for use in subsequent requests
        """
        student_id = self.repository.create_student(name, chapter)
        return student_id
    
    def get_next_question(
        self,
        student_id: str,
        question_generator_func
    ) -> Dict:
        """
        Get next adaptive question for student.
        
        Args:
            student_id: Student's ID
            question_generator_func: Callable that generates Question objects
                                    Signature: () -> Question
            
        Returns:
            Dict with question, question_id, and metadata
        """
        # Get student's current progress
        student = self.repository.get_student(student_id)
        if not student:
            return {
                "success": False,
                "error": f"Student {student_id} not found"
            }
        
        # Get adaptive recommendation
        recommendation = self.adaptive_engine.get_next_recommendation(student)
        
        # Generate question matching recommendation
        question = question_generator_func()
        
        # Store in cache for later reference
        question_id = str(uuid.uuid4())
        self._question_cache[question_id] = {
            "question": question,
            "student_id": student_id,
            "timestamp": datetime.utcnow(),
            "recommendation": recommendation
        }
        
        return {
            "success": True,
            "question_id": question_id,
            "student_id": student_id,
            "question": {
                "topic": question.topic,
                "text": question.question_text,
                "options": question.options,
                "difficulty": question.difficulty_level,
                "bloom_level": question.bloom_level.value if question.bloom_level else None
            },
            "recommendation": {
                "type": recommendation.recommendation_type,
                "reason": recommendation.reasoning,
                "target_difficulty": recommendation.recommended_difficulty,
                "target_bloom_level": recommendation.recommended_bloom_level.value
            }
        }
    
    def process_student_answer(
        self,
        student_id: str,
        question_id: str,
        selected_option_index: int,
        time_spent_seconds: int = 30
    ) -> Dict:
        """
        Process student's answer and detect misconceptions.
        
        Args:
            student_id: Student's ID
            question_id: Question ID (from get_next_question)
            selected_option_index: Which option (0-3) student selected
            time_spent_seconds: Time spent on question
            
        Returns:
            Dict with correctness, misconception detection, and recommendations
        """
        # Validate question exists
        if question_id not in self._question_cache:
            return {
                "success": False,
                "error": f"Question {question_id} not found or expired"
            }
        
        cached = self._question_cache[question_id]
        question = cached["question"]
        recommendation = cached["recommendation"]
        
        # Check if answer is correct
        is_correct = selected_option_index == question.correct_option_index
        
        # Detect misconception if wrong
        misconception = None
        misconception_explanation = None
        if not is_correct:
            misconception = self.misconception_detector.detect_misconception(
                question,
                selected_option_index
            )
            if misconception:
                misconception_explanation = self.misconception_detector.get_misconception_explanation(
                    question,
                    misconception
                )
        
        # Record attempt in repository
        attempt = AttemptResult(
            student_id=student_id,
            question_id=question_id,
            response_selected=selected_option_index,
            is_correct=is_correct,
            time_spent_seconds=time_spent_seconds,
            difficulty_level=question.difficulty_level,
            bloom_level=question.bloom_level or BloomLevel.REMEMBER,
            misconception_revealed=misconception,
            timestamp=datetime.utcnow()
        )
        
        # Save attempt
        self.repository.record_attempt(attempt)
        
        # Get updated student progress
        student = self.repository.get_student(student_id)
        
        # Prepare feedback
        feedback = {
            "is_correct": is_correct,
            "correct_index": question.correct_option_index,
            "solution_steps": question.solution_steps,
            "answer": question.answer
        }
        
        # Add misconception feedback if detected
        if misconception:
            feedback["misconception"] = misconception_explanation
            feedback["remediation"] = self.remediation_recommender.get_remediation_sequence(
                student,
                misconception,
                num_questions=3
            )
        
        # Clean up cache
        del self._question_cache[question_id]
        
        return {
            "success": True,
            "feedback": feedback,
            "student_progress": {
                "accuracy": student.overall_percentage,
                "total_attempts": student.total_attempts,
                "mastered_difficulties": [
                    d for d, m in student.difficulty_mastery.items()
                    if m.mastered
                ],
                "problem_misconceptions": [
                    m.value for m in student.get_problem_misconceptions()
                ]
            }
        }
    
    def get_student_dashboard(self, student_id: str) -> Dict:
        """
        Get comprehensive student dashboard data.
        
        Args:
            student_id: Student's ID
            
        Returns:
            Dict with performance, misconceptions, and recommendations
        """
        student = self.repository.get_student(student_id)
        if not student:
            return {
                "success": False,
                "error": f"Student {student_id} not found"
            }
        
        # Get detailed report
        report = MisconceptionReport.generate_student_report(student)
        learning_curve = self.performance_analyzer.analyze_learning_curve(student)
        
        return {
            "success": True,
            "student_id": student_id,
            "student_name": student.student_name,
            "report": report,
            "learning_curve": learning_curve,
            "action_items": self._generate_action_items(student)
        }
    
    def get_class_analytics(self, student_ids: list) -> Dict:
        """
        Get class-wide analytics and misconception patterns.
        
        Args:
            student_ids: List of student IDs to analyze
            
        Returns:
            Dict with class-level statistics and recommendations
        """
        students = [
            self.repository.get_student(sid)
            for sid in student_ids
            if self.repository.get_student(sid)
        ]
        
        if not students:
            return {
                "success": False,
                "error": "No valid students provided"
            }
        
        # Get class report
        class_report = MisconceptionReport.generate_class_report(students)
        class_stats = self.repository.get_class_statistics(student_ids)
        
        return {
            "success": True,
            "class_size": len(students),
            "analytics": class_report,
            "statistics": class_stats,
            "interventions_needed": self._identify_interventions(students)
        }
    
    def _generate_action_items(self, student: StudentProgress) -> list:
        """Generate personalized action items for student."""
        actions = []
        
        # Check misconceptions
        misconceptions = student.get_problem_misconceptions()
        if misconceptions:
            actions.append({
                "type": "remediation",
                "priority": "high",
                "message": f"Address {len(misconceptions)} misconceptions before advancing"
            })
        
        # Check difficulty progression
        if student.should_advance_difficulty():
            actions.append({
                "type": "advancement",
                "priority": "medium",
                "message": "Ready to advance to higher difficulty level"
            })
        elif student.should_retreat_difficulty():
            actions.append({
                "type": "review",
                "priority": "high",
                "message": "Review current difficulty before advancing"
            })
        
        # Check overall progress
        if student.overall_percentage < 50:
            actions.append({
                "type": "support",
                "priority": "high",
                "message": "Provide additional support and practice"
            })
        
        return actions
    
    def _identify_interventions(self, students: list) -> list:
        """Identify students needing intervention."""
        interventions = []
        
        for student in students:
            if student.overall_percentage < 50:
                interventions.append({
                    "student_id": student.student_id,
                    "student_name": student.student_name,
                    "issue": "Low overall accuracy",
                    "accuracy": student.overall_percentage,
                    "recommendation": "1-on-1 support needed"
                })
            elif len(student.get_problem_misconceptions()) > 3:
                interventions.append({
                    "student_id": student.student_id,
                    "student_name": student.student_name,
                    "issue": "Multiple misconceptions",
                    "count": len(student.get_problem_misconceptions()),
                    "recommendation": "Targeted remediation sequence"
                })
        
        return interventions
    
    def cleanup_expired_questions(self, max_age_seconds: int = 3600) -> int:
        """
        Clean up expired questions from cache.
        
        Args:
            max_age_seconds: Questions older than this are removed
            
        Returns:
            Number of questions cleaned up
        """
        now = datetime.utcnow()
        expired_ids = []
        
        for question_id, cached in self._question_cache.items():
            age = (now - cached["timestamp"]).total_seconds()
            if age > max_age_seconds:
                expired_ids.append(question_id)
        
        for question_id in expired_ids:
            del self._question_cache[question_id]
        
        return len(expired_ids)
    
    def get_service_status(self) -> Dict:
        """Get service health status."""
        return {
            "service": "AdaptiveLearningService",
            "status": "operational",
            "components": {
                "repository": "ok" if self.repository else "error",
                "adaptive_engine": "ok" if self.adaptive_engine else "error",
                "misconception_detector": "ok",
                "remediation_recommender": "ok",
                "performance_analyzer": "ok"
            },
            "cached_questions": len(self._question_cache),
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instance for easy access
_adaptive_learning_service: Optional[AdaptiveLearningService] = None


def get_adaptive_learning_service(
    repository: Optional[ORMStudentRepository] = None,
    adaptive_engine: Optional[AdaptiveEngine] = None
) -> "AdaptiveLearningService":
    """Get or create global AdaptiveLearningService instance."""
    global _adaptive_learning_service
    if _adaptive_learning_service is None:
        _adaptive_learning_service = AdaptiveLearningService(
            repository=repository,
            adaptive_engine=adaptive_engine
        )
    return _adaptive_learning_service


def set_adaptive_learning_service(service: AdaptiveLearningService) -> None:
    """Set global AdaptiveLearningService instance (for testing)."""
    global _adaptive_learning_service
    _adaptive_learning_service = service
