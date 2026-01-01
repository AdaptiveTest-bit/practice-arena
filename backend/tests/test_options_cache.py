"""Tests for Options Cache Manager"""

import pytest
import json
import sys
import os
import redis

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.options_cache import OptionsCacheManager, get_options_cache


@pytest.fixture
def redis_client():
    """Create a test Redis client."""
    client = redis.Redis(
        host='localhost',
        port=6379,
        db=14,  # Use different test DB
        decode_responses=True
    )
    # Flush test DB before each test
    client.flushdb()
    return client


@pytest.fixture
def cache(redis_client):
    """Create a test cache manager."""
    return OptionsCacheManager(redis_client=redis_client, ttl_days=7)


def test_options_cache_basic(cache):
    """Test basic cache operations."""
    key = "options:skeleton_1:INCOMPLETE_REASONING"
    options = [
        {"option": "A", "text": "12", "distractor_type": "INCOMPLETE_REASONING"},
        {"option": "B", "text": "24", "distractor_type": "INCOMPLETE_REASONING"},
        {"option": "C", "text": "8", "distractor_type": "INCOMPLETE_REASONING"},
    ]

    # Test set
    success = cache.set(key, options)
    assert success is True

    # Test get
    retrieved = cache.get(key)
    assert retrieved == options
    assert cache.hits == 1


def test_options_cache_miss(cache):
    """Test cache miss."""
    result = cache.get("options:nonexistent:TYPE")
    assert result is None
    assert cache.misses == 1


def test_options_cache_multiple_operations(cache):
    """Test multiple cache operations."""
    options_data = {
        "options:skel_1:INCOMPLETE_REASONING": [
            {"option": "A", "text": "12"},
            {"option": "B", "text": "24"},
        ],
        "options:skel_1:WRONG_OPERATION": [
            {"option": "A", "text": "5"},
            {"option": "B", "text": "15"},
        ],
        "options:skel_2:COMPUTATIONAL_ERROR": [
            {"option": "A", "text": "9"},
            {"option": "B", "text": "18"},
        ],
    }

    for key, data in options_data.items():
        cache.set(key, data)

    # Retrieve them
    for key, expected_data in options_data.items():
        result = cache.get(key)
        assert result == expected_data

    assert cache.hits == 3
    assert cache.misses == 0


def test_options_cache_key_generation(cache):
    """Test cache key generation."""
    key1 = cache.get_key("skeleton_123", "INCOMPLETE_REASONING")
    key2 = cache.get_key("skeleton_123", "INCOMPLETE_REASONING")
    key3 = cache.get_key("skeleton_123", "WRONG_OPERATION")

    # Same parameters = same key
    assert key1 == key2

    # Different misconception types = different keys
    assert key1 != key3

    # Key format validation
    assert key1.startswith("options:")
    assert "skeleton_123" in key1
    assert "INCOMPLETE_REASONING" in key1


def test_options_cache_delete(cache):
    """Test delete operation."""
    key = "options:skel:TYPE"
    options = [{"option": "A", "text": "Value"}]

    # Set and verify
    cache.set(key, options)
    assert cache.get(key) is not None

    # Delete
    deleted = cache.delete(key)
    assert deleted is True

    # Verify deletion
    assert cache.get(key) is None


def test_options_cache_invalidate_pattern(redis_client):
    """Test pattern-based invalidation."""
    cache = OptionsCacheManager(redis_client=redis_client)

    # Add options with different patterns
    cache.set("options:skeleton_1:INCOMPLETE_REASONING", [{"option": "A"}])
    cache.set("options:skeleton_1:WRONG_OPERATION", [{"option": "B"}])
    cache.set("options:skeleton_2:INCOMPLETE_REASONING", [{"option": "C"}])

    # Invalidate by skeleton
    deleted = cache.invalidate_pattern("options:skeleton_1:*")
    assert deleted == 2

    # Verify skeleton_1 options are gone
    assert cache.get("options:skeleton_1:INCOMPLETE_REASONING") is None
    assert cache.get("options:skeleton_1:WRONG_OPERATION") is None

    # Verify skeleton_2 still exists
    assert cache.get("options:skeleton_2:INCOMPLETE_REASONING") is not None


