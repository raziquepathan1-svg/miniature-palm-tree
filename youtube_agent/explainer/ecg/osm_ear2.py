"""EAR - cinematic version (owner images art/ear/shot1-6, fact-checked script ../ear). Not queued until final.

    python3 osm_ear2.py [stills] | short 1|2 [stills]
Env: EP_DIR (default ../ear), OUT_DIR.
"""
import math
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "ear")))
OUT = Path(os.environ.get("OUT_DIR", str(HERE)))
ART = HERE.parent / "art" / "ear"
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_brain as OB  # noqa: E402
import osm_neuron as NU  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
PINK, LILAC, CREAM, MINT = OB.PINK, OB.LILAC, OB.CREAM, OB.MINT
PW, PH = 1920, 1080
K = 1920 / 1376
IH = 768 * K
SHORT_TITLES = {1: "The Smallest Bone", 2: "Why You Feel Dizzy"}
SHORT_Q = {1: "So what is the smallest bone?", 2: "So which part makes you dizzy?"}
SOUND, VIB, FLUID, SIG = (230, 100, 145), (245, 180, 40), (70, 160, 230), (250, 200, 40)


def shot(n):
    return Image.open(ART / f"shot{n}.png").convert("RGBA")


def P(ox, oy, x, y):
    """image pixel (of a 1376x768 shot placed full-page at page origin ox, oy) -> board units"""
    return (ox + x * K, oy + PH / 2 - IH / 2 + y * K)


def ellipse_pts(ox, oy, cx, cy, rx, ry, a0=0, turns=1.0, n=48):
    return [P(ox, oy, cx + rx * math.cos(a0 + 2 * math.pi * turns * i / n), cy + ry * math.sin(a0 + 2 * math.pi * turns * i / n)) for i in range(n + 1)]


def spiral_pts(ox, oy, cx, cy, r0, r1, turns=2.6, n=90):
    return [P(ox, oy, cx + (r0 + (r1 - r0) * i / n) * math.cos(math.pi + 2 * math.pi * turns * i / n),
              cy + (r0 + (r1 - r0) * i / n) * math.sin(math.pi + 2 * math.pi * turns * i / n)) for i in range(n + 1)]


class Cine:
    """camera + animation helpers (anatomy-unfolded-cinematic skill)."""
    def __init__(self, bd):
        self.bd, self.movers, self.glows = bd, [], []

    def flow(self, pts, t0, t1, period=2.4, col=SOUND, r=13, n=3, smooth=True):
        self.movers.append((B.smooth(pts, 10) if smooth else pts, t0, t1, period, col, r, n))

    def glow(self, t0, p, dur=2.4, r=70, col=SIG):
        self.glows.append((t0, p, dur, r, col))

    def push(self, s, page, lead=1.2, tail=0.5):
        self.bd.camera(s.start + lead, page[0], page[1], 1.04, max(1.0, s.dur - lead - tail))

    def dive_out(self, s, p, z=4.0, d=1.5):
        self.bd.camera(s.start + s.dur - d - 0.1, p[0], p[1], z, d)

    def land(self, s, page):
        self.bd.camera(s.start, page[0], page[1], 0.7, 0)
        self.bd.camera(s.start + 0.05, page[0], page[1], 1.0, 1.1)

    def fx(self, crop, ctx, t):
        lay = None
        for t0, p, d_, r, col in self.glows:
            if t0 <= t <= t0 + d_:
                x = (t - t0) / d_
                a = min(1, x / 0.2) * min(1, (1 - x) / 0.3) * (0.75 + 0.25 * math.sin(t * 6))
                if lay is None:
                    lay = Image.new("RGBA", crop.size, (0, 0, 0, 0))
                cx, cy = ctx.px(p)
                rr = r * B.BS
                ImageDraw.Draw(lay).ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=col + (int(120 * a),))
        if lay is not None:
            crop.alpha_composite(lay.filter(ImageFilter.GaussianBlur(18)))
        d = ImageDraw.Draw(crop)
        for pts, t0, t1, per, col, r, n in self.movers:
            if not (t0 <= t <= t1):
                continue
            for k in range(n):
                if t - t0 < k * per / n:
                    continue
                ph = ((t - t0) / per + k / n) % 1.0
                cx, cy = ctx.px(B.partial_pts(pts, max(ph, 0.02))[-1])
                a = min(1.0, ph / 0.12, (1 - ph) / 0.12)
                rr = r * B.BS * (0.6 + 0.4 * a)
                d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=col, outline=(70, 60, 60), width=max(1, int(2 * B.BS)))


