"""Kidney (urinary system) video (fact-checked 13 Nov 2026) + 2 story Shorts.

    python3 osm_kidney.py [stills] | short 1|2 [stills]
Env: EP_DIR (default ../kidney), OUT_DIR.
"""
import math
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "kidney")))
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
import osm_digest as DG  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OB.PINK, OB.LILAC, OB.CREAM, OB.MINT, OB.SKY
PW, PH = 1920, 1080
sv = OB.sv
SHORT_TITLES = {1: "Where Does 180 Liters Go", 2: "The Fist Sized Filter"}
SHORT_Q = {1: "So where does the fluid go?", 2: "So what message do they send?"}
S = 3
new, done, tube = DG.new, DG.done, DG.tube
OLN = (120, 80, 70, 255)


def tub_pic():
    W, H = 900, 420
    im, d = new(W, H)
    d.rounded_rectangle((40 * S, 120 * S, 860 * S, 360 * S), radius=110 * S, fill=(235, 240, 250, 255), outline=(120, 130, 160, 255), width=6 * S)
    d.rounded_rectangle((70 * S, 150 * S, 830 * S, 250 * S), radius=40 * S, fill=(140, 200, 240, 255))
    for x in (130, 730):
        d.rectangle((x * S, 355 * S, (x + 40) * S, 400 * S), fill=(120, 130, 160, 255))
    return done(im, W, H)


def urinary_pic():
    W, H = 640, 980
    im, d = new(W, H)
    kc, ko = (205, 90, 90, 255), (120, 40, 50, 255)
    for cx in (190, 450):
        d.ellipse(((cx - 80) * S, 40 * S, (cx + 80) * S, 330 * S), fill=kc, outline=ko, width=6 * S)
        d.ellipse(((cx - 35) * S, 110 * S, (cx + 35) * S, 260 * S), fill=(235, 235, 235, 255) if False else (230, 150, 150, 255))
    tube(d, [(215, 300), (250, 560), (300, 700)], (240, 200, 90, 255), 20)
    tube(d, [(425, 300), (390, 560), (340, 700)], (240, 200, 90, 255), 20)
    d.ellipse((230 * S, 680 * S, 410 * S, 830 * S), fill=(250, 220, 120, 255), outline=(170, 130, 30, 255), width=6 * S)
    tube(d, [(320, 820), (320, 960)], (240, 200, 90, 255), 20)
    return done(im, W, H)


def glom_pic():
    W, H = 620, 620
    im, d = new(W, H)
    d.ellipse((60 * S, 60 * S, 560 * S, 560 * S), fill=(235, 245, 255, 255), outline=(110, 140, 190, 255), width=8 * S)
    for r, ang in ((150, 0), (110, 40), (70, 80)):
        for k in range(8):
            a = math.radians(ang + k * 45)
            x, y = 310 + r * math.cos(a), 310 + r * math.sin(a)
            d.ellipse(((x - 45) * S, (y - 45) * S, (x + 45) * S, (y + 45) * S), outline=(210, 60, 70, 255), width=9 * S)
    tube(d, [(0, 250), (200, 300)], (210, 60, 70, 255), 22)
    tube(d, [(0, 370), (200, 320)], (110, 90, 200, 255), 22)
    return done(im, W, H)


def nephron_pic():
    W, H = 900, 760
    im, d = new(W, H)
    d.ellipse((60 * S, 40 * S, 260 * S, 240 * S), fill=(235, 245, 255, 255), outline=(110, 140, 190, 255), width=7 * S)
    for k in range(6):
        a = math.radians(k * 60)
        x, y = 160 + 40 * math.cos(a), 140 + 40 * math.sin(a)
        d.ellipse(((x - 24) * S, (y - 24) * S, (x + 24) * S, (y + 24) * S), outline=(210, 60, 70, 255), width=6 * S)
    tube(d, [(200, 220), (240, 330), (180, 420), (260, 520), (360, 420), (440, 320), (540, 420), (640, 560), (720, 460), (800, 700)], (245, 205, 120, 255), 34)
    return done(im, W, H)


