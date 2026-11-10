"""Original, fully synthesized soundtrack for "香港夜雨 / Hong Kong Night Rain" (50 s).

A slow lo-fi night groove (72 BPM, 15 bars of 3.33 s) over a bed of rain and city ambience.
No samples or audio files: every sound comes from oscillators and filtered noise. Output: build/music.wav.

Cues follow the picture (see README):
  0.0   rain, city hum, electric-piano chords (title)
  6.0   a tram bell "ding ding" as the worm's-eye shot finds the tram
  6.7   the beat and bass come in
  20.0  vibraphone melody
  25.8  a swell into 26.7, where the camera rises over the rooftops: full arrangement
  33.0  distant thunder
  41.8  a second tram bell in the low shot
  43.3  outro: drums drop away at 46.7, the last chord rings out under the rain
"""
import os
import wave

import numpy as np
from scipy import signal

SR = 44100
DUR = 50.0
N = int(SR * DUR)
BPM = 72
BEAT = 60 / BPM
BAR = BEAT * 4
rng = np.random.default_rng(852)

music = np.zeros((2, N))
amb = np.zeros((2, N))
verb = np.zeros(N)


def tt(d):
    return np.arange(int(d * SR)) / SR


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(sig, t0, gain=1.0, pan=0.0, rev=0.0, bus=None):
    bus = music if bus is None else bus
    i = int(round(t0 * SR))
    if i >= N or i + len(sig) <= 0:
        return
    s = sig * gain
    if i < 0:
        s, i = s[-i:], 0
    s = s[: N - i]
    bus[0, i:i + len(s)] += s * np.cos((pan + 1) * np.pi / 4)
    bus[1, i:i + len(s)] += s * np.sin((pan + 1) * np.pi / 4)
    if rev:
        verb[i:i + len(s)] += s * rev


def filt(x, kind, fc, order=2):
    fc = np.atleast_1d(fc) / (SR / 2)
    b, a = signal.butter(order, fc if len(fc) > 1 else fc[0], kind)
    return signal.lfilter(b, a, x)


# ---------- instruments ----------
def epiano(m, t0, dur, g=1.0, pan=0.0):
    """FM electric piano: a bright tine at the attack that mellows, stereo tremolo."""
    f = mtof(m)
    t = tt(dur + 1.6)
    idx = 1.8 * np.exp(-t * 3.5) + 0.35
    s = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    s += 0.18 * np.sin(2 * np.pi * f * 14.0 * t) * np.exp(-t * 18)   # tine click
    env = np.exp(-t * 0.9) * np.minimum(1, t / 0.004)
    env *= np.clip(1 - (t - dur) / 1.2, 0, 1)
    trem = 1 + 0.18 * np.sin(2 * np.pi * 4.2 * t + pan * 3)
    place(s * env * trem * 0.16 * g, t0, pan=pan, rev=0.35)


def chord(notes, t0, dur, g=1.0, strum=0.025):
    for k, m in enumerate(notes):
        epiano(m, t0 + k * strum, dur, g * (0.9 if k else 1.0), pan=-0.5 + k / max(1, len(notes) - 1))


def vibes(m, t0, g=1.0, pan=0.2):
    f = mtof(m)
    t = tt(2.6)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 4.0 * t) * np.exp(-t * 6) + 0.08 * np.sin(2 * np.pi * f * 10.0 * t) * np.exp(-t * 20)
    env = np.exp(-t * 1.4) * np.minimum(1, t / 0.002) * (1 + 0.25 * np.sin(2 * np.pi * 5.5 * t))
    place(s * env * 0.12 * g, t0, pan=pan, rev=0.5)


def bass(m, t0, dur, g=1.0):
    f = mtof(m)
    t = tt(dur + 0.08)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) + 0.1 * np.sin(2 * np.pi * 3 * f * t)
    env = np.minimum(1, t / 0.01) * np.exp(-t * 1.2) * np.clip(1 - (t - dur) / 0.08, 0, 1)
    place(filt(s * env, "low", 900) * 0.32 * g, t0)


