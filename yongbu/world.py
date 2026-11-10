"""永不失联的爱 · 场景和道具：旧屋（同一套坐标反复用）、光照、红台灯、两只杯子、绿格布、钥匙、开关特写、
窗外巷口和那栋楼、站台和列车、楼道、手机界面、大手。

所有画面都在 480×270 的画布上。旧屋先画在 560 宽的底图上，再按镜头位置裁出 480 宽，好做慢慢的横移。
光照：先用"白天的固有色"画好整间屋子和人，再整体乘一层环境光（夜里偏冷），加上台灯的暖光（点阵分档的光圈和光锥），
最后画会发光的东西（灯泡、窗外、手机屏）。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
from pix import W, H, FONT, FONT_S, OUT, SKIN, SKIN_S, clamp, lerp, lerpc, ease, eout, ein, span, glow, blend_box, rng, bayer
import props

# ---------------------------------------------------------------- 色板
NAVY = (25, 37, 59)          # 现实：深蓝灰
FOG = (84, 103, 128)         # 雾灰
HONEY = (240, 178, 92)       # 灯光：蜜金
APRICOT = (218, 160, 117)    # 回忆：杏色
RUSTBR = (168, 98, 79)       # 回忆：橘棕
WOODBR = (103, 68, 84)       # 回忆：木褐
DAWN0, DAWN1 = (155, 174, 198), (248, 207, 159)
SHADE, SHADE_D, SHADE_L = (160, 60, 58), (112, 38, 42), (206, 96, 84)     # 红灯罩
CUPB, CUPB_D, CUPB_L = (73, 111, 158), (50, 78, 116), (120, 156, 200)     # 蓝杯（有缺口）
CUPA, CUPA_D, CUPA_L = (212, 146, 62), (160, 100, 40), (246, 196, 112)    # 琥珀杯
PLAID, PLAID_D, PLAID_L = (76, 128, 92), (50, 90, 64), (128, 176, 132)    # 绿格布
MOONY = (250, 214, 90)       # 布角的黄色弯月
BRASS = (214, 176, 84)       # 他那把钥匙的黄铜环
THREAD = (70, 130, 220)      # 她那把钥匙上的蓝线
CASE, CASE_D, CASE_L = (110, 128, 112), (78, 94, 80), (150, 166, 146)     # 灰绿硬壳箱
CARD, CARD_D = (196, 156, 104), (150, 112, 70)                              # 纸箱
WALL, WALL_D, WALL_L = (196, 184, 168), (164, 150, 136), (214, 204, 190)
FLOOR, FLOOR_D, FLOOR_L = (150, 104, 76), (118, 80, 60), (176, 128, 92)
DESK, DESK_D, DESK_L = (132, 92, 66), (98, 66, 50), (166, 120, 84)
FRAME = (226, 218, 204)
STEEL = (64, 66, 78)

# 环境光（乘在固有色上）
AMB = {
    'now': (0.36, 0.44, 0.64),
    'dark': (0.17, 0.21, 0.36),
    'black': (0.08, 0.10, 0.18),
    'past': (1.02, 0.90, 0.76),
    'past_eve': (0.86, 0.66, 0.56),
    'past_night': (0.30, 0.30, 0.46),
    'dawn': (0.92, 0.86, 0.86),
    'pre_dawn': (0.52, 0.56, 0.72),
}
WARM = (1.25, 0.86, 0.44)    # 台灯的暖光


def amb_mix(a, b, f):
    A = AMB.get(a, a); B = AMB.get(b, b)
    return tuple(lerp(x, y, clamp(f)) for x, y in zip(A, B))


# ---------------------------------------------------------------- 光照
@lru_cache(64)
def _radial(cx, cy, r, ry, levels, power):
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.sqrt(((xx - cx) / r) ** 2 + ((yy - cy) / ry) ** 2)
    v = np.clip(1 - dist, 0, 1) ** power
    return np.clip(np.floor(v * levels + pix.BAYER) / levels, 0, 1)


@lru_cache(32)
def _cone(x0, y0, half0, x1, half1, y1, levels):
    """台灯往下的光锥：从 (x0, y0) 宽 half0 张到 y1 宽 half1，越往下越淡"""
    yy, xx = np.mgrid[0:H, 0:W]
    f = np.clip((yy - y0) / max(1, y1 - y0), 0, 1)
    cx = x0 + (x1 - x0) * f
    half = half0 + (half1 - half0) * f
    inside = (yy >= y0) & (np.abs(xx - cx) <= half)
    v = inside * (1 - 0.55 * f) * np.clip(1 - np.abs(xx - cx) / np.maximum(half, 1) * 0.5, 0, 1)
    return np.clip(np.floor(v * levels + pix.BAYER) / levels, 0, 1)


def light(img, amb, lights=(), cones=()):
    """amb：环境光倍数或 AMB 里的名字；lights：[(cx, cy, r, ry, 强度, 颜色倍数)]；cones：[(参数元组, 强度, 颜色)]"""
    amb = AMB.get(amb, amb)
    a = np.asarray(img, np.float32)
    F = np.empty((H, W, 3), np.float32); F[:] = amb
    for cx, cy, r, ry, k, col in lights:
        if k <= 0: continue
        F += _radial(int(cx), int(cy), int(r), int(ry), 6, 1.3)[..., None] * (np.array(col, np.float32) * k)
    for args, k, col in cones:
        if k <= 0: continue
        F += _cone(*args)[..., None] * (np.array(col, np.float32) * k)
    img.paste(Image.fromarray(np.clip(a * F, 0, 255).astype(np.uint8)))


def emit(c, amb):
    """把一个颜色按环境光压暗（在光照之后补画的东西用）"""
    amb = AMB.get(amb, amb)
    return tuple(int(clamp(v * m / 255) * 255) for v, m in zip(c, amb))


# ---------------------------------------------------------------- 小道具
def cup(d, x, y, kind, s=1, steam=0.0, t=0.0, handle=1):
    """杯子：(x, y) 是杯底中点。kind='blue' 带缺口，'amber' 琥珀色。handle=1 杯柄朝右，-1 朝左"""
    c, cd, cl = (CUPB, CUPB_D, CUPB_L) if kind == 'blue' else (CUPA, CUPA_D, CUPA_L)
    w, h = 5 * s, 8 * s
    d.rectangle([x - w, y - h, x + w - 1, y - 1], fill=c)
    d.rectangle([x - w, y - h, x - w + s - 1, y - 1], fill=cl)
    d.rectangle([x + w - 2 * s, y - h, x + w - 1, y - 1], fill=cd)
    d.rectangle([x - w, y - h, x + w - 1, y - h + s - 1], fill=cl)
    hx = x + w if handle > 0 else x - w - 2 * s
    d.rectangle([hx, y - h + 2 * s, hx + 2 * s - 1, y - h + 2 * s + s - 1], fill=cd)
    d.rectangle([hx + (s if handle > 0 else 0), y - h + 2 * s, hx + (2 * s - 1 if handle > 0 else s - 1), y - 3 * s], fill=cd)
    d.rectangle([hx, y - 3 * s, hx + 2 * s - 1, y - 2 * s - 1], fill=cd)
    if kind == 'blue':           # 杯口的小缺口
        d.rectangle([x - 2 * s, y - h, x - s, y - h + s - 1], fill=(30, 30, 44))
    d.rectangle([x - w, y, x + w - 1, y + s - 1], fill=lerpc(c, (0, 0, 0), 0.5))
    if steam > 0:
        for k in range(3):
            ph = (t * 0.6 + k / 3) % 1
            sy = y - h - 2 - ph * 14 * s
            sx = x - 2 * s + k * 2 * s + round(math.sin(t * 2.4 + k * 2 + ph * 6) * 1.5 * s)
            a = steam * (1 - ph)
            if a > 0.15: d.rectangle([sx, sy, sx + s - 1, sy + s], fill=lerpc((120, 130, 150), (236, 238, 244), a))


def key(d, x, y, kind, s=1, ang=0.0, swing=0.0):
    """钥匙：(x, y) 是钥匙环中心。kind='hers' 挂一段蓝线，'his' 只有黄铜环"""
    ring = (196, 196, 204) if kind == 'hers' else BRASS
    r = 2 * s
    d.ellipse([x - r, y - r, x + r, y + r], outline=ring, width=max(1, s))
    ca, sa = math.cos(ang), math.sin(ang)
    for i in range(2, 9):
        px, py = x + ca * (r + i * s), y + sa * (r + i * s)
        d.rectangle([px, py, px + s - 1, py + s - 1], fill=(206, 200, 170) if kind == 'his' else (214, 214, 222))
    tx, ty = x + ca * (r + 7 * s) - sa * s, y + sa * (r + 7 * s) + ca * s
    d.rectangle([tx, ty, tx + s - 1, ty + s - 1], fill=(170, 164, 140) if kind == 'his' else (170, 170, 180))
    if kind == 'hers':
        sw = math.sin(swing) * 3 * s
        pts = [(x - r, y), (x - r - 2 * s + sw * 0.4, y + 3 * s), (x - r - 2 * s + sw, y + 7 * s)]
        d.line(pts, fill=THREAD, width=max(1, s))


def dish(d, x, y, s=1, keys=1, t=0.0, swing=0.0, ang=0.0):
    """门边矮台上的圆铁碟，(x, y) 是碟心。keys=1 只有她那把，2 再加他那把"""
    rw, rh = 12 * s, 3 * s
    d.ellipse([x - rw, y - rh, x + rw, y + rh + s], fill=(70, 72, 82))
    d.ellipse([x - rw + s, y - rh + s, x + rw - s, y + rh - s], fill=(108, 110, 122))
    d.ellipse([x - rw + 2 * s, y - rh + s, x + rw - 2 * s, y + rh - s], fill=(92, 94, 106))
    if keys >= 1: key(d, x - 4 * s, y, 'hers', max(1, s // 2) if s > 1 else 1, ang, swing)
    if keys >= 2: key(d, x + 3 * s, y - s, 'his', max(1, s // 2) if s > 1 else 1, 0.4)


def plaid(d, box, s=2, moon=True, fold=0.0):
    """绿格布：box 内画格子，右下角一针黄色弯月"""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=PLAID)
    st = 6 * s
    for x in range(int(x0) + 2 * s, int(x1), st):
        d.rectangle([x, y0, x + s, y1], fill=PLAID_D)
    for y in range(int(y0) + 2 * s, int(y1), st):
        d.rectangle([x0, y, x1, y + s], fill=PLAID_D)
    for x in range(int(x0) + 2 * s, int(x1), st):
        for y in range(int(y0) + 2 * s, int(y1), st):
            d.rectangle([x, y, x + s, y + s], fill=(40, 70, 52))
    for x in range(int(x0) + 4 * s, int(x1), st):
        d.line([(x, y0), (x, y1)], fill=PLAID_L)
    if moon:
        mx, my = x1 - 7 * s, y1 - 7 * s
        moon_glyph(d, mx, my, s)


def moon_glyph(d, x, y, s=1):
    """一针黄色弯月（缝线）"""
    pts = [(0, 0), (1, -1), (2, -1), (-1, 1), (-1, 2), (0, 3), (1, 4), (2, 4), (3, 3)]
    for px, py in pts: d.rectangle([x + px * s, y + py * s, x + px * s + s - 1, y + py * s + s - 1], fill=MOONY)


def bulb(d, x, y, s=1, lit=0.0, broken=False):
    """灯泡：(x, y) 是螺口底部中点"""
    glass = lerpc((214, 222, 230), (255, 246, 200), lit)
    d.rectangle([x - 2 * s, y - 3 * s, x + 2 * s - 1, y - 1], fill=(170, 170, 176))
    for k in range(3): d.line([(x - 2 * s, y - 3 * s + k * s), (x + 2 * s - 1, y - 3 * s + k * s)], fill=(124, 124, 132))
    d.ellipse([x - 4 * s, y - 11 * s, x + 4 * s - 1, y - 3 * s], fill=glass)
    d.rectangle([x - 2 * s, y - 5 * s, x + 2 * s - 1, y - 3 * s], fill=glass)
    if not broken:
        d.line([(x - s, y - 4 * s), (x - s, y - 7 * s), (x + s, y - 7 * s), (x + s, y - 4 * s)], fill=(150, 120, 90) if lit < 0.5 else (255, 255, 230))
    else:
        d.line([(x - s, y - 4 * s), (x - s, y - 7 * s)], fill=(90, 80, 70)); d.point((x, y - 9 * s), fill=(90, 90, 96))
        d.ellipse([x - 3 * s, y - 10 * s, x - s, y - 8 * s], fill=(150, 150, 150))
    d.rectangle([x - 3 * s, y - 10 * s, x - 2 * s, y - 8 * s], fill=(255, 255, 255))


def bulb_box(d, x, y, s=1, n=2, open_=False):
    """一盒两只的灯泡纸盒"""
    d.rectangle([x, y - 8 * s, x + 18 * s, y], fill=(222, 210, 180))
    d.rectangle([x, y - 8 * s, x + 18 * s, y - 7 * s], fill=(190, 70, 64))
    d.rectangle([x + 3 * s, y - 5 * s, x + 6 * s, y - 2 * s], fill=(250, 210, 90))
    d.rectangle([x + 12 * s, y - 5 * s, x + 15 * s, y - 2 * s], fill=(250, 210, 90))


def box(d, x0, y0, x1, y1, open_=0.0, label=True):
    """纸箱"""
    d.rectangle([x0, y0, x1, y1], fill=CARD)
    d.rectangle([x0, y0, x0 + 2, y1], fill=lerpc(CARD, (255, 240, 200), 0.3))
    d.rectangle([x1 - 3, y0, x1, y1], fill=CARD_D)
    d.line([(x0, y0 + 2), (x1, y0 + 2)], fill=CARD_D)
    if label: d.rectangle([(x0 + x1) // 2 - 3, y0 + 4, (x0 + x1) // 2 + 3, y0 + 8], fill=(232, 220, 196))
    if open_ > 0:
        f = int(6 * open_)
        d.polygon([(x0, y0), (x0 - f, y0 - f), (x0 + 6, y0 - f - 2), (x0 + 8, y0)], fill=CARD_D)
        d.polygon([(x1, y0), (x1 + f, y0 - f), (x1 - 6, y0 - f - 2), (x1 - 8, y0)], fill=CARD_D)


def suitcase(d, x, y, s=1, handle=0.0, open_=False, lay=False):
    """灰绿硬壳箱：(x, y) 是箱底中点；handle 0..1 拉杆拉出的长度"""
    w, h = 12 * s, 18 * s
    if lay:
        d.rectangle([x - 18 * s, y - 7 * s, x + 18 * s, y], fill=CASE_D)
        d.rectangle([x - 18 * s, y - 7 * s, x + 18 * s, y - 5 * s], fill=CASE_L)
        if open_:
            d.rectangle([x - 16 * s, y - 6 * s, x + 16 * s, y - 2 * s], fill=(70, 66, 70))
            d.polygon([(x - 18 * s, y - 7 * s), (x + 18 * s, y - 7 * s), (x + 16 * s, y - 24 * s), (x - 16 * s, y - 24 * s)], fill=CASE)
            d.line([(x - 16 * s, y - 22 * s), (x + 16 * s, y - 22 * s)], fill=CASE_L)
        return
    if handle > 0:
        hh = int(14 * s * handle)
        d.rectangle([x - 5 * s, y - h - hh, x - 4 * s, y - h], fill=(90, 92, 100))
        d.rectangle([x + 4 * s, y - h - hh, x + 5 * s, y - h], fill=(90, 92, 100))
        d.rectangle([x - 5 * s, y - h - hh - s, x + 5 * s, y - h - hh], fill=(60, 62, 70))
    d.rounded_rectangle([x - w, y - h, x + w, y - s], 2 * s, fill=CASE)
    d.rectangle([x - w + s, y - h + s, x - w + 2 * s, y - 2 * s], fill=CASE_L)
    for k in (-6, 0, 6):
        d.line([(x + k * s, y - h + 2 * s), (x + k * s, y - 3 * s)], fill=CASE_D)
    d.rectangle([x - w + 2 * s, y - s, x - w + 4 * s, y], fill=(40, 40, 46))
    d.rectangle([x + w - 4 * s, y - s, x + w - 2 * s, y], fill=(40, 40, 46))


def lamp_obj(d, x, y, s=1, on=0.0, dir_=-1, cable=True, head_up=0):
    """红台灯：(x, y) 是灯座底部中点。dir_=-1 灯罩朝左（朝窗/朝屋里看情况翻）。返回灯泡位置"""
    base = (52, 50, 58)
    d.rectangle([x - 7 * s, y - 2 * s, x + 7 * s, y - 1], fill=base)
    d.rectangle([x - 6 * s, y - 3 * s, x + 6 * s, y - 2 * s], fill=(80, 78, 88))
    # 斜杆
    ax, ay = x + 2 * s * (-dir_), y - 3 * s
    bx, by = x + 1 * s * (-dir_), y - 20 * s - head_up * s
    pix._limb(d, [(ax, ay), (bx, by)], (70, 68, 78), max(1, s))
    # 斜罩：一个梯形，左边一处浅凹
    hx, hy = bx + dir_ * 2 * s, by
    if dir_ < 0:
        pts = [(hx + 4 * s, hy - 3 * s), (hx - 2 * s, hy - 4 * s), (hx - 11 * s, hy + 3 * s), (hx - 7 * s, hy + 8 * s), (hx + 5 * s, hy + 3 * s)]
    else:
        pts = [(hx - 4 * s, hy - 3 * s), (hx + 2 * s, hy - 4 * s), (hx + 11 * s, hy + 3 * s), (hx + 7 * s, hy + 8 * s), (hx - 5 * s, hy + 3 * s)]
    d.polygon(pts, fill=SHADE)
    d.line(pts[:3], fill=SHADE_L, width=max(1, s))
    d.line([pts[2], pts[3]], fill=SHADE_D, width=max(1, s))
    # 凹痕
    dx_ = hx + dir_ * 3 * s
    d.rectangle([dx_ - s, hy - s, dx_, hy], fill=SHADE_D)
    # 灯口
    mx, my = (pts[2][0] + pts[3][0]) / 2, (pts[2][1] + pts[3][1]) / 2
    lc = lerpc((60, 50, 50), (255, 244, 200), on)
    d.ellipse([mx - 3 * s, my - 2 * s, mx + 3 * s, my + 2 * s], fill=lc)
    if cable:
        d.line([(x + 7 * s * (-dir_), y - 2 * s), (x + 10 * s * (-dir_), y - 1)], fill=(30, 30, 34), width=max(1, s))
    return (mx, my + s)


def photo_img(w=30, h=24, warm=1.0, lean=0.0, t=0.0, live=False):
    """合照：刚搬进来时两人并肩坐在空房的地板上。lean 0..1 小满往他肩上靠"""
    im = Image.new('RGB', (w * 2, h * 2), (226, 196, 160))
    d = ImageDraw.Draw(im)
    d.rectangle([0, h * 2 - 14, w * 2, h * 2], fill=(176, 126, 92))
    d.rectangle([0, h * 2 - 15, w * 2, h * 2 - 15], fill=(150, 104, 76))
    d.rectangle([w * 2 - 14, 4, w * 2 - 4, 16], fill=(250, 230, 180))       # 墙上的窗光
    d.rectangle([2, h * 2 - 22, 12, h * 2 - 12], fill=(196, 156, 104))     # 纸箱
    pix.person(im, 'boy', w - 8, h * 2 + 1, age='past', view='front', pose='sit', expr='happy' if lean > 0.5 else 'smile')
    gx = w + 9 - int(round(3 * lean))
    pix.person(im, 'girl', gx, h * 2 + 1, age='past', view='front', pose='sit', expr='happy')
    if lean > 0.5:   # 她的头再靠过来一点
        pass
    im = im.resize((w, h), Image.BOX)
    if warm < 1:
        a = np.asarray(im, float); g = a @ np.array([0.3, 0.59, 0.11])
        a = a * warm + g[..., None] * (1 - warm)
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return im


@lru_cache(None)
def photo_big(lean_q=0, sc=1):
    """特写时的大合照：在 120×96 的底图上直接画，人物放大 2 倍"""
    w, h = 112, 88
    im = Image.new('RGB', (w, h), (232, 204, 166))
    d = ImageDraw.Draw(im)
    pix.sky(im, ((0, (238, 214, 176)), (1, (226, 190, 150))), 0, h) if False else None
    d.rectangle([0, 0, w, 60], fill=(236, 212, 176))
    d.rectangle([70, 6, 104, 34], fill=(252, 236, 190))
    d.line([(87, 6), (87, 34)], fill=(220, 196, 160)); d.line([(70, 20), (104, 20)], fill=(220, 196, 160))
    d.rectangle([0, 60, w, h], fill=(176, 126, 92))
    for y in (66, 74, 82): d.line([(0, y), (w, y)], fill=(156, 108, 80))
    box(d, 4, 40, 26, 62, label=True)
    lean = lean_q / 4
    pix.person(im, 'boy', 50, 82, age='past', view='front', pose='sit', expr='happy' if lean > 0.4 else 'smile', s=2)
    pix.person(im, 'girl', 74 - round(4 * lean), 82 - round(1 * lean), age='past', view='front', pose='sit', expr='happy', s=2)
    cup(d, 96, 82, 'amber', 1); cup(d, 104, 82, 'blue', 1)
    return im


# ---------------------------------------------------------------- 窗外
def outside_night(img, d, box, t, rain_=1.0, glow_=0.0, seed=0, tone=0.0):
    """窗外：夜里的对面楼和雨。tone 0 深夜 → 1 清晨"""
    x0, y0, x1, y1 = box
    top = lerpc((14, 20, 38), (150, 168, 196), tone)
    bot = lerpc((30, 40, 66), (248, 206, 160), tone)
    for y in range(y0, y1):
        f = (y - y0) / max(1, y1 - y0 - 1)
        q = math.floor(f * 6 + pix._B4[y % 4, 0]) / 6
        d.line([(x0, y), (x1 - 1, y)], fill=lerpc(top, bot, q))
    # 对面的楼
    r = rng(seed)
    bx = x0 - 6
    bcol = lerpc((20, 26, 44), (126, 128, 150), tone)
    while bx < x1:
        bw = r.randint(16, 30); bh = r.randint(int((y1 - y0) * 0.35), int((y1 - y0) * 0.8))
        d.rectangle([max(x0, bx), y1 - bh, min(x1 - 1, bx + bw), y1 - 1], fill=bcol)
        for wy in range(y1 - bh + 4, y1 - 3, 6):
            for wx in range(bx + 3, bx + bw - 2, 5):
                if x0 <= wx < x1 - 2 and r.random() < 0.3 * (1 - tone):
                    d.rectangle([wx, wy, wx + 1, wy + 2], fill=(236, 190, 110) if r.random() < 0.7 else (150, 190, 230))
        bx += bw + r.randint(1, 4)
    if rain_ > 0:
        pix.rain(d, t, x0, x1, y0, y1, int(26 * rain_ * (x1 - x0) / 100), lerpc((110, 130, 170), (220, 220, 230), tone), speed=180, slant=-3, ln=4, seed=seed)


# ---------------------------------------------------------------- 旧屋
RW = 560
DOOR = (40, 70, 100, 190)
STAND = (108, 166, 140)     # 矮台 x0, 台面 y, x1
DISH = (124, 163)
PHOTO = (214, 74)           # 合照左上角（14×16）
BED = (166, 330)
SHELF = (338, 396, 98)
WIN = (402, 54, 498, 142)
DESKX = (386, 532)
DESKY = 154
DRAWER = (420, 158, 482, 168)
LAMP = (508, 154)
CUPS = (452, 470)           # 琥珀杯、蓝杯（今夜的摆法）
FLOOR_Y = 190


def room_base(state, t):
    """画旧屋的固有色底图（560×270），返回 (图, 画笔)。state 是这一刻屋里东西的状态"""
    img = Image.new('RGB', (RW, H), WALL); d = ImageDraw.Draw(img); d.fontmode = '1'
    past = state.get('past', False)
    wall = WALL if not past else (222, 196, 166)
    d.rectangle([0, 0, RW, FLOOR_Y], fill=wall)
    # 墙上细细的竖纹和踢脚线
    for x in range(6, RW, 28): d.line([(x, 0), (x, FLOOR_Y - 6)], fill=lerpc(wall, (0, 0, 0), 0.05))
    d.rectangle([0, FLOOR_Y - 6, RW, FLOOR_Y - 1], fill=lerpc(wall, (90, 60, 50), 0.35))
    # 地板
    fl = FLOOR
    d.rectangle([0, FLOOR_Y, RW, H], fill=fl)
    for i, y in enumerate(range(FLOOR_Y + 6, H, 9)):
        d.line([(0, y), (RW, y)], fill=FLOOR_D)
        for x in range((i * 37) % 60, RW, 60): d.line([(x, y - 8), (x, y)], fill=FLOOR_D)
    d.line([(0, FLOOR_Y), (RW, FLOOR_Y)], fill=FLOOR_L)
    # 门
    x0, y0, x1, y1 = DOOR
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1], fill=FRAME)
    op = state.get('door', 0.0)
    d.rectangle([x0, y0, x1, y1], fill=(60, 56, 64) if op > 0 else (170, 128, 96))
    if op > 0:
        hall = state.get('hall', (90, 84, 70))
        d.rectangle([x0, y0, x1, y1], fill=hall)
        dw = int((x1 - x0) * (1 - op))
        d.rectangle([x0, y0, x0 + dw, y1], fill=(170, 128, 96))
    else:
        d.rectangle([x0 + 6, y0 + 8, x1 - 6, y0 + 50], outline=(146, 106, 80))
        d.rectangle([x0 + 6, y0 + 60, x1 - 6, y1 - 10], outline=(146, 106, 80))
        d.rectangle([x1 - 10, y0 + 62, x1 - 7, y0 + 66], fill=(210, 190, 120))
    # 矮台和铁碟
    sx0, sy, sx1 = STAND
    d.rectangle([sx0, sy, sx1, FLOOR_Y + 2], fill=DESK_D)
    d.rectangle([sx0 - 2, sy - 2, sx1 + 2, sy], fill=DESK)
    dish(d, DISH[0], DISH[1], 1, state.get('keys', 1), t, state.get('swing', 0.0), state.get('key_ang', 0.0))
    # 床（回忆）或床的压痕（今夜）
    bx0, bx1 = BED
    if state.get('bed'):
        d.rectangle([bx0, 120, bx0 + 8, FLOOR_Y + 4], fill=DESK)
        d.rectangle([bx0, FLOOR_Y - 18, bx1, FLOOR_Y + 4], fill=DESK_D)
        d.rectangle([bx0 + 8, FLOOR_Y - 30, bx1, FLOOR_Y - 18], fill=(236, 232, 222))
        quilt = state.get('quilt', (204, 120, 100))
        d.rectangle([bx0 + 40, FLOOR_Y - 32, bx1, FLOOR_Y - 18], fill=quilt)
        d.rectangle([bx0 + 40, FLOOR_Y - 32, bx1, FLOOR_Y - 30], fill=lerpc(quilt, (255, 255, 255), 0.3))
        for k in range(bx0 + 52, bx1, 16): d.line([(k, FLOOR_Y - 30), (k, FLOOR_Y - 19)], fill=lerpc(quilt, (0, 0, 0), 0.15))
        d.rectangle([bx0 + 12, FLOOR_Y - 38, bx0 + 36, FLOOR_Y - 30], fill=(248, 246, 238))
        if state.get('pillows', 2) == 2: d.rectangle([bx0 + 12, FLOOR_Y - 46, bx0 + 36, FLOOR_Y - 39], fill=(240, 236, 226))
    elif state.get('marks', True):
        d.rectangle([bx0, FLOOR_Y - 60, bx1, FLOOR_Y - 7], fill=lerpc(wall, (255, 255, 255), 0.12))
        for x in (bx0 + 4, bx1 - 6):
            d.rectangle([x, FLOOR_Y + 4, x + 3, FLOOR_Y + 6], fill=FLOOR_D)
        d.rectangle([bx0, FLOOR_Y + 1, bx1, FLOOR_Y + 3], fill=lerpc(FLOOR, FLOOR_L, 0.6))
    # 合照
    ph = state.get('photo', 'wall')
    px, py = PHOTO
    if ph == 'wall':
        d.rectangle([px - 1, py - 1, px + 14, py + 16], fill=OUT)
        d.rectangle([px, py, px + 13, py + 15], fill=(244, 238, 222))
        img.paste(photo_img(10, 10), (px + 2, py + 2))
        d.rectangle([px + 4, py - 2, px + 9, py], fill=(232, 222, 170))
    elif ph == 'pale':
        d.rectangle([px, py, px + 13, py + 15], fill=lerpc(wall, (255, 255, 255), 0.25))
    # 搁板
    s0, s1, sy_ = SHELF
    d.rectangle([s0, sy_, s1, sy_ + 2], fill=DESK)
    d.rectangle([s0 + 4, sy_ + 3, s0 + 5, sy_ + 8], fill=DESK_D); d.rectangle([s1 - 5, sy_ + 3, s1 - 4, sy_ + 8], fill=DESK_D)
    for item, ix in state.get('shelf', []):
        if item == 'cup': cup(d, s0 + ix, sy_, 'blue')
        elif item == 'bulbbox': bulb_box(d, s0 + ix, sy_)
        elif item == 'bundle': bundle(d, s0 + ix, sy_)
        elif item == 'books':
            for k, c in enumerate([(120, 60, 60), (70, 90, 120), (190, 160, 90)]):
                d.rectangle([s0 + ix + k * 4, sy_ - 12 + k % 2 * 2, s0 + ix + k * 4 + 3, sy_ - 1], fill=c)
        elif item == 'plant':
            d.rectangle([s0 + ix - 3, sy_ - 6, s0 + ix + 3, sy_ - 1], fill=(190, 110, 80))
            for k in range(-4, 5, 2): d.line([(s0 + ix, sy_ - 6), (s0 + ix + k, sy_ - 14 + abs(k))], fill=(80, 150, 90))
    # 窗
    wx0, wy0, wx1, wy1 = WIN
    d.rectangle([wx0 - 4, wy0 - 4, wx1 + 4, wy1 + 4], fill=FRAME)
    d.rectangle([wx0, wy0, wx1, wy1], fill=(30, 36, 60))     # 窗外之后再画
    d.rectangle([wx0 - 6, wy1 + 2, wx1 + 6, wy1 + 6], fill=lerpc(FRAME, (0, 0, 0), 0.1))
    # 书桌
    dx0, dx1 = DESKX
    d.rectangle([dx0, DESKY, dx1, DESKY + 4], fill=DESK_L)
    d.rectangle([dx0, DESKY + 4, dx1, DESKY + 16], fill=DESK)
    d.rectangle([dx0 + 4, DESKY + 16, dx0 + 8, FLOOR_Y + 8], fill=DESK_D)
    d.rectangle([dx1 - 8, DESKY + 16, dx1 - 4, FLOOR_Y + 8], fill=DESK_D)
    a0, a1, a2, a3 = DRAWER
    dro = state.get('drawer', 0)
    d.rectangle([a0, a1 + dro // 3, a2, a3 + dro // 3], fill=DESK_L if dro else DESK)
    d.rectangle([a0, a1 + dro // 3, a2, a3 + dro // 3], outline=DESK_D)
    d.rectangle([(a0 + a2) // 2 - 2, (a1 + a3) // 2 - 1 + dro // 3, (a0 + a2) // 2 + 2, (a1 + a3) // 2 + dro // 3], fill=(220, 200, 150))
    # 桌上：车票、灯、杯子
    if state.get('tickets'):
        for k in range(state['tickets']):
            d.rectangle([396 + k * 3, DESKY - 2 - k, 412 + k * 3, DESKY - 1 - k], fill=(236, 214, 170) if k % 2 else (200, 220, 236))
    if state.get('clutter', 0) > 0:
        n = int(state['clutter'] * 5)
        for k in range(n):
            c = [(200, 120, 90), (120, 160, 120), (230, 220, 190), (110, 120, 170), (220, 180, 90)][k]
            hgt = [10, 6, 3, 12, 5][k]
            d.rectangle([394 + k * 9, DESKY - hgt, 400 + k * 9, DESKY - 1], fill=c)
    if state.get('phone_desk'):
        d.rectangle([420, DESKY - 2, 432, DESKY - 1], fill=(30, 30, 40))
    if state.get('cloth_desk'):
        plaid(d, (482, DESKY - 3, 500, DESKY), 1, moon=False)
    for kind, x in state.get('cups', [('amber', CUPS[0]), ('blue', CUPS[1])]):
        cup(d, x, DESKY, kind, 1, state.get('steam', 0.0), t, state.get('handle', 1))
    lamp_at = state.get('lamp', LAMP)
    tip = None
    if lamp_at:
        tip = lamp_obj(d, lamp_at[0], lamp_at[1], 1, state.get('lamp_on', 0.0), -1)
        # 灯线垂到桌边，线控开关挂在那儿
        sx_ = lamp_at[0] + 10
        d.line([(sx_, lamp_at[1] - 1), (sx_ + 4, DESKY + 10), (sx_ + 2, DESKY + 26)], fill=(28, 28, 32))
        d.rectangle([sx_ + 1, DESKY + 20, sx_ + 5, DESKY + 28], fill=(24, 24, 28))
    # 桌下的纸箱、行李箱
    if state.get('box_under'):
        box(d, 396, 168, 438, FLOOR_Y + 6)
    if state.get('box_floor'):
        bx_ = state['box_floor']
        box(d, bx_ - 22, 162, bx_ + 22, FLOOR_Y + 8, open_=1.0)
    if state.get('case'):
        cx_, mode = state['case']
        if mode == 'stand': suitcase(d, cx_, FLOOR_Y + 6, 1)
        elif mode == 'open': suitcase(d, cx_, FLOOR_Y + 10, 1, open_=True, lay=True)
        elif mode == 'handle': suitcase(d, cx_, FLOOR_Y + 6, 1, handle=1.0)
    return img, d, tip


def bundle(d, x, y, s=1, moon=True):
    """绿格布包"""
    d.ellipse([x - 7 * s, y - 7 * s, x + 7 * s, y], fill=PLAID)
    d.line([(x - 5 * s, y - 5 * s), (x + 5 * s, y - 2 * s)], fill=PLAID_D)
    d.line([(x - 3 * s, y - 1), (x + 3 * s, y - 6 * s)], fill=PLAID_D)
    d.polygon([(x, y - 7 * s), (x - 2 * s, y - 10 * s), (x + 3 * s, y - 9 * s)], fill=PLAID_L)
    if moon: d.point((x + 4 * s, y - 2 * s), fill=MOONY)


def room(img, t, state, cam=50, amb='now', lamp_on=0.0, actors=None, outside=None, extra_lights=(), post=None, cone=True):
    """画一帧旧屋。actors(img, d, ox) 在光照前画人物（ox 是 560 底图到屏幕的偏移，画在屏幕坐标上）；
    outside(img, d, box, t) 画窗外；post(img, d, ox) 在光照之后画发光的东西"""
    st = dict(state); st['lamp_on'] = lamp_on
    base, bd, tip = room_base(st, t)
    cam = int(round(cam))
    img.paste(base.crop((cam, 0, cam + W, H)))
    d = ImageDraw.Draw(img); d.fontmode = '1'
    if actors: actors(img, d, -cam)
    lights = list(extra_lights)
    cones = []
    if tip and lamp_on > 0:
        lx, ly = tip[0] - cam, tip[1]
        lights.append((lx, ly, 170, 120, 0.85 * lamp_on, WARM))
        lights.append((lx, ly, 60, 50, 0.7 * lamp_on, WARM))
        if cone:
            cones.append(((int(lx), int(ly), 4, int(lx - 50), 70, FLOOR_Y + 40, 4), 0.45 * lamp_on, WARM))
    light(img, amb, lights, cones)
    # 窗外（自己发光，不受屋里环境光影响）
    wx0, wy0, wx1, wy1 = WIN
    wb = (wx0 - cam, wy0, wx1 - cam + 1, wy1 + 1)
    if outside is None:
        outside_night(img, d, wb, t, 1.0)
    else:
        outside(img, d, wb, t)
    # 窗框十字和窗帘
    fc = emit(FRAME, amb)
    if lamp_on > 0: fc = lerpc(fc, (255, 200, 140), 0.3 * lamp_on)
    mx = (wx0 + wx1) // 2 - cam
    d.rectangle([mx - 1, wy0, mx + 1, wy1], fill=fc)
    d.rectangle([wx0 - cam, (wy0 + wy1) // 2 - 1, wx1 - cam, (wy0 + wy1) // 2 + 1], fill=fc)
    cur = state.get('curtain', None)
    if cur is not None:
        cc = emit(state.get('curtain_col', (226, 210, 180)), amb)
        if lamp_on > 0: cc = lerpc(cc, (250, 196, 130), 0.5 * lamp_on)
        cw = int((wx1 - wx0) / 2 * (1 - cur)) + 6
        d.rectangle([wx0 - cam - 6, wy0 - 6, wx0 - cam - 6 + cw, wy1 + 8], fill=cc)
        d.rectangle([wx1 - cam + 6 - cw, wy0 - 6, wx1 - cam + 6, wy1 + 8], fill=cc)
        for k in range(0, cw, 4):
            d.line([(wx0 - cam - 6 + k, wy0 - 6), (wx0 - cam - 6 + k, wy1 + 8)], fill=lerpc(cc, (0, 0, 0), 0.12))
            d.line([(wx1 - cam + 6 - k, wy0 - 6), (wx1 - cam + 6 - k, wy1 + 8)], fill=lerpc(cc, (0, 0, 0), 0.12))
    if tip and lamp_on > 0:
        glow(img, tip[0] - cam, tip[1], 26, (255, 214, 140), 0.5 * lamp_on)
        d.ellipse([tip[0] - cam - 3, tip[1] - 3, tip[0] - cam + 3, tip[1] + 1], fill=lerpc((120, 90, 60), (255, 250, 220), lamp_on))
    if post: post(img, d, -cam)
    return tip


# ---------------------------------------------------------------- 大手（特写）
def hand(img, x, y, s=4, kind='grip', flip=False, sleeve=(36, 58, 96), patch=False, skin=SKIN, skin_s=SKIN_S, ang=0):
    """特写的大手，(x, y) 是手腕中点，默认手指朝右。kind：grip 握拳拇指在上 / press 拇指压下 / flat 手掌平放 /
    pinch 捏着东西 / open 张开 / point 食指伸出。先画在小图上描一圈深色轮廓再贴上去"""
    lw, lh = 32 * s, 20 * s
    lay = Image.new('RGBA', (lw, lh)); d = ImageDraw.Draw(lay)
    ox, oy = 16 * s, 10 * s
    R = lambda ax, ay, bx, by, c: d.rectangle([ox + ax * s, oy + ay * s, ox + bx * s - 1 + s, oy + by * s - 1 + s], fill=c + (255,))
    R(-16, -5, -3, 5, sleeve)
    R(-16, -5, -3, -4, lerpc(sleeve, (255, 255, 255), 0.15))
    R(-16, 4, -3, 5, lerpc(sleeve, (0, 0, 0), 0.25))
    R(-4, -5, -3, 5, lerpc(sleeve, (0, 0, 0), 0.3))
    if patch: R(-8, 1, -5, 4, pix.PATCH)
    nail = lerpc(skin, (255, 255, 255), 0.35)
    if kind in ('grip', 'press'):
        R(-2, -4, 5, 4, skin)                 # 掌
        R(5, -3, 8, 4, skin)                  # 弯着的四指
        for k in range(3): R(6, -2 + 2 * k, 8, -2 + 2 * k, skin_s)
        R(-2, 3, 5, 4, skin_s)
        if kind == 'grip': R(0, -6, 6, -5, skin); R(6, -6, 6, -6, nail)          # 拇指搭在上面
        else: R(1, -5, 7, -4, skin); R(7, -4, 7, -3, nail)                     # 拇指往下压
    elif kind == 'flat':
        R(-2, -3, 6, 3, skin)
        for k in range(4): R(6, -3 + k * 2, 12 - abs(k - 1), -2 + k * 2, skin)
        for k in range(4): R(12 - abs(k - 1), -3 + k * 2, 12 - abs(k - 1), -3 + k * 2, nail)
        R(1, -5, 5, -4, skin)
        R(-2, 2, 11, 3, skin_s)
    elif kind == 'pinch':
        R(-2, -3, 5, 3, skin)
        R(5, -4, 10, -3, skin); R(10, -4, 10, -4, nail)
        R(5, 0, 9, 2, skin); R(5, 2, 9, 2, skin_s)
        R(3, 3, 7, 4, skin_s)
    elif kind == 'open':
        R(-2, -4, 5, 4, skin)
        for k in range(4): R(5, -4 + k * 2, 11 - abs(k - 1), -3 + k * 2, skin)
        R(1, -8, 3, -5, skin)
    elif kind == 'point':
        R(-2, -3, 5, 4, skin)
        R(5, -3, 13, -2, skin); R(13, -3, 13, -3, nail)
        R(5, -1, 8, 4, skin); R(6, 0, 8, 4, skin_s)
        R(1, -5, 5, -4, skin)
    lay = pix.outline(lay, pix.OUT)
    if flip: lay = lay.transpose(Image.FLIP_LEFT_RIGHT); ox = lw - ox
    if ang: lay = lay.rotate(ang, Image.NEAREST, center=(ox, oy))
    img.paste(lay, (int(round(x - ox)), int(round(y - oy))), lay)


# ---------------------------------------------------------------- 楼和巷口（仰视）
BLD = (70, 18, 410, 236)          # 楼的外墙
WIN_COLS = [96, 156, 216, 276, 336]
WIN_ROWS = [40, 96, 152]
OURS = (2, 1)                     # 那一格窗：第 3 列第 2 行（216, 96）
WIN_W, WIN_H = 34, 36


def our_window():
    return WIN_COLS[OURS[0]], WIN_ROWS[OURS[1]]


def building(img, d, t, tone=0.0, lit_ours=1.0, others=None, seed=3, rain_=1.0, season=None, wet=1.0, ours_col=None,
             sun=0.0, curtain=0.0, empty_ours=False):
    """巷口仰看那栋旧楼。tone 0 深夜 → 1 清晨；others: 函数 (列, 行) → 亮度 0..1；season: 'rain'/'leaf'/'frost'"""
    sk_top = lerpc((10, 14, 30), (150, 172, 206), tone)
    sk_bot = lerpc((34, 42, 74), (252, 210, 164), tone)
    pix.sky(img, ((0, sk_top), (1, sk_bot)), 0, 240)
    if tone < 0.6: pix.stars(d, t, 120, 1 - tone / 0.6, n=60)
    if sun > 0:
        glow(img, 440, 70, 90, (255, 214, 150), 0.45 * sun)
    # 远处的楼影
    pix.city(img, d, 210, 7, 0, lerpc((18, 22, 40), (120, 124, 150), tone), None, 40, 120, 0.0, t, blink=False)
    x0, y0, x1, y1 = BLD
    wall = lerpc((44, 50, 70), (176, 164, 160), tone)
    d.rectangle([x0, y0, x1, y1], fill=wall)
    for y in range(y0 + 6, y1, 8):          # 砖缝
        d.line([(x0, y), (x1, y)], fill=lerpc(wall, (0, 0, 0), 0.12))
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y0], fill=lerpc(wall, (0, 0, 0), 0.25))
    # 水管和空调
    d.rectangle([x1 - 12, y0, x1 - 10, y1], fill=lerpc(wall, (0, 0, 0), 0.3))
    for (cx, cy) in [(126, 86), (306, 142), (366, 30)]:
        d.rectangle([cx, cy, cx + 14, cy + 9], fill=lerpc((150, 150, 160), wall, 0.4)); d.ellipse([cx + 3, cy + 2, cx + 9, cy + 8], outline=wall)
    for i, wx in enumerate(WIN_COLS):
        for j, wy in enumerate(WIN_ROWS):
            ours = (i, j) == OURS
            if ours:
                k = lit_ours
                base_ = lerpc((20, 24, 40), (250, 196, 112), k) if not empty_ours else lerpc(lerpc((40, 46, 66), (232, 214, 186), tone), (255, 226, 170), 0.6 * sun)
                if ours_col: base_ = ours_col
            else:
                k = others(i, j) if others else 0.0
                base_ = lerpc(lerpc((20, 24, 40), (120, 130, 150), tone * 0.8), (232, 182, 108), k)
            d.rectangle([wx - 2, wy - 2, wx + WIN_W + 2, wy + WIN_H + 2], fill=lerpc(wall, (0, 0, 0), 0.35))
            d.rectangle([wx, wy, wx + WIN_W, wy + WIN_H], fill=base_)
            if ours and empty_ours and sun > 0:            # 晨光穿过空了的窗
                d.polygon([(wx, wy), (wx + 12, wy), (wx + WIN_W, wy + 20), (wx + WIN_W, wy + WIN_H), (wx + 22, wy + WIN_H)],
                          fill=lerpc(base_, (255, 236, 196), 0.6 * sun))
            if ours and curtain > 0 and not empty_ours:
                d.rectangle([wx, wy, wx + 8, wy + WIN_H], fill=lerpc(base_, (180, 120, 80), 0.4))
                d.rectangle([wx + WIN_W - 8, wy, wx + WIN_W, wy + WIN_H], fill=lerpc(base_, (180, 120, 80), 0.4))
            d.line([(wx + WIN_W // 2, wy), (wx + WIN_W // 2, wy + WIN_H)], fill=lerpc(wall, (0, 0, 0), 0.35))
            d.line([(wx, wy + WIN_H // 2), (wx + WIN_W, wy + WIN_H // 2)], fill=lerpc(wall, (0, 0, 0), 0.35))
            d.rectangle([wx - 3, wy + WIN_H + 2, wx + WIN_W + 3, wy + WIN_H + 4], fill=lerpc(wall, (255, 255, 255), 0.15))
            if ours and k > 0.2 and not empty_ours:
                # 屋里那盏红灯的剪影
                lx, ly = wx + WIN_W - 9, wy + WIN_H - 3
                d.rectangle([lx - 3, ly - 1, lx + 3, ly], fill=(110, 40, 40))
                d.polygon([(lx - 1, ly - 9), (lx + 3, ly - 10), (lx - 5, ly - 4), (lx - 1, ly - 3)], fill=(170, 60, 56))
    # 门洞
    d.rectangle([224, 196, 256, y1], fill=lerpc((20, 20, 30), (70, 64, 70), tone))
    d.rectangle([220, 192, 260, 196], fill=lerpc(wall, (0, 0, 0), 0.3))
    # 巷子地面
    gy = 236
    g = lerpc((26, 30, 46), (130, 120, 120), tone)
    d.rectangle([0, gy, W, H], fill=g)
    for y in range(gy + 4, H, 7): d.line([(0, y), (W, y)], fill=lerpc(g, (0, 0, 0), 0.2))
    # 左右两边更近的墙
    side = lerpc((14, 16, 28), (90, 92, 110), tone)
    d.polygon([(0, 0), (52, 0), (52, 250), (0, H)], fill=side)
    d.polygon([(W, 0), (428, 0), (428, 250), (W, H)], fill=side)
    d.line([(0, 34), (W, 28)], fill=lerpc((10, 10, 20), (70, 70, 90), tone))     # 电线
    d.line([(0, 44), (W, 50)], fill=lerpc((10, 10, 20), (70, 70, 90), tone))
    if lit_ours > 0 and not empty_ours:
        wx, wy = our_window()
        glow(img, wx + WIN_W / 2, wy + WIN_H / 2, 46, (255, 196, 120), 0.35 * lit_ours)
        # 地面水洼里的倒影
        if wet > 0:
            for k in range(0, 24, 2):
                if (k + int(t * 6)) % 5:
                    d.line([(wx + 6 + k % 6, gy + 8 + k), (wx + WIN_W - 6 - k % 4, gy + 8 + k)], fill=lerpc(g, (250, 190, 110), 0.55 * lit_ours * (1 - k / 26)))
    if season == 'rain' or (season is None and rain_ > 0 and tone < 0.5):
        pix.rain(d, t, 0, W, 0, H, int(90 * rain_), lerpc((100, 120, 170), (200, 200, 220), tone), speed=240, slant=-4, ln=6, seed=seed)
    elif season == 'leaf':
        props.leaves(d, t, n=26, speed=26, wind=30, seed=seed)
    elif season == 'frost':
        pix.snow(d, t, n=50, speed=10, col=(220, 230, 250), seed=seed)
        d.rectangle([0, gy, W, gy + 2], fill=(200, 210, 230))


# ---------------------------------------------------------------- 站台和列车
PLAT_Y = 206


def platform(img, d, t, tone=0.0, amb=None):
    """站台：远处的雨棚、柱子和站牌。tone 0 白天阴天 → 1 傍晚"""
    sk = lerpc((150, 164, 186), (230, 160, 130), tone)
    pix.sky(img, ((0, lerpc(sk, (90, 100, 130), 0.4)), (1, sk)), 0, PLAT_Y)
    pix.city(img, d, 150, 21, 0, lerpc((110, 120, 146), (120, 90, 110), tone), None, 20, 70, 0.0, t, blink=False)
    # 对面的轨道
    d.rectangle([0, 150, W, 160], fill=(80, 80, 92))
    d.rectangle([0, 160, W, PLAT_Y], fill=(64, 62, 72))
    d.line([(0, 168), (W, 168)], fill=(130, 130, 140)); d.line([(0, 178), (W, 178)], fill=(130, 130, 140))
    # 站台面
    d.rectangle([0, PLAT_Y, W, H], fill=(150, 146, 140))
    d.rectangle([0, PLAT_Y, W, PLAT_Y + 4], fill=(236, 206, 80))
    for x in range(0, W, 6): d.point((x + 2, PLAT_Y + 2), fill=(200, 170, 60))
    for y in range(PLAT_Y + 14, H, 12): d.line([(0, y), (W, y)], fill=(132, 128, 124))
    # 雨棚
    d.rectangle([0, 0, W, 14], fill=(70, 76, 90))
    d.rectangle([0, 14, W, 16], fill=(50, 54, 66))
    for x in (40, 200, 360):
        d.rectangle([x, 16, x + 6, PLAT_Y], fill=(96, 100, 116)); d.rectangle([x, 16, x + 1, PLAT_Y], fill=(130, 134, 150))
    d.rectangle([250, 30, 330, 44], fill=(40, 70, 120)); d.rectangle([252, 32, 328, 42], fill=(60, 96, 150))
    pix.text(img, '月 台 2', 290, 37, col=(240, 240, 250), font=FONT_S, shadow=False, out=None)


def train_car(img, d, x, base, t, s=1, inside=None, lit=0.3, cars=3):
    """通勤列车（侧面），x 是车尾左端。inside(img, d, 窗框) 往某扇窗里画人；返回各车窗框列表"""
    wins = []
    car_l = 200 * s
    for c in range(cars):
        cx0 = int(round(x + c * (car_l + 6 * s)))
        cx1 = cx0 + car_l
        if cx1 < -10 or cx0 > W + 10: continue
        top, bot = base - 78 * s, base - 8 * s
        d.rounded_rectangle([cx0, top, cx1, bot], 6 * s, fill=(222, 226, 232))
        d.rectangle([cx0, bot - 22 * s, cx1, bot - 17 * s], fill=(60, 110, 180))
        d.rectangle([cx0, bot - 16 * s, cx1, bot - 15 * s], fill=(236, 206, 80))
        d.rectangle([cx0, top, cx1, top + 3 * s], fill=(180, 186, 196))
        for k, wx in enumerate(range(cx0 + 14 * s, cx1 - 30 * s, 46 * s)):
            box_ = (wx, top + 14 * s, wx + 34 * s, top + 40 * s)
            d.rectangle([box_[0] - s, box_[1] - s, box_[2] + s, box_[3] + s], fill=(80, 84, 96))
            d.rectangle(box_, fill=lerpc((90, 110, 130), (230, 214, 170), lit))
            d.line([(box_[0] + 4 * s, box_[3] - 3 * s), (box_[0] + 16 * s, box_[1] + 3 * s)], fill=lerpc((140, 160, 180), (250, 240, 210), lit))
            wins.append(box_)
        # 车门
        dx = cx1 - 30 * s
        d.rectangle([dx, top + 8 * s, dx + 22 * s, bot], fill=(200, 204, 212))
        d.rectangle([dx + 3 * s, top + 14 * s, dx + 19 * s, top + 36 * s], fill=lerpc((90, 110, 130), (230, 214, 170), lit))
        d.line([(dx + 11 * s, top + 8 * s), (dx + 11 * s, bot)], fill=(150, 154, 164))
        # 车轮
        for wx in (cx0 + 24 * s, cx0 + 44 * s, cx1 - 44 * s, cx1 - 24 * s):
            d.ellipse([wx - 6 * s, bot - 4 * s, wx + 6 * s, base + 2 * s], fill=(40, 40, 46))
        d.rectangle([cx0 + 4 * s, bot, cx1 - 4 * s, bot + 4 * s], fill=(60, 60, 70))
    if inside: inside(img, d, wins)
    return wins


# ---------------------------------------------------------------- 手机界面
def phone(img, d, cx, cy, s=1, screen='chat', t=0.0, glow_=1.0, thumb=None, send_on=0.0, items=None):
    """大手机，(cx, cy) 是中心。screen：'chat' 旧对话 / 'call' 来电 / 'missed' 未接 / 'off' 黑屏 / 'album' 相册"""
    w, h = 64 * s, 120 * s
    x0, y0 = cx - w // 2, cy - h // 2
    d.rounded_rectangle([x0 - 2, y0 - 2, x0 + w + 2, y0 + h + 2], 8 * s, fill=(20, 20, 28))
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], 7 * s, fill=(40, 40, 52))
    sx0, sy0, sx1, sy1 = x0 + 4 * s, y0 + 10 * s, x0 + w - 4 * s, y0 + h - 10 * s
    if screen == 'off' or glow_ <= 0:
        d.rectangle([sx0, sy0, sx1, sy1], fill=(14, 16, 24))
        d.line([(sx0 + 4, sy0 + 10), (sx0 + 20, sy0 + 2)], fill=(40, 44, 60))
        return (sx0, sy0, sx1, sy1)
    bg = lerpc((14, 16, 24), (226, 232, 240), glow_)
    d.rectangle([sx0, sy0, sx1, sy1], fill=bg)
    ink = lambda c: lerpc((14, 16, 24), c, glow_)
    if screen in ('chat', 'album'):
        d.rectangle([sx0, sy0, sx1, sy0 + 12 * s], fill=ink((200, 208, 220)))
        d.ellipse([sx0 + 3 * s, sy0 + 3 * s, sx0 + 9 * s, sy0 + 9 * s], fill=ink((172, 74, 60)))     # 她的头像：砖红色块
        d.rectangle([sx0 + 12 * s, sy0 + 5 * s, sx0 + 30 * s, sy0 + 7 * s], fill=ink((120, 126, 140)))
        y = sy0 + 18 * s
        for side, ln in (items or [(0, 30), (1, 22), (0, 18), (1, 34), (0, 26)]):
            if side == 0:
                d.rounded_rectangle([sx0 + 3 * s, y, sx0 + 3 * s + ln * s, y + 8 * s], 3 * s, fill=ink((255, 255, 255)))
            else:
                d.rounded_rectangle([sx1 - 3 * s - ln * s, y, sx1 - 3 * s, y + 8 * s], 3 * s, fill=ink((150, 214, 140)))
            y += 12 * s
        if thumb is not None:
            tw, th = thumb.size
            img.paste(thumb, (int(sx1 - 3 * s - tw), int(sy1 - 18 * s - th)))
        # 输入栏和发送键
        d.rectangle([sx0, sy1 - 14 * s, sx1, sy1], fill=ink((210, 216, 226)))
        d.rounded_rectangle([sx0 + 3 * s, sy1 - 11 * s, sx1 - 18 * s, sy1 - 3 * s], 3 * s, fill=ink((255, 255, 255)))
        sc = lerpc(ink((150, 156, 170)), (80, 200, 110), send_on)
        d.rounded_rectangle([sx1 - 15 * s, sy1 - 11 * s, sx1 - 3 * s, sy1 - 3 * s], 3 * s, fill=sc)
        if send_on > 0.5:
            glow(img, sx1 - 9 * s, sy1 - 7 * s, 14 * s, (120, 255, 150), 0.25 * (0.6 + 0.4 * math.sin(t * 6)))
        d.polygon([(sx1 - 12 * s, sy1 - 9 * s), (sx1 - 6 * s, sy1 - 7 * s), (sx1 - 12 * s, sy1 - 5 * s)], fill=(255, 255, 255))
    elif screen in ('call', 'missed'):
        d.rectangle([sx0, sy0, sx1, sy1], fill=ink((44, 54, 80)))
        r = 10 * s
        cxs, cys = (sx0 + sx1) // 2, sy0 + 30 * s
        if screen == 'call':
            for k in range(3):
                rr = r + ((t * 1.5 + k / 3) % 1) * 14 * s
                d.ellipse([cxs - rr, cys - rr, cxs + rr, cys + rr], outline=ink((120, 140, 190)))
        d.ellipse([cxs - r, cys - r, cxs + r, cys + r], fill=ink((172, 74, 60)))
        d.rectangle([cxs - 14 * s, cys + 18 * s, cxs + 14 * s, cys + 21 * s], fill=ink((200, 206, 220)))
        if screen == 'call':
            d.ellipse([cxs - 22 * s, sy1 - 22 * s, cxs - 10 * s, sy1 - 10 * s], fill=ink((230, 70, 70)))
            d.ellipse([cxs + 10 * s, sy1 - 22 * s, cxs + 22 * s, sy1 - 10 * s], fill=ink((80, 200, 110)))
        else:
            d.ellipse([cxs - 6 * s, sy1 - 22 * s, cxs + 6 * s, sy1 - 10 * s], fill=ink((230, 70, 70)))
            d.line([(cxs - 3 * s, sy1 - 19 * s), (cxs + 3 * s, sy1 - 13 * s)], fill=(255, 255, 255), width=s)
    return (sx0, sy0, sx1, sy1)


def signal_icon(d, x, y, bars, s=2, col=(255, 230, 160), dim=(80, 76, 90)):
    """信号格：bars 0..4"""
    for k in range(4):
        hgt = (k + 1) * 3 * s
        c = col if k < bars else dim
        d.rectangle([x + k * 4 * s, y - hgt, x + k * 4 * s + 2 * s, y], fill=c)


def heart(d, cx, cy, s, col, out=None):
    poly = pix.heart_poly(cx, cy, s)
    if out: d.polygon([(px + 1, py + 1) for px, py in poly], fill=out)
    d.polygon(poly, fill=col)


# ---------------------------------------------------------------- 镜头
def zoomv(img, z, cx, cy):
    """把画面以 (cx, cy) 为中心放大 z 倍（最近邻，保持像素感）"""
    if z <= 1.001: return
    w_, h_ = W / z, H / z
    x0 = clamp(cx - w_ / 2, 0, W - w_); y0 = clamp(cy - h_ / 2, 0, H - h_)
    crop = img.crop((int(round(x0)), int(round(y0)), int(round(x0 + w_)), int(round(y0 + h_))))
    img.paste(crop.resize((W, H), Image.NEAREST))


def layer(w, h):
    im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im); d.fontmode = '1'
    return im, d


def neighbor(img, x, y, s=2, ph=0, flip=False, col=(96, 92, 100), bag=True):
    """邻居：只有背影，提着菜袋"""
    props.person_s(img, 'boy', x, y, s, age='now', view='back', pose='walk', ph=ph, tint=col, flip=flip)
    if bag:
        d = ImageDraw.Draw(img)
        bx = x + (8 if not flip else -14) * s / 2
        d.rectangle([bx, y - 18 * s / 2, bx + 6 * s / 2 * 2, y - 8 * s / 2], fill=(214, 214, 200))
        d.line([(bx + 3, y - 18 * s / 2 - 4), (bx + 9, y - 18 * s / 2 - 4)], fill=(170, 170, 160))
        d.point((bx + 4, y - 19 * s / 2), fill=(90, 160, 80))
