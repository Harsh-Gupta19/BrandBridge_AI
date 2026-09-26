from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.integrations.base import (
    NormalisedAccount,
    NormalisedContent,
    NormalisedMetrics,
    OAuthTokens,
)
from app.models import User, UserRole, UserRoleRow
from app.models.enums import DataProvenance, Platform


def test_missing_metrics_stay_missing_and_defaults_are_independent():
    first = NormalisedMetrics()
    second = NormalisedMetrics()
    assert first.followers is None
    assert first.total_views is None
    assert first.engagement_rate is None
    first.platform_specific["hidden_count"] = True
    assert second.platform_specific == {}


@pytest.mark.parametrize("rate", [-0.01, 5.86, float("nan"), float("inf")])
def test_engagement_is_a_fraction_not_a_percentage(rate):
    with pytest.raises(ValidationError):
        NormalisedMetrics(engagement_rate=rate)


def test_account_with_manual_fallback_and_content_round_trips():
    account = NormalisedAccount(
        platform=Platform.BLUESKY,
        external_account_id="did:plc:example",
        metrics=NormalisedMetrics(engagement_rate=0.0586),
        captured_at=datetime(2026, 9, 26, tzinfo=UTC),
        provenance=DataProvenance.PUBLIC_OBSERVABLE,
        degraded_reason="Latest provider request failed; using a dated snapshot",
        recent_content=[
            NormalisedContent(
                external_content_id="post-1",
                caption="A caption",
                data_provenance=DataProvenance.PUBLIC_OBSERVABLE,
            )
        ],
    )
    restored = NormalisedAccount.model_validate_json(account.model_dump_json())
    assert restored == account
    assert restored.metrics.total_views is None
    assert restored.metrics.engagement_rate == 0.0586
    assert restored.platform is Platform.BLUESKY


def test_provider_fields_and_naive_timestamps_are_rejected():
    with pytest.raises(ValidationError):
        NormalisedMetrics(subscriberCount=100)
    with pytest.raises(ValidationError):
        NormalisedAccount(
            platform=Platform.YOUTUBE,
            external_account_id="channel",
            metrics=NormalisedMetrics(),
            captured_at=datetime(2026, 9, 26),
            provenance=DataProvenance.AUTHORIZED_API,
        )
    with pytest.raises(ValidationError):
        NormalisedMetrics(
            sample_window_start=datetime(2026, 9, 26, tzinfo=UTC),
            sample_window_end=datetime(2026, 9, 25, tzinfo=UTC),
        )


def test_tokens_are_redacted_in_representations_and_json():
    tokens = OAuthTokens(access_token="access-value", refresh_token="refresh-value")
    assert "access-value" not in repr(tokens)
    assert "refresh-value" not in tokens.model_dump_json()
    assert tokens.access_token.get_secret_value() == "access-value"


def test_user_role_membership_supports_both_modes():
    user = User(roles=[UserRoleRow(role=UserRole.CREATOR), UserRoleRow(role=UserRole.BRAND)])
    assert user.has_role(UserRole.CREATOR)
    assert user.has_role(UserRole.BRAND)
    assert not user.has_role(UserRole.ADMIN)
