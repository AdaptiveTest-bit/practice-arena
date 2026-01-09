"""
Adaptive Engine - Core intelligence for personalized learning sequencing
Determines next question based on student profile, Bloom's levels, and misconceptions
"""

from typing import List, Optional, Tuple, Dict
from enum import Enum
from api.models.quiz import Question
from api.models.cognitive_levels import BloomLevel
from models.student_profile import StudentProfile, PerformanceStatus, LearningPhase
from api.models.distractor import MisconceptionType
import random


class SequencingStrategy(str, Enum):
    """Question sequencing approaches"""
    BLOOM_PROGRESSION = "bloom_progression"          # REMEMBER → UNDERSTAND → APPLY → ...
    SPIRAL_REVIEW = "spiral_review"                  # Mix revisit + new
    REMEDIAL = "remedial"                            # Focus on misconceptions
    CHALLENGE = "challenge"                          # Push advanced students
    BALANCED = "balanced"                            # Mix all strategies


class AdaptiveEngine:
    """
    Intelligent question sequencing engine
    
    Adapts to student's learning profile:
    - Bloom's cognitive level progression
    - Misconception detection and remediation
    - Difficulty adjustment
    - Optimal challenge zone (slightly above current ability)
    """
    
    def __init__(self):
        self.sequencing_strategy = SequencingStrategy.BALANCED
        self.min_attempts_before_advance = 2
        self.mastery_threshold = 80.0  # accuracy % for level mastery
        self.spiral_review_ratio = 0.2  # 20% revisit questions
        self.challenge_ratio = 0.15  # 15% challenge questions for advanced
    
    def select_next_bloom_level(
        self,
        student: StudentProfile,
        chapter: str
    ) -> BloomLevel:
        """
        Intelligently select the next Bloom's level
        
        Logic:
        1. If struggling in current level (< mastery), stay in level
        2. If mastered current level, advance to next
        3. If no progress yet, start at REMEMBER
        """
        if chapter not in student.chapter_progress:
            return BloomLevel.REMEMBER
        
        ch_progress = student.chapter_progress[chapter]
        current_level_prog = ch_progress.bloom_progress.get(student.current_bloom_level)
        
        # If no progress yet in this level, keep trying
        if not current_level_prog or current_level_prog.questions_attempted == 0:
            return student.current_bloom_level
        
        # If mastered, advance to next
        if current_level_prog.mastery:
            next_level = self._get_next_bloom_level(student.current_bloom_level)
            if next_level:
                return next_level
        
        # If struggling, stay in current level
        if current_level_prog.accuracy < 50.0:
            return student.current_bloom_level
        
        # If developing but not mastered yet, need more practice
        if current_level_prog.accuracy < self.mastery_threshold:
            return student.current_bloom_level
        
        return student.current_bloom_level
    
    def select_next_chapter(
        self,
        student: StudentProfile,
        available_chapters: List[str]
    ) -> str:
        """
        Select the next chapter to study
        
        Priority order:
        1. Continue current chapter if not completed
        2. Detect and remediate misconceptions across chapters
        3. Review chapters with < 80% accuracy
        4. Advance to new chapters for advanced students
        """
        # If no current chapter or student is advanced, pick strategically
        if not student.current_chapter or student.performance_status == PerformanceStatus.ADVANCED:
            # Find chapter with lowest accuracy
            if student.chapter_progress:
                weakest_chapter = min(
                    student.chapter_progress.items(),
                    key=lambda x: x[1].accuracy
                )[0]
                if weakest_chapter in available_chapters:
                    return weakest_chapter
            
            # Otherwise pick first available
            return available_chapters[0] if available_chapters else "default"
        
        # Continue current chapter if available
        if student.current_chapter in available_chapters:
            return student.current_chapter
        
        # Otherwise move to next
        return available_chapters[0] if available_chapters else "default"
    
    def filter_questions_by_bloom_level(
        self,
        questions: List[Question],
        target_bloom_level: BloomLevel
    ) -> List[Question]:
        """Filter questions matching target Bloom's level"""
        return [
            q for q in questions
            if q.bloom_info and q.bloom_info.bloom_level == target_bloom_level
        ]
    
    def select_question(
        self,
        student: StudentProfile,
        questions: List[Question],
        chapter: str
    ) -> Optional[Question]:
        """
        Select optimal next question for student
        
        Considers:
        1. Bloom's level (adaptive progression)
        2. Misconception remediation (if > 2 detections)
        3. Difficulty adjustment
        4. Spiral review (occasional revisit of previous topics)
        5. Challenge zone (optimal difficulty)
        """
        if not questions:
            return None
        
        # Determine target Bloom's level
        target_bloom = self.select_next_bloom_level(student, chapter)
        
        # Filter by Bloom's level
        bloom_filtered = self.filter_questions_by_bloom_level(questions, target_bloom)
        
        if not bloom_filtered:
            # Fallback: use any available question
            bloom_filtered = questions
        
        # Apply misconception remediation if needed
        question = self._apply_misconception_strategy(student, bloom_filtered)
        
        if not question:
            # Fallback to random from filtered
            question = random.choice(bloom_filtered)
        
        return question
    
    def _normalize_misconception_type(self, raw: object) -> Optional[MisconceptionType]:
        """Normalize raw misconception identifiers into `MisconceptionType`.

        Bank/YAML content sometimes emits slightly different strings (case, spaces, hyphens).
        This helper keeps the adaptive selection path resilient.
        """
        if raw is None:
            return None
        if isinstance(raw, MisconceptionType):
            return raw

        s = str(raw).strip()
        if not s:
            return None

        # 1) Direct enum value match
        try:
            return MisconceptionType(s)
        except Exception:
            pass

        # 2) Common normalizations
        normalized = (
            s.upper()
            .replace(" ", "_")
            .replace("-", "_")
        )
        try:
            return MisconceptionType(normalized)
        except Exception:
            return None

    def _extract_misconception_types(self, q: Question) -> set[MisconceptionType]:
        """Best-effort extraction of misconception types a question can diagnose.

        Supports multiple historical/question-bank shapes:
        - Bank payload: q.misconception_info OR q.payload["misconception_info"] OR q.meta["misconception_info"]
        - Legacy: q.distractor_info.misconception_map (dict)
        - DistractorSet-style: q.distractor_info.distractors[*].misconception_type

        Returns a set of MisconceptionType values.
        """
        types: set[MisconceptionType] = set()

        def _ingest_mis_info(mis_info_obj: object) -> None:
            if not isinstance(mis_info_obj, list):
                return
            for entry in mis_info_obj:
                # Expected modern shape: {"type": "...", "value": "..."}
                if isinstance(entry, dict):
                    raw = entry.get("type") or entry.get("misconception_type")
                    mt = self._normalize_misconception_type(raw)
                    if mt:
                        types.add(mt)
                    continue

                # Older/badged shapes: allow raw strings/enums in list
                mt = self._normalize_misconception_type(entry)
                if mt:
                    types.add(mt)

        # 1) Bank payload format (preferred)
        _ingest_mis_info(getattr(q, "misconception_info", None))

        # Sometimes the Question is a wrapper around a stored payload dict
        payload = getattr(q, "payload", None)
        if isinstance(payload, dict):
            _ingest_mis_info(payload.get("misconception_info"))

        meta = getattr(q, "meta", None)
        if isinstance(meta, dict):
            _ingest_mis_info(meta.get("misconception_info"))

        # 2) Legacy distraction map: {MisconceptionType: value} or {"TYPE": "value"}
        d_info = getattr(q, "distractor_info", None)
        m_map = getattr(d_info, "misconception_map", None) if d_info else None
        if isinstance(m_map, dict):
            for k in m_map.keys():
                mt = self._normalize_misconception_type(k)
                if mt:
                    types.add(mt)

        # 3) DistractorSet-style list
        distractors = getattr(d_info, "distractors", None) if d_info else None
        if isinstance(distractors, list):
            for d in distractors:
                raw = getattr(d, "misconception_type", None)
                mt = self._normalize_misconception_type(raw)
                if mt:
                    types.add(mt)

        return types

    def _apply_misconception_strategy(
        self,
        student: StudentProfile,
        questions: List[Question]
    ) -> Optional[Question]:
        """
        Target questions that address student's detected misconceptions.

        Only triggers remediation if the misconception was detected with meaningful frequency
        (historical intent: "if > 2 detections").
        """
        top_misconceptions = student.get_top_misconceptions(limit=3)

        if not top_misconceptions:
            return None  # No misconceptions to remediate

        # Expected shape: List[Tuple[MisconceptionType, int]]
        primary_type_raw, primary_count = top_misconceptions[0]

        # Gate remediation: don't overfit to a single accidental wrong click
        try:
            count = int(primary_count)
        except Exception:
            count = 0

        if count <= 2:
            return None

        primary_type = self._normalize_misconception_type(primary_type_raw)
        if not primary_type:
            return None

        matching_questions = [
            q for q in questions
            if primary_type in self._extract_misconception_types(q)
        ]

        if matching_questions:
            return random.choice(matching_questions)

        return None
    
    def adjust_difficulty(
        self,
        student: StudentProfile,
        questions: List[Question]
    ) -> List[Question]:
        """
        Adjust question difficulty based on student performance
        
        Difficulty adjustment factor:
        - 0.5: Much easier (struggling students)
        - 0.75: Easier (developing students)
        - 1.0: Normal (proficient students)
        - 1.25: Slightly harder (advanced students)
        - 1.5: Much harder (elite students)
        """
        adjustment = student.difficulty_adjustment
        
        if adjustment == 1.0:
            return questions  # No adjustment needed
        
        # Sort by difficulty (trap_info contains difficulty level)
        def get_difficulty(q):
            return q.trap_info.difficulty if q.trap_info else 3
        
        sorted_questions = sorted(questions, key=get_difficulty)
        
        if adjustment < 1.0:
            # Easier: select from lower difficulty questions
            cutoff_idx = int(len(sorted_questions) * min(adjustment, 0.7))
            return sorted_questions[:max(cutoff_idx, 1)]
        else:
            # Harder: select from higher difficulty questions
            cutoff_idx = int(len(sorted_questions) * (1.0 / adjustment))
            return sorted_questions[cutoff_idx:]
    
    def generate_learning_recommendation(
        self,
        student: StudentProfile
    ) -> Dict:
        """
        Generate actionable learning recommendation based on profile
        
        Returns dict with:
        - next_chapter: Recommended chapter
        - next_bloom_level: Target Bloom's level
        - focus_area: Specific topic to focus on
        - misconception_to_address: Top misconception
        - difficulty_adjustment: Recommended difficulty
        - hint_level: Recommended hint level
        """
        # Get top misconceptions
        top_miscon = student.get_top_misconceptions(limit=1)
        
        # Recommended difficulty
        suggested_difficulty = student.recommend_difficulty_adjustment()
        student.difficulty_adjustment = suggested_difficulty
        
        # Recommended hint level based on performance
        if student.performance_status == PerformanceStatus.STRUGGLING:
            suggested_hint = 3  # Full solution hints
        elif student.performance_status == PerformanceStatus.DEVELOPING:
            suggested_hint = 2  # Detailed hints
        elif student.performance_status == PerformanceStatus.PROFICIENT:
            suggested_hint = 1  # Basic hints
        else:
            suggested_hint = 0  # No hints for advanced
        
        student.hint_level = suggested_hint
        
        recommendation = {
            "student_id": student.student_id,
            "performance_status": student.performance_status.value,
            "learning_phase": student.learning_phase.value,
            "overall_accuracy": round(student.overall_accuracy, 2),
            "recommended_chapter": student.current_chapter or "Chapter 1",
            "recommended_bloom_level": student.current_bloom_level.value,
            "focus_area": student.chapter_progress.get(
                student.current_chapter or "Chapter 1",
                {}
            ).topics_covered[-1] if student.current_chapter else "Foundations",
            "top_misconception": top_miscon[0][0].value if top_miscon else None,
            "misconception_frequency": top_miscon[0][1] if top_miscon else 0,
            "recommended_difficulty": round(suggested_difficulty, 2),
            "recommended_hint_level": suggested_hint,
            "questions_until_mastery": 5 - (student.chapter_progress.get(
                student.current_chapter or "Chapter 1", ChapterProgress("temp")
            ).bloom_progress.get(student.current_bloom_level, BloomLevelProgress(student.current_bloom_level)).questions_attempted % 5)
        }
        
        return recommendation
    
    def get_next_recommendation(self, student: StudentProfile):
        """Backward-compatible recommendation API.

        Some callers (e.g. `domain.adaptive_learning.service.AdaptiveLearningService`) expect
        `AdaptiveEngine.get_next_recommendation(student)` to exist and return an object with:
        - recommendation_type
        - reasoning
        - recommended_difficulty
        - recommended_bloom_level

        The modern flow in this repo primarily uses `generate_learning_recommendation`, but we
        keep this shim to avoid runtime AttributeError.
        """

        class _Rec:
            def __init__(
                self,
                *,
                recommendation_type: str,
                reasoning: str,
                recommended_difficulty: float,
                recommended_bloom_level: BloomLevel,
            ):
                self.recommendation_type = recommendation_type
                self.reasoning = reasoning
                self.recommended_difficulty = recommended_difficulty
                self.recommended_bloom_level = recommended_bloom_level

            def to_dict(self) -> dict:
                return {
                    "recommendation_type": self.recommendation_type,
                    "reasoning": self.reasoning,
                    "recommended_difficulty": self.recommended_difficulty,
                    "recommended_bloom_level": getattr(self.recommended_bloom_level, "value", str(self.recommended_bloom_level)),
                }

        chapter = getattr(student, "current_chapter", None) or "Chapter 1"
        target_bloom = getattr(student, "current_bloom_level", None)
        try:
            if not isinstance(target_bloom, BloomLevel):
                target_bloom = BloomLevel.REMEMBER
        except Exception:
            target_bloom = BloomLevel.REMEMBER

        try:
            next_bloom = self.select_next_bloom_level(student, chapter)
        except Exception:
            next_bloom = target_bloom or BloomLevel.REMEMBER

        recommended_difficulty = getattr(student, "difficulty_adjustment", 1.0) or 1.0

        return _Rec(
            recommendation_type="adaptive",
            reasoning=f"Next Bloom level: {getattr(next_bloom, 'value', str(next_bloom))}",
            recommended_difficulty=float(recommended_difficulty),
            recommended_bloom_level=next_bloom,
        )

    def _get_next_bloom_level(self, current_level: BloomLevel) -> Optional[BloomLevel]:
        """Get the next Bloom's level in progression"""
        bloom_order = [
            BloomLevel.REMEMBER,
            BloomLevel.UNDERSTAND,
            BloomLevel.APPLY,
            BloomLevel.ANALYZE,
            BloomLevel.EVALUATE,
            BloomLevel.CREATE,
        ]
        
        try:
            current_idx = bloom_order.index(current_level)
            if current_idx < len(bloom_order) - 1:
                return bloom_order[current_idx + 1]
        except ValueError:
            pass
        
        return None


# Import at end to avoid circular imports
from models.student_profile import ChapterProgress, BloomLevelProgress
