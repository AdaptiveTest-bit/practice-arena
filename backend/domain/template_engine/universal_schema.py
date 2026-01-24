"""
Universal Template Schema - Pydantic models for the drop-point format.

All template creation paths (Manual UI, LLM Batch, File Import) produce
this same format. The schema validates and transforms into internal DB format.
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime


# ============================================================
# ENUMS
# ============================================================

class QuestionType(str, Enum):
    """Supported question types."""
    MCQ = "MCQ"
    MCQ_MULTI = "MCQ_MULTI"
    FILL_BLANK = "FILL_BLANK"
    TRUE_FALSE = "TRUE_FALSE"
    ASSERTION_REASON = "ASSERTION_REASON"
    CASE_STUDY = "CASE_STUDY"
    MATCH_FOLLOWING = "MATCH_FOLLOWING"
    ORDERING = "ORDERING"
    NUMERIC = "NUMERIC"


class TemplateSource(str, Enum):
    """Source of template creation."""
    MANUAL = "MANUAL"
    LLM_BATCH = "LLM_BATCH"
    FILE_IMPORT = "FILE_IMPORT"


class TemplateStatus(str, Enum):
    """Template workflow status."""
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"


class VariationStatus(str, Enum):
    """Status of word problem variations."""
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"


# ============================================================
# VARIABLE DEFINITIONS
# ============================================================

class BaseVariable(BaseModel):
    """Base variable definition for random generation."""
    type: Literal["integer", "float", "string", "boolean"] = "integer"
    enum: Optional[List[Union[int, float, str]]] = None
    minimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None
    description: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_range_or_enum(self):
        """Ensure either enum or min/max is provided for numeric types."""
        if self.type in ("integer", "float"):
            if self.enum is None and (self.minimum is None or self.maximum is None):
                # Default range for integers
                if self.type == "integer":
                    self.minimum = self.minimum or 1
                    self.maximum = self.maximum or 100
                else:
                    self.minimum = self.minimum or 1.0
                    self.maximum = self.maximum or 100.0
        return self


class ComputedVariable(BaseModel):
    """Computed variable derived from base variables."""
    formula: str = Field(..., description="Formula using base variables and functions")
    type: Optional[Literal["integer", "float", "string", "boolean", "list", "tuple"]] = None
    description: Optional[str] = None
    default: Optional[Any] = Field(None, description="Default value if formula evaluation fails")


class CustomFunction(BaseModel):
    """
    User-defined function for use in formulas.
    
    Allows content writers to define reusable logic without backend changes.
    
    Example:
        {
            "params": ["x"],
            "body": "int(sqrt(x)) ** 2 == x",
            "description": "Checks if x is a perfect square"
        }
    
    Security: Only allowed to use safe functions and basic Python operations.
    """
    params: List[str] = Field(..., description="Parameter names for the function")
    body: str = Field(..., description="Single expression that returns a value")
    description: Optional[str] = Field(None, description="What this function does")
    
    @field_validator('body')
    @classmethod
    def validate_body_is_expression(cls, v):
        """Ensure body is a valid Python expression (not statements)."""
        try:
            compile(v, '<string>', 'eval')
        except SyntaxError as e:
            raise ValueError(f"Function body must be a single expression: {e}")
        return v
    
    @field_validator('params')
    @classmethod
    def validate_params(cls, v):
        """Ensure parameter names are valid identifiers."""
        import keyword
        for param in v:
            if not param.isidentifier():
                raise ValueError(f"Invalid parameter name: {param}")
            if keyword.iskeyword(param):
                raise ValueError(f"Parameter name cannot be a Python keyword: {param}")
        return v


class VariableSchema(BaseModel):
    """Complete variable definitions for a template."""
    base: Dict[str, BaseVariable] = Field(default_factory=dict)
    computed: Dict[str, Union[ComputedVariable, str]] = Field(default_factory=dict)
    constraints: List[str] = Field(default_factory=list)
    custom_functions: Dict[str, CustomFunction] = Field(
        default_factory=dict,
        description="User-defined functions for use in formulas"
    )
    use_libraries: List[str] = Field(
        default_factory=list,
        description="List of function library names to import (e.g., 'math_helpers', 'physics_basics')"
    )
    
    @field_validator('computed', mode='before')
    @classmethod
    def normalize_computed(cls, v):
        """Allow both dict and string shorthand for computed variables."""
        if isinstance(v, dict):
            result = {}
            for key, val in v.items():
                if isinstance(val, str):
                    result[key] = {"formula": val}
                else:
                    result[key] = val
            return result
        return v


# ============================================================
# OPTION DEFINITIONS
# ============================================================

class OptionDefinition(BaseModel):
    """Answer option definition."""
    pattern: str = Field(..., description="Option pattern with {{variables}}")
    is_correct: Union[bool, str] = Field(False, description="Is this the correct answer? Can be a formula string for dynamic correctness.")
    misconception_id: Optional[str] = None
    student_thinking: Optional[str] = Field(None, description="Why student might choose this")
    remediation: Optional[str] = Field(None, description="Hint for this wrong option")


# ============================================================
# SOLUTION DEFINITIONS
# ============================================================

class SolutionStep(BaseModel):
    """A single step in the solution."""
    number: int
    text: str
    latex: Optional[str] = None
    explanation: Optional[str] = None


class SolutionDefinition(BaseModel):
    """Step-by-step solution pattern."""
    steps: List[SolutionStep] = Field(default_factory=list)
    computed_vars: Optional[Dict[str, str]] = None


# ============================================================
# VISUAL DEFINITIONS
# ============================================================

class DiagramConfig(BaseModel):
    """Diagram configuration for visual questions."""
    type: str = Field(..., description="Diagram type from library")
    parameters: Dict[str, str] = Field(default_factory=dict)
    custom_svg: Optional[str] = None


# ============================================================
# MULTI-PART QUESTION DEFINITIONS
# ============================================================

class QuestionPart(BaseModel):
    """Part of a multi-part question (Case Study, A-R)."""
    type: Literal["assertion", "reason", "context", "sub_question"]
    label: Optional[str] = None
    pattern: str
    is_true: Optional[Union[bool, str]] = None  # Can be formula for dynamic
    options: Optional[List[OptionDefinition]] = None


class WordVariation(BaseModel):
    """Word problem variation for contextualized learning."""
    id: str
    context: str
    question_pattern: str
    answer_pattern: str
    status: VariationStatus = VariationStatus.DRAFT


# ============================================================
# MAIN TEMPLATE SCHEMA
# ============================================================

class UniversalTemplate(BaseModel):
    """
    Universal Template Schema - The single "drop point" format.
    
    All template creation paths produce this format:
    - Manual UI entry
    - LLM batch generation  
    - File import (JSON/YAML)
    
    Example:
        {
            "name": "Quadratic - Find Roots",
            "concept_id": "math.class10.quadratic.solve_factorization",
            "question_type": "MCQ",
            "question_pattern": "Find the roots of x² − {{sum}}x + {{product}} = 0",
            "variables": {
                "base": {"root1": {"type": "integer", "enum": [1,2,3,4,5]}},
                "computed": {"sum": "root1 + root2"}
            },
            "options": [...],
            "difficulty": 2
        }
    """
    
    # ============================================================
    # SECTION 1: IDENTITY
    # ============================================================
    
    id: Optional[str] = Field(None, description="Unique identifier (auto-generated if not provided)")
    name: str = Field(..., min_length=1, max_length=255, description="Human-readable name")
    concept_id: str = Field(..., min_length=1, description="Concept from knowledge graph")
    question_type: QuestionType = Field(QuestionType.MCQ, description="Question type")
    
    # ============================================================
    # SECTION 2: QUESTION DEFINITION
    # ============================================================
    
    question_pattern: Optional[str] = Field(None, description="Question pattern with {{variables}}")
    parts: Optional[List[QuestionPart]] = Field(None, description="For multi-part questions")
    options: List[OptionDefinition] = Field(..., min_length=2, description="Answer options")
    difficulty: int = Field(2, ge=1, le=5, description="Difficulty 1-5")
    
    # ============================================================
    # SECTION 3: VARIABLES
    # ============================================================
    
    variables: VariableSchema = Field(default_factory=VariableSchema)
    
    # ============================================================
    # SECTION 4: SOLUTION & HINTS
    # ============================================================
    
    solution: Optional[SolutionDefinition] = None
    hints: Optional[List[str]] = None
    
    # ============================================================
    # SECTION 5: VISUAL
    # ============================================================
    
    diagram: Optional[DiagramConfig] = None
    requires_latex: bool = Field(False, description="LaTeX rendering needed?")
    
    # ============================================================
    # SECTION 6: METADATA
    # ============================================================
    
    source: TemplateSource = Field(TemplateSource.MANUAL, description="Creation source")
    status: TemplateStatus = Field(TemplateStatus.DRAFT, description="Workflow status")
    tags: List[str] = Field(default_factory=list)
    variations: Optional[List[WordVariation]] = None
    
    # Additional metadata
    bloom_level: str = Field("UNDERSTAND", description="Bloom's taxonomy level")
    estimated_time: int = Field(60, ge=10, le=600, description="Estimated time in seconds")
    created_by: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_question_content(self):
        """Ensure either question_pattern or parts is provided."""
        if not self.question_pattern and not self.parts:
            raise ValueError("Either 'question_pattern' or 'parts' is required")
        return self
    
    @field_validator('options')
    @classmethod
    def validate_options(cls, v, info):
        """Validate options have at least one correct answer."""
        # Count statically correct options (ignore dynamic formulas)
        static_correct = sum(1 for opt in v if opt.is_correct is True)
        dynamic_correct = sum(1 for opt in v if isinstance(opt.is_correct, str))
        
        # If all options have static is_correct, ensure at least one is True
        if dynamic_correct == 0 and static_correct == 0:
            raise ValueError("At least one option must be marked as correct")
        
        return v


class UniversalTemplateBatch(BaseModel):
    """Batch of templates for bulk import."""
    templates: List[UniversalTemplate]
    metadata: Optional[Dict[str, Any]] = None


# ============================================================
# RESPONSE MODELS
# ============================================================

class IngestResult(BaseModel):
    """Result of single template ingestion."""
    success: bool
    template_id: Optional[int] = None
    name: str
    status: str = "DRAFT"
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    test_generations: int = 0


class BatchIngestResult(BaseModel):
    """Result of batch template ingestion."""
    total: int
    successful: int
    failed: int
    results: List[IngestResult]


class GenerationTestResult(BaseModel):
    """Result of test generation."""
    success: bool
    question: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
