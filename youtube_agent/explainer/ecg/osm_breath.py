"""Respiratory series: How Breathing Works (owner-approved script, narration only)."""
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "breath")))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_preview as OP  # noqa: E402
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_bp as BPm  # noqa: E402
import osm_lungs as LU  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OF.MAROON, OF.PURPLE, OP.BLUE_T, OP.RED_T, OP.GOLD_T, OF.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OF.PINK, OF.LILAC, OF.CREAM, OF.MINT, OF.SKY
PW, PH = 1920, 1080
sv = LU.sv
MUSCLE = (195, 75, 85)
OUTL = (70, 60, 70)


def candle_pic():
    S = 3
    im = Image.new("RGBA", (160 * S, 320 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((45 * S, 120 * S, 115 * S, 310 * S), radius=10 * S, fill=(250, 240, 220), outline=OUTL, width=5 * S)
    d.line([(80 * S, 120 * S), (80 * S, 95 * S)], fill=OUTL, width=4 * S)
    d.ellipse((60 * S, 20 * S, 100 * S, 95 * S), fill=(255, 190, 60), outline=(220, 120, 30), width=4 * S)
    d.ellipse((72 * S, 55 * S, 88 * S, 90 * S), fill=(255, 240, 160))
    return im.resize((160, 320), Image.LANCZOS)


def bottle_pic():
    S = 3
    im = Image.new("RGBA", (180 * S, 340 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((65 * S, 10 * S, 115 * S, 60 * S), radius=8 * S, fill=(120, 170, 230), outline=OUTL, width=4 * S)
    d.rounded_rectangle((25 * S, 60 * S, 155 * S, 330 * S), radius=30 * S, fill=(220, 236, 250), outline=OUTL, width=5 * S)
    d.rounded_rectangle((30 * S, 190 * S, 150 * S, 325 * S), radius=26 * S, fill=(150, 200, 245))
    return im.resize((180, 340), Image.LANCZOS)


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
    pops, glows, anims = [], [], []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    add, cam = bd.add, bd.camera
    A, Bc, C = (960, 540), (PW + 960, 540), (2 * PW + 960, 540)
    D, E, Fp = (960, PH + 540), (PW + 960, PH + 540), (2 * PW + 960, PH + 540)
    cam(0, *A, 1.0, 0.1)

    # ---------------- HOOK (A)
    s = sc["hook"]
    lg = pop(sv("poumons_01"), 520, 520, h=700, t=0.3)
    hk = [lg, text("lungs have no muscles", 1360, 170, 60, MAROON, s.t("muscles"), "c"), text("of their own", 1360, 245, 46, MAROON, s.t("own"), "c"),
          text("~20,000 breaths a day", 1360, 400, 60, BLUE_T, s.t("thousand"), "c"),
          text("without thinking!", 1360, 480, 46, PURPLE, s.t("thinking"), "c"),
          panel(980, 620, 1360, 780, PINK, s.t("muscle", 2) - 0.3), text("a muscle", 1170, 715, 52, RED_T, s.t("muscle", 2), "c"),
          panel(1400, 620, 1780, 780, SKY, s.t("simple") - 0.3), text("+ pressure", 1590, 715, 52, BLUE_T, s.t("simple"), "c")]

    # ---------------- DIAPHRAGM (B) - animated dome under the lungs
    s = sc["diaphragm"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, hk + [lg])
    X = PW
    lg2 = pop(sv("poumons_01"), X + 560, 430, h=560, t=s.start + 0.3)
    dm = [lg2, text("diaphragm", X + 1360, 200, 84, RED_T, s.t("diaphragm"), "c"),
          text("dome-shaped sheet of muscle", X + 1360, 290, 44, MAROON, s.t("dome"), "c"),
          text("under the lungs", X + 1360, 360, 44, MAROON, s.t("under"), "c"),
          text("chest", X + 1080, 520, 44, BLUE_T, s.t("chest")), text("belly", X + 1080, 800, 44, GOLD_T, s.t("belly")),
          panel(X + 1000, 880, X + 1760, 1010, MINT, s.t("main") - 1.0), text("the main breathing muscle", X + 1380, 960, 48, GREEN_T, s.t("main") - 0.8, "c")]
    # dome: (page centre x, y of the top of the dome) - drawn every frame by fx, moves with the breath
    anims.append(("dome", X + 560, 730, s.t("dome") - 0.4, sc["diaphragm"].end))

    # ---------------- INHALE (C)
    s = sc["inhale"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, dm + [lg2])
    X = 2 * PW
    lg3 = pop(sv("poumons_01"), X + 560, 430, h=560, t=s.start + 0.3)
    tc = s.t("contracts")
    inh = [lg3, text("breathing in", X + 1360, 130, 76, BLUE_T, s.start + 0.4, "c"),
           text("diaphragm contracts", X + 1360, 260, 48, RED_T, tc, "c"), text("+ flattens (moves down)", X + 1360, 330, 44, MAROON, s.t("flattens"), "c"),
           text("external intercostals", X + 1360, 470, 48, PURPLE, s.t("external"), "c"), text("lift ribs up + out", X + 1360, 540, 44, MAROON, s.t("ribs"), "c"),
           panel(X + 1000, 680, X + 1720, 820, SKY, s.t("chest") - 0.6), text("chest gets bigger", X + 1360, 765, 54, BLUE_T, s.t("chest") - 0.4, "c")]
    anims.append(("dome_down", X + 560, 730, tc, s.end))
    anims.append(("ribs_up", X + 560, 430, s.t("external"), s.end))
    inh += [lead([(X + 560, 820), (X + 560, 930)], tc + 0.3, RED_T, 8, 0.4, arrow=True)]

    # ---------------- PRESSURE (D)
    s = sc["pressure"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, inh + [lg3])
    pr = title("the pressure rule", 960, PH + 100, s.start + 0.3) + [
          panel(160, PH + 220, 1760, PH + 360, CREAM, s.t("bigger") - 0.3),
          text("bigger space -> lower pressure", 960, PH + 310, 60, GOLD_T, s.t("bigger"), "c")]
    tf = s.t("falls")
    pr += [pop(sv("poumons_01"), 600, PH + 700, h=480, t=s.start + 0.8),
           text("lungs: low pressure", 1300, PH + 520, 50, BLUE_T, tf), text("outside air: higher", 1300, PH + 610, 50, RED_T, s.t("outside")),
           panel(1150, PH + 760, 1800, PH + 900, SKY, s.t("rushes") - 0.3), text("-> air rushes in", 1475, PH + 845, 56, BLUE_T, s.t("rushes"), "c")]
    tr = s.t("rushes")
    for k in range(3):
        pr.append(lead([(600 - 60 + k * 60, PH + 380), (600 - 20 + k * 20, PH + 500)], tr + 0.15 * k, BLUE_T, 7, 0.4, arrow=True))
    glows.append((s.t("alveoli"), (600, PH + 760), 2.5, 160))

    # ---------------- EXHALE (E)
    s = sc["exhale"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, pr)
    X = PW
    lg4 = pop(sv("poumons_01"), X + 560, 430, h=560, t=s.start + 0.3)
    tp = s.t("passive")
    ex = [lg4, text("breathing out (at rest)", X + 1360, 130, 64, PURPLE, s.start + 0.4, "c"),
          panel(X + 1100, 210, X + 1620, 330, LILAC, tp - 0.3), text("= passive", X + 1360, 290, 60, PURPLE, tp, "c"),
          text("diaphragm relaxes, domes up", X + 1360, 420, 44, RED_T, s.t("relaxes"), "c"),
          text("ribs fall", X + 1360, 490, 44, MAROON, s.t("fall"), "c"),
          text("stretchy lungs spring back", X + 1360, 560, 44, GREEN_T, s.t("spring"), "c"),
          panel(X + 1000, 680, X + 1720, 830, PINK, s.t("smaller") - 0.3), text("smaller chest, higher pressure", X + 1360, 745, 42, RED_T, s.t("smaller"), "c"),
          text("-> air flows out", X + 1360, 805, 48, BLUE_T, s.t("flows") - 0.4, "c")]
    anims.append(("dome_up", X + 560, 730, s.t("relaxes"), s.end))
    tfl = s.t("flows")
    ex += [lead([(X + 560, 140), (X + 560, 40)], tfl - 0.6, BLUE_T, 8, 0.4, arrow=True)]

    # ---------------- FORCED (F)
    s = sc["forced"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ex + [lg4])
    X = 2 * PW
    fo = title("breathing out with force", X + 960, 100, s.start + 0.3)
    for i, (w, lab, pic) in enumerate((("exercise", "exercise", None), ("cough", "cough", None), ("candles", "blowing out candles", candle_pic()))):
        tt = s.t(w)
        x = X + 340 + i * 620
        fo += [panel(x - 260, 200, x + 260, 560, [MINT, SKY, CREAM][i], tt - 0.3), text(lab, x, 520, 44, MAROON, tt, "c")]
        fo.append(pop(pic, x, 360, h=260, t=tt) if pic is not None else text(["run!", "cough!"][i], x, 360, 90, [GREEN_T, BLUE_T][i], tt + 0.1, "c"))
    ti = s.t("internal")
    fo += [panel(X + 200, 650, X + 1720, 950, PINK, ti - 0.3), text("internal intercostals", X + 960, 730, 54, RED_T, ti, "c"),
           text("+ belly muscles squeeze", X + 960, 810, 54, RED_T, s.t("belly"), "c"), text("-> air out faster", X + 960, 890, 46, MAROON, s.t("pushing") - 0.3, "c")]

    # ---------------- NUMBERS (A)
    s = sc["numbers"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, fo)
    tw = s.t("twelve")
    nu = title("breathing by numbers", 960, 100, s.start + 0.3) + [
          panel(160, 220, 900, 760, SKY, tw - 0.3), text("12 - 20", 530, 430, 130, BLUE_T, tw, "c"),
          text("breaths / minute", 530, 560, 50, MAROON, s.t("minute"), "c"), text("(adult at rest)", 530, 640, 40, MAROON, s.t("rest") + 0.2, "c")]
    th = s.t("half")
    nu += [panel(1020, 220, 1760, 760, MINT, th - 0.3), pop(bottle_pic(), 1200, 490, h=420, t=th),
           text("~0.5 L", 1540, 440, 90, GREEN_T, th + 0.2, "c"), text("per quiet breath", 1540, 560, 44, MAROON, s.t("liter") - 0.3, "c")]

    # ---------------- CONTROL (B)
    s = sc["control"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, nu)
    X = PW
    br = pop(sv("Cerveau_beau"), X + 480, 440, h=600, t=s.start + 0.3)
    stem = br.map((0.5 * br.src.width, 0.82 * br.src.height))
    co = [br, text("who decides?", X + 1360, 130, 70, PURPLE, s.start + 0.4, "c"),
          text("brainstem", X + 1100, 300, 60, GOLD_T, s.t("brainstem")), text("control center", X + 1100, 370, 44, MAROON, s.t("brainstem") + 0.4),
          lead([(X + 1090, 305), (stem[0] + 30, stem[1])], s.t("brainstem") + 0.3, GOLD_T, 6)]
    glows.append((s.t("brainstem"), stem, s.end - s.t("brainstem"), 70))
    tco = s.t("carbon")
    co += [panel(X + 1000, 480, X + 1780, 640, CREAM, tco - 0.3), text("main signal: CO2", X + 1390, 570, 58, RED_T, tco, "c"),
           text("CO2 builds up in blood", X + 1390, 720, 46, MAROON, s.t("builds"), "c"),
           text("-> sensors tell the brain", X + 1390, 800, 46, PURPLE, s.t("sensors"), "c"),
           panel(X + 1000, 860, X + 1780, 1000, MINT, s.t("faster") - 1.0), text("-> faster + deeper breathing", X + 1390, 945, 46, GREEN_T, s.t("faster") - 0.9, "c")]

    # ---------------- OXYGEN (C)
    s = sc["oxygen"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, co + [br])
    X = 2 * PW
    al = pop(sv("poumon_10"), X + 360, 560, h=820, t=s.start + 0.3)
    th_ = s.t("hemoglobin")
    ox = [al, text("oxygen -> blood", X + 1250, 150, 64, RED_T, s.t("oxygen"), "c"),
          pop(sv("hematie_02"), X + 1000, 440, h=260, t=s.t("red") - 0.4),
          text("rides on hemoglobin", X + 1440, 400, 48, RED_T, th_ - 0.3, "c"), text("in red blood cells", X + 1440, 470, 44, MAROON, s.t("red"), "c"),
          text("-> to every part of the body", X + 1250, 620, 48, PURPLE, s.t("every"), "c"),
          panel(X + 800, 740, X + 1720, 900, SKY, s.t("carbon") - 0.3), text("CO2 travels back to be breathed out", X + 1260, 830, 44, BLUE_T, s.t("carbon"), "c")]

    # ---------------- SUMMARY (D)
    s = sc["summary"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, ox + [al])
    sm = title("remember", 960, PH + 100, s.start + 0.4)
    cards = [("active", "in = active", "diaphragm down, ribs up", SKY, BLUE_T, 400), ("passive", "out = passive", "(at rest)", LILAC, PURPLE, 960),
             ("trigger", "CO2", "main trigger", PINK, RED_T, 1520)]
    for w, a, b, col, tc_, x in cards:
        tt = s.t(w) - 0.3
        sm += [panel(x - 265, PH + 220, x + 265, PH + 560, col, tt - 0.2), text(a, x, PH + 350, 52, tc_, tt, "c"), text(b, x, PH + 450, 36, MAROON, tt + 0.6, "c")]
    sm += [panel(260, PH + 620, 1660, PH + 740, CREAM, s.t("bigger") - 0.3),
           text("bigger chest -> lower pressure -> air flows in", 960, PH + 700, 48, GOLD_T, s.t("bigger"), "c")]
    tn = s.t("next")
    sm += [panel(460, PH + 800, 1460, PH + 950, MINT, tn - 0.3), text("next: what goes wrong in asthma", 960, PH + 895, 50, GREEN_T, tn, "c")]

    def dome_pts(cx, top, flat, w=420):
        """diaphragm as a dome: flat=0 domed up (relaxed), flat=1 flatter + lower (contracted)."""
        rise = 110 * (1 - 0.7 * flat)
        base = top + 110 + 70 * flat
        return [(cx - w + 2 * w * i / 40, base - rise * math.sin(math.pi * i / 40)) for i in range(41)]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
        d = ImageDraw.Draw(crop)
        for kind, cx, top, ta, tb in anims:
            if not (ta <= t <= tb):
                continue
            u = min(1.0, (t - ta) / 1.6)
            u = u * u * (3 - 2 * u)
            if kind == "ribs_up":
                for k in range(4):   # ribs lift: arcs move up and outward
                    y = top - 150 + k * 70 - 18 * u
                    ww = 300 + 25 * u
                    pts = [ctx.px((cx - ww + 2 * ww * i / 30, y + 60 * math.sin(math.pi * i / 30))) for i in range(31)]
                    d.line(pts, fill=(150, 130, 120), width=int(5 * B.BS))
                continue
            flat = {"dome": 0.0, "dome_down": u, "dome_up": 1 - u}[kind]
            if kind == "dome":
                flat = 0.35 * (1 - math.cos(2 * math.pi * (t - ta) / 3.0)) / 2   # gentle breathing in the intro
            pts = [ctx.px(p) for p in dome_pts(cx, top, flat)]
            d.line(pts, fill=MUSCLE, width=int(28 * B.BS), joint="curve")
            d.line(pts, fill=(225, 120, 125), width=int(10 * B.BS), joint="curve")
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render(out="how_breathing_works.mp4"):
    import subprocess
    import render_ecg as RE
    bd, sc = build()
    vid = HERE / "breath_video_only.mp4"
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
            OF.credit(bd.frame(t)).save(HERE / f"breath_{t:06.1f}.png")
        print("ok", round(bd.total, 1), ends)
    else:
        render()
