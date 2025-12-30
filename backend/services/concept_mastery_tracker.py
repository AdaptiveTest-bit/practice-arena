"""Concept Mastery Tracker - Tracks student mastery of individual concepts.

Responsibilities:
1. Track accuracy per concept
2. Determine if concept is mastered (80%+ accuracy)
3. Identify weak concepts (< 70% accuracy)
4. Calculate concept progression within Bloom's levels
5. Provide concept-level recommendations
"""

from typing import Optional, Dict, Any, List
from database import SessionLocal, PracticeSession, get_practice_session, update_practice_session


class ConceptMasteryTracker:
    """Tracks student mastery of individual concepts."""
    
    # Mastery threshold (80% accuracy)
    MASTERY_THRESHOLD = 0.80
    
    # Weakness threshold (70% accuracy)
    WEAKNESS_THRESHOLD = 0.70
    
    # Minimum questions needed to evaluate a concept (3 questions)
    MIN_QUESTIONS_FOR_CONCEPT = 3
    
    def __init__(self):
        """Initialize the tracker."""
        pass
    
    # ========================================================================
    # CONCEPT ACCURACY UPDATES
    # ========================================================================
    
    def update_concept_accuracy(
        self,
        session_id: int,
        concept: str,
        is_correct: bool,
        bloom_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update accuracy for a concept based on a new question result.
        
        Operations:
        1. Get current accuracy for concept
        2. Recalculate with new answer
        3. Determine if mastered (>= 80%) or weak (< 70%)
        4. Update session data
        
        Args:
            session_id: ID of the practice session
            concept: Name of the concept
            is_correct: Whether the question was answered correctly
            bloom_level: Current Bloom level (optional, for tracking)
        
        Returns:
            Dictionary with updated accuracy info
        """
        session = get_practice_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Get or initialize concept in session
        accuracy_by_concept = session.accuracy_by_concept or {}
        
        # Get current stats (stored as decimal)
        current_stats = accuracy_by_concept.get(concept, {
            "total": 0,
            "correct": 0,
            "accuracy": 0.0
        })
        
        # Update counters
        total = current_stats["total"] + 1
        correct = current_stats["correct"] + (1 if is_correct else 0)
        new_accuracy = correct / total if total > 0 else 0.0
        
        # Update the concept stats
        current_stats["total"] = total
        current_stats["correct"] = correct
        current_stats["accuracy"] = round(new_accuracy, 3)
        current_stats["last_updated"] = True  # Flag for tracking
        
        if bloom_level:
            current_stats["last_bloom_level"] = bloom_level
        
        accuracy_by_concept[concept] = current_stats
        
        # Determine mastery status
        mastery_status = self._determine_mastery_status(concept, current_stats)
        
        # Update session's concepts lists
        concepts_covered = session.concepts_covered or []
        concepts_mastered = session.concepts_mastered or []
        concepts_weak = session.concepts_weak or []
        
        # Add to covered if new
        if concept not in concepts_covered:
            concepts_covered.append(concept)
        
        # Update mastery list
        if mastery_status == "mastered" and concept not in concepts_mastered:
            concepts_mastered.append(concept)
            # Remove from weak if previously there
            if concept in concepts_weak:
                concepts_weak.remove(concept)
        
        # Update weak list
        elif mastery_status == "weak" and concept not in concepts_weak:
            concepts_weak.append(concept)
            # Remove from mastered if previously there
            if concept in concepts_mastered:
                concepts_mastered.remove(concept)
        
        # Remove from both if in progress
        elif mastery_status == "in_progress":
            if concept in concepts_mastered:
                concepts_mastered.remove(concept)
            if concept in concepts_weak:
                concepts_weak.remove(concept)
        
        # Save all updates
        update_practice_session(session_id, {
            "accuracy_by_concept": accuracy_by_concept,
            "concepts_covered": concepts_covered,
            "concepts_mastered": concepts_mastered,
            "concepts_weak": concepts_weak
        })
        
        return {
            "concept": concept,
            "total_questions": total,
            "correct_answers": correct,
            "accuracy": round(new_accuracy, 2),
            "mastery_status": mastery_status,
            "is_mastered": mastery_status == "mastered",
            "is_weak": mastery_status == "weak",
            "message": self._generate_concept_message(concept, mastery_status, new_accuracy)
        }
    
    # ========================================================================
    # CONCEPT STATUS QUERIES
    # ========================================================================
    
    def get_concept_accuracy(self, session_id: int, concept: str) -> Optional[Dict[str, Any]]:
        """
        Get accuracy information for a specific concept.
        
        Args:
            session_id: ID of the practice session
            concept: Name of the concept
        
        Returns:
            Dictionary with concept accuracy or None
        """
        session = get_practice_session(session_id)
        if not session:
            return None
        
        accuracy_by_concept = session.accuracy_by_concept or {}
        
        if concept not in accuracy_by_concept:
            return {
                "concept": concept,
                "total_questions": 0,
                "correct_answers": 0,
                "accuracy": 0.0,
                "mastery_status": "not_started",
                "is_mastered": False,
                "is_weak": False
            }
        
        stats = accuracy_by_concept[concept]
        mastery_status = self._determine_mastery_status(concept, stats)
        
        return {
            "concept": concept,
            "total_questions": stats.get("total", 0),
            "correct_answers": stats.get("correct", 0),
            "accuracy": round(stats.get("accuracy", 0), 2),
            "mastery_status": mastery_status,
            "is_mastered": mastery_status == "mastered",
            "is_weak": mastery_status == "weak",
            "last_bloom_level": stats.get("last_bloom_level")
        }
    
    def get_all_concepts_accuracy(self, session_id: int) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Get accuracy for all concepts in a session.
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            Dictionary with accuracy for all concepts
        """
        session = get_practice_session(session_id)
        if not session:
            return None
        
        accuracy_by_concept = session.accuracy_by_concept or {}
        
        result = {}
        for concept in accuracy_by_concept:
            result[concept] = self.get_concept_accuracy(session_id, concept)
        
        return result
    
    def get_mastered_concepts(self, session_id: int) -> List[str]:
        """
        Get list of mastered concepts.
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            List of mastered concept names
        """
        session = get_practice_session(session_id)
        if not session:
            return []
        
        return session.concepts_mastered or []
    
    def get_weak_concepts(self, session_id: int) -> List[str]:
        """
        Get list of weak concepts.
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            List of weak concept names
        """
        session = get_practice_session(session_id)
        if not session:
            return []
        
        return session.concepts_weak or []
    
    def get_concepts_in_progress(self, session_id: int) -> List[str]:
        """
        Get list of concepts still being practiced (not yet mastered or weak).
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            List of concept names in progress
        """
        session = get_practice_session(session_id)
        if not session:
            return []
        
        concepts_covered = session.concepts_covered or []
        concepts_mastered = session.concepts_mastered or []
        concepts_weak = session.concepts_weak or []
        
        # In progress = covered but not mastered and not weak
        in_progress = [
            c for c in concepts_covered
            if c not in concepts_mastered and c not in concepts_weak
        ]
        
        return in_progress
    
    # ========================================================================
    # CONCEPT RECOMMENDATIONS
    # ========================================================================
    
    def get_concept_recommendations(self, session_id: int) -> Dict[str, List[str]]:
        """
        Get recommendations based on concept performance.
        
        Returns:
        - What to focus on next
        - What needs remediation
        - What's going well
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            Dictionary with recommendations
        """
        session = get_practice_session(session_id)
        if not session:
            return {}
        
        weak_concepts = self.get_weak_concepts(session_id)
        mastered_concepts = self.get_mastered_concepts(session_id)
        in_progress = self.get_concepts_in_progress(session_id)
        
        recommendations = {
            "focus_on": weak_concepts[:2] if weak_concepts else [],
            "continue_practicing": in_progress[:2] if in_progress else [],
            "celebrate_mastery": mastered_concepts[:2] if mastered_concepts else [],
            "next_concepts": in_progress[2:] if len(in_progress) > 2 else []
        }
        
        return recommendations
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _determine_mastery_status(
        self,
        concept: str,
        stats: Dict[str, Any]
    ) -> str:
        """
        Determine the mastery status of a concept.
        
        Returns: "mastered", "weak", "in_progress", or "not_started"
        """
        total = stats.get("total", 0)
        accuracy = stats.get("accuracy", 0)
        
        if total == 0:
            return "not_started"
        elif total < self.MIN_QUESTIONS_FOR_CONCEPT:
            return "in_progress"  # Not enough questions yet
        elif accuracy >= self.MASTERY_THRESHOLD:
            return "mastered"
        elif accuracy < self.WEAKNESS_THRESHOLD:
            return "weak"
        else:
            return "in_progress"
    
    def _generate_concept_message(
        self,
        concept: str,
        status: str,
        accuracy: float
    ) -> str:
        """Generate a feedback message for concept performance."""
        if status == "mastered":
            return f"🎉 Mastered '{concept}'! Accuracy: {accuracy*100:.0f}%"
        elif status == "weak":
            return f"⚠️  Weak area: '{concept}'. Accuracy: {accuracy*100:.0f}%. Keep practicing!"
        elif accuracy >= 0.70:
            return f"📚 Good progress on '{concept}'. Accuracy: {accuracy*100:.0f}%. Almost there!"
        else:
            return f"🔄 Practicing '{concept}'. Accuracy: {accuracy*100:.0f}%."
    
    def calculate_average_accuracy(self, session_id: int) -> float:
        """
        Calculate average accuracy across all concepts.
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            Average accuracy (0-1)
        """
        session = get_practice_session(session_id)
        if not session:
            return 0.0
        
        accuracy_by_concept = session.accuracy_by_concept or {}
        
        if not accuracy_by_concept:
            return 0.0
        
        total_accuracy = sum(stats.get("accuracy", 0) for stats in accuracy_by_concept.values())
        avg = total_accuracy / len(accuracy_by_concept)
        
        return round(avg, 2)
    
    def get_concept_summary(self, session_id: int) -> Dict[str, Any]:
        """
        Get a summary of concept performance.
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            Dictionary with concept summary
        """
        session = get_practice_session(session_id)
        if not session:
            return {}
        
        mastered = self.get_mastered_concepts(session_id)
        weak = self.get_weak_concepts(session_id)
        in_progress = self.get_concepts_in_progress(session_id)
        avg_accuracy = self.calculate_average_accuracy(session_id)
        
        return {
            "total_concepts_covered": len(session.concepts_covered or []),
            "concepts_mastered": len(mastered),
            "concepts_weak": len(weak),
            "concepts_in_progress": len(in_progress),
            "average_accuracy": avg_accuracy,
            "mastered_list": mastered,
            "weak_list": weak,
            "in_progress_list": in_progress
        }
