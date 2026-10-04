"""Free AI narration: Kokoro TTS (Apache-2.0, runs on CPU) or a clone of your own voice (Chatterbox, MIT).

Produces one WAV per scene plus caption timings, so subtitles line up with the voice.

Your voice: set `voice: {engine: clone}` in config.yaml. The workflow decrypts voice/voice_sample.wav.enc with
the VOICE_KEY secret into VOICE_SAMPLE; Chatterbox then speaks in that voice. If anything about the clone
fails (no key, model download, out of memory), the Kokoro voice is used so the video still gets made.
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
_clone = None
_clone_failed = False
_vc = None
_vc_failed = False


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


def _clone_engine(voice_cfg: dict):
    """Chatterbox, conditioned once on your voice sample; None if it can't be used (Kokoro is used instead)."""
    global _clone, _clone_failed
    if _clone_failed:
        return None
    if _clone is not None:
        return _clone
    sample = os.environ.get("VOICE_SAMPLE", "")
    if not sample or not Path(sample).exists():
        print("  (Voice clone: no voice sample - is the VOICE_KEY secret set? Using the standard AI voice.)")
        _clone_failed = True
        return None
    try:
        import torch
        from chatterbox.tts import ChatterboxTTS

        torch.set_num_threads(os.cpu_count() or 4)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"  Loading your cloned voice ({device})...")
        model = ChatterboxTTS.from_pretrained(device=device)
        model.prepare_conditionals(sample, exaggeration=float(voice_cfg.get("exaggeration", 0.5)))
        _clone = model
    except Exception as e:  # never lose a video over the voice
        print(f"  (Voice clone unavailable, using the standard AI voice: {e})")
        _clone_failed = True
    return _clone


def _convert_engine():
    """Chatterbox voice conversion: turns any speech into your voice, keeping its accent and timing."""
    global _vc, _vc_failed
    if _vc_failed:
        return None
    if _vc is not None:
        return _vc
    sample = os.environ.get("VOICE_SAMPLE", "")
    try:
        if not sample or not Path(sample).exists():
            raise RuntimeError("no voice sample - is the VOICE_KEY secret set?")
        import torch
        from chatterbox.vc import ChatterboxVC

        torch.set_num_threads(os.cpu_count() or 4)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"  Loading the voice converter ({device})...")
        _vc = ChatterboxVC.from_pretrained(device=device)
        _vc.set_target_voice(sample)
    except Exception as e:
        print(f"  (Voice conversion unavailable, keeping the standard AI voice: {e})")
        _vc_failed = True
    return _vc


def convert_file(wav_path: Path) -> bool:
    """Re-speak a finished WAV in your voice (same length, so caption timings stay right)."""
    vc = _convert_engine()
    if vc is None:
        return False
    try:
        import torch

        with torch.inference_mode():
            wav = vc.generate(str(wav_path))
        audio = wav.squeeze(0).cpu().numpy().astype(np.float32)
        peak = float(np.abs(audio).max() or 1.0)
        _write_wav(wav_path, audio * min(1.0, 0.95 / peak), vc.sr)
        return True
    except Exception as e:
        print(f"  (Voice conversion failed for this scene, keeping the standard AI voice: {e})")
        return False


def _trim(audio: np.ndarray, sample_rate: int, keep: float = 0.04) -> np.ndarray:
    """Cut the silence the clone leaves before and after each sentence (the pause is added separately)."""
    loud = np.flatnonzero(np.abs(audio) > 0.02)
    if not len(loud):
        return audio
    pad = int(keep * sample_rate)
    return audio[max(0, loud[0] - pad):loud[-1] + pad]


def _tempo(audio: np.ndarray, sample_rate: int, speed: float) -> np.ndarray:
    """Faster or slower speech without changing the pitch (ffmpeg atempo)."""
    if abs(speed - 1.0) < 0.01:
        return audio
    import subprocess
    import tempfile

    from .editor import ffmpeg_bin

    with tempfile.TemporaryDirectory() as tmp:
        src, dst = Path(tmp) / "in.wav", Path(tmp) / "out.wav"
        _write_wav(src, audio, sample_rate)
        subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(src), "-af", f"atempo={speed:.3f}",
                        str(dst)], check=True)
        with wave.open(str(dst), "rb") as w:
            pcm = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return pcm.astype(np.float32) / 32767


def synthesize(text: str, voice: str, speed: float, voice_cfg: dict | None = None) -> tuple[np.ndarray, int]:
    """Return mono float32 audio for one sentence."""
    voice_cfg = voice_cfg or {}
    if voice_cfg.get("engine") == "clone":
        model = _clone_engine(voice_cfg)
        if model is not None:
            import torch

            try:
                with torch.inference_mode():
                    wav = model.generate(text, exaggeration=float(voice_cfg.get("exaggeration", 0.5)),
                                         cfg_weight=float(voice_cfg.get("cfg_weight", 0.3)),
                                         temperature=float(voice_cfg.get("temperature", 0.8)))
                audio = _trim(wav.squeeze(0).cpu().numpy().astype(np.float32), model.sr)
                return _tempo(audio, model.sr, speed), model.sr  # 24 kHz, same as Kokoro
            except Exception as e:
                global _clone_failed
                print(f"  (Voice clone failed on a sentence, using the standard AI voice from here: {e})")
                _clone_failed = True
        voice = voice_cfg.get("fallback_voice", "af_heart")
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
    if voice_cfg.get("engine") == "convert":  # American voice first, then turned into your voice
        voice = voice_cfg.get("base_voice", "am_michael")

    pause = float(voice_cfg.get("pause", 0.18 if voice_cfg.get("engine") == "clone" else SENTENCE_PAUSE))
    pieces: list[np.ndarray] = []
    captions: list[tuple[float, float, str]] = []
    t = 0.0
    sample_rate = 24000
    for sentence in split_sentences(text):
        audio, sample_rate = synthesize(sentence, voice, speed, voice_cfg)
        dur = len(audio) / sample_rate
        # Spread the sentence's time over its caption chunks by length
        chunks = _caption_chunks(sentence)
        total_chars = sum(len(c) for c in chunks) or 1
        start = t
        for c in chunks:
            end = start + dur * len(c) / total_chars
            captions.append((start, end, c))
            start = end
        pieces += [audio.astype(np.float32), np.zeros(int(pause * sample_rate), np.float32)]
        t += dur + pause
    pieces.append(np.zeros(int(SCENE_TAIL * sample_rate), np.float32))
    audio = np.concatenate(pieces) if pieces else np.zeros(sample_rate, np.float32)

    _write_wav(out_wav, audio, sample_rate)
    if voice_cfg.get("engine") == "convert":
        convert_file(out_wav)
    return len(audio) / sample_rate, captions


def _write_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm.tobytes())
