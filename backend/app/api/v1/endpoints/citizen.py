import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import ScopeChecker, get_current_user, get_db, require_role
from app.core.exceptions import EntityNotFoundException, ForbiddenException
from app.models.user import User
from app.repositories.audit import AuditRepository
from app.repositories.parcel import ParcelRepository
from app.schemas.citizen import (
    CitizenCompensationDetail,
    CitizenConsentStatus,
    CitizenNotificationRead,
    CitizenParcelSummary,
    CitizenPaymentDetail,
)
from app.schemas.consent import ConsentSubmitRequest
from app.schemas.grievance import (
    GrievanceCreate,
    GrievanceRead,
)
from app.schemas.parcel import ParcelFilter
from app.schemas.rr import AffectedFamilyRead
from app.services.compensation import CompensationService
from app.services.consent import ConsentService
from app.services.grievance import GrievanceService
from app.services.rr import RrService

router = APIRouter()


# -----------------------------------------------------------------------------
# 1. Citizen Parcel Access
# -----------------------------------------------------------------------------

@router.get(
    "/parcels",
    response_model=List[CitizenParcelSummary],
    summary="List citizen's registered land parcels",
)
async def list_citizen_parcels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[CitizenParcelSummary]:
    """Retrieve all cadastral land parcels owned by or registered to the authenticated citizen."""
    parcel_repo = ParcelRepository(db)
    filter_params = ParcelFilter()
    parcels = await parcel_repo.list_parcels(
        filter_params=filter_params,
        owner_user_id=current_user.id,
    )

    result = []
    for p in parcels:
        result.append(
            CitizenParcelSummary(
                id=p.id,
                survey_number=p.survey_number,
                project_id=p.project_id,
                project_name=p.project.name if p.project else None,
                landowner_name=p.landowner_name,
                masked_aadhaar=p.masked_aadhaar,
                state=p.state,
                district=p.district,
                village=p.village,
                area_acres=p.area_acres,
                land_type=p.land_type,
                acquisition_status=p.acquisition_status,
                compensation_status=p.compensation_status,
                possession_status=p.possession_status,
                market_value_per_acre=p.market_value_per_acre,
                multiplier_factor=p.multiplier_factor,
                asset_valuation=p.asset_valuation,
                total_compensation=p.total_compensation,
                consent_received=p.consent_received,
                consent_date=p.consent_date,
                center_lat=p.center_lat,
                center_lng=p.center_lng,
                polygon_coords=p.polygon_coords or [],
            )
        )
    return result


@router.get(
    "/parcels/{parcel_id}",
    response_model=CitizenParcelSummary,
    summary="Get details of an authorized parcel",
)
async def get_citizen_parcel(
    parcel_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CitizenParcelSummary:
    """Retrieve cadastral and PostGIS spatial particulars for a specific authorized land parcel."""
    parcel_repo = ParcelRepository(db)
    parcel = await parcel_repo.get_by_id(parcel_id)
    if not parcel:
        raise EntityNotFoundException("LandParcel", parcel_id)

    ScopeChecker.verify_parcel_access(current_user, parcel)

    return CitizenParcelSummary(
        id=parcel.id,
        survey_number=parcel.survey_number,
        project_id=parcel.project_id,
        project_name=parcel.project.name if parcel.project else None,
        landowner_name=parcel.landowner_name,
        masked_aadhaar=parcel.masked_aadhaar,
        state=parcel.state,
        district=parcel.district,
        village=parcel.village,
        area_acres=parcel.area_acres,
        land_type=parcel.land_type,
        acquisition_status=parcel.acquisition_status,
        compensation_status=parcel.compensation_status,
        possession_status=parcel.possession_status,
        market_value_per_acre=parcel.market_value_per_acre,
        multiplier_factor=parcel.multiplier_factor,
        asset_valuation=parcel.asset_valuation,
        total_compensation=parcel.total_compensation,
        consent_received=parcel.consent_received,
        consent_date=parcel.consent_date,
        center_lat=parcel.center_lat,
        center_lng=parcel.center_lng,
        polygon_coords=parcel.polygon_coords or [],
    )


# -----------------------------------------------------------------------------
# 2. Citizen Compensation Tracking (Reusing CompensationService)
# -----------------------------------------------------------------------------

@router.get(
    "/compensation/{parcel_id}",
    response_model=CitizenCompensationDetail,
    summary="Track statutory compensation formulation and Section 31 award",
)
async def get_citizen_compensation(
    parcel_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CitizenCompensationDetail:
    """Track Section 26-30 statutory valuation, Solatium, interest, and Section 31 digital award seal."""
    comp_service = CompensationService(db)
    assessment = await comp_service.get_or_create_assessment_for_parcel(parcel_id, current_user)

    award = assessment.award
    return CitizenCompensationDetail(
        parcel_id=assessment.parcel_id,
        project_id=assessment.project_id,
        survey_number=assessment.survey_number,
        landowner_name=assessment.landowner_name,
        land_area_acres=assessment.land_area_acres,
        market_value_per_acre=assessment.market_value_per_acre,
        multiplier_factor=assessment.multiplier_factor,
        asset_valuation=assessment.asset_valuation,
        basic_land_value=assessment.basic_land_value,
        multiplied_land_value=assessment.multiplied_land_value,
        market_value_plus_assets=assessment.market_value_plus_assets,
        solatium_percentage=assessment.solatium_percentage,
        solatium_amount=assessment.solatium_amount,
        interest_percentage=assessment.interest_percentage,
        interest_amount=assessment.interest_amount,
        total_compensation=assessment.total_compensation,
        status=assessment.status,
        rule_version=assessment.rule_version,
        award_number=award.award_number if award else None,
        award_date=award.award_date if award else None,
        digital_seal_ref=award.digital_seal_ref if award else None,
        competent_authority_name=award.competent_authority_name if award else None,
        competent_authority_designation=award.competent_authority_designation if award else None,
    )


# -----------------------------------------------------------------------------
# 3. Citizen Consent Status & Aadhaar eSign (Reusing ConsentService)
# -----------------------------------------------------------------------------

@router.get(
    "/consent/{parcel_id}",
    response_model=CitizenConsentStatus,
    summary="Check Aadhaar eSign consent status for a parcel",
)
async def get_citizen_consent_status(
    parcel_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CitizenConsentStatus:
    """Retrieve voluntary acquisition consent records and eSign certification status."""
    parcel_repo = ParcelRepository(db)
    parcel = await parcel_repo.get_by_id(parcel_id)
    if not parcel:
        raise EntityNotFoundException("LandParcel", parcel_id)

    ScopeChecker.verify_parcel_access(current_user, parcel)

    consent_service = ConsentService(db)
    consent = await consent_service.get_consent_by_parcel(parcel_id, current_user)

    if not consent:
        return CitizenConsentStatus(
            parcel_id=parcel_id,
            consent_id=None,
            consent_received=bool(parcel.consent_received),
            consent_date=parcel.consent_date,
            consent_type="VOLUNTARY_ACQUISITION",
            status="DRAFT",
            is_esign_completed=False,
            document_hash=None,
            esign_timestamp=None,
        )

    return CitizenConsentStatus(
        parcel_id=consent.parcel_id,
        consent_id=consent.id,
        consent_received=consent.is_verified or bool(parcel.consent_received),
        consent_date=consent.verified_at.date() if consent.verified_at else parcel.consent_date,
        consent_type=consent.consent_type,
        status=consent.status,
        is_esign_completed=consent.esign_verified or bool(consent.esign_simulation_ref),
        document_hash=consent.document_hash,
        esign_timestamp=consent.submitted_at or consent.created_at,
    )


@router.post(
    "/consent/{parcel_id}/esign",
    response_model=CitizenConsentStatus,
    summary="Execute Aadhaar eSign consent for voluntary acquisition",
)
async def execute_citizen_esign_consent(
    parcel_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CitizenConsentStatus:
    """Submit Aadhaar eSign verified consent directly from citizen portal."""
    consent_service = ConsentService(db)
    payload = ConsentSubmitRequest(
        consent_type="VOLUNTARY_ACQUISITION",
        notes="Citizen verified via BhoomiSetu Aadhaar eSign simulation.",
    )
    res = await consent_service.submit_consent(parcel_id, payload, current_user)

    return CitizenConsentStatus(
        parcel_id=res.parcel_id,
        consent_id=res.id,
        consent_received=res.is_verified,
        consent_date=res.verified_at.date() if res.verified_at else None,
        consent_type=res.consent_type,
        status=res.status,
        is_esign_completed=True,
        document_hash=res.document_hash,
        esign_timestamp=res.submitted_at,
    )


# -----------------------------------------------------------------------------
# 4. Citizen Payment Status
# -----------------------------------------------------------------------------

@router.get(
    "/payment/{parcel_id}",
    response_model=CitizenPaymentDetail,
    summary="Track compensation disbursement and PFMS DBT mandate status",
)
async def get_citizen_payment_status(
    parcel_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CitizenPaymentDetail:
    """Track internal Direct Benefit Transfer (DBT) status route, simulated PFMS mandate ID, and account disbursement."""
    parcel_repo = ParcelRepository(db)
    parcel = await parcel_repo.get_by_id(parcel_id)
    if not parcel:
        raise EntityNotFoundException("LandParcel", parcel_id)

    ScopeChecker.verify_parcel_access(current_user, parcel)

    comp_service = CompensationService(db)
    assessment = await comp_service.get_or_create_assessment_for_parcel(parcel_id, current_user)

    award = assessment.award
    is_approved = assessment.status == "APPROVED" and award is not None

    payment_status = "READY_FOR_PFMS_TRANSFER" if is_approved else "PENDING_OFFICER_AWARD"
    pfms_mandate = f"PFMS-GOI-2026-{abs(hash(parcel.id)) % 90000 + 10000}" if is_approved else None

    return CitizenPaymentDetail(
        parcel_id=parcel.id,
        landowner_name=parcel.landowner_name,
        total_award_amount=award.total_awarded_amount if award else assessment.total_compensation,
        award_status=award.status if award else "NOT_ISSUED",
        disbursement_route="Direct Benefit Transfer (DBT)",
        masked_bank_account=parcel.masked_bank_account or "State Bank of India (••••4892)",
        bank_ifsc="SBIN0004128",
        pfms_mandate_id=pfms_mandate,
        payment_status=payment_status,
        disbursement_date=award.award_date if award else None,
        treasury_ref=award.digital_seal_ref if award else None,
    )


# -----------------------------------------------------------------------------
# 5. Citizen Grievance Creation & Tracking (Reusing GrievanceService)
# -----------------------------------------------------------------------------

@router.post(
    "/grievances",
    response_model=GrievanceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Lodge a statutory grievance petition",
)
async def lodge_citizen_grievance(
    payload: GrievanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GrievanceRead:
    """Lodge a grievance on an authorized land parcel with grounds of objection."""
    grievance_service = GrievanceService(db)
    return await grievance_service.create_grievance(payload, current_user)


@router.get(
    "/grievances",
    response_model=List[GrievanceRead],
    summary="List citizen's registered grievance petitions",
)
async def list_citizen_grievances(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[GrievanceRead]:
    """Retrieve all grievance petitions lodged by the authenticated citizen."""
    grievance_service = GrievanceService(db)
    return await grievance_service.list_grievances(current_user=current_user)


@router.get(
    "/grievances/{grievance_id}",
    response_model=GrievanceRead,
    summary="Track specific grievance petition and hearing resolution",
)
async def get_citizen_grievance(
    grievance_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GrievanceRead:
    """Retrieve status, assigned revenue officer, attached documents, and official hearing findings."""
    grievance_service = GrievanceService(db)
    return await grievance_service.get_grievance(grievance_id, current_user)


# -----------------------------------------------------------------------------
# 6. Citizen Notifications
# -----------------------------------------------------------------------------

@router.get(
    "/notifications",
    response_model=List[CitizenNotificationRead],
    summary="List notifications addressed to authenticated citizen",
)
async def list_citizen_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[CitizenNotificationRead]:
    """Retrieve alerts, gazette notices, and payment status updates."""
    audit_repo = AuditRepository(db)
    notifs = await audit_repo.list_user_notifications(current_user.id)
    return [
        CitizenNotificationRead(
            id=n.id,
            title=n.title,
            message=n.message,
            category=n.category,
            link_view=n.link_view,
            is_read=n.is_read,
            created_at=n.created_at,
        )
        for n in notifs
    ]


@router.put(
    "/notifications/{notification_id}/read",
    response_model=CitizenNotificationRead,
    summary="Mark notification as read",
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CitizenNotificationRead:
    """Acknowledge and mark an in-app notification as read."""
    audit_repo = AuditRepository(db)
    notif = await audit_repo.mark_notification_as_read(notification_id, current_user.id)
    if not notif:
        raise EntityNotFoundException("Notification", str(notification_id))
    return CitizenNotificationRead(
        id=notif.id,
        title=notif.title,
        message=notif.message,
        category=notif.category,
        link_view=notif.link_view,
        is_read=notif.is_read,
        created_at=notif.created_at,
    )


# -----------------------------------------------------------------------------
# 7. Citizen R&R Benefits Tracking (Reusing RrService)
# -----------------------------------------------------------------------------

@router.get(
    "/rr-benefits",
    response_model=Optional[AffectedFamilyRead],
    summary="Track Rehabilitation & Resettlement entitlements for citizen family",
)
async def get_citizen_rr_benefits(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Optional[AffectedFamilyRead]:
    """Retrieve RFCTLARR Second Schedule R&R entitlements, eligibility verification, and grant disbursements."""
    rr_service = RrService(db)
    return await rr_service.get_family_for_citizen(current_user)