def kick(t0, g=1.0):
    t = tt(0.45)
    f = 45 + 55 * np.exp(-t * 28)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) + 0.25 * filt(rng.standard_normal(len(t)), "low", 1500) * np.exp(-t * 60)
    place(s * 0.55 * g, t0)


def snare(t0, g=1.0):
    t = tt(0.32)
    n = filt(rng.standard_normal(len(t)), "band", [900, 6000]) * np.exp(-t * 16)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    place((n * 0.5 + tone * 0.3) * 0.36 * g, t0, pan=0.1, rev=0.25)


def hat(t0, g=1.0, pan=0.35):
    t = tt(0.09)
    s = filt(rng.standard_normal(len(t)), "high", 7000) * np.exp(-t * 60)
    place(s * 0.12 * g, t0, pan=pan)


def shaker(t0, g=1.0):
    t = tt(0.12)
    s = filt(rng.standard_normal(len(t)), "band", [4000, 11000]) * np.sin(np.pi * np.clip(t / 0.12, 0, 1)) ** 2
    place(s * 0.07 * g, t0, pan=-0.3)


def tram_bell(t0, g=1.0, pan=-0.2):
    """Two strikes of a tram's foot gong: inharmonic partials, a long ring."""
    for k, dt in enumerate([0.0, 0.28]):
        t = tt(2.2)
        f = 1180
        s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in [(1, 1, 2.2), (2.76, .5, 3.5), (5.4, .25, 6), (8.9, .12, 9)])
        s *= np.minimum(1, t / 0.0015)
        place(s * 0.13 * g * (1 if k == 0 else .85), t0 + dt, pan=pan, rev=0.6, bus=amb)


def swell(t0, dur, g=1.0):
    t = tt(dur)
    s = filt(rng.standard_normal(len(t)), "band", [600, 9000]) * (t / dur) ** 2.5
    place(s * 0.09 * g, t0, rev=0.4)


def thunder(t0, g=1.0):
    t = tt(4.5)
    s = filt(rng.standard_normal(len(t)), "low", 160, 4) * (np.minimum(1, t / 0.4) * np.exp(-t * 0.9))
    s *= 1 + 0.8 * filt(np.abs(rng.standard_normal(len(t))), "low", 6)
    place(s * 1.4 * g, t0, pan=0.3, rev=0.3, bus=amb)


# ---------- ambience: rain on the street, drips, the city's hum, a passing car ----------
for ch in range(2):
    n = rng.standard_normal(N)
    rain = filt(n, "band", [350, 7000]) * 0.075 + filt(rng.standard_normal(N), "high", 5000) * 0.03
    amb[ch] += rain * (1 + 0.15 * np.sin(2 * np.pi * 0.07 * np.arange(N) / SR + ch))
    amb[ch] += filt(rng.standard_normal(N), "low", 120, 3) * 0.12   # far traffic rumble
for _ in range(260):   # drips off canopies and signs
    t0 = rng.uniform(0, DUR)
    t = tt(0.06)
    f = rng.uniform(1800, 4200)
    place(np.sin(2 * np.pi * f * t * (1 + 0.6 * t / 0.06)) * np.exp(-t * 90) * rng.uniform(0.01, 0.035), t0, pan=rng.uniform(-.9, .9), bus=amb)
hum = tt(DUR)
amb += (np.sin(2 * np.pi * 100 * hum) * 0.004 + np.sin(2 * np.pi * 200 * hum) * 0.002)[None, :]   # neon transformer buzz
for t0, pan in [(11.5, -1), (31.0, 1), (38.5, -1)]:   # tyres hissing through puddles
    t = tt(3.0)
    s = filt(rng.standard_normal(len(t)), "band", [500, 5000]) * np.sin(np.pi * t / 3.0) ** 3
    for k, side in enumerate([0, 1]):
        p = pan * (1 - 2 * t / 3.0)
        amb[k, int(t0 * SR):int(t0 * SR) + len(t)] += s * 0.12 * (np.cos((p + 1) * np.pi / 4) if k == 0 else np.sin((p + 1) * np.pi / 4))
