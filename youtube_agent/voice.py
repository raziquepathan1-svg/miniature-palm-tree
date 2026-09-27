"""Free AI narration with Kokoro TTS (Apache-2.0, commercial use allowed, runs on CPU).

Produces one WAV per scene plus caption timings, so subtitles line up with the voice.
"""

import os
import re
import wave
from pathlib import Path

import numpy as np
import requests

MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
MODEL_DIR = Path(os.environ.get("KOKORO_DIR", Path.home() / ".cache" / "kokoro"))

SENTENCE_PAUSE = 0.30  # seconds of silence after each sentence
SCENE_TAIL = 0.50      # extra silence at the end of each scene
CAPTION_MAX_WORDS = 7  # words per on-screen caption

_kokoro = None


def _download(url: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  Downloading voice model {dest.name} (one time)...")
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    tmp.rename(dest)


def _engine():
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro

        model, voices = MODEL_DIR / "kokoro-v1.0.onnx", MODEL_DIR / "voices-v1.0.bin"
        _download(MODEL_URL, model)
        _download(VOICES_URL, voices)
        _kokoro = Kokoro(str(model), str(voices))
    return _kokoro


def list_voices() -> list[str]:
    return sorted(_engine().get_voices())


def synthesize(text: str, voice: str, speed: float) -> tuple[np.ndarray, int]:
    """Return mono float32 audio for one sentence."""
    return _engine().create(text, voice=voice, speed=speed, lang="en-us")


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _caption_chunks(sentence: str) -> list[str]:
    words = sentence.split()
    return [" ".join(words[i:i + CAPTION_MAX_WORDS]) for i in range(0, len(words), CAPTION_MAX_WORDS)]


def narrate_scene(text: str, voice_cfg: dict, out_wav: Path) -> tuple[float, list[tuple[float, float, str]]]:
    """Speak one scene. Returns (duration_seconds, [(start, end, caption_text), ...])."""
    voice = voice_cfg.get("voice", "af_heart")
    speed = float(voice_cfg.get("speed", 1.0))

    pieces: list[np.ndarray] = []
    captions: list[tuple[float, float, str]] = []
    t = 0.0
    sample_rate = 24000
    for sentence in split_sentences(text):
        audio, sample_rate = synthesize(sentence, voice, speed)
        dur = len(audio) / sample_rate
        # Spread the sentence's time over its caption chunks by length
        chunks = _caption_chunks(sentence)
        total_chars = sum(len(c) for c in chunks) or 1
        start = t
        for c in chunks:
            end = start + dur * len(c) / total_chars
            captions.append((start, end, c))
            start = end
        pieces += [audio.astype(np.float32), np.zeros(int(SENTENCE_PAUSE * sample_rate), np.float32)]
        t += dur + SENTENCE_PAUSE
    pieces.append(np.zeros(int(SCENE_TAIL * sample_rate), np.float32))
    audio = np.concatenate(pieces) if pieces else np.zeros(sample_rate, np.float32)

    _write_wav(out_wav, audio, sample_rate)
    return len(audio) / sample_rate, captions


def _write_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm.tobytes())
