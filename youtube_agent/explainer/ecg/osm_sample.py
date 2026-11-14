"""2-minute SAMPLE video: how smell works (fact-checked 14 Nov 2026). Not queued.

    python3 osm_sample.py [stills]
Env: EP_DIR (default ../sample_smell), OUT_DIR.
"""
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "sample_smell")))
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
PW, PH = 1920, 1080
S = 3
new, done, tube = DG.new, DG.done, DG.tube
OLN = (110, 80, 90, 255)
SKIN = (248, 214, 190, 255)
MUC = (190, 225, 235, 255)
EPI = (250, 210, 90, 255)
LIME = (150, 205, 90, 255)
PINKC = (240, 150, 170, 255)


def mol(d, x, y, r=14, col=(150, 205, 90, 255)):
    d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=col, outline=OLN, width=3 * S)
    for dx in (-5, 5):
        d.ellipse(((x + dx - 3) * S, (y - 4) * S, (x + dx + 3) * S, (y + 2) * S), fill=(255, 255, 255, 255), outline=OLN, width=1 * S)
    for a in (0.6, 2.6, 4.4):
        d.line([(x * S, y * S), ((x + 1.9 * r * math.cos(a)) * S, (y + 1.9 * r * math.sin(a)) * S)], fill=OLN, width=3 * S)



def person_pic():
    W, H = 1000, 900
    im, d = new(W, H)
    SK = (240, 200, 170, 255)
    HAIR = (95, 65, 50, 255)
    d.rounded_rectangle((150 * S, 650 * S, 720 * S, 930 * S), radius=90 * S, fill=(110, 165, 215, 255), outline=OLN, width=6 * S)   # shoulders / shirt
    d.rectangle((370 * S, 520 * S, 490 * S, 690 * S), fill=SK, outline=OLN, width=5 * S)                                           # neck
    d.rectangle((376 * S, 500 * S, 484 * S, 560 * S), fill=SK)
    d.ellipse((220 * S, 130 * S, 600 * S, 540 * S), fill=SK, outline=OLN, width=6 * S)                                              # head (profile)
    d.polygon([(586 * S, 320 * S), (680 * S, 392 * S), (588 * S, 420 * S)], fill=SK, outline=OLN)                                   # nose
    d.line([(586 * S, 322 * S), (680 * S, 392 * S), (588 * S, 420 * S)], fill=OLN, width=5 * S, joint="curve")
    d.chord((200 * S, 100 * S, 600 * S, 400 * S), 175, 345, fill=HAIR, outline=OLN, width=6 * S)                                    # hair
    d.ellipse((205 * S, 190 * S, 400 * S, 470 * S), fill=HAIR, outline=OLN, width=6 * S)                                            # back hair
    d.ellipse((380 * S, 330 * S, 440 * S, 420 * S), fill=(228, 180, 150, 255), outline=OLN, width=5 * S)                            # ear
    d.arc((490 * S, 285 * S, 565 * S, 335 * S), 200, 340, fill=OLN, width=7 * S)                                                    # closed happy eye
    d.line([(488 * S, 270 * S), (565 * S, 262 * S)], fill=HAIR, width=8 * S)                                                        # eyebrow
    d.arc((520 * S, 432 * S, 590 * S, 480 * S), 25, 150, fill=OLN, width=5 * S)                                                     # small calm smile
    d.ellipse((560 * S, 310 * S, 700 * S, 430 * S), outline=(250, 190, 60, 255), width=7 * S)                                       # gold ring on the nose
    d.line([(640 * S, 730 * S), (735 * S, 570 * S)], fill=SK, width=64 * S)                                                         # arm
    d.line([(735 * S, 560 * S), (735 * S, 470 * S)], fill=(110, 160, 90, 255), width=10 * S)                                        # stem
    for a_ in range(0, 360, 72):                                                                                                    # flower
        x, y = 735 + 36 * math.cos(math.radians(a_)), 430 + 36 * math.sin(math.radians(a_))
        d.ellipse(((x - 24) * S, (y - 24) * S, (x + 24) * S, (y + 24) * S), fill=(240, 130, 170, 255), outline=OLN, width=3 * S)
    d.ellipse((718 * S, 413 * S, 752 * S, 447 * S), fill=(250, 210, 80, 255), outline=OLN, width=3 * S)
    d.ellipse((716 * S, 540 * S, 766 * S, 590 * S), fill=SK, outline=OLN, width=4 * S)                                             # hand
    for (x, y, r) in ((630, 205, 12), (672, 150, 19)):                                                                              # thought-bubble trail
        d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=(255, 255, 255, 255), outline=OLN, width=4 * S)
    d.ellipse((700 * S, 10 * S, 990 * S, 190 * S), fill=(255, 250, 235, 255), outline=OLN, width=5 * S)
    d.polygon([(775 * S, 100 * S), (845 * S, 42 * S), (915 * S, 100 * S)], fill=(230, 120, 90, 255), outline=OLN)                   # little house = memory
    d.rectangle((790 * S, 100 * S, 900 * S, 145 * S), fill=(250, 220, 150, 255), outline=OLN, width=3 * S)
    return done(im, W, H)


