from datetime import date
from typing import Any, Dict, List, Optional
from sqlalchemy import Date, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    """National/State Infrastructure Land Acquisition Project entity."""

    __tablename__ = "projects"

    # User/Business string ID (e.g. 'NLA-TS-2026-001')
    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    ministry: Mapped[str] = mapped_column(String(200), nullable=False)
    implementing_agency: Mapped[str] = mapped_column(String(200), nullable=False)

    # Geographic Scope
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Project Classification & Status
    project_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="Active", nullable=False, index=True)

    # Metrics
    land_required: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # Acres
    land_acquired: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # Acres
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0 to 100 percentage
    budget_cr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # In Crores INR
    compensation_disbursed_cr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Timeline
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expected_completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Workflow & Lifecycle Stages JSON
    lifecycle: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list, nullable=True)

    # Relationship to Land Parcels
    parcels = relationship(
        "LandParcel",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __init__(self, **kwargs):
        if "code" in kwargs and "id" not in kwargs:
            kwargs["id"] = kwargs.pop("code")
        else:
            kwargs.pop("code", None)
        super().__init__(**kwargs)

