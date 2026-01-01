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

from config.logging_config import get_logger
from models.question import ChapterEnum
from factory import QuestionGeneratorFactory
from services.adaptive_learning_service import AdaptiveLearningService
from services.orm_student_repository import get_repository, ORMStudentRepository
from services.misconception_analyzer import MisconceptionDetector

logger = get_logger(__name__)


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
        Get next question in the quiz sequence with ADAPTIVE ROUTING.
        
        🆕 PHASE 2 ENHANCEMENT: 
        Uses adaptive_engine to recommend next chapter based on student mastery.
        Automatically routes to different chapters as student progresses.
        
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
        student_id = session.get("student_id")
        grade_level = session["grade_level"]
        
        # 🆕 PHASE 2: GET ADAPTIVE ROUTING RECOMMENDATION
        try:
            student = self.repository.get_student(student_id)
            if student:
                # Get adaptive recommendation from adaptive_engine
                recommendation = self.adaptive_service.adaptive_engine.generate_learning_recommendation(student)
                next_chapter = recommendation.get("recommended_chapter", session["chapter"])
                
                # Track chapter transitions for analytics
                if next_chapter != session["chapter"]:
                    session["chapter"] = next_chapter
                    if "chapter_transitions" not in session:
                        session["chapter_transitions"] = []
                    session["chapter_transitions"].append({
                        "from": session.get("previous_chapter", session["chapter"]),
                        "to": next_chapter,
                        "timestamp": datetime.utcnow().isoformat(),
                        "reason": recommendation.get("reason", "adaptive_progression"),
                        "student_status": recommendation.get("performance_status", "unknown")
                    })
                    session["previous_chapter"] = session["chapter"]
                    print(f"✨ Adaptive routing: Student {student_id} routed from {session['chapter_transitions'][-1]['from']} → {next_chapter}")
            else:
                next_chapter = session["chapter"]
        except Exception as e:
            # Fallback to current chapter if adaptive routing fails
            print(f"⚠️ Adaptive routing failed: {e}, using current chapter")
            next_chapter = session["chapter"]
        
        chapter = next_chapter
        
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
            attempted = session.get("attempted_count", 0)
            correct = session.get("correct_count", 0)
            accuracy = (correct / attempted * 100) if attempted > 0 else 50

            if accuracy > 70 and attempted > 3:
                difficulty = min(5, base_difficulty + 1)
            elif accuracy < 30 and attempted > 3:
                difficulty = max(1, base_difficulty - 1)
            else:
                difficulty = base_difficulty

            # Override with question's own difficulty if it has one
            if hasattr(question, "difficulty") and question.difficulty:
                # Blend: 60% from student progression, 40% from question difficulty
                difficulty = int(difficulty * 0.6 + question.difficulty * 0.4)

            # --- Normalize options (fix duplicate labels / inconsistent correct index) ---
            # Some strategies may occasionally output duplicate option labels (e.g., several "9").
            # The frontend keys and correctness are index-based, so duplicates are confusing and
            # can make feedback look wrong. If duplicates are detected, rebuild options from
            # distractor_info (which provides correct_answer + distractors) and re-align correct index.
            try:
                if hasattr(question, "options") and question.options:
                    opts = [str(o) for o in question.options]
                    if len(opts) != len(set(opts)):
                        if hasattr(question, "distractor_info") and question.distractor_info:
                            reconstructed = [
                                str(question.distractor_info.correct_answer),
                                *[str(d.value) for d in getattr(question.distractor_info, "distractors", [])],
                            ]
                            # Only accept if it yields 4 unique options
                            if len(reconstructed) == 4 and len(set(reconstructed)) == 4:
                                question.options = reconstructed
                                # Ensure correct index points to correct_answer
                                question.correct_option_index = 0
            except Exception as e:
                logger.warning(f"Option normalization skipped due to error: {e}")

            # 1. Extract distractor information for options
            try:
                formatted_options = self._format_options_with_misconceptions(
                    question.options,
                    question.distractor_info if hasattr(question, 'distractor_info') else None,
                    question.trap_info if hasattr(question, 'trap_info') else None
                )
            except Exception as e:
                logger.error(f"Error in _format_options_with_misconceptions: {e}", exc_info=True)
                raise
            
            # 2. Extract data representation (tables, diagrams, etc.)
            try:
                data_representation = self._extract_data_representation(question)
            except Exception as e:
                logger.error(f"Error in _extract_data_representation: {e}", exc_info=True)
                raise
            
            # 3. Build hint strategy with visual hints
            try:
                hint_strategy = self._build_hint_strategy(question)
            except Exception as e:
                logger.error(f"Error in _build_hint_strategy: {e}", exc_info=True)
                raise
            
            # 4. Convert difficulty integer to enum
            try:
                difficulty_enum = self._convert_difficulty_to_enum(difficulty)
            except Exception as e:
                logger.error(f"Error in _convert_difficulty_to_enum: {e}", exc_info=True)
                raise
            
            # 5. Extract chapter ID
            try:
                chapter_id = self._get_chapter_id(chapter)
            except Exception as e:
                logger.error(f"Error in _get_chapter_id: {e}", exc_info=True)
                raise
            
            # 6. Get subtopic if available
            try:
                subtopic = self._extract_subtopic(question)
            except Exception as e:
                logger.error(f"Error in _extract_subtopic: {e}", exc_info=True)
                raise
            
            # 7. Build rendering hints
            try:
                rendering_hints = self._build_rendering_hints(question)
            except Exception as e:
                logger.error(f"Error in _build_rendering_hints: {e}", exc_info=True)
                raise
            
            try:
                response_dict = {
                    "questionId": question_id,
                    "topic": question.topic if hasattr(question, 'topic') else chapter,
                    "subtopic": subtopic,
                    "chapterId": chapter_id,
                    "difficulty": difficulty_enum,  # ✅ Now enum, not integer
                    "question": question.question_text,
                    "questionContext": self._extract_question_context(question),
                    "dataRepresentation": data_representation,
                    "options": formatted_options,  # ✅ Now with misconception data
                    "optionLayout": self._build_option_layout(),
                    "estimatedTime": 60,  # seconds
                    "misconceptionTag": question.misconception_category if hasattr(question, 'misconception_category') else None,
                    "logicalTrapPresent": bool(question.logical_trap if hasattr(question, 'logical_trap') else False),
                    # 🔗 Bloom's cognitive level (for adaptive sequencing)
                    # Note: bloom_level is already converted to string by Pydantic (use_enum_values=True)
                    "bloomLevel": question.bloom_info.bloom_level if (hasattr(question, 'bloom_info') and question.bloom_info) else "remember",
                    # ✅ Hint strategy with visual hints transformed to HintItem objects
                    "hintStrategy": hint_strategy,
                    # ✅ Rendering hints for frontend configuration
                    "renderingHints": rendering_hints,
                    # 🆕 Rich content from Hybrid Neuro-Symbolic Pipeline
                    "richNarrative": question.rich_narrative if hasattr(question, 'rich_narrative') else None,
                    "richHtmlContent": question.rich_html_content if hasattr(question, 'rich_html_content') else None,
                    "visualHints": question.visual_hints if hasattr(question, 'visual_hints') else None,
                    # ✅ Additional data for feedback and analytics
                    "correctAnswerId": str(question.correct_option_index),
                    "attemptNumber": len(session["answers_submitted"]),
                }
            except Exception as e:
                import traceback
                logger.error(f"Error building response_dict: {traceback.format_exc()}")
                raise
            return response_dict
        except Exception as e:
            import traceback
            logger.error(f"Full traceback for question generation error: {traceback.format_exc()}")
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
    
    def _format_options(self, options: List[str]) -> List[Dict[str, Any]]:
        """Format options for frontend as AnswerOption objects."""
        return [
            {
                "id": str(i),
                "label": opt,
                "displayType": "text",
                "commonMistake": False,
                # Optional fields (set to None by default)
                "icon": None,
                "imageUrl": None,
                "misconceptionTarget": None,
                "isTrap": False,
                "trapExplanation": None,
                "selectionFrequency": None,
            }
            for i, opt in enumerate(options)
        ]
    
    def _format_options_with_misconceptions(
        self, 
        options: List[str], 
        distractor_info=None,
        trap_info=None
    ) -> List[Dict[str, Any]]:
        """Format options with misconception and trap data extracted from distractor_info and trap_info."""
        formatted = []

        # Support both older trap_info shapes (with trap_indices) and TrapInfo model (single trap for the question)
        trap_indices = None
        trap_description = None
        try:
            if trap_info is not None:
                trap_indices = getattr(trap_info, "trap_indices", None)
                trap_description = getattr(trap_info, "description", None)
        except Exception:
            trap_indices = None
            trap_description = None

        for i, opt in enumerate(options):
            option_dict = {
                "id": str(i),
                "label": opt,
                "displayType": "text",
                "commonMistake": False,
                "icon": None,
                "imageUrl": None,
                "misconceptionTarget": None,  # Will be populated below as object with {id, name, explanation}
                "isTrap": False,  # Will be populated below
                "trapExplanation": None,
                "selectionFrequency": None,
            }

            # Extract misconception data if available
            if distractor_info and hasattr(distractor_info, 'distractors'):
                for distractor in distractor_info.distractors:
                    if distractor.value == opt:
                        misconception_type = (
                            distractor.misconception_type.value 
                            if hasattr(distractor.misconception_type, 'value') 
                            else str(distractor.misconception_type)
                        )
                        option_dict["misconceptionTarget"] = {
                            "id": f"misconception_{i}_{misconception_type}",
                            "name": misconception_type.replace("_", " ").title(),
                            "explanation": distractor.why_wrong or f"This represents a {misconception_type} misconception",
                        }
                        option_dict["commonMistake"] = True
                        break

            # Extract trap data
            # - If trap_indices exists: mark those indices as traps
            # - Else if trap_info exists (TrapInfo model): keep logicalTrapPresent at question-level,
            #   but do not force an option-level trap unless indices are provided.
            if trap_indices is not None:
                try:
                    if i in trap_indices:
                        option_dict["isTrap"] = True
                        option_dict["trapExplanation"] = trap_description or "This is a logical trap"
                except Exception:
                    pass

            formatted.append(option_dict)

        return formatted
    
    def _extract_data_representation(self, question) -> Dict[str, Any]:
        """Extract data representation (tables, diagrams) from question."""
        if not hasattr(question, 'data_representation') or not question.data_representation:
            return None
        
        data_rep = question.data_representation
        
        # Detect representation type
        repr_type = "text"
        if "```" in data_rep:
            repr_type = "code"
        elif "|" in data_rep:
            repr_type = "table"
        elif any(char in data_rep for char in ["●", "○", "■", "□"]):
            repr_type = "diagram"
        
        return {
            "type": repr_type,
            "url": None,  # Backend sends text/markdown, not URL
            "alt": f"Visual representation for {question.topic}",
            "caption": f"Data: {question.topic}",
            "content": data_rep,  # Raw markdown/text content
        }
    
    def _build_hint_strategy(self, question) -> Dict[str, Any]:
        """Build hint strategy with visual hints transformed to HintItem objects."""
        hints = []
        
        # Extract visual hints if available
        if hasattr(question, 'visual_hints') and question.visual_hints:
            hints = [
                {
                    "id": f"hint_{i}",
                    "order": i,
                    "type": "visual",
                    "content": hint_text,
                    "severity": ["light", "moderate", "heavy"][min(i, 2)],  # ✅ Use enum string, not int
                }
                for i, hint_text in enumerate(question.visual_hints)
            ]
        
        # Fallback generic hints if none available
        if not hints:
            hints = [
                {
                    "id": "hint_0",
                    "order": 0,
                    "type": "conceptual",
                    "content": "Break down the problem into smaller parts.",
                    "severity": "light",  # ✅ Use enum string
                },
                {
                    "id": "hint_1",
                    "order": 1,
                    "type": "visual",
                    "content": "Look for patterns or relationships in the numbers.",
                    "severity": "moderate",  # ✅ Use enum string
                },
                {
                    "id": "hint_2",
                    "order": 2,
                    "type": "process",
                    "content": "Work through the calculation step by step.",
                    "severity": "heavy",  # ✅ Use enum string
                },
            ]
        
        return {
            "available": len(hints) > 0,
            "allowedCount": min(3, len(hints)),
            "hints": hints,
            "showHintButton": True,
            "hintButtonPlacement": "bottom_right",
        }
    
    def _convert_difficulty_to_enum(self, difficulty: int) -> str:
        """Convert integer difficulty (1-5) to enum string."""
        if difficulty <= 2:
            return "easy"
        elif difficulty == 3:
            return "medium"
        else:
            return "hard"
    
    def _get_chapter_id(self, chapter: str) -> str:
        """Extract chapter ID from chapter string."""
        chapter_mapping = {
            "large_numbers": "ch_1_large_numbers",
            "dice_logic": "ch_2_dice_logic",
            "cube_counting": "ch_3_cube_counting",
            "nets": "ch_4_nets",
            "data_handling": "ch_5_data_handling",
            "clock_angles": "ch_6_clock_angles",
            "symmetry": "ch_7_symmetry",
            "rotation": "ch_8_rotation",
            "factors_multiples": "ch_9_factors_multiples",
            "fractions_decimals": "ch_10_fractions_decimals",
        }
        return chapter_mapping.get(chapter, f"ch_{chapter}")
    
    def _extract_subtopic(self, question) -> str:
        """Extract subtopic from question if available."""
        if hasattr(question, 'subtopic') and question.subtopic:
            return question.subtopic
        
        # Fallback: use topic as subtopic
        if hasattr(question, 'topic') and question.topic:
            return question.topic
        
        return None
    
    def _build_rendering_hints(self, question) -> Dict[str, bool]:
        """Build rendering hints configuration for frontend."""
        return {
            "showDifficulty": True,
            "showTimer": True,
            "showBloomLevel": True,
            "showHintCount": True,
            "showProgressBar": True,
            "enableAnimations": True,
            "enableSoundFeedback": True,
            "enableConfetti": True,
            "useAdaptiveLayout": True,
            "prioritizeAccessibility": False,
        }
    
    def _extract_question_context(self, question) -> str:
        """Extract additional context for the question."""
        if hasattr(question, 'question_context') and question.question_context:
            return question.question_context
        
        # Fallback: use rich_narrative as context
        if hasattr(question, 'rich_narrative') and question.rich_narrative:
            return question.rich_narrative[:200]  # First 200 chars
        
        return None
    
    def _build_option_layout(self) -> Dict[str, Any]:
        """Build option layout configuration for frontend."""
        return {
            "type": "grid",
            "columns": 2,
            "shuffle": False,
            "tileStyle": "elevated",
            "tileSize": "medium",
        }

    
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
