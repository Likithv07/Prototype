import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class FieldAssignmentCreate(BaseModel):
    """Schema to assign a parcel to a field officer."""

    id: Optional[str] = Field(None, description="Optional custom ID (e.g. ASN-2026-091)")
    parcel_id: str = Field(..., description="Target parcel ID")
    assigned_officer_id: uuid.UUID = Field(..., description="Field officer user ID")
    priority: Literal["High", "Medium", "Low"] = "High"
    due_date: Optional[date] = None
    required_tasks: Optional[List[str]] = Field(
        default_factory=lambda: [
            "GPS Geo-tagging",
            "Landowner Aadhaar Verification",
            "Tree & Asset Enumeration",
            "Boundary Pegging",
        ]
    )
    remarks: Optional[str] = None


class FieldAssignmentUpdateStatus(BaseModel):
    """Schema to update assignment status."""

    status: Literal["Pending", "In Progress", "Completed", "Cancelled"] = Field(..., description="New status")
    remarks: Optional[str] = None


class FieldAssignmentRead(BaseModel):
    """Schema for field assignment response."""

    id: str
    parcel_id: str
    project_id: str
    assigned_officer_id: uuid.UUID
    assigned_officer_name: Optional[str] = None
    assigned_by_id: Optional[uuid.UUID] = None
    assigned_date: date
    due_date: Optional[date] = None
    priority: str
    status: str
    required_tasks: List[str] = Field(default_factory=list)
    remarks: Optional[str] = None
    survey_number: Optional[str] = None
    landowner_name: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    project_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FieldSurveyCreate(BaseModel):
    """Schema to submit ground survey enumeration."""

    id: Optional[str] = None
    parcel_id: str
    assignment_id: Optional[str] = None
    survey_type: str = "Joint Ground Verification"
    structures_observed: Optional[str] = None
    crops_observed: Optional[str] = None
    trees_count: int = 0
    wells_count: int = 0
    remarks: Optional[str] = None


class FieldSurveyRead(BaseModel):
    """Schema for field survey record response."""

    id: str
    parcel_id: str
    project_id: str
    assignment_id: Optional[str] = None
    officer_id: uuid.UUID
    officer_name: Optional[str] = None
    survey_date: date
    survey_type: str
    structures_observed: Optional[str] = None
    crops_observed: Optional[str] = None
    trees_count: int
    wells_count: int
    remarks: Optional[str] = None
    verification_status: str
    verified_by_id: Optional[uuid.UUID] = None
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FieldPhotoRead(BaseModel):
    """Schema for field photo ground evidence response."""

    id: str
    parcel_id: str
    assignment_id: Optional[str] = None
    officer_name: str
    caption: str
    photo_type: str
    filename: str
    file_size_bytes: int
    mime_type: str
    document_hash: str
    photo_url: str
    thumbnail_url: Optional[str] = None
    latitude: float
    longitude: float
    accuracy_meters: float
    captured_at: datetime
    status: str
    verified_by_id: Optional[uuid.UUID] = None
    verification_remarks: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FieldDocumentRead(BaseModel):
    """Schema for field document response."""

    id: str
    parcel_id: str
    assignment_id: Optional[str] = None
    uploaded_by: str
    title: str
    category: str
    filename: str
    file_size_bytes: int
    mime_type: str
    document_hash: str
    file_url: str
    version: str
    status: str
    verified_by_id: Optional[uuid.UUID] = None
    verification_remarks: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EvidenceVerificationRequest(BaseModel):
    """Schema for supervisory approval or rejection of field evidence."""

    status: Literal["Verified", "Rejected"] = Field(..., description="'Verified' or 'Rejected'")
    remarks: Optional[str] = Field(None, description="Mandatory remarks if rejected")

