"""Heart Anatomy v2: professor-style script + 'zoom journey' camera (body -> chest -> heart -> wall -> inside)."""
import json
import os
import sys
from pathlib import Path

from PIL import ImageDraw

HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE.parent / "hanat2")))
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_preview as OP  # noqa: E402
import osm_full as OF  # noqa: E402
import osm_mi as OM  # noqa: E402
import osm_hanat as HA  # noqa: E402
import osm_hphys as HP  # noqa: E402

MAROON, PURPLE, TEAL, BLUE_T, RED_T, GOLD_T, GREEN_T = OF.MAROON, OF.PURPLE, OF.TEAL, OF.BLUE_T, OF.RED_T, OF.GOLD_T, OF.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OF.PINK, OF.LILAC, OF.CREAM, OF.MINT, OF.SKY
sv = HA.sv
PW, PH = 1920, 1080


class Sc(HA.Sc):
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
    bd = B.Board(4, 2)
    pops, glows, flows = [], [], []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    add, cam = bd.add, bd.camera

    def F(pic, fx, fy):
        return pic.map((fx * pic.src.width, fy * pic.src.height))

    def zoom_cut(t, into, page_center, zoom=3.0, dur=0.9):
        """Fly into a point, then continue the zoom on the next page (feels like one long zoom)."""
        cam(t, into[0], into[1], zoom, dur)
        cam(t + dur, page_center[0], page_center[1], 0.72, 0.0)
        cam(t + dur + 0.01, page_center[0], page_center[1], 1.0, 0.9)
        return t + dur

    A = (960, 540)            # page: body
    Bc = (PW + 960, 540)      # page: heart
    C = (2 * PW + 960, 540)   # page: wall layers
    D = (960, PH + 540)       # page: summary
    cam(0, *A, 1.0, 0.1)

    # ---------------- HOOK (body page)
    s = sc["hook"]
    body = pop(sv("Male-silhouette"), 600, 600, h=1000, t=0.3)
    hk = [body, panel(1080, 220, 1820, 360, PINK, s.t("hundred") - 0.3), text("100,000 beats / day", 1120, 305, 52, RED_T, s.t("hundred"))]
    hk += [panel(1080, 410, 1820, 550, CREAM, s.t("stops") - 0.3), text("never stops, never rests", 1120, 495, 44, GOLD_T, s.t("stops"))]
    hk += [text("how is it built?", 1450, 700, 60, PURPLE, s.t("built") - 0.2, "c")]
    hk += [lead([(1350, 750), (1100, 820), (640, 520)], s.t("zoom"), PURPLE, 5, 0.6, arrow=True)]

    # ---------------- LOCATION
    s = sc["location"]
    bd.erase(s.start, hk[1:])
    lungs = pop(sv("poumons_01"), 600, 440, h=380, t=s.t("lungs") - 0.6)
    heart_small = pop(sv("coeur_09"), 625, 490, h=200, t=s.t("here") - 0.1)
    glows.append((s.t("here"), (625, 490), 2.0, 90))
    lo = [text("middle of the chest", 1050, 300, 50, MAROON, s.t("middle")), lead([(1045, 295), (800, 380), (660, 470)], s.t("middle") + 0.4),
          text("between the lungs", 1050, 400, 46, BLUE_T, s.t("lungs")), text("tilted to the left", 1050, 490, 46, MAROON, s.t("tilted")),
          panel(1040, 580, 1800, 720, PINK, s.t("fist") - 0.3), text("size of your fist", 1080, 665, 52, RED_T, s.t("fist"))]
    tz = s.end - 1.0
    zoom_cut(tz, (625, 490), Bc, 3.2, 1.0)
    bd.erase(tz + 1.0, [body, lungs, heart_small] + lo)

    # ---------------- WALL (heart page -> layers page -> back)
    s = sc["wall"]
    ext = pop(sv("coeur_09"), PW + 760, 580, h=900, t=tz + 0.95, dur=0.2)
    tw = s.t("wall")
    spot = F(ext, 0.62, 0.62)
    glows.append((tw - 0.4, spot, 1.0, 60))
    zoom_cut(tw, spot, C, 3.4, 0.9)
    X = 2 * PW
    wl = [text("3 layers of the heart wall", X + 960, 110, 60, MAROON, tw + 1.0, "c")]
    lay = [("epicardium", "tunique_coeur_2", 420, 250, "outside", GOLD_T),
           ("myocardium", "tunique_coeur_3", 960, 380, "thick muscle: pumps!", RED_T),
           ("endocardium", "tunique_coeur_4", 1500, 250, "smooth inside lining", MAROON)]
    for name, img, x, w, desc, col in lay:
        tt = s.t(name)
        wl += [pop(sv(img), X + x, 520, w=w, t=tt - 0.3), text(name, X + x, 860, 52, col, tt, "c"), text(desc, X + x, 925, 34, MAROON, tt + 0.6, "c")]
    glows.append((s.t("pumps") if "pumps" in s.words else s.t("myocardium") + 1.5, (X + 960, 520), 1.8, 160))
    tp = s.t("pericardium") - 1.6
    cam(tp, Bc[0], Bc[1], 1.0, 1.0)
    bd.erase(tp + 1.0, wl)
    cx, cy = F(ext, 0.5, 0.52)
    import math
    sac = [(cx + 360 * math.cos(a / 48 * 6.283), cy + 470 * math.sin(a / 48 * 6.283)) for a in range(49)]
    pe = [add(B.Stroke(sac, PURPLE, 7, t=tp + 1.0, dur=1.2)), text("pericardium", PW + 1250, 300, 56, PURPLE, s.t("pericardium")),
          text("protective bag", PW + 1250, 365, 40, MAROON, s.t("pericardium") + 0.6)]

    # ---------------- TWO PUMPS (cut open)
    s = sc["pumps"]
    tc = s.t("cut")
    cut = add(B.Stroke([F(ext, 0.55, 0.05), F(ext, 0.5, 0.5), F(ext, 0.55, 0.98)], (90, 90, 100), 6, t=tc, dur=0.7))
    bd.erase(tc + 0.9, pe + [cut, ext])
    hs = pop(OP.HEART, PW + 760, 590, h=900, t=tc + 0.8, dur=0.5)
    M = lambda k: hs.map(OP.P[k])
    tb = s.t("big")
    pu = [text("two pumps", PW + 1450, 140, 64, MAROON, s.t("two") - 0.2, "c")]
    lung_i = pop(sv("poumons_01"), PW + 1330, 380, h=220, t=s.t("lungs") - 0.4)
    body_i = pop(sv("Male-silhouette"), PW + 1640, 700, h=330, t=s.t("body") - 0.4)
    pu += [lung_i, body_i, text("right pump -> lungs", PW + 1150, 560, 40, BLUE_T, s.t("right")),
           text("left pump -> body", PW + 1150, 920, 40, RED_T, s.t("left"))]
    flows.append(([hs.map(p) for p in HP.RIGHT_PATH], s.t("right"), s.end + 1.0, (90, 130, 210)))
    flows.append(([hs.map(p) for p in HP.LEFT_PATH], s.t("left"), s.end + 1.0, (215, 70, 80)))
    pu += [lead([M("RV"), (PW + 1000, 470), (PW + 1210, 400)], s.t("lungs"), BLUE_T, 6, 0.5, arrow=True),
           lead([M("LV"), (PW + 1250, 780), (PW + 1480, 720)], s.t("body"), RED_T, 6, 0.5, arrow=True)]
    tsp = s.t("septum")
    pu += [text("septum", PW + 120, 600, 52, PURPLE, tsp), lead([(PW + 300, 590), (PW + 500, 650), M("septum")], tsp + 0.4, PURPLE)]
    glows.append((tsp, M("septum"), 2.0, 70))

    # ---------------- CHAMBERS
    s = sc["chambers"]
    bd.erase(s.start, pu)
    ta, tv = s.t("upstairs"), s.t("downstairs")
    ch = [panel(PW + 1180, 230, PW + 1840, 400, SKY, ta - 0.2), text("upstairs: atrium", PW + 1220, 305, 48, BLUE_T, ta),
          text("receives blood", PW + 1220, 365, 36, MAROON, s.t("receives")),
          panel(PW + 1180, 450, PW + 1840, 620, PINK, tv - 0.2), text("downstairs: ventricle", PW + 1220, 525, 46, RED_T, tv),
          text("pumps blood out", PW + 1220, 585, 36, MAROON, s.t("out")),
          text("= 4 chambers", PW + 1510, 760, 72, MAROON, s.t("four"), "c")]
    glows += [(ta, M("RA"), 2.2, 110), (ta, M("LA"), 2.2, 100), (tv, M("RV"), 2.2, 120), (tv, M("LV"), 2.2, 130)]
    for k in ("RA", "LA", "RV", "LV"):
        glows.append((s.t("four"), M(k), 1.2, 100))

    # ---------------- THICK WALL (zoom into ventricles)
    s = sc["thick"]
    bd.erase(s.start, ch)
    lvw, rvw = hs.map((475, 520)), hs.map((185, 628))
    cam(s.start, PW + 820, 760, 1.5, 1.0)
    th = [text("thick!", PW + 1150, 620, 60, RED_T, s.t("thicker")), lead([(PW + 1145, 615), (lvw[0] + 15, lvw[1])], s.t("thicker") + 0.4, RED_T, 6),
          text("the bodybuilder", PW + 1150, 690, 40, MAROON, s.t("bodybuilder")),
          text("thin", PW + 300, 640, 50, BLUE_T, s.t("thicker") + 0.8), lead([(PW + 400, 650), (rvw[0] - 10, rvw[1])], s.t("thicker") + 1.2, BLUE_T, 6)]
    glows += [(s.t("thicker"), lvw, 3.0, 80)]
    te = s.t("exam")
    th += [panel(PW + 1100, 820, PW + 1840, 960, CREAM, te - 0.3), text("exam tip:", PW + 1130, 870, 36, GOLD_T, te),
           text("thickest wall = left ventricle", PW + 1130, 925, 34, MAROON, te + 0.6)]

    # ---------------- VALVES + mnemonic
    s = sc["valves"]
    cam(s.start, *Bc, 1.0, 1.0)
    bd.erase(s.start + 0.5, th)
    va = [text("4 one-way doors", PW + 1450, 140, 56, MAROON, s.t("doors") - 0.3, "c")]
    tt = s.t("try")
    va += [panel(PW + 1120, 230, PW + 1840, 330, CREAM, tt - 0.3), text("try pulling my aorta", PW + 1480, 300, 46, GOLD_T, tt, "c")]
    vpos = {"tricuspid": (165, 400), "pulmonary": (245, 330), "mitral": (370, 390), "aortic": (300, 330)}
    for i, (w, col) in enumerate((("tricuspid", BLUE_T), ("pulmonary", BLUE_T), ("mitral", RED_T), ("aortic", RED_T))):
        tw_ = s.t(w)
        y = 420 + i * 95
        va += [text(f"{w[0].upper()} = {w}", PW + 1160, y, 46, col, tw_ - 0.1)]
        glows.append((tw_, hs.map(vpos[w]), 1.3, 55))

    # ---------------- CHORDAE (zoom on tricuspid)
    s = sc["chordae"]
    bd.erase(s.start, va)
    cho, pap = hs.map((150, 445)), hs.map((172, 505))
    cam(s.start, cho[0] + 120, cho[1] + 20, 2.2, 1.1)
    cd = [panel(cho[0] + 95, cho[1] - 115, cho[0] + 470, cho[1] - 5, CREAM, s.t("chordae") - 0.3),
          panel(pap[0] + 75, pap[1] + 25, pap[0] + 400, pap[1] + 85, PINK, s.t("papillary") - 0.3),
          text("chordae tendineae", cho[0] + 110, cho[1] - 70, 30, MAROON, s.t("chordae")),
          lead([(cho[0] + 105, cho[1] - 72), (cho[0] + 5, cho[1] - 5)], s.t("chordae") + 0.5, MAROON, 4),
          text("papillary muscle", pap[0] + 90, pap[1] + 60, 28, RED_T, s.t("papillary")),
          lead([(pap[0] + 85, pap[1] + 52), (pap[0] + 6, pap[1] + 4)], s.t("papillary") + 0.5, RED_T, 4),
          text("like parachute strings", cho[0] + 110, cho[1] - 25, 22, PURPLE, s.t("parachute"))]
    glows += [(s.t("strings"), cho, 2.0, 35), (s.t("papillary"), pap, 1.5, 25)]

    # ---------------- VESSELS (pull back)
    s = sc["vessels"]
    cam(s.start, *Bc, 1.0, 1.1)
    bd.erase(s.start + 0.3, cd)
    V = lambda p: hs.map(p)
    gv = [text("vena cava -> in", PW + 100, 160, 42, BLUE_T, s.t("cava")), lead([(PW + 400, 170), V((100, 90))], s.t("cava") + 0.4, BLUE_T),
          text("pulmonary trunk -> lungs", PW + 1220, 200, 40, BLUE_T, s.t("trunk")), lead([(PW + 1215, 195), V((380, 175))], s.t("trunk") + 0.4, BLUE_T),
          text("pulmonary veins <- back", PW + 1260, 430, 40, RED_T, s.t("veins")), lead([(PW + 1255, 425), V((485, 255))], s.t("veins") + 0.4, RED_T),
          text("aorta -> body", PW + 1220, 100, 46, RED_T, s.t("aorta")), lead([(PW + 1215, 95), V((250, 100))], s.t("aorta") + 0.4, RED_T)]
    for w, p in (("cava", (100, 90)), ("trunk", (380, 175)), ("veins", (485, 255)), ("aorta", (250, 100))):
        glows.append((s.t(w), V(p), 1.4, 55))

    # ---------------- SUMMARY (slide to summary page)
    s = sc["summary"]
    cam(s.start, *D, 1.0, 1.1)
    bd.erase(s.start + 1.2, gv + [hs])
    sm = title("remember 3 things", D[0], PH + 110, s.start + 0.6)
    for w, nm, img, x, col in (("pumps", "2 pumps", None, 400, SKY), ("chambers", "4 chambers", "heart", 960, PINK),
                               ("doors", "4 one-way doors", "valves_01", 1520, CREAM)):
        tt = s.t(w) - 0.3
        sm += [panel(x - 250, PH + 250, x + 250, PH + 700, col, tt - 0.2), text(nm, x, PH + 650, 46, MAROON, tt + 0.2, "c")]
        if img == "heart":
            sm.append(pop(OP.HEART, x, PH + 440, h=300, t=tt))
        elif img:
            sm.append(pop(sv(img), x, PH + 440, h=260, t=tt))
        else:
            sm += [pop(sv("poumons_01"), x - 90, PH + 440, h=170, t=tt), pop(sv("Male-silhouette"), x + 110, PH + 440, h=260, t=tt + 0.2)]
    tn = s.t("next")
    sm += [panel(560, PH + 800, 1360, PH + 960, LILAC, tn), text("next: how it all works together", 960, PH + 900, 46, PURPLE, tn + 0.3, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
        d = ImageDraw.Draw(crop)
        for pts, ta, tb2, col in flows:
            if ta <= t <= tb2:
                gap = 0.11
                u = ((t - ta) * 0.18) % gap
                while u <= 1.0:
                    cx_, cy_ = ctx.px(B.partial_pts(pts, u)[-1])
                    r = 11 * B.BS
                    d.ellipse((cx_ - r, cy_ - r, cx_ + r, cy_ + r), fill=col, outline=(255, 255, 255), width=int(3 * B.BS))
                    u += gap
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render(out="heart_anatomy_v2.mp4"):
    import subprocess
    import render_ecg as RE
    bd, sc = build()
    vid = HERE / "ha2_video_only.mp4"
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
    import sfx
    S = sc
    cues = [(S["hook"].start, S["hook"].end, "heartbeat"), (S["pumps"].t("right"), S["pumps"].end, "flow"),
            (S["chordae"].start, S["chordae"].end, "heartbeat")]
    moods = [(0, S["location"].start, "curious"), (S["location"].start, S["thick"].start, "steady"),
             (S["thick"].start, S["valves"].start, "tension"), (S["valves"].start, bd.total, "steady")]
    OM.pop_sfx(raw, mix, bd.pops, RE.INTRO_DUR)  # owner: narration only, no SFX/music
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(mix), "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(HERE / out)], check=True)
    print("done ->", HERE / out)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        bd, _ = build()
        for t in sorted(float(x) for x in sys.argv[2:]):
            OF.credit(bd.frame(t)).save(HERE / f"h2_{t:06.1f}.png")
        print("ok", round(bd.total, 1))
    else:
        render()
