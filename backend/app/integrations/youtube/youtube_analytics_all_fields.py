import json
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ============================================================
# BRAND BRIDGE AI
# YOUTUBE ANALYTICS - ALL FIELD / REPORT EXPLORER
# ============================================================
#
# This collector is designed for API learning and exploration.
#
# It:
#   1. Tests documented YouTube Analytics metrics.
#   2. Tests multiple report/dimension combinations.
#   3. Stores actual API results.
#   4. Stores null when a field/report is unavailable.
#   5. Stores the API error/reason separately.
#
# IMPORTANT:
# YouTube Analytics does not support fields=*.
# Metrics are only valid with certain dimensions/reports
#
# Official documentation:
# https://developers.google.com/youtube/analytics/channel_reports
# ============================================================


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

TOKEN_FILE = BASE_DIR / "oauth" / "token.json"

PROJECT_ROOT = BASE_DIR.parents[4]

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "youtube" / "analytics"

OUTPUT_FILE = OUTPUT_DIR / "youtube_analytics_all_fields.json"


# ============================================================
# CONFIGURATION
# ============================================================

ANALYTICS_SERVICE_NAME = "youtubeAnalytics"
ANALYTICS_VERSION = "v2"

YOUTUBE_SERVICE_NAME = "youtube"
YOUTUBE_VERSION = "v3"

# Analytics data can have processing delay.
# Use a historical range rather than today.
END_DATE = date.today() - timedelta(days=3)

START_DATE = END_DATE - timedelta(days=30)

MAX_TOP_RESULTS = 200

REQUEST_DELAY_SECONDS = 0.15


# ============================================================
# METRICS
# ============================================================
#
# These are the documented channel-report metrics currently
# relevant to the report families used by this collector.
#
# Monetary metrics are included separately because they require
# the monetary OAuth scope + monetization eligibility.
# ============================================================

GENERAL_METRICS = [
    "engagedViews",
    "views",
    "redViews",
    "comments",
    "likes",
    "dislikes",
    "videosAddedToPlaylists",
    "videosRemovedFromPlaylists",
    "shares",
    "estimatedMinutesWatched",
    "estimatedRedMinutesWatched",
    "averageViewDuration",
    "averageViewPercentage",
    "annotationClickThroughRate",
    "annotationCloseRate",
    "annotationImpressions",
    "annotationClickableImpressions",
    "annotationClosableImpressions",
    "annotationClicks",
    "annotationCloses",
    "cardClickRate",
    "cardTeaserClickRate",
    "cardImpressions",
    "cardTeaserImpressions",
    "cardClicks",
    "cardTeaserClicks",
    "subscribersGained",
    "subscribersLost",
    "uniques",
]


MONETARY_METRICS = [
    "estimatedRevenue",
    "estimatedAdRevenue",
    "grossRevenue",
    "estimatedRedPartnerRevenue",
    "monetizedPlaybacks",
    "playbackBasedCpm",
    "adImpressions",
    "cpm",
]


RETENTION_METRICS = [
    "audienceWatchRatio",
    "relativeRetentionPerformance",
    "startedWatching",
    "stoppedWatching",
    "totalSegmentImpressions",
]


LIVE_METRICS = [
    "averageConcurrentViewers",
    "peakConcurrentViewers",
]


PLAYLIST_METRICS = [
    "engagedViews",
    "views",
    "estimatedMinutesWatched",
    "averageViewDuration",
    "averageTimeInPlaylist",
    "playlistAverageViewDuration",
    "playlistEstimatedMinutesWatched",
    "playlistSaves",
    "playlistStarts",
    "playlistViews",
    "viewsPerPlaylistStart",
]


DEMOGRAPHIC_METRICS = [
    "viewerPercentage",
]


SHARING_METRICS = [
    "shares",
]


AD_METRICS = [
    "grossRevenue",
    "adImpressions",
    "cpm",
]


