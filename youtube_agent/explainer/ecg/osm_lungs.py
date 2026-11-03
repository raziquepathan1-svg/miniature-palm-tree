"""Respiratory series: Lung Anatomy (owner-approved script, narration only)."""
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "lungs")))
SV = HERE.parent / "servier"
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_preview as OP  # noqa: E402
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_bp as BPm  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OF.MAROON, OF.PURPLE, OP.BLUE_T, OP.RED_T, OP.GOLD_T, OF.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OF.PINK, OF.LILAC, OF.CREAM, OF.MINT, OF.SKY
PW, PH = 1920, 1080
AIR = (90, 160, 230)
TUBE = (200, 120, 130)


def sv(name):
    for sub in ("lu", "bpx", "bv", "ha", "mi", ""):
        p = SV / sub / f"{name}.png"
        if p.exists():
            return Image.open(p).convert("RGBA")
    raise FileNotFoundError(name)


def branch(x, y, ang, length, depth, out):
    """recursive airway tree as line segments (x, y, angle in degrees from straight down)."""
    if depth == 0 or length < 12:
        return
    a = math.radians(ang)
    x2, y2 = x + length * math.sin(a), y + length * math.cos(a)
    out.append(((x, y), (x2, y2), depth))
    for d_ang in (-28, 28):
        branch(x2, y2, ang + d_ang, length * 0.72, depth - 1, out)


class Sc(BPm.Sc):
    def __init__(self, sid, text, start):
        import render as R
        self.id, self.text, self.start = sid, text, start
        self.audio = EP / "audio" / f"{sid}.wav"
        self.dur = R.dur(self.audio)
        self.words = text.lower().replace(",", "").replace(".", "").replace("?", "").replace(":", "").split()


