"""Builds a narrated explainer video: branded slides + optional stock footage + burned-in captions.

No avatar needed. Each scene = background (Pexels stock clip, or an animated brand gradient)
+ a graphic overlay drawn from the scene's layout/heading/points + the narration + captions.
"""

import os
import re
import subprocess
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .editor import ffmpeg_bin

FPS = 30
FONT_DIR = Path(os.environ.get("FONT_DIR", Path.home() / ".cache" / "yt-agent-fonts"))

# Brand colors (match the channel banner and logo)
NAVY = (11, 37, 69)
TEAL = (20, 184, 166)
MINT = (207, 245, 239)
CORAL = (255, 107, 107)
YELLOW = (255, 212, 0)
WHITE = (255, 255, 255)
RED = (229, 57, 53)
BG_GRADIENT = ((11, 37, 69), (14, 124, 123))  # fallback background when there's no stock clip
ICON = "cross"  # brand icon on slides and thumbnails: "cross" (health) or "house" (home makeovers)
WARNING_NOTE = "In an emergency, call 911."
OUTRO_NOTE = "Educational only. Not medical advice."


def set_brand(brand: dict | None) -> None:
    """Apply a channel's colors, icon and on-screen notes (config.yaml "brand"); no-op if not set."""
    global NAVY, TEAL, MINT, CORAL, BG_GRADIENT, ICON, WARNING_NOTE, OUTRO_NOTE
    if not brand:
        return
    rgb = lambda key, default: tuple(brand[key]) if brand.get(key) else default
    NAVY, TEAL = rgb("panel", NAVY), rgb("accent", TEAL)
    MINT, CORAL = rgb("light", MINT), rgb("highlight", CORAL)
    if brand.get("background"):
        BG_GRADIENT = tuple(tuple(c) for c in brand["background"])
    ICON = brand.get("icon", ICON)
    WARNING_NOTE = brand.get("warning_note", WARNING_NOTE)
    OUTRO_NOTE = brand.get("outro_note", OUTRO_NOTE)
    for style, (label, color) in (brand.get("badges") or {}).items():
        BADGES[style] = (label, tuple(color))


# ---------------------------------------------------------------- fonts
def ensure_fonts() -> None:
    """Download Poppins (Open Font License) from Google Fonts once; fall back to DejaVu if offline."""
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    for weight in (500, 700, 800):
        dest = FONT_DIR / f"Poppins-{weight}.ttf"
        if dest.exists():
            continue
        try:
            css = requests.get(
                f"https://fonts.googleapis.com/css2?family=Poppins:wght@{weight}",
                headers={"User-Agent": "Mozilla/4.0"}, timeout=30,
            ).text
            url = re.search(r"url\((https://[^)]+\.ttf)\)", css).group(1)
            dest.write_bytes(requests.get(url, timeout=60).content)
        except Exception as e:  # offline: Pillow/libass fall back to system fonts
            print(f"  (Could not download Poppins font: {e})")
            return


