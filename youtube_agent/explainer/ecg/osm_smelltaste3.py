"""SMELL & TASTE v3 - smooth single-page cinematic build (cross-fades, location-first push-ins, labelled pointers).
Owner images art/smelltaste/shot1-6. Same fact-checked script ../smelltaste.

    python3 osm_smelltaste3.py [stills] | short 1|2 [stills]
"""
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "smelltaste")))
OUT = Path(os.environ.get("OUT_DIR", str(HERE)))
ART = HERE.parent / "art" / "smelltaste"
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_hanat as HA  # noqa: E402
import osm_brain as OB  # noqa: E402
import osm_neuron as NU  # noqa: E402
from osm_ear2 import Cine, P as P0  # noqa: E402
from osm_cell import Stage, LX  # noqa: E402  (also switches the Servier credit line off)

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
PINK, LILAC, CREAM, MINT = OB.PINK, OB.LILAC, OB.CREAM, OB.MINT
CR = 26
SMELL, SIG, TASTE, BUD = (110, 180, 90), (240, 180, 40), (220, 90, 120), (200, 150, 60)
TASTES = (("SWEET", (220, 90, 140)), ("SALTY", (70, 130, 210)), ("SOUR", (190, 150, 20)), ("BITTER", (90, 140, 60)), ("UMAMI", (180, 100, 50)))
SHORT_TITLES = {1: "Is The Tongue Map Real", 2: "Why Food Tastes Bland"}
SHORT_Q = {1: "So how many basic tastes are there?", 2: "So what is missing when food tastes bland?"}


def shot(n):
    im = Image.open(ART / f"shot{n}.jpg").convert("RGBA")
    return im.crop((CR, CR, 1376 - CR, 768 - CR)).resize((1376, 768), Image.LANCZOS)


def P(x, y, n=2):
    return P0(0, 0, (x - CR) * 1376 / (1376 - 2 * CR), (y - CR) * 768 / (768 - 2 * CR))


def load(d):
    return NU.load(d)


