try:
    from geoalchemy2.shape import from_shape, to_shape
    from shapely.geometry import mapping, shape
    _HAS_SHAPELY = True
except ImportError:
    _HAS_SHAPELY = False
    from_shape = None
    to_shape = None
    mapping = None
    shape = None

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.parcel import LandParcel
from app.repositories.base import BaseRepository
from app.schemas.parcel import ParcelCreate, ParcelFilter, ParcelUpdate


class ParcelRepository(BaseRepository[LandParcel, ParcelCreate, ParcelUpdate]):
    """Repository managing LandParcel queries with PostGIS spatial indexing and scope filters."""

    def __init__(self, session: AsyncSession):
        super().__init__(LandParcel, session)

    async def get_by_id(self, parcel_id: str) -> Optional[LandParcel]:
        """Fetch parcel by ID with project relationship."""
        stmt = (
            select(LandParcel)
            .where(LandParcel.id == parcel_id)
            .options(selectinload(LandParcel.project))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_parcels(
        self,
        *,
        filter_params: ParcelFilter,
        allowed_states: Optional[List[str]] = None,
        allowed_districts: Optional[List[str]] = None,
        assigned_officer_id: Optional[uuid.UUID] = None,
        owner_user_id: Optional[uuid.UUID] = None,
    ) -> List[LandParcel]:
        """Fetch parcels subject to multi-tier scope and filter parameters."""
        stmt = select(LandParcel).options(selectinload(LandParcel.project))

        # Jurisdictional Scope Constraints
        if allowed_states is not None:
            stmt = stmt.where(LandParcel.state.in_(allowed_states))
        if allowed_districts is not None:
            stmt = stmt.where(LandParcel.district.in_(allowed_districts))
        if assigned_officer_id is not None:
            stmt = stmt.where(LandParcel.assigned_officer_id == assigned_officer_id)
        if owner_user_id is not None:
            stmt = stmt.where(LandParcel.owner_user_id == owner_user_id)

        # Filters
        if filter_params.project_id:
            stmt = stmt.where(LandParcel.project_id == filter_params.project_id)
        if filter_params.state:
            stmt = stmt.where(LandParcel.state.ilike(f"%{filter_params.state}%"))
        if filter_params.district:
            stmt = stmt.where(LandParcel.district.ilike(f"%{filter_params.district}%"))
        if filter_params.village:
            stmt = stmt.where(LandParcel.village.ilike(f"%{filter_params.village}%"))
        if filter_params.acquisition_status:
            stmt = stmt.where(LandParcel.acquisition_status.ilike(filter_params.acquisition_status))
        if filter_params.compensation_status:
            stmt = stmt.where(LandParcel.compensation_status.ilike(filter_params.compensation_status))
        if filter_params.possession_status:
            stmt = stmt.where(LandParcel.possession_status.ilike(filter_params.possession_status))
        if filter_params.land_type:
            stmt = stmt.where(LandParcel.land_type.ilike(filter_params.land_type))
        if filter_params.search:
            pattern = f"%{filter_params.search}%"
            stmt = stmt.where(
                or_(
                    LandParcel.id.ilike(pattern),
                    LandParcel.survey_number.ilike(pattern),
                    LandParcel.landowner_name.ilike(pattern),
                )
            )

        stmt = stmt.order_by(LandParcel.created_at.desc()).offset(filter_params.skip).limit(filter_params.limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create_with_geometry(
        self,
        *,
        parcel_in: ParcelCreate,
    ) -> LandParcel:
        """Create parcel entity, converting GeoJSON geometry to PostGIS polygon if supplied."""
        data = parcel_in.model_dump(exclude={"geojson"})

        # Process GeoJSON geometry into PostGIS geometry and centroid
        if parcel_in.geojson and _HAS_SHAPELY and shape and from_shape:
            try:
                shapely_geom = shape(parcel_in.geojson.model_dump())
                data["geometry"] = from_shape(shapely_geom, srid=4326)
                centroid = shapely_geom.centroid
                data["center_lat"] = centroid.y
                data["center_lng"] = centroid.x
            except Exception:
                pass
        elif parcel_in.polygon_coords:
            coords = parcel_in.polygon_coords
            if coords and len(coords) > 0:
                lats = [c[0] for c in coords if len(c) >= 2]
                lngs = [c[1] for c in coords if len(c) >= 2]
                if lats and lngs:
                    data.setdefault("center_lat", sum(lats) / len(lats))
                    data.setdefault("center_lng", sum(lngs) / len(lngs))

        db_parcel = LandParcel(**data)
        self.session.add(db_parcel)
        await self.session.flush()
        await self.session.refresh(db_parcel)
        return db_parcel

    async def update_with_geometry(
        self,
        *,
        db_parcel: LandParcel,
        parcel_in: ParcelUpdate,
    ) -> LandParcel:
        """Update parcel entity with optional geometry re-calculation."""
        update_data = parcel_in.model_dump(exclude_unset=True, exclude={"geojson"})

        if parcel_in.geojson is not None and _HAS_SHAPELY and shape and from_shape:
            try:
                shapely_geom = shape(parcel_in.geojson.model_dump())
                update_data["geometry"] = from_shape(shapely_geom, srid=4326)
                centroid = shapely_geom.centroid
                update_data["center_lat"] = centroid.y
                update_data["center_lng"] = centroid.x
            except Exception:
                pass

        for field, value in update_data.items():
            setattr(db_parcel, field, value)

        self.session.add(db_parcel)
        await self.session.flush()
        await self.session.refresh(db_parcel)
        return db_parcel

    @staticmethod
    def extract_geojson(db_parcel: LandParcel) -> Optional[Dict[str, Any]]:
        """Safely extract GeoJSON dictionary representation from PostGIS geometry."""
        if db_parcel.geometry is None:
            if db_parcel.polygon_coords:
                return {
                    "type": "Polygon",
                    "coordinates": [db_parcel.polygon_coords],
                }
            return None
        if not _HAS_SHAPELY or to_shape is None or mapping is None:
            if db_parcel.polygon_coords:
                return {
                    "type": "Polygon",
                    "coordinates": [db_parcel.polygon_coords],
                }
            return None
        try:
            shapely_geom = to_shape(db_parcel.geometry)
            return mapping(shapely_geom)
        except Exception:
            return None

