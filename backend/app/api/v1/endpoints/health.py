from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_health_service
from app.schemas.health import HealthResponse, ReadinessResponse
from app.services.health import HealthService

router = APIRouter()


@router.get(
    "",
    response_model=HealthResponse,
    summary="Liveness check",
    description="Returns HTTP 200 if the FastAPI application server is alive and accepting traffic.",
)
async def get_health(
    health_service: HealthService = Depends(get_health_service),
) -> HealthResponse:
    """Check liveness status."""
    return health_service.get_liveness()


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness check",
    description="Probes downstream infrastructure (PostgreSQL database and Redis) to confirm readiness to serve traffic.",
)
async def get_readiness(
    response: Response,
    db: AsyncSession = Depends(get_db),
    health_service: HealthService = Depends(get_health_service),
) -> ReadinessResponse:
    """Check readiness status across core infrastructure dependencies."""
    readiness = await health_service.check_readiness(session=db)
    if readiness.status != "ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return readiness

