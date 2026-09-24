"""Initial schema with users, roles, permissions, projects, and PostGIS land parcels

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-23 22:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Enable PostGIS Extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # 1. Users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("phone_number", sa.String(20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("district", sa.String(100), nullable=True),
        sa.Column("department", sa.String(150), nullable=True),
        sa.Column("aadhaar_hash", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_state", "users", ["state"])
    op.create_index("ix_users_district", "users", ["district"])
    op.create_index("ix_users_aadhaar_hash", "users", ["aadhaar_hash"])

    # 2. Roles table
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("is_system_role", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_roles_id", "roles", ["id"])
    op.create_index("ix_roles_name", "roles", ["name"])

    # 3. Permissions table
    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("module", sa.String(50), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_permissions_id", "permissions", ["id"])
    op.create_index("ix_permissions_code", "permissions", ["code"])
    op.create_index("ix_permissions_module", "permissions", ["module"])

    # 4. Association: user_roles
    op.create_table(
        "user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )

    # 5. Association: role_permissions
    op.create_table(
        "role_permissions",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    )

    # 6. Projects table
    op.create_table(
        "projects",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("ministry", sa.String(200), nullable=False),
        sa.Column("implementing_agency", sa.String(200), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("project_type", sa.String(100), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="Active"),
        sa.Column("land_required", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("land_acquired", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("progress", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("budget_cr", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("compensation_disbursed_cr", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("expected_completion_date", sa.Date(), nullable=True),
        sa.Column("lifecycle", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_projects_id", "projects", ["id"])
    op.create_index("ix_projects_name", "projects", ["name"])
    op.create_index("ix_projects_state", "projects", ["state"])
    op.create_index("ix_projects_district", "projects", ["district"])
    op.create_index("ix_projects_status", "projects", ["status"])
    op.create_index("ix_projects_project_type", "projects", ["project_type"])

    # 7. Land Parcels table with PostGIS geometry
    op.create_table(
        "land_parcels",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("survey_number", sa.String(50), nullable=False),
        sa.Column("project_id", sa.String(100), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("landowner_name", sa.String(200), nullable=False),
        sa.Column("landowner_mobile", sa.String(30), nullable=True),
        sa.Column("landowner_address", sa.Text(), nullable=True),
        sa.Column("masked_aadhaar", sa.String(20), nullable=True),
        sa.Column("masked_bank_account", sa.String(50), nullable=True),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("village", sa.String(100), nullable=False),
        sa.Column("area_acres", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("land_type", sa.String(50), nullable=False, server_default="Agricultural"),
        sa.Column("acquisition_status", sa.String(50), nullable=False, server_default="Proposed"),
        sa.Column("compensation_status", sa.String(50), nullable=False, server_default="Pending"),
        sa.Column("possession_status", sa.String(50), nullable=False, server_default="Not Started"),
        sa.Column("market_value_per_acre", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("multiplier_factor", sa.Float(), nullable=True, server_default="1.0"),
        sa.Column("asset_valuation", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("total_compensation", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("consent_received", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("consent_date", sa.Date(), nullable=True),
        sa.Column("compensation_details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("geometry", geoalchemy2.types.Geometry(geometry_type="POLYGON", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"), nullable=True),
        sa.Column("center_lat", sa.Float(), nullable=True),
        sa.Column("center_lng", sa.Float(), nullable=True),
        sa.Column("polygon_coords", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assigned_officer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_land_parcels_id", "land_parcels", ["id"])
    op.create_index("ix_land_parcels_survey_number", "land_parcels", ["survey_number"])
    op.create_index("ix_land_parcels_project_id", "land_parcels", ["project_id"])
    op.create_index("ix_land_parcels_state", "land_parcels", ["state"])
    op.create_index("ix_land_parcels_district", "land_parcels", ["district"])
    op.create_index("ix_land_parcels_village", "land_parcels", ["village"])
    op.create_index("ix_land_parcels_land_type", "land_parcels", ["land_type"])
    op.create_index("ix_land_parcels_acquisition_status", "land_parcels", ["acquisition_status"])
    op.create_index("ix_land_parcels_owner_user_id", "land_parcels", ["owner_user_id"])
    op.create_index("ix_land_parcels_assigned_officer_id", "land_parcels", ["assigned_officer_id"])


def downgrade() -> None:
    op.drop_table("land_parcels")
    op.drop_table("projects")
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("users")

