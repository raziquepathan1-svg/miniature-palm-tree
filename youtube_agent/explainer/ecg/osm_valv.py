"""Cardiovascular series: Heart Valve Disease (owner-approved script, narration only)."""
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "valv")))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_preview as OP  # noqa: E402
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_bv as BV  # noqa: E402
import osm_bp as BPm  # noqa: E402
import osm_hf as HF  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OF.MAROON, OF.PURPLE, OP.BLUE_T, OP.RED_T, OP.GOLD_T, OF.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OF.PINK, OF.LILAC, OF.CREAM, OF.MINT, OF.SKY
PW, PH = 1920, 1080
sv = BPm.sv
OUTL = (70, 60, 70)
VPOS = {"tricuspid": (0.28, 0.27), "mitral": (0.68, 0.27), "aortic": (0.45, 0.58), "pulmonary": (0.47, 0.82)}


def valve_pic(kind):
    """front view of a valve as a door in a tube: normal open, stenosis (tiny opening), regurgitation (gap + back-flow)."""
    S = 3
    W_, H_ = 420, 300
    im = Image.new("RGBA", (W_ * S, H_ * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((10 * S, 60 * S, 410 * S, 240 * S), fill=(250, 215, 210))
    d.line([(10 * S, 60 * S), (410 * S, 60 * S)], fill=OUTL, width=6 * S)
    d.line([(10 * S, 240 * S), (410 * S, 240 * S)], fill=OUTL, width=6 * S)
    lc = (235, 235, 240)
    if kind == "open":
        d.polygon([(200 * S, 62 * S), (290 * S, 85 * S), (205 * S, 100 * S)], fill=lc, outline=OUTL)
        d.polygon([(200 * S, 238 * S), (290 * S, 215 * S), (205 * S, 200 * S)], fill=lc, outline=OUTL)
    elif kind == "stenosis":
        d.polygon([(200 * S, 62 * S), (250 * S, 140 * S), (215 * S, 138 * S)], fill=(225, 215, 190), outline=OUTL)
        d.polygon([(200 * S, 238 * S), (250 * S, 160 * S), (215 * S, 162 * S)], fill=(225, 215, 190), outline=OUTL)
        for x, y in ((220, 110), (225, 190), (235, 130)):
            d.ellipse(((x - 6) * S, (y - 6) * S, (x + 6) * S, (y + 6) * S), fill=(250, 245, 230), outline=OUTL)
    else:  # leaky
        d.polygon([(200 * S, 62 * S), (215 * S, 135 * S), (202 * S, 135 * S)], fill=lc, outline=OUTL)
        d.polygon([(200 * S, 238 * S), (215 * S, 168 * S), (202 * S, 168 * S)], fill=lc, outline=OUTL)
    return im.resize((W_, H_), Image.LANCZOS)


def hose_pinched():
    im = BPm.hose_pic()
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((560, 170, 640, 290), radius=20, fill=(60, 60, 70))
    return im


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

    def arrow(pts, t, col=RED_T, w=7):
        return lead(pts, t, col, w, 0.4, arrow=True)

    # ---------------- HOOK (A)
    s = sc["hook"]
    hs = pop(OP.HEART, 480, 560, h=820, t=0.3)
    hk = [hs, text("4 tiny doors", 1370, 170, 80, PURPLE, s.t("doors"), "c"),
          text("open + close ~100,000 times a day", 1370, 260, 44, MAROON, s.t("hundred") + 0.3, "c"),
          panel(980, 380, 1360, 520, CREAM, s.t("stiff") - 0.3), text("stiff?", 1170, 465, 56, GOLD_T, s.t("stiff"), "c"),
          panel(1400, 380, 1780, 520, SKY, s.t("leak") - 0.3), text("leaky?", 1590, 465, 56, BLUE_T, s.t("leak"), "c"),
          text("-> the whole heart works harder", 1380, 650, 48, RED_T, s.t("harder") - 0.4, "c")]
    for k in range(int(s.dur / 0.9)):
        glows.append((0.6 + k * 0.9, hs.map(OP.P["LV"]), 0.4, 110))

    # ---------------- THE 4 VALVES (B)
    s = sc["valves"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, hk + [hs])
    X = PW
    vb = pop(sv("valves_01"), X + 560, 560, h=780, t=s.start + 0.3)
    va = [vb, text("the 4 heart valves", X + 560, 110, 60, MAROON, s.start + 0.5, "c"), text("(seen from above)", X + 560, 175, 34, MAROON, s.start + 1.0, "c")]
    cols = {"tricuspid": GREEN_T, "pulmonary": BLUE_T, "mitral": PURPLE, "aortic": RED_T}
    for i, name in enumerate(("mitral", "tricuspid", "aortic", "pulmonary")):
        tt = s.t(name)
        p = F(vb, *VPOS[name])
        y = 280 + i * 120
        va += [text(name, X + 1250, y, 54, cols[name], tt), lead([(X + 1240, y), (p[0] + 40, p[1])], tt + 0.3, cols[name], 5)]
        glows.append((tt, p, 1.5, 60))
    va += [panel(X + 1120, 770, X + 1820, 940, MINT, s.t("one") - 0.3), text("one-way doors", X + 1470, 835, 54, GREEN_T, s.t("one"), "c"),
           text("open, then snap shut", X + 1470, 905, 40, MAROON, s.t("snaps"), "c")]

    # ---------------- TWO PROBLEMS (C)
    s = sc["two"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, va)
    X = 2 * PW
    tw = title("2 ways a valve goes wrong", X + 960, 90, s.start + 0.3)
    tw += [pop(valve_pic("open"), X + 960, 270, w=360, t=s.start + 0.6), text("normal", X + 960, 400, 40, GREEN_T, s.start + 0.9, "c")]
    ts_, tr_ = s.t("narrow"), s.t("leaky")
    tw += [panel(X + 100, 470, X + 900, 990, CREAM, ts_ - 0.3), pop(valve_pic("stenosis"), X + 500, 640, w=420, t=ts_),
           text("narrow + stiff", X + 500, 820, 50, GOLD_T, ts_ + 0.3, "c"), text("doesn't open fully", X + 500, 880, 40, MAROON, s.t("open"), "c"),
           text("= stenosis", X + 500, 950, 54, RED_T, s.t("stenosis"), "c"),
           panel(X + 1020, 470, X + 1820, 990, SKY, tr_ - 0.3), pop(valve_pic("leaky"), X + 1420, 640, w=420, t=tr_),
           text("leaky", X + 1420, 820, 50, BLUE_T, tr_ + 0.3, "c"), text("doesn't close tightly", X + 1420, 880, 40, MAROON, s.t("close"), "c"),
           text("= regurgitation", X + 1420, 950, 54, PURPLE, s.t("close") + 0.4, "c")]

    # ---------------- STENOSIS (D)
    s = sc["stenosis"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, tw)
    st = [text("stenosis", 960, PH + 100, 72, GOLD_T, s.start + 0.3, "c"),
          pop(sv("valves_02"), 380, PH + 420, h=440, t=s.start + 0.5), text("narrow valve", 380, PH + 680, 42, MAROON, s.start + 1.0, "c"),
          pop(hose_pinched(), 1260, PH + 380, w=760, t=s.t("pinched") - 0.4), text("like a pinched hose", 1260, PH + 560, 46, PURPLE, s.t("pinched"), "c")]
    tth = s.t("thickens")
    st += [pop(BV.ring(140, 60, (215, 90, 105, 255), (255, 250, 250, 255), MAROON), 900, PH + 800, h=230, t=tth - 0.2),
           text("muscle thickens + tires", 1090, PH + 790, 46, RED_T, tth),
           panel(380, PH + 900, 1540, PH + 1020, CREAM, s.t("aortic") - 0.3),
           text("aortic stenosis: common in older adults", 960, PH + 975, 46, GOLD_T, s.t("aortic"), "c")]

    # ---------------- REGURGITATION (E)
    s = sc["leak"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, st)
    X = PW
    lk = [text("regurgitation", X + 960, PH + 100, 72, PURPLE, s.start + 0.3, "c"),
          pop(valve_pic("leaky"), X + 520, PH + 380, w=640, t=s.start + 0.5)]
    tb = s.t("backward")
    lk += [arrow([(X + 760, PH + 380), (X + 600, PH + 380)], tb - 0.2, RED_T), arrow([(X + 760, PH + 330), (X + 640, PH + 345)], tb, RED_T, 5),
           text("blood leaks backward", X + 1360, PH + 330, 50, RED_T, tb),
           text("every beat", X + 1360, PH + 400, 40, MAROON, s.t("every"))]
    tsa = s.t("same")
    lk += [text("pumps the same blood again", X + 1360, PH + 520, 46, PURPLE, tsa, "c"),
           pop(BV.ring(110, 85, (235, 120, 130, 255), (255, 250, 250, 255), RED_T), X + 520, PH + 800, h=200, t=s.t("stretches") - 0.6),
           arrow([(X + 660, PH + 800), (X + 760, PH + 800)], s.t("stretches") - 0.3, MAROON, 5),
           pop(BV.ring(160, 135, (235, 120, 130, 255), (255, 250, 250, 255), RED_T), X + 920, PH + 800, h=290, t=s.t("stretches")),
           text("chamber stretches", X + 1420, PH + 770, 46, BLUE_T, s.t("bigger") - 0.5, "c"),
           text("-> can weaken", X + 1420, PH + 840, 46, RED_T, s.t("weaken") - 0.6, "c")]

    # ---------------- CAUSES (F)
    s = sc["causes"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, lk)
    X = 2 * PW
    ca = title("what damages valves?", X + 960, 90, s.start + 0.3)
    items = [("age", "wear + calcium with age", None, 0, 0), ("rheumatic", "rheumatic fever", None, 1, 0),
             ("born", "born with it", None, 2, 0), ("endocarditis", "valve infection", None, 0, 1),
             ("attack", "heart attack damage", sv("Infarctus1"), 1, 1)]
    for w, lab, pic, cx_, cy_ in items:
        tt = s.t(w) - (0.8 if w == "attack" else 0)
        x0, y0 = X + 120 + cx_ * 580 + (290 if cy_ else 0), 190 + cy_ * 420
        ca += [panel(x0, y0, x0 + 520, y0 + 370, PINK if cy_ == 0 else CREAM, tt - 0.3), text(lab, x0 + 260, y0 + 330, 40, MAROON, tt, "c")]
        if pic is not None:
            ca.append(pop(pic, x0 + 260, y0 + 150, h=220, t=tt - 0.1))
        else:
            sub_ = {"age": "most common", "rheumatic": "after untreated strep throat", "born": "e.g. 2-flap aortic valve",
                    "endocarditis": "(endocarditis)"}[w]
            ca.append(text(sub_, x0 + 260, y0 + 170, 36, PURPLE, tt + 0.4, "c"))

    # ---------------- MURMUR + ECHO (A)
    s = sc["murmur"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, ca)
    mu = [pop(sv("stethoscope"), 380, 420, h=480, t=s.start + 0.3),
          text("heart murmur", 1250, 200, 70, PURPLE, s.t("murmur"), "c"), text("= extra whooshing sound", 1250, 290, 46, MAROON, s.t("whooshing"), "c"),
          text("heard with a stethoscope", 1250, 360, 40, MAROON, s.t("stethoscope"), "c")]
    tec = s.t("echocardiogram")
    mu += [pop(HF.echo_pic(), 600, 820, w=360, t=s.t("ultrasound") - 0.3),
           panel(900, 700, 1800, 940, SKY, s.t("key") - 0.3), text("key test:", 1350, 760, 44, MAROON, s.t("key"), "c"),
           text("echocardiogram", 1350, 840, 60, BLUE_T, tec, "c"), text("shows the valve moving", 1350, 905, 38, MAROON, s.t("ultrasound"), "c")]

    # ---------------- SIGNS (B)
    s = sc["signs"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, mu)
    X = PW
    sg = [title("signs", X + 960, 90, s.start + 0.3),
          panel(X + 120, 160, X + 1800, 260, MINT, s.t("many") - 0.2), text("often no symptoms for years", X + 960, 225, 50, GREEN_T, s.t("many"), "c")]
    signs = [("breathlessness", "breathlessness", BLUE_T), ("tiredness", "tiredness", PURPLE), ("chest", "chest pain", RED_T),
             ("dizziness", "dizziness / fainting", GOLD_T), ("swollen", "swollen ankles", BLUE_T)]
    for i, (w, lab, col) in enumerate(signs):
        sg.append(text("- " + lab, X + 160 + (i // 3) * 820, 360 + (i % 3) * 95, 52, col, s.t(w)))
    tsu = s.t("sudden")
    sg += [panel(X + 120, 720, X + 1800, 900, PINK, tsu - 0.3), text("sudden chest pain or fainting", X + 960, 790, 52, RED_T, tsu, "c"),
           text("-> urgent medical help", X + 960, 860, 50, RED_T, s.t("urgent") - 0.5, "c")]

    # ---------------- TREAT (C)
    s = sc["treat"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, sg)
    X = 2 * PW
    tr = title("treatment", X + 960, 90, s.start + 0.3)
    tr += [panel(X + 100, 170, X + 900, 320, MINT, s.t("mild") - 0.3), text("mild: regular check-ups", X + 500, 260, 46, GREEN_T, s.t("mild"), "c"),
           panel(X + 1020, 170, X + 1820, 320, CREAM, s.t("medicines") - 0.3), text("medicines ease symptoms", X + 1420, 260, 46, GOLD_T, s.t("medicines"), "c")]
    trp = s.t("repaired")
    tr += [text("badly damaged -> repair or replace", X + 960, 410, 56, PURPLE, trp - 0.4, "c"),
           pop(sv("valves_10"), X + 400, 600, h=260, t=trp), text("tissue valve", X + 400, 760, 38, MAROON, trp + 0.3, "c"),
           pop(sv("valves_11"), X + 800, 600, h=260, t=trp + 0.4), text("mechanical valve", X + 800, 760, 38, MAROON, trp + 0.7, "c"),
           text("open heart surgery", X + 1100, 560, 46, RED_T, s.t("open")),
           text("or a thin tube in a blood vessel", X + 1100, 640, 46, BLUE_T, s.t("thin") - 0.3)]
    tsr = s.t("strep")
    tr += [panel(X + 200, 840, X + 1720, 980, MINT, tsr - 0.6), text("treat strep throat early -> protects valves", X + 960, 925, 48, GREEN_T, tsr - 0.4, "c")]

    # ---------------- SUMMARY (D)
    s = sc["summary"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, tr)
    sm = title("remember 3 things", 960, PH + 110, s.start + 0.5)
    cards = [("valves", "valves =", "one-way doors", MINT, GREEN_T, 400), ("stenosis", "stenosis = stiff", "regurgitation = leaky", CREAM, GOLD_T, 960),
             ("echocardiogram", "echocardiogram", "finds it", SKY, BLUE_T, 1520)]
    for w, a, b, col, tc_, x in cards:
        tt = s.t(w) - 0.3
        sm += [panel(x - 265, PH + 260, x + 265, PH + 620, col, tt - 0.2), text(a, x, PH + 400, 46, tc_, tt, "c"), text(b, x, PH + 500, 38, MAROON, tt + 0.6, "c")]
    tn = s.t("next")
    sm += [panel(360, PH + 760, 1560, PH + 920, LILAC, tn - 0.6), text("next: the lungs + breathing", 960, PH + 860, 52, PURPLE, tn - 0.3, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render(out="heart_valves.mp4"):
    import subprocess
    import render_ecg as RE
    bd, sc = build()
    vid = HERE / "valv_video_only.mp4"
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
            OF.credit(bd.frame(t)).save(HERE / f"valv_{t:06.1f}.png")
        print("ok", round(bd.total, 1), ends)
    else:
        render()
