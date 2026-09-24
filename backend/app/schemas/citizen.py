import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class CitizenParcelSummary(BaseModel):
    """Citizen-facing summary of their registered cadastral land parcel."""

    id: str
    survey_number: str
    project_id: str
    project_name: Optional[str] = None
    landowner_name: str
    masked_aadhaar: Optional[str] = None
    state: str
    district: str
    village: str
    area_acres: float
    land_type: str
    acquisition_status: str
    compensation_status: str
    possession_status: str
    market_value_per_acre: Optional[float] = None
    multiplier_factor: Optional[float] = None
    asset_valuation: Optional[float] = None
    total_compensation: Optional[float] = None
    consent_received: Optional[bool] = False
    consent_date: Optional[date] = None
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None
    polygon_coords: Optional[List[List[float]]] = []

    model_config = ConfigDict(from_attributes=True)


class CitizenCompensationDetail(BaseModel):
    """Citizen view of statutory compensation breakdown pursuant to Sections 26-30 of RFCTLARR Act 2013."""

    parcel_id: str
    project_id: str
    survey_number: str
    landowner_name: str
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
    status: str
    rule_version: str

    # Section 31 Award details (if approved)
    award_number: Optional[str] = None
    award_date: Optional[date] = None
    digital_seal_ref: Optional[str] = None
    competent_authority_name: Optional[str] = None
    competent_authority_designation: Optional[str] = None


class CitizenPaymentDetail(BaseModel):
    """Citizen-facing compensation disbursal and PFMS Direct Benefit Transfer (DBT) particulars."""

    parcel_id: str
    landowner_name: str
    total_award_amount: float
    award_status: str
    disbursement_route: str = "Direct Benefit Transfer (DBT)"
    masked_bank_account: Optional[str] = None
    bank_ifsc: str = "SBIN0004128"
    pfms_mandate_id: Optional[str] = None
    payment_status: str
    disbursement_date: Optional[date] = None
    treasury_ref: Optional[str] = None


class CitizenConsentStatus(BaseModel):
    """Citizen-facing status of Aadhaar eSign consent for voluntary acquisition."""

    parcel_id: str
    consent_id: Optional[str] = None
    consent_received: bool
    consent_date: Optional[date] = None
    consent_type: str = "VOLUNTARY_ACQUISITION"
    status: str = "DRAFT"  # DRAFT, SUBMITTED, VERIFIED, REJECTED
    is_esign_completed: bool = False
    document_hash: Optional[str] = None
    esign_timestamp: Optional[datetime] = None


class CitizenNotificationRead(BaseModel):
    """In-app notifications targeted to citizens."""

    id: uuid.UUID
    title: str
    message: str
    category: str
    link_view: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

