"""Structured logging configuration with JSON output support."""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pythonjsonlogger import jsonlogger
from config.settings import settings


class StructuredFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context."""
    
    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record["timestamp"] = datetime.utcnow().isoformat()
        
        # Add log level
        log_record["level"] = record.levelname
        
        # Add module info
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno
        
        # Add environment
        log_record["environment"] = "development" if settings.DEBUG else "production"


def setup_logging() -> logging.Logger:
    """Configure application logging with optional JSON output.
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("practice_engine")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    if settings.LOG_FORMAT == "json":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if configured)
    if settings.LOG_FILE:
        try:
            file_handler = logging.FileHandler(settings.LOG_FILE)
            file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create file handler: {e}")
    
    return logger


# Initialize logger
logger = setup_logging()


def get_logger(name: str) -> logging.Logger:
    """Get a child logger with given name.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(f"practice_engine.{name}")
