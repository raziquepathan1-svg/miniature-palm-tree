"""Visual makeover videos: an empty or tired space is transformed step by step, with no narration.

Each video picks a space (empty living room, bare backyard, empty rooftop terrace...) and a style
(Japandi, Boho, Coastal...) that haven't been used together yet. An AI image model draws the "before"
photo, then edits that same picture stage by stage (paint, floor, furniture, plants, lights...).
The stages become a music video with zooms, pans, swipe transitions and BEFORE / STEP / AFTER labels:
a landscape YouTube video plus a vertical Short for YouTube Shorts, Instagram and Facebook Reels.

Images: Google Gemini (GEMINI_API_KEY, keeps the same room between edits) when the key is set,
otherwise the free Pollinations service (no key; each stage is drawn fresh with the same seed).

Usage (from the repo root; the workflow sets CHANNEL=restore_remake):
    CHANNEL=restore_remake python -m youtube_agent.makeover            # make and upload
    CHANNEL=restore_remake python -m youtube_agent.makeover --dry-run  # make, don't upload
"""

import argparse
import base64
import datetime as dt
import io
import json
import os
import random
import subprocess
import time
import urllib.parse
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter

from . import visuals
from .editor import ffmpeg_bin
from .main import (CHANNEL_DIR, OUTPUT_DIR, last_scheduled, load_config, load_history, match_playlist,
                   next_publish_time, save_history, slugify, write_summary)

FPS = 30
W, H = 1920, 1080          # landscape video
SW, SH = 1080, 1920        # vertical Short
GEMINI_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
KEEP = ("Keep the exact same space, camera position, angle, perspective, walls, windows, doors and ceiling. "
        "Only change what is described. Photorealistic, natural light, high detail, no people, no text, no watermark.")


# ---------------------------------------------------------------- choosing the makeover
def pick_makeover(cfg: dict, history: list[dict], rng: random.Random) -> dict:
    """Next space + style pair that hasn't been published yet, rotating through the space categories."""
    done = {h.get("makeover_key") for h in history}
    spaces, styles = cfg["spaces"], cfg["styles"]
    recent = [h.get("space") for h in history if h.get("space")][-len(spaces) + 1:] if len(spaces) > 1 else []
    order = sorted(spaces, key=lambda s: (s["name"] in recent, rng.random()))
    for space in order:
        for style in rng.sample(styles, len(styles)):
            if f"{space['name']}|{style['name']}" not in done:
                return {"space": space, "style": style}
    return {"space": rng.choice(spaces), "style": rng.choice(styles)}  # everything used: start over


def fill(text: str, space: dict, style: dict) -> str:
    return (text.replace("{style}", style["name"]).replace("{look}", style["look"])
            .replace("{palette}", style["palette"]).replace("{space}", space["short"])
            .replace("{Space}", space["short"].title()))


def build_stages(space: dict, style: dict) -> list[dict]:
    """[{label, prompt}] for each step after the before photo; prompts are cumulative edits."""
    return [{"label": fill(s["label"], space, style), "edit": fill(s["edit"], space, style)} for s in space["stages"]]


def metadata(space: dict, style: dict, stages: list[dict], cfg: dict, rng: random.Random) -> dict:
    sub = {"{Space}": space["short"].title(), "{space}": space["short"], "{Style}": style["name"],
           "{Before}": space["before_label"].title(), "{before}": space["before_label"]}

    def t(s: str) -> str:
        for k, v in sub.items():
            s = s.replace(k, v)
        return s

    title = next((x for x in (t(x) for x in rng.sample(cfg["titles"], len(cfg["titles"]))) if len(x) <= 95),
                 f"{space['short'].title()} Makeover: {style['name']}")
    steps = "\n".join(f"{i}. {s['label']}" for i, s in enumerate(stages, 1))
    tags = list(dict.fromkeys([f"{space['short']} makeover", f"{style['name'].lower()} {space['short']}",
                               f"{style['name'].lower()} style", *space.get("tags", []), *cfg.get("tags", [])]))[:15]
    hashtags = " ".join(cfg.get("hashtags", [])[:4] + ["#" + style["name"].replace(" ", "").replace("-", "")])
    description = (f"{t(rng.choice(cfg['hooks']))}\n\nThe makeover, step by step:\n{steps}\n\n"
                   f"Style: {style['name']} ({style['look']}).\n\n"
                   "Which space should we transform next? Tell us in the comments!\n\n" + hashtags)
    caption = f"{t(rng.choice(cfg['hooks']))} Which step is your favorite? {hashtags} #roomtransformation"
    return {"title": title, "description": description, "tags": tags, "caption": caption,
            "short_title": (t(rng.choice(cfg["short_titles"]))[:50] + " #Shorts"),
            "thumb_from": space["before_label"].upper(), "thumb_to": style["name"].upper(),
            "playlist": space["playlist"]}


