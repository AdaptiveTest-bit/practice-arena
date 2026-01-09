"""Misconception Detection & Analysis Service

Analyzes student responses to detect misconceptions and provides remediation guidance.
"""

from typing import Optional, Dict, List, Tuple
from api.models.quiz import Question
from api.models.distractor import MisconceptionType, DistractorInfo
from api.models.student_progress import StudentProgress, AttemptResult
from api.models.cognitive_levels import BloomLevel
import uuid
from datetime import datetime


class MisconceptionDetector:
    """Detects misconceptions from student responses."""

    @staticmethod
    def _normalize_option_value(v: object) -> str:
        """Normalize option strings for robust matching.

        We want misconception tagging to be resilient to formatting differences
        (extra spaces, non-breaking spaces, etc.) without changing semantics.
        """
        if v is None:
            return ""
        s = str(v)
        # normalize whitespace (including NBSP) and trim
        s = s.replace("\u00a0", " ")
        return " ".join(s.split()).strip()

    @staticmethod
    def _normalize_misconception_type(raw: object) -> Optional[MisconceptionType]:
        """Best-effort normalization into MisconceptionType."""
        if raw is None:
            return None
        if isinstance(raw, MisconceptionType):
            return raw

        s = str(raw).strip()
        if not s:
            return None

        # Direct enum match
        try:
            return MisconceptionType(s)
        except Exception:
            pass

        # Common normalizations
        s2 = s.lower().replace(" ", "_").replace("-", "_")
        try:
            return MisconceptionType(s2)
        except Exception:
            return None

    @staticmethod
    def detect_misconception(
        question: Question,
        selected_option_index: int
    ) -> Optional[MisconceptionType]:
        """Detect misconception from selected distractor.

        Supports multiple historical/question-bank shapes:
        1) Preferred (DB/bank payload): question.payload/meta["misconception_info"] or question.misconception_info
           where entries look like {"type": "...", "value": "..."}
        2) DistractorSet: question.distractor_info.distractors[*] with (value, misconception_type)
        3) Legacy: question.distractor_info.misconception_map (dict)

        Returns:
            MisconceptionType if wrong answer, else None.
        """
        # If correct, no misconception
        if selected_option_index == question.correct_option_index:
            return None

        # Validate selection
        if not question.options or not (0 <= selected_option_index < len(question.options)):
            return None

        selected_value = MisconceptionDetector._normalize_option_value(
            question.options[selected_option_index]
        )
        if not selected_value:
            return None

        # --- 1) Bank payload format (preferred) ---
        def _scan_misconception_info(mis_info_obj: object) -> Optional[MisconceptionType]:
            if not isinstance(mis_info_obj, list):
                return None
            for entry in mis_info_obj:
                # Expected: {"type": "...", "value": "..."}
                if isinstance(entry, dict):
                    v = MisconceptionDetector._normalize_option_value(entry.get("value"))
                    if v and v == selected_value:
                        raw_t = entry.get("type") or entry.get("misconception_type")
                        return MisconceptionDetector._normalize_misconception_type(raw_t)
            return None

        # Direct attribute (some generators/wrappers)
        mt = _scan_misconception_info(getattr(question, "misconception_info", None))
        if mt:
            return mt

        payload = getattr(question, "payload", None)
        if isinstance(payload, dict):
            mt = _scan_misconception_info(payload.get("misconception_info"))
            if mt:
                return mt

        meta = getattr(question, "meta", None)
        if isinstance(meta, dict):
            mt = _scan_misconception_info(meta.get("misconception_info"))
            if mt:
                return mt

        # --- 2) DistractorSet-style list ---
        d_info = getattr(question, "distractor_info", None)
        distractors = getattr(d_info, "distractors", None) if d_info else None
        if isinstance(distractors, list):
            for d in distractors:
                dv = MisconceptionDetector._normalize_option_value(getattr(d, "value", None))
                if dv and dv == selected_value:
                    return MisconceptionDetector._normalize_misconception_type(
                        getattr(d, "misconception_type", None)
                    )

        # --- 3) Legacy misconception_map ---
        misconception_map = getattr(d_info, "misconception_map", None) if d_info else None
        if isinstance(misconception_map, dict):
            for misconception_type, distractor_value in misconception_map.items():
                dv = MisconceptionDetector._normalize_option_value(distractor_value)
                if dv and dv == selected_value:
                    return MisconceptionDetector._normalize_misconception_type(misconception_type)

        return None

    @staticmethod
    def get_misconception_explanation(
        question: Question,
        misconception: MisconceptionType
    ) -> Dict[str, str]:
        """Get pedagogical explanation for a misconception.

        Preference order:
        1) If the question has `distractor_info.distractors[]`, return that distractor's
           `why_wrong` + `teaching_point` (most specific, teacher-quality).
        2) Else if `trap_info` matches, return trap-level explanation.
        3) Else return a generic explanation.
        """
        # 1) Distractor-level pedagogy (best)
        d_info = getattr(question, "distractor_info", None)
        distractors = getattr(d_info, "distractors", None) if d_info else None
        if isinstance(distractors, list):
            for d in distractors:
                mt = MisconceptionDetector._normalize_misconception_type(
                    getattr(d, "misconception_type", None)
                )
                if mt == misconception:
                    why_wrong = getattr(d, "why_wrong", None)
                    teaching_point = getattr(d, "teaching_point", None)
                    return {
                        "type": misconception.value,
                        "explanation": teaching_point or (
                            f"This choice reflects: {misconception.value.replace('_', ' ')}"
                        ),
                        "why_effective": why_wrong or "This is a common error pattern.",
                        "how_to_avoid": "Slow down, identify the key idea, and check each step against the concept.",
                    }

        # 2) Trap-level explanation (fallback)
        if getattr(question, "trap_info", None) and getattr(question.trap_info, "misconception_type", None) == misconception:
            return {
                "type": misconception.value,
                "explanation": question.trap_info.description,
                "why_effective": question.trap_info.why_effective,
                "how_to_avoid": question.trap_info.how_to_avoid,
                "difficulty": question.trap_info.difficulty
            }

        # 3) Generic fallback
        return {
            "type": misconception.value,
            "explanation": f"Misconception detected: {misconception.value.replace('_', ' ').title()}",
            "why_effective": "This is a common error pattern",
            "how_to_avoid": "Review the concept carefully"
        }


