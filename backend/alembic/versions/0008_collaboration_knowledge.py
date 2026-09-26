"""Two-way versioned proposals, collaborations, knowledge and AI audit.

Build Manual section 5.2.
"""

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0008_collaboration_knowledge"
down_revision = "0007_matching_and_labels"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "proposals",
        "status",
        existing_type=sa.Enum(
            "DRAFT", "SUBMITTED", "ACCEPTED", "REJECTED", name="proposal_status", native_enum=False
        ),
        type_=sa.Enum(
            "DRAFT",
            "SUBMITTED",
            "REVIEWING",
            "COUNTER_OFFER",
            "ACCEPTED",
            "REJECTED",
            "WITHDRAWN",
            name="proposal_status",
            native_enum=False,
        ),
    )
    op.add_column(
        "proposals",
        sa.Column(
            "initiated_by", sa.String(length=8), server_default=sa.text("'CREATOR'"), nullable=False
        ),
    )
    op.add_column("proposals", sa.Column("match_score_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_proposals_match_score_id", "proposals", "match_scores", ["match_score_id"], ["id"]
    )
    op.add_column(
        "proposals",
        sa.Column(
            "deliverables",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
    )
    op.add_column(
        "proposals",
        sa.Column("currency", sa.CHAR(length=3), server_default=sa.text("'INR'"), nullable=False),
    )
    op.add_column(
        "proposals",
        sa.Column(
            "collaboration_model",
            sa.String(length=16),
            server_default=sa.text("'PAID'"),
            nullable=False,
        ),
    )
    op.add_column("proposals", sa.Column("available_from", sa.Date(), nullable=True))
    op.add_column(
        "proposals",
        sa.Column(
            "current_version", sa.SmallInteger(), server_default=sa.text("1"), nullable=False
        ),
    )
    op.add_column(
        "proposals",
        sa.Column("ai_assisted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column("proposals", sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_proposal_campaign", "proposals", ["campaign_id", "status"], unique=False)
    op.create_index(
        "ix_proposal_creator", "proposals", ["creator_profile_id", "status"], unique=False
    )
    op.create_table(
        "proposal_versions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("proposal_id", sa.UUID(), nullable=False),
        sa.Column("version_no", sa.SmallInteger(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("currency", sa.CHAR(length=3), server_default=sa.text("'INR'"), nullable=False),
        sa.Column(
            "deliverables",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.UUID(), nullable=False),
        sa.Column("created_by_role", sa.String(length=8), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(["proposal_id"], ["proposals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("proposal_id", "version_no", name="uq_proposal_version"),
    )
    op.execute(
        """
        INSERT INTO proposal_versions
         (id, proposal_id, version_no, amount, currency, deliverables, message,
        created_by_user_id, created_by_role, created_at)
         SELECT gen_random_uuid(), p.id, 1, p.commercial_offer, p.currency, p.deliverables,
                p.message, c.user_id, 'CREATOR', p.created_at
         FROM proposals p JOIN creator_profiles c ON c.id = p.creator_profile_id
        """
    )
    op.create_table(
        "collaborations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("accepted_proposal_id", sa.UUID(), nullable=False),
        sa.Column("campaign_id", sa.UUID(), nullable=False),
        sa.Column("creator_id", sa.UUID(), nullable=False),
        sa.Column("brand_id", sa.UUID(), nullable=False),
        sa.Column(
            "status", sa.String(length=20), server_default=sa.text("'ACTIVE'"), nullable=False
        ),
        sa.Column("agreed_amount", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("currency", sa.CHAR(length=3), server_default=sa.text("'INR'"), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=True),
        sa.Column("ends_on", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["accepted_proposal_id"],
            ["proposals.id"],
        ),
        sa.ForeignKeyConstraint(
            ["brand_id"],
            ["brand_profiles.id"],
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id"],
            ["campaigns.id"],
        ),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["creator_profiles.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("accepted_proposal_id", name="uq_collaboration_accepted_proposal"),
    )
    op.create_table(
        "agreements",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("collaboration_id", sa.UUID(), nullable=False),
        sa.Column("version", sa.SmallInteger(), server_default=sa.text("1"), nullable=False),
        sa.Column("draft_text", sa.Text(), nullable=False),
        sa.Column(
            "evidence_refs",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column(
            "generated_by",
            sa.String(length=16),
            server_default=sa.text("'AI_DRAFT'"),
            nullable=False,
        ),
        sa.Column(
            "status", sa.String(length=20), server_default=sa.text("'DRAFT'"), nullable=False
        ),
        sa.Column("brand_approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("creator_approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["collaboration_id"], ["collaborations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("collaboration_id", sa.UUID(), nullable=True),
        sa.Column("proposal_id", sa.UUID(), nullable=True),
        sa.Column("sender_user_id", sa.UUID(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "collaboration_id IS NOT NULL OR proposal_id IS NOT NULL", name="ck_message_context"
        ),
        sa.ForeignKeyConstraint(["collaboration_id"], ["collaborations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["proposal_id"], ["proposals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["sender_user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "collaboration_outcomes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("proposal_id", sa.UUID(), nullable=False),
        sa.Column("accepted", sa.Boolean(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=True),
        sa.Column("brand_rating", sa.SmallInteger(), nullable=True),
        sa.Column("creator_rating", sa.SmallInteger(), nullable=True),
        sa.Column(
            "outcome_metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["proposal_id"], ["proposals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("proposal_id", name="uq_outcome_proposal"),
    )
    op.create_table(
        "documents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("owner_type", sa.String(length=12), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("document_type", sa.String(length=32), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("storage_uri", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=80), nullable=True),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.Column("page_count", sa.SmallInteger(), nullable=True),
        sa.Column(
            "ingest_status",
            sa.String(length=16),
            server_default=sa.text("'PENDING'"),
            nullable=False,
        ),
        sa.Column("uploaded_by", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("chunk_index", sa.SmallInteger(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("page_number", sa.SmallInteger(), nullable=True),
        sa.Column("embedding", Vector(384), nullable=False),
        sa.Column("token_count", sa.SmallInteger(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk"),
    )
    op.create_index(
        "ix_chunk_vec",
        "document_chunks",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.create_table(
        "ai_execution_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("workflow_type", sa.String(length=40), nullable=False),
        sa.Column("subject_type", sa.String(length=24), nullable=True),
        sa.Column("subject_id", sa.UUID(), nullable=True),
        sa.Column("actor_user_id", sa.UUID(), nullable=True),
        sa.Column("provider", sa.String(length=40), nullable=True),
        sa.Column("model", sa.String(length=80), nullable=True),
        sa.Column("prompt_version", sa.String(length=32), nullable=True),
        sa.Column("state_version", sa.String(length=32), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("estimated_cost", sa.Numeric(precision=10, scale=5), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("error_category", sa.String(length=40), nullable=True),
        sa.Column("correlation_id", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
         IF EXISTS (SELECT 1 FROM proposals WHERE status NOT IN
                    ('DRAFT','SUBMITTED','ACCEPTED','REJECTED')) THEN
           RAISE EXCEPTION 'Cannot downgrade proposals: %',
               'REVIEWING, COUNTER_OFFER and WITHDRAWN are not legacy statuses';
         END IF;
         END $$
        """
    )
    op.execute(
        """
        UPDATE proposals p SET commercial_offer = v.amount, message = v.message
        FROM proposal_versions v
        WHERE v.proposal_id = p.id AND v.version_no = p.current_version
        """
    )
    op.drop_table("ai_execution_logs")
    op.drop_index(
        "ix_chunk_vec",
        table_name="document_chunks",
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.drop_table("document_chunks")
    op.drop_table("documents")
    op.drop_table("collaboration_outcomes")
    op.drop_table("messages")
    op.drop_table("agreements")
    op.drop_table("collaborations")
    op.drop_table("proposal_versions")
    op.drop_index("ix_proposal_creator", table_name="proposals")
    op.drop_index("ix_proposal_campaign", table_name="proposals")
    op.drop_column("proposals", "responded_at")
    op.drop_column("proposals", "ai_assisted")
    op.drop_column("proposals", "current_version")
    op.drop_column("proposals", "available_from")
    op.drop_column("proposals", "collaboration_model")
    op.drop_column("proposals", "currency")
    op.drop_column("proposals", "deliverables")
    op.drop_constraint("fk_proposals_match_score_id", "proposals", type_="foreignkey")
    op.drop_column("proposals", "match_score_id")
    op.drop_column("proposals", "initiated_by")
    op.alter_column(
        "proposals",
        "status",
        existing_type=sa.Enum(
            "DRAFT",
            "SUBMITTED",
            "REVIEWING",
            "COUNTER_OFFER",
            "ACCEPTED",
            "REJECTED",
            "WITHDRAWN",
            name="proposal_status",
            native_enum=False,
        ),
        type_=sa.Enum(
            "DRAFT", "SUBMITTED", "ACCEPTED", "REJECTED", name="proposal_status", native_enum=False
        ),
    )
