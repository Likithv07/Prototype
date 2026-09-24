import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.workflow import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowStageDefinition,
    WorkflowTransitionDefinition,
    WorkflowTransitionHistory,
)

# Standard 14-Stage Statutory Land Acquisition Workflow Specification (SIH / RFCTLARR 2013)
STATUTORY_STAGES = [
    (1, "PROJECT_PLANNING", "Project Planning & DPR Feasibility", "Initial feasibility, DPR preparation, and ministry sanction", "CENTRAL_OFFICIAL", 30, True, False),
    (2, "LAND_REQUIREMENT", "Land Requirement Demarcation", "Demarcation of required acreage and alignment bounds", "STATE_OFFICIAL", 45, False, False),
    (3, "SURVEY_RECORDS", "Cadastral Survey & Land Records", "LiDAR / DGPS survey and revenue land records matching", "FIELD_OFFICER", 60, False, False),
    (4, "PARCEL_IDENTIFICATION", "Parcel Identification & Demarcation", "Detailed identification of individual survey numbers and parcels", "DISTRICT_OFFICER", 30, False, False),
    (5, "SECTION_11_NOTIFICATION", "Statutory Notification (Sec 11)", "Publication of preliminary statutory acquisition notice in gazette", "DISTRICT_OFFICER", 60, False, False),
    (6, "OBJECTIONS_CLAIMS", "Objections & Claims Enquiry (Sec 15)", "Public hearing and disposal of citizen title and boundary objections", "DISTRICT_OFFICER", 60, False, False),
    (7, "FIELD_VERIFICATION", "Ground Field Verification", "On-ground joint inspection, asset enumeration, and evidence capture", "FIELD_OFFICER", 45, False, False),
    (8, "COMPENSATION_ASSESSMENT", "Compensation Assessment & Valuation", "RFCTLARR 2013 calculation, market rate multiplier, and solatium", "DISTRICT_OFFICER", 45, False, False),
    (9, "AWARD_ENQUIRY", "Collector Award Declaration (Sec 23)", "Formal determination of compensation award by District Magistrate / LAO", "DISTRICT_OFFICER", 30, False, False),
    (10, "CONSENT_ACQUISITION", "Consent & Agreement Execution", "Execution of voluntary consent agreements and bank details verification", "DISTRICT_OFFICER", 60, False, False),
    (11, "PAYMENT_DISBURSEMENT", "Direct Payment Disbursement", "Direct Benefit Transfer (DBT) to verified landowner bank accounts", "STATE_OFFICIAL", 30, False, False),
    (12, "POSSESSION_HANDOVER", "Physical Possession & Demarcation", "Demarcation fencing and handover of physical possession to agency", "DISTRICT_OFFICER", 45, False, False),
    (13, "MUTATION_RECORD", "Revenue Land Record Mutation", "Formal Tehsil mutation transfer in state land registries", "DISTRICT_OFFICER", 30, False, False),
    (14, "MONITORING_CLOSURE", "Monitoring, Commissioning & Closure", "Final post-acquisition compliance review and project commissioning", "CENTRAL_OFFICIAL", 30, False, True),
]

