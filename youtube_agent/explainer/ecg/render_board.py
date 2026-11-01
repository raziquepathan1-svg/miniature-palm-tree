"""Video 1 rebuilt in Osmosis whiteboard style: every drawing is drawn live while the narrator explains,
labels are handwritten, the camera pans across a big board and zooms into details."""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "heart"))
sys.path.insert(0, str(HERE.parent / "main"))
import board as B  # noqa: E402
import lineart as LA  # noqa: E402
import render as R  # noqa: E402
from youtube_agent.doodles import Pad, PINK, YEL, RED as DRED  # noqa: E402

FPS = 30
INK = (32, 34, 44)
BLUE_T, RED_T, GOLD_T, GREEN_T, MAROON = (40, 92, 190), (196, 40, 52), (184, 120, 0), (30, 130, 80), (150, 42, 66)
WIRE, WIRE_D = (246, 178, 40), (128, 78, 0)


# ------------------------------------------------------------------ pictures
def key_white(img):
    img = img.convert("RGB")
    w, h = img.size
    for c in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        ImageDraw.floodfill(img, c, (1, 254, 1), thresh=30)
    a = np.array(img.convert("RGBA"))
    m = (a[..., 0] < 10) & (a[..., 1] > 245) & (a[..., 2] < 10)
    a[m, 3] = 0
    return Image.fromarray(a)


def heart_rgba():
    img, _ = LA.draw((0, 255, 0), arrows=False)
    a = np.array(img.convert("RGBA"))
    m = (a[..., 1] > 200) & (a[..., 0] < 90) & (a[..., 2] < 90)
    a[m, 3] = 0
    return Image.fromarray(a)


LA.BLUE, LA.RED = (122, 168, 232), (240, 116, 120)
LA.BLUE_CAP, LA.RED_CAP = (182, 208, 246), (250, 176, 178)
LA.WALL, LA.LINE = (251, 216, 206), (52, 52, 62)
HX0, HY0, HX1, HY1 = (505 + LA.DX) * 2, 25 * 2, (1196 + LA.DX) * 2, 1080 * 2
HEART_SRC = heart_rgba().crop((HX0, HY0, HX1, HY1))


def lsrc(p):  # lineart coords -> heart source pixel
    return ((p[0] + LA.DX) * 2 - HX0, p[1] * 2 - HY0)


def brain_pic():
    p = Pad(950, 760)
    p.blob(470, 360, 380, 270, PINK, 9, 0.07)
    p.line([(470, 100), (440, 220), (500, 340), (450, 470), (480, 620)], 10)
    for pts in ([(170, 260), (260, 230), (300, 300), (380, 270)], [(130, 420), (230, 390), (290, 450), (360, 420)],
                [(200, 540), (290, 520), (350, 570)], [(580, 250), (660, 220), (700, 290), (790, 270)],
                [(560, 420), (650, 400), (700, 460), (810, 430)], [(590, 560), (680, 530), (750, 580)]):
        p.line(pts, 9)
    return key_white(p.img)


def clock_pic():
    p = Pad(800, 800)
    p.oval(400, 420, 320, fill=YEL)
    p.oval(400, 420, 270, fill="white")
    for k in range(12):
        a = math.radians(k * 30)
        r0 = 225 if k % 3 else 205
        p.line([(400 + r0 * math.cos(a), 420 + r0 * math.sin(a)), (400 + 250 * math.cos(a), 420 + 250 * math.sin(a))], 9)
    p.line([(400, 420), (400, 250)], 14)
    p.line([(400, 420), (510, 480)], 14)
    p.oval(400, 420, 18, fill=DRED)
    p.rect(330, 50, 140, 50, fill=DRED, r=12)
    return key_white(p.img)


