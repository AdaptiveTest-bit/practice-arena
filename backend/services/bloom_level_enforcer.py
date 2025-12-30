"""Bloom's Level Enforcer - Manages progression through Bloom's cognitive levels.

Responsibilities:
1. Enforce sequential Bloom's level progression (Remember → Understand → Apply → Analyze → Evaluate → Create)
2. Check if student can advance to next level (80% accuracy required)
3. Calculate accuracy for each level
4. Lock/unlock levels based on performance
5. Provide progression recommendations
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from database import SessionLocal, PracticeSession, get_practice_session, update_practice_session


class BloomLevelEnforcer:
    """Manages Bloom's level progression and enforcement."""
    
    # Bloom's levels in order
    BLOOM_LEVELS = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
    
    # Minimum accuracy required to advance (80%)
    ADVANCEMENT_THRESHOLD = 0.80
    
    # Minimum questions needed to evaluate a level (5 questions)
    MIN_QUESTIONS_FOR_LEVEL = 5
    
    def __init__(self):
        """Initialize the enforcer."""
        pass
    
    # ========================================================================
    # LEVEL ADVANCEMENT LOGIC
    # ========================================================================
    
    def can_advance_to_next_level(self, session_id: int, current_level: str) -> Dict[str, Any]:
        """
        Check if student can advance from current Bloom level to the next.
        
        Rule: Must have >= 80% accuracy at current level with minimum questions.
        
        Args:
            session_id: ID of the practice session
            current_level: Current Bloom level
        
        Returns:
            Dictionary with advancement status:
            {
                "can_advance": True/False,
                "current_level": "remember",
                "next_level": "understand",
                "current_accuracy": 0.85,
                "required_accuracy": 0.80,
                "questions_completed": 7,
                "questions_required": 5,
                "message": "..."
            }
        """
        session = get_practice_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Get current level stats
        bloom_data = session.bloom_levels_completed.get(current_level, {})
        accuracy = bloom_data.get("accuracy", 0.0)
        questions_completed = bloom_data.get("questions_completed", 0)
        
        # Find next level
        next_level = self._get_next_level(current_level)
        
        # Check advancement criteria
        can_advance = (
            accuracy >= self.ADVANCEMENT_THRESHOLD and
            questions_completed >= self.MIN_QUESTIONS_FOR_LEVEL and
            next_level is not None
        )
        
        # Generate message
        if not can_advance:
            if accuracy < self.ADVANCEMENT_THRESHOLD:
                message = f"Need {self.ADVANCEMENT_THRESHOLD*100:.0f}% accuracy. You're at {accuracy*100:.1f}%."
            elif questions_completed < self.MIN_QUESTIONS_FOR_LEVEL:
                message = f"Need {self.MIN_QUESTIONS_FOR_LEVEL} questions. You've done {questions_completed}."
            else:
                message = "Cannot advance further."
        else:
            message = f"✅ Ready to advance to {next_level}!"
        
        return {
            "can_advance": can_advance,
            "current_level": current_level,
            "next_level": next_level,
            "current_accuracy": round(accuracy, 2),
            "required_accuracy": self.ADVANCEMENT_THRESHOLD,
            "questions_completed": questions_completed,
            "questions_required": self.MIN_QUESTIONS_FOR_LEVEL,
            "message": message
        }
    
    def advance_to_next_level(self, session_id: int, current_level: str) -> Dict[str, Any]:
        """
        Advance student to the next Bloom level (if eligible).
        
        Operations:
        1. Check if advancement is allowed
        2. Mark current level as "completed"
        3. Unlock next level
        4. Mark next level as "in_progress"
        5. Save changes
        
        Args:
            session_id: ID of the practice session
            current_level: Current Bloom level
        
        Returns:
            Dictionary with advancement result
        """
        # Check if can advance
        advancement_check = self.can_advance_to_next_level(session_id, current_level)
        if not advancement_check.get("can_advance"):
            return {
                "success": False,
                "message": advancement_check.get("message", "Cannot advance"),
                "current_level": current_level
            }
        
        session = get_practice_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        next_level = advancement_check["next_level"]
        
        # Update bloom levels
        bloom_data = session.bloom_levels_completed
        
        # Mark current as completed
        if current_level in bloom_data:
            bloom_data[current_level]["status"] = "completed"
            bloom_data[current_level]["completed_at"] = datetime.utcnow().isoformat()
        
        # Mark next as in_progress
        if next_level and next_level in bloom_data:
            bloom_data[next_level]["status"] = "in_progress"
        
        # Save changes
        update_practice_session(session_id, {
            "bloom_levels_completed": bloom_data
        })
        
        return {
            "success": True,
            "message": f"✅ Advanced to {next_level}!",
            "previous_level": current_level,
            "current_level": next_level,
            "previous_accuracy": round(advancement_check["current_accuracy"], 2)
        }
    
    # ========================================================================
    # LEVEL STATUS QUERIES
    # ========================================================================
    
    def get_current_level(self, session_id: int) -> Optional[str]:
        """
        Get the current active Bloom level for a session.
        
        Returns the highest unlocked level that is either "in_progress" or "completed".
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            Current Bloom level or None
        """
        session = get_practice_session(session_id)
        if not session:
            return None
        
        # Find the highest level with status "in_progress" or "completed"
        for level in reversed(self.BLOOM_LEVELS):
            if level in session.bloom_levels_completed:
                status = session.bloom_levels_completed[level].get("status")
                if status in ["in_progress", "completed"]:
                    return level
        
        return "remember"
    
    def get_level_status(self, session_id: int, level: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed status of a specific Bloom level.
        
        Args:
            session_id: ID of the practice session
            level: Bloom level name
        
        Returns:
            Dictionary with level status or None
        """
        session = get_practice_session(session_id)
        if not session or level not in session.bloom_levels_completed:
            return None
        
        level_data = session.bloom_levels_completed[level]
        
        return {
            "level": level,
            "status": level_data.get("status"),
            "accuracy": round(level_data.get("accuracy", 0), 2),
            "questions_completed": level_data.get("questions_completed", 0),
            "completed_at": level_data.get("completed_at"),
            "can_advance": level_data.get("accuracy", 0) >= self.ADVANCEMENT_THRESHOLD
        }
    
    def get_all_levels_status(self, session_id: int) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Get status of all Bloom levels.
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            Dictionary with all levels' statuses
        """
        session = get_practice_session(session_id)
        if not session:
            return None
        
        status_by_level = {}
        for level in self.BLOOM_LEVELS:
            if level in session.bloom_levels_completed:
                level_status = self.get_level_status(session_id, level)
                if level_status:
                    status_by_level[level] = level_status
        
        return status_by_level
    
    # ========================================================================
    # ACCURACY CALCULATION & UPDATES
    # ========================================================================
    
    def update_level_accuracy(
        self,
        session_id: int,
        level: str,
        is_correct: bool,
        timestamp: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update accuracy for a Bloom level based on a new question result.
        
        Recalculates the accuracy for the level:
        accuracy = total_correct / total_questions
        
        Args:
            session_id: ID of the practice session
            level: Bloom level
            is_correct: Whether the question was answered correctly
            timestamp: When the answer was given (optional)
        
        Returns:
            Dictionary with updated accuracy
        """
        session = get_practice_session(session_id)
        if not session or level not in session.bloom_levels_completed:
            return None
        
        level_data = session.bloom_levels_completed[level]
        
        # Update counters
        total = level_data.get("questions_completed", 0) + 1
        correct = level_data.get("questions_correct", 0)
        if is_correct:
            correct += 1
        
        # Calculate new accuracy
        new_accuracy = correct / total if total > 0 else 0.0
        
        # Update the data
        level_data["questions_completed"] = total
        level_data["questions_correct"] = correct
        level_data["accuracy"] = new_accuracy
        
        # Mark as in_progress if not already
        if level_data.get("status") == "locked":
            level_data["status"] = "in_progress"
        
        # Save changes
        update_practice_session(session_id, {
            "bloom_levels_completed": session.bloom_levels_completed
        })
        
        return {
            "level": level,
            "questions_completed": total,
            "questions_correct": correct,
            "accuracy": round(new_accuracy, 2),
            "can_advance": new_accuracy >= self.ADVANCEMENT_THRESHOLD and total >= self.MIN_QUESTIONS_FOR_LEVEL
        }
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _get_next_level(self, current_level: str) -> Optional[str]:
        """Get the next Bloom level."""
        try:
            current_idx = self.BLOOM_LEVELS.index(current_level)
            if current_idx < len(self.BLOOM_LEVELS) - 1:
                return self.BLOOM_LEVELS[current_idx + 1]
        except ValueError:
            pass
        
        return None
    
    def _get_previous_level(self, current_level: str) -> Optional[str]:
        """Get the previous Bloom level."""
        try:
            current_idx = self.BLOOM_LEVELS.index(current_level)
            if current_idx > 0:
                return self.BLOOM_LEVELS[current_idx - 1]
        except ValueError:
            pass
        
        return None
    
    def is_level_locked(self, session_id: int, level: str) -> bool:
        """Check if a level is locked."""
        status = self.get_level_status(session_id, level)
        if status:
            return status["status"] == "locked"
        return True
    
    def is_level_completed(self, session_id: int, level: str) -> bool:
        """Check if a level is completed."""
        status = self.get_level_status(session_id, level)
        if status:
            return status["status"] == "completed"
        return False
    
    def get_next_level_to_practice(self, session_id: int) -> Optional[str]:
        """
        Get the recommended next Bloom level to practice.
        
        Returns:
        - Current level if not yet completed
        - Next level if current is completed
        - None if all levels are completed
        """
        current = self.get_current_level(session_id)
        
        if not current:
            return "remember"
        
        if self.is_level_completed(session_id, current):
            next_level = self._get_next_level(current)
            if next_level:
                return next_level
            return None
        
        return current
