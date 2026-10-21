"""曾经是情侣 · 像素工具：缓动、点阵渐变与光晕、粒子、角色精灵和文字。所有画面都画在 480×270 的画布上。

从 zuozhuandeng/pix.py 复制而来，换了两个角色的造型（他穿牛仔蓝衬衫，她披着长发、穿珊瑚红连衣裙、别一枚红发卡）。
"""
import math, random
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 480, 270
FPS = 30
_TTC = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
FONT = ImageFont.truetype(_TTC, 16, index=2)     # 文泉驿点阵正黑：16px、12px 都有内嵌点阵字形
FONT_S = ImageFont.truetype(_TTC, 12, index=2)

# 渲染前由 render.py 填好：每帧音量、节拍和小节线、歌名歌手
AUDIO = {'amp': np.zeros(1), 'beats': np.zeros(0), 'bars': np.zeros(0)}
META = {}


def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, f): return a + (b - a) * f
def lerpc(c1, c2, f): f = clamp(f); return tuple(int(round(a + (b - a) * f)) for a, b in zip(c1, c2))
def ease(f): f = clamp(f); return f * f * (3 - 2 * f)
def eout(f): f = clamp(f); return 1 - (1 - f) ** 3
def ein(f): f = clamp(f); return f ** 3
def eback(f): f = clamp(f); c = 1.9; return 1 + (c + 1) * (f - 1) ** 3 + c * (f - 1) ** 2
def span(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def tri(f): return 1 - abs(2 * (f % 1) - 1)


def amp(T):
    a = AUDIO['amp']
    return float(a[min(len(a) - 1, max(0, int(T * FPS)))])


def pulse(T, decay=0.3, which='beats'):
    """拍点上为 1，之后在 decay 秒内衰减到 0"""
    b = AUDIO[which]
    i = int(np.searchsorted(b, T, 'right')) - 1
    return 0.0 if i < 0 else max(0.0, 1 - (T - b[i]) / decay)


# ---------------------------------------------------------------- 点阵渐变、光晕、半透明
_B4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], float) / 16 + 1 / 32


