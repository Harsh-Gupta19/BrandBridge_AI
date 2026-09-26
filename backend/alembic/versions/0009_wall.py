"""Community posts, comments, reactions and profile follows, separate from matching.

Build Manual section 5.2.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0009_wall"
down_revision = "0008_collaboration_knowledge"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "wall_posts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("author_user_id", sa.UUID(), nullable=False),
        sa.Column("author_role", sa.String(length=8), nullable=False),
        sa.Column("author_profile_id", sa.UUID(), nullable=False),
        sa.Column(
            "post_kind", sa.String(length=16), server_default=sa.text("'IDEA'"), nullable=False
        ),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "topics",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column("media_uri", sa.String(length=500), nullable=True),
        sa.Column("linked_campaign_id", sa.UUID(), nullable=True),
        sa.Column(
            "visibility", sa.String(length=16), server_default=sa.text("'MEMBERS'"), nullable=False
        ),
        sa.Column(
            "status", sa.String(length=16), server_default=sa.text("'PUBLISHED'"), nullable=False
        ),
        sa.Column("reply_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("reaction_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("edited_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("char_length(body) <= 2000", name="ck_wall_post_length"),
        sa.ForeignKeyConstraint(["author_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["linked_campaign_id"], ["campaigns.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_wall_feed", "wall_posts", ["status", "created_at"], unique=False)
    op.create_index(
        "ix_wall_author", "wall_posts", ["author_profile_id", "created_at"], unique=False
    )
    op.create_index(
        "ix_wall_topics", "wall_posts", ["topics"], unique=False, postgresql_using="gin"
    )
    op.create_table(
        "wall_comments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("post_id", sa.UUID(), nullable=False),
        sa.Column("author_user_id", sa.UUID(), nullable=False),
        sa.Column("author_role", sa.String(length=8), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "status", sa.String(length=16), server_default=sa.text("'PUBLISHED'"), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("char_length(body) <= 1000", name="ck_wall_comment_length"),
        sa.ForeignKeyConstraint(["author_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["post_id"], ["wall_posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_wall_comment_post", "wall_comments", ["post_id", "created_at"], unique=False
    )
    op.create_table(
        "wall_reactions",
        sa.Column("post_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["post_id"], ["wall_posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("post_id", "user_id"),
    )
    op.create_table(
        "wall_follows",
        sa.Column("follower_user_id", sa.UUID(), nullable=False),
        sa.Column("followed_profile_id", sa.UUID(), nullable=False),
        sa.Column("followed_kind", sa.String(length=8), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["follower_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("follower_user_id", "followed_profile_id"),
    )
    op.create_index("ix_follow_profile", "wall_follows", ["followed_profile_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_follow_profile", table_name="wall_follows")
    op.drop_table("wall_follows")
    op.drop_table("wall_reactions")
    op.drop_index("ix_wall_comment_post", table_name="wall_comments")
    op.drop_table("wall_comments")
    op.drop_index("ix_wall_topics", table_name="wall_posts", postgresql_using="gin")
    op.drop_index("ix_wall_author", table_name="wall_posts")
    op.drop_index("ix_wall_feed", table_name="wall_posts")
    op.drop_table("wall_posts")
