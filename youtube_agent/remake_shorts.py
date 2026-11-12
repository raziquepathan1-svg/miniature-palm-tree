"""Re-make the YouTube Shorts (and the Instagram/Facebook Reels) of a video that is already up.

Owner, Nov 12: the RSV Shorts showed a clip labelled "Flu in the Airway" - "change these clips, I don't want any
mistake ... make new 3 shorts". The video's script is rebuilt exactly as the daily run does (shortened plan, growth
lines, suspense/story), the Shorts are made again with today's clip labels, uploaded PRIVATE (so they are checked
before going public), linked to the full video, and recorded in history.json. The files are kept in
youtube_agent/output/remake/social for the check and for the Reels.

    python -m youtube_agent.remake_shorts <video_id> [slots, e.g. 1,2,3]
"""

import datetime as dt
import shutil
import sys
from pathlib import Path

import yaml

from . import growth, main, planner, suspense, uploader

HERE = Path(__file__).parent


def run(video_id: str, slots: set[int]) -> None:
    config, history = main.load_config(), main.load_history()
    entry = next(h for h in history if h.get("youtube_id") == video_id)
    data = yaml.safe_load((HERE / "script_bank" / entry["script_file"]).read_text())
    plan = planner.VideoPlan.model_validate(data["plan"])
    video_cfg = dict(config["video"])
    if video_cfg.get("bank_minutes"):
        main.shorten(plan, float(video_cfg["bank_minutes"]), float(config.get("voice", {}).get("speed", 1.0)))
    growth.PART_IN_TITLE = False
    growth.LAST_MID = growth.apply(plan, None, len(history))
    suspense.apply(plan, data.get("story"))
    main.USED_SHORT_PAGES.update(entry.get("remade_short_pages") or [])  # Shorts made on other days

    workdir = HERE / "output" / "remake"
    shutil.rmtree(workdir, ignore_errors=True)
    workdir.mkdir(parents=True)
    channel_name = config["channel"]["name"]
    yt = dict(config["youtube"], privacy="private")
    yt.pop("publish_at", None)
    footer = (config["youtube"].get("description_footer") or "").strip()
    lang = config["channel"].get("language_code", "en-US")
    shorts_playlist = yt.get("shorts_playlist", "Health Shorts")

    if 1 in slots:
        social = main.make_social_short(plan, Path("unused"), video_cfg, config, channel_name, workdir)
        short_file = social / "short.mp4" if social else None
        if short_file and short_file.exists():
            title = plan.short_title if "#shorts" in plan.short_title.lower() else f"{plan.short_title} #Shorts"
            desc = f"{plan.short_caption}\n\n▶️ Watch the full video: https://youtu.be/{video_id}\n\n{footer}".strip()
            sid = uploader.upload_video(short_file, None, title, desc, plan.tags + ["shorts"], yt, lang)
            entry["short_youtube_id"] = sid
            main.save_history(history)
            uploader.add_to_playlists(sid, [shorts_playlist], yt.get("playlist_description"))
            print(f"Short 1 (private): https://youtu.be/{sid}  {title}")
    if 2 in slots:
        sid = main.upload_second_short(plan, video_id, video_cfg, config, channel_name, workdir, yt, footer,
                                       data.get("short2_hook") or "", data.get("short2_title") or "")
        if sid:
            entry["short2_youtube_id"] = sid
            main.save_history(history)
            print(f"Short 2 (private): https://youtu.be/{sid}")
    if 3 in slots:
        sid = main.upload_second_short(plan, video_id, video_cfg, config, channel_name, workdir, yt, footer,
                                       slot=3, skip=set(main.USED_SHORT_PAGES))
        if sid:
            entry["short3_youtube_id"] = sid
            main.save_history(history)
            print(f"Short 3 (private): https://youtu.be/{sid}")
    entry["remade_short_pages"] = sorted(main.USED_SHORT_PAGES)
    entry["shorts_remade"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    main.save_history(history)


if __name__ == "__main__":
    run(sys.argv[1], {int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else "1,2,3").split(",")})
