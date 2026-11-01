"""Replies to viewers' comments, as the channel (owner, Nov 1: "auto reply"). Free mode: no paid AI here.

    python -m youtube_agent.comment_replies inbox   # new viewer comments -> youtube_agent/comment_inbox.json
    python -m youtube_agent.comment_replies reply   # posts youtube_agent/reply_jobs.json, marks them done

The daily check reads the inbox, writes each reply in the chat (never personal medical advice, never "I'm a
doctor", emergencies -> call 911 / local emergency number, spam and insults skipped) and adds them to
reply_jobs.json as {comment_id, parent_id, video_id, text} ({comment_id, skip: true} for spam). Viewers' answers under our pinned comment count too:
YouTube replies are one level deep, so those replies go to the same thread."""

import datetime as dt
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from googleapiclient.discovery import build

from .uploader import _credentials

HERE = Path(__file__).parent
HISTORY = HERE / "history.json"
INBOX = HERE / "comment_inbox.json"
JOBS = HERE / "reply_jobs.json"
DONE = HERE / "comments_replied.json"
MAX_PER_DAY = 20  # 50 quota units each; the daily uploads (video + 3 Shorts) need most of the 10,000


def _load(p: Path, default):
    return json.loads(p.read_text()) if p.exists() else default


def _titles() -> dict[str, str]:
    out = {}
    for h in _load(HISTORY, []):
        for k in ("youtube_id", "short_youtube_id", "short2_youtube_id", "short3_youtube_id"):
            if h.get(k):
                out[h[k]] = h.get("title", "") + ("" if k == "youtube_id" else " (Short)")
    return out


def inbox() -> None:
    yt = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    me = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    done = _load(DONE, {})
    titles = _titles()
    found, req, pages = [], yt.commentThreads().list(part="snippet,replies", allThreadsRelatedToChannelId=me,
                                                     maxResults=100, order="time", textFormat="plainText"), 0
    while req is not None and pages < 3:
        resp = req.execute()
        pages += 1
        for th in resp.get("items", []):
            top = th["snippet"]["topLevelComment"]
            vid = th["snippet"].get("videoId", "")
            replies = (th.get("replies") or {}).get("comments", [])
            ours = {c["id"] for c in replies if c["snippet"].get("authorChannelId", {}).get("value") == me}
            cands = [] if top["snippet"].get("authorChannelId", {}).get("value") == me else [top]
            cands += [c for c in replies if c["snippet"].get("authorChannelId", {}).get("value") != me]
            for c in cands:
                if c["id"] in done or (c is top and ours):
                    continue  # already answered (by us, here or by hand in Studio)
                s = c["snippet"]
                found.append({"comment_id": c["id"], "parent_id": th["id"], "video_id": vid,
                              "video": titles.get(vid, ""), "author": s.get("authorDisplayName", ""),
                              "text": s.get("textDisplay", "")[:1500], "published": s.get("publishedAt", "")})
        req = yt.commentThreads().list_next(req, resp)
    INBOX.write_text(json.dumps(found, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(found)} viewer comment(s) waiting for a reply")
    for f in found:
        print(f"  [{f['comment_id']}] {f['author']} on {f['video'] or f['video_id']}: {f['text'][:200]}")


def reply() -> None:
    jobs = _load(JOBS, [])
    pending = [j for j in jobs if not j.get("done")]
    if not pending:
        print("No replies to post.")
        return
    yt = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    done = _load(DONE, {})
    today = dt.datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()  # YouTube's quota day
    budget = done.pop("_budget", {})
    used = budget.get("used", 0) if budget.get("day") == today else 0
    for j in pending:
        if j["comment_id"] in done:
            j["done"] = True
            continue
        if j.get("skip"):  # spam, links, insults, fights: no reply, just never shown again
            done[j["comment_id"]] = "skipped"
            j["done"] = True
            continue
        if used >= MAX_PER_DAY:
            print("  (Today's reply budget is used; the rest go tomorrow.)")
            break
        try:
            r = yt.comments().insert(part="snippet", body={"snippet": {
                "parentId": j["parent_id"], "textOriginal": j["text"]}}).execute()
            done[j["comment_id"]] = r["id"]
            j["done"] = True
            used += 1
            print(f"  Replied on https://youtu.be/{j.get('video_id', '')}: {j['text'][:120]}")
        except Exception as e:
            print(f"  (Could not reply to {j['comment_id']}: {e})")
    done["_budget"] = {"day": today, "used": used}
    DONE.write_text(json.dumps(done, indent=2) + "\n")
    JOBS.write_text(json.dumps(jobs, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    {"inbox": inbox, "reply": reply}[sys.argv[1]]()
