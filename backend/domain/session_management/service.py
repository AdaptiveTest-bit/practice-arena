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
from config.chapter_config import CHAPTER_CONFIG
from api.models.quiz import ChapterEnum
from domain.session_management.student.repository import get_repository, ORMStudentRepository
from domain.adaptive_learning.misconceptions.detector import MisconceptionDetector

# NOTE: Avoid direct SQLAlchemy Core imports in this file to reduce editor import
# resolution issues in minimal environments. We use ORM query patterns instead.

from db.models.session import QuizSession
from db.models.question_bank import QuestionBankItem
from domain.content_generation.service import QuestionBankService
from core.database import SessionLocal
from domain.adaptive_learning.scheduler.leitner import SchedulerService

import uuid as _uuid
from datetime import timedelta

from db.models.concepts import StudentBreakpoint, StudentConceptState
from db.models.events import LearningEvent

# New adaptive selection layer
from domain.adaptation import get_adaptive_selector, AdaptiveQuestionSelector

logger = get_logger(__name__)


class SessionAdapter:
    """Bridges frontend session-based API to backend question generation and tracking."""

    # Feature flag: Use new adaptive selector for these chapters
    ADAPTIVE_CHAPTERS = {"factors_multiples"}

    def __init__(self):
        """Initialize with existing backend services."""
        self.repository: ORMStudentRepository = get_repository()
        self.misconception_detector: MisconceptionDetector = MisconceptionDetector()

        # Runtime question bank (Option A)
        self.question_bank = QuestionBankService()

        # Scheduler (Leitner + breakpoints)
        self.scheduler = SchedulerService()
        
        # New adaptive selectors (cached per chapter)
        self._adaptive_selectors: Dict[str, AdaptiveQuestionSelector] = {}

        # Concept roadmaps (derived from YAML banks). Cached in-memory by chapter key.
        self._concept_roadmaps: Dict[str, List[str]] = {}

        # Default concept roadmap for factors_multiples (Chapter 9 / legacy Class 5 Chapter 5)
        # Used for the MVP sequencing rule: wrong -> same concept, right -> next concept.
        self.chapter5_concept_sequence: List[str] = self.get_concept_roadmap("factors_multiples")

        # IMPORTANT (Week-1 fix): do not keep per-session authoritative state in-memory.
        # In-memory state breaks with multi-worker deployments.
        self._sessions: Dict[str, Dict[str, Any]] = {}

    # ============================================================================
    # CONCEPT ROADMAPS (K-12 ready)
    # ============================================================================

    def get_concept_roadmap(self, chapter_key: str) -> List[str]:
        """Return a stable ordered concept roadmap for a chapter.

        Roadmaps are derived from the YAML bank where available and cached per-process.

        Args:
            chapter_key: Canonical chapter key (e.g. "class5_chapter5").

        Returns:
            Ordered unique concept labels.
        """
        ch = self._normalize_chapter_key(chapter_key)
        if ch in self._concept_roadmaps:
            return self._concept_roadmaps[ch]

        roadmap = self._load_concept_sequence_from_yaml(ch)
        self._concept_roadmaps[ch] = roadmap
        return roadmap

    def _load_concept_sequence_from_yaml(self, chapter_key: str) -> List[str]:
        """Load (and de-dupe) concepts from a chapter YAML bank.

        Tries multiple naming conventions:
            1. backend/data/<chapter_key>_lean.yaml (current standard)
            2. backend/data/<chapter_key>_bank.yaml (legacy)
            3. backend/data/<chapter_key>_rich.yaml (fallback)
        """
        try:
            from pathlib import Path
            import yaml

            data_dir = Path(__file__).resolve().parent.parent / "data"
            
            # Try multiple naming conventions
            candidates = [
                data_dir / f"{chapter_key}_lean.yaml",
                data_dir / f"{chapter_key}_bank.yaml",
                data_dir / f"{chapter_key}_rich.yaml",
            ]
            
            bank_path = None
            for candidate in candidates:
                if candidate.exists():
                    bank_path = candidate
                    break
            
            if bank_path is None:
                logger.warning(f"No YAML bank found for chapter='{chapter_key}' (tried: {[c.name for c in candidates]})")
                return []

            with bank_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            # Handle both nested (rich) and flat (lean) YAML structures
            questions_root = (data or {}).get("questions") or []
            
            seen: set[str] = set()
            ordered: List[str] = []

            # Lean format: questions is a flat list
            if isinstance(questions_root, list):
                for q in questions_root:
                    if not isinstance(q, dict):
                        continue
                    concept = str(q.get("concept") or "").strip()
                    if concept and concept not in seen:
                        seen.add(concept)
                        ordered.append(concept)
                return ordered

            # Rich/nested format: category -> difficulty -> list
            if isinstance(questions_root, dict):
                for _category, category_data in questions_root.items():
                    if not isinstance(category_data, dict):
                        continue
                    for _difficulty, buckets in category_data.items():
                        if not isinstance(buckets, list):
                            continue
                        for q in buckets:
                            if not isinstance(q, dict):
                                continue
                            concept = str(q.get("concept") or "").strip()
                            if concept and concept not in seen:
                                seen.add(concept)
                                ordered.append(concept)
            
            return ordered
        except Exception as e:
            logger.warning(f"Failed to load concept roadmap from YAML for chapter='{chapter_key}': {e}")
            return []

    # Backwards compatible wrappers (keep existing callers working)
    def _load_class5_chapter5_concept_sequence(self) -> List[str]:
        # Note: class5_chapter5 normalizes to factors_multiples
        roadmap = self.get_concept_roadmap("factors_multiples")
        return roadmap or self._fallback_chapter5_concept_sequence()

    def _fallback_chapter5_concept_sequence(self) -> List[str]:
        """Hardcoded fallback if YAML is missing/unreadable."""
        return [
            "Meaning of factors",
            "Counting factors",
            "Meaning of multiples",
            "Prime number definition",
            "Composite number definition",
            "HCF (basic)",
            "LCM (basic)",
        ]

    # ============================================================================
    # ADAPTIVE SELECTION (NEW)
    # ============================================================================

    def _get_adaptive_selector(self, chapter_key: str, db_session=None) -> AdaptiveQuestionSelector:
        """Get or create an adaptive selector for a chapter.
        
        Args:
            chapter_key: Chapter key (e.g., "factors_multiples")
            db_session: Database session for template queries (required for template-based generation)
            
        Returns:
            AdaptiveQuestionSelector instance
        """
        normalized = self._normalize_chapter_key(chapter_key)
        
        # Always create new selector with db_session for template-based generation
        if db_session is not None:
            return get_adaptive_selector(normalized, db_session)
        
        # Fallback to cached (will fail on generate without db_session)
        if normalized not in self._adaptive_selectors:
            self._adaptive_selectors[normalized] = get_adaptive_selector(normalized)
        return self._adaptive_selectors[normalized]

    def _should_use_adaptive(self, chapter_key: str) -> bool:
        """Check if this chapter should use new adaptive selection."""
        normalized = self._normalize_chapter_key(chapter_key)
        return normalized in self.ADAPTIVE_CHAPTERS

    def _get_adaptive_question(
        self,
        session_id: str,
        student_id: str,
        chapter: str,
        attempted: int,
    ) -> Dict[str, Any]:
        """Generate a question using the new adaptive selection system.
        
        Uses pure template-based architecture - all questions come from template database.
        
        Args:
            session_id: Current session ID
            student_id: Student identifier
            chapter: Chapter key (e.g., "factors_multiples")
            attempted: Number of questions attempted so far
            
        Returns:
            Question response dict for frontend
        """
        # Get db_session for template-based generation
        with SessionLocal() as db:
            selector = self._get_adaptive_selector(chapter, db_session=db)
            
            # Select optimal question based on mastery state
            question, metadata = selector.select_question(student_id=student_id)
        
        # Generate unique question ID for this session
        question_id = f"adaptive_{session_id}_{attempted}"
        
        # Store question in cache for answer validation
        self._cache_question(question_id, question, metadata)
        
        # Extract info from selection metadata
        selection = metadata.get("selection", {})
        concept_id = selection.get("concept_id", "unknown")
        difficulty = selection.get("difficulty", 2)
        bloom_level = selection.get("bloom_level", "APPLY")
        
        # Build frontend response
        response = {
            "questionId": question_id,
            "topic": question.topic,
            "subtopic": selection.get("concept_key"),
            "chapterId": self._get_chapter_id(chapter),
            "difficulty": self._convert_difficulty_to_enum(difficulty),
            "question": question.question_text,
            "questionContext": None,
            "dataRepresentation": question.data_representation,
            "options": self._format_options_with_misconceptions(
                question.options, 
                question.distractor_info,
                question.misconception_info
            ),
            "optionLayout": self._build_option_layout(),
            "estimatedTime": 90,
            "misconceptionTag": None,
            "logicalTrapPresent": bool(question.logical_trap),
            "bloomLevel": str(bloom_level).lower(),
            "hintStrategy": [],
            "renderingHints": {},
            "richNarrative": getattr(question, 'rich_narrative', None),
            # Phase 1: richHtmlContent moved to answer response only (bandwidth reduction)
            "richHtmlContent": None,
            "visualHints": None,
            # Phase 1: correctAnswerId removed from question payload (security fix)
            # "correctAnswerId": f"option_{question.correct_option_index}",  # REMOVED
            "attemptNumber": attempted + 1,
            # New: Include adaptive metadata for frontend
            "adaptive": {
                "conceptId": concept_id,
                "reason": selection.get("reason", ""),
                "mastery": metadata.get("mastery", {}),
                "progress": metadata.get("progress", {}),
            },
        }
        
        # Record SERVED event
        try:
            now = datetime.utcnow()
            with SessionLocal() as db:
                db.add(
                    LearningEvent(
                        id=str(_uuid.uuid4()),
                        student_id=str(student_id),
                        session_id=str(session_id),
                        event_type="SERVED",
                        timestamp=now,
                        subject="math",
                        chapter_key=str(chapter),
                        concept_id=str(concept_id),
                        bloom_level=str(bloom_level).upper() if bloom_level else None,
                        difficulty=str(difficulty),
                        served_question_id=str(question_id),
                        payload={
                            "adaptive": True,
                            "selection_reason": selection.get("reason", ""),
                            "strategy": selection.get("strategy", ""),
                        },
                    )
                )
                db.commit()
        except Exception as e:
            logger.warning(f"Failed to write SERVED learning event: {e}")
        
        logger.info(
            f"🎯 Adaptive question served: session={session_id[:8]}..., "
            f"concept={selection.get('concept_key')}, difficulty={difficulty}"
        )
        
        return response

    def _cache_question(self, question_id: str, question, metadata: dict):
        """Cache question for answer validation."""
        # Use a simple in-memory cache (could be Redis in production)
        if not hasattr(self, '_question_cache'):
            self._question_cache = {}
        self._question_cache[question_id] = {
            "question": question,
            "metadata": metadata,
            "cached_at": datetime.utcnow(),
        }

    def _get_cached_question(self, question_id: str) -> Optional[dict]:
        """Retrieve cached question."""
        if not hasattr(self, '_question_cache'):
            return None
        return self._question_cache.get(question_id)

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
                chapters: List<Chapter>
            }
        """
        # Create session ID
        session_id = str(uuid.uuid4())

        # Chapter handling:
        # - Accept strategy key strings directly (e.g., "large_numbers", "factors_multiples", "class5_chapter5")
        # - If caller passes a numeric chapter id ("9"), map via ChapterEnum -> strategy value
        selected_chapter = "large_numbers"
        if chapter:
            raw = str(chapter).strip()
            if raw.isdigit():
                try:
                    selected_chapter = ChapterEnum(int(raw)).value
                except Exception:
                    logger.warning(f"Invalid chapter id '{chapter}', using default 'large_numbers'")
                    selected_chapter = "large_numbers"
            else:
                selected_chapter = raw

        selected_chapter = self._normalize_chapter_key(selected_chapter)

        # Persist session in DB (authoritative)
        with SessionLocal() as db:
            db.add(
                QuizSession(
                    id=session_id,
                    student_id=str(student_id),
                    grade_level=int(grade_level),
                    mode=str(mode),
                    chapter=selected_chapter,
                    attempted_count=0,
                    correct_count=0,
                    current_streak=0,
                    chapter_transitions=[],
                    is_active=True,
                )
            )
            # Event: SESSION_STARTED
            db.add(
                LearningEvent(
                    id=str(_uuid.uuid4()),
                    student_id=str(student_id),
                    session_id=str(session_id),
                    event_type="SESSION_STARTED",
                    timestamp=datetime.utcnow(),
                    subject="math",
                    chapter_key=str(selected_chapter),
                    concept_id=None,
                    bloom_level=None,
                    difficulty=None,
                    served_question_id=None,
                    payload={"mode": str(mode), "grade_level": int(grade_level)},
                )
            )
            db.commit()

        # Week-1: do NOT populate legacy in-memory session store.
        # The session is DB-backed and should work across workers.

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
        # DB-first path (authoritative)
        try:
            with SessionLocal() as db:
                db_sess = db.get(QuizSession, session_id)
                if db_sess:
                    student = self.repository.get_student(str(db_sess.student_id))
                    return {
                        "sessionId": session_id,
                        "mode": str(db_sess.mode or "practice"),
                        "classLevel": int(db_sess.grade_level or 6),
                        "uiConfig": self._get_ui_config(int(db_sess.grade_level or 6), str(db_sess.mode or "practice")),
                        "student": self._format_student_profile(student),
                        "chapters": self._get_available_chapters(),
                    }
        except Exception as e:
            logger.warning(f"DB-backed get_session_state failed: {e}; falling back to legacy state")

        # Week-1: remove legacy in-memory fallback.
        raise ValueError(f"Session {session_id} not found")

    # ============================================================================
    # QUESTION MANAGEMENT
    # ============================================================================
    
    def get_next_question(self, session_id: str) -> Dict[str, Any]:
        """
        Get next question in the quiz sequence.
        
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
        # Load session from DB (authoritative)
        with SessionLocal() as db:
            db_sess = db.get(QuizSession, session_id)

        if not db_sess:
            raise ValueError(f"Session {session_id} not found")

        student_id = db_sess.student_id
        grade_level = db_sess.grade_level
        attempted = int(db_sess.attempted_count or 0)

        # Normalize chapter key
        chapter = self._normalize_chapter_key(db_sess.chapter)
        
        # =========================================================================
        # NEW: Use adaptive selection for supported chapters
        # =========================================================================
        if self._should_use_adaptive(chapter):
            # Pure template-based architecture - no fallback to legacy
            return self._get_adaptive_question(
                session_id=session_id,
                student_id=student_id,
                chapter=chapter,
                attempted=attempted,
            )
        
        # =========================================================================
        # LEGACY: Bank-based question selection (for non-adaptive chapters)
        # =========================================================================

        # NOTE: Chapter routing removed in Phase 3 cleanup.
        # MVP has single chapter; multi-chapter routing can be re-added when needed.

        # Difficulty heuristic (reuse existing simple mapping)
        base_difficulty = max(1, (grade_level - 2) // 2)
        correct = int(db_sess.correct_count or 0)
        accuracy = (correct / attempted * 100) if attempted > 0 else 50

        if accuracy > 70 and attempted > 3:
            difficulty = min(5, base_difficulty + 1)
        elif accuracy < 30 and attempted > 3:
            difficulty = max(1, base_difficulty - 1)
        else:
            difficulty = base_difficulty

        # Bank currently has difficulty buckets 1..3 (from YAML). Clamp to avoid misses.
        try:
            difficulty = max(1, min(3, int(difficulty)))
        except Exception:
            difficulty = 1

        # Pick (concept, bloom_level) based on configured chapter curriculum.
        # For MVP, we pick deterministically to avoid importing randomness into tests.
        try:
            # Default bloom: prefer UNDERSTAND (matches the imported bank well)
            bloom_level = "UNDERSTAND"

            # If this chapter is part of CHAPTER_CONFIG, use its bloom_distribution
            try:
                chapter_id = self._get_chapter_id(chapter)
                cfg = CHAPTER_CONFIG.get(int(chapter_id))
                bloom_dist = dict(cfg.get("bloom_distribution") or {}) if cfg else {}
                if bloom_dist:
                    ordered = sorted(bloom_dist.items(), key=lambda kv: (-kv[1], kv[0]))
                    bloom_level = ordered[attempted % len(ordered)][0].upper()
            except Exception:
                pass

            # Concept: pick from actual bank concepts for this chapter
            with SessionLocal() as db:
                concepts = (
                    db.query(QuestionBankItem.concept)
                    .filter(
                        QuestionBankItem.chapter == str(chapter),
                        QuestionBankItem.difficulty == int(difficulty),
                    )
                    .distinct()
                    .order_by(QuestionBankItem.concept.asc())
                    .all()
                )
            concept = concepts[attempted % len(concepts)][0] if concepts else "general"
        except Exception:
            concept = "general"
            bloom_level = "UNDERSTAND"

        # Serve from bank (Option A). Fallback to dynamic generation if bank is empty.
        try:
            # Concept selection is scheduler-driven (curated concept_id)
            scheduled = self.scheduler.pick_next_concept(
                student_id=str(student_id),
                chapter_key=str(chapter),
            )
            concept = scheduled.concept_id

            # Try exact (chapter, concept_id, difficulty, bloom) first.
            try_blooms = [str(bloom_level or "").strip().upper()] if bloom_level else []
            for b in ("UNDERSTAND", "REMEMBER", "APPLY", "ANALYZE", "EVALUATE"):
                if b not in try_blooms:
                    try_blooms.append(b)

            # Try multiple difficulties (target first, then fallback to 1, 2, 3)
            try_difficulties = [int(difficulty)]
            for d in (1, 2, 3):
                if d not in try_difficulties:
                    try_difficulties.append(d)

            last_err = None
            payload = None
            for d in try_difficulties:
                for b in try_blooms:
                    try:
                        payload = self.question_bank.get_next_unseen(
                            session_id=session_id,
                            student_id=str(student_id),
                            chapter=str(chapter),
                            concept=str(concept),
                            difficulty=d,
                            bloom_level=b,
                        )
                        difficulty = d
                        bloom_level = b
                        break
                    except Exception as e:
                        last_err = e
                        payload = None
                if payload:
                    break

            if payload is None:
                raise last_err or ValueError("No bank question available")

            # Convert payload to frontend response structure
            question_id = payload.get("served_id")
            options = payload.get("options", [])

            response = {
                "questionId": question_id,
                "topic": payload.get("topic") or str(chapter),
                "subtopic": None,
                "chapterId": self._get_chapter_id(chapter),
                "difficulty": self._convert_difficulty_to_enum(int(difficulty)),
                "question": payload.get("question_text") or "",
                "questionContext": payload.get("question_context"),
                "dataRepresentation": payload.get("rich_html_content") or payload.get("data_representation"),
                "options": self._format_options_with_misconceptions(options, None, None),
                "optionLayout": self._build_option_layout(),
                "estimatedTime": 60,
                "misconceptionTag": None,
                "logicalTrapPresent": False,
                "bloomLevel": str(bloom_level).lower(),
                "hintStrategy": [],
                "renderingHints": {},
                "richNarrative": payload.get("rich_narrative"),
                # Phase 1: richHtmlContent moved to answer response only
                "richHtmlContent": None,
                "visualHints": payload.get("visual_hints"),
                # Phase 1: correctAnswerId removed from question payload (security)
                # "correctAnswerId": None,  # REMOVED
                "attemptNumber": attempted,
            }

            # Event: SERVED
            try:
                now = datetime.utcnow()
                with SessionLocal() as db:
                    db.add(
                        LearningEvent(
                            id=str(_uuid.uuid4()),
                            student_id=str(student_id),
                            session_id=str(session_id),
                            event_type="SERVED",
                            timestamp=now,
                            subject="math",
                            chapter_key=str(chapter),
                            concept_id=str(concept),
                            bloom_level=str(bloom_level).upper() if bloom_level else None,
                            difficulty=str(difficulty),
                            served_question_id=str(question_id),
                            payload={
                                "bank_item_id": payload.get("bank_item_id"),
                                "topic": payload.get("topic") or str(chapter),
                            },
                        )
                    )
                    db.commit()
            except Exception as e:
                logger.warning(f"Failed to write SERVED learning event: {e}")

            return response
        except Exception as e:
            logger.warning(f"Question bank serve failed ({e}); falling back to dynamic generation")

        # Week-1: disable legacy dynamic fallback (multi-worker unsafe + not needed for MVP).
        raise ValueError(
            "Question bank is empty or lookup failed. "
            "Populate `question_bank_items` for this chapter/concept/difficulty."
        )

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
        # DB-first path (Option A): question_id is actually served_id.
        # This removes the multi-worker correctness bug caused by in-memory caches.
        db_session_row = None
        try:
            with SessionLocal() as db:
                db_session_row = db.get(QuizSession, session_id)
        except Exception:
            db_session_row = None

        if db_session_row:
            student_id = str(db_session_row.student_id)
            chapter_key = self._normalize_chapter_key(str(db_session_row.chapter or ""))

            # Convert answer_id (string) to index
            try:
                selected_index = int(answer_id)
            except (ValueError, TypeError):
                selected_index = 0

            # =========================================================================
            # NEW: Handle adaptive questions
            # =========================================================================
            cached = self._get_cached_question(question_id)
            if cached and question_id.startswith("adaptive_"):
                # This was an adaptive question - handle it specially
                question = cached["question"]
                metadata = cached["metadata"]
                concept_id = metadata.get("selection", {}).get("concept_id", "")
                
                correct_index = question.correct_option_index
                is_correct = selected_index == correct_index
                
                # Update adaptive mastery tracker (no db_session needed for record_attempt)
                if self._should_use_adaptive(chapter_key) and concept_id:
                    try:
                        # Note: record_attempt doesn't need template generation, so no db_session
                        selector = self._get_adaptive_selector(chapter_key)
                        mastery_result = selector.record_attempt(
                            student_id=student_id,
                            concept_id=concept_id,
                            is_correct=is_correct,
                            time_spent=time_spent,
                        )
                        logger.info(
                            f"📊 Adaptive mastery updated: {concept_id} -> {mastery_result['mastery_level']}"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to update adaptive mastery: {e}")
                
                # Build response for adaptive question
                return self._build_adaptive_answer_response(
                    session_id=session_id,
                    student_id=student_id,
                    question=question,
                    metadata=metadata,
                    selected_index=selected_index,
                    correct_index=correct_index,
                    is_correct=is_correct,
                    time_spent=time_spent,
                    db_session_row=db_session_row,
                )

            # =========================================================================
            # LEGACY: Bank-based question handling
            # =========================================================================
            served, item = self.question_bank.get_served_with_item(served_id=question_id)
            payload = dict(item.payload or {})
            correct_index = self.question_bank.get_correct_index_from_payload(payload=payload)
            is_correct = selected_index == correct_index

            # Persist served answer
            try:
                self.question_bank.mark_answered(
                    served_id=question_id,
                    selected_index=selected_index,
                    is_correct=is_correct,
                )
            except Exception as e:
                logger.warning(f"Failed to persist served answer: {e}")

            # --- Leitner + breakpoints update (concept-level) ---
            concept_id = str(item.concept or payload.get("concept_id") or "").strip() or None
            chapter_key = self._normalize_chapter_key(str(item.chapter or db_session_row.chapter or ""))

            if concept_id:
                try:
                    now = datetime.utcnow()
                    with SessionLocal() as db:
                        state = db.get(StudentConceptState, {"student_id": student_id, "concept_id": concept_id})
                        if not state:
                            state = StudentConceptState(
                                student_id=student_id,
                                concept_id=concept_id,
                                leitner_box=1,
                                due_at=now,
                                last_seen_at=None,
                                attempts=0,
                                correct=0,
                                last_bloom_served=None,
                                updated_at=now,
                            )
                            db.add(state)
                            db.flush()

                        # Update counters
                        state.attempts = int(state.attempts or 0) + 1
                        state.correct = int(state.correct or 0) + (1 if is_correct else 0)
                        state.last_seen_at = now
                        state.updated_at = now

                        # Update Leitner box
                        old_box = int(state.leitner_box or 1)
                        if is_correct:
                            new_box = min(5, old_box + 1)
                        else:
                            new_box = 1
                        state.leitner_box = new_box
                        state.due_at = self.scheduler.compute_next_due_at(leitner_box=new_box, now=now)

                        # Breakpoints (simple wrong-streak based)
                        bp = db.get(StudentBreakpoint, {"student_id": student_id, "concept_id": concept_id})
                        if not bp:
                            bp = StudentBreakpoint(
                                student_id=student_id,
                                concept_id=concept_id,
                                severity=1,
                                reason="LOW_ACCURACY",
                                wrong_streak=0,
                                active=True,
                                last_triggered_at=None,
                                updated_at=now,
                            )
                            db.add(bp)

                        if is_correct:
                            bp.wrong_streak = 0
                            # If they recovered, deactivate mild breakpoints
                            if int(bp.severity or 1) <= 2:
                                bp.active = False
                        else:
                            bp.wrong_streak = int(bp.wrong_streak or 0) + 1
                            bp.active = True
                            bp.last_triggered_at = now
                            bp.updated_at = now
                            # escalate severity at wrong streak thresholds
                            if bp.wrong_streak >= 4:
                                bp.severity = max(int(bp.severity or 1), 4)
                                bp.reason = "REPEATED_WRONG"
                            elif bp.wrong_streak >= 2:
                                bp.severity = max(int(bp.severity or 1), 3)
                                bp.reason = "REPEATED_WRONG"

                            # Force immediate review if breakpoint is active
                            if bp.active:
                                state.due_at = min(state.due_at, now)

                        # Detect misconception for wrong answers
                        misconception_detected = None
                        if not is_correct:
                            misconception_detected = self._detect_misconception_from_selection(
                                payload, selected_index, correct_index
                            )

                        # Write learning event (ANSWERED) with misconception tracking
                        event_payload = {
                            "selected_index": selected_index,
                            "correct_index": correct_index,
                            "is_correct": is_correct,
                            "time_spent": int(time_spent or 0),
                        }
                        # Add misconception data if wrong answer
                        if misconception_detected:
                            event_payload["misconception_type"] = misconception_detected.get("type")
                            event_payload["misconception_value"] = misconception_detected.get("value")
                            event_payload["why_wrong"] = misconception_detected.get("why_wrong")
                            event_payload["teaching_point"] = misconception_detected.get("teaching_point")

                        db.add(
                            LearningEvent(
                                id=str(_uuid.uuid4()),
                                student_id=student_id,
                                session_id=str(session_id),
                                event_type="ANSWERED",
                                timestamp=now,
                                subject="math",
                                chapter_key=chapter_key,
                                concept_id=concept_id,
                                bloom_level=str(payload.get("bloom_level") or "").strip() or None,
                                difficulty=str(item.difficulty) if item.difficulty is not None else None,
                                served_question_id=str(question_id),
                                payload=event_payload,
                            )
                        )

                        db.commit()
                except Exception as e:
                    logger.warning(f"Leitner/breakpoint update failed (concept_id={concept_id}): {e}")

            # Update session row counters (authoritative)
            previous_streak = int(db_session_row.current_streak or 0)
            current_streak = (previous_streak + 1) if is_correct else 0
            streak_milestone = current_streak if current_streak in [5, 10, 25, 50] else None

            attempted = int(db_session_row.attempted_count or 0) + 1
            correct = int(db_session_row.correct_count or 0) + (1 if is_correct else 0)

            try:
                with SessionLocal() as db:
                    sess_row = db.get(QuizSession, session_id)
                    if sess_row:
                        sess_row.attempted_count = attempted
                        sess_row.correct_count = correct
                        sess_row.current_streak = current_streak
                        db.commit()
            except Exception as e:
                logger.warning(f"Failed to update session counters: {e}")

            # Get student's current mastery (uses existing student repository)
            student = self.repository.get_student(student_id)
            previous_mastery = student.overall_percentage / 100 if student else 0

            mastery_delta = 0.1 if is_correct else -0.05
            current_mastery = min(1.0, max(0.0, previous_mastery + mastery_delta))

            # Minimal solution summary from payload
            options = payload.get("options") or []
            correct_value = None
            selected_value = None
            try:
                if isinstance(options, list) and 0 <= correct_index < len(options):
                    correct_value = options[correct_index]
                if isinstance(options, list) and 0 <= selected_index < len(options):
                    selected_value = options[selected_index]
            except Exception:
                correct_value = None
                selected_value = None

            # Convert index to letter (A, B, C, D)
            option_letter = chr(65 + correct_index)  # 0->A, 1->B, 2->C, 3->D
            selected_letter = chr(65 + selected_index)  # 0->A, 1->B, 2->C, 3->D

            # Build rich solution explanation
            solution_steps = payload.get("solution_steps") or []
            rich_narrative = payload.get("rich_narrative") or ""
            visual_hints = payload.get("visual_hints") or []
            concept = payload.get("concept") or item.concept or ""

            # Build comprehensive summary for wrong answers
            if is_correct:
                summary = f"✓ Correct! The answer is {option_letter}: {correct_value}"
            else:
                summary_parts = [
                    f"The correct answer is {option_letter}: {correct_value}",
                ]
                if selected_value:
                    summary_parts.append(f"You selected {selected_letter}: {selected_value}")
                if rich_narrative:
                    # Extract key insight from rich narrative
                    summary_parts.append(f"\n💡 {rich_narrative[:300]}{'...' if len(rich_narrative) > 300 else ''}")
                summary = "\n".join(summary_parts)

            # Build detailed explanation for wrong answers
            explanation = None
            misconception_for_response = None
            if not is_correct:
                # Detect misconception for response
                misconception_for_response = self._detect_misconception_from_selection(
                    payload, selected_index, correct_index
                )
                
                explanation_parts = []
                if concept:
                    explanation_parts.append(f"This question tests: {concept}")
                
                # Add misconception-specific feedback
                if misconception_for_response and misconception_for_response.get("type") != "UNKNOWN":
                    misc_type = misconception_for_response.get("type", "")
                    misc_name = misc_type.replace("_", " ").title()
                    explanation_parts.append(f"⚠️ Misconception detected: {misc_name}")
                    if misconception_for_response.get("teaching_point"):
                        explanation_parts.append(f"💡 {misconception_for_response.get('teaching_point')}")
                    elif misconception_for_response.get("why_wrong"):
                        explanation_parts.append(f"💡 {misconception_for_response.get('why_wrong')}")
                
                if solution_steps:
                    explanation_parts.append("Solution steps:")
                    for i, step in enumerate(solution_steps[:5], 1):
                        explanation_parts.append(f"  {i}. {step}")
                if visual_hints:
                    explanation_parts.append("Hints to remember:")
                    for hint in visual_hints[:3]:
                        explanation_parts.append(f"  • {hint}")
                explanation = "\n".join(explanation_parts) if explanation_parts else None

            return {
                "isCorrect": is_correct,
                "correctAnswerId": str(correct_index),
                "selectedAnswerId": answer_id,
                "feedback": {
                    "depthLevel": "detailed" if not is_correct else "minimal",
                    "showSolution": not is_correct,
                    "enableHints": True,
                    "showMisconception": False,
                    "explanation": explanation,  # Added detailed explanation
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
                    "steps": solution_steps,
                    "summary": summary,
                    "concept": concept,
                    "richNarrative": rich_narrative,
                    "visualHints": visual_hints,
                    # Phase 1: richHtmlContent returned in answer response (not question)
                    "richHtmlContent": payload.get("rich_html_content"),
                },
                "misconceptionDetected": {
                    "type": misconception_for_response.get("type"),
                    "name": misconception_for_response.get("type", "").replace("_", " ").title(),
                    "whyWrong": misconception_for_response.get("why_wrong"),
                    "teachingPoint": misconception_for_response.get("teaching_point"),
                    "selectedValue": misconception_for_response.get("value"),
                } if misconception_for_response else None,
                "advancedMisconceptionFeedback": self._get_advanced_misconception_feedback(
                    misconception_for_response.get("type", ""), None
                ) if misconception_for_response and misconception_for_response.get("type") != "UNKNOWN" else None,
                "logicalTrapTriggered": False,
                "trapDetails": {"id": "trap_1", "type": "logical", "explanation": ""},
                "attemptNumber": attempted,
            }

        # ---- Legacy fallback (in-memory cache) ----
        raise ValueError("Legacy in-memory session mode is disabled. Use DB-backed sessions.")

    def _build_adaptive_answer_response(
        self,
        session_id: str,
        student_id: str,
        question,
        metadata: dict,
        selected_index: int,
        correct_index: int,
        is_correct: bool,
        time_spent: int,
        db_session_row,
    ) -> Dict[str, Any]:
        """Build answer response for adaptive questions."""
        
        # Get chapter info
        chapter_key = self._normalize_chapter_key(str(db_session_row.chapter or ""))
        concept_id = metadata.get("selection", {}).get("concept_id", "")
        
        # Get FRESH progress from adaptive selector (after mastery was updated)
        # Note: get_mastery_tracker doesn't need template generation, so no db_session
        fresh_progress = {}
        fresh_mastery = {}
        if self._should_use_adaptive(chapter_key):
            try:
                selector = self._get_adaptive_selector(chapter_key)
                mastery_tracker = selector.get_mastery_tracker(student_id)
                # Answer response: include full concept lists for mastery panel update
                fresh_progress = selector._get_progress_summary(mastery_tracker, include_concept_lists=True)
                concept_mastery = mastery_tracker.get_mastery(concept_id)
                fresh_mastery = {
                    "current_level": concept_mastery.level.name,
                    "attempts": concept_mastery.total_attempts,
                    "accuracy": concept_mastery.accuracy,
                }
            except Exception as e:
                logger.warning(f"Failed to get fresh progress: {e}")
                fresh_progress = metadata.get("progress", {})
                fresh_mastery = metadata.get("mastery", {})
        else:
            fresh_progress = metadata.get("progress", {})
            fresh_mastery = metadata.get("mastery", {})
        
        # Update session counters
        previous_streak = int(db_session_row.current_streak or 0)
        current_streak = (previous_streak + 1) if is_correct else 0
        streak_milestone = current_streak if current_streak in [5, 10, 25, 50] else None
        
        attempted = int(db_session_row.attempted_count or 0) + 1
        correct_count = int(db_session_row.correct_count or 0) + (1 if is_correct else 0)
        
        try:
            with SessionLocal() as db:
                sess_row = db.get(QuizSession, session_id)
                if sess_row:
                    sess_row.attempted_count = attempted
                    sess_row.correct_count = correct_count
                    sess_row.current_streak = current_streak
                    db.commit()
        except Exception as e:
            logger.warning(f"Failed to update session counters: {e}")
        
        # Record learning event
        now = datetime.utcnow()
        try:
            misconception_detected = None
            if not is_correct and question.misconception_info:
                # Find misconception for selected option
                for mi in question.misconception_info:
                    if mi.get("option_index") == selected_index:
                        misconception_detected = mi
                        break
            
            event_payload = {
                "selected_index": selected_index,
                "correct_index": correct_index,
                "is_correct": is_correct,
                "time_spent": time_spent,
                "adaptive": True,
            }
            if misconception_detected:
                event_payload["misconception_type"] = misconception_detected.get("misconception_type")
                event_payload["why_wrong"] = misconception_detected.get("why_wrong")
                event_payload["teaching_point"] = misconception_detected.get("teaching_point")
            
            with SessionLocal() as db:
                db.add(
                    LearningEvent(
                        id=str(_uuid.uuid4()),
                        student_id=student_id,
                        session_id=session_id,
                        event_type="ANSWERED",
                        timestamp=now,
                        subject="math",
                        chapter_key=chapter_key,
                        concept_id=concept_id,
                        bloom_level=metadata.get("selection", {}).get("bloom_level"),
                        difficulty=str(metadata.get("selection", {}).get("difficulty", 2)),
                        served_question_id=session_id,  # Use session for adaptive
                        payload=event_payload,
                    )
                )
                db.commit()
        except Exception as e:
            logger.warning(f"Failed to write ANSWERED event: {e}")
        
        # Build response
        options = question.options or []
        correct_value = options[correct_index] if correct_index < len(options) else ""
        selected_value = options[selected_index] if selected_index < len(options) else ""
        option_letter = chr(65 + correct_index)
        selected_letter = chr(65 + selected_index)
        
        # Solution summary
        if is_correct:
            summary = f"✓ Correct! The answer is {option_letter}: {correct_value}"
        else:
            summary = f"The correct answer is {option_letter}: {correct_value}\nYou selected {selected_letter}: {selected_value}"
        
        # Build misconception feedback for wrong answers
        misconception_for_response = None
        if not is_correct and question.misconception_info:
            for mi in question.misconception_info:
                if mi.get("option_index") == selected_index:
                    misconception_for_response = {
                        "type": mi.get("misconception_type", "UNKNOWN"),
                        "why_wrong": mi.get("why_wrong"),
                        "teaching_point": mi.get("teaching_point"),
                        "value": selected_value,
                    }
                    break
        
        # Get updated mastery info - use fresh data
        current_mastery = fresh_mastery.get("accuracy", 0)
        
        return {
            "isCorrect": is_correct,
            "correctAnswerId": str(correct_index),
            "selectedAnswerId": str(selected_index),
            "feedback": {
                "depthLevel": "detailed" if not is_correct else "minimal",
                "showSolution": not is_correct,
                "enableHints": True,
                "showMisconception": misconception_for_response is not None,
                "explanation": misconception_for_response.get("teaching_point") if misconception_for_response else None,
            },
            "masteryScore": {
                "previous": current_mastery,
                "current": current_mastery + (0.1 if is_correct else -0.05),
                "delta": 0.1 if is_correct else -0.05,
            },
            "streakUpdate": {
                "current": current_streak,
                "previous": previous_streak,
                "milestone": streak_milestone,
            },
            "solution": {
                "steps": question.solution_steps or [],
                "summary": summary,
                "concept": concept_id,
                "richNarrative": getattr(question, 'rich_narrative', None),
                # Phase 1: richHtmlContent returned in answer response (not question)
                "richHtmlContent": getattr(question, 'rich_html_content', None),
                "visualHints": [],
            },
            "misconceptionDetected": {
                "type": misconception_for_response.get("type"),
                "name": misconception_for_response.get("type", "").replace("_", " ").title(),
                "whyWrong": misconception_for_response.get("why_wrong"),
                "teachingPoint": misconception_for_response.get("teaching_point"),
                "selectedValue": misconception_for_response.get("value"),
            } if misconception_for_response else None,
            "logicalTrapTriggered": False,
            "trapDetails": None,
            "attemptNumber": attempted,
            # NEW: Include adaptive progress for frontend
            "adaptive": {
                "conceptId": concept_id,
                "masteryLevel": fresh_mastery.get("current_level", "NOT_STARTED"),
                "progress": fresh_progress,
            },
        }

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
        # DB-first path: question_id is served_id for bank questions
        try:
            with SessionLocal() as db:
                db_sess = db.get(QuizSession, session_id)
        except Exception:
            db_sess = None

        if not db_sess:
            raise ValueError(f"Session {session_id} not found")

        # Check if this is an adaptive question (generated on-the-fly)
        is_adaptive = question_id.startswith("adaptive_")
        
        hints = []
        
        if is_adaptive:
            # For adaptive questions, use concept-based hints from the session's current question
            # Get hints from the last served learning event or use generic concept-based hints
            chapter = self._normalize_chapter_key(db_sess.chapter)
            
            # Generic hints for adaptive questions based on chapter
            if chapter == "factors_multiples":
                hints = [
                    {"content": "Remember: A factor divides the number exactly with no remainder.", "type": "conceptual"},
                    {"content": "Try listing factor pairs: start with 1 × n, then 2 × ?, etc.", "type": "process"},
                    {"content": "Check if the number is divisible by 2, 3, 5 first - these are common factors.", "type": "elimination"},
                ]
            elif chapter == "large_numbers":
                hints = [
                    {"content": "Compare numbers digit by digit, starting from the leftmost digit.", "type": "conceptual"},
                    {"content": "Count the number of digits first - more digits usually means larger.", "type": "process"},
                    {"content": "Use place value: lakhs, ten thousands, thousands, hundreds, tens, ones.", "type": "visual"},
                ]
            else:
                hints = [
                    {"content": "Try breaking down the problem into smaller parts.", "type": "conceptual"},
                    {"content": "Look for a pattern or relationship in the numbers.", "type": "visual"},
                    {"content": "Re-read the question and identify what is being asked.", "type": "process"},
                ]
        else:
            # Try to get hints from the question bank
            try:
                _, item = self.question_bank.get_served_with_item(served_id=question_id)
                payload = dict(item.payload or {})
                visual_hints = payload.get("visual_hints") or []

                # Normalize into list[str]
                if isinstance(visual_hints, str):
                    visual_hints = [visual_hints]
                if not isinstance(visual_hints, list):
                    visual_hints = []

                hints = [
                    {"content": str(h), "type": "reference"}
                    for h in visual_hints
                    if h is not None and str(h).strip()
                ]
            except Exception as e:
                logger.warning(f"Bank hint lookup failed: {e}")

        # Fallback generic hints if none found
        if not hints:
            hints = [
                {"content": "Try breaking down the problem into smaller parts.", "type": "conceptual"},
                {"content": "Look for a pattern or relationship in the numbers.", "type": "visual"},
                {"content": "Re-read the question and identify what is being asked.", "type": "process"},
            ]

        if hint_index >= len(hints):
            hint_index = len(hints) - 1

        hint = hints[hint_index]
        return {
            "hintContent": hint.get("content"),
            "hintType": hint.get("type", "conceptual"),
            "hintIndex": hint_index,
            "remainingHints": max(0, len(hints) - hint_index - 1),
            "maxHints": len(hints),
            "severity": hint_index + 1,
            "displayFormat": "text",
        }

        # ---- Legacy fallback (in-memory cache) ----
        raise ValueError("Legacy in-memory session mode is disabled. Use DB-backed sessions.")

    def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        End a session and return final results.

        Args:
            session_id: Session ID

        Returns:
            Session summary with statistics
        """
        # DB-first path
        try:
            with SessionLocal() as db:
                db_sess = db.get(QuizSession, session_id)
                if db_sess:
                    attempted = int(db_sess.attempted_count or 0)
                    correct = int(db_sess.correct_count or 0)
                    accuracy = (correct / attempted * 100) if attempted > 0 else 0

                    # mark ended
                    db_sess.ended_at = datetime.utcnow()
                    db_sess.is_active = False

                    # Event: SESSION_ENDED
                    db.add(
                        LearningEvent(
                            id=str(_uuid.uuid4()),
                            student_id=str(db_sess.student_id),
                            session_id=str(session_id),
                            event_type="SESSION_ENDED",
                            timestamp=datetime.utcnow(),
                            subject="math",
                            chapter_key=str(db_sess.chapter),
                            concept_id=None,
                            bloom_level=None,
                            difficulty=None,
                            served_question_id=None,
                            payload={
                                "attempted": attempted,
                                "correct": correct,
                                "accuracy": accuracy,
                            },
                        )
                    )
                    db.commit()

                    return {
                        "sessionId": session_id,
                        "finalScore": correct,
                        "totalQuestions": attempted,
                        "correctAnswers": correct,
                        "accuracy": accuracy,
                        "streak": int(db_sess.current_streak or 0),
                        "masteryGains": {"overall": correct * 0.1},
                        "completedAt": datetime.utcnow().isoformat(),
                        "recommendations": self._generate_recommendations(
                            str(db_sess.chapter),
                            accuracy,
                        ),
                    }
        except Exception as e:
            logger.warning(f"DB-backed end_session failed: {e}")

        # Week-1: remove legacy fallback.
        raise ValueError(f"Session {session_id} not found")

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
        """Get list of available chapters.

        MVP: only expose Factors & Multiples.
        """
        return [
            {"id": "factors_multiples", "name": "Factors & Multiples", "icon": "🎯"},
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
    
    def _detect_misconception_from_selection(
        self, 
        payload: Dict[str, Any], 
        selected_index: int, 
        correct_index: int
    ) -> Optional[Dict[str, str]]:
        """Detect which misconception was triggered by the student's wrong answer.

        Preference order:
        1) Index/ID-based match against payload["misconception_info"] using option_index/option_id (schema v4+)
        2) Fallback string match against payload["misconception_info"][].value (legacy)
        3) Fallback distractor_info.distractors (older format)
        """
        # If correct, no misconception
        if selected_index == correct_index:
            return None

        options = payload.get("options", [])
        if not options or selected_index >= len(options):
            return None

        def _norm(v: object) -> str:
            s = "" if v is None else str(v)
            return " ".join(s.replace("\u00a0", " ").split()).strip()

        selected_value = _norm(options[selected_index])

        misconception_info = payload.get("misconception_info")
        option_ids = payload.get("option_ids")
        selected_option_id = None
        if isinstance(option_ids, list) and selected_index < len(option_ids):
            selected_option_id = str(option_ids[selected_index])

        # --- 1) Index/ID-based misconception_info (preferred) ---
        if misconception_info and isinstance(misconception_info, list):
            for info in misconception_info:
                if not isinstance(info, dict):
                    continue

                idx = info.get("option_index")
                try:
                    if idx is not None and int(idx) == int(selected_index):
                        return {
                            "type": info.get("type", "UNKNOWN"),
                            "value": selected_value,
                            "why_wrong": info.get("why_wrong", ""),
                            "teaching_point": info.get("teaching_point", ""),
                            "description": info.get("description", ""),
                        }
                except Exception:
                    pass

                if selected_option_id and str(info.get("option_id") or "") == selected_option_id:
                    return {
                        "type": info.get("type", "UNKNOWN"),
                        "value": selected_value,
                        "why_wrong": info.get("why_wrong", ""),
                        "teaching_point": info.get("teaching_point", ""),
                        "description": info.get("description", ""),
                    }

        # --- 2) Legacy value match for misconception_info ---
        if misconception_info and isinstance(misconception_info, list):
            for info in misconception_info:
                if not isinstance(info, dict):
                    continue
                if _norm(info.get("value")) == selected_value:
                    return {
                        "type": info.get("type", "UNKNOWN"),
                        "value": selected_value,
                        "why_wrong": info.get("why_wrong", ""),
                        "teaching_point": info.get("teaching_point", ""),
                        "description": info.get("description", ""),
                    }

        # Fallback: try distractor_info (older format, stored as string repr)
        distractor_info = payload.get("distractor_info")
        if distractor_info:
            try:
                if hasattr(distractor_info, "distractors"):
                    for d in distractor_info.distractors:
                        if _norm(getattr(d, "value", None)) == selected_value:
                            misc_type = d.misconception_type.value if hasattr(d.misconception_type, "value") else str(d.misconception_type)
                            return {
                                "type": misc_type,
                                "value": selected_value,
                                "why_wrong": getattr(d, "why_wrong", "") or "",
                                "teaching_point": getattr(d, "teaching_point", "") or "",
                            }
            except Exception:
                pass

        # Unknown misconception - still track that they got it wrong
        return {
            "type": "UNKNOWN",
            "value": selected_value,
            "why_wrong": "",
            "teaching_point": "",
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
        trap_info=None,
        include_misconceptions: bool = False,  # Phase 1: Default to False for question payload
    ) -> List[Dict[str, Any]]:
        """Format options with misconception and trap data extracted from distractor_info and trap_info.
        
        Args:
            options: List of option text strings
            distractor_info: Optional distractor metadata
            trap_info: Optional trap metadata
            include_misconceptions: If True, include misconception data (for answer responses).
                                    If False, return lean options (for question payloads).
                                    Phase 1 security: misconception data only on wrong answers.
        """
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

            # Phase 1: Only extract misconception data when explicitly requested (answer responses)
            if include_misconceptions and distractor_info and hasattr(distractor_info, "distractors"):
                for distractor in distractor_info.distractors:
                    if distractor.value == opt:
                        misconception_type = (
                            distractor.misconception_type.value
                            if hasattr(distractor.misconception_type, "value")
                            else str(distractor.misconception_type)
                        )
                        option_dict["misconceptionTarget"] = {
                            "id": f"misconception_{i}_{misconception_type}",
                            "name": misconception_type.replace("_", " ").title(),
                            "explanation": distractor.why_wrong or f"This represents a {misconception_type} misconception",
                        }
                        option_dict["commonMistake"] = True
                        break

            # Phase 1: Only include trap data when misconceptions are requested (answer responses)
            if include_misconceptions and trap_indices is not None:
                try:
                    if i in trap_indices:
                        option_dict["isTrap"] = True
                        option_dict["trapExplanation"] = trap_description
                except Exception:
                    pass

            formatted.append(option_dict)

        return formatted

    def _extract_data_representation(self, question) -> Optional[Dict[str, Any]]:
        """Extract data representation (tables, diagrams) from question.

        Normalizes older Question model fields into the frontend `dataRepresentation` shape.
        """
        if not hasattr(question, "data_representation") or not question.data_representation:
            return None

        data_rep = question.data_representation

        # Detect representation type
        repr_type = "text"
        if isinstance(data_rep, str):
            if "```" in data_rep:
                repr_type = "code"
            elif "|" in data_rep:
                repr_type = "table"
            elif any(char in data_rep for char in ["●", "○", "■", "□"]):
                repr_type = "diagram"

        return {
            "type": repr_type,
            "url": None,  # Backend sends text/markdown, not URL
            "alt": f"Visual representation for {getattr(question, 'topic', 'question')}",
            "caption": f"Data: {getattr(question, 'topic', 'question')}",
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
        from api.models.distractor import MisconceptionType
        
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

    def _normalize_chapter_key(self, chapter: str | None) -> str:
        """Normalize chapter keys to canonical frontend values.

        Canonical chapter keys (used everywhere):
        - large_numbers (Chapter 1)
        - fractions_decimals (Chapter 6)
        - factors_multiples (Chapter 9)
        - data_patterns (Chapter 10)

        This method maps all known aliases (legacy names, frontend variants,
        chapter numbers) to canonical keys and logs warnings for unknowns.
        """
        raw = str(chapter or "").strip().lower()
        if not raw:
            return "large_numbers"

        # Canonical keys (return immediately if exact match)
        CANONICAL_KEYS = {"large_numbers", "fractions_decimals", "factors_multiples", "data_patterns"}
        if raw in CANONICAL_KEYS:
            return raw

        # Alias mapping: legacy names, chapter numbers, frontend-friendly variants
        ALIAS_MAP = {
            # large_numbers aliases
            "ch1": "large_numbers",
            "chapter1": "large_numbers",
            "chapter 1": "large_numbers",
            "ch1: the fish tale": "large_numbers",
            "the fish tale": "large_numbers",
            "place_value": "large_numbers",
            "place value": "large_numbers",
            "large numbers": "large_numbers",

            # fractions_decimals aliases
            "ch6": "fractions_decimals",
            "chapter6": "fractions_decimals",
            "chapter 6": "fractions_decimals",
            "fractions": "fractions_decimals",
            "decimals": "fractions_decimals",
            "fractions decimals": "fractions_decimals",
            "fractions and decimals": "fractions_decimals",
            "fractions_and_decimals": "fractions_decimals",

            # factors_multiples aliases (including legacy class5_chapter5)
            "ch5": "factors_multiples",
            "chapter5": "factors_multiples",
            "chapter 5": "factors_multiples",
            "ch9": "factors_multiples",
            "chapter9": "factors_multiples",
            "chapter 9": "factors_multiples",
            "class5_chapter5": "factors_multiples",
            "class5 chapter5": "factors_multiples",
            "class5_chapter_5": "factors_multiples",
            "factors": "factors_multiples",
            "multiples": "factors_multiples",
            "factors multiples": "factors_multiples",
            "factors and multiples": "factors_multiples",
            "factors_and_multiples": "factors_multiples",
            "hcf": "factors_multiples",
            "lcm": "factors_multiples",
            "gcd": "factors_multiples",

            # data_patterns aliases
            "ch10": "data_patterns",
            "chapter10": "data_patterns",
            "chapter 10": "data_patterns",
            "data patterns": "data_patterns",
            "patterns": "data_patterns",
            "sequences": "data_patterns",
            "data handling": "data_patterns",
            "data_handling": "data_patterns",
        }

        if raw in ALIAS_MAP:
            return ALIAS_MAP[raw]

        # Fuzzy fallback: check if any canonical key is a substring
        for canonical in CANONICAL_KEYS:
            if canonical.replace("_", "") in raw.replace("_", "").replace(" ", ""):
                logger.debug(f"Chapter key '{chapter}' fuzzy-matched to '{canonical}'")
                return canonical

        # Unknown key: log warning and default to large_numbers
        logger.warning(f"Unknown chapter key '{chapter}' – defaulting to 'large_numbers'")
        return "large_numbers"


# Singleton instance
_adapter_instance: Optional[SessionAdapter] = None


def get_session_adapter() -> SessionAdapter:
    """Get or create singleton SessionAdapter instance."""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = SessionAdapter()
    return _adapter_instance
