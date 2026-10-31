"""Sample v4: our own colour line-art heart (lineart.py) as the main diagram, with glows, label tags and blood
dots timed to the narration. The chest-location and lungs scenes keep the OpenStax figures (credited)."""
import json
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

import lineart as LA
import render as R
import render3 as V3
from render import BG, BLUE_D, GOLD, GRAY, INK, MAROON, RED_D, SS, FPS, H, W, Scene, layer, text
from render3 import View, header, item

HERE = Path(__file__).resolve().parent
CX0 = 900  # crop of the supersampled line-art canvas: x from 900 to 2700 (SS px)


def build_heart():
    img, _ = LA.draw(BG)
    return img.convert("RGB").crop((CX0, 0, CX0 + 1800, H * SS))


V3.FIG["heart"] = build_heart()


def F(p):
    """lineart screen coords -> heart figure coords."""
    return ((p[0] + LA.DX) * SS - CX0, p[1] * SS)


PATHS = {
    "right": [(650, 70), (650, 300), (662, 520), (700, 610), (736, 690), (768, 790), (798, 770), (806, 640), (814, 482),
              (845, 388), (905, 336), (990, 318), (1090, 315), (1165, 318)],
    "left": [(1172, 442), (1100, 460), (1030, 500), (1018, 570), (1018, 650), (1005, 780), (965, 850), (930, 760),
             (905, 660), (898, 560), (890, 450), (885, 340), (902, 250), (952, 192), (1012, 186), (1056, 226),
             (1072, 300)],
}
PATHS = {k: [F(p) for p in v] for k, v in PATHS.items()}
LEN = {k: V3.cum(v) for k, v in PATHS.items()}

# name -> (target in lineart coords, tag offset in frame px)
TAGS = {
    "SVC": ("Superior vena cava", (650, 200), (-150, -40), BLUE_D),
    "IVC": ("Inferior vena cava", (612, 960), (-120, 0), BLUE_D),
    "RA": ("Right atrium", (612, 560), (-150, -30), BLUE_D),
    "RV": ("Right ventricle", (735, 850), (60, 170), BLUE_D),
    "LA": ("Left atrium", (1035, 515), (170, 50), RED_D),
    "LV": ("Left ventricle", (1010, 800), (130, 60), RED_D),
    "septum": ("Septum", (866, 860), (60, 130), MAROON),
    "tricuspid": ("Tricuspid valve", (724, 668), (-230, 90), BLUE_D),
    "pulmonary": ("Pulmonary valve", (805, 630), (-60, -260), BLUE_D),
    "mitral": ("Mitral valve", (1018, 618), (160, 110), RED_D),
    "aortic": ("Aortic valve", (900, 612), (-200, -130), RED_D),
    "PA": ("Pulmonary artery", (1110, 318), (60, -80), BLUE_D),
    "PV": ("Pulmonary veins", (1150, 447), (50, -70), RED_D),
    "aorta": ("Aorta", (1000, 175), (120, -20), RED_D),
}
GLOW = {"RA": ((660, 550), 95), "RV": ((760, 820), 100), "LA": ((1020, 520), 75), "LV": ((990, 800), 115),
        "septum": ((866, 840), 50), "tricuspid": ((724, 668), 45), "pulmonary": ((805, 630), 40),
        "mitral": ((1018, 618), 45), "aortic": ((900, 612), 45), "SVC": ((650, 200), 55), "IVC": ((612, 960), 55),
        "PA": ((1060, 318), 60), "aorta": ((990, 190), 75), "PV": ((1150, 500), 70), "LVwall": ((1000, 800), 135)}

FULL = (60, 0, 1800, 2160)
VALVE_ZOOM = (480, 950, 1580, 1890)
CREDIT_SCENES = {"chest", "lungs"}


def heart_view(a, b=None):
    return View("heart", a, b)


