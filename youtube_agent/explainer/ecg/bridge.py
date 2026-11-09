"""Cliffhanger bridge for Shorts: ~3 s open-loop question (computer voice + card) pointing to the full video."""
import subprocess, sys, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "main"))
import package as P

QUESTIONS = {
    "heart_physiology": ["So why do the valves snap shut?", "What happens in each heartbeat?"],
    "heart_electrical": ["What if the SA node stops?", "How does this match the heart?"],
    "heart_attack": ["What happens inside the artery?", "Why is time muscle?"],
    "blood_vessels": ["Why are artery walls so thick?", "What pushes blood up your legs?"],
    "blood_pressure": ["How does your body control it?", "And what do your kidneys do?"],
    "heart_anatomy_v2": ["What keeps the valves shut?", "Why is one wall so thick?"],
}


def card(q, path, k=1):
    im = Image.new("RGB", (1080, 1920), (255, 255, 255))
    d = ImageDraw.Draw(im)
    words, lines, cur = q.upper().split(), [], ""
    for w in words:
        if len(cur + " " + w) > 15:
            lines.append(cur.strip()); cur = w
        else:
            cur += " " + w
    lines.append(cur.strip())
    y = 820 - 60 * len(lines)
    for ln in lines:
        P.btext(d, (540, y), ln, 96, (98, 25, 49), "mm"); y += 120
    d.rounded_rectangle((100, 1130, 980, 1250), radius=60, fill=(255, 30, 39))   # owner (9 Nov): give a REASON to click + subscribe
    if k == 0:   # 12 PM Short -> full video at 3:30 PM
        d.text((540, 1190), "FULL ANSWER IN TODAY'S VIDEO", font=P.f(46), fill=(255, 255, 255), anchor="mm", stroke_width=2, stroke_fill=(255, 255, 255))
        d.text((540, 1310), "TODAY 3:30 PM, STEP BY STEP", font=P.f(40), fill=(98, 25, 49), anchor="mm")
    else:        # 9 PM Short -> the full video is already out
        d.text((540, 1190), "FULL ANSWER IN THE VIDEO", font=P.f(46), fill=(255, 255, 255), anchor="mm", stroke_width=2, stroke_fill=(255, 255, 255))
        d.text((540, 1310), "LIVE NOW, STEP BY STEP", font=P.f(40), fill=(98, 25, 49), anchor="mm")
    d.rounded_rectangle((160, 1400, 920, 1510), radius=55, fill=(98, 25, 49))
    d.text((540, 1455), "SUBSCRIBE: NEW BODY EXPLAINER DAILY", font=P.f(34), fill=(255, 255, 255), anchor="mm")
    im.save(path)


def add_bridge(short_path, eid, k):
    from youtube_agent import voice
    q = QUESTIONS[eid][k]
    tail = (" The full answer is in today's video at 3:30 PM, with step by step drawings. Subscribe for a new body explainer every day." if k == 0
            else " The full answer is in our video, live now, with step by step drawings. Subscribe for a new body explainer every day.")
    audio, sr = voice.synthesize(q + tail, "am_michael", 1.1)
    audio = np.concatenate([np.zeros(int(0.15 * sr)), audio, np.zeros(int(0.4 * sr))])
    wav = HERE / "_bridge.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes())
    png = HERE / "_bridge.png"
    card(q, png, k)
    tail = HERE / "_bridge.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-i", str(png), "-i", str(wav), "-shortest",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "1", str(tail)], check=True)
    out = short_path.with_suffix(".tmp.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(short_path), "-i", str(tail), "-filter_complex",
                    "[0:v]fps=30,format=yuv420p[a];[1:v]fps=30,format=yuv420p[b];[0:a]aresample=48000,aformat=channel_layouts=mono[x];"
                    "[1:a]aresample=48000,aformat=channel_layouts=mono[y];[a][x][b][y]concat=n=2:v=1:a=1[v][au]",
                    "-map", "[v]", "-map", "[au]", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "aac", "-b:a", "160k",
                    "-movflags", "+faststart", str(out)], check=True)
    out.replace(short_path)
