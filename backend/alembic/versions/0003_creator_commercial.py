"""Creator profile evidence, historical rates, preferences and availability.

Build Manual section 5.2.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0003_creator_commercial"
down_revision = "0002_dual_role_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "creator_profiles",
        "categories",
        existing_type=sa.JSON(),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        postgresql_using="categories::jsonb",
        server_default=sa.text("'[]'::jsonb"),
    )
    op.alter_column(
        "creator_profiles",
        "audience_summary",
        existing_type=sa.JSON(),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        postgresql_using="audience_summary::jsonb",
        server_default=sa.text("'{}'::jsonb"),
    )
    op.add_column("creator_profiles", sa.Column("country_code", sa.CHAR(length=2), nullable=True))
    op.add_column("creator_profiles", sa.Column("city", sa.String(length=120), nullable=True))
    op.add_column(
        "creator_profiles",
        sa.Column(
            "languages",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
    )
    op.add_column(
        "creator_profiles",
        sa.Column(
            "content_topics",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
    )
    op.add_column(
        "creator_profiles",
        sa.Column(
            "content_formats",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
    )
    op.add_column(
        "creator_profiles",
        sa.Column(
            "travel_willingness", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
    )
    op.add_column(
        "creator_profiles", sa.Column("profile_image_url", sa.String(length=500), nullable=True)
    )
    op.add_column("creator_profiles", sa.Column("headline", sa.String(length=160), nullable=True))
    op.add_column(
        "creator_profiles",
        sa.Column("is_discoverable", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    op.add_column(
        "creator_profiles",
        sa.Column(
            "completeness_score",
            sa.Numeric(precision=4, scale=3),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.add_column(
        "creator_profiles",
        sa.Column(
            "data_provenance",
            sa.String(length=24),
            server_default=sa.text("'CREATOR_PROVIDED'"),
            nullable=False,
        ),
    )
    op.add_column(
        "creator_profiles",
        sa.Column("profile_version", sa.Integer(), server_default=sa.text("1"), nullable=False),
    )
    op.create_index("ix_creator_country", "creator_profiles", ["country_code"], unique=False)
    op.create_index(
        "ix_creator_categories",
        "creator_profiles",
        ["categories"],
        unique=False,
        postgresql_using="gin",
    )
    op.create_index(
        "ix_creator_discover",
        "creator_profiles",
        ["is_discoverable"],
        unique=False,
        postgresql_where=sa.text("is_discoverable = true"),
    )
    op.create_table(
        "creator_preferences",
        sa.Column("creator_id", sa.UUID(), nullable=False),
        sa.Column(
            "accepted_categories",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column(
            "excluded_categories",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column(
            "excluded_brand_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column(
            "preferred_models",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column("min_rate_inr", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("values_statement", sa.Text(), nullable=True),
        sa.Column(
            "content_restrictions",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column("max_campaigns_month", sa.SmallInteger(), nullable=True),
        sa.Column("responds_within_hours", sa.SmallInteger(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["creator_id"], ["creator_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("creator_id"),
    )
    op.create_table(
        "rate_card_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("creator_id", sa.UUID(), nullable=False),
        sa.Column("platform", sa.String(length=16), nullable=False),
        sa.Column("content_type", sa.String(length=16), nullable=False),
        sa.Column("rate_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("currency", sa.CHAR(length=3), server_default=sa.text("'INR'"), nullable=False),
        sa.Column("is_negotiable", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "effective_from", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False
        ),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("rate_amount >= 0", name="ck_rate_amount_nonnegative"),
        sa.ForeignKeyConstraint(["creator_id"], ["creator_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_rate_active",
        "rate_card_items",
        ["creator_id", "platform", "content_type"],
        unique=True,
        postgresql_where=sa.text("active = true"),
    )
    op.create_table(
        "creator_availability",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("creator_id", sa.UUID(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column(
            "status", sa.String(length=16), server_default=sa.text("'AVAILABLE'"), nullable=False
        ),
        sa.Column("notes", sa.String(length=240), nullable=True),
        sa.CheckConstraint("end_date >= start_date", name="ck_availability_dates"),
        sa.ForeignKeyConstraint(["creator_id"], ["creator_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("creator_availability")
    op.drop_index(
        "uq_rate_active", table_name="rate_card_items", postgresql_where=sa.text("active = true")
    )
    op.drop_table("rate_card_items")
    op.drop_table("creator_preferences")
    op.drop_index(
        "ix_creator_discover",
        table_name="creator_profiles",
        postgresql_where=sa.text("is_discoverable = true"),
    )
    op.drop_index("ix_creator_categories", table_name="creator_profiles", postgresql_using="gin")
    op.drop_index("ix_creator_country", table_name="creator_profiles")
    op.drop_column("creator_profiles", "profile_version")
    op.drop_column("creator_profiles", "data_provenance")
    op.drop_column("creator_profiles", "completeness_score")
    op.drop_column("creator_profiles", "is_discoverable")
    op.drop_column("creator_profiles", "headline")
    op.drop_column("creator_profiles", "profile_image_url")
    op.drop_column("creator_profiles", "travel_willingness")
    op.drop_column("creator_profiles", "content_formats")
    op.drop_column("creator_profiles", "content_topics")
    op.drop_column("creator_profiles", "languages")
    op.drop_column("creator_profiles", "city")
    op.drop_column("creator_profiles", "country_code")
    op.alter_column(
        "creator_profiles",
        "audience_summary",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        type_=sa.JSON(),
        postgresql_using="audience_summary::json",
        server_default=sa.text("'{}'::json"),
    )
    op.alter_column(
        "creator_profiles",
        "categories",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        type_=sa.JSON(),
        postgresql_using="categories::json",
        server_default=sa.text("'[]'::json"),
    )
