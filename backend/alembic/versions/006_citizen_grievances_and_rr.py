"""Add grievances, grievance documents, grievance history, affected families, rr eligibilities, rr benefits, and resettlement colonies

Revision ID: 006_citizen_grievances_and_rr
Revises: 005_compensation_and_awards
Create Date: 2026-09-23 23:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "006_citizen_grievances_and_rr"
down_revision: Union[str, None] = "005_compensation_and_awards"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Grievances Table
    op.create_table(
        "grievances",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("parcel_id", sa.String(100), sa.ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(100), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("citizen_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("citizen_name", sa.String(200), nullable=False),
        sa.Column("citizen_phone", sa.String(30), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="SUBMITTED"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="NORMAL"),
        sa.Column("assigned_officer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assigned_officer_name", sa.String(150), nullable=True),
        sa.Column("assigned_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("resolved_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("resolved_by_name", sa.String(150), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sla_due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_grievances_id", "grievances", ["id"])
    op.create_index("ix_grievances_parcel_id", "grievances", ["parcel_id"])
    op.create_index("ix_grievances_project_id", "grievances", ["project_id"])
    op.create_index("ix_grievances_citizen_user_id", "grievances", ["citizen_user_id"])
    op.create_index("ix_grievances_status", "grievances", ["status"])
    op.create_index("ix_grievances_category", "grievances", ["category"])
    op.create_index("ix_grievances_assigned_officer_id", "grievances", ["assigned_officer_id"])

    # 2. Grievance Documents Table
    op.create_table(
        "grievance_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("grievance_id", sa.String(100), sa.ForeignKey("grievances.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mime_type", sa.String(100), nullable=False, server_default="application/pdf"),
        sa.Column("sha256_hash", sa.String(64), nullable=False),
        sa.Column("uploaded_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("uploaded_by_name", sa.String(150), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_grievance_docs_grievance_id", "grievance_documents", ["grievance_id"])

    # 3. Grievance History Table
    op.create_table(
        "grievance_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("grievance_id", sa.String(100), sa.ForeignKey("grievances.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("from_status", sa.String(50), nullable=True),
        sa.Column("to_status", sa.String(50), nullable=True),
        sa.Column("performed_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("performed_by_name", sa.String(150), nullable=False),
        sa.Column("performed_by_role", sa.String(100), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_grievance_history_grievance_id", "grievance_history", ["grievance_id"])
    op.create_index("ix_grievance_history_action", "grievance_history", ["action"])

    # 4. Affected Families Table
    op.create_table(
        "affected_families",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("project_id", sa.String(100), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parcel_id", sa.String(100), sa.ForeignKey("land_parcels.id", ondelete="SET NULL"), nullable=True),
        sa.Column("citizen_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("head_of_family", sa.String(200), nullable=False),
        sa.Column("aadhaar_masked", sa.String(20), nullable=True),
        sa.Column("contact_number", sa.String(30), nullable=True),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("village", sa.String(100), nullable=False),
        sa.Column("family_members_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("affected_type", sa.String(50), nullable=False, server_default="Agricultural"),
        sa.Column("relocation_status", sa.String(50), nullable=False, server_default="Pending Rehabilitation"),
        sa.Column("total_financial_package_lakhs", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("status", sa.String(50), nullable=False, server_default="Under Assessment"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_affected_families_id", "affected_families", ["id"])
    op.create_index("ix_affected_families_project_id", "affected_families", ["project_id"])
    op.create_index("ix_affected_families_citizen_user_id", "affected_families", ["citizen_user_id"])
    op.create_index("ix_affected_families_state", "affected_families", ["state"])
    op.create_index("ix_affected_families_district", "affected_families", ["district"])
    op.create_index("ix_affected_families_status", "affected_families", ["status"])

    # 5. R&R Eligibilities Table
    op.create_table(
        "rr_eligibilities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("family_id", sa.String(100), sa.ForeignKey("affected_families.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("is_eligible", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("eligibility_criteria", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="PENDING_VERIFICATION"),
        sa.Column("verified_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("verified_by_name", sa.String(150), nullable=True),
        sa.Column("verification_date", sa.Date(), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
    )
    op.create_index("ix_rr_eligibilities_family_id", "rr_eligibilities", ["family_id"])
    op.create_index("ix_rr_eligibilities_status", "rr_eligibilities", ["status"])

    # 6. R&R Benefits Table
    op.create_table(
        "rr_benefits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("family_id", sa.String(100), sa.ForeignKey("affected_families.id", ondelete="CASCADE"), nullable=False),
        sa.Column("benefit_type", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("monetary_value_lakhs", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("housing_colony_name", sa.String(200), nullable=True),
        sa.Column("housing_unit_number", sa.String(100), nullable=True),
        sa.Column("benefit_status", sa.String(50), nullable=False, server_default="SANCTIONED"),
        sa.Column("disbursement_status", sa.String(50), nullable=False, server_default="PENDING"),
        sa.Column("disbursed_amount_lakhs", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("disbursement_date", sa.Date(), nullable=True),
        sa.Column("disbursement_ref", sa.String(100), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_rr_benefits_family_id", "rr_benefits", ["family_id"])
    op.create_index("ix_rr_benefits_benefit_type", "rr_benefits", ["benefit_type"])
    op.create_index("ix_rr_benefits_disbursement_status", "rr_benefits", ["disbursement_status"])

    # 7. Resettlement Colonies Table
    op.create_table(
        "resettlement_colonies",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("project_id", sa.String(100), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("allotted_units", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_units", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("school_hospital_status", sa.String(100), nullable=False, server_default="Operational"),
        sa.Column("water_electricity_status", sa.String(100), nullable=False, server_default="100% Commissioned"),
        sa.Column("livelihood_grants_disbursed_cr", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_resettlement_colonies_id", "resettlement_colonies", ["id"])
    op.create_index("ix_resettlement_colonies_state", "resettlement_colonies", ["state"])
    op.create_index("ix_resettlement_colonies_district", "resettlement_colonies", ["district"])
    op.create_index("ix_resettlement_colonies_project_id", "resettlement_colonies", ["project_id"])


def downgrade() -> None:
    op.drop_table("resettlement_colonies")
    op.drop_table("rr_benefits")
    op.drop_table("rr_eligibilities")
    op.drop_table("affected_families")
    op.drop_table("grievance_history")
    op.drop_table("grievance_documents")
    op.drop_table("grievances")

