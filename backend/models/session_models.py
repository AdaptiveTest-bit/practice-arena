"""Pydantic models for session management API."""

from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from enum import Enum
from api.models.distractor import DistractorSet, TrapInfo
from api.models.cognitive_levels import BloomInfo


class BloomLevel(str, Enum):
    """Bloom's taxonomy cognitive levels."""
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


class SessionStatus(str, Enum):
    """Practice session status."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    RESUMED = "resumed"


class MasteryStatus(str, Enum):
    """Concept mastery status."""
    MASTERED = "mastered"
    IN_PROGRESS = "in_progress"
    WEAK = "weak"
    NOT_STARTED = "not_started"


# ============================================================================
# REQUEST MODELS
# ============================================================================

class StartSessionRequest(BaseModel):
    """Request to start a new practice session."""
    student_id: int
    chapter_id: int
    class_level: int = 5
    subject: str = "Mathematics"


class RecordAnswerRequest(BaseModel):
    """Request to record an answer."""
    concept: str
    bloom_level: str
    is_correct: bool
    time_taken_seconds: Optional[int] = None
    misconception_type: Optional[str] = None


class PauseSessionRequest(BaseModel):
    """Request to pause a session."""
    reason: Optional[str] = None


class EndSessionRequest(BaseModel):
    """Request to end a session."""
    reason: Optional[str] = None


class UpdateSessionRequest(BaseModel):
    """Request to update session manually."""
    accuracy_by_concept: Optional[Dict[str, float]] = None
    completion_percentage: Optional[float] = None
    bloom_levels_completed: Optional[List[str]] = None


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class BloomLevelStatus(BaseModel):
    """Status of a Bloom level."""
    level: str
    status: str  # "locked", "in_progress", "completed"
    accuracy: float = 0.0
    questions_attempted: int = 0
    questions_correct: int = 0
    can_advance: bool = False
    advancement_message: str = ""


class ConceptStatus(BaseModel):
    """Status of a concept."""
    concept: str
    accuracy: float
    total_questions: int
    correct_answers: int
    status: str  # "mastered", "in_progress", "weak", "not_started"
    bloom_levels_covered: List[str] = []


class BreakPoint(BaseModel):
    """A break point (struggle point)."""
    concept: str
    bloom_level: str
    accuracy: float
    severity: str  # "critical", "high", "medium", "low"
    recorded_at: str


class Misconception(BaseModel):
    """A recorded misconception."""
    misconception_type: str
    concept: str
    bloom_levels: List[str]
    frequency: int


class RemediationPlan(BaseModel):
    """Remediation plan for a session."""
    critical_concepts: List[str] = []
    frequent_misconceptions: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    priorities: List[Dict[str, Any]] = []
    total_break_points: int = 0


class SessionProgressResponse(BaseModel):
    """Complete session progress response."""
    session_id: int
    student_id: int
    chapter_id: int
    subject: str = "Mathematics"
    class_level: int = 5
    
    # Overall metrics
    completion_percentage: float
    overall_accuracy: float
    total_questions_attempted: int
    total_questions_correct: int
    session_duration_minutes: int
    
    # Bloom levels
    current_bloom_level: str
    bloom_levels_status: Optional[Dict[str, Dict[str, Any]]] = None
    
    # Concepts
    concepts_covered: List[str] = []
    concepts_mastered: List[str] = []
    concepts_weak: List[str] = []
    accuracy_by_concept: Dict[str, float] = {}
    
    # Status
    status: str = "in_progress"
    session_start_time: str
    last_updated: str


class SessionStartResponse(BaseModel):
    """Response when starting a session."""
    success: bool
    session_id: int
    student_id: int
    chapter_id: int
    status: str
    message: str
    is_new: bool = True


class AnswerRecordResponse(BaseModel):
    """Response when recording an answer."""
    success: bool
    is_correct: bool
    
    # Concept result
    concept: str
    concept_accuracy: float
    concept_status: str
    
    # Bloom level result
    bloom_level: str
    bloom_accuracy: float
    can_advance_to_next_level: bool
    advancement_message: str = ""
    
    # Break point info
    break_point_recorded: bool = False
    break_point_severity: Optional[str] = None
    
    # Misconception info
    misconception_recorded: bool = False
    misconception_type: Optional[str] = None
    
    # Overall progress
    overall_accuracy: float
    completion_percentage: float


class SessionEndResponse(BaseModel):
    """Response when ending a session."""
    success: bool
    session_id: int
    status: str
    completion_percentage: float
    overall_accuracy: float
    total_questions_attempted: int
    total_questions_correct: int
    session_duration_minutes: int
    concepts_mastered: List[str] = []
    concepts_weak: List[str] = []
    message: str


class RemediationResponse(BaseModel):
    """Response with remediation plan."""
    session_id: int
    has_issues: bool
    remediation_plan: RemediationPlan
    total_break_points: int
    critical_issues: int
    high_priority_issues: int


class ErrorResponse(BaseModel):
    """Error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    status_code: int


