from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "youtube"

CHANNEL_PARTS = (
    "snippet",
    "statistics",
    "contentDetails",
    "brandingSettings",
    "topicDetails",
    "status",
    "localizations",
)

VIDEO_PARTS = (
    "snippet",
    "statistics",
    "contentDetails",
    "status",
    "topicDetails",
    "recordingDetails",
    "liveStreamingDetails",
    "localizations",
)

PLAYLIST_ITEM_PARTS = (
    "snippet",
    "contentDetails",
    "status",
)

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


class YouTubeCollectionError(RuntimeError):
    """Raised when YouTube data collection cannot continue."""


@dataclass(frozen=True)
class YouTubeCollectorConfig:
    api_key: str
    output_dir: Path = DEFAULT_OUTPUT_DIR
    search_queries: tuple[str, ...] = DEFAULT_SEARCH_QUERIES
    max_creators: int = 100
    max_videos_per_creator: int = 20
    search_pages_per_query: int = 1
    region_code: str = "IN"
    language_code: str = "en"
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


def chunked(values: list[str], size: int) -> list[list[str]]:
    return [values[index : index + size] for index in range(0, len(values), size)]


def parse_youtube_duration_seconds(duration: str | None) -> int | None:
    if not duration:
        return None

    pattern = re.compile(
        r"^P(?:(?P<days>\d+)D)?"
        r"(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?$"
    )
    match = pattern.match(duration)
    if not match:
        return None

    parts = {key: int(value or 0) for key, value in match.groupdict().items()}
    return (
        parts["days"] * 86_400
        + parts["hours"] * 3_600
        + parts["minutes"] * 60
        + parts["seconds"]
    )


def infer_content_formats(videos: list[dict[str, Any]]) -> list[str]:
    formats: set[str] = set()

    for video in videos:
        duration_seconds = video.get("duration_seconds")
        if duration_seconds is None:
            continue
        if duration_seconds <= 60:
            formats.add("short_form")
        elif duration_seconds <= 600:
            formats.add("mid_form")
        else:
            formats.add("long_form")

    return sorted(formats)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output_file:
        json.dump(data, output_file, indent=2, ensure_ascii=False)


def youtube_get(
    resource: str,
    params: dict[str, str | int | None],
    config: YouTubeCollectorConfig,
) -> dict[str, Any]:
    request_params = {
        key: value
        for key, value in params.items()
        if value is not None and value != ""
    }
    request_params["key"] = config.api_key

    url = f"{YOUTUBE_API_BASE_URL}/{resource}?{urlencode(request_params)}"
    request = Request(url, headers={"Accept": "application/json"})

    try:
        with urlopen(request, timeout=config.timeout_seconds) as response:
            payload = response.read().decode("utf-8")
    except HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        raise YouTubeCollectionError(
            f"YouTube API request failed with HTTP {error.code}: {error_body}"
        ) from error
    except URLError as error:
        raise YouTubeCollectionError(f"YouTube API request failed: {error}") from error

    time.sleep(config.request_delay_seconds)
    return json.loads(payload)


