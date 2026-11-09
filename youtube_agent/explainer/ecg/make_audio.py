"""Narration for one episode: Kokoro am_michael, speed 1.1, one sentence at a time (EP_DIR = episode folder)."""
import json, os, re, sys, wave
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
EP = Path(os.environ.get("EP_DIR", str(HERE)))
sys.path.insert(0, str(HERE.parents[2]))  # repo root
from youtube_agent import voice
(EP / "audio").mkdir(exist_ok=True)
for s in json.load(open(EP / "script.json")):
    out = EP / "audio" / f"{s['id']}.wav"
    if out.exists():
        continue
    parts, sr = [], 24000
    for sent in re.split(r"(?<=[.?!])\s+", s["text"].strip()):
        a, sr = voice.synthesize(sent, "am_michael", 1.1)
        parts += [a, np.zeros(int(0.22 * sr))]
    audio = np.concatenate([np.zeros(int(0.25 * sr))] + parts[:-1] + [np.zeros(int(0.55 * sr))])
    pcm = (np.clip(audio, -1, 1) * 32767).astype("<i2")
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())
    print(s["id"], round(len(audio) / sr, 1), flush=True)
