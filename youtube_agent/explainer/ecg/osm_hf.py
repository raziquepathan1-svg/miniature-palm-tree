"""Cardiovascular series: Heart Failure (owner-approved script, narration only)."""
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "hf")))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_preview as OP  # noqa: E402
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_bv as BV  # noqa: E402
import osm_bp as BPm  # noqa: E402
import osm_htn as HT  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OF.MAROON, OF.PURPLE, OP.BLUE_T, OP.RED_T, OP.GOLD_T, OF.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OF.PINK, OF.LILAC, OF.CREAM, OF.MINT, OF.SKY
PW, PH = 1920, 1080
sv = BPm.sv
OUTL = (70, 60, 70)


def _pad(w, h):
    S = 3
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im), S


def _done(im, w, h):
    return im.resize((w, h), Image.LANCZOS)


def pillow_pic():
    im, d, S = _pad(360, 200)
    for k, y in enumerate((120, 60)):
        d.rounded_rectangle((20 * S, (y - 10) * S, 340 * S, (y + 60) * S), radius=35 * S, fill=(235, 240, 250) if k else (245, 245, 252),
                            outline=OUTL, width=5 * S)
    return _done(im, 360, 200)


def leg_pic(swollen=True):
    im, d, S = _pad(300, 520)
    k = 1.35 if swollen else 1.0
    pts = [(110, 10), (190, 10), (185, 250), (170 + 25 * k, 380), (165 + 30 * k, 440), (285, 470), (290, 505), (60, 505),
           (70, 450), (125 - 25 * k, 380), (115, 250)]
    d.polygon([(x * S, y * S) for x, y in pts], fill=(250, 218, 205), outline=OUTL)
    d.line([(x * S, y * S) for x, y in pts + [pts[0]]], fill=OUTL, width=5 * S, joint="curve")
    if swollen:
        d.ellipse((120 * S, 395 * S, 150 * S, 425 * S), fill=(230, 190, 180), outline=(150, 100, 100), width=3 * S)  # the dent
        for y in (330, 360, 470):
            d.arc((60 * S, (y - 10) * S, 240 * S, (y + 40) * S), 200, 340, fill=(120, 160, 230), width=4 * S)
    return _done(im, 300, 520)


def xray_pic():
    im, d, S = _pad(320, 360)
    d.rounded_rectangle((10 * S, 10 * S, 310 * S, 350 * S), radius=14 * S, fill=(30, 35, 50), outline=OUTL, width=5 * S)
    for i in range(6):
        y = 80 + i * 38
        d.arc((50 * S, y * S, 270 * S, (y + 60) * S), 200, 340, fill=(200, 205, 215), width=5 * S)
    d.ellipse((120 * S, 170 * S, 230 * S, 290 * S), fill=(170, 175, 190))
    d.line([(160 * S, 40 * S), (160 * S, 320 * S)], fill=(210, 215, 225), width=8 * S)
    return _done(im, 320, 360)


def tube_pic():
    im, d, S = _pad(140, 360)
    d.rounded_rectangle((40 * S, 10 * S, 100 * S, 60 * S), radius=8 * S, fill=(120, 170, 230), outline=OUTL, width=4 * S)
    d.rounded_rectangle((45 * S, 55 * S, 95 * S, 340 * S), radius=24 * S, fill=(250, 250, 255), outline=OUTL, width=5 * S)
    d.rounded_rectangle((50 * S, 150 * S, 90 * S, 334 * S), radius=20 * S, fill=(210, 40, 50))
    return _done(im, 140, 360)


def echo_pic():
    im, d, S = _pad(380, 320)
    d.rounded_rectangle((10 * S, 10 * S, 370 * S, 250 * S), radius=16 * S, fill=(25, 30, 40), outline=OUTL, width=6 * S)
    d.pieslice((60 * S, -60 * S, 320 * S, 240 * S), 50, 130, fill=(70, 75, 90))
    d.ellipse((150 * S, 110 * S, 230 * S, 200 * S), fill=(25, 30, 40), outline=(200, 200, 210), width=4 * S)
    d.rectangle((160 * S, 250 * S, 220 * S, 290 * S), fill=(150, 155, 165), outline=OUTL, width=4 * S)
    d.rounded_rectangle((100 * S, 285 * S, 280 * S, 310 * S), radius=8 * S, fill=(150, 155, 165), outline=OUTL, width=4 * S)
    return _done(im, 380, 320)


