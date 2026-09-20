"""
BrandBridge AI - Instagram API All-Fields Explorer

Purpose
-------
Learning/exploration collector for Instagram Professional accounts.

It is intentionally NOT a production scraper. It probes a broad set of
documented/current Instagram Graph API fields and resources and records
unavailable fields as null with an error/status explanation.

Supports:
1. Instagram Login
   - graph.instagram.com
   - separate token for an authorized Professional account
2. Facebook Login
   - graph.facebook.com
   - Page-linked Professional account
   - optional Page/User token variables

Expected output:
    data/raw/instagram/instagram_api_all_fields.json

Environment variables
---------------------
Required for Instagram Login:
    INSTAGRAM_ACCESS_TOKEN

Optional:
    INSTAGRAM_API_VERSION=v22.0
    INSTAGRAM_API_BASE=https://graph.instagram.com
    INSTAGRAM_USER_ID=
    INSTAGRAM_MEDIA_LIMIT=100
    INSTAGRAM_INCLUDE_INSIGHTS=true
    INSTAGRAM_INCLUDE_COMMENTS=true

For a Facebook Login run, set:
    INSTAGRAM_API_BASE=https://graph.facebook.com
    INSTAGRAM_ACCESS_TOKEN=<page/user access token>
    INSTAGRAM_USER_ID=<professional IG user id>

Notes
-----
- There is no fields=* endpoint. "All fields" here means a broad catalog
  of candidate fields/resources that this collector tests individually.
- Availability depends on API version, account type, permissions, token
  type, and the specific account.
- Do not put access tokens in the JSON output.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


# ---------------------------------------------------------------------------
# Paths / environment
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[4]


def load_dotenv_values() -> dict[str, str]:
    """
    Load .env directly so the script does not depend on VS Code terminal
    environment injection.
    """
    values: dict[str, str] = {}

    candidates = [
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / "backend" / ".env",
    ]

    for env_path in candidates:
        if not env_path.exists():
            continue

        try:
            for raw_line in env_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()

                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if (
                    len(value) >= 2
                    and value[0] == value[-1]
                    and value[0] in {'"', "'"}
                ):
                    value = value[1:-1]

                values[key] = value
        except OSError:
            pass

    return values


DOTENV_VALUES = load_dotenv_values()


def get_env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name) or DOTENV_VALUES.get(name) or default


API_VERSION = get_env("INSTAGRAM_API_VERSION", "v22.0")
BASE_URL = (get_env("INSTAGRAM_API_BASE", "https://graph.instagram.com") or "").rstrip(
    "/"
)
ACCESS_TOKEN = get_env("INSTAGRAM_ACCESS_TOKEN")
USER_ID = get_env("INSTAGRAM_USER_ID")

MEDIA_LIMIT = int(get_env("INSTAGRAM_MEDIA_LIMIT", "100") or "100")
INCLUDE_INSIGHTS = (get_env("INSTAGRAM_INCLUDE_INSIGHTS", "true") or "").lower() == "true"
INCLUDE_COMMENTS = (get_env("INSTAGRAM_INCLUDE_COMMENTS", "true") or "").lower() == "true"

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "instagram"
OUTPUT_FILE = OUTPUT_DIR / "instagram_api_all_fields.json"


# ---------------------------------------------------------------------------
# Candidate field catalog
# ---------------------------------------------------------------------------

PROFILE_FIELDS = [
    "id",
    "username",
    "name",
    "biography",
    "website",
    "profile_picture_url",
    "followers_count",
    "follows_count",
    "media_count",
    "account_type",
]

MEDIA_FIELDS = [
    "id",
    "caption",
    "media_type",
    "media_product_type",
    "media_url",
    "thumbnail_url",
    "permalink",
    "timestamp",
    "username",
    "shortcode",
    "like_count",
    "comments_count",
    "view_count",
    "is_comment_enabled",
    "is_shared_to_feed",
    "alt_text",
]

CAROUSEL_CHILD_FIELDS = [
    "id",
    "media_type",
    "media_url",
    "thumbnail_url",
    "permalink",
]

COMMENT_FIELDS = [
    "id",
    "text",
    "timestamp",
    "username",
    "like_count",
    "hidden",
    "from",
    "replies",
]

# Candidate Insights metrics. Meta may add/remove metrics or restrict them
# by account type, media type, period, or API version.
USER_INSIGHT_METRICS = [
    "accounts_engaged",
    "comments",
    "follows_and_unfollows",
    "likes",
    "profile_links_taps",
    "profile_views",
    "replies",
    "shares",
    "total_interactions",
    "views",
]

MEDIA_INSIGHT_METRICS = [
    "comments",
    "follows",
    "likes",
    "profile_activity",
    "profile_visits",
    "replies",
    "saved",
    "shares",
    "total_interactions",
    "views",
]

AUDIENCE_INSIGHT_METRICS = [
    "audience_city",
    "audience_country",
    "audience_gender_age",
]

# Common candidate fields for Page objects when using Facebook Login.
PAGE_FIELDS = [
    "id",
    "name",
    "access_token",
    "tasks",
    "instagram_business_account",
]

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

session = requests.Session()
session.headers.update(
    {
        "User-Agent": "BrandBridgeAI-Instagram-All-Fields-Explorer/1.0",
        "Accept": "application/json",
    }
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def endpoint(path: str) -> str:
    path = path.lstrip("/")
    return f"{BASE_URL}/{API_VERSION}/{path}"


def api_request(
    path: str,
    *,
    params: dict[str, Any] | None = None,
    timeout: int = 30,
) -> tuple[bool, dict[str, Any]]:
    """
    Return (success, payload).

    Payload is always JSON-like. Errors are kept so unavailable fields can
    be represented as null rather than silently dropped.
    """
    params = dict(params or {})
    params["access_token"] = ACCESS_TOKEN

    try:
        response = session.get(
            endpoint(path),
            params=params,
            timeout=timeout,
        )

        try:
            payload = response.json()
        except ValueError:
            payload = {"raw_text": response.text}

        if response.ok and "error" not in payload:
            return True, payload

        return False, {
            "http_status": response.status_code,
            "error": payload.get(
                "error",
                {
                    "message": response.text[:500],
                },
            ),
        }

    except requests.RequestException as exc:
        return False, {
            "error": {
                "type": "RequestException",
                "message": str(exc),
            }
        }


def normalize_value(value: Any) -> Any:
    """
    Preserve useful nested API values while converting empty strings to null.
    """
    if value == "":
        return None

    if isinstance(value, dict):
        return {k: normalize_value(v) for k, v in value.items()}

    if isinstance(value, list):
        return [normalize_value(v) for v in value]

    return value


def probe_fields(
    object_id: str,
    fields: list[str],
    *,
    label: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Probe every field individually.

    This is deliberately slower than one giant fields= request, but it lets
    the dataset retain field-level availability and nulls.
    """
    values: dict[str, Any] = {}
    status: dict[str, Any] = {}

    for field_name in fields:
        ok, payload = api_request(
            object_id,
            params={"fields": field_name},
        )

        if ok:
            value = normalize_value(payload.get(field_name))
            values[field_name] = value
            status[field_name] = {
                "available": value is not None,
                "value_is_null": value is None,
                "error": None,
            }
        else:
            values[field_name] = None
            status[field_name] = {
                "available": False,
                "value_is_null": True,
                "error": payload.get("error"),
                "http_status": payload.get("http_status"),
            }

        time.sleep(0.03)

    return values, status


