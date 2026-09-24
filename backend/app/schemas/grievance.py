import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class GrievanceBase(BaseModel):
    """Base fields for statutory grievance petitions."""

    category: str = Field(
        ...,
        description="Grievance Category (Compensation Issue, Land Area Dispute, Ownership Issue, Payment Delay, R&R Issue, etc.)",
    )
    subject: str = Field(..., max_length=255)
    description: str = Field(...)
    priority: str = Field("NORMAL", description="Priority level: NORMAL, HIGH, URGENT")


class GrievanceCreate(GrievanceBase):
    """Payload to lodge a formal grievance petition."""

    parcel_id: str = Field(..., description="Cadastral Land Parcel ID (e.g. TS-HYD-2026-001245)")
    citizen_name: str = Field(..., max_length=200)
    citizen_phone: str = Field(..., max_length=30)


class GrievanceAssignRequest(BaseModel):
    """Payload for allocating a grievance to an administrative officer."""

    assigned_officer_id: uuid.UUID
    notes: Optional[str] = None


class GrievanceStatusUpdateRequest(BaseModel):
    """Payload for updating grievance lifecycle status."""

    status: str = Field(
        ...,
        description="SUBMITTED, UNDER_REVIEW, OFFICER_ASSIGNED, RESOLVED, REJECTED",
    )
    notes: Optional[str] = None


class GrievanceResolutionRequest(BaseModel):
    """Payload for recording formal hearing findings and resolution."""

    resolution_notes: str = Field(..., min_length=5)


class GrievanceDocumentRead(BaseModel):
    """Supporting affidavit or revenue title document representation."""

    id: uuid.UUID
    grievance_id: str
    document_name: str
    file_size_bytes: int
    mime_type: str
    sha256_hash: str
    uploaded_by_name: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GrievanceHistoryRead(BaseModel):
    """Audit log entry for grievance actions and transitions."""

    id: uuid.UUID
    grievance_id: str
    action: str
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    performed_by_id: Optional[uuid.UUID] = None
    performed_by_name: str
    performed_by_role: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GrievanceRead(GrievanceBase):
    """Full representation of a statutory grievance petition."""

    id: str
    parcel_id: str
    project_id: str
    citizen_user_id: Optional[uuid.UUID] = None
    citizen_name: str
    citizen_phone: str
    status: str
    assigned_officer_id: Optional[uuid.UUID] = None
    assigned_officer_name: Optional[str] = None
    assigned_date: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    resolved_by_name: Optional[str] = None
    resolved_at: Optional[datetime] = None
    sla_due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    documents: List[GrievanceDocumentRead] = []
    history: List[GrievanceHistoryRead] = []

    model_config = ConfigDict(from_attributes=True)


class GrievanceFilter(BaseModel):
    """Query filter parameters for listing grievances."""

    status: Optional[str] = None
    category: Optional[str] = None
    parcel_id: Optional[str] = None
    project_id: Optional[str] = None
    district: Optional[str] = None