def cells_pic():
    p = Pad(900, 900)
    p.oval(450, 450, 420, fill=(255, 246, 222))
    import random
    rnd = random.Random(4)
    spots = [(450, 450), (300, 360), (600, 360), (300, 560), (600, 560), (450, 230), (450, 680), (200, 460), (700, 460)]
    for (x, y) in spots:
        p.blob(x, y, 95, 78, (250, 200, 110), 5, 0.06, rot=rnd.random() * 6)
        p.oval(x + rnd.randint(-15, 15), y + rnd.randint(-10, 10), 26, fill=(190, 120, 50))
    return key_white(p.img)


def bolt_pic():
    p = Pad(300, 420)
    p.poly([(170, 20), (60, 230), (140, 230), (100, 400), (250, 170), (165, 170), (230, 20)], fill=(255, 205, 50))
    return key_white(p.img)


def heart_icon():
    p = Pad(400, 380)
    pts = [(200 + 10.5 * 16 * math.sin(t) ** 3,
            185 - 10.5 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)))
           for t in [k * 2 * math.pi / 120 for k in range(120)]]
    p.poly(pts, (226, 70, 70))
    return key_white(p.img)


def node_pic():
    p = Pad(120, 120)
    p.oval(60, 60, 42, fill=WIRE)
    return key_white(p.img)


# ------------------------------------------------------------------ scenes / timing
class Sc:
    def __init__(self, sid, text, start):
        self.id, self.text, self.start = sid, text, start
        self.audio = HERE / "audio" / f"{sid}.wav"
        self.dur = R.dur(self.audio)
        self.words = text.lower().replace(",", "").replace(".", "").replace("?", "").split()

    def t(self, word, nth=1, off=0.0):
        n = 0
        for i, w in enumerate(self.words):
            if w.startswith(word.lower()):
                n += 1
                if n == nth:
                    return self.start + 0.25 + (self.dur - 0.8) * i / len(self.words) + off
        raise KeyError(f"{self.id}: {word}")

    @property
    def end(self):
        return self.start + self.dur


def ecg_wave(n=200):
    out = []
    for i in range(n + 1):
        x = i / n
        y = 0.0
        if 0.08 <= x <= 0.18:
            y = -0.13 * math.sin(math.pi * (x - 0.08) / 0.10)
        elif 0.26 <= x <= 0.28:
            y = 0.10 * (x - 0.26) / 0.02
        elif 0.28 < x <= 0.31:
            y = 0.10 - 1.10 * (x - 0.28) / 0.03
        elif 0.31 < x <= 0.34:
            y = -1.0 + 1.28 * (x - 0.31) / 0.03
        elif 0.34 < x <= 0.37:
            y = 0.28 - 0.28 * (x - 0.34) / 0.03
        elif 0.50 <= x <= 0.70:
            y = -0.26 * math.sin(math.pi * (x - 0.50) / 0.20)
        out.append((x, y))
    return out


WAVE = ecg_wave()