def test_options_cache_clear_all(redis_client):
    """Test clearing entire cache."""
    cache = OptionsCacheManager(redis_client=redis_client)

    # Add multiple option sets
    for i in range(5):
        cache.set(f"options:skel_{i}:MISCONCEPTION", [{"option": "A", "text": f"Value {i}"}])

    # Clear all
    deleted = cache.clear_all()
    assert deleted == 5

    # Verify all are gone
    for i in range(5):
        assert cache.get(f"options:skel_{i}:MISCONCEPTION") is None


def test_options_cache_stats(redis_client):
    """Test statistics tracking."""
    cache = OptionsCacheManager(redis_client=redis_client)

    # Add some options
    cache.set("options:skel:TYPE", [{"option": "A"}])

    # Hit it multiple times
    cache.get("options:skel:TYPE")
    cache.get("options:skel:TYPE")

    # Miss it
    cache.get("options:nonexistent:TYPE")

    stats = cache.stats()
    assert stats['cached_option_sets'] == 1
    assert stats['hits'] == 2
    assert stats['misses'] == 1
    assert stats['total_requests'] == 3
    assert stats['hit_rate_percent'] == 66.67


def test_options_cache_complex_data(cache):
    """Test caching complex nested data."""
    key = "options:complex:test"
    options = [
        {
            "option": "A",
            "text": "12",
            "distractor_type": "INCOMPLETE_REASONING",
            "remediation": "Remember: Multiply all factors",
            "pedagogical_insight": "Student forgot to multiply both numbers"
        },
        {
            "option": "B",
            "text": "24",
            "distractor_type": "WRONG_OPERATION",
            "remediation": "Use multiplication, not addition",
            "pedagogical_insight": "Student added instead of multiplied"
        },
    ]

    cache.set(key, options)
    retrieved = cache.get(key)

    assert retrieved == options
    assert len(retrieved) == 2
    assert retrieved[0]["distractor_type"] == "INCOMPLETE_REASONING"


def test_options_cache_json_serialization(cache):
    """Test JSON serialization of special types."""
    key = "options:special:types"
    options = [
        {
            "option": "A",
            "text": "Value",
            "tags": ["misconception", "math"],
            "metadata": {"version": 1, "active": True}
        }
    ]

    cache.set(key, options)
    retrieved = cache.get(key)

    assert isinstance(retrieved[0]["tags"], list)
    assert retrieved[0]["metadata"]["active"] is True


def test_options_cache_ttl(redis_client):
    """Test TTL expiration."""
    cache = OptionsCacheManager(redis_client=redis_client, ttl_days=7)

    key = "options:skel:principle"
    options = [{"option": "A", "text": "Value"}]

    cache.set(key, options)

    # Verify TTL is set
    ttl = redis_client.ttl(key)
    assert ttl > 0
    assert ttl <= 7 * 24 * 60 * 60


def test_options_cache_misconception_types(cache):
    """Test that cache supports all misconception types."""
    misconception_types = [
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

    # Verify all types are defined
    assert cache.misconception_types == misconception_types

    # Cache options for each type
    for i, mtype in enumerate(misconception_types):
        key = cache.get_key(f"skeleton_{i}", mtype)
        options = [{"option": "A", "type": mtype}]
        cache.set(key, options)

    # Verify all can be retrieved
    for i, mtype in enumerate(misconception_types):
        key = cache.get_key(f"skeleton_{i}", mtype)
        retrieved = cache.get(key)
        assert retrieved is not None


def test_options_cache_singleton(redis_client):
    """Test singleton pattern."""
    cache1 = get_options_cache(redis_client)
    cache2 = get_options_cache(redis_client)

    assert cache1 is cache2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
