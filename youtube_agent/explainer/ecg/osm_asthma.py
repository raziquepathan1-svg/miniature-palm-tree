"""Respiratory series: Asthma (owner-approved script, narration only)."""
import json
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "asthma")))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_preview as OP  # noqa: E402
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_bp as BPm  # noqa: E402
import osm_lungs as LU  # noqa: E402
import osm_hf as HF  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OF.MAROON, OF.PURPLE, OP.BLUE_T, OP.RED_T, OP.GOLD_T, OF.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OF.PINK, OF.LILAC, OF.CREAM, OF.MINT, OF.SKY
PW, PH = 1920, 1080
sv = LU.sv
OUTL = (70, 60, 70)


def straw_pic(narrow=False):
    S = 3
    im = Image.new("RGBA", (700 * S, 160 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(70):
        x = 10 + i * 10
        h = 60 if not narrow else 60 - 45 * (i / 69)
        d.rectangle(((x) * S, (80 - h) * S, (x + 11) * S, (80 + h) * S), fill=(120, 200, 230) if i % 8 < 4 else (250, 250, 255))
    d.line([(10 * S, 20 * S), (710 * S, (80 - (15 if narrow else 60)) * S)], fill=OUTL, width=5 * S)
    d.line([(10 * S, 140 * S), (710 * S, (80 + (15 if narrow else 60)) * S)], fill=OUTL, width=5 * S)
    return im.resize((700, 160), Image.LANCZOS)


def meter_pic():
    S = 3
    im = Image.new("RGBA", (420 * S, 160 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((60 * S, 30 * S, 410 * S, 130 * S), radius=30 * S, fill=(235, 240, 250), outline=OUTL, width=5 * S)
    d.rounded_rectangle((5 * S, 55 * S, 70 * S, 105 * S), radius=10 * S, fill=(180, 190, 205), outline=OUTL, width=4 * S)
    for k in range(9):
        x = 120 + k * 32
        d.line([(x * S, 45 * S), (x * S, (65 if k % 2 else 75) * S)], fill=OUTL, width=3 * S)
    d.polygon([(250 * S, 80 * S), (270 * S, 110 * S), (230 * S, 110 * S)], fill=(230, 60, 60))
    return im.resize((420, 160), Image.LANCZOS)


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
    hk = [pop(straw_pic(False), 520, 300, w=700, t=0.4), text("normal", 520, 420, 44, GREEN_T, 0.8, "c"),
          pop(straw_pic(True), 520, 640, w=700, t=s.t("thinner") - 0.3), text("thinner + thinner...", 520, 760, 44, RED_T, s.t("thinner"), "c"),
          text("an asthma attack", 1400, 300, 66, RED_T, s.t("asthma"), "c"),
          panel(1040, 440, 1780, 640, SKY, s.t("hundred") - 0.3), text("~260 million", 1410, 530, 70, BLUE_T, s.t("hundred"), "c"),
          text("people live with asthma", 1410, 600, 40, MAROON, s.t("live"), "c"),
          text("what happens inside?", 1400, 790, 54, PURPLE, s.t("actually") - 0.3, "c")]

    # ---------------- WHAT (B)
    s = sc["what"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, hk)
    X = PW
    lg = pop(sv("poumons_01"), X + 520, 540, h=720, t=s.start + 0.3)
    wh = [lg, text("asthma", X + 1360, 160, 90, RED_T, s.t("asthma"), "c"),
          text("long-term disease of the airways", X + 1360, 260, 44, MAROON, s.t("long"), "c"),
          text("bronchi + bronchioles", X + 1360, 340, 48, BLUE_T, s.t("bronchi"), "c")]
    ti = s.t("inflamed")
    for fx_, fy_ in ((0.35, 0.45), (0.65, 0.45), (0.3, 0.65), (0.7, 0.65), (0.5, 0.25)):
        glows.append((ti, lg.map((fx_ * lg.src.width, fy_ * lg.src.height)), s.end - ti, 60))
    wh += [panel(X + 1000, 440, X + 1720, 640, PINK, ti - 0.3), text("inflamed", X + 1360, 520, 60, RED_T, ti, "c"),
           text("+ extra sensitive", X + 1360, 595, 46, RED_T, s.t("sensitive"), "c"),
           text("-> they overreact", X + 1360, 760, 52, PURPLE, s.t("overreact"), "c")]

    # ---------------- ATTACK (C)
    s = sc["attack"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, wh + [lg])
    X = 2 * PW
    at = title("during an attack: 3 things at once", X + 960, 90, s.start + 0.3)
    at += [pop(sv("bronche_saine"), X + 380, 420, h=380, t=s.start + 0.5), text("normal airway", X + 380, 650, 44, GREEN_T, s.start + 0.8, "c"),
           pop(sv("bronche_infla"), X + 1540, 420, h=380, t=s.t("narrower") - 0.6), text("asthma attack", X + 1540, 650, 44, RED_T, s.t("narrower") - 0.4, "c")]
    items = [("muscles", "1. muscles squeeze tight", RED_T), ("lining", "2. lining swells", PURPLE), ("mucus", "3. thick sticky mucus", GOLD_T)]
    for i, (w, lab, col) in enumerate(items):
        at.append(text(lab, X + 960, 300 + i * 110, 46, col, s.t(w), "c"))
    at += [panel(X + 500, 760, X + 1420, 900, PINK, s.t("together") - 0.3), text("= much narrower airway", X + 960, 845, 52, RED_T, s.t("together"), "c")]

    # ---------------- WHEEZE (D)
    s = sc["wheeze"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, at)
    wz = [pop(straw_pic(True), 560, PH + 400, w=820, t=s.start + 0.3),
          text("air squeezes through a narrow pipe", 960, PH + 150, 50, MAROON, s.t("squeeze"), "c")]
    tw = s.t("wheeze")
    for k in range(3):
        wz.append(add(B.Stroke(B.smooth([(1040 + k * 50, PH + 330), (1065 + k * 50, PH + 400), (1040 + k * 50, PH + 470)], 8), BLUE_T, 6,
                               t=tw + 0.15 * k, dur=0.3, arrow=False)))
    wz += [text("= wheeze", 1400, PH + 400, 70, BLUE_T, tw), text("(whistling sound)", 1400, PH + 470, 40, MAROON, s.t("whistling"))]
    tt = s.t("trapped")
    wz += [panel(300, PH + 620, 1620, PH + 900, CREAM, tt - 0.3), text("air gets trapped in the lungs", 960, PH + 720, 52, GOLD_T, tt, "c"),
           text("-> chest feels tight", 960, PH + 810, 52, RED_T, s.t("trapped") + 0.8, "c")]

    # ---------------- SYMPTOMS (E)
    s = sc["symptoms"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, wz)
    X = PW
    sy = title("main signs", X + 960, PH + 100, s.start + 0.3)
    signs = [("wheezing", "wheezing", BLUE_T), ("coughing", "coughing (often night / early morning)", PURPLE),
             ("tight", "tight chest", RED_T), ("shortness", "shortness of breath", GOLD_T)]
    for i, (w, lab, col) in enumerate(signs):
        sy.append(text("- " + lab, X + 200, PH + 240 + i * 120, 56, col, s.t(w) - (0.6 if w == "shortness" else 0)))
    sy += [panel(X + 400, PH + 760, X + 1520, PH + 900, LILAC, s.t("come") - 0.8),
           text("they come and go: mild or severe", X + 960, PH + 845, 46, PURPLE, s.t("come") - 0.6, "c")]

    # ---------------- TRIGGERS (F)
    s = sc["triggers"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, sy)
    X = 2 * PW
    tg = title("common triggers", X + 960, PH + 90, s.start + 0.3)
    trig = [("dust", "dust mites"), ("pollen", "pollen"), ("pet", "pet hair"), ("mold", "mold"), ("smoke", "smoke"),
            ("pollution", "air pollution"), ("cold", "cold air"), ("exercise", "exercise"), ("colds", "colds + flu"), ("strong", "strong smells")]
    for i, (w, lab) in enumerate(trig):
        tt = s.t(w) - (0.8 if i >= 8 else 0)
        x0, y0 = X + 90 + (i % 5) * 355, PH + 200 + (i // 5) * 190
        tg += [panel(x0, y0, x0 + 330, y0 + 150, [PINK, CREAM, SKY, MINT, LILAC][i % 5], tt - 0.2), text(lab, x0 + 165, y0 + 90, 42, MAROON, tt, "c")]
    tp = s.t("pet")
    tg += [pop(sv("Chat"), X + 700, PH + 800, h=260, t=tp), pop(sv("Chien"), X + 1200, PH + 800, h=260, t=tp + 0.3)]

    # ---------------- DIAGNOSE (A)
    s = sc["diagnose"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, tg)
    dg = title("how it's diagnosed", 960, 90, s.start + 0.3)
    tsp = s.t("spirometry")
    dg += [pop(sv("stethoscope"), 300, 420, h=360, t=s.t("listen") - 0.2), text("listen to the chest", 300, 650, 40, MAROON, s.t("listen"), "c"),
           panel(620, 200, 1820, 560, SKY, tsp - 0.3), text("spirometry", 1220, 280, 66, BLUE_T, tsp, "c"),
           text("how much air you can blow out", 1220, 380, 44, MAROON, s.t("much"), "c"), text("+ how fast", 1220, 450, 44, MAROON, s.t("fast"), "c"),
           pop(meter_pic(), 900, 800, w=420, t=s.t("peak") - 0.2),
           text("peak flow meter", 1420, 780, 52, GREEN_T, s.t("peak") - 0.1, "c"), text("tracks it at home", 1420, 850, 40, MAROON, s.t("peak") + 0.4, "c")]

    # ---------------- INHALERS (B)
    s = sc["inhalers"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, dg)
    X = PW
    ih = title("2 kinds of inhaler", X + 960, 90, s.start + 0.3)
    tr, tpv = s.t("reliever"), s.t("preventer")
    ih += [panel(X + 120, 180, X + 900, 940, SKY, tr - 0.3), pop(sv("Inhalateur"), X + 300, 520, h=420, t=tr),
           text("reliever", X + 640, 300, 66, BLUE_T, tr, "c"), text("opens airways", X + 640, 400, 42, MAROON, s.t("opens"), "c"),
           text("within minutes", X + 640, 460, 42, MAROON, s.t("minutes"), "c"), text("relaxes tight muscles", X + 640, 560, 38, MAROON, s.t("relaxing"), "c"),
           text("for symptoms", X + 640, 640, 40, BLUE_T, s.t("symptoms"), "c"),
           panel(X + 1020, 180, X + 1800, 940, MINT, tpv - 0.3), pop(sv("Inhalateur"), X + 1200, 520, h=420, t=tpv),
           text("preventer", X + 1540, 300, 66, GREEN_T, tpv, "c"), text("used every day", X + 1540, 400, 42, MAROON, s.t("every"), "c"),
           text("calms inflammation", X + 1540, 480, 40, MAROON, s.t("calms"), "c"), text("fewer attacks", X + 1540, 580, 42, GREEN_T, s.t("attacks") - 0.6, "c")]

    # ---------------- EMERGENCY (C)
    s = sc["emergency"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, ih)
    X = 2 * PW
    em = [text("get emergency help if:", X + 960, 110, 66, RED_T, s.start + 0.3, "c")]
    signs = [("hard", "breathing is very hard"), ("speak", "can't speak in full sentences"), ("lips", "lips / nails turn blue or grey"),
             ("reliever", "reliever isn't helping")]
    for i, (w, lab) in enumerate(signs):
        em.append(text("- " + lab, X + 200, 260 + i * 120, 56, PURPLE, s.t(w)))
    tc = s.t("call")
    em += [panel(X + 200, 760, X + 1720, 920, PINK, tc - 0.6), text("-> call your local emergency number", X + 960, 855, 56, RED_T, tc - 0.4, "c"),
           pop(sv("Smartphone-1"), X + 1600, 400, h=380, t=tc - 0.6)]

    # ---------------- SUMMARY (D)
    s = sc["summary"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, em)
    sm = title("remember", 960, PH + 100, s.start + 0.4)
    cards = [("squeeze", "squeeze, swell", "+ mucus", PINK, RED_T, 400), ("triggers", "know your", "triggers", CREAM, GOLD_T, 960),
             ("preventer", "preventer daily", "reliever for help", MINT, GREEN_T, 1520)]
    for w, a, b, col, tc_, x in cards:
        tt = s.t(w) - 0.3
        sm += [panel(x - 265, PH + 220, x + 265, PH + 560, col, tt - 0.2), text(a, x, PH + 350, 50, tc_, tt, "c"), text(b, x, PH + 450, 44, MAROON, tt + 0.6, "c")]
    sm += [panel(360, PH + 620, 1560, PH + 740, SKY, s.t("cured") - 0.3), text("not cured, but controlled", 960, PH + 700, 52, BLUE_T, s.t("cured"), "c")]
    tn = s.t("next")
    sm += [panel(460, PH + 800, 1460, PH + 950, LILAC, tn - 0.3), text("next: pneumonia", 960, PH + 895, 54, PURPLE, tn, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render(out="asthma.mp4"):
    import subprocess
    import render_ecg as RE
    bd, sc = build()
    vid = HERE / "asthma_video_only.mp4"
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
            OF.credit(bd.frame(t)).save(HERE / f"asthma_{t:06.1f}.png")
        print("ok", round(bd.total, 1), ends)
    else:
        render()