def bayer(h, w, ox=0, oy=0):
    return np.roll(np.tile(_B4, (h // 4 + 2, w // 4 + 2)), (-oy % 4, -ox % 4), (0, 1))[:h, :w]


BAYER = bayer(H, W)


@lru_cache(None)
def vgrad(w, h, stops, steps=5):
    """竖向渐变，相邻色之间分 steps 档，用 Bayer 点阵过渡。stops = ((位置0..1, 颜色), ...)"""
    ys = (np.arange(h) + 0.5) / h
    pos = np.array([p for p, _ in stops], float); cols = np.array([c for _, c in stops], float)
    k = np.clip(np.searchsorted(pos, ys, 'right') - 1, 0, len(pos) - 2)
    f = np.clip((ys - pos[k]) / np.maximum(pos[k + 1] - pos[k], 1e-6), 0, 1)
    q = np.clip(np.floor(f[:, None] * steps + bayer(h, w)) / steps, 0, 1)[..., None]
    c = cols[k][:, None, :] * (1 - q) + cols[k + 1][:, None, :] * q
    return Image.fromarray(c.round().astype(np.uint8))


def sky(img, stops, y0=0, y1=H, steps=5):
    stops = tuple((p, tuple(c)) for p, c in stops)
    img.paste(vgrad(W, int(y1 - y0), stops, steps), (0, int(y0)))


def blend_box(img, box, col, alpha, levels=8):
    """在 box 内按 alpha 数组（与 box 同大小）混合颜色。alpha 量化成几档，档与档之间用 Bayer 点阵过渡"""
    x0, y0, x1, y1 = box
    a = np.asarray(img.crop(box), float)
    al = np.clip(np.floor(alpha * levels + bayer(y1 - y0, x1 - x0, x0, y0)) / levels, 0, 1)[..., None]
    a = a * (1 - al) + np.array(col, float) * al
    img.paste(Image.fromarray(a.round().astype(np.uint8)), (x0, y0))


def glow(img, cx, cy, r, col, a=0.5, ry=None, power=1.6):
    ry = ry or r
    x0, y0 = max(0, int(cx - r)), max(0, int(cy - ry))
    x1, y1 = min(W, int(cx + r) + 1), min(H, int(cy + ry) + 1)
    if x1 <= x0 or y1 <= y0 or a <= 0: return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    dist = np.sqrt(((xx - cx) / r) ** 2 + ((yy - cy) / ry) ** 2)
    blend_box(img, (x0, y0, x1, y1), col, a * np.clip(1 - dist, 0, 1) ** power)


def tfill(img, shape, coords, col, a, width=1):
    if a <= 0: return
    m = Image.new('L', (W, H), 0); md = ImageDraw.Draw(m)
    if shape == 'line': md.line(coords, fill=int(255 * clamp(a)), width=width)
    else: getattr(md, shape)(coords, fill=int(255 * clamp(a)))
    img.paste(col, (0, 0, W, H), m)


def darken(img, a, col=(0, 0, 0)):
    if a > 0: img.paste(col, (0, 0, W, H), Image.new('L', (W, H), int(255 * clamp(a))))


def dither_fade(img, a, col=(0, 0, 0)):
    """按 Bayer 点阵把画面盖上纯色（a=1 时全盖住）"""
    if a <= 0: return
    m = Image.fromarray(((BAYER < a) * 255).astype(np.uint8))
    img.paste(col, (0, 0, W, H), m)


def vignette(img, a=0.35, col=(10, 6, 24)):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    blend_box(img, (0, 0, W, H), col, a * np.clip(d - 0.55, 0, 1) * 2.2)


@lru_cache(None)
def _vig(a, col):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    al = np.clip(np.floor(a * np.clip(d - 0.6, 0, 1) ** 1.3 * 2.4 * 8 + BAYER) / 8, 0, 1)
    return Image.fromarray((al * 255).astype(np.uint8))


def vig(img, a=0.35, col=(10, 6, 24)):
    img.paste(col, (0, 0, W, H), _vig(round(a, 2), col))


def grade(img, sat=1.0, mul=(1, 1, 1), add=(0, 0, 0)):
    """整体调色：饱和度、乘色、加色"""
    a = np.asarray(img, float)
    if sat != 1:
        g = a @ np.array([0.3, 0.59, 0.11])
        a = g[..., None] + (a - g[..., None]) * sat
    a = a * np.array(mul) + np.array(add)
    img.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))


# ---------------------------------------------------------------- 小精灵（字符画）
SPR = {
    'heart': [".RR.RR.", "RWRRRRR", "RRRRRRR", ".RRRRR.", "..RRR..", "...R..."],
    'heart_l': [".YY.", "YWYY", "YYYY", ".YYY", "..YY", "...Y"],
    'heart_r': ["RR.", "RRR", "RRR", "RR.", "R..", "..."],
    'bigheart': ["..RRR...RRR..", ".RWWRR.RRRRR.", "RRWRRRRRRRRRR", "RRRRRRRRRRRRR", "RRRRRRRRRRRRR",
                 ".RRRRRRRRRRR.", "..RRRRRRRRR..", "...RRRRRRR...", "....RRRRR....", ".....RRR.....", "......R......"],
    'note': ["..KK", "..KK", "..K.", "..K.", "KKK.", "KK.."],
    'star': ["..Y..", ".YYY.", "YYYYY", ".YYY.", ".Y.Y."],
    'bird': ["K...K", ".K.K.", "..K.."],
    'drop': [".B.", "BBB", "BBB", ".B."],
    'mail': ["WWWWWWW", "WKWWWKW", "WWKWKWW", "WWWKWWW", "WWWWWWW"],
    'anger': [".R.R.", "RR.RR", ".....", "RR.RR", ".R.R."],
}
SPAL = {'R': (238, 76, 104), 'W': (255, 236, 240), 'Y': (255, 214, 80), 'K': (40, 30, 48), 'B': (120, 190, 255)}


@lru_cache(None)
def spr(name, s=1, flip=False, tint=None):
    rows = SPR[name]
    h = len(rows); w = max(len(r) for r in rows)
    im = Image.new('RGBA', (w, h)); px = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.': px[x, y] = (tint if tint else SPAL[ch]) + (255,)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if s != 1: im = im.resize((w * s, h * s), Image.NEAREST)
    return im


def with_alpha(im, a):
    if a >= 1: return im
    im = im.copy()
    im.putalpha(im.getchannel('A').point(lambda v: int(v * clamp(a))))
    return im


def paste(img, im, x, y, alpha=1.0, anchor='cb'):
    """anchor: cb=底边中点，cc=中心，lt=左上"""
    if alpha <= 0: return
    if alpha < 1: im = with_alpha(im, alpha)
    if anchor == 'cb': x, y = x - im.width / 2, y - im.height
    elif anchor == 'cc': x, y = x - im.width / 2, y - im.height / 2
    img.paste(im, (int(round(x)), int(round(y))), im)


def put(img, name, x, y, s=1, flip=False, tint=None, alpha=1.0, anchor='cc'):
    paste(img, spr(name, s, flip, tint), x, y, alpha, anchor)


def outline(im, col):
    a = np.array(im)
    m = a[..., 3] > 0
    n = np.zeros_like(m)
    n[1:] |= m[:-1]; n[:-1] |= m[1:]; n[:, 1:] |= m[:, :-1]; n[:, :-1] |= m[:, 1:]
    a[n & ~m] = tuple(col) + (255,)
    return Image.fromarray(a)


# ---------------------------------------------------------------- 角色
# 两个原创角色："我"是黑色短发、穿牛仔蓝衬衫的男孩；"你"是黑褐色长发、穿珊瑚红连衣裙、别着一枚红发卡的女孩。
# 红色是两人之间那根红线的颜色。'old' 是多年以后的样子：他穿深色外套，她把长发盘起来。
# 头部是 12×12 的字符画，身体按姿势用矩形和线段现画，最后自动描一圈深色轮廓。
OUT = (40, 30, 48)
SKIN, SKIN_S = (252, 218, 186), (232, 182, 152)
EYE, BLUSH, MOUTH = (46, 34, 48), (246, 146, 150), (198, 88, 96)

LOOK = {
    ('girl', 'young'): dict(hair=(58, 38, 46), hair_s=(38, 24, 32), hair_l=(104, 72, 80), top=(240, 106, 98), top_s=(198, 72, 76),
                            low=(240, 106, 98), low_s=(198, 72, 76), leg=SKIN, sock=(255, 250, 246), shoe=(150, 82, 70),
                            acc=(226, 40, 64), arm=SKIN, collar=(255, 246, 238), long=True),
    ('boy', 'young'): dict(hair=(34, 32, 46), hair_s=(20, 18, 30), hair_l=(70, 74, 104), top=(92, 140, 208), top_s=(62, 102, 166),
                           low=(54, 56, 78), low_s=(40, 42, 60), shoe=(240, 240, 244), collar=(236, 240, 250)),
    ('girl', 'old'): dict(hair=(58, 38, 46), hair_s=(38, 24, 32), hair_l=(104, 72, 80), top=(250, 236, 214), top_s=(220, 200, 176),
                          low=(132, 150, 120), low_s=(104, 120, 96), leg=SKIN, shoe=(120, 80, 64), acc=(226, 40, 64), arm=(250, 236, 214),
                          bun=True),
    ('boy', 'old'): dict(hair=(34, 32, 46), hair_s=(20, 18, 30), hair_l=(70, 74, 104), top=(70, 74, 96), top_s=(50, 52, 72),
                         low=(44, 46, 62), low_s=(34, 36, 50), shoe=(90, 70, 60), scarf=(196, 52, 64)),
}

HEAD = {
    ('girl', 'front'): ["...hHHHHh...", ".hHHLLHHHHh.", "hHHLLHHHHHHh", "HHHHHHHHHHAH", "HHHHHHHHHAAA", "HHSHHHHHSSAH",
                        "HSSSSSSSSSSH", "HSSSSSSSSSSH", "HSSSSSSSSSSH", "HhSSSSSSSShH", "Hh.SSSSSS.hH", "hh..ssss..hh"],
    ('boy', 'front'): ["..H.HHH.H...", ".HHHHHHHHHH.", "HHHLLHHHHHHH", "HHHHHHHHHHHH", "HHHHHHHHHHHH", "HHSHHSHHHSHH",
                       "HSSSSSSSSSSH", "hSSSSSSSSSSh", ".SSSSSSSSSS.", ".SSSSSSSSSS.", "..SSSSSSSS..", "....ssss...."],
    ('girl', 'side'): ["...hHHHHh...", ".hHHLLHHHHh.", "hHHLLHHHHHHh", "HHHHHHHHHHHH", "HHHHHHHHHHSH", "HHHHHHHHSSSS",
                       "AHHHHHHSSSSS", "AAHHHHHSSSSS", "HHHHHHSSSSSS", "hHHHHhSSSSS.", "hHHHh..SSSS.", "hhh.....ss.."],
    ('boy', 'side'): ["..H.HHHH....", ".HHHHHHHHH..", "HHHHLLHHHHH.", "HHHHHHHHHHHH", "HHHHHHHHHHSH", "HHHHHHHSHSSS",
                      "HHHHHHSSSSSS", "HHHHHSSSSSSS", ".HHHHSSSSSSS", ".hHHSSSSSSS.", "..hSSSSSSSS.", "....sss....."],
    ('girl', 'back'): ["...hHHHHh...", ".hHHHHHHHHh.", "hHHLLHHHHHHh", "HHHLLHHHHHHH", "HHHHHHHHHHHH", "HHHHHHHHHHHH",
                       "HHHHHHHHHHHH", "HHHHHAAHHHHH", "HHHHHHHHHHHH", "hHHHHHHHHHHh", "hHHHHHHHHHHh", ".hHHHHHHHHh."],
    ('boy', 'back'): ["..H.HHH.H...", ".HHHHHHHHHH.", "HHHHHHHHHHHH", "HHHLLHHHHHHH", "HHHHHHHHHHHH", "HHHHHHHHHHHH",
                      "HHHHHHHHHHHH", "hHHHHHHHHHHh", ".hHHHHHHHHh.", "..SSSSSSSS..", "..SSSSSSSS..", "....ssss...."],
}

CW, CH, CX, FY = 30, 42, 15, 40      # 角色画布大小；脚底中点在 (CX, FY)


def _seg(d, x0, y0, x1, y1, col, w=2):
    """像素线段：沿长轴逐格画 w 宽的短条"""
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = round(lerp(x0, x1, i / n)); y = round(lerp(y0, y1, i / n))
        if abs(y1 - y0) >= abs(x1 - x0): d.rectangle([x, y, x + w - 1, y], fill=col)
        else: d.rectangle([x, y, x, y + w - 1], fill=col)


def _limb(d, pts, col, w=2):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]): _seg(d, x0, y0, x1, y1, col, w)


