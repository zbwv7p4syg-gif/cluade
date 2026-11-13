#!/usr/bin/env python3
"""Pixel-art lyric MV renderer. usage: mv.py audio.mp3 lyrics.lrc out.mp4 [--preview t1,t2,...]"""
import sys, math, subprocess, re, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 480, 270, 24
FONT = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 16)
TITLE = "数钱的女孩"
ARTIST = "连麻Swimming / 热单间HEATROOM"

# ---------------------------------------------------------------- utils
def lerp(a, b, t): return a + (b - a) * t
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(t): return 1 - (1 - t) ** 3
def ease_in_out(t): return t * t * (3 - 2 * t)
def ease_back(t):
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def mix(c1, c2, t): return tuple(int(lerp(a, b, clamp(t))) for a, b in zip(c1, c2))
def rnd(i, k=0): return (math.sin(i * 12.9898 + k * 78.233) * 43758.5453) % 1.0

E = 0.0    # energy (0..1)
BASS = 0.0
BP = 0.0   # beat pulse 1 -> 0
BPH = 0.0  # beat phase

# ---------------------------------------------------------------- audio analysis
def analyze(path):
    sr = 11025
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    k = 40
    c = np.cumsum(np.insert(x, 0, 0)); lp = (c[k:] - c[:-k]) / k
    def env(sig, rate):
        hop = sr / rate; n = int(len(sig) / hop)
        idx = (np.arange(n + 1) * hop).astype(int)
        s2 = np.cumsum(np.insert(sig ** 2, 0, 0))
        e = np.sqrt((s2[idx[1:]] - s2[idx[:-1]]) / np.maximum(1, idx[1:] - idx[:-1]))
        return e
    e = env(x, FPS); e = np.clip(e / np.percentile(e, 97), 0, 1.3)
    b = env(lp, FPS); b = np.clip(b / np.percentile(b, 97), 0, 1.3)
    # tempo
    b100 = env(lp, 100)
    on = np.maximum(0, np.diff(b100, prepend=b100[0]))
    on = on - on.mean()
    best, bl = -1, 50
    for lag in range(int(6000 / 180), int(6000 / 70) + 1):
        v = np.dot(on[:-lag], on[lag:])
        if v > best: best, bl = v, lag
    # refine lag with fractional search
    bpm0 = 6000 / bl
    best2, bpm = -1, bpm0
    for bb in np.arange(bpm0 - 3, bpm0 + 3, 0.05):
        per = 6000 / bb
        sc = 0
        for ph in np.arange(0, per, 1.0):
            pos = (ph + np.arange(0, (len(on) - ph) / per) * per).astype(int)
            s = on[pos].sum()
            if s > sc: sc, phb = s, ph
        if sc > best2: best2, bpm, phase = sc, bb, phb / 100
    return e, b, bpm, phase

