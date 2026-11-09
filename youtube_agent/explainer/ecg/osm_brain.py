"""Nervous system series: Brain Anatomy (owner-approved script, narration only)."""
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "brain")))
OUT = Path(os.environ.get("OUT_DIR", str(HERE)))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_preview as OP  # noqa: E402
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402


MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OF.MAROON, OF.PURPLE, OP.BLUE_T, OP.RED_T, OP.GOLD_T, OF.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OF.PINK, OF.LILAC, OF.CREAM, OF.MINT, OF.SKY
GRAY_T = (100, 95, 110)
PW, PH = 1920, 1080
SV = HERE.parent / "servier"


def sv(name):
    for sub in ("", "ha", "mi", "bpx", "bv", "lu"):
        p = SV / sub / f"{name}.png"
        if p.exists():
            return Image.open(p).convert("RGBA")
    raise FileNotFoundError(name)


OUTL = (70, 60, 70)

# ---- regions of the Servier brain picture (580 x 592, side view, FRONT of the brain = right) ----
REG = {
    "frontal": [(250, 0), (580, 0), (580, 320), (500, 345), (400, 338), (372, 300), (345, 268), (330, 255)],
    "parietal": [(125, 0), (255, 0), (330, 255), (250, 250), (125, 243)],
    "occipital": [(0, 0), (128, 0), (128, 246), (80, 252), (40, 275), (0, 310)],
    "temporal": [(40, 275), (80, 252), (125, 243), (250, 250), (330, 258), (372, 300), (372, 345), (330, 392), (250, 398), (150, 388), (60, 365), (0, 330), (0, 310)],
    "cerebrum": [(0, 0), (580, 0), (580, 345), (412, 345), (412, 372), (370, 392), (300, 400), (240, 398), (150, 388), (60, 368), (0, 335)],
    "brainstem": [(236, 402), (362, 398), (350, 440), (300, 540), (292, 592), (232, 592), (232, 480)],
}
COL = {"frontal": (244, 130, 130), "parietal": (245, 200, 70), "occipital": (110, 140, 240), "temporal": (90, 190, 130),
       "cerebrum": (244, 143, 143), "cerebellum": (165, 125, 225), "brainstem": (240, 190, 60)}


def brain_img():
    return sv("Cerveau_beau")