def build():
    sc = {s["id"]: Scene(s["id"], s["text"]) for s in json.load(open(HERE / "script.json"))}
    for s in sc.values():
        s.glows, s.tags, s.flows, s.views, s.bursts = [], [], [], [], []

    def mark(s, word, key, nth=1, glow=True, tag=True, until=None):
        t0 = s.t(word, nth)
        if glow:
            s.glows.append((t0, key, until))
        if tag and key in TAGS:
            s.tags.append((t0, key))

    s = sc["hook"]
    s.views = [(0, heart_view(FULL, (160, 80, 1760, 2100)))]
    s.add(0, header("THE HEART", "Anatomy & how blood flows"))
    s.add(s.t("beats"), item(330, "≈ 100,000", RED_D, size=72, weight=800))
    s.add(s.t("beats"), item(430, "heartbeats every day", INK, size=34, weight=500))
    s.add(s.t("pumps"), item(560, "≈ 7,000 liters", BLUE_D, size=72, weight=800))
    s.add(s.t("pumps"), item(660, "of blood pumped every day", INK, size=34, weight=500))
    s.flows += [("right", [(s.t("follow"), 0), (s.dur, LEN["right"][-1] * 0.6)]),
                ("left", [(s.t("follow"), 0), (s.dur, LEN["left"][-1] * 0.6)])]
    s.add(0, lambda d: text(d, (1250, 1000), "Educational content only, not medical advice.", 22, GRAY, 500))

    s = sc["chest"]
    s.views = [(0, View("thorax", (0, 0, 2177, 1974)))]
    s.add(0, header("WHERE IS THE HEART?"))
    for i, (w, line) in enumerate([("middle", "Middle of the chest"), ("between", "Between the two lungs"),
                                   ("tilted", "Tilted slightly to the left"), ("size", "About the size of your fist"),
                                   ("cardiac", "Made of cardiac muscle")]):
        s.add(s.t(w), item(300 + i * 90, line, dot=R.MUSCLE_D, size=34))

    s = sc["chambers"]
    s.views = [(0, heart_view(FULL, (100, 300, 1760, 2120)))]
    s.add(0, header("4 CHAMBERS", "Two pumps, side by side"))
    s.add(s.t("atrium"), item(300, "Atrium: receives blood", dot=GOLD))
    s.add(s.t("ventricle"), item(375, "Ventricle: pumps blood out", dot=GOLD))
    s.add(s.t("four"), item(470, "Right side: oxygen-poor blood", dot=R.BLUE))
    s.add(s.t("four"), item(545, "Left side: oxygen-rich blood", dot=R.RED))
    mark(s, "septum", "septum")
    mark(s, "right", "RA", 1)
    mark(s, "ventricle", "RV", 2)
    mark(s, "left", "LA", 1)
    mark(s, "left", "LV", 2)

    s = sc["valves"]
    s.views = [(0, heart_view(FULL, VALVE_ZOOM))]
    s.add(0, header("4 VALVES", "One-way doors"))
    for i, (w, key, col, side) in enumerate([("tricuspid", "Tricuspid", BLUE_D, "right"),
                                             ("pulmonary", "Pulmonary", BLUE_D, "right"),
                                             ("mitral", "Mitral", RED_D, "left"), ("aortic", "Aortic", RED_D, "left")]):
        s.add(s.t(w), item(300 + i * 80, f"{i + 1}  {key} valve  ({side} side)", col))
        mark(s, w, w)

    s = sc["right"]
    s.views = [(0, heart_view(FULL, (40, 120, 1640, 2120)))]
    s.add(0, header("RIGHT SIDE", "Blood goes to the lungs"))
    for i, (w, line) in enumerate([("vena", "1  Vena cava  ->  right atrium"),
                                   ("tricuspid", "2  Tricuspid valve  ->  right ventricle"),
                                   ("pulmonary", "3  Pulmonary valve  ->  pulmonary artery"),
                                   ("lungs", "4  Pulmonary artery  ->  lungs")]):
        s.add(s.t(w), item(300 + i * 78, line, BLUE_D, size=30))
    mark(s, "superior", "SVC")
    mark(s, "inferior", "IVC")
    mark(s, "atrium", "RA", glow=False)
    mark(s, "tricuspid", "tricuspid")
    mark(s, "ventricle", "RV", glow=False)
    mark(s, "pulmonary", "pulmonary")
    mark(s, "artery", "PA")
    L = LEN["right"]
    s.flows.append(("right", [(s.t("returns"), 0), (s.t("atrium"), L[2]), (s.t("tricuspid"), L[4]),
                              (s.t("pumps"), L[6]), (s.t("pulmonary"), L[7]), (s.t("lungs"), L[-1])]))

    s = sc["lungs"]
    s.views = [(0, View("circ", (0, 0, 2287, 2525), (650, 1050, 1950, 2150)))]
    s.add(0, header("IN THE LUNGS", "Oxygen in, carbon dioxide out"))
    for i, (w, line, c) in enumerate([("carbon", "CO2 out", BLUE_D), ("oxygen", "O2 in", RED_D),
                                      ("pulmonary", "Pulmonary veins  ->  left atrium", RED_D)]):
        s.add(s.t(w), item(300 + i * 80, line, c, size=34))

    s = sc["left"]
    s.views = [(0, heart_view(FULL, (200, 60, 1800, 2000)))]
    s.add(0, header("LEFT SIDE", "Blood goes to the body"))
    for i, (w, line) in enumerate([("mitral", "1  Mitral valve  ->  left ventricle"),
                                   ("thickest", "2  Thickest wall: pumps to the whole body"),
                                   ("aortic", "3  Aortic valve  ->  aorta"), ("organ", "4  Aorta  ->  every organ")]):
        s.add(s.t(w), item(300 + i * 78, line, RED_D, size=30))
    mark(s, "from", "PV", glow=False)
    mark(s, "atrium", "LA")
    mark(s, "mitral", "mitral")
    mark(s, "ventricle", "LV", glow=False)
    mark(s, "thickest", "LVwall", tag=False)
    mark(s, "aortic", "aortic")
    mark(s, "aorta", "aorta", 1)
    L = LEN["left"]
    s.flows.append(("left", [(0.2, 0), (s.t("mitral"), L[4]), (s.t("ventricle"), L[6]), (s.t("aortic"), L[9]),
                             (s.t("organ"), L[-1])]))

    s = sc["lubdub"]
    s.views = [(0, heart_view(FULL, VALVE_ZOOM))]
    s.add(0, header("LUB - DUB", "The sound of valves closing"))
    s.add(s.t("lub", 2), item(300, "LUB = tricuspid + mitral close", BLUE_D))
    s.add(s.t("lub", 2), item(350, "(ventricles start to squeeze)", GRAY, size=28, weight=500))
    s.add(s.t("dub", 2), item(450, "DUB = pulmonary + aortic close", RED_D))
    s.add(s.t("dub", 2), item(500, "(ventricles relax)", GRAY, size=28, weight=500))
    for k in ("tricuspid", "mitral"):
        mark(s, "lub", k, 2, until=s.t("dub", 2))
    for k in ("pulmonary", "aortic"):
        mark(s, "dub", k, 2)
    s.bursts += [(s.t("lub", 2), "LUB", BLUE_D), (s.t("dub", 2), "DUB", RED_D)]

    s = sc["summary"]
    s.views = [(0, heart_view((160, 80, 1760, 2100), FULL))]
    s.add(0, header("SUMMARY"))
    for i, (w, line, c) in enumerate([("right", "Right side  ->  lungs: picks up oxygen", BLUE_D),
                                      ("left", "Left side  ->  body: delivers oxygen", RED_D),
                                      ("four", "4 valves keep blood flowing one way", MAROON)]):
        s.add(s.t(w), item(300 + i * 85, line, c, size=30))
    s.flows += [("right", [(s.t("right"), 0), (s.t("right") + 4, LEN["right"][-1])]),
                ("left", [(s.t("left"), 0), (s.t("left") + 4, LEN["left"][-1])])]
    s.add(s.t("next"), item(620, "NEXT VIDEO:", GOLD, size=30, weight=800))
    s.add(s.t("next"), item(670, "The heart's electrical system (ECG)", INK, size=30))
    s.add(0, lambda d: text(d, (1250, 1000), "Educational content only, not medical advice.", 22, GRAY, 500))
    for s in sc.values():
        if s.id in CREDIT_SCENES:
            s.add(0, V3.credit)
    return [sc[k] for k in ("hook", "chest", "chambers", "valves", "right", "lungs", "left", "lubdub", "summary")]


