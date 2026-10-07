"""Posts the daily vertical Short to Instagram Reels and Facebook Page Reels (Meta Graph API).

Runs after the YouTube video has gone public. If you set the YouTube video to Private (or deleted
it) during your review, the Short is NOT posted.

Usage (from the repo root; the GitHub workflow does this for you):
    python -m youtube_agent.social path/to/social_folder
    python -m youtube_agent.social --check     # test the connection without posting anything

Needs these environment variables (GitHub secrets):
    META_PAGE_ID     Facebook Page ID
    META_PAGE_TOKEN  long-lived Page access token
    IG_USER_ID       Instagram professional account ID linked to the Page (optional: skip Instagram)
"""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import requests

GRAPH = "https://graph.facebook.com"  # unversioned: uses your Meta app's default API version
POLL_SECONDS = 10
POLL_LIMIT = 90  # ~15 minutes


def _check(resp: requests.Response) -> dict:
    try:
        data = resp.json()
    except ValueError:
        resp.raise_for_status()
        raise
    if resp.status_code >= 400 or "error" in data:
        raise RuntimeError(f"Meta API error ({resp.status_code}): {data.get('error', data)}")
    return data


def youtube_is_public(youtube_id: str) -> bool:
    """True only if the YouTube video exists and is public (i.e. you didn't stop it during review)."""
    from googleapiclient.discovery import build

    from .uploader import _credentials

    yt = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    items = yt.videos().list(part="status", id=youtube_id).execute().get("items", [])
    return bool(items) and items[0]["status"]["privacyStatus"] == "public"


def instagram_ready(video: Path) -> Path:
    """Re-encode to Instagram's Reels spec (H.264 high, yuv420p, 30 fps, AAC 48 kHz, no edit lists,
    moov atom first). The Short is stitched from separately encoded clips, which Instagram rejects
    with 'ProcessingFailedError' even though Facebook accepts it."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("  (ffmpeg not found - uploading the Short as it is)")
        return video
    out = video.with_name("short_instagram.mp4")
    subprocess.run([
        ffmpeg, "-y", "-loglevel", "error", "-i", str(video),
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30", "-g", "60",
        "-preset", "medium", "-crf", "20", "-maxrate", "8M", "-bufsize", "16M",
        "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "128k",
        "-use_editlist", "0", "-movflags", "+faststart", str(out),
    ], check=True)
    return out


def _wait_and_publish_instagram(container_id: str, ig_user_id: str, token: str) -> str:
    for _ in range(POLL_LIMIT):
        status = _check(requests.get(
            f"{GRAPH}/{container_id}", params={"fields": "status_code,status", "access_token": token}, timeout=60,
        ))
        if status.get("status_code") == "FINISHED":
            break
        if status.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram could not process the video: {status}")
        time.sleep(POLL_SECONDS)
    else:
        raise TimeoutError("Instagram took too long to process the video.")
    published = _check(requests.post(
        f"{GRAPH}/{ig_user_id}/media_publish",
        params={"creation_id": container_id, "access_token": token}, timeout=60,
    ))
    return published["id"]


def post_instagram_reel_from_url(video_url: str, caption: str, ig_user_id: str, token: str) -> str:
    """Instagram fetches the video itself from a public URL (here: the Facebook Reel's video file)."""
    container = _check(requests.post(
        f"{GRAPH}/{ig_user_id}/media",
        data={"media_type": "REELS", "video_url": video_url, "caption": caption,
              "share_to_feed": "true", "access_token": token},
        timeout=60,
    ))
    return _wait_and_publish_instagram(container["id"], ig_user_id, token)


def post_instagram_reel(video: Path, caption: str, ig_user_id: str, token: str) -> str:
    """Direct (resumable) upload of the local file."""
    video = instagram_ready(video)
    size = video.stat().st_size
    container = _check(requests.post(
        f"{GRAPH}/{ig_user_id}/media",
        data={"media_type": "REELS", "upload_type": "resumable", "caption": caption,
              "share_to_feed": "true", "access_token": token},
        timeout=60,
    ))
    with open(video, "rb") as f:
        _check(requests.post(
            container["uri"],
            headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)},
            data=f, timeout=600,
        ))
    return _wait_and_publish_instagram(container["id"], ig_user_id, token)


def facebook_video_source(video_id: str, token: str) -> str:
    """Public MP4 URL of a posted Facebook video, once Facebook has finished processing it."""
    for _ in range(POLL_LIMIT):
        info = _check(requests.get(f"{GRAPH}/{video_id}", params={"fields": "source,status",
                                                                  "access_token": token}, timeout=60))
        if info.get("source"):
            return info["source"]
        if (info.get("status") or {}).get("video_status") == "error":
            raise RuntimeError(f"Facebook could not process the video: {info.get('status')}")
        time.sleep(POLL_SECONDS)
    raise TimeoutError("Facebook took too long to process the video.")


def latest_facebook_reel(page_id: str, token: str) -> str | None:
    reels = _check(requests.get(f"{GRAPH}/{page_id}/video_reels", params={"fields": "id", "limit": 1,
                                                                         "access_token": token}, timeout=60))
    return (reels.get("data") or [{}])[0].get("id")


