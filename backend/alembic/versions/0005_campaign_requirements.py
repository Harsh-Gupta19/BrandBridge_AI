"""Raw briefs, confirmed requirements, discovery and competitor policies.

Build Manual section 5.2.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0005_campaign_requirements"
down_revision = "0004_social_evidence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("campaigns", sa.Column("raw_brief", sa.Text(), nullable=True))
    op.add_column("campaigns", sa.Column("objective", sa.String(length=32), nullable=True))
    op.add_column(
        "campaigns",
        sa.Column(
            "status", sa.String(length=16), server_default=sa.text("'DRAFT'"), nullable=False
        ),
    )
    op.add_column(
        "campaigns", sa.Column("budget_min", sa.Numeric(precision=12, scale=2), nullable=True)
    )
    op.add_column(
        "campaigns", sa.Column("budget_max", sa.Numeric(precision=12, scale=2), nullable=True)
    )
    op.add_column(
        "campaigns",
        sa.Column("currency", sa.CHAR(length=3), server_default=sa.text("'INR'"), nullable=False),
    )
    op.add_column("campaigns", sa.Column("starts_on", sa.Date(), nullable=True))
    op.add_column("campaigns", sa.Column("ends_on", sa.Date(), nullable=True))
    op.add_column("campaigns", sa.Column("parser_version", sa.String(length=32), nullable=True))
    op.add_column("campaigns", sa.Column("parsed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("campaigns", sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("campaigns", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))
    op.execute(
        """
        UPDATE campaigns SET raw_brief = brief, budget_max = budget_amount
        """
    )
    op.create_index("ix_campaign_status", "campaigns", ["status", "published_at"], unique=False)
    op.create_table(
        "campaign_requirements",
        sa.Column("campaign_id", sa.UUID(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=True),
        sa.Column("target_age_min", sa.SmallInteger(), nullable=True),
        sa.Column("target_age_max", sa.SmallInteger(), nullable=True),
        sa.Column(
            "geographies",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column(
            "languages",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column(
            "platforms",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column(
            "content_types",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column(
            "preferred_categories",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column(
            "mandatory_constraints",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column("min_followers", sa.Integer(), nullable=True),
        sa.Column("max_rate_inr", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column(
            "physical_attendance", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("attendance_city", sa.String(length=120), nullable=True),
        sa.Column(
            "extraction_confidence",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column("confirmed_by_user_id", sa.UUID(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["confirmed_by_user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("campaign_id"),
    )
    op.create_table(
        "campaign_discovery_policy",
        sa.Column("campaign_id", sa.UUID(), nullable=False),
        sa.Column(
            "mode", sa.String(length=24), server_default=sa.text("'NO_PREFERENCE'"), nullable=False
        ),
        sa.Column(
            "vertical_experience",
            sa.String(length=16),
            server_default=sa.text("'PREFERRED'"),
            nullable=False,
        ),
        sa.Column(
            "novelty_weight",
            sa.Numeric(precision=4, scale=3),
            server_default=sa.text("0.000"),
            nullable=False,
        ),
        sa.Column(
            "min_transferable_fit",
            sa.Numeric(precision=4, scale=3),
            server_default=sa.text("0.620"),
            nullable=False,
        ),
        sa.Column(
            "enable_fairness_rerank", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column(
            "diversity_lambda",
            sa.Numeric(precision=4, scale=3),
            server_default=sa.text("0.300"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("campaign_id"),
    )
    op.create_table(
        "competitor_registry",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("parent_entity", sa.String(length=160), nullable=False),
        sa.Column("brand", sa.String(length=160), nullable=False),
        sa.Column("product_line", sa.String(length=160), nullable=True),
        sa.Column(
            "aliases",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column(
            "handles",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "campaign_competitor_policies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("campaign_id", sa.UUID(), nullable=False),
        sa.Column("competitor_id", sa.UUID(), nullable=False),
        sa.Column(
            "association_type",
            sa.String(length=32),
            server_default=sa.text("'PAID_ONLY'"),
            nullable=False,
        ),
        sa.Column(
            "lookback_days", sa.SmallInteger(), server_default=sa.text("180"), nullable=False
        ),
        sa.Column(
            "action", sa.String(length=16), server_default=sa.text("'EXCLUDE'"), nullable=False
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["competitor_id"],
            ["competitor_registry.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "brand_products",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("brand_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["brand_id"], ["brand_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_brand_products_brand", "brand_products", ["brand_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_brand_products_brand", table_name="brand_products")
    op.drop_table("brand_products")
    op.drop_table("campaign_competitor_policies")
    op.drop_table("competitor_registry")
    op.drop_table("campaign_discovery_policy")
    op.drop_table("campaign_requirements")
    op.drop_index("ix_campaign_status", table_name="campaigns")
    op.drop_column("campaigns", "published_at")
    op.drop_column("campaigns", "confirmed_at")
    op.drop_column("campaigns", "parsed_at")
    op.drop_column("campaigns", "parser_version")
    op.drop_column("campaigns", "ends_on")
    op.drop_column("campaigns", "starts_on")
    op.drop_column("campaigns", "currency")
    op.drop_column("campaigns", "budget_max")
    op.drop_column("campaigns", "budget_min")
    op.drop_column("campaigns", "status")
    op.drop_column("campaigns", "objective")
    op.drop_column("campaigns", "raw_brief")