def _face(px, view, hx, hy, expr, L, flip_eye=False):
    """在头部字符画上画五官。px 是像素访问器，(hx, hy) 是头部左上角"""
    if view == 'back': return
    eyes = [(hx + 3, hy + 7), (hx + 8, hy + 7)] if view == 'front' else [(hx + 8, hy + 7)]
    cheeks = [(hx + 2, hy + 9), (hx + 9, hy + 9)] if view == 'front' else [(hx + 9, hy + 9)]
    mouth = [(hx + 5, hy + 10), (hx + 6, hy + 10)] if view == 'front' else [(hx + 10, hy + 10)]

    def P(x, y, c):
        if 0 <= x < CW and 0 <= y < CH: px[x, y] = c + (255,)
    EYE = L.get('eye', globals()['EYE'])
    if expr == 'drunk':
        for (ex, ey) in eyes: P(ex - 1, ey, EYE); P(ex, ey + 1, EYE); P(ex + 1, ey, EYE)
        for (cx, cy) in cheeks: P(cx, cy, BLUSH); P(cx - 1 if view == 'front' and cx < hx + 6 else cx + (0 if view == 'side' else 1), cy, BLUSH)
        P(mouth[0][0], mouth[0][1], MOUTH)
        return
    if expr == 'sneer':
        for (ex, ey) in eyes: P(ex, ey, EYE); P(ex + (1 if view == 'side' else (1 if ex > hx + 6 else -1)), ey, EYE)
        P(mouth[0][0], mouth[0][1], EYE)
        if view == 'front': P(mouth[1][0] + 1, mouth[1][1] - 1, EYE)
        return
    for (ex, ey) in eyes:
        if expr in ('happy', 'laugh'):
            P(ex - 1, ey + 1, EYE); P(ex, ey, EYE); P(ex + 1, ey + 1, EYE)
        elif expr in ('closed', 'shy', 'pout', 'blink'):
            P(ex - (1 if view == 'front' and ex < hx + 6 else 0), ey + 1, EYE); P(ex + (0 if view == 'front' and ex < hx + 6 else 1), ey + 1, EYE)
        elif expr == 'sad':
            P(ex, ey + 1, EYE); P(ex - 1 if ex < hx + 6 else ex + 1, ey - 1, L['hair_s'])
        elif expr == 'down':
            P(ex, ey + 1, EYE)
        elif expr == 'surprised':
            P(ex, ey, EYE); P(ex, ey + 1, EYE); P(ex, ey - 1, EYE)
        else:
            P(ex, ey, EYE); P(ex, ey + 1, EYE)
    for (cx, cy) in cheeks:
        if expr in ('shy', 'pout', 'laugh', 'happy', 'smile', 'blush'):
            P(cx, cy, BLUSH)
            if expr in ('shy', 'pout'): P(cx + (1 if cx > hx + 6 or view == 'side' else -0), cy, BLUSH) if view == 'front' else P(cx - 1, cy, BLUSH)
    if expr in ('laugh', 'surprised'):
        for (mx, my) in mouth: P(mx, my, MOUTH)
        if view == 'front': P(mouth[0][0], mouth[0][1] - 1, MOUTH) if expr == 'surprised' else None
    elif expr in ('sad', 'worried', 'pout'):
        P(mouth[0][0], mouth[0][1], EYE)
    elif expr in ('smile', 'happy', 'shy', 'blush', 'closed', 'neutral', 'down', 'blink'):
        if view == 'front': P(mouth[0][0], mouth[0][1], MOUTH); P(mouth[1][0], mouth[1][1], MOUTH)
        else: P(mouth[0][0], mouth[0][1], MOUTH)


