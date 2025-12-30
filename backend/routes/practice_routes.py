"""API endpoints for practice sessions."""

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from services.session_manager import SessionManager
from services.bloom_level_enforcer import BloomLevelEnforcer
from services.concept_mastery_tracker import ConceptMasteryTracker
from services.break_point_tracker import BreakPointTracker
from models.session_models import (
    StartSessionRequest,
    RecordAnswerRequest,
    PauseSessionRequest,
    EndSessionRequest,
    SessionStartResponse,
    SessionProgressResponse,
    AnswerRecordResponse,
    SessionEndResponse,
    RemediationResponse,
    ErrorResponse,
    NextQuestionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    SessionCompletionResponse,
)
from services.question_service import QuestionService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/practice", tags=["practice"])

# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_session_manager() -> SessionManager:
    """Get session manager instance."""
    return SessionManager()


def get_bloom_enforcer() -> BloomLevelEnforcer:
    """Get Bloom level enforcer instance."""
    return BloomLevelEnforcer()


def get_concept_tracker() -> ConceptMasteryTracker:
    """Get concept mastery tracker instance."""
    return ConceptMasteryTracker()


def get_break_tracker() -> BreakPointTracker:
    """Get break point tracker instance."""
    return BreakPointTracker()


def get_question_service(request: Request) -> QuestionService:
    """Get question service instance from app state (singleton)."""
    return request.app.state.question_service


# ============================================================================
# SESSION MANAGEMENT ENDPOINTS
# ============================================================================

