import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    print("ERROR: INSTAGRAM_ACCESS_TOKEN not found.")
    print("Create a .env file and add:")
    print("INSTAGRAM_ACCESS_TOKEN=your_token_here")
    sys.exit(1)


# Meta's Instagram Login API uses graph.instagram.com.
BASE_URL = "https://graph.instagram.com"

# Do not hard-code an old version unless you specifically need one.
# If Meta's dashboard gives you a required version, put it here.
API_VERSION = os.getenv("INSTAGRAM_API_VERSION", "")

if API_VERSION:
    API_BASE = f"{BASE_URL}/{API_VERSION}"
else:
    API_BASE = BASE_URL


OUTPUT_FILE = Path("instagram_data.json")


# ============================================================
# HTTP HELPERS
# ============================================================

def api_get(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    if params is None:
        params = {}

    params["access_token"] = ACCESS_TOKEN

    if endpoint.startswith("http"):
        url = endpoint
    else:
        url = f"{API_BASE}/{endpoint.lstrip('/')}"

    print(f"\nGET {url}")
    
    # Never print the access token.
    safe_params = {
        key: value
        for key, value in params.items()
        if key != "access_token"
    }

    print(f"Parameters: {safe_params}")

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30,
        )

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Network error while calling Instagram API: {exc}"
        ) from exc

    print(f"HTTP Status: {response.status_code}")

    try:
        data = response.json()
    except ValueError:
        print(response.text)
        raise RuntimeError(
            "Instagram API returned a non-JSON response."
        )

    if not response.ok:
        print("\nInstagram API error:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        raise RuntimeError(
            f"Instagram API request failed with HTTP {response.status_code}"
        )

    return data


# ============================================================
# PROFILE
# ============================================================

# Broad set of profile fields relevant to BrandBridge.
#
# Meta controls which fields are actually available to your
# account/token. If a field is not supported for your current
# API setup, Meta may return an error. The collector therefore
# tries multiple groups rather than failing the entire run.

PROFILE_FIELD_GROUPS = [

    # Core identity
    [
        "id",
        "username",
        "name",
        "account_type",
    ],

    # Profile information
    [
        "biography",
        "website",
        "profile_picture_url",
    ],

    # Audience/account metrics
    [
        "followers_count",
        "follows_count",
        "media_count",
    ],

    # Additional commonly documented identifier
    [
        "ig_id",
    ],
]


def fetch_profile() -> Dict[str, Any]:

    print("\n" + "=" * 70)
    print("FETCHING INSTAGRAM PROFILE")
    print("=" * 70)

    profile: Dict[str, Any] = {}

    for fields in PROFILE_FIELD_GROUPS:

        field_string = ",".join(fields)

        try:

            result = api_get(
                "me",
                {
                    "fields": field_string,
                },
            )

            if isinstance(result, dict):
                profile.update(result)

            print("\nReturned:")
            print(
                json.dumps(
                    result,
                    indent=2,
                    ensure_ascii=False,
                )
            )

        except RuntimeError as exc:

            print(
                f"\nCould not fetch field group "
                f"{fields}: {exc}"
            )

    return profile


# ============================================================
# MEDIA
# ============================================================

MEDIA_FIELD_GROUPS = [

    # Core media
    [
        "id",
        "caption",
        "media_type",
        "media_product_type",
        "timestamp",
        "permalink",
    ],

    # Media URLs
    [
        "media_url",
        "thumbnail_url",
    ],

    # Performance
    [
        "like_count",
        "comments_count",
        "view_count",
    ],

    # Other useful metadata
    [
        "username",
        "shortcode",
    ],

    # Reels / feed information
    [
        "is_shared_to_feed",
    ],

    # Comment state
    [
        "is_comment_enabled",
    ],

    # Accessibility / other metadata where available
    [
        "alt_text",
    ],
]


def fetch_media_page(
    limit: int = 25,
    after: Optional[str] = None,
) -> Dict[str, Any]:

    fields = ",".join(
        [
            field
            for group in MEDIA_FIELD_GROUPS
            for field in group
        ]
    )

    params: Dict[str, Any] = {
        "fields": fields,
        "limit": limit,
    }

    if after:
        params["after"] = after

    try:

        return api_get(
            "me/media",
            params,
        )

    except RuntimeError:

        # Some fields may not be supported by the current
        # account/API version. Try progressively smaller
        # groups so we still collect useful data.

        print(
            "\nBroad media field request failed."
        )

        collected_fields = []

        media_response = None

        for group in MEDIA_FIELD_GROUPS:

            test_fields = collected_fields + group

            try:

                response = api_get(
                    "me/media",
                    {
                        "fields": ",".join(test_fields),
                        "limit": limit,
                        **(
                            {"after": after}
                            if after
                            else {}
                        ),
                    },
                )

                collected_fields = test_fields
                media_response = response

            except RuntimeError as exc:

                print(
                    f"Skipping unsupported field group "
                    f"{group}: {exc}"
                )

        if media_response is None:

            raise RuntimeError(
                "Could not retrieve Instagram media."
            )

        return media_response


