"""Deduplication service for session-level uniqueness tracking.

Prevents users from receiving the same question twice in a single session.
"""

from typing import Dict, Set, Optional
from models.question import Question
import uuid


class DeduplicationService:
    """Manages session-level question deduplication using fingerprints.
    
    Uses SHA256 hashing of question content to track uniqueness.
    Supports multiple concurrent sessions with separate tracking.
    """
    
    def __init__(self):
        """Initialize the deduplication service."""
        # Map of session_id -> set of question fingerprints
        self._sessions: Dict[str, Set[str]] = {}
        # Map of session_id -> dedup stats
        self._stats: Dict[str, Dict] = {}
    
    def create_session(self) -> str:
        """Create a new session for question generation.
        
        Returns:
            str: A unique session ID
        """
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = set()
        self._stats[session_id] = {
            'total_generated': 0,
            'unique_questions': 0,
            'duplicates_regenerated': 0
        }
        return session_id
    
    def is_duplicate(self, session_id: str, question: Question) -> bool:
        """Check if a question was already generated in this session.
        
        Args:
            session_id: The session ID
            question: The question to check
        
        Returns:
            bool: True if this question was already in the session
            
        Raises:
            ValueError: If session_id is not found
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        fingerprint = question.get_fingerprint()
        return fingerprint in self._sessions[session_id]
    
    def track_question(self, session_id: str, question: Question) -> None:
        """Add a question to the session's tracked fingerprints.
        
        Args:
            session_id: The session ID
            question: The question to track
            
        Raises:
            ValueError: If session_id is not found
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        fingerprint = question.get_fingerprint()
        self._sessions[session_id].add(fingerprint)
        self._stats[session_id]['unique_questions'] += 1
    
    def mark_regeneration_attempt(self, session_id: str) -> None:
        """Record that a duplicate was detected and a regeneration was attempted.
        
        Args:
            session_id: The session ID
            
        Raises:
            ValueError: If session_id is not found
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        self._stats[session_id]['duplicates_regenerated'] += 1
    
    def get_stats(self, session_id: str) -> Dict:
        """Get deduplication statistics for a session.
        
        Args:
            session_id: The session ID
        
        Returns:
            Dict with keys: total_generated, unique_questions, duplicates_regenerated, success_rate
            
        Raises:
            ValueError: If session_id is not found
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        stats = self._stats[session_id].copy()
        total = stats['unique_questions'] + stats['duplicates_regenerated']
        success_rate = (stats['unique_questions'] / total * 100) if total > 0 else 0
        stats['success_rate'] = round(success_rate, 1)
        
        return stats
    
    def delete_session(self, session_id: str) -> None:
        """Clean up a session (e.g., when user logs out).
        
        Args:
            session_id: The session ID
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
        if session_id in self._stats:
            del self._stats[session_id]
    
    def cleanup_old_sessions(self, max_sessions: int = 1000) -> None:
        """Clean up oldest sessions if there are too many.
        
        Useful for long-running servers to prevent memory leaks.
        
        Args:
            max_sessions: Maximum number of sessions to keep
        """
        if len(self._sessions) > max_sessions:
            # Keep only the most recent sessions
            # In production, use timestamps for better cleanup
            sessions_to_delete = list(self._sessions.keys())[: -max_sessions]
            for session_id in sessions_to_delete:
                self.delete_session(session_id)
    
    def track_answer_attempt(self, session_id: str, question: Question, user_answer: str) -> None:
        """Track an answer attempt for session analytics.

        This is lightweight in-memory tracking used by `QuestionService.check_answer_with_tracking`.
        It does NOT persist to the database.

        Args:
            session_id: The session ID
            question: The question attempted
            user_answer: The user's answer
        """
        if session_id not in self._stats:
            raise ValueError(f"Session {session_id} not found")

        # Initialize attempts list lazily
        if "answer_attempts" not in self._stats[session_id]:
            self._stats[session_id]["answer_attempts"] = []

        self._stats[session_id]["answer_attempts"].append(
            {
                "fingerprint": question.get_fingerprint(),
                "question_text": question.question_text,
                "user_answer": user_answer,
            }
        )

    def get_answer_attempts(self, session_id: str):
        """Get all recorded answer attempts for a session."""
        if session_id not in self._stats:
            raise ValueError(f"Session {session_id} not found")
        return self._stats[session_id].get("answer_attempts", [])
