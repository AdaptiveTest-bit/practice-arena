"""Business logic service for question generation and management.

Orchestrates the factory, deduplication, and validation layers.
"""

from typing import Optional, Any, Dict
from models.question import Question, ChapterEnum
from services.deduplication import DeduplicationService


class QuestionService:
    """High-level service for generating questions with deduplication.
    
    Coordinates:
    - Factory pattern for strategy instantiation
    - Deduplication to prevent duplicate questions
    - Validation of generated questions
    - Session management
    """
    
    def __init__(self):
        """Initialize the question service."""
        self._dedup_service = DeduplicationService()
        self._question_cache = {}  # Map of question_id -> Question
        self._practice_to_dedup_session = {}  # Map practice_session_id -> dedup UUID
        self._question_context = {}  # Map question_id -> context dict
        
        # Add Phase 1 service integration
        try:
            from services.session_manager import SessionManager
            from services.bloom_level_enforcer import BloomLevelEnforcer
            from services.concept_mastery_tracker import ConceptMasteryTracker
            from services.break_point_tracker import BreakPointTracker
            
            self.session_manager = SessionManager()
            self.bloom_enforcer = BloomLevelEnforcer()
            self.concept_tracker = ConceptMasteryTracker()
            self.break_tracker = BreakPointTracker()
            
            from services.adaptive_question_selector import AdaptiveQuestionSelector
            self.adaptive_selector = AdaptiveQuestionSelector()
        except Exception as e:
            print(f"Warning: Could not initialize Phase 1 services: {e}")
            self.session_manager = None
            self.bloom_enforcer = None
            self.concept_tracker = None
            self.break_tracker = None
    
    def create_session(self) -> str:
        """Create a new user session for deduplication tracking.
        
        Returns:
            str: A unique session ID
        """
        return self._dedup_service.create_session()
    
    def generate_question(
        self,
        session_id: str,
        chapter: ChapterEnum,
        max_regeneration_attempts: int = 5
    ) -> tuple[Question, str]:
        """Generate a unique question for the given chapter.
        
        Automatically handles regeneration if a duplicate is detected.
        
        Args:
            session_id: The session ID (from create_session)
            chapter: The ChapterEnum value
            max_regeneration_attempts: Max times to retry if duplicates found
        
        Returns:
            Tuple of (Question, question_id) where question_id is for later lookup
            
        Raises:
            ValueError: If unable to generate unique question after max attempts
        """
        if session_id not in self._dedup_service._sessions:
            raise ValueError(f"Invalid session_id: {session_id}")
        
        # Create strategy instance using factory
        from factory import QuestionGeneratorFactory
        strategy = QuestionGeneratorFactory.create(chapter)
        
        # Try to generate a unique question
        for attempt in range(max_regeneration_attempts):
            question = strategy.generate()
            
            if not self._dedup_service.is_duplicate(session_id, question):
                # Found a unique question
                self._dedup_service.track_question(session_id, question)
                
                # Generate unique question ID and cache it
                question_id = self._generate_question_id(session_id)
                self._question_cache[question_id] = question
                
                return question, question_id
            else:
                # Duplicate detected, record it
                self._dedup_service.mark_regeneration_attempt(session_id)
        
        # Failed to generate unique question
        raise ValueError(
            f"Could not generate unique question after {max_regeneration_attempts} attempts. "
            f"Try increasing max_regeneration_attempts or review question variety."
        )
    
    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """Retrieve a cached question by its ID.
        
        Args:
            question_id: The question ID returned from generate_question
        
        Returns:
            The Question object, or None if not found
        """
        return self._question_cache.get(question_id)
    
    def get_session_stats(self, session_id: str) -> dict:
        """Get deduplication statistics for a session.
        
        Args:
            session_id: The session ID
        
        Returns:
            Dict with dedup statistics
        """
        return self._dedup_service.get_stats(session_id)
    
    def end_session(self, session_id: str) -> None:
        """End a session and clean up resources.
        
        Args:
            session_id: The session ID
        """
        # Remove cached questions for this session
        # (In production, could use session-prefixed IDs for easier cleanup)
        self._dedup_service.delete_session(session_id)
    
    def check_answer_with_tracking(
        self, session_id: str, question_id: str, user_answer: str
    ) -> bool:
        """Check an answer with deduplication tracking.
        
        Args:
            session_id: The session ID (from create_session)
            question_id: The question ID (for lookup)
            user_answer: The user's answer to check
        
        Returns:
            bool: True if the answer is correct, False otherwise
            
        Raises:
            ValueError: If the session or question is invalid
        """
        if session_id not in self._dedup_service._sessions:
            raise ValueError(f"Invalid session_id: {session_id}")
        
        question = self.get_question_by_id(question_id)
        if not question:
            raise ValueError(f"Invalid question_id: {question_id}")
        
        # Track the answer attempt (for analytics, deduplication, etc.)
        self._dedup_service.track_answer_attempt(session_id, question, user_answer)
        
        # Check the answer using the existing method
        is_correct = question.check_answer(user_answer)
        
        return is_correct
    
    # =========================================================================
    # PHASE 3: PRACTICE SESSION CANONICAL FLOW
    # =========================================================================

    def _get_or_create_dedup_session_for_practice(self, practice_session_id: int) -> str:
        """Return a stable internal dedup session UUID for a DB practice session."""
        if practice_session_id in self._practice_to_dedup_session:
            return self._practice_to_dedup_session[practice_session_id]
        
        dedup_session_id = self._dedup_service.create_session()
        self._practice_to_dedup_session[practice_session_id] = dedup_session_id
        return dedup_session_id

    def generate_next_question_for_practice(self, practice_session_id: int):
        """Generate next question for a practice session using adaptive selection.
        
        Falls back to simple generation if Phase 1 services not initialized.
        """
        # FALLBACK: If Phase 1 services not initialized, use simple generation
        if not self.session_manager:
            return self._generate_next_question_simple(practice_session_id)
        
        session = self.session_manager._get_session(practice_session_id)
        if not session:
            raise ValueError(f"Session {practice_session_id} not found")
        
        chapter_id = int(session.chapter_id)
        bloom_level = "remember"
        if self.bloom_enforcer:
            current = self.bloom_enforcer.get_current_level(practice_session_id)
            if current:
                bloom_level = current
        
        from config.chapter_config import get_chapter_concepts, validate_bloom_level
        if not validate_bloom_level(bloom_level):
            bloom_level = "remember"
        
        chapter_concepts = get_chapter_concepts(chapter_id)
        if not chapter_concepts:
            raise ValueError(f"No concepts configured for chapter_id={chapter_id}")
        
        concept = chapter_concepts[0]
        difficulty = 1.0
        if self.adaptive_selector:
            try:
                analysis = self.adaptive_selector.analyze_learning_gaps(practice_session_id, chapter_id)
                focus = analysis.get("next_focus")
                if focus and focus in chapter_concepts:
                    concept = focus
                difficulty = float(self.adaptive_selector.get_question_difficulty(chapter_id, bloom_level))
            except Exception:
                pass
        
        chapter_enum = self._map_chapter_id_to_question_chapter(chapter_id)
        dedup_session_id = self._get_or_create_dedup_session_for_practice(practice_session_id)
        question, question_id = self.generate_question(dedup_session_id, chapter_enum)
        
        self._question_context[question_id] = {
            "practice_session_id": practice_session_id,
            "chapter_id": chapter_id,
            "concept": concept,
            "bloom_level": bloom_level,
            "difficulty": difficulty,
        }
        
        return {
            "success": True,
            "session_id": practice_session_id,
            "question_id": question_id,
            "chapter_id": chapter_id,
            "concept": concept,
            "bloom_level": bloom_level,
            "difficulty": difficulty,
            "question_text": question.question_text,
            "options": question.options,
            # Rich content fields for hybrid neuro-symbolic rendering
            "rich_narrative": getattr(question, "rich_narrative", None),
            "rich_html_content": getattr(question, "rich_html_content", None),
            "visual_hints": getattr(question, "visual_hints", None),
            "logical_trap": getattr(question, "logical_trap", None),
            "solution_steps": getattr(question, "solution_steps", None),
            # Phase 1-3 metadata (optional)
            "distractor_info": getattr(question, "distractor_info", None),
            "trap_info": getattr(question, "trap_info", None),
            "bloom_info": getattr(question, "bloom_info", None),
        }

    def submit_answer_for_practice(self, practice_session_id: int, question_id: str, selected_index: int, time_taken_seconds: Optional[int] = None):
        """Submit answer and update all Phase 1 DB trackers."""
        if not (self.session_manager and self.bloom_enforcer and self.concept_tracker and self.break_tracker):
            raise RuntimeError("Phase 1 services not initialized")
        
        ctx = self._question_context.get(question_id)
        if not ctx:
            raise ValueError(f"Unknown question_id: {question_id}")
        
        if int(ctx.get("practice_session_id")) != int(practice_session_id):
            raise ValueError("question_id does not belong to this session")
        
        question = self.get_question_by_id(question_id)
        if not question or question.correct_option_index is None:
            raise ValueError("Question not found or not multiple-choice")
        
        is_correct = int(selected_index) == int(question.correct_option_index)
        concept = ctx["concept"]
        bloom_level = ctx["bloom_level"]
        
        self.bloom_enforcer.update_level_accuracy(practice_session_id, bloom_level, is_correct)
        concept_result = self.concept_tracker.update_concept_accuracy(practice_session_id, concept, is_correct, bloom_level)
        
        if concept_result and float(concept_result.get("accuracy", 0.0)) < 0.70:
            self.break_tracker.record_break_point(practice_session_id, concept, bloom_level, float(concept_result.get("accuracy", 0.0)), int(concept_result.get("total_questions", 1)), int(concept_result.get("correct_answers", 0)))
        
        advancement = self.bloom_enforcer.can_advance_to_next_level(practice_session_id, bloom_level)
        session = self.session_manager._get_session(practice_session_id)
        if not session:
            raise ValueError(f"Session {practice_session_id} not found")
        
        updated_session = self.session_manager.update_session_progress(practice_session_id, {"total_questions_attempted": (session.total_questions_attempted or 0) + 1, "total_questions_correct": (session.total_questions_correct or 0) + (1 if is_correct else 0)})
        
        overall_accuracy = float(updated_session.overall_accuracy or 0.0) if updated_session else 0.0
        completion_percentage = float(updated_session.completion_percentage or 0.0) if updated_session else 0.0
        
        try:
            dedup_session_id = self._practice_to_dedup_session.get(practice_session_id)
            if dedup_session_id:
                self._dedup_service.track_answer_attempt(dedup_session_id, question, str(selected_index))
        except Exception:
            pass
        
        return {"success": True, "session_id": practice_session_id, "question_id": question_id, "is_correct": is_correct, "correct_index": question.correct_option_index, "answer": question.answer, "solution_steps": question.solution_steps, "concept": concept, "bloom_level": bloom_level, "concept_accuracy": float(concept_result.get("accuracy", 0.0)) if concept_result else 0.0, "concept_status": concept_result.get("status", "not_started") if concept_result else "not_started", "can_advance_to_next_level": bool(advancement.get("can_advance", False)), "advancement_message": advancement.get("message", ""), "overall_accuracy": overall_accuracy, "completion_percentage": completion_percentage}

    def _map_chapter_id_to_question_chapter(self, chapter_id: int) -> ChapterEnum:
        """Map numeric chapter_id (config) -> ChapterEnum (question generation)."""
        mapping = {
            1: ChapterEnum.LARGE_NUMBERS,
            2: ChapterEnum.CLOCK_ANGLES,
            3: ChapterEnum.SYMMETRY,
            4: ChapterEnum.ROTATION,
            5: ChapterEnum.FRACTION_AREA,
            6: ChapterEnum.FRACTIONS_DECIMALS,
            7: ChapterEnum.DICE_LOGIC,
            8: ChapterEnum.NETS,
            9: ChapterEnum.FACTORS_MULTIPLES,
            10: ChapterEnum.DATA_PATTERNS,
            11: ChapterEnum.MAPPING,
            12: ChapterEnum.CUBE_COUNTING,
            13: ChapterEnum.GEOMETRY_MEASUREMENT,
            14: ChapterEnum.DATA_HANDLING,
            15: ChapterEnum.MULTIPLICATION_DIVISION,
            16: ChapterEnum.MEASUREMENT,
        }
        return mapping.get(chapter_id, ChapterEnum.LARGE_NUMBERS)

    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================
    
    def _generate_next_question_simple(self, practice_session_id: int):
        """Fallback: Generate question without Phase 1 services.
        
        Used when session_manager not initialized. Simply generates a question
        from the strategy with rich content included.
        """
        from models.question import ChapterEnum
        
        # Map practice_session_id to a chapter (simple mapping)
        # In production with Phase 1 services, this comes from session_manager
        chapter_mapping = {
            1: ChapterEnum.FACTORS_MULTIPLES,
            2: ChapterEnum.FACTORS_MULTIPLES,
            3: ChapterEnum.FACTORS_MULTIPLES,
            5: ChapterEnum.FACTORS_MULTIPLES,
        }
        
        chapter_enum = chapter_mapping.get(
            practice_session_id % 5,
            ChapterEnum.FACTORS_MULTIPLES
        )
        
        # Create strategy and generate question
        from factory import QuestionGeneratorFactory
        strategy = QuestionGeneratorFactory.create(chapter_enum)
        question = strategy.generate()
        
        # Generate question ID and cache it
        dedup_session_id = self._get_or_create_dedup_session_for_practice(practice_session_id)
        question_id = self._generate_question_id(dedup_session_id)
        self._question_cache[question_id] = question
        
        # Return response with rich content
        return {
            "success": True,
            "session_id": practice_session_id,
            "question_id": question_id,
            "chapter_id": 5,  # Factors & Multiples
            "concept": "factors_multiples",
            "bloom_level": "understand",
            "difficulty": 2.0,
            "question_text": question.question_text,
            "options": question.options,
            # Include rich content fields for frontend display
            "rich_narrative": getattr(question, "rich_narrative", None),
            "rich_html_content": getattr(question, "rich_html_content", None),
            "visual_hints": getattr(question, "visual_hints", None),
        }
    
    def _generate_question_id(self, session_id: str) -> str:
        """Generate a unique ID for a question in the cache.
        
        Args:
            session_id: The session ID (for debugging/organization)
        
        Returns:
            str: A unique question ID
        """
        import uuid
        return f"{session_id}_{uuid.uuid4().hex[:8]}"
