"""Sample v3: real textbook figures (OpenStax Anatomy & Physiology 2e, CC BY 4.0) with slow zooms, gold
highlights timed to the narration, blood dots flowing over the real heart, and our text panel."""
import json
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

import render as R
from render import BG, BLUE, BLUE_D, GOLD, GRAY, INK, MAROON, RED, RED_D, SS, FPS, H, W, P, Scene, layer, text

HERE = Path(__file__).resolve().parent
OX = HERE.parent / "ox"
FIG = {k: Image.open(OX / f"fig_{n}").convert("RGB") for k, n in
       (("ext", 5), ("thorax", 1), ("int", 8), ("valves", 11), ("circ", 3), ("sys", 13), ("dia", 12))
       if (OX / f"fig_{n}").exists()}  # only fig_1 (thorax) and fig_3 (circulation) are kept for v4
AREA = (30, 40, 1200, 1030)
CREDIT = "Figure: OpenStax, Anatomy & Physiology 2e (Rice University), CC BY 4.0"

PATHS = {
    "svc": [(600, 140), (600, 360), (600, 480), (625, 630), (700, 740), (760, 660), (790, 560), (790, 503), (830, 380),
            (880, 280), (960, 232), (1050, 205)],
    "pv": [(1095, 385), (1040, 370), (960, 380), (975, 450), (985, 500), (1000, 600), (1010, 690), (950, 640),
           (900, 580), (860, 512), (820, 420), (780, 330), (750, 200), (760, 90), (780, 30)],
}


def cum(pts):
    out = [0.0]
    for a, b in zip(pts, pts[1:]):
        out.append(out[-1] + math.dist(a, b))
    return out


LEN = {k: cum(v) for k, v in PATHS.items()}


def at(key, s):
    pts, L = PATHS[key], LEN[key]
    s = max(0.0, min(s, L[-1]))
    for i in range(len(L) - 1):
        if L[i] <= s <= L[i + 1]:
            t = (s - L[i]) / max(L[i + 1] - L[i], 1e-6)
            return pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t
    return pts[-1]


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


class View:
    """A figure shown in AREA, slowly zooming from rect a to rect b (figure pixel coordinates)."""
    def __init__(self, fig, a, b=None):
        self.img, self.a, self.b = FIG[fig], a, b or a

    def rect(self, u):
        e = ease(u)
        return tuple(self.a[i] + (self.b[i] - self.a[i]) * e for i in range(4))

    def transform(self, u):
        x0, y0, x1, y1 = self.rect(u)
        aw, ah = AREA[2] - AREA[0], AREA[3] - AREA[1]
        k = min(aw / (x1 - x0), ah / (y1 - y0))
        ox = AREA[0] + (aw - (x1 - x0) * k) / 2
        oy = AREA[1] + (ah - (y1 - y0) * k) / 2
        return x0, y0, x1, y1, k, ox, oy

    def draw(self, frame, u):
        x0, y0, x1, y1, k, ox, oy = self.transform(u)
        crop = self.img.crop((int(x0), int(y0), int(x1), int(y1)))
        crop = crop.resize((max(1, int((x1 - x0) * k)), max(1, int((y1 - y0) * k))), Image.BILINEAR)
        frame.paste(crop, (int(ox), int(oy)))

    def map(self, u, pt):
        x0, y0, x1, y1, k, ox, oy = self.transform(u)
        return ox + (pt[0] - x0) * k, oy + (pt[1] - y0) * k, k


def header(title, sub=None):
    def fn(d):
        text(d, (1250, 80), title, 60, MAROON, 800)
        w = d.textlength(title, font=R.F(60, 800)) / SS
        d.line(P([(1252, 156), (1250 + w, 152)]), fill=GOLD, width=8 * SS)
        if sub:
            text(d, (1252, 172), sub, 30, GRAY, 500)
    return fn


def item(y, s, color=INK, dot=None, size=32, weight=700):
    return R.panel_item(y, s, color, dot, size, 1250, weight)


