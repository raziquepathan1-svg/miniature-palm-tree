"""YouTube avatar agent: topic -> script -> avatar video -> editing -> upload.

Usage (from the repo root):
    python -m youtube_agent.main                   # make and upload videos_per_run videos
    python -m youtube_agent.main --dry-run         # make the video but don't upload
    python -m youtube_agent.main --script-only     # only write the script (no HeyGen credits used)
    python -m youtube_agent.main --topic "How do vaccines work?"
    python -m youtube_agent.main --list-avatars    # show your HeyGen avatar/voice IDs
    python -m youtube_agent.main --setup-youtube   # one-time YouTube login
"""

import argparse
import datetime as dt
import json
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
    done = {h["topic"].strip().lower() for h in history}
    for topic in config["channel"].get("topic_queue") or []:
        if topic.strip().lower() not in done:
            return topic
    return None


def make_one_video(config: dict, history: list[dict], topic: str | None, dry_run: bool, script_only: bool) -> None:
    from . import planner

    topic = topic or next_queued_topic(config, history)
    print("1/5 Choosing topic and writing script with Claude...")
    plan = planner.plan_video(config["channel"], config["video"], [h["topic"] for h in history], topic)
    print(f"    Topic: {plan.topic}\n    Title: {plan.title}")

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    workdir = OUTPUT_DIR / f"{stamp}-{slugify(plan.title)}"
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "plan.json").write_text(plan.model_dump_json(indent=2))
    (workdir / "script.txt").write_text("\n\n".join(plan.scenes))
    if script_only:
        print(f"    Script saved to {workdir}")
        return

    from . import editor, heygen

    print("2/5 Rendering your avatar video on HeyGen (this can take 5-30 min)...")
    raw = heygen.render_video(plan.scenes, plan.title, config["avatar"], config["video"], workdir / "avatar.mp4")

    print("3/5 Editing (intro/outro/music)...")
    final = editor.edit_video(raw, config["editing"], config["video"], HERE, workdir / "final.mp4")

    print("4/5 Making thumbnail...")
    shorts = config["video"].get("format") == "shorts"
    thumb = editor.make_thumbnail(final, plan.thumbnail_text, workdir / "thumbnail.jpg", shorts=shorts)

    description = plan.description
    title = plan.title
    if shorts and "#shorts" not in (title + description).lower():
        description += "\n\n#shorts"

    entry = {"date": dt.datetime.now().isoformat(timespec="seconds"), "topic": plan.topic, "title": title}
    if dry_run:
        print(f"5/5 Dry run - not uploading. Files in {workdir}")
        return

    from . import uploader

    print("5/5 Uploading to YouTube...")
    entry["youtube_id"] = uploader.upload_video(final, thumb, title, description, plan.tags, config["youtube"])
    history.append(entry)
    save_history(history)


def main() -> None:
    parser = argparse.ArgumentParser(description="Educational YouTube avatar agent")
    parser.add_argument("--topic", help="Make a video on this exact topic")
    parser.add_argument("--count", type=int, help="How many videos to make (default: videos_per_run)")
    parser.add_argument("--dry-run", action="store_true", help="Make the video but don't upload it")
    parser.add_argument("--script-only", action="store_true", help="Only write the script")
    parser.add_argument("--list-avatars", action="store_true", help="List HeyGen avatar and voice IDs")
    parser.add_argument("--setup-youtube", action="store_true", help="One-time YouTube login")
    args = parser.parse_args()

    if args.list_avatars:
        from . import heygen
        heygen.list_avatars_and_voices()
        return
    if args.setup_youtube:
        from . import uploader
        uploader.setup_youtube_login()
        return

    config = load_config()
    history = load_history()
    count = args.count or config["video"].get("videos_per_run", 1)
    for i in range(count):
        print(f"\n=== Video {i + 1} of {count} ===")
        make_one_video(config, history, args.topic, args.dry_run, args.script_only)


if __name__ == "__main__":
    main()
