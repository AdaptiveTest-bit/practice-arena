"""Content Caching Layer

This package provides caching for generated content to improve performance.

Cache Types:
- skeleton_cache: Caches mathematical skeletons (SymPy computations)
- story_cache: Caches generated K.C. Nag stories
- options_cache: Caches generated answer options

All caches use TTL-based expiration and LRU eviction policies.
"""

__all__ = []
