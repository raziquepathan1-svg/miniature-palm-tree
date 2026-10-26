"""Make videos public right away instead of at their scheduled time. Run by the "Publish now" workflow.

    python -m youtube_agent.publish_now VIDEO_ID [VIDEO_ID ...]
"""

import datetime as dt
import sys

from .main import load_history, save_history


def main() -> None:
    from googleapiclient.discovery import build

    from .uploader import _credentials

    ids = [i for a in sys.argv[1:] for i in a.replace(",", " ").split()]
    if not ids:
        sys.exit("Give the video IDs to publish.")
    youtube = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    history = load_history()
    for vid in ids:
        item = youtube.videos().list(part="status", id=vid).execute()["items"][0]
        status = dict(item["status"])  # keep every other setting (made-for-kids, AI label...)
        status["privacyStatus"] = "public"
        for key in ("publishAt", "uploadStatus", "failureReason", "rejectionReason"):
            status.pop(key, None)
        youtube.videos().update(part="status", body={"id": vid, "status": status}).execute()
        print(f"Public now: https://youtu.be/{vid}")
        for h in history:
            if h.get("youtube_id") == vid:
                h["publish_at"] = now
                h["awaiting_approval"] = False
    save_history(history)


if __name__ == "__main__":
    main()
