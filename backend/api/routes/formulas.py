"""
Formula Management API Routes.

Endpoints for creating, testing, and managing custom formulas.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, update
import logging

from core.database import get_db
from db.models.custom_formula import CustomFormula, FormulaStatus, FormulaCategory
from domain.template_engine.formula_sandbox import (
    FormulaSandbox, 
    FormulaSandboxError,
    FormulaValidationError,
    get_sandbox
)

logger = logging.getLogger(__name__)
# Note: Mounted at root in app_main.py, so we include full path here
router = APIRouter(prefix="/api/admin/formulas", tags=["Formulas"])


# ============================================================
# Pydantic Models
# ============================================================

class FormulaParameter(BaseModel):
    """A parameter for a formula."""
    name: str = Field(..., min_length=1, max_length=50)
    type: str = Field(default="integer")  # integer, float, string, list, boolean
    description: str = Field(default="")
    default_value: Optional[Any] = None


class TestCase(BaseModel):
    """A test case for a formula."""
    input: List[Any]
    expected: Any


class FormulaCreate(BaseModel):
    """Request model for creating a formula."""
    name: str = Field(..., min_length=1, max_length=100, pattern=r'^[a-z_][a-z0-9_]*$')
    display_name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(default=FormulaCategory.GENERAL.value)
    parameters: List[FormulaParameter] = Field(default_factory=list)
    return_type: str = Field(default="any")
    code: str = Field(..., min_length=10)
    description: Optional[str] = None
    example_usage: Optional[str] = None
    test_cases: List[TestCase] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "add_fractions",
                "display_name": "Add Two Fractions",
                "category": "Fractions",
                "parameters": [
                    {"name": "n1", "type": "integer", "description": "Numerator 1"},
                    {"name": "d1", "type": "integer", "description": "Denominator 1"},
                    {"name": "n2", "type": "integer", "description": "Numerator 2"},
                    {"name": "d2", "type": "integer", "description": "Denominator 2"}
                ],
                "return_type": "tuple",
                "code": "def add_fractions(n1, d1, n2, d2):\n    from math import gcd\n    num = n1 * d2 + n2 * d1\n    den = d1 * d2\n    g = gcd(num, den)\n    return (num // g, den // g)",
                "description": "Adds two fractions and returns the simplified result",
                "example_usage": "add_fractions(1, 2, 1, 3) → (5, 6)",
                "test_cases": [
                    {"input": [1, 2, 1, 3], "expected": [5, 6]},
                    {"input": [1, 4, 1, 4], "expected": [1, 2]}
                ]
            }
        }


class FormulaUpdate(BaseModel):
    """Request model for updating a formula."""
    display_name: Optional[str] = None
    category: Optional[str] = None
    parameters: Optional[List[FormulaParameter]] = None
    return_type: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    example_usage: Optional[str] = None
    test_cases: Optional[List[TestCase]] = None


class FormulaTestRequest(BaseModel):
    """Request model for testing a formula."""
    input: List[Any]


class FormulaResponse(BaseModel):
    """Response model for a formula."""
    id: str
    name: str
    display_name: str
    category: str
    parameters: List[dict]
    return_type: str
    code: str
    description: Optional[str]
    example_usage: Optional[str]
    test_cases: List[dict]
    status: str
    created_by: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class TestResult(BaseModel):
    """Result of a single test case."""
    index: int
    input: List[Any]
    expected: Any
    actual: Optional[Any]
    passed: bool
    error: Optional[str]


class ValidationResult(BaseModel):
    """Result of code validation."""
    is_valid: bool
    error: Optional[str]
    test_results: Optional[List[TestResult]]


# ============================================================
# API Endpoints
# ============================================================

@router.get("", response_model=List[FormulaResponse])
async def list_formulas(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in name or description"),
    db: Session = Depends(get_db)
):
    """
    List all custom formulas.
    
    Filter by category, status, or search term.
    """
    query = select(CustomFormula)
    
    if category:
        query = query.where(CustomFormula.category == category)
    
    if status:
        query = query.where(CustomFormula.status == status)
    else:
        # Default: show active and draft
        query = query.where(CustomFormula.status.in_([
            FormulaStatus.ACTIVE.value, 
            FormulaStatus.DRAFT.value
        ]))
    
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            CustomFormula.name.ilike(search_pattern) |
            CustomFormula.display_name.ilike(search_pattern) |
            CustomFormula.description.ilike(search_pattern)
        )
    
    query = query.order_by(CustomFormula.category, CustomFormula.name)
    
    result = db.execute(query)
    formulas = result.scalars().all()
    
    return [f.to_dict() for f in formulas]


@router.get("/categories")
async def list_categories():
    """List available formula categories."""
    return [
        {"value": c.value, "label": c.value}
        for c in FormulaCategory
    ]


@router.get("/active", response_model=List[FormulaResponse])
async def list_active_formulas(db: Session = Depends(get_db)):
    """
    List only ACTIVE formulas (for template editor).
    """
    query = select(CustomFormula).where(
        CustomFormula.status == FormulaStatus.ACTIVE.value
    ).order_by(CustomFormula.category, CustomFormula.name)
    
    result = db.execute(query)
    formulas = result.scalars().all()
    
    return [f.to_dict() for f in formulas]


@router.get("/{formula_id}", response_model=FormulaResponse)
async def get_formula(
    formula_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a single formula by ID."""
    result = db.execute(
        select(CustomFormula).where(CustomFormula.id == formula_id)
    )
    formula = result.scalar_one_or_none()
    
    if not formula:
        raise HTTPException(status_code=404, detail="Formula not found")
    
    return formula.to_dict()


