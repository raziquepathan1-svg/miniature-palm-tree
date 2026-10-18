"""Gives viewers a reason to subscribe: the channel runs 5-part series (one theme for 5 days in a row, then a
new series). Each video says which part it is, asks for the subscribe early (after the first useful part, not
only at the end where most viewers have already left) and names the next part in the outro. Shorts end with a
subscribe line too."""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

MID_LINES = [
    "Quick note: this is part {n} of our {total} part series, {series}. Every day I explain one health topic in "
    "plain words, so if this is helping you, subscribe and you won't miss the next part.",
    "By the way, this video is part {n} of {total} in our {series} series. If you're finding this useful, "
    "subscribe so the next part finds you.",
    "This is part {n} of our {total} part {series} series. If you want simple, trustworthy health information "
    "every day, subscribe now, then let's keep going.",
]
SHORT_LINE = "Subscribe for one simple health tip every day."
LAST_MID: str | None = None  # the line added mid-video (left out of the second Short)
LAST_EP = None  # today's series episode (set by main)
SHORT1_HOOK: str | None = None  # the first new-style Short's hook, so the second one takes another angle


@dataclass
class Episode:
    series: str
    n: int
    total: int
    bank_file: Path
    next_topic: str | None   # the next part of this series, or the first video of the next series
    next_series: str | None  # set on the last part: the series that starts next


def _spoken(text: str) -> str:
    """Topic names are written for the screen; make them safe for the voice."""
    text = re.sub(r"\bvs\.?\b", "versus", text, flags=re.I)
    return text.replace("&", "and").replace("/", " or ").replace(":", ",").strip().rstrip(".")


def series_for(playlist: str, cfg: dict) -> str | None:
    return (cfg.get("series") or {}).get(playlist)


def _load(f: Path) -> dict:
    return yaml.safe_load(f.read_text())


def _topic(f: Path) -> str:
    d = _load(f)
    return d.get("queue_topic") or d["plan"]["topic"]


def _by_series(bank: list[Path], cfg: dict) -> dict[str, list[Path]]:
    out: dict[str, list[Path]] = {}
    for f in bank:
        s = series_for(_load(f)["plan"].get("playlist", ""), cfg)
        if s:
            out.setdefault(s, []).append(f)
    first = cfg.get("first") or []  # scripts that should come early in their series (strong or seasonal topics)
    for fs in out.values():
        fs.sort(key=lambda f: (first.index(f.name) if f.name in first else len(first), f.name))
    return out


def _new_series(groups: dict[str, list[Path]], total: int, skip: str | None, order: list | None = None) -> str | None:
    """The series to start next: one with enough scripts for all its parts. The config's `order` (series that
    get the most views first) decides; otherwise the one earliest in the bank."""
    ready = [s for s, fs in groups.items() if len(fs) >= total and s != skip]
    for s in order or []:
        if s in ready:
            return s
    return min(ready, key=lambda s: groups[s][0].name) if ready else None


def next_episode(history: list[dict], bank: list[Path], cfg: dict) -> Episode | None:
    """Which series and part today's video is, and its bank script. None = no series (old behaviour)."""
    if not cfg.get("enabled", True) or not cfg.get("series"):
        return None
    total = int(cfg.get("parts", 5))
    groups = _by_series(bank, cfg)
    last = next((h for h in reversed(history) if h.get("series") and h.get("status") != "rejected_by_fact_check"),
                None)
    if last and last.get("episode", total) < total and groups.get(last["series"]):
        series, n = last["series"], last["episode"] + 1
    else:
        series, n = _new_series(groups, total, last and last.get("series"), cfg.get("order")), 1
    if not series:
        return None
    files = groups[series]
    if n < total and len(files) > 1:
        return Episode(series, n, total, files[0], _topic(files[1]), None)
    rest = {s: [f for f in fs if f != files[0]] for s, fs in groups.items()}
    upcoming = _new_series(rest, total, series, cfg.get("order"))
    return Episode(series, n, total, files[0], _topic(rest[upcoming][0]) if upcoming else None, upcoming)


