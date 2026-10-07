"""YouTube avatar agent: topic -> script -> avatar video -> editing -> upload.

Usage (from the repo root):
    python -m youtube_agent.main                   # make and upload videos_per_run videos
    python -m youtube_agent.main --dry-run         # make the video but don't upload
    python -m youtube_agent.main --script-only     # only write the script (no HeyGen credits used)
    python -m youtube_agent.main --topic "How do vaccines work?"
    python -m youtube_agent.main --list-avatars    # show your HeyGen avatar/voice IDs
    python -m youtube_agent.main --setup-youtube   # one-time YouTube login
    python -m youtube_agent.main --voice-sample    # hear the free AI voices

Second channel: set CHANNEL=restore_remake to use youtube_agent/channels/restore_remake/ (its own
config.yaml, history.json, script_bank/ and assets/) instead of the Health Support Studio files here.
"""

import argparse
import datetime as dt
import json
import os
import re
from pathlib import Path

from types import SimpleNamespace

import yaml

HERE = Path(__file__).parent
# Each channel keeps its own config, history, script bank and assets. Health Support Studio lives in
# youtube_agent/ itself; other channels live in youtube_agent/channels/<name>/ (CHANNEL=<name>).
CHANNEL_DIR = HERE / "channels" / os.environ["CHANNEL"] if os.environ.get("CHANNEL") else HERE
HISTORY_FILE = CHANNEL_DIR / "history.json"
SCRIPT_BANK = CHANNEL_DIR / "script_bank"  # pre-written scripts: used first, no API cost
OUTPUT_DIR = HERE / "output"


def _host_image(config: dict) -> Path | None:
    """The presenter cut-out for thumbnails (config.yaml thumbnail.host_image), if set."""
    rel = (config.get("thumbnail") or {}).get("host_image")
    return (CHANNEL_DIR / rel).resolve() if rel else None


def load_config() -> dict:
    return yaml.safe_load((CHANNEL_DIR / "config.yaml").read_text())


def load_history() -> list[dict]:
    return json.loads(HISTORY_FILE.read_text()) if HISTORY_FILE.exists() else []


def save_history(history: list[dict]) -> None:
    HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False) + "\n")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "video"


def next_queued_topic(config: dict, history: list[dict]) -> str | None:
    done = {(h.get(k) or "").strip().lower() for h in history for k in ("topic", "requested_topic")}
    for topic in config["channel"].get("topic_queue") or []:
        if topic.strip().lower() not in done:
            return topic
    return None


def unused_bank_scripts(history: list[dict], skip_styles: tuple = ("Quick Short",)) -> list[Path]:
    """Pre-written scripts not used yet. Quick Short scripts are skipped: every long video already makes
    two Shorts, so each day's main video is a long one."""
    used = {h.get("script_file") for h in history}
    return [f for f in sorted(SCRIPT_BANK.glob("*.yaml")) if f.name not in used
            and yaml.safe_load(f.read_text()).get("style") not in skip_styles]


def pick_style(config: dict, history: list[dict]) -> dict | None:
    """Rotate through the configured video styles so the channel doesn't feel repetitive."""
    styles = config["video"].get("styles") or []
    if not styles:
        return None
    published = sum(1 for h in history if h.get("youtube_id"))
    return styles[published % len(styles)]


def next_publish_time(time_str: str, tz_name: str, now: dt.datetime | None = None,
                      after: dt.datetime | None = None) -> dt.datetime:
    """Next occurrence of HH:MM in the given time zone (at least 1 hour from now, and later than any
    video already scheduled), as UTC."""
    from zoneinfo import ZoneInfo

    tz = ZoneInfo(tz_name)
    now = (now or dt.datetime.now(dt.timezone.utc)).astimezone(tz)
    hour, minute = (int(x) for x in time_str.split(":"))
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    while target < now + dt.timedelta(hours=1) or (after and target <= after.astimezone(tz)):
        target += dt.timedelta(days=1)
    return target.astimezone(dt.timezone.utc)


def last_scheduled(history: list[dict]) -> dt.datetime | None:
    times = [dt.datetime.fromisoformat(h["publish_at"].replace("Z", "+00:00")) for h in history if h.get("publish_at")]
    return max(times) if times else None


