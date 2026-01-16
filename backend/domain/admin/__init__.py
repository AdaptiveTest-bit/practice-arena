"""
Admin Module for Phase 5 implementation.

Contains service layer and API endpoints for template management,
workflow transitions, and validation.
"""

from .template_service import AdminTemplateService, TemplateValidationError, WorkflowTransitionError

__all__ = [
    "AdminTemplateService",
    "TemplateValidationError", 
    "WorkflowTransitionError"
]
