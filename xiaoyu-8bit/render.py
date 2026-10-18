"""小宇 · 8-bit 像素 MV：在 320×180 的画布上逐帧绘制，放大 4 倍到 1280×720，分块并行编码后合成音乐。

python3 render.py 小宇.mp3 --lyrics 歌词.lrc [--stills 20,75,140]
"""
import argparse, math, multiprocessing, os, random, re, shutil, subprocess
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FPS = 24
W, H = 320, 180
SC = 4
FONT = ImageFont.truetype('/usr/share/fonts/opentype/unifont/unifont.otf', 16)


def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, f): return a + (b - a) * f
def lerpc(c1, c2, f): return tuple(int(round(lerp(a, b, clamp(f)))) for a, b in zip(c1, c2))
def ease(f): f = clamp(f); return f * f * (3 - 2 * f)


# ---------------------------------------------------------------- sprites
PAL = {'K': (44, 38, 56), 'S': (246, 204, 166), 'B': (66, 116, 220), 'N': (38, 50, 90),
       'H': (126, 76, 44), 'R': (226, 70, 96), 'P': (248, 150, 170), 'W': (250, 250, 250),
       'Y': (255, 216, 84), 'E': (24, 22, 34), 'D': (120, 74, 40), 'O': (176, 112, 60),
       'G': (90, 190, 100), 'L': (210, 230, 255)}
BOY = ["..KKKK..", ".KKKKKK.", ".KSSSSK.", ".SESSES.", ".SSSSSS.", "..SSSS..",
       "..BBBB..", ".BBBBBB.", "SBBBBBBS", "S.BBBB.S", "..NNNN..", "..N..N..", "..N..N..", ".KK..KK."]
BOY_LEGW = [".NN..N..", ".N....N.", "KK....KK"]
BOY_BACK = BOY[:2] + [".KKKKKK.", ".KKKKKK.", ".SKKKKS.", "..SSSS.."] + BOY[6:]
GIRL = ["..HHHH..", ".HHHHHH.", "HHSSSSHH", "HSESSESH", "HSSSSSSH", "HHSPPSHH",
        "H.RRRR.H", ".RRRRRR.", "SRRRRRRS", "..RRRR..", ".RRRRRR.", "..S..S..", "..S..S..", ".WW..WW."]
GIRL_LEGW = [".S....S.", ".S....S.", "WW....WW"]
GIRL_BACK = GIRL[:2] + ["HHHHHHHH", "HHHHHHHH", "HHHHHHHH", "HHHHHHHH"] + GIRL[6:]
SPR = {
    'boy': BOY, 'boy_w': BOY[:11] + BOY_LEGW, 'boy_b': BOY_BACK, 'boy_bw': BOY_BACK[:11] + BOY_LEGW,
    'girl': GIRL, 'girl_w': GIRL[:11] + GIRL_LEGW, 'girl_b': GIRL_BACK, 'girl_bw': GIRL_BACK[:11] + GIRL_LEGW,
    'boy_up': BOY[:10], 'boyhead': BOY[:6], 'boyhead_b': BOY_BACK[:6], 'girlhead_b': GIRL_BACK[:6],
    'heart': [".RR.RR.", "RPRRRRR", "RRRRRRR", ".RRRRR.", "..RRR..", "...R..."],
    'boat': ["D..........D", "DDDDDDDDDDDD", ".DOOOOOOOOD.", "..DDDDDDDD.."],
    'note': ["..KK", "..KK", "..K.", "..K.", "KKK.", "KK.."],
}


@lru_cache(None)
def spr_img(name, s=1, flip=False, tint=None):
    rows = SPR[name]
    h = len(rows); w = max(len(r) for r in rows)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); px = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.':
                px[x, y] = (tint if tint else PAL[ch]) + (255,)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if s != 1: im = im.resize((w * s, h * s), Image.NEAREST)
    return im


def with_alpha(im, a):
    im = im.copy()
    im.putalpha(im.getchannel('A').point(lambda v: int(v * clamp(a))))
    return im


def put(img, name, x, y, s=1, flip=False, tint=None, alpha=1.0):
    """x = center, y = bottom"""
    im = spr_img(name, s, flip, tint)
    if alpha < 1: im = with_alpha(im, alpha)
    img.paste(im, (int(round(x - im.width / 2)), int(round(y - im.height))), im)
    return im


def put_h(img, name, x, y, height, flip=False, tint=None, alpha=1.0):
    im = spr_img(name, 1, flip, tint)
    s = height / im.height
    im = im.resize((max(1, round(im.width * s)), max(1, round(height))), Image.NEAREST)
    if alpha < 1: im = with_alpha(im, alpha)
    img.paste(im, (int(round(x - im.width / 2)), int(round(y - im.height))), im)
    return im


