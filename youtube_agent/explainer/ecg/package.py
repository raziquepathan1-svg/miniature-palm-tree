"""Make thumbnails, Shorts and upload metadata for the cardiovascular series, and write the publish queue."""
import datetime as dt
import json
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SP = HERE.parent
SV = SP / "servier"
OUT = SP / "queue"
OUT.mkdir(exist_ok=True)
SC = "/root/.cache/yt-agent-fonts/PatrickHandSC.ttf"
MAROON, RED, BLUE, GOLD, PURPLE = (98, 25, 49), (170, 30, 50), (30, 70, 150), (150, 90, 0), (73, 36, 104)
INTRO = 3.6
REPO_Q = SP / "main" / "explainer_queue" / "queue.json"
SKIP = set(sys.argv[2:])


def sv(name):
    for sub in ("bpx", "bv", "ha", "mi", ""):
        p = SV / sub / f"{name}.png"
        if p.exists():
            return Image.open(p).convert("RGBA")
    sys.path.insert(0, str(HERE))
    import osm_preview as OP
    return OP.HEART


def f(size):
    return ImageFont.truetype(SC, size)


def btext(d, xy, s, size, col, anchor="la"):
    d.text(xy, s, font=f(size), fill=col, anchor=anchor, stroke_width=max(2, size // 22), stroke_fill=col)


def dur(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


EPISODES = [
    {"id": "heart_anatomy_v2", "focus": [0.45, 0.62], "video": HERE / "final_heart_anatomy.mp4", "dir": SP / "hanat2",
     "title": "Anatomy of the Heart: Chambers, Valves & Layers Explained",
     "thumb": ("HEART", "ANATOMY", "4 chambers • 4 valves", "coeur_09"),
     "chapters": {"hook": "Intro", "location": "Where the heart is", "wall": "3 layers of the wall & pericardium", "pumps": "Two pumps & the septum",
                  "chambers": "4 chambers", "thick": "Why the left ventricle is thickest", "valves": "4 valves: Try Pulling My Aorta",
                  "chordae": "Chordae tendineae & papillary muscles", "vessels": "Great vessels", "summary": "Remember 3 things"},
     "about": "Learn the structure of the heart: where it sits, the 3 layers of the heart wall and the pericardium, the two pumps and the septum, the 4 chambers, why the left ventricle is thickest, the 4 valves (Try Pulling My Aorta), the chordae tendineae and the great vessels.",
     "short": [(["pumps", "chambers"], "Your Heart Is Actually Two Pumps"), (["valves", "chordae"], "Remember the 4 Heart Valves")],
     "tags": ["heart anatomy", "anatomy of the heart", "heart chambers", "heart valves", "cardiac anatomy", "anatomy and physiology"]},
    {"id": "heart_physiology", "focus": [0.5, 0.5], "video": HERE / "final_heart_physiology.mp4", "dir": SP / "hphys",
     "title": "Physiology of the Heart: How Blood Flows & the Cardiac Cycle",
     "thumb": ("HOW THE HEART", "PUMPS", "systole • diastole • lub-dub", "heart_section"),
     "chapters": {"hook": "Intro", "circuits": "Pulmonary & systemic circulation", "right": "Right side blood flow", "lungs": "In the lungs",
                  "left": "Left side blood flow", "cycle": "Cardiac cycle: systole & diastole", "pressure": "Why valves open and close",
                  "lubdub": "Lub-dub heart sounds", "output": "Cardiac output", "summary": "Summary"},
     "about": "How the heart works: the pulmonary and systemic circulations, blood flow through the right and left heart, the cardiac cycle (systole and diastole), why valves open and close, the lub-dub heart sounds, and cardiac output.",
     "short": [(["pressure", "lubdub"], "Where Does the Lub-Dub Sound Come From?"), (["cycle"], "Systole vs Diastole Explained")],
     "tags": ["heart physiology", "cardiac cycle", "systole diastole", "blood flow through the heart", "heart sounds", "cardiac output"]},
    {"id": "heart_electrical", "focus": [0.42, 0.6], "video": HERE / "final_heart_electrical.mp4", "dir": SP / "ecg",
     "title": "The Heart's Electrical System Explained: SA Node to ECG",
     "thumb": ("WHO STARTS", "YOUR HEARTBEAT?", "SA node to ECG", "heart_section"),
     "chapters": {"hook": "Intro", "why": "The conduction system", "sa": "SA node: the pacemaker", "atria": "Atria contract",
                  "av": "AV node delay", "his": "Bundle of His & Purkinje fibers", "backup": "Backup pacemakers",
                  "ecg": "ECG: P, QRS and T waves", "nerves": "Nerves change the pace", "summary": "Summary"},
     "about": "How every heartbeat starts: the SA node, AV node, bundle of His, bundle branches and Purkinje fibers, backup pacemakers, what the P wave, QRS complex and T wave on an ECG mean, and how nerves change the heart rate.",
     "short": [(["sa", "atria"], "Your Heart Has Its Own Pacemaker"), (["ecg"], "What P, QRS and T Mean on an ECG")],
     "tags": ["heart electrical system", "cardiac conduction system", "SA node", "AV node", "ECG explained", "Purkinje fibers"]},
    {"id": "heart_attack", "focus": [0.38, 0.5], "video": HERE / "final_heart_attack.mp4", "dir": SP / "mi",
     "title": "Heart Attack Explained: What Happens Inside Your Heart",
     "thumb": ("HEART", "ATTACK", "what happens inside", "atherome"),
     "chapters": {"hook": "Intro", "coronary": "Coronary arteries", "plaque": "Plaque & coronary artery disease", "clot": "The clot",
                  "damage": "Time is muscle", "symptoms": "Warning signs", "act": "What to do", "treatment": "Treatment: angioplasty & stent",
                  "arrest": "Heart attack vs cardiac arrest", "summary": "Risk factors & summary"},
     "about": "What happens during a heart attack (myocardial infarction): coronary artery disease, plaque rupture and a blood clot, why time is muscle, the warning signs, what to do, how doctors open the artery, and how a heart attack differs from cardiac arrest.",
     "short": [(["symptoms", "act"], "Heart Attack Warning Signs You Should Know"), (["arrest"], "Heart Attack vs Cardiac Arrest")],
     "tags": ["heart attack", "myocardial infarction", "heart attack symptoms", "coronary artery disease", "cardiac arrest vs heart attack", "angioplasty stent"]},
    {"id": "blood_vessels", "focus": [0.4, 0.42], "video": HERE / "final_blood_vessels.mp4", "dir": SP / "vessels",
     "title": "Blood Vessels Explained: Arteries, Veins & Capillaries",
     "thumb": ("ARTERIES", "vs VEINS", "and capillaries", "Arteres_couches"),
     "chapters": {"hook": "Intro", "overview": "Arteries, capillaries & veins", "wall": "3 layers of the vessel wall", "arteries": "Arteries & the pulse",
                  "arterioles": "Arterioles: vasoconstriction & vasodilation", "capillaries": "Capillaries: where exchange happens",
                  "veins": "Veins", "valves": "Vein valves & the muscle pump", "exception": "The pulmonary exception", "summary": "Summary"},
     "about": "The three types of blood vessels: arteries, capillaries and veins. The 3 layers of the vessel wall, why arteries have thick walls, arterioles and blood pressure, capillary exchange, vein valves and the skeletal muscle pump, and why pulmonary arteries carry oxygen-poor blood.",
     "short": [(["exception"], "Arteries Don't Always Carry Oxygen-Rich Blood!"), (["capillaries"], "Capillaries: Where the Real Work Happens")],
     "tags": ["blood vessels", "arteries veins capillaries", "artery vs vein", "tunica intima media externa", "capillary exchange", "anatomy and physiology"]},
]

FOOTER = """
Part of the Cardiovascular System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Some illustrations: Servier Medical Art (smart.servier.com), licensed under CC BY 4.0.

#anatomy #physiology #medicalstudent #nursing #cardiology"""


def scene_times(ep):
    data = json.load(open(ep["dir"] / "script.json"))
    t = INTRO
    out = []
    for s in data:
        d = dur(ep["dir"] / "audio" / f"{s['id']}.wav")
        out.append((s["id"], t, d))
        t += d
    return out


def stamp(t):
    t = int(t)
    return f"{t // 60}:{t % 60:02d}"


def thumbnail(ep, path):
    a, b, c, img = ep["thumb"]
    W, H = 1280, 720
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((640, 0, W, H), radius=0, fill=(252, 236, 238))
    pic = sv(img)
    pic.thumbnail((620, 680), Image.LANCZOS)
    bg = Image.new("RGBA", pic.size, (255, 255, 255, 0))
    im.paste(pic, (20 + (620 - pic.width) // 2, (H - pic.height) // 2), pic)
    size1 = 96 if len(a) <= 10 else 74
    size2 = 120 if len(b) <= 8 else (96 if len(b) <= 12 else 78)
    btext(d, (960, 230), a, size1, MAROON, "mm")
    btext(d, (960, 360), b, size2, RED, "mm")
    d.rounded_rectangle((690, 480, 1230, 570), radius=45, fill=MAROON)
    d.text((960, 525), c.upper(), font=f(40), fill=(255, 255, 255), anchor="mm", stroke_width=1, stroke_fill=(255, 255, 255))
    d.text((960, 660), "THE ANATOMY UNFOLDED", font=f(30), fill=(150, 120, 130), anchor="mm")
    im.save(path, quality=92)


def short(ep, path, k):
    ids, title = ep["short"][k]
    sc = {i: (t, d) for i, t, d in scene_times(ep)}
    t0 = sc[ids[0]][0]
    t1 = sc[ids[-1]][0] + sc[ids[-1]][1]
    length = min(t1 - t0, 58.0)
    # Owner (2 Nov): nothing may be cut - show the WHOLE 16:9 board (1080x608), title above, link pill below.
    top = Image.new("RGBA", (1080, 1920), (255, 255, 255, 0))
    d = ImageDraw.Draw(top)
    words = title.upper().split()
    lines, cur = [], ""
    for w in words:
        if len(cur + " " + w) > 14:
            lines.append(cur.strip())
            cur = w
        else:
            cur += " " + w
    lines.append(cur.strip())
    size = 96 if len(lines) <= 3 else 80
    y = 600 - (size + 18) * len(lines) + (size + 18) // 2 - 20
    for ln in lines:
        btext(d, (540, y), ln, size, MAROON, "mm")
        y += size + 18
    d.rounded_rectangle((170, 1380, 910, 1490), radius=55, fill=MAROON)
    d.text((540, 1435), "FULL VIDEO ON THE CHANNEL", font=f(44), fill=(255, 255, 255), anchor="mm", stroke_width=1, stroke_fill=(255, 255, 255))
    d.text((540, 1600), "THE ANATOMY UNFOLDED", font=f(46), fill=(150, 120, 130), anchor="mm")
    ov = OUT / f"{ep['id']}_short{k}_overlay.png"
    top.save(ov)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.2f}", "-t", f"{length:.2f}", "-i", str(ep["video"]), "-i", str(ov),
                    "-filter_complex", f"color=white:s=1080x1920:r=30[bg];[0:v]scale=1080:608[v];[bg][v]overlay=0:656:shortest=1[b];[b][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                    str(path)], check=True)
    ov.unlink()
    return title


def main(start_date):
    queue = []
    day = dt.date.fromisoformat(start_date)
    for i, ep in enumerate(EPISODES):
        if not ep["video"].exists() or ep["id"] in SKIP:
            print(f"not ready yet: {ep['id']}")
            continue
        when = dt.datetime.combine(day + dt.timedelta(days=i), dt.time(12, 30), dt.timezone.utc)  # 18:00 IST
        vid = OUT / f"{ep['id']}.mp4"
        subprocess.run(["cp", str(ep["video"]), str(vid)], check=True)
        thumb = OUT / f"{ep['id']}_thumb.jpg"
        thumbnail(ep, thumb)
        print("packaging", ep["id"], flush=True)

        chap = "\n".join(["0:00 Intro"] + [f"{stamp(t)} {ep['chapters'][i_]}" for i_, t, _ in scene_times(ep)[1:]])
        desc = f"{ep['about']}\n\nCHAPTERS\n{chap}\n{FOOTER}"
        queue.append({"id": ep["id"], "kind": "video", "file": vid.name, "thumbnail": thumb.name, "title": ep["title"],
                      "description": desc, "tags": ep["tags"] + ["the anatomy unfolded"], "playlist": "Cardiovascular System",
                      "publish_at": when.strftime("%Y-%m-%dT%H:%M:%SZ"), "youtube_id": None})
        # 2 Shorts a day: 12:00 PM and 9:00 PM India time (06:30 / 15:30 UTC); the long video is at 6 PM
        for k, hh in ((0, (6, 30)), (1, (15, 30))):
            sh = OUT / f"{ep['id']}_short{k + 1}.mp4"
            stitle = short(ep, sh, k)
            st = dt.datetime.combine(day + dt.timedelta(days=i), dt.time(*hh), dt.timezone.utc)
            queue.append({"id": f"{ep['id']}_short{k + 1}", "kind": "short", "file": sh.name, "thumbnail": None,
                          "title": f"{stitle} #Shorts",
                          "description": f"{ep['about']}\n\nFull video: \"{ep['title']}\" on The Anatomy Unfolded.\n{FOOTER} #shorts",
                          "tags": ep["tags"] + ["shorts"], "playlist": None,
                          "publish_at": st.strftime("%Y-%m-%dT%H:%M:%SZ"), "youtube_id": None})
            print(ep["id"], st, stitle)
    old = {q["id"]: q for q in json.load(open(REPO_Q))} if REPO_Q.exists() else {}
    for q in queue:  # keep what is already on YouTube
        if q["id"] in old and old[q["id"]].get("youtube_id"):
            q.update(old[q["id"]])
    json.dump(queue, open(OUT / "queue.json", "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "thumbs":
        for ep in EPISODES:
            thumbnail(ep, OUT / f"{ep['id']}_thumb.jpg")
    else:
        main(sys.argv[1])
