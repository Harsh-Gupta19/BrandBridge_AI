"""Database mapping for documents."""

from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    owner_type: Mapped[str] = mapped_column(sa.String(12), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), nullable=False)
    document_type: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    filename: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    storage_uri: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(sa.String(80), nullable=True)
    checksum: Mapped[str | None] = mapped_column(sa.String(64), nullable=True)
    page_count: Mapped[int | None] = mapped_column(sa.SmallInteger(), nullable=True)
    ingest_status: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, server_default=sa.text("'PENDING'")
    )
    uploaded_by: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
