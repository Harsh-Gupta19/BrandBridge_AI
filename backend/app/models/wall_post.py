"""Database mapping for wall_posts."""

from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import InitiatedBy


class WallPost(Base):
    __tablename__ = "wall_posts"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    author_user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    author_role: Mapped[InitiatedBy] = mapped_column(
        sa.Enum(InitiatedBy, native_enum=False, length=8, validate_strings=True), nullable=False
    )
    author_profile_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), nullable=False)
    post_kind: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, server_default=sa.text("'IDEA'")
    )
    body: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    topics: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    media_uri: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    linked_campaign_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True,
    )
    visibility: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, server_default=sa.text("'MEMBERS'")
    )
    status: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, server_default=sa.text("'PUBLISHED'")
    )
    reply_count: Mapped[int] = mapped_column(
        sa.Integer(), nullable=False, server_default=sa.text("0")
    )
    reaction_count: Mapped[int] = mapped_column(
        sa.Integer(), nullable=False, server_default=sa.text("0")
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
    edited_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        sa.CheckConstraint("char_length(body) <= 2000", name="ck_wall_post_length"),
        sa.Index("ix_wall_author", "author_profile_id", "created_at"),
        sa.Index("ix_wall_feed", "status", "created_at"),
        sa.Index("ix_wall_topics", "topics", postgresql_using="gin"),
    )
