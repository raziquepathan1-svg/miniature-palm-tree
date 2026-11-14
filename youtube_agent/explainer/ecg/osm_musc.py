"""Musculoskeletal system video (fact-checked 14 Nov 2026) + 2 story Shorts.

    python3 osm_musc.py [stills] | short 1|2 [stills]
Env: EP_DIR (default ../musc), OUT_DIR.
"""
import math
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "musc")))
OUT = Path(os.environ.get("OUT_DIR", str(HERE)))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_preview as OP  # noqa: E402
import osm_brain as OB  # noqa: E402
import osm_neuron as NU  # noqa: E402
import osm_digest as DG  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OB.MAROON, OB.PURPLE, OB.BLUE_T, OB.RED_T, OB.GOLD_T, OB.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OB.PINK, OB.LILAC, OB.CREAM, OB.MINT, OB.SKY
PW, PH = 1920, 1080
sv = OB.sv
SHORT_TITLES = {1: "Where Did The Bones Go", 2: "Muscles Only Pull"}
SHORT_Q = {1: "So where did the extra bones go?", 2: "So how do you straighten your arm?"}
S = 3
new, done, tube = DG.new, DG.done, DG.tube
OLN = (110, 95, 80, 255)
BONE, BONE_D = (245, 235, 215, 255), (200, 185, 160, 255)
MUS = (215, 90, 90, 255)


def bone_shape(d, x0, y0, x1, y1, w=34, col=BONE):
    """A long bone (shaft + two knobs) from (x0,y0) to (x1,y1)."""
    big = lambda p: (p[0] * S, p[1] * S)
    d.line([big((x0, y0)), big((x1, y1))], fill=OLN, width=(w + 8) * S)
    d.line([big((x0, y0)), big((x1, y1))], fill=col, width=w * S)
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang), math.cos(ang)
    for (x, y) in ((x0, y0), (x1, y1)):
        for sgn in (-1, 1):
            cx, cy = x + sgn * nx * w * 0.5, y + sgn * ny * w * 0.5
            r = w * 0.62
            d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=col, outline=OLN, width=4 * S)


def skeleton_pic():
    W, H = 520, 900
    im, d = new(W, H)
    d.ellipse((190 * S, 20 * S, 330 * S, 170 * S), fill=BONE, outline=OLN, width=6 * S)        # skull
    d.rounded_rectangle((215 * S, 150 * S, 305 * S, 200 * S), radius=14 * S, fill=BONE, outline=OLN, width=5 * S)
    d.line([(260 * S, 200 * S), (260 * S, 470 * S)], fill=OLN, width=30 * S)                  # spine
    d.line([(260 * S, 200 * S), (260 * S, 470 * S)], fill=BONE, width=20 * S)
    for k in range(6):                                                                         # ribs
        y = 205 + k * 34
        d.arc((165 * S, y * S, 260 * S, (y + 80) * S), 90, 270, fill=OLN, width=8 * S)
        d.arc((260 * S, y * S, 355 * S, (y + 80) * S), 270, 90, fill=OLN, width=8 * S)
    d.ellipse((190 * S, 440 * S, 330 * S, 540 * S), fill=BONE, outline=OLN, width=6 * S)       # pelvis
    for sx in (-1, 1):
        bone_shape(d, 260 + sx * 110, 210, 260 + sx * 130, 330, 26)                            # upper arm
        bone_shape(d, 260 + sx * 130, 340, 260 + sx * 150, 470, 22)                            # forearm
        bone_shape(d, 260 + sx * 45, 540, 260 + sx * 60, 700, 32)                              # femur
        bone_shape(d, 260 + sx * 60, 710, 260 + sx * 66, 860, 28)                              # tibia
    return done(im, W, H)


def fuse_pic():
    W, H = 900, 420
    im, d = new(W, H)
    for k, (x, y) in enumerate(((90, 90), (190, 210), (90, 330), (250, 90), (250, 330))):
        d.ellipse(((x - 40) * S, (y - 40) * S, (x + 40) * S, (y + 40) * S), fill=BONE, outline=OLN, width=5 * S)
    d.polygon([(380 * S, 190 * S), (480 * S, 190 * S), (480 * S, 150 * S), (570 * S, 210 * S), (480 * S, 270 * S), (480 * S, 230 * S), (380 * S, 230 * S)], fill=(80, 130, 210, 255))
    d.ellipse((620 * S, 60 * S, 860 * S, 360 * S), fill=BONE, outline=OLN, width=7 * S)
    return done(im, W, H)


