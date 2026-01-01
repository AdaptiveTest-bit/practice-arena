"""Cache Models - ORM definitions for persistent question caching"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, Index, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class CachedQuestion(Base):
    """
    ORM model for cached questions with warm cache persistence.

    This table stores generated questions for:
    - Warm cache (fallback when Redis is down)
    - Analytics (track which questions are used)
    - Reuse (serve similar students without regeneration)
    """

    __tablename__ = 'cached_questions'

    id = Column(Integer, primary_key=True, index=True)
    
    # Cache key for lookup
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    
    # Question metadata
    chapter = Column(String(100), nullable=False, index=True)
    concept = Column(String(100), nullable=False, index=True)
    difficulty = Column(Integer, nullable=False, index=True)
    
    # Question data (complete JSON)
    question_data = Column(JSON, nullable=False)
    
    # Lifecycle tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    
    # Cache control
    ttl_days = Column(Integer, default=30)
    
    # Usage tracking
    hit_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    
    # Version for cache invalidation
    cache_version = Column(Integer, default=1)
    
    # Status
    is_active = Column(Integer, default=1)
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_chapter_concept_diff', 'chapter', 'concept', 'difficulty'),
        Index('idx_chapter_difficulty', 'chapter', 'difficulty'),
        Index('idx_cache_key_active', 'cache_key', 'is_active'),
    )

    def __repr__(self):
        return f"<CachedQuestion(key={self.cache_key}, chapter={self.chapter}, difficulty={self.difficulty})>"


class CacheStats(Base):
    """
    Track cache performance metrics over time.
    
    Used for analytics and optimization:
    - Hit rate by chapter/difficulty
    - Cache efficiency
    - Invalidation frequency
    """

    __tablename__ = 'cache_stats'

    id = Column(Integer, primary_key=True, index=True)
    
    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Cache layer
    cache_layer = Column(String(50), nullable=False)  # 'skeleton', 'story', 'options', 'question'
    
    # Metrics
    total_entries = Column(Integer, default=0)
    hits = Column(Integer, default=0)
    misses = Column(Integer, default=0)
    hit_rate_percent = Column(Integer, default=0)
    
    # Performance
    avg_lookup_time_ms = Column(Integer, default=0)
    avg_generation_time_ms = Column(Integer, default=0)
    
    # Meta
    metadata_json = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('idx_cache_layer_time', 'cache_layer', 'recorded_at'),
    )

    def __repr__(self):
        return f"<CacheStats(layer={self.cache_layer}, hit_rate={self.hit_rate_percent}%)>"


# Helper function to get database connection
def get_db_connection(database_url: str = None):
    """Get database connection."""
    if database_url is None:
        database_url = "postgresql://kunalranjan@localhost:5432/edtech_mvp"
    
    engine = create_engine(database_url)
    return engine


def create_cache_tables(database_url: str = None):
    """Create cache tables if they don't exist."""
    engine = get_db_connection(database_url)
    Base.metadata.create_all(bind=engine)
    print("✓ Cache tables created/verified")


def get_cache_session(database_url: str = None):
    """Get a database session for cache operations."""
    engine = get_db_connection(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
