import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin


class Grievance(Base, TimestampMixin):
    """Statutory grievance petition filed under RFCTLARR Act 2013 and CPGRAMS mechanism."""

    __tablename__ = "grievances"

    # Business String ID (e.g. 'GRV-2026-TS-00124')
    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)

    # Associated Cadastral Land Parcel & Project
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

    # Petitioner / Citizen Information
    citizen_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    citizen_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    citizen_phone: Mapped[str] = mapped_column(String(30), nullable=False)

    # Grievance Particulars
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )  # Compensation Issue, Land Area Dispute, Ownership Issue, Payment Delay, Incorrect Information, R&R Issue, Other
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Lifecycle & Resolution Status
    status: Mapped[str] = mapped_column(
        String(50),
        default="SUBMITTED",
        nullable=False,
        index=True,
    )  # SUBMITTED, UNDER_REVIEW, OFFICER_ASSIGNED, RESOLVED, REJECTED
    priority: Mapped[str] = mapped_column(
        String(20),
        default="NORMAL",
        nullable=False,
    )  # NORMAL, HIGH, URGENT

    # Officer Assignment
    assigned_officer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assigned_officer_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    assigned_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Formal Resolution Details
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    resolved_by_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Statutory SLA Due Date (Default 30 days)
    sla_due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    parcel = relationship("LandParcel", lazy="selectin")
    project = relationship("Project", lazy="selectin")
    citizen = relationship("User", foreign_keys=[citizen_user_id], lazy="selectin")
    assigned_officer = relationship("User", foreign_keys=[assigned_officer_id], lazy="selectin")
    resolved_by = relationship("User", foreign_keys=[resolved_by_id], lazy="selectin")
    documents: Mapped[List["GrievanceDocument"]] = relationship(
        "GrievanceDocument",
        back_populates="grievance",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    history: Mapped[List["GrievanceHistory"]] = relationship(
        "GrievanceHistory",
        back_populates="grievance",
        cascade="all, delete-orphan",
        order_by="GrievanceHistory.created_at.asc()",
        lazy="selectin",
    )


class GrievanceDocument(Base, UUIDMixin):
    """Supporting affidavit or revenue title document attached to a grievance petition."""

    __tablename__ = "grievance_documents"

    grievance_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("grievances.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), default="application/pdf", nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    uploaded_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    uploaded_by_name: Mapped[str] = mapped_column(String(150), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    grievance = relationship("Grievance", back_populates="documents")


class GrievanceHistory(Base, UUIDMixin):
    """Immutable audit trail for statutory grievance lifecycle transitions and actions."""

    __tablename__ = "grievance_history"

    grievance_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("grievances.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )  # CREATED, ASSIGNED, STATUS_UPDATED, RESOLUTION_ADDED, DOCUMENT_ATTACHED
    from_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    to_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    performed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    performed_by_name: Mapped[str] = mapped_column(String(150), nullable=False)
    performed_by_role: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    grievance = relationship("Grievance", back_populates="history")

