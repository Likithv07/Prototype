from typing import Any, Dict, List, Optional
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.field import (
    EvidenceVerificationRequest,
    FieldAssignmentCreate,
    FieldAssignmentRead,
    FieldAssignmentUpdateStatus,
    FieldDocumentRead,
    FieldPhotoRead,
    FieldSurveyCreate,
    FieldSurveyRead,
)
from app.services.field import FieldService

router = APIRouter()


# -----------------------------------------------------------------------------
# Field Assignments
# -----------------------------------------------------------------------------

@router.post(
    "/assignments",
    response_model=FieldAssignmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Assign parcel to field officer",
    description="District Officer or Admin assigns a specific land parcel to a field officer with prioritized required tasks.",
)
async def create_assignment(
    assignment_in: FieldAssignmentCreate,
    current_user: User = Depends(require_role("ADMIN", "DISTRICT_OFFICER", "STATE_OFFICIAL")),
    db: AsyncSession = Depends(get_db),
) -> FieldAssignmentRead:
    """Create field assignment."""
    service = FieldService(db)
    return await service.create_assignment(assignment_in=assignment_in, current_user=current_user)


@router.get(
    "/assignments",
    response_model=List[FieldAssignmentRead],
    summary="List field assignments",
    description="List assignments. Field officers only see their assigned tasks; supervisors see assignments within their jurisdiction.",
)
async def list_assignments(
    status: Optional[str] = Query(None, description="Filter by status ('Pending', 'In Progress', 'Completed')"),
    priority: Optional[str] = Query(None, description="Filter by priority ('High', 'Medium', 'Low')"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    parcel_id: Optional[str] = Query(None, description="Filter by parcel ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[FieldAssignmentRead]:
    """List assignments."""
    service = FieldService(db)
    return await service.list_assignments(
        status=status,
        priority=priority,
        project_id=project_id,
        parcel_id=parcel_id,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )


@router.put(
    "/assignments/{assignment_id}/status",
    response_model=FieldAssignmentRead,
    summary="Update assignment status",
    description="Field officers update task progress ('In Progress', 'Completed') with completion remarks.",
)
async def update_assignment_status(
    assignment_id: str,
    status_update: FieldAssignmentUpdateStatus,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FieldAssignmentRead:
    """Update assignment status."""
    service = FieldService(db)
    return await service.update_assignment_status(
        assignment_id=assignment_id,
        new_status=status_update.status,
        remarks=status_update.remarks,
        current_user=current_user,
    )


# -----------------------------------------------------------------------------
# Field Survey Enumeration
# -----------------------------------------------------------------------------

@router.post(
    "/surveys",
    response_model=FieldSurveyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit ground survey enumeration",
    description="Submit physical asset enumeration (structures, standing crops, counted trees, wells) for a demarcated parcel.",
)
async def create_survey_record(
    survey_in: FieldSurveyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FieldSurveyRead:
    """Create survey record."""
    service = FieldService(db)
    return await service.create_survey_record(survey_in=survey_in, current_user=current_user)


@router.get(
    "/surveys",
    response_model=List[FieldSurveyRead],
    summary="List survey records",
    description="Fetch survey enumeration records for specified parcel or project.",
)
async def list_surveys(
    parcel_id: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[FieldSurveyRead]:
    """List survey records."""
    service = FieldService(db)
    surveys = await service.field_repo.list_surveys(
        parcel_id=parcel_id,
        project_id=project_id,
        skip=skip,
        limit=limit,
    )
    return [
        FieldSurveyRead(
            id=s.id,
            parcel_id=s.parcel_id,
            project_id=s.project_id,
            assignment_id=s.assignment_id,
            officer_id=s.officer_id,
            officer_name=s.officer.full_name if s.officer else None,
            survey_date=s.survey_date,
            survey_type=s.survey_type,
            structures_observed=s.structures_observed,
            crops_observed=s.crops_observed,
            trees_count=s.trees_count,
            wells_count=s.wells_count,
            remarks=s.remarks,
            verification_status=s.verification_status,
            verified_by_id=s.verified_by_id,
            verified_at=s.verified_at,
            rejection_reason=s.rejection_reason,
            created_at=s.created_at,
        )
        for s in surveys
    ]


# -----------------------------------------------------------------------------
# Field Photos & GPS Metadata Upload
# -----------------------------------------------------------------------------

@router.post(
    "/photos",
    response_model=FieldPhotoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload geotagged field photo evidence",
    description="Upload photo with validated magic bytes, SHA-256 hash calculation, and precision GPS latitude/longitude/accuracy metadata.",
)
async def upload_field_photo(
    parcel_id: str = Form(...),
    caption: str = Form(...),
    latitude: float = Form(..., description="GPS Latitude in decimal degrees"),
    longitude: float = Form(..., description="GPS Longitude in decimal degrees"),
    accuracy_meters: float = Form(1.0, description="Differential GPS / RTK accuracy in meters"),
    photo_type: str = Form("Boundary Marker"),
    assignment_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FieldPhotoRead:
    """Upload photo."""
    service = FieldService(db)
    file_bytes = await file.read()
    return await service.upload_field_photo(
        file_bytes=file_bytes,
        filename=file.filename or "photo.jpg",
        parcel_id=parcel_id,
        assignment_id=assignment_id,
        photo_type=photo_type,
        caption=caption,
        latitude=latitude,
        longitude=longitude,
        accuracy_meters=accuracy_meters,
        current_user=current_user,
    )


@router.get(
    "/photos",
    response_model=List[FieldPhotoRead],
    summary="List field photos",
    description="Fetch geotagged field photos filtered by parcel or assignment.",
)
async def list_photos(
    parcel_id: Optional[str] = Query(None),
    assignment_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[FieldPhotoRead]:
    """List photos."""
    service = FieldService(db)
    photos = await service.field_repo.list_photos(
        parcel_id=parcel_id,
        assignment_id=assignment_id,
        status=status,
        skip=skip,
        limit=limit,
    )
    return [service._to_photo_read(p) for p in photos]


# -----------------------------------------------------------------------------
# Field Documents Upload
# -----------------------------------------------------------------------------

@router.post(
    "/documents",
    response_model=FieldDocumentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload statutory field document",
    description="Upload survey PDFs, title deeds, or consent agreements with cryptographic SHA-256 hash generation.",
)
async def upload_field_document(
    parcel_id: str = Form(...),
    title: str = Form(...),
    category: str = Form("Land Survey Report"),
    assignment_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FieldDocumentRead:
    """Upload document."""
    service = FieldService(db)
    file_bytes = await file.read()
    return await service.upload_field_document(
        file_bytes=file_bytes,
        filename=file.filename or "document.pdf",
        parcel_id=parcel_id,
        assignment_id=assignment_id,
        title=title,
        category=category,
        current_user=current_user,
    )


@router.get(
    "/documents",
    response_model=List[FieldDocumentRead],
    summary="List field documents",
    description="Fetch field documents filtered by parcel, assignment, or category.",
)
async def list_documents(
    parcel_id: Optional[str] = Query(None),
    assignment_id: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[FieldDocumentRead]:
    """List documents."""
    service = FieldService(db)
    docs = await service.field_repo.list_documents(
        parcel_id=parcel_id,
        assignment_id=assignment_id,
        category=category,
        status=status,
        skip=skip,
        limit=limit,
    )
    return [service._to_doc_read(d) for d in docs]


# -----------------------------------------------------------------------------
# Evidence Verification / Rejection
# -----------------------------------------------------------------------------

@router.put(
    "/evidence/{evidence_type}/{evidence_id}/verify",
    response_model=Dict[str, Any],
    summary="Verify or reject field evidence",
    description="Supervisors (District Officers / Admins) review and verify or reject photos and documents with mandatory remarks on rejection.",
)
async def verify_evidence(
    evidence_type: str,
    evidence_id: str,
    verification_in: EvidenceVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Verify evidence."""
    service = FieldService(db)
    return await service.verify_evidence(
        evidence_type=evidence_type,
        evidence_id=evidence_id,
        verification_in=verification_in,
        current_user=current_user,
    )

