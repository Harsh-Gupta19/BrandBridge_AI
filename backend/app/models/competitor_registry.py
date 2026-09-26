"""Database mapping for competitor_registry."""

from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CompetitorRegistry(Base):
    __tablename__ = "competitor_registry"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    parent_entity: Mapped[str] = mapped_column(sa.String(160), nullable=False)
    brand: Mapped[str] = mapped_column(sa.String(160), nullable=False)
    product_line: Mapped[str | None] = mapped_column(sa.String(160), nullable=True)
    aliases: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    handles: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
