from __future__ import annotations

"""
BrandBridge AI - Instagram Professional Creator ALL-FIELD EXPLORER

Exploratory collector for an Instagram Professional Creator account.
Instagram does not support fields=*, so documented/candidate fields and
endpoints are explicitly probed. Unavailable fields are kept as null/error.
The collector accepts account_type values such as MEDIA_CREATOR and does not
require the API to return exactly "CREATOR".
"""

import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "instagram"
OUTPUT_FILE = OUTPUT_DIR / "instagram_creator_all_fields.json"
DEFAULT_API_BASE = "https://graph.instagram.com"
DEFAULT_API_VERSION = "v23.0"
DEFAULT_TIMEOUT = 30

PROFILE_FIELDS = [
    "id", "username", "name", "account_type", "biography", "website",
    "profile_picture_url", "followers_count", "follows_count", "media_count",
]

MEDIA_FIELDS = [
    "id", "caption", "media_type", "media_product_type", "media_url",
    "thumbnail_url", "permalink", "timestamp", "username", "like_count",
    "comments_count", "shortcode",
]

COMMENT_FIELDS = ["id", "text", "timestamp", "username", "from"]

USER_INSIGHT_METRICS = [
    "impressions", "reach", "follower_count", "profile_views",
    "website_clicks", "email_contacts", "phone_call_clicks",
    "text_message_clicks", "get_directions_clicks",
]

MEDIA_INSIGHT_METRICS = [
    "engagement", "impressions", "reach", "saved", "video_views",
    "likes", "comments", "shares", "total_interactions",
]

DOTENV_VALUES: dict[str, str] = {}


def load_dotenv_values() -> None:
    for env_path in (PROJECT_ROOT / ".env", PROJECT_ROOT / "backend" / ".env"):
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            DOTENV_VALUES[key.strip()] = value.strip().strip('"').strip("'")


load_dotenv_values()


def get_env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name) or DOTENV_VALUES.get(name) or default


def get_int_env(name: str, default: int) -> int:
    value = get_env(name)
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default


def get_token() -> str:
    token = get_env("INSTAGRAM_CREATOR_ACCESS_TOKEN") or get_env(
        "INSTAGRAM_ACCESS_TOKEN"
    )
    if not token:
        raise RuntimeError(
            "Instagram access token is not configured. "
            "Set INSTAGRAM_CREATOR_ACCESS_TOKEN in .env."
        )
    return token


def api_base() -> str:
    return (
        get_env("INSTAGRAM_API_BASE", DEFAULT_API_BASE) or DEFAULT_API_BASE
    ).rstrip("/")


def api_version() -> str:
    return get_env("INSTAGRAM_API_VERSION", DEFAULT_API_VERSION) or DEFAULT_API_VERSION


def api_url(path: str) -> str:
    return f"{api_base()}/{api_version().strip('/')}/{path.strip('/')}"


def instagram_get(
    path: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    query = {
        key: value for key, value in (params or {}).items()
        if value is not None and value != ""
    }
    query["access_token"] = get_token()
    url = f"{api_url(path)}?{urlencode(query)}"
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "BrandBridgeAI/1.0"},
    )

    try:
        with urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
            status = response.status
            body = response.read().decode("utf-8")
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        try:
            error_payload: Any = json.loads(body)
        except json.JSONDecodeError:
            error_payload = {"raw": body}
        return {
            "ok": False, "status": error.code, "url": url, "error": error_payload
        }
    except URLError as error:
        return {
            "ok": False, "status": None, "url": url, "error": str(error)
        }

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        payload = {"raw": body}

    delay = get_int_env("INSTAGRAM_REQUEST_DELAY_MS", 100) / 1000
    if delay > 0:
        time.sleep(delay)

    return {"ok": True, "status": status, "url": url, "data": payload}


