"""
Template Ingestor API Routes.

Endpoints for ingesting templates via Universal Schema format.
Supports Manual UI, LLM Batch, and File Import.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
import json
import yaml
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from domain.template_engine import (
    UniversalTemplateIngestor,
    UniversalTemplate,
    UniversalTemplateBatch,
    IngestResult,
    BatchIngestResult,
    GenerationTestResult,
    QuestionType,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin/templates/universal", tags=["Templates - Universal Schema"])


# ============================================================
# Pydantic Request/Response Models
# ============================================================

class TemplateIngestRequest(BaseModel):
    """Request to ingest a single template."""
    template: Dict[str, Any] = Field(..., description="Template in Universal Schema format")
    source: str = Field("MANUAL", description="Creation source: MANUAL, LLM_BATCH, FILE_IMPORT")
    created_by: str = Field("admin", description="User who created the template")


class BatchIngestRequest(BaseModel):
    """Request to ingest multiple templates."""
    templates: List[Dict[str, Any]] = Field(..., description="List of templates in Universal Schema format")
    source: str = Field("LLM_BATCH", description="Creation source")
    created_by: str = Field("admin", description="User who created the templates")


class PreviewRequest(BaseModel):
    """Request to preview template generation."""
    template: Dict[str, Any] = Field(..., description="Template to preview")
    count: int = Field(5, ge=1, le=20, description="Number of questions to generate")


class TemplateListResponse(BaseModel):
    """Response with list of templates."""
    total: int
    templates: List[Dict[str, Any]]


# ============================================================
# API Endpoints
# ============================================================

@router.post("/ingest", response_model=IngestResult)
async def ingest_template(
    request: TemplateIngestRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest a single template in Universal Schema format.
    
    This is the "drop point" - regardless of how the template was created
    (manual UI, LLM generation, file import), it goes through this endpoint.
    
    The template is validated, test-generated, and stored if successful.
    """
    try:
        ingestor = UniversalTemplateIngestor(db)
        result = await ingestor.ingest(
            template_data=request.template,
            source=request.source,
            created_by=request.created_by
        )
        
        if not result.success:
            # Return 200 with success=False so client can see detailed errors
            return result
        
        return result
        
    except Exception as e:
        logger.error(f"Template ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/batch", response_model=BatchIngestResult)
