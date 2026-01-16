"""
Template Engine Module for Phase 4.

Contains the LeanTemplateEngine and supporting classes for generating
question instances from templates with lean payloads.
"""

from .lean_template_engine import (
    LeanTemplateEngine,
    VariableGenerator,
    TemplateRenderer,
    AnswerEvaluator
)

__all__ = [
    "LeanTemplateEngine",
    "VariableGenerator", 
    "TemplateRenderer",
    "AnswerEvaluator"
]