def filter_pic():
    W, H = 900, 560
    im, d = new(W, H)
    d.rectangle((40 * S, 60 * S, 860 * S, 500 * S), fill=(245, 245, 250, 255), outline=OLN, width=4 * S)
    d.rectangle((420 * S, 60 * S, 480 * S, 500 * S), fill=(220, 190, 160, 255), outline=OLN, width=4 * S)     # filter wall
    for y in range(110, 480, 70):
        d.rectangle((420 * S, y * S, 480 * S, (y + 28) * S), fill=(245, 245, 250, 255))                         # gaps
    for x, y in ((120, 140), (250, 300), (330, 430), (170, 400), (330, 120)):
        d.ellipse(((x - 38) * S, (y - 38) * S, (x + 38) * S, (y + 38) * S), fill=(215, 60, 70, 255), outline=(130, 30, 40, 255), width=4 * S)    # blood cells
    for x, y in ((90, 270), (270, 190), (210, 490)):
        d.ellipse(((x - 24) * S, (y - 24) * S, (x + 24) * S, (y + 24) * S), fill=(150, 110, 200, 255))                                       # proteins
    for x, y in ((380, 150), (560, 145), (620, 215), (580, 285), (680, 340), (610, 410), (730, 460), (540, 450)):
        d.ellipse(((x - 11) * S, (y - 11) * S, (x + 11) * S, (y + 11) * S), fill=(90, 160, 230, 255))                                        # small molecules
    return done(im, W, H)


def reabs_pic():
    W, H = 1000, 460
    im, d = new(W, H)
    tube(d, [(60, 300), (940, 300)], (245, 205, 120, 255), 120)
    for x in range(120, 900, 90):
        d.ellipse((x * S, 270 * S, (x + 28) * S, (270 + 36) * S), fill=(90, 160, 230, 255))
    for x in range(150, 900, 180):
        d.polygon([((x - 20) * S, 215 * S), ((x + 20) * S, 215 * S), (x * S, 150 * S)], fill=(60, 120, 200, 255))
        d.line([(x * S, 150 * S), (x * S, 70 * S)], fill=(60, 120, 200, 255), width=8 * S)
    d.rounded_rectangle((60 * S, 20 * S, 940 * S, 70 * S), radius=24 * S, fill=(245, 175, 175, 255), outline=(180, 70, 80, 255), width=5 * S)
    return done(im, W, H)


def rbc_pic():
    W, H = 360, 360
    im, d = new(W, H)
    d.ellipse((30 * S, 30 * S, 330 * S, 330 * S), fill=(215, 60, 70, 255), outline=(130, 30, 40, 255), width=8 * S)
    d.ellipse((115 * S, 115 * S, 245 * S, 245 * S), fill=(235, 120, 125, 255))
    return done(im, W, H)


