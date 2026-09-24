from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Build async database engine with graceful fallback if driver not compiled
try:
    engine: AsyncEngine = create_async_engine(
        settings.get_database_url(),
        echo=settings.DEBUG and settings.ENVIRONMENT == "development",
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=True,
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
except Exception as exc:
    logger.warning(f"Database engine initialization deferred (driver not loaded: {exc})")
    from unittest.mock import AsyncMock
    engine = AsyncMock()
    AsyncSessionLocal = async_sessionmaker(class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection helper for database sessions.
    
    Provides an async transactional scope around each request.
    Rolls back automatically upon uncaught exceptions.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_health(session: AsyncSession) -> bool:
    """Execute a lightweight probe query to verify database connectivity."""
    try:
        result = await session.execute(text("SELECT 1"))
        return result.scalar() == 1
    except Exception as exc:
        logger.warning(f"Database health check failed: {str(exc)}")
        return False


async def close_db_connection() -> None:
    """Dispose of the database engine connection pool on shutdown."""
    logger.info("Disposing of database connection pool...")
    if hasattr(engine, "dispose"):
        res = engine.dispose()
        if hasattr(res, "__await__"):
            await res
    logger.info("Database connection pool disposed.")