async def ingest_templates_batch(
    request: BatchIngestRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest multiple templates at once.
    
    Useful for:
    - LLM batch generation results
    - Importing from question banks
    - Bulk template creation
    
    Each template is validated independently. Some may succeed while others fail.
    """
    try:
        ingestor = UniversalTemplateIngestor(db)
        result = await ingestor.ingest_batch(
            batch_data={"templates": request.templates},
            source=request.source,
            created_by=request.created_by
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Batch ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview", response_model=List[GenerationTestResult])
async def preview_template(
    request: PreviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Preview question generation without saving.
    
    Use this to test a template before committing it.
    Returns generated questions with variables.
    """
    try:
        ingestor = UniversalTemplateIngestor(db)
        results = await ingestor.preview_generation(
            template_data=request.template,
            count=request.count
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Preview generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import/file", response_model=BatchIngestResult)
async def import_templates_from_file(
    file: UploadFile = File(...),
    source: str = Query("FILE_IMPORT", description="Source tag for imported templates"),
    created_by: str = Query("admin", description="User importing the file"),
    db: AsyncSession = Depends(get_db)
):
    """
    Import templates from a JSON or YAML file.
    
    Supported formats:
    - JSON array of templates
    - JSON object with "templates" key
    - YAML equivalent
    
    Each template must conform to Universal Schema format.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Determine file format
    filename = file.filename.lower()
    is_yaml = filename.endswith('.yaml') or filename.endswith('.yml')
    is_json = filename.endswith('.json')
    
    if not (is_yaml or is_json):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file format. Use .json or .yaml/.yml"
        )
    
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        if is_yaml:
            data = yaml.safe_load(content_str)
        else:
            data = json.loads(content_str)
        
        # Normalize to list of templates
        if isinstance(data, list):
            templates = data
        elif isinstance(data, dict):
            if 'templates' in data:
                templates = data['templates']
            else:
                # Single template
                templates = [data]
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid file content. Expected array or object with templates."
            )
        
        # Ingest the templates
        ingestor = UniversalTemplateIngestor(db)
        result = await ingestor.ingest_batch(
            batch_data={"templates": templates},
            source=source,
            created_by=created_by
        )
        
        return result
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {e}")
    except Exception as e:
        logger.error(f"File import failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=IngestResult)
async def validate_template(
    request: TemplateIngestRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate a template without saving.
    
    Returns validation result with any errors or warnings.
    The template is not stored even if validation passes.
    """
    try:
        # Validate schema
        try:
            template = UniversalTemplate.model_validate(request.template)
        except Exception as e:
            return IngestResult(
                success=False,
                name=request.template.get('name', 'Unknown'),
                errors=[f"Schema validation failed: {str(e)}"]
            )
        
        # Validate formulas
        ingestor = UniversalTemplateIngestor(db)
        formula_result = ingestor._validate_formulas(template)
        
        if not formula_result[0]:
            return IngestResult(
                success=False,
                name=template.name,
                errors=formula_result[1],
                warnings=formula_result[2]
            )
        
        # Test generation
        test_result = ingestor._test_generation(template, count=5)
        
        return IngestResult(
            success=test_result[0],
            name=template.name,
            errors=test_result[1] if not test_result[0] else [],
            warnings=formula_result[2],
            test_generations=test_result[2]
        )
        
    except Exception as e:
        logger.error(f"Template validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema")
async def get_template_schema():
    """
    Get the Universal Template Schema definition.
    
    Returns the JSON Schema for template validation.
    Useful for building UI forms or LLM prompts.
    """
    return {
        "schema_version": "1.0",
        "title": "Universal Template Schema",
        "description": "Single format for all template creation methods",
        "question_types": [qt.value for qt in QuestionType],
        "example": {
            "name": "Example - Find Roots of Quadratic",
            "concept_id": "math.class10.quadratic.solve_factorization",
            "question_type": "MCQ",
            "question_pattern": "Find the roots of x² − {{sum}}x + {{product}} = 0",
            "variables": {
                "base": {
                    "root1": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
                    "root2": {"type": "integer", "enum": [1, 2, 3, 4, 5]}
                },
                "computed": {
                    "sum": {"formula": "root1 + root2"},
                    "product": {"formula": "root1 * root2"}
                },
                "constraints": ["root1 < root2"]
            },
            "options": [
                {"pattern": "{{root1}}, {{root2}}", "is_correct": True},
                {"pattern": "{{root1}}, {{-root2}}", "is_correct": False, "misconception_id": "SIGN_ERROR"},
                {"pattern": "{{sum}}, {{product}}", "is_correct": False},
                {"pattern": "{{root1 + 1}}, {{root2 - 1}}", "is_correct": False}
            ],
            "difficulty": 2,
            "bloom_level": "APPLY",
            "estimated_time": 60,
            "hints": [
                "Think about what two numbers add up to {{sum}}",
                "Those same numbers should multiply to give {{product}}"
            ],
            "tags": ["quadratic", "factorization", "roots"]
        },
        "available_functions": [
            "gcd(a, b)", "lcm(a, b)", "factors(n)", "multiples(n, count)",
            "is_prime(n)", "prime_factors(n)", "sum_factors(n)", 
            "factor_count(n)", "is_coprime(a, b)", "lcm_three(a, b, c)",
            "gcd_three(a, b, c)", "is_perfect_square(n)", "is_perfect_cube(n)",
            "sqrt(n)", "abs(n)", "min(a, b)", "max(a, b)", "pow(a, b)",
            "floor(n)", "ceil(n)", "round(n)"
        ]
    }


@router.get("/functions")
async def get_available_functions():
    """
    Get list of available functions for computed variables.
    
    These functions can be used in formula definitions.
    """
    from domain.template_engine.lean_template_engine import VariableGenerator
    
    safe_funcs = VariableGenerator._get_safe_functions()
    
    functions = []
    for name, func in safe_funcs.items():
        doc = func.__doc__ or "No description available"
        functions.append({
            "name": name,
            "description": doc.strip().split('\n')[0] if doc else "No description"
        })
    
    return {
        "total": len(functions),
        "functions": sorted(functions, key=lambda x: x["name"])
    }