class RemediationRecommender:
    """Recommends remediation for identified misconceptions."""
    
    def __init__(self, misconception_index: Optional[Dict] = None):
        """
        Initialize with optional misconception index.
        
        Args:
            misconception_index: Optional index mapping misconceptions to questions
        """
        self.misconception_index = misconception_index or self._build_default_index()
    
    def get_remediation_sequence(
        self,
        student: StudentProgress,
        misconception: MisconceptionType,
        num_questions: int = 3
    ) -> Dict:
        """
        Create a remediation sequence for a misconception.
        
        Args:
            student: The student's current progress
            misconception: The misconception to remediate
            num_questions: How many practice questions (default 3)
            
        Returns:
            Dict with sequence details and recommendations
        """
        misconception_info = self.misconception_index.get(misconception.value, {})
        
        return {
            "misconception": misconception.value,
            "difficulty_adjustment": 0.75,  # Easier questions for remediation
            "num_questions": num_questions,
            "bloom_level_recommended": BloomLevel.UNDERSTAND.value,
            "teaching_strategy": self._get_teaching_strategy(misconception),
            "success_criteria": {
                "min_accuracy": 0.8,  # Need 80% correct to exit remediation
                "min_attempts": 3,  # At least 3 questions
                "confidence": 0.85  # High confidence required
            }
        }
    
    def _get_teaching_strategy(self, misconception: MisconceptionType) -> str:
        """Get teaching strategy for misconception."""
        strategies = {
            "opposite_confusion": "Use visual aids showing opposite pairs clearly",
            "universal_vs_specific": "Distinguish between always true vs sometimes true",
            "operation_direction": "Explicitly check direction of operation (÷ vs ×)",
            "reference_point_error": "Identify correct reference point before calculating",
            "incomplete_reasoning": "Ensure all steps are completed, don't skip steps",
            "arithmetic_error": "Double-check calculations with alternative method",
            "operation_selection": "Review what operation the problem is asking for",
            "formula_misapplication": "Verify correct formula before applying it",
            "formula_confusion": "Compare similar formulas side-by-side",
            "unit_error": "Always include units and check conversions",
            "logical_disconnect": "Trace through logic step-by-step",
            "constraint_violation": "List all constraints before solving",
            "pattern_misidentification": "Look at pattern carefully from multiple angles",
            "similar_concept_error": "Distinguish between similar but different concepts"
        }
        
        return strategies.get(
            misconception.value,
            "Review the concept and practice similar problems"
        )
    
    def _build_default_index(self) -> Dict:
        """Build default misconception index."""
        return {}


