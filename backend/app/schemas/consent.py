import uuid
from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

ConsentTypeLiteral = Literal[
    "VOLUNTARY_ACQUISITION",
    "COMPENSATION_ACCEPTANCE",
    "RESETTLEMENT_CHOICE",
]

ConsentStatusLiteral = Literal[
    "DRAFT",
    "SUBMITTED",
    "PENDING_VERIFICATION",
    "VERIFIED",
    "REJECTED",
]


class ConsentCreate(BaseModel):
    """Schema for initiating a new landowner consent record."""

    id: Optional[str] = Field(None, description="Optional custom ID (e.g. CONSENT-2026-001)")
    parcel_id: str = Field(..., description="Target cadastral land parcel ID")
    landowner_name: str = Field(..., max_length=200, description="Legal landowner full name")
    landowner_aadhaar_masked: str = Field(
        ...,
        max_length=20,
        description="Masked Aadhaar (e.g. 'XXXX-XXXX-1234') - plaintext UID never stored",
    )
    landowner_phone: Optional[str] = Field(None, max_length=30, description="Contact phone number")
    consent_type: ConsentTypeLiteral = Field(
        "VOLUNTARY_ACQUISITION",
        description="Statutory category under RFCTLARR Act",
    )
    supporting_document_id: Optional[str] = Field(
        None,
        description="Associated statutory document ID (e.g. uploaded signed paper form)",
    )


class ConsentESignInitiateRequest(BaseModel):
    """Schema to request simulated OTP for eSign."""

    consent_id: str = Field(..., description="Target consent record ID")


class ConsentESignVerifyRequest(BaseModel):
    """Schema to verify simulated OTP and complete mock eSign."""

    transaction_id: str = Field(..., description="Active eSign transaction ID")
    otp_code: str = Field(
        ...,
        description="6-digit OTP code (For development/demo, use '781923')",
    )


class ConsentSubmitRequest(BaseModel):
    """Schema to formally submit consent for administrative verification."""

    remarks: Optional[str] = Field(None, description="Submission remarks or statements")


class ConsentVerificationRequest(BaseModel):
    """Schema for officer verification or rejection of landowner consent."""

    action: Literal["VERIFY", "REJECT"] = Field(..., description="Action: VERIFY or REJECT")
    remarks: Optional[str] = Field(None, description="Officer verification notes or rejection reasons")


class ESignInitiateResponse(BaseModel):
    """Response returned upon simulated eSign OTP dispatch."""

    is_mock: bool = True
    provider_name: str
    disclaimer: str
    transaction_id: str
    consent_id: str
    status: str
    message: str


class ESignVerifyResponse(BaseModel):
    """Response returned upon successful simulated OTP verification."""

    is_mock: bool = True
    provider_name: str
    disclaimer: str
    transaction_id: str
    consent_id: str
    status: str
    signer_name: str
    signature_reference: str
    qr_verification_code: str
    message: str


class ConsentHistoryRead(BaseModel):
    """Schema for individual audit trail entry in consent lifecycle."""

    id: uuid.UUID
    consent_id: str
    action: str
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    performed_by_id: Optional[uuid.UUID] = None
    performed_by_name: str
    performed_by_role: str
    remarks: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class ConsentRead(BaseModel):
    """Schema for landowner consent record with full audit history."""

    id: str
    parcel_id: str
    project_id: str
    landowner_user_id: Optional[uuid.UUID] = None
    landowner_name: str
    landowner_aadhaar_masked: str
    landowner_phone: Optional[str] = None
    consent_type: str
    status: str
    submitted_at: Optional[datetime] = None
    supporting_document_id: Optional[str] = None
    esign_simulation_ref: Optional[str] = None
    esign_verified: bool
    qr_verification_code: Optional[str] = None
    document_hash: Optional[str] = None
    verifying_officer_id: Optional[uuid.UUID] = None
    verifying_officer_name: Optional[str] = None
    verified_at: Optional[datetime] = None
    verification_remarks: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    history: List[ConsentHistoryRead] = Field(default_factory=list)

    @property
    def is_verified(self) -> bool:
        return self.status == "VERIFIED"

    class Config:
        from_attributes = True

