"""Database mapping for model_versions."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    model_version: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    algorithm: Mapped[str] = mapped_column(sa.String(40), nullable=False)
    feature_version: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    trained_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    train_rows: Mapped[int | None] = mapped_column(sa.Integer(), nullable=True)
    metrics: Mapped[dict[str, Any]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'{}'"), default=dict
    )
    artifact_path: Mapped[str | None] = mapped_column(sa.String(300), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean(), nullable=False, server_default=sa.text("false")
    )

    __table_args__ = (sa.UniqueConstraint("model_version", name="uq_model_version"),)
