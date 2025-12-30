"""Session Adapter Service - Bridges Frontend Session Model to Backend Question Generation.

This service acts as the glue layer between:
- Frontend: Expects session-based quiz management
- Backend: Has question generation, student tracking, adaptive learning

The adapter reuses existing backend services and exposes them via session-based endpoints.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json

from models.question import ChapterEnum
from factory import QuestionGeneratorFactory
from services.adaptive_learning_service import AdaptiveLearningService
from services.orm_student_repository import get_repository, ORMStudentRepository
from services.misconception_analyzer import MisconceptionDetector


class SessionAdapter:
    """Bridges frontend session-based API to backend question generation and tracking."""
    
    def __init__(self):
        """Initialize with existing backend services."""
        self.repository: ORMStudentRepository = get_repository()
        self.adaptive_service: AdaptiveLearningService = AdaptiveLearningService()
        self.misconception_detector: MisconceptionDetector = MisconceptionDetector()
        
        # In-memory session store (can be moved to database)
        # Key: session_id, Value: session_data
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    # ============================================================================
    # SESSION MANAGEMENT
    # ============================================================================
    
    def start_session(
        self,
        student_id: str,
        grade_level: int,
        mode: str = "practice",
        chapter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a new quiz session for a student.
        
        Args:
            student_id: Student UUID
            grade_level: Grade level (3-10)
            mode: "practice" or "assessment"
            chapter: Optional chapter to focus on (e.g., "large_numbers", "dice_logic", "nets")
            
        Returns:
            SessionStartResponse {
                sessionId: str,
                mode: str,
                classLevel: int,
                uiConfig: UIConfiguration,
                student: StudentProfile,
                chapters: List[Chapter]
            }
        """
        # Create session ID
        session_id = str(uuid.uuid4())
        
        # ⚠️ CRITICAL FIX: Validate and use the chapter parameter
        # If chapter is provided, validate it's a valid ChapterEnum
        selected_chapter = "large_numbers"  # Default chapter
        if chapter:
            try:
                # Try to create ChapterEnum from the string
                selected_chapter = ChapterEnum(chapter).value
            except ValueError:
                # If invalid chapter, log and use default
                print(f"Warning: Invalid chapter '{chapter}', using default 'large_numbers'")
                selected_chapter = "large_numbers"
        
        # Store session data
        self._sessions[session_id] = {
            "student_id": student_id,
            "grade_level": grade_level,
            "mode": mode,
            "chapter": selected_chapter,  # Use validated chapter
            "questions_asked": [],
            "answers_submitted": [],
            "start_time": datetime.utcnow().isoformat(),
            "current_streak": 0,
            "correct_count": 0,
            "attempted_count": 0,
        }
        
        return {
            "sessionId": session_id,
            "mode": mode,
            "classLevel": grade_level,
            "uiConfig": self._get_ui_config(grade_level, mode),
            "student": {
                "studentId": student_id,
                "name": f"Student {student_id[:8]}",
                "gradeLevel": grade_level,
                "chapter": selected_chapter,
                "masteryScore": 0.0,
                "totalQuestionsAttempted": 0,
            },
            "chapters": self._get_available_chapters(),
        }
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """
        Get current session state (for resuming).
        
        Args:
            session_id: Session ID
            
        Returns:
            SessionStartResponse with current progress
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self._sessions[session_id]
        student = self.repository.get_student(session["student_id"])
        
        return {
            "sessionId": session_id,
            "mode": session["mode"],
            "classLevel": session["grade_level"],
            "uiConfig": self._get_ui_config(session["grade_level"], session["mode"]),
            "student": self._format_student_profile(student),
            "chapters": self._get_available_chapters(),
        }
    
    # ============================================================================
    # QUESTION MANAGEMENT
    # ============================================================================
    
    def get_next_question(self, session_id: str) -> Dict[str, Any]:
        """
        Get next question in the quiz sequence.
        
        Args:
            session_id: Session ID
            
        Returns:
            NextQuestionResponse {
                questionId: str,
                topic: str,
                difficulty: int,
                question: str,
                options: List[AnswerOption],
                optionLayout: str,
                estimatedTime: int,
                misconceptionTag?: str,
                logicalTrapPresent: bool
            }
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self._sessions[session_id]
        chapter = session["chapter"]
        grade_level = session["grade_level"]
        
        # Generate question using factory
        try:
            strategy = QuestionGeneratorFactory.create(chapter)
            question = strategy.generate()  # Use generate() method, not generate_question()
            question_id = str(uuid.uuid4())
            
            # 🔧 SCALE DIFFICULTY BASED ON GRADE LEVEL
            # Grade 3-4: difficulty 1-2 (easy)
            # Grade 5-6: difficulty 2-3 (medium)
            # Grade 7-8: difficulty 3-4 (hard)
            # Grade 9-10: difficulty 4-5 (very hard)
            base_difficulty = max(1, (grade_level - 2) // 2)  # Maps: 3->1, 4->1, 5->2, 6->2, etc.
            # Add some variance based on performance
            attempted = session.get("attempted_count", 0)
            correct = session.get("correct_count", 0)
            accuracy = (correct / attempted * 100) if attempted > 0 else 50
            
            # If student is doing well (>70% accuracy), increase difficulty
            if accuracy > 70 and attempted > 3:
                difficulty = min(5, base_difficulty + 1)
            # If student is struggling (<30% accuracy), decrease difficulty
            elif accuracy < 30 and attempted > 3:
                difficulty = max(1, base_difficulty - 1)
            else:
                difficulty = base_difficulty
            
            # Override with question's own difficulty if it has one
            if hasattr(question, 'difficulty') and question.difficulty:
                # Blend: 60% from student progression, 40% from question difficulty
                difficulty = int(difficulty * 0.6 + question.difficulty * 0.4)
            
            # ⚠️ CRITICAL: Store the actual question object so we can retrieve it later
            # This ensures that when the user submits an answer, we check against the SAME question
            if "question_cache" not in session:
                session["question_cache"] = {}
            session["question_cache"][question_id] = question
            
            # Track this question in session
            session["questions_asked"].append({
                "question_id": question_id,
                "question_text": question.question_text,
                "chapter": chapter,
                "correct_option_index": question.correct_option_index,  # Store correct index
            })
            
            response_dict = {
                "questionId": question_id,
                "topic": question.topic if hasattr(question, 'topic') else chapter,
                "difficulty": difficulty,
                "question": question.question_text,
                "options": self._format_options(question.options),
                "optionLayout": "grid",
                "estimatedTime": 60,  # seconds
                "misconceptionTag": question.misconception_category if hasattr(question, 'misconception_category') else None,
                "logicalTrapPresent": bool(question.logical_trap if hasattr(question, 'logical_trap') else False),
                # 🆕 Rich content from Hybrid Neuro-Symbolic Pipeline
                "richNarrative": question.rich_narrative if hasattr(question, 'rich_narrative') else None,
                "richHtmlContent": question.rich_html_content if hasattr(question, 'rich_html_content') else None,
                "visualHints": question.visual_hints if hasattr(question, 'visual_hints') else None,
            }
            return response_dict
        except Exception as e:
            raise ValueError(f"Failed to generate question for {chapter}: {str(e)}")
    
    # ============================================================================
    # ANSWER MANAGEMENT
    # ============================================================================
    
    def submit_answer(
        self,
        session_id: str,
        question_id: str,
        answer_id: str,
        time_spent: int = 0
    ) -> Dict[str, Any]:
        """
        Submit an answer and get feedback.
        
        Args:
            session_id: Session ID
            question_id: Question ID
            answer_id: Selected answer ID (0-3 for 4-option MC)
            time_spent: Time spent on question (seconds)
            
        Returns:
            SubmitAnswerResponse {
                isCorrect: bool,
                correctAnswerId: str,
                selectedAnswerId: str,
                feedback: FeedbackConfig,
                masteryScore: { previous, current, delta },
                streakUpdate: { current, previous, milestone? },
                solution: { steps, summary },
                misconceptionDetected?: MisconceptionInfo,
                logicalTrapTriggered: bool,
                trapDetails: TrapInfo,
                attemptNumber: int
            }
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self._sessions[session_id]
        student_id = session["student_id"]
        
        # ⚠️ CRITICAL FIX: Retrieve the cached question instead of regenerating
        if "question_cache" not in session or question_id not in session["question_cache"]:
            raise ValueError(f"Question {question_id} not found in session cache")
        
        question = session["question_cache"][question_id]
        
        # Convert answer_id (string) to index
        try:
            selected_index = int(answer_id)
        except (ValueError, TypeError):
            selected_index = 0
        
        is_correct = selected_index == question.correct_option_index
        correct_index = question.correct_option_index
        
        # Get student's current mastery
        student = self.repository.get_student(student_id)
        previous_mastery = student.overall_percentage / 100 if student else 0
        
        # Calculate new mastery (simple: 10% increase per correct answer)
        mastery_delta = 0.1 if is_correct else -0.05
        current_mastery = min(1.0, max(0.0, previous_mastery + mastery_delta))
        
        # Update streak
        previous_streak = session.get("current_streak", 0)
        current_streak = (previous_streak + 1) if is_correct else 0
        streak_milestone = None
        
        if current_streak in [5, 10, 25, 50]:
            streak_milestone = current_streak
        
        # Record in session
        session["answers_submitted"].append({
            "question_id": question_id,
            "selected_index": selected_index,
            "is_correct": is_correct,
            "time_spent": time_spent,
        })
        session["attempted_count"] += 1
        if is_correct:
            session["correct_count"] += 1
        session["current_streak"] = current_streak
        
        # Detect misconceptions
        misconception_detected = None
        if not is_correct and hasattr(question, 'distractor_info') and question.distractor_info:
            # Find which misconception the student fell into
            selected_option = question.options[selected_index] if selected_index < len(question.options) else None
            for distractor in question.distractor_info.distractors:
                if distractor.value == selected_option:
                    misconception_detected = {
                        "type": distractor.misconception_type.value,
                        "explanation": distractor.why_wrong or "This is a common misconception",
                        "recommendation": distractor.teaching_point or f"Review the concept carefully"
                    }
                    break
        
        # Get logical trap info
        trap_triggered = False
        trap_details = {
            "id": "trap_1",
            "type": "logical",
            "explanation": ""
        }
        
        if hasattr(question, 'logical_trap') and question.logical_trap and not is_correct:
            trap_triggered = True
            trap_details["explanation"] = f"This is a common trap: {question.logical_trap}"
        elif hasattr(question, 'trap_info') and question.trap_info:
            trap = question.trap_info
            if not is_correct:
                trap_triggered = True
                trap_details["explanation"] = trap.description or "This is a logical trap in the question"
        
        return {
            "isCorrect": is_correct,
            "correctAnswerId": str(correct_index),
            "selectedAnswerId": answer_id,
            "feedback": {
                "depthLevel": "detailed" if not is_correct else "minimal",
                "showSolution": not is_correct,
                "enableHints": True,
                "showMisconception": misconception_detected is not None,
            },
            "masteryScore": {
                "previous": previous_mastery,
                "current": current_mastery,
                "delta": mastery_delta,
            },
            "streakUpdate": {
                "current": current_streak,
                "previous": previous_streak,
                "milestone": streak_milestone,
            },
            "solution": {
                "steps": self._format_solution_steps(question),
                "summary": f"The correct answer is option {correct_index}: {question.options[correct_index]}",
            },
            "misconceptionDetected": misconception_detected,
            "logicalTrapTriggered": trap_triggered,
            "trapDetails": trap_details,
            "attemptNumber": len(session["answers_submitted"]),
        }
    
    # ============================================================================
    # HINT MANAGEMENT
    # ============================================================================
    
    def get_hint(
        self,
        session_id: str,
        question_id: str,
        hint_index: int = 0
    ) -> Dict[str, Any]:
        """
        Get a hint for the current question.
        
        Args:
            session_id: Session ID
            question_id: Question ID
            hint_index: Which hint (0 = first, 1 = second, etc.)
            
        Returns:
            HintResponse {
                hintContent: str,
                hintType: str,
                hintIndex: int,
                remainingHints: int,
                maxHints: int,
                severity: int,
                displayFormat: str
            }
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self._sessions[session_id]
        
        # ⚠️ CRITICAL: Retrieve cached question for correct hints
        if "question_cache" not in session or question_id not in session["question_cache"]:
            raise ValueError(f"Question {question_id} not found in session cache")
        
        question = session["question_cache"][question_id]
        
        # Use hints from question if available
        hints = []
        if hasattr(question, 'hint_strategy') and question.hint_strategy and hasattr(question.hint_strategy, 'hints'):
            hints = question.hint_strategy.hints or []
        
        # If no hints in question, generate generic ones based on question type
        if not hints:
            hints = [
                {
                    "content": "Try breaking down the problem into smaller parts.",
                    "type": "conceptual",
                },
                {
                    "content": f"Look at the data representation: {question.data_representation if hasattr(question, 'data_representation') else 'the numbers'}",
                    "type": "visual",
                },
                {
                    "content": f"Consider: what is the question really asking for? It's asking for {question.topic}.",
                    "type": "example",
                },
            ]
        
        if hint_index >= len(hints):
            hint_index = len(hints) - 1
        
        hint = hints[hint_index] if hint_index < len(hints) else {"content": "No more hints available", "type": "info"}
        hint_content = hint.get("content") if isinstance(hint, dict) else str(hint)
        hint_type = hint.get("type", "conceptual") if isinstance(hint, dict) else "conceptual"
        
        return {
            "hintContent": hint_content,
            "hintType": hint_type,
            "hintIndex": hint_index,
            "remainingHints": max(0, 3 - hint_index - 1),
            "maxHints": 3,
            "severity": hint_index + 1,
            "displayFormat": "text",
        }
    
    # ============================================================================
    # SESSION COMPLETION
    # ============================================================================
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        End a session and return final results.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session summary with statistics
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self._sessions[session_id]
        attempted = session["attempted_count"]
        correct = session["correct_count"]
        accuracy = (correct / attempted * 100) if attempted > 0 else 0
        
        return {
            "sessionId": session_id,
            "finalScore": correct,
            "totalQuestions": attempted,
            "correctAnswers": correct,
            "accuracy": accuracy,
            "streak": session["current_streak"],
            "masteryGains": {
                "overall": correct * 0.1,  # 10% per correct
            },
            "completedAt": datetime.utcnow().isoformat(),
            "recommendations": self._generate_recommendations(
                session["chapter"],
                accuracy
            ),
        }
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _get_ui_config(self, grade_level: int, mode: str) -> Dict[str, Any]:
        """Get UI configuration based on grade level and mode."""
        return {
            "theme": "light",
            "fontSize": "medium" if grade_level >= 6 else "large",
            "animationIntensity": "medium",
            "showTimer": mode == "assessment",
            "hintsEnabled": True,
            "difficultyBadgeEnabled": True,
            "soundEnabled": True,
            "confettiEnabled": True,
            "feedbackDepth": "detailed" if mode == "practice" else "minimal",
        }
    
    def _get_available_chapters(self) -> List[Dict[str, str]]:
        """Get list of available chapters."""
        return [
            {"id": "large_numbers", "name": "Large Numbers", "icon": "🔢"},
            {"id": "dice_logic", "name": "Dice Logic", "icon": "🎲"},
            {"id": "cube_counting", "name": "Cube Counting", "icon": "📦"},
            {"id": "nets", "name": "Nets", "icon": "�"},
            {"id": "data_handling", "name": "Data Handling", "icon": "📊"},
            {"id": "clock_angles", "name": "Clock Angles", "icon": "�"},
            {"id": "symmetry", "name": "Symmetry", "icon": "🪞"},
            {"id": "rotation", "name": "Rotations", "icon": "🔄"},
            {"id": "factors_multiples", "name": "Factors & Multiples", "icon": "🎯"},
            {"id": "fractions_decimals", "name": "Fractions & Decimals", "icon": "�"},
        ]
    
    def _format_student_profile(self, student) -> Dict[str, Any]:
        """Format student data for frontend."""
        if not student:
            return {
                "studentId": "unknown",
                "name": "Guest",
                "gradeLevel": 6,
                "chapter": "Ch1: The Fish Tale",
                "masteryScore": 0.0,
                "totalQuestionsAttempted": 0,
            }
        
        return {
            "studentId": student.student_id if hasattr(student, 'student_id') else "unknown",
            "name": student.name if hasattr(student, 'name') else "Student",
            "gradeLevel": student.grade_level if hasattr(student, 'grade_level') else 6,
            "chapter": student.chapter if hasattr(student, 'chapter') else "Ch1: The Fish Tale",
            "masteryScore": (student.overall_percentage / 100) if hasattr(student, 'overall_percentage') else 0.0,
            "totalQuestionsAttempted": student.total_attempts if hasattr(student, 'total_attempts') else 0,
        }
    
    def _format_options(self, options: List[str]) -> List[Dict[str, str]]:
        """Format options for frontend."""
        return [
            {
                "id": str(i),
                "label": opt,
                "displayType": "text",
            }
            for i, opt in enumerate(options)
        ]
    
    def _format_solution_steps(self, question) -> List[Dict[str, str]]:
        """Format solution steps for frontend."""
        if hasattr(question, 'solution_steps') and question.solution_steps:
            return [
                {
                    "step": i + 1,
                    "explanation": step,
                }
                for i, step in enumerate(question.solution_steps)
            ]
        return [
            {
                "step": 1,
                "explanation": "Work through this step by step.",
            }
        ]
    
    def _generate_recommendations(self, chapter: str, accuracy: float) -> List[str]:
        """Generate recommendations based on performance."""
        recommendations = []
        
        if accuracy < 50:
            recommendations.append(f"Review {chapter} concepts with your teacher")
        elif accuracy < 70:
            recommendations.append(f"Practice more {chapter} problems")
        else:
            recommendations.append(f"Great job! Ready for next chapter?")
        
        return recommendations


# Singleton instance
_adapter_instance: Optional[SessionAdapter] = None


def get_session_adapter() -> SessionAdapter:
    """Get or create singleton SessionAdapter instance."""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = SessionAdapter()
    return _adapter_instance
