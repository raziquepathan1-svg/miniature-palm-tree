"""Gives viewers a reason to subscribe: every video belongs to a named series, asks for the subscribe early
(after the first useful part, not only at the end where most viewers have already left) and names the next
episode of its series in the outro. Works on pre-written bank scripts and on scripts Claude writes."""

import re
from pathlib import Path

import yaml

MID_LINES = [
    "Quick note: this video is part of our {series} series. Every day I explain one health topic in plain "
    "words, so if this is helping you, subscribe and you won't miss the next one.",
    "By the way, this is part of our {series} series, with a new video every day. If you're finding this "
    "useful, subscribe so the next one finds you.",
    "This video is one part of our {series} series. If you want simple, trustworthy health information every "
    "day, subscribe now, then let's keep going.",
]
SHORT_LINE = "Subscribe for one simple health tip every day."
LAST_MID: str | None = None  # the line added mid-video (left out of the second Short)


def _spoken(text: str) -> str:
    """Topic names are written for the screen; make them safe for the voice."""
    text = re.sub(r"\bvs\.?\b", "versus", text, flags=re.I)
    return text.replace("&", "and").replace("/", " or ").replace(":", ",").strip().rstrip(".")


def series_for(playlist: str, cfg: dict) -> str | None:
    return (cfg.get("series") or {}).get(playlist)


def next_in_series(playlist: str, after: Path | None, bank: list[Path]) -> str | None:
    """The topic of the next unused bank script in the same playlist (the next episode of this series)."""
    for f in bank:
        if after and f.name <= after.name:
            continue
        data = yaml.safe_load(f.read_text())
        if data["plan"].get("playlist") == playlist:
            return data.get("queue_topic") or data["plan"]["topic"]
    return None


def _mid_index(scenes) -> int:
    """The scene ending about 40-60 seconds in (roughly 100-150 spoken words), never the hook or the outro."""
    words = 0
    for i, s in enumerate(scenes[:-1]):
        words += len(s.narration.split())
        if i >= 1 and words >= 100:
            return i
    return min(1, len(scenes) - 2)


def apply(plan, cfg: dict, day: int, next_topic: str | None) -> str | None:
    """Adds the series, the early subscribe line and the next-episode teaser to the plan. Returns the line
    added mid-video (so the second Short, cut from a middle scene, can leave it out)."""
    if not cfg.get("enabled", True) or len(plan.scenes) < 3:
        return None
    series = series_for(plan.playlist, cfg)
    mid = None
    if series:
        i = _mid_index(plan.scenes)
        if "subscribe" not in plan.scenes[i].narration.lower():
            mid = MID_LINES[day % len(MID_LINES)].format(series=series)
            plan.scenes[i].narration = f"{plan.scenes[i].narration.rstrip()} {mid}"

        outro = plan.scenes[-1]
        teaser = (f"Next in our {series} series: {_spoken(next_topic)}. Subscribe to Health Support Studio so "
                  "you don't miss it." if next_topic else
                  f"Subscribe to Health Support Studio for the next video in our {series} series.")
        sentences = re.split(r"(?<=[.!?])\s+", outro.narration.strip())
        kept = [s for s in sentences if "subscribe" not in s.lower()]
        outro.narration = " ".join(kept + [teaser])

        top = f"📌 Part of our {series} series." + (f" Next: {next_topic}." if next_topic else "")
        plan.description = f"{top}\n\n{plan.description}"

    if plan.short_scenes and "subscribe" not in plan.short_scenes[-1].narration.lower():
        plan.short_scenes[-1].narration = f"{plan.short_scenes[-1].narration.rstrip()} {SHORT_LINE}"
    return mid
