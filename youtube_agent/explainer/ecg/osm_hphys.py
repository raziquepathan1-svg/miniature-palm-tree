"""Cardiovascular series ep.2: Physiology of the Heart (Osmosis style)."""
import json
import math
import sys
from pathlib import Path

from PIL import ImageDraw

HERE = Path(__file__).resolve().parent
EP = HERE.parent / "hphys"
sys.path.insert(0, str(HERE.parent / "heart"))
import board as B  # noqa: E402

B.FONT[0] = B.SC
import osm_preview as OP  # noqa: E402
import osm_full as OF  # noqa: E402
import osm_mi as OM  # noqa: E402
import osm_hanat as HA  # noqa: E402

MAROON, PURPLE, TEAL, BLUE_T, RED_T, GOLD_T, GREEN_T = OF.MAROON, OF.PURPLE, OF.TEAL, OF.BLUE_T, OF.RED_T, OF.GOLD_T, OF.GREEN_T
PINK, LILAC, CREAM, MINT, SKY = OF.PINK, OF.LILAC, OF.CREAM, OF.MINT, OF.SKY
sv = HA.sv

RIGHT_PATH = [(95, 30), (100, 200), (115, 300), (160, 390), (190, 470), (215, 540), (235, 450), (250, 330), (300, 235), (390, 160), (480, 150)]
LEFT_PATH = [(505, 275), (430, 285), (370, 320), (365, 400), (390, 500), (400, 580), (340, 470), (300, 340), (260, 230), (240, 130), (270, 40)]


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
    bd = B.Board(1, 1)
    pops, glows, flows = [], [], []
    text, sub, lead, pop, panel, title = HA.kit(bd, pops)
    add, cam = bd.add, bd.camera
    cam(0, 960, 540, 1.0, 0.1)

    def F(pic, fx, fy):
        return pic.map((fx * pic.src.width, fy * pic.src.height))

    # ---------------- HOOK
    s = sc["hook"]
    hk = title("physiology of the heart", 960, 100, 0.3)
    hk += [pop(sv("coeur_09"), 640, 600, h=700, t=0.6), panel(1180, 330, 1800, 470, LILAC, s.t("last") - 0.2),
           text("last video: the parts", 1220, 410, 44, PURPLE, s.t("last")),
           panel(1180, 520, 1800, 660, PINK, s.t("together") - 0.3), text("now: how they work", 1220, 600, 44, RED_T, s.t("together"))]
    glows += [(s.t("beat", 1) + k * 0.8, (640, 640), 0.5, 220) for k in range(3)]

    # ---------------- TWO CIRCUITS: lungs top, body bottom, heart middle
    s = sc["circuits"]
    bd.erase(s.start, hk)
    hrt = pop(OP.HEART, 960, 560, h=420, t=s.start + 0.2)
    lu = pop(sv("poumons_01"), 960, 160, h=250, t=s.t("lungs") - 0.4)
    bo = pop(sv("Male-silhouette"), 960, 900, h=300, t=s.t("body") - 0.4)
    tp, ts = s.t("pulmonary"), s.t("systemic")
    loopL = [(880, 470), (620, 420), (620, 200), (820, 150)]
    loopR = [(1100, 160), (1300, 200), (1300, 420), (1050, 470)]
    ci = [hrt, lu, bo, text("lungs", 960, 320, 40, BLUE_T, s.t("lungs"), "c"), text("body", 1180, 900, 40, RED_T, s.t("body")),
          add(B.Stroke(B.smooth(loopL, 10), BLUE_T, 7, t=s.t("right") + 0.2, dur=1.0, arrow=True)),
          add(B.Stroke(B.smooth(loopR, 10), RED_T, 7, t=s.t("right") + 1.0, dur=1.0, arrow=True)),
          panel(80, 220, 560, 380, SKY, tp - 0.3), text("pulmonary", 120, 285, 48, BLUE_T, tp), text("circulation", 120, 345, 40, BLUE_T, tp + 0.5),
          text("right heart -> lungs", 120, 430, 32, MAROON, tp + 1.0),
          add(B.Stroke(B.smooth([(1050, 650), (1450, 700), (1450, 960), (1110, 980)], 10), RED_T, 7, t=s.t("left") + 0.2, dur=1.2, arrow=True)),
          add(B.Stroke(B.smooth([(810, 980), (470, 960), (470, 700), (870, 650)], 10), BLUE_T, 7, t=s.t("left") + 1.2, dur=1.2, arrow=True)),
          panel(1360, 220, 1840, 380, PINK, ts - 0.3), text("systemic", 1400, 285, 48, RED_T, ts), text("circulation", 1400, 345, 40, RED_T, ts + 0.5),
          text("left heart -> body", 1400, 430, 32, MAROON, ts + 1.0)]

    # ---------------- RIGHT SIDE path with flowing blood
    s = sc["right"]
    bd.erase(s.start, ci)
    hs = pop(OP.HEART, 760, 590, h=900, t=s.start + 0.2)
    rp = [hs.map(p) for p in RIGHT_PATH]
    flows.append((rp, s.start + 0.6, s.end - 0.3, (90, 130, 210)))
    steps = [("vena", "vena cava", 120), ("atrium", "right atrium", 190), ("tricuspid", "tricuspid valve", 260),
             ("ventricle", "right ventricle", 330), ("pulmonary", "pulmonary valve", 400), ("artery", "pulmonary artery", 470), ("lungs", "-> lungs", 540)]
    rt = [panel(1260, 80, 1840, 600, SKY, s.start + 0.4), text("right side", 1550, 60, 44, BLUE_T, s.start + 0.5, "c")]
    for i, (w, nm, y) in enumerate(steps):
        rt.append(text(f"{i + 1}. {nm}" if w != "lungs" else nm, 1300, y + 40, 38, BLUE_T, s.t(w) - 0.1))
    gl = {"atrium": (110, 320), "tricuspid": (165, 400), "ventricle": (190, 520), "pulmonary": (245, 330), "artery": (360, 175)}
    for w, p in gl.items():
        glows.append((s.t(w), hs.map(p), 1.4, 70))

    # ---------------- LUNGS exchange
    s = sc["lungs"]
    bd.erase(s.start, rt + [hs])
    lg = pop(sv("poumons_01"), 620, 560, h=700, t=s.start + 0.2)
    tco, tox = s.t("carbon"), s.t("oxygen")
    lu2 = [lg, panel(1180, 260, 1820, 420, SKY, tco - 0.3), text("drops off CO2", 1220, 350, 50, BLUE_T, tco),
           lead([(1175, 340), (900, 420)], tco + 0.5, BLUE_T, 5, 0.4, arrow=True),
           panel(1180, 480, 1820, 640, PINK, tox - 0.3), text("picks up O2", 1220, 570, 50, RED_T, tox),
           lead([(900, 600), (1175, 560)], tox + 0.5, RED_T, 5, 0.4, arrow=True)]
    tpv = s.t("veins")
    lu2 += [panel(1180, 700, 1820, 860, CREAM, tpv - 0.3), text("pulmonary veins", 1220, 770, 44, RED_T, tpv),
            text("-> left atrium", 1220, 830, 38, MAROON, s.t("left"))]

    # ---------------- LEFT SIDE path
    s = sc["left"]
    bd.erase(s.start, lu2)
    hs2 = pop(OP.HEART, 760, 590, h=900, t=s.start + 0.2)
    lp = [hs2.map(p) for p in LEFT_PATH]
    flows.append((lp, s.start + 0.5, s.end - 0.2, (215, 70, 80)))
    steps = [("atrium", "left atrium", 120), ("mitral", "mitral valve", 190), ("ventricle", "left ventricle", 260),
             ("aortic", "aortic valve", 330), ("aorta", "aorta", 400), ("organ", "-> every organ", 470)]
    lt = [panel(1260, 80, 1840, 540, PINK, s.start + 0.3), text("left side", 1550, 60, 44, RED_T, s.start + 0.4, "c")]
    for i, (w, nm, y) in enumerate(steps):
        lt.append(text(f"{i + 1}. {nm}" if w != "organ" else nm, 1300, y + 40, 38, RED_T, s.t(w) - 0.1))
    gl = {"atrium": (380, 290), "mitral": (370, 390), "ventricle": (400, 520), "aortic": (300, 330), "aorta": (250, 110)}
    for w, p in gl.items():
        glows.append((s.t(w), hs2.map(p), 1.4, 70))

    # ---------------- CARDIAC CYCLE: systole / diastole
    s = sc["cycle"]
    bd.erase(s.start, lt + [hs2])
    tsy, tdi = s.t("systole"), s.t("diastole")
    cy = title("the cardiac cycle", 960, 90, s.start + 0.2)
    cy += [panel(80, 180, 920, 900, PINK, tsy - 0.4), text("systole", 500, 250, 60, RED_T, tsy, "c"),
           pop(sv("systole"), 500, 520, w=720, t=tsy + 0.2), text("ventricles contract", 500, 790, 40, MAROON, s.t("contract", 1), "c"),
           text("-> push blood out", 500, 850, 36, MAROON, s.t("push"), "c")]
    cy += [panel(1000, 180, 1840, 900, SKY, tdi - 0.4), text("diastole", 1420, 250, 60, BLUE_T, tdi, "c"),
           pop(sv("diastole"), 1420, 520, w=720, t=tdi + 0.2), text("ventricles relax", 1420, 790, 40, MAROON, s.t("relax"), "c"),
           text("-> fill with blood", 1420, 850, 36, MAROON, s.t("fill"), "c")]
    tb = s.t("both", 1)
    cy += [text("atria together, then ventricles together", 960, 990, 40, PURPLE, tb, "c")]

    # ---------------- PRESSURE opens / closes valves (drawn diagram)
    s = sc["pressure"]
    bd.erase(s.start, cy)
    pr = title("valves follow pressure", 960, 90, s.start + 0.2)

    def valve_diagram(x0, t, open_):
        out = [add(B.Panel(x0, 300, x0 + 360, 700, (250, 225, 228), t=t)), add(B.Panel(x0 + 420, 380, x0 + 760, 620, (250, 225, 228), t=t))]
        cx = x0 + 390
        if open_:
            flaps = [[(cx, 380), (cx + 60, 420)], [(cx, 620), (cx + 60, 580)]]
        else:
            flaps = [[(cx, 380), (cx + 10, 497)], [(cx, 620), (cx + 10, 503)]]
        out += [add(B.Stroke(f, MAROON, 10, t=t + 0.4, dur=0.3)) for f in flaps]
        return out
    tb_ = s.t("behind")
    pr += valve_diagram(80, tb_ - 0.8, True)
    pr += [text("high", 260, 480, 52, RED_T, tb_), text("low", 640, 500, 44, BLUE_T, tb_ + 0.3),
           lead([(330, 560), (700, 560)], tb_ + 0.5, RED_T, 6, 0.5, arrow=True), text("opens", 500, 780, 52, GREEN_T, s.t("opens"), "c")]
    tf = s.t("front")
    pr += valve_diagram(1040, tf - 0.8, False)
    pr += [text("low", 1220, 500, 44, BLUE_T, tf), text("high", 1600, 480, 52, RED_T, tf + 0.3),
           lead([(1680, 560), (1520, 560)], tf + 0.5, RED_T, 6, 0.4, arrow=True), text("snaps shut", 1420, 780, 52, RED_T, s.t("snaps"), "c")]
    pr += [panel(560, 870, 1360, 990, LILAC, s.t("one") - 0.3), text("blood flows one way", 960, 945, 48, PURPLE, s.t("one"), "c")]

    # ---------------- LUB DUB
    s = sc["lubdub"]
    bd.erase(s.start, pr)
    st = pop(sv("stethoscope"), 300, 560, h=700, t=s.start + 0.2)
    vt = pop(sv("valves_01"), 960, 560, w=640, t=s.start + 0.8)
    tri, mit, aor, pul = F(vt, 0.29, 0.33), F(vt, 0.73, 0.33), F(vt, 0.42, 0.6), F(vt, 0.5, 0.8)
    tl, td = s.t("lub", 1), s.t("dub", 1)
    ld = [st, vt, panel(1360, 220, 1840, 500, SKY, tl - 0.3), text("lub", 1600, 300, 70, BLUE_T, tl, "c"),
          text("tricuspid + mitral close", 1600, 380, 32, MAROON, tl + 0.6, "c"), text("ventricles start to squeeze", 1600, 440, 28, MAROON, s.t("squeeze"), "c"),
          panel(1360, 560, 1840, 840, PINK, td - 0.3), text("dub", 1600, 640, 70, RED_T, td, "c"),
          text("pulmonary + aortic close", 1600, 720, 32, MAROON, td + 0.6, "c"), text("ventricles relax", 1600, 780, 28, MAROON, s.t("relax"), "c")]
    glows += [(tl, tri, 2.5, 90), (tl, mit, 2.5, 90), (td, aor, 2.5, 60), (td, pul, 2.5, 60)]

    # ---------------- CARDIAC OUTPUT
    s = sc["output"]
    bd.erase(s.start, ld)
    tco = s.t("cardiac")
    co = title("cardiac output", 960, 90, tco - 0.4)
    trate, tsv = s.t("rate"), s.t("stroke")
    co += [panel(140, 260, 620, 460, PINK, trate - 0.3), text("heart rate", 380, 340, 50, RED_T, trate, "c"), text("beats / minute", 380, 410, 32, MAROON, trate + 0.5, "c"),
           text("x", 700, 380, 80, MAROON, s.t("times"), "c"),
           panel(780, 260, 1260, 460, SKY, tsv - 0.3), text("stroke volume", 1020, 340, 50, BLUE_T, tsv, "c"), text("blood per beat", 1020, 410, 32, MAROON, tsv + 0.5, "c"),
           text("=", 1340, 380, 80, MAROON, tsv + 1.0, "c"),
           panel(1420, 260, 1840, 460, CREAM, tco - 0.2), text("cardiac output", 1630, 340, 46, GOLD_T, tco + 0.2, "c"), text("blood / minute", 1630, 410, 32, MAROON, tco + 0.8, "c")]
    tfive = s.t("five")
    co += [pop(sv("coeur_09"), 520, 760, h=330, t=tfive - 0.4), text("at rest: ~5 liters / minute", 760, 740, 52, RED_T, tfive),
           text("exercise: several times higher", 760, 830, 46, GREEN_T, s.t("exercise")),
           lead([(1560, 900), (1560, 760)], s.t("exercise") + 0.3, GREEN_T, 7, 0.4, arrow=True)]

    # ---------------- SUMMARY
    s = sc["summary"]
    bd.erase(s.start, co)
    sm = title("summary", 960, 100, s.start + 0.2)
    items = [("circuits", "2 circuits", "lungs & body", SKY, 360), ("phases", "2 phases", "systole & diastole", PINK, 960),
             ("pressure", "valves", "driven by pressure", LILAC, 1560)]
    for w, a, b, col, x in items:
        tt = s.t(w) - 0.3
        sm += [panel(x - 260, 260, x + 260, 520, col, tt - 0.2), text(a, x, 360, 56, MAROON, tt, "c"), text(b, x, 440, 36, PURPLE, tt + 0.5, "c")]
    tn = s.t("next")
    sm += [panel(560, 680, 1360, 880, CREAM, tn), pop(OF.bolt(), 660, 780, h=140, t=tn + 0.2),
           text("next video", 1010, 750, 42, PURPLE, tn + 0.3, "c"), text("the electrical system", 1010, 830, 52, GOLD_T, tn + 0.9, "c")]

    def fx(crop, ctx, t):
        OP.fx(crop, ctx, t, [], [], glows)
        d = ImageDraw.Draw(crop)
        for pts, ta, tb2, col in flows:
            if ta <= t <= tb2:
                L = B.partial_pts  # noqa
                gap, speed = 0.11, 0.18
                ph = ((t - ta) * speed) % gap
                u = ph
                while u <= 1.0:
                    p = B.partial_pts(pts, u)[-1]
                    cx, cy = ctx.px(p)
                    r = 11 * B.BS
                    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=(255, 255, 255), width=int(3 * B.BS))
                    u += gap
    bd.fx.append(fx)
    bd.total = t0
    bd.pops = pops
    return bd, sc


def render(out="heart_physiology.mp4"):
    import subprocess
    import render_ecg as RE
    bd, sc = build()
    vid = HERE / "hp_video_only.mp4"
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
            OF.credit(bd.frame(t)).save(HERE / f"p_{t:06.1f}.png")
        print("ok", round(bd.total, 1))
    else:
        render()
