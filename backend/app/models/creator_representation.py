"""Database mapping for creator_representations."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CreatorRepresentation(Base):
    __tablename__ = "creator_representations"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    creator_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("creator_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    representation_version: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    encoder_name: Mapped[str] = mapped_column(sa.String(80), nullable=False)
    source_text: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    overall_embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=False)
    topic_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'{}'"), default=dict
    )
    style_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'{}'"), default=dict
    )
    value_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'{}'"), default=dict
    )
    is_current: Mapped[bool] = mapped_column(
        sa.Boolean(), nullable=False, server_default=sa.text("true")
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    __table_args__ = (
        sa.Index(
            "ix_repr_vec",
            "overall_embedding",
            postgresql_using="hnsw",
            postgresql_ops={"overall_embedding": "vector_cosine_ops"},
        ),
        sa.Index(
            "uq_repr_current",
            "creator_id",
            unique=True,
            postgresql_where=sa.text("is_current = true"),
        ),
    )
