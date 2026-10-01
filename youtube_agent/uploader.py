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
    refresh = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    if refresh:  # browser-only setup (Google OAuth Playground): three separate secrets
        info = {
            "client_id": os.environ["YOUTUBE_CLIENT_ID"].strip(),
            "client_secret": os.environ["YOUTUBE_CLIENT_SECRET"].strip(),
            "refresh_token": refresh.strip(),
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    elif raw:
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
            "Get a new YouTube login (refresh token) while signed in to the right channel's Google account."
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
    if yt.get("publish_at"):  # scheduled publish: must be uploaded as private
        body["status"]["privacyStatus"] = "private"
        body["status"]["publishAt"] = yt["publish_at"]
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


def add_to_playlists(video_id: str, playlist_titles: list[str], about: str | None = None) -> None:
    """Add a video to playlists by title, creating any public playlist that doesn't exist yet."""
    try:
        youtube = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
        existing = {}
        request = youtube.playlists().list(part="snippet", mine=True, maxResults=50)
        while request is not None:
            response = request.execute()
            for item in response.get("items", []):
                existing[item["snippet"]["title"].strip().lower()] = item["id"]
            request = youtube.playlists().list_next(request, response)
        for title in dict.fromkeys(t.strip() for t in playlist_titles if t and t.strip()):
            playlist_id = existing.get(title.lower())
            if not playlist_id:
                created = youtube.playlists().insert(
                    part="snippet,status",
                    body={"snippet": {"title": title, "description": (
                              about or "Health Support Studio: {title}. Educational only, not medical advice."
                          ).format(title=title)},
                          "status": {"privacyStatus": "public"}},
                ).execute()
                playlist_id = existing[title.lower()] = created["id"]
                print(f"  Created playlist: {title}")
            youtube.playlistItems().insert(
                part="snippet",
                body={"snippet": {"playlistId": playlist_id,
                                  "resourceId": {"kind": "youtube#video", "videoId": video_id}}},
            ).execute()
            print(f"  Added to playlist: {title}")
    except Exception as e:  # playlists are nice-to-have; never fail the upload for them
        print(f"  (Could not update playlists: {e})")
