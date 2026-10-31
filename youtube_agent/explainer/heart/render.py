"""Sample explainer: "The Heart: Anatomy & How Blood Flows". Everything is drawn in code (accurate by design):
a schematic heart with 4 chambers, 4 valves, great vessels, lungs and body, blood dots flowing along the real
path, labels with leader lines, and a text panel - all timed to the narration (word positions)."""
import json
import math
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # repo root
from youtube_agent import visuals  # noqa: E402

HERE = Path(__file__).resolve().parent
W, H, FPS, SS = 1920, 1080, 30, 2
BG = (255, 253, 251)
INK = (45, 48, 66)
MAROON = (150, 42, 66)
MUSCLE, MUSCLE_D = (246, 176, 186), (214, 112, 132)
BLUE, BLUE_D, BLUE_L = (104, 150, 226), (62, 102, 184), (214, 228, 250)
RED, RED_D, RED_L = (226, 82, 98), (176, 44, 62), (252, 214, 218)
LUNG, LUNG_D = (250, 196, 204), (218, 136, 152)
BODY, BODY_D = (255, 231, 206), (226, 176, 128)
GOLD = (246, 184, 60)
GRAY = (130, 134, 150)


def F(size, weight=700):
    return visuals.font(size * SS, weight)


def dur(path):
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


# ---------------------------------------------------------------- geometry
def spline(points, closed=True, n=14):
    """Catmull-Rom through the points (smooth hand-drawn shapes)."""
    pts = points + points[:3] if closed else [points[0]] + points + [points[-1]]
    out = []
    for i in range(len(pts) - 3):
        p0, p1, p2, p3 = pts[i:i + 4]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    if not closed:
        out.append(points[-1])
    return out


def S(pts, dx=0, dy=0, k=1.0, cx=640, cy=600):
    return [((x - cx) * k + cx + dx, (y - cy) * k + cy + dy) for x, y in pts]


HEART = [(470, 410), (560, 392), (650, 398), (740, 392), (830, 410), (885, 470), (912, 580), (900, 700), (860, 800),
         (800, 872), (752, 880), (680, 850), (580, 805), (500, 740), (452, 650), (440, 540)]
CAV = {"RA": [(478, 435), (560, 425), (605, 450), (612, 515), (585, 555), (515, 560), (472, 520)],
       "LA": [(708, 440), (790, 430), (858, 460), (866, 520), (830, 555), (740, 558), (706, 515)],
       "RV": [(492, 605), (575, 592), (618, 612), (624, 700), (600, 785), (555, 805), (508, 748), (482, 668)],
       "LV": [(712, 612), (790, 600), (838, 640), (846, 740), (812, 822), (772, 840), (736, 790), (708, 700)]}
CENTER = {"RA": (540, 490), "LA": (785, 495), "RV": (555, 690), "LV": (776, 720)}
VALVE = {"tricuspid": (548, 576), "mitral": (775, 580), "pulmonary": (636, 470), "aortic": (690, 482)}
IVC = [(400, 975), (400, 620), (430, 575), (478, 540)]
SVC = [(330, 300), (390, 345), (450, 400), (500, 432)]
TRUNK = [(636, 440), (636, 300), (626, 252)]
PV = [(800, 255), (805, 330), (795, 438)]
AORTA = [(690, 440), (690, 345), (712, 305), (790, 290), (875, 302), (938, 345), (952, 425), (952, 920)]
LUNGS = [(470, 160), (540, 118), (630, 135), (650, 200), (670, 135), (760, 118), (830, 160), (845, 230), (800, 268),
         (700, 262), (650, 240), (600, 262), (500, 268), (455, 230)]
FLOW = [(400, 990), (400, 620), (430, 575), (478, 540), (540, 490), (548, 576), (555, 690), (612, 640), (636, 590),
        (636, 470), (636, 300), (626, 240), (600, 200), (650, 175), (720, 180), (790, 210), (800, 255), (805, 330),
        (795, 438), (785, 495), (775, 580), (775, 710), (714, 640), (690, 590), (690, 482), (690, 345), (712, 305),
        (790, 290), (875, 302), (938, 345), (952, 425), (952, 920), (952, 990), (680, 1000), (400, 990)]