def head_pic(extra=False):
    W, H = 1000, 640
    im, d = new(W, H)
    d.rounded_rectangle((330 * S, 40 * S, 960 * S, 600 * S), radius=120 * S, fill=SKIN, outline=(170, 110, 90, 255), width=6 * S)           # head
    d.polygon([(330 * S, 300 * S), (200 * S, 400 * S), (330 * S, 430 * S)], fill=SKIN, outline=(170, 110, 90, 255))                          # nose tip
    d.rounded_rectangle((330 * S, 250 * S, 700 * S, 400 * S), radius=60 * S, fill=(255, 235, 230, 255), outline=OLN, width=5 * S)            # nasal cavity
    d.rounded_rectangle((420 * S, 238 * S, 640 * S, 268 * S), radius=14 * S, fill=EPI, outline=OLN, width=4 * S)                            # olfactory epithelium
    d.rounded_rectangle((330 * S, 460 * S, 640 * S, 540 * S), radius=36 * S, fill=(250, 190, 190, 255), outline=OLN, width=5 * S)            # mouth
    for (x, y) in ((250, 380), (300, 340), (400, 310), (500, 290)):
        mol(d, x, y, 15)
    if extra:
        d.ellipse((430 * S, 470 * S, 490 * S, 520 * S), fill=(230, 160, 70, 255), outline=OLN, width=4 * S)
        tube(d, [(470, 460), (520, 380), (520, 300)], (150, 205, 90, 255), 10)
    return done(im, W, H)


def epi_pic():
    W, H = 900, 480
    im, d = new(W, H)
    d.rectangle((0, 40 * S, W * S, 150 * S), fill=MUC, outline=OLN, width=4 * S)                  # mucus
    d.rectangle((0, 380 * S, W * S, 480 * S), fill=EPI, outline=OLN, width=4 * S)                 # tissue
    for x in range(80, 860, 120):
        d.rounded_rectangle(((x - 30) * S, 300 * S, (x + 30) * S, 400 * S), radius=24 * S, fill=PINKC, outline=OLN, width=4 * S)
        for k in range(-1, 2):
            d.line([(x + k * 8) * S, 300 * S, (x + k * 14) * S, 120 * S], fill=(140, 90, 200, 255), width=5 * S)
        d.line([(x * S, 400 * S), (x * S, 480 * S)], fill=(250, 190, 60, 255), width=5 * S)
    mol(d, 200, 90, 14)
    mol(d, 560, 70, 14, (240, 130, 90, 255))
    return done(im, W, H)


def bulb_pic():
    W, H = 900, 560
    im, d = new(W, H)
    d.rectangle((0, 300 * S, W * S, 350 * S), fill=(245, 235, 215, 255), outline=OLN, width=5 * S)            # skull plate
    for x in (250, 380, 510, 640):
        d.rectangle(((x - 14) * S, 300 * S, (x + 14) * S, 350 * S), fill=(255, 255, 255, 255))
        d.line([(x * S, 520 * S), (x * S, 190 * S)], fill=(250, 190, 60, 255), width=6 * S)                  # fibers
    d.ellipse((180 * S, 60 * S, 700 * S, 220 * S), fill=(240, 200, 215, 255), outline=OLN, width=5 * S)       # bulb
    tube(d, [(700, 140), (800, 140), (880, 200)], (240, 210, 100, 255), 22)
    return done(im, W, H)


def limbic_pic():
    W, H = 1000, 560
    im, d = new(W, H)
    d.rounded_rectangle((20 * S, 220 * S, 160 * S, 320 * S), radius=30 * S, fill=EPI, outline=OLN, width=5 * S)       # nose
    d.ellipse((220 * S, 200 * S, 360 * S, 340 * S), fill=(240, 200, 215, 255), outline=OLN, width=5 * S)              # bulb
    d.ellipse((430 * S, 200 * S, 570 * S, 340 * S), fill=(200, 230, 200, 255), outline=OLN, width=5 * S)              # cortex
    tube(d, [(160, 270), (220, 270)], (250, 190, 60, 255), 10)
    tube(d, [(360, 270), (430, 270)], (250, 190, 60, 255), 10)
    d.ellipse((760 * S, 60 * S, 900 * S, 180 * S), fill=(235, 100, 100, 255), outline=OLN, width=5 * S)               # amygdala
    d.ellipse((760 * S, 360 * S, 960 * S, 470 * S), fill=(170, 130, 220, 255), outline=OLN, width=5 * S)              # hippocampus
    tube(d, [(570, 250), (680, 160), (760, 130)], (250, 190, 60, 255), 12)
    tube(d, [(570, 290), (680, 390), (760, 410)], (250, 190, 60, 255), 12)
    d.rounded_rectangle((420 * S, 460 * S, 620 * S, 530 * S), radius=20 * S, fill=(225, 225, 225, 255), outline=(150, 150, 150, 255), width=4 * S)   # thalamus (skipped)
    d.line([(420 * S, 460 * S), (620 * S, 530 * S)], fill=(200, 60, 60, 255), width=8 * S)
    d.line([(420 * S, 530 * S), (620 * S, 460 * S)], fill=(200, 60, 60, 255), width=8 * S)
    return done(im, W, H)


