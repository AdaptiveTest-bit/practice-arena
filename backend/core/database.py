"""Database utilities and connection management."""

from sqlalchemy import create_engine, event, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Optional

from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)


# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,  # Test connections before using
    connect_args={"connect_timeout": 10}
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set optimizations on connection."""
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("SET synchronous = 2")  # Full synchronization
        cursor.close()
    except Exception:
        pass  # Not all databases support these pragmas


@event.listens_for(engine, "connect")
def pool_pre_ping(dbapi_conn, connection_record):
    """Verify connection is alive before using."""
    try:
        dbapi_conn.cursor().execute("SELECT 1")
    except Exception as e:
        logger.warning(f"Database connection check failed: {e}")


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session in FastAPI.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()


def init_db(base_metadata=None) -> bool:
    """Initialize database - verify connection and health.
    
    Args:
        base_metadata: Optional SQLAlchemy Base.metadata (for creating new tables if needed)
    
    Returns:
        Success status
    """
    try:
        # Test connection with explicit isolation level
        with engine.connect() as conn:
            conn.connection.rollback()  # Reset any failed transaction state
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection verified")
        
        # Only create tables if base_metadata is provided
        # This is safe because the tables already exist in the production database
        if base_metadata is not None:
            try:
                base_metadata.create_all(bind=engine)
                logger.info("✅ Database tables ensured")
            except Exception as e:
                logger.warning(f"⚠️ Could not auto-create tables (they may already exist): {e}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        return False


def drop_db(base_metadata) -> bool:
    """Drop all tables (use with caution!).
    
    Args:
        base_metadata: SQLAlchemy Base.metadata
    
    Returns:
        Success status
    """
    try:
        base_metadata.drop_all(bind=engine)
        logger.warning("⚠️ All database tables dropped")
        return True
    except Exception as e:
        logger.error(f"❌ Error dropping database: {e}")
        return False


def get_session() -> Session:
    """Get a new database session (non-FastAPI usage).
    
    Returns:
        Database session
    """
    return SessionLocal()


def execute_query(query: str) -> Optional[list]:
    """Execute raw SQL query.
    
    Args:
        query: SQL query string
    
    Returns:
        Query results or None on error
    """
    db = SessionLocal()
    try:
        result = db.execute(text(query))
        db.commit()
        return result.fetchall()
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def get_engine():
    """Get database engine (for migrations, etc.)."""
    return engine
