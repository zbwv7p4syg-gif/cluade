"""Original, fully synthesized score for "我眼中的世界 / The World Through My Eyes" (48 s).

120 BPM, D major, 24 bars of 2 s = eight 6-second chapters. No samples, no audio files:
every sound is generated from oscillators and filtered noise. Output: build/music.wav.
"""
import os
import wave

import numpy as np
from scipy import signal

SR = 44100
BPM = 120
BEAT = 60 / BPM
STEP = BEAT / 4
DUR = 48.0
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




# ------------------------------------------------------------ extra voices
def musicbox(m, t0, g=1.0, pan=0.0):
    t = tt(1.2)
    f = mtof(m)
    s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t * 6)
         + 0.15 * np.sin(2 * np.pi * 5.4 * f * t) * np.exp(-t * 12)) * np.exp(-t * 3.2)
    s *= np.clip(t / 0.002, 0, 1)
    place(s * 0.2, t0, g, pan, rev=0.6)


def whale(t0, g=1.0):
    t = tt(1.6)
    f = 260 * np.exp(-t * 0.35) * (1 + 0.25 * np.sin(np.pi * t / 1.6)) * (1 + 0.01 * np.sin(2 * np.pi * 5 * t))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    s *= np.sin(np.pi * t / 1.6) ** 2
    place(s * 0.25, t0, g, -0.3, rev=0.9)


def clack(t0, g=1.0, f=900):
    t = tt(0.15)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 45) + bp(rng.standard_normal(len(t)), 1500, 4000) * np.exp(-t * 90) * 0.5
    place(s * 0.5, t0, g, 0.1, rev=0.2)


def splash(t0, g=1.0):
    t = tt(0.9)
    n = lp(rng.standard_normal(len(t)), 3500) * np.exp(-t * 5) * np.clip(t / 0.01, 0, 1)
    place(n * 0.6, t0, g, 0.0, rev=0.4)


def riser(t0, dur, g=1.0):
    t = tt(dur)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(n)
    chunks = 40
    for c in range(chunks):
        a, b = c * len(n) // chunks, (c + 1) * len(n) // chunks
        fc = 300 + (c / (chunks - 1)) ** 2 * 9000
        out[a:b] = bp(n[max(0, a - 400):b], fc * 0.7, min(fc * 1.5, 18000))[-(b - a):]
    place(out * (t / dur) ** 2 * 0.45, t0, g, 0.0, rev=0.3)


# ------------------------------------------------------------------ harmony
CH = {
    "D": ([62, 66, 69], 38), "A": ([61, 64, 69], 45), "Bm": ([59, 62, 66], 47), "G": ([59, 62, 67], 43),
}
BARS = ["D", "G", "A", "D", "A", "Bm", "G", "D", "A", "Bm", "G", "A",
        "D", "A", "Bm", "G", "D", "A", "Bm", "G", "A", "G", "A", "D"]
HOOK = {
    "D": [(0, 74, 2), (2, 78, 2), (4, 81, 4), (8, 78, 2), (10, 76, 2), (12, 74, 4)],
    "A": [(0, 73, 2), (2, 76, 2), (4, 81, 4), (8, 79, 2), (10, 78, 2), (12, 76, 4)],
    "Bm": [(0, 71, 2), (2, 74, 2), (4, 78, 4), (8, 76, 2), (10, 74, 2), (12, 73, 4)],
    "G": [(0, 71, 2), (2, 74, 2), (4, 79, 3), (7, 78, 1), (8, 76, 4), (12, 74, 2), (14, 73, 2)],
}


def bar_t(b, step=0):
    return b * 4 * BEAT + step * STEP


