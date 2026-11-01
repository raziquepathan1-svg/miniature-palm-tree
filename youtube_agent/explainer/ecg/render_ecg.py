"""Video 1: The Heart's Electrical System. Our colour line-art heart (no blood-flow arrows) with the conduction
system drawn on in gold, an electrical pulse travelling along it, chambers flashing when they contract, an ECG
that draws itself, and a branded intro. Timings come from word positions in the narration."""
import json
import math
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "heart"))
import lineart as LA  # noqa: E402
import render as R  # noqa: E402
import render3 as V3  # noqa: E402
from render import BG, BLUE_D, GOLD, GRAY, INK, MAROON, RED_D, SS, FPS, H, W, Scene, layer, text  # noqa: E402
from render3 import View, header, item  # noqa: E402

CX0 = 900
NAVY0, NAVY1 = (9, 22, 48), (24, 52, 110)
WIRE = (246, 178, 40)
WIRE_D = (120, 72, 0)
SPARK = (255, 247, 205)
GOLD_T = (176, 112, 0)
FLASH = (255, 255, 255)


def F(p):
    return ((p[0] + LA.DX) * SS - CX0, p[1] * SS)


img, _ = LA.draw(BG, arrows=False)
V3.FIG["heart"] = img.convert("RGB").crop((CX0, 0, CX0 + 1800, H * SS))

SEG = {
    "internodal": [(598, 462), (650, 540), (705, 600), (752, 628)],
    "his": [(752, 628), (800, 668), (866, 712)],
    "rbb": [(866, 712), (858, 800), (846, 890), (812, 948)],
    "lbb": [(866, 712), (878, 800), (894, 900), (930, 972)],
    "rpk": [(812, 948), (760, 962), (708, 910), (676, 830)],
    "lpk": [(930, 972), (995, 985), (1060, 915), (1098, 800), (1102, 700)],
}
SEG = {k: [F(p) for p in v] for k, v in SEG.items()}
NODES = {"SA": F((598, 462)), "AV": F((752, 628))}
ALL_SEGS = list(SEG)
ROUTE_R = SEG["his"] + SEG["rbb"][1:] + SEG["rpk"][1:]
ROUTE_L = SEG["his"] + SEG["lbb"][1:] + SEG["lpk"][1:]


def chamber_layer(shape):
    m = LA.mask_of([LA.blob(shape)])[:, CX0:CX0 + 1800]
    a = np.zeros(m.shape + (4,), "uint8")
    a[m] = FLASH + (255,)
    return Image.fromarray(a, "RGBA")


CH = {"RA": chamber_layer(LA.RA), "LA": chamber_layer(LA.LA), "RV": chamber_layer(LA.RV), "LV": chamber_layer(LA.LV)}
GROUP = {"atria": ["RA", "LA"], "ventricles": ["RV", "LV"], "RA": ["RA"], "LA": ["LA"]}

TAGS = {
    "SA": ("SA node", (598, 462), (-190, -70), GOLD_T),
    "AV": ("AV node", (752, 628), (-230, 70), GOLD_T),
    "His": ("Bundle of His", (800, 668), (-250, 150), GOLD_T),
    "BB": ("Bundle branches", (870, 800), (150, 40), GOLD_T),
    "PK": ("Purkinje fibers", (1060, 915), (110, 70), GOLD_T),
    "RA": ("Right atrium", (650, 520), (-200, 10), BLUE_D),
    "LA": ("Left atrium", (1035, 515), (150, -40), RED_D),
    "RV": ("Right ventricle", (735, 850), (-210, 60), BLUE_D),
    "LV": ("Left ventricle", (1010, 800), (130, 60), RED_D),
    "SVC": ("Superior vena cava", (650, 380), (-170, -60), BLUE_D),
    "septum": ("Septum", (866, 860), (70, 140), MAROON),
}

FULL = (60, 0, 1800, 2160)
SA_Z = (60, 560, 1060, 1410)
AV_Z = (350, 860, 1450, 1795)
V_Z = (200, 1000, 1700, 2160)
ATRIA_Z = (60, 600, 1800, 1500)


