"""Respiratory series: COPD (owner-approved script, narration only)."""
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "copd")))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_preview as OP  # noqa: E402
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_bp as BPm  # noqa: E402
import osm_lungs as LU  # noqa: E402
import osm_hf as HF  # noqa: E402
import osm_asthma as AS  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OF.MAROON, OF.PURPLE, OP.BLUE_T, OP.RED_T, OP.GOLD_T, OF.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OF.PINK, OF.LILAC, OF.CREAM, OF.MINT, OF.SKY
PW, PH = 1920, 1080
sv = LU.sv
OUTL = (70, 60, 70)


def sacs(healthy):
    """healthy = many small air sacs; damaged = few big merged sacs with broken walls (emphysema)."""
    S = 3
    im = Image.new("RGBA", (420 * S, 420 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if healthy:
        for r_ in range(4):
            for c_ in range(4):
                cx, cy = 60 + c_ * 88 + (r_ % 2) * 40, 70 + r_ * 92
                d.ellipse(((cx - 48) * S, (cy - 48) * S, (cx + 48) * S, (cy + 48) * S), fill=(250, 220, 215), outline=(200, 110, 110), width=5 * S)
    else:
        for cx, cy, r in ((130, 140, 115), (300, 150, 100), (210, 310, 110)):
            d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=(235, 225, 225), outline=(150, 120, 120), width=5 * S)
        for x, y in ((200, 140), (250, 230), (150, 250)):
            d.line([((x - 15) * S, (y - 15) * S), ((x + 15) * S, (y + 15) * S)], fill=(150, 120, 120), width=6 * S)
    return im.resize((420, 420), Image.LANCZOS)


def fire_pic():
    S = 3
    im = Image.new("RGBA", (300 * S, 300 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(3):
        d.line([((60 + k * 40) * S, 280 * S), ((200 - k * 20) * S, 230 * S)], fill=(120, 80, 50), width=18 * S)
    d.polygon([(150 * S, 80 * S), (220 * S, 230 * S), (80 * S, 230 * S)], fill=(255, 160, 40), outline=(210, 90, 30))
    d.polygon([(150 * S, 140 * S), (185 * S, 230 * S), (115 * S, 230 * S)], fill=(255, 230, 120))
    for k in range(3):
        y = 60 - k * 25
        d.arc(((110 + k * 15) * S, y * S, (190 + k * 15) * S, (y + 50) * S), 180, 360, fill=(150, 150, 160), width=6 * S)
    return im.resize((300, 300), Image.LANCZOS)


def factory_pic():
    S = 3
    im = Image.new("RGBA", (320 * S, 260 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((20 * S, 140 * S, 300 * S, 250 * S), fill=(200, 205, 215), outline=OUTL, width=5 * S)
    d.polygon([(20 * S, 140 * S), (110 * S, 100 * S), (110 * S, 140 * S), (200 * S, 100 * S), (200 * S, 140 * S), (300 * S, 100 * S), (300 * S, 140 * S)],
              fill=(170, 175, 190), outline=OUTL)
    d.rectangle((230 * S, 30 * S, 265 * S, 110 * S), fill=(160, 160, 170), outline=OUTL, width=4 * S)
    for k in range(3):
        d.ellipse(((240 + k * 15) * S, (5 - k * 2) * S, (275 + k * 18) * S, (35 - k * 2) * S), fill=(150, 150, 160))
    return im.resize((320, 260), Image.LANCZOS)


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
    pops, glows = [], []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    add, cam = bd.add, bd.camera
    A, Bc, C = (960, 540), (PW + 960, 540), (2 * PW + 960, 540)
    D, E, Fp = (960, PH + 540), (PW + 960, PH + 540), (2 * PW + 960, PH + 540)
    cam(0, *A, 1.0, 0.1)

    # ---------------- HOOK (A)
    s = sc["hook"]
    lg = pop(sv("poumons_01"), 500, 540, h=720, t=0.3)
    hk = [lg, panel(980, 180, 1780, 400, PINK, s.t("three") - 0.3), text("3+ million deaths", 1380, 270, 66, RED_T, s.t("three"), "c"),
          text("every year, worldwide", 1380, 350, 42, MAROON, s.t("world"), "c"),
          text("many never heard its name", 1380, 500, 46, PURPLE, s.t("heard"), "c"),
          text("steals the ability to breathe OUT", 1380, 620, 46, RED_T, s.t("steals"), "c"),
          text("what is it?", 1380, 760, 60, BLUE_T, s.t("what") - 0.3, "c")]

    # ---------------- WHAT (B)
    s = sc["what"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, hk + [lg])
    X = PW
    letters = [("C", "chronic", "long-term"), ("O", "obstructive", "blocks airflow"), ("P", "pulmonary", "lungs"), ("D", "disease", "")]
    wh = [text("COPD", X + 960, 120, 100, MAROON, s.t("copd"), "c")]
    for i, (L, w, m) in enumerate(letters):
        tt = s.t(w)
        x0 = X + 120 + i * 430
        wh += [panel(x0, 220, x0 + 400, 500, [CREAM, PINK, SKY, LILAC][i], tt - 0.2), text(L, x0 + 200, 320, 110, [GOLD_T, RED_T, BLUE_T, PURPLE][i], tt, "c"),
               text(w, x0 + 200, 420, 42, MAROON, tt + 0.2, "c")]
        if m:
            wh.append(text(m, x0 + 200, 470, 32, MAROON, tt + 0.5, "c"))
    wh += [panel(X + 360, 580, X + 1560, 720, MINT, s.t("hard") - 0.3), text("hard to breathe OUT", X + 960, 665, 60, GREEN_T, s.t("hard"), "c"),
           text("emphysema", X + 600, 860, 56, RED_T, s.t("emphysema")), text("+ chronic bronchitis", X + 1000, 860, 56, GOLD_T, s.t("chronic", 2) - 0.5)]

    # ---------------- EMPHYSEMA (C)
    s = sc["emphysema"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, wh)
    X = 2 * PW
    tm = s.t("merge")
    em = [text("emphysema", X + 960, 100, 76, RED_T, s.start + 0.3, "c"),
          pop(sacs(True), X + 380, 450, h=420, t=s.start + 0.6), text("healthy: many small sacs", X + 380, 700, 40, GREEN_T, s.start + 0.9, "c"),
          text("air sac walls damaged", X + 960, 260, 44, MAROON, s.t("walls"), "c"),
          pop(sacs(False), X + 1540, 450, h=420, t=tm), text("fewer, bigger sacs", X + 1540, 700, 40, RED_T, tm + 0.3, "c"),
          lead([(X + 640, 450), (X + 1280, 450)], tm - 0.2, MAROON, 7, 0.5, arrow=True),
          text("less surface for oxygen", X + 960, 520, 40, BLUE_T, s.t("surface"), "c"),
          panel(X + 360, 800, X + 1560, 960, PINK, s.t("stretch") - 0.3), text("lungs lose stretch", X + 960, 860, 50, RED_T, s.t("stretch"), "c"),
          text("-> old air gets trapped", X + 960, 925, 42, MAROON, s.t("trapped") - 0.6, "c")]

    # ---------------- BRONCHITIS (D)
    s = sc["bronchitis"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, em)
    br = [text("chronic bronchitis", 960, PH + 100, 76, GOLD_T, s.start + 0.3, "c"),
          pop(sv("bronche_saine"), 360, PH + 440, h=380, t=s.start + 0.6), text("healthy airway", 360, PH + 670, 40, GREEN_T, s.start + 0.9, "c"),
          pop(sv("bronche_infla"), 1560, PH + 440, h=380, t=s.t("inflamed") - 0.3), text("inflamed + swollen", 1560, PH + 670, 40, RED_T, s.t("swollen"), "c"),
          text("too much mucus", 960, PH + 380, 50, GOLD_T, s.t("mucus"), "c"),
          text("cleaning hairs damaged", 960, PH + 480, 44, PURPLE, s.t("hairs"), "c"),
          panel(500, PH + 780, 1420, PH + 920, CREAM, s.t("builds") - 0.3), text("-> mucus builds up -> long-term cough", 960, PH + 865, 44, MAROON, s.t("builds") - 0.1, "c")]

    # ---------------- CAUSES (E)
    s = sc["causes"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, br)
    X = PW
    ca = title("what causes COPD?", X + 960, PH + 90, s.start + 0.3)
    items = [("smoking", "smoking (main cause)", sv("cigarettes_01"), PINK), ("cooking", "indoor cooking smoke", fire_pic(), CREAM),
             ("pollution", "air pollution", None, SKY), ("chemicals", "dust + chemicals at work", factory_pic(), MINT), ("genetic", "rarely: genetic", None, LILAC)]
    for i, (w, lab, pic, col) in enumerate(items):
        tt = s.t(w) - (0.8 if w == "genetic" else 0)
        x0, y0 = X + 60 + (i % 3) * 610 + (305 if i >= 3 else 0), PH + 190 + (i // 3) * 420
        ca += [panel(x0, y0, x0 + 580, y0 + 380, col, tt - 0.3), text(lab, x0 + 290, y0 + 340, 40, MAROON, tt, "c")]
        if pic is not None:
            ca.append(pop(pic, x0 + 290, y0 + 160, h=240, t=tt - 0.1))
        else:
            ca.append(text("+", x0 + 290, y0 + 170, 150, [BLUE_T, PURPLE][i == 4], tt, "c"))

    # ---------------- SYMPTOMS (F)
    s = sc["symptoms"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, ca)
    X = 2 * PW
    sy = title("main signs", X + 960, PH + 90, s.start + 0.3)
    signs = [("shortness", "short of breath (when active)", BLUE_T), ("cough", "cough that won't go away", GOLD_T), ("mucus", "lots of mucus", GOLD_T),
             ("wheezing", "wheezing", PURPLE), ("tiredness", "tiredness", MAROON), ("frequent", "frequent chest infections", RED_T)]
    for i, (w, lab, col) in enumerate(signs):
        sy.append(text("- " + lab, X + 140 + (i // 3) * 880, PH + 230 + (i % 3) * 120, 48, col, s.t(w)))
    sy += [panel(X + 360, PH + 680, X + 1560, PH + 830, LILAC, s.t("slowly") - 0.8), text("gets worse slowly, over years", X + 960, PH + 770, 52, PURPLE, s.t("slowly") - 0.6, "c")]

    # ---------------- DIAGNOSE (A)
    s = sc["diagnose"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, sy)
    tsp = s.t("spirometry")
    dg = [text("spirometry", 960, 140, 90, BLUE_T, tsp, "c"),
          pop(AS.meter_pic(), 960, 330, w=520, t=tsp + 0.2),
          text("how much air you blow out in 1 second", 960, 500, 48, MAROON, s.t("second") - 0.6, "c"),
          panel(260, 600, 1660, 820, PINK, s.t("slowly") - 0.3), text("in COPD: air comes out too slowly", 960, 680, 52, RED_T, s.t("slowly"), "c"),
          text("even after airway-opening medicine", 960, 765, 42, MAROON, s.t("even") - 0.3, "c")]

    # ---------------- TREAT (B)
    s = sc["treat"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, dg)
    X = PW
    tr = [text("can't be undone, but can be slowed", X + 960, 100, 60, PURPLE, s.t("undone"), "c")]
    tq = s.t("quitting")
    tr += [panel(X + 360, 180, X + 1560, 340, MINT, tq - 0.3), text("quit smoking = the most important step", X + 960, 275, 52, GREEN_T, tq, "c")]
    tips = [("inhalers", "inhalers open airways", sv("Inhalateur"), SKY, BLUE_T), ("breathing", "breathing exercise programs", None, CREAM, GOLD_T),
            ("vaccines", "vaccines prevent infections", sv("seringue_01"), PINK, RED_T), ("oxygen", "oxygen for some", None, LILAC, PURPLE)]
    for i, (w, lab, pic, col, tc_) in enumerate(tips):
        tt = s.t(w) - (0.8 if w == "oxygen" else 0)
        x0, y0 = X + 120 + (i % 2) * 880, 400 + (i // 2) * 290
        tr += [panel(x0, y0, x0 + 820, y0 + 250, col, tt - 0.3), text(lab, x0 + (520 if pic else 410), y0 + 140, 42, tc_, tt, "c")]
        if pic is not None:
            tr.append(pop(pic, x0 + 130, y0 + 125, h=200 if w == "inhalers" else None, w=None if w == "inhalers" else 220, t=tt - 0.1))

    # ---------------- EMERGENCY (C)
    s = sc["emergency"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, tr)
    X = 2 * PW
    em2 = [text("get urgent help if:", X + 960, 110, 66, RED_T, s.start + 0.3, "c")]
    signs = [("suddenly", "breathlessness suddenly much worse"), ("lips", "lips or fingertips turn blue"), ("chest", "chest pain"),
             ("confused", "confused or very sleepy")]
    for i, (w, lab) in enumerate(signs):
        em2.append(text("- " + lab, X + 180, 260 + i * 115, 54, PURPLE, s.t(w)))
    tc = s.t("call")
    em2 += [panel(X + 200, 760, X + 1720, 920, PINK, tc - 0.6), text("-> call your local emergency number", X + 960, 855, 56, RED_T, tc - 0.4, "c"),
            pop(sv("Smartphone-1"), X + 1620, 400, h=360, t=tc - 0.6)]

    # ---------------- SUMMARY (D)
    s = sc["summary"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, em2)
    sm = title("remember", 960, PH + 100, s.start + 0.4)
    cards = [("hard", "hard to", "breathe out", PINK, RED_T, 400), ("smoking", "smoking +", "indoor smoke", CREAM, GOLD_T, 960),
             ("quitting", "quitting", "slows it down", MINT, GREEN_T, 1520)]
    for w, a, b, col, tc_, x in cards:
        tt = s.t(w) - 0.3
        sm += [panel(x - 265, PH + 220, x + 265, PH + 560, col, tt - 0.2), text(a, x, PH + 350, 54, tc_, tt, "c"), text(b, x, PH + 450, 46, MAROON, tt + 0.6, "c")]
    tn = s.t("next")
    sm += [panel(360, PH + 700, 1560, PH + 860, LILAC, tn - 0.3), text("next: the brain + nerves", 960, PH + 795, 56, PURPLE, tn, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render(out="copd.mp4"):
    import subprocess
    import render_ecg as RE
    bd, sc = build()
    vid = HERE / "copd_video_only.mp4"
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
            OF.credit(bd.frame(t)).save(HERE / f"copd_{t:06.1f}.png")
        print("ok", round(bd.total, 1), ends)
    else:
        render()
