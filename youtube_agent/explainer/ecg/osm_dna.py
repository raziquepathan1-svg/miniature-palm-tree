"""F2 INSIDE THE NUCLEUS: how DNA makes proteins - smooth single-page cinematic build.
Owner images art/dna/shot3-8 (+ the cell and nucleus from art/cell for the location-first opening).

    python3 osm_dna.py [stills] | short 1|2 [stills]
"""
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "dna")))
OUT = Path(os.environ.get("OUT_DIR", str(HERE)))
ART = HERE.parent / "art" / "dna"
CELL = HERE.parent / "art" / "cell"
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_hanat as HA  # noqa: E402
import osm_brain as OB  # noqa: E402
import osm_neuron as NU  # noqa: E402
from osm_ear2 import Cine, P as P0  # noqa: E402
from osm_cell import Stage, LX  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
LILAC = OB.LILAC
CR = 26
DNA_C, RNA_C, AA, NUC = (90, 120, 200), (230, 120, 60), (200, 80, 120), (150, 110, 220)
SHORT_TITLES = {1: "Two Meters Of DNA In Every Cell", 2: "How The Recipe Leaves The Nucleus"}
SHORT_Q = {1: "So how does it fit?", 2: "So how does the recipe get out?"}


def shot(n, folder=None):
    im = Image.open((folder or ART) / f"shot{n}.jpg").convert("RGBA")
    return im.crop((CR, CR, 1376 - CR, 768 - CR)).resize((1376, 768), Image.LANCZOS)


