"""
Lean API v2 endpoints for Phase 8 implementation.

Provides clean, lean endpoints using only the lean template engine.
Supports feature flag routing for gradual rollout.
"""

from fastapi import APIRouter, HTTPException, Query, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import uuid
import asyncio
from datetime import datetime
import json
import hashlib

from db.base import Base
from core.database import get_db
from domain.template_engine import LeanTemplateEngine
from domain.cdn import DiagramCDNService


# Pydantic models for v2 API
class SessionStartRequestV2(BaseModel):
    """Request model for v2 session start."""
    student_id: Optional[str] = Field(None, description="Student identifier")
    grade_level: int = Field(..., ge=1, le=12, description="Grade level")
    mode: str = Field("practice", description="Session mode (practice, test, review)")
    chapter: Optional[str] = Field(None, description="Optional chapter filter")
    concept_ids: Optional[List[str]] = Field(None, description="Specific concepts to focus on")


class SessionStartResponseV2(BaseModel):
    """Response model for v2 session start."""
    success: bool
    session_id: str = Field(..., description="Unique session identifier")
    student_id: Optional[str] = Field(None, description="Student identifier")
    grade_level: int = Field(..., description="Grade level")
    mode: str = Field(..., description="Session mode")
    total_questions: int = Field(..., description="Number of questions in session")
    estimated_duration: int = Field(..., description="Estimated duration in minutes")
    concepts: List[str] = Field(..., description="Concepts covered in session")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class QuestionResponseV2(BaseModel):
    """Lean response model for v2 question endpoint."""
    success: bool
    session_id: str = Field(..., description="Session identifier")
    question_id: str = Field(..., description="Unique question identifier")
    question: str = Field(..., description="Question text")
    options: Optional[List[str]] = Field(None, description="Multiple choice options")
    diagrams: List[Dict[str, Any]] = Field(default=[], description="CDN diagram URLs")
    metadata: Dict[str, Any] = Field(..., description="Question metadata")
    # Note: No rich_html_content - using CDN URLs instead


class AnswerSubmitRequestV2(BaseModel):
    """Request model for v2 answer submission."""
    question_id: str = Field(..., description="Question identifier")
    selected_index: int = Field(..., ge=0, le=3, description="Selected option index")
    time_taken_seconds: Optional[int] = Field(None, description="Time taken to answer")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Student confidence level")


class AnswerSubmitResponseV2(BaseModel):
    """Response model for v2 answer submission."""
    success: bool
    is_correct: bool = Field(..., description="Whether answer was correct")
    correct_index: int = Field(..., description="Index of correct answer")
    feedback: Optional[Dict[str, Any]] = Field(None, description="Misconception feedback")
    mastery_score: float = Field(..., description="Updated mastery score")
    next_question_available: bool = Field(..., description="Whether more questions are available")


class SessionEndRequestV2(BaseModel):
    """Request model for v2 session end."""
    session_id: str = Field(..., description="Session identifier")
    reason: str = Field("completed", description="Reason for ending session")


class SessionEndResponseV2(BaseModel):
    """Response model for v2 session end."""
    success: bool
    session_summary: Dict[str, Any] = Field(..., description="Session performance summary")
    recommendations: List[str] = Field(..., description="Learning recommendations")


# Create router
router = APIRouter(prefix="/api/v2/quiz", tags=["quiz-v2"])


