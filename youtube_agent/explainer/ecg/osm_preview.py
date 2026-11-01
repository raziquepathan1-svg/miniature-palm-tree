"""Osmosis-style preview: hook + 'why' scenes on a white board with a painted heart illustration, maroon
small-caps handwriting, thin leader lines that draw on, a soft pink panel, and the gold conduction path."""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OSM = HERE.parent / "osm"
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import render_board as RB  # noqa: E402  (Sc timing class, fx)
import render as R  # noqa: E402

MAROON, PURPLE, TEAL, BLUE_T, RED_T, GOLD_T = (122, 31, 61), (91, 45, 130), (24, 110, 110), (46, 96, 176), (186, 46, 70), (170, 110, 0)
WIRE, WIRE_D = (248, 186, 60), (190, 120, 20)
FPS = 30

SRC = Image.open(OSM / "heart_section.png").convert("RGB").crop((380, 0, 900, 720))


def white_to_alpha(img):
    import numpy as np
    a = np.array(img.convert("RGBA")).astype(np.int16)
    m = (a[..., 0] > 243) & (a[..., 1] > 243) & (a[..., 2] > 243)
    a[m, 3] = 0
    return Image.fromarray(a.astype("uint8"))


HEART = white_to_alpha(SRC)

# structure positions in the cropped illustration (pixels), checked by eye on the image
P = {"SA": (112, 252), "AV": (200, 396), "RA": (110, 320), "LA": (360, 290), "RV": (190, 520), "LV": (395, 500),
     "SVC": (95, 140), "septum": (300, 520)}
WIRES = [[(112, 252), (150, 320), (185, 375), (200, 396)],
         [(200, 396), (245, 412), (290, 445)],
         [(290, 445), (288, 540), (296, 640), (240, 668), (175, 640), (132, 560)],
         [(290, 445), (322, 540), (340, 640), (395, 662), (462, 610), (488, 480), (475, 380)]]


def build():
    data = json.load(open(HERE / "script.json"))[:2]
    sc, t0 = {}, 0.0
    for s in data:
        sc[s["id"]] = RB.Sc(s["id"], s["text"], t0)
        t0 += sc[s["id"]].dur
    bd = B.Board(1, 1)
    add, cam = bd.add, bd.camera
    cam(0, 960, 540, 1.0, 0.1)

    def text(s, x, y, size, color, t, anchor="l", dur=None):
        return add(B.Text(s.upper(), x, y, size, color, t=t, dur=dur, anchor=anchor))

    def sub(s_, x, y, size, color, t):
        add(B.Stroke([(x - 2, y - 40), (x - 2, y - 10), (x + 18, y - 10)], color, 3, t=t, dur=0.25))
        return text(s_, x + 26, y, size, color, t + 0.2)

    def lead(pts, t, color=MAROON, width=3, dur=0.45):
        return add(B.Stroke(B.smooth(pts, 10), color, width, t=t, dur=dur))

    s = sc["hook"]
    heart = add(B.Pop(HEART, 820, 590, h=900, t=0.4, dur=0.8))
    M = lambda k: heart.map(P[k])
    text("The heart's", 960, 70, 40, MAROON, 0.2, "c")
    text("Electrical System", 960, 128, 64, MAROON, 0.9, "c")
    add(B.Stroke([(700, 165), (1220, 162)], MAROON, 4, t=2.0, dur=0.5))
    th = s.t("hundred")
    add(B.Panel(1250, 300, 1820, 470, (252, 230, 233), t=th - 0.3))
    text("~100,000", 1290, 365, 64, RED_T, th)
    text("heartbeats / day", 1290, 430, 44, MAROON, th + 0.7)
    tsp = s.t("spark")
    add(B.Panel(1250, 510, 1820, 680, (253, 243, 214), t=tsp - 0.3))
    text("1 electrical spark", 1290, 575, 48, GOLD_T, tsp)
    sub("starts every beat", 1290, 640, 40, MAROON, tsp + 0.9)
    sa = M("SA")
    lead([(1250, 595), (1050, 520), (sa[0] + 14, sa[1] - 6)], tsp + 0.4, GOLD_T, 3)
    rings = [(tsp + 0.4, sa, 1.0)]
    pulses = []
    tw = s.t("spread")
    for i, w in enumerate(WIRES):
        pts = [heart.map(p) for p in w]
        add(B.Stroke(B.smooth(pts, 8), WIRE, 7, t=tw + 0.5 * i, dur=0.9, shadow=WIRE_D))
    beat_routes = [[heart.map(p) for p in WIRES[0]], [heart.map(p) for p in WIRES[1] + WIRES[2][1:]],
                   [heart.map(p) for p in WIRES[1] + WIRES[3][1:]]]
    tb = tw + 2.6
    while tb < s.end - 0.5:
        rings.append((tb, sa, 0.6))
        pulses += [(beat_routes[0], tb, 0.3), (beat_routes[1], tb + 0.35, 0.3), (beat_routes[2], tb + 0.35, 0.3)]
        tb += 0.9

    s = sc["why"]
    tb_ = s.t("brain")
    add(B.Panel(1250, 300, 1820, 470, (234, 228, 246), t=tb_ - 0.4))
    text("not from the brain", 1290, 365, 46, PURPLE, tb_ - 0.2)
    sub("makes its own signals", 1290, 430, 40, PURPLE, s.t("makes"))
    tc = s.t("conduction")
    add(B.Panel(1250, 510, 1820, 680, (253, 243, 214), t=tc - 0.4))
    text("conduction system", 1290, 575, 48, GOLD_T, tc)
    sub("built-in wiring", 1290, 640, 40, MAROON, s.t("wiring", 1))
    ta, tv = s.t("atria", 1), s.t("ventricles", 1)
    text("atria", 200, 300, 54, BLUE_T, ta)
    text("1st", 200, 360, 40, MAROON, ta + 0.5)
    lead([(330, 290), (430, 330), M("RA")], ta + 0.3, BLUE_T)
    lead([(330, 285), (600, 220), (900, 240), M("LA")], ta + 0.6, BLUE_T)
    text("ventricles", 200, 820, 54, RED_T, tv)
    text("2nd", 200, 880, 40, MAROON, tv + 0.5)
    lead([(420, 810), (520, 800), M("RV")], tv + 0.3, RED_T)
    lead([(420, 815), (700, 900), (900, 860), M("LV")], tv + 0.6, RED_T)
    glows = [(ta + 0.2, M("RA"), 1.6, 110), (ta + 0.2, M("LA"), 1.6, 100), (tv + 0.2, M("RV"), 1.8, 120),
             (tv + 0.2, M("LV"), 1.8, 130)]
    wt = s.t("wiring", 2)
    pulses += [(beat_routes[0], wt, 0.6), (beat_routes[1], wt + 0.7, 0.7), (beat_routes[2], wt + 0.7, 0.7)]
    bd.fx.append(lambda crop, ctx, t: fx(crop, ctx, t, rings, pulses, glows))
    bd.total = t0
    return bd, sc


