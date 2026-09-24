from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.logging import get_logger

logger = get_logger(__name__)


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str = "An unexpected internal error occurred.",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_SERVER_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class EntityNotFoundException(AppException):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        entity_name: str,
        entity_id: Any,
        message: Optional[str] = None,
    ):
        super().__init__(
            message=message or f"{entity_name} with identifier '{entity_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details={"entity_name": entity_name, "entity_id": str(entity_id)},
        )


class EntityAlreadyExistsException(AppException):
    """Raised when a resource already exists."""

    def __init__(
        self,
        entity_name: str,
        field: str,
        value: Any,
        message: Optional[str] = None,
    ):
        super().__init__(
            message=message or f"{entity_name} with {field} '{value}' already exists.",
            status_code=status.HTTP_409_CONFLICT,
            error_code="RESOURCE_CONFLICT",
            details={"entity_name": entity_name, "field": field, "value": str(value)},
        )


class ValidationException(AppException):
    """Raised when input validation fails business rules."""

    def __init__(
        self,
        message: str = "Validation failed.",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class UnauthorizedException(AppException):
    """Raised when authentication credentials are missing or invalid."""

    def __init__(self, message: str = "Authentication required."):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
        )


class ForbiddenException(AppException):
    """Raised when the user does not have permission to perform an action."""

    def __init__(self, message: str = "Access forbidden. Insufficient permissions."):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
        )


class DatabaseException(AppException):
    """Raised when database query or transaction fails."""

    def __init__(self, message: str = "A database operation error occurred.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details,
        )


class ServiceUnavailableException(AppException):
    """Raised when a downstream service or resource is unavailable."""

    def __init__(self, service_name: str, message: Optional[str] = None):
        super().__init__(
            message=message or f"Service '{service_name}' is currently unavailable.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="SERVICE_UNAVAILABLE",
            details={"service_name": service_name},
        )


# -------------------------------------------------------------
# FastAPI Exception Handlers
# -------------------------------------------------------------

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    logger.warning(
        f"AppException: [{exc.error_code}] {exc.message} on path {request.url.path}",
        extra={"error_code": exc.error_code, "status_code": exc.status_code, "path": request.url.path}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_code": exc.error_code,
            "message": exc.message,
            "detail": exc.message,
            "details": exc.details,
            "path": str(request.url.path),
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI / Pydantic request validation errors."""
    logger.warning(
        f"Validation error on path {request.url.path}: {exc.errors()}",
        extra={"path": request.url.path}
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "error_code": "REQUEST_VALIDATION_ERROR",
            "message": "Input data validation failed.",
            "details": {"errors": exc.errors()},
            "path": str(request.url.path),
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected unhandled exceptions."""
    logger.error(
        f"Unhandled Exception on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method}
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred on the server.",
            "details": {},
            "path": str(request.url.path),
        },
    )