@lru_cache(None)
def char_img(who, age='young', view='side', pose='stand', ph=0, expr='smile', arms='auto', scarf=None, tint=None):
    """画一个角色，返回 30×42 的 RGBA 图，脚底中点在 (15, 40)，侧面朝右"""
    L = dict(LOOK[(who, age)])
    girl = who == 'girl'
    im = Image.new('RGBA', (CW, CH)); d = ImageDraw.Draw(im)
    top, top_s, low, low_s, shoe = L['top'], L['top_s'], L['low'], L['low_s'], L['shoe']
    leg = L.get('leg') or low; legs_s = lerpc(leg, (0, 0, 0), 0.18)
    sock = L.get('sock')
    cx = CX
    bob = 0
    if pose == 'walk': bob = -1 if ph % 2 == 1 else 0
    if pose == 'run': bob = -1 if ph % 2 == 1 else 0
    if pose == 'jump': bob = -3
    ty = FY - 16 + bob                         # 上身顶端
    hip = FY - 9 + bob
    old = False

    def leg_pair(back, front):
        """侧面的两条腿。back/front = (脚相对髋部的 dx, 抬脚高度, 膝盖位置或 None)"""
        for k, (dx, lift, knee) in enumerate((back, front)):
            col = legs_s if k == 0 else leg
            hx = cx - 1 + k
            y0 = hip + (5 if girl else 0)
            fy = FY - 2 - lift
            if knee and fy - y0 > 3:
                kx, ky = knee
                _limb(d, [(hx, y0), (hx + kx, y0 + ky), (hx + dx, fy)], col)
            else:
                _seg(d, hx, y0, hx + dx, fy, col)
            if girl and sock and lift == 0: d.rectangle([hx + dx, fy, hx + dx + 1, fy], fill=sock)
            d.rectangle([hx + dx, fy + 1, hx + dx + 2, fy + 1], fill=lerpc(shoe, (0, 0, 0), 0.2) if k == 0 else shoe)

    # ---- 腿和下装
    if view == 'side':
        if pose == 'sit':
            y = FY - 9
            d.rectangle([cx - 3, y, cx + 4, y + 1], fill=low if not girl else low)
            d.rectangle([cx + 3, y + 2, cx + 4, FY - 2], fill=leg)
            d.rectangle([cx + 3, FY - 1, cx + 6, FY - 1], fill=shoe)
            if girl: d.rectangle([cx - 3, y - 1, cx + 3, y + 1], fill=low)
        else:
            n = None
            cyc = {'stand': [((0, 0, n), (1, 0, n))] * 4,
                   'walk': [((-3, 0, n), (3, 0, n)), ((-1, 1, n), (1, 0, n)), ((3, 0, n), (-3, 0, n)), ((1, 0, n), (-1, 1, n))],
                   'run': [((-4, 1, n), (2, 3, (3, 3))), ((-3, 3, (0, 3)), (1, 0, n)),
                           ((2, 3, (3, 3)), (-4, 1, n)), ((1, 0, n), (-3, 3, (0, 3)))],
                   'jump': [((-2, 2, (1, 3)), (2, 3, (3, 2)))] * 4}[pose if pose in ('walk', 'run', 'jump') else 'stand']
            b, f = cyc[ph % 4]
            leg_pair(b, f)
            if girl:
                y = hip - 2
                d.rectangle([cx - 3, y, cx + 2, y + 1], fill=low)
                d.rectangle([cx - 4, y + 2, cx + 3, y + 4], fill=low)
                d.rectangle([cx - 4, y + 5, cx + 3, y + 5], fill=low_s)
            else:
                d.rectangle([cx - 2, hip, cx + 1, hip + 1], fill=low)
    else:
        if pose == 'sit':
            y = FY - 9
            d.rectangle([cx - 4, y, cx + 3, y + 2], fill=low)
            if view == 'front':
                for lx in (cx - 3, cx + 1):
                    d.rectangle([lx, y + 3, lx + 1, FY - 2], fill=leg)
                    d.rectangle([lx - (1 if lx < cx else 0), FY - 1, lx + (1 if lx < cx else 2), FY - 1], fill=shoe)
        else:
            sway = {'walk': [0, 1, 0, -1], 'run': [1, 2, -1, -2]}.get(pose, [0] * 4)[ph % 4]
            for k, lx in enumerate((cx - 3, cx + 1)):
                lift = max(0, sway if k == 0 else -sway)
                y0 = hip + (5 if girl else 0)
                d.rectangle([lx, y0, lx + 1, FY - 2 - lift], fill=leg)
                if girl and sock and lift == 0: d.rectangle([lx, FY - 2, lx + 1, FY - 2], fill=sock)
                d.rectangle([lx - (1 if k == 0 else 0), FY - 1 - lift, lx + (1 if k == 0 else 2), FY - 1 - lift], fill=shoe)
            if girl:
                y = hip - 2
                d.rectangle([cx - 4, y, cx + 3, y + 1], fill=low)
                d.rectangle([cx - 5, y + 2, cx + 4, y + 4], fill=low)
                d.rectangle([cx - 5, y + 5, cx + 4, y + 5], fill=low_s)
            else:
                d.rectangle([cx - 4, hip, cx + 3, hip + 1], fill=low)

    # ---- 手臂（先画身后的那只）
    sh = ty + 1                                 # 肩膀高度
    if arms == 'auto':
        arms = {'walk': 'swing', 'run': 'run', 'jump': 'up', 'sit': 'lap'}.get(pose, 'down')
    sw = {'swing': [-2, 0, 2, 0], 'run': [-3, 0, 3, 0]}.get(arms, [0] * 4)[ph % 4]

    def arm(pts, col, hand=True):
        _limb(d, pts, col)
        if hand:
            x, y = pts[-1]; d.rectangle([x, y, x + 1, y], fill=SKIN)

    front_arms = []
    if view == 'side':
        far, near = [], []
        if arms in ('down', 'swing', 'run', 'lap'):
            if arms == 'run':
                far = [(cx - 1, sh), (cx - 1 - sw, sh + 3), (cx + 1 - sw, sh + 4)]
                near = [(cx, sh), (cx + sw, sh + 3), (cx + sw + 2, sh + 4)]
            elif arms == 'lap':
                near = [(cx, sh), (cx + 1, sh + 4), (cx + 3, sh + 6)]
            else:
                far = [(cx - 1, sh), (cx - 1 - sw, sh + 5)]
                near = [(cx, sh), (cx + sw, sh + 5)]
        elif arms == 'phone':
            near = [(cx, sh), (cx + 1, sh + 4), (cx + 4, sh + 2)]
        elif arms == 'hug':
            far = [(cx, sh + 1), (cx + 5, sh + 1)]
            near = [(cx, sh + 2), (cx + 6, sh + 2)]
        elif arms == 'reach':
            far = [(cx - 1, sh), (cx - 1, sh + 5)]
            near = [(cx, sh), (cx + 7, sh + 2)]
        elif arms == 'hold':                    # 牵着身后那人的手
            far = [(cx - 1, sh), (cx - 4, sh + 5)]
            near = [(cx, sh), (cx + 1, sh + 5)]
        elif arms == 'hold_f':                  # 往前下方伸手，牵着前面那人的手
            far = [(cx - 1, sh), (cx - 2, sh + 5)]
            near = [(cx, sh), (cx + 4, sh + 5)]
        elif arms == 'wave':
            far = [(cx - 1, sh), (cx - 1, sh + 5)]
            wv = [0, 1, 2, 1][ph % 4]
            near = [(cx, sh), (cx + 2, sh - 3), (cx + 2 + wv - 1, sh - 7)]
        elif arms == 'up':
            far = [(cx - 1, sh), (cx - 3, sh - 6)]
            near = [(cx, sh), (cx + 2, sh - 6)]
        elif arms == 'type':
            far = [(cx - 1, sh), (cx + 1, sh + 4), (cx + 5, sh + 4)]
            near = [(cx, sh), (cx + 2, sh + 4), (cx + 6, sh + 4)]
        elif arms == 'eat':
            near = [(cx, sh), (cx + 2, sh + 4), (cx + 5, sh + 2 - (ph % 2))]
        elif arms == 'throw':
            if ph % 2 == 0: near = [(cx, sh), (cx - 3, sh - 3), (cx - 5, sh - 6)]
            else: near = [(cx, sh), (cx + 4, sh - 1), (cx + 7, sh - 3)]
            far = [(cx - 1, sh), (cx + 2, sh + 4)]
        elif arms == 'umbrella':
            far = [(cx - 1, sh), (cx - 1, sh + 5)]
            near = [(cx, sh), (cx + 2, sh + 1), (cx + 3, sh - 3)]
        elif arms == 'pull':                    # 向后伸手拉人
            far = [(cx, sh), (cx + 2, sh + 5)]
            near = [(cx - 1, sh), (cx - 7, sh + 2)]
        if far: arm(far, lerpc(L.get('arm', top_s), (0, 0, 0), 0.15))
        front_arms = [near] if near else []
    else:
        lx, rx = cx - 6, cx + 4
        if arms in ('down', 'swing', 'run', 'lap'):
            a = sw // 2
            front_arms = [[(lx, sh), (lx, sh + 5 + a)], [(rx, sh), (rx, sh + 5 - a)]]
            if arms == 'lap': front_arms = [[(lx, sh), (lx + 1, sh + 5)], [(rx, sh), (rx - 1, sh + 5)]]
        elif arms == 'wave':
            wv = [0, 1, 2, 1][ph % 4]
            front_arms = [[(lx, sh), (lx, sh + 5)], [(rx, sh), (rx + 2, sh - 3), (rx + 1 + wv, sh - 7)]]
        elif arms == 'up':
            front_arms = [[(lx, sh), (lx - 2, sh - 4), (lx - 2, sh - 8)], [(rx, sh), (rx + 2, sh - 4), (rx + 2, sh - 8)]]
        elif arms == 'phone':
            front_arms = [[(lx, sh), (lx + 1, sh + 4), (cx - 2, sh + 3)], [(rx, sh), (rx - 1, sh + 4), (cx + 1, sh + 3)]]
        elif arms == 'cross':
            front_arms = [[(lx, sh), (lx, sh + 3), (rx - 1, sh + 3)], [(rx, sh), (rx, sh + 4), (lx + 1, sh + 4)]]
        elif arms == 'behind':
            front_arms = [[(lx, sh), (lx + 1, sh + 4)], [(rx, sh), (rx - 1, sh + 4)]]
        elif arms == 'hold_l':                  # 左手伸出去牵人
            front_arms = [[(lx, sh), (lx - 4, sh + 5)], [(rx, sh), (rx, sh + 5)]]
        elif arms == 'hold_r':
            front_arms = [[(lx, sh), (lx, sh + 5)], [(rx, sh), (rx + 4, sh + 5)]]
        elif arms == 'cover':                   # 双手捂脸
            front_arms = [[(lx, sh), (lx + 1, sh - 2), (cx - 4, sh - 5)], [(rx, sh), (rx - 1, sh - 2), (cx + 2, sh - 5)]]
        elif arms == 'flowers':
            front_arms = [[(lx, sh), (lx + 2, sh + 4), (cx - 1, sh + 4)], [(rx, sh), (rx - 2, sh + 4), (cx, sh + 4)]]

    # ---- 上身
    tw0, tw1 = (cx - 3, cx + 2) if view == 'side' else (cx - 4, cx + 3)
    tb = hip - 1 if not girl else hip - 3
    d.rectangle([tw0, ty, tw1, tb], fill=top)
    d.rectangle([tw0, tb, tw1, tb], fill=top_s)
    if view != 'back' and L.get('collar'):
        if view == 'front': d.rectangle([cx - 1, ty, cx, ty + 1], fill=L['collar'])
        else: d.rectangle([cx + 1, ty, cx + 2, ty], fill=L['collar'])
    if old and view == 'front':
        for y in range(ty + 1, tb, 2): d.point((cx - 1, y), fill=top_s)   # 开衫的纽扣
    if scarf:
        d.rectangle([tw0, ty, tw1, ty + 1], fill=scarf)
        if view == 'front': d.rectangle([cx + 1, ty + 2, cx + 2, ty + 5], fill=scarf)
        elif view == 'side': d.rectangle([cx - 4, ty + 1, cx - 3, ty + 4], fill=scarf)
    if L.get('num') and view != 'back':        # 球衣上的白色号码和领口
        if view == 'front':
            d.rectangle([cx - 2, ty + 3, cx - 2, ty + 6], fill=L['num']); d.rectangle([cx, ty + 3, cx + 1, ty + 3], fill=L['num'])
            d.point([(cx + 1, ty + 4), (cx, ty + 5), (cx, ty + 6)], fill=L['num'])
            d.rectangle([cx - 1, ty, cx, ty], fill=SKIN)
        else:
            d.rectangle([cx, ty + 3, cx + 1, ty + 5], fill=L['num']); d.point((cx + 2, ty), fill=SKIN)
        d.rectangle([tw0, tb, tw1, tb], fill=L['num'])
    if L.get('hood') and view != 'front':      # 卫衣帽子
        if view == 'side': d.rectangle([cx - 4, ty, cx - 2, ty + 2], fill=L['hood'])
        else: d.rectangle([cx - 3, ty, cx + 2, ty + 2], fill=L['hood'])
    if L.get('hood') and view == 'front':
        d.point([(cx - 1, ty + 1), (cx, ty + 1)], fill=L['top_s']); d.point([(cx - 1, ty + 2), (cx, ty + 3)], fill=(250, 246, 236))
    for pts in front_arms:
        arm(pts, L.get('arm', top_s), hand=arms not in ('behind',))
    if arms == 'phone':
        if view == 'side': d.rectangle([cx + 4, sh - 2, cx + 5, sh + 1], fill=(48, 48, 66)); d.point((cx + 4, sh - 1), fill=(170, 225, 255))
        elif view == 'front': d.rectangle([cx - 2, sh + 1, cx + 1, sh + 3], fill=(48, 48, 66))

    # ---- 头
    hv = 'back' if view == 'back' else view
    rows = HEAD[(who, hv)]
    hx = cx - 6 + (1 if view == 'side' else 0) + (1 if old and view == 'side' else 0)
    hy = ty - 12 + (1 if old else 0)
    if pose == 'run' and view == 'side': hx += 1
    if expr == 'down' and view == 'side': hy += 1
    pal = {'H': L['hair'], 'h': L['hair_s'], 'L': L['hair_l'], 'S': SKIN, 's': SKIN_S, 'A': L.get('acc') or L['hair']}
    px = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.' and 0 <= hx + x < CW and 0 <= hy + y < CH:
                px[hx + x, hy + y] = pal[ch] + (255,)
    if L.get('bun'):
        bx = hx + (6 if view != 'side' else 2)
        d.rectangle([bx - 2, hy - 2, bx + 1, hy], fill=L['hair']); d.point((bx - 1, hy - 2), fill=L['hair_l'])
    if L.get('tail'):
        hc, hs = L['hair'], L['hair_s']
        if view == 'side':
            sw_ = 1 if pose in ('walk', 'run') and ph % 2 else 0
            d.rectangle([hx - 1, hy + 3, hx, hy + 4], fill=L['acc'])
            d.rectangle([hx - 3 - sw_, hy + 4, hx - 1, hy + 6], fill=hc); d.rectangle([hx - 3 - sw_, hy + 7, hx - 2 - sw_, hy + 10], fill=hs)
        elif view == 'back':
            d.rectangle([hx + 5, hy + 1, hx + 6, hy + 1], fill=L['acc'])
            d.rectangle([hx + 5, hy + 2, hx + 6, hy + 13], fill=hs); d.rectangle([hx + 5, hy + 2, hx + 5, hy + 10], fill=hc)
    if L.get('long'):
        hc, hs = L['hair'], L['hair_s']
        wv = 1 if pose in ('walk', 'run') and ph % 2 else 0
        if view == 'side':
            d.rectangle([hx - wv, hy + 8, hx + 4, ty + 4], fill=hc); d.rectangle([hx - wv, hy + 9, hx - wv + 1, ty + 5], fill=hs)
            d.rectangle([hx + 1 - wv, ty + 5, hx + 3, ty + 6], fill=hs)
        elif view == 'front':
            for x0 in (hx, hx + 10):
                d.rectangle([x0, hy + 6, x0 + 1, ty + 4], fill=hc); d.point((x0 + (0 if x0 == hx else 1), ty + 5), fill=hs)
        else:
            d.rectangle([hx + 1, hy + 10, hx + 10, ty + 5], fill=hc); d.rectangle([hx + 2, ty + 6, hx + 9, ty + 7], fill=hs)
            d.line([(hx + 4, hy + 11), (hx + 4, ty + 4)], fill=hs); d.line([(hx + 7, hy + 11), (hx + 7, ty + 5)], fill=hs)
    if L.get('scarf') and not scarf:
        d.rectangle([tw0, ty, tw1, ty + 1], fill=L['scarf'])
        if view == 'side': d.rectangle([cx - 4, ty + 1, cx - 3, ty + 4], fill=L['scarf'])
        elif view == 'front': d.rectangle([cx + 1, ty + 2, cx + 2, ty + 5], fill=L['scarf'])
    _face(px, view, hx, hy, expr, L)
    if L.get('glasses') and view != 'back':
        g = (70, 60, 70)
        if view == 'front':
            for ex in (hx + 3, hx + 8):
                d.rectangle([ex - 1, hy + 6, ex + 1, hy + 6], fill=g)
        else:
            d.rectangle([hx + 7, hy + 6, hx + 10, hy + 6], fill=g)
    for pts in front_arms if arms == 'cover' else []:
        x, y = pts[-1]; d.rectangle([x, y, x + 1, y + 1], fill=SKIN)

    im = outline(im, OUT)
    if tint:
        a = np.array(im); m = a[..., 3] > 0; a[m, :3] = tint
        im = Image.fromarray(a)
    return im


