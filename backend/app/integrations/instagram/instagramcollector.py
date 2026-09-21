import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    print("ERROR: INSTAGRAM_ACCESS_TOKEN not found")
    print("Add this to .env:")
    print("INSTAGRAM_ACCESS_TOKEN=your_token_here")
    sys.exit(1)


BASE_URL = "https://graph.instagram.com"

API_VERSION = os.getenv("INSTAGRAM_API_VERSION", "").strip()

if API_VERSION:
    API_BASE = f"{BASE_URL}/{API_VERSION}"
else:
    API_BASE = BASE_URL


# Project root:
# BrandBridge_AI/
# ├── backend/
# │   └── app/
# │       └── integrations/
# │           └── instagram/
# │               └── instagramcollector.py
# └── data/
#
# parents[4] -> BrandBridge_AI
PROJECT_ROOT = Path(__file__).resolve().parents[4]

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "instagram"

OUTPUT_FILE = OUTPUT_DIR / "instagram_business_data.json"

MAX_MEDIA_ITEMS = int(os.getenv("INSTAGRAM_MAX_MEDIA_ITEMS", "100"))


# ============================================================
# DOCUMENTED / KNOWN PROFILE FIELDS
# ============================================================
#
# We test each field separately.
#
# This is intentional:
# If Meta rejects one field, the other fields can still
# be collected.
# ============================================================

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


# ============================================================
# DOCUMENTED / KNOWN MEDIA FIELDS
# ============================================================

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


# ============================================================
# CAROUSEL CHILD FIELDS
# ============================================================

CAROUSEL_CHILD_FIELDS = [
    "id",
    "media_type",
    "media_url",
    "thumbnail_url",
]


# ============================================================
# HTTP REQUEST
# ============================================================


def api_get(
    endpoint: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:

    if params is None:
        params = {}

    params = dict(params)

    params["access_token"] = ACCESS_TOKEN

    if endpoint.startswith("http"):
        url = endpoint
    else:
        url = f"{API_BASE}/{endpoint.lstrip('/')}"

    safe_params = {key: value for key, value in params.items() if key != "access_token"}

    print(f"\nGET {url}")
    print(f"Parameters: {safe_params}")

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30,
        )

    except requests.RequestException as exc:
        raise RuntimeError(f"Network error: {exc}") from exc

    print(f"HTTP Status: {response.status_code}")

    try:
        data = response.json()

    except ValueError:
        raise RuntimeError("Instagram API returned non-JSON response.")from None

    if not response.ok:
        print(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            )
        )

        raise RuntimeError(f"Instagram API request failed with HTTP {response.status_code}")

    return data


# ============================================================
# FIELD PROBE
# ============================================================
#
# This is the important part.
#
# We ask Meta for ONE field at a time.
#
# If available:
#     value is stored
#
# If unavailable:
#     null is stored
# ============================================================


def probe_field(
    endpoint: str,
    field: str,
) -> dict[str, Any]:

    try:
        response = api_get(
            endpoint,
            {
                "fields": field,
            },
        )

        if field in response:
            return {
                "field": field,
                "available": True,
                "value": response.get(field),
                "error": None,
            }

        return {
            "field": field,
            "available": False,
            "value": None,
            "error": "Field not returned",
        }

    except RuntimeError as exc:
        return {
            "field": field,
            "available": False,
            "value": None,
            "error": str(exc),
        }


# ============================================================
# PROFILE
# ============================================================


def fetch_profile() -> dict[str, Any]:

    print("\n" + "=" * 70)
    print("PROBING ALL PROFILE FIELDS")
    print("=" * 70)

    profile = {}

    field_status = {}

    for field in PROFILE_FIELDS:
        print(f"\nTesting profile field: {field}")

        result = probe_field(
            "me",
            field,
        )

        profile[field] = result["value"]

        field_status[field] = {
            "available": result["available"],
            "error": result["error"],
        }

    return {
        "data": profile,
        "field_status": field_status,
    }


# ============================================================
# MEDIA SCHEMA
# ============================================================
#
# This gives you the complete expected structure even when
# the account currently has ZERO media.
# ============================================================


