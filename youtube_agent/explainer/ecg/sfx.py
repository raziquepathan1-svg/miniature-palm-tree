"""Synthesized sound design for The Anatomy Unfolded (no copyrighted audio).

mix(bd, voice_wav, out_wav, offset, cues) adds: pops when pictures appear, soft marker scratch while text is
written, whooshes on camera moves, a quiet music bed, and per-scene physiological sounds (heartbeat, blood flow,
electrical hum). cues = list of (t0, t1, kind) in board time, kind in {"heartbeat", "flow", "hum"}; music
moods = list of (t0, t1, mood) with mood in {"curious", "steady", "tension"}."""
import math
import wave

import numpy as np

import board as B

SR = 24000
RNG = np.random.default_rng(7)


def _read(p):
    with wave.open(str(p)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32) / 32767, w.getframerate()


def _write(p, a, sr):
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype("<i2").tobytes())


def _add(a, x, t):
    i = int(t * SR)
    if i < 0 or i >= len(a):
        return
    n = min(len(x), len(a) - i)
    a[i:i + n] += x[:n]


def _lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def pop():
    t = np.arange(int(0.07 * SR)) / SR
    return 0.06 * np.sin(2 * np.pi * (520 - 2200 * t) * t) * np.exp(-t * 55)


def whoosh(d=0.8):
    n = int(d * SR)
    t = np.arange(n) / SR
    noise = RNG.standard_normal(n)
    sweep = np.zeros(n)
    k0, k1 = 60, 6
    for j in range(0, n, 2400):   # band moves from low to high
        k = int(k0 + (k1 - k0) * j / n)
        seg = _lowpass(noise[j:j + 2400], max(2, k))
        sweep[j:j + len(seg)] = seg
    env = np.sin(np.pi * t / d) ** 2
    return 0.10 * sweep * env


def scratch(d):
    n = int(d * SR)
    t = np.arange(n) / SR
    noise = RNG.standard_normal(n)
    hp = noise - _lowpass(noise, 8)                      # thin, papery
    strokes = 0.5 + 0.5 * np.sin(2 * np.pi * 7 * t + RNG.uniform(0, 6)) ** 2
    env = np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.08)
    return 0.016 * hp * strokes * env


def heartbeat(d, bpm=66):
    out = np.zeros(int(d * SR))
    tt = np.arange(int(0.16 * SR)) / SR
    thump = lambda f, a: a * np.exp(-tt * 28) * (1 - np.exp(-tt * 300)) * np.sin(2 * np.pi * f * tt * (1 - 0.3 * tt))
    p = 60 / bpm
    b = 0.0
    while b < d - 0.4:
        _add(out, thump(55, 0.22), b)
        _add(out, thump(70, 0.15), b + 0.24)
        b += p
    return _lowpass(out, 6)


def flow(d):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = _lowpass(RNG.standard_normal(n), 40)
    return 0.05 * x * (0.6 + 0.4 * np.sin(2 * np.pi * 1.1 * t)) * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4)


def hum(d):
    t = np.arange(int(d * SR)) / SR
    x = 0.018 * (np.sin(2 * np.pi * 120 * t) + 0.5 * np.sin(2 * np.pi * 240 * t))
    return x * (0.7 + 0.3 * np.sin(2 * np.pi * 0.7 * t)) * np.minimum(1, t / 0.5) * np.minimum(1, (d - t) / 0.5)


CHORDS = {"curious": [(220.0, 261.6, 329.6), (196.0, 246.9, 311.1)],
          "steady": [(196.0, 246.9, 293.7), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7)],
          "tension": [(207.7, 246.9, 311.1), (196.0, 233.1, 293.7)]}


def music(total, moods):
    out = np.zeros(int(total * SR))
    for t0, t1, mood in moods:
        n = int((t1 - t0) * SR)
        t = np.arange(n) / SR
        seg = np.zeros(n)
        bar = 2.4 if mood != "steady" else 1.8
        for k, chord in enumerate(CHORDS[mood] * int(1 + (t1 - t0) / (bar * len(CHORDS[mood])))):
            s0 = k * bar
            if s0 >= t1 - t0:
                break
            m = (t >= s0) & (t < s0 + bar + 0.4)
            tt = t[m] - s0
            env = np.minimum(1, tt / 0.6) * np.minimum(1, (bar + 0.4 - tt) / 0.6)
            for f in chord:
                seg[m] += np.sin(2 * np.pi * f * tt) * env * 0.33
        if mood == "steady":   # soft pulse to drive the explanation
            pulse = (np.sin(2 * np.pi * 2.0 * t) > 0.92).astype(float)
            seg += _lowpass(pulse * RNG.standard_normal(n), 30) * 0.6
        fade = np.minimum(1, t / 1.0) * np.minimum(1, (t1 - t0 - t) / 1.0)
        _add(out, 0.022 * seg * fade, t0)
    return _lowpass(out, 3)


def mix(bd, voice_wav, out_wav, offset, cues=(), moods=()):
    v, sr = _read(voice_wav)
    assert sr == SR
    a = v.copy()
    total = len(a) / SR
    for t in bd.pops:
        _add(a, pop(), t + offset)
    for it in bd.items:
        if isinstance(it, B.Text) and it.dur > 0.2:
            _add(a, scratch(min(it.dur, 2.5)), it.t + offset)
    for (t0, x, y, z, d) in bd.cam:
        if d >= 0.6 and t0 > 0.2:
            _add(a, whoosh(min(1.2, d + 0.2)), t0 + offset - 0.1)
    for t0, t1, kind in cues:
        f = {"heartbeat": heartbeat, "flow": flow, "hum": hum}[kind]
        _add(a, f(t1 - t0), t0 + offset)
    if moods:
        m_ = music(total + 1, [(t0 + offset, min(t1 + offset, total), m) for t0, t1, m in moods])[:len(a)]
        a[:len(m_)] += m_
    peak = float(np.abs(a).max() or 1)
    _write(out_wav, a * min(1.0, 0.97 / peak), SR)