# ---------------------------------------------------------------- AI images
def _gemini(prompt: str, image: Image.Image | None) -> Image.Image:
    key = os.environ["GEMINI_API_KEY"].strip()
    parts: list[dict] = [{"text": prompt}]
    if image is not None:
        buf = io.BytesIO()
        image.convert("RGB").save(buf, "JPEG", quality=92)
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}})
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}}}
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
                      headers={"x-goog-api-key": key}, json=body, timeout=180)
    if r.status_code >= 400:
        raise RuntimeError(f"Gemini {r.status_code}: {r.text[:300]}")
    for cand in r.json().get("candidates", []):
        for part in (cand.get("content") or {}).get("parts", []):
            data = (part.get("inlineData") or part.get("inline_data") or {}).get("data")
            if data:
                return Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB")
    raise RuntimeError(f"Gemini returned no image: {r.text[:300]}")


def _pollinations(prompt: str, seed: int) -> Image.Image:
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt[:1500])
           + f"?width=1344&height=768&seed={seed}&nologo=true&model=flux")
    last = None
    for attempt in range(4):
        try:
            r = requests.get(url, timeout=240)
            if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
                return Image.open(io.BytesIO(r.content)).convert("RGB")
            last = f"HTTP {r.status_code}: {r.text[:200]}"
        except requests.RequestException as e:
            last = str(e)
        time.sleep(15 * (attempt + 1))
    raise RuntimeError(f"Pollinations failed: {last}")


def make_images(space: dict, style: dict, stages: list[dict], seed: int, out: Path) -> tuple[list[Path], str]:
    """Before photo + one image per stage. Returns (paths, source used)."""
    before_prompt = f"Wide-angle real estate photo of {space['before']}. Photorealistic, natural daylight, " \
                    "no people, no text, no watermark."
    if os.environ.get("GEMINI_API_KEY", "").strip():
        try:
            imgs = [_gemini(before_prompt, None)]
            for st in stages:
                print(f"    Gemini: {st['label']}")
                imgs.append(_gemini(f"Edit this photo: {st['edit']} {KEEP}", imgs[-1]))
            return _save(imgs, out), "Gemini"
        except Exception as e:  # quota, outage...: redo the whole set with the free service
            print(f"  (Gemini failed, using Pollinations instead: {e})")
    imgs = [_pollinations(before_prompt, seed)]
    done = []
    for st in stages:
        print(f"    Pollinations: {st['label']}")
        done.append(st["edit"])
        imgs.append(_pollinations(f"Wide-angle real estate photo of {fill(space['after_base'], space, style)}, same layout and camera "
                                  f"angle. Completed so far: {' '.join(done)} Photorealistic, natural daylight, "
                                  "no people, no text, no watermark.", seed))
    return _save(imgs, out), "Pollinations"


