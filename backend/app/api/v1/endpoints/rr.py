import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.rr import (
    AffectedFamilyCreate,
    AffectedFamilyFilter,
    AffectedFamilyRead,
    ResettlementColonyRead,
    RrBenefitCreate,
    RrBenefitDisburseRequest,
    RrBenefitRead,
    RrEligibilityCreate,
    RrEligibilityRead,
)
from app.services.rr import RrService

router = APIRouter()


@router.get(
    "/colonies",
    response_model=List[ResettlementColonyRead],
    summary="List model resettlement colonies and civic infrastructure metrics",
)
async def list_resettlement_colonies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ResettlementColonyRead]:
    """Retrieve social infrastructure, power, water grid, and handover rates for R&R colonies."""
    service = RrService(db)
    return await service.list_resettlement_colonies(current_user)


@router.get(
    "/families",
    response_model=List[AffectedFamilyRead],
    summary="List project-affected families scoped to jurisdiction",
    dependencies=[Depends(require_role("DISTRICT_OFFICER", "STATE_OFFICIAL", "CENTRAL_OFFICIAL", "ADMIN"))],
)
async def list_affected_families(
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    affected_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[AffectedFamilyRead]:
    """Retrieve project-affected families subject to jurisdictional scope constraints."""
    filter_params = AffectedFamilyFilter(
        state=state,
        district=district,
        project_id=project_id,
        status=status_filter,
        affected_type=affected_type,
    )
    service = RrService(db)
    return await service.list_affected_families(
        current_user=current_user,
        filter_params=filter_params,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/families/{family_id}",
    response_model=AffectedFamilyRead,
    summary="Get affected family particulars and R&R entitlements",
)
async def get_affected_family(
    family_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AffectedFamilyRead:
    """Retrieve family demographics, Second Schedule eligibility, and itemized benefits."""
    service = RrService(db)
    return await service.get_family_by_id(family_id, current_user)


@router.post(
    "/families",
    response_model=AffectedFamilyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a project-affected family (PAF)",
    dependencies=[Depends(require_role("DISTRICT_OFFICER", "STATE_OFFICIAL", "CENTRAL_OFFICIAL", "ADMIN"))],
)
async def register_affected_family(
    payload: AffectedFamilyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AffectedFamilyRead:
    """Register an affected family from the Social Impact Assessment (SIA) census."""
    service = RrService(db)
    return await service.create_affected_family(payload, current_user)


@router.post(
    "/families/{family_id}/eligibility",
    response_model=RrEligibilityRead,
    summary="Verify or update statutory R&R eligibility",
    dependencies=[Depends(require_role("DISTRICT_OFFICER", "STATE_OFFICIAL", "CENTRAL_OFFICIAL", "ADMIN"))],
)
async def verify_family_eligibility(
    family_id: str,
    payload: RrEligibilityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RrEligibilityRead:
    """Record statutory eligibility determination under Second Schedule of RFCTLARR Act 2013."""
    service = RrService(db)
    return await service.verify_eligibility(family_id, payload, current_user)


@router.post(
    "/families/{family_id}/benefits",
    response_model=RrBenefitRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add an R&R benefit entitlement",
    dependencies=[Depends(require_role("DISTRICT_OFFICER", "STATE_OFFICIAL", "CENTRAL_OFFICIAL", "ADMIN"))],
)
async def add_family_benefit(
    family_id: str,
    payload: RrBenefitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RrBenefitRead:
    """Allocate an alternative housing unit, livelihood grant, or shifting allowance."""
    service = RrService(db)
    return await service.add_benefit(family_id, payload, current_user)


@router.post(
    "/benefits/{benefit_id}/disburse",
    response_model=RrBenefitRead,
    summary="Disburse R&R financial allowance",
    dependencies=[Depends(require_role("DISTRICT_OFFICER", "STATE_OFFICIAL", "CENTRAL_OFFICIAL", "ADMIN"))],
)
async def disburse_family_benefit(
    benefit_id: uuid.UUID,
    payload: RrBenefitDisburseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RrBenefitRead:
    """Record financial grant transfer reference and mark benefit as disbursed."""
    service = RrService(db)
    return await service.disburse_benefit(benefit_id, payload, current_user)

