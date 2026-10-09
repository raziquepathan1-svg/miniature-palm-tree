"""Re-voice the host's spoken intro/outro clips with the cloned voice, the same voice as the narration.

Voice conversion (speaking_test) keeps much of the original Flow voice, so it does not sound fully like the host.
Here the clone speaks the words itself instead: Whisper finds what is said and when, the clone speaks each
phrase, the phrase is fitted to the time the lips move, and the new sound replaces the old one.
Writes <name>_dub.mp4 next to each clip (the video is copied unchanged).

Runs in the "Intro/outro in your cloned voice" workflow (needs VOICE_SAMPLE and faster-whisper).
    python -m youtube_agent.dub_clips                 # every intro/outro clip in config.yaml
    python -m youtube_agent.dub_clips path/clip.mp4   # just these clips
"""

import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

from . import voice
from .editor import ffmpeg_bin
from .main import load_config

ROOT = Path(__file__).resolve().parent.parent
SR = 24000
GAP = 0.35  # a pause longer than this between words starts a new phrase


def _fix_text(text: str) -> str:
    """Clean up the transcript: the channel name, and words Flow said twice in a row."""
    text = re.sub(r"health\s+support(\s+support)*\s+studio", "Health Support Studio", text, flags=re.I)
    for _ in range(3):  # "welcome back to welcome back to" -> "welcome back to"
        text = re.sub(r"\b(\w+(?:[\s,]+\w+){0,3})[\s,.]+\1\b", r"\1", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()


def phrases(clip: Path, whisper) -> list[tuple[float, float, str]]:
    """[(start, end, text)] of what is said in the clip, split at pauses."""
    segs, _ = whisper.transcribe(str(clip), word_timestamps=True)
    words = [w for s in segs for w in (s.words or [])]
    out, cur = [], []
    for w in words:
        if cur and w.start - cur[-1].end > GAP:
            out.append(cur)
            cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return [(p[0].start, p[-1].end, _fix_text(" ".join(w.word.strip() for w in p))) for p in out]


def _duration(path: Path) -> float:
    err = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def dub(clip: Path, whisper, voice_cfg: dict) -> tuple[Path, str]:
    total = _duration(clip)
    track = np.zeros(int(total * SR) + SR, dtype=np.float32)
    said = []
    for start, end, text in phrases(clip, whisper):
        if not text:
            continue
        audio, sr = voice.synthesize(text, voice_cfg.get("voice", "am_michael"), 1.0, voice_cfg)
        if sr != SR:  # resample to the track rate
            audio = np.interp(np.linspace(0, len(audio), int(len(audio) * SR / sr), endpoint=False),
                              np.arange(len(audio)), audio).astype(np.float32)
        target = max(0.3, end - start + 0.08)
        speed = min(1.45, max(0.75, len(audio) / SR / target))  # fit the time the lips move
        audio = voice._tempo(audio, SR, speed)
        a = int(start * SR)
        audio = audio[: len(track) - a]
        track[a:a + len(audio)] += audio
        said.append(f"{start:.1f}-{end:.1f}s x{speed:.2f}: {text}")
    out = clip.with_name(clip.stem.replace("_myvoice", "") + "_dub.mp4")
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "voice.wav"
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((np.clip(track, -1, 1) * 32767).astype(np.int16).tobytes())
        subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(clip), "-i", str(wav),
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5",
                        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-t", f"{total:.3f}", str(out)], check=True)
    return out, " | ".join(said)


def config_clips(config: dict) -> list[Path]:
    clips = []
    for key in ("intro", "outro"):
        cfg = (config["video"].get("host_clips") or {}).get(key)
        for c in cfg if isinstance(cfg, list) else [cfg] if cfg else []:
            clips.append(ROOT / c["file"])
    return clips


def main() -> None:
    from faster_whisper import WhisperModel

    config = load_config()
    clips = [Path(a) for a in sys.argv[1:]] or config_clips(config)
    whisper = WhisperModel("small.en", device="cpu", compute_type="int8")
    notes = []
    for clip in clips:
        if not clip.exists():
            notes.append(f"{clip.name}: not found")
            continue
        out, said = dub(clip, whisper, config.get("voice") or {})
        notes.append(f"{out.name}: {said}")
        print(notes[-1], flush=True)
    (ROOT / "branding/health-support-studio/avatar/speaking/dub_report.txt").write_text("\n".join(notes) + "\n")


if __name__ == "__main__":
    main()