STATUTORY_TRANSITIONS = [
    ("PROJECT_PLANNING", "LAND_REQUIREMENT", "APPROVE_PLANNING", "Approve feasibility DPR and project alignment", "CENTRAL_OFFICIAL", "project:approve", False),
    ("LAND_REQUIREMENT", "SURVEY_RECORDS", "DEMARCATE_ALIGNMENT", "Confirm land requirement and order cadastral survey", "STATE_OFFICIAL", "project:update", False),
    ("SURVEY_RECORDS", "PARCEL_IDENTIFICATION", "FINALIZE_SURVEY", "Upload cadastral records and boundary survey", "FIELD_OFFICER", "survey:conduct", False),
    ("PARCEL_IDENTIFICATION", "SECTION_11_NOTIFICATION", "REGISTER_PARCELS", "Validate parcel registry for statutory gazette", "DISTRICT_OFFICER", "parcel:manage_district", False),
    ("SECTION_11_NOTIFICATION", "OBJECTIONS_CLAIMS", "PUBLISH_NOTIFICATION", "Publish preliminary Section 11 gazette notification", "DISTRICT_OFFICER", "compensation:approve_district", True),
    ("OBJECTIONS_CLAIMS", "FIELD_VERIFICATION", "DISPOSE_OBJECTIONS", "Hear and formally dispose citizen objections", "DISTRICT_OFFICER", "grievance:resolve_district", True),
    ("OBJECTIONS_CLAIMS", "SURVEY_RECORDS", "REQUEST_RE_SURVEY", "Refer boundary discrepancy back for field re-survey", "DISTRICT_OFFICER", "survey:assign", True),
    ("FIELD_VERIFICATION", "COMPENSATION_ASSESSMENT", "COMPLETE_VERIFICATION", "Submit verified ground inspection and evidence", "FIELD_OFFICER", "verification:submit", False),
    ("COMPENSATION_ASSESSMENT", "AWARD_ENQUIRY", "SUBMIT_VALUATION", "Finalize valuation matrix and solatium schedule", "DISTRICT_OFFICER", "compensation:approve_district", False),
    ("AWARD_ENQUIRY", "CONSENT_ACQUISITION", "DECLARE_AWARD", "Declare formal Section 23 land acquisition award", "DISTRICT_OFFICER", "compensation:approve_district", True),
    ("CONSENT_ACQUISITION", "PAYMENT_DISBURSEMENT", "EXECUTE_CONSENT", "Verify landowner consent deeds and bank accounts", "DISTRICT_OFFICER", "compensation:approve_district", False),
    ("PAYMENT_DISBURSEMENT", "POSSESSION_HANDOVER", "DISBURSE_FUNDS", "Disburse electronic payment to eligible beneficiaries", "STATE_OFFICIAL", "awards:approve_state", True),
    ("POSSESSION_HANDOVER", "MUTATION_RECORD", "TAKE_POSSESSION", "Execute physical takeover and boundary clearance", "DISTRICT_OFFICER", "parcel:manage_district", True),
    ("MUTATION_RECORD", "MONITORING_CLOSURE", "RECORD_MUTATION", "Complete Tehsil record mutation in revenue registry", "DISTRICT_OFFICER", "parcel:manage_district", True),
    ("MONITORING_CLOSURE", "MONITORING_CLOSURE", "CLOSE_PROJECT", "Commission infrastructure project and close acquisition", "CENTRAL_OFFICIAL", "project:approve_macro", True),
]


