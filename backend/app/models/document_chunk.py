"""Database mapping for document_chunks."""

from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    document_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(sa.SmallInteger(), nullable=False)
    chunk_text: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    page_number: Mapped[int | None] = mapped_column(sa.SmallInteger(), nullable=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=False)
    token_count: Mapped[int | None] = mapped_column(sa.SmallInteger(), nullable=True)
    chunk_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB(), nullable=False, server_default=sa.text("'{}'"), default=dict
    )

    __table_args__ = (
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk"),
        sa.Index(
            "ix_chunk_vec",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )
