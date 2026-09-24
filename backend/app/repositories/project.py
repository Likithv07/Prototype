from typing import List, Optional
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.project import Project
from app.repositories.base import BaseRepository
from app.schemas.project import ProjectCreate, ProjectFilter, ProjectUpdate


class ProjectRepository(BaseRepository[Project, ProjectCreate, ProjectUpdate]):
    """Repository managing Project data queries with geographic scoping filters."""

    def __init__(self, session: AsyncSession):
        super().__init__(Project, session)

    async def get_by_id(self, project_id: str) -> Optional[Project]:
        """Fetch project by ID with associated parcels."""
        stmt = (
            select(Project)
            .where(Project.id == project_id)
            .options(selectinload(Project.parcels))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_projects(
        self,
        *,
        filter_params: ProjectFilter,
        allowed_states: Optional[List[str]] = None,
        allowed_districts: Optional[List[str]] = None,
    ) -> List[Project]:
        """Fetch paginated projects matching search criteria and geographic permissions."""
        stmt = select(Project).options(selectinload(Project.parcels))

        # Jurisdictional Scope Constraints
        if allowed_states is not None:
            stmt = stmt.where(Project.state.in_(allowed_states))
        if allowed_districts is not None:
            stmt = stmt.where(Project.district.in_(allowed_districts))

        # User Filter Criteria
        if filter_params.state:
            stmt = stmt.where(Project.state.ilike(f"%{filter_params.state}%"))
        if filter_params.district:
            stmt = stmt.where(Project.district.ilike(f"%{filter_params.district}%"))
        if filter_params.status:
            stmt = stmt.where(Project.status.ilike(filter_params.status))
        if filter_params.project_type:
            stmt = stmt.where(Project.project_type.ilike(filter_params.project_type))
        if filter_params.search:
            pattern = f"%{filter_params.search}%"
            stmt = stmt.where(
                or_(
                    Project.name.ilike(pattern),
                    Project.id.ilike(pattern),
                    Project.implementing_agency.ilike(pattern),
                )
            )

        stmt = stmt.order_by(Project.created_at.desc()).offset(filter_params.skip).limit(filter_params.limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def count_projects(
        self,
        *,
        filter_params: ProjectFilter,
        allowed_states: Optional[List[str]] = None,
        allowed_districts: Optional[List[str]] = None,
    ) -> int:
        """Count total projects matching filters."""
        stmt = select(func.count(Project.id))

        if allowed_states is not None:
            stmt = stmt.where(Project.state.in_(allowed_states))
        if allowed_districts is not None:
            stmt = stmt.where(Project.district.in_(allowed_districts))

        if filter_params.state:
            stmt = stmt.where(Project.state.ilike(f"%{filter_params.state}%"))
        if filter_params.district:
            stmt = stmt.where(Project.district.ilike(f"%{filter_params.district}%"))
        if filter_params.status:
            stmt = stmt.where(Project.status.ilike(filter_params.status))

        res = await self.session.execute(stmt)
        return res.scalar() or 0