def post_facebook_reel(video: Path, caption: str, page_id: str, token: str) -> str:
    size = video.stat().st_size
    start = _check(requests.post(
        f"{GRAPH}/{page_id}/video_reels",
        params={"upload_phase": "start", "access_token": token}, timeout=60,
    ))
    video_id = start["video_id"]
    with open(video, "rb") as f:
        _check(requests.post(
            start["upload_url"],
            headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)},
            data=f, timeout=600,
        ))
    _check(requests.post(
        f"{GRAPH}/{page_id}/video_reels",
        params={"upload_phase": "finish", "video_id": video_id, "video_state": "PUBLISHED",
                "description": caption, "access_token": token},
        timeout=60,
    ))
    return video_id


def _env(name: str) -> str | None:
    """Secrets pasted into GitHub often carry a trailing newline or spaces; HTTP headers reject them."""
    value = (os.environ.get(name) or "").strip()
    return value or None


def page_token(page_id: str, token: str) -> tuple[str, bool]:
    """Return (Page token, was_user_token). A user token saved by mistake is swapped for the Page token
    (Facebook Reels need a Page token; one derived from a long-lived user token never expires)."""
    me = _check(requests.get(f"{GRAPH}/me", params={"fields": "id", "access_token": token}, timeout=60))
    if me.get("id") == page_id:
        return token, False
    page = _check(requests.get(f"{GRAPH}/{page_id}", params={"fields": "access_token", "access_token": token},
                               timeout=60))
    if not page.get("access_token"):
        raise RuntimeError("META_PAGE_TOKEN is a user token without access to this Page")
    return page["access_token"], True


def check_connection() -> None:
    """Read-only test that the secrets work: names the Page and Instagram account, posts nothing."""
    page_id, token = _env("META_PAGE_ID"), _env("META_PAGE_TOKEN")
    ig_user_id = _env("IG_USER_ID")
    missing = [n for n, v in (("META_PAGE_ID", page_id), ("META_PAGE_TOKEN", token), ("IG_USER_ID", ig_user_id)) if not v]
    if missing:
        sys.exit(f"Missing GitHub secrets: {', '.join(missing)}")
    lines = []
    try:
        token, was_user = page_token(page_id, token)
        if was_user:
            lines.append("WARN META_PAGE_TOKEN is a user token (expires in ~2 months) - it works, but saving the "
                         "Page token from me/accounts makes it permanent")
    except Exception as e:
        lines.append(f"FAIL Token: {e}")
    try:
        page = _check(requests.get(f"{GRAPH}/{page_id}", params={"fields": "name,instagram_business_account",
                                                                   "access_token": token}, timeout=60))
        lines.append(f"OK  Facebook Page: {page.get('name')}")
        linked = (page.get("instagram_business_account") or {}).get("id")
        if linked and linked != ig_user_id:
            lines.append(f"FAIL IG_USER_ID does not match the Instagram account linked to this Page ({linked})")
    except Exception as e:
        lines.append(f"FAIL Facebook Page: {e}")
    try:
        ig = _check(requests.get(f"{GRAPH}/{ig_user_id}", params={"fields": "username", "access_token": token},
                                 timeout=60))
        lines.append(f"OK  Instagram: @{ig.get('username')}")
        limit = _check(requests.get(f"{GRAPH}/{ig_user_id}/content_publishing_limit",
                                    params={"access_token": token}, timeout=60))
        lines.append(f"OK  Instagram publishing allowed ({limit.get('data', [{}])[0].get('quota_usage', 0)} posts used today)")
    except Exception as e:
        lines.append(f"FAIL Instagram: {e}")
    print("\n".join(lines))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write("## Facebook / Instagram connection test\n" + "\n".join(f"- {l}" for l in lines) + "\n")
    if any(l.startswith("FAIL") for l in lines):
        sys.exit(1)


def _youtube_channel(youtube_id: str) -> str:
    """The channel's address, like youtube.com/@name (from the video), or '' if YouTube can't tell."""
    try:
        from googleapiclient.discovery import build

        from .uploader import _credentials

        yt = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
        channel_id = yt.videos().list(part="snippet", id=youtube_id).execute()["items"][0]["snippet"]["channelId"]
        handle = yt.channels().list(part="snippet", id=channel_id).execute()["items"][0]["snippet"].get("customUrl")
        return f"youtube.com/{handle}" if handle else f"youtube.com/channel/{channel_id}"
    except Exception as e:
        print(f"  (could not look up the YouTube channel: {e})")
        return ""


def _graph_field(obj_id: str, field: str, token: str) -> str:
    try:
        return requests.get(f"{GRAPH}/{obj_id}", params={"fields": field, "access_token": token},
                            timeout=60).json().get(field) or ""
    except Exception:
        return ""


def _split_hashtags(text: str) -> tuple[str, str]:
    """('caption text', '#tags at the end') so the hashtags can go last, after the calls to action."""
    words = text.split()
    k = len(words)
    while k and words[k - 1].startswith("#"):
        k -= 1
    return " ".join(words[:k]), " ".join(words[k:])