def cumlen(pts):
    out = [0.0]
    for a, b in zip(pts, pts[1:]):
        out.append(out[-1] + math.dist(a, b))
    return out


FLEN = cumlen(FLOW)
MARK = {"body0": 0, "ra": FLEN[4], "rv": FLEN[6], "pulm": FLEN[9], "lungs_in": FLEN[11], "lungs_mid": FLEN[13],
        "la": FLEN[19], "lv": FLEN[21], "aortic": FLEN[24], "body": FLEN[32], "end": FLEN[-1]}


def at(s):
    s %= FLEN[-1]
    for i in range(len(FLEN) - 1):
        if FLEN[i] <= s <= FLEN[i + 1]:
            t = (s - FLEN[i]) / max(FLEN[i + 1] - FLEN[i], 1e-6)
            a, b = FLOW[i], FLOW[i + 1]
            return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
    return FLOW[-1]


def flow_color(s):
    s %= FLEN[-1]
    if s < MARK["lungs_mid"] or s > MARK["body"]:
        return BLUE_D
    return RED_D


# ---------------------------------------------------------------- drawing helpers (on SS canvas)
def P(pts, ox=0, oy=0, k=1.0):
    return [((x * k + ox) * SS, (y * k + oy) * SS) for x, y in pts]


def mix(c, d_, t):
    return tuple(int(c[i] + (d_[i] - c[i]) * t) for i in range(3))


def tube(d, pts, color, edge, w=30, smooth=True, shine=True):
    pts = spline(pts, closed=False, n=10) if smooth and len(pts) > 2 else pts
    q = P(pts)
    d.line(q, fill=edge, width=(w + 8) * SS, joint="curve")
    d.line(q, fill=color, width=w * SS, joint="curve")
    for x, y in (q[0], q[-1]):
        r = w * SS / 2
        d.ellipse((x - r, y - r, x + r, y + r), fill=color)
    if shine:
        o = w * 0.2 * SS
        d.line([(x - o, y - o) for x, y in q], fill=mix(color, (255, 255, 255), 0.45), width=max(2, int(w * 0.22)) * SS,
               joint="curve")


def grad_blob(d, pts, c_in, c_out, outline, width=6, n=14, focus=(0.32, 0.28)):
    """Smooth shape with a soft radial shading (light where the light hits)."""
    q = P(spline(pts, n=n))
    img = d._image
    xs, ys = [x for x, _ in q], [y for _, y in q]
    x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)) + 2, int(max(ys)) + 2
    w, h = x1 - x0, y1 - y0
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon([(x - x0, y - y0) for x, y in q], fill=255)
    yy, xx = np.mgrid[0:h, 0:w]
    t = np.clip(np.hypot(xx - focus[0] * w, yy - focus[1] * h) / (0.95 * max(w, h)), 0, 1)[..., None]
    col = (np.array(c_in) * (1 - t) + np.array(c_out) * t).astype(np.uint8)
    g = Image.fromarray(np.dstack([col, np.full((h, w, 1), 255, np.uint8)]), "RGBA")
    img.paste(g, (x0, y0), mask)
    d.line(q + [q[0]], fill=outline, width=width * SS, joint="curve")


def blob(d, pts, fill, outline, width=6, n=14):
    q = P(spline(pts, n=n))
    d.polygon(q, fill=fill)
    d.line(q + [q[0]], fill=outline, width=width * SS, joint="curve")


def highlight(d, pts, w=14, alpha=120, blur=7):
    img = d._image
    hl = Image.new("RGBA", img.size, (255, 255, 255, 0))  # white, so the blur fades to white, not gray
    ImageDraw.Draw(hl).line(P(spline(pts, closed=False, n=10)), fill=(255, 255, 255, alpha), width=w * SS, joint="curve")
    img.alpha_composite(hl.filter(ImageFilter.GaussianBlur(blur * SS)))


