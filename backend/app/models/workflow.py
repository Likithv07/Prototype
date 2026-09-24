import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin


class WorkflowDefinition(Base, UUIDMixin, TimestampMixin):
    """Configurable workflow definition blueprint."""

    __tablename__ = "workflow_definitions"

    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    stages: Mapped[List["WorkflowStageDefinition"]] = relationship(
        "WorkflowStageDefinition",
        back_populates="workflow_definition",
        order_by="WorkflowStageDefinition.stage_order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    transitions: Mapped[List["WorkflowTransitionDefinition"]] = relationship(
        "WorkflowTransitionDefinition",
        back_populates="workflow_definition",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class WorkflowStageDefinition(Base, UUIDMixin, TimestampMixin):
    """Individual stage specification within a workflow blueprint."""

    __tablename__ = "workflow_stage_definitions"

    workflow_definition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_definitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stage_code: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stage_order: Mapped[int] = mapped_column(Integer, nullable=False)
    required_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sla_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)  # Statutory deadline
    is_initial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_terminal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    workflow_definition: Mapped["WorkflowDefinition"] = relationship(
        "WorkflowDefinition", back_populates="stages"
    )


class WorkflowTransitionDefinition(Base, UUIDMixin, TimestampMixin):
    """Legal state transition rules within a workflow blueprint."""

    __tablename__ = "workflow_transition_definitions"

    workflow_definition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_definitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_stage_code: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    to_stage_code: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    action_name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    required_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    required_permission: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    requires_remarks: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    workflow_definition: Mapped["WorkflowDefinition"] = relationship(
        "WorkflowDefinition", back_populates="transitions"
    )


class WorkflowInstance(Base, UUIDMixin, TimestampMixin):
    """Runtime execution instance of a workflow attached to a specific project."""

    __tablename__ = "workflow_instances"

    project_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("projects.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    workflow_definition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_definitions.id"),
        nullable=False,
        index=True,
    )
    current_stage_code: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", index=True, nullable=False)  # ACTIVE, COMPLETED, SUSPENDED

    # Current SLA and officer in charge
    assigned_officer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    stage_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deadline_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True)

    # Relationships
    project = relationship("Project")
    workflow_definition = relationship("WorkflowDefinition", lazy="selectin")
    history: Mapped[List["WorkflowTransitionHistory"]] = relationship(
        "WorkflowTransitionHistory",
        back_populates="workflow_instance",
        order_by="WorkflowTransitionHistory.timestamp.desc()",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def current_stage(self) -> Optional["WorkflowStageDefinition"]:
        if hasattr(self, "_current_stage") and self._current_stage is not None:
            return self._current_stage
        if self.workflow_definition and self.workflow_definition.stages:
            for s in self.workflow_definition.stages:
                if s.stage_code == self.current_stage_code:
                    return s
        return None

    @current_stage.setter
    def current_stage(self, stage: Optional["WorkflowStageDefinition"]) -> None:
        self._current_stage = stage
        if stage and hasattr(stage, "stage_code"):
            self.current_stage_code = stage.stage_code

    def __init__(self, **kwargs):
        current_stage = kwargs.pop("current_stage", None)
        if "current_stage_code" not in kwargs:
            if current_stage and hasattr(current_stage, "stage_code"):
                kwargs["current_stage_code"] = current_stage.stage_code
            else:
                kwargs["current_stage_code"] = "draft"
        if "workflow_definition_id" not in kwargs:
            kwargs["workflow_definition_id"] = uuid.uuid4()
        super().__init__(**kwargs)
        if current_stage is not None:
            self._current_stage = current_stage


class WorkflowTransitionHistory(Base, UUIDMixin):
    """Append-only audit ledger of executed workflow transitions."""

    __tablename__ = "workflow_transition_history"

    workflow_instance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_instances.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_stage_code: Mapped[str] = mapped_column(String(100), nullable=False)
    to_stage_code: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(150), nullable=False)

    # User attribution
    performed_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    performed_by_name: Mapped[str] = mapped_column(String(150), nullable=False)
    performed_by_role: Mapped[str] = mapped_column(String(50), nullable=False)

    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    workflow_instance = relationship("WorkflowInstance", back_populates="history")

