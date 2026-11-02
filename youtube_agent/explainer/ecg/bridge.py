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


def card(q, path):
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
    d.rounded_rectangle((140, 1180, 940, 1300), radius=60, fill=(255, 30, 39))
    d.text((540, 1240), "FULL ANSWER IN THE VIDEO", font=P.f(48), fill=(255, 255, 255), anchor="mm", stroke_width=2, stroke_fill=(255, 255, 255))
    d.text((540, 1380), "LINK ON SCREEN", font=P.f(44), fill=(98, 25, 49), anchor="mm")
    im.save(path)


def add_bridge(short_path, eid, k):
    from youtube_agent import voice
    q = QUESTIONS[eid][k]
    audio, sr = voice.synthesize(q + " Watch the full video, link on screen.", "am_michael", 1.1)
    audio = np.concatenate([np.zeros(int(0.15 * sr)), audio, np.zeros(int(0.4 * sr))])
    wav = HERE / "_bridge.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes())
    png = HERE / "_bridge.png"
    card(q, png)
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
