"""Database mapping for experiment_runs."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ExperimentRun(Base):
    __tablename__ = "experiment_runs"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    run_name: Mapped[str] = mapped_column(sa.String(80), nullable=False)
    variant: Mapped[str] = mapped_column(sa.String(48), nullable=False)
    dataset_version: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    feature_version: Mapped[str | None] = mapped_column(sa.String(32), nullable=True)
    model_version: Mapped[str | None] = mapped_column(sa.String(32), nullable=True)
    split_strategy: Mapped[str | None] = mapped_column(sa.String(32), nullable=True)
    metrics: Mapped[dict[str, Any]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'{}'"), default=dict
    )
    notes: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