class WorkflowRepository:
    """Repository managing workflow definitions, instances, and transition execution."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def seed_default_workflow_definition(self) -> WorkflowDefinition:
        """Seed default 14-stage statutory RFCTLARR workflow definition if not present."""
        stmt = (
            select(WorkflowDefinition)
            .where(WorkflowDefinition.code == "STANDARD_RFCTLARR_2013")
            .options(
                selectinload(WorkflowDefinition.stages),
                selectinload(WorkflowDefinition.transitions),
            )
        )
        res = await self.session.execute(stmt)
        wf_def = res.scalars().first()

        if wf_def:
            return wf_def

        # Create Blueprint
        wf_def = WorkflowDefinition(
            code="STANDARD_RFCTLARR_2013",
            name="Standard RFCTLARR 2013 Statutory Lifecycle",
            description="Comprehensive 14-stage statutory workflow from project planning to revenue mutation and closure",
            version=1,
            is_active=True,
            is_default=True,
        )
        self.session.add(wf_def)
        await self.session.flush()

        # Seed Stages
        for order, code, name, desc, role, sla, initial, terminal in STATUTORY_STAGES:
            stage = WorkflowStageDefinition(
                workflow_definition_id=wf_def.id,
                stage_code=code,
                name=name,
                description=desc,
                stage_order=order,
                required_role=role,
                sla_days=sla,
                is_initial=initial,
                is_terminal=terminal,
            )
            self.session.add(stage)

        # Seed Transitions
        for from_code, to_code, action, desc, role, perm, req_remarks in STATUTORY_TRANSITIONS:
            trans = WorkflowTransitionDefinition(
                workflow_definition_id=wf_def.id,
                from_stage_code=from_code,
                to_stage_code=to_code,
                action_name=action,
                description=desc,
                required_role=role,
                required_permission=perm,
                requires_remarks=req_remarks,
            )
            self.session.add(trans)

        await self.session.flush()
        await self.session.refresh(wf_def)
        return wf_def

    async def get_default_workflow_definition(self) -> WorkflowDefinition:
        """Fetch or create the default workflow blueprint."""
        return await self.seed_default_workflow_definition()

    async def get_instance_by_project_id(self, project_id: str) -> Optional[WorkflowInstance]:
        """Fetch active workflow instance attached to project."""
        stmt = (
            select(WorkflowInstance)
            .where(WorkflowInstance.project_id == project_id)
            .options(
                selectinload(WorkflowInstance.workflow_definition).selectinload(WorkflowDefinition.stages),
                selectinload(WorkflowInstance.workflow_definition).selectinload(WorkflowDefinition.transitions),
                selectinload(WorkflowInstance.history),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_or_create_instance_for_project(
        self,
        project_id: str,
        workflow_def_id: Optional[uuid.UUID] = None,
    ) -> WorkflowInstance:
        """Fetch existing workflow instance for project or initialize at stage 1."""
        instance = await self.get_instance_by_project_id(project_id)
        if instance:
            return instance

        wf_def = await self.get_default_workflow_definition()
        first_stage = wf_def.stages[0] if wf_def.stages else None
        initial_stage_code = first_stage.stage_code if first_stage else "PROJECT_PLANNING"
        sla_days = first_stage.sla_days if first_stage else 30

        now = datetime.now(timezone.utc)
        deadline = now + timedelta(days=sla_days)

        new_instance = WorkflowInstance(
            project_id=project_id,
            workflow_definition_id=wf_def.id,
            current_stage_code=initial_stage_code,
            status="ACTIVE",
            stage_started_at=now,
            deadline_at=deadline,
        )
        self.session.add(new_instance)
        await self.session.flush()
        return await self.get_instance_by_project_id(project_id)

    async def get_allowed_transitions(
        self,
        workflow_def_id: uuid.UUID,
        current_stage_code: str,
    ) -> List[WorkflowTransitionDefinition]:
        """Return legal transition definitions available from the current stage."""
        stmt = (
            select(WorkflowTransitionDefinition)
            .where(
                WorkflowTransitionDefinition.workflow_definition_id == workflow_def_id,
                WorkflowTransitionDefinition.from_stage_code == current_stage_code,
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def find_matching_transition(
        self,
        workflow_def_id: uuid.UUID,
        from_stage_code: str,
        action_name: str,
        to_stage_code: str,
    ) -> Optional[WorkflowTransitionDefinition]:
        """Find a transition matching exact origin, action, and target destination."""
        stmt = (
            select(WorkflowTransitionDefinition)
            .where(
                WorkflowTransitionDefinition.workflow_definition_id == workflow_def_id,
                WorkflowTransitionDefinition.from_stage_code == from_stage_code,
                WorkflowTransitionDefinition.action_name == action_name,
                WorkflowTransitionDefinition.to_stage_code == to_stage_code,
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def record_transition_history(
        self,
        *,
        workflow_instance_id: uuid.UUID,
        from_stage_code: str,
        to_stage_code: str,
        action: str,
        performed_by_user_id: Optional[uuid.UUID],
        performed_by_name: str,
        performed_by_role: str,
        remarks: Optional[str] = None,
        data_payload: Optional[Dict[str, Any]] = None,
    ) -> WorkflowTransitionHistory:
        """Append an entry to the transition audit ledger."""
        entry = WorkflowTransitionHistory(
            workflow_instance_id=workflow_instance_id,
            from_stage_code=from_stage_code,
            to_stage_code=to_stage_code,
            action=action,
            performed_by_user_id=performed_by_user_id,
            performed_by_name=performed_by_name,
            performed_by_role=performed_by_role,
            remarks=remarks,
            data_payload=data_payload or {},
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

