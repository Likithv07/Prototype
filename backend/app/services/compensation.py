import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import ScopeChecker
from app.core.compensation_rules import (
    CompensationCalculationResult,
    CompensationRulesEngine,
    get_default_statutory_rule,
)
from app.core.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
    ForbiddenException,
    ValidationException,
)
from app.core.logging import get_logger
from app.models.compensation import (
    Award,
    CompensationAssessment,
    CompensationComponent,
    CompensationHistory,
    CompensationRule,
)
from app.models.document import Document
from app.models.field import FieldPhoto, FieldSurveyRecord
from app.models.parcel import LandParcel
from app.models.user import User
from app.models.workflow import WorkflowInstance
from app.repositories.audit import AuditRepository
from app.repositories.compensation import CompensationRepository
from app.repositories.parcel import ParcelRepository
from app.repositories.project import ProjectRepository
from app.schemas.compensation import (
    AwardApprovalRequest,
    AwardRead,
    CompensationAssessmentCreate,
    CompensationAssessmentRead,
    CompensationAssessmentUpdate,
    CompensationBreakdownRead,
    CompensationCalculateRequest,
    CompensationComponentCreate,
    CompensationComponentRead,
    CompensationHistoryRead,
    RevisionRequest,
)

logger = get_logger(__name__)


