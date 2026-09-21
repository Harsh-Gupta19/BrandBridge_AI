"""
BrandBridge AI - YouTube Data API v3 ALL-FIELD EXPLORER

Reads YOUTUBE_API_KEY directly from the project .env, so it does not depend
on VS Code terminal environment-file injection.

Run from the BrandBridge_AI project root:
    python backend/app/integrations/youtube/youtube_data_api_all_fields.py

Recommended first test in .env:
    YOUTUBE_CHANNEL_ID=YOUR_CHANNEL_ID
    YOUTUBE_MAX_VIDEOS=5
    YOUTUBE_MAX_PLAYLISTS=5
    YOUTUBE_MAX_COMMENT_THREADS=5
    YOUTUBE_MAX_ACTIVITIES=10
    YOUTUBE_MAX_CHANNEL_SECTIONS=10

Output:
    data/raw/youtube/youtube_data_api_all_fields.json
    data/raw/youtube/youtube_v3_discovery.json

This is an exploratory field collector. Public fields are collected with an
API key. Owner-only/restricted fields are attempted separately and recorded
as null + an error when the current credentials cannot access them.
"""

from __future__ import annotations

import csv
import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# ============================================================
# PROJECT / CONFIG
# ============================================================

YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"
DISCOVERY_URL = "https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest"

PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "youtube"
OUTPUT_FILE = OUTPUT_DIR / "youtube_data_api_all_fields.json"
DISCOVERY_FILE = OUTPUT_DIR / "youtube_v3_discovery.json"
CREATOR_CSV = OUTPUT_DIR / "youtube_creators.csv"

DEFAULT_TIMEOUT = 30
DEFAULT_DELAY = 0.1


# ============================================================
# ENVIRONMENT LOADER
# Same approach as your working collector.
# ============================================================


def load_dotenv_values() -> dict[str, str]:
    values: dict[str, str] = {}

    for env_path in (
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / "backend" / ".env",
    ):
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
    try:
        return int(value)
    except ValueError:
        return default


