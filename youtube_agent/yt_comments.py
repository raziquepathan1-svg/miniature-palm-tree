"""A comment from the channel on every public video and Short (pin it in Studio when you like):
- Shorts: a link to their full video, and the subscribe link.
- Full videos: the series playlist and the previous part (series videos), and the subscribe link.
Only public videos get one (comments on private/scheduled videos fail), each video only once
(youtube_agent/comments_posted.json remembers them).   python -m youtube_agent.yt_comments"""

import json
from pathlib import Path

from googleapiclient.discovery import build

from .uploader import _credentials

HERE = Path(__file__).parent
HISTORY = HERE / "history.json"
DONE = HERE / "comments_posted.json"
MAX_PER_RUN = 40  # 50 quota units each; the daily upload needs about 5,000 of the 10,000


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
        lines = ["📌 Thanks for watching!"]
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
                out[e[key]] = (f"▶ Watch the full video here: https://youtu.be/{vid}\n"
                               f"🔔 Subscribe for one simple health tip every day: {sub}")
    return out


def main() -> None:
    yt = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    channel = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    sub = f"https://www.youtube.com/channel/{channel}?sub_confirmation=1"
    history = json.loads(HISTORY.read_text())
    done = json.loads(DONE.read_text()) if DONE.exists() else {}
    todo = {v: t for v, t in texts(history, sub, _playlists(yt)).items() if v not in done}
    public = _public(yt, list(todo))
    posted = 0
    for vid, text in todo.items():
        if vid not in public:
            continue
        if posted >= MAX_PER_RUN:
            print("  (Enough for this run; the rest go next time.)")
            break
        try:
            r = yt.commentThreads().insert(part="snippet", body={"snippet": {
                "videoId": vid, "topLevelComment": {"snippet": {"textOriginal": text}}}}).execute()
            done[vid] = r["id"]
            posted += 1
            print(f"  Commented on https://youtu.be/{vid}")
        except Exception as e:
            print(f"  (Could not comment on {vid}: {e})")
    DONE.write_text(json.dumps(done, indent=2) + "\n")
    print(f"Posted {posted} comments; {len(todo) - posted} waiting (not public yet or next run).")


if __name__ == "__main__":
    main()