# ------------------------------------------------------------------ helpers
def cum(pts):
    out = [0.0]
    for a, b in zip(pts, pts[1:]):
        out.append(out[-1] + math.dist(a, b))
    return out


def partial(pts, frac):
    L = cum(pts)
    lim = L[-1] * max(0.0, min(1.0, frac))
    out = [pts[0]]
    for i in range(1, len(pts)):
        if L[i] <= lim:
            out.append(pts[i])
        else:
            t = (lim - L[i - 1]) / max(L[i] - L[i - 1], 1e-6)
            out.append((pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * t, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * t))
            break
    return out


def point_at(pts, frac):
    return partial(pts, frac)[-1]


def ramp(t, t0, dur):
    return max(0.0, min(1.0, (t - t0) / max(dur, 1e-3)))


def view_layer(lay, view, u):
    x0, y0, x1, y1, k, ox, oy = view.transform(u)
    crop = lay.crop((int(x0), int(y0), int(x1), int(y1)))
    crop = crop.resize((max(1, int((x1 - x0) * k)), max(1, int((y1 - y0) * k))), Image.BILINEAR)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(crop, (int(ox), int(oy)))
    return out


WAVE = []
for i in range(201):
    x = i / 200
    y = 0.0
    if 0.08 <= x <= 0.18:
        y = -0.13 * math.sin(math.pi * (x - 0.08) / 0.10)
    elif 0.26 <= x <= 0.28:
        y = 0.10 * (x - 0.26) / 0.02
    elif 0.28 < x <= 0.31:
        y = 0.10 - 1.10 * (x - 0.28) / 0.03
    elif 0.31 < x <= 0.34:
        y = -1.0 + 1.28 * (x - 0.31) / 0.03
    elif 0.34 < x <= 0.37:
        y = 0.28 - 0.28 * (x - 0.34) / 0.03
    elif 0.50 <= x <= 0.70:
        y = -0.26 * math.sin(math.pi * (x - 0.50) / 0.20)
    WAVE.append((x, y))


def wave_y(x):
    x = max(0.0, min(1.0, x))
    return WAVE[min(200, int(round(x * 200)))][1]


# ------------------------------------------------------------------ scenes
class EScene(Scene):
    def __init__(self, sid, text_):
        self.id, self.text = sid, text_
        self.audio = HERE / "audio" / f"{sid}.wav"
        self.dur = R.dur(self.audio)
        self.words = text_.lower().replace(",", "").replace(".", "").replace("?", "").split()
        self.items, self.dyn = [], []
        self.shown, self.nodes, self.reveals, self.flashes, self.pulses = set(), [], [], [], []
        self.tags, self.views, self.rings, self.dead = [], [], [], None
        self.ecg = None
        self.strip = None

    def beat(self, tb, P, origin="SA"):
        if origin == "SA":
            self.rings.append((tb, "SA"))
            self.pulses.append((SEG["internodal"], tb, 0.25 * P))
            self.flashes.append(("atria", tb + 0.08 * P, 0.35 * P))
        else:
            self.rings.append((tb, "AV"))
        self.pulses.append((ROUTE_R, tb + 0.40 * P, 0.22 * P))
        self.pulses.append((ROUTE_L, tb + 0.40 * P, 0.22 * P))
        self.flashes.append(("ventricles", tb + 0.55 * P, 0.35 * P))

    def beats(self, t0, t1, P, origin="SA"):
        tb = t0
        while tb < t1 - 0.2:
            self.beat(tb, P, origin)
            tb += P


def hv(a, b=None):
    return View("heart", a, b)