def search_channels(
    config: YouTubeCollectorConfig,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    channel_lookup: dict[str, dict[str, Any]] = {}
    raw_search_pages: list[dict[str, Any]] = []

    for query in config.search_queries:
        next_page_token: str | None = None

        for page_number in range(config.search_pages_per_query):
            response = youtube_get(
                "search",
                {
                    "part": "snippet",
                    "q": query,
                    "type": "channel",
                    "maxResults": 50,
                    "regionCode": config.region_code,
                    "relevanceLanguage": config.language_code,
                    "pageToken": next_page_token,
                },
                config,
            )

            raw_search_pages.append(
                {
                    "query": query,
                    "page_number": page_number + 1,
                    "response": response,
                }
            )

            for item in response.get("items", []):
                channel_id = item.get("id", {}).get("channelId")
                if not channel_id:
                    continue

                snippet = item.get("snippet", {})
                existing = channel_lookup.setdefault(
                    channel_id,
                    {
                        "channel_id": channel_id,
                        "discovery_queries": [],
                        "search_results": [],
                    },
                )

                if query not in existing["discovery_queries"]:
                    existing["discovery_queries"].append(query)

                existing["search_results"].append(
                    {
                        "query": query,
                        "title": snippet.get("title"),
                        "description": snippet.get("description"),
                        "published_at": snippet.get("publishedAt"),
                        "thumbnail_url": snippet.get("thumbnails", {})
                        .get("high", {})
                        .get("url"),
                        "raw": item if config.include_raw_api_payloads else None,
                    }
                )

                if len(channel_lookup) >= config.max_creators:
                    break

            if len(channel_lookup) >= config.max_creators:
                break

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        if len(channel_lookup) >= config.max_creators:
            break

    return channel_lookup, raw_search_pages


def get_channel_details(
    channel_lookup: dict[str, dict[str, Any]],
    config: YouTubeCollectorConfig,
) -> list[dict[str, Any]]:
    channel_ids = list(channel_lookup.keys())
    channels: list[dict[str, Any]] = []

    for batch in chunked(channel_ids, 50):
        response = youtube_get(
            "channels",
            {
                "part": ",".join(CHANNEL_PARTS),
                "id": ",".join(batch),
                "maxResults": 50,
            },
            config,
        )
        channels.extend(response.get("items", []))

    return channels


def get_recent_playlist_videos(
    channel: dict[str, Any],
    config: YouTubeCollectorConfig,
) -> list[dict[str, Any]]:
    playlist_id = channel.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
    if not playlist_id:
        return []

    playlist_items: list[dict[str, Any]] = []
    next_page_token: str | None = None

    while len(playlist_items) < config.max_videos_per_creator:
        remaining = config.max_videos_per_creator - len(playlist_items)
        response = youtube_get(
            "playlistItems",
            {
                "part": ",".join(PLAYLIST_ITEM_PARTS),
                "playlistId": playlist_id,
                "maxResults": min(50, remaining),
                "pageToken": next_page_token,
            },
            config,
        )

        items = response.get("items", [])
        playlist_items.extend(items)

        next_page_token = response.get("nextPageToken")
        if not next_page_token or not items:
            break

    return playlist_items[: config.max_videos_per_creator]


def get_video_details(
    video_ids: list[str],
    config: YouTubeCollectorConfig,
) -> dict[str, dict[str, Any]]:
    video_lookup: dict[str, dict[str, Any]] = {}

    for batch in chunked(video_ids, 50):
        response = youtube_get(
            "videos",
            {
                "part": ",".join(VIDEO_PARTS),
                "id": ",".join(batch),
                "maxResults": 50,
            },
            config,
        )

        for video in response.get("items", []):
            video_lookup[video["id"]] = video

    return video_lookup


def normalize_video(
    playlist_item: dict[str, Any],
    video_resource: dict[str, Any] | None,
    creator_name: str | None,
    include_raw: bool,
) -> dict[str, Any]:
    content_details = playlist_item.get("contentDetails", {})
    playlist_snippet = playlist_item.get("snippet", {})
    video_id = content_details.get("videoId")
    video_resource = video_resource or {}
    video_snippet = video_resource.get("snippet", playlist_snippet)
    video_stats = video_resource.get("statistics", {})
    video_content = video_resource.get("contentDetails", {})
    video_status = video_resource.get("status", {})

    duration = video_content.get("duration")
    duration_seconds = parse_youtube_duration_seconds(duration)

    return {
        "video_id": video_id,
        "channel_id": video_snippet.get("channelId") or playlist_snippet.get("channelId"),
        "creator_name": creator_name,
        "title": video_snippet.get("title") or playlist_snippet.get("title"),
        "description": video_snippet.get("description") or playlist_snippet.get("description"),
        "published_at": video_snippet.get("publishedAt") or playlist_snippet.get("publishedAt"),
        "thumbnail_url": video_snippet.get("thumbnails", {}).get("high", {}).get("url"),
        "category_id": video_snippet.get("categoryId"),
        "tags": video_snippet.get("tags", []),
        "default_language": video_snippet.get("defaultLanguage"),
        "default_audio_language": video_snippet.get("defaultAudioLanguage"),
        "duration_iso8601": duration,
        "duration_seconds": duration_seconds,
        "definition": video_content.get("definition"),
        "caption": video_content.get("caption"),
        "licensed_content": video_content.get("licensedContent"),
        "privacy_status": video_status.get("privacyStatus"),
        "embeddable": video_status.get("embeddable"),
        "made_for_kids": video_status.get("madeForKids"),
        "views": safe_int(video_stats.get("viewCount")),
        "likes": safe_int(video_stats.get("likeCount")),
        "comments": safe_int(video_stats.get("commentCount")),
        "topic_categories": video_resource.get("topicDetails", {}).get("topicCategories", []),
        "raw": video_resource if include_raw else None,
    }


def extract_top_tags(videos: list[dict[str, Any]], limit: int = 25) -> list[str]:
    counter: Counter[str] = Counter()
    for video in videos:
        for tag in video.get("tags", []):
            cleaned = str(tag).strip().lower()
            if cleaned:
                counter[cleaned] += 1
    return [tag for tag, _count in counter.most_common(limit)]


def derive_creator_categories(
    discovery_queries: list[str],
    top_tags: list[str],
    limit: int = 15,
) -> list[str]:
    ignored_words = {"india", "indian", "creator", "channel", "youtube"}
    categories: list[str] = []

    for query in discovery_queries:
        for word in query.lower().replace("/", " ").split():
            if word not in ignored_words and word not in categories:
                categories.append(word)

    for tag in top_tags:
        if tag not in ignored_words and tag not in categories:
            categories.append(tag)

    return categories[:limit]


def calculate_creator_metrics(videos: list[dict[str, Any]]) -> dict[str, Any]:
    views = [safe_int(video.get("views")) for video in videos]
    likes = [safe_int(video.get("likes")) for video in videos]
    comments = [safe_int(video.get("comments")) for video in videos]
    valid_views = [value for value in views if value > 0]

    average_views = safe_mean(valid_views)
    average_likes = safe_mean(likes)
    average_comments = safe_mean(comments)

    engagement_rate = 0.0
    if average_views > 0:
        engagement_rate = ((average_likes + average_comments) / average_views) * 100

    return {
        "videos_analyzed": len(videos),
        "average_views": round(average_views, 2),
        "average_likes": round(average_likes, 2),
        "average_comments": round(average_comments, 2),
        "engagement_rate_percent": round(engagement_rate, 4),
        "total_recent_views": sum(views),
        "total_recent_likes": sum(likes),
        "total_recent_comments": sum(comments),
    }


def build_creator_record(
    channel: dict[str, Any],
    discovery: dict[str, Any],
    videos: list[dict[str, Any]],
    include_raw: bool,
) -> dict[str, Any]:
    channel_id = channel["id"]
    snippet = channel.get("snippet", {})
    statistics = channel.get("statistics", {})
    branding = channel.get("brandingSettings", {})
    content_details = channel.get("contentDetails", {})
    status = channel.get("status", {})
    topic_details = channel.get("topicDetails", {})

    metrics = calculate_creator_metrics(videos)
    subscriber_count = safe_int(statistics.get("subscriberCount"))
    average_views = metrics["average_views"]
    views_to_subscriber_ratio = (
        round(average_views / subscriber_count, 4) if subscriber_count else 0
    )
    top_tags = extract_top_tags(videos)
    discovery_queries = discovery.get("discovery_queries", [])
    creator_categories = derive_creator_categories(discovery_queries, top_tags)
    content_formats = infer_content_formats(videos)

    channel_url = f"https://www.youtube.com/channel/{channel_id}"
    custom_url = snippet.get("customUrl")

    return {
        "creator_id": f"youtube:{channel_id}",
        "platform": "youtube",
        "channel": {
            "channel_id": channel_id,
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "custom_url": custom_url,
            "channel_url": channel_url,
            "country": snippet.get("country"),
            "published_at": snippet.get("publishedAt"),
            "default_language": snippet.get("defaultLanguage"),
            "localized": snippet.get("localized"),
            "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url"),
            "uploads_playlist_id": content_details.get("relatedPlaylists", {}).get("uploads"),
        },
        "public_statistics": {
            "subscriber_count": subscriber_count,
            "hidden_subscriber_count": statistics.get("hiddenSubscriberCount", False),
            "total_view_count": safe_int(statistics.get("viewCount")),
            "video_count": safe_int(statistics.get("videoCount")),
        },
        "branding": {
            "channel_keywords": branding.get("channel", {}).get("keywords"),
            "unsubscribed_trailer": branding.get("channel", {}).get("unsubscribedTrailer"),
            "default_tab": branding.get("channel", {}).get("defaultTab"),
        },
        "status": {
            "privacy_status": status.get("privacyStatus"),
            "is_linked": status.get("isLinked"),
            "long_uploads_status": status.get("longUploadsStatus"),
            "made_for_kids": status.get("madeForKids"),
        },
        "topics": {
            "topic_ids": topic_details.get("topicIds", []),
            "topic_categories": topic_details.get("topicCategories", []),
        },
        "discovery": {
            "queries": discovery_queries,
            "search_results": discovery.get("search_results", []),
        },
        "recent_video_metrics": {
            **metrics,
            "average_views_to_subscriber_ratio": views_to_subscriber_ratio,
            "top_tags": top_tags,
            "content_formats_observed": content_formats,
        },
        "brandbridge_fields": {
            "creator_categories": creator_categories,
            "platforms": {
                "youtube": {
                    "channel_id": channel_id,
                    "channel_url": channel_url,
                    "custom_url": custom_url,
                    "subscribers": subscriber_count,
                    "average_views": average_views,
                    "engagement_rate_percent": metrics["engagement_rate_percent"],
                }
            },
            "audience": {
                "primary_country": snippet.get("country"),
                "age_range": None,
                "gender_split": None,
                "missing_reason": (
                    "Audience demographics require YouTube Analytics OAuth permission "
                    "from the creator or manual creator input."
                ),
            },
            "collaboration": {
                "rate_card": None,
                "business_email": None,
                "preferred_content_formats": content_formats,
                "missing_reason": (
                    "Rate card and contact details are not available from the public "
                    "YouTube Data API key flow."
                ),
            },
            "matching_features": {
                "category_similarity_inputs": creator_categories,
                "country_match_input": snippet.get("country"),
                "platform_match_input": "youtube",
                "engagement_rate": metrics["engagement_rate_percent"],
                "follower_score_input": subscriber_count,
                "semantic_similarity_text": " ".join(
                    value
                    for value in [
                        snippet.get("title"),
                        snippet.get("description"),
                        " ".join(top_tags[:10]),
                    ]
                    if value
                ),
            },
        },
        "recent_videos": videos,
        "raw": channel if include_raw else None,
    }