def captions(meta: dict, page_id: str, ig_user_id: str | None, token: str) -> tuple[str, str]:
    """Facebook and Instagram captions: the Short's text, then where to watch more and follow, then hashtags.
    Facebook makes links clickable; Instagram doesn't, so it points to the link in the bio.
    Meta asks creators to disclose realistic AI-generated audio; the narration is an AI voice."""
    text, tags = _split_hashtags(meta["caption"])
    video = f"https://youtu.be/{meta['youtube_id']}"
    channel = _youtube_channel(meta["youtube_id"])
    ig_name = _graph_field(ig_user_id, "username", token) if ig_user_id else ""
    fb_name = _graph_field(page_id, "name", token)
    ai_note = "🤖 Narrated with an AI voice."

    fb = [text, "", f"▶️ Watch the full video on YouTube: {video}"]
    if channel:
        fb.append(f"📺 More videos every day on our YouTube channel: https://{channel} (subscribe!)")
    if ig_name:
        fb.append(f"📸 Follow us on Instagram for more videos: https://instagram.com/{ig_name}")
    fb += ["👍 Like, comment and share, and follow our page for more videos like this!", ai_note]

    ig = [text, "", f"▶️ Watch more videos on our YouTube channel{f' ({channel})' if channel else ''}: link in bio 🔗"]
    if ig_name:
        ig.append(f"👉 Follow @{ig_name} for more videos!")
    ig.append("❤️ Like, comment and share" + (f", and follow us on Facebook too: {fb_name}" if fb_name else "") + "!")
    ig.append(ai_note)
    if tags:
        fb += ["", tags]
        ig += ["", tags]
    return "\n".join(fb), "\n".join(ig)


def post(social_dir: Path) -> None:
    meta = json.loads((social_dir / "social.json").read_text())
    video = social_dir / "short.mp4"
    page_id, token = _env("META_PAGE_ID"), _env("META_PAGE_TOKEN")
    ig_user_id = _env("IG_USER_ID")
    if not (page_id and token):
        print("Facebook/Instagram not connected yet (META_PAGE_ID / META_PAGE_TOKEN missing) - skipping.")
        return
    if not youtube_is_public(meta["youtube_id"]):
        print(f"YouTube video {meta['youtube_id']} is not public (stopped during review?) - not posting the Short.")
        return
    token, was_user = page_token(page_id, token)
    if was_user:
        print("  (META_PAGE_TOKEN is a user token; using the Page token derived from it)")

    if meta.get("comment"):  # a question from the channel starts the conversation (pin it in Studio)
        try:
            from googleapiclient.discovery import build

            from .uploader import _credentials

            yt = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
            yt.commentThreads().insert(part="snippet", body={"snippet": {
                "videoId": meta["youtube_id"], "topLevelComment": {"snippet": {"textOriginal": meta["comment"]}}}}
            ).execute()
            print("  Posted the question comment on YouTube")
        except Exception as e:
            print(f"  (Could not post the YouTube comment: {e})")
    fb_caption, ig_caption = captions(meta, page_id, ig_user_id, token)
    results = []
    fb_video_id = None
    if os.environ.get("ONLY_INSTAGRAM", "").lower() == "true":  # retrying Instagram alone
        try:
            fb_video_id = latest_facebook_reel(page_id, token)
        except Exception as e:  # only needed for the fallback; the direct upload doesn't use it
            print(f"  (could not look up the latest Facebook Reel: {e})")
    else:
        try:
            fb_video_id = post_facebook_reel(video, fb_caption, page_id, token)
            results.append(f"Facebook Reel posted: {fb_video_id}")
        except Exception as e:
            results.append(f"Facebook FAILED: {e}")
    if ig_user_id:
        # Direct upload of the re-encoded file; if Instagram rejects it, let Instagram fetch the video
        # from the Facebook Reel instead.
        try:
            results.append(f"Instagram Reel posted: {post_instagram_reel(video, ig_caption, ig_user_id, token)}")
        except Exception as e:
            print(f"  (Instagram direct upload failed: {e}; trying the Facebook Reel's video)")
            try:
                if not fb_video_id:
                    raise RuntimeError("no Facebook Reel to take the video from")
                ig_id = post_instagram_reel_from_url(facebook_video_source(fb_video_id, token), ig_caption,
                                                     ig_user_id, token)
                results.append(f"Instagram Reel posted: {ig_id}")
            except Exception as e2:
                results.append(f"Instagram FAILED: {e2}")
    print("\n".join(results))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write(f"## Short for: {meta['title']}\n" + "\n".join(f"- {r}" for r in results) + "\n")
    if any("posted" in r for r in results):
        (social_dir / "posted.flag").write_text("\n".join(results))  # tells the workflow not to post again
    if any("FAILED" in r for r in results):
        sys.exit(1)


if __name__ == "__main__":
    if sys.argv[1:] == ["--check"]:
        check_connection()
        sys.exit(0)
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m youtube_agent.social path/to/social_folder")
    post(Path(sys.argv[1]))