def fetch_all_media(
    max_items: int = 100,
) -> List[Dict[str, Any]]:

    print("\n" + "=" * 70)
    print("FETCHING INSTAGRAM MEDIA")
    print("=" * 70)

    all_media: List[Dict[str, Any]] = []

    after: Optional[str] = None

    while len(all_media) < max_items:

        remaining = max_items - len(all_media)

        limit = min(
            25,
            remaining,
        )

        response = fetch_media_page(
            limit=limit,
            after=after,
        )

        page_data = response.get(
            "data",
            [],
        )

        if not isinstance(page_data, list):
            break

        all_media.extend(page_data)

        print(
            f"Retrieved {len(page_data)} media items "
            f"(total: {len(all_media)})"
        )

        paging = response.get(
            "paging",
            {},
        )

        cursors = paging.get(
            "cursors",
            {},
        )

        after = cursors.get("after")

        next_url = paging.get("next")

        if not after and not next_url:
            break

        if not page_data:
            break

        # Small delay to avoid hammering the API.
        time.sleep(0.2)

    return all_media[:max_items]


# ============================================================
# CAROUSEL CHILDREN
# ============================================================

CHILD_FIELDS = [
    "id",
    "media_type",
    "media_url",
    "thumbnail_url",
]


def fetch_carousel_children(
    media_id: str,
) -> List[Dict[str, Any]]:

    try:

        response = api_get(
            f"{media_id}/children",
            {
                "fields": ",".join(
                    CHILD_FIELDS
                ),
            },
        )

        return response.get(
            "data",
            [],
        )

    except RuntimeError as exc:

        print(
            f"Could not fetch carousel children "
            f"for {media_id}: {exc}"
        )

        return []


def enrich_carousels(
    media: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    print("\n" + "=" * 70)
    print("CHECKING CAROUSEL MEDIA")
    print("=" * 70)

    for item in media:

        if item.get("media_type") != "CAROUSEL_ALBUM":
            continue

        media_id = item.get("id")

        if not media_id:
            continue

        print(
            f"Fetching children for carousel {media_id}"
        )

        children = fetch_carousel_children(
            media_id
        )

        item["children"] = children

    return media


# ============================================================
# TOKEN DEBUGGING
# ============================================================

def validate_token() -> Dict[str, Any]:

    print("\n" + "=" * 70)
    print("VALIDATING ACCESS TOKEN")
    print("=" * 70)

    try:

        response = api_get(
            "me",
            {
                "fields": "id,username",
            },
        )

        print("\nToken is working.")
        print(
            json.dumps(
                response,
                indent=2,
                ensure_ascii=False,
            )
        )

        return response

    except RuntimeError as exc:

        print("\nTOKEN VALIDATION FAILED.")
        print(exc)

        raise


# ============================================================
# SUMMARY
# ============================================================

def build_summary(
    profile: Dict[str, Any],
    media: List[Dict[str, Any]],
) -> Dict[str, Any]:

    media_types: Dict[str, int] = {}

    products: Dict[str, int] = {}

    total_likes = 0
    total_comments = 0
    total_views = 0

    videos_with_views = 0

    for item in media:

        media_type = item.get(
            "media_type",
            "UNKNOWN",
        )

        media_types[media_type] = (
            media_types.get(media_type, 0) + 1
        )

        product_type = item.get(
            "media_product_type",
            "UNKNOWN",
        )

        products[product_type] = (
            products.get(product_type, 0) + 1
        )

        likes = item.get(
            "like_count"
        )

        comments = item.get(
            "comments_count"
        )

        views = item.get(
            "view_count"
        )

        if isinstance(likes, int):
            total_likes += likes

        if isinstance(comments, int):
            total_comments += comments

        if isinstance(views, int):
            total_views += views
            videos_with_views += 1

    return {
        "profile": {
            "id": profile.get("id"),
            "username": profile.get("username"),
            "name": profile.get("name"),
            "account_type": profile.get("account_type"),
            "followers_count": profile.get(
                "followers_count"
            ),
            "follows_count": profile.get(
                "follows_count"
            ),
            "media_count": profile.get(
                "media_count"
            ),
        },
        "collection": {
            "media_collected": len(media),
            "media_types": media_types,
            "media_product_types": products,
            "total_likes_in_sample": total_likes,
            "total_comments_in_sample": total_comments,
            "total_views_in_sample": total_views,
            "media_with_view_count": videos_with_views,
        },
        "collected_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }


# ============================================================
# SAVE JSON
# ============================================================

def save_json(
    data: Dict[str, Any],
    filename: Path = OUTPUT_FILE,
) -> None:

    with filename.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"\nJSON saved to: {filename.resolve()}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("BRANDBRIDGE AI - INSTAGRAM DATA COLLECTOR")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Validate token
    # --------------------------------------------------------

    validate_token()

    # --------------------------------------------------------
    # 2. Get profile
    # --------------------------------------------------------

    profile = fetch_profile()

    # --------------------------------------------------------
    # 3. Get media
    # --------------------------------------------------------

    media = fetch_all_media(
        max_items=100
    )

    # --------------------------------------------------------
    # 4. Get carousel children
    # --------------------------------------------------------

    media = enrich_carousels(
        media
    )

    # --------------------------------------------------------
    # 5. Build summary
    # --------------------------------------------------------

    summary = build_summary(
        profile,
        media,
    )

    # --------------------------------------------------------
    # 6. Final JSON object
    # --------------------------------------------------------

    output = {
        "source": "Instagram Graph API",
        "api_setup": "Instagram Login",
        "collector": "BrandBridge AI",
        "collected_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "profile": profile,

        "media": media,

        "summary": summary,
    }

    # --------------------------------------------------------
    # 7. Save
    # --------------------------------------------------------

    save_json(
        output
    )

    # --------------------------------------------------------
    # 8. Display
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL JSON")
    print("=" * 70)

    print(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        )
    )

    print("\n" + "=" * 70)
    print("COLLECTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()