import uuid
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import status
from httpx import AsyncClient
from app.api.deps import get_current_user, get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.user import Role, User

pytestmark = pytest.mark.asyncio


async def test_register_user_success(client: AsyncClient):
    """Test successful user registration."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    register_payload = {
        "email": "rajesh.patel@bhoomi.gov.in",
        "username": "rajesh_patel",
        "password": "SecurePassword123!",
        "full_name": "Rajesh Patel",
        "phone_number": "+91 98765 43210",
        "state": "Gujarat",
        "district": "Ahmedabad",
        "role_name": "DISTRICT_OFFICER",
    }

    mock_role = Role(id=uuid.uuid4(), name="DISTRICT_OFFICER")
    created_user = User(
        id=uuid.uuid4(),
        email=register_payload["email"],
        username=register_payload["username"],
        hashed_password=hash_password(register_payload["password"]),
        full_name=register_payload["full_name"],
        phone_number=register_payload["phone_number"],
        state=register_payload["state"],
        district=register_payload["district"],
        is_active=True,
        is_verified=True,
    )
    created_user.roles = [mock_role]
    created_user.created_at = "2026-09-23T00:00:00Z"
    created_user.updated_at = "2026-09-23T00:00:00Z"

    with patch("app.repositories.user.UserRepository.seed_system_roles_and_permissions", AsyncMock()):
        with patch("app.repositories.user.UserRepository.get_by_email", AsyncMock(return_value=None)):
            with patch("app.repositories.user.UserRepository.get_by_username", AsyncMock(return_value=None)):
                with patch("app.repositories.user.UserRepository.get_role_by_name", AsyncMock(return_value=mock_role)):
                    with patch("app.repositories.user.UserRepository.get_by_id", AsyncMock(return_value=created_user)):
                        response = await client.post("/api/v1/auth/register", json=register_payload)
                        assert response.status_code == status.HTTP_201_CREATED
                        data = response.json()
                        assert data["email"] == register_payload["email"]
                        assert data["username"] == register_payload["username"]
                        assert "password" not in data
                        assert "hashed_password" not in data
                        assert "DISTRICT_OFFICER" in data["roles"]

    app.dependency_overrides.clear()


async def test_login_invalid_password(client: AsyncClient):
    """Test login failure with wrong password returns 401."""
    mock_db = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    mock_user = User(
        id=uuid.uuid4(),
        email="test@bhoomi.gov.in",
        username="test_officer",
        hashed_password=hash_password("CorrectPassword!"),
        full_name="Test Officer",
        is_active=True,
        is_verified=True,
    )
    mock_user.roles = []

    with patch("app.repositories.user.UserRepository.get_by_username_or_email", AsyncMock(return_value=mock_user)):
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "test_officer", "password": "WrongPassword123"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["error_code"] == "UNAUTHORIZED"

    app.dependency_overrides.clear()


async def test_expired_token_rejection(client: AsyncClient):
    """Test that requests with expired JWT token are rejected with 401."""
    expired_token = create_access_token(
        subject=str(uuid.uuid4()),
        claims={"username": "expired_user"},
        expires_delta=timedelta(seconds=-60),  # In the past
    )

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "expired" in data["message"].lower()


async def test_unauthorized_missing_token(client: AsyncClient):
    """Test accessing protected /auth/me without authorization header returns 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

