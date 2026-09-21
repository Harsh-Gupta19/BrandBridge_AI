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
# BRAND BRIDGE AI
# INSTAGRAM CREATOR ACCOUNT DATA COLLECTOR
# ============================================================

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://graph.instagram.com"

ACCESS_TOKEN = os.getenv("INSTAGRAM_CREATOR_ACCESS_TOKEN")

OUTPUT_DIR = Path("output")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "instagram_creator_data.json"

MAX_MEDIA = 100


# ============================================================
# VALIDATE CONFIGURATION
# ============================================================

if not ACCESS_TOKEN:
    print("\nERROR: INSTAGRAM_CREATOR_ACCESS_TOKEN was not found.")

    print("\nCreate a .env file containing:")

    print("INSTAGRAM_CREATOR_ACCESS_TOKEN=your_token_here")

    sys.exit(1)


# ============================================================
# API REQUEST HELPER
# ============================================================


def api_get(
    endpoint: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:

    if params is None:
        params = {}

    params = params.copy()

    params["access_token"] = ACCESS_TOKEN

    if endpoint.startswith("http"):
        url = endpoint

    else:
        url = f"{BASE_URL}/{endpoint.lstrip('/')}"

    # --------------------------------------------------------
    # NEVER PRINT ACCESS TOKEN
    # --------------------------------------------------------

    safe_params = {key: value for key, value in params.items() if key != "access_token"}

    print("\n" + "-" * 70)
    print(f"GET {url}")
    print("Parameters:", safe_params)

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

    except ValueError as exc:
        print("\nRaw response:")

        print(response.text)

        raise RuntimeError("Instagram API returned a non-JSON response.") from exc

    if not response.ok:
        print("\nInstagram API ERROR:")

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
# 1. GET CREATOR PROFILE
# ============================================================

PROFILE_FIELDS = [
    "id",
    "username",
    "name",
    "account_type",
    "biography",
    "website",
    "profile_picture_url",
    "followers_count",
    "follows_count",
    "media_count",
]


def fetch_creator_profile() -> dict[str, Any]:

    print("\n")
    print("=" * 70)
    print("1. FETCHING CREATOR PROFILE")
    print("=" * 70)

    fields = ",".join(PROFILE_FIELDS)

    response = api_get("me", {"fields": fields})

    print("\nCreator profile:")
    print(
        json.dumps(
            response,
            indent=2,
            ensure_ascii=False,
        )
    )

    return response


# ============================================================
# 2. GET CREATOR MEDIA
# ============================================================

MEDIA_FIELDS = [
    "id",
    "caption",
    "media_type",
    "media_product_type",
    "timestamp",
    "permalink",
    "media_url",
    "thumbnail_url",
    "like_count",
    "comments_count",
    "view_count",
    "username",
]


def fetch_media_page(
    limit: int = 25,
    after: str | None = None,
) -> dict[str, Any]:

    params: dict[str, Any] = {
        "fields": ",".join(MEDIA_FIELDS),
        "limit": limit,
    }

    if after:
        params["after"] = after

    return api_get("me/media", params)


def fetch_all_media(
    max_items: int = 100,
) -> list[dict[str, Any]]:

    print("\n")
    print("=" * 70)
    print("2. FETCHING CREATOR MEDIA")
    print("=" * 70)

    all_media: list[dict[str, Any]] = []

    after: str | None = None

    while len(all_media) < max_items:
        remaining = max_items - len(all_media)

        limit = min(25, remaining)

        response = fetch_media_page(
            limit=limit,
            after=after,
        )

        page = response.get("data", [])

        if not page:
            print("\nNo more media returned.")

            break

        all_media.extend(page)

        print(f"Retrieved {len(page)} media items")

        print(f"Total collected: {len(all_media)}")

        paging = response.get("paging", {})

        cursors = paging.get("cursors", {})

        after = cursors.get("after")

        if not after:
            print("\nPagination complete.")

            break

        # Small pause between requests
        time.sleep(0.2)

    return all_media[:max_items]


# ============================================================
# 3. CAROUSEL CHILDREN
# ============================================================

CAROUSEL_CHILD_FIELDS = [
    "id",
    "media_type",
    "media_url",
    "thumbnail_url",
]


def fetch_carousel_children(
    media_id: str,
) -> list[dict[str, Any]]:

    try:
        response = api_get(f"{media_id}/children", {"fields": ",".join(CAROUSEL_CHILD_FIELDS)})

        return response.get("data", [])

    except RuntimeError as exc:
        print(f"\nCould not retrieve carousel children for {media_id}")

        print(exc)

        return []


def enrich_carousels(
    media: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    print("\n")
    print("=" * 70)
    print("3. PROCESSING CAROUSEL MEDIA")
    print("=" * 70)

    carousel_count = 0

    for item in media:
        if item.get("media_type") != "CAROUSEL_ALBUM":
            continue

        media_id = item.get("id")

        if not media_id:
            continue

        carousel_count += 1

        print(f"\nCarousel {carousel_count}: {media_id}")

        children = fetch_carousel_children(media_id)

        item["children"] = children

    print(f"\nTotal carousels processed: {carousel_count}")

    return media


# ============================================================
# 4. CALCULATE SUMMARY
# ============================================================


def calculate_summary(
    profile: dict[str, Any],
    media: list[dict[str, Any]],
) -> dict[str, Any]:

    print("\n")
    print("=" * 70)
    print("4. CALCULATING SUMMARY")
    print("=" * 70)

    media_types: dict[str, int] = {}

    product_types: dict[str, int] = {}

    total_likes = 0

    total_comments = 0

    total_views = 0

    media_with_likes = 0

    media_with_comments = 0

    media_with_views = 0

    for item in media:
        # ----------------------------------------------------
        # Media type
        # ----------------------------------------------------

        media_type = item.get("media_type", "UNKNOWN")

        media_types[media_type] = media_types.get(media_type, 0) + 1

        # ----------------------------------------------------
        # Product type
        # ----------------------------------------------------

        product_type = item.get("media_product_type", "UNKNOWN")

        product_types[product_type] = product_types.get(product_type, 0) + 1

        # ----------------------------------------------------
        # Likes
        # ----------------------------------------------------

        likes = item.get("like_count")

        if isinstance(likes, (int, float)):
            total_likes += likes

            media_with_likes += 1

        # ----------------------------------------------------
        # Comments
        # ----------------------------------------------------

        comments = item.get("comments_count")

        if isinstance(comments, (int, float)):
            total_comments += comments

            media_with_comments += 1

        # ----------------------------------------------------
        # Views
        # ----------------------------------------------------

        views = item.get("view_count")

        if isinstance(views, (int, float)):
            total_views += views

            media_with_views += 1

    # --------------------------------------------------------
    # Averages
    # --------------------------------------------------------

    average_likes = total_likes / media_with_likes if media_with_likes else 0

    average_comments = total_comments / media_with_comments if media_with_comments else 0

    average_views = total_views / media_with_views if media_with_views else 0

    summary = {
        "profile": {
            "instagram_user_id": profile.get("id"),
            "username": profile.get("username"),
            "name": profile.get("name"),
            "account_type": profile.get("account_type"),
            "followers_count": profile.get("followers_count"),
            "follows_count": profile.get("follows_count"),
            "media_count": profile.get("media_count"),
        },
        "collection": {
            "media_collected": len(media),
            "media_types": media_types,
            "media_product_types": product_types,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_views": total_views,
            "average_likes": round(average_likes, 2),
            "average_comments": round(average_comments, 2),
            "average_views": round(average_views, 2),
            "media_with_likes": media_with_likes,
            "media_with_comments": media_with_comments,
            "media_with_views": media_with_views,
        },
    }

    return summary


# ============================================================
# 5. BUILD FINAL DATASET
# ============================================================


def build_dataset(
    profile: dict[str, Any],
    media: list[dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, Any]:

    return {
        "project": "BrandBridge AI",
        "collector": "Instagram Creator Data Collector",
        "source": "Instagram Graph API",
        "authentication": "Instagram Login",
        "account_type": "Professional Creator",
        "collected_at": datetime.now(UTC).isoformat(),
        "profile": profile,
        "media": media,
        "summary": summary,
    }


# ============================================================
# 6. SAVE JSON
# ============================================================


def save_dataset(
    dataset: dict[str, Any],
) -> None:

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            dataset,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("\n")
    print("=" * 70)
    print("5. DATA SAVED")
    print("=" * 70)

    print(f"\nFile:\n{OUTPUT_FILE.resolve()}")


# ============================================================
# 7. MAIN
# ============================================================


def main():

    print("\n")
    print("#" * 70)
    print("BRANDBRIDGE AI")
    print("INSTAGRAM PROFESSIONAL CREATOR COLLECTOR")
    print("#" * 70)

    # --------------------------------------------------------
    # STEP 1
    # --------------------------------------------------------

    profile = fetch_creator_profile()

    # --------------------------------------------------------
    # Verify account type
    # --------------------------------------------------------

    account_type = profile.get("account_type")

    username = profile.get("username")

    print("\n")
    print("=" * 70)
    print("ACCOUNT VERIFICATION")
    print("=" * 70)

    print(f"\nUsername: {username}")

    print(f"Account type returned by API: {account_type}")

    if account_type != "CREATOR":
        print("\nWARNING:")

        print("The API did not return 'CREATOR' as the account type.")

        print(
            "The collector will stop so that "
            "we do not accidentally mix "
            "the Business account dataset."
        )

        return

    print("\nConfirmed: Professional Creator account.")

    # --------------------------------------------------------
    # STEP 2
    # --------------------------------------------------------

    media = fetch_all_media(max_items=MAX_MEDIA)

    # --------------------------------------------------------
    # STEP 3
    # --------------------------------------------------------

    media = enrich_carousels(media)

    # --------------------------------------------------------
    # STEP 4
    # --------------------------------------------------------

    summary = calculate_summary(profile, media)

    # --------------------------------------------------------
    # STEP 5
    # --------------------------------------------------------

    dataset = build_dataset(profile, media, summary)

    # --------------------------------------------------------
    # STEP 6
    # --------------------------------------------------------

    save_dataset(dataset)

    # --------------------------------------------------------
    # DISPLAY FINAL JSON
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("FINAL DATASET")
    print("=" * 70)

    print(
        json.dumps(
            dataset,
            indent=2,
            ensure_ascii=False,
        )
    )

    print("\n")
    print("=" * 70)
    print("COLLECTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
