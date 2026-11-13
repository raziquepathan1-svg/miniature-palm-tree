"""Skin (integumentary) video (fact-checked 13 Nov 2026) + 2 story Shorts.

    python3 osm_skin.py [stills] | short 1|2 [stills]
Env: EP_DIR (default ../skin), OUT_DIR.
"""
import math
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "skin")))
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
import osm_auto as AU  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OB.PINK, OB.LILAC, OB.CREAM, OB.MINT, OB.SKY
PW, PH = 1920, 1080
SHORT_TITLES = {1: "Dead Cells As A Shield", 2: "Your Built In Sunscreen"}
SHORT_Q = {1: "So how do dead cells protect you?", 2: "So what is the pigment called?"}
S = 3
new, done, tube = DG.new, DG.done, DG.tube
OL = (120, 80, 70, 255)
EPI, DER, HYP = (245, 190, 170, 255), (240, 150, 140, 255), (250, 225, 150, 255)


def section_pic():
    W, H = 900, 760
    im, d = new(W, H)
    d.rectangle((0, 40 * S, W * S, 150 * S), fill=EPI, outline=OL, width=5 * S)
    d.rectangle((0, 150 * S, W * S, 500 * S), fill=DER, outline=OL, width=5 * S)
    d.rectangle((0, 500 * S, W * S, 740 * S), fill=HYP, outline=OL, width=5 * S)
    for x in range(10, W, 36):
        d.rounded_rectangle((x * S, 40 * S, (x + 32) * S, 62 * S), radius=8 * S, fill=(225, 205, 180, 255), outline=OL, width=2 * S)
    for cx in range(80, 860, 120):
        d.ellipse((cx * S, 540 * S, (cx + 90) * S, 620 * S), fill=(255, 240, 190, 255), outline=(190, 150, 60, 255), width=4 * S)
        d.ellipse(((cx + 40) * S, 640 * S, (cx + 140) * S, 720 * S), fill=(255, 240, 190, 255), outline=(190, 150, 60, 255), width=4 * S)
    d.line([(120 * S, 40 * S), (140 * S, 0)], fill=(80, 50, 40, 255), width=6 * S)
    d.line([(160 * S, 150 * S), (200 * S, 400 * S), (215 * S, 440 * S)], fill=(80, 50, 40, 255), width=14 * S)
    d.ellipse((190 * S, 420 * S, 250 * S, 480 * S), fill=(200, 160, 140, 255), outline=OL, width=4 * S)
    tube(d, [(500, 160), (520, 300), (470, 400), (560, 460)], (190, 40, 50, 255), 22)
    tube(d, [(700, 160), (690, 280), (730, 380), (680, 450)], (200, 160, 220, 255), 14)
    return done(im, W, H)


def dead_cells_pic(rows=4):
    W, H = 900, 380
    im, d = new(W, H)
    for r in range(rows):
        for c in range(9):
            x = 20 + c * 98 + (46 if r % 2 else 0)
            d.rounded_rectangle((x * S, (30 + r * 70) * S, (x + 94) * S, (30 + r * 70 + 54) * S), radius=22 * S, fill=(225, 205, 180, 255), outline=(150, 120, 100, 255), width=4 * S)
            d.line([((x + 18) * S, (30 + r * 70 + 27) * S), ((x + 76) * S, (30 + r * 70 + 27) * S)], fill=(190, 160, 120, 255), width=4 * S)
    return done(im, W, H)


def column_pic():
    W, H = 640, 860
    im, d = new(W, H)
    for k in range(6):
        y = 790 - k * 130
        r_h = 62 - k * 8
        w = 90 + k * 14
        col = (250, 190, 180, 255) if k < 2 else ((240, 215, 190, 255) if k < 4 else (225, 205, 180, 255))
        for dx in (-1, 0, 1):
            cx = 330 + dx * (w + 10)
            d.ellipse(((cx - w / 2) * S, (y - r_h / 2) * S, (cx + w / 2) * S, (y + r_h / 2) * S), fill=col, outline=OL, width=4 * S)
    d.line([(40 * S, 760 * S), (40 * S, 80 * S)], fill=(60, 120, 200, 255), width=10 * S)
    d.polygon([(10 * S, 110 * S), (70 * S, 110 * S), (40 * S, 40 * S)], fill=(60, 120, 200, 255))
    return done(im, W, H)


