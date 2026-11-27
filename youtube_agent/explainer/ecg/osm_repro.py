"""REPRODUCTIVE SYSTEM - cinematic build (owner images art/repro/shot2-6, whole human art/ear/shot1, fact-checked script ../repro).

    python3 osm_repro.py [stills] | short 1|2 [stills]
Env: EP_DIR (default ../repro), OUT_DIR.
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
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_brain as OB  # noqa: E402
import osm_neuron as NU  # noqa: E402
from osm_ear2 import Cine, P as P0  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
PINK, LILAC, CREAM, MINT = OB.PINK, OB.LILAC, OB.CREAM, OB.MINT
PW, PH = 1920, 1080
CR = 26                                                        # owner shots have a whiteboard frame: crop it off
EGG, SPERM, HORM, PLUM = (250, 200, 70), (120, 160, 230), (240, 120, 170), (150, 70, 130)
SHORT_TITLES = {1: "How Many Eggs Are Released", 2: "Only One Sperm Gets In"}
SHORT_Q = {1: "So how many eggs are released in a lifetime?", 2: "So what stops all the other sperm?"}


def shot(n):
    if n == 1:
        return Image.open(HERE.parent / "art" / "ear" / "shot1.png").convert("RGBA")
    im = Image.open(ART / f"shot{n}.jpg").convert("RGBA")
    return im.crop((CR, CR, 1376 - CR, 768 - CR)).resize((1376, 768), Image.LANCZOS)


def P(ox, oy, x, y):
    """pixel of an ORIGINAL 1376x768 owner shot (before the frame crop) -> board units"""
    return P0(ox, oy, (x - CR) * 1376 / (1376 - 2 * CR), (y - CR) * 768 / (768 - 2 * CR))


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

    # ---------------- STORY (A): the whole human, then dive into the pelvis
    s = sc["story"]
    st = [pop(shot(1), 960, 540, w=1920, t=0.0, dur=0.4), text("ONE single cell", 330, 240, 58, GOLD_T, s.t("single") - 0.4, "c"),
          text("~0.1 mm wide", 330, 360, 52, MAROON, s.t("tenth") - 0.4, "c"), text("a whole new life?", 1600, 260, 56, PURPLE, s.t("life") - 0.6, "c"),
          text("REPRODUCTIVE", 1600, 560, 64, RED_T, s.t("reproductive") - 0.3, "c"), text("SYSTEM", 1600, 650, 64, RED_T, s.t("reproductive") - 0.1, "c"),
          text("follow the journey", 330, 820, 54, GREEN_T, s.t("follow") - 1.7, "c")]
    pelvis = P0(0, 0, 690, 395)
    cv.glow(s.t("reproductive") - 0.2, pelvis, 3.0, 70, EGG)
    cv.dive_out(s, pelvis, 4.5, 2.0)

    # ---------------- FEMALE (B): ovaries, tubes, uterus, cervix
    s = sc["female"]
    cv.land(s, Bc)
    bd.erase(s.start + 0.8, st[:1])
    bd.erase(s.start - 1.2, st[1:])
    X = PW
    fe = [pop(shot(2), X + 960, 540, w=1920, t=s.start), text("2 OVARIES", X + 1600, 170, 62, GOLD_T, s.t("ovaries") - 0.3, "c"),
          text("2 FALLOPIAN TUBES", X + 1600, 300, 52, PURPLE, s.t("fallopian") - 0.3, "c"), text("UTERUS", X + 1600, 430, 66, RED_T, s.t("uterus") - 0.3, "c"),
          text("CERVIX", X + 1600, 560, 60, MAROON, s.t("cervix") - 0.3, "c"),
          text("hormones:", X + 1600, 740, 44, MAROON, s.t("hormones") - 0.4, "c"), text("ESTROGEN + PROGESTERONE", X + 1600, 830, 40, PLUM, s.t("estrogen") - 1.0, "c")]
    cv.glow(s.t("ovaries") - 0.2, P(X, 0, 240, 330), 2.0, 70, EGG)
    cv.glow(s.t("ovaries") - 0.1, P(X, 0, 760, 330), 2.0, 70, EGG)
    cv.flow([P(X, 0, x, y) for x, y in ((180, 330), (165, 230), (230, 170), (330, 200), (420, 235))], s.t("fallopian") - 0.2, s.t("uterus") + 0.6, 1.4, PLUM, 9, 2)
    cv.flow([P(X, 0, x, y) for x, y in ((850, 330), (860, 230), (800, 170), (700, 200), (600, 235))], s.t("fallopian") - 0.1, s.t("uterus") + 0.6, 1.4, PLUM, 9, 2)
    cv.glow(s.t("uterus") - 0.2, P(X, 0, 500, 330), 2.0, 120, (235, 110, 140))
    cv.glow(s.t("cervix") - 0.2, P(X, 0, 500, 560), 1.8, 60, (235, 110, 140))
    cv.glow(s.t("estrogen") - 0.2, P(X, 0, 240, 330), 3.0, 60, HORM)
    cv.glow(s.t("estrogen") - 0.2, P(X, 0, 760, 330), 3.0, 60, HORM)
    cv.push(s, Bc, 1.0, 1.9)
    cv.dive_out(s, P(X, 0, 240, 330), 4.0, 1.5)

    # ---------------- OVULATION (C): follicle bursts, fimbriae sweep the egg in
    s = sc["ovulation"]
    cv.land(s, C)
    bd.erase(s.start + 0.8, fe[:1])
    bd.erase(s.start - 1.0, fe[1:])
    X = 2 * PW
    ov = [pop(shot(3), X + 960, 540, w=1920, t=s.start), text("born with ALL her eggs", X + 1600, 150, 44, MAROON, s.t("born") - 0.3, "c"),
          text("1-2 MILLION", X + 1600, 250, 62, GOLD_T, s.t("million") - 0.4, "c"), text("FOLLICLE matures", X + 1600, 400, 52, PURPLE, s.t("follicle") - 0.4, "c"),
          text("OVULATION!", X + 1600, 540, 72, RED_T, s.t("ovulation") - 0.2, "c"), text("FIMBRIAE sweep it in", X + 1600, 680, 48, PLUM, s.t("fimbriae") - 0.4, "c"),
          text("lifetime: only a few HUNDRED", X + 1600, 850, 38, GREEN_T, s.t("hundred") - 2.2, "c")]
    for i, (x, y) in enumerate(((290, 330), (380, 290), (250, 410), (400, 520))):
        cv.glow(s.t("eggs") + 0.15 * i, P(X, 0, x, y), 1.6, 30, EGG)
    cv.glow(s.t("follicle") - 0.2, P(X, 0, 590, 400), 2.6, 95, (235, 110, 140))
    cv.flow([P(X, 0, x, y) for x, y in ((600, 400), (680, 390), (740, 385), (800, 330), (830, 250), (790, 160), (650, 130), (420, 140))],
            s.t("bursts") - 0.1, s.start + s.dur, 3.2, EGG, 16, 1)
    cv.glow(s.t("fimbriae") - 0.2, P(X, 0, 800, 320), 2.4, 80, PLUM)
    cv.push(s, C, 1.0)

    # ---------------- MALE (D): testis -> epididymis -> vas deferens
    s = sc["male"]
    cam(s.start, *D, 1.0, 1.2)
    bd.erase(s.start + 1.4, ov)
    ma = [pop(shot(4), 960, Y + 540, w=1920, t=s.start + 0.3), text("TESTES", 1600, Y + 130, 70, BLUE_T, s.t("testes") - 0.3, "c"),
          text("sperm + TESTOSTERONE", 1600, Y + 240, 44, MAROON, s.t("testosterone") - 0.4, "c"),
          text("SEMINIFEROUS TUBULES", 1600, Y + 370, 44, PURPLE, s.t("seminiferous") - 0.3, "c"), text("-> EPIDIDYMIS", 1600, Y + 480, 52, PLUM, s.t("epididymis") - 0.3, "c"),
          text("-> VAS DEFERENS", 1600, Y + 590, 52, BLUE_T, s.t("vas") - 0.3, "c"), text("a little COOLER", 1600, Y + 740, 54, GREEN_T, s.t("cooler") - 0.4, "c"),
          text("MILLIONS every day", 1600, Y + 870, 52, GOLD_T, s.t("millions") - 1.1, "c")]
    cv.glow(s.t("seminiferous") - 0.2, P(0, Y, 470, 450), 2.6, 150, SPERM)
    cv.flow([P(0, Y, x, y) for x, y in ((470, 450), (450, 300), (440, 220), (560, 215), (640, 320), (660, 520), (700, 580), (715, 420), (700, 250), (660, 100))],
            s.t("epididymis") - 0.4, s.start + s.dur, 3.0, SPERM, 10, 4)
    cv.push(s, D, 1.4)

    # ---------------- FERTILIZE (E): many sperm, only one gets in
    s = sc["fertilize"]
    cam(s.start, *E, 1.0, 1.2)
    bd.erase(s.start + 1.4, ma)
    X = PW
    fz = [pop(shot(5), X + 960, Y + 540, w=1920, t=s.start + 0.3), text("in the FALLOPIAN TUBE", X + 1600, Y + 160, 46, PURPLE, s.t("fallopian") - 0.4, "c"),
          text("only ONE gets in", X + 1600, Y + 320, 60, RED_T, s.t("one") - 0.3, "c"), text("outer layer BLOCKS", X + 1600, Y + 460, 52, MAROON, s.t("blocks") - 0.5, "c"),
          text("23 + 23 = 46", X + 1600, Y + 640, 72, GOLD_T, s.t("twenty") - 0.4, "c"), text("chromosomes", X + 1600, Y + 740, 44, MAROON, s.t("chromosomes") - 0.4, "c"),
          text("a brand NEW set", X + 1600, Y + 880, 54, GREEN_T, s.t("brand") - 0.4, "c")]
    for i, (x, y) in enumerate(((160, 300), (170, 470), (300, 180), (320, 620), (140, 390))):
        cv.flow([P(X, Y, x, y), P(X, Y, (x + 500) / 2, (y + 400) / 2), P(X, Y, 500 + (x - 500) * 0.22, 400 + (y - 400) * 0.22)], s.start + 0.6 + 0.2 * i, s.t("blocks"), 2.2, SPERM, 7, 2)
    cv.glow(s.t("one") - 0.2, P(X, Y, 580, 392), 2.4, 40, (255, 240, 200))
    cv.glow(s.t("blocks") - 0.3, P(X, Y, 500, 400), 3.0, 150, EGG)
    cv.glow(s.t("brand") - 0.3, P(X, Y, 500, 400), 2.6, 110, (255, 220, 120))
    cv.push(s, E, 1.4, 1.9)
    cv.dive_out(s, P(X, Y, 500, 400), 4.0, 1.5)

    # ---------------- IMPLANT (F): the blastocyst sinks into the lining
    s = sc["implant"]
    cv.land(s, Fp)
    bd.erase(s.start + 0.8, fz[:1])
    bd.erase(s.start - 1.0, fz[1:])
    X = 2 * PW
    im_ = [pop(shot(6), X + 960, Y + 540, w=1920, t=s.start), text("DIVIDES again and again", X + 1600, Y + 150, 42, PURPLE, s.t("divides") - 0.4, "c"),
           text("BLASTOCYST", X + 1600, Y + 290, 64, GOLD_T, s.t("blastocyst") - 0.3, "c"), text("6-10 days after", X + 1600, Y + 420, 50, MAROON, s.t("six") - 0.4, "c"),
           text("UTERINE LINING", X + 1600, Y + 560, 54, RED_T, s.t("lining") - 0.4, "c"), text("= IMPLANTATION", X + 1600, Y + 700, 60, PLUM, s.t("implantation") - 0.9, "c"),
           text("pregnancy begins", X + 1600, Y + 850, 54, GREEN_T, s.t("pregnancy") - 0.8, "c")]
    cv.glow(s.t("blastocyst") - 0.2, P(X, Y, 490, 400), 3.0, 110, EGG)
    cv.glow(s.t("lining") - 0.2, P(X, Y, 560, 300), 2.4, 160, (235, 110, 140))
    cv.glow(s.t("implantation") - 0.2, P(X, Y, 490, 400), 3.5, 130, EGG)
    cv.push(s, Fp, 1.0)

    # ---------------- CYCLE (A): no fertilization -> period
    s = sc["cycle"]
    cam(s.start, *A, 1.0, 1.2)
    bd.erase(s.start + 1.4, im_)
    cy = [pop(shot(2), 960, 540, w=1920, t=s.start + 0.3), text("no fertilized egg?", 1600, 200, 52, PURPLE, s.t("fertilized") - 0.4, "c"),
          text("hormones FALL", 1600, 360, 60, MAROON, s.t("fall") - 0.4, "c"), text("lining SHEDS", 1600, 500, 60, RED_T, s.t("sheds") - 0.4, "c"),
          text("= the PERIOD", 1600, 620, 60, RED_T, s.t("period") - 0.4, "c"), text("then it starts AGAIN", 1600, 800, 50, GREEN_T, s.t("again") - 1.6, "c")]
    cv.glow(s.t("sheds") - 0.2, P(0, 0, 500, 330), 3.0, 120, (220, 70, 80))
    cv.flow([P(0, 0, x, y) for x, y in ((500, 330), (500, 450), (500, 560), (500, 640))], s.t("sheds") - 0.1, s.t("again"), 1.6, (210, 60, 70), 9, 3)
    cv.push(s, A, 1.0)

    # ---------------- CARE (B)
    s = sc["care"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, cy)
    X = PW
    ca = [text("very painful or irregular periods", X + 960, 200, 56, RED_T, s.t("painful") - 0.4, "c"),
          text("a lump or pain in a testicle", X + 960, 340, 56, BLUE_T, s.t("lump") - 0.4, "c"),
          text("no pregnancy after 1 year of trying", X + 960, 480, 52, PURPLE, s.t("trouble") - 0.4, "c"),
          text("(6 months if over 35)", X + 960, 580, 46, MAROON, s.t("six") - 0.6, "c"),
          panel(X + 560, 700, X + 1360, 860, MINT, s.t("doctor") - 0.6), text("see a doctor", X + 960, 780, 70, GREEN_T, s.t("doctor") - 0.4, "c")]

    # ---------------- RECAP (C)
    s = sc["recap"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ca)
    X = 2 * PW
    rp = title("remember 3 things", X + 960, 100, s.start + 0.4)
    for w, a, b, col, tc_, x in (("ovaries", "ovaries -> eggs", "testes -> sperm", PINK, RED_T, 400), ("fertilization", "fertilization", "in the fallopian tube", CREAM, GOLD_T, 960),
                                 ("embryo", "the embryo implants", "in the uterus lining", LILAC, PURPLE, 1520)):
        tw2 = s.t(w) - 0.3
        rp += [panel(X + x - 265, 220, X + x + 265, 600, col, tw2 - 0.2), text(a, X + x, 360, 38, tc_, tw2, "c"), text(b, X + x, 470, 34, MAROON, tw2 + 0.6, "c")]
    tn = s.t("next") - 1.0
    rp += [panel(X + 200, 720, X + 1720, 890, LILAC, tn - 0.3), text("next: a new body story", X + 960, 820, 56, PURPLE, tn, "c")]

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
        a = [pop(shot(3), 960, 540, w=1920, t=0.0, dur=0.3), text("born with ALL her eggs", 1600, 260, 46, MAROON, s.t("born") - 0.4, "c"),
             text("1-2 MILLION", 1600, 420, 70, GOLD_T, s.t("million") - 0.6, "c")]
        for i, (x, y) in enumerate(((290, 330), (380, 290), (250, 410), (400, 520))):
            cv.glow(0.6 + 0.3 * i, P(0, 0, x, y), 2.0, 30, EGG)
        cv.push(s, A, 0.4, 0.2)
        s = sc["turn"]
        cam(s.start, *Bc, 1.0, 0.9)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(shot(3), X + 960, 540, w=1920, t=s.start + 0.2), text("most are NEVER used", X + 1600, 220, 48, RED_T, s.t("never") - 0.4, "c"),
             text("how many released?", X + 1600, 420, 52, GOLD_T, s.t("how") - 0.4, "c"), text("?", X + 1600, 680, 200, PURPLE, s.t("released") - 0.6, "c")]
        cv.flow([P(X, 0, x, y) for x, y in ((600, 400), (680, 390), (740, 385), (800, 330))], s.start + 0.4, s.start + s.dur, 2.0, EGG, 14, 1)
        cv.push(s, Bc, 0.6, 0.2)
    else:
        s = sc["case"]
        a = [pop(shot(5), 960, 540, w=1920, t=0.0, dur=0.3), text("MANY sperm", 1600, 260, 70, BLUE_T, s.t("many") - 0.3, "c"),
             text("reach the egg", 1600, 400, 56, MAROON, s.t("reach") - 0.4, "c")]
        for i, (x, y) in enumerate(((160, 300), (170, 470), (300, 180), (320, 620))):
            cv.flow([P(0, 0, x, y), P(0, 0, 500 + (x - 500) * 0.22, 400 + (y - 400) * 0.22)], 0.3 + 0.2 * i, s.start + s.dur, 1.6, SPERM, 7, 2)
        cv.push(s, A, 0.3, 0.2)
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 0.8)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(shot(5), X + 960, 540, w=1920, t=s.start + 0.1), text("only ONE gets in", X + 1600, 320, 62, RED_T, s.t("one") - 0.4, "c")]
        cv.glow(s.t("one") - 0.3, P(X, 0, 580, 392), 2.5, 40, (255, 240, 200))
        cv.push(s, Bc, 0.4, 0.2)
        s = sc["clue"]
        cam(s.start, *C, 1.0, 0.8)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        c = [pop(shot(5), X + 960, 540, w=1920, t=s.start + 0.1), text("what stops the others?", X + 1600, 300, 48, GOLD_T, s.t("stops") - 0.5, "c"),
             text("?", X + 1600, 640, 200, PURPLE, s.t("others") - 0.5, "c")]
        cv.glow(s.start + 0.4, P(X, 0, 500, 400), s.dur - 0.4, 140, EGG)
        cv.push(s, C, 0.3, 0.2)

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
            OF.credit(bd.frame(round(v.start + v.dur * 0.85, 1))).save(OUT / f"rp_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                OF.credit(bd.frame(round(v.start + v.dur * 0.85, 1))).save(OUT / f"rp_short{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "repro", intro=True)
        f.replace(OUT / "final_repro.mp4")
        print("done ->", OUT / "final_repro.mp4")
