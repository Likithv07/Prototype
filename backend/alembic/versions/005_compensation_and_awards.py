"""Add compensation rules, assessments, components, awards, and compensation history

Revision ID: 005_compensation_and_awards
Revises: 004_documents_and_consent
Create Date: 2026-09-23 23:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "005_compensation_and_awards"
down_revision: Union[str, None] = "004_documents_and_consent"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Compensation Rules Table
    op.create_table(
        "compensation_rules",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("version", sa.String(50), nullable=False, server_default="v1.0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("effective_from", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("solatium_percentage", sa.Float(), nullable=False, server_default="100.0"),
        sa.Column("additional_interest_percentage", sa.Float(), nullable=False, server_default="12.0"),
        sa.Column("urban_multiplier", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("rural_multiplier_min", sa.Float(), nullable=False, server_default="1.5"),
        sa.Column("rural_multiplier_max", sa.Float(), nullable=False, server_default="2.0"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("formula_definition", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_compensation_rules_id", "compensation_rules", ["id"])
    op.create_index("ix_compensation_rules_is_active", "compensation_rules", ["is_active"])
    op.create_index("ix_compensation_rules_state", "compensation_rules", ["state"])

    # Seed Default Central RFCTLARR 2013 Rule
    op.execute(
        """
        INSERT INTO compensation_rules (
            id, name, version, is_active, state, solatium_percentage,
            additional_interest_percentage, urban_multiplier, rural_multiplier_min,
            rural_multiplier_max, description
        ) VALUES (
            'RULE-RFCTLARR-2013-V1',
            'RFCTLARR Standard Statutory Formula 2013',
            'v1.0',
            true,
            NULL,
            100.0,
            12.0,
            1.0,
            1.5,
            2.0,
            'Central statutory compensation formulation under Sections 26-30 of the RFCTLARR Act 2013.'
        ) ON CONFLICT (id) DO NOTHING;
        """
    )

    # 2. Compensation Assessments Table
    op.create_table(
        "compensation_assessments",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("parcel_id", sa.String(100), sa.ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(100), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("landowner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("landowner_name", sa.String(200), nullable=False),
        sa.Column("survey_number", sa.String(50), nullable=False),
        sa.Column("rule_id", sa.String(100), sa.ForeignKey("compensation_rules.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("rule_version", sa.String(50), nullable=False, server_default="v1.0"),
        sa.Column("status", sa.String(50), nullable=False, server_default="DRAFT"),
        sa.Column("land_area_acres", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("market_value_per_acre", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("multiplier_factor", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("asset_valuation", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("basic_land_value", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("multiplied_land_value", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("market_value_plus_assets", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("solatium_percentage", sa.Float(), nullable=False, server_default="100.0"),
        sa.Column("solatium_amount", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("interest_percentage", sa.Float(), nullable=False, server_default="12.0"),
        sa.Column("interest_amount", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("total_compensation", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("calculated_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("submitted_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("submission_notes", sa.Text(), nullable=True),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approval_remarks", sa.Text(), nullable=True),
        sa.Column("digital_signature_ref", sa.String(100), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("revision_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_compensation_assessments_id", "compensation_assessments", ["id"])
    op.create_index("ix_compensation_assessments_parcel_id", "compensation_assessments", ["parcel_id"])
    op.create_index("ix_compensation_assessments_project_id", "compensation_assessments", ["project_id"])
    op.create_index("ix_compensation_assessments_landowner_id", "compensation_assessments", ["landowner_id"])
    op.create_index("ix_compensation_assessments_status", "compensation_assessments", ["status"])

    # 3. Itemized Compensation Components Table
    op.create_table(
        "compensation_components",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("assessment_id", sa.String(100), sa.ForeignKey("compensation_assessments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("component_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("quantity", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("rate_per_unit", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("gross_value", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("depreciation_percentage", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("net_value", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("valuation_date", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")),
        sa.Column("remarks", sa.Text(), nullable=True),
    )
    op.create_index("ix_compensation_components_id", "compensation_components", ["id"])
    op.create_index("ix_compensation_components_assessment_id", "compensation_components", ["assessment_id"])
    op.create_index("ix_compensation_components_component_type", "compensation_components", ["component_type"])

    # 4. Section 31 Statutory Awards Table
    op.create_table(
        "awards",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("assessment_id", sa.String(100), sa.ForeignKey("compensation_assessments.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("parcel_id", sa.String(100), sa.ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(100), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("award_number", sa.String(100), unique=True, nullable=False),
        sa.Column("award_date", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")),
        sa.Column("competent_authority_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("competent_authority_name", sa.String(150), nullable=False),
        sa.Column("competent_authority_designation", sa.String(100), nullable=False),
        sa.Column("total_awarded_amount", sa.Float(), nullable=False),
        sa.Column("digital_seal_ref", sa.String(100), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="ISSUED"),
        sa.Column("gazette_ref", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_awards_id", "awards", ["id"])
    op.create_index("ix_awards_assessment_id", "awards", ["assessment_id"])
    op.create_index("ix_awards_parcel_id", "awards", ["parcel_id"])
    op.create_index("ix_awards_project_id", "awards", ["project_id"])
    op.create_index("ix_awards_award_number", "awards", ["award_number"])
    op.create_index("ix_awards_status", "awards", ["status"])

    # 5. Compensation History Table
    op.create_table(
        "compensation_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("assessment_id", sa.String(100), sa.ForeignKey("compensation_assessments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("from_status", sa.String(50), nullable=True),
        sa.Column("to_status", sa.String(50), nullable=True),
        sa.Column("from_total", sa.Float(), nullable=True),
        sa.Column("to_total", sa.Float(), nullable=True),
        sa.Column("performed_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("performed_by_name", sa.String(150), nullable=False),
        sa.Column("performed_by_role", sa.String(100), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_compensation_history_id", "compensation_history", ["id"])
    op.create_index("ix_compensation_history_assessment_id", "compensation_history", ["assessment_id"])
    op.create_index("ix_compensation_history_action", "compensation_history", ["action"])
    op.create_index("ix_compensation_history_timestamp", "compensation_history", ["timestamp"])


def downgrade() -> None:
    op.drop_table("compensation_history")
    op.drop_table("awards")
    op.drop_table("compensation_components")
    op.drop_table("compensation_assessments")
    op.drop_table("compensation_rules")

