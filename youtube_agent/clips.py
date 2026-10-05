"""Makeover Shorts from AI video clips you make yourself (Google Flow, Dreamina, Qwen...).

You upload the clips of one makeover (usually 3 clips of ~8 seconds: clean up, build, finish) into the
`rrs_inbox/` folder of the repository. This joins them into a vertical Short with a title, the clips' own
work sounds plus soft music, and a BEFORE -> AFTER reveal at the end, then schedules it on YouTube (with
the "altered or synthetic content" label) and leaves it ready for the Instagram/Facebook workflow.
The clips are then moved to `rrs_clips/<date>-<name>/`, where the weekly long compilation finds them.

Clips belong to the same makeover when they are uploaded together. Files named by Google Flow end in a
timestamp (..._20261004133358.mp4); clips made more than `group_gap_hours` apart are treated as different
makeovers, and they are joined in the order they were made (otherwise in name order).

Usage (from the repo root; the workflow sets CHANNEL=restore_remake):
    CHANNEL=restore_remake python -m youtube_agent.clips              # process the inbox and upload
    CHANNEL=restore_remake python -m youtube_agent.clips --dry-run    # make the videos, don't upload or move
    CHANNEL=restore_remake python -m youtube_agent.clips --compile    # weekly long compilation
"""

import argparse
import base64
import datetime as dt
import io
import json
import os
import random
import re
import shutil
import subprocess
from pathlib import Path

import requests
from PIL import Image

from . import makeover, visuals
from .editor import ffmpeg_bin
from .main import (OUTPUT_DIR, load_config, load_history, next_publish_time, save_history, slugify,
                   write_summary)

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "rrs_inbox"
DONE = ROOT / "rrs_clips"
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm"}
FPS = 30
SW, SH = 1080, 1920        # Short
W, H = 1920, 1080          # long compilation
TEXT_MODEL = os.environ.get("GEMINI_TEXT_MODEL", "gemini-2.5-flash")


# ---------------------------------------------------------------- inbox
def _made_at(p: Path) -> dt.datetime | None:
    m = re.search(r"(20\d{6})[_-]?(\d{6})", p.stem)
    if not m:
        return None
    try:
        return dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    except ValueError:
        return None


def inbox_groups(gap_hours: float) -> list[list[Path]]:
    """Clips in the inbox, split into makeovers. Sub-folders are one makeover each; loose files are split
    wherever two clips were made more than gap_hours apart."""
    if not INBOX.exists():
        return []
    groups = []
    for d in sorted(p for p in INBOX.iterdir() if p.is_dir()):
        clips = sorted((p for p in d.iterdir() if p.suffix.lower() in VIDEO_EXT),
                       key=lambda p: (_made_at(p) or dt.datetime.min, p.name))
        if clips:
            groups.append(clips)
    loose = sorted((p for p in INBOX.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXT),
                   key=lambda p: (_made_at(p) or dt.datetime.min, p.name))
    current: list[Path] = []
    for p in loose:
        if current:
            a, b = _made_at(current[-1]), _made_at(p)
            if a and b and (b - a).total_seconds() > gap_hours * 3600:
                groups.append(current)
                current = []
        current.append(p)
    if current:
        groups.append(current)
    return groups


def ready(group: list[Path], want: int, wait_hours: float) -> bool:
    """A makeover is made once all its clips are in, when it has its own folder (one folder = one finished
    makeover, however many clips), or when the last clip has waited long enough."""
    if len(group) >= want or group[0].parent != INBOX:
        return True
    # when the clips were uploaded (a fresh checkout gives every file the current time, so git is used)
    newest = max((_git_added_time(p) or p.stat().st_mtime) for p in group)
    return (dt.datetime.now().timestamp() - newest) > wait_hours * 3600


