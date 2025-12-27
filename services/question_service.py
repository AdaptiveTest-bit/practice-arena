"""Business logic service for question generation and management.

Orchestrates the factory, deduplication, and validation layers.
"""

from typing import Optional
from models.question import Question, ChapterEnum
from factory import QuestionGeneratorFactory
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
    
    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================
    
    def _generate_question_id(self, session_id: str) -> str:
        """Generate a unique ID for a question in the cache.
        
        Args:
            session_id: The session ID (for debugging/organization)
        
        Returns:
            str: A unique question ID
        """
        import uuid
        return f"{session_id}_{uuid.uuid4().hex[:8]}"
