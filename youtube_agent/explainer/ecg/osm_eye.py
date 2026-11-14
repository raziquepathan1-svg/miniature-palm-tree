"""The eye / vision video (fact-checked 14 Nov 2026) + 2 story Shorts.

    python3 osm_eye.py [stills] | short 1|2 [stills]
Env: EP_DIR (default ../eye), OUT_DIR.
"""
import math
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "eye")))
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
SHORT_TITLES = {1: "Your Eye Sees Upside Down", 2: "Your Eye Has A Blind Spot"}
SHORT_Q = {1: "So what does your brain do?", 2: "So how does your brain hide it?"}
S = 3
OLN = (110, 80, 90, 255)
AMBER = (250, 190, 60, 255)


def new(w, h):
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def done(im, w, h):
    return im.resize((w, h), Image.LANCZOS)


def eye_section(rays=False, spot=False):
    """Side cross-section of the eye. Cornea on the left, retina arc on the right, optic nerve bottom right."""
    W, H = 900, 640
    im, d = new(W, H)
    d.ellipse((140 * S, 60 * S, 800 * S, 580 * S), fill=(250, 245, 235, 255), outline=OLN, width=7 * S)                  # eyeball
    d.pieslice((60 * S, 190 * S, 260 * S, 450 * S), 100, 260, fill=(200, 230, 245, 255), outline=(90, 140, 190, 255), width=6 * S)   # cornea bulge
    d.arc((140 * S, 60 * S, 800 * S, 580 * S), 300, 60, fill=(210, 80, 90, 255), width=14 * S)                          # retina (back arc)
    d.line([(260 * S, 250 * S), (260 * S, 190 * S)], fill=(130, 90, 70, 255), width=18 * S)                              # iris
    d.line([(260 * S, 390 * S), (260 * S, 450 * S)], fill=(130, 90, 70, 255), width=18 * S)
    d.ellipse((300 * S, 250 * S, 370 * S, 390 * S), fill=(250, 225, 140, 255), outline=(190, 150, 50, 255), width=5 * S)    # lens
    tube = [(690 * S, 500 * S), (760 * S, 560 * S), (840 * S, 610 * S)]
    d.line(tube, fill=(240, 205, 90, 255), width=40 * S)                                                                # optic nerve
    if spot:
        d.ellipse((665 * S, 475 * S, 715 * S, 525 * S), fill=(60, 60, 70, 255))
    if rays:
        for y0, y1 in ((250, 460), (320, 320), (390, 180)):   # rays cross at the lens and invert
            d.line([(0, y0 * S), (330 * S, 320 * S), (700 * S, y1 * S)], fill=AMBER, width=7 * S)
    return done(im, W, H)


def arrow_pic(up=True, col=(60, 120, 200, 255)):
    W, H = 200, 360
    im, d = new(W, H)
    d.line([(100 * S, 60 * S), (100 * S, 320 * S)], fill=col, width=26 * S)
    d.polygon([(40 * S, 110 * S), (160 * S, 110 * S), (100 * S, 20 * S)], fill=col)
    if not up:
        im = im.transpose(Image.FLIP_TOP_BOTTOM)
    return done(im, W, H)


def cells_pic():
    W, H = 900, 520
    im, d = new(W, H)
    d.rectangle((0, 440 * S, W * S, H * S), fill=(210, 80, 90, 255), outline=OLN, width=4 * S)
    for i, x in enumerate(range(60, 860, 90)):
        if i % 3 == 1:
            d.polygon([((x - 28) * S, 440 * S), ((x + 28) * S, 440 * S), (x * S, 190 * S)], fill=(80, 160, 90, 255) if i % 2 else (210, 90, 100, 255), outline=OLN)
        else:
            d.rounded_rectangle(((x - 12) * S, 130 * S, (x + 12) * S, 440 * S), radius=12 * S, fill=(150, 130, 210, 255), outline=OLN, width=3 * S)
    for x, y in ((100, 60), (300, 90), (520, 50), (720, 80)):
        d.line([(x * S, 0), ((x + 10) * S, 120 * S)], fill=AMBER, width=8 * S)
    return done(im, W, H)


def blindspot_pic():
    W, H = 900, 420
    im, d = new(W, H)
    d.rectangle((0, 0, W * S, H * S), fill=(250, 245, 235, 255), outline=OLN, width=4 * S)
    for x in range(60, 840, 70):
        d.line([(x * S, 40 * S), (x * S, 380 * S)], fill=(190, 160, 210, 255), width=10 * S)
    d.ellipse((380 * S, 150 * S, 520 * S, 290 * S), fill=(250, 245, 235, 255), outline=(60, 60, 70, 255), width=6 * S)
    return done(im, W, H)


