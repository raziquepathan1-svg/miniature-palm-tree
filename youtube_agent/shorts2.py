"""Shorts that stop the scroll: a hook made for each topic over the host's face in the first second, one
complete useful answer told in quick beats (a new picture every few seconds, big word-by-word captions),
a preview of what the full video adds, and the series part with a pointer to the full video.

    python -m youtube_agent.shorts2 sample SCRIPT.yaml OUTDIR    # one Short from a script-bank file
"""

import datetime as dt
import json
import random
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
from pydantic import BaseModel, Field

from . import visuals
from .editor import ffmpeg_bin

W, H, FPS = 1080, 1920, 30
HERE = Path(__file__).resolve().parent
HOST_CLIPS = HERE.parent / "branding/health-support-studio/avatar/broll"
# (background, text) pairs for the hook card; one per day so the first frames don't all look alike
HOOK_COLORS = [((255, 212, 0), (11, 37, 69)), ((255, 107, 107), (255, 255, 255)), ((20, 184, 166), (255, 255, 255)),
               ((255, 255, 255), (11, 37, 69)), ((88, 101, 242), (255, 255, 255)), ((255, 140, 0), (255, 255, 255))]


class Beat(BaseModel):
    narration: str = Field(description="1-2 short spoken sentences, max 28 words. Plain words only.")
    label: str = Field(description="2-4 word on-screen keyword for this beat, e.g. 'Start at 45'")
    footage_query: str = Field(description="2-4 word stock-video search for a calm, non-graphic clip that shows exactly this beat (e.g. 'mammogram machine', 'woman talking to doctor'); never a generic machine or scan word that could find unrelated scans (ultrasound, x-ray, dental)")


class ShortScript(BaseModel):
    hook_text: str = Field(description="2-6 BIG words on screen in the first second: a surprising fact or "
                           "question, e.g. 'SCREENING STARTS AT 45'. Must be true. No fear-mongering, no clickbait.")
    hook_line: str = Field(description="The first spoken sentence, max 14 words, that makes people want the answer.")
    beats: list[Beat] = Field(description="4-6 beats that give ONE complete, useful answer, in order.")
    preview: list[str] = Field(description="3 short phrases (max 6 words) naming what the FULL video adds that "
                               "this Short does not cover, e.g. 'the 3 home test options'")
    title: str = Field(description="YouTube Shorts title, max 60 characters, a curiosity question or bold claim "
                       "with the topic keyword, no hashtags")
    loop_end: str = Field(default="", description="Loop Shorts only: the last spoken words (max 12) that flow "
                          "straight back into hook_line, so the restart sounds like one continuous sentence "
                          "(e.g. hook 'Most people take this pill wrong.' and loop_end 'And that is exactly why'). "
                          "Empty for other Shorts.")


def write_script(plan, series: str | None = None, part: str | None = None, avoid: str | None = None,
                 loop: bool = False) -> ShortScript:
    """Claude writes the Short from the (already fact-checked) full script, using only facts in it."""
    import anthropic

    from .planner import MODEL, _fallback_kwargs

    source = "\n".join(f"- {s.heading}: {s.narration}" for s in plan.scenes)
    second = (f"\n- This is the second Short about this video: use a DIFFERENT angle, hook and takeaway than this "
              f"one: {avoid}") if avoid else ""
    loop_rule = ("\n- INFINITE LOOP: this Short has no ending card. Write loop_end: the final words that lead straight "
                 "back into hook_line, so when the video restarts it sounds like one continuous thought and people "
                 "watch it again. The hook must work as the first 1.5 seconds AND as the continuation of loop_end."
                 ) if loop else ""
    # Loop Shorts are short: viewers who watch to the end (and again) are what makes YouTube show a Short
    length, words = (("35-45 second", "about 85-105 spoken words, 3-4 beats") if loop
                     else ("50-65 second", "about 120-150 spoken words"))
    prompt = f"""You write YouTube Shorts for Health Support Studio, a calm, trustworthy health-education
channel for US adults. Never call the host a doctor or nurse; never invent personal stories.

Write a {length} vertical Short ({words} in total, hook + beats) about:
{plan.topic}
{f'It is part {part} of our series "{series}".' if series else ''}

Use ONLY facts from this fact-checked script (do not add new numbers or claims):
{source}

Rules:
- The hook must stop the scroll in the first second: a surprising true fact, a common mistake, or a direct
  question the viewer wants answered. Specific to this topic. Not "Myth or fact?" and not generic.
- Then deliver ONE complete, useful answer in short beats, so the viewer learns something real.
- Short sentences, everyday words, American English. Write numbers out as they are spoken.
- The preview names 3 things the full video covers that this Short does not, so viewers want to watch it.
- Change the focus every sentence (about every 3 seconds): blistering pace, no filler, never "hey guys" or an intro.
- Do not mention YouTube, subscribing or the channel; that is added automatically.{second}{loop_rule}"""
    client = anthropic.Anthropic()
    response = client.beta.messages.parse(model=MODEL, max_tokens=4000, **_fallback_kwargs(),
                                          messages=[{"role": "user", "content": prompt}], output_format=ShortScript)
    return response.parsed_output


