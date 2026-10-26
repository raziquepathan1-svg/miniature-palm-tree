"""Make videos public right away instead of at their scheduled time. Run by the "Publish now" workflow.

    python -m youtube_agent.publish_now VIDEO_ID [VIDEO_ID ...]

Our API project may not switch a video to public directly (YouTube answers "public" but keeps it private),
but it may schedule: so each video is rescheduled a few minutes from now and YouTube publishes it then.
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
    when = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=3)).strftime("%Y-%m-%dT%H:%M:00Z")
    history = load_history()
    failed = []
    for vid in ids:
        item = youtube.videos().list(part="status", id=vid).execute()["items"][0]
        if item["status"].get("privacyStatus") == "public":
            print(f"Already public: https://youtu.be/{vid}")
            continue
        status = dict(item["status"])  # keep every other setting (made-for-kids, AI label...)
        status.update(privacyStatus="private", publishAt=when)
        for key in ("uploadStatus", "failureReason", "rejectionReason"):  # read-only
            status.pop(key, None)
        youtube.videos().update(part="status", body={"id": vid, "status": status}).execute()
        after = youtube.videos().list(part="status", id=vid).execute()["items"][0]["status"]
        if after.get("publishAt") != when:
            failed.append(vid)
            print(f"{vid}: YouTube kept {after}")
            continue
        print(f"Goes public at {when} UTC (in about 3 minutes): https://youtu.be/{vid}")
        for h in history:
            if h.get("youtube_id") == vid:
                h["publish_at"] = when
                h["awaiting_approval"] = False
    save_history(history)
    if failed:
        sys.exit(f"Not changed: {failed}")


if __name__ == "__main__":
    main()
