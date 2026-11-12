"""Nervous system series: The Autonomic Nervous System (owner-approved 12 Nov 2026) + 2 story Shorts.

    python3 osm_auto.py [stills]            # full video -> final_auto.mp4
    python3 osm_auto.py short 1|2 [stills]  # story Short -> auto_short1.mp4 / auto_short2.mp4
Env: EP_DIR (default ../autonomic), OUT_DIR.
"""
import math
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "autonomic")))
OUT = Path(os.environ.get("OUT_DIR", str(HERE)))
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
SHORT_TITLES = {1: "The Hidden Brake", 2: "The Bang"}
SHORT_Q = {1: "So who is holding the brake?", 2: "So which team just won?"}
S = 3


# ----------------------------------------------------------------------------- pictures
def eye_pic(dilated=False):
    W, H = 420, 260
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((10 * S, 40 * S, 410 * S, 220 * S), fill=(255, 255, 255), outline=(120, 90, 90), width=6 * S)
    d.ellipse((120 * S, 30 * S, 300 * S, 230 * S), fill=(120, 170, 220), outline=(70, 110, 160), width=5 * S)
    r = 62 if dilated else 24
    d.ellipse((210 * S - r * S, 130 * S - r * S, 210 * S + r * S, 130 * S + r * S), fill=(40, 30, 50))
    d.ellipse((235 * S, 100 * S, 255 * S, 120 * S), fill=(255, 255, 255))
    return im.resize((W, H), Image.LANCZOS)


def stomach_pic(active=False):
    W, H = 300, 300
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = (245, 190, 150) if active else (240, 215, 200)
    pts = [(120, 30), (170, 30), (190, 80), (250, 130), (265, 200), (215, 265), (140, 270), (90, 225), (95, 140), (110, 85)]
    d.polygon([(x * S, y * S) for x, y in pts], fill=col, outline=(170, 110, 90))
    d.line([(x * S, y * S) for x, y in pts + [pts[0]]], fill=(170, 110, 90), width=5 * S, joint="curve")
    return im.resize((W, H), Image.LANCZOS)


def sleeper_pic():
    W, H = 900, 520
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20 * S, 300 * S, 880 * S, 470 * S), radius=40 * S, fill=(190, 205, 240), outline=(110, 120, 170), width=5 * S)
    d.rounded_rectangle((40 * S, 230 * S, 220 * S, 330 * S), radius=40 * S, fill=(255, 255, 255), outline=(150, 160, 200), width=5 * S)   # pillow
    d.ellipse((90 * S, 200 * S, 230 * S, 320 * S), fill=(248, 214, 190), outline=(170, 110, 90), width=5 * S)    # head
    d.arc((120 * S, 250 * S, 150 * S, 270 * S), 200, 340, fill=(120, 80, 70), width=4 * S)   # closed eye
    d.rounded_rectangle((200 * S, 240 * S, 860 * S, 400 * S), radius=70 * S, fill=(170, 195, 235), outline=(110, 120, 170), width=5 * S)   # blanket
    m = Image.new("L", im.size, 0); md = ImageDraw.Draw(m)
    md.ellipse((690 * S, 20 * S, 840 * S, 170 * S), fill=255); md.ellipse((725 * S, 10 * S, 880 * S, 160 * S), fill=0)
    im.paste((250, 225, 120, 255), (0, 0), m)   # crescent moon
    return im.resize((W, H), Image.LANCZOS)


def drop_pic():
    W, H = 240, 300
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(120 * S, 20 * S), (200 * S, 170 * S), (40 * S, 170 * S)], fill=(150, 205, 240), outline=(70, 130, 190))
    d.ellipse((40 * S, 110 * S, 200 * S, 270 * S), fill=(150, 205, 240), outline=(70, 130, 190), width=5 * S)
    d.polygon([(120 * S, 28 * S), (194 * S, 168 * S), (46 * S, 168 * S)], fill=(150, 205, 240))
    return im.resize((W, H), Image.LANCZOS)


