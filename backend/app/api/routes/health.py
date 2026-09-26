from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check")
async def health_check() -> dict[str, str]:
    """Liveness endpoint; database readiness will be added with migrations."""
    return {"status": "ok", "service": "bhoomisetu-api"}