def build():
    sc = {s["id"]: EScene(s["id"], s["text"]) for s in json.load(open(HERE / "script.json"))}

    s = sc["hook"]
    s.views = [(0, hv(FULL, (160, 120, 1760, 2100)))]
    s.add(0, header("ELECTRICAL SYSTEM", "How every heartbeat starts"))
    s.add(s.t("hundred"), item(330, "≈ 100,000", RED_D, size=72, weight=800))
    s.add(s.t("hundred"), item(430, "heartbeats every day", INK, size=34, weight=500))
    s.add(s.t("spark"), item(540, "Each beat starts with", INK, size=34, weight=500))
    s.add(s.t("spark"), item(595, "an electrical spark", GOLD_T, size=40, weight=800))
    s.add(0, lambda d: text(d, (1250, 1000), "Educational content only, not medical advice.", 22, GRAY, 500))
    s.nodes.append(("SA", s.t("spark")))
    s.rings.append((s.t("spark"), "SA"))
    t0 = s.t("spread")
    for k in ALL_SEGS:
        s.reveals.append((k, t0, 2.4))
    s.nodes.append(("AV", t0 + 0.6))
    s.beats(t0 + 2.6, s.dur, 0.85)

    s = sc["why"]
    s.views = [(0, hv(FULL))]
    s.shown = set(ALL_SEGS)
    s.nodes += [("SA", 0), ("AV", 0)]
    s.add(0, header("BUILT-IN WIRING", "The conduction system"))
    s.add(s.t("brain"), item(300, "No signal needed from the brain", size=30))
    s.add(s.t("makes"), item(370, "Makes its own electrical signals", size=30))
    s.add(s.t("atria", 1), item(470, "1  Atria squeeze first", BLUE_D, size=32))
    s.add(s.t("ventricles", 1), item(540, "2  Ventricles squeeze right after", RED_D, size=32))
    s.flashes.append(("atria", s.t("atria", 1), 1.6))
    s.tags += [(s.t("atria", 1), "RA"), (s.t("atria", 1), "LA")]
    s.flashes.append(("ventricles", s.t("ventricles", 1), 1.8))
    s.tags += [(s.t("ventricles", 1), "RV"), (s.t("ventricles", 1), "LV")]
    s.beat(s.t("wiring"), 1.6)

    s = sc["sa"]
    s.views = [(0, hv(FULL, SA_Z))]
    s.add(0, header("SA NODE", "The natural pacemaker"))
    s.add(s.t("cluster"), item(300, "Small cluster of special cells", size=30))
    s.add(s.t("right"), item(370, "In the wall of the right atrium", size=30))
    s.add(s.t("pacemaker"), item(440, "Starts every heartbeat", GOLD_T, size=32))
    s.add(s.t("sixty"), item(540, "60–100", RED_D, size=64, weight=800))
    s.add(s.t("sixty"), item(625, "times a minute at rest", INK, size=32, weight=500))
    s.nodes.append(("SA", s.t("sinoatrial")))
    s.tags += [(s.t("sinoatrial"), "SA"), (s.t("right"), "RA"), (s.t("superior"), "SVC")]
    s.rings += [(s.t("sinoatrial"), "SA"), (s.t("pacemaker"), "SA")]
    tb = s.t("sixty")
    while tb < s.dur - 0.3:
        s.rings.append((tb, "SA"))
        tb += 0.8

    s = sc["atria"]
    s.views = [(0, hv(SA_Z, ATRIA_Z))]
    s.nodes.append(("SA", 0))
    s.add(0, header("ATRIA CONTRACT"))
    s.add(s.t("spreads"), item(300, "Signal spreads across both atria", size=30))
    s.add(s.t("contract"), item(370, "The atria contract", BLUE_D, size=32))
    s.add(s.t("top"), item(440, "-> top up the ventricles with blood", INK, size=30, weight=500))
    s.rings.append((s.t("spreads"), "SA"))
    s.flashes += [("RA", s.t("spreads") + 0.2, 2.8), ("LA", s.t("spreads") + 0.7, 2.3)]
    s.tags += [(s.t("spreads") + 0.2, "RA"), (s.t("spreads") + 0.7, "LA")]
    s.flashes.append(("atria", s.t("contract"), 2.0))

    s = sc["av"]
    s.views = [(0, hv(ATRIA_Z, AV_Z))]
    s.nodes.append(("SA", 0))
    s.add(0, header("AV NODE", "Between atria and ventricles"))
    s.add(s.t("atrioventricular"), item(300, "Atrioventricular (AV) node", GOLD_T, size=32))
    s.add(s.t("delayed"), item(380, "The signal is briefly delayed", size=30))
    s.add(s.t("emptying"), item(450, "Atria finish emptying", BLUE_D, size=30))
    s.add(s.t("full"), item(520, "Ventricles are full before they squeeze", RED_D, size=30))
    s.reveals.append(("internodal", s.t("signal", 1), 1.4))
    s.pulses.append((SEG["internodal"], s.t("signal", 1), 1.4))
    s.nodes.append(("AV", s.t("atrioventricular")))
    s.tags.append((s.t("atrioventricular"), "AV"))
    tb = s.t("delayed")
    while tb < s.t("delayed") + 3.0:
        s.rings.append((tb, "AV"))
        tb += 0.5
    s.flashes.append(("atria", s.t("emptying"), 1.8))

    s = sc["his"]
    s.views = [(0, hv(AV_Z, V_Z))]
    s.shown = {"internodal"}
    s.nodes += [("SA", 0), ("AV", 0)]
    s.add(0, header("TO THE VENTRICLES"))
    s.add(s.t("bundle", 1), item(300, "1  Bundle of His", GOLD_T, size=32))
    s.add(s.t("branches"), item(370, "2  Right & left bundle branches", GOLD_T, size=32))
    s.add(s.t("purkinje"), item(440, "3  Purkinje fibers", GOLD_T, size=32))
    s.add(s.t("contract"), item(540, "Both ventricles contract together", RED_D, size=30))
    s.reveals.append(("his", s.t("rushes"), 1.2))
    s.pulses.append((SEG["his"], s.t("rushes"), 1.2))
    s.tags.append((s.t("bundle", 1), "His"))
    s.reveals += [("rbb", s.t("splits"), 1.6), ("lbb", s.t("splits"), 1.6)]
    s.tags += [(s.t("branches"), "BB"), (s.t("septum"), "septum")]
    s.reveals += [("rpk", s.t("purkinje"), 1.8), ("lpk", s.t("purkinje"), 1.8)]
    s.tags.append((s.t("purkinje"), "PK"))
    s.pulses += [(ROUTE_R, s.t("purkinje") - 0.6, 2.4), (ROUTE_L, s.t("purkinje") - 0.6, 2.4)]
    s.flashes.append(("ventricles", s.t("contract"), 2.6))
    s.beats(s.t("lungs"), s.dur, 0.9)

    s = sc["backup"]
    s.views = [(0, hv(FULL))]
    s.shown = set(ALL_SEGS)
    s.nodes += [("SA", 0), ("AV", 0)]
    s.dead = s.t("fails")
    s.add(0, header("BACKUP PACEMAKERS"))
    s.add(0, item(300, "SA node      60–100 / min", GOLD_T, size=32))
    s.add(s.t("take"), item(380, "AV node      40–60 / min", GOLD_T, size=32))
    s.add(s.t("twenty"), item(460, "Ventricles   20–40 / min", RED_D, size=32))
    s.add(s.t("slower"), item(560, "Slower, but blood keeps moving", INK, size=30, weight=500))
    s.tags += [(s.t("fails"), "SA"), (s.t("take"), "AV")]
    s.beats(s.t("take"), s.t("twenty"), 1.2, origin="AV")
    s.flashes.append(("ventricles", s.t("twenty"), 2.0))
    s.tags += [(s.t("twenty"), "RV"), (s.t("twenty"), "LV")]

    s = sc["ecg"]
    s.views = [(0, hv(FULL, (60, 300, 1800, 2160)))]
    s.shown = set(ALL_SEGS)
    s.nodes += [("SA", 0), ("AV", 0)]
    s.add(0, header("THE ECG", "Electrocardiogram"))
    tP, tQ, tT = s.t("wave", 1), s.t("complex"), s.t("wave", 2)
    s.ecg = [(s.t("electrocardiogram"), 0.0), (s.t("electrocardiogram") + 0.8, 0.07), (tP - 0.3, 0.07), (tP + 0.9, 0.21),
             (tQ - 0.4, 0.21), (tQ + 0.6, 0.42), (tT - 0.3, 0.42), (tT + 1.4, 1.0)]
    s.ecg_t = (tP, tQ, tT)
    s.add(tP, item(700, "P wave  =  atria activated", BLUE_D, size=30))
    s.add(tQ, item(765, "QRS  =  ventricles activated", RED_D, size=30))
    s.add(tT, item(830, "T wave  =  ventricles recovering", MAROON, size=30))
    s.rings.append((tP, "SA"))
    s.pulses.append((SEG["internodal"], tP, 0.6))
    s.flashes.append(("atria", tP + 0.2, 1.4))
    s.pulses += [(ROUTE_R, tQ - 0.2, 0.8), (ROUTE_L, tQ - 0.2, 0.8)]
    s.flashes.append(("ventricles", tQ + 0.3, 1.8))

    s = sc["nerves"]
    s.views = [(0, hv(FULL))]
    s.shown = set(ALL_SEGS)
    s.nodes += [("SA", 0), ("AV", 0)]
    s.add(0, header("CHANGING THE PACE"))
    s.add(s.t("exercise"), item(300, "Exercise / stress", RED_D, size=32))
    s.add(s.t("sympathetic"), item(360, "Sympathetic nerves  ->  faster", INK, size=30, weight=500))
    s.add(s.t("rest"), item(450, "Rest", BLUE_D, size=32))
    s.add(s.t("vagus"), item(510, "Vagus nerve  ->  slower", INK, size=30, weight=500))
    tr = s.t("rest")
    s.strip = []
    tb = -2.0
    while tb < s.dur:
        P = 0.55 if tb < tr else 1.1
        s.strip.append((tb, P))
        if tb >= 0:
            s.beat(tb, P)
        tb += P
    s.strip_rest = tr

    s = sc["summary"]
    s.views = [(0, hv((160, 120, 1760, 2100), FULL))]
    s.add(0, header("SUMMARY"))
    steps = [("node", 1, "1  SA node", GOLD_T), ("atria", 1, "2  Atria", BLUE_D), ("node", 2, "3  AV node", GOLD_T),
             ("bundle", 1, "4  Bundle of His", GOLD_T), ("branches", 1, "5  Bundle branches", GOLD_T),
             ("purkinje", 1, "6  Purkinje fibers", GOLD_T), ("ventricles", 1, "7  Ventricles", RED_D)]
    for i, (w, n, line, col) in enumerate(steps):
        s.add(s.t(w, n), item(290 + i * 58, line, col, size=30))
    s.nodes.append(("SA", s.t("node", 1)))
    s.tags.append((s.t("node", 1), "SA"))
    s.flashes.append(("atria", s.t("atria"), 1.2))
    s.reveals.append(("internodal", s.t("node", 2) - 0.8, 0.8))
    s.nodes.append(("AV", s.t("node", 2)))
    s.tags.append((s.t("node", 2), "AV"))
    s.reveals.append(("his", s.t("bundle"), 0.8))
    s.reveals += [("rbb", s.t("branches"), 0.8), ("lbb", s.t("branches"), 0.8)]
    s.reveals += [("rpk", s.t("purkinje"), 0.9), ("lpk", s.t("purkinje"), 0.9)]
    s.flashes.append(("ventricles", s.t("ventricles"), 1.2))
    s.beats(s.t("spark"), s.t("next"), 0.85)
    s.add(s.t("next"), item(720, "NEXT VIDEO:", GOLD, size=30, weight=800))
    s.add(s.t("next"), item(770, "What happens in a heart attack", INK, size=30))
    s.add(0, lambda d: text(d, (1250, 1000), "Educational content only, not medical advice.", 22, GRAY, 500))
    return [sc[k] for k in ("hook", "why", "sa", "atria", "av", "his", "backup", "ecg", "nerves", "summary")]


