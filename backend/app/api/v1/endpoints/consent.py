from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.consent import (
    ConsentCreate,
    ConsentESignVerifyRequest,
    ConsentHistoryRead,
    ConsentRead,
    ConsentSubmitRequest,
    ConsentVerificationRequest,
    ESignInitiateResponse,
    ESignVerifyResponse,
)
from app.services.consent import ConsentService

router = APIRouter()


@router.post(
    "",
    response_model=ConsentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create landowner consent draft",
    description="Initiate a new statutory landowner consent record linked to a cadastral land parcel.",
)
async def create_consent(
    consent_in: ConsentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConsentRead:
    service = ConsentService(db)
    return await service.create_consent(consent_in=consent_in, current_user=current_user)


@router.get(
    "",
    response_model=List[ConsentRead],
    summary="List landowner consent records",
    description="List consents with filtering by project, parcel, and lifecycle status. Citizens can only access their own records.",
)
async def list_consents(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    parcel_id: Optional[str] = Query(None, description="Filter by parcel ID"),
    status: Optional[str] = Query(None, description="Filter by status ('DRAFT', 'SUBMITTED', 'VERIFIED', 'REJECTED')"),
    consent_type: Optional[str] = Query(None, description="Filter by statutory consent type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ConsentRead]:
    service = ConsentService(db)
    return await service.list_consents(
        project_id=project_id,
        parcel_id=parcel_id,
        status=status,
        consent_type=consent_type,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{consent_id}",
    response_model=ConsentRead,
    summary="Retrieve landowner consent record",
    description="Retrieve consent details, eSign verification state, and officer remarks.",
)
async def get_consent(
    consent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConsentRead:
    service = ConsentService(db)
    return await service.get_consent(consent_id=consent_id, current_user=current_user)


@router.get(
    "/{consent_id}/history",
    response_model=List[ConsentHistoryRead],
    summary="Retrieve consent audit trail",
    description="Retrieve immutable lifecycle audit log for a specific landowner consent record.",
)
async def get_consent_history(
    consent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ConsentHistoryRead]:
    service = ConsentService(db)
    return await service.get_consent_history(consent_id=consent_id, current_user=current_user)


@router.post(
    "/{consent_id}/esign/initiate",
    response_model=ESignInitiateResponse,
    summary="Initiate mock Aadhaar eSign (Development Simulation)",
    description="Simulate eSign OTP dispatch. Clearly marked mock simulation - does not connect to live UIDAI/C-DAC gateway.",
)
async def initiate_mock_esign(
    consent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ESignInitiateResponse:
    service = ConsentService(db)
    return await service.initiate_mock_esign(consent_id=consent_id, current_user=current_user)


@router.post(
    "/{consent_id}/esign/verify",
    response_model=ESignVerifyResponse,
    summary="Verify mock OTP and record simulated eSign",
    description="Verify simulated OTP (default: 781923) and record mock electronic signature reference on consent record.",
)
async def verify_mock_esign(
    consent_id: str,
    verify_in: ConsentESignVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ESignVerifyResponse:
    service = ConsentService(db)
    return await service.verify_mock_esign(
        transaction_id=verify_in.transaction_id,
        otp_code=verify_in.otp_code,
        current_user=current_user,
    )


@router.post(
    "/{consent_id}/submit",
    response_model=ConsentRead,
    summary="Submit draft consent for official verification",
    description="Formally submit draft consent for review and verification by the district administration.",
)
async def submit_consent(
    consent_id: str,
    submit_in: ConsentSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConsentRead:
    service = ConsentService(db)
    return await service.submit_consent(
        consent_id=consent_id,
        submit_in=submit_in,
        current_user=current_user,
    )


@router.put(
    "/{consent_id}/verify",
    response_model=ConsentRead,
    summary="Verify or reject landowner consent",
    description="Supervisory district or field officers verify or reject the submitted consent, syncing cadastral parcel records.",
)
async def verify_consent(
    consent_id: str,
    verify_in: ConsentVerificationRequest,
    current_user: User = Depends(
        require_role("ADMIN", "CENTRAL_OFFICIAL", "STATE_OFFICIAL", "DISTRICT_OFFICER", "FIELD_OFFICER")
    ),
    db: AsyncSession = Depends(get_db),
) -> ConsentRead:
    service = ConsentService(db)
    return await service.verify_or_reject_consent(
        consent_id=consent_id,
        verify_in=verify_in,
        current_user=current_user,
    )