def collect_paginated(
    path: str,
    *,
    params: dict[str, Any],
    limit: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Cursor pagination helper.
    """
    records: list[dict[str, Any]] = []
    page_count = 0

    current_params = dict(params)
    current_params["limit"] = min(limit, 100)

    while len(records) < limit:
        ok, payload = api_request(path, params=current_params)

        if not ok:
            return records, {
                "success": False,
                "pages": page_count,
                "error": payload.get("error"),
                "http_status": payload.get("http_status"),
            }

        page_count += 1
        batch = payload.get("data", [])

        if isinstance(batch, list):
            records.extend(batch)

        paging = payload.get("paging") or {}
        next_url = paging.get("next")

        if not next_url or not batch:
            break

        after = (paging.get("cursors") or {}).get("after")
        if not after:
            break

        current_params["after"] = after

        if len(records) >= limit:
            break

    return records[:limit], {
        "success": True,
        "pages": page_count,
        "records": len(records[:limit]),
    }


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

def collect_profile(user_id: str) -> dict[str, Any]:
    values, status = probe_fields(
        user_id,
        PROFILE_FIELDS,
        label="profile",
    )

    return {
        "fields": values,
        "field_status": status,
    }


# ---------------------------------------------------------------------------
# Media
# ---------------------------------------------------------------------------

def collect_media(user_id: str) -> dict[str, Any]:
    """
    Collect media and probe the candidate media fields individually.
    """
    # First get IDs. This request intentionally uses only id so it can work
    # even when another candidate field is unavailable.
    media, pagination_status = collect_paginated(
        f"{user_id}/media",
        params={"fields": "id"},
        limit=MEDIA_LIMIT,
    )

    normalized_media: list[dict[str, Any]] = []

    for index, media_stub in enumerate(media, start=1):
        media_id = media_stub.get("id")

        if not media_id:
            continue

        values, status = probe_fields(
            media_id,
            MEDIA_FIELDS,
            label=f"media[{index}]",
        )

        children: list[dict[str, Any]] = []
        children_status: dict[str, Any] | None = None

        # Carousel children are a separate edge.
        if values.get("media_type") == "CAROUSEL_ALBUM":
            child_records, child_pagination = collect_paginated(
                f"{media_id}/children",
                params={"fields": "id"},
                limit=100,
            )

            for child in child_records:
                child_id = child.get("id")
                if not child_id:
                    continue

                child_values, child_status = probe_fields(
                    child_id,
                    CAROUSEL_CHILD_FIELDS,
                    label=f"media[{index}].children",
                )

                children.append(
                    {
                        "fields": child_values,
                        "field_status": child_status,
                    }
                )

            children_status = child_pagination

        normalized_media.append(
            {
                "fields": values,
                "field_status": status,
                "children": children,
                "children_collection_status": children_status,
            }
        )

    return {
        "media": normalized_media,
        "pagination": pagination_status,
        "requested_fields": MEDIA_FIELDS,
        "children_requested_fields": CAROUSEL_CHILD_FIELDS,
    }


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def collect_comments(media_records: list[dict[str, Any]]) -> dict[str, Any]:
    if not INCLUDE_COMMENTS:
        return {
            "enabled": False,
            "media": [],
        }

    output: list[dict[str, Any]] = []

    for media_record in media_records:
        media_fields = media_record.get("fields", {})
        media_id = media_fields.get("id")

        if not media_id:
            continue

        # Request IDs first, then probe each comment field.
        comments, pagination_status = collect_paginated(
            f"{media_id}/comments",
            params={"fields": "id"},
            limit=100,
        )

        comment_rows: list[dict[str, Any]] = []

        for comment in comments:
            comment_id = comment.get("id")
            if not comment_id:
                continue

            values, status = probe_fields(
                comment_id,
                COMMENT_FIELDS,
                label=f"comment[{comment_id}]",
            )

            comment_rows.append(
                {
                    "fields": values,
                    "field_status": status,
                }
            )

        output.append(
            {
                "media_id": media_id,
                "comments": comment_rows,
                "pagination": pagination_status,
            }
        )

    return {
        "enabled": True,
        "media": output,
    }


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

def probe_insight_metric(
    object_id: str,
    metric: str,
    *,
    period: str,
    metric_type: str,
) -> dict[str, Any]:
    """
    Probe one metric. Because Insights metric availability changes, every
    metric gets its own result.
    """
    ok, payload = api_request(
        f"{object_id}/insights",
        params={
            "metric": metric,
            "period": period,
        },
    )

    if ok:
        return {
            "metric": metric,
            "period": period,
            "metric_type": metric_type,
            "available": True,
            "data": normalize_value(payload.get("data")),
            "error": None,
        }

    return {
        "metric": metric,
        "period": period,
        "metric_type": metric_type,
        "available": False,
        "data": None,
        "error": payload.get("error"),
        "http_status": payload.get("http_status"),
    }


def collect_user_insights(user_id: str) -> dict[str, Any]:
    if not INCLUDE_INSIGHTS:
        return {"enabled": False}

    results: list[dict[str, Any]] = []

    # "day" is broadly useful for metrics that support it.
    for metric in USER_INSIGHT_METRICS:
        results.append(
            probe_insight_metric(
                user_id,
                metric,
                period="day",
                metric_type="user",
            )
        )
        time.sleep(0.05)

    return {
        "enabled": True,
        "requested_metrics": USER_INSIGHT_METRICS,
        "results": results,
    }


def collect_media_insights(media_records: list[dict[str, Any]]) -> dict[str, Any]:
    if not INCLUDE_INSIGHTS:
        return {"enabled": False}

    output: list[dict[str, Any]] = []

    for media_record in media_records:
        media_fields = media_record.get("fields", {})
        media_id = media_fields.get("id")

        if not media_id:
            continue

        results: list[dict[str, Any]] = []

        for metric in MEDIA_INSIGHT_METRICS:
            # Some media insight metrics use no period; some API versions
            # accept period=day only for user insights. Probe without period.
            ok, payload = api_request(
                f"{media_id}/insights",
                params={"metric": metric},
            )

            if ok:
                results.append(
                    {
                        "metric": metric,
                        "available": True,
                        "data": normalize_value(payload.get("data")),
                        "error": None,
                    }
                )
            else:
                results.append(
                    {
                        "metric": metric,
                        "available": False,
                        "data": None,
                        "error": payload.get("error"),
                        "http_status": payload.get("http_status"),
                    }
                )

            time.sleep(0.05)

        output.append(
            {
                "media_id": media_id,
                "results": results,
            }
        )

    return {
        "enabled": True,
        "requested_metrics": MEDIA_INSIGHT_METRICS,
        "media": output,
    }


# ---------------------------------------------------------------------------
# Facebook Login Page discovery
# ---------------------------------------------------------------------------

def collect_page_context() -> dict[str, Any]:
    """
    Optional helper for Facebook Login.

    If INSTAGRAM_PAGE_ID is present, probe the Page fields.
    If it is absent, return a null schema rather than guessing a Page.
    """
    page_id = get_env("INSTAGRAM_PAGE_ID")

    if not page_id:
        return {
            "enabled": False,
            "page_id": None,
            "fields": {field: None for field in PAGE_FIELDS},
            "field_status": {
                field: {
                    "available": False,
                    "value_is_null": True,
                    "error": "INSTAGRAM_PAGE_ID not configured",
                }
                for field in PAGE_FIELDS
            },
        }

    values, status = probe_fields(
        page_id,
        PAGE_FIELDS,
        label="page",
    )

    return {
        "enabled": True,
        "page_id": page_id,
        "fields": values,
        "field_status": status,
    }


# ---------------------------------------------------------------------------
# Derived summary
# ---------------------------------------------------------------------------

def safe_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def calculate_summary(media: list[dict[str, Any]]) -> dict[str, Any]:
    likes: list[float] = []
    comments: list[float] = []
    views: list[float] = []

    media_types: dict[str, int] = {}
    product_types: dict[str, int] = {}

    for row in media:
        fields = row.get("fields", {})

        like_count = safe_number(fields.get("like_count"))
        comment_count = safe_number(fields.get("comments_count"))
        view_count = safe_number(fields.get("view_count"))

        if like_count is not None:
            likes.append(like_count)

        if comment_count is not None:
            comments.append(comment_count)

        if view_count is not None:
            views.append(view_count)

        media_type = fields.get("media_type")
        if media_type:
            media_types[media_type] = media_types.get(media_type, 0) + 1

        product_type = fields.get("media_product_type")
        if product_type:
            product_types[product_type] = product_types.get(product_type, 0) + 1

    def avg(values: list[float]) -> float | None:
        return sum(values) / len(values) if values else None

    total_likes = sum(likes) if likes else None
    total_comments = sum(comments) if comments else None
    total_views = sum(views) if views else None

    return {
        "media_count_collected": len(media),
        "media_type_distribution": media_types,
        "media_product_type_distribution": product_types,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_views": total_views,
        "average_likes": avg(likes),
        "average_comments": avg(comments),
        "average_views": avg(views),
    }


# ---------------------------------------------------------------------------
# Main collector
# ---------------------------------------------------------------------------

def run() -> dict[str, Any]:
    if not ACCESS_TOKEN:
        raise RuntimeError(
            "INSTAGRAM_ACCESS_TOKEN is not configured. "
            "Add it to .env or the environment."
        )

    if not USER_ID:
        raise RuntimeError(
            "INSTAGRAM_USER_ID is not configured. "
            "Add the Instagram Professional account ID to .env."
        )

    print("=" * 72)
    print("BrandBridge AI - Instagram API All-Fields Explorer")
    print("=" * 72)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"API base:     {BASE_URL}")
    print(f"API version:  {API_VERSION}")
    print(f"User ID:      {USER_ID}")
    print(f"Token loaded: {bool(ACCESS_TOKEN)}")
    print(f"Output:       {OUTPUT_FILE}")
    print()

    # Minimal authentication check.
    ok, me = api_request(
        USER_ID,
        params={"fields": "id"},
    )

    if not ok:
        raise RuntimeError(
            "Instagram authentication/request failed:\n"
            + json.dumps(me, indent=2, ensure_ascii=False)
        )

    print("Authentication check: OK")

    profile = collect_profile(USER_ID)
    print("Profile field probing complete.")

    media_result = collect_media(USER_ID)
    media = media_result["media"]
    print(f"Media collection complete: {len(media)} media records.")

    comments = collect_comments(media)
    print("Comment probing complete.")

    user_insights = collect_user_insights(USER_ID)
    print("User insights probing complete.")

    media_insights = collect_media_insights(media)
    print("Media insights probing complete.")

    page_context = collect_page_context()
    print("Page context probing complete.")

    summary = calculate_summary(media)

    result = {
        "metadata": {
            "collector": "instagram_api_all_fields",
            "brandbridge_project": "BrandBridge AI",
            "collected_at": now_iso(),
            "api_base": BASE_URL,
            "api_version": API_VERSION,
            "instagram_user_id": USER_ID,
            "token_type": "redacted",
            "purpose": "learning_and_exploration",
            "important_note": (
                "This is a broad field/resource explorer. Instagram does not "
                "provide a universal fields=* schema endpoint. Availability "
                "depends on API version, account type, permissions, token, "
                "and resource."
            ),
        },
        "profile": profile,
        "media": media_result,
        "comments": comments,
        "insights": {
            "user": user_insights,
            "media": media_insights,
        },
        "facebook_login_page_context": page_context,
        "derived_summary": summary,
        "schemas": {
            "profile_fields": {
                field: None for field in PROFILE_FIELDS
            },
            "media_fields": {
                field: None for field in MEDIA_FIELDS
            },
            "carousel_child_fields": {
                field: None for field in CAROUSEL_CHILD_FIELDS
            },
            "comment_fields": {
                field: None for field in COMMENT_FIELDS
            },
            "user_insight_metrics": {
                metric: None for metric in USER_INSIGHT_METRICS
            },
            "media_insight_metrics": {
                metric: None for metric in MEDIA_INSIGHT_METRICS
            },
            "audience_insight_metrics": {
                metric: None for metric in AUDIENCE_INSIGHT_METRICS
            },
            "page_fields": {
                field: None for field in PAGE_FIELDS
            },
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("DONE")
    print("=" * 72)
    print(f"Saved: {OUTPUT_FILE}")
    print(f"Media collected: {len(media)}")
    print(f"Output size: {OUTPUT_FILE.stat().st_size:,} bytes")

    return result


if __name__ == "__main__":
    run()
