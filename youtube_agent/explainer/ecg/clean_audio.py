"""Replace every finished video's audio with narration only (silent intro, no pops / stings)."""
import json, subprocess, sys
from pathlib import Path
import render_ecg as RE
HERE = Path(__file__).resolve().parent
SP = HERE.parent
JOBS = [("heart_anatomy_v2.mp4", SP / "hanat2", "final_heart_anatomy.mp4"),
        ("heart_physiology.mp4", SP / "hphys", "final_heart_physiology.mp4"),
        ("heart_electrical_osmosis.mp4", SP / "ecg", "final_heart_electrical.mp4"),
        ("heart_attack.mp4", SP / "mi", "final_heart_attack.mp4"),
        ("blood_vessels.mp4", SP / "vessels", "final_blood_vessels.mp4")]
RE.intro_audio(HERE / "silent_intro.wav")
for src, ep, out in JOBS:
    lst = HERE / f"{out}.txt"
    with open(lst, "w") as fh:
        fh.write(f"file '{HERE / 'silent_intro.wav'}'\n")
        for s in json.load(open(ep / "script.json")):
            fh.write(f"file '{ep / 'audio' / (s['id'] + '.wav')}'\n")
    wav = HERE / f"{out}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "pcm_s16le", str(wav)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / src), "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", str(HERE / out)], check=True)
    v = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(HERE / src)], capture_output=True, text=True).stdout)
    a = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)], capture_output=True, text=True).stdout)
    print(out, round(v, 1), round(a, 1))
