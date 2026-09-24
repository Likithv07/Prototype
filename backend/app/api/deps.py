import uuid
from typing import AsyncGenerator, Callable, List, Optional, Tuple
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db as _get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token
from app.models.parcel import LandParcel
from app.models.project import Project
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.health import HealthService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider for database session."""
    async for session in _get_db():
        yield session


def get_health_service() -> HealthService:
    """Dependency provider for HealthService."""
    return HealthService()


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI dependency to authenticate and resolve the current User entity from JWT Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("Missing or malformed Authorization header. Expected 'Bearer <token>'.")

    token = authorization.split(" ")[1]
    payload = decode_token(token)

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Token payload missing subject identifier.")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid user identifier in token.")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UnauthorizedException("User account not found.")

    if not user.is_active:
        raise UnauthorizedException("User account has been deactivated.")

    return user


def require_role(*allowed_roles: str) -> Callable[[User], User]:
    """Reusable dependency ensuring the authenticated user possesses at least one of the specified roles."""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_roles = set(r.upper() for r in current_user.role_names)
        target_roles = set(r.upper() for r in allowed_roles)

        # ADMIN always has superuser bypass
        if "ADMIN" in user_roles or bool(user_roles & target_roles):
            return current_user

        raise ForbiddenException(
            f"Access denied. Requires one of roles: {list(allowed_roles)}. Assigned: {current_user.role_names}"
        )

    return role_checker


def require_permission(*required_perms: str) -> Callable[[User], User]:
    """Reusable dependency ensuring the authenticated user has all specified permissions (or admin:all)."""

    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        granted_codes = set(current_user.permission_codes)

        # Admin wildcard
        if "admin:all" in granted_codes:
            return current_user

        missing = [p for p in required_perms if p not in granted_codes]
        if missing:
            raise ForbiddenException(
                f"Access denied. Missing required permissions: {missing}"
            )

        return current_user

    return permission_checker


class ScopeChecker:
    """Enforces geographic and organizational multi-tier scope policies."""

    @staticmethod
    def get_query_scope(user: User) -> Tuple[Optional[List[str]], Optional[List[str]], Optional[uuid.UUID], Optional[uuid.UUID]]:
        """Return (allowed_states, allowed_districts, assigned_officer_id, owner_user_id) for query filtering."""
        roles = set(user.role_names)

        # 1. National Scope: ADMIN and CENTRAL_OFFICIAL
        if "ADMIN" in roles or "CENTRAL_OFFICIAL" in roles:
            return None, None, None, None

        # 2. State Scope: STATE_OFFICIAL
        if "STATE_OFFICIAL" in roles:
            states = [user.state] if user.state else []
            return states, None, None, None

        # 3. District Scope: DISTRICT_OFFICER
        if "DISTRICT_OFFICER" in roles:
            states = [user.state] if user.state else []
            districts = [user.district] if user.district else []
            return states, districts, None, None

        # 4. Field Assignment Scope: FIELD_OFFICER
        if "FIELD_OFFICER" in roles:
            return None, None, user.id, None

        # 5. Citizen Scope: CITIZEN
        if "CITIZEN" in roles:
            return None, None, None, user.id

        # Fallback to no records
        return [], [], None, None

    @staticmethod
    def verify_project_access(user: User, project: Project) -> None:
        """Verify user is permitted to view or manage a specific Project."""
        roles = set(user.role_names)

        if "ADMIN" in roles or "CENTRAL_OFFICIAL" in roles:
            return

        if "STATE_OFFICIAL" in roles:
            if not user.state or project.state.strip().lower() != user.state.strip().lower():
                raise ForbiddenException(
                    f"Access denied. Project is in state '{project.state}', but officer jurisdiction is '{user.state}'."
                )
            return

        if "DISTRICT_OFFICER" in roles:
            state_match = bool(user.state and project.state.strip().lower() == user.state.strip().lower())
            district_match = bool(user.district and project.district.strip().lower() == user.district.strip().lower())
            if not (state_match and district_match):
                raise ForbiddenException(
                    f"Access denied. Project is in '{project.district}, {project.state}', but officer jurisdiction is '{user.district}, {user.state}'."
                )
            return

        # CITIZEN / FIELD_OFFICER have general read access to project overview
        return

    @staticmethod
    def verify_parcel_access(user: User, parcel: LandParcel) -> None:
        """Verify user is permitted to view or manage a specific Land Parcel."""
        roles = set(user.role_names)

        if "ADMIN" in roles or "CENTRAL_OFFICIAL" in roles:
            return

        if "STATE_OFFICIAL" in roles:
            if not user.state or parcel.state.strip().lower() != user.state.strip().lower():
                raise ForbiddenException(
                    f"Access denied. Parcel is in state '{parcel.state}', but officer jurisdiction is '{user.state}'."
                )
            return

        if "DISTRICT_OFFICER" in roles:
            state_match = bool(user.state and parcel.state.strip().lower() == user.state.strip().lower())
            district_match = bool(user.district and parcel.district.strip().lower() == user.district.strip().lower())
            if not (state_match and district_match):
                raise ForbiddenException(
                    f"Access denied. Parcel is in '{parcel.district}, {parcel.state}', but officer jurisdiction is '{user.district}, {user.state}'."
                )
            return

        if "FIELD_OFFICER" in roles:
            if parcel.assigned_officer_id != user.id:
                raise ForbiddenException(
                    f"Access denied. Field officer is not assigned to parcel '{parcel.id}'."
                )
            return

        if "CITIZEN" in roles:
            if parcel.owner_user_id == user.id:
                return
            raise ForbiddenException(
                "Access denied. Citizens can only access their authorized land parcels."
            )

        raise ForbiddenException("Access denied.")
