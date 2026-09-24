from unittest.mock import AsyncMock, patch
import pytest
from fastapi import status
from httpx import AsyncClient
from app.api.deps import get_db
from app.core.exceptions import EntityNotFoundException
from app.main import app
from app.schemas.health import ComponentHealth, ReadinessResponse

pytestmark = pytest.mark.asyncio


async def test_root_health_check(client: AsyncClient):
    """Test GET /health returns 200 OK and expected structure."""
    response = await client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert "app_name" in data
    assert "version" in data
    assert "timestamp" in data
    assert data["version"] == "0.1.0"


async def test_api_v1_health_check(client: AsyncClient):
    """Test GET /api/v1/health returns 200 OK."""
    response = await client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


async def test_root_endpoint(client: AsyncClient):
    """Test GET / root metadata endpoint."""
    response = await client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "project" in data
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"
    assert data["api_v1"] == "/api/v1"


async def test_openapi_schema(client: AsyncClient):
    """Test OpenAPI JSON schema endpoint is accessible."""
    response = await client.get("/api/v1/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    schema = response.json()
    assert "openapi" in schema
    assert "paths" in schema
    assert "/health" in schema["paths"]
    assert "/api/v1/health" in schema["paths"]
    assert "/api/v1/health/ready" in schema["paths"]


async def test_readiness_probe_healthy(client: AsyncClient):
    """Test GET /api/v1/health/ready when downstream dependencies are healthy."""
    mock_db = AsyncMock()

    # Override get_db dependency
    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    # Mock HealthService.check_readiness
    mock_readiness = ReadinessResponse(
        status="ready",
        environment="test",
        components={
            "database": ComponentHealth(status="healthy", latency_ms=1.5),
            "redis": ComponentHealth(status="healthy", latency_ms=0.8),
        },
    )

    with patch("app.services.health.HealthService.check_readiness", AsyncMock(return_value=mock_readiness)):
        response = await client.get("/api/v1/health/ready")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ready"
        assert data["components"]["database"]["status"] == "healthy"
        assert data["components"]["redis"]["status"] == "healthy"

    app.dependency_overrides.clear()


async def test_readiness_probe_degraded(client: AsyncClient):
    """Test GET /api/v1/health/ready returns 503 when a dependency is down."""
    mock_db = AsyncMock()

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    mock_readiness = ReadinessResponse(
        status="not_ready",
        environment="test",
        components={
            "database": ComponentHealth(status="unhealthy", latency_ms=2.1, error="Connection refused"),
            "redis": ComponentHealth(status="healthy", latency_ms=0.5),
        },
    )

    with patch("app.services.health.HealthService.check_readiness", AsyncMock(return_value=mock_readiness)):
        response = await client.get("/api/v1/health/ready")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert data["status"] == "not_ready"
        assert data["components"]["database"]["status"] == "unhealthy"

    app.dependency_overrides.clear()


async def test_centralized_exception_handler(client: AsyncClient):
    """Test that custom AppException triggers structured JSON error responses."""
    # Temporarily register an ephemeral test route that raises AppException
    @app.get("/test-error")
    async def raise_test_error():
        raise EntityNotFoundException(entity_name="LandParcel", entity_id="LP-TEST-999")

    response = await client.get("/test-error")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["status"] == "error"
    assert data["error_code"] == "RESOURCE_NOT_FOUND"
    assert "LP-TEST-999" in data["message"]
    assert data["details"]["entity_name"] == "LandParcel"
    assert data["details"]["entity_id"] == "LP-TEST-999"

