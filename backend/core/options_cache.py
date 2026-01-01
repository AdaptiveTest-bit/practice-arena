"""Options Cache Manager - Redis-backed caching for misconception distractors"""

import json
import logging
from typing import Optional, List, Dict, Any
from datetime import timedelta
import redis

logger = logging.getLogger(__name__)


class OptionsCacheManager:
    """Manages options/distractors caching in Redis."""

    def __init__(self, redis_client: redis.Redis = None, ttl_days: int = 7):
        """
        Initialize options cache manager.

        Args:
            redis_client: Redis client instance (creates default if None)
            ttl_days: Time-to-live for cached options in days
        """
        if redis_client is None:
            redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )

        self.redis = redis_client
        self.ttl = timedelta(days=ttl_days)
        self.hits = 0
        self.misses = 0
        self.misconception_types = [
            'INCOMPLETE_REASONING',
            'WRONG_OPERATION',
            'COMPUTATIONAL_ERROR',
            'CONCEPTUAL_ERROR',
            'CONTEXTUAL_ERROR',
            'TRAP_ANSWER',
            'OFF_BY_ONE',
            'MISINTERPRETATION',
            'REVERSED_LOGIC',
            'PARTIAL_KNOWLEDGE'
        ]
        logger.info(f"OptionsCacheManager initialized (TTL: {ttl_days} days)")

    def get_key(self, skeleton_id: str, misconception_type: str) -> str:
        """Generate options cache key."""
        return f"options:{skeleton_id}:{misconception_type}"

    def get(self, key: str) -> Optional[List[Dict]]:
        """
        Retrieve options from cache.

        Args:
            key: Cache key

        Returns:
            Cached options list or None if not found
        """
        try:
            value = self.redis.get(key)
            if value:
                self.hits += 1
                logger.debug(f"Options Cache HIT: {key}")
                return json.loads(value)
            self.misses += 1
            logger.debug(f"Options Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Options cache get error: {e}")
            self.misses += 1
            return None

    def set(self, key: str, options: List[Dict]) -> bool:
        """
        Store options in cache.

        Args:
            key: Cache key
            options: List of option dictionaries

        Returns:
            True if successful, False otherwise
        """
        try:
            self.redis.setex(
                key,
                int(self.ttl.total_seconds()),
                json.dumps(options, default=str)
            )
            logger.debug(f"Options cached: {key}")
            return True
        except Exception as e:
            logger.error(f"Options cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete specific options from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise
        """
        try:
            deleted = self.redis.delete(key)
            logger.debug(f"Options cache deleted: {key}")
            return deleted > 0
        except Exception as e:
            logger.error(f"Options cache delete error: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all options matching pattern.

        Args:
            pattern: Redis pattern (e.g., "options:skeleton_1:*")

        Returns:
            Number of keys deleted
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                deleted = self.redis.delete(*keys)
                logger.info(f"Invalidated {deleted} options matching pattern {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Options cache invalidation error: {e}")
            return 0

    def clear_all(self) -> int:
        """
        Clear all options cache entries.

        Returns:
            Number of keys deleted
        """
        try:
            keys = self.redis.keys("options:*")
            if keys:
                deleted = self.redis.delete(*keys)
                logger.info(f"Cleared all options cache ({deleted} entries)")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Options cache clear error: {e}")
            return 0

    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        try:
            keys = len(self.redis.keys("options:*"))
            return {
                'cached_option_sets': keys,
                'hits': self.hits,
                'misses': self.misses,
                'total_requests': total,
                'hit_rate_percent': round(hit_rate, 2)
            }
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {
                'error': str(e),
                'hits': self.hits,
                'misses': self.misses
            }


# Singleton instance
_options_cache = None


def get_options_cache(redis_client: redis.Redis = None) -> OptionsCacheManager:
    """Get or create global options cache instance."""
    global _options_cache
    if _options_cache is None:
        _options_cache = OptionsCacheManager(redis_client)
    return _options_cache
