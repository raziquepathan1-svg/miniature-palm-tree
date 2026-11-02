"""Post The Anatomy Unfolded's Shorts as Reels on Instagram + Facebook (2 a day: 12 PM and 9 PM India time).

Run a few minutes after each Short goes public on YouTube. Posts the newest Short that is due, public on YouTube
and not posted yet (explainer_queue/social_posted.json). Captions come from the queue item's "social_caption"
(keyword line + hook + hashtags, owner's tag rule). Reuses the tested Restore Remake Studio Meta code.

    python -m youtube_agent.explainer.social_post            # post the due Short
    python -m youtube_agent.explainer.social_post --check    # test the connection, posts nothing
"""
import datetime as dt
import json
import sys
from pathlib import Path

from .. import social as S

QDIR = Path(__file__).resolve().parents[2] / "explainer_queue"
QUEUE, POSTED = QDIR / "queue.json", QDIR / "social_posted.json"
AI_NOTE = "🤖 Narrated with an AI voice."
CHANNEL = "https://www.youtube.com/@theanatomyunfolded"


def due_short(queue, posted, now):
    shorts = [q for q in queue if q["kind"] == "short" and q.get("youtube_id") and q["id"] not in posted
              and dt.datetime.fromisoformat(q["publish_at"].replace("Z", "+00:00")) <= now
              and now - dt.datetime.fromisoformat(q["publish_at"].replace("Z", "+00:00")) < dt.timedelta(hours=8)]
    return max(shorts, key=lambda q: q["publish_at"]) if shorts else None


def build_captions(item, queue, ig_name):
    base = item.get("social_caption") or item["title"].replace(" #Shorts", "")
    text, tags = S._split_hashtags(base) if not item.get("social_caption") else (base, "")
    lines = text.rstrip().split("\n")
    tag_line = lines[-1] if lines and lines[-1].startswith("#") else ""
    body = "\n".join(lines[:-1] if tag_line else lines).rstrip()
    eid = item["id"].split("_short")[0]
    long_ = next((q for q in queue if q["id"] == eid), None)
    fb_body = body.replace("Full video on YouTube: The Anatomy Unfolded (link in bio) 👆",
                           f"▶️ Full video on YouTube: {CHANNEL}")
    if long_ and long_.get("youtube_id") and long_["publish_at"] <= item["publish_at"]:
        fb_body = fb_body.replace(CHANNEL, f"https://youtu.be/{long_['youtube_id']}")
    ig_body = body + (f"\n👉 Follow @{ig_name} for a new body explainer every day." if ig_name and "Follow" not in body else "")
    fb = f"{fb_body}\n{AI_NOTE}\n\n{tag_line or tags}".strip()
    ig = f"{ig_body}\n{AI_NOTE}\n\n{tag_line or tags}".strip()
    return fb, ig


def main():
    if "--check" in sys.argv:
        return S.check_connection()
    page_id, token, ig_user_id = S._env("META_PAGE_ID"), S._env("META_PAGE_TOKEN"), S._env("IG_USER_ID")
    if not (page_id and token):
        sys.exit("Facebook/Instagram secrets are missing - nothing posted.")
    queue = json.loads(QUEUE.read_text())
    posted = json.loads(POSTED.read_text()) if POSTED.exists() else {}
    item = due_short(queue, posted, dt.datetime.now(dt.timezone.utc))
    if not item:
        print("No Short is due right now (or it was already posted).")
        return
    if not S.youtube_is_public(item["youtube_id"]):
        print(f"{item['id']}: YouTube Short {item['youtube_id']} is not public yet - not posting.")
        return
    token, _ = S.page_token(page_id, token)
    ig_name = S._graph_field(ig_user_id, "username", token) if ig_user_id else ""
    fb_cap, ig_cap = build_captions(item, queue, ig_name)
    video = QDIR / item["file"]
    rec, fb_id = {"youtube_id": item["youtube_id"]}, None
    try:
        fb_id = S.post_facebook_reel(video, fb_cap, page_id, token)
        rec["facebook"] = fb_id
        print(f"Facebook Reel posted: {fb_id}")
    except Exception as e:
        print(f"Facebook FAILED: {e}")
    if ig_user_id:
        try:
            rec["instagram"] = S.post_instagram_reel(video, ig_cap, ig_user_id, token)
        except Exception as e:
            print(f"  (Instagram direct upload failed: {e}; trying the Facebook Reel's video)")
            try:
                if not fb_id:
                    raise RuntimeError("no Facebook Reel to take the video from")
                rec["instagram"] = S.post_instagram_reel_from_url(S.facebook_video_source(fb_id, token), ig_cap, ig_user_id, token)
            except Exception as e2:
                print(f"Instagram FAILED: {e2}")
        if rec.get("instagram"):
            print(f"Instagram Reel posted: {rec['instagram']}")
    if rec.get("facebook") or rec.get("instagram"):
        posted[item["id"]] = rec
        POSTED.write_text(json.dumps(posted, indent=1))
    if not (rec.get("facebook") and (rec.get("instagram") or not ig_user_id)):
        sys.exit(1)


if __name__ == "__main__":
    main()
