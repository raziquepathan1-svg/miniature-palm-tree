"""Lymphatic system video (fact-checked 14 Nov 2026) + 2 story Shorts.

    python3 osm_lymph.py [stills] | short 1|2 [stills]
Env: EP_DIR (default ../lymph), OUT_DIR.
"""
import math
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "lymph")))
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
import osm_immune as IM  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OB.PINK, OB.LILAC, OB.CREAM, OB.MINT, OB.SKY
PW, PH = 1920, 1080
sv = OB.sv
SHORT_TITLES = {1: "Your Second Drainage System", 2: "Lumps In Your Neck"}
SHORT_Q = {1: "So what is the drainage network?", 2: "So what are these lumps called?"}
S = 3
new, done, tube = DG.new, DG.done, DG.tube
OL = (90, 80, 70, 255)
LYM = (240, 210, 90, 255)
BLOOD = (200, 50, 60, 255)


def leak_pic():
    W, H = 900, 520
    im, d = new(W, H)
    d.rectangle((0, 0, W * S, 150 * S), fill=(245, 200, 200, 255), outline=OL, width=4 * S)        # blood vessel
    d.rectangle((0, 150 * S, W * S, H * S), fill=(250, 235, 215, 255), outline=OL, width=4 * S)    # tissue
    for x in range(80, 860, 110):
        d.ellipse((x * S, 50 * S, (x + 30) * S, 80 * S), fill=BLOOD)
    for x, y in ((150, 230), (300, 300), (460, 250), (620, 320), (760, 240), (220, 400), (540, 420)):
        d.ellipse(((x - 11) * S, (y - 11) * S, (x + 11) * S, (y + 11) * S), fill=(120, 190, 240, 255))
        d.line([(x * S, (y - 30) * S), (x * S, 150 * S)], fill=(120, 190, 240, 120), width=3 * S)
    return done(im, W, H)


def drain_pic():
    W, H = 900, 520
    im, d = new(W, H)
    d.rectangle((0, 40 * S, W * S, 120 * S), fill=(245, 200, 200, 255), outline=OL, width=4 * S)
    d.rectangle((0, 400 * S, W * S, 500 * S), fill=(250, 235, 215, 255), outline=OL, width=4 * S)
    tube(d, [(80, 400), (140, 300), (240, 260), (420, 260), (600, 230), (780, 140), (820, 90)], LYM, 30)
    for x, y in ((190, 340), (330, 330), (470, 310)):
        d.ellipse(((x - 10) * S, (y - 10) * S, (x + 10) * S, (y + 10) * S), fill=(120, 190, 240, 255))
    d.polygon([(780 * S, 60 * S), (840 * S, 100 * S), (780 * S, 140 * S)], fill=(60, 140, 90, 255))
    return done(im, W, H)


def valves_pic():
    W, H = 900, 360
    im, d = new(W, H)
    tube(d, [(40, 180), (860, 180)], LYM, 110)
    for x in (220, 420, 620):
        d.polygon([((x - 28) * S, 130 * S), ((x + 28) * S, 130 * S), (x * S, 180 * S)], fill=(60, 140, 90, 255))
        d.polygon([((x - 28) * S, 230 * S), ((x + 28) * S, 230 * S), (x * S, 180 * S)], fill=(60, 140, 90, 255))
    d.polygon([(780 * S, 150 * S), (860 * S, 180 * S), (780 * S, 210 * S)], fill=(60, 120, 60, 255))
    return done(im, W, H)


def node_pic(big=False):
    W, H = 640, 420
    im, d = new(W, H)
    k = 1.25 if big else 1.0
    cx, cy = 320, 210
    d.ellipse(((cx - 200 * k) * S, (cy - 110 * k) * S, (cx + 200 * k) * S, (cy + 110 * k) * S), fill=(205, 230, 170, 255), outline=(100, 140, 70, 255), width=6 * S)
    tube(d, [(0, 210), (cx - 190 * k, 210)], LYM, 16)
    tube(d, [(cx + 190 * k, 210), (640, 210)], LYM, 16)
    for x, y in ((230, 170), (300, 250), (380, 180), (430, 260), (260, 215), (350, 215)):
        d.ellipse(((x - 16) * S, (y - 16) * S, (x + 16) * S, (y + 16) * S), fill=(130, 100, 200, 255))
    return done(im, W, H)


