"""Add field assignments, survey records, field photos, and field documents tables

Revision ID: 003_field_survey_evidence
Revises: 002_workflow_engine
Create Date: 2026-09-23 22:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003_field_survey_evidence"
down_revision: Union[str, None] = "002_workflow_engine"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Field Assignments
    op.create_table(
        "field_assignments",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("parcel_id", sa.String(100), sa.ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(100), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assigned_officer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assigned_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assigned_date", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("priority", sa.String(50), nullable=False, server_default="High"),
        sa.Column("status", sa.String(50), nullable=False, server_default="Pending"),
        sa.Column("required_tasks", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_field_assignments_id", "field_assignments", ["id"])
    op.create_index("ix_field_assignments_parcel_id", "field_assignments", ["parcel_id"])
    op.create_index("ix_field_assignments_project_id", "field_assignments", ["project_id"])
    op.create_index("ix_field_assignments_officer_id", "field_assignments", ["assigned_officer_id"])
    op.create_index("ix_field_assignments_status", "field_assignments", ["status"])

    # 2. Field Survey Records
    op.create_table(
        "field_survey_records",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("assignment_id", sa.String(100), sa.ForeignKey("field_assignments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("parcel_id", sa.String(100), sa.ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(100), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("officer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("survey_date", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")),
        sa.Column("survey_type", sa.String(100), nullable=False, server_default="Joint Ground Verification"),
        sa.Column("structures_observed", sa.Text(), nullable=True),
        sa.Column("crops_observed", sa.Text(), nullable=True),
        sa.Column("trees_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wells_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("verification_status", sa.String(50), nullable=False, server_default="Pending"),
        sa.Column("verified_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_field_survey_records_id", "field_survey_records", ["id"])
    op.create_index("ix_field_survey_records_parcel_id", "field_survey_records", ["parcel_id"])
    op.create_index("ix_field_survey_records_project_id", "field_survey_records", ["project_id"])
    op.create_index("ix_field_survey_records_officer_id", "field_survey_records", ["officer_id"])
    op.create_index("ix_field_survey_records_status", "field_survey_records", ["verification_status"])

    # 3. Field Photos
    op.create_table(
        "field_photos",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("parcel_id", sa.String(100), sa.ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assignment_id", sa.String(100), sa.ForeignKey("field_assignments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("survey_record_id", sa.String(100), sa.ForeignKey("field_survey_records.id", ondelete="SET NULL"), nullable=True),
        sa.Column("uploader_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("officer_name", sa.String(150), nullable=False),
        sa.Column("caption", sa.String(255), nullable=False),
        sa.Column("photo_type", sa.String(100), nullable=False, server_default="Boundary Marker"),
        sa.Column("storage_key", sa.String(255), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("document_hash", sa.String(128), nullable=False),
        sa.Column("photo_url", sa.String(500), nullable=False),
        sa.Column("thumbnail_url", sa.String(500), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("accuracy_meters", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="Pending"),
        sa.Column("verified_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("verification_remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_field_photos_id", "field_photos", ["id"])
    op.create_index("ix_field_photos_parcel_id", "field_photos", ["parcel_id"])
    op.create_index("ix_field_photos_assignment_id", "field_photos", ["assignment_id"])
    op.create_index("ix_field_photos_hash", "field_photos", ["document_hash"])
    op.create_index("ix_field_photos_status", "field_photos", ["status"])

    # 4. Field Documents
    op.create_table(
        "field_documents",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("parcel_id", sa.String(100), sa.ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assignment_id", sa.String(100), sa.ForeignKey("field_assignments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("survey_record_id", sa.String(100), sa.ForeignKey("field_survey_records.id", ondelete="SET NULL"), nullable=True),
        sa.Column("uploader_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uploaded_by", sa.String(150), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("storage_key", sa.String(255), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("document_hash", sa.String(128), nullable=False),
        sa.Column("file_url", sa.String(500), nullable=False),
        sa.Column("version", sa.String(50), nullable=False, server_default="v1.0"),
        sa.Column("status", sa.String(50), nullable=False, server_default="Pending"),
        sa.Column("verified_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("verification_remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_field_documents_id", "field_documents", ["id"])
    op.create_index("ix_field_documents_parcel_id", "field_documents", ["parcel_id"])
    op.create_index("ix_field_documents_category", "field_documents", ["category"])
    op.create_index("ix_field_documents_hash", "field_documents", ["document_hash"])
    op.create_index("ix_field_documents_status", "field_documents", ["status"])


def downgrade() -> None:
    op.drop_table("field_documents")
    op.drop_table("field_photos")
    op.drop_table("field_survey_records")
    op.drop_table("field_assignments")