# ------------------------------------------------------------------ drawing
def tag(d, view, u, key, a):
    name, tgt, (ox, oy), col = TAGS[key]
    x, y, k = view.map(u, F(tgt))
    f = R.F(26, 700)
    tw = d.textlength(name, font=f) / SS
    bx = x + ox
    bx = min(max(bx, 40 + (tw + 28 if ox < 0 else 0)), 1220 - (0 if ox < 0 else tw + 28))
    by = min(max(y + oy, 60), 1010)
    x0, x1 = (bx - tw - 28, bx) if ox < 0 else (bx, bx + tw + 28)
    edge = (x1 if ox < 0 else x0, by)
    c = lambda col_: R.mix((255, 255, 255), col_, a)
    d.line([(x * SS, y * SS), (edge[0] * SS, edge[1] * SS)], fill=c(INK), width=3 * SS)
    r = 6 * SS
    d.ellipse((x * SS - r, y * SS - r, x * SS + r, y * SS + r), fill=c(INK))
    d.rounded_rectangle((x0 * SS, (by - 22) * SS, x1 * SS, (by + 22) * SS), radius=12 * SS, fill=(255, 255, 255),
                        outline=c(col), width=4 * SS)
    d.text(((x0 + x1) / 2 * SS, by * SS), name, font=f, fill=c(col), anchor="mm")


