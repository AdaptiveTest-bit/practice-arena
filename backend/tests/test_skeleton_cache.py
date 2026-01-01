"""Tests for Skeleton Cache Manager"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.skeleton_cache import SkeletonCacheManager, get_skeleton_cache


def test_skeleton_cache_basic():
    """Test basic cache operations."""
    cache = SkeletonCacheManager(max_entries=100)

    # Test set
    key = "skeleton:TEST:1:abc123"
    skeleton = {"problem": "1+1", "answer": 2}
    cache.set(key, skeleton, "TEST", 1)

    # Test get
    retrieved = cache.get(key)
    assert retrieved == skeleton
    assert cache.hits == 1


def test_skeleton_cache_miss():
    """Test cache miss."""
    cache = SkeletonCacheManager()
    result = cache.get("nonexistent")
    assert result is None
    assert cache.misses == 1


def test_skeleton_cache_lru_eviction():
    """Test LRU eviction when full."""
    cache = SkeletonCacheManager(max_entries=3)

    # Fill cache
    for i in range(3):
        cache.set(f"key{i}", {"data": i}, "TEST", 1)

    assert len(cache.cache) == 3

    # Access key0 to make it LRU-safe
    cache.get("key0")

    # Add 4th item - should evict key1 (LRU)
    cache.set("key3", {"data": 3}, "TEST", 1)

    assert len(cache.cache) == 3
    assert "key0" in cache.cache
    assert "key1" not in cache.cache


def test_skeleton_cache_stats():
    """Test statistics generation."""
    cache = SkeletonCacheManager()
    cache.set("key1", {"data": 1}, "TEST", 1)
    cache.get("key1")
    cache.get("key1")
    cache.get("nonexistent")

    stats = cache.stats()
    assert stats['hits'] == 2
    assert stats['misses'] == 1
    assert stats['hit_rate_percent'] == 66.67


def test_skeleton_cache_key_generation():
    """Test deterministic key generation."""
    cache = SkeletonCacheManager()

    # Same parameters should generate same key
    key1 = cache.get_key("MATH", 1, {"type": "factor", "number": 12})
    key2 = cache.get_key("MATH", 1, {"type": "factor", "number": 12})

    assert key1 == key2

    # Different parameters should generate different key
    key3 = cache.get_key("MATH", 1, {"type": "factor", "number": 13})
    assert key1 != key3


def test_skeleton_cache_hit_count():
    """Test hit count tracking."""
    cache = SkeletonCacheManager()
    key = "test_key"

    cache.set(key, {"data": 1}, "TEST", 1)

    # Access multiple times
    for _ in range(5):
        cache.get(key)

    assert cache.cache[key].hit_count == 5


def test_skeleton_cache_clear():
    """Test cache clearing."""
    cache = SkeletonCacheManager()

    # Add entries
    for i in range(5):
        cache.set(f"key{i}", {"data": i}, "TEST", 1)

    # Record hits
    cache.get("key0")
    cache.get("key0")

    assert len(cache.cache) == 5
    assert cache.hits == 2

    # Clear
    cache.clear()

    assert len(cache.cache) == 0
    assert cache.hits == 0
    assert cache.misses == 0


def test_singleton_instance():
    """Test that get_skeleton_cache returns singleton."""
    cache1 = get_skeleton_cache()
    cache2 = get_skeleton_cache()

    assert cache1 is cache2


def test_skeleton_cache_chapter_tracking():
    """Test chapter and difficulty tracking."""
    cache = SkeletonCacheManager()

    # Add entries with different chapters/difficulties
    cache.set("key1", {"data": 1}, "CHAPTER_A", 1)
    cache.set("key2", {"data": 2}, "CHAPTER_A", 2)
    cache.set("key3", {"data": 3}, "CHAPTER_B", 1)

    assert cache.cache["key1"].chapter == "CHAPTER_A"
    assert cache.cache["key1"].difficulty == 1
    assert cache.cache["key3"].chapter == "CHAPTER_B"
    assert cache.cache["key3"].difficulty == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