def credit(d):
    text(d, (40, 1046), CREDIT, 18, GRAY, 500)


def build():
    sc = {s["id"]: Scene(s["id"], s["text"]) for s in json.load(open(HERE / "script.json"))}
    for s in sc.values():
        s.glows, s.flows, s.views, s.bursts = [], [], [], []

    s = sc["hook"]
    s.views = [(0, View("ext", (0, 0, 2233, 1060), (0, 10, 2233, 1050)))]
    s.add(0, header("THE HEART", "Anatomy & how blood flows"))
    s.add(s.t("beats"), item(330, "≈ 100,000", RED_D, size=72, weight=800))
    s.add(s.t("beats"), item(430, "heartbeats every day", INK, size=34, weight=500))
    s.add(s.t("pumps"), item(560, "≈ 7,000 liters", BLUE_D, size=72, weight=800))
    s.add(s.t("pumps"), item(660, "of blood pumped every day", INK, size=34, weight=500))
    s.add(0, lambda d: text(d, (1250, 1000), "Educational content only, not medical advice.", 22, GRAY, 500))

    s = sc["chest"]
    s.views = [(0, View("thorax", (0, 0, 2177, 1974)))]
    s.add(0, header("WHERE IS THE HEART?"))
    for i, (w, line) in enumerate([("middle", "Middle of the chest"), ("between", "Between the two lungs"),
                                   ("tilted", "Tilted slightly to the left"), ("size", "About the size of your fist"),
                                   ("cardiac", "Made of cardiac muscle")]):
        s.add(s.t(w), item(300 + i * 90, line, dot=R.MUSCLE_D, size=34))

    s = sc["chambers"]
    s.views = [(0, View("int", (0, 0, 1656, 1159), (0, 25, 1656, 1140)))]
    s.add(0, header("4 CHAMBERS", "Two pumps, side by side"))
    s.add(s.t("atrium"), item(300, "Atrium: receives blood", dot=GOLD))
    s.add(s.t("ventricle"), item(375, "Ventricle: pumps blood out", dot=GOLD))
    s.glows += [(s.t("septum"), "int", (912, 740), 60), (s.t("right", 1), "int", (600, 490), 95),
                (s.t("ventricle", 3), "int", (705, 745), 105), (s.t("left", 1), "int", (960, 375), 85),
                (s.t("left", 2), "int", (1000, 700), 115)]
    s.add(s.t("four"), item(470, "Right side: oxygen-poor blood", dot=BLUE))
    s.add(s.t("four"), item(545, "Left side: oxygen-rich blood", dot=RED))

    s = sc["valves"]
    s.views = [(0, View("valves", (0, 0, 1525, 1217), (0, 15, 1525, 1205)))]
    s.add(0, header("4 VALVES", "One-way doors (seen from above)"))
    for i, (w, key, pt, r, col, side) in enumerate([
            ("tricuspid", "Tricuspid", (510, 398), 150, BLUE_D, "right"), ("pulmonary", "Pulmonary", (750, 912), 110, BLUE_D, "right"),
            ("mitral", "Mitral", (960, 435), 160, RED_D, "left"), ("aortic", "Aortic", (682, 682), 100, RED_D, "left")]):
        s.glows.append((s.t(w), "valves", pt, r))
        s.add(s.t(w), item(300 + i * 80, f"{i + 1}  {key} valve  ({side} side)", col))

    s = sc["right"]
    s.views = [(0, View("int", (0, 25, 1656, 1140), (440, 20, 1238, 960)))]
    s.add(0, header("RIGHT SIDE", "Blood goes to the lungs"))
    for i, (w, line) in enumerate([("vena", "1  Vena cava  ->  right atrium"),
                                   ("tricuspid", "2  Tricuspid valve  ->  right ventricle"),
                                   ("pulmonary", "3  Pulmonary valve  ->  pulmonary artery"),
                                   ("lungs", "4  Pulmonary artery  ->  lungs")]):
        s.add(s.t(w), item(300 + i * 78, line, BLUE_D, size=30))
    s.glows += [(s.t("superior"), "int", (600, 170), 60), (s.t("inferior"), "int", (600, 870), 60),
                (s.t("artery"), "int", (955, 232), 60)]
    s.flows.append(("svc", [(s.t("returns"), 0), (s.t("atrium"), LEN["svc"][2]), (s.t("tricuspid"), LEN["svc"][4]),
                            (s.t("pumps"), LEN["svc"][7]), (s.t("lungs"), LEN["svc"][-1])], 0.0))

    s = sc["lungs"]
    s.views = [(0, View("circ", (0, 0, 2287, 2525), (650, 1050, 1950, 2150)))]
    s.add(0, header("IN THE LUNGS", "Oxygen in, carbon dioxide out"))
    for i, (w, line, c) in enumerate([("carbon", "CO2 out", BLUE_D), ("oxygen", "O2 in", RED_D),
                                      ("pulmonary", "Pulmonary veins  ->  left atrium", RED_D)]):
        s.add(s.t(w), item(300 + i * 80, line, c, size=34))

    s = sc["left"]
    s.views = [(0, View("int", (440, 20, 1238, 960), (625, 0, 1238, 930)))]
    s.add(0, header("LEFT SIDE", "Blood goes to the body"))
    for i, (w, line) in enumerate([("mitral", "1  Mitral valve  ->  left ventricle"),
                                   ("thickest", "2  Thickest wall: pumps to the whole body"),
                                   ("aortic", "3  Aortic valve  ->  aorta"), ("organ", "4  Aorta  ->  every organ")]):
        s.add(s.t(w), item(300 + i * 78, line, RED_D, size=30))
    s.glows += [(s.t("thickest"), "int", (1045, 700), 150), (s.t("aorta", 1), "int", (760, 200), 90)]
    s.flows.append(("pv", [(0.2, LEN["pv"][2]), (s.t("mitral"), LEN["pv"][6]), (s.t("aortic"), LEN["pv"][9]),
                           (s.t("organ"), LEN["pv"][-1])], 0.0))

    s = sc["lubdub"]
    s.views = [(0, View("sys", (0, 0, 1985, 1912))), (s.t("dub", 2), View("dia", (0, 0, 1991, 1919)))]
    s.add(0, header("LUB - DUB", "The sound of valves closing"))
    s.add(s.t("lub", 2), item(300, "LUB = tricuspid + mitral close", BLUE_D))
    s.add(s.t("lub", 2), item(350, "(ventricles start to squeeze)", GRAY, size=28, weight=500))
    s.add(s.t("dub", 2), item(450, "DUB = pulmonary + aortic close", RED_D))
    s.add(s.t("dub", 2), item(500, "(ventricles relax)", GRAY, size=28, weight=500))
    s.bursts += [(s.t("lub", 2), "LUB", BLUE_D), (s.t("dub", 2), "DUB", RED_D)]

    s = sc["summary"]
    s.views = [(0, View("circ", (0, 0, 2287, 2525)))]
    s.add(0, header("SUMMARY"))
    for i, (w, line, c) in enumerate([("right", "Right side  ->  lungs: picks up oxygen", BLUE_D),
                                      ("left", "Left side  ->  body: delivers oxygen", RED_D),
                                      ("four", "4 valves keep blood flowing one way", MAROON)]):
        s.add(s.t(w), item(300 + i * 85, line, c, size=30))
    s.add(s.t("next"), item(620, "NEXT VIDEO:", GOLD, size=30, weight=800))
    s.add(s.t("next"), item(670, "The heart's electrical system (ECG)", INK, size=30))
    s.add(0, lambda d: text(d, (1250, 1000), "Educational content only, not medical advice.", 22, GRAY, 500))
    for s in sc.values():
        s.add(0, credit)
    return [sc[k] for k in ("hook", "chest", "chambers", "valves", "right", "lungs", "left", "lubdub", "summary")]


