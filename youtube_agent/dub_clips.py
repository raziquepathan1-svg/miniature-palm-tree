"""Re-voice the host's spoken intro/outro clips with the cloned voice, the same voice as the narration.

Voice conversion (speaking_test) keeps much of the original Flow voice, so it does not sound fully like the host.
Default: the clone says the clip's words and each word is moved and stretched to when the lips say it (for Flow
clips that say exactly the intended line; the video is untouched). --lipsync: the clone says the cleaned-up line at the
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


def _words(path: Path, whisper) -> list[tuple[float, float, str]]:
    segs, _ = whisper.transcribe(str(path), word_timestamps=True)
    return [(w.start, w.end, re.sub(r"[^a-z0-9']", "", w.word.lower())) for s in segs for w in (s.words or [])]


def _wsola(y: np.ndarray, src_times: np.ndarray, sr: int, hop: float = 0.01, win: float = 0.04) -> np.ndarray:
    """Time-warp without changing the pitch: output grain k (every `hop` s) comes from source time src_times[k],
    overlap-added with a small search for the best-fitting grain (WSOLA)."""
    H, N = int(hop * sr), int(win * sr)
    search = int(0.006 * sr)
    w = np.hanning(N).astype(np.float32)
    out = np.zeros(len(src_times) * H + N, np.float32)
    norm = np.zeros_like(out)
    yp = np.pad(y, (N + search, N + search))
    prev = None
    for k, t in enumerate(src_times):
        c = int(t * sr) + N + search - N // 2
        if prev is not None:  # pick the offset whose grain best continues the previous one
            best, best_d = 0, -1e9
            ref = yp[prev + H: prev + H + N]
            for d in range(-search, search + 1, 4):
                seg = yp[c + d: c + d + N]
                v = float(np.dot(ref, seg))
                if v > best_d:
                    best, best_d = d, v
            c += best
        out[k * H: k * H + N] += yp[c: c + N] * w
        norm[k * H: k * H + N] += w
        prev = c
    return out / np.maximum(norm, 1e-3)


def dtw_refine(orig: np.ndarray, new: np.ndarray, sr: int = SR) -> np.ndarray:
    """Move every syllable of `new` (the cloned voice, roughly in place) to where the same sound is in `orig`
    (the clip's own voice, which the lips follow): MFCC dynamic time warping, then a pitch-safe time warp."""
    import librosa

    hop = int(0.01 * sr)
    feats = []
    for a in (orig, new):
        m = librosa.feature.mfcc(y=a.astype(np.float32), sr=sr, n_mfcc=20, hop_length=hop, n_fft=int(0.032 * sr))[1:]
        feats.append((m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6))
    _, path = librosa.sequence.dtw(X=feats[0], Y=feats[1], global_constraints=True, band_rad=0.08)
    path = path[::-1]
    n = feats[0].shape[1]
    src = np.zeros(n)
    for i in range(n):  # for each output frame, the matching source frame
        src[i] = np.median(path[path[:, 0] == i, 1]) if np.any(path[:, 0] == i) else np.nan
    idx = np.arange(n)
    good = ~np.isnan(src)
    src = np.interp(idx, idx[good], src[good])
    src = np.convolve(np.pad(src, 4, mode="edge"), np.ones(9) / 9, "valid")  # smooth (no warbling)
    for i in range(1, n):  # never go backwards, speed between 0.5x and 2x
        src[i] = min(max(src[i], src[i - 1] + 0.5), src[i - 1] + 2.0)
    return _wsola(new.astype(np.float32), src * 0.01, sr)[: len(orig)]


def _orig_audio(clip: Path, tmp: Path) -> np.ndarray:
    wav = tmp / f"{clip.stem}_orig.wav"
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(clip), "-ac", "1", "-ar", str(SR), str(wav)],
                   check=True)
    return _read_wav(wav)


def _speaking(clip: Path, tmp: Path, n: int) -> np.ndarray:
    """0..1 per sample: 1 while the clip's own voice is heard (so the lips are moving), fading to 0 in silences.
    Keeps the new voice from sounding while the mouth is closed."""
    a = _orig_audio(clip, tmp)
    hop = int(0.02 * SR)
    rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2) + 1e-12) for i in range(0, len(a), hop)])
    on = 20 * np.log10(rms) > max(-38.0, 20 * np.log10(rms.max()) - 30)
    k = 6  # keep 0.12 s around each sound (word ends, breaths)
    on = np.convolve(on.astype(float), np.ones(2 * k + 1), "same") > 0
    gate = np.convolve(on.astype(float), np.ones(5) / 5, "same")  # soft edges
    g = np.repeat(gate, hop)[:n]
    return np.pad(g, (0, max(0, n - len(g))))


