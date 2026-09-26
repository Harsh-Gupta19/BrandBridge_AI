"""Persist reciprocal scores, evidence, exclusions, models and research labels.

Build Manual section 5.2.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0007_matching_and_labels"
down_revision = "0006_representations_vectors"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "model_versions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False),
        sa.Column("algorithm", sa.String(length=40), nullable=False),
        sa.Column("feature_version", sa.String(length=32), nullable=False),
        sa.Column("trained_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("train_rows", sa.Integer(), nullable=True),
        sa.Column(
            "metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column("artifact_path", sa.String(length=300), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("model_version", name="uq_model_version"),
    )
    op.create_table(
        "match_scores",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("campaign_id", sa.UUID(), nullable=False),
        sa.Column("creator_id", sa.UUID(), nullable=False),
        sa.Column("direction", sa.String(length=16), nullable=False),
        sa.Column("eligibility_status", sa.String(length=20), nullable=False),
        sa.Column("structured_score", sa.Numeric(precision=6, scale=5), nullable=True),
        sa.Column("semantic_score", sa.Numeric(precision=6, scale=5), nullable=True),
        sa.Column("brand_side_score", sa.Numeric(precision=6, scale=5), nullable=True),
        sa.Column("creator_side_score", sa.Numeric(precision=6, scale=5), nullable=True),
        sa.Column("reciprocal_score", sa.Numeric(precision=6, scale=5), nullable=True),
        sa.Column("reranked_score", sa.Numeric(precision=6, scale=5), nullable=True),
        sa.Column("final_rank", sa.SmallInteger(), nullable=True),
        sa.Column("feature_version", sa.String(length=32), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False),
        sa.Column("representation_version", sa.String(length=32), nullable=True),
        sa.Column("scoring_profile", sa.String(length=32), nullable=False),
        sa.Column(
            "components",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["creator_id"], ["creator_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "campaign_id",
            "creator_id",
            "direction",
            "model_version",
            "feature_version",
            name="uq_match_pair_direction_versions",
        ),
    )
    op.create_index(
        "ix_match_rank", "match_scores", ["campaign_id", "direction", "final_rank"], unique=False
    )
    op.create_index(
        "ix_match_creator",
        "match_scores",
        ["creator_id", "direction", "reciprocal_score"],
        unique=False,
    )
    op.create_table(
        "match_evidence",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("match_score_id", sa.UUID(), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("value_text", sa.String(length=240), nullable=True),
        sa.Column("value_numeric", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("provenance", sa.String(length=24), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["match_score_id"], ["match_scores.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "eligibility_exclusions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("campaign_id", sa.UUID(), nullable=False),
        sa.Column("creator_id", sa.UUID(), nullable=False),
        sa.Column("rule_code", sa.String(length=48), nullable=False),
        sa.Column("rule_version", sa.String(length=16), nullable=False),
        sa.Column("detail", sa.String(length=240), nullable=True),
        sa.Column("confidence", sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["creator_id"], ["creator_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "pair_labels",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("campaign_id", sa.UUID(), nullable=False),
        sa.Column("creator_id", sa.UUID(), nullable=False),
        sa.Column("rater_id", sa.String(length=40), nullable=False),
        sa.Column("brand_rating", sa.SmallInteger(), nullable=True),
        sa.Column("creator_rating", sa.SmallInteger(), nullable=True),
        sa.Column(
            "mutually_relevant",
            sa.Boolean(),
            sa.Computed("brand_rating >= 2 AND creator_rating >= 2", persisted=True),
            nullable=True,
        ),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("label_source", sa.String(length=24), nullable=False),
        sa.Column("rubric_version", sa.String(length=16), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("brand_rating BETWEEN 0 AND 3", name="ck_pair_brand_rating"),
        sa.CheckConstraint("creator_rating BETWEEN 0 AND 3", name="ck_pair_creator_rating"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["creator_id"], ["creator_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "campaign_id", "creator_id", "rater_id", "rubric_version", name="uq_pair_rater_rubric"
        ),
    )
    op.create_table(
        "experiment_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("run_name", sa.String(length=80), nullable=False),
        sa.Column("variant", sa.String(length=48), nullable=False),
        sa.Column("dataset_version", sa.String(length=32), nullable=False),
        sa.Column("feature_version", sa.String(length=32), nullable=True),
        sa.Column("model_version", sa.String(length=32), nullable=True),
        sa.Column("split_strategy", sa.String(length=32), nullable=True),
        sa.Column(
            "metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("experiment_runs")
    op.drop_table("pair_labels")
    op.drop_table("eligibility_exclusions")
    op.drop_table("match_evidence")
    op.drop_index("ix_match_creator", table_name="match_scores")
    op.drop_index("ix_match_rank", table_name="match_scores")
    op.drop_table("match_scores")
    op.drop_table("model_versions")
