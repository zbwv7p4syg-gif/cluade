"""永不失联的爱 · 这首歌自己的道具：信号格、手机和聊天气泡、传声筒和发光的线、心电图、纸船、星星鲸鱼、卫星、
小星球、天台、电话亭、日历、形状各异的云、牵着的手、地球、山。

"信号"是这首歌的主线：开头手机找不到信号，副歌里一根传声筒的线把两个人连起来，线上跑着一颗颗小心；
最后信号满格，"已连接"。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
from pix import (W, H, FONT, FONT_S, OUT, SKIN, SKIN_S, clamp, lerp, lerpc, ease, eout, glow, tfill, blend_box, outline, rng, text)
from props import dpaste, CREAM, GOLD, GOLD_L, PINK, PINK_L, CYAN

SIG = (120, 220, 255)            # 信号的青色
SIG_L = (210, 246, 255)
HEART, HEART_L, HEART_D = (255, 96, 128), (255, 176, 196), (176, 40, 76)
SKY_B = (124, 186, 236)          # 她的天蓝
ORANGE = (240, 132, 74)          # 他的暖橙


# ---------------------------------------------------------------- 小心（字幕进度、线上的脉冲）
MINI_ROWS = [".H.H.", "HLHHH", "HHHHH", ".HHH.", "..H.."]
_MINI = {}


def mini_heart(img, x, y, T, alpha=1.0, col=HEART):
    """5×5 的小心，随拍子鼓一下"""
    big = pix.pulse(T, 0.2) > 0.4
    key = (big, col)
    if key not in _MINI:
        im = Image.new('RGBA', (5, 5)); px = im.load()
        for yy, row in enumerate(MINI_ROWS):
            for xx, ch in enumerate(row):
                if ch != '.': px[xx, yy] = (lerpc(col, (255, 255, 255), 0.5) if ch == 'L' else col) + (255,)
        im = outline(im, (70, 16, 40))
        if big: im = im.resize((14, 14), Image.NEAREST)
        _MINI[key] = im
    im = _MINI[key]
    dpaste(img, im, x - im.width / 2, y - im.height / 2, alpha)


@lru_cache(None)
def heart_spr(s=1, col=HEART, out=(70, 16, 40)):
    rows = [".HH.HH.", "HLHHHHH", "HHHHHHH", ".HHHHH.", "..HHH..", "...H..."]
    im = Image.new('RGBA', (7, 6)); px = im.load()
    for yy, row in enumerate(rows):
        for xx, ch in enumerate(row):
            if ch != '.': px[xx, yy] = (lerpc(col, (255, 255, 255), 0.55) if ch == 'L' else col) + (255,)
    if out: im = outline(im, out)
    return im.resize((im.width * s, im.height * s), Image.NEAREST) if s != 1 else im


def heart_at(img, x, y, s=1, col=HEART, alpha=1.0, out=(70, 16, 40)):
    im = heart_spr(s, col, out)
    dpaste(img, im, x - im.width / 2, y - im.height / 2, alpha)


# ---------------------------------------------------------------- 信号格、手机、聊天气泡
def bars(d, x, y, level, s=1, on=SIG, off=(70, 76, 100)):
    """四格信号：(x, y) 是左下角，level 0..4（可以是小数，最后一格按比例闪）"""
    for k in range(4):
        h = (k + 1) * 2 * s
        c = on if level >= k + 1 else off
        d.rectangle([x + k * 3 * s, y - h, x + k * 3 * s + 2 * s - 1, y], fill=c)


def wifi(img, d, x, y, s, f, col=SIG, a=1.0):
    """从 (x, y) 往上发出去的三道弧，f 是时间相位"""
    for k in range(3):
        u = (f + k / 3) % 1
        r = (4 + u * 16) * s
        c = lerpc(col, (0, 0, 0), u * 0.7)
        if a >= 1 and u < 0.85: d.arc([x - r, y - r, x + r, y + r], 225, 315, fill=c, width=max(1, int(s)))


def phone(img, d, x, y, w, h, scr=(16, 20, 40), body=(40, 40, 54), rim=(110, 110, 130), level=4, T=0.0, notch=True, light=True):
    """竖着的手机，(x, y) 是左上角。返回屏幕矩形 (x0, y0, x1, y1)"""
    d.rounded_rectangle([x - 1, y - 1, x + w + 1, y + h + 1], 5, fill=OUT)
    d.rounded_rectangle([x, y, x + w, y + h], 5, fill=body)
    d.rounded_rectangle([x, y, x + w, y + h], 5, outline=rim)
    sx0, sy0, sx1, sy1 = x + 3, y + 4, x + w - 3, y + h - 4
    d.rectangle([sx0, sy0, sx1, sy1], fill=scr)
    if notch: d.rectangle([x + w / 2 - 5, y + 1, x + w / 2 + 5, y + 2], fill=(20, 20, 28))
    if light: glow(img, (sx0 + sx1) / 2, (sy0 + sy1) / 2, max(w, h) * 0.9, lerpc(scr, (200, 230, 255), 0.6), 0.18)
    return (sx0, sy0, sx1, sy1)


def status(d, box, level, T, col=(230, 236, 255), clock='23:10'):
    sx0, sy0, sx1, sy1 = box
    pix_text(d, clock, sx0 + 2, sy0 + 1, col)
    bars(d, sx1 - 13, sy0 + 7, level, 1, on=col, off=(70, 76, 100))


@lru_cache(None)
def small_text_img(s, col, font_size=12):
    font = FONT_S if font_size == 12 else pix.FONT
    w = int(font.getlength(s)) + 2; h = font.size + 3
    im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im); d.fontmode = '1'
    d.text((1, 0), s, font=font, fill=col)
    return im


def pix_text(d, s, x, y, col, size=12):
    """小号的点阵字，没有描边（贴在手机屏、牌子上）"""
    im = small_text_img(s, (255, 255, 255), size)
    d.bitmap((int(x), int(y)), im.getchannel('A'), fill=tuple(col))


def bubble(img, d, x, y, s, mine=False, f=1.0, col=None, tcol=None, size=12, maxw=None):
    """聊天气泡：mine=True 靠右、绿色；(x, y) 是气泡尾巴那一侧的上角。f 0..1 弹出。返回 (宽, 高)"""
    if f <= 0: return 0, 0
    font = FONT_S if size == 12 else pix.FONT
    tw = font.getlength(s)
    bw, bh = int(tw) + 10, font.size + 7
    col = col or ((150, 236, 140) if mine else (250, 250, 252))
    tcol = tcol or (30, 30, 40)
    k = pix.eback(f)
    w_, h_ = max(4, bw * k), max(3, bh * k)
    x0 = x - w_ if mine else x
    y0 = y + (bh - h_) / 2
    d.rounded_rectangle([x0 - 1, y0 - 1, x0 + w_ + 1, y0 + h_ + 1], 5, fill=OUT)
    d.rounded_rectangle([x0, y0, x0 + w_, y0 + h_], 5, fill=col)
    tx = x0 + w_ if mine else x0
    d.polygon([(tx, y0 + h_ - 6), (tx + (5 if mine else -5), y0 + h_ + 1), (tx + (-2 if mine else 2), y0 + h_ - 2)], fill=col)
    if f > 0.6: pix_text(d, s, x0 + 5, y0 + 3, tcol, size)
    return bw, bh


def typing(d, x, y, T, col=(250, 250, 252), dot=(140, 140, 160)):
    """对方正在输入：灰气泡里三个跳动的点"""
    d.rounded_rectangle([x - 1, y - 1, x + 25, y + 13], 5, fill=OUT)
    d.rounded_rectangle([x, y, x + 24, y + 12], 5, fill=col)
    for k in range(3):
        b = 1 if int(T * 6 - k) % 3 == 0 else 0
        d.rectangle([x + 6 + k * 5, y + 5 - b, x + 7 + k * 5, y + 6 - b], fill=dot)


# ---------------------------------------------------------------- 传声筒和线
def can(d, x, y, s=1, flip=False, col=(214, 214, 224), col_d=(150, 150, 170), band=HEART):
    """侧放的罐头传声筒，(x, y) 是开口中心，罐身朝右（flip 朝左）。返回拉线的点（罐底中心）"""
    sg = -1 if flip else 1
    L, R = 12 * s, 6 * s
    x1 = x + sg * L
    d.rectangle([min(x, x1) - 1, y - R - 1, max(x, x1) + 1, y + R + 1], fill=OUT)
    d.rectangle([min(x, x1), y - R, max(x, x1), y + R], fill=col)
    d.rectangle([min(x, x1), y + R - 2 * s, max(x, x1), y + R], fill=col_d)
    d.rectangle([min(x, x1) + 3 * s, y - R, max(x, x1) - 3 * s, y - R + 2 * s], fill=band)
    d.ellipse([x - 3 * s - 1, y - R - 1, x + 3 * s + 1, y + R + 1], fill=OUT)
    d.ellipse([x - 3 * s, y - R, x + 3 * s, y + R], fill=lerpc(col_d, (40, 40, 60), 0.5))
    return (x1, y)


def string_pts(p0, p1, sag, n=40, T=0.0, wob=0.0):
    (x0, y0), (x1, y1) = p0, p1
    pts = []
    for i in range(n + 1):
        u = i / n
        pts.append((lerp(x0, x1, u), lerp(y0, y1, u) + sag * 4 * u * (1 - u) + wob * math.sin(u * math.pi) * math.sin(T * 9 + u * 6)))
    return pts


def string(img, d, p0, p1, sag, T, col=(250, 236, 214), glow_a=0.0, pulses=(), wob=0.0, f=1.0):
    """两点之间的一根线：sag 下垂量；glow_a 让线发光；pulses 是 0..1 的位置列表，在那里放一颗小心。f 0..1 线从 p0 往 p1 画出来"""
    pts = string_pts(p0, p1, sag, 60, T, wob)
    m = max(2, int(len(pts) * clamp(f)))
    if glow_a > 0:
        for i in range(0, m, 6):
            glow(img, pts[i][0], pts[i][1], 7, SIG, 0.25 * glow_a)
    d.line(pts[:m], fill=col)
    for u in pulses:
        if 0 <= u <= f:
            i = int(u * 60)
            px, py = pts[i]
            glow(img, px, py, 12, HEART, 0.5)
            heart_at(img, px, py - 1, 1)
    return pts


# ---------------------------------------------------------------- 心电图
def ecg_y(x, beats_x, h=26, w=14):
    """心跳曲线在 x 处的偏移：每个 beats_x 位置一个 P-QRS-T 波形"""
    y = 0.0
    for bx in beats_x:
        u = (x - bx) / w
        if -1.5 < u < 2.5:
            if -1.2 < u < -0.7: y -= 3 * math.sin((u + 1.2) / 0.5 * math.pi)
            elif -0.3 < u < 0: y += h * 0.25 * (u + 0.3) / 0.3
            elif 0 <= u < 0.25: y -= h * (u / 0.25) - h * 0.25 * (1 - u / 0.25)
            elif 0.25 <= u < 0.55: y -= h * (1 - (u - 0.25) / 0.3) - h * 0.45 * (u - 0.25) / 0.3
            elif 0.55 <= u < 0.75: y += h * 0.45 * (1 - (u - 0.55) / 0.2)
            elif 1.2 < u < 2.0: y -= 5 * math.sin((u - 1.2) / 0.8 * math.pi)
    return y


# ---------------------------------------------------------------- 纸船、星星鲸鱼、卫星、小星球
def boat(d, x, y, s=1.0, rock=0.0, col=(250, 248, 240), sh=(200, 204, 220)):
    """纸船，(x, y) 是船底中点"""
    ca, sa = math.cos(rock), math.sin(rock)

    def P(u, v): return (x + (u * ca - v * sa) * s, y + (u * sa + v * ca) * s)
    hull = [P(-18, -7), P(18, -7), P(12, 0), P(-12, 0)]
    sail = [P(-8, -7), P(0, -22), P(8, -7)]
    sail2 = [P(0, -22), P(8, -7), P(4, -7)]
    d.polygon([(a + 1, b + 1) for a, b in hull], fill=OUT)
    d.polygon(sail, fill=col); d.polygon(sail2, fill=sh)
    d.line(sail + [sail[0]], fill=OUT)
    d.polygon(hull, fill=col)
    d.line(hull + [hull[0]], fill=OUT)
    d.line([P(-14, -4), P(14, -4)], fill=sh)


WHALE = [(-30, 0), (-22, -9), (-6, -13), (12, -11), (24, -5), (30, 2), (24, 8), (6, 11), (-12, 10), (-26, 6)]


def whale(img, d, x, y, s, T, alpha=1.0, col=(70, 120, 210), belly=(150, 200, 255), flip=False):
    """星星做的鲸鱼：半透明的身体、肚子上的条纹、身上撒着星点，尾巴上下摆"""
    sg = -1 if flip else 1
    tail = math.sin(T * 2.4) * 6
    body = [(x + sg * u * s, y + v * s) for u, v in WHALE]
    m = Image.new('L', (W, H)); md = ImageDraw.Draw(m)
    md.polygon(body, fill=int(255 * 0.55 * alpha))
    tx, ty = x - sg * 30 * s, y
    md.polygon([(tx, ty - 2 * s), (tx - sg * 12 * s, ty - (8 + tail) * s), (tx - sg * 8 * s, ty), (tx - sg * 12 * s, ty + (6 - tail) * s),
                (tx, ty + 3 * s)], fill=int(255 * 0.55 * alpha))
    a = np.asarray(m, float) / 255
    ys, xs = np.nonzero(a)
    if len(xs):
        box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
        blend_box(img, box, col, a[box[1]:box[3], box[0]:box[2]], levels=4)
    for k in range(4):
        yy = y + (3 + k * 2) * s
        d.line([(x - sg * (12 - k * 2) * s, yy), (x + sg * (18 - k * 3) * s, yy)], fill=lerpc(col, belly, 0.6))
    r = rng(int(s * 10) + 3)
    for i in range(int(22 * s)):
        u, v = r.uniform(-26, 26), r.uniform(-10, 6)
        px, py = x + sg * u * s, y + v * s
        b = 0.5 + 0.5 * math.sin(T * 3 + i)
        if b > 0.3: d.point((px, py), fill=lerpc(col, (255, 255, 240), b))
    ex, ey = x + sg * 20 * s, y - 3 * s
    d.rectangle([ex, ey, ex + max(1, s * 0.8), ey + max(1, s * 0.8)], fill=(255, 255, 255))
    glow(img, x, y, 40 * s, col, 0.15 * alpha)


def satellite(d, x, y, s=1.0, ang=0.0, body=(220, 220, 230), panel=(70, 110, 200), T=0.0):
    ca, sa = math.cos(ang), math.sin(ang)

    def P(u, v): return (x + (u * ca - v * sa) * s, y + (u * sa + v * ca) * s)
    for sg in (-1, 1):
        d.polygon([P(sg * 6, -4), P(sg * 22, -4), P(sg * 22, 4), P(sg * 6, 4)], fill=panel)
        for k in range(1, 4): d.line([P(sg * (6 + k * 4), -4), P(sg * (6 + k * 4), 4)], fill=lerpc(panel, (255, 255, 255), 0.3))
    d.polygon([P(-6, -6), P(6, -6), P(6, 6), P(-6, 6)], fill=body)
    d.polygon([P(-6, 4), P(6, 4), P(6, 6), P(-6, 6)], fill=lerpc(body, (0, 0, 0), 0.3))
    d.line([P(0, -6), P(0, -13)], fill=body)
    d.point(P(0, -14), fill=(255, 80, 80) if int(T * 3) % 2 else (120, 40, 40))


def planet(img, d, cx, cy, r, T, ground=(110, 190, 120), ground_d=(70, 140, 96), sea=(80, 140, 220), ring=None, spin=0.2):
    """小星球：圆形，表面有转动的色块，外面一圈光"""
    glow(img, cx, cy, r * 1.5, (160, 200, 255), 0.25)
    d.ellipse([cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1], fill=OUT)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=sea)
    yy, xx = np.mgrid[int(cy - r):int(cy + r) + 1, int(cx - r):int(cx + r) + 1]
    inside = (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
    lon = np.arcsin(np.clip((xx - cx) / np.maximum(1e-6, np.sqrt(np.maximum(1, r * r - (yy - cy) ** 2))), -1, 1)) + T * spin
    lat = (yy - cy) / r
    land = (np.sin(lon * 3 + lat * 2) + np.sin(lon * 5 - lat * 4 + 1)) > 0.4
    arr = np.asarray(img).copy()
    y0, x0 = int(cy - r), int(cx - r)
    sub = arr[max(0, y0):y0 + inside.shape[0], max(0, x0):x0 + inside.shape[1]]
    oy, ox = max(0, -y0), max(0, -x0)
    m = (inside & land)[oy:oy + sub.shape[0], ox:ox + sub.shape[1]]
    sh = (((xx - cx + r * 0.3) ** 2 + (yy - cy + r * 0.3) ** 2) > (r * 1.05) ** 2)[oy:oy + sub.shape[0], ox:ox + sub.shape[1]]
    sub[m] = ground
    sub[m & sh] = ground_d
    ins = inside[oy:oy + sub.shape[0], ox:ox + sub.shape[1]]
    sub[ins & ~m & sh] = lerpc(sea, (0, 0, 0), 0.3)
    img.paste(Image.fromarray(arr))
    if ring:
        d.arc([cx - r * 1.7, cy - r * 0.35, cx + r * 1.7, cy + r * 0.35], 0, 180, fill=ring, width=2)


# ---------------------------------------------------------------- 天台、电话亭、日历、路灯下的雪
def rooftop(d, x0, x1, top, col=(40, 40, 70), edge=(70, 70, 110), win=None, T=0.0, tank=True, seed=0):
    """楼顶：一截楼身、栏杆，可选水箱和天线"""
    if top - 30 > H: return
    d.rectangle([x0, top, x1, max(top, H)], fill=col)
    d.line([(x0, top), (x1, top)], fill=edge)
    for x in range(int(x0), int(x1), 6): d.line([(x, top - 6), (x, top)], fill=edge)
    d.line([(x0, top - 6), (x1, top - 6)], fill=edge)
    if tank:
        tx = x0 + (x1 - x0) * 0.7
        d.rectangle([tx - 10, top - 26, tx + 10, top - 10], fill=lerpc(col, edge, 0.5))
        d.rectangle([tx - 10, top - 26, tx + 10, top - 24], fill=edge)
        for lx in (tx - 8, tx + 7): d.line([(lx, top - 10), (lx, top)], fill=edge)
    if win:
        r = rng(seed)
        for wy in range(int(top) + 8, H, 9):
            for wx in range(int(x0) + 4, int(x1) - 4, 8):
                if r.random() < 0.45: d.rectangle([wx, wy, wx + 3, wy + 4], fill=win)


def booth(img, d, x, base, T, lit=1.0, col=(200, 60, 64), col_d=(140, 36, 44)):
    """电话亭，(x, base) 是底边中点，宽 30 高 70。返回玻璃内的矩形"""
    w, h = 30, 70
    x0 = x - w / 2
    d.rectangle([x0 - 1, base - h - 1, x0 + w + 1, base], fill=OUT)
    d.rectangle([x0, base - h, x0 + w, base], fill=col)
    d.rectangle([x0, base - h, x0 + w, base - h + 7], fill=col_d)
    if lit > 0: glow(img, x, base - h + 3, 14, (255, 240, 200), 0.3 * lit)
    d.rectangle([x0 + 6, base - h + 2, x0 + w - 6, base - h + 5], fill=lerpc((90, 80, 80), (255, 246, 210), lit))
    g = (x0 + 3, base - h + 10, x0 + w - 3, base - 6)
    d.rectangle(g, fill=lerpc((40, 50, 70), (150, 170, 190), 0.4 + 0.3 * lit))
    for k in range(1, 4):
        yy = g[1] + (g[3] - g[1]) * k / 4
        d.line([(g[0], yy), (g[2], yy)], fill=col)
    if lit > 0: glow(img, x, base - h / 2, 30, (255, 220, 160), 0.25 * lit)
    return g


def calendar(img, d, x, y, day, month='', flip=0.0, w=56, h=64):
    """撕页日历，(x, y) 左上角；flip 0..1 把当前这页往上翻走"""
    d.rectangle([x - 1, y - 1, x + w + 1, y + h + 1], fill=OUT)
    d.rectangle([x, y, x + w, y + h], fill=(250, 248, 240))
    d.rectangle([x, y, x + w, y + 12], fill=(220, 70, 80))
    for k in range(4): d.rectangle([x + 8 + k * 12, y - 3, x + 10 + k * 12, y + 2], fill=(60, 60, 70))
    if month: pix_text(d, month, x + w / 2 - FONT_S.getlength(month) / 2, y, (255, 255, 255))
    if flip > 0:
        fh = (h - 12) * (1 - flip)
        d.polygon([(x, y + 12), (x + w, y + 12), (x + w, y + 12 + fh), (x, y + 12 + fh * 0.8)], fill=(236, 230, 220))
        d.line([(x, y + 12 + fh * 0.8), (x + w, y + 12 + fh)], fill=(200, 190, 180))
    s = str(day)
    im = pix.text_img(s, (60, 50, 70), None, None, False)
    im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    img.paste(im, (int(x + w / 2 - im.width / 2), int(y + 22)), im)


# ---------------------------------------------------------------- 云彩
CLOUD_SHAPES = {
    'heart': [".XXX...XXX.", "XXXXX.XXXXX", "XXXXXXXXXXX", "XXXXXXXXXXX", ".XXXXXXXXX.", "..XXXXXXX..", "...XXXXX...", "....XXX....",
              ".....X....."],
    'cat': ["X.......X..", "XX.....XX..", "XXXXXXXXX..", "XXOXXXOXX..", "XXXXXXXXX.X", "XXXXXXXXXXX", ".XXXXXXXXX.", ".XXXXXXXXX.",
            ".XX.XX.XX.."],
    'whale': ["....XXXXX......", "..XXXXXXXXX..X.", ".XXXXXXXXXXXXX.", "XXOXXXXXXXXXX..", "XXXXXXXXXXXXXX.", ".XXXXXXXXXX..X.",
              "..XXXXXXX......"],
    'star': ["....X....", "...XXX...", "XXXXXXXXX", ".XXXXXXX.", "..XXXXX..", ".XXX.XXX.", ".X.....X."],
    'rabbit': ["..X.X....", "..X.X....", "..X.X....", ".XXXXX...", ".XOXOX...", "XXXXXXXXX", "XXXXXXXXXX", ".XXXXXXXX.", "..XX..XX.."],
    'note': ["....XXX", "....X.X", "....X..", "....X..", ".XXXX..", "XXXXX..", ".XXX..."],
}


@lru_cache(None)
def cloud_img(kind, s=3, col=(255, 255, 255), shade=(214, 222, 240), eye=(90, 90, 120)):
    rows = CLOUD_SHAPES[kind]
    h = len(rows); w = max(len(r) for r in rows)
    im = Image.new('RGBA', (w, h)); px = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == 'X': px[x, y] = (shade if y >= h - 2 else col) + (255,)
            elif ch == 'O': px[x, y] = eye + (255,)
    im = im.resize((w * s, h * s), Image.NEAREST)
    # 边缘削成圆的：每个角去掉一格
    a = np.array(im)
    return outline(Image.fromarray(a), lerpc(shade, (120, 130, 170), 0.5))


def shape_cloud(img, kind, x, y, s=3, alpha=1.0, col=(255, 255, 255), shade=(214, 222, 240)):
    im = cloud_img(kind, s, col, shade)
    dpaste(img, im, x - im.width / 2, y - im.height / 2, alpha)


# ---------------------------------------------------------------- 牵着的两只手（侧面大特写）
def hands(img, d, cx, cy, s, sep=0.0, slip=0.0, T=0.0, sleeve_l=ORANGE, sleeve_r=SKY_B, shade=1.0):
    """左边他的手从左边伸过来，右边她的手从右边伸过来，在中间握住。sep 是两只手分开的距离（像素），
    slip 0..1 让手指一根根松开"""
    sh = lambda c: lerpc((10, 10, 30), c, shade)
    sk, skd, skl = sh(SKIN), sh(SKIN_S), sh((255, 232, 210))
    for side in (-1, 1):
        ox = cx + side * (6 * s + sep / 2)
        sl = sh(sleeve_l if side < 0 else sleeve_r)
        # 手臂和袖子
        d.polygon([(ox + side * 10 * s, cy - 7 * s), (ox + side * 60 * s, cy - 14 * s), (ox + side * 60 * s, cy + 12 * s),
                   (ox + side * 10 * s, cy + 6 * s)], fill=sh((40, 30, 50)))
        d.polygon([(ox + side * 18 * s, cy - 8 * s), (ox + side * 60 * s, cy - 13 * s), (ox + side * 60 * s, cy + 11 * s),
                   (ox + side * 18 * s, cy + 6 * s)], fill=sl)
        d.rectangle([min(ox + side * 18 * s, ox + side * 20 * s), cy - 8 * s, max(ox + side * 18 * s, ox + side * 20 * s), cy + 6 * s],
                    fill=lerpc(sl, (0, 0, 0), 0.25))
        # 手掌
        d.rounded_rectangle([min(ox, ox + side * 18 * s) - 1, cy - 7 * s - 1, max(ox, ox + side * 18 * s) + 1, cy + 5 * s + 1], 3 * s,
                            fill=OUT)
        d.rounded_rectangle([min(ox, ox + side * 18 * s), cy - 7 * s, max(ox, ox + side * 18 * s), cy + 5 * s], 3 * s, fill=sk)
        d.line([(ox + side * 4 * s, cy + 4 * s), (ox + side * 16 * s, cy + 4 * s)], fill=skd, width=max(1, s))
        # 四根手指：握住时弯过去搭在对方手背上；slip 让它们一根根缩回来
        for k in range(4):
            open_ = clamp(slip * 4 - (k if side < 0 else 3 - k) * 0.7)
            fy = cy - 5 * s + k * 3 * s
            reach = lerp(9, 2, open_) * s
            x_a = ox; x_b = ox - side * reach
            d.rounded_rectangle([min(x_a, x_b) - 1, fy - 1, max(x_a, x_b) + 1, fy + 2 * s + 1], s, fill=OUT)
            d.rounded_rectangle([min(x_a, x_b), fy, max(x_a, x_b), fy + 2 * s], s, fill=skl if k % 2 == 0 else sk)
        # 大拇指
        d.rounded_rectangle([min(ox + side * 2 * s, ox + side * 10 * s) - 1, cy - 10 * s - 1, max(ox + side * 2 * s, ox + side * 10 * s) + 1,
                             cy - 7 * s + 1], s, fill=OUT)
        d.rounded_rectangle([min(ox + side * 2 * s, ox + side * 10 * s), cy - 10 * s, max(ox + side * 2 * s, ox + side * 10 * s), cy - 7 * s],
                            s, fill=sk)


# ---------------------------------------------------------------- 地球、山
def globe(img, d, cx, cy, r, T, spin=0.4):
    planet(img, d, cx, cy, r, T, ground=(120, 200, 110), ground_d=(80, 150, 90), sea=(70, 140, 230), spin=spin)
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 260, fill=(220, 240, 255))


def mountains(d, base, amp, freq, ph, col, snow=None, off=0.0):
    """尖尖的山：三角形的锯齿叠加，snow 给山顶一层白"""
    pts = []
    for x in range(-2, W + 3, 2):
        xx = x + off
        u = (xx * freq + ph) % 1
        tri = 1 - abs(2 * u - 1)
        k = int(xx * freq + ph)
        hk = 0.55 + 0.45 * ((k * 37) % 11) / 10
        y = base - amp * tri * hk - 0.15 * amp * math.sin(xx * 0.05)
        pts.append((x, y))
    d.polygon(pts + [(W + 2, H), (-2, H)], fill=col)
    if snow:
        for (x, y) in pts:
            if y < base - amp * 0.62: d.line([(x, y), (x + 1, y + 4)], fill=snow)
