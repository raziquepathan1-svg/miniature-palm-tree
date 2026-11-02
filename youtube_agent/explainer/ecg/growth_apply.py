"""Apply the owner's growth rules to every queued video that is not on YouTube yet:
no logo intro (cut the first 3.6 s), curiosity titles, dark glowing thumbnails, chapters from 0:00."""
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import package as P

HERE = Path(__file__).resolve().parent
REPO = P.SP / "main" / "explainer_queue"
NAVY0, NAVY1 = (8, 16, 38), (22, 46, 98)

NEW = {
    "heart_physiology": ("Why Does Your Heart Go 'Lub-Dub'? Heart Physiology & Cardiac Cycle Explained",
                         ("LUB-DUB", "SECRET"), "heart_section", (90, 150, 255)),
    "heart_electrical": ("What Makes Your Heart Beat? The Heart's Electrical System Explained (SA Node to ECG)",
                         ("THE HEART'S", "SPARK"), "heart_section", (255, 215, 0)),
    "heart_attack": ("What Happens During a Heart Attack? Inside Your Heart, Step by Step",
                     ("TIME IS", "MUSCLE"), "atherome", (255, 30, 39)),
    "blood_vessels": ("Arteries vs Veins: Why Are They Built So Differently? (Blood Vessels Explained)",
                      ("THICK", "vs THIN"), "Arteres_couches", (255, 30, 39)),
    "blood_pressure": ("What Does 120/80 Mean? Blood Pressure Explained (Systolic vs Diastolic)",
                       ("120/80", "DECODED"), "cuff_gauge", (255, 30, 39)),
}
KEYWORDS = {
    "heart_physiology": "Heart physiology • Cardiac cycle • Lub dub heart sounds",
    "heart_electrical": "Heart electrical system • Cardiac conduction system • SA node",
    "heart_attack": "Heart attack • Heart attack symptoms • What happens during a heart attack",
    "blood_vessels": "Blood vessels • Arteries vs veins • Capillaries",
    "blood_pressure": "Blood pressure • Systolic and diastolic • What does 120/80 mean",
}
CHAPTERS = {   # 4-6 chapters (owner's search rule): (first scene id, chapter title)
    "heart_physiology": [("hook", "Intro"), ("circuits", "Two circulations & the path of blood"), ("cycle", "Cardiac cycle: systole & diastole"),
                         ("pressure", "Why valves close & the lub-dub sound"), ("output", "Cardiac output & summary")],
    "heart_electrical": [("hook", "What makes your heart beat?"), ("sa", "SA node: the natural pacemaker"),
                         ("av", "AV node, bundle of His & Purkinje fibers"), ("backup", "Backup pacemakers & the ECG"), ("nerves", "Heart rate control & summary")],
    "heart_attack": [("hook", "Intro & the coronary arteries"), ("plaque", "Plaque, clot & why time is muscle"), ("symptoms", "Heart attack warning signs"),
                     ("act", "What to do & treatment"), ("arrest", "Heart attack vs cardiac arrest & risk factors")],
    "blood_vessels": [("hook", "Arteries, capillaries & veins"), ("wall", "Vessel wall layers & arteries"), ("capillaries", "Capillary exchange"),
                      ("veins", "Veins & vein valves"), ("exception", "The pulmonary exception & summary")],
    "blood_pressure": [("hook", "What does 120/80 mean?"), ("systolic", "Systolic vs diastolic"), ("measure", "How it's measured & normal ranges"),
                       ("formula", "How your body controls blood pressure"), ("summary", "Summary")],
}


def dark_thumb(img_name, words, glow, path):
    W, H = 1280, 720
    y, x = np.mgrid[0:H, 0:W]
    r = np.clip(np.sqrt(((x - W * 0.3) / W) ** 2 + ((y - H * 0.5) / H) ** 2) / 0.8, 0, 1)[..., None]
    im = Image.fromarray((np.array(NAVY1) * (1 - r) + np.array(NAVY0) * r).astype("uint8"), "RGB").convert("RGBA")
    pic = P.sv(img_name)
    pic.thumbnail((620, 660), Image.LANCZOS)
    px, py = 30 + (620 - pic.width) // 2, (H - pic.height) // 2
    halo = Image.new("RGBA", im.size, (0, 0, 0, 0))
    mask = pic.getchannel("A").filter(ImageFilter.MaxFilter(25))
    g = Image.new("RGBA", pic.size, glow + (0,))
    g.putalpha(mask.point(lambda v: int(v * 0.85)))
    halo.paste(g, (px, py), g)
    im.alpha_composite(halo.filter(ImageFilter.GaussianBlur(28)))
    im.alpha_composite(pic, (px, py))
    d = ImageDraw.Draw(im)
    a_, b_ = words
    s1 = 104 if len(a_) <= 8 else 84
    s2 = 120 if len(b_) <= 8 else 96
    for txt, yy, size, col in ((a_, 270, s1, (255, 255, 255)), (b_, 400, s2, (255, 215, 0))):
        d.text((975, yy), txt, font=P.f(size), fill=col, anchor="mm", stroke_width=max(3, size // 18), stroke_fill=col)
    d.text((975, 640), "THE ANATOMY UNFOLDED", font=P.f(30), fill=(150, 170, 210), anchor="mm")
    im.convert("RGB").save(path, quality=92)


def main():
    P.INTRO = 0.0
    q = json.load(open(REPO / "queue.json"))
    eps = {e["id"]: e for e in P.EPISODES}
    for eid, (title, words, img, glow) in NEW.items():
        items = [x for x in q if x["id"] == eid]
        if not items or items[0].get("youtube_id"):
            print("skip (already on YouTube or not queued):", eid)
            continue
        main_item = items[0]
        src = REPO / main_item["file"]
        tmp = HERE / f"_trim_{eid}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "3.6", "-i", str(src), "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(tmp)], check=True)
        tmp.replace(src)
        thumb = REPO / f"{eid}_thumb.jpg"
        dark_thumb(img, words, glow, thumb)
        ep = eps.get(eid)
        if ep is None:
            import add_bp  # noqa: F401  (defines the blood pressure episode in P.EPISODES)
            ep = [e for e in P.EPISODES if e["id"] == eid][0]
        st = {i: t for i, t, _ in P.scene_times(ep)}
        chap = "\n".join(f"{P.stamp(0 if n == 0 else st[i])} {name}" for n, (i, name) in enumerate(CHAPTERS[eid]))
        main_item["title"] = title
        main_item["thumbnail"] = thumb.name
        main_item["description"] = f"{KEYWORDS[eid]}\n\n{ep['about']}\n\nCHAPTERS\n{chap}\n{P.FOOTER}"
        for x in q:
            if x["id"].startswith(eid + "_short"):
                x["description"] = f"{ep['about']}\n\nFull video: \"{title}\" on The Anatomy Unfolded.\n{P.FOOTER} #shorts"
        print("updated", eid, "|", title)
    json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