def collect_youtube_creator_data(config: YouTubeCollectorConfig) -> dict[str, Any]:
    started_at = datetime.now(UTC)
    channel_lookup, raw_search_pages = search_channels(config)
    channels = get_channel_details(channel_lookup, config)

    all_video_ids: list[str] = []
    playlist_items_by_channel: dict[str, list[dict[str, Any]]] = {}

    for channel in channels:
        channel_id = channel["id"]
        playlist_items = get_recent_playlist_videos(channel, config)
        playlist_items_by_channel[channel_id] = playlist_items

        for item in playlist_items:
            video_id = item.get("contentDetails", {}).get("videoId")
            if video_id and video_id not in all_video_ids:
                all_video_ids.append(video_id)

    video_detail_lookup = get_video_details(all_video_ids, config)

    creators: list[dict[str, Any]] = []
    videos: list[dict[str, Any]] = []

    for channel in channels:
        channel_id = channel["id"]
        snippet = channel.get("snippet", {})
        normalized_videos = [
            normalize_video(
                item,
                video_detail_lookup.get(item.get("contentDetails", {}).get("videoId")),
                snippet.get("title"),
                config.include_raw_api_payloads,
            )
            for item in playlist_items_by_channel.get(channel_id, [])
        ]

        videos.extend(normalized_videos)
        creators.append(
            build_creator_record(
                channel,
                channel_lookup.get(channel_id, {}),
                normalized_videos,
                config.include_raw_api_payloads,
            )
        )

    creators.sort(
        key=lambda creator: creator["public_statistics"]["subscriber_count"],
        reverse=True,
    )

    finished_at = datetime.now(UTC)
    return {
        "metadata": {
            "project": "BrandBridge AI",
            "source": "YouTube Data API v3",
            "data_classification": "development_public_api_data",
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "duration_seconds": round((finished_at - started_at).total_seconds(), 2),
            "creator_count": len(creators),
            "video_count": len(videos),
            "notes": [
                "Only public YouTube Data API fields are collected with an API key.",
                "Private analytics, audience demographics, revenue, and watch-time data "
                "require OAuth.",
                "Rate card, collaboration preferences, and brand safety labels need creator "
                "input or later enrichment.",
            ],
        },
        "collection_config": {
            "search_queries": list(config.search_queries),
            "max_creators": config.max_creators,
            "max_videos_per_creator": config.max_videos_per_creator,
            "search_pages_per_query": config.search_pages_per_query,
            "region_code": config.region_code,
            "language_code": config.language_code,
            "include_raw_api_payloads": config.include_raw_api_payloads,
        },
        "creators": creators,
        "videos": videos,
        "raw_search_pages": raw_search_pages if config.include_raw_api_payloads else [],
    }