def dub_aligned(clip: Path, whisper, voice_cfg: dict, tmp: Path) -> tuple[Path, str]:
    """The cloned voice says the clip's words; each word is moved and stretched to when the lips say it.
    For Flow clips that say exactly the intended line: the lips are not touched, so they look natural."""
    import difflib

    flow = [w for w in _words(clip, whisper) if w[2]]
    text = _fix_text(" ".join(t for _, _, t in phrases(clip, whisper)))
    if not flow or not text:
        raise RuntimeError("no speech found")
    wav = tmp / f"{clip.stem}_clone.wav"
    narrate_scene(text, voice_cfg, wav)
    clone_audio = _read_wav(wav)
    clone = [w for w in _words(wav, whisper) if w[2]]
    match = difflib.SequenceMatcher(None, [w[2] for w in clone], [w[2] for w in flow], autojunk=False)
    pairs = [(a + k, b + k) for a, b, n in match.get_matching_blocks() for k in range(n)]
    if len(pairs) < max(2, len(flow) * 0.6):
        raise RuntimeError(f"the clip does not say the same words ({len(pairs)} of {len(flow)} match)")
    track = np.zeros(int((_duration(clip) + 1) * SR), np.float32)
    stretch = []
    for n, (ci, fi) in enumerate(pairs):
        nci, nfi = pairs[n + 1] if n + 1 < len(pairs) else (len(clone), len(flow))
        cs, ce = clone[ci][0], clone[nci - 1][1]  # this word plus any unmatched words after it
        fs, fe = flow[fi][0], flow[nfi - 1][1]
        piece = clone_audio[int(cs * SR):int(ce * SR) + int(0.03 * SR)]
        if len(piece) < 10 or fe <= fs:
            continue
        speed = min(1.6, max(0.6, (ce - cs) / (fe - fs)))
        piece = voice._tempo(piece, SR, speed)
        ramp = min(len(piece) // 4, int(0.008 * SR))  # tiny fades: no clicks between words
        if ramp:
            piece[:ramp] *= np.linspace(0, 1, ramp)
            piece[-ramp:] *= np.linspace(1, 0, ramp)
        a = int(fs * SR)
        piece = piece[: max(0, len(track) - a)]
        track[a:a + len(piece)] += piece
        stretch.append(speed)
    track = track[: int(_duration(clip) * SR)]
    try:  # syllable by syllable, on top of the word-by-word placement
        orig = _orig_audio(clip, tmp)
        track = dtw_refine(orig[: len(track)], track)
        track = np.pad(track, (0, max(0, int(_duration(clip) * SR) - len(track))))
    except Exception as e:
        print(f"  (fine alignment skipped: {e})")
    track = track * _speaking(clip, tmp, len(track))
    out = clip.with_name(clip.stem + "_aligned.mp4")
    voice_wav = tmp / f"{clip.stem}_aligned.wav"
    _write(voice_wav, track)
    _mux(clip, voice_wav, out)
    return out, f"{len(pairs)}/{len(flow)} words matched, speed {min(stretch):.2f}-{max(stretch):.2f}: {text}"


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
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    clips = [Path(a).resolve() for a in args] or config_clips(config)
    missing = [c for c in clips if not c.exists()]
    clips = [c for c in clips if c.exists()]
    whisper = WhisperModel("small.en", device="cpu", compute_type="int8")
    voice_cfg = config.get("voice") or {}
    notes = [f"{c.name}: not found" for c in missing]
    if "--lipsync" not in sys.argv:  # default: the cloned voice fitted word by word to the clip's own lips
        with tempfile.TemporaryDirectory() as tmp:
            for clip in clips:
                try:
                    out, said = dub_aligned(clip, whisper, voice_cfg, Path(tmp))
                    notes.append(f"{out.name}: {said}")
                except Exception as e:
                    notes.append(f"{clip.name}: FAILED {e}")
    elif clips and talking.kaggle_ready():
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
