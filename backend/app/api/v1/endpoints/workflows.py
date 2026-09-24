from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.workflow import (
    PendingActionRead,
    WorkflowInstanceRead,
    WorkflowStageRead,
    WorkflowTransitionHistoryRead,
    WorkflowTransitionRequest,
)
from app.services.workflow import WorkflowService

router = APIRouter()


@router.get(
    "/projects/{project_id}",
    response_model=WorkflowInstanceRead,
    summary="Get project workflow status",
    description="Fetch active workflow state, current stage, SLA remaining days, and allowable next transition commands.",
)
async def get_workflow_status(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WorkflowInstanceRead:
    """Get project workflow status."""
    service = WorkflowService(db)
    return await service.get_workflow_status(project_id=project_id, current_user=current_user)


@router.post(
    "/projects/{project_id}/transitions",
    response_model=WorkflowInstanceRead,
    status_code=status.HTTP_200_OK,
    summary="Execute controlled workflow transition",
    description="Execute an atomic state transition command validating rules, user role, jurisdiction, mandatory remarks, and updating SLAs.",
)
async def execute_transition(
    project_id: str,
    transition_in: WorkflowTransitionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WorkflowInstanceRead:
    """Execute workflow transition."""
    service = WorkflowService(db)
    return await service.execute_transition(
        project_id=project_id,
        transition_in=transition_in,
        current_user=current_user,
    )


@router.get(
    "/projects/{project_id}/history",
    response_model=List[WorkflowTransitionHistoryRead],
    summary="Get workflow transition history",
    description="Retrieve chronological append-only audit ledger of all executed state transitions for the project.",
)
async def get_transition_history(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[WorkflowTransitionHistoryRead]:
    """Get transition history."""
    service = WorkflowService(db)
    return await service.get_transition_history(project_id=project_id, current_user=current_user)


@router.get(
    "/projects/{project_id}/current-stage",
    response_model=WorkflowStageRead,
    summary="Get current stage definition",
    description="Retrieve statutory metadata for the project's current active lifecycle stage.",
)
async def get_current_stage(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WorkflowStageRead:
    """Get current stage."""
    service = WorkflowService(db)
    return await service.get_current_stage(project_id=project_id, current_user=current_user)


@router.get(
    "/projects/{project_id}/pending-actions",
    response_model=List[PendingActionRead],
    summary="Get pending allowable actions",
    description="List valid next transition actions available to the authenticated user based on role and stage rules.",
)
async def get_pending_actions(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[PendingActionRead]:
    """Get pending actions."""
    service = WorkflowService(db)
    return await service.get_pending_actions(project_id=project_id, current_user=current_user)

