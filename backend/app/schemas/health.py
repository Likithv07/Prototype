from datetime import datetime, timezone
from typing import Dict, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Liveness probe response model."""

    status: str = Field(default="ok", description="Overall service status ('ok', 'degraded')")
    app_name: str = Field(..., description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    environment: str = Field(..., description="Runtime environment (e.g. development, production)")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of the health check",
    )


class ComponentHealth(BaseModel):
    """Health status of an external dependency component."""

    status: str = Field(..., description="Status ('healthy', 'unhealthy', 'unconfigured')")
    latency_ms: Optional[float] = Field(None, description="Response latency in milliseconds")
    error: Optional[str] = Field(None, description="Error message if probe failed")


class ReadinessResponse(BaseModel):
    """Readiness probe response model including downstream dependencies."""

    status: str = Field(..., description="Service readiness ('ready', 'not_ready')")
    environment: str = Field(..., description="Runtime environment")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of the readiness check",
    )
    components: Dict[str, ComponentHealth] = Field(
        ...,
        description="Status of individual dependencies (database, redis)",
    )