@router.post("", response_model=FormulaResponse)
async def create_formula(
    data: FormulaCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new custom formula.
    
    The formula starts in DRAFT status and must be published
    after passing all tests.
    """
    # Check if name already exists
    existing = db.execute(
        select(CustomFormula).where(CustomFormula.name == data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400, 
            detail=f"Formula with name '{data.name}' already exists"
        )
    
    # Validate code
    sandbox = get_sandbox()
    is_valid, error = sandbox.validate_code(data.code)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Code validation failed: {error}"
        )
    
    # Create formula
    formula = CustomFormula(
        name=data.name,
        display_name=data.display_name,
        category=data.category,
        parameters=[p.model_dump() for p in data.parameters],
        return_type=data.return_type,
        code=data.code,
        description=data.description,
        example_usage=data.example_usage,
        test_cases=[t.model_dump() for t in data.test_cases],
        status=FormulaStatus.DRAFT.value,
    )
    
    db.add(formula)
    db.commit()
    db.refresh(formula)
    
    logger.info(f"Created formula: {formula.name}")
    return formula.to_dict()


@router.put("/{formula_id}", response_model=FormulaResponse)
async def update_formula(
    formula_id: UUID,
    data: FormulaUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a formula.
    
    If code is changed, status resets to DRAFT.
    """
    result = db.execute(
        select(CustomFormula).where(CustomFormula.id == formula_id)
    )
    formula = result.scalar_one_or_none()
    
    if not formula:
        raise HTTPException(status_code=404, detail="Formula not found")
    
    # Validate new code if provided
    if data.code:
        sandbox = get_sandbox()
        is_valid, error = sandbox.validate_code(data.code)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Code validation failed: {error}"
            )
        # Reset to draft if code changed
        formula.status = FormulaStatus.DRAFT.value
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == 'parameters' and value:
            value = [p if isinstance(p, dict) else p.model_dump() for p in value]
        if key == 'test_cases' and value:
            value = [t if isinstance(t, dict) else t.model_dump() for t in value]
        setattr(formula, key, value)
    
    db.commit()
    db.refresh(formula)
    
    logger.info(f"Updated formula: {formula.name}")
    return formula.to_dict()