# ---------------------------------------------------------------- primitives
def sky(d, c1, c2, y0=0, y1=H, bands=12):
    hh = y1 - y0
    for i in range(bands):
        c = lerpc(c1, c2, i / (bands - 1))
        d.rectangle([0, y0 + hh * i // bands, W, y0 + hh * (i + 1) // bands], fill=c)


def tfill(img, shape, coords, color, a):
    m = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(m)
    getattr(md, shape)(coords, fill=int(255 * clamp(a)))
    img.paste(color, (0, 0, W, H), m)


def darken(img, a, color=(0, 0, 0)):
    if a > 0: img.paste(color, (0, 0, W, H), Image.new('L', (W, H), int(255 * clamp(a))))


_R = random.Random(7)
STARS = [(_R.randrange(W), _R.randrange(H), _R.random() * 6.28, _R.random() < 0.15) for _ in range(110)]


def stars(d, t, ymax=H, alpha=1.0, n=110):
    for x, y, p, big in STARS[:n]:
        if y >= ymax: continue
        b = (0.55 + 0.45 * math.sin(t * 3 + p)) * alpha
        if b < 0.15: continue
        d.point((x, y), fill=lerpc((50, 50, 90), (255, 255, 235), b))
        if big and b > 0.6:
            d.point([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], fill=lerpc((50, 50, 90), (190, 200, 255), b * 0.8))


def meteor(d, t, t0, x0, y0, dx, dy, life=0.9, n=14):
    f = (t - t0) / life
    if not 0 <= f <= 1: return
    hx, hy = x0 + dx * f, y0 + dy * f
    L = math.hypot(dx, dy)
    for i in range(n):
        k = i / n
        d.point((int(hx - dx / L * i * 1.5), int(hy - dy / L * i * 1.5)), fill=lerpc((255, 255, 220), (60, 60, 120), k))
    d.point([(int(hx) + 1, int(hy)), (int(hx), int(hy) + 1)], fill=(255, 255, 255))


def sparkle(d, x, y, t, col=(255, 250, 200), size=3):
    s = int(1 + (size - 1) * (0.5 + 0.5 * math.sin(t * 6)))
    d.point((x, y), fill=col)
    for i in range(1, s + 1):
        d.point([(x - i, y), (x + i, y), (x, y - i), (x, y + i)], fill=col)


def moon(d, x, y, r, col=(250, 242, 200)):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    c2 = lerpc(col, (180, 170, 140), 0.35)
    for cx, cy, cr in [(-0.35, -0.2, 0.18), (0.3, 0.25, 0.14), (0.1, -0.45, 0.09)]:
        d.ellipse([x + cx * r - cr * r, y + cy * r - cr * r, x + cx * r + cr * r, y + cy * r + cr * r], fill=c2)


def sun(d, x, y, r, t, col=(255, 220, 90), face=False):
    for k in range(8):
        a = t * 0.8 + k * math.pi / 4
        d.line([(x + math.cos(a) * (r + 3), y + math.sin(a) * (r + 3)),
                (x + math.cos(a) * (r + 8), y + math.sin(a) * (r + 8))], fill=col, width=2)
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    if face:
        d.rectangle([x - 5, y - 3, x - 4, y - 1], fill=PAL['E']); d.rectangle([x + 4, y - 3, x + 5, y - 1], fill=PAL['E'])
        d.arc([x - 5, y - 3, x + 5, y + 5], 20, 160, fill=PAL['E'])
        d.rectangle([x - 9, y + 1, x - 7, y + 2], fill=(255, 150, 120)); d.rectangle([x + 7, y + 1, x + 9, y + 2], fill=(255, 150, 120))


@lru_cache(None)
def city_layout(seed, hmin, hmax):
    r = random.Random(seed); out = []; x = 0
    while x < W * 2:
        w = r.randint(12, 28); out.append((x, w, r.randint(hmin, hmax), r.randrange(1 << 30))); x += w + r.randint(1, 4)
    return out, x


def city(d, base, seed, off, col, win=None, hmin=20, hmax=60, win_frac=0.4):
    lay, total = city_layout(seed, hmin, hmax)
    for bx, w, h, ws in lay:
        x = int((bx - off) % total)
        if x > W + 30: x -= total
        if x + w < 0 or x > W: continue
        d.rectangle([x, base - h, x + w - 1, base], fill=col)
        if win:
            rr = random.Random(ws)
            for wy in range(base - h + 3, base - 3, 5):
                for wx in range(x + 2, x + w - 2, 4):
                    if rr.random() < win_frac: d.rectangle([wx, wy, wx + 1, wy + 1], fill=win)


def hill_y(x, base, amp, freq, ph):
    return base + amp * math.sin(x * freq + ph) + amp * 0.5 * math.sin(x * freq * 2.3 + ph * 1.7)


def hills(d, base, amp, freq, ph, col):
    for x in range(W):
        d.line([(x, int(hill_y(x, base, amp, freq, ph))), (x, H)], fill=col)


CLOUD_BLOBS = [(0, 6, 6), (8, 1, 8), (19, 3, 7), (27, 7, 5)]


def cloud(d, x, y, s, col, shade=None):
    for cx, cy, r in CLOUD_BLOBS:
        d.ellipse([x + (cx - r) * s, y + (cy - r) * s, x + (cx + r) * s, y + (cy + r) * s], fill=col)
    d.rectangle([x, y + 6 * s, x + 28 * s, y + 12 * s], fill=col)
    if shade: d.rectangle([x + 2 * s, y + 11 * s, x + 26 * s, y + 12 * s], fill=shade)


def cute_cloud(d, x, y, s, t, col=(250, 252, 255), shade=(214, 226, 244), mood='happy', look=0):
    cloud(d, x, y, s, col, shade)
    fx, fy = x + 13 * s + look, y + 5 * s
    blink = (t % 3.1) < 0.12
    e = PAL['E']
    for ex in (fx - 6 * s // 2 - 2, fx + 6 * s // 2 + 1):
        if blink or mood == 'shy':
            d.rectangle([ex - 1, fy + 1, ex + 2, fy + 1], fill=e)
        else:
            d.rectangle([ex, fy - 1, ex + 1, fy + 2], fill=e)
            d.point((ex, fy - 1), fill=(255, 255, 255))
    d.rectangle([fx - 3 * s - 4, fy + 4, fx - 3 * s - 1, fy + 5], fill=(255, 170, 190))
    d.rectangle([fx + 3 * s + 2, fy + 4, fx + 3 * s + 5, fy + 5], fill=(255, 170, 190))
    if mood == 'worried':
        d.line([(fx - 2, fy + 6), (fx + 2, fy + 5)], fill=e)
        d.rectangle([fx + 6 * s, fy - 4, fx + 6 * s + 1, fy - 1], fill=(120, 190, 255))
    else:
        d.point([(fx - 2, fy + 4), (fx - 1, fy + 5), (fx, fy + 5), (fx + 1, fy + 5), (fx + 2, fy + 4)], fill=e)


def rain(d, t, x0, x1, y0, y1, n, col, speed=140, slant=0):
    span = max(1, y1 - y0); wid = max(1, x1 - x0)
    for i in range(n):
        ph = (i * 37 % 97) / 97
        y = y0 + (t * speed + ph * span) % span
        x = x0 + (i * 73) % wid + slant * (y - y0) / span
        d.line([(x, y), (x + slant * 0.05, y + 3)], fill=col)


CONF = [(255, 90, 110), (255, 210, 80), (90, 200, 255), (140, 230, 120), (220, 140, 255)]


def confetti(d, t, n=50, speed=40):
    for i in range(n):
        ph = (i * 53 % 101) / 101
        y = (t * speed * (0.7 + (i % 5) * 0.1) + ph * (H + 20)) % (H + 20) - 10
        x = (i * 67) % W + 6 * math.sin(t * 2 + i)
        w = 1 if int(t * 8 + i) % 2 else 2
        d.rectangle([x, y, x + w, y + 1], fill=CONF[i % len(CONF)])


def floating_hearts(img, t, x0, x1, ybase, n=8, speed=18, rise=90, scale=1, col=None):
    for i in range(n):
        ph = (i * 0.37) % 1
        f = (t * speed / rise + ph) % 1
        x = x0 + (i * 47) % max(1, (x1 - x0)) + 4 * math.sin(t * 2 + i)
        y = ybase - f * rise
        a = 1 - f
        put(img, 'heart', x, y, scale, tint=col, alpha=a)


def tree(d, x, base, s=1):
    d.rectangle([x - 2 * s, base - 10 * s, x + 1 * s, base], fill=(110, 70, 40))
    d.ellipse([x - 10 * s, base - 30 * s, x + 10 * s, base - 8 * s], fill=(50, 140, 70))
    d.ellipse([x - 7 * s, base - 28 * s, x + 4 * s, base - 18 * s], fill=(80, 175, 90))


# ---------------------------------------------------------------- text
def text_img(s, color, outline=(0, 0, 0)):
    w = int(FONT.getlength(s)) + 4
    t = Image.new('RGBA', (w, 20), (0, 0, 0, 0)); td = ImageDraw.Draw(t); td.fontmode = '1'
    if outline:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)]:
            td.text((2 + dx, 1 + dy), s, font=FONT, fill=outline)
    td.text((2, 1), s, font=FONT, fill=color)
    return t


def bigtext(img, s, cx, cy, scale, color, outline=(0, 0, 0), alpha=1.0):
    t = text_img(s, color, outline)
    if scale != 1: t = t.resize((t.width * scale, t.height * scale), Image.NEAREST)
    if alpha < 1: t = with_alpha(t, alpha)
    img.paste(t, (int(cx - t.width / 2), int(cy - t.height / 2)), t)


def dialog(img, d, text, lt, dur):
    grow = ease(lt / 0.18)
    x0, x1, y0, y1 = 20, 300, 145, 175
    cy = (y0 + y1) / 2; hh = (y1 - y0) / 2 * grow
    ya, yb = int(cy - hh), int(cy + hh)
    if yb - ya < 6: return
    tfill(img, 'rectangle', [x0, ya, x1, yb], (14, 18, 50), 0.88)
    d.rectangle([x0, ya, x1, yb], outline=(240, 240, 255))
    d.rectangle([x0 + 2, ya + 2, x1 - 2, yb - 2], outline=(92, 112, 210))
    if grow < 1: return
    n = len(text)
    shown = min(n, int(lt / 0.05) + 1)
    kp = clamp((lt - 0.15) / max(0.6, dur * 0.82)) * n
    x = 160 - FONT.getlength(text) / 2
    for i, ch in enumerate(text[:shown]):
        col = (255, 222, 96) if i < kp else (255, 255, 255)
        d.text((x + 1, y0 + 7), ch, font=FONT, fill=(10, 10, 30))
        d.text((x, y0 + 6), ch, font=FONT, fill=col)
        x += FONT.getlength(ch)
    if shown == n and int(lt * 3) % 2 == 0:
        d.polygon([(x1 - 12, y1 - 9), (x1 - 6, y1 - 9), (x1 - 9, y1 - 6)], fill=(255, 255, 255))


# ---------------------------------------------------------------- shared scene parts
def street(img, d, lt, T, scroll, lamps_on=1.0):
    sky(d, (22, 18, 62), (136, 84, 140), 0, 136)
    stars(d, T, 100)
    moon(d, 262, 28, 11)
    city(d, 124, 11, scroll * 0.3, (66, 54, 106), (110, 90, 150), 30, 70, 0.25)
    city(d, 136, 12, scroll * 0.6, (38, 30, 68), (255, 210, 120), 20, 52)
    d.rectangle([0, 136, W, H], fill=(76, 68, 96))
    d.line([(0, 136), (W, 136)], fill=(140, 130, 160))
    for x in range(-int(scroll) % 16, W, 16):
        d.line([(x, 137), (x - 8, H)], fill=(64, 58, 84))
    for i in range(5):
        lx = int((i * 90 - scroll) % (W + 90) - 45)
        d.rectangle([lx, 96, lx + 1, 136], fill=(50, 48, 70))
        d.rectangle([lx - 3, 94, lx + 4, 96], fill=(50, 48, 70))
        d.rectangle([lx - 2, 97, lx + 3, 98], fill=lerpc((60, 60, 80), (255, 236, 150), lamps_on))
        if lamps_on > 0:
            tfill(img, 'polygon', [(lx - 2, 99), (lx + 3, 99), (lx + 22, 136), (lx - 20, 136)], (255, 230, 150), 0.22 * lamps_on)


def walkname(base, lt, moving=True, rate=6):
    return base + ('w' if base.endswith('_b') else '_w') if moving and int(lt * rate) % 2 else base


def road(img, d, lt, top, bot, sunc, field):
    sky(d, top, bot, 0, 82)
    d.ellipse([140, 64, 180, 100], fill=sunc)
    d.rectangle([0, 82, W, H], fill=field)
    for i in range(12):
        y = 82 + int(98 * (i / 12) ** 2)
        d.line([(0, y), (W, y)], fill=lerpc(field, (0, 0, 0), 0.12))
    d.polygon([(157, 82), (163, 82), (300, H), (20, H)], fill=(96, 92, 110))
    for k in range(10):
        z = (k / 10 + lt * 0.25) % 1
        ya = 82 + 98 * z * z; yb = 82 + 98 * min(1, (z + 0.04)) ** 2
        w = 0.5 + 3 * z
        d.rectangle([160 - w, ya, 160 + w, yb], fill=(250, 240, 200))


# ---------------------------------------------------------------- scenes
def s_intro(img, d, lt, dur, T, A):
    sky(d, (8, 8, 30), (72, 42, 112), 0, 140)
    stars(d, T)
    moon(d, 262, 32, 14)
    meteor(d, lt, 2.0, 60, 10, 90, 40)
    meteor(d, lt, 5.6, 250, 60, -80, 35)
    city(d, 140, 3, T * 3, (32, 26, 64), (250, 210, 120), 30, 70)
    city(d, 152, 5, T * 8, (18, 14, 36), (255, 180, 90), 20, 45)
    d.rectangle([0, 152, W, H], fill=(14, 10, 28))
    a = ease(lt / 1.2)
    bigtext(img, META.get('ti', ''), 160, 52 + int(2 * math.sin(lt * 3)), 4, (255, 222, 96), (90, 30, 70), a)
    bigtext(img, META.get('ar', ''), 160, 92, 1, (220, 220, 255), (30, 20, 60), ease((lt - 0.8) / 1))
    if lt > 2:
        on = (int(lt * 2) % 2 == 0) if lt < 8.6 else (int(lt * 14) % 2 == 0)
        if on: bigtext(img, 'PRESS START', 160, 126, 1, (255, 255, 255), (40, 30, 80))
        put(img, 'heart', 104, 132, 1)
        put(img, 'heart', 216, 132, 1)


def s_meet0(img, d, lt, dur, T, A):
    street(img, d, lt, T, lt * 24)
    meteor(d, lt, 0.8, 300, 8, -110, 45, 1.0)
    meteor(d, lt, 3.0, 220, 20, -90, 40, 0.8)
    put(img, walkname('boy', lt), 120, 136, 2)
    if lt > 3.3:
        bigtext(img, '!', 120, 96 - int(2 * abs(math.sin(lt * 8))), 2, (255, 222, 96), (60, 20, 40))
        for i, (sx, sy) in enumerate([(100, 100), (142, 92), (90, 120), (150, 116)]):
            sparkle(d, sx, sy, lt + i)


def s_meet1(img, d, lt, dur, T, A):
    street(img, d, lt, T, 5.4 * 24)
    f = lt / 2.5
    gx = lerp(345, 192, ease(f))
    put(img, 'boy', 128, 136, 2)
    put(img, walkname('girl', lt, f < 1), gx, 136, 2, flip=True)
    if lt > 2.6:
        k = lt - 2.6
        sc = 1 + min(2, int(k * 8)) if k < 0.5 else (3 if int(lt * 4) % 2 else 2)
        put(img, 'heart', 160, 96, sc)
        floating_hearts(img, lt, 130, 190, 100, n=5, rise=60)


def eye(d, cx, cy, look, blink, heart_on, img):
    dark = (60, 34, 30)
    if blink:
        d.arc([cx - 26, cy - 10, cx + 26, cy + 10], 20, 160, fill=dark, width=3)
        return
    d.ellipse([cx - 27, cy - 18, cx + 27, cy + 18], fill=dark)
    d.ellipse([cx - 24, cy - 15, cx + 24, cy + 15], fill=(255, 255, 255))
    ix = cx + look
    d.ellipse([ix - 14, cy - 14, ix + 14, cy + 14], fill=(130, 84, 60))
    d.ellipse([ix - 10, cy - 10, ix + 10, cy + 10], fill=(96, 58, 44))
    d.ellipse([ix - 6, cy - 6, ix + 6, cy + 6], fill=(28, 18, 22))
    d.rectangle([ix - 10, cy - 10, ix - 5, cy - 5], fill=(255, 255, 255))
    d.rectangle([ix + 5, cy + 4, ix + 7, cy + 6], fill=(255, 255, 255))
    if heart_on: put(img, 'heart', ix + 1, cy + 4, 1, tint=(255, 120, 160))
    d.arc([cx - 27, cy - 18, cx + 27, cy + 18], 190, 350, fill=dark, width=4)
    for k in range(3):
        x = cx + (24 if cx > 160 else -24) + (k * 3 if cx > 160 else -k * 3)
        d.line([(x, cy - 10 - k * 2), (x + (4 if cx > 160 else -4), cy - 14 - k * 2)], fill=dark, width=2)


def s_eyes(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(246, 206, 170))
    for x in range(0, W, 2):
        y = 26 + int(6 * abs(math.sin(x * 0.11))) + (x // 2 % 3)
        d.line([(x, 0), (x, y)], fill=(126, 76, 44)); d.line([(x + 1, 0), (x + 1, y - 2)], fill=(150, 96, 60))
    blink = (2.2 < lt < 2.35) or (4.9 < lt < 5.05)
    look = int(4 * math.sin(lt * 1.3))
    for cx in (100, 220):
        eye(d, cx, 76, look, blink, lt > 2.6, img)
        d.rectangle([cx - 18, 104, cx - 4, 108], fill=(250, 160, 160))
        d.rectangle([cx + 4, 104, cx + 18, 108], fill=(250, 160, 160))
    for i, (sx, sy) in enumerate([(40, 50), (280, 46), (160, 40), (30, 110), (290, 112), (160, 118)]):
        sparkle(d, sx, sy, lt * 1.3 + i * 1.7, (255, 255, 255), 3)


def s_dream(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, 120], fill=(46, 44, 86))
    for x in range(0, W, 24): d.line([(x, 0), (x, 120)], fill=(52, 50, 94))
    d.rectangle([0, 120, W, H], fill=(84, 58, 52))
    for y in range(124, H, 8): d.line([(0, y), (W, y)], fill=(74, 50, 46))
    # window
    d.rectangle([24, 18, 94, 72], fill=(110, 80, 60))
    d.rectangle([28, 22, 90, 68], fill=(14, 16, 50))
    for x, y, p, big in STARS[:40]:
        px, py = 28 + x % 62, 22 + y % 46
        if math.sin(T * 3 + p) > 0: d.point((px, py), fill=(240, 240, 255))
    moon(d, 72, 38, 8)
    d.line([(59, 22), (59, 68)], fill=(110, 80, 60), width=2); d.line([(28, 45), (90, 45)], fill=(110, 80, 60), width=2)
    # bed
    d.rectangle([140, 96, 300, 132], fill=(130, 84, 50))
    d.rectangle([140, 86, 148, 132], fill=(110, 70, 40))
    d.rectangle([150, 98, 182, 110], fill=(250, 250, 250))
    head = spr_img('boyhead', 2).rotate(90, expand=True)
    img.paste(head, (152, 92), head)
    d.rectangle([170, 102, 298, 122], fill=(80, 120, 220))
    for x in range(176, 298, 12): d.rectangle([x, 106, x + 5, 109], fill=(110, 150, 240))
    breathe = int(math.sin(lt * 2) > 0)
    d.rectangle([180, 100 - breathe, 260, 102], fill=(80, 120, 220))
    # Zzz
    for k in range(3):
        f = (lt * 0.6 + k / 3) % 1
        bigtext(img, 'z', 168 + f * 20, 92 - f * 30, 1, (220, 220, 255), (40, 40, 90), 1 - f)
    # dream bubble
    g = ease((lt - 0.6) / 0.9)
    if lt > 0.3: d.ellipse([174, 74, 180, 80], fill=(255, 255, 255))
    if lt > 0.5: d.ellipse([182, 60, 192, 70], fill=(255, 255, 255))
    if g > 0:
        cx, cy, rx, ry = 230, 38, 66 * g, 30 * g
        d.ellipse([cx - rx - 2, cy - ry - 2, cx + rx + 2, cy + ry + 2], fill=(255, 255, 255))
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(255, 226, 240))
        if g >= 1:
            put(img, 'girl', 230, 66 + int(math.sin(lt * 3)), 2)
            for i, hx in enumerate((188, 272)):
                put(img, 'heart', hx, 44 + int(3 * math.sin(lt * 3 + i)), 1)
            sparkle(d, 200, 22, lt, (255, 200, 230)); sparkle(d, 262, 18, lt + 1, (255, 200, 230))


