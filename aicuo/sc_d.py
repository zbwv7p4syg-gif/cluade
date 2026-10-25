"""爱错 · 间奏后的桥段、最后一段副歌和片尾。签名都是 (img, d, lt, dur, T, A)。

灰蒙蒙的公园长椅上，他身边的位置空着，她的影子坐下来又淡掉；夜里的树林，他打着手电找那些萤火，光一照到就灭了；
黄昏的站台，火车载着她开走，他追了几步，手抬到一半又放下；旧照片一张张褪成白色。
最后一段副歌是一场风暴：北风从海上升起来怒吼，他站在崖边；特写他闭着眼淋雨；他张开双臂朝天喊；
红叶穿过云层往上飞，他往下坠，落在一片像镜子的水面上，四周漂着碎掉的钟，大钟在高音里炸开。
风停了，雪地上空挂着极光，他和北风并排坐着；她在雪里回头笑了一下，化成红叶；他接住一片，又把它交给北风，
北风这次轻轻地把叶子托上月亮。"爱错"砸下来三次。片尾天亮了，秃树上冒出一颗新芽，他踩着雪走远；
最后的片名上，那道裂缝被金色补好了。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
import motifs as M
import sc_a
from props import *          # noqa: F401,F403
from pix import (W, H, FONT, FONT_S, OUT, SKIN, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky,
                 stars, person, wph, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, city, lamp, BAYER)
from sc_a import ridge, hill, NIGHT_W, title_cells, crack_x, TS
from sc_c import photo

YY, XX = np.mgrid[0:H, 0:W]
GRAY = ((0, (110, 112, 126)), (0.6, (160, 158, 166)), (1, (196, 190, 186)))
STORMNIGHT = ((0, (10, 10, 24)), (0.6, (30, 30, 52)), (1, (54, 50, 78)))


def snowfield(img, d, T, base=200, col=(214, 224, 244), shade=(170, 184, 220)):
    for x in range(W):
        y = base + 5 * math.sin(x * 0.02 + 1) + 3 * math.sin(x * 0.07)
        d.line([(x, y), (x, H)], fill=col)
        d.point((x, y), fill=(250, 252, 255))
    for i in range(40):
        r = rng(i * 3)
        x, y = r.uniform(0, W), r.uniform(base + 10, H)
        d.line([(x, y), (x + r.uniform(6, 20), y)], fill=shade)


# ================================================================ 长椅上空着的一半
def s_bench(img, d, lt, dur, T, A):
    sky(img, GRAY, 0, 196, 5)
    for i, x in enumerate((40, 120, 380, 450)):
        pix.tree_round(d, x, 196, 2.2 - (i % 2) * 0.4, leaf=(150, 104, 70), leaf_l=(186, 132, 86), trunk=(84, 66, 60))
    d.rectangle([0, 196, W, H], fill=(124, 118, 104))
    d.polygon([(150, 196), (330, 196), (420, H), (60, H)], fill=(150, 142, 128))
    grade(img, sat=0.55)
    M.bench(d, 180, 214, 120, col=(130, 96, 74), col_d=(92, 64, 50))
    for i in range(30):                                                 # 地上的落叶
        r = rng(i * 7)
        M.leaf_bit(d, r.uniform(0, W), r.uniform(214, 268), 0, i)
    # 她的影子在旁边坐下，又慢慢淡掉
    ga = clamp((lt - 0.9) / 0.8) * clamp((3.9 - lt) / 1.0) * 0.65
    if ga > 0:
        glow(img, 262, 186, 30, (255, 190, 190), 0.2 * ga)
        props.ghost(img, 'girl', 262, 218, 2, ga, view='front', pose='sit', expr='smile')
    person(img, 'boy', 204, 218, view='front', pose='sit', expr='down', s=2)
    pix.petals(d, T, 24, M.LEAF_COLS, 18, 26, seed=5)
    vig(img, 0.4, (40, 36, 40))


# ================================================================ 手电照到的萤火一个个熄灭
FLIES = [(rng(i * 13).uniform(230, 460), rng(i * 13 + 1).uniform(60, 196)) for i in range(16)]
HAND = (154, 196)


def beam_ang(t):
    return -0.18 + 0.42 * math.sin(t * 1.15 - 0.6)


@lru_cache(None)
def fly_out():
    """每只萤火第一次被光束扫到的时间"""
    out = []
    for i, (x, y) in enumerate(FLIES):
        phi = math.atan2(y - HAND[1], x - HAND[0])
        hit = 5.4 + i * 0.03
        t = 0.6
        while t < 5.6:
            if abs(beam_ang(t) - phi) < 0.09: hit = t; break
            t += 0.02
        out.append(hit)
    return out


def s_search(img, d, lt, dur, T, A):
    sky(img, ((0, (6, 10, 18)), (0.7, (14, 26, 34)), (1, (24, 40, 46))), 0, H, 5)
    for layer, (col, n, wmin) in enumerate((((20, 34, 40), 9, 6), ((12, 22, 28), 6, 12))):
        for i in range(n):
            r = rng(i * 7 + layer * 50)
            x = r.uniform(-10, W)
            w = r.uniform(wmin, wmin * 1.8)
            d.rectangle([x, 0, x + w, H], fill=col)
    d.rectangle([0, 222, W, H], fill=(16, 26, 26))
    lower = lt > 5.7
    ang = beam_ang(lt) if not lower else lerp(beam_ang(5.7), 1.0, ease((lt - 5.7) / 0.5))
    hx, hy = HAND
    L = 320; sp = 0.13
    p1 = (hx + math.cos(ang - sp) * L, hy + math.sin(ang - sp) * L)
    p2 = (hx + math.cos(ang + sp) * L, hy + math.sin(ang + sp) * L)
    tfill(img, 'polygon', [(hx, hy - 1), p1, p2, (hx, hy + 1)], (255, 244, 200), 0.16)
    tfill(img, 'polygon', [(hx, hy), (hx + math.cos(ang - sp / 2) * L, hy + math.sin(ang - sp / 2) * L),
                           (hx + math.cos(ang + sp / 2) * L, hy + math.sin(ang + sp / 2) * L)], (255, 248, 220), 0.12)
    outs = fly_out()
    for i, ((x, y), t_out) in enumerate(zip(FLIES, outs)):
        x += 6 * math.sin(T * 0.6 + i); y += 4 * math.sin(T * 0.8 + i * 2)
        if lt < t_out:
            b = 0.6 + 0.4 * math.sin(T * 3 + i)
            glow(img, x, y, 7, (255, 220, 120), 0.45 * b)
            d.point((x, y), fill=(255, 250, 200))
        elif lt < t_out + 0.35:
            twinkle(d, int(x), int(y), (lt - t_out) / 0.35, (255, 240, 200), 4)
    person(img, 'boy', 140, 222, view='side', pose='walk' if 0.3 < lt < 1.6 else 'stand', ph=wph(lt, 5), expr='sad' if lt > 4 else 'neutral',
           arms='reach' if not lower else 'down', s=2)
    if not lower:
        d.rectangle([hx - 4, hy - 2, hx + 2, hy + 1], fill=(70, 70, 80)); glow(img, hx + 2, hy, 8, (255, 244, 200), 0.6)
    vig(img, 0.5, (0, 0, 0))


# ================================================================ 黄昏站台
def s_platform(img, d, lt, dur, T, A):
    sky(img, GOLDEN, 0, 196, 6)
    glow(img, 380, 150, 120, (255, 200, 140), 0.45, 60)
    d.ellipse([360, 130, 400, 170], fill=(255, 232, 186))
    city(img, d, 180, 31, 0, (150, 100, 120), hmin=20, hmax=60, frac=0, T=T)
    for x in range(-20, W + 40, 120):                                  # 电线杆和电线
        d.rectangle([x, 70, x + 3, 196], fill=(80, 60, 70)); d.rectangle([x - 10, 76, x + 13, 78], fill=(80, 60, 70))
    for y in (78, 84): d.line([(0, y), (W, y + 2)], fill=(90, 66, 76))
    d.rectangle([0, 190, W, 200], fill=(96, 80, 84))
    props.rails(d, 196, 0, (70, 56, 60), (110, 84, 70))
    go = 1.2
    tx = 360 + (17.4 * (lt - go) ** 2 if lt > go else 0)
    wins = props.train(img, d, tx, 196, T, cars=2, s=1.0, lit=0.5, hero=(0, 2), seed=4)
    # 站台
    d.rectangle([0, 206, W, H], fill=(150, 140, 140))
    d.rectangle([0, 206, W, 209], fill=(230, 200, 90))
    for x in range(0, W, 30): d.line([(x, 210), (x - 20, H)], fill=(136, 126, 128))
    d.rectangle([40, 120, 44, 206], fill=(70, 66, 80)); d.rectangle([20, 112, 70, 124], fill=(40, 70, 120))
    text(img, '站台 1', 45, 118, col=(255, 255, 255), out=None, font=FONT_S, shadow=False)
    # 他：追着火车走了几步，停下，手抬到一半，又放下
    if lt < 1.6: bx, pose, arms, ex = 210, 'stand', 'down', 'sad'
    elif lt < 4.0: bx, pose, arms, ex = 210 + (lt - 1.6) * 40, 'walk' if lt < 2.6 else 'run', 'auto', 'surprised'
    elif lt < 4.3: bx, pose, arms, ex = 306, 'stand', 'down', 'sad'
    elif lt < 5.8: bx, pose, arms, ex = 306, 'stand', 'reach', 'sad'
    else: bx, pose, arms, ex = 306, 'stand', 'down', 'down'
    person(img, 'boy', bx, 246, view='side', pose=pose, ph=wph(lt, 8 if pose == 'run' else 5), expr=ex, arms=arms, s=2)
    for j in range(4): pix.bird(d, int(120 + j * 30 + lt * 14), int(50 + (j % 2) * 8 - lt * 3), T, (110, 70, 80), j)
    vig(img, 0.35, (60, 30, 40))


# ================================================================ 旧照片一张张褪成白色
@lru_cache(None)
def snap_photo(T0, w, h):
    return props.sepia(props.shrink(props.SNAP(T0), w, h), 0.8)


def s_past(img, d, lt, dur, T, A):
    img.paste((250, 246, 238), (0, 0, W, H))
    pics = [(photo('park', 96, 60), 100, -0.4, 6, 0.9), (snap_photo(48.5, 96, 60), 230, -0.1, -5, 1.3),
            (photo('sea', 96, 60), 360, -0.25, 8, 1.7), (snap_photo(97.2, 96, 60), 170, -0.7, -9, 2.1)]
    for im, x, y0, rot, fade in pics:
        y = lerp(60, 180, (lt + 0.6 + y0) / 3.2)
        a = clamp((fade + 0.4 - lt) / 0.5)
        props.polaroid(img, d, x, y, im, 1.0, a, rot)
    pix.petals(d, T, 14, ((230, 220, 210), (240, 230, 220)), 14, 6, seed=2)


# ================================================================ 最后一段副歌：风暴
def flash(img, T, at, dur_=0.18):
    k = T - at
    if 0 <= k < dur_: dither_fade(img, 0.75 * (1 - k / dur_), (240, 240, 255)); return True
    return False


def s_storm(img, d, lt, dur, T, A):
    sky(img, STORMNIGHT, 0, H, 6)
    for i in range(5):
        r = rng(i * 5)
        cloud(d, (r.uniform(-60, W) + T * 30) % (W + 160) - 100, r.uniform(0, 50), 3 + r.random(), (40, 40, 64), (30, 30, 50))
    bolts = [x for x in beats_in(T - lt, T - lt + dur) if x in pix.AUDIO['bars']] + [T - lt + 0.1]
    for b in bolts:
        if 0 <= T - b < 0.25:
            M.lightning(d, 300 + (b * 37) % 120, 0, 150, int(b * 10))
    # 海面的大浪
    for x in range(0, W, 2):
        y = 196 + 8 * math.sin(x * 0.04 + T * 2.2) + 5 * math.sin(x * 0.11 - T * 3.1)
        d.line([(x, y), (x, H)], fill=(24, 34, 62)); d.line([(x + 1, y), (x + 1, H)], fill=(24, 34, 62))
        if (x // 2 + int(T * 8)) % 7 == 0: d.point((x, y), fill=(200, 210, 240))
    # 北风从海上升起来，冲着崖边怒吼
    wy = lerp(300, 108, eout(lt / 2.2))
    M.wind(img, 360, wy, 4.5, T, 'roar' if lt > 1.5 else 'sad', flip=True)
    M.streaks(img, d, T, (0, 20, W, 240), n=40, speed=520, seed=9, dirx=-1)
    # 悬崖和他
    d.polygon([(0, 150), (150, 150), (176, 160), (190, 210), (200, H), (0, H)], fill=(20, 18, 30))
    d.line([(0, 150), (150, 150), (176, 160)], fill=(46, 42, 60))
    person(img, 'boy', 150, 150, view='side', pose='stand', expr='down' if lt < 3 else 'sad', s=2, shade=(0.8, 0.8, 0.95))
    # 一圈红叶绕着他转
    for j in range(36):
        r = rng(j * 3)
        a = T * (1.4 + r.random()) + j
        rad = 30 + r.random() * 40
        x = 150 + math.cos(a) * rad; y = 116 + math.sin(a) * rad * 0.45 + 10 * math.sin(T + j)
        M.leaf_bit(d, x, y, T, j)
    pix.rain(d, T, 0, W, 0, H, 150, (110, 120, 170), speed=420, slant=8, ln=8)
    for b in bolts:
        if flash(img, T, b): shake(img, T - b, 3, 0.25)
    vig(img, 0.45, (0, 0, 10))


def s_face(img, d, lt, dur, T, A):
    sky(img, STORMNIGHT, 0, H, 6)
    for k in range(4):
        r = rng(k)
        cloud(d, (r.uniform(0, W) + T * 50) % (W + 160) - 100, r.uniform(0, 140), 4, (36, 36, 58), (28, 28, 46))
    eyes = props.bust(img, d, 'boy', 240, 34, 6, 'closed' if lt < 1.5 else 'sad', wind=1.0, T=T)
    if lt > 1.8:                                                         # 一滴眼泪
        ex, ey = eyes[1]
        k = clamp((lt - 1.8) / 1.2)
        d.rectangle([ex, ey + 8 + k * 30, ex + 3, ey + 13 + k * 30], fill=(150, 210, 255))
    pix.rain(d, T, 0, W, 0, H, 120, (130, 140, 190), speed=460, slant=6, ln=10)
    for j in range(5):                                                   # 前景飞过的大片红叶
        k = ((lt * 0.6 + j / 5) % 1)
        M.leaf(img, -30 + k * 560, 40 + j * 44 + 20 * math.sin(k * 6 + j), 2 + j % 2, T, spin=2, ph=j)
    flash(img, T, T - lt + 0.05, 0.2)
    vig(img, 0.45, (0, 0, 10))


def s_shout(img, d, lt, dur, T, A):
    sky(img, STORMNIGHT, 0, H, 6)
    # 云层裂开一道光
    op = eout(lt / 1.6)
    tfill(img, 'polygon', [(240 - 20 * op, 0), (240 + 20 * op, 0), (240 + 120 * op, 230), (240 - 120 * op, 230)], (255, 240, 220), 0.18 * op)
    for side in (-1, 1):
        for k in range(3):
            cloud(d, 240 + side * (40 + 50 * op + k * 70) - (0 if side > 0 else 90), 6 + k * 18, 3, (44, 42, 66), (34, 32, 52))
    glow(img, 240, 54, 60, (255, 120, 120), 0.4 + 0.3 * thump(T, 0.4))
    M.leaf(img, 240, 54 + 4 * math.sin(T * 2), 3, T, spin=0.4)
    # 喊出去的声波一圈圈散开
    for j in range(4):
        k = ((lt * 1.2 + j / 4) % 1)
        r = 10 + k * 160
        d.ellipse([240 - r, 128 - r * 0.6, 240 + r, 128 + r * 0.6], outline=lerpc((255, 255, 255), (50, 50, 80), k))
    d.polygon([(120, H), (180, 236), (300, 236), (360, H)], fill=(20, 18, 30))
    person(img, 'boy', 240, 240, view='front', pose='stand', expr='surprised', arms='spread', s=3, shade=(0.85, 0.85, 1.0))
    pix.rain(d, T, 0, W, 0, H, 100, (130, 140, 190), speed=420, slant=5, ln=8)
    vig(img, 0.4, (0, 0, 10))


def s_rise(img, d, lt, dur, T, A):
    up = ease(lt / 3.0)
    sky(img, mix_stops(STORMNIGHT, ((0, (4, 6, 26)), (0.6, (16, 22, 64)), (1, (40, 50, 110))), up), 0, H, 6)
    stars(d, T, H, up, 160)
    moon(d, 360, lerp(-40, 60, up), 22)
    glow(img, 360, lerp(-40, 60, up), 70, (210, 220, 255), 0.35 * up)
    # 一层层云往下掉（镜头往上升），最后在脚下铺成云海
    for k in range(10):
        r = rng(k * 9)
        y = (r.uniform(-100, 300) + lt * 140) % 420 - 100
        if lt > 2.4: y = max(y, lerp(y, 230 + r.uniform(0, 30), ease((lt - 2.4) / 0.6)))
        cloud(d, r.uniform(-40, W - 60), y, 3 + r.random() * 2, lerpc((50, 50, 76), (180, 190, 230), up), lerpc((40, 40, 62), (140, 150, 200), up))
    lx, ly = 240 + 10 * math.sin(T * 2), 140 - 30 * up
    glow(img, lx, ly, 30, (255, 130, 130), 0.4)
    M.leaf(img, lx, ly, 3, T, spin=0.6)
    for j in range(3):                                                    # 托着它往上的风
        a = T * 3 + j * 2.1
        pts = [(lx + math.cos(a + u * 3) * (14 + u * 20), ly + 30 - u * 50 + math.sin(a + u * 3) * 6) for u in np.linspace(0, 1, 12)]
        d.line(pts, fill=(220, 236, 255))


def s_fall(img, d, lt, dur, T, A):
    sky(img, ((0, (4, 6, 26)), (0.6, (16, 22, 64)), (1, (40, 50, 110))), 0, H, 6)
    for i in range(70):                                                   # 星星被拉成往上飞的线
        r = rng(i * 3)
        x = r.uniform(0, W); y = (r.uniform(0, H) - lt * 300 * (0.5 + r.random())) % H
        d.line([(x, y), (x, y + 6 + r.random() * 10)], fill=(150, 160, 220) if i % 3 else (240, 240, 255))
    for k in range(4):
        r = rng(k * 11)
        y = (r.uniform(0, 400) - lt * 260) % 420 - 80
        cloud(d, r.uniform(-40, W - 60), y, 3.5, (60, 70, 120), (44, 52, 96))
    lx, ly = 300 + 20 * math.sin(lt), 40 - lt * 10
    M.leaf(img, lx, ly, 1, T, spin=1)
    sway = 6 * math.sin(lt * 2)
    person(img, 'boy', 220 + sway, 170 + 4 * math.sin(lt * 5), view='front', pose='jump', expr='closed', arms='spread', s=2)
    vig(img, 0.4, (0, 0, 10))


def clock_bits(img, d, T, cx, cy, spread, n=9, seed=3, a=1.0):
    """漂浮的钟面碎片和小齿轮"""
    for j in range(n):
        r = rng(j * 17 + seed)
        ang = r.uniform(0, 6.28) + T * 0.2 * (1 if j % 2 else -1)
        rad = spread * r.uniform(0.4, 1.0)
        x, y = cx + math.cos(ang) * rad, cy + math.sin(ang) * rad * 0.5 + 6 * math.sin(T + j)
        if j % 3 == 0:
            M.gear(d, x, y, 5 + j % 4, T * (1 if j % 2 else -1), 7, (120, 110, 90), (70, 60, 50))
        else:
            rr = 10 + j % 5 * 3
            a0 = r.uniform(0, 360) + T * 30 * (1 if j % 2 else -1)
            d.pieslice([x - rr, y - rr, x + rr, y + rr], a0, a0 + 50, fill=(236, 226, 200), outline=(90, 70, 60))
            d.line([(x, y), (x + math.cos(math.radians(a0 + 25)) * rr * 0.8, y + math.sin(math.radians(a0 + 25)) * rr * 0.8)], fill=(60, 44, 46))


def void_floor(img, d, T):
    img.paste((10, 10, 22), (0, 0, W, H))
    glow(img, 240, 200, 260, (60, 70, 130), 0.3, 60)
    d.rectangle([0, 200, W, H], fill=(16, 18, 36))
    d.line([(0, 200), (W, 200)], fill=(70, 80, 130))


def s_land(img, d, lt, dur, T, A):
    void_floor(img, d, T)
    clock_bits(img, d, T, 240, 110, 200, 12)
    touch = 0.5
    y = lerp(-20, 200, eout(lt / touch)) if lt < touch else 200
    person(img, 'boy', 240, y, view='front', pose='stand', expr='down', arms='down' if lt > touch else 'up', s=2)
    props.reflect(img, 201, 60, T, (10, 10, 30), 0.6, 1.0, src_h=90)
    if lt > touch:
        for j in range(3):
            k = clamp((lt - touch - j * 0.4) / 1.8)
            if 0 < k < 1:
                r = 8 + k * 200
                d.ellipse([240 - r, 202 - r * 0.12, 240 + r, 202 + r * 0.12], outline=lerpc((180, 200, 255), (16, 18, 36), k))
    vig(img, 0.45, (0, 0, 0))


def s_burst(img, d, lt, dur, T, A):
    void_floor(img, d, T)
    boom = 0.35
    cx, cy = 240, 92
    if lt < boom:
        M.big_clock(img, d, cx, cy, 64, 1.2, -lt * 8, T, crack=lt / boom, glow_a=0.3)
    else:
        k = lt - boom
        for j in range(16):                                               # 光束
            a = j * math.pi / 8 + k * 0.4
            w = 0.07
            L = 400 * eout(k / 0.4)
            tfill(img, 'polygon', [(cx, cy), (cx + math.cos(a - w) * L, cy + math.sin(a - w) * L), (cx + math.cos(a + w) * L, cy + math.sin(a + w) * L)],
                  (255, 240, 210), 0.22 * clamp(1 - k / 2.4))
        glow(img, cx, cy, 120, (255, 230, 200), 0.6 * clamp(1 - k / 1.5))
        clock_bits(img, d, T, cx, cy, 30 + 260 * eout(k / 1.4), 14, seed=9)
        if k < 0.3: dither_fade(img, 1 - k / 0.3, (255, 252, 240))
        if k < 0.45: shake(img, k, 6, 0.45)
    person(img, 'boy', 240, 200, view='front', pose='stand', expr='surprised' if lt > boom else 'down', s=2)
    props.reflect(img, 201, 60, T, (10, 10, 30), 0.6, 1.0, src_h=90)
    vig(img, 0.4, (0, 0, 0))


# ================================================================ 风停了：极光、雪、她、接住和放手
def snowy_night(img, d, T, aur=0.5):
    sky(img, NIGHT_W, 0, 210, 6)
    stars(d, T, 190, 1.0, 160)
    if aur > 0: M.aurora(img, T, 20, 120, aur)
    ridge(d, 180, 26, 0.012, 0.4, (40, 50, 92))
    snowfield(img, d, T, 200)


def s_aurora(img, d, lt, dur, T, A):
    snowy_night(img, d, T, 0.55)
    hill(d, 300, 170, 200, (220, 230, 248))
    M.tree(img, d, 330, 176, 120, T, seed=3, sway=0.4 * math.sin(T * 0.7), leaf_on=lambda j, r: False, snow=1.0, spread=0.62,
           bark=(52, 46, 66), bark_d=(36, 32, 52))
    person(img, 'boy', 236, 188, view='back', pose='sit', s=2)
    M.wind(img, 280, 176, 1.25, T, 'calm', flip=True, tail=False)
    pix.snow(d, T, n=80, speed=12, wind=3)
    props.zoom(img, lerp(1.35, 1.0, ease(lt / 7.0)), 260, 150)
    vig(img, 0.4, (4, 6, 20))


def s_memory_girl(img, d, lt, dur, T, A):
    snowy_night(img, d, T, 0.25)
    turn = 0.6; go = 1.3
    x, y = 240, 214
    if lt < go:
        view = 'back' if lt < turn else 'front'
        glow(img, x, y - 40, 50, (255, 170, 170), 0.25)
        person(img, 'girl', x, y, view=view, pose='stand', expr='smile', s=2)
    else:
        k = lt - go                                                       # 化成红叶飞走
        props.ghost(img, 'girl', x, y, 2, clamp(1 - k / 0.6), view='front', pose='stand', expr='smile')
        for j in range(60):
            r = rng(j * 7)
            sx, sy = x + r.uniform(-14, 14), y - r.uniform(0, 80)
            q = k - r.random() * 0.5
            if q < 0: continue
            M.leaf_bit(d, sx + 120 * q * q + 40 * q, sy - 60 * q + 8 * math.sin(q * 5 + j), T, j)
    pix.snow(d, T, n=80, speed=12, wind=3)
    vig(img, 0.4, (4, 6, 20))


def s_catch(img, d, lt, dur, T, A):
    sky(img, ((0, (10, 14, 40)), (1, (40, 50, 96))), 0, H, 5)
    props.bokeh(img, T, 12, [(150, 170, 230), (200, 210, 255)], seed=6, a=0.25)
    land = 1.6
    M.cupped_hands(img, d, 240, 178, 4, 0.0)
    if lt < land:
        k = lt / land
        M.leaf(img, 240 + 40 * math.sin(lt * 3) * (1 - k), lerp(-20, 160, ease(k)), 3, T, spin=0.8)
    else:
        glow(img, 240, 164, 40, (255, 160, 140), 0.45 * clamp((lt - land) / 0.4))
        M.leaf(img, 240, 164, 3, T, spin=0, rot=-20)
    pix.snow(d, T, n=70, speed=14, wind=3)
    vig(img, 0.45, (4, 6, 20))


def s_release(img, d, lt, dur, T, A):
    sky(img, NIGHT_W, 0, 210, 6)
    stars(d, T, 190, 1.0, 160)
    mx, my = 360, 64
    glow(img, mx, my, 90, (210, 220, 255), 0.4)
    moon(d, mx, my, 30)
    ridge(d, 186, 22, 0.012, 0.4, (40, 50, 92))
    snowfield(img, d, T, 204)
    person(img, 'boy', 170, 214, view='side', pose='stand', expr='closed' if lt > 1.2 else 'sad', arms='up' if lt < 2.6 else 'down', s=2)
    # 叶子从他手里升起来；北风轻轻绕着它，一圈圈把它托向月亮
    k = ease((lt - 0.4) / 3.6)
    lx = lerp(174, mx - 8, k) + 18 * math.sin(lt * 2.4) * (1 - k)
    ly = lerp(150, my + 6, k)
    a = lt * 2.4
    M.wind(img, lx + math.cos(a) * 36, ly + math.sin(a) * 14 + 10, 1.0, T, 'calm', flip=math.sin(a) > 0, tail=True)
    s = 2 if k < 0.6 else 1
    M.leaf(img, lx, ly, s, T, spin=0.5)
    glow(img, lx, ly, 16, (255, 150, 140), 0.3)
    pix.snow(d, T, n=60, speed=10, wind=2)
    vig(img, 0.4, (4, 6, 20))


# ================================================================ 片名跟着节拍连砸三次
def slam_times(T0):
    b = [x for x in pix.AUDIO['beats'] if x > T0 - 0.2][:4]
    while len(b) < 4: b.append((b[-1] if b else T0) + 0.82)
    return b


def s_slam(img, d, lt, dur, T, A):
    T0 = T - lt
    hits = slam_times(T0)
    img.paste((26, 4, 14), (0, 0, W, H))
    last = max([h for h in hits if h <= T] or [T0])
    p = clamp(1 - (T - last) / 0.4)
    glow(img, 240, 135, 260, (200, 20, 50), 0.35 + 0.35 * p, 160)
    for j in range(24):                                                    # 放射状的速度线
        a = j * math.pi / 12 + T * 0.3
        r0 = 60 + 20 * math.sin(T * 3 + j)
        d.line([(240 + math.cos(a) * r0, 135 + math.sin(a) * r0 * 0.6), (240 + math.cos(a) * 400, 135 + math.sin(a) * 240)],
               fill=lerpc((60, 10, 26), (140, 30, 50), p))
    title = title_str()
    spots = [(130, 70, 3), (350, 70, 3), (240, 150, 5)]
    for i, (hx, hy, sc) in enumerate(spots):
        if T < hits[i]: continue
        k = T - hits[i]
        s_ = sc + (1 if k < 0.08 else 0)
        jit = int(3 * math.sin(T * 40)) if k < 0.3 else 0
        if i == 2 and k > 0.5:                                           # 最后一下：红蓝错开的故障感
            big_text(img, title, hx - 3, hy, s_, top=(90, 220, 255), bot=(40, 120, 200), line=(10, 40, 80), out=(10, 10, 30))
        big_text(img, title, hx + jit, hy, s_, top=(255, 170, 170), bot=(230, 40, 64), line=(110, 10, 34), out=(20, 2, 10))
    if T >= hits[3]:                                                       # 第四拍：一道裂缝横过画面
        k = clamp((T - hits[3]) / 0.4)
        pts = [(x, 150 + (8 if (x // 20) % 2 else -8)) for x in range(0, int(W * k) + 1, 20)]
        if len(pts) > 1: d.line(pts, fill=(255, 240, 240), width=2)
    for h in hits:
        if 0 <= T - h < 0.3: shake(img, T - h, 5, 0.3)
        if 0 <= T - h < 0.1: dither_fade(img, 0.5 * (1 - (T - h) / 0.1), (255, 230, 230))
    vig(img, 0.45, (8, 0, 4))


def s_moon_leaf(img, d, lt, dur, T, A):
    sky(img, NIGHT_W, 0, H, 6)
    stars(d, T, H, 1, 200)
    glow(img, 240, 120, 150, (210, 220, 255), 0.35)
    moon(d, 240, 120, 74, col=(246, 240, 214))
    k = lt / 2.4
    lx, ly = lerp(80, 420, k), 120 + 30 * math.sin(k * 3)
    im = M.leaf_img(3, max(4, int(round(8 * abs(math.cos(T * 1.5))))), int(round(20 * math.sin(T * 2) / 15)) * 15)
    a = np.array(im); a[a[..., 3] > 0, :3] = (30, 26, 44)
    sil = Image.fromarray(a)
    dpaste(img, sil, lx - sil.width / 2, ly - sil.height / 2)
    for j in range(3):
        q = (T * 1.4 + j / 3) % 1
        tfill(img, 'line', [(lx - 18 - q * 40, ly - 4 + j * 4), (lx - 8 - q * 40, ly - 4 + j * 4)], (230, 236, 255), (1 - q) * 0.7)
    vig(img, 0.4, (4, 6, 20))


# ================================================================ 片尾：天亮了，新芽，他走远；金色补好的片名
def s_dawn(img, d, lt, dur, T, A):
    sky(img, DAWN, 0, 200, 6)
    sy = lerp(190, 120, ease(lt / 12))
    glow(img, 120, sy, 160, (255, 200, 150), 0.5, 80)
    d.ellipse([100, sy - 20, 140, sy + 20], fill=(255, 236, 196))
    ridge(d, 184, 24, 0.012, 0.8, (150, 130, 170))
    snowfield(img, d, T, 200, col=(240, 226, 230), shade=(214, 196, 210))
    hill(d, 320, 172, 200, (246, 234, 236))
    bud = ease((lt - 4.0) / 3.0)
    M.tree(img, d, 330, 178, 120, T, seed=3, sway=0.3 * math.sin(T * 0.7), leaf_on=lambda j, r: False, snow=clamp(1 - lt / 10), spread=0.62,
           bark=(90, 64, 70), bark_d=(64, 44, 52), bud=bud)
    if 4.0 < lt < 5.2:
        twinkle(d, 300, 100, (lt - 4.0) / 1.2, (220, 255, 200), 5)
    # 北风轻轻绕着树转
    a = lt * 0.8
    M.wind(img, 330 + math.cos(a) * 90, 110 + math.sin(a) * 26, 1.0, T, 'calm', flip=math.sin(a) > 0)
    # 他踩着雪往左边的太阳走远，身后一串脚印
    k = clamp((lt - 1.0) / 10.0)
    bx = lerp(250, -30, k)
    for j in range(int((250 - bx) / 8)):
        fx = 250 - j * 8
        d.rectangle([fx - 2, 232 + (j % 2) * 3, fx, 233 + (j % 2) * 3], fill=(196, 180, 200))
    person(img, 'boy', bx, 236, view='side', pose='walk', ph=wph(lt, 4), expr='smile', s=1, flip=True)
    pix.snow(d, T, n=int(60 * clamp(1 - lt / 9)), speed=10, wind=2)
    vig(img, 0.3, (60, 40, 70))


def s_end(img, d, lt, dur, T, A):
    sky(img, NIGHT_W, 0, H, 6)
    stars(d, T, H, 1, 200)
    cells, box = title_cells()
    bx0, by0, bx1, by1 = box
    glow(img, W / 2, sc_a.TITLE_CY, 170, (255, 90, 100), 0.22, 80)
    for (cx, cy, col, u, r) in cells:
        d.rectangle([cx, cy, cx + TS - 1, cy + TS - 1], fill=col)
    # 裂缝用金子补好了
    pts = [(crack_x(y, box), y) for y in np.linspace(by0 + 4, by1 - 4, 25)]
    gk = ease((lt - 0.6) / 1.6)
    if gk > 0:
        n = max(2, int(len(pts) * gk))
        d.line(pts[:n], fill=(255, 206, 90), width=3)
        d.line([(x - 1, y) for x, y in pts[:n]], fill=(255, 246, 200), width=1)
        glow(img, pts[n - 1][0], pts[n - 1][1], 16, (255, 220, 120), 0.5 * (1 - gk) + 0.1)
    a = clamp((lt - 1.5) / 0.8)
    artist = artist_str()
    if artist: text(img, '演唱 · ' + artist, W / 2, by1 + 16, col=(236, 226, 255), alpha=a)
    text(img, '像 素 动 画 M V', W / 2, by1 + 36, col=(170, 160, 210), font=FONT_S, alpha=a * 0.9)
    M.leaf(img, 120 + 30 * math.sin(lt * 0.8), lerp(-20, 290, lt / 9.5), 2, T, spin=0.5)
    vig(img, 0.4, (4, 6, 20))
    fade = ease((lt - 8.6) / 1.6)
    if lt < 0.8: dither_fade(img, 1 - lt / 0.8, (0, 0, 0))
    if fade > 0: dither_fade(img, fade, (0, 0, 0))
