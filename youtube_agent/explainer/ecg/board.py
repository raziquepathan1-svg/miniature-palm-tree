"""Osmosis-style whiteboard engine: a big board, a camera that pans/zooms, pictures that draw themselves
(outline traced like a pen, then colour fills in), handwritten labels written letter by letter, strokes and
arrows that draw on, and transient effects (glows, travelling pulses, chamber flashes).

Coordinates are LOGICAL board units (1 unit = 1 output pixel at camera zoom 1). The board is stored at BS
pixels per unit so zoom-ins stay sharp."""
import math
from collections import deque

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BS = 1.25
PAPER = (255, 255, 255)
INK = (32, 34, 44)
KALAM = "/root/.cache/yt-agent-fonts/Kalam-Bold.ttf"
SC = "/root/.cache/yt-agent-fonts/PatrickHandSC.ttf"
FONT = [KALAM]


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ramp(t, t0, d):
    return max(0.0, min(1.0, (t - t0) / max(d, 1e-3)))


def hfont(size):
    return ImageFont.truetype(FONT[0], max(8, int(size)))


# ------------------------------------------------------------------ trace order for a picture's outline
def trace_order(outline):
    """outline: bool array. Returns uint8 order map (0..254 along a pen path, 255 = not outline)."""
    h, w = outline.shape
    sc = max(1, int(math.ceil(max(h, w) / 420)))
    small = outline[::sc, ::sc].copy()
    sh, sw = small.shape
    dist = np.full((sh, sw), -1, np.int32)
    comps = []
    ys, xs = np.nonzero(small)
    order_idx = np.lexsort((xs, ys))
    for i in order_idx:
        y0, x0 = ys[i], xs[i]
        if dist[y0, x0] >= 0:
            continue
        q = deque([(y0, x0)])
        dist[y0, x0] = 0
        pix = []
        while q:
            y, x = q.popleft()
            pix.append((y, x))
            dv = dist[y, x] + 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < sh and 0 <= xx < sw and small[yy, xx] and dist[yy, xx] < 0:
                        dist[yy, xx] = dv
                        q.append((yy, xx))
        comps.append(pix)
    comps.sort(key=lambda c: -len(c))
    total = sum(len(c) for c in comps) or 1
    order_small = np.full((sh, sw), 255, np.float32)
    start = 0.0
    for c in comps:
        span = len(c) / total
        dmax = max(dist[y, x] for y, x in c) or 1
        for y, x in c:
            order_small[y, x] = (start + span * dist[y, x] / dmax) * 254
        start += span
    big = np.repeat(np.repeat(order_small, sc, 0), sc, 1)[:h, :w]
    # fill outline pixels that the subsampling missed with the nearest small value (grow a few times)
    out = np.where(outline, big, 255).astype(np.float32)
    for _ in range(sc + 2):
        miss = outline & (out >= 255)
        if not miss.any():
            break
        g = out.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            g = np.minimum(g, np.roll(np.roll(out, dy, 0), dx, 1))
        out[miss] = g[miss]
    out[outline & (out >= 255)] = 254
    return out.astype(np.uint8)