def _save(imgs: list[Image.Image], out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, img in enumerate(imgs):
        p = out / f"{i:02d}.jpg"
        visuals._cover(img, W, H).save(p, "JPEG", quality=94)
        paths.append(p)
    return paths


# ---------------------------------------------------------------- overlays
def _label(text: str, size: tuple[int, int], color, out: Path, step: str | None = None) -> Path:
    """Big label pill near the top (plus small 'STEP 2/5' tag above it)."""
    w, h = size
    portrait = h > w
    u = (w / 1080) if portrait else (w / 1920)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = visuals.font(int(64 * u), 800)
    tw = d.textlength(text, font=f)
    pad = int(36 * u)
    x0 = (w - tw) / 2 - pad
    y0 = int((260 if portrait else 70) * u)
    if step:
        sf = visuals.font(int(34 * u), 800)
        sw = d.textlength(step, font=sf)
        d.rounded_rectangle(((w - sw) / 2 - 20 * u, y0 - 62 * u, (w + sw) / 2 + 20 * u, y0 - 12 * u), int(25 * u),
                            fill=(255, 255, 255, 235))
        d.text(((w - sw) / 2, y0 - 58 * u), step, font=sf, fill=(28, 25, 23))
    d.rounded_rectangle((x0, y0, x0 + tw + 2 * pad, y0 + int(100 * u)), int(50 * u), fill=(*color, 240))
    d.text((x0 + pad, y0 + int(12 * u)), text, font=f, fill=(255, 255, 255))
    # channel tag bottom
    tag = "RESTORE REMAKE STUDIO"
    tf = visuals.font(int(30 * u), 800)
    tgw = d.textlength(tag, font=tf)
    ty = h - int((330 if portrait else 90) * u)
    d.rounded_rectangle(((w - tgw) / 2 - 70 * u, ty - 10 * u, (w + tgw) / 2 + 24 * u, ty + 50 * u), int(30 * u),
                        fill=(28, 25, 23, 200))
    visuals._house_icon(d, int((w - tgw) / 2 - 36 * u), int(ty + 20 * u), int(40 * u))
    d.text(((w - tgw) / 2, ty), tag, font=tf, fill=(255, 255, 255))
    img.save(out)
    return out


def _endcard(size: tuple[int, int], out: Path) -> Path:
    w, h = size
    portrait = h > w
    u = (w / 1080) if portrait else (w / 1920)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = visuals.font(int(58 * u), 800)
    lines = ["Which style should", "we try next? 👇"] if portrait else ["Which style should we try next?"]
    lines = [l.replace(" 👇", "") for l in lines]
    y = h - int((640 if portrait else 330) * u)
    box_h = int(len(lines) * 78 * u + 150 * u)
    d.rounded_rectangle((int(60 * u), y - int(30 * u), w - int(60 * u), y + box_h), int(40 * u), fill=(28, 25, 23, 215))
    for line in lines:
        lw = d.textlength(line, font=f)
        d.text(((w - lw) / 2, y), line, font=f, fill=(255, 255, 255))
        y += int(78 * u)
    sub = "FOLLOW FOR A NEW MAKEOVER DAILY"
    sf = visuals.font(int(36 * u), 800)
    sw = d.textlength(sub, font=sf)
    d.rounded_rectangle(((w - sw) / 2 - 30 * u, y + 10 * u, (w + sw) / 2 + 30 * u, y + 80 * u), int(35 * u),
                        fill=(245, 158, 11))
    d.text(((w - sw) / 2, y + 20 * u), sub, font=sf, fill=(28, 25, 23))
    img.save(out)
    return out


# ---------------------------------------------------------------- video
def _run(args: list[str]) -> None:
    r = subprocess.run([ffmpeg_bin(), "-hide_banner", "-loglevel", "error", *args], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"ffmpeg failed: {r.stderr[-1500:]}")


def _still_clip(img: Path, overlay: Path, dur: float, size: tuple[int, int], motion: str, out: Path,
                extra: Path | None = None) -> Path:
    """One image with slow motion (zoom in landscape, side-to-side pan in vertical) and its label."""
    w, h = size
    frames = int(dur * FPS)
    if h > w:  # vertical: the 16:9 photo is panned across so the whole room is seen
        sx = int(h * 16 / 9)
        span = sx - w
        x = f"{span}*n/{frames}" if motion == "right" else f"{span}*(1-n/{frames})"
        vf = f"[0:v]scale={sx}:{h},crop={w}:{h}:x='{x}':y=0,setsar=1[bg]"
    else:
        zoom = "min(1+0.0009*on,1.12)" if motion != "out" else "max(1.12-0.0009*on,1)"
        vf = (f"[0:v]scale={w * 2}:{h * 2},zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
              f":d={frames}:s={w}x{h}:fps={FPS},setsar=1[bg]")
    inputs = ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur}", "-i", str(img), "-i", str(overlay)]
    vf += ";[bg][1:v]overlay=0:0:format=auto[v1]"
    last = "v1"
    if extra:
        inputs += ["-i", str(extra)]
        vf += f";[v1][2:v]overlay=0:0:format=auto:enable='gte(t,{max(0.0, dur - 3.2):.2f})'[v2]"
        last = "v2"
    _run(["-y", *inputs, "-filter_complex", vf + f";[{last}]format=yuv420p[v]", "-map", "[v]", "-t", f"{dur}",
          "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(out)])
    return out


def _reveal_clip(before: Path, after: Path, size: tuple[int, int], out_dir: Path) -> Path:
    """Final BEFORE -> AFTER wipe on the full images."""
    w, h = size
    tag = "v" if h > w else "h"
    a = _still_clip(before, _label("BEFORE", size, (87, 83, 78), out_dir / f"rb_{tag}.png"), 2.2, size, "out",
                    out_dir / f"r1_{tag}.mp4")
    b = _still_clip(after, _label("AFTER", size, (13, 148, 136), out_dir / f"ra_{tag}.png"), 4.0, size, "in",
                    out_dir / f"r2_{tag}.mp4", extra=_endcard(size, out_dir / f"end_{tag}.png"))
    out = out_dir / f"reveal_{tag}.mp4"
    _run(["-y", "-i", str(a), "-i", str(b), "-filter_complex",
          "[0:v][1:v]xfade=transition=wiperight:duration=1.4:offset=0.8,format=yuv420p[v]", "-map", "[v]",
          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(out)])
    return out


TRANSITIONS = ["wipeleft", "slideleft", "smoothleft", "circleopen", "fadewhite", "radial", "wiperight", "diagtl"]


def _music(dur: float, out: Path, rng: random.Random) -> Path:
    """A random track from assets/music/ (or assets/music.mp3); otherwise a soft generated ambient pad."""
    tracks = sorted((CHANNEL_DIR / "assets" / "music").glob("*.mp3")) + sorted(CHANNEL_DIR.glob("assets/music.mp3"))
    fade = f"afade=t=in:d=1,afade=t=out:st={max(0.0, dur - 2.5):.2f}:d=2.5"
    if tracks:
        track = rng.choice(tracks)
        _run(["-y", "-stream_loop", "-1", "-i", str(track), "-t", f"{dur:.2f}", "-af", f"volume=0.8,{fade}",
              "-ar", "48000", "-ac", "2", str(out)])
        return out
    root = rng.choice([220.0, 246.94, 261.63, 196.0])
    chords = [(1, 1.26, 1.5), (0.89, 1.12, 1.33), (0.75, 0.94, 1.12), (0.84, 1.0, 1.26)]
    seg = 4.0
    expr = []
    for i, ch in enumerate(chords):
        notes = "+".join(f"sin(2*PI*{root * r:.2f}*t)" for r in ch)
        expr.append(f"between(mod(t,{seg * len(chords)}),{i * seg},{(i + 1) * seg})*({notes})")
    pad = f"0.05*({'+'.join(expr)})*(0.75+0.25*sin(2*PI*0.25*t))"
    _run(["-y", "-f", "lavfi", "-i", f"aevalsrc='{pad}':s=48000:d={dur:.2f}", "-af",
          f"lowpass=f=1800,aecho=0.8:0.7:120:0.25,{fade}", "-ac", "2", str(out)])
    return out


def build_video(images: list[Path], stages: list[dict], size: tuple[int, int], hold: float, out_dir: Path,
                out: Path, rng: random.Random) -> Path:
    """Stills with labels joined by swipe transitions, then the BEFORE -> AFTER reveal, with music."""
    w, h = size
    tag = "v" if h > w else "h"
    td = 0.8
    labels = [("BEFORE", (87, 83, 78), None)] + [
        (s["label"].upper(), (13, 148, 136) if i < len(stages) else (245, 158, 11), f"STEP {i}/{len(stages)}")
        for i, s in enumerate(stages, 1)]
    clips = []
    for i, (img, (text, color, step)) in enumerate(zip(images, labels)):
        ov = _label(text, size, color, out_dir / f"l{i:02d}_{tag}.png", step)
        motion = ("right" if i % 2 == 0 else "left") if h > w else ("in" if i % 2 == 0 else "out")
        clips.append(_still_clip(img, ov, hold + td, size, motion, out_dir / f"c{i:02d}_{tag}.mp4"))
    clips.append(_reveal_clip(images[0], images[-1], size, out_dir))

    inputs, chain, offset, prev = [], [], 0.0, "0:v"
    durs = [hold + td] * (len(clips) - 1) + [_duration(clips[-1])]
    for c in clips:
        inputs += ["-i", str(c)]
    for i in range(1, len(clips)):
        offset += durs[i - 1] - td
        tr = rng.choice(TRANSITIONS)
        chain.append(f"[{prev}][{i}:v]xfade=transition={tr}:duration={td}:offset={offset:.2f}[x{i}]")
        prev = f"x{i}"
    total = offset + durs[-1]
    silent = out_dir / f"silent_{tag}.mp4"
    _run(["-y", *inputs, "-filter_complex", ";".join(chain) + f";[{prev}]format=yuv420p[v]", "-map", "[v]",
          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", str(FPS), str(silent)])
    music = _music(total, out_dir / f"music_{tag}.m4a", rng)
    _run(["-y", "-i", str(silent), "-i", str(music), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
          "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)])
    return out


def _duration(path: Path) -> float:
    r = subprocess.run([ffmpeg_bin().replace("ffmpeg", "ffprobe"), "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 6.0


# ---------------------------------------------------------------- thumbnail
def make_thumbnail(before: Path, after: Path, top: str, bottom: str, out: Path) -> Path:
    """1280x720: before on the left, after on the right, diagonal gold split, big labels."""
    TW, TH = 1280, 720
    b = visuals._cover(Image.open(before).convert("RGB"), TW, TH)
    a = visuals._cover(Image.open(after).convert("RGB"), TW, TH)
    from PIL import ImageEnhance
    a = ImageEnhance.Contrast(ImageEnhance.Color(a).enhance(1.25)).enhance(1.08)
    b = ImageEnhance.Color(b).enhance(0.7)
    mask = Image.new("L", (TW, TH), 0)
    ImageDraw.Draw(mask).polygon([(TW * 0.56, 0), (TW, 0), (TW, TH), (TW * 0.44, TH)], fill=255)
    img = Image.composite(a, b, mask).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.line([(TW * 0.56, 0), (TW * 0.44, TH)], fill=(253, 230, 138), width=12)
    for text, x, color in (("BEFORE", 40, (87, 83, 78)), ("AFTER", TW - 300, (13, 148, 136))):
        f = visuals.font(54, 800)
        tw = d.textlength(text, font=f)
        d.rounded_rectangle((x, 36, x + tw + 50, 116), 40, fill=(*color, 245))
        d.text((x + 25, 44), text, font=f, fill=(255, 255, 255))
    # big headline at the bottom: "EMPTY ROOM -> JAPANDI"
    shade = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(TH - 260, TH):
        sd.line([(0, y), (TW, y)], fill=(0, 0, 0, int(200 * (y - (TH - 260)) / 260)))
    img.alpha_composite(shade)
    d = ImageDraw.Draw(img)
    size = 104
    while size > 50:
        f = visuals.font(size, 800)
        arrow_w = size * 0.9
        total = d.textlength(top, font=f) + d.textlength(bottom, font=f) + arrow_w + size * 0.5
        if total <= TW - 80:
            break
        size -= 6
    x = (TW - total) / 2
    y = TH - size - 50
    stroke = max(5, size // 16)
    d.text((x, y), top, font=f, fill=(255, 255, 255), stroke_width=stroke, stroke_fill=(0, 0, 0))
    x += d.textlength(top, font=f) + size * 0.25
    cy = y + size * 0.62  # the font has no arrow glyph, so draw one
    pts = [(x, cy - size * 0.13), (x + arrow_w * 0.55, cy - size * 0.13), (x + arrow_w * 0.55, cy - size * 0.3),
           (x + arrow_w, cy), (x + arrow_w * 0.55, cy + size * 0.3), (x + arrow_w * 0.55, cy + size * 0.13),
           (x, cy + size * 0.13)]
    d.polygon(pts, fill=(253, 230, 138), outline=(0, 0, 0), width=stroke // 2)
    x += arrow_w + size * 0.25
    d.text((x, y), bottom, font=f, fill=(253, 230, 138), stroke_width=stroke, stroke_fill=(0, 0, 0))
    img.convert("RGB").save(out, "JPEG", quality=92)
    return out


# ---------------------------------------------------------------- one video, end to end
def make_one(config: dict, history: list[dict], dry_run: bool) -> None:
    cfg = config["makeover"]
    seed = int(time.time()) % 1_000_000
    rng = random.Random(seed)
    pick = pick_makeover(cfg, history, rng)
    space, style = pick["space"], pick["style"]
    stages = build_stages(space, style)
    meta = metadata(space, style, stages, cfg, rng)
    print(f"1/5 Makeover: {space['name']} -> {style['name']}\n    Title: {meta['title']}")

    workdir = OUTPUT_DIR / f"{dt.datetime.now():%Y%m%d-%H%M}-{slugify(meta['title'])}"
    work = workdir / "build"
    work.mkdir(parents=True, exist_ok=True)
    visuals.set_brand(config.get("brand"))
    visuals.ensure_fonts()

    print("2/5 Drawing the before photo and each makeover step with AI...")
    images, source = make_images(space, style, stages, seed, workdir / "images")

    print("3/5 Building the landscape video and the vertical Short...")
    final = build_video(images, stages, (W, H), cfg.get("hold_seconds", 4.5), work, workdir / "final.mp4", rng)
    social_dir = workdir / "social"
    social_dir.mkdir(exist_ok=True)
    short = build_video(images, stages, (SW, SH), cfg.get("short_hold_seconds", 3.2), work,
                        social_dir / "short.mp4", rng)
    thumb = make_thumbnail(images[0], images[-1], meta["thumb_from"], meta["thumb_to"], workdir / "thumbnail.jpg")
    (workdir / "meta.json").write_text(json.dumps({**meta, "space": space["name"], "style": style["name"],
                                                   "image_source": source, "seed": seed}, indent=2))

    footer = (config["youtube"].get("description_footer") or "").strip()
    description = meta["description"] + ("\n\n" + footer if footer else "")
    entry = {"date": dt.datetime.now().isoformat(timespec="seconds"), "topic": f"{space['name']} - {style['name']}",
             "title": meta["title"], "style": "Visual Makeover", "space": space["name"],
             "makeover_key": f"{space['name']}|{style['name']}", "image_source": source}
    if dry_run:
        print(f"5/5 Dry run - not uploading. Files in {workdir}")
        return

    from . import uploader

    yt = dict(config["youtube"])
    publish_at = None
    if yt.get("auto_publish_time"):
        publish_at = next_publish_time(yt["auto_publish_time"], yt.get("auto_publish_timezone", "America/New_York"),
                                       after=last_scheduled(history))
        yt["privacy"] = "private"
        yt["publish_at"] = publish_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    elif yt.get("review_before_publish", True):
        yt["privacy"] = "private"
    lang = config["channel"].get("language_code", "en-US")
    print(f"4/5 Uploading to YouTube ({'scheduled ' + yt['publish_at'] if publish_at else yt.get('privacy')})...")
    video_id = uploader.upload_video(final, thumb, meta["title"], description, meta["tags"], yt, lang)
    entry["youtube_id"] = video_id
    if yt.get("publish_at"):
        entry["publish_at"] = yt["publish_at"]
    history.append(entry)
    save_history(history)

    about = yt.get("playlist_description")
    playlist = match_playlist(meta["playlist"], config["channel"].get("playlists") or [],
                              yt.get("default_playlist", "Makeovers"))
    if yt.get("playlists", True):
        uploader.add_to_playlists(video_id, [playlist], about)

    short_id = None
    if yt.get("upload_short", True):
        short_yt = dict(yt)
        if yt.get("publish_at"):
            short_yt["publish_at"] = (dt.datetime.fromisoformat(yt["publish_at"].replace("Z", "+00:00"))
                                      + dt.timedelta(hours=float(yt.get("short_delay_hours", 6)))
                                      ).strftime("%Y-%m-%dT%H:%M:%SZ")
        print("5/5 Uploading the Short to YouTube Shorts...")
        try:
            short_id = uploader.upload_video(short, None, meta["short_title"],
                                             f"{meta['caption']}\n\n▶️ Full makeover: https://youtu.be/{video_id}\n\n{footer}",
                                             meta["tags"] + ["shorts"], short_yt, lang)
            entry["short_youtube_id"] = short_id
            save_history(history)
            if yt.get("playlists", True):
                uploader.add_to_playlists(short_id, [yt.get("shorts_playlist", "Makeover Shorts")], about)
        except Exception as e:
            print(f"  (Could not upload the YouTube Short: {e})")
    (social_dir / "social.json").write_text(json.dumps({
        "youtube_id": video_id, "title": meta["title"], "caption": meta["caption"],
        "publish_at": yt.get("publish_at")}, indent=2))

    summary = [f"## {meta['title']}",
               f"- Makeover: {space['name']} → {style['name']} (images: {source})",
               f"- Review: https://studio.youtube.com/video/{video_id}/edit"]
    if short_id:
        summary.append(f"- YouTube Short: https://studio.youtube.com/video/{short_id}/edit")
    if publish_at:
        summary.append(f"- **Scheduled** to go public at {yt['publish_at']} (UTC). To stop it, set it to Private.")
    print("\n".join(summary))
    write_summary(summary)


def main() -> None:
    parser = argparse.ArgumentParser(description="Visual makeover videos")
    parser.add_argument("--dry-run", action="store_true", help="Make the video but don't upload it")
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()
    config, history = load_config(), load_history()
    for i in range(args.count):
        print(f"\n=== Makeover {i + 1} of {args.count} ===")
        make_one(config, history, args.dry_run)


if __name__ == "__main__":
    main()
