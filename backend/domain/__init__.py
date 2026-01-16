"""Business Logic Domains

This package organizes the backend business logic into core domains:

1. content_generation/ - Question generation, YAML banks, rendering
2. adaptive_learning/  - Leitner scheduling, misconception detection
3. session_management/ - Quiz sessions, student tracking, database operations
4. adaptation/         - Concept graphs, mastery tracking, adaptive sequencing

Each domain is self-contained with its own models, services, and utilities.
Cross-domain communication happens through well-defined service interfaces.
"""

__all__ = [
    "content_generation",
    "adaptive_learning",
    "session_management",
    "adaptation",
]