def network_pic():
    W, H = 640, 1000
    im, d = new(W, H)
    sil = sv("Male-silhouette").convert("RGBA").resize((int(673 * 1000 / 1207), 1000))
    im2 = im.resize((W * S, H * S)) if False else None
    big = sil.resize((sil.width * S, sil.height * S))
    im.paste(big, ((W * S - big.width) // 2, 0), big)
    cx = W * S // 2
    nodes = [(cx - 0 * S, 150 * S), (cx - 120 * S, 255 * S), (cx + 120 * S, 255 * S), (cx - 12 * S, 330 * S), (cx - 70 * S, 520 * S), (cx + 70 * S, 520 * S), (cx - 85 * S, 700 * S), (cx + 85 * S, 700 * S)]
    for (x, y) in nodes:
        d.ellipse((x - 14 * S, y - 14 * S, x + 14 * S, y + 14 * S), fill=(130, 190, 80, 255), outline=(60, 110, 40, 255), width=3 * S)
    d.line([(cx, 150 * S), (cx, 330 * S), (cx, 520 * S)], fill=LYM, width=5 * S)
    d.line([(cx - 120 * S, 255 * S), (cx, 300 * S), (cx + 120 * S, 255 * S)], fill=LYM, width=5 * S)
    d.line([(cx, 520 * S), (cx - 85 * S, 700 * S)], fill=LYM, width=5 * S)
    d.line([(cx, 520 * S), (cx + 85 * S, 700 * S)], fill=LYM, width=5 * S)
    return done(im, W, H)


def organs_pic(kind):
    W, H = 360, 300
    im, d = new(W, H)
    if kind == "spleen":
        d.ellipse((40 * S, 50 * S, 320 * S, 250 * S), fill=(170, 80, 130, 255), outline=(100, 40, 80, 255), width=6 * S)
    elif kind == "thymus":
        d.ellipse((50 * S, 60 * S, 170 * S, 250 * S), fill=(235, 200, 120, 255), outline=(170, 130, 50, 255), width=6 * S)
        d.ellipse((190 * S, 60 * S, 310 * S, 250 * S), fill=(235, 200, 120, 255), outline=(170, 130, 50, 255), width=6 * S)
    else:
        d.ellipse((50 * S, 90 * S, 170 * S, 220 * S), fill=(235, 150, 150, 255), outline=(150, 70, 80, 255), width=6 * S)
        d.ellipse((190 * S, 90 * S, 310 * S, 220 * S), fill=(235, 150, 150, 255), outline=(150, 70, 80, 255), width=6 * S)
    return done(im, W, H)


def lacteal_pic():
    W, H = 640, 640
    im, d = new(W, H)
    d.rounded_rectangle((200 * S, 40 * S, 440 * S, 640 * S), radius=120 * S, fill=(250, 205, 190, 255), outline=OL, width=6 * S)
    tube(d, [(320, 600), (320, 140)], LYM, 44)
    tube(d, [(260, 560), (260, 200)], BLOOD, 14)
    for x, y in ((120, 200), (90, 340), (140, 480), (520, 280), (550, 420)):
        d.ellipse(((x - 18) * S, (y - 18) * S, (x + 18) * S, (y + 18) * S), fill=(250, 230, 130, 255), outline=(190, 150, 40, 255), width=3 * S)
    return done(im, W, H)


def swollen_arm_pic(swollen=True):
    W, H = 900, 460
    im, d = new(W, H)
    h = 150 if swollen else 100
    d.rounded_rectangle((60 * S, (230 - h) * S, 780 * S, (230 + h) * S), radius=h * S, fill=(250, 205, 180, 255), outline=(170, 110, 90, 255), width=6 * S)
    d.ellipse((730 * S, 150 * S, 880 * S, 310 * S), fill=(250, 205, 180, 255), outline=(170, 110, 90, 255), width=6 * S)
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
    st = [pop(leak_pic(), 520, 540, w=900, t=0.3), text("fluid slips out", 1400, 220, 80, BLUE_T, s.t("slips") - 0.4, "c"), text("of tiny blood vessels", 1400, 330, 60, MAROON, s.t("vessels") - 0.5, "c"),
          text("nowhere to go = SWELLING", 1400, 560, 64, RED_T, s.t("swell") - 0.7, "c"), text("where does it go?", 1400, 800, 84, PURPLE, s.t("where") - 0.4, "c")]

    # ---------------- OVERVIEW (B)
    s = sc["overview"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, st)
    X = PW
    ov = [pop(network_pic(), X + 480, 540, h=980, t=s.start + 0.3), text("the LYMPHATIC SYSTEM", X + 1420, 180, 72, GREEN_T, s.t("lymphatic") - 0.4, "c"),
          text("vessels - nodes - organs", X + 1420, 330, 58, MAROON, s.t("network") - 0.5, "c"), text("carries LYMPH", X + 1420, 520, 86, GOLD_T, s.t("lymph") - 0.4, "c"),
          text("= interstitial fluid", X + 1420, 650, 60, BLUE_T, s.t("interstitial") - 0.5, "c"), text("(the fluid between cells)", X + 1420, 740, 46, MAROON, s.t("between") - 0.6, "c")]

    # ---------------- DRAIN (C)
    s = sc["drain"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ov)
    X = 2 * PW
    dr = [pop(drain_pic(), X + 520, 400, w=900, t=s.start + 0.3), text("lymphatic CAPILLARIES absorb it", X + 1450, 200, 52, GREEN_T, s.t("capillaries") - 0.5, "c"),
          text("= LYMPH", X + 1450, 320, 80, GOLD_T, s.t("becomes") - 0.4, "c"), text("returned to the blood", X + 1450, 450, 56, BLUE_T, s.t("returned") - 0.5, "c"),
          text("SUBCLAVIAN veins (collarbone)", X + 960, 800, 60, RED_T, s.t("subclavian") - 0.5, "c"), text("mystery solved!", X + 960, 940, 84, GREEN_T, s.t("solved") - 0.4, "c")]

    # ---------------- VESSELS (D)
    s = sc["vessels"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, dr)
    ve = [pop(valves_pic(), 520, Y + 380, w=900, t=s.start + 0.3), text("no heart to push it", 1400, Y + 230, 66, RED_T, s.t("heart") - 0.5, "c"), text("VALVES: one way only", 960, Y + 700, 70, GREEN_T, s.t("valves") - 0.4, "c"),
          text("squeezing muscles help push", 960, Y + 830, 56, BLUE_T, s.t("squeezing") - 0.6, "c")]

    # ---------------- NODES (E)
    s = sc["nodes"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, ve)
    X = PW
    nd = [pop(node_pic(), X + 480, Y + 400, w=780, t=s.start + 0.3), text("LYMPH NODES", X + 1450, Y + 160, 80, GREEN_T, s.t("nodes") - 0.3, "c"), text("about 600", X + 1450, Y + 290, 90, GOLD_T, s.t("six") - 0.5, "c"),
          text("filter lymph: debris + germs", X + 1450, Y + 460, 54, MAROON, s.t("filter") - 0.5, "c"), text("contain lymphocytes", X + 1450, Y + 570, 58, PURPLE, s.t("lymphocytes") - 0.5, "c"),
          pop(node_pic(True), X + 480, Y + 820, w=560, t=s.t("infection") - 0.6), text("infection = nodes can SWELL", X + 1300, Y + 860, 50, RED_T, s.t("infection") - 0.2, "c")]

    # ---------------- ORGANS (F)
    s = sc["organs"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, nd)
    X = 2 * PW
    og = [pop(organs_pic("spleen"), X + 330, Y + 400, w=480, t=s.t("spleen") - 0.9), text("SPLEEN", X + 330, Y + 620, 70, PURPLE, s.t("spleen") - 0.4, "c"), text("filters BLOOD", X + 330, Y + 710, 50, MAROON, s.t("blood") - 0.6, "c"),
          pop(organs_pic("thymus"), X + 960, Y + 400, w=480, t=s.t("thymus") - 0.9), text("THYMUS", X + 960, Y + 620, 70, GOLD_T, s.t("thymus") - 0.4, "c"), text("T cells mature", X + 960, Y + 710, 50, MAROON, s.t("mature") - 0.6, "c"),
          pop(organs_pic("tonsils"), X + 1590, Y + 400, w=480, t=s.t("tonsils") - 0.9), text("TONSILS", X + 1590, Y + 620, 70, RED_T, s.t("tonsils") - 0.4, "c"), text("help block germs", X + 1590, Y + 710, 50, MAROON, s.t("block") - 0.6, "c")]

    # ---------------- LACTEALS (A)
    s = sc["lacteals"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, og)
    la = [pop(lacteal_pic(), 480, 540, h=860, t=s.start + 0.3), text("small intestine", 1400, 220, 66, MAROON, s.t("intestine") - 0.4, "c"), text("LACTEALS", 1400, 400, 100, GREEN_T, s.t("lacteals") - 0.4, "c"),
          text("absorb dietary FATS", 1400, 600, 70, GOLD_T, s.t("fats") - 0.7, "c")]

    # ---------------- EDEMA (B)
    s = sc["edema"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, la)
    X = PW
    ed = [pop(swollen_arm_pic(True), X + 520, 420, w=900, t=s.start + 0.3), text("lymph cannot drain", X + 1450, 160, 62, MAROON, s.t("drain") - 0.4, "c"), text("= fluid builds up", X + 1450, 270, 62, BLUE_T, s.t("builds") - 0.5, "c"),
          text("LYMPHEDEMA", X + 1450, 480, 90, RED_T, s.t("lymphedema") - 0.4, "c"), text("arms or legs", X + 1450, 600, 56, GOLD_T, s.t("arms") - 0.5, "c"),
          panel(X + 200, 760, X + 1720, 940, MINT, s.t("doctor") - 2.0), text("swelling or a lump? see a doctor", X + 960, 850, 62, GREEN_T, s.t("doctor") - 1.7, "c")]

    # ---------------- RECAP (C)
    s = sc["recap"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ed)
    X = 2 * PW
    rp = title("remember 3 things", X + 960, 100, s.start + 0.4)
    for w, a, b, col, tc_, x in (("drains", "drains tissue fluid", "returns it to blood", PINK, RED_T, 400), ("filter", "nodes filter lymph", "and house immune cells", CREAM, GOLD_T, 960), ("lacteals", "lacteals help", "absorb fats", MINT, GREEN_T, 1520)):
        tw2 = s.t(w) - 0.3
        rp += [panel(X + x - 265, 220, X + x + 265, 600, col, tw2 - 0.2), text(a, X + x, 360, 40, tc_, tw2, "c"), text(b, X + x, 470, 36, MAROON, tw2 + 0.6, "c")]
    tn = s.t("senses") - 0.8
    rp += [panel(X + 200, 720, X + 1720, 890, LILAC, tn - 0.3), text("next: the senses", X + 960, 820, 56, PURPLE, tn, "c")]

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
        a = [pop(leak_pic(), 520, 540, w=900, t=0.3), text("fluid leaks out", 1400, 260, 84, BLUE_T, s.t("leaks") - 0.4, "c"), text("of tiny blood vessels", 1400, 380, 60, MAROON, s.t("smallest") - 0.8, "c")]
        s = sc["turn"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(leak_pic(), X + 520, 540, w=900, t=s.start + 0.3), text("never drained = SWELLING", X + 1450, 260, 62, RED_T, s.t("swell") - 0.6, "c"), text("a second drainage network", X + 1450, 480, 58, GREEN_T, s.t("second") - 0.4, "c"),
             text("?", X + 1450, 820, 220, GOLD_T, s.t("what") - 0.2, "c")]
    else:
        s = sc["case"]
        a = [pop(node_pic(True), 520, 540, w=800, t=0.3), text("sick? small lumps", 1400, 260, 72, MAROON, s.t("lumps") - 0.5, "c"), text("swell in your neck", 1400, 400, 72, RED_T, s.t("neck") - 0.5, "c")]
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(network_pic(), X + 480, 540, h=960, t=s.start + 0.3), text("those lumps are FILTERS", X + 1450, 300, 66, GREEN_T, s.t("filters") - 0.5, "c"), text("a network through", X + 1450, 520, 62, MAROON, s.t("network") - 0.6, "c"),
             text("your whole body", X + 1450, 620, 62, MAROON, s.t("whole") - 0.5, "c")]
        s = sc["clue"]
        cam(s.start, *C, 1.0, 1.0)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        c = [pop(node_pic(), X + 520, 540, w=800, t=s.start + 0.3), text("what are they called?", X + 1450, 380, 80, GOLD_T, s.t("what") - 0.2, "c"), text("?", X + 1450, 700, 220, GOLD_T, s.t("called") - 0.1, "c")]

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
    board = NU.render_board(bd, sc, f"lym_story{n}")
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
    ov = OUT / f"lym_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"lym_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["lymph"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "lymph", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"lym_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"lshort{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "lym", intro=True)
        f.replace(OUT / "final_lym.mp4")
        print("done ->", OUT / "final_lym.mp4")
