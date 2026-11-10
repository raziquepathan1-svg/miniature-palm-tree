"""Nervous system series: How Do Brain Cells Talk? (owner-approved script, 9 Nov 2026) + 2 story Shorts.

    python3 osm_neuron.py                 # full video  -> final_neuron.mp4
    python3 osm_neuron.py stills          # end-of-scene frames
    python3 osm_neuron.py short 1|2       # story Short -> neuron_short1.mp4 / neuron_short2.mp4
Env: EP_DIR (episode folder, default ../neuron), OUT_DIR (output folder).
"""
import json
import math
import os
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "neuron")))
OUT = Path(os.environ.get("OUT_DIR", str(HERE)))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_preview as OP  # noqa: E402
import osm_brain as OB  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OB.PINK, OB.LILAC, OB.CREAM, OB.MINT, OB.SKY
PW, PH = 1920, 1080
sv = OB.sv
SHORT_TITLES = {1: "The Hot Pan Mystery", 2: "The Poison That Stops Every Muscle"}
SHORT_Q = {1: "So how does one cell tell the next one?", 2: "So what is it blocking?"}


# ----------------------------------------------------------------------------- pictures
def pan_pic():
    S, W, H = 3, 560, 330
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(3):   # heat waves
        pts = [((90 + k * 130 + 14 * math.sin(y / 14.0)) * S, y * S) for y in range(10, 120, 4)]
        d.line(pts, fill=(235, 90, 50, 255), width=7 * S)
    d.rounded_rectangle((370 * S, 215 * S, 550 * S, 245 * S), radius=14 * S, fill=(60, 60, 70), outline=(30, 30, 40), width=3 * S)
    d.ellipse((30 * S, 130 * S, 400 * S, 310 * S), fill=(75, 75, 88), outline=(30, 30, 40), width=5 * S)
    d.ellipse((60 * S, 148 * S, 370 * S, 280 * S), fill=(105, 105, 120), outline=(60, 60, 70), width=3 * S)
    d.ellipse((60 * S, 148 * S, 370 * S, 280 * S), outline=(240, 110, 50), width=8 * S)
    return im.resize((W, H), Image.LANCZOS)


def _branch(d, x, y, ang, ln, depth, w, col, S):
    if depth == 0 or ln < 14:
        return
    a = math.radians(ang)
    x2, y2 = x + ln * math.cos(a), y + ln * math.sin(a)
    d.line([(x * S, y * S), (x2 * S, y2 * S)], fill=col, width=max(2, int(w * S)))
    for da in (-28, 26):
        _branch(d, x2, y2, ang + da, ln * 0.68, depth - 1, w * 0.7, col, S)


def neuron_pic():
    """one neuron, 1500 x 600: dendrites (blue), cell body (pink), axon (green), terminals (purple)."""
    S, W, H = 2, 1500, 600
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for ang in (125, 150, 175, 200, 225, 250):
        _branch(d, 400, 300, ang, 165, 3, 11, (70, 120, 210), S)
    d.line([(480 * S, 300 * S), (1235 * S, 300 * S)], fill=(120, 180, 110), width=18 * S)
    for ex, ey in ((1340, 215), (1365, 300), (1340, 385)):
        d.line([(1235 * S, 300 * S), (ex * S, ey * S)], fill=(120, 180, 110), width=9 * S)
        d.ellipse(((ex - 30) * S, (ey - 30) * S, (ex + 30) * S, (ey + 30) * S), fill=(166, 125, 214), outline=(100, 60, 150), width=4 * S)
    d.ellipse((305 * S, 205 * S, 495 * S, 395 * S), fill=(248, 190, 205), outline=(190, 90, 120), width=6 * S)
    d.ellipse((365 * S, 265 * S, 445 * S, 335 * S), fill=(214, 120, 150), outline=(150, 60, 90), width=4 * S)
    return im.resize((W, H), Image.LANCZOS)


def myelin_pic():
    S, W, H = 2, 1500, 600
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(7):
        x0 = 530 + i * 96
        d.rounded_rectangle((x0 * S, 272 * S, (x0 + 82) * S, 328 * S), radius=24 * S, fill=(250, 215, 90), outline=(170, 120, 0), width=4 * S)
    return im.resize((W, H), Image.LANCZOS)


