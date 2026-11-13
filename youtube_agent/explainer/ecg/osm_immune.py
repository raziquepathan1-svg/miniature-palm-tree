"""Immune system video (fact-checked 13 Nov 2026) + 2 story Shorts.

    python3 osm_immune.py [stills] | short 1|2 [stills]
Env: EP_DIR (default ../immune), OUT_DIR.
"""
import math
import os
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "immune")))
OUT = Path(os.environ.get("OUT_DIR", str(HERE)))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_preview as OP  # noqa: E402
import osm_brain as OB  # noqa: E402
import osm_neuron as NU  # noqa: E402
import osm_digest as DG  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OB.PINK, OB.LILAC, OB.CREAM, OB.MINT, OB.SKY
PW, PH = 1920, 1080
SHORT_TITLES = {1: "Who Makes Your Finger Red", 2: "How Does Your Body Remember"}
SHORT_Q = {1: "So who is causing it?", 2: "So what cells keep the memory?"}
S = 3
new, done, tube = DG.new, DG.done, DG.tube
OL = (90, 70, 90, 255)
GERM = (110, 190, 90, 255)


def germs(d, pts, r=14):
    for x, y in pts:
        d.ellipse(((x - r) * S, (y - r * 0.6) * S, (x + r) * S, (y + r * 0.6) * S), fill=GERM, outline=(50, 120, 50, 255), width=3 * S)


def finger_pic(red=False):
    W, H = 560, 760
    im, d = new(W, H)
    col = (245, 150, 140, 255) if red else (248, 214, 190, 255)
    d.rounded_rectangle((150 * S, 80 * S, 410 * S, 760 * S), radius=130 * S, fill=col, outline=(170, 110, 90, 255), width=6 * S)
    d.line([(160 * S, 250 * S), (400 * S, 300 * S)], fill=(190, 40, 50, 255), width=10 * S)
    germs(d, [(120, 200), (80, 280), (460, 230), (500, 320), (140, 340)])
    if red:
        for a in range(5):
            r = 170 + a * 36
            d.arc(((280 - r) * S, (275 - r) * S, (280 + r) * S, (275 + r) * S), 200 + a * 4, 340 - a * 4, fill=(230, 80, 60, 150), width=5 * S)
    return done(im, W, H)


def skin_pic():
    W, H = 900, 520
    im, d = new(W, H)
    for r in range(3):
        for c in range(10):
            x = 30 + c * 85 + (40 if r % 2 else 0)
            d.rounded_rectangle((x * S, (240 + r * 85) * S, (x + 80) * S, (240 + r * 85 + 80) * S), radius=14 * S, fill=(245, 185, 165, 255), outline=(170, 110, 90, 255), width=4 * S)
    random.seed(4)
    germs(d, [(90, 70), (250, 130), (420, 60), (600, 120), (780, 70), (330, 190), (690, 190)])
    for x in (90, 330, 600):
        d.line([(x * S, 150 * S), (x * S, 230 * S)], fill=(200, 60, 60, 255), width=5 * S)
        d.polygon([((x - 18) * S, 215 * S), ((x + 18) * S, 215 * S), (x * S, 245 * S)], fill=(200, 60, 60, 255))
    return done(im, W, H)


def cell(d, cx, cy, r, body, nuc, kind="round", ol=OL):
    d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=body, outline=ol, width=5 * S)
    if kind == "lobes":
        for dx, dy in ((-0.3, -0.2), (0.25, -0.3), (0.0, 0.3)):
            d.ellipse(((cx + dx * r - r * 0.32) * S, (cy + dy * r - r * 0.32) * S, (cx + dx * r + r * 0.32) * S, (cy + dy * r + r * 0.32) * S), fill=nuc)
    elif kind == "granules":
        d.ellipse(((cx - r * 0.45) * S, (cy - r * 0.45) * S, (cx + r * 0.45) * S, (cy + r * 0.45) * S), fill=nuc)
        for k in range(10):
            a = k * 36
            x = cx + r * 0.75 * math.cos(math.radians(a)); y = cy + r * 0.75 * math.sin(math.radians(a))
            d.ellipse(((x - r * 0.08) * S, (y - r * 0.08) * S, (x + r * 0.08) * S, (y + r * 0.08) * S), fill=(120, 60, 90, 255))
    else:
        d.ellipse(((cx - r * 0.5) * S, (cy - r * 0.5) * S, (cx + r * 0.5) * S, (cy + r * 0.5) * S), fill=nuc)


