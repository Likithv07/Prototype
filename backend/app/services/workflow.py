import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import ScopeChecker
from app.core.exceptions import (
    EntityNotFoundException,
    ForbiddenException,
    ValidationException,
)
from app.core.logging import get_logger
from app.models.project import Project
from app.models.user import User
from app.models.workflow import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowStageDefinition,
    WorkflowTransitionDefinition,
    WorkflowTransitionHistory,
)
from app.repositories.audit import AuditRepository
from app.repositories.project import ProjectRepository
from app.repositories.workflow import WorkflowRepository
from app.schemas.workflow import (
    PendingActionRead,
    WorkflowInstanceRead,
    WorkflowStageRead,
    WorkflowTransitionHistoryRead,
    WorkflowTransitionRequest,
)

logger = get_logger(__name__)


class WorkflowService:
    """Service governing transactional land acquisition state transitions, SLA tracking, and audit trails."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.wf_repo = WorkflowRepository(session)
        self.project_repo = ProjectRepository(session)
        self.audit_repo = AuditRepository(session)

    async def get_workflow_status(
        self,
        project_id: str,
        current_user: User,
    ) -> WorkflowInstanceRead:
        """Fetch active workflow instance and calculate SLA days remaining."""
        project = await self._get_and_verify_project(project_id, current_user)
        instance = await self.wf_repo.get_or_create_instance_for_project(project_id)

        pending_actions = await self.get_pending_actions(project_id, current_user)
        return self._to_instance_read(instance, pending_actions)

    async def get_current_stage(
        self,
        project_id: str,
        current_user: User,
    ) -> WorkflowStageRead:
        """Retrieve details of the active stage definition."""
        project = await self._get_and_verify_project(project_id, current_user)
        instance = await self.wf_repo.get_or_create_instance_for_project(project_id)

        stages_map = {s.stage_code: s for s in instance.workflow_definition.stages}
        current_stage = stages_map.get(instance.current_stage_code)
        if not current_stage:
            raise EntityNotFoundException("WorkflowStage", instance.current_stage_code)

        return WorkflowStageRead(
            stage_code=current_stage.stage_code,
            name=current_stage.name,
            description=current_stage.description,
            stage_order=current_stage.stage_order,
            required_role=current_stage.required_role,
            sla_days=current_stage.sla_days,
            is_terminal=current_stage.is_terminal,
            is_initial=current_stage.is_initial,
        )

    async def get_pending_actions(
        self,
        project_id: str,
        current_user: User,
    ) -> List[PendingActionRead]:
        """List allowable transitions from current state based on workflow rules and user role."""
        project = await self._get_and_verify_project(project_id, current_user)
        instance = await self.wf_repo.get_or_create_instance_for_project(project_id)

        if instance.status != "ACTIVE":
            return []

        allowed_defs = await self.wf_repo.get_allowed_transitions(
            instance.workflow_definition_id,
            instance.current_stage_code,
        )

        stages_map = {s.stage_code: s.name for s in instance.workflow_definition.stages}
        user_roles = set(r.upper() for r in current_user.role_names)
        is_admin = "ADMIN" in user_roles

        pending: List[PendingActionRead] = []
        for t in allowed_defs:
            # Check role eligibility
            if not is_admin and t.required_role:
                if t.required_role.upper() not in user_roles:
                    continue

            pending.append(
                PendingActionRead(
                    action_name=t.action_name,
                    target_stage_code=t.to_stage_code,
                    target_stage_name=stages_map.get(t.to_stage_code, t.to_stage_code),
                    description=t.description,
                    required_role=t.required_role,
                    requires_remarks=t.requires_remarks,
                )
            )

        return pending

    async def execute_transition(
        self,
        project_id: str,
        transition_in: WorkflowTransitionRequest,
        current_user: User,
    ) -> WorkflowInstanceRead:
        """Execute a controlled state transition inside an atomic database transaction.
        
        Guarantees:
        1. Validates current state matches legal transition from_stage.
        2. Verifies user role and geographic jurisdiction on project.
        3. Enforces mandatory remarks and required data.
        4. Calculates new SLA statutory deadline.
        5. Synchronizes parent Project progress, status, and lifecycle stages.
        6. Persists immutable transition history entry.
        7. Persists immutable regulatory audit log.
        8. Emits notifications to target stakeholder roles.
        """
        project = await self._get_and_verify_project(project_id, current_user)
        instance = await self.wf_repo.get_or_create_instance_for_project(project_id)

        if instance.status != "ACTIVE":
            raise ValidationException(
                f"Cannot execute transition on workflow with status '{instance.status}'."
            )

        # 1. Match legal transition
        transition_def = await self.wf_repo.find_matching_transition(
            workflow_def_id=instance.workflow_definition_id,
            from_stage_code=instance.current_stage_code,
            action_name=transition_in.action_name,
            to_stage_code=transition_in.target_stage_code,
        )

        if not transition_def:
            raise ValidationException(
                f"Illegal transition: Action '{transition_in.action_name}' to stage '{transition_in.target_stage_code}' is not permitted from current stage '{instance.current_stage_code}'."
            )

        # 2. Verify user role & permissions
        user_roles = set(r.upper() for r in current_user.role_names)
        if "ADMIN" not in user_roles and transition_def.required_role:
            if transition_def.required_role.upper() not in user_roles:
                raise ForbiddenException(
                    f"Access denied. Action '{transition_in.action_name}' requires role '{transition_def.required_role}'. Assigned: {current_user.role_names}"
                )

        # 3. Validate mandatory fields
        if transition_def.requires_remarks and (not transition_in.remarks or not transition_in.remarks.strip()):
            raise ValidationException(
                f"Statutory remarks are mandatory for action '{transition_in.action_name}'."
            )

        from_stage = instance.current_stage_code
        to_stage = transition_in.target_stage_code

        # 4. Resolve destination stage & calculate SLA
        stages_map = {s.stage_code: s for s in instance.workflow_definition.stages}
        target_stage_def = stages_map.get(to_stage)
        if not target_stage_def:
            raise EntityNotFoundException("WorkflowStage", to_stage)

        now = datetime.now(timezone.utc)
        instance.current_stage_code = to_stage
        instance.stage_started_at = now
        instance.deadline_at = now + timedelta(days=target_stage_def.sla_days)

        if target_stage_def.is_terminal:
            instance.status = "COMPLETED"

        # 5. Append transition history
        await self.wf_repo.record_transition_history(
            workflow_instance_id=instance.id,
            from_stage_code=from_stage,
            to_stage_code=to_stage,
            action=transition_in.action_name,
            performed_by_user_id=current_user.id,
            performed_by_name=current_user.full_name,
            performed_by_role=current_user.role_names[0] if current_user.role_names else "OFFICER",
            remarks=transition_in.remarks,
            data_payload=transition_in.payload,
        )

        # 6. Append Immutable Audit Log
        primary_role = current_user.role_names[0] if current_user.role_names else "OFFICER"
        await self.audit_repo.log_action(
            user_id=current_user.id,
            user_name=current_user.full_name,
            role=primary_role,
            action=f"WORKFLOW_{transition_in.action_name}",
            module="workflow",
            entity_type="Project",
            entity_id=project_id,
            details=f"Advanced stage from '{from_stage}' to '{to_stage}'. Action: {transition_in.action_name}. Remarks: {transition_in.remarks or 'N/A'}",
        )

        # 7. Create Targeted Notification
        next_role = target_stage_def.required_role or "OFFICER"
        await self.audit_repo.create_notification(
            title=f"Stage Advanced: {project.name}",
            message=f"Project '{project_id}' advanced to '{target_stage_def.name}'. Action required by {next_role}.",
            category="workflow",
            recipient_role=next_role,
            link_view="projects",
        )

        # 8. Synchronize Project Metrics & Lifecycle
        total_stages = len(instance.workflow_definition.stages)
        new_progress = round((target_stage_def.stage_order / total_stages) * 100, 1)
        project.progress = min(100.0, new_progress)

        if target_stage_def.is_terminal:
            project.status = "Completed"
        else:
            project.status = target_stage_def.name

        # Update Project.lifecycle stages
        if project.lifecycle:
            updated_lifecycle = []
            for st in project.lifecycle:
                st_dict = dict(st)
                if st_dict.get("id", 0) < target_stage_def.stage_order:
                    st_dict["status"] = "Completed"
                elif st_dict.get("id", 0) == target_stage_def.stage_order:
                    st_dict["status"] = "In Progress"
                else:
                    st_dict["status"] = "Pending"
                updated_lifecycle.append(st_dict)
            project.lifecycle = updated_lifecycle

        self.session.add(project)
        self.session.add(instance)
        await self.session.flush()

        logger.info(
            f"Workflow for project '{project_id}' transitioned: [{from_stage}] -> [{to_stage}] by user '{current_user.username}'."
        )

        # Re-fetch fresh state
        fresh_instance = await self.wf_repo.get_instance_by_project_id(project_id)
        pending_actions = await self.get_pending_actions(project_id, current_user)
        return self._to_instance_read(fresh_instance or instance, pending_actions)

    async def get_transition_history(
        self,
        project_id: str,
        current_user: User,
    ) -> List[WorkflowTransitionHistoryRead]:
        """Fetch chronological audit ledger of transitions for project."""
        await self._get_and_verify_project(project_id, current_user)
        instance = await self.wf_repo.get_or_create_instance_for_project(project_id)

        return [
            WorkflowTransitionHistoryRead(
                id=h.id,
                from_stage_code=h.from_stage_code,
                to_stage_code=h.to_stage_code,
                action=h.action,
                performed_by_name=h.performed_by_name,
                performed_by_role=h.performed_by_role,
                remarks=h.remarks,
                timestamp=h.timestamp,
            )
            for h in instance.history
        ]

    async def _get_and_verify_project(self, project_id: str, user: User) -> Project:
        """Fetch project and verify user's geographic jurisdiction."""
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise EntityNotFoundException("Project", project_id)

        ScopeChecker.verify_project_access(user, project)
        return project

    @staticmethod
    def _to_instance_read(
        instance: WorkflowInstance,
        pending_actions: List[PendingActionRead],
    ) -> WorkflowInstanceRead:
        stages_map = {s.stage_code: s for s in instance.workflow_definition.stages}
        current_stage = stages_map.get(instance.current_stage_code)
        stage_name = current_stage.name if current_stage else instance.current_stage_code
        stage_order = current_stage.stage_order if current_stage else 1
        total_stages = len(instance.workflow_definition.stages)

        days_remaining = None
        if instance.deadline_at:
            delta = instance.deadline_at - datetime.now(timezone.utc)
            days_remaining = max(0, delta.days)

        return WorkflowInstanceRead(
            id=instance.id,
            project_id=instance.project_id,
            workflow_code=instance.workflow_definition.code,
            workflow_name=instance.workflow_definition.name,
            current_stage_code=instance.current_stage_code,
            current_stage_name=stage_name,
            stage_order=stage_order,
            total_stages=total_stages,
            status=instance.status,
            sla_days_remaining=days_remaining,
            deadline_at=instance.deadline_at,
            stage_started_at=instance.stage_started_at,
            pending_actions=pending_actions,
        )