MEMBERSHIP_METRICS = [
    "membershipsCancellationSurveyResponses",
]


# ============================================================
# DIMENSIONS
# ============================================================

DIMENSIONS = [
    "day",
    "month",
    "video",
    "playlist",
    "country",
    "continent",
    "subContinent",
    "province",
    "city",
    "dma",
    "creatorContentType",
    "liveOrOnDemand",
    "subscribedStatus",
    "youtubeProduct",
    "insightPlaybackLocationType",
    "insightPlaybackLocationDetail",
    "insightTrafficSourceType",
    "insightTrafficSourceDetail",
    "deviceType",
    "operatingSystem",
    "ageGroup",
    "gender",
    "sharingService",
    "elapsedVideoTimeRatio",
    "livestreamPosition",
    "membershipsCancellationSurveyReason",
    "adType",
]


# ============================================================
# DOCUMENTED REPORT DEFINITIONS
# ============================================================
#
# Each report defines:
#
#   name
#   dimensions
#   metrics
#   optional filters
#   optional sort
#   optional maxResults
#
# We deliberately test metrics individually.
#
# This prevents one unsupported metric from making an entire
# report fail.
# ============================================================

REPORTS = [
    # --------------------------------------------------------
    # BASIC CHANNEL TOTALS
    # --------------------------------------------------------
    {
        "name": "channel_overview",
        "dimensions": "",
        "metrics": GENERAL_METRICS + MONETARY_METRICS,
    },
    # --------------------------------------------------------
    # DAILY ACTIVITY
    # --------------------------------------------------------
    {
        "name": "daily_activity",
        "dimensions": "day",
        "metrics": GENERAL_METRICS + MONETARY_METRICS,
    },
    # --------------------------------------------------------
    # MONTHLY ACTIVITY
    # --------------------------------------------------------
    {
        "name": "monthly_activity",
        "dimensions": "month",
        "metrics": GENERAL_METRICS + MONETARY_METRICS,
    },
    # --------------------------------------------------------
    # COUNTRY
    # --------------------------------------------------------
    {
        "name": "country_activity",
        "dimensions": "country",
        "metrics": GENERAL_METRICS + MONETARY_METRICS,
    },
    # --------------------------------------------------------
    # CITY
    # --------------------------------------------------------
    {
        "name": "city_activity",
        "dimensions": "city",
        "metrics": [
            "engagedViews",
            "views",
            "estimatedMinutesWatched",
            "averageViewDuration",
            "averageViewPercentage",
        ],
        "sort": "-views",
        "maxResults": 250,
    },
    # --------------------------------------------------------
    # DMA
    # --------------------------------------------------------
    {
        "name": "dma_activity",
        "dimensions": "dma",
        "metrics": [
            "engagedViews",
            "views",
            "estimatedMinutesWatched",
            "averageViewDuration",
            "averageViewPercentage",
        ],
        "filters": "country==US",
        "sort": "-views",
    },
    # --------------------------------------------------------
    # US PROVINCES
    # --------------------------------------------------------
    {
        "name": "province_activity",
        "dimensions": "province",
        "metrics": [
            "engagedViews",
            "views",
            "redViews",
            "estimatedMinutesWatched",
            "estimatedRedMinutesWatched",
            "averageViewDuration",
            "averageViewPercentage",
            "annotationClickThroughRate",
            "annotationCloseRate",
            "annotationImpressions",
            "annotationClickableImpressions",
            "annotationClosableImpressions",
            "annotationClicks",
            "annotationCloses",
            "cardClickRate",
            "cardTeaserClickRate",
            "cardImpressions",
            "cardTeaserImpressions",
            "cardClicks",
            "cardTeaserClicks",
        ],
        "filters": "country==US",
    },
    # --------------------------------------------------------
    # PLAYBACK LOCATION
    # --------------------------------------------------------
    {
        "name": "playback_location",
        "dimensions": "insightPlaybackLocationType",
        "metrics": [
            "engagedViews",
            "views",
            "estimatedMinutesWatched",
        ],
    },
    # --------------------------------------------------------
    # TRAFFIC SOURCE
    # --------------------------------------------------------
    {
        "name": "traffic_source",
        "dimensions": "insightTrafficSourceType",
        "metrics": [
            "engagedViews",
            "views",
            "estimatedMinutesWatched",
        ],
    },
    # --------------------------------------------------------
    # DEVICE
    # --------------------------------------------------------
    {
        "name": "device_type",
        "dimensions": "deviceType",
        "metrics": [
            "engagedViews",
            "views",
            "estimatedMinutesWatched",
        ],
    },
    # --------------------------------------------------------
    # OPERATING SYSTEM
    # --------------------------------------------------------
    {
        "name": "operating_system",
        "dimensions": "operatingSystem",
        "metrics": [
            "engagedViews",
            "views",
            "estimatedMinutesWatched",
        ],
    },
    # --------------------------------------------------------
    # DEVICE + OS
    # --------------------------------------------------------
    {
        "name": "device_operating_system",
        "dimensions": "deviceType,operatingSystem",
        "metrics": [
            "engagedViews",
            "views",
            "estimatedMinutesWatched",
        ],
    },
    # --------------------------------------------------------
    # DEMOGRAPHICS
    # --------------------------------------------------------
    {
        "name": "viewer_demographics",
        "dimensions": "ageGroup,gender",
        "metrics": DEMOGRAPHIC_METRICS,
    },
    # --------------------------------------------------------
    # SHARING SERVICE
    # --------------------------------------------------------
    {
        "name": "sharing_service",
        "dimensions": "sharingService",
        "metrics": SHARING_METRICS,
    },
    # --------------------------------------------------------
    # PLAYBACK DETAILS
    # --------------------------------------------------------
    {
        "name": "playback_live_on_demand",
        "dimensions": ("liveOrOnDemand"),
        "metrics": [
            "engagedViews",
            "views",
            "redViews",
            "estimatedMinutesWatched",
            "estimatedRedMinutesWatched",
            "averageViewDuration",
        ],
    },
    {
        "name": "playback_average_percentage",
        "dimensions": ("subscribedStatus"),
        "metrics": [
            "engagedViews",
            "views",
            "redViews",
            "estimatedMinutesWatched",
            "estimatedRedMinutesWatched",
            "averageViewDuration",
            "averageViewPercentage",
        ],
    },
    # --------------------------------------------------------
    # TOP VIDEOS
    # --------------------------------------------------------
    {
        "name": "top_videos",
        "dimensions": "video",
        "metrics": GENERAL_METRICS + MONETARY_METRICS,
        "sort": "-views",
        "maxResults": 200,
    },
    # --------------------------------------------------------
    # TOP VIDEOS BY PRODUCT
    # --------------------------------------------------------
    {
        "name": "top_videos_by_product",
        "dimensions": "video",
        "metrics": [
            "engagedViews",
            "views",
            "redViews",
            "estimatedMinutesWatched",
            "estimatedRedMinutesWatched",
            "averageViewDuration",
            "averageViewPercentage",
        ],
        "sort": "-views",
        "maxResults": 200,
    },
    # --------------------------------------------------------
    # PLAYLIST BASIC
    #
    # Playlist filter is inserted dynamically.
    # --------------------------------------------------------
    {
        "name": "playlist_basic",
        "dimensions": "",
        "metrics": PLAYLIST_METRICS,
        "requires_playlist": True,
    },
    # --------------------------------------------------------
    # PLAYLIST TIME
    # --------------------------------------------------------
    {
        "name": "playlist_daily",
        "dimensions": "day",
        "metrics": PLAYLIST_METRICS,
        "requires_playlist": True,
    },
    # --------------------------------------------------------
    # PLAYLIST COUNTRY
    # --------------------------------------------------------
    {
        "name": "playlist_country",
        "dimensions": "country",
        "metrics": [
            "engagedViews",
            "views",
            "estimatedMinutesWatched",
            "averageViewDuration",
        ],
        "requires_playlist": True,
    },
    # --------------------------------------------------------
    # PLAYLIST DEVICE
    # --------------------------------------------------------
    {
        "name": "playlist_device",
        "dimensions": "deviceType",
        "metrics": PLAYLIST_METRICS,
        "requires_playlist": True,
    },
    # --------------------------------------------------------
    # PLAYLIST OPERATING SYSTEM
    # --------------------------------------------------------
    {
        "name": "playlist_operating_system",
        "dimensions": "operatingSystem",
        "metrics": PLAYLIST_METRICS,
        "requires_playlist": True,
    },
    # --------------------------------------------------------
    # PLAYLIST DEVICE + OS
    # --------------------------------------------------------
    {
        "name": "playlist_device_os",
        "dimensions": ("deviceType,operatingSystem"),
        "metrics": PLAYLIST_METRICS,
        "requires_playlist": True,
    },
    # --------------------------------------------------------
    # PLAYLIST DEMOGRAPHICS
    # --------------------------------------------------------
    {
        "name": "playlist_demographics",
        "dimensions": "ageGroup,gender",
        "metrics": DEMOGRAPHIC_METRICS,
        "requires_playlist": True,
    },
    # --------------------------------------------------------
    # MEMBERSHIP CANCELLATIONS
    # --------------------------------------------------------
    {
        "name": "membership_cancellations",
        "dimensions": ("membershipsCancellationSurveyReason"),
        "metrics": MEMBERSHIP_METRICS,
    },
    # --------------------------------------------------------
    # AD PERFORMANCE
    # --------------------------------------------------------
    {
        "name": "ad_performance",
        "dimensions": "adType",
        "metrics": AD_METRICS,
    },
    # --------------------------------------------------------
    # DAILY AD PERFORMANCE
    # --------------------------------------------------------
    {
        "name": "daily_ad_performance",
        "dimensions": "adType,day",
        "metrics": AD_METRICS,
    },
    # --------------------------------------------------------
    # AUDIENCE RETENTION
    #
    # Requires a real video ID.
    # --------------------------------------------------------
    {
        "name": "audience_retention",
        "dimensions": "elapsedVideoTimeRatio",
        "metrics": RETENTION_METRICS,
        "requires_video": True,
    },
    # --------------------------------------------------------
    # LIVESTREAM CONCURRENT VIEWERS
    #
    # Requires a livestream video.
    # --------------------------------------------------------
    {
        "name": "livestream_concurrent_viewers",
        "dimensions": "livestreamPosition",
        "metrics": LIVE_METRICS,
        "requires_video": True,
    },
]