def s_cloud(img, d, lt, dur, T, A):
    sky(d, (80, 150, 236), (196, 228, 255), 0, 136)
    sun(d, 36, 28, 11, lt)
    for i, (cx, cy) in enumerate([(0, 22), (140, 58), (250, 14)]):
        cloud(d, int((cx + lt * 6) % 380 - 40), cy, 1, (240, 246, 255), (214, 226, 244))
    hills(d, 116, 6, 0.03, 0, (120, 196, 120)); hills(d, 128, 5, 0.05, 1, (74, 164, 86))
    x = int(80 + lt * 7); y = int(46 + 3 * math.sin(lt * 2))
    cute_cloud(d, x, y, 3, lt)
    for i in range(4):
        bx = (lt * 28 + i * 70) % 380 - 30; by = 20 + i * 9 + 3 * math.sin(lt * 2 + i)
        fl = 2 if int(lt * 6 + i) % 2 else -1
        d.line([(bx - 3, by - fl), (bx, by), (bx + 3, by - fl)], fill=(50, 60, 90))
    if lt > 2.5:
        for i in range(3):
            put(img, 'heart', x + 40 + i * 22, y - 12 - int(4 * math.sin(lt * 4 + i)), 1)


def s_drift(img, d, lt, dur, T, A):
    sky(d, (90, 156, 236), (200, 230, 255), 0, 136)
    sun(d, 290, 26, 10, lt)
    ph = -lt * 1.6
    hills(d, 112, 7, 0.025, ph * 0.5, (130, 200, 130))
    hills(d, 126, 6, 0.04, ph, (74, 164, 86))
    gx = lerp(310, 30, lt / dur)
    gy = hill_y(gx, 126, 6, 0.04, ph)
    put(img, 'girl', gx, gy + 1, 1)
    if int(lt * 2) % 2: bigtext(img, '?', gx, gy - 22, 1, (255, 255, 255), (40, 40, 90))
    for i in range(9):
        wx = W - (lt * 220 + i * 61) % (W + 60); wy = 14 + (i * 37) % 100
        d.line([(wx, wy), (wx + 10 + (i % 3) * 4, wy)], fill=(255, 255, 255))
    x = int(110 + 6 * math.sin(lt * 5)); y = int(36 + 3 * math.sin(lt * 3))
    cute_cloud(d, x, y, 3, lt, mood='worried', look=-4)


def s_rain(img, d, lt, dur, T, A):
    sky(d, (110, 132, 176), (176, 190, 214), 0, 136)
    for i, cx in enumerate([10, 230]):
        cloud(d, int((cx + lt * 4) % 360 - 30), 20 + i * 10, 1, (190, 200, 222))
    hills(d, 128, 3, 0.04, 0, (78, 150, 92))
    d.rectangle([0, 136, W, H], fill=(70, 136, 84))
    rain(d, lt, 72, 180, 66, 132, 46, (170, 210, 255), 110)
    for i, px in enumerate([90, 128, 166]):
        f = (lt * 0.8 + i * 0.33) % 1
        r = 2 + f * 12
        d.ellipse([px - r, 133 - r * 0.25, px + r, 133 + r * 0.25], outline=lerpc((200, 230, 255), (78, 150, 92), f))
    cute_cloud(d, 85, 30 + int(2 * math.sin(lt * 2)), 3, lt, col=(214, 222, 240), shade=(170, 184, 210))
    if lt > 2:
        put(img, 'heart', 132, 128 - int(lt * 6 % 30), 1, tint=(150, 200, 255))


