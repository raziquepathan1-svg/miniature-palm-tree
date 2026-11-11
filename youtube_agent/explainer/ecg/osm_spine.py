"""Nervous system series: The Spinal Cord & Reflexes (owner-approved 11 Nov 2026) + 2 story Shorts.

    python3 osm_spine.py [stills]          # full video -> final_spine.mp4
    python3 osm_spine.py short 1|2 [stills]  # story Short -> spine_short1.mp4 / spine_short2.mp4
Env: EP_DIR (default ../spine), OUT_DIR.
"""
import json
import math
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "spine")))
OUT = Path(os.environ.get("OUT_DIR", str(HERE)))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_preview as OP  # noqa: E402
import osm_brain as OB  # noqa: E402
import osm_neuron as NU  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OB.PINK, OB.LILAC, OB.CREAM, OB.MINT, OB.SKY
PW, PH = 1920, 1080
sv = OB.sv
VIOLET = (140, 90, 220)
SHORT_TITLES = {1: "The Knee Tap Mystery", 2: "The Needle in Your Back"}
SHORT_Q = {1: "So what is the spinal cord really doing?", 2: "So what is it called?"}


# ----------------------------------------------------------------------------- pictures
def _rect(cx, cy, w, h, ang):
    a = math.radians(ang)
    pts = []
    for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        pts.append((cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)))
    return pts


def knee_pic(kick=False):
    S, W, H = 3, 760, 640
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    skin, ol = (248, 214, 190), (170, 110, 90)
    d.rounded_rectangle((40 * S, 190 * S, 450 * S, 330 * S), radius=60 * S, fill=skin, outline=ol, width=5 * S)   # thigh
    d.ellipse((380 * S, 190 * S, 500 * S, 340 * S), fill=skin, outline=ol, width=5 * S)   # knee
    if not kick:
        d.polygon([(p[0] * S, p[1] * S) for p in _rect(440, 460, 110, 280, 0)], fill=skin, outline=ol)
        d.ellipse((400 * S, 560 * S, 540 * S, 620 * S), fill=skin, outline=ol, width=5 * S)
    else:
        d.polygon([(p[0] * S, p[1] * S) for p in _rect(580, 360, 110, 280, -62)], fill=skin, outline=ol)
        d.ellipse((650 * S, 280 * S, 740 * S, 400 * S), fill=skin, outline=ol, width=5 * S)
        for k in range(3):   # motion marks
            d.arc((520 * S, (250 + k * 40) * S, 700 * S, (430 + k * 40) * S), 280, 340, fill=(235, 90, 60), width=6 * S)
    d.line([(690 * S, 40 * S), (500 * S, 215 * S)], fill=(120, 80, 50), width=14 * S)   # reflex hammer
    d.ellipse((440 * S, 190 * S, 520 * S, 250 * S), fill=(140, 140, 150), outline=(70, 70, 80), width=4 * S)
    return im.resize((W, H), Image.LANCZOS)


SPINE_H = 1000
SPINE_REG = [("C", 7, 26, 90, (150, 190, 240)), ("T", 12, 35, 112, (150, 215, 170)), ("L", 5, 44, 134, (245, 215, 120)), ("S", 1, 80, 120, (245, 170, 190)), ("Cx", 1, 22, 50, (200, 200, 205))]


def spine_layout():
    y, out = 6, []
    for name, n, hgt, w, col in SPINE_REG:
        for i in range(n):
            out.append((name, i, y, hgt, w, col))
            y += hgt + 3
    return out


def spine_marks():
    lay = spine_layout()
    ends = {}
    for name, i, y, h, w, col in lay:
        ends[(name, i)] = (y, y + h)
    return {"C": (lay[0][2], ends[("C", 6)][1]), "T": (ends[("T", 0)][0], ends[("T", 11)][1]), "L": (ends[("L", 0)][0], ends[("L", 4)][1]),
            "S": (ends[("S", 0)][0], ends[("S", 0)][1]), "L1end": ends[("L", 0)][1], "L2end": ends[("L", 1)][1], "bottom": ends[("Cx", 0)][1]}