def text(d, xy, s, size, color=INK, weight=700, anchor="la"):
    d.text((xy[0] * SS, xy[1] * SS), s, font=F(size, weight), fill=color, anchor=anchor)


def layer(fn):
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    fn(ImageDraw.Draw(img))
    return img.resize((W, H), Image.LANCZOS)


# ---------------------------------------------------------------- reusable pictures
def draw_vessels(d):
    tube(d, AORTA, RED, RED_D)
    tube(d, PV, RED, RED_D, w=24)
    tube(d, TRUNK, BLUE, BLUE_D)
    tube(d, IVC, BLUE, BLUE_D)
    tube(d, SVC, BLUE, BLUE_D, w=26)


def draw_lungs_body(d):
    grad_blob(d, LUNGS, (255, 222, 228), LUNG, LUNG_D, width=5, n=10)
    for pts in ([(540, 150), (560, 200), (590, 230)], [(760, 150), (740, 200), (710, 230)]):
        d.line(P(spline(pts, closed=False, n=8)), fill=LUNG_D, width=3 * SS, joint="curve")
    q = P([(350, 925), (980, 925), (980, 1040), (350, 1040)])
    d.rounded_rectangle((q[0][0], q[0][1], q[2][0], q[2][1]), radius=40 * SS, fill=BODY, outline=BODY_D, width=5 * SS)
    text(d, (665, 982), "BODY  (organs & tissues)", 30, (150, 100, 60), 700, "mm")


MUSCLE_IN, MUSCLE_OUT = (253, 206, 212), (228, 132, 150)


def draw_heart(d, tint=True):
    grad_blob(d, HEART, MUSCLE_IN, MUSCLE_OUT, MUSCLE_D, width=7, n=12)
    for pts in ([(470, 600), (520, 760), (640, 830)], [(880, 520), (885, 680), (820, 830)],
                [(560, 420), (640, 415), (720, 418)]):
        d.line(P(spline(pts, closed=False, n=8)), fill=(238, 160, 174), width=3 * SS, joint="curve")
    for k, pts in CAV.items():
        right = k in ("RA", "RV")
        if tint:
            c_in, c_out, edge = ((236, 243, 255), (190, 210, 246), BLUE) if right else ((255, 236, 239), (248, 190, 199), RED)
        else:
            c_in, c_out, edge = (255, 242, 245), (246, 214, 222), MUSCLE_D
        grad_blob(d, pts, c_in, c_out, edge, width=4, n=10, focus=(0.4, 0.3))
    cav = lambda right: ((214, 228, 252) if right else (252, 214, 220)) if tint else (250, 230, 236)  # noqa: E731
    for (x0, y0, x1, y1), right in (((522, 548, 576, 604), True), ((748, 548, 802, 612), False)):
        q = P([(x0, y0), (x1, y1)])
        d.rounded_rectangle((q[0][0], q[0][1], q[1][0], q[1][1]), radius=12 * SS, fill=cav(right))
    tube(d, [(612, 640), (636, 590), (636, 440)], cav(True), MUSCLE_D, w=22, smooth=False, shine=False)
    tube(d, [(714, 640), (690, 590), (690, 440)], cav(False), MUSCLE_D, w=22, smooth=False, shine=False)
    for a, b in (((533, 588), (530, 700)), ((566, 588), (586, 712)), ((760, 592), (752, 714)), ((792, 592), (812, 724))):
        d.line(P([a, b]), fill=(255, 255, 255), width=2 * SS)
        x, y = b
        d.ellipse(P([(x - 11, y - 4), (x + 11, y + 22)])[0] + P([(x + 11, y + 22)])[0], fill=(236, 150, 166),
                  outline=MUSCLE_D, width=2 * SS)
    for name, (x, y) in VALVE.items():
        flap(d, x, y, vertical=name in ("pulmonary", "aortic"))
    highlight(d, [(500, 470), (530, 420), (620, 405)], w=12, alpha=110)


