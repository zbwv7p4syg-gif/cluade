"""Original, fully synthesized soundtrack for "Opus 5.5 x CapCut" (30 s, 120 BPM, C major).

No samples or audio files are used: every sound is generated from sine/saw/square
oscillators and filtered noise. Output: build/music.wav (44.1 kHz, 16-bit stereo).

Beat grid: 120 BPM -> one beat every 0.5 s, one bar (4/4) every 2 s, 15 bars total.
The animation (index.html) uses the same grid so every cut/pop lands on the music.
"""
import os
import wave

import numpy as np
from scipy import signal

SR = 44100
BPM = 120
BEAT = 60 / BPM
STEP = BEAT / 4  # 16th note
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(55)

# Stereo buses
dry = np.zeros((2, N))
side = np.zeros((2, N))  # sidechained bus (ducked by kick in the drop)
verb = np.zeros(N)  # mono reverb send
kick_env = np.zeros(N)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def place(sig, t0, gain=1.0, pan=0.0, rev=0.0, bus=None):
    bus = dry if bus is None else bus
    i = int(round(t0 * SR))
    if i >= N or i + len(sig) <= 0:
        return
    s = sig * gain
    if i < 0:
        s, i = s[-i:], 0
    s = s[: N - i]
    lg = np.cos((pan + 1) * np.pi / 4)
    rg = np.sin((pan + 1) * np.pi / 4)
    bus[0, i:i + len(s)] += s * lg
    bus[1, i:i + len(s)] += s * rg
    if rev:
        verb[i:i + len(s)] += s * rev


def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc, SR / 2 - 100) / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def adsr(n_sec, a=0.005, d=0.08, s=0.6, r=0.04):
    t = tt(n_sec + r)
    env = np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rel = np.clip(1 - (t - n_sec) / r, 0, 1)
    return env * np.where(t > n_sec, rel, 1.0)


def bl_saw(f, t, fmax=9000):
    k = max(1, int(fmax / f))
    out = np.zeros_like(t)
    for h in range(1, k + 1):
        out += np.sin(2 * np.pi * h * f * t) / h
    return out * (2 / np.pi)


def bl_square(f, t, fmax=7000, vib=None):
    ph = 2 * np.pi * f * t if vib is None else 2 * np.pi * np.cumsum(f * vib) / SR
    k = max(1, int(fmax / f))
    out = np.zeros_like(t)
    for h in range(1, k + 1, 2):
        out += np.sin(h * ph) / h
    return out * (4 / np.pi)


# ---------------------------------------------------------------- instruments
def kick(t0, g=1.0):
    t = tt(0.4)
    f = 48 + 120 * np.exp(-t * 32)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8)
    s += rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.25
    place(np.tanh(s * 1.6) * 0.9, t0, g)
    i = int(t0 * SR)
    e = np.exp(-tt(0.3) * 9)
    j = min(N, i + len(e))
    kick_env[i:j] = np.maximum(kick_env[i:j], e[: j - i])


def clap(t0, g=1.0):
    t = tt(0.35)
    n = bp(rng.standard_normal(len(t)), 900, 3200)
    env = np.zeros_like(t)
    for d in (0, 0.011, 0.022):
        env += np.where(t >= d, np.exp(-(t - d) * 180), 0)
    env += np.where(t >= 0.03, np.exp(-(t - 0.03) * 16) * 0.55, 0)
    place(n * env * 0.9, t0, g, 0.05, rev=0.35)


def hat(t0, g=1.0, open_=False, pan=0.25):
    t = tt(0.3 if open_ else 0.06)
    n = hp(rng.standard_normal(len(t)), 7500)
    place(n * np.exp(-t * (12 if open_ else 70)) * 0.35, t0, g, pan)


def snap(t0, g=1.0):
    t = tt(0.12)
    n = bp(rng.standard_normal(len(t)), 1800, 5000) * np.exp(-t * 70)
    n += np.sin(2 * np.pi * 1900 * t) * np.exp(-t * 90) * 0.4
    place(n * 0.8, t0, g, -0.1, rev=0.3)


def crash(t0, g=1.0):
    t = tt(2.2)
    n = hp(rng.standard_normal(len(t)), 4000) * np.exp(-t * 2.2)
    place(n * 0.35, t0, g, 0.0, rev=0.4)


def bass(m, t0, dur, g=1.0):
    t = tt(dur + 0.03)
    f = mtof(m)
    s = lp(bl_saw(f, t, 3000), 520 + 900 * 0.5) * 0.7 + np.sin(2 * np.pi * f * t) * 0.6
    place(s * adsr(dur, 0.003, 0.12, 0.55, 0.03), t0, g, bus=side)


