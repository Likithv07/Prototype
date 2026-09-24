from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.parcel import ParcelFilter, ParcelRead
from app.schemas.project import ProjectCreate, ProjectFilter, ProjectRead, ProjectUpdate
from app.services.parcel import ParcelService
from app.services.project import ProjectService

router = APIRouter()


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create new project",
    description="Register a new national or state infrastructure project. Requires ADMIN, CENTRAL_OFFICIAL, or STATE_OFFICIAL role.",
)
async def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(require_role("ADMIN", "CENTRAL_OFFICIAL", "STATE_OFFICIAL")),
    db: AsyncSession = Depends(get_db),
) -> ProjectRead:
    """Create project."""
    service = ProjectService(db)
    return await service.create_project(project_in=project_in, current_user=current_user)


@router.get(
    "",
    response_model=List[ProjectRead],
    summary="List projects",
    description="List infrastructure projects filtered by user's permitted geographic scope (state/district) and search filters.",
)
async def list_projects(
    state: Optional[str] = Query(None, description="Filter by state name"),
    district: Optional[str] = Query(None, description="Filter by district name"),
    status: Optional[str] = Query(None, description="Filter by project status"),
    project_type: Optional[str] = Query(None, description="Filter by project type"),
    search: Optional[str] = Query(None, description="Search term for name or ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ProjectRead]:
    """List projects."""
    service = ProjectService(db)
    filter_params = ProjectFilter(
        state=state,
        district=district,
        status=status,
        project_type=project_type,
        search=search,
        skip=skip,
        limit=limit,
    )
    return await service.list_projects(filter_params=filter_params, current_user=current_user)


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Get project by ID",
    description="Retrieve project details with lifecycle stages and metrics. Validates user's geographic jurisdiction.",
)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectRead:
    """Get project by ID."""
    service = ProjectService(db)
    return await service.get_project(project_id=project_id, current_user=current_user)


@router.put(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Update project",
    description="Update project details, metrics, or lifecycle stage status. Requires ADMIN, CENTRAL_OFFICIAL, or STATE_OFFICIAL role.",
)
async def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    current_user: User = Depends(require_role("ADMIN", "CENTRAL_OFFICIAL", "STATE_OFFICIAL")),
    db: AsyncSession = Depends(get_db),
) -> ProjectRead:
    """Update project."""
    service = ProjectService(db)
    return await service.update_project(
        project_id=project_id,
        project_in=project_in,
        current_user=current_user,
    )


@router.get(
    "/{project_id}/parcels",
    response_model=List[ParcelRead],
    summary="List parcels under project",
    description="Fetch all land parcels demarcated within the specified infrastructure project.",
)
async def list_project_parcels(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ParcelRead]:
    """List parcels under project."""
    project_service = ProjectService(db)
    await project_service.get_project(project_id=project_id, current_user=current_user)

    parcel_service = ParcelService(db)
    filter_params = ParcelFilter(project_id=project_id, skip=skip, limit=limit)
    return await parcel_service.list_parcels(filter_params=filter_params, current_user=current_user)

