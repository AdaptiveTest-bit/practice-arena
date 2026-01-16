"""
Admin API Module for Phase 5 implementation.

RESTful API endpoints for template management and workflow.
"""

from .templates import router as templates_router

__all__ = ["templates_router"]