def person(img, who, x, y, age='young', view='side', pose='stand', ph=0, expr='smile', arms='auto', s=1, flip=False,
           scarf=None, tint=None, alpha=1.0, shade=None):
    """把角色放在 (x, y)：x 为身体中线，y 为脚底。flip=True 时侧面朝左；shade=(r,g,b) 倍数，用来压暗夜景里的人"""
    im = char_img(who, age, view, pose, ph % 4, expr, arms, scarf, tint)
    if shade:
        a = np.array(im); a[..., :3] = np.clip(a[..., :3] * np.array(shade), 0, 255).astype(np.uint8); im = Image.fromarray(a)
    ax = CX
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT); ax = CW - 1 - CX
    if s != 1: im = im.resize((CW * s, CH * s), Image.NEAREST)
    if alpha < 1: im = with_alpha(im, alpha)
    img.paste(im, (int(round(x - ax * s)), int(round(y - FY * s))), im)


def wph(t, rate=8):
    """走路/跑步的帧号"""
    return int(t * rate) % 4


# ---------------------------------------------------------------- 文字
TXT_OUT = (34, 22, 46)


@lru_cache(None)
def text_img(s, col=(255, 250, 236), out=TXT_OUT, font=None, shadow=True):
    font = font or FONT
    w = int(font.getlength(s)) + 6; h = font.size + 8
    im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im); d.fontmode = '1'
    if shadow and out: d.text((4, 4), s, font=font, fill=out)
    if out:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)): d.text((3 + dx, 2 + dy), s, font=font, fill=out)
    d.text((3, 2), s, font=font, fill=col)
    return im


