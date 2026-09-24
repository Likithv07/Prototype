from typing import List, Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=3600, description="Expiration time in seconds")


class TokenPayload(BaseModel):
    """Payload decoded from JWT token."""

    sub: str
    username: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    state: Optional[str] = None
    district: Optional[str] = None
    type: str = "access"
    exp: Optional[int] = None


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""

    refresh_token: str = Field(..., description="Valid JWT refresh token")