tram_bell(6.0)
tram_bell(41.8, pan=0.25)
thunder(33.0, 0.9)

# ---------- the score ----------
# ii-V-I-vi in C, voiced warm: Dm9 - G13sus - Cmaj9 - Am9, one chord per bar
PROG = [([50, 57, 60, 64, 65], 38), ([55, 60, 62, 65, 69], 43), ([48, 55, 59, 62, 64], 36), ([45, 52, 55, 60, 64], 33)]
for b in range(15):
    t0 = b * BAR
    notes, root = PROG[b % 4]
    last = b == 14
    chord(notes, t0, BAR * (1.6 if last else 0.95), g=0.85 if b < 2 else 1.0)
    if 2 <= b <= 13:
        bass(root, t0, BEAT * 1.4)
        bass(root, t0 + BEAT * 1.5, BEAT * 0.4, 0.7)
        bass(root + 7, t0 + BEAT * 2.5, BEAT * 0.9, 0.85)
        bass(root + (5 if b % 4 == 1 else 10), t0 + BEAT * 3.5, BEAT * 0.45, 0.7)
    if 2 <= b <= 13:   # drums: laid-back kick and snare, swung hats
        sw = BEAT / 2 * 0.62
        kick(t0)
        kick(t0 + BEAT * 1.5 + 0.02, 0.6)
        kick(t0 + BEAT * 2.5, 0.8)
        snare(t0 + BEAT + 0.03)
        snare(t0 + BEAT * 3 + 0.03)
        for k in range(4):
            hat(t0 + k * BEAT, 0.9)
            hat(t0 + k * BEAT + sw, 0.55)
            if b >= 8:
                shaker(t0 + k * BEAT + BEAT / 4)
# melody: sparse vibraphone phrases from bar 6, answering in bars 10-13
MEL = [(6, 0, 76), (6, 1.5, 74), (6, 2.5, 72), (7, 0.5, 71), (7, 2, 67), (8, 0, 72), (8, 1, 76), (8, 2, 79), (8, 3.5, 77), (9, 0, 76), (9, 1.5, 72),
       (10, 0, 74), (10, 1, 77), (10, 2.5, 81), (11, 0, 79), (11, 2, 74), (12, 0, 76), (12, 1.5, 79), (12, 3, 83), (13, 0, 81), (13, 2, 76), (14, 0, 72)]
for b, beat, m in MEL:
    vibes(m, b * BAR + beat * BEAT, g=1.1 if b >= 8 else 0.9, pan=0.15 + 0.1 * np.sin(b + beat))
swell(25.8 - 1.6, 1.6 + 0.9)

# ---------- mix ----------
# reverb: a 2.6 s dark plate made of decaying filtered noise, convolved once
ir_t = tt(2.6)
ir = filt(rng.standard_normal((2, len(ir_t))), "low", 5500) * np.exp(-ir_t * 2.4)
wet = np.stack([signal.fftconvolve(verb, ir[c])[:N] for c in range(2)]) * 0.05
mus = music + wet
mus = np.stack([filt(mus[c], "low", 7500) for c in range(2)])   # lo-fi top end
mus = np.tanh(mus * 1.4) / 1.4
crackle = np.zeros(N)
idx = rng.integers(0, N, 900)
crackle[idx] = rng.uniform(-1, 1, len(idx))
crackle = filt(crackle, "band", [1500, 9000]) * 0.15
mix = mus * 0.9 + amb + crackle[None, :]
fade = np.ones(N)
fi, fo = int(0.8 * SR), int(3.0 * SR)
fade[:fi] = np.linspace(0, 1, fi) ** 2
fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
mix *= fade[None, :]
mix *= 0.89 / np.max(np.abs(mix))

os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build"), exist_ok=True)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "music.wav")
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix.T * 32767).astype("<i2").tobytes())
print("wrote", out, f"{DUR:.1f}s")
