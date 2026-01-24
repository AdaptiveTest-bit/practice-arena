"""
Template Engine Module for Phase 4.

Contains the LeanTemplateEngine and supporting classes for generating
question instances from templates with lean payloads.

Phase 7 Update: Universal Template Ingestor for single "drop point" format.
Phase 8 Update: Refactored with separation of concerns:
  - safe_functions.py: Math/educational functions registry
  - constraint_validator.py: Two-phase constraint validation
  - variable_generator.py: Variable generation with constraints
  - template_renderer.py: Template rendering and question building
  - question_generator.py: Main orchestrator
"""

# New modular components (recommended)
from .safe_functions import safe_functions, SafeFunctions
from .constraint_validator import constraint_validator, ConstraintValidator
from .variable_generator import variable_generator, VariableGenerator as NewVariableGenerator, GenerationResult
from .template_renderer import template_renderer, question_builder, TemplateRenderer as NewTemplateRenderer, QuestionBuilder
from .question_generator import (
    question_generator,
    QuestionGenerator,
    QuestionResult,
    generate_question,
    generate_batch,
    validate_template,
)

# Legacy imports for backward compatibility
from .lean_template_engine import (
    LeanTemplateEngine,
    VariableGenerator,
    TemplateRenderer,
    AnswerEvaluator
)

from .ingestor import (
    UniversalTemplateIngestor,
    UniversalTemplateIngestorSync,
)

from .universal_schema import (
    UniversalTemplate,
    UniversalTemplateBatch,
    IngestResult,
    BatchIngestResult,
    GenerationTestResult,
    QuestionType,
    TemplateSource,
    TemplateStatus,
    VariableSchema,
    OptionDefinition,
    SolutionDefinition,
    DiagramConfig,
    CustomFunction,
)

__all__ = [
    # Core engine
    "LeanTemplateEngine",
    "VariableGenerator", 
    "TemplateRenderer",
    "AnswerEvaluator",
    # Universal Ingestor
    "UniversalTemplateIngestor",
    "UniversalTemplateIngestorSync",
    # Schema types
    "UniversalTemplate",
    "UniversalTemplateBatch",
    "IngestResult",
    "BatchIngestResult",
    "GenerationTestResult",
    "QuestionType",
    "TemplateSource",
    "TemplateStatus",
    "VariableSchema",
    "OptionDefinition",
    "SolutionDefinition",
    "DiagramConfig",
    "CustomFunction",
]
