"""Uploads a finished video + thumbnail to YouTube with the YouTube Data API v3."""

import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]
HERE = Path(__file__).parent
CLIENT_SECRET = HERE / "client_secret.json"
TOKEN_FILE = HERE / "youtube_token.json"


def setup_youtube_login() -> None:
    """One-time: opens a browser to log in to your YouTube channel and saves a token."""
    if not CLIENT_SECRET.exists():
        raise SystemExit(f"Put your Google OAuth 'Desktop app' client file at {CLIENT_SECRET} first (see README).")
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    TOKEN_FILE.write_text(creds.to_json())
    print(f"Saved login to {TOKEN_FILE}.")
    print("For GitHub Actions, copy that file's full contents into a repo secret named YOUTUBE_TOKEN_JSON.")


def _credentials() -> Credentials:
    raw = os.environ.get("YOUTUBE_TOKEN_JSON")
    if raw:
        info = json.loads(raw)
    elif TOKEN_FILE.exists():
        info = json.loads(TOKEN_FILE.read_text())
    else:
        raise RuntimeError("No YouTube login found. Run `python -m youtube_agent.main --setup-youtube` first.")
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    if not creds.valid:
        creds.refresh(Request())
    return creds


def _check_channel(youtube, expected_id: str | None) -> None:
    """Refuse to upload if the saved login belongs to a different channel."""
    if not expected_id:
        return
    items = youtube.channels().list(part="id,snippet", mine=True).execute().get("items", [])
    ids = [c["id"] for c in items]
    if expected_id not in ids:
        names = ", ".join(f"{c['snippet']['title']} ({c['id']})" for c in items) or "no channel"
        raise RuntimeError(
            f"Logged in to {names}, but config.yaml expects channel {expected_id}. "
            "Run --setup-youtube again and sign in as healthsupportstudio@gmail.com."
        )


def upload_video(video_path: Path, thumbnail_path: Path | None, title: str, description: str,
                 tags: list[str], yt: dict, language_code: str = "en-US") -> str:
    youtube = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    _check_channel(youtube, yt.get("channel_id"))
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags,
            "categoryId": yt.get("category_id", "27"),
            "defaultLanguage": language_code,
            "defaultAudioLanguage": language_code,
        },
        "status": {
            "privacyStatus": yt.get("privacy", "public"),
            "selfDeclaredMadeForKids": bool(yt.get("made_for_kids", False)),
            "containsSyntheticMedia": bool(yt.get("contains_synthetic_media", True)),
        },
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Uploading... {int(status.progress() * 100)}%")
    video_id = response["id"]
    print(f"  Uploaded: https://youtu.be/{video_id}")

    if thumbnail_path and thumbnail_path.exists():
        try:
            youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumbnail_path))).execute()
        except HttpError as e:
            # Custom thumbnails need a phone-verified channel; the video is still published.
            print(f"  Could not set thumbnail (verify your channel at youtube.com/verify): {e.reason}")
    return video_id
