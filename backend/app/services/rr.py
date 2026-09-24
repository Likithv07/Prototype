import uuid
from datetime import date, datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import ScopeChecker
from app.core.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
    ForbiddenException,
    ValidationException,
)
from app.core.logging import get_logger
from app.models.rr import (
    AffectedFamily,
    ResettlementColony,
    RrBenefit,
    RrEligibility,
)
from app.models.user import User
from app.repositories.audit import AuditRepository
from app.repositories.project import ProjectRepository
from app.repositories.rr import RrRepository
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

logger = get_logger(__name__)


class RrService:
    """Domain service managing Rehabilitation and Resettlement (R&R) entitlements and disbursements."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.rr_repo = RrRepository(session)
        self.project_repo = ProjectRepository(session)
        self.audit_repo = AuditRepository(session)

    def _verify_family_access(self, current_user: User, family: AffectedFamily) -> None:
        """Enforce scoped data isolation: citizens can only access their own family package; officers scoped to jurisdiction."""
        roles = set(r.upper() for r in current_user.role_names)

        if "ADMIN" in roles or "CENTRAL_OFFICIAL" in roles:
            return

        if "CITIZEN" in roles:
            if family.citizen_user_id == current_user.id:
                return
            raise ForbiddenException("Access denied: Citizens can only access their own family R&R entitlements.")

        if "STATE_OFFICIAL" in roles:
            if not current_user.state or family.state.strip().lower() != current_user.state.strip().lower():
                raise ForbiddenException(
                    f"Access denied: Family is in state '{family.state}', but official scope is '{current_user.state}'."
                )
            return

        if "DISTRICT_OFFICER" in roles:
            state_match = bool(current_user.state and family.state.strip().lower() == current_user.state.strip().lower())
            dist_match = bool(current_user.district and family.district.strip().lower() == current_user.district.strip().lower())
            if not (state_match and dist_match):
                raise ForbiddenException(
                    f"Access denied: Family is in '{family.district}, {family.state}', but officer jurisdiction is '{current_user.district}, {current_user.state}'."
                )
            return

        raise ForbiddenException("Access denied: Insufficient R&R permissions.")

    def _to_eligibility_read(self, e: Optional[RrEligibility]) -> Optional[RrEligibilityRead]:
        if not e:
            return None
        return RrEligibilityRead(
            id=e.id,
            family_id=e.family_id,
            is_eligible=e.is_eligible,
            eligibility_criteria=e.eligibility_criteria,
            status=e.status,
            verified_by_id=e.verified_by_id,
            verified_by_name=e.verified_by_name,
            verification_date=e.verification_date,
            remarks=e.remarks,
        )

    def _to_benefit_read(self, b: RrBenefit) -> RrBenefitRead:
        return RrBenefitRead(
            id=b.id,
            family_id=b.family_id,
            benefit_type=b.benefit_type,
            description=b.description,
            monetary_value_lakhs=b.monetary_value_lakhs,
            housing_colony_name=b.housing_colony_name,
            housing_unit_number=b.housing_unit_number,
            benefit_status=b.benefit_status,
            disbursement_status=b.disbursement_status,
            disbursed_amount_lakhs=b.disbursed_amount_lakhs,
            disbursement_date=b.disbursement_date,
            disbursement_ref=b.disbursement_ref,
            remarks=b.remarks,
            created_at=b.created_at or datetime.now(timezone.utc),
        )

    def _to_family_read(self, f: AffectedFamily) -> AffectedFamilyRead:
        benefits_read = [self._to_benefit_read(b) for b in (f.benefits or [])]
        eligibility_read = self._to_eligibility_read(f.eligibility)

        return AffectedFamilyRead(
            id=f.id,
            project_id=f.project_id,
            parcel_id=f.parcel_id,
            citizen_user_id=f.citizen_user_id,
            head_of_family=f.head_of_family,
            aadhaar_masked=f.aadhaar_masked,
            contact_number=f.contact_number,
            state=f.state,
            district=f.district,
            village=f.village,
            family_members_count=f.family_members_count,
            affected_type=f.affected_type,
            relocation_status=f.relocation_status,
            total_financial_package_lakhs=f.total_financial_package_lakhs,
            status=f.status,
            created_at=f.created_at or datetime.now(timezone.utc),
            updated_at=f.updated_at or datetime.now(timezone.utc),
            eligibility=eligibility_read,
            benefits=benefits_read,
        )

    # -------------------------------------------------------------------------
    # 1. Citizen Access & Queries
    # -------------------------------------------------------------------------

    async def get_family_for_citizen(self, current_user: User) -> Optional[AffectedFamilyRead]:
        """Retrieve affected family details, eligibility, and R&R benefits for the authenticated citizen."""
        family = await self.rr_repo.get_family_by_citizen_user_id(current_user.id)
        if not family:
            return None
        self._verify_family_access(current_user, family)
        return self._to_family_read(family)

    async def get_family_by_id(self, family_id: str, current_user: User) -> AffectedFamilyRead:
        """Fetch affected family with scoped authorization check."""
        family = await self.rr_repo.get_family_by_id(family_id)
        if not family:
            raise EntityNotFoundException("AffectedFamily", family_id)

        self._verify_family_access(current_user, family)
        return self._to_family_read(family)

    async def list_affected_families(
        self,
        current_user: User,
        filter_params: Optional[AffectedFamilyFilter] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[AffectedFamilyRead]:
        """List affected families scoped to official's jurisdiction."""
        allowed_states, allowed_districts, _, _ = ScopeChecker.get_query_scope(current_user)
        families = await self.rr_repo.list_affected_families(
            filter_params=filter_params,
            allowed_states=allowed_states,
            allowed_districts=allowed_districts,
            skip=skip,
            limit=limit,
        )
        return [self._to_family_read(f) for f in families]

    # -------------------------------------------------------------------------
    # 2. Administrative Operations: Register Family, Eligibility, Benefits, Disburse
    # -------------------------------------------------------------------------

    async def create_affected_family(
        self,
        payload: AffectedFamilyCreate,
        current_user: User,
    ) -> AffectedFamilyRead:
        """Register a new project-affected family."""
        existing = await self.rr_repo.get_family_by_id(payload.id)
        if existing:
            raise EntityAlreadyExistsException("AffectedFamily", payload.id)

        project = await self.project_repo.get_by_id(payload.project_id)
        if not project:
            raise EntityNotFoundException("Project", payload.project_id)

        ScopeChecker.verify_project_access(current_user, project)

        family = AffectedFamily(
            id=payload.id,
            project_id=payload.project_id,
            parcel_id=payload.parcel_id,
            citizen_user_id=payload.citizen_user_id,
            head_of_family=payload.head_of_family,
            aadhaar_masked=payload.aadhaar_masked,
            contact_number=payload.contact_number,
            state=payload.state,
            district=payload.district,
            village=payload.village,
            family_members_count=payload.family_members_count,
            affected_type=payload.affected_type,
            relocation_status=payload.relocation_status,
            total_financial_package_lakhs=payload.total_financial_package_lakhs,
            status=payload.status,
        )

        saved = await self.rr_repo.create_affected_family(family)

        user_role = current_user.role_names[0] if current_user.role_names else "OFFICER"
        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name or current_user.username,
            role=user_role,
            action="CREATE_AFFECTED_FAMILY",
            module="rr",
            entity_type="AffectedFamily",
            entity_id=family.id,
            details=f"Registered affected family {family.id} for project {payload.project_id}.",
        )

        return self._to_family_read(saved)

    async def verify_eligibility(
        self,
        family_id: str,
        payload: RrEligibilityCreate,
        current_user: User,
    ) -> RrEligibilityRead:
        """Record statutory eligibility determination under Second Schedule of RFCTLARR Act 2013."""
        family = await self.rr_repo.get_family_by_id(family_id)
        if not family:
            raise EntityNotFoundException("AffectedFamily", family_id)

        self._verify_family_access(current_user, family)

        eligibility = family.eligibility
        if not eligibility:
            eligibility = RrEligibility(
                id=uuid.uuid4(),
                family_id=family.id,
                is_eligible=payload.is_eligible,
                eligibility_criteria=payload.eligibility_criteria,
                status="VERIFIED" if payload.is_eligible else "INELIGIBLE",
                verified_by_id=current_user.id,
                verified_by_name=current_user.full_name or current_user.username,
                verification_date=date.today(),
                remarks=payload.remarks,
            )
        else:
            eligibility.is_eligible = payload.is_eligible
            eligibility.eligibility_criteria = payload.eligibility_criteria
            eligibility.status = "VERIFIED" if payload.is_eligible else "INELIGIBLE"
            eligibility.verified_by_id = current_user.id
            eligibility.verified_by_name = current_user.full_name or current_user.username
            eligibility.verification_date = date.today()
            eligibility.remarks = payload.remarks

        saved = await self.rr_repo.save_eligibility(eligibility)

        user_role = current_user.role_names[0] if current_user.role_names else "OFFICER"
        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name or current_user.username,
            role=user_role,
            action="VERIFY_RR_ELIGIBILITY",
            module="rr",
            entity_type="AffectedFamily",
            entity_id=family.id,
            details=f"Eligibility set to is_eligible={payload.is_eligible}. Remarks: {payload.remarks or 'N/A'}",
        )

        # Notify affected citizen
        if family.citizen_user_id:
            await self.audit_repo.create_notification(
                title="R&R Statutory Eligibility Determined",
                message=f"Your family ({family.id}) has been verified as eligible for RFCTLARR Second Schedule R&R benefits.",
                category="rr",
                user_id=family.citizen_user_id,
                link_view="rr_dashboard",
            )

        return self._to_eligibility_read(saved)  # type: ignore

    async def add_benefit(
        self,
        family_id: str,
        payload: RrBenefitCreate,
        current_user: User,
    ) -> RrBenefitRead:
        """Add an R&R benefit entitlement to an affected family."""
        family = await self.rr_repo.get_family_by_id(family_id)
        if not family:
            raise EntityNotFoundException("AffectedFamily", family_id)

        self._verify_family_access(current_user, family)

        benefit = RrBenefit(
            id=uuid.uuid4(),
            family_id=family.id,
            benefit_type=payload.benefit_type,
            description=payload.description,
            monetary_value_lakhs=payload.monetary_value_lakhs,
            housing_colony_name=payload.housing_colony_name,
            housing_unit_number=payload.housing_unit_number,
            benefit_status="SANCTIONED",
            disbursement_status="PENDING",
            disbursed_amount_lakhs=0.0,
            remarks=payload.remarks,
        )

        saved = await self.rr_repo.add_benefit(benefit)

        # Update family financial package total
        family.total_financial_package_lakhs += payload.monetary_value_lakhs
        await self.session.flush()

        user_role = current_user.role_names[0] if current_user.role_names else "OFFICER"
        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name or current_user.username,
            role=user_role,
            action="CREATE_RR_BENEFIT",
            module="rr",
            entity_type="RrBenefit",
            entity_id=str(benefit.id),
            details=f"Sanctioned benefit {payload.benefit_type} of ₹{payload.monetary_value_lakhs} Lakhs for family {family.id}.",
        )

        return self._to_benefit_read(saved)

    async def disburse_benefit(
        self,
        benefit_id: uuid.UUID,
        payload: RrBenefitDisburseRequest,
        current_user: User,
    ) -> RrBenefitRead:
        """Disburse an R&R financial allowance or grant."""
        benefit = await self.rr_repo.get_benefit_by_id(benefit_id)
        if not benefit:
            raise EntityNotFoundException("RrBenefit", str(benefit_id))

        family = benefit.family or await self.rr_repo.get_family_by_id(benefit.family_id)
        if family:
            self._verify_family_access(current_user, family)

        if benefit.disbursement_status == "DISBURSED":
            raise ValidationException(f"Benefit {benefit_id} has already been disbursed.")
        if benefit.benefit_status != "SANCTIONED":
            raise ValidationException(f"Benefit {benefit_id} is not in SANCTIONED status.")
        if payload.disbursed_amount_lakhs > benefit.monetary_value_lakhs:
            raise ValidationException(
                f"Disbursed amount ({payload.disbursed_amount_lakhs} Lakhs) cannot exceed sanctioned monetary value ({benefit.monetary_value_lakhs} Lakhs)."
            )

        benefit.disbursement_status = "DISBURSED"
        benefit.disbursed_amount_lakhs = payload.disbursed_amount_lakhs
        benefit.disbursement_date = date.today()
        benefit.disbursement_ref = payload.disbursement_ref
        if payload.remarks:
            benefit.remarks = payload.remarks

        await self.session.flush()

        user_role = current_user.role_names[0] if current_user.role_names else "OFFICER"
        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name or current_user.username,
            role=user_role,
            action="DISBURSE_RR_BENEFIT",
            module="rr",
            entity_type="RrBenefit",
            entity_id=str(benefit.id),
            details=f"Disbursed ₹{payload.disbursed_amount_lakhs} Lakhs under ref {payload.disbursement_ref} for family {family.id if family else benefit.family_id}.",
        )

        # Notify citizen
        if family and family.citizen_user_id:
            await self.audit_repo.create_notification(
                title="R&R Allowance Disbursed",
                message=f"Financial grant of ₹{payload.disbursed_amount_lakhs} Lakhs has been disbursed under ref {payload.disbursement_ref}.",
                category="payment",
                user_id=family.citizen_user_id,
                link_view="citizen_compensation",
            )

        return self._to_benefit_read(benefit)

    async def list_resettlement_colonies(self, current_user: User) -> List[ResettlementColonyRead]:
        """List model resettlement colonies with civic amenities status."""
        allowed_states, allowed_districts, _, _ = ScopeChecker.get_query_scope(current_user)
        colonies = await self.rr_repo.list_resettlement_colonies(
            allowed_states=allowed_states,
            allowed_districts=allowed_districts,
        )
        return [
            ResettlementColonyRead(
                id=c.id,
                name=c.name,
                location=c.location,
                state=c.state,
                district=c.district,
                project_id=c.project_id,
                allotted_units=c.allotted_units,
                completed_units=c.completed_units,
                school_hospital_status=c.school_hospital_status,
                water_electricity_status=c.water_electricity_status,
                livelihood_grants_disbursed_cr=c.livelihood_grants_disbursed_cr,
                created_at=c.created_at,
            )
            for c in colonies
        ]

