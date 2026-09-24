"""Add documents, document_versions, landowner_consents, and consent_history tables

Revision ID: 004_documents_and_consent
Revises: 003_field_survey_evidence
Create Date: 2026-09-23 23:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "004_documents_and_consent"
down_revision: Union[str, None] = "003_field_survey_evidence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Statutory Documents Master Registry
    op.create_table(
        "documents",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("project_id", sa.String(100), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=True),
        sa.Column("parcel_id", sa.String(100), sa.ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=True),
        sa.Column("uploader_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uploaded_by", sa.String(150), nullable=False),
        sa.Column("current_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("verified_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verification_remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_documents_id", "documents", ["id"])
    op.create_index("ix_documents_title", "documents", ["title"])
    op.create_index("ix_documents_category", "documents", ["category"])
    op.create_index("ix_documents_project_id", "documents", ["project_id"])
    op.create_index("ix_documents_parcel_id", "documents", ["parcel_id"])
    op.create_index("ix_documents_uploader_id", "documents", ["uploader_id"])
    op.create_index("ix_documents_is_verified", "documents", ["is_verified"])

    # 2. Immutable Document Versions Revision Ledger
    op.create_table(
        "document_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("document_id", sa.String(100), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("version_label", sa.String(50), nullable=False),
        sa.Column("storage_key", sa.String(255), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("checksum_sha256", sa.String(128), nullable=False),
        sa.Column("file_url", sa.String(500), nullable=False),
        sa.Column("changelog", sa.Text(), nullable=True),
        sa.Column("uploaded_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_document_versions_id", "document_versions", ["id"])
    op.create_index("ix_document_versions_document_id", "document_versions", ["document_id"])
    op.create_index("ix_document_versions_checksum_sha256", "document_versions", ["checksum_sha256"])
    op.create_index("ix_document_versions_created_at", "document_versions", ["created_at"])

    # 3. Landowner Consent Records
    op.create_table(
        "landowner_consents",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("parcel_id", sa.String(100), sa.ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(100), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("landowner_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("landowner_name", sa.String(200), nullable=False),
        sa.Column("landowner_aadhaar_masked", sa.String(20), nullable=False),
        sa.Column("landowner_phone", sa.String(30), nullable=True),
        sa.Column("consent_type", sa.String(50), nullable=False, server_default="VOLUNTARY_ACQUISITION"),
        sa.Column("status", sa.String(50), nullable=False, server_default="DRAFT"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("supporting_document_id", sa.String(100), sa.ForeignKey("documents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("esign_simulation_ref", sa.String(100), nullable=True),
        sa.Column("esign_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("qr_verification_code", sa.String(255), nullable=True),
        sa.Column("document_hash", sa.String(128), nullable=True),
        sa.Column("verifying_officer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verification_remarks", sa.Text(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_landowner_consents_id", "landowner_consents", ["id"])
    op.create_index("ix_landowner_consents_parcel_id", "landowner_consents", ["parcel_id"])
    op.create_index("ix_landowner_consents_project_id", "landowner_consents", ["project_id"])
    op.create_index("ix_landowner_consents_user_id", "landowner_consents", ["landowner_user_id"])
    op.create_index("ix_landowner_consents_name", "landowner_consents", ["landowner_name"])
    op.create_index("ix_landowner_consents_aadhaar", "landowner_consents", ["landowner_aadhaar_masked"])
    op.create_index("ix_landowner_consents_status", "landowner_consents", ["status"])

    # 4. Consent Audit Trail History
    op.create_table(
        "consent_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("consent_id", sa.String(100), sa.ForeignKey("landowner_consents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("from_status", sa.String(50), nullable=True),
        sa.Column("to_status", sa.String(50), nullable=True),
        sa.Column("performed_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("performed_by_name", sa.String(150), nullable=False),
        sa.Column("performed_by_role", sa.String(100), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_consent_history_id", "consent_history", ["id"])
    op.create_index("ix_consent_history_consent_id", "consent_history", ["consent_id"])
    op.create_index("ix_consent_history_action", "consent_history", ["action"])
    op.create_index("ix_consent_history_timestamp", "consent_history", ["timestamp"])


def downgrade() -> None:
    op.drop_table("consent_history")
    op.drop_table("landowner_consents")
    op.drop_table("document_versions")
    op.drop_table("documents")

