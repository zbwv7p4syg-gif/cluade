"""左转灯 · 道具：跟着节拍闪的转向灯、他的小车（侧面、俯视、车尾）、手机和聊天界面、手、霓虹片名、拍立得、湿马路的倒影。"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
from pix import (W, H, FONT, FONT_S, OUT, SKIN, SKIN_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box,
                 paste, outline, text, rng, sky, stars, rain, city, lamp, with_alpha)

AMB, AMB_L, AMB_D = (255, 172, 36), (255, 232, 140), (186, 100, 22)
TEAL, TEAL_S, TEAL_L = (46, 196, 186), (28, 148, 144), (160, 244, 232)
PINK, PINK_D = (255, 90, 158), (176, 46, 112)
CYAN = (96, 222, 255)
RED = (240, 60, 70)
CREAM = (255, 246, 228)
INK = (14, 10, 30)
NIGHT = ((0, (8, 6, 26)), (0.55, (28, 18, 62)), (1, (84, 40, 104)))
CAR, CAR_S, CAR_L = (238, 230, 212), (192, 180, 162), (255, 252, 240)


# ---------------------------------------------------------------- 节拍上的转向灯
def beat_phase(T):
    """当前拍内的相位 0..1 和拍号"""
    b = pix.AUDIO['beats']
    if len(b) < 2: return (T * 1.1) % 1, int(T * 1.1)
    i = int(np.searchsorted(b, T, 'right')) - 1
    if i < 0:
        per = b[1] - b[0]; k = (T - b[0]) / per
        return k % 1, int(math.floor(k))
    if i >= len(b) - 1:
        per = b[-1] - b[-2]; k = (T - b[-1]) / per
        return k % 1, len(b) - 1 + int(k)
    return (T - b[i]) / (b[i + 1] - b[i]), i


def blink(T, duty=0.5):
    """转向灯跟着拍子一亮一灭：每拍的前半拍亮"""
    return beat_phase(T)[0] < duty


def blink_a(T):
    """亮度：拍点上最亮，半拍后熄灭（带一点余辉）"""
    ph = beat_phase(T)[0]
    return 1.0 if ph < 0.42 else max(0.0, 1 - (ph - 0.42) / 0.12) * 0.6


ARROW = ["....A......", "...AA......", "..AAA......", ".AAAAAAAAAA", "AAAAAAAAAAA", ".AAAAAAAAAA", "..AAA......", "...AA......",
         "....A......"]


@lru_cache(None)
def arrow_img(s=1, col=AMB, left=True, edge=OUT, hi=AMB_L):
    h = len(ARROW); w = len(ARROW[0])
    a = np.zeros((h, w, 4), np.uint8)
    for y, r in enumerate(ARROW):
        for x, ch in enumerate(r):
            if ch == 'A': a[y, x] = (hi if y == 3 and x > 1 else col) + (255,)
    im = Image.fromarray(a)
    if not left: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = im.resize((w * s, h * s), Image.NEAREST)
    return outline(im, edge) if edge else im


def arrow(img, x, y, s, on=1.0, left=True, col=AMB, off=(70, 50, 40), glow_r=None):
    """转向灯箭头（中心在 x, y）。on=1 时亮并带光晕，on=0 时是熄灭的暗色"""
    if on > 0.05 and glow_r != 0:
        glow(img, x, y, glow_r or 9 * s, col, 0.5 * on)
    c = lerpc(off, col, on); hi = lerpc(off, AMB_L if col == AMB else lerpc(col, (255, 255, 255), 0.5), on)
    paste(img, arrow_img(s, c, left, OUT, hi), x, y, 1, 'cc')


# ---------------------------------------------------------------- 他的小车
def _wheel(d, x, y, r, ph):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(30, 28, 38))
    d.ellipse([x - r + 2, y - r + 2, x + r - 2, y + r - 2], fill=(150, 150, 164))
    a = ph * 2 * math.pi
    for k in range(2):
        aa = a + k * math.pi / 2
        d.line([(x - math.cos(aa) * (r - 2), y - math.sin(aa) * (r - 2)), (x + math.cos(aa) * (r - 2), y + math.sin(aa) * (r - 2))],
               fill=(96, 96, 110))
    d.point((x, y), fill=(220, 220, 230))


@lru_cache(None)
def car_side(sig=0, ph=0, lights=True, brake=False, body=CAR, body_s=CAR_S, glass=(52, 76, 120), driver=None):
    """侧面的小车，车头朝右，62×28，车轮底边在 y=26。sig=1 时左转灯（近侧）亮。driver='boy' 时车窗里有他"""
    im = Image.new('RGBA', (62, 28)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([3, 11, 58, 22], 4, fill=body)
    d.polygon([(14, 11), (20, 3), (41, 3), (48, 11)], fill=body)
    d.rectangle([3, 19, 58, 22], fill=body_s)
    d.rectangle([3, 15, 58, 15], fill=body_s)
    d.polygon([(17, 11), (22, 5), (30, 5), (30, 11)], fill=glass)
    d.polygon([(32, 11), (32, 5), (40, 5), (45, 11)], fill=glass)
    d.line([(22, 6), (19, 10)], fill=lerpc(glass, (255, 255, 255), 0.45))
    d.line([(34, 6), (34, 7)], fill=lerpc(glass, (255, 255, 255), 0.45))
    if driver:
        hc = pix.LOOK[(driver, 'young')]['hair']
        d.rectangle([35, 6, 39, 10], fill=hc); d.rectangle([38, 8, 40, 11], fill=SKIN)
        d.rectangle([34, 10, 39, 11], fill=pix.LOOK[(driver, 'young')]['top'])
    d.line([(31, 12), (31, 19)], fill=body_s)
    d.rectangle([35, 13, 37, 13], fill=body_s); d.rectangle([22, 13, 24, 13], fill=body_s)
    d.rectangle([56, 12, 58, 14], fill=(255, 250, 220) if lights else (210, 206, 190))
    d.rectangle([3, 12, 5, 14], fill=(255, 70, 70) if (brake or lights) else (150, 50, 56))
    d.rectangle([56, 16, 58, 17], fill=AMB_L if sig else (170, 110, 50))
    d.rectangle([3, 16, 4, 17], fill=AMB_L if sig else (170, 110, 50))
    d.rectangle([26, 12, 27, 13], fill=AMB_L if sig else (190, 130, 60))         # 侧转向灯
    for wx in (15, 47):
        d.pieslice([wx - 7, 14, wx + 7, 28], 180, 360, fill=(36, 32, 44))
        _wheel(d, wx, 22, 5, ph / 4)
    return outline(im, OUT)


def car(img, x, y, sig=0.0, ph=0, s=1, flip=False, lights=True, brake=False, driver='boy', beams=True, body=CAR, body_s=CAR_S):
    """侧面小车：x 为车身中线，y 为轮胎着地处。flip=True 时车头朝左。sig 是转向灯亮度"""
    im = car_side(int(sig > 0.5), int(ph) % 4, lights, brake, body, body_s, driver=driver)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if s != 1: im = im.resize((im.width * s, im.height * s), Image.NEAREST)
    fx = (x + 27 * s) if not flip else (x - 27 * s)
    rx = (x - 28 * s) if not flip else (x + 28 * s)
    if lights and beams:
        dirn = -1 if flip else 1
        tfill(img, 'polygon', [(fx, y - 13 * s), (fx, y - 11 * s), (fx + dirn * 90 * s, y + 2 * s), (fx + dirn * 90 * s, y - 22 * s)],
              (255, 244, 200), 0.18)
        glow(img, fx, y - 13 * s, 10 * s, (255, 244, 210), 0.45)
    paste(img, im, x, y + 2 * s, 1, 'cb')
    if sig > 0.05:
        glow(img, fx, y - 10 * s, 9 * s, AMB, 0.6 * sig)
        glow(img, rx, y - 10 * s, 9 * s, AMB, 0.6 * sig)
        glow(img, x - 2 * s if not flip else x + 2 * s, y - 14 * s, 5 * s, AMB, 0.4 * sig)


@lru_cache(None)
def car_top(sig_l=0, sig_r=0, brake=False, body=CAR, body_s=CAR_S, glass=(44, 64, 104)):
    """俯视的小车，车头朝上，20×34"""
    im = Image.new('RGBA', (20, 34)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([2, 1, 17, 32], 4, fill=body)
    d.rectangle([3, 26, 16, 31], fill=body_s)
    d.polygon([(4, 9), (15, 9), (14, 13), (5, 13)], fill=glass)
    d.rectangle([5, 14, 14, 22], fill=lerpc(body, (255, 255, 255), 0.3))
    d.polygon([(5, 23), (14, 23), (15, 26), (4, 26)], fill=glass)
    d.line([(5, 10), (7, 10)], fill=lerpc(glass, (255, 255, 255), 0.5))
    d.point([(1, 12), (18, 12)], fill=body_s)
    d.rectangle([3, 1, 5, 2], fill=(255, 252, 220)); d.rectangle([14, 1, 16, 2], fill=(255, 252, 220))
    tl = (255, 60, 60) if brake else (190, 50, 60)
    d.rectangle([3, 31, 5, 32], fill=tl); d.rectangle([14, 31, 16, 32], fill=tl)
    off = (160, 104, 48)
    d.rectangle([2, 3, 2, 5], fill=AMB_L if sig_l else off); d.rectangle([2, 28, 2, 30], fill=AMB_L if sig_l else off)
    d.rectangle([17, 3, 17, 5], fill=AMB_L if sig_r else off); d.rectangle([17, 28, 17, 30], fill=AMB_L if sig_r else off)
    return outline(im, OUT)


def car_top_at(img, x, y, ang, s=2, sig_l=0.0, sig_r=0.0, brake=False, beams=True, body=CAR, body_s=CAR_S):
    """俯视小车，中心 (x, y)，ang 是车头方向（度，0=朝上，90=朝右）"""
    rad = math.radians(ang)
    fx, fy = math.sin(rad), -math.cos(rad)          # 车头方向
    rx_, ry_ = math.cos(rad), math.sin(rad)          # 车的右侧方向
    if beams:
        L = 70 * s / 2
        p0 = (x + fx * 16 * s - rx_ * 6 * s, y + fy * 16 * s - ry_ * 6 * s)
        p1 = (x + fx * 16 * s + rx_ * 6 * s, y + fy * 16 * s + ry_ * 6 * s)
        p2 = (p1[0] + fx * L + rx_ * 22 * s, p1[1] + fy * L + ry_ * 22 * s)
        p3 = (p0[0] + fx * L - rx_ * 22 * s, p0[1] + fy * L - ry_ * 22 * s)
        tfill(img, 'polygon', [p0, p1, p2, p3], (255, 236, 180), 0.12)
    im = car_top(int(sig_l > 0.5), int(sig_r > 0.5), brake, body, body_s)
    if s != 1: im = im.resize((im.width * s, im.height * s), Image.NEAREST)
    im = im.rotate(-ang, resample=Image.NEAREST, expand=True)
    paste(img, im, x, y, 1, 'cc')
    for side, a in ((-1, sig_l), (1, sig_r)):
        if a > 0.05:
            for k in (-1, 1):
                gx = x + rx_ * side * 8 * s + fx * k * 13 * s; gy = y + ry_ * side * 8 * s + fy * k * 13 * s
                glow(img, gx, gy, 8 * s, AMB, 0.65 * a)
    if brake:
        for side in (-1, 1):
            glow(img, x + rx_ * side * 5 * s - fx * 16 * s, y + ry_ * side * 5 * s - fy * 16 * s, 7 * s, (255, 50, 50), 0.4)


@lru_cache(None)
def car_rear_img(sig_l=0, brake=True, body=CAR, body_s=CAR_S):
    """车尾，50×30，车轮底边在 y=29"""
    im = Image.new('RGBA', (50, 30)); d = ImageDraw.Draw(im)
    d.rectangle([5, 25, 11, 29], fill=(30, 28, 38)); d.rectangle([38, 25, 44, 29], fill=(30, 28, 38))
    d.polygon([(11, 2), (38, 2), (43, 11), (6, 11)], fill=body)
    d.polygon([(13, 4), (36, 4), (40, 11), (9, 11)], fill=(44, 64, 104))
    d.line([(14, 5), (18, 5)], fill=(110, 140, 180))
    d.rounded_rectangle([2, 10, 47, 26], 3, fill=body)
    d.rectangle([2, 22, 47, 26], fill=body_s)
    d.rectangle([2, 23, 47, 23], fill=lerpc(body_s, (0, 0, 0), 0.25))
    tl = (255, 64, 64) if brake else (186, 46, 56)
    d.rectangle([3, 13, 10, 17], fill=tl); d.rectangle([39, 13, 46, 17], fill=tl)
    d.rectangle([4, 14, 6, 14], fill=(255, 170, 170) if brake else (220, 90, 100))
    d.rectangle([3, 18, 10, 19], fill=AMB_L if sig_l else (150, 96, 46))
    d.rectangle([39, 18, 46, 19], fill=(150, 96, 46))
    d.rectangle([18, 15, 31, 20], fill=(250, 248, 236)); d.rectangle([19, 16, 30, 19], fill=(60, 70, 120))
    for i, x in enumerate(range(20, 30, 2)): d.point((x, 17 + i % 2), fill=(250, 248, 236))
    d.rectangle([40, 26, 42, 27], fill=(80, 80, 90))
    return outline(im, OUT)


def car_rear(img, x, y, s, sig_l=0.0, brake=True, tilt=0):
    """车尾：x 为中线，y 为着地处"""
    im = car_rear_img(int(sig_l > 0.5), brake)
    im = im.resize((im.width * s, im.height * s), Image.NEAREST)
    if tilt: im = im.rotate(tilt, resample=Image.NEAREST, expand=True)
    paste(img, im, x, y, 1, 'cb')
    if brake:
        for gx in (x - 18 * s, x + 18 * s): glow(img, gx, y - 14 * s, 9 * s, (255, 50, 60), 0.45)
    if sig_l > 0.05:
        glow(img, x - 18 * s, y - 11 * s, 12 * s, AMB, 0.75 * sig_l)


# ---------------------------------------------------------------- 马路、倒影、雨
def reflect(img, y0, h, t, tint=(14, 12, 40), a=0.5, amp=2.0, src_h=None):
    """湿地面：把 y0 以上的画面倒过来贴到下面，每行左右抖一点，再压一层夜色"""
    src_h = src_h or h
    arr = np.asarray(img)
    top = arr[max(0, y0 - src_h):y0][::-1]
    n = min(h, len(top), H - y0)
    if n <= 0: return
    out = top[:n].copy()
    for r in range(n):
        sh = int(round(amp * math.sin(t * 3 + r * 0.7) * (0.3 + r / n)))
        if sh: out[r] = np.roll(out[r], sh, axis=0)
    under = arr[y0:y0 + n].astype(float)
    k = np.linspace(0.55, 0.15, n)[:, None, None] * a / 0.5
    al = np.clip(np.floor(k * 6 + pix.bayer(n, W, 0, y0)[..., None]) / 6, 0, 1)
    mix = under * (1 - al) + (out.astype(float) * 0.75 + np.array(tint) * 0.25) * al
    img.paste(Image.fromarray(mix.round().astype(np.uint8)), (0, y0))


def splashes(d, t, y0, y1, n, col=(150, 170, 230), seed=0):
    """雨点打在地上的小水花"""
    for i in range(n):
        r = rng(i * 13 + seed)
        per = 0.5 + r.random() * 0.4
        k = ((t + r.random() * per) % per) / per
        if k > 0.45: continue
        x = r.uniform(0, W); y = r.uniform(y0, y1)
        s = 1 + int(k * 6)
        d.point([(x - s, y), (x + s, y)], fill=col)
        if k < 0.2: d.point((x, y - 1), fill=col)


def drops_on_glass(img, d, t, box, n=40, seed=0, col=(180, 200, 255)):
    """窗玻璃上的雨珠，慢慢往下滑"""
    x0, y0, x1, y1 = box
    for i in range(n):
        r = rng(i * 7 + seed)
        sp = r.uniform(4, 30)
        x = r.uniform(x0, x1); y = y0 + (r.uniform(0, y1 - y0) + t * sp) % (y1 - y0)
        d.point((x, y), fill=col)
        if sp > 18: d.line([(x, y - 3), (x, y - 1)], fill=lerpc(col, (40, 40, 80), 0.6))
        if i % 3 == 0: d.point((x + 1, y), fill=lerpc(col, (255, 255, 255), 0.5))


def night_city(img, d, T, base=200, off=0.0, sky_stops=NIGHT, far=(36, 26, 70), mid=(24, 18, 50), near=(16, 12, 34), star_n=120,
               moon_xy=None, win=(255, 214, 120), frac=0.3):
    sky(img, sky_stops, 0, base + 2)
    stars(d, T, base - 40, 0.9, star_n)
    if moon_xy: pix.moon(d, moon_xy[0], moon_xy[1], 10); glow(img, moon_xy[0], moon_xy[1], 30, (250, 240, 200), 0.25)
    city(img, d, base - 12, 3, off * 0.3, far, lerpc(far, win, 0.5), 40, 100, 0.25, T, 10, 22)
    city(img, d, base - 4, 7, off * 0.6, mid, win, 30, 80, frac, T)
    city(img, d, base, 13, off, near, lerpc(win, (255, 255, 255), 0.2), 18, 54, frac * 0.8, T, 18, 40)


def road_side(img, d, y, T, off=0.0, col=(40, 38, 56), line=(220, 216, 200), curb=(90, 86, 104)):
    """侧面的马路：路沿、路面和虚线"""
    d.rectangle([0, y - 3, W, y - 1], fill=curb)
    d.rectangle([0, y, W, H], fill=col)
    for x in range(int(-(off % 40)), W, 40):
        d.rectangle([x, y + 18, x + 20, y + 19], fill=line)


# ---------------------------------------------------------------- 手机和聊天界面
def phone(img, d, cx, cy, w, h, screen=None, body=(34, 32, 48), on=1.0, rot=0):
    """竖着的手机，中心 (cx, cy)。screen(im, d2, w, h) 往屏幕上画内容"""
    im = Image.new('RGBA', (w + 2, h + 2)); dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([1, 1, w, h], max(3, w // 10), fill=body, outline=OUT)
    dd.rectangle([w // 2 - 4, 4, w // 2 + 4, 4], fill=(70, 70, 90))
    sw, sh = w - 6, h - 16
    if screen and on > 0:
        sc = Image.new('RGB', (sw, sh), (20, 20, 30)); sd = ImageDraw.Draw(sc); sd.fontmode = '1'
        screen(sc, sd, sw, sh)
        if on < 1:
            a = np.asarray(sc, float) * on + np.array((10, 10, 16)) * (1 - on)
            sc = Image.fromarray(a.astype(np.uint8))
        im.paste(sc, (4, 9))
    else:
        dd.rectangle([4, 9, 4 + sw - 1, 9 + sh - 1], fill=(16, 16, 24))
    if rot: im = im.rotate(rot, resample=Image.NEAREST, expand=True)
    if screen and on > 0: glow(img, cx, cy, max(w, h) * 0.9, (150, 200, 255), 0.18 * on)
    paste(img, im, cx, cy, 1, 'cc')
    return (cx - w / 2 + 3, cy - h / 2 + 8, sw, sh)


def scribble(d, x, y, w, col, seed=0):
    """聊天泡泡里的“字”：一串高低不平的小横道"""
    r = rng(seed); xx = x
    while xx < x + w - 1:
        L = r.randint(2, 5)
        L = min(L, int(x + w - xx))
        d.line([(xx, y), (xx + L - 1, y)], fill=col)
        if r.random() < 0.4: d.point((xx + r.randrange(max(1, L)), y - 1), fill=col)
        xx += L + 1


def chat_bubble(d, x, y, w, h, mine, seed=0, f=1.0):
    if f <= 0: return
    w = max(4, int(w * eback(f)))
    bg = AMB if mine else (236, 236, 244)
    fg = (90, 50, 20) if mine else (90, 90, 110)
    x0 = x - w if mine else x
    d.rounded_rectangle([x0, y, x0 + w, y + h], 3, fill=bg)
    if mine: d.polygon([(x, y + h - 4), (x + 3, y + h), (x - 2, y + h)], fill=bg)
    else: d.polygon([(x, y + h - 4), (x - 3, y + h), (x + 2, y + h)], fill=bg)
    if f >= 1:
        for k in range(max(1, (h - 2) // 5)):
            scribble(d, x0 + 3, y + 4 + k * 5, w - 6, fg, seed + k)


@lru_cache(None)
def head_icon(who, expr='smile', s=1, age='young'):
    im = pix.char_img(who, age, 'front', 'stand', 0, expr)
    return im.crop((CXH - 8, 0, CXH + 8, 18)).resize((16 * s, 18 * s), Image.NEAREST)


CXH = pix.CX


def chat_header(sd, w, avatar_img=None, sc=None, col=(40, 40, 58)):
    sd.rectangle([0, 0, w, 15], fill=col)
    sd.polygon([(4, 7), (8, 3), (8, 11)], fill=(220, 220, 236))
    if avatar_img is not None and sc is not None:
        sd.ellipse([13, 1, 26, 14], fill=TEAL_L)
        sc.paste(avatar_img.crop((0, 0, 16, 14)).resize((12, 11), Image.NEAREST), (14, 3), avatar_img.crop((0, 0, 16, 14)).resize((12, 11), Image.NEAREST))
    sd.rectangle([30, 5, 30 + 16, 6], fill=(220, 220, 236)); sd.rectangle([30, 9, 30 + 10, 10], fill=(140, 140, 160))


# ---------------------------------------------------------------- 文字和片名
@lru_cache(None)
def big_glyph(ch, scale=3, top=AMB_L, bot=AMB, line=(170, 70, 20), out=(26, 12, 34), font=None):
    font = font or FONT
    w = int(font.getlength(ch)) + 8; h = font.size + 8
    m = Image.new('L', (w, h)); md = ImageDraw.Draw(m); md.fontmode = '1'
    md.text((4, 3), ch, font=font, fill=255)
    mk = np.array(m) > 0
    a = np.zeros((h, w, 4), np.uint8)
    for y in range(h): a[y, :, :3] = lerpc(top, bot, (y - 4) / (font.size - 1))
    a[..., 3] = mk * 255
    im = outline(outline(Image.fromarray(a), line), out)
    sh = Image.new('RGBA', (w + 1, h + 1))
    shadow = np.array(im); shadow[shadow[..., 3] > 0, :3] = out
    sh.paste(Image.fromarray(shadow), (1, 1)); sh.alpha_composite(im)
    return sh.resize((sh.width * scale, sh.height * scale), Image.NEAREST)


def big_text(img, s, cx, cy, scale, col=AMB, top=None, alpha=1.0, gap=0):
    top = top or lerpc(col, (255, 255, 255), 0.5)
    gl = [big_glyph(c, scale, top, col, lerpc(col, (0, 0, 0), 0.45)) for c in s]
    adv = [FONT.getlength(c) * scale + gap for c in s]
    x = cx - sum(adv) / 2 - 4 * scale
    for g, a in zip(gl, adv):
        paste(img, g, x, cy - g.height / 2, alpha, 'lt')
        x += a


@lru_cache(None)
def glyph_pixels(s, scale):
    """片名每个像素点的位置（用来做粒子汇聚），按字分组"""
    out = []
    x = 0
    for ch in s:
        m = Image.new('L', (int(FONT.getlength(ch)) + 4, FONT.size + 4)); md = ImageDraw.Draw(m); md.fontmode = '1'
        md.text((2, 1), ch, font=FONT, fill=255)
        ys, xs = np.nonzero(np.array(m))
        out.append([(x + (px - 2) * scale, (py - 1) * scale) for px, py in zip(xs, ys)])
        x += FONT.getlength(ch) * scale
    return out, x


def neon_rect(img, d, box, col, a=1.0, w=1):
    if a <= 0: return
    x0, y0, x1, y1 = box
    glow(img, (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 + 10, col, 0.2 * a, (y1 - y0) / 2 + 10)
    d.rectangle(box, outline=lerpc((40, 30, 50), col, a), width=w)
    d.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], outline=lerpc((40, 30, 50), lerpc(col, (255, 255, 255), 0.5), a))


def counter(img, x, y, n, col=AMB, digits=4, scale=2, prefix='×'):
    s = prefix + str(int(n)).rjust(digits, '0') if digits else prefix + str(int(n))
    text(img, s, x, y, col, OUT, scale=scale)


# ---------------------------------------------------------------- 拍立得
def polaroid(img, d, cx, cy, photo, f=1.0, alpha=1.0, rot=0, frame=CREAM):
    """拍立得：photo 是 RGB 图，f 从 0 到 1 显影"""
    if alpha <= 0: return
    pw, ph = photo.size
    im = Image.new('RGBA', (pw + 8, ph + 16), frame + (255,))
    p = photo
    if f < 1:
        a = np.asarray(p, float); g = a @ np.array([0.3, 0.59, 0.11])
        dev = np.clip(f * 1.4, 0, 1)
        a = (a * dev + (g[..., None] * 0.3 + 40) * (1 - dev)) * (0.4 + 0.6 * dev)
        p = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    im.paste(p, (4, 4))
    im = outline(im, OUT)
    if rot: im = im.rotate(rot, resample=Image.NEAREST, expand=True)
    paste(img, im, cx, cy, alpha, 'cc')


def shrink(im, w, h):
    """把整帧缩成小图（拍立得、电视里的画面）：按块取平均，保留像素感"""
    return im.resize((w, h), Image.BOX)


# ---------------------------------------------------------------- 手
def hand_blob(d, x, y, s, col=SKIN, sh=SKIN_S, fingers=4, flip=False, thumb=True):
    """手背朝外的大手（特写用）：(x, y) 是手腕中心，手指朝上"""
    k = -1 if flip else 1
    d.rounded_rectangle([x - 6 * s, y - 12 * s, x + 6 * s, y], 3 * s, fill=col)
    for i in range(fingers):
        fx = x - 5 * s + i * 3 * s + (0 if i else 0)
        fl = [7, 9, 8, 6][i] * s
        d.rounded_rectangle([fx, y - 12 * s - fl, fx + 2 * s, y - 10 * s], s, fill=col)
        d.line([(fx + 2 * s, y - 12 * s - fl + s), (fx + 2 * s, y - 11 * s)], fill=sh)
    if thumb:
        tx = x + k * 6 * s
        d.polygon([(tx, y - 4 * s), (tx + k * 5 * s, y - 9 * s), (tx + k * 6 * s, y - 7 * s), (tx + k * 1 * s, y - 1 * s)], fill=col)
    d.line([(x - 6 * s, y - 2 * s), (x + 6 * s, y - 2 * s)], fill=sh)


# ---------------------------------------------------------------- 通用小效果（泡泡、震屏、迸射、光斑）
def shake(img, k, amp_, dur):
    if not 0 <= k < dur: return
    a = amp_ * (1 - k / dur)
    dx, dy = round(a * math.sin(k * 97)), round(a * math.cos(k * 71))
    if dx or dy:
        src = img.copy(); img.paste((8, 6, 20), (0, 0, W, H)); img.paste(src, (dx, dy))


def bubble(img, d, x, y, w, h, f, thought=False, tail=(0, 1), col=(255, 255, 255), edge=OUT):
    """对话泡泡。(x, y) 是尾巴尖，f 从 0 到 1 弹出来。返回泡泡内容区域的中心"""
    if f <= 0: return None
    s = eback(f)
    bw, bh = max(2, w * s), max(2, h * s)
    cx = x + tail[0] * 6 * s; cy = y - 8 * s - bh / 2
    box = [cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2]
    if thought:
        for k, (dx, dy, r) in enumerate([(0, -3, 1.5), (tail[0] * 3, -7, 2.5)]):
            rr = r * s
            d.ellipse([x + dx * s - rr - 1, y + dy * s - rr - 1, x + dx * s + rr + 1, y + dy * s + rr + 1], fill=edge)
            d.ellipse([x + dx * s - rr, y + dy * s - rr, x + dx * s + rr, y + dy * s + rr], fill=col)
        d.rounded_rectangle([box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1], radius=int(min(bw, bh) / 2), fill=edge)
        d.rounded_rectangle(box, radius=int(min(bw, bh) / 2 - 1), fill=col)
    else:
        tp = [(x, y), (cx - 3 * s + tail[0] * 2, cy + bh / 2 - 1), (cx + 3 * s + tail[0] * 2, cy + bh / 2 - 1)]
        d.rounded_rectangle([box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1], radius=4, fill=edge)
        d.polygon([(x, y + 1), (tp[1][0] - 1, tp[1][1]), (tp[2][0] + 1, tp[2][1])], fill=edge)
        d.rounded_rectangle(box, radius=3, fill=col)
        d.polygon(tp, fill=col)
    return (cx, cy) if f >= 0.6 else None


@lru_cache(None)
def head_img(who, age='young', expr='smile', s=1, view='front'):
    im = pix.char_img(who, age, view, 'stand', 0, expr)
    return im.crop((pix.CX - 8, pix.FY - 31, pix.CX + 8, pix.FY - 15)).resize((16 * s, 16 * s), Image.NEAREST)


_RB = rng(5)
BURST = [(_RB.uniform(0, 2 * math.pi), _RB.uniform(60, 180), i % 4, [AMB, TEAL, (255, 255, 255), PINK][i % 4]) for i in range(56)]


def burst(img, d, k, cx, cy, parts=BURST, life=1.2, scale=1.0):
    if not 0 <= k < life: return
    u = k / life
    for ang, sp, kind, col in parts:
        dist = (6 + sp * eout(u)) * scale
        x = cx + math.cos(ang) * dist; y = cy + math.sin(ang) * dist * 0.8 + 20 * u * u * scale
        c = lerpc(col, (30, 20, 50), u)
        if kind == 0: pix.put(img, 'heart', x, y, 1, tint=col, alpha=1 - u)
        elif kind == 1: pix.twinkle(d, int(x), int(y), 1 - u * 0.8, c, 3)
        else: d.rectangle([x, y, x + 1, y + 1], fill=c)


BOKEH_COLS = [AMB, PINK, TEAL, (140, 120, 255), (255, 220, 160)]


def bokeh(img, T, n=14, cols=BOKEH_COLS, seed=0, a=0.3, rmin=8, rmax=22, drift=6, box=(0, 0, W, H)):
    """虚焦的光斑，慢慢漂"""
    x0, y0, x1, y1 = box
    for i in range(n):
        r = rng(i * 17 + seed)
        x = x0 + (r.uniform(0, x1 - x0) + T * drift * r.uniform(-1, 1)) % (x1 - x0)
        y = y0 + r.uniform(0, y1 - y0) + 4 * math.sin(T * 0.7 + i)
        rad = r.uniform(rmin, rmax)
        glow(img, x, y, rad, cols[i % len(cols)], a * (0.6 + 0.4 * math.sin(T * 1.3 + i * 2)), power=0.7)


def beats_in(t0, t1):
    b = pix.AUDIO['beats']
    return [x for x in b if t0 <= x < t1]


def last_beat(T):
    b = pix.AUDIO['beats']
    i = int(np.searchsorted(b, T, 'right')) - 1
    return b[i] if i >= 0 else -9.0


SNAP = None    # render.py 填入：SNAP(T) 返回全片 T 秒处的画面（不含字幕）
