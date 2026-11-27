"""REPRODUCTIVE SYSTEM v3 - smooth single-page cinematic build (cross-fades, location-first push-ins, labelled pointers).
Owner images art/repro/shot2-6 + whole human art/ear/shot1. Same fact-checked script ../repro.

    python3 osm_repro3.py [stills] | short 1|2 [stills]
"""
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "repro")))
OUT = Path(os.environ.get("OUT_DIR", str(HERE)))
ART = HERE.parent / "art" / "repro"
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
EGG, SPERM, HORM, PLUM, UT = (240, 180, 50), (90, 140, 220), (230, 110, 160), (150, 70, 130), (220, 100, 130)
SHORT_TITLES = {1: "How Many Eggs Are Released", 2: "Only One Sperm Gets In"}
SHORT_Q = {1: "So how many eggs are released in a lifetime?", 2: "So what stops all the other sperm?"}


def shot(n):
    if n == 1:
        return Image.open(HERE.parent / "art" / "ear" / "shot1.png").convert("RGBA")
    im = Image.open(ART / f"shot{n}.jpg").convert("RGBA")
    return im.crop((CR, CR, 1376 - CR, 768 - CR)).resize((1376, 768), Image.LANCZOS)


def P(x, y, n=2):
    if n == 1:
        return P0(0, 0, x, y)
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
    lead = kit[2]
    bd.camera(0, 960, 540, 1.0, 0.1)
    pelvis = P(690, 395, 1)

    # ---------------- STORY: whole body -> into the pelvis
    s = sc["story"]
    g.picture(shot(1), 0.0, 0.4)
    g.say("ONE single cell", 70, 230, 60, GOLD_T, s.t("single") - 0.4)
    g.say("~0.1 mm wide", 70, 330, 52, MAROON, s.t("tenth") - 0.4)
    g.say("a whole new life?", 70, 480, 52, PURPLE, s.t("life") - 0.6)
    g.say("REPRODUCTIVE SYSTEM", 70, 640, 50, RED_T, s.t("reproductive") - 0.3)
    g.say("follow the journey", 70, 790, 48, GREEN_T, s.t("follow") - 1.4)
    cv.glow(s.t("reproductive") - 0.2, pelvis, 3.5, 70, EGG)
    g.clear(s.start + s.dur - 2.2)
    g.focus(s.start + s.dur, pelvis, 2.6, 2.2)

    # ---------------- FEMALE organs
    s = sc["female"]
    g.picture(shot(2), s.start - 0.6)
    g.label("OVARY", P(240, 330), 160, s.t("ovaries") - 0.3, GOLD_T, 52)
    g.labels.append(lead([(LX - 12, 156), (1100, 200), P(760, 330)], s.t("ovaries") - 0.1, GOLD_T, 4, 0.5, arrow=True))
    g.label("FALLOPIAN TUBE", P(340, 238), 290, s.t("fallopian") - 0.3, PURPLE, 46)
    g.label("FIMBRIAE", P(165, 335), 410, s.t("fallopian") + 0.4, PLUM, 42)
    g.label("UTERUS", P(500, 300), 540, s.t("uterus") - 0.3, RED_T, 54)
    g.label("CERVIX", P(500, 497), 670, s.t("cervix") - 0.3, MAROON, 50)
    g.say("hormones: ESTROGEN +", LX, 800, 36, HORM, s.t("estrogen") - 1.0)
    g.say("PROGESTERONE", LX, 870, 40, HORM, s.t("estrogen") - 0.4)
    cv.glow(s.t("estrogen") - 0.2, P(240, 330), 3.0, 70, HORM)
    cv.glow(s.t("estrogen") - 0.2, P(760, 330), 3.0, 70, HORM)
    g.drift(s, 1.2, 2.0)
    g.clear(s.start + s.dur - 1.8)
    g.focus(s.start + s.dur, P(240, 330), 1.5, 1.8)

    # ---------------- OVULATION
    s = sc["ovulation"]
    g.picture(shot(3), s.start - 0.6)
    g.say("born with ALL her eggs", LX, 110, 38, MAROON, s.t("born") - 0.3)
    g.say("1-2 MILLION", LX, 200, 56, GOLD_T, s.t("million") - 0.4)
    g.label("FOLLICLES", P(380, 290, 3), 330, s.t("follicle") - 0.6, PURPLE, 46)
    g.labels.append(lead([(LX - 12, 326), (1150, 380), P(300, 440, 3)], s.t("follicle") - 0.4, PURPLE, 4, 0.5, arrow=True))
    g.label("MATURE FOLLICLE bursts", P(590, 400, 3), 450, s.t("bursts") - 0.4, RED_T, 38)
    g.label("EGG", P(735, 385, 3), 570, s.t("releases") - 0.3, EGG, 56)
    g.label("FIMBRIAE", P(810, 320, 3), 690, s.t("fimbriae") - 0.3, PLUM, 46)
    g.say("lifetime: only a few HUNDRED", LX, 830, 34, GREEN_T, s.t("hundred") - 2.2)
    cv.glow(s.t("follicle") - 0.2, P(590, 400, 3), 2.6, 90, (235, 110, 140))
    cv.flow([P(x, y, 3) for x, y in ((600, 400), (680, 390), (740, 385), (800, 330), (830, 250), (790, 160), (650, 130), (420, 140))],
            s.t("bursts") - 0.1, s.start + s.dur, 3.2, EGG, 16, 1)
    g.drift(s)
    g.clear(s.start + s.dur - 1.0)

    # ---------------- MALE: locate on the body first, then dissolve into the testis
    s = sc["male"]
    g.picture(shot(1), s.start - 0.6)
    g.say("now the MALE system", 70, 300, 52, BLUE_T, s.start + 0.2)
    cv.glow(s.start + 0.2, P(690, 470, 1), 2.4, 60, SPERM)
    g.focus(s.start + 2.4, P(690, 470, 1), 2.4, 2.0)
    tc = s.start + 2.2
    g.clear(tc - 0.4)
    g.picture(shot(4), tc)
    g.label("TESTIS", P(330, 520, 4), 150, s.t("testes") - 0.2, BLUE_T, 56)
    g.say("sperm + TESTOSTERONE", LX, 250, 36, MAROON, s.t("testosterone") - 0.4)
    g.label("SEMINIFEROUS TUBULES", P(420, 380, 4), 370, s.t("seminiferous") - 0.3, PURPLE, 38)
    g.label("EPIDIDYMIS", P(560, 215, 4), 490, s.t("epididymis") - 0.3, PLUM, 48)
    g.label("VAS DEFERENS", P(700, 260, 4), 610, s.t("vas") - 0.3, BLUE_T, 46)
    g.say("a little COOLER", LX, 750, 48, GREEN_T, s.t("cooler") - 0.6)
    g.say("MILLIONS every day", LX, 860, 46, GOLD_T, s.t("millions") - 1.1)
    cv.glow(s.t("seminiferous") - 0.2, P(470, 450, 4), 2.6, 150, SPERM)
    cv.flow([P(x, y, 4) for x, y in ((470, 450), (450, 300), (440, 220), (560, 215), (640, 320), (660, 520), (700, 580), (715, 420), (700, 250), (660, 100))],
            s.t("epididymis") - 0.4, s.start + s.dur, 3.0, SPERM, 10, 4)
    g.drift(s, 3.6)
    g.clear(s.start + s.dur - 1.0)

    # ---------------- FERTILIZE: locate the tube, push in, dissolve into the meeting
    s = sc["fertilize"]
    g.picture(shot(2), s.start - 0.6)
    cv.glow(s.start + 0.1, P(330, 230), 2.4, 80, EGG)
    g.focus(s.start + 2.2, P(330, 230), 1.8, 1.9)
    tc = s.start + 2.0
    g.picture(shot(5), tc)
    g.say("in the FALLOPIAN TUBE", LX, 110, 40, PURPLE, s.t("fallopian") - 0.4)
    g.label("EGG", P(500, 430, 5), 240, s.t("egg") - 0.3, EGG, 56)
    g.label("SPERM", P(368, 335, 5), 360, s.t("sperm") - 0.3, SPERM, 50)
    g.label("only ONE gets in", P(580, 392, 5), 480, s.t("one") - 0.3, RED_T, 44)
    g.label("OUTER LAYER blocks", P(500, 305, 5), 600, s.t("blocks") - 0.6, MAROON, 40)
    g.say("23 + 23 = 46", LX, 750, 64, GOLD_T, s.t("twenty") - 0.4)
    g.say("chromosomes: a NEW set", LX, 850, 36, GREEN_T, s.t("brand") - 0.8)
    for i, (x, y) in enumerate(((160, 300), (170, 470), (300, 180), (320, 620), (140, 390))):
        cv.flow([P(x, y, 5), P((x + 500) / 2, (y + 400) / 2, 5), P(500 + (x - 500) * 0.22, 400 + (y - 400) * 0.22, 5)], tc + 0.6 + 0.2 * i, s.t("blocks"), 2.2, SPERM, 7, 2)
    cv.glow(s.t("blocks") - 0.3, P(500, 400, 5), 3.0, 150, EGG)
    cv.glow(s.t("brand") - 0.3, P(500, 400, 5), 2.6, 110, (255, 220, 120))
    g.drift(s, 3.4, 1.9)
    g.clear(s.start + s.dur - 1.7)
    g.focus(s.start + s.dur, P(500, 400, 5), 1.6, 1.7)

    # ---------------- IMPLANT
    s = sc["implant"]
    g.picture(shot(6), s.start - 0.6)
    g.say("DIVIDES again and again", LX, 110, 38, PURPLE, s.t("divides") - 0.4)
    g.label("BLASTOCYST", P(490, 400, 6), 250, s.t("blastocyst") - 0.3, GOLD_T, 52)
    g.say("6-10 days after fertilization", LX, 370, 32, MAROON, s.t("six") - 0.4)
    g.label("UTERINE LINING", P(640, 250, 6), 500, s.t("lining") - 0.4, RED_T, 46)
    g.label("blood vessels", P(160, 470, 6), 620, s.t("blood") - 0.3, (200, 60, 70), 40)
    g.say("= IMPLANTATION", LX, 760, 52, PLUM, s.t("implantation") - 0.9)
    g.say("pregnancy begins", LX, 860, 48, GREEN_T, s.t("pregnancy") - 0.8)
    cv.glow(s.t("blastocyst") - 0.2, P(490, 400, 6), 3.0, 110, EGG)
    cv.glow(s.t("implantation") - 0.2, P(490, 400, 6), 3.5, 130, EGG)
    g.drift(s)
    g.clear(s.start + s.dur - 1.0)

    # ---------------- CYCLE
    s = sc["cycle"]
    g.picture(shot(2), s.start - 0.6)
    g.say("no fertilized egg?", LX, 160, 46, PURPLE, s.t("fertilized") - 0.4)
    g.say("hormones FALL", LX, 290, 52, MAROON, s.t("fall") - 0.4)
    g.label("UTERINE LINING sheds", P(500, 330), 420, s.t("sheds") - 0.4, RED_T, 40)
    g.say("= the PERIOD", LX, 560, 54, RED_T, s.t("period") - 0.4)
    g.say("then it starts AGAIN", LX, 720, 46, GREEN_T, s.t("again") - 1.6)
    cv.glow(s.t("sheds") - 0.2, P(500, 330), 3.0, 120, (220, 70, 80))
    cv.flow([P(x, y) for x, y in ((500, 330), (500, 450), (500, 560), (500, 640))], s.t("sheds") - 0.1, s.t("again"), 1.6, (210, 60, 70), 9, 3)
    g.drift(s, 0.8, 0.8)
    g.clear(s.start + s.dur - 0.8)

    # ---------------- CARE
    s = sc["care"]
    g.say("SEE A DOCTOR if:", LX, 130, 50, GREEN_T, s.t("doctor") - 0.4)
    g.say("very painful or irregular periods", LX, 260, 30, RED_T, s.t("painful") - 0.4)
    g.say("a lump or pain in a testicle", LX, 370, 32, BLUE_T, s.t("lump") - 0.4)
    g.say("no pregnancy after 1 year", LX, 480, 34, PURPLE, s.t("trouble") - 0.4)
    g.say("(6 months if over 35)", LX, 570, 34, MAROON, s.t("six") - 0.6)
    g.drift(s, 0.5, 0.5)
    g.clear(s.start + s.dur - 0.6)

    # ---------------- RECAP
    s = sc["recap"]
    g.say("remember 3 things", LX, 110, 46, MAROON, s.start + 0.3)
    g.label("ovaries -> eggs", P(240, 330), 240, s.t("ovaries") - 0.3, GOLD_T, 42)
    g.say("testes -> sperm", LX, 330, 42, BLUE_T, s.t("testes") - 0.3)
    g.label("fertilization: the TUBE", P(330, 230), 460, s.t("fertilization") - 0.3, PURPLE, 38)
    g.label("embryo implants: UTERUS", P(500, 300), 580, s.t("embryo") - 0.3, RED_T, 36)
    tn = s.t("next") - 1.0
    g.labels.append(g.panel(LX - 30, 700, 1900, 880, LILAC, tn - 0.3))
    g.say("next: back to the start", LX, 760, 36, PURPLE, tn)
    g.say("THE CELL", LX, 830, 44, PURPLE, tn + 0.6)
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
        g.picture(shot(3), 0.0, 0.3)
        g.say("born with ALL her eggs", LX, 220, 40, MAROON, s.t("born") - 0.4)
        g.say("1-2 MILLION", LX, 360, 62, GOLD_T, s.t("million") - 0.6)
        for i, (x, y) in enumerate(((290, 330), (380, 290), (250, 410), (400, 520))):
            cv.glow(0.6 + 0.3 * i, P(x, y, 3), 2.0, 30, EGG)
        g.drift(s, 0.3, 0.2)
        g.clear(s.start + s.dur - 0.5)
        s = sc["turn"]
        g.say("most are NEVER used", LX, 220, 44, RED_T, s.t("never") - 0.4)
        g.say("how many released?", LX, 380, 46, GOLD_T, s.t("how") - 0.4)
        g.say("?", LX + 200, 680, 200, PURPLE, s.t("released") - 0.6)
        cv.flow([P(x, y, 3) for x, y in ((600, 400), (680, 390), (740, 385), (800, 330))], s.start + 0.4, s.start + s.dur, 2.0, EGG, 14, 1)
        g.focus(s.start + s.dur, P(735, 385, 3), 1.3, 2.5)
    else:
        s = sc["case"]
        g.picture(shot(5), 0.0, 0.3)
        g.say("MANY sperm", LX, 240, 62, BLUE_T, s.t("many") - 0.3)
        g.say("reach the egg", LX, 360, 50, MAROON, s.t("reach") - 0.4)
        for i, (x, y) in enumerate(((160, 300), (170, 470), (300, 180), (320, 620))):
            cv.flow([P(x, y, 5), P(500 + (x - 500) * 0.22, 400 + (y - 400) * 0.22, 5)], 0.3 + 0.2 * i, s.start + s.dur, 1.6, SPERM, 7, 2)
        s = sc["twist"]
        g.label("only ONE gets in", P(580, 392, 5), 520, s.t("one") - 0.4, RED_T, 46)
        g.focus(s.start + s.dur, P(560, 395, 5), 1.35, s.dur)
        s = sc["clue"]
        g.say("what stops the others?", LX, 680, 40, GOLD_T, s.t("stops") - 0.5)
        cv.glow(s.start + 0.2, P(500, 400, 5), s.dur, 140, EGG)

    bd.fx.append(cv.fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def make_short(n):
    import package as Pk
    import bridge
    bd, sc = build_short(n)
    board = NU.render_board(bd, sc, f"repro_story{n}")
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
    ov = OUT / f"repro_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"repro_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["repro"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "repro", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            bd.frame(round(v.start + v.dur * 0.8, 1)).save(OUT / f"r3_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                bd.frame(round(v.start + v.dur * 0.85, 1)).save(OUT / f"r3_short{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "repro", intro=True)
        f.replace(OUT / "final_repro.mp4")
        print("done ->", OUT / "final_repro.mp4")
