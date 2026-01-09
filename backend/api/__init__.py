"""API Layer

This package contains all API-related code:
- models/  - Pydantic request/response models (API contracts)
- routes/  - FastAPI route handlers (endpoints)

Separation from domain logic:
- API models handle serialization/deserialization
- Domain models handle business logic
- Routes orchestrate calls to domain services
"""

__all__ = ["models", "routes"]