def spine_pic():
    S, W = 3, 460
    H = SPINE_H
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = W // 2
    for name, i, y, h, w, col in spine_layout():
        d.rounded_rectangle(((cx - w / 2) * S, y * S, (cx + w / 2) * S, (y + h) * S), radius=12 * S, fill=col, outline=(110, 100, 110), width=3 * S)
        if name != "Cx":
            d.rounded_rectangle(((cx - 12) * S, (y + 3) * S, (cx + 12) * S, (y + h - 3) * S), radius=6 * S, fill=(255, 255, 255))
    return im.resize((W, H), Image.LANCZOS)


def cord_overlay():
    S, W, H = 3, 460, SPINE_H
    m = spine_marks()
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = W // 2
    d.rounded_rectangle(((cx - 9) * S, 0, (cx + 9) * S, (m["L1end"] + 18) * S), radius=9 * S, fill=VIOLET + (255,), outline=(80, 40, 150), width=2 * S)
    return im.resize((W, H), Image.LANCZOS)


def cauda_overlay():
    S, W, H = 3, 460, SPINE_H
    m = spine_marks()
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = W // 2
    y0 = m["L1end"] + 12
    for k in range(-5, 6):
        pts = [((cx + k * 0.6) * S, y0 * S), ((cx + k * 1.6) * S, (y0 + 90) * S), ((cx + k * 1.2) * S, (m["S"][0] + 10) * S)]
        d.line(pts, fill=(200, 120, 230, 255), width=3 * S)
    return im.resize((W, H), Image.LANCZOS)


def _butterfly(d, cx, cy, S, scale=1.0, fill=(190, 175, 195), outline=(110, 90, 120)):
    def el(x, y, rx, ry, ang=0):
        pts = []
        for i in range(60):
            a = 2 * math.pi * i / 60
            px, py = rx * math.cos(a), ry * math.sin(a)
            r = math.radians(ang)
            pts.append(((cx + (x + px * math.cos(r) - py * math.sin(r)) * scale) * S, (cy + (y + px * math.sin(r) + py * math.cos(r)) * scale) * S))
        return pts
    for spec in ((0, 0, 100, 48, 0), (-95, -95, 36, 100, -25), (95, -95, 36, 100, 25), (-110, 85, 62, 70, 20), (110, 85, 62, 70, -20)):
        d.polygon(el(*spec), fill=fill)
    for spec in ((0, 0, 100, 48, 0), (-95, -95, 36, 100, -25), (95, -95, 36, 100, 25), (-110, 85, 62, 70, 20), (110, 85, 62, 70, -20)):
        pts = el(*spec)
        d.line(pts + [pts[0]], fill=outline, width=int(3 * S))
    for spec in ((0, 0, 100, 48, 0), (-95, -95, 36, 100, -25), (95, -95, 36, 100, 25), (-110, 85, 62, 70, 20), (110, 85, 62, 70, -20)):
        d.polygon(el(*spec), fill=fill)
    r = 10 * scale
    d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=(255, 255, 255), outline=outline, width=2 * S)


def cross_pic(roots=False):
    S, W, H = 3, 900, 720
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = 400, 360
    d.ellipse(((cx - 330) * S, (cy - 290) * S, (cx + 330) * S, (cy + 290) * S), fill=(253, 251, 247), outline=(150, 130, 150), width=5 * S)
    _butterfly(d, cx, cy, S, 1.45)
    if roots:
        d.line([(560 * S, 190 * S), (640 * S, 110 * S), (760 * S, 170 * S), (840 * S, 330 * S)], fill=(60, 110, 200), width=10 * S)   # dorsal root
        d.ellipse((605 * S, 80 * S, 675 * S, 140 * S), fill=(120, 160, 235), outline=(40, 80, 160), width=4 * S)   # dorsal root ganglion
        d.line([(560 * S, 560 * S), (690 * S, 620 * S), (790 * S, 500 * S), (840 * S, 330 * S)], fill=(210, 60, 70), width=10 * S)   # ventral root
        d.line([(840 * S, 330 * S), (895 * S, 330 * S)], fill=(150, 90, 190), width=14 * S)   # spinal nerve
    return im.resize((W, H), Image.LANCZOS)


