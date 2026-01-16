"""
CDN API Module for Phase 6 implementation.

RESTful API endpoints for diagram CDN management.
"""

from .diagrams import router as diagrams_router

__all__ = ["diagrams_router"]
