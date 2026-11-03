"""Uploads the finished Ali aur Dadu videos in islamic_channel/upload_queue/ to the Islamic YouTube channel.

Each video is a folder: video.mp4, meta.json ({"title", "description", "tags"}, optional "publish_at"
as an ISO UTC time) and optionally thumbnail.jpg. A folder that has uploaded.json is done.
Without publish_at the video is scheduled for the next 7:30 PM India time that is at least 2 hours away,
so the owner can check it in YouTube Studio first (set it to Private to stop it).
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from youtube_agent.uploader import add_to_playlists, upload_video

HERE = Path(__file__).parent
QUEUE = HERE / "upload_queue"
CONFIG = json.loads((HERE / "config.json").read_text())


def next_slot(now: datetime) -> str:
    hour, minute = CONFIG["publish_utc"]
    slot = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    while slot < now + timedelta(hours=2):
        slot += timedelta(days=1)
    return slot.strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    pending = sorted(d for d in QUEUE.iterdir() if d.is_dir() and not (d / "uploaded.json").exists()) \
        if QUEUE.exists() else []
    if not pending:
        print("Nothing to upload.")
        return 0
    failed = 0
    for folder in pending:
        meta = json.loads((folder / "meta.json").read_text())
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
    sys.exit(main())