def text(img, s, x, y, col=(255, 250, 236), out=TXT_OUT, font=None, alpha=1.0, scale=1, anchor='cc', shadow=True):
    im = text_img(s, col, out, font, shadow)
    if scale != 1: im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    paste(img, im, x, y, alpha, anchor)
    return im.width


# ---------------------------------------------------------------- 粒子与自然
def rng(seed): return random.Random(seed)


_R = rng(11)
STARS = [(_R.randrange(W), _R.randrange(H), _R.random() * 6.28, _R.random()) for _ in range(260)]


def stars(d, T, y1=H, alpha=1.0, n=200, ox=0, oy=0, base=(40, 40, 90)):
    for x, y, p, k in STARS[:n]:
        x = (x - ox) % W; y = (y - oy) % H
        if y >= y1: continue
        b = (0.5 + 0.5 * math.sin(T * (1.5 + k * 2.5) + p)) * alpha
        if b < 0.12: continue
        c = lerpc(base, (255, 252, 230) if k < 0.7 else (200, 220, 255), b)
        d.point((x, y), fill=c)
        if k > 0.9 and b > 0.55:
            c2 = lerpc(base, (180, 190, 255), b * 0.7)
            d.point([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], fill=c2)


def sparkle(d, x, y, t, col=(255, 250, 200), size=3):
    s = int(round(1 + (size - 1) * (0.5 + 0.5 * math.sin(t * 6))))
    d.point((x, y), fill=col)
    for i in range(1, s + 1):
        d.point([(x - i, y), (x + i, y), (x, y - i), (x, y + i)], fill=col)


def twinkle(d, x, y, f, col=(255, 255, 240), size=4):
    """十字闪光，f 从 0 到 1 先变大再消失"""
    s = int(round(size * math.sin(math.pi * clamp(f))))
    if s <= 0: return
    d.point((x, y), fill=col)
    for i in range(1, s + 1):
        d.point([(x - i, y), (x + i, y), (x, y - i), (x, y + i)], fill=col)
    if s >= 3: d.point([(x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1), (x + 1, y + 1)], fill=col)


def meteor(d, t, t0, x0, y0, dx, dy, life=0.9, n=18, col=(255, 255, 230)):
    f = (t - t0) / life
    if not 0 <= f <= 1: return
    hx, hy = x0 + dx * f, y0 + dy * f
    Ln = math.hypot(dx, dy)
    for i in range(n):
        k = i / n
        d.point((int(hx - dx / Ln * i * 1.5), int(hy - dy / Ln * i * 1.5)), fill=lerpc(col, (60, 60, 120), k))
    d.point([(int(hx) + 1, int(hy)), (int(hx), int(hy) + 1)], fill=(255, 255, 255))


def moon(d, x, y, r, col=(252, 244, 206), shade=None):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    c2 = shade or lerpc(col, (190, 180, 150), 0.4)
    for cx, cy, cr in [(-0.35, -0.2, 0.2), (0.3, 0.25, 0.15), (0.12, -0.45, 0.1), (-0.1, 0.45, 0.08)]:
        d.ellipse([x + cx * r - cr * r, y + cy * r - cr * r, x + cx * r + cr * r, y + cy * r + cr * r], fill=c2)