def write_summary(lines: list[str]) -> None:
    """Show a short report on the GitHub Actions run page (no-op when run locally)."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as f:
            f.write("\n".join(lines) + "\n\n")


def make_one_video(config: dict, history: list[dict], topic: str | None, dry_run: bool, script_only: bool) -> None:
    from . import planner

    # A script from the bank is used first (free); otherwise Claude writes one through the API.
    bank = [] if topic else unused_bank_scripts(history)
    bank_file = bank[0] if bank else None
    bank_data = yaml.safe_load(bank_file.read_text()) if bank_file else {}
    styles = {s["name"]: s for s in config["video"].get("styles") or []}
    style = styles.get(bank_data.get("style")) or pick_style(config, history)
    video_cfg = {**config["video"], **{k: v for k, v in (style or {}).items() if k in ("format", "target_minutes")}}
    if bank_file:
        print(f"1/6 Using pre-written script {bank_file.name} ({len(bank) - 1} left after this one)")
        plan = planner.VideoPlan.model_validate(bank_data["plan"])
        topic = bank_data.get("queue_topic") or plan.topic
    else:
        topic = topic or next_queued_topic(config, history)
        print("1/6 Choosing topic and writing script with Claude...")
        plan = planner.plan_video(config["channel"], video_cfg, [h["topic"] for h in history], topic, style)
    if style:
        print(f"    Style: {style['name']} ({video_cfg.get('format')})")
    print(f"    Topic: {plan.topic}\n    Title: {plan.title}")

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    workdir = OUTPUT_DIR / f"{stamp}-{slugify(plan.title)}"
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "draft_script.txt").write_text("\n\n".join(plan.narration()))

    sources: list[str] = bank_data.get("sources", [])
    fact_issues: list[str] = []
    if not bank_file and config["video"].get("fact_check", True):
        from . import fact_check

        print("2/6 Fact-checking every health claim against trusted sources...")
        # The companion Short is checked together with the main script.
        review = fact_check.fact_check(plan.topic, plan.scenes + plan.short_scenes,
                                       config["video"].get("fact_check_searches", 6))
        (workdir / "fact_check.json").write_text(review.model_dump_json(indent=2))
        for issue in review.issues:
            print(f"    fixed: {issue}")
        if not review.approved:
            print(f"    NOT APPROVED - video skipped. Details in {workdir / 'fact_check.json'}")
            if not script_only:  # remember it so the agent moves on to another topic
                history.append({"date": dt.datetime.now().isoformat(timespec="seconds"),
                                "topic": plan.topic, "requested_topic": topic, "title": plan.title,
                                "status": "rejected_by_fact_check"})
                save_history(history)
            return
        checked = review.apply_to(plan.scenes + plan.short_scenes)
        plan.scenes, plan.short_scenes = checked[:len(plan.scenes)], checked[len(plan.scenes):]
        sources = review.sources
        fact_issues = review.issues

    (workdir / "plan.json").write_text(plan.model_dump_json(indent=2))
    (workdir / "script.txt").write_text("\n\n".join(plan.narration()))
    if script_only:
        print(f"    Script saved to {workdir}")
        return

    from . import editor

    shorts = video_cfg.get("format") == "shorts"
    channel_name = config["channel"].get("name", "")
    if video_cfg.get("mode") == "avatar":
        from . import heygen

        print("3/6 Rendering your avatar video on HeyGen (this can take 5-30 min)...")
        raw = heygen.render_video(plan.narration(), plan.title, config["avatar"], video_cfg, workdir / "avatar.mp4")
    else:
        from . import visuals

        visuals.set_brand(config.get("brand"))
        if video_cfg.get("rotate_colors"):  # a different color theme for every video
            visuals.use_theme(dt.date.today().toordinal())
        print("3/6 Narrating with the free AI voice and building graphics...")
        raw = visuals.build_video(plan, video_cfg, config.get("voice", {}), channel_name, workdir)

    print("4/6 Editing (intro/outro/music)...")
    final = editor.edit_video(raw, config["editing"], video_cfg, CHANNEL_DIR, workdir / "final.mp4")

    print("5/6 Making thumbnail...")
    if video_cfg.get("mode") == "avatar":
        thumb = editor.make_thumbnail(final, plan.thumbnail_text, workdir / "thumbnail.jpg", shorts=shorts)
    else:
        frame = visuals.fetch_photo(plan.thumbnail_photo_query, workdir / "thumb_photo.jpg")
        first_clip = workdir / "scenes" / "01_bg.mp4"
        if frame is None and first_clip.exists():
            frame = workdir / "thumb_frame.png"
            editor._run(["-y", "-ss", "1", "-i", str(first_clip), "-frames:v", "1", str(frame)])
        thumb = visuals.make_thumbnail(plan.thumbnail_text, channel_name, workdir / "thumbnail.jpg", frame,
                                       style=(style or {}).get("name"), highlight=plan.thumbnail_highlight,
                                       host=_host_image(config))

    social_dir = None
    if config.get("social", {}).get("enabled", True):
        social_dir = make_social_short(plan, final, video_cfg, config, channel_name, workdir)

    description = plan.description
    if sources:
        description += "\n\nSources:\n" + "\n".join(f"- {u}" for u in sources)
    chapters = workdir / "chapters.txt"
    if not shorts and chapters.exists() and chapters.read_text().strip():
        description += "\n\nChapters:\n" + chapters.read_text().strip()
    footer = (config["youtube"].get("description_footer") or "").strip()
    if footer:
        description += "\n\n" + footer
    title = plan.title
    if shorts and "#shorts" not in (title + description).lower():
        description += "\n\n#shorts"

    entry = {"date": dt.datetime.now().isoformat(timespec="seconds"), "topic": plan.topic,
             "requested_topic": topic, "title": title, "style": (style or {}).get("name")}
    if bank_file:
        entry["script_file"] = bank_file.name
    if dry_run:
        print(f"6/6 Dry run - not uploading. Files in {workdir}")
        return

    from . import uploader

    yt = dict(config["youtube"])
    publish_at = None
    if yt.get("auto_publish_time"):
        # Upload as private + scheduled: YouTube makes it public by itself at this time.
        publish_at = next_publish_time(yt["auto_publish_time"], yt.get("auto_publish_timezone", "America/New_York"),
                                       after=last_scheduled(history))
        yt["privacy"] = "private"
        yt["publish_at"] = publish_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    elif yt.get("review_before_publish", True):
        yt["privacy"] = "private"
    print(f"6/6 Uploading to YouTube ({'scheduled ' + yt['publish_at'] if publish_at else yt.get('privacy')})...")
    video_id = uploader.upload_video(
        final, thumb, title, description, plan.tags, yt,
        config["channel"].get("language_code", "en-US"),
    )
    entry["youtube_id"] = video_id
    if yt.get("publish_at"):
        entry["publish_at"] = yt["publish_at"]
    history.append(entry)
    save_history(history)

    shorts_playlist = yt.get("shorts_playlist", "Health Shorts")
    playlist_about = yt.get("playlist_description")
    playlists = [match_playlist(plan.playlist, config["channel"].get("playlists") or [],
                                yt.get("default_playlist", "Health Tips"))]
    if shorts:
        playlists.append(shorts_playlist)
    if yt.get("playlists", True):
        uploader.add_to_playlists(video_id, playlists, playlist_about)

    # Also upload the companion vertical Short to YouTube Shorts (not on days the video is itself a Short).
    short_id = None
    short_file = social_dir / "short.mp4" if social_dir else None
    if yt.get("upload_short", True) and not shorts and short_file and short_file.exists():
        short_yt = dict(yt)
        if yt.get("publish_at"):
            short_time = dt.datetime.fromisoformat(yt["publish_at"].replace("Z", "+00:00")) + dt.timedelta(
                hours=float(yt.get("short_delay_hours", 6)))
            short_yt["publish_at"] = short_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        short_title = plan.short_title if "#shorts" in plan.short_title.lower() else f"{plan.short_title} #Shorts"
        short_desc = (f"{plan.short_caption}\n\n▶️ Watch the full video: https://youtu.be/{video_id}\n\n{footer}").strip()
        print("    Uploading the Short to YouTube Shorts...")
        try:
            short_id = uploader.upload_video(short_file, None, short_title, short_desc, plan.tags + ["shorts"],
                                             short_yt, config["channel"].get("language_code", "en-US"))
            entry["short_youtube_id"] = short_id
            save_history(history)
            if yt.get("playlists", True):
                uploader.add_to_playlists(short_id, [shorts_playlist], playlist_about)
        except Exception as e:  # the main video is already up; don't fail the whole run
            print(f"  (Could not upload the YouTube Short: {e})")
    # A second Short from the most interesting part of the long video: Shorts bring most new viewers.
    short2_id = None
    if yt.get("second_short", True) and not shorts and uploads_today() < int(yt.get("max_uploads_per_day", 5)):
        try:
            short2_id = upload_second_short(plan, video_id, video_cfg, config, channel_name, workdir, yt, footer)
            if short2_id:
                entry["short2_youtube_id"] = short2_id
                save_history(history)
        except Exception as e:  # the main video and first Short are already up
            print(f"  (Could not make the second Short: {e})")
    if social_dir:
        topic = plan.topic.split(":")[0].strip()
        comment = (f"What's your biggest question about {topic.lower()}? Ask below 👇 I read every comment and "
                   f"your questions may become our next video. If this helped you, please share it with "
                   f"someone who needs it ❤️")
        (social_dir / "social.json").write_text(json.dumps({
            "youtube_id": video_id, "title": title, "caption": plan.short_caption,
            "publish_at": yt.get("publish_at"), "comment": comment,
        }, indent=2))

    summary = [
        f"## {title}",
        f"- Style: {(style or {}).get('name', 'default')} | Privacy: **{yt.get('privacy')}**",
        f"- Review and publish: https://studio.youtube.com/video/{video_id}/edit",
        f"- Playlist: {', '.join(playlists)}",
    ]
    if short_id:
        summary.append(f"- YouTube Short: https://studio.youtube.com/video/{short_id}/edit")
    if short2_id:
        summary.append(f"- Second YouTube Short: https://studio.youtube.com/video/{short2_id}/edit")
    if fact_issues:
        summary.append("- Fact-check corrections: " + "; ".join(fact_issues))
    left = len(unused_bank_scripts(history))
    summary.append(f"- Pre-written scripts left: **{left}**" + (
        " - ask Claude to write more scripts soon (after they run out, videos use your paid API credit)"
        if left <= 5 else ""))
    if publish_at:
        summary.append(f"- **Scheduled** to go public automatically at {yt['publish_at']} (UTC). "
                       "Watch it before then; to stop it, set Visibility to Private or delete it.")
    elif yt.get("privacy") == "private":
        summary.append("- **Waiting for your review**: open the link, watch it, then set Visibility to Public.")
    print("\n".join(summary))
    write_summary(summary)


def match_playlist(name: str, allowed: list[str], default: str = "Health Tips") -> str:
    """Map Claude's playlist choice onto the configured list so no stray playlists get created."""
    lowered = {p.lower(): p for p in allowed}
    if name.strip().lower() in lowered:
        return lowered[name.strip().lower()]
    words = set(name.lower().replace("&", " ").split())
    best = max(allowed, key=lambda p: len(words & set(p.lower().replace("&", " ").split())), default=None)
    return best if best and words & set(best.lower().replace("&", " ").split()) else default