def melanocyte_pic():
    W, H = 640, 520
    im, d = new(W, H)
    d.rectangle((0, 400 * S, W * S, H * S), fill=EPI, outline=OL, width=4 * S)
    d.ellipse((190 * S, 250 * S, 450 * S, 420 * S), fill=(205, 160, 120, 255), outline=OL, width=5 * S)
    for ex in (60, 170, 320, 470, 580):
        d.line([(320 * S, 320 * S), (ex * S, 130 * S)], fill=(150, 100, 70, 255), width=14 * S)
    for x, y in ((90, 180), (130, 130), (240, 190), (330, 150), (430, 170), (520, 130), (560, 200), (300, 300), (350, 330)):
        d.ellipse(((x - 14) * S, (y - 14) * S, (x + 14) * S, (y + 14) * S), fill=(110, 70, 40, 255))
    return done(im, W, H)


def sun_pic(r=110):
    W = 2 * (r + 70)
    im, d = new(W, W)
    c = W // 2
    for k in range(12):
        a = math.radians(k * 30)
        d.line([((c + (r + 10) * math.cos(a)) * S, (c + (r + 10) * math.sin(a)) * S), ((c + (r + 65) * math.cos(a)) * S, (c + (r + 65) * math.sin(a)) * S)], fill=(250, 190, 50, 255), width=12 * S)
    d.ellipse(((c - r) * S, (c - r) * S, (c + r) * S, (c + r) * S), fill=(255, 220, 90, 255), outline=(210, 160, 30, 255), width=6 * S)
    return done(im, W, W)


def dermis_pic():
    W, H = 900, 640
    im, d = new(W, H)
    d.rectangle((0, 0, W * S, H * S), fill=DER, outline=OL, width=5 * S)
    for k in range(8):
        pts = [(x, 60 + k * 70 + 18 * math.sin(x / 40 + k)) for x in range(20, 880, 20)]
        d.line([(x * S, y * S) for x, y in pts], fill=(255, 225, 200, 255), width=6 * S)
    tube(d, [(100, 100), (200, 200), (160, 330), (260, 420)], (190, 40, 50, 255), 24)
    d.line([(420 * S, 0), (440 * S, 280), ], fill=(80, 50, 40, 255), width=8 * S) if False else None
    d.line([(640 * S, 30 * S), (660 * S, 300 * S), (680 * S, 340 * S)], fill=(80, 50, 40, 255), width=14 * S)
    d.ellipse((650 * S, 320 * S, 720 * S, 390 * S), fill=(200, 160, 140, 255), outline=OL, width=4 * S)
    tube(d, [(480, 60), (500, 240), (470, 330)], (200, 170, 230, 255), 12)
    for k in range(5):
        d.arc((430 * S, (360 + k * 38) * S, 520 * S, (400 + k * 38) * S), 0, 180, fill=(150, 200, 230, 255), width=7 * S)
    return done(im, W, H)


def gland_pic():
    W, H = 640, 520
    im, d = new(W, H)
    d.rectangle((0, 0, W * S, 120 * S), fill=EPI, outline=OL, width=4 * S)
    tube(d, [(200, 120), (200, 260)], (150, 200, 235, 255), 16)
    for k in range(5):
        d.ellipse(((150 + k * 6) * S, (260 + k * 36) * S, (250 - k * 6) * S, (320 + k * 36) * S), outline=(90, 150, 210, 255), width=8 * S)
    for x, y in ((170, 70), (230, 40), (210, 90)):
        d.polygon([((x - 12) * S, (y + 8) * S), ((x + 12) * S, (y + 8) * S), (x * S, (y - 24) * S)], fill=(150, 200, 240, 255))
    tube(d, [(460, 120), (460, 220)], (245, 220, 120, 255), 16)
    d.ellipse((380 * S, 220 * S, 540 * S, 330 * S), fill=(250, 235, 150, 255), outline=(190, 150, 40, 255), width=6 * S)
    return done(im, W, H)


