from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.token import RefreshTokenRequest, Token
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services.auth import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user account",
    description="Register a new user with secure bcrypt password hashing and default role assignment.",
)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """Register user."""
    auth_service = AuthService(db)
    return await auth_service.register_user(user_in)


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticate user by username or email and password, returning JWT access and refresh tokens.",
)
async def login(
    login_in: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Authenticate user."""
    auth_service = AuthService(db)
    return await auth_service.login(login_in)


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Provide a valid refresh token to rotate credentials and obtain a new access/refresh token pair.",
)
async def refresh_token(
    refresh_in: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Rotate tokens."""
    auth_service = AuthService(db)
    return await auth_service.refresh_token(refresh_in.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Revoke the active JWT authentication token.",
)
async def logout(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Revoke token."""
    token = authorization.split(" ")[1] if " " in authorization else authorization
    auth_service = AuthService(db)
    await auth_service.logout(token)
    return {"status": "success", "message": "Successfully logged out."}


@router.get(
    "/me",
    response_model=UserRead,
    summary="Current user profile",
    description="Fetch the authenticated user's profile, roles, assigned permissions, and geographic jurisdiction.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """Current user profile."""
    auth_service = AuthService(db)
    return await auth_service.get_user_profile(current_user.id)