def sun_pic():
    W, H = 360, 360
    im, d = new(W, H)
    for k in range(12):
        a = math.radians(k * 30)
        d.line([((180 + 100 * math.cos(a)) * S, (180 + 100 * math.sin(a)) * S), ((180 + 160 * math.cos(a)) * S, (180 + 160 * math.sin(a)) * S)], fill=(250, 190, 50, 255), width=14 * S)
    d.ellipse((90 * S, 90 * S, 270 * S, 270 * S), fill=(255, 220, 90, 255), outline=(210, 160, 30, 255), width=7 * S)
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
    kid = sv("rein_01")

    # ---------------- STORY (A)
    s = sc["story"]
    st = [pop(tub_pic(), 520, 520, w=860, t=0.3), text("150 - 180 liters filtered", 1380, 200, 66, BLUE_T, s.t("liters") - 0.8, "c"), text("enough to fill a bathtub", 1380, 320, 56, MAROON, s.t("bathtub") - 0.5, "c"),
          text("urine: only 1 - 2 liters", 1380, 520, 70, GOLD_T, s.t("urine") - 0.6, "c"), text("where does the rest go?", 1380, 780, 80, RED_T, s.t("rest") - 0.4, "c")]

    # ---------------- OVERVIEW (B)
    s = sc["overview"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, st)
    X = PW
    ov = [pop(urinary_pic(), X + 420, 540, h=980, t=s.start + 0.3), text("2 KIDNEYS", X + 1330, 150, 80, RED_T, s.t("kidneys") - 0.3, "c"), text("each the size of a FIST", X + 1330, 260, 56, MAROON, s.t("fist") - 0.5, "c"),
          text("just below the rib cage", X + 1330, 400, 56, BLUE_T, s.t("rib") - 0.5, "c"), text("ureters", X + 1330, 600, 62, GOLD_T, s.t("ureters") - 0.3, "c"),
          text("bladder", X + 1330, 700, 62, GOLD_T, s.t("bladder") - 0.3, "c"), text("urethra", X + 1330, 800, 62, GOLD_T, s.t("urethra") - 0.3, "c")]

    # ---------------- BLOOD (C)
    s = sc["blood"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ov)
    X = 2 * PW
    bl = [pop(kid, X + 520, 540, h=640, t=s.start + 0.3), text("renal ARTERY in", X + 1380, 200, 70, RED_T, s.t("artery") - 0.4, "c"), text("renal VEIN out", X + 1380, 330, 70, BLUE_T, s.t("vein") - 0.4, "c"),
          text("a QUARTER of the heart's blood", X + 1380, 560, 62, GOLD_T, s.t("quarter") - 0.5, "c"), text("a little over 1 liter / minute", X + 1380, 690, 46, MAROON, s.t("quarter") - 0.3, "c")]

    # ---------------- NEPHRON (D)
    s = sc["nephron"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, bl)
    ne = [pop(nephron_pic(), 520, Y + 540, h=900, t=s.start + 0.3), text("about a MILLION nephrons", 1400, Y + 200, 68, GOLD_T, s.t("million") - 0.6, "c"), text("in each kidney", 1400, Y + 300, 54, MAROON, s.t("kidney") - 0.5, "c"),
          text("GLOMERULUS = the filter", 1400, Y + 520, 62, RED_T, s.t("glomerulus") - 0.5, "c"), text("TUBULE = long tube", 1400, Y + 680, 62, BLUE_T, s.t("tubule") - 1.0, "c")]

    # ---------------- FILTER (E)
    s = sc["filter"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, ne)
    X = PW
    fl = [pop(filter_pic(), X + 560, Y + 540, w=940, t=s.start + 0.3), text("water, salts, sugar, waste", X + 1560, Y + 220, 52, BLUE_T, s.t("salts") - 0.9, "c"), text("squeezed THROUGH", X + 1560, Y + 310, 52, BLUE_T, s.t("pushes") - 0.5, "c"),
          text("blood cells + big proteins", X + 1560, Y + 560, 52, RED_T, s.t("cells") - 0.6, "c"), text("STAY behind", X + 1560, Y + 650, 64, PURPLE, s.t("stay") - 0.5, "c")]

    # ---------------- REABSORB (F)
    s = sc["reabsorb"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, fl)
    X = 2 * PW
    ra = [pop(reabs_pic(), X + 560, Y + 360, w=1000, t=s.start + 0.3), text("the body TAKES BACK", X + 560, Y + 680, 76, GREEN_T, s.t("takes") - 0.5, "c"), text("water, sugar, salts", X + 560, Y + 780, 56, MAROON, s.t("sugar") - 0.5, "c"),
          text("99%", X + 1560, Y + 260, 220, RED_T, s.t("ninety") - 0.5, "c"), text("reabsorbed", X + 1560, Y + 470, 70, GOLD_T, s.t("reabsorbed") - 0.5, "c"), text("left: waste + extra water", X + 1500, Y + 700, 46, BLUE_T, s.t("urine") - 1.8, "c"), text("= URINE", X + 1500, Y + 780, 60, GOLD_T, s.t("urine") - 1.4, "c")]

    # ---------------- BALANCE (A)
    s = sc["balance"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, ra)
    ba = title("fine tuning", 960, 140, s.start + 0.3) + [text("how much WATER stays", 960, 460, 90, BLUE_T, s.t("water") - 0.4, "c"), text("how much SALT stays", 960, 640, 90, GOLD_T, s.t("salt") - 0.4, "c"),
          text("second by second", 960, 860, 70, MAROON, s.t("second") - 0.4, "c")]

    # ---------------- URINE (B)
    s = sc["urine"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, ba)
    X = PW
    ur = [pop(urinary_pic(), X + 520, 540, h=980, t=s.start + 0.3), text("kidney", X + 1380, 220, 66, RED_T, s.t("collects") - 0.5, "c"), text("ureters", X + 1380, 420, 66, GOLD_T, s.t("ureters") - 0.3, "c"),
          text("bladder", X + 1380, 620, 66, GOLD_T, s.t("bladder") - 0.9, "c"), text("urethra - out", X + 1380, 820, 66, GOLD_T, s.t("urethra") - 1.3, "c")]

    # ---------------- JOBS (C)
    s = sc["jobs"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ur)
    X = 2 * PW
    jb = title("more than cleaning", X + 960, 110, s.start + 0.3) + [
        pop(sv("cuff_gauge"), X + 330, 480, h=300, t=s.t("renin") - 0.9), text("RENIN", X + 330, 700, 62, RED_T, s.t("renin") - 0.4, "c"), text("blood pressure", X + 330, 780, 46, MAROON, s.t("pressure") - 0.5, "c"),
        pop(rbc_pic(), X + 960, 480, h=260, t=s.t("erythropoietin") - 1.1), text("ERYTHROPOIETIN", X + 960, 700, 50, PURPLE, s.t("erythropoietin") - 0.5, "c"), text("red blood cells", X + 960, 780, 46, MAROON, s.t("bone") - 0.9, "c"),
        pop(sun_pic(), X + 1590, 480, h=260, t=s.t("vitamin") - 0.9), text("VITAMIN D", X + 1590, 700, 62, GOLD_T, s.t("vitamin") - 0.5, "c"), text("activated", X + 1590, 780, 46, MAROON, s.t("activate") - 0.4, "c")]

    # ---------------- RECAP (D)
    s = sc["recap"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, jb)
    rp = title("remember 3 things", 960, Y + 100, s.start + 0.4)
    for w, a, b, col, tc_, x in (("filter", "kidneys filter", "your blood", PINK, RED_T, 400), ("taken", "most fluid is taken back", "the rest = urine", CREAM, GOLD_T, 960), ("pressure", "they help control", "blood pressure + red cells", SKY, BLUE_T, 1520)):
        tw2 = s.t(w) - 0.3
        rp += [panel(x - 265, Y + 220, x + 265, Y + 600, col, tw2 - 0.2), text(a, x, Y + 360, 38, tc_, tw2, "c"), text(b, x, Y + 470, 34, MAROON, tw2 + 0.6, "c")]
    tn = s.t("immune") - 0.8
    rp += [panel(200, Y + 720, 1720, Y + 890, LILAC, tn - 0.3), text("next: the immune system", 960, Y + 820, 56, PURPLE, tn, "c")]

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
    kid = sv("rein_01")
    if n == 1:
        s = sc["case"]
        a = [pop(tub_pic(), 520, 520, w=860, t=0.3), text("filtered: 150 - 180 L", 1400, 220, 72, BLUE_T, s.t("liters") - 0.8, "c"), text("every day", 1400, 340, 60, MAROON, s.t("day") - 0.5, "c"),
             text("urine: only 1 - 2 L", 1400, 560, 76, GOLD_T, s.t("pass") - 0.4, "c")]
        s = sc["turn"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(reabs_pic(), X + 560, 460, w=980, t=s.start + 0.3), text("where does the rest go?", X + 1400, 800, 72, RED_T, s.t("where") - 0.4, "c"), text("a clever trick in a tiny tube", X + 560, 780, 56, GOLD_T, s.t("trick") - 0.5, "c")]
    else:
        s = sc["case"]
        a = [pop(kid, 520, 540, h=640, t=0.3), text("size of a FIST", 1400, 250, 90, RED_T, s.t("fist") - 0.5, "c"), text("gets a QUARTER", 1400, 520, 80, GOLD_T, s.t("quarter") - 0.5, "c"),
             text("of the heart's blood", 1400, 640, 60, MAROON, s.t("quarter") - 0.8, "c")]
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(nephron_pic(), X + 520, 540, h=800, t=s.start + 0.3), text("cleaned again and again", X + 1400, 400, 70, BLUE_T, s.t("again") - 0.8, "c"), text("all day long", X + 1400, 540, 70, MAROON, s.t("day") - 0.4, "c")]
        s = sc["clue"]
        cam(s.start, *C, 1.0, 1.0)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        c = [pop(rbc_pic(), X + 520, 540, h=420, t=s.t("message") - 0.8), text("a message to the BONE MARROW", X + 1400, 300, 62, PURPLE, s.t("message") - 0.4, "c"), text("what is it?", X + 1400, 540, 100, GOLD_T, s.t("what") - 0.3, "c"),
             text("?", X + 1400, 820, 220, GOLD_T, s.t("what") - 0.1, "c")]

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
    board = NU.render_board(bd, sc, f"kid_story{n}")
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
    ov = OUT / f"kid_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"kid_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["kidney"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "kidney", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"kid_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"kshort{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "kid", intro=True)
        f.replace(OUT / "final_kid.mp4")
        print("done ->", OUT / "final_kid.mp4")
