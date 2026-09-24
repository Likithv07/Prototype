import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class GeoJSONPolygon(BaseModel):
    """GeoJSON Polygon Geometry definition."""

    type: Literal["Polygon"] = "Polygon"
    coordinates: List[List[List[float]]] = Field(
        ...,
        description="GeoJSON polygon linear rings format: [[[lng, lat], [lng, lat], ...]]",
    )


class GeoJSONFeature(BaseModel):
    """GeoJSON Feature representation."""

    type: Literal["Feature"] = "Feature"
    id: str
    geometry: Optional[GeoJSONPolygon] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class ParcelBase(BaseModel):
    """Base parcel properties matching frontend LandParcel interface."""

    survey_number: str = Field(..., max_length=50, description="e.g. 145/2")
    project_id: str = Field(..., max_length=100, description="Parent project ID (e.g. NLA-TS-2026-001)")
    landowner_name: str = Field(..., max_length=200)
    landowner_mobile: Optional[str] = None
    landowner_address: Optional[str] = None
    masked_aadhaar: Optional[str] = None
    masked_bank_account: Optional[str] = None
    state: str = Field(..., max_length=100)
    district: str = Field(..., max_length=100)
    village: str = Field(..., max_length=100)
    area_acres: float = Field(default=0.0, ge=0.0)
    land_type: str = Field(
        default="Agricultural",
        description="'Agricultural', 'Commercial', 'Residential', 'Barren / Industrial', 'Forest'",
    )
    acquisition_status: str = Field(
        default="Proposed",
        description="'Proposed', 'Notification Issued', 'Under Verification', 'Compensation Pending', 'Land Acquired', 'Disputed', 'Possession Completed'",
    )
    compensation_status: str = Field(
        default="Pending",
        description="'Pending', 'Approved', 'Payment Processing', 'Payment Completed', 'Under Review', 'Disputed'",
    )
    possession_status: str = Field(
        default="Not Started",
        description="'Not Started', 'Demarcated', 'Partial Possession', 'Possession Completed'",
    )
    market_value_per_acre: Optional[float] = 0.0
    multiplier_factor: Optional[float] = 1.0
    asset_valuation: Optional[float] = 0.0
    total_compensation: Optional[float] = 0.0
    consent_received: Optional[bool] = False
    consent_date: Optional[date] = None
    compensation_details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    polygon_coords: Optional[List[List[float]]] = Field(
        default_factory=list,
        description="Canvas/SVG relative coordinate points for frontend visualization",
    )


class ParcelCreate(ParcelBase):
    """Parcel creation schema with optional GeoJSON polygon geometry."""

    id: str = Field(..., min_length=3, max_length=100, description="Identifier (e.g. TS-HYD-2026-001245)")
    geojson: Optional[GeoJSONPolygon] = Field(None, description="Standard PostGIS GeoJSON Polygon")
    owner_user_id: Optional[uuid.UUID] = Field(None, description="Authorized citizen user ID")
    assigned_officer_id: Optional[uuid.UUID] = Field(None, description="Assigned field officer user ID")


class ParcelUpdate(BaseModel):
    """Parcel partial update schema."""

    survey_number: Optional[str] = None
    landowner_name: Optional[str] = None
    landowner_mobile: Optional[str] = None
    landowner_address: Optional[str] = None
    masked_aadhaar: Optional[str] = None
    masked_bank_account: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    area_acres: Optional[float] = None
    land_type: Optional[str] = None
    acquisition_status: Optional[str] = None
    compensation_status: Optional[str] = None
    possession_status: Optional[str] = None
    market_value_per_acre: Optional[float] = None
    multiplier_factor: Optional[float] = None
    asset_valuation: Optional[float] = None
    total_compensation: Optional[float] = None
    consent_received: Optional[bool] = None
    consent_date: Optional[date] = None
    compensation_details: Optional[Dict[str, Any]] = None
    polygon_coords: Optional[List[List[float]]] = None
    geojson: Optional[GeoJSONPolygon] = None
    owner_user_id: Optional[uuid.UUID] = None
    assigned_officer_id: Optional[uuid.UUID] = None


class ParcelRead(ParcelBase):
    """Parcel response representation."""

    id: str
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None
    center: Optional[List[float]] = None
    geojson: Optional[Dict[str, Any]] = None
    owner_user_id: Optional[uuid.UUID] = None
    assigned_officer_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ParcelFilter(BaseModel):
    """Query parameters for parcel search and filtering."""

    project_id: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    acquisition_status: Optional[str] = None
    compensation_status: Optional[str] = None
    possession_status: Optional[str] = None
    land_type: Optional[str] = None
    search: Optional[str] = None
    skip: int = 0
    limit: int = 50