def iris_front(pupil):
    W = 420
    im, d = new(W, W)
    d.ellipse((20 * S, 20 * S, 400 * S, 400 * S), fill=(120, 170, 220, 255), outline=(70, 110, 160, 255), width=8 * S)
    for k in range(24):
        a = math.radians(k * 15)
        d.line([((210 + 70 * math.cos(a)) * S, (210 + 70 * math.sin(a)) * S), ((210 + 185 * math.cos(a)) * S, (210 + 185 * math.sin(a)) * S)], fill=(90, 140, 190, 255), width=3 * S)
    d.ellipse(((210 - pupil) * S, (210 - pupil) * S, (210 + pupil) * S, (210 + pupil) * S), fill=(30, 25, 40, 255))
    return done(im, W, W)


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
    st = [pop(eye_section(True), 520, 540, w=900, t=0.3), pop(arrow_pic(False), 1000, 560, h=240, t=s.t("upside") - 0.4), text("the image is UPSIDE DOWN", 1450, 220, 62, RED_T, s.t("upside") - 0.5, "c"),
          text("yet you see it upright", 1450, 400, 64, GREEN_T, s.t("right") - 0.5, "c"), text("how?", 1450, 700, 150, GOLD_T, s.t("how") - 0.4, "c")]

    # ---------------- OVERVIEW (B)
    s = sc["overview"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, st)
    X = PW
    ov = [pop(eye_section(), X + 520, 540, w=900, t=s.start + 0.3), text("like a CAMERA", X + 1450, 160, 80, GOLD_T, s.t("camera") - 0.4, "c"),
          text("CORNEA", X + 1450, 330, 70, BLUE_T, s.t("cornea") - 0.3, "c"), text("PUPIL", X + 1450, 450, 70, PURPLE, s.t("pupil") - 0.3, "c"),
          text("LENS", X + 1450, 570, 70, GOLD_T, s.t("lens") - 0.3, "c"), text("RETINA", X + 1450, 690, 70, RED_T, s.t("retina") - 0.3, "c")]

    # ---------------- IRIS (C)
    s = sc["iris"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ov)
    X = 2 * PW
    ir = [pop(iris_front(40), X + 380, 440, h=380, t=s.start + 0.3), pop(iris_front(95), X + 960, 440, h=380, t=s.t("size") - 0.5), text("IRIS", X + 1500, 260, 100, BLUE_T, s.t("iris") - 0.3, "c"),
          text("muscles change", X + 1500, 400, 56, MAROON, s.t("muscles") - 0.4, "c"), text("the PUPIL size", X + 1500, 490, 70, PURPLE, s.t("size") - 0.5, "c"),
          text("controls how much light", X + 1500, 700, 54, GOLD_T, s.t("light") - 0.8, "c"), text("small", X + 380, 720, 62, MAROON, s.start + 0.6, "c"), text("large", X + 960, 720, 62, MAROON, s.t("size") - 0.2, "c")]

    # ---------------- LENS (D)
    s = sc["lens"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, ir)
    le = [pop(eye_section(True), 520, Y + 540, w=900, t=s.start + 0.3), text("cornea + lens bend light", 1450, Y + 200, 56, GOLD_T, s.t("bend") - 0.5, "c"), text("like a CONVEX lens", 1450, Y + 320, 62, BLUE_T, s.t("convex") - 0.5, "c"),
          text("image on the retina", 1450, Y + 540, 56, MAROON, s.t("image") - 0.5, "c"), text("= UPSIDE DOWN", 1450, Y + 660, 80, RED_T, s.t("upside") - 0.4, "c")]

    # ---------------- RETINA (E)
    s = sc["retina"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, le)
    X = PW
    re = [pop(cells_pic(), X + 520, Y + 380, w=900, t=s.start + 0.3), text("RODS: dim light", X + 1450, Y + 160, 64, PURPLE, s.t("rods") - 0.3, "c"), text("CONES: color", X + 1450, Y + 290, 64, GREEN_T, s.t("cones") - 0.5, "c"),
          text("FOVEA = sharp central vision", X + 1450, Y + 430, 48, GOLD_T, s.t("fovea") - 0.5, "c"), text("3 cone types: red - green - blue", X + 960, Y + 780, 62, RED_T, s.t("three") - 0.5, "c")]

    # ---------------- NERVE (F)
    s = sc["nerve"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, re)
    X = 2 * PW
    ne = [pop(eye_section(), X + 380, Y + 540, w=640, t=s.start + 0.3), pop(brain, X + 1500, Y + 320, h=420, t=s.t("brain") - 0.7), text("light -> electrical signals", X + 960, Y + 100, 62, GOLD_T, s.t("electrical") - 0.5, "c"),
          text("OPTIC NERVE", X + 1000, Y + 740, 80, PURPLE, s.t("optic") - 0.4, "c"), text("-> the brain", X + 1500, Y + 640, 64, RED_T, s.t("brain") - 0.4, "c")]

    # ---------------- MYSTERY (A)
    s = sc["mystery"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, ne)
    my = [pop(arrow_pic(False), 330, 540, h=620, t=s.start + 0.3), pop(brain, 960, 540, h=520, t=s.t("brain") - 0.5), pop(arrow_pic(True, (60, 160, 90, 255)), 1560, 540, h=620, t=s.t("upright") - 0.7),
          text("mystery", 960, 130, 90, GREEN_T, s.t("mystery") - 0.3, "c"), text("brain's visual processing", 960, 900, 60, GOLD_T, s.t("processing") - 0.5, "c"), text("how? scientists don't fully know", 960, 1000, 50, MAROON, s.t("fully") - 0.8, "c")]

    # ---------------- BLIND SPOT (B)
    s = sc["blindspot"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, my)
    X = PW
    bs = [pop(eye_section(False, True), X + 480, 440, w=800, t=s.start + 0.3), pop(blindspot_pic(), X + 1500, 400, w=520, t=s.t("fills") - 0.8), text("BLIND SPOT", X + 960, 820, 100, RED_T, s.t("blind") - 0.4, "c"),
          text("optic nerve exit: no rods or cones", X + 960, 930, 56, MAROON, s.t("nerve") - 0.4, "c") if False else text("optic nerve exit: no rods or cones", X + 960, 930, 56, MAROON, s.t("leaves") - 0.4, "c"),
          text("brain fills in", X + 1500, 640, 60, GREEN_T, s.t("fills") - 0.4, "c")]

    # ---------------- RECAP (C)
    s = sc["recap"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, bs)
    X = 2 * PW
    rp = title("remember 3 things", X + 960, 100, s.start + 0.4)
    for w, a, b, col, tc_, x in (("cornea", "cornea - pupil - lens", "-> retina", PINK, RED_T, 400), ("rods", "rods + cones", "-> signals to the brain", CREAM, GOLD_T, 960), ("brain", "brain handles", "upside-down + blind spot", LILAC, PURPLE, 1520)):
        tw2 = s.t(w) - 0.3
        rp += [panel(X + x - 265, 220, X + x + 265, 600, col, tw2 - 0.2), text(a, X + x, 360, 38, tc_, tw2, "c"), text(b, X + x, 470, 34, MAROON, tw2 + 0.6, "c")]
    tn = s.t("hearing") - 0.8
    rp += [panel(X + 200, 720, X + 1720, 890, LILAC, tn - 0.3), text("next: hearing", X + 960, 820, 56, PURPLE, tn, "c")]

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
    brain = OB.brain_img()
    if n == 1:
        s = sc["case"]
        a = [pop(eye_section(True), 520, 540, w=900, t=0.3), pop(arrow_pic(False), 1000, 560, h=240, t=s.t("upside") - 0.5), text("the image is", 1450, 280, 70, MAROON, s.t("image") - 0.3, "c"), text("UPSIDE DOWN", 1450, 420, 100, RED_T, s.t("upside") - 0.4, "c")]
        s = sc["turn"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(arrow_pic(False), X + 380, 540, h=560, t=s.start + 0.3), pop(brain, X + 960, 540, h=420, t=s.t("brain") - 0.6), pop(arrow_pic(True, (60, 160, 90, 255)), X + 1540, 540, h=560, t=s.t("right") - 0.9),
             text("yet you see it upright", X + 960, 900, 64, GREEN_T, s.t("right") - 0.5, "c"), text("?", X + 960, 180, 200, GOLD_T, s.t("brain") - 0.2, "c")]
    else:
        s = sc["case"]
        a = [pop(eye_section(False, True), 520, 540, w=900, t=0.3), text("a spot where", 1450, 280, 70, MAROON, s.t("spot") - 0.4, "c"), text("you cannot see", 1450, 420, 90, RED_T, s.t("cannot") - 0.4, "c")]
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(blindspot_pic(), X + 520, 540, w=900, t=s.start + 0.3), text("never noticed it", X + 1450, 300, 72, MAROON, s.t("noticed") - 0.4, "c"), text("your brain hides it", X + 1450, 480, 80, PURPLE, s.t("hides") - 0.5, "c")]
        s = sc["clue"]
        cam(s.start, *C, 1.0, 1.0)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        c = [pop(eye_section(False, True), X + 520, 540, w=900, t=s.start + 0.3), text("what is it?", X + 1450, 300, 100, GOLD_T, s.t("what") - 0.3, "c"), text("how is it hidden?", X + 1450, 500, 70, PURPLE, s.t("hide") - 0.5, "c"),
             text("?", X + 1450, 820, 200, GOLD_T, s.t("hide") - 0.2, "c")]

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
    board = NU.render_board(bd, sc, f"eye_story{n}")
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
    ov = OUT / f"eye_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"eye_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["eye"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "eye", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"eye_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"eshort{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "eye", intro=True)
        f.replace(OUT / "final_eye.mp4")
        print("done ->", OUT / "final_eye.mp4")
