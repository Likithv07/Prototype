from typing import List
from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.compensation import (
    AwardApprovalRequest,
    CompensationAssessmentRead,
    CompensationAssessmentUpdate,
    CompensationBreakdownRead,
    CompensationCalculateRequest,
    CompensationHistoryRead,
    RevisionRequest,
)
from app.services.compensation import CompensationService

router = APIRouter()


@router.post(
    "/{parcel_id}/calculate",
    response_model=CompensationBreakdownRead,
    summary="Interactive statutory compensation calculator",
    description="Calculate statutory compensation breakdown according to Section 26-30 of RFCTLARR Act 2013 using versioned statutory rules.",
)
async def calculate_compensation(
    parcel_id: str,
    calc_in: CompensationCalculateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CompensationBreakdownRead:
    service = CompensationService(db)
    return await service.calculate(parcel_id=parcel_id, calc_in=calc_in, current_user=current_user)


@router.get(
    "/{parcel_id}",
    response_model=CompensationAssessmentRead,
    summary="Retrieve compensation assessment for parcel",
    description="Retrieve the active statutory compensation assessment, itemized asset valuations, and award details.",
)
async def get_compensation_assessment(
    parcel_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CompensationAssessmentRead:
    service = CompensationService(db)
    return await service.get_or_create_assessment_for_parcel(parcel_id=parcel_id, current_user=current_user)


@router.put(
    "/{assessment_id}",
    response_model=CompensationAssessmentRead,
    summary="Update compensation assessment formulation",
    description="Update valuation parameters or attached itemized components (structures, trees, crops) while in DRAFT or REVISION_REQUESTED.",
)
async def update_compensation_assessment(
    assessment_id: str,
    update_in: CompensationAssessmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CompensationAssessmentRead:
    service = CompensationService(db)
    return await service.update_assessment(
        assessment_id=assessment_id,
        update_in=update_in,
        current_user=current_user,
    )


@router.post(
    "/{assessment_id}/submit",
    response_model=CompensationAssessmentRead,
    summary="Submit compensation assessment for supervisory review",
    description="Transition assessment from DRAFT to SUBMITTED for Section 31 statutory award review.",
)
async def submit_compensation_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CompensationAssessmentRead:
    service = CompensationService(db)
    return await service.submit_assessment(assessment_id=assessment_id, current_user=current_user)


@router.post(
    "/{assessment_id}/approve",
    response_model=CompensationAssessmentRead,
    summary="Approve compensation and issue statutory Section 31 Award",
    description="Authorized supervisory officer digitally certifies compensation assessment. Enforces 6 mandatory statutory verification gates.",
)
async def approve_compensation_assessment(
    assessment_id: str,
    approval_in: AwardApprovalRequest,
    current_user: User = Depends(
        require_role("ADMIN", "CENTRAL_OFFICIAL", "STATE_OFFICIAL", "DISTRICT_OFFICER")
    ),
    db: AsyncSession = Depends(get_db),
) -> CompensationAssessmentRead:
    service = CompensationService(db)
    return await service.approve_and_issue_award(
        assessment_id=assessment_id,
        approval_in=approval_in,
        current_user=current_user,
    )


@router.post(
    "/{assessment_id}/reject",
    response_model=CompensationAssessmentRead,
    summary="Request revision or reject compensation assessment",
    description="Supervisory officer requests formulation revision stating statutory grounds.",
)
async def reject_compensation_assessment(
    assessment_id: str,
    revision_in: RevisionRequest,
    current_user: User = Depends(
        require_role("ADMIN", "CENTRAL_OFFICIAL", "STATE_OFFICIAL", "DISTRICT_OFFICER")
    ),
    db: AsyncSession = Depends(get_db),
) -> CompensationAssessmentRead:
    service = CompensationService(db)
    return await service.reject_or_request_revision(
        assessment_id=assessment_id,
        revision_in=revision_in,
        current_user=current_user,
    )


@router.get(
    "/{assessment_id}/history",
    response_model=List[CompensationHistoryRead],
    summary="Retrieve compensation revision and audit history",
    description="Retrieve the complete immutable audit trail of calculation updates, revisions, and approval events.",
)
async def get_compensation_history(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[CompensationHistoryRead]:
    service = CompensationService(db)
    return await service.get_history(assessment_id=assessment_id, current_user=current_user)

