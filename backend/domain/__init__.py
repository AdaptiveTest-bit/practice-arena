"""Business Logic Domains

This package organizes the backend business logic into 4 core domains:

1. content_generation/ - Question generation, YAML banks, rendering, story generation
2. adaptive_learning/  - Leitner scheduling, misconception detection, difficulty adaptation
3. session_management/ - Quiz sessions, student tracking, database operations
4. analytics/          - Progress tracking, reporting, parent-facing analytics

Each domain is self-contained with its own models, services, and utilities.
Cross-domain communication happens through well-defined service interfaces.
"""

__all__ = [
    "content_generation",
    "adaptive_learning",
    "session_management",
    "analytics",
]
