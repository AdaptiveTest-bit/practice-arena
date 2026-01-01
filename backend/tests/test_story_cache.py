"""Tests for Story Cache Manager"""

import pytest
import json
import sys
import os
import redis

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.story_cache import StoryCacheManager, get_story_cache


@pytest.fixture
def redis_client():
    """Create a test Redis client."""
    client = redis.Redis(
        host='localhost',
        port=6379,
        db=15,  # Use test DB
        decode_responses=True
    )
    # Flush test DB before each test
    client.flushdb()
    return client


@pytest.fixture
def cache(redis_client):
    """Create a test cache manager."""
    return StoryCacheManager(redis_client=redis_client, ttl_days=7)


def test_story_cache_basic(cache):
    """Test basic cache operations."""
    key = "story:skeleton_1:real_world"
    story = {
        "text": "Rahul is buying apples...",
        "characters": ["Rahul"],
        "principle": "real_world"
    }

    # Test set
    success = cache.set(key, story)
    assert success is True

    # Test get
    retrieved = cache.get(key)
    assert retrieved == story
    assert cache.hits == 1


def test_story_cache_miss(cache):
    """Test cache miss."""
    result = cache.get("story:nonexistent:principle")
    assert result is None
    assert cache.misses == 1


def test_story_cache_multiple_operations(cache):
    """Test multiple cache operations."""
    # Add 3 stories
    stories = {
        "story:skel_1:real_world": {"text": "Story 1", "principle": "real_world"},
        "story:skel_1:meaningful": {"text": "Story 2", "principle": "meaningful"},
        "story:skel_2:active": {"text": "Story 3", "principle": "active"},
    }

    for key, data in stories.items():
        cache.set(key, data)

    # Retrieve them
    for key, expected_data in stories.items():
        result = cache.get(key)
        assert result == expected_data

    assert cache.hits == 3
    assert cache.misses == 0


def test_story_cache_key_generation(cache):
    """Test cache key generation."""
    key1 = cache.get_key("skeleton_123", "real_world")
    key2 = cache.get_key("skeleton_123", "real_world")
    key3 = cache.get_key("skeleton_123", "meaningful")

    # Same parameters = same key
    assert key1 == key2

    # Different principles = different keys
    assert key1 != key3

    # Key format validation
    assert key1.startswith("story:")
    assert "skeleton_123" in key1
    assert "real_world" in key1


def test_story_cache_delete(cache):
    """Test delete operation."""
    key = "story:skel:principle"
    story = {"text": "Story"}

    # Set and verify
    cache.set(key, story)
    assert cache.get(key) is not None

    # Delete
    deleted = cache.delete(key)
    assert deleted is True

    # Verify deletion
    assert cache.get(key) is None


def test_story_cache_invalidate_pattern(redis_client):
    """Test pattern-based invalidation."""
    cache = StoryCacheManager(redis_client=redis_client)

    # Add stories with different patterns
    cache.set("story:skeleton_1:real_world", {"text": "S1"})
    cache.set("story:skeleton_1:meaningful", {"text": "S2"})
    cache.set("story:skeleton_2:real_world", {"text": "S3"})

    # Invalidate by skeleton
    deleted = cache.invalidate_pattern("story:skeleton_1:*")
    assert deleted == 2

    # Verify skeleton_1 stories are gone
    assert cache.get("story:skeleton_1:real_world") is None
    assert cache.get("story:skeleton_1:meaningful") is None

    # Verify skeleton_2 still exists
    assert cache.get("story:skeleton_2:real_world") is not None


def test_story_cache_clear_all(redis_client):
    """Test clearing entire cache."""
    cache = StoryCacheManager(redis_client=redis_client)

    # Add multiple stories
    for i in range(5):
        cache.set(f"story:skel_{i}:principle", {"text": f"Story {i}"})

    # Clear all
    deleted = cache.clear_all()
    assert deleted == 5

    # Verify all are gone
    for i in range(5):
        assert cache.get(f"story:skel_{i}:principle") is None


def test_story_cache_stats(redis_client):
    """Test statistics tracking."""
    cache = StoryCacheManager(redis_client=redis_client)

    # Add a story
    cache.set("story:skel:principle", {"text": "Story"})

    # Hit it multiple times
    cache.get("story:skel:principle")
    cache.get("story:skel:principle")

    # Miss it
    cache.get("story:nonexistent:principle")

    stats = cache.stats()
    assert stats['cached_stories'] == 1
    assert stats['hits'] == 2
    assert stats['misses'] == 1
    assert stats['total_requests'] == 3
    assert stats['hit_rate_percent'] == 66.67


def test_story_cache_complex_data(cache):
    """Test caching complex nested data."""
    key = "story:complex:test"
    complex_story = {
        "text": "Complex story",
        "characters": ["Rahul", "Priya"],
        "context": {
            "location": "Market",
            "items": ["apples", "mangoes"],
            "prices": {"apples": 10, "mangoes": 20}
        },
        "pedagogy": {
            "principle": "real_world",
            "level": "engage",
            "target_audience": ["5th grade", "6th grade"]
        }
    }

    cache.set(key, complex_story)
    retrieved = cache.get(key)

    assert retrieved == complex_story
    assert retrieved["context"]["prices"]["apples"] == 10


def test_story_cache_json_serialization(cache):
    """Test JSON serialization of special types."""
    key = "story:special:types"
    story = {
        "text": "Story",
        "timestamp": "2025-12-31T12:00:00",
        "tags": ["educational", "math"],
        "metadata": {"version": 1, "active": True}
    }

    cache.set(key, story)
    retrieved = cache.get(key)

    assert retrieved["text"] == "Story"
    assert isinstance(retrieved["tags"], list)
    assert retrieved["metadata"]["active"] is True


def test_story_cache_ttl(redis_client):
    """Test TTL expiration."""
    cache = StoryCacheManager(redis_client=redis_client, ttl_days=7)

    key = "story:skel:principle"
    story = {"text": "Story"}

    cache.set(key, story)

    # Verify TTL is set (should be ~7 days in seconds)
    ttl = redis_client.ttl(key)
    assert ttl > 0  # TTL is set
    assert ttl <= 7 * 24 * 60 * 60  # Less than 7 days in seconds


def test_story_cache_error_handling(redis_client):
    """Test error handling with bad Redis connection."""
    cache = StoryCacheManager(redis_client=redis_client)

    # Create a cache with unreachable Redis
    bad_redis = redis.Redis(
        host='127.0.0.1',
        port=9999,  # Non-existent port
        db=0,
        decode_responses=True,
        socket_connect_timeout=0.1
    )
    bad_cache = StoryCacheManager(redis_client=bad_redis)

    # Operations should fail gracefully
    result = bad_cache.get("story:key:principle")
    assert result is None

    success = bad_cache.set("story:key:principle", {"text": "Story"})
    assert success is False


def test_story_cache_singleton(redis_client):
    """Test singleton pattern."""
    cache1 = get_story_cache(redis_client)
    cache2 = get_story_cache(redis_client)

    assert cache1 is cache2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
