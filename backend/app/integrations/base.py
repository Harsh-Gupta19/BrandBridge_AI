"""Provider-neutral contracts from Build Manual §5.7.

Adapters return these objects. Persistence and transaction ownership remain in
services/repositories; provider payloads stay inside their individual adapters.
"""

from typing import Any, ClassVar, Literal, Protocol

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, SecretStr, model_validator

from app.models.enums import ContentType, DataProvenance, Platform


class NormalisedMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    followers: int | None = Field(default=None, ge=0)
    total_content: int | None = Field(default=None, ge=0)
    total_views: int | None = Field(default=None, ge=0)
    sample_size: int | None = Field(default=None, ge=0)
    sample_window_start: AwareDatetime | None = None
    sample_window_end: AwareDatetime | None = None
    average_views: float | None = Field(default=None, ge=0)
    median_views: float | None = Field(default=None, ge=0)
    average_likes: float | None = Field(default=None, ge=0)
    average_comments: float | None = Field(default=None, ge=0)
    engagement_rate: float | None = Field(default=None, ge=0, le=1)
    posts_last_30_days: int | None = Field(default=None, ge=0)
    platform_specific: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_sample_window(self) -> "NormalisedMetrics":
        if (
            self.sample_window_start is not None
            and self.sample_window_end is not None
            and self.sample_window_end < self.sample_window_start
        ):
            raise ValueError("sample_window_end must be on or after sample_window_start")
        return self


class NormalisedContent(BaseModel):
    """One content item mapped onto creator_content_items (§5.6)."""

    model_config = ConfigDict(extra="forbid")

    external_content_id: str | None = Field(default=None, max_length=160)
    media_type: ContentType | None = None
    caption: str | None = None
    transcript: str | None = None
    published_at: AwareDatetime | None = None
    organic_or_sponsored: Literal["ORGANIC", "SPONSORED", "UNKNOWN"] = "UNKNOWN"
    brand_entity: str | None = Field(default=None, max_length=160)
    detection_evidence: str | None = None
    detection_confidence: float | None = Field(default=None, ge=0, le=1)
    metrics_json: dict[str, Any] = Field(default_factory=dict)
    data_provenance: DataProvenance


class NormalisedAccount(BaseModel):
    model_config = ConfigDict(extra="forbid")

    platform: Platform
    external_account_id: str = Field(min_length=1, max_length=128)
    handle: str | None = Field(default=None, max_length=120)
    profile_url: str | None = Field(default=None, max_length=500)
    account_type: str | None = Field(default=None, max_length=24)
    verified_by_oauth: bool = False
    metrics: NormalisedMetrics
    recent_content: list[NormalisedContent] = Field(default_factory=list)
    captured_at: AwareDatetime
    provenance: DataProvenance
    degraded_reason: str | None = None


class OAuthTokens(BaseModel):
    """Internal adapter result; never an API response model or a log payload."""

    model_config = ConfigDict(extra="forbid")

    access_token: SecretStr
    refresh_token: SecretStr | None = None
    token_type: str = "Bearer"
    expires_at: AwareDatetime | None = None
    granted_scopes: list[str] = Field(default_factory=list)


class SocialAdapter(Protocol):
    platform: ClassVar[Platform]

    def authorize_url(self, state: str) -> str: ...

    async def exchange_code(self, code: str) -> OAuthTokens: ...

    async def fetch_public(self, handle: str) -> NormalisedAccount: ...

    async def fetch_authorized(self, tokens: OAuthTokens) -> NormalisedAccount: ...

