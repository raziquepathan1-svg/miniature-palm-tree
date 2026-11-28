"""F1 THE CELL - smooth single-page cinematic build (owner images art/cell/shot2-7 + whole human art/ear/shot1).

New house style (owner, 27 Nov 2026):
  * SMOOTH TRANSITIONS: every picture dissolves into the next (cross-fade) while the camera glides; no cuts, no page slides.
  * LABELLED DIAGRAMS: every named part gets its name + a pointer line to the exact spot.
  * LOCATION FIRST: each organelle is first shown glowing inside the whole cell, the camera pushes in, then dissolves to its close-up.

    python3 osm_cell.py [stills] | short 1|2 [stills]
"""
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "cell")))
OUT = Path(os.environ.get("OUT_DIR", str(HERE)))
ART = HERE.parent / "art" / "cell"
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_brain as OB  # noqa: E402
import osm_neuron as NU  # noqa: E402
from osm_ear2 import Cine, P as P0  # noqa: E402

OF.credit = lambda frame: frame        # owner art only: no Servier credit line
MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
PINK, LILAC, CREAM, MINT = OB.PINK, OB.LILAC, OB.CREAM, OB.MINT
CR, XF = 26, 1.1                       # whiteboard frame crop; cross-fade seconds
LX = 1330                              # labels start here (right third of every shot is empty)
SHORT_TITLES = {1: "What Is Your Cell's Control Center", 2: "Your Cells Have Power Plants"}
SHORT_Q = {1: "So what is the control center called?", 2: "So what are these power plants called?"}
NUC, MITO, ER, GOLGI, LYSO, MEM, CYTO = (150, 110, 220), (240, 120, 60), (90, 140, 210), (90, 180, 120), (230, 190, 40), (70, 170, 170), (220, 170, 130)


def shot(n):
    if n == 1:
        return Image.open(HERE.parent / "art" / "ear" / "shot1.png").convert("RGBA")
    im = Image.open(ART / f"shot{n}.jpg").convert("RGBA")
    return im.crop((CR, CR, 1376 - CR, 768 - CR)).resize((1376, 768), Image.LANCZOS)


def P(x, y, n=2):
    """pixel of an ORIGINAL owner shot -> board units (single page). Shot 1 has no crop."""
    if n == 1:
        return P0(0, 0, x, y)
    return P0(0, 0, (x - CR) * 1376 / (1376 - 2 * CR), (y - CR) * 768 / (768 - 2 * CR))


def feather(im, edge=0.16):
    """soft edges so a growing inner picture melts into the one around it."""
    import numpy as np
    a = np.array(im.convert("RGBA"), dtype=np.float32)
    h, w = a.shape[:2]
    ex, ey = max(1, int(w * edge)), max(1, int(h * edge))
    rx = np.clip(np.minimum(np.arange(w), np.arange(w)[::-1]) / ex, 0, 1)
    ry = np.clip(np.minimum(np.arange(h), np.arange(h)[::-1]) / ey, 0, 1)
    a[..., 3] *= np.outer(ry, rx)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


