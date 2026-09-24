from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LifecycleStageSchema(BaseModel):
    """Schema for a project lifecycle workflow stage."""

    id: int
    name: str
    description: str
    status: str = Field(default="Pending", description="'Completed', 'In Progress', 'Pending', 'Delayed'")
    completedDate: Optional[str] = None
    targetDate: Optional[str] = None
    officerInCharge: Optional[str] = None
    delayDays: Optional[int] = None


class ProjectBase(BaseModel):
    """Base project schema matching frontend Project interface."""

    name: str = Field(..., min_length=3, max_length=255)
    ministry: str = Field(..., max_length=200)
    implementing_agency: str = Field(..., max_length=200)
    state: str = Field(..., max_length=100)
    district: str = Field(..., max_length=100)
    project_type: str = Field(..., max_length=100)
    land_required: float = Field(default=0.0, ge=0.0, description="In Acres")
    land_acquired: float = Field(default=0.0, ge=0.0, description="In Acres")
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="0 to 100 percentage")
    status: str = Field(default="Active", description="'Active', 'Under Survey', 'Compensation Stage', 'Possession', 'Completed', 'Delayed'")
    start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    budget_cr: float = Field(default=0.0, ge=0.0, description="Budget in Crores INR")
    compensation_disbursed_cr: float = Field(default=0.0, ge=0.0, description="Compensation disbursed in Crores INR")
    lifecycle: Optional[List[LifecycleStageSchema]] = Field(default_factory=list)


class ProjectCreate(ProjectBase):
    """Project creation schema."""

    id: str = Field(..., min_length=3, max_length=100, description="Identifier (e.g. NLA-TS-2026-001)")


class ProjectUpdate(BaseModel):
    """Project partial update schema."""

    name: Optional[str] = None
    ministry: Optional[str] = None
    implementing_agency: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    project_type: Optional[str] = None
    land_required: Optional[float] = None
    land_acquired: Optional[float] = None
    progress: Optional[float] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    budget_cr: Optional[float] = None
    compensation_disbursed_cr: Optional[float] = None
    lifecycle: Optional[List[LifecycleStageSchema]] = None


class ProjectRead(ProjectBase):
    """Project response representation."""

    id: str
    parcels_count: Optional[int] = Field(default=0, description="Number of associated parcels")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectFilter(BaseModel):
    """Query parameters for project search and filtering."""

    state: Optional[str] = None
    district: Optional[str] = None
    status: Optional[str] = None
    project_type: Optional[str] = None
    search: Optional[str] = None
    skip: int = 0
    limit: int = 50