def s_sprout(img, d, lt, dur, T, A):
    sky(d, (150, 200, 245), (226, 242, 252), 0, 110)
    rb = ease((lt - 1.5) / 2)
    if rb > 0:
        cols = [(255, 90, 90), (255, 170, 70), (255, 230, 90), (110, 210, 110), (90, 160, 255), (160, 110, 230)]
        for i, c in enumerate(cols):
            r = 120 - i * 4
            d.arc([160 - r, 120 - r, 160 + r, 120 + r], 180, 180 + 180 * rb, fill=c, width=4)
    rain(d, lt, 0, W, 0, 110, int(30 * (1 - clamp(lt / 3))), (150, 190, 240), 130)
    d.rectangle([0, 110, W, H], fill=(122, 82, 52))
    d.rectangle([0, 108, W, 111], fill=(96, 170, 80))
    for i in range(60):
        d.point(((i * 53) % W, 114 + (i * 29) % 60), fill=(100, 66, 42))
    xs = [30, 62, 94, 126, 194, 226, 258, 290]
    cols = [(255, 120, 150), (255, 220, 90), (180, 130, 255), (255, 150, 90)]
    for i, x in enumerate(xs):
        g = clamp((lt - 0.2 - (i % 4) * 0.3 - (i // 4) * 0.15) / 1.3)
        if g <= 0: continue
        h = int(22 * ease(g))
        d.line([(x, 109), (x, 109 - h)], fill=(70, 160, 70), width=2)
        if g > 0.4:
            d.rectangle([x - 4, 100, x - 1, 102], fill=(90, 190, 90)); d.rectangle([x + 2, 96, x + 5, 98], fill=(90, 190, 90))
        if g >= 1:
            c = cols[i % 4]; fy = 109 - h
            d.rectangle([x - 4, fy - 2, x + 5, fy + 3], fill=c); d.rectangle([x - 2, fy - 4, x + 3, fy + 5], fill=c)
            d.rectangle([x - 1, fy - 1, x + 2, fy + 2], fill=(255, 240, 140))
    g = clamp((lt - 2.2) / 1.5)
    if g > 0:
        h = int(34 * ease(g))
        d.line([(160, 109), (160, 109 - h)], fill=(70, 160, 70), width=3)
        if g >= 1:
            sc = 3 if int(lt * 3) % 2 else 4
            put(img, 'heart', 160, 109 - h + 6, sc)
            sparkle(d, 140, 60, lt); sparkle(d, 182, 56, lt + 1)


def s_future(img, d, lt, dur, T, A):
    road(img, d, lt, (60, 40, 120), (250, 172, 120), (255, 220, 140), (96, 150, 90))
    d.rectangle([58, 84, 60, 132], fill=(110, 70, 40))
    for k, (dy, dirn) in enumerate([(86, 1), (100, -1)]):
        x0 = 59 if dirn > 0 else 31
        d.rectangle([x0, dy, x0 + 28, dy + 10], fill=(210, 170, 110))
        tip = x0 + 28 if dirn > 0 else x0
        d.polygon([(tip, dy), (tip + 5 * dirn, dy + 5), (tip, dy + 10)], fill=(210, 170, 110))
        bigtext(img, '?', x0 + 14, dy + 5, 1, (90, 50, 30), None)
    bob = int(lt * 4) % 2
    put(img, walkname('boy_b', lt, rate=4), 150, 132, 2)
    put(img, walkname('girl_b', lt, rate=4), 172, 132 - bob, 2)
    for i in range(3):
        f = (lt * 0.4 + i / 3) % 1
        bigtext(img, '?', 120 + i * 40, 70 - f * 40, 1, (255, 255, 255), (80, 50, 110), 1 - f)


def s_happy(img, d, lt, dur, T, A):
    sky(d, (110, 190, 250), (206, 236, 255), 0, 120)
    sun(d, 272, 32, 12, lt, face=True)
    cloud(d, int((20 + lt * 8) % 360 - 30), 20, 1, (255, 255, 255))
    cloud(d, int((170 + lt * 8) % 360 - 30), 40, 1, (255, 255, 255))
    d.rectangle([0, 120, W, H], fill=(104, 196, 96))
    tree(d, 30, 124, 1); tree(d, 292, 126, 1)
    for i in range(14):
        x = (i * 41) % W; y = 126 + (i * 13) % 14
        d.rectangle([x, y, x + 1, y + 1], fill=CONF[i % 5])
    bounce = 0.6 + A * 0.8
    put(img, 'boy', 130, 136 - abs(math.sin(lt * 5)) * 10 * bounce, 2)
    put(img, 'girl', 190, 136 - abs(math.sin(lt * 5 + 1.2)) * 10 * bounce, 2)
    confetti(d, lt, 50)
    for i in range(4):
        f = (lt * 0.5 + i / 4) % 1
        put(img, 'note', 160 + 70 * math.sin(i * 2.1) + 5 * math.sin(lt * 3 + i), 100 - f * 80, 1, alpha=1 - f)


def s_book(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(92, 56, 36))
    for y in range(0, H, 18): d.line([(0, y), (W, y)], fill=(76, 46, 30))
    tfill(img, 'ellipse', [40, -20, 280, 160], (255, 220, 150), 0.18)
    d.rectangle([76, 26, 244, 130], fill=(150, 40, 50))
    d.rectangle([82, 30, 158, 124], fill=(250, 240, 214)); d.rectangle([162, 30, 238, 124], fill=(250, 240, 214))
    d.rectangle([158, 28, 162, 126], fill=(200, 186, 160))
    r = random.Random(4)
    end = lt > 3.2
    for y in range(38, 118, 7):
        d.line([(88, y), (88 + r.randint(40, 64), y)], fill=(170, 160, 140))
        if not end: d.line([(168, y), (168 + r.randint(40, 64), y)], fill=(170, 160, 140))
    if not end:
        f = (lt % 0.8) / 0.8
        w = 76 * math.cos(math.pi * f)
        if w >= 0: d.rectangle([162, 30, 162 + w, 124], fill=(236, 226, 200), outline=(200, 186, 160))
        else: d.rectangle([158 + w, 30, 158, 124], fill=(236, 226, 200), outline=(200, 186, 160))
    else:
        bigtext(img, 'END', 196, 68, 2, (200, 50, 60), None)
        q = 2 if int(lt * 3) % 2 else 3
        bigtext(img, '?', 200, 100, q, (60, 60, 160), None)
    # candle
    d.rectangle([272, 92, 282, 128], fill=(246, 240, 226))
    fl = int(2 * math.sin(lt * 17) + math.sin(lt * 7))
    d.ellipse([273 + fl * 0.5, 80, 281 + fl * 0.5, 91], fill=(255, 190, 70))
    d.ellipse([275 + fl * 0.5, 84, 279 + fl * 0.5, 91], fill=(255, 250, 200))


def s_moon(img, d, lt, dur, T, A):
    sky(d, (10, 12, 42), (46, 44, 96), 0, 136)
    stars(d, T)
    for k, a in enumerate([0.08, 0.12, 0.18]):
        r = 52 - k * 7
        tfill(img, 'ellipse', [230 - r, 56 - r, 230 + r, 56 + r], (255, 240, 200), a)
    moon(d, 230, 56, 32)
    put(img, 'girl', 230, 80, 3, tint=(214, 200, 160), alpha=ease((lt - 1) / 2))
    put(img, 'boy_b', 90, 128, 2)
    d.polygon([(0, 122), (200, 116), (230, 136), (0, 136)], fill=(52, 38, 60))
    for x in range(0, 210, 10): d.line([(x, 121 - x * 0.03), (x + 4, 136)], fill=(40, 28, 48))
    d.rectangle([150, 98, 162, 118], fill=(70, 50, 70))
    d.rectangle([0, 136, W, H], fill=(28, 20, 36))
    for i in range(3):
        f = (lt * 0.3 + i / 3) % 1
        put(img, 'heart', lerp(96, 210, f), lerp(100, 60, f) - 10 * math.sin(f * math.pi), 1, alpha=1 - f * 0.8)


def s_game(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(36, 30, 48))
    d.rectangle([0, 128, W, H], fill=(60, 44, 40))
    d.line([(130, 14), (112, 0)], fill=(150, 150, 160), width=2); d.line([(190, 14), (208, 0)], fill=(150, 150, 160), width=2)
    d.rectangle([54, 14, 266, 134], fill=(160, 150, 140))
    d.rectangle([58, 18, 262, 130], fill=(120, 110, 104))
    sx0, sy0, sx1, sy1 = 66, 24, 230, 122
    if lt < 3.6:
        d.rectangle([sx0, sy0, sx1, sy1], fill=(10, 16, 30))
        for i in range(3): put(img, 'heart', 78 + i * 10, 38, 1)
        bigtext(img, 'GAME', 148, 64, 2, (120, 255, 140), (0, 60, 20))
        if int(lt * 2) % 2 == 0: bigtext(img, 'PRESS START', 148, 100, 1, (255, 255, 255), None)
        if lt > 1.8:
            g = ease((lt - 1.8) / 0.4)
            d.line([(100, 46), (100 + 96 * g, 46 + 36 * g)], fill=(255, 60, 70), width=5)
            d.line([(196, 46), (196 - 96 * g, 46 + 36 * g)], fill=(255, 60, 70), width=5)
    else:
        d.rectangle([sx0, sy0, sx1, sy1], fill=(255, 196, 214))
        sc = 4 if A > 0.55 else 3
        put(img, 'heart', 148, 84, sc + (1 if int(lt * 4) % 2 else 0))
        bigtext(img, 'NOT A GAME', 148, 104, 1, (200, 40, 80), (255, 255, 255))
        bigtext(img, 'REAL', 148, 40, 1, (200, 40, 80), (255, 255, 255))
    for y in range(sy0, sy1, 2):
        tfill(img, 'rectangle', [sx0, y, sx1, y], (0, 0, 0), 0.25)
    for i, c in enumerate([(200, 60, 60), (90, 90, 100)]):
        d.ellipse([240, 40 + i * 22, 254, 54 + i * 22], fill=c)
    put(img, 'boy_b', 40, 140, 2)


def s_trueheart(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(255, 196, 214))
    for k in range(12):
        a = math.radians(k * 30 + lt * 20)
        if k % 2: continue
        tfill(img, 'polygon', [(160, 80), (160 + 400 * math.cos(a - 0.26), 80 + 400 * math.sin(a - 0.26)),
                               (160 + 400 * math.cos(a + 0.26), 80 + 400 * math.sin(a + 0.26))], (255, 240, 246), 0.6)
    d.rectangle([0, 136, W, H], fill=(230, 150, 180))
    put(img, 'boy', 104, 136, 2)
    put(img, 'girl', 222, 136, 2, flip=True)
    h = 30 + 10 * A + 3 * math.sin(lt * 6)
    put_h(img, 'heart', 160, 70 + h / 2, h)
    for i in range(6):
        a = lt * 1.5 + i * math.pi / 3
        sparkle(d, int(160 + 42 * math.cos(a)), int(68 + 34 * math.sin(a)), lt + i, (255, 255, 255))
    d.rectangle([114, 112, 128, 114], fill=PAL['S'])


def s_secret(img, d, lt, dur, T, A):
    sky(d, (90, 70, 140), (170, 130, 190), 0, 136)
    for i in range(30):
        d.point(((i * 47) % W, (i * 31) % 130), fill=(200, 170, 220))
    d.rectangle([0, 136, W, H], fill=(70, 56, 100))
    put(img, 'boy', 120, 136, 2)
    put(img, 'girl', 200, 136, 2, flip=True)
    if lt < 2.6:
        d.rounded_rectangle([60, 46, 140, 80], 6, fill=(255, 255, 255), outline=(40, 30, 60))
        d.polygon([(108, 80), (116, 80), (114, 92)], fill=(255, 255, 255))
        n = int(lt * 4) % 7
        for k in range(n): d.rectangle([74 + k * 9, 62, 77 + k * 9, 65], fill=(40, 30, 60))
    else:
        d.rectangle([114, 117, 125, 121], fill=(200, 200, 210))
        d.line([(115, 117), (124, 121)], fill=(120, 120, 130)); d.line([(115, 121), (124, 117)], fill=(120, 120, 130))
        put(img, 'heart', 96 - int((lt - 2.6) * 10), 100, 1, tint=(160, 140, 180))
    if lt > 1:
        d.rounded_rectangle([196, 62, 220, 86], 5, fill=(255, 255, 255), outline=(40, 30, 60))
        bigtext(img, '?', 208, 74, 1, (80, 60, 160), None)


def s_quiz(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(20, 20, 60))
    for x in range(0, W, 20):
        for y in range(0, 136, 20):
            if (x + y) // 20 % 2: d.rectangle([x, y, x + 19, y + 19], fill=(26, 26, 70))
    tfill(img, 'polygon', [(150, 0), (170, 0), (200, 136), (120, 136)], (255, 255, 200), 0.18)
    d.rectangle([0, 136, W, H], fill=(40, 36, 80))
    d.rectangle([60, 8, 260, 34], fill=(250, 250, 255), outline=(255, 210, 80), width=2)
    bigtext(img, 'Q. ???', 160, 21, 1, (40, 40, 90), None)
    sel = int(lt / 0.5) % 2
    for i, (x0, c) in enumerate([(30, (230, 70, 90)), (190, (70, 130, 230))]):
        d.rectangle([x0, 48, x0 + 100, 90], fill=c, outline=(255, 230, 90) if sel == i else (255, 255, 255), width=3 if sel == i else 1)
        bigtext(img, 'AB'[i], x0 + 50, 69, 2, (255, 255, 255), None)
    ax = 22 if sel == 0 else 182
    d.polygon([(ax, 62), (ax + 6, 69), (ax, 76)], fill=(255, 255, 255))
    put(img, 'girl', 160, 136, 2)
    if int(lt * 3) % 2: d.rectangle([174, 108, 175, 112], fill=(120, 190, 255))
    for i in range(3):
        f = (lt * 0.5 + i / 3) % 1
        bigtext(img, '?', 160 + (i - 1) * 26, 104 - f * 20, 1, (255, 230, 90), (30, 30, 70), 1 - f)


def s_shadow(img, d, lt, dur, T, A):
    sky(d, (110, 86, 104), (70, 52, 80), 0, 136)
    d.rectangle([0, 136, W, H], fill=(52, 38, 48))
    g = ease(lt / 4.5)
    h = lerp(36, 112, g)
    sim = put_h(img, 'boy', 215, 136, h, tint=(34, 20, 44), alpha=0.85)
    if lt > 2.4 and (lt % 1.6) > 0.15:
        left = 215 - sim.width / 2; top = 136 - sim.height; sx = sim.width / 8; sy = sim.height / 14
        for ex in (2, 5):
            d.rectangle([left + ex * sx, top + 3 * sy, left + (ex + 1) * sx - 1, top + 4 * sy - 1], fill=(255, 70, 90))
    tfill(img, 'ellipse', [10, 50, 90, 140], (255, 230, 160), 0.2)
    d.rectangle([48, 70, 50, 136], fill=(60, 50, 50))
    d.polygon([(38, 70), (60, 70), (54, 56), (44, 56)], fill=(255, 220, 140))
    d.rectangle([42, 134, 56, 136], fill=(60, 50, 50))
    put(img, 'boy', 110, 136, 2)


def s_night(img, d, lt, dur, T, A):
    k = ease(lt / 3.6)
    street(img, d, lt, T, 0, lamps_on=1 - k)
    darken(img, k * 0.9, (4, 4, 16))
    stars(d, T, 110, k)
    if k < 0.8:
        put(img, 'boy', 160, 136, 2, tint=lerpc(PAL['B'], (10, 10, 20), k) if k > 0.3 else None)
    else:
        put(img, 'boy', 160, 136, 2, tint=(8, 8, 20))
    if k > 0.6 and not (3.8 < lt < 3.95 or 5.2 < lt < 5.35):
        for ex in (2, 5):
            d.rectangle([152 + ex * 2, 114, 153 + ex * 2, 115], fill=(255, 255, 240))


def s_boat(img, d, lt, dur, T, A):
    sky(d, (74, 44, 110), (252, 146, 96), 0, 92)
    d.ellipse([186, 72, 222, 108], fill=(255, 210, 120))
    sky(d, (90, 60, 120), (40, 34, 80), 92, H, 8)
    for i in range(14):
        y = 94 + i * 3 + i * i // 6
        w = 26 - i + 8 * math.sin(lt * 3 + i)
        if y < H: d.line([(204 - w, y), (204 + w, y)], fill=(255, 200, 130))
    for i in range(16):
        x = (i * 43 + lt * 10) % W; y = 100 + (i * 19) % 70
        d.line([(x, y), (x + 6, y)], fill=(120, 90, 150))
    bx = 80 + lt * 7; by = 116 + 2 * math.sin(lt * 2)
    put(img, 'boy_up', bx + 2, by - 4, 2)
    put(img, 'boat', bx, by + 4, 2)
    d.line([(bx + 12, by - 10), (bx + 22, by + 10)], fill=(140, 90, 50), width=2)
    for j in range(3):
        f = (lt * 0.7 + j / 3) % 1
        r = 14 + f * 20
        d.arc([bx - r, by + 2, bx + r, by + 10], 0, 180, fill=lerpc((200, 170, 220), (60, 46, 96), f))


HEART_PTS = [(16 * math.sin(t) ** 3, -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)))
             for t in np.linspace(0, 2 * math.pi, 80)]


def heart_poly(cx, cy, s):
    return [(cx + x * s, cy + y * s) for x, y in HEART_PTS]


def s_heartlake(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(96, 176, 92))
    for i in range(160):
        d.point(((i * 61) % W, (i * 37) % H), fill=(70, 150, 74))
    d.polygon(heart_poly(160, 72, 5.4), fill=(226, 206, 150))
    d.polygon(heart_poly(160, 72, 5.0), fill=(70, 130, 220))
    d.polygon(heart_poly(160, 74, 3.6), fill=(80, 145, 230))
    for i in range(20):
        x = 100 + (i * 41) % 120; y = 30 + (i * 23) % 80
        if int(lt * 2 + i) % 3 == 0: d.line([(x, y), (x + 3, y)], fill=(170, 210, 255))
    for x, y in [(40, 30), (280, 26), (30, 110), (290, 104), (70, 130), (250, 132), (160, 136)]:
        d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(40, 120, 60)); d.ellipse([x - 7, y - 8, x + 3, y + 1], fill=(70, 160, 80))
    def pos(t):
        a = t * 0.9
        return (160 + 2.9 * 16 * math.sin(a) ** 3,
                72 - 2.9 * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)))
    for j in range(1, 10):
        x, y = pos(lt - j * 0.12)
        d.point((x, y), fill=(220, 236, 255))
    x, y = pos(lt)
    d.ellipse([x - 5, y - 3, x + 5, y + 3], fill=(140, 90, 50))
    d.rectangle([x - 1, y - 2, x + 1, y], fill=PAL['K'])