def membrane_pic():
    """cell membrane at rest: more sodium (gold) outside, more potassium (purple) inside."""
    S, W, H = 3, 900, 560
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W * S, 250 * S), fill=(226, 238, 250))
    d.rectangle((0, 310 * S, W * S, H * S), fill=(252, 232, 236))
    for x in range(10, W, 26):
        for y in (262, 298):
            d.line([(x * S, 268 * S), (x * S, 292 * S)], fill=(190, 150, 100), width=3 * S)
            d.ellipse(((x - 12) * S, (y - 12) * S, (x + 12) * S, (y + 12) * S), fill=(240, 215, 170), outline=(180, 140, 90), width=2 * S)
    for cx in (200, 450, 700):
        d.rounded_rectangle(((cx - 32) * S, 238 * S, (cx + 32) * S, 322 * S), radius=14 * S, fill=(150, 110, 200), outline=(90, 60, 140), width=4 * S)
        d.rounded_rectangle(((cx - 8) * S, 244 * S, (cx + 8) * S, 316 * S), radius=6 * S, fill=(255, 255, 255))
    rnd = random.Random(5)
    f = B.hfont(15 * S)

    def ion(x, y, kind):
        col, ol, lab = ((245, 200, 60), (170, 120, 0), "Na+") if kind == "na" else ((166, 125, 214), (100, 60, 150), "K+")
        d.ellipse(((x - 19) * S, (y - 19) * S, (x + 19) * S, (y + 19) * S), fill=col, outline=ol, width=3 * S)
        d.text((x * S, y * S), lab, font=f, fill=(60, 30, 80), anchor="mm")
    spots = [(60 + (i % 7) * 120 + rnd.randint(-15, 15), 40 + (i // 7) * 62 + rnd.randint(-8, 8)) for i in range(21)]
    for i, (x, y) in enumerate(spots):
        ion(x, y, "na" if i % 7 != 3 or i < 7 else "k")
    spots = [(70 + (i % 6) * 135 + rnd.randint(-15, 15), 350 + (i // 6) * 60 + rnd.randint(-8, 8)) for i in range(18)]
    for i, (x, y) in enumerate(spots):
        ion(x, y, "k" if i % 6 != 2 or i < 6 else "na")
    return im.resize((W, H), Image.LANCZOS)


def synapse_pic(with_dots=False):
    S, W, H = 3, 1000, 700
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if not with_dots:
        d.ellipse((130 * S, -120 * S, 870 * S, 300 * S), fill=(232, 222, 247), outline=(110, 70, 160), width=6 * S)
        for (x, y) in ((300, 150), (430, 205), (570, 150), (700, 205), (370, 90), (630, 90)):
            d.ellipse(((x - 38) * S, (y - 38) * S, (x + 38) * S, (y + 38) * S), fill=(255, 255, 255), outline=(150, 100, 200), width=4 * S)
            for k in range(3):
                d.ellipse(((x - 14 + k * 14) * S, (y - 5) * S, (x - 6 + k * 14) * S, (y + 3) * S), fill=(245, 200, 60))
        d.rounded_rectangle((60 * S, 420 * S, 940 * S, 700 * S), radius=30 * S, fill=(226, 238, 250), outline=(60, 110, 180), width=6 * S)
        for x in (250, 430, 610, 790):
            d.pieslice(((x - 42) * S, 380 * S, (x + 42) * S, 464 * S), 0, 180, fill=(255, 255, 255), outline=(60, 110, 180), width=5 * S)
    else:
        rnd = random.Random(9)
        for i in range(22):
            x, y = rnd.randint(200, 800), rnd.randint(320, 400)
            d.ellipse(((x - 11) * S, (y - 11) * S, (x + 11) * S, (y + 11) * S), fill=(245, 200, 60), outline=(170, 120, 0), width=2 * S)
    return im.resize((W, H), Image.LANCZOS)


def keylock_pic():
    S, W, H = 3, 1000, 420
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((60 * S, 130 * S, 260 * S, 330 * S), fill=(245, 200, 60), outline=(170, 120, 0), width=6 * S)
    d.rectangle((250 * S, 205 * S, 330 * S, 255 * S), fill=(245, 200, 60), outline=(170, 120, 0), width=5 * S)
    d.rounded_rectangle((560 * S, 40 * S, 960 * S, 380 * S), radius=30 * S, fill=(226, 238, 250), outline=(60, 110, 180), width=6 * S)
    d.ellipse((520 * S, 130 * S, 720 * S, 330 * S), fill=(255, 255, 255), outline=(60, 110, 180), width=5 * S)
    d.rectangle((520 * S, 205 * S, 640 * S, 255 * S), fill=(255, 255, 255))
    return im.resize((W, H), Image.LANCZOS)


def network_pic():
    S, W, H = 2, 1400, 700
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rnd = random.Random(11)
    pts = [(rnd.randint(60, W - 60), rnd.randint(50, H - 50)) for _ in range(34)]
    for i, (x, y) in enumerate(pts):
        near = sorted(range(len(pts)), key=lambda j: (pts[j][0] - x) ** 2 + (pts[j][1] - y) ** 2)[1:4]
        for j in near:
            d.line([(x * S, y * S), (pts[j][0] * S, pts[j][1] * S)], fill=(150, 185, 238), width=3 * S)
    for (x, y) in pts:
        r = rnd.choice((13, 16, 20))
        d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=(205, 175, 238), outline=(110, 70, 160), width=3 * S)
    return im.resize((W, H), Image.LANCZOS)


def arrow_pic():
    S, W, H = 3, 900, 200
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line([(60 * S, 100 * S), (800 * S, 100 * S)], fill=(140, 95, 55), width=12 * S)
    d.polygon([(800 * S, 60 * S), (890 * S, 100 * S), (800 * S, 140 * S)], fill=(120, 120, 130), outline=(60, 60, 70))
    for k in range(3):
        x = 60 + k * 36
        d.polygon([(x * S, 100 * S), ((x + 40) * S, 55 * S), ((x + 60) * S, 55 * S), ((x + 22) * S, 100 * S)], fill=(200, 60, 60))
        d.polygon([(x * S, 100 * S), ((x + 40) * S, 145 * S), ((x + 60) * S, 145 * S), ((x + 22) * S, 100 * S)], fill=(200, 60, 60))
    return im.resize((W, H), Image.LANCZOS)


class Sc(HA.Sc):
    def __init__(self, sid, text, start, d):
        import render as R
        self.id, self.text, self.start = sid, text, start
        self.audio = d / "audio" / f"{sid}.wav"
        self.dur = R.dur(self.audio)
        self.words = text.lower().replace(",", "").replace(".", "").replace("?", "").replace(":", "").replace("'", "").split()


def load(d):
    data = json.load(open(d / "script.json"))
    sc, t0 = {}, 0.0
    for s in data:
        sc[s["id"]] = Sc(s["id"], s["text"], t0, d)
        t0 += sc[s["id"]].dur
    return sc, t0


# ----------------------------------------------------------------------------- full video
def build():
    sc, t0 = load(EP)
    bd = B.Board(3, 2)
    pops, glows = [], []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    cam = bd.camera
    A, Bc, C = (960, 540), (PW + 960, 540), (2 * PW + 960, 540)
    D, E, Fp = (960, PH + 540), (PW + 960, PH + 540), (2 * PW + 960, PH + 540)
    cam(0, *A, 1.0, 0.1)
    GRAY = OB.GRAY_T

    def L(p0, p1, t, col=MAROON, w=4):
        mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - 18)
        return lead([p0, mid, p1], t, col, w, 0.5)

    # ---------------- STORY (A)
    s = sc["story"]
    arm = pop(sv("Bras"), 540, 580, w=1000, t=0.3)
    pan = pop(pan_pic(), 1480, 640, w=640, t=s.t("pan") - 0.3)
    st = [arm, pan, text("HOT!", 1480, 400, 130, RED_T, s.t("hot"), "c"),
          lead([(1040, 470), (800, 440), (560, 470)], s.t("jumped") - 0.2, BLUE_T, 8, 0.6, arrow=True), text("hand jumps back!", 760, 400, 56, BLUE_T, s.t("jumped"), "c"),
          text("how so fast?", 960, 860, 90, PURPLE, s.t("how"), "c"), text("let's follow the message", 960, 980, 56, MAROON, s.t("follow") - 0.8, "c")]

    # ---------------- OVERVIEW (B)
    s = sc["overview"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, st)
    X = PW
    nw = pop(network_pic(), X + 960, 480, w=1500, t=s.start + 0.3)
    ov = [nw, text("86 billion neurons", X + 960, 130, 100, GOLD_T, s.t("86"), "c"), text("tiny electrical signals", X + 960, 930, 70, PURPLE, s.t("electrical"), "c"),
          text("let's zoom into ONE neuron", X + 960, 1030, 50, BLUE_T, s.t("one") - 0.2, "c")]

    # ---------------- STRUCTURE (C) + MYELIN
    s = sc["structure"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ov)
    X = 2 * PW
    nu = pop(neuron_pic(), X + 960, 440, w=1700, t=s.start + 0.3)
    ss = [nu]
    td, tb, ta = s.t("dendrites"), s.t("cell"), s.t("axon")
    ss += [text("dendrites", X + 330, 910, 66, BLUE_T, td, "c"), text("receive messages", X + 330, 1003, 40, MAROON, td + 0.6, "c"), L((X + 330, 860), nu.map((250, 310)), td + 0.2, BLUE_T),
           text("cell body", X + 780, 910, 66, RED_T, tb, "c"), text("processes them", X + 780, 1003, 40, MAROON, tb + 0.6, "c"), L((X + 780, 860), nu.map((400, 340)), tb + 0.2, RED_T),
           text("axon", X + 1400, 910, 66, GREEN_T, ta, "c"), text("carries the message away", X + 1400, 1003, 40, MAROON, ta + 0.6, "c"), L((X + 1400, 860), nu.map((900, 304)), ta + 0.2, GREEN_T)]
    s2 = sc["myelin"]
    tm = s2.t("myelin")
    mp = pop(myelin_pic(), X + 960, 440, w=1700, t=tm - 0.2)
    ss += [mp, text("myelin = insulation", X + 1380, 100, 62, GOLD_T, tm, "c"), L((X + 1300, 135), nu.map((900, 276)), tm + 0.4, GOLD_T),
           panel(X + 1160, 150, X + 1830, 270, CREAM, s2.t("faster") - 0.9), text("up to 120 m/s", X + 1495, 232, 66, GREEN_T, s2.t("faster") - 0.6, "c")]

    # ---------------- RESTING (D)
    s = sc["resting"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, ss)
    Y = PH
    mb = pop(membrane_pic(), 650, Y + 530, w=1240, t=s.start + 0.3)
    rs = [mb, text("OUTSIDE", 650, Y + 90, 54, BLUE_T, s.t("outside") - 0.3, "c"), text("INSIDE", 650, Y + 1005, 54, RED_T, s.t("inside") - 0.3, "c"),
          panel(1330, Y + 120, 1880, Y + 360, CREAM, s.t("battery") - 0.3), text("like a charged", 1605, Y + 215, 50, MAROON, s.t("battery"), "c"),
          text("battery", 1605, Y + 295, 70, GOLD_T, s.t("battery") + 0.4, "c"),
          text("more sodium", 1605, Y + 470, 54, (170, 120, 0), s.t("sodium"), "c"), text("outside", 1605, Y + 545, 40, MAROON, s.t("sodium") + 0.4, "c"),
          text("more potassium", 1605, Y + 640, 54, PURPLE, s.t("potassium"), "c"), text("inside", 1605, Y + 715, 40, MAROON, s.t("potassium") + 0.4, "c"),
          panel(1330, Y + 780, 1880, Y + 960, SKY, s.t("slightly") - 1.4), text("inside = negative", 1605, Y + 850, 50, BLUE_T, s.t("slightly") - 1.1, "c"),
          text("about -70 mV", 1605, Y + 925, 46, MAROON, s.t("slightly") - 0.3, "c")]

    # ---------------- SPIKE (E)
    s = sc["spike"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, rs)
    X = PW

    def gy(mv):
        return Y + 840 - (mv + 80) * 4.9

    gx = X + 180
    sp = [text("action potential", X + 660, Y + 100, 72, PURPLE, s.start + 0.3, "c"),
          lead([(gx - 20, gy(-80)), (gx - 20, gy(40))], s.start + 0.5, MAROON, 5, 0.6, arrow=True), lead([(gx - 20, gy(-80)), (gx + 1000, gy(-80))], s.start + 0.8, MAROON, 5, 0.6, arrow=True),
          text("voltage", gx - 30, Y + 190, 34, MAROON, s.start + 1.0, "r"), text("time", gx + 940, gy(-80) + 50, 34, MAROON, s.start + 1.2, "c"),
          text("-70 mV", gx - 40, gy(-70) + 12, 36, BLUE_T, s.start + 1.0, "r"), text("+30 mV", gx - 40, gy(30) + 12, 36, RED_T, s.start + 1.0, "r"),
          lead([(gx, gy(-55)), (gx + 900, gy(-55))], s.t("enough"), (170, 110, 0), 3, 0.8), text("threshold", gx + 760, gy(-55) - 14, 34, (170, 110, 0), s.t("enough"), "l")]
    up = [(gx, gy(-70)), (gx + 150, gy(-70)), (gx + 215, gy(-55)), (gx + 255, gy(30)), (gx + 285, gy(30))]
    down = [(gx + 285, gy(30)), (gx + 330, gy(-60)), (gx + 400, gy(-78)), (gx + 520, gy(-71)), (gx + 700, gy(-70))]
    sp += [lead(up, s.t("sodium"), RED_T, 9, 1.0), lead(down, s.t("potassium"), BLUE_T, 9, 1.2)]
    steps = [("1  sodium channels open", s.t("channels"), GOLD_T), ("2  sodium rushes in: inside turns +", s.t("rushes"), RED_T),
             ("3  the spike = ACTION POTENTIAL", s.t("spike"), PURPLE), ("4  potassium flows out: resets", s.t("potassium"), BLUE_T)]
    for i, (lab, tt, col) in enumerate(steps):
        sp.append(text(lab, X + 1230, Y + 300 + i * 150, 42, col, tt, "l"))

    # ---------------- TRAVEL (F)
    s = sc["travel"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, sp)
    X = 2 * PW
    tr = [text("the spike travels down the axon", X + 960, Y + 110, 66, MAROON, s.start + 0.3, "c"),
          lead([(X + 120, Y + 560), (X + 1800, Y + 560)], s.start + 0.5, (120, 180, 110), 22, 1.0)]
    tdm = s.t("dominoes")
    for i in range(10):
        tt = tdm - 0.4 + i * 0.28
        x0 = X + 200 + i * 160
        tr.append(panel(x0, Y + 440, x0 + 56, Y + 560, [(250, 215, 90), (245, 170, 80)][i % 2], tt))
        glows.append((tt, (x0 + 28, Y + 500), 0.7, 70))
    tr += [text("a wave of falling dominoes", X + 960, Y + 770, 62, GOLD_T, tdm, "c"),
           panel(X + 260, Y + 830, X + 1660, Y + 1000, PINK, s.t("all") - 0.3), text("ALL OR NOTHING", X + 960, Y + 930, 90, RED_T, s.t("all"), "c")]

    # ---------------- SYNAPSE (A)
    s = sc["synapse"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, tr)
    sy = pop(synapse_pic(), 560, 560, h=880, t=s.start + 0.3)
    tg, trl = s.t("gap"), s.t("releases")
    dots = pop(synapse_pic(True), 560, 560, h=880, t=trl)
    sn = [sy, dots, text("end of the axon", 1300, 150, 54, GREEN_T, s.start + 0.5, "l"), L((1290, 135), sy.map((650, 120)), s.start + 0.8, GREEN_T),
          text("SYNAPSE", 1300, 400, 90, RED_T, s.t("synapse"), "l"), text("a tiny gap", 1300, 500, 50, MAROON, tg + 0.1, "l"), L((1290, 385), sy.map((930, 350)), tg + 0.3, RED_T),
          text("signal can't jump across", 1270, 620, 44, MAROON, s.t("cannot"), "l"),
          text("neurotransmitters", 1270, 780, 56, GOLD_T, s.t("neurotransmitters") - 0.9, "l"), text("= chemical messengers", 1270, 860, 42, MAROON, s.t("neurotransmitters") - 0.2, "l"),
          lead([(900, 330), (900, 440)], trl, GOLD_T, 7, 0.6, arrow=True), text("next cell", 1270, 960, 50, BLUE_T, s.t("instead") - 0.5, "l"), L((1290, 945), sy.map((930, 560)), s.t("instead") + 0.3, BLUE_T)]

    # ---------------- RECEPTOR (B)
    s = sc["receptor"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, sn)
    X = PW
    kl = pop(keylock_pic(), X + 760, 420, w=1300, t=s.t("fit") - 0.3)
    rc = [kl, text("neurotransmitters fit into receptors", X + 960, 110, 60, MAROON, s.start + 0.4, "c"),
          text("like a KEY in a LOCK", X + 760, 700, 80, GOLD_T, s.t("key"), "c"),
          lead([(X + 560, 420), (X + 900, 420)], s.t("key") + 0.4, GOLD_T, 8, 0.6, arrow=True),
          panel(X + 360, 800, X + 1160, 920, MINT, s.t("passes") - 0.3), text("message passed on!", X + 760, 880, 66, GREEN_T, s.t("passes"), "c")]
    for i, (nm, col, pc) in enumerate((("dopamine", RED_T, PINK), ("serotonin", PURPLE, LILAC), ("acetylcholine", BLUE_T, SKY))):
        tt = s.t(nm) - (1.0 if nm == "acetylcholine" else 0.3)
        y0 = 250 + i * 250
        rc += [panel(X + 1420, y0, X + 1880, y0 + 190, pc, tt - 0.3), text(nm, X + 1650, y0 + 120, 52 if i == 2 else 60, col, tt, "c")]

    # ---------------- PAYOFF (C)
    s = sc["payoff"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, rc)
    X = 2 * PW
    arm2 = pop(sv("Bras"), X + 620, 930, w=1100, t=s.start + 0.3)
    pan2 = pop(pan_pic(), X + 1500, 930, w=420, t=s.start + 0.5)
    cord = panel(X + 760, 330, X + 860, 760, LILAC, s.t("spinal") - 0.5)
    tp, tsp, trf, tmu, tbr = s.t("pain"), s.t("spinal"), s.t("reflex"), s.t("muscle"), s.t("reaches")
    py = [arm2, pan2, cord, text("spinal cord", X + 720, 470, 54, PURPLE, tsp, "r"),
          lead([(X + 1170, 880), (X + 1170, 700), (X + 860, 600)], tp + 0.2, BLUE_T, 9, 0.9, arrow=True), text("pain nerves", X + 1330, 640, 56, BLUE_T, tp, "l"),
          text("reflex circuit", X + 810, 800, 48, PURPLE, trf, "c"),
          lead([(X + 760, 600), (X + 560, 760), (X + 560, 860)], tmu - 0.5, RED_T, 9, 0.9, arrow=True), text("muscle pulls back", X + 80, 650, 52, RED_T, tmu - 0.3, "l"),
          pop(brain := OB.brain_img(), X + 810, 140, h=200, t=tbr - 0.3),
          lead([(X + 810, 330), (X + 810, 250)], tbr, MAROON, 6, 0.7, arrow=True), text("feels it a moment later", X + 1150, 150, 50, MAROON, tbr + 0.3, "l")]

    # ---------------- RECAP (D)
    s = sc["recap"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, py)
    Y = PH
    rp = title("remember 3 things", 960, Y + 100, s.start + 0.4)
    cards = [("spikes", "neurons use", "electrical spikes", PINK, RED_T, 400), ("chemicals", "synapses use", "chemicals", CREAM, GOLD_T, 960), ("fast", "myelin makes it", "FAST", MINT, GREEN_T, 1520)]
    for w, a, b, col, tc_, x in cards:
        tw_ = s.t(w) - 0.3
        rp += [panel(x - 265, Y + 220, x + 265, Y + 600, col, tw_ - 0.2), text(a, x, Y + 360, 54, tc_, tw_, "c"), text(b, x, Y + 470, 56, MAROON, tw_ + 0.6, "c")]
    tn = s.t("next")
    rp += [panel(240, Y + 720, 1680, Y + 890, LILAC, tn - 0.3), text("next: how the spinal cord carries messages", 960, Y + 820, 54, PURPLE, tn, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


# ----------------------------------------------------------------------------- story Shorts
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
        arm = pop(sv("Bras"), 540, 560, w=1000, t=0.3)
        pan = pop(pan_pic(), 1480, 620, w=660, t=s.t("hot") - 0.2)
        a = [arm, pan, text("HOT PAN!", 1480, 380, 120, RED_T, s.t("pan"), "c"), lead([(1040, 450), (800, 420), (560, 450)], s.t("jumps") - 0.1, BLUE_T, 9, 0.6, arrow=True),
             text("hand jumps back", 780, 380, 72, BLUE_T, s.t("jumps"), "c"), text("before you feel pain!", 960, 880, 84, PURPLE, s.t("before") - 0.3, "c"),
             text("how is that possible?", 960, 1000, 60, MAROON, s.t("how") - 0.5, "c")]
        s = sc["speed"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [text("nerve signal speed", X + 960, 130, 66, MAROON, s.start + 0.3, "c"), text("120", X + 650, 380, 240, GOLD_T, s.t("120"), "c"), text("meters per second", X + 650, 600, 62, MAROON, s.t("meters"), "c"),
             pop(OB.brain_img(), X + 1450, 420, h=420, t=s.t("wait") - 0.5), text("doesn't wait", X + 1450, 700, 64, RED_T, s.t("wait"), "c"),
             text("for your brain", X + 1450, 780, 64, RED_T, s.t("wait") + 0.5, "c"), text("who gave the order?", X + 960, 960, 100, PURPLE, s.t("who") - 0.2, "c")]
    else:
        s = sc["arrows"]
        ar = pop(arrow_pic(), 700, 400, w=1100, t=s.t("arrows") - 0.3)
        a = [text("South America", 960, 130, 70, MAROON, s.start + 0.3, "c"), ar, text("CURARE", 1500, 320, 110, PURPLE, s.t("poison") - 0.3, "c"), text("a poison", 1500, 455, 56, MAROON, s.t("poison") + 0.4, "c"),
             text("could NOT move", 960, 760, 100, RED_T, s.t("move") - 0.3, "c"), text("could not even breathe alone", 960, 900, 70, RED_T, s.t("breathe") - 0.6, "c")]
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [text("YET...", X + 960, 130, 120, BLUE_T, s.start + 0.3, "c"), pop(OB.brain_img(), X + 560, 560, h=640, t=s.t("brain") - 0.3),
             text("brain: working", X + 1450, 380, 84, GREEN_T, s.t("working") - 0.3, "c"), text("brain: untouched", X + 1450, 560, 76, MAROON, s.t("never") - 0.3, "c"),
             text("muscles: untouched", X + 1450, 700, 76, MAROON, s.t("never") + 0.8, "c")]
        s = sc["clue"]
        cam(s.start, *C, 1.0, 1.0)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        sy = pop(synapse_pic(), X + 560, 560, h=880, t=s.start + 0.3)
        c = [sy, pop(synapse_pic(True), X + 560, 560, h=880, t=s.start + 0.8), text("it blocked something", X + 1400, 250, 70, RED_T, s.t("blocked"), "c"),
             text("in between:", X + 1400, 340, 66, MAROON, s.t("between"), "c"), text("a tiny gap", X + 1400, 520, 100, PURPLE, s.t("gap") - 0.3, "c"),
             text("?", X + 1400, 820, 240, GOLD_T, s.t("talks") - 0.4, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render_board(bd, sc, name, intro=False):
    import render_ecg as RE
    vid = OUT / f"{name}_video_only.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", "30", "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(vid)], stdin=subprocess.PIPE)
    if intro:
        for f in range(int(round(RE.INTRO_DUR * 30))):
            ff.stdin.write(RE.intro_frame(f / 30).tobytes())
    for f in range(int(bd.total * 30)):
        ff.stdin.write(OF.credit(bd.frame(f / 30)).tobytes())
    ff.stdin.close()
    ff.wait()
    lst = OUT / f"{name}_audio.txt"
    with open(lst, "w") as fh:
        if intro:
            RE.intro_audio(OUT / "chime_intro.wav")
            fh.write(f"file '{OUT / 'chime_intro.wav'}'\n")
        for s in sc.values():
            fh.write(f"file '{s.audio}'\n")
    wav = OUT / f"{name}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "pcm_s16le", str(wav)], check=True)
    final = OUT / f"{name}_board.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(wav), "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final)], check=True)
    return final


def make_short(n):
    import package as P
    import bridge
    bd, sc = build_short(n)
    board = render_board(bd, sc, f"neuron_story{n}")
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
    ov = OUT / f"neuron_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"neuron_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["neuron"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "neuron", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"neuron_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"nshort{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = render_board(bd, sc, "neuron", intro=True)
        f.replace(OUT / "final_neuron.mp4")
        print("done ->", OUT / "final_neuron.mp4")
