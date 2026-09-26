"""Normalised social accounts, dated snapshots, content and sync audit.

Build Manual section 5.2.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0004_social_evidence"
down_revision = "0003_creator_commercial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "social_accounts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("creator_id", sa.UUID(), nullable=False),
        sa.Column("platform", sa.String(length=16), nullable=False),
        sa.Column("external_account_id", sa.String(length=128), nullable=False),
        sa.Column("handle", sa.String(length=120), nullable=True),
        sa.Column("profile_url", sa.String(length=500), nullable=True),
        sa.Column("account_type", sa.String(length=24), nullable=True),
        sa.Column(
            "verified_by_oauth", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("token_ciphertext", sa.LargeBinary(), nullable=True),
        sa.Column(
            "granted_scopes",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "sync_status", sa.String(length=16), server_default=sa.text("'NEVER'"), nullable=False
        ),
        sa.Column("data_provenance", sa.String(length=24), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["creator_id"], ["creator_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("platform", "external_account_id", name="uq_social_platform_account"),
    )
    op.create_index("ix_social_creator", "social_accounts", ["creator_id"], unique=False)
    op.create_table(
        "social_metric_snapshots",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("social_account_id", sa.UUID(), nullable=False),
        sa.Column(
            "captured_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("followers", sa.Integer(), nullable=True),
        sa.Column("total_content", sa.Integer(), nullable=True),
        sa.Column("total_views", sa.BigInteger(), nullable=True),
        sa.Column("sample_size", sa.SmallInteger(), nullable=True),
        sa.Column("sample_window_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sample_window_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("average_views", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("median_views", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("average_likes", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("average_comments", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("engagement_rate", sa.Numeric(precision=6, scale=4), nullable=True),
        sa.Column("posts_last_30_days", sa.SmallInteger(), nullable=True),
        sa.Column(
            "platform_specific",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column("data_provenance", sa.String(length=24), nullable=False),
        sa.ForeignKeyConstraint(["social_account_id"], ["social_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_snap_account_time",
        "social_metric_snapshots",
        ["social_account_id", "captured_at"],
        unique=False,
    )
    op.create_table(
        "creator_content_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("creator_id", sa.UUID(), nullable=False),
        sa.Column("social_account_id", sa.UUID(), nullable=True),
        sa.Column("external_content_id", sa.String(length=160), nullable=True),
        sa.Column("media_type", sa.String(length=16), nullable=True),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "organic_or_sponsored",
            sa.String(length=12),
            server_default=sa.text("'UNKNOWN'"),
            nullable=False,
        ),
        sa.Column("brand_entity", sa.String(length=160), nullable=True),
        sa.Column("detection_evidence", sa.Text(), nullable=True),
        sa.Column("detection_confidence", sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column(
            "metrics_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column("data_provenance", sa.String(length=24), nullable=False),
        sa.ForeignKeyConstraint(["creator_id"], ["creator_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["social_account_id"], ["social_accounts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_content_creator_pub",
        "creator_content_items",
        ["creator_id", "published_at"],
        unique=False,
    )
    op.create_table(
        "integration_sync_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("social_account_id", sa.UUID(), nullable=True),
        sa.Column("platform", sa.String(length=16), nullable=False),
        sa.Column("request_class", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("error_category", sa.String(length=40), nullable=True),
        sa.Column("error_detail", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("correlation_id", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["social_account_id"], ["social_accounts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_sync_account_time",
        "integration_sync_logs",
        ["social_account_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_sync_account_time", table_name="integration_sync_logs")
    op.drop_table("integration_sync_logs")
    op.drop_index("ix_content_creator_pub", table_name="creator_content_items")
    op.drop_table("creator_content_items")
    op.drop_index("ix_snap_account_time", table_name="social_metric_snapshots")
    op.drop_table("social_metric_snapshots")
    op.drop_index("ix_social_creator", table_name="social_accounts")
    op.drop_table("social_accounts")
