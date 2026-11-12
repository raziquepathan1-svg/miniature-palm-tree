"""Digestive system video (owner-approved 12 Nov 2026) + 2 story Shorts.

    python3 osm_digest.py [stills] | short 1|2 [stills]
Env: EP_DIR (default ../digestive), OUT_DIR.
"""
import math
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "digestive")))
OUT = Path(os.environ.get("OUT_DIR", str(HERE)))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_preview as OP  # noqa: E402
import osm_brain as OB  # noqa: E402
import osm_neuron as NU  # noqa: E402
import osm_auto as AU  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OB.PINK, OB.LILAC, OB.CREAM, OB.MINT, OB.SKY
PW, PH = 1920, 1080
sv = OB.sv
SHORT_TITLES = {1: "Why It Never Digests Itself", 2: "The Six Meter Tube"}
SHORT_Q = {1: "So what protects the stomach?", 2: "So what do the tiny fingers do?"}
S = 3
OL = (120, 80, 70, 255)


def new(w, h):
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def done(im, w, h):
    return im.resize((w, h), Image.LANCZOS)


def tube(d, pts, col, w, ol=OL):
    big = [(x * S, y * S) for x, y in pts]
    d.line(big, fill=ol, width=(w + 8) * S, joint="curve")
    d.line(big, fill=col, width=w * S, joint="curve")
    for x, y in big[:1] + big[-1:]:
        for c, ww in ((ol, w + 8), (col, w)):
            d.ellipse((x - ww * S / 2, y - ww * S / 2, x + ww * S / 2, y + ww * S / 2), fill=c)


def gi_map():
    W, H = 760, 1000
    im, d = new(W, H)
    d.ellipse((290 * S, 20 * S, 470 * S, 110 * S), fill=(235, 150, 150, 255), outline=OL, width=5 * S)     # mouth
    d.line([(300 * S, 70 * S), (460 * S, 70 * S)], fill=(255, 255, 255, 255), width=8 * S)
    tube(d, [(380, 110), (380, 280)], (240, 190, 170, 255), 26)                                            # esophagus
    d.polygon([(x * S, y * S) for x, y in [(380, 250), (470, 260), (520, 330), (470, 400), (390, 380), (360, 320)]], fill=(245, 170, 140, 255), outline=OL)   # stomach
    d.ellipse((120 * S, 280 * S, 360 * S, 400 * S), fill=(170, 100, 70, 255), outline=OL, width=5 * S)    # liver
    d.ellipse((330 * S, 385 * S, 380 * S, 440 * S), fill=(110, 170, 90, 255), outline=OL, width=4 * S)     # gallbladder
    d.ellipse((420 * S, 400 * S, 640 * S, 450 * S), fill=(235, 200, 90, 255), outline=OL, width=4 * S)     # pancreas
    pts = []
    for i in range(7):
        y = 470 + i * 52
        pts += [(260, y), (500, y + 26)] if i % 2 == 0 else [(500, y), (260, y + 26)]
    tube(d, pts, (245, 200, 170, 255), 26)                                                                  # small intestine
    tube(d, [(200, 900), (200, 480), (560, 480), (620, 480), (620, 900), (380, 960)], (200, 160, 120, 255), 30)   # large intestine
    return done(im, W, H), W, H


def teeth_pic():
    W, H = 640, 360
    im, d = new(W, H)
    d.rounded_rectangle((20 * S, 20 * S, 620 * S, 340 * S), radius=140 * S, fill=(230, 130, 130, 255), outline=OL, width=6 * S)
    for i in range(7):
        x = 90 + i * 74
        d.rounded_rectangle((x * S, 40 * S, (x + 60) * S, 140 * S), radius=18 * S, fill=(255, 255, 255, 255), outline=(150, 150, 160, 255), width=4 * S)
        d.rounded_rectangle((x * S, 220 * S, (x + 60) * S, 320 * S), radius=18 * S, fill=(255, 255, 255, 255), outline=(150, 150, 160, 255), width=4 * S)
    d.ellipse((220 * S, 150 * S, 420 * S, 215 * S), fill=(240, 110, 120, 255))
    return done(im, W, H)


def esoph_pic():
    W, H = 360, 900
    im, d = new(W, H)
    tube(d, [(180, 30), (180, 870)], (240, 190, 170, 255), 120)
    for y in (210, 520):
        d.ellipse((110 * S, (y - 55) * S, 250 * S, (y + 55) * S), fill=(250, 150, 90, 255), outline=OL, width=5 * S)
    for y in (330, 640):
        d.arc((90 * S, (y - 40) * S, 270 * S, (y + 40) * S), 0, 180, fill=(170, 80, 70, 255), width=8 * S)
    return done(im, W, H)


