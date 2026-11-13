"""曾经是情侣 · 第二段副歌和片尾。

三段间奏的哼唱：两座楼顶上的人看着同一场烟花；八音盒上转圈的两个小人；湖上升起满天的孔明灯。
墙上那张合照慢慢褪成旧照片，玻璃裂开；天亮时他坐在码头尽头等明天；手心里捧着的一颗心飘起来，变成一盏心形的灯；
灯升成天上的一颗星，两人在河的两岸各自转身走远，断掉的那截红线顺着河漂走。
片尾回到最开始的山坡：树下没有人了，风筝挂在树枝上；云又慢慢拼成片名，然后淡出。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
from props import *          # noqa: F401,F403
from pix import (W, H, FONT, FONT_S, OUT, SKIN, SKIN_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng,
                 sky, stars, person, wph, put, twinkle, sparkle, hills, moon, cloud, darken, dither_fade, grade, vig, vgrad, BAYER, bayer)
from sc_a import dpaste, winds, hill_world, hill_y, title_glyph_pos, TITLE_Y, kite_xy
from sc_b import canvas

YY, XX = np.mgrid[0:H, 0:W]
FW_COLS = [(255, 110, 140), (255, 210, 100), (120, 220, 255), (190, 150, 255), (140, 255, 180)]


# ================================================================ 间奏（一）：两座楼顶，同一场烟花
def rooftop(d, x0, x1, y, col=(26, 22, 44), edge=(50, 44, 76)):
    d.rectangle([x0, y, x1, H], fill=col)
    d.rectangle([x0 - 2, y - 3, x1 + 2, y], fill=edge)
    for x in range(x0 + 4, x1 - 2, 6): d.line([(x, y - 9), (x, y - 3)], fill=edge)
    d.line([(x0, y - 9), (x1, y - 9)], fill=edge)


def s_nana1(img, d, lt, dur, T, A):
    sky(img, ((0, (6, 6, 22)), (0.6, (22, 18, 54)), (1, (52, 34, 80))), 0, H)
    stars(d, T, 200, 1.0, 160)
    pix.city(img, d, 270, 3, 0, (20, 16, 40), (255, 200, 120), 60, 160, 0.3, T, 10, 24)
    bs = beats_in(T - lt - 1.0, T - lt + dur)
    for j, b in enumerate(bs):
        r = rng(int(b * 10))
        pix.firework(img, d, T, b - 0.5, r.uniform(150, 330), r.uniform(50, 100), FW_COLS[j % len(FW_COLS)], r.uniform(50, 72), 1.8, 40, j)
        pix.firework(img, d, T, b + 0.05, r.uniform(120, 360), r.uniform(40, 120), FW_COLS[(j + 2) % len(FW_COLS)], r.uniform(26, 40), 1.4, 28, j + 50)
    flash = max([0.0] + [1 - (T - b) / 0.25 for b in bs if 0 <= T - b < 0.25])
    rooftop(d, -10, 130, 196); rooftop(d, 350, 490, 186)
    for x0 in (10, 70): d.rectangle([x0, 210, x0 + 16, 226], fill=(255, 210, 130) if (x0 // 10) % 2 else (40, 34, 60))
    for x0 in (380, 440): d.rectangle([x0, 204, x0 + 16, 220], fill=(255, 210, 130))
    shade = (0.6 + 0.4 * flash, 0.6 + 0.3 * flash, 0.8 + 0.2 * flash)
    person(img, 'boy', 80, 196, 'old', 'side', 'stand', 0, 'smile', s=2, shade=shade)
    person(img, 'girl', 400, 186, 'old', 'side', 'stand', 0, 'smile', s=2, flip=True, shade=shade)
    notes(img, d, T, 12, (0, 40, W, 200), 1)
    vig(img, 0.4, (4, 4, 14))


# ================================================================ 墙上的合照褪色、玻璃裂开
@lru_cache(None)
def couple_picture(w=220, h=150):
    im = Image.new('RGB', (w, h)); d = ImageDraw.Draw(im)
    sky(im, SUNSET, 0, h)
    glow(im, w / 2, h - 30, 70, (255, 200, 160), 0.5)
    d.ellipse([w / 2 - 20, h - 54, w / 2 + 20, h - 14], fill=(255, 236, 200))
    pix.hills(d, h - 30, 4, 0.03, 1.0, (176, 108, 150))
    cloud(d, 10, 20, 1.2, (255, 214, 214), (236, 160, 176)); cloud(d, 150, 34, 1.0, (255, 214, 214), (236, 160, 176))
    kite(d, w - 30, 30, 1.0, 0.0)
    bust(im, d, 'boy', w / 2 + 34, 40, 3, 'happy', 'young')
    bust(im, d, 'girl', w / 2 - 34, 44, 3, 'laugh', 'young')
    heart(im, d, w / 2, 26, 0.55, RED, RED_L)
    return im


CRACK = [[(0, 0), (-16, 10), (-26, 8), (-44, 22)], [(0, 0), (12, 16), (10, 30), (26, 44), (24, 60)], [(0, 0), (20, -6), (40, -2)],
         [(-16, 10), (-14, 26), (-24, 40)], [(12, 16), (30, 18)]]


def s_couple(img, d, lt, dur, T, A):
    img.paste((228, 206, 184), (0, 0, W, H))
    for x in range(0, W, 20):
        d.line([(x, 0), (x, H)], fill=(220, 196, 174))
        for y in range(10, H, 40): put(img, 'heart', x + 10, y + (x // 20 % 2) * 20, 1, tint=(236, 214, 194))
    tfill(img, 'polygon', [(0, 0), (90, 0), (300, H), (120, H)], (255, 246, 220), 0.18)
    for j in range(24):                                     # 光里的灰尘
        r = rng(j + 3)
        x = r.uniform(40, 260) + 6 * math.sin(T * 0.5 + j); y = (r.uniform(0, H) - T * 4) % H
        d.point((x, y), fill=(255, 250, 230))
    zoom = 1 + 0.06 * ease(clamp(lt / dur))
    pw, ph = int(220 * zoom), int(150 * zoom)
    old = ease(span(lt, 0.4, dur - 0.6))
    pic = sepia(couple_picture(), old * 0.85)
    pic = pic.resize((pw, ph), Image.NEAREST)
    cx, cy = 240, 120
    x0, y0 = int(cx - pw / 2), int(cy - ph / 2)
    d.line([(cx, y0 - 14), (x0 + 20, y0 - 2)], fill=(90, 70, 60)); d.line([(cx, y0 - 14), (x0 + pw - 20, y0 - 2)], fill=(90, 70, 60))
    d.ellipse([cx - 2, y0 - 16, cx + 2, y0 - 12], fill=(140, 120, 100))
    d.rectangle([x0 - 12, y0 - 12, x0 + pw + 12, y0 + ph + 12], fill=(140, 92, 60), outline=OUT)
    d.rectangle([x0 - 7, y0 - 7, x0 + pw + 7, y0 + ph + 7], fill=(176, 120, 80))
    d.rectangle([x0 - 2, y0 - 2, x0 + pw + 1, y0 + ph + 1], fill=OUT)
    img.paste(pic, (x0, y0))
    d.line([(x0 + 10, y0 + 6), (x0 + 40, y0 + 6)], fill=(255, 255, 255))           # 玻璃反光
    d.line([(x0 + 10, y0 + 9), (x0 + 24, y0 + 9)], fill=(255, 255, 255))
    # 一根红线从相框角上垂下来
    thread(img, d, (x0 + pw + 8, y0 + ph + 8), (x0 + pw + 4, y0 + ph + 50), -6, RED)
    # 最后玻璃裂开
    bs = beats_in(T - lt + dur - 1.4, T - lt + dur)
    ct = (bs[0] - (T - lt)) if bs else dur - 0.8
    if lt > ct:
        k = lt - ct
        ox, oy = x0 + pw * 0.66, y0 + ph * 0.36
        g = eout(clamp(k / 0.25))
        for seg in CRACK:
            pts = [(ox + x * zoom * g, oy + y * zoom * g) for x, y in seg]
            d.line(pts, fill=(255, 255, 255), width=1)
            d.line([(x + 1, y + 1) for x, y in pts], fill=(120, 110, 110))
        if k < 0.1: pix.blend_box(img, (0, 0, W, H), (255, 255, 255), np.full((H, W), 0.5))
        props.shake(img, k, 3, 0.3)
    vig(img, 0.45, (40, 24, 20))


# ================================================================ 间奏（二）：八音盒
def s_nana2(img, d, lt, dur, T, A):
    sky(img, ((0, (40, 20, 50)), (1, (90, 50, 90))), 0, H)
    props.bokeh(img, T, 18, [(255, 160, 190), (255, 220, 160), (190, 160, 255)], 11, 0.25, 10, 26, 5)
    d.rectangle([0, 214, W, H], fill=(110, 70, 70)); d.line([(0, 214), (W, 214)], fill=(150, 100, 90))
    cx, cy = 240, 168
    # 盒子和打开的盖子（盖子里有镜子）
    d.polygon([(150, 150), (330, 150), (340, 70), (160, 70)], fill=(170, 60, 80), outline=OUT)
    d.polygon([(162, 145), (318, 145), (326, 78), (170, 78)], fill=(210, 230, 240))
    for j in range(3): d.line([(180 + j * 14, 140), (200 + j * 14, 84)], fill=(240, 250, 255))
    d.rectangle([150, 168, 330, 214], fill=(190, 70, 92), outline=OUT)
    d.rectangle([150, 150, 330, 168], fill=(214, 96, 116), outline=OUT)
    for x in range(160, 330, 18): put(img, 'heart', x + 4, 192, 1, tint=(255, 200, 210))
    d.rectangle([150, 166, 330, 170], fill=GOLD)
    # 发条钥匙
    a = T * 3
    d.line([(334, 190), (346, 190)], fill=GOLD, width=3)
    d.ellipse([344 + 3 * math.cos(a), 182, 356 - 3 * math.cos(a), 198], outline=GOLD, width=2)
    # 转盘和两个转圈的小人
    d.ellipse([cx - 52, cy - 16, cx + 52, cy + 8], fill=(250, 220, 180), outline=OUT)
    d.ellipse([cx - 46, cy - 12, cx + 46, cy + 4], fill=(255, 236, 210))
    th = T * 2.2
    figs = []
    for who, off in (('boy', 0.0), ('girl', math.pi)):
        a = th + off
        x = cx + 26 * math.cos(a); y = cy - 4 + 7 * math.sin(a)
        s = math.sin(a)
        view = 'front' if s > 0.5 else ('back' if s < -0.5 else 'side')
        flip = math.cos(a) > 0 if view == 'side' else False
        figs.append((y, who, x, view, flip))
    for y, who, x, view, flip in sorted(figs):
        person(img, who, x, y, 'young', view, 'stand', 0, 'happy', 'up' if view != 'side' else 'reach', s=1, flip=flip)
    notes(img, d, T, 14, (120, 20, 360, 150), 3, speed=26)
    for j in range(6): twinkle(d, int(cx + 70 * math.cos(j + T)), int(110 + 30 * math.sin(j * 1.7 + T)), (T * 0.8 + j * 0.17) % 1, (255, 250, 220), 4)
    vig(img, 0.45, (20, 8, 20))


# ================================================================ 天亮的码头
def s_tomorrow(img, d, lt, dur, T, A):
    f = ease(clamp(lt / dur))
    hz = 150
    pre = ((0, (40, 40, 100)), (0.6, (170, 110, 150)), (1, (255, 170, 130)))
    dawn = ((0, (90, 140, 210)), (0.6, (250, 190, 170)), (1, (255, 230, 170)))
    stops = mix_stops(pre, dawn, f)
    sky(img, stops, 0, hz + 1)
    stars(d, T, 80, 1 - f, 60)
    sy = lerp(hz + 12, hz - 26, f)
    glow(img, 240, sy, 120, (255, 220, 160), 0.5, 60)
    d.ellipse([240 - 20, sy - 20, 240 + 20, sy + 20], fill=(255, 244, 210))
    d.rectangle([0, hz, W, H], fill=lerpc((40, 50, 100), (80, 110, 170), f))
    for y in range(hz + 1, H, 2):                            # 海面上的光
        k = (y - hz) / (H - hz)
        w = 20 + 60 * k
        x = 240 + math.sin(y * 0.7 + T * 3) * 4
        if (y // 2 + int(T * 6)) % 3: d.line([(x - w * (0.4 + 0.3 * math.sin(y + T)), y), (x + w * (0.4 + 0.3 * math.cos(y - T)), y)], fill=lerpc((255, 200, 150), (255, 246, 220), f))
        for j in range(3):
            xx = (j * 170 + y * 13 + T * 10) % W
            d.line([(xx, y), (xx + 8 + 10 * k, y)], fill=lerpc((60, 70, 130), (140, 170, 220), f))
    d.rectangle([0, hz - 1, W, hz], fill=lerpc((255, 200, 150), (255, 240, 200), f))
    # 码头
    d.polygon([(-20, H), (150, 206), (170, 206), (40, H)], fill=(110, 76, 56))
    for j in range(8):
        u = j / 8
        x0, y0 = lerp(-20, 150, u), lerp(H, 206, u)
        d.line([(x0, y0), (x0 + lerp(60, 20, u), y0)], fill=(80, 54, 40))
    d.rectangle([150, 202, 250, 208], fill=(130, 90, 64), outline=OUT)
    for x in (156, 200, 244): d.rectangle([x, 208, x + 4, 236], fill=(80, 54, 40))
    person(img, 'boy', 236, 216, 'young', 'side', 'sit', 0, 'smile', s=2)
    # 纸船往太阳那边漂
    bx = lerp(260, 330, f); by = lerp(226, 190, f)
    paper_boat(d, bx, by, 1, bob=math.sin(T * 3))
    for j in range(3):
        r = rng(j + 4)
        x = (r.uniform(0, W) + T * 20) % (W + 40) - 20
        pix.bird(d, int(x), int(60 + j * 14), T, (60, 50, 70), j)
    vig(img, 0.3, (30, 20, 40))


# ================================================================ 间奏（三）：满天孔明灯
def s_nana3(img, d, lt, dur, T, A):
    hz = 176
    sky(img, ((0, (6, 6, 24)), (0.7, (26, 20, 60)), (1, (70, 40, 80))), 0, hz + 1)
    stars(d, T, hz, 1.0, 140)
    pix.hills(d, hz - 4, 6, 0.02, 1.0, (24, 18, 44))
    d.rectangle([0, hz, W, H], fill=(14, 12, 34))
    for j in range(70):
        r = rng(j + 10)
        sp = r.uniform(10, 26)
        y = hz - 4 - ((T - 158) * sp + r.uniform(0, 260)) % 260
        x = r.uniform(0, W) + 6 * math.sin(T * 0.6 + j)
        s = 0.5 + (y / hz) * 1.0
        fl = 0.7 + 0.3 * math.sin(T * 7 + j * 3) + 0.2 * A
        lantern(img, d, x, y, s, clamp(fl), glow_r=10 * s)
        ry = hz + (hz - y) * 0.6
        if ry < H: d.rectangle([x - 1, ry, x + 1, ry + 1], fill=lerpc((255, 170, 80), (14, 12, 34), 0.4))
    person(img, 'boy', 170, 262, 'old', 'back', 'stand', 0, 'smile', 'up', s=2)
    person(img, 'girl', 310, 262, 'old', 'back', 'stand', 0, 'smile', 'up', s=2)
    notes(img, d, T, 10, (0, 30, W, 170), 9)
    vig(img, 0.4, (4, 4, 14))


# ================================================================ 手心里的心飘起来，变成一盏灯
HAND = [(0, 18), (-12, 17), (-24, 12), (-31, 4), (-33, -4), (-29, -6), (-26, -1), (-18, 3), (-10, 4), (-7, -3), (-5, -9), (-2, -7),
        (-1, 4)]


def cupped_hands(d, cx, cy, s=3):
    """手心朝上、并在一起捧着东西的两只手；(cx, cy) 是两手之间"""
    for side, sl in ((-1, CORAL), (1, DENIM)):
        d.polygon([(cx + side * 12 * s, cy + 17 * s), (cx + side * 24 * s, cy + 12 * s), (cx + side * 70 * s, H + 10), (cx + side * 14 * s, H + 10)], fill=sl)
        d.line([(cx + side * 12 * s, cy + 17 * s), (cx + side * 24 * s, cy + 12 * s)], fill=lerpc(sl, (255, 255, 255), 0.4), width=2)
        pts = [(cx + side * x * s, cy + y * s) for x, y in HAND]
        d.polygon([(x + side, y + 1) for x, y in pts], fill=OUT)
        d.polygon(pts, fill=SKIN)
        for (x0, y0), (x1, y1) in [((-30, -1), (-25, 7)), ((-27, 1), (-21, 8)), ((-22, 3), (-17, 9))]:   # 手指的缝
            d.line([(cx + side * x0 * s, cy + y0 * s), (cx + side * x1 * s, cy + y1 * s)], fill=SKIN_S)
        d.line([(cx + side * 6 * s, cy - 2 * s), (cx + side * 9 * s, cy + 3 * s)], fill=SKIN_S)                 # 拇指根
        d.arc([cx + (-20 if side < 0 else 4) * s, cy + 4 * s, cx + (-4 if side < 0 else 20) * s, cy + 14 * s], 20, 160, fill=SKIN_S)


def s_heart(img, d, lt, dur, T, A):
    sky(img, ((0, (8, 6, 24)), (1, (40, 20, 50))), 0, H)
    props.bokeh(img, T, 14, [(255, 120, 150), (255, 200, 150), (200, 150, 255)], 13, 0.22, 12, 28, 4)
    stars(d, T, 120, 0.7, 80)
    lift_t = 2.4
    hy0 = 178
    u = clamp((lt - lift_t) / (dur - lift_t))
    hy = hy0 - 240 * ein(u) * 0.9
    hx = 240 + 10 * math.sin(lt * 1.4) * u
    hand_y = 214 + 40 * ease(span(lt, lift_t + 0.6, dur))
    cupped_hands(d, 240, hand_y, 3)
    tb = thump(T, 0.35)
    sc = 1.3 + 0.25 * tb
    if u < 0.4:
        heart(img, d, hx, hy, sc, RED, RED_L, glow_a=0.45 + 0.3 * tb)
    if u > 0.2:                                            # 变成一盏心形的灯，下面有一点火光
        a = clamp((u - 0.2) / 0.2)
        glow(img, hx, hy, 50, (255, 160, 120), 0.4 * a)
        heart(img, d, hx, hy, sc * (1 - 0.2 * a), lerpc(RED, (255, 120, 110), a), (255, 210, 200), glow_a=0.3)
        d.ellipse([hx - 3, hy + 8 * sc, hx + 3, hy + 14 * sc], fill=(255, 240, 180)); glow(img, hx, hy + 11 * sc, 10, (255, 230, 150), 0.7 * a)
    for j in range(12):                                     # 往上飘的小光点
        r = rng(j + 22)
        k = ((T * 0.6 + r.random()) % 1)
        x = hx + r.uniform(-30, 30) + 6 * math.sin(T * 3 + j); y = hy + 30 - k * 90
        d.point((x, y), fill=lerpc((255, 220, 200), (40, 20, 50), k))
    vig(img, 0.45, (4, 2, 12))


# ================================================================ 河的两岸，各自走远
def s_unrelated(img, d, lt, dur, T, A):
    sky(img, ((0, (6, 8, 26)), (1, (30, 26, 70))), 0, 110)
    stars(d, T, 108, 1.0, 140)
    # 心形灯升成一颗星
    sx, sy = 240, lerp(40, 26, ease(clamp(lt / 1.2)))
    if lt < 1.2:
        lantern(img, d, sx, sy, 1.0 - 0.6 * lt / 1.2, 1.0, heart_shape=True)
    else:
        k = lt - 1.2
        glow(img, sx, sy, 16, (255, 220, 220), 0.5)
        twinkle(d, sx, int(sy), 0.5 + 0.2 * math.sin(T * 5), (255, 240, 240), 5)
    pix.hills(d, 104, 6, 0.02, 1.0, (24, 26, 50))
    d.rectangle([0, 110, W, 150], fill=(34, 40, 60))                 # 远岸
    d.rectangle([0, 150, W, 206], fill=(24, 30, 70))                 # 河
    for y in range(152, 206, 3):
        for x in range(int((y * 11 + T * 30) % 40) - 40, W, 40):
            d.line([(x, y), (x + 10, y)], fill=(40, 50, 96))
    d.rectangle([0, 206, W, H], fill=(40, 46, 60))                   # 近岸
    d.line([(0, 150), (W, 150)], fill=(70, 80, 110)); d.line([(0, 206), (W, 206)], fill=(70, 80, 110))
    # 河面上的星光倒影、两岸的芦苇
    glow(img, sx, 180, 14, (255, 220, 220), 0.25)
    for y in range(156, 204, 4): d.line([(sx - 3 + 2 * math.sin(T * 3 + y), y), (sx + 3 + 2 * math.sin(T * 3 + y), y)], fill=(200, 180, 210))
    for j in range(26):
        r = rng(j + 70)
        x = r.uniform(0, W); base = r.choice([150, 208])
        hgt = r.uniform(6, 14) * (1 if base == 208 else 0.6)
        sw = 1.5 * math.sin(T * 1.5 + j)
        d.line([(x, base), (x + sw, base - hgt)], fill=(50, 70, 70)); d.point((x + sw, base - hgt), fill=(130, 110, 90))
    # 断掉的那截红线顺着河漂走
    rx = lerp(150, 520, clamp(lt / dur))
    pts = [(rx + j * 3, 178 + 2 * math.sin(T * 3 + j * 0.6)) for j in range(10)]
    d.line(pts, fill=RED)
    # 他在近岸往左走，她在远岸往右走
    turn = 0.5
    walk = clamp(lt - turn)
    bx = 210 - walk * 46
    gx = 270 + walk * 40
    if lt < turn:
        person(img, 'boy', 210, 250, 'old', 'back', 'stand', 0, 'neutral', s=2)
        person_s(img, 'girl', 270, 148, 1.5, 'old', 'front', 'stand', 0, 'neutral')
    else:
        person(img, 'boy', bx, 250, 'old', 'side', 'walk', wph(T, 5), 'down', s=2, flip=True)
        person_s(img, 'girl', gx, 148, 1.5, 'old', 'side', 'walk', wph(T, 5), 'down')
    pix.fireflies(img, d, T, 8, (0, 110, W, 150), (200, 220, 255), 3)
    vig(img, 0.45, (4, 4, 14))


# ================================================================ 片尾：回到山坡，云又拼成片名
def s_outro(img, d, lt, dur, T, A):
    dawn = ((0, (70, 100, 170)), (0.4, (190, 150, 190)), (0.75, (255, 196, 170)), (1, (255, 226, 180)))
    hill_world(img, d, T, 0.0, couple=None, kite_on=False, clouds_x=lt * 6)
    # 风筝挂在树枝上
    kite(d, 372, 140, 1.2, T * 0.3, RED, GOLD_L, tail=True)
    d.line([(372, 152), (388, 170), (396, 180)], fill=(240, 230, 220))
    # 云从左边飘进来，拼成片名
    for i, (c, x, a) in enumerate(title_glyph_pos()):
        ts = 1.2 + i * 0.45
        k = lt - ts
        if k < 0: continue
        cg = cloud_glyph(c, 4)
        u = eout(clamp(k / 1.6))
        gx = lerp(x - 260 - i * 40, x - 6, u)
        gy = TITLE_Y - cg.height / 2 - 4 + 3 * math.sin(T * 0.8 + i)
        dpaste(img, cg, gx, gy, clamp(k / 0.6))
    if lt > 4.6:
        f = ease(span(lt, 4.6, 5.4))
        d.line([(120, TITLE_Y + 42), (lerp(120, 360, f), TITLE_Y + 42)], fill=RED)
        put(img, 'heart', lerp(120, 360, f) + 4, TITLE_Y + 42, 1)
        ar = artist_str()
        if ar: text(img, ar, 240, TITLE_Y + 60, (255, 246, 240), (80, 40, 70), alpha=f)
    pix.petals(d, T, 14, speed=12, wind=20, seed=12)
    end = ease(span(lt, dur - 2.6, dur - 0.3))
    if end > 0: dither_fade(img, end, (8, 6, 18))


s_outro.no_sub = True