# ============================================================
# AUTHENTICATION
# ============================================================


def get_credentials() -> Credentials:

    if not TOKEN_FILE.exists():
        raise FileNotFoundError(
            f"OAuth token not found:\n{TOKEN_FILE}\n\nRun the OAuth authorization script first."
        )

    credentials = Credentials.from_authorized_user_file(str(TOKEN_FILE))

    return credentials


def get_analytics_service():

    credentials = get_credentials()

    return build(
        ANALYTICS_SERVICE_NAME,
        ANALYTICS_VERSION,
        credentials=credentials,
    )


def get_youtube_service():

    credentials = get_credentials()

    return build(
        YOUTUBE_SERVICE_NAME,
        YOUTUBE_VERSION,
        credentials=credentials,
    )


# ============================================================
# YOUTUBE CHANNEL INFORMATION
# ============================================================


def get_channel_information(
    youtube_service,
) -> dict[str, Any]:

    response = (
        youtube_service.channels()
        .list(
            part="snippet,contentDetails,statistics",
            mine=True,
        )
        .execute()
    )

    items = response.get(
        "items",
        [],
    )

    if not items:
        return {
            "channel_id": None,
            "channel_title": None,
            "uploads_playlist_id": None,
            "statistics": {},
        }

    channel = items[0]

    return {
        "channel_id": channel.get("id"),
        "channel_title": (channel.get("snippet", {}).get("title")),
        "uploads_playlist_id": (
            channel.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
        ),
        "statistics": (channel.get("statistics", {})),
    }


