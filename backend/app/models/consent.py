import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin


class LandownerConsent(Base, TimestampMixin):
    """Statutory Landowner Consent record for RFCTLARR Act 2013 compliance."""

    __tablename__ = "landowner_consents"

    # Business String ID (e.g. 'CONSENT-TS-HYD-2026-001245')
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

    # Landowner Identification
    landowner_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    landowner_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    landowner_aadhaar_masked: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    landowner_phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Consent Type & Statutory Status
    consent_type: Mapped[str] = mapped_column(
        String(50),
        default="VOLUNTARY_ACQUISITION",
        nullable=False,
    )  # VOLUNTARY_ACQUISITION, COMPENSATION_ACCEPTANCE, RESETTLEMENT_CHOICE
    status: Mapped[str] = mapped_column(
        String(50),
        default="DRAFT",
        nullable=False,
        index=True,
    )  # DRAFT, SUBMITTED, PENDING_VERIFICATION, VERIFIED, REJECTED

    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Supporting Document Linkage (e.g. Uploaded Signed Form or Title Deed)
    supporting_document_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Electronic Signature Simulation Reference (Development Mock - NOT LIVE UIDAI)
    esign_simulation_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    esign_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    qr_verification_code: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    document_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    # Supervisory Officer Verification
    verifying_officer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    parcel = relationship("LandParcel", lazy="selectin")
    project = relationship("Project", lazy="selectin")
    landowner_user = relationship("User", foreign_keys=[landowner_user_id], lazy="selectin")
    supporting_document = relationship("Document", foreign_keys=[supporting_document_id], lazy="selectin")
    verifying_officer = relationship("User", foreign_keys=[verifying_officer_id], lazy="selectin")
    history: Mapped[List["ConsentHistory"]] = relationship(
        "ConsentHistory",
        back_populates="consent",
        cascade="all, delete-orphan",
        order_by="ConsentHistory.timestamp.asc()",
        lazy="selectin",
    )

    @property
    def is_verified(self) -> bool:
        """Convenience property for verified status."""
        return self.status == "VERIFIED"

    def __init__(self, **kwargs):
        if kwargs.pop("is_verified", False):
            if "status" not in kwargs:
                kwargs["status"] = "VERIFIED"
            if "esign_verified" not in kwargs:
                kwargs["esign_verified"] = True
        kwargs.pop("signed_doc_path", None)
        if "consent_type" not in kwargs or kwargs.get("consent_type") is None:
            kwargs["consent_type"] = "VOLUNTARY_ACQUISITION"
        super().__init__(**kwargs)


class ConsentHistory(Base, UUIDMixin):
    """Immutable audit ledger of every consent lifecycle event."""

    __tablename__ = "consent_history"

    consent_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("landowner_consents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    from_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    to_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

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

    consent = relationship("LandownerConsent", back_populates="history")
    performed_by = relationship("User", foreign_keys=[performed_by_id], lazy="selectin")

