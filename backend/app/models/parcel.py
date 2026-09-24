import uuid
from datetime import date
from typing import Any, Dict, List, Optional
from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Date, Float, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class LandParcel(Base, TimestampMixin):
    """Cadastral Land Parcel entity with PostGIS spatial geometry and ownership linkage."""

    __tablename__ = "land_parcels"

    # Business String ID (e.g. 'TS-HYD-2026-001245')
    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    survey_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Associated Project
    project_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Landowner Details
    landowner_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    landowner_mobile: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    landowner_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    masked_aadhaar: Mapped[Optional[str]] = mapped_column(String(20), index=True, nullable=True)
    masked_bank_account: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Geographic Location Hierarchy
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    village: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Physical & Legal Properties
    area_acres: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    land_type: Mapped[str] = mapped_column(String(50), default="Agricultural", nullable=False, index=True)

    # Lifecycle Statuses
    acquisition_status: Mapped[str] = mapped_column(String(50), default="Proposed", nullable=False, index=True)
    compensation_status: Mapped[str] = mapped_column(String(50), default="Pending", nullable=False, index=True)
    possession_status: Mapped[str] = mapped_column(String(50), default="Not Started", nullable=False, index=True)

    # Valuation & RFCTLARR Metrics
    market_value_per_acre: Mapped[Optional[float]] = mapped_column(Float, default=0.0, nullable=True)
    multiplier_factor: Mapped[Optional[float]] = mapped_column(Float, default=1.0, nullable=True)
    asset_valuation: Mapped[Optional[float]] = mapped_column(Float, default=0.0, nullable=True)
    total_compensation: Mapped[Optional[float]] = mapped_column(Float, default=0.0, nullable=True)
    consent_received: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)
    consent_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    compensation_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True)

    # PostGIS Spatial Polygon (WGS84 SRID 4326) with GIST Index
    geometry: Mapped[Optional[Any]] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, spatial_index=True),
        nullable=True,
    )

    # Centroid coordinates and UI polygon representation
    center_lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    center_lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    polygon_coords: Mapped[Optional[List[List[float]]]] = mapped_column(JSON, default=list, nullable=True)

    # Authorization / Scope Linkages
    owner_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assigned_officer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    project = relationship("Project", back_populates="parcels")
    owner = relationship("User", foreign_keys=[owner_user_id], lazy="selectin")
    assigned_officer = relationship("User", foreign_keys=[assigned_officer_id], lazy="selectin")