# ============================================================
# GET VIDEO ID
# ============================================================


def get_latest_video_id(
    youtube_service,
    uploads_playlist_id: str | None,
) -> str | None:

    if not uploads_playlist_id:
        return None

    response = (
        youtube_service.playlistItems()
        .list(
            part="contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=1,
        )
        .execute()
    )

    items = response.get(
        "items",
        [],
    )

    if not items:
        return None

    return items[0].get("contentDetails", {}).get("videoId")


# ============================================================
# API QUERY
# ============================================================


def execute_query(
    service,
    report: dict[str, Any],
    metric: str,
    video_id: str | None = None,
    playlist_id: str | None = None,
) -> dict[str, Any]:

    params = {
        "ids": "channel==MINE",
        "startDate": START_DATE.isoformat(),
        "endDate": END_DATE.isoformat(),
        "metrics": metric,
    }

    dimensions = report.get("dimensions")

    if dimensions:
        params["dimensions"] = dimensions

    filters = []

    if report.get("requires_video"):
        if not video_id:
            raise ValueError("No video available.")

        filters.append(f"video=={video_id}")

    if report.get("requires_playlist"):
        if not playlist_id:
            raise ValueError("No playlist available.")

        filters.append(f"playlist=={playlist_id}")

    if report.get("filters"):
        filters.append(report["filters"])

    if filters:
        params["filters"] = ";".join(filters)

    if report.get("sort"):
        params["sort"] = report["sort"]

    if report.get("maxResults"):
        params["maxResults"] = report["maxResults"]

    response = service.reports().query(**params).execute()

    return response