def s_lighthouse(img, d, lt, dur, T, A):
    sky(d, (6, 8, 32), (24, 34, 76), 0, 100)
    stars(d, T, 96)
    d.rectangle([0, 100, W, H], fill=(14, 28, 62))
    for i in range(18):
        x = (i * 53 - lt * 12 * (1 + i % 3)) % (W + 20) - 10; y = 104 + (i * 13) % 40
        d.line([(x, y), (x + 8, y)], fill=(40, 70, 120))
    d.polygon([(220, 136), (232, 100), (276, 96), (300, 136)], fill=(60, 60, 72))
    a = math.pi + 0.55 * math.sin(lt * 1.1)
    tfill(img, 'polygon', [(252, 34), (252 + 330 * math.cos(a - 0.09), 34 + 330 * math.sin(a - 0.09)),
                           (252 + 330 * math.cos(a + 0.09), 34 + 330 * math.sin(a + 0.09))], (255, 236, 150), 0.38)
    for i in range(6):
        y0 = 100 - i * 10
        c = (230, 70, 70) if i % 2 else (240, 240, 240)
        w0 = 12 - i * 0.6
        d.rectangle([252 - w0, y0 - 10, 252 + w0, y0], fill=c)
    d.rectangle([244, 28, 260, 40], fill=(255, 230, 120))
    d.polygon([(242, 28), (262, 28), (252, 18)], fill=(200, 60, 60))
    bx = 40 + lt * 9; by = 120 + 2 * math.sin(lt * 2.5)
    put(img, 'boy_up', bx + 2, by - 4, 2)
    put(img, 'boat', bx, by + 4, 2)


