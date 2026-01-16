"""Application lifecycle management (startup/shutdown)."""

import asyncio
from contextlib import asynccontextmanager
from typing import Callable, Dict, Any, Optional

from config.logging_config import get_logger, setup_logging
from config.settings import settings
from core.cache import cache_manager

logger = get_logger(__name__)

# Background task reference for Notion sync
_notion_sync_task: Optional[asyncio.Task] = None


class LifecycleManager:
    """Manages application startup and shutdown."""
    
    def __init__(self):
        """Initialize lifecycle manager."""
        self.startup_hooks: Dict[str, Callable] = {}
        self.shutdown_hooks: Dict[str, Callable] = {}
        self.initialized = False
    
    def register_startup(self, name: str, hook: Callable) -> None:
        """Register a startup hook.
        
        Args:
            name: Hook name (for logging)
            hook: Async function to execute
        """
        self.startup_hooks[name] = hook
    
    def register_shutdown(self, name: str, hook: Callable) -> None:
        """Register a shutdown hook.
        
        Args:
            name: Hook name (for logging)
            hook: Async function to execute
        """
        self.shutdown_hooks[name] = hook
    
    async def startup(self) -> bool:
        """Execute all startup hooks.
        
        Returns:
            Success status
        """
        try:
            logger.info("=" * 60)
            logger.info("🚀 Starting application...")
            logger.info("=" * 60)
            
            # Log configuration
            logger.info(
                "Configuration loaded",
                extra={
                    "debug": settings.DEBUG,
                    "host": settings.HOST,
                    "port": settings.PORT,
                    "log_level": settings.LOG_LEVEL,
                    "cache_enabled": settings.ENABLE_CACHING,
                    "database_url": settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "local"
                }
            )
            
            # Execute hooks
            for name, hook in self.startup_hooks.items():
                try:
                    logger.info(f"⚙️  Initializing {name}...")
                    await hook()
                    logger.info(f"✅ {name} initialized")
                except Exception as e:
                    logger.error(f"❌ {name} initialization failed: {e}", exc_info=True)
                    return False
            
            self.initialized = True
            logger.info("=" * 60)
            logger.info("✅ Application started successfully")
            logger.info("=" * 60)
            return True
        
        except Exception as e:
            logger.error(f"Startup failed: {e}", exc_info=True)
            return False
    
    async def shutdown(self) -> bool:
        """Execute all shutdown hooks.
        
        Returns:
            Success status
        """
        try:
            logger.info("=" * 60)
            logger.info("🛑 Shutting down application...")
            logger.info("=" * 60)
            
            # Execute hooks in reverse order
            for name, hook in reversed(list(self.shutdown_hooks.items())):
                try:
                    logger.info(f"⚙️  Cleaning up {name}...")
                    await hook()
                    logger.info(f"✅ {name} cleaned up")
                except Exception as e:
                    logger.error(f"❌ {name} cleanup failed: {e}", exc_info=True)
            
            logger.info("=" * 60)
            logger.info("✅ Application shut down successfully")
            logger.info("=" * 60)
            return True
        
        except Exception as e:
            logger.error(f"Shutdown error: {e}", exc_info=True)
            return False


# Global lifecycle manager
lifecycle_manager = LifecycleManager()


def get_lifecycle_manager() -> LifecycleManager:
    """Get lifecycle manager instance."""
    return lifecycle_manager


@asynccontextmanager
async def lifespan_context(app):
    """FastAPI lifespan context manager.
    
    Usage:
        app = FastAPI(lifespan=lifespan_context)
    """
    # Startup
    success = await lifecycle_manager.startup()
    if not success:
        raise RuntimeError("Application startup failed")
    
    yield
    
    # Shutdown
    await lifecycle_manager.shutdown()
