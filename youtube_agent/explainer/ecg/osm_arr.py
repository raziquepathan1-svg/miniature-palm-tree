"""Cardiovascular series: Arrhythmia (owner-approved script, narration only)."""
import json
import math
import os
import random
import sys
from pathlib import Path

from PIL import ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "arr")))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_preview as OP  # noqa: E402
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_bp as BPm  # noqa: E402
import osm_hf as HF  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OF.MAROON, OF.PURPLE, OP.BLUE_T, OP.RED_T, OP.GOLD_T, OF.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OF.PINK, OF.LILAC, OF.CREAM, OF.MINT, OF.SKY
PW, PH = 1920, 1080
sv = BPm.sv
ECG_COL = (215, 40, 55)


def beat(x):
    """one P-QRS-T complex over x in 0..1 (y up = negative)."""
    if 0.08 <= x <= 0.18:
        return -0.13 * math.sin(math.pi * (x - 0.08) / 0.10)
    if 0.26 <= x <= 0.28:
        return 0.10 * (x - 0.26) / 0.02
    if 0.28 < x <= 0.31:
        return 0.10 - 1.10 * (x - 0.28) / 0.03
    if 0.31 < x <= 0.34:
        return -1.0 + 1.28 * (x - 0.31) / 0.03
    if 0.34 < x <= 0.37:
        return 0.28 - 0.28 * (x - 0.34) / 0.03
    if 0.50 <= x <= 0.70:
        return -0.26 * math.sin(math.pi * (x - 0.50) / 0.20)
    return 0.0