def save_dataset(dataset: dict[str, Any], output_dir: Path) -> dict[str, str]:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    dataset_path = output_dir / f"brandbridge_youtube_dataset_{timestamp}.json"
    creators_path = output_dir / f"brandbridge_youtube_creators_{timestamp}.json"
    videos_path = output_dir / f"brandbridge_youtube_videos_{timestamp}.json"

    write_json(dataset_path, dataset)
    write_json(creators_path, dataset["creators"])
    write_json(videos_path, dataset["videos"])

    latest_dataset_path = output_dir / "brandbridge_youtube_dataset.latest.json"
    latest_creators_path = output_dir / "brandbridge_youtube_creators.latest.json"
    latest_videos_path = output_dir / "brandbridge_youtube_videos.latest.json"

    write_json(latest_dataset_path, dataset)
    write_json(latest_creators_path, dataset["creators"])
    write_json(latest_videos_path, dataset["videos"])

    return {
        "dataset": str(dataset_path),
        "creators": str(creators_path),
        "videos": str(videos_path),
        "latest_dataset": str(latest_dataset_path),
        "latest_creators": str(latest_creators_path),
        "latest_videos": str(latest_videos_path),
    }


def parse_search_queries(values: list[str] | None) -> tuple[str, ...]:
    if not values:
        return get_list_env("YOUTUBE_SEARCH_QUERIES", DEFAULT_SEARCH_QUERIES)

    queries: list[str] = []
    for value in values:
        queries.extend(query.strip() for query in value.split(",") if query.strip())
    return tuple(queries)