def flap(d, x, y, vertical=False, color=(255, 255, 255)):
    for s in (-1, 1):
        if vertical:
            pts = [(x + s * 12, y - 10), (x + s * 2, y + 7), (x + s * 12, y + 10)]
        else:
            pts = [(x + s * 25, y - 6), (x + s * 3, y + 12), (x + s * 25, y + 6)]
        d.polygon(P(pts), fill=color, outline=INK)


def heart_icon(d, cx=640, cy=560, k=1.0):
    """Outside view of the heart: great vessels with the aortic branches, auricles, coronary vessels."""
    def T(pts):
        return S(pts, dx=cx - 640, dy=cy - 600, k=k)

    def tb(pts, c, e, w, shine=True):
        tube(d, T(pts), c, e, w=max(4, int(w * k)), shine=shine)
    for pts in ([(735, 275), (728, 190)], [(790, 252), (795, 172)], [(845, 262), (868, 188)]):
        tb(pts, RED, RED_D, 24)
    tb([(690, 430), (690, 310), (735, 262), (810, 248), (880, 270), (920, 340), (925, 430)], RED, RED_D, 52)
    tb([(480, 460), (480, 228)], BLUE, BLUE_D, 46)
    tb([(630, 450), (640, 340)], BLUE, BLUE_D, 50)
    tb([(640, 345), (590, 305), (530, 300)], BLUE, BLUE_D, 30)
    tb([(640, 345), (700, 300), (760, 300)], BLUE, BLUE_D, 30)
    grad_blob(d, T(HEART), MUSCLE_IN, MUSCLE_OUT, MUSCLE_D, width=max(3, int(7 * k)), n=12)
    grad_blob(d, T([(462, 440), (520, 420), (560, 445), (530, 480), (480, 485)]), (250, 196, 206), (226, 140, 158),
              MUSCLE_D, width=max(2, int(5 * k)), n=8)
    grad_blob(d, T([(800, 430), (850, 420), (885, 450), (860, 488), (812, 478)]), (250, 196, 206), (226, 140, 158),
              MUSCLE_D, width=max(2, int(5 * k)), n=8)
    for pts, c, w in (([(684, 440), (700, 560), (740, 700), (790, 850)], (200, 64, 86), 7),
                      ([(670, 440), (684, 560), (722, 700), (772, 850)], (96, 120, 196), 4),
                      ([(560, 440), (470, 560), (480, 700), (560, 790)], (200, 64, 86), 6),
                      ([(720, 600), (800, 640), (860, 700)], (200, 64, 86), 4)):
        d.line(P(spline(T(pts), closed=False, n=8)), fill=c, width=max(2, int(w * k)) * SS, joint="curve")
    highlight(d, T([(500, 520), (540, 450), (620, 425)]), w=max(4, int(16 * k)), alpha=120, blur=max(2, int(8 * k)))


def torso(d):
    T = lambda pts: S(pts, dy=110, k=0.86, cx=640, cy=540)  # noqa: E731
    pts = [(560, 70), (720, 70), (730, 150), (900, 210), (960, 330), (920, 720), (880, 1000), (400, 1000), (360, 720),
           (320, 330), (380, 210), (550, 150)]
    grad_blob(d, T(pts), (244, 249, 255), (214, 230, 248), (150, 180, 214), width=6, n=10)
    grad_blob(d, T([(470, 300), (600, 270), (620, 420), (610, 640), (520, 700), (420, 640), (410, 420)]),
              (255, 222, 228), LUNG, LUNG_D, n=8)
    grad_blob(d, T([(680, 270), (810, 300), (870, 420), (860, 640), (760, 700), (700, 640), (720, 520), (690, 420)]),
              (255, 222, 228), LUNG, LUNG_D, n=8)
    tube(d, T([(640, 150), (640, 300)]), (232, 236, 244), (170, 180, 200), w=26, smooth=False)