def protect_pic():
    S, W, H = 3, 760, 760
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = 380, 330

    def circ(r, fill=None, outline=None, w=3):
        d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=fill, outline=outline, width=w * S)
    d.polygon([(p[0] * S, p[1] * S) for p in _rect(cx, cy + 300, 200, 150, 0)], fill=(240, 231, 212), outline=(120, 100, 80))   # spinous process
    d.ellipse(((cx - 250) * S, (cy + 120) * S, (cx + 250) * S, (cy + 380) * S), fill=(240, 231, 212), outline=(120, 100, 80), width=5 * S)   # body area
    circ(250, (240, 231, 212), (120, 100, 80), 6)
    circ(200, (255, 255, 255), (150, 130, 110), 3)
    circ(190, None, (150, 90, 190), 5)       # dura
    circ(172, (200, 226, 250), (190, 150, 40), 4)   # arachnoid + CSF
    circ(140, (200, 226, 250), (200, 70, 90), 3)    # pia
    circ(132, (253, 251, 247), (110, 90, 120), 3)
    _butterfly(d, cx, cy, S, 0.55)
    return im.resize((W, H), Image.LANCZOS)


def tint(level):
    """red tint on the body silhouette below a level (0..1 from the top)."""
    base = sv("Male-silhouette")
    a = base.getchannel("A")
    mask = Image.new("L", base.size, 0)
    ImageDraw.Draw(mask).rectangle((0, int(level * base.height), base.width, base.height), fill=150)
    mask = ImageChops.multiply(mask, a)
    ov = Image.new("RGBA", base.size, (220, 50, 60, 0))
    ov.putalpha(mask)
    return ov


