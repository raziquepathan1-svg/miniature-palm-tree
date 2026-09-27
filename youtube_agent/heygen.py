"""Renders the script with your HeyGen avatar and downloads the finished video."""

import os
import time
from pathlib import Path

import requests

API = "https://api.heygen.com"
POLL_SECONDS = 20
TIMEOUT_SECONDS = 60 * 60


def _headers() -> dict:
    key = os.environ.get("HEYGEN_API_KEY")
    if not key:
        raise RuntimeError("HEYGEN_API_KEY is not set.")
    return {"X-Api-Key": key, "Content-Type": "application/json", "Accept": "application/json"}


def _check(resp: requests.Response) -> dict:
    try:
        body = resp.json()
    except ValueError:
        resp.raise_for_status()
        raise
    if resp.status_code >= 400 or body.get("error"):
        raise RuntimeError(f"HeyGen API error ({resp.status_code}): {body.get('error') or body}")
    return body["data"]


def list_avatars_and_voices() -> None:
    """Print the avatar, photo-avatar and voice IDs available on your HeyGen account."""
    avatars = _check(requests.get(f"{API}/v2/avatars", headers=_headers(), timeout=60))
    print("== Avatars (avatar_type: avatar) ==")
    for a in avatars.get("avatars", []):
        print(f"  {a.get('avatar_id')}  {a.get('avatar_name')}")
    print("== Photo avatars (avatar_type: talking_photo) ==")
    for p in avatars.get("talking_photos", []):
        print(f"  {p.get('talking_photo_id')}  {p.get('talking_photo_name')}")
    voices = _check(requests.get(f"{API}/v2/voices", headers=_headers(), timeout=60))
    print("== Voices ==")
    for v in voices.get("voices", []):
        print(f"  {v.get('voice_id')}  {v.get('name')}  [{v.get('language')}]")


def render_video(scenes: list[str], title: str, avatar: dict, video: dict, out_path: Path) -> Path:
    avatar_id = os.environ.get("HEYGEN_AVATAR_ID") or avatar["avatar_id"]
    voice_id = os.environ.get("HEYGEN_VOICE_ID") or avatar["voice_id"]
    if not avatar_id or not voice_id:
        raise RuntimeError("Set avatar.avatar_id and avatar.voice_id in config.yaml (see --list-avatars).")

    if avatar.get("avatar_type") == "talking_photo":
        character = {"type": "talking_photo", "talking_photo_id": avatar_id}
    else:
        character = {"type": "avatar", "avatar_id": avatar_id, "avatar_style": "normal"}

    dimension = {"width": 720, "height": 1280} if video.get("format") == "shorts" else {"width": 1280, "height": 720}
    payload = {
        "title": title,
        "caption": bool(video.get("captions")),
        "dimension": dimension,
        "video_inputs": [
            {
                "character": character,
                "voice": {
                    "type": "text",
                    "input_text": scene,
                    "voice_id": voice_id,
                    "speed": avatar.get("voice_speed", 1.0),
                },
                "background": {"type": "color", "value": video.get("background_color", "#0F172A")},
            }
            for scene in scenes
        ],
    }

    data = _check(requests.post(f"{API}/v2/video/generate", headers=_headers(), json=payload, timeout=120))
    video_id = data["video_id"]
    print(f"  HeyGen render started: {video_id}")

    deadline = time.time() + TIMEOUT_SECONDS
    while time.time() < deadline:
        status = _check(
            requests.get(f"{API}/v1/video_status.get", params={"video_id": video_id}, headers=_headers(), timeout=60)
        )
        state = status.get("status")
        if state == "completed":
            url = (video.get("captions") and status.get("video_url_caption")) or status["video_url"]
            _download(url, out_path)
            return out_path
        if state == "failed":
            raise RuntimeError(f"HeyGen render failed: {status.get('error')}")
        print(f"  HeyGen status: {state}...")
        time.sleep(POLL_SECONDS)
    raise TimeoutError(f"HeyGen video {video_id} was not ready after {TIMEOUT_SECONDS // 60} minutes.")


def _download(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
