"""Brain Anatomy - two story Shorts (owner-approved 9 Nov 2026): suspense scene + cut-off cliffhanger bridge.

    python3 osm_brain_shorts.py 1      # H.M. (12 PM Short)     -> brain_story1.mp4
    python3 osm_brain_shorts.py 2      # Phineas Gage (9 PM)    -> brain_story2.mp4
Env: OUT_DIR = where files are written.
"""
import json
import math
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("OUT_DIR", str(HERE)))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_preview as OP  # noqa: E402
import osm_brain as OB  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OB.PINK, OB.LILAC, OB.CREAM, OB.MINT, OB.SKY
PW, PH = 1920, 1080
sv = OB.sv
TITLES = {1: "The Man Who Forgot Every Minute", 2: "The Iron Rod Through His Head"}
QUESTIONS = {1: "Why does losing it erase new memories, but not old ones?", 2: "So which part is it?"}


def mirror_pic():
    """mirror-drawing task: a star seen in a mirror, with a pencil."""
    S, W, H = 3, 760, 480
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20 * S, 20 * S, 740 * S, 460 * S), radius=40 * S, fill=(226, 238, 250), outline=(70, 110, 170), width=8 * S)
    d.polygon([(60 * S, 60 * S), (300 * S, 40 * S), (180 * S, 120 * S)], fill=(255, 255, 255))   # shine
    cx, cy, r1, r2 = 380, 250, 150, 62
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = r1 if i % 2 == 0 else r2
        pts.append(((cx + r * math.cos(a)) * S, (cy + r * math.sin(a)) * S))
    d.line(pts + [pts[0]], fill=(200, 140, 20), width=9 * S)
    d.polygon([(520 * S, 380 * S), (640 * S, 300 * S), (660 * S, 322 * S), (545 * S, 405 * S)], fill=(245, 200, 80), outline=(140, 90, 0))   # pencil
    d.polygon([(520 * S, 380 * S), (545 * S, 405 * S), (505 * S, 420 * S)], fill=(240, 215, 180), outline=(140, 90, 0))
    return im.resize((W, H), Image.LANCZOS)


def deep_pic_hippo():
    """middle cut of the brain with only the seahorse-shaped part coloured (name not shown)."""
    S, W, H = 3, 640, 560
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    out = OB.wavy(310, 250, 290, 215, 0.02, 12, S=S)
    d.polygon(out, fill=(250, 238, 226))
    d.line(out + [out[0]], fill=(120, 95, 90), width=5 * S)
    d.polygon([(330 * S, 440 * S), (420 * S, 430 * S), (400 * S, 556 * S), (350 * S, 556 * S)], fill=(246, 222, 184), outline=(120, 95, 90))
    d.ellipse((120 * S, 400 * S, 270 * S, 470 * S), fill=(240, 205, 208), outline=(120, 95, 90), width=3 * S)
    d.arc((150 * S, 120 * S, 470 * S, 330 * S), 200, 340, fill=(215, 210, 218), width=14 * S)
    d.ellipse((250 * S, 200 * S, 390 * S, 290 * S), fill=(238, 228, 214), outline=(190, 175, 160), width=3 * S)
    d.arc((170 * S, 240 * S, 380 * S, 420 * S), 90, 225, fill=(160, 120, 222), width=26 * S)   # the seahorse-shaped part
    return im.resize((W, H), Image.LANCZOS)


class Sc(HA.Sc):
    def __init__(self, sid, text, start, d):
        import render as R
        self.id, self.text, self.start = sid, text, start
        self.audio = d / "audio" / f"{sid}.wav"
        self.dur = R.dur(self.audio)
        self.words = text.lower().replace(",", "").replace(".", "").replace("?", "").replace(":", "").split()


