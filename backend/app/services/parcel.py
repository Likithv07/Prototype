from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import ScopeChecker
from app.core.exceptions import EntityAlreadyExistsException, EntityNotFoundException, ForbiddenException
from app.core.logging import get_logger
from app.models.parcel import LandParcel
from app.models.user import User
from app.repositories.parcel import ParcelRepository
from app.repositories.project import ProjectRepository
from app.schemas.parcel import (
    GeoJSONFeature,
    GeoJSONPolygon,
    ParcelCreate,
    ParcelFilter,
    ParcelRead,
    ParcelUpdate,
)

logger = get_logger(__name__)


class ParcelService:
    """Service handling LandParcel operations with PostGIS spatial geometry and scope policies."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.parcel_repo = ParcelRepository(session)
        self.project_repo = ProjectRepository(session)

    async def create_parcel(self, parcel_in: ParcelCreate, current_user: User) -> ParcelRead:
        """Create new land parcel with geometry and jurisdictional validation."""
        # Verify parent project exists
        project = await self.project_repo.get_by_id(parcel_in.project_id)
        if not project:
            raise EntityNotFoundException("Project", parcel_in.project_id)

        # Check duplicate
        existing = await self.parcel_repo.get_by_id(parcel_in.id)
        if existing:
            raise EntityAlreadyExistsException("LandParcel", "id", parcel_in.id)

        # Enforce jurisdictional creation rights
        roles = set(current_user.role_names)
        if "STATE_OFFICIAL" in roles and current_user.state:
            if parcel_in.state.strip().lower() != current_user.state.strip().lower():
                raise ForbiddenException(
                    f"State officials can only register parcels within '{current_user.state}'."
                )

        if "DISTRICT_OFFICER" in roles and current_user.district:
            if parcel_in.district.strip().lower() != current_user.district.strip().lower():
                raise ForbiddenException(
                    f"District officers can only register parcels within '{current_user.district}'."
                )

        db_parcel = await self.parcel_repo.create_with_geometry(parcel_in=parcel_in)
        logger.info(f"Parcel '{db_parcel.id}' created under project '{parcel_in.project_id}'.")
        return self._to_read_schema(db_parcel)

    async def get_parcel(self, parcel_id: str, current_user: User) -> ParcelRead:
        """Fetch parcel by ID with spatial geometry and scope validation."""
        parcel = await self.parcel_repo.get_by_id(parcel_id)
        if not parcel:
            raise EntityNotFoundException("LandParcel", parcel_id)

        ScopeChecker.verify_parcel_access(current_user, parcel)
        return self._to_read_schema(parcel)

    async def list_parcels(
        self,
        filter_params: ParcelFilter,
        current_user: User,
    ) -> List[ParcelRead]:
        """Fetch parcels subject to user's jurisdictional scope."""
        allowed_states, allowed_districts, assigned_officer_id, owner_user_id = ScopeChecker.get_query_scope(current_user)

        parcels = await self.parcel_repo.list_parcels(
            filter_params=filter_params,
            allowed_states=allowed_states,
            allowed_districts=allowed_districts,
            assigned_officer_id=assigned_officer_id,
            owner_user_id=owner_user_id,
            aadhaar_hash=current_user.aadhaar_hash,
        )

        return [self._to_read_schema(p) for p in parcels]

    async def update_parcel(
        self,
        parcel_id: str,
        parcel_in: ParcelUpdate,
        current_user: User,
    ) -> ParcelRead:
        """Update parcel details or spatial boundaries."""
        parcel = await self.parcel_repo.get_by_id(parcel_id)
        if not parcel:
            raise EntityNotFoundException("LandParcel", parcel_id)

        ScopeChecker.verify_parcel_access(current_user, parcel)
        updated = await self.parcel_repo.update_with_geometry(db_parcel=parcel, parcel_in=parcel_in)
        logger.info(f"Parcel '{parcel_id}' updated by user '{current_user.username}'.")
        return self._to_read_schema(updated)

    async def get_parcel_geojson_feature(self, parcel_id: str, current_user: User) -> GeoJSONFeature:
        """Export parcel as a standard RFC 7946 GeoJSON Feature."""
        parcel = await self.parcel_repo.get_by_id(parcel_id)
        if not parcel:
            raise EntityNotFoundException("LandParcel", parcel_id)

        ScopeChecker.verify_parcel_access(current_user, parcel)
        geojson_dict = self.parcel_repo.extract_geojson(parcel)

        properties = {
            "id": parcel.id,
            "survey_number": parcel.survey_number,
            "project_id": parcel.project_id,
            "landowner_name": parcel.landowner_name,
            "state": parcel.state,
            "district": parcel.district,
            "village": parcel.village,
            "area_acres": parcel.area_acres,
            "land_type": parcel.land_type,
            "acquisition_status": parcel.acquisition_status,
            "compensation_status": parcel.compensation_status,
            "possession_status": parcel.possession_status,
        }

        return GeoJSONFeature(
            id=parcel.id,
            geometry=GeoJSONPolygon(**geojson_dict) if geojson_dict else None,
            properties=properties,
        )

    def _to_read_schema(self, parcel: LandParcel) -> ParcelRead:
        """Convert database entity to Pydantic read schema with extracted GeoJSON."""
        geojson_dict = self.parcel_repo.extract_geojson(parcel)

        center_list = None
        if parcel.center_lat is not None and parcel.center_lng is not None:
            center_list = [parcel.center_lat, parcel.center_lng]

        return ParcelRead(
            id=parcel.id,
            survey_number=parcel.survey_number,
            project_id=parcel.project_id,
            landowner_name=parcel.landowner_name,
            landowner_mobile=parcel.landowner_mobile,
            landowner_address=parcel.landowner_address,
            masked_aadhaar=parcel.masked_aadhaar,
            masked_bank_account=parcel.masked_bank_account,
            state=parcel.state,
            district=parcel.district,
            village=parcel.village,
            area_acres=parcel.area_acres,
            land_type=parcel.land_type,
            acquisition_status=parcel.acquisition_status,
            compensation_status=parcel.compensation_status,
            possession_status=parcel.possession_status,
            market_value_per_acre=parcel.market_value_per_acre,
            multiplier_factor=parcel.multiplier_factor,
            asset_valuation=parcel.asset_valuation,
            total_compensation=parcel.total_compensation,
            consent_received=parcel.consent_received,
            consent_date=parcel.consent_date,
            compensation_details=parcel.compensation_details or {},
            polygon_coords=parcel.polygon_coords or [],
            center_lat=parcel.center_lat,
            center_lng=parcel.center_lng,
            center=center_list,
            geojson=geojson_dict,
            owner_user_id=parcel.owner_user_id,
            assigned_officer_id=parcel.assigned_officer_id,
            created_at=parcel.created_at,
            updated_at=parcel.updated_at,
        )

