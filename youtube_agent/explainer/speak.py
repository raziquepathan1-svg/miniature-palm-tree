"""Speak an explainer script in the owner's cloned voice (same settings as the channel config).

    python -m youtube_agent.explainer.speak hanat
Writes youtube_agent/explainer/<ep>/voice_clone/<scene>.wav (0.25 s lead, 0.55 s tail, like the sample audio).
"""
import json
import re
import sys
import wave
from pathlib import Path

import numpy as np

from .. import voice

HERE = Path(__file__).resolve().parent
CFG = {"engine": "clone", "speed": 1.1, "cfg_weight": 0.3, "exaggeration": 0.5, "fallback_voice": "am_michael"}


def main(ep: str) -> None:
    d = HERE / ep
    out = d / "voice_clone"
    out.mkdir(exist_ok=True)
    for s in json.load(open(d / "script.json")):
        parts, sr = [], 24000
        for sent in re.split(r"(?<=[.?!])\s+", s["text"].strip()):  # the clone speaks best one sentence at a time
            a, sr = voice.synthesize(sent, "am_michael", CFG["speed"], CFG)
            parts += [a, np.zeros(int(0.22 * sr))]
        audio = np.concatenate([np.zeros(int(0.25 * sr))] + parts[:-1] + [np.zeros(int(0.55 * sr))])
        with wave.open(str(out / f"{s['id']}.wav"), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
            w.writeframes((np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes())
        print(f"{ep}/{s['id']}: {len(audio) / sr:.1f}s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
