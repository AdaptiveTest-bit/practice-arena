"""FastAPI middleware for logging, error handling, and monitoring."""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import time
import uuid

from config.logging_config import get_logger
from core.exceptions import APIException, ErrorResponse

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request and response details."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Record start time
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Incoming request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown"
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response sent",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2)
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
        
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(
                f"Request processing error",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "duration_ms": round(duration * 1000, 2)
                },
                exc_info=True
            )
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling and formatting errors."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Handle exceptions and return formatted error responses."""
        try:
            return await call_next(request)
        
        except APIException as e:
            # Handle custom API exceptions
            return JSONResponse(
                status_code=e.status_code,
                content=ErrorResponse(
                    error=e.message,
                    error_code=e.error_code,
                    status_code=e.status_code,
                    details=e.details,
                    timestamp=datetime.utcnow().isoformat()
                ).model_dump()
            )
        
        except ValueError as e:
            # Handle validation errors
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    error=str(e),
                    error_code="VALIDATION_ERROR",
                    status_code=400,
                    timestamp=datetime.utcnow().isoformat()
                ).model_dump()
            )
        
        except Exception as e:
            # Handle unexpected errors
            logger.error(
                f"Unhandled exception",
                extra={
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    "error": str(e)
                },
                exc_info=True
            )
            
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error="Internal server error",
                    error_code="INTERNAL_SERVER_ERROR",
                    status_code=500,
                    timestamp=datetime.utcnow().isoformat()
                ).model_dump()
            )


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring API performance."""
    
    def __init__(self, app, slow_request_threshold_ms: int = 1000):
        """Initialize middleware.
        
        Args:
            app: FastAPI application
            slow_request_threshold_ms: Threshold for logging slow requests
        """
        super().__init__(app)
        self.slow_request_threshold_ms = slow_request_threshold_ms
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Monitor request performance."""
        start_time = time.time()
        
        try:
            response = await call_next(request)
        finally:
            duration_ms = (time.time() - start_time) * 1000
            
            # Log slow requests
            if duration_ms > self.slow_request_threshold_ms:
                logger.warning(
                    f"Slow request detected",
                    extra={
                        "request_id": getattr(request.state, "request_id", "unknown"),
                        "method": request.method,
                        "path": request.url.path,
                        "duration_ms": round(duration_ms, 2),
                        "threshold_ms": self.slow_request_threshold_ms
                    }
                )
        
        return response