# ---------------------------------------------------------------- scene builder
class Scene:
    def __init__(self, sid, text_):
        self.id, self.text, self.audio = sid, text_, HERE / "audio" / f"{sid}.wav"
        self.dur = dur(self.audio)
        self.words = text_.lower().replace(",", "").replace(".", "").replace("?", "").split()
        self.items = []      # (t, layer)
        self.dyn = []        # callables(draw, t)

    def t(self, word, nth=1, offset=0.0):
        n = 0
        for i, w in enumerate(self.words):
            if w.startswith(word.lower()):
                n += 1
                if n == nth:
                    return 0.25 + (self.dur - 0.8) * i / len(self.words) + offset
        raise KeyError(f"{self.id}: {word}")

    def add(self, t, fn):
        self.items.append((t, layer(fn)))


def header(title, sub=None, color=MAROON):
    def fn(d):
        text(d, (90, 60), title, 64, color, 800)
        w = d.textlength(title, font=F(64, 800)) / SS
        d.line(P([(92, 142), (92 + w, 138)]), fill=GOLD, width=8 * SS)
        if sub:
            text(d, (92, 160), sub, 30, GRAY, 500)
    return fn


def panel_item(y, s, color=INK, dot=None, size=36, x=1250, weight=700):
    def fn(d):
        if dot:
            d.ellipse(P([(x - 34, y + 14), (x - 12, y + 36)])[0] + P([(x - 12, y + 36)])[0], fill=dot)
        text(d, (x, y), s, size, color, weight)
    return fn


def label(xy, to, s, color=INK, size=30, anchor="lm"):
    def fn(d):
        d.line(P([xy, to]), fill=color, width=3 * SS)
        x, y = to
        d.ellipse(P([(x - 6, y - 6), (x + 6, y + 6)])[0] + P([(x + 6, y + 6)])[0], fill=color)
        tx = xy[0] + (10 if anchor == "lm" else -10)
        text(d, (tx, xy[1]), s, size, color, 700, anchor)
    return fn


def glow(x, y, r=34, color=GOLD):
    def fn(d):
        d.ellipse(P([(x - r, y - r), (x + r, y + r)])[0] + P([(x + r, y + r)])[0], outline=color, width=7 * SS)
    return fn


