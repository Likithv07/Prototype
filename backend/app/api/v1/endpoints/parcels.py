from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.parcel import (
    GeoJSONFeature,
    ParcelCreate,
    ParcelFilter,
    ParcelRead,
    ParcelUpdate,
)
from app.services.parcel import ParcelService

router = APIRouter()


@router.post(
    "",
    response_model=ParcelRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create land parcel",
    description="Register a new cadastral land parcel with optional GeoJSON polygon geometry. Requires official role.",
)
async def create_parcel(
    parcel_in: ParcelCreate,
    current_user: User = Depends(require_role("ADMIN", "CENTRAL_OFFICIAL", "STATE_OFFICIAL", "DISTRICT_OFFICER")),
    db: AsyncSession = Depends(get_db),
) -> ParcelRead:
    """Create parcel."""
    service = ParcelService(db)
    return await service.create_parcel(parcel_in=parcel_in, current_user=current_user)


@router.get(
    "",
    response_model=List[ParcelRead],
    summary="List land parcels",
    description="Fetch land parcels subject to user role and geographic scope (state/district/assigned officer/citizen).",
)
async def list_parcels(
    project_id: Optional[str] = Query(None, description="Filter by parent project ID"),
    state: Optional[str] = Query(None, description="Filter by state"),
    district: Optional[str] = Query(None, description="Filter by district"),
    village: Optional[str] = Query(None, description="Filter by village"),
    acquisition_status: Optional[str] = Query(None, description="Filter by acquisition status"),
    compensation_status: Optional[str] = Query(None, description="Filter by compensation status"),
    possession_status: Optional[str] = Query(None, description="Filter by possession status"),
    land_type: Optional[str] = Query(None, description="Filter by land type"),
    search: Optional[str] = Query(None, description="Search term for survey number or landowner name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ParcelRead]:
    """List parcels."""
    service = ParcelService(db)
    filter_params = ParcelFilter(
        project_id=project_id,
        state=state,
        district=district,
        village=village,
        acquisition_status=acquisition_status,
        compensation_status=compensation_status,
        possession_status=possession_status,
        land_type=land_type,
        search=search,
        skip=skip,
        limit=limit,
    )
    return await service.list_parcels(filter_params=filter_params, current_user=current_user)


@router.get(
    "/{parcel_id}",
    response_model=ParcelRead,
    summary="Get parcel by ID",
    description="Retrieve cadastral land parcel details, spatial polygon representation, and ownership information.",
)
async def get_parcel(
    parcel_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ParcelRead:
    """Get parcel by ID."""
    service = ParcelService(db)
    return await service.get_parcel(parcel_id=parcel_id, current_user=current_user)


@router.put(
    "/{parcel_id}",
    response_model=ParcelRead,
    summary="Update parcel",
    description="Update parcel attributes, status, or GeoJSON spatial boundaries. Requires authorized officer role.",
)
async def update_parcel(
    parcel_id: str,
    parcel_in: ParcelUpdate,
    current_user: User = Depends(
        require_role("ADMIN", "CENTRAL_OFFICIAL", "STATE_OFFICIAL", "DISTRICT_OFFICER", "FIELD_OFFICER")
    ),
    db: AsyncSession = Depends(get_db),
) -> ParcelRead:
    """Update parcel."""
    service = ParcelService(db)
    return await service.update_parcel(
        parcel_id=parcel_id,
        parcel_in=parcel_in,
        current_user=current_user,
    )


@router.get(
    "/{parcel_id}/geojson",
    response_model=GeoJSONFeature,
    summary="Export parcel as GeoJSON Feature",
    description="Return standard RFC 7946 GeoJSON Feature representing the parcel's spatial boundary and attributes.",
)
async def get_parcel_geojson(
    parcel_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GeoJSONFeature:
    """Export GeoJSON."""
    service = ParcelService(db)
    return await service.get_parcel_geojson_feature(parcel_id=parcel_id, current_user=current_user)