def P(x, y):
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

    # ---------------- STORY: the cell -> its nucleus -> push in
    s = sc["story"]
    g.picture(shot(3, CELL), 0.0, 0.4)
    g.say("DNA of ONE cell", LX, 200, 52, DNA_C, s.t("dna") - 0.3)
    g.say("stretched out = ~2 METERS", LX, 300, 36, GOLD_T, s.t("meters") - 0.4)
    g.label("fits in the NUCLEUS", P(450, 345), 440, s.t("nucleus") - 0.4, NUC, 44)
    cv.glow(s.t("tiny") - 0.2, P(450, 345), 3.0, 110, NUC)
    tc = s.t("how") - 0.2
    g.focus(tc + 1.4, P(450, 345), 1.6, 1.8)
    g.clear(tc - 0.2)
    g.picture(shot(4, CELL), tc + 0.6)
    g.say("how does it BUILD you?", LX, 300, 44, PURPLE, s.t("build") - 0.2)
    g.say("let's go INSIDE", LX, 460, 50, GREEN_T, s.t("inside") - 0.8)
    g.clear(s.start + s.dur - 1.7)
    g.focus(s.start + s.dur, P(300, 250), 1.6, 1.8)

    # ---------------- PACK: chromosome -> histones -> helix
    s = sc["pack"]
    g.picture(shot(3), s.start - 0.6)
    g.label("CHROMOSOME", P(215, 330), 80, s.t("chromosomes") - 0.4, PURPLE, 44)
    g.say("46 chromosomes in a cell", 90, 1000, 38, MAROON, s.t("forty") - 0.4)
    g.label("coiled fiber", P(510, 540), 160, s.t("tighter") - 0.4, NUC, 38)
    g.label("HISTONES (protein spools)", P(735, 455), 240, s.t("histones") - 0.3, (200, 80, 120), 32)
    g.label("DNA thread", P(1060, 520), 320, s.t("thread") - 0.3, DNA_C, 38)
    g.say("folds again and again", 1000, 1000, 38, GREEN_T, s.t("fold") - 0.6)
    cv.flow([P(x, y) for x, y in ((1250, 320), (1150, 450), (1000, 560), (880, 560), (760, 455), (640, 360), (520, 380), (480, 480), (450, 560), (380, 520))],
            s.t("histones") - 0.4, s.start + s.dur, 3.4, (250, 210, 90), 10, 2)
    g.drift(s)
    g.clear(s.start + s.dur - 1.7)
    g.focus(s.start + s.dur, P(1150, 450), 1.6, 1.8)

    # ---------------- HELIX: base pairs and genes
    s = sc["helix"]
    g.picture(shot(4), s.start - 0.6)
    g.label("DOUBLE HELIX", P(320, 330), 140, s.t("helix") - 0.3, DNA_C, 52)
    g.label("BASE PAIR (a rung)", P(400, 425), 270, s.t("rung") - 0.3, GOLD_T, 42)
    g.say("A pairs with T", LX, 400, 48, RED_T, s.t("always") - 0.4)
    g.say("G pairs with C", LX, 480, 48, GREEN_T, s.t("always", 2) - 0.4)
    g.say("the ORDER = the code", LX, 600, 44, PURPLE, s.t("order") - 0.3)
    g.label("a GENE = one recipe", P(430, 520), 720, s.t("gene") - 0.3, MAROON, 40)
    g.say("~20,000 genes", LX, 840, 46, GOLD_T, s.t("twenty") - 0.4)
    for i, (x, y) in enumerate(((240, 150), (290, 205), (270, 255), (360, 360), (380, 410), (400, 465), (420, 515))):
        cv.glow(s.t("pairs") + 0.12 * i, P(x, y), 1.6, 32, (250, 220, 120))
    cv.glow(s.t("gene") - 0.2, P(420, 470), 3.2, 120, (240, 150, 170))
    g.drift(s)
    g.clear(s.start + s.dur - 1.0)

    # ---------------- TRANSCRIBE
    s = sc["transcribe"]
    g.picture(shot(5), s.start - 0.6)
    g.say("step 1: make a COPY", LX, 120, 46, MAROON, s.t("copy") - 0.3)
    g.label("RNA POLYMERASE (enzyme)", P(540, 390), 260, s.t("polymerase") - 0.3, PURPLE, 34)
    g.label("DNA opened", P(450, 480), 380, s.t("opens") - 0.3, DNA_C, 44)
    g.label("mRNA (messenger)", P(240, 235), 510, s.t("messenger") - 0.3, RNA_C, 44)
    g.say("in RNA, U replaces T", LX, 640, 42, GOLD_T, s.t("letter") - 0.3)
    g.say("= TRANSCRIPTION", LX, 780, 50, RED_T, s.t("transcription") - 0.5)
    cv.flow([P(x, y) for x, y in ((500, 410), (420, 360), (350, 300), (280, 250), (200, 200), (160, 130))], s.t("builds") - 0.2, s.start + s.dur, 2.6, RNA_C, 11, 3)
    cv.glow(s.t("polymerase") - 0.2, P(540, 390), 3.0, 140, (200, 170, 240))
    g.drift(s)
    g.clear(s.start + s.dur - 1.0)

    # ---------------- EXPORT: out through the nuclear pore
    s = sc["export"]
    g.picture(shot(6), s.start - 0.6)
    g.label("inside the NUCLEUS", P(150, 250), 150, s.t("nucleus") - 0.3, NUC, 44)
    g.label("NUCLEAR PORE", P(375, 370), 290, s.t("pore") - 0.3, PURPLE, 48)
    g.label("mRNA copy", P(560, 490), 430, s.t("copy") - 0.3, RNA_C, 46)
    g.label("RIBOSOMES waiting", P(630, 385), 570, s.t("ribosomes") - 0.4, BLUE_T, 42)
    g.say("in the CYTOPLASM", LX, 700, 44, GREEN_T, s.t("cytoplasm") - 0.4)
    cv.flow([P(x, y) for x, y in ((300, 330), (370, 370), (420, 420), (480, 480), (560, 490), (640, 480), (700, 560), (740, 600))], s.start + 0.6, s.start + s.dur, 2.6, RNA_C, 11, 3)
    g.drift(s, 0.8, 1.4)
    g.clear(s.start + s.dur - 1.4)
    g.focus(s.start + s.dur, P(630, 385), 1.5, 1.4)

    # ---------------- TRANSLATE at the ribosome
    s = sc["translate"]
    g.picture(shot(7), s.start - 0.6)
    g.label("RIBOSOME", P(450, 260), 130, s.t("ribosome") - 0.3, NUC, 52)
    g.label("mRNA message", P(150, 545), 250, s.t("message") - 0.3, RNA_C, 42)
    g.label("CODON = 3 letters", P(345, 445), 370, s.t("codon") - 0.4, GOLD_T, 42)
    g.label("tRNA", P(150, 375), 490, s.t("transfer") - 0.3, BLUE_T, 50)
    g.label("AMINO ACID", P(125, 335), 610, s.t("amino") - 0.3, AA, 44)
    g.label("growing CHAIN", P(470, 125), 730, s.t("chain") - 0.3, GREEN_T, 44)
    g.say("= TRANSLATION", LX, 850, 50, RED_T, s.t("translation") - 0.6)
    cv.flow([P(x, y) for x, y in ((390, 270), (405, 215), (420, 190), (470, 125), (550, 128), (630, 150), (710, 95))], s.t("links") - 0.2, s.start + s.dur, 2.6, (250, 200, 80), 11, 3)
    cv.flow([P(x, y) for x, y in ((60, 550), (200, 500), (330, 460), (450, 455), (600, 510), (740, 560))], s.start + 0.8, s.start + s.dur, 4.0, RNA_C, 9, 2)
    g.drift(s)
    g.clear(s.start + s.dur - 1.0)

    # ---------------- FOLD
    s = sc["fold"]
    g.picture(shot(8), s.start - 0.6)
    g.say("20 kinds of amino acids", LX, 120, 40, AA, s.t("twenty") - 0.3)
    g.label("amino acid chain", P(160, 190), 250, s.t("chain") - 0.3, MAROON, 42)
    g.label("SPIRALS (alpha helix)", P(430, 330), 370, s.t("spirals") - 0.3, RED_T, 38)
    g.label("SHEETS (beta sheet)", P(590, 400), 490, s.t("sheets") - 0.3, BLUE_T, 38)
    g.label("FOLDED PROTEIN", P(810, 400), 610, s.t("final") - 0.3, GREEN_T, 44)
    g.say("SHAPE decides the JOB", LX, 730, 42, GOLD_T, s.t("shape") - 0.3)
    g.say("oxygen · germs · muscles", LX, 830, 38, PURPLE, s.t("oxygen") - 0.4)
    cv.glow(s.t("final") - 0.2, P(810, 400), 3.5, 150, (250, 220, 140))
    g.drift(s)
    g.clear(s.start + s.dur - 0.8)

    # ---------------- RECAP
    s = sc["recap"]
    g.picture(shot(5), s.start - 0.6)
    g.say("remember the flow:", LX, 120, 46, MAROON, s.start + 0.4)
    g.label("DNA", P(300, 540), 250, s.t("dna") - 0.3, DNA_C, 56)
    g.label("-> RNA", P(240, 235), 360, s.t("rna") - 0.3, RNA_C, 56)
    g.say("-> PROTEIN", LX, 470, 56, GREEN_T, s.t("protein") - 0.3)
    g.say("transcription: nucleus", LX, 590, 36, PURPLE, s.t("transcription") - 0.3)
    g.say("translation: ribosome", LX, 660, 36, BLUE_T, s.t("translation") - 0.3)
    tn = s.t("next") - 1.0
    g.labels.append(g.panel(LX - 30, 740, 1900, 900, LILAC, tn - 0.3))
    g.say("next: how cells", LX, 790, 38, PURPLE, tn)
    g.say("make ENERGY", LX, 860, 44, PURPLE, tn + 0.5)
    g.drift(s, 0.8, 0.5)

    bd.fx.append(cv.fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


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
        g.picture(shot(4), 0.0, 0.3)
        g.say("DNA of ONE cell", LX, 220, 54, DNA_C, s.t("dna") - 0.3)
        g.say("~2 METERS long!", LX, 360, 58, GOLD_T, s.t("meters") - 0.5)
        g.clear(s.start + s.dur - 0.5)
        g.focus(s.start + s.dur, P(400, 420), 1.3, 1.2)
        s = sc["turn"]
        g.picture(shot(4, CELL), s.start - 0.4, 0.8)
        g.label("a tiny NUCLEUS", P(430, 372), 240, s.t("nucleus") - 0.4, NUC, 46)
        g.say("how does it fit?", LX, 420, 50, GOLD_T, s.t("fit") - 0.8)
        g.say("?", LX + 200, 700, 200, PURPLE, s.t("fit") - 0.3)
    else:
        s = sc["case"]
        g.picture(shot(4, CELL), 0.0, 0.3)
        g.label("DNA stays in the NUCLEUS", P(300, 250), 240, s.t("nucleus") - 0.5, NUC, 38)
        s = sc["twist"]
        g.say("proteins: built OUTSIDE", LX, 420, 42, GREEN_T, s.t("outside") - 0.6)
        g.clear(s.start + s.dur - 0.4)
        g.focus(s.start + s.dur, P(212, 318), 1.4, 1.0)
        s = sc["clue"]
        g.picture(shot(6), s.start - 0.3, 0.7)
        g.say("how does the recipe", LX, 280, 46, GOLD_T, s.t("how") - 0.3)
        g.say("get OUT?", LX, 370, 56, GOLD_T, s.t("out") - 0.4)
        cv.glow(s.start + 0.2, P(375, 370), s.dur, 90, (200, 170, 240))

    bd.fx.append(cv.fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def make_short(n):
    import package as Pk
    import bridge
    bd, sc = build_short(n)
    board = NU.render_board(bd, sc, f"dna_story{n}")
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
    ov = OUT / f"dna_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"dna_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["dna"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "dna", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            bd.frame(round(v.start + v.dur * 0.82, 1)).save(OUT / f"d_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                bd.frame(round(v.start + v.dur * 0.85, 1)).save(OUT / f"d_short{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "dna", intro=True)
        f.replace(OUT / "final_dna.mp4")
        print("done ->", OUT / "final_dna.mp4")