def build():
    sc = {s["id"]: Scene(s["id"], s["text"]) for s in json.load(open(HERE / "script.json"))}
    base_diagram = lambda d: (draw_lungs_body(d), draw_vessels(d), draw_heart(d))  # noqa: E731

    s = sc["hook"]
    s.add(0, header("THE HEART", "Anatomy & how blood flows"))
    s.dyn.append(("beat_icon",))
    s.add(s.t("beats"), panel_item(330, "≈ 100,000", RED_D, size=72, weight=800))
    s.add(s.t("beats"), panel_item(430, "heartbeats every day", INK, size=34, weight=500))
    s.add(s.t("pumps"), panel_item(560, "≈ 7,000 liters", BLUE_D, size=72, weight=800))
    s.add(s.t("pumps"), panel_item(660, "of blood pumped every day", INK, size=34, weight=500))
    s.add(0, lambda d: text(d, (90, 1030), "Educational content only, not medical advice.", 24, GRAY, 500))

    s = sc["chest"]
    s.add(0, header("WHERE IS THE HEART?"))
    s.add(0, torso)
    s.add(0, lambda d: heart_icon(d, cx=692, cy=633, k=0.36))
    for i, (w, line) in enumerate([("middle", "Middle of the chest"), ("between", "Between the two lungs"),
                                   ("tilted", "Tilted slightly to the left"), ("size", "About the size of your fist"),
                                   ("cardiac", "Made of cardiac muscle")]):
        s.add(s.t(w), panel_item(300 + i * 95, line, dot=MUSCLE_D))
    s.add(s.t("lungs"), label((380, 590), (477, 590), "Lung", INK, 30, "rm"))
    s.add(s.t("tilted"), label((985, 800), (760, 745), "Heart", RED_D, 30, "lm"))

    s = sc["chambers"]
    s.add(0, header("4 CHAMBERS", "Two pumps, side by side"))
    s.add(0, lambda d: draw_heart(d, tint=False))
    s.add(s.t("septum"), lambda d: d.line(P([(666, 605), (690, 835)]), fill=GOLD, width=10 * SS))
    s.add(s.t("septum"), label((600, 900), (688, 828), "Septum", MAROON, 30, "rm"))
    s.add(s.t("atrium"), panel_item(300, "Atrium: receives blood", dot=GOLD))
    s.add(s.t("ventricle"), panel_item(380, "Ventricle: pumps blood out", dot=GOLD))
    s.add(s.t("four"), lambda d: draw_heart(d, tint=True))
    s.add(s.t("right", 1), label((300, 470), (520, 480), "Right atrium", BLUE_D, 30, "rm"))
    s.add(s.t("ventricle", 3), label((300, 700), (540, 700), "Right ventricle", BLUE_D, 30, "rm"))
    s.add(s.t("left", 1), label((985, 470), (810, 480), "Left atrium", RED_D, 30, "lm"))
    s.add(s.t("left", 2), label((985, 730), (800, 720), "Left ventricle", RED_D, 30, "lm"))
    s.add(s.t("four"), panel_item(480, "Right side: oxygen-poor blood", dot=BLUE))
    s.add(s.t("four"), panel_item(560, "Left side: oxygen-rich blood", dot=RED))

    s = sc["valves"]
    s.add(0, header("4 VALVES", "One-way doors"))
    s.add(0, lambda d: draw_heart(d))
    for i, (w, name, col, xy, side) in enumerate([
            ("tricuspid", "Tricuspid valve", BLUE_D, (300, 560), "rm"), ("pulmonary", "Pulmonary valve", BLUE_D, (500, 300), "rm"),
            ("mitral", "Mitral valve", RED_D, (1000, 600), "lm"), ("aortic", "Aortic valve", RED_D, (985, 240), "lm")]):
        key = name.split()[0].lower()
        s.add(s.t(w), glow(*VALVE[key], 24 if key in ("pulmonary", "aortic") else 34))
        s.add(s.t(w), label(xy, VALVE[key], name, col, 28, side))
        s.add(s.t(w), panel_item(300 + i * 90, name + ("  (right)" if col == BLUE_D else "  (left)"), dot=col))

    for sid, ttl, sub in (("right", "RIGHT SIDE", "Blood goes to the lungs"),
                          ("lungs", "IN THE LUNGS", "Oxygen in, carbon dioxide out"),
                          ("left", "LEFT SIDE", "Blood goes to the body"),
                          ("lubdub", "LUB - DUB", "The sound of valves closing"),
                          ("summary", "SUMMARY", None)):
        sc[sid].add(0, header(ttl, sub))
        sc[sid].add(0, base_diagram)

    s = sc["right"]
    steps = [("vena", "1  Vena cava  ->  right atrium"), ("tricuspid", "2  Tricuspid valve  ->  right ventricle"),
             ("pulmonary", "3  Pulmonary valve  ->  pulmonary artery"), ("lungs", "4  Pulmonary artery  ->  lungs")]
    for i, (w, line) in enumerate(steps):
        s.add(s.t(w), panel_item(300 + i * 85, line, BLUE_D, size=31))
    s.add(s.t("vena"), label((385, 700), (400, 700), "Inferior vena cava", BLUE_D, 26, "rm"))
    s.add(s.t("superior"), label((318, 380), (390, 345), "Superior vena cava", BLUE_D, 24, "rm"))
    s.add(s.t("artery"), label((440, 268), (636, 330), "Pulmonary artery", BLUE_D, 24, "rm"))
    s.dyn.append(("flow", 0.0, [(s.t("returns"), MARK["ra"]), (s.t("tricuspid"), MARK["rv"]),
                                (s.t("pumps"), MARK["pulm"]), (s.t("lungs"), MARK["lungs_mid"])]))

    s = sc["lungs"]
    for i, (w, line, c) in enumerate([("carbon", "CO2 out", BLUE_D), ("oxygen", "O2 in", RED_D),
                                      ("pulmonary", "Pulmonary veins  ->  left atrium", RED_D)]):
        s.add(s.t(w), panel_item(300 + i * 85, line, c, size=34))
    s.add(s.t("carbon"), lambda d: blob(d, LUNGS, (255, 150, 165), RED_D, n=10))
    s.add(s.t("pulmonary"), label((985, 330), (805, 330), "Pulmonary veins", RED_D, 26, "lm"))
    s.dyn.append(("flow", 0.0, [(0.5, MARK["lungs_mid"]), (s.t("travels"), MARK["lungs_mid"] + 120),
                                (s.t("atrium"), MARK["la"])]))

    s = sc["left"]
    for i, (w, line) in enumerate([("mitral", "1  Mitral valve  ->  left ventricle"),
                                   ("thickest", "2  Thickest wall: pumps to the whole body"),
                                   ("aortic", "3  Aortic valve  ->  aorta"), ("organ", "4  Aorta  ->  every organ")]):
        s.add(s.t(w), panel_item(300 + i * 85, line, RED_D, size=31))
    s.add(s.t("thickest"), glow(776, 720, 105, GOLD))
    s.add(s.t("aorta", 1), label((985, 260), (875, 302), "Aorta", RED_D, 28, "lm"))
    s.dyn.append(("flow", 0.0, [(0.3, MARK["la"]), (s.t("mitral"), MARK["lv"]), (s.t("aortic"), MARK["aortic"]),
                                (s.t("organ"), MARK["body"])]))

    s = sc["lubdub"]
    s.add(s.t("lub", 2), lambda d: (glow(*VALVE["tricuspid"])(d), glow(*VALVE["mitral"])(d)))
    s.add(s.t("lub", 2), panel_item(300, "LUB = tricuspid + mitral close", BLUE_D, size=32))
    s.add(s.t("lub", 2), panel_item(350, "(ventricles start to squeeze)", GRAY, size=28, weight=500))
    s.add(s.t("dub", 2), lambda d: (glow(*VALVE["pulmonary"], 26)(d), glow(*VALVE["aortic"], 26)(d)))
    s.add(s.t("dub", 2), panel_item(450, "DUB = pulmonary + aortic close", RED_D, size=32))
    s.add(s.t("dub", 2), panel_item(500, "(ventricles relax)", GRAY, size=28, weight=500))
    s.dyn.append(("flow_all",))
    s.dyn.append(("word", s.t("lub", 2), "LUB", (560, 470), BLUE_D))
    s.dyn.append(("word", s.t("dub", 2), "DUB", (690, 450), RED_D))

    s = sc["summary"]
    for i, (w, line, c) in enumerate([("right", "Right side  ->  lungs: picks up oxygen", BLUE_D),
                                      ("left", "Left side  ->  body: delivers oxygen", RED_D),
                                      ("four", "4 valves keep blood flowing one way", MAROON)]):
        s.add(s.t(w), panel_item(300 + i * 90, line, c, size=32))
    s.add(s.t("next"), panel_item(640, "NEXT VIDEO:", GOLD, size=30, weight=800))
    s.add(s.t("next"), panel_item(690, "The heart's electrical system (ECG)", INK, size=32))
    s.add(0, lambda d: text(d, (1250, 1010), "Educational content only, not medical advice.", 22, GRAY, 500))
    s.dyn.append(("flow_all",))
    return [sc[k] for k in ("hook", "chest", "chambers", "valves", "right", "lungs", "left", "lubdub", "summary")]