def _git_added_time(p: Path) -> float | None:
    r = subprocess.run(["git", "log", "-1", "--format=%ct", "--", str(p)], cwd=ROOT, capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


# ---------------------------------------------------------------- ffmpeg helpers
def _run(args: list[str]) -> None:
    r = subprocess.run([ffmpeg_bin(), "-hide_banner", "-loglevel", "error", *args], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"ffmpeg failed: {r.stderr[-1500:]}")


def probe(path: Path) -> tuple[float, bool]:
    """(duration in seconds, has audio) read from ffmpeg's own output, so ffprobe isn't needed."""
    r = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 8.0
    return dur, bool(re.search(r"Stream #.*Audio", r.stderr))


def frame(path: Path, out: Path, last: bool) -> Path:
    args = ["-y", "-sseof", "-0.15"] if last else ["-y", "-ss", "0.05"]
    _run([*args, "-i", str(path), "-frames:v", "1", "-update", "1", "-q:v", "2", str(out)])
    return out


def normalize(src: Path, out: Path, size: tuple[int, int], speed: float = 1.0) -> Path:
    """Same size, frame rate and audio format for every clip. Vertical clips in a landscape video sit on a
    blurred copy of themselves; clips without sound get silence."""
    w, h = size
    dur, has_audio = probe(src)
    pts = f",setpts=PTS/{speed},fps={FPS}" if speed != 1.0 else ""
    if h > w:
        vf = (f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={FPS}{pts},"
              "setsar=1,format=yuv420p[v]")
    else:
        vf = (f"[0:v]split[a][b];[a]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=30:3,"
              f"eq=brightness=-0.08[bg];[b]scale=-2:{h}[fg];[bg][fg]overlay=(W-w)/2:0,fps={FPS}{pts},"
              "setsar=1,format=yuv420p[v]")
    if has_audio:
        af = "[0:a]aresample=48000,aformat=channel_layouts=stereo" + (f",atempo={speed}" if speed != 1.0 else "")
        af += "[a]"
        inputs = ["-i", str(src)]
    else:
        af = "[1:a]anull[a]"
        inputs = ["-i", str(src), "-f", "lavfi", "-t", f"{dur:.2f}", "-i", "anullsrc=r=48000:cl=stereo"]
    _run(["-y", *inputs, "-filter_complex", f"{vf};{af}", "-map", "[v]", "-map", "[a]", "-t", f"{dur / speed:.2f}",
          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
          "-video_track_timescale", "15360", str(out)])  # same time base as the other parts, for joining
    return out


def join(clips: list[Path], out: Path, fade: float = 0.35) -> Path:
    """Clips joined with a short cross-fade (picture and sound)."""
    if len(clips) == 1:
        shutil.copy(clips[0], out)
        return out
    durs = [probe(c)[0] for c in clips]
    inputs, vchain, achain = [], [], []
    for c in clips:
        inputs += ["-i", str(c)]
    offset, pv, pa = 0.0, "0:v", "0:a"
    for i in range(1, len(clips)):
        offset += durs[i - 1] - fade
        vchain.append(f"[{pv}][{i}:v]xfade=transition=fade:duration={fade}:offset={offset:.3f}[v{i}]")
        achain.append(f"[{pa}][{i}:a]acrossfade=d={fade}[a{i}]")
        pv, pa = f"v{i}", f"a{i}"
    _run(["-y", *inputs, "-filter_complex", ";".join(vchain + achain), "-map", f"[{pv}]", "-map", f"[{pa}]",
          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-c:a", "aac", "-b:a", "192k", str(out)])
    return out


def still(img: Path, overlay: Path, dur: float, size: tuple[int, int], out: Path, zoom_in: bool = True) -> Path:
    """A frame held for a moment with a slow zoom and a label; silent audio so it joins with the clips."""
    w, h = size
    n = int(dur * FPS)
    z = "min(1+0.0012*on,1.1)" if zoom_in else "max(1.1-0.0012*on,1)"
    if h > w:
        base = f"[0:v]scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase,crop={w * 2}:{h * 2}"
    else:
        base = (f"[0:v]split[p][q];[p]scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase,crop={w * 2}:{h * 2},"
                f"boxblur=40:3,eq=brightness=-0.08[bg];[q]scale=-2:{h * 2}[fg];[bg][fg]overlay=(W-w)/2:0")
    vf = (f"{base},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={w}x{h}:fps={FPS},setsar=1[bg2];"
          "[bg2][1:v]overlay=0:0:format=auto,format=yuv420p[v]")
    _run(["-y", "-loop", "1", "-framerate", str(FPS), "-t", f"{dur}", "-i", str(img), "-i", str(overlay),
          "-f", "lavfi", "-t", f"{dur}", "-i", "anullsrc=r=48000:cl=stereo", "-filter_complex", vf,
          "-map", "[v]", "-map", "2:a", "-t", f"{dur}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
          "-c:a", "aac", "-b:a", "192k", str(out)])
    return out


def reveal(before: Path, after: Path, size: tuple[int, int], work: Path, endcard: bool = True) -> Path:
    """BEFORE held briefly, then a wipe to AFTER (with the follow end card on the Short)."""
    w, h = size
    tag = "v" if h > w else "h"
    a = still(before, makeover._label("BEFORE", size, (87, 83, 78), work / f"rv_b_{tag}.png"), 1.8, size,
              work / f"rv_a_{tag}.mp4", zoom_in=False)
    ov = makeover._label("AFTER", size, (13, 148, 136), work / f"rv_l_{tag}.png")
    if endcard:
        question = ("Which place should", "we restore next?")
        card = Image.open(makeover._endcard(size, work / f"rv_e_{tag}.png", question)).convert("RGBA")
        lab = Image.open(ov).convert("RGBA")
        lab.alpha_composite(card)
        lab.save(ov)
    b = still(after, ov, 4.2, size, work / f"rv_c_{tag}.mp4")
    out = work / f"reveal_{tag}.mp4"
    tr = "wipeup" if h > w else "wiperight"
    _run(["-y", "-i", str(a), "-i", str(b), "-filter_complex",
          f"[0:v][1:v]xfade=transition={tr}:duration=1.0:offset=0.9,format=yuv420p[v];"
          "[0:a][1:a]acrossfade=d=1.0[a]", "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast",
          "-crf", "19", "-c:a", "aac", str(out)])
    return out


def title_overlay(text: str, size: tuple[int, int], out: Path) -> Path:
    """Hook text across the top for the first seconds, plus the channel tag and an 'AI-generated' note."""
    w, h = size
    u = w / 1080 if h > w else w / 1920
    img = Image.open(makeover._label("BEFORE", size, (87, 83, 78), out.with_suffix(".base.png"))).convert("RGBA")
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    size_px = int(70 * u)
    f = visuals.font(size_px, 800)
    words, lines, line = text.split(), [], ""
    for wd in words:
        trial = f"{line} {wd}".strip()
        if d.textlength(trial, font=f) > w * 0.86 and line:
            lines.append(line)
            line = wd
        else:
            line = trial
    lines.append(line)
    y = int((430 if h > w else 200) * u)
    for ln in lines[:3]:
        lw = d.textlength(ln, font=f)
        d.text(((w - lw) / 2, y), ln, font=f, fill=(255, 255, 255), stroke_width=max(4, size_px // 12),
               stroke_fill=(0, 0, 0))
        y += int(size_px * 1.2)
    img.save(out)
    return out


def ai_note(size: tuple[int, int], out: Path) -> Path:
    from PIL import ImageDraw
    w, h = size
    u = w / 1080 if h > w else w / 1920
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = visuals.font(int(26 * u), 700)
    text = "AI-generated concept"
    tw = d.textlength(text, font=f)
    x, y = w - tw - int(40 * u), int((150 if h > w else 30) * u)
    d.rounded_rectangle((x - 16 * u, y - 8 * u, x + tw + 16 * u, y + 40 * u), int(20 * u), fill=(0, 0, 0, 140))
    d.text((x, y), text, font=f, fill=(255, 255, 255, 230))
    img.save(out)
    return out


def _with_overlay(video: Path, overlay: Path, out: Path) -> Path:
    _run(["-y", "-i", str(video), "-i", str(overlay), "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,"
          "format=yuv420p[v]", "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
          "-c:a", "copy", "-video_track_timescale", "15360", str(out)])
    return out


def finish(body: Path, overlays: list[tuple[Path, float | None]], music_vol: float, out: Path,
           rng: random.Random, narration: Path | None = None, narration_start: float = 0.8) -> Path:
    """Overlays on the joined video (each until its end time, or the whole video), the clips' sound with
    soft music underneath and the host's narration on top, loudness evened out for phones."""
    dur, _ = probe(body)
    music = makeover._music(dur, out.parent / f"music_{out.stem}.m4a", rng)
    inputs = ["-i", str(body), "-i", str(music)]
    if narration:
        inputs += ["-i", str(narration)]
    chain, prev = [], "0:v"
    first = 3 if narration else 2
    for i, (ov, until) in enumerate(overlays):
        inputs += ["-i", str(ov)]
        en = f":enable='lte(t,{until:.2f})'" if until else ""
        chain.append(f"[{prev}][{i + first}:v]overlay=0:0:format=auto{en}[o{i}]")
        prev = f"o{i}"
    chain.append(f"[{prev}]format=yuv420p[v]")
    if narration:  # work sounds and music step back while the host talks
        ms = int(narration_start * 1000)
        chain.append(f"[1:a]volume={music_vol * 0.6:.3f}[m];[0:a]volume=0.45[c];"
                     f"[2:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms},volume=1.6[n];"
                     "[c][m][n]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[a]")
    else:
        chain.append(f"[1:a]volume={music_vol}[m];[0:a][m]amix=inputs=2:duration=first:normalize=0,"
                     "loudnorm=I=-15:TP=-1.5:LRA=11[a]")
    _run(["-y", *inputs, "-filter_complex", ";".join(chain), "-map", "[v]", "-map", "[a]", "-c:v", "libx264",
          "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
          "-movflags", "+faststart", str(out)])
    return out


# ---------------------------------------------------------------- titles
# ---------------------------------------------------------------- scripts: a new one for every Short
PLACE_WORDS = ("rooftop", "backyard", "garden", "terrace", "balcony", "garage", "kitchen", "bathroom", "bedroom",
               "living room", "house", "car", "bike", "porch", "yard", "attic", "basement", "pool", "room")
WORK = {  # what the crew does, in order (three are picked per Short)
    "rooftop": ["swept away years of trash", "pressure-washed the old concrete", "laid a beautiful new floor",
                "built planter boxes along the edges", "hung string lights overhead", "brought in cozy furniture"],
    "yard": ["pulled out every dead weed", "hauled away the broken junk", "laid a new stone path",
             "rolled out fresh green grass", "planted new shrubs and flowers", "added soft garden lights"],
    "garage": ["hauled out all the junk", "swept and scrubbed the floor", "painted the walls bright white",
               "laid a tough rubber floor", "brought in the new equipment", "installed modern lighting"],
    "room": ["cleared out the old furniture", "patched and painted the walls", "laid a brand new floor",
             "hung new curtains and lights", "brought in new furniture", "added the finishing touches"],
    "kitchen": ["tore out the old cabinets", "scrubbed every surface", "fitted new cabinets",
                "installed new countertops", "added modern lighting", "styled it with fresh details"],
    "bathroom": ["ripped out the old tiles", "cleaned up years of grime", "laid fresh new tiles",
                 "installed a new vanity", "fitted a modern shower", "added warm lighting"],
    "pool": ["drained the green water", "scooped out the mud and leaves", "repaired the cracked walls",
             "laid new stone around the edge", "filled it with crystal clear water", "set up loungers and lights"],
    "car": ["washed off years of dirt", "pulled out the rusted parts", "sanded down the body",
            "sprayed on a shiny new paint job", "fitted new wheels", "polished every inch"],
    "default": ["cleared out all the trash", "scrubbed away years of dirt", "repaired everything that was broken",
                "rebuilt it piece by piece", "added fresh new details", "gave it the finishing touches"],
}
WORK_KEY = {"backyard": "yard", "garden": "yard", "yard": "yard", "porch": "yard", "terrace": "rooftop",
            "balcony": "rooftop", "bedroom": "room", "living room": "room", "attic": "room", "basement": "room",
            "house": "room", "bike": "car"}
OPENERS = ["Nobody had touched this {place} in years.", "This {place} was a total disaster.",
           "Look at this {place}. Trash, dirt, and broken everything.",
           "Would you believe someone just gave up on this {place}?", "This might be the worst {place} we've seen.",
           "Everyone walked right past this abandoned {place}.", "This {place} was forgotten for years.",
           "Could you fix a {place} this bad?", "This {place} looked completely hopeless.",
           "Abandoned, dirty, and falling apart. That was this {place}.",
           "Most people would have given up on this {place}.", "Here's a {place} nobody wanted."]
MIDDLES = ["The crew {a}, {b}, and {c}.", "First they {a}. Then they {b}, and {c}.",
           "Step by step, they {a}, {b}, and finally {c}.", "They {a}. They {b}. And then they {c}.",
           "Watch closely. They {a}, {b}, and {c}.", "Bit by bit, the crew {a}, {b}, and {c}."]
REVEALS = ["And now? Just look at it.", "The final result is unbelievable.", "From forgotten to beautiful.",
           "Same {place}. Completely new life.", "Can you believe it's the same {place}?",
           "Now it's the kind of place you never want to leave.", "What a transformation.",
           "And just like that, it's brand new.", "Honestly, this one turned out amazing."]
CTAS = ["If you loved this, share it with a friend and subscribe for more. And let me know in the comments if "
        "you want more videos like this.",
        "Share this with someone who loves a good makeover, and subscribe so you don't miss the next one. Tell me "
        "in the comments if you want more like this.",
        "Don't forget to like, share, and subscribe. And comment below if you want to see more makeovers like this.",
        "Subscribe for a new makeover every day, share it with your friends, and let me know in the comments what "
        "we should restore next.",
        "Hit subscribe, share this with a friend, and drop a comment if you want more videos like this.",
        "Want more makeovers like this? Subscribe, share this video, and tell me in the comments."]
CAPTION_CTA = "👉 Share with a friend, subscribe for a new makeover every day, and comment if you want more like this!"


def _recent_scripts(limit: int = 8) -> list[str]:
    """Narrations of the latest published makeovers, so a new Short doesn't repeat them."""
    metas = sorted(DONE.glob("*/meta.json")) if DONE.exists() else []
    out = []
    for m in metas[-limit:]:
        try:
            out.append(json.loads(m.read_text()).get("narration", ""))
        except (OSError, ValueError):
            pass
    return out


def _pick(options: list[str], recent: str, rng: random.Random, **fill) -> str:
    """A random option whose text wasn't used in the recent scripts (if possible)."""
    texts = [o.format(**fill) for o in options]
    fresh = [t for t in texts if t not in recent] or texts
    return rng.choice(fresh)


def write_script(place: str, rng: random.Random) -> str:
    """Opener + what the crew did + reveal + share/subscribe/comment, with no line reused from recent Shorts."""
    recent = " ".join(_recent_scripts())
    work = WORK[WORK_KEY.get(place, place) if WORK_KEY.get(place, place) in WORK else "default"]
    a, b, c = (work[i] for i in sorted(rng.sample(range(len(work)), 3)))
    return " ".join([_pick(OPENERS, recent, rng, place=place), _pick(MIDDLES, recent, rng, a=a, b=b, c=c),
                     _pick(REVEALS, recent, rng, place=place), _pick(CTAS, recent, rng)])


def with_cta(text: str, rng: random.Random) -> str:
    return text if "subscribe" in text.lower() else f"{text.rstrip()} {_pick(CTAS, ' '.join(_recent_scripts()), rng)}"


def describe(before: Path, after: Path, names: list[str], cfg: dict, rng: random.Random) -> dict:
    """Title, captions, tags and the narration script. Gemini (free key) looks at the first and last frame;
    without it, a fresh script is put together from many lines so no two Shorts sound the same."""
    hint = " / ".join(re.sub(r"[_-]+", " ", re.sub(r"[_-]?20\d{12}.*$", "", re.sub(r"^[0-9a-f]{8}-", "", n))).strip()
                      for n in names)
    place = next((w for w in PLACE_WORDS if w in hint.lower()), "space")
    if os.environ.get("GEMINI_API_KEY", "").strip():
        try:
            data = _gemini_describe(before, after, hint, cfg)
            data["narration"] = with_cta(data.get("narration") or write_script(place, rng), rng)
            data["caption"] = f"{data.get('caption', '').strip()} {CAPTION_CTA}".strip()
            return data
        except Exception as e:
            print(f"  (Gemini titles failed, using a fresh template script: {e})")
    recent_titles = " ".join(json.loads(m.read_text()).get("title", "") for m in DONE.glob("*/meta.json")) \
        if DONE.exists() else ""
    title = _pick([t.replace("{Place}", place.title()).replace("{place}", place)
                   for t in (cfg.get("clip_titles") or ["Abandoned {Place} Transformed ✨"])], recent_titles, rng)
    hook = rng.choice([f"Watch this abandoned {place} come back to life", f"Nobody wanted this {place}",
                       f"This {place} was a disaster", f"Can this {place} be saved?", f"Wait for the {place} reveal"])
    caption = rng.choice([f"This abandoned {place} got a second life 😍 Would you live here?",
                          f"From forgotten to beautiful ✨ What would you add to this {place}?",
                          f"Rate this {place} makeover from 1 to 10 👇", f"Same {place}, completely new life 🔨"])
    return {"title": title, "short_title": title, "hook": hook,
            "before": "ABANDONED", "after": "DREAM " + place.upper(), "caption": f"{caption} {CAPTION_CTA}",
            "tags": [f"{place} makeover", f"{place} transformation", f"abandoned {place}"],
            "narration": write_script(place, rng)}


def _gemini_describe(before: Path, after: Path, hint: str, cfg: dict) -> dict:
    parts: list[dict] = [{"text": (
        "These are the first and last frames of a short AI-generated time-lapse video where workers transform "
        f"a neglected place. The clip files were named: {hint}. Write YouTube Shorts metadata for the channel "
        "Restore Remake Studio (satisfying makeovers, US audience). Reply with JSON only, keys: "
        '"title" (max 60 chars, catchy, 1 emoji, like "Abandoned Rooftop → Dream Terrace 🌇", no hashtags), '
        '"hook" (max 45 chars, shown on screen in the first seconds, no emoji), '
        '"before" (max 2 words, upper case, e.g. "ABANDONED ROOFTOP"), "after" (max 2 words, e.g. "DREAM TERRACE"), '
        '"caption" (1-2 sentences for Instagram/Facebook ending with a question, max 2 emoji, no hashtags), '
        '"tags" (8 lowercase YouTube tags), '
        '"narration" (what the host says over the video: 4-5 short spoken sentences, 55-70 words in total, '
        'friendly storytelling about the place being cleaned, rebuilt and revealed, ending by asking viewers to '
        'share the video, subscribe, and say in the comments if they want more videos like this; plain words, '
        'no emoji, no numbers as digits). Do not claim it is a real project or real people. Every video needs '
        'a fresh script: do not reuse the wording of these earlier narrations: ' + " | ".join(_recent_scripts(5)))}]
    for p in (before, after):
        img = Image.open(p).convert("RGB")
        img.thumbnail((768, 768))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=88)
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}})
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{TEXT_MODEL}:generateContent",
                      headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"].strip()},
                      json={"contents": [{"parts": parts}],
                            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.9}},
                      timeout=90)
    if r.status_code >= 400:
        raise RuntimeError(f"{r.status_code}: {r.text[:200]}")
    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    data = json.loads(text)
    data["title"] = data["title"].strip()[:90]
    data["short_title"] = data["title"]
    data["tags"] = [t.lower() for t in data.get("tags", [])][:10]
    return data