def _mid_index(scenes, after_words: int = 100) -> int:
    """The scene ending after about `after_words` spoken words (100 = 40-60 s, 300 = about 2 minutes),
    never the hook or the outro."""
    words = 0
    for i, s in enumerate(scenes[:-1]):
        words += len(s.narration.split())
        if i >= 1 and words >= after_words:
            return i
    return min(1, len(scenes) - 2)


def apply(plan, ep: Episode | None, day: int, bridge: str | None = None, subscribe_after: int = 100) -> str | None:
    """Adds the series part, the subscribe line and the ending to the plan. The ending is the next-part teaser,
    or (bridge given) a 20-second bridge to a related video followed by one short line about the next part.
    Returns the line added mid-video (so the second Short, cut from a middle scene, can leave it out)."""
    mid = None
    if ep and len(plan.scenes) >= 3:
        i = _mid_index(plan.scenes, subscribe_after)
        if "subscribe" not in plan.scenes[i].narration.lower():
            mid = MID_LINES[day % len(MID_LINES)].format(n=ep.n, total=ep.total, series=ep.series)
            plan.scenes[i].narration = f"{plan.scenes[i].narration.rstrip()} {mid}"

        if ep.next_series and ep.next_topic:
            teaser = (f"That's the end of our {ep.series} series. Next, we start a brand new series, "
                      f"{ep.next_series}, beginning with {_spoken(ep.next_topic)}. Subscribe to Health Support "
                      "Studio so you don't miss it.")
            top = (f"📌 {ep.series}: part {ep.n} of {ep.total} (final part). "
                   f"Next series: {ep.next_series}, starting with {ep.next_topic}.")
        elif ep.next_topic:
            teaser = (f"Next, in part {ep.n + 1} of our {ep.series} series: {_spoken(ep.next_topic)}. "
                      "Subscribe to Health Support Studio so you don't miss it.")
            top = f"📌 {ep.series}: part {ep.n} of {ep.total}. Next: {ep.next_topic}."
        else:
            teaser = "Subscribe to Health Support Studio for a new health video every day."
            top = f"📌 {ep.series}: part {ep.n} of {ep.total}."
        if bridge:  # no goodbye: the bridge sends viewers on; the series gets one short line
            nxt = (f"Part {ep.n + 1} is next in this series. Subscribe so it finds you." if ep.next_topic and
                   not ep.next_series else f"A brand new series, {ep.next_series}, starts next. Subscribe so "
                   "you don't miss it." if ep.next_series else "Subscribe for a new health video every day.")
            teaser = f"{bridge} {nxt}"
        outro = plan.scenes[-1]
        sentences = re.split(r"(?<=[.!?])\s+", outro.narration.strip())
        outro.narration = " ".join([s for s in sentences if "subscribe" not in s.lower()] + [teaser])
        plan.description = f"{top}\n\n{plan.description}"
        part = f" (Part {ep.n}/{ep.total})"
        if len(plan.title) + len(part) <= 70:
            plan.title += part

    if plan.short_scenes and "subscribe" not in plan.short_scenes[-1].narration.lower():
        plan.short_scenes[-1].narration = f"{plan.short_scenes[-1].narration.rstrip()} {SHORT_LINE}"
    return mid


REEL_FOLLOW = "Follow us for one simple health tip every day."
_OFF_PLATFORM = re.compile(r"youtube|channel|subscrib|full video|link", re.I)


def native_reel(scenes: list, follow: str = REEL_FOLLOW) -> list:
    """The Instagram/Facebook version of a Short: the ending asks people to follow the page there, instead of
    sending them to YouTube (Instagram and Facebook show posts that send people away to fewer people)."""
    *body, last = scenes
    kept = [x for x in re.split(r"(?<=[.!?])\s+", last.narration.strip()) if x and not _OFF_PLATFORM.search(x)]
    update = {"narration": " ".join(kept + [follow])}
    if last.layout == "outro":
        update.update(heading="Follow for more", points=["One simple health tip every day"])
    return body + [last.model_copy(update=update)]