# ------------------------------------------------------------------ items
class Picture:
    def __init__(self, rgba, x, y, h=None, w=None, t=0.0, outline_dur=2.0, fill_dur=0.8, center=True):
        self.src = rgba
        if h:
            sc = h / rgba.height
        else:
            sc = w / rgba.width
        self.w_u, self.h_u = rgba.width * sc, rgba.height * sc
        self.x_u = x - self.w_u / 2 if center else x
        self.y_u = y - self.h_u / 2 if center else y
        pw, ph = int(self.w_u * BS), int(self.h_u * BS)
        self.img = rgba.resize((pw, ph), Image.LANCZOS)
        a = np.array(self.img)
        lum = a[..., :3].mean(-1)
        self.outline = (a[..., 3] > 100) & (lum < 95)
        self.order = trace_order(self.outline)
        self.t, self.d1, self.d2 = t, outline_dur, fill_dur
        self.end = t + outline_dur + fill_dur
        ink = np.zeros_like(a)
        ink[..., :3] = INK
        self.ink = ink
        self.px, self.py = int(self.x_u * BS), int(self.y_u * BS)

    def partial(self, t):
        if t < self.t + self.d1:
            p = ramp(t, self.t, self.d1)
            m = self.order <= int(p * 254)
            a = self.ink.copy()
            a[..., 3] = (m * 255).astype(np.uint8)
            return Image.fromarray(a)
        f = ramp(t, self.t + self.d1, self.d2)
        a = np.array(self.img).copy()
        alpha = a[..., 3].astype(np.float32) * f
        alpha[self.outline] = a[..., 3][self.outline]
        a[..., 3] = alpha.astype(np.uint8)
        return Image.fromarray(a)

    def final(self):
        return self.img

    def map(self, p_src):
        """source-image pixel -> logical board coords"""
        return (self.x_u + p_src[0] * self.w_u / self.src.width, self.y_u + p_src[1] * self.h_u / self.src.height)


TEXT_SCALE = [1.15]     # bigger handwriting for readability (owner: words were too thin/small)
TEXT_BOLD = [0.032]      # stroke width as a share of the font size
TEXT_DARK = [0.8]      # colour multiplier (<1 = darker)