# ---------------------------------------------------------------- one makeover
def narrate(text: str, voice_cfg: dict, out: Path, max_seconds: float) -> Path | None:
    """The host's narration in the channel voice (your clone when set up); None if it can't be made or
    is longer than the video."""
    from . import voice

    try:
        dur, _ = voice.narrate_scene(text, voice_cfg, out)
    except Exception as e:
        print(f"  (No narration: {e})")
        return None
    if dur > max_seconds:
        print(f"  (Narration is {dur:.0f} s, longer than the video - left out)")
        return None
    return out


def make_short(group: list[Path], workdir: Path, cfg: dict, rng: random.Random,
               voice_cfg: dict | None = None) -> dict:
    work = workdir / "build"
    work.mkdir(parents=True, exist_ok=True)
    before = frame(group[0], work / "before.jpg", last=False)
    after = frame(group[-1], work / "after.jpg", last=True)
    meta = describe(before, after, [p.name for p in group], cfg, rng)
    print(f"  Title: {meta['title']}")

    print(f"  Joining {len(group)} clips...")
    # very short makeovers (one 8-10 s clip) are slowed down a little so each step can be seen
    total = sum(probe(p)[0] for p in group)
    speed = max(0.75, min(1.0, total / cfg.get("min_clip_seconds", 13)))
    if speed < 1.0:
        print(f"  Short makeover ({total:.0f} s) - playing at {speed:.2f}x")
    norm = [normalize(p, work / f"n{i}_v.mp4", (SW, SH), speed) for i, p in enumerate(group)]
    body = join(norm, work / "body_v.mp4")
    parts = [body]
    min_len = cfg.get("min_short_seconds", 30)
    if probe(body)[0] + 6.5 < min_len:  # too short for a good Short: show the whole makeover once more, faster
        need = min_len - probe(body)[0] - 6.0
        rate = min(1.5, max(0.8, (total - 1.0) / max(need, 1.0)))
        print(f"  Adding a replay at {rate:.1f}x so the Short is long enough")
        fast = [normalize(p, work / f"r{i}_v.mp4", (SW, SH), rate) for i, p in enumerate(group)]
        replay = join(fast, work / "replay_v.mp4")
        tag = makeover._label("ONE MORE TIME" if rate < 1.2 else f"REPLAY {rate:.1f}X", (SW, SH), (245, 158, 11),
                              work / "replay_label.png")
        parts.append(_with_overlay(replay, tag, work / "replay_tag_v.mp4"))
    parts.append(reveal(before, after, (SW, SH), work))
    full = join(parts, work / "full_v.mp4", fade=0.4)
    hook = title_overlay(meta.get("hook") or meta["title"], (SW, SH), work / "hook_v.png")
    note = ai_note((SW, SH), work / "ai_v.png")
    social = workdir / "social"
    social.mkdir(exist_ok=True)
    speech = None
    if voice_cfg and cfg.get("narration", True) and meta.get("narration"):
        print("  Recording the narration...")
        speech = narrate(meta["narration"], voice_cfg, work / "narration.wav", probe(full)[0] - 1.5)
    short = finish(full, [(hook, 2.6), (note, None)], cfg.get("music_volume", 0.18), social / "short.mp4", rng,
                   narration=speech)
    meta["clips"] = [p.name for p in group]
    meta["duration"] = round(probe(short)[0], 1)
    return {"short": short, "meta": meta, "before": before, "after": after}


