"""Video 2: Heart Attack, in the approved Osmosis style (see .claude/skills/anatomy-unfolded-style)."""
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
MI = HERE.parent / "mi"
SV = HERE.parent / "servier"
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import render_board as RB  # noqa: E402
import osm_preview as OP  # noqa: E402
import osm_full as OF  # noqa: E402

MAROON, PURPLE, TEAL, BLUE_T, RED_T, GOLD_T, GREEN_T = OF.MAROON, OF.PURPLE, OF.TEAL, OF.BLUE_T, OF.RED_T, OF.GOLD_T, OF.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OF.PINK, OF.LILAC, OF.CREAM, OF.MINT, OF.SKY
DARK_RED = (150, 30, 50)
FPS = 30


def sv(name):
    p = SV / "mi" / f"{name}.png"
    return Image.open(p if p.exists() else SV / f"{name}.png").convert("RGBA")


class Sc(RB.Sc):
    def __init__(self, sid, text, start):
        self.id, self.text, self.start = sid, text, start
        self.audio = MI / "audio" / f"{sid}.wav"
        import render as R
        self.dur = R.dur(self.audio)
        self.words = text.lower().replace(",", "").replace(".", "").replace("?", "").replace(":", "").split()


def build():
    data = json.load(open(MI / "script.json"))
    sc, t0 = {}, 0.0
    for s in data:
        sc[s["id"]] = Sc(s["id"], s["text"], t0)
        t0 += sc[s["id"]].dur
    bd = B.Board(2, 1)
    add, cam = bd.add, bd.camera
    rings, pulses, glows = [], [], []
    pops = []

    def text(s, x, y, size, color, t, anchor="l", dur=None):
        return add(B.Text(s.upper(), x, y, size, color, t=t, dur=dur, anchor=anchor))

    def sub(s_, x, y, size, color, t):
        a = add(B.Stroke([(x - 2, y - 40), (x - 2, y - 10), (x + 18, y - 10)], color, 3, t=t, dur=0.25))
        return [a, text(s_, x + 26, y, size, color, t + 0.2)]

    def lead(pts, t, color=MAROON, width=3, dur=0.45, arrow=False):
        return add(B.Stroke(B.smooth(pts, 10), color, width, t=t, dur=dur, arrow=arrow))

    def pop(img, x, y, h=None, w=None, t=0.0, dur=0.6):
        pops.append(t)
        return add(B.Pop(img, x, y, h=h, w=w, t=t, dur=dur))

    def panel(x0, y0, x1, y1, col, t):
        return add(B.Panel(x0, y0, x1, y1, col, t=t))

    def cross(x0, y0, x1, y1, t, w=10):
        return [add(B.Stroke([(x0, y0), (x1, y1)], RED_T, w, t=t, dur=0.25)),
                add(B.Stroke([(x1, y0), (x0, y1)], RED_T, w, t=t + 0.2, dur=0.25))]

    def F(pic, fx, fy):
        return pic.map((fx * pic.src.width, fy * pic.src.height))

    cam(0, 960, 540, 1.0, 0.1)

    # ======================= HOOK
    s = sc["hook"]
    hk = [text("heart attack", 960, 100, 72, MAROON, 0.3, "c"), add(B.Stroke([(720, 140), (1200, 137)], MAROON, 4, t=1.3, dur=0.4)),
          text("what happens inside", 960, 190, 38, PURPLE, 1.6, "c")]
    te = s.t("electricity")
    hk += [panel(1180, 300, 1800, 440, LILAC, te - 0.3), pop(OF.bolt(), 1250, 370, h=110, t=te),
           text("last video:", 1310, 350, 34, PURPLE, te + 0.2), text("electrical system", 1310, 405, 44, PURPLE, te + 0.6)]
    heart = pop(sv("coeur_09"), 640, 600, h=720, t=s.t("muscle") - 0.4)
    tb = s.t("blood")
    hk += [panel(1180, 490, 1800, 640, PINK, tb - 0.2), text("heart muscle needs", 1220, 550, 42, MAROON, tb),
           text("a constant blood supply", 1220, 610, 42, RED_T, tb + 0.8)]
    tcu = s.t("cut")
    hk += [text("what if it's cut off?", 1220, 680, 44, PURPLE, tcu)]
    ta = s.t("attack")
    hk += [panel(1180, 730, 1800, 890, PINK, ta - 0.3), text("= heart attack", 1220, 795, 56, RED_T, ta),
           text("(myocardial infarction)", 1220, 860, 34, MAROON, ta + 0.8)]

    # ======================= CORONARY ARTERIES
    s = sc["coronary"]
    bd.erase(s.start, hk)
    rca, lad, lcx = F(heart, 0.33, 0.78), F(heart, 0.62, 0.64), F(heart, 0.74, 0.52)
    co = [text("coronary arteries", 1180, 330, 56, RED_T, s.t("coronary")),
          lead([(1175, 320), (1000, 360), (lcx[0] + 6, lcx[1])], s.t("coronary") + 0.6, RED_T),
          lead([(1175, 325), (900, 470), (lad[0] + 6, lad[1])], s.t("coronary") + 0.8, RED_T),
          lead([(1175, 330), (700, 300), (rca[0] + 4, rca[1] - 20)], s.t("coronary") + 1.0, RED_T)]
    glows += [(s.t("coronary") + 0.5, lad, 2.5, 60), (s.t("coronary") + 0.5, rca, 2.5, 50), (s.t("coronary") + 0.5, lcx, 2.5, 45)]
    tcr = s.t("crown")
    co += [panel(1180, 420, 1800, 560, CREAM, tcr - 0.3), text("corona = crown", 1220, 480, 46, GOLD_T, tcr),
           text("wrap around the heart", 1220, 535, 34, MAROON, tcr + 0.6)]
    tox = s.t("oxygen")
    co += [panel(1180, 610, 1800, 760, PINK, tox - 0.3), text("carry oxygen", 1220, 670, 46, RED_T, tox)]
    co += sub("to the heart muscle", 1220, 735, 36, MAROON, tox + 0.7)

    # ======================= PLAQUE
    s = sc["plaque"]
    bd.erase(s.start, co + [heart])
    h1 = pop(sv("Artere_coupe_sang"), 470, 560, h=640, t=s.start + 0.3)
    pl = [h1, text("healthy artery", 470, 950, 46, GREEN_T, s.start + 0.8, "c")]
    tpl = s.t("plaque")
    a2 = pop(sv("Artere_simple_ouverte"), 1150, 560, h=640, t=tpl - 0.5)
    pq = F(a2, 0.77, 0.6)
    pl += [a2, text("plaque", 1500, 330, 56, GOLD_T, tpl), lead([(1495, 325), (1400, 420), (pq[0] + 4, pq[1])], tpl + 0.5, GOLD_T),
           text("fatty deposits", 1500, 390, 34, MAROON, tpl + 0.9)]
    tcad = s.t("disease")
    pl += [panel(940, 880, 1880, 1010, CREAM, tcad - 1.0), text("coronary artery disease", 1410, 960, 50, MAROON, tcad - 0.8, "c")]
    tn = s.t("narrows")
    inset = pop(OF.circle_inset(sv("atherome_D"), 380, GOLD_T), 1640, 620, h=380, t=tn)
    pl += [inset, lead([(pq[0], pq[1]), (1430, 620)], tn - 0.2, GOLD_T, 3, 0.3)]
    tls = s.t("less")
    pl += [text("narrower = less blood", 1640, 840, 38, RED_T, tls, "c")]

    # ======================= CLOT
    s = sc["clot"]
    bd.erase(s.start, pl)
    at = pop(sv("atherome"), 560, 560, h=780, t=s.start + 0.2)
    rup = F(at, 0.57, 0.62)
    cl = [at, text("plaque breaks open", 980, 300, 48, MAROON, s.t("breaks")),
          lead([(975, 295), (800, 380), (rup[0] + 10, rup[1] - 10)], s.t("breaks") + 0.6)]
    tcl = s.t("clot")
    th = pop(sv("thrombus"), 1420, 620, w=760, t=tcl - 0.3)
    clp = F(th, 0.55, 0.5)
    cl += [th, text("blood clot", 1420, 430, 56, DARK_RED, tcl, "c"), lead([(1420, 450), (clp[0], clp[1] - 40)], tcl + 0.5, DARK_RED)]
    tco = s.t("completely")
    cl += [panel(1060, 820, 1780, 960, PINK, tco - 0.3), text("artery blocked!", 1420, 905, 56, RED_T, tco, "c")]

    # ======================= DAMAGE
    s = sc["damage"]
    bd.erase(s.start, cl)
    inf = pop(sv("Infarctus2"), 560, 560, h=860, t=s.start + 0.3)
    clot2, dead = F(inf, 0.74, 0.38), F(inf, 0.84, 0.16)
    dm = [inf, text("clot", 960, 470, 44, DARK_RED, s.start + 1.0), lead([(955, 465), (clot2[0] + 20, clot2[1])], s.start + 1.4, DARK_RED)]
    tox = s.t("oxygen")
    dm += [text("no oxygen", 960, 180, 52, PURPLE, tox), lead([(955, 175), (dead[0] + 30, dead[1])], tox + 0.5, PURPLE)]
    tmi = s.t("minutes")
    dm += [panel(1180, 300, 1840, 440, LILAC, tmi - 0.3), text("damage within minutes", 1220, 380, 44, PURPLE, tmi)]
    tdi = s.t("die")
    dm += [panel(1180, 490, 1840, 630, LILAC, tdi - 0.6), text("muscle begins to die", 1220, 570, 44, PURPLE, tdi - 0.4)]
    ttm = s.t("time")
    dm += [panel(1180, 700, 1840, 880, PINK, ttm - 0.3), text("time is muscle!", 1510, 815, 72, RED_T, ttm, "c")]
    glows.append((tox + 0.2, dead, 3.0, 90))

    # ======================= SYMPTOMS
    s = sc["symptoms"]
    bd.erase(s.start, dm)
    man = pop(sv("Systeme_homme"), 430, 560, h=1000, t=s.start + 0.2)
    chest = F(man, 0.57, 0.25)
    arm, neck, jaw = F(man, 0.82, 0.42), F(man, 0.52, 0.15), F(man, 0.55, 0.11)
    tch = s.t("chest", 1)
    sy = [man, panel(860, 220, 1500, 360, PINK, tch - 0.4), text("chest pain / pressure", 900, 285, 46, RED_T, tch),
          text("center or left side", 900, 340, 34, MAROON, s.t("center")), lead([(855, 280), (chest[0] + 25, chest[1])], tch + 0.6, RED_T)]
    tsp = s.t("spread")
    for k, (p, nm, w) in enumerate(((arm, "arm", "arm"), (neck, "neck", "neck"), (jaw, "jaw", "jaw"))):
        tt = s.t(w)
        sy += [lead([chest, p], tt - 0.3, RED_T, 4, 0.4, arrow=True)]
        glows.append((tt, p, 3.5, 45))
    sy += [text("arm, back, neck, jaw", 900, 430, 40, MAROON, tsp)]
    glows += [(tch, chest, 6.0, 70)]
    tob = s.t("shortness")
    others = [("shortness of breath", tob), ("cold sweat", s.t("sweat")), ("nausea", s.t("nausea")), ("lightheaded", s.t("lightheaded"))]
    sy += [panel(860, 480, 1500, 760, SKY, tob - 0.3)]
    for i, (nm, tt) in enumerate(others):
        sy += sub(nm, 900, 550 + i * 60, 38, BLUE_T, tt - 0.2)
    tw = s.t("women")
    sy += [panel(860, 810, 1840, 1000, LILAC, tw - 0.3), text("women, older adults, diabetes:", 900, 870, 40, PURPLE, tw),
           text("may have little or no chest pain", 900, 940, 42, PURPLE, s.t("little"))]

    # ======================= ACT FAST
    s = sc["act"]
    bd.erase(s.start, sy)
    ph = pop(sv("Smartphone-1"), 480, 560, h=700, t=s.start + 0.2)
    tca = s.t("call")
    ac = [ph, panel(860, 260, 1840, 460, PINK, tca - 0.3), text("call your local", 900, 330, 50, RED_T, tca),
          text("emergency number!", 900, 410, 64, RED_T, tca + 0.6)]
    rings += [(tca + k * 0.6, F(ph, 0.5, 0.45), 0.6) for k in range(5)]
    tw_ = s.t("wait")
    ac += [panel(860, 520, 1840, 640, CREAM, tw_ - 0.3), text("don't wait for it to go away", 920, 595, 42, MAROON, tw_)]
    ac += cross(880, 545, 905, 615, tw_ + 0.2, 6)
    tdr = s.t("drive")
    ac += [panel(860, 690, 1840, 810, CREAM, tdr - 0.3), text("don't drive yourself", 920, 765, 42, MAROON, tdr)]
    ac += cross(880, 715, 905, 785, tdr + 0.2, 6)

    # ======================= TREATMENT
    s = sc["treatment"]
    bd.erase(s.start, ac)
    tt0 = s.t("open", 1)
    tr = [text("open the artery fast", 960, 120, 60, MAROON, tt0, "c"), add(B.Stroke([(680, 160), (1240, 157)], MAROON, 4, t=tt0 + 1.0, dur=0.4))]
    tmd = s.t("medicines")
    th2 = pop(sv("thrombus"), 470, 360, w=640, t=tmd - 0.4)
    tr += [th2, panel(830, 270, 1820, 410, CREAM, tmd - 0.2), text("medicines that dissolve the clot", 870, 350, 42, GOLD_T, tmd)]
    tan = s.t("angioplasty")
    va = pop(sv("vaisseau_12"), 820, 720, w=1300, t=tan - 0.3)
    bal, stn = F(va, 0.28, 0.38), F(va, 0.8, 0.58)
    tr += [va, text("angioplasty", 1560, 470, 50, MAROON, tan)]
    tbl = s.t("balloon")
    tr += [text("balloon", 300, 520, 46, BLUE_T, tbl), lead([(420, 530), (bal[0], bal[1] - 20)], tbl + 0.5, BLUE_T)]
    tst = s.t("stent")
    tr += [text("stent", 1600, 960, 50, TEAL, tst), lead([(1595, 950), (stn[0] + 30, stn[1] + 30)], tst + 0.5, TEAL),
           text("keeps it open", 1600, 1020, 34, MAROON, tst + 0.9)]

    # ======================= HEART ATTACK vs CARDIAC ARREST (slide to page 2)
    s = sc["arrest"]
    X = 1920
    cam(s.start, X + 960, 540, 1.0, 1.1)
    bd.erase(s.start + 1.2, tr)
    tha = s.t("circulation")
    ar = [text("not the same!", X + 960, 110, 64, MAROON, s.start + 0.6, "c"),
          panel(X + 80, 200, X + 920, 900, PINK, s.t("attack", 1) - 0.3), text("heart attack", X + 500, 280, 58, RED_T, s.t("attack", 1), "c"),
          text("circulation problem", X + 500, 360, 42, MAROON, tha, "c"), pop(sv("thrombus"), X + 500, 560, w=640, t=tha + 0.3),
          text("blood can't reach the heart", X + 500, 760, 36, MAROON, s.t("reach"), "c"),
          text("heart usually keeps beating", X + 500, 830, 36, GREEN_T, s.t("beating"), "c")]
    tel = s.t("electrical")
    ar += [panel(X + 1000, 200, X + 1840, 900, LILAC, s.t("arrest", 2) - 0.3),
           text("cardiac arrest", X + 1420, 280, 58, PURPLE, s.t("arrest", 2), "c"),
           text("electrical problem", X + 1420, 360, 42, MAROON, tel, "c"), pop(OF.bolt(), X + 1420, 560, h=240, t=tel + 0.3)]
    ar += cross(X + 1300, 440, X + 1540, 680, tel + 0.8, 12)
    tsto = s.t("stops")
    ar += [text("heart stops pumping", X + 1420, 800, 38, RED_T, tsto, "c")]
    tld = s.t("lead")
    ar += [lead([(X + 860, 960), (X + 1060, 960)], tld, MAROON, 5, 0.5, arrow=True),
           text("can sometimes lead to", X + 960, 1030, 36, MAROON, tld + 0.3, "c")]

    # ======================= RISK FACTORS + SUMMARY
    s = sc["summary"]
    bd.erase(s.start, ar)
    rk = [text("risk factors", X + 960, 110, 64, MAROON, s.start + 0.4, "c"),
          add(B.Stroke([(X + 720, 150), (X + 1200, 147)], MAROON, 4, t=s.start + 1.2, dur=0.4))]
    items = [("blood", 2, "high blood pressure"), ("cholesterol", 1, "high cholesterol"), ("smoking", 1, "smoking"),
             ("diabetes", 1, "diabetes"), ("overweight", 1, "being overweight"), ("active", 1, "not being active")]
    for i, (w, n, nm) in enumerate(items):
        tt = s.t(w, n) if w != "blood" else s.t("pressure") - 0.3
        x0 = X + 160 + (i % 3) * 560
        y0 = 230 + (i // 3) * 190
        rk += [panel(x0, y0, x0 + 500, y0 + 140, CREAM if i % 2 else PINK, tt - 0.2), text(nm, x0 + 250, y0 + 85, 42, MAROON, tt, "c")]
    rk.append(pop(sv("cigarettes_01"), X + 1500, 340, h=120, t=s.t("smoking")))
    tsum = s.t("sum")
    bd.erase(tsum, rk)
    steps = [("plaque", 1, "plaque builds up", "Artere_simple_ouverte"), ("clot", 1, "clot blocks artery", "thrombus"),
             ("muscle", 1, "muscle starts to die", "Infarctus2")]
    sm = [text("summary", X + 960, 110, 64, MAROON, tsum + 0.2, "c")]
    for i, (w, n, nm, img) in enumerate(steps):
        tt = s.t(w, n) - 0.3
        x = X + 330 + i * 630
        sm += [pop(sv(img), x, 430, h=380 if img != "thrombus" else None, w=520 if img == "thrombus" else None, t=tt),
               text(nm, x, 700, 44, RED_T if i else GOLD_T, tt + 0.3, "c")]
        if i:
            sm.append(lead([(x - 420, 430), (x - 230, 430)], tt - 0.2, MAROON, 5, 0.3, arrow=True))
    tf = s.t("fast")
    sm += [panel(X + 360, 780, X + 1560, 900, PINK, tf - 0.3), text("act fast: time is muscle", X + 960, 860, 56, RED_T, tf, "c")]
    tn = s.t("next")
    sm += [text("next video: blood vessels", X + 960, 1000, 44, PURPLE, tn + 0.4, "c"),
           pop(sv("Artere_coupe_sang"), X + 1700, 960, h=170, t=tn + 0.2)]

    bd.fx.append(lambda crop, ctx, t: OP.fx(crop, ctx, t, rings, pulses, glows))
    bd.total = t0
    bd.pops = pops
    return bd, sc


def pop_sfx(path_in, path_out, times, offset):
    with wave.open(str(path_in)) as w:
        sr, n = w.getframerate(), w.getnframes()
        a = np.frombuffer(w.readframes(n), "<i2").astype(np.float32) / 32767
    t = np.arange(int(0.07 * sr)) / sr
    blip = 0.07 * np.sin(2 * np.pi * (520 - 2200 * t) * t) * np.exp(-t * 55)
    for tt in times:
        i = int((tt + offset) * sr)
        if 0 <= i < len(a) - len(blip):
            a[i:i + len(blip)] += blip
    with wave.open(str(path_out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype("<i2").tobytes())


def render(out="heart_attack.mp4"):
    import render_ecg as RE
    bd, sc = build()
    vid = HERE / "mi_video_only.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", str(vid)], stdin=subprocess.PIPE)
    for f in range(int(round(RE.INTRO_DUR * FPS))):
        ff.stdin.write(RE.intro_frame(f / FPS).tobytes())
    for f in range(int(bd.total * FPS)):
        ff.stdin.write(OF.credit(bd.frame(f / FPS)).tobytes())
        if f % 900 == 0:
            print(f"  t={f / FPS:.0f}s", flush=True)
    ff.stdin.close()
    ff.wait()
    RE.intro_audio(HERE / "audio_intro.wav")
    with open(HERE / "mi_audio.txt", "w") as fh:
        fh.write(f"file '{HERE / 'audio_intro.wav'}'\n")
        for s in sc.values():
            fh.write(f"file '{s.audio}'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(HERE / "mi_audio.txt"),
                    "-c", "pcm_s16le", str(HERE / "mi_voice_raw.wav")], check=True)
    pop_sfx(HERE / "mi_voice_raw.wav", HERE / "mi_voice.wav", bd.pops, RE.INTRO_DUR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(HERE / "mi_voice.wav"), "-c:v", "libx264",
                    "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                    str(HERE / out)], check=True)
    print("done ->", HERE / out)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        bd, _ = build()
        for t in sorted(float(x) for x in sys.argv[2:]):
            OF.credit(bd.frame(t)).save(HERE / f"m_{t:06.1f}.png")
        print("ok", round(bd.total, 1))
    else:
        render()
