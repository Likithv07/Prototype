from typing import Any, List, Optional
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Query,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.document import (
    DocumentCreate,
    DocumentRead,
    DocumentVerificationRequest,
)
from app.services.document import DocumentService

router = APIRouter()


@router.post(
    "",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload statutory document",
    description="Upload a new statutory document (Gazette, Valuation, SIA & Consent, Title Deed, etc.) and record its initial version v1.0.",
)
async def upload_document(
    file: UploadFile = File(..., description="File document (PDF, PNG, JPG, JPEG)"),
    title: str = Form(..., description="Document title"),
    category: str = Form(..., description="Statutory category (e.g. Gazette, Valuation, SIA & Consent, Title Deed)"),
    project_id: Optional[str] = Form(None, description="Optional associated project ID"),
    parcel_id: Optional[str] = Form(None, description="Optional associated parcel ID"),
    custom_id: Optional[str] = Form(None, description="Optional custom document ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentRead:
    file_bytes = await file.read()
    service = DocumentService(db)
    doc_in = DocumentCreate(
        id=custom_id,
        title=title,
        category=category,
        project_id=project_id,
        parcel_id=parcel_id,
    )
    return await service.create_document(
        file_bytes=file_bytes,
        filename=file.filename or "statutory_document.pdf",
        doc_in=doc_in,
        current_user=current_user,
    )


@router.post(
    "/{document_id}/versions",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload revised document version",
    description="Upload an immutable new revision version for an existing statutory document without destroying previous versions.",
)
async def upload_document_version(
    document_id: str,
    file: UploadFile = File(..., description="Revised file revision"),
    changelog: Optional[str] = Form(None, description="Reason or changelog notes for this version"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentRead:
    file_bytes = await file.read()
    service = DocumentService(db)
    return await service.add_version(
        document_id=document_id,
        file_bytes=file_bytes,
        filename=file.filename or "statutory_revision.pdf",
        changelog=changelog,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=List[DocumentRead],
    summary="List statutory documents",
    description="List documents with filtering by category, project, parcel, and verified state. Citizen and officer geographic scopes are enforced.",
)
async def list_documents(
    category: Optional[str] = Query(None, description="Filter by category"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    parcel_id: Optional[str] = Query(None, description="Filter by parcel ID"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification state"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[DocumentRead]:
    service = DocumentService(db)
    return await service.list_documents(
        category=category,
        project_id=project_id,
        parcel_id=parcel_id,
        is_verified=is_verified,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentRead,
    summary="Retrieve document metadata and version history",
    description="Retrieve document metadata, current version, verification status, and all version history.",
)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentRead:
    service = DocumentService(db)
    return await service.get_document(document_id=document_id, current_user=current_user)


@router.get(
    "/{document_id}/download",
    summary="Download statutory document file",
    description="Download the verified binary file payload for authorized users. Defaults to latest version unless specific version is requested.",
)
async def download_document(
    document_id: str,
    version: Optional[int] = Query(None, description="Specific version number to download (default: latest)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    service = DocumentService(db)
    file_bytes, filename, mime_type, sha256 = await service.get_download_file(
        document_id=document_id,
        version_number=version,
        current_user=current_user,
    )
    return Response(
        content=file_bytes,
        media_type=mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Checksum-SHA256": sha256,
        },
    )


@router.put(
    "/{document_id}/verify",
    response_model=DocumentRead,
    summary="Verify or reject statutory document",
    description="Authorized officers verify or reject the authenticity of a statutory document revision.",
)
async def verify_document(
    document_id: str,
    verify_in: DocumentVerificationRequest,
    current_user: User = Depends(
        require_role("ADMIN", "CENTRAL_OFFICIAL", "STATE_OFFICIAL", "DISTRICT_OFFICER", "FIELD_OFFICER")
    ),
    db: AsyncSession = Depends(get_db),
) -> DocumentRead:
    service = DocumentService(db)
    return await service.verify_document(
        document_id=document_id,
        verify_in=verify_in,
        current_user=current_user,
    )

