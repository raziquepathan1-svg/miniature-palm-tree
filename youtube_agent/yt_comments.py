"""ONE comment from the channel on every public video and Short, to pin in Studio:
- Full videos: an open question first (the day's pin question), then the related video, the series playlist,
  the previous part and the subscribe link. No "thanks for watching".
- Shorts: the full-video link first, then the question.
Comments posted in the older format are updated to the new one.
Only public videos get one (comments on private/scheduled videos fail), each video only once
(youtube_agent/comments_posted.json remembers them).   python -m youtube_agent.yt_comments"""

import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from googleapiclient.discovery import build

from .uploader import _credentials

HERE = Path(__file__).parent
HISTORY = HERE / "history.json"
DONE = HERE / "comments_posted.json"
MAX_PER_DAY = 25  # 50 quota units each; YouTube's day (Pacific time) also carries the ~5,000-unit daily upload
VERSION = 2  # bump when the wording changes: older comments are updated


def _question(e: dict) -> str:
    q = e.get("pin_question")
    if not q:
        topic = (e.get("topic") or "this").split(":")[0].strip().lower()
        q = f"What's one thing about {topic} you wish someone had told you sooner?"
    return f"💬 {q} Tell us below 👇"


def _public(yt, ids: list[str]) -> set[str]:
    out = set()
    for k in range(0, len(ids), 50):
        for v in yt.videos().list(part="status", id=",".join(ids[k:k + 50])).execute().get("items", []):
            if v["status"]["privacyStatus"] == "public":
                out.add(v["id"])
    return out


def _playlists(yt) -> dict[str, str]:
    found, req = {}, yt.playlists().list(part="snippet", mine=True, maxResults=50)
    while req is not None:
        resp = req.execute()
        found.update({p["snippet"]["title"].strip().lower(): p["id"] for p in resp.get("items", [])})
        req = yt.playlists().list_next(req, resp)
    return found


def texts(history: list[dict], sub: str, playlists: dict[str, str]) -> dict[str, str]:
    """{video id: comment} for every video and Short in the history."""
    out = {}
    for i, e in enumerate(history):
        vid = e.get("youtube_id")
        if not vid:
            continue
        lines = [_question(e), ""]
        if e.get("bridge_id"):
            lines.append(f"▶ Watch next: https://youtu.be/{e['bridge_id']}")
        series, n = e.get("series"), e.get("episode")
        if series and n:
            lines.append(f"This is part {n} of our {series} series.")
            pl = playlists.get(series.lower())
            if pl:
                lines.append(f"▶ Watch the whole series in order: https://www.youtube.com/playlist?list={pl}")
            prev = next((h for h in reversed(history[:i]) if h.get("series") == series
                         and h.get("episode") == n - 1 and h.get("youtube_id")), None)
            if prev:
                lines.append(f"⏮ Previous part: https://youtu.be/{prev['youtube_id']}")
        else:
            lines.append(f"▶ More simple health videos: {sub.split('?')[0]}/videos")
        lines += [f"🔔 Subscribe for a new health video every day: {sub}",
                  "Educational only, not medical advice."]
        out[vid] = "\n".join(lines)
        for key in ("short_youtube_id", "short2_youtube_id"):
            if e.get(key):
                out[e[key]] = (f"▶ Watch the full video here: https://youtu.be/{vid}\n\n{_question(e)}\n\n"
                               f"🔔 Subscribe for one simple health tip every day: {sub}")
    return out


def main() -> None:
    yt = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    channel = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    sub = f"https://www.youtube.com/channel/{channel}?sub_confirmation=1"
    history = json.loads(HISTORY.read_text())
    done = json.loads(DONE.read_text()) if DONE.exists() else {}
    today = dt.datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()  # YouTube's quota day
    budget = done.pop("_budget", {})
    used = budget.get("used", 0) if budget.get("day") == today else 0
    def version(v):
        return v.get("v", 1) if isinstance(v, dict) else 1

    texts_now = texts(history, sub, _playlists(yt))
    new = [v for v in texts_now if v not in done]
    todo = {v: texts_now[v] for v in new + [v for v in texts_now if v in done and version(done[v]) < VERSION]}
    public = _public(yt, list(todo))
    posted = 0
    for vid, text in todo.items():
        if vid not in public:
            continue
        if used + posted >= MAX_PER_DAY:
            print("  (Today's comment budget is used; the rest go tomorrow.)")
            break
        try:
            old = done.get(vid)
            if old:  # the thread id is also its top-level comment's id: rewrite it in the new format
                cid = old["id"] if isinstance(old, dict) else old
                yt.comments().update(part="snippet", body={"id": cid, "snippet": {"textOriginal": text}}).execute()
                print(f"  Updated the comment on https://youtu.be/{vid}")
            else:
                cid = yt.commentThreads().insert(part="snippet", body={"snippet": {
                    "videoId": vid, "topLevelComment": {"snippet": {"textOriginal": text}}}}).execute()["id"]
                print(f"  Commented on https://youtu.be/{vid}")
            done[vid] = {"id": cid, "v": VERSION}
            posted += 1
        except Exception as e:
            print(f"  (Could not comment on {vid}: {e})")
    done["_budget"] = {"day": today, "used": used + posted}
    DONE.write_text(json.dumps(done, indent=2) + "\n")
    print(f"Posted {posted} comments; {len(todo) - posted} waiting (not public yet or next run).")


if __name__ == "__main__":
    main()