def build():
    sc, t0 = load(EP)
    bd = B.Board(1, 1)
    pops = []
    kit = HA.kit(bd, pops)
    cv = Cine(bd)
    g = Stage(bd, kit, cv)
    bd.camera(0, 960, 540, 1.0, 0.1)

    # ---------------- STORY: the owner's person pinching the nose -> dive into the nose
    s = sc["story"]
    g.picture(shot(1), 0.0, 0.4)
    g.label("PINCH your nose", P(560, 300, 1), 200, s.t("pinch") - 0.3, RED_T, 50)
    g.label("+ a STRAWBERRY", P(600, 385, 1), 330, s.t("strawberry") - 0.3, TASTE, 46)
    g.say("still SWEET...", LX, 490, 54, GOLD_T, s.t("sweet") - 0.4)
    g.say("but the FLAVOR? gone!", LX, 590, 44, PURPLE, s.t("disappears") - 0.6)
    g.say("flavor = 2 senses", LX, 740, 52, GREEN_T, s.t("teamwork") - 0.5)
    g.say("follow a bite", LX, 860, 50, MAROON, s.t("follow") - 1.4)
    g.clear(s.start + s.dur - 2.1)
    g.focus(s.start + s.dur, P(545, 300, 1), 2.6, 2.1)

    # ---------------- NOSE
    s = sc["nose"]
    g.picture(shot(2), s.start - 0.6)
    g.say("SMELL = tiny molecules", LX, 110, 40, SMELL, s.t("molecules") - 0.3)
    g.label("NOSTRIL", P(770, 372), 240, s.t("travel") - 0.3, BLUE_T, 48)
    g.label("NASAL CAVITY", P(600, 300), 370, s.t("nasal") - 0.3, MAROON, 46)
    g.label("OLFACTORY EPITHELIUM", P(675, 195), 500, s.t("olfactory") - 0.6, GOLD_T, 38)
    g.say("(the smell patch)", LX, 570, 36, GOLD_T, s.t("olfactory"))
    g.say("dissolve in MUCUS", LX, 720, 50, PURPLE, s.t("dissolve") - 0.8)
    cv.flow([P(x, y) for x, y in ((900, 400), (800, 375), (730, 330), (700, 270), (680, 205))], s.t("travel") - 0.3, s.start + s.dur, 2.6, SMELL, 13, 4)
    g.drift(s, 1.2, 1.9)
    g.clear(s.start + s.dur - 1.7)
    g.focus(s.start + s.dur, P(675, 195), 1.6, 1.7)

    # ---------------- RECEPTORS
    s = sc["receptors"]
    g.picture(shot(3), s.start - 0.6)
    g.label("SMELL RECEPTOR NEURONS", P(420, 545, 3), 200, s.t("neurons") - 0.4, PURPLE, 36)
    g.label("CILIA in the mucus", P(385, 632, 3), 330, s.t("receptors") - 0.2, (60, 150, 160), 40)
    g.label("ODOR MOLECULE", P(320, 690, 3), 460, s.t("molecule") - 0.4, SMELL, 42)
    g.say("HUNDREDS of receptor kinds", LX, 600, 34, GOLD_T, s.t("hundreds") - 0.4)
    g.say("molecule fits = SIGNAL", LX, 700, 44, RED_T, s.t("fits") - 0.5)
    g.say("a different route...", LX, 840, 48, PURPLE, s.t("strange") - 0.6)
    for i, x in enumerate((300, 340, 380, 420, 465, 505, 545)):
        cv.glow(s.t("fires") - 0.3 + 0.1 * i, P(x, 560, 3), 1.6, 30, SIG)
        cv.flow([P(x, 620, 3), P(x, 520, 3), P(x + (420 - x) * 0.4, 380, 3), P(420 + (x - 420) * 0.5, 230, 3)], s.t("fires") - 0.2 + 0.12 * i, s.start + s.dur, 1.6, SIG, 9, 1)
    cv.flow([P(x, 690, 3) for x in (240, 330, 420)], s.start + 0.6, s.t("fits"), 2.0, SMELL, 10, 2)
    g.drift(s)
    g.clear(s.start + s.dur - 1.0)

    # ---------------- BRAIN: skull holes -> bulb, then dissolve to the brain (emotion + memory)
    s = sc["brain"]
    g.label("tiny HOLES in the skull", P(430, 320, 3), 260, s.t("holes") - 0.4, MAROON, 40)
    g.label("OLFACTORY BULB", P(420, 170, 3), 400, s.t("bulb") - 0.2, RED_T, 46)
    for i, x in enumerate((370, 420, 470)):
        cv.flow([P(x, 520, 3), P(x, 330, 3), P(420 + (x - 420) * 1.6, 170, 3)], s.start + 0.6 + 0.2 * i, s.t("from") + 0.6, 1.5, SIG, 10, 1)
    tm = s.t("from") - 0.3
    g.clear(tm - 0.5)
    g.focus(tm + 0.2, P(420, 170, 3), 1.4, 1.4)
    g.picture(shot(4), tm)
    g.label("OLFACTORY BULB", P(275, 410, 4), 180, tm + 0.6, SMELL, 44)
    g.label("AMYGDALA = emotion", P(445, 445, 4), 320, s.t("amygdala") - 0.4, RED_T, 42)
    g.label("HIPPOCAMPUS = memory", P(560, 410, 4), 460, s.t("hippocampus") - 0.4, PURPLE, 38)
    g.say("smell SKIPS the thalamus", LX, 640, 36, MAROON, s.t("skips") - 0.9)
    g.say("memory back FAST", LX, 780, 54, GOLD_T, s.t("fast") - 0.9)
    cv.flow([P(x, y, 4) for x, y in ((275, 410), (360, 400), (445, 440))], tm + 0.8, s.start + s.dur, 1.6, SIG, 11, 2)
    cv.flow([P(x, y, 4) for x, y in ((275, 410), (380, 380), (480, 380), (560, 410))], tm + 1.0, s.start + s.dur, 1.9, SIG, 11, 2)
    g.clear(s.start + s.dur - 1.0)

    # ---------------- TONGUE
    s = sc["tongue"]
    g.picture(shot(5), s.start - 0.6)
    g.say("now: TASTE", LX, 120, 60, RED_T, s.t("taste") - 0.3)
    g.label("PAPILLAE (small bumps)", P(330, 420, 5), 270, s.t("papillae") - 0.3, PURPLE, 38)
    g.label("large papillae (V-row)", P(460, 250, 5), 400, s.t("papillae") + 0.5, MAROON, 36)
    g.say("THOUSANDS of taste buds", LX, 560, 38, GOLD_T, s.t("thousands") - 0.5)
    g.say("50-150 receptor cells", LX, 680, 42, MAROON, s.t("fifty") - 0.6)
    g.say("in EACH bud", LX, 760, 42, MAROON, s.t("fifty") - 0.1)
    cv.glow(s.t("tongue") - 0.2, P(460, 430, 5), 2.4, 220, TASTE)
    for i, (x, y) in enumerate(((300, 180), (380, 215), (460, 250), (540, 215), (620, 180))):
        cv.glow(s.t("papillae") + 0.4 + 0.12 * i, P(x, y, 5), 2.0, 34, BUD)
    g.drift(s, 1.2, 1.8)
    g.clear(s.start + s.dur - 1.6)
    g.focus(s.start + s.dur, P(460, 250, 5), 1.6, 1.6)

    # ---------------- FIVE tastes: inside one taste bud
    s = sc["five"]
    g.picture(shot(6), s.start - 0.6)
    g.label("TASTE PORE", P(440, 130, 6), 130, s.start + 0.6, BLUE_T, 44)
    g.label("TASTE RECEPTOR CELLS", P(420, 380, 6), 250, s.t("cells") - 0.2, PURPLE, 34)
    for i, (w, c) in enumerate(TASTES):
        g.say(w, LX + (i % 2) * 280, 400 + (i // 2) * 90, 46, c, s.t(w.lower()) - 0.2)
        cv.glow(s.t(w.lower()) - 0.2, P(360 + 40 * i, 380, 6), 1.4, 45, c)
    g.say("NO tongue map!", LX, 760, 54, RED_T, s.t("myth") - 0.2)
    g.say("every taste, all over", LX, 860, 40, GREEN_T, s.t("spread") - 0.9)
    g.drift(s)
    g.clear(s.start + s.dur - 1.0)

    # ---------------- NERVES
    s = sc["nerves"]
    g.picture(shot(4), s.start - 0.6)
    g.say("3 CRANIAL NERVES:", LX, 110, 46, GOLD_T, s.t("three") - 0.3)
    g.say("facial", LX, 200, 46, RED_T, s.t("facial") - 0.2)
    g.say("glossopharyngeal", LX, 280, 40, PURPLE, s.t("glossopharyngeal") - 0.2)
    g.say("vagus", LX, 360, 46, BLUE_T, s.t("vagus") - 0.2)
    g.label("BRAINSTEM", P(605, 620, 4), 490, s.t("facial") + 0.3, MAROON, 44)
    g.label("THALAMUS first", P(540, 340, 4), 620, s.t("thalamus") - 0.4, GOLD_T, 44)
    g.label("TASTE AREA (cortex)", P(470, 320, 4), 760, s.t("area") - 1.4, GREEN_T, 38)
    for i, col in enumerate(((220, 80, 80), (140, 100, 210), (60, 140, 220))):
        x0 = 590 + 20 * i
        cv.flow([P(x0, 700, 4), P(x0 + 5, 600, 4), P(580, 470, 4), P(545, 350, 4)], (s.t("facial"), s.t("glossopharyngeal"), s.t("vagus"))[i] - 0.2,
                s.start + s.dur, 2.0, col, 11, 2)
    g.drift(s)
    g.clear(s.start + s.dur - 1.0)

    # ---------------- RENEW
    s = sc["renew"]
    g.picture(shot(6), s.start - 0.6)
    g.say("something RARE", LX, 140, 54, PURPLE, s.t("rare") - 0.3)
    g.say("taste + smell cells", LX, 270, 44, MAROON, s.t("taste") - 0.3)
    g.say("are REPLACED", LX, 360, 54, GREEN_T, s.t("replaced") - 0.3)
    g.label("new cells grow from the base", P(440, 560, 6), 520, s.t("replaced") + 0.6, GREEN_T, 30)
    g.say("taste cells: ~ every 10 days", LX, 700, 34, GOLD_T, s.t("ten") - 1.6)
    cv.flow([P(440, 600, 6), P(440, 480, 6), P(440, 330, 6)], s.t("replaced"), s.start + s.dur, 2.2, (110, 190, 110), 12, 2)
    g.drift(s, 0.8, 0.8)
    g.clear(s.start + s.dur - 1.0)

    # ---------------- FLAVOR
    s = sc["flavor"]
    g.picture(shot(2), s.start - 0.6)
    g.say("FLAVOR = ?", LX, 110, 60, PURPLE, s.t("flavor") - 0.3)
    g.label("MOUTH (chewing)", P(640, 445), 250, s.t("chew") - 0.3, TASTE, 42)
    g.label("aroma rises to the SMELL PATCH", P(675, 195), 380, s.t("aroma") - 0.3, SMELL, 30)
    g.say("brain BLENDS it with taste", LX, 530, 36, GOLD_T, s.t("blends") - 0.5)
    g.say("nose blocked = BLAND", LX, 660, 46, RED_T, s.t("bland") - 0.4)
    g.say("taste buds still work", LX, 780, 42, MAROON, s.t("buds") - 0.4)
    cv.flow([P(x, y) for x, y in ((650, 440), (560, 430), (490, 390), (470, 310), (520, 250), (600, 215), (675, 195))], s.t("chew") - 0.2, s.start + s.dur, 2.6, SMELL, 13, 4)
    g.drift(s)
    g.clear(s.start + s.dur - 0.8)

    # ---------------- CARE
    s = sc["care"]
    g.say("SUDDEN loss of", LX, 200, 50, RED_T, s.t("suddenly") - 0.3)
    g.say("smell or taste?", LX, 290, 50, RED_T, s.t("smell") - 0.2)
    g.say("or not back 1-2 weeks", LX, 430, 38, MAROON, s.t("week") - 0.8)
    g.say("after a cold", LX, 500, 38, MAROON, s.t("cold") - 0.4)
    g.labels.append(g.panel(LX - 30, 600, 1880, 740, MINT, s.t("doctor") - 1.0))
    g.say("see a doctor", LX, 670, 56, GREEN_T, s.t("doctor") - 0.8)
    g.drift(s, 0.5, 0.5)
    g.clear(s.start + s.dur - 0.6)

    # ---------------- RECAP
    s = sc["recap"]
    g.say("remember 3 things", LX, 110, 46, MAROON, s.start + 0.3)
    g.label("smell -> emotion + memory", P(675, 195), 240, s.t("smell") - 0.3, SMELL, 32)
    g.label("5 tastes, all over the TONGUE", P(580, 460), 380, s.t("taste") - 0.3, TASTE, 30)
    g.say("FLAVOR = taste + smell", LX, 520, 40, GOLD_T, s.t("flavor") - 0.3)
    tn = s.t("next") - 1.0
    g.labels.append(g.panel(LX - 30, 680, 1900, 860, LILAC, tn - 0.3))
    g.say("next:", LX, 740, 36, PURPLE, tn)
    g.say("the reproductive system", LX, 810, 36, PURPLE, tn + 0.4)
    g.drift(s, 0.8, 0.5)

    bd.fx.append(cv.fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def map_shot(cross=False):
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


def build_short(n):
    sc, t0 = load(EP / f"short{n}")
    bd = B.Board(1, 1)
    pops = []
    kit = HA.kit(bd, pops)
    cv = Cine(bd)
    g = Stage(bd, kit, cv)
    bd.camera(0, 960, 540, 1.0, 0.1)
    if n == 1:
        s = sc["case"]
        g.picture(map_shot(), 0.0, 0.3)
        g.say("the old TONGUE MAP", LX, 200, 48, PURPLE, s.t("tongue") - 0.4)
        g.label("sweet at the TIP", P(460, 680, 5), 360, s.t("sweet") - 0.3, RED_T, 44)
        g.label("bitter at the BACK", P(460, 190, 5), 500, s.t("bitter") - 1.0, GREEN_T, 44)
        g.clear(s.start + s.dur - 0.5)
        s = sc["turn"]
        g.picture(map_shot(True), s.start - 0.4, 0.8)
        g.say("a MYTH", LX, 200, 90, RED_T, s.t("myth") - 0.3)
        g.say("every taste, all over", LX, 380, 44, GREEN_T, s.t("over") - 1.0)
        g.say("how many tastes?", LX, 520, 50, GOLD_T, s.t("many") - 1.4)
        g.say("?", LX + 200, 800, 200, PURPLE, s.t("tastes") - 0.9)
    else:
        s = sc["case"]
        g.picture(shot(2), 0.0, 0.3)
        g.say("STUFFY nose", LX, 220, 66, BLUE_T, s.t("stuffy") - 0.4)
        g.say("favorite food = BLAND", LX, 360, 42, RED_T, s.t("favorite") - 0.2)
        cv.glow(0.3, P(640, 290), s.dur, 150, (110, 170, 230))
        g.clear(s.start + s.dur - 0.5)
        g.focus(s.start + s.dur, P(580, 460), 1.4, 1.2)
        s = sc["twist"]
        g.picture(shot(6), s.start - 0.4, 0.8)
        g.say("taste buds: FINE", LX, 260, 58, GREEN_T, s.t("buds") - 0.4)
        g.say("something else is missing", LX, 420, 34, PURPLE, s.t("something") - 0.2)
        g.clear(s.start + s.dur - 0.5)
        s = sc["clue"]
        g.picture(shot(2), s.start - 0.4, 0.8)
        g.say("what is missing?", LX, 300, 54, GOLD_T, s.t("what") - 0.3)
        g.say("?", LX + 200, 640, 200, PURPLE, s.t("flavor") - 0.2)
        cv.flow([P(x, y) for x, y in ((650, 440), (560, 430), (490, 390), (470, 310), (520, 250), (600, 215), (675, 195))], s.start + 0.3, s.start + s.dur, 2.2, SMELL, 12, 3)

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
            bd.frame(round(v.start + v.dur * 0.8, 1)).save(OUT / f"s3_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                bd.frame(round(v.start + v.dur * 0.85, 1)).save(OUT / f"s3_short{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "smelltaste", intro=True)
        f.replace(OUT / "final_smelltaste.mp4")
        print("done ->", OUT / "final_smelltaste.mp4")
