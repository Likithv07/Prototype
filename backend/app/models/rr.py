import uuid
from datetime import date, datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin


class AffectedFamily(Base, TimestampMixin):
    """Project-Affected Family (PAF) registered under Second Schedule of RFCTLARR Act 2013."""

    __tablename__ = "affected_families"

    # Business String ID (e.g. 'FAM-TS-001')
    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)

    # Associated Project & Cadastral Parcel
    project_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parcel_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("land_parcels.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Linked Citizen User Account (for scoped citizen access)
    citizen_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Demographics & Identification
    head_of_family: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    aadhaar_masked: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    contact_number: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Geographic Location
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    village: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Affected Profile & Census
    family_members_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    affected_type: Mapped[str] = mapped_column(
        String(50),
        default="Agricultural",
        nullable=False,
        index=True,
    )  # Agricultural, Homestead & Land, Commercial, Tenant
    relocation_status: Mapped[str] = mapped_column(
        String(50),
        default="Pending Rehabilitation",
        nullable=False,
        index=True,
    )  # Rehabilitated, Pending Rehabilitation, Allotment in Progress

    # Financial Package Summary
    total_financial_package_lakhs: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default="Under Assessment",
        nullable=False,
        index=True,
    )  # Active, Disbursed, Under Assessment

    # Relationships
    project = relationship("Project", lazy="selectin")
    parcel = relationship("LandParcel", lazy="selectin")
    citizen = relationship("User", foreign_keys=[citizen_user_id], lazy="selectin")
    eligibility: Mapped[Optional["RrEligibility"]] = relationship(
        "RrEligibility",
        back_populates="family",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    benefits: Mapped[List["RrBenefit"]] = relationship(
        "RrBenefit",
        back_populates="family",
        cascade="all, delete-orphan",
        order_by="RrBenefit.created_at.asc()",
        lazy="selectin",
    )


class RrEligibility(Base, UUIDMixin):
    """Statutory eligibility assessment for R&R entitlements under RFCTLARR 2013."""

    __tablename__ = "rr_eligibilities"

    family_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("affected_families.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    is_eligible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    eligibility_criteria: Mapped[str] = mapped_column(
        String(255),
        default="RFCTLARR Second Schedule - Displaced Family",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING_VERIFICATION",
        nullable=False,
        index=True,
    )  # PENDING_VERIFICATION, VERIFIED, INELIGIBLE

    verified_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    verified_by_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    verification_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    family = relationship("AffectedFamily", back_populates="eligibility")
    verified_by = relationship("User", foreign_keys=[verified_by_id], lazy="selectin")


class RrBenefit(Base, UUIDMixin):
    """Specific R&R entitlement package component (Housing, Shifting, Subsistence, Livelihood)."""

    __tablename__ = "rr_benefits"

    family_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("affected_families.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    benefit_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )  # HOUSING_ALLOTMENT, LIVELIHOOD_GRANT, SHIFTING_GRANT, JOB_TRAINING, ANNUITY_BOND, COMMERCIAL_SHOP
    description: Mapped[str] = mapped_column(Text, nullable=False)
    monetary_value_lakhs: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Housing Allotment Particulars (if applicable)
    housing_colony_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    housing_unit_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Entitlement & Disbursement Status
    benefit_status: Mapped[str] = mapped_column(
        String(50),
        default="SANCTIONED",
        nullable=False,
        index=True,
    )  # SANCTIONED, ALLOTTED, UNDER_REVIEW, CANCELLED
    disbursement_status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        nullable=False,
        index=True,
    )  # PENDING, PARTIALLY_DISBURSED, DISBURSED
    disbursed_amount_lakhs: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    disbursement_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    disbursement_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    family = relationship("AffectedFamily", back_populates="benefits")


class ResettlementColony(Base, TimestampMixin):
    """Model Resettlement Colony providing civic amenities under Third Schedule of RFCTLARR Act 2013."""

    __tablename__ = "resettlement_colonies"

    # Business String ID (e.g. 'COLONY-TS-001')
    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    project_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Capacity & Construction Metrics
    allotted_units: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_units: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    school_hospital_status: Mapped[str] = mapped_column(String(100), default="Operational", nullable=False)
    water_electricity_status: Mapped[str] = mapped_column(String(100), default="100% Commissioned", nullable=False)
    livelihood_grants_disbursed_cr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    project = relationship("Project", lazy="selectin")

