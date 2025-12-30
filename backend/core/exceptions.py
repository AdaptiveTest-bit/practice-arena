"""Custom exceptions and error handlers."""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class APIException(Exception):
    """Base exception for API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize API exception.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code
            error_code: Machine-readable error code
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(APIException):
    """Raised when resource is not found."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource_type": resource_type} if resource_type else {}
        )


class UnauthorizedError(APIException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED"
        )


class ForbiddenError(APIException):
    """Raised when user lacks permissions."""
    
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN"
        )


class ConflictError(APIException):
    """Raised when request conflicts with existing data."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details=details
        )


class DatabaseError(APIException):
    """Raised when database operation fails."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details={"original_error": str(original_error)} if original_error else {}
        )


class ExternalServiceError(APIException):
    """Raised when external service call fails."""
    
    def __init__(self, service_name: str, message: str):
        super().__init__(
            message=f"{service_name}: {message}",
            status_code=503,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service_name}
        )


class RateLimitError(APIException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after}
        )


class ErrorResponse(BaseModel):
    """Standard API error response format."""
    
    success: bool = False
    error: str
    error_code: str
    status_code: int
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