class PerformanceAnalyzer:
    """Analyzes student performance patterns."""
    
    @staticmethod
    def analyze_learning_curve(
        student: StudentProgress,
        last_n_attempts: int = 10
    ) -> Dict:
        """
        Analyze learning curve from recent attempts.
        
        Args:
            student: Student profile
            last_n_attempts: How many recent attempts to analyze
            
        Returns:
            Dict with trend analysis
        """
        # Get recent mastery data
        recent_accuracy = student.overall_percentage
        total_attempts = student.total_attempts
        
        # Difficulty trend
        difficulty_mastery = student.difficulty_mastery
        difficulty_trend = {
            level: {
                "accuracy": mastery.percentage_correct,
                "mastered": mastery.mastered,
                "attempts": mastery.attempts
            }
            for level, mastery in difficulty_mastery.items()
        }
        
        # Bloom's trend
        bloom_trend = {
            level: {
                "accuracy": mastery.percentage_correct,
                "mastered": mastery.mastered,
                "attempts": mastery.attempts
            }
            for level, mastery in student.bloom_mastery.items()
        }
        
        return {
            "recent_accuracy": recent_accuracy,
            "total_attempts": total_attempts,
            "trend": "improving" if recent_accuracy > 60 else "needs_support",
            "difficulty_progression": difficulty_trend,
            "bloom_progression": bloom_trend,
            "recommendation": PerformanceAnalyzer._get_recommendation(student)
        }
    
    @staticmethod
    def _get_recommendation(student: StudentProgress) -> str:
        """Get recommendation based on performance."""
        if student.should_advance_difficulty():
            return "Ready to advance to next difficulty level"
        elif student.should_retreat_difficulty():
            return "Consider reducing difficulty to rebuild confidence"
        elif student.get_problem_misconceptions():
            return f"Address {len(student.get_problem_misconceptions())} misconceptions before advancing"
        else:
            return "Continue current trajectory"


class MisconceptionReport:
    """Generates detailed misconception reports."""
    
    @staticmethod
    def generate_student_report(student: StudentProgress) -> Dict:
        """Generate comprehensive misconception report for student."""
        analyzer = PerformanceAnalyzer()
        
        problem_misconceptions = student.get_problem_misconceptions()
        misconception_details = []
        
        for misc in problem_misconceptions:
            misc_key = misc if isinstance(misc, str) else misc.value
            encounter = student.misconceptions.get(misc_key)
            if encounter:
                misconception_details.append({
                    "type": misc_key,
                    "encounters": encounter.encounter_count,
                    "first_seen": encounter.first_encountered.isoformat() if encounter.first_encountered else None,
                    "last_seen": encounter.last_encountered.isoformat() if encounter.last_encountered else None,
                    "remediation_needed": True,
                    "teaching_strategy": RemediationRecommender()._get_teaching_strategy(misc)
                })
        
        return {
            "student_id": student.student_id,
            "generated_at": datetime.utcnow().isoformat(),
            "overall_performance": {
                "accuracy": student.overall_percentage,
                "total_attempts": student.total_attempts,
                "status": "proficient" if student.overall_percentage >= 70 else "developing"
            },
            "learning_curve": analyzer.analyze_learning_curve(student),
            "misconceptions": misconception_details,
            "recommendations": [
                analyzer._get_recommendation(student)
            ]
        }
    
    @staticmethod
    def generate_class_report(students: List[StudentProgress]) -> Dict:
        """Generate class-wide misconception report."""
        if not students:
            return {"error": "No students provided"}
        
        # Aggregate misconceptions
        misconception_stats = {}
        for student in students:
            for misc_key, encounter in student.misconceptions.items():
                if misc_key not in misconception_stats:
                    misconception_stats[misc_key] = {
                        "type": misc_key,
                        "total_encounters": 0,
                        "affected_students": set()
                    }
                misconception_stats[misc_key]["total_encounters"] += encounter.encounter_count
                misconception_stats[misc_key]["affected_students"].add(student.student_id)
        
        # Convert sets to counts
        for misc_data in misconception_stats.values():
            misc_data["affected_students"] = len(misc_data["affected_students"])
        
        # Sort by frequency
        sorted_misconceptions = sorted(
            misconception_stats.values(),
            key=lambda x: x["total_encounters"],
            reverse=True
        )
        
        return {
            "class_size": len(students),
            "generated_at": datetime.utcnow().isoformat(),
            "average_accuracy": sum(s.overall_percentage for s in students) / len(students) if students else 0,
            "top_misconceptions": sorted_misconceptions[:10],
            "class_recommendations": [
                f"Focus on remediation: {sorted_misconceptions[0]['type']}" if sorted_misconceptions else "No major misconceptions"
            ]
        }
