"""Respiratory series: Pneumonia (owner-approved script, narration only)."""
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "pneu")))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_preview as OP  # noqa: E402
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_bp as BPm  # noqa: E402
import osm_lungs as LU  # noqa: E402
import osm_hf as HF  # noqa: E402
import osm_breath as BR  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OF.MAROON, OF.PURPLE, OP.BLUE_T, OP.RED_T, OP.GOLD_T, OF.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OF.PINK, OF.LILAC, OF.CREAM, OF.MINT, OF.SKY
PW, PH = 1920, 1080
sv = LU.sv
OUTL = (70, 60, 70)


def cocci_pic():
    """Streptococcus pneumoniae: lancet-shaped cocci in pairs (diplococci) with a capsule."""
    S = 3
    im = Image.new("RGBA", (360 * S, 260 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for cx, cy, a in ((110, 90, -20), (250, 170, 25)):
        d.ellipse(((cx - 95) * S, (cy - 60) * S, (cx + 95) * S, (cy + 60) * S), fill=(230, 240, 200), outline=(170, 190, 120), width=4 * S)
        for dx in (-42, 42):
            d.ellipse(((cx + dx - 42) * S, (cy - 36) * S, (cx + dx + 42) * S, (cy + 36) * S), fill=(150, 110, 200), outline=OUTL, width=4 * S)
    return im.resize((360, 260), Image.LANCZOS)


def virus_pic():
    S = 3
    im = Image.new("RGBA", (260 * S, 260 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, r = 130, 70
    for k in range(16):
        a = 2 * math.pi * k / 16
        x1, y1 = c + r * math.cos(a), c + r * math.sin(a)
        x2, y2 = c + (r + 38) * math.cos(a), c + (r + 38) * math.sin(a)
        d.line([(x1 * S, y1 * S), (x2 * S, y2 * S)], fill=(200, 80, 90), width=7 * S)
        d.ellipse(((x2 - 12) * S, (y2 - 12) * S, (x2 + 12) * S, (y2 + 12) * S), fill=(230, 110, 120), outline=OUTL, width=3 * S)
    d.ellipse(((c - r) * S, (c - r) * S, (c + r) * S, (c + r) * S), fill=(250, 180, 170), outline=OUTL, width=5 * S)
    return im.resize((260, 260), Image.LANCZOS)


def sacs_pic(fill):
    """3 alveoli; fill 0 = air (light), 1 = filled with fluid/pus (yellow-grey)."""
    S = 3
    im = Image.new("RGBA", (520 * S, 320 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for cx, cy in ((130, 170), (260, 140), (390, 170)):
        d.ellipse(((cx - 115) * S, (cy - 115) * S, (cx + 115) * S, (cy + 115) * S), fill=(250, 225, 220), outline=(200, 110, 110), width=6 * S)
        if fill:
            d.chord(((cx - 105) * S, (cy - 105) * S, (cx + 105) * S, (cy + 105) * S), 200 - 180 * fill, 340 + 180 * fill,
                    fill=(235, 215, 140), outline=(200, 170, 90))
            for k in range(6):
                a = k * 1.1
                x, y = cx + 50 * math.cos(a), cy + 35 + 25 * math.sin(a)
                d.ellipse(((x - 12) * S, (y - 12) * S, (x + 12) * S, (y + 12) * S), fill=(245, 235, 245), outline=(150, 110, 180), width=2 * S)
    return im.resize((520, 320), Image.LANCZOS)


def xray_patch():
    im = sv("Radio_thorax").convert("RGBA")
    w, h = im.size
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).ellipse((int(w * 0.58), int(h * 0.55), int(w * 0.85), int(h * 0.8)), fill=(255, 255, 255, 170))
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(w // 30)))
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
    pops, glows = [], []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    add, cam = bd.add, bd.camera
    A, Bc, C = (960, 540), (PW + 960, 540), (2 * PW + 960, 540)
    D, E, Fp = (960, PH + 540), (PW + 960, PH + 540), (2 * PW + 960, PH + 540)
    cam(0, *A, 1.0, 0.1)

    # ---------------- HOOK (A)
    s = sc["hook"]
    hk = [pop(sacs_pic(0), 480, 330, w=640, t=0.4), text("normal: full of air", 480, 520, 46, BLUE_T, s.t("air"), "c"),
          pop(sacs_pic(1), 480, 760, w=640, t=s.t("pneumonia") - 0.2), text("pneumonia: fluid + pus", 480, 950, 46, RED_T, s.t("fluid"), "c"),
          text("pneumonia", 1380, 260, 90, RED_T, s.t("pneumonia"), "c"),
          text("how does an infection", 1380, 450, 50, PURPLE, s.t("infection") - 0.6, "c"), text("flood the lungs?", 1380, 530, 50, PURPLE, s.t("flood"), "c"),
          text("why so dangerous?", 1380, 680, 54, RED_T, s.t("why") - 0.2, "c")]

    # ---------------- WHAT (B)
    s = sc["what"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, hk)
    X = PW
    lg = pop(sv("poumons_01"), X + 520, 540, h=720, t=s.start + 0.3)
    inf = lg.map((0.75 * lg.src.width, 0.72 * lg.src.height))
    glows.append((s.t("inflames"), inf, s.end - s.t("inflames"), 120))
    wh = [lg, text("an infection", X + 1360, 180, 64, RED_T, s.t("infection"), "c"),
          text("that inflames the air sacs", X + 1360, 260, 46, MAROON, s.t("inflames"), "c"),
          text("(alveoli)", X + 1360, 325, 42, BLUE_T, s.t("alveoli"), "c"),
          text("one or both lungs", X + 1360, 420, 44, PURPLE, s.t("both"), "c"),
          panel(X + 1000, 560, X + 1720, 760, PINK, s.t("fill") - 0.3), text("sacs fill with fluid", X + 1360, 640, 50, RED_T, s.t("fill"), "c"),
          text("-> less oxygen into the blood", X + 1360, 720, 40, MAROON, s.t("oxygen") - 0.4, "c")]

    # ---------------- CAUSES (C)
    s = sc["causes"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, wh + [lg])
    X = 2 * PW
    tb, tv, tf = s.t("bacteria"), s.t("viruses"), s.t("fungi")
    ca = title("caused by germs", X + 960, 90, s.start + 0.3)
    ca += [panel(X + 80, 180, X + 660, 700, CREAM, tb - 0.3), pop(cocci_pic(), X + 370, 360, w=380, t=tb), text("bacteria", X + 370, 540, 56, GOLD_T, tb, "c"),
           text("most often", X + 370, 600, 38, MAROON, tb + 0.3, "c"), text("Streptococcus pneumoniae", X + 370, 655, 32, PURPLE, s.t("streptococcus"), "c"),
           panel(X + 700, 180, X + 1280, 700, PINK, tv - 0.3), pop(virus_pic(), X + 990, 360, w=260, t=tv), text("viruses", X + 990, 540, 56, RED_T, tv, "c"),
           text("flu, RSV, COVID-19", X + 990, 610, 38, MAROON, s.t("flu"), "c"),
           panel(X + 1320, 180, X + 1840, 700, MINT, tf - 0.3), text("fungi", X + 1580, 540, 56, GREEN_T, tf, "c"), text("less often", X + 1580, 610, 38, MAROON, tf + 0.3, "c")]
    td = s.t("spread") - 0.3
    ca += [panel(X + 300, 760, X + 1620, 900, SKY, td - 0.3), text("spread by droplets from coughs + sneezes", X + 960, 845, 48, BLUE_T, td, "c")]

    # ---------------- INSIDE (D)
    s = sc["inside"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, ca)
    ti = s.t("immune")
    ins = [text("inside the lung", 960, PH + 90, 70, MAROON, s.start + 0.3, "c"),
           pop(sacs_pic(0), 420, PH + 350, w=560, t=s.start + 0.5), pop(cocci_pic(), 420, PH + 330, w=200, t=s.t("germs") + 0.2),
           text("germs reach the alveoli", 420, PH + 540, 40, MAROON, s.t("reach"), "c"),
           text("immune system fights back", 1350, PH + 250, 50, PURPLE, ti, "c"),
           pop(sv("neutrophile_01"), 1180, PH + 420, h=200, t=s.t("white") - 0.2), text("white blood cells rush in", 1300, PH + 420, 44, BLUE_T, s.t("white"))]
    tl = s.t("leaks")
    ins += [pop(sacs_pic(1), 420, PH + 760, w=560, t=tl), text("fluid leaks in, air pushed out", 420, PH + 950, 40, RED_T, s.t("pushed") - 0.3, "c"),
            panel(900, PH + 640, 1800, PH + 900, CREAM, s.t("solid") - 0.3), text("lung becomes solid + heavy", 1350, PH + 730, 48, GOLD_T, s.t("solid"), "c"),
            text("like a wet sponge", 1350, PH + 820, 50, MAROON, s.t("sponge") - 0.6, "c")]

    # ---------------- SYMPTOMS (E)
    s = sc["symptoms"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, ins)
    X = PW
    sy = title("main signs", X + 960, PH + 90, s.start + 0.3)
    signs = [("cough", "cough (often yellow / green phlegm)", GOLD_T), ("fever", "fever + chills", RED_T), ("shortness", "shortness of breath", BLUE_T),
             ("chest", "chest pain when breathing / coughing", PURPLE), ("tiredness", "tiredness", MAROON)]
    for i, (w, lab, col) in enumerate(signs):
        sy.append(text("- " + lab, X + 160, PH + 210 + i * 105, 52, col, s.t(w)))
    to = s.t("older")
    sy += [panel(X + 300, PH + 780, X + 1620, PH + 920, LILAC, to - 0.6), text("older adults: may only seem confused or weak", X + 960, PH + 865, 44, PURPLE, to - 0.4, "c")]

    # ---------------- RISK (F)
    s = sc["risk"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, sy)
    X = 2 * PW
    rk = title("who is at higher risk?", X + 960, PH + 90, s.start + 0.3)
    risks = [("young", "young children"), ("sixty", "adults over 65"), ("smokers", "smokers"), ("asthma", "asthma"), ("diabetes", "diabetes"),
             ("heart", "heart disease"), ("immune", "weak immune system")]
    for i, (w, lab) in enumerate(risks):
        tt = s.t(w) - (0.8 if w == "immune" else 0)
        x0, y0 = X + 120 + (i % 4) * 430, PH + 220 + (i // 4) * 260
        if i >= 4:
            x0 += 215
        rk += [panel(x0, y0, x0 + 400, y0 + 200, [PINK, CREAM, SKY, MINT][i % 4], tt - 0.2), text(lab, x0 + 200, y0 + 115, 38 if len(lab) > 15 else 44, MAROON, tt, "c")]
    rk.append(text("anyone can get it", X + 960, PH + 830, 50, PURPLE, s.t("anyone"), "c"))

    # ---------------- DIAGNOSE (A)
    s = sc["diagnose"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, rk)
    tx = s.t("x-ray")
    dg = title("how doctors find it", 960, 90, s.start + 0.3)
    dg += [pop(sv("stethoscope"), 230, 380, h=300, t=s.t("listen") - 0.2), text("crackling sounds", 230, 580, 40, MAROON, s.t("crackling"), "c"),
           text("oxygen finger clip", 230, 700, 40, BLUE_T, s.t("oxygen"), "c"),
           pop(xray_patch(), 900, 540, h=720, t=tx - 0.2), text("chest x-ray", 1450, 330, 60, MAROON, tx, "c"),
           text("infected part =", 1450, 470, 48, RED_T, s.t("infected"), "c"), text("white patch", 1450, 550, 66, RED_T, s.t("white") - 0.2, "c")]
    xp = (900 + 720 * 0.71 * 0.5, 540 + 720 * 0.17)  # roughly at the patch
    dg.append(lead([(1300, 560), (1080, 640)], s.t("white"), RED_T, 6, 0.4, arrow=True))

    # ---------------- TREAT (B)
    s = sc["treat"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, dg)
    X = PW
    tr = title("treatment", X + 960, 90, s.start + 0.3)
    tbac = s.t("bacterial")
    tr += [panel(X + 100, 180, X + 900, 560, CREAM, tbac - 0.3), pop(HF.pills_pic(), X + 300, 330, h=140, t=tbac),
           text("bacterial:", X + 640, 290, 50, GOLD_T, tbac, "c"), text("antibiotics", X + 640, 370, 56, GOLD_T, s.t("antibiotics"), "c"),
           text("take the full course", X + 500, 470, 42, RED_T, s.t("full"), "c"), text("exactly as prescribed", X + 500, 525, 38, MAROON, s.t("exactly"), "c"),
           panel(X + 1020, 180, X + 1820, 560, SKY, s.t("viral") - 0.3), text("viral:", X + 1420, 290, 50, BLUE_T, s.t("viral"), "c"),
           text("rest + fluids", X + 1420, 380, 50, BLUE_T, s.t("rest"), "c"), text("sometimes antivirals", X + 1420, 460, 42, MAROON, s.t("antiviral"), "c"),
           panel(X + 360, 640, X + 1560, 820, PINK, s.t("severe") - 0.6), text("severe: hospital + extra oxygen", X + 960, 740, 52, RED_T, s.t("severe") - 0.4, "c")]

    # ---------------- PREVENT (C)
    s = sc["prevent"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, tr)
    X = 2 * PW
    tvac = s.t("vaccines")
    pv = title("lower the risk", X + 960, 90, s.start + 0.3)
    pv += [panel(X + 100, 180, X + 1000, 520, MINT, tvac - 0.3), pop(sv("seringue_01"), X + 330, 300, w=360, t=tvac),
           text("vaccines", X + 760, 290, 56, GREEN_T, tvac, "c"), text("pneumococcus, flu, COVID", X + 550, 440, 42, MAROON, s.t("pneumococcus"), "c"),
           text("- wash your hands", X + 1100, 250, 46, BLUE_T, s.t("wash")), text("- don't smoke", X + 1100, 340, 46, PURPLE, s.t("smoke")),
           text("- cover your coughs", X + 1100, 430, 46, GOLD_T, s.t("cover"))]
    tu = s.t("urgent")
    pv += [panel(X + 100, 600, X + 1820, 900, PINK, tu - 0.3), text("get urgent help for:", X + 960, 680, 54, RED_T, tu, "c"),
           text("trouble breathing, blue lips, chest pain or confusion", X + 960, 790, 44, RED_T, s.t("trouble"), "c")]

    # ---------------- SUMMARY (D)
    s = sc["summary"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, pv)
    sm = title("remember", 960, PH + 100, s.start + 0.4)
    cards = [("fluid", "air sacs fill", "with fluid", PINK, RED_T, 400), ("cough", "cough, fever,", "breathlessness", CREAM, GOLD_T, 960),
             ("antibiotics", "antibiotics", "+ vaccines", MINT, GREEN_T, 1520)]
    for w, a, b, col, tc_, x in cards:
        tt = s.t(w) - 0.3
        sm += [panel(x - 265, PH + 220, x + 265, PH + 560, col, tt - 0.2), text(a, x, PH + 350, 50, tc_, tt, "c"), text(b, x, PH + 450, 46, MAROON, tt + 0.6, "c")]
    tn = s.t("next")
    sm += [panel(460, PH + 700, 1460, PH + 860, LILAC, tn - 0.3), text("next: COPD", 960, PH + 795, 58, PURPLE, tn, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render(out="pneumonia.mp4"):
    import subprocess
    import render_ecg as RE
    bd, sc = build()
    vid = HERE / "pneu_video_only.mp4"
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
            OF.credit(bd.frame(t)).save(HERE / f"pneu_{t:06.1f}.png")
        print("ok", round(bd.total, 1), ends)
    else:
        render()
