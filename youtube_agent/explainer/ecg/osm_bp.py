"""Cardiovascular series: Blood Pressure (approved blueprint, professor style, narration only)."""
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "bp")))
SV = HERE.parent / "servier"
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_preview as OP  # noqa: E402
import osm_full as OF  # noqa: E402
import osm_mi as OM  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_hphys as HP  # noqa: E402
import osm_bv as BV  # noqa: E402

MAROON, PURPLE, TEAL, BLUE_T, RED_T, GOLD_T, GREEN_T = OF.MAROON, OF.PURPLE, OF.TEAL, OP.BLUE_T, OP.RED_T, OP.GOLD_T, OF.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OF.PINK, OF.LILAC, OF.CREAM, OF.MINT, OF.SKY
PW, PH = 1920, 1080


def sv(name):
    for sub in ("bpx", "bv", "ha", "mi", ""):
        p = SV / sub / f"{name}.png"
        if p.exists():
            return Image.open(p).convert("RGBA")
    raise FileNotFoundError(name)


def cuff_pic():
    S = 3
    im = Image.new("RGBA", (520 * S, 420 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20 * S, 40 * S, 240 * S, 260 * S), radius=30 * S, fill=(150, 175, 215), outline=(60, 80, 130), width=5 * S)
    for k in range(4):
        d.line([(40 * S, (80 + k * 45) * S), (220 * S, (80 + k * 45) * S)], fill=(120, 145, 190), width=3 * S)
    d.line([(240 * S, 150 * S), (330 * S, 150 * S), (360 * S, 220 * S)], fill=(60, 60, 70), width=6 * S, joint="curve")
    cx, cy, r = 400 * S, 300 * S, 95 * S
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(250, 250, 252), outline=(60, 60, 70), width=7 * S)
    for k in range(13):
        a = math.radians(150 + k * 20)
        d.line([(cx + 0.78 * r * math.cos(a), cy + 0.78 * r * math.sin(a)), (cx + 0.92 * r * math.cos(a), cy + 0.92 * r * math.sin(a))],
               fill=(60, 60, 70), width=3 * S)
    d.arc((cx - 0.9 * r, cy - 0.9 * r, cx + 0.9 * r, cy + 0.9 * r), 330, 390, fill=(255, 30, 39), width=8 * S)
    a = math.radians(300)
    d.line([(cx, cy), (cx + 0.75 * r * math.cos(a), cy + 0.75 * r * math.sin(a))], fill=(200, 30, 40), width=6 * S)
    d.ellipse((cx - 10 * S, cy - 10 * S, cx + 10 * S, cy + 10 * S), fill=(60, 60, 70))
    return im.resize((520, 420), Image.LANCZOS)


def hose_pic():
    S = 3
    im = Image.new("RGBA", (900 * S, 360 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20 * S, 60 * S, 130 * S, 130 * S), radius=15 * S, fill=(190, 195, 205), outline=(80, 85, 95), width=5 * S)
    d.rectangle((60 * S, 20 * S, 90 * S, 60 * S), fill=(190, 195, 205), outline=(80, 85, 95), width=5 * S)
    pts = [(130, 95), (300, 110), (450, 200), (620, 230), (860, 200)]
    q = [(x * S, y * S) for x, y in B.smooth(pts, 12)]
    d.line(q, fill=(40, 120, 60), width=70 * S, joint="curve")
    d.line(q, fill=(110, 190, 120), width=56 * S, joint="curve")
    d.line(q, fill=(120, 180, 240), width=30 * S, joint="curve")
    return im.resize((900, 360), Image.LANCZOS)


class Sc(HA.Sc):
    def __init__(self, sid, text, start):
        import render as R
        self.id, self.text, self.start = sid, text, start
        self.audio = EP / "audio" / f"{sid}.wav"
        self.dur = R.dur(self.audio)
        self.words = text.lower().replace(",", "").replace(".", "").replace("?", "").replace(":", "").split()