def build():
    data = json.load(open(HERE / "script.json"))
    sc, t0 = {}, 0.0
    for s in data:
        sc[s["id"]] = Sc(s["id"], s["text"], t0)
        t0 += sc[s["id"]].dur
    total = t0
    bd = B.Board(4, 2)
    add, cam = bd.add, bd.camera

    def text(s, x, y, size, color, t, anchor="l", dur=None):
        return add(B.Text(s, x, y, size * 1.2, color, t=t, dur=dur, anchor=anchor))

    def arrow(pts, t, color=INK, width=5, dur=0.5):
        return add(B.Stroke(B.smooth(pts, 8), color, width, t=t, dur=dur, arrow=True))

    def line(pts, t, color=INK, width=5, dur=0.6, closed=False):
        return add(B.Stroke(pts, color, width, t=t, dur=dur, closed=closed))

    # ---------------- page A: the heart
    heart = add(B.Picture(HEART_SRC, 620, 545, h=980, t=0.6, outline_dur=4.0, fill_dur=1.2))
    L = lambda p: heart.map(lsrc(p))          # lineart -> board
    SA, AV = L((598, 462)), L((752, 628))

    def wire(pts, t, dur):
        q = [L(p) for p in pts]
        return add(B.Stroke(B.smooth(q, 6), WIRE, 8, t=t, dur=dur, shadow=WIRE_D))

    flash_layers = {}
    for k, shape in (("RA", LA.RA), ("LA", LA.LA), ("RV", LA.RV), ("LV", LA.LV)):
        m = LA.mask_of([LA.blob(shape)])[HY0:HY1, HX0:HX1]
        a = np.zeros(m.shape + (4,), "uint8")
        a[m] = (255, 255, 255, 255)
        flash_layers[k] = Image.fromarray(a).resize(heart.img.size, Image.BILINEAR)
    flashes, rings, pulses = [], [], []
    bd.fx.append(lambda crop, ctx, t: fx_all(crop, ctx, t, heart, flash_layers, flashes, rings, pulses))

    s = sc["hook"]
    cam(0, 960, 540, 1.0, 0.1)
    text("The Heart's", 1180, 150, 74, INK, s.t("heart") + 3.0)
    text("Electrical System", 1180, 245, 74, MAROON, s.t("heart") + 3.8)
    line([(1180, 300), (1760, 296)], s.t("heart") + 5.0, WIRE, 8, 0.6)
    hook_notes = [text("≈ 100,000 beats / day", 1180, 420, 58, RED_T, s.t("hundred")),
                  add(B.Picture(bolt_pic(), 1240, 610, h=170, t=s.t("spark"), outline_dur=0.7, fill_dur=0.3)),
                  text("1 electrical spark", 1320, 590, 54, GOLD_T, s.t("spark") + 0.6),
                  text("starts every beat", 1320, 670, 54, GOLD_T, s.t("spark") + 1.4)]
    rings.append((s.t("spark") + 0.6, SA, 1.0))

    # ---------------- page B: not the brain / built-in wiring
    s = sc["why"]
    cam(s.t("unlike") - 0.3, 2880, 540, 1.0, 1.0)
    bd.erase(s.t("unlike") + 1.0, hook_notes)
    add(B.Picture(brain_pic(), 2380, 460, h=470, t=s.t("muscles"), outline_dur=1.8, fill_dur=0.5))
    text("brain", 2380, 760, 54, INK, s.t("muscles") + 2.2, "c")
    bx, by = 2380, 460
    line([(bx - 230, by - 200), (bx + 230, by + 200)], s.t("brain"), RED_T, 14, 0.4)
    line([(bx + 230, by - 200), (bx - 230, by + 200)], s.t("brain") + 0.35, RED_T, 14, 0.4)
    text("heart makes its", 2800, 330, 60, INK, s.t("makes"))
    text("OWN signals", 2800, 410, 70, RED_T, s.t("makes") + 0.9)
    text("conduction system", 2800, 600, 62, GOLD_T, s.t("conduction"))
    text("= built-in wiring", 2800, 690, 58, INK, s.t("wiring", 1))
    tw = s.t("wiring", 2)
    cam(tw - 0.6, 960, 540, 1.0, 1.0)
    for k, d_ in (("internodal", 0.8), ("his", 0.6), ("rbb", 0.8), ("lbb", 0.8), ("rpk", 0.8), ("lpk", 0.9)):
        pass
    wt = tw + 0.4
    wire([(598, 462), (650, 540), (705, 600), (752, 628)], wt, 0.9)
    wire([(752, 628), (800, 668), (866, 712)], wt + 0.9, 0.6)
    wire([(866, 712), (858, 800), (846, 890), (812, 948)], wt + 1.5, 0.7)
    wire([(866, 712), (878, 800), (894, 900), (930, 972)], wt + 1.5, 0.7)
    wire([(812, 948), (760, 962), (708, 910), (676, 830)], wt + 2.2, 0.7)
    wire([(930, 972), (995, 985), (1060, 915), (1098, 800), (1102, 700)], wt + 2.2, 0.9)
    ta, tv = s.t("atria", 1), s.t("ventricles", 1)
    why_lab = [text("1st", 150, 150, 56, BLUE_T, ta, "c"), text("atria", 150, 215, 56, BLUE_T, ta + 0.3, "c"),
               arrow([(150, 250), (230, 380), L((650, 520))], ta + 0.6, BLUE_T)]
    flashes += [("RA", ta + 0.4, 1.6), ("LA", ta + 0.4, 1.6)]
    why_lab += [text("2nd", 1180, 840, 56, RED_T, tv), text("ventricles", 1180, 910, 56, RED_T, tv + 0.3),
                arrow([(1170, 900), (1000, 880), L((1010, 820))], tv + 0.8, RED_T)]
    flashes += [("RV", tv + 0.5, 1.8), ("LV", tv + 0.5, 1.8)]

    # ---------------- SA node: zoom into the heart, then page C close-up
    s = sc["sa"]
    cam(s.start, SA[0] + 120, SA[1] + 120, 1.8, 1.2)
    bd.erase(s.start + 0.2, why_lab)
    sa_node = add(B.Picture(node_pic(), SA[0], SA[1], h=44, t=s.t("sinoatrial"), outline_dur=0.4, fill_dur=0.2))
    rings.append((s.t("sinoatrial") + 0.6, SA, 0.9))
    ra = L((650, 560))
    svc = L((650, 330))
    sa_lab = [text("SA node", SA[0] - 75, SA[1] - 30, 40, GOLD_T, s.t("sinoatrial") + 0.3, "r"),
              text("sinoatrial node", SA[0] - 75, SA[1] + 15, 24, GOLD_T, s.t("node", 1) + 0.4, "r"),
              arrow([(SA[0] - 70, SA[1] - 34), (SA[0] - 20, SA[1] - 6)], s.t("sinoatrial") + 1.2, GOLD_T, 3, 0.3),
              text("right atrium", SA[0] - 75, ra[1] + 30, 30, BLUE_T, s.t("right"), "r"),
              arrow([(SA[0] - 70, ra[1] + 26), (ra[0] - 10, ra[1] + 6)], s.t("right") + 0.8, BLUE_T, 3, 0.3),
              text("superior vena cava", SA[0] - 75, svc[1] + 10, 26, BLUE_T, s.t("superior"), "r"),
              arrow([(SA[0] - 70, svc[1] + 4), (svc[0] - 22, svc[1] + 4)], s.t("superior") + 0.8, BLUE_T, 3, 0.3)]
    tp = s.t("pacemaker")
    cam(tp - 0.5, 960, 1620, 1.0, 1.0)
    add(B.Picture(cells_pic(), 520, 1600, h=600, t=tp, outline_dur=2.2, fill_dur=0.6))
    text("pacemaker cells", 520, 1975, 54, GOLD_T, tp + 2.6, "c")
    text("natural", 1080, 1360, 70, INK, tp + 0.4)
    text("pacemaker", 1080, 1450, 80, GOLD_T, tp + 1.0)
    ts = s.t("sixty")
    add(B.Picture(heart_icon(), 1230, 1700, h=170, t=ts - 0.4, outline_dur=0.6, fill_dur=0.3))
    text("60 - 100", 1340, 1690, 70, RED_T, ts + 0.2)
    text("times / minute (at rest)", 1340, 1780, 44, INK, ts + 1.0)
    for k in range(6):
        rings.append((ts + 0.6 + k * 0.8, (1230, 1700), 0.7))

    # ---------------- atria contract
    s = sc["atria"]
    cam(s.start, 830, 560, 1.15, 1.1)
    bd.erase(s.start + 0.5, sa_lab)
    tsp = s.t("spreads")
    pulses.append(([L(p) for p in [(598, 462), (650, 540), (705, 600), (752, 628)]], tsp, 1.0))
    rings.append((tsp, SA, 1.4))
    flashes += [("RA", tsp + 0.2, 2.6), ("LA", tsp + 0.6, 2.2)]
    tc = s.t("contract")
    atria_lab = [text("signal spreads", 1060, 400, 46, GOLD_T, tsp), text("like a wave", 1060, 460, 46, GOLD_T, tsp + 0.7),
                 text("atria contract", 1060, 590, 52, BLUE_T, tc - 0.2),
                 arrow([(1120, 630), (1120, 720)], s.t("top"), BLUE_T, 5, 0.4),
                 text("top up the ventricles", 1060, 790, 44, RED_T, s.t("top") + 0.3)]
    flashes.append(("RA", tc, 1.4))
    flashes.append(("LA", tc, 1.4))

    # ---------------- AV node + page D (delay)
    s = sc["av"]
    cam(s.start, AV[0] + 60, AV[1], 1.7, 1.0)
    bd.erase(s.start + 0.3, atria_lab)
    pulses.append(([L(p) for p in [(598, 462), (650, 540), (705, 600), (752, 628)]], s.t("signal", 1), 1.0))
    tav = s.t("atrioventricular")
    add(B.Picture(node_pic(), AV[0], AV[1], h=44, t=tav, outline_dur=0.4, fill_dur=0.2))
    av_lab = [text("AV node", 300, AV[1] - 60, 40, GOLD_T, tav + 0.3, "r"),
              text("atrioventricular node", 300, AV[1] - 15, 22, GOLD_T, tav + 1.2, "r"),
              arrow([(300, AV[1] - 62), (AV[0] - 60, AV[1] - 30), (AV[0] - 18, AV[1] - 6)], tav + 0.9, GOLD_T, 3, 0.4),
              text("between atria", 300, AV[1] + 60, 28, INK, s.t("sits"), "r"),
              text("& ventricles", 300, AV[1] + 100, 28, INK, s.t("sits") + 0.6, "r")]
    td = s.t("delayed")
    for k in range(5):
        rings.append((td - 0.8 + k * 0.45, AV, 0.45))
    cam(td + 0.6, 2880, 1620, 1.0, 1.0)
    add(B.Picture(clock_pic(), 2350, 1560, h=480, t=td + 1.0, outline_dur=1.8, fill_dur=0.4))
    text("short delay", 2350, 1900, 62, GOLD_T, td + 2.6, "c")
    te = s.t("emptying")
    text("atria finish", 2780, 1380, 56, BLUE_T, te - 0.4)
    text("emptying", 2780, 1450, 56, BLUE_T, te + 0.3)
    arrow([(2900, 1490), (2900, 1600)], te + 1.0, INK, 5, 0.4)
    text("ventricles fill up", 2780, 1660, 56, RED_T, s.t("full") - 0.3)
    arrow([(2900, 1700), (2900, 1790)], s.t("squeeze") - 0.2, INK, 5, 0.3)
    text("then they squeeze", 2780, 1850, 56, RED_T, s.t("squeeze"))

    # ---------------- His / branches / Purkinje (zoom on ventricles)
    s = sc["his"]
    vc = L((860, 800))
    cam(s.start, vc[0] + 120, vc[1], 1.45, 1.1)
    his_pts = [(752, 628), (800, 668), (866, 712)]
    tr = s.t("rushes")
    pulses.append(([L(p) for p in his_pts], tr, 1.2))
    bd.erase(s.start + 0.3, av_lab)
    text("bundle of His", 990, 560, 44, GOLD_T, s.t("bundle", 1))
    arrow([(985, 555), (800, 560), L((805, 668))], s.t("bundle", 1) + 0.8, GOLD_T, 3, 0.5)
    text("right & left", 990, 690, 42, GOLD_T, s.t("branches") - 0.4)
    text("bundle branches", 990, 745, 42, GOLD_T, s.t("branches") + 0.3)
    arrow([(985, 735), L((880, 800))], s.t("branches") + 1.0, GOLD_T, 3, 0.4)
    text("septum", 990, 860, 40, MAROON, s.t("septum"))
    arrow([(985, 855), L((868, 880))], s.t("septum") + 0.5, MAROON, 3, 0.4)
    tpk = s.t("purkinje")
    pk = L((1080, 880))
    text("Purkinje fibers", 990, 960, 44, GOLD_T, tpk + 0.3)
    arrow([(985, 960), (pk[0] + 10, pk[1] + 10)], tpk + 1.2, GOLD_T, 3, 0.3)
    route_r = [L(p) for p in his_pts + [(858, 800), (846, 890), (812, 948), (760, 962), (708, 910), (676, 830)]]
    route_l = [L(p) for p in his_pts + [(878, 800), (894, 900), (930, 972), (995, 985), (1060, 915), (1098, 800), (1102, 700)]]
    pulses += [(route_r, tpk - 0.4, 2.2), (route_l, tpk - 0.4, 2.2)]
    tco = s.t("contract")
    flashes += [("RV", tco, 2.4), ("LV", tco, 2.4)]
    text("contract together!", 990, 1045, 44, RED_T, tco + 0.2)
    for k in range(4):
        tb = s.t("lungs") + k * 0.9
        pulses += [(route_r, tb, 0.5), (route_l, tb, 0.5)]
        flashes += [("RV", tb + 0.35, 0.5), ("LV", tb + 0.35, 0.5)]

    # ---------------- page E: backup pacemakers
    s = sc["backup"]
    cam(s.start, 4800, 540, 1.0, 1.1)
    text("Backup pacemakers", 4800, 150, 78, INK, s.start + 0.8, "c")
    line([(4430, 205), (5170, 200)], s.start + 2.0, WIRE, 8, 0.6)
    rows = [("SA node", "60 - 100 / min", 360, s.start + 1.2), ("AV node", "40 - 60 / min", 560, s.t("take")),
            ("ventricles", "20 - 40 / min", 760, s.t("twenty"))]
    for name, rate, y, tt in rows:
        add(B.Picture(node_pic() if name != "ventricles" else heart_icon(), 4140, y, h=70 if name != "ventricles" else 90,
                      t=tt, outline_dur=0.4, fill_dur=0.2))
        text(name, 4220, y, 62, GOLD_T if name != "ventricles" else RED_T, tt + 0.3)
        text(rate, 4880, y, 62, INK, tt + 0.9)
    tf = s.t("fails")
    line([(4110, 330), (5320, 390)], tf, RED_T, 10, 0.5)
    text("fails!", 5380, 360, 54, RED_T, tf + 0.4)
    text("slower... but blood keeps moving", 4800, 960, 54, GREEN_T, s.t("slower"), "c")

    # ---------------- page F: ECG
    s = sc["ecg"]
    cam(s.start, 4800, 1620, 1.0, 1.1)
    gx0, gx1, gy0, gy1 = 4000, 5600, 1300, 1800
    tg = s.start + 0.3
    for i, x in enumerate(range(gx0, gx1 + 1, 50)):
        add(B.Stroke([(x, gy0), (x, gy1)], (246, 200, 205), 2 if i % 5 else 4, t=tg + i * 0.012, dur=0.25))
    for i, y in enumerate(range(gy0, gy1 + 1, 50)):
        add(B.Stroke([(gx0, y), (gx1, y)], (246, 200, 205), 2 if i % 5 else 4, t=tg + i * 0.02, dur=0.3))
    text("ECG", 4000, 1210, 80, INK, s.t("electrocardiogram") - 0.6)
    text("= electrocardiogram", 4180, 1210, 54, INK, s.t("electrocardiogram"))
    base, A = 1640, 300
    pts = [(gx0 + 40 + x * (gx1 - gx0 - 80), base + y * A) for x, y in WAVE]

    def seg(a, b):
        return [p for (x, y), p in zip(WAVE, pts) if a <= x <= b]
    tP, tQ, tT = s.t("wave", 1), s.t("complex"), s.t("wave", 2)
    add(B.Stroke(seg(0, 0.08), INK, 6, t=s.t("electrocardiogram") + 0.6, dur=0.6))
    add(B.Stroke(seg(0.08, 0.24), INK, 6, t=tP - 0.3, dur=0.9))
    add(B.Stroke(seg(0.24, 0.44), INK, 6, t=tQ - 0.4, dur=0.8))
    add(B.Stroke(seg(0.44, 1.0), INK, 6, t=tT - 0.3, dur=1.4))
    pP = pts[26]
    pR = pts[62]
    pT = pts[120]
    text("P", pP[0], pP[1] - 70, 64, BLUE_T, tP + 0.6, "c")
    text("QRS", pR[0], pR[1] - 50, 64, RED_T, tQ + 0.4, "c")
    text("T", pT[0], pT[1] - 80, 64, MAROON, tT + 0.8, "c")
    text("P wave = atria activated", 4000, 1900, 50, BLUE_T, tP + 1.0)
    text("QRS = ventricles activated", 4000, 1975, 50, RED_T, tQ + 0.9)
    text("T wave = ventricles recover", 4000, 2050, 50, MAROON, tT + 1.2)

    # ---------------- page G: nerves change the pace
    s = sc["nerves"]
    cam(s.start, 6720, 540, 1.0, 1.1)
    text("Changing the pace", 6720, 140, 78, INK, s.start + 0.6, "c")

    def strip(x0, x1, y, P, t, dur, color):
        out = []
        n = int((x1 - x0) / P)
        for k in range(n):
            for x, yy in WAVE[::4]:
                out.append((x0 + (k + x) * P, y + yy * 110))
        return add(B.Stroke(out, color, 5, t=t, dur=dur))
    te = s.t("exercise")
    text("exercise / stress", 5900, 320, 60, RED_T, te)
    text("sympathetic nerves  ->  FASTER", 5900, 395, 46, INK, s.t("sympathetic"))
    strip(5900, 7560, 520, 140, s.t("sympathetic") + 0.6, 2.0, RED_T)
    trs = s.t("rest")
    text("rest", 5900, 680, 60, BLUE_T, trs)
    text("vagus nerve  ->  slower", 5900, 755, 46, INK, s.t("vagus"))
    strip(5900, 7560, 890, 330, s.t("vagus") + 0.5, 2.2, BLUE_T)

    # ---------------- page H: summary flow chart, then zoom out over the whole board
    s = sc["summary"]
    cam(s.start, 6720, 1620, 1.0, 1.1)
    text("Summary", 6720, 1210, 78, INK, s.start + 0.3, "c")
    steps = [("node", 1, "SA node", GOLD_T), ("atria", 1, "atria", BLUE_T), ("node", 2, "AV node", GOLD_T),
             ("bundle", 1, "bundle of His", GOLD_T), ("branches", 1, "bundle branches", GOLD_T),
             ("purkinje", 1, "Purkinje fibers", GOLD_T), ("ventricles", 1, "ventricles", RED_T)]
    pos = [(5890, 1420), (6380, 1420), (6870, 1420), (7360, 1420), (7360, 1700), (6870, 1700), (6380, 1700)]
    for i, ((w, n, name, col), (x, y)) in enumerate(zip(steps, pos)):
        tt = s.t(w, n) - 0.2
        bw, bh = 220, 70
        box = [(x - bw, y - bh), (x + bw, y - bh), (x + bw, y + bh), (x - bw, y + bh)]
        add(B.Stroke(box, col, 5, t=tt, dur=0.45, closed=True))
        text(name, x, y + 10, 46 if len(name) < 12 else 40, col, tt + 0.3, "c", dur=0.5)
        if i:
            px_, py_ = pos[i - 1]
            if py_ == y:
                a = [(px_ + bw * (1 if x > px_ else -1) + 8 * (1 if x > px_ else -1), y),
                     (x - bw * (1 if x > px_ else -1) - 8 * (1 if x > px_ else -1), y)]
            else:
                a = [(x, py_ + bh + 8), (x, y - bh - 8)]
            add(B.Stroke(a, INK, 5, t=tt - 0.25, dur=0.25, arrow=True))
    tsp = s.t("spark")
    cam(tsp, 3840, 1080, 0.25, 2.2)
    tn = s.t("next")
    cam(tn - 0.3, 6720, 1620, 1.0, 1.2)
    text("Next video:", 6000, 1960, 56, INK, tn + 0.6)
    text("What happens in a heart attack?", 6000, 2040, 60, RED_T, tn + 1.2)
    bd.total = total
    return bd, sc