CLOUD_BLOBS = [(0, 6, 6), (8, 1, 8), (19, 3, 7), (27, 7, 5)]


def cloud(d, x, y, s, col, shade=None, light=None):
    for cx, cy, r in CLOUD_BLOBS:
        d.ellipse([x + (cx - r) * s, y + (cy - r) * s, x + (cx + r) * s, y + (cy + r) * s], fill=col)
    d.rectangle([x, y + 6 * s, x + 28 * s, y + 12 * s], fill=col)
    if shade: d.rectangle([x + 1 * s, y + 10 * s, x + 27 * s, y + 12 * s], fill=shade)
    if light:
        for cx, cy, r in CLOUD_BLOBS[1:3]:
            d.arc([x + (cx - r) * s, y + (cy - r) * s, x + (cx + r) * s, y + (cy + r) * s], 200, 300, fill=light)


def hill_y(x, base, amp, freq, ph):
    return base + amp * math.sin(x * freq + ph) + amp * 0.5 * math.sin(x * freq * 2.3 + ph * 1.7)


def hills(d, base, amp, freq, ph, col, x0=0, x1=W):
    for x in range(x0, x1):
        d.line([(x, int(hill_y(x, base, amp, freq, ph))), (x, H)], fill=col)


def rain(d, t, x0, x1, y0, y1, n, col, speed=220, slant=-4, ln=5, seed=0):
    sp = max(1, y1 - y0); wid = max(1, x1 - x0)
    for i in range(n):
        ph = ((i * 37 + seed * 13) % 97) / 97
        y = y0 + (t * speed * (0.85 + (i % 3) * 0.1) + ph * sp) % sp
        x = x0 + ((i * 73 + seed * 31) % wid) + slant * (y - y0) / sp * 4
        d.line([(x, y), (x + slant * 0.3, y + ln)], fill=col)


def snow(d, t, n=120, speed=18, col=(255, 255, 255), y1=H, seed=0, wind=6):
    for i in range(n):
        ph = ((i * 53 + seed) % 101) / 101
        y = (t * speed * (0.6 + (i % 5) * 0.12) + ph * (y1 + 10)) % (y1 + 10) - 5
        x = ((i * 67 + seed * 7) % (W + 20)) - 10 + wind * math.sin(t * 0.9 + i * 1.7) + t * wind * 0.8
        x %= W
        if i % 4 == 0: d.rectangle([x, y, x + 1, y + 1], fill=col)
        else: d.point((x, y), fill=col)


PETAL_COLS = [(255, 182, 200), (255, 212, 222), (250, 150, 180)]


def petals(d, t, n=40, cols=PETAL_COLS, speed=20, wind=30, x0=0, x1=W, y0=-10, y1=H, seed=0, size=2):
    """飘落的花瓣/叶子：小菱形，左右翻转"""
    wid = max(1, x1 - x0); hh = max(1, y1 - y0)
    for i in range(n):
        r1 = ((i * 53 + seed * 17) % 101) / 101; r2 = ((i * 29 + seed * 7) % 89) / 89
        y = y0 + (t * speed * (0.6 + r2 * 0.8) + r1 * hh) % hh
        x = x0 + ((i * 71 + seed * 13) % wid + t * wind * (0.5 + r1) + 8 * math.sin(t * 1.3 + i)) % wid
        c = cols[i % len(cols)]
        flipping = int(t * 4 + i) % 3
        if size == 1 or flipping == 0: d.point((x, y), fill=c)
        elif flipping == 1: d.rectangle([x, y, x + 1, y], fill=c)
        else: d.rectangle([x, y, x + 1, y + 1], fill=c); d.point((x + 1, y), fill=lerpc(c, (255, 255, 255), 0.4))


def fireflies(img, d, t, n, box, col=(255, 240, 140), seed=0):
    x0, y0, x1, y1 = box
    for i in range(n):
        r = rng(i * 31 + seed)
        bx = r.uniform(x0, x1); by = r.uniform(y0, y1)
        x = bx + 10 * math.sin(t * (0.3 + r.random() * 0.4) + r.random() * 6)
        y = by + 6 * math.sin(t * (0.4 + r.random() * 0.5) + r.random() * 6)
        b = 0.5 + 0.5 * math.sin(t * (2 + r.random() * 2) + i)
        if b > 0.35:
            glow(img, x, y, 4, col, 0.35 * b)
            d.point((int(x), int(y)), fill=lerpc((140, 130, 60), col, b))


def butterfly(d, x, y, t, col=(255, 160, 200), ph=0):
    flap = int(t * 10 + ph) % 2
    d.point((x, y), fill=(60, 40, 60)); d.point((x, y + 1), fill=(60, 40, 60))
    if flap: d.rectangle([x - 2, y - 1, x - 1, y + 1], fill=col); d.rectangle([x + 1, y - 1, x + 2, y + 1], fill=col)
    else: d.rectangle([x - 1, y - 2, x - 1, y], fill=col); d.rectangle([x + 1, y - 2, x + 1, y], fill=col)


def bird(d, x, y, t, col=(50, 50, 70), ph=0):
    f = int(t * 6 + ph) % 2
    if f: d.point([(x - 2, y - 1), (x - 1, y), (x, y + 1), (x + 1, y), (x + 2, y - 1)], fill=col)
    else: d.point([(x - 2, y + 1), (x - 1, y), (x, y + 1), (x + 1, y), (x + 2, y + 1)], fill=col)


HEART_PTS = [(16 * math.sin(a) ** 3, -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)))
             for a in [i * 2 * math.pi / 64 for i in range(64)]]


def heart_poly(cx, cy, s):
    return [(cx + x * s, cy + y * s) for x, y in HEART_PTS]


