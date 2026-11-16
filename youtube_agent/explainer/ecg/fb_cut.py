"""Facebook/Instagram cut of a Short (owner, 16 Nov 2026: FB gets no views/followers).

Why: the YouTube Short ends with a YouTube-only card + voice ("subscribe", "today's video at 3:30 PM") that
Facebook/Instagram viewers cannot act on, and most people watch Reels muted but our Reels had no captions.
This cut: (1) drops the YouTube ending, (2) burns big captions into the empty space under the picture,
(3) ends with a short FB/IG-native card + voice: "Follow The Anatomy Unfolded...".
    python3 fb_cut.py <queue_id> [<queue_id> ...]     -> explainer_queue/<file stem>_fb.mp4
"""
import json, re, subprocess, sys, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
QDIR = REPO / "explainer_queue"
sys.path.insert(0, str(HERE.parent / "main"))
sys.path.insert(0, str(REPO))
import package as P

MAROON = (98, 25, 49)
TMP = HERE / "_fb"


def wav_dur(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def chunks_for(text, t0, dur):
    """sentence-level timing like make_audio (0.25 s lead, 0.22 s gaps, 0.55 s tail), split into <=5-word captions."""
    sents = [s for s in re.split(r"(?<=[.?!])\s+", text.strip()) if s]
    speech = max(0.5, dur - 0.8 - 0.22 * (len(sents) - 1))
    tot = sum(len(s) for s in sents)
    out, t = [], t0 + 0.25
    for s in sents:
        sd = speech * len(s) / tot
        words = s.split()
        groups = [words[i:i + 5] for i in range(0, len(words), 5)]
        if len(groups) > 1 and len(groups[-1]) <= 2:
            last_ = groups.pop(); groups[-1] += last_
        gc = sum(len(" ".join(g)) for g in groups)
        tt = t
        for g in groups:
            gd = sd * len(" ".join(g)) / gc
            out.append((" ".join(g), tt, tt + gd))
            tt += gd
        t += sd + 0.22
    return out


def wrap(text, n=16):
    lines, cur = [], ""
    for w in text.upper().split():
        if cur and len(cur + " " + w) > n:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur] if cur else lines


def base_png(path):
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 1264, 1080, 1920), fill=(255, 255, 255, 255))      # hide the YouTube-only pill / name
    d.rounded_rectangle((150, 1770, 930, 1860), radius=45, fill=MAROON)
    d.text((540, 1815), "FOLLOW FOR DAILY BODY STORIES", font=P.f(36), fill=(255, 255, 255), anchor="mm")
    im.save(path)


def cap_png(text, path):
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lines = wrap(text)
    size = 78 if len(lines) <= 2 else 64
    y = 1480 - (len(lines) - 1) * (size + 14) / 2
    for ln in lines:
        P.btext(d, (540, int(y)), ln, size, MAROON, "mm")
        y += size + 14
    im.save(path)


def tail_clip(title, path):
    from youtube_agent import voice
    a, sr = voice.synthesize("Follow The Anatomy Unfolded for a new body story every day.", "am_michael", 1.1)
    a = np.concatenate([np.zeros(int(0.15 * sr)), a, np.zeros(int(0.5 * sr))])
    wv = TMP / "tail.wav"
    with wave.open(str(wv), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(a, -1, 1) * 32767).astype("<i2").tobytes())
    im = Image.new("RGB", (1080, 1920), (255, 255, 255))
    d = ImageDraw.Draw(im)
    y = 700
    for ln in wrap(title, 14):
        P.btext(d, (540, y), ln, 96, MAROON, "mm"); y += 120
    d.rounded_rectangle((120, 1080, 960, 1210), radius=65, fill=(24, 119, 242))
    d.text((540, 1145), "FOLLOW", font=P.f(64), fill=(255, 255, 255), anchor="mm", stroke_width=2, stroke_fill=(255, 255, 255))
    d.text((540, 1300), "A NEW BODY STORY EVERY DAY", font=P.f(44), fill=MAROON, anchor="mm")
    d.text((540, 1600), "THE ANATOMY UNFOLDED", font=P.f(46), fill=(150, 120, 130), anchor="mm")
    png = TMP / "tail.png"
    im.save(png)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-i", str(png), "-i", str(wv), "-shortest",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "1", str(path)], check=True)


def make(qid):
    q = {x["id"]: x for x in json.load(open(QDIR / "queue.json"))}[qid]
    eid, n = qid.split("_short")
    sdir = HERE.parent / eid / f"short{n}"
    scr = json.load(open(sdir / "script.json"))
    TMP.mkdir(exist_ok=True)
    caps, t = [], 0.0
    for s in scr:
        d = wav_dur(sdir / "audio" / f"{s['id']}.wav")
        caps += chunks_for(s["text"], t, d)
        t += d
    board_dur = t
    base = TMP / "base.png"
    base_png(base)
    ins, filt, last = ["-i", str(base)], "[0:v][1:v]overlay=0:0[v0]", "v0"
    for i, (txt, a, b) in enumerate(caps):
        p = TMP / f"c{i}.png"
        cap_png(txt, p)
        ins += ["-i", str(p)]
        filt += f";[{last}][{i + 2}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[v{i + 1}]"
        last = f"v{i + 1}"
    main = TMP / "main.mp4"
    src = QDIR / q["file"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-t", f"{board_dur:.2f}", "-i", str(src), *ins, "-filter_complex", filt, "-map", f"[{last}]", "-map", "0:a",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "1", str(main)], check=True)
    tail = TMP / "tail.mp4"
    tail_clip(q["title"].replace(" #Shorts", ""), tail)
    out = QDIR / (Path(q["file"]).stem + "_fb.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(main), "-i", str(tail), "-filter_complex",
                    "[0:v]fps=30,format=yuv420p[a];[1:v]fps=30,format=yuv420p[b];[0:a]aresample=48000[x];[1:a]aresample=48000[y];[a][x][b][y]concat=n=2:v=1:a=1[v][au]",
                    "-map", "[v]", "-map", "[au]", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)], check=True)
    print("done ->", out.name, f"{board_dur:.1f}s + tail")


if __name__ == "__main__":
    for qid in sys.argv[1:]:
        make(qid)