def marimba(m, t0, g=1.0, pan=0.0):
    t = tt(0.7)
    f = mtof(m)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 7)
         + 0.3 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 32)
         + 0.08 * np.sin(2 * np.pi * 9.9 * f * t) * np.exp(-t * 70))
    s *= np.clip(t / 0.002, 0, 1)
    place(s * 0.45, t0, g, pan, rev=0.25)


def stab(notes, t0, dur=0.22, g=1.0):
    t = tt(dur + 0.05)
    s = np.zeros_like(t)
    for m in notes:
        for det in (-0.09, 0.0, 0.09):
            s += bl_saw(mtof(m + det), t, 6000)
    s = lp(s, 2600) / (len(notes) * 3)
    s *= adsr(dur, 0.004, 0.09, 0.35, 0.05)
    place(s * 0.9, t0, g, 0.0, rev=0.3, bus=side)
    # stereo width: slightly delayed copy on the right
    place(s * 0.35, t0 + 0.012, g, 0.9, bus=side)


def pad(notes, t0, dur, g=1.0):
    t = tt(dur + 0.4)
    s = np.zeros_like(t)
    for m in notes:
        for det in (-0.12, 0.12):
            s += bl_saw(mtof(m + det), t, 3000)
    s = lp(s, 1400) / (len(notes) * 2)
    s *= adsr(dur, 0.25, 0.5, 0.8, 0.4)
    place(s * 0.5, t0, g, 0.0, rev=0.5, bus=side)


def lead(m, t0, dur, g=1.0, pan=0.0):
    t = tt(dur + 0.05)
    f = mtof(m)
    vib = 1 + 0.009 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.12) / 0.1, 0, 1)
    s = bl_square(f, t, 6000, vib) * 0.5 + np.sin(2 * np.pi * np.cumsum(f * vib) / SR) * 0.5
    s = lp(s, 4200) * adsr(dur, 0.004, 0.1, 0.65, 0.05)
    place(s * 0.32, t0, g, pan, rev=0.25)
    # dotted-8th ping-pong echo
    for k, (d, p) in enumerate(((0.375, -0.7), (0.75, 0.7), (1.125, -0.5))):
        place(lp(s, 2500) * 0.32 * 0.38 ** (k + 1), t0 + d, g, p)


def bell(m, t0, g=1.0, pan=0.0):
    t = tt(1.4)
    f = mtof(m)
    s = np.sin(2 * np.pi * f * t + 2.2 * np.exp(-t * 4) * np.sin(2 * np.pi * 3.5 * f * t))
    place(s * np.exp(-t * 3.5) * 0.22, t0, g, pan, rev=0.5)


def pop(t0, f0=600, g=1.0, pan=0.0):
    t = tt(0.12)
    f = f0 * (1 + 0.8 * np.clip(t / 0.04, 0, 1))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)
    place(s * 0.4, t0, g, pan, rev=0.15)


def whoosh(t0, dur=0.5, g=1.0, up=True):
    t = tt(dur)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(n)
    chunks = 24
    for c in range(chunks):
        a, b = c * len(n) // chunks, (c + 1) * len(n) // chunks
        x = c / (chunks - 1)
        fc = 400 + (x if up else 1 - x) ** 2 * 7000
        out[a:b] = bp(n[max(0, a - 400):b], fc * 0.6, min(fc * 1.6, 18000))[-(b - a):]
    env = np.sin(np.pi * t / dur) ** 2
    place(out * env * 0.5, t0, g, 0.0, rev=0.3)


def boing(t0, g=1.0):
    t = tt(0.45)
    f = 220 * (1 + 0.6 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 5)) * (1 + t)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    place(s * 0.45, t0, g, 0.0, rev=0.2)


def snip(t0, g=1.0):
    for d, f in ((0, 3200), (0.07, 4200)):
        t = tt(0.05)
        s = (np.sin(2 * np.pi * f * t) * 0.5 + hp(rng.standard_normal(len(t)), 5000)) * np.exp(-t * 110)
        place(s * 0.5, t0 + d, g, 0.2)


def slide_whistle(t0, dur, f0, f1, g=1.0):
    t = tt(dur)
    f = np.geomspace(f0, f1, len(t)) * (1 + 0.012 * np.sin(2 * np.pi * 6 * t))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    s = s * np.clip(t / 0.03, 0, 1) * np.clip((dur - t) / 0.05, 0, 1)
    return s * 0.35