def draw_frame(s, t, settled_overlay, fading):
    frame = Image.new("RGB", (W, H), BG)
    u = t / max(s.dur, 1e-3)
    view = [v for t0, v in s.views if t >= t0 - 1e-6][-1]
    prev = [v for t0, v in s.views if t >= t0 - 1e-6]
    view.draw(frame, u)
    if len(prev) > 1:  # crossfade into the newest figure
        t_new = [t0 for t0, v in s.views if t >= t0 - 1e-6][-1]
        a = min(1.0, (t - t_new) / 0.5)
        if a < 1.0:
            old = Image.new("RGB", (W, H), BG)
            prev[-2].draw(old, u)
            frame = Image.blend(old, frame, a)
    d = ImageDraw.Draw(frame)
    for t0, fig, pt, r in s.glows:
        if t >= t0 and view.img is FIG[fig]:
            x, y, k = view.map(u, pt)
            a = min(1.0, (t - t0) / 0.4)
            rr = r * k * (1.0 + 0.04 * math.sin((t - t0) * 6))
            for w_, c in ((10, (255, 255, 255)), (6, GOLD)):
                d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=c if a >= 1 else R.mix(BG, c, a), width=w_)
    for key, keys, start in s.flows:
        if t < keys[0][0] or view.img is not FIG["int"]:
            continue
        lim = keys[-1][1]
        for (ta, sa), (tb, sb) in zip(keys, keys[1:]):
            if t < tb:
                lim = sa + (sb - sa) * max(0.0, t - ta) / max(tb - ta, 1e-3)
                break
        first = keys[0][1] if key == "pv" else 0.0
        gap, speed = 46.0, 160.0
        x = first + (t * speed) % gap
        col = BLUE_D if key == "svc" else RED_D
        while x <= lim:
            px, py, k = view.map(u, at(key, x))
            rad = max(6, 11 * k)
            d.ellipse((px - rad, py - rad, px + rad, py + rad), fill=col, outline=(255, 255, 255), width=3)
            x += gap
    out = frame.convert("RGBA")
    out.alpha_composite(settled_overlay)
    for lay, a in fading:
        tmp = lay.copy()
        tmp.putalpha(tmp.getchannel("A").point(lambda v, a=a: int(v * a)))
        out.alpha_composite(tmp)
    for t0, w, col in s.bursts:
        if t0 <= t <= t0 + 1.4:
            sz = int(50 + 60 * min(1, (t - t0) / 0.25))
            key = (w, sz)
            if key not in WORDS:
                WORDS[key] = layer(lambda dd, w=w, sz=sz, col=col: text(dd, (615, 535), w, sz, col, 800, "mm"))
            out.alpha_composite(WORDS[key])
    return out.convert("RGB")


WORDS = {}


def render(out_name="heart_sample_v3.mp4", only=None):
    scenes = build()
    if only:
        scenes = [s for s in scenes if s.id in only]
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", str(HERE / "video_only3.mp4")], stdin=subprocess.PIPE)
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
    with open(HERE / "audio_list3.txt", "w") as fh:
        for s in scenes:
            fh.write(f"file '{s.audio}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(HERE / "audio_list3.txt"),
                    "-c", "pcm_s16le", str(HERE / "voice3.wav")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "video_only3.mp4"), "-i", str(HERE / "voice3.wav"),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(HERE / out_name)], check=True)
    print("done ->", HERE / out_name)


def stills():
    for s in build():
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for _, lay in s.items:
            overlay.alpha_composite(lay)
        t = s.dur * 0.85
        draw_frame(s, t, overlay, []).save(HERE / f"v3_{s.id}.png")
    print("stills ok")


if __name__ == "__main__":
    stills() if len(sys.argv) > 1 and sys.argv[1] == "stills" else render()
