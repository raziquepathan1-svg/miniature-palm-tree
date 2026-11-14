"""The ear / hearing video (fact-checked 14 Nov 2026) + 2 story Shorts.

    python3 osm_ear.py [stills] | short 1|2 [stills]
Env: EP_DIR (default ../ear), OUT_DIR.
"""
import math
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "ear")))
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
SHORT_TITLES = {1: "The Smallest Bone", 2: "Why You Feel Dizzy"}
SHORT_Q = {1: "So what is the smallest bone?", 2: "So which part makes you dizzy?"}
S = 3
new, done, tube = DG.new, DG.done, DG.tube
OLN = (110, 80, 90, 255)
SKIN = (248, 214, 190, 255)
BONE = (245, 235, 215, 255)


def new_(w, h):
    return new(w, h)


def ear_section():
    W, H = 1000, 640
    im, d = new(W, H)
    d.pieslice((20 * S, 120 * S, 240 * S, 520 * S), 90, 270, fill=SKIN, outline=(170, 110, 90, 255), width=6 * S)                 # pinna
    d.rounded_rectangle((200 * S, 290 * S, 430 * S, 350 * S), radius=30 * S, fill=(250, 235, 225, 255), outline=OLN, width=5 * S)    # ear canal
    d.line([(430 * S, 270 * S), (430 * S, 370 * S)], fill=(200, 80, 90, 255), width=10 * S)                                          # eardrum
    for (x, y, r) in ((480, 300, 16), (530, 320, 14), (580, 340, 11)):                                                              # ossicles
        d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=BONE, outline=OLN, width=4 * S)
    d.line([(430 * S, 320 * S), (480 * S, 300 * S), (530 * S, 320 * S), (580 * S, 340 * S)], fill=OLN, width=5 * S)
    d.rounded_rectangle((440 * S, 380 * S, 700 * S, 420 * S), radius=20 * S, fill=(180, 210, 230, 255), outline=OLN, width=4 * S)  # eustachian tube
    for k in range(3):                                                                                                               # cochlea
        r = 90 - k * 28
        d.ellipse(((750 - r) * S, (330 - r) * S, (750 + r) * S, (330 + r) * S), outline=(250, 190, 60, 255), width=10 * S)
    for k in range(3):                                                                                                               # semicircular canals
        d.ellipse(((700 + k * 40) * S, (130 + k * 24) * S, (810 + k * 40) * S, (240 + k * 24) * S), outline=(140, 90, 200, 255), width=9 * S)
    tube(d, [(820, 380), (900, 440), (960, 520)], (240, 210, 100, 255), 22)                                                          # auditory nerve
    return done(im, W, H)


def ossicles_pic():
    W, H = 900, 360
    im, d = new(W, H)
    d.line([(60 * S, 260 * S), (60 * S, 80 * S)], fill=(200, 80, 90, 255), width=14 * S)                                             # eardrum
    parts = [(200, 180, 80, "malleus"), (420, 150, 60, "incus"), (640, 190, 36, "stapes")]
    for x, y, r, nm in parts:
        d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=BONE, outline=OLN, width=6 * S)
    d.line([(70 * S, 170 * S), (200 * S, 180 * S), (420 * S, 150 * S), (640 * S, 190 * S)], fill=OLN, width=7 * S)
    d.rectangle((760 * S, 120 * S, 860 * S, 260 * S), fill=(250, 190, 60, 255), outline=OLN, width=5 * S)                              # oval window
    d.line([(676 * S, 190 * S), (760 * S, 190 * S)], fill=OLN, width=6 * S)
    return done(im, W, H)


def cochlea_pic():
    W, H = 640, 640
    im, d = new(W, H)
    for k in range(5):
        r = 280 - k * 52
        d.ellipse(((320 - r) * S, (320 - r) * S, (320 + r) * S, (320 + r) * S), outline=(250, 190, 60, 255), width=16 * S)
    d.ellipse((300 * S, 300 * S, 340 * S, 340 * S), fill=(250, 190, 60, 255))
    return done(im, W, H)


def hair_pic():
    W, H = 900, 480
    im, d = new(W, H)
    d.rectangle((0, 380 * S, W * S, 480 * S), fill=(250, 210, 140, 255), outline=OLN, width=4 * S)
    for x in range(70, 860, 110):
        d.rounded_rectangle(((x - 34) * S, 330 * S, (x + 34) * S, 400 * S), radius=24 * S, fill=(240, 170, 190, 255), outline=OLN, width=4 * S)
        for k in range(-2, 3):
            d.line([(x + k * 10) * S, 330 * S, (x + k * 12) * S, 200 * S], fill=(140, 90, 200, 255), width=6 * S)
    for x in (140, 360, 580, 800):
        d.line([(x * S, 60 * S), ((x + 40) * S, 160 * S)], fill=(250, 190, 60, 255), width=8 * S)
    return done(im, W, H)


