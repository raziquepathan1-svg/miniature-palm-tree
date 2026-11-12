"""Endocrine system video (owner-approved 12 Nov 2026) + 2 story Shorts.

    python3 osm_endo.py [stills] | short 1|2 [stills]
Env: EP_DIR (default ../endocrine), OUT_DIR.
"""
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "endocrine")))
OUT = Path(os.environ.get("OUT_DIR", str(HERE)))
os.environ.setdefault("EP_DIR", str(EP))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_preview as OP  # noqa: E402
import osm_brain as OB  # noqa: E402
import osm_neuron as NU  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OB.PINK, OB.LILAC, OB.CREAM, OB.MINT, OB.SKY
PW, PH = 1920, 1080
sv = OB.sv
SHORT_TITLES = {1: "The Boss of the Pea", 2: "Why Are My Hands Still Shaking"}
SHORT_Q = {1: "So who is the real boss?", 2: "So what is still in your blood?"}
S = 3
GL = {"hypo": (170, 120, 220), "pit": (240, 150, 60), "thy": (240, 130, 160), "adr": (240, 200, 70), "pan": (120, 190, 120), "gon": (130, 170, 235)}


def dot_pic(col, r=40):
    W = r * 2 + 12
    im = Image.new("RGBA", (W * S, W * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((6 * S, 6 * S, (W - 6) * S, (W - 6) * S), fill=col + (255,), outline=(70, 50, 70, 255), width=4 * S)
    return im.resize((W, W), Image.LANCZOS)


def butterfly_pic():
    W, H = 520, 360
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col, ol = GL["thy"] + (255,), (170, 70, 100, 255)
    d.ellipse((30 * S, 40 * S, 250 * S, 300 * S), fill=col, outline=ol, width=6 * S)
    d.ellipse((270 * S, 40 * S, 490 * S, 300 * S), fill=col, outline=ol, width=6 * S)
    d.rectangle((225 * S, 180 * S, 295 * S, 260 * S), fill=col)
    return im.resize((W, H), Image.LANCZOS)


def cap_pic():
    W, H = 300, 200
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(30 * S, 170 * S), (150 * S, 20 * S), (270 * S, 170 * S)], fill=GL["adr"] + (255,), outline=(180, 140, 30, 255))
    d.line([(30 * S, 170 * S), (150 * S, 20 * S), (270 * S, 170 * S), (30 * S, 170 * S)], fill=(180, 140, 30, 255), width=6 * S, joint="curve")
    return im.resize((W, H), Image.LANCZOS)


def pancreas_pic():
    W, H = 760, 300
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col, ol = GL["pan"] + (255,), (60, 120, 70, 255)
    d.ellipse((20 * S, 60 * S, 260 * S, 260 * S), fill=col, outline=ol, width=6 * S)
    d.rounded_rectangle((200 * S, 110 * S, 730 * S, 210 * S), radius=50 * S, fill=col, outline=ol, width=6 * S)
    return im.resize((W, H), Image.LANCZOS)


def bolt_pic():
    W, H = 260, 360
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(170, 10), (60, 190), (130, 190), (80, 350), (210, 140), (140, 140)]
    d.polygon([(x * S, y * S) for x, y in pts], fill=(250, 215, 70, 255), outline=(190, 150, 20, 255))
    return im.resize((W, H), Image.LANCZOS)


def blood_pic():
    W, H = 1100, 240
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10 * S, 40 * S, 1090 * S, 200 * S), radius=80 * S, fill=(245, 175, 175, 255), outline=(180, 70, 80, 255), width=6 * S)
    for i, x in enumerate(range(90, 1050, 120)):
        y = 120 + (-30 if i % 2 else 30)
        d.ellipse((x * S, (y - 24) * S, (x + 48) * S, (y + 24) * S), fill=(150, 90, 220, 255), outline=(90, 50, 150, 255), width=4 * S)
    return im.resize((W, H), Image.LANCZOS)