class Text:
    def __init__(self, text, x, y, size, color=INK, t=0.0, dur=None, anchor="l"):
        size = size * TEXT_SCALE[0]
        color = tuple(int(c * TEXT_DARK[0]) for c in color[:3])
        while 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2] > 115:   # keep labels readable on white
            color = tuple(int(c * 0.88) for c in color)
        f = hfont(size * BS)
        sw = int(round(size * BS * TEXT_BOLD[0]))
        box = f.getbbox(text, stroke_width=sw)
        lay = Image.new("RGBA", (box[2] + 16 + 2 * sw, int(size * BS * 1.45) + 10 + 2 * sw), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((8 + sw, 4 + sw), text, font=f, fill=color, stroke_width=sw, stroke_fill=color)
        self.img = lay
        self.label = text
        self.cols = np.where(np.array(lay)[..., 3].max(0) > 0)[0]
        w_u = lay.width / BS
        x0 = x - w_u if anchor == "r" else (x - w_u / 2 if anchor == "c" else x)
        self.px, self.py = int(x0 * BS), int((y - size * 0.75) * BS)
        self.t = t
        self.dur = dur if dur is not None else 0.25 + 0.055 * len(text)
        self.end = t + self.dur

    def partial(self, t):
        p = ramp(t, self.t, self.dur)
        if len(self.cols) == 0:
            return self.img
        right = int(self.cols[0] + (self.cols[-1] + 1 - self.cols[0]) * p)
        a = np.array(self.img).copy()
        a[:, right:, 3] = 0
        return Image.fromarray(a)

    def final(self):
        return self.img


class Stroke:
    """Polyline in logical coords that draws itself; optional arrow head, optional closed."""
    def __init__(self, pts, color=INK, width=6, t=0.0, dur=1.0, arrow=False, closed=False, shadow=None):
        self.pts = list(pts) + ([pts[0]] if closed else [])
        self.color, self.width, self.t, self.dur, self.arrow, self.shadow = color, width, t, dur, arrow, shadow
        self.end = t + dur
        xs = [p[0] for p in self.pts]
        ys = [p[1] for p in self.pts]
        pad = width * 3 + 30
        self.bx, self.by = min(xs) - pad, min(ys) - pad
        self.bw, self.bh = max(xs) - self.bx + pad, max(ys) - self.by + pad
        self.px, self.py = int(self.bx * BS), int(self.by * BS)
        self._final = None

    def _draw(self, frac):
        lay = Image.new("RGBA", (int(self.bw * BS) + 2, int(self.bh * BS) + 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        q = [((x - self.bx) * BS, (y - self.by) * BS) for x, y in partial_pts(self.pts, frac)]
        if len(q) > 1:
            if self.shadow:
                d.line(q, fill=self.shadow, width=int((self.width + 4) * BS), joint="curve")
            d.line(q, fill=self.color, width=int(self.width * BS), joint="curve")
            r = self.width * BS / 2
            for x, y in (q[0], q[-1]):
                d.ellipse((x - r, y - r, x + r, y + r), fill=self.color)
            if self.arrow and frac >= 0.999:
                (x0, y0), (x1, y1) = q[-2], q[-1]
                ang = math.atan2(y1 - y0, x1 - x0)
                L = (self.width * 3.2 + 10) * BS
                for s in (-1, 1):
                    a = ang + math.pi + s * 0.5
                    d.line([(x1, y1), (x1 + L * math.cos(a), y1 + L * math.sin(a))], fill=self.color,
                           width=int(self.width * BS))
        return lay

    def partial(self, t):
        return self._draw(ramp(t, self.t, self.dur))

    def final(self):
        if self._final is None:
            self._final = self._draw(1.0)
        return self._final


def partial_pts(pts, frac):
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + math.dist(a, b))
    lim = L[-1] * max(0.0, min(1.0, frac))
    out = [pts[0]]
    for i in range(1, len(pts)):
        if L[i] <= lim:
            out.append(pts[i])
        else:
            u = (lim - L[i - 1]) / max(L[i] - L[i - 1], 1e-6)
            out.append((pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * u, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * u))
            break
    return out


def smooth(pts, n=10):
    """Catmull-Rom through pts (open)."""
    if len(pts) < 3:
        return list(pts)
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


# ------------------------------------------------------------------ board + camera
class Board:
    def __init__(self, cols, rows):
        self.wu, self.hu = cols * W, rows * H
        self.items = []
        self.fx = []        # transient effects: fn(draw_ctx, t) with ctx.to_px
        self.cam = []       # (t, cx, cy, zoom, move_dur)
        self.committed = Image.new("RGB", (int(self.wu * BS), int(self.hu * BS)), PAPER)
        self.done = set()
        self.erases = []    # (t, dur, [items])
        self.gone = set()

    def erase(self, t, items, dur=0.5):
        self.erases.append((t, dur, [id(i) for i in items]))

    def _rebuild(self):
        self.committed = Image.new("RGB", self.committed.size, PAPER)
        for i, it in enumerate(self.items):
            if i in self.done and id(it) not in self.gone:
                f = it.final()
                self.committed.paste(f, (it.px, it.py), f)

    def add(self, it):
        self.items.append(it)
        return it

    def camera(self, t, cx, cy, zoom=1.0, dur=1.0):
        self.cam.append((t, cx, cy, zoom, dur))
        self.cam.sort(key=lambda c: c[0])

    def cam_at(self, t):
        cx, cy, z = self.cam[0][1:4]
        for (t0, x, y, zz, d) in self.cam:
            if t < t0:
                break
            e = ease((t - t0) / d) if d > 0 else 1.0
            # interpolate in log-zoom for natural zoom feel
            cx, cy = cx + (x - cx) * e, cy + (y - cy) * e
            z = math.exp(math.log(z) + (math.log(zz) - math.log(z)) * e)
        return cx, cy, z

    def frame(self, t):
        for i, it in enumerate(self.items):
            if i not in self.done and t >= it.end and id(it) not in self.gone:
                f = it.final()
                self.committed.paste(f, (it.px, it.py), f)
                self.done.add(i)
        fading = []
        for (te, de, ids) in self.erases:
            if t >= te and any(i not in self.gone for i in ids):
                self.gone.update(ids)
                self._rebuild()
            if te <= t < te + de:
                fading += [(it, 1 - (t - te) / de) for it in self.items if id(it) in ids]
        cx, cy, z = self.cam_at(t)
        vw, vh = W / z, H / z
        if vw < self.wu:
            cx = min(max(cx, vw / 2), self.wu - vw / 2)
        if vh < self.hu:
            cy = min(max(cy, vh / 2), self.hu - vh / 2)
        x0, y0 = (cx - vw / 2) * BS, (cy - vh / 2) * BS
        box = (int(x0), int(y0), int(x0 + vw * BS), int(y0 + vh * BS))
        crop = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), PAPER + (255,))
        ix0, iy0 = max(0, box[0]), max(0, box[1])
        ix1, iy1 = min(self.committed.width, box[2]), min(self.committed.height, box[3])
        if ix1 > ix0 and iy1 > iy0:
            crop.paste(self.committed.crop((ix0, iy0, ix1, iy1)), (ix0 - box[0], iy0 - box[1]))
        for i, it in enumerate(self.items):
            if i in self.done or t < it.t or id(it) in self.gone:
                continue
            p = it.partial(t)
            if self._inside(it, box, p):
                paste_clipped(crop, p, (it.px - box[0], it.py - box[1]))
        for it, a in fading:
            f = it.final().copy()
            f.putalpha(f.getchannel("A").point(lambda v, a=a: int(v * a)))
            paste_clipped(crop, f, (it.px - box[0], it.py - box[1]))
        ctx = Ctx(box)
        for fx in self.fx:
            fx(crop, ctx, t)
        return crop.convert("RGB").resize((W, H), Image.LANCZOS if z < 1 else Image.BICUBIC)

    @staticmethod
    def _inside(it, box, p):
        return not (it.px > box[2] or it.py > box[3] or it.px + p.width < box[0] or it.py + p.height < box[1])