# ------------------------------------------------------------------ harmony
CH = {
    "C": ([60, 64, 67], 36), "G": ([59, 62, 67], 43),
    "Am": ([57, 60, 64], 45), "F": ([57, 60, 65], 41),
}
BARS = ["C", "G", "Am", "F", "C", "G", "F", "C", "G", "Am", "F", "C", "G", "F", "C"]
HOOK = {
    "C": [(0, 76, 2), (2, 79, 2), (4, 84, 2), (6, 79, 1), (7, 81, 1), (8, 79, 2), (10, 76, 2), (12, 74, 2), (14, 72, 2)],
    "G": [(0, 74, 2), (2, 79, 2), (4, 83, 2), (6, 86, 2), (8, 83, 1), (9, 81, 1), (10, 79, 2), (12, 74, 4)],
    "Am": [(0, 72, 2), (2, 76, 2), (4, 81, 2), (6, 84, 2), (8, 83, 2), (10, 81, 2), (12, 76, 2), (14, 79, 2)],
    "F": [(0, 81, 3), (3, 84, 3), (6, 81, 2), (8, 79, 2), (10, 77, 2), (12, 76, 2), (14, 74, 2)],
}


def bar_t(b, step=0):
    return b * 4 * BEAT + step * STEP


for b, name in enumerate(BARS):
    notes, root = CH[name]
    t0 = bar_t(b)
    drop = 7 <= b <= 11
    # --- marimba arpeggio everywhere except the drop (where stabs take over)
    arp = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[1] + 12]
    if not drop and b not in (14,):
        for s in range(0, 16, 2):
            if b == 6 and s >= 4:
                break
            if b == 12 and s >= 12:
                break
            marimba(arp[(s // 2) % 4] + (12 if s >= 8 and b % 2 else 0), bar_t(b, s), 0.7 if b < 7 else 0.55,
                    pan=-0.3 if (s // 2) % 2 else 0.3)
    # --- drums
    if b == 0:
        for s in (4, 12):
            snap(bar_t(b, s))
        hat(bar_t(b, 14), 0.6)
    elif 1 <= b <= 5 or b == 13:
        for s in (0, 8, 10):
            kick(bar_t(b, s), 0.85)
        for s in (4, 12):
            clap(bar_t(b, s), 0.8)
        for s in range(0, 16, 2 if b < 3 else 1):
            hat(bar_t(b, s), 0.55 if s % 4 == 2 else 0.3, pan=0.3 if s % 2 else -0.2)
    elif b == 6:
        kick(bar_t(b, 0))
        clap(bar_t(b, 4), 0.7)
        hat(bar_t(b, 2), 0.4)
    elif drop:
        for s in (0, 4, 8, 12):
            kick(bar_t(b, s))
        for s in (4, 12):
            clap(bar_t(b, s))
        for s in range(16):
            if s % 4 == 2:
                hat(bar_t(b, s), 0.7, open_=True)
            else:
                hat(bar_t(b, s), 0.35 if s % 2 else 0.2, pan=-0.3)
        if b == 9:  # little snare roll into the playhead surf
            for s in range(12, 16):
                clap(bar_t(b, s), 0.35 + 0.1 * (s - 12))
    elif b == 12:  # export: half-time
        kick(bar_t(b, 0))
        clap(bar_t(b, 4), 0.7)
        kick(bar_t(b, 8), 0.7)
    # --- bass
    if 1 <= b <= 5 or b == 13 or b == 12:
        for s in (0, 3, 6, 8, 11, 14):
            if b == 12 and s >= 12:
                break
            bass(root + (12 if s in (6, 14) else 0), bar_t(b, s), STEP * 1.8, 0.8)
    elif drop:
        for s in range(0, 16, 2):
            bass(root + (12 if s % 4 == 2 else 0), bar_t(b, s), STEP * 1.6, 0.9)
    elif b == 6:
        bass(root, bar_t(b, 0), STEP * 3, 0.8)
    # --- chords
    if drop:
        for s in (2, 6, 10, 14):
            stab([n + 12 for n in notes], bar_t(b, s), 0.18, 0.8)
        pad(notes, t0, 2.0, 0.6)
    elif 2 <= b <= 5:
        pad(notes, t0, 2.0, 0.55)
    # --- lead hook
    if b in (4, 5) or drop or b == 13:
        for s, m, ln in HOOK[name]:
            if b == 13 and s >= 8:
                break
            lead(m - (12 if b in (4, 5) else 0), bar_t(b, s), ln * STEP * 0.92,
                 0.75 if b in (4, 5) else 1.0)

# ---------------------------------------------------- story-synced "musical sfx"
bell(84, 0.0, 1.0)          # Opus pops in
bell(88, 0.25, 0.7, 0.3)
for i, bt in enumerate((2.0, 2.5, 3.0, 3.5, 4.0)):   # clips land in the timeline
    pop(bt, 500 + i * 90, 0.9, pan=-0.4 + i * 0.2)
whoosh(4.1, 0.6, 0.6)       # Opus runs over
for bt in (6.0, 7.0):       # snip snip
    snip(bt)
boing(7.5)                  # kick the loading screen away
whoosh(7.5, 0.9, 0.8)
whoosh(8.0, 0.45, 0.5, up=False)  # gap closes
for i, bt in enumerate((9.0, 9.5, 10.0)):   # transitions snap in
    whoosh(bt - 0.3, 0.35, 0.6)
    bell(79 + [0, 4, 7][i], bt, 0.8)
marimba(84, 11.5, 0.6)       # hop onto the Effects button
marimba(88, 11.75, 0.6)
# sneeze -> chaos arpeggio
crash(12.5, 0.8)
boing(12.5, 1.0)
wt = [72, 74, 76, 78, 80, 82, 84, 86, 88]
for k in range(16):
    bell(int(rng.choice(wt)), 12.5 + k * 0.03125, 0.55, pan=float(rng.uniform(-0.8, 0.8)))
for s in (12, 13, 14, 15):
    hat(bar_t(6, s), 0.5)
# text words pop on beats
for i, bt in enumerate((14.5, 15.0, 15.5, 16.0, 16.5)):
    pop(bt, 700 + 60 * i, 0.8, pan=0.2)
# beat markers ripple in, clips snap
for i in range(9):
    marimba(84 + [0, 2, 4, 7, 9, 12, 14, 16, 19][i], 17.0 + i * 0.055, 0.35, pan=-0.8 + i * 0.2)
whoosh(17.6, 0.4, 0.5, up=False)
crash(18.0, 0.5)
whoosh(19.4, 0.6, 0.8)      # leap to the playhead
crash(20.0, 0.6)
whoosh(23.4, 0.6, 0.8)      # leap to Export
# export progress ticks
for i, bt in enumerate((24.0, 24.5, 25.0)):
    pop(bt, 600 + i * 200, 0.7)
for k in range(4):          # stalled clock tick at 99%
    hat(25.5 + k * 0.125, 0.5, pan=0.0)
# 100%! ta-da
crash(26.0, 1.0)
kick(26.0)
stab([72, 76, 79, 84], 26.0, 0.5, 1.0)
bell(96, 26.0, 0.8)
pop(26.5, 900, 0.9)         # Post to X
for k in range(8):          # likes counting up
    bell(91 + (k % 4) * 2, 27.0 + k * 0.125, 0.25, pan=0.5 * np.sin(k))
# finale
crash(28.0, 0.7)
kick(28.0)
pad([60, 64, 67, 72], 28.0, 1.7, 0.9)
bass(36, 28.0, 1.6, 0.9)
for i, m in enumerate((72, 76, 79, 84, 88)):
    marimba(m, 28.0 + i * 0.0625, 0.55, pan=-0.4 + i * 0.2)
for m, bt in ((79, 29.0), (76, 29.25), (84, 29.5)):  # "bye-bye!" motif
    lead(m, bt, 0.2 if bt < 29.5 else 0.45, 0.9)
bell(96, 29.5, 0.8)

# ------------------------------------------------------------------- mixdown
duck = 1 - 0.6 * kick_env
drop_mask = np.zeros(N)
drop_mask[int(14 * SR):int(24 * SR)] = 1
duck = np.where(drop_mask > 0, duck, 1 - 0.25 * kick_env)
mix = dry + side * duck

# reverb: stereo convolution with decaying noise
ir_t = tt(1.6)
ir_l = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 3.2)
ir_r = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 3.2)
ir_l, ir_r = lp(ir_l, 6000), lp(ir_r, 6000)
v = hp(verb, 250)
mix[0] += signal.fftconvolve(v, ir_l)[:N] * 0.045
mix[1] += signal.fftconvolve(v, ir_r)[:N] * 0.045

# tape stop 13.0 -> 13.5, silence 13.5 -> 14.0 (the "record freeze" gag)
a, b = int(13.0 * SR), int(13.5 * SR)
tau = np.arange(b - a) / SR
pos = (tau - tau ** 2 / 1.0) * SR + a
for ch in range(2):
    seg = np.interp(pos, np.arange(N), mix[ch])
    fade = np.clip(1 - tau / 0.5, 0, 1) ** 0.5
    mix[ch, a:b] = seg * fade
    mix[ch, b:int(14.0 * SR)] *= 0.0
# post-freeze: slide whistle as the sunglasses descend, then the drop hits
sw = slide_whistle(13.5, 0.46, 1600, 520)
i = int(13.5 * SR)
mix[:, i:i + len(sw)] += sw

# master: gentle glue + soft clip + fade tail
mix /= np.percentile(np.abs(mix), 99.99)
mix = np.tanh(mix * 0.9) / np.tanh(0.9)
fade_n = int(0.6 * SR)
mix[:, -fade_n:] *= np.linspace(1, 0, fade_n) ** 1.5
mix /= np.max(np.abs(mix)) / 0.89

os.makedirs("build", exist_ok=True)
pcm = (mix.T * 32767).astype("<i2")
with wave.open("build/music.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote build/music.wav", mix.shape[1] / SR, "s")
