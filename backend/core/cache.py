"""Redis caching utilities for performance optimization."""

import json
import pickle
from typing import Any, Optional, Callable
from functools import wraps
from datetime import timedelta
import asyncio

from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Manages caching operations with optional Redis backend."""
    
    def __init__(self):
        """Initialize cache manager."""
        self.redis_client = None
        self.enabled = settings.ENABLE_CACHING
        
        if self.enabled:
            try:
                import redis
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                logger.info("✅ Redis cache connected")
            except Exception as e:
                logger.warning(f"Redis unavailable, using in-memory cache: {e}")
                self.enabled = False
                self.in_memory_cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None
        """
        if not self.enabled:
            return None
        
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                return self.in_memory_cache.get(key)
        except Exception as e:
            logger.warning(f"Cache get failed for {key}: {e}")
        
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        
        Returns:
            Success status
        """
        if not self.enabled:
            return False
        
        ttl = ttl or settings.CACHE_TTL_SECONDS
        
        try:
            if self.redis_client:
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value, default=str)
                )
            else:
                self.in_memory_cache[key] = value
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Success status
        """
        if not self.enabled:
            return False
        
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.in_memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed for {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "user:*")
        
        Returns:
            Number of keys deleted
        """
        if not self.enabled:
            return 0
        
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
            else:
                count = 0
                keys_to_delete = [
                    k for k in self.in_memory_cache.keys()
                    if self._match_pattern(k, pattern)
                ]
                for k in keys_to_delete:
                    del self.in_memory_cache[k]
                    count += 1
                return count
        except Exception as e:
            logger.warning(f"Cache clear pattern failed: {e}")
        
        return 0
    
    @staticmethod
    def _match_pattern(key: str, pattern: str) -> bool:
        """Simple pattern matching (supports * wildcard)."""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)
    
    def close(self):
        """Close cache connections."""
        if self.redis_client:
            try:
                self.redis_client.close()
                logger.info("Cache connection closed")
            except Exception as e:
                logger.warning(f"Error closing cache: {e}")


# Global cache manager
cache_manager = CacheManager()


def cached(
    key_prefix: str,
    ttl: Optional[int] = None
):
    """Decorator for caching function results.
    
    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds
    
    Example:
        @cached(key_prefix="question", ttl=3600)
        def get_question(question_id: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # Build cache key
            cache_key = f"{key_prefix}:{func.__name__}"
            if args:
                cache_key += f":{':'.join(str(a) for a in args)}"
            if kwargs:
                cache_key += f":{':'.join(f'{k}={v}' for k, v in kwargs.items())}"
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache set: {cache_key}")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            # Build cache key
            cache_key = f"{key_prefix}:{func.__name__}"
            if args:
                cache_key += f":{':'.join(str(a) for a in args)}"
            if kwargs:
                cache_key += f":{':'.join(f'{k}={v}' for k, v in kwargs.items())}"
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache set: {cache_key}")
            
            return result
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def get_cache_manager() -> CacheManager:
    """Get cache manager instance (dependency injection)."""
    return cache_manager
