"""Database mapping for creator_profiles."""

from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin
from app.models.enums import DataProvenance

if TYPE_CHECKING:
    from app.models.proposal import Proposal
    from app.models.user import User


class CreatorProfile(TimestampMixin, Base):
    __tablename__ = "creator_profiles"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
    )
    display_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    location: Mapped[str | None] = mapped_column(sa.String(120), nullable=True)
    categories: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    audience_summary: Mapped[dict[str, Any]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'{}'"), default=dict
    )
    country_code: Mapped[str | None] = mapped_column(sa.CHAR(2), nullable=True)
    city: Mapped[str | None] = mapped_column(sa.String(120), nullable=True)
    languages: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    content_topics: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    content_formats: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    travel_willingness: Mapped[bool] = mapped_column(
        sa.Boolean(), nullable=False, server_default=sa.text("false")
    )
    profile_image_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    headline: Mapped[str | None] = mapped_column(sa.String(160), nullable=True)
    is_discoverable: Mapped[bool] = mapped_column(
        sa.Boolean(), nullable=False, server_default=sa.text("true")
    )
    completeness_score: Mapped[Decimal] = mapped_column(
        sa.Numeric(4, 3), nullable=False, server_default=sa.text("0")
    )
    data_provenance: Mapped[DataProvenance] = mapped_column(
        sa.Enum(DataProvenance, native_enum=False, length=24, validate_strings=True),
        nullable=False,
        server_default=sa.text("'CREATOR_PROVIDED'"),
    )
    profile_version: Mapped[int] = mapped_column(
        sa.Integer(), nullable=False, server_default=sa.text("1")
    )

    __table_args__ = (
        sa.UniqueConstraint("user_id"),
        sa.Index("ix_creator_categories", "categories", postgresql_using="gin"),
        sa.Index("ix_creator_country", "country_code"),
        sa.Index(
            "ix_creator_discover",
            "is_discoverable",
            postgresql_where=sa.text("is_discoverable = true"),
        ),
    )

    user: Mapped["User"] = relationship(back_populates="creator_profile")
    proposals: Mapped[list["Proposal"]] = relationship(back_populates="creator_profile")
