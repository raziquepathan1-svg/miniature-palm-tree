"""Schedule a video that was held for your OK (youtube.hold_for_approval): the video and its Shorts get their
publish times. Run by the "Approve video" workflow.

    python -m youtube_agent.approve            # the latest video waiting for approval
    python -m youtube_agent.approve VIDEO_ID   # this one
"""

import datetime as dt
import sys

from .main import load_config, load_history, last_scheduled, next_publish_time, save_history


def _schedule(youtube, video_id: str, when: dt.datetime) -> None:
    item = youtube.videos().list(part="status", id=video_id).execute()["items"][0]
    status = dict(item["status"])  # keep every other setting (made-for-kids, AI label...)
    status.update(privacyStatus="private", publishAt=when.strftime("%Y-%m-%dT%H:%M:%SZ"))
    for key in ("uploadStatus", "failureReason", "rejectionReason"):  # read-only
        status.pop(key, None)
    youtube.videos().update(part="status", body={"id": video_id, "status": status}).execute()


def main() -> None:
    from googleapiclient.discovery import build

    from .uploader import _credentials

    config, history = load_config(), load_history()
    yt = config["youtube"]
    wanted = sys.argv[1] if len(sys.argv) > 1 else None
    entry = next((h for h in reversed(history) if h.get("awaiting_approval")
                  and (not wanted or h.get("youtube_id") == wanted)), None)
    if not entry:
        sys.exit("No video is waiting for approval.")
    when = dt.datetime.fromisoformat(entry["planned_publish_at"].replace("Z", "+00:00"))
    if when < dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1):  # approved late: the next free slot
        others = [h for h in history if h is not entry]
        when = next_publish_time(yt["auto_publish_time"], yt.get("auto_publish_timezone", "America/New_York"),
                                 after=last_scheduled(others))
    youtube = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    _schedule(youtube, entry["youtube_id"], when)
    print(f"Scheduled {entry.get('title', entry['youtube_id'])}: {when:%Y-%m-%d %H:%M} UTC")
    for key, hours in (("short_youtube_id", yt.get("short_delay_hours", 6)),
                       ("short2_youtube_id", yt.get("second_short_delay_hours", 3))):
        if entry.get(key):
            t = when + dt.timedelta(hours=float(hours))
            _schedule(youtube, entry[key], t)
            print(f"Scheduled the Short {entry[key]}: {t:%Y-%m-%d %H:%M} UTC")
    entry["publish_at"] = when.strftime("%Y-%m-%dT%H:%M:%SZ")
    entry["awaiting_approval"] = False
    entry.pop("planned_publish_at", None)
    save_history(history)


if __name__ == "__main__":
    main()
