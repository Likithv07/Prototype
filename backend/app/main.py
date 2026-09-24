from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import close_db_connection
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging import get_logger, setup_logging
from app.schemas.health import HealthResponse
from app.services.health import HealthService

# Configure structured logging on import
setup_logging()
logger = get_logger("bhoomi_setu")

# Ensure static upload storage directory exists
UPLOAD_STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage" / "uploads"
UPLOAD_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle management for startup and shutdown hooks."""
    logger.info(
        f"Starting {settings.PROJECT_NAME} in [{settings.ENVIRONMENT}] environment..."
    )
    yield
    logger.info("Shutting down application and disposing of resources...")
    await close_db_connection()
    logger.info("Application shutdown complete.")


# Initialize FastAPI instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
# BhoomiSetu - National Land Acquisition & Management Platform
Digital governance backend supporting end-to-end transparent, automated, and legally compliant land acquisition.

### Key Capabilities:
* **Workflow Engine**: 14-stage statutory land acquisition lifecycle management.
* **GIS & Spatial**: PostGIS parcel geometry, boundary conflict detection, GIS overlays.
* **Field Survey & Evidence**: Object-storage decoupled evidence, geotagged photos, SHA-256 hashes, RTK GPS metadata.
* **Compensation & Awards**: RFCTLARR 2013-compliant compensation calculation and awards.
* **Grievance Redressal**: SLA-monitored citizen dispute and grievance tracking.
    """,
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register centralized exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Mount local object-storage static uploads
app.mount("/static/uploads", StaticFiles(directory=str(UPLOAD_STORAGE_DIR)), name="static_uploads")

# Mount API version 1 routers
app.include_router(api_router, prefix=settings.API_V1_STR)


# Top-level Health and Root Routes
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System Health"],
    summary="Root Liveness Probe",
    description="Top-level health check endpoint for container orchestrators and load balancers.",
)
async def root_health() -> HealthResponse:
    """Return application liveness status."""
    return HealthService.get_liveness()


@app.get(
    "/",
    tags=["Root"],
    summary="Application Root",
    description="Root information endpoint providing API metadata and documentation links.",
)
async def root():
    """Application metadata."""
    return {
        "project": settings.PROJECT_NAME,
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "api_v1": settings.API_V1_STR,
    }
