import time
from typing import Dict
try:
    from redis import asyncio as aioredis
    _HAS_REDIS = True
except ImportError:
    _HAS_REDIS = False

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import check_db_health
from app.core.logging import get_logger
from app.schemas.health import ComponentHealth, HealthResponse, ReadinessResponse

logger = get_logger(__name__)


class HealthService:
    """Service handling application health, liveness, and dependency readiness probes."""

    @staticmethod
    def get_liveness() -> HealthResponse:
        """Return the basic liveness status of the FastAPI application."""
        return HealthResponse(
            status="ok",
            app_name=settings.PROJECT_NAME,
            version="0.1.0",
            environment=settings.ENVIRONMENT,
        )

    @staticmethod
    async def check_readiness(session: AsyncSession) -> ReadinessResponse:
        """Probe downstream dependencies (PostgreSQL + PostGIS, Redis) to verify readiness."""
        components: Dict[str, ComponentHealth] = {}
        all_ready = True

        # 1. Probe PostgreSQL Database
        db_start = time.perf_counter()
        try:
            db_ok = await check_db_health(session)
            db_latency = (time.perf_counter() - db_start) * 1000
            if db_ok:
                components["database"] = ComponentHealth(
                    status="healthy",
                    latency_ms=round(db_latency, 2),
                )
            else:
                components["database"] = ComponentHealth(
                    status="unhealthy",
                    latency_ms=round(db_latency, 2),
                    error="Database probe query returned unexpected result",
                )
                all_ready = False
        except Exception as exc:
            db_latency = (time.perf_counter() - db_start) * 1000
            components["database"] = ComponentHealth(
                status="unhealthy",
                latency_ms=round(db_latency, 2),
                error=str(exc),
            )
            all_ready = False

        # 2. Probe Redis
        if not _HAS_REDIS:
            components["redis"] = ComponentHealth(
                status="unhealthy",
                latency_ms=0.0,
                error="Redis library not installed in current environment",
            )
        else:
            redis_start = time.perf_counter()
            try:
                redis_client = aioredis.from_url(
                    settings.get_redis_url(),
                    socket_timeout=2.0,
                    decode_responses=True,
                )
                ping_ok = await redis_client.ping()
                await redis_client.aclose()
                redis_latency = (time.perf_counter() - redis_start) * 1000

                if ping_ok:
                    components["redis"] = ComponentHealth(
                        status="healthy",
                        latency_ms=round(redis_latency, 2),
                    )
                else:
                    components["redis"] = ComponentHealth(
                        status="unhealthy",
                        latency_ms=round(redis_latency, 2),
                        error="Redis ping returned False",
                    )
                    all_ready = False
            except Exception as exc:
                redis_latency = (time.perf_counter() - redis_start) * 1000
                components["redis"] = ComponentHealth(
                    status="unhealthy",
                    latency_ms=round(redis_latency, 2),
                    error=str(exc),
                )
                all_ready = False

        return ReadinessResponse(
            status="ready" if all_ready else "not_ready",
            environment=settings.ENVIRONMENT,
            components=components,
        )