class Stage:
    """one page; pictures cross-fade into each other; labels with pointer lines."""
    def __init__(self, bd, kit, cv):
        self.bd, self.cv = bd, cv
        self.text, self.sub, self.lead, self.pop, self.panel, self.title = kit
        self.img, self.labels = None, []
        self.pending = None                                           # a focus() waiting to become a zoom-through

    def picture(self, im, t, dur=XF):
        if self.pending is not None:
            ts, pt, cam_entry = self.pending
            self.pending = None
            if cam_entry in self.bd.cam and t + 0.6 - ts >= 1.0:
                self.bd.cam.remove(cam_entry)
                return self.zoom_through(im, pt, ts, t + 0.6)
        new = self.pop(im, 960, 540, w=1920, t=t, dur=dur)
        if self.img is not None:
            self.bd.erase(t + dur + 0.15, [self.img], 0.05)          # old picture removed only once the new one covers it
        self.img = new
        self.bd.camera(t, 960, 540, 1.0, dur + 0.4)                   # glide back to the full view while dissolving
        return new

    def clear(self, t):
        if self.labels:
            self.bd.erase(t, self.labels, 0.5)
        self.labels = []

    def say(self, s, x, y, size, col, t, anchor="l"):
        it = self.text(s, x, y, size, col, t, anchor)
        self.labels.append(it)
        return it

    def label(self, name, part, y, t, col, size=46):
        """NAME on the right with a pointer line ending in an arrow on the exact part."""
        tx = self.text(name, LX, y, size, col, t)
        ln = self.lead([(LX - 12, y - 4), ((LX - 12 + part[0]) / 2, y - 4 + (part[1] - y) * 0.2), part], t - 0.05, col, 4, 0.5, arrow=True)
        self.labels += [tx, ln]
        self.cv.glow(t + 0.3, part, 2.2, 40, col)
        return tx

    def focus(self, t_end, pt, z=1.35, d=1.6):
        """push in on a point; if a new picture follows, it becomes an INFINITE-ZOOM move into that point."""
        self.bd.camera(t_end - d, pt[0], pt[1], z, d)
        self.pending = (t_end - d, pt, (t_end - d, pt[0], pt[1], z, d))

    def zoom_through(self, im, pt, ts, te, Z=2.4):
        """owner's reference (27/28 Nov): keep diving into one point; the next, deeper picture grows out of it
        (feathered, centred on the point), then takes over the full frame seamlessly."""
        K = 1.12                                                      # inner picture a bit bigger than the view: its soft edges stay outside
        vw, vh = 1920 / Z, 1080 / Z
        cx = min(max(pt[0], vw * K / 2), 1920 - vw * K / 2)
        cy = min(max(pt[1], vh * K / 2), 1080 - vh * K / 2)
        dur = te - ts
        self.bd.camera(ts, cx, cy, Z, dur)
        small = self.pop(feather(im, 0.05), cx, cy, w=vw * K, t=ts + 0.2 * dur, dur=0.5 * dur)
        full = self.pop(im, 960, 540, w=1920, t=te, dur=0.02)
        self.bd.camera(te, 960, 540, K, 0)                            # identical view, now the full-resolution picture
        self.bd.camera(te + 0.02, 960, 540, 1.0, 1.3)                  # ...and settle back out to the whole picture
        gone = [small] + ([self.img] if self.img is not None else [])
        self.bd.erase(te + 0.06, gone, 0.02)
        self.img = full
        return full

    def drift(self, s, lead=1.4, tail=1.8):
        self.bd.camera(s.start + lead, 960, 540, 1.03, max(1.0, s.dur - lead - tail))


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

    # ---------------- STORY: the whole body -> push into the cheek
    s = sc["story"]
    g.picture(shot(1), 0.0, 0.4)
    g.say("30 TRILLION", 70, 230, 76, GOLD_T, s.t("thirty") - 0.3)
    g.say("cells build you", 70, 330, 50, MAROON, s.t("cells") - 0.3)
    g.say("too small to see", 70, 470, 46, PURPLE, s.t("small") - 0.3)
    g.say("each one ALIVE", 70, 570, 52, RED_T, s.t("alive") - 0.3)
    g.say("what's inside one?", 70, 760, 50, GREEN_T, s.t("inside") - 0.6)
    cheek = P(700, 78, 1)
    cv.glow(s.t("cells"), cheek, 3.0, 40, (240, 150, 170))
    g.clear(s.start + s.dur - 2.2)
    g.focus(s.start + s.dur, cheek, 2.6, 2.2)

    # ---------------- TISSUE: cheek cells
    s = sc["tissue"]
    g.picture(shot(2), s.start - 0.6)
    g.label("one CELL", P(400, 330), 220, s.t("cells") - 0.2, PURPLE)
    g.label("CELL MEMBRANE (border)", P(337, 300), 360, s.t("border") - 0.3, MEM, 40)
    g.label("NUCLEUS (dark spot)", P(372, 294), 500, s.t("dark") - 0.3, NUC, 42)
    g.say("cells join = TISSUE", LX, 700, 54, GREEN_T, s.t("tissues") - 0.8)
    for i, (x, y) in enumerate(((296, 254), (372, 294), (437, 385), (515, 360), (590, 300), (225, 335))):
        cv.glow(s.t("join") + 0.12 * i, P(x, y), 1.6, 30, NUC)
    g.drift(s)
    g.clear(s.start + s.dur - 1.7)
    g.focus(s.start + s.dur, P(372, 294), 1.45)

    # ---------------- OVERVIEW: one cell cut open
    s = sc["overview"]
    g.picture(shot(3), s.start - 0.6)
    g.say("ONE CELL, cut open", LX, 150, 56, MAROON, s.start + 0.6)
    g.say("ORGANELLES = tiny parts", LX, 300, 44, PURPLE, s.t("organelles") - 0.4)
    g.say("each with its own JOB", LX, 380, 44, GOLD_T, s.t("job") - 0.4)
    g.label("CYTOPLASM (jelly)", P(300, 560), 540, s.t("cytoplasm") - 0.3, CYTO, 44)
    for i, (x, y, c) in enumerate(((450, 345, NUC), (335, 195, MITO), (520, 255, ER), (365, 505, GOLGI), (380, 230, LYSO), (530, 145, MITO), (705, 395, MITO))):
        cv.glow(s.t("organelles") + 0.2 * i, P(x, y), 1.8, 45, c)
    g.say("from the outside in", LX, 760, 46, GREEN_T, s.t("outside") - 0.6)
    g.drift(s)
    g.clear(s.start + s.dur - 1.7)
    g.focus(s.start + s.dur, P(175, 420), 1.4)

    # ---------------- MEMBRANE
    s = sc["membrane"]
    g.picture(shot(7), s.start - 0.6)
    g.say("CELL MEMBRANE = gatekeeper", LX, 110, 40, MEM, s.t("membrane") - 0.3)
    g.label("PHOSPHOLIPID heads", P(330, 300, 7), 260, s.t("phospholipids") - 0.4, (220, 130, 90), 40)
    g.label("fatty tails (2 layers)", P(330, 420, 7), 380, s.t("layers") - 0.3, GOLD_T, 40)
    g.label("PROTEIN CHANNEL", P(420, 400, 7), 520, s.t("channels") - 0.3, MEM, 44)
    g.label("sugar chain", P(150, 175, 7), 640, s.t("channels") + 0.5, GREEN_T, 38)
    g.say("right things IN, wrong things OUT", LX, 800, 34, MAROON, s.t("keep") - 1.0)
    cv.flow([P(420, 120, 7), P(420, 330, 7), P(420, 480, 7), P(420, 640, 7)], s.t("let") - 0.2, s.start + s.dur, 1.8, (90, 170, 230), 11, 3)
    g.drift(s)
    g.clear(s.start + s.dur - 1.0)

    # ---------------- NUCLEUS: locate it in the cell, push in, dissolve to the close-up
    s = sc["nucleus"]
    g.picture(shot(3), s.start - 0.6)
    cv.glow(s.start + 0.2, P(450, 345), 2.4, 110, NUC)
    g.focus(s.start + 2.2, P(450, 345), 1.5, 1.8)
    tc = s.start + 2.0
    g.picture(shot(4), tc)
    g.say("NUCLEUS = control center", LX, 110, 40, NUC, s.t("control") - 0.3)
    g.label("DNA (chromatin)", P(300, 250, 4), 250, s.t("dna") - 0.3, PURPLE, 44)
    g.label("NUCLEAR PORES", P(212, 318, 4), 380, s.t("pores") - 0.4, MEM, 44)
    g.label("NUCLEOLUS", P(430, 372, 4), 510, s.t("nucleolus") - 0.2, NUC, 48)
    g.label("ROUGH ER + ribosomes", P(785, 450, 4), 640, s.t("ribosomes") - 0.6, ER, 38)
    g.say("red blood cells: NO nucleus", LX, 800, 34, RED_T, s.t("exception") - 1.2)
    g.drift(s, 3.4)
    g.clear(s.start + s.dur - 1.0)

    # ---------------- MITOCHONDRIA
    s = sc["mito"]
    g.picture(shot(3), s.start - 0.6)
    for x, y in ((335, 195), (530, 145), (255, 410), (705, 395), (510, 515)):
        cv.glow(s.start + 0.2, P(x, y), 2.4, 55, MITO)
    g.focus(s.start + 2.2, P(510, 515), 1.5, 1.8)
    tc = s.start + 2.0
    g.picture(shot(5), tc)
    g.say("MITOCHONDRIA = power plants", LX, 110, 36, MITO, s.t("power") - 0.3)
    g.say("oxygen + sugar -> ATP energy", LX, 220, 34, GOLD_T, s.t("atp") - 0.8)
    g.label("OUTER MEMBRANE", P(150, 330, 5), 380, s.t("membrane") - 0.6, MITO, 42)
    g.label("INNER FOLDS (cristae)", P(380, 232, 5), 510, s.t("folded") - 0.3, RED_T, 40)
    g.label("MATRIX", P(480, 330, 5), 640, s.t("space") - 0.3, GOLD_T, 46)
    g.say("has its OWN DNA!", LX, 800, 46, PURPLE, s.t("fun") - 0.2)
    cv.glow(s.t("atp") - 0.2, P(470, 330, 5), 3.0, 160, (250, 170, 80))
    g.drift(s, 3.4)
    g.clear(s.start + s.dur - 1.0)

    # ---------------- PROTEIN FACTORY
    s = sc["factory"]
    g.picture(shot(3), s.start - 0.6)
    cv.glow(s.start + 0.2, P(520, 255), 2.4, 70, ER)
    cv.glow(s.start + 0.4, P(365, 505), 2.2, 60, GOLGI)
    g.focus(s.start + 2.2, P(450, 380), 1.4, 1.8)
    tc = s.start + 2.0
    g.picture(shot(6), tc)
    g.say("the PROTEIN FACTORY", LX, 110, 46, MAROON, s.t("factory") - 0.2)
    g.label("RIBOSOMES (dots)", P(140, 515, 6), 250, s.t("ribosomes") - 0.3, PURPLE, 42)
    g.label("ROUGH ER", P(260, 320, 6), 380, s.t("rough") - 0.3, ER, 48)
    g.label("VESICLES (bubbles)", P(510, 380, 6), 510, s.t("bubbles") - 0.3, GOLD_T, 42)
    g.label("GOLGI APPARATUS", P(660, 410, 6), 640, s.t("golgi") - 0.3, GOLGI, 44)
    g.say("sorts, packs + SHIPS", LX, 790, 46, GREEN_T, s.t("ships") - 0.6)
    cv.flow([P(x, y, 6) for x, y in ((430, 360), (480, 385), (520, 385), (560, 375), (610, 400), (700, 420), (760, 470), (810, 470), (860, 495))],
            s.t("bubbles") - 0.2, s.start + s.dur, 3.0, (240, 220, 150), 12, 3)
    g.drift(s, 3.4)
    g.clear(s.start + s.dur - 1.0)

    # ---------------- LYSOSOMES
    s = sc["cleaners"]
    g.picture(shot(3), s.start - 0.6)
    g.say("LYSOSOMES = clean-up crew", LX, 150, 38, LYSO, s.t("lysosomes") - 0.2)
    for i, (x, y) in enumerate(((255, 285), (380, 230), (630, 250), (680, 345), (475, 545))):
        it = g.lead([(LX - 12, 300), ((LX - 12 + P(x, y)[0]) / 2, 300 + (P(x, y)[1] - 300) * 0.3), P(x, y)], s.t("lysosomes") + 0.15 * i, LYSO, 3, 0.45, arrow=True)
        g.labels.append(it)
        cv.glow(s.t("enzymes") + 0.1 * i, P(x, y), 2.4, 40, LYSO)
    g.say("strong ENZYMES", LX, 400, 48, RED_T, s.t("enzymes") - 0.3)
    g.say("break down waste", LX, 500, 46, MAROON, s.t("waste") - 0.4)
    g.say("+ worn-out parts", LX, 590, 46, MAROON, s.t("worn") - 0.4)
    g.drift(s, 0.8, 0.8)
    g.clear(s.start + s.dur - 0.6)

    # ---------------- RECAP: the whole cell with every part named
    s = sc["recap"]
    rows = (("membrane", "MEMBRANE guards", P(175, 420), MEM), ("nucleus", "NUCLEUS controls", P(450, 345), NUC),
            ("mitochondria", "MITOCHONDRIA = energy", P(705, 395), MITO), ("ribosomes", "RIBOSOMES build", P(520, 255), ER),
            ("golgi", "GOLGI ships", P(365, 505), GOLGI))
    for i, (w, name, pt, col) in enumerate(rows):
        g.label(name, pt, 140 + i * 120, s.t(w) - 0.3, col, 40)
    tn = s.t("next") - 1.0
    g.labels.append(g.panel(LX - 30, 760, 1900, 900, LILAC, tn - 0.3))
    g.say("next: how DNA makes proteins", LX, 830, 34, PURPLE, tn)
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
        g.picture(shot(2), 0.0, 0.3)
        g.say("30 TRILLION cells", LX, 260, 54, GOLD_T, s.t("thirty") - 0.3)
        g.say("each has a CONTROL CENTER", LX, 400, 36, MAROON, s.t("control") - 0.6)
        for i, (x, y) in enumerate(((296, 254), (372, 294), (437, 385), (515, 360), (590, 300))):
            cv.glow(s.t("control") - 0.4 + 0.1 * i, P(x, y), 2.0, 30, NUC)
        g.clear(s.start + s.dur - 0.6)
        g.focus(s.start + s.dur, P(372, 294), 1.4, 1.2)
        s = sc["turn"]
        g.picture(shot(4), s.start - 0.5, 0.9)
        g.label("holds your DNA", P(300, 250, 4), 260, s.t("dna") - 0.3, PURPLE, 44)
        g.say("tells the cell what to do", LX, 420, 36, MAROON, s.t("tells") - 0.3)
        g.say("?", LX + 200, 680, 200, PURPLE, s.t("called") - 0.6)
        cv.glow(s.start + 0.3, P(430, 372, 4), s.dur - 0.3, 150, NUC)
    else:
        s = sc["case"]
        g.picture(shot(3), 0.0, 0.3)
        g.say("your cells need ENERGY", LX, 300, 40, GOLD_T, s.t("energy") - 0.4)
        g.say("every second", LX, 420, 46, MAROON, s.t("every") - 0.2)
        g.clear(s.start + s.dur - 0.5)
        s = sc["twist"]
        for x, y in ((335, 195), (530, 145), (255, 410), (705, 395), (510, 515)):
            cv.glow(s.start, P(x, y), s.dur, 55, MITO)
        g.say("tiny POWER PLANTS", LX, 280, 50, MITO, s.t("power") - 0.4)
        g.say("with their OWN DNA", LX, 420, 46, PURPLE, s.t("dna") - 0.6)
        g.clear(s.start + s.dur - 0.5)
        g.focus(s.start + s.dur, P(510, 515), 1.4, 1.2)
        s = sc["clue"]
        g.picture(shot(5), s.start - 0.4, 0.8)
        g.say("what are they called?", LX, 300, 44, GOLD_T, s.t("what") - 0.3)
        g.say("?", LX + 200, 640, 200, PURPLE, s.t("called") - 0.5)
        cv.glow(s.start + 0.2, P(470, 330, 5), s.dur, 170, (250, 170, 80))

    bd.fx.append(cv.fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def make_short(n):
    import package as Pk
    import bridge
    bd, sc = build_short(n)
    board = NU.render_board(bd, sc, f"cell_story{n}")
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
    ov = OUT / f"cell_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"cell_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["cell"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "cell", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            for fr in (0.5, 0.92):
                bd.frame(round(v.start + v.dur * fr, 1)).save(OUT / f"c_{v.id}_{int(fr * 100)}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                bd.frame(round(v.start + v.dur * 0.85, 1)).save(OUT / f"c_short{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "cell", intro=True)
        f.replace(OUT / "final_cell.mp4")
        print("done ->", OUT / "final_cell.mp4")