class CompensationService:
    """Service orchestrating statutory compensation calculations, itemized valuations, and award issuance."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.comp_repo = CompensationRepository(session)
        self.parcel_repo = ParcelRepository(session)
        self.project_repo = ProjectRepository(session)
        self.audit_repo = AuditRepository(session)

    # -------------------------------------------------------------------------
    # Helper mappers
    # -------------------------------------------------------------------------

    def _to_component_read(self, c: CompensationComponent) -> CompensationComponentRead:
        return CompensationComponentRead(
            id=c.id,
            assessment_id=c.assessment_id,
            component_type=c.component_type,
            name=c.name,
            unit=c.unit,
            quantity=c.quantity,
            rate_per_unit=c.rate_per_unit,
            gross_value=c.gross_value,
            depreciation_percentage=c.depreciation_percentage,
            net_value=c.net_value,
            valuation_date=c.valuation_date,
            remarks=c.remarks,
        )

    def _to_award_read(self, a: Optional[Award]) -> Optional[AwardRead]:
        if not a:
            return None
        return AwardRead(
            id=a.id,
            assessment_id=a.assessment_id,
            parcel_id=a.parcel_id,
            project_id=a.project_id,
            award_number=a.award_number,
            award_date=a.award_date,
            competent_authority_id=a.competent_authority_id,
            competent_authority_name=a.competent_authority_name,
            competent_authority_designation=a.competent_authority_designation,
            total_awarded_amount=a.total_awarded_amount,
            digital_seal_ref=a.digital_seal_ref,
            status=a.status,
            gazette_ref=a.gazette_ref,
            created_at=a.created_at or datetime.now(timezone.utc),
        )

    def _to_history_read(self, h: CompensationHistory) -> CompensationHistoryRead:
        return CompensationHistoryRead(
            id=h.id,
            assessment_id=h.assessment_id,
            action=h.action,
            from_status=h.from_status,
            to_status=h.to_status,
            from_total=h.from_total,
            to_total=h.to_total,
            performed_by_id=h.performed_by_id,
            performed_by_name=h.performed_by_name,
            performed_by_role=h.performed_by_role,
            remarks=h.remarks,
            timestamp=h.timestamp or datetime.now(timezone.utc),
        )

    def _to_assessment_read(self, a: CompensationAssessment) -> CompensationAssessmentRead:
        components_read = [self._to_component_read(c) for c in (a.components or [])]
        history_read = [self._to_history_read(h) for h in (a.history or [])]
        award_read = self._to_award_read(a.award)
        fallback_uuid = uuid.UUID("00000000-0000-0000-0000-000000000000")

        return CompensationAssessmentRead(
            id=a.id,
            parcel_id=a.parcel_id,
            project_id=a.project_id,
            landowner_id=a.landowner_id,
            landowner_name=a.landowner_name,
            survey_number=a.survey_number,
            rule_id=a.rule_id,
            rule_version=a.rule_version,
            status=a.status,
            land_area_acres=a.land_area_acres,
            market_value_per_acre=a.market_value_per_acre,
            multiplier_factor=a.multiplier_factor,
            asset_valuation=a.asset_valuation,
            basic_land_value=a.basic_land_value,
            multiplied_land_value=a.multiplied_land_value,
            market_value_plus_assets=a.market_value_plus_assets,
            solatium_percentage=a.solatium_percentage,
            solatium_amount=a.solatium_amount,
            interest_percentage=a.interest_percentage,
            interest_amount=a.interest_amount,
            total_compensation=a.total_compensation,
            calculated_by_id=a.calculated_by_id or fallback_uuid,
            submitted_by_id=a.submitted_by_id,
            submitted_at=a.submitted_at,
            submission_notes=a.submission_notes,
            approved_by_id=a.approved_by_id,
            approved_at=a.approved_at,
            approval_remarks=a.approval_remarks,
            digital_signature_ref=a.digital_signature_ref,
            rejection_reason=a.rejection_reason,
            revision_notes=a.revision_notes,
            components=components_read,
            award=award_read,
            history=history_read,
            created_at=a.created_at or datetime.now(timezone.utc),
            updated_at=a.updated_at or datetime.now(timezone.utc),
        )

    # -------------------------------------------------------------------------
    # 1. Interactive Statutory Calculator
    # -------------------------------------------------------------------------

    async def calculate(
        self,
        parcel_id: str,
        calc_in: CompensationCalculateRequest,
        current_user: User,
    ) -> CompensationBreakdownRead:
        """Calculate statutory compensation using the active versioned rules engine."""
        parcel = await self.parcel_repo.get_by_id(parcel_id)
        if not parcel:
            raise EntityNotFoundException("LandParcel", parcel_id)

        ScopeChecker.verify_parcel_access(current_user, parcel)

        # Retrieve active rule (with state override if applicable)
        rule = await self.comp_repo.get_active_rule(rule_id=calc_in.rule_id, state=parcel.state)
        if not rule:
            rule = get_default_statutory_rule()

        engine = CompensationRulesEngine(rule)

        # Default inputs to parcel cadastral values if omitted
        area = calc_in.land_area_acres or parcel.area_acres or 1.0
        rate = calc_in.market_value_per_acre or parcel.market_value_per_acre or 100000.0
        multiplier = calc_in.multiplier_factor or parcel.multiplier_factor or 1.0
        assets = calc_in.asset_valuation if calc_in.asset_valuation is not None else (parcel.asset_valuation or 0.0)

        result: CompensationCalculationResult = engine.calculate(
            land_area_acres=area,
            market_value_per_acre=rate,
            multiplier_factor=multiplier,
            asset_valuation=assets,
            custom_solatium_pct=calc_in.solatium_percentage,
            custom_interest_pct=calc_in.interest_percentage,
        )

        return CompensationBreakdownRead(
            land_area_acres=result.land_area_acres,
            market_value_per_acre=result.market_value_per_acre,
            multiplier_factor=result.multiplier_factor,
            asset_valuation=result.asset_valuation,
            basic_land_value=result.basic_land_value,
            multiplied_land_value=result.multiplied_land_value,
            market_value_plus_assets=result.market_value_plus_assets,
            solatium_percentage=result.solatium_percentage,
            solatium_amount=result.solatium_amount,
            interest_percentage=result.interest_percentage,
            interest_amount=result.interest_amount,
            total_compensation=result.total_compensation,
            rule_id=result.rule_id,
            rule_version=result.rule_version,
        )

    # -------------------------------------------------------------------------
    # 2. Assessment CRUD & Formulations
    # -------------------------------------------------------------------------

    async def get_or_create_assessment_for_parcel(
        self,
        parcel_id: str,
        current_user: User,
    ) -> CompensationAssessmentRead:
        """Retrieve existing assessment or generate a draft from parcel cadastral registry."""
        parcel = await self.parcel_repo.get_by_id(parcel_id)
        if not parcel:
            raise EntityNotFoundException("LandParcel", parcel_id)

        ScopeChecker.verify_parcel_access(current_user, parcel)

        assessment = await self.comp_repo.get_assessment_by_parcel_id(parcel_id)
        if assessment:
            return self._to_assessment_read(assessment)

        # Initialize draft assessment from parcel base registry
        rule = await self.comp_repo.get_active_rule(state=parcel.state) or get_default_statutory_rule()
        engine = CompensationRulesEngine(rule)

        area = parcel.area_acres or 1.0
        rate = parcel.market_value_per_acre or 100000.0
        multiplier = parcel.multiplier_factor or 1.0
        assets = parcel.asset_valuation or 0.0

        calc = engine.calculate(
            land_area_acres=area,
            market_value_per_acre=rate,
            multiplier_factor=multiplier,
            asset_valuation=assets,
        )

        assessment_id = f"COMP-{parcel.id}"
        new_assessment = CompensationAssessment(
            id=assessment_id,
            parcel_id=parcel.id,
            project_id=parcel.project_id,
            landowner_id=parcel.owner_user_id,
            landowner_name=parcel.landowner_name,
            survey_number=parcel.survey_number,
            rule_id=rule.id,
            rule_version=rule.version,
            status="DRAFT",
            land_area_acres=calc.land_area_acres,
            market_value_per_acre=calc.market_value_per_acre,
            multiplier_factor=calc.multiplier_factor,
            asset_valuation=calc.asset_valuation,
            basic_land_value=calc.basic_land_value,
            multiplied_land_value=calc.multiplied_land_value,
            market_value_plus_assets=calc.market_value_plus_assets,
            solatium_percentage=calc.solatium_percentage,
            solatium_amount=calc.solatium_amount,
            interest_percentage=calc.interest_percentage,
            interest_amount=calc.interest_amount,
            total_compensation=calc.total_compensation,
            calculated_by_id=current_user.id,
        )
        created = await self.comp_repo.create_assessment(new_assessment)

        user_role = current_user.role_names[0] if current_user.role_names else "OFFICER"
        history = CompensationHistory(
            assessment_id=created.id,
            action="CALCULATED",
            from_status=None,
            to_status="DRAFT",
            from_total=0.0,
            to_total=calc.total_compensation,
            performed_by_id=current_user.id,
            performed_by_name=current_user.full_name,
            performed_by_role=user_role,
            remarks=f"Initial draft formulation created for parcel {parcel.id} under {rule.name}",
        )
        await self.comp_repo.add_history(history)

        fresh = await self.comp_repo.get_assessment_by_id(created.id)
        return self._to_assessment_read(fresh or created)

    async def update_assessment(
        self,
        assessment_id: str,
        update_in: CompensationAssessmentUpdate,
        current_user: User,
    ) -> CompensationAssessmentRead:
        """Update compensation assessment parameters or itemized components while in DRAFT or REVISION_REQUESTED."""
        assessment = await self.comp_repo.get_assessment_by_id(assessment_id)
        if not assessment:
            raise EntityNotFoundException("CompensationAssessment", assessment_id)

        if assessment.parcel:
            ScopeChecker.verify_parcel_access(current_user, assessment.parcel)

        if assessment.status not in ["DRAFT", "REVISION_REQUESTED"]:
            raise ValidationException(
                f"Cannot modify assessment in status '{assessment.status}'. Only 'DRAFT' or 'REVISION_REQUESTED' can be edited."
            )

        rule = await self.comp_repo.get_active_rule(rule_id=assessment.rule_id) or get_default_statutory_rule()
        engine = CompensationRulesEngine(rule)

        area = update_in.land_area_acres if update_in.land_area_acres is not None else assessment.land_area_acres
        rate = update_in.market_value_per_acre if update_in.market_value_per_acre is not None else assessment.market_value_per_acre
        multiplier = update_in.multiplier_factor if update_in.multiplier_factor is not None else assessment.multiplier_factor

        # Calculate attached asset valuation from components if provided
        assets_total = assessment.asset_valuation
        if update_in.components is not None:
            # Add or update components
            comp_sum = 0.0
            for c_in in update_in.components:
                gross = c_in.gross_value if c_in.gross_value is not None else round(c_in.quantity * c_in.rate_per_unit, 2)
                depreciation = round(gross * (c_in.depreciation_percentage / 100.0), 2)
                net = round(gross - depreciation, 2)
                comp_sum += net

                comp = CompensationComponent(
                    assessment_id=assessment.id,
                    component_type=c_in.component_type,
                    name=c_in.name,
                    unit=c_in.unit,
                    quantity=c_in.quantity,
                    rate_per_unit=c_in.rate_per_unit,
                    gross_value=gross,
                    depreciation_percentage=c_in.depreciation_percentage,
                    net_value=net,
                    valuation_date=c_in.valuation_date or date.today(),
                    remarks=c_in.remarks,
                )
                await self.comp_repo.add_component(comp)
            assets_total = comp_sum
        elif update_in.asset_valuation is not None:
            assets_total = update_in.asset_valuation

        calc = engine.calculate(
            land_area_acres=area,
            market_value_per_acre=rate,
            multiplier_factor=multiplier,
            asset_valuation=assets_total,
        )

        prev_total = assessment.total_compensation
        assessment.land_area_acres = calc.land_area_acres
        assessment.market_value_per_acre = calc.market_value_per_acre
        assessment.multiplier_factor = calc.multiplier_factor
        assessment.asset_valuation = calc.asset_valuation
        assessment.basic_land_value = calc.basic_land_value
        assessment.multiplied_land_value = calc.multiplied_land_value
        assessment.market_value_plus_assets = calc.market_value_plus_assets
        assessment.solatium_amount = calc.solatium_amount
        assessment.interest_amount = calc.interest_amount
        assessment.total_compensation = calc.total_compensation

        if update_in.notes:
            assessment.submission_notes = update_in.notes

        await self.comp_repo.update_assessment(assessment)

        user_role = current_user.role_names[0] if current_user.role_names else "OFFICER"
        history = CompensationHistory(
            assessment_id=assessment.id,
            action="UPDATED",
            from_status=assessment.status,
            to_status=assessment.status,
            from_total=prev_total,
            to_total=calc.total_compensation,
            performed_by_id=current_user.id,
            performed_by_name=current_user.full_name,
            performed_by_role=user_role,
            remarks=update_in.notes or "Recalculated valuation and updated attached assets",
        )
        await self.comp_repo.add_history(history)

        fresh = await self.comp_repo.get_assessment_by_id(assessment.id)
        return self._to_assessment_read(fresh or assessment)

    async def submit_assessment(
        self,
        assessment_id: str,
        current_user: User,
    ) -> CompensationAssessmentRead:
        """Submit compensation assessment for supervisory review and Section 31 award approval."""
        assessment = await self.comp_repo.get_assessment_by_id(assessment_id)
        if not assessment:
            raise EntityNotFoundException("CompensationAssessment", assessment_id)

        if assessment.parcel:
            ScopeChecker.verify_parcel_access(current_user, assessment.parcel)

        if assessment.status not in ["DRAFT", "REVISION_REQUESTED"]:
            raise ValidationException(
                f"Cannot submit assessment in status '{assessment.status}'. Must be DRAFT or REVISION_REQUESTED."
            )

        if assessment.total_compensation <= 0:
            raise ValidationException("Cannot submit assessment with zero or negative total compensation.")

        prev_status = assessment.status
        assessment.status = "SUBMITTED"
        assessment.submitted_by_id = current_user.id
        assessment.submitted_at = datetime.now(timezone.utc)
        await self.comp_repo.update_assessment(assessment)

        user_role = current_user.role_names[0] if current_user.role_names else "OFFICER"
        history = CompensationHistory(
            assessment_id=assessment.id,
            action="SUBMITTED",
            from_status=prev_status,
            to_status="SUBMITTED",
            from_total=assessment.total_compensation,
            to_total=assessment.total_compensation,
            performed_by_id=current_user.id,
            performed_by_name=current_user.full_name,
            performed_by_role=user_role,
            remarks="Submitted for statutory Section 31 award review by Competent Authority",
        )
        await self.comp_repo.add_history(history)

        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=user_role,
            action="COMPENSATION_SUBMITTED",
            module="compensation",
            entity_type="CompensationAssessment",
            entity_id=assessment.id,
            details=f"Assessment '{assessment.id}' submitted for Section 31 review. Total: ₹{assessment.total_compensation}",
        )

        fresh = await self.comp_repo.get_assessment_by_id(assessment.id)
        return self._to_assessment_read(fresh or assessment)

    # -------------------------------------------------------------------------
    # 3. Multi-Gated Statutory Approval & Award Issuance
    # -------------------------------------------------------------------------

    async def approve_and_issue_award(
        self,
        assessment_id: str,
        approval_in: AwardApprovalRequest,
        current_user: User,
    ) -> CompensationAssessmentRead:
        """Supervisory officer approves assessment and issues statutory Land Acquisition Award.
        
        Strictly enforces 6 mandatory verification gates:
        1. User Permission (District Officer, State Official, Admin).
        2. Parcel Status (Active, not disputed, not proposed, not already possessed).
        3. Required Evidence (At least 1 verified field photo or survey record).
        4. Required Documents (At least 1 verified statutory document attached).
        5. Workflow Stage (Project active workflow at/beyond survey/valuation stage).
        6. Calculation Completeness (Total, basic land value, and solatium > 0).
        """
        # Gate 1: User Permission check
        allowed_roles = ["ADMIN", "STATE_OFFICIAL", "DISTRICT_OFFICER"]
        if not any(r in current_user.role_names for r in allowed_roles):
            raise ForbiddenException(
                "Access denied: Only District Officers, State Officials, or Administrators can approve statutory awards."
            )

        if not approval_in.digital_signature_consent:
            raise ValidationException(
                "Statutory compliance checkbox must be accepted before digital award sign-off."
            )

        assessment = await self.comp_repo.get_assessment_by_id(assessment_id)
        if not assessment:
            raise EntityNotFoundException("CompensationAssessment", assessment_id)

        parcel = await self.parcel_repo.get_by_id(assessment.parcel_id)
        if not parcel:
            raise EntityNotFoundException("LandParcel", assessment.parcel_id)

        ScopeChecker.verify_parcel_access(current_user, parcel)

        # Gate 2: Parcel Status check
        if parcel.acquisition_status in ["Proposed", "Disputed", "Possession Completed"]:
            raise ValidationException(
                f"Cannot approve compensation for parcel in acquisition status '{parcel.acquisition_status}'. "
                "Must be under active verification or notification stage."
            )
        if parcel.compensation_status == "Approved" and assessment.status == "APPROVED":
            raise ValidationException("Compensation award has already been approved for this parcel.")

        # Gate 3: Required Evidence check (verified field photos or survey records)
        stmt_photos = select(FieldPhoto).where(
            FieldPhoto.parcel_id == parcel.id,
            FieldPhoto.status == "Verified",
        )
        res_photos = await self.session.execute(stmt_photos)
        verified_photos = res_photos.scalars().all()

        stmt_surveys = select(FieldSurveyRecord).where(
            FieldSurveyRecord.parcel_id == parcel.id,
            FieldSurveyRecord.verification_status == "Verified",
        )
        res_surveys = await self.session.execute(stmt_surveys)
        verified_surveys = res_surveys.scalars().all()

        if not verified_photos and not verified_surveys:
            raise ValidationException(
                "Statutory Gate 3 Violation: At least one verified field survey record or verified "
                "geotagged field photograph is required before compensation approval."
            )

        # Gate 4: Required Documents check (verified statutory documents)
        stmt_docs = select(Document).where(
            Document.parcel_id == parcel.id,
            Document.is_verified == True,
        )
        res_docs = await self.session.execute(stmt_docs)
        verified_docs = res_docs.scalars().all()

        if not verified_docs:
            raise ValidationException(
                "Statutory Gate 4 Violation: At least one verified statutory document "
                "(e.g. Form 16-B Field Valuation Report or Title Deed) must be on record."
            )

        # Gate 5: Workflow Stage check
        stmt_wf = select(WorkflowInstance).where(WorkflowInstance.project_id == parcel.project_id)
        res_wf = await self.session.execute(stmt_wf)
        wf_instance = res_wf.scalars().first()

        if wf_instance and wf_instance.current_stage:
            # Order 1 = project planning, Order 2 = land requirement. Must be >= 3
            if wf_instance.current_stage.stage_order < 3:
                raise ValidationException(
                    f"Statutory Gate 5 Violation: Project workflow is currently in stage '{wf_instance.current_stage.name}'. "
                    "Compensation formulation requires project to be at or beyond 'Survey / Land Records' stage."
                )

        # Gate 6: Calculation Completeness
        if (
            assessment.total_compensation <= 0
            or assessment.basic_land_value <= 0
            or assessment.solatium_amount <= 0
        ):
            raise ValidationException(
                "Statutory Gate 6 Violation: Incomplete compensation calculation. "
                "Basic land value, solatium, and total compensation must be positive non-zero values."
            )

        # All 6 Gates Passed: Execute Atomic Statutory Approval
        prev_status = assessment.status
        assessment.status = "APPROVED"
        assessment.approved_by_id = current_user.id
        assessment.approved_at = datetime.now(timezone.utc)
        assessment.approval_remarks = approval_in.approval_remarks or "Statutory compensation award digitally certified"
        assessment.digital_signature_ref = approval_in.digital_seal_ref
        await self.comp_repo.update_assessment(assessment)

        # Generate Statutory Award Entity under Section 31
        award_id = f"AWARD-{parcel.id}"
        award_num = f"LAO/{parcel.district[:3].upper()}/{date.today().year}/AW-{parcel.survey_number.replace('/', '-')}"
        user_role = current_user.role_names[0] if current_user.role_names else "COMPETENT_AUTHORITY"

        award = Award(
            id=award_id,
            assessment_id=assessment.id,
            parcel_id=parcel.id,
            project_id=parcel.project_id,
            award_number=award_num,
            award_date=date.today(),
            competent_authority_id=current_user.id,
            competent_authority_name=current_user.full_name,
            competent_authority_designation=user_role,
            total_awarded_amount=assessment.total_compensation,
            digital_seal_ref=approval_in.digital_seal_ref,
            status="ISSUED",
        )
        created_award = await self.comp_repo.create_award(award)

        # Synchronize Cadastral LandParcel record
        parcel.compensation_status = "Approved"
        parcel.total_compensation = assessment.total_compensation
        parcel.market_value_per_acre = assessment.market_value_per_acre
        parcel.multiplier_factor = assessment.multiplier_factor
        parcel.asset_valuation = assessment.asset_valuation
        await self.parcel_repo.update(parcel)

        # Record History Ledger Entry
        history = CompensationHistory(
            assessment_id=assessment.id,
            action="APPROVED",
            from_status=prev_status,
            to_status="APPROVED",
            from_total=assessment.total_compensation,
            to_total=assessment.total_compensation,
            performed_by_id=current_user.id,
            performed_by_name=current_user.full_name,
            performed_by_role=user_role,
            remarks=f"Statutory Award {award_num} digitally approved with DSC seal {approval_in.digital_seal_ref}",
        )
        await self.comp_repo.add_history(history)

        # Audit Log Event
        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=user_role,
            action="COMPENSATION_AWARD_APPROVED",
            module="compensation",
            entity_type="Award",
            entity_id=created_award.id,
            details=f"Statutory Award '{award_num}' issued for parcel '{parcel.id}'. Amount: ₹{assessment.total_compensation:,.2f}",
        )

        # Notification for Landowner if user profile exists
        if parcel.owner_user_id:
            await self.audit_repo.create_notification(
                user_id=parcel.owner_user_id,
                title="Statutory Compensation Award Approved",
                message=f"Land Acquisition Award {award_num} for ₹{assessment.total_compensation:,.2f} has been approved under Section 31.",
                notification_type="COMPENSATION_AWARD",
                link_url=f"/citizen/compensation?parcelId={parcel.id}",
            )

        fresh = await self.comp_repo.get_assessment_by_id(assessment.id)
        return self._to_assessment_read(fresh or assessment)

    # -------------------------------------------------------------------------
    # 4. Revision Request & Rejection
    # -------------------------------------------------------------------------

    async def reject_or_request_revision(
        self,
        assessment_id: str,
        revision_in: RevisionRequest,
        current_user: User,
    ) -> CompensationAssessmentRead:
        """Supervisory officer rejects or requests revision with mandatory statutory grounds."""
        allowed_roles = ["ADMIN", "STATE_OFFICIAL", "DISTRICT_OFFICER"]
        if not any(r in current_user.role_names for r in allowed_roles):
            raise ForbiddenException("Only supervisory officers can request revision or reject compensation.")

        assessment = await self.comp_repo.get_assessment_by_id(assessment_id)
        if not assessment:
            raise EntityNotFoundException("CompensationAssessment", assessment_id)

        if assessment.parcel:
            ScopeChecker.verify_parcel_access(current_user, assessment.parcel)

        prev_status = assessment.status
        assessment.status = "REVISION_REQUESTED"
        assessment.revision_notes = revision_in.revision_notes
        await self.comp_repo.update_assessment(assessment)

        user_role = current_user.role_names[0] if current_user.role_names else "OFFICER"
        history = CompensationHistory(
            assessment_id=assessment.id,
            action="REVISION_REQUESTED",
            from_status=prev_status,
            to_status="REVISION_REQUESTED",
            from_total=assessment.total_compensation,
            to_total=assessment.total_compensation,
            performed_by_id=current_user.id,
            performed_by_name=current_user.full_name,
            performed_by_role=user_role,
            remarks=revision_in.revision_notes,
        )
        await self.comp_repo.add_history(history)

        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=user_role,
            action="COMPENSATION_REVISION_REQUESTED",
            module="compensation",
            entity_type="CompensationAssessment",
            entity_id=assessment.id,
            details=f"Revision requested for assessment '{assessment.id}': {revision_in.revision_notes}",
        )

        fresh = await self.comp_repo.get_assessment_by_id(assessment.id)
        return self._to_assessment_read(fresh or assessment)

    async def get_history(
        self,
        assessment_id: str,
        current_user: User,
    ) -> List[CompensationHistoryRead]:
        """Retrieve complete immutable audit history for an assessment."""
        assessment = await self.comp_repo.get_assessment_by_id(assessment_id)
        if not assessment:
            raise EntityNotFoundException("CompensationAssessment", assessment_id)

        if assessment.parcel:
            ScopeChecker.verify_parcel_access(current_user, assessment.parcel)

        histories = await self.comp_repo.get_history(assessment_id)
        return [self._to_history_read(h) for h in histories]