def scale_pic():
    im, d, S = _pad(320, 200)
    d.rounded_rectangle((10 * S, 40 * S, 310 * S, 190 * S), radius=30 * S, fill=(235, 238, 245), outline=OUTL, width=6 * S)
    d.rounded_rectangle((100 * S, 60 * S, 220 * S, 110 * S), radius=10 * S, fill=(40, 60, 80))
    d.text((122 * S, 64 * S), "70.4", fill=(120, 230, 160), font=ImageFont_fallback(36 * S))
    return _done(im, 320, 200)


def ImageFont_fallback(size):
    try:
        from PIL import ImageFont
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except Exception:
        from PIL import ImageFont
        return ImageFont.load_default()


def pills_pic():
    im, d, S = _pad(320, 200)
    for x, y, c in ((60, 100, (240, 120, 120)), (160, 70, (120, 170, 240)), (250, 120, (250, 210, 90))):
        d.rounded_rectangle(((x - 50) * S, (y - 22) * S, (x + 50) * S, (y + 22) * S), radius=22 * S, fill=c, outline=OUTL, width=4 * S)
        d.line([(x * S, (y - 22) * S), (x * S, (y + 22) * S)], fill=OUTL, width=3 * S)
    return _done(im, 320, 200)


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

    def F(pic, fx, fy):
        return pic.map((fx * pic.src.width, fy * pic.src.height))

    # ---------------- HOOK (A)
    s = sc["hook"]
    hs = pop(OP.HEART, 520, 580, h=860, t=0.3)
    for k in range(int(s.dur / 0.9)):
        glows.append((0.6 + k * 0.9, hs.map(OP.P["LV"]), 0.45, 120))
    hk = [hs, text("heart failure", 1380, 160, 84, RED_T, s.t("failure"), "c"),
          panel(1000, 260, 1780, 420, MINT, s.t("hasn't") - 0.3), text("not a stopped heart!", 1390, 360, 56, GREEN_T, s.t("hasn't"), "c"),
          text("still beating", 1390, 480, 46, MAROON, s.t("beating"), "c"),
          text("so what is failing?", 1390, 600, 52, PURPLE, s.t("what"), "c"),
          panel(1000, 700, 1380, 840, SKY, s.t("breathless") - 0.2), text("breathless?", 1190, 785, 50, BLUE_T, s.t("breathless"), "c"),
          panel(1420, 700, 1800, 840, PINK, s.t("swollen") - 0.2), text("swollen?", 1610, 785, 50, RED_T, s.t("swollen"), "c")]

    # ---------------- DEFINE (B)
    s = sc["define"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, hk)
    X = PW
    df = [text("can't pump enough blood", X + 960, 110, 64, MAROON, s.t("pump"), "c"),
          text("for the body's needs", X + 960, 190, 44, MAROON, s.t("needs"), "c")]
    tw, tst = s.t("weak"), s.t("stiff")
    df += [pop(BV.ring(150, 125, (235, 120, 130, 255), (255, 250, 250, 255), RED_T), X + 520, 470, h=330, t=tw - 0.3),
           text("too weak", X + 520, 690, 56, RED_T, tw, "c"), text("can't squeeze well", X + 520, 755, 40, MAROON, s.t("squeeze"), "c"),
           pop(BV.ring(150, 55, (215, 90, 105, 255), (255, 250, 250, 255), MAROON), X + 1400, 470, h=330, t=tst - 0.3),
           text("too stiff", X + 1400, 690, 56, PURPLE, tst, "c"), text("can't fill well", X + 1400, 755, 40, MAROON, s.t("fill"), "c")]
    tb = s.t("slowly") + 0.9
    df += [panel(X + 560, 850, X + 1360, 990, SKY, s.t("slowly") - 0.3), text("blood moves slowly", X + 960, 905, 42, MAROON, s.t("slowly"), "c"),
           text("-> fluid backs up", X + 960, 965, 46, BLUE_T, tb, "c")]

    # ---------------- CAUSES (C)
    s = sc["causes"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, df)
    X = 2 * PW
    ca = title("what causes it?", X + 960, 90, s.start + 0.3)
    items = [("attack", "heart attack", sv("atherome"), 0, 0), ("high", "high blood pressure", sv("cuff_gauge"), 1, 0),
             ("valves", "leaky / narrow valves", sv("valves_01"), 2, 0), ("muscle", "heart muscle disease", sv("coeur_10"), 0, 1),
             ("diabetes", "diabetes", None, 1, 1), ("alcohol", "heavy alcohol use", None, 2, 1)]
    for w, lab, pic, cx_, cy_ in items:
        tt = s.t(w) - (1.2 if w == "alcohol" else 0)
        x0, y0 = X + 120 + cx_ * 580, 190 + cy_ * 430
        ca += [panel(x0, y0, x0 + 520, y0 + 390, PINK if cy_ == 0 else CREAM, tt - 0.3), text(lab, x0 + 260, y0 + 350, 40, MAROON, tt, "c")]
        if pic is not None:
            ca.append(pop(pic, x0 + 260, y0 + 160, h=260, t=tt - 0.1))
        else:
            ca.append(text("+", x0 + 260, y0 + 170, 160, RED_T if w == "diabetes" else GOLD_T, tt, "c"))
    glows.append((s.t("most"), (X + 380, 330), 3.0, 160))

    # ---------------- EJECTION FRACTION (D)
    s = sc["ef"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, ca)
    h2 = pop(OP.HEART, 430, PH + 580, h=780, t=s.start + 0.3)
    lv = h2.map(OP.P["LV"])
    glows.append((s.t("left"), lv, 3.0, 140))
    ef = [h2, text("left ventricle", 860, PH + 200, 46, RED_T, s.t("left")), lead([(850, PH + 210), (lv[0] + 40, lv[1])], s.t("left") + 0.4, RED_T),
          text("ejection fraction", 1330, PH + 330, 64, PURPLE, s.t("ejection"), "c"),
          text("% pumped out each beat", 1330, PH + 400, 40, MAROON, s.t("beat") - 0.4, "c")]
    tf, t4 = s.t("fifty"), s.t("forty")
    bx0, bx1 = 900, 1780
    ef += [panel(bx0, PH + 500, bx1, PH + 600, (240, 240, 245), tf - 0.6),
           panel(bx0, PH + 500, bx0 + int((bx1 - bx0) * 0.6), PH + 600, (200, 238, 210), tf - 0.2),
           text("healthy: 50-70%", 1340, PH + 665, 50, GREEN_T, tf, "c"),
           panel(bx0, PH + 760, bx1, PH + 860, (240, 240, 245), t4 - 0.6),
           panel(bx0, PH + 760, bx0 + int((bx1 - bx0) * 0.35), PH + 860, (252, 210, 215), t4 - 0.2),
           text("40% or lower = weak pump", 1340, PH + 925, 50, RED_T, t4, "c")]

    # ---------------- LEFT-SIDED (E)
    s = sc["left"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, ef + [h2])
    X = PW
    lu = pop(sv("poumons_01"), X + 500, PH + 560, h=640, t=s.start + 0.3)
    le = [lu, text("left side fails", X + 500, PH + 130, 60, RED_T, s.start + 0.5, "c")]
    tl = s.t("lungs")
    for fx_, fy_ in ((0.28, 0.65), (0.72, 0.65), (0.3, 0.8), (0.7, 0.8)):
        glows.append((tl, F(lu, fx_, fy_), s.end - tl, 70))
    le += [text("blood backs up into the lungs", X + 1380, PH + 240, 46, MAROON, tl, "c"),
           text("fluid in the air sacs", X + 1380, PH + 330, 46, BLUE_T, s.t("leaks"), "c"),
           panel(X + 1000, PH + 410, X + 1780, PH + 550, SKY, s.t("flat") - 0.4), text("hard to breathe lying flat", X + 1390, PH + 495, 46, BLUE_T, s.t("flat") - 0.2, "c"),
           text("waking up gasping", X + 1390, PH + 640, 46, PURPLE, s.t("gasping") - 0.3, "c"),
           pop(pillow_pic(), X + 1250, PH + 830, w=300, t=s.t("pillows") - 0.3), text("extra pillows", X + 1590, PH + 840, 44, MAROON, s.t("pillows"), "c")]

    # ---------------- RIGHT-SIDED (F)
    s = sc["right"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, le)
    X = 2 * PW
    bo = pop(sv("Male-silhouette"), X + 380, PH + 600, h=960, t=s.start + 0.3)
    ri = [bo, text("right side fails", X + 1000, PH + 130, 60, BLUE_T, s.start + 0.5, "c"),
          text("blood backs up into body veins", X + 1000, PH + 210, 42, MAROON, s.t("veins"), "c")]
    tlg = s.t("legs")
    glows += [(tlg, F(bo, 0.42, 0.93), s.end - tlg, 60), (tlg, F(bo, 0.58, 0.93), s.end - tlg, 60), (s.t("belly"), F(bo, 0.5, 0.55), 3.0, 70)]
    ri += [text("swollen legs + ankles", X + 1000, PH + 330, 46, BLUE_T, tlg),
           text("sometimes the belly", X + 1000, PH + 400, 40, MAROON, s.t("belly")),
           pop(leg_pic(), X + 1250, PH + 720, h=480, t=s.t("press") - 0.4),
           text("press -> dent stays", X + 1430, PH + 600, 44, PURPLE, s.t("dent") - 0.4),
           text("= pitting edema", X + 1430, PH + 670, 44, RED_T, s.t("dent") + 0.2)]

    # ---------------- SYMPTOMS (A)
    s = sc["symptoms"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, ri + [hs])
    sy = title("main signs", 960, 90, s.start + 0.3)
    signs = [("shortness", "shortness of breath", BLUE_T), ("tiredness", "tiredness", PURPLE),
             ("swollen", "swollen feet + ankles", RED_T), ("weight", "quick weight gain (fluid)", GOLD_T)]
    for i, (w, lab, col) in enumerate(signs):
        tt = s.t(w)
        sy += [text("- " + lab, 160, 220 + i * 100, 54, col, tt)]
    te = s.t("suddenly")
    sy += [panel(120, 650, 1800, 960, PINK, te - 0.3), text("emergency: sudden severe breathlessness,", 960, 740, 48, RED_T, te, "c"),
           text("chest pain or fainting", 960, 815, 48, RED_T, s.t("chest"), "c"),
           text("-> call your local emergency number", 960, 900, 46, MAROON, s.t("chest") + 1.0, "c"),
           pop(sv("Smartphone-1"), 1600, 360, h=360, t=s.t("call") - 0.3)]

    # ---------------- DIAGNOSE (B)
    s = sc["diagnose"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, sy)
    X = PW
    dg = title("how doctors find it", X + 960, 90, s.start + 0.3)
    tests = [("listen", "listen: heart + lungs", sv("stethoscope"), 0), ("x-ray", "chest x-ray", xray_pic(), 1),
             ("b", "BNP blood test", tube_pic(), 2), ("echocardiogram", "echocardiogram", echo_pic(), 3)]
    for w, lab, pic, i in tests:
        tt = s.t(w) if w != "b" else s.t("blood")
        x = X + 250 + i * 470
        dg += [panel(x - 210, 200, x + 210, 760, [MINT, SKY, PINK, LILAC][i], tt - 0.3), pop(pic, x, 450, h=340, t=tt - 0.1),
               text(lab, x, 700, 38 if i == 0 else 42, MAROON, tt + 0.2, "c")]
    dg += [text("ultrasound: how well it pumps", X + 960, 880, 48, PURPLE, s.t("ultrasound"), "c")]

    # ---------------- TREAT (C)
    s = sc["treat"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, dg)
    X = 2 * PW
    tr = title("controlled, not cured", X + 960, 90, s.t("controlled") - 0.3)
    tips = [("medicines", "medicines help the heart", MINT, GREEN_T, pills_pic()), ("water", "water pills remove fluid", SKY, BLUE_T, None),
            ("salt", "eat less salt", CREAM, GOLD_T, None), ("weigh", "weigh yourself daily", LILAC, PURPLE, scale_pic()),
            ("active", "stay active as advised", MINT, GREEN_T, None), ("cause", "treat the cause", PINK, RED_T, None)]
    for i, (w, lab, col, tc_, pic) in enumerate(tips):
        tt = s.t(w) - (1.3 if w == "cause" else 0)
        x0, y0 = X + 100 + (i % 2) * 880, 190 + (i // 2) * 260
        tr += [panel(x0, y0, x0 + 840, y0 + 210, col, tt - 0.3), text(lab, x0 + (500 if pic else 420), y0 + 120, 44 if pic else 48, tc_, tt, "c")]
        if pic is not None:
            tr.append(pop(pic, x0 + 140, y0 + 105, h=100, t=tt - 0.1))

    # ---------------- SUMMARY (D)
    s = sc["summary"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, tr)
    sm = title("remember 3 things", 960, PH + 110, s.start + 0.5)
    cards = [("weak", "weak or stiff", "not stopped", PINK, RED_T, 400), ("left", "left -> lungs", "right -> legs", SKY, BLUE_T, 960),
             ("treatment", "with treatment", "live well", MINT, GREEN_T, 1520)]
    for w, a, b, col, tc_, x in cards:
        tt = s.t(w) - 0.3
        sm += [panel(x - 260, PH + 260, x + 260, PH + 620, col, tt - 0.2), text(a, x, PH + 400, 52, tc_, tt, "c"), text(b, x, PH + 500, 50, MAROON, tt + 0.6, "c")]
    tn = s.t("next")
    sm += [panel(360, PH + 760, 1560, PH + 920, LILAC, tn), text("next: when the rhythm goes wrong", 960, PH + 860, 50, PURPLE, tn + 0.3, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render(out="heart_failure.mp4"):
    import subprocess
    import render_ecg as RE
    bd, sc = build()
    vid = HERE / "hf_video_only.mp4"
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
            OF.credit(bd.frame(t)).save(HERE / f"hf_{t:06.1f}.png")
        print("ok", round(bd.total, 1), ends)
    else:
        render()
