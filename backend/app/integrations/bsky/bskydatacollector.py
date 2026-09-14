from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BSKY_API_BASE_URL = "https://public.api.bsky.app/xrpc"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "bsky"

DEFAULT_SEARCH_QUERIES = (
    "fitness India",
    "nutrition India",
    "gym India",
    "beauty India",
    "skincare India",
    "makeup India",
    "technology India",
    "smartphone India",
    "gaming India",
    "food India",
    "cooking India",
    "travel India",
    "fashion India",
    "finance India",
    "education India",
)


class BlueSkyCollectionError(RuntimeError):
    """Raised when BlueSky data collection cannot continue."""


@dataclass(frozen=True)
class BlueSkyCollectorConfig:
    output_dir: Path = DEFAULT_OUTPUT_DIR
    search_queries: tuple[str, ...] = DEFAULT_SEARCH_QUERIES
    max_creators: int = 100
    max_posts_per_creator: int = 50
    request_delay_seconds: float = 0.1
    timeout_seconds: int = 30
    include_raw_api_payloads: bool = True


def load_dotenv_values() -> dict[str, str]:
    values: dict[str, str] = {}

    for env_path in (PROJECT_ROOT / ".env", PROJECT_ROOT / "backend" / ".env"):
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, raw_value = stripped.split("=", 1)
            values[key.strip()] = raw_value.strip().strip('"').strip("'")

    return values


DOTENV_VALUES = load_dotenv_values()


def get_env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name) or DOTENV_VALUES.get(name) or default


def get_int_env(name: str, default: int) -> int:
    value = get_env(name)
    if value is None:
        return default
    return safe_int(value, default)


