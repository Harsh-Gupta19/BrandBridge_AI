"""Versioned creator vectors and multi-vertical content clusters.

Build Manual section 5.2.
"""

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0006_representations_vectors"
down_revision = "0005_campaign_requirements"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "creator_representations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("creator_id", sa.UUID(), nullable=False),
        sa.Column("representation_version", sa.String(length=32), nullable=False),
        sa.Column("encoder_name", sa.String(length=80), nullable=False),
        sa.Column("source_text", sa.Text(), nullable=True),
        sa.Column("overall_embedding", Vector(384), nullable=False),
        sa.Column(
            "topic_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column(
            "style_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column(
            "value_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column("is_current", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["creator_id"], ["creator_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_repr_current",
        "creator_representations",
        ["creator_id"],
        unique=True,
        postgresql_where=sa.text("is_current = true"),
    )
    op.create_index(
        "ix_repr_vec",
        "creator_representations",
        ["overall_embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_ops={"overall_embedding": "vector_cosine_ops"},
    )
    op.create_table(
        "creator_content_clusters",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("representation_id", sa.UUID(), nullable=False),
        sa.Column("label", sa.String(length=80), nullable=False),
        sa.Column("share", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("embedding", Vector(384), nullable=False),
        sa.Column("item_count", sa.SmallInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["representation_id"], ["creator_representations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_cluster_vec",
        "creator_content_clusters",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cluster_vec",
        table_name="creator_content_clusters",
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.drop_table("creator_content_clusters")
    op.drop_index(
        "ix_repr_vec",
        table_name="creator_representations",
        postgresql_using="hnsw",
        postgresql_ops={"overall_embedding": "vector_cosine_ops"},
    )
    op.drop_index(
        "uq_repr_current",
        table_name="creator_representations",
        postgresql_where=sa.text("is_current = true"),
    )
    op.drop_table("creator_representations")