def pedals_pic():
    W, H = 760, 520
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((60 * S, 60 * S, 300 * S, 460 * S), radius=40 * S, fill=(245, 150, 140), outline=(170, 70, 70), width=6 * S)   # brake (left, wide)
    d.rounded_rectangle((430 * S, 120 * S, 690 * S, 460 * S), radius=40 * S, fill=(160, 215, 165), outline=(70, 130, 80), width=6 * S)   # gas
    for x0, x1 in ((90, 270), (460, 660)):
        for y in range(100, 440, 40):
            d.line([(x0 * S, y * S), (x1 * S, y * S)], fill=(255, 255, 255), width=4 * S)
    return im.resize((W, H), Image.LANCZOS)


def chain_pic():
    W, H = 1500, 460
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10 * S, 130 * S, 250 * S, 330 * S), radius=40 * S, fill=LILAC, outline=(120, 90, 160), width=6 * S)          # brain / cord
    d.ellipse((520 * S, 150 * S, 690 * S, 310 * S), fill=GOLD_T and (250, 225, 150), outline=(190, 150, 60), width=6 * S)             # ganglion
    d.line([(250 * S, 230 * S), (520 * S, 230 * S)], fill=(60, 90, 200), width=12 * S)                                               # neuron 1
    d.line([(690 * S, 230 * S), (1180 * S, 230 * S)], fill=(220, 90, 70), width=12 * S)                                              # neuron 2
    for x in (250, 520, 690):
        d.ellipse(((x - 16) * S, 214 * S, (x + 16) * S, 246 * S), fill=(255, 255, 255), outline=(80, 80, 90), width=4 * S)
    d.ellipse((1180 * S, 150 * S, 1340 * S, 310 * S), fill=(245, 170, 170), outline=(170, 70, 80), width=6 * S)                       # organ
    return im.resize((W, H), Image.LANCZOS)


def person_pic(low=False):
    im = sv("Male-silhouette")
    return im


