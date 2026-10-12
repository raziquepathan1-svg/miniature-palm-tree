"""Whiteboard animation: a marker writes the words and draws the diagrams on a white board while the narrator
explains. Everything is drawn in code (handwriting font, hand-drawn lines and arrows), so labels are always
spelled right and no AI image is needed.

A board is a list of items, each drawn during its own time window:
  {"t": 1.0, "dur": 2.0, "kind": "text", "x": 120, "y": 80, "text": "Heart", "size": 90, "color": "ink"}
  {"t": 3.0, "dur": 1.0, "kind": "line", "points": [[x, y], ...], "color": "blue", "arrow": true}
  {"t": 4.0, "dur": 1.5, "kind": "box", "x": 600, "y": 300, "w": 300, "h": 200}
  {"t": 5.0, "dur": 1.0, "kind": "circle", "x": 900, "y": 500, "r": 80}
  {"t": 6.0, "dur": 0.0, "kind": "wipe"}      (clears the board: next page)
"""

import math
import random
import subprocess
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont

from .editor import ffmpeg_bin
from .visuals import FONT_DIR

W, H, FPS = 1920, 1080, 30
COLORS = {"ink": (30, 34, 44), "blue": (35, 92, 196), "red": (204, 40, 46), "green": (32, 138, 76),
          "orange": (226, 120, 20), "grey": (120, 124, 132)}
KALAM_URL = "https://fonts.gstatic.com/s/kalam/v18/YA9Qr0Wd4kDdMtDqHQLL.ttf"


def _font(size: int) -> ImageFont.FreeTypeFont:
    path = FONT_DIR / "Kalam-Bold.ttf"
    if not path.exists():
        FONT_DIR.mkdir(parents=True, exist_ok=True)
        path.write_bytes(requests.get(KALAM_URL, timeout=60).content)
    return ImageFont.truetype(str(path), size)


def _color(c) -> tuple:
    return COLORS.get(c, COLORS["ink"]) if isinstance(c, str) else tuple(c)


def _board() -> Image.Image:
    """Off-white board with a very faint texture, like a real whiteboard."""
    rng = np.random.default_rng(7)
    base = np.full((H, W, 3), 250, np.float32)
    base += rng.normal(0, 1.2, (H, W, 1))
    yy = np.linspace(-1, 1, H)[:, None, None]
    xx = np.linspace(-1, 1, W)[None, :, None]
    base -= 6 * (xx ** 2 + yy ** 2)  # soft vignette
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))


def _wobble(points: list, seed: int, amp: float = 2.2, step: float = 14) -> list:
    """Resample a polyline and add a smooth, small wobble so it looks drawn by hand."""
    if not amp:  # straight lines: keep the corners only, so edges stay clean
        return [tuple(p) for p in points]
    rnd = random.Random(seed)
    out = []
    phase, freq = rnd.uniform(0, 6.28), rnd.uniform(0.02, 0.04)
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        n = max(2, int(seg / step))
        nx, ny = (-(y1 - y0) / seg, (x1 - x0) / seg) if seg else (0, 0)
        for i in range(n):
            f = i / n
            x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
            d = amp * math.sin(phase + freq * len(out) * step)
            out.append((x + nx * d, y + ny * d))
    out.append(tuple(points[-1]))
    return out


def _shape_points(it: dict) -> list:
    k = it["kind"]
    if k == "line":
        return [tuple(p) for p in it["points"]]
    if k == "box":
        x, y, w, h = it["x"], it["y"], it["w"], it["h"]
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y + 2)]
    if k == "circle":
        cx, cy, rx = it["x"], it["y"], it["r"]
        ry = it.get("ry", rx)
        return [(cx + rx * math.cos(a), cy + ry * math.sin(a))
                for a in np.linspace(-math.pi / 2, 1.5 * math.pi + 0.15, 90)]
    if k == "heart":  # a simple hand-drawn heart shape
        cx, cy, s = it["x"], it["y"], it["size"] / 34
        return [(cx + s * 16 * math.sin(t) ** 3,
                 cy - s * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)))
                for t in np.linspace(0, 2 * math.pi, 120)]
    raise ValueError(k)


