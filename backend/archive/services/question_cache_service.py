"""Question Cache Service - Dual-layer caching (Redis + PostgreSQL)"""

import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import redis
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class QuestionCacheService:
    """
    Manages complete question caching with dual-layer strategy:
    
    Layer 1 (Hot Cache - Redis):
    - Fast in-memory retrieval (milliseconds)
    - TTL-based expiration
    - High-performance tier
    - 7-day retention
    
    Layer 2 (Warm Cache - PostgreSQL):
    - Persistent storage (backup)
    - Enables service restart without data loss
    - Analytics and auditing
    - 30-day retention
    
    Strategy:
    1. Try Redis (hot cache) first
    2. If miss, try PostgreSQL (warm cache)
    3. If miss in both, generate new
    4. Cache in both layers
    """

    def __init__(
        self,
        redis_client: redis.Redis = None,
        db_session: Session = None,
        redis_ttl_days: int = 7,
        db_ttl_days: int = 30
    ):
        """
        Initialize question cache service.

        Args:
            redis_client: Redis client instance
            db_session: SQLAlchemy session for database
            redis_ttl_days: Redis TTL in days
            db_ttl_days: Database TTL in days
        """
        self.redis = redis_client
        self.db = db_session
        self.redis_ttl = timedelta(days=redis_ttl_days)
        self.db_ttl = timedelta(days=db_ttl_days)
        
        self.hits_redis = 0
        self.hits_db = 0
        self.misses = 0
        
        logger.info(
            f"QuestionCacheService initialized "
            f"(Redis TTL: {redis_ttl_days}d, DB TTL: {db_ttl_days}d)"
        )

    def get_key(self, chapter: str, concept: str, difficulty: int) -> str:
        """Generate cache key."""
        return f"question:{chapter}:{concept}:{difficulty}"

    def get_cached_question(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve question from cache (Redis → PostgreSQL).

        Tries hot cache first, falls back to warm cache.

        Args:
            key: Cache key

        Returns:
            Cached question dict or None if not found
        """
        # Try Redis first (hot cache)
        if self.redis:
            try:
                value = self.redis.get(key)
                if value:
                    self.hits_redis += 1
                    logger.debug(f"Question Cache HIT (Redis): {key}")
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis retrieval failed: {e}")

        # Fall back to PostgreSQL (warm cache)
        if self.db:
            try:
                from models.cache_models import CachedQuestion
                
                question = self.db.query(CachedQuestion).filter_by(
                    cache_key=key,
                    is_active=1
                ).first()
                
                if question:
                    # Check if not expired
                    if question.expires_at and question.expires_at < datetime.utcnow():
                        # Expired, mark as inactive
                        question.is_active = 0
                        self.db.commit()
                        logger.debug(f"Question cache expired: {key}")
                    else:
                        # Valid, update access time and hit count
                        question.last_accessed = datetime.utcnow()
                        question.hit_count = (question.hit_count or 0) + 1
                        self.db.commit()
                        
                        self.hits_db += 1
                        logger.debug(f"Question Cache HIT (PostgreSQL): {key}")
                        return json.loads(question.question_data)
            except Exception as e:
                logger.warning(f"Database retrieval failed: {e}")

        self.misses += 1
        logger.debug(f"Question Cache MISS: {key}")
        return None

    def cache_question(
        self,
        key: str,
        question_data: Dict[str, Any],
        chapter: str,
        concept: str,
        difficulty: int
    ) -> bool:
        """
        Cache question in both Redis and PostgreSQL.

        Args:
            key: Cache key
            question_data: Complete question data
            chapter: Chapter identifier
            concept: Concept name
            difficulty: Difficulty level

        Returns:
            True if successful, False otherwise
        """
        success = True

        # Cache in Redis (hot cache)
        if self.redis:
            try:
                self.redis.setex(
                    key,
                    int(self.redis_ttl.total_seconds()),
                    json.dumps(question_data, default=str)
                )
                logger.debug(f"Question cached in Redis: {key}")
            except Exception as e:
                logger.error(f"Redis caching failed: {e}")
                success = False

        # Cache in PostgreSQL (warm cache)
        if self.db:
            try:
                from models.cache_models import CachedQuestion
                
                # Check if already exists
                existing = self.db.query(CachedQuestion).filter_by(
                    cache_key=key
                ).first()
                
                if existing:
                    # Update existing
                    existing.question_data = json.dumps(question_data)
                    existing.is_active = 1
                    existing.hit_count = 0
                    existing.last_accessed = datetime.utcnow()
                    existing.expires_at = datetime.utcnow() + self.db_ttl
                else:
                    # Create new
                    cached_q = CachedQuestion(
                        cache_key=key,
                        chapter=chapter,
                        concept=concept,
                        difficulty=difficulty,
                        question_data=json.dumps(question_data),
                        created_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + self.db_ttl,
                        ttl_days=30,
                        is_active=1
                    )
                    self.db.add(cached_q)
                
                self.db.commit()
                logger.debug(f"Question cached in PostgreSQL: {key}")
            except Exception as e:
                logger.error(f"Database caching failed: {e}")
                self.db.rollback()
                success = False

        return success

    def invalidate_question(self, key: str) -> bool:
        """
        Invalidate question from both caches.

        Args:
            key: Cache key

        Returns:
            True if successfully invalidated
        """
        success = True

        # Remove from Redis
        if self.redis:
            try:
                self.redis.delete(key)
                logger.debug(f"Invalidated from Redis: {key}")
            except Exception as e:
                logger.warning(f"Redis invalidation failed: {e}")
                success = False

        # Mark as inactive in PostgreSQL
        if self.db:
            try:
                from models.cache_models import CachedQuestion
                
                question = self.db.query(CachedQuestion).filter_by(
                    cache_key=key
                ).first()
                
                if question:
                    question.is_active = 0
                    self.db.commit()
                    logger.debug(f"Invalidated in PostgreSQL: {key}")
            except Exception as e:
                logger.warning(f"Database invalidation failed: {e}")
                success = False

        return success

    def invalidate_concept(self, chapter: str, concept: str) -> int:
        """
        Invalidate all questions for a concept.

        Args:
            chapter: Chapter identifier
            concept: Concept name

        Returns:
            Number of questions invalidated
        """
        count = 0

        if self.db:
            try:
                from models.cache_models import CachedQuestion
                
                questions = self.db.query(CachedQuestion).filter_by(
                    chapter=chapter,
                    concept=concept,
                    is_active=1
                ).all()
                
                for q in questions:
                    # Remove from Redis if available
                    if self.redis:
                        try:
                            self.redis.delete(q.cache_key)
                        except:
                            pass
                    
                    # Mark as inactive in DB
                    q.is_active = 0
                    count += 1
                
                self.db.commit()
                logger.info(f"Invalidated {count} questions for {chapter}/{concept}")
            except Exception as e:
                logger.error(f"Concept invalidation failed: {e}")

        return count

    def cleanup_expired(self) -> int:
        """
        Remove expired questions from PostgreSQL.

        Returns:
            Number of questions cleaned up
        """
        count = 0

        if self.db:
            try:
                from models.cache_models import CachedQuestion
                
                expired = self.db.query(CachedQuestion).filter(
                    CachedQuestion.expires_at < datetime.utcnow(),
                    CachedQuestion.is_active == 1
                ).all()
                
                for q in expired:
                    q.is_active = 0
                    count += 1
                
                self.db.commit()
                logger.info(f"Cleaned up {count} expired questions")
            except Exception as e:
                logger.error(f"Cleanup failed: {e}")

        return count

    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with comprehensive cache stats
        """
        total_requests = self.hits_redis + self.hits_db + self.misses
        hit_rate = (
            ((self.hits_redis + self.hits_db) / total_requests * 100)
            if total_requests > 0
            else 0
        )

        stats = {
            'redis_hits': self.hits_redis,
            'db_hits': self.hits_db,
            'total_hits': self.hits_redis + self.hits_db,
            'misses': self.misses,
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 2)
        }

        # Add database stats
        if self.db:
            try:
                from models.cache_models import CachedQuestion
                
                total_cached = self.db.query(CachedQuestion).filter_by(
                    is_active=1
                ).count()
                stats['cached_in_db'] = total_cached
            except Exception as e:
                logger.warning(f"Could not get DB stats: {e}")

        return stats


# Singleton instance
_question_cache_service = None


def get_question_cache_service(
    redis_client: redis.Redis = None,
    db_session: Session = None
) -> QuestionCacheService:
    """Get or create global question cache service."""
    global _question_cache_service
    if _question_cache_service is None:
        _question_cache_service = QuestionCacheService(redis_client, db_session)
    return _question_cache_service