def probe_fields(
    endpoint: str,
    fields: list[str],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = instagram_get(
        endpoint, {**(extra or {}), "fields": ",".join(fields)}
    )
    if result["ok"]:
        value = result.get("data", {})
        return {
            "available": True,
            "requested_fields": fields,
            "value": value if isinstance(value, dict) else {"value": value},
            "error": None,
            "http_status": result["status"],
            "url": result["url"],
        }

    return {
        "available": False,
        "requested_fields": fields,
        "value": {field: None for field in fields},
        "error": result["error"],
        "http_status": result["status"],
        "url": result["url"],
    }


def get_profile(user_id: str | None) -> dict[str, Any]:
    return probe_fields(user_id or "me", PROFILE_FIELDS)


def get_media(user_id: str, limit: int) -> dict[str, Any]:
    result = instagram_get(
        f"{user_id}/media",
        {"fields": ",".join(MEDIA_FIELDS), "limit": min(limit, 100)},
    )
    if not result["ok"]:
        return {
            "available": False, "items": [], "error": result["error"],
            "http_status": result["status"], "url": result["url"],
            "requested_fields": MEDIA_FIELDS,
        }

    payload = result.get("data", {})
    return {
        "available": True,
        "items": payload.get("data", [])[:limit],
        "paging": payload.get("paging"),
        "error": None,
        "http_status": result["status"],
        "url": result["url"],
        "requested_fields": MEDIA_FIELDS,
    }


def get_comments(media_id: str, limit: int) -> dict[str, Any]:
    result = instagram_get(
        f"{media_id}/comments",
        {"fields": ",".join(COMMENT_FIELDS), "limit": min(limit, 100)},
    )
    if not result["ok"]:
        return {
            "available": False, "items": [], "error": result["error"],
            "http_status": result["status"], "url": result["url"],
            "requested_fields": COMMENT_FIELDS,
        }

    payload = result.get("data", {})
    return {
        "available": True,
        "items": payload.get("data", [])[:limit],
        "paging": payload.get("paging"),
        "error": None,
        "http_status": result["status"],
        "url": result["url"],
        "requested_fields": COMMENT_FIELDS,
    }


def get_insights(media_id: str, metrics: list[str]) -> dict[str, Any]:
    result = instagram_get(
        f"{media_id}/insights", {"metric": ",".join(metrics)}
    )
    if not result["ok"]:
        return {
            "available": False, "data": [], "error": result["error"],
            "requested_metrics": metrics, "http_status": result["status"],
            "url": result["url"],
        }

    payload = result.get("data", {})
    return {
        "available": True,
        "data": payload.get("data", []),
        "error": None,
        "requested_metrics": metrics,
        "http_status": result["status"],
        "url": result["url"],
    }


def get_user_insights(user_id: str) -> dict[str, Any]:
    return get_insights(user_id, USER_INSIGHT_METRICS)


def get_media_insights(media_id: str) -> dict[str, Any]:
    return get_insights(media_id, MEDIA_INSIGHT_METRICS)


def probe_extra_edges(user_id: str) -> dict[str, Any]:
    edges = {"mentioned_media": "mentioned_media", "tags": "tags"}
    output: dict[str, Any] = {}

    for name, edge in edges.items():
        result = instagram_get(
            f"{user_id}/{edge}",
            {"fields": ",".join(MEDIA_FIELDS), "limit": 25},
        )
        if result["ok"]:
            payload = result.get("data", {})
            output[name] = {
                "available": True,
                "data": payload.get("data", []),
                "paging": payload.get("paging"),
                "error": None,
                "http_status": result["status"],
                "url": result["url"],
            }
        else:
            output[name] = {
                "available": False,
                "data": [],
                "error": result["error"],
                "http_status": result["status"],
                "url": result["url"],
            }
    return output


def main() -> None:
    print("=" * 70)
    print("BRANDBRIDGE AI")
    print("INSTAGRAM PROFESSIONAL CREATOR")
    print("ALL-FIELD EXPLORER")
    print("=" * 70)

    configured_id = get_env("INSTAGRAM_USER_ID")
    print(f"API base: {api_base()}")
    print(f"API version: {api_version()}")
    print(f"Configured user ID: {configured_id or 'AUTO /me'}")

    profile = get_profile(configured_id)
    profile_value = profile.get("value", {})
    user_id = (
        profile_value.get("id") if isinstance(profile_value, dict) else None
    ) or configured_id

    if not user_id:
        raise RuntimeError(
            "Could not resolve Instagram user ID from /me. "
            "Set INSTAGRAM_USER_ID in .env."
        )

    account_type = (
        profile_value.get("account_type")
        if isinstance(profile_value, dict)
        else None
    )

    print("ACCOUNT VERIFICATION")
    print(f"Username: {profile_value.get('username')}")
    print(f"Account type returned by API: {account_type}")

    if account_type not in {
        "CREATOR", "MEDIA_CREATOR", "BUSINESS", "MEDIA_BUSINESS"
    }:
        print("WARNING: Unknown account type; preserving API value and continuing.")

    max_media = get_int_env("INSTAGRAM_MAX_MEDIA", 50)
    max_comments = get_int_env("INSTAGRAM_MAX_COMMENTS_PER_MEDIA", 25)

    media = get_media(user_id, max_media)
    media_records: list[dict[str, Any]] = []

    for index, item in enumerate(media["items"], start=1):
        media_id = item.get("id")
        record = {
            "media": item,
            "comments": None,
            "insights": None,
            "field_probe": None,
        }
        if media_id:
            print(f"Media {index}: {media_id}")
            record["field_probe"] = probe_fields(media_id, MEDIA_FIELDS)
            record["comments"] = get_comments(media_id, max_comments)
            record["insights"] = get_media_insights(media_id)
        media_records.append(record)

    user_insights = get_user_insights(user_id)
    extra_edges = probe_extra_edges(user_id)

    dataset = {
        "metadata": {
            "project": "BrandBridge AI",
            "collector": "instagram_creator_all_fields.py",
            "source": "Instagram API",
            "api_base": api_base(),
            "api_version": api_version(),
            "account_type_returned": account_type,
            "notes": [
                "Instagram API does not provide fields=*.",
                "Candidate fields/endpoints are explicitly probed.",
                "Unavailable fields are preserved with null/error information.",
                "No synthetic media records are created.",
                "Insights depend on account, permissions, API version, and metrics.",
            ],
        },
        "profile": profile,
        "user_insights": user_insights,
        "media": media_records,
        "media_collection": {
            "available": media["available"],
            "count": len(media_records),
            "requested_fields": MEDIA_FIELDS,
            "error": media["error"],
        },
        "extra_edges": extra_edges,
        "collection_config": {
            "max_media": max_media,
            "max_comments_per_media": max_comments,
            "profile_fields": PROFILE_FIELDS,
            "media_fields": MEDIA_FIELDS,
            "comment_fields": COMMENT_FIELDS,
            "user_insight_metrics": USER_INSIGHT_METRICS,
            "media_insight_metrics": MEDIA_INSIGHT_METRICS,
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(dataset, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("" + "=" * 70)
    print("COLLECTION COMPLETE")
    print("=" * 70)
    print(f"Instagram user: {user_id}")
    print(f"Account type: {account_type}")
    print(f"Media collected: {len(media_records)}")
    print(f"Output: {OUTPUT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    main()
