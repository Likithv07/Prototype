import uuid
from datetime import date, datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

ComponentTypeLiteral = Literal[
    "LAND",
    "STRUCTURE",
    "TREE",
    "CROP",
    "WELL",
    "BOREWELL",
    "COMMERCIAL",
    "OTHER",
]

AssessmentStatusLiteral = Literal[
    "DRAFT",
    "SUBMITTED",
    "APPROVED",
    "REVISION_REQUESTED",
    "REJECTED",
]


class CompensationCalculateRequest(BaseModel):
    """Interactive compensation calculator input pursuant to Section 26-30 of RFCTLARR Act 2013."""

    land_area_acres: Optional[float] = Field(None, gt=0, description="Acres (defaults to cadastral parcel area)")
    market_value_per_acre: Optional[float] = Field(None, gt=0, description="Unit rate in ₹/acre")
    multiplier_factor: Optional[float] = Field(None, ge=1.0, le=2.0, description="Multiplier factor (1.0 urban to 2.0 rural)")
    asset_valuation: Optional[float] = Field(0.0, ge=0, description="Valuation of structures, trees, crops")
    solatium_percentage: Optional[float] = Field(100.0, ge=0, description="Solatium % (Section 30(1), statutory 100%)")
    interest_percentage: Optional[float] = Field(12.0, ge=0, description="Additional interest % (Section 30(3), statutory 12%)")
    rule_id: Optional[str] = Field(None, description="Optional specific statutory rule ID")


class CompensationBreakdownRead(BaseModel):
    """Calculated breakdown of statutory compensation."""

    land_area_acres: float
    market_value_per_acre: float
    multiplier_factor: float
    asset_valuation: float
    basic_land_value: float
    multiplied_land_value: float
    market_value_plus_assets: float
    solatium_percentage: float
    solatium_amount: float
    interest_percentage: float
    interest_amount: float
    total_compensation: float
    rule_id: str
    rule_version: str


class CompensationComponentCreate(BaseModel):
    """Itemized attached asset component."""

    component_type: ComponentTypeLiteral
    name: str = Field(..., max_length=200, description="Asset description, e.g. 'Residential Brick House'")
    unit: Optional[str] = Field(None, max_length=50, description="Units (Acres, Sq.ft, Trees, Nos)")
    quantity: float = Field(1.0, gt=0)
    rate_per_unit: float = Field(..., ge=0)
    gross_value: Optional[float] = None
    depreciation_percentage: float = Field(0.0, ge=0, le=100)
    net_value: Optional[float] = None
    valuation_date: Optional[date] = None
    remarks: Optional[str] = None


class CompensationComponentRead(BaseModel):
    """Itemized attached asset component read schema."""

    id: uuid.UUID
    assessment_id: str
    component_type: str
    name: str
    unit: Optional[str] = None
    quantity: float
    rate_per_unit: float
    gross_value: float
    depreciation_percentage: float
    net_value: float
    valuation_date: date
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class CompensationAssessmentCreate(BaseModel):
    """Schema to formulate initial compensation assessment."""

    land_area_acres: Optional[float] = Field(None, gt=0)
    market_value_per_acre: Optional[float] = Field(None, gt=0)
    multiplier_factor: Optional[float] = Field(None, ge=1.0, le=2.0)
    asset_valuation: Optional[float] = Field(0.0, ge=0)
    components: Optional[List[CompensationComponentCreate]] = Field(default_factory=list)
    rule_id: Optional[str] = None


class CompensationAssessmentUpdate(BaseModel):
    """Schema to update calculation parameters or attached components while in draft or revision requested."""

    land_area_acres: Optional[float] = Field(None, gt=0)
    market_value_per_acre: Optional[float] = Field(None, gt=0)
    multiplier_factor: Optional[float] = Field(None, ge=1.0, le=2.0)
    asset_valuation: Optional[float] = Field(None, ge=0)
    components: Optional[List[CompensationComponentCreate]] = None
    notes: Optional[str] = None


class AwardApprovalRequest(BaseModel):
    """Schema for supervisory digital DSC approval of Land Acquisition Award."""

    digital_signature_consent: bool = Field(
        ...,
        description="Officer certifies compliance with Section 31 statutory award requirements and survey verification",
    )
    digital_seal_ref: str = Field(
        "NIC-DSC-GOV-2026-9812",
        description="Class-3 DSC Digital Seal identifier",
    )
    approval_remarks: Optional[str] = Field(None, description="Officer statutory remarks")


class RevisionRequest(BaseModel):
    """Schema for supervisory officer requesting revision of compensation assessment."""

    revision_notes: str = Field(
        ...,
        min_length=5,
        description="Statutory reasons and discrepancy notes requiring formulation revision",
    )


class CompensationHistoryRead(BaseModel):
    """Schema for individual audit history ledger entry."""

    id: uuid.UUID
    assessment_id: str
    action: str
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    from_total: Optional[float] = None
    to_total: Optional[float] = None
    performed_by_id: Optional[uuid.UUID] = None
    performed_by_name: str
    performed_by_role: str
    remarks: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class AwardRead(BaseModel):
    """Schema for statutory Land Acquisition Award issued under Section 31."""

    id: str
    assessment_id: str
    parcel_id: str
    project_id: str
    award_number: str
    award_date: date
    competent_authority_id: uuid.UUID
    competent_authority_name: str
    competent_authority_designation: str
    total_awarded_amount: float
    digital_seal_ref: str
    status: str
    gazette_ref: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CompensationAssessmentRead(BaseModel):
    """Comprehensive compensation assessment with components, award, and audit history."""

    id: str
    parcel_id: str
    project_id: str
    landowner_id: Optional[uuid.UUID] = None
    landowner_name: str
    survey_number: str
    rule_id: str
    rule_version: str
    status: str
    land_area_acres: float
    market_value_per_acre: float
    multiplier_factor: float
    asset_valuation: float
    basic_land_value: float
    multiplied_land_value: float
    market_value_plus_assets: float
    solatium_percentage: float
    solatium_amount: float
    interest_percentage: float
    interest_amount: float
    total_compensation: float
    calculated_by_id: uuid.UUID
    submitted_by_id: Optional[uuid.UUID] = None
    submitted_at: Optional[datetime] = None
    submission_notes: Optional[str] = None
    approved_by_id: Optional[uuid.UUID] = None
    approved_at: Optional[datetime] = None
    approval_remarks: Optional[str] = None
    digital_signature_ref: Optional[str] = None
    rejection_reason: Optional[str] = None
    revision_notes: Optional[str] = None
    components: List[CompensationComponentRead] = Field(default_factory=list)
    award: Optional[AwardRead] = None
    history: List[CompensationHistoryRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

