"""SMELL & TASTE v2 - cinematic build with the OWNER's scene images art/smelltaste/shot1-6 (fact-checked script ../smelltaste).

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
from osm_ear2 import Cine, P as P0  # noqa: E402

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


OF.credit = lambda frame: frame          # owner art only: no Servier credit line on screen
ART = HERE.parent / "art" / "smelltaste"
CR = 26


def shot(n):
    im = Image.open(ART / f"shot{n}.jpg").convert("RGBA")
    return im.crop((CR, CR, 1376 - CR, 768 - CR)).resize((1376, 768), Image.LANCZOS)


def P(ox, oy, x, y):
    return P0(ox, oy, (x - CR) * 1376 / (1376 - 2 * CR), (y - CR) * 768 / (768 - 2 * CR))


def map_shot(cross=False):
    """owner's tongue (shot5) with the OLD, wrong 'tongue map' painted on it."""
    im = shot(5)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    def q(x, y):
        return ((x - CR) * 1376 / (1376 - 2 * CR), (y - CR) * 768 / (768 - 2 * CR))
    zones = [((300, 120, 620, 260), (130, 170, 90)), ((250, 280, 360, 470), (240, 200, 60)), ((560, 280, 670, 470), (240, 200, 60)),
             ((250, 480, 360, 620), (110, 170, 230)), ((560, 480, 670, 620), (110, 170, 230)), ((340, 600, 580, 730), (240, 130, 170))]
    for (x0, y0, x1, y1), c in zones:
        a, b = q(x0, y0), q(x1, y1)
        d.rounded_rectangle((a[0], a[1], b[0], b[1]), radius=40, fill=c + (150,), outline=(110, 80, 90, 220), width=4)
    if cross:
        a, b = q(200, 60), q(720, 750)
        d.line([a, b], fill=(210, 50, 50, 255), width=26)
        d.line([(b[0], a[1]), (a[0], b[1])], fill=(210, 50, 50, 255), width=26)
    im.alpha_composite(lay)
    return im


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

    # ---------------- STORY (A): the owner's person pinching the nose, strawberry -> dive into the nose
    s = sc["story"]
    st = [pop(shot(1), 960, 540, w=1920, t=0.0, dur=0.4), text("PINCH your nose", 1560, 200, 62, RED_T, s.t("pinch") - 0.3, "c"),
          text("+ eat a strawberry", 1560, 310, 50, RED_T, s.t("strawberry") - 0.3, "c"), text("still SWEET", 1560, 470, 64, GOLD_T, s.t("sweet") - 0.4, "c"),
          text("but the flavor... gone?", 1560, 590, 50, PURPLE, s.t("disappears") - 0.6, "c"), text("flavor = 2 senses", 1560, 750, 58, GREEN_T, s.t("teamwork") - 0.5, "c"),
          text("follow a bite", 1560, 880, 56, MAROON, s.t("follow") - 1.4, "c")]
    cv.glow(s.t("pinch") - 0.1, P(0, 0, 560, 300), 2.5, 70, (235, 90, 90))
    cv.glow(s.t("strawberry") - 0.1, P(0, 0, 600, 385), 2.5, 70, TASTE)
    cv.dive_out(s, P(0, 0, 545, 300), 4.5, 2.0)

    # ---------------- NOSE (B): molecules rise to the smell patch
    s = sc["nose"]
    cv.land(s, Bc)
    bd.erase(s.start + 0.8, st[:1])
    bd.erase(s.start - 1.2, st[1:])
    X = PW
    no = [pop(shot(2), X + 960, 540, w=1920, t=s.start), text("SMELL = molecules", X + 1560, 200, 58, GREEN_T, s.t("molecules") - 0.3, "c"),
          text("travel up the nose", X + 1560, 340, 54, BLUE_T, s.t("travel") - 0.3, "c"), text("OLFACTORY EPITHELIUM", X + 1560, 500, 48, GOLD_T, s.t("olfactory") - 0.6, "c"),
          text("dissolve in MUCUS", X + 1560, 680, 58, PURPLE, s.t("dissolve") - 0.8, "c")]
    cv.flow([P(X, 0, x, y) for x, y in ((900, 400), (800, 375), (730, 330), (700, 270), (680, 205))], s.t("travel") - 0.3, s.start + s.dur, 2.6, SMELL, 13, 4)
    cv.glow(s.t("patch") - 0.2, P(X, 0, 675, 195), 3.0, 80, (250, 200, 60))
    cv.push(s, Bc, 1.0, 1.9)
    cv.dive_out(s, P(X, 0, 675, 195), 4.0, 1.5)

    # ---------------- RECEPTORS (C): the smell neurons fire
    s = sc["receptors"]
    cv.land(s, C)
    bd.erase(s.start + 0.8, no[:1])
    bd.erase(s.start - 1.0, no[1:])
    X = 2 * PW
    re = [pop(shot(3), X + 960, 540, w=1920, t=s.start), text("SENSORY NEURONS", X + 1560, 200, 58, PURPLE, s.t("neurons") - 0.4, "c"),
          text("HUNDREDS of receptor kinds", X + 1560, 340, 44, GOLD_T, s.t("hundreds") - 0.4, "c"), text("molecule fits = SIGNAL", X + 1560, 500, 54, RED_T, s.t("fits") - 0.5, "c"),
          text("a different route?", X + 1560, 760, 68, PURPLE, s.t("strange") - 0.6, "c")]
    for i, x in enumerate((300, 340, 380, 420, 465, 505, 545)):
        cv.glow(s.t("fires") - 0.3 + 0.1 * i, P(X, 0, x, 560), 1.6, 30, SIG)
        cv.flow([P(X, 0, x, 620), P(X, 0, x, 520), P(X, 0, x + (420 - x) * 0.4, 380), P(X, 0, 420 + (x - 420) * 0.5, 230)], s.t("fires") - 0.2 + 0.12 * i, s.start + s.dur, 1.6, SIG, 9, 1)
    cv.flow([P(X, 0, x, 690) for x in (240, 330, 420)], s.start + 0.6, s.t("fits"), 2.0, SMELL, 10, 2)
    cv.push(s, C, 1.2)

    # ---------------- BRAIN (D -> E): through the skull holes to the bulb, then emotion + memory
    s = sc["brain"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, re)
    br1 = [pop(shot(3), 960, Y + 540, w=1920, t=s.start + 0.3), text("tiny HOLES in the skull", 1560, Y + 260, 52, MAROON, s.t("holes") - 0.4, "c"),
           text("OLFACTORY BULB", 1560, Y + 460, 62, RED_T, s.t("bulb") - 0.2, "c")]
    cv.glow(s.t("holes") - 0.2, P(0, Y, 430, 320), 2.4, 90, (250, 200, 60))
    for i, x in enumerate((370, 420, 470)):
        cv.flow([P(0, Y, x, 520), P(0, Y, x, 330), P(0, Y, 420 + (x - 420) * 1.6, 170)], s.start + 1.0 + 0.2 * i, s.t("from") + 0.6, 1.5, SIG, 10, 1)
    cv.glow(s.t("bulb") - 0.2, P(0, Y, 420, 170), 2.6, 130, SMELL)
    tm = s.t("from") - 0.3
    cam(tm, *E, 1.0, 1.2)
    bd.erase(tm + 1.4, br1)
    X = PW
    br2 = [pop(shot(4), X + 960, Y + 540, w=1920, t=tm), text("AMYGDALA = emotion", X + 1580, Y + 200, 50, RED_T, s.t("amygdala") - 0.4, "c"),
           text("HIPPOCAMPUS = memory", X + 1580, Y + 360, 48, PURPLE, s.t("hippocampus") - 0.4, "c"), text("smell SKIPS the thalamus", X + 1580, Y + 560, 44, MAROON, s.t("skips") - 0.9, "c"),
           text("memory back FAST", X + 1580, Y + 760, 64, GOLD_T, s.t("fast") - 0.9, "c")]
    cv.flow([P(X, Y, x, y) for x, y in ((275, 410), (360, 400), (445, 440))], tm + 0.6, s.start + s.dur, 1.6, SIG, 11, 2)
    cv.flow([P(X, Y, x, y) for x, y in ((275, 410), (380, 380), (480, 380), (560, 410))], tm + 0.8, s.start + s.dur, 1.9, SIG, 11, 2)
    cv.glow(tm + 0.4, P(X, Y, 275, 410), 2.0, 70, SMELL)
    cv.glow(s.t("amygdala") - 0.3, P(X, Y, 445, 445), 2.5, 80, (235, 90, 90))
    cv.glow(s.t("hippocampus") - 0.3, P(X, Y, 560, 410), 2.5, 90, (150, 110, 220))

    # ---------------- TONGUE (F): papillae and taste buds
    s = sc["tongue"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, br2)
    X = 2 * PW
    to = [pop(shot(5), X + 960, Y + 540, w=1920, t=s.start + 0.3), text("now: TASTE", X + 1560, Y + 160, 66, RED_T, s.t("taste") - 0.3, "c"),
          text("PAPILLAE = small bumps", X + 1560, Y + 340, 48, PURPLE, s.t("papillae") - 0.3, "c"), text("THOUSANDS of taste buds", X + 1560, Y + 500, 46, GOLD_T, s.t("thousands") - 0.5, "c"),
          text("50-150 receptor cells", X + 1560, Y + 660, 48, MAROON, s.t("fifty") - 0.6, "c"), text("in each bud", X + 1560, Y + 750, 44, MAROON, s.t("fifty") - 0.2, "c")]
    cv.glow(s.t("tongue") - 0.2, P(X, Y, 460, 430), 2.4, 220, TASTE)
    for i, (x, y) in enumerate(((300, 180), (380, 215), (460, 250), (540, 215), (620, 180))):
        cv.glow(s.t("papillae") - 0.2 + 0.12 * i, P(X, Y, x, y), 2.0, 34, (250, 200, 60))
    for i, (x, y) in enumerate(((330, 400), (560, 420), (400, 560), (520, 600), (450, 330))):
        cv.glow(s.t("buds") - 0.2 + 0.1 * i, P(X, Y, x, y), 2.6, 26, (250, 200, 60))
    cv.push(s, Fp, 1.2, 1.8)
    cv.dive_out(s, P(X, Y, 460, 250), 4.0, 1.4)

    # ---------------- FIVE (A): one taste bud, five tastes, the tongue-map myth
    s = sc["five"]
    cv.land(s, A)
    bd.erase(s.start + 0.8, to[:1])
    bd.erase(s.start - 1.0, to[1:])
    fi = [pop(shot(6), 960, 540, w=1920, t=s.start), text("TASTE RECEPTOR CELLS", 1460, 70, 40, PURPLE, s.t("cells") - 0.3, "c")]
    for i, (w, c) in enumerate(TASTES):
        y = 170 + i * 110
        fi += [panel(1240, y - 44, 1680, y + 44, c, s.t(w.lower()) - 0.3), text(w, 1460, y, 50, MAROON, s.t(w.lower()) - 0.2, "c")]
    fi += [text("(umami = savory)", 1460, 735, 38, MAROON, s.t("savory") - 0.4, "c"),
           text("NO tongue map!", 1460, 860, 60, RED_T, s.t("myth") - 0.2, "c"), text("every taste, all over", 1460, 960, 44, GREEN_T, s.t("spread") - 0.9, "c")]
    cv.glow(s.start + 0.6, P(0, 0, 440, 130), 2.4, 50, (250, 200, 60))
    for i, (w, c) in enumerate(TASTES):
        cv.glow(s.t(w.lower()) - 0.2, P(0, 0, 360 + 40 * i, 380), 1.4, 45, c)
    cv.push(s, A, 1.0)

    # ---------------- NERVES (B): three cranial nerves, then the thalamus
    s = sc["nerves"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, fi)
    X = PW
    ne = [pop(shot(4), X + 960, 540, w=1920, t=s.start + 0.3), text("3 CRANIAL NERVES", X + 1580, 160, 60, GOLD_T, s.t("three") - 0.3, "c"),
          text("FACIAL", X + 1580, 290, 56, RED_T, s.t("facial") - 0.2, "c"), text("GLOSSOPHARYNGEAL", X + 1580, 390, 46, PURPLE, s.t("glossopharyngeal") - 0.2, "c"),
          text("VAGUS", X + 1580, 490, 56, BLUE_T, s.t("vagus") - 0.2, "c"),
          text("THALAMUS first", X + 1580, 680, 58, MAROON, s.t("thalamus") - 0.4, "c"), text("-> taste area of the brain", X + 1580, 800, 42, GREEN_T, s.t("area") - 1.4, "c")]
    for i, col in enumerate(((235, 90, 90), (150, 110, 220), (70, 160, 230))):
        x0 = 590 + 20 * i
        cv.flow([P(X, 0, x0, 700), P(X, 0, x0 + 5, 600), P(X, 0, 580, 470), P(X, 0, 545, 350)], (s.t("facial"), s.t("glossopharyngeal"), s.t("vagus"))[i] - 0.2,
                s.start + s.dur, 2.0, col, 11, 2)
    cv.glow(s.t("thalamus") - 0.3, P(X, 0, 540, 340), 2.6, 60, (250, 200, 60))
    cv.glow(s.t("area") - 0.3, P(X, 0, 470, 320), 3.0, 75, (120, 200, 120))
    cv.push(s, Bc, 1.0)

    # ---------------- RENEW (C): new taste cells from the base of the bud
    s = sc["renew"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ne)
    X = 2 * PW
    rn = [pop(shot(6), X + 960, 540, w=1920, t=s.start + 0.3), text("something RARE", X + 1560, 200, 60, PURPLE, s.t("rare") - 0.3, "c"),
          text("taste + smell cells", X + 1560, 360, 54, MAROON, s.t("taste") - 0.3, "c"), text("are REPLACED", X + 1560, 470, 64, GREEN_T, s.t("replaced") - 0.3, "c"),
          text("taste cells: ~ every 10 days", X + 1560, 680, 44, GOLD_T, s.t("ten") - 1.6, "c")]
    for i, x in enumerate((340, 400, 460, 520)):
        cv.glow(s.t("replaced") - 0.2 + 0.25 * i, P(X, 0, x, 520), 2.2, 40, (120, 200, 120))
    cv.flow([P(X, 0, 440, 600), P(X, 0, 440, 480), P(X, 0, 440, 330)], s.t("replaced"), s.start + s.dur, 2.2, (120, 200, 120), 12, 2)
    cv.push(s, C, 1.0)

    # ---------------- FLAVOR (D): aroma rises from the back of the mouth to the smell patch
    s = sc["flavor"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, rn)
    fl = [pop(shot(2), 960, Y + 540, w=1920, t=s.start + 0.3), text("FLAVOR = ?", 1560, Y + 140, 70, PURPLE, s.t("flavor") - 0.3, "c"),
          text("chewing -> AROMA rises", 1560, Y + 300, 50, GREEN_T, s.t("aroma") - 0.5, "c"), text("brain BLENDS it with taste", 1560, Y + 450, 44, GOLD_T, s.t("blends") - 0.5, "c"),
          text("nose blocked = BLAND", 1560, Y + 620, 56, RED_T, s.t("bland") - 0.4, "c"), text("taste buds still work", 1560, Y + 780, 48, MAROON, s.t("buds") - 0.4, "c")]
    cv.flow([P(0, Y, x, y) for x, y in ((650, 440), (560, 430), (490, 390), (470, 310), (520, 250), (600, 215), (675, 195))], s.t("chew") - 0.2, s.start + s.dur, 2.6, SMELL, 13, 4)
    cv.glow(s.t("blends") - 0.2, P(0, Y, 675, 195), 2.4, 80, (250, 200, 60))
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
        a = [pop(map_shot(), 960, 540, w=1920, t=0.0, dur=0.3), text("the TONGUE MAP", 1560, 220, 66, PURPLE, s.t("tongue") - 0.4, "c"),
             text("sweet at the tip", 1560, 420, 54, RED_T, s.t("sweet") - 0.3, "c"), text("bitter at the back", 1560, 560, 54, GREEN_T, s.t("bitter") - 1.0, "c")]
        cv.push(s, A, 0.4, 0.2)
        s = sc["turn"]
        cam(s.start, *Bc, 1.0, 0.9)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(map_shot(True), X + 960, 540, w=1920, t=s.start + 0.2), text("a MYTH", X + 1560, 220, 96, RED_T, s.t("myth") - 0.3, "c"),
             text("every taste, all over", X + 1560, 420, 52, GREEN_T, s.t("over") - 1.0, "c"), text("how many tastes?", X + 1560, 620, 58, GOLD_T, s.t("many") - 1.4, "c"),
             text("?", X + 1560, 820, 180, PURPLE, s.t("tastes") - 0.9, "c")]
        cv.push(s, Bc, 0.6, 0.2)
    else:
        s = sc["case"]
        a = [pop(shot(2), 960, 540, w=1920, t=0.0, dur=0.3), text("STUFFY nose", 1560, 240, 76, BLUE_T, s.t("stuffy") - 0.4, "c"),
             text("favorite food = BLAND", 1560, 440, 54, RED_T, s.t("favorite") - 0.2, "c")]
        cv.glow(0.3, P(0, 0, 640, 290), s.dur, 150, (110, 170, 230))
        cv.push(s, A, 0.4, 0.2)
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 0.9)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(shot(6), X + 960, 540, w=1920, t=s.start + 0.2), text("taste buds: FINE", X + 1560, 300, 66, GREEN_T, s.t("buds") - 0.4, "c"),
             text("something else is missing", X + 1560, 520, 44, PURPLE, s.t("something") - 0.2, "c")]
        cv.glow(s.start + 0.4, P(X, 0, 440, 380), s.dur, 120, (120, 200, 120))
        cv.push(s, Bc, 0.5, 0.2)
        s = sc["clue"]
        cam(s.start, *C, 1.0, 0.9)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        c = [pop(shot(2), X + 960, 540, w=1920, t=s.start + 0.2), text("what is missing?", X + 1560, 300, 64, GOLD_T, s.t("what") - 0.3, "c"),
             text("?", X + 1560, 640, 200, PURPLE, s.t("flavor") - 0.2, "c")]
        cv.flow([P(X, 0, x, y) for x, y in ((650, 440), (560, 430), (490, 390), (470, 310), (520, 250), (600, 215), (675, 195))], s.start + 0.3, s.start + s.dur, 2.2, SMELL, 12, 3)
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