def car_pic():
    W, H = 760, 380
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((30 * S, 150 * S, 730 * S, 290 * S), radius=50 * S, fill=(240, 120, 110, 255), outline=(150, 50, 50, 255), width=6 * S)
    d.polygon([(180 * S, 150 * S), (260 * S, 50 * S), (500 * S, 50 * S), (600 * S, 150 * S)], fill=(250, 150, 140, 255), outline=(150, 50, 50, 255))
    d.line([(180 * S, 150 * S), (260 * S, 50 * S), (500 * S, 50 * S), (600 * S, 150 * S)], fill=(150, 50, 50, 255), width=6 * S)
    for x in (190, 560):
        d.ellipse(((x - 60) * S, 240 * S, (x + 60) * S, 360 * S), fill=(60, 60, 70, 255), outline=(30, 30, 40, 255), width=4 * S)
        d.ellipse(((x - 22) * S, 278 * S, (x + 22) * S, 322 * S), fill=(200, 200, 210, 255))
    return im.resize((W, H), Image.LANCZOS)


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
    brain = OB.brain_img()
    Y = PH

    # ---------------- STORY (A)
    s = sc["story"]
    br = pop(brain, 520, 520, h=620, t=0.3)
    pea = pop(dot_pic(GL["pit"], 26), br.map((300, 430))[0], br.map((300, 430))[1], h=64, t=s.t("pea") - 0.4)
    st = [br, pea, text("a gland the size of a PEA", 1400, 190, 70, GOLD_T, s.t("pea") - 0.3, "c"), text("orders to almost every gland", 1400, 400, 60, MAROON, s.t("orders") - 0.3, "c"),
          text("growth  •  stress  •  energy", 1400, 560, 60, BLUE_T, s.t("grow") - 0.5, "c"), text("who orders the pea?", 1400, 820, 84, RED_T, s.t("who") - 0.3, "c")]

    # ---------------- OVERVIEW (B)
    s = sc["overview"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, st)
    X = PW
    ov = title("THE ENDOCRINE SYSTEM", X + 960, 130, s.start + 0.3) + [
        pop(dot_pic(GL["pit"], 60), X + 300, 520, h=240, t=s.t("glands") - 0.5), text("GLAND", X + 300, 700, 62, GOLD_T, s.t("glands") - 0.3, "c"),
        pop(blood_pic(), X + 1050, 520, w=900, t=s.t("blood") - 1.2), text("hormones travel in the BLOOD", X + 1050, 700, 60, RED_T, s.t("blood") - 1.0, "c"),
        text("chemical messengers = hormones", X + 960, 900, 64, PURPLE, s.t("hormones") - 0.2, "c")]

    # ---------------- SPEED (C)
    s = sc["speed"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ov)
    X = 2 * PW
    sp = [pop(bolt_pic(), X + 480, 440, h=420, t=s.start + 0.3), text("NERVES", X + 480, 740, 80, GOLD_T, s.t("nerves") - 0.2, "c"), text("fast - a flash", X + 480, 840, 56, MAROON, s.t("flash") - 0.8, "c"),
          pop(sv("Horloge"), X + 1440, 440, h=380, t=s.start + 0.5), text("HORMONES", X + 1440, 740, 80, PURPLE, s.t("hormones") - 0.2, "c"), text("slower, but last longer", X + 1440, 840, 56, MAROON, s.t("longer") - 0.9, "c")]

    # ---------------- MAP (D)
    s = sc["map"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, sp)
    sil = pop(sv("Male-silhouette"), 540, Y + 540, h=1000, t=s.start + 0.3)
    ks = 1000 / 1207
    def at(px, py):
        return sil.map((px, py))
    items = [sil]
    spec = [("hypo", "hypothalamus + pituitary", (340, 80), s.t("hypothalamus") - 0.3, GL["hypo"], 220), ("thy", "thyroid", (340, 195), s.t("thyroid") - 0.6, GL["thy"], 400),
            ("adr", "adrenal glands", (385, 410), s.t("adrenal") - 0.6, GL["adr"], 560), ("pan", "pancreas", (330, 460), s.t("pancreas") - 0.6, GL["pan"], 700),
            ("gon", "ovaries + testes", (340, 640), s.t("ovaries") - 0.7, GL["gon"], 860)]
    for key, lab, (px, py), tt, col, ty in spec:
        cx, cy = at(px, py)
        items.append(pop(dot_pic(col, 18), cx, cy, h=44, t=tt))
        items.append(text(lab, 1350, Y + ty - 200 + 80, 56, tuple(max(0, c - 70) for c in col), tt, "c"))
        items.append(lead([(1000, Y + ty - 120 + 80), (cx + 40, cy)], tt + 0.2, tuple(max(0, c - 40) for c in col), 4, 0.5))
    mp = items

    # ---------------- PITUITARY (E)
    s = sc["pituitary"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, mp)
    X = PW
    pb = pop(brain, X + 520, Y + 520, h=700, t=s.start + 0.3)
    px_, py_ = pb.map((300, 440))
    pi = [pb, pop(dot_pic(GL["pit"], 30), px_, py_, h=70, t=s.t("pituitary") - 0.3), lead([(X + 1000, Y + 300), (px_ + 30, py_ - 20)], s.t("pituitary") + 0.3, GOLD_T, 6, 0.6),
          text("PITUITARY", X + 1350, Y + 260, 90, GOLD_T, s.t("pituitary") - 0.2, "c"), text("the 'master gland'", X + 1350, Y + 380, 60, MAROON, s.t("master") - 0.4, "c"),
          text("tells other glands what to do", X + 1350, Y + 560, 56, BLUE_T, s.t("tells") - 0.4, "c"), text("controls growth", X + 1350, Y + 700, 62, GREEN_T, s.t("growth") - 0.5, "c")]

    # ---------------- THYROID (F)
    s = sc["thyroid"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, pi)
    X = 2 * PW
    th = [pop(butterfly_pic(), X + 560, Y + 520, w=780, t=s.start + 0.3), text("THYROID", X + 1450, Y + 280, 100, RED_T, s.t("thyroid") - 0.2, "c"),
          text("a butterfly in the neck", X + 1450, Y + 420, 56, MAROON, s.t("butterfly") - 0.4, "c"), text("sets your METABOLISM", X + 1450, Y + 620, 62, GOLD_T, s.t("metabolism") - 0.8, "c"),
          text("how fast cells use energy", X + 1450, Y + 730, 52, BLUE_T, s.t("energy") - 1.4, "c")]

    # ---------------- ADRENAL (A)
    s = sc["adrenal"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, th)
    kd = pop(sv("rein_01"), 520, 640, h=520, t=s.start + 0.3)
    cp = pop(cap_pic(), 560, 395, w=300, t=s.start + 0.5)
    ad = [kd, cp, text("adrenal gland", 1400, 160, 76, GOLD_T, s.t("adrenal") - 0.2, "c"), text("on top of a kidney", 1400, 255, 50, MAROON, s.t("kidney") - 0.4, "c"),
          text("CORTISOL", 1400, 450, 80, BLUE_T, s.t("cortisol") - 0.3, "c"), text("handles stress", 1400, 540, 50, MAROON, s.t("stress") - 0.4, "c"),
          text("ADRENALINE", 1400, 740, 80, RED_T, s.t("adrenaline") - 0.3, "c"), text("a burst of energy", 1400, 830, 50, MAROON, s.t("burst") - 0.4, "c")]

    # ---------------- PANCREAS (B)
    s = sc["pancreas"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, ad)
    X = PW
    pn = [pop(pancreas_pic(), X + 560, 330, w=780, t=s.start + 0.3), text("PANCREAS", X + 560, 520, 80, GREEN_T, s.t("pancreas") - 0.2, "c"), text("controls blood sugar", X + 560, 620, 54, MAROON, s.t("blood") - 0.4, "c"),
          panel(X + 1080, 160, X + 1800, 480, MINT, s.t("insulin") - 0.6), text("INSULIN", X + 1440, 270, 80, BLUE_T, s.t("insulin") - 0.4, "c"), text("sugar goes IN to cells", X + 1440, 390, 50, MAROON, s.t("take") - 0.8, "c"),
          panel(X + 1080, 560, X + 1800, 880, CREAM, s.t("glucagon") - 0.6), text("GLUCAGON", X + 1440, 670, 80, RED_T, s.t("glucagon") - 0.4, "c"), text("raises sugar when low", X + 1440, 790, 50, MAROON, s.t("raises") - 0.8, "c")]

    # ---------------- FEEDBACK (C)
    s = sc["feedback"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, pn)
    X = 2 * PW
    fb = title("a thermostat", X + 960, 120, s.t("thermostat") - 0.4) + [
        panel(X + 150, 300, X + 650, 560, SKY, s.start + 0.5), text("GLAND", X + 400, 430, 76, BLUE_T, s.start + 0.6, "c"),
        panel(X + 1270, 300, X + 1770, 560, PINK, s.start + 0.8), text("HORMONE", X + 1520, 430, 76, RED_T, s.t("hormone") - 0.3, "c"),
        lead([(X + 660, 400), (X + 960, 380), (X + 1260, 400)], s.t("hormone") + 0.2, GOLD_T, 10, 0.9, arrow=True),
        lead([(X + 1520, 580), (X + 960, 760), (X + 400, 580)], s.t("turns") - 0.4, PURPLE, 10, 1.0, arrow=True),
        text("HIGH enough = turn DOWN", X + 960, 840, 60, RED_T, s.t("high") - 0.4, "c"), text("LOW = turn UP", X + 960, 930, 60, GREEN_T, s.t("low") - 0.3, "c")]

    # ---------------- PAYOFF (D)
    s = sc["payoff"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, fb)
    pb2 = pop(brain, 420, Y + 520, h=620, t=s.start + 0.3)
    hx, hy = pb2.map((300, 400))
    py2 = pop(dot_pic(GL["pit"], 20), hx, hy + 70, h=50, t=s.start + 0.5)
    hp = pop(dot_pic(GL["hypo"], 24), hx, hy - 50, h=56, t=s.t("hypothalamus") - 0.4)
    pf = [pb2, py2, hp, lead([(hx, hy - 20), (hx, hy + 40)], s.t("orders") - 0.2, PURPLE, 8, 0.4, arrow=True),
          text("HYPOTHALAMUS = the real boss", 1360, Y + 170, 64, PURPLE, s.t("hypothalamus") - 0.3, "c"), text("links NERVES to HORMONES", 1360, Y + 300, 58, BLUE_T, s.t("links") - 0.5, "c"),
          text("hands shaking after a scare?", 1360, Y + 560, 62, MAROON, s.t("shake") - 0.6, "c"), text("ADRENALINE stays in the blood", 1360, Y + 680, 62, RED_T, s.t("adrenaline") - 0.9, "c")]

    # ---------------- RECAP (E)
    s = sc["recap"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, pf)
    X = PW
    rp = title("remember 3 things", X + 960, Y + 100, s.start + 0.4)
    for w, a, b, col, tc_, x in (("glands", "glands release", "hormones in the blood", PINK, RED_T, 400), ("slower", "slower than nerves", "but they last longer", CREAM, GOLD_T, 960), ("feedback", "feedback loops", "keep them in balance", SKY, BLUE_T, 1520)):
        tw2 = s.t(w) - 0.3
        rp += [panel(X + x - 265, Y + 220, X + x + 265, Y + 600, col, tw2 - 0.2), text(a, X + x, Y + 360, 46, tc_, tw2, "c"), text(b, X + x, Y + 470, 44, MAROON, tw2 + 0.6, "c")]
    tn = s.t("digestive") - 0.8
    rp += [panel(X + 200, Y + 720, X + 1720, Y + 890, LILAC, tn - 0.3), text("next: the digestive system", X + 960, Y + 820, 56, PURPLE, tn, "c")]

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
        br = pop(brain, 520, 540, h=700, t=0.3)
        hx, hy = br.map((300, 440))
        a = [br, pop(dot_pic(GL["pit"], 26), hx, hy, h=70, t=s.t("pea") - 0.4), text("size of a PEA", 1400, 190, 84, GOLD_T, s.t("pea") - 0.3, "c"),
             text("tells the thyroid", 1400, 420, 60, MAROON, s.t("thyroid") - 0.4, "c"), text("and adrenal glands", 1400, 520, 60, MAROON, s.t("adrenal") - 0.6, "c"),
             text("controls growth", 1400, 700, 66, GREEN_T, s.t("grow") - 0.5, "c")]
        s = sc["turn"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(brain, X + 520, 640, h=520, t=s.start + 0.3), text("THE BOSS?", X + 1400, 200, 110, RED_T, s.t("boss") - 0.3, "c"), text("not quite", X + 1400, 380, 80, MAROON, s.t("quite") - 0.4, "c"),
             text("something ABOVE gives the orders", X + 1400, 580, 62, PURPLE, s.t("above") - 0.5, "c"), text("?", X + 1400, 860, 240, GOLD_T, s.t("what") - 0.4, "c")]
    else:
        s = sc["case"]
        a = [pop(car_pic(), 540, 420, w=760, t=0.3), text("CAR!", 540, 740, 120, RED_T, s.t("car") - 0.2, "c"), text("you jump back", 1400, 300, 80, BLUE_T, s.t("jump") - 0.4, "c"),
             text("SAFE", 1400, 500, 120, GREEN_T, s.t("safe") - 0.3, "c"), text("minutes later...", 1400, 720, 70, MAROON, s.t("minutes") - 0.4, "c"), text("hands still SHAKING", 1400, 850, 64, PURPLE, s.t("shaking") - 0.4, "c")]
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [text("danger is gone", X + 960, 220, 100, GREEN_T, s.t("danger") - 0.3, "c"), pop(bolt_pic(), X + 600, 640, h=420, t=s.t("nerves") - 0.5), text("nerves: done in a flash", X + 1300, 640, 62, GOLD_T, s.t("flash") - 0.8, "c")]
        s = sc["clue"]
        cam(s.start, *C, 1.0, 1.0)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        c = [pop(blood_pic(), X + 960, 400, w=1300, t=s.t("blood") - 1.0), text("a chemical in the BLOOD", X + 960, 700, 76, RED_T, s.t("chemical") - 0.3, "c"), text("?", X + 960, 900, 200, GOLD_T, s.t("shaking") - 0.3, "c")]

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
    board = NU.render_board(bd, sc, f"endo_story{n}")
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
    ov = OUT / f"endo_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"endo_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["endocrine"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "endocrine", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"endo_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"eshort{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "endo", intro=True)
        f.replace(OUT / "final_endo.mp4")
        print("done ->", OUT / "final_endo.mp4")
