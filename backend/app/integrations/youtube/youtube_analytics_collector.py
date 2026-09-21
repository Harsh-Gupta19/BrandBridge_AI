import json
from datetime import date, timedelta
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

TOKEN_FILE = BASE_DIR / "oauth" / "token.json"

OUTPUT_DIR = (BASE_DIR / "../../../../data/raw/youtube/analytics").resolve()

OUTPUT_FILE = OUTPUT_DIR / "youtube_analytics_data.json"

API_SERVICE_NAME = "youtubeAnalytics"
API_VERSION = "v2"


# ============================================================
# DATE RANGE
# ============================================================

END_DATE = date.today()

# YouTube Analytics data can have processing latency
# Use a safe historical range for the first test.
START_DATE = END_DATE - timedelta(days=30)


# ============================================================
# AUTHENTICATION
# ============================================================


def get_credentials():

    if not TOKEN_FILE.exists():
        raise FileNotFoundError(f"Token file not found: {TOKEN_FILE}")

    credentials = Credentials.from_authorized_user_file(str(TOKEN_FILE))

    return credentials


# ============================================================
# YOUTUBE ANALYTICS SERVICE
# ============================================================


def get_analytics_service():

    credentials = get_credentials()

    service = build(
        API_SERVICE_NAME,
        API_VERSION,
        credentials=credentials,
    )

    return service


# ============================================================
# BASIC CHANNEL ANALYTICS
# ============================================================


def get_channel_overview(service):

    print("\n" + "=" * 70)
    print("YOUTUBE ANALYTICS - CHANNEL OVERVIEW")
    print("=" * 70)

    response = (
        service.reports()
        .query(
            ids="channel==MINE",
            startDate=START_DATE.isoformat(),
            endDate=END_DATE.isoformat(),
            metrics=(
                "views,"
                "likes,"
                "comments,"
                "shares,"
                "estimatedMinutesWatched,"
                "averageViewDuration,"
                "subscribersGained,"
                "subscribersLost"
            ),
        )
        .execute()
    )

    return response


# ============================================================
# SAVE
# ============================================================


def save_json(data):

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

    print(f"\nSaved to:\n{OUTPUT_FILE}")


# ============================================================
# MAIN
# ============================================================


def main():

    print("\n")
    print("=" * 70)
    print("BRANDBRIDGE AI")
    print("YOUTUBE ANALYTICS API")
    print("=" * 70)

    print(f"\nDate range:\n{START_DATE} → {END_DATE}")

    try:
        service = get_analytics_service()

        response = get_channel_overview(service)

        output = {
            "source": "YouTube Analytics API",
            "api_version": API_VERSION,
            "channel": "channel==MINE",
            "start_date": START_DATE.isoformat(),
            "end_date": END_DATE.isoformat(),
            "report": response,
        }

        save_json(output)

        print("\n" + "=" * 70)
        print("SUCCESS")
        print("=" * 70)

        print(
            json.dumps(
                response,
                indent=2,
                ensure_ascii=False,
            )
        )

    except HttpError as exc:
        print("\nYouTube Analytics API ERROR:")
        print(exc)

        raise

    except Exception as exc:
        print("\nERROR:")
        print(exc)

        raise


if __name__ == "__main__":
    main()
