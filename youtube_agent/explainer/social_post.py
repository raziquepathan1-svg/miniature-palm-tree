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
    shorts = [q for q in queue if q["kind"] == "short" and q.get("youtube_id")
              and (q["id"] not in posted or not posted[q["id"]].get("instagram"))   # retry Instagram-only failures
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
    ig_body = body
    if long_ and long_["publish_at"] > item["publish_at"] and long_["publish_at"] > dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"):   # owner: the full video comes at 3:30 PM - say so on the 12 PM Reel
        fb_body = fb_body.replace(f"▶️ Full video on YouTube: {CHANNEL}",
                                  f"▶️ Full video today at 3:30 PM (India time) on YouTube: {CHANNEL}")
        ig_body = ig_body.replace("Full video on YouTube: The Anatomy Unfolded (link in bio) 👆",
                                  "Full video today at 3:30 PM (India time) on YouTube: The Anatomy Unfolded (link in bio) 👆") + (f"\n👉 Follow @{ig_name} for a new body explainer every day." if ig_name and "Follow" not in body else "")
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
    run_file = QDIR / "social_run.txt"
    backfill = []
    if run_file.exists():   # a line "backfill: id1,id2" posts those (already public) Shorts that were missed
        for ln in run_file.read_text().splitlines():
            if ln.lower().startswith("backfill:"):
                backfill = [x.strip() for x in ln.split(":", 1)[1].split(",") if x.strip()]
    items = [q for q in queue if q["id"] in backfill and q.get("youtube_id")
             and not (posted.get(q["id"], {}).get("facebook") and posted.get(q["id"], {}).get("instagram"))]
    items.sort(key=lambda q: q["publish_at"])
    one = due_short(queue, posted, dt.datetime.now(dt.timezone.utc))
    if one and one["id"] not in [q["id"] for q in items]:
        items.append(one)
    if not items:
        print("No Short is due right now (or it was already posted).")
        return
    token, _ = S.page_token(page_id, token)
    ig_name = S._graph_field(ig_user_id, "username", token) if ig_user_id else ""
    failed = False
    for item in items:
        if not S.youtube_is_public(item["youtube_id"]):
            print(f"{item['id']}: YouTube Short {item['youtube_id']} is not public yet - not posting.")
            continue
        if not post_one(item, queue, posted, token, page_id, ig_user_id, ig_name):
            failed = True
    if failed:
        sys.exit(1)


def ig_copy(video):
    """Instagram rejects some of our very low-bitrate whiteboard videos (error 2207076); a constant-bitrate copy
    (3.5 Mbps, stereo 44.1 kHz) is accepted (tested 11 Nov 2026)."""
    import subprocess, tempfile
    out = Path(tempfile.gettempdir()) / f"ig_{video.name}"
    try:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-c:v", "libx264", "-profile:v", "main", "-level", "4.0",
                        "-pix_fmt", "yuv420p", "-r", "30", "-g", "60", "-bf", "0", "-b:v", "3500k", "-minrate", "3500k",
                        "-maxrate", "3500k", "-bufsize", "7000k", "-x264-params", "nal-hrd=cbr", "-c:a", "aac", "-b:a", "128k",
                        "-ar", "44100", "-ac", "2", "-movflags", "+faststart", str(out)], check=True)
        return out
    except Exception as e:
        print(f"  (could not make the Instagram copy, using the original: {e})")
        return video


def post_one(item, queue, posted, token, page_id, ig_user_id, ig_name):
    print(f"== {item['id']}")
    fb_cap, ig_cap = build_captions(item, queue, ig_name)
    video = QDIR / item["file"]
    rec = dict(posted.get(item["id"], {"youtube_id": item["youtube_id"]}))
    fb_id = rec.get("facebook")
    if fb_id:
        print(f"Facebook Reel already posted ({fb_id}) - retrying Instagram only")
    else:
        try:
            fb_id = S.post_facebook_reel(video, fb_cap, page_id, token)
            rec["facebook"] = fb_id
            print(f"Facebook Reel posted: {fb_id}")
        except Exception as e:
            print(f"Facebook FAILED: {e}")
    if ig_user_id:
        try:
            rec["instagram"] = S.post_instagram_reel(ig_copy(video), ig_cap, ig_user_id, token)
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
    return bool(rec.get("facebook") and (rec.get("instagram") or not ig_user_id))


if __name__ == "__main__":
    main()
