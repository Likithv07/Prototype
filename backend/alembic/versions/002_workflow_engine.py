"""Add workflow engine, audit logs, and notifications tables

Revision ID: 002_workflow_engine
Revises: 001_initial_schema
Create Date: 2026-09-23 22:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_workflow_engine"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Workflow Definitions
    op.create_table(
        "workflow_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_workflow_definitions_id", "workflow_definitions", ["id"])
    op.create_index("ix_workflow_definitions_code", "workflow_definitions", ["code"])

    # 2. Workflow Stage Definitions
    op.create_table(
        "workflow_stage_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workflow_definition_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stage_code", sa.String(100), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("stage_order", sa.Integer(), nullable=False),
        sa.Column("required_role", sa.String(50), nullable=True),
        sa.Column("sla_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("is_initial", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_terminal", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_workflow_stage_definitions_id", "workflow_stage_definitions", ["id"])
    op.create_index("ix_workflow_stage_definitions_wf_def_id", "workflow_stage_definitions", ["workflow_definition_id"])
    op.create_index("ix_workflow_stage_definitions_stage_code", "workflow_stage_definitions", ["stage_code"])

    # 3. Workflow Transition Definitions
    op.create_table(
        "workflow_transition_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workflow_definition_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_stage_code", sa.String(100), nullable=False),
        sa.Column("to_stage_code", sa.String(100), nullable=False),
        sa.Column("action_name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("required_role", sa.String(50), nullable=True),
        sa.Column("required_permission", sa.String(100), nullable=True),
        sa.Column("requires_remarks", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_workflow_transition_definitions_id", "workflow_transition_definitions", ["id"])
    op.create_index("ix_workflow_transition_definitions_wf_def_id", "workflow_transition_definitions", ["workflow_definition_id"])
    op.create_index("ix_workflow_transition_definitions_action", "workflow_transition_definitions", ["action_name"])

    # 4. Workflow Instances
    op.create_table(
        "workflow_instances",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", sa.String(100), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("workflow_definition_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_definitions.id"), nullable=False),
        sa.Column("current_stage_code", sa.String(100), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.Column("assigned_officer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("stage_started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_workflow_instances_id", "workflow_instances", ["id"])
    op.create_index("ix_workflow_instances_project_id", "workflow_instances", ["project_id"])
    op.create_index("ix_workflow_instances_current_stage", "workflow_instances", ["current_stage_code"])
    op.create_index("ix_workflow_instances_status", "workflow_instances", ["status"])

    # 5. Workflow Transition History
    op.create_table(
        "workflow_transition_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workflow_instance_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflow_instances.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_stage_code", sa.String(100), nullable=False),
        sa.Column("to_stage_code", sa.String(100), nullable=False),
        sa.Column("action", sa.String(150), nullable=False),
        sa.Column("performed_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("performed_by_name", sa.String(150), nullable=False),
        sa.Column("performed_by_role", sa.String(50), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("data_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_workflow_transition_history_id", "workflow_transition_history", ["id"])
    op.create_index("ix_workflow_transition_history_wf_inst_id", "workflow_transition_history", ["workflow_instance_id"])
    op.create_index("ix_workflow_transition_history_timestamp", "workflow_transition_history", ["timestamp"])

    # 6. Audit Logs
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_name", sa.String(150), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("module", sa.String(50), nullable=False, server_default="workflow"),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(100), nullable=False),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_audit_logs_id", "audit_logs", ["id"])
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_role", "audit_logs", ["role"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])

    # 7. Notifications
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("recipient_role", sa.String(50), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("category", sa.String(50), nullable=False, server_default="workflow"),
        sa.Column("link_view", sa.String(100), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_notifications_id", "notifications", ["id"])
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_recipient_role", "notifications", ["recipient_role"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("audit_logs")
    op.drop_table("workflow_transition_history")
    op.drop_table("workflow_instances")
    op.drop_table("workflow_transition_definitions")
    op.drop_table("workflow_stage_definitions")
    op.drop_table("workflow_definitions")