# ============================================================
# RUN ONE METRIC
# ============================================================


def run_metric(
    service,
    report: dict[str, Any],
    metric: str,
    video_id: str | None,
    playlist_id: str | None,
) -> dict[str, Any]:

    try:
        response = execute_query(
            service=service,
            report=report,
            metric=metric,
            video_id=video_id,
            playlist_id=playlist_id,
        )

        headers = response.get(
            "columnHeaders",
            [],
        )

        rows = response.get(
            "rows",
            [],
        )

        return {
            "available": True,
            "value": rows,
            "column_headers": headers,
            "error": None,
        }

    except ValueError as exc:
        return {
            "available": False,
            "value": None,
            "column_headers": [],
            "error": str(exc),
        }

    except HttpError as exc:
        return {
            "available": False,
            "value": None,
            "column_headers": [],
            "error": str(exc),
        }

    except Exception as exc:
        return {
            "available": False,
            "value": None,
            "column_headers": [],
            "error": str(exc),
        }


# ============================================================
# RUN REPORT
# ============================================================


def run_report(
    service,
    report: dict[str, Any],
    video_id: str | None,
    playlist_id: str | None,
) -> dict[str, Any]:

    print("\n" + "-" * 70)
    print(f"REPORT: {report['name']}")
    print("-" * 70)

    results = {}

    for metric in report["metrics"]:
        print(f"Testing metric: {metric}")

        result = run_metric(
            service=service,
            report=report,
            metric=metric,
            video_id=video_id,
            playlist_id=playlist_id,
        )

        results[metric] = result

        if result["available"]:
            print("  [AVAILABLE]")

        else:
            print("  [NULL]")

        time.sleep(REQUEST_DELAY_SECONDS)

    return {
        "dimensions": report.get("dimensions", ""),
        "results": results,
    }