# ============================================================================
# PHASE 3 - QUESTION GENERATION & ANSWER SUBMISSION MODELS
# ============================================================================

class NextQuestionResponse(BaseModel):
    """Response for a generated next question tied to a practice session."""

    success: bool
    session_id: int
    question_id: str

    # Question metadata used for tracking
    chapter_id: int
    concept: str
    bloom_level: str
    difficulty: float = 1.0

    # Renderable question payload (aligned with Question model)
    question_text: str
    options: Optional[List[str]] = None
    
    # Rich content fields for hybrid neuro-symbolic rendering
    rich_html_content: Optional[str] = None
    rich_narrative: Optional[str] = None
    visual_hints: Optional[List[str]] = None
    logical_trap: Optional[str] = None
    solution_steps: Optional[List[str]] = None
    
    # Phase 1-3 metadata (optional, for advanced features)
    distractor_info: Optional[DistractorSet] = None
    trap_info: Optional[TrapInfo] = None
    bloom_info: Optional[BloomInfo] = None


class SubmitAnswerRequest(BaseModel):
    """Submit an answer for a previously generated question."""

    question_id: str

    # For this repo's MCQ flow, we accept selectedIndex to match existing endpoint.
    selected_index: int

    time_taken_seconds: Optional[int] = None


class SubmitAnswerResponse(BaseModel):
    """Answer checking + full tracker update response."""

    success: bool
    session_id: int
    question_id: str

    is_correct: bool
    correct_index: Optional[int] = None

    # Lightweight feedback (can expand later)
    answer: Optional[str] = None
    solution_steps: Optional[List[str]] = None

    # Tracking context
    concept: str
    bloom_level: str

    # Tracker results (mirrors AnswerRecordResponse where possible)
    concept_accuracy: float
    concept_status: str

    can_advance_to_next_level: bool
    advancement_message: str = ""

    overall_accuracy: float
    completion_percentage: float


class DifficultyMasteryStatus(BaseModel):
    """Status of mastery for a single difficulty level."""
    accuracy: float
    attempts: int
    mastered: bool
    status: str


class BloomMasteryStatus(BaseModel):
    """Status of mastery for a single Bloom level."""
    accuracy: float
    attempts: int
    mastered: bool
    status: str


class ConceptMasteryStatus(BaseModel):
    """Status of mastery for a single concept."""
    accuracy: float
    attempts: int
    mastered: bool
    status: str


class MisconceptionInfo(BaseModel):
    """Information about a misconception."""
    type: str
    count: int


class CompletionAnalysis(BaseModel):
    """Analysis of completion status across all dimensions."""
    difficulty_mastery: Dict[int, Dict[str, Any]]
    bloom_mastery: Dict[str, Dict[str, Any]]
    concept_mastery: Dict[str, Dict[str, Any]]
    problem_misconceptions: List[Dict[str, Any]]


class SessionSummary(BaseModel):
    """Summary of session performance."""
    questions_answered: int
    accuracy_overall: float
    concepts_mastered: List[str] = []
    concepts_in_progress: List[str] = []
    time_spent_minutes: int


class SessionCompletionResponse(BaseModel):
    """Response when checking if session is complete."""
    success: bool
    is_complete: bool
    completion_analysis: CompletionAnalysis
    session_summary: SessionSummary
    next_recommendation: str  # "COMPLETE" or "CONTINUE"