def build():
    data = json.load(open(EP / "script.json"))
    sc, t0 = {}, 0.0
    for s in data:
        sc[s["id"]] = Sc(s["id"], s["text"], t0)
        t0 += sc[s["id"]].dur
    bd = B.Board(3, 2)
    pops, glows, flows = [], [], []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    add, cam = bd.add, bd.camera
    A, Bc, C = (960, 540), (PW + 960, 540), (2 * PW + 960, 540)
    D, E, Fp = (960, PH + 540), (PW + 960, PH + 540), (2 * PW + 960, PH + 540)
    cam(0, *A, 1.0, 0.1)

    def F(pic, fx, fy):
        return pic.map((fx * pic.src.width, fy * pic.src.height))

    def seg(p, q, t, col=TUBE, w=10, dur=0.35):
        return add(B.Stroke([p, q], col, w, t=t, dur=dur, arrow=False))

    def tree(x, y, t, scale=1.0, dur=2.5, depth=6, col=TUBE):
        segs = []
        branch(x, y, 0, 150 * scale, depth, segs)
        items = []
        maxd = depth
        for p, q, d in segs:
            lvl = maxd - d
            items.append(seg(p, q, t + lvl * dur / maxd, col, max(3, int(3 + d * 2.2 * scale)), dur / maxd))
        return items, segs

    # ---------------- HOOK (A)
    s = sc["hook"]
    bo = pop(sv("Male-silhouette"), 480, 600, h=980, t=0.3)
    lu = pop(sv("poumons_01"), 495, 470, h=330, t=s.t("tree") - 0.2)
    hk = [bo, lu, text("every breath", 1380, 170, 72, BLUE_T, s.t("breath"), "c"),
          text("travels down a tree", 1380, 250, 50, MAROON, s.t("tree"), "c")]
    tr_items, _ = tree(1380, 360, s.t("pipe") - 0.3, scale=1.0, dur=3.0, depth=6)
    hk += tr_items
    hk += [text("1 pipe in your neck", 1550, 380, 38, MAROON, s.t("pipe")),
           text("-> hundreds of millions of air sacs", 1380, 960, 44, PURPLE, s.t("millions"), "c")]

    # ---------------- UPPER AIRWAY (B)
    s = sc["upper"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, hk + [bo, lu])
    X = PW
    head = pop(sv("Male-silhouette").crop((150, 0, 520, 380)), X + 420, 480, h=760, t=s.start + 0.3)
    nose, phar, lar, neck = F(head, 0.92, 0.42), F(head, 0.62, 0.55), F(head, 0.62, 0.8), F(head, 0.6, 0.98)
    path = [nose, (nose[0] - 60, nose[1] - 10), phar, lar, neck]
    up = [head, add(B.Stroke(B.smooth(path, 10), AIR, 12, t=s.start + 0.8, dur=1.5, arrow=True)),
          text("nose", X + 900, 220, 52, BLUE_T, s.t("nose")), lead([(X + 890, 225), (nose[0] + 20, nose[1])], s.t("nose") + 0.3, BLUE_T, 5),
          text("warms, wets + filters air", X + 1060, 290, 38, MAROON, s.t("warms")),
          text("pharynx (throat)", X + 900, 420, 50, PURPLE, s.t("pharynx")), lead([(X + 890, 425), (phar[0] + 20, phar[1])], s.t("pharynx") + 0.3, PURPLE, 5),
          text("larynx (voice box)", X + 900, 560, 50, GOLD_T, s.t("larynx")), lead([(X + 890, 565), (lar[0] + 20, lar[1])], s.t("larynx") + 0.3, GOLD_T, 5)]
    te = s.t("epiglottis")
    up += [pop(sv("Larynx"), X + 1600, 740, h=420, t=te - 0.2),
           panel(X + 820, 680, X + 1420, 940, MINT, te - 0.3), text("epiglottis", X + 1120, 750, 54, GREEN_T, te, "c"),
           text("flap covers the airway", X + 1120, 820, 38, MAROON, s.t("covers"), "c"),
           text("when you swallow", X + 1120, 880, 38, MAROON, s.t("swallow"), "c")]

    # ---------------- TRACHEA (C)
    s = sc["trachea"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, up + [head])
    X = 2 * PW
    lx = pop(sv("Larynx"), X + 380, 560, h=900, t=s.start + 0.3)
    rings = F(lx, 0.5, 0.82)
    tc = [lx, text("trachea", X + 980, 140, 76, BLUE_T, s.t("trachea"), "c"), text("(windpipe)", X + 980, 215, 44, MAROON, s.t("windpipe"), "c"),
          text("C-shaped cartilage rings", X + 780, 330, 46, GOLD_T, s.t("c-shaped")),
          lead([(X + 770, 335), (rings[0] + 60, rings[1] - 60)], s.t("c-shaped") + 0.4, GOLD_T, 5),
          text("never collapses", X + 780, 400, 40, MAROON, s.t("collapses"))]
    tm = s.t("mucus")
    tc += [pop(sv("bronche_saine"), X + 1000, 760, h=380, t=tm - 0.3),
           panel(X + 1260, 560, X + 1840, 960, CREAM, tm - 0.3), text("mucus traps dust", X + 1550, 640, 44, GOLD_T, tm, "c"),
           text("+ germs", X + 1550, 700, 44, GOLD_T, s.t("germs"), "c"),
           text("cilia sweep it", X + 1550, 800, 44, PURPLE, s.t("cilia"), "c"), text("back up to the throat", X + 1550, 860, 40, MAROON, s.t("sweep"), "c")]
    glows.append((s.t("cilia"), (X + 1000, 760), 3.0, 80))

    # ---------------- BRONCHI (D)
    s = sc["bronchi"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, tc + [lx])
    cx, ty = 960, PH + 160
    split = (cx, PH + 460)
    # patient's right = viewer's left: wider, shorter, more upright
    rb = [split, (cx - 120, PH + 640), (cx - 170, PH + 860)]
    lb = [split, (cx + 200, PH + 600), (cx + 380, PH + 760)]
    ts_ = s.t("splits")
    br = [add(B.Stroke([(cx, ty), split], TUBE, 46, t=s.start + 0.4, dur=0.8, arrow=False)),
          add(B.Stroke(B.smooth(rb, 8), TUBE, 40, t=ts_, dur=0.8, arrow=False)),
          add(B.Stroke(B.smooth(lb, 8), TUBE, 28, t=ts_ + 0.3, dur=0.8, arrow=False)),
          text("trachea", cx + 60, PH + 260, 44, BLUE_T, s.start + 0.6),
          text("2 main bronchi", cx, PH + 110, 60, MAROON, ts_, "c"),
          text("RIGHT", cx - 560, PH + 520, 56, RED_T, s.t("right")), text("(patient's right)", cx - 580, PH + 580, 34, MAROON, s.t("right") + 0.3),
          text("LEFT", cx + 420, PH + 520, 56, BLUE_T, s.t("lung"))]
    tw = s.t("wider")
    br += [panel(cx - 760, PH + 650, cx - 220, PH + 900, PINK, tw - 0.3), text("wider, shorter,", cx - 490, PH + 730, 44, RED_T, tw, "c"),
           text("more upright", cx - 490, PH + 800, 44, RED_T, s.t("upright"), "c"),
           panel(cx + 230, PH + 830, cx + 900, PH + 1010, CREAM, s.t("inhaled") - 0.3),
           text("inhaled objects -> right", cx + 565, PH + 900, 40, GOLD_T, s.t("inhaled"), "c"),
           text("more often", cx + 565, PH + 960, 38, MAROON, s.t("often"), "c")]
    flows.append(([(cx, ty + 40), split, rb[1], rb[2]], s.t("inhaled"), s.end, (230, 150, 40)))

    # ---------------- LOBES (E)
    s = sc["lobes"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, br)
    X = PW
    lg = pop(sv("poumons_01"), X + 700, PH + 560, h=760, t=s.start + 0.3)
    rl, ll = F(lg, 0.22, 0.55), F(lg, 0.8, 0.55)
    lo = [lg, text("not twins!", X + 700, PH + 110, 66, PURPLE, s.t("twins"), "c")]
    t3, t2 = s.t("three"), s.t("only")
    lo += [text("right lung", X + 120, PH + 300, 50, RED_T, t3 - 0.5), text("3 lobes", X + 120, PH + 370, 64, RED_T, t3),
           lead([(X + 300, PH + 400), (rl[0], rl[1])], t3 + 0.3, RED_T, 5),
           text("left lung", X + 1300, PH + 300, 50, BLUE_T, t2 - 0.5), text("2 lobes", X + 1300, PH + 370, 64, BLUE_T, t2),
           lead([(X + 1290, PH + 400), (ll[0], ll[1])], t2 + 0.3, BLUE_T, 5)]
    tn = s.t("cardiac") - 0.9
    notch = F(lg, 0.62, 0.72)
    glows.append((s.t("heart"), notch, 4.0, 90))
    lo += [panel(X + 1240, PH + 650, X + 1840, PH + 900, PINK, s.t("heart") - 0.3), text("room for the heart", X + 1540, PH + 730, 44, RED_T, s.t("heart"), "c"),
           text("= cardiac notch", X + 1540, PH + 820, 50, PURPLE, tn, "c"),
           lead([(X + 1240, PH + 760), (notch[0] + 20, notch[1])], tn + 0.3, PURPLE, 5)]

    # ---------------- BRONCHIAL TREE (F)
    s = sc["tree"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, lo + [lg])
    X = 2 * PW
    tt_items, segs = tree(X + 640, PH + 160, s.t("branching") - 0.4, scale=1.35, dur=4.0, depth=7)
    tb = tt_items + [text("bronchi", X + 1240, PH + 250, 50, MAROON, s.t("bronchi")),
                     text("-> bronchioles", X + 1240, PH + 340, 50, PURPLE, s.t("bronchioles")),
                     text("like an upside-down tree", X + 1240, PH + 460, 44, GREEN_T, s.t("upside")),
                     text("-> clusters of air sacs", X + 1240, PH + 580, 50, BLUE_T, s.t("clusters"))]
    leaves = [q for p, q, d in segs if d == 1]
    tsacs = s.t("sacs") - 0.4
    for k, q in enumerate(leaves[::2]):
        glows.append((tsacs + 0.02 * k, q, s.end - tsacs, 18))
    tb.append(pop(sv("poumon_07"), X + 1500, PH + 820, h=330, t=tsacs))

    # ---------------- ALVEOLI (A)
    s = sc["alveoli"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, tb)
    al = [pop(sv("poumon_10"), 480, 560, h=900, t=s.start + 0.3),
          text("alveoli", 1340, 160, 90, BLUE_T, s.t("alveoli"), "c"), text("(tiny air sacs)", 1340, 245, 44, MAROON, s.t("alveoli") + 0.5, "c"),
          text("hundreds of millions per lung", 1340, 350, 46, PURPLE, s.t("millions"), "c"),
          text("very thin walls", 1340, 450, 46, GOLD_T, s.t("thin"), "c"),
          text("wrapped in capillaries", 1340, 530, 46, RED_T, s.t("capillaries"), "c"),
          panel(960, 640, 1740, 900, SKY, s.t("spread") - 0.3), text("spread out flat:", 1350, 710, 44, MAROON, s.t("spread"), "c"),
          text("~ a badminton court", 1350, 800, 58, BLUE_T, s.t("badminton") - 0.4, "c")]

    # ---------------- GAS EXCHANGE (B)
    s = sc["exchange"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, al)
    X = PW
    ex = [text("gas exchange", X + 960, 110, 76, PURPLE, s.start + 0.3, "c"),
          panel(X + 200, 260, X + 860, 860, SKY, s.start + 0.5), text("alveolus (air)", X + 530, 320, 46, BLUE_T, s.start + 0.7, "c"),
          panel(X + 1060, 260, X + 1720, 860, PINK, s.start + 0.6), text("capillary (blood)", X + 1390, 320, 46, RED_T, s.start + 0.8, "c"),
          add(B.Stroke([(X + 960, 250), (X + 960, 880)], (150, 130, 140), 6, t=s.start + 0.6, dur=0.4, arrow=False)),
          text("thin wall", X + 960, 930, 38, MAROON, s.start + 0.9, "c")]
    to, tco = s.t("oxygen"), s.t("carbon")
    for k in range(3):
        y = 440 + k * 60
        ex.append(lead([(X + 560, y), (X + 1300, y)], to + 0.2 * k, RED_T, 8, 0.6, arrow=True))
        y2 = 680 + k * 60
        ex.append(lead([(X + 1300, y2), (X + 560, y2)], tco + 0.2 * k, BLUE_T, 8, 0.6, arrow=True))
    ex += [text("O2 -> into the blood", X + 960, 400, 46, RED_T, to + 0.3, "c"), text("CO2 -> out, breathed away", X + 960, 640, 46, BLUE_T, tco + 0.3, "c")]

    # ---------------- PLEURA + DIAPHRAGM (C)
    s = sc["pleura"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ex)
    X = 2 * PW
    lg2 = pop(sv("poumons_01"), X + 560, 500, h=640, t=s.start + 0.3)
    tp = s.t("pleura")
    pl = [lg2, text("pleura", X + 1340, 170, 76, PURPLE, tp, "c"), text("2 thin layers + a little fluid", X + 1340, 255, 42, MAROON, s.t("layers") + 0.3, "c"),
          text("lungs glide smoothly", X + 1340, 340, 46, GREEN_T, s.t("glide"), "c"),
          add(B.Stroke(B.smooth([F(lg2, 0.01, 0.9), F(lg2, 0.03, 0.45), F(lg2, 0.16, 0.13), F(lg2, 0.33, 0.12), F(lg2, 0.43, 0.5)], 10),
                       PURPLE, 6, t=tp, dur=1.0, arrow=False)),
          add(B.Stroke(B.smooth([(p_[0] - 14, p_[1]) for p_ in (F(lg2, 0.01, 0.9), F(lg2, 0.03, 0.45))] +
                                [(p_[0], p_[1] - 14) for p_ in (F(lg2, 0.16, 0.13), F(lg2, 0.33, 0.12))], 10),
                       (160, 120, 200), 5, t=tp + 0.4, dur=1.0, arrow=False))]
    td = s.t("dome") - 0.6
    dome = [(X + 120, 900), (X + 300, 830), (X + 560, 800), (X + 820, 830), (X + 1000, 900)]
    pl += [add(B.Stroke(B.smooth(dome, 10), (190, 80, 90), 26, t=s.t("dome") - 0.3, dur=1.0, arrow=False)),
           text("diaphragm", X + 1340, 760, 70, RED_T, td, "c"), text("dome-shaped muscle below", X + 1340, 840, 42, MAROON, td + 0.2, "c")]

    # ---------------- SUMMARY (D)
    s = sc["summary"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, pl + [lg2])
    sm = title("the path of air", 960, PH + 100, s.start + 0.4)
    steps = [("nose", "nose"), ("pharynx", "pharynx"), ("larynx", "larynx"), ("trachea", "trachea"), ("bronchi", "bronchi"),
             ("bronchioles", "bronchioles"), ("alveoli", "alveoli")]
    for i, (w, lab) in enumerate(steps):
        tt = s.t(w)
        x = 150 + i * 270
        sm += [panel(x - 125, PH + 230, x + 125, PH + 330, [SKY, MINT, CREAM, SKY, MINT, CREAM, PINK][i], tt - 0.2),
               text(lab, x, PH + 293, 34, MAROON, tt, "c")]
        if i:
            sm.append(lead([(x - 150, PH + 280), (x - 128, PH + 280)], tt - 0.2, MAROON, 4, 0.2, arrow=True))
    sm += [text("gas exchange happens in the alveoli", 960, PH + 420, 46, RED_T, s.t("gas"), "c"),
           panel(300, PH + 520, 900, PH + 700, PINK, s.t("three") - 0.3), text("right lung: 3 lobes", 600, PH + 625, 48, RED_T, s.t("three"), "c"),
           panel(1020, PH + 520, 1620, PH + 700, SKY, s.t("two") - 0.3), text("left lung: 2 lobes", 1320, PH + 625, 48, BLUE_T, s.t("two"), "c")]
    tn = s.t("next")
    sm += [panel(360, PH + 790, 1560, PH + 950, LILAC, tn - 0.3), text("next: how breathing works", 960, PH + 890, 52, PURPLE, tn, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
        from PIL import ImageDraw
        d = ImageDraw.Draw(crop)
        for pts_, ta, tb2, col in flows:
            if ta <= t <= tb2:
                u = min(1.0, (t - ta) / 1.6)
                cx_, cy_ = ctx.px(B.partial_pts(pts_, u)[-1])
                r = 16 * B.BS
                d.ellipse((cx_ - r, cy_ - r, cx_ + r, cy_ + r), fill=col, outline=(90, 60, 20), width=int(3 * B.BS))
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render(out="lung_anatomy.mp4"):
    import subprocess
    import render_ecg as RE
    bd, sc = build()
    vid = HERE / "lungs_video_only.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080",
                           "-r", "30", "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", str(vid)], stdin=subprocess.PIPE)
    for f in range(int(round(RE.INTRO_DUR * 30))):
        ff.stdin.write(RE.intro_frame(f / 30).tobytes())
    for f in range(int(bd.total * 30)):
        ff.stdin.write(OF.credit(bd.frame(f / 30)).tobytes())
    ff.stdin.close()
    ff.wait()
    RE.intro_audio(HERE / "chime_intro.wav")
    lst = HERE / f"{out}.txt"
    with open(lst, "w") as fh:
        fh.write(f"file '{HERE / 'chime_intro.wav'}'\n")
        for s in sc.values():
            fh.write(f"file '{s.audio}'\n")
    wav = HERE / f"{out}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "pcm_s16le", str(wav)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(wav), "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", str(HERE / ("final_" + out))], check=True)
    print("done ->", HERE / ("final_" + out))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        bd, sc = build()
        ends = [round(v.start + v.dur - 0.3, 1) for v in sc.values()]
        for t in ends:
            OF.credit(bd.frame(t)).save(HERE / f"lungs_{t:06.1f}.png")
        print("ok", round(bd.total, 1), ends)
    else:
        render()