def uploads_today() -> int:
    """YouTube uploads of both channels since the API quota last reset (midnight Pacific, ~07:00 UTC).
    Both channels may share one Google project: about 6 uploads a day fit in its free quota."""
    now = dt.datetime.utcnow()
    start = now.replace(hour=7, minute=0, second=0, microsecond=0)
    if now < start:
        start -= dt.timedelta(days=1)
    count = 0
    for f in (HERE / "history.json", HERE / "channels" / "restore_remake" / "history.json"):
        try:
            for h in json.loads(f.read_text()):
                if dt.datetime.fromisoformat(h.get("date", "1970-01-01")) >= start:
                    count += sum(1 for k in ("youtube_id", "short_youtube_id", "short2_youtube_id") if h.get(k))
        except Exception:
            pass
    return count


def upload_second_short(plan, video_id: str, video_cfg: dict, config: dict, channel_name: str, workdir: Path,
                        yt: dict, footer: str) -> str | None:
    """A ~45 s vertical Short from one strong scene of the video (myth vs fact, warning signs, a key number),
    with a hook first and the host's outro, scheduled a few hours after the first Short."""
    from . import uploader, visuals
    from .planner import Scene

    used = {s.heading for s in plan.short_scenes}
    middle = [s for s in plan.scenes[1:-1] if s.heading not in used]
    order = {"myth_fact": 0, "warning": 1, "big_number": 2, "bullets": 3}
    picks = sorted((s for s in middle if s.layout in order), key=lambda s: order[s.layout])
    if not picks:
        return None
    best = [s for s in picks if s.layout == picks[0].layout]
    scene = best[len(best) // 2]
    topic = plan.topic.split(":")[0].strip()
    if scene.layout == "myth_fact" and scene.points:
        hook = "Myth or fact? Most people get this one wrong."
        title = f"Myth or fact: {scene.points[0].rstrip('.?!')}?"
    elif scene.layout == "warning":
        hook = "Do you know these warning signs? Don't ignore them."
        title = f"{scene.heading}: don't ignore these"
    elif scene.layout == "big_number":
        hook = f"Here's one number about {topic.lower()} everyone should know."
        title = f"{topic}: know this number"
    else:
        hook = f"{scene.heading}. Here's what you need to know."
        title = f"{scene.heading} in 40 seconds"
    if len(title) > 50:
        title = title[:47].rsplit(" ", 1)[0] + "..."
    title += " #Shorts"
    hook_scene = Scene(layout="title", heading="Myth or Fact?" if scene.layout == "myth_fact" else scene.heading[:40],
                       points=[topic[:40]], footage_query=scene.footage_query, narration=hook)
    body = scene.model_copy(update={"narration": scene.narration.rstrip() +
                                    " Watch the full video on the Health Support Studio channel."})
    print(f"    Making a second Short: {title}")
    raw = visuals.build_video(SimpleNamespace(scenes=[hook_scene, body], short_scenes=[]),
                              {**video_cfg, "format": "shorts"}, config.get("voice", {}), channel_name,
                              workdir / "short2_build")
    short_yt = dict(yt)
    if yt.get("publish_at"):
        t = dt.datetime.fromisoformat(yt["publish_at"].replace("Z", "+00:00")) + dt.timedelta(
            hours=float(yt.get("second_short_delay_hours", 3)))
        short_yt["publish_at"] = t.strftime("%Y-%m-%dT%H:%M:%SZ")
    tags = " ".join(w for w in plan.short_caption.split() if w.startswith("#"))
    desc = f"{hook}\n\n▶️ Watch the full video: https://youtu.be/{video_id}\n\n{tags}\n\n{footer}".strip()
    print("    Uploading the second Short...")
    short_id = uploader.upload_video(raw, None, title, desc, plan.tags + ["shorts"], short_yt,
                                     config["channel"].get("language_code", "en-US"))
    if yt.get("playlists", True):
        uploader.add_to_playlists(short_id, [yt.get("shorts_playlist", "Health Shorts")], yt.get("playlist_description"))
    return short_id


def make_social_short(plan, final: Path, video_cfg: dict, config: dict, channel_name: str,
                      workdir: Path) -> Path | None:
    """Make the vertical Short for Instagram/Facebook Reels (reuses the video itself on Shorts days)."""
    import shutil

    social_dir = workdir / "social"
    social_dir.mkdir(exist_ok=True)
    if video_cfg.get("format") == "shorts":
        shutil.copyfile(final, social_dir / "short.mp4")
        return social_dir
    if not plan.short_scenes:
        return None
    from . import visuals

    print("    Making the vertical Short for Instagram/Facebook...")
    short_cfg = {**video_cfg, "format": "shorts"}
    raw = visuals.build_video(SimpleNamespace(scenes=plan.short_scenes), short_cfg, config.get("voice", {}),
                              channel_name, workdir / "short_build")
    shutil.copyfile(raw, social_dir / "short.mp4")
    return social_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Educational YouTube avatar agent")
    parser.add_argument("--topic", help="Make a video on this exact topic")
    parser.add_argument("--count", type=int, help="How many videos to make (default: videos_per_run)")
    parser.add_argument("--dry-run", action="store_true", help="Make the video but don't upload it")
    parser.add_argument("--script-only", action="store_true", help="Only write the script")
    parser.add_argument("--list-avatars", action="store_true", help="List HeyGen avatar and voice IDs")
    parser.add_argument("--setup-youtube", action="store_true", help="One-time YouTube login")
    parser.add_argument("--voice-sample", action="store_true", help="Make short samples of the free AI voices")
    args = parser.parse_args()

    if args.list_avatars:
        from . import heygen
        heygen.list_avatars_and_voices()
        return
    if args.setup_youtube:
        from . import uploader
        uploader.setup_youtube_login()
        return

    if args.voice_sample:
        from . import voice
        out = OUTPUT_DIR / "voice_samples"
        out.mkdir(parents=True, exist_ok=True)
        text = ("Welcome to Health Support Studio. Today, let's talk about what your blood pressure "
                "numbers really mean, and when you should call your doctor.")
        for v in ("af_heart", "af_bella", "af_nicole", "af_sarah", "am_michael", "am_fenrir", "am_puck"):
            voice.narrate_scene(text, {"voice": v}, out / f"{v}.wav")
            print(f"  {out / (v + '.wav')}")
        return

    config = load_config()
    history = load_history()
    count = args.count or config["video"].get("videos_per_run", 1)
    for i in range(count):
        print(f"\n=== Video {i + 1} of {count} ===")
        make_one_video(config, history, args.topic, args.dry_run, args.script_only)


if __name__ == "__main__":
    main()
