import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.grievance import (
    GrievanceAssignRequest,
    GrievanceCreate,
    GrievanceDocumentRead,
    GrievanceFilter,
    GrievanceHistoryRead,
    GrievanceRead,
    GrievanceResolutionRequest,
    GrievanceStatusUpdateRequest,
)
from app.services.grievance import GrievanceService

router = APIRouter()


@router.post(
    "",
    response_model=GrievanceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Lodge a statutory grievance petition",
)
async def create_grievance(
    payload: GrievanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GrievanceRead:
    """Lodge a new grievance on a cadastral land parcel with ground particulars."""
    service = GrievanceService(db)
    return await service.create_grievance(payload, current_user)


@router.get(
    "",
    response_model=List[GrievanceRead],
    summary="List grievances scoped to administrative jurisdiction",
)
async def list_grievances(
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    parcel_id: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[GrievanceRead]:
    """Retrieve grievances filtered by jurisdictional authority (District, State, or National)."""
    filter_params = GrievanceFilter(
        status=status_filter,
        category=category,
        parcel_id=parcel_id,
        project_id=project_id,
        district=district,
    )
    service = GrievanceService(db)
    return await service.list_grievances(
        current_user=current_user,
        filter_params=filter_params,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{grievance_id}",
    response_model=GrievanceRead,
    summary="Get grievance details with documents and audit trail",
)
async def get_grievance(
    grievance_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GrievanceRead:
    """Retrieve specific grievance details with evidence documents and timeline history."""
    service = GrievanceService(db)
    return await service.get_grievance(grievance_id, current_user)


@router.post(
    "/{grievance_id}/assign",
    response_model=GrievanceRead,
    summary="Allocate grievance to an inquiry officer",
    dependencies=[Depends(require_role("DISTRICT_OFFICER", "STATE_OFFICIAL", "CENTRAL_OFFICIAL", "ADMIN"))],
)
async def assign_grievance(
    grievance_id: str,
    payload: GrievanceAssignRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GrievanceRead:
    """Assign grievance to a revenue or land acquisition officer for statutory inquiry."""
    service = GrievanceService(db)
    return await service.assign_grievance(grievance_id, payload, current_user)


@router.put(
    "/{grievance_id}/status",
    response_model=GrievanceRead,
    summary="Update grievance lifecycle status",
    dependencies=[Depends(require_role("DISTRICT_OFFICER", "STATE_OFFICIAL", "CENTRAL_OFFICIAL", "ADMIN"))],
)
async def update_grievance_status(
    grievance_id: str,
    payload: GrievanceStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GrievanceRead:
    """Transition grievance through hearing review states."""
    service = GrievanceService(db)
    return await service.update_status(grievance_id, payload, current_user)


@router.post(
    "/{grievance_id}/resolve",
    response_model=GrievanceRead,
    summary="Record formal inquiry findings and close grievance",
    dependencies=[Depends(require_role("DISTRICT_OFFICER", "STATE_OFFICIAL", "CENTRAL_OFFICIAL", "ADMIN"))],
)
async def resolve_grievance(
    grievance_id: str,
    payload: GrievanceResolutionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GrievanceRead:
    """Record formal hearing findings and conclude grievance resolution."""
    service = GrievanceService(db)
    return await service.resolve_grievance(grievance_id, payload, current_user)


@router.post(
    "/{grievance_id}/documents",
    response_model=GrievanceDocumentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Attach supporting document to grievance",
)
async def attach_grievance_document(
    grievance_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GrievanceDocumentRead:
    """Upload supporting title deed, affidavit, or revenue order to a grievance."""
    service = GrievanceService(db)
    contents = await file.read()
    return await service.attach_document(
        grievance_id=grievance_id,
        document_name=file.filename or "supporting_evidence.pdf",
        file_bytes=contents,
        mime_type=file.content_type or "application/pdf",
        current_user=current_user,
    )


@router.get(
    "/{grievance_id}/history",
    response_model=List[GrievanceHistoryRead],
    summary="Retrieve full audit history for grievance",
)
async def get_grievance_history(
    grievance_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[GrievanceHistoryRead]:
    """Retrieve immutable audit trail of actions, officer assignments, and hearing decisions."""
    service = GrievanceService(db)
    grievance = await service.get_grievance(grievance_id, current_user)
    return grievance.history

