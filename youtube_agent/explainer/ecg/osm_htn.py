"""Cardiovascular series: High Blood Pressure / Hypertension (owner-approved blueprint, narration only)."""
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "htn")))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_preview as OP  # noqa: E402
import osm_full as OF  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_hphys as HP  # noqa: E402
import osm_bv as BV  # noqa: E402
import osm_bp as BPm  # noqa: E402

MAROON, PURPLE, BLUE_T, RED_T, GOLD_T, GREEN_T = OF.MAROON, OF.PURPLE, OP.BLUE_T, OP.RED_T, OP.GOLD_T, OF.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OF.PINK, OF.LILAC, OF.CREAM, OF.MINT, OF.SKY
PW, PH = 1920, 1080
sv = BPm.sv


def eye_pic():
    S = 3
    im = Image.new("RGBA", (420 * S, 240 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((10 * S, 20 * S, 410 * S, 220 * S), fill=(252, 248, 245), outline=(70, 60, 70), width=6 * S)
    d.ellipse((140 * S, 50 * S, 280 * S, 190 * S), fill=(90, 150, 200), outline=(50, 80, 120), width=4 * S)
    d.ellipse((180 * S, 90 * S, 240 * S, 150 * S), fill=(30, 30, 40))
    d.ellipse((195 * S, 100 * S, 212 * S, 117 * S), fill=(255, 255, 255))
    for pts in (((30, 120), (70, 100), (110, 110)), ((40, 160), (80, 150), (120, 165)), ((390, 110), (350, 95), (300, 105)),
                ((385, 150), (345, 160), (300, 150))):
        d.line([(x * S, y * S) for x, y in pts], fill=(220, 60, 70), width=3 * S, joint="curve")
    return im.resize((420, 240), Image.LANCZOS)


def salt_pic():
    S = 3
    im = Image.new("RGBA", (200 * S, 300 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40 * S, 90 * S, 160 * S, 290 * S), radius=20 * S, fill=(235, 240, 248), outline=(80, 85, 100), width=5 * S)
    d.pieslice((40 * S, 20 * S, 160 * S, 160 * S), 180, 360, fill=(180, 185, 195), outline=(80, 85, 100), width=5 * S)
    for x, y in ((80, 60), (100, 50), (120, 60), (90, 75), (110, 75)):
        d.ellipse(((x - 5) * S, (y - 5) * S, (x + 5) * S, (y + 5) * S), fill=(60, 60, 70))
    return im.resize((200, 300), Image.LANCZOS)


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

    def body(t, extra_t=None):
        """silhouette with heart, brain and kidney drawn in place; returns items + anchor points"""
        bo = pop(sv("Male-silhouette"), 470, 600, h=960, t=t)
        return bo, {"heart": F(bo, 0.53, 0.30), "brain": F(bo, 0.46, 0.06), "kidney": F(bo, 0.42, 0.42), "eye": F(bo, 0.52, 0.085)}

    # ---------------- HOOK (page A)
    s = sc["hook"]
    bo, P = body(0.3)
    hk = [bo, text("the silent killer", 1350, 140, 70, RED_T, s.t("silent"), "c"),
          text("most people feel fine", 1350, 230, 44, MAROON, s.t("fine"), "c")]
    for key, pic, x, y, h, word in (("heart", sv("coeur_10"), 1100, 470, 300, "heart"), ("brain", sv("Cerveau_beau"), 1400, 470, 260, "brain"),
                                    ("kidney", sv("Rein_beau"), 1680, 470, 280, "kidneys")):
        tt = s.t(word)
        hk += [pop(pic, x, y, h=h, t=tt - 0.2), text(key if key != "kidney" else "kidneys", x, y + 190, 44, RED_T, tt + 0.2, "c")]
        glows.append((tt, P[key], 1.5, 45))
    hk += [panel(1000, 820, 1820, 960, LILAC, s.t("stay") - 0.4), text("how? stay with me", 1410, 905, 50, PURPLE, s.t("stay") - 0.2, "c")]

    # ---------------- DEFINE (page B)
    s = sc["define"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, hk)
    X = PW
    df = [pop(sv("cuff_gauge"), X + 470, 560, h=620, t=s.start + 0.4)]
    tn = s.t("thirty")
    df += [text("130 / 80", X + 1350, 330, 150, RED_T, tn, "c"), text("or higher", X + 1350, 460, 60, MAROON, s.t("higher"), "c"),
           text("= hypertension", X + 1350, 560, 66, PURPLE, s.t("hypertension"), "c")]
    te = s.t("either")
    df += [panel(X + 960, 700, X + 1760, 860, CREAM, te - 0.3), text("either number", X + 1360, 760, 48, GOLD_T, te, "c"),
           text("can be too high", X + 1360, 825, 44, MAROON, te + 0.6, "c")]

    # ---------------- WHY (page C)
    s = sc["why"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, df)
    X = 2 * PW
    wy = title("why does it happen?", X + 960, 90, s.start + 0.3)
    risks = [("age", "age", None), ("family", "family history", None), ("salt", "too much salt", salt_pic()), ("weight", "extra weight", None),
             ("moving", "not moving", None), ("alcohol", "alcohol", None), ("smoking", "smoking", sv("cigarettes_01"))]
    for i, (w, lab, pic) in enumerate(risks):
        tt = s.t(w)
        cx_, cy_ = X + 180 + (i % 4) * 430, 230 + (i // 4) * 150
        wy += [panel(cx_ - 20, cy_ - 50, cx_ + 380, cy_ + 60, PINK if i % 2 else CREAM, tt - 0.25), text(lab, cx_ + 180, cy_ + 20, 44, MAROON, tt, "c")]
    wy.append(pop(sv("Horloge"), X + 1610, 380, h=150, t=s.t("years") - 0.2))
    tp = s.t("primary")
    wy += [panel(X + 100, 600, X + 900, 960, MINT, tp - 0.3), text("primary", X + 500, 680, 64, GREEN_T, tp, "c"),
           text("most adults", X + 500, 770, 44, MAROON, tp + 0.5, "c"), text("no single cause", X + 500, 840, 44, MAROON, tp + 0.9, "c"),
           text("builds over years", X + 500, 910, 40, MAROON, tp + 1.3, "c")]
    ts = s.t("secondary")
    wy += [panel(X + 1000, 600, X + 1820, 960, SKY, s.t("another") - 0.3), text("secondary", X + 1300, 680, 64, BLUE_T, ts, "c"),
           text("another problem", X + 1300, 770, 44, MAROON, s.t("another"), "c"), text("e.g. kidney disease", X + 1300, 840, 40, MAROON, s.t("kidney"), "c"),
           pop(sv("Rein_beau"), X + 1700, 790, h=270, t=s.t("kidney") - 0.1)]

    # ---------------- ARTERIES (page D)
    s = sc["arteries"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, wy)
    art = pop(sv("Artere_coupe_sang"), 380, PH + 560, h=760, t=s.start + 0.3)
    ctr = F(art, 0.62, 0.55)
    ar = [art, text("inside an artery", 380, PH + 110, 52, MAROON, s.start + 0.6, "c")]
    tpu = s.t("pushes")
    for k, ang in enumerate((-60, 0, 60, 180)):
        a = math.radians(ang)
        ar.append(lead([(ctr[0] + 30 * math.cos(a), ctr[1] + 60 * math.sin(a)), (ctr[0] + 140 * math.cos(a), ctr[1] + 160 * math.sin(a))],
                       tpu + k * 0.15, RED_T, 6, 0.3, arrow=True))
    ar += [text("constant strain", 380, PH + 1010, 44, RED_T, s.t("strain"), "c")]
    tst = s.t("stiff")
    ar += [pop(BV.ring(140, 105, (240, 170, 160, 255), (255, 30, 39, 255), RED_T), 960, PH + 380, h=290, t=tst - 0.6),
           text("normal", 960, PH + 570, 44, GREEN_T, tst - 0.4, "c"),
           pop(BV.ring(140, 55, (225, 150, 140, 255), (255, 30, 39, 255), MAROON), 1500, PH + 380, h=290, t=tst),
           text("stiff + thick wall", 1500, PH + 570, 44, RED_T, s.t("thick"), "c"),
           text("narrower inside", 1500, PH + 630, 40, MAROON, s.t("narrower"), "c")]
    tpl = s.t("plaque")
    ar += [pop(sv("atherome_C"), 1230, PH + 860, h=230, t=s.t("tears") - 0.2), text("tiny tears", 870, PH + 800, 40, MAROON, s.t("tears")),
           text("-> plaque builds up", 1470, PH + 1020, 40, GOLD_T, tpl, "c")]

    # ---------------- HEART (page E)
    s = sc["heart"]
    cam(s.start, *E, 1.0, 1.0)
    bd.erase(s.start + 0.8, ar)
    X = PW
    hs = pop(OP.HEART, X + 520, PH + 590, h=880, t=s.start + 0.3)
    lv = hs.map(OP.P["LV"])
    glows.append((s.t("left"), lv, 4.0, 150))
    he = [hs, text("hard work every beat", X + 1350, PH + 130, 50, MAROON, s.t("hard"), "c")]
    tl = s.t("left")
    he += [text("left ventricle", X + 1010, PH + 260, 46, RED_T, tl), lead([(X + 1000, PH + 270), (lv[0] + 40, lv[1])], tl + 0.4, RED_T)]
    tth = s.t("thicker")
    he += [pop(BV.ring(140, 105, (235, 120, 130, 255), (255, 250, 250, 255), RED_T), X + 1180, PH + 500, h=250, t=tth - 0.5),
           text("normal wall", X + 1180, PH + 670, 40, GREEN_T, tth - 0.3, "c"),
           pop(BV.ring(140, 60, (215, 90, 105, 255), (255, 250, 250, 255), MAROON), X + 1610, PH + 500, h=250, t=tth),
           text("thick wall", X + 1610, PH + 670, 44, RED_T, tth + 0.2, "c"), text("like a gym muscle", X + 1400, PH + 750, 38, PURPLE, s.t("gym"), "c")]
    tf = s.t("stiff") + 1.0
    he += [panel(X + 1000, PH + 820, X + 1820, PH + 960, PINK, s.t("stiff") - 0.3), text("too thick -> stiff", X + 1410, PH + 875, 44, RED_T, s.t("stiff"), "c"),
           text("-> heart can fail", X + 1410, PH + 935, 44, MAROON, tf, "c")]

    # ---------------- SILENT (page F)
    s = sc["silent"]
    cam(s.start, *Fp, 1.0, 1.0)
    bd.erase(s.start + 0.8, he)
    X = 2 * PW
    si = title("why the silent killer?", X + 960, PH + 100, s.start + 0.3)
    si += [panel(X + 140, PH + 230, X + 900, PH + 560, LILAC, s.t("quietly") - 0.3), text("damage happens", X + 520, PH + 330, 50, PURPLE, s.t("quietly"), "c"),
           text("quietly", X + 520, PH + 410, 70, PURPLE, s.t("quietly") + 0.3, "c"),
           text("no symptoms for years", X + 520, PH + 500, 40, MAROON, s.t("symptoms"), "c"),
           pop(sv("Horloge"), X + 1450, PH + 400, h=300, t=s.t("years") - 0.2)]
    tm = s.t("measure")
    si += [pop(sv("cuff_gauge"), X + 600, PH + 800, h=340, t=tm - 0.4),
           panel(X + 960, PH + 700, X + 1800, PH + 900, MINT, tm - 0.2), text("only way to know:", X + 1380, PH + 770, 44, MAROON, s.t("only"), "c"),
           text("measure it", X + 1380, PH + 855, 60, GREEN_T, tm, "c")]

    # ---------------- DAMAGE (page A again)
    s = sc["damage"]
    cam(s.start, *A, 1.0, 1.0)
    bd.erase(s.start + 0.8, si)
    bo2, P2 = body(s.start + 0.6)
    dm = [bo2, text("left untreated...", 1300, 110, 56, MAROON, s.start + 0.6, "c")]
    items = [("stroke", "stroke (brain)", "brain", (900, 240), PURPLE), ("tiny", "eye vessels", "eye", (900, 380), GOLD_T),
             ("attack", "heart attack", "heart", (900, 520), RED_T), ("failure", "heart failure", "heart", (900, 640), RED_T),
             ("kidney", "kidney damage", "kidney", (900, 800), BLUE_T)]
    for w, lab, organ, (x, y), col in items:
        tt = s.t(w)
        dm += [text(lab, x, y, 50, col, tt), lead([(x - 15, y), (P2[organ][0] + 25, P2[organ][1])], tt + 0.3, col, 5)]
        glows.append((tt, P2[organ], 2.0, 50))
    dm += [pop(sv("Cerveau_beau"), 1600, 260, h=200, t=s.t("stroke") + 0.2), pop(eye_pic(), 1600, 450, w=260, t=s.t("tiny") + 0.2),
           pop(sv("coeur_10"), 1600, 650, h=200, t=s.t("attack") + 0.2), pop(sv("Rein_beau"), 1600, 870, h=200, t=s.t("kidney") + 0.2)]

    # ---------------- CRISIS (page B)
    s = sc["crisis"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.8, dm + [bo2])
    X = PW
    tv = s.t("eighty")
    cr = [panel(X + 160, 120, X + 1760, 330, PINK, tv - 0.4), text("above 180 / 120", X + 960, 210, 96, RED_T, tv, "c"),
          text("emergency warning sign", X + 960, 295, 46, MAROON, s.t("emergency"), "c")]
    sym = [("chest", "chest pain"), ("severe", "severe headache"), ("confusion", "confusion"), ("trouble", "trouble seeing")]
    for i, (w, lab) in enumerate(sym):
        tt = s.t(w)
        cr += [text("- " + lab, X + 220, 450 + i * 110, 52, PURPLE, tt)]
    tc = s.t("call")
    cr += [pop(sv("Smartphone-1"), X + 1250, 680, h=420, t=tc - 0.3), panel(X + 1420, 560, X + 1840, 800, CREAM, tc),
           text("call your", X + 1630, 640, 44, MAROON, tc + 0.2, "c"), text("emergency", X + 1630, 700, 44, RED_T, tc + 0.4, "c"),
           text("number now", X + 1630, 760, 44, MAROON, tc + 0.6, "c")]

    # ---------------- CONTROL (page C)
    s = sc["control"]
    cam(s.start, *C, 1.0, 1.0)
    bd.erase(s.start + 0.8, cr)
    X = 2 * PW
    co = title("it can be controlled", X + 960, 90, s.t("controlled") - 0.3)
    tips = [("less", "less salt", CREAM, GOLD_T), ("fruits", "more fruit + veg", MINT, GREEN_T), ("move", "move 150 min / week", SKY, BLUE_T),
            ("healthy", "healthy weight", MINT, GREEN_T), ("limit", "limit alcohol", CREAM, GOLD_T), ("smoke", "don't smoke", PINK, RED_T)]
    for i, (w, lab, col, tc_) in enumerate(tips):
        tt = s.t(w)
        x0, y0 = X + 120 + (i % 2) * 860, 200 + (i // 2) * 170
        co += [panel(x0, y0, x0 + 800, y0 + 130, col, tt - 0.3), text(lab, x0 + 400, y0 + 80, 52, tc_, tt, "c")]
    tmed = s.t("medicines")
    co += [panel(X + 300, 740, X + 1620, 960, LILAC, tmed - 0.3), text("+ medicines when needed", X + 960, 820, 54, PURPLE, tmed, "c"),
           text("relax vessels / remove extra fluid", X + 960, 900, 40, MAROON, s.t("relax"), "c")]

    # ---------------- SUMMARY (page D)
    s = sc["summary"]
    cam(s.start, *D, 1.0, 1.0)
    bd.erase(s.start + 0.8, co)
    sm = title("remember 3 things", 960, PH + 110, s.start + 0.5)
    cards = [("thirty", "130/80+", "= high", PINK, RED_T, 400), ("silent", "it's silent", "so check it", LILAC, PURPLE, 960),
             ("controlled", "it can be", "controlled", MINT, GREEN_T, 1520)]
    for w, a, b, col, tc_, x in cards:
        tt = s.t(w) - 0.3
        sm += [panel(x - 260, PH + 260, x + 260, PH + 620, col, tt - 0.2), text(a, x, PH + 400, 60, tc_, tt, "c"), text(b, x, PH + 500, 46, MAROON, tt + 0.5, "c")]
    tn = s.t("next")
    sm += [panel(460, PH + 760, 1460, PH + 920, SKY, tn), text("next: heart failure", 960, PH + 860, 54, BLUE_T, tn + 0.3, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render(out="high_blood_pressure.mp4"):
    import subprocess
    import render_ecg as RE
    bd, sc = build()
    vid = HERE / "htn_video_only.mp4"
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
        for t in sorted(float(x) for x in sys.argv[2:]):
            OF.credit(bd.frame(t)).save(HERE / f"htn_{t:06.1f}.png")
        print("ok", round(bd.total, 1), {k: round(v.start + v.dur, 1) for k, v in sc.items()})
    else:
        render()
