"""老公爱 · 这首歌自己的道具：霓虹字和霓虹城、手机和聊天气泡、钢琴键、信封、天平、红绿灯、跑车、音箱和打碟台、
麦克风、寺庙、飞蛾和火苗、玻璃心、字幕下面的小粉心。签名里的 (img, d) 是画布和它的 ImageDraw。"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
from pix import (W, H, FONT, FONT_S, OUT, SKIN, SKIN_S, clamp, lerp, lerpc, ease, eout, glow, tfill, blend_box, paste, outline,
                 text, rng, sky, stars, city, heart_poly)

PINK, PINK_L, PINK_D = (255, 80, 170), (255, 190, 225), (170, 30, 110)
CYAN, CYAN_L = (80, 236, 255), (210, 250, 255)
PURP, PURP_L = (170, 110, 255), (220, 196, 255)
YEL = (255, 226, 90)
NIGHT_SKY = ((0, (10, 6, 30)), (0.5, (34, 16, 64)), (0.85, (84, 30, 98)), (1, (140, 50, 120)))
TITLE_KW = dict(top=(255, 214, 236), bot=(255, 64, 158), line=(150, 18, 96), out=(36, 6, 36))


# ---------------------------------------------------------------- 字幕下面的小粉心
@lru_cache(None)
def _mini(ph):
    rows = [".P.P.", "PWPPP", "PPPPP", ".PPP.", "..P.."] if ph == 0 else [".P.P.", "PPPPP", "PWPPP", ".PPP.", "..P.."]
    im = Image.new('RGBA', (5, 5)); px = im.load()
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c != '.': px[x, y] = ((255, 96, 170) if c == 'P' else (255, 236, 246)) + (255,)
    return outline(im, (60, 10, 50))


def mini_heart(img, x, y, T, alpha=1.0):
    im = _mini(int(T * 4) % 2)
    if alpha < 1:
        a = np.array(im); a[pix.bayer(im.height, im.width, int(x), int(y)) >= alpha, 3] = 0; im = Image.fromarray(a)
    img.paste(im, (int(round(x)) - 3, int(round(y)) - 3), im)


# ---------------------------------------------------------------- 霓虹字
@lru_cache(None)
def _mask(s, scale, small):
    font = FONT_S if small else FONT
    w = int(font.getlength(s)) + 4; h = font.size + 4
    m = Image.new('L', (w, h)); md = ImageDraw.Draw(m); md.fontmode = '1'
    md.text((2, 1), s, font=font, fill=255)
    a = np.array(m) > 0
    return a.repeat(scale, 0).repeat(scale, 1)


@lru_cache(None)
def neon_img(s, scale, col, on=True, small=False):
    """霓虹灯管字：亮的时候是白芯 + 彩色灯管；灭的时候是暗灰的玻璃管"""
    m = _mask(s, scale, small)
    pad = 2
    m = np.pad(m, pad)
    n = m.copy()
    n[1:] |= m[:-1]; n[:-1] |= m[1:]; n[:, 1:] |= m[:, :-1]; n[:, :-1] |= m[:, 1:]
    core = m.copy()
    if scale >= 3:          # 灯管中间一条白芯
        e = m.copy()
        e[1:] &= m[:-1]; e[:-1] &= m[1:]; e[:, 1:] &= m[:, :-1]; e[:, :-1] &= m[:, 1:]
        core = e
    a = np.zeros(m.shape + (4,), np.uint8)
    if on:
        a[n] = tuple(lerpc(col, (0, 0, 0), 0.35)) + (255,)
        a[m] = tuple(col) + (255,)
        a[core & m] = tuple(lerpc(col, (255, 255, 255), 0.7)) + (255,)
    else:
        a[n] = (30, 26, 40, 255); a[m] = (70, 64, 86, 255)
    return Image.fromarray(a)


def neon(img, s, cx, cy, scale, col, on=1.0, small=False, glow_r=None):
    """在 (cx, cy) 居中放一行霓虹字。on<0.5 时是灭的"""
    lit = on >= 0.5
    im = neon_img(s, scale, tuple(col), lit, small)
    if lit:
        glow(img, cx, cy, glow_r or im.width * 0.62, col, 0.32 * on, im.height * 0.9)
    img.paste(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))), im)
    return im.width


def flicker(T, seed=0, rate=0.06):
    """霓虹偶尔闪一下：返回 0 或 1"""
    r = rng(int(T * 15) * 31 + seed).random()
    return 0.0 if r < rate else 1.0


def title(img, cx, cy, scale=4, alpha=1.0, T=0.0, glow_a=0.35):
    """片名《老公爱》大字：粉色渐变块字 + 粉色光晕"""
    import props
    if glow_a > 0: glow(img, cx, cy, 70 * scale, PINK, glow_a * alpha * (0.85 + 0.15 * math.sin(T * 4)), 22 * scale)
    props.big_text(img, '老公爱', cx, cy, scale, alpha, **TITLE_KW)


# ---------------------------------------------------------------- 霓虹城市夜景
SIGNS = [('LOVE', PINK), ('24H', CYAN), ('KTV', YEL), ('BAR', PURP), ('♥', PINK), ('CLUB', CYAN), ('酒', YEL), ('爱', PINK)]


def night_city(img, d, T, off=0.0, ground=222, signs=True, seed=4, wet=True, sky_stops=NIGHT_SKY):
    sky(img, sky_stops, 0, ground, 6)
    stars(d, T, ground - 80, 0.7, 90)
    glow(img, W / 2, ground, 300, (255, 70, 160), 0.18, 70)
    city(img, d, ground, seed, off * 0.3, (40, 24, 70), (120, 90, 180), 60, 150, 0.25, T, 18, 36)
    city(img, d, ground, seed + 7, off * 0.6, (22, 14, 40), (255, 210, 120), 30, 100, 0.3, T, 20, 44, edge=(60, 40, 90))
    if signs:
        for i, (s, col) in enumerate(SIGNS):
            x = (i * 67 + 30 - off * 0.6) % (W + 100) - 50
            y = 120 + (i * 37) % 60
            neon(img, s, x, y, 1, col, flicker(T, i, 0.08), small=True, glow_r=24)
    d.rectangle([0, ground, W, H], fill=(20, 14, 34))
    if wet:
        for x in range(0, W, 2):
            r = rng(x // 2 + int(off) // 2)
            if r.random() < 0.3:
                c = [PINK, CYAN, YEL, PURP][r.randrange(4)]
                y = ground + 2 + r.randrange(H - ground - 2)
                d.line([(x, y), (x + r.randrange(2, 7), y)], fill=lerpc((20, 14, 34), c, 0.35))
    d.line([(0, ground), (W, ground)], fill=(70, 50, 100))


def street_lines(d, ground, off, col=(200, 190, 230)):
    y = ground + (H - ground) // 2
    for x in range(-40, W + 40, 40):
        xx = x - off % 40
        d.rectangle([xx, y, xx + 18, y + 1], fill=col)


# ---------------------------------------------------------------- 房间
def room(img, d, T, night=1.0, wall=(58, 40, 86), floor_y=200, window=True, lamp=1.0):
    d.rectangle([0, 0, W, floor_y], fill=wall)
    for x in range(0, W, 24): d.line([(x, 0), (x, floor_y)], fill=lerpc(wall, (0, 0, 0), 0.12))
    d.rectangle([0, floor_y, W, H], fill=lerpc(wall, (40, 26, 30), 0.6))
    for x in range(-40, W, 30): d.line([(x, H), (x + 60, floor_y)], fill=lerpc(wall, (20, 10, 20), 0.7))
    if window:
        wx, wy, ww, wh = 300, 40, 110, 90
        d.rectangle([wx - 4, wy - 4, wx + ww + 4, wy + wh + 4], fill=(30, 20, 44))
        sub = Image.new('RGB', (ww, wh)); sd = ImageDraw.Draw(sub)
        sub.paste(pix.vgrad(ww, wh, tuple((p, lerpc(c, (120, 170, 230), 1 - night)) for p, c in NIGHT_SKY), 5))
        for i in range(30):
            r = rng(i); x, y = r.randrange(ww), r.randrange(wh // 2)
            if math.sin(T * 2 + i) > 0: sd.point((x, y), fill=(255, 250, 220))
        pix.moon(sd, 80, 22, 9)
        for i in range(8):
            r = rng(i + 50); bx = i * 15 - 4; bh = r.randrange(20, 50)
            sd.rectangle([bx, wh - bh, bx + 12, wh], fill=(26, 18, 46))
            for yy in range(wh - bh + 3, wh - 2, 5):
                if r.random() < 0.5: sd.point((bx + 3 + r.randrange(6), yy), fill=(255, 210, 120))
        img.paste(sub, (wx, wy))
        d.line([(wx + ww // 2, wy), (wx + ww // 2, wy + wh)], fill=(30, 20, 44), width=2)
        d.line([(wx, wy + wh // 2), (wx + ww, wy + wh // 2)], fill=(30, 20, 44), width=2)
        tfill(img, 'polygon', [(wx, wy + wh), (wx + ww, wy + wh), (wx + ww - 30, floor_y + 60), (wx - 70, floor_y + 60)], (150, 170, 255), 0.06)
    # 海报
    d.rectangle([60, 40, 110, 110], fill=(30, 20, 44)); d.rectangle([62, 42, 108, 108], fill=(255, 90, 160))
    neon(img, 'HIP', 85, 62, 1, (255, 240, 120), 1, small=True, glow_r=1); neon(img, 'HOP', 85, 84, 1, (40, 20, 60), 1, small=True, glow_r=1)
    if lamp > 0: glow(img, 200, 150, 200, (255, 190, 120), 0.12 * lamp)


def bed(d, x, base, w=150, col=(240, 236, 250), blanket=(120, 90, 200)):
    d.rectangle([x - 4, base - 46, x + 4, base], fill=(110, 70, 50))
    d.rectangle([x, base - 22, x + w, base - 8], fill=col)
    d.rectangle([x + 30, base - 26, x + w, base - 10], fill=blanket)
    d.rectangle([x + 4, base - 28, x + 26, base - 20], fill=(255, 255, 255))
    d.rectangle([x, base - 8, x + w, base - 2], fill=(110, 70, 50))
    d.rectangle([x + 2, base - 2, x + 6, base], fill=(80, 50, 36)); d.rectangle([x + w - 6, base - 2, x + w - 2, base], fill=(80, 50, 36))


def desk(img, d, x, base, w=120, lamp_on=1.0):
    top = base - 34
    d.rectangle([x, top, x + w, top + 4], fill=(150, 100, 64)); d.line([(x, top + 4), (x + w, top + 4)], fill=(100, 64, 44))
    d.rectangle([x + 4, top + 5, x + 8, base], fill=(110, 72, 48)); d.rectangle([x + w - 8, top + 5, x + w - 4, base], fill=(110, 72, 48))
    lx = x + w - 22
    d.line([(lx, top), (lx - 6, top - 22), (lx + 4, top - 32)], fill=(60, 60, 80), width=2)
    d.polygon([(lx - 2, top - 36), (lx + 12, top - 34), (lx + 10, top - 26)], fill=(255, 210, 90))
    if lamp_on > 0:
        tfill(img, 'polygon', [(lx + 6, top - 28), (lx + 12, top - 30), (x + 30, top), (x + w - 10, top)], (255, 230, 150), 0.18 * lamp_on)
        glow(img, lx + 8, top - 28, 40, (255, 220, 140), 0.3 * lamp_on)
    return top


# ---------------------------------------------------------------- 手机和聊天
def phone(img, d, x0, y0, w, h, body=(26, 24, 36), screen=(18, 16, 30), lit=1.0):
    """竖着的大手机，返回屏幕区域 (x0, y0, x1, y1)"""
    d.rounded_rectangle([x0 - 1, y0 - 1, x0 + w + 1, y0 + h + 1], 8, fill=OUT)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], 7, fill=body)
    d.rounded_rectangle([x0 + 2, y0 + 2, x0 + w - 2, y0 + h - 2], 6, outline=(70, 66, 90))
    sx0, sy0, sx1, sy1 = x0 + 5, y0 + 12, x0 + w - 5, y0 + h - 12
    d.rectangle([sx0, sy0, sx1, sy1], fill=lerpc((6, 6, 12), screen, lit))
    d.rounded_rectangle([x0 + w / 2 - 8, y0 + 5, x0 + w / 2 + 8, y0 + 8], 2, fill=(10, 10, 16))
    d.rounded_rectangle([x0 + w / 2 - 10, y0 + h - 7, x0 + w / 2 + 10, y0 + h - 5], 1, fill=(90, 86, 110))
    if lit > 0: glow(img, x0 + w / 2, y0 + h / 2, w * 1.1, (160, 180, 255), 0.12 * lit, h * 0.7)
    return sx0, sy0, sx1, sy1


def status_bar(d, box, T, col=(230, 230, 250)):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y0 + 9], fill=(30, 26, 50))
    text_s(d, '23:59', x0 + 3, y0 - 1, col)
    d.rectangle([x1 - 12, y0 + 3, x1 - 4, y0 + 6], outline=col); d.rectangle([x1 - 11, y0 + 4, x1 - 8, y0 + 5], fill=(120, 255, 140))


def text_s(d, s, x, y, col):
    d.fontmode = '1'
    d.text((x, y), s, font=FONT_S, fill=col)


def bubble(img, d, x, y, s, side='l', col=(255, 255, 255), tc=(30, 26, 40), small=True, a=1.0):
    """聊天气泡：(x, y) 是气泡贴边那一侧的上角；side='l' 靠左，'r' 靠右。返回 (宽, 高)"""
    font = FONT_S if small else FONT
    tw = int(font.getlength(s)); th = font.size
    w, h = tw + 10, th + 6
    bx = x if side == 'l' else x - w
    im = Image.new('RGBA', (w + 4, h + 4)); dd = ImageDraw.Draw(im); dd.fontmode = '1'
    dd.rounded_rectangle([1, 1, w + 1, h + 1], 4, fill=col, outline=OUT)
    if side == 'l': dd.polygon([(1, h - 3), (-3 + 4, h + 3), (8, h)], fill=col)
    else: dd.polygon([(w + 1, h - 3), (w + 3, h + 3), (w - 6, h)], fill=col)
    dd.text((6, 2 + (0 if small else 0)), s, font=font, fill=tc)
    if a < 1:
        arr = np.array(im); arr[pix.bayer(im.height, im.width, int(bx), int(y)) >= a, 3] = 0; im = Image.fromarray(arr)
    img.paste(im, (int(bx) - 1, int(y) - 1), im)
    return w, h


def finger(d, x, y, s=2, press=0.0):
    """从下往上伸过来的食指，(x, y) 是指尖"""
    y = y + press * 2 * s
    d.rounded_rectangle([x - 3 * s, y, x + 3 * s, y + 40 * s], 3 * s, fill=OUT)
    d.rounded_rectangle([x - 3 * s + 1, y + 1, x + 3 * s - 1, y + 40 * s], 3 * s, fill=SKIN)
    d.rectangle([x - 2 * s + 1, y + 2, x + 2 * s - 1, y + 4 * s], fill=(255, 236, 226))
    d.line([(x - 3 * s + 2, y + 9 * s), (x + 3 * s - 2, y + 9 * s)], fill=SKIN_S)
    d.rounded_rectangle([x - 8 * s, y + 14 * s, x + 6 * s, y + 46 * s], 4 * s, fill=OUT)
    d.rounded_rectangle([x - 8 * s + 1, y + 14 * s + 1, x + 6 * s - 1, y + 46 * s], 4 * s, fill=SKIN)
    d.line([(x - 8 * s + 2, y + 20 * s), (x - 3 * s, y + 20 * s)], fill=SKIN_S)


# ---------------------------------------------------------------- 钢琴键、音符
def keys(d, x0, y0, w, h, n, lit=(), col=(255, 120, 190)):
    kw = w / n
    for i in range(n):
        x = x0 + i * kw
        d.rectangle([x, y0, x + kw - 1, y0 + h], fill=col if i in lit else (250, 248, 255), outline=(40, 36, 56))
    for i in range(n - 1):
        if i % 7 in (2, 6): continue
        x = x0 + (i + 1) * kw - kw * 0.3
        d.rectangle([x, y0, x + kw * 0.6, y0 + h * 0.6], fill=(30, 26, 40) if (100 + i) not in lit else col)


NOTE = ["..XX", "..XX", "..X.", "..X.", "XXX.", "XX.."]
NOTE2 = ["XXXXX", "X...X", "X...X", "X..XX", "XX.XX", "XX..."]


@lru_cache(None)
def note_img(kind, col, s):
    rows = NOTE if kind == 0 else NOTE2
    im = Image.new('RGBA', (len(rows[0]), len(rows))); px = im.load()
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c == 'X': px[x, y] = tuple(col) + (255,)
    im = outline(im, OUT)
    return im.resize((im.width * s, im.height * s), Image.NEAREST)


def note(img, x, y, kind=0, col=PINK, s=1):
    im = note_img(kind % 2, tuple(col), s)
    img.paste(im, (int(round(x - im.width / 2)), int(round(y - im.height / 2))), im)


def notes_rise(img, T, x, y, n=6, spread=40, h=120, seed=0, cols=(PINK, CYAN, YEL, PURP), s=1, speed=0.6):
    for i in range(n):
        r = rng(i * 7 + seed)
        k = (T * speed + r.random()) % 1
        nx = x + (r.random() - 0.5) * spread + 10 * math.sin(T * 2 + i)
        note(img, nx, y - k * h, i, cols[i % len(cols)], s)


# ---------------------------------------------------------------- 信封、信纸
def envelope(img, d, cx, cy, w, h, open_=0.0, col=(250, 244, 230), seal=(230, 50, 90)):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=OUT)
    d.rectangle([x0, y0, x1, y1], fill=col)
    d.line([(x0, y1), (cx, cy + 2), (x1, y1)], fill=lerpc(col, (0, 0, 0), 0.2))
    tip = lerp(cy + 4, y0 - h * 0.55, ease(open_))
    d.polygon([(x0, y0), (x1, y0), (cx, tip)], fill=lerpc(col, (0, 0, 0), 0.08), outline=lerpc(col, (0, 0, 0), 0.3))
    if open_ < 0.3:
        d.polygon(heart_poly(cx, tip - 2, 0.32), fill=seal)


def letter(d, x0, y0, w, h, lines=6, col=(255, 252, 240), ink=(80, 70, 110), f=1.0, seed=0):
    d.rectangle([x0 - 1, y0 - 1, x0 + w + 1, y0 + h + 1], fill=OUT)
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=col)
    for i in range(lines):
        y = y0 + 8 + i * (h - 12) / lines
        r = rng(i + seed)
        ln = (w - 12) * (0.6 + 0.4 * r.random()) * clamp(f * lines - i)
        if ln > 0:
            x = x0 + 6
            while x < x0 + 6 + ln:
                seg = r.randrange(3, 9); d.line([(x, y), (min(x + seg, x0 + 6 + ln), y)], fill=ink); x += seg + 2


# ---------------------------------------------------------------- 天平
def balance(img, d, cx, base, tilt, lw=80, col=(220, 190, 110), col_d=(160, 120, 60)):
    """天平：tilt>0 右边沉下去。返回 (左盘中心, 右盘中心)"""
    top = base - 120
    d.rectangle([cx - 3, top, cx + 3, base], fill=col_d); d.rectangle([cx - 24, base - 6, cx + 24, base], fill=col_d)
    d.ellipse([cx - 6, top - 6, cx + 6, top + 6], fill=col)
    a = math.radians(14 * tilt)
    lx, ly = cx - lw * math.cos(a), top - lw * math.sin(a)
    rx, ry = cx + lw * math.cos(a), top + lw * math.sin(a)
    d.line([(lx, ly), (rx, ry)], fill=col, width=4)
    pans = []
    for px, py in ((lx, ly), (rx, ry)):
        d.line([(px, py), (px - 24, py + 50)], fill=col_d); d.line([(px, py), (px + 24, py + 50)], fill=col_d)
        d.chord([px - 30, py + 38, px + 30, py + 62], 0, 180, fill=col, outline=col_d)
        pans.append((px, py + 50))
    return pans


def brick(img, d, x, y, s, col, label='谎', lc=(255, 255, 255)):
    d.rectangle([x - s - 1, y - s - 1, x + s + 1, y + s + 1], fill=OUT)
    d.rectangle([x - s, y - s, x + s, y + s], fill=col)
    d.line([(x - s, y - s), (x + s, y - s)], fill=lerpc(col, (255, 255, 255), 0.4))
    if s >= 7: text(img, label, x, y + 1, col=lc, font=FONT_S if s < 10 else FONT, shadow=False)


# ---------------------------------------------------------------- 红绿灯、路牌
def traffic_light(img, d, x, base, state, T, h=90):
    d.rectangle([x - 1, base - h, x + 1, base], fill=(60, 56, 70))
    d.rectangle([x - 7, base - h - 34, x + 7, base - h], fill=(30, 28, 40), outline=OUT)
    for i, col in enumerate(((255, 60, 70), (255, 200, 60), (80, 240, 120))):
        on = state == i
        c = col if on else lerpc(col, (20, 20, 30), 0.75)
        d.ellipse([x - 4, base - h - 31 + i * 10, x + 4, base - h - 23 + i * 10], fill=c)
        if on: glow(img, x, base - h - 27 + i * 10, 22, col, 0.45)


# ---------------------------------------------------------------- 跑车（侧面，朝右）
def car(img, d, x, base, T, col=(240, 60, 120), col_d=(170, 30, 80), roll=0.0, bounce=0.0, lights=1.0, driver=True):
    """x 是车尾，车长 96，base 是轮子底"""
    y = base - 8 - bounce
    if lights > 0:
        tfill(img, 'polygon', [(x + 94, y - 12), (x + 94, y - 6), (x + 180, y + 6), (x + 180, y - 30)], (255, 250, 200), 0.18 * lights)
    body = [(x, y - 4), (x + 2, y - 16), (x + 26, y - 18), (x + 40, y - 30), (x + 66, y - 30), (x + 80, y - 18), (x + 94, y - 14), (x + 96, y - 4)]
    d.polygon([(px, py + 1) for px, py in body], fill=OUT)
    d.polygon(body, fill=col)
    d.rectangle([x + 2, y - 6, x + 95, y - 3], fill=col_d)
    d.polygon([(x + 30, y - 18), (x + 42, y - 28), (x + 64, y - 28), (x + 76, y - 18)], fill=(130, 200, 255))
    d.line([(x + 53, y - 28), (x + 53, y - 18)], fill=col, width=2)
    d.line([(x + 6, y - 12), (x + 90, y - 12)], fill=lerpc(col, (255, 255, 255), 0.4))
    if driver:
        d.rectangle([x + 58, y - 26, x + 64, y - 19], fill=(30, 26, 40)); d.rectangle([x + 60, y - 22, x + 65, y - 19], fill=SKIN)
        d.line([(x + 61, y - 22), (x + 65, y - 22)], fill=(16, 14, 24))
    d.rectangle([x + 92, y - 12, x + 95, y - 9], fill=(255, 250, 200)); d.rectangle([x, y - 14, x + 2, y - 10], fill=(255, 60, 60))
    import props
    for wx in (x + 20, x + 76):
        props.wheel(d, wx, base - 8, 8, roll)
    glow(img, x + 48, base + 1, 60, PINK, 0.25, 6)


# ---------------------------------------------------------------- 音箱、打碟台、麦克风
def speaker(img, d, x, y, w, h, pump=0.0, col=(36, 32, 48)):
    d.rectangle([x - 1, y - 1, x + w + 1, y + h + 1], fill=OUT); d.rectangle([x, y, x + w, y + h], fill=col)
    for cy_, r in ((y + h * 0.3, w * 0.22), (y + h * 0.68, w * 0.36)):
        rr = r * (1 + 0.12 * pump)
        d.ellipse([x + w / 2 - rr - 2, cy_ - rr - 2, x + w / 2 + rr + 2, cy_ + rr + 2], fill=(70, 66, 90))
        d.ellipse([x + w / 2 - rr, cy_ - rr, x + w / 2 + rr, cy_ + rr], fill=(20, 18, 28))
        d.ellipse([x + w / 2 - rr * 0.35, cy_ - rr * 0.35, x + w / 2 + rr * 0.35, cy_ + rr * 0.35], fill=(90, 86, 110))
    if pump > 0.2:
        for k in range(3):
            r = w * (0.6 + 0.3 * k) * (1 + pump * 0.4)
            d.arc([x + w / 2 - r, y + h * 0.68 - r, x + w / 2 + r, y + h * 0.68 + r], 300, 60, fill=lerpc((40, 30, 60), CYAN, pump * (1 - k / 3)))
            d.arc([x + w / 2 - r, y + h * 0.68 - r, x + w / 2 + r, y + h * 0.68 + r], 120, 240, fill=lerpc((40, 30, 60), CYAN, pump * (1 - k / 3)))


def pads(img, d, x0, y0, n, size, lit, cols=(PINK, CYAN, YEL, PURP)):
    """打击垫：n×n 个方块，lit(i, j) 返回 0..1 的亮度"""
    for j in range(n):
        for i in range(n):
            x, y = x0 + i * (size + 3), y0 + j * (size + 3)
            c = cols[(i + j) % len(cols)]
            b = lit(i, j)
            d.rectangle([x - 1, y - 1, x + size + 1, y + size + 1], fill=OUT)
            d.rectangle([x, y, x + size, y + size], fill=lerpc(lerpc(c, (30, 26, 40), 0.75), c, b))
            if b > 0.5: glow(img, x + size / 2, y + size / 2, size * 1.4, c, 0.3 * b)


def turntable(d, cx, cy, r, T, col=(40, 36, 52)):
    d.rectangle([cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8], fill=col, outline=OUT)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(16, 14, 22))
    for k in range(max(0, min(3, (r - 5) // 4))): d.ellipse([cx - r + 4 + k * 4, cy - r + 4 + k * 4, cx + r - 4 - k * 4, cy + r - 4 - k * 4], outline=(40, 36, 56))
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=PINK)
    a = T * 7
    d.line([(cx, cy), (cx + math.cos(a) * (r - 2), cy + math.sin(a) * (r - 2))], fill=(120, 116, 150))


def mic(d, x, y, s=1.0, col=(200, 200, 216), stand=True, base=None):
    """立麦：(x, y) 是麦头中心"""
    r = 6 * s
    if stand:
        d.line([(x, y + r), (x, base or y + 90 * s)], fill=(60, 56, 72), width=max(1, int(2 * s)))
        b = base or y + 90 * s
        d.line([(x - 14 * s, b), (x + 14 * s, b)], fill=(60, 56, 72), width=max(1, int(2 * s)))
    d.rounded_rectangle([x - r - 1, y - r * 1.4 - 1, x + r + 1, y + r * 1.4 + 1], r, fill=OUT)
    d.rounded_rectangle([x - r, y - r * 1.4, x + r, y + r * 1.4], r, fill=col)
    for k in range(int(-r), int(r), 2): d.line([(x - r + 1, y + k), (x + r - 1, y + k)], fill=lerpc(col, (40, 40, 50), 0.4))


# ---------------------------------------------------------------- 寺庙
def temple(img, d, cx, base, s=1.0, T=0.0, lanterns=True):
    """红柱金瓦的庙门：(cx, base) 是台阶底边中点"""
    R, Rd, G, Gd = (200, 40, 50), (140, 24, 36), (240, 190, 70), (180, 120, 40)
    w = 150 * s
    d.rectangle([cx - w / 2 - 14 * s, base - 10 * s, cx + w / 2 + 14 * s, base], fill=(170, 160, 170))
    d.rectangle([cx - w / 2 - 6 * s, base - 16 * s, cx + w / 2 + 6 * s, base - 10 * s], fill=(200, 190, 196))
    top = base - 110 * s
    d.rectangle([cx - w / 2, top, cx + w / 2, base - 16 * s], fill=(120, 30, 40))
    for k in range(4):
        px = cx - w / 2 + 6 * s + k * (w - 18 * s) / 3
        d.rectangle([px, top, px + 8 * s, base - 16 * s], fill=R); d.line([(px + 2 * s, top), (px + 2 * s, base - 16 * s)], fill=(240, 90, 90))
    d.rectangle([cx - 22 * s, top + 30 * s, cx + 22 * s, base - 16 * s], fill=(70, 20, 30))
    d.rectangle([cx - 20 * s, top + 32 * s, cx + 20 * s, base - 16 * s], fill=(255, 210, 120) if lanterns else (90, 30, 30))
    if lanterns: glow(img, cx, top + 60 * s, 60 * s, (255, 200, 120), 0.3)
    # 匾
    d.rectangle([cx - 20 * s, top + 8 * s, cx + 20 * s, top + 24 * s], fill=Gd); d.rectangle([cx - 18 * s, top + 10 * s, cx + 18 * s, top + 22 * s], fill=(30, 30, 60))
    # 屋顶：两层飞檐
    for k, (yy, ww) in enumerate(((top, w / 2 + 30 * s), (top - 34 * s, w / 2 + 6 * s))):
        roof = [(cx - ww - 8 * s, yy - 12 * s), (cx - ww + 10 * s, yy - 6 * s), (cx - ww + 30 * s, yy - 24 * s), (cx + ww - 30 * s, yy - 24 * s),
                (cx + ww - 10 * s, yy - 6 * s), (cx + ww + 8 * s, yy - 12 * s), (cx + ww, yy + 2 * s), (cx - ww, yy + 2 * s)]
        d.polygon(roof, fill=Gd)
        d.polygon([(px, py - 2 * s) for px, py in roof[:6]] + [(cx + ww - 2 * s, yy - 2 * s), (cx - ww + 2 * s, yy - 2 * s)], fill=G)
        for x in range(int(cx - ww + 14 * s), int(cx + ww - 14 * s), max(2, int(5 * s))):
            d.line([(x, yy - 20 * s), (x, yy)], fill=Gd)
        if k == 0: d.rectangle([cx - w / 2 + 10 * s, yy - 34 * s, cx + w / 2 - 10 * s, yy - 22 * s], fill=(120, 30, 40))
    if lanterns:
        for lx in (cx - w / 2 - 2 * s, cx + w / 2 + 2 * s):
            sw = 2 * math.sin(T * 2 + lx)
            d.line([(lx, top + 2 * s), (lx + sw, top + 10 * s)], fill=(60, 30, 30))
            d.ellipse([lx + sw - 7 * s, top + 10 * s, lx + sw + 7 * s, top + 28 * s], fill=(255, 60, 60))
            d.rectangle([lx + sw - 3 * s, top + 27 * s, lx + sw + 3 * s, top + 30 * s], fill=G)
            glow(img, lx + sw, top + 19 * s, 22 * s, (255, 120, 90), 0.4)


# ---------------------------------------------------------------- 飞蛾、火苗
def flame(img, d, x, base, h, T, seed=0, a=1.0):
    glow(img, x, base - h * 0.5, h * 1.6, (255, 160, 60), 0.4 * a)
    for k, (col, sc) in enumerate((((255, 90, 40), 1.0), ((255, 180, 60), 0.7), ((255, 250, 200), 0.38))):
        hh = h * sc * (0.9 + 0.1 * math.sin(T * 13 + seed + k))
        ww = h * 0.32 * sc
        sway = 2 * math.sin(T * 9 + seed) * sc
        d.polygon([(x - ww, base - hh * 0.25), (x - ww * 0.6, base - hh * 0.6), (x + sway, base - hh), (x + ww * 0.6, base - hh * 0.55),
                   (x + ww, base - hh * 0.25), (x + ww * 0.5, base), (x - ww * 0.5, base)], fill=col)


def moth(d, x, y, T, s=2, col=(220, 210, 190), col_d=(150, 130, 110)):
    f = int(T * 14) % 2
    d.rectangle([x - s, y - 2 * s, x, y + 3 * s], fill=(80, 64, 50))
    if f:
        d.polygon([(x - s, y - s), (x - 7 * s, y - 6 * s), (x - 8 * s, y + 1 * s), (x - s, y + s)], fill=col)
        d.polygon([(x, y - s), (x + 6 * s, y - 6 * s), (x + 7 * s, y + 1 * s), (x, y + s)], fill=col)
        d.point([(x - 5 * s, y - 2 * s), (x + 4 * s, y - 2 * s)], fill=col_d)
    else:
        d.polygon([(x - s, y), (x - 6 * s, y + 3 * s), (x - 4 * s, y + 5 * s), (x - s, y + 2 * s)], fill=col)
        d.polygon([(x, y), (x + 5 * s, y + 3 * s), (x + 3 * s, y + 5 * s), (x, y + 2 * s)], fill=col)
    d.line([(x - s, y - 2 * s), (x - 3 * s, y - 5 * s)], fill=col_d); d.line([(x, y - 2 * s), (x + 2 * s, y - 5 * s)], fill=col_d)


def fire_wall(img, d, T, y0, n=16, h=40, seed=0, a=1.0):
    for i in range(n):
        r = rng(i + seed)
        x = (i + 0.5) * W / n + r.uniform(-8, 8)
        flame(img, d, x, H + 6, h * (0.7 + 0.6 * r.random()) * (0.9 + 0.2 * math.sin(T * 5 + i)) + (H - y0), T, i, a)


def embers(d, T, n=40, seed=0, box=(0, 0, W, H), col=(255, 180, 80)):
    x0, y0, x1, y1 = box
    for i in range(n):
        r = rng(i * 13 + seed)
        k = (T * (0.3 + 0.3 * r.random()) + r.random()) % 1
        x = x0 + r.random() * (x1 - x0) + 8 * math.sin(T * 2 + i)
        y = y1 - k * (y1 - y0)
        d.point((x, y), fill=lerpc(col, (120, 40, 40), k))


# ---------------------------------------------------------------- 心
def pix_heart(img, cx, cy, s, col=PINK, hi=PINK_L, lo=PINK_D, alpha=1.0):
    import motifs
    im = motifs.heart_img(s, col, hi, lo)
    if alpha < 1:
        a = np.array(im); a[pix.bayer(im.height, im.width, 0, 0) >= alpha, 3] = 0; im = Image.fromarray(a)
    img.paste(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))), im)


def heart_burst(img, d, t, cx, cy, n=12, r=60, col=PINK, life=0.8, seed=0):
    if not 0 <= t < life: return
    f = t / life
    for i in range(n):
        a = 2 * math.pi * i / n + seed
        x, y = cx + math.cos(a) * r * eout(f), cy + math.sin(a) * r * eout(f) + 10 * f * f
        if f < 0.7 or i % 2: pix.put(img, 'heart', x, y, 1, tint=col if i % 3 else None)


def scan(img, y, h, col=(255, 255, 255), a=0.12):
    """水平扫描线"""
    if a > 0 and 0 <= y < H: blend_box(img, (0, int(y), W, min(H, int(y + h))), col, np.full((min(H, int(y + h)) - int(y), W), a))


def scanlines(img, a=0.08):
    arr = np.asarray(img).copy()
    arr[::2] = (arr[::2] * (1 - a)).astype(np.uint8)
    img.paste(Image.fromarray(arr))


def rgb_split(img, k):
    """故障效果：红蓝通道错开 k 个像素"""
    if k < 1: return
    a = np.asarray(img).copy()
    a[..., 0] = np.roll(a[..., 0], int(k), 1); a[..., 2] = np.roll(a[..., 2], -int(k), 1)
    img.paste(Image.fromarray(a))


def glitch(img, T, k, seed=0):
    """横向错位的故障条"""
    if k <= 0: return
    a = np.asarray(img).copy()
    r = rng(int(T * 20) + seed)
    for _ in range(int(6 * k)):
        y = r.randrange(H); h = r.randrange(2, 12); dx = r.randrange(-int(20 * k) - 1, int(20 * k) + 2)
        a[y:y + h] = np.roll(a[y:y + h], dx, 1)
    img.paste(Image.fromarray(a))
    rgb_split(img, 2 * k)