def joint_pic():
    W, H = 900, 560
    im, d = new(W, H)
    bone_shape(d, 140, 120, 420, 270, 54)
    bone_shape(d, 470, 300, 760, 450, 54)
    d.line([(400 * S, 215 * S), (480 * S, 250 * S)], fill=(60, 150, 90, 255), width=14 * S)     # ligament (bone to bone)
    d.line([(410 * S, 300 * S), (500 * S, 340 * S)], fill=(60, 150, 90, 255), width=14 * S)
    d.rounded_rectangle((160 * S, 330 * S, 460 * S, 400 * S), radius=34 * S, fill=MUS, outline=(130, 40, 40, 255), width=5 * S)   # muscle
    d.line([(460 * S, 365 * S), (580 * S, 390 * S)], fill=(240, 200, 90, 255), width=14 * S)      # tendon (muscle to bone)
    return done(im, W, H)


def types_pic(kind):
    W, H = 400, 300
    im, d = new(W, H)
    if kind == "skeletal":
        for y in (60, 130, 200):
            d.rounded_rectangle((20 * S, y * S, 380 * S, (y + 56) * S), radius=28 * S, fill=MUS, outline=(130, 40, 40, 255), width=4 * S)
            for x in range(60, 360, 36):
                d.line([(x * S, (y + 8) * S), (x * S, (y + 48) * S)], fill=(250, 200, 200, 255), width=4 * S)
    elif kind == "smooth":
        for k, (x, y) in enumerate(((80, 80), (200, 130), (110, 200), (290, 80), (300, 210))):
            d.ellipse(((x - 70) * S, (y - 22) * S, (x + 70) * S, (y + 22) * S), fill=(230, 150, 170, 255), outline=(150, 70, 90, 255), width=4 * S)
            d.ellipse(((x - 10) * S, (y - 10) * S, (x + 10) * S, (y + 10) * S), fill=(140, 60, 90, 255))
    else:
        d.polygon([(60 * S, 100 * S), (200 * S, 60 * S), (340 * S, 100 * S), (330 * S, 220 * S), (200 * S, 260 * S), (70 * S, 220 * S)], fill=(235, 130, 130, 255), outline=(150, 40, 50, 255))
        for a in range(4):
            d.line([(80 * S, (110 + a * 36) * S), (320 * S, (110 + a * 36) * S)], fill=(255, 215, 215, 255), width=5 * S)
    return done(im, W, H)


def arm_pic(bent=True):
    W, H = 900, 640
    im, d = new(W, H)
    bone_shape(d, 140, 200, 440, 200, 46)                                   # humerus
    fore = (700, 120) if bent else (760, 270)
    bone_shape(d, 440, 200, fore[0], fore[1], 40)                           # forearm
    d.ellipse((190 * S, 110 * S, 440 * S, 170 * S), fill=MUS, outline=(130, 40, 40, 255), width=5 * S)    # biceps (front)
    d.ellipse((190 * S, 232 * S, 440 * S, 290 * S), fill=(110, 150, 220, 255), outline=(50, 80, 150, 255), width=5 * S)   # triceps (back)
    return done(im, W, H)


def filament_pic():
    W, H = 900, 420
    im, d = new(W, H)
    for y in (90, 210, 330):
        d.line([(30 * S, y * S), (870 * S, y * S)], fill=(210, 80, 80, 255), width=16 * S)     # myosin (thick)
    for y in (150, 270):
        d.line([(30 * S, y * S), (870 * S, y * S)], fill=(90, 130, 210, 255), width=8 * S)      # actin (thin)
    for x in range(120, 800, 90):
        for y in (90, 210, 330):
            d.line([(x * S, y * S), ((x + 22) * S, (y + 34) * S)], fill=(150, 40, 40, 255), width=6 * S)
    return done(im, W, H)


def load(d):
    return NU.load(d)


