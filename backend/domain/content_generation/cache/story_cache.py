"""Story Context Cache Manager - Redis-backed caching for LLM-generated stories"""

import json
import logging
from typing import Optional, Dict, Any
from datetime import timedelta
import redis

logger = logging.getLogger(__name__)


class StoryCacheManager:
    """Manages story caching in Redis."""

    def __init__(self, redis_client: redis.Redis = None, ttl_days: int = 7):
        """
        Initialize story cache manager.

        Args:
            redis_client: Redis client instance (creates default if None)
            ttl_days: Time-to-live for cached stories in days
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
        logger.info(f"StoryCacheManager initialized (TTL: {ttl_days} days)")

    def get_key(self, skeleton_id: str, principle_type: str) -> str:
        """Generate story cache key."""
        return f"story:{skeleton_id}:{principle_type}"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve story from Redis.

        Args:
            key: Cache key

        Returns:
            Cached story dict or None if not found
        """
        try:
            value = self.redis.get(key)
            if value:
                self.hits += 1
                logger.debug(f"Story Cache HIT: {key}")
                return json.loads(value)
            self.misses += 1
            logger.debug(f"Story Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Story cache get error: {e}")
            self.misses += 1
            return None

    def set(self, key: str, story_data: Dict[str, Any]) -> bool:
        """
        Store story in Redis with TTL.

        Args:
            key: Cache key
            story_data: Story data to cache

        Returns:
            True if successful, False otherwise
        """
        try:
            self.redis.setex(
                key,
                int(self.ttl.total_seconds()),
                json.dumps(story_data, default=str)
            )
            logger.debug(f"Story cached: {key}")
            return True
        except Exception as e:
            logger.error(f"Story cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete a specific story from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise
        """
        try:
            deleted = self.redis.delete(key)
            logger.debug(f"Story cache deleted: {key}")
            return deleted > 0
        except Exception as e:
            logger.error(f"Story cache delete error: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all stories matching pattern.

        Args:
            pattern: Redis pattern (e.g., "story:skeleton_1:*")

        Returns:
            Number of keys deleted
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                deleted = self.redis.delete(*keys)
                logger.info(f"Invalidated {deleted} stories matching pattern {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Story cache invalidation error: {e}")
            return 0

    def clear_all(self) -> int:
        """
        Clear all story cache entries.

        Returns:
            Number of keys deleted
        """
        try:
            keys = self.redis.keys("story:*")
            if keys:
                deleted = self.redis.delete(*keys)
                logger.info(f"Cleared all story cache ({deleted} entries)")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Story cache clear error: {e}")
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
            keys = len(self.redis.keys("story:*"))
            return {
                'cached_stories': keys,
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
_story_cache = None


def get_story_cache(redis_client: redis.Redis = None) -> StoryCacheManager:
    """Get or create global story cache instance."""
    global _story_cache
    if _story_cache is None:
        _story_cache = StoryCacheManager(redis_client)
    return _story_cache
