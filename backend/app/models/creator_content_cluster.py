"""Database mapping for creator_content_clusters."""

from decimal import Decimal
from uuid import UUID, uuid4

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CreatorContentCluster(Base):
    __tablename__ = "creator_content_clusters"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    representation_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("creator_representations.id", ondelete="CASCADE"),
        nullable=False,
    )
    label: Mapped[str] = mapped_column(sa.String(80), nullable=False)
    share: Mapped[Decimal] = mapped_column(sa.Numeric(5, 4), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=False)
    item_count: Mapped[int | None] = mapped_column(sa.SmallInteger(), nullable=True)

    __table_args__ = (
        sa.Index(
            "ix_cluster_vec",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )
