"""SMELL & TASTE - cinematic build (fact-checked script ../smelltaste, Servier CC BY art + owner's whiteboard human).

    python3 osm_smelltaste.py [stills] | short 1|2 [stills]
Env: EP_DIR (default ../smelltaste), OUT_DIR.
"""
import math
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "smelltaste")))
OUT = Path(os.environ.get("OUT_DIR", str(HERE)))
SERV = HERE.parent / "servier"
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_brain as OB  # noqa: E402
import osm_neuron as NU  # noqa: E402
import osm_digest as DG  # noqa: E402
import osm_sample as SM  # noqa: E402
from osm_ear2 import Cine  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
PINK, LILAC, CREAM, MINT = OB.PINK, OB.LILAC, OB.CREAM, OB.MINT
PW, PH = 1920, 1080
S = 3
new, done = DG.new, DG.done
OLN = (110, 80, 90, 255)
SMELL, SIG, TASTE = (150, 205, 90), (255, 215, 70), (240, 120, 150)
TASTES = (("SWEET", (240, 130, 170)), ("SALTY", (110, 170, 230)), ("SOUR", (240, 200, 60)), ("BITTER", (130, 170, 90)), ("UMAMI", (200, 120, 70)))
SHORT_TITLES = {1: "Is The Tongue Map Real", 2: "Why Food Tastes Bland"}
SHORT_Q = {1: "So how many basic tastes are there?", 2: "So what is missing when food tastes bland?"}


def sv(name):
    return Image.open(SERV / name).convert("RGBA")


def section_pic(aroma=False):
    return SM.section_pic(aroma)


def bud_pic():
    """one taste bud: an onion of receptor cells with a taste pore on top, nerve fibres below."""
    W, H = 900, 640
    im, d = new(W, H)
    d.rectangle((0, 120 * S, W * S, H * S), fill=(245, 200, 205, 255), outline=OLN, width=4 * S)          # tongue tissue
    d.rectangle((0, 120 * S, W * S, 160 * S), fill=(235, 160, 175, 255))
    cx, top, bot = 450, 150, 540
    d.ellipse(((cx - 210) * S, (top - 10) * S, (cx + 210) * S, (bot + 20) * S), fill=(255, 235, 225, 255), outline=OLN, width=5 * S)
    cols = [c for _, c in TASTES] * 2
    for i in range(9):
        f = (i - 4) / 4.0
        x0 = cx + f * 150
        d.polygon([(cx * S, (top + 20) * S), ((x0 - 22) * S, (bot - 10) * S), ((x0 + 22) * S, (bot - 10) * S)], fill=cols[i] + (255,), outline=OLN)
        d.ellipse(((x0 - 14) * S, (bot - 90) * S, (x0 + 14) * S, (bot - 60) * S), fill=(120, 70, 110, 255))
    d.ellipse(((cx - 26) * S, (top - 4) * S, (cx + 26) * S, (top + 30) * S), fill=(255, 255, 255, 255), outline=OLN, width=4 * S)   # taste pore
    for k in (-120, -40, 40, 120):
        d.line([((cx + k) * S, (bot + 10) * S), ((cx + k * 1.4) * S, (H - 10) * S)], fill=(250, 190, 60, 255), width=6 * S)
    return done(im, W, H)


def oldmap_pic(cross=False):
    """the old (wrong) 'tongue map' drawn on a simple tongue shape."""
    W, H = 640, 760
    im, d = new(W, H)
    d.rounded_rectangle((90 * S, 40 * S, 550 * S, 740 * S), radius=230 * S, fill=(240, 160, 170, 255), outline=OLN, width=6 * S)
    d.line([(320 * S, 80 * S), (320 * S, 560 * S)], fill=(200, 110, 125, 255), width=5 * S)
    zones = [((200, 560, 440, 720), (240, 130, 170)), ((110, 380, 230, 560), (110, 170, 230)), ((410, 380, 530, 560), (110, 170, 230)),
             ((110, 200, 230, 380), (240, 200, 60)), ((410, 200, 530, 380), (240, 200, 60)), ((190, 60, 450, 190), (130, 170, 90))]
    for (x0, y0, x1, y1), c in zones:
        d.rounded_rectangle((x0 * S, y0 * S, x1 * S, y1 * S), radius=40 * S, fill=c + (200,), outline=OLN, width=3 * S)
    if cross:
        d.line([(40 * S, 60 * S), (600 * S, 720 * S)], fill=(210, 50, 50, 255), width=22 * S)
        d.line([(600 * S, 60 * S), (40 * S, 720 * S)], fill=(210, 50, 50, 255), width=22 * S)
    return done(im, W, H)


def berry_pic():
    W, H = 300, 340
    im, d = new(W, H)
    d.polygon([(150 * S, 330 * S), (30 * S, 120 * S), (80 * S, 70 * S), (220 * S, 70 * S), (270 * S, 120 * S)], fill=(225, 50, 70, 255), outline=OLN)
    d.line([(150 * S, 330 * S), (30 * S, 120 * S), (80 * S, 70 * S), (220 * S, 70 * S), (270 * S, 120 * S), (150 * S, 330 * S)], fill=OLN, width=5 * S, joint="curve")
    for x, y in ((90, 120), (150, 110), (210, 120), (110, 180), (190, 180), (150, 240), (120, 140), (180, 150)):
        d.ellipse(((x - 6) * S, (y - 9) * S, (x + 6) * S, (y + 9) * S), fill=(255, 225, 120, 255))
    for a in (-60, -20, 20, 60):
        d.polygon([(150 * S, 70 * S), ((150 + a * 1.3) * S, 20 * S), ((150 + a * 0.5) * S, 75 * S)], fill=(90, 170, 80, 255), outline=OLN)
    return done(im, W, H)


def pinch_pic():
    """two fingertips pinching the nose."""
    W, H = 220, 220
    im, d = new(W, H)
    SK = (240, 200, 170, 255)
    d.rounded_rectangle((20 * S, 20 * S, 200 * S, 80 * S), radius=30 * S, fill=SK, outline=OLN, width=5 * S)
    d.rounded_rectangle((20 * S, 140 * S, 200 * S, 200 * S), radius=30 * S, fill=SK, outline=OLN, width=5 * S)
    d.ellipse((150 * S, 28 * S, 190 * S, 72 * S), fill=(250, 225, 215, 255), outline=OLN, width=3 * S)
    d.ellipse((150 * S, 148 * S, 190 * S, 192 * S), fill=(250, 225, 215, 255), outline=OLN, width=3 * S)
    return done(im, W, H)