def s_harbor(img, d, lt, dur, T, A):
    sky(d, (120, 160, 232), (255, 194, 144), 0, 96)
    sy = 96 - 18 * ease(lt / dur)
    d.ellipse([60, sy - 14, 88, sy + 14], fill=(255, 226, 140))
    sky(d, (90, 150, 210), (50, 100, 170), 96, H, 8)
    for i in range(12):
        x = (i * 47 + lt * 8) % W; y = 100 + (i * 17) % 60
        d.line([(x, y), (x + 6, y)], fill=(150, 200, 240))
    for x in range(204, W, 22): d.rectangle([x, 112, x + 3, 140], fill=(90, 56, 34))
    d.rectangle([196, 106, W, 112], fill=(150, 100, 60))
    for x in range(196, W, 8): d.line([(x, 106), (x, 112)], fill=(120, 80, 48))
    put(img, 'girl', 232, 106 - abs(math.sin(lt * 4)) * 4, 2, flip=True)
    bx = lerp(30, 176, ease(lt / 4)); by = 118 + 2 * math.sin(lt * 2)
    put(img, 'boy_up', bx + 2, by - 4, 2)
    put(img, 'boat', bx, by + 4, 2)
    for i in range(3):
        gx = (lt * 20 + i * 90) % 360 - 20; gy = 30 + i * 10
        fl = 2 if int(lt * 5 + i) % 2 else -1
        d.line([(gx - 3, gy - fl), (gx, gy), (gx + 3, gy - fl)], fill=(255, 255, 255))
    if lt > 4.1:
        put(img, 'heart', 206, 70, 2 if int(lt * 4) % 2 else 3)


METEORS = [(i * 1.3 + 0.4, 60 + (i * 97) % 260, 4 + (i * 23) % 40) for i in range(40)]


def s_interlude(img, d, lt, dur, T, A):
    sky(d, (6, 6, 28), (40, 30, 90), 0, 122)
    stars(d, T)
    moon(d, 52, 34, 13)
    for t0, x0, y0 in METEORS:
        meteor(d, lt, t0, x0, y0, -90, 40, 0.8)
    if lt > 10:
        for t0, x0, y0 in METEORS[::2]:
            meteor(d, lt, t0 + 0.6, x0 + 30, y0 + 10, -70, 36, 0.7)
    gx = lerp(340, 182, ease((lt - 10) / 3)) if lt > 10 else None
    put(img, 'boy_b', 140, 128, 2)
    if gx is not None:
        put(img, walkname('girl_b', lt, gx > 183), gx, 128, 2)
        if lt > 13.5: put(img, 'heart', 161, 92 - int(2 * math.sin(lt * 3)), 1)
    d.rectangle([0, 120, W, 136], fill=(44, 32, 56))
    for x in range(0, W, 8): d.line([(x, 120), (x, 136)], fill=(36, 26, 46))
    d.rectangle([0, 136, W, H], fill=(24, 18, 34))
    for i in range(10):
        f = (lt * 0.35 + i / 10) % 1
        put(img, 'note', 140 + 30 * math.sin(i * 1.7 + f * 4), 104 - f * 90, 1, tint=(255, 240, 200), alpha=1 - f)
    spec = SPEC[min(len(SPEC) - 1, int(T * FPS))]
    nb = len(spec); bw = W // nb
    for i, v in enumerate(spec):
        hgt = int(v * 9) * 4
        c = lerpc((120, 90, 255), (255, 120, 180), i / nb)
        for y in range(0, hgt, 4):
            d.rectangle([i * bw + 2, 176 - y, i * bw + bw - 2, 178 - y], fill=lerpc(c, (255, 240, 160), y / 40))


def s_together(img, d, lt, dur, T, A):
    road(img, d, lt, (80, 50, 120), (255, 140, 110), (255, 190, 110), (150, 110, 90))
    put(img, walkname('boy_b', lt, rate=4), 152, 132, 2)
    put(img, walkname('girl_b', lt, rate=4), 168, 132, 2)
    d.rectangle([158, 120, 162, 121], fill=PAL['S'])
    put(img, 'heart', 160, 92 - int(3 * math.sin(lt * 3)), 2)
    floating_hearts(img, lt, 60, 260, 120, n=6, rise=80)


BURSTS = [(0.2 + i * 0.5, 40 + (i * 89) % 240, 22 + (i * 29) % 50, CONF[i % 5]) for i in range(14)]


def s_fireworks(img, d, lt, dur, T, A):
    sky(d, (6, 6, 26), (40, 24, 70), 0, 136)
    stars(d, T, 100, 0.6)
    for t0, x, y, c in BURSTS:
        f = (lt - t0)
        if -0.45 < f < 0:
            ry = y + (-f) * 160
            d.rectangle([x, ry, x, ry + 3], fill=(255, 240, 200))
        elif 0 <= f < 1.5:
            r = 34 * ease(f / 0.9)
            for j in range(24):
                a = j * math.pi / 12
                px = x + math.cos(a) * r; py = y + math.sin(a) * r + 14 * f * f
                col = lerpc(c, (30, 20, 50), (f - 0.6) / 0.9)
                d.point((px, py), fill=col)
                d.point((px - math.cos(a) * 2, py - math.sin(a) * 2), fill=lerpc(col, (30, 20, 50), 0.5))
            if f < 0.15: d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 230))
    city(d, 136, 21, 0, (20, 16, 36), (255, 200, 110), 14, 40)
    d.rectangle([0, 136, W, H], fill=(14, 10, 24))
    d.ellipse([90, 118, 230, 160], fill=(14, 10, 24))
    put(img, 'boy_b', 150, 132, 2)
    put(img, 'girl_b', 170, 132, 2)
    d.rectangle([156, 120, 164, 121], fill=PAL['S'])


def s_theater(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(16, 10, 22))
    tfill(img, 'polygon', [(160, 180), (50, 12), (270, 12)], (255, 250, 220), 0.06)
    d.rectangle([50, 12, 270, 102], fill=(255, 210, 222))
    put(img, 'boy', 136, 92, 2); put(img, 'girl', 184, 92, 2, flip=True)
    hh = 10 + 16 * ease(lt / 3)
    put_h(img, 'heart', 160, 64 + hh / 2, hh)
    if lt > 3:
        bigtext(img, 'FIN' + ('?' if int(lt * 2) % 2 else ' '), 160, 28, 2, (200, 40, 80), (255, 255, 255))
    darken(img, 0.06 * (1 + math.sin(lt * 23)))
    for side in (0, 1):
        for i in range(5):
            x = (i * 10) if side == 0 else W - 50 + i * 10
            d.rectangle([x, 0, x + 9, 120], fill=(150, 20, 40) if i % 2 else (180, 30, 50))
    d.rectangle([0, 0, W, 8], fill=(130, 16, 36))
    put(img, 'boyhead_b', 150, 124, 2); put(img, 'girlhead_b', 172, 124, 2)
    for row, y in enumerate((118, 134)):
        for x in range(-10 + row * 12, W, 24):
            d.rounded_rectangle([x, y, x + 20, y + 22], 4, fill=(50, 20, 34) if row == 0 else (40, 14, 26))


def photo(kind, lt):
    p = Image.new('RGB', (40, 40)); pd = ImageDraw.Draw(p)
    if kind == 0:
        pd.rectangle([0, 0, 40, 40], fill=(140, 200, 250)); pd.rectangle([0, 30, 40, 40], fill=(100, 190, 100))
        g = spr_img('girl', 2); p.paste(g, (12, 4), g)
    elif kind == 1:
        pd.rectangle([0, 0, 40, 40], fill=(30, 30, 80)); moon(pd, 30, 9, 5)
        b = spr_img('boy_b', 2); p.paste(b, (2, 12), b)
        g = spr_img('girl_b', 2); p.paste(g, (20, 12), g)
    elif kind == 2:
        pd.rectangle([0, 0, 40, 40], fill=(255, 200, 220))
        h = spr_img('heart', 4); p.paste(h, (6, 8), h)
    else:
        pd.rectangle([0, 0, 40, 40], fill=(255, 170, 120)); pd.rectangle([0, 28, 40, 40], fill=(60, 100, 170))
        b = spr_img('boy', 2); p.paste(b, (3, 10), b)
        g = spr_img('girl', 2); p.paste(g, (21, 10), g)
    fr = Image.new('RGBA', (46, 54), (250, 250, 250, 255))
    fr.paste(p, (3, 3))
    return fr


