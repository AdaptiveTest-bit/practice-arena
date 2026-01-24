"""Application settings and configuration management.

Uses environment variables with sensible defaults for development.
All settings are validated at startup using Pydantic.
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    # ========== API Configuration ==========
    API_TITLE: str = "K.C. Nag Practice Engine"
    API_VERSION: str = "2.0.0"
    API_DESCRIPTION: str = "Adaptive Question Generation & Learning Analytics for CBSE Class 5 Mathematics"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # ========== Server Configuration ==========
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "5002"))
    RELOAD: bool = os.getenv("RELOAD", "False").lower() == "true"
    WORKERS: int = int(os.getenv("WORKERS", "4"))
    
    # ========== Database Configuration ==========
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://kunalranjan@localhost:5432/edtech_mvp"
    )
    DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() == "true"
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    
    # ========== Redis Configuration (Caching) ==========
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", None)
    REDIS_CACHE_ENABLED: bool = REDIS_URL is not None
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    
    # ========== CORS Configuration ==========
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",  # Admin UI (alternate port)
        "http://127.0.0.1:3002",  # Admin UI (alternate port)
        "http://localhost:3003",  # Admin UI
        "http://127.0.0.1:3003",  # Admin UI
        "http://localhost:5002",
    ]
    if os.getenv("CORS_ORIGINS"):
        CORS_ORIGINS = os.getenv("CORS_ORIGINS").split(",")
    
    # ========== Logging Configuration ==========
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "json"  # json or text
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", None)
    
    # ========== Feature Flags ==========
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "True").lower() == "true"
    ENABLE_PROFILING: bool = os.getenv("ENABLE_PROFILING", "False").lower() == "true"
    ENABLE_CACHING: bool = REDIS_CACHE_ENABLED and os.getenv("ENABLE_CACHING", "True").lower() == "true"
    
    # ========== Application Limits ==========
    MAX_REQUEST_SIZE: int = int(os.getenv("MAX_REQUEST_SIZE", "1048576"))  # 1MB
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_BLOOM_LEVELS: int = 6  # Remember, Understand, Apply, Analyze, Evaluate, Create
    QUESTIONS_PER_BLOOM_LEVEL: int = int(os.getenv("QUESTIONS_PER_BLOOM_LEVEL", "5"))
    MASTERY_THRESHOLD: float = 0.8  # 80% accuracy for mastery
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings (dependency injection)."""
    return settings