def scale_pt(cx, cy, w, img_w, img_h, x, y):
    k = w / img_w
    return (cx - w / 2 + x * k, cy - img_h * k / 2 + y * k)


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
    Y = PH
    cam(0, *A, 1.0, 0.1)
    kS = 900 / 876                                                 # Servier sagittal section at w=900

    # ---------------- STORY (A): a head in profile (Servier line art), pinch + strawberry, then dive into the nose
    s = sc["story"]
    hw = 820
    def hp(x, y):
        return scale_pt(760, 560, hw, 592, 653, x, y)
    st = [pop(sv("bouche.png"), 760, 560, w=hw, t=0.0, dur=0.3), pop(berry_pic(), 210, 820, w=220, t=s.t("strawberry") - 0.4),
          pop(pinch_pic(), hp(18, 360)[0], hp(18, 360)[1], w=150, t=s.t("pinch") - 0.2),
          text("PINCH your nose", 300, 120, 54, RED_T, s.t("pinch") - 0.3, "c"), text("+ eat a strawberry", 300, 220, 44, RED_T, s.t("strawberry") - 0.3, "c"),
          text("still SWEET", 1500, 260, 64, GOLD_T, s.t("sweet") - 0.4, "c"), text("but the flavor... gone?", 1500, 400, 54, PURPLE, s.t("disappears") - 0.6, "c"),
          text("flavor = 2 senses", 1500, 620, 60, GREEN_T, s.t("teamwork") - 0.5, "c"), text("follow a bite", 1500, 800, 58, MAROON, s.t("follow") - 0.8, "c")]
    cv.glow(s.t("pinch") - 0.1, hp(18, 380), 2.5, 70, (235, 90, 90))
    cv.flow([hp(-60, 520), hp(-20, 505), hp(25, 490)], s.t("strawberry") + 0.2, s.t("follow"), 1.4, TASTE, 10, 2)
    cv.dive_out(s, hp(170, 330), 4.0, 2.0)

    # ---------------- NOSE (B): molecules rise to the smell patch
    s = sc["nose"]
    cv.land(s, Bc)
    bd.erase(s.start + 0.8, st[:3])
    bd.erase(s.start - 1.2, st[3:])
    X = PW
    no = [pop(section_pic(), X + 500, 540, w=900, t=s.start), text("SMELL = molecules", X + 1460, 200, 58, GREEN_T, s.t("molecules") - 0.3, "c"),
          text("travel up the nose", X + 1460, 340, 54, BLUE_T, s.t("travel") - 0.3, "c"), text("OLFACTORY EPITHELIUM", X + 1460, 500, 50, GOLD_T, s.t("olfactory") - 0.6, "c"),
          text("dissolve in MUCUS", X + 1460, 680, 58, PURPLE, s.t("dissolve") - 0.8, "c")]
    cv.flow([(X + 50 + x * kS, 204.5 + y * kS) for x, y in ((-60, 200), (30, 150), (90, 110), (160, 70), (235, 32))], s.t("travel") - 0.3, s.start + s.dur, 2.6, SMELL, 13, 4)
    cv.glow(s.t("patch") - 0.2, (X + 50 + 240 * kS, 204.5 + 14 * kS), 3.0, 90, (250, 200, 60))
    cv.push(s, Bc, 1.0, 1.9)
    cv.dive_out(s, (X + 296, 222), 4.0, 1.5)

    # ---------------- RECEPTORS (C): neurons fire
    s = sc["receptors"]
    cv.land(s, C)
    bd.erase(s.start + 0.8, no[:1])
    bd.erase(s.start - 1.0, no[1:])
    X = 2 * PW
    re = [pop(SM.epi_pic(), X + 520, 540, w=900, t=s.start), text("SENSORY NEURONS", X + 1480, 200, 58, PURPLE, s.t("neurons") - 0.4, "c"),
          text("HUNDREDS of receptor kinds", X + 1480, 340, 46, GOLD_T, s.t("hundreds") - 0.4, "c"), text("molecule fits = SIGNAL", X + 1480, 500, 54, RED_T, s.t("fits") - 0.5, "c"),
          text("a different route?", X + 1480, 760, 70, PURPLE, s.t("strange") - 0.6, "c")]
    for i_, x_ in enumerate(range(80, 860, 120)):
        cv.flow([(X + 70 + x_, 610), (X + 70 + x_, 700), (X + 70 + x_, 775)], s.t("fires") - 0.3 + 0.12 * i_, s.start + s.dur, 1.3, SIG, 10, 1)
    cv.push(s, C, 1.2)

    # ---------------- BRAIN (D -> E): through the skull to the bulb, then emotion + memory
    s = sc["brain"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, re)
    kb = 940 / 1119
    br1 = [pop(sv("Bulbes_olfactifs2.png"), 520, Y + 540, w=940, t=s.start + 0.3), text("tiny HOLES in the skull", 1450, Y + 260, 54, MAROON, s.t("holes") - 0.4, "c"),
           text("OLFACTORY BULB", 1450, Y + 460, 64, RED_T, s.t("bulb") - 0.2, "c")]
    for i_, x_ in enumerate((265, 415, 600, 790)):
        cv.flow([(50 + x_ * kb, Y + 192 + 660 * kb), (50 + x_ * kb, Y + 192 + 440 * kb), (50 + (x_ + 10) * kb, Y + 192 + 290 * kb)], s.start + 1.2 + 0.25 * i_, s.t("amygdala") + 1.0, 1.6, SIG, 11, 1)
    tm = s.t("from") - 0.3
    cam(tm, *E, 1.0, 1.2)
    bd.erase(tm + 1.4, br1)
    X = PW
    lx, ly = X + 20, Y + 200
    br2 = [pop(SM.limbic_pic(), X + 520, Y + 480, w=1000, t=tm), text("AMYGDALA = emotion", X + 1490, Y + 160, 50, RED_T, s.t("amygdala") - 0.4, "c"),
           text("HIPPOCAMPUS = memory", X + 1490, Y + 700, 50, PURPLE, s.t("hippocampus") - 0.4, "c"), text("THALAMUS: skipped", X + 560, Y + 820, 52, MAROON, s.t("skips") - 0.8, "c"),
           text("memory back FAST", X + 1490, Y + 420, 66, GOLD_T, s.t("fast") - 0.8, "c")]
    cv.flow([(lx + 90, ly + 270), (lx + 290, ly + 270), (lx + 500, ly + 270), (lx + 680, ly + 160), (lx + 830, ly + 120)], tm + 0.6, s.start + s.dur, 2.0, SIG, 12, 2)
    cv.flow([(lx + 90, ly + 270), (lx + 290, ly + 270), (lx + 500, ly + 270), (lx + 680, ly + 390), (lx + 860, ly + 415)], tm + 0.6, s.start + s.dur, 2.0, SIG, 12, 2)
    cv.glow(s.t("amygdala") - 0.3, (lx + 830, ly + 120), 2.5, 90, (235, 90, 90))
    cv.glow(s.t("hippocampus") - 0.3, (lx + 860, ly + 415), 2.5, 100, (150, 110, 220))

    # ---------------- TONGUE (F): papillae and taste buds
    s = sc["tongue"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, br2)
    X = 2 * PW
    oc_w = 560
    to = [pop(sv("oral-cavity.png"), X + 380, Y + 540, w=oc_w, t=s.start + 0.3), text("now: TASTE", X + 1390, Y + 120, 66, RED_T, s.t("taste") - 0.3, "c"),
          pop(sv("Papilles_gustatives.png"), X + 1390, Y + 420, w=760, t=s.t("papillae") - 0.5), text("PAPILLAE = small bumps", X + 1390, Y + 720, 50, PURPLE, s.t("papillae") - 0.3, "c"),
          text("THOUSANDS of taste buds", X + 1390, Y + 830, 48, GOLD_T, s.t("thousands") - 0.5, "c"),
          text("50-150 receptor cells each", X + 1390, Y + 940, 44, MAROON, s.t("fifty") - 0.3, "c")]
    kp = 760 / 577
    for bx, by in ((155, 210), (295, 210)):                     # the taste buds in the papilla walls
        cv.glow(s.t("buds") - 0.2, (X + 1390 - 380 + bx * kp, Y + 420 - 175 * kp + by * kp), 3.5, 40, (250, 200, 60))
    tongue_pt = scale_pt(X + 380, Y + 540, oc_w, 489, 756, 245, 520)
    cv.glow(s.t("tongue") - 0.2, tongue_pt, 2.4, 130, (240, 120, 150))
    cv.push(s, Fp, 1.2, 1.8)
    cv.dive_out(s, (X + 1390 - 380 + 225 * kp, Y + 420 - 175 * kp + 210 * kp), 4.0, 1.4)

    # ---------------- FIVE (A): one taste bud, five tastes, the tongue-map myth
    s = sc["five"]
    cv.land(s, A)
    bd.erase(s.start + 0.8, to[:1] + to[2:3])
    bd.erase(s.start - 1.0, to[1:2] + to[3:])
    fi = [pop(bud_pic(), 470, 420, w=820, t=s.start), text("TASTE RECEPTOR CELLS", 470, 820, 48, PURPLE, s.t("cells") - 0.3, "c")]
    for i, (w, c) in enumerate(TASTES):
        y = 140 + i * 125
        fi += [panel(1180, y - 50, 1640, y + 50, c, s.t(w.lower()) - 0.3), text(w, 1410, y, 54, MAROON, s.t(w.lower()) - 0.2, "c")]
    fi += [text("(umami = savory)", 1410, 770, 40, MAROON, s.t("savory") - 0.4, "c"),
           pop(oldmap_pic(True), 1760, 880, w=180, t=s.t("map") - 0.3), text("NO tongue map!", 1410, 900, 62, RED_T, s.t("myth") - 0.2, "c"),
           text("every taste, all over", 1410, 1000, 46, GREEN_T, s.t("spread") - 0.6, "c")]
    cv.glow(s.start + 0.6, (470, 175), 2.4, 50, (250, 200, 60))
    cv.push(s, A, 1.0)

    # ---------------- NERVES (B): three cranial nerves, then the thalamus
    s = sc["nerves"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, fi)
    X = PW
    bw = 640
    def bp(x, y):
        return scale_pt(X + 500, 520, bw, 580, 592, x, y)
    ne = [pop(sv("Cerveau_beau.png"), X + 500, 520, w=bw, t=s.start + 0.3), text("3 CRANIAL NERVES", X + 1440, 160, 62, GOLD_T, s.t("three") - 0.3, "c"),
          text("FACIAL", X + 1440, 300, 56, RED_T, s.t("facial") - 0.2, "c"), text("GLOSSOPHARYNGEAL", X + 1440, 400, 50, PURPLE, s.t("glossopharyngeal") - 0.2, "c"),
          text("VAGUS", X + 1440, 500, 56, BLUE_T, s.t("vagus") - 0.2, "c"),
          text("THALAMUS first", X + 1440, 680, 58, MAROON, s.t("thalamus") - 0.4, "c"), text("-> taste area of the brain", X + 1440, 800, 46, GREEN_T, s.t("area") - 1.4, "c")]
    for i, (col, x0) in enumerate((((235, 90, 90), -40), ((150, 110, 220), 20), ((70, 160, 230), 80))):
        cv.flow([bp(255 + x0 / 4, 590), bp(275, 520), bp(290, 430), bp(300, 300)], (s.t("facial"), s.t("glossopharyngeal"), s.t("vagus"))[i] - 0.2,
                s.start + s.dur, 2.0, col, 11, 2)
    cv.glow(s.t("thalamus") - 0.3, bp(300, 290), 2.6, 60, (250, 200, 60))
    cv.glow(s.t("area") - 0.3, bp(240, 230), 3.0, 70, (120, 200, 120))
    cv.push(s, Bc, 1.0)

    # ---------------- RENEW (C)
    s = sc["renew"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ne)
    X = 2 * PW
    rn = [pop(SM.renew_pic(), X + 520, 480, w=900, t=s.start + 0.3), text("something RARE", X + 1450, 200, 60, PURPLE, s.t("rare") - 0.3, "c"),
          text("taste + smell cells", X + 1450, 360, 54, MAROON, s.t("taste") - 0.3, "c"), text("are REPLACED", X + 1450, 470, 64, GREEN_T, s.t("replaced") - 0.3, "c"),
          text("taste cells: ~ every 10 days", X + 1450, 680, 46, GOLD_T, s.t("ten") - 1.6, "c")]
    cv.glow(s.t("replaced") - 0.2, (X + 520 - 450 + 170, 480 - 210 + 320), 2.5, 60, (250, 200, 60))
    cv.push(s, C, 1.0)

    # ---------------- FLAVOR (D): aroma rises from the mouth to the nose
    s = sc["flavor"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, rn)
    fl = [pop(section_pic(True), 500, Y + 540, w=900, t=s.start + 0.3), text("FLAVOR = ?", 1450, Y + 140, 70, PURPLE, s.t("flavor") - 0.3, "c"),
          text("chewing -> AROMA rises", 1450, Y + 300, 52, GREEN_T, s.t("aroma") - 0.5, "c"), text("brain BLENDS it with taste", 1450, Y + 450, 46, GOLD_T, s.t("blends") - 0.5, "c"),
          text("nose blocked = BLAND", 1450, Y + 620, 58, RED_T, s.t("bland") - 0.4, "c"), text("taste buds still work", 1450, Y + 780, 50, MAROON, s.t("buds") - 0.4, "c")]
    cv.flow([(50 + x * kS, Y + 204.5 + y * kS) for x, y in ((300, 330), (420, 280), (430, 170), (380, 90), (290, 45))], s.t("chew") - 0.2, s.start + s.dur, 2.4, SMELL, 13, 4)
    cv.push(s, D, 1.0)

    # ---------------- CARE (E)
    s = sc["care"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, fl)
    X = PW
    ca = [text("SUDDEN loss of smell or taste?", X + 960, Y + 280, 70, RED_T, s.t("suddenly") - 0.3, "c"),
          text("or not back 1-2 weeks after a cold", X + 960, Y + 440, 56, MAROON, s.t("week") - 0.8, "c"),
          panel(X + 560, Y + 600, X + 1360, Y + 760, MINT, s.t("doctor") - 1.2), text("see a doctor", X + 960, Y + 680, 70, GREEN_T, s.t("doctor") - 1.0, "c")]

    # ---------------- RECAP (F)
    s = sc["recap"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, ca)
    X = 2 * PW
    rp = title("remember 3 things", X + 960, Y + 100, s.start + 0.4)
    for w, a, b, col, tc_, x in (("smell", "smell -> receptors", "emotion + memory", MINT, GREEN_T, 400), ("taste", "5 basic tastes", "all over the tongue", PINK, RED_T, 960),
                                 ("flavor", "FLAVOR =", "taste + smell", CREAM, GOLD_T, 1520)):
        tw2 = s.t(w) - 0.3
        rp += [panel(X + x - 265, Y + 220, X + x + 265, Y + 600, col, tw2 - 0.2), text(a, X + x, Y + 360, 40, tc_, tw2, "c"), text(b, X + x, Y + 470, 36, MAROON, tw2 + 0.6, "c")]
    tn = s.t("next") - 1.2
    rp += [panel(X + 200, Y + 720, X + 1720, Y + 890, LILAC, tn - 0.3), text("next: the reproductive system", X + 960, Y + 820, 52, PURPLE, tn, "c")]

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
        a = [pop(oldmap_pic(), 560, 540, w=620, t=0.0, dur=0.3), text("the TONGUE MAP", 1430, 220, 70, PURPLE, s.t("tongue") - 0.4, "c"),
             text("sweet at the tip", 1430, 420, 56, RED_T, s.t("sweet") - 0.3, "c"), text("bitter at the back", 1430, 560, 56, GREEN_T, s.t("bitter") - 1.0, "c")]
        cv.push(s, A, 0.4, 0.2)
        s = sc["turn"]
        cam(s.start, *Bc, 1.0, 0.9)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(oldmap_pic(True), X + 560, 540, w=620, t=s.start + 0.2), text("a MYTH", X + 1430, 220, 96, RED_T, s.t("myth") - 0.3, "c"),
             text("every taste, all over", X + 1430, 420, 54, GREEN_T, s.t("over") - 1.0, "c"), text("how many tastes?", X + 1430, 620, 60, GOLD_T, s.t("many") - 1.4, "c"),
             text("?", X + 1430, 820, 180, PURPLE, s.t("tastes") - 0.9, "c")]
        cv.push(s, Bc, 0.6, 0.2)
    else:
        s = sc["case"]
        kS = 900 / 876
        a = [pop(section_pic(), 500, 540, w=900, t=0.0, dur=0.3), text("STUFFY nose", 1450, 240, 76, BLUE_T, s.t("stuffy") - 0.4, "c"),
             text("favorite food = BLAND", 1450, 440, 56, RED_T, s.t("favorite") - 0.2, "c")]
        cv.glow(0.3, (50 + 120 * kS, 204.5 + 120 * kS), s.dur, 120, (110, 170, 230))
        cv.push(s, A, 0.4, 0.2)
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 0.9)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(bud_pic(), X + 520, 480, w=820, t=s.start + 0.2), text("taste buds: FINE", X + 1450, 300, 66, GREEN_T, s.t("buds") - 0.4, "c"),
             text("something else is missing", X + 1450, 520, 46, PURPLE, s.t("something") - 0.2, "c")]
        cv.push(s, Bc, 0.5, 0.2)
        s = sc["clue"]
        cam(s.start, *C, 1.0, 0.9)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        c = [pop(section_pic(True), X + 500, 540, w=900, t=s.start + 0.2), text("what is missing?", X + 1450, 300, 66, GOLD_T, s.t("what") - 0.3, "c"),
             text("?", X + 1450, 640, 200, PURPLE, s.t("flavor") - 0.2, "c")]
        cv.push(s, C, 0.4, 0.2)

    bd.fx.append(cv.fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def make_short(n):
    import package as Pk
    import bridge
    bd, sc = build_short(n)
    board = NU.render_board(bd, sc, f"smelltaste_story{n}")
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
    ov = OUT / f"smelltaste_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"smelltaste_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["smelltaste"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "smelltaste", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            for fr in (0.45, 0.9):
                OF.credit(bd.frame(round(v.start + v.dur * fr, 1))).save(OUT / f"st_{v.id}_{int(fr * 100)}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                OF.credit(bd.frame(round(v.start + v.dur * 0.8, 1))).save(OUT / f"st_short{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "smelltaste", intro=True)
        f.replace(OUT / "final_smelltaste.mp4")
        print("done ->", OUT / "final_smelltaste.mp4")
