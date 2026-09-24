import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user properties."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=150)
    phone_number: Optional[str] = None
    state: Optional[str] = Field(None, description="Permitted state jurisdiction")
    district: Optional[str] = Field(None, description="Permitted district jurisdiction")
    department: Optional[str] = None
    aadhaar_hash: Optional[str] = None


class UserCreate(UserBase):
    """User registration schema."""

    password: str = Field(..., min_length=6, description="Plaintext password")
    role_name: Optional[str] = Field(default="CITIZEN", description="Primary role to assign")


class UserLogin(BaseModel):
    """User authentication login schema."""

    username: str = Field(..., description="Username or email address")
    password: str = Field(..., description="Account password")


class UserUpdate(BaseModel):
    """User profile update schema."""

    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    """User profile response representation."""

    id: uuid.UUID
    is_active: bool
    is_verified: bool
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

