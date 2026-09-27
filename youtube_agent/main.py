"""YouTube avatar agent: topic -> script -> avatar video -> editing -> upload.

Usage (from the repo root):
    python -m youtube_agent.main                   # make and upload videos_per_run videos
    python -m youtube_agent.main --dry-run         # make the video but don't upload
    python -m youtube_agent.main --script-only     # only write the script (no HeyGen credits used)
    python -m youtube_agent.main --topic "How do vaccines work?"
    python -m youtube_agent.main --list-avatars    # show your HeyGen avatar/voice IDs
    python -m youtube_agent.main --setup-youtube   # one-time YouTube login
    python -m youtube_agent.main --voice-sample    # hear the free AI voices
"""

import argparse
import datetime as dt
import json
import os
import re
from pathlib import Path

import yaml

HERE = Path(__file__).parent
HISTORY_FILE = HERE / "history.json"
OUTPUT_DIR = HERE / "output"


def load_config() -> dict:
    return yaml.safe_load((HERE / "config.yaml").read_text())


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


def pick_style(config: dict, history: list[dict]) -> dict | None:
    """Rotate through the configured video styles so the channel doesn't feel repetitive."""
    styles = config["video"].get("styles") or []
    if not styles:
        return None
    published = sum(1 for h in history if h.get("youtube_id"))
    return styles[published % len(styles)]


def next_publish_time(time_str: str, tz_name: str, now: dt.datetime | None = None) -> dt.datetime:
    """Next occurrence of HH:MM in the given time zone (at least 1 hour from now), as UTC."""
    from zoneinfo import ZoneInfo

    tz = ZoneInfo(tz_name)
    now = (now or dt.datetime.now(dt.timezone.utc)).astimezone(tz)
    hour, minute = (int(x) for x in time_str.split(":"))
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target < now + dt.timedelta(hours=1):
        target += dt.timedelta(days=1)
    return target.astimezone(dt.timezone.utc)


def write_summary(lines: list[str]) -> None:
    """Show a short report on the GitHub Actions run page (no-op when run locally)."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as f:
            f.write("\n".join(lines) + "\n\n")


def make_one_video(config: dict, history: list[dict], topic: str | None, dry_run: bool, script_only: bool) -> None:
    from . import planner

    topic = topic or next_queued_topic(config, history)
    style = pick_style(config, history)
    video_cfg = {**config["video"], **{k: v for k, v in (style or {}).items() if k in ("format", "target_minutes")}}
    print("1/6 Choosing topic and writing script with Claude...")
    if style:
        print(f"    Style: {style['name']} ({video_cfg.get('format')})")
    plan = planner.plan_video(config["channel"], video_cfg, [h["topic"] for h in history], topic, style)
    print(f"    Topic: {plan.topic}\n    Title: {plan.title}")

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    workdir = OUTPUT_DIR / f"{stamp}-{slugify(plan.title)}"
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "draft_script.txt").write_text("\n\n".join(plan.narration()))

    sources: list[str] = []
    fact_issues: list[str] = []
    if config["video"].get("fact_check", True):
        from . import fact_check

        print("2/6 Fact-checking every health claim against trusted sources...")
        review = fact_check.fact_check(plan.topic, plan.scenes)
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
        plan.scenes = review.apply_to(plan.scenes)
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

        print("3/6 Narrating with the free AI voice and building graphics...")
        raw = visuals.build_video(plan, video_cfg, config.get("voice", {}), channel_name, workdir)

    print("4/6 Editing (intro/outro/music)...")
    final = editor.edit_video(raw, config["editing"], video_cfg, HERE, workdir / "final.mp4")

    print("5/6 Making thumbnail...")
    if video_cfg.get("mode") == "avatar":
        thumb = editor.make_thumbnail(final, plan.thumbnail_text, workdir / "thumbnail.jpg", shorts=shorts)
    else:
        first_clip = workdir / "scenes" / "01_bg.mp4"
        frame = None
        if first_clip.exists():
            frame = workdir / "thumb_frame.png"
            editor._run(["-y", "-ss", "1", "-i", str(first_clip), "-frames:v", "1", str(frame)])
        thumb = visuals.make_thumbnail(plan.thumbnail_text, channel_name, workdir / "thumbnail.jpg", frame)

    description = plan.description
    if sources:
        description += "\n\nSources:\n" + "\n".join(f"- {u}" for u in sources)
    footer = (config["youtube"].get("description_footer") or "").strip()
    if footer:
        description += "\n\n" + footer
    title = plan.title
    if shorts and "#shorts" not in (title + description).lower():
        description += "\n\n#shorts"

    entry = {"date": dt.datetime.now().isoformat(timespec="seconds"), "topic": plan.topic,
             "requested_topic": topic, "title": title, "style": (style or {}).get("name")}
    if dry_run:
        print(f"6/6 Dry run - not uploading. Files in {workdir}")
        return

    from . import uploader

    yt = dict(config["youtube"])
    publish_at = None
    if yt.get("auto_publish_time"):
        # Upload as private + scheduled: YouTube makes it public by itself at this time.
        publish_at = next_publish_time(yt["auto_publish_time"], yt.get("auto_publish_timezone", "America/New_York"))
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
    history.append(entry)
    save_history(history)

    summary = [
        f"## {title}",
        f"- Style: {(style or {}).get('name', 'default')} | Privacy: **{yt.get('privacy')}**",
        f"- Review and publish: https://studio.youtube.com/video/{video_id}/edit",
    ]
    if fact_issues:
        summary.append("- Fact-check corrections: " + "; ".join(fact_issues))
    if publish_at:
        summary.append(f"- **Scheduled** to go public automatically at {yt['publish_at']} (UTC). "
                       "Watch it before then; to stop it, set Visibility to Private or delete it.")
    elif yt.get("privacy") == "private":
        summary.append("- **Waiting for your review**: open the link, watch it, then set Visibility to Public.")
    print("\n".join(summary))
    write_summary(summary)


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