@router.post(
    "/session/start",
    response_model=SessionStartResponse,
    summary="Start a new practice session",
    tags=["Session Management"]
)
async def start_session(
    request: StartSessionRequest,
    sm: SessionManager = Depends(get_session_manager),
) -> SessionStartResponse:
    """
    Start a new practice session or resume an existing one.
    
    **Parameters:**
    - `student_id`: ID of the student
    - `chapter_id`: ID of the chapter to practice
    - `class_level`: Class level (default: 5)
    - `subject`: Subject name (default: Mathematics)
    
    **Response:**
    - `session_id`: The session ID to use for subsequent operations
    - `status`: "new" or "resumed"
    - `is_new`: Whether this is a new session or resumed
    """
    try:
        result = sm.start_session(
            student_id=request.student_id,
            chapter_id=request.chapter_id,
            class_level=request.class_level,
            subject=request.subject,
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail="Failed to start session"
            )
        
        return SessionStartResponse(
            success=True,
            session_id=result["session_id"],
            student_id=request.student_id,
            chapter_id=request.chapter_id,
            status=result["status"],
            message=result.get("message", "Session started successfully"),
            is_new=result.get("is_new", True),
        )
    except Exception as e:
        logger.error(f"Error starting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/session/{session_id}/progress",
    response_model=SessionProgressResponse,
    summary="Get session progress",
    tags=["Session Management"]
)
async def get_session_progress(
    session_id: int,
    sm: SessionManager = Depends(get_session_manager),
) -> SessionProgressResponse:
    """
    Get detailed progress information for a session.
    
    **Parameters:**
    - `session_id`: The session ID
    
    **Response:**
    - Complete session progress with all metrics
    - Bloom level status
    - Concept accuracy
    - Overall completion and accuracy
    """
    try:
        progress = sm.get_session_progress(session_id)
        
        if not progress:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return SessionProgressResponse(**progress)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/session/{session_id}/pause",
    summary="Pause a session",
    tags=["Session Management"]
)
async def pause_session(
    session_id: int,
    request: Optional[PauseSessionRequest] = None,
    sm: SessionManager = Depends(get_session_manager),
) -> Dict[str, Any]:
    """
    Pause a session (student can resume later).
    
    **Parameters:**
    - `session_id`: The session ID
    - `reason`: Optional reason for pausing
    
    **Response:**
    - Success status and confirmation
    """
    try:
        reason = request.reason if request else None
        result = sm.pause_session(session_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return {
            "success": True,
            "session_id": session_id,
            "status": "paused",
            "message": "Session paused successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/session/{session_id}/end",
    response_model=SessionEndResponse,
    summary="End a session",
    tags=["Session Management"]
)
async def end_session(
    session_id: int,
    request: Optional[EndSessionRequest] = None,
    sm: SessionManager = Depends(get_session_manager),
) -> SessionEndResponse:
    """
    End a practice session and finalize all metrics.
    
    **Parameters:**
    - `session_id`: The session ID
    - `reason`: Optional reason for ending
    
    **Response:**
    - Final session statistics
    - Mastered and weak concepts
    - Total duration and accuracy
    """
    try:
        result = sm.end_session(session_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return SessionEndResponse(
            success=True,
            session_id=session_id,
            status="completed",
            completion_percentage=result.get("completion_percentage", 0),
            overall_accuracy=result.get("overall_accuracy", 0),
            total_questions_attempted=result.get("total_questions_attempted", 0),
            total_questions_correct=result.get("total_questions_correct", 0),
            session_duration_minutes=result.get("session_duration_minutes", 0),
            concepts_mastered=result.get("concepts_mastered", []),
            concepts_weak=result.get("concepts_weak", []),
            message="Session ended successfully",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ANSWER & TRACKING ENDPOINTS
# ============================================================================

@router.post(
    "/session/{session_id}/answer",
    response_model=AnswerRecordResponse,
    summary="Record an answer",
    tags=["Answer Recording"]
)
async def record_answer(
    session_id: int,
    request: RecordAnswerRequest,
    sm: SessionManager = Depends(get_session_manager),
    be: BloomLevelEnforcer = Depends(get_bloom_enforcer),
    ct: ConceptMasteryTracker = Depends(get_concept_tracker),
    bt: BreakPointTracker = Depends(get_break_tracker),
) -> AnswerRecordResponse:
    """
    Record an answer and update all tracking systems.
    
    This endpoint:
    1. Updates Bloom level accuracy
    2. Updates concept mastery
    3. Detects and records break points
    4. Records misconceptions
    5. Updates session progress
    6. Checks for level advancement
    
    **Parameters:**
    - `session_id`: The session ID
    - `concept`: The concept being tested
    - `bloom_level`: The Bloom level of the question
    - `is_correct`: Whether the answer was correct
    - `time_taken_seconds`: Optional time taken for the answer
    - `misconception_type`: Optional misconception detected
    
    **Response:**
    - Answer correctness
    - Updated accuracies and statuses
    - Advancement eligibility
    - Any issues detected (break points, misconceptions)
    """
    try:
        # Get current session state
        session = sm._get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        # 1. Update Bloom level accuracy
        be.update_level_accuracy(session_id, request.bloom_level, request.is_correct)
        
        # 2. Update concept accuracy
        concept_result = ct.update_concept_accuracy(
            session_id,
            request.concept,
            request.is_correct,
            request.bloom_level
        )
        
        # 3. Check for break points
        break_point_recorded = False
        break_point_severity = None
        if concept_result:
            accuracy = concept_result.get("accuracy", 0)
            if accuracy < 0.70:  # BREAK_POINT_THRESHOLD
                break_result = bt.record_break_point(
                    session_id,
                    request.concept,
                    request.bloom_level,
                    accuracy,
                    concept_result.get("total_questions", 1),
                    concept_result.get("correct_answers", 0)
                )
                if break_result:
                    break_point_recorded = True
                    break_point_severity = break_result.get("severity")
        
        # 4. Record misconception if provided
        misconception_recorded = False
        if request.misconception_type:
            bt.record_misconception(
                session_id,
                request.misconception_type,
                request.concept,
                request.bloom_level
            )
            misconception_recorded = True
        
        # 5. Check for advancement
        advancement = be.can_advance_to_next_level(session_id, request.bloom_level)
        
        # 6. Update session progress
        updated_session = sm.update_session_progress(
            session_id,
            {
                "total_questions_attempted": (session.total_questions_attempted or 0) + 1,
                "total_questions_correct": (session.total_questions_correct or 0) + (1 if request.is_correct else 0),
            }
        )
        
        # Get updated overall accuracy
        overall_accuracy = 0.0
        if updated_session and updated_session.total_questions_attempted > 0:
            overall_accuracy = (
                updated_session.total_questions_correct or 0
            ) / updated_session.total_questions_attempted
        
        # Get updated completion percentage
        completion = updated_session.completion_percentage if updated_session else 0.0
        
        return AnswerRecordResponse(
            success=True,
            is_correct=request.is_correct,
            concept=request.concept,
            concept_accuracy=concept_result.get("accuracy", 0) if concept_result else 0,
            concept_status=concept_result.get("status", "not_started") if concept_result else "not_started",
            bloom_level=request.bloom_level,
            bloom_accuracy=0.0,  # Could be enhanced to get actual bloom accuracy
            can_advance_to_next_level=advancement.get("can_advance", False),
            advancement_message=advancement.get("message", ""),
            break_point_recorded=break_point_recorded,
            break_point_severity=break_point_severity,
            misconception_recorded=misconception_recorded,
            misconception_type=request.misconception_type,
            overall_accuracy=overall_accuracy,
            completion_percentage=completion,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording answer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TRACKING & ANALYTICS ENDPOINTS
# ============================================================================

@router.get(
    "/session/{session_id}/concepts",
    summary="Get concept tracking",
    tags=["Analytics"]
)
async def get_concepts(
    session_id: int,
    ct: ConceptMasteryTracker = Depends(get_concept_tracker),
) -> Dict[str, Any]:
    """
    Get concept accuracy and mastery status for a session.
    
    **Parameters:**
    - `session_id`: The session ID
    
    **Response:**
    - All concepts with accuracy
    - Mastered concepts
    - Weak concepts
    - In-progress concepts
    """
    try:
        concepts = ct.get_all_concepts_accuracy(session_id)
        if not concepts:
            raise HTTPException(
                status_code=404,
                detail=f"No concepts found for session {session_id}"
            )
        
        mastered = ct.get_mastered_concepts(session_id)
        weak = ct.get_weak_concepts(session_id)
        
        return {
            "session_id": session_id,
            "all_concepts": concepts,
            "mastered_concepts": mastered,
            "weak_concepts": weak,
            "concept_count": len(concepts),
            "mastered_count": len(mastered),
            "weak_count": len(weak),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting concepts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/session/{session_id}/bloom-levels",
    summary="Get Bloom level status",
    tags=["Analytics"]
)
async def get_bloom_levels(
    session_id: int,
    be: BloomLevelEnforcer = Depends(get_bloom_enforcer),
) -> Dict[str, Any]:
    """
    Get Bloom level progression status for a session.
    
    **Parameters:**
    - `session_id`: The session ID
    
    **Response:**
    - Status of each Bloom level
    - Current level
    - Advancement options
    """
    try:
        all_levels = be.get_all_levels_status(session_id)
        current_level = be.get_current_level(session_id)
        
        if not all_levels:
            raise HTTPException(
                status_code=404,
                detail=f"No Bloom levels found for session {session_id}"
            )
        
        return {
            "session_id": session_id,
            "current_level": current_level,
            "all_levels": all_levels,
            "total_levels": len(all_levels),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Bloom levels: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/session/{session_id}/break-points",
    summary="Get break points",
    tags=["Analytics"]
)
async def get_break_points(
    session_id: int,
    severity: Optional[str] = Query(None, description="Filter by severity: critical, high, medium, low"),
    bt: BreakPointTracker = Depends(get_break_tracker),
) -> Dict[str, Any]:
    """
    Get all break points (struggle areas) for a session.
    
    **Parameters:**
    - `session_id`: The session ID
    - `severity`: Optional filter by severity level
    
    **Response:**
    - List of break points with severity
    - Critical break points
    - Remediation suggestions
    """
    try:
        break_points = bt.get_all_break_points(session_id)
        critical_points = bt.get_critical_break_points(session_id)
        
        if break_points is None:
            raise HTTPException(
                status_code=404,
                detail=f"No break points data found for session {session_id}"
            )
        
        # Filter by severity if requested
        if severity and break_points:
            break_points = [bp for bp in break_points if bp.get("severity") == severity]
        
        return {
            "session_id": session_id,
            "break_points": break_points or [],
            "critical_break_points": critical_points or [],
            "total_break_points": len(break_points or []),
            "critical_count": len(critical_points or []),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting break points: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/session/{session_id}/remediation",
    response_model=RemediationResponse,
    summary="Get remediation plan",
    tags=["Analytics"]
)
async def get_remediation_plan(
    session_id: int,
    bt: BreakPointTracker = Depends(get_break_tracker),
) -> RemediationResponse:
    """
    Get a complete remediation plan for a session.
    
    This includes:
    - Critical concepts needing immediate help
    - Frequent misconceptions
    - Personalized recommendations
    - Priority list for remediation
    
    **Parameters:**
    - `session_id`: The session ID
    
    **Response:**
    - Structured remediation plan
    - Issue severity classification
    - Actionable recommendations
    """
    try:
        plan = bt.get_remediation_plan(session_id)
        
        if not plan:
            raise HTTPException(
                status_code=404,
                detail=f"No remediation plan available for session {session_id}"
            )
        
        break_points = bt.get_all_break_points(session_id) or []
        critical_points = bt.get_critical_break_points(session_id) or []
        high_priority = [bp for bp in break_points if bp.get("severity") in ["high", "critical"]]
        
        return RemediationResponse(
            session_id=session_id,
            has_issues=len(break_points) > 0,
            remediation_plan=plan,
            total_break_points=len(break_points),
            critical_issues=len(critical_points),
            high_priority_issues=len(high_priority),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting remediation plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HELPER ENDPOINTS
# ============================================================================

@router.get(
    "/session/{session_id}/status",
    summary="Get session status",
    tags=["Session Management"]
)
async def get_session_status(
    session_id: int,
    sm: SessionManager = Depends(get_session_manager),
) -> Dict[str, Any]:
    """
    Quick status check for a session.
    
    **Parameters:**
    - `session_id`: The session ID
    
    **Response:**
    - Session status
    - Basic metrics
    - Current activity
    """
    try:
        session = sm._get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return {
            "session_id": session_id,
            "student_id": session.student_id,
            "chapter_id": session.chapter_id,
            "status": session.status,
            "completion_percentage": session.completion_percentage,
            "overall_accuracy": session.overall_accuracy,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "updated_at": session.updated_at.isoformat() if session.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    summary="Health check",
    tags=["System"]
)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring.
    
    **Response:**
    - Service status
    - Timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Practice Engine API"
    }


# ============================================================================
# PHASE 3 - QUESTION GENERATION & ANSWER SUBMISSION (CANONICAL FLOW)
# ============================================================================

@router.post(
    "/session/{session_id}/next-question",
    response_model=NextQuestionResponse,
    summary="Generate next adaptive question",
    tags=["Question Generation"]
)
async def next_question(
    session_id: str,
    qs: QuestionService = Depends(get_question_service),
) -> NextQuestionResponse:
    """
    Generate the next question for a practice session using adaptive selection.
    
    **Parameters:**
    - `session_id`: The practice session ID (accepts string, converts to int)
    
    **Response:**
    - Question ID, text, options
    - Metadata: concept, bloom_level, difficulty
    - Ready for student to answer
    """
    try:
        # Convert session_id from string to int
        try:
            session_id_int = int(session_id) if isinstance(session_id, str) else session_id
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid session_id: {session_id}. Must be a valid integer.")
        
        result = qs.generate_next_question_for_practice(session_id_int)
        return NextQuestionResponse(**result)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating next question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/session/{session_id}/submit-answer",
    response_model=SubmitAnswerResponse,
    summary="Submit answer and update trackers",
    tags=["Question Generation"]
)
async def submit_answer(
    session_id: str,
    request: SubmitAnswerRequest,
    qs: QuestionService = Depends(get_question_service),
) -> SubmitAnswerResponse:
    """
    Submit an answer and update all Phase 1 trackers atomically.
    
    **Parameters:**
    - `session_id`: The practice session ID (accepts string, converts to int)
    - `question_id`: The question ID from next-question response
    - `selected_index`: The MCQ option index (0-3)
    - `time_taken_seconds`: Optional time spent on question
    
    **Response:**
    - Answer correctness
    - Updated accuracies and statuses
    - Advancement eligibility
    - Overall progress
    """
    try:
        # Convert session_id from string to int
        try:
            session_id_int = int(session_id) if isinstance(session_id, str) else session_id
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid session_id: {session_id}. Must be a valid integer.")
        
        result = qs.submit_answer_for_practice(
            practice_session_id=session_id_int,
            question_id=request.question_id,
            selected_index=request.selected_index,
            time_taken_seconds=request.time_taken_seconds,
        )
        return SubmitAnswerResponse(**result)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MISSING ENDPOINTS FOR INTEGRATION & OTHER PROJECT
# ============================================================================

@router.post(
    "/question",
    response_model=Dict[str, Any],
    summary="Get next question for practice session",
    tags=["Question Generation"]
)
async def get_next_question(
    request: Dict[str, Any],
    qs: QuestionService = Depends(get_question_service),
) -> Dict[str, Any]:
    """
    Get the next question for a practice session.
    
    This endpoint is an alias for /session/{session_id}/next-question
    providing backward compatibility and simpler request model.
    
    **Parameters:**
    - `student_id`: ID of the student
    - `session_id`: ID of the practice session
    - `bloom_level`: (Optional) Target Bloom level
    
    **Response:**
    - Question with options
    - Metadata (concept, bloom_level, difficulty)
    """
    try:
        session_id = request.get("session_id")
        if not session_id:
            raise ValueError("session_id is required")
        
        result = qs.generate_next_question_for_practice(session_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting next question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/student/{student_id}/chapter/{chapter_id}/status",
    response_model=Dict[str, Any],
    summary="Get student chapter completion status (for other project)",
    tags=["Cross-Project Integration"]
)
async def get_student_chapter_status(
    student_id: int,
    chapter_id: int,
    sm: SessionManager = Depends(get_session_manager),
) -> Dict[str, Any]:
    """
    Get the completion status of a chapter for a student.
    
    This endpoint is designed for the "other project" to query:
    "Is this chapter 80% complete?" and get remediation details.
    
    **Parameters:**
    - `student_id`: ID of the student
    - `chapter_id`: ID of the chapter
    
    **Response:**
    - Completion percentage
    - Is ready for next chapter (>= 80%)
    - Weak concepts needing remediation
    - Detected misconceptions
    - Session history
    """
    try:
        # Get latest session for this student/chapter combo
        from database import get_active_session_for_student
        
        active_session = get_active_session_for_student(student_id, chapter_id)
        
        if not active_session:
            # No active session, check for completed sessions
            return {
                "student_id": student_id,
                "chapter_id": chapter_id,
                "has_active_session": False,
                "active_session_id": None,
                "last_session": None,
                "completion_percentage": 0,
                "is_ready_for_next_chapter": False,
                "weak_concepts": [],
                "misconceptions_detected": [],
                "message": "No session found for this student/chapter combination"
            }
        
        # Get session progress
        progress = sm.get_session_progress(active_session.id)
        
        completion = progress.get("completion_percentage", 0) if progress else 0
        overall_accuracy = progress.get("overall_accuracy", 0) if progress else 0
        weak_concepts = progress.get("concepts_weak", []) if progress else []
        
        # Check if ready (80%+ completion AND 80%+ overall accuracy)
        is_ready = completion >= 80 and overall_accuracy >= 0.80
        
        return {
            "student_id": student_id,
            "chapter_id": chapter_id,
            "has_active_session": True,
            "active_session_id": active_session.id,
            "last_session": {
                "session_id": active_session.id,
                "completion_percentage": active_session.completion_percentage or 0,
                "status": active_session.status,
                "created_at": active_session.created_at.isoformat() if active_session.created_at else None,
                "ended_at": active_session.session_end_time.isoformat() if active_session.session_end_time else None,
            },
            "completion_percentage": completion,
            "overall_accuracy": overall_accuracy,
            "is_ready_for_next_chapter": is_ready,
            "weak_concepts": weak_concepts,
            "misconceptions_detected": active_session.misconceptions_detected if hasattr(active_session, 'misconceptions_detected') else [],
            "session_duration_minutes": active_session.total_duration_minutes or 0,
        }
    except Exception as e:
        logger.error(f"Error getting student chapter status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SESSION COMPLETION CHECK
# ============================================================================

@router.get(
    "/session/{session_id}/check-completion",
    response_model=SessionCompletionResponse,
    summary="Check if student achieved mastery",
    tags=["Session Management"]
)
async def check_session_completion(
    session_id: str,
    sm: SessionManager = Depends(get_session_manager)
) -> SessionCompletionResponse:
    """
    Check if student has achieved mastery across all dimensions.
    
    Mastery requires:
    1. All difficulties (1-5): ≥80% accuracy each
    2. All Bloom levels in chapter: ≥80% accuracy each
    3. All concepts: ≥80% accuracy each
    4. No problematic misconceptions (2+ errors in same type)
    
    Note: Only checks dimensions that exist in the chapter. 
    If a Bloom level wasn't taught, it's not required.
    
    Returns:
    - is_complete: True if mastery achieved
    - completion_analysis: Breakdown of each dimension
    - session_summary: Stats and progress
    - next_recommendation: "COMPLETE" or "CONTINUE"
    """
    try:
        # Convert session_id from string to int
        try:
            session_id_int = int(session_id) if isinstance(session_id, str) else session_id
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid session_id: {session_id}. Must be a valid integer.")
        
        result = sm.check_session_completion(session_id_int)
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "Session not found"))
        
        return SessionCompletionResponse(
            success=result["success"],
            is_complete=result["is_complete"],
            completion_analysis=result["completion_analysis"],
            session_summary=result["session_summary"],
            next_recommendation=result["next_recommendation"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking session completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))