for b, name in enumerate(BARS):
    notes, root = CH[name]
    t0 = bar_t(b)
    ch = b // 3  # chapter 0..7
    # pads almost everywhere: the "air" of the world
    if b < 23:
        pad(notes, t0, 2.0, 0.55 if ch in (0, 3, 7) else 0.4)
    # music box arpeggio: waking up, and the finale
    if ch in (0, 7) or ch == 1:
        arp = [notes[0] + 24, notes[1] + 24, notes[2] + 24, notes[1] + 24]
        for s in range(0, 16, 2):
            if b == 23 and s > 8:
                break
            musicbox(arp[(s // 2) % 4] + (12 if s == 12 and ch == 0 else 0), bar_t(b, s), 0.8 if ch != 1 else 0.45,
                     pan=-0.4 if (s // 2) % 2 else 0.4)
    # marimba 16ths: text rain, garden
    if ch in (1, 5):
        for s in range(16):
            m = [notes[0] + 12, notes[2] + 12, notes[1] + 24, notes[2] + 12][s % 4]
            marimba(m, bar_t(b, s), 0.45 if s % 2 else 0.6, pan=-0.35 if s % 2 else 0.35)
    # drums
    if ch == 1:
        kick(bar_t(b, 0), 0.7); kick(bar_t(b, 8), 0.6)
        for s in range(2, 16, 4):
            hat(bar_t(b, s), 0.35)
    elif ch in (2, 6):
        for s in (0, 6, 8, 11) if ch == 2 else (0, 4, 8, 12):
            kick(bar_t(b, s), 0.85)
        for s in (4, 12):
            clap(bar_t(b, s), 0.8)
        for s in range(16):
            hat(bar_t(b, s), 0.45 if s % 4 == 2 else 0.22, open_=(s % 4 == 2 and ch == 6), pan=0.3 if s % 2 else -0.2)
        if b == 20:  # snare roll into the finale
            for s in range(8, 16):
                clap(bar_t(b, s), 0.3 + 0.08 * (s - 8))
    elif ch == 3:  # underwater (gets muffled at mixdown)
        kick(bar_t(b, 0), 0.8); kick(bar_t(b, 10), 0.6)
        clap(bar_t(b, 8), 0.5)
    elif ch == 4:  # the drop
        for s in (0, 4, 8, 12):
            kick(bar_t(b, s))
        for s in (4, 12):
            clap(bar_t(b, s))
        for s in range(16):
            hat(bar_t(b, s), 0.7 if s % 4 == 2 else 0.25, open_=s % 4 == 2)
    elif ch == 5:
        for s in (0, 7, 8):
            kick(bar_t(b, s), 0.75)
        for s in (4, 12):
            clap(bar_t(b, s), 0.65)
            snap(bar_t(b, s + 2), 0.5)
    # bass
    if ch in (2, 4, 6):
        for s in range(0, 16, 2):
            bass(root + (12 if s % 4 == 2 else 0), bar_t(b, s), STEP * 1.6, 0.85)
    elif ch in (3, 5):
        for s in (0, 3, 6, 10):
            bass(root, bar_t(b, s), STEP * 2.5, 0.75)
    elif ch == 7 and b < 23:
        bass(root, t0, 1.9, 0.8)
    # chords stabs in the big chapters
    if ch in (4, 6):
        for s in (2, 6, 10, 14):
            stab([n + 12 for n in notes], bar_t(b, s), 0.18, 0.75)
    # lead hook
    if ch in (2, 4, 6):
        for s, m, ln in HOOK[name]:
            lead(m - (12 if ch == 2 else 0), bar_t(b, s), ln * STEP * 0.92, 0.8 if ch == 2 else 1.0)
    elif ch == 5:
        for s, m, ln in HOOK[name]:
            marimba(m, bar_t(b, s), 0.9, pan=0.1)
    elif ch == 7 and b in (21, 22):
        for s, m, ln in HOOK[name]:
            musicbox(m + 12, bar_t(b, s), 1.0)

# ------------------------------------------------------------ story sfx
for k in range(10):                       # typing "claude" / "show me the world"
    hat(0.3 + k * 0.07, 0.4, pan=0.2)
for k in range(14):
    hat(1.3 + k * 0.05, 0.35, pan=0.2)
bell(86, 2.0, 1.0)                         # eyes open
bell(90, 2.5, 0.8, 0.3)
pop(3.0, 700, 0.6, -0.5); pop(3.5, 800, 0.6, 0.5)   # looks left / right
for i in range(6):                         # title letters
    musicbox(86 + [0, 2, 4, 7, 9, 12][i], 4.0 + i * 0.1, 0.9)
whoosh(5.3, 0.7, 0.9)                      # dive into the eye
bell(93, 9.0, 0.9)                         # catches a glowing word
whoosh(11.4, 0.9, 0.8)                     # letters rise to the stars
for i in range(12):                        # questions float up from Earth
    pop(12.4 + i * 0.45, 600 + (i % 6) * 90, 0.55, pan=float(np.sin(i * 1.7)) * 0.6)
whoosh(17.3, 0.6, 0.8, up=False)           # dive
splash(17.85, 1.0)
for k in range(24):                        # bubbles
    pop(18.2 + k * 0.23 + float(rng.uniform(0, 0.1)), float(rng.uniform(900, 1600)), 0.25, pan=float(rng.uniform(-0.7, 0.7)))
whale(19.5); whale(21.5, 0.8)
whoosh(23.3, 0.8, 1.0)                     # whale breaches into space
crash(24.0, 0.8)
for i in range(6):                         # constellations light up
    ct = [24.5, 25.5, 26.5, 27.5, 28.5, 29.0][i]
    for j in range(4):
        bell(81 + [0, 4, 7, 12][j] + (i % 3) * 2, ct + j * 0.07, 0.45, pan=-0.6 + i * 0.25)
whoosh(29.4, 0.6, 0.9, up=False)           # comet
crash(30.0, 1.0)
for i in range(6):                         # bugs -> butterflies
    bt = 31.0 + i * 0.75
    boing(bt, 0.35)
    bell(88 + (i % 3) * 3, bt + 0.12, 0.6, pan=0.3)
whoosh(35.5, 0.8, 0.9)                     # butterfly swarm
for i in range(8):                         # bridge blocks
    clack(36.5 + i * 0.5, 0.9, 700 + i * 60)
for k in range(8):                         # hearts / high five
    bell(86 + (k % 4) * 3, 41.0 + k * 0.06, 0.4)
riser(40.0, 2.0, 0.8)
crash(42.0, 0.9)
kick(42.0)
pad([62, 66, 69, 74], 42.0, 3.5, 0.9)
for i, m in enumerate((74, 78, 81, 86, 90)):
    musicbox(m, 46.0 + i * 0.12, 1.0, pan=-0.4 + i * 0.2)
musicbox(86, 47.3, 0.9); musicbox(98, 47.5, 0.7)
bass(38, 46.0, 1.9, 0.8)

# ------------------------------------------------------------------- mixdown
duck = 1 - 0.55 * kick_env
mix = dry + side * duck

ir_t = tt(2.0)
ir_l = lp(rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 2.6), 6000)
ir_r = lp(rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 2.6), 6000)
v = hp(verb, 250)
mix[0] += signal.fftconvolve(v, ir_l)[:N] * 0.045
mix[1] += signal.fftconvolve(v, ir_r)[:N] * 0.045

# underwater chapter: muffle everything, crossfading in and out
a, b = int(17.8 * SR), int(24.1 * SR)
w = np.zeros(N)
w[a:b] = 1
fade = int(0.3 * SR)
w[a:a + fade] = np.linspace(0, 1, fade)
w[b - fade:b] = np.linspace(1, 0, fade)
for ch_ in range(2):
    muff = lp(mix[ch_], 700, order=2) * 1.6
    mix[ch_] = mix[ch_] * (1 - w) + muff * w

mix /= np.percentile(np.abs(mix), 99.99)
mix = np.tanh(mix * 0.9) / np.tanh(0.9)
fade_n = int(0.8 * SR)
mix[:, -fade_n:] *= np.linspace(1, 0, fade_n) ** 1.5
mix /= np.max(np.abs(mix)) / 0.89

os.makedirs("build", exist_ok=True)
pcm = (mix.T * 32767).astype("<i2")
with wave.open("build/music.wav", "wb") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(pcm.tobytes())
print("wrote build/music.wav", mix.shape[1] / SR, "s")