def empty_media_record() -> dict[str, Any]:

    return {field: None for field in MEDIA_FIELDS}


# ============================================================
# FETCH MEDIA
# ============================================================


def fetch_media() -> dict[str, Any]:

    print("\n" + "=" * 70)
    print("FETCHING INSTAGRAM MEDIA")
    print("=" * 70)

    all_media = []

    after = None

    available_fields = {field: None for field in MEDIA_FIELDS}

    field_status = {
        field: {
            "available": None,
            "error": None,
        }
        for field in MEDIA_FIELDS
    }

    # --------------------------------------------------------
    # First determine which media fields are accepted.
    #
    # This is done against /me/media.
    # --------------------------------------------------------

    print("\nTesting media fields...")

    for field in MEDIA_FIELDS:
        print(f"\nTesting media field: {field}")

        try:
            params = {
                "fields": field,
                "limit": 1,
            }

            if after:
                params["after"] = after

            response = api_get(
                "me/media",
                params,
            )

            field_status[field] = {
                "available": True,
                "error": None,
            }

            available_fields[field] = True

        except RuntimeError as exc:
            field_status[field] = {
                "available": False,
                "error": str(exc),
            }

            available_fields[field] = False

    # --------------------------------------------------------
    # Build list of fields that Meta accepted
    # --------------------------------------------------------

    supported_fields = [field for field in MEDIA_FIELDS if available_fields[field] is True]

    print("\n" + "-" * 70)
    print("SUPPORTED MEDIA FIELDS")
    print("-" * 70)

    for field in supported_fields:
        print(f"  [AVAILABLE] {field}")

    print("\n" + "-" * 70)
    print("UNAVAILABLE MEDIA FIELDS")
    print("-" * 70)

    for field in MEDIA_FIELDS:
        if available_fields[field] is False:
            print(f"  [NULL] {field}")

    # --------------------------------------------------------
    # No supported fields
    # --------------------------------------------------------

    if not supported_fields:
        return {
            "data": [],
            "schema": empty_media_record(),
            "field_status": field_status,
        }

    # --------------------------------------------------------
    # Fetch actual media using all supported fields
    # --------------------------------------------------------

    fields_string = ",".join(supported_fields)

    after = None

    while len(all_media) < MAX_MEDIA_ITEMS:
        remaining = MAX_MEDIA_ITEMS - len(all_media)

        limit = min(
            25,
            remaining,
        )

        params = {
            "fields": fields_string,
            "limit": limit,
        }

        if after:
            params["after"] = after

        try:
            response = api_get(
                "me/media",
                params,
            )

        except RuntimeError as exc:
            print("\nCould not fetch media:")
            print(exc)

            break

        page_data = response.get(
            "data",
            [],
        )

        if not isinstance(
            page_data,
            list,
        ):
            break

        for item in page_data:
            normalized = {}

            for field in MEDIA_FIELDS:
                normalized[field] = item.get(field)

            all_media.append(normalized)

        print(f"Retrieved {len(page_data)} media items (total: {len(all_media)})")

        paging = response.get(
            "paging",
            {},
        )

        cursors = paging.get(
            "cursors",
            {},
        )

        after = cursors.get("after")

        if not after:
            break

        time.sleep(0.2)

    return {
        "data": all_media[:MAX_MEDIA_ITEMS],
        "schema": empty_media_record(),
        "field_status": field_status,
    }


# ============================================================
# CAROUSEL CHILDREN
# ============================================================


def fetch_carousel_children(
    media_id: str,
) -> list[dict[str, Any]]:

    supported_fields = []

    for field in CAROUSEL_CHILD_FIELDS:
        try:
            api_get(
                f"{media_id}/children",
                {
                    "fields": field,
                },
            )

            supported_fields.append(field)

        except RuntimeError:
            pass

    if not supported_fields:
        return []

    fields_string = ",".join(supported_fields)

    try:
        response = api_get(
            f"{media_id}/children",
            {
                "fields": fields_string,
            },
        )

        children = response.get(
            "data",
            [],
        )

        normalized_children = []

        for child in children:
            normalized = {}

            for field in CAROUSEL_CHILD_FIELDS:
                normalized[field] = child.get(field)

            normalized_children.append(normalized)

        return normalized_children

    except RuntimeError:
        return []


