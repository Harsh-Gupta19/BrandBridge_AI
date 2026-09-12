from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin
from app.models.enums import ProposalStatus


class Proposal(TimestampMixin, Base):
    __tablename__ = "proposals"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    creator_profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("creator_profiles.id"),
        nullable=False,
    )
    status: Mapped[ProposalStatus] = mapped_column(
        Enum(ProposalStatus, name="proposal_status", native_enum=False),
        default=ProposalStatus.DRAFT,
        nullable=False,
    )
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    commercial_offer: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    campaign: Mapped["Campaign"] = relationship(back_populates="proposals")
    creator_profile: Mapped["CreatorProfile"] = relationship(back_populates="proposals")
