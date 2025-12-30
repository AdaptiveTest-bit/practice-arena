"""
🔗 INTEGRATED SESSION ADAPTER
=============================

Bridges hybrid neuro-symbolic questions with existing session tracking.

Ensures that when a rich question is answered:
1. StudentProgress is updated with correct/wrong tracking
2. Bloom level enforcement still works
3. Misconception detection triggers
4. Analytics are aggregated
5. Session management continues seamlessly
"""

from typing import Dict, Any, Optional
from datetime import datetime
from models.question import Question, ChapterEnum
from models.student_progress import StudentProgress, AttemptResult
from models.cognitive_levels import BloomLevel
from models.distractor import MisconceptionType
from services.orm_student_repository import ORMStudentRepository
from services.adaptive_learning_service import AdaptiveLearningService
from services.misconception_analyzer import MisconceptionAnalyzer
from services.performance_tracker import PerformanceTracker
from services.session_manager import SessionManager
import uuid


class IntegratedSessionAdapter:
    """
    🔗 Adapter pattern: Makes rich questions work seamlessly with session tracking
    
    Problem it solves:
    - Hybrid system generates questions without session context
    - Session system expects AttemptResult with specific fields
    - This adapter bridges the gap transparently
    
    Solution:
    - Record rich question attempt as normal AttemptResult
    - Extract misconception info from distractor_info
    - Update StudentProgress with Bloom's level
    - Trigger misconception detection
    - Maintain session timeline
    """
    
    def __init__(self, student_id: str, session_id: str):
        self.student_id = student_id
        self.session_id = session_id
        self.repo = ORMStudentRepository()
        self.adaptive_service = AdaptiveLearningService(self.repo)
        self.misconception_analyzer = MisconceptionAnalyzer()
        self.performance_tracker = PerformanceTracker()
        self.session_manager = SessionManager(student_id=student_id)
    
    def record_rich_question_attempt(
        self,
        question: Question,
        selected_option_index: int,
        time_spent_seconds: int,
        attempt_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record a rich question attempt in the session tracking system.
        
        Args:
            question: The rich Question object (with all metadata)
            selected_option_index: Which option student selected (0-3)
            time_spent_seconds: Time spent on this question
            attempt_id: Optional ID; generated if not provided
        
        Returns:
            Response dict with:
            - success: bool
            - is_correct: bool
            - feedback: str (misconception feedback if wrong)
            - bloom_level_feedback: str (progression info)
            - next_action: str (what to do next)
            - student_progress: StudentProgress object
        """
        
        if attempt_id is None:
            attempt_id = str(uuid.uuid4())[:8]
        
        # Determine if answer is correct
        is_correct = selected_option_index == question.correct_option_index
        
        # Extract misconception type from distractor info
        misconception_type = None
        if not is_correct and question.distractor_info:
            # Find which misconception corresponds to selected option
            selected_option = question.options[selected_option_index]
            for distractor in question.distractor_info:
                if distractor.value == selected_option and distractor.misconception_type:
                    misconception_type = distractor.misconception_type
                    break
        
        # Extract Bloom's level from question metadata
        bloom_level = BloomLevel.REMEMBER  # Default fallback
        if question.bloom_info:
            bloom_level_str = question.bloom_info.level
            # Map string to BloomLevel enum
            level_map = {
                "remember": BloomLevel.REMEMBER,
                "understand": BloomLevel.UNDERSTAND,
                "apply": BloomLevel.APPLY,
                "analyze": BloomLevel.ANALYZE,
                "evaluate": BloomLevel.EVALUATE,
                "create": BloomLevel.CREATE,
            }
            bloom_level = level_map.get(bloom_level_str.lower(), BloomLevel.REMEMBER)
        
        # Determine difficulty from trap_info
        difficulty_level = 1
        if question.trap_info:
            difficulty_level = question.trap_info.difficulty
        
        # Create AttemptResult object (existing system's record format)
        attempt_result = AttemptResult(
            attempt_id=attempt_id,
            student_id=self.student_id,
            question_id=question.get_fingerprint(),  # Use question hash as ID
            chapter=question.chapter.value,
            response_selected=selected_option_index,
            is_correct=is_correct,
            time_spent_seconds=time_spent_seconds,
            difficulty_level=difficulty_level,
            bloom_level=bloom_level.value,
            misconceptions_targeted=[misconception_type.value] if misconception_type else [],
            misconception_revealed=misconception_type.value if (not is_correct and misconception_type) else None,
            created_at=datetime.utcnow()
        )
        
        # Record attempt in session manager
        self.session_manager.record_attempt(attempt_result)
        
        # Record in database (persistent storage)
        self.repo.record_attempt(
            student_id=self.student_id,
            chapter=question.chapter.value,
            topic=question.topic,
            question_id=attempt_result.question_id,
            response_selected=selected_option_index,
            is_correct=is_correct,
            time_spent_seconds=time_spent_seconds,
            difficulty_level=difficulty_level,
            bloom_level=bloom_level.value,
            misconceptions_targeted=[misconception_type.value] if misconception_type else [],
            misconception_revealed=misconception_type.value if (not is_correct and misconception_type) else None,
        )
        
        # Get updated student progress
        student_progress = self.repo.get_student(self.student_id)
        
        # ==================== ADAPTIVE ENGINE INTEGRATION ====================
        
        # Generate misconception feedback (if wrong)
        misconception_feedback = ""
        if not is_correct and misconception_type:
            misconception_feedback = self._generate_misconception_feedback(
                misconception_type,
                question,
                selected_option_index
            )
        
        # Check Bloom's level enforcement (80% mastery rule)
        bloom_feedback = self._check_bloom_progression(student_progress, bloom_level)
        
        # Determine next action based on progress
        next_action = self._determine_next_action(
            student_progress,
            bloom_level,
            difficulty_level,
            is_correct
        )
        
        # Return response
        return {
            "success": True,
            "attempt_id": attempt_id,
            "is_correct": is_correct,
            "correct_option_index": question.correct_option_index,
            "correct_answer": question.answer,
            "solution_steps": question.solution_steps,
            "misconception_feedback": misconception_feedback,
            "bloom_level_feedback": bloom_feedback,
            "next_action": next_action,
            "student_progress": student_progress,
            "session_status": self.session_manager.get_session_status(self.session_id)
        }
    
    def _generate_misconception_feedback(
        self,
        misconception_type: MisconceptionType,
        question: Question,
        selected_option_index: int
    ) -> str:
        """Generate pedagogical feedback for detected misconception."""
        
        feedback_map = {
            MisconceptionType.OPPOSITE_CONFUSION: 
                "✗ You inverted the answer. Remember to carefully check if your result is correct before finalizing.",
            
            MisconceptionType.UNIVERSAL_VS_SPECIFIC:
                "✗ This rule works for this case, but check if it applies universally to all similar problems.",
            
            MisconceptionType.OPERATION_DIRECTION:
                "✗ Check whether you should multiply or divide here. Think about what the problem is asking.",
            
            MisconceptionType.INCOMPLETE_REASONING:
                "✗ You're on the right track, but it looks like you missed a step. Are you sure your answer is complete?",
            
            MisconceptionType.ARITHMETIC_ERROR:
                "✗ Your approach is correct, but double-check your arithmetic/calculation.",
            
            MisconceptionType.FORMULA_MISAPPLICATION:
                "✗ You used the wrong formula. Make sure you understand which formula applies to this type of problem.",
            
            MisconceptionType.FORMULA_CONFUSION:
                "✗ This resembles another formula, but it's different. Review the difference between these formulas.",
            
            MisconceptionType.CONSTRAINT_VIOLATION:
                "✗ You ignored a constraint or condition in the problem. Re-read carefully.",
            
            MisconceptionType.SIMILAR_CONCEPT_ERROR:
                "✗ This concept is similar to another one you know, but they're different. Make sure you understand the distinction.",
            
            MisconceptionType.PATTERN_MISIDENTIFICATION:
                "✗ Check if you identified the pattern correctly. Look more carefully at the sequence.",
        }
        
        # Get custom description from trap_info if available
        if question.trap_info:
            return f"✗ {question.trap_info.description}"
        
        # Use generic feedback
        return feedback_map.get(misconception_type, "✗ Your answer is not correct. Review your working.")
    
    def _check_bloom_progression(
        self,
        student_progress: StudentProgress,
        current_bloom_level: BloomLevel
    ) -> str:
        """Check if student can progress to next Bloom's level (80% mastery rule)."""
        
        bloom_str = current_bloom_level.value
        
        # Get mastery for current level
        if bloom_str in student_progress.bloom_mastery:
            mastery = student_progress.bloom_mastery[bloom_str]
            percentage = mastery.percentage_correct
            
            # Check if they've reached 80% (mastered)
            if percentage >= 80 and mastery.attempts >= 3:
                return f"✓ Great progress! You've mastered {current_bloom_level.value.title()} ({percentage:.1f}%). You can now advance to {self._next_bloom_level(current_bloom_level).title()}."
            elif percentage >= 70:
                return f"Good progress on {current_bloom_level.value.title()} ({percentage:.1f}%). Keep practicing to reach 80% mastery."
            else:
                return f"You're working on {current_bloom_level.value.title()} ({percentage:.1f}%). Keep attempting more questions to improve."
        
        return ""
    
    def _next_bloom_level(self, current: BloomLevel) -> str:
        """Get next Bloom's level in sequence."""
        sequence = [
            "remember", "understand", "apply", "analyze", "evaluate", "create"
        ]
        try:
            idx = sequence.index(current.value)
            if idx < len(sequence) - 1:
                return sequence[idx + 1]
        except (ValueError, IndexError):
            pass
        return "create"
    
    def _determine_next_action(
        self,
        student_progress: StudentProgress,
        bloom_level: BloomLevel,
        difficulty_level: int,
        is_correct: bool
    ) -> str:
        """Determine what the student should do next (adaptive routing)."""
        
        # If wrong, focus on same level
        if not is_correct:
            return f"Try another {difficulty_level}/5 difficulty question at {bloom_level.value} level to strengthen understanding"
        
        # If correct, check advancement
        bloom_str = bloom_level.value
        if bloom_str in student_progress.bloom_mastery:
            mastery = student_progress.bloom_mastery[bloom_str]
            
            # If they've reached mastery, advance
            if mastery.percentage_correct >= 80 and mastery.attempts >= 3:
                next_level = self._next_bloom_level(bloom_level)
                return f"Excellent! Try questions at the next level: {next_level}"
            
            # Otherwise, stay at level but can increase difficulty
            if difficulty_level < 5:
                return f"Good! Try a level {difficulty_level + 1}/5 difficulty question at {bloom_level.value} level"
            else:
                return f"Perfect! Get another question at {bloom_level.value} level"
        
        return "Try another question at this level"
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary combining rich questions with tracking."""
        
        session_status = self.session_manager.get_session_status(self.session_id)
        student_progress = self.repo.get_student(self.student_id)
        
        return {
            "session_id": self.session_id,
            "student_id": self.student_id,
            "session_status": session_status,
            "student_progress": student_progress,
            "performance_analytics": self.performance_tracker.get_student_mastery_metrics(
                student_progress
            ),
            "misconception_analysis": self.misconception_analyzer.analyze_student_misconceptions(
                student_progress
            )
        }