def draw_wire(d, view, u, pts, frac):
    q = [view.map(u, p)[:2] for p in partial(pts, frac)]
    k = view.map(u, pts[0])[2]
    w = max(5, int(16 * k))
    if len(q) > 1:
        d.line(q, fill=WIRE_D, width=w + 6, joint="curve")
        d.line(q, fill=WIRE, width=w, joint="curve")


def draw_node(d, view, u, key, a=1.0, dead=False):
    x, y, k = view.map(u, NODES[key])
    r = max(9, 26 * k)
    fill = (150, 150, 150) if dead else R.mix(BG, WIRE, a)
    d.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=R.mix(BG, WIRE_D, a), width=4)
    if dead:
        d.line([(x - r, y - r), (x + r, y + r)], fill=(200, 30, 30), width=6)
        d.line([(x - r, y + r), (x + r, y - r)], fill=(200, 30, 30), width=6)


def draw_spark(d, x, y, k):
    r = max(8, 22 * k)
    d.ellipse((x - 1.8 * r, y - 1.8 * r, x + 1.8 * r, y + 1.8 * r), outline=WIRE, width=4)
    d.ellipse((x - r, y - r, x + r, y + r), fill=SPARK, outline=WIRE_D, width=3)


def draw_frame(s, t, settled, fading):
    frame = Image.new("RGB", (W, H), BG)
    u = t / max(s.dur, 1e-3)
    view = [v for t0, v in s.views if t >= t0 - 1e-6][-1]
    view.draw(frame, u)
    out = frame.convert("RGBA")
    # chamber flashes
    inten = {}
    for grp, t0, dur in s.flashes:
        if t0 <= t <= t0 + dur:
            x = (t - t0) / dur
            a = min(1.0, x / 0.2) * min(1.0, (1 - x) / 0.35)
            for c in GROUP[grp]:
                inten[c] = max(inten.get(c, 0), a)
    for c, a in inten.items():
        if a > 0.02:
            lay = view_layer(CH[c], view, u)
            lay.putalpha(lay.getchannel("A").point(lambda v, a=a: int(v * 0.5 * a)))
            out.alpha_composite(lay)
    d = ImageDraw.Draw(out)
    # wiring
    for k in ALL_SEGS:
        frac = 1.0 if k in s.shown else 0.0
        for kk, t0, dur in s.reveals:
            if kk == k and t >= t0:
                frac = max(frac, ramp(t, t0, dur))
        if frac > 0:
            draw_wire(d, view, u, SEG[k], frac)
    for key, t0 in s.nodes:
        if t >= t0:
            draw_node(d, view, u, key, ramp(t, t0, 0.3), dead=(key == "SA" and s.dead is not None and t >= s.dead))
    for t0, key in s.rings:
        if t0 <= t <= t0 + 0.7:
            x, y, k = view.map(u, NODES[key])
            x_ = (t - t0) / 0.7
            r = max(9, 26 * k) * (1 + 2.2 * x_)
            d.ellipse((x - r, y - r, x + r, y + r), outline=R.mix(BG, WIRE, 1 - x_), width=5)
    for pts, t0, dur in s.pulses:
        if t0 <= t <= t0 + dur:
            px, py = point_at(pts, (t - t0) / dur)
            x, y, k = view.map(u, (px, py))
            draw_spark(d, x, y, k)
    # ECG drawn in the panel
    if s.ecg:
        keys = s.ecg
        prog = keys[-1][1] if t >= keys[-1][0] else 0.0
        for (ta, pa), (tb, pb) in zip(keys, keys[1:]):
            if ta <= t < tb:
                prog = pa + (pb - pa) * (t - ta) / max(tb - ta, 1e-3)
                break
        X0, X1, Y0, A = 1260, 1860, 590, 200
        d.line([(X0, Y0 + 60), (X1, Y0 + 60)], fill=(230, 226, 220), width=2)
        for gx in range(X0, X1 + 1, 30):
            d.line([(gx, Y0 - 190), (gx, Y0 + 60)], fill=(246, 232, 232), width=1)
        for gy in range(Y0 - 190, Y0 + 61, 30):
            d.line([(X0, gy), (X1, gy)], fill=(246, 232, 232), width=1)
        if prog > 0:
            pts = [(X0 + x * (X1 - X0), Y0 + y * A) for x, y in WAVE if x <= prog]
            if len(pts) > 1:
                d.line(pts, fill=INK, width=5, joint="curve")
        tP, tQ, tT = s.ecg_t
        f = R.F(30, 800)
        for tl, lab, xx, col in ((tP, "P", 0.13, BLUE_D), (tQ, "QRS", 0.31, RED_D), (tT, "T", 0.60, MAROON)):
            if t >= tl + 0.3:
                yy = Y0 + wave_y(xx) * A - 40
                d.text((X0 + xx * (X1 - X0), yy), lab, font=R.visuals.font(30, 800), fill=col, anchor="mb")
    if s.strip:
        X0, X1, Y0, A, win = 1260, 1860, 760, 150, 3.0
        d.rounded_rectangle((X0 - 10, Y0 - 190, X1 + 10, Y0 + 50), radius=14, fill=(250, 246, 240), outline=(230, 222, 212))
        pts = []
        for i in range(0, X1 - X0 + 1, 3):
            tt = t - win + win * i / (X1 - X0)
            y = 0.0
            for tb, P in s.strip:
                if tb <= tt < tb + P:
                    y = wave_y((tt - tb) / P)
                    break
            pts.append((X0 + i, Y0 + y * A))
        d.line(pts, fill=(200, 40, 60), width=4, joint="curve")
        bpm = "≈ 110 beats / min" if t < s.strip_rest else "≈ 55 beats / min"
        d.text((X0, Y0 + 70), bpm, font=R.visuals.font(30, 800), fill=RED_D if t < s.strip_rest else BLUE_D)
    out2 = out
    if s.tags:
        tl = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        td = ImageDraw.Draw(tl)
        for t0, key in s.tags:
            if t >= t0:
                tag(td, view, u, key, min(1.0, (t - t0) / 0.35))
        out2.alpha_composite(tl.resize((W, H), Image.LANCZOS))
    out2.alpha_composite(settled)
    for lay, a in fading:
        tmp = lay.copy()
        tmp.putalpha(tmp.getchannel("A").point(lambda v, a=a: int(v * a)))
        out2.alpha_composite(tmp)
    return out2.convert("RGB")


