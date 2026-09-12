"""Initial foundation tables and pgvector extension.

Revision ID: 0001_initial_foundation
Revises:
Create Date: 2026-09-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_foundation"
down_revision = None
branch_labels = None
depends_on = None


def created_at_column() -> sa.Column:
    return sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )


def updated_at_column() -> sa.Column:
    return sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("CREATOR", "BRAND", "ADMIN", name="user_role", native_enum=False),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        created_at_column(),
        updated_at_column(),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "creator_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=120), nullable=True),
        sa.Column("categories", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("audience_summary", sa.JSON(), nullable=False, server_default="{}"),
        created_at_column(),
        updated_at_column(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "brand_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("brand_name", sa.String(length=255), nullable=False),
        sa.Column("industry", sa.String(length=120), nullable=True),
        sa.Column("website_url", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        created_at_column(),
        updated_at_column(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("brand_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("brief", sa.Text(), nullable=True),
        sa.Column("budget_amount", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("target_country", sa.String(length=120), nullable=True),
        sa.Column("target_audience", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("preferred_platforms", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("creator_categories", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("content_formats", sa.JSON(), nullable=False, server_default="[]"),
        created_at_column(),
        updated_at_column(),
        sa.ForeignKeyConstraint(["brand_profile_id"], ["brand_profiles.id"]),
    )

    op.create_table(
        "proposals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("creator_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "SUBMITTED",
                "ACCEPTED",
                "REJECTED",
                name="proposal_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("commercial_offer", sa.Numeric(precision=12, scale=2), nullable=True),
        created_at_column(),
        updated_at_column(),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"]),
        sa.ForeignKeyConstraint(["creator_profile_id"], ["creator_profiles.id"]),
    )


def downgrade() -> None:
    op.drop_table("proposals")
    op.drop_table("campaigns")
    op.drop_table("brand_profiles")
    op.drop_table("creator_profiles")
    op.drop_table("users")
