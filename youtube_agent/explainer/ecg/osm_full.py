"""Video 1, Osmosis style, full length: pictures pop in for each idea, get labelled in maroon small-caps
handwriting, then fade away; the camera zooms and pans; the conduction path draws on the painted heart."""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
SV = HERE.parent / "servier"
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import render_board as RB  # noqa: E402
import render as R  # noqa: E402
import osm_preview as OP  # noqa: E402

MAROON, PURPLE, TEAL, BLUE_T, RED_T, GOLD_T, GREEN_T = OP.MAROON, OP.PURPLE, OP.TEAL, OP.BLUE_T, OP.RED_T, OP.GOLD_T, (40, 140, 90)
WIRE, WIRE_D = OP.WIRE, OP.WIRE_D
FPS = 30
PINK, LILAC, CREAM, MINT, SKY = (252, 230, 233), (236, 230, 247), (253, 243, 214), (224, 244, 233), (226, 238, 250)


def sv(name):
    return Image.open(SV / f"{name}.png").convert("RGBA")


def bolt():
    S = 4
    im = Image.new("RGBA", (300 * S, 420 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(x * S, y * S) for x, y in [(170, 20), (60, 230), (140, 230), (100, 400), (250, 170), (165, 170), (230, 20)]]
    d.polygon(pts, fill=(255, 215, 90, 255))
    d.line(pts + [pts[0]], fill=(214, 150, 30, 255), width=7 * S, joint="curve")
    return im.resize((300, 420), Image.LANCZOS)


def battery(level, col):
    S = 4
    im = Image.new("RGBA", (220 * S, 420 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    dark = tuple(int(c * 0.7) for c in col)
    d.rounded_rectangle((70 * S, 10 * S, 150 * S, 50 * S), radius=10 * S, fill=(220, 220, 228), outline=(150, 150, 160), width=5 * S)
    d.rounded_rectangle((20 * S, 40 * S, 200 * S, 410 * S), radius=28 * S, fill=(246, 246, 250), outline=(150, 150, 160), width=6 * S)
    top = 400 - int(350 * level)
    d.rounded_rectangle((36 * S, top * S, 184 * S, 394 * S), radius=18 * S, fill=col + (255,), outline=dark + (255,), width=4 * S)
    return im.resize((220, 420), Image.LANCZOS)


def circle_inset(img, size=440, border=(122, 31, 61)):
    S = 2
    src = img.copy()
    src.thumbnail((size * S * 1.3, size * S * 1.3), Image.LANCZOS)
    canvas = Image.new("RGBA", (size * S, size * S), (255, 255, 255, 255))
    canvas.alpha_composite(src, ((size * S - src.width) // 2, (size * S - src.height) // 2))
    m = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(m).ellipse((4, 4, size * S - 4, size * S - 4), fill=255)
    out = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    out.paste(canvas, (0, 0), m)
    ImageDraw.Draw(out).ellipse((4, 4, size * S - 4, size * S - 4), outline=border + (255,), width=6 * S)
    return out.resize((size, size), Image.LANCZOS)


def build():
    data = json.load(open(HERE / "script.json"))
    sc, t0 = {}, 0.0
    for s in data:
        sc[s["id"]] = RB.Sc(s["id"], s["text"], t0)
        t0 += sc[s["id"]].dur
    bd = B.Board(3, 1)
    add, cam = bd.add, bd.camera
    rings, pulses, glows = [], [], []

    def text(s, x, y, size, color, t, anchor="l", dur=None):
        return add(B.Text(s.upper(), x, y, size, color, t=t, dur=dur, anchor=anchor))

    def sub(s_, x, y, size, color, t):
        a = add(B.Stroke([(x - 2, y - 40), (x - 2, y - 10), (x + 18, y - 10)], color, 3, t=t, dur=0.25))
        return [a, text(s_, x + 26, y, size, color, t + 0.2)]

    def lead(pts, t, color=MAROON, width=3, dur=0.45, arrow=False):
        return add(B.Stroke(B.smooth(pts, 10), color, width, t=t, dur=dur, arrow=arrow))

    def pop(img, x, y, h=None, w=None, t=0.0, dur=0.6):
        return add(B.Pop(img, x, y, h=h, w=w, t=t, dur=dur))

    def panel(x0, y0, x1, y1, col, t):
        return add(B.Panel(x0, y0, x1, y1, col, t=t))

    cam(0, 960, 540, 1.0, 0.1)

    # ======================= HOOK: outside of the heart, 100,000 beats, one spark
    s = sc["hook"]
    hook = [text("The heart's", 960, 70, 40, MAROON, 0.2, "c"), text("Electrical System", 960, 128, 64, MAROON, 0.9, "c"),
            add(B.Stroke([(700, 165), (1220, 162)], MAROON, 4, t=2.0, dur=0.5))]
    hook.append(pop(sv("coeur_09"), 640, 610, h=760, t=0.4, dur=0.8))
    th = s.t("hundred")
    hook += [panel(1180, 300, 1800, 470, PINK, th - 0.3), text("~100,000", 1220, 365, 64, RED_T, th)]
    hook += sub("heartbeats every day", 1220, 430, 42, MAROON, th + 0.7)
    tsp = s.t("spark")
    hook += [pop(bolt(), 1010, 420, h=190, t=tsp - 0.2, dur=0.4), panel(1180, 510, 1800, 680, CREAM, tsp - 0.1),
             text("1 electrical spark", 1220, 575, 50, GOLD_T, tsp)]
    hook += sub("starts every beat", 1220, 640, 42, MAROON, tsp + 0.9)
    tq = s.t("spread")
    hook += [text("how does it spread?", 1220, 800, 52, PURPLE, tq)]

    # ======================= WHY: arm muscle waits for the brain; the heart doesn't
    s = sc["why"]
    tu = s.t("unlike")
    bd.erase(tu - 0.2, hook)
    arm = pop(sv("Bras"), 560, 640, w=820, t=tu + 0.1)
    brain = pop(sv("Cerveau_beau"), 1380, 330, h=380, t=tu + 0.6)
    why1 = [arm, brain, text("skeletal muscle", 420, 520, 46, MAROON, tu + 0.6),
            lead([(1300, 500), (1100, 600), (900, 620)], s.t("signal", 1), PURPLE, 4, 0.7, arrow=True),
            text("signal from the brain", 1130, 760, 44, PURPLE, s.t("signal", 1) + 0.4)]
    tw = s.t("wait")
    hx = pop(sv("coeur_09"), 1500, 760, h=330, t=s.t("heart") - 0.2)
    why1 += [hx, text("heart", 1500, 960, 44, RED_T, s.t("heart"), "c")]
    tm = s.t("makes")
    why1 += [add(B.Stroke([(1230, 160), (1530, 500)], RED_T, 12, t=tm - 0.6, dur=0.3)),
             add(B.Stroke([(1530, 160), (1230, 500)], RED_T, 12, t=tm - 0.35, dur=0.3)),
             pop(bolt(), 1700, 690, h=150, t=tm, dur=0.4), text("makes its own signals", 1300, 1040, 44, GOLD_T, tm + 0.3)]
    tc = s.t("conduction")
    bd.erase(tc - 0.5, why1)
    heart = pop(OP.HEART, 800, 590, h=900, t=tc - 0.2, dur=0.7)
    M = lambda k: heart.map(OP.P[k])
    why2 = [panel(1250, 300, 1820, 470, CREAM, tc), text("conduction system", 1290, 365, 50, GOLD_T, tc + 0.2)]
    why2 += sub("built-in wiring", 1290, 430, 42, MAROON, s.t("wiring", 1))
    tw2 = s.t("wiring", 2)
    for i, w in enumerate(OP.WIRES):
        add(B.Stroke(B.smooth([heart.map(p) for p in w], 8), WIRE, 7, t=tw2 - 0.6 + 0.45 * i, dur=0.8, shadow=WIRE_D))
    routes = [[heart.map(p) for p in OP.WIRES[0]], [heart.map(p) for p in OP.WIRES[1] + OP.WIRES[2][1:]],
              [heart.map(p) for p in OP.WIRES[1] + OP.WIRES[3][1:]]]
    ta, tv = s.t("atria", 1), s.t("ventricles", 1)
    why2 += [text("atria", 160, 300, 56, BLUE_T, ta), text("1st", 160, 360, 40, MAROON, ta + 0.5),
             lead([(300, 290), (430, 330), M("RA")], ta + 0.3, BLUE_T),
             lead([(300, 285), (600, 220), (900, 240), M("LA")], ta + 0.6, BLUE_T),
             text("ventricles", 160, 820, 56, RED_T, tv), text("2nd", 160, 880, 40, MAROON, tv + 0.5),
             lead([(430, 810), (520, 800), M("RV")], tv + 0.3, RED_T),
             lead([(430, 815), (700, 900), (900, 860), M("LV")], tv + 0.6, RED_T)]
    glows += [(ta + 0.2, M("RA"), 1.6, 110), (ta + 0.2, M("LA"), 1.6, 100), (tv + 0.2, M("RV"), 1.8, 120),
              (tv + 0.2, M("LV"), 1.8, 130)]
    pulses += [(routes[0], ta - 0.4, 0.6), (routes[1], tv - 0.5, 0.6), (routes[2], tv - 0.5, 0.6)]

    # ======================= SA NODE: zoom in, inset of pacemaker cells, 60-100 / min
    s = sc["sa"]
    SA = M("SA")
    bd.erase(s.start, why2)
    cam(s.start, SA[0] + 160, SA[1] + 120, 1.9, 1.2)
    tsa = s.t("sinoatrial")
    sa1 = [text("SA node", SA[0] - 150, SA[1] - 40, 40, GOLD_T, tsa + 0.2, "r"),
           text("sinoatrial node", SA[0] - 150, SA[1] + 6, 24, MAROON, s.t("node", 1) + 0.3, "r"),
           lead([(SA[0] - 146, SA[1] - 44), (SA[0] - 60, SA[1] - 30), (SA[0] - 14, SA[1] - 8)], tsa + 0.9, GOLD_T, 3, 0.4)]
    rings += [(tsa, SA, 1.0), (tsa + 1.1, SA, 1.0)]
    tcl = s.t("cluster")
    cam(tcl - 0.3, 960, 540, 1.0, 1.1)
    inset = pop(circle_inset(sv("cellules_coeur"), 440), 1500, 420, h=440, t=tcl + 0.6)
    sa1 += [lead([(SA[0] + 10, SA[1] - 10), (900, 260), (1290, 380)], tcl + 0.4, MAROON, 3, 0.5), inset,
            text("pacemaker cells", 1500, 690, 46, MAROON, tcl + 1.0, "c")]
    tr = s.t("right")
    sa1 += [text("right atrium", 160, 440, 46, BLUE_T, tr), lead([(330, 430), (430, 440), M("RA")], tr + 0.6, BLUE_T)]
    tsv = s.t("superior")
    svc = M("SVC")
    sa1 += [text("superior", 160, 160, 42, BLUE_T, tsv), text("vena cava", 160, 210, 42, BLUE_T, tsv + 0.5),
            lead([(370, 190), (svc[0] - 25, svc[1])], tsv + 1.0, BLUE_T)]
    tpm = s.t("pacemaker")
    bd.erase(tpm - 0.2, [inset] + sa1[3:])
    sa2 = [panel(1250, 260, 1820, 430, CREAM, tpm), text("natural pacemaker", 1290, 330, 50, GOLD_T, tpm + 0.2)]
    sa2 += sub("starts every beat", 1290, 395, 42, MAROON, tpm + 1.0)
    t6 = s.t("sixty")
    sa2 += [panel(1250, 480, 1820, 680, PINK, t6 - 0.3), text("60 - 100", 1290, 560, 70, RED_T, t6)]
    sa2 += sub("times a minute at rest", 1290, 635, 40, MAROON, t6 + 0.8)
    tb = t6
    while tb < s.end - 0.3:
        rings.append((tb, SA, 0.7))
        pulses += [(routes[0], tb, 0.25), (routes[1], tb + 0.3, 0.25), (routes[2], tb + 0.3, 0.25)]
        tb += 0.8

    # ======================= ATRIA contract
    s = sc["atria"]
    bd.erase(s.start, sa1[:3] + sa2)
    tsp = s.t("spreads")
    pulses.append((routes[0], tsp, 1.0))
    rings.append((tsp, SA, 1.4))
    glows += [(tsp + 0.2, M("RA"), 2.6, 120), (tsp + 0.6, M("LA"), 2.2, 110)]
    at = [panel(1250, 300, 1820, 470, SKY, tsp - 0.3), text("signal spreads", 1290, 365, 50, BLUE_T, tsp)]
    at += sub("like a wave across both atria", 1290, 430, 36, MAROON, tsp + 0.8)
    tco = s.t("contract")
    at += [panel(1250, 520, 1820, 690, SKY, tco - 0.3), text("atria contract", 1290, 585, 50, BLUE_T, tco)]
    at += sub("top up the ventricles", 1290, 650, 40, MAROON, s.t("top"))
    glows += [(tco, M("RA"), 1.5, 120), (tco, M("LA"), 1.5, 110)]

    # ======================= AV node: delay
    s = sc["av"]
    AV = M("AV")
    bd.erase(s.start, at)
    cam(s.start, AV[0] + 60, AV[1], 1.8, 1.1)
    pulses.append((routes[0], s.t("signal", 1), 1.2))
    tav = s.t("atrioventricular")
    av1 = [text("AV node", 470, AV[1] - 70, 40, GOLD_T, tav + 0.2, "r"),
           text("atrioventricular node", 470, AV[1] - 25, 22, MAROON, tav + 0.9, "r"),
           lead([(474, AV[1] - 74), (620, AV[1] - 40), (AV[0] - 14, AV[1] - 6)], tav + 0.6, GOLD_T, 3, 0.4),
           text("between atria", 470, AV[1] + 40, 26, MAROON, s.t("sits"), "r"),
           text("and ventricles", 470, AV[1] + 75, 26, MAROON, s.t("sits") + 0.6, "r")]
    rings.append((tav, AV, 1.0))
    td = s.t("delayed")
    cam(td - 0.3, 960, 540, 1.0, 1.1)
    for k in range(6):
        rings.append((td + k * 0.5, AV, 0.45))
    clock = pop(sv("Horloge"), 1500, 380, h=360, t=td + 0.4)
    av2 = [clock, text("short pause", 1500, 610, 50, GOLD_T, td + 0.9, "c")]
    te = s.t("emptying")
    bd.erase(te - 0.3, [clock] + av2[1:] + av1[3:])
    av3 = [panel(1250, 260, 1820, 380, SKY, te - 0.2), text("atria finish emptying", 1280, 330, 44, BLUE_T, te),
           lead([(1535, 395), (1535, 470)], te + 1.0, MAROON, 4, 0.3, arrow=True),
           panel(1250, 490, 1820, 610, PINK, s.t("full") - 0.3), text("ventricles fill up", 1280, 560, 44, RED_T, s.t("full")),
           lead([(1535, 625), (1535, 700)], s.t("squeeze") - 0.3, MAROON, 4, 0.3, arrow=True),
           panel(1250, 720, 1820, 840, PINK, s.t("squeeze") - 0.2), text("then they squeeze", 1280, 790, 44, RED_T, s.t("squeeze"))]
    glows.append((te, M("RA"), 1.6, 120))

    # ======================= His, branches, Purkinje -> lungs & body
    s = sc["his"]
    bd.erase(s.start, av1[:3] + av3)
    V = M("septum")
    cam(s.start, V[0] + 260, V[1] - 40, 1.45, 1.1)
    his = [heart.map(p) for p in OP.WIRES[1]]
    tr_ = s.t("rushes")
    pulses.append((his, tr_, 1.1))
    tb_ = s.t("bundle", 1)
    hb = [text("bundle of His", 1150, 430, 44, GOLD_T, tb_), lead([(1145, 425), (980, 430), his[1]], tb_ + 0.7, GOLD_T)]
    tbr = s.t("branches")
    sp = M("septum")
    hb += [text("right & left", 1150, 560, 42, GOLD_T, tbr - 0.4), text("bundle branches", 1150, 615, 42, GOLD_T, tbr + 0.2),
           lead([(1145, 600), (sp[0] + 10, sp[1] - 40)], tbr + 0.9, GOLD_T)]
    hb += [text("septum", 1150, 730, 42, MAROON, s.t("septum")), lead([(1145, 725), (sp[0] + 8, sp[1] + 20)], s.t("septum") + 0.5)]
    tpk = s.t("purkinje")
    pk = heart.map((462, 610))
    hb += [text("Purkinje fibers", 1150, 860, 44, GOLD_T, tpk + 0.2), lead([(1145, 850), (pk[0] + 8, pk[1])], tpk + 1.0, GOLD_T)]
    pulses += [(routes[1], tpk - 0.4, 2.2), (routes[2], tpk - 0.4, 2.2)]
    tco = s.t("contract")
    glows += [(tco, M("RV"), 2.4, 130), (tco, M("LV"), 2.4, 140)]
    tlu = s.t("lungs")
    cam(tlu - 1.0, 960, 540, 1.0, 1.0)
    bd.erase(tlu - 1.0, hb)
    lungs = pop(sv("poumons_01"), 1520, 300, h=360, t=tlu - 0.3)
    body = pop(sv("Male-silhouette"), 1540, 820, h=420, t=s.t("body") - 0.3)
    hb2 = [lungs, body, text("lungs", 1520, 510, 44, BLUE_T, tlu, "c"), text("body", 1300, 900, 44, RED_T, s.t("body"), "c"),
           lead([M("RV"), (1000, 350), (1340, 300)], tlu - 0.2, BLUE_T, 4, 0.6, arrow=True),
           lead([M("LV"), (1100, 760), (1360, 820)], s.t("body") - 0.4, RED_T, 4, 0.6, arrow=True)]
    for k in range(3):
        tb = tlu + 0.2 + k * 0.9
        pulses += [(routes[1], tb, 0.4), (routes[2], tb, 0.4)]
        glows += [(tb + 0.3, M("RV"), 0.5, 120), (tb + 0.3, M("LV"), 0.5, 130)]

    # ======================= BACKUP pacemakers (page 2)
    s = sc["backup"]
    cam(s.start, 2880, 540, 1.0, 1.1)
    bd.erase(s.start + 1.2, hb2 + [heart])
    X0 = 1920
    bk = [text("backup pacemakers", X0 + 960, 110, 70, MAROON, s.start + 0.6, "c"),
          add(B.Stroke([(X0 + 640, 150), (X0 + 1280, 147)], MAROON, 4, t=s.start + 1.6, dur=0.4))]
    rows = [("SA node", "60 - 100 / min", 1.0, (120, 200, 140), s.start + 1.0, GOLD_T),
            ("AV node", "40 - 60 / min", 0.55, (246, 206, 100), s.t("take"), GOLD_T),
            ("ventricles", "20 - 40 / min", 0.25, (238, 128, 128), s.t("twenty"), RED_T)]
    for i, (name, rate, lvl, col, tt, tc_) in enumerate(rows):
        x = X0 + 420 + i * 540
        bk += [pop(battery(lvl, col), x, 470, h=360, t=tt), text(name, x, 730, 52, tc_, tt + 0.3, "c"),
               text(rate, x, 800, 46, MAROON, tt + 0.9, "c")]
    tf = s.t("fails")
    bk += [add(B.Stroke([(X0 + 250, 300), (X0 + 590, 640)], RED_T, 12, t=tf, dur=0.3)),
           add(B.Stroke([(X0 + 590, 300), (X0 + 250, 640)], RED_T, 12, t=tf + 0.25, dur=0.3)),
           text("fails", X0 + 420, 870, 46, RED_T, tf + 0.5, "c")]
    bk += [panel(X0 + 560, 920, X0 + 1360, 1030, MINT, s.t("slower") - 0.3),
           text("slower, but blood keeps moving", X0 + 960, 990, 44, GREEN_T, s.t("slower"), "c")]

    # ======================= ECG
    s = sc["ecg"]
    bd.erase(s.start, bk)
    te_ = s.t("electrocardiogram")
    man = pop(sv("Male-silhouette"), X0 + 380, 600, h=880, t=s.start + 0.3)
    ec = [man, text("ECG", X0 + 760, 110, 74, MAROON, te_ - 0.6), text("= electrocardiogram", X0 + 920, 110, 50, MAROON, te_)]
    el = sv("electrode_01")
    for i, (ex, ey) in enumerate([(330, 470), (430, 470), (360, 560), (420, 560), (300, 620), (460, 620)]):
        ec.append(pop(el, X0 + ex, ey, h=46, t=te_ + 0.3 + i * 0.12, dur=0.3))
    gx0, gx1, gy0, gy1 = X0 + 780, X0 + 1820, 250, 650
    for i, x in enumerate(range(gx0, gx1 + 1, 40)):
        ec.append(add(B.Stroke([(x, gy0), (x, gy1)], (246, 200, 206), 3 if i % 5 == 0 else 1, t=s.start + 0.6 + i * 0.01, dur=0.25)))
    for i, y in enumerate(range(gy0, gy1 + 1, 40)):
        ec.append(add(B.Stroke([(gx0, y), (gx1, y)], (246, 200, 206), 3 if i % 5 == 0 else 1, t=s.start + 0.6 + i * 0.02, dur=0.3)))
    ec.append(lead([(X0 + 470, 520), (X0 + 620, 450), (gx0 - 10, 450)], te_ + 1.2, PURPLE, 3, 0.5, arrow=True))
    base, A = 520, 260
    pts = [(gx0 + 30 + x * (gx1 - gx0 - 60), base + y * A) for x, y in RB.WAVE]

    def seg(a, b):
        return [p for (x, y), p in zip(RB.WAVE, pts) if a <= x <= b]
    tP, tQ, tT = s.t("wave", 1), s.t("complex"), s.t("wave", 2)
    ec += [add(B.Stroke(seg(0, 0.08), (60, 60, 70), 5, t=te_ + 1.6, dur=0.5)),
           add(B.Stroke(seg(0.08, 0.24), (60, 60, 70), 5, t=tP - 0.3, dur=0.9)),
           add(B.Stroke(seg(0.24, 0.44), (60, 60, 70), 5, t=tQ - 0.4, dur=0.8)),
           add(B.Stroke(seg(0.44, 1.0), (60, 60, 70), 5, t=tT - 0.3, dur=1.4))]
    pP, pR, pT = pts[26], pts[62], pts[120]
    ec += [text("P", pP[0], pP[1] - 50, 60, BLUE_T, tP + 0.6, "c"), text("QRS", pR[0], pR[1] - 30, 60, RED_T, tQ + 0.4, "c"),
           text("T", pT[0], pT[1] - 60, 60, TEAL, tT + 0.8, "c")]
    ec += [panel(gx0, 720, gx1, 1040, LILAC, tP + 0.6)]
    ec += [text("P wave = atria activated", gx0 + 40, 790, 46, BLUE_T, tP + 1.0),
           text("QRS = ventricles activated", gx0 + 40, 880, 46, RED_T, tQ + 0.9),
           text("T wave = ventricles recover", gx0 + 40, 970, 46, TEAL, tT + 1.2)]

    # ======================= NERVES change the pace (page 3)
    s = sc["nerves"]
    X2 = 3840
    cam(s.start, X2 + 960, 540, 1.0, 1.1)
    bd.erase(s.start + 1.2, ec)
    nv = [text("changing the pace", X2 + 960, 110, 70, MAROON, s.start + 0.5, "c"),
          add(B.Stroke([(X2 + 660, 150), (X2 + 1260, 147)], MAROON, 4, t=s.start + 1.4, dur=0.4))]
    tex = s.t("exercise")
    fast_heart = pop(sv("coeur_09"), X2 + 260, 400, h=260, t=tex - 0.3)
    nv += [fast_heart, panel(X2 + 450, 250, X2 + 1820, 560, PINK, tex - 0.2), text("exercise / stress", X2 + 490, 320, 52, RED_T, tex)]
    nv += sub("sympathetic nerves -> faster", X2 + 490, 385, 40, MAROON, s.t("sympathetic"))

    def strip(x0, x1, y, P, t, dur, color):
        out = []
        n = int((x1 - x0) / P)
        for k in range(n):
            for x, yy in RB.WAVE[::4]:
                out.append((x0 + (k + x) * P, y + yy * 90))
        return add(B.Stroke(out, color, 4, t=t, dur=dur))
    nv.append(strip(X2 + 500, X2 + 1780, 490, 120, s.t("sympathetic") + 0.5, 1.8, RED_T))
    trs = s.t("rest")
    slow_heart = pop(sv("coeur_09"), X2 + 260, 780, h=260, t=trs - 0.3)
    nv += [slow_heart, panel(X2 + 450, 630, X2 + 1820, 940, SKY, trs - 0.2), text("rest", X2 + 490, 700, 52, BLUE_T, trs)]
    nv += sub("vagus nerve -> slower", X2 + 490, 765, 40, MAROON, s.t("vagus"))
    nv.append(strip(X2 + 500, X2 + 1780, 870, 300, s.t("vagus") + 0.4, 2.0, BLUE_T))

    # ======================= SUMMARY flow chart
    s = sc["summary"]
    bd.erase(s.start + 0.2, nv)
    sm = [text("summary", X2 + 960, 110, 70, MAROON, s.start + 0.5, "c"),
          add(B.Stroke([(X2 + 780, 150), (X2 + 1140, 147)], MAROON, 4, t=s.start + 1.2, dur=0.4))]
    steps = [("node", 1, "SA node", GOLD_T, CREAM), ("atria", 1, "atria", BLUE_T, SKY), ("node", 2, "AV node", GOLD_T, CREAM),
             ("bundle", 1, "bundle of His", GOLD_T, CREAM), ("branches", 1, "bundle branches", GOLD_T, CREAM),
             ("purkinje", 1, "Purkinje fibers", GOLD_T, CREAM), ("ventricles", 1, "ventricles", RED_T, PINK)]
    pos = [(X2 + 260, 330), (X2 + 720, 330), (X2 + 1180, 330), (X2 + 1640, 330), (X2 + 1640, 580), (X2 + 1180, 580), (X2 + 720, 580)]
    for i, ((w, n, name, col, bg), (x, y)) in enumerate(zip(steps, pos)):
        tt = s.t(w, n) - 0.2
        bw, bh = 200, 62
        sm += [panel(x - bw, y - bh, x + bw, y + bh, bg, tt), text(name, x, y + 12, 44 if len(name) < 12 else 38, col, tt + 0.2, "c", dur=0.5)]
        if i:
            px_, py_ = pos[i - 1]
            if py_ == y:
                sgn = 1 if x > px_ else -1
                a = [(px_ + sgn * (bw + 8), y), (x - sgn * (bw + 8), y)]
            else:
                a = [(x, py_ + bh + 8), (x, y - bh - 8)]
            sm.append(add(B.Stroke(a, MAROON, 4, t=tt - 0.25, dur=0.25, arrow=True)))
    tsk = s.t("spark")
    sm += [pop(bolt(), X2 + 180, 760, h=120, t=tsk), text("one spark, perfectly timed", X2 + 250, 775, 46, GOLD_T, tsk + 0.3)]
    tn = s.t("next")
    sm += [panel(X2 + 1000, 700, X2 + 1880, 900, LILAC, tn), text("next video", X2 + 1440, 770, 46, PURPLE, tn + 0.3, "c"),
           text("what happens in a heart attack?", X2 + 1440, 850, 48, RED_T, tn + 1.0, "c")]

    bd.fx.append(lambda crop, ctx, t: OP.fx(crop, ctx, t, rings, pulses, glows))
    bd.total = t0
    return bd, sc


CREDIT = "Some illustrations: Servier Medical Art (smart.servier.com), CC BY 4.0"


def credit(frame):
    d = ImageDraw.Draw(frame)
    d.text((24, 1046), CREDIT, font=B.hfont(22), fill=(160, 160, 170))
    return frame


def render(out="heart_electrical_osmosis.mp4"):
    import render_ecg as RE
    bd, sc = build()
    vid = HERE / "osmf_video_only.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", str(vid)], stdin=subprocess.PIPE)
    for f in range(int(round(RE.INTRO_DUR * FPS))):
        ff.stdin.write(RE.intro_frame(f / FPS).tobytes())
    for f in range(int(bd.total * FPS)):
        ff.stdin.write(credit(bd.frame(f / FPS)).tobytes())
        if f % 600 == 0:
            print(f"  t={f / FPS:.0f}s", flush=True)
    ff.stdin.close()
    ff.wait()
    RE.intro_audio(HERE / "audio_intro.wav")
    with open(HERE / "osmf_audio.txt", "w") as fh:
        fh.write(f"file '{HERE / 'audio_intro.wav'}'\n")
        for s in sc.values():
            fh.write(f"file '{s.audio}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(HERE / "osmf_audio.txt"),
                    "-c", "pcm_s16le", str(HERE / "osmf_voice.wav")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(HERE / "osmf_voice.wav"), "-i",
                    str(HERE.parent / "clips" / "clip1.mp4"), "-filter_complex",
                    "[2:v]trim=0:3.4,setpts=PTS-STARTPTS,fps=30,scale=1920:1080,format=yuva420p,"
                    "fade=t=in:st=0:d=0.3:alpha=1,fade=t=out:st=3.0:d=0.4:alpha=1,setpts=PTS+3.6/TB[c];"
                    "[0:v][c]overlay=eof_action=pass[v]", "-map", "[v]", "-map", "1:a", "-c:v", "libx264",
                    "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", str(HERE / out)], check=True)
    print("done ->", HERE / out)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        bd, _ = build()
        for t in sorted(float(x) for x in sys.argv[2:]):
            credit(bd.frame(t)).save(HERE / f"f_{t:06.1f}.png")
        print("ok", round(bd.total, 1))
    else:
        render()