def fx_all(crop, ctx, t, heart, flash_layers, flashes, rings, pulses):
    inten = {}
    for k, t0, d in flashes:
        if t0 <= t <= t0 + d:
            x = (t - t0) / d
            inten[k] = max(inten.get(k, 0), min(1, x / 0.2) * min(1, (1 - x) / 0.35))
    for k, a in inten.items():
        lay = flash_layers[k].copy()
        lay.putalpha(lay.getchannel("A").point(lambda v, a=a: int(v * 0.5 * a)))
        B.paste_clipped(crop, lay, (heart.px - ctx.box[0], heart.py - ctx.box[1]))
    d = ImageDraw.Draw(crop)
    for t0, p, d_ in rings:
        if t0 <= t <= t0 + d_:
            x_ = (t - t0) / d_
            cx, cy = ctx.px(p)
            r = (14 + 70 * x_) * B.BS
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=R.mix((255, 255, 255), WIRE, 1 - x_), width=int(6 * B.BS))
    for pts, t0, d_ in pulses:
        if t0 <= t <= t0 + d_:
            p = B.partial_pts(pts, (t - t0) / d_)[-1]
            cx, cy = ctx.px(p)
            r = 13 * B.BS
            d.ellipse((cx - 1.8 * r, cy - 1.8 * r, cx + 1.8 * r, cy + 1.8 * r), outline=WIRE, width=int(4 * B.BS))
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 247, 205), outline=WIRE_D, width=int(3 * B.BS))