def firework(img, d, t, t0, x, y, col, r=36, life=1.6, n=32, seed=0, col2=None):
    """烟花：先拖着尾巴升空，再炸成一圈带拖尾的亮点，内圈换一种颜色，最后下坠、闪烁、变暗"""
    k = t - t0
    if k < 0: return
    rise = 0.5
    if k < rise:
        f = k / rise
        yy = lerp(H + 10, y, eout(f))
        for i in range(6): d.point((x + math.sin(i + k * 30) * 0.6, yy + i * 3), fill=lerpc((255, 240, 200), (90, 70, 100), i / 6))
        d.rectangle([x, yy - 1, x + 1, yy], fill=(255, 250, 230))
        return
    k -= rise
    if k > life: return
    f = k / life
    if f < 0.35: glow(img, x, y, r * 1.5, col, 0.5 * (1 - f / 0.35))
    rr = random.Random(seed)
    col2 = col2 or lerpc(col, (255, 255, 255), 0.55)
    for ring, (cnt, rad, c0) in enumerate(((n, r, col), (n // 2, r * 0.55, col2))):
        for i in range(cnt):
            a = 2 * math.pi * i / cnt + rr.uniform(-0.06, 0.06) + ring * 0.2
            sp = rad * (0.85 + rr.random() * 0.25)
            dist = sp * eout(min(1, f * 1.5))
            drop = 18 * f * f
            px = x + math.cos(a) * dist; py = y + math.sin(a) * dist + drop
            if f < 0.15: c = (255, 255, 245)
            elif f < 0.65: c = c0
            else: c = lerpc(c0, (50, 36, 70), (f - 0.65) / 0.35)
            if f > 0.55 and (int(k * 24) + i) % 3 == 0: continue
            if f < 0.6:
                qx = x + math.cos(a) * dist * 0.72; qy = y + math.sin(a) * dist * 0.72 + drop * 0.8
                d.line([(qx, qy), (px, py)], fill=lerpc(c, (40, 30, 60), 0.45))
            if f < 0.45: d.rectangle([px, py, px + 1, py + 1], fill=c)
            else: d.point((px, py), fill=c)


# ---------------------------------------------------------------- 树、花、草
def tree_round(d, x, base, s=1.0, leaf=(64, 150, 84), leaf_l=(98, 186, 96), trunk=(112, 74, 50), sway=0):
    s = float(s)
    d.rectangle([x - 2 * s, base - 14 * s, x + 2 * s, base], fill=trunk)
    blobs = [(-8, -24, 10), (7, -25, 10), (0, -33, 11), (-3, -20, 8), (5, -18, 8)]
    for bx, by, r in blobs:
        d.ellipse([x + bx * s - r * s + sway, base + by * s - r * s, x + bx * s + r * s + sway, base + by * s + r * s], fill=leaf)
    for bx, by, r in blobs[:3]:
        d.ellipse([x + bx * s - r * s * 0.6 - 2 * s + sway, base + by * s - r * s * 0.8, x + bx * s + r * s * 0.3 + sway, base + by * s - r * s * 0.1],
                  fill=leaf_l)


def flower(d, x, y, col, kind=0, stem=(70, 150, 70), h=6, open_=1.0):
    if h > 0: d.line([(x, y), (x, y - h)], fill=stem)
    fy = y - h
    if open_ <= 0: return
    if kind == 0:     # 五瓣小花
        d.point([(x - 1, fy), (x + 1, fy), (x, fy - 1), (x, fy + 1)], fill=col)
        d.point((x, fy), fill=(255, 236, 120))
    elif kind == 1:   # 郁金香
        d.rectangle([x - 1, fy - 2, x + 1, fy], fill=col); d.point([(x - 1, fy - 3), (x + 1, fy - 3)], fill=col)
    elif kind == 2:   # 大花
        d.rectangle([x - 2, fy - 1, x + 2, fy + 1], fill=col); d.rectangle([x - 1, fy - 2, x + 1, fy + 2], fill=col)
        d.point((x, fy), fill=(255, 240, 150))
    elif kind == 3:   # 向日葵
        d.line([(x, y), (x, fy)], fill=stem, width=2)
        d.rectangle([x - 3, fy - 1, x + 3, fy + 1], fill=(255, 210, 60)); d.rectangle([x - 1, fy - 3, x + 1, fy + 3], fill=(255, 210, 60))
        d.point([(x - 2, fy - 2), (x + 2, fy - 2), (x - 2, fy + 2), (x + 2, fy + 2)], fill=(255, 190, 40))
        d.rectangle([x - 1, fy - 1, x + 1, fy + 1], fill=(130, 80, 40))


def grass(d, y, col, col2, t=0, x0=0, x1=W, step=3, seed=0, hmax=4):
    for i, x in enumerate(range(x0, x1, step)):
        h = 1 + ((i * 7 + seed) % hmax)
        sw = int(round(math.sin(t * 2 + x * 0.1) * 0.6))
        d.line([(x, y), (x + sw, y - h)], fill=col if i % 3 else col2)


# ---------------------------------------------------------------- 城市
@lru_cache(None)
def skyline(seed, w, hmin, hmax, wmin=14, wmax=34):
    r = rng(seed); out = []; x = -10
    while x < w + 40:
        bw = r.randint(wmin, wmax); bh = r.randint(hmin, hmax)
        roof = r.choice(['flat', 'flat', 'step', 'antenna', 'slope'])
        out.append((x, bw, bh, roof, r.randrange(1 << 30)))
        x += bw + r.randint(0, 3)
    return out, x


def city(img, d, base, seed, off, col, win=None, hmin=30, hmax=90, frac=0.35, T=0, wmin=14, wmax=34, edge=None, blink=True):
    lay, total = skyline(seed, W, hmin, hmax, wmin, wmax)
    base = int(round(base))
    for bx, bw, bh, roof, ws in lay:
        x = int((bx - off) % total) - 10
        if x > W + 10: x -= total
        if x + bw < -2 or x > W + 2: continue
        top = base - bh
        d.rectangle([x, top, x + bw - 1, base], fill=col)
        if edge: d.line([(x, top), (x, base)], fill=edge)
        if roof == 'step' and bw > 9: d.rectangle([x + 3, top - 5, x + bw - 4, top], fill=col)
        elif roof == 'antenna':
            d.line([(x + bw // 2, top), (x + bw // 2, top - 9)], fill=col)
            if blink and math.sin(T * 3 + ws % 7) > 0.3: d.point((x + bw // 2, top - 10), fill=(255, 80, 80))
        elif roof == 'slope': d.polygon([(x, top), (x + bw - 1, top), (x + bw - 1, top - 6)], fill=col)
        if win:
            rr = rng(ws)
            for wy in range(top + 4, base - 3, 5):
                for wx in range(x + 2, x + bw - 2, 4):
                    if rr.random() < frac:
                        on = True
                        if blink and rr.random() < 0.08: on = math.sin(T * 0.7 + rr.random() * 9) > 0
                        if on: d.rectangle([wx, wy, wx + 1, wy + 1], fill=win if rr.random() > 0.2 else lerpc(win, (255, 255, 255), 0.3))


def lamp(img, d, x, base, on=1.0, h=46, col=(70, 66, 90), light=(255, 228, 150)):
    d.rectangle([x, base - h, x + 1, base], fill=col)
    d.rectangle([x - 4, base - h - 2, x + 5, base - h], fill=col)
    d.rectangle([x - 3, base - h + 1, x + 4, base - h + 2], fill=lerpc((90, 90, 110), light, on))
    if on > 0:
        tfill(img, 'polygon', [(x - 3, base - h + 3), (x + 4, base - h + 3), (x + 24, base), (x - 23, base)], light, 0.16 * on)
        glow(img, x + 0.5, base - h + 2, 10, light, 0.45 * on)


def window_light(img, x, y, w, h, col, a=0.4):
    glow(img, x + w / 2, y + h / 2, max(w, h) * 1.2, col, a)