# ------------------------------------------------------------------ branded intro
INTRO_DUR = 3.6
LOGO = Image.open(HERE.parent / "brand" / "logo_final.png").convert("RGBA")


def intro_audio(path):
    sr = 24000
    n = int(INTRO_DUR * sr)
    a = np.zeros(n)
    t = np.arange(int(0.18 * sr)) / sr
    def thump(at, f, amp):
        env = np.exp(-t * 22) * (1 - np.exp(-t * 400))
        s_ = amp * env * np.sin(2 * np.pi * f * t * (1 - 0.25 * t))
        i = int(at * sr)
        a[i:i + len(s_)] += s_[:max(0, n - i)]
    for base in (0.55, 1.45):
        thump(base, 58, 0.75)
        thump(base + 0.22, 72, 0.55)
    # soft rising tone under the logo reveal
    tt = np.arange(n) / sr
    swell = 0.10 * np.sin(2 * np.pi * 220 * tt) * np.clip((tt - 1.9) / 0.5, 0, 1) * np.clip((INTRO_DUR - 0.2 - tt) / 0.9, 0, 1)
    swell += 0.06 * np.sin(2 * np.pi * 330 * tt) * np.clip((tt - 2.1) / 0.5, 0, 1) * np.clip((INTRO_DUR - 0.2 - tt) / 0.9, 0, 1)
    a += swell
    pcm = (np.clip(a, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())


def _bg():
    y, x = np.mgrid[0:H, 0:W]
    r = np.clip(np.sqrt(((x - W / 2) / W) ** 2 + ((y - H / 2) / H) ** 2) / 0.75, 0, 1)[..., None]
    return Image.fromarray((np.array(NAVY1) * (1 - r) + np.array(NAVY0) * r).astype("uint8"), "RGB")


INTRO_BG = _bg()


def intro_frame(t):
    fr = INTRO_BG.copy().convert("RGBA")
    d = ImageDraw.Draw(fr)
    # ECG line drawing across (0 -> 1.9 s), two beats matching the thumps
    prog = ramp(t, 0.0, 1.9)
    Y = 560
    pts = []
    for i in range(0, int(W * prog) + 1, 4):
        x = i / W
        y = 0.0
        for b in (0.28, 0.75):
            if b - 0.12 <= x < b + 0.28:
                y = wave_y((x - (b - 0.12)) / 0.40)
        pts.append((i, Y + y * 170))
    fade = 1 - ramp(t, 2.0, 0.6)
    if len(pts) > 1 and fade > 0:
        d.line(pts, fill=R.mix(NAVY1, WIRE, fade), width=6, joint="curve")
        if prog < 1:
            x, y = pts[-1]
            d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=SPARK)
    a = ramp(t, 1.9, 0.5)
    if a > 0:
        sc = 0.85 + 0.15 * (1 - (1 - a) ** 3)
        size = int(330 * sc)
        lg = LOGO.resize((size, size), Image.LANCZOS)
        lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a)))
        fr.alpha_composite(lg, (560 - size // 2, 540 - size // 2))
        f1 = R.visuals.font(92, 800)
        d.text((770, 455), "THE ANATOMY", font=f1, fill=R.mix(NAVY1, (255, 255, 255), a))
        d.text((770, 560), "UNFOLDED", font=f1, fill=R.mix(NAVY1, GOLD, a))
    out = fr.convert("RGB")
    w = ramp(t, INTRO_DUR - 0.35, 0.35)
    if w > 0:
        out = Image.blend(out, Image.new("RGB", (W, H), BG), w)
    return out


# ------------------------------------------------------------------ render
def render(out_name="heart_electrical_system.mp4"):
    scenes = build()
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", str(HERE / "video_only.mp4")], stdin=subprocess.PIPE)
    for f in range(int(round(INTRO_DUR * FPS))):
        ff.stdin.write(intro_frame(f / FPS).tobytes())
    print("  intro done", flush=True)
    for s in scenes:
        n = int(round(s.dur * FPS))
        items = sorted(s.items, key=lambda x: x[0])
        settled = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        done = 0
        for f in range(n):
            t = f / FPS
            while done < len(items) and t >= items[done][0] + 0.45:
                settled.alpha_composite(items[done][1])
                done += 1
            fading = [(lay, (t - t0) / 0.45) for t0, lay in items[done:] if t >= t0]
            ff.stdin.write(draw_frame(s, t, settled, fading).tobytes())
        print(f"  {s.id} done ({s.dur:.1f}s)", flush=True)
    ff.stdin.close()
    ff.wait()
    intro_audio(HERE / "audio_intro.wav")
    with open(HERE / "audio_list.txt", "w") as fh:
        fh.write(f"file '{HERE / 'audio_intro.wav'}'\n")
        for s in scenes:
            fh.write(f"file '{s.audio}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(HERE / "audio_list.txt"),
                    "-c", "pcm_s16le", str(HERE / "voice.wav")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "video_only.mp4"), "-i", str(HERE / "voice.wav"),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                    str(HERE / out_name)], check=True)
    print("done ->", HERE / out_name)


def stills():
    for i, tt in enumerate((0.9, 1.6, 2.6, 3.4)):
        intro_frame(tt).save(HERE / f"s_intro{i}.png")
    for s in build():
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for _, lay in s.items:
            overlay.alpha_composite(lay)
        draw_frame(s, s.dur * 0.8, overlay, []).save(HERE / f"s_{s.id}.png")
    print("stills ok")


if __name__ == "__main__":
    stills() if len(sys.argv) > 1 and sys.argv[1] == "stills" else render()
