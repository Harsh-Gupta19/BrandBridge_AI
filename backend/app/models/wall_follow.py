"""Database mapping for wall_follows."""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import InitiatedBy


class WallFollow(Base):
    __tablename__ = "wall_follows"

    follower_user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    followed_profile_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False
    )
    followed_kind: Mapped[InitiatedBy] = mapped_column(
        sa.Enum(InitiatedBy, native_enum=False, length=8, validate_strings=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    __table_args__ = (sa.Index("ix_follow_profile", "followed_profile_id"),)