def wave(x):
    """arterial pressure shape, 0..1 over one beat: fast rise, notch, decay (0 = diastolic, 1 = systolic)."""
    if x < 0.15:
        return math.sin(math.pi / 2 * x / 0.15)
    if x < 0.35:
        return 1 - 0.45 * (x - 0.15) / 0.2
    if x < 0.4:
        return 0.55 + 0.08 * math.sin(math.pi * (x - 0.35) / 0.05)
    return 0.55 * (1 - (x - 0.4) / 0.6) ** 1.3


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

    # ---------------- HOOK
    s = sc["hook"]
    arm = pop(sv("Bras"), 560, 560, w=900, t=0.3)
    cuff = pop(cuff_pic(), 450, 640, w=520, t=0.9)
    th = s.t("one")
    hk = [arm, cuff, text("120 / 80", 1450, 380, 130, RED_T, th, "c"), text("?", 1450, 560, 140, PURPLE, s.t("mean") - 0.2, "c")]
    cam(th, 1000, 500, 1.12, 1.2)

    # ---------------- WHAT: hose -> artery
    s = sc["what"]
    cam(s.start, *A, 1.0, 0.8)
    bd.erase(s.start, hk)
    tp = s.t("push")
    art = pop(sv("Artere_coupe_sang"), 470, 560, h=700, t=s.start + 0.2)
    ctr = F(art, 0.62, 0.55)
    wt = [art, text("blood pressure", 1000, 230, 64, RED_T, s.start + 0.6), text("= push on artery walls", 1000, 300, 44, MAROON, tp)]
    for k, ang in enumerate((-60, 0, 60, 180)):
        a = math.radians(ang)
        wt.append(lead([(ctr[0] + 30 * math.cos(a), ctr[1] + 60 * math.sin(a)), (ctr[0] + 150 * math.cos(a), ctr[1] + 170 * math.sin(a))],
                       tp + 0.2 + k * 0.15, RED_T, 6, 0.3, arrow=True))
    tg = s.t("garden")
    hose = pop(hose_pic(), 1400, 600, w=760, t=tg - 0.2)
    wt += [hose, text("heart = tap", 1080, 870, 46, BLUE_T, s.t("tap", 2)), text("arteries = hose", 1080, 940, 46, RED_T, s.t("arteries", 2) - 0.4)]

    # ---------------- SYSTOLIC (heart page)
    s = sc["systolic"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, wt)
    hs = pop(OP.HEART, PW + 560, 590, h=880, t=s.start + 0.3)
    M = lambda k: hs.map(OP.P[k])
    lv = M("LV")
    glows.append((s.t("squeezes"), lv, 2.5, 150))
    lp = [hs.map(p) for p in HP.LEFT_PATH[3:]]
    flows.append((lp, s.t("pushes"), s.end + 0.5, (255, 30, 39)))
    gx0, gx1, gy0, gy1 = PW + 1080, PW + 1840, 260, 760
    sy = [add(B.Stroke([(gx0, gy0 - 30), (gx0, gy1), (gx1, gy1)], (90, 90, 100), 5, t=s.start + 0.5, dur=0.6, arrow=False)),
          text("pressure", gx0 - 10, gy0 - 110, 34, MAROON, s.start + 0.8)]
    pts = [(gx0 + 20 + x * 700, gy1 - 80 - wave(x) * 340) for x in [i / 80 for i in range(81)]]
    rise = [p for p, x in zip(pts, [i / 80 for i in range(81)]) if x <= 0.16]
    fall = [p for p, x in zip(pts, [i / 80 for i in range(81)]) if x >= 0.15]
    sy += [add(B.Stroke(rise, (255, 30, 39), 7, t=s.t("up"), dur=0.6)), text("systolic", pts[12][0] - 20, pts[12][1] - 60, 54, RED_T, s.t("systolic"), "c"),
           text("= top number", pts[12][0] + 140, pts[12][1] - 5, 34, MAROON, s.t("top"))]

    # ---------------- DIASTOLIC
    s = sc["diastolic"]
    aorta = hs.map((250, 110))
    sy += [add(B.Stroke(fall, (0, 85, 255), 7, t=s.t("relaxes"), dur=3.0)),
           text("doesn't fall to zero", gx0 + 20, gy1 + 115, 32, PURPLE, s.t("zero"))]
    for k in range(4):
        glows.append((s.t("springs") + k * 0.6, aorta, 0.5, 90))
    sy += [text("aorta springs back", PW + 200, 140, 42, RED_T, s.t("springs")),
           lead([(PW + 480, 150), (aorta[0] - 30, aorta[1] - 20)], s.t("springs") + 0.4, RED_T)]
    sy += [text("diastolic", gx1 - 150, gy1 - 270, 54, BLUE_T, s.t("diastolic"), "c"),
           text("= bottom number", gx1 - 150, gy1 + 55, 34, MAROON, s.t("bottom"), "c")]

    # ---------------- MEASURE (cuff page, zoom into artery under the cuff)
    s = sc["measure"]
    cam(s.start, *C, 1.0, 1.1)
    bd.erase(s.start + 1.0, sy + [hs])
    X = 2 * PW
    arm2 = pop(sv("Bras"), X + 520, 360, w=880, t=s.start + 0.4)
    cuff2 = pop(cuff_pic(), X + 340, 440, w=480, t=s.start + 0.6)
    ms = [arm2, cuff2, text("mmHg", X + 1450, 200, 80, MAROON, s.t("millimeters"), "c"),
          text("millimeters of mercury", X + 1450, 280, 36, MAROON, s.t("mercury"), "c")]
    tsq = s.t("squeezes")
    # artery under the cuff drawn as a tube: blocked -> spurts -> smooth
    ay = 760
    tube = [add(B.Stroke([(X + 200, ay - 50), (X + 1300, ay - 50)], (200, 60, 70), 8, t=tsq, dur=0.6)),
            add(B.Stroke([(X + 200, ay + 50), (X + 1300, ay + 50)], (200, 60, 70), 8, t=tsq, dur=0.6)),
            add(B.Stroke([(X + 650, ay - 50), (X + 650, ay + 50)], (60, 80, 130), 14, t=tsq + 0.6, dur=0.3)),
            text("artery squeezed shut", X + 750, ay - 90, 34, PURPLE, tsq + 0.6)]
    ts1, ts2 = s.t("systolic"), s.t("diastolic")
    tube += [panel(X + 1350, 600, X + 1880, 720, PINK, ts1 - 0.4), text("first spurt = systolic", X + 1380, 670, 38, RED_T, ts1 - 0.2),
             panel(X + 1350, 760, X + 1880, 880, SKY, ts2 - 1.2), text("smooth flow = diastolic", X + 1380, 830, 38, BLUE_T, ts2 - 1.0)]
    flows.append(([(X + 210, ay), (X + 640, ay)], s.t("lets") - 0.2, ts1, (255, 30, 39)))
    flows.append(([(X + 210, ay), (X + 1290, ay)], ts1, s.end, (255, 30, 39)))
    ms += tube

    # ---------------- NUMBERS (page D)
    s = sc["numbers"]
    cam(s.start, *D, 1.0, 1.1)
    bd.erase(s.start + 1.0, ms)
    nb = title("adult blood pressure", D[0], PH + 110, s.start + 0.4)
    rows = [("normal", "below 120 / 80", (222, 244, 228), GREEN_T, s.t("normal")),
            ("elevated", "120-129 and below 80", (253, 243, 205), GOLD_T, s.t("elevated")),
            ("high", "130 / 80 or higher", (252, 222, 226), RED_T, s.t("high"))]
    for i, (a, b, col, tc, tt) in enumerate(rows):
        y = PH + 230 + i * 170
        nb += [panel(220, y, 1700, y + 140, col, tt - 0.3), text(a, 280, y + 90, 60, tc, tt), text(b, 900, y + 90, 54, MAROON, tt + 0.4)]
    te = s.t("exam")
    nb += [panel(420, PH + 790, 1500, PH + 940, LILAC, te - 0.3), text("exam tip: top OR bottom high", 960, PH + 885, 54, PURPLE, te, "c")]

    # ---------------- FORMULA (page E)
    s = sc["formula"]
    cam(s.start, *E, 1.0, 1.1)
    bd.erase(s.start + 1.0, nb)
    X = PW
    tf = s.t("formula")
    fo = [text("BP = cardiac output x resistance", X + 960, PH + 200, 72, MAROON, tf, "c")]
    fo += [add(B.Stroke([(X + 300, PH + 250), (X + 1620, PH + 247)], GOLD_T, 6, t=tf + 1.8, dur=0.5))]
    tn = s.t("narrower")
    fo += [pop(BV.ring(150, 45, (240, 170, 160, 255), (255, 30, 39, 255), RED_T), X + 560, PH + 580, h=330, t=tn - 0.3),
           text("narrow vessel", X + 560, PH + 800, 44, RED_T, tn, "c"), text("pressure up", X + 560, PH + 860, 50, RED_T, s.t("higher"), "c"),
           pop(BV.ring(150, 120, (240, 170, 160, 255), (255, 30, 39, 255), BLUE_T), X + 1360, PH + 580, h=330, t=s.t("wider") - 0.3),
           text("wide vessel", X + 1360, PH + 800, 44, BLUE_T, s.t("wider"), "c"), text("pressure down", X + 1360, PH + 860, 50, BLUE_T, s.t("lower"), "c")]

    # ---------------- BARORECEPTORS (page F)
    s = sc["baroreceptors"]
    cam(s.start, *Fp, 1.0, 1.1)
    bd.erase(s.start + 1.0, fo)
    X = 2 * PW
    head = sv("aorte2").crop((0, 0, 816, 1000))
    hb = pop(head, X + 480, PH + 560, h=980, t=s.start + 0.4)
    car, arch, brain = F(hb, 0.47, 0.70), F(hb, 0.40, 0.81), F(hb, 0.45, 0.25)
    tb = s.t("baroreceptors")
    br = [hb, text("baroreceptors", X + 1150, PH + 200, 60, GOLD_T, tb), text("pressure sensors", X + 1150, PH + 265, 38, MAROON, tb + 0.6),
          text("carotid artery (neck)", X + 1150, PH + 380, 40, RED_T, s.t("carotid")),
          lead([(X + 1145, PH + 375), (car[0] + 12, car[1])], s.t("carotid") + 0.4, GOLD_T, 5),
          text("aortic arch", X + 1150, PH + 470, 40, RED_T, s.t("arch")),
          lead([(X + 1145, PH + 465), (arch[0] + 20, arch[1])], s.t("arch") + 0.4, GOLD_T, 5)]
    glows += [(s.t("carotid"), car, 6.0, 40), (s.t("arch"), arch, 5.0, 50)]
    tbrn = s.t("brain")
    flows.append(([car, (car[0] - 20, car[1] - 120), brain], tbrn - 0.4, tbrn + 2.0, (255, 215, 0)))
    br += [panel(X + 1120, PH + 560, X + 1860, PH + 900, CREAM, s.t("drops") - 0.3), text("pressure drops", X + 1160, PH + 630, 44, PURPLE, s.t("drops")),
           text("(standing up fast)", X + 1160, PH + 690, 32, MAROON, s.t("stand")),
           text("-> heart speeds up", X + 1160, PH + 770, 40, RED_T, s.t("speeds")), text("-> vessels tighten", X + 1160, PH + 840, 40, RED_T, s.t("tighten") - 0.8)]

    # ---------------- KIDNEYS (back to page E region: reuse page D? use E)
    s = sc["kidneys"]
    cam(s.start, *E, 1.0, 1.1)
    bd.erase(s.start + 1.0, br + [hb])
    X = PW
    kd = pop(sv("rein_01"), X + 300, PH + 560, h=560, t=s.start + 0.4)
    ki = [kd, text("long-term control", X + 300, PH + 180, 46, MAROON, s.start + 0.6, "c"), text("kidneys", X + 300, PH + 900, 52, MAROON, s.t("kidneys"), "c")]
    chain = [("renin", "renin", "from the kidneys", s.t("renin", 1), CREAM, GOLD_T),
             ("two", "angiotensin II", "tightens vessels", s.t("two"), PINK, RED_T),
             ("aldosterone", "aldosterone", "keeps salt + water", s.t("aldosterone", 2), SKY, BLUE_T)]
    for i, (w, nm, desc, tt, col, tc) in enumerate(chain):
        y = PH + 240 + i * 230
        ki += [panel(X + 700, y, X + 1500, y + 170, col, tt - 0.3), text(nm, X + 740, y + 75, 54, tc, tt), text(desc, X + 740, y + 140, 36, MAROON, tt + 0.6)]
        if i:
            ki.append(lead([(X + 1100, y - 55), (X + 1100, y - 5)], tt - 0.4, MAROON, 6, 0.3, arrow=True))
    ki += [text("more fluid", X + 1530, PH + 830, 40, BLUE_T, s.t("fluid") - 1.0), text("= more pressure", X + 1530, PH + 890, 40, RED_T, s.t("fluid") - 0.3)]
    ki.append(lead([(X + 500, PH + 500), (X + 690, PH + 320)], s.t("renin", 1), GOLD_T, 6, 0.4, arrow=True))

    # ---------------- SUMMARY (page D)
    s = sc["summary"]
    cam(s.start, *D, 1.0, 1.1)
    bd.erase(s.start + 1.0, ki)
    sm = title("remember 3 things", D[0], PH + 110, s.start + 0.6)
    cards = [("top", "top number", "heart squeezing", PINK, RED_T, 400), ("bottom", "bottom number", "heart relaxing", SKY, BLUE_T, 960),
             ("equals", "BP = CO x R", "output x resistance", CREAM, GOLD_T, 1520)]
    for w, a, b, col, tc, x in cards:
        tt = s.t(w) - 0.3
        sm += [panel(x - 260, PH + 260, x + 260, PH + 620, col, tt - 0.2), text(a, x, PH + 400, 54, tc, tt, "c"), text(b, x, PH + 500, 38, MAROON, tt + 0.5, "c")]
    tn = s.t("next")
    sm += [panel(460, PH + 760, 1460, PH + 920, LILAC, tn), text("next: when blood pressure stays too high", 960, PH + 860, 44, PURPLE, tn + 0.3, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
        d = ImageDraw.Draw(crop)
        for pts_, ta, tb2, col in flows:
            if ta <= t <= tb2:
                gap = 0.12
                u = ((t - ta) * 0.25) % gap
                while u <= 1.0:
                    cx_, cy_ = ctx.px(B.partial_pts(pts_, u)[-1])
                    r = 11 * B.BS
                    d.ellipse((cx_ - r, cy_ - r, cx_ + r, cy_ + r), fill=col, outline=(255, 255, 255), width=int(3 * B.BS))
                    u += gap
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render(out="blood_pressure.mp4"):
    import subprocess
    import render_ecg as RE
    bd, sc = build()
    vid = HERE / "bp_video_only.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080",
                           "-r", "30", "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", str(vid)], stdin=subprocess.PIPE)
    for f in range(int(round(RE.INTRO_DUR * 30))):
        ff.stdin.write(RE.intro_frame(f / 30).tobytes())
    for f in range(int(bd.total * 30)):
        ff.stdin.write(OF.credit(bd.frame(f / 30)).tobytes())
    ff.stdin.close()
    ff.wait()
    RE.intro_audio(HERE / "silent_intro.wav")
    lst = HERE / f"{out}.txt"
    with open(lst, "w") as fh:
        fh.write(f"file '{HERE / 'silent_intro.wav'}'\n")
        for s in sc.values():
            fh.write(f"file '{s.audio}'\n")
    wav = HERE / f"{out}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "pcm_s16le", str(wav)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(wav), "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", str(HERE / out)], check=True)
    print("done ->", HERE / out)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        bd, _ = build()
        for t in sorted(float(x) for x in sys.argv[2:]):
            OF.credit(bd.frame(t)).save(HERE / f"bp_{t:06.1f}.png")
        print("ok", round(bd.total, 1))
    else:
        render()