def get_float_env(name: str, default: float) -> float:
    value = get_env(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def get_list_env(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    value = get_env(name)
    if not value:
        return default
    if value.startswith("["):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return default
        if not isinstance(parsed, list):
            return default
        return tuple(str(item).strip() for item in parsed if str(item).strip())
    return tuple(item.strip() for item in value.split(",") if item.strip())


def safe_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_mean(values: list[int]) -> float:
    if not values:
        return 0
    return sum(values) / len(values)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output_file:
        json.dump(data, output_file, indent=2, ensure_ascii=False)


def bsky_get(
    resource: str,
    params: dict[str, str | int | None],
    config: BlueSkyCollectorConfig,
) -> dict[str, Any]:
    request_params = {
        key: value
        for key, value in params.items()
        if value is not None and value != ""
    }

    url = f"{BSKY_API_BASE_URL}/{resource}?{urlencode(request_params)}"
    request = Request(url, headers={"Accept": "application/json"})

    try:
        with urlopen(request, timeout=config.timeout_seconds) as response:
            payload = response.read().decode("utf-8")
    except HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        raise BlueSkyCollectionError(
            f"BlueSky API request failed with HTTP {error.code}: {error_body}"
        ) from error
    except URLError as error:
        raise BlueSkyCollectionError(f"BlueSky API request failed: {error}") from error

    time.sleep(config.request_delay_seconds)
    return json.loads(payload)


def search_creators(
    config: BlueSkyCollectorConfig,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    creator_lookup: dict[str, dict[str, Any]] = {}
    raw_search_pages: list[dict[str, Any]] = []

    for query in config.search_queries:
        try:
            response = bsky_get(
                "app.bsky.actor.searchActors",
                {
                    "q": query,
                    "limit": 50,
                },
                config,
            )

            raw_search_pages.append(
                {
                    "query": query,
                    "response": response,
                }
            )

            for actor in response.get("actors", []):
                did = actor.get("did")
                if not did:
                    continue

                handle = actor.get("handle")
                existing = creator_lookup.setdefault(
                    did,
                    {
                        "did": did,
                        "discovery_queries": [],
                        "search_results": [],
                    },
                )

                if query not in existing["discovery_queries"]:
                    existing["discovery_queries"].append(query)

                existing["search_results"].append(
                    {
                        "query": query,
                        "handle": handle,
                        "display_name": actor.get("displayName"),
                        "description": actor.get("description"),
                        "avatar": actor.get("avatar"),
                        "indexed_at": actor.get("indexedAt"),
                        "raw": actor if config.include_raw_api_payloads else None,
                    }
                )

                if len(creator_lookup) >= config.max_creators:
                    break

            if len(creator_lookup) >= config.max_creators:
                break

        except BlueSkyCollectionError as error:
            print(f"Warning: Failed to search for query '{query}': {error}", file=sys.stderr)
            continue

    return creator_lookup, raw_search_pages


def get_creator_profile(
    did: str,
    config: BlueSkyCollectorConfig,
) -> dict[str, Any] | None:
    try:
        response = bsky_get(
            "app.bsky.actor.getProfile",
            {
                "actor": did,
            },
            config,
        )
        return response
    except BlueSkyCollectionError as error:
        print(f"Warning: Failed to fetch profile for {did}: {error}", file=sys.stderr)
        return None


def get_creator_feed(
    did: str,
    config: BlueSkyCollectorConfig,
) -> list[dict[str, Any]]:
    posts: list[dict[str, Any]] = []
    cursor: str | None = None

    try:
        while len(posts) < config.max_posts_per_creator:
            remaining = config.max_posts_per_creator - len(posts)
            response = bsky_get(
                "app.bsky.feed.getAuthorFeed",
                {
                    "actor": did,
                    "limit": min(100, remaining),
                    "cursor": cursor,
                },
                config,
            )

            items = response.get("feed", [])
            if not items:
                break

            posts.extend(items)
            cursor = response.get("cursor")
            if not cursor:
                break

    except BlueSkyCollectionError as error:
        print(f"Warning: Failed to fetch feed for {did}: {error}", file=sys.stderr)

    return posts[: config.max_posts_per_creator]


def normalize_post(
    post_item: dict[str, Any],
    creator_handle: str | None,
    include_raw: bool,
) -> dict[str, Any]:
    record = post_item.get("post", {})
    post_data = record.get("record", {})
    reply_ref = post_data.get("reply", {})
    embed_data = post_data.get("embed", {})
    author = record.get("author", {})

    likes_count = record.get("likeCount", 0)
    replies_count = record.get("replyCount", 0)
    reposts_count = record.get("repostCount", 0)
    quotes_count = record.get("quoteCount", 0)

    engagement_count = likes_count + replies_count + reposts_count + quotes_count

    return {
        "post_uri": record.get("uri"),
        "post_cid": record.get("cid"),
        "did": author.get("did"),
        "creator_handle": creator_handle,
        "created_at": post_data.get("createdAt"),
        "text": post_data.get("text"),
        "facets": post_data.get("facets", []),
        "reply_ref": reply_ref if reply_ref else None,
        "embed": embed_data if embed_data else None,
        "langs": post_data.get("langs", []),
        "likes": likes_count,
        "replies": replies_count,
        "reposts": reposts_count,
        "quotes": quotes_count,
        "total_engagement": engagement_count,
        "engagement_rate": (
            round((engagement_count / 1.0), 2) if engagement_count > 0 else 0
        ),
        "reply": post_item.get("reply", {}),
        "reason": post_item.get("reason"),
        "raw": record if include_raw else None,
    }


def extract_top_words(posts: list[dict[str, Any]], limit: int = 25) -> list[str]:
    counter: Counter[str] = Counter()
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "is", "are", "was", "were"}

    for post in posts:
        text = post.get("text", "").lower()
        words = text.split()
        for word in words:
            # Clean word: remove punctuation and strip
            cleaned = word.strip(".,!?;:()[]{}\"'").lower()
            if cleaned and len(cleaned) > 2 and cleaned not in stop_words:
                counter[cleaned] += 1

    return [word for word, _count in counter.most_common(limit)]


def derive_creator_categories(
    discovery_queries: list[str],
    top_words: list[str],
    limit: int = 15,
) -> list[str]:
    ignored_words = {"india", "indian", "creator", "account", "bsky", "bluesky"}
    categories: list[str] = []

    for query in discovery_queries:
        for word in query.lower().replace("/", " ").split():
            if word not in ignored_words and word not in categories:
                categories.append(word)

    for word in top_words:
        if word not in ignored_words and word not in categories:
            categories.append(word)

    return categories[:limit]


def calculate_creator_metrics(posts: list[dict[str, Any]]) -> dict[str, Any]:
    likes = [safe_int(post.get("likes")) for post in posts]
    replies = [safe_int(post.get("replies")) for post in posts]
    reposts = [safe_int(post.get("reposts")) for post in posts]
    quotes = [safe_int(post.get("quotes")) for post in posts]
    engagements = [post.get("total_engagement", 0) for post in posts]

    valid_engagements = [value for value in engagements if value > 0]
    average_engagement = safe_mean(valid_engagements)

    return {
        "posts_analyzed": len(posts),
        "average_likes": round(safe_mean(likes), 2),
        "average_replies": round(safe_mean(replies), 2),
        "average_reposts": round(safe_mean(reposts), 2),
        "average_quotes": round(safe_mean(quotes), 2),
        "average_engagement": round(average_engagement, 2),
        "total_likes": sum(likes),
        "total_replies": sum(replies),
        "total_reposts": sum(reposts),
        "total_quotes": sum(quotes),
        "total_engagement": sum(engagements),
    }


def build_creator_record(
    profile: dict[str, Any],
    discovery: dict[str, Any],
    posts: list[dict[str, Any]],
    include_raw: bool,
) -> dict[str, Any]:
    did = profile.get("did")
    handle = profile.get("handle")
    creator_url = f"https://bsky.app/profile/{handle}"

    metrics = calculate_creator_metrics(posts)
    followers_count = safe_int(profile.get("followersCount"))
    follows_count = safe_int(profile.get("followsCount"))
    posts_count = safe_int(profile.get("postsCount"))

    average_engagement = metrics["average_engagement"]
    engagement_per_follower = (
        round(average_engagement / followers_count, 4) if followers_count > 0 else 0
    )

    top_words = extract_top_words(posts)
    discovery_queries = discovery.get("discovery_queries", [])
    creator_categories = derive_creator_categories(discovery_queries, top_words)

    return {
        "creator_id": f"bsky:{did}",
        "platform": "bsky",
        "profile": {
            "did": did,
            "handle": handle,
            "display_name": profile.get("displayName"),
            "description": profile.get("description"),
            "avatar": profile.get("avatar"),
            "banner": profile.get("banner"),
            "creator_url": creator_url,
            "created_at": profile.get("createdAt"),
            "indexed_at": profile.get("indexedAt"),
        },
        "public_statistics": {
            "followers_count": followers_count,
            "follows_count": follows_count,
            "posts_count": posts_count,
            "follower_to_following_ratio": (
                round(followers_count / follows_count, 2) if follows_count > 0 else 0
            ),
        },
        "viewer_state": {
            "muted": profile.get("viewer", {}).get("muted", False),
            "blocked_by": profile.get("viewer", {}).get("blockedBy", False),
        },
        "discovery": {
            "queries": discovery_queries,
            "search_results": discovery.get("search_results", []),
        },
        "recent_post_metrics": {
            **metrics,
            "engagement_per_follower": engagement_per_follower,
            "top_words": top_words,
        },
        "brandbridge_fields": {
            "creator_categories": creator_categories,
            "platforms": {
                "bsky": {
                    "did": did,
                    "handle": handle,
                    "creator_url": creator_url,
                    "followers": followers_count,
                    "average_engagement": average_engagement,
                    "average_engagement_per_follower": engagement_per_follower,
                }
            },
            "audience": {
                "follower_count": followers_count,
                "estimated_reach": followers_count,
                "missing_reason": (
                    "Detailed audience demographics are not available from BlueSky public API."
                ),
            },
            "collaboration": {
                "rate_card": None,
                "business_email": None,
                "preferred_content_formats": None,
                "missing_reason": (
                    "Rate card and contact details are not available from BlueSky public API. "
                    "Manual creator input required."
                ),
            },
            "matching_features": {
                "category_similarity_inputs": creator_categories,
                "platform_match_input": "bsky",
                "engagement_per_follower": engagement_per_follower,
                "follower_score_input": followers_count,
                "semantic_similarity_text": " ".join(
                    value
                    for value in [
                        profile.get("displayName"),
                        profile.get("description"),
                        " ".join(top_words[:10]),
                    ]
                    if value
                ),
            },
        },
        "recent_posts": posts,
        "raw": profile if include_raw else None,
    }


def collect_bsky_creator_data(config: BlueSkyCollectorConfig) -> dict[str, Any]:
    started_at = datetime.now(timezone.utc)
    creator_lookup, raw_search_pages = search_creators(config)

    creators: list[dict[str, Any]] = []
    posts: list[dict[str, Any]] = []

    for did, discovery in creator_lookup.items():
        profile = get_creator_profile(did, config)
        if not profile:
            continue

        creator_posts = get_creator_feed(did, config)

        normalized_posts = [
            normalize_post(item, profile.get("handle"), config.include_raw_api_payloads)
            for item in creator_posts
        ]

        posts.extend(normalized_posts)
        creators.append(
            build_creator_record(
                profile,
                discovery,
                normalized_posts,
                config.include_raw_api_payloads,
            )
        )

    creators.sort(
        key=lambda creator: creator["public_statistics"]["followers_count"],
        reverse=True,
    )

    finished_at = datetime.now(timezone.utc)
    return {
        "metadata": {
            "project": "BrandBridge AI",
            "source": "BlueSky Public API (public.api.bsky.app/xrpc)",
            "data_classification": "public_api_data",
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "duration_seconds": round((finished_at - started_at).total_seconds(), 2),
            "creator_count": len(creators),
            "post_count": len(posts),
            "notes": [
                "Only public BlueSky API data is collected (no authentication required).",
                "Access to private profiles and direct messages requires OAuth.",
                "Rate card and collaboration preferences need creator input or later enrichment.",
                "BlueSky API endpoints used: app.bsky.actor.searchActors, app.bsky.actor.getProfile, app.bsky.feed.getAuthorFeed",
            ],
        },
        "collection_config": {
            "search_queries": list(config.search_queries),
            "max_creators": config.max_creators,
            "max_posts_per_creator": config.max_posts_per_creator,
            "include_raw_api_payloads": config.include_raw_api_payloads,
        },
        "creators": creators,
        "posts": posts,
        "raw_search_pages": raw_search_pages if config.include_raw_api_payloads else [],
    }


def save_dataset(dataset: dict[str, Any], output_dir: Path) -> dict[str, str]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dataset_path = output_dir / f"brandbridge_bsky_dataset_{timestamp}.json"
    creators_path = output_dir / f"brandbridge_bsky_creators_{timestamp}.json"
    posts_path = output_dir / f"brandbridge_bsky_posts_{timestamp}.json"

    write_json(dataset_path, dataset)
    write_json(creators_path, dataset["creators"])
    write_json(posts_path, dataset["posts"])

    latest_dataset_path = output_dir / "brandbridge_bsky_dataset.latest.json"
    latest_creators_path = output_dir / "brandbridge_bsky_creators.latest.json"
    latest_posts_path = output_dir / "brandbridge_bsky_posts.latest.json"

    write_json(latest_dataset_path, dataset)
    write_json(latest_creators_path, dataset["creators"])
    write_json(latest_posts_path, dataset["posts"])

    return {
        "dataset": str(dataset_path),
        "creators": str(creators_path),
        "posts": str(posts_path),
        "latest_dataset": str(latest_dataset_path),
        "latest_creators": str(latest_creators_path),
        "latest_posts": str(latest_posts_path),
    }


def parse_search_queries(values: list[str] | None) -> tuple[str, ...]:
    if not values:
        return get_list_env("BSKY_SEARCH_QUERIES", DEFAULT_SEARCH_QUERIES)

    queries: list[str] = []
    for value in values:
        queries.extend(query.strip() for query in value.split(",") if query.strip())
    return tuple(queries)


def build_config_from_args(args: argparse.Namespace) -> BlueSkyCollectorConfig:
    return BlueSkyCollectorConfig(
        output_dir=Path(args.output_dir),
        search_queries=parse_search_queries(args.search_query),
        max_creators=args.max_creators,
        max_posts_per_creator=args.max_posts_per_creator,
        request_delay_seconds=args.request_delay_seconds,
        include_raw_api_payloads=not args.no_raw,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect public BlueSky creator data for BrandBridge AI analysis."
    )
    parser.add_argument(
        "--max-creators",
        type=int,
        default=get_int_env("BSKY_MAX_CREATORS", 100),
    )
    parser.add_argument(
        "--max-posts-per-creator",
        type=int,
        default=get_int_env("BSKY_MAX_POSTS_PER_CREATOR", 50),
    )
    parser.add_argument(
        "--search-query",
        action="append",
        help="Search query. Can be repeated or comma-separated.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where JSON output files will be written.",
    )
    parser.add_argument(
        "--request-delay-seconds",
        type=float,
        default=get_float_env("BSKY_REQUEST_DELAY_SECONDS", 0.1),
    )
    parser.add_argument(
        "--no-raw",
        action="store_true",
        help="Exclude raw API payloads from the generated dataset.",
    )
    return parser.parse_args()


def main() -> None:
    try:
        config = build_config_from_args(parse_args())
        dataset = collect_bsky_creator_data(config)
        output_files = save_dataset(dataset, config.output_dir)
    except BlueSkyCollectionError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1) from None

    print(json.dumps({"metadata": dataset["metadata"], "output_files": output_files}, indent=2))


if __name__ == "__main__":
    main()
