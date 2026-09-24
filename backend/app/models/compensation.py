import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin


class CompensationRule(Base, TimestampMixin):
    """Versioned statutory compensation rules under RFCTLARR Act 2013 and state amendments."""

    __tablename__ = "compensation_rules"

    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    effective_from: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Statutory Percentages & Multipliers
    solatium_percentage: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    additional_interest_percentage: Mapped[float] = mapped_column(Float, default=12.0, nullable=False)
    urban_multiplier: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    rural_multiplier_min: Mapped[float] = mapped_column(Float, default=1.5, nullable=False)
    rural_multiplier_max: Mapped[float] = mapped_column(Float, default=2.0, nullable=False)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    formula_definition: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True)


class CompensationAssessment(Base, TimestampMixin):
    """Statutory compensation assessment for an acquired cadastral land parcel."""

    __tablename__ = "compensation_assessments"

    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    parcel_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("land_parcels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    landowner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    landowner_name: Mapped[str] = mapped_column(String(200), nullable=False)
    survey_number: Mapped[str] = mapped_column(String(50), nullable=False)

    rule_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("compensation_rules.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    rule_version: Mapped[str] = mapped_column(String(50), default="v1.0", nullable=False)

    status: Mapped[str] = mapped_column(
        String(50),
        default="DRAFT",
        nullable=False,
        index=True,
    )  # DRAFT, SUBMITTED, APPROVED, REVISION_REQUESTED, REJECTED

    # Calculation Fields pursuant to Sections 26-30 of RFCTLARR Act 2013
    land_area_acres: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    market_value_per_acre: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    multiplier_factor: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    asset_valuation: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    basic_land_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    multiplied_land_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    market_value_plus_assets: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    solatium_percentage: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    solatium_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    interest_percentage: Mapped[float] = mapped_column(Float, default=12.0, nullable=False)
    interest_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    total_compensation: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Lifecycle & Audit Metadata
    calculated_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    submitted_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    submission_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    digital_signature_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    revision_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    parcel = relationship("LandParcel", lazy="selectin")
    project = relationship("Project", lazy="selectin")
    rule = relationship("CompensationRule", lazy="selectin")
    calculated_by = relationship("User", foreign_keys=[calculated_by_id], lazy="selectin")
    submitted_by = relationship("User", foreign_keys=[submitted_by_id], lazy="selectin")
    approved_by = relationship("User", foreign_keys=[approved_by_id], lazy="selectin")
    components: Mapped[List["CompensationComponent"]] = relationship(
        "CompensationComponent",
        back_populates="assessment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    award: Mapped[Optional["Award"]] = relationship(
        "Award",
        back_populates="assessment",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    history: Mapped[List["CompensationHistory"]] = relationship(
        "CompensationHistory",
        back_populates="assessment",
        cascade="all, delete-orphan",
        order_by="CompensationHistory.timestamp.asc()",
        lazy="selectin",
    )


class CompensationComponent(Base, UUIDMixin):
    """Itemized physical asset attached to land (structures, trees, crops, wells, etc.)."""

    __tablename__ = "compensation_components"

    assessment_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("compensation_assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    component_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # LAND, STRUCTURE, TREE, CROP, WELL, BOREWELL, OTHER
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    quantity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    rate_per_unit: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    gross_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    depreciation_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    net_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    valuation_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    assessment = relationship("CompensationAssessment", back_populates="components")


class Award(Base, TimestampMixin):
    """Legally binding statutory Land Acquisition Award issued under Section 31 of RFCTLARR Act 2013."""

    __tablename__ = "awards"

    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    assessment_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("compensation_assessments.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    parcel_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("land_parcels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    award_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    award_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    competent_authority_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    competent_authority_name: Mapped[str] = mapped_column(String(150), nullable=False)
    competent_authority_designation: Mapped[str] = mapped_column(String(100), nullable=False)

    total_awarded_amount: Mapped[float] = mapped_column(Float, nullable=False)
    digital_seal_ref: Mapped[str] = mapped_column(String(100), nullable=False)  # NIC-DSC-GOV-2026-9812
    status: Mapped[str] = mapped_column(String(50), default="ISSUED", nullable=False, index=True)  # ISSUED, DISBURSED, ANNULLED
    gazette_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    assessment = relationship("CompensationAssessment", back_populates="award")
    parcel = relationship("LandParcel", lazy="selectin")
    project = relationship("Project", lazy="selectin")
    competent_authority = relationship("User", foreign_keys=[competent_authority_id], lazy="selectin")


class CompensationHistory(Base, UUIDMixin):
    """Immutable audit trail of all compensation formulations, revisions, and approval events."""

    __tablename__ = "compensation_history"

    assessment_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("compensation_assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    from_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    to_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    from_total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    to_total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    performed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    performed_by_name: Mapped[str] = mapped_column(String(150), nullable=False)
    performed_by_role: Mapped[str] = mapped_column(String(100), nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    assessment = relationship("CompensationAssessment", back_populates="history")
    performed_by = relationship("User", foreign_keys=[performed_by_id], lazy="selectin")