def get_float_env(name: str, default: float) -> float:
    value = get_env(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def get_bool_env(name: str, default: bool) -> bool:
    value = get_env(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def get_api_key() -> str:
    key = get_env("YOUTUBE_API_KEY")
    if not key:
        raise RuntimeError(
            "YOUTUBE_API_KEY is not configured.\n"
            "Checked:\n"
            f"  {PROJECT_ROOT / '.env'}\n"
            f"  {PROJECT_ROOT / 'backend' / '.env'}"
        )
    return key


# ============================================================
# DOCUMENTED PARTS
# ============================================================

CHANNEL_PARTS = [
    "snippet",
    "contentDetails",
    "statistics",
    "topicDetails",
    "status",
    "brandingSettings",
    "auditDetails",
    "contentOwnerDetails",
    "localizations",
]
CHANNEL_PUBLIC_PARTS = [
    "snippet",
    "contentDetails",
    "statistics",
    "topicDetails",
    "status",
    "brandingSettings",
    "localizations",
]
CHANNEL_RESTRICTED_PARTS = ["auditDetails", "contentOwnerDetails"]

VIDEO_PARTS = [
    "brandPartner",
    "contentDetails",
    "fileDetails",
    "id",
    "liveStreamingDetails",
    "localizations",
    "paidProductPlacementDetails",
    "player",
    "processingDetails",
    "recordingDetails",
    "snippet",
    "statistics",
    "status",
    "suggestions",
    "topicDetails",
]
VIDEO_PUBLIC_PARTS = [
    "brandPartner",
    "contentDetails",
    "id",
    "liveStreamingDetails",
    "localizations",
    "paidProductPlacementDetails",
    "player",
    "recordingDetails",
    "snippet",
    "statistics",
    "status",
    "topicDetails",
]
VIDEO_RESTRICTED_PARTS = ["fileDetails", "processingDetails", "suggestions"]

PLAYLIST_PARTS = ["snippet", "contentDetails", "status", "player", "localizations"]
PLAYLIST_ITEM_PARTS = ["snippet", "contentDetails", "status"]
COMMENT_THREAD_PARTS = ["snippet", "replies"]
ACTIVITY_PARTS = ["snippet", "contentDetails"]
CHANNEL_SECTION_PARTS = ["snippet", "contentDetails"]


# ============================================================
# GENERIC HELPERS
# ============================================================


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def chunked(values: list[str], size: int) -> list[list[str]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


def youtube_get(resource: str, params: dict[str, Any]) -> dict[str, Any]:
    request_params = {k: v for k, v in params.items() if v is not None and v != ""}
    request_params["key"] = get_api_key()

    url = f"{YOUTUBE_API_BASE_URL}/{resource}?{urlencode(request_params)}"
    request = Request(url, headers={"Accept": "application/json"})

    try:
        with urlopen(
            request, timeout=get_int_env("YOUTUBE_TIMEOUT_SECONDS", DEFAULT_TIMEOUT)
        ) as response:
            payload = response.read().decode("utf-8")
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"YouTube API HTTP {error.code}: {body}") from error
    except URLError as error:
        raise RuntimeError(f"YouTube API request failed: {error}") from error

    delay = get_float_env("YOUTUBE_REQUEST_DELAY_SECONDS", DEFAULT_DELAY)
    if delay > 0:
        time.sleep(delay)

    return json.loads(payload)


def safe_get(resource: str, params: dict[str, Any]) -> dict[str, Any]:
    try:
        return {"available": True, "value": youtube_get(resource, params), "error": None}
    except Exception as error:
        return {"available": False, "value": None, "error": str(error)}


# ============================================================
# DISCOVERY SCHEMA
# ============================================================


def get_discovery() -> dict[str, Any]:
    if DISCOVERY_FILE.exists():
        try:
            return json.loads(DISCOVERY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    request = Request(DISCOVERY_URL, headers={"Accept": "application/json"})
    with urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
        discovery = json.loads(response.read().decode("utf-8"))

    write_json(DISCOVERY_FILE, discovery)
    return discovery


def resolve_schema(discovery: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    if "$ref" in schema:
        return discovery.get("schemas", {}).get(schema["$ref"], schema)
    return schema


def null_structure(discovery: dict[str, Any], schema: dict[str, Any]) -> Any:
    schema = resolve_schema(discovery, schema)
    schema_type = schema.get("type")

    if schema_type == "object":
        return {
            name: null_structure(discovery, child)
            for name, child in schema.get("properties", {}).items()
        }

    if schema_type == "array":
        return []

    return None


def merge_schema(
    discovery: dict[str, Any],
    schema: dict[str, Any],
    actual: Any,
) -> Any:
    schema = resolve_schema(discovery, schema)

    if actual is None:
        return null_structure(discovery, schema)

    schema_type = schema.get("type")

    if schema_type == "object" and isinstance(actual, dict):
        properties = schema.get("properties", {})
        result: dict[str, Any] = {}

        for name, child in properties.items():
            if name in actual:
                result[name] = merge_schema(discovery, child, actual[name])
            else:
                result[name] = null_structure(discovery, child)

        # Preserve dynamic-map keys such as thumbnail sizes/localization maps.
        for name, value in actual.items():
            if name not in result:
                result[name] = value

        return result

    if schema_type == "array" and isinstance(actual, list):
        child = schema.get("items", {})
        return [merge_schema(discovery, child, item) for item in actual]

    return actual


def normalize(
    discovery: dict[str, Any],
    schema_name: str,
    resource: dict[str, Any] | None,
    error: str | None = None,
) -> dict[str, Any]:
    schema = discovery.get("schemas", {}).get(schema_name, {})

    value = (
        merge_schema(discovery, schema, resource)
        if resource is not None
        else null_structure(discovery, schema)
    )

    if not isinstance(value, dict):
        value = {"value": value}

    value["_availability"] = {
        "available": resource is not None and error is None,
        "error": error,
    }
    return value


# ============================================================
# CHANNELS
# ============================================================


def get_channel(channel_id: str, discovery: dict[str, Any]) -> dict[str, Any]:
    public = safe_get(
        "channels",
        {"part": ",".join(CHANNEL_PUBLIC_PARTS), "id": channel_id},
    )

    public_items = (public["value"] or {}).get("items", []) if public["available"] else []
    resource = public_items[0] if public_items else None

    result: dict[str, Any] = {
        "channel_id": channel_id,
        "resource": normalize(
            discovery,
            "Channel",
            resource,
            None if resource else public["error"] or "Channel not found.",
        ),
        "restricted_parts": {},
    }

    for part in CHANNEL_RESTRICTED_PARTS:
        response = safe_get(
            "channels",
            {"part": part, "id": channel_id},
        )
        items = (response["value"] or {}).get("items", []) if response["available"] else []
        restricted = items[0] if items else None
        result["restricted_parts"][part] = {
            "available": restricted is not None,
            "value": restricted,
            "error": None
            if restricted is not None
            else (response["error"] or "No resource returned."),
        }
        if restricted:
            result["resource"] = merge_schema(
                discovery,
                discovery.get("schemas", {}).get("Channel", {}),
                {**(result.get("resource") or {}), **restricted},
            )

    return result


# ============================================================
# PLAYLIST ITEMS / VIDEOS / PLAYLISTS
# ============================================================


def get_playlist_items(playlist_id: str, max_items: int) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    page_token: str | None = None

    try:
        while len(items) < max_items:
            response = youtube_get(
                "playlistItems",
                {
                    "part": ",".join(PLAYLIST_ITEM_PARTS),
                    "playlistId": playlist_id,
                    "maxResults": min(50, max_items - len(items)),
                    "pageToken": page_token,
                },
            )
            page_items = response.get("items", [])
            items.extend(page_items)
            page_token = response.get("nextPageToken")
            if not page_token or not page_items:
                break

        return {"available": True, "items": items[:max_items], "error": None}
    except Exception as error:
        return {"available": False, "items": items, "error": str(error)}


def get_playlists(channel_id: str, max_items: int) -> dict[str, Any]:
    try:
        response = youtube_get(
            "playlists",
            {
                "part": ",".join(PLAYLIST_PARTS),
                "channelId": channel_id,
                "maxResults": min(50, max_items),
            },
        )
        return {
            "available": True,
            "items": response.get("items", [])[:max_items],
            "error": None,
        }
    except Exception as error:
        return {"available": False, "items": [], "error": str(error)}


def get_videos(video_ids: list[str], discovery: dict[str, Any]) -> list[dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}

    for batch in chunked(video_ids, 50):
        if not batch:
            continue

        public = safe_get(
            "videos",
            {"part": ",".join(VIDEO_PUBLIC_PARTS), "id": ",".join(batch)},
        )
        public_items = (public["value"] or {}).get("items", []) if public["available"] else []
        by_id = {item.get("id"): item for item in public_items if item.get("id")}

        for video_id in batch:
            resource = by_id.get(video_id)
            results[video_id] = {
                "resource": normalize(
                    discovery,
                    "Video",
                    resource,
                    None if resource else public["error"] or "Video not returned.",
                ),
                "restricted_parts": {},
            }

        # Owner-only parts are requested one part at a time so a forbidden
        # part does not prevent the public fields from being collected.
        for part in VIDEO_RESTRICTED_PARTS:
            response = safe_get(
                "videos",
                {"part": part, "id": ",".join(batch)},
            )
            restricted_items = (
                (response["value"] or {}).get("items", []) if response["available"] else []
            )
            restricted_by_id = {item.get("id"): item for item in restricted_items if item.get("id")}

            for video_id in batch:
                restricted = restricted_by_id.get(video_id)
                results[video_id]["restricted_parts"][part] = {
                    "available": restricted is not None,
                    "value": restricted,
                    "error": None
                    if restricted is not None
                    else (response["error"] or "No resource returned."),
                }

    return list(results.values())


# ============================================================
# OTHER CREATOR-RELATED RESOURCES
# ============================================================


def get_comment_threads(video_id: str, max_items: int, discovery: dict[str, Any]) -> dict[str, Any]:
    try:
        response = youtube_get(
            "commentThreads",
            {
                "part": ",".join(COMMENT_THREAD_PARTS),
                "videoId": video_id,
                "maxResults": min(100, max_items),
                "textFormat": "plainText",
            },
        )
        return {
            "available": True,
            "items": [
                normalize(discovery, "CommentThread", x)
                for x in response.get("items", [])[:max_items]
            ],
            "error": None,
        }
    except Exception as error:
        return {"available": False, "items": [], "error": str(error)}


def get_activities(channel_id: str, max_items: int, discovery: dict[str, Any]) -> dict[str, Any]:
    try:
        response = youtube_get(
            "activities",
            {
                "part": ",".join(ACTIVITY_PARTS),
                "channelId": channel_id,
                "maxResults": min(50, max_items),
            },
        )
        return {
            "available": True,
            "items": [
                normalize(discovery, "Activity", x) for x in response.get("items", [])[:max_items]
            ],
            "error": None,
        }
    except Exception as error:
        return {"available": False, "items": [], "error": str(error)}


def get_channel_sections(
    channel_id: str, max_items: int, discovery: dict[str, Any]
) -> dict[str, Any]:
    try:
        response = youtube_get(
            "channelSections",
            {
                "part": ",".join(CHANNEL_SECTION_PARTS),
                "channelId": channel_id,
                "maxResults": min(50, max_items),
            },
        )
        return {
            "available": True,
            "items": [
                normalize(discovery, "ChannelSection", x)
                for x in response.get("items", [])[:max_items]
            ],
            "error": None,
        }
    except Exception as error:
        return {"available": False, "items": [], "error": str(error)}


def get_reference_resources() -> dict[str, Any]:
    result: dict[str, Any] = {}
    region = get_env("YOUTUBE_REGION_CODE", "IN") or "IN"

    calls = {
        "video_categories": (
            "videoCategories",
            {"part": "snippet", "regionCode": region, "maxResults": 50},
        ),
        "guide_categories": (
            "guideCategories",
            {"part": "snippet", "regionCode": region, "maxResults": 50},
        ),
        "i18n_languages": ("i18nLanguages", {"part": "snippet"}),
        "i18n_regions": ("i18nRegions", {"part": "snippet"}),
        "video_abuse_report_reasons": ("videoAbuseReportReasons", {"part": "snippet"}),
    }

    for name, (resource, params) in calls.items():
        response = safe_get(resource, params)
        result[name] = {
            "available": response["available"],
            "items": (response["value"] or {}).get("items", []) if response["available"] else [],
            "error": response["error"],
        }

    return result


# ============================================================
# CHANNEL ID SOURCE
# ============================================================


def read_csv_channel_ids() -> list[str]:
    if not CREATOR_CSV.exists():
        return []

    ids: list[str] = []
    with CREATOR_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            channel_id = row.get("channel_id") or row.get("channelId")
            if channel_id and channel_id not in ids:
                ids.append(channel_id.strip())
    return ids


def discover_channels() -> tuple[list[str], dict[str, Any]]:
    configured = get_env("YOUTUBE_CHANNEL_ID")
    max_creators = get_int_env("YOUTUBE_MAX_CREATORS", 100)

    if configured:
        ids = [x.strip() for x in configured.split(",") if x.strip()]
        return ids[:max_creators], {"used": False, "queries": [], "pages": []}

    csv_ids = read_csv_channel_ids()
    if csv_ids:
        return csv_ids[:max_creators], {
            "used": False,
            "queries": [],
            "pages": [],
            "source": str(CREATOR_CSV),
        }

    queries_raw = get_env("YOUTUBE_SEARCH_QUERIES")
    if queries_raw:
        queries = [x.strip() for x in queries_raw.split(",") if x.strip()]
    else:
        queries = [
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
        ]

    region = get_env("YOUTUBE_REGION_CODE", "IN") or "IN"
    language = get_env("YOUTUBE_LANGUAGE_CODE", "en") or "en"
    pages_per_query = get_int_env("YOUTUBE_SEARCH_PAGES_PER_QUERY", 1)

    ids: list[str] = []
    pages: list[dict[str, Any]] = []

    for query in queries:
        token: str | None = None
        for page_number in range(pages_per_query):
            response = youtube_get(
                "search",
                {
                    "part": "snippet",
                    "q": query,
                    "type": "channel",
                    "maxResults": 50,
                    "regionCode": region,
                    "relevanceLanguage": language,
                    "pageToken": token,
                },
            )
            pages.append({"query": query, "page": page_number + 1, "response": response})
            for item in response.get("items", []):
                channel_id = item.get("id", {}).get("channelId")
                if channel_id and channel_id not in ids:
                    ids.append(channel_id)
                    if len(ids) >= max_creators:
                        break
            if len(ids) >= max_creators:
                break
            token = response.get("nextPageToken")
            if not token:
                break
        if len(ids) >= max_creators:
            break

    return ids, {"used": True, "queries": queries, "pages": pages}


# ============================================================
# ONE CREATOR
# ============================================================


def collect_creator(channel_id: str, discovery: dict[str, Any]) -> dict[str, Any]:
    max_videos = get_int_env("YOUTUBE_MAX_VIDEOS", 20)
    max_playlists = get_int_env("YOUTUBE_MAX_PLAYLISTS", 20)
    max_comments = get_int_env("YOUTUBE_MAX_COMMENT_THREADS", 20)
    max_activities = get_int_env("YOUTUBE_MAX_ACTIVITIES", 20)
    max_sections = get_int_env("YOUTUBE_MAX_CHANNEL_SECTIONS", 20)

    print(f"\nCollecting channel: {channel_id}")

    channel = get_channel(channel_id, discovery)
    channel_resource = channel["resource"]

    if not channel_resource.get("id"):
        return {
            "channel_id": channel_id,
            "channel": channel,
            "uploads_playlist_id": None,
            "playlist_items": {"available": False, "items": [], "error": "Channel unavailable."},
            "videos": [],
            "playlists": {"available": False, "items": [], "error": "Channel unavailable."},
            "comments": {},
            "activities": {"available": False, "items": [], "error": "Channel unavailable."},
            "channel_sections": {"available": False, "items": [], "error": "Channel unavailable."},
        }

    content = channel_resource.get("contentDetails", {})
    related = content.get("relatedPlaylists", {}) if isinstance(content, dict) else {}
    uploads_id = related.get("uploads")

    print("  Channel: OK")

    playlist_items = (
        get_playlist_items(uploads_id, max_videos)
        if uploads_id
        else {"available": False, "items": [], "error": "Uploads playlist ID unavailable."}
    )
    print(f"  Upload playlist items: {len(playlist_items['items'])}")

    video_ids = [item.get("contentDetails", {}).get("videoId") for item in playlist_items["items"]]
    video_ids = [x for x in video_ids if x]

    videos = get_videos(video_ids, discovery)
    print(f"  Videos: {len(videos)}")

    playlists = get_playlists(channel_id, max_playlists)
    print(f"  Playlists: {len(playlists['items'])}")

    comments: dict[str, Any] = {}
    for video_id in video_ids:
        comments[video_id] = get_comment_threads(video_id, max_comments, discovery)

    activities = get_activities(channel_id, max_activities, discovery)
    sections = get_channel_sections(channel_id, max_sections, discovery)

    return {
        "channel_id": channel_id,
        "channel": channel,
        "uploads_playlist_id": uploads_id,
        "playlist_items": {
            "available": playlist_items["available"],
            "items": [normalize(discovery, "PlaylistItem", x) for x in playlist_items["items"]],
            "error": playlist_items["error"],
        },
        "videos": videos,
        "playlists": {
            "available": playlists["available"],
            "items": [normalize(discovery, "Playlist", x) for x in playlists["items"]],
            "error": playlists["error"],
        },
        "comments": comments,
        "activities": activities,
        "channel_sections": sections,
    }


# ============================================================
# MAIN
# ============================================================


def main() -> None:
    print("=" * 80)
    print("BRANDBRIDGE AI")
    print("YOUTUBE DATA API v3")
    print("ALL-FIELD EXPLORER")
    print("=" * 80)

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Root .env exists: {(PROJECT_ROOT / '.env').exists()}")
    print(f"Backend .env exists: {(PROJECT_ROOT / 'backend' / '.env').exists()}")
    print(f"YOUTUBE_API_KEY loaded: {bool(get_api_key())}")

    discovery = get_discovery()
    write_json(DISCOVERY_FILE, discovery)
    print(f"Discovery: {DISCOVERY_FILE}")

    channel_ids, search_metadata = discover_channels()
    print(f"Channels to collect: {len(channel_ids)}")

    reference_resources = get_reference_resources()

    creators: list[dict[str, Any]] = []
    for index, channel_id in enumerate(channel_ids, start=1):
        print(f"\n[{index}/{len(channel_ids)}]")
        creators.append(collect_creator(channel_id, discovery))

    dataset = {
        "metadata": {
            "project": "BrandBridge AI",
            "source": "YouTube Data API v3",
            "collector": "youtube_data_api_all_fields.py",
            "api_base_url": YOUTUBE_API_BASE_URL,
            "discovery_url": DISCOVERY_URL,
"notes": [
    "API key is loaded directly from .env or process environment.",
    (
    "Documented fields missing from a response are represented"
    "null/empty arrays using Discovery schema."
    ),
    (
    "Restricted owner-only fields are attempted independently"
    "retain an error when inaccessible."
    ),
    (
     "Audience demographics are not public YouTube Data API fields; "
     "use YouTube Analytics OAuth for those."
    ),
    "Channel country is channel metadata and does not represent audience geography.",
    (
     "This explorer focuses on creator-related read/list resources; "
     "it does not execute mutating endpoints."
    ),
],
        },
        "collection_config": {
            "max_creators": get_int_env("YOUTUBE_MAX_CREATORS", 100),
            "max_videos": get_int_env("YOUTUBE_MAX_VIDEOS", 20),
            "max_playlists": get_int_env("YOUTUBE_MAX_PLAYLISTS", 20),
            "max_comment_threads": get_int_env("YOUTUBE_MAX_COMMENT_THREADS", 20),
            "max_activities": get_int_env("YOUTUBE_MAX_ACTIVITIES", 20),
            "max_channel_sections": get_int_env("YOUTUBE_MAX_CHANNEL_SECTIONS", 20),
            "region_code": get_env("YOUTUBE_REGION_CODE", "IN"),
            "language_code": get_env("YOUTUBE_LANGUAGE_CODE", "en"),
        },
        "search": search_metadata,
        "reference_resources": reference_resources,
        "creators": creators,
    }

    write_json(OUTPUT_FILE, dataset)

    print("\n" + "=" * 80)
    print("COLLECTION COMPLETE")
    print("=" * 80)
    print(f"Creators: {len(creators)}")
    print(f"Output:   {OUTPUT_FILE}")
    print(f"Schema:   {DISCOVERY_FILE}")
    print("=" * 80)


if __name__ == "__main__":
    main()