def cord_on_body():
    base = sv("Male-silhouette")
    S = 2
    ov = Image.new("RGBA", (base.width * S, base.height * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    cx = base.width // 2
    d.rounded_rectangle(((cx - 7) * S, int(0.17 * base.height) * S, (cx + 7) * S, int(0.49 * base.height) * S), radius=7 * S, fill=VIOLET + (255,), outline=(80, 40, 150), width=2 * S)
    return ov.resize(base.size, Image.LANCZOS)


# ----------------------------------------------------------------------------- scenes
def load(d):
    return NU.load(d)


def build():
    sc, t0 = load(EP)
    bd = B.Board(3, 2)
    pops, glows = [], []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    cam = bd.camera
    A, Bc, C = (960, 540), (PW + 960, 540), (2 * PW + 960, 540)
    D, E, Fp = (960, PH + 540), (PW + 960, PH + 540), (2 * PW + 960, PH + 540)
    cam(0, *A, 1.0, 0.1)
    brain = OB.brain_img()

    def L(p0, p1, t, col=MAROON, w=4):
        mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - 18)
        return lead([p0, mid, p1], t, col, w, 0.5)

    # ---------------- STORY (A)
    s = sc["story"]
    k1 = pop(knee_pic(False), 520, 560, h=760, t=0.3)
    tk = s.t("kicks")
    k2 = pop(knee_pic(True), 520, 560, h=760, t=tk - 0.1)
    bd.erase(tk - 0.1, [k1])
    st = [k1, k2, text("a tap on the knee", 1400, 150, 66, MAROON, s.start + 0.4, "c"), text("the leg kicks!", 1400, 300, 90, RED_T, tk, "c"),
          text("you did not decide", 1400, 450, 60, PURPLE, s.t("decide"), "c"), text("WHO gave the order?", 1400, 640, 84, GOLD_T, s.t("who"), "c"),
          text("let's follow the signal", 1400, 820, 54, BLUE_T, s.t("follow") - 0.6, "c")]

    # ---------------- OVERVIEW (B)
    s = sc["overview"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, st)
    X = PW
    sil = pop(sv("Male-silhouette"), X + 560, 560, h=960, t=s.start + 0.3)
    cb = pop(cord_on_body(), X + 560, 560, h=960, t=s.t("spinal") - 0.2)
    ov = [sil, cb, text("spinal cord", X + 1250, 330, 90, PURPLE, s.t("spinal"), "c"), L((X + 1020, 330), sil.map((345, 400)), s.t("spinal") + 0.3, PURPLE),
          text("about 45 cm long", X + 1250, 470, 64, GOLD_T, s.t("45"), "c"), text("as thick as your finger", X + 1250, 565, 56, MAROON, s.t("thick"), "c"),
          text("brain", X + 1250, 120, 64, RED_T, s.t("brain"), "c"), L((X + 1130, 120), sil.map((340, 70)), s.t("brain") + 0.2, RED_T),
          text("reaches almost", X + 1250, 760, 54, BLUE_T, s.t("whole") - 1.2, "c"), text("the whole body", X + 1250, 830, 54, BLUE_T, s.t("whole") - 0.8, "c")]

    # ---------------- PROTECT (C)
    s = sc["protect"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ov)
    X = 2 * PW
    pp = pop(protect_pic(), X + 520, 540, h=900, t=s.start + 0.3)
    k = 900 / 760

    def pt(r, ang):
        a = math.radians(ang)
        return (X + 520 - 380 * k + (380 + r * math.cos(a)) * k, 540 - 450 + (330 + r * math.sin(a)) * k)
    tb, tm, tc = s.t("bony"), s.t("membranes"), s.t("cerebrospinal") - 0.3
    pr = [pp, text("bony tunnel", X + 1380, 160, 70, GOLD_T, tb, "c"), text("= vertebral column", X + 1380, 235, 46, MAROON, tb + 0.7, "c"), L((X + 1180, 160), pt(225, -40), tb + 0.3, GOLD_T),
          text("3 membranes", X + 1380, 420, 70, PURPLE, tm - 0.4, "c"), text("= meninges", X + 1380, 495, 46, MAROON, tm + 0.3, "c"), L((X + 1180, 420), pt(186, -15), tm, PURPLE),
          text("cerebrospinal fluid", X + 1340, 690, 54, BLUE_T, tc - 1.2, "c"), text("a liquid cushion", X + 1340, 765, 44, MAROON, tc - 0.5, "c"), L((X + 1180, 690), pt(156, 15), tc + 0.3, BLUE_T)]

    # ---------------- REGIONS (D)
    s = sc["regions"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, pr)
    Y = PH
    sp = pop(spine_pic(), 380, Y + 540, h=980, t=s.start + 0.3)
    m = spine_marks()
    ks = 980 / SPINE_H
    rg = [sp]
    for key, nm, desc, col, n in (("C", "cervical", "neck", BLUE_T, "8 pairs"), ("T", "thoracic", "chest", GREEN_T, "12 pairs"), ("L", "lumbar", "lower back", GOLD_T, "5 pairs"), ("S", "sacral", "bottom", RED_T, "5 + 1 pairs")):
        tt = s.t(nm)
        ymid = Y + 540 - 490 + (m[key][0] + m[key][1]) / 2 * ks
        yy = {"C": Y + 140, "T": Y + 380, "L": Y + 620, "S": Y + 850}[key]
        rg += [text(nm, 820, yy, 70, col, tt, "l"), text(f"{desc}  ({n})", 820, yy + 85, 42, MAROON, tt + 0.5, "l"), L((810, yy - 15), (380 + 40, ymid), tt + 0.2, col)]
    tth = s.t("thirty")
    rg += [panel(1380, Y + 70, 1880, Y + 320, CREAM, tth - 0.3), text("31 pairs", 1630, Y + 170, 80, PURPLE, tth, "c"), text("of spinal nerves", 1630, Y + 270, 40, MAROON, tth + 0.5, "c")]

    # ---------------- HORSETAIL (E)
    s = sc["horsetail"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, rg)
    X = PW
    sp2 = pop(spine_pic(), X + 380, Y + 540, h=980, t=s.start + 0.3)
    co = pop(cord_overlay(), X + 380, Y + 540, h=980, t=s.t("spinal") - 0.2)
    ca = pop(cauda_overlay(), X + 380, Y + 540, h=980, t=s.t("loose") - 0.3)
    yl1 = Y + 540 - 490 + m["L1end"] * ks
    he = [sp2, co, ca, text("here is a surprise!", X + 1300, Y + 120, 70, RED_T, s.t("surprise"), "c"),
          text("the cord ends at L1 - L2", X + 1300, Y + 290, 66, PURPLE, s.t("ends"), "c"), L((X + 940, Y + 290), (X + 380 + 12, yl1), s.t("ends") + 0.3, PURPLE),
          text("much higher than the spine", X + 1300, Y + 400, 50, MAROON, s.t("higher"), "c"),
          text("cauda equina", X + 1300, Y + 650, 80, GOLD_T, s.t("cauda") - 0.4, "c"), text("= horse's tail", X + 1300, Y + 770, 56, MAROON, s.t("horses") - 0.2, "c"),
          L((X + 960, Y + 650), (X + 380, Y + 540 - 490 + (m["L1end"] + 100) * ks), s.t("cauda") - 0.1, GOLD_T)]

    # ---------------- CROSS (F)
    s = sc["cross"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, he)
    X = 2 * PW
    cp = pop(cross_pic(), X + 700, Y + 540, h=960, t=s.start + 0.3)
    kc = 960 / 720
    cr = [cp, text("a butterfly shape", X + 1500, Y + 140, 66, PURPLE, s.t("butterfly"), "c"),
          text("GRAY matter", X + 1500, Y + 430, 70, (110, 100, 120), s.t("gray"), "c"), text("= nerve cell bodies", X + 1500, Y + 500, 44, MAROON, s.t("gray") + 0.6, "c"),
          L((X + 1280, Y + 430), cp.map((470, 340)), s.t("gray") + 0.3, (110, 100, 120)),
          text("WHITE matter", X + 1500, Y + 700, 70, BLUE_T, s.t("white"), "c"), text("= cables up and down", X + 1500, Y + 770, 44, MAROON, s.t("white") + 0.6, "c"),
          L((X + 1280, Y + 700), cp.map((690, 480)), s.t("white") + 0.3, BLUE_T)]

    # ---------------- ROOTS (A)
    s = sc["roots"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, cr)
    rp = pop(cross_pic(True), 640, 560, h=960, t=s.start + 0.3)
    rt = [rp, text("spinal nerve", 1350, 160, 60, PURPLE, s.t("spinal") - 0.2, "c"),
          text("DORSAL root", 1400, 330, 70, BLUE_T, s.t("dorsal"), "c"), text("sensory signals IN", 1400, 400, 46, MAROON, s.t("sensory"), "c"), L((1180, 330), rp.map((640, 110)), s.t("dorsal") + 0.3, BLUE_T),
          text("VENTRAL root", 1400, 600, 70, RED_T, s.t("ventral"), "c"), text("motor commands OUT", 1400, 670, 46, MAROON, s.t("motor"), "c"), L((1180, 600), rp.map((700, 620)), s.t("ventral") + 0.3, RED_T),
          panel(1130, 810, 1860, 950, CREAM, s.t("means") - 0.9), text("dorsal = back, ventral = front", 1495, 895, 46, GOLD_T, s.t("means") - 0.6, "c")]

    # ---------------- TRACTS (B)
    s = sc["tracts"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, rt)
    X = PW
    tr = [pop(brain, X + 960, 190, h=280, t=s.start + 0.3), panel(X + 900, 350, X + 1020, 800, LILAC, s.start + 0.6), text("spinal cord", X + 960, 880, 56, PURPLE, s.start + 0.8, "c"),
          lead([(X + 925, 780), (X + 925, 380)], s.t("ascending"), BLUE_T, 12, 0.9, arrow=True), lead([(X + 995, 380), (X + 995, 780)], s.t("descending"), RED_T, 12, 0.9, arrow=True),
          text("ASCENDING", X + 830, 500, 64, BLUE_T, s.t("ascending"), "r"), text("sensations up", X + 830, 570, 46, MAROON, s.t("sensations"), "r"), text("to the brain", X + 830, 645, 46, MAROON, s.t("sensations") + 0.5, "r"),
          text("DESCENDING", X + 1090, 500, 64, RED_T, s.t("descending"), "l"), text("commands down", X + 1090, 570, 46, MAROON, s.t("commands"), "l"), text("to the muscles", X + 1090, 645, 46, MAROON, s.t("commands") + 0.5, "l"),
          text("white matter = highways", X + 960, 1010, 50, GOLD_T, s.start + 0.4, "c")]

    # ---------------- PAYOFF (C)
    s = sc["payoff"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, tr)
    X = 2 * PW
    kn = pop(knee_pic(False), X + 400, 650, h=640, t=s.start + 0.3)
    tsn, tmo = s.t("sensory"), s.t("motor")
    cc = pop(cross_pic(), X + 1250, 470, w=640, t=s.t("spinal") - 0.3)
    py = [kn, text("hammer stretches the muscle", X + 600, 130, 56, MAROON, s.t("stretches") - 0.3, "c"), cc,
          lead([(X + 560, 520), (X + 800, 400), (X + 1050, 380)], tsn, BLUE_T, 10, 0.9, arrow=True), text("sensory nerve", X + 800, 330, 50, BLUE_T, tsn, "c"),
          lead([(X + 1050, 600), (X + 800, 700), (X + 520, 640)], tmo - 0.3, RED_T, 10, 0.9, arrow=True), text("motor neuron", X + 800, 770, 50, RED_T, tmo - 0.1, "c"),
          text("muscle contracts", X + 450, 1010, 52, RED_T, s.t("contract"), "c"),
          pop(brain, X + 1700, 230, h=240, t=s.t("brain") - 0.4), text("not needed!", X + 1700, 420, 56, GOLD_T, s.t("needed"), "c"), text("so it is FAST", X + 1700, 770, 62, GREEN_T, s.t("fast") - 1.0, "c")]

    # ---------------- INJURY (D)
    s = sc["injury"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, py)
    Y = PH
    si = pop(sv("Male-silhouette"), 520, Y + 540, h=980, t=s.start + 0.3)
    tw_, th_ = s.t("below"), s.t("higher")
    ti = pop(tint(0.50), 520, Y + 540, h=980, t=tw_ - 0.2)
    th = pop(tint(0.20), 520, Y + 540, h=980, t=th_ - 0.2)
    ij = [si, ti, th, text("injury: connection cut", 1330, Y + 190, 66, RED_T, s.t("injury"), "c"), text("everything below is cut off", 1330, Y + 290, 56, MAROON, tw_, "c"),
          text("the HIGHER the injury", 1330, Y + 520, 70, RED_T, th_ - 0.2, "c"), text("the MORE body is affected", 1330, Y + 610, 56, MAROON, th_ + 0.5, "c"),
          panel(980, Y + 790, 1700, Y + 950, MINT, s.t("protecting") - 0.9), text("protect your spine", 1340, Y + 890, 64, GREEN_T, s.t("protecting") - 0.6, "c")]

    # ---------------- RECAP (E)
    s = sc["recap"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, ij)
    X = PW
    rp2 = title("remember 3 things", X + 960, Y + 100, s.start + 0.4)
    for w, a, b, col, tc_, x in (("cable", "a cable from", "brain to body", PINK, RED_T, 400), ("gray", "gray processes,", "white carries", CREAM, GOLD_T, 960), ("reflexes", "reflexes", "skip the brain", MINT, GREEN_T, 1520)):
        tw2 = s.t(w) - 0.3
        rp2 += [panel(X + x - 265, Y + 220, X + x + 265, Y + 600, col, tw2 - 0.2), text(a, X + x, Y + 360, 52, tc_, tw2, "c"), text(b, X + x, Y + 470, 52, MAROON, tw2 + 0.6, "c")]
    tn = s.t("next")
    rp2 += [panel(X + 200, Y + 720, X + 1720, Y + 890, LILAC, tn - 0.3), text("next: who runs your heart without asking?", X + 960, Y + 820, 52, PURPLE, tn, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def build_short(n):
    d = EP / f"short{n}"
    sc, t0 = load(d)
    bd = B.Board(3, 2)
    pops, glows = [], []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    cam = bd.camera
    A, Bc, C = (960, 540), (PW + 960, 540), (2 * PW + 960, 540)
    cam(0, *A, 1.0, 0.1)
    if n == 1:
        s = sc["case"]
        k1 = pop(knee_pic(False), 520, 560, h=760, t=0.3)
        tk = s.t("kicks")
        k2 = pop(knee_pic(True), 520, 560, h=760, t=tk - 0.1)
        bd.erase(tk - 0.1, [k1])
        a = [k1, k2, text("TAP!", 1400, 200, 130, GOLD_T, s.t("taps"), "c"), text("the leg kicks", 1400, 400, 90, RED_T, tk, "c"),
             text("you did not decide", 1400, 620, 70, PURPLE, s.t("decide") - 0.3, "c")]
        s = sc["turn"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(knee_pic(False), X + 380, 700, h=560, t=s.start + 0.3), pop(OB.brain_img(), X + 1500, 190, h=300, t=s.t("brain") - 0.5),
             lead([(X + 560, 520), (X + 900, 380), (X + 1050, 300)], s.t("signal"), BLUE_T, 10, 1.0, arrow=True), text("the signal turns around", X + 1050, 560, 64, RED_T, s.t("turns"), "c"),
             text("long before the brain!", X + 1250, 660, 58, MAROON, s.t("before") - 0.2, "c"), text("where?", X + 960, 900, 150, GOLD_T, s.t("where") - 0.3, "c")]
    else:
        s = sc["case"]
        sp = pop(spine_pic(), 360, 540, h=980, t=0.3)
        m = spine_marks()
        ks = 980 / SPINE_H
        yl = 540 - 490 + (m["L"][0] + m["L"][1]) / 2 * ks
        ne = lead([(1000, yl - 60), (560, yl - 5), (400, yl)], s.t("needle"), (110, 110, 120), 14, 0.9)
        a = [sp, ne, text("a needle in the lower back", 1350, 230, 62, MAROON, s.t("needle"), "c"), text("tests the fluid", 1350, 330, 66, BLUE_T, s.t("fluid"), "c"),
             text("and does NOT hurt the cord", 1350, 480, 62, GREEN_T, s.t("hurt"), "c"), text("how?", 1350, 800, 170, GOLD_T, s.t("how") - 0.3, "c")]
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        yl1 = 540 - 490 + m["L1end"] * ks
        b = [pop(spine_pic(), X + 360, 540, h=980, t=s.start + 0.3), pop(cord_overlay(), X + 360, 540, h=980, t=s.t("spinal") - 0.2),
             text("the cord stops HIGH", X + 1350, 330, 76, PURPLE, s.t("stops"), "c"), lead([(X + 1000, 330), (X + 360, yl1)], s.t("stops") + 0.2, PURPLE, 6, 0.6),
             text("the spine goes lower", X + 1350, 560, 70, MAROON, s.t("spine") - 0.2, "c")]
        s = sc["clue"]
        cam(s.start, *C, 1.0, 1.0)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        c = [pop(spine_pic(), X + 360, 540, h=980, t=s.start + 0.3), pop(cord_overlay(), X + 360, 540, h=980, t=s.start + 0.4), pop(cauda_overlay(), X + 360, 540, h=980, t=s.t("hangs") - 0.3),
             text("a bundle of nerves hangs below", X + 1350, 330, 60, GOLD_T, s.t("bundle"), "c"), text("with a strange name", X + 1350, 430, 62, MAROON, s.t("strange") - 0.2, "c"),
             text("?", X + 1350, 800, 240, GOLD_T, s.t("name") - 0.3, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def make_short(n):
    import package as P
    import bridge
    bd, sc = build_short(n)
    board = NU.render_board(bd, sc, f"spine_story{n}")
    top = Image.new("RGBA", (1080, 1920), (255, 255, 255, 0))
    d = ImageDraw.Draw(top)
    lines, cur = [], ""
    for w in SHORT_TITLES[n].upper().split():
        if len(cur + " " + w) > 14:
            lines.append(cur.strip())
            cur = w
        else:
            cur += " " + w
    lines.append(cur.strip())
    size = 96 if len(lines) <= 3 else 80
    y = 600 - (size + 18) * len(lines) + (size + 18) // 2 - 20
    for ln in lines:
        P.btext(d, (540, y), ln, size, P.MAROON, "mm")
        y += size + 18
    d.rounded_rectangle((170, 1380, 910, 1490), radius=55, fill=P.MAROON)
    d.text((540, 1435), "FULL VIDEO ON THE CHANNEL", font=P.f(44), fill=(255, 255, 255), anchor="mm", stroke_width=1, stroke_fill=(255, 255, 255))
    d.text((540, 1600), "THE ANATOMY UNFOLDED", font=P.f(46), fill=(150, 120, 130), anchor="mm")
    ov = OUT / f"spine_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"spine_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["spine"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "spine", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"spine_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"sshort{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "spine", intro=True)
        f.replace(OUT / "final_spine.mp4")
        print("done ->", OUT / "final_spine.mp4")
