import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkflowTransitionRequest(BaseModel):
    """Command schema to execute a controlled workflow state transition."""

    action_name: str = Field(..., description="Action identifier (e.g. ISSUE_NOTIFICATION, DECLARE_AWARD)")
    target_stage_code: str = Field(..., description="Target destination stage code")
    remarks: Optional[str] = Field(None, description="Official remarks or statutory justification")
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contextual data accompanying transition")


class WorkflowStageRead(BaseModel):
    """Schema for a workflow stage definition."""

    stage_code: str
    name: str
    description: Optional[str] = None
    stage_order: int
    required_role: Optional[str] = None
    sla_days: int
    is_terminal: bool
    is_initial: bool

    class Config:
        from_attributes = True


class PendingActionRead(BaseModel):
    """Schema for next allowable legal actions from the current stage."""

    action_name: str
    target_stage_code: str
    target_stage_name: str
    description: Optional[str] = None
    required_role: Optional[str] = None
    requires_remarks: bool = False


class WorkflowTransitionHistoryRead(BaseModel):
    """Schema for transition history ledger entry."""

    id: uuid.UUID
    from_stage_code: str
    to_stage_code: str
    action: str
    performed_by_name: str
    performed_by_role: str
    remarks: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class WorkflowInstanceRead(BaseModel):
    """Schema for the active project workflow state and statutory SLA status."""

    id: uuid.UUID
    project_id: str
    workflow_code: str
    workflow_name: str
    current_stage_code: str
    current_stage_name: str
    stage_order: int
    total_stages: int
    status: str
    sla_days_remaining: Optional[int] = None
    deadline_at: Optional[datetime] = None
    stage_started_at: datetime
    pending_actions: List[PendingActionRead] = Field(default_factory=list)

    class Config:
        from_attributes = True