def build(n):
    d = HERE.parent / "brain" / f"short{n}"
    data = json.load(open(d / "script.json"))
    sc, t0 = {}, 0.0
    for s in data:
        sc[s["id"]] = Sc(s["id"], s["text"], t0, d)
        t0 += sc[s["id"]].dur
    bd = B.Board(3, 2)
    pops, glows = [], []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    cam = bd.camera
    A, Bc, C = (960, 540), (PW + 960, 540), (2 * PW + 960, 540)
    cam(0, *A, 1.0, 0.1)
    brain = OB.brain_img()
    ovf = OB.overlay("frontal", 150)
    if n == 1:
        s = sc["case"]
        b1 = pop(brain, 470, 540, h=700, t=0.3)
        a = [b1, text("1953", 1380, 215, 190, GOLD_T, s.t("1953"), "c"),
             panel(1000, 300, 1840, 540, PINK, s.t("surgery") - 0.3), text("brain surgery", 1420, 405, 84, RED_T, s.t("surgery"), "c"),
             text("to stop seizures", 1420, 500, 62, MAROON, s.t("seizures"), "c"),
             panel(1000, 570, 1840, 860, CREAM, s.t("never") - 0.5), text("NO NEW", 1420, 690, 96, RED_T, s.t("never") - 0.2, "c"),
             text("MEMORIES", 1420, 820, 96, RED_T, s.t("memory") - 0.1, "c"),
             pop(sv("Horloge"), 1090, 955, h=190, t=s.t("conversation") - 0.2), text("gone in minutes", 1520, 985, 74, PURPLE, s.t("minutes") - 1.2, "c")]
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        bb = [text("YET...", X + 960, 170, 140, BLUE_T, s.start + 0.3, "c"),
              pop(mirror_pic(), X + 960, 520, h=420, t=s.t("drawing") - 0.3),
              text("he still LEARNS new skills", X + 960, 820, 80, GREEN_T, s.t("learn"), "c"),
              text("but can't remember practicing", X + 960, 930, 68, RED_T, s.t("remembering") - 1.0, "c")]
        s = sc["clue"]
        cam(s.start, *C, 1.0, 1.0)
        bd.erase(s.start + 0.8, bb)
        X = 2 * PW
        dp = pop(deep_pic_hippo(), X + 520, 560, h=820, t=s.start + 0.3)
        glows.append((s.t("seahorse"), dp.map((223, 404)), 2.5, 120))
        cc = [dp, text("what did they remove?", X + 1400, 220, 84, RED_T, s.t("what"), "c"),
              text("small,", X + 1400, 450, 76, PURPLE, s.t("small"), "c"), text("seahorse-shaped", X + 1400, 575, 84, PURPLE, s.t("seahorse"), "c"),
              lead([(X + 1130, 540), dp.map((223, 404))], s.t("seahorse") + 0.3, PURPLE, 6, 0.6),
              text("deep inside the brain", X + 1400, 720, 68, MAROON, s.t("deep"), "c"),
              text("?", X + 1400, 950, 230, GOLD_T, s.t("brain"), "c")]
    else:
        s = sc["accident"]
        b1 = pop(brain, 470, 540, h=700, t=0.3)
        rod = lead([b1.map((560, 400)), b1.map((470, 150)), b1.map((420, -70))], s.t("iron"), (120, 80, 50), 22, 0.7)
        a = [b1, text("1848", 1380, 200, 180, GOLD_T, s.t("1848"), "c"), text("railroad worker", 1420, 360, 70, MAROON, s.t("railroad"), "c"),
             text("Phineas Gage", 1420, 450, 78, PURPLE, s.t("phineas"), "c"), text("BOOM!", 1420, 620, 140, RED_T, s.t("blew"), "c"),
             rod, text("iron rod,", 1420, 780, 70, MAROON, s.t("iron"), "c"), text("over 3 feet (1 m) long", 1420, 870, 66, RED_T, s.t("three"), "c")]
        s = sc["survive"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        bb = [text("HE SURVIVED", X + 960, 170, 140, GREEN_T, s.t("survived"), "c"), text("still walks + talks", X + 960, 310, 76, MAROON, s.t("walk"), "c"),
              text("BUT...", X + 960, 500, 140, RED_T, s.t("but"), "c"), panel(X + 220, 580, X + 1700, 790, PINK, s.t("old") - 0.3),
              text('"the old Phineas was gone"', X + 960, 710, 78, PURPLE, s.t("old"), "c"),
              text("personality reportedly changed", X + 960, 930, 70, MAROON, s.t("personality") - 0.9, "c")]
        s = sc["clue"]
        cam(s.start, *C, 1.0, 1.0)
        bd.erase(s.start + 0.8, bb)
        X = 2 * PW
        b3 = pop(brain, X + 470, 540, h=700, t=s.start + 0.3)
        cc = [b3, pop(ovf, X + 470, 540, h=700, t=s.t("front") - 0.3), text("which part?", X + 1400, 200, 100, RED_T, s.t("which"), "c"),
              text("the very front", X + 1400, 420, 84, RED_T, s.t("front"), "c"), text("plans", X + 1400, 570, 76, MAROON, s.t("plans"), "c"),
              text("decides", X + 1400, 670, 76, MAROON, s.t("decides"), "c"), text("shapes who you are", X + 1400, 780, 76, PURPLE, s.t("shapes"), "c"),
              text("?", X + 1400, 960, 200, GOLD_T, s.t("shapes") + 1.0, "c")]
        glows.append((s.t("front"), b3.map((450, 160)), 2.5, 140))

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render_board(n):
    bd, sc = build(n)
    vid = OUT / f"story{n}_video_only.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", "30", "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(vid)], stdin=subprocess.PIPE)
    for f in range(int(bd.total * 30)):
        ff.stdin.write(OF.credit(bd.frame(f / 30)).tobytes())
    ff.stdin.close()
    ff.wait()
    lst = OUT / f"story{n}_audio.txt"
    with open(lst, "w") as fh:
        for s in sc.values():
            fh.write(f"file '{s.audio}'\n")
    wav = OUT / f"story{n}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "pcm_s16le", str(wav)], check=True)
    board = OUT / f"story{n}_board.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(wav), "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest", str(board)], check=True)
    return board


def make_short(n):
    import package as P
    import bridge
    board = render_board(n)
    title = TITLES[n]
    top = Image.new("RGBA", (1080, 1920), (255, 255, 255, 0))
    d = ImageDraw.Draw(top)
    lines, cur = [], ""
    for w in title.upper().split():
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
    ov = OUT / f"story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"brain_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["brain"] = [QUESTIONS[1], QUESTIONS[2]]
    bridge.add_bridge(sh, "brain", n - 1)
    print("done ->", sh)
    return sh


if __name__ == "__main__":
    n = int(sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2] == "stills":
        bd, sc = build(n)
        for v in sc.values():
            OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"story{n}_{v.id}.png")
    else:
        make_short(n)
