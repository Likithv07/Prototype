import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
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


class FieldAssignment(Base, TimestampMixin):
    """Field officer task assignment for on-ground parcel survey and evidence capture."""

    __tablename__ = "field_assignments"

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
    assigned_officer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    assigned_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(String(50), default="High", nullable=False)  # High, Medium, Low
    status: Mapped[str] = mapped_column(String(50), default="Pending", nullable=False, index=True)  # Pending, In Progress, Completed
    required_tasks: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    parcel = relationship("LandParcel", lazy="selectin")
    project = relationship("Project", lazy="selectin")
    assigned_officer = relationship("User", foreign_keys=[assigned_officer_id], lazy="selectin")
    assigned_by = relationship("User", foreign_keys=[assigned_by_id], lazy="selectin")
    photos: Mapped[List["FieldPhoto"]] = relationship(
        "FieldPhoto",
        back_populates="assignment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    documents: Mapped[List["FieldDocument"]] = relationship(
        "FieldDocument",
        back_populates="assignment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class FieldSurveyRecord(Base, TimestampMixin):
    """Detailed ground survey record enumerating physical assets and boundary confirmation."""

    __tablename__ = "field_survey_records"

    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    assignment_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("field_assignments.id", ondelete="SET NULL"),
        nullable=True,
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
    officer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    survey_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    survey_type: Mapped[str] = mapped_column(
        String(100),
        default="Joint Ground Verification",
        nullable=False,
    )
    structures_observed: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    crops_observed: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trees_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wells_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Verification State
    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="Pending",
        nullable=False,
        index=True,
    )  # Pending, Verified, Rejected
    verified_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    parcel = relationship("LandParcel", lazy="selectin")
    officer = relationship("User", foreign_keys=[officer_id], lazy="selectin")
    verified_by = relationship("User", foreign_keys=[verified_by_id], lazy="selectin")


class FieldPhoto(Base, TimestampMixin):
    """Geotagged photographic ground evidence with RTK GPS coordinates and SHA-256 hash."""

    __tablename__ = "field_photos"

    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    parcel_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("land_parcels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assignment_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("field_assignments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    survey_record_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("field_survey_records.id", ondelete="SET NULL"),
        nullable=True,
    )
    uploader_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    officer_name: Mapped[str] = mapped_column(String(150), nullable=False)

    caption: Mapped[str] = mapped_column(String(255), nullable=False)
    photo_type: Mapped[str] = mapped_column(
        String(100),
        default="Boundary Marker",
        nullable=False,
    )  # Boundary Marker, Agricultural Crop, Residential Structure, Commercial Shed

    # Object Storage & Integrity
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    document_hash: Mapped[str] = mapped_column(String(128), index=True, nullable=False)  # SHA-256
    photo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # GPS Geotagging
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    accuracy_meters: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Supervisory Verification
    status: Mapped[str] = mapped_column(
        String(50),
        default="Pending",
        nullable=False,
        index=True,
    )  # Pending, Verified, Rejected
    verified_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    verification_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    assignment = relationship("FieldAssignment", back_populates="photos")
    uploader = relationship("User", foreign_keys=[uploader_id], lazy="selectin")
    verified_by = relationship("User", foreign_keys=[verified_by_id], lazy="selectin")


class FieldDocument(Base, TimestampMixin):
    """Field statutory and verification documents (PDF, deeds, survey reports)."""

    __tablename__ = "field_documents"

    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    parcel_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("land_parcels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assignment_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("field_assignments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    survey_record_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("field_survey_records.id", ondelete="SET NULL"),
        nullable=True,
    )
    uploader_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    uploaded_by: Mapped[str] = mapped_column(String(150), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )  # Land Survey Report, Ownership Document, Consent Form, Field Inspection Report, Other

    # Object Storage & Integrity
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    document_hash: Mapped[str] = mapped_column(String(128), index=True, nullable=False)  # SHA-256
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    version: Mapped[str] = mapped_column(String(50), default="v1.0", nullable=False)

    # Supervisory Verification
    status: Mapped[str] = mapped_column(
        String(50),
        default="Pending",
        nullable=False,
        index=True,
    )  # Pending, Verified, Rejected
    verified_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    verification_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    assignment = relationship("FieldAssignment", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploader_id], lazy="selectin")
    verified_by = relationship("User", foreign_keys=[verified_by_id], lazy="selectin")
