"""Make new-style thumbnails for videos that are already on YouTube.

Reads youtube_agent/thumbnail_jobs.json (youtube_id, text, highlight, style, photo_query),
renders each thumbnail and uploads it. Finished jobs are marked "done" so they never run twice.

    python -m youtube_agent.set_thumbnails
"""

import json
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from . import visuals
from .uploader import _credentials

HERE = Path(__file__).parent
JOBS = HERE / "thumbnail_jobs.json"
OUT = HERE / "output" / "thumbnails"
HOST = HERE.parent / "branding" / "health-support-studio" / "avatar" / "nurse_cutout.png"


def main() -> None:
    jobs = json.loads(JOBS.read_text())
    pending = [j for j in jobs if not j.get("done")]
    if not pending:
        print("No thumbnail jobs to do.")
        return
    visuals.ensure_fonts()
    OUT.mkdir(parents=True, exist_ok=True)
    youtube = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    for job in pending:
        vid = job["youtube_id"]
        photo = visuals.fetch_photo(job.get("photo_query", ""), OUT / f"{vid}_photo.jpg")
        thumb = visuals.make_thumbnail(job["text"], "Health Support Studio", OUT / f"{vid}.jpg", photo,
                                       style=job.get("style"), highlight=job.get("highlight"),
                                       host=HOST if HOST.exists() else None)
        try:
            youtube.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb))).execute()
            job["done"] = True
            print(f"Thumbnail set: https://youtu.be/{vid}")
        except Exception as e:
            print(f"FAILED for {vid}: {e}")
    JOBS.write_text(json.dumps(jobs, indent=2) + "\n")


if __name__ == "__main__":
    main()