def fx(crop, ctx, t, rings, pulses, glows):
    from PIL import ImageFilter
    for t0, p, d_, r in glows:
        if t0 <= t <= t0 + d_:
            x = (t - t0) / d_
            a = min(1, x / 0.2) * min(1, (1 - x) / 0.3)
            lay = Image.new("RGBA", crop.size, (0, 0, 0, 0))
            cx, cy = ctx.px(p)
            rr = r * B.BS
            ImageDraw.Draw(lay).ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(255, 255, 255, int(150 * a)))
            crop.alpha_composite(lay.filter(ImageFilter.GaussianBlur(30)))
    d = ImageDraw.Draw(crop)
    for t0, p, d_ in rings:
        if t0 <= t <= t0 + d_:
            x_ = (t - t0) / d_
            cx, cy = ctx.px(p)
            r = (12 + 60 * x_) * B.BS
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=R.mix((255, 255, 255), WIRE, 1 - x_), width=int(5 * B.BS))
    for pts, t0, d_ in pulses:
        if t0 <= t <= t0 + d_:
            p = B.partial_pts(pts, (t - t0) / d_)[-1]
            cx, cy = ctx.px(p)
            r = 11 * B.BS
            d.ellipse((cx - 1.8 * r, cy - 1.8 * r, cx + 1.8 * r, cy + 1.8 * r), outline=WIRE, width=int(4 * B.BS))
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 250, 220), outline=WIRE_D, width=int(3 * B.BS))


def render(out="osmosis_preview.mp4"):
    bd, sc = build()
    vid = HERE / "osm_video_only.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", str(vid)], stdin=subprocess.PIPE)
    for f in range(int(bd.total * FPS)):
        ff.stdin.write(bd.frame(f / FPS).tobytes())
    ff.stdin.close()
    ff.wait()
    with open(HERE / "osm_audio.txt", "w") as fh:
        for s in sc.values():
            fh.write(f"file '{s.audio}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(HERE / "osm_audio.txt"),
                    "-c", "pcm_s16le", str(HERE / "osm_voice.wav")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(HERE / "osm_voice.wav"), "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(HERE / out)], check=True)
    print("done")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        bd, _ = build()
        for t in [float(x) for x in sys.argv[2:]]:
            bd.frame(t).save(HERE / f"o_{t:05.1f}.png")
        print("ok", bd.total)
    else:
        render()
