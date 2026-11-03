"""Schedule The Anatomy Unfolded explainer videos and Shorts from explainer_queue/queue.json.

Each run uploads the next items that are not on YouTube yet (earliest publish time first), as PRIVATE with a
scheduled publish time (6 PM India time), so the owner can still check them in YouTube Studio before they go
public. At most MAX_PER_RUN uploads per run (YouTube API quota, shared with Health Support Studio).

    python -m youtube_agent.explainer.publish [--dry-run]
"""
import datetime as dt
import json
import sys
from pathlib import Path

from googleapiclient.errors import HttpError

from ..uploader import add_to_playlists, upload_video

ROOT = Path(__file__).resolve().parents[2]
QDIR = ROOT / "explainer_queue"
QUEUE = QDIR / "queue.json"
CHANNEL_ID = "UChgwZ4Ch-53T4cMyQwKa2OA"   # The Anatomy Unfolded (formerly Restore Remake Studio)
MAX_PER_RUN = 3
ABOUT = ("The Anatomy Unfolded: {title}. Anatomy, physiology and diseases explained with clear diagrams. "
         "Educational only, not medical advice.")


def main() -> None:
    dry = "--dry-run" in sys.argv
    if not QUEUE.exists():
        print("Nothing in the queue yet.")
        return
    queue = json.loads(QUEUE.read_text())
    dele = QDIR / "delete.json"
    if dele.exists() and not dry:   # replaced uploads: remove them from YouTube first
        from googleapiclient.discovery import build
        from ..uploader import _credentials
        yt_api = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
        left_ids = []
        ids_now = {q["id"]: q.get("youtube_id") for q in queue}
        for vid in json.loads(dele.read_text()):
            if isinstance(vid, dict):   # {"id": old, "after": item}: delete only once the replacement is on YouTube
                if not ids_now.get(vid["after"]):
                    left_ids.append(vid)
                    continue
                vid = vid["id"]
            try:
                yt_api.videos().delete(id=vid).execute()
                print(f"Deleted old upload {vid}")
            except HttpError as e:
                if e.resp.status == 404:
                    print(f"Already gone: {vid}")
                else:
                    print(f"Could not delete {vid}: {e}")
                    left_ids.append(vid)
        dele.write_text(json.dumps(left_ids))
    if not dry:   # metadata refresh for items already on YouTube (title / description / tags / thumbnail)
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from ..uploader import _credentials
        api = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
        for q in queue:
            if q.get("youtube_id") and q.get("update_status"):   # owner (3 Nov): new publish time (long video 3:30 PM)
                api.videos().update(part="status", body={"id": q["youtube_id"], "status": {
                    "privacyStatus": "private", "publishAt": q["publish_at"], "selfDeclaredMadeForKids": False,
                    "containsSyntheticMedia": True}}).execute()
                q.pop("update_status", None)
                QUEUE.write_text(json.dumps(queue, indent=1, ensure_ascii=False))
                print(f"New publish time: {q['id']} -> {q['publish_at']}")
            if q.get("youtube_id") and q.get("update"):
                body = {"id": q["youtube_id"], "snippet": {"title": q["title"][:100], "description": q["description"][:5000],
                                                         "tags": q["tags"], "categoryId": "27", "defaultLanguage": "en-US",
                                                         "defaultAudioLanguage": "en-US"}}
                api.videos().update(part="snippet", body=body).execute()
                if q.get("thumbnail"):
                    try:
                        api.thumbnails().set(videoId=q["youtube_id"], media_body=MediaFileUpload(str(QDIR / q["thumbnail"]))).execute()
                    except HttpError as e:
                        print(f"  thumbnail not set for {q['id']}: {e}")
                q.pop("update", None)
                QUEUE.write_text(json.dumps(queue, indent=1, ensure_ascii=False))
                print(f"Updated title/description/thumbnail: {q['id']} -> {q['title']}")
    now = dt.datetime.now(dt.timezone.utc)
    todo = [q for q in queue if not q.get("youtube_id")]
    todo.sort(key=lambda q: q["publish_at"])
    done = 0
    for q in todo:
        if done >= MAX_PER_RUN:
            break
        when = dt.datetime.fromisoformat(q["publish_at"].replace("Z", "+00:00"))
        if when < now + dt.timedelta(minutes=20):
            # too late to schedule: move it to the same time on the next free day
            when = when + dt.timedelta(days=((now - when).days + 1))
            q["publish_at"] = when.strftime("%Y-%m-%dT%H:%M:%SZ")
        yt = {"channel_id": CHANNEL_ID, "category_id": "27", "made_for_kids": False,
              "contains_synthetic_media": True, "publish_at": q["publish_at"]}
        print(f"{q['id']}: {q['title']} -> {q['publish_at']}")
        if dry:
            done += 1
            continue
        try:
            vid = upload_video(QDIR / q["file"], QDIR / q["thumbnail"] if q.get("thumbnail") else None,
                               q["title"], q["description"], q["tags"], yt)
        except HttpError as e:
            if "quota" in str(e).lower():
                print("YouTube upload quota used up for today; the rest will go in the next run.")
                break
            raise
        q["youtube_id"] = vid
        done += 1
        QUEUE.write_text(json.dumps(queue, indent=1, ensure_ascii=False))
        if q.get("playlist"):
            add_to_playlists(vid, [q["playlist"]], about=ABOUT)
    if dele.exists() and not dry:   # replacements uploaded in this run: remove the old uploads now
        ids_now = {q["id"]: q.get("youtube_id") for q in queue}
        keep = []
        for vid in json.loads(dele.read_text()):
            if isinstance(vid, dict) and ids_now.get(vid["after"]):
                try:
                    yt_api.videos().delete(id=vid["id"]).execute()
                    print(f"Deleted old upload {vid['id']} (replaced by {vid['after']})")
                except HttpError as e:
                    print(f"Could not delete {vid['id']}: {e}")
                    keep.append(vid)
            else:
                keep.append(vid)
        dele.write_text(json.dumps(keep))
    left = sum(1 for q in queue if not q.get("youtube_id"))
    print(f"Scheduled {done} item(s); {left} still waiting.")


if __name__ == "__main__":
    main()
