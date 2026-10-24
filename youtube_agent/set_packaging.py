"""Free mode: the title, top description lines and pinned question written in the daily check (no paid API).

Reads youtube_agent/packaging_jobs.json (youtube_id, title, description_top, pin_question, optional packages),
changes the video's title and puts the keyword lines at the top of its description, and stores the question
in history.json, where yt_comments picks it up for the pinned comment. Finished jobs are marked "done".

    python -m youtube_agent.set_packaging
"""

import json
from pathlib import Path

from googleapiclient.discovery import build

from .uploader import _credentials

HERE = Path(__file__).parent
JOBS = HERE / "packaging_jobs.json"
HISTORY = HERE / "history.json"
KEEP = ("title", "description", "categoryId", "tags", "defaultLanguage", "defaultAudioLanguage")


def main() -> None:
    jobs = json.loads(JOBS.read_text()) if JOBS.exists() else []
    pending = [j for j in jobs if not j.get("done")]
    if not pending:
        print("No packaging jobs to do.")
        return
    history = json.loads(HISTORY.read_text())
    youtube = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    for job in pending:
        vid = job["youtube_id"]
        try:
            snip = youtube.videos().list(part="snippet", id=vid).execute()["items"][0]["snippet"]
            body = {k: snip[k] for k in KEEP if k in snip}
            body["title"] = job["title"][:100]
            top = (job.get("description_top") or "").strip()
            if top and not body.get("description", "").startswith(top):
                body["description"] = f"{top}\n\n{body.get('description', '')}"[:5000]
            youtube.videos().update(part="snippet", body={"id": vid, "snippet": body}).execute()
        except Exception as e:
            print(f"FAILED for {vid}: {e}")
            continue
        entry = next((h for h in history if h.get("youtube_id") == vid), None)
        if entry is not None:
            entry["title"] = job["title"]
            for key in ("pin_question", "packages", "chosen"):
                if job.get(key):
                    entry[key] = job[key]
        job["done"] = True
        print(f"Title and description set: https://youtu.be/{vid}  ({job['title']})")
    HISTORY.write_text(json.dumps(history, indent=2, ensure_ascii=False) + "\n")
    JOBS.write_text(json.dumps(jobs, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
