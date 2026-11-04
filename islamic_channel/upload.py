"""Uploads the finished Ali aur Dadu videos in islamic_channel/upload_queue/ to the Hidaya YouTube channel (the Islamic channel).

Each video is a folder: video.mp4, meta.json ({"title", "description", "tags"}, optional "publish_at"
as an ISO UTC time) and optionally thumbnail.jpg. A folder that has uploaded.json is done.
Without publish_at the video is scheduled for the next 7:30 PM India time that is at least 2 hours away,
so the owner can check it in YouTube Studio first (set it to Private to stop it).
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from googleapiclient.discovery import build

from youtube_agent.uploader import _credentials, add_to_playlists, upload_video

HERE = Path(__file__).parent
QUEUE = HERE / "upload_queue"
CONFIG = json.loads((HERE / "config.json").read_text())
# e.g. "Sahih Bukhari 6224", "Sunan Abu Dawud 3767", "Jami at-Tirmidhi 1858", "Surah An-Nisa 4:86"
SOURCE = re.compile(r"\b(Sahih|Sunan|Jami|Muwatta|Musnad|Riyad)\b[^\n]*\d|\bSurah\b[^\n]*\d+:\d+")


def next_slot(now: datetime) -> str:
    hour, minute = CONFIG["publish_utc"]
    slot = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    while slot < now + timedelta(hours=2):
        slot += timedelta(days=1)
    return slot.strftime("%Y-%m-%dT%H:%M:%SZ")


def check_login() -> int:
    """Shows which channel the saved login uploads to, without uploading anything."""
    youtube = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    items = youtube.channels().list(part="id,snippet,statistics", mine=True).execute().get("items", [])
    lines = [f"- **{c['snippet']['title']}** ({c['id']}), {c['statistics'].get('subscriberCount', '?')} subscribers"
             for c in items] or ["- no channel"]
    print("\n".join(lines))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write("## The login uploads to\n" + "\n".join(lines) + "\n")
    return 0 if items else 1


def main() -> int:
    pending = sorted(d for d in QUEUE.iterdir() if d.is_dir() and not (d / "uploaded.json").exists()) \
        if QUEUE.exists() else []
    if not pending:
        print("Nothing to upload.")
        return 0
    if not CONFIG.get("channel_id"):  # never upload to the wrong channel (the first login was Health Support Studio)
        print("Put Hidaya's channel ID (starts with UC) in islamic_channel/config.json first. Nothing was uploaded.")
        return 1
    failed = 0
    for folder in pending:
        meta = json.loads((folder / "meta.json").read_text())
        if not SOURCE.search(meta["description"]):  # owner's rule: book + number in every description
            print(f"{folder.name}: SKIPPED - the description has no hadith book/number or Surah reference.")
            failed += 1
            continue
        publish_at = meta.get("publish_at") or next_slot(datetime.now(timezone.utc))
        yt = {
            "channel_id": CONFIG.get("channel_id") or None,
            "category_id": "27",  # Education
            "made_for_kids": CONFIG["made_for_kids"],
            "contains_synthetic_media": True,  # AI-made cartoon
            "publish_at": publish_at,
        }
        print(f"{folder.name}: uploading, goes public {publish_at}")
        try:
            video_id = upload_video(folder / "video.mp4", folder / "thumbnail.jpg", meta["title"],
                                    meta["description"], meta.get("tags", []), yt, language_code="hi")
        except Exception as e:  # keep going with the other videos
            print(f"  FAILED: {e}")
            failed += 1
            continue
        add_to_playlists(video_id, [CONFIG["playlist"]], about=CONFIG["playlist_about"])
        (folder / "uploaded.json").write_text(json.dumps(
            {"video_id": video_id, "url": f"https://youtu.be/{video_id}", "publish_at": publish_at}, indent=2) + "\n")
        print(f"  Done: https://youtu.be/{video_id}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(check_login() if "--check" in sys.argv else main())