def strip(x0, x1, y, amp, widths, p=True, fib=None, seed=1):
    """ECG line from x0 to x1: beats of the given pixel widths; fib='a' wavy baseline (AFib), 'v' chaos (VFib)."""
    rnd = random.Random(seed)
    pts, x = [], x0
    if fib == "v":
        while x < x1:
            pts.append((x, y + amp * 0.45 * math.sin(x / 23.0) * (0.6 + 0.4 * rnd.random()) + amp * 0.2 * math.sin(x / 9.0)))
            x += 4
        return pts
    for w in widths:
        for i in range(0, 61):
            u = i / 60
            yy = beat(u) if (p or not (0.08 <= u <= 0.18)) else 0.0
            if fib == "a":
                yy += 0.06 * math.sin((x + u * w) / 7.0) * (0.5 + rnd.random())
            pts.append((x + u * w, y + amp * yy))
        x += w
        if x >= x1:
            break
    return [q for q in pts if q[0] <= x1]


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

    def line(pts, t, dur, col=ECG_COL, w=6):
        return add(B.Stroke(pts, col, w, t=t, dur=dur, arrow=False))

    # ---------------- HOOK (A)
    s = sc["hook"]
    hs = pop(OP.HEART, 480, 560, h=820, t=0.3)
    for k, dt_ in enumerate((0.0, 0.8, 1.2, 2.4, 2.8, 3.1, 3.4, 4.6, 5.4)):
        glows.append((0.6 + dt_, hs.map(OP.P["LV"]), 0.35, 120))
    hk = [hs, line(strip(950, 1840, 330, 160, [150, 150, 70, 230, 150, 60, 60, 60, 150]), 0.8, 3.5),
          text("skipped beat?", 1120, 160, 50, PURPLE, s.t("skip"), "c"), text("racing?", 1640, 160, 50, RED_T, s.t("race"), "c"),
          text("arrhythmia", 1390, 560, 90, RED_T, s.t("arrhythmia"), "c"), text("= change in heart rhythm", 1390, 650, 44, MAROON, s.t("rhythm") + 0.2, "c"),
          panel(980, 760, 1360, 900, MINT, s.t("harmless") - 0.3), text("most: harmless", 1170, 845, 46, GREEN_T, s.t("harmless"), "c"),
          panel(1420, 760, 1800, 900, PINK, s.t("deadly") - 0.3), text("a few: deadly", 1610, 845, 46, RED_T, s.t("deadly"), "c")]

    # ---------------- NORMAL (B)
    s = sc["normal"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, hk + [hs])
    X = PW
    h2 = pop(OP.HEART, X + 470, 560, h=820, t=s.start + 0.3)
    sa = h2.map(OP.P["SA"]) if "SA" in OP.P else h2.map((150, 150))
    tsa = s.t("s")
    glows.append((tsa, sa, 3.0, 60))
    nm = [h2, text("SA node", X + 960, 170, 54, GOLD_T, tsa), lead([(X + 950, 175), (sa[0] + 25, sa[1])], tsa + 0.4, GOLD_T),
          text("natural pacemaker", X + 960, 240, 40, MAROON, s.t("pacemaker"))]
    tst = s.t("steady")
    nm += [line(strip(X + 950, X + 1840, 480, 140, [180] * 5), s.t("spreads"), 3.0, GREEN_T),
           text("steady rhythm", X + 1390, 620, 50, GREEN_T, tst, "c"),
           panel(X + 980, 760, X + 1800, 920, MINT, s.t("sixty") - 0.3), text("60 - 100 beats / min", X + 1390, 835, 56, GREEN_T, s.t("sixty"), "c"),
           text("at rest (adult)", X + 1390, 895, 36, MAROON, s.t("rest") + 0.3, "c")]
    for k in range(6):
        glows.append((s.t("spreads") + k * 0.8, h2.map(OP.P["LV"]), 0.35, 110))

    # ---------------- WHAT (C)
    s = sc["what"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, nm + [h2])
    X = 2 * PW
    wt = title("arrhythmia = wrong beat", X + 960, 90, s.start + 0.3)
    tf, tsl, ti = s.t("fast"), s.t("slow"), s.t("irregular")
    rows = [(tf, "too fast", RED_T, [90] * 10), (tsl, "too slow", BLUE_T, [300, 300, 300]), (ti, "irregular", PURPLE, [140, 70, 230, 110, 60, 200, 120])]
    for i, (tt, lab, col, ws) in enumerate(rows):
        y = 260 + i * 170
        wt += [text(lab, X + 120, y, 50, col, tt - 0.2), line(strip(X + 520, X + 1500, y + 10, 110, ws, seed=i + 3), tt, 1.5, col, 5)]
    tt_, tb_ = s.t("tachycardia"), s.t("bradycardia")
    wt += [panel(X + 120, 760, X + 900, 940, PINK, tt_ - 0.3), text("tachycardia", X + 510, 830, 54, RED_T, tt_, "c"),
           text("over 100 / min at rest", X + 510, 900, 38, MAROON, tt_ + 0.5, "c"),
           panel(X + 1020, 760, X + 1800, 940, SKY, tb_ - 0.3), text("bradycardia", X + 1410, 830, 54, BLUE_T, tb_, "c"),
           text("under 60 (athletes: can be normal)", X + 1410, 900, 34, MAROON, s.t("athletes"), "c")]

    # ---------------- SKIPPED (D)
    s = sc["skipped"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, wt)
    sk = [text("that 'skipped beat' feeling", 960, PH + 110, 62, PURPLE, s.start + 0.3, "c"),
          text("= an extra early beat", 960, PH + 190, 50, MAROON, s.t("extra"), "c")]
    te = s.t("soon")
    widths = [220, 220, 120, 330, 220, 220]
    sk.append(line(strip(160, 1760, PH + 520, 220, widths), s.t("extra"), 3.0))
    sk += [text("early", 160 + 440 + 40, PH + 300, 44, RED_T, te), lead([(160 + 440 + 60, PH + 315), (160 + 440 + 40, PH + 420)], te + 0.3, RED_T, 5, 0.3, arrow=True),
           text("pause", 160 + 560 + 120, PH + 640, 44, BLUE_T, s.t("pauses")),
           text("stronger beat", 160 + 890 + 20, PH + 300, 44, GOLD_T, s.t("stronger"))]
    sk += [panel(500, PH + 800, 1420, PH + 950, MINT, s.t("common") - 1.0), text("very common, usually harmless", 960, PH + 890, 50, GREEN_T, s.t("common") - 0.8, "c")]

    # ---------------- AFIB (E)
    s = sc["afib"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, sk)
    X = PW
    h3 = pop(OP.HEART, X + 420, PH + 560, h=760, t=s.start + 0.3)
    ra, la = h3.map(OP.P["RA"]), h3.map(OP.P["LA"])
    tq = s.t("quiver")
    for k in range(12):
        glows += [(tq + k * 0.25, ra, 0.2, 70), (tq + k * 0.25 + 0.12, la, 0.2, 70)]
    af = [h3, text("atrial fibrillation", X + 1300, PH + 130, 64, RED_T, s.t("atrial"), "c"),
          text("(AFib) most common lasting type", X + 1300, PH + 205, 38, MAROON, s.t("lasting"), "c"),
          text("top chambers quiver", X + 1300, PH + 300, 46, PURPLE, tq, "c"),
          line(strip(X + 860, X + 1800, PH + 450, 120, [130, 70, 180, 90, 150, 60, 200], fib="a", seed=7), s.t("pulse") - 0.4, 2.5),
          text("fast + irregular pulse", X + 1330, PH + 560, 44, RED_T, s.t("irregular"), "c")]
    tcl = s.t("clots")
    af += [pop(sv("thrombus"), X + 1040, PH + 790, w=300, t=tcl - 0.2), text("clots", X + 1040, PH + 950, 44, MAROON, tcl, "c"),
           lead([(X + 1200, PH + 790), (X + 1430, PH + 790)], s.t("travel"), RED_T, 6, 0.4, arrow=True),
           pop(sv("Cerveau_beau"), X + 1620, PH + 780, h=230, t=s.t("brain") - 0.2), text("stroke", X + 1620, PH + 950, 50, RED_T, s.t("stroke"), "c")]

    # ---------------- VFIB (F)
    s = sc["vfib"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, af + [h3])
    X = 2 * PW
    vf = [text("ventricular fibrillation", X + 960, PH + 110, 66, RED_T, s.t("ventricular"), "c"),
          text("the most dangerous", X + 960, PH + 190, 44, MAROON, s.t("dangerous") - 0.5, "c"),
          line(strip(X + 140, X + 1780, PH + 380, 200, [], fib="v", seed=3), s.t("quiver") - 0.3, 2.0),
          text("main chambers quiver -> no blood pumped", X + 960, PH + 560, 46, PURPLE, s.t("pumped") - 0.6, "c"),
          panel(X + 160, PH + 640, X + 1760, PH + 780, PINK, s.t("collapses") - 0.3),
          text("collapse in seconds = cardiac arrest", X + 960, PH + 725, 52, RED_T, s.t("cardiac") - 0.6, "c"),
          panel(X + 400, PH + 820, X + 1520, PH + 960, MINT, s.t("c") - 0.3),
          text("CPR + defibrillator (AED) now", X + 960, PH + 905, 52, GREEN_T, s.t("c"), "c")]

    # ---------------- CAUSES (A)
    s = sc["causes"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, vf)
    ca = title("what causes arrhythmias?", 960, 90, s.start + 0.3)
    items = [("scars", "heart attack scar", sv("Infarctus1"), 0, 0), ("high", "high blood pressure", sv("cuff_gauge"), 1, 0),
             ("failure", "heart failure", sv("coeur_10"), 2, 0), ("thyroid", "thyroid problems", None, 3, 0),
             ("potassium", "low potassium", None, 0, 1), ("medicines", "some medicines", HF.pills_pic(), 1, 1),
             ("caffeine", "too much caffeine", None, 2, 1), ("alcohol", "alcohol / stimulants", None, 3, 1)]
    for w, lab, pic, cx_, cy_ in items:
        tt = s.t(w) - (1.0 if w == "alcohol" else 0)
        x0, y0 = 70 + cx_ * 455, 180 + cy_ * 420
        ca += [panel(x0, y0, x0 + 420, y0 + 380, PINK if cy_ == 0 else CREAM, tt - 0.3), text(lab, x0 + 210, y0 + 340, 38, MAROON, tt, "c")]
        if pic is not None:
            ca.append(pop(pic, x0 + 210, y0 + 150, h=220 if w != "medicines" else 130, t=tt - 0.1))
        else:
            ca.append(text("+", x0 + 210, y0 + 160, 150, GOLD_T if cy_ else RED_T, tt, "c"))

    # ---------------- SIGNS (B)
    s = sc["signs"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, ca)
    X = PW
    sg = title("warning signs", X + 960, 90, s.start + 0.3)
    signs = [("fluttering", "fluttering / pounding heartbeat", RED_T), ("dizziness", "dizziness", PURPLE), ("breathlessness", "breathlessness", BLUE_T),
             ("tiredness", "tiredness", GOLD_T)]
    for i, (w, lab, col) in enumerate(signs):
        sg.append(text("- " + lab, X + 160, 220 + i * 95, 54, col, s.t(w)))
    tfa = s.t("faints")
    sg += [panel(X + 120, 620, X + 1800, 960, PINK, tfa - 0.3), text("fainting, chest pain, or collapse", X + 960, 710, 52, RED_T, tfa, "c"),
           text("(not breathing normally)", X + 960, 785, 40, MAROON, s.t("breathing"), "c"),
           text("-> call emergency + start CPR", X + 960, 890, 54, RED_T, s.t("call"), "c"),
           pop(sv("Smartphone-1"), X + 1620, 330, h=340, t=s.t("call") - 0.3)]

    # ---------------- TREAT (C)
    s = sc["treat"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, sg)
    X = 2 * PW
    tr = title("find it, then treat it", X + 960, 90, s.start + 0.3)
    te_ = s.t("e")
    tr += [panel(X + 100, 170, X + 900, 420, SKY, te_ - 0.3), text("ECG", X + 500, 230, 60, BLUE_T, te_, "c"),
           line(strip(X + 160, X + 840, 330, 90, [170] * 4), te_ + 0.3, 1.2, ECG_COL, 4),
           panel(X + 1020, 170, X + 1820, 420, LILAC, s.t("portable") - 0.3), text("portable monitor", X + 1420, 250, 52, PURPLE, s.t("portable"), "c"),
           text("worn for a day or more", X + 1420, 330, 40, MAROON, s.t("day"), "c")]
    tips = [("cause", "treat the cause", MINT, GREEN_T), ("medicines", "medicines", CREAM, GOLD_T), ("thinners", "blood thinners (AFib)", PINK, RED_T),
            ("pacemaker", "pacemaker (slow rhythm)", SKY, BLUE_T), ("procedures", "procedures fix the wiring", LILAC, PURPLE)]
    for i, (w, lab, col, tc_) in enumerate(tips):
        tt = s.t(w) - (1.0 if w == "procedures" else 0)
        x0, y0 = X + 100 + (i % 2) * 880 + (440 if i == 4 else 0), 480 + (i // 2) * 170
        tr += [panel(x0, y0, x0 + 840, y0 + 140, col, tt - 0.3), text(lab, x0 + 420, y0 + 88, 48, tc_, tt, "c")]

    # ---------------- SUMMARY (D)
    s = sc["summary"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, tr)
    sm = title("remember 3 things", 960, PH + 110, s.start + 0.5)
    cards = [("sixty", "60-100 / min", "normal at rest", MINT, GREEN_T, 400), ("skipped", "skipped beat", "usually harmless", LILAC, PURPLE, 960),
             ("fainting", "fainting / collapse", "= emergency", PINK, RED_T, 1520)]
    for w, a, b, col, tc_, x in cards:
        tt = s.t(w) - 0.3
        sm += [panel(x - 260, PH + 260, x + 260, PH + 620, col, tt - 0.2), text(a, x, PH + 400, 48, tc_, tt, "c"), text(b, x, PH + 500, 44, MAROON, tt + 0.6, "c")]
    tn = s.t("next")
    sm += [panel(360, PH + 760, 1560, PH + 920, SKY, tn), text("next: the heart valves", 960, PH + 860, 52, BLUE_T, tn + 0.3, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render(out="arrhythmia.mp4"):
    import subprocess
    import render_ecg as RE
    bd, sc = build()
    vid = HERE / "arr_video_only.mp4"
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
            OF.credit(bd.frame(t)).save(HERE / f"arr_{t:06.1f}.png")
        print("ok", round(bd.total, 1), ends)
    else:
        render()
