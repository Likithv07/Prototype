import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin


class Document(Base, TimestampMixin):
    """Master statutory and legal document registry."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )  # Gazette, Valuation, SIA & Consent, Title Deed, Consent Form, Field Inspection Report, Other

    # Context Associations
    project_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    parcel_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("land_parcels.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    uploader_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    uploaded_by: Mapped[str] = mapped_column(String(150), nullable=False)

    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Verification State
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    verified_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    project = relationship("Project", lazy="selectin")
    parcel = relationship("LandParcel", lazy="selectin")
    uploader = relationship("User", foreign_keys=[uploader_id], lazy="selectin")
    verified_by = relationship("User", foreign_keys=[verified_by_id], lazy="selectin")
    versions: Mapped[List["DocumentVersion"]] = relationship(
        "DocumentVersion",
        back_populates="document",
        order_by="DocumentVersion.version_number.desc()",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class DocumentVersion(Base, UUIDMixin):
    """Immutable document version revision. Important files are never overwritten."""

    __tablename__ = "document_versions"

    document_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    version_label: Mapped[str] = mapped_column(String(50), nullable=False)  # v1.0, v2.0

    # Storage & Cryptographic Checksum
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)

    changelog: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    document = relationship("Document", back_populates="versions")
    uploaded_by_user = relationship("User", foreign_keys=[uploaded_by_id], lazy="selectin")

