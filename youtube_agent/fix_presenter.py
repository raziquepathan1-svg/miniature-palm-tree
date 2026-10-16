"""Adds the corner presenter to a daily video that came out without him (Kaggle lip-sync did not come back),
from the run's saved files, and swaps it in on YouTube: the new upload gets the old video's title, description,
tags, thumbnail and playlists, the two Shorts point to it, and history.json follows it. The old video stays
private (delete it in YouTube Studio when you like).

python -m youtube_agent.fix_presenter <run files folder> <old YouTube video ID>"""

import re
import sys
from pathlib import Path

from . import editor, presenter
from .editor import _duration
from .main import CHANNEL_DIR, load_config, load_history, save_history


def _parts(workdir: Path) -> list[Path]:
    """The narrated video's parts in order (from the concat list; paths were the old runner's)."""
    scenes = workdir / "scenes"
    names = re.findall(r"file '([^']+)'", (workdir / "narrated.txt").read_text())
    return [scenes / Path(n).name for n in names]


def _shows(parts: list[Path]) -> list[tuple[float, float]]:
    """When the presenter shows: every part except the host's own clips (desk clips, intro, outro)."""
    shows, t = [], 0.0
    for p in parts:
        d = _duration(p)
        if not (p.stem.endswith("_host") or p.stem in ("intro", "outro")):
            if shows and abs(shows[-1][1] - t) < 0.05:
                shows[-1] = (shows[-1][0], t + d)
            else:
                shows.append((t, t + d))
        t += d
    return shows


def _swap_on_youtube(old: str, final: Path, thumb: Path | None, entry: dict, config: dict) -> str:
    from googleapiclient.discovery import build

    from . import uploader

    yt_api = build("youtube", "v3", credentials=uploader._credentials(), cache_discovery=False)
    snip = yt_api.videos().list(part="snippet", id=old).execute()["items"][0]["snippet"]
    yt = dict(config["youtube"], privacy="private")
    yt.pop("publish_at", None)
    new = uploader.upload_video(final, thumb, snip["title"], snip.get("description", ""), snip.get("tags", []),
                                yt, snip.get("defaultLanguage") or config["channel"].get("language_code", "en-US"))

    # the old video's playlists: the new one takes its place, the old one leaves
    req = yt_api.playlists().list(part="snippet", mine=True, maxResults=50)
    while req is not None:
        resp = req.execute()
        for pl in resp.get("items", []):
            items = yt_api.playlistItems().list(part="id", playlistId=pl["id"], videoId=old).execute().get("items", [])
            if items:
                yt_api.playlistItems().insert(part="snippet", body={"snippet": {
                    "playlistId": pl["id"], "resourceId": {"kind": "youtube#video", "videoId": new}}}).execute()
                for it in items:
                    yt_api.playlistItems().delete(id=it["id"]).execute()
                print(f"  Playlist {pl['snippet']['title']}: swapped")
        req = yt_api.playlists().list_next(req, resp)

    # the Shorts link to the full video
    for key in ("short_youtube_id", "short2_youtube_id"):
        sid = entry.get(key)
        if not sid:
            continue
        s = yt_api.videos().list(part="snippet", id=sid).execute()["items"][0]["snippet"]
        if old in s.get("description", ""):
            body = {k: s[k] for k in ("title", "description", "categoryId", "tags", "defaultLanguage",
                                      "defaultAudioLanguage") if k in s}
            body["description"] = body["description"].replace(old, new)
            yt_api.videos().update(part="snippet", body={"id": sid, "snippet": body}).execute()
            print(f"  Short {sid}: now links to {new}")
    return new


def main(run_dir: str, old: str) -> None:
    config, history = load_config(), load_history()
    entry = next(h for h in history if h.get("youtube_id") == old)
    if not entry.get("awaiting_approval"):
        sys.exit("This video is already approved or public; not replacing it.")
    workdir = next(p.parent for p in Path(run_dir).rglob("narrated.txt"))
    narrated = workdir / "narrated.mp4"
    parts = _parts(workdir)
    shows = _shows(parts)
    print(f"  {len(parts)} parts, presenter shows in {len(shows)} stretches")
    video_cfg = config["video"]
    with_him = presenter.add_presenter(narrated, shows, video_cfg["presenter"], workdir)
    if with_him == narrated:
        sys.exit("The presenter could not be added (see above); nothing was changed.")
    final = editor.edit_video(with_him, config["editing"], video_cfg, CHANNEL_DIR, workdir / "final_presenter.mp4")
    thumb = workdir / "thumbnail.jpg"
    new = _swap_on_youtube(old, final, thumb if thumb.exists() else None, entry, config)
    entry["youtube_id"] = new
    entry.setdefault("replaced_ids", []).append(old)
    entry.pop("preview", None)
    save_history(history)
    Path("new_video_id.txt").write_text(new)
    Path("final_presenter_path.txt").write_text(str(final))
    print(f"Replaced {old} with {new} (with the corner presenter). The old video stays private.")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