def one_cell(body, nuc, kind="round", r=130, tint=None):
    W = r * 2 + 40
    im, d = new(W, W)
    cell(d, W // 2, W // 2, r, body, nuc, kind)
    return done(im, W, W)


def neutrophil_pic():
    W, H = 640, 400
    im, d = new(W, H)
    cell(d, 200, 200, 150, (235, 225, 245, 255), (140, 90, 190, 255), "lobes")
    germs(d, [(160, 120), (230, 250)], 22)
    germs(d, [(420, 90), (520, 170), (480, 300), (580, 250)], 18)
    return done(im, W, H)


def y_pic():
    W, H = 220, 260
    im, d = new(W, H)
    col = (120, 100, 210, 255)
    d.line([(110 * S, 250 * S), (110 * S, 130 * S)], fill=col, width=22 * S)
    d.line([(110 * S, 130 * S), (40 * S, 30 * S)], fill=col, width=22 * S)
    d.line([(110 * S, 130 * S), (180 * S, 30 * S)], fill=col, width=22 * S)
    return done(im, W, H)


def node_pic():
    W, H = 640, 420
    im, d = new(W, H)
    d.ellipse((120 * S, 90 * S, 520 * S, 330 * S), fill=(205, 225, 175, 255), outline=(100, 130, 70, 255), width=6 * S)
    tube(d, [(0, 210), (130, 210)], (230, 200, 90, 255), 16)
    tube(d, [(510, 210), (640, 210)], (230, 200, 90, 255), 16)
    for x, y in ((230, 170), (300, 250), (380, 180), (430, 260), (260, 215), (350, 215)):
        d.ellipse(((x - 18) * S, (y - 18) * S, (x + 18) * S, (y + 18) * S), fill=(130, 100, 200, 255))
    return done(im, W, H)


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
    Y = PH

    # ---------------- STORY (A)
    s = sc["story"]
    st = [pop(finger_pic(False), 460, 540, h=860, t=0.3), text("a cut finger", 1330, 170, 76, RED_T, s.t("cut") - 0.3, "c"), text("germs slip in", 1330, 330, 66, GREEN_T, s.t("germs") - 0.4, "c"),
          text("red - warm - swollen", 1330, 520, 70, GOLD_T, s.t("red") - 0.5, "c"), text("who is doing it?", 1330, 800, 90, PURPLE, s.t("who") - 0.3, "c")]

    # ---------------- OVERVIEW (B)
    s = sc["overview"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, st)
    X = PW
    ov = title("THE IMMUNE SYSTEM", X + 960, 120, s.start + 0.3) + [
        panel(X + 160, 260, X + 900, 820, PINK, s.t("innate") - 0.5), text("INNATE", X + 530, 460, 96, RED_T, s.t("innate") - 0.2, "c"), text("FAST", X + 530, 600, 100, GOLD_T, s.t("fast") - 0.3, "c"),
        panel(X + 1020, 260, X + 1760, 820, SKY, s.t("adaptive") - 0.5), text("ADAPTIVE", X + 1390, 460, 90, BLUE_T, s.t("adaptive") - 0.2, "c"), text("slower, precise", X + 1390, 600, 70, GREEN_T, s.t("precise") - 0.8, "c")]

    # ---------------- BARRIER (C)
    s = sc["barrier"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ov)
    X = 2 * PW
    ba = [pop(skin_pic(), X + 560, 520, w=960, t=s.start + 0.3), text("SKIN = a big barrier", X + 1500, 260, 70, GOLD_T, s.t("skin") - 0.3, "c"),
          text("airway + gut linings", X + 1500, 480, 62, BLUE_T, s.t("linings") - 0.5, "c"), text("make MUCUS", X + 1500, 590, 70, GREEN_T, s.t("mucus") - 0.4, "c"), text("help block germs", X + 1500, 740, 56, MAROON, s.t("block") - 0.8, "c")]

    # ---------------- INNATE (D)
    s = sc["innate"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, ba)
    inn = [pop(neutrophil_pic(), 420, Y + 400, w=760, t=s.start + 0.3), text("NEUTROPHILS", 1400, Y + 190, 80, PURPLE, s.t("neutrophils") - 0.3, "c"), text("first cellular responders", 1400, Y + 290, 54, MAROON, s.t("first") - 0.5, "c"),
           text("swallow bacteria = PHAGOCYTOSIS", 1350, Y + 420, 52, GREEN_T, s.t("phagocytosis") - 1.2, "c"),
           pop(one_cell((245, 215, 190, 255), (150, 90, 70, 255), "round", 120), 250, Y + 840, h=250, t=s.t("macrophages") - 0.9), text("MACROPHAGES", 640, Y + 800, 56, GOLD_T, s.t("macrophages") - 0.4, "l"),
           pop(one_cell((215, 235, 245, 255), (70, 130, 190, 255), "granules", 120), 1130, Y + 840, h=250, t=s.t("killer") - 1.0), text("NATURAL KILLER", 1470, Y + 800, 52, BLUE_T, s.t("killer") - 0.5, "l")]

    # ---------------- INFLAMMATION (E)
    s = sc["inflammation"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, inn)
    X = PW
    inf = [pop(finger_pic(True), X + 460, Y + 540, h=860, t=s.start + 0.3), title("INFLAMMATION", X + 1330, Y + 120, s.t("inflammation") - 0.4)[0] if False else text("INFLAMMATION", X + 1330, Y + 150, 90, RED_T, s.t("inflammation") - 0.4, "c"),
           text("redness", X + 1330, Y + 340, 70, RED_T, s.t("redness") - 0.4, "c"), text("heat", X + 1330, Y + 450, 70, GOLD_T, s.t("heat") - 0.4, "c"),
           text("swelling", X + 1330, Y + 560, 70, BLUE_T, s.t("swelling") - 0.4, "c"), text("pain", X + 1330, Y + 670, 70, PURPLE, s.t("pain") - 0.4, "c"),
           text("= your immune system at work", X + 1250, Y + 860, 44, GREEN_T, s.t("work") - 2.0, "c")]

    # ---------------- ADAPTIVE (F)
    s = sc["adaptive"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, inf)
    X = 2 * PW
    ad = [pop(node_pic(), X + 520, Y + 480, w=800, t=s.start + 0.3), text("LYMPH NODE", X + 520, Y + 740, 66, GREEN_T, s.t("lymph") - 0.3, "c"),
          text("dendritic cells carry", X + 1450, Y + 220, 58, GOLD_T, s.t("dendritic") - 0.4, "c"), text("pieces of the germ", X + 1450, Y + 310, 58, GOLD_T, s.t("pieces") - 0.4, "c"),
          text("alert T CELLS", X + 1450, Y + 470, 80, PURPLE, s.t("alert") - 0.3, "c"), text("takes DAYS - very specific", X + 1450, Y + 700, 58, BLUE_T, s.t("days") - 0.9, "c")]

    # ---------------- T CELLS (A)
    s = sc["tcells"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, ad)
    tc = [pop(one_cell((225, 215, 245, 255), (110, 80, 190, 255), "round", 130), 360, 480, h=340, t=s.start + 0.3), text("HELPER T CELL", 360, 770, 62, PURPLE, s.t("helper") - 0.3, "c"), text("activates other cells", 360, 850, 44, MAROON, s.t("messengers") - 0.8, "c"),
          pop(one_cell((235, 200, 205, 255), (190, 60, 80, 255), "round", 130), 1000, 480, h=340, t=s.t("cytotoxic") - 0.9), text("CYTOTOXIC T CELL", 1000, 770, 58, RED_T, s.t("cytotoxic") - 0.3, "c"), text("destroys infected cells", 1000, 850, 44, MAROON, s.t("destroy") - 0.6, "c")]

    # ---------------- B CELLS (B)
    s = sc["bcells"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, tc)
    X = PW
    bc = [pop(one_cell((215, 235, 225, 255), (60, 150, 110, 255), "round", 130), X + 420, 520, h=420, t=s.start + 0.3)]
    for k, (dx, dy) in enumerate(((140, -200), (250, -90), (260, 70), (160, 190))):
        bc.append(pop(y_pic(), X + 420 + dx, 520 + dy, h=120, t=s.t("antibodies") - 0.3 + k * 0.15))
    bc += [text("B CELLS", X + 1450, 240, 90, GREEN_T, s.t("cells") - 0.3, "c"), text("make ANTIBODIES", X + 1450, 400, 80, PURPLE, s.t("antibodies") - 0.3, "c"),
           text("proteins that attach", X + 1450, 600, 58, MAROON, s.t("attach") - 0.6, "c"), text("to a specific germ", X + 1450, 690, 58, MAROON, s.t("specific") - 0.6, "c")]

    # ---------------- MEMORY (C)
    s = sc["memory"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, bc)
    X = 2 * PW
    me = [pop(one_cell((245, 225, 150, 255), (200, 150, 30, 255), "round", 130), X + 380, 420, h=300, t=s.t("memory") - 0.5), pop(one_cell((245, 225, 150, 255), (200, 150, 30, 255), "round", 130), X + 700, 420, h=300, t=s.t("memory") - 0.2),
          text("MEMORY CELLS", X + 540, 640, 70, GOLD_T, s.t("memory") - 0.3, "c"), text("faster response next time", X + 540, 740, 48, MAROON, s.t("faster") - 0.6, "c"),
          text("VACCINES", X + 1450, 240, 90, BLUE_T, s.t("vaccines") - 0.3, "c"), text("show small pieces of a germ", X + 1450, 380, 52, MAROON, s.t("pieces") - 0.6, "c"),
          text("protection may last", X + 1450, 620, 56, GREEN_T, s.t("months") - 1.0, "c"), text("months, years, a lifetime", X + 1450, 710, 56, GREEN_T, s.t("lifetime") - 1.2, "c")]

    # ---------------- RECAP (D)
    s = sc["recap"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, me)
    rp = title("remember 3 things", 960, Y + 100, s.start + 0.4)
    for w, a, b, col, tc_, x in (("barriers", "barriers + innate", "cells respond first", PINK, RED_T, 400), ("slower", "T + B cells: slower", "but very specific", CREAM, GOLD_T, 960), ("memory", "memory cells", "respond faster next time", SKY, BLUE_T, 1520)):
        tw2 = s.t(w) - 0.3
        rp += [panel(x - 265, Y + 220, x + 265, Y + 600, col, tw2 - 0.2), text(a, x, Y + 360, 40, tc_, tw2, "c"), text(b, x, Y + 470, 36, MAROON, tw2 + 0.6, "c")]
    tn = s.t("skin") - 0.8
    rp += [panel(200, Y + 720, 1720, Y + 890, LILAC, tn - 0.3), text("next: the skin", 960, Y + 820, 56, PURPLE, tn, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def build_short(n):
    sc, t0 = load(EP / f"short{n}")
    bd = B.Board(3, 2)
    pops, glows = [], []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    cam = bd.camera
    A, Bc, C = (960, 540), (PW + 960, 540), (2 * PW + 960, 540)
    cam(0, *A, 1.0, 0.1)
    if n == 1:
        s = sc["case"]
        a = [pop(finger_pic(False), 460, 540, h=860, t=0.3), text("a cut finger", 1380, 200, 80, RED_T, s.t("cut") - 0.3, "c"), text("germs slip in", 1380, 380, 70, GREEN_T, s.t("germs") - 0.4, "c"),
             text("red - warm - swollen", 1380, 640, 72, GOLD_T, s.t("red") - 0.6, "c")]
        s = sc["turn"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(finger_pic(True), X + 460, 540, h=860, t=s.start + 0.3), text("the infection itself?", X + 1380, 240, 68, MAROON, s.t("infection") - 0.4, "c"), text("not exactly", X + 1380, 400, 80, RED_T, s.t("exactly") - 0.4, "c"),
             text("caused on PURPOSE", X + 1380, 620, 70, PURPLE, s.t("purpose") - 0.8, "c"), text("?", X + 1380, 880, 200, GOLD_T, s.t("what") - 0.2, "c")]
    else:
        s = sc["case"]
        a = [pop(one_cell((245, 225, 150, 255), (200, 150, 30, 255), "round", 130), 520, 540, h=520, t=0.3), text("months, years,", 1400, 280, 80, GREEN_T, s.t("months") - 0.6, "c"), text("even a lifetime", 1400, 400, 80, GREEN_T, s.t("lifetime") - 0.8, "c"),
             text("after infections and vaccines", 1400, 640, 52, MAROON, s.t("vaccines") - 0.8, "c")]
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [text("no notebook inside you", X + 960, 300, 90, MAROON, s.t("notebook") - 0.4, "c"), text("so how does it remember?", X + 960, 560, 82, PURPLE, s.t("remember") - 0.9, "c")]
        s = sc["clue"]
        cam(s.start, *C, 1.0, 1.0)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        c = [pop(one_cell((245, 225, 150, 255), (200, 150, 30, 255), "round", 130), X + 520, 540, h=420, t=s.start + 0.3), text("special cells keep it", X + 1400, 320, 72, GOLD_T, s.t("special") - 0.5, "c"),
             text("what are they?", X + 1400, 520, 90, PURPLE, s.t("what") - 0.3, "c"), text("?", X + 1400, 820, 220, GOLD_T, s.t("what") - 0.1, "c")]

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
    board = NU.render_board(bd, sc, f"imm_story{n}")
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
    ov = OUT / f"imm_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"imm_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["immune"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "immune", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"imm_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"ishort{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "imm", intro=True)
        f.replace(OUT / "final_imm.mp4")
        print("done ->", OUT / "final_imm.mp4")
