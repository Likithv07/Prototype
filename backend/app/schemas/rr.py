import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class RrEligibilityBase(BaseModel):
    """Base eligibility attributes under RFCTLARR Act 2013."""

    is_eligible: bool = True
    eligibility_criteria: str = "RFCTLARR Second Schedule - Displaced Family"
    status: str = "PENDING_VERIFICATION"
    remarks: Optional[str] = None


class RrEligibilityCreate(RrEligibilityBase):
    pass


class RrEligibilityRead(RrEligibilityBase):
    id: uuid.UUID
    family_id: str
    verified_by_id: Optional[uuid.UUID] = None
    verified_by_name: Optional[str] = None
    verification_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class RrBenefitBase(BaseModel):
    """Specific R&R entitlement package component."""

    benefit_type: str = Field(
        ...,
        description="HOUSING_ALLOTMENT, LIVELIHOOD_GRANT, SHIFTING_GRANT, JOB_TRAINING, ANNUITY_BOND, etc.",
    )
    description: str
    monetary_value_lakhs: float = 0.0
    housing_colony_name: Optional[str] = None
    housing_unit_number: Optional[str] = None
    remarks: Optional[str] = None


class RrBenefitCreate(RrBenefitBase):
    """Payload to allocate an R&R benefit. Initial benefit_status is always controlled server-side."""
    pass


class RrBenefitDisburseRequest(BaseModel):
    """Payload to disburse an R&R financial benefit."""

    disbursed_amount_lakhs: float = Field(..., gt=0)
    disbursement_ref: str = Field(..., description="PFMS or Treasury reference code")
    remarks: Optional[str] = None


class RrBenefitRead(RrBenefitBase):
    id: uuid.UUID
    family_id: str
    benefit_status: str = "SANCTIONED"
    disbursement_status: str
    disbursed_amount_lakhs: float
    disbursement_date: Optional[date] = None
    disbursement_ref: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AffectedFamilyBase(BaseModel):
    """Demographics and impact particulars for an affected family."""

    head_of_family: str
    aadhaar_masked: Optional[str] = None
    contact_number: Optional[str] = None
    state: str
    district: str
    village: str
    family_members_count: int = 1
    affected_type: str = "Agricultural"
    relocation_status: str = "Pending Rehabilitation"
    total_financial_package_lakhs: float = 0.0
    status: str = "Under Assessment"


class AffectedFamilyCreate(AffectedFamilyBase):
    id: str = Field(..., description="Family ID e.g. FAM-TS-001")
    project_id: str
    parcel_id: Optional[str] = None
    citizen_user_id: Optional[uuid.UUID] = None


class AffectedFamilyRead(AffectedFamilyBase):
    id: str
    project_id: str
    parcel_id: Optional[str] = None
    citizen_user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    eligibility: Optional[RrEligibilityRead] = None
    benefits: List[RrBenefitRead] = []

    model_config = ConfigDict(from_attributes=True)


class AffectedFamilyFilter(BaseModel):
    """Filter parameters for listing affected families."""

    state: Optional[str] = None
    district: Optional[str] = None
    project_id: Optional[str] = None
    status: Optional[str] = None
    affected_type: Optional[str] = None


class ResettlementColonyRead(BaseModel):
    """Model Resettlement Colony metrics and civic amenities."""

    id: str
    name: str
    location: str
    state: str
    district: str
    project_id: str
    allotted_units: int
    completed_units: int
    school_hospital_status: str
    water_electricity_status: str
    livelihood_grants_disbursed_cr: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