class _Stroke:
    def __init__(self, it: dict, seed: int):
        self.it = it
        self.color = _color(it.get("color", "ink"))
        self.width = it.get("width", 12)
        self.pts = _wobble(_shape_points(it), seed, amp=it.get("wobble", 0.0))
        self.cum = [0.0]
        for a, b in zip(self.pts, self.pts[1:]):
            self.cum.append(self.cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
        self.done = 0

    def draw_to(self, d: ImageDraw.ImageDraw, frac: float):
        """Draw from where we stopped up to this fraction of the length; returns the pen tip."""
        target = frac * self.cum[-1]
        i = self.done
        while i + 1 < len(self.pts) and self.cum[i + 1] <= target:
            d.line([self.pts[i], self.pts[i + 1]], fill=self.color, width=self.width)
            d.ellipse([self.pts[i + 1][0] - self.width / 2, self.pts[i + 1][1] - self.width / 2,
                       self.pts[i + 1][0] + self.width / 2, self.pts[i + 1][1] + self.width / 2], fill=self.color)
            i += 1
        self.done = i
        tip = self.pts[i]
        if i + 1 < len(self.pts) and frac < 1:
            a, b = self.pts[i], self.pts[i + 1]
            f = (target - self.cum[i]) / max(1e-6, self.cum[i + 1] - self.cum[i])
            tip = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
            d.line([a, tip], fill=self.color, width=self.width)
        if frac >= 1 and self.it.get("arrow") and not getattr(self, "headed", False):
            self.headed = True
            (x0, y0), (x1, y1) = self.pts[-4] if len(self.pts) > 4 else self.pts[0], self.pts[-1]
            ang, L = math.atan2(y1 - y0, x1 - x0), self.it.get("head", 38)
            for s in (-0.5, 0.5):
                d.line([(x1, y1), (x1 - L * math.cos(ang + s), y1 - L * math.sin(ang + s))],
                       fill=self.color, width=self.width)
        return tip


class _Text:
    def __init__(self, it: dict):
        self.it = it
        f = _font(it.get("size", 70))
        box = f.getbbox(it["text"])
        self.layer = Image.new("RGBA", (box[2] + 20, box[3] + 30), (0, 0, 0, 0))
        ImageDraw.Draw(self.layer).text((10, 10), it["text"], font=f, fill=_color(it.get("color", "ink")))
        x, y = it["x"], it["y"]
        if it.get("align") == "center":
            x -= self.layer.width // 2
        self.x, self.y = int(x), int(y)
        self.cols = np.where(np.asarray(self.layer)[..., 3].max(0) > 0)[0]
        self.shown = 0

    def draw_to(self, board: Image.Image, frac: float):
        right = int(self.cols[-1] + 1) if len(self.cols) else 0
        x_to = int(frac * right) if frac < 1 else self.layer.width
        if x_to > self.shown:
            part = self.layer.crop((self.shown, 0, x_to, self.layer.height))
            board.paste(part, (self.x + self.shown, self.y), part)
            self.shown = x_to
        h = self.layer.height
        bob = (0.35 + 0.25 * math.sin(frac * 90)) * h  # the pen moves up and down while writing
        return (self.x + x_to, self.y + bob)


def _pen(frame: Image.Image, tip, color) -> None:
    """A marker pen held at an angle, its tip on the board."""
    x, y = tip
    d = ImageDraw.Draw(frame)
    ang = math.radians(-58)
    ux, uy = math.cos(ang), math.sin(ang)
    nx, ny = -uy, ux

    def quad(a, b, w):
        return [(x + ux * a + nx * w, y + uy * a + ny * w), (x + ux * b + nx * w, y + uy * b + ny * w),
                (x + ux * b - nx * w, y + uy * b - ny * w), (x + ux * a - nx * w, y + uy * a - ny * w)]

    shadow = [(px + 14, py + 10) for px, py in quad(30, 330, 20)]
    d.polygon(shadow, fill=(200, 200, 200))
    d.polygon([(x, y), (x + ux * 30 + nx * 9, y + uy * 30 + ny * 9), (x + ux * 30 - nx * 9, y + uy * 30 - ny * 9)],
              fill=color)
    d.polygon(quad(28, 70, 16), fill=(235, 235, 235))
    d.polygon(quad(70, 330, 21), fill=color)
    d.polygon(quad(85, 330, 7), fill=tuple(min(255, c + 60) for c in color))


def render(items: list, duration: float, out: Path, audio: Path | None = None) -> Path:
    """Draws the board frame by frame and encodes it (with the narration if given)."""
    clean = _board()
    board = clean.copy()
    objs = []
    for n, it in enumerate(sorted(items, key=lambda i: i["t"])):
        objs.append((it, _Text(it) if it["kind"] == "text" else None if it["kind"] == "wipe" else _Stroke(it, n)))
    cmd = [ffmpeg_bin(), "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-"]
    if audio:
        cmd += ["-i", str(audio), "-c:a", "aac", "-b:a", "160k", "-shortest"]
    cmd += ["-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-preset", "medium", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    pending = list(objs)
    active: list = []
    tip, pen_color, last_tip_t = None, COLORS["ink"], -9.0
    for f in range(int(duration * FPS)):
        t = f / FPS
        while pending and pending[0][0]["t"] <= t:
            it, obj = pending.pop(0)
            if it["kind"] == "wipe":
                board = clean.copy()
                active = []
            else:
                active.append((it, obj))
        d = ImageDraw.Draw(board)
        still = []
        for it, obj in active:
            frac = min(1.0, (t - it["t"]) / max(it.get("dur", 1.0), 1e-3))
            tip = obj.draw_to(board, frac) if isinstance(obj, _Text) else obj.draw_to(d, frac)
            pen_color, last_tip_t = _color(it.get("color", "ink")), t
            if frac < 1:
                still.append((it, obj))
        active = still
        frame = board.copy()
        if tip and t - last_tip_t < 0.4:  # the pen leaves the board when nothing is being drawn
            _pen(frame, tip, pen_color)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()
    return out


def heart_demo() -> tuple[list, float]:
    """'How your heart pumps blood': a test page."""
    I = []

    def add(t, dur, kind, **kw):
        I.append({"t": t, "dur": dur, "kind": kind, **kw})

    add(0.3, 2.2, "text", x=960, y=40, text="How Your Heart Pumps Blood", size=86, align="center")
    add(2.5, 0.8, "line", points=[[560, 168], [1360, 168]], color="red")
    # the heart: four rooms (your right side is on the left of the picture)
    add(3.4, 2.0, "box", x=560, y=380, w=800, h=520)
    add(5.4, 0.7, "line", points=[[960, 380], [960, 900]])
    add(6.1, 0.7, "line", points=[[560, 640], [1360, 640]])
    add(6.9, 1.2, "text", x=740, y=470, text="Right atrium", size=46, align="center", color="blue")
    add(8.1, 1.2, "text", x=740, y=770, text="Right ventricle", size=46, align="center", color="blue")
    add(9.3, 1.2, "text", x=1180, y=470, text="Left atrium", size=46, align="center", color="red")
    add(10.5, 1.2, "text", x=1180, y=770, text="Left ventricle", size=46, align="center", color="red")
    # oxygen-poor blood: body -> right side -> lungs
    add(12.0, 1.0, "text", x=250, y=450, text="Body", size=60, align="center", color="blue")
    add(13.0, 1.0, "line", points=[[330, 500], [550, 500]], color="blue", arrow=True)
    add(14.0, 0.7, "line", points=[[740, 560], [740, 760]], color="blue", arrow=True)
    add(14.9, 1.4, "line", points=[[925, 860], [925, 318]], color="blue", arrow=True)
    add(16.3, 1.2, "text", x=960, y=198, text="Lungs", size=64, align="center", color="green")
    add(17.5, 1.4, "circle", x=960, y=248, r=170, ry=56, color="green")
    # oxygen-rich blood: lungs -> left side -> body
    add(19.0, 1.0, "line", points=[[1000, 318], [1000, 450]], color="red", arrow=True)
    add(20.2, 0.7, "line", points=[[1180, 560], [1180, 760]], color="red", arrow=True)
    add(21.1, 1.2, "line", points=[[1370, 820], [1580, 820]], color="red", arrow=True)
    add(22.3, 1.0, "text", x=1690, y=775, text="Body", size=60, align="center", color="red")
    add(23.6, 1.6, "text", x=200, y=960, text="Blue = low in oxygen", size=46, color="blue")
    add(25.4, 1.6, "text", x=1280, y=960, text="Red = full of oxygen", size=46, color="red")
    return I, 28.5


if __name__ == "__main__":
    import sys

    items, dur = heart_demo()
    print(render(items, dur, Path(sys.argv[1] if len(sys.argv) > 1 else "whiteboard_demo.mp4")))