@router.post("/{formula_id}/validate", response_model=ValidationResult)
async def validate_formula(
    formula_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Validate a formula by running all test cases.
    """
    result = db.execute(
        select(CustomFormula).where(CustomFormula.id == formula_id)
    )
    formula = result.scalar_one_or_none()
    
    if not formula:
        raise HTTPException(status_code=404, detail="Formula not found")
    
    sandbox = get_sandbox()
    
    # Validate code first
    is_valid, error = sandbox.validate_code(formula.code)
    if not is_valid:
        return ValidationResult(
            is_valid=False,
            error=f"Code validation failed: {error}",
            test_results=None
        )
    
    # Run test cases
    if not formula.test_cases:
        return ValidationResult(
            is_valid=False,
            error="No test cases defined. Add at least one test case.",
            test_results=[]
        )
    
    test_results = sandbox.run_test_cases(
        formula.code, 
        formula.name, 
        formula.test_cases
    )
    
    all_passed = all(r['passed'] for r in test_results)
    
    # Update status if all tests pass
    if all_passed:
        formula.status = FormulaStatus.TESTING.value
        db.commit()
    
    return ValidationResult(
        is_valid=all_passed,
        error=None if all_passed else "Some test cases failed",
        test_results=test_results
    )


@router.post("/{formula_id}/test", response_model=TestResult)
async def test_formula(
    formula_id: UUID,
    data: FormulaTestRequest,
    db: Session = Depends(get_db)
):
    """
    Run a formula with custom input for testing.
    """
    result = db.execute(
        select(CustomFormula).where(CustomFormula.id == formula_id)
    )
    formula = result.scalar_one_or_none()
    
    if not formula:
        raise HTTPException(status_code=404, detail="Formula not found")
    
    sandbox = get_sandbox()
    
    try:
        actual = sandbox.execute(formula.code, formula.name, data.input)
        return TestResult(
            index=0,
            input=data.input,
            expected=None,
            actual=actual,
            passed=True,
            error=None
        )
    except FormulaSandboxError as e:
        return TestResult(
            index=0,
            input=data.input,
            expected=None,
            actual=None,
            passed=False,
            error=str(e)
        )


@router.post("/{formula_id}/publish", response_model=FormulaResponse)
async def publish_formula(
    formula_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Publish a formula (make it available in templates).
    
    Requirements:
    - All test cases must pass
    - Must have at least one test case
    """
    result = db.execute(
        select(CustomFormula).where(CustomFormula.id == formula_id)
    )
    formula = result.scalar_one_or_none()
    
    if not formula:
        raise HTTPException(status_code=404, detail="Formula not found")
    
    # Validate first
    sandbox = get_sandbox()
    
    is_valid, error = sandbox.validate_code(formula.code)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Code validation failed: {error}"
        )
    
    if not formula.test_cases:
        raise HTTPException(
            status_code=400,
            detail="Cannot publish: No test cases defined"
        )
    
    # Run all tests
    test_results = sandbox.run_test_cases(
        formula.code, 
        formula.name, 
        formula.test_cases
    )
    
    if not all(r['passed'] for r in test_results):
        failed = [r for r in test_results if not r['passed']]
        raise HTTPException(
            status_code=400,
            detail=f"Cannot publish: {len(failed)} test(s) failed"
        )
    
    # Publish
    formula.status = FormulaStatus.ACTIVE.value
    db.commit()
    db.refresh(formula)
    
    logger.info(f"Published formula: {formula.name}")
    return formula.to_dict()


@router.delete("/{formula_id}")
async def deprecate_formula(
    formula_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Deprecate a formula (soft delete).
    
    The formula is marked as DEPRECATED but not deleted.
    """
    result = db.execute(
        select(CustomFormula).where(CustomFormula.id == formula_id)
    )
    formula = result.scalar_one_or_none()
    
    if not formula:
        raise HTTPException(status_code=404, detail="Formula not found")
    
    formula.status = FormulaStatus.DEPRECATED.value
    db.commit()
    
    logger.info(f"Deprecated formula: {formula.name}")
    return {"message": f"Formula '{formula.name}' deprecated"}


# ============================================================
# Formula Reload Endpoint (refresh loaded formulas)
# ============================================================

@router.post("/reload")
async def reload_formulas():
    """
    Reload all custom formulas from the database.
    
    Call this after publishing new formulas to make them
    immediately available in the template engine without 
    requiring a server restart.
    
    Returns:
        Number of formulas loaded
    """
    from domain.template_engine.lean_template_engine import VariableGenerator
    
    try:
        count = VariableGenerator.reload_custom_formulas()
        logger.info(f"Reloaded {count} custom formulas")
        return {
            "success": True,
            "message": f"Reloaded {count} custom formulas",
            "count": count
        }
    except Exception as e:
        logger.error(f"Failed to reload formulas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload formulas: {str(e)}"
        )


# ============================================================
# Code Preview Endpoint (for testing without saving)
# ============================================================

class CodeTestRequest(BaseModel):
    """Request for testing code without saving."""
    code: str
    function_name: str
    test_input: List[Any]


@router.post("/preview/test")
async def test_code_preview(data: CodeTestRequest):
    """
    Test code without saving.
    
    Use this for live preview in the editor.
    """
    sandbox = get_sandbox()
    
    # Validate
    is_valid, error = sandbox.validate_code(data.code)
    if not is_valid:
        return {
            "success": False,
            "error": f"Validation failed: {error}",
            "result": None
        }
    
    # Execute
    try:
        result = sandbox.execute(data.code, data.function_name, data.test_input)
        return {
            "success": True,
            "error": None,
            "result": result
        }
    except FormulaSandboxError as e:
        return {
            "success": False,
            "error": str(e),
            "result": None
        }