def s_polaroid(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(232, 214, 186))
    for x in range(0, W, 12): d.line([(x, 0), (x, H)], fill=(224, 204, 176))
    sy = lambda x: 26 + 10 * math.sin(math.pi * x / W)
    for x in range(0, W): d.point((x, sy(x)), fill=(120, 90, 70))
    for i, x in enumerate(range(10, W, 20)):
        on = int(lt * 3 + i) % 2
        d.rectangle([x, sy(x) + 1, x + 1, sy(x) + 2], fill=CONF[i % 5] if on else (180, 160, 140))
    for i, (cx, ang) in enumerate([(52, -6), (124, 4), (196, -3), (268, 6)]):
        f = clamp((lt - i * 1.0) / 0.6)
        if f <= 0: continue
        ty = sy(cx) + 4
        y = lerp(-70, ty, ease(f)) + (3 * math.sin(f * math.pi * 2) * (1 - f) if f < 1 else 0)
        fr = photo(i, lt).rotate(ang + 2 * math.sin(lt * 2 + i), resample=Image.NEAREST, expand=True)
        img.paste(fr, (int(cx - fr.width / 2), int(y)), fr)
        d.rectangle([cx - 1, y, cx + 1, y + 2], fill=(220, 50, 60))
    if lt > 4:
        put(img, 'heart', 160, 136, 2)


def s_timelapse(img, d, lt, dur, T, A):
    u = (lt / 2.4 + 0.25) % 1
    day = clamp(math.sin(2 * math.pi * u) * 2 + 0.5)
    sky(d, lerpc((10, 12, 44), (100, 170, 240), day), lerpc((50, 40, 100), (210, 236, 255), day), 0, 136)
    stars(d, T * 4, 110, 1 - day)
    sxp = 160 - 140 * math.cos(2 * math.pi * u); syp = 130 - 110 * math.sin(2 * math.pi * u)
    if syp < 130: d.ellipse([sxp - 10, syp - 10, sxp + 10, syp + 10], fill=(255, 220, 90))
    mx = 160 + 140 * math.cos(2 * math.pi * u); my = 130 + 110 * math.sin(2 * math.pi * u)
    if my < 130: moon(d, mx, my, 9)
    for i in range(3):
        cloud(d, int((i * 130 + lt * 60) % 400 - 40), 20 + i * 12, 1, lerpc((90, 90, 130), (255, 255, 255), day))
    hills(d, 120, 4, 0.03, 0, lerpc((30, 60, 40), (100, 190, 100), day))
    d.rectangle([128, 96, 182, 132], fill=lerpc((120, 100, 90), (240, 220, 190), day))
    d.polygon([(122, 98), (155, 72), (188, 98)], fill=lerpc((90, 30, 40), (210, 70, 70), day))
    d.rectangle([150, 114, 160, 132], fill=(120, 80, 50))
    win = (255, 220, 120) if day < 0.5 else (150, 200, 240)
    d.rectangle([134, 104, 144, 112], fill=win); d.rectangle([166, 104, 176, 112], fill=win)
    d.rectangle([0, 132, W, H], fill=lerpc((30, 60, 40), (100, 190, 100), day))
    tint = None if day > 0.4 else (20, 20, 40)
    put(img, 'boy', 210, 136, 2, tint=tint); put(img, 'girl', 230, 136, 2, tint=tint)


def s_calendar(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(206, 186, 166))
    for x in range(0, W, 16):
        for y in range(0, H, 16): d.point((x + 8, y + 8), fill=(190, 166, 146))
    d.rectangle([0, 136, W, H], fill=(120, 90, 70))
    step = 0.42
    n = int(lt / step) + 1; f = (lt % step) / step
    d.rectangle([108, 14, 212, 36], fill=(220, 60, 70))
    for x in (124, 196): d.rectangle([x, 10, x + 3, 18], fill=(80, 80, 90))
    bigtext(img, 'DAY', 160, 26, 1, (255, 255, 255), None)
    d.rectangle([108, 36, 212, 132], fill=(252, 252, 248))
    bigtext(img, str(n), 160, 68, 3, (50, 50, 70), None)
    put(img, 'heart', 160, 124, 2)
    if n > 1 and f < 0.6:
        g = f / 0.6
        dy = g * 140; dx = g * 70; sk = g * 30
        pts = [(108 + dx, 36 + dy), (212 + dx, 36 + dy + sk * 0.3), (212 + dx - sk, 132 + dy), (108 + dx - sk, 132 + dy - sk * 0.3)]
        d.polygon(pts, fill=(236, 236, 230), outline=(200, 200, 200))
        bigtext(img, str(n - 1), 160 + dx - sk / 2, 68 + dy, 3, (120, 120, 140), None)
    put(img, 'boy', 62, 136 - (abs(math.sin(lt * math.pi / step)) * 6), 2)
    if int(lt * 2) % 2: put(img, 'heart', 62, 96, 1)


def hourglass(lt):
    im = Image.new('RGBA', (60, 92), (0, 0, 0, 0)); hd = ImageDraw.Draw(im)
    hd.rectangle([0, 0, 59, 6], fill=(150, 96, 56)); hd.rectangle([0, 85, 59, 91], fill=(150, 96, 56))
    hd.rectangle([4, 6, 6, 85], fill=(120, 76, 44)); hd.rectangle([53, 6, 55, 85], fill=(120, 76, 44))
    glass = (210, 230, 255, 140)
    hd.polygon([(10, 8), (49, 8), (31, 45), (28, 45)], fill=glass)
    hd.polygon([(28, 46), (31, 46), (49, 83), (10, 83)], fill=glass)
    s = clamp(lt / 2.6)
    sand = (255, 140, 170, 255)
    top = 8 + 36 * s
    if s < 1:
        k = (top - 8) / 37
        hd.polygon([(10 + 19 * k, top), (49 - 18 * k, top), (31, 45), (28, 45)], fill=sand)
        hd.line([(29, 45), (29, 83)], fill=sand, width=2)
    hgt = 30 * s
    hd.polygon([(29 - hgt * 0.9, 83), (30 + hgt * 0.9, 83), (30, 83 - hgt)], fill=sand)
    return im