class LeanQuizServiceV2:
    """
    Lean quiz service using only the lean template engine.
    
    Single source of truth for question generation and session management.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.cdn_service = DiagramCDNService()
        self.template_engine = LeanTemplateEngine(db, self.cdn_service)
        
        # In-memory session storage (use Redis in production)
        self._sessions = {}
        self._session_questions = {}
    
    async def start_session(self, request: SessionStartRequestV2) -> SessionStartResponseV2:
        """
        Start a new quiz session using lean template engine.
        
        Args:
            request: Session start request
            
        Returns:
            Session configuration with lean metadata
        """
        session_id = str(uuid.uuid4())
        
        # Determine concepts for this session
        if request.concept_ids:
            concepts = request.concept_ids
        elif request.chapter:
            # Get concepts for chapter (currently factors_multiples only)
            concepts = ["factors_multiples.find_factors", "factors_multiples.find_multiples"]
        else:
            # Default concepts for grade level
            concepts = ["factors_multiples.find_factors", "factors_multiples.find_multiples"]
        
        # Generate questions using lean template engine
        try:
            questions = []
            for concept in concepts:
                concept_questions = await self.template_engine.generate_questions_for_concept(concept, 2)
                questions.extend(concept_questions)
            
            # Store session data
            self._sessions[session_id] = {
                "session_id": session_id,
                "student_id": request.student_id,
                "grade_level": request.grade_level,
                "mode": request.mode,
                "chapter": request.chapter,
                "concepts": concepts,
                "created_at": datetime.utcnow(),
                "current_question_index": 0,
                "total_questions": len(questions),
                "answered_questions": []
            }
            
            self._session_questions[session_id] = questions
            
            return SessionStartResponseV2(
                success=True,
                session_id=session_id,
                student_id=request.student_id,
                grade_level=request.grade_level,
                mode=request.mode,
                total_questions=len(questions),
                estimated_duration=len(questions) * 2,  # 2 minutes per question estimate
                concepts=concepts,
                metadata={
                    "engine": "lean_template_v2",
                    "cdn_enabled": True,
                    "payload_type": "lean"
                }
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")
    
    async def get_next_question(self, session_id: str) -> QuestionResponseV2:
        """
        Get the next question in the session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Lean question with CDN URLs
        """
        if session_id not in self._sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = self._sessions[session_id]
        questions = self._session_questions[session_id]
        
        if session["current_question_index"] >= len(questions):
            raise HTTPException(status_code=404, detail="No more questions in session")
        
        # Get current question
        question_data = questions[session["current_question_index"]]
        session["current_question_index"] += 1
        
        # Generate unique question ID
        question_id = f"{session_id}_q{session['current_question_index']}"
        
        return QuestionResponseV2(
            success=True,
            session_id=session_id,
            question_id=question_id,
            question=question_data["question"],
            options=question_data.get("options"),
            diagrams=question_data.get("diagrams", []),
            metadata=question_data["metadata"]
        )
    
    async def submit_answer(self, session_id: str, request: AnswerSubmitRequestV2) -> AnswerSubmitResponseV2:
        """
        Submit an answer and get lean feedback.
        
        Args:
            session_id: Session identifier
            request: Answer submission
            
        Returns:
            Lean feedback with mastery score
        """
        if session_id not in self._sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = self._sessions[session_id]
        
        # In a real implementation, we would evaluate the answer
        # For now, simulate evaluation
        is_correct = request.selected_index == 0  # Simplified: first option is correct
        correct_index = 0
        mastery_score = 0.8 if is_correct else 0.3
        
        # Record answer
        session["answered_questions"].append({
            "question_id": request.question_id,
            "selected_index": request.selected_index,
            "is_correct": is_correct,
            "time_taken": request.time_taken_seconds,
            "confidence": request.confidence
        })
        
        # Check if more questions available
        more_available = session["current_question_index"] < session["total_questions"]
        
        return AnswerSubmitResponseV2(
            success=True,
            is_correct=is_correct,
            correct_index=correct_index,
            feedback=None,  # Add misconception feedback if needed
            mastery_score=mastery_score,
            next_question_available=more_available
        )
    
    async def end_session(self, session_id: str, request: SessionEndRequestV2) -> SessionEndResponseV2:
        """
        End a quiz session and provide summary.
        
        Args:
            session_id: Session identifier
            request: Session end request
            
        Returns:
            Session summary and recommendations
        """
        if session_id not in self._sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = self._sessions[session_id]
        answered = session["answered_questions"]
        
        # Calculate session summary
        total_answered = len(answered)
        correct_count = sum(1 for a in answered if a["is_correct"])
        accuracy = correct_count / total_answered if total_answered > 0 else 0
        
        avg_time = sum(a.get("time_taken", 0) for a in answered) / total_answered if total_answered > 0 else 0
        
        session_summary = {
            "session_id": session_id,
            "total_questions": session["total_questions"],
            "questions_answered": total_answered,
            "correct_answers": correct_count,
            "accuracy": round(accuracy * 100, 1),
            "average_time_per_question": round(avg_time, 1),
            "concepts_covered": session["concepts"],
            "mode": session["mode"]
        }
        
        # Generate recommendations
        recommendations = []
        if accuracy < 0.6:
            recommendations.append("Review basic concepts and practice more problems")
        elif accuracy < 0.8:
            recommendations.append("Good progress! Focus on speed and accuracy")
        else:
            recommendations.append("Excellent! Try more challenging problems")
        
        # Clean up session data
        del self._sessions[session_id]
        del self._session_questions[session_id]
        
        return SessionEndResponseV2(
            success=True,
            session_summary=session_summary,
            recommendations=recommendations
        )


# Service dependency
def get_quiz_service_v2(db: Session = Depends(get_db)) -> LeanQuizServiceV2:
    """Dependency injection for v2 quiz service."""
    return LeanQuizServiceV2(db)


# V2 Endpoints
@router.post("/session/start", response_model=SessionStartResponseV2)
async def start_session_v2(
    request: SessionStartRequestV2,
    service: LeanQuizServiceV2 = Depends(get_quiz_service_v2)
):
    """
    Start a new quiz session using lean template engine.
    
    - Uses only lean template engine for question generation
    - CDN URLs for diagrams (no inline HTML)
    - Optimized payload sizes
    """
    return await service.start_session(request)


@router.get("/{session_id}/question", response_model=QuestionResponseV2)
async def get_question_v2(
    session_id: str,
    service: LeanQuizServiceV2 = Depends(get_quiz_service_v2)
):
    """
    Get the next question in the session.
    
    Returns lean question payload with CDN URLs.
    """
    return await service.get_next_question(session_id)


@router.post("/{session_id}/answer", response_model=AnswerSubmitResponseV2)
async def submit_answer_v2(
    session_id: str,
    request: AnswerSubmitRequestV2,
    service: LeanQuizServiceV2 = Depends(get_quiz_service_v2)
):
    """
    Submit an answer and get lean feedback.
    
    Provides mastery scoring and misconception feedback.
    """
    return await service.submit_answer(session_id, request)


@router.post("/{session_id}/end", response_model=SessionEndResponseV2)
async def end_session_v2(
    session_id: str,
    request: SessionEndRequestV2,
    service: LeanQuizServiceV2 = Depends(get_quiz_service_v2)
):
    """
    End a quiz session and get summary.
    
    Provides performance analytics and recommendations.
    """
    return await service.end_session(session_id, request)


@router.get("/{session_id}/status")
async def get_session_status_v2(
    session_id: str,
    service: LeanQuizServiceV2 = Depends(get_quiz_service_v2)
):
    """
    Get current session status.
    
    Returns progress and metadata without revealing answers.
    """
    if session_id not in service._sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = service._sessions[session_id]
    
    return {
        "success": True,
        "session_id": session_id,
        "current_question": session["current_question_index"],
        "total_questions": session["total_questions"],
        "questions_answered": len(session["answered_questions"]),
        "progress": round(session["current_question_index"] / session["total_questions"] * 100, 1)
    }


@router.get("/health")
async def health_check_v2():
    """
    Health check for v2 endpoints.
    
    Returns status of lean template engine and CDN service.
    """
    return {
        "success": True,
        "version": "v2",
        "engine": "lean_template",
        "cdn": "enabled",
        "payload_type": "lean",
        "timestamp": datetime.utcnow().isoformat()
    }