def _footer(config: dict) -> str:
    return (config["youtube"].get("clip_description_footer") or config["youtube"].get("description_footer")
            or "").strip()


def _next_slot(yt: dict, history: list[dict], kind: str) -> dt.datetime:
    """The next free publish time for this kind of video. Shorts can have several slots a day
    (clip_publish_times); each new Short takes the earliest slot after the last one scheduled."""
    times = [dt.datetime.fromisoformat(h["publish_at"].replace("Z", "+00:00")) for h in history
             if h.get("publish_at") and h.get("kind") == kind]
    last = max(times) if times else None
    tz = yt.get("auto_publish_timezone", "America/New_York")
    if kind == "compilation":
        slots = [yt.get("compilation_publish_time") or "11:00"]
    else:
        slots = yt.get("clip_publish_times") or [yt.get("clip_publish_time") or yt.get("auto_publish_time", "13:00")]
    return min(next_publish_time(t, tz, after=last) for t in slots)


def process_inbox(config: dict, history: list[dict], dry_run: bool) -> int:
    cfg = config.get("clips") or {}
    groups = inbox_groups(cfg.get("group_gap_hours", 3))
    groups = [g for g in groups if ready(g, cfg.get("clips_per_makeover", 3), cfg.get("wait_hours", 6))]
    groups = groups[:1]  # one per run: the Instagram/Facebook workflow posts one Short per run; the rest wait
    if not groups:
        print("No finished makeover in rrs_inbox/ yet - nothing to do.")
        write_summary(["## No new clips", "Upload the clips of one makeover into `rrs_inbox/` to make a Short."])
        return 0
    visuals.set_brand(config.get("brand"))
    visuals.ensure_fonts()
    yt_base = dict(config["youtube"])
    lang = config["channel"].get("language_code", "en-US")
    summary = []
    for n, group in enumerate(groups, 1):
        print(f"\n=== Makeover {n} of {len(groups)}: {', '.join(p.name for p in group)} ===")
        rng = random.Random(sum(p.stat().st_size for p in group))
        stamp = (_made_at(group[0]) or dt.datetime.now()).strftime("%Y%m%d-%H%M")
        workdir = OUTPUT_DIR / f"{stamp}-clips"
        made = make_short(group, workdir, cfg, rng, config.get("voice"))
        meta = made["meta"]
        slug = f"{stamp}-{slugify(meta['title'])[:40]}"
        tags = list(dict.fromkeys(meta.get("tags", []) + cfg.get("tags", [])))[:15]
        hashtags = " ".join(cfg.get("hashtags", []))
        caption = f"{meta['caption']} {hashtags}".strip()
        entry = {"date": dt.datetime.now().isoformat(timespec="seconds"), "kind": "clip_short",
                 "title": meta["title"], "topic": meta["title"], "style": "AI Clip Makeover", "folder": slug}
        if dry_run:
            print(f"  Dry run - not uploading. Short: {made['short']}")
            summary.append(f"- (dry run) {meta['title']} - {meta['duration']} s")
            continue

        from . import uploader

        yt = dict(yt_base)
        publish_at = _next_slot(yt, history, "clip_short")
        yt["privacy"] = "private"
        yt["publish_at"] = publish_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        description = f"{meta['caption']}\n\n{hashtags}\n\n{_footer(config)}"
        print(f"  Uploading the Short (goes public {yt['publish_at']} UTC)...")
        video_id = uploader.upload_video(made["short"], None, meta["short_title"][:90] + " #Shorts", description,
                                         tags + ["shorts"], yt, lang)
        entry.update(youtube_id=video_id, publish_at=yt["publish_at"])
        history.append(entry)
        save_history(history)
        if yt.get("playlists", True):
            try:
                uploader.add_to_playlists(video_id, [yt.get("shorts_playlist", "Makeover Shorts")],
                                          yt.get("playlist_description"))
            except Exception as e:
                print(f"  (Could not add to playlist: {e})")
        (workdir / "social" / "social.json").write_text(json.dumps({
            "youtube_id": video_id, "title": meta["title"], "caption": caption,
            "publish_at": yt["publish_at"]}, indent=2))

        # keep the clips for the weekly compilation; the inbox is left empty
        dest = DONE / slug
        dest.mkdir(parents=True, exist_ok=True)
        for p in group:
            shutil.move(str(p), dest / p.name)
        (dest / "meta.json").write_text(json.dumps({**meta, "youtube_id": video_id, "publish_at": yt["publish_at"],
                                                    "compiled": False}, indent=2))
        for d in INBOX.iterdir():
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
        summary += [f"### {meta['title']}", f"- Short ({meta['duration']} s): https://studio.youtube.com/video/{video_id}/edit",
                    f"- Goes public {yt['publish_at']} (UTC). To stop it, set it to Private."]
    print("\n".join(summary))
    write_summary(["## Restore Remake Studio - new makeover Shorts", *summary])
    return len(groups)


