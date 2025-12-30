"""Session Manager Service - Handles creation, resumption, and tracking of practice sessions.

Responsibilities:
1. Create new practice sessions
2. Resume existing sessions
3. Update session progress
4. Track session timing
5. Calculate completion percentage
6. Store break points
7. End sessions and finalize analytics
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
import json
from database import SessionLocal, PracticeSession, create_practice_session, get_practice_session, update_practice_session, end_practice_session


class SessionManager:
    """Manages practice session lifecycle and progress tracking."""
    
    def __init__(self):
        """Initialize the session manager."""
        pass
    
    # ========================================================================
    # SESSION LIFECYCLE MANAGEMENT
    # ========================================================================
    
    def start_session(
        self,
        student_id: int,
        chapter_id: int,
        class_level: int = 5,
        subject: str = "Mathematics"
    ) -> Dict[str, Any]:
        """
        Start a new practice session or resume an existing one.
        
        Logic:
        1. Check if student has an active (in_progress) session for this chapter
        2. If yes, return resume data
        3. If no, create a new session
        4. Return session data with initial bloom levels
        
        Args:
            student_id: ID of the student
            chapter_id: ID of the chapter
            class_level: Grade level (default 5)
            subject: Subject name (default Mathematics)
        
        Returns:
            Dictionary with session info and initial data
        """
        db = SessionLocal()
        try:
            # Check for active session
            existing_session = db.query(PracticeSession).filter(
                PracticeSession.student_id == student_id,
                PracticeSession.chapter_id == chapter_id,
                PracticeSession.status == "in_progress"
            ).first()
            
            if existing_session:
                # Resume existing session
                return {
                    "success": True,
                    "session_id": existing_session.id,
                    "status": "resumed",
                    "student_id": student_id,
                    "chapter_id": chapter_id,
                    "current_bloom_level": self._get_current_bloom_level(existing_session),
                    "completion_percentage": existing_session.completion_percentage,
                    "progress": self._get_session_progress(existing_session)
                }
            
            # Create new session
            session = PracticeSession(
                student_id=student_id,
                chapter_id=chapter_id,
                class_level=class_level,
                subject=subject,
                status="in_progress",
                completion_percentage=0,
                bloom_levels_completed=self._initialize_bloom_levels()
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            
            return {
                "success": True,
                "session_id": session.id,
                "status": "new",
                "student_id": student_id,
                "chapter_id": chapter_id,
                "current_bloom_level": "remember",
                "completion_percentage": 0,
                "progress": self._get_session_progress(session)
            }
        finally:
            db.close()
    
    def update_session_progress(
        self,
        session_id: int,
        updates: Dict[str, Any]
    ) -> Optional[PracticeSession]:
        """
        Update session progress with new information.
        
        Updates can include:
        - accuracy_by_concept
        - concepts_covered
        - concepts_mastered
        - bloom_levels_completed
        - misconceptions_detected
        - completion_percentage
        - And more
        
        Args:
            session_id: ID of the session to update
            updates: Dictionary of fields to update
        
        Returns:
            Updated PracticeSession or None if not found
        """
        session = get_practice_session(session_id)
        if not session:
            return None
        
        # Update each field carefully
        for key, value in updates.items():
            if hasattr(session, key):
                current_value = getattr(session, key)
                
                # Handle JSON fields that need merging
                if key in ["accuracy_by_concept", "misconceptions_detected", "bloom_levels_completed"]:
                    if isinstance(current_value, dict) and isinstance(value, dict):
                        current_value.update(value)
                        setattr(session, key, current_value)
                    else:
                        setattr(session, key, value)
                # Handle list fields that need appending
                elif key in ["concepts_covered", "concepts_mastered", "concepts_weak", "break_points"]:
                    if isinstance(current_value, list) and isinstance(value, list):
                        # Avoid duplicates in lists
                        for item in value:
                            if item not in current_value:
                                current_value.append(item)
                        setattr(session, key, current_value)
                    else:
                        setattr(session, key, value)
                else:
                    setattr(session, key, value)
        
        # Save updates
        db = SessionLocal()
        try:
            db.merge(session)
            db.commit()
            return session
        finally:
            db.close()
    
    def end_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        End a practice session and finalize analytics.
        
        Operations:
        1. Set session_end_time
        2. Calculate total_duration_minutes
        3. Calculate overall_accuracy
        4. Mark as completed
        5. Return summary
        
        Args:
            session_id: ID of the session to end
        
        Returns:
            Dictionary with session summary or None if not found
        """
        session = end_practice_session(session_id)
        if not session:
            return None
        
        return {
            "success": True,
            "session_id": session.id,
            "status": "completed",
            "completion_percentage": session.completion_percentage,
            "session_summary": {
                "total_duration_minutes": session.total_duration_minutes,
                "total_questions_attempted": session.total_questions_attempted,
                "total_questions_correct": session.total_questions_correct,
                "overall_accuracy": round(session.overall_accuracy, 2),
                "concepts_covered": session.concepts_covered,
                "concepts_mastered": session.concepts_mastered,
                "concepts_weak": session.concepts_weak,
                "misconceptions_found": len(session.misconceptions_detected),
                "break_points_found": len(session.break_points)
            },
            "recommendations": self._generate_recommendations(session)
        }
    
    def pause_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Pause a session (student can resume later).
        
        Args:
            session_id: ID of the session to pause
        
        Returns:
            Dictionary with pause confirmation
        """
        session = get_practice_session(session_id)
        if not session or session.status != "in_progress":
            return None
        
        update_practice_session(session_id, {"status": "paused"})
        
        return {
            "success": True,
            "session_id": session_id,
            "status": "paused",
            "message": "Session paused. You can resume anytime."
        }
    
    # ========================================================================
    # PROGRESS TRACKING
    # ========================================================================
    
    def get_session_progress(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed progress information for a session.
        
        Args:
            session_id: ID of the session
        
        Returns:
            Dictionary with detailed progress info
        """
        session = get_practice_session(session_id)
        if not session:
            return None
        
        return self._get_session_progress(session)
    
    def _get_session(self, session_id: int) -> Optional[PracticeSession]:
        """
        Get a practice session by ID.
        
        Args:
            session_id: ID of the session
        
        Returns:
            PracticeSession object or None if not found
        """
        return get_practice_session(session_id)
    
    def _get_session_progress(self, session: PracticeSession) -> Dict[str, Any]:
        """Internal method to get session progress from a session object."""
        current_bloom = self._get_current_bloom_level(session)
        next_bloom = self._get_next_bloom_level(current_bloom)
        
        return {
            "session_id": session.id,
            "student_id": session.student_id,
            "chapter_id": session.chapter_id,
            "subject": session.subject or "Mathematics",
            "class_level": session.class_level or 5,
            "completion_percentage": session.completion_percentage or 0,
            "session_duration_minutes": self._calculate_duration_minutes(session),
            "current_bloom_level": current_bloom,
            "next_bloom_level": next_bloom,
            "concepts_covered": session.concepts_covered or [],
            "concepts_mastered": session.concepts_mastered or [],
            "concepts_weak": session.concepts_weak or [],
            "accuracy_by_concept": session.accuracy_by_concept or {},
            "overall_accuracy": round(session.overall_accuracy, 2) if session.overall_accuracy else 0,
            "total_questions_attempted": session.total_questions_attempted or 0,
            "total_questions_correct": session.total_questions_correct or 0,
            "status": session.status or "in_progress",
            "session_start_time": session.session_start_time.isoformat() if session.session_start_time else "",
            "last_updated": session.updated_at.isoformat() if session.updated_at else "",
            "bloom_levels_progress": self._get_bloom_levels_progress(session)
        }
    
    def calculate_session_completion_percentage(self, session: PracticeSession) -> float:
        """
        Calculate the overall completion percentage of a session.
        
        Factors:
        - Concepts covered (out of total in chapter)
        - Concepts mastered
        - Bloom levels completed
        
        Args:
            session: PracticeSession object
        
        Returns:
            Completion percentage (0-100)
        """
        # For MVP: Simple calculation based on questions answered
        # Can be refined later based on chapter config
        if session.total_questions_attempted == 0:
            return 0.0
        
        # Assume 30-40 questions per chapter for full completion
        # This is a rough estimate
        completion = min(100.0, (session.total_questions_attempted / 40) * 100)
        return round(completion, 1)
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _initialize_bloom_levels(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the bloom levels structure for a new session."""
        bloom_levels = [
            "remember",
            "understand",
            "apply",
            "analyze",
            "evaluate",
            "create"
        ]
        
        return {
            level: {
                "status": "unlocked" if level == "remember" else "locked",
                "accuracy": 0.0,
                "questions_completed": 0,
                "completed_at": None
            }
            for level in bloom_levels
        }
    
    def _get_current_bloom_level(self, session: PracticeSession) -> str:
        """Get the current/highest unlocked Bloom's level."""
        bloom_levels = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
        
        if not session.bloom_levels_completed:
            return "remember"
        
        # Find the highest completed level
        for level in reversed(bloom_levels):
            if level in session.bloom_levels_completed:
                level_data = session.bloom_levels_completed[level]
                if level_data.get("status") in ["completed", "in_progress"]:
                    return level
        
        return "remember"
    
    def _get_next_bloom_level(self, current_level: str) -> Optional[str]:
        """Get the next Bloom level after the current one."""
        bloom_levels = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
        
        try:
            current_idx = bloom_levels.index(current_level)
            if current_idx < len(bloom_levels) - 1:
                return bloom_levels[current_idx + 1]
        except (ValueError, IndexError):
            pass
        
        return None
    
    def _get_bloom_levels_progress(self, session: PracticeSession) -> Dict[str, Dict[str, Any]]:
        """Get progress for all Bloom levels."""
        progress = {}
        
        for level, data in session.bloom_levels_completed.items():
            progress[level] = {
                "status": data.get("status", "not_started"),
                "accuracy": round(data.get("accuracy", 0), 2),
                "questions_completed": data.get("questions_completed", 0),
                "completed_at": data.get("completed_at")
            }
        
        return progress
    
    def _calculate_duration_minutes(self, session: PracticeSession) -> int:
        """Calculate session duration in minutes."""
        if session.total_duration_minutes:
            return session.total_duration_minutes
        
        if session.session_start_time:
            end_time = session.session_end_time or datetime.utcnow()
            duration = (end_time - session.session_start_time).total_seconds()
            return int(duration / 60)
        
        return 0
    
    def _generate_recommendations(self, session: PracticeSession) -> List[str]:
        """Generate recommendations based on session performance."""
        recommendations = []
        
        # Completion message
        if session.completion_percentage >= 80:
            recommendations.append("✅ Excellent! You've completed the chapter above 80%.")
        elif session.completion_percentage >= 60:
            recommendations.append("🟡 Good progress! Continue practicing to reach 80%.")
        else:
            recommendations.append("⏳ Keep practicing! You're on your way.")
        
        # Weak concepts
        if session.concepts_weak:
            weak_list = ", ".join(session.concepts_weak[:2])
            recommendations.append(f"📚 Focus on: {weak_list}")
        
        # Misconceptions
        if session.misconceptions_detected:
            misconception_count = len(session.misconceptions_detected)
            recommendations.append(f"⚠️ Address {misconception_count} misconception(s) for better understanding.")
        
        # Mastered concepts
        if session.concepts_mastered:
            mastered_list = ", ".join(session.concepts_mastered[:2])
            recommendations.append(f"🎉 You've mastered: {mastered_list}")
        
        return recommendations
    
    def check_session_completion(self, session_id: int) -> Dict[str, Any]:
        """
        Check if student has achieved mastery across all dimensions.
        
        Criteria (ALL must be met):
        1. Difficulty 1-5: ALL ≥80% accuracy
        2. Bloom's Remember-Apply: ALL ≥80% accuracy  
        3. All concepts: ≥80% accuracy each
        4. No problematic misconceptions (2+ errors in same type)
        """
        session = get_practice_session(session_id)
        if not session:
            return {
                "success": False,
                "error": "Session not found",
                "is_complete": False
            }
        
        # ===== CHECK 1: DIFFICULTY MASTERY (1-5) =====
        difficulty_mastery = {}
        all_difficulties_mastered = True
        
        for difficulty in range(1, 6):
            difficulty_stats = session.accuracy_by_concept.get(f"difficulty_{difficulty}", {
                "attempts": 0,
                "correct": 0,
                "accuracy": 0.0
            })
            accuracy = difficulty_stats.get("accuracy", 0.0) if isinstance(difficulty_stats, dict) else 0.0
            attempts = difficulty_stats.get("attempts", 0) if isinstance(difficulty_stats, dict) else 0
            
            difficulty_mastery[difficulty] = {
                "accuracy": accuracy,
                "attempts": attempts,
                "mastered": accuracy >= 0.80 and attempts >= 3,
                "status": "✅ Mastered" if (accuracy >= 0.80 and attempts >= 3) 
                          else ("⚠️ In Progress" if accuracy >= 0.70 
                          else "❌ Weak")
            }
            
            if not (accuracy >= 0.80 and attempts >= 3):
                all_difficulties_mastered = False
        
        # ===== CHECK 2: BLOOM'S LEVEL MASTERY =====
        # Only check Bloom levels that the chapter actually teaches
        bloom_mastery = {}
        all_bloom_levels_mastered = True
        
        # Get the Bloom levels that were actually covered in this session
        covered_bloom_levels = [
            level for level in session.bloom_levels_completed.keys()
            if session.bloom_levels_completed[level].get("attempts", 0) > 0 or
               session.bloom_levels_completed[level].get("status") != "locked"
        ]
        
        # If no Bloom levels were covered, that's okay (chapter might not require them)
        if not covered_bloom_levels:
            all_bloom_levels_mastered = True
        else:
            # Check only the Bloom levels that are in the chapter
            for level in covered_bloom_levels:
                level_stats = session.bloom_levels_completed.get(level, {
                    "status": "not_started",
                    "accuracy": 0.0,
                    "attempts": 0
                })
                accuracy = level_stats.get("accuracy", 0.0) if isinstance(level_stats, dict) else 0.0
                attempts = level_stats.get("attempts", 0) if isinstance(level_stats, dict) else 0
                
                bloom_mastery[level] = {
                    "accuracy": accuracy,
                    "attempts": attempts,
                    "mastered": accuracy >= 0.80 and attempts >= 2,
                    "status": "✅ Mastered" if (accuracy >= 0.80 and attempts >= 2)
                              else ("⚠️ In Progress" if accuracy >= 0.70
                              else "❌ Weak")
                }
                
                if not (accuracy >= 0.80 and attempts >= 2):
                    all_bloom_levels_mastered = False
        
        # ===== CHECK 3: CONCEPT MASTERY =====
        concept_mastery = {}
        all_concepts_mastered = True
        
        accuracy_by_concept = session.accuracy_by_concept or {}
        for concept, stats in accuracy_by_concept.items():
            # Skip difficulty trackers
            if concept.startswith("difficulty_"):
                continue
            
            accuracy = stats.get("accuracy", 0.0) if isinstance(stats, dict) else 0.0
            attempts = stats.get("total", 0) if isinstance(stats, dict) else 0
            
            concept_mastery[concept] = {
                "accuracy": accuracy,
                "attempts": attempts,
                "mastered": accuracy >= 0.80,
                "status": "✅ Mastered" if accuracy >= 0.80
                          else ("⚠️ In Progress" if accuracy >= 0.70
                          else "❌ Weak")
            }
            
            if not (accuracy >= 0.80):
                all_concepts_mastered = False
        
        # ===== CHECK 4: MISCONCEPTIONS =====
        problem_misconceptions = []
        misconceptions = session.misconceptions_detected or {}
        has_problems = False
        
        for misconception_type, count in misconceptions.items():
            if isinstance(count, dict):
                count = count.get("encounter_count", 0)
            if count >= 2:
                has_problems = True
                problem_misconceptions.append({
                    "type": misconception_type,
                    "count": count
                })
        
        # ===== DETERMINE COMPLETION =====
        is_complete = (
            all_difficulties_mastered and
            all_bloom_levels_mastered and
            all_concepts_mastered and
            not has_problems
        )
        
        return {
            "success": True,
            "is_complete": is_complete,
            "completion_analysis": {
                "difficulty_mastery": difficulty_mastery,
                "bloom_mastery": bloom_mastery,
                "concept_mastery": concept_mastery,
                "problem_misconceptions": problem_misconceptions
            },
            "session_summary": {
                "questions_answered": session.total_questions_attempted,
                "accuracy_overall": round(session.overall_accuracy * 100, 1),
                "concepts_mastered": session.concepts_mastered or [],
                "concepts_in_progress": [
                    c for c in session.concepts_covered 
                    if c not in (session.concepts_mastered or [])
                ],
                "time_spent_minutes": self._calculate_duration_minutes(session)
            },
            "next_recommendation": (
                "COMPLETE" if is_complete
                else "CONTINUE"
            )
        }