def font(size: int, weight: int = 700) -> ImageFont.FreeTypeFont:
    for path in (
        FONT_DIR / f"Poppins-{weight}.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def caption_font_name() -> str:
    return "Poppins" if (FONT_DIR / "Poppins-700.ttf").exists() else "DejaVu Sans"


# ---------------------------------------------------------------- drawing helpers
def _wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_w: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def _text_block(draw, xy, text, fnt, fill, max_w, line_gap=1.15, anchor_center=False) -> int:
    """Draw wrapped text; returns the y below the block."""
    x, y = xy
    size = fnt.size
    for line in _wrap(draw, text, fnt, max_w):
        if anchor_center:
            w = draw.textlength(line, font=fnt)
            draw.text((x + (max_w - w) / 2, y), line, font=fnt, fill=fill)
        else:
            draw.text((x, y), line, font=fnt, fill=fill)
        y += int(size * line_gap)
    return y


def _brand_icon(draw, cx, cy, s):
    (_house_icon if ICON == "house" else _cross_icon)(draw, cx, cy, s)


def _house_icon(draw, cx, cy, s, fill=WHITE):
    """Simple house with a leaf: the Restore Remake Studio mark."""
    k = s / 100
    x0, y0 = cx - s / 2, cy - s / 2
    P = lambda pts: [(x0 + x * k, y0 + y * k) for x, y in pts]
    draw.polygon(P([(50, 4), (98, 46), (86, 46), (86, 96), (14, 96), (14, 46), (2, 46)]), fill=fill)
    draw.rectangle(P([(66, 10), (78, 30)]), fill=fill)
    draw.rounded_rectangle(P([(41, 64), (59, 96)]), max(1, int(4 * k)), fill=CORAL)
    draw.rectangle(P([(22, 52), (36, 64)]), fill=TEAL)
    draw.rectangle(P([(64, 52), (78, 64)]), fill=TEAL)


def _cross_icon(draw, cx, cy, s, fill=WHITE, pulse=None):
    pulse = pulse or CORAL
    arm = s * 0.3
    r = s * 0.09
    draw.rounded_rectangle((cx - arm / 2, cy - s / 2, cx + arm / 2, cy + s / 2), r, fill=fill)
    draw.rounded_rectangle((cx - s / 2, cy - arm / 2, cx + s / 2, cy + arm / 2), r, fill=fill)
    k = s / 200
    pts = [(8, 100), (78, 100), (90, 62), (104, 140), (118, 82), (128, 100), (192, 100)]
    draw.line([(cx - s / 2 + px * k, cy - s / 2 + py * k) for px, py in pts], fill=pulse,
              width=max(3, int(12 * k)), joint="curve")


def _check_icon(draw, x, y, s, color=WHITE):
    w = max(3, int(s * 0.16))
    draw.line([(x, y + s * 0.55), (x + s * 0.38, y + s * 0.9), (x + s, y + s * 0.15)], fill=color, width=w, joint="curve")


def _x_icon(draw, x, y, s, color=WHITE):
    w = max(3, int(s * 0.16))
    draw.line([(x + s * 0.1, y + s * 0.1), (x + s * 0.9, y + s * 0.9)], fill=color, width=w)
    draw.line([(x + s * 0.9, y + s * 0.1), (x + s * 0.1, y + s * 0.9)], fill=color, width=w)


def _lines_h(draw, text, fnt, max_w, gap=1.15) -> int:
    return len(_wrap(draw, text, fnt, max_w)) * int(fnt.size * gap)


def _panel(size, box, color=None, alpha=215, radius=36):
    color = color or NAVY
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(box, radius, fill=(*color, alpha))
    return layer


# ---------------------------------------------------------------- slide overlay
def render_overlay(scene, size: tuple[int, int], channel_name: str, out_png: Path) -> Path:
    """Draw the scene's graphic on a transparent canvas (captions go in the bottom ~22%)."""
    W, H = size
    portrait = H > W
    u = W / 1920 if not portrait else W / 1080  # scale unit
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Brand tag (top-left)
    tag_h = int(64 * u)
    _brand_icon(d, int(60 * u), int(60 * u), tag_h)
    d.text((int(105 * u), int(38 * u)), channel_name.upper(), font=font(int(34 * u), 700), fill=WHITE)

    margin = int(110 * u)
    content_top = int((300 if portrait else 170) * u)
    content_bottom = int(H * (0.72 if portrait else 0.76))
    max_w = W - 2 * margin
    layout = scene.layout
    heading, points = scene.heading, [p for p in scene.points if p.strip()]

    def card(top, bottom, color=NAVY, alpha=215):
        img.alpha_composite(_panel(size, (margin - int(40 * u), top, W - margin + int(40 * u), bottom), color, alpha))

    if layout == "title":
        f = font(int((110 if not portrait else 104) * u), 800)
        lines = _wrap(d, heading, f, max_w)
        block_h = len(lines) * int(f.size * 1.12) + (int(110 * u) if points else int(40 * u))
        y = (content_top + content_bottom - block_h) // 2
        card(y - int(60 * u), y + block_h + int(50 * u), alpha=170)
        y = _text_block(d, (margin, y), heading, f, WHITE, max_w, 1.12, anchor_center=True)
        d.rounded_rectangle((W / 2 - 90 * u, y + 22 * u, W / 2 + 90 * u, y + 34 * u), 6, fill=CORAL)
        if points:
            _text_block(d, (margin, y + int(55 * u)), points[0], font(int(46 * u), 500), MINT, max_w, anchor_center=True)

    elif layout == "big_number":
        size_px = int(230 * u)
        f = font(size_px, 800)
        # Long words ("Hundreds") must fit the width, especially on vertical Shorts.
        while size_px > int(90 * u) and (max(d.textlength(w, font=f) for w in heading.split() or [""]) > max_w
                                          or len(_wrap(d, heading, f, max_w)) > 2):
            size_px -= int(10 * u) or 1
            f = font(size_px, 800)
        pf = font(int(54 * u), 700)
        block_h = _lines_h(d, heading, f, max_w, 1.1) + sum(_lines_h(d, p, pf, max_w) + int(10 * u) for p in points[:3])
        y = max(content_top, (content_top + content_bottom - block_h) // 2)
        card(y - int(50 * u), y + block_h + int(50 * u), alpha=185)
        y = _text_block(d, (margin, y - int(30 * u)), heading, f, YELLOW, max_w, 1.1, anchor_center=True) + int(25 * u)
        for p in points[:3]:
            y = _text_block(d, (margin, y + int(10 * u)), p, pf, WHITE, max_w, anchor_center=True)

    elif layout == "myth_fact":
        myth = points[0] if points else heading
        fact = points[1] if len(points) > 1 else ""
        if portrait:
            boxes = [(margin - 40 * u, content_top, W - margin + 40 * u, (content_top + content_bottom) / 2 - 20 * u),
                     (margin - 40 * u, (content_top + content_bottom) / 2 + 20 * u, W - margin + 40 * u, content_bottom)]
        else:
            mid = W / 2
            boxes = [(margin - 40 * u, content_top, mid - 25 * u, content_bottom),
                     (mid + 25 * u, content_top, W - margin + 40 * u, content_bottom)]
        for (x0, y0, x1, y1), label, color, text in ((boxes[0], "MYTH", CORAL, myth), (boxes[1], "FACT", TEAL, fact)):
            img.alpha_composite(_panel(size, (int(x0), int(y0), int(x1), int(y1)), NAVY, 220))
            d.rounded_rectangle((x0, y0, x1, y0 + 95 * u), int(36 * u), fill=color)
            d.rectangle((x0, y0 + 60 * u, x1, y0 + 95 * u), fill=color)
            (_x_icon if label == "MYTH" else _check_icon)(d, x0 + 45 * u, y0 + 25 * u, 46 * u)
            d.text((x0 + 115 * u, y0 + 14 * u), label, font=font(int(56 * u), 800), fill=WHITE)
            _text_block(d, (int(x0 + 45 * u), int(y0 + 135 * u)), text, font(int(52 * u), 700), WHITE,
                        int(x1 - x0 - 90 * u))

    else:  # bullets / warning / outro
        accent = RED if layout == "warning" else TEAL
        hf = font(int(76 * u), 800)
        pf = font(int(52 * u), 700)
        head_w = max_w - (int(110 * u) if layout == "warning" else 0)
        block_h = (_lines_h(d, heading, hf, head_w) + int(20 * u)
                   + sum(_lines_h(d, p, pf, max_w - int(70 * u)) + int(16 * u) for p in points[:4])
                   + (int(110 * u) if layout == "warning" else 0) + (int((230 if portrait else 150) * u) if layout == "outro" else 0))
        y = max(content_top, (content_top + content_bottom - block_h) // 2)
        bottom = min(content_bottom, y + block_h + int(20 * u))
        card(y - int(40 * u), bottom, alpha=210)
        d.rounded_rectangle((margin - 40 * u, y - 40 * u, margin - 22 * u, bottom), 8, fill=accent)
        if layout == "warning":
            tri = [(margin, y + 70 * u), (margin + 40 * u, y), (margin + 80 * u, y + 70 * u)]
            d.polygon(tri, fill=RED)
            d.text((margin + 33 * u, y + 12 * u), "!", font=font(int(50 * u), 800), fill=WHITE)
            y = _text_block(d, (margin + int(110 * u), y - int(8 * u)), heading, hf, WHITE, max_w - int(110 * u))
        else:
            y = _text_block(d, (margin, y - int(8 * u)), heading, hf, WHITE, max_w)
        y += int(20 * u)
        for p in points[:4]:
            cx, cy = margin + int(24 * u), y + int(33 * u)
            d.ellipse((cx - 20 * u, cy - 20 * u, cx + 20 * u, cy + 20 * u), fill=accent)
            y = _text_block(d, (margin + int(70 * u), y), p, pf, WHITE, max_w - int(70 * u)) + int(16 * u)
        if layout == "warning":
            d.text((margin, bottom - int(80 * u)), WARNING_NOTE,
                   font=font(int(44 * u), 800), fill=YELLOW)
        if layout == "outro":
            pill_w, pill_h = int(420 * u), int(90 * u)
            px, py = margin, bottom - pill_h - int(30 * u)
            d.rounded_rectangle((px, py, px + pill_w, py + pill_h), pill_h // 2, fill=RED)
            sf = font(int(44 * u), 800)
            d.text((px + (pill_w - d.textlength("SUBSCRIBE", font=sf)) / 2, py + 18 * u), "SUBSCRIBE", font=sf, fill=WHITE)
            note = OUTRO_NOTE
            if portrait:  # not enough width beside the button: put the note above it
                d.text((px, py - int(65 * u)), note, font=font(int(34 * u), 500), fill=MINT)
            else:
                d.text((px + pill_w + int(30 * u), py + 24 * u), note, font=font(int(34 * u), 500), fill=MINT)

    img.save(out_png)
    return out_png


def render_background(size: tuple[int, int], out_png: Path) -> Path:
    """Brand gradient with a faint cross pattern (used when no stock footage is available)."""
    import numpy as np

    W, H = size
    c0, c1 = np.array(BG_GRADIENT[0], float), np.array(BG_GRADIENT[1], float)
    t = np.clip(np.add.outer(np.arange(H) / H * 0.6, np.arange(W) / W * 0.6), 0, 1)[..., None]
    img = Image.fromarray((c0 + (c1 - c0) * t).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    step = max(60, W // 32)
    for y in range(step // 2, H, step):
        for x in range(step // 2, W, step):
            d.rectangle((x - 6, y - 2, x + 6, y + 2), fill=(255, 255, 255, 14))
            d.rectangle((x - 2, y - 6, x + 2, y + 6), fill=(255, 255, 255, 14))
    img.save(out_png)
    return out_png


# ---------------------------------------------------------------- stock footage (Pexels, free)
def _download(url: str, dest: Path) -> Path:
    with requests.get(url, stream=True, timeout=120) as dl:
        dl.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in dl.iter_content(1 << 20):
                fh.write(chunk)
    return dest


def fetch_footage(query: str, size: tuple[int, int], dest: Path, used: set) -> Path | None:
    """A free stock clip: Pexels first, then Pixabay (each only if its API key is set)."""
    if not query:
        return None
    return _pexels_footage(query, size, dest, used) or _pixabay_footage(query, size, dest, used)


def _pexels_footage(query: str, size: tuple[int, int], dest: Path, used: set) -> Path | None:
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        return None
    W, H = size
    orientation = "portrait" if H > W else "landscape"
    try:
        r = requests.get(
            "https://api.pexels.com/videos/search",
            params={"query": query, "orientation": orientation, "size": "medium", "per_page": 10},
            headers={"Authorization": key}, timeout=30,
        )
        r.raise_for_status()
        for video in r.json().get("videos", []):
            if video["id"] in used:
                continue
            files = [f for f in video.get("video_files", [])
                     if f.get("file_type") == "video/mp4" and f.get("width") and f.get("height")
                     and min(f["width"], f["height"]) >= 720]
            if not files:
                continue
            best = min(files, key=lambda f: abs(f["width"] - W))
            _download(best["link"], dest)
            used.add(video["id"])
            return dest
    except Exception as e:
        print(f"  (No Pexels footage for '{query}': {e})")
    return None


def _pixabay_footage(query: str, size: tuple[int, int], dest: Path, used: set) -> Path | None:
    key = os.environ.get("PIXABAY_API_KEY")
    if not key:
        return None
    W, H = size
    portrait = H > W
    try:
        r = requests.get("https://pixabay.com/api/videos/",
                         params={"key": key.strip(), "q": query[:100], "per_page": 20, "safesearch": "true"},
                         timeout=30)
        r.raise_for_status()
        for hit in r.json().get("hits", []):
            if f"pixabay-{hit['id']}" in used:
                continue
            files = [f for f in (hit.get("videos") or {}).values()
                     if f.get("url") and f.get("width") and f.get("height")
                     and min(f["width"], f["height"]) >= 720 and (f["height"] > f["width"]) == portrait]
            if not files:
                continue
            best = min(files, key=lambda f: abs(f["width"] - W))
            _download(best["url"], dest)
            used.add(f"pixabay-{hit['id']}")
            return dest
    except Exception as e:
        print(f"  (No Pixabay footage for '{query}': {e})")
    return None


# ---------------------------------------------------------------- captions
def _ass_time(t: float) -> str:
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def write_ass(captions: list[tuple[float, float, str]], size: tuple[int, int], out: Path) -> Path:
    W, H = size
    portrait = H > W
    fs = int(W * (0.075 if portrait else 0.036))
    margin_v = int(H * (0.12 if portrait else 0.07))
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{caption_font_name()},{fs},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,{max(3, fs // 12)},2,2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [
        f"Dialogue: 0,{_ass_time(a)},{_ass_time(b)},Cap,,0,0,0,,{text.replace(chr(10), ' ')}"
        for a, b, text in captions
    ]
    out.write_text(header + "\n".join(lines) + "\n")
    return out


# ---------------------------------------------------------------- assembly
def _run(args: list[str]) -> None:
    proc = subprocess.run([ffmpeg_bin(), "-hide_banner", "-loglevel", "error", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{proc.stderr[-3000:]}")


def _escape_filter_path(p: Path) -> str:
    return str(p).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")


def render_scene(bg: Path, is_video: bool, overlay: Path, wav: Path, ass: Path | None,
                 duration: float, size: tuple[int, int], out: Path) -> Path:
    W, H = size
    frames = int(duration * FPS) + 1
    if is_video:
        bg_in = ["-stream_loop", "-1", "-i", str(bg)]
        bg_f = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
                f"eq=brightness=-0.10:saturation=0.85,setsar=1[bg]")
    else:  # slow zoom on the still gradient
        bg_in = ["-loop", "1", "-i", str(bg)]
        bg_f = (f"[0:v]scale={W * 2}:{H * 2},zoompan=z='min(zoom+0.0004,1.08)':d={frames}"
                f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},setsar=1[bg]")
    fade_out = max(0.0, duration - 0.3)
    chain = [
        bg_f,
        "[1:v]format=rgba,fade=t=in:st=0.15:d=0.5:alpha=1[ov]",
        f"[bg][ov]overlay=0:0,fade=t=in:st=0:d=0.3,fade=t=out:st={fade_out:.2f}:d=0.3",
    ]
    if ass:
        fonts = f":fontsdir='{_escape_filter_path(FONT_DIR)}'" if FONT_DIR.exists() else ""
        chain[-1] += f",subtitles='{_escape_filter_path(ass)}'{fonts}"
    chain[-1] += ",format=yuv420p[v]"
    _run([
        "-y", *bg_in, "-loop", "1", "-i", str(overlay), "-i", str(wav),
        "-filter_complex", ";".join(chain),
        "-map", "[v]", "-map", "2:a", "-t", f"{duration:.3f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
        str(out),
    ])
    return out


def render_host_scene(talk: Path, wav: Path, ass: Path | None, duration: float, size: tuple[int, int],
                      out: Path, landscape_crop: float = 1.0) -> Path:
    """The talking host, centred over a blurred copy of the same picture, with captions; audio is the narration.

    landscape_crop: in landscape videos, show only this top part of a tall host clip (head to waist).
    """
    W, H = size
    fade_out = max(0.0, duration - 0.3)
    talk_in = f"[0:v]fps={FPS},tpad=stop_mode=clone:stop_duration=5"
    if W > H and landscape_crop < 1:
        talk_in += f",crop=iw:trunc(ih*{landscape_crop}/2)*2:0:0"
    fades = f"fade=t=in:st=0:d=0.3,fade=t=out:st={fade_out:.2f}:d=0.3"
    if H > W:  # vertical: the host fills the screen (waist-up, sides cropped)
        chain = [f"{talk_in},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,{fades}"]
    else:  # landscape: the host in the middle, a blurred copy of the picture fills the sides
        chain = [
            f"{talk_in},split[a][b]",
            f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=28:2,eq=brightness=-0.06[bg]",
            f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease,setsar=1[fg]",
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,{fades}",
        ]
    if ass:
        fonts = f":fontsdir='{_escape_filter_path(FONT_DIR)}'" if FONT_DIR.exists() else ""
        chain[-1] += f",subtitles='{_escape_filter_path(ass)}'{fonts}"
    chain[-1] += ",format=yuv420p[v]"
    _run([
        "-y", "-i", str(talk), "-i", str(wav),
        "-filter_complex", ";".join(chain),
        "-map", "[v]", "-map", "1:a", "-t", f"{duration:.3f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
        str(out),
    ])
    return out


def concat(parts: list[Path], out: Path) -> Path:
    listfile = out.with_suffix(".txt")
    listfile.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    _run(["-y", "-f", "concat", "-safe", "0", "-i", str(listfile), "-c", "copy", "-movflags", "+faststart", str(out)])
    return out


def build_video(plan, video_cfg: dict, voice_cfg: dict, channel_name: str, workdir: Path) -> Path:
    """Narrate every scene, render its graphic, and join everything into one captioned video."""
    from . import voice

    ensure_fonts()
    size = (1080, 1920) if video_cfg.get("format") == "shorts" else (1920, 1080)
    scenes_dir = workdir / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    gradient = render_background(size, scenes_dir / "gradient.png")
    use_footage = video_cfg.get("stock_footage", True)
    used: set = set()

    narrated = []
    for i, scene in enumerate(plan.scenes, 1):
        print(f"    Narrating scene {i}/{len(plan.scenes)}: {scene.layout} - {scene.heading}")
        wav = scenes_dir / f"{i:02d}.wav"
        narrated.append((wav, *voice.narrate_scene(scene.narration, voice_cfg, wav)))

    # The host (talking photo, made on Kaggle) presents some scenes between the normal visuals
    host_cfg = video_cfg.get("host") or {}
    host = {}
    if host_cfg.get("enabled"):
        from . import talking

        picks = talking.pick_scenes(len(plan.scenes), host_cfg)
        print(f"    Making the host talk for scenes {[i + 1 for i in picks]} on Kaggle...")
        host = talking.make_clips({f"s{i + 1:02d}": narrated[i][0] for i in picks}, workdir, host_cfg)

    parts = []
    for i, (scene, (wav, duration, captions)) in enumerate(zip(plan.scenes, narrated), 1):
        print(f"    Scene {i}/{len(plan.scenes)}: {scene.layout} - {scene.heading}")
        ass = write_ass(captions, size, scenes_dir / f"{i:02d}.ass") if video_cfg.get("captions", True) else None
        talk = host.get(f"s{i:02d}")
        if talk:
            parts.append(render_host_scene(talk, wav, ass, duration, size, scenes_dir / f"{i:02d}.mp4",
                                           talking.landscape_crop(host_cfg)))
            continue
        overlay = render_overlay(scene, size, channel_name, scenes_dir / f"{i:02d}_overlay.png")
        clip = fetch_footage(scene.footage_query, size, scenes_dir / f"{i:02d}_bg.mp4", used) if use_footage else None
        parts.append(render_scene(clip or gradient, clip is not None, overlay, wav, ass, duration, size,
                                  scenes_dir / f"{i:02d}.mp4"))
    return concat(parts, workdir / "narrated.mp4")


# ---------------------------------------------------------------- thumbnail
BADGES = {
    "Explainer": ("EXPLAINED", TEAL),
    "Myth vs Fact": ("MYTH vs FACT", CORAL),
    "Warning Signs": ("WARNING SIGNS", RED),
    "Top Questions": ("YOUR QUESTIONS", (124, 58, 237)),
}


def fetch_photo(query: str, dest: Path) -> Path | None:
    """A landscape stock photo from Pexels (free) for the thumbnail background."""
    key = os.environ.get("PEXELS_API_KEY")
    if not key or not query:
        return None
    try:
        r = requests.get("https://api.pexels.com/v1/search",
                         params={"query": query, "orientation": "landscape", "per_page": 5},
                         headers={"Authorization": key}, timeout=30)
        r.raise_for_status()
        photos = r.json().get("photos", [])
        if not photos:
            return None
        url = photos[0]["src"].get("large2x") or photos[0]["src"]["original"]
        dest.write_bytes(requests.get(url, timeout=60).content)
        return dest
    except Exception as e:
        print(f"  (No thumbnail photo for '{query}': {e})")
        return None


def _cover(img: Image.Image, W: int, H: int) -> Image.Image:
    scale = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * scale) + 1, int(img.height * scale) + 1), Image.LANCZOS)
    left, top = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((left, top, left + W, top + H))


def make_thumbnail(text: str, channel_name: str, out: Path, background: Path | None = None,
                   style: str | None = None, highlight: str | None = None, host: Path | None = None) -> Path:
    """Eye-catching 1280x720 thumbnail: photo on the right, huge text on the left, style badge, brand.

    host: optional cut-out PNG of the presenter (transparent background), shown waist-up on the right.
    """
    from PIL import ImageEnhance

    W, H = 1280, 720
    if background and background.exists():
        img = _cover(Image.open(background).convert("RGB"), W, H)
        img = ImageEnhance.Contrast(ImageEnhance.Color(img).enhance(1.25)).enhance(1.1)
    else:
        tmp = out.with_suffix(".bg.png")
        img = Image.open(render_background((W, H), tmp)).convert("RGB")
        tmp.unlink(missing_ok=True)
    img = img.convert("RGBA")

    # Dark brand gradient on the left so the text pops; the photo stays visible on the right
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for x in range(W):
        a = 245 if x < W * 0.38 else int(245 * max(0.0, 1 - (x - W * 0.38) / (W * 0.30)))
        sd.line([(x, 0), (x, H)], fill=(*NAVY, a))
    img.alpha_composite(shade)
    d = ImageDraw.Draw(img)

    # Style badge (top-left)
    label, color = BADGES.get(style or "", (None, None))
    top = 48
    if label:
        bf = font(40, 800)
        bw = d.textlength(label, font=bf) + 56
        d.rounded_rectangle((48, top, 48 + bw, top + 70), 35, fill=color)
        d.text((76, top + 10), label, font=bf, fill=WHITE)
        top += 100

    # Huge text, auto-sized to fit in 3 lines within the left ~62%
    words = text.upper().split()
    hl = (highlight or "").upper().strip(" ?!.,")
    host_img = Image.open(host).convert("RGBA") if host and Path(host).exists() else None
    max_w, max_lines = int(W * (0.56 if host_img else 0.62)), 3
    size = 150
    bottom_limit = H - 120  # keep clear of the brand badge
    while size > 70:
        f = font(size, 800)
        lines = _wrap(d, " ".join(words), f, max_w)
        fits_h = top + len(lines) * int(size * 1.08) + int(size * 0.25) <= bottom_limit
        if len(lines) <= max_lines and fits_h and all(d.textlength(l, font=f) <= max_w for l in lines):
            break
        size -= 6
    line_h = int(size * 1.08)
    block_h = len(lines) * line_h
    y = max(top, min((H - block_h) // 2 + 10, bottom_limit - block_h - int(size * 0.25)))
    for line in lines[:max_lines]:
        x = 48
        for word in line.split():
            fill = YELLOW if hl and word.strip(" ?!.,") == hl else WHITE
            d.text((x, y), word, font=f, fill=fill, stroke_width=max(6, size // 16), stroke_fill=(0, 0, 0))
            x += d.textlength(word + " ", font=f)
        y += line_h
    bar_y = y + int(size * 0.18)
    d.rounded_rectangle((48, bar_y, 48 + 220, bar_y + 14), 7, fill=YELLOW)

    if host_img:  # presenter from the waist up, standing in the bottom-right corner
        waist = host_img.crop((0, 0, host_img.width, int(host_img.height * 0.56)))
        scale = (H + 40) / waist.height
        waist = waist.resize((int(waist.width * scale), H + 40), Image.LANCZOS)
        glow = Image.new("RGBA", waist.size, (0, 0, 0, 0))
        glow.putalpha(waist.getchannel("A").point(lambda a: int(a * 0.55)))
        glow = glow.filter(ImageFilter.GaussianBlur(14))
        hx = W - waist.width + 30
        img.alpha_composite(glow, (hx + 10, 0))
        img.alpha_composite(waist, (hx, 0))
        d = ImageDraw.Draw(img)

    # Brand (bottom-right)
    nf = font(30, 800)
    name = channel_name.upper()
    nw = d.textlength(name, font=nf)
    bx, by = W - nw - 150, H - 88
    d.rounded_rectangle((bx - 20, by - 8, W - 36, by + 60), 34, fill=(*NAVY, 235))
    _brand_icon(d, int(bx + 26), int(by + 26), 44)
    d.text((bx + 64, by + 6), name, font=nf, fill=WHITE)
    img.convert("RGB").save(out, "JPEG", quality=92)
    return out
