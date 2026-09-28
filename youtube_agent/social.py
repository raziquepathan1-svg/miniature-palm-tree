"""Posts the daily vertical Short to Instagram Reels and Facebook Page Reels (Meta Graph API).

Runs after the YouTube video has gone public. If you set the YouTube video to Private (or deleted
it) during your review, the Short is NOT posted.

Usage (from the repo root; the GitHub workflow does this for you):
    python -m youtube_agent.social path/to/social_folder

Needs these environment variables (GitHub secrets):
    META_PAGE_ID     Facebook Page ID
    META_PAGE_TOKEN  long-lived Page access token
    IG_USER_ID       Instagram professional account ID linked to the Page (optional: skip Instagram)
"""

import json
import os
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


def post_instagram_reel(video: Path, caption: str, ig_user_id: str, token: str) -> str:
    size = video.stat().st_size
    container = _check(requests.post(
        f"{GRAPH}/{ig_user_id}/media",
        params={"media_type": "REELS", "upload_type": "resumable", "caption": caption,
                "share_to_feed": "true", "access_token": token},
        timeout=60,
    ))
    with open(video, "rb") as f:
        _check(requests.post(
            container["uri"],
            headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)},
            data=f, timeout=600,
        ))
    for _ in range(POLL_LIMIT):
        status = _check(requests.get(
            f"{GRAPH}/{container['id']}", params={"fields": "status_code,status", "access_token": token}, timeout=60,
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
        params={"creation_id": container["id"], "access_token": token}, timeout=60,
    ))
    return published["id"]


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


def post(social_dir: Path) -> None:
    meta = json.loads((social_dir / "social.json").read_text())
    video = social_dir / "short.mp4"
    page_id, token = os.environ.get("META_PAGE_ID"), os.environ.get("META_PAGE_TOKEN")
    ig_user_id = os.environ.get("IG_USER_ID")
    if not (page_id and token):
        print("Facebook/Instagram not connected yet (META_PAGE_ID / META_PAGE_TOKEN missing) - skipping.")
        return
    if not youtube_is_public(meta["youtube_id"]):
        print(f"YouTube video {meta['youtube_id']} is not public (stopped during review?) - not posting the Short.")
        return

    link = f"https://youtu.be/{meta['youtube_id']}"
    # Facebook makes caption links clickable; Instagram doesn't, so point people to the bio link too.
    fb_caption = f"{meta['caption']}\n\n▶️ Watch the full video on YouTube: {link}"
    ig_caption = f"{meta['caption']}\n\n▶️ Full video on YouTube (link in bio): {link}"
    results = []
    if ig_user_id:
        try:
            results.append(f"Instagram Reel posted: {post_instagram_reel(video, ig_caption, ig_user_id, token)}")
        except Exception as e:  # keep going so Facebook still gets posted
            results.append(f"Instagram FAILED: {e}")
    try:
        results.append(f"Facebook Reel posted: {post_facebook_reel(video, fb_caption, page_id, token)}")
    except Exception as e:
        results.append(f"Facebook FAILED: {e}")
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
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m youtube_agent.social path/to/social_folder")
    post(Path(sys.argv[1]))
