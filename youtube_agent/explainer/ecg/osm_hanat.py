"""Cardiovascular series ep.1: Anatomy of the Heart (Osmosis style)."""
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
EP = HERE.parent / "hanat"
SV = HERE.parent / "servier"
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_preview as OP  # noqa: E402
import osm_full as OF  # noqa: E402
import osm_mi as OM  # noqa: E402

MAROON, PURPLE, TEAL, BLUE_T, RED_T, GOLD_T, GREEN_T = OF.MAROON, OF.PURPLE, OF.TEAL, OF.BLUE_T, OF.RED_T, OF.GOLD_T, OF.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OF.PINK, OF.LILAC, OF.CREAM, OF.MINT, OF.SKY


def sv(name):
    for sub in ("ha", "mi", ""):
        p = SV / sub / f"{name}.png"
        if p.exists():
            return Image.open(p).convert("RGBA")
    raise FileNotFoundError(name)


class Sc(OM.Sc):
    def __init__(self, sid, text, start):
        import render as R
        self.id, self.text, self.start = sid, text, start
        self.audio = EP / "audio" / f"{sid}.wav"
        self.dur = R.dur(self.audio)
        self.words = text.lower().replace(",", "").replace(".", "").replace("?", "").replace(":", "").replace(";", "").split()


def kit(bd, pops):
    add = bd.add

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

    def title(s, x, y, t, size=64, color=MAROON):
        w = len(s) * size * 0.42
        return [text(s, x, y, size, color, t, "c"), add(B.Stroke([(x - w / 2, y + 40), (x + w / 2, y + 37)], color, 4, t=t + 0.9, dur=0.4))]
    return text, sub, lead, pop, panel, title


