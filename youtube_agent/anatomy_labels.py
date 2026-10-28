"""Textbook-style labels on our anatomy clips (heart, lungs, brain...): the organ's name, then each part
appears with a line pointing at it, then one "how it works" line. The labels are drawn onto a copy of
the clip, which is then used like any other footage clip.

Each clip's labels are in branding/health-support-studio/footage/labels.yaml (positions as fractions
of the frame, times in seconds of the clip):

    16x9_lungs_breathing.mp4:
      title: "The Lungs"
      labels:
        - {text: "Windpipe (trachea)", at: [0.06, 0.22], to: [0.495, 0.25], start: 0.6}   # optional end: 2.5
      note: {text: "Air in: oxygen goes into the blood", start: 3.6}
      until: 3.5            # the label lines fade here (the camera starts turning)

    python -m youtube_agent.anatomy_labels 16x9_lungs_breathing.mp4 out.mp4
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw

from .editor import ffmpeg_bin
from .visuals import ensure_fonts, font

FOOTAGE = Path(__file__).resolve().parent.parent / "branding/health-support-studio/footage"
LABELS = FOOTAGE / "labels.yaml"
FPS = 24
WHITE, ACCENT, SHADOW = (255, 255, 255, 255), (255, 214, 64, 255), (0, 0, 0, 150)


def _probe(src: Path) -> tuple[int, int, float]:
    """Width, height and length of a clip (from ffmpeg's own report: no ffprobe needed)."""
    import re

    err = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", str(src)], capture_output=True, text=True).stderr
    w, h = (int(v) for v in re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", err).groups())
    hh, mm, ss = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err).groups()
    return w, h, int(hh) * 3600 + int(mm) * 60 + float(ss)


def _ease(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _text(d: ImageDraw.ImageDraw, xy, text: str, size: int, color, alpha: float, anchor="la") -> tuple:
    f = font(size, 700)
    a = int(255 * alpha)
    for dx, dy in ((2, 2), (3, 3)):  # soft shadow so it reads on any background
        d.text((xy[0] + dx, xy[1] + dy), text, font=f, fill=SHADOW[:3] + (int(SHADOW[3] * alpha),), anchor=anchor)
    d.text(xy, text, font=f, fill=color[:3] + (a,), anchor=anchor)
    return d.textbbox(xy, text, font=f, anchor=anchor)


def frame(spec: dict, w: int, h: int, t: float) -> Image.Image:
    """The label layer (transparent) at time t."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = h / 720
    until = float(spec.get("until", 99))
    fade = 1 - _ease((t - until) / 0.4)  # label lines go when the camera turns
    if spec.get("title"):
        a = _ease(t / 0.5)
        _text(d, (int(0.05 * w), int(0.06 * h)), spec["title"].upper(), int(46 * s), ACCENT, a)
    for lab in spec.get("labels", []):
        p = (t - float(lab["start"])) / 0.6
        lfade = min(fade, 1 - _ease((t - float(lab.get("end", 99))) / 0.4))  # a label can leave early
        if p <= 0 or lfade <= 0:
            continue
        ax, ay = lab["at"][0] * w, lab["at"][1] * h
        tx, ty = lab["to"][0] * w, lab["to"][1] * h
        right = ax > tx  # text on the right side of the organ
        box = _text(d, (ax, ay), lab["text"], int(30 * s), WHITE, _ease(p * 2) * lfade,
                    anchor="rm" if not right else "lm")
        sx = box[2] + 10 * s if not right else box[0] - 10 * s
        k = _ease(p)  # the line grows from the text to the part
        ex, ey = sx + (tx - sx) * k, ay + (ty - ay) * k
        col = WHITE[:3] + (int(230 * lfade),)
        d.line([(sx, ay), (ex, ey)], fill=col, width=max(2, int(3 * s)))
        if k >= 1:
            r = 6 * s
            d.ellipse([tx - r, ty - r, tx + r, ty + r], fill=ACCENT[:3] + (int(255 * lfade),))
    note = spec.get("note")
    if note and t >= float(note["start"]):
        a = _ease((t - float(note["start"])) / 0.5)
        f = font(int(34 * s), 700)
        tw = d.textlength(note["text"], font=f)
        x0, y0 = 0.05 * w - 18 * s, 0.06 * h + 62 * s  # under the title: the captions use the bottom
        d.rounded_rectangle([x0, y0, x0 + tw + 36 * s, y0 + 60 * s], radius=int(14 * s),
                            fill=(10, 30, 60, int(190 * a)))
        _text(d, (x0 + 18 * s, y0 + 30 * s), note["text"], int(34 * s), WHITE, a, anchor="lm")
    return img


def label_clip(src: Path, spec: dict, out: Path) -> Path:
    """Draws the labels onto a copy of the clip (no sound, like our other footage)."""
    ensure_fonts()
    w, h, dur = _probe(src)
    cmd = [ffmpeg_bin(), "-loglevel", "error", "-y", "-i", str(src), "-f", "rawvideo", "-pix_fmt", "rgba",
           "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-",
           "-filter_complex", f"[0:v]fps={FPS}[b];[b][1:v]overlay=0:0:shortest=1,format=yuv420p[v]",
           "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "17", "-preset", "slow", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(int(dur * FPS)):
        proc.stdin.write(frame(spec, w, h, n / FPS).tobytes())
    proc.stdin.close()
    if proc.wait():
        raise RuntimeError("ffmpeg failed while drawing the labels")
    return out


if __name__ == "__main__":
    name, dest = sys.argv[1], Path(sys.argv[2])
    spec = (yaml.safe_load(LABELS.read_text()) or {})[name]
    print(label_clip(FOOTAGE / spec.get("source", name), spec, dest))
