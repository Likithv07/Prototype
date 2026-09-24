import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
    UnauthorizedException,
)
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    revoke_token,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserLogin, UserRead

logger = get_logger(__name__)


class AuthService:
    """Service encapsulating user registration, authentication, and JWT lifecycle."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register_user(self, user_in: UserCreate) -> UserRead:
        """Register a new user account with hashed password and assign default role."""
        # Ensure system roles exist
        await self.user_repo.seed_system_roles_and_permissions()

        # Check for duplicates
        if await self.user_repo.get_by_email(user_in.email):
            raise EntityAlreadyExistsException("User", "email", user_in.email)
        if await self.user_repo.get_by_username(user_in.username):
            raise EntityAlreadyExistsException("User", "username", user_in.username)

        # Hash password securely
        hashed = hash_password(user_in.password)

        user_data = user_in.model_dump(exclude={"password", "role_name"})
        user_data["hashed_password"] = hashed
        db_user = User(**user_data)

        # Assign requested or default role
        target_role_name = (user_in.role_name or "CITIZEN").upper()
        role = await self.user_repo.get_role_by_name(target_role_name)
        if role:
            db_user.roles.append(role)

        self.session.add(db_user)
        await self.session.flush()
        await self.session.refresh(db_user)

        # Re-fetch with eager loaded relationships
        loaded_user = await self.user_repo.get_by_id(db_user.id)
        return self._to_user_read(loaded_user or db_user)

    async def authenticate_user(self, login_in: UserLogin) -> User:
        """Authenticate user by username or email and verify bcrypt password."""
        user = await self.user_repo.get_by_username_or_email(login_in.username)
        if not user:
            raise UnauthorizedException("Invalid username or password.")

        if not verify_password(login_in.password, user.hashed_password):
            raise UnauthorizedException("Invalid username or password.")

        if not user.is_active:
            raise UnauthorizedException("User account is disabled or inactive.")

        return user

    async def login(self, login_in: UserLogin) -> Token:
        """Authenticate user and issue access and refresh tokens."""
        user = await self.authenticate_user(login_in)

        claims = {
            "username": user.username,
            "roles": user.role_names,
            "permissions": user.permission_codes,
            "state": user.state,
            "district": user.district,
        }

        access_token = create_access_token(subject=str(user.id), claims=claims)
        refresh_token = create_refresh_token(subject=str(user.id), claims=claims)

        logger.info(f"User '{user.username}' successfully authenticated.")
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
        )

    async def refresh_token(self, refresh_token_str: str) -> Token:
        """Rotate tokens given a valid refresh token."""
        payload = decode_token(refresh_token_str)
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type. Expected refresh token.")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise UnauthorizedException("Token payload missing subject.")

        user = await self.user_repo.get_by_id(uuid.UUID(user_id_str))
        if not user or not user.is_active:
            raise UnauthorizedException("User associated with token not found or inactive.")

        # Revoke old refresh token (rotation)
        revoke_token(refresh_token_str)

        claims = {
            "username": user.username,
            "roles": user.role_names,
            "permissions": user.permission_codes,
            "state": user.state,
            "district": user.district,
        }

        new_access = create_access_token(subject=str(user.id), claims=claims)
        new_refresh = create_refresh_token(subject=str(user.id), claims=claims)

        return Token(
            access_token=new_access,
            refresh_token=new_refresh,
            token_type="bearer",
            expires_in=3600,
        )

    async def logout(self, token_str: str) -> None:
        """Revoke the current authentication token."""
        revoke_token(token_str)
        logger.info("Token successfully revoked upon logout.")

    async def get_user_profile(self, user_id: uuid.UUID) -> UserRead:
        """Fetch user profile details."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundException("User", user_id)
        return self._to_user_read(user)

    @staticmethod
    def _to_user_read(user: User) -> UserRead:
        return UserRead(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            phone_number=user.phone_number,
            is_active=user.is_active,
            is_verified=user.is_verified,
            state=user.state,
            district=user.district,
            department=user.department,
            aadhaar_hash=user.aadhaar_hash,
            roles=user.role_names,
            permissions=user.permission_codes,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