# ---------------------------------------------------------------- drawing helpers
def sky(top, bot, step=4):
    ys = (np.arange(H) // step * step) / (H - 1)
    col = np.array(top, float)[None, :] * (1 - ys[:, None]) + np.array(bot, float)[None, :] * ys[:, None]
    arr = np.ascontiguousarray(np.broadcast_to(col[:, None, :], (H, W, 3)).astype(np.uint8))
    return Image.fromarray(arr)

STARS = [(int(rnd(i, 1) * W), int(rnd(i, 2) * H * 0.62), rnd(i, 3) * 6.28, 1 + int(rnd(i, 4) * 1.6)) for i in range(110)]
def stars(d, t, alpha=1.0, n=110):
    for x, y, ph, s in STARS[:n]:
        b = 0.5 + 0.5 * math.sin(t * 2.5 + ph * 3)
        if b * alpha > 0.35:
            c = int(255 * b * alpha)
            d.rectangle([x, y, x + s - 1, y + s - 1], fill=(c, c, min(255, c + 40)))
            if s == 2 and b > 0.9:
                d.point([(x - 1, y), (x + 2, y), (x, y - 1), (x, y + 2)], fill=(c, c, 255))

def sparkle(d, x, y, r, col=(255, 255, 220)):
    x, y, r = int(x), int(y), int(r)
    d.line([x - r, y, x + r, y], fill=col); d.line([x, y - r, x, y + r], fill=col)
    if r > 3:
        d.point([(x - 1, y - 1), (x + 1, y + 1), (x - 1, y + 1), (x + 1, y - 1)], fill=col)

def coin(d, x, y, r, ang):
    x, y, r = int(x), int(y), max(2, int(r))
    w = max(1, int(abs(math.cos(ang)) * r))
    d.ellipse([x - w, y - r, x + w, y + r], fill=(170, 100, 10))
    if w > 2:
        d.ellipse([x - w + 1, y - r + 1, x + w - 1, y + r - 1], fill=(255, 196, 40))
    if w > 4 and r > 4:
        h = max(1, r // 4); hw = max(1, int(h * w / r))
        d.rectangle([x - hw, y - h, x + hw, y + h], fill=(190, 120, 20))
    if w > 2:
        d.point((x - w // 2, y - r // 2), fill=(255, 250, 210))

def bill(d, x, y, ang, s=1):
    x, y = int(x), int(y)
    w = int(abs(math.cos(ang)) * 7 * s); h = 3 * s
    if w < 1:
        d.line([x, y - h, x, y + h], fill=(160, 40, 50)); return
    d.rectangle([x - w, y - h, x + w, y + h], fill=(170, 40, 55))
    if w > 1:
        d.rectangle([x - w + 1, y - h + 1, x + w - 1, y + h - 1], fill=(240, 110, 120))
        d.rectangle([x - max(0, w // 3), y - 1, x + max(0, w // 3), y + 1], fill=(255, 210, 190))

def burst(d, cx, cy, age, col, n=26, spd=55, seed=0):
    if age < 0 or age > 1.4: return
    fade = clamp(1.3 - age)
    c = mix((0, 0, 0), col, fade * 1.2)
    for i in range(n):
        a = i / n * 6.283 + rnd(seed, i) * 0.3
        r = spd * ease_out(clamp(age / 1.0)) * (0.7 + 0.3 * rnd(seed + i, 2))
        x = cx + math.cos(a) * r; y = cy + math.sin(a) * r + 18 * age * age
        d.rectangle([int(x), int(y), int(x) + 1, int(y) + 1], fill=c)
        if age < 0.5:
            x2 = cx + math.cos(a) * r * 0.75; y2 = cy + math.sin(a) * r * 0.75
            d.point((int(x2), int(y2)), fill=mix(c, (255, 255, 255), 0.5))

def heart_px(d, cx, cy, s, col=(240, 60, 90)):
    rows = HEART
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                c = col if ch == 'r' else (255, 230, 240)
                x = int(cx + (i - 4.5) * s); y = int(cy + (j - 4) * s)
                d.rectangle([x, y, x + s - 1, y + s - 1], fill=c)

def bubble(img, d, x, y, text, fill=(255, 255, 255), fg=(30, 20, 40)):
    ti = text_img(text, fg, None)
    w, h = ti.size
    x0, y0 = int(x - w / 2 - 5), int(y - h - 6)
    d.rectangle([x0, y0, x0 + w + 9, y0 + h + 5], fill=fill, outline=(30, 20, 40))
    d.polygon([(x - 3, y0 + h + 5), (x + 3, y0 + h + 5), (x - 4, y + 4)], fill=fill, outline=(30, 20, 40))
    d.line([x - 2, y0 + h + 5, x + 2, y0 + h + 5], fill=fill)
    img.paste(ti, (x0 + 5, y0 + 3), ti)

# ---------------------------------------------------------------- text
_tc = {}
def text_img(s, fill, outline=(0, 0, 0), ow=1):
    key = (s, fill, outline, ow)
    if key in _tc: return _tc[key]
    w = int(FONT.getlength(s)) + 2 * ow + 1
    h = 17 + 2 * ow
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); dd = ImageDraw.Draw(im); dd.fontmode = "1"
    if outline:
        for dx in range(-ow, ow + 1):
            for dy in range(-ow, ow + 1):
                if dx or dy: dd.text((ow + dx, ow + dy), s, font=FONT, fill=outline)
    dd.text((ow, ow), s, font=FONT, fill=fill)
    _tc[key] = im
    return im

def put_text(img, s, x, y, fill=(255, 255, 255), outline=(0, 0, 0), scale=1, anchor="c", ow=1):
    ti = text_img(s, fill, outline, ow)
    if scale != 1:
        ti = ti.resize((ti.width * scale, ti.height * scale), Image.NEAREST)
    if anchor == "c": x = x - ti.width // 2
    img.paste(ti, (int(x), int(y)), ti)
    return ti.width

def dilate(m, r):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx == 0 and dy == 0: continue
            sh = np.zeros_like(m)
            ys = slice(max(0, dy), m.shape[0] + min(0, dy)); yd = slice(max(0, -dy), m.shape[0] + min(0, -dy))
            xs = slice(max(0, dx), m.shape[1] + min(0, dx)); xd = slice(max(0, -dx), m.shape[1] + min(0, -dx))
            sh[ys, xs] = m[yd, xd]
            out |= sh
    return out

_mask_c = {}
def fancy_text(s, scale, t, style="gold"):
    """Big pixel title text with gradient, shine, outline and drop shadow -> RGBA image."""
    key = (s, scale)
    if key not in _mask_c:
        m = Image.new("L", (int(FONT.getlength(s)), 16), 0)
        dd = ImageDraw.Draw(m); dd.fontmode = "1"; dd.text((0, 0), s, font=FONT, fill=255)
        m = np.array(m) > 0
        m = np.repeat(np.repeat(m, scale, 0), scale, 1)
        pad = scale + 3
        m = np.pad(m, ((pad, pad + scale), (pad, pad + scale)))
        o = dilate(m, max(2, scale // 2 + 1))
        sh = np.zeros_like(o); sh[scale:, scale:] = o[:-scale, :-scale]
        _mask_c[key] = (m, o, sh)
    m, o, sh = _mask_c[key]
    h, w = m.shape
    out = np.zeros((h, w, 4), np.uint8)
    out[sh & ~o] = (40, 10, 60, 255)
    if style == "gold":
        oc = (90, 30, 10)
        stops = [(255, 250, 200), (255, 215, 60), (240, 150, 20), (200, 90, 20)]
    elif style == "pink":
        oc = (70, 10, 50)
        stops = [(255, 240, 250), (255, 150, 200), (240, 70, 150), (170, 30, 120)]
    elif style == "cyan":
        oc = (10, 30, 70)
        stops = [(230, 255, 255), (120, 240, 255), (60, 170, 255), (40, 90, 220)]
    else:
        oc = (30, 30, 40)
        stops = [(255, 255, 255), (230, 230, 240), (200, 200, 220), (160, 160, 190)]
    out[o] = (*oc, 255)
    yy = np.arange(h)[:, None] / h
    seg = np.clip((yy * 3).astype(int), 0, 2)
    ft = (yy * 3) - seg
    st = np.array(stops, float)
    grad = st[seg] * (1 - ft[..., None]) + st[seg + 1] * ft[..., None]
    grad = np.round(grad / 16) * 16  # banding = pixel look
    grad = np.broadcast_to(grad, (h, w, 3))
    xx = np.arange(w)[None, :]; yi = np.arange(h)[:, None]
    shine = (((xx + yi * 0.6) - (t * 160) % (w + 200) + 100) % (w + 200)) < 10
    col = np.where(shine[..., None], 255, np.clip(grad, 0, 255))
    out[m, :3] = col[m].astype(np.uint8); out[m, 3] = 255
    return Image.fromarray(out, "RGBA")

# ---------------------------------------------------------------- sprites
OUT_C = (24, 14, 32)
GIRL = [
    "..hhhhhhhh..",
    ".hhhhhhhhhh.",
    "hhhhhhhhhhhh",
    "hhhsssssshhh",
    "hhsesssseshh",
    "hhspsssspshh",
    "hhsssmmssshh",
    "hhhsssssshhh",
    "hhhhhsshhhhh",
    "hhddddddddhh",
    ".sdddwwddds.",
    ".sdddddddds.",
    "..dddddddd..",
    ".dddddddddd.",
    "dddddddddddd",
    "DDDDDDDDDDDD",
    "...ss..ss...",
    "...ss..ss...",
    "..bbb..bbb..",
]
BOY = [
    "..cccccccc..",
    ".cccccccccc.",
    "CCCCCCCCCCCC",
    ".hssssssssh.",
    ".hsessssesh.",
    ".ssssssssss.",
    ".sssmmmmsss.",
    "..ssssssss..",
    "....ssss....",
    ".dddddddddd.",
    "dddddwwddddd",
    "sddddwwdddds",
    "sdddddddddds",
    ".dddddddddd.",
    ".llllllllll.",
    ".llll..llll.",
    ".llll..llll.",
    ".bbbb..bbbb.",
]
MAN = ["..hhhhhhhh..", ".hhhhhhhhhh.", ".hhhhhhhhhh."] + BOY[3:]
HEART = [
    ".rr...rr.",
    "rrrr.rrrr",
    "rwwrrrrrr",
    "rwrrrrrrr",
    "rrrrrrrrr",
    ".rrrrrrr.",
    "..rrrrr..",
    "...rrr...",
    "....r....",
]
GLASS = [
    "wwwwwww",
    "wyyyyyw",
    "wyyyyyw",
    ".wyyyw.",
    "..www..",
    "...w...",
    "...w...",
    ".wwwww.",
]
SKIN = (255, 206, 160)
P_GIRL = {'h': (80, 40, 30), 's': SKIN, 'e': (30, 20, 40), 'p': (255, 140, 150), 'm': (220, 70, 90),
          'd': (225, 45, 70), 'D': (160, 25, 50), 'w': (255, 230, 120), 'b': (70, 30, 40)}
P_BRIDE = dict(P_GIRL, d=(250, 250, 255), D=(215, 215, 235), w=(255, 170, 200))
P_BOY = {'c': (30, 30, 46), 'C': (250, 200, 50), 'h': (30, 20, 20), 's': SKIN, 'e': (30, 20, 40), 'm': (200, 80, 80),
         'd': (60, 110, 225), 'w': (245, 245, 245), 'l': (40, 40, 64), 'b': (245, 245, 245), 'p': (255, 150, 150)}
P_GROOM = dict(P_BOY, h=(20, 15, 15), d=(30, 30, 40), w=(220, 30, 50), l=(25, 25, 35), b=(20, 20, 20))
P_DAD1 = dict(P_BOY, h=(170, 170, 170), d=(120, 80, 50), w=(230, 210, 170), l=(60, 50, 40), b=(50, 40, 30))
P_DAD2 = dict(P_BOY, h=(140, 140, 150), d=(60, 90, 80), w=(200, 220, 200), l=(50, 50, 50), b=(40, 40, 40))
P_MOM1 = dict(P_GIRL, h=(160, 160, 170), d=(140, 60, 150), D=(100, 40, 110), w=(255, 220, 120))
P_MOM2 = dict(P_GIRL, h=(120, 110, 110), d=(200, 120, 40), D=(150, 80, 30), w=(255, 240, 200))
P_HATER = dict(P_BOY, h=(50, 50, 60), s=(220, 200, 180), d=(110, 110, 125), w=(60, 60, 70), l=(70, 70, 80), b=(30, 30, 30), m=(120, 60, 60))
P_PAST = dict(P_BOY, c=(90, 90, 100), C=(130, 130, 140), d=(120, 120, 130), w=(160, 160, 170), l=(80, 80, 90), b=(150, 150, 150), s=(200, 190, 180))

_sc = {}
def sprite(rows, pal, s, flip=False, blink=False, outline=True):
    key = (id(rows), tuple(sorted(pal.items())), s, flip, blink, outline)
    if key in _sc: return _sc[key]
    w = max(len(r) for r in rows); h = len(rows)
    a = np.zeros((h + 2, w + 2, 4), np.uint8)
    for j, r in enumerate(rows):
        r = r.center(w, '.')
        for i, ch in enumerate(r):
            if ch == '.': continue
            if blink and ch == 'e': c = (200, 140, 110)
            else: c = pal.get(ch)
            if c is None: continue
            a[j + 1, i + 1] = (*c, 255)
    if outline:
        al = a[..., 3] > 0
        ed = dilate(al, 1) & ~al
        a[ed] = (*OUT_C, 255)
    if flip: a = a[:, ::-1]
    im = Image.fromarray(np.ascontiguousarray(a), "RGBA").resize(((w + 2) * s, (h + 2) * s), Image.NEAREST)
    _sc[key] = im
    return im

def person(img, rows, pal, cx, by, s=3, t=0.0, flip=False, bob=None, seed=0, alpha=255, closed=False):
    blink = closed or ((t * 0.8 + seed * 0.37) % 3.1) < 0.13
    sp = sprite(rows, pal, s, flip, blink)
    if bob is None: bob = int(round(abs(math.sin(BPH * math.pi)) * 1.0)) * (s // 2 or 1) if BP > 0 else 0
    x = int(cx - sp.width / 2); y = int(by - sp.height - bob)
    if alpha < 255:
        sp = sp.copy(); sp.putalpha(sp.getchannel("A").point(lambda v: v * alpha // 255))
    img.paste(sp, (x, y), sp)
    # eye positions (row 5 incl outline), cols 4 & 9
    return dict(x=x, y=y, w=sp.width, h=sp.height, eyes=((x + 4 * s, y + 5 * s + s), (x + 9 * s, y + 5 * s + s)),
                hands=((x + 1 * s, y + 12 * s), (x + sp.width - 2 * s, y + 12 * s)), top=y)

def tears(d, info, lt, s=3, heavy=False):
    n = 8 if heavy else 4
    for (ex, ey) in info["eyes"]:
        for i in range(n):
            age = (lt * (1.6 if heavy else 1.0) + i / n) % 1.0
            side = -1 if ex < info["x"] + info["w"] / 2 else 1
            x = ex + side * (2 + age * (10 if heavy else 3)); y = ey + age * 26 + (age ** 2) * 8
            d.rectangle([int(x), int(y), int(x) + 1, int(y) + 2], fill=(120, 200, 255))
        if heavy:
            d.line([ex, ey, ex, ey + 6], fill=(150, 220, 255))

def walls(img, d, wall, floor, y=200):
    d.rectangle([0, 0, W, y], fill=wall)
    for x in range(0, W, 24):
        d.line([x, 0, x, y], fill=mix(wall, (0, 0, 0), 0.08))
    d.rectangle([0, y, W, H], fill=floor)
    for x in range(-40, W + 40, 30):
        d.line([x, y, x + (x - W / 2) * 0.6, H], fill=mix(floor, (0, 0, 0), 0.15))
    d.line([0, y, W, y], fill=mix(floor, (0, 0, 0), 0.4))

def make_city(seed, hmin, hmax, wmin, wmax, col, wincol, lit=0.45, total=W * 2):
    im = Image.new("RGBA", (total, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = 0; i = 0
    while x < total:
        w = int(wmin + rnd(seed + i, 1) * (wmax - wmin)); h = int(hmin + rnd(seed + i, 2) * (hmax - hmin))
        w = min(w, total - x)
        d.rectangle([x, 160 - h, x + w - 1, 159], fill=col)
        if rnd(seed + i, 5) > 0.7:
            d.rectangle([x + w // 2 - 1, 160 - h - 8, x + w // 2, 160 - h], fill=col)
            d.point((x + w // 2, 160 - h - 9), fill=(255, 60, 60))
        if wincol:
            for wy in range(160 - h + 4, 156, 6):
                for wx in range(x + 3, x + w - 3, 5):
                    if rnd(wx * 7 + wy, seed) < lit:
                        d.rectangle([wx, wy, wx + 1, wy + 2], fill=wincol)
        x += w + int(rnd(seed + i, 3) * 3); i += 1
    return im

_city = {}
def city(img, name, base_y, scroll, **kw):
    if name not in _city: _city[name] = make_city(**kw)
    im = _city[name]
    off = int(scroll) % im.width
    img.paste(im, (-off, base_y - 160), im)
    img.paste(im, (im.width - off, base_y - 160), im)

def overlay(img, draw_fn):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    draw_fn(ld)
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def beams(ld, t, n=3, col=(255, 240, 200, 50), base_y=H, spread=0.5, speed=0.8):
    for k in range(n):
        bx = W * (k + 0.5) / n
        a = -math.pi / 2 + math.sin(t * speed + k * 2.1) * spread
        L = 400
        a1, a2 = a - 0.09, a + 0.09
        ld.polygon([(bx, base_y), (bx + math.cos(a1) * L, base_y + math.sin(a1) * L),
                    (bx + math.cos(a2) * L, base_y + math.sin(a2) * L)], fill=col)

def lantern(d, x, y, t, ph=0):
    sw = math.sin(t * 2 + ph) * 3
    d.line([x, 0, x + sw, y], fill=(80, 40, 20))
    cx = x + sw
    d.ellipse([cx - 9, y, cx + 9, y + 16], fill=(220, 30, 30), outline=(120, 10, 10))
    d.rectangle([cx - 5, y - 1, cx + 5, y + 1], fill=(240, 190, 40))
    d.rectangle([cx - 5, y + 15, cx + 5, y + 17], fill=(240, 190, 40))
    d.line([cx, y + 2, cx, y + 14], fill=(255, 120, 80))
    for k in range(3): d.line([cx - 2 + k * 2, y + 18, cx - 2 + k * 2, y + 24], fill=(240, 190, 40))

def confetti(d, lt, n=60, seed=0, cols=((255, 80, 120), (255, 220, 60), (80, 200, 255), (140, 255, 140), (255, 255, 255))):
    for i in range(n):
        sp = 25 + rnd(i, seed + 1) * 40
        x = rnd(i, seed + 2) * W + math.sin(lt * 3 + i) * 6
        y = (rnd(i, seed + 3) * 300 + lt * sp) % 290 - 15
        c = cols[i % len(cols)]
        if (lt * 6 + i) % 2 < 1: d.rectangle([int(x), int(y), int(x) + 1, int(y) + 1], fill=c)
        else: d.point((int(x), int(y)), fill=c)

def money_rain(d, lt, n=40, seed=0, speed=1.0, coins=True, bills=True):
    for i in range(n):
        sp = (40 + rnd(i, seed + 1) * 60) * speed
        x = rnd(i, seed + 2) * W + math.sin(lt * 2 + i) * 8
        y = (rnd(i, seed + 3) * 300 + lt * sp) % 300 - 20
        if i % 2 == 0 and coins: coin(d, x, y, 3 + int(rnd(i, 4) * 3), lt * 6 + i)
        elif bills: bill(d, x, y, lt * 4 + i, 1)

def draw_car(d, x, y, col=(220, 30, 50), t=0.0, s=1, heads=None):
    # x center, y = ground
    dark = mix(col, (0, 0, 0), 0.4)
    L = 70 * s
    d.rectangle([x - L // 2, y - 22 * s, x + L // 2, y - 8 * s], fill=col, outline=dark)
    d.polygon([(x - 20 * s, y - 22 * s), (x - 12 * s, y - 34 * s), (x + 14 * s, y - 34 * s), (x + 24 * s, y - 22 * s)], fill=col, outline=dark)
    d.polygon([(x - 16 * s, y - 23 * s), (x - 10 * s, y - 32 * s), (x, y - 32 * s), (x, y - 23 * s)], fill=(150, 210, 255))
    d.polygon([(x + 2 * s, y - 23 * s), (x + 2 * s, y - 32 * s), (x + 13 * s, y - 32 * s), (x + 20 * s, y - 23 * s)], fill=(150, 210, 255))
    if heads:
        for hx, pal in heads:
            d.rectangle([x + hx * s - 3, y - 30 * s, x + hx * s + 3, y - 24 * s], fill=SKIN)
            d.rectangle([x + hx * s - 3, y - 31 * s, x + hx * s + 3, y - 29 * s], fill=pal)
    d.line([x - L // 2 + 2, y - 15 * s, x + L // 2 - 2, y - 15 * s], fill=mix(col, (255, 255, 255), 0.4))
    d.rectangle([x + L // 2 - 4, y - 19 * s, x + L // 2, y - 15 * s], fill=(255, 250, 180))
    d.rectangle([x - L // 2, y - 19 * s, x - L // 2 + 3, y - 15 * s], fill=(255, 60, 60))
    for wx in (x - 22 * s, x + 22 * s):
        r = 8 * s
        d.ellipse([wx - r, y - r - 1, wx + r, y + r - 1], fill=(25, 25, 30))
        d.ellipse([wx - r // 2, y - r // 2 - 1, wx + r // 2, y + r // 2 - 1], fill=(170, 170, 180))
        a = t * 12
        d.line([wx + math.cos(a) * r * 0.5, y - 1 + math.sin(a) * r * 0.5, wx - math.cos(a) * r * 0.5, y - 1 - math.sin(a) * r * 0.5], fill=(80, 80, 90))

def glass(img, x, y, s=2):
    g = sprite(GLASS, {'w': (220, 240, 255), 'y': (255, 190, 60)}, s)
    img.paste(g, (int(x - g.width / 2), int(y)), g)

def mountains(d, base, layers):
    for k, (col, hgt, seed, n) in enumerate(layers):
        pts = [(0, H)]
        for i in range(n + 1):
            x = i * W / n
            pts.append((x - W / n / 2, base - hgt * (0.3 + 0.7 * rnd(i, seed))))
            pts.append((x, base - hgt * 0.15 * rnd(i, seed + 1)))
        pts.append((W, H))
        d.polygon(pts, fill=col)

def karst(d, base, col, seed, n, hmax, wmax):
    for i in range(n):
        x = rnd(i, seed) * (W + 60) - 30; h = hmax * (0.5 + 0.5 * rnd(i, seed + 1)); w = wmax * (0.6 + 0.4 * rnd(i, seed + 2))
        d.ellipse([x - w / 2, base - h, x + w / 2, base + h * 0.6], fill=col)

def cloud(d, x, y, s=1.0, col=(255, 255, 255)):
    for dx, dy, r in ((0, 0, 10), (12, -5, 12), (26, 0, 10), (13, 4, 11)):
        d.ellipse([x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s], fill=col)

def notes(img, lt, cx, cy, n=5, col=(255, 230, 120), seed=0):
    for i in range(n):
        age = (lt * 0.8 + i / n) % 1.0
        x = cx + (rnd(i, seed) - 0.5) * 80 + math.sin(age * 6 + i) * 6
        y = cy - age * 60
        put_text(img, "♪" if i % 2 else "♫", x, y, col, (40, 20, 40))

# ---------------------------------------------------------------- scenes  (each: f(lt, dur, v, t) -> Image)
def sc_intro(lt, dur, v, t):
    if lt < 1.8:
        img = Image.new("RGB", (W, H), (6, 4, 16)); d = ImageDraw.Draw(img)
        stars(d, t, clamp(lt / 1.2))
        p = ease_out(clamp(lt / 1.8))
        r = int(3 + 20 * p)
        cy = H // 2 - 14
        for k in range(3):
            rr = r + 8 + k * 7 + int(3 * math.sin(lt * 6 + k))
            d.ellipse([W / 2 - rr, cy - rr, W / 2 + rr, cy + rr], outline=mix((6, 4, 16), (255, 180, 60), 0.5 - k * 0.15))
        coin(d, W // 2, cy, r, lt * 6)
        sparkle(d, W // 2 + r - 3, cy - r + 3, 3 + int(4 * abs(math.sin(lt * 5))))
        for i in range(10):
            a = i / 10 * 6.28 + lt
            rr = r + 30 + 10 * math.sin(lt * 3 + i)
            sparkle(d, W / 2 + math.cos(a) * rr, cy + math.sin(a) * rr, 2, (255, 220, 120))
        if lt > 0.6:
            put_text(img, "♪ 一首关于数钱的歌 ♪", W // 2, cy + 44, (255, 220, 180), (40, 10, 30))
        return img
    tt = lt - 1.8
    img = sky((16, 8, 46), (130, 40, 110)); d = ImageDraw.Draw(img)
    stars(d, t)
    d.ellipse([392, 22, 420, 50], fill=(255, 240, 200)); d.ellipse([400, 18, 428, 46], fill=(16, 10, 48))
    img = overlay(img, lambda ld: beams(ld, t, 4, (255, 200, 255, 38), H, 0.6))
    city(img, "far1", 200, t * 6, seed=11, hmin=40, hmax=110, wmin=16, wmax=34, col=(50, 26, 80), wincol=(140, 90, 160), lit=0.25)
    city(img, "near1", 214, t * 14, seed=31, hmin=30, hmax=80, wmin=22, wmax=44, col=(28, 14, 44), wincol=(255, 210, 120), lit=0.35)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 214, W, H], fill=(36, 18, 52))
    for x in range(0, W, 16):
        c = (255, 120, 200) if (x // 16 + int(t * 6)) % 2 else (120, 220, 255)
        d.rectangle([x + 6, 216, x + 9, 218], fill=c)
    # rain of money, heavy then light
    money_rain(d, tt, n=int(70 if tt < 3 else 36), seed=3, speed=1.4)
    # girl rises
    if tt > 2.2:
        gp = ease_out(clamp((tt - 2.2) / 0.8))
        by = int(lerp(300, 252, gp))
        # pile
        info = person(img, GIRL, P_GIRL, W // 2, by, 3, t)
        for i in range(10):
            age = (tt * 1.2 + i / 10) % 1.0
            vx = (rnd(i, 7) - 0.5) * 140; vy = -120 - rnd(i, 8) * 60
            x = W / 2 + vx * age; y = by - 40 + vy * age + 200 * age * age
            bill(d, x, y, tt * 8 + i, 2)
    # title slam
    ts = clamp((tt - 0.2) / 0.6)
    if ts > 0:
        ti = fancy_text(TITLE, 4, t)
        f = lerp(3.0, 1.0, ease_back(ts))
        ti2 = ti.resize((max(1, int(ti.width * f)), max(1, int(ti.height * f))), Image.NEAREST)
        bounce = int(math.sin(t * 3) * 2) if ts >= 1 else 0
        img.paste(ti2, (W // 2 - ti2.width // 2, 66 - ti2.height // 2 + bounce), ti2)
        d = ImageDraw.Draw(img)
        if ts >= 1:
            for i in range(6):
                k = (int(t * 4) + i * 7) % 23
                sparkle(d, W / 2 - 150 + rnd(k, 1) * 300, 40 + rnd(k, 2) * 50, 2 + (i % 3), (255, 255, 230))
    if tt > 1.2:
        n = int(clamp((tt - 1.2) / 1.2) * len(ARTIST) + 0.5)
        if n: put_text(img, ARTIST[:n], W // 2, 106, (255, 225, 245), (60, 10, 60))
    if tt > 2.6 and int(t * 3) % 2 == 0:
        put_text(img, "★ PIXEL  MV ★", W // 2, 126, (120, 230, 255), (10, 20, 60))
    # flash on slam
    if 0.75 < tt < 1.3:
        a = 1 - (tt - 0.75) / 0.55
        img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), a * 0.85)
    return img

CH_BG = [((20, 14, 50), (70, 40, 110), (40, 26, 60)), ((140, 200, 255), (250, 230, 200), (180, 120, 90)), ((255, 140, 60), (255, 210, 120), (120, 60, 50))]

def sc_money(lt, dur, v, t):
    top, bot, floor = CH_BG[v]
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    wall = [(60, 40, 90), (250, 225, 200), (170, 70, 70)][v]
    walls(img, d, wall, floor, 196)
    # window
    win = sky(top, bot).crop((0, 0, 140, 90))
    if v == 0:
        wd = ImageDraw.Draw(win); stars(wd, t, 1, 30)
    city(win, ["far1", "far1", "far1"][v], 96, t * 4, seed=11, hmin=40, hmax=110, wmin=16, wmax=34, col=(50, 26, 80), wincol=(140, 90, 160), lit=0.25)
    img.paste(win, (40, 30)); d.rectangle([38, 28, 181, 121], outline=(120, 70, 40), width=3); d.line([110, 30, 110, 120], fill=(120, 70, 40), width=2)
    # wall art: ¥ poster
    d.rectangle([350, 40, 420, 110], fill=(255, 220, 80), outline=(140, 80, 20), width=2)
    put_text(img, "招财", 385, 50, (200, 30, 30), None)
    put_text(img, "进宝", 385, 78, (200, 30, 30), None)
    if v == 2:
        img = overlay(img, lambda ld: beams(ld, t, 3, (255, 240, 180, 50), 0, 0.5))
        d = ImageDraw.Draw(img)
    # girl
    info = person(img, GIRL, P_GIRL if v != 2 else P_BRIDE, 240, 214, 3, t)
    d = ImageDraw.Draw(img)
    # money pile in front
    for row in range(4):
        y = 216 - row * 4
        wd = 80 - row * 12
        for k in range(-wd, wd, 14):
            xx = 240 + k + (row % 2) * 7
            d.rectangle([xx, y - 4, xx + 13, y], fill=(240, 110, 120), outline=(170, 40, 55))
            d.rectangle([xx + 5, y - 3, xx + 8, y - 1], fill=(255, 210, 190))
    # bills she hugs
    for i in range(5):
        bill(d, info["x"] + 8 + i * 6, info["y"] + 34 + (i % 2) * 2, 0, 2)
    # fountain
    for i in range(18):
        age = (lt * 0.9 + i / 18) % 1.0
        vx = (rnd(i, 7) - 0.5) * 220; vy = -170 - rnd(i, 8) * 80
        x = 240 + vx * age * 1.3; y = 200 + vy * age + 300 * age * age
        if i % 3 == 0: coin(d, x, y, 4, lt * 7 + i)
        else: bill(d, x, y, lt * 6 + i, 2)
    # hearts
    for i in range(4):
        age = (lt * 0.7 + i / 4) % 1.0
        heart_px(d, info["x"] + info["w"] / 2 + (i - 1.5) * 26 + math.sin(age * 6) * 4, info["y"] - age * 60, 1 + (i % 2))
    # boy watching
    person(img, BOY, P_BOY, 380, 214, 3, t, flip=True, seed=2)
    # counter
    val = int(ease_in_out(clamp(lt / dur)) * 9999999)
    d.rectangle([12, 140, 140, 176], fill=(20, 16, 30), outline=(255, 200, 60), width=2)
    put_text(img, "已数:", 20, 149, (255, 255, 255), None, anchor="l")
    put_text(img, f"¥{val:,}", 64, 149, (255, 220, 60), None, anchor="l")
    if v == 2:
        confetti(ImageDraw.Draw(img), lt, 50)
    return img

def sc_wedding(lt, dur, v, t):
    wall = [(130, 20, 30), (250, 210, 220), (200, 120, 30)][v]
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=wall)
    # back pattern
    for y in range(0, 190, 20):
        for x in range((y // 20 % 2) * 20, W, 40):
            d.rectangle([x + 8, y + 8, x + 11, y + 11], fill=mix(wall, (255, 220, 80), 0.25))
    xi = fancy_text("囍", 6, t, "gold" if v != 1 else "pink")
    img.paste(xi, (W // 2 - xi.width // 2, 14 + int(math.sin(t * 2) * 2)), xi)
    # flower arch
    for i in range(30):
        a = math.pi + i / 29 * math.pi
        x = W / 2 + math.cos(a) * 120; y = 200 + math.sin(a) * 160
        c = [(255, 120, 160), (255, 255, 255), (255, 200, 80)][i % 3]
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=c, outline=mix(c, (0, 0, 0), 0.3))
        d.point((int(x), int(y)), fill=(255, 240, 120))
    # curtains
    for side in (0, 1):
        for k in range(6):
            x0 = k * 10 if side == 0 else W - (k + 1) * 10
            sh = (150, 10, 30) if k % 2 else (200, 30, 50)
            d.rectangle([x0, 0, x0 + 9, 200 - k * 4], fill=sh)
    # stage
    d.rectangle([0, 200, W, H], fill=(60, 20, 30))
    d.rectangle([0, 200, W, 205], fill=(240, 190, 60))
    img = overlay(img, lambda ld: [ld.polygon([(W / 2 - 20, 0), (W / 2 + 20, 0), (W / 2 + 120, 210), (W / 2 - 120, 210)], fill=(255, 250, 220, 50)),
                                   ld.ellipse([W / 2 - 120, 196, W / 2 + 120, 216], fill=(255, 250, 220, 60))])
    d = ImageDraw.Draw(img)
    heavy = lt > dur * 0.45
    g = person(img, MAN, P_GROOM, 205, 206, 3, t, seed=1)
    b = person(img, GIRL, P_BRIDE, 275, 206, 3, t, seed=3)
    # veil and bouquet
    d.rectangle([b["x"] + 3, b["y"] + 3, b["x"] + b["w"] - 4, b["y"] + 6], fill=(255, 255, 255))
    d.point([(b["x"] + 8 + k * 6, b["y"] + 4) for k in range(5)], fill=(255, 150, 190))
    for k in range(5):
        d.ellipse([b["x"] - 2 + k * 3, b["y"] + 33 + (k % 2) * 2, b["x"] + 3 + k * 3, b["y"] + 38 + (k % 2) * 2], fill=(255, 90, 140))
    tears(d, g, lt, 3, heavy); tears(d, b, lt + 0.3, 3, heavy)
    # mic in front
    d.line([240, 206, 240, 166], fill=(60, 60, 70), width=2)
    d.ellipse([236, 160, 244, 168], fill=(180, 180, 190), outline=(40, 40, 50))
    if heavy and int(lt * 4) % 2 == 0:
        put_text(img, "呜哇~", 150, 120, (140, 220, 255), (20, 40, 80))
        put_text(img, "呜呜~", 335, 120, (140, 220, 255), (20, 40, 80))
    # audience
    for i in range(16):
        x = 15 + i * 30
        bob = int(abs(math.sin(t * 5 + i)) * 3 * (0.3 + BASS))
        y = 248 - bob
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(20, 10, 18))
        d.rectangle([x - 12, y + 6, x + 12, H], fill=(20, 10, 18))
    confetti(d, lt, 70, seed=v)
    return img

def sc_heart(lt, dur, v, t):
    tops = [((20, 10, 40), (80, 20, 70)), ((60, 120, 200), (200, 170, 230)), ((120, 30, 60), (255, 150, 80))][v]
    img = sky(*tops); d = ImageDraw.Draw(img)
    stars(d, t, 0.7 if v != 1 else 0.0)
    img = overlay(img, lambda ld: [ld.polygon([(W / 2, 92), (W / 2 + math.cos(t * 0.3 + k * 0.523) * 400, 92 + math.sin(t * 0.3 + k * 0.523) * 400),
                                               (W / 2 + math.cos(t * 0.3 + k * 0.523 + 0.2) * 400, 92 + math.sin(t * 0.3 + k * 0.523 + 0.2) * 400)],
                                              fill=(255, 200, 220, 30)) for k in range(12)])
    d = ImageDraw.Draw(img)
    p = clamp(lt / dur)
    s = 11 + int(BP * 1.5)
    hs = sprite(HEART, {'r': (230, 50, 80), 'w': (255, 200, 210)}, s)
    hx, hy = W // 2 - hs.width // 2, 92 - hs.height // 2
    img.paste(hs, (hx, hy), hs)
    d = ImageDraw.Draw(img)
    # windows inside heart
    hm = np.array(hs.getchannel("A")) > 0
    cells = []
    for cy in range(hy + 18, hy + hs.height - 20, 13):
        for cx in range(hx + 14, hx + hs.width - 14, 13):
            ly, lx = cy - hy, cx - hx
            if hm[ly:ly + 12, lx:lx + 11].all() if ly + 12 < hm.shape[0] and lx + 11 < hm.shape[1] else False:
                cells.append((cx, cy))
    for i, (cx, cy) in enumerate(cells):
        order = rnd(i, 5)
        lit = order < p * 1.3
        d.rectangle([cx, cy, cx + 9, cy + 9], fill=(255, 225, 120) if lit else (120, 20, 40), outline=(90, 10, 30))
        if lit:
            c = [(60, 110, 225), (225, 45, 70), (120, 80, 50), (140, 60, 150)][i % 4]
            d.rectangle([cx + 3, cy + 2, cx + 6, cy + 4], fill=SKIN)
            d.rectangle([cx + 2, cy + 5, cx + 7, cy + 9], fill=c)
    # walkers coming into heart
    pals = [P_GIRL, P_BOY, P_DAD1, P_MOM1, P_DAD2, P_MOM2]
    for i in range(10):
        age = (lt * 0.45 + i / 10) % 1.0
        side = -1 if i % 2 else 1
        sx = W / 2 + side * 250; sy = 210
        x = lerp(sx, W / 2, ease_in_out(age)); y = lerp(sy, 100, age ** 2)
        if age < 0.92:
            rows = GIRL if i % 3 == 0 else MAN
            person(img, rows, pals[i % 6], x, y, 1, t, flip=side > 0, bob=int(abs(math.sin(lt * 10 + i)) * 2), seed=i)
    # the guy below
    person(img, MAN, dict(P_BOY, d=(50, 50, 60), w=(200, 40, 40)), W // 2, 236, 3, t)
    d = ImageDraw.Draw(img)
    for k in range(6):
        y = 186 - k * 12 - int(lt * 30) % 12
        if y > hy + hs.height - 20: d.rectangle([W // 2 - 1, y, W // 2, y + 5], fill=(255, 180, 200))
    return img

def sc_toast(lt, dur, v, t):
    wall = [(110, 40, 30), (240, 200, 150), (150, 60, 40)][v]
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    walls(img, d, wall, (90, 50, 40), 200)
    # window behind
    win = sky(*[((20, 14, 50), (90, 50, 120)), ((120, 190, 255), (230, 240, 255)), ((255, 120, 60), (255, 200, 120))][v]).crop((0, 0, 120, 70))
    city(win, "far1", 78, t * 3, seed=11, hmin=40, hmax=110, wmin=16, wmax=34, col=(50, 26, 80), wincol=(140, 90, 160), lit=0.25)
    img.paste(win, (180, 24)); d.rectangle([178, 22, 301, 95], outline=(80, 40, 20), width=3)
    put_text(img, "福", 100, 40, (240, 190, 40), (120, 10, 10), scale=2)
    put_text(img, "福", 380, 40, (240, 190, 40), (120, 10, 10), scale=2)
    for i, x in enumerate((30, 150, 330, 450)): lantern(d, x, 20, t, i)
    p = lt / dur
    raise_g = ease_out(clamp((p % 0.5) / 0.25))
    # parents
    ppl = [(70, P_DAD1, MAN), (130, P_MOM1, GIRL), (350, P_MOM2, GIRL), (410, P_DAD2, MAN)]
    infos = []
    for i, (x, pal, rows) in enumerate(ppl):
        infos.append(person(img, rows, pal, x, 196, 3, t, seed=i, flip=x > 240))
    hero = person(img, MAN, dict(P_BOY, d=(200, 40, 50), w=(255, 220, 80)), 240, 196, 3, t, seed=5)
    d = ImageDraw.Draw(img)
    # table
    d.rectangle([0, 170, W, 210], fill=(200, 30, 40)); d.rectangle([0, 170, W, 174], fill=(240, 190, 60))
    for x in range(10, W, 28): d.line([x, 175, x + 4, 210], fill=(170, 20, 30))
    for i, x in enumerate(range(30, W, 60)):
        d.ellipse([x - 14, 176, x + 14, 186], fill=(250, 250, 250), outline=(180, 180, 190))
        fc = [(230, 120, 40), (120, 200, 90), (200, 60, 50), (240, 200, 90)][i % 4]
        d.ellipse([x - 9, 177, x + 9, 184], fill=fc)
    # raised glasses
    gy = 130 - int(raise_g * 34)
    glass(img, 240, gy, 2)
    for inf in infos:
        cx = inf["x"] + inf["w"] / 2
        glass(img, cx + (14 if cx < 240 else -14), 150 - int(raise_g * 18), 2)
    d = ImageDraw.Draw(img)
    if raise_g > 0.95:
        for k in range(8):
            a = k / 8 * 6.28 + t * 2
            sparkle(d, 240 + math.cos(a) * 16, gy - 4 + math.sin(a) * 12, 3)
        put_text(img, "干杯!", 240, gy - 34, (255, 230, 80), (100, 20, 20), scale=1)
    # labels
    if p < 0.5:
        bubble(img, d, 240, 60, "第二杯 → 家庭")
    else:
        bubble(img, d, 240, 60, "第一杯 → 四位父母")
        for inf in infos:
            heart_px(d, inf["x"] + inf["w"] / 2, inf["y"] - 10 - (lt * 20) % 14, 1)
    return img

def sc_daynight(lt, dur, v, t):
    cyc = (lt / 1.5) % 1.0  # 0..1 day+night
    sun_a = cyc * 2 * math.pi
    day = 0.5 + 0.5 * math.sin(sun_a)
    top = mix((10, 10, 40), (90, 170, 255), day); bot = mix((60, 30, 90), (255, 220, 170), day)
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    wall = mix((40, 34, 70), (240, 210, 170), day * 0.8 + 0.1)
    if v == 1: wall = mix(wall, (255, 200, 80), 0.3)
    walls(img, d, wall, mix((50, 30, 40), (150, 100, 70), day), 190)
    win = sky(top, bot).crop((0, 0, 200, 110)); wd = ImageDraw.Draw(win)
    stars(wd, t, 1 - day, 40)
    sx = 100 + math.cos(sun_a - math.pi / 2) * 80 * -1; sy = 100 - math.sin(sun_a) * 80
    wd.ellipse([sx - 10, sy - 10, sx + 10, sy + 10], fill=(255, 220, 80))
    mx = 100 - math.cos(sun_a - math.pi / 2) * 80 * -1; my = 100 + math.sin(sun_a) * 80
    wd.ellipse([mx - 8, my - 8, mx + 8, my + 8], fill=(240, 240, 255))
    city(win, "far1", 112, t * 2, seed=11, hmin=40, hmax=110, wmin=16, wmax=34, col=(50, 26, 80), wincol=(140, 90, 160), lit=0.25)
    img.paste(win, (30, 20)); d.rectangle([28, 18, 231, 131], outline=(100, 60, 30), width=3)
    d.line([130, 20, 130, 130], fill=(100, 60, 30), width=2); d.line([30, 75, 230, 75], fill=(100, 60, 30), width=2)
    # clock
    cx, cy = 400, 60
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(250, 250, 240), outline=(80, 50, 30), width=3)
    for k in range(12):
        a = k / 12 * 6.28
        d.point((int(cx + math.cos(a) * 21), int(cy + math.sin(a) * 21)), fill=(40, 40, 40))
    a1 = lt * 8; a2 = lt * 0.66
    d.line([cx, cy, cx + math.sin(a1) * 20, cy - math.cos(a1) * 20], fill=(30, 30, 30), width=1)
    d.line([cx, cy, cx + math.sin(a2) * 13, cy - math.cos(a2) * 13], fill=(200, 30, 30), width=2)
    # calendar
    day_n = 1 + int(lt / 0.75)
    d.rectangle([300, 40, 350, 92], fill=(255, 255, 255), outline=(80, 80, 80))
    d.rectangle([300, 40, 350, 52], fill=(220, 40, 40))
    put_text(img, f"{day_n}", 325, 58, (30, 30, 30), None, scale=1)
    put_text(img, "日夜", 325, 74, (120, 120, 120), None)
    # girl at desk
    g = person(img, GIRL, P_GIRL, 260, 200, 3, t)
    d = ImageDraw.Draw(img)
    d.rectangle([150, 172, 370, 182], fill=(130, 80, 40), outline=(70, 40, 20)); d.rectangle([160, 182, 170, 226], fill=(100, 60, 30)); d.rectangle([350, 182, 360, 226], fill=(100, 60, 30))
    # stacks
    left_h = 14 - int((lt * 4) % 14); right_h = int((lt * 4) % 14) + 2
    for k in range(left_h): d.rectangle([196, 170 - k * 2, 222, 171 - k * 2], fill=(240, 110, 120) if k % 2 else (200, 70, 80))
    for k in range(right_h): d.rectangle([298, 170 - k * 2, 324, 171 - k * 2], fill=(240, 110, 120) if k % 2 else (200, 70, 80))
    fp = (lt * 4) % 1.0
    bill(d, lerp(209, 311, fp), 160 - math.sin(fp * math.pi) * 40, fp * 6, 2)
    # lamp at night
    if day < 0.4:
        img = overlay(img, lambda ld: ld.polygon([(260, 110), (170, 182), (350, 182)], fill=(255, 230, 150, int(70 * (1 - day / 0.4)))))
        d = ImageDraw.Draw(img)
    total = int(lt * 123457) * (3 if v else 1)
    put_text(img, f"¥{total:,}", 260, 104, (255, 220, 60), (60, 20, 10), scale=1)
    if v == 1: money_rain(d, lt, 24, seed=9, speed=0.8, bills=False)
    return img

def sc_goodbye(lt, dur, v, t):
    if v == 0: top, bot = (60, 40, 120), (255, 150, 90)
    else: top, bot = (120, 160, 255), (255, 230, 170)
    img = sky(top, bot); d = ImageDraw.Draw(img)
    sun_y = 150 + (lt / dur) * 20 * (1 if v == 0 else -1)
    d.ellipse([W / 2 - 40, sun_y - 40, W / 2 + 40, sun_y + 40], fill=(255, 220, 140))
    for k in range(4): d.rectangle([W / 2 - 42, sun_y + 4 + k * 8, W / 2 + 42, sun_y + 6 + k * 8], fill=mix(top, bot, 0.8))
    mountains(d, 190, [((150, 80, 120), 60, 1, 6), ((100, 50, 100), 40, 3, 9)])
    d.rectangle([0, 190, W, H], fill=(60, 40, 60))
    for x in range(-30, W, 40):
        xx = x - int(lt * 30) % 40
        d.rectangle([xx, 214, xx + 18, 216], fill=(240, 220, 160))
    p = lt / dur
    # present couple on right
    person(img, MAN, dict(P_BOY, d=(200, 40, 50), w=(255, 220, 80)), 330, 206, 3, t, flip=True)
    person(img, GIRL, P_GIRL, 370, 206, 3, t, flip=True, seed=4)
    d = ImageDraw.Draw(img)
    d.rectangle([345, 172, 356, 175], fill=SKIN)  # holding hands
    # past self dissolving
    sp = sprite(BOY, P_PAST, 3, False, False)
    arr = np.array(sp).copy()
    dis = clamp((p - 0.35) / 0.6)
    hh, ww = arr.shape[:2]
    if dis > 0:
        yy, xx = np.mgrid[0:hh, 0:ww]
        r = ((np.sin((xx // 3) * 12.9898 + (yy // 3) * 78.233) * 43758.5453) % 1.0)
        r = r * 0.6 + (1 - yy / hh) * 0.4
        arr[r < dis, 3] = 0
    arr[..., 3] = (arr[..., 3] * 0.8).astype(np.uint8)
    gim = Image.fromarray(arr, "RGBA")
    gx, gy = 140 - ww // 2, 206 - hh
    img.paste(gim, (gx, gy), gim)
    d = ImageDraw.Draw(img)
    if dis > 0:
        for i in range(40):
            age = (lt * 0.8 + i / 40) % 1.0
            if rnd(i, 3) > dis + 0.2: continue
            x = gx + rnd(i, 1) * ww + math.sin(age * 5 + i) * 6
            y = gy + rnd(i, 2) * hh - age * 80
            c = mix((200, 200, 220), (255, 255, 255), age)
            d.rectangle([int(x), int(y), int(x) + 2, int(y) + 2], fill=c)
    if p < 0.5:
        bubble(img, d, 140, gy - 4, "再见啦,以前的我")
    # waving hand of girl
    wv = int(math.sin(lt * 10) * 3)
    d.rectangle([386 + wv, 150, 390 + wv, 156], fill=SKIN, outline=OUT_C)
    return img

def sc_account(lt, dur, v, t):
    img = sky((30, 20, 60), (90, 40, 100)); d = ImageDraw.Draw(img)
    city(img, "near1", 230, t * 5, seed=31, hmin=30, hmax=80, wmin=22, wmax=44, col=(28, 14, 44), wincol=(255, 210, 120), lit=0.35)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 220, W, H], fill=(40, 30, 50))
    half = dur / 2
    # phone slides in
    pp = ease_out(clamp((lt - 0.6) / 0.8))
    px = int(lerp(W + 10, 270, pp))
    d.rectangle([px, 26, px + 170, 210], fill=(20, 20, 28), outline=(200, 200, 220), width=2)
    d.rectangle([px + 8, 40, px + 162, 196], fill=(240, 245, 255))
    d.rectangle([px + 8, 40, px + 162, 62], fill=(220, 50, 60))
    put_text(img, "我的账户", px + 85, 43, (255, 255, 255), None)
    put_text(img, "余额(元)", px + 85, 72, (120, 120, 140), None)
    zeros = 0 if lt < 1.4 else min(9, int((lt - 1.4) * 2.2) + 1)
    amt = int("8" + "0" * zeros)
    s = f"{amt:,}"
    put_text(img, s, px + 85, 98, (220, 40, 50), None, scale=1 if len(s) > 9 else 2)
    d.rectangle([px + 20, 140, px + 150, 160], fill=(255, 200, 60), outline=(180, 120, 20))
    put_text(img, f"+{zeros} 个零", px + 85, 142, (120, 40, 10), None)
    d.ellipse([px + 78, 200, px + 92, 206], fill=(60, 60, 70))
    # hater
    squash = 0.0
    if lt > half:
        squash = clamp((lt - half) / (half * 0.8)) * 0.55
    sp = sprite(MAN, P_HATER, 3, False, False)
    nh = int(sp.height * (1 - squash)); nw = int(sp.width * (1 + squash * 0.6))
    sp2 = sp.resize((nw, nh), Image.NEAREST)
    hx = 110
    shake = int(math.sin(lt * 40) * 2) if lt > 1.4 else 0
    img.paste(sp2, (hx - nw // 2 + shake, 220 - nh), sp2)
    d = ImageDraw.Draw(img)
    if lt < 1.4:
        bubble(img, d, hx, 220 - nh - 4, "哈哈 崽种!")
    elif lt < half:
        put_text(img, "!?", hx, 220 - nh - 26, (255, 255, 120), (80, 20, 20), scale=2)
        # big eyes
        ex = hx - nw // 2 + 4 * 3 + shake; ey = 220 - nh + 6 * 3
        d.rectangle([ex - 2, ey - 2, ex + 3, ey + 3], fill=(255, 255, 255), outline=OUT_C)
        d.rectangle([ex + 13, ey - 2, ex + 18, ey + 3], fill=(255, 255, 255), outline=OUT_C)
    # falling zeros crush him
    if lt > half * 0.9:
        zt = lt - half * 0.9
        for i in range(min(7, int(zt * 3) + 1)):
            fall = clamp((zt - i / 3) / 0.35)
            target = 220 - nh - 30 - i * 34
            y = lerp(-60, target, fall ** 2)
            zi = fancy_text("0", 3, t, "white")
            img.paste(zi, (hx - zi.width // 2 + (i % 2) * 4 - 2, int(y)), zi)
    return img

def sc_heaven(lt, dur, v, t):
    img = sky((90, 170, 255), (255, 250, 230)); d = ImageDraw.Draw(img)
    img = overlay(img, lambda ld: [ld.polygon([(W / 2, 30), (W / 2 + math.cos(t * 0.5 + k * 0.4) * 500, 30 + math.sin(t * 0.5 + k * 0.4) * 500),
                                               (W / 2 + math.cos(t * 0.5 + k * 0.4 + 0.15) * 500, 30 + math.sin(t * 0.5 + k * 0.4 + 0.15) * 500)],
                                              fill=(255, 240, 150, 60)) for k in range(16)])
    d = ImageDraw.Draw(img)
    for i in range(6):
        x = (rnd(i, 1) * W + t * (6 + i * 2)) % (W + 80) - 60
        cloud(d, x, 50 + rnd(i, 2) * 120, 0.8 + rnd(i, 3) * 0.6)
    cloud(d, W / 2 - 60, 26, 2.2); cloud(d, W / 2 + 10, 20, 2.0)
    d.rectangle([0, 222, W, H], fill=(120, 200, 100)); d.rectangle([0, 222, W, 225], fill=(80, 160, 70))
    p = clamp(lt / dur)
    by = lerp(40, 150, ease_in_out(clamp(p / 0.8)))
    # glow
    for k in range(3):
        rr = 34 + k * 8 + int(BP * 4)
        d.ellipse([W / 2 - rr, by - rr + 8, W / 2 + rr, by + rr + 8], outline=(255, 230, 120))
    # bowl
    d.ellipse([W / 2 - 30, by - 14, W / 2 + 30, by + 4], fill=(255, 255, 255), outline=(200, 200, 200))
    for k in range(5): d.ellipse([W / 2 - 28 + k * 11, by - 20 + (k % 2) * 2, W / 2 - 14 + k * 11, by - 6], fill=(255, 255, 255))
    d.chord([W / 2 - 30, by - 30, W / 2 + 30, by + 26], 0, 180, fill=(60, 110, 200), outline=(30, 60, 140))
    for k in range(5): d.rectangle([W / 2 - 22 + k * 10, by + 6, W / 2 - 18 + k * 10, by + 10], fill=(255, 255, 255))
    d.rectangle([W / 2 - 10, by + 24, W / 2 + 10, by + 28], fill=(30, 60, 140))
    d.line([W / 2 + 8, by - 40, W / 2 + 26, by - 8], fill=(160, 90, 40), width=2)
    d.line([W / 2 + 14, by - 42, W / 2 + 30, by - 10], fill=(160, 90, 40), width=2)
    for k in range(3):
        x = W / 2 - 12 + k * 12
        for j in range(4):
            yy = by - 26 - j * 5 - (lt * 20) % 5
            d.point((int(x + math.sin(yy * 0.4 + k) * 2), int(yy)), fill=(255, 255, 255))
    put_text(img, "饭", W // 2, by - 12, (200, 40, 40), None)
    # hero
    person(img, MAN, dict(P_BOY, d=(200, 40, 50), w=(255, 220, 80)), W // 2, 236, 3, t)
    d = ImageDraw.Draw(img)
    d.rectangle([W // 2 - 22, 178, W // 2 - 18, 186], fill=SKIN, outline=OUT_C); d.rectangle([W // 2 + 18, 178, W // 2 + 22, 186], fill=SKIN, outline=OUT_C)
    # hater blown away
    hp = clamp((lt - dur * 0.5) / (dur * 0.4))
    hx = lerp(90, -60, ease_in_out(hp)); hy = 236 - math.sin(hp * math.pi) * 60
    if hp < 1:
        sp = sprite(MAN, P_HATER, 2, False, False).rotate(hp * 720, expand=True)
        img.paste(sp, (int(hx - sp.width / 2), int(hy - sp.height)), sp)
        if hp > 0: put_text(img, "嗖~", hx + 30, hy - 60, (255, 255, 255), (40, 40, 80))
    return img

def sc_dream(lt, dur, v, t):
    wake = lt > dur * 0.42
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    walls(img, d, (30, 30, 70) if not wake else (70, 60, 110), (40, 30, 50), 180)
    win = sky((8, 8, 30), (40, 30, 90)).crop((0, 0, 100, 80)); stars(ImageDraw.Draw(win), t, 1, 40)
    ImageDraw.Draw(win).ellipse([60, 10, 80, 30], fill=(250, 250, 220))
    img.paste(win, (330, 30)); d.rectangle([328, 28, 431, 111], outline=(90, 70, 60), width=3)
    # bed
    d.rectangle([90, 170, 330, 216], fill=(110, 70, 40), outline=(60, 30, 20))
    d.rectangle([80, 140, 96, 216], fill=(110, 70, 40), outline=(60, 30, 20))
    d.rectangle([100, 156, 150, 172], fill=(250, 250, 250), outline=(180, 180, 200))
    sit = ease_out(clamp((lt - dur * 0.45) / 0.3)) if wake else 0
    head = sprite(MAN[:9], P_BOY, 3, False, not wake)
    img.paste(head, (110, int(lerp(130, 104, sit))), head)
    d = ImageDraw.Draw(img)
    d.rectangle([140, 160, 330, 200], fill=(70, 110, 220), outline=(40, 60, 140))
    for x in range(150, 330, 20): d.rectangle([x, 170, x + 8, 178], fill=(100, 140, 240))
    if not wake:
        for i in range(3):
            age = (lt * 0.7 + i / 3) % 1.0
            put_text(img, "Z" if i % 2 else "z", 160 + age * 40 + i * 6, 120 - age * 60, (200, 210, 255), (30, 30, 80), scale=1 + (i % 2))
        # dream bubble with money
        d.ellipse([200, 30, 300, 100], fill=(230, 230, 255), outline=(150, 150, 200))
        d.ellipse([180, 100, 190, 110], fill=(230, 230, 255)); d.ellipse([168, 114, 174, 120], fill=(230, 230, 255))
        for i in range(4): bill(d, 230 + i * 12, 60 + (i % 2) * 8, lt * 3 + i, 2)
        put_text(img, "♪", 250, 36, (150, 80, 200), None)
    else:
        wt = lt - dur * 0.42
        bx, by = 135, 70
        r = int(14 + BP * 3)
        for k in range(12):
            a = k / 12 * 6.28 + lt
            d.line([bx + math.cos(a) * (r + 4), by + math.sin(a) * (r + 4), bx + math.cos(a) * (r + 14), by + math.sin(a) * (r + 14)], fill=(255, 240, 120), width=2)
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=(255, 245, 140), outline=(200, 160, 40))
        d.rectangle([bx - 6, by + r - 2, bx + 6, by + r + 8], fill=(160, 160, 170), outline=(90, 90, 100))
        d.line([bx - 4, by + 2, bx, by - 4, bx + 4, by + 2], fill=(220, 140, 30))
        notes(img, lt, 220, 150, 7)
        put_text(img, "灵感!", 135, 20, (255, 255, 120), (100, 50, 0), scale=1)
        if wt < 0.25:
            img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 240)), 0.8 * (1 - wt / 0.25))
    return img

def sc_wheat(lt, dur, v, t):
    img = sky((100, 170, 255), (255, 230, 170)); d = ImageDraw.Draw(img)
    d.ellipse([400, 20, 440, 60], fill=(255, 230, 100))
    mountains(d, 150, [((140, 170, 120), 40, 5, 7)])
    d.rectangle([0, 150, W, H], fill=(190, 140, 50))
    # player UI
    d.rectangle([110, 12, 370, 72], fill=(30, 26, 40), outline=(255, 255, 255), width=2)
    d.rectangle([118, 20, 158, 64], fill=(220, 60, 80))
    coin(d, 138, 42, 12, t * 2)
    d.polygon([(166, 24), (166, 38), (178, 31)], fill=(120, 255, 160))
    put_text(img, TITLE, 186, 22, (255, 255, 255), None, anchor="l")
    prog = clamp(lt / dur)
    d.rectangle([166, 48, 360, 52], fill=(80, 80, 90)); d.rectangle([166, 48, 166 + int(194 * prog), 52], fill=(120, 255, 160))
    plays = int(1000 + (lt / dur) ** 2 * 98765432)
    put_text(img, f"播放 {plays:,}", 264, 54, (255, 220, 80), None)
    # wheat = equalizer
    cut_x = lerp(-20, W + 20, clamp(lt / dur))
    for i in range(0, W, 6):
        base = 226 - (i % 12) // 2
        band = 0.5 + 0.5 * math.sin(i * 0.15 + t * 3) * math.sin(i * 0.07 - t * 2)
        hgt = 30 + int((band * 0.6 + E * 0.6) * 40)
        sway = int(math.sin(t * 3 + i * 0.1) * 3)
        if i < cut_x:
            d.line([i, base, i, base - 6], fill=(150, 110, 40))
            continue
        d.line([i, base, i + sway, base - hgt], fill=(200, 160, 50))
        d.ellipse([i + sway - 2, base - hgt - 9, i + sway + 2, base - hgt + 1], fill=(255, 210, 70), outline=(180, 130, 30))
    # bundles -> coins
    for i in range(8):
        x = 20 + i * 60
        if x < cut_x - 20:
            d.rectangle([x - 4, 200, x + 4, 224], fill=(230, 180, 60), outline=(150, 100, 30))
            d.rectangle([x - 5, 210, x + 5, 212], fill=(160, 90, 30))
            age = clamp((cut_x - 20 - x) / 80)
            if age < 1: coin(d, x, 196 - age * 40, 5, t * 8 + i)
    person(img, MAN, dict(P_BOY, d=(200, 40, 50), w=(255, 220, 80)), cut_x, 228, 3, t, flip=False)
    d = ImageDraw.Draw(img)
    a = math.sin(t * 10) * 0.8
    hx, hy = cut_x + 16, 186
    d.line([hx, hy, hx + 10, hy - 14], fill=(110, 70, 30), width=2)
    d.arc([hx - 2 + math.cos(a) * 2, hy - 30, hx + 22, hy - 6], 200, 340, fill=(220, 220, 230), width=2)
    return img

def sc_car(lt, dur, v, t):
    img = sky((255, 170, 120), (255, 230, 190)); d = ImageDraw.Draw(img)
    city(img, "far2", 170, 40, seed=51, hmin=50, hmax=120, wmin=20, wmax=40, col=(220, 150, 140), wincol=(255, 230, 200), lit=0.3)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 170, W, H], fill=(90, 90, 100)); d.rectangle([0, 170, W, 176], fill=(200, 200, 200))
    for x in range(0, W, 40): d.rectangle([x, 214, x + 20, 216], fill=(250, 240, 200))
    p = ease_out(clamp(lt / 1.2))
    cx = int(lerp(W + 80, 250, p))
    draw_car(d, cx, 210, (220, 30, 50), t * (1 - p) * 3, 2)
    # bow
    d.polygon([(cx - 6, 140), (cx - 26, 128), (cx - 26, 152)], fill=(255, 210, 40), outline=(160, 110, 20))
    d.polygon([(cx + 6, 140), (cx + 26, 128), (cx + 26, 152)], fill=(255, 210, 40), outline=(160, 110, 20))
    d.rectangle([cx - 6, 134, cx + 6, 146], fill=(255, 230, 80), outline=(160, 110, 20))
    d.line([cx, 146, cx, 166], fill=(255, 210, 40), width=3)
    if p > 0.9:
        for i in range(6):
            k = (int(t * 5) + i * 5) % 17
            sparkle(d, cx - 70 + rnd(k, 1) * 140, 150 + rnd(k, 2) * 50, 3)
    dad = person(img, MAN, P_DAD1, 80, 226, 3, t, seed=1)
    person(img, MAN, dict(P_BOY, d=(200, 40, 50), w=(255, 220, 80)), 410, 226, 3, t, flip=True)
    d = ImageDraw.Draw(img)
    if lt > 1.2:
        kp = clamp((lt - 1.2) / 0.8)
        kx = lerp(395, 100, kp); ky = 186 - math.sin(kp * math.pi) * 70
        d.ellipse([kx - 4, ky - 4, kx + 4, ky + 4], outline=(255, 210, 40), width=2)
        d.line([kx + 4, ky, kx + 12, ky], fill=(255, 210, 40), width=2); d.line([kx + 10, ky, kx + 10, ky + 3], fill=(255, 210, 40))
    if lt > 2.0:
        bubble(img, d, 80, dad["y"] - 4, "儿子!")
        for i in range(3): heart_px(d, 60 + i * 20, dad["y"] - 30 - (lt * 20 + i * 7) % 20, 1)
    else:
        bubble(img, d, 410, 150, "爸,给你的!")
    return img

def sc_seasons(lt, dur, v, t):
    k = min(3, int(lt / dur * 4))
    cols = [((255, 190, 220), (255, 240, 240), (140, 200, 120)), ((80, 180, 255), (200, 240, 255), (90, 190, 80)),
            ((230, 120, 50), (255, 210, 130), (170, 110, 50)), ((140, 160, 200), (230, 235, 250), (240, 240, 250))][k]
    img = sky(cols[0], cols[1]); d = ImageDraw.Draw(img)
    d.rectangle([0, 200, W, H], fill=cols[2])
    for i in range(5):
        x = 40 + i * 100
        d.rectangle([x - 3, 140, x + 3, 200], fill=(100, 60, 40))
        tc = [(255, 170, 200), (60, 160, 60), (230, 130, 40), (255, 255, 255)][k]
        d.ellipse([x - 26, 100, x + 26, 150], fill=tc)
    for i in range(50):
        sp = 30 + rnd(i, 1) * 30
        x = (rnd(i, 2) * W + math.sin(lt * 3 + i) * 10 + (lt * 20 if k != 3 else 0)) % W
        y = (rnd(i, 3) * 280 + lt * sp) % 280
        c = [(255, 200, 220), None, (220, 100, 30), (255, 255, 255)][k]
        if c: d.rectangle([int(x), int(y), int(x) + 1, int(y) + 1], fill=c)
    if k == 1:
        d.ellipse([380, 20, 430, 70], fill=(255, 230, 60))
    names = ["春", "夏", "秋", "冬"]
    put_text(img, names[k], 40, 20, (255, 255, 255), (60, 30, 30), scale=3, anchor="l")
    # rapper with mic + nosebleed
    info = person(img, MAN, dict(P_BOY, d=(30, 30, 30), w=(255, 255, 255)), W // 2, 214, 3, t)
    d = ImageDraw.Draw(img)
    d.line([W // 2 + 30, 214, W // 2 + 30, 160], fill=(60, 60, 70), width=2)
    d.ellipse([W // 2 + 25, 152, W // 2 + 35, 162], fill=(180, 180, 190), outline=(30, 30, 30))
    nx, ny = info["x"] + info["w"] // 2, info["y"] + 7 * 3 + 2
    d.rectangle([nx - 4, ny, nx - 3, ny + 5], fill=(220, 20, 30)); d.rectangle([nx + 2, ny, nx + 3, ny + 4], fill=(220, 20, 30))
    for i in range(4):
        age = (lt * 1.5 + i / 4) % 1.0
        d.rectangle([nx - 4, ny + 6 + age * 40, nx - 3, ny + 8 + age * 40], fill=(220, 20, 30))
    put_text(img, f"第{k + 1}季", W - 70, 24, (255, 255, 255), (40, 40, 40), scale=2)
    return img

def sepia(img, amt):
    a = np.asarray(img).astype(np.float32)
    g = a @ np.array([0.299, 0.587, 0.114])
    s = np.stack([g * 1.07 + 20, g * 0.9 + 10, g * 0.65], -1)
    a = a * (1 - amt) + np.clip(s, 0, 255) * amt
    noise = (np.random.default_rng(int(amt * 1000) + int(E * 99)).random((H // 3 + 1, W // 3 + 1)) * 24 - 12)
    noise = np.repeat(np.repeat(noise, 3, 0), 3, 1)[:H, :W]
    a += noise[..., None] * amt
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def sc_guiyang(lt, dur, v, t):
    img = sky((150, 200, 230), (230, 240, 240)); d = ImageDraw.Draw(img)
    karst(d, 150, (130, 170, 160), 3, 9, 70, 60)
    d.rectangle([0, 130, W, 140], fill=(220, 230, 230))
    karst(d, 175, (80, 130, 110), 7, 8, 60, 70)
    city(img, "gy", 200, t * 10, seed=71, hmin=30, hmax=90, wmin=18, wmax=36, col=(110, 120, 140), wincol=(200, 220, 240), lit=0.4)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 200, W, H], fill=(80, 80, 90))
    for x in range(-40, W, 40): d.rectangle([x + 40 - int(lt * 60) % 40, 228, x + 60 - int(lt * 60) % 40, 230], fill=(240, 240, 200))
    second = lt > 1.6
    # sign
    sy = 40
    d.rectangle([340, sy + 60, 344, 200], fill=(140, 140, 150)); d.rectangle([440, sy + 60, 444, 200], fill=(140, 140, 150))
    d.rectangle([326, sy, 458, sy + 62], fill=(20, 120, 60), outline=(255, 255, 255), width=2)
    put_text(img, "贵阳 →", 392, sy + 8, (255, 255, 255), None)
    put_text(img, "← 毕节", 392, sy + 32, (255, 255, 255), None)
    if not second:
        d.rectangle([330, sy + 4, 454, sy + 26], outline=(255, 230, 80), width=1 if int(t * 6) % 2 else 2)
    else:
        d.rectangle([330, sy + 28, 454, sy + 50], outline=(255, 230, 80), width=1 if int(t * 6) % 2 else 2)
    # boy with boombox walking
    bx = 170 + math.sin(lt) * 6
    info = person(img, BOY, dict(P_BOY, c=(220, 40, 40), C=(30, 30, 30)), bx, 226, 3, t, bob=int(abs(math.sin(lt * 8)) * 3))
    d = ImageDraw.Draw(img)
    x0, y0 = int(bx + 8), info["y"] + 4
    d.rectangle([x0, y0, x0 + 40, y0 + 22], fill=(50, 50, 60), outline=(200, 200, 210))
    r = 5 + int(BASS * 3)
    for cx in (x0 + 9, x0 + 31):
        d.ellipse([cx - r, y0 + 11 - r, cx + r, y0 + 11 + r], fill=(20, 20, 20), outline=(150, 150, 160))
    d.rectangle([x0 + 16, y0 + 4, x0 + 24, y0 + 10], fill=(255, 200, 80))
    notes(img, lt, x0 + 20, y0, 4, (255, 255, 255))
    if second:
        put_text(img, "那时的说唱", 120, 30, (255, 240, 200), (80, 50, 20), scale=2)
        img = sepia(img, clamp((lt - 1.6) / 0.5) * 0.85)
    return img

def small_room(img, d, t, warm=False):
    wall = (70, 90, 70) if not warm else (150, 100, 70)
    walls(img, d, wall, (60, 50, 40), 196)
    for i in range(8):
        x = rnd(i, 4) * W; y = rnd(i, 5) * 150 + 20
        d.rectangle([x, y, x + 12, y + 6], fill=mix(wall, (0, 0, 0), 0.25))
    d.rectangle([0, 0, W, 14], fill=(40, 40, 40))
    win = sky((40, 50, 70), (90, 100, 120)).crop((0, 0, 70, 50)); wd = ImageDraw.Draw(win)
    for i in range(20):
        x = (rnd(i, 1) * 70 + t * 30) % 70; y = (rnd(i, 2) * 50 + t * 120) % 50
        wd.line([x, y, x - 2, y + 5], fill=(170, 190, 220))
    img.paste(win, (380, 50)); d.rectangle([378, 48, 451, 101], outline=(40, 30, 20), width=3)
    d.rectangle([40, 50, 90, 110], fill=(30, 30, 30)); put_text(img, "HIP", 65, 58, (255, 220, 60), None); put_text(img, "HOP", 65, 80, (255, 80, 80), None)
    sw = math.sin(t * 1.6) * 14
    d.line([240, 14, 240 + sw, 60], fill=(20, 20, 20))
    d.ellipse([240 + sw - 6, 58, 240 + sw + 6, 70], fill=(255, 240, 160))
    return 240 + sw, 64

def sc_hotdog(lt, dur, v, t):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    lx, ly = small_room(img, d, t)
    img = overlay(img, lambda ld: ld.polygon([(lx, ly), (lx - 160, 230), (lx + 160, 230)], fill=(255, 240, 160, 40)))
    d = ImageDraw.Draw(img)
    d.rectangle([60, 206, 200, 222], fill=(200, 200, 220), outline=(120, 120, 140))  # mattress
    info = person(img, MAN, dict(P_BOY, d=(120, 60, 160), w=(255, 255, 255)), 250, 224, 3, t)
    d = ImageDraw.Draw(img)
    # sunglasses (yuppie)
    ex1, ey1 = info["eyes"][0]; ex2, ey2 = info["eyes"][1]
    d.rectangle([ex1 - 4, ey1 - 4, ex1 + 4, ey1 + 1], fill=(10, 10, 10)); d.rectangle([ex2 - 4, ey2 - 4, ex2 + 4, ey2 + 1], fill=(10, 10, 10))
    d.line([ex1 + 4, ey1 - 3, ex2 - 4, ey2 - 3], fill=(10, 10, 10))
    d.point([(ex1 - 2, ey1 - 3), (ex2 - 2, ey2 - 3)], fill=(255, 255, 255))
    # hotdog
    bites = min(3, int(lt / dur * 4))
    hx, hy = info["x"] + info["w"] - 4, info["y"] + 24
    L = 30 - bites * 7
    d.rounded_rectangle([hx - 4, hy, hx - 4 + L, hy + 9], 4, fill=(230, 180, 100), outline=(150, 100, 40))
    d.rounded_rectangle([hx - 6, hy + 2, hx - 2 + L + 2, hy + 7], 3, fill=(200, 70, 50), outline=(130, 30, 20))
    d.line([hx, hy + 3, hx + L - 6, hy + 3], fill=(255, 220, 40))
    for i in range(3):
        yy = hy - 6 - ((lt * 18 + i * 5) % 14)
        d.point((int(hx + 6 + i * 6 + math.sin(yy) * 2), int(yy)), fill=(255, 255, 255))
    # price tag
    tx, ty = hx + 50, hy - 30
    d.polygon([(tx + math.cos(a * 0.785) * (24 if a % 2 else 16), ty + math.sin(a * 0.785) * (24 if a % 2 else 16)) for a in range(8)], fill=(255, 220, 40), outline=(200, 60, 30))
    put_text(img, "¥2", tx, ty - 8, (200, 30, 30), None)
    if bites < 3:
        put_text(img, "啊呜~", hx - 10, info["y"] - 20, (255, 255, 255), (60, 30, 30))
    return img

def sc_wife(lt, dur, v, t):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    lx, ly = small_room(img, d, t, warm=True)
    img = overlay(img, lambda ld: ld.ellipse([lx - 200, ly - 60, lx + 200, 300], fill=(255, 210, 160, 50)))
    boy = person(img, MAN, dict(P_BOY, d=(120, 60, 160)), 210, 224, 3, t, bob=0, seed=2)
    girl = person(img, GIRL, P_GIRL, 270, 224, 3, t, flip=True, seed=1)
    d = ImageDraw.Draw(img)
    pat = int(abs(math.sin(lt * 7)) * 4)
    d.rectangle([boy["x"] + 20, boy["y"] - 4 - pat, boy["x"] + 34, boy["y"] + 1 - pat], fill=SKIN, outline=OUT_C)
    d.line([girl["x"] + 3, girl["y"] + 33, boy["x"] + 30, boy["y"] - pat], fill=OUT_C, width=3)
    d.line([girl["x"] + 3, girl["y"] + 33, boy["x"] + 30, boy["y"] - pat], fill=(225, 45, 70), width=1)
    for i in range(6):
        age = (lt * 0.6 + i / 6) % 1.0
        heart_px(d, 240 + (rnd(i, 1) - 0.5) * 120 + math.sin(age * 8) * 5, 180 - age * 140, 1 + i % 2)
    msgs = ["他只是累了", "他会成功的", "别怪他嘛"]
    m = msgs[min(2, int(lt / dur * 3))]
    bubble(img, d, girl["x"] + girl["w"] // 2 + 20, girl["y"] - 6, m)
    return img

def sc_hunter(lt, dur, v, t):
    flash = (lt % 1.6) < 0.08
    img = sky((50, 55, 70), (110, 110, 120)) if not flash else sky((200, 200, 230), (255, 255, 255))
    d = ImageDraw.Draw(img)
    mountains(d, 180, [((70, 75, 85), 60, 9, 6), ((55, 60, 70), 40, 11, 8)])
    d.rectangle([0, 180, W, H], fill=(70, 70, 55))
    for i in range(6):
        d.ellipse([rnd(i, 1) * W, 200 + rnd(i, 2) * 30, rnd(i, 1) * W + 40, 206 + rnd(i, 2) * 30], fill=(100, 110, 130))
    if flash:
        d.line([300, 0, 290, 40, 310, 70, 295, 110], fill=(255, 255, 220), width=2)
    info = person(img, MAN, dict(P_BOY, d=(90, 80, 60), w=(120, 100, 70), l=(60, 50, 40)), 220, 224, 3, t, bob=0)
    d = ImageDraw.Draw(img)
    # bow on back
    d.arc([info["x"] - 14, info["y"] + 20, info["x"] + 10, info["y"] + 60], 100, 260, fill=(140, 90, 40), width=2)
    d.line([info["x"] - 4, info["y"] + 22, info["x"] - 4, info["y"] + 58], fill=(220, 220, 220))
    # hoe: trying to lift
    ang = 0.15 + abs(math.sin(lt * 5)) * 0.12
    hx, hy = info["x"] + info["w"] - 4, info["y"] + 38
    ex, ey = hx + math.cos(ang) * 60, hy + math.sin(ang) * 60
    d.line([hx, hy, ex, ey], fill=(130, 90, 50), width=3)
    d.polygon([(ex, ey - 2), (ex + 4, ey - 2), (ex + 2, ey + 14), (ex - 6, ey + 14)], fill=(150, 150, 160), outline=(60, 60, 70))
    for i in range(3):
        age = (lt * 1.5 + i / 3) % 1.0
        d.rectangle([info["x"] + 4 + i * 12, info["y"] + 10 + age * 20, info["x"] + 5 + i * 12, info["y"] + 12 + age * 20], fill=(150, 210, 255))
    put_text(img, "嘿…咻…", ex, info["y"] - 4, (220, 220, 230), (40, 40, 50))
    for i in range(140):
        x = (rnd(i, 1) * (W + 60) - t * 60) % (W + 60)
        y = (rnd(i, 2) * H + t * 260) % H
        d.line([x, y, x - 3, y + 8], fill=(160, 170, 200))
    return img

def sc_feast(lt, dur, v, t):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    walls(img, d, (120, 30, 40), (90, 40, 30), 180)
    for x in range(0, W, 60): d.rectangle([x + 20, 30, x + 40, 160], fill=(150, 50, 50), outline=(220, 170, 60))
    d.line([240, 0, 240, 30], fill=(200, 160, 60))
    d.polygon([(200, 30), (280, 30), (260, 50), (220, 50)], fill=(250, 210, 80), outline=(160, 110, 30))
    for k in range(6):
        sparkle(d, 205 + k * 14, 56 + (k % 2) * 4, 2 + int((t * 4 + k) % 3))
    boy = person(img, MAN, dict(P_BOY, d=(30, 30, 40), w=(200, 30, 50)), 240, 172, 3, t, bob=0)
    d = ImageDraw.Draw(img)
    d.ellipse([60, 150, 420, 230], fill=(250, 240, 230), outline=(200, 180, 160))
    d.ellipse([140, 168, 340, 212], fill=(220, 200, 180), outline=(180, 160, 140))
    dishes = [(230, 120, 40), (140, 80, 40), (220, 40, 40), (90, 180, 70), (250, 230, 120), (180, 120, 200), (240, 160, 160), (120, 70, 30)]
    for i, c in enumerate(dishes):
        a = i / len(dishes) * 6.28 + lt * 0.6
        x = 240 + math.cos(a) * 140; y = 190 + math.sin(a) * 28
        d.ellipse([x - 16, y - 7, x + 16, y + 7], fill=(255, 255, 255), outline=(180, 180, 190))
        d.ellipse([x - 11, y - 5, x + 11, y + 4], fill=c)
        if i % 2 == 0:
            for j in range(2): d.point((int(x - 3 + j * 6), int(y - 9 - (lt * 12 + j * 3) % 6)), fill=(255, 255, 255))
    # gloom cloud
    cloud(d, 210, boy["y"] - 22, 1.0, (90, 90, 110))
    for i in range(6):
        y = boy["y"] - 10 + (lt * 40 + i * 6) % 18
        d.line([214 + i * 6, y, 213 + i * 6, y + 3], fill=(140, 180, 240))
    bubble(img, d, 330, 120, "没胃口…")
    return img

def sc_sew(lt, dur, v, t):
    img = sky((10, 10, 30), (40, 30, 70)); d = ImageDraw.Draw(img)
    stars(d, t, 0.8)
    d.ellipse([30, 20, 60, 50], fill=(250, 250, 220)); d.ellipse([38, 16, 68, 46], fill=(10, 10, 30))
    p = clamp(lt / dur)
    nightn = min(365, 1 + int(ease_in_out(clamp(p / 0.7)) * 364))
    # calendar
    d.rectangle([40, 70, 150, 200], fill=(250, 250, 250), outline=(80, 80, 80), width=2)
    d.rectangle([40, 70, 150, 94], fill=(200, 30, 40))
    put_text(img, "夜", 95, 74, (255, 255, 255), None)
    put_text(img, f"{nightn}", 95, 118, (30, 30, 30), None, scale=3)
    if p < 0.7:
        fp = (lt * 8) % 1.0
        d.polygon([(40, 94), (150, 94), (150 - fp * 40, 94 + fp * 60), (40 + fp * 20, 94 + fp * 100)], fill=(230, 230, 230), outline=(160, 160, 160))
    put_text(img, "/ 365 夜", 95, 168, (200, 30, 40), None)
    # heart with wound
    fold = clamp((p - 0.6) / 0.3)
    hs = sprite(HEART, {'r': (220, 60, 90), 'w': (255, 190, 200)}, 12)
    hw = max(4, int(hs.width * (1 - fold * 0.5)))
    hs2 = hs.resize((hw, hs.height), Image.NEAREST)
    hx, hy = 320 - hw // 2, 50
    img.paste(hs2, (hx, hy), hs2)
    d = ImageDraw.Draw(img)
    path = [(hx + hw * (0.3 + 0.4 * k / 10), hy + 30 + k * 6 + (6 if k % 2 else -6) * (1 - fold)) for k in range(11)]
    sp = clamp(p / 0.6)
    ni = int(sp * 10)
    for k in range(10):
        a, b = path[k], path[k + 1]
        if k >= ni:
            d.line([a, b], fill=(90, 10, 30), width=3)
        else:
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            d.line([mx - 6, my - 2, mx + 6, my + 2], fill=(255, 255, 255), width=1)
            d.line([a, b], fill=(160, 40, 60), width=1)
    if fold < 1 and sp < 1:
        nx, ny = path[min(10, ni)]
        bob = math.sin(lt * 20) * 4
        d.line([nx, ny + bob, nx + 24, ny - 18 + bob], fill=(220, 220, 230), width=2)
        d.point((int(nx + 22), int(ny - 16 + bob)), fill=(30, 30, 30))
        d.line([nx + 24, ny - 18 + bob, nx + 60, ny - 40, nx + 90, ny - 10], fill=(255, 120, 150))
    if fold > 0:
        d.line([hx + hw - 2, hy + 6, hx + hw - 2, hy + hs.height - 20], fill=(150, 30, 60), width=2)
        if fold > 0.8:
            d.rectangle([hx + 8, hy + 50, hx + hw - 8, hy + 66], fill=(255, 240, 200), outline=(200, 170, 130))
            d.line([hx + 8, hy + 58, hx + hw - 8, hy + 58], fill=(220, 190, 150))
            put_text(img, "藏好了", 320, 182, (255, 220, 230), (60, 10, 30))
    return img

def sc_speaker(lt, dur, v, t):
    img = sky((20, 0, 40), (60, 0, 80)); d = ImageDraw.Draw(img)
    img = overlay(img, lambda ld: [ld.polygon([(W / 2, H / 2), (W / 2 + math.cos(k * 0.39 + t) * 500, H / 2 + math.sin(k * 0.39 + t) * 500),
                                               (W / 2 + math.cos(k * 0.39 + t + 0.18) * 500, H / 2 + math.sin(k * 0.39 + t + 0.18) * 500)],
                                              fill=(255, 60, 200, 40)) for k in range(16)])
    d = ImageDraw.Draw(img)
    hit = [0.0, 0.5, 1.0]
    last = max([h for h in hit if h <= lt] or [0])
    since = lt - last
    pulse = clamp(1 - since / 0.35)
    for cx in (80, 400):
        d.rectangle([cx - 60, 40, cx + 60, 230], fill=(30, 30, 36), outline=(120, 120, 140), width=3)
        for cy, r0 in ((90, 26), (175, 40)):
            r = int(r0 + pulse * 8 + BASS * 4)
            d.ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], fill=(70, 70, 80))
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(15, 15, 18), outline=(150, 150, 170))
            d.ellipse([cx - r // 3, cy - r // 3, cx + r // 3, cy + r // 3], fill=(90, 90, 100))
        for k in range(3):
            rr = int(since * 300) + k * 25
            if rr < 300: d.ellipse([cx - rr, 175 - rr, cx + rr, 175 + rr], outline=mix((60, 0, 80), (255, 120, 255), clamp(1 - rr / 300)))
    n = sum(1 for h in hit if h <= lt)
    for i in range(n):
        ti = fancy_text("咚", 4 if i == n - 1 else 2, t, "pink")
        f = 1 + (pulse * 0.4 if i == n - 1 else 0)
        ti = ti.resize((int(ti.width * f), int(ti.height * f)), Image.NEAREST)
        img.paste(ti, (W // 2 - ti.width // 2 + (i - 1) * 50 * (i != n - 1), 70 - ti.height // 2 + i * 30 * (i != n - 1)), ti)
    return img

def sc_epitaph(lt, dur, v, t):
    img = sky((10, 14, 30), (40, 50, 80)); d = ImageDraw.Draw(img)
    stars(d, t)
    d.ellipse([380, 20, 420, 60], fill=(240, 240, 220))
    d.ellipse([-60, 190, 540, 360], fill=(30, 40, 40))
    # stone
    d.rounded_rectangle([200, 70, 300, 220], 30, fill=(140, 140, 150), outline=(60, 60, 70), width=2)
    d.line([206, 100, 206, 210], fill=(170, 170, 180))
    txt = ["此生热爱", "押韵到底"]
    total = 8
    shown = int(clamp(lt / (dur * 0.9)) * total + 0.5)
    k = 0
    for col, line in enumerate(txt):
        for j, ch in enumerate(line):
            if k < shown:
                put_text(img, ch, 264 - col * 28, 92 + j * 26, (60, 60, 70), (170, 170, 180))
            k += 1
    # carver
    info = person(img, MAN, dict(P_BOY, d=(70, 70, 90), w=(200, 200, 210)), 140, 230, 3, t, bob=0)
    d = ImageDraw.Draw(img)
    cur = min(7, shown)
    tx = 264 - (cur // 4) * 28 + 8; ty = 92 + (cur % 4) * 26 + 8
    hammer = abs(math.sin(lt * 14))
    d.line([info["x"] + info["w"] - 4, info["y"] + 34, tx - 4, ty], fill=(180, 180, 190), width=2)
    hx, hy = tx - 22, ty - 10 - hammer * 12
    d.line([info["x"] + info["w"] - 6, info["y"] + 30, hx, hy], fill=(120, 80, 40), width=2)
    d.rectangle([hx - 4, hy - 4, hx + 4, hy + 2], fill=(90, 90, 100))
    if hammer < 0.3:
        for i in range(6):
            a = rnd(i + int(lt * 14), 1) * 6.28
            sparkle(d, tx + math.cos(a) * 8, ty + math.sin(a) * 8, 2, (255, 220, 120))
    img = overlay(img, lambda ld: [ld.ellipse([x - 80, 205, x + 80, 245], fill=(200, 210, 230, 30)) for x in ((t * 20) % (W + 160) - 80, (t * 12 + 250) % (W + 160) - 80)])
    return img

def sc_pop(lt, dur, v, t):
    img = sky((20, 10, 30), (50, 20, 60)); d = ImageDraw.Draw(img)
    pop_t = dur * 0.45
    img = overlay(img, lambda ld: [ld.line([W / 2 + math.cos(k * 0.21) * 60, 120 + math.sin(k * 0.21) * 60,
                                            W / 2 + math.cos(k * 0.21) * 400, 120 + math.sin(k * 0.21) * 400], fill=(255, 255, 255, 30), width=2) for k in range(30)])
    d = ImageDraw.Draw(img)
    sq = clamp(lt / pop_t)
    if lt < pop_t:
        r = 30; rx = int(r * (1 - sq * 0.5)); ry = int(r * (1 + sq * 0.2))
        for k in range(3):
            g = rx + 6 + k * 5
            d.ellipse([W / 2 - g, 120 - ry - 6 - k * 5, W / 2 + g, 120 + ry + 6 + k * 5], outline=(60, 200 - k * 40, 180 - k * 40))
        d.ellipse([W / 2 - rx, 120 - ry, W / 2 + rx, 120 + ry], fill=(80, 230, 200), outline=(20, 120, 100), width=2)
        d.ellipse([W / 2 - rx + 6, 120 - ry + 6, W / 2 - rx + 14, 120 - ry + 14], fill=(220, 255, 250))
        # tiny hater face inside
        d.rectangle([W / 2 - 6, 116, W / 2 - 3, 119], fill=(30, 30, 30)); d.rectangle([W / 2 + 3, 116, W / 2 + 6, 119], fill=(30, 30, 30))
        d.line([W / 2 - 4, 128, W / 2 + 4, 126], fill=(30, 30, 30))
        if sq > 0.5: put_text(img, "救命!", W // 2, 70, (255, 255, 255), (30, 30, 60))
        fx = rx + 4
    else:
        fx = 12
        at = lt - pop_t
        cols = [(255, 80, 120), (80, 230, 200), (255, 220, 60), (140, 160, 255)]
        for k, c in enumerate(cols):
            burst(d, W / 2, 120, at * 1.2, c, 20, 70 + k * 25, seed=k * 7)
        rr = int(at * 260)
        d.ellipse([W / 2 - rr, 120 - rr, W / 2 + rr, 120 + rr], outline=(255, 255, 255), width=2)
        ti = fancy_text("啪!", 4, t, "cyan")
        img.paste(ti, (W // 2 - ti.width // 2, 40), ti)
        if at < 0.15:
            img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), 0.8)
        d = ImageDraw.Draw(img)
    # hand pinching
    for side in (-1, 1):
        x = W / 2 + side * fx
        d.rectangle([x - 7 if side < 0 else x, 110, x + 7 if side > 0 else x, 220], fill=SKIN, outline=OUT_C)
        d.rectangle([x - 7 if side < 0 else x, 110, x + 7 if side > 0 else x, 116], fill=(255, 230, 220), outline=OUT_C)
    d.rectangle([W / 2 - fx - 30, 200, W / 2 + fx + 30, 270], fill=SKIN, outline=OUT_C)
    return img

FW_COLS = [(255, 90, 140), (255, 220, 70), (100, 220, 255), (160, 255, 140), (220, 140, 255)]
def fireworks(d, t, rate=1.0, seed=0, area=(40, 20, 440, 120)):
    for i in range(6):
        per = 1.6 / rate
        age = ((t + i * per / 6 * 1.0) % per) / 1.0
        idx = int((t + i * per / 6) / per) * 6 + i + seed
        cx = area[0] + rnd(idx, 1) * (area[2] - area[0]); cy = area[1] + rnd(idx, 2) * (area[3] - area[1])
        if age < 0.3:
            y = lerp(H, cy, age / 0.3)
            d.rectangle([int(cx), int(y), int(cx), int(y) + 3], fill=(255, 240, 200))
        else:
            burst(d, cx, cy, (age - 0.3), FW_COLS[idx % 5], 28, 40 + rnd(idx, 3) * 30, seed=idx)

def sc_bridge(lt, dur, v, t):
    img = sky((10, 6, 40), (110, 30, 120)); d = ImageDraw.Draw(img)
    stars(d, t)
    # EQ in sky
    for i in range(48):
        x = i * 10 + 2
        hgt = int((0.3 + 0.7 * abs(math.sin(i * 0.7 + t * 4) * math.cos(i * 0.23 - t * 2.3))) * (10 + E * 60))
        c = mix((80, 220, 255), (255, 80, 200), i / 48)
        for y in range(0, hgt, 3):
            d.rectangle([x, 4 + y, x + 6, 5 + y], fill=c)
    if lt > dur / 2:
        fireworks(d, lt, 1.6, seed=3, area=(40, 40, 440, 110))
    speed = 140
    city(img, "far1", 170, lt * speed * 0.2, seed=11, hmin=40, hmax=110, wmin=16, wmax=34, col=(50, 26, 80), wincol=(140, 90, 160), lit=0.25)
    city(img, "near1", 196, lt * speed * 0.5, seed=31, hmin=30, hmax=80, wmin=22, wmax=44, col=(28, 14, 44), wincol=(255, 210, 120), lit=0.35)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 196, W, H], fill=(40, 36, 50)); d.rectangle([0, 196, W, 199], fill=(90, 90, 110))
    off = int(lt * speed) % 60
    for x in range(-60, W + 60, 60): d.rectangle([x - off, 224, x - off + 30, 226], fill=(250, 230, 120))
    for x in range(-120, W + 120, 120):
        lx = x - int(lt * speed * 1.0) % 120
        d.rectangle([lx, 130, lx + 2, 198], fill=(80, 80, 90)); d.rectangle([lx - 6, 128, lx + 4, 132], fill=(255, 240, 180))
    img = overlay(img, lambda ld: [ld.polygon([(x - int(lt * speed) % 120 - 1, 132), (x - int(lt * speed) % 120 - 24, 198), (x - int(lt * speed) % 120 + 22, 198)],
                                              fill=(255, 240, 180, 40)) for x in range(-120, W + 120, 120)])
    d = ImageDraw.Draw(img)
    cx = 200 + int(math.sin(lt * 0.8) * 20)
    bounce = int(BASS * 3)
    draw_car(d, cx, 222 - bounce, (230, 30, 60), lt * 6, 2, heads=[(-6, (30, 20, 20)), (8, (80, 40, 30))])
    for i in range(16):
        age = (lt * 1.2 + i / 16) % 1.0
        x = cx - 70 - age * 260; y = 160 - bounce + math.sin(age * 8 + i) * 20 - age * 40 + 100 * age * age
        if i % 3 == 0: coin(d, x, y, 3, lt * 8 + i)
        else: bill(d, x, y, lt * 7 + i, 2)
    if lt > dur / 2 + 0.3:
        ti = fancy_text(TITLE, 3, t, "cyan" if int(lt * 2) % 2 else "pink")
        if not (int(lt * 13) % 9 == 0):
            img.paste(ti, (W // 2 - ti.width // 2, 50), ti)
    return img

def sc_outro(lt, dur, v, t):
    if lt < 12.5:
        nt = clamp(lt / 8)
        img = sky(mix((255, 120, 70), (14, 8, 44), nt), mix((255, 200, 140), (120, 40, 110), nt)); d = ImageDraw.Draw(img)
        stars(d, t, nt)
        if nt < 1: d.ellipse([W / 2 - 30, 150 + nt * 80 - 30, W / 2 + 30, 150 + nt * 80 + 30], fill=(255, 220, 140))
        if lt > 3: fireworks(d, lt, 1.3, seed=11, area=(40, 30, 440, 110))
        city(img, "far1", 200, 120, seed=11, hmin=40, hmax=110, wmin=16, wmax=34, col=(50, 26, 80), wincol=(140, 90, 160), lit=0.25)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 200, W, H], fill=(40, 30, 50)); d.rectangle([0, 200, W, 204], fill=(90, 70, 90))
        person(img, MAN, dict(P_BOY, d=(200, 40, 50), w=(255, 220, 80)), 224, 214, 3, t, seed=1)
        person(img, GIRL, P_GIRL, 256, 214, 3, t, seed=2)
        d = ImageDraw.Draw(img)
        d.rectangle([236, 178, 244, 181], fill=SKIN)
        for i in range(5):
            age = (lt * 0.4 + i / 5) % 1.0
            heart_px(d, 240 + (i - 2) * 16 + math.sin(age * 6 + i) * 4, 150 - age * 80, 1 + i % 2)
        if lt > 11:
            img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), clamp((lt - 11) / 1.5))
        return img
    tt = lt - 12.5
    img = sky((10, 6, 30), (50, 20, 70)); d = ImageDraw.Draw(img)
    stars(d, t)
    money_rain(d, tt, 30, seed=21, speed=0.5)
    ti = fancy_text(TITLE, 4, t)
    a = ease_out(clamp(tt / 1.0))
    img.paste(ti, (W // 2 - ti.width // 2, int(lerp(10, 36, a))), ti)
    if tt > 1: put_text(img, ARTIST, W // 2, 124, (255, 225, 245), (60, 10, 60))
    if tt > 2:
        person(img, GIRL, P_GIRL, W // 2 - 20, 236, 2, t); person(img, MAN, dict(P_BOY, d=(200, 40, 50), w=(255, 220, 80)), W // 2 + 20, 236, 2, t)
        d = ImageDraw.Draw(img)
        heart_px(d, W // 2, 184 + int(math.sin(t * 4) * 2), 2)
    if tt > 3 and int(t * 2) % 2 == 0:
        put_text(img, "— THE END —", W // 2, 148, (255, 220, 120), (60, 20, 10))
    end = dur - 12.5
    if tt > end - 1.5:
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), clamp((tt - (end - 1.5)) / 1.4))
    return img

SCENES = [
    (0.0, 11.0, sc_intro, 0),
    (11.0, 13.5, sc_money, 0), (13.5, 16.6, sc_wedding, 0), (16.6, 19.4, sc_heart, 0), (19.4, 23.0, sc_toast, 0),
    (23.0, 25.6, sc_money, 1), (25.6, 28.6, sc_wedding, 1), (28.6, 31.5, sc_heart, 1), (31.5, 34.8, sc_toast, 1),
    (34.8, 41.0, sc_daynight, 0), (41.0, 46.9, sc_goodbye, 0),
    (46.9, 52.9, sc_account, 0), (52.9, 55.9, sc_heaven, 0), (55.9, 58.8, sc_dream, 0), (58.8, 61.9, sc_wheat, 0),
    (61.9, 64.8, sc_car, 0), (64.8, 66.4, sc_seasons, 0), (66.4, 70.2, sc_guiyang, 0), (70.2, 73.9, sc_hotdog, 0),
    (73.9, 76.9, sc_wife, 0), (76.9, 79.9, sc_hunter, 0), (79.9, 82.8, sc_feast, 0), (82.8, 88.5, sc_sew, 0),
    (88.5, 90.0, sc_speaker, 0), (90.0, 92.0, sc_epitaph, 0), (92.0, 94.9, sc_pop, 0), (94.9, 106.9, sc_bridge, 0),
    (106.9, 109.4, sc_money, 2), (109.4, 112.4, sc_wedding, 2), (112.4, 115.3, sc_heart, 2), (115.3, 118.6, sc_toast, 2),
    (118.6, 125.1, sc_daynight, 1), (125.1, 133.0, sc_goodbye, 1), (133.0, 999, sc_outro, 0),
]

# ---------------------------------------------------------------- lyrics
def parse_lrc(path):
    out = []
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\[(\d+):(\d+(?:\.\d+)?)\](.*)", line.strip())
        if m: out.append((int(m.group(1)) * 60 + float(m.group(2)), m.group(3).strip()))
    out.sort()
    return out

def split_line(s):
    if FONT.getlength(s) <= W - 30 or " " not in s: return [s]
    spaces = [i for i, c in enumerate(s) if c == " "]
    mid = len(s) / 2
    k = min(spaces, key=lambda i: abs(i - mid))
    return [s[:k], s[k + 1:]]

def draw_lyrics(img, t, lrc):
    cur = None
    for i, (ts, tx) in enumerate(lrc):
        if ts <= t: cur = i
    if cur is None or not lrc[cur][1]: return img
    ts, tx = lrc[cur]
    te = lrc[cur + 1][0] if cur + 1 < len(lrc) else ts + 4
    lines = split_line(tx)
    a = np.asarray(img).copy()
    y0 = H - 22 * len(lines) - 6
    a[y0 - 4:, :] = (a[y0 - 4:, :] * 0.45).astype(np.uint8)
    img = Image.fromarray(a)
    dur = max(0.5, (te - ts) * 0.92)
    prog = clamp((t - ts) / dur)
    nch = sum(len(l) for l in lines)
    filled = prog * nch
    up = int((1 - ease_out(clamp((t - ts) / 0.18))) * 6)
    for li, l in enumerate(lines):
        wi = text_img(l, (255, 255, 255), (20, 10, 30), 1)
        yi = text_img(l, (255, 215, 60), (90, 20, 20), 1)
        x = W // 2 - wi.width // 2; y = y0 + li * 22 + up
        img.paste(wi, (x, y), wi)
        before = sum(len(q) for q in lines[:li])
        k = clamp(filled - before, 0, len(l))
        if k > 0:
            ki = int(k)
            pw = int(FONT.getlength(l[:ki]) + (FONT.getlength(l[:ki + 1]) - FONT.getlength(l[:ki])) * (k - ki)) + 1
            crop = yi.crop((0, 0, min(yi.width, pw + 1), yi.height))
            img.paste(crop, (x, y), crop)
    return img

# ---------------------------------------------------------------- main
def render_frame(t, lrc):
    for i, (s, e, fn, v) in enumerate(SCENES):
        if s <= t < e: break
    e = min(e, DURATION)
    lt = t - s
    img = fn(lt, e - s, v, t)
    img = draw_lyrics(img, t, lrc)
    a = np.asarray(img)
    # scene-in pixel transition
    if lt < 0.3 and s > 0:
        p = lt / 0.3
        bs = 16
        gy, gx = np.mgrid[0:H // bs + 1, 0:W // bs + 1]
        thr = ((np.sin(gx * 12.9898 + gy * 78.233) * 43758.5453) % 1.0) * 0.5 + (gx / (W / bs)) * 0.5
        m = np.repeat(np.repeat(thr > p, bs, 0), bs, 1)[:H, :W]
        a = a.copy(); a[m] = (12, 6, 24)
    return a

DURATION = 153.6

def main():
    global E, BASS, BP, BPH, DURATION
    audio, lrcp, out = sys.argv[1:4]
    lrc = parse_lrc(lrcp)
    en, ba, bpm, phase = analyze(audio)
    DURATION = min(153.6, len(en) / FPS)
    print(f"bpm={bpm:.2f} phase={phase:.3f} dur={DURATION:.2f}", flush=True)
    def set_globals(t):
        global E, BASS, BP, BPH
        i = min(len(en) - 1, int(t * FPS))
        E = float(en[i]); BASS = float(ba[i])
        BPH = ((t - phase) * bpm / 60) % 1.0
        BP = max(0.0, 1 - BPH * 3)
    if "--preview" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]
        os.makedirs(out, exist_ok=True)
        for t in ts:
            set_globals(t)
            Image.fromarray(render_frame(t, lrc)).resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(out, f"f_{t:07.2f}.png"))
        return
    n = int(DURATION * FPS)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", audio, "-vf", "scale=1920:1080:flags=neighbor", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(n):
        t = f / FPS
        set_globals(t)
        pr.stdin.write(render_frame(t, lrc).tobytes())
        if f % 240 == 0: print(f"frame {f}/{n}", flush=True)
    pr.stdin.close(); pr.wait()
    print("done", out)

if __name__ == "__main__":
    main()