def _clean(text: str) -> str:
    """Plain spoken text: escaped characters decoded, dashes turned into commas (the voice reads them better)."""
    text = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), text)
    text = re.sub(r"(\d)\s*[\u2013\u2014-]\s*(\d)", r"\1 to \2", text)  # "15-20" -> "15 to 20"
    text = re.sub(r"\s*[\u2014\u2013]\s*", ", ", text)
    # brackets are not spoken: citations like "(USPSTF, 2024)" go, other asides become ", like cysts,"
    text = re.sub(r"\s*\([^()]*\b(?:19|20)\d\d\b[^()]*\)", "", text)
    text = re.sub(r"\s*\(([^()]*)\)\s*([.!?]?)", lambda m: f", {m.group(1)}{m.group(2) or ','} ", text)
    text = re.sub(r",\s*([,.!?])", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def clean_script(script: ShortScript) -> ShortScript:
    script.hook_text, script.hook_line, script.title = map(_clean, (script.hook_text, script.hook_line, script.title))
    script.preview = [_clean(p) for p in script.preview]
    script.loop_end = _clean(script.loop_end)
    for b in script.beats:
        b.narration, b.label = _clean(b.narration), _clean(b.label)
    return script


def check_facts(script: ShortScript, topic: str) -> ShortScript:
    """The same fact check as the long video (budget mode), on the hook and every beat."""
    from . import fact_check
    from .planner import Scene

    scenes = [Scene(narration=script.hook_line, layout="title", heading=script.hook_text, points=[],
                    footage_query="")]
    scenes += [Scene(narration=b.narration, layout="bullets", heading=b.label, points=[], footage_query=b.footage_query)
               for b in script.beats]
    review = fact_check.fact_check(topic, scenes, 0)
    if not review.approved:
        raise RuntimeError(f"Short not approved by the fact check: {review.issues}")
    fixed = review.apply_to(scenes)
    script.hook_line, script.hook_text = fixed[0].narration, fixed[0].heading
    for b, s in zip(script.beats, fixed[1:]):
        b.narration, b.label = s.narration, s.heading
    # The hook must stay a few seconds long: anything the check added to it (e.g. a 911 safety note) moves to
    # the end of the last beat, where it is still said.
    sentences = re.split(r"(?<=[.!?])\s+", script.hook_line.strip())
    keep = sentences[:1]
    for x in sentences[1:]:  # a short second sentence may stay; long safety notes move on
        if len(" ".join(keep + [x]).split()) <= 22 and not re.search(r"911|emergency|ER\b", x):
            keep.append(x)
        else:
            break
    extra = " ".join(sentences[len(keep):]).strip("() ")
    if extra:
        script.hook_line = " ".join(keep)
        script.beats[-1].narration = f"{script.beats[-1].narration.rstrip()} {extra}"
    return script


# ---------------------------------------------------------------- drawing
def _font(size: int, weight: int = 800):
    return visuals.font(size, weight)


def _wrap(d, text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = f"{cur} {w}".strip()
        if d.textlength(t, font=f) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur] if cur else lines


def hook_card(text: str, tag: str, colors, out: Path) -> Path:
    """Huge hook words on a bold color block in the upper part of the screen, a small series tag above it."""
    bg, fg = colors
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    size = 132
    while True:
        f = _font(size)
        lines = _wrap(d, text.upper(), f, W - 170)
        if len(lines) <= 3 or size <= 84:
            break
        size -= 8
    lh = int(size * 1.08)
    top = 860  # below the host's face, so the face stays visible in the first second
    box_h = lh * len(lines) + 70
    d.rounded_rectangle((50, top, W - 50, top + box_h), 40, fill=(*bg, 240))
    for i, line in enumerate(lines):
        d.text((W / 2, top + 35 + i * lh + lh / 2), line, font=f, fill=fg, anchor="mm")
    if tag:
        tf = _font(44, 700)
        tw = d.textlength(tag, font=tf)
        d.rounded_rectangle(((W - tw) / 2 - 28, top - 100, (W + tw) / 2 + 28, top - 30), 34, fill=(11, 37, 69, 225))
        d.text((W / 2, top - 65), tag, font=tf, fill=(255, 255, 255), anchor="mm")
    img.save(out)
    return out


def label_card(label: str, color, out: Path) -> Path:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = _font(68)
    text = label.upper()
    tw = min(d.textlength(text, font=f), W - 160)
    d.rounded_rectangle(((W - tw) / 2 - 40, 1300, (W + tw) / 2 + 40, 1410), 36, fill=(*color, 235))
    d.text((W / 2, 1355), text, font=f, fill=(11, 37, 69) if sum(color) > 600 else (255, 255, 255), anchor="mm")
    img.save(out)
    return out


def list_card(title: str, items: list[str], footer: str, color, out: Path) -> Path:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    tf, f, ff = _font(70), _font(58, 700), _font(52, 700)
    y = 380
    body = []
    for it in items:
        body.append(_wrap(d, it, f, W - 300))
    box_h = 150 + sum(len(b) * 72 + 40 for b in body) + 40
    d.rounded_rectangle((60, y, W - 60, y + box_h), 44, fill=(11, 37, 69, 230))
    d.text((W / 2, y + 85), title.upper(), font=tf, fill=color, anchor="mm")
    yy = y + 170
    for b in body:
        d.ellipse((110, yy + 12, 150, yy + 52), fill=color)
        d.line([(119, yy + 33), (127, yy + 42), (142, yy + 22)], fill=(11, 37, 69), width=6)
        for line in b:
            d.text((180, yy), line, font=f, fill=(255, 255, 255))
            yy += 72
        yy += 40
    if footer:
        fw = d.textlength(footer, font=ff)
        fy = y + box_h + 50
        d.rounded_rectangle(((W - fw) / 2 - 36, fy, (W + fw) / 2 + 36, fy + 100), 50, fill=(*color, 245))
        d.text((W / 2, fy + 50), footer, font=ff, fill=(11, 37, 69) if sum(color) > 600 else (255, 255, 255),
               anchor="mm")
    img.save(out)
    return out


# ---------------------------------------------------------------- captions
def word_captions(captions, out: Path, y: int = 1580) -> Path:
    """Big captions in the middle of the screen, 3 words at a time, each word lighting up yellow as it is said."""
    fs = 118
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{visuals.caption_font_name()},{fs},&H0000D4FF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for a, b, text in captions:
        words = text.split()
        chunks = [words[i:i + 3] for i in range(0, len(words), 3)]
        total = sum(len(w) + 1 for w in words) or 1
        t = a
        for ch in chunks:
            dur = (b - a) * sum(len(w) + 1 for w in ch) / total
            k = "".join(f"{{\\k{max(1, int(dur * 100 * (len(w) + 1) / sum(len(x) + 1 for x in ch)))}}}{w} "
                        for w in ch)
            lines.append(f"Dialogue: 0,{visuals._ass_time(t)},{visuals._ass_time(t + dur)},Cap,,0,0,0,,"
                         f"{{\\pos({W // 2},{y})}}{k.strip()}")
            t += dur
    out.write_text(header + "\n".join(lines) + "\n")
    return out


# ---------------------------------------------------------------- rendering
def _segment(bg: Path | None, cards: list[Path], wav: Path, ass: Path | None, duration: float, out: Path,
             zoom: bool = True, blur: bool = False, cut_at: float | None = None, bg2: Path | None = None,
             more: list | None = None) -> Path:
    """Background clips (slow push-in; a second clip from cut_at, or several clips in equal parts), card PNGs on
    top, captions, audio."""
    inputs, chain = [], []
    n = 0
    clips = [c for c in [bg, bg2, *(more or [])] if c]
    if not clips:
        grad = visuals.render_background((W, H), out.with_suffix(".bg.png"))
        clips = [grad]
    for c in clips:
        if c.suffix.lower() == ".png":
            inputs += ["-loop", "1", "-i", str(c)]
        else:
            inputs += ["-stream_loop", "-1", "-i", str(c)]
    bgs = []
    for i, _ in enumerate(clips):
        f = f"[{i}:v]fps={FPS},scale={int(W * 1.12)}:{int(H * 1.12)}:force_original_aspect_ratio=increase,"
        if zoom:  # push in slowly: the crop window shrinks toward the centre
            f += (f"crop=w='iw-{int(W * 0.12)}*min(t/{max(duration, 1):.2f},1)':"
                  f"h='ih-{int(H * 0.12)}*min(t/{max(duration, 1):.2f},1)',")
        f += f"scale={W}:{H},setsar=1"
        if blur:
            f += ",boxblur=22:2,eq=brightness=-0.12"
        else:
            f += ",eq=brightness=-0.06:saturation=1.05"
        bgs.append(f"{f}[b{i}]")
    chain += bgs
    if len(clips) == 2 and cut_at:
        chain.append(f"[b0]trim=0:{cut_at:.2f},setpts=PTS-STARTPTS[c0];"
                     f"[b1]trim=0:{duration - cut_at + 0.1:.2f},setpts=PTS-STARTPTS[c1];[c0][c1]concat=n=2:v=1:a=0[v0]")
    elif len(clips) > 1:  # a new shot every few seconds
        seg = duration / len(clips)
        chain += [f"[b{i}]trim=0:{seg + (0.1 if i == len(clips) - 1 else 0):.2f},setpts=PTS-STARTPTS[c{i}]"
                  for i in range(len(clips))]
        chain.append("".join(f"[c{i}]" for i in range(len(clips))) + f"concat=n={len(clips)}:v=1:a=0[v0]")
    else:
        chain.append("[b0]null[v0]")
    n = len(clips)
    last = "v0"
    for j, card in enumerate(cards):
        inputs += ["-loop", "1", "-i", str(card)]
        chain.append(f"[{n + j}:v]format=rgba[k{j}];[{last}][k{j}]overlay=0:0[v{j + 1}]")
        last = f"v{j + 1}"
    tail = f"[{last}]fade=t=in:st=0:d=0.15"
    if ass:
        fonts = f":fontsdir='{visuals._escape_filter_path(visuals.FONT_DIR)}'" if visuals.FONT_DIR.exists() else ""
        tail += f",subtitles='{visuals._escape_filter_path(ass)}'{fonts}"
    chain.append(tail + ",format=yuv420p[v]")
    audio_idx = n + len(cards)
    inputs += ["-i", str(wav)]
    visuals._run(["-y", *inputs, "-filter_complex", ";".join(chain), "-map", "[v]", "-map", f"{audio_idx}:a",
                  "-t", f"{duration:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", str(FPS),
                  "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", str(out)])
    return out


def _host_clip(day: int) -> Path | None:
    clips = sorted(p for p in HOST_CLIPS.glob("Man_*.mp4"))
    return clips[day % len(clips)] if clips else None


def build(script: ShortScript, voice_cfg: dict, workdir: Path, series: str | None = None, part: str | None = None,
          ending: str = "youtube", day: int | None = None) -> Path:
    """Render the Short. ending='youtube' points to the full video; 'follow' (Instagram/Facebook) asks to follow."""
    from . import voice

    visuals.ensure_fonts()
    workdir.mkdir(parents=True, exist_ok=True)
    day = dt.date.today().toordinal() if day is None else day
    colors = HOOK_COLORS[day % len(HOOK_COLORS)]
    accent = colors[0] if sum(colors[0]) < 700 else (20, 184, 166)
    used: set = set()
    parts = []
    tag = f"PART {part} • {series.upper()}" if series and part else ""

    # 1. the hook over the host's face
    wav = workdir / "00.wav"
    dur, caps = voice.narrate_scene(script.hook_line, voice_cfg, wav)
    parts.append(_segment(_host_clip(day), [hook_card(script.hook_text, tag, colors, workdir / "00.png")], wav,
                          word_captions(caps, workdir / "00.ass", y=1560), dur, workdir / "00.mp4"))
    # 2. the beats: a new picture every few seconds
    for i, b in enumerate(script.beats, 1):
        wav = workdir / f"{i:02d}.wav"
        dur, caps = voice.narrate_scene(b.narration, voice_cfg, wav)
        want = max(1, min(4, round(dur / 3)))  # a new shot about every 3 seconds
        shots = [visuals.fetch_footage(b.footage_query, (W, H), workdir / f"{i:02d}{chr(97 + j)}.mp4", used)
                 for j in range(want)]
        shots = [c for c in shots if c] or [_host_clip(day + i)]
        parts.append(_segment(shots[0], [label_card(b.label, accent, workdir / f"{i:02d}.png")], wav,
                              word_captions(caps, workdir / f"{i:02d}.ass"), dur, workdir / f"{i:02d}.mp4",
                              more=shots[1:]))
    k = len(script.beats) + 1
    if ending == "loop":  # 3. no ending card: the last words lead straight back into the hook (same shot)
        if script.loop_end:
            wav = workdir / f"{k:02d}.wav"
            dur, caps = voice.narrate_scene(script.loop_end, voice_cfg, wav)
            parts.append(_segment(_host_clip(day), [], wav, word_captions(caps, workdir / f"{k:02d}.ass", y=1560),
                                  dur, workdir / f"{k:02d}.mp4", zoom=False))
        joined = visuals.concat(parts, workdir / "joined.mp4")
        out = workdir / "short.mp4"
        visuals._run(["-y", "-i", str(joined), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r",
                      str(FPS), "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", str(out)])
        return out
    # 3. what the full video adds + where to find it
    preview = "In the full video: " + ", ".join(script.preview[:-1]) + f", and {script.preview[-1]}."
    if ending == "youtube":
        footer = "FULL VIDEO: LINK ABOVE THE TITLE"
        end = (f"It's part {part} of our {series} series. The full video is linked right above the title."
               if series and part else "The full video is linked right above the title.")
    else:
        footer = "FOLLOW FOR DAILY HEALTH TIPS"
        end = "Follow us for one simple health tip every day."
    wav = workdir / f"{k:02d}.wav"
    dur, caps = voice.narrate_scene(f"{preview} {end}", voice_cfg, wav)
    parts.append(_segment(_host_clip(day + 3), [list_card("In the full video", script.preview, footer, accent,
                                                          workdir / f"{k:02d}.png")],
                          wav, None, dur, workdir / f"{k:02d}.mp4", zoom=False, blur=True))
    # One re-encode of the joined parts, so the timestamps are clean (seeking and players behave)
    joined = visuals.concat(parts, workdir / "joined.mp4")
    out = workdir / "short.mp4"
    visuals._run(["-y", "-i", str(joined), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", str(FPS),
                  "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", str(out)])
    return out


def make_pair(plan, voice_cfg: dict, workdir: Path, series: str | None, part: str | None, day: int,
              avoid: str | None = None, loop: bool = False) -> tuple[ShortScript, Path, Path]:
    """Script (fact-checked) + the YouTube Short + the Instagram/Facebook version (same voice takes).
    loop=True: an infinite-loop Short (no ending card), the same file on every platform."""
    script = clean_script(check_facts(clean_script(write_script(plan, series, part, avoid, loop)), plan.topic))
    (workdir / "short_script.json").parent.mkdir(parents=True, exist_ok=True)
    (workdir / "short_script.json").write_text(script.model_dump_json(indent=2))
    if loop and script.loop_end:
        looped = build(script, voice_cfg, workdir / "yt", series, part, "loop", day)
        return script, looped, looped
    youtube = build(script, voice_cfg, workdir / "yt", series, part, "youtube", day)
    follow = build(script, voice_cfg, workdir / "ig", series, part, "follow", day)
    return script, youtube, follow


def sample(script_file: str, out_dir: str) -> None:
    """One new-style Short (and its Instagram/Facebook version) from a script-bank file, for review."""
    import yaml

    from . import growth, main, planner

    data = yaml.safe_load(Path(script_file).read_text())
    plan = planner.VideoPlan.model_validate(data["plan"])
    cfg = main.load_config()
    series = growth.series_for(plan.playlist, cfg.get("growth") or {})
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    print("Writing the Short...")
    script = clean_script(check_facts(clean_script(write_script(plan, series, "3/5")), plan.topic))
    (out / "short_script.json").write_text(script.model_dump_json(indent=2))
    print(json.dumps(script.model_dump(), indent=2))
    video = build(script, cfg.get("voice", {}), out / "build", series, "3/5")
    final = out / "short_sample.mp4"
    final.write_bytes(video.read_bytes())
    print(f"Saved {final}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["sample"]:
        sample(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