def fat_pic():
    W, H = 900, 420
    im, d = new(W, H)
    for r in range(3):
        for c in range(7):
            x = 30 + c * 120 + (55 if r % 2 else 0)
            d.ellipse((x * S, (20 + r * 130) * S, (x + 110) * S, (20 + r * 130 + 120) * S), fill=(255, 240, 190, 255), outline=(190, 150, 60, 255), width=5 * S)
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
    st = [pop(dead_cells_pic(), 520, 520, w=860, t=0.3), text("the part you SEE and TOUCH", 1380, 200, 64, MAROON, s.t("see") - 0.5, "c"), text("= DEAD cells", 1380, 340, 100, RED_T, s.t("dead") - 0.4, "c"),
          text("yet it protects your body", 1380, 560, 62, GOLD_T, s.t("protects") - 0.5, "c"), text("how can dead cells do that?", 1380, 800, 70, PURPLE, s.t("how") - 0.4, "c")]

    # ---------------- OVERVIEW (B)
    s = sc["overview"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, st)
    X = PW
    ov = [pop(section_pic(), X + 520, 540, h=900, t=s.start + 0.3), text("the LARGEST organ", X + 1450, 160, 68, GOLD_T, s.t("largest") - 0.4, "c"),
          text("EPIDERMIS", X + 1450, 360, 80, RED_T, s.t("epidermis") - 0.3, "c"), text("DERMIS", X + 1450, 520, 80, MAROON, s.t("dermis") - 0.3, "c"), text("HYPODERMIS", X + 1450, 680, 80, GOLD_T, s.t("hypodermis") - 0.5, "c")]

    # ---------------- EPIDERMIS (C)
    s = sc["epidermis"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ov)
    X = 2 * PW
    ep = [pop(column_pic(), X + 480, 540, h=900, t=s.start + 0.3), text("EPIDERMIS", X + 1450, 130, 80, RED_T, s.t("epidermis") - 0.3, "c"), text("90% keratinocytes", X + 1450, 270, 64, GOLD_T, s.t("ninety") - 0.6, "c"),
          text("they make KERATIN", X + 1450, 400, 64, BLUE_T, s.t("keratin") - 0.5, "c"), text("new cells form at the bottom", X + 1450, 600, 52, MAROON, s.t("bottom") - 0.8, "c"),
          text("outer cells: dead, flat", X + 1450, 740, 56, PURPLE, s.t("outermost") - 1.2, "c")]

    # ---------------- PROTECT (D)
    s = sc["protect"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, ep)
    pr = [pop(dead_cells_pic(3), 520, Y + 420, w=860, t=s.start + 0.3), text("mystery solved!", 1400, Y + 200, 90, GREEN_T, s.t("answer") - 0.4, "c"),
          text("dead, keratin-filled cells", 1400, Y + 360, 56, MAROON, s.t("keratin") - 0.5, "c"), text("= a protective membrane", 1400, Y + 460, 62, GOLD_T, s.t("membrane") - 0.5, "c"),
          text("constantly shed and replaced", 1400, Y + 640, 54, BLUE_T, s.t("shed") - 0.6, "c"), text("a fresh barrier", 520, Y + 820, 70, RED_T, s.t("fresh") - 0.6, "c")]

    # ---------------- MELANIN (E)
    s = sc["melanin"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, pr)
    X = PW
    me = [pop(melanocyte_pic(), X + 450, Y + 540, w=780, t=s.start + 0.3), pop(sun_pic(70), X + 780, Y + 170, h=240, t=s.t("sunlight") - 0.8),
          text("MELANOCYTES", X + 1450, Y + 180, 76, RED_T, s.t("melanocytes") - 0.4, "c"), text("make MELANIN", X + 1450, Y + 320, 80, GOLD_T, s.t("melanin") - 0.4, "c"),
          text("the pigment of skin color", X + 1450, Y + 440, 54, MAROON, s.t("pigment") - 0.5, "c"), text("sunlight = more melanin", X + 1450, Y + 640, 56, BLUE_T, s.t("sunlight") - 0.4, "c"),
          text("absorbs UV: built-in sunscreen", X + 1450, Y + 760, 48, GREEN_T, s.t("sunscreen") - 1.4, "c")]

    # ---------------- DERMIS (F)
    s = sc["dermis"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, me)
    X = 2 * PW
    de = [pop(dermis_pic(), X + 520, Y + 480, w=900, t=s.start + 0.3), text("DERMIS", X + 1450, Y + 130, 80, MAROON, s.t("dermis") - 0.3, "c"), text("collagen + elastin: strength, stretch", X + 1450, Y + 260, 46, GOLD_T, s.t("collagen") - 0.6, "c"),
          text("blood vessels", X + 1450, Y + 420, 56, RED_T, s.t("vessels") - 0.8, "c"), text("nerve endings", X + 1450, Y + 520, 56, PURPLE, s.t("nerve") - 0.9, "c"),
          text("hair follicles", X + 1450, Y + 620, 56, BLUE_T, s.t("follicles") - 1.0, "c"), text("sweat + oil glands", X + 1450, Y + 720, 56, GREEN_T, s.t("glands") - 1.0, "c")]

    # ---------------- GLANDS (A)
    s = sc["glands"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, de)
    gl = [pop(gland_pic(), 460, 540, w=780, t=s.start + 0.3), text("SWEAT", 1380, 200, 90, BLUE_T, s.t("sweat") - 0.3, "c"), text("evaporates = cools you", 1380, 320, 58, MAROON, s.t("evaporates") - 0.6, "c"),
          text("SEBUM", 1380, 560, 90, GOLD_T, s.t("sebum") - 0.3, "c"), text("oily: waterproofs skin + hair", 1380, 680, 54, MAROON, s.t("waterproof") - 0.7, "c")]

    # ---------------- HYPODERMIS (B)
    s = sc["hypo"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, gl)
    X = PW
    hy = [pop(fat_pic(), X + 520, 520, w=860, t=s.start + 0.3), text("HYPODERMIS", X + 1450, 240, 80, GOLD_T, s.t("hypodermis") - 0.3, "c"), text("the deepest layer", X + 1450, 360, 56, MAROON, s.t("deepest") - 0.5, "c"),
          text("stores FAT", X + 1450, 580, 90, RED_T, s.t("fat") - 0.4, "c"), text("cushions + insulates", X + 1450, 720, 58, BLUE_T, s.t("insulates") - 0.6, "c")]

    # ---------------- VITAMIN D (C)
    s = sc["vitd"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, hy)
    X = 2 * PW
    vd = [pop(sun_pic(110), X + 420, 300, h=380, t=s.t("ultraviolet") - 0.5), pop(section_pic(), X + 420, 760, w=560, t=s.start + 0.3),
          text("VITAMIN D", X + 1400, 260, 100, GOLD_T, s.t("vitamin") - 0.3, "c"), text("UV light from the sun", X + 1400, 420, 56, BLUE_T, s.t("ultraviolet") - 0.5, "c"),
          text("a cholesterol-related molecule", X + 1400, 540, 50, MAROON, s.t("cholesterol") - 0.6, "c"), text("-> vitamin D3", X + 1400, 680, 80, GREEN_T, s.t("d3") - 0.6, "c")]

    # ---------------- RECAP (D)
    s = sc["recap"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, vd)
    rp = title("remember 3 things", 960, Y + 100, s.start + 0.4)
    for w, a, b, col, tc_, x in (("layers", "3 layers", "epidermis - dermis - hypodermis", PINK, RED_T, 400), ("outer", "outer layer = dead cells", "constantly replaced", CREAM, GOLD_T, 960), ("senses", "senses, cools,", "waterproofs, makes vitamin D", SKY, BLUE_T, 1520)):
        tw2 = s.t(w) - 0.3
        rp += [panel(x - 265, Y + 220, x + 265, Y + 600, col, tw2 - 0.2), text(a, x, Y + 360, 38, tc_, tw2, "c"), text(b, x, Y + 470, 32, MAROON, tw2 + 0.6, "c")]
    tn = s.t("musculoskeletal") - 0.8
    rp += [panel(200, Y + 720, 1720, Y + 890, LILAC, tn - 0.3), text("next: the musculoskeletal system", 960, Y + 820, 52, PURPLE, tn, "c")]

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
        a = [pop(dead_cells_pic(), 520, 520, w=860, t=0.3), text("the part you SEE", 1400, 240, 70, MAROON, s.t("see") - 0.4, "c"), text("= DEAD cells", 1400, 420, 100, RED_T, s.t("dead") - 0.4, "c")]
        s = sc["turn"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(dead_cells_pic(3), X + 520, 520, w=860, t=s.start + 0.3), text("yet it protects you", X + 1400, 260, 72, GOLD_T, s.t("protects") - 0.4, "c"), text("a SHIELD?", X + 1400, 480, 110, RED_T, s.t("shield") - 0.4, "c"),
             text("?", X + 1400, 800, 200, GOLD_T, s.t("shield") - 0.1, "c")]
    else:
        s = sc["case"]
        a = [pop(sun_pic(110), 520, 420, h=420, t=0.3), pop(melanocyte_pic(), 520, 820, w=560, t=0.5), text("a BUILT-IN SUNSCREEN", 1400, 280, 70, GOLD_T, s.t("sunscreen") - 0.5, "c"),
             text("made by your own cells", 1400, 480, 62, MAROON, s.t("cells") - 0.6, "c")]
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(sun_pic(110), X + 520, 540, h=500, t=s.start + 0.3), text("sunlight says:", X + 1400, 360, 72, BLUE_T, s.t("sunlight") - 0.4, "c"), text("make MORE!", X + 1400, 560, 110, RED_T, s.t("more") - 0.5, "c")]
        s = sc["clue"]
        cam(s.start, *C, 1.0, 1.0)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        c = [pop(melanocyte_pic(), X + 520, 540, w=700, t=s.start + 0.3), text("a PIGMENT", X + 1400, 360, 100, GOLD_T, s.t("pigment") - 0.4, "c"), text("what is it called?", X + 1400, 560, 70, PURPLE, s.t("pigment") - 0.2, "c"),
             text("?", X + 1400, 840, 200, GOLD_T, s.t("called") - 0.1, "c")]

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
    board = NU.render_board(bd, sc, f"skin_story{n}")
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
    ov = OUT / f"skin_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"skin_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["skin"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "skin", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"skin_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"sshort{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "skin", intro=True)
        f.replace(OUT / "final_skin.mp4")
        print("done ->", OUT / "final_skin.mp4")
