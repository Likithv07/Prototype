from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import ScopeChecker
from app.core.exceptions import EntityAlreadyExistsException, EntityNotFoundException, ForbiddenException
from app.core.logging import get_logger
from app.models.project import Project
from app.models.user import User
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectFilter, ProjectRead, ProjectUpdate

logger = get_logger(__name__)


class ProjectService:
    """Service handling Project lifecycle and geographic scope validation."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.project_repo = ProjectRepository(session)

    async def create_project(self, project_in: ProjectCreate, current_user: User) -> ProjectRead:
        """Create a new infrastructure land acquisition project with jurisdictional checks."""
        # Check duplicate
        existing = await self.project_repo.get_by_id(project_in.id)
        if existing:
            raise EntityAlreadyExistsException("Project", "id", project_in.id)

        # Enforce jurisdictional creation rights
        roles = set(current_user.role_names)
        if "STATE_OFFICIAL" in roles and current_user.state:
            if project_in.state.strip().lower() != current_user.state.strip().lower():
                raise ForbiddenException(
                    f"State officials can only register projects within their state ('{current_user.state}')."
                )

        if "DISTRICT_OFFICER" in roles and current_user.district:
            if project_in.district.strip().lower() != current_user.district.strip().lower():
                raise ForbiddenException(
                    f"District officers can only register projects within their district ('{current_user.district}')."
                )

        db_project = await self.project_repo.create(obj_in=project_in)
        logger.info(f"Project '{db_project.id}' created by user '{current_user.username}'.")
        return self._to_read_schema(db_project)

    async def get_project(self, project_id: str, current_user: User) -> ProjectRead:
        """Retrieve project by ID and verify geographic access."""
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise EntityNotFoundException("Project", project_id)

        ScopeChecker.verify_project_access(current_user, project)
        return self._to_read_schema(project)

    async def list_projects(
        self,
        filter_params: ProjectFilter,
        current_user: User,
    ) -> List[ProjectRead]:
        """Fetch list of projects filtered by user's permitted jurisdictional scope."""
        allowed_states, allowed_districts, _, _ = ScopeChecker.get_query_scope(current_user)

        projects = await self.project_repo.list_projects(
            filter_params=filter_params,
            allowed_states=allowed_states,
            allowed_districts=allowed_districts,
        )

        return [self._to_read_schema(p) for p in projects]

    async def update_project(
        self,
        project_id: str,
        project_in: ProjectUpdate,
        current_user: User,
    ) -> ProjectRead:
        """Update project details subject to scope permissions."""
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise EntityNotFoundException("Project", project_id)

        ScopeChecker.verify_project_access(current_user, project)
        updated = await self.project_repo.update(db_obj=project, obj_in=project_in)
        logger.info(f"Project '{project_id}' updated by user '{current_user.username}'.")
        return self._to_read_schema(updated)

    async def delete_project(self, project_id: str, current_user: User) -> None:
        """Delete project (Admin only)."""
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise EntityNotFoundException("Project", project_id)

        await self.project_repo.delete(id=project_id)
        logger.info(f"Project '{project_id}' deleted by user '{current_user.username}'.")

    @staticmethod
    def _to_read_schema(project: Project) -> ProjectRead:
        """Convert database model to Pydantic read schema."""
        return ProjectRead(
            id=project.id,
            name=project.name,
            ministry=project.ministry,
            implementing_agency=project.implementing_agency,
            state=project.state,
            district=project.district,
            project_type=project.project_type,
            land_required=project.land_required,
            land_acquired=project.land_acquired,
            progress=project.progress,
            status=project.status,
            start_date=project.start_date,
            expected_completion_date=project.expected_completion_date,
            budget_cr=project.budget_cr,
            compensation_disbursed_cr=project.compensation_disbursed_cr,
            lifecycle=project.lifecycle or [],
            parcels_count=len(project.parcels) if project.parcels else 0,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