def renew_pic():
    W, H = 900, 420
    im, d = new(W, H)
    d.rectangle((0, 330 * S, W * S, 420 * S), fill=EPI, outline=OLN, width=4 * S)
    d.ellipse((120 * S, 280 * S, 220 * S, 360 * S), fill=(250, 190, 60, 255), outline=OLN, width=5 * S)             # stem cell
    for x, a in ((330, 120), (520, 190), (710, 255)):
        d.rounded_rectangle(((x - 40) * S, (300 - 150 * a / 255) * S, (x + 40) * S, 330 * S), radius=30 * S, fill=(240, 150, 170, a), outline=(110, 80, 90, a), width=4 * S)
        d.line([(x - 130) * S, 300 * S, (x - 60) * S, 300 * S], fill=OLN, width=4 * S)
    return done(im, W, H)


SERV = HERE.parent / "servier"


def man_pic():
    return Image.open(HERE.parent / "art" / "human_board.png").convert("RGBA")


def section_pic(aroma=False):
    """Servier sagittal section + our overlays (smell patch, molecules, aroma path)."""
    im = Image.open(SERV / "swallowing-system.png").convert("RGBA")
    k = 3
    im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((150 * k, 5 * k, 330 * k, 23 * k), radius=9 * k, fill=(250, 200, 60, 255), outline=(110, 80, 90, 255), width=2 * k)
    pts = [(30, 150), (90, 110), (160, 70), (230, 45)] if not aroma else [(300, 330), (420, 280), (430, 170), (380, 90), (290, 45)]
    if aroma:
        d.line([(x * k, y * k) for x, y in pts], fill=(120, 190, 80, 255), width=7 * k, joint="curve")
    for x, y in pts:
        r = 11
        d.ellipse(((x - r) * k, (y - r) * k, (x + r) * k, (y + r) * k), fill=(150, 205, 90, 255), outline=(60, 90, 40, 255), width=2 * k)
    return im


