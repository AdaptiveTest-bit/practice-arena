"""Skeleton Cache Manager - In-memory caching for SymPy-generated skeletons"""

import hashlib
import json
import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SkeletonCacheEntry:
    """Single cache entry for a skeleton."""
    skeleton: Dict[str, Any]
    difficulty: int
    chapter: str
    created_at: float
    hit_count: int = 0
    last_accessed: float = field(default_factory=time.time)


class SkeletonCacheManager:
    """LRU cache for math skeletons."""

    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self.cache: Dict[str, SkeletonCacheEntry] = {}
        self.hits = 0
        self.misses = 0
        logger.info(f"SkeletonCacheManager initialized (max: {max_entries})")

    def get_key(self, chapter: str, difficulty: int, parameters: Dict) -> str:
        """Generate deterministic cache key."""
        params_str = json.dumps(parameters, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"skeleton:{chapter}:{difficulty}:{params_hash}"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve from cache."""
        if key in self.cache:
            entry = self.cache[key]
            entry.hit_count += 1
            entry.last_accessed = time.time()
            self.hits += 1
            logger.debug(f"Cache HIT: {key} (total hits: {self.hits})")
            return entry.skeleton
        self.misses += 1
        logger.debug(f"Cache MISS: {key} (total misses: {self.misses})")
        return None

    def set(self, key: str, skeleton: Dict, chapter: str, difficulty: int) -> None:
        """Store in cache with LRU eviction."""
        if len(self.cache) >= self.max_entries:
            # Evict LRU
            lru_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].last_accessed
            )
            del self.cache[lru_key]
            logger.debug(f"LRU evicted: {lru_key}")

        self.cache[key] = SkeletonCacheEntry(
            skeleton=skeleton,
            difficulty=difficulty,
            chapter=chapter,
            created_at=time.time(),
            hit_count=0,
            last_accessed=time.time()
        )
        logger.debug(f"Cached: {key}")

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'entries': len(self.cache),
            'max_entries': self.max_entries,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate_percent': round(hit_rate, 2),
            'utilization_percent': round(len(self.cache) / self.max_entries * 100, 2)
        }

    def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")


# Singleton instance
_skeleton_cache = SkeletonCacheManager()


def get_skeleton_cache() -> SkeletonCacheManager:
    """Get global cache instance."""
    return _skeleton_cache