def build():
    sc, t0 = load(EP)
    bd = B.Board(3, 2)
    pops, glows = [], []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    cam = bd.camera
    A, Bc, C = (960, 540), (PW + 960, 540), (2 * PW + 960, 540)
    D, E, Fp = (960, PH + 540), (PW + 960, PH + 540), (2 * PW + 960, PH + 540)
    cam(0, *A, 1.0, 0.1)
    Y = PH

    # ---------------- STORY (A)
    s = sc["story"]
    st = [pop(skeleton_pic(), 460, 540, h=900, t=0.3), text("baby: 270 - 300 bones", 1380, 200, 70, GOLD_T, s.t("baby") - 0.4, "c"), text("adult: only 206", 1380, 380, 90, RED_T, s.t("adult") - 0.4, "c"),
          text("nothing was thrown away", 1380, 590, 58, MAROON, s.t("thrown") - 0.5, "c"), text("where did they go?", 1380, 800, 80, PURPLE, s.t("where") - 0.4, "c")]

    # ---------------- OVERVIEW (B)
    s = sc["overview"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, st)
    X = PW
    ov = title("THE MUSCULOSKELETAL SYSTEM", X + 960, 120, s.start + 0.3) + [
        text("BONES", X + 400, 360, 90, GOLD_T, s.t("bones") - 0.3, "c"), text("MUSCLES", X + 960, 360, 90, RED_T, s.t("muscles") - 0.3, "c"), text("TENDONS", X + 1520, 360, 90, GREEN_T, s.t("tendons") - 0.3, "c"),
        text("LIGAMENTS", X + 680, 540, 90, BLUE_T, s.t("ligaments") - 0.3, "c"), text("JOINTS", X + 1260, 540, 90, PURPLE, s.t("joints") - 0.3, "c"),
        text("support - protect - move", X + 960, 840, 82, MAROON, s.t("move") - 1.0, "c")]

    # ---------------- PROTECT (C)
    s = sc["protect"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ov)
    X = 2 * PW
    pr = [pop(skeleton_pic(), X + 460, 540, h=900, t=s.start + 0.3), text("SKULL", X + 1380, 260, 100, GOLD_T, s.t("skull") - 0.3, "c"), text("shields the brain", X + 1380, 380, 58, MAROON, s.t("brain") - 0.4, "c"),
          text("RIB CAGE", X + 1380, 600, 100, BLUE_T, s.t("rib") - 0.3, "c"), text("shields heart + lungs", X + 1380, 720, 50, MAROON, s.t("rib") + 0.2, "c")]

    # ---------------- BONES (D)
    s = sc["bones"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, pr)
    bo = [pop(fuse_pic(), 520, Y + 380, w=800, t=s.start + 0.3) if False else None]
    bo = [pop(skeleton_pic(), 400, Y + 540, h=900, t=s.start + 0.3), text("bones are LIVING tissue", 1380, Y + 170, 68, GREEN_T, s.t("living") - 0.4, "c"),
          text("old bone broken down", 1380, Y + 330, 56, RED_T, s.t("broken") - 0.5, "c"), text("new bone made - all life", 1380, Y + 430, 56, BLUE_T, s.t("made") - 0.6, "c"),
          text("stores CALCIUM", 1380, Y + 620, 64, GOLD_T, s.t("calcium") - 0.4, "c"), text("houses BONE MARROW", 1380, Y + 740, 60, PURPLE, s.t("marrow") - 0.9, "c")]

    # ---------------- FUSION (E)
    s = sc["fusion"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, bo)
    X = PW
    fu = [pop(fuse_pic(), X + 520, Y + 420, w=860, t=s.start + 0.3), text("mystery solved!", X + 1450, Y + 200, 90, GREEN_T, s.t("mystery") - 0.3, "c"), text("separate bones JOIN together", X + 960, Y + 700, 70, GOLD_T, s.t("join") - 0.5, "c"),
          text("adult count = 206", X + 960, Y + 840, 86, RED_T, s.t("206") - 0.6, "c")]

    # ---------------- JOINTS (F)
    s = sc["joints"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, fu)
    X = 2 * PW
    jo = [pop(joint_pic(), X + 480, Y + 500, w=860, t=s.start + 0.3), text("JOINT = where bones meet", X + 1450, Y + 180, 60, PURPLE, s.t("joints") - 0.4, "c"),
          text("LIGAMENT: bone to bone", X + 1450, Y + 380, 62, GREEN_T, s.t("ligaments") - 0.4, "c"), text("keeps joints stable", X + 1450, Y + 470, 48, MAROON, s.t("stable") - 0.5, "c"),
          text("TENDON: muscle to bone", X + 1450, Y + 680, 62, GOLD_T, s.t("tendons") - 0.4, "c")]

    # ---------------- TYPES (A)
    s = sc["types"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, jo)
    ty = [pop(types_pic("skeletal"), 330, 400, w=520, t=s.t("skeletal") - 0.9), text("SKELETAL", 330, 620, 62, RED_T, s.t("skeletal") - 0.3, "c"), text("you control it", 330, 700, 46, MAROON, s.t("control") - 0.6, "c"),
          pop(types_pic("smooth"), 960, 400, w=520, t=s.t("smooth") - 0.9), text("SMOOTH", 960, 620, 62, PURPLE, s.t("smooth") - 0.3, "c"), text("automatic: gut", 960, 700, 46, MAROON, s.t("automatically") - 0.9, "c"),
          pop(types_pic("cardiac"), 1590, 400, w=520, t=s.t("cardiac") - 0.9), text("CARDIAC", 1590, 620, 62, BLUE_T, s.t("cardiac") - 0.3, "c"), text("the heart", 1590, 700, 46, MAROON, s.t("heart") - 0.6, "c"),
          text("600+ muscles", 960, 900, 80, GOLD_T, s.t("hundred") - 0.5, "c")]

    # ---------------- PULL (B)
    s = sc["pull"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, ty)
    X = PW
    pu = [pop(arm_pic(True), X + 480, 440, w=800, t=s.start + 0.3), text("a muscle can only PULL", X + 1450, 160, 62, RED_T, s.t("pull") - 0.3, "c"), text("never push", X + 1450, 260, 70, MAROON, s.t("never") - 0.4, "c"),
          text("BICEPS pulls = elbow bends", X + 1450, 480, 54, RED_T, s.t("biceps") - 0.4, "c"), text("TRICEPS pulls = elbow straightens", X + 1450, 600, 50, BLUE_T, s.t("triceps") - 0.5, "c"),
          text("opposing pairs", X + 960, 900, 80, GOLD_T, s.t("pairs") - 0.5, "c")]

    # ---------------- CONTRACTION (C)
    s = sc["contraction"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, pu)
    X = 2 * PW
    co = [pop(filament_pic(), X + 520, 480, w=860, t=s.start + 0.3), text("MYOSIN (thick)", X + 1450, 250, 64, RED_T, s.t("myosin") - 0.4, "c"), text("ACTIN (thin)", X + 1450, 380, 64, BLUE_T, s.t("actin") - 0.9, "c"),
          text("slide past each other", X + 1450, 520, 56, MAROON, s.t("slide") - 0.5, "c"), text("CALCIUM = switch ON", X + 1450, 700, 60, GOLD_T, s.t("calcium") - 0.4, "c"), text("ATP = energy", X + 1450, 820, 62, GREEN_T, s.t("atp") - 0.6, "c")]

    # ---------------- RECAP (D)
    s = sc["recap"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, co)
    rp = title("remember 3 things", 960, Y + 100, s.start + 0.4)
    for w, a, b, col, tc_, x in (("living", "bones are living tissue", "some join as you grow", PINK, RED_T, 400), ("tendons", "tendon: muscle to bone", "ligament: bone to bone", CREAM, GOLD_T, 960), ("pull", "muscles only pull", "so they work in pairs", SKY, BLUE_T, 1520)):
        tw2 = s.t(w) - 0.3
        rp += [panel(x - 265, Y + 220, x + 265, Y + 600, col, tw2 - 0.2), text(a, x, Y + 360, 36, tc_, tw2, "c"), text(b, x, Y + 470, 34, MAROON, tw2 + 0.6, "c")]
    tn = s.t("lymphatic") - 0.8
    rp += [panel(200, Y + 720, 1720, Y + 890, LILAC, tn - 0.3), text("next: the lymphatic system", 960, Y + 820, 56, PURPLE, tn, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def build_short(n):
    sc, t0 = load(EP / f"short{n}")
    bd = B.Board(3, 2)
    pops, glows = [], []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    cam = bd.camera
    A, Bc, C = (960, 540), (PW + 960, 540), (2 * PW + 960, 540)
    cam(0, *A, 1.0, 0.1)
    if n == 1:
        s = sc["case"]
        a = [pop(skeleton_pic(), 460, 540, h=900, t=0.3), text("a baby is born with", 1400, 260, 62, MAROON, s.t("baby") - 0.5, "c"), text("270 - 300 bones", 1400, 420, 100, GOLD_T, s.t("bones") - 0.8, "c")]
        s = sc["turn"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(fuse_pic(), X + 520, 400, w=860, t=s.start + 0.3), text("an adult has only 206", X + 960, 760, 84, RED_T, s.t("206") - 0.5, "c"), text("where did they go?", X + 960, 920, 76, PURPLE, s.t("where") - 0.5, "c")]
    else:
        s = sc["case"]
        a = [pop(arm_pic(True), 520, 540, w=860, t=0.3), text("a muscle can only PULL", 1440, 300, 70, RED_T, s.t("pull") - 0.4, "c"), text("never push", 1440, 460, 100, MAROON, s.t("push") - 0.4, "c")]
        s = sc["twist"]
        cam(s.start, *Bc, 1.0, 1.0)
        bd.erase(s.start + 0.8, a)
        X = PW
        b = [pop(arm_pic(True), X + 520, 540, w=700, t=s.start + 0.3), pop(arm_pic(False), X + 1400, 540, w=700, t=s.t("straighten") - 0.6), text("bend", X + 520, 880, 76, RED_T, s.t("bend") - 0.3, "c"), text("straighten", X + 1400, 880, 76, BLUE_T, s.t("straighten") - 0.3, "c")]
        s = sc["clue"]
        cam(s.start, *C, 1.0, 1.0)
        bd.erase(s.start + 0.8, b)
        X = 2 * PW
        c = [pop(arm_pic(False), X + 520, 540, w=860, t=s.start + 0.3), text("it only pulls", X + 1450, 300, 70, MAROON, s.t("pulls") - 0.4, "c"), text("so how?", X + 1450, 520, 110, GOLD_T, s.t("how") - 0.4, "c"), text("?", X + 1450, 820, 200, GOLD_T, s.t("elbow") - 0.2, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def make_short(n):
    import package as P
    import bridge
    bd, sc = build_short(n)
    board = NU.render_board(bd, sc, f"musc_story{n}")
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
        P.btext(d, (540, y), ln, size, P.MAROON, "mm")
        y += size + 18
    d.rounded_rectangle((170, 1380, 910, 1490), radius=55, fill=P.MAROON)
    d.text((540, 1435), "FULL VIDEO ON THE CHANNEL", font=P.f(44), fill=(255, 255, 255), anchor="mm", stroke_width=1, stroke_fill=(255, 255, 255))
    d.text((540, 1600), "THE ANATOMY UNFOLDED", font=P.f(46), fill=(150, 120, 130), anchor="mm")
    ov = OUT / f"musc_story{n}_overlay.png"
    top.save(ov)
    sh = OUT / f"musc_short{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(board), "-i", str(ov), "-filter_complex",
                    "color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(sh)], check=True)
    bridge.QUESTIONS["musc"] = [SHORT_Q[1], SHORT_Q[2]]
    bridge.add_bridge(sh, "musc", n - 1)
    print("done ->", sh)


if __name__ == "__main__":
    a = sys.argv[1:] or ["video"]
    if a[0] == "stills":
        bd, sc = build()
        for v in sc.values():
            OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"musc_{v.id}.png")
    elif a[0] == "short":
        if len(a) > 2 and a[2] == "stills":
            bd, sc = build_short(int(a[1]))
            for v in sc.values():
                OF.credit(bd.frame(round(v.start + v.dur - 0.3, 1))).save(OUT / f"mshort{a[1]}_{v.id}.png")
        else:
            make_short(int(a[1]))
    else:
        bd, sc = build()
        f = NU.render_board(bd, sc, "musc", intro=True)
        f.replace(OUT / "final_musc.mp4")
        print("done ->", OUT / "final_musc.mp4")
