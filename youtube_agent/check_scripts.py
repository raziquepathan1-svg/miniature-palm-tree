"""Checks the pre-written scripts in script_bank/ before they are used.

    python -m youtube_agent.check_scripts            # length, layout and on-screen text limits
    python -m youtube_agent.check_scripts --links    # also check that every source link opens
"""

import re
import sys

import yaml

from .main import SCRIPT_BANK, load_config
from .planner import VideoPlan

# Things the text-to-speech voice may read wrongly; narration must spell them out.
# Sites that block automated requests (they answer 404 even for real pages); checked by hand instead.
NO_ROBOT_CHECK = ("fda.gov",)

TTS_BAD = re.compile(r"\bmg\b|\be\.g\.|\bi\.e\.|%|°|/|&|\bvs\b|\bDr\b")


def words(scenes) -> int:
    return sum(len(s.narration.split()) for s in scenes)


def check(path, config) -> list[str]:
    errs = []
    try:
        data = yaml.safe_load(path.read_text())
        plan = VideoPlan.model_validate(data["plan"])
    except Exception as e:
        return [f"cannot load: {e}"]
    styles = {s["name"]: s for s in config["video"]["styles"]}
    style = styles.get(data.get("style"))
    if not style:
        errs.append(f"unknown style {data.get('style')!r}")
    shorts = (style or {}).get("format") == "shorts"
    if plan.playlist not in config["channel"]["playlists"]:
        errs.append(f"playlist {plan.playlist!r} not in config")
    if not data.get("sources"):
        errs.append("no sources")
    if len(plan.title) > 70:
        errs.append(f"title too long ({len(plan.title)})")
    if not 8 <= len(plan.tags) <= 15:
        errs.append(f"{len(plan.tags)} tags")
    if not plan.short_title.endswith("#Shorts") or len(plan.short_title) > 60:
        errs.append("short_title must end with #Shorts and be under 60 characters")
    if "http" in plan.short_caption:
        errs.append("link in short_caption")
    if plan.thumbnail_highlight.upper() not in plan.thumbnail_text.upper():
        errs.append("thumbnail_highlight not in thumbnail_text")
    n = words(plan.scenes)
    if shorts:
        if not 90 <= n <= 135:
            errs.append(f"Short is {n} words (want 90-135)")
        if plan.short_scenes:
            errs.append("short_scenes must be empty for a Quick Short")
    else:
        if not 420 <= n <= 680:
            errs.append(f"video is {n} words (want 420-680)")
        m = words(plan.short_scenes)
        if not 2 <= len(plan.short_scenes) <= 4 or not 65 <= m <= 130:
            errs.append(f"companion Short: {len(plan.short_scenes)} scenes, {m} words (want 2-4, 65-130)")
    for group, scenes in (("scene", plan.scenes), ("short scene", plan.short_scenes)):
        if scenes and (scenes[0].layout != "title" or scenes[-1].layout != "outro"):
            errs.append(f"{group}s must start with 'title' and end with 'outro'")
        for i, s in enumerate(scenes, 1):
            where = f"{group} {i}"
            if len(s.narration) > 900:
                errs.append(f"{where}: narration over 900 characters")
            if TTS_BAD.search(s.narration):
                errs.append(f"{where}: narration has {TTS_BAD.search(s.narration).group()!r}")
            if len(s.heading.split()) > 6:
                errs.append(f"{where}: heading over 6 words")
            if len(s.points) > 4 or any(len(p.split()) > 8 for p in s.points):
                errs.append(f"{where}: too many / too long points")
            if s.layout == "myth_fact" and len(s.points) != 2:
                errs.append(f"{where}: myth_fact needs exactly 2 points")
    text = yaml.safe_dump(data).lower()
    if "nurse" in text.replace("doctor, nurse or pharmacist", ""):
        errs.append("mentions 'nurse'")
    return errs


def broken_links(path) -> list[str]:
    import requests

    errs = []
    for source in yaml.safe_load(path.read_text()).get("sources", []):
        url = re.search(r"https?://\S+", source)
        if not url:
            errs.append(f"source has no link: {source}")
            continue
        if any(domain in url.group() for domain in NO_ROBOT_CHECK):
            continue
        try:
            r = requests.get(url.group(), timeout=30, allow_redirects=True,
                             headers={"User-Agent": "Mozilla/5.0 (link check)"})
            if r.status_code >= 400 and r.status_code not in (401, 403, 405, 429):  # some sites block robots
                errs.append(f"link {r.status_code}: {url.group()}")
        except requests.RequestException as e:
            errs.append(f"link failed ({type(e).__name__}): {url.group()}")
    return errs


def main() -> None:
    config = load_config()
    files = sorted(SCRIPT_BANK.glob("*.yaml"))
    bad = 0
    for f in files:
        errs = check(f, config) + (broken_links(f) if "--links" in sys.argv else [])
        bad += bool(errs)
        print(f"{'OK  ' if not errs else 'FAIL'} {f.name}" + "".join(f"\n     - {e}" for e in errs))
    print(f"\n{len(files) - bad}/{len(files)} scripts OK")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
