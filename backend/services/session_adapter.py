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
        
        # Detect misconceptions with advanced feedback
        misconception_detected = None
        advanced_misconception_feedback = None
        
        if not is_correct and hasattr(question, 'distractor_info') and question.distractor_info:
            # Find which misconception the student fell into
            selected_option = question.options[selected_index] if selected_index < len(question.options) else None
            for distractor in question.distractor_info.distractors:
                if distractor.value == selected_option:
                    misconception_type = distractor.misconception_type.value if hasattr(distractor.misconception_type, 'value') else str(distractor.misconception_type)
                    
                    misconception_detected = {
                        "type": misconception_type,
                        "explanation": distractor.why_wrong or "This is a common misconception",
                        "recommendation": distractor.teaching_point or f"Review the concept carefully"
                    }
                    
                    # Get advanced pedagogical feedback
                    advanced_misconception_feedback = self._get_advanced_misconception_feedback(
                        misconception_type,
                        question
                    )
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
            "advancedMisconceptionFeedback": advanced_misconception_feedback,  # ← NEW: Advanced feedback
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
            session_id: Session ID (can be UUID string or numeric ID from database)
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
        # ✅ FIX: Try multiple session lookup strategies
        session = None
        
        # Strategy 1: Check in-memory session store
        if session_id in self._sessions:
            session = self._sessions[session_id]
        
        # Strategy 2: If not in memory, try to load from database
        if session is None:
            try:
                # Try to load session from database
                db_session = self.repository.get_session(session_id)
                if db_session:
                    # Create session dict from database record
                    session = {
                        "student_id": str(db_session.student_id),
                        "grade_level": db_session.class_level or 6,
                        "mode": "practice",
                        "chapter": "large_numbers",
                        "question_cache": {},  # Will be populated on demand
                    }
            except Exception as e:
                # Database lookup failed, continue without it
                pass
        
        # If still not found, raise error
        if session is None:
            raise ValueError(f"Session {session_id} not found in memory or database")
        
        # ⚠️ CRITICAL: Retrieve cached question for correct hints
        if "question_cache" not in session or question_id not in session["question_cache"]:
            # If question not in cache, we'll generate generic hints
            # (In a real scenario, you'd regenerate the question or look it up)
            pass
        
        question = None
        if "question_cache" in session and question_id in session["question_cache"]:
            question = session["question_cache"][question_id]
        
        # ✅ FIX: Use visual_hints array from question if available
        # This array is shown in "Reference Hints (if needed next time)" after submission
        # Question model has: visual_hints (snake_case)
        hints = []
        
        if question and hasattr(question, 'visual_hints') and question.visual_hints:
            # Convert visual_hints string array to hint objects
            hints = [
                {
                    "content": hint_text,
                    "type": "reference",
                }
                for hint_text in question.visual_hints
            ]
        
        # If no visual_hints in question, generate generic ones as fallback
        if not hints:
            hints = [
                {
                    "content": "Try breaking down the problem into smaller parts.",
                    "type": "conceptual",
                },
                {
                    "content": "Look at the numbers and their relationship to each other.",
                    "type": "visual",
                },
                {
                    "content": "Consider what the question is really asking you to find.",
                    "type": "process",
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
    
    # ============================================================================
    # ADVANCED BLOOM'S LEVEL TRACKING (From integrated_session_adapter.py)
    # ============================================================================
    
    def _get_advanced_misconception_feedback(self, misconception_type: str, question) -> str:
        """Generate advanced pedagogical feedback for detected misconception.
        
        Maps 10 specific misconception types to targeted feedback.
        """
        from models.distractor import MisconceptionType
        
        feedback_map = {
            "opposite_confusion": 
                "✗ You inverted the answer. Remember to carefully check if your result is correct before finalizing.",
            
            "universal_vs_specific":
                "✗ This rule works for this case, but check if it applies universally to all similar problems.",
            
            "operation_direction":
                "✗ Check whether you should multiply or divide here. Think about what the problem is asking.",
            
            "incomplete_reasoning":
                "✗ You're on the right track, but it looks like you missed a step. Are you sure your answer is complete?",
            
            "arithmetic_error":
                "✗ Your approach is correct, but double-check your arithmetic/calculation.",
            
            "formula_misapplication":
                "✗ You used the wrong formula. Make sure you understand which formula applies to this type of problem.",
            
            "formula_confusion":
                "✗ This resembles another formula, but it's different. Review the difference between these formulas.",
            
            "constraint_violation":
                "✗ You ignored a constraint or condition in the problem. Re-read carefully.",
            
            "similar_concept_error":
                "✗ This concept is similar to another one you know, but they're different. Make sure you understand the distinction.",
            
            "pattern_misidentification":
                "✗ Check if you identified the pattern correctly. Look more carefully at the sequence.",
        }
        
        # Get custom description from trap_info if available
        if hasattr(question, 'trap_info') and question.trap_info:
            return f"✗ {question.trap_info.description}"
        
        # Use generic feedback
        return feedback_map.get(
            misconception_type.lower() if isinstance(misconception_type, str) else str(misconception_type),
            "✗ Your answer is not correct. Review your working."
        )
    
    def _check_bloom_progression(self, student, bloom_level_str: str) -> str:
        """Check if student can progress to next Bloom's level (80% mastery rule).
        
        Implements sophisticated Bloom's taxonomy progression:
        - Requires 80% accuracy on current level
        - Requires at least 3 attempts
        - Provides progression guidance
        """
        if not student:
            return ""
        
        # Try to get Bloom's mastery from student progress
        if hasattr(student, 'bloom_mastery'):
            if bloom_level_str in student.bloom_mastery:
                mastery = student.bloom_mastery[bloom_level_str]
                percentage = mastery.get('percentage_correct', 0) if isinstance(mastery, dict) else 0
                attempts = mastery.get('attempts', 0) if isinstance(mastery, dict) else 0
                
                # Check if they've reached 80% (mastered)
                if percentage >= 80 and attempts >= 3:
                    next_level = self._next_bloom_level(bloom_level_str)
                    return f"✓ Great progress! You've mastered {bloom_level_str.title()} ({percentage:.1f}%). You can now advance to {next_level.title()}."
                elif percentage >= 70:
                    return f"Good progress on {bloom_level_str.title()} ({percentage:.1f}%). Keep practicing to reach 80% mastery."
                else:
                    return f"You're working on {bloom_level_str.title()} ({percentage:.1f}%). Keep attempting more questions to improve."
        
        return ""
    
    def _next_bloom_level(self, current: str) -> str:
        """Get next Bloom's level in sequence."""
        sequence = [
            "remember", "understand", "apply", "analyze", "evaluate", "create"
        ]
        try:
            current_lower = current.lower() if isinstance(current, str) else str(current)
            idx = sequence.index(current_lower)
            if idx < len(sequence) - 1:
                return sequence[idx + 1]
        except (ValueError, IndexError):
            pass
        return "create"
    
    def _determine_next_action_advanced(
        self,
        student,
        bloom_level_str: str,
        difficulty_level: int,
        is_correct: bool
    ) -> str:
        """Determine what the student should do next (adaptive routing).
        
        Uses Bloom's mastery threshold to route students:
        - Struggling: Same level, same difficulty
        - Proficient: Same level, increase difficulty
        - Mastered: Next Bloom's level
        """
        if not student:
            return "Try another question at this level"
        
        # If wrong, focus on same level
        if not is_correct:
            return f"Try another {difficulty_level}/5 difficulty question at {bloom_level_str} level to strengthen understanding"
        
        # If correct, check advancement
        if hasattr(student, 'bloom_mastery'):
            if bloom_level_str in student.bloom_mastery:
                mastery = student.bloom_mastery[bloom_level_str]
                percentage = mastery.get('percentage_correct', 0) if isinstance(mastery, dict) else 0
                attempts = mastery.get('attempts', 0) if isinstance(mastery, dict) else 0
                
                # If they've reached mastery, advance
                if percentage >= 80 and attempts >= 3:
                    next_level = self._next_bloom_level(bloom_level_str)
                    return f"Excellent! Try questions at the next level: {next_level}"
                
                # Otherwise, stay at level but can increase difficulty
                if difficulty_level < 5:
                    return f"Good! Try a level {difficulty_level + 1}/5 difficulty question at {bloom_level_str} level"
                else:
                    return f"Perfect! Get another question at {bloom_level_str} level"
        
        return "Try another question at this level"


# Singleton instance
_adapter_instance: Optional[SessionAdapter] = None


def get_session_adapter() -> SessionAdapter:
    """Get or create singleton SessionAdapter instance."""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = SessionAdapter()
    return _adapter_instance