# ----------------------------------------------------------------------------- scenes
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
    heart = sv("coeur_09")
    lungs = sv("poumons_01")
    brain = OB.brain_img()

    # ---------------- STORY (A)
    s = sc["story"]
    bed = pop(sleeper_pic(), 560, 560, w=900, t=0.3)
    ht = pop(heart, 1450, 330, h=260, t=s.t("heart") - 0.4)
    stm = pop(stomach_pic(), 1450, 700, h=240, t=s.t("stomach") - 0.5)
    st = [bed, text("zzz", 760, 250, 90, PURPLE, s.start + 0.6, "c"), ht, text("beating", 1700, 330, 54, RED_T, s.t("heart") - 0.3, "l"), stm,
          text("digesting", 1700, 700, 54, GOLD_T, s.t("stomach") - 1.2, "l"), text("WHO is running the show?", 700, 900, 84, GOLD_T, s.t("who") - 0.3, "c")]

    # ---------------- OVERVIEW (B)
    s = sc["overview"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, st)
    X = PW
    ov = [text("AUTONOMIC = AUTOMATIC", X + 960, 130, 92, PURPLE, s.t("autonomic") - 0.2, "c"),
          pop(heart, X + 300, 520, h=260, t=s.t("heart") - 0.3), text("heart", X + 300, 700, 56, RED_T, s.t("heart"), "c"),
          pop(stomach_pic(), X + 760, 520, h=240, t=s.t("gut") - 0.9), text("gut", X + 760, 700, 56, GOLD_T, s.t("gut") - 0.6, "c"),
          pop(lungs, X + 1220, 520, h=260, t=s.t("airways") - 0.9), text("airways", X + 1220, 700, 56, BLUE_T, s.t("airways") - 0.6, "c"),
          pop(drop_pic(), X + 1650, 520, h=230, t=s.t("glands") - 0.6), text("glands", X + 1650, 640, 56, GREEN_T, s.t("glands") - 0.3, "c"),
          text("you never have to think about them", X + 960, 900, 62, MAROON, s.t("airways") - 0.3, "c")]

    # ---------------- TWO TEAMS (C)
    s = sc["two"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ov)
    X = 2 * PW
    ts, tp = s.t("sympathetic"), s.t("parasympathetic") - 0.2
    tw = [panel(X + 120, 200, X + 900, 800, PINK, ts - 0.4), text("SYMPATHETIC", X + 510, 420, 80, RED_T, ts, "c"), text("team 1", X + 510, 330, 50, MAROON, ts - 0.2, "c"),
          panel(X + 1020, 200, X + 1800, 800, SKY, tp - 0.4), text("PARASYMPATHETIC", X + 1410, 420, 70, BLUE_T, tp, "c"), text("team 2", X + 1410, 330, 50, MAROON, tp - 0.2, "c"),
          text("opposite jobs", X + 960, 930, 80, GOLD_T, s.t("opposite"), "c")]

    # ---------------- SYMPATHETIC (D)
    s = sc["sympathetic"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, tw)
    Y = PH
    sy = title("FIGHT or FLIGHT", 960, Y + 110, s.start + 0.3) + [
          pop(heart, 330, Y + 440, h=240, t=s.t("faster") - 0.9), text("heart FASTER", 330, Y + 640, 56, RED_T, s.t("faster") - 0.6, "c"),
          pop(eye_pic(True), 800, Y + 440, w=300, t=s.t("widen") - 0.9), text("pupils WIDEN", 800, Y + 600, 56, PURPLE, s.t("widen") - 0.6, "c"),
          pop(lungs, 1270, Y + 440, h=240, t=s.t("open") - 0.9), text("airways OPEN", 1270, Y + 640, 56, BLUE_T, s.t("open") - 0.6, "c"),
          pop(stomach_pic(), 1700, Y + 440, h=220, t=s.t("digestion") - 0.9), text("digestion SLOWS", 1700, Y + 640, 54, GOLD_T, s.t("digestion") - 0.6, "c"),
          text("when you are scared or excited", 960, Y + 900, 62, MAROON, s.t("scared") - 0.2, "c")]

    # ---------------- PARASYMPATHETIC (E)
    s = sc["parasympathetic"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, sy)
    X = PW
    pa = title("REST and DIGEST", X + 960, Y + 110, s.start + 0.3) + [
          pop(heart, X + 330, Y + 440, h=240, t=s.t("slows") - 0.9), text("heart SLOWER", X + 330, Y + 640, 56, RED_T, s.t("slows") - 0.6, "c"),
          pop(eye_pic(False), X + 800, Y + 440, w=300, t=s.t("narrows") - 0.9), text("pupils NARROW", X + 800, Y + 600, 56, PURPLE, s.t("narrows") - 0.6, "c"),
          pop(stomach_pic(True), X + 1270, Y + 440, h=240, t=s.t("wakes") - 0.9), text("digestion WAKES", X + 1270, Y + 640, 54, GOLD_T, s.t("wakes") - 0.6, "c"),
          text("calm down", X + 1700, Y + 440, 70, GREEN_T, s.t("calm") - 0.6, "c"), text("save energy", X + 1700, Y + 540, 70, GREEN_T, s.t("energy") - 0.6, "c"),
          text("the body relaxes", X + 960, Y + 900, 62, MAROON, s.t("helps") - 0.2, "c")]

    # ---------------- BALANCE (F)
    s = sc["balance"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, pa)
    X = 2 * PW
    ba = [pop(pedals_pic(), X + 560, Y + 560, w=900, t=s.start + 0.4),
          text("BRAKE", X + 300, Y + 880, 80, RED_T, s.t("brake") - 0.2, "c"), text("parasympathetic", X + 300, Y + 960, 44, MAROON, s.t("brake") + 0.3, "c"),
          text("GAS", X + 810, Y + 880, 80, GREEN_T, s.t("gas") - 0.2, "c"), text("sympathetic", X + 810, Y + 960, 44, MAROON, s.t("gas") + 0.3, "c"),
          text("both work together", X + 1500, Y + 400, 66, PURPLE, s.t("both") - 0.2, "c"), text("balanced second by second", X + 1500, Y + 520, 56, GOLD_T, s.t("balances") - 1.0, "c")]

    # ---------------- VAGUS (A)
    s = sc["vagus"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, ba)
    br = pop(brain, 420, 200, h=280, t=s.start + 0.3)
    hh = pop(heart, 420, 760, h=300, t=s.t("heart") - 0.5)
    lg = pop(lungs, 900, 640, h=220, t=s.t("lungs") - 1.0)
    gu = pop(stomach_pic(), 160, 640, h=200, t=s.t("gut") - 1.0)
    vg = [br, hh, lg, gu, lead([(420, 340), (430, 520), (420, 620)], s.t("vagus") - 0.2, BLUE_T, 10, 0.9, arrow=True),
          lead([(520, 280), (800, 500), (900, 540)], s.t("lungs") - 0.7, BLUE_T, 8, 0.8, arrow=True), lead([(330, 280), (200, 460), (160, 540)], s.t("gut") - 0.7, BLUE_T, 8, 0.8, arrow=True),
          text("the VAGUS nerve", 1400, 150, 76, BLUE_T, s.t("vagus") - 0.2, "c"), text("a surprise!", 1400, 260, 62, RED_T, s.t("surprise") - 0.2, "c"),
          text("own pacemaker: ~100 / min", 1400, 480, 62, GOLD_T, s.t("hundred") - 0.8, "c"), text("yours: slower", 1400, 590, 70, GREEN_T, s.t("slower") - 0.3, "c"),
          text("the vagus holds the brake", 1500, 800, 56, RED_T, s.t("brake") - 0.3, "c")]

    # ---------------- CHAIN (B)
    s = sc["chain"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, vg)
    X = PW
    ch = [pop(chain_pic(), X + 960, 380, w=1500, t=s.start + 0.3), text("brain / cord", X + 270, 250, 46, PURPLE, s.start + 0.8, "c"),
          text("neuron 1", X + 540, 520, 54, BLUE_T, s.t("first") - 0.2, "c"), text("GANGLION", X + 960, 520, 54, GOLD_T, s.t("ganglion") - 0.3, "c"),
          text("neuron 2", X + 1400, 520, 54, RED_T, s.t("second") - 0.4, "c"), text("organ", X + 1630, 250, 46, MAROON, s.t("organ") - 0.4, "c"),
          panel(X + 160, 650, X + 940, 900, SKY, s.t("parasympathetic") - 1.0), text("PARASYMPATHETIC", X + 550, 730, 56, BLUE_T, s.t("parasympathetic") - 0.8, "c"), text("acetylcholine", X + 550, 830, 64, MAROON, s.t("acetylcholine") - 0.2, "c"),
          panel(X + 980, 650, X + 1760, 900, PINK, s.t("sympathetic") - 0.8), text("SYMPATHETIC", X + 1370, 730, 56, RED_T, s.t("sympathetic") - 0.6, "c"), text("norepinephrine", X + 1370, 830, 64, MAROON, s.t("norepinephrine") - 0.5, "c")]

    # ---------------- PAYOFF (C)
    s = sc["payoff"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ch)
    X = 2 * PW
    pf = [pop(sleeper_pic(), X + 480, 520, w=800, t=s.start + 0.3), pop(heart, X + 480, 800, h=200, t=s.start + 0.5), text("brake ON", X + 800, 800, 70, GREEN_T, s.t("brake") - 0.3, "l"),
          text("BANG!", X + 1450, 200, 130, RED_T, s.t("noise") - 0.2, "c"), text("gas pedal!", X + 1450, 420, 84, GREEN_T, s.t("gas") - 0.3, "c"),
          pop(eye_pic(True), X + 1450, 620, w=300, t=s.t("second") - 0.6), text("heart POUNDS", X + 1450, 800, 70, RED_T, s.t("pounds") - 0.4, "c")]

    # ---------------- FAINT (D)
    s = sc["faint"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, pf)
    Y = PH
    fa = [pop(sv("Male-silhouette"), 460, Y + 540, h=900, t=s.start + 0.3), text("standing up too fast", 1330, Y + 160, 62, MAROON, s.t("standing") - 0.2, "c"),
          text("brake pulls TOO hard", 1330, Y + 300, 70, RED_T, s.t("brake") - 0.2, "c"), text("heart slows", 1330, Y + 440, 62, GOLD_T, s.t("slows") - 0.2, "c"),
          text("blood pressure drops", 1330, Y + 570, 62, BLUE_T, s.t("drops") - 0.6, "c"), text("brain gets less blood", 1330, Y + 700, 60, PURPLE, s.t("less") - 0.6, "c"),
          panel(980, Y + 800, 1700, Y + 960, MINT, s.t("doctor") - 1.0), text("often? see a doctor", 1340, Y + 900, 60, GREEN_T, s.t("doctor") - 0.7, "c")]

    # ---------------- RECAP (E)
    s = sc["recap"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, fa)
    X = PW
    rp = title("remember 3 things", X + 960, Y + 100, s.start + 0.4)
    for w, a, b, col, tc_, x in (("automatically", "runs your body", "automatically", PINK, RED_T, 400), ("gas", "gas = sympathetic", "brake = parasympathetic", CREAM, GOLD_T, 960), ("vagus", "the vagus nerve", "brakes your heart", SKY, BLUE_T, 1520)):
        tw2 = s.t(w) - 0.3
        rp += [panel(X + x - 265, Y + 220, X + x + 265, Y + 600, col, tw2 - 0.2), text(a, X + x, Y + 360, 46, tc_, tw2, "c"), text(b, X + x, Y + 470, 44, MAROON, tw2 + 0.6, "c")]
    tn = s.t("endocrine") - 0.8
    rp += [panel(X + 200, Y + 720, X + 1720, Y + 890, LILAC, tn - 0.3), text("next: the endocrine system", X + 960, Y + 820, 56, PURPLE, tn, "c")]

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
    heart = sv("coeur_09")
    if n == 1:
        s = sc["case"]
        a = [pop(sleeper_pic(), 560, 600, w=900, t=0.3), text("zzz", 760, 260, 90, PURPLE, 0.6, "c"), pop(heart, 1450, 400, h=300, t=s.t("heart") - 0.4),
             text("beating", 1700, 400, 56, RED_T, s.t("beating"), "l"), text("pacemaker wants ~100 / min", 1260, 800, 62, GOLD_T, s.t("hundred") - 0.8, "c")]
        s = sc["turn"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(heart, X + 520, 520, h=420, t=s.start + 0.3), text("100", X + 1350, 260, 200, GOLD_T, s.start + 0.5, "c"), text("yours: much slower", X + 1350, 520, 70, GREEN_T, s.t("slower") - 0.3, "c"),
             text("something holds it back", X + 1350, 680, 62, MAROON, s.t("holding") - 0.5, "c"), text("?", X + 1350, 900, 220, GOLD_T, s.t("what") - 0.4, "c")]
    else:
        s = sc["case"]
        a = [text("BANG!", 520, 260, 200, RED_T, s.t("bang") - 0.4, "c"), pop(heart, 520, 700, h=360, t=s.t("heart") - 0.5), text("heart POUNDS", 520, 930, 60, RED_T, s.t("pounds") - 0.2, "c"),
             pop(eye_pic(True), 1400, 420, w=500, t=s.t("pupils") - 0.5), text("pupils WIDEN", 1400, 640, 66, PURPLE, s.t("widen") - 0.3, "c"),
             text("you did not decide", 1400, 850, 60, MAROON, s.t("decide") - 0.3, "c")]
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [text("a hidden system", X + 960, 200, 100, PURPLE, s.t("hidden") - 0.2, "c"), panel(X + 260, 380, X + 900, 780, PINK, s.t("two") - 0.6), text("TEAM 1", X + 580, 580, 100, RED_T, s.t("two") - 0.3, "c"),
             panel(X + 1020, 380, X + 1660, 780, SKY, s.t("two") - 0.2), text("TEAM 2", X + 1340, 580, 100, BLUE_T, s.t("two") + 0.1, "c"), text("took over in under a second", X + 960, 920, 66, GOLD_T, s.t("second") - 0.8, "c")]
        s = sc["clue"]
        cam(s.start, *C, 1.0, 1.0)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        c = [pop(pedals_pic(), X + 560, 540, w=900, t=s.start + 0.3), text("GAS", X + 810, 880, 90, GREEN_T, s.t("gas") - 0.3, "c"), text("BRAKE", X + 300, 880, 90, RED_T, s.t("brake") - 0.3, "c"),
             text("which one", X + 1500, 360, 80, MAROON, s.t("which") - 0.3, "c"), text("just won?", X + 1500, 480, 100, GOLD_T, s.t("won") - 0.4, "c")]

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
    board = NU.render_board(bd, sc, f"auto_story{n}")
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
    ov = OUT / f"auto_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"auto_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["autonomic"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "autonomic", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"auto_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"ashort{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "auto", intro=True)
        f.replace(OUT / "final_auto.mp4")
        print("done ->", OUT / "final_auto.mp4")