# ---------------------------------------------------------------- frame rendering
def render():
    scenes = build()
    beat_icon = {}
    for k in (1.0, 1.04, 1.07):
        beat_icon[k] = layer(lambda d, k=k: heart_icon(d, cx=640, cy=600, k=k * 0.95))
    word_cache = {}
    out = HERE / "heart_sample.mp4"
    total = sum(s.dur for s in scenes)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", str(HERE / "video_only.mp4")], stdin=subprocess.PIPE)
    for s in scenes:
        n = int(round(s.dur * FPS))
        items = sorted(s.items, key=lambda x: x[0])
        settled = Image.new("RGBA", (W, H), BG + (255,))
        done = 0
        for f in range(n):
            t = f / FPS
            while done < len(items) and t >= items[done][0] + 0.45:
                settled.alpha_composite(items[done][1])
                done += 1
            frame = settled.copy()
            for t0, lay in items[done:]:
                if t >= t0:
                    a = (t - t0) / 0.45
                    tmp = lay.copy()
                    tmp.putalpha(tmp.getchannel("A").point(lambda v, a=a: int(v * a)))
                    frame.alpha_composite(tmp)
            d = ImageDraw.Draw(frame)
            for spec in s.dyn:
                kind = spec[0]
                if kind == "beat_icon":
                    ph = (t % 0.86) / 0.86
                    k = 1.07 if ph < 0.08 else 1.04 if 0.18 < ph < 0.24 else 1.0
                    frame.alpha_composite(beat_icon[k])
                elif kind in ("flow", "flow_all"):
                    if kind == "flow":
                        keys = spec[2]
                        lim = keys[0][1]
                        for (ta, sa), (tb, sb) in zip(keys, keys[1:]):
                            if t >= tb:
                                lim = sb
                            elif t >= ta:
                                lim = sa + (sb - sa) * (t - ta) / max(tb - ta, 1e-3)
                                break
                        start = 0.0 if s.id == "right" else MARK["lungs_in"] if s.id == "lungs" else MARK["la"] - 60
                    else:
                        start, lim = 0.0, FLEN[-1]
                    speed, gap = 150.0, 46.0
                    off = (t * speed) % gap
                    x = start + off
                    while x <= lim:
                        px, py = at(x)
                        c = flow_color(x)
                        d.ellipse((px - 8, py - 8, px + 8, py + 8), fill=c, outline=(255, 255, 255), width=2)
                        x += gap
                elif kind == "word":
                    _, t0, w, (wx, wy), col = spec
                    if t0 <= t <= t0 + 1.4:
                        sz = int(40 + 50 * min(1, (t - t0) / 0.25))
                        key = (w, sz)
                        if key not in word_cache:
                            word_cache[key] = layer(lambda dd, w=w, sz=sz, wx=wx, wy=wy, col=col:
                                                    text(dd, (wx, wy - 120), w, sz, col, 800, "mm"))
                        frame.alpha_composite(word_cache[key])
            ff.stdin.write(frame.convert("RGB").tobytes())
        print(f"  {s.id} done ({s.dur:.1f}s)", flush=True)
    ff.stdin.close()
    ff.wait()
    with open(HERE / "audio_list.txt", "w") as fh:
        for s in scenes:
            fh.write(f"file '{s.audio}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(HERE / "audio_list.txt"),
                    "-c", "pcm_s16le", str(HERE / "voice.wav")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "video_only.mp4"), "-i", str(HERE / "voice.wav"),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)], check=True)
    print("total", round(total, 1), "->", out)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        scenes = build()
        for s in scenes:
            img = Image.new("RGBA", (W, H), BG + (255,))
            for _, lay in s.items:
                img.alpha_composite(lay)
            if any(x[0] == "beat_icon" for x in s.dyn):
                img.alpha_composite(layer(lambda d: heart_icon(d, cx=640, cy=600, k=0.95)))
            img.convert("RGB").save(HERE / f"still_{s.id}.png")
        print("stills ok")
    else:
        render()