def at(key, x):
    pts, L = PATHS[key], LEN[key]
    x = max(0.0, min(x, L[-1]))
    for i in range(len(L) - 1):
        if L[i] <= x <= L[i + 1]:
            u = (x - L[i]) / max(L[i + 1] - L[i], 1e-6)
            return pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u
    return pts[-1]


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


def draw_frame(s, t, settled, fading):
    frame = Image.new("RGB", (W, H), BG)
    u = t / max(s.dur, 1e-3)
    view = [v for t0, v in s.views if t >= t0 - 1e-6][-1]
    view.draw(frame, u)
    is_heart = view.img is V3.FIG["heart"]
    d = ImageDraw.Draw(frame)
    if is_heart:
        for t0, key, until in s.glows:
            if t >= t0 and (until is None or t < until):
                (pt, r) = GLOW[key]
                x, y, k = view.map(u, F(pt))
                a = min(1.0, (t - t0) / 0.4)
                rr = r * SS * k * (1.0 + 0.05 * math.sin((t - t0) * 6))
                for w_, c in ((12, (255, 255, 255)), (7, GOLD)):
                    d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=R.mix(BG, c, a), width=w_)
        for key, keys in s.flows:
            if t < keys[0][0]:
                continue
            lim = keys[-1][1]
            for (ta, sa), (tb, sb) in zip(keys, keys[1:]):
                if t < tb:
                    lim = sa + (sb - sa) * max(0.0, t - ta) / max(tb - ta, 1e-3)
                    break
            gap, speed = 95.0, 240.0
            x = (t * speed) % gap
            col = (22, 40, 105) if key == "right" else (105, 12, 24)
            while x <= lim:
                px, py, k = view.map(u, at(key, x))
                rad = max(10, 22 * k)
                d.ellipse((px - rad, py - rad, px + rad, py + rad), fill=col, outline=(255, 255, 255), width=3)
                x += gap
    out = frame.convert("RGBA")
    if is_heart and s.tags:
        tl = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        td = ImageDraw.Draw(tl)
        for t0, key in s.tags:
            if t >= t0:
                tag(td, view, u, key, min(1.0, (t - t0) / 0.35))
        out.alpha_composite(tl.resize((W, H), Image.LANCZOS))
    out.alpha_composite(settled)
    for lay, a in fading:
        tmp = lay.copy()
        tmp.putalpha(tmp.getchannel("A").point(lambda v, a=a: int(v * a)))
        out.alpha_composite(tmp)
    for t0, w, col in s.bursts:
        if t0 <= t <= t0 + 1.4:
            sz = int(50 + 60 * min(1, (t - t0) / 0.25))
            key = (w, sz)
            if key not in V3.WORDS:
                V3.WORDS[key] = layer(lambda dd, w=w, sz=sz, col=col: text(dd, (615, 110), w, sz, col, 800, "mm"))
            out.alpha_composite(V3.WORDS[key])
    return out.convert("RGB")


def render(out_name="heart_sample_v4.mp4"):
    scenes = build()
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", str(HERE / "video_only4.mp4")], stdin=subprocess.PIPE)
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
    with open(HERE / "audio_list4.txt", "w") as fh:
        for s in scenes:
            fh.write(f"file '{s.audio}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(HERE / "audio_list4.txt"),
                    "-c", "pcm_s16le", str(HERE / "voice4.wav")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "video_only4.mp4"), "-i", str(HERE / "voice4.wav"),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(HERE / out_name)], check=True)
    print("done ->", HERE / out_name)


def stills():
    for s in build():
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for _, lay in s.items:
            overlay.alpha_composite(lay)
        draw_frame(s, s.dur * 0.85, overlay, []).save(HERE / f"v4_{s.id}.png")
    print("stills ok")


if __name__ == "__main__":
    stills() if len(sys.argv) > 1 and sys.argv[1] == "stills" else render()
