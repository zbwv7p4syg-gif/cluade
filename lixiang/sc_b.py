"""理想三旬 · 第一段副歌和间奏。签名都是 (img, d, lt, dur, T, A)。

无名小站的长椅上，树开花、长叶、落叶、下雪，他的头发慢慢白了，身边的小黑猫一直没醒；天亮的站台上火车开走、鸟群飞远；
他坐在一个停不下来的大钟摆上；楼顶的落日里眯着眼弹琴唱歌；一滴眼泪落下去，画面碎成一块块掉进黑暗；
铁轨一直通到远处的灯火，他一直走，灯火一直不近。间奏里火车沿着发光的铁轨开上夜空，一头鲸鱼在云海里陪它游，最后从巨大的月亮前面开过去，落进城市的灯火里。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
from props import *          # noqa: F401,F403
from pix import (W, H, FONT, FONT_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky, stars,
                 person, wph, put, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, vgrad, BAYER, bayer)
from sc_a import mountains, pole, wire, bez

YY, XX = np.mgrid[0:H, 0:W]


def snowfall(d, T, k, n=120):
    if k > 0: pix.snow(d, T, int(n * k), 16, (250, 250, 255), H, 3, 8)


# ================================================================ 无名小站的长椅：四季和白头发
SEASONS = [((255, 176, 200), (255, 214, 226)), ((80, 150, 80), (120, 186, 100)), ((220, 120, 50), (250, 170, 70)), ((236, 240, 250), (255, 255, 255))]


def season_tree(d, x, base, T, si, f):
    """树在四季之间换颜色；si 是第几季，f 是这一季里过了多少"""
    a, b = SEASONS[si % 4], SEASONS[(si + 1) % 4]
    k = ease(clamp((f - 0.7) / 0.3))
    leaf, leaf_l = lerpc(a[0], b[0], k), lerpc(a[1], b[1], k)
    if si % 4 == 3 and k < 0.5: leaf, leaf_l = (120, 110, 130), (236, 240, 250)
    pix.tree_round(d, x, base, 2.6, leaf, leaf_l, (70, 52, 50), math.sin(T) * 1.5)


def s_age(img, d, lt, dur, T, A):
    f = lt / dur
    si = min(3, int(f * 4)); sf = (f * 4) % 1 if si < 3 else clamp((f - 0.75) * 4)
    sky(img, NIGHT, 0, 196, 5)
    stars(d, T, 196, 1, 200)
    moon(d, 80, 50, 12)
    # 远处的山和小站的雨棚
    mountains(d, 196, 30, 0.014, 0.6, (34, 30, 66))
    d.rectangle([0, 196, W, H], fill=lerpc((52, 50, 76), (200, 206, 226), clamp((f - 0.72) * 4)))
    d.rectangle([0, 196, W, 200], fill=(90, 86, 110))
    season_tree(d, 140, 200, T, si, sf)
    # 站牌
    d.rectangle([380, 120, 382, 200], fill=(70, 66, 90))
    d.rectangle([346, 106, 418, 124], fill=(236, 236, 226)); d.rectangle([346, 106, 418, 124], outline=OUT)
    text(img, '无名站', 382, 115, (40, 60, 120), None, FONT, shadow=False)
    pix.lamp(img, d, 316, 200, 1.0, 84)
    # 长椅
    bx0, bx1, by = 190, 300, 186
    d.rectangle([bx0, by - 22, bx1, by - 18], fill=WOOD_D); d.rectangle([bx0, by - 15, bx1, by - 11], fill=WOOD_D)
    d.rectangle([bx0 - 4, by - 2, bx1 + 4, by + 2], fill=WOOD); d.rectangle([bx0 - 4, by + 2, bx1 + 4, by + 3], fill=WOOD_D)
    for lx in (bx0 + 4, bx1 - 6): d.rectangle([lx, by + 3, lx + 2, 200], fill=(60, 56, 70))
    # 他慢慢变老：灰白的头发用点阵一点点盖上来
    old = ease(clamp((f - 0.35) / 0.55))
    shade = (0.95, 0.92, 1.0)
    pix.person(img, 'boy', 236, 200 + 1, view='front', pose='sit', s=2, expr='closed', shade=shade)
    if old > 0:
        ghost(img, 'boy', 236, 201, 2, old, age='old', view='front', pose='sit', expr='closed')
    cat(img, 272, by - 2, 'sleep', 2, flip=True, rim=(120, 112, 150), T=T)
    # 落花、落叶、雪
    if si == 0: pix.petals(d, T, 26, seed=2, x0=60, x1=260, y1=200)
    if si == 2: leaves(d, T, 22, seed=3, box=(60, 0, 260, 200))
    snowfall(d, T, clamp((f - 0.68) * 4))
    vig(img, 0.4, (8, 6, 20))


# ================================================================ 天亮的站台：火车开走、鸟群飞远
def s_leave(img, d, lt, dur, T, A):
    sky(img, DAWN, 0, 200, 6)
    glow(img, 400, 196, 160, (255, 210, 160), 0.5, 60)
    d.ellipse([380, 180, 420, 220], fill=(255, 236, 196))
    mountains(d, 196, 26, 0.02, 2.2, (120, 96, 140))
    city(img, d, 200, 21, 0, (96, 80, 120), (255, 214, 150), 12, 40, frac=0.15, T=T)
    # 站台雨棚
    d.rectangle([0, 40, W, 46], fill=(60, 56, 76))
    for x in range(30, W, 110):
        d.rectangle([x, 46, x + 4, 210], fill=(60, 56, 76))
    # 列车慢慢开出去
    go = clamp((lt - 0.5) / (dur - 0.5))
    tx = 300 + 420 * ein(go)
    train(img, d, tx, 202, T, cars=3, lit=0.3, seed=9, roll=tx / 5)
    props.smoke(img, tx - 30, 150, T, n=8, col=(250, 236, 236), shade=(220, 190, 200), vx=-40 - 120 * go, vy=-16, life=1.8, r1=14, seed=3)
    props.rails(d, 202, 0, (90, 80, 90), (110, 90, 80))
    # 站台
    d.rectangle([0, 206, W, H], fill=(130, 120, 140))
    d.rectangle([0, 206, W, 210], fill=(236, 210, 120))
    for x in range(0, W, 12): d.point((x, 208), fill=(200, 170, 80))
    # 他站在站台上，手里攥着车票，没有上车
    pix.person(img, 'boy', 150, 252, view='side', s=2, arms='reach' if lt > 0.8 else 'down')
    if lt > 0.8:
        put(img, 'ticket', 168, 216, 1)
    cat(img, 112, 252, 'sit', 2, rim=(150, 130, 160), T=T)
    # 雨棚上的鸟一拍飞起，往远方飞
    fly = beat_after(T - lt + 0.2) - (T - lt)
    for j in range(9):
        r = rng(j * 5)
        k = clamp((lt - fly - j * 0.05) / 2.6)
        x0, y0 = 40 + j * 46, 38
        if k <= 0: put(img, 'bird', x0, y0, 1, tint=(50, 44, 64))
        else: pix.bird(d, x0 + k * (380 - x0) + math.sin(k * 6 + j) * 6, y0 + k * 120 - math.sin(k * 3) * 40 + r.uniform(-8, 8) * k, T, (60, 50, 74), j)
    vig(img, 0.3, (40, 20, 40))


# ================================================================ 无处停摆：停不下来的大钟摆
def gear(d, cx, cy, r, teeth, ang, col, hole=None):
    pts = []
    for i in range(teeth * 4):
        a = ang + i * 2 * math.pi / (teeth * 4)
        rr = r if (i % 4) in (0, 1) else r * 0.84
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    d.polygon(pts, fill=col)
    d.ellipse([cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3], fill=hole or lerpc(col, (0, 0, 0), 0.5))


def s_pendulum(img, d, lt, dur, T, A):
    sky(img, ((0, (16, 12, 40)), (0.6, (44, 30, 80)), (1, (80, 50, 110))), 0, H, 6)
    stars(d, T, H, 0.6, 120)
    # 背景里慢慢转的齿轮和飘着的钟
    for j, (gx, gy, gr, tt) in enumerate([(40, 60, 46, 12), (430, 210, 60, 16), (470, 40, 30, 10), (20, 230, 34, 10)]):
        gear(d, gx, gy, gr, tt, T * (0.3 if j % 2 else -0.3), (54, 42, 86))
    for j in range(5):
        r = rng(j * 3)
        cx, cy = r.uniform(60, 420), r.uniform(30, 240) + 8 * math.sin(T * 0.6 + j)
        rad = r.uniform(10, 20)
        clock(d, cx, cy, rad, T * 0.5 + j, T * (2 + j), rim=(110, 90, 140), face=(200, 190, 214), hand=(60, 50, 80), ticks=False)
    # 钟摆：摆到两头正好踩在拍点上
    bs = beats_in(T - lt - 1.5, T - lt + dur + 1.5)
    i = int(np.searchsorted(bs, T, 'right')) - 1
    if 0 <= i < len(bs) - 1:
        u = (T - bs[i]) / (bs[i + 1] - bs[i]); side = 1 if i % 2 == 0 else -1
        ang = side * math.cos(math.pi * u) * 0.55
    else: ang = 0.55 * math.cos(T * 2.6)
    px, py, Lr = 240, -30, 220
    for j in (3, 2, 1):                                       # 残影
        a2 = ang - j * 0.05 * (1 if ang > 0 else -1)
        bx, by = px + math.sin(a2) * Lr, py + math.cos(a2) * Lr
        d.line([(px, py), (bx, by)], fill=(70, 60, 100))
    bx, by = px + math.sin(ang) * Lr, py + math.cos(ang) * Lr
    d.line([(px - 1, py), (bx - 1, by)], fill=(150, 120, 60)); d.line([(px, py), (bx, by)], fill=(220, 180, 90)); d.line([(px + 1, py), (bx + 1, by)], fill=(150, 120, 60))
    glow(img, bx, by, 50, (255, 210, 120), 0.3)
    d.ellipse([bx - 24, by - 24, bx + 24, by + 24], fill=(150, 110, 50))
    d.ellipse([bx - 21, by - 21, bx + 21, by + 21], fill=(230, 186, 90))
    d.ellipse([bx - 14, by - 14, bx + 6, by + 6], fill=(250, 220, 140))
    # 他坐在摆锤顶上
    pix.person(img, 'boy', bx, by - 16, view='front', pose='sit', s=2, expr='neutral')
    vig(img, 0.45, (8, 4, 20))


# ================================================================ 楼顶的落日：弹琴唱歌
def rooftop(img, d, T, sun_y=150):
    sky(img, GOLDEN, 0, 210, 6)
    glow(img, 360, sun_y, 190, (255, 220, 160), 0.55, 100)
    d.ellipse([320, sun_y - 40, 400, sun_y + 40], fill=(255, 240, 200))
    for i in range(3):
        cloud(d, (40 + i * 170 + T * 5) % (W + 100) - 50, 30 + i * 18, 2.0, (255, 214, 196), (240, 170, 160), (255, 240, 230))
    city(img, d, 210, 31, T * 2, (170, 100, 110), (255, 230, 170), 30, 110, frac=0.12, T=T)
    city(img, d, 222, 33, T * 4, (120, 70, 90), (255, 220, 150), 20, 80, frac=0.12, T=T)
    # 楼顶：水箱、晾衣绳
    d.rectangle([0, 214, W, H], fill=(96, 70, 80))
    d.rectangle([0, 210, W, 216], fill=(140, 104, 108))
    d.rectangle([40, 150, 90, 210], fill=(120, 88, 96)); d.ellipse([40, 140, 90, 160], fill=(140, 104, 108))
    for lx in (46, 84): d.rectangle([lx, 196, lx + 3, 214], fill=(80, 60, 70))
    d.line([(100, 160), (200, 172)], fill=(70, 50, 60))
    for k, c in enumerate([(240, 240, 250), (120, 170, 220), (250, 200, 90)]):
        x = 116 + k * 26; y = 162 + k * 3 + math.sin(T * 3 + k) * 1.5
        d.rectangle([x, y, x + 12, y + 14 + (k % 2) * 4], fill=c)


def guitar_lap(d, x, y, T, strum=0.0):
    """抱在怀里的吉他（侧面坐着的人身前）"""
    d.ellipse([x - 4, y - 10, x + 18, y + 6], fill=OUT)
    d.ellipse([x - 3, y - 9, x + 17, y + 5], fill=(214, 146, 78))
    d.ellipse([x + 4, y - 4, x + 9, y + 1], fill=(60, 36, 24))
    d.line([(x + 14, y - 6), (x + 40, y - 22)], fill=(110, 70, 46), width=3)
    d.rectangle([x + 38, y - 26, x + 44, y - 20], fill=(80, 50, 36))
    d.rectangle([x + 2 + strum, y - 1, x + 5 + strum, y + 2], fill=SKIN)


def s_sing(img, d, lt, dur, T, A):
    def wide(img, d, t):
        rooftop(img, d, T)
        # 他坐在楼顶边上弹琴，围巾被风吹起来
        x, y = 290, 214
        pix.person(img, 'boy', x, y, view='side', pose='sit', s=3, expr='happy', arms='down')
        strum = int(2 * math.sin(T * 12) * (1 if pix.amp(T) > 0.3 else 0.3))
        guitar_lap(d, x - 8, y - 33, T, strum)
        fl = math.sin(T * 9) * 2
        d.polygon([(x - 12, y - 46), (x - 6, y - 46), (x - 30 + fl, y - 54), (x - 34 + fl, y - 50)], fill=MUSTARD)
        notes(img, d, T, 10, (200, 40, 420, 190), seed=11, speed=20)
        for j in range(3):
            pix.bird(d, (T * 30 + j * 90) % (W + 40) - 20, 60 + j * 14 + math.sin(T * 2 + j) * 5, T, (120, 70, 80), j)

    def close(img, d, t):
        rooftop(img, d, T, 120)
        props.bokeh(img, T, 12, [(255, 230, 170), (255, 200, 150), (255, 250, 220)], seed=2, a=0.35)
        on = pix.pulse(T, 0.35) > 0.2
        bust(img, d, 'boy', 200, 40 + round(math.sin(T * 5)), 5, 'sing' if on else 'happy', wind=1.0, T=T)
        notes(img, d, T, 12, (260, 20, 470, 200), seed=12, speed=26)
    cut = beat_after(T - lt + 3.4) - (T - lt)
    shots(img, lt, [(0, wide), (cut, close)], 0.3)
    vig(img, 0.3, (100, 40, 50))


# ================================================================ 热泪的崩坏
EYE_C = (240, 146)


@lru_cache(None)
def eye_base():
    """眼睛的大特写：皮肤、眉毛、几缕头发、睫毛和带高光的眼珠"""
    img = Image.new('RGB', (W, H), SKIN); d = ImageDraw.Draw(img)
    a = np.asarray(img, float).copy()
    dist = np.sqrt(((XX - 240) / 300) ** 2 + ((YY - 150) / 200) ** 2)
    sh = np.clip(np.floor((dist - 0.5) * 6 + BAYER) / 6, 0, 1)[..., None]
    a = a * (1 - sh * 0.35) + np.array(SKIN_S) * sh * 0.35
    img = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(img)
    cx, cy = EYE_C
    wdt, ht, hb = 120, 46, 26
    lens = (np.abs(XX - cx) < wdt) & (YY > cy - ht * (1 - ((XX - cx) / wdt) ** 2)) & (YY < cy + hb * (1 - ((XX - cx) / wdt) ** 2))
    arr = np.asarray(img).copy()
    arr[lens] = (250, 246, 240)
    ir = (XX - cx - 6) ** 2 + (YY - cy + 4) ** 2
    arr[lens & (ir < 38 ** 2)] = (110, 72, 56)
    arr[lens & (ir < 34 ** 2)] = (84, 52, 42)
    arr[lens & (ir < 16 ** 2)] = (22, 16, 22)
    arr[lens & (YY < cy - 20)] = (np.asarray(arr[lens & (YY < cy - 20)], float) * 0.85).astype(np.uint8)
    img = Image.fromarray(arr); d = ImageDraw.Draw(img)
    d.rectangle([cx - 16, cy - 20, cx - 6, cy - 10], fill=(255, 255, 255))
    d.rectangle([cx + 16, cy + 8, cx + 20, cy + 12], fill=(255, 255, 255))
    up = [(cx + x, cy - ht * (1 - (x / wdt) ** 2)) for x in range(-wdt, wdt + 1, 4)]
    lo = [(cx + x, cy + hb * (1 - (x / wdt) ** 2)) for x in range(-wdt, wdt + 1, 4)]
    d.line(up, fill=(40, 28, 34), width=7)
    d.line(lo, fill=SKIN_S, width=3)
    for k in range(9):                                        # 睫毛
        x = -wdt + 30 + k * 24
        x0, y0 = cx + x, cy - ht * (1 - (x / wdt) ** 2) - 2
        d.line([(x0, y0), (x0 + 6 + k, y0 - 12)], fill=(40, 28, 34), width=3)
    d.line([(cx - 130, cy - 82), (cx - 40, cy - 98), (cx + 60, cy - 96), (cx + 140, cy - 80)], fill=(54, 40, 44), width=12)
    for k in range(5):                                        # 垂下来的几缕头发
        x = 40 + k * 100
        d.polygon([(x - 50, 0), (x + 50, 0), (x + 10 + k * 3, 30 + (k % 2) * 16), (x - 10, 22)], fill=(40, 34, 42))
    return img


def eye_close(img, d, t, tear):
    img.paste(eye_base())
    cx, cy = EYE_C
    # 眼泪：先在下眼睑的内眼角鼓起来，再顺着脸颊滑下去，最后掉出画面
    ex, ey = cx - 70, cy + 22
    if tear < 0.35:
        r = 3 + tear / 0.35 * 9
        x, y = ex, ey + 4
    elif tear < 0.75:
        k = (tear - 0.35) / 0.4
        r = 12; x, y = ex - k * 10, ey + 4 + ein(k) * 80
    else:
        k = (tear - 0.75) / 0.25
        r = 12 - k * 3; x, y = ex - 14, ey + 84 + ein(k) * 140
    if 0.35 < tear < 0.85:
        d.line([(ex, ey + 4), (x, y - r)], fill=(176, 206, 236), width=5)
    d.polygon([(x - r * 0.8, y - r * 0.5), (x, y - r * 2.2), (x + r * 0.8, y - r * 0.5)], fill=(150, 196, 246))
    d.ellipse([x - r, y - r * 1.1, x + r, y + r], fill=(150, 196, 246))
    d.ellipse([x - r * 0.55, y - r * 0.7, x - r * 0.1, y - r * 0.2], fill=(240, 250, 255))
    d.arc([x - r, y - r * 1.1, x + r, y + r], 20, 160, fill=(110, 160, 220))


SHARDS = [(bx, by, rng(bx * 31 + by).uniform(0, 0.5), rng(bx + by * 17).uniform(-60, 60)) for bx in range(0, W, 30) for by in range(0, H, 30)]


def s_tear(img, d, lt, dur, T, A):
    hit = beat_after(T - lt + 1.9) - (T - lt)
    tear = clamp(lt / hit)
    eye_close(img, d, lt, tear)
    k = lt - hit
    if k < 0: return vig(img, 0.4, (10, 6, 20))
    # 落地的那一拍：裂纹从中间散开，再一块块往下掉
    cx, cy = 240, 200
    src = np.asarray(img).copy()
    if k < 0.45:
        for j in range(14):
            a = j * 2 * math.pi / 14 + 0.2
            ln = eout(k / 0.3) * 260
            pts = [(cx, cy)]
            for s in range(1, 8):
                pts.append((cx + math.cos(a + math.sin(s * 3 + j) * 0.15) * ln * s / 7, cy + math.sin(a + math.sin(s * 2 + j) * 0.15) * ln * s / 7))
            d.line(pts, fill=(240, 250, 255))
        glow(img, cx, cy, 60, (180, 220, 255), 0.6 * (1 - k / 0.45))
        props.shake(img, k, 4, 0.3)
        return
    src = np.asarray(img).copy()
    out = Image.new('RGB', (W, H), (4, 4, 10)); od = ImageDraw.Draw(out)
    kk = k - 0.45
    for bx, by, delay, spin in SHARDS:
        u = kk - delay - (abs(bx - cx) + abs(by - cy)) / 900
        if u < 0:
            out.paste(Image.fromarray(src[by:by + 30, bx:bx + 30]), (bx, by)); continue
        y = by + 300 * u * u + 20 * u; x = bx + spin * u * 0.4
        if y > H: continue
        piece = Image.fromarray(src[by:by + 30, bx:bx + 30])
        if u > 0.05:
            a = np.asarray(piece, float) * max(0.3, 1 - u)
            piece = Image.fromarray(a.astype(np.uint8))
        out.paste(piece, (int(x), int(y)))
        od.rectangle([x, y, x + 29, y + 29], outline=(200, 220, 255) if u < 0.2 else None)
    img.paste(out)
    glow(img, cx, cy, 80, (120, 170, 255), 0.25 * clamp(1 - kk))


# ================================================================ 没抵达的存在：一直走不到的灯火
def s_unreached(img, d, lt, dur, T, A):
    hz = 118
    sky(img, ((0, (10, 10, 34)), (0.7, (40, 30, 80)), (1, (110, 70, 120))), 0, hz + 2, 6)
    stars(d, T, hz, 1, 220)
    pix.meteor(d, lt, 1.0, 380, 20, -140, 60)
    pix.meteor(d, lt, 3.3, 200, 10, -120, 50)
    # 远处的灯火：一直在地平线上，跟着节拍轻轻跳
    glow(img, 240, hz, 120, (255, 200, 130), 0.45 + 0.15 * pix.pulse(T, 0.5), 30)
    for j in range(16):
        r = rng(j * 7)
        x = 240 + r.uniform(-50, 50); h = r.uniform(2, 10)
        d.rectangle([x, hz - h, x + r.randint(2, 5), hz], fill=(60, 40, 70))
        if r.random() < 0.7: d.point((x + 1, hz - h + 2), fill=(255, 220, 150))
    d.rectangle([0, hz, W, H], fill=(24, 22, 44))
    # 透视的铁轨：枕木一直往脚下滚，人却一直走不近
    off = (lt * 2.2) % 1
    for i in range(70):
        z = (i + 1 - off) * 0.32
        if z <= 0.3: continue
        y = hz + 140 / z
        if y > H + 20: continue
        hw = 120 / z
        c = lerpc((24, 22, 44), (110, 86, 76), clamp(2.4 / z))
        d.rectangle([240 - hw * 1.4, y, 240 + hw * 1.4, y + max(1, 9 / z)], fill=c)
    for side in (-1, 1):
        d.line([(240, hz), (240 + side * 120 / 0.3 * 1.0, hz + 140 / 0.3)], fill=(160, 150, 170))
    # 两边的电线杆
    for i in range(10):
        z = (i * 3 + 2 - (lt * 2.2 * 0.53) % 3) * 0.6
        if z <= 0.4: continue
        y = hz + 140 / z; x = 240 + 320 / z
        h = 260 / z
        for sx in (x, 480 - x):
            d.rectangle([sx - max(1, 3 / z), y - h, sx + max(1, 3 / z), y], fill=(40, 36, 60))
    # 他背对着我们沿着铁轨走
    pix.person(img, 'boy', 240, 236, view='back', pose='walk', ph=wph(T, 6), s=2)
    cat(img, 268, 236, 'walk', 2, flip=False, rim=(110, 100, 140), T=T)
    pix.fireflies(img, d, T, 12, (20, 140, 460, 250), seed=5)
    vig(img, 0.45, (6, 4, 18))


# ================================================================ 间奏：开上夜空的火车 / 云海里的鲸 / 巨大的月亮
def s_skytrack(img, d, lt, dur, T, A):
    rise = ease(clamp(lt / dur))
    sky(img, mix_stops(((0, (30, 26, 70)), (0.6, (80, 60, 120)), (1, (170, 110, 140))), NIGHT, rise), 0, H, 6)
    stars(d, T, H, 0.4 + 0.6 * rise, 240, ox=T * 20, oy=-rise * 120)
    # 城市和地面往下沉，云层从下面升上来
    gy = 200 + rise * 160
    city(img, d, gy, 41, T * 40, (30, 26, 60), (255, 210, 140), 30, 80, frac=0.3, T=T)
    if gy < H: d.rectangle([0, gy, W, H], fill=(20, 18, 44))
    for j in range(6):
        cx = (j * 110 - T * 60) % (W + 160) - 80
        cloud(d, cx, 260 - rise * 120 + (j % 2) * 16, 3.0, (110, 96, 150), (80, 70, 120), (150, 140, 190))
    # 发光的铁轨托着火车往上开
    ty = 170 - rise * 30
    for x in range(-20, W + 20, 12):
        xx = (x - T * 140) % (W + 40) - 20
        d.rectangle([xx, ty + 1, xx + 6, ty + 3], fill=(255, 220, 160))
    d.line([(0, ty), (W, ty)], fill=(255, 240, 200))
    glow(img, 240, ty, 260, (255, 210, 150), 0.2, 8)
    train(img, d, 360, ty, T, cars=3, night=0.6, lit=1.0, seed=4, hero=(0, 2), roll=T * 30, headlight=1.0)
    props.smoke(img, 330, ty - 52, T, n=8, col=(200, 196, 230), shade=None, vx=-90, vy=-6, life=1.8, r1=12, seed=8)
    for j in range(3): pix.meteor(d, lt, 1 + j * 1.6, 420 - j * 80, 10 + j * 14, -160, 70)
    vig(img, 0.35, (8, 6, 24))


def whale(img, d, x, y, s, T, col=(40, 70, 130), belly=(150, 190, 230), spots=(220, 240, 255)):
    """云海里的鲸鱼，(x, y) 是身体中心，头朝右"""
    S = lambda v: v * s
    sw = math.sin(T * 1.2) * S(4)
    d.ellipse([x - S(80), y - S(26), x + S(70), y + S(26)], fill=col)
    d.ellipse([x + S(30), y - S(22), x + S(90), y + S(22)], fill=col)
    d.chord([x - S(60), y - S(6), x + S(86), y + S(28)], 0, 180, fill=belly)
    for k in range(6):
        d.line([(x - S(30) + k * S(14), y + S(12)), (x - S(26) + k * S(14), y + S(22))], fill=lerpc(belly, col, 0.4))
    tail = [(x - S(76), y - S(4)), (x - S(118), y - S(22) + sw), (x - S(126), y - S(30) + sw), (x - S(110), y + sw * 0.5),
            (x - S(126), y + S(26) + sw), (x - S(116), y + S(20) + sw), (x - S(76), y + S(8))]
    d.polygon(tail, fill=col)
    d.polygon([(x - S(10), y + S(14)), (x + S(14), y + S(16)), (x - S(4), y + S(40) + sw), (x - S(20), y + S(34) + sw)], fill=lerpc(col, (0, 0, 0), 0.2))
    d.ellipse([x + S(56), y - S(8), x + S(62), y - S(2)], fill=(250, 250, 255))
    d.point((x + S(59), y - S(5)), fill=(20, 20, 40))
    for k in range(14):
        r = rng(k * 3)
        px, py = x + r.uniform(-S(70), S(60)), y - S(20) + r.uniform(0, S(16))
        b = 0.5 + 0.5 * math.sin(T * 3 + k)
        if b > 0.3: d.point((px, py), fill=lerpc(col, spots, b))
    # 喷出来的星星
    for k in range(10):
        u = (T * 0.7 + k / 10) % 1
        px = x + S(40) + math.sin(k * 2.3) * u * S(26); py = y - S(26) - u * S(50)
        twinkle(d, int(px), int(py), u, (255, 250, 220), 2)


def s_whale(img, d, lt, dur, T, A):
    sky(img, NIGHT, 0, H, 6)
    stars(d, T, H, 1, 260, ox=T * 10)
    moon(d, 90, 50, 18)
    glow(img, 90, 50, 70, (240, 230, 200), 0.3)
    for j in range(4): pix.meteor(d, lt, 0.4 + j * 1.3, 470 - j * 60, 8 + j * 12, -170, 80)
    # 云海
    for row, (y, col, sp) in enumerate([(200, (60, 56, 110), 20), (216, (84, 76, 136), 40), (236, (110, 100, 160), 70)]):
        for j in range(9):
            cx = (j * 70 - T * sp + row * 30) % (W + 140) - 70
            d.ellipse([cx - 40, y - 14 + (j % 2) * 4, cx + 40, y + 20], fill=col)
        d.rectangle([0, y + 6, W, H], fill=col)
    wx = lerp(-160, 280, ease(clamp(lt / (dur * 0.7)))) + math.sin(T * 0.8) * 6
    whale(img, d, wx, 106 + math.sin(T * 1.1) * 6, 1.3, T)
    # 火车在前面开，窗里他探出头看鲸鱼
    ty = 200
    for x in range(-20, W + 20, 12):
        xx = (x - T * 140) % (W + 40) - 20
        d.rectangle([xx, ty + 1, xx + 6, ty + 3], fill=(255, 220, 160))
    d.line([(0, ty), (W, ty)], fill=(255, 240, 200))
    train(img, d, 440, ty, T, cars=3, night=0.6, lit=1.0, seed=4, hero=(0, 4), roll=T * 30, headlight=1.0)
    props.smoke(img, 410, ty - 52, T, n=8, col=(200, 196, 230), shade=None, vx=-90, vy=-6, life=1.8, r1=12, seed=8)
    vig(img, 0.35, (8, 6, 24))


def s_moon(img, d, lt, dur, T, A):
    pan = ease(clamp((lt - (dur - 2.4)) / 2.2))               # 最后镜头往下摇到城市
    oy = -pan * 200
    sky(img, NIGHT, 0, H, 6)
    stars(d, T, H, 1 - pan * 0.5, 260, oy=-oy)
    mx, my, mr = 240, 120 + oy, 96
    glow(img, mx, my, 200, (250, 240, 210), 0.35)
    moon(d, mx, my, mr, (252, 246, 220), (226, 218, 190))
    # 剪影的火车从月亮前面开过
    tx = lerp(-60, W + 420, lt / (dur - 0.6))
    ty = 170 + oy
    sil = Image.new('RGBA', (W, H)); sd = ImageDraw.Draw(sil)
    train(sil, sd, tx, ty, T, cars=3, seed=4, roll=T * 30, people=False, rust=0, body=(20, 20, 40), body_s=(16, 16, 30), body_l=(30, 30, 50),
          tint_win=(255, 220, 150))
    a = np.array(sil); m = a[..., 3] > 0
    win = (a[..., 0] > 200) & m
    a[m & ~win, :3] = (14, 14, 30)
    img.paste(Image.fromarray(a), (0, 0), Image.fromarray(a))
    d.line([(0, ty), (W, ty)], fill=(255, 240, 200))
    props.smoke(img, tx - 30, ty - 52, T, n=8, col=(30, 30, 56), shade=None, vx=-90, vy=-6, life=1.8, r1=12, seed=8)
    # 往下摇出来的城市
    cy = H + 200 + oy
    if cy < H + 120:
        city(img, d, cy - 20, 51, 0, (40, 30, 70), (255, 200, 120), 60, 170, frac=0.4, T=T)
        city(img, d, cy, 52, 0, (24, 20, 50), (255, 160, 200), 40, 120, frac=0.45, T=T)
        props.bokeh(img, T, 10, seed=3, a=0.3 * pan, box=(0, H - 120, W, H))
    vig(img, 0.35, (8, 6, 24))