def canals_pic():
    W, H = 640, 640
    im, d = new(W, H)
    d.ellipse((80 * S, 120 * S, 460 * S, 500 * S), outline=(140, 90, 200, 255), width=22 * S)
    d.ellipse((200 * S, 40 * S, 580 * S, 420 * S), outline=(190, 130, 230, 255), width=22 * S)
    d.ellipse((160 * S, 220 * S, 540 * S, 600 * S), outline=(110, 70, 170, 255), width=22 * S)
    for x, y in ((300, 300), (330, 280), (270, 330)):
        d.ellipse(((x - 14) * S, (y - 14) * S, (x + 14) * S, (y + 14) * S), fill=(120, 190, 240, 255))
    return done(im, W, H)


def wave_pic():
    W, H = 900, 300
    im, d = new(W, H)
    pts = [(x, 150 + 80 * math.sin(x / 40)) for x in range(10, 890, 8)]
    d.line([(x * S, y * S) for x, y in pts], fill=(250, 190, 60, 255), width=10 * S)
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
    brain = OB.brain_img()

    # ---------------- STORY (A)
    s = sc["story"]
    st = [pop(wave_pic(), 520, 420, w=900, t=0.3), pop(ear_section(), 520, 780, w=760, t=s.t("ear") - 0.6), text("sound = moving air", 1450, 200, 72, GOLD_T, s.t("moving") - 0.4, "c"),
          text("the SMALLEST bone", 1450, 420, 76, RED_T, s.t("smallest") - 0.4, "c"), text("how?", 1450, 700, 160, PURPLE, s.t("how") - 0.4, "c")]

    # ---------------- OVERVIEW (B)
    s = sc["overview"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, st)
    X = PW
    ov = [pop(ear_section(), X + 520, 540, w=980, t=s.start + 0.3), text("OUTER", X + 1500, 260, 80, GOLD_T, s.t("outer") - 0.3, "c"), text("MIDDLE", X + 1500, 420, 80, RED_T, s.t("middle") - 0.3, "c"), text("INNER", X + 1500, 580, 80, PURPLE, s.t("inner") - 0.3, "c")]

    # ---------------- OUTER (C)
    s = sc["outer"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ov)
    X = 2 * PW
    ou = [pop(ear_section(), X + 520, 540, w=980, t=s.start + 0.3), text("PINNA collects sound", X + 1500, 220, 60, GOLD_T, s.t("pinna") - 0.4, "c"), text("EAR CANAL", X + 1500, 380, 70, BLUE_T, s.t("canal") - 0.3, "c"),
          text("EARDRUM vibrates", X + 1500, 560, 64, RED_T, s.t("eardrum") - 0.3, "c")]

    # ---------------- MIDDLE (D)
    s = sc["middle"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, ou)
    mi = [pop(ossicles_pic(), 520, Y + 380, w=900, t=s.start + 0.3), text("MALLEUS", 220, Y + 600, 56, GOLD_T, s.t("malleus") - 0.3, "c"), text("INCUS", 520, Y + 600, 56, PURPLE, s.t("incus") - 0.3, "c"), text("STAPES", 820, Y + 600, 56, RED_T, s.t("stapes") - 0.3, "c"),
          text("smallest bone in the body", 1440, Y + 260, 56, RED_T, s.t("smallest") - 0.5, "c"), text("EUSTACHIAN TUBE", 1440, Y + 760, 62, BLUE_T, s.t("eustachian") - 0.4, "c"), text("equalizes pressure", 1440, Y + 850, 50, MAROON, s.t("pressure") - 0.7, "c")]

    # ---------------- INNER (E)
    s = sc["inner"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, mi)
    X = PW
    ie = [pop(cochlea_pic(), X + 480, Y + 540, h=800, t=s.start + 0.3), text("COCHLEA", X + 1450, Y + 200, 90, GOLD_T, s.t("cochlea") - 0.3, "c"), text("fluid-filled, snail-shaped", X + 1450, Y + 340, 56, MAROON, s.t("snail") - 0.6, "c"),
          text("stapes pushes the fluid", X + 1450, Y + 560, 56, RED_T, s.t("pushes") - 0.5, "c"), text("= waves inside", X + 1450, Y + 680, 70, PURPLE, s.t("waves") - 0.4, "c")]

    # ---------------- HAIR (F)
    s = sc["hair"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, ie)
    X = 2 * PW
    ha = [pop(hair_pic(), X + 500, Y + 380, w=860, t=s.start + 0.3), text("HAIR CELLS", X + 1450, Y + 160, 80, PURPLE, s.t("hair") - 0.3, "c"), text("vibrations -> electrical signals", X + 1450, Y + 300, 46, GOLD_T, s.t("electrical") - 0.6, "c"),
          text("AUDITORY NERVE -> brain", X + 960, Y + 700, 70, RED_T, s.t("auditory") - 0.4, "c"), text("mystery solved!", X + 960, Y + 850, 90, GREEN_T, s.t("answer") - 0.5, "c")]

    # ---------------- BALANCE (A)
    s = sc["balance"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, ha)
    ba = [pop(canals_pic(), 460, 540, h=780, t=s.start + 0.3), text("SEMICIRCULAR CANALS", 1400, 200, 62, PURPLE, s.t("semicircular") - 0.4, "c"), text("fluid-filled: BALANCE", 1400, 350, 64, GOLD_T, s.t("balance") - 0.4, "c"),
          text("spin... fluid keeps moving", 1400, 560, 56, MAROON, s.t("spin") - 0.4, "c"), text("= DIZZY", 1400, 720, 110, RED_T, s.t("dizzy") - 0.5, "c")]

    # ---------------- CARE (B)
    s = sc["care"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, ba)
    X = PW
    ca = [pop(hair_pic(), X + 500, 420, w=860, t=s.start + 0.3), text("hair cells do NOT regenerate", X + 960, 800, 66, RED_T, s.t("regenerate") - 0.5, "c"),
          text("damage = permanent hearing loss", X + 960, 910, 56, MAROON, s.t("permanent") - 0.5, "c"), text("protect from loud noise", X + 1500, 220, 58, GREEN_T, s.t("protecting") - 0.4, "c"),
          panel(X + 1000, 330, X + 1860, 470, MINT, s.t("notice") - 0.6), text("hearing change? see a doctor", X + 1430, 400, 42, GREEN_T, s.t("notice") - 0.3, "c")]

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
        a = [pop(ear_section(), 520, 540, w=900, t=0.3), text("the SMALLEST bone", 1450, 280, 80, RED_T, s.t("smallest") - 0.4, "c"), text("in your whole body", 1450, 420, 60, MAROON, s.t("whole") - 0.4, "c"),
             text("hidden in your ear", 1450, 600, 64, GOLD_T, s.t("hidden") - 0.4, "c")]
        s = sc["turn"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(ossicles_pic(), X + 520, 460, w=900, t=s.start + 0.3), text("a chain of 3 tiny bones", X + 960, 760, 64, GOLD_T, s.t("chain") - 0.5, "c"), text("?", X + 960, 930, 180, PURPLE, s.t("called") - 0.3, "c")]
    else:
        s = sc["case"]
        a = [pop(canals_pic(), 520, 540, h=760, t=0.3), text("you stopped spinning", 1450, 280, 68, MAROON, s.t("stopped") - 0.5, "c"), text("the room keeps spinning", 1450, 440, 66, RED_T, s.t("spinning") - 0.6, "c")]
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(ear_section(), X + 520, 540, w=900, t=s.start + 0.3), text("part of the answer", X + 1450, 300, 68, MAROON, s.t("answer") - 0.4, "c"), text("is in your EARS", X + 1450, 460, 84, PURPLE, s.t("hidden") - 0.2, "c")]
        s = sc["clue"]
        cam(s.start, *C, 1.0, 1.0)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        c = [pop(ear_section(), X + 520, 540, w=900, t=s.start + 0.3), text("which part?", X + 1450, 360, 100, GOLD_T, s.t("which") - 0.3, "c"), text("?", X + 1450, 720, 200, GOLD_T, s.t("dizzy") - 0.2, "c")]

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
        P.btext(d, (540, y), ln, size, P.MAROON, "mm")
        y += size + 18
    d.rounded_rectangle((170, 1380, 910, 1490), radius=55, fill=P.MAROON)
    d.text((540, 1435), "FULL VIDEO ON THE CHANNEL", font=P.f(44), fill=(255, 255, 255), anchor="mm", stroke_width=1, stroke_fill=(255, 255, 255))
    d.text((540, 1600), "THE ANATOMY UNFOLDED", font=P.f(46), fill=(150, 120, 130), anchor="mm")
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
            OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"ear_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"rshort{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "ear", intro=True)
        f.replace(OUT / "final_ear.mp4")
        print("done ->", OUT / "final_ear.mp4")