class Ctx:
    def __init__(self, box):
        self.box = box

    def px(self, p):
        return (p[0] * BS - self.box[0], p[1] * BS - self.box[1])


def paste_clipped(crop, img, xy):
    """alpha_composite that tolerates negative / out-of-range offsets."""
    x, y = int(xy[0]), int(xy[1])
    sx, sy = max(0, -x), max(0, -y)
    if sx >= img.width or sy >= img.height:
        return
    part = img.crop((sx, sy, img.width, img.height))
    x, y = x + sx, y + sy
    if x >= crop.width or y >= crop.height:
        return
    part = part.crop((0, 0, min(part.width, crop.width - x), min(part.height, crop.height - y)))
    crop.alpha_composite(part, (x, y))


class Pop:
    """An illustration that appears softly (fade + slight grow), like Osmosis pictures popping in."""
    def __init__(self, rgba, x, y, h=None, w=None, t=0.0, dur=0.6):
        sc = h / rgba.height if h else w / rgba.width
        self.src = rgba
        self.w_u, self.h_u = rgba.width * sc, rgba.height * sc
        self.x_u, self.y_u = x - self.w_u / 2, y - self.h_u / 2
        self.img = rgba.resize((int(self.w_u * BS), int(self.h_u * BS)), Image.LANCZOS)
        self.px, self.py = int(self.x_u * BS), int(self.y_u * BS)
        self.t, self.dur, self.end = t, dur, t + dur

    def partial(self, t):
        a = ease(ramp(t, self.t, self.dur))
        im = self.img.copy()
        im.putalpha(im.getchannel("A").point(lambda v, a=a: int(v * a)))
        return im

    def final(self):
        return self.img

    def map(self, p_src):
        return (self.x_u + p_src[0] * self.w_u / self.src.width, self.y_u + p_src[1] * self.h_u / self.src.height)


class Panel:
    """Soft rounded pastel panel behind a group of notes (Osmosis style)."""
    def __init__(self, x0, y0, x1, y1, fill=(250, 232, 234), t=0.0, dur=0.4, r=26):
        self.box = (x0, y0, x1, y1)
        w, h = int((x1 - x0) * BS), int((y1 - y0) * BS)
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(self.img).rounded_rectangle((0, 0, w - 1, h - 1), radius=int(r * BS), fill=fill + (255,))
        self.px, self.py = int(x0 * BS), int(y0 * BS)
        self.t, self.dur, self.end = t, dur, t + dur

    def partial(self, t):
        a = ease(ramp(t, self.t, self.dur))
        im = self.img.copy()
        im.putalpha(im.getchannel("A").point(lambda v, a=a: int(v * a)))
        return im

    def final(self):
        return self.img