def build():
    data = json.load(open(EP / "script.json"))
    sc, t0 = {}, 0.0
    for s in data:
        sc[s["id"]] = Sc(s["id"], s["text"], t0)
        t0 += sc[s["id"]].dur
    bd = B.Board(1, 1)
    pops, rings, pulses, glows = [], [], [], []
    text, sub, lead, pop, panel, title = kit(bd, pops)
    cam = bd.camera
    cam(0, 960, 540, 1.0, 0.1)

    def F(pic, fx, fy):
        return pic.map((fx * pic.src.width, fy * pic.src.height))

    # ---------------- HOOK
    s = sc["hook"]
    hk = title("anatomy of the heart", 960, 100, 0.3)
    ext = pop(sv("coeur_09"), 640, 600, h=720, t=0.6)
    tf = s.t("fist")
    hk += [ext, panel(1180, 300, 1800, 440, PINK, tf - 0.3), text("about the size", 1220, 360, 44, MAROON, tf - 0.2),
           text("of your fist", 1220, 415, 44, RED_T, tf + 0.5)]
    tb = s.t("break")
    hk += [panel(1180, 490, 1800, 600, CREAM, tb - 0.3), text("never takes a break", 1220, 560, 44, GOLD_T, tb)]
    ts = s.t("structure")
    hk += [text("let's look at its structure", 1200, 720, 42, PURPLE, ts - 0.4)]

    # ---------------- LOCATION: torso + lungs + heart
    s = sc["location"]
    bd.erase(s.start, hk)
    torso = pop(sv("Male-silhouette"), 560, 640, h=1000, t=s.start + 0.2)
    lungs = pop(sv("poumons_01"), 560, 470, h=380, t=s.t("lungs") - 0.5)
    hrt = pop(sv("coeur_09"), 585, 520, h=200, t=s.t("chest") - 0.3)
    lo = [torso, lungs, hrt, text("middle of the chest", 1050, 300, 46, MAROON, s.t("middle")),
          lead([(1045, 295), (800, 380), (620, 470)], s.t("middle") + 0.6),
          text("between the lungs", 1050, 380, 42, BLUE_T, s.t("lungs")), text("tilted to the left", 1050, 450, 42, MAROON, s.t("tilted"))]
    glows.append((s.t("chest"), (585, 520), 2.0, 80))
    tcm = s.t("cardiac")
    lo += [pop(OF.circle_inset(sv("cellules_coeur"), 360, RED_T), 1450, 700, h=340, t=tcm - 0.2),
           text("cardiac muscle", 1450, 920, 48, RED_T, tcm + 0.3, "c"), text("never tires out", 1450, 980, 36, MAROON, s.t("tiring"), "c")]

    # ---------------- WALL: pericardium + 3 layers
    s = sc["wall"]
    bd.erase(s.start, lo)
    ca = pop(sv("Coeur_A"), 430, 560, h=960, t=s.start + 0.2)
    tp = s.t("pericardium")
    sac = [(F(ca, 0.5, 0.31)[0] + 260 * __import__("math").cos(a / 40 * 6.283), F(ca, 0.5, 0.31)[1] + 300 * __import__("math").sin(a / 40 * 6.283)) for a in range(41)]
    wl = [ca, bd.add(B.Stroke(sac, PURPLE, 4, t=tp - 0.2, dur=1.0)), text("pericardium", 760, 150, 46, PURPLE, tp),
          text("protective sac", 760, 205, 34, MAROON, tp + 0.7)]
    lay = [("epicardium", "tunique_coeur_2", 1160, 230, "thin outer layer", GOLD_T),
           ("myocardium", "tunique_coeur_3", 1420, 330, "thick muscle: pumps", RED_T),
           ("endocardium", "tunique_coeur_4", 1690, 230, "smooth inner lining", MAROON)]
    for name, img, x, w, desc, col in lay:
        tt = s.t(name)
        wl += [pop(sv(img), x, 560, w=w, t=tt - 0.3), text(name, x, 860, 42, col, tt, "c"), text(desc, x, 910, 28, MAROON, tt + 0.6, "c")]
    wl += [text("3 layers of the heart wall", 1420, 230, 46, MAROON, s.t("three") - 0.2, "c")]
    mz = F(ca, 0.6, 0.4)
    glows.append((s.t("myocardium"), mz, 2.0, 60))

    # ---------------- CHAMBERS (painted section)
    s = sc["chambers"]
    bd.erase(s.start, wl)
    hs = pop(OP.HEART, 800, 590, h=900, t=s.start + 0.2)
    M = lambda k: hs.map(OP.P[k])
    ta, tv = s.t("atria"), s.t("ventricles")
    ch = [text("atria", 160, 280, 56, BLUE_T, ta), text("receive blood", 160, 335, 34, MAROON, ta + 0.6),
          lead([(300, 275), (430, 320), M("RA")], ta + 0.3, BLUE_T), lead([(300, 270), (600, 210), (900, 240), M("LA")], ta + 0.5, BLUE_T),
          text("ventricles", 160, 800, 56, RED_T, tv), text("pump blood out", 160, 855, 34, MAROON, tv + 0.6),
          lead([(440, 795), (520, 790), M("RV")], tv + 0.3, RED_T), lead([(440, 800), (700, 900), (900, 860), M("LV")], tv + 0.5, RED_T)]
    glows += [(ta, M("RA"), 1.8, 110), (ta, M("LA"), 1.8, 100), (tv, M("RV"), 1.8, 120), (tv, M("LV"), 1.8, 130)]
    for nm, k, y, tt in (("right atrium", "RA", 300, s.t("right", 1)), ("left atrium", "LA", 360, s.t("left", 1)),
                         ("right ventricle", "RV", 420, s.t("right", 2)), ("left ventricle", "LV", 480, s.t("left", 2))):
        ch.append(text(nm, 1300, y, 40, BLUE_T if "right" in nm else RED_T, tt))
    tse = s.t("septum")
    ch += [panel(1260, 560, 1820, 700, LILAC, tse - 0.3), text("septum", 1300, 620, 48, PURPLE, tse),
           text("separates right & left", 1300, 675, 32, MAROON, tse + 0.6), lead([(1255, 640), (1100, 640), M("septum")], tse + 0.4, PURPLE)]
    glows.append((tse + 0.2, M("septum"), 1.6, 60))

    # ---------------- WALL THICKNESS (zoom ventricles)
    s = sc["thickness"]
    bd.erase(s.start, ch)
    cam(s.start, 820, 760, 1.4, 1.0)
    lvw, rvw = hs.map((475, 520)), hs.map((70, 560))
    th = [text("thick wall", 1150, 640, 44, RED_T, s.t("thickest")), lead([(1145, 635), (lvw[0] + 15, lvw[1])], s.t("thickest") + 0.5, RED_T),
          text("-> whole body", 1150, 690, 34, MAROON, s.t("entire")),
          text("thin wall", 260, 640, 44, BLUE_T, s.t("thinner")), lead([(390, 650), (rvw[0] - 10, rvw[1])], s.t("thinner") + 0.5, BLUE_T),
          text("-> nearby lungs", 260, 690, 34, MAROON, s.t("lungs"))]
    glows += [(s.t("thickest"), lvw, 2.5, 70), (s.t("thinner"), rvw, 2.5, 55)]

    # ---------------- VALVES (top view) then chordae (zoom)
    s = sc["valves"]
    cam(s.start, 960, 540, 1.0, 1.0)
    bd.erase(s.start, th + [hs])
    vt = pop(sv("valves_01"), 760, 560, w=820, t=s.start + 0.3)
    tri, mit, aor, pul = F(vt, 0.29, 0.33), F(vt, 0.73, 0.33), F(vt, 0.42, 0.6), F(vt, 0.5, 0.8)
    tav = s.t("atrioventricular")
    va = [vt, text("seen from above", 760, 140, 36, PURPLE, s.start + 0.8, "c"),
          panel(1260, 230, 1840, 520, SKY, tav - 0.3), text("AV valves", 1300, 290, 48, BLUE_T, tav)]
    va += sub("tricuspid: 3 flaps", 1300, 360, 38, MAROON, s.t("tricuspid")) + sub("mitral: 2 flaps", 1300, 430, 38, MAROON, s.t("mitral"))
    va += [lead([(1255, 350), (900, 180), (tri[0], tri[1] - 60)], s.t("tricuspid") + 0.3, BLUE_T),
           lead([(1255, 420), (mit[0] + 60, mit[1])], s.t("mitral") + 0.3, BLUE_T)]
    tsl = s.t("semilunar")
    va += [panel(1260, 580, 1840, 870, PINK, tsl - 0.3), text("semilunar valves", 1300, 640, 48, RED_T, tsl)]
    va += sub("pulmonary", 1300, 710, 38, MAROON, s.t("pulmonary")) + sub("aortic", 1300, 780, 38, MAROON, s.t("aortic"))
    va += [lead([(1255, 700), (900, 900), (pul[0] + 40, pul[1] + 20)], s.t("pulmonary") + 0.3, RED_T),
           lead([(1255, 770), (1000, 640), (aor[0] + 50, aor[1])], s.t("aortic") + 0.3, RED_T)]
    glows += [(s.t("tricuspid"), tri, 1.5, 90), (s.t("mitral"), mit, 1.5, 90), (s.t("pulmonary"), pul, 1.5, 60), (s.t("aortic"), aor, 1.5, 60)]
    tch = s.t("chordae")
    bd.erase(tch - 0.6, va)
    hs2 = pop(OP.HEART, 800, 590, h=900, t=tch - 0.5)
    cho, pap = hs2.map((395, 430)), hs2.map((395, 510))
    cam(tch - 0.3, cho[0] + 120, cho[1] + 30, 1.9, 1.0)
    cd = [text("chordae tendineae", cho[0] + 120, cho[1] - 110, 30, MAROON, tch), lead([(cho[0] + 115, cho[1] - 112), (cho[0] + 6, cho[1] - 6)], tch + 0.6),
          text("papillary muscles", pap[0] + 120, pap[1] + 70, 30, RED_T, s.t("papillary")),
          lead([(pap[0] + 115, pap[1] + 62), (pap[0] + 10, pap[1] + 6)], s.t("papillary") + 0.5, RED_T),
          text("stop flaps flipping back", cho[0] + 120, cho[1] - 65, 22, PURPLE, s.t("flipping"))]

    # ---------------- GREAT VESSELS
    s = sc["vessels"]
    bd.erase(s.start, cd)
    cam(s.start, 960, 540, 1.0, 1.0)
    V = lambda p: hs2.map(p)
    gv = [text("superior vena cava", 120, 160, 38, BLUE_T, s.t("superior")), lead([(420, 170), V((100, 90))], s.t("superior") + 0.6, BLUE_T),
          text("inferior vena cava", 120, 960, 38, BLUE_T, s.t("inferior")), lead([(420, 950), V((85, 660))], s.t("inferior") + 0.6, BLUE_T),
          text("pulmonary trunk", 1250, 170, 40, BLUE_T, s.t("trunk")), lead([(1245, 165), (1150, 200), V((380, 175))], s.t("trunk") + 0.6, BLUE_T),
          text("pulmonary veins", 1300, 420, 40, RED_T, s.t("veins")), lead([(1295, 415), V((485, 255))], s.t("veins") + 0.6, RED_T),
          text("aorta", 1250, 80, 46, RED_T, s.t("aorta", 1)), lead([(1245, 75), (1000, 90), V((250, 100))], s.t("aorta", 1) + 0.5, RED_T)]
    glows += [(s.t("superior"), V((100, 90)), 1.5, 50), (s.t("inferior"), V((85, 660)), 1.5, 50), (s.t("trunk"), V((380, 175)), 1.5, 50),
              (s.t("veins"), V((485, 255)), 1.5, 50), (s.t("aorta", 1), V((250, 100)), 1.5, 60)]
    gv += [panel(1250, 600, 1840, 760, SKY, s.t("into") - 0.3), text("blue = oxygen-poor", 1290, 665, 38, BLUE_T, s.t("into")),
           panel(1250, 790, 1840, 950, PINK, s.t("body") - 0.8), text("red = oxygen-rich", 1290, 855, 38, RED_T, s.t("body") - 0.6)]

    # ---------------- CORONARY
    s = sc["coronary"]
    bd.erase(s.start, gv + [hs2])
    co = pop(sv("coeur_09"), 640, 590, h=780, t=s.start + 0.2)
    base, lad, rca = F(co, 0.42, 0.42), F(co, 0.62, 0.64), F(co, 0.33, 0.78)
    cr = [co, text("coronary arteries", 1180, 330, 56, RED_T, s.t("coronary")),
          lead([(1175, 325), (950, 420), (lad[0] + 6, lad[1])], s.t("coronary") + 0.5, RED_T),
          lead([(1175, 330), (800, 250), (rca[0], rca[1] - 30)], s.t("coronary") + 0.7, RED_T),
          panel(1180, 420, 1820, 560, CREAM, s.t("base") - 0.6), text("branch off the aorta", 1220, 485, 42, GOLD_T, s.t("base") - 0.4),
          text("at its base", 1220, 540, 36, MAROON, s.t("base")), lead([(1175, 480), (base[0] + 10, base[1])], s.t("base"), GOLD_T)]
    glows += [(s.t("coronary"), lad, 3.0, 60), (s.t("coronary"), rca, 3.0, 50), (s.t("base"), base, 1.5, 50)]

    # ---------------- SUMMARY
    s = sc["summary"]
    bd.erase(s.start, cr)
    sm = title("summary", 960, 100, s.start + 0.2)
    items = [("layers", "3 wall layers", "tunique_coeur_3", 300), ("chambers", "4 chambers", None, 760),
             ("valves", "4 valves", "valves_01", 1220), ("great", "great vessels", "coeur_09", 1680)]
    for w, nm, img, x in items:
        tt = s.t(w) - 0.3
        sm += [panel(x - 200, 220, x + 200, 640, CREAM if img else PINK, tt - 0.2), text(nm, x, 600, 40, MAROON, tt + 0.2, "c")]
        if img:
            sm.append(pop(sv(img), x, 400, h=260 if img != "tunique_coeur_3" else 260, t=tt))
        else:
            sm.append(pop(OP.HEART, x, 400, h=300, t=tt))
    tn = s.t("next")
    sm += [panel(560, 760, 1360, 940, LILAC, tn), text("next video", 960, 830, 42, PURPLE, tn + 0.3, "c"),
           text("physiology of the heart", 960, 905, 54, RED_T, tn + 0.9, "c")]

    bd.fx.append(lambda crop, ctx, t: OP.fx(crop, ctx, t, rings, pulses, glows))
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render(out="heart_anatomy.mp4"):
    import subprocess
    import render_ecg as RE
    bd, sc = build()
    vid = HERE / "ha_video_only.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080",
                           "-r", "30", "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                           "-pix_fmt", "yuv420p", str(vid)], stdin=subprocess.PIPE)
    for f in range(int(round(RE.INTRO_DUR * 30))):
        ff.stdin.write(RE.intro_frame(f / 30).tobytes())
    for f in range(int(bd.total * 30)):
        ff.stdin.write(OF.credit(bd.frame(f / 30)).tobytes())
    ff.stdin.close()
    ff.wait()
    RE.intro_audio(HERE / "audio_intro.wav")
    lst = HERE / f"{out}.txt"
    with open(lst, "w") as fh:
        fh.write(f"file '{HERE / 'audio_intro.wav'}'\n")
        for s in sc.values():
            fh.write(f"file '{s.audio}'\n")
    raw, mix = HERE / f"{out}.raw.wav", HERE / f"{out}.mix.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "pcm_s16le", str(raw)], check=True)
    OM.pop_sfx(raw, mix, bd.pops, RE.INTRO_DUR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(mix), "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(HERE / out)], check=True)
    print("done ->", HERE / out)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        bd, _ = build()
        for t in sorted(float(x) for x in sys.argv[2:]):
            OF.credit(bd.frame(t)).save(HERE / f"a_{t:06.1f}.png")
        print("ok", round(bd.total, 1))
    else:
        render()