def s_hourglass(img, d, lt, dur, T, A):
    sky(d, (40, 26, 80), (90, 60, 130), 0, H)
    stars(d, T, H, 0.7)
    cyc = 2.9
    k = lt % cyc; flip = int(lt / cyc) % 2
    if k < 2.5: hg = hourglass(k).rotate(180 * flip, resample=Image.NEAREST)
    else:
        a = 180 * flip + 180 * ease((k - 2.5) / 0.4)
        hg = hourglass(2.6).rotate(a, resample=Image.NEAREST, expand=True)
    img.paste(hg, (160 - hg.width // 2, 70 - hg.height // 2), hg)
    floating_hearts(img, lt, 40, 280, 150, n=10, rise=150, speed=24)
    for i, (x, y) in enumerate([(60, 40), (260, 50), (80, 110), (240, 116)]):
        sparkle(d, x, y, lt + i)


def s_beach(img, d, lt, dur, T, A):
    sky(d, (140, 90, 160), (255, 160, 120), 0, 96)
    d.ellipse([136, 70, 184, 118], fill=(255, 210, 120))
    sky(d, (230, 140, 120), (90, 80, 140), 96, 120, 6)
    for i in range(10):
        y = 98 + i * 2; w = 20 - i * 1.5 + 4 * math.sin(lt * 3 + i)
        d.line([(160 - w, y), (160 + w, y)], fill=(255, 220, 150))
    d.rectangle([0, 120, W, H], fill=(236, 200, 150))
    wv = 120 + int(2 * math.sin(lt * 1.5))
    for x in range(0, W, 2): d.point((x, wv + int(math.sin(x * 0.2 + lt * 3))), fill=(255, 255, 255))
    put(img, 'boy', 148, 138, 2)
    put(img, 'girl', 172, 138 - int(abs(math.sin(lt * 2)) * 2), 2)
    d.rectangle([156, 124, 164, 126], fill=PAL['S'])
    floating_hearts(img, lt, 100, 220, 110, n=4 + int(lt), rise=100, speed=20)
    for i in range(3):
        gx = (lt * 18 + i * 110) % 360 - 20; gy = 26 + i * 12
        fl = 2 if int(lt * 5 + i) % 2 else -1
        d.line([(gx - 3, gy - fl), (gx, gy), (gx + 3, gy - fl)], fill=(70, 50, 90))


def s_believe(img, d, lt, dur, T, A):
    sky(d, (80, 84, 100), (140, 144, 156), 0, 136)
    city(d, 136, 31, 0, (100, 104, 118), None, 30, 70)
    d.rectangle([0, 136, W, H], fill=(90, 92, 104))
    for x in (60, 200, 270):
        d.ellipse([x - 16, 140, x + 16, 146], fill=(120, 126, 144))
    gx = 200 + lt * 9
    put(img, walkname('girl_b', lt, rate=3), gx, 136, 2, tint=None)
    put(img, 'boy', 100, 136, 2)
    hy = 92
    if lt < 2.5:
        put(img, 'heart', 100, hy, 2)
    else:
        put(img, 'heart', 100, hy, 2, tint=(150, 150, 166))
        d.line([(100, hy - 12), (98, hy - 8), (102, hy - 5), (99, hy - 1)], fill=(80, 80, 96))
    rain(d, lt, 0, W, 0, 140, 110, (190, 200, 230), 200, slant=-10)
    darken(img, 0.12, (40, 40, 70))


def s_leave(img, d, lt, dur, T, A):
    sky(d, (10, 14, 40), (54, 60, 106), 0, 70)
    stars(d, T, 60, 0.8)
    d.rectangle([0, 70, W, H], fill=(206, 214, 236))
    d.polygon([(158, 70), (162, 70), (250, H), (70, H)], fill=(170, 176, 204))
    for i in range(1, 7):
        z = i / 7
        y = 70 + 110 * z * z; off = 10 + 120 * z * z
        for sx in (-1, 1):
            x = 160 + sx * off; hgt = 4 + 50 * z * z
            d.line([(x, y), (x, y - hgt)], fill=(60, 60, 90), width=1 + int(z * 2))
            d.rectangle([x - 1 - z * 2, y - hgt - 2 - z * 2, x + 1 + z * 2, y - hgt], fill=(255, 230, 150))
    p = ease(lt / max(1, dur - 0.5))
    hgt = lerp(46, 5, p); y = lerp(150, 74, p)
    zf = (y - 70) / 110
    for k in range(12):
        fy = y + 4 + k * 6
        if fy > H: break
        d.point((160 + (2 if k % 2 else -2) * (0.5 + zf), fy), fill=(150, 156, 186))
    put_h(img, walkname('boy_b', lt, rate=3), 160, y, hgt)
    for i in range(70):
        ph = (i * 37 % 97) / 97
        sy = (lt * (20 + i % 5 * 6) + ph * H) % H
        sx = (i * 73) % W + 5 * math.sin(lt * 1.5 + i)
        d.point((sx, sy), fill=(255, 255, 255))
        if i % 4 == 0: d.point((sx + 1, sy), fill=(255, 255, 255))
    darken(img, ease((lt - dur + 2.5) / 2.5) * 0.7)


def s_outro(img, d, lt, dur, T, A):
    sky(d, (4, 4, 20), (30, 26, 70), 0, 140)
    stars(d, T)
    meteor(d, lt, 3.5, 280, 20, -120, 50, 1.2)
    put(img, 'heart', 230, 40, 1, tint=(255, 240, 200), alpha=0.5 + 0.5 * math.sin(lt * 2))
    hills(d, 140, 5, 0.02, 1, (12, 10, 30))
    put(img, 'boy_b', 110, 140, 1, tint=(12, 10, 30))
    a = ease((lt - 1.5) / 2)
    bigtext(img, META.get('ti', ''), 160, 70, 3, (255, 222, 96), (90, 30, 70), a)
    bigtext(img, 'THE END', 160, 106, 1, (230, 230, 255), (30, 20, 60), ease((lt - 3.5) / 1.5))
    darken(img, ease((lt - dur + 2.5) / 2.3))


LYRIC_SCENES = [s_meet0, s_meet1, s_eyes, s_dream, s_cloud, s_drift, s_rain, s_sprout,
                s_future, s_happy, s_book, s_moon, s_game, s_trueheart, s_secret, s_quiz,
                s_shadow, s_night, s_boat, s_heartlake, s_lighthouse, s_harbor,
                s_together, s_fireworks, s_theater, s_polaroid, s_timelapse, s_calendar,
                s_hourglass, s_beach, s_believe, s_leave]
GAP_SCENES = [s_interlude, s_outro]

# ---------------------------------------------------------------- data
HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, 'build')
META = {}; LINES = []; SCHED = []
DUR = 0.0; NFR = 0; AMP = SPEC = None


def load(song, lyrics):
    global DUR, NFR, AMP, SPEC
    for raw in open(lyrics, encoding='utf-8-sig'):
        raw = raw.strip()
        m = re.match(r'\[(ti|ar):(.*)\]', raw)
        if m: META[m.group(1)] = m.group(2).strip(); continue
        m = re.match(r'\[(\d+):(\d+(?:\.\d+)?)\](.*)', raw)
        if m: LINES.append((int(m.group(1)) * 60 + float(m.group(2)), m.group(3).strip()))
    LINES.sort()
    DUR = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', song]))
    NFR = int(DUR * FPS)

    # one scene per sung line; blank lines followed by more than 5 s of music become the interlude and the outro
    SCHED.append((0.0, s_intro))
    k = 0; gaps = list(GAP_SCENES)
    for i, (t, txt) in enumerate(LINES):
        nxt = LINES[i + 1][0] if i + 1 < len(LINES) else DUR
        if txt:
            SCHED.append((t, LYRIC_SCENES[k % len(LYRIC_SCENES)])); k += 1
        elif nxt - t > 5 and gaps:
            SCHED.append((t, gaps.pop(0)))
    SCHED.append((DUR, None))

    pcm = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', song, '-ac', '1', '-ar', '24000', '-f', 's16le', '-']),
                        np.int16).astype(np.float32) / 32768
    spf = 24000 // FPS
    pcm = np.pad(pcm, (0, max(0, NFR * spf - len(pcm))))
    rms = np.array([np.sqrt(np.mean(pcm[i * spf:(i + 1) * spf] ** 2) + 1e-9) for i in range(NFR)])
    AMP = np.clip(rms / (np.percentile(rms, 95) + 1e-9), 0, 1)
    edges = np.geomspace(120, 8000, 33)
    freqs = np.fft.rfftfreq(2048, 1 / 24000)
    win = np.hanning(2048)
    spec = []
    for i in range(NFR):
        c = i * spf + spf // 2
        seg = pcm[max(0, c - 1024):c + 1024]
        if len(seg) < 2048: seg = np.pad(seg, (0, 2048 - len(seg)))
        mag = np.abs(np.fft.rfft(seg * win))
        spec.append([mag[(freqs >= edges[j]) & (freqs < edges[j + 1])].mean() for j in range(32)])
    spec = np.log1p(np.nan_to_num(np.array(spec)) * 4)
    SPEC = np.clip(spec / (np.percentile(spec, 98, axis=0) + 1e-9), 0, 1)


_b = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
BAYER = np.tile(np.kron(_b, np.ones((2, 2))), (H // 8 + 1, W // 8 + 1))[:H, :W]


def scene_at(T):
    for i in range(len(SCHED) - 1):
        if SCHED[i][0] <= T < SCHED[i + 1][0]:
            return i
    return len(SCHED) - 2


def render_scene(i, T, fi):
    t0, fn = SCHED[i]
    img = Image.new('RGB', (W, H)); d = ImageDraw.Draw(img); d.fontmode = '1'
    fn(img, d, T - t0, SCHED[i + 1][0] - t0, T, float(AMP[min(fi, NFR - 1)]))
    return img, d


def lyric_at(T):
    cur = None
    for i, (t, txt) in enumerate(LINES):
        if t <= T: cur = i
    if cur is None or not LINES[cur][1]: return None
    nxt = LINES[cur + 1][0] if cur + 1 < len(LINES) else DUR
    return LINES[cur][1], T - LINES[cur][0], nxt - LINES[cur][0]


def frame(fi):
    T = fi / FPS
    i = scene_at(T)
    img, d = render_scene(i, T, fi)
    ly = lyric_at(T)
    if ly: dialog(img, d, *ly)
    a = np.asarray(img)
    lt = T - SCHED[i][0]
    if i > 0 and lt < 0.45:
        prev, pd = render_scene(i - 1, SCHED[i][0] - 1 / FPS, fi)
        ply = lyric_at(SCHED[i][0] - 1 / FPS)
        if ply: dialog(prev, pd, *ply)
        mask = BAYER < (lt / 0.45)
        a = np.where(mask[..., None], a, np.asarray(prev))
    if T < 0.6: a = (a * (T / 0.6)).astype(np.uint8)
    return a


def render_chunk(job):
    lo, hi, path = job
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W * SC}x{H * SC}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-tune', 'animation',
                          '-crf', '18', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    for fi in range(lo, hi):
        p.stdin.write(np.repeat(np.repeat(frame(fi), SC, 0), SC, 1).tobytes())
    p.stdin.close()
    if p.wait(): raise RuntimeError(f'ffmpeg failed on frames {lo}-{hi}')
    return path


def main():
    ap = argparse.ArgumentParser(description='小宇 · 8-bit 像素 MV')
    ap.add_argument('song', help='歌曲音频，例如 小宇.mp3')
    ap.add_argument('--lyrics', required=True, help='对应的 .lrc 歌词')
    ap.add_argument('-o', '--out', default=os.path.join(BUILD, '小宇_8bit_MV.mp4'))
    ap.add_argument('--jobs', type=int, default=min(4, os.cpu_count() or 1), help='并行渲染的进程数')
    ap.add_argument('--stills', help='只抽帧检查：逗号分隔的秒数，输出到 build/stills/')
    args = ap.parse_args()
    load(args.song, args.lyrics)

    if args.stills:
        out = os.path.join(BUILD, 'stills'); os.makedirs(out, exist_ok=True)
        for t in map(float, args.stills.split(',')):
            path = os.path.join(out, f'{t:07.2f}.png')
            Image.fromarray(frame(int(t * FPS))).resize((W * 2, H * 2), Image.NEAREST).save(path)
            print(path)
        return

    # forked workers inherit the analysed audio; each encodes one slice of frames, then the slices are joined without re-encoding
    parts = os.path.join(BUILD, 'parts'); os.makedirs(parts, exist_ok=True)
    step = -(-NFR // args.jobs)
    jobs = [(lo, min(lo + step, NFR), os.path.join(parts, f'part{n}.mp4')) for n, lo in enumerate(range(0, NFR, step))]
    with multiprocessing.get_context('fork').Pool(len(jobs)) as pool:
        paths = pool.map(render_chunk, jobs)
    listing = os.path.join(parts, 'list.txt')
    with open(listing, 'w') as f:
        f.writelines(f"file '{p}'\n" for p in paths)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', listing, '-i', args.song,
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                    '-movflags', '+faststart', args.out], check=True)
    shutil.rmtree(parts)
    print(args.out)


if __name__ == '__main__':
    main()
