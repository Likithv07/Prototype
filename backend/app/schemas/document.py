import uuid
from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

DocumentCategory = Literal[
    "Gazette",
    "Valuation",
    "SIA & Consent",
    "Title Deed",
    "Consent Form",
    "Field Inspection Report",
    "Other",
]


class DocumentVersionRead(BaseModel):
    """Schema for individual document version revisions."""

    id: uuid.UUID
    document_id: str
    version_number: int
    version_label: str
    filename: str
    file_size_bytes: int
    mime_type: str
    checksum_sha256: str
    file_url: str
    changelog: Optional[str] = None
    uploaded_by_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentCreate(BaseModel):
    """Schema for registering a new statutory document."""

    id: Optional[str] = Field(None, description="Optional custom ID (e.g. DOC-2026-001)")
    title: str = Field(..., max_length=255, description="Document title")
    category: DocumentCategory = Field(..., description="Statutory document category")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    parcel_id: Optional[str] = Field(None, description="Associated parcel ID")


class DocumentVersionCreate(BaseModel):
    """Schema for uploading a revised version of an existing document."""

    changelog: Optional[str] = Field(None, description="Reason or notes for this version update")


class DocumentVerificationRequest(BaseModel):
    """Schema for officer verification or rejection of document."""

    is_verified: bool = Field(..., description="True if verified, False if rejected")
    verification_remarks: Optional[str] = Field(None, description="Officer verification remarks")


class DocumentRead(BaseModel):
    """Schema for document master record with embedded version history."""

    id: str
    title: str
    category: str
    project_id: Optional[str] = None
    parcel_id: Optional[str] = None
    uploader_id: uuid.UUID
    uploaded_by: str
    current_version: int
    is_verified: bool
    verified_by_id: Optional[uuid.UUID] = None
    verified_at: Optional[datetime] = None
    verification_remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    versions: List[DocumentVersionRead] = Field(default_factory=list)
    latest_version: Optional[DocumentVersionRead] = None

    class Config:
        from_attributes = True


class DocumentDownloadResponse(BaseModel):
    """Schema for authorized document download metadata."""

    document_id: str
    version_number: int
    filename: str
    mime_type: str
    download_url: str
    checksum_sha256: str