def load(d):
    return NU.load(d)


def build():
    sc, t0 = load(EP)
    bd = B.Board(3, 2)
    pops = []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    cv = Cine(bd)
    cam = bd.camera
    A, Bc, C = (960, 540), (PW + 960, 540), (2 * PW + 960, 540)
    D, E, Fp = (960, PH + 540), (PW + 960, PH + 540), (2 * PW + 960, PH + 540)
    cam(0, *A, 1.0, 0.1)
    Y = PH

    # ---------------- STORY (A): the whole human, then dive into his ear
    s = sc["story"]
    st = [pop(shot(1), 960, 540, w=1920, t=0.0, dur=0.4), text("sound = moving air", 400, 300, 54, GOLD_T, s.t("moving") - 0.4, "c"),
          text("the SMALLEST bone", 1530, 300, 58, RED_T, s.t("smallest") - 0.4, "c"), text("how?", 1530, 560, 130, PURPLE, s.t("how") - 0.4, "c"),
          text("follow the sound", 400, 760, 58, GREEN_T, s.t("follow") - 1.6, "c")]
    ear_pt = P(0, 0, 724, 120)
    cv.flow([(ear_pt[0] + 330, ear_pt[1] - 20), (ear_pt[0] + 170, ear_pt[1] - 5), (ear_pt[0] + 10, ear_pt[1])], s.t("sound") - 0.2, s.start + s.dur, 1.6, SOUND, 10, 3)
    cv.dive_out(s, ear_pt, 5.0, 2.0)

    # ---------------- OVERVIEW (B): the whole ear
    s = sc["overview"]
    cv.land(s, Bc)
    bd.erase(s.start + 0.8, st)
    X = PW
    ov = [pop(shot(2), X + 960, 540, w=1920, t=s.start), text("OUTER ear", X + 1600, 300, 66, GOLD_T, s.t("outer") - 0.3, "c"),
          text("MIDDLE ear", X + 1600, 460, 66, RED_T, s.t("middle") - 0.3, "c"), text("INNER ear", X + 1600, 620, 66, PURPLE, s.t("inner") - 0.4, "c")]
    cv.glow(s.t("outer") - 0.2, P(X, 0, 190, 360), 1.8, 120, VIB)
    cv.glow(s.t("middle") - 0.2, P(X, 0, 545, 330), 1.8, 80, (235, 90, 90))
    cv.glow(s.t("inner") - 0.2, P(X, 0, 690, 330), 1.8, 110, (150, 110, 220))
    cv.push(s, Bc)

    # ---------------- OUTER (C): sound travels down the canal
    s = sc["outer"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ov)
    X = 2 * PW
    ou = [pop(shot(2), X + 960, 540, w=1920, t=s.start + 0.2), text("PINNA collects sound", X + 1590, 260, 42, GOLD_T, s.t("pinna") - 0.4, "c"),
          text("EAR CANAL", X + 1600, 420, 64, BLUE_T, s.t("canal") - 0.3, "c"), text("EARDRUM vibrates", X + 1600, 580, 58, RED_T, s.t("eardrum") - 0.3, "c")]
    cv.flow([P(X, 0, x, y) for x, y in ((120, 330), (230, 370), (350, 385), (450, 385), (530, 385))], s.t("collects") - 0.2, s.start + s.dur, 1.8, SOUND, 12, 4)
    cv.glow(s.t("vibrates") - 0.3, P(X, 0, 540, 385), 3.0, 60, (235, 90, 90))
    cv.push(s, C, 1.0, 1.9)
    cv.dive_out(s, P(X, 0, 548, 330), 4.0, 1.5)

    # ---------------- MIDDLE (D): three tiny bones
    s = sc["middle"]
    cv.land(s, D)
    bd.erase(s.start + 0.8, ou)
    mi = [pop(shot(3), 960, Y + 540, w=1920, t=s.start), text("MALLEUS", 1600, Y + 200, 60, GOLD_T, s.t("malleus") - 0.3, "c"),
          text("INCUS", 1600, Y + 320, 60, PURPLE, s.t("incus") - 0.3, "c"), text("STAPES", 1600, Y + 440, 64, RED_T, s.t("stapes") - 0.3, "c"),
          text("smallest bone in the body", 1600, Y + 560, 40, RED_T, s.t("smallest") - 0.5, "c"),
          text("EUSTACHIAN TUBE", 1600, Y + 760, 52, BLUE_T, s.t("eustachian") - 0.4, "c"), text("equalizes pressure", 1600, Y + 860, 44, MAROON, s.t("pressure") - 0.9, "c")]
    cv.flow([P(0, Y, x, y) for x, y in ((390, 500), (470, 470), (500, 330), (430, 230), (520, 220), (560, 330), (600, 410), (700, 410), (770, 420))],
            s.t("vibrations") - 0.2, s.start + s.dur, 2.2, VIB, 13, 3)
    cv.glow(s.t("malleus") - 0.2, P(0, Y, 420, 220), 1.8, 85, VIB)
    cv.glow(s.t("incus") - 0.2, P(0, Y, 525, 220), 1.8, 85, (150, 110, 220))
    cv.glow(s.t("stapes") - 0.2, P(0, Y, 700, 410), 4.0, 80, (235, 90, 90))
    cv.push(s, D, 1.0, 1.9)
    cv.dive_out(s, P(0, Y, 790, 420), 4.0, 1.5)

    # ---------------- INNER (E): the cochlea, fluid waves
    s = sc["inner"]
    cv.land(s, E)
    bd.erase(s.start + 0.8, mi)
    X = PW
    ie = [pop(shot(4), X + 960, Y + 540, w=1920, t=s.start), text("COCHLEA", X + 1640, Y + 200, 84, GOLD_T, s.t("cochlea") - 0.3, "c"),
          text("fluid-filled snail", X + 1640, Y + 330, 50, MAROON, s.t("snail") - 0.6, "c"),
          text("stapes pushes fluid", X + 1640, Y + 560, 48, RED_T, s.t("pushes") - 0.5, "c"), text("= WAVES", X + 1640, Y + 680, 76, BLUE_T, s.t("waves") - 0.4, "c")]
    cv.flow(spiral_pts(X, Y, 705, 375, 215, 25), s.t("pushes") - 0.2, s.start + s.dur, 2.6, FLUID, 12, 4)
    cv.glow(s.t("cochlea") - 0.2, P(X, Y, 705, 375), 2.0, 160, VIB)
    cv.push(s, E, 1.0, 1.9)
    cv.dive_out(s, P(X, Y, 705, 375), 4.0, 1.5)

    # ---------------- HAIR (F): hair cells -> nerve signals
    s = sc["hair"]
    cv.land(s, Fp)
    bd.erase(s.start + 0.8, ie)
    X = 2 * PW
    ha = [pop(shot(5), X + 960, Y + 540, w=1920, t=s.start), text("HAIR CELLS", X + 1530, Y + 200, 76, PURPLE, s.t("hair") - 0.3, "c"),
          text("vibrations -> signals", X + 1530, Y + 330, 50, GOLD_T, s.t("electrical") - 0.6, "c"),
          text("AUDITORY NERVE", X + 1530, Y + 520, 60, RED_T, s.t("auditory") - 0.4, "c"), text("-> to the brain", X + 1530, Y + 610, 50, MAROON, s.t("brain") - 0.6, "c"),
          text("mystery solved!", X + 1530, Y + 820, 76, GREEN_T, s.t("answer") - 0.6, "c")]
    for i, cx in enumerate((205, 320, 440, 560, 690)):
        cv.glow(s.t("hair") - 0.2 + 0.15 * i, P(X, Y, cx, 230), 1.6, 60, (170, 120, 230))
        cv.flow([P(X, Y, x, y) for x, y in ((cx, 560), (cx - 20, 640), (max(140, cx - 140), 690), (130, 705))], s.t("electrical") - 0.2 + 0.2 * i, s.start + s.dur, 1.8, SIG, 11, 1)
    cv.push(s, Fp)

    # ---------------- BALANCE (A): semicircular canals
    s = sc["balance"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, ha)
    ba = [pop(shot(6), 960, 540, w=1920, t=s.start + 0.2), text("SEMICIRCULAR CANALS", 1520, 220, 50, PURPLE, s.t("semicircular") - 0.4, "c"),
          text("= BALANCE", 1520, 340, 70, GOLD_T, s.t("balance") - 0.4, "c"), text("spin... fluid keeps moving", 1520, 560, 44, MAROON, s.t("spin") - 0.4, "c"),
          text("= DIZZY", 1520, 720, 110, RED_T, s.t("dizzy") - 0.6, "c")]
    cv.flow(ellipse_pts(0, 0, 330, 390, 170, 190), s.t("spin") - 0.3, s.start + s.dur, 2.0, FLUID, 12, 3)
    cv.flow(ellipse_pts(0, 0, 485, 245, 62, 160), s.t("spin") - 0.1, s.start + s.dur, 1.7, FLUID, 11, 2)
    cv.flow(ellipse_pts(0, 0, 410, 412, 140, 40), s.t("spin") + 0.1, s.start + s.dur, 1.5, FLUID, 10, 2)
    cv.push(s, A)

    # ---------------- CARE (B)
    s = sc["care"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, ba)
    X = PW
    ca = [pop(shot(5), X + 960, 540, w=1920, t=s.start + 0.2), text("hair cells do NOT regrow", X + 1530, 200, 46, RED_T, s.t("regenerate") - 0.5, "c"),
          text("damage = permanent loss", X + 1530, 310, 44, MAROON, s.t("permanent") - 0.5, "c"), text("protect from loud noise", X + 1530, 470, 46, GREEN_T, s.t("protecting") - 0.4, "c"),
          panel(X + 1150, 600, X + 1910, 740, MINT, s.t("notice") - 0.6), text("hearing change? see a doctor", X + 1530, 670, 38, GREEN_T, s.t("notice") - 0.3, "c")]
    for i, cx in enumerate((205, 320, 440, 560, 690)):
        cv.glow(s.t("damaged") - 0.2 + 0.1 * i, P(X, 0, cx, 230), 2.2, 55, (235, 90, 90))
    cv.push(s, Bc)

    # ---------------- RECAP (C)
    s = sc["recap"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ca)
    X = 2 * PW
    rp = title("remember 3 things", X + 960, 100, s.start + 0.4)
    for w, a, b, col, tc_, x in (("pinna", "pinna - eardrum", "3 bones - cochlea", PINK, RED_T, 400), ("hair", "hair cells -> signals", "to the brain", CREAM, GOLD_T, 960), ("balance", "the inner ear also", "helps you balance", LILAC, PURPLE, 1520)):
        tw2 = s.t(w) - 0.3
        rp += [panel(X + x - 265, 220, X + x + 265, 600, col, tw2 - 0.2), text(a, X + x, 360, 38, tc_, tw2, "c"), text(b, X + x, 470, 34, MAROON, tw2 + 0.6, "c")]
    tn = s.t("smell") - 0.8
    rp += [panel(X + 200, 720, X + 1720, 890, LILAC, tn - 0.3), text("next: smell and taste", X + 960, 820, 56, PURPLE, tn, "c")]

    bd.fx.append(cv.fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def build_short(n):
    sc, t0 = load(EP / f"short{n}")
    bd = B.Board(3, 2)
    pops = []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    cv = Cine(bd)
    cam = bd.camera
    A, Bc, C = (960, 540), (PW + 960, 540), (2 * PW + 960, 540)
    cam(0, *A, 1.0, 0.1)
    if n == 1:
        s = sc["case"]
        a = [pop(shot(2), 960, 540, w=1920, t=0.0, dur=0.3), text("the SMALLEST bone", 1600, 300, 62, RED_T, s.t("smallest") - 0.4, "c"),
             text("in your whole body", 1600, 430, 50, MAROON, s.t("whole") - 0.4, "c"), text("hidden in your ear", 1600, 600, 56, GOLD_T, s.t("hidden") - 0.4, "c")]
        cv.glow(s.t("hidden") - 0.3, P(0, 0, 548, 330), 2.5, 70, (235, 90, 90))
        cv.dive_out(s, P(0, 0, 548, 330), 4.0, 1.3)
        s = sc["turn"]
        cv.land(s, Bc)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(shot(3), X + 960, 540, w=1920, t=s.start), text("a chain of 3 tiny bones", X + 1600, 300, 48, GOLD_T, s.t("chain") - 0.5, "c"),
             text("?", X + 1600, 620, 220, PURPLE, s.t("called") - 0.3, "c")]
        cv.flow([P(X, 0, x, y) for x, y in ((390, 500), (470, 470), (500, 330), (430, 230), (520, 220), (560, 330), (600, 410), (700, 410), (770, 420))],
                s.t("carry") - 0.3, s.start + s.dur, 2.0, VIB, 13, 3)
        cv.push(s, Bc)
    else:
        s = sc["case"]
        a = [pop(shot(1), 960, 540, w=1920, t=0.0, dur=0.3), text("you stopped spinning", 420, 300, 50, MAROON, s.t("stopped") - 0.5, "c"),
             text("the room keeps spinning", 1500, 300, 50, RED_T, s.t("spinning") - 0.6, "c")]
        cv.dive_out(s, P(0, 0, 724, 120), 5.0, 1.4)
        s = sc["twist"]
        cv.land(s, Bc)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(shot(2), X + 960, 540, w=1920, t=s.start), text("part of the answer", X + 1600, 300, 56, MAROON, s.t("answer") - 0.4, "c"),
             text("is in your EARS", X + 1600, 440, 66, PURPLE, s.t("hidden") - 0.2, "c")]
        cv.push(s, Bc, 0.6, 0.3)
        s = sc["clue"]
        cam(s.start, *C, 1.0, 1.0)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        c = [pop(shot(2), X + 960, 540, w=1920, t=s.start + 0.2), text("which part?", X + 1600, 340, 84, GOLD_T, s.t("which") - 0.3, "c"),
             text("?", X + 1600, 680, 220, GOLD_T, s.t("dizzy") - 0.2, "c")]
        cv.glow(s.start + 0.6, P(X, 0, 640, 290), s.dur - 0.6, 110, (150, 110, 220))
        cv.push(s, C, 0.4, 0.2)

    bd.fx.append(cv.fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def make_short(n):
    import package as Pk
    import bridge
    bd, sc = build_short(n)
    board = NU.render_board(bd, sc, f"ear_story{n}")
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
        Pk.btext(d, (540, y), ln, size, Pk.MAROON, "mm")
        y += size + 18
    d.rounded_rectangle((170, 1380, 910, 1490), radius=55, fill=Pk.MAROON)
    d.text((540, 1435), "FULL VIDEO ON THE CHANNEL", font=Pk.f(44), fill=(255, 255, 255), anchor="mm", stroke_width=1, stroke_fill=(255, 255, 255))
    d.text((540, 1600), "THE ANATOMY UNFOLDED", font=Pk.f(46), fill=(150, 120, 130), anchor="mm")
    ov = OUT / f"ear_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"ear_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["ear"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "ear", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            OF.credit(bd.frame(round(v.start + v.dur * 0.6, 1))).save(OUT / f"ear2_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                OF.credit(bd.frame(round(v.start + v.dur * 0.6, 1))).save(OUT / f"ear2_short{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "ear", intro=True)
        f.replace(OUT / "final_ear.mp4")
        print("done ->", OUT / "final_ear.mp4")
