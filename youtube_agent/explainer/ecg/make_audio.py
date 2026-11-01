import json, sys, wave
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "main"))
from youtube_agent import voice
for s in json.load(open(HERE / "script.json")):
    out = HERE / "audio" / f"{s['id']}.wav"
    if out.exists():
        continue
    audio, sr = voice.synthesize(s["text"], "am_michael", 1.0)
    audio = np.concatenate([np.zeros(int(0.25 * sr)), audio, np.zeros(int(0.55 * sr))])
    pcm = (np.clip(audio, -1, 1) * 32767).astype("<i2")
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())
    print(s["id"], round(len(audio) / sr, 1), flush=True)