def overlay(name, alpha=125):
    base = brain_img()
    a = base.getchannel("A")
    mask = Image.new("L", base.size, 0)
    if name == "cerebellum":   # the pink striped parts, found by colour inside two boxes
        px = base.load()
        m = mask.load()
        for (x0, y0, x1, y1) in ((95, 372, 275, 485), (345, 330, 415, 410)):
            for y in range(y0, y1):
                for x in range(x0, x1):
                    r, g, b_, al = px[x, y]
                    if al > 200 and r - g > 52 and abs(g - b_) < 38:
                        m[x, y] = 255
    else:
        ImageDraw.Draw(mask).polygon(REG[name], fill=255)
    mask = ImageChops.multiply(mask, a)
    ov = Image.new("RGBA", base.size, COL[name] + (0,))
    ov.putalpha(mask.point(lambda v: v * alpha // 255))
    return ov


def wavy(cx, cy, rx, ry, amp, k, phase=0.0, n=360, S=1):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1 + amp * math.sin(k * a + phase) + amp * 0.5 * math.sin((2 * k + 1) * a)
        pts.append(((cx + rx * r * math.cos(a)) * S, (cy + ry * r * math.sin(a)) * S))
    return pts


def slice_pic():
    """a brain slice: grey matter (outer wavy layer) and white matter (inside)."""
    S, W, H = 3, 700, 560
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    outer = wavy(W / 2, H / 2, 318, 248, 0.034, 13, S=S)
    inner = wavy(W / 2, H / 2, 244, 180, 0.05, 11, 1.0, S=S)
    d.polygon(outer, fill=(196, 184, 198))
    d.polygon(inner, fill=(253, 251, 248))
    d.line(inner + [inner[0]], fill=(120, 105, 125), width=3 * S)
    d.line(outer + [outer[0]], fill=(100, 85, 105), width=5 * S)
    d.line([(W / 2 * S, 40 * S), (W / 2 * S, 150 * S)], fill=(100, 85, 105), width=5 * S)
    for k in range(-3, 4):   # white matter fibre lines
        d.arc(((W / 2 - 150 + k * 6) * S, (H / 2 - 70) * S, (W / 2 + 150 - k * 6) * S, (H / 2 + 120 + k * 8) * S), 20, 160, fill=(190, 200, 235), width=2 * S)
    return im.resize((W, H), Image.LANCZOS)


def hemi_pic():
    """top view: left half (blue) and right half (pink) joined by the corpus callosum bridge."""
    S, W, H = 3, 760, 520
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    for cx, col in ((200, (190, 215, 245)), (560, (245, 205, 212))):
        pts = wavy(cx, H / 2, 172, 235, 0.03, 15, S=S)
        d = ImageDraw.Draw(im)
        d.polygon(pts, fill=col + (255,))
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        for k in range(9):
            y0 = 60 + k * 45
            ld.line([((cx - 150 + x) * S, (y0 + 14 * math.sin((x + k * 40) / 22.0)) * S) for x in range(0, 301, 6)], fill=(120, 100, 115, 170), width=3 * S)
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).polygon(pts, fill=255)
        layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
        im.alpha_composite(layer)
        ImageDraw.Draw(im).line(pts + [pts[0]], fill=(100, 80, 95, 255), width=5 * S)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((250 * S, 240 * S, 510 * S, 282 * S), radius=20 * S, fill=(247, 196, 80, 240), outline=(170, 110, 0, 255), width=4 * S)
    return im.resize((W, H), Image.LANCZOS)


def deep_pic():
    """simplified middle cut through the brain with the four deep structures (front = right)."""
    S, W, H = 3, 640, 560
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    out = wavy(310, 250, 290, 215, 0.02, 12, S=S)
    d.polygon(out, fill=(250, 238, 226))
    d.line(out + [out[0]], fill=(120, 95, 90), width=5 * S)
    d.polygon([(330 * S, 440 * S), (420 * S, 430 * S), (400 * S, 556 * S), (350 * S, 556 * S)], fill=(246, 222, 184), outline=(120, 95, 90))   # brainstem
    d.ellipse((120 * S, 400 * S, 270 * S, 470 * S), fill=(240, 200, 205), outline=(120, 95, 90), width=3 * S)   # cerebellum
    d.arc((150 * S, 120 * S, 470 * S, 330 * S), 200, 340, fill=(200, 195, 205), width=14 * S)   # corpus callosum (faint)
    d.ellipse((250 * S, 200 * S, 390 * S, 290 * S), fill=(247, 205, 92), outline=(170, 110, 0), width=3 * S)   # thalamus
    d.ellipse((318 * S, 305 * S, 382 * S, 352 * S), fill=(245, 150, 172), outline=(186, 46, 70), width=3 * S)   # hypothalamus
    d.arc((170 * S, 240 * S, 380 * S, 420 * S), 90, 225, fill=(160, 120, 222), width=24 * S)   # hippocampus (C shape)
    d.ellipse((330 * S, 392 * S, 392 * S, 440 * S), fill=(240, 110, 110), outline=(186, 46, 70), width=3 * S)   # amygdala
    return im.resize((W, H), Image.LANCZOS)


LAY = dict(cx=350, cy=300, skull=(330, 285), dura=(290, 245), arach=(268, 224), pia=(236, 192), brain=(232, 188))


def layers_pic():
    S, W, H = 3, 700, 600
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = LAY["cx"], LAY["cy"]

    def ell(r, fill=None, outline=None, w=3):
        d.ellipse(((cx - r[0]) * S, (cy - r[1]) * S, (cx + r[0]) * S, (cy + r[1]) * S), fill=fill, outline=outline, width=w * S)
    ell(LAY["skull"], (240, 231, 212), (120, 100, 80), 6)
    ell((292, 248), (255, 255, 255), (150, 130, 110), 3)
    ell(LAY["dura"], None, (150, 90, 190), 5)
    ell(LAY["arach"], (200, 226, 250), (190, 150, 40), 4)
    ell(LAY["pia"], (200, 226, 250), (200, 70, 90), 3)
    br = wavy(cx, cy, LAY["brain"][0], LAY["brain"][1], 0.03, 14, S=S)
    d.polygon(br, fill=(240, 205, 160))
    d.line(br + [br[0]], fill=(150, 100, 80), width=3 * S)
    for k in range(7):
        d.arc(((cx - 170 + k * 12) * S, (cy - 120 + k * 22) * S, (cx + 170 - k * 12) * S, (cy + 60 + k * 18) * S), 200, 340, fill=(190, 140, 110), width=3 * S)
    d.line([(cx * S, (cy - 190) * S), (cx * S, (cy - 60) * S)], fill=(150, 100, 80), width=4 * S)
    return im.resize((W, H), Image.LANCZOS)


class Sc(HA.Sc):
    def __init__(self, sid, text, start):
        import render as R
        self.id, self.text, self.start = sid, text, start
        self.audio = EP / "audio" / f"{sid}.wav"
        self.dur = R.dur(self.audio)
        self.words = text.lower().replace(",", "").replace(".", "").replace("?", "").replace(":", "").split()


def build():
    data = json.load(open(EP / "script.json"))
    sc, t0 = {}, 0.0
    for s in data:
        sc[s["id"]] = Sc(s["id"], s["text"], t0)
        t0 += sc[s["id"]].dur
    bd = B.Board(3, 2)
    pops, glows = [], []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    cam = bd.camera
    A, Bc, C = (960, 540), (PW + 960, 540), (2 * PW + 960, 540)
    D, E, Fp = (960, PH + 540), (PW + 960, PH + 540), (2 * PW + 960, PH + 540)
    cam(0, *A, 1.0, 0.1)
    brain = brain_img()
    OV = {k: overlay(k) for k in ("frontal", "parietal", "occipital", "temporal", "cerebrum", "cerebellum", "brainstem")}
    WHITE, RED_P = (255, 255, 255), (244, 150, 150)

    def L(p0, p1, t, col=MAROON, w=4):
        mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - 18)
        return lead([p0, mid, p1], t, col, w, 0.5)

    def chip(name, p, col, tcol, t, w=250):
        return [panel(p[0] - w / 2, p[1] - 33, p[0] + w / 2, p[1] + 33, col, t), text(name, p[0], p[1] + 12, 36, tcol, t + 0.1, "c")]

    # ---------------- HOOK (A)
    s = sc["story"]
    br = pop(brain, 520, 560, h=800, t=0.3)
    rod = lead([br.map((560, 400)), br.map((470, 150)), br.map((420, -70))], s.t("iron"), (120, 80, 50), 26, 0.7)
    st = [rod, text("1848", 1400, 215, 180, GOLD_T, s.t("1848"), "c"), text("iron rod through his skull", 1400, 380, 66, RED_T, s.t("iron"), "c"),
          text("HE SURVIVED", 1400, 530, 100, GREEN_T, s.t("survived"), "c"), text("but was never the same", 1400, 650, 70, MAROON, s.t("never"), "c"),
          text("why? let's look inside the brain", 1400, 830, 62, BLUE_T, s.t("understand"), "c")]
    s = sc["hook"]
    bd.erase(s.start + 0.8, st)
    tt, tf = s.t("three"), s.t("fifth")
    hk = [br, panel(1000, 140, 1800, 400, PINK, tt - 0.3), text("about 3 pounds", 1400, 262, 72, RED_T, tt, "c"),
          text("(about 1.4 kg)", 1400, 345, 40, MAROON, tt + 0.6, "c"),
          panel(1000, 440, 1800, 890, CREAM, tf - 0.5), text("uses about", 1400, 510, 48, MAROON, tf - 0.4, "c"),
          text("20%", 1400, 650, 150, GOLD_T, tf - 0.2, "c"), text("of your body's energy", 1400, 785, 46, MAROON, tf + 0.4, "c")]
    for i in range(5):
        hk.append(panel(1150 + i * 100, 815, 1230 + i * 100, 860, RED_P if i == 0 else WHITE, tf + 0.5 + i * 0.1))
    hk.append(text("what is inside?", 1400, 985, 64, BLUE_T, s.t("what") - 0.3, "c"))
    # ---------------- OVERVIEW (B)
    s = sc["overview"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, hk)
    X = PW
    b2 = pop(brain, X + 520, 560, h=800, t=s.start + 0.3)
    t1, t2, t3 = s.t("cerebrum"), s.t("cerebellum"), s.t("brainstem")
    ov = [b2, pop(OV["cerebrum"], X + 520, 560, h=800, t=t1 - 0.2), pop(OV["cerebellum"], X + 520, 560, h=800, t=t2 - 0.2),
          pop(OV["brainstem"], X + 520, 560, h=800, t=t3 - 0.2)]
    ov += [text("cerebrum", X + 1030, 230, 76, RED_T, t1, "l"), L((X + 1020, 215), b2.map((430, 150)), t1 + 0.3, RED_T),
           text("the boss", X + 1030, 314, 46, MAROON, s.t("boss")),
           text("cerebellum", X + 70, 920, 62, PURPLE, t2, "l"), L((X + 220, 865), b2.map((190, 440)), t2 + 0.3, PURPLE),
           text("the coordinator", X + 70, 990, 40, MAROON, s.t("coordinator")),
           text("brainstem", X + 1030, 800, 76, GOLD_T, t3, "l"), L((X + 1020, 785), b2.map((290, 520)), t3 + 0.3, GOLD_T),
           text("the power cable", X + 1030, 884, 46, MAROON, s.t("power")),
           text("all safely inside your skull", X + 1030, 990, 46, BLUE_T, s.t("safely") - 0.4)]
    # ---------------- CEREBRUM (C)
    s = sc["cerebrum"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ov)
    X = 2 * PW
    b3 = pop(brain, X + 420, 560, h=720, t=s.start + 0.3)
    tc = s.t("cortex")
    ce = [b3, pop(OV["cerebrum"], X + 420, 560, h=720, t=s.start + 0.6),
          text("cerebrum = the biggest part", X + 420, 130, 52, RED_T, s.start + 0.4, "c"),
          text("cortex = wrinkled outer layer", X + 420, 1000, 42, PURPLE, tc - 0.2, "c")]
    glows.append((tc, b3.map((200, 90)), 2.0, 110))
    tfo = s.t("folds")
    sl = pop(slice_pic(), X + 1440, 470, w=700, t=tfo - 0.2)
    ce += [sl, text("folds = more surface", X + 1440, 100, 54, MAROON, tfo - 0.2, "c"), text("in a small skull", X + 1440, 160, 40, MAROON, tfo + 0.5, "c")]
    tg, tw = s.t("gray"), s.t("white")
    ce += [text("gray matter", X + 1000, 850, 56, GRAY_T, tg, "l"), text("= nerve cell bodies", X + 1000, 920, 38, MAROON, tg + 0.5, "l"),
           L((X + 1110, 810), sl.map((75, 300)), tg + 0.3, GRAY_T),
           text("white matter", X + 1500, 850, 56, BLUE_T, tw, "l"), text("= cables between them", X + 1500, 920, 38, MAROON, tw + 0.5, "l"),
           L((X + 1600, 810), sl.map((420, 330)), tw + 0.3, BLUE_T)]
    # ---------------- LOBES 1 + 2 (D)
    s = sc["lobes1"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, ce)
    Y = PH
    bl = pop(brain, 520, Y + 560, h=800, t=s.start + 0.3)
    lb = [bl, text("4 lobes on each side", 520, Y + 100, 56, MAROON, s.t("four") - 0.3, "c")]
    tf_, tp_ = s.t("frontal"), s.t("parietal")
    lb += [pop(OV["frontal"], 520, Y + 560, h=800, t=tf_ - 0.2)] + chip("frontal", bl.map((440, 160)), PINK, RED_T, tf_)
    lb += [panel(1000, Y + 150, 1840, Y + 355, PINK, tf_ - 0.2), text("frontal lobe", 1030, Y + 206, 58, RED_T, tf_),
           text("plans, decides, moves", 1030, Y + 277, 42, MAROON, s.t("plans")), text("the part Phineas Gage damaged", 1030, Y + 332, 34, PURPLE, s.t("phineas"))]
    lb += [pop(OV["parietal"], 520, Y + 560, h=800, t=tp_ - 0.2)] + chip("parietal", bl.map((225, 110)), CREAM, GOLD_T, tp_)
    lb += [panel(1000, Y + 375, 1840, Y + 565, CREAM, tp_ - 0.2), text("parietal lobe", 1030, Y + 445, 58, GOLD_T, tp_),
           text("touch + where your body is", 1030, Y + 515, 42, MAROON, s.t("touch"))]
    s2 = sc["lobes2"]
    tt_, to_ = s2.t("temporal"), s2.t("occipital")
    lb += [pop(OV["temporal"], 520, Y + 560, h=800, t=tt_ - 0.2)] + chip("temporal", bl.map((190, 335)), MINT, GREEN_T, tt_)
    lb += [panel(1000, Y + 590, 1840, Y + 780, MINT, tt_ - 0.2), text("temporal lobe", 1030, Y + 665, 58, GREEN_T, tt_),
           text("hearing, language, memory", 1030, Y + 735, 42, MAROON, s2.t("hearing"))]
    lb += [pop(OV["occipital"], 520, Y + 560, h=800, t=to_ - 0.2)] + chip("occipital", bl.map((62, 140)), SKY, BLUE_T, to_)
    lb += [panel(1000, Y + 810, 1840, Y + 1000, SKY, to_ - 0.2), text("occipital lobe", 1030, Y + 885, 58, BLUE_T, to_),
           text("vision", 1030, Y + 955, 42, MAROON, s2.t("vision"))]
    te = s2.t("exam")
    lb += [text("exam tip: temporal = temple, occipital = back", 1420, Y + 1048, 36, PURPLE, te, "c")]

    # ---------------- HEMISPHERES (E)
    s = sc["hemispheres"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, lb)
    X = PW
    th = s.t("thick")
    hp = pop(hemi_pic(), X + 960, Y + 330, w=700, t=s.start + 0.3)
    he = [hp, text("top view (front at the top)", X + 960, Y + 55, 40, MAROON, s.start + 0.4, "c"),
          text("LEFT", X + 560, Y + 130, 50, BLUE_T, s.t("left"), "c"), text("RIGHT", X + 1360, Y + 130, 50, RED_T, s.t("right"), "c"),
          text("corpus callosum", X + 1330, Y + 300, 46, GOLD_T, s.t("corpus"), "l"), text("bridge of nerve fibers", X + 1330, Y + 364, 36, MAROON, th, "l"),
          text("(deep inside)", X + 1330, Y + 410, 34, MAROON, th + 0.5, "l"), L((X + 1320, Y + 322), hp.map((505, 261)), s.t("corpus") + 0.3, GOLD_T)]
    tcr = s.t("opposite")
    he += [panel(X + 300, Y + 790, X + 880, Y + 900, CREAM, tcr - 0.3), text("LEFT side of body", X + 590, Y + 858, 46, BLUE_T, tcr, "c"),
           panel(X + 1040, Y + 790, X + 1620, Y + 900, CREAM, tcr - 0.3), text("RIGHT side of body", X + 1330, Y + 858, 46, RED_T, tcr, "c")]
    tl = s.t("so")
    he += [lead([(X + 760, Y + 580), (X + 1330, Y + 780)], tcr + 0.3, BLUE_T, 7, 0.7, arrow=True),
           lead([(X + 1160, Y + 580), (X + 590, Y + 780)], tcr + 0.6, RED_T, 7, 0.7, arrow=True),
           panel(X + 500, Y + 930, X + 1420, Y + 1035, PINK, tl - 0.3), text("left brain moves your right hand", X + 960, Y + 997, 50, PURPLE, tl, "c")]
    # ---------------- CEREBELLUM (F)
    s = sc["cerebellum"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, he)
    X = 2 * PW
    b7 = pop(brain, X + 520, Y + 540, h=760, t=s.start + 0.3)
    tcb = s.t("cerebellum")
    ca = [b7, pop(OV["cerebellum"], X + 520, Y + 540, h=760, t=tcb - 0.2)]
    glows.append((tcb, b7.map((180, 430)), 2.2, 110))
    ca += [text("cerebellum", X + 80, Y + 915, 62, PURPLE, tcb, "l"), L((X + 220, Y + 860), b7.map((190, 440)), tcb + 0.3, PURPLE),
           text("= the little brain", X + 80, Y + 985, 40, MAROON, s.t("little"))]
    tn = s.t("not")
    ca += [panel(X + 1030, Y + 150, X + 1840, Y + 290, PINK, tn - 0.3), text("does NOT start movements", X + 1435, Y + 235, 46, RED_T, tn, "c")]
    tfi = s.t("fine")
    ca += [panel(X + 1030, Y + 340, X + 1840, Y + 610, LILAC, tfi - 0.3), text("fine-tunes them:", X + 1060, Y + 420, 46, PURPLE, tfi),
           text("- keeps your balance", X + 1060, Y + 490, 44, MAROON, s.t("balance")), text("- makes actions smooth", X + 1060, Y + 560, 44, MAROON, s.t("smooth"))]
    tm = s.t("more")
    ca += [panel(X + 1030, Y + 660, X + 1840, Y + 900, CREAM, tm - 0.3), text("MORE THAN HALF", X + 1435, Y + 765, 62, GOLD_T, tm, "c"),
           text("of all your nerve cells", X + 1435, Y + 840, 44, MAROON, tm + 0.5, "c")]
    # ---------------- BRAINSTEM (A)
    s = sc["brainstem"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, ca)
    b8 = pop(brain, 520, 540, h=760, t=s.start + 0.3)
    tbs = s.t("brainstem")
    bs = [b8, pop(OV["brainstem"], 520, 540, h=760, t=tbs - 0.2)]
    glows.append((tbs, b8.map((290, 500)), 2.2, 110))
    tsp = s.t("spinal")
    bs += [text("to the spinal cord", 520, 985, 44, GOLD_T, tsp - 0.2, "c"), lead([(520, 950), b8.map((268, 585))], tsp, GOLD_T, 5, 0.5, arrow=True)]
    parts = [("midbrain", (305, 425), 690), ("pons", (290, 478), 790), ("medulla", (275, 545), 890)]
    for nm, pt, yy in parts:
        tn_ = s.t(nm)
        bs += [panel(760, yy, 1140, yy + 75, CREAM, tn_ - 0.2), text(nm, 950, yy + 56, 50, GOLD_T, tn_, "c"), L((755, yy + 37), b8.map(pt), tn_ + 0.2, GOLD_T)]
    tj = s.t("jobs")
    bs += [text("runs jobs you never think about", 1400, 130, 46, PURPLE, tj - 0.4, "c")]
    cards = [("breathing", sv("poumons_01"), 940), ("heart rate", sv("coeur_09"), 1240), ("swallowing", None, 1540)]
    for i, (nm, pic, x0) in enumerate(cards):
        tn_ = s.t(nm.split()[0]) - (0.9 if nm == "swallowing" else 0.2)
        bs += [panel(x0, 200, x0 + 280, 640, [SKY, PINK, MINT][i], tn_ - 0.2), text(nm, x0 + 140, 600, 32, [BLUE_T, RED_T, GREEN_T][i], tn_ + 0.1, "c")]
        if pic is not None:
            bs.append(pop(pic, x0 + 140, 400, h=240, t=tn_))
        else:
            bs.append(text("gulp", x0 + 140, 430, 66, GREEN_T, tn_, "c"))
    # ---------------- DEEP STRUCTURES (B)
    s = sc["deep"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, bs)
    X = PW
    dp = pop(deep_pic(), X + 520, 560, h=820, t=s.start + 0.3)
    de = [dp, text("simplified middle cut", X + 520, 90, 40, MAROON, s.start + 0.5, "c")]
    items = [("thalamus", "relays incoming senses", (320, 245), PINK, RED_T, 230), ("hypothalamus", "temperature, hunger, thirst", (350, 328), CREAM, GOLD_T, 420),
             ("hippocampus", "forms new memories", (223, 404), LILAC, PURPLE, 610), ("amygdala", "fear + strong emotions", (361, 416), MINT, GREEN_T, 800)]
    for nm, fn, pt, col, tcol, yy in items:
        tn_ = s.t(nm)
        de += [panel(X + 1030, yy - 60, X + 1860, yy + (125 if nm == "hippocampus" else 95), col, tn_ - 0.3), text(nm, X + 1060, yy + (-5 if nm == "hippocampus" else 5), 56, tcol, tn_), text(fn, X + 1060, yy + (55 if nm == "hippocampus" else 68), 40, MAROON, tn_ + 0.6),
               L((X + 1025, yy + 20), dp.map(pt), tn_ + 0.2, tcol)]
        if nm == "hippocampus":
            de.append(text("lose it = no new memories", X + 1060, yy + 118, 28, PURPLE, s.t("lose"), "l"))
    # ---------------- PROTECTION + SUMMARY (C, then F)
    s = sc["protect"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, de)
    X = 2 * PW
    lp = pop(layers_pic(), X + 520, 540, h=850, t=s.start + 0.3)
    cx, cy = X + 520 - 350 * 850 / 600 + LAY["cx"] * 850 / 600, 540 - 300 * 850 / 600 + LAY["cy"] * 850 / 600
    k = 850 / 600

    def pt(r, ang):
        a = math.radians(ang)
        return (cx + r[0] * k * math.cos(a), cy + r[1] * k * math.sin(a))
    ts_, tm_, tcs = s.t("skull"), s.t("meninges"), s.t("cerebrospinal")
    pr = [lp, text("skull", X + 1140, 150, 66, GOLD_T, ts_, "l"), text("bone", X + 1340, 150, 42, MAROON, ts_ + 0.4, "l"),
          L((X + 1130, 135), pt((310, 266), -52), ts_ + 0.3, GOLD_T),
          text("meninges (3 layers)", X + 1140, 330, 62, PURPLE, tm_, "l"),
          text("dura", X + 1180, 405, 40, PURPLE, tm_ + 0.4, "l"), L((X + 1170, 395), pt(LAY["dura"], -22), tm_ + 0.5, PURPLE, 3),
          text("arachnoid", X + 1180, 460, 40, (150, 110, 20), tm_ + 0.9, "l"), L((X + 1170, 450), pt(LAY["arach"], -8), tm_ + 1.0, (150, 110, 20), 3),
          text("pia", X + 1180, 515, 40, RED_T, tm_ + 1.4, "l"), L((X + 1170, 505), pt(LAY["pia"], 8), tm_ + 1.5, RED_T, 3),
          text("cerebrospinal fluid", X + 1140, 700, 60, BLUE_T, tcs, "l"), text("a clear liquid cushion", X + 1140, 765, 42, MAROON, tcs + 0.8, "l"),
          L((X + 1130, 685), pt(((LAY["arach"][0] + LAY["pia"][0]) / 2, (LAY["arach"][1] + LAY["pia"][1]) / 2), 38), tcs + 0.3, BLUE_T),
          text("like a water bag", X + 1140, 830, 46, BLUE_T, s.t("water"))]
    trm = s.t("remember")
    cam(trm - 0.4, *Fp, 1.0, 1.0)
    X = 2 * PW
    sm = title("remember 3 things", X + 960, Y + 100, trm)
    cards = [("parts", "3 parts", ["cerebrum,", "cerebellum,", "brainstem"], PINK, RED_T, 400), ("lobes", "4 lobes", ["frontal, parietal,", "temporal, occipital"], CREAM, GOLD_T, 960),
             ("layers", "layers of", ["protection"], MINT, GREEN_T, 1520)]
    for w, a, lines, col, tc_, x in cards:
        tw_ = s.t(w, 2 if w == "layers" else 1)
        sm += [panel(X + x - 265, Y + 220, X + x + 265, Y + 600, col, tw_ - 0.3), text(a, X + x, Y + 345, 66, tc_, tw_ - 0.1, "c")]
        for j, ln in enumerate(lines):
            sm.append(text(ln, X + x, Y + 430 + j * 55, 42, MAROON, tw_ + 0.5 + j * 0.3, "c"))
    tx = s.t("next")
    sm += [panel(X + 360, Y + 720, X + 1560, Y + 890, LILAC, tx - 0.3), text("next: how brain cells talk", X + 960, Y + 820, 56, PURPLE, tx, "c")]
    del pr, sm

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render(out="brain.mp4"):
    import subprocess
    import render_ecg as RE
    bd, sc = build()
    vid = OUT / "brain_video_only.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080",
                           "-r", "30", "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", str(vid)], stdin=subprocess.PIPE)
    for f in range(int(round(RE.INTRO_DUR * 30))):
        ff.stdin.write(RE.intro_frame(f / 30).tobytes())
    for f in range(int(bd.total * 30)):
        ff.stdin.write(OF.credit(bd.frame(f / 30)).tobytes())
    ff.stdin.close()
    ff.wait()
    RE.intro_audio(OUT / "chime_intro.wav")
    lst = OUT / f"{out}.txt"
    with open(lst, "w") as fh:
        fh.write(f"file '{OUT / 'chime_intro.wav'}'\n")
        for s in sc.values():
            fh.write(f"file '{s.audio}'\n")
    wav = OUT / f"{out}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "pcm_s16le", str(wav)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(wav), "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", str(OUT / ("final_" + out))], check=True)
    print("done ->", OUT / ("final_" + out))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        bd, sc = build()
        ends = [round(v.start + v.dur - 0.3, 1) for v in sc.values()]
        for t in ends:
            OF.credit(bd.frame(t)).save(OUT / f"brain_{t:06.1f}.png")
        print("ok", round(bd.total, 1), ends)
    else:
        render()