# ============================================================
# FIELD STATUS
# ============================================================


def build_metric_catalog(
    report_results: dict[str, Any],
) -> dict[str, Any]:

    catalog = {}

    for report_name, report_data in report_results.items():
        for metric, result in report_data.get("results", {}).items():
            if metric not in catalog:
                catalog[metric] = {
                    "tested": True,
                    "available": False,
                    "reports": [],
                }

            if result.get("available"):
                catalog[metric]["available"] = True

            catalog[metric]["reports"].append(
                {
                    "report": report_name,
                    "available": result.get("available"),
                    "error": result.get("error"),
                }
            )

    return catalog


# ============================================================
# DIMENSION CATALOG
# ============================================================


def build_dimension_catalog() -> dict[str, Any]:

    return {
        dimension: {
            "documented": True,
            "tested": False,
            "value": None,
        }
        for dimension in DIMENSIONS
    }


# ============================================================
# MAIN
# ============================================================


def main():

    print("\n")
    print("=" * 70)
    print("BRANDBRIDGE AI")
    print("YOUTUBE ANALYTICS")
    print("ALL FIELD / REPORT EXPLORER")
    print("=" * 70)

    print(f"\nDate range:\n{START_DATE} -> {END_DATE}")

    print(
        "\nNOTE:"
        "\nYouTube Analytics metrics have"
        "\nreport-specific compatibility rules."
        "\nEach metric is therefore tested separately."
    )

    # --------------------------------------------------------
    # Services
    # --------------------------------------------------------

    analytics_service = get_analytics_service()

    youtube_service = get_youtube_service()

    # --------------------------------------------------------
    # Channel
    # --------------------------------------------------------

    channel = get_channel_information(youtube_service)

    print(f"\nChannel: {channel.get('channel_title')}")

    print(f"Channel ID: {channel.get('channel_id')}")

    # --------------------------------------------------------
    # Video
    # --------------------------------------------------------

    latest_video_id = get_latest_video_id(
        youtube_service,
        channel.get("uploads_playlist_id"),
    )

    print(f"\nLatest video: {latest_video_id}")

    # --------------------------------------------------------
    # Run reports
    # --------------------------------------------------------

    report_results = {}

    for report in REPORTS:
        result = run_report(
            service=analytics_service,
            report=report,
            video_id=latest_video_id,
            playlist_id=channel.get("uploads_playlist_id"),
        )

        report_results[report["name"]] = result

    # --------------------------------------------------------
    # Catalog
    # --------------------------------------------------------

    metric_catalog = build_metric_catalog(report_results)

    dimension_catalog = build_dimension_catalog()

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    available_metrics = [name for name, info in metric_catalog.items() if info["available"]]

    unavailable_metrics = [name for name, info in metric_catalog.items() if not info["available"]]

    # --------------------------------------------------------
    # Final JSON
    # --------------------------------------------------------

    output = {
        "source": "YouTube Analytics API",
        "api_version": ANALYTICS_VERSION,
        "collector": "BrandBridge AI",
        "collector_type": "all_field_explorer",
        "collected_at": date.today().isoformat(),
        "date_range": {
            "start": START_DATE.isoformat(),
            "end": END_DATE.isoformat(),
        },
        "channel": channel,
        "test_video_id": latest_video_id,
        "documented_dimensions": dimension_catalog,
        "metric_catalog": {
            "total_tested": len(metric_catalog),
            "available": available_metrics,
            "unavailable": unavailable_metrics,
            "details": metric_catalog,
        },
        "reports": report_results,
    }

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # Console summary
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("COLLECTION COMPLETE")
    print("=" * 70)

    print(f"\nMetrics tested: {len(metric_catalog)}")

    print(f"Available: {len(available_metrics)}")

    print(f"Unavailable: {len(unavailable_metrics)}")

    print("\nOutput:")

    print(OUTPUT_FILE.resolve())


if __name__ == "__main__":
    main()