def render(out_name="heart_electrical_board.mp4", t_from=0.0, t_to=None, video_only=False):
    import render_ecg as RE  # intro frames + audio
    bd, sc = build()
    t_to = t_to or bd.total
    vid = HERE / ("board_video_only.mp4" if not video_only else out_name)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", str(vid)], stdin=subprocess.PIPE)
    if t_from == 0 and not video_only:
        for f in range(int(round(RE.INTRO_DUR * FPS))):
            ff.stdin.write(RE.intro_frame(f / FPS).tobytes())
    n0, n1 = int(t_from * FPS), int(t_to * FPS)
    for f in range(n0, n1):
        ff.stdin.write(bd.frame(f / FPS).tobytes())
        if f % 300 == 0:
            print(f"  t={f / FPS:.0f}s", flush=True)
    ff.stdin.close()
    ff.wait()
    if video_only:
        return
    RE.intro_audio(HERE / "audio_intro.wav")
    with open(HERE / "audio_list_b.txt", "w") as fh:
        fh.write(f"file '{HERE / 'audio_intro.wav'}'\n")
        for s in sc.values():
            fh.write(f"file '{s.audio}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(HERE / "audio_list_b.txt"),
                    "-c", "pcm_s16le", str(HERE / "voice_b.wav")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(HERE / "voice_b.wav"), "-i",
                    str(HERE.parent / "clips" / "clip1.mp4"), "-filter_complex",
                    "[2:v]trim=0:3.4,setpts=PTS-STARTPTS,fps=30,scale=1920:1080,format=yuva420p,"
                    "fade=t=in:st=0:d=0.3:alpha=1,fade=t=out:st=3.0:d=0.4:alpha=1,setpts=PTS+3.6/TB[c];"
                    "[0:v][c]overlay=eof_action=pass[v]", "-map", "[v]", "-map", "1:a", "-c:v", "libx264",
                    "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", str(HERE / out_name)], check=True)
    print("done ->", HERE / out_name)


def stills(times):
    bd, sc = build()
    for t in sorted(times):
        bd.frame(t).save(HERE / f"b_{t:06.1f}.png")
    print("ok", round(bd.total, 1))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        stills([float(x) for x in sys.argv[2:]])
    else:
        render()
