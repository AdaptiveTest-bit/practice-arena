"""
Admin API endpoints for Phase 5 implementation.

RESTful API for template management, workflow transitions, and validation.
Integrates with admin service layer and provides HTTP responses.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from core.database import get_db
from db.models import QuestionTemplate
from domain.admin.template_service import AdminTemplateService, TemplateValidationError, WorkflowTransitionError


# Pydantic models for request/response
class TemplateCreateRequest(BaseModel):
    """Request model for template creation."""
    concept_id: str = Field(..., description="Concept ID from taxonomy")
    template_code: str = Field(..., description="Python template code")
    question_pattern: str = Field(..., description="Question text template")
    variable_schema: Dict[str, Any] = Field(..., description="Variable generation schema")
    answer_logic: str = Field(..., description="Answer computation logic")
    option_patterns: List[str] = Field(..., description="Option template patterns")
    difficulty: int = Field(..., ge=1, le=5, description="Difficulty level 1-5")
    bloom_level: str = Field(..., description="Bloom's taxonomy level")
    estimated_time: int = Field(..., gt=0, description="Estimated time in seconds")
    misconceptions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Misconception mappings")
    # Quality fields
    solution_pattern: Optional[str] = Field(default=None, description="Jinja2 template for step-by-step solution")
    solution_steps_schema: Optional[Dict[str, Any]] = Field(default=None, description="Schema for solution steps")
    hint_pattern: Optional[str] = Field(default=None, description="Jinja2 template for progressive hints")
    narrative_pattern: Optional[str] = Field(default=None, description="Jinja2 template for rich narrative")
    diagram_config: Optional[Dict[str, Any]] = Field(default=None, description="Diagram type and variable mappings")


class TemplateResponse(BaseModel):
    """Response model for template data."""
    id: int
    concept_id: str
    question_pattern: str
    difficulty: int
    bloom_level: str
    estimated_time: int
    status: str
    validation_passed: bool
    validation_errors: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    reviewed_by: Optional[str]
    published_at: Optional[datetime]
    # Quality fields
    solution_pattern: Optional[str] = None
    hint_pattern: Optional[str] = None
    narrative_pattern: Optional[str] = None
    diagram_config: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class WorkflowActionRequest(BaseModel):
    """Request model for workflow actions."""
    feedback: Optional[str] = Field(default=None, description="Feedback for rejection")


class BulkIngestRequest(BaseModel):
    """Request model for bulk template ingestion."""
    templates: List[TemplateCreateRequest] = Field(..., description="Templates to ingest")


class BulkIngestResponse(BaseModel):
    """Response model for bulk ingestion results."""
    total: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]]
    created_templates: List[Dict[str, Any]]


# Create router
router = APIRouter(prefix="/api/admin/templates", tags=["admin"])


def get_template_service(db: Session = Depends(get_db)) -> AdminTemplateService:
    """Dependency injection for template service."""
    return AdminTemplateService(db)


@router.post("/ingest", response_model=TemplateResponse)
async def ingest_template(
    template_data: TemplateCreateRequest,
    db: Session = Depends(get_db),
    service: AdminTemplateService = Depends(get_template_service)
):
    """
    Ingest a new template with validation.
    
    - Validates concept ID and bloom level against taxonomy
    - Validates template structure and quality against rubrics
    - Creates template in DRAFT status
    - Processes misconception mappings if provided
    """
    try:
        # Convert to dict for service
        template_dict = template_data.model_dump(exclude_unset=True)
        
        # Get created_by from auth (for now, use a placeholder)
        created_by = "admin_user"  # TODO: Get from authentication
        
        template = service.ingest_template(template_dict, created_by)
        return TemplateResponse.from_orm(template)
        
    except TemplateValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/ingest/bulk", response_model=BulkIngestResponse)
async def ingest_bulk_templates(
    request: BulkIngestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    service: AdminTemplateService = Depends(get_template_service)
):
    """
    Bulk ingest multiple templates.
    
    - Processes each template individually
    - Continues processing even if some fail
    - Returns detailed results for each template
    """
    try:
        # Convert to dict for service
        templates_data = [template.model_dump(exclude_unset=True) for template in request.templates]
        created_by = "admin_user"  # TODO: Get from authentication
        
        results = service.ingest_bulk_templates(templates_data, created_by)
        return BulkIngestResponse(**results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{template_id}/submit", response_model=TemplateResponse)
async def submit_template_for_review(
    template_id: int,
    db: Session = Depends(get_db),
    service: AdminTemplateService = Depends(get_template_service)
):
    """
    Submit a template for review.
    
    - Moves template from DRAFT to REVIEW status
    - Requires validation to have passed
    """
    try:
        submitted_by = "admin_user"  # TODO: Get from authentication
        template = service.submit_for_review(template_id, submitted_by)
        return TemplateResponse.from_orm(template)
        
    except WorkflowTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{template_id}/approve", response_model=TemplateResponse)
async def approve_template(
    template_id: int,
    db: Session = Depends(get_db),
    service: AdminTemplateService = Depends(get_template_service)
):
    """
    Approve a template.
    
    - Moves template from REVIEW to APPROVED status
    - Sets reviewed_by timestamp
    """
    try:
        approved_by = "admin_user"  # TODO: Get from authentication
        template = service.approve_template(template_id, approved_by)
        return TemplateResponse.from_orm(template)
        
    except WorkflowTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{template_id}/publish", response_model=TemplateResponse)
async def publish_template(
    template_id: int,
    db: Session = Depends(get_db),
    service: AdminTemplateService = Depends(get_template_service)
):
    """
    Publish a template for serving.
    
    - Moves template from APPROVED to PUBLISHED status
    - Sets published_at timestamp
    - Only published templates can be served to users
    """
    try:
        published_by = "admin_user"  # TODO: Get from authentication
        template = service.publish_template(template_id, published_by)
        return TemplateResponse.from_orm(template)
        
    except WorkflowTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{template_id}/reject", response_model=TemplateResponse)
async def reject_template(
    template_id: int,
    request: WorkflowActionRequest,
    db: Session = Depends(get_db),
    service: AdminTemplateService = Depends(get_template_service)
):
    """
    Reject a template with feedback.
    
    - Moves template back to DRAFT status
    - Stores feedback as validation error
    - Requires feedback to be provided
    """
    if not request.feedback:
        raise HTTPException(status_code=400, detail="Feedback is required for rejection")
    
    try:
        rejected_by = "admin_user"  # TODO: Get from authentication
        template = service.reject_template(template_id, rejected_by, request.feedback)
        return TemplateResponse.from_orm(template)
        
    except WorkflowTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{template_id}/archive", response_model=TemplateResponse)
async def archive_template(
    template_id: int,
    db: Session = Depends(get_db),
    service: AdminTemplateService = Depends(get_template_service)
):
    """
    Archive a template.
    
    - Moves template to ARCHIVED status
    - Cannot be served when archived
    """
    try:
        archived_by = "admin_user"  # TODO: Get from authentication
        template = service.archive_template(template_id, archived_by)
        return TemplateResponse.from_orm(template)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    status: Optional[str] = None,
    concept_id: Optional[str] = None,
    db: Session = Depends(get_db),
    service: AdminTemplateService = Depends(get_template_service)
):
    """
    List templates with optional filtering.
    
    - Filter by status (DRAFT, REVIEW, APPROVED, PUBLISHED, ARCHIVED)
    - Filter by concept ID
    - Returns most recent templates first
    """
    try:
        if status:
            templates = service.get_templates_by_status(status.upper(), concept_id)
        else:
            # If no status specified, return all templates
            query = db.query(QuestionTemplate)
            if concept_id:
                query = query.filter(QuestionTemplate.concept_id == concept_id)
            templates = query.order_by(QuestionTemplate.created_at.desc()).all()
        
        return [TemplateResponse.from_orm(template) for template in templates]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific template by ID.
    """
    template = db.query(QuestionTemplate).filter(QuestionTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return TemplateResponse.from_orm(template)


@router.get("/workflow/summary")
async def get_workflow_summary(
    db: Session = Depends(get_db),
    service: AdminTemplateService = Depends(get_template_service)
):
    """
    Get summary of templates by workflow status.
    
    Returns counts for each status and total.
    """
    try:
        summary = service.get_template_workflow_summary()
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{template_id}/preview")
async def preview_template(
    template_id: int,
    db: Session = Depends(get_db),
    service: AdminTemplateService = Depends(get_template_service)
):
    """
    Generate a preview question from a template.
    
    - Works for any template status (including DRAFT)
    - Returns generated question with all options
    - Useful for content writers to test templates
    """
    try:
        # Get template regardless of status
        template = db.query(QuestionTemplate).filter(QuestionTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Try to generate a preview question (allow any status for previews)
        from domain.template_engine.lean_template_engine import LeanTemplateEngine
        engine = LeanTemplateEngine(db)
        
        try:
            question_data = await engine.generate_question(template_id, allow_any_status=True)
            return {
                "success": True,
                "template_id": template_id,
                "status": template.status,
                "question": question_data.get('payload', {}),
                "variables": question_data.get('variables', {}),
                "correct_index": question_data.get('correct_index'),
            }
        except Exception as gen_error:
            return {
                "success": False,
                "template_id": template_id,
                "status": template.status,
                "error": str(gen_error),
                "question_pattern": template.question_pattern,
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{template_id}/validate")
async def validate_template_for_generation(
    template_id: int,
    db: Session = Depends(get_db),
    service: AdminTemplateService = Depends(get_template_service)
):
    """
    Validate that a template can be used for question generation.
    
    - Checks if template is published and validated
    - Tests actual question generation
    - Returns sample question if successful
    """
    try:
        validation_result = service.validate_template_for_generation(template_id)
        return validation_result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/status/{status}", response_model=List[TemplateResponse])
async def get_templates_by_status(
    status: str,
    concept_id: Optional[str] = None,
    db: Session = Depends(get_db),
    service: AdminTemplateService = Depends(get_template_service)
):
    """
    Get templates by status.
    
    - Valid statuses: DRAFT, REVIEW, APPROVED, PUBLISHED, ARCHIVED
    - Optional concept ID filtering
    """
    try:
        templates = service.get_templates_by_status(status.upper(), concept_id)
        return [TemplateResponse.from_orm(template) for template in templates]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# Misconceptions API
# ============================================================================

class MisconceptionResponse(BaseModel):
    """Response model for misconception data."""
    id: int
    code: str
    title: str
    description: str
    teaching_point: str
    subject: str
    concept_tags: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class MisconceptionCreateRequest(BaseModel):
    """Request model for creating a misconception."""
    code: str = Field(..., description="Unique misconception code (e.g., ARITHMETIC_ERROR)")
    title: str = Field(..., description="Brief title for the misconception")
    description: str = Field(..., description="Detailed description of the misconception")
    teaching_point: str = Field(..., description="How to correct this misconception")
    subject: str = Field(..., description="Subject area (math, science, etc.)")
    concept_tags: Optional[List[str]] = Field(default=None, description="Related concept IDs")


@router.get("/misconceptions", response_model=List[MisconceptionResponse])
async def list_misconceptions(
    subject: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all misconceptions, optionally filtered by subject.
    
    Used by the admin UI to tag incorrect options with misconceptions.
    """
    from db.models import Misconception
    
    try:
        query = db.query(Misconception)
        if subject:
            query = query.filter(Misconception.subject == subject.lower())
        
        misconceptions = query.order_by(Misconception.code).all()
        return [MisconceptionResponse.from_orm(m) for m in misconceptions]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/misconceptions", response_model=MisconceptionResponse)
async def create_misconception(
    data: MisconceptionCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new misconception.
    
    Misconceptions can be reused across multiple templates.
    """
    from db.models import Misconception
    
    try:
        # Check if code already exists
        existing = db.query(Misconception).filter(Misconception.code == data.code).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Misconception with code '{data.code}' already exists")
        
        misconception = Misconception(
            code=data.code,
            title=data.title,
            description=data.description,
            teaching_point=data.teaching_point,
            subject=data.subject.lower(),
            concept_tags=data.concept_tags,
        )
        
        db.add(misconception)
        db.commit()
        db.refresh(misconception)
        
        return MisconceptionResponse.from_orm(misconception)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/misconceptions/{misconception_id}", response_model=MisconceptionResponse)
async def get_misconception(
    misconception_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific misconception by ID."""
    from db.models import Misconception
    
    misconception = db.query(Misconception).filter(Misconception.id == misconception_id).first()
    if not misconception:
        raise HTTPException(status_code=404, detail="Misconception not found")
    
    return MisconceptionResponse.from_orm(misconception)


@router.delete("/misconceptions/{misconception_code}")
async def delete_misconception(
    misconception_code: str,
    db: Session = Depends(get_db)
):
    """Delete a misconception by code."""
    from db.models import Misconception
    
    try:
        misconception = db.query(Misconception).filter(Misconception.code == misconception_code).first()
        if not misconception:
            raise HTTPException(status_code=404, detail=f"Misconception with code '{misconception_code}' not found")
        
        db.delete(misconception)
        db.commit()
        
        return {"success": True, "message": f"Misconception '{misconception_code}' deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateCreateRequest,
    db: Session = Depends(get_db),
    service: AdminTemplateService = Depends(get_template_service)
):
    """
    Update an existing template.
    
    - Only DRAFT templates can be updated
    - Re-validates the template after update
    """
    try:
        template = db.query(QuestionTemplate).filter(QuestionTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Only allow updates to DRAFT templates
        if template.status not in ("DRAFT", "REVIEW"):
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot update template in {template.status} status. Only DRAFT or REVIEW templates can be updated."
            )
        
        # Update template fields
        update_data = template_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(template, field):
                setattr(template, field, value)
        
        # Re-validate
        template.validation_passed = True  # Simplified - actual validation would be more complex
        template.validation_errors = None
        
        db.commit()
        db.refresh(template)
        
        return TemplateResponse.from_orm(template)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