# ---------------------------------------------------------------- long compilation
def compile_long(config: dict, history: list[dict], dry_run: bool, force: bool = False) -> None:
    """All makeovers not used in a compilation yet, one after another in a landscape video, each with a
    title card and its before -> after reveal."""
    cfg = config.get("clips") or {}
    todo = []
    for d in sorted(DONE.iterdir()) if DONE.exists() else []:
        mf = d / "meta.json"
        if mf.exists():
            m = json.loads(mf.read_text())
            if not m.get("compiled"):
                todo.append((d, m))
    need = cfg.get("compilation_min_makeovers", 5)
    if len(todo) < need and not force:
        print(f"Only {len(todo)} new makeovers (need {need}) - no compilation this time.")
        write_summary(["## No compilation yet", f"{len(todo)} of {need} makeovers ready."])
        return
    if not todo:
        print("No makeovers to compile.")
        return
    visuals.set_brand(config.get("brand"))
    visuals.ensure_fonts()
    rng = random.Random(len(todo))
    workdir = OUTPUT_DIR / f"{dt.datetime.now():%Y%m%d-%H%M}-compilation"
    work = workdir / "build"
    work.mkdir(parents=True, exist_ok=True)
    parts = []
    for i, (d, m) in enumerate(todo, 1):
        clips = sorted((p for p in d.iterdir() if p.suffix.lower() in VIDEO_EXT),
                       key=lambda p: (_made_at(p) or dt.datetime.min, p.name))
        print(f"  {i}/{len(todo)} {m['title']}")
        before = frame(clips[0], work / f"b{i}.jpg", last=False)
        after = frame(clips[-1], work / f"a{i}.jpg", last=True)
        card = makeover._label(f"MAKEOVER {i}", (W, H), (245, 158, 11), work / f"card{i}.png",
                               step=re.sub(r"[^\w\s→&'-]", "", m["title"]).strip().upper()[:40])
        segs = [still(before, card, 2.2, (W, H), work / f"t{i}.mp4")]
        segs += [normalize(p, work / f"n{i}_{k}.mp4", (W, H)) for k, p in enumerate(clips)]
        segs.append(reveal(before, after, (W, H), work, endcard=False))
        parts.append(join(segs, work / f"part{i}.mp4"))
    body = join(parts, work / "body.mp4", fade=0.6)
    note = ai_note((W, H), work / "ai_h.png")
    final = finish(body, [(note, None)], cfg.get("music_volume", 0.18), workdir / "final.mp4", rng)
    n = len(todo)
    title = rng.choice(cfg.get("compilation_titles") or ["{n} Satisfying Makeovers: Abandoned to Amazing"]).replace(
        "{n}", str(n))
    thumb = makeover.make_thumbnail(work / "b1.jpg", work / f"a{n}.jpg", "ABANDONED", "AMAZING",
                                    workdir / "thumbnail.jpg")
    lines = "\n".join(f"{i}. {m['title']}" for i, (_, m) in enumerate(todo, 1))
    description = (f"{n} abandoned places brought back to life, one after another. Which one is your favorite?\n\n"
                   f"In this video:\n{lines}\n\n{' '.join(cfg.get('hashtags', []))}\n\n{_footer(config)}")
    dur = probe(final)[0]
    print(f"  Compilation: {title} ({dur / 60:.1f} min)")
    if dry_run:
        print(f"  Dry run - not uploading: {final}")
        return

    from . import uploader

    yt = dict(config["youtube"])
    publish_at = _next_slot(yt, history, "compilation")
    yt["privacy"] = "private"
    yt["publish_at"] = publish_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    tags = list(dict.fromkeys(["makeover compilation", "satisfying transformation", "abandoned restoration",
                               *cfg.get("tags", [])]))[:15]
    video_id = uploader.upload_video(final, thumb, title, description, tags, yt,
                                     config["channel"].get("language_code", "en-US"))
    history.append({"date": dt.datetime.now().isoformat(timespec="seconds"), "kind": "compilation", "title": title,
                    "topic": title, "style": "AI Clip Compilation", "youtube_id": video_id,
                    "publish_at": yt["publish_at"], "makeovers": [d.name for d, _ in todo]})
    save_history(history)
    if yt.get("playlists", True):
        try:
            uploader.add_to_playlists(video_id, [cfg.get("compilation_playlist", "Makeover Compilations")],
                                      yt.get("playlist_description"))
        except Exception as e:
            print(f"  (Could not add to playlist: {e})")
    for d, m in todo:
        m["compiled"] = video_id
        (d / "meta.json").write_text(json.dumps(m, indent=2))
    write_summary([f"## {title}", f"- {n} makeovers, {dur / 60:.1f} min",
                   f"- Review: https://studio.youtube.com/video/{video_id}/edit",
                   f"- Goes public {yt['publish_at']} (UTC)."])


def main() -> None:
    parser = argparse.ArgumentParser(description="Makeover Shorts and compilations from your AI clips")
    parser.add_argument("--dry-run", action="store_true", help="Make the videos but don't upload or move clips")
    parser.add_argument("--compile", action="store_true", help="Make the long compilation instead")
    parser.add_argument("--force", action="store_true", help="Compile even with fewer makeovers than the minimum")
    args = parser.parse_args()
    config, history = load_config(), load_history()
    if args.compile:
        compile_long(config, history, args.dry_run, args.force)
    else:
        process_inbox(config, history, args.dry_run)


if __name__ == "__main__":
    main()
