"""Re-voice the host's spoken intro/outro clips with the cloned voice, the same voice as the narration.

Voice conversion (speaking_test) keeps much of the original Flow voice, so it does not sound fully like the host.
Here the clone speaks the words itself: Whisper finds what is said, the clone says the cleaned-up line at the
normal narration pace, and LatentSync (Kaggle's free GPU, as for the talking host) moves the lips to the new
voice, so words and lips match. Without the Kaggle secrets, each phrase is fitted to the time the lips move instead.
Writes <name>_dub.mp4 next to each clip, starting just before the first word.

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

from . import talking, voice
from .editor import ffmpeg_bin
from .main import load_config
from .voice import narrate_scene

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


LEAD = 0.4  # seconds of the clip kept before the first word


def _read_wav(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32767


def _write(path: Path, audio: np.ndarray) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())


def _mux(video: Path, wav: Path, out: Path) -> None:
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(video), "-i", str(wav),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", str(out)], check=True)


def _out(clip: Path) -> Path:
    return clip.with_name(clip.stem.replace("_myvoice", "") + "_dub.mp4")


def new_voice(clip: Path, whisper, voice_cfg: dict, wav: Path) -> tuple[float, str]:
    """The cloned voice saying the clip's (cleaned-up) words at the narration pace, after LEAD s of quiet.
    Returns (second of the clip to start from, the words)."""
    said = phrases(clip, whisper)
    text = _fix_text(" ".join(t for _, _, t in said))
    if not text:
        raise RuntimeError("no speech found")
    narrate_scene(text, voice_cfg, wav)  # same speed and pauses as the narration
    ss = max(0.0, said[0][0] - LEAD)
    audio = _read_wav(wav)
    _write(wav, np.concatenate([np.zeros(int((said[0][0] - ss) * SR), np.float32), audio]))
    return ss, text


def dub_lipsync(clips: list[Path], whisper, voice_cfg: dict, workdir: Path) -> dict[Path, str]:
    """Every clip in one Kaggle run: new voice, then LatentSync moves the lips to it."""
    audio, notes, job_clips, job_ss = {}, {}, {}, {}
    for clip in clips:
        k = re.sub(r"\W", "_", clip.stem)
        wav = workdir / f"{k}.wav"
        try:
            job_ss[k], notes[clip] = new_voice(clip, whisper, voice_cfg, wav)
        except Exception as e:
            notes[clip] = f"skipped: {e}"
            continue
        audio[k], job_clips[k] = wav, clip.name
    folder = clips[0].parent.relative_to(ROOT).as_posix()
    made = talking.make_clips(audio, workdir, {"moves": folder, "moves_only": list(job_clips.values()),
                                               "any_shape": True, "job_clips": job_clips, "job_ss": job_ss})
    for clip in clips:
        k = re.sub(r"\W", "_", clip.stem)
        if k in made:
            _mux(made[k], audio[k], _out(clip))
            notes[clip] = f"lips matched, from {job_ss[k]:.1f}s: {notes[clip]}"
        elif k in audio:
            notes[clip] = f"lip-sync FAILED (kept the old version): {notes[clip]}"
    return notes


def dub(clip: Path, whisper, voice_cfg: dict) -> tuple[Path, str]:
    """Without Kaggle: each phrase fitted to the time the lips move (lips and words match less well)."""
    total = _duration(clip)
    track = np.zeros(int(total * SR) + SR, dtype=np.float32)
    said = []
    for start, end, text in phrases(clip, whisper):
        if not text:
            continue
        audio, sr = voice.synthesize(text, voice_cfg.get("voice", "am_michael"), float(voice_cfg.get("speed", 1.0)),
                                     voice_cfg)
        if sr != SR:  # resample to the track rate
            audio = np.interp(np.linspace(0, len(audio), int(len(audio) * SR / sr), endpoint=False),
                              np.arange(len(audio)), audio).astype(np.float32)
        target = max(0.3, end - start + 0.08)
        speed = min(1.45, max(1.0, len(audio) / SR / target))  # fit the time the lips move, never slower
        audio = voice._tempo(audio, SR, speed)
        a = int(start * SR)
        audio = audio[: len(track) - a]
        track[a:a + len(audio)] += audio
        said.append(f"{start:.1f}-{end:.1f}s x{speed:.2f}: {text}")
    out = _out(clip)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "voice.wav"
        _write(wav, track[: int(total * SR)])
        _mux(clip, wav, out)
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
    clips = [Path(a).resolve() for a in sys.argv[1:]] or config_clips(config)
    missing = [c for c in clips if not c.exists()]
    clips = [c for c in clips if c.exists()]
    whisper = WhisperModel("small.en", device="cpu", compute_type="int8")
    voice_cfg = config.get("voice") or {}
    notes = [f"{c.name}: not found" for c in missing]
    if clips and talking.kaggle_ready():
        with tempfile.TemporaryDirectory() as tmp:
            done = dub_lipsync(clips, whisper, voice_cfg, Path(tmp))
        notes += [f"{_out(c).name}: {n}" for c, n in done.items()]
    else:
        for clip in clips:
            out, said = dub(clip, whisper, voice_cfg)
            notes.append(f"{out.name}: {said}")
    print("\n".join(notes), flush=True)
    (ROOT / "branding/health-support-studio/avatar/speaking/dub_report.txt").write_text("\n".join(notes) + "\n")


if __name__ == "__main__":
    main()