def mucus_pic():
    W, H = 900, 520
    im, d = new(W, H)
    d.rectangle((0, 380 * S, W * S, H * S), fill=(240, 160, 160, 255), outline=OL, width=5 * S)       # cells
    for x in range(30, W, 90):
        d.rounded_rectangle((x * S, 395 * S, (x + 70) * S, 500 * S), radius=20 * S, fill=(250, 190, 190, 255), outline=OL, width=3 * S)
    d.rectangle((0, 240 * S, W * S, 380 * S), fill=(255, 235, 140, 255), outline=(190, 160, 40, 255), width=5 * S)   # mucus
    for i, x in enumerate(range(60, W, 110)):
        d.ellipse((x * S, (280 + (i % 2) * 40) * S, (x + 28) * S, (308 + (i % 2) * 40) * S), fill=(110, 170, 240, 255))          # bicarbonate
    for i, x in enumerate(range(40, W, 80)):
        d.ellipse((x * S, (60 + (i % 3) * 50) * S, (x + 34) * S, (94 + (i % 3) * 50) * S), fill=(235, 90, 70, 255))              # acid
    return done(im, W, H)


def coil_pic():
    W, H = 760, 540
    im, d = new(W, H)
    pts = []
    for i in range(6):
        y = 50 + i * 85
        pts += [(70, y), (690, y + 40)] if i % 2 == 0 else [(690, y), (70, y + 40)]
    tube(d, pts, (245, 200, 170, 255), 44)
    return done(im, W, H)


def villi_pic():
    W, H = 1000, 500
    im, d = new(W, H)
    d.rectangle((0, 400 * S, W * S, H * S), fill=(240, 180, 180, 255), outline=OL, width=5 * S)
    for i in range(7):
        x = 70 + i * 135
        d.rounded_rectangle((x * S, 90 * S, (x + 70) * S, 410 * S), radius=35 * S, fill=(250, 205, 190, 255), outline=OL, width=5 * S)
        d.line([(x + 35) * S, 130 * S, (x + 35) * S, 400 * S], fill=(215, 60, 70, 255), width=8 * S)
        d.ellipse(((x + 28) * S, 112 * S, (x + 42) * S, 128 * S), fill=(215, 60, 70, 255))
    return done(im, W, H)