def build_config_from_args(args: argparse.Namespace) -> YouTubeCollectorConfig:
    api_key = get_env("YOUTUBE_API_KEY")
    if not api_key:
        raise YouTubeCollectionError(
            "YOUTUBE_API_KEY is missing. Add it to your local .env or shell environment."
        )

    return YouTubeCollectorConfig(
        api_key=api_key,
        output_dir=Path(args.output_dir),
        search_queries=parse_search_queries(args.search_query),
        max_creators=args.max_creators,
        max_videos_per_creator=args.max_videos_per_creator,
        search_pages_per_query=args.search_pages_per_query,
        region_code=args.region_code,
        language_code=args.language_code,
        request_delay_seconds=args.request_delay_seconds,
        include_raw_api_payloads=not args.no_raw,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect public YouTube creator data for BrandBridge AI analysis."
    )
    parser.add_argument(
        "--max-creators",
        type=int,
        default=get_int_env("YOUTUBE_MAX_CREATORS", 100),
    )
    parser.add_argument(
        "--max-videos-per-creator",
        type=int,
        default=get_int_env("YOUTUBE_MAX_VIDEOS_PER_CREATOR", 20),
    )
    parser.add_argument(
        "--search-pages-per-query",
        type=int,
        default=get_int_env("YOUTUBE_SEARCH_PAGES_PER_QUERY", 1),
    )
    parser.add_argument("--region-code", default=get_env("YOUTUBE_REGION_CODE", "IN"))
    parser.add_argument("--language-code", default=get_env("YOUTUBE_LANGUAGE_CODE", "en"))
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
        default=get_float_env("YOUTUBE_REQUEST_DELAY_SECONDS", 0.1),
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
        dataset = collect_youtube_creator_data(config)
        output_files = save_dataset(dataset, config.output_dir)
    except YouTubeCollectionError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1) from None

    print(json.dumps({"metadata": dataset["metadata"], "output_files": output_files}, indent=2))


if __name__ == "__main__":
    main()
