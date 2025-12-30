"""Break Point Tracker - Identifies and tracks points where students struggle significantly.

Responsibilities:
1. Record break points (where student accuracy drops below threshold)
2. Track misconceptions per session
3. Provide remediation data
4. Calculate break point severity
5. Generate intervention recommendations
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from database import SessionLocal, PracticeSession, get_practice_session, update_practice_session


class BreakPointTracker:
    """Tracks break points and misconceptions in student learning."""
    
    # Break point threshold (accuracy below 70%)
    BREAK_POINT_THRESHOLD = 0.70
    
    # Critical threshold (accuracy below 50%)
    CRITICAL_THRESHOLD = 0.50
    
    def __init__(self):
        """Initialize the tracker."""
        pass
    
    # ========================================================================
    # BREAK POINT RECORDING
    # ========================================================================
    
    def record_break_point(
        self,
        session_id: int,
        concept: str,
        bloom_level: str,
        accuracy: float,
        questions_attempted: int,
        questions_correct: int
    ) -> Optional[Dict[str, Any]]:
        """
        Record a break point when student struggles on a concept.
        
        A break point is recorded when:
        - Accuracy < 70% for a concept at a Bloom level
        - At least 3 questions answered
        
        Args:
            session_id: ID of the practice session
            concept: Name of the concept
            bloom_level: Current Bloom level
            accuracy: Accuracy percentage (0-1)
            questions_attempted: Number of questions attempted
            questions_correct: Number of correct answers
        
        Returns:
            Dictionary with break point info or None
        """
        # Check if this qualifies as a break point
        if accuracy >= self.BREAK_POINT_THRESHOLD or questions_attempted < 3:
            return None  # Not a break point
        
        session = get_practice_session(session_id)
        if not session:
            return None
        
        # Create break point record
        break_point = {
            "concept": concept,
            "bloom_level": bloom_level,
            "accuracy": round(accuracy, 3),
            "timestamp": datetime.utcnow().isoformat(),
            "questions_attempted": questions_attempted,
            "questions_correct": questions_correct,
            "severity": self._calculate_severity(accuracy),
            "remediation_priority": self._get_remediation_priority(accuracy)
        }
        
        # Get existing break points
        break_points = session.break_points or []
        
        # Check if this concept/level combination already exists
        existing_idx = None
        for i, bp in enumerate(break_points):
            if bp["concept"] == concept and bp["bloom_level"] == bloom_level:
                existing_idx = i
                break
        
        if existing_idx is not None:
            # Update existing break point
            break_points[existing_idx] = break_point
        else:
            # Add new break point
            break_points.append(break_point)
        
        # Update session
        update_practice_session(session_id, {
            "break_points": break_points
        })
        
        return break_point
    
    # ========================================================================
    # MISCONCEPTION TRACKING
    # ========================================================================
    
    def record_misconception(
        self,
        session_id: int,
        misconception_type: str,
        concept: str,
        bloom_level: str,
        details: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Record a misconception when detected during answer checking.
        
        Args:
            session_id: ID of the practice session
            misconception_type: Type of misconception (e.g., "place_value_confusion")
            concept: Related concept
            bloom_level: Current Bloom level
            details: Additional details about the misconception
        
        Returns:
            Dictionary with misconception info
        """
        session = get_practice_session(session_id)
        if not session:
            return None
        
        # Get or initialize misconceptions dict
        misconceptions = session.misconceptions_detected or {}
        
        # Create unique key for this misconception
        key = misconception_type
        
        # Increment count
        if key not in misconceptions:
            misconceptions[key] = {
                "count": 0,
                "concept": concept,
                "bloom_levels": [],
                "first_detected": datetime.utcnow().isoformat(),
                "last_detected": None,
                "details": details
            }
        
        # Update the record
        misconceptions[key]["count"] += 1
        misconceptions[key]["last_detected"] = datetime.utcnow().isoformat()
        
        if bloom_level not in misconceptions[key]["bloom_levels"]:
            misconceptions[key]["bloom_levels"].append(bloom_level)
        
        # Save updates
        update_practice_session(session_id, {
            "misconceptions_detected": misconceptions
        })
        
        return misconceptions[key]
    
    # ========================================================================
    # BREAK POINT QUERIES
    # ========================================================================
    
    def get_all_break_points(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Get all break points recorded in a session.
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            List of break point records
        """
        session = get_practice_session(session_id)
        if not session:
            return []
        
        return session.break_points or []
    
    def get_critical_break_points(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Get only critical break points (accuracy < 50%).
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            List of critical break points
        """
        all_break_points = self.get_all_break_points(session_id)
        
        return [
            bp for bp in all_break_points
            if bp.get("accuracy", 0) < self.CRITICAL_THRESHOLD
        ]
    
    def get_break_points_by_concept(self, session_id: int, concept: str) -> List[Dict[str, Any]]:
        """
        Get break points for a specific concept.
        
        Args:
            session_id: ID of the practice session
            concept: Name of the concept
        
        Returns:
            List of break points for the concept
        """
        all_break_points = self.get_all_break_points(session_id)
        
        return [
            bp for bp in all_break_points
            if bp.get("concept") == concept
        ]
    
    def get_misconceptions(self, session_id: int) -> Dict[str, Dict[str, Any]]:
        """
        Get all misconceptions detected in a session.
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            Dictionary of misconceptions
        """
        session = get_practice_session(session_id)
        if not session:
            return {}
        
        return session.misconceptions_detected or {}
    
    def get_most_frequent_misconceptions(
        self,
        session_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get the most frequently occurring misconceptions.
        
        Args:
            session_id: ID of the practice session
            limit: Maximum number to return
        
        Returns:
            List of most frequent misconceptions
        """
        misconceptions = self.get_misconceptions(session_id)
        
        # Convert to list and sort by count
        misconception_list = [
            {
                "type": k,
                "count": v.get("count", 0),
                "concept": v.get("concept"),
                "bloom_levels": v.get("bloom_levels", [])
            }
            for k, v in misconceptions.items()
        ]
        
        # Sort by count (descending)
        misconception_list.sort(key=lambda x: x["count"], reverse=True)
        
        return misconception_list[:limit]
    
    # ========================================================================
    # REMEDIATION RECOMMENDATIONS
    # ========================================================================
    
    def get_remediation_plan(self, session_id: int) -> Dict[str, Any]:
        """
        Generate a remediation plan based on break points and misconceptions.
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            Dictionary with remediation recommendations
        """
        break_points = self.get_all_break_points(session_id)
        critical_bp = self.get_critical_break_points(session_id)
        misconceptions = self.get_most_frequent_misconceptions(session_id)
        
        # Identify priority areas
        critical_concepts = list(set(bp["concept"] for bp in critical_bp))
        all_break_concepts = list(set(bp["concept"] for bp in break_points))
        
        return {
            "total_break_points": len(break_points),
            "critical_break_points": len(critical_bp),
            "critical_concepts": critical_concepts,
            "all_struggle_concepts": all_break_concepts,
            "frequent_misconceptions": misconceptions,
            "remediation_priority": self._prioritize_remediation(
                critical_bp, misconceptions
            ),
            "recommendations": self._generate_remediation_recommendations(
                critical_concepts, misconceptions
            )
        }
    
    def get_intervention_target_concepts(self, session_id: int) -> List[str]:
        """
        Get list of concepts that need intervention (based on break points).
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            List of concept names that need intervention
        """
        critical_bp = self.get_critical_break_points(session_id)
        concepts = list(set(bp["concept"] for bp in critical_bp))
        
        return sorted(concepts)
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _calculate_severity(self, accuracy: float) -> str:
        """
        Calculate the severity of a break point.
        
        Returns: "critical", "high", "medium", or "low"
        """
        if accuracy < 0.30:
            return "critical"
        elif accuracy < 0.50:
            return "high"
        elif accuracy < 0.60:
            return "medium"
        else:
            return "low"
    
    def _get_remediation_priority(self, accuracy: float) -> int:
        """
        Get the priority level for remediation (1=highest, 4=lowest).
        
        Returns: 1, 2, 3, or 4
        """
        if accuracy < 0.30:
            return 1  # Immediate attention
        elif accuracy < 0.50:
            return 2  # High priority
        elif accuracy < 0.60:
            return 3  # Medium priority
        else:
            return 4  # Lower priority
    
    def _prioritize_remediation(
        self,
        critical_bp: List[Dict[str, Any]],
        misconceptions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Prioritize remediation based on severity and frequency.
        
        Returns:
            List of prioritized remediation targets
        """
        priorities = []
        
        # Add critical break points
        for bp in critical_bp:
            priorities.append({
                "type": "break_point",
                "concept": bp["concept"],
                "bloom_level": bp["bloom_level"],
                "accuracy": bp["accuracy"],
                "severity": bp["severity"],
                "priority": bp["remediation_priority"]
            })
        
        # Add frequent misconceptions
        for misconception in misconceptions[:3]:
            priorities.append({
                "type": "misconception",
                "name": misconception["type"],
                "concept": misconception["concept"],
                "frequency": misconception["count"],
                "priority": min(misconception["count"], 3)  # Cap at 3
            })
        
        # Sort by priority
        priorities.sort(key=lambda x: x.get("priority", 4))
        
        return priorities
    
    def _generate_remediation_recommendations(
        self,
        critical_concepts: List[str],
        misconceptions: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate human-readable remediation recommendations.
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Concept-based recommendations
        if critical_concepts:
            concepts_str = ", ".join(critical_concepts)
            recommendations.append(
                f"🎯 Priority: Review and practice '{concepts_str}' - students are struggling here."
            )
        
        # Misconception-based recommendations
        if misconceptions:
            for misconception in misconceptions[:2]:
                recommendations.append(
                    f"⚠️  Common misconception: '{misconception['type']}' "
                    f"({misconception['count']} occurrences). "
                    f"Provide targeted explanation."
                )
        
        # General recommendations
        if len(critical_concepts) > 0:
            recommendations.append(
                f"📚 Suggest diagnostic assessment to identify root causes."
            )
        
        return recommendations
    
    def has_critical_issues(self, session_id: int) -> bool:
        """
        Check if session has critical break points or misconceptions.
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            True if critical issues found
        """
        critical_bp = self.get_critical_break_points(session_id)
        return len(critical_bp) > 0
    
    def get_break_point_summary(self, session_id: int) -> Dict[str, Any]:
        """
        Get a summary of break points and misconceptions.
        
        Args:
            session_id: ID of the practice session
        
        Returns:
            Summary dictionary
        """
        all_bp = self.get_all_break_points(session_id)
        critical_bp = self.get_critical_break_points(session_id)
        misconceptions = self.get_misconceptions(session_id)
        
        return {
            "total_break_points": len(all_bp),
            "critical_break_points": len(critical_bp),
            "unique_misconceptions": len(misconceptions),
            "has_critical_issues": self.has_critical_issues(session_id),
            "affected_concepts": len(set(bp["concept"] for bp in all_bp)),
            "affected_bloom_levels": len(set(bp["bloom_level"] for bp in all_bp))
        }