def colon_pic():
    W, H = 640, 640
    im, d = new(W, H)
    tube(d, [(90, 560), (90, 90), (550, 90), (550, 480), (330, 540)], (210, 170, 130, 255), 80)
    for i, (x, y) in enumerate([(120, 200), (300, 100), (480, 100), (530, 300), (90, 330), (560, 420), (400, 500), (140, 460)]):
        d.ellipse((x * S, y * S, (x + 22) * S, (y + 22) * S), fill=(120, 190, 110, 255))
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
    stomach = AU.stomach_pic(True)

    # ---------------- STORY (A)
    s = sc["story"]
    st = [pop(stomach, 520, 560, h=620, t=0.3), text("ACID", 1300, 190, 120, RED_T, s.t("acid") - 0.3, "c"), text("strong enough to digest MEAT", 1300, 340, 60, MAROON, s.t("meat") - 0.5, "c"),
          text("the stomach is made of protein too", 1300, 520, 58, PURPLE, s.t("protein") - 0.9, "c"), text("so what protects it?", 1300, 760, 90, GOLD_T, s.t("protects") - 0.3, "c")]

    # ---------------- OVERVIEW (B)
    s = sc["overview"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, st)
    X = PW
    gm, GW, GH = gi_map()
    g = pop(gm, X + 480, 540, h=960, t=s.start + 0.3)
    ov = [g, text("one long tube", X + 1380, 160, 76, GOLD_T, s.t("tube") - 0.3, "c"), text("about 9 meters (stretched out)", X + 1380, 270, 64, MAROON, s.t("nine") - 0.4, "c"),
          text("helpers:", X + 1380, 470, 58, BLUE_T, s.t("helper") - 0.3, "c"), text("liver", X + 1380, 570, 62, (150, 80, 50), s.t("liver") - 0.4, "c"),
          text("gallbladder", X + 1380, 660, 62, GREEN_T, s.t("gallbladder") - 0.4, "c"), text("pancreas", X + 1380, 750, 62, GOLD_T, s.t("pancreas") - 0.5, "c")]

    # ---------------- MOUTH (C)
    s = sc["mouth"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ov)
    X = 2 * PW
    mo = [pop(teeth_pic(), X + 520, 520, w=800, t=s.start + 0.3), text("TEETH break it up", X + 1400, 220, 70, GOLD_T, s.t("teeth") - 0.3, "c"),
          pop(AU.drop_pic(), X + 1180, 520, h=200, t=s.t("saliva") - 0.5), text("SALIVA moistens", X + 1560, 520, 64, BLUE_T, s.t("saliva") - 0.2, "c"),
          text("enzyme starts breaking down STARCH", X + 1400, 800, 56, GREEN_T, s.t("enzyme") - 0.5, "c")]

    # ---------------- SWALLOW (D)
    s = sc["swallow"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, mo)
    sw = [pop(esoph_pic(), 520, Y + 540, h=980, t=s.start + 0.3), text("the ESOPHAGUS", 1350, Y + 190, 76, GOLD_T, s.t("esophagus") - 0.3, "c"),
          text("waves of squeezing", 1350, Y + 400, 62, RED_T, s.t("waves") - 0.4, "c"), text("= PERISTALSIS", 1350, Y + 500, 70, PURPLE, s.t("peristalsis") - 0.3, "c"),
          text("works even upside down!", 1350, Y + 760, 62, GREEN_T, s.t("upside") - 0.6, "c")]

    # ---------------- STOMACH (E)
    s = sc["stomach"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, sw)
    X = PW
    sm = [pop(stomach, X + 520, Y + 540, h=700, t=s.start + 0.3), text("hydrochloric ACID", X + 1380, Y + 170, 64, RED_T, s.t("hydrochloric") - 0.4, "c"),
          text("PEPSIN digests protein", X + 1380, Y + 300, 60, GOLD_T, s.t("pepsin") - 0.5, "c"), text("churning = CHYME", X + 1380, Y + 470, 70, PURPLE, s.t("chyme") - 0.5, "c"),
          text("stays a few hours", X + 1380, Y + 700, 62, MAROON, s.t("hours") - 0.8, "c")]

    # ---------------- PROTECT (F)
    s = sc["protect"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, sm)
    X = 2 * PW
    pr = [pop(mucus_pic(), X + 560, Y + 540, w=1000, t=s.start + 0.3), text("thick MUCUS layer", X + 1560, Y + 250, 62, GOLD_T, s.t("mucus") - 0.4, "c"),
          text("BICARBONATE neutralizes acid", X + 1560, Y + 420, 50, BLUE_T, s.t("bicarbonate") - 0.5, "c"), text("lining replaced every few days", X + 1560, Y + 600, 48, GREEN_T, s.t("replaced") - 0.9, "c"),
          text("mystery solved!", X + 1560, Y + 820, 90, RED_T, s.t("digest") - 0.5, "c")]

    # ---------------- SMALL INTESTINE (A)
    s = sc["small"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, pr)
    sn = [pop(coil_pic(), 520, 540, w=880, t=s.start + 0.3), text("SMALL intestine", 1400, 150, 70, GOLD_T, s.t("small") - 0.3, "c"), text("6 to 7 meters (stretched out)", 1400, 250, 52, MAROON, s.t("six") - 0.4, "c"),
          text("BILE (liver)", 1400, 440, 70, GREEN_T, s.t("bile") - 0.3, "c"), text("digests FAT", 1400, 530, 56, MAROON, s.t("fat") - 0.5, "c"),
          text("PANCREAS enzymes", 1400, 720, 66, GOLD_T, s.t("pancreas") - 0.5, "c"), text("carbs, proteins, fats", 1400, 810, 54, MAROON, s.t("fats") - 0.8, "c")]

    # ---------------- ABSORB (B)
    s = sc["absorb"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, sn)
    X = PW
    ab = [pop(villi_pic(), X + 560, 540, w=980, t=s.start + 0.3), text("VILLI", X + 1560, 220, 100, RED_T, s.t("villi") - 0.3, "c"), text("tiny fingers", X + 1560, 340, 64, MAROON, s.t("fingers") - 0.5, "c"),
          text("HUGE surface area", X + 1560, 520, 62, GOLD_T, s.t("surface") - 0.5, "c"), text("nutrients pass into blood", X + 1500, 700, 50, BLUE_T, s.t("blood") - 0.6, "c")]

    # ---------------- LARGE (C)
    s = sc["large"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ab)
    X = 2 * PW
    lg = [pop(colon_pic(), X + 520, 540, h=800, t=s.start + 0.3), text("LARGE intestine", X + 1400, 170, 70, GOLD_T, s.t("large") - 0.3, "c"), text("absorbs WATER", X + 1400, 340, 66, BLUE_T, s.t("water") - 0.3, "c"),
          text("trillions of helpful bacteria", X + 1400, 560, 56, GREEN_T, s.t("bacteria") - 0.8, "c"), text("what remains leaves the body", X + 1400, 780, 56, MAROON, s.t("leaves") - 0.7, "c")]

    # ---------------- JOURNEY (D)
    s = sc["journey"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, lg)
    jr = [pop(sv("Horloge"), 520, Y + 480, h=560, t=s.start + 0.3), text("1 to 3 DAYS", 1350, Y + 220, 100, GOLD_T, s.t("days") - 0.4, "c"), text("mouth to the end", 1350, Y + 340, 56, MAROON, s.t("mouth") - 0.4, "c"),
          text("most absorption: SMALL intestine", 1350, Y + 520, 56, GREEN_T, s.t("most") - 0.5, "c"),
          panel(850, Y + 700, 1850, Y + 940, MINT, s.t("pain") - 1.5), text("ongoing pain or blood in stool?", 1350, Y + 780, 52, RED_T, s.t("pain") - 1.2, "c"), text("see a doctor", 1350, Y + 880, 66, GREEN_T, s.t("doctor") - 0.7, "c")]

    # ---------------- RECAP (E)
    s = sc["recap"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, jr)
    X = PW
    rp = title("remember 3 things", X + 960, Y + 100, s.start + 0.4)
    for w, a, b, col, tc_, x in (("tube", "one long tube", "with helper organs", PINK, RED_T, 400), ("mucus", "mucus protects", "the stomach", CREAM, GOLD_T, 960), ("absorbing", "the small intestine", "does most absorbing", SKY, BLUE_T, 1520)):
        tw2 = s.t(w) - 0.3
        rp += [panel(X + x - 265, Y + 220, X + x + 265, Y + 600, col, tw2 - 0.2), text(a, X + x, Y + 360, 46, tc_, tw2, "c"), text(b, X + x, Y + 470, 44, MAROON, tw2 + 0.6, "c")]
    tn = s.t("kidneys") - 0.8
    rp += [panel(X + 200, Y + 720, X + 1720, Y + 890, LILAC, tn - 0.3), text("next: the kidneys", X + 960, Y + 820, 56, PURPLE, tn, "c")]

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
        a = [pop(AU.stomach_pic(True), 520, 560, h=700, t=0.3), text("ACID", 1400, 200, 130, RED_T, s.t("acid") - 0.3, "c"), text("digests MEAT", 1400, 400, 78, MAROON, s.t("meat") - 0.4, "c"),
             text("the stomach is protein too", 1400, 620, 62, PURPLE, s.t("protein") - 0.9, "c")]
        s = sc["turn"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(AU.stomach_pic(False), X + 520, 540, h=640, t=s.start + 0.3), text("never digests itself", X + 1400, 260, 76, RED_T, s.t("itself") - 0.4, "c"),
             text("replaced every few days", X + 1400, 470, 62, GREEN_T, s.t("replaced") - 0.9, "c"), text("what protects it?", X + 1400, 700, 80, GOLD_T, s.t("what") - 0.5, "c"), text("?", X + 1400, 900, 200, GOLD_T, s.t("what") - 0.2, "c")]
    else:
        s = sc["case"]
        a = [pop(coil_pic(), 520, 540, w=880, t=0.3), text("6 - 7 METERS", 1400, 250, 110, GOLD_T, s.t("six") - 0.4, "c"), text("longer than a car", 1400, 430, 66, MAROON, s.t("car") - 0.4, "c"),
             text("fits inside your belly", 1400, 620, 62, BLUE_T, s.t("fits") - 0.5, "c")]
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(villi_pic(), X + 540, 540, w=900, t=s.start + 0.3), text("length is not the secret", X + 1500, 250, 60, MAROON, s.t("secret") - 0.5, "c"),
             text("tiny FINGERS cover the wall", X + 1500, 480, 66, RED_T, s.t("fingers") - 0.6, "c")]
        s = sc["clue"]
        cam(s.start, *C, 1.0, 1.0)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        c = [pop(villi_pic(), X + 540, 540, w=900, t=s.start + 0.2), text("what do they do?", X + 1500, 340, 82, GOLD_T, s.t("what") - 0.3, "c"), text("?", X + 1500, 700, 240, GOLD_T, s.t("matter") - 0.8, "c")]

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
    board = NU.render_board(bd, sc, f"dig_story{n}")
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
    ov = OUT / f"dig_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"dig_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["digestive"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "digestive", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"dig_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"dshort{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "dig", intro=True)
        f.replace(OUT / "final_dig.mp4")
        print("done ->", OUT / "final_dig.mp4")
