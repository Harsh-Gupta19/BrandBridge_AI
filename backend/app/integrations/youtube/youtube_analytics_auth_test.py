from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = [
     "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
]


BASE_DIR = Path(__file__).resolve().parent

CLIENT_SECRET_FILE = (
    BASE_DIR
    / "oauth"
    / "client_secret.json"
)

TOKEN_FILE = (
    BASE_DIR
    / "oauth"
    / "token.json"
)


def main():

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRET_FILE),
        SCOPES,
    )

    credentials = flow.run_local_server(
        port=0
    )

    # Save OAuth credentials
    TOKEN_FILE.write_text(
        credentials.to_json(),
        encoding="utf-8",
    )

    print("\nOAuth authorization successful.")
    print("Credentials saved successfully.")
    print(f"Token file: {TOKEN_FILE}")

    if credentials.token:
        print(
            "Access token:",
            credentials.token[:10] + "..."
        )

    if credentials.refresh_token:
        print("Refresh token: available")
    else:
        print("Refresh token: not available")


if __name__ == "__main__":
    main()