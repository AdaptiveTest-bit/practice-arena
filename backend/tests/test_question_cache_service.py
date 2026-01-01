"""Tests for Question Cache Service"""

import pytest
import json
import sys
import os
import redis
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.question_cache_service import QuestionCacheService, get_question_cache_service


@pytest.fixture
def redis_client():
    """Create a test Redis client."""
    client = redis.Redis(
        host='localhost',
        port=6379,
        db=15,  # Use test DB
        decode_responses=True
    )
    client.flushdb()
    return client


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    class MockSession:
        def __init__(self):
            self.data = {}
        
        def query(self, model):
            return self
        
        def filter_by(self, **kwargs):
            return self
        
        def filter(self, *args):
            return self
        
        def first(self):
            return None
        
        def all(self):
            return []
        
        def add(self, obj):
            pass
        
        def commit(self):
            pass
        
        def rollback(self):
            pass
    
    return MockSession()


@pytest.fixture
def cache_service(redis_client, mock_db_session):
    """Create a test cache service."""
    return QuestionCacheService(
        redis_client=redis_client,
        db_session=mock_db_session,
        redis_ttl_days=7,
        db_ttl_days=30
    )


def test_question_cache_basic(cache_service):
    """Test basic cache operations."""
    key = "question:FACTORS:factors:1"
    question = {
        "id": "q1",
        "text": "Find all factors of 12",
        "answer": [1, 2, 3, 4, 6, 12],
        "options": [
            {"text": "[1, 2, 3, 4, 6, 12]", "correct": True},
            {"text": "[2, 4, 6]", "correct": False},
        ]
    }

    # Cache it
    success = cache_service.cache_question(
        key, question, "FACTORS", "factors", 1
    )
    assert success is True

    # Retrieve it
    retrieved = cache_service.get_cached_question(key)
    assert retrieved == question
    assert cache_service.hits_redis == 1


def test_question_cache_miss(cache_service):
    """Test cache miss."""
    result = cache_service.get_cached_question("question:UNKNOWN:concept:5")
    assert result is None
    assert cache_service.misses == 1


def test_question_cache_key_generation(cache_service):
    """Test cache key generation."""
    key1 = cache_service.get_key("CHAPTER_A", "concept_x", 1)
    key2 = cache_service.get_key("CHAPTER_A", "concept_x", 1)
    key3 = cache_service.get_key("CHAPTER_A", "concept_y", 1)

    assert key1 == key2
    assert key1 != key3
    assert "CHAPTER_A" in key1
    assert "concept_x" in key1
    assert "1" in key1


def test_question_cache_multiple_retrievals(redis_client, mock_db_session):
    """Test multiple cache retrievals."""
    cache_service = QuestionCacheService(
        redis_client=redis_client,
        db_session=mock_db_session
    )

    key = "question:test:concept:1"
    question = {"id": "q1", "text": "Test question"}

    # Cache it
    cache_service.cache_question(key, question, "TEST", "concept", 1)

    # Retrieve multiple times
    for _ in range(5):
        result = cache_service.get_cached_question(key)
        assert result == question

    assert cache_service.hits_redis == 5
    assert cache_service.misses == 0


def test_question_cache_stats(redis_client, mock_db_session):
    """Test statistics tracking."""
    cache_service = QuestionCacheService(
        redis_client=redis_client,
        db_session=mock_db_session
    )

    key = "question:test:concept:1"
    question = {"id": "q1", "text": "Test"}

    cache_service.cache_question(key, question, "TEST", "concept", 1)
    cache_service.get_cached_question(key)
    cache_service.get_cached_question(key)
    cache_service.get_cached_question("nonexistent")

    stats = cache_service.stats()
    assert stats['redis_hits'] == 2
    assert stats['misses'] == 1
    assert stats['total_hits'] == 2
    assert stats['hit_rate_percent'] == 66.67


def test_question_cache_complex_data(redis_client, mock_db_session):
    """Test caching complex question data."""
    cache_service = QuestionCacheService(
        redis_client=redis_client,
        db_session=mock_db_session
    )

    key = "question:complex:test:3"
    complex_question = {
        "id": "q_complex",
        "text": "Complex question",
        "metadata": {
            "bloom_level": "ANALYZE",
            "misconceptions": [
                {"type": "INCOMPLETE_REASONING", "description": "Wrong approach"},
                {"type": "COMPUTATIONAL_ERROR", "description": "Math mistake"}
            ],
            "pedagogy": {
                "principle": "real_world",
                "characters": ["Rahul", "Priya"],
                "context": {
                    "location": "Market",
                    "items": [
                        {"name": "Apples", "quantity": 12, "price": 5},
                        {"name": "Mangoes", "quantity": 8, "price": 10}
                    ]
                }
            }
        },
        "options": [
            {
                "text": "Answer 1",
                "correct": True,
                "explanation": "This is correct because..."
            }
        ]
    }

    cache_service.cache_question(key, complex_question, "MATH", "factors", 3)
    retrieved = cache_service.get_cached_question(key)

    assert retrieved == complex_question
    assert retrieved["metadata"]["misconceptions"][0]["type"] == "INCOMPLETE_REASONING"


def test_question_cache_invalidate(redis_client, mock_db_session):
    """Test cache invalidation."""
    cache_service = QuestionCacheService(
        redis_client=redis_client,
        db_session=mock_db_session
    )

    key = "question:test:concept:1"
    question = {"id": "q1", "text": "Test"}

    # Cache it
    cache_service.cache_question(key, question, "TEST", "concept", 1)
    assert cache_service.get_cached_question(key) is not None

    # Invalidate it
    cache_service.invalidate_question(key)

    # Should be gone
    assert cache_service.get_cached_question(key) is None


def test_question_cache_ttl_settings(redis_client, mock_db_session):
    """Test TTL configuration."""
    cache_service = QuestionCacheService(
        redis_client=redis_client,
        db_session=mock_db_session,
        redis_ttl_days=3,
        db_ttl_days=15
    )

    assert cache_service.redis_ttl == timedelta(days=3)
    assert cache_service.db_ttl == timedelta(days=15)


def test_question_cache_json_serialization(redis_client, mock_db_session):
    """Test JSON serialization of special types."""
    cache_service = QuestionCacheService(
        redis_client=redis_client,
        db_session=mock_db_session
    )

    key = "question:json:test:1"
    question = {
        "id": "q1",
        "text": "Test",
        "timestamp": datetime.utcnow().isoformat(),
        "numbers": [1, 2, 3],
        "nested": {
            "bool_value": True,
            "null_value": None
        }
    }

    cache_service.cache_question(key, question, "TEST", "concept", 1)
    retrieved = cache_service.get_cached_question(key)

    assert retrieved["numbers"] == [1, 2, 3]
    assert retrieved["nested"]["bool_value"] is True


def test_question_cache_singleton(redis_client, mock_db_session):
    """Test singleton pattern."""
    service1 = get_question_cache_service(redis_client, mock_db_session)
    service2 = get_question_cache_service(redis_client, mock_db_session)

    assert service1 is service2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