def bulb_art():
    return Image.open(SERV / "Bulbes_olfactifs2.png").convert("RGBA")



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

    s = sc["story"]                                              # HOOK (A): the whole human first (owner's whiteboard picture)
    st = [pop(man_pic(), 960, 540, w=1920, t=0.0, dur=0.3), text("ONE SMELL", 532, 150, 80, GOLD_T, 0.5, "c"), text("20 years back", 1478, 208, 56, PURPLE, s.t("twenty") - 0.4, "c"),
          text("memory + emotion?", 458, 872, 44, RED_T, s.t("memory") - 0.5, "c"), text("follow the smell", 1461, 872, 50, GREEN_T, s.t("follow") - 2.4, "c")]
    end = s.start + s.dur
    cam(end - 2.4, 961, 262, 3.6, 2.2)                           # DIVE into the nose

    s = sc["nose"]                                               # NOSE (B)
    cam(s.start, *Bc, 0.7, 0)
    cam(s.start + 0.05, *Bc, 1.0, 1.1)
    bd.erase(s.start + 0.8, st)
    X = PW
    no = [pop(section_pic(), X + 500, 540, w=900, t=s.start + 0.3), text("MOLECULES in the air", X + 1500, 200, 60, GREEN_T, s.t("molecules") - 0.3, "c"),
          text("breathe in", X + 1500, 340, 66, BLUE_T, s.t("breathe") - 0.3, "c"), text("OLFACTORY EPITHELIUM", X + 1500, 500, 52, GOLD_T, s.t("olfactory") - 0.6, "c"),
          text("dissolve in MUCUS", X + 1500, 680, 60, PURPLE, s.t("dissolve") - 1.2, "c")]
    cam(s.start + s.dur - 1.6, X + 296, 222, 4.0, 1.5)           # DIVE into the olfactory patch

    s = sc["receptors"]                                          # RECEPTORS (C) -- zoom in
    cam(s.start, *C, 0.7, 0)
    cam(s.start + 0.05, *C, 1.0, 1.1)
    bd.erase(s.start + 0.8, no)
    X = 2 * PW
    re = [pop(epi_pic(), X + 520, 540, w=900, t=s.start + 0.3), text("SENSORY NEURONS", X + 1500, 200, 60, PURPLE, s.t("neurons") - 0.5, "c"),
          text("hundreds of receptor kinds", X + 1500, 350, 52, GOLD_T, s.t("hundreds") - 0.4, "c"), text("molecule fits = SIGNAL", X + 1500, 520, 58, RED_T, s.t("fits") - 0.5, "c"),
          text("a different route?", X + 1500, 760, 76, PURPLE, s.t("strange") - 0.6, "c")]

    s = sc["bulb"]                                               # BULB (D)
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, re)
    bu = [pop(bulb_art(), 520, Y + 540, w=940, t=s.start + 0.3), text("holes in the skull", 1450, Y + 220, 58, MAROON, s.t("holes") - 0.4, "c"),
          text("OLFACTORY BULB", 1450, Y + 400, 66, RED_T, s.t("bulb") - 0.1, "c"), text("then CORTEX", 1450, Y + 600, 60, GREEN_T, s.t("cortex") - 1.4, "c")]

    s = sc["brain"]                                              # BRAIN (E) -- the payoff
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, bu)
    X = PW
    br = [pop(limbic_pic(), X + 520, Y + 480, w=1000, t=s.start + 0.3), text("AMYGDALA = emotion", X + 1500, Y + 160, 50, RED_T, s.t("amygdala") - 0.4, "c"),
          text("HIPPOCAMPUS = memory", X + 1500, Y + 700, 50, PURPLE, s.t("hippocampus") - 0.4, "c"), text("THALAMUS: skipped", X + 560, Y + 820, 52, MAROON, s.t("skips") - 0.9, "c"),
          text("memory back FAST", X + 1500, Y + 400, 70, GOLD_T, s.t("fast") - 0.8, "c")]

    s = sc["renew"]                                              # RENEW (F)
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, br)
    X = 2 * PW
    rn = [pop(renew_pic(), X + 520, Y + 480, w=900, t=s.start + 0.3), text("STEM CELLS replace them", X + 1450, Y + 260, 56, GREEN_T, s.t("stem") - 0.4, "c"),
          text("weeks to months", X + 1450, Y + 440, 70, GOLD_T, s.t("weeks") - 0.4, "c"), text("unusual for nerve cells", X + 1450, Y + 620, 52, MAROON, s.t("unusual") - 1.2, "c")]

    s = sc["taste"]                                              # TASTE (A)
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, rn)
    ta = [pop(section_pic(True), 500, 540, w=900, t=s.start + 0.3), text("chewing -> AROMA rises", 1450, 220, 56, GREEN_T, s.t("aroma") - 0.5, "c"),
          text("nose blocked = BLAND", 1450, 420, 62, RED_T, s.t("bland") - 0.4, "c"), text("taste buds still work", 1450, 600, 54, MAROON, s.t("buds") - 0.4, "c")]

    s = sc["care"]                                               # CARE (B)
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, ta)
    X = PW
    ca = [text("SUDDEN loss of smell?", X + 960, 280, 84, RED_T, s.t("suddenly") - 0.3, "c"), text("or not back in 1-2 weeks", X + 960, 450, 66, MAROON, s.t("week") - 0.8, "c"),
          panel(X + 560, 620, X + 1360, 780, (215, 240, 215), s.t("doctor") - 1.4), text("see a doctor", X + 960, 700, 70, GREEN_T, s.t("doctor") - 1.2, "c")]

    s = sc["recap"]                                              # RECAP (C)
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ca)
    X = 2 * PW
    rp = title("remember it like this", X + 960, 100, s.start + 0.4)
    for w, a, b, col, tc_, x in (("molecules", "molecules dissolve", "in mucus", (230, 245, 220), GREEN_T, 400), ("receptors", "receptors fire", "a signal", (255, 240, 215), GOLD_T, 960), ("bulb", "bulb -> emotion", "and memory", (240, 225, 250), PURPLE, 1520)):
        tw2 = s.t(w) - 0.3
        rp += [panel(X + x - 265, 220, X + x + 265, 600, col, tw2 - 0.2), text(a, X + x, 360, 38, tc_, tw2, "c"), text(b, X + x, 470, 34, MAROON, tw2 + 0.6, "c")]
    tn = s.t("taste") - 0.8
    rp += [panel(X + 200, 720, X + 1720, 890, (240, 225, 250), tn - 0.3), text("next: TASTE", X + 960, 820, 64, PURPLE, tn, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"smell_{v.id}.png")
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "smell", intro=True)
        f.replace(OUT / "sample_smell_2min.mp4")
        print("done ->", OUT / "sample_smell_2min.mp4")