def enrich_carousels(
    media: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    for item in media:
        if item.get("media_type") != "CAROUSEL_ALBUM":
            continue

        media_id = item.get("id")

        if not media_id:
            continue

        item["children"] = fetch_carousel_children(media_id)

    return media


# ============================================================
# TOKEN VALIDATION
# ============================================================


def validate_token():

    print("\n" + "=" * 70)
    print("VALIDATING ACCESS TOKEN")
    print("=" * 70)

    response = api_get(
        "me",
        {
            "fields": "id,username",
        },
    )

    print("\nToken is working.")

    return response


# ============================================================
# SUMMARY
# ============================================================


def build_summary(
    profile: dict[str, Any],
    media: list[dict[str, Any]],
) -> dict[str, Any]:

    media_types = {}
    product_types = {}

    total_likes = 0
    total_comments = 0
    total_views = 0

    for item in media:
        media_type = item.get("media_type")

        if media_type:
            media_types[media_type] = (
                media_types.get(
                    media_type,
                    0,
                )
                + 1
            )

        product_type = item.get("media_product_type")

        if product_type:
            product_types[product_type] = (
                product_types.get(
                    product_type,
                    0,
                )
                + 1
            )

        likes = item.get("like_count")

        comments = item.get("comments_count")

        views = item.get("view_count")

        if isinstance(
            likes,
            int,
        ):
            total_likes += likes

        if isinstance(
            comments,
            int,
        ):
            total_comments += comments

        if isinstance(
            views,
            int,
        ):
            total_views += views

    return {
        "media_collected": len(media),
        "media_types": media_types,
        "media_product_types": product_types,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_views": total_views,
    }


# ============================================================
# SAVE JSON
# ============================================================


def save_json(
    data: dict[str, Any],
) -> None:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("\nJSON saved to:")

    print(OUTPUT_FILE.resolve())


# ============================================================
# MAIN
# ============================================================


def main():

    print("\n")
    print("=" * 70)
    print("BRANDBRIDGE AI - INSTAGRAM BUSINESS FIELD EXPLORER")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Validate token
    # --------------------------------------------------------

    token_validation = validate_token()

    # --------------------------------------------------------
    # 2. Profile
    # --------------------------------------------------------

    profile_result = fetch_profile()

    profile = profile_result["data"]

    # --------------------------------------------------------
    # 3. Media
    # --------------------------------------------------------

    media_result = fetch_media()

    media = media_result["data"]

    # --------------------------------------------------------
    # 4. Carousel children
    # --------------------------------------------------------

    media = enrich_carousels(media)

    # --------------------------------------------------------
    # 5. Summary
    # --------------------------------------------------------

    summary = build_summary(
        profile,
        media,
    )

    # --------------------------------------------------------
    # 6. Final output
    # --------------------------------------------------------

    output = {
        "source": "Instagram Graph API",
        "api_setup": "Instagram Login",
        "account_type": "BUSINESS",
        "collector": "BrandBridge AI",
        "collected_at": datetime.now(UTC).isoformat(),
        "token_validation": token_validation,
        "profile": profile,
        "profile_field_status": profile_result["field_status"],
        "media": media,
        "media_schema": media_result["schema"],
        "media_field_status": media_result["field_status"],
        "summary": summary,
    }

    # --------------------------------------------------------
    # 7. Save
    # --------------------------------------------------------

    save_json(output)

    # --------------------------------------------------------
    # 8. Console summary
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("COLLECTION COMPLETE")
    print("=" * 70)

    print(f"\nProfile fields tested: {len(PROFILE_FIELDS)}")

    print(f"Media fields tested: {len(MEDIA_FIELDS)}")

    print(f"Media records collected: {len(media)}")

    print(f"\nOutput:\n{OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
