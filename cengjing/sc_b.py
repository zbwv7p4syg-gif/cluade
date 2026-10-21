"""曾经是情侣 · 第二段主歌到第一段副歌之前。

很多年过去，大树开花、长叶、落叶、积雪转了好几轮；她把头发盘了起来，一个人在夜里种下一片会发光的花田。
三句"一样"都用左右分屏：左边是那时候的她（旧照片的颜色），右边是现在的她，做着一样的事、笑得一样灿烂。
然后回到当年：一条路，到了岔口两人分头走，红线越拉越长；他一个人顶着风雪往前走，路没有尽头；
在一颗小小的星球上走过美好的一面和难看的一面；深夜的站台上两人各坐长椅的一头；沙漏里的长椅和人一点点漏下去。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
from props import *          # noqa: F401,F403
from pix import (W, H, FONT, FONT_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky, stars,
                 person, wph, put, twinkle, sparkle, hills, moon, cloud, darken, dither_fade, grade, vig, vgrad, BAYER, bayer)
from sc_a import dpaste, winds


def canvas():
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im); d.fontmode = '1'
    return im, d


def split(img, left, right, x=240, T=0.0, labels=('那时', '现在'), sep=1.0, left_sepia=0.75):
    """左右分屏：left/right 各自画在整张画布上，左边取左半、右边取右半；中间一根微微摆动的红线"""
    li, ld = canvas(); left(li, ld)
    ri, rd = canvas(); right(ri, rd)
    if left_sepia: li = sepia(li, left_sepia)
    img.paste(ri)
    img.paste(li.crop((0, 0, int(x), H)), (0, 0))
    d = ImageDraw.Draw(img)
    if sep > 0:
        pts = [(x + 1.5 * math.sin(y * 0.05 + T * 3), y) for y in range(0, int(H * sep) + 1, 3)]
        d.line([(px + 1, py) for px, py in pts], fill=RED_D, width=2)
        d.line(pts, fill=RED)
    if labels:
        text(img, labels[0], 30, 16, (255, 240, 220), (60, 40, 30), FONT_S)
        text(img, labels[1], W - 30, 16, (255, 255, 255), (40, 30, 60), FONT_S)


# ================================================================ 四季轮转
SEASON = [  # 叶子、叶子亮部、地面、地面亮部
    ((255, 176, 204), (255, 220, 232), (120, 190, 110), (170, 220, 130)),     # 春
    ((60, 150, 84), (100, 190, 96), (84, 160, 84), (130, 196, 100)),          # 夏
    ((222, 118, 48), (250, 176, 70), (170, 140, 70), (210, 180, 96)),         # 秋
    ((150, 150, 170), (200, 200, 220), (236, 240, 250), (255, 255, 255)),     # 冬
]


def season_cols(s):
    i = int(s * 4) % 4; f = ease(((s * 4) % 1 - 0.65) / 0.35)
    a, b = SEASON[i], SEASON[(i + 1) % 4]
    return [lerpc(x, y, f) for x, y in zip(a, b)], i, f


def bare_tree(d, x, base, s, col):
    d.rectangle([x - 3 * s, base - 30 * s, x + 3 * s, base], fill=col)
    for ang, ln, y0 in [(-0.8, 22, 28), (0.7, 24, 26), (-0.3, 18, 34), (0.3, 20, 33), (-1.2, 14, 20), (1.1, 14, 22)]:
        x1 = x + math.sin(ang) * ln * s; y1 = base - y0 * s - math.cos(ang) * ln * s
        d.line([(x, base - y0 * s), (x1, y1)], fill=col, width=max(1, int(2 * s)))


def s_years(img, d, lt, dur, T, A):
    end = dur - 1.9
    yrs = 4 * (clamp(lt / end) ** 1.35) + max(0.0, lt - end) * 0.03
    dayp = yrs * 2
    day = 0.5 + 0.5 * math.cos(2 * math.pi * dayp)
    (leaf, leaf_l, gnd, gnd_l), si, sf = season_cols(yrs)
    winter = clamp(1 - abs((yrs % 1) - 0.87) / 0.13)              # 冬天叶子掉光
    night = ((0, (10, 12, 36)), (0.6, (26, 30, 70)), (1, (50, 46, 96)))
    noon = ((0, (90, 150, 230)), (0.6, (150, 200, 245)), (1, (210, 236, 250)))
    sky(img, mix_stops(night, noon, day), 0, 200)
    stars(d, T, 190, 1 - day, 120)
    th = 2 * math.pi * dayp
    for k, (col, r) in enumerate((((255, 240, 180), 12), ((250, 244, 220), 9))):
        a = th + math.pi * k
        x, y = 240 - 230 * math.sin(a), 210 - 170 * math.cos(a)
        if y < 205:
            if k == 0: glow(img, x, y, 40, (255, 220, 150), 0.4); d.ellipse([x - r, y - r, x + r, y + r], fill=col)
            else: moon(d, x, y, r)
    # 远山和地面
    pix.hills(d, 176, 6, 0.02, 1.2, lerpc(lerpc(gnd, (60, 70, 110), 0.5), (20, 22, 44), 1 - day))
    gcol = lerpc(gnd, (24, 30, 50), (1 - day) * 0.75); gl = lerpc(gnd_l, (40, 48, 70), (1 - day) * 0.75)
    d.ellipse([-60, 196, 540, 380], fill=gcol)
    d.arc([-60, 196, 540, 380], 200, 340, fill=gl)
    # 大树
    tcol = lerpc((110, 76, 56), (34, 30, 44), (1 - day) * 0.7)
    bare_tree(d, 240, 214, 2.0, tcol)
    lc = lerpc(leaf, (30, 34, 60), (1 - day) * 0.6); ll = lerpc(leaf_l, (50, 56, 90), (1 - day) * 0.6)
    leaf_a = 1 - winter
    if leaf_a > 0.02:
        r = rng(9)
        for j in range(26):
            bx, by = r.uniform(-62, 62), r.uniform(-120, -56)
            rad = r.uniform(12, 22) * (0.4 + 0.6 * leaf_a)
            if abs(bx) > 70 - rad: continue
            d.ellipse([240 + bx - rad, 214 + by - rad * 0.8, 240 + bx + rad, 214 + by + rad * 0.8], fill=lc)
            d.ellipse([240 + bx - rad * 0.6, 214 + by - rad * 0.8, 240 + bx + rad * 0.2, 214 + by - rad * 0.1], fill=ll)
    if winter > 0.3:                                               # 积雪
        d.ellipse([-60, 196, 540, 380], outline=(255, 255, 255))
        for j in range(8): d.line([(240 - 30 + j * 8, 214 - 60 - (j % 3) * 6), (240 - 26 + j * 8, 214 - 60 - (j % 3) * 6)], fill=(255, 255, 255))
    # 季节的粒子
    if si == 0: pix.petals(d, T, 26, speed=18, wind=14, seed=1)
    elif si == 1 and day < 0.5: pix.fireflies(img, d, T, 10, (60, 150, 420, 240), seed=2)
    elif si == 2: pix.petals(d, T, 30, cols=[(230, 120, 50), (250, 180, 70), (200, 90, 40)], speed=26, wind=20, seed=4)
    elif si == 3: pix.snow(d, T, 90, 26, seed=3)
    # 日历一页页翻过去
    yr = int(yrs) + 1
    d.rectangle([22, 20, 70, 70], fill=(250, 248, 240), outline=pix.OUT)
    d.rectangle([22, 20, 70, 32], fill=RED, outline=pix.OUT)
    for x in (32, 60): d.rectangle([x, 16, x + 2, 24], fill=(90, 90, 100))
    text(img, str(yr), 46, 50, (60, 40, 50), None, scale=2, shadow=False)
    flip = (yrs % 1)
    if flip < 0.25 and yrs > 0.5:
        u = flip / 0.25
        d.polygon([(22, 32), (70, 32), (70 - 10 * u, lerp(70, 140, u)), (22 + 30 * u, lerp(70, 150, u))], fill=(236, 232, 222), outline=pix.OUT)
    # 最后时间慢下来：盘起头发的她站在树下
    a = ease(span(lt, end + 0.2, end + 1.0))
    if a > 0:
        person(img, 'girl', 196, 236, 'old', 'side', 'stand', 0, 'smile', s=2, alpha=a)
        if a < 1: twinkle(d, 196, 180, a, (255, 255, 255), 6)
    vig(img, 0.35, (16, 12, 30))


# ================================================================ 夜里种下一片发光的花田
DREAM = ((0, (8, 8, 34)), (0.5, (34, 26, 84)), (1, (92, 56, 140)))
DREAM_COLS = [(110, 230, 255), (255, 150, 200), (255, 220, 110), (190, 160, 255), (150, 255, 200)]


@lru_cache(None)
def dream_flowers(n=190):
    r = rng(77); out = []
    for i in range(n):
        y = 172 + (r.random() ** 0.7) * 96
        x = r.uniform(-10, W + 10)
        sc = (y - 166) / 100
        gx = (x - 240) / max(0.2, sc)
        dist = math.hypot(gx, (y - 232) * 2.4)
        out.append((x, y, dist, r.randrange(5), r.random()))
    return sorted(out, key=lambda f: f[1])


def dream_world(img, d, T, glow_on=1.0):
    sky(img, DREAM, 0, 170)
    stars(d, T, 168, 1.0, 220)
    for j in range(3):                                     # 极光一样的光带
        col = [(110, 230, 255), (255, 150, 220), (170, 140, 255)][j]
        for x in range(0, W, 2):
            y = 40 + j * 22 + 14 * math.sin(x * 0.012 + T * 0.4 + j * 2) + 6 * math.sin(x * 0.04 - T * 0.7)
            if (x // 2 + j) % 2 == 0: d.point((x, y), fill=lerpc((34, 26, 84), col, 0.5))
    glow(img, 384, 54, 60, (220, 220, 255), 0.35)
    moon(d, 384, 54, 20, (246, 242, 255), (210, 204, 236))
    pix.hills(d, 166, 8, 0.016, 0.7, (52, 40, 100))
    pix.hills(d, 172, 5, 0.03, 2.1, (40, 32, 82))
    pix.sky(img, ((0, (40, 32, 82)), (1, (22, 18, 50))), 172, H)


def dream_field(img, d, lt, T, t0=0.0, speed=0.0085):
    for x, y, dist, ci, rv in dream_flowers():
        ts = t0 + dist * speed
        k = lt - ts
        if k < 0: continue
        col = DREAM_COLS[ci]
        sc = (y - 166) / 100
        hgt = (3 + 9 * sc) * eout(clamp(k / 0.35))
        sw = math.sin(T * 1.6 + x * 0.05) * 1.2 * sc
        d.line([(x, y), (x + sw, y - hgt)], fill=(70, 140, 120))
        if k > 0.3:
            op = eback(clamp((k - 0.3) / 0.3))
            fx, fy = x + sw, y - hgt
            if k < 0.9: glow(img, fx, fy, 10 * sc + 4, col, 0.5 * (1 - (k - 0.3) / 0.6))
            r = max(1, int((1 + 2.4 * sc) * op))
            d.ellipse([fx - r, fy - r, fx + r, fy + r], fill=col)
            d.point((fx, fy), fill=(255, 255, 240))
            if rv < 0.18:                                  # 有的花冒出一颗光点往上飘
                u = ((T * 0.5 + rv * 7) % 1)
                d.point((fx + 3 * math.sin(T * 2 + rv * 9), fy - u * 60), fill=lerpc(col, (34, 26, 84), u))


def s_dreamfield(img, d, lt, dur, T, A):
    dream_world(img, d, T)
    land = 1.05
    dream_field(img, d, lt, T, land)
    if lt > land:                                          # 种子落地，一圈光往外扩
        k = lt - land
        for j in range(3):
            rr = (k - j * 0.25) * 260
            if rr > 0:
                d.ellipse([240 - rr, 232 - rr * 0.22, 240 + rr, 232 + rr * 0.22], outline=lerpc((180, 240, 255), (40, 32, 82), clamp(rr / 400)))
    arms = 'flowers' if lt < 0.6 else ('up' if lt > 4.0 else 'down')
    expr = 'smile' if lt < 4.0 else 'happy'
    person(img, 'girl', 240, 234, 'old', 'front', 'stand', 0, expr, arms, s=2)
    if lt < land:                                          # 手里发光的种子，落到地上
        f = clamp((lt - 0.55) / 0.5)
        sx, sy = 240, lerp(206, 233, ein(f))
        glow(img, sx, sy, 18, GOLD_L, 0.7)
        d.rectangle([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 250, 220))
    else:
        glow(img, 240, 233, 30, (180, 240, 255), 0.4 * (0.6 + 0.4 * math.sin(T * 4)))
    if lt > 4.0:
        burst(img, d, lt - 4.0, 240, 180, life=1.6, scale=1.2)
    pix.fireflies(img, d, T, 16, (0, 120, W, 260), (200, 255, 230), 7)
    vig(img, 0.4, (8, 6, 24))


# ================================================================ 分屏：锄地
def hoe_pose(T):
    """锄地的动作跟着拍子：拍点上锄下去"""
    k = T - last_beat(T)
    if k < 0.18: return 'down', k
    if k < 0.55: return 'mid', k
    return 'up', k


def hoer(img, d, who, age, x, y, s, T, flip=False):
    pose, k = hoe_pose(T)
    arms = {'down': 'reach', 'mid': 'reach', 'up': 'up'}[pose]
    person(img, who, x, y, age, 'side', 'stand', 0, 'happy' if pose == 'down' else 'smile', arms, s=s, flip=flip)
    sg = -1 if flip else 1
    hx, hy = x + sg * (7 if pose != 'up' else 2) * s, y - (13 if pose != 'up' else 23) * s
    if pose == 'down': tip = (x + sg * 18 * s, y - 1)
    elif pose == 'mid': tip = (x + sg * 16 * s, y - 10 * s)
    else: tip = (x + sg * 2 * s, y - 36 * s)
    d.line([(hx - sg * 6 * s * (pose != 'up'), hy + 2 * s * (pose != 'up')), tip], fill=(140, 96, 60), width=max(1, s))
    d.line([tip, (tip[0] - sg * 3 * s, tip[1] + 2 * s)], fill=(170, 176, 190), width=max(1, s + 1))
    if pose == 'down':
        for j in range(5):
            r = rng(int(T * 7) + j)
            d.point((tip[0] + r.uniform(-6, 6), tip[1] - r.uniform(0, 8) * (1 - k / 0.18)), fill=(120, 84, 60))
    return tip


def sprouts(d, T, x0, y, step, t_start, n_max, s=1, flip=False):
    bs = beats_in(t_start, T + 0.01)
    for j, b in enumerate(bs[:n_max]):
        k = T - b - 0.15
        if k < 0: continue
        x = x0 + (j * step) * (-1 if flip else 1)
        g = eback(clamp(k / 0.3))
        hgt = 5 * s * g
        d.line([(x, y), (x, y - hgt)], fill=(80, 170, 80), width=max(1, s // 2))
        d.ellipse([x - 3 * s * g, y - hgt - 2 * s * g, x, y - hgt + 1], fill=(110, 200, 90))
        d.ellipse([x, y - hgt - 2 * s * g, x + 3 * s * g, y - hgt + 1], fill=(130, 220, 100))


def s_till(img, d, lt, dur, T, A):
    t_start = T - lt

    def left(im, dd):                                     # 那时：屋后的小菜园
        sky(im, ((0, (120, 180, 240)), (1, (220, 236, 250))), 0, 190)
        cloud(dd, 40, 40, 1.4, (255, 255, 255), (220, 230, 245))
        dd.rectangle([20, 120, 90, 190], fill=(230, 210, 180)); dd.polygon([(10, 122), (55, 90), (100, 122)], fill=(196, 90, 80))
        dd.rectangle([46, 150, 62, 190], fill=(140, 100, 70)); dd.rectangle([28, 134, 40, 146], fill=(170, 210, 240))
        dd.rectangle([0, 190, 240, H], fill=(150, 110, 76))
        for y in range(200, H, 12): dd.line([(0, y), (240, y)], fill=(120, 86, 60))
        for x in range(100, 240, 10): dd.rectangle([x, 172, x + 2, 192], fill=(200, 170, 130))
        dd.line([(100, 178), (240, 178)], fill=(200, 170, 130)); dd.line([(100, 186), (240, 186)], fill=(200, 170, 130))
        sprouts(dd, T, 150, 236, 14, t_start, 6, 2)
        hoer(im, dd, 'girl', 'young', 112, 238, 2, T)

    def right(im, dd):                                    # 现在：一大片田
        sky(im, ((0, (90, 160, 240)), (0.7, (180, 220, 250)), (1, (250, 230, 200))), 0, 150)
        glow(im, 430, 40, 40, (255, 240, 180), 0.5); dd.ellipse([418, 28, 442, 52], fill=(255, 246, 200))
        pix.hills(dd, 140, 6, 0.02, 1.0, (120, 170, 120))
        dd.rectangle([240, 150, W, H], fill=(140, 104, 72))
        for j in range(-8, 9):                             # 往远处收的田垄
            dd.line([(360 + j * 4, 150), (360 + j * 60, H)], fill=(116, 84, 58))
        for j in range(12):
            r = rng(j + 40)
            x, y = r.uniform(250, 470), r.uniform(156, 200)
            dd.line([(x, y), (x, y - 3)], fill=(90, 170, 80))
        sprouts(dd, T, 400, 236, 14, t_start, 5, 2)
        hoer(im, dd, 'girl', 'old', 362, 238, 2, T)
        for j in range(4): pix.bird(dd, int(300 + j * 16 + (T * 20) % 60), 60 + j * 4, T, (60, 60, 80), j)

    split(img, left, right, T=T)


# ================================================================ 分屏：看流星许愿
def s_hope(img, d, lt, dur, T, A):
    mt = (0.5, 1.5)

    def star_streak(im, dd):
        f = (lt - mt[0]) / (mt[1] - mt[0])
        if 0 <= f <= 1.2:
            hx, hy = lerp(-20, 500, f), lerp(20, 78, f)
            for j in range(40):
                x, y = hx - j * 4, hy - j * 4 * 58 / 520
                dd.point((x, y), fill=lerpc((255, 255, 240), (60, 60, 120), j / 40))
            glow(im, hx, hy, 12, (255, 255, 230), 0.8)

    def wishes(im, dd, x0, y0):
        for j in range(6):
            k = lt - 1.6 - j * 0.3
            if k <= 0: continue
            u = clamp(k / 2.0)
            twinkle(dd, int(x0 + 20 * math.sin(j * 2.1 + k)), int(y0 - u * 140), 0.5 + 0.5 * math.sin(k * 6), (255, 240, 180), 3)

    def left(im, dd):                                     # 那时：在屋里看窗外
        sky(im, NIGHT, 0, H)
        stars(dd, T, H, 1.0, 160)
        star_streak(im, dd)
        wall = Image.new('RGB', (W, H), (120, 84, 70)); wd = ImageDraw.Draw(wall)
        glow(wall, 200, 230, 120, (255, 200, 140), 0.4)
        m = Image.new('L', (W, H), 255); ImageDraw.Draw(m).rectangle([40, 40, 200, 170], fill=0)
        im.paste(wall, (0, 0), m)
        dd.rectangle([0, 200, 240, H], fill=(96, 66, 60))
        dd.rectangle([30, 170, 210, 180], fill=(150, 104, 80), outline=pix.OUT)
        dd.rectangle([36, 34, 46, 176], fill=(210, 110, 120)); dd.rectangle([194, 34, 204, 176], fill=(210, 110, 120))   # 窗帘
        dd.rectangle([40, 40, 200, 170], outline=(150, 104, 80), width=3)
        dd.line([(120, 40), (120, 170)], fill=(150, 104, 80), width=3); dd.line([(40, 105), (200, 105)], fill=(150, 104, 80), width=3)
        person(im, 'girl', 120, 250, 'young', 'back', 'stand', 0, 'closed', 'flowers', s=2)
        wishes(im, dd, 120, 180)

    def right(im, dd):                                    # 现在：花田里抬头
        dream_world(im, dd, T)
        star_streak(im, dd)
        dream_field(im, dd, 10, T)
        person(im, 'girl', 360, 250, 'old', 'back', 'stand', 0, 'closed', 'flowers', s=2)
        wishes(im, dd, 360, 180)

    split(img, left, right, T=T)
    vig(img, 0.3, (8, 6, 24))


# ================================================================ 分屏：两张笑脸合成一个
def sunburst(img, d, cx, cy, T, c1, c2, n=14, r=520):
    img.paste(c1, (0, 0, W, H))
    for j in range(n):
        a0 = T * 0.25 + j * 2 * math.pi / n
        a1 = a0 + math.pi / n
        d.polygon([(cx, cy), (cx + r * math.cos(a0), cy + r * math.sin(a0)), (cx + r * math.cos(a1), cy + r * math.sin(a1))], fill=c2)


def s_smile(img, d, lt, dur, T, A):
    cut = 2.2
    if lt < cut:
        def left(im, dd):
            sunburst(im, dd, 120, 150, T, (255, 214, 140), (255, 196, 110))
            bust(im, dd, 'girl', 120, 40 + 3 * thump(T), 5, 'laugh', 'young')
            for j in range(5): twinkle(dd, 40 + j * 40, 50 + (j % 2) * 120, (T * 1.3 + j * 0.3) % 1, (255, 255, 255), 4)

        def right(im, dd):
            sunburst(im, dd, 360, 150, T, (255, 220, 150), (255, 190, 120))
            bust(im, dd, 'girl', 360, 40 + 3 * thump(T), 5, 'laugh', 'old')
            for j in range(5): twinkle(dd, 280 + j * 40, 60 + (j % 2) * 110, (T * 1.3 + j * 0.3 + 0.5) % 1, (255, 255, 255), 4)
        split(img, left, right, T=T, sep=1.0, left_sepia=0.6)
        return
    k = lt - cut
    # 向日葵田和旋转的日光
    sunburst(img, d, 240, 120, T, (255, 206, 120), (255, 226, 160), 16)
    glow(img, 240, 120, 90, (255, 255, 230), 0.6)
    d.ellipse([214, 94, 266, 146], fill=(255, 246, 210))
    pix.hills(d, 196, 6, 0.02, 1.0, (130, 180, 90))
    d.rectangle([0, 210, W, H], fill=(96, 150, 70))
    bs = beats_in(T - k, T + 0.01)
    r = rng(3)
    for j in range(40):
        x = r.uniform(0, W); y = r.uniform(204, 268)
        tpop = (j % max(1, len(bs) + 1)) * 0.9 + r.uniform(0, 0.6)
        g = eback(clamp((k - tpop * 0.6) / 0.35))
        if g <= 0: continue
        h = (8 + (y - 204) * 0.25) * g
        pix.flower(d, int(x), int(y), (255, 210, 60), 3, (70, 130, 60), int(h))
    # 现在的她，和当年的她叠在一起，慢慢合成一个
    m = ease(span(k, 0.6, 2.4))
    yb = 252 - 4 * thump(T)
    if m < 1:
        ghost = Image.new('RGBA', (W, H))
        person(ghost, 'girl', lerp(170, 240, m), yb, 'young', 'front', 'stand', 0, 'laugh', 'up', s=3)
        ga = np.array(ghost)
        glow(img, lerp(170, 240, m), yb - 60, 60, (255, 240, 200), 0.5 * (1 - m))
        ga[..., :3] = (ga[..., :3] * 0.75 + np.array([255, 220, 170]) * 0.25).astype(np.uint8)
        ga[(BAYER >= 0.85 * (1 - m)), 3] = 0
        g = Image.fromarray(ga); img.paste(g, (0, 0), g)
    person(img, 'girl', lerp(310, 240, m), yb, 'old', 'front', 'stand', 0, 'laugh', 'up', s=3)
    if 2.2 < k < 3.6: burst(img, d, k - 2.2, 240, 150, life=1.4, scale=1.4)
    pix.petals(d, T, 24, cols=[(255, 230, 120), (255, 200, 80), (255, 255, 220)], speed=16, wind=20, seed=6)
    vig(img, 0.25, (60, 30, 20))


# ================================================================ 一条路铺到天边
DUSK2 = ((0, (52, 50, 120)), (0.5, (176, 110, 150)), (0.85, (255, 170, 130)), (1, (255, 214, 160)))


def s_road(img, d, lt, dur, T, A):
    hz = 124
    sky(img, DUSK2, 0, hz + 1)
    glow(img, 240, hz, 110, (255, 210, 160), 0.4, 40)
    pix.hills(d, hz - 4, 5, 0.02, 0.5, (120, 80, 120))
    d.rectangle([0, hz, W, H], fill=(70, 96, 70))
    for j in range(60):
        r = rng(j + 900)
        y = r.uniform(hz + 2, H); x = r.uniform(0, W)
        pix.flower(d, int(x), int(y), r.choice([(255, 200, 220), (255, 240, 160), (220, 220, 255)]), 0, (60, 110, 60), int(1 + (y - hz) * 0.04))
    f = eout(clamp(lt / 1.3))
    yend = lerp(H, hz, f)
    for y in range(int(yend), H):
        sc = (y - hz) / (H - hz)
        hw = 4 + 150 * sc
        d.line([(240 - hw, y), (240 + hw, y)], fill=(98, 92, 104))
        d.point([(240 - hw, y), (240 + hw, y)], fill=(200, 190, 170))
        z = 20 / max(0.02, sc)
        if int(z) % 6 < 3 and sc > 0.03: d.line([(240 - 1 - 2 * sc, y), (240 + 1 + 2 * sc, y)], fill=(250, 230, 170))
    # 路标
    if lt > 1.0:
        a = ease(span(lt, 1.0, 1.4))
        bx, by = 372, 200 + (1 - a) * 30
        d.rectangle([bx, by - 40, bx + 2, by], fill=(110, 80, 60))
        d.polygon([(bx - 18, by - 42), (bx + 22, by - 42), (bx + 28, by - 36), (bx + 22, by - 30), (bx - 18, by - 30)], fill=(250, 240, 220), outline=pix.OUT)
    # 两个人牵着手站在路口
    girl_x, boy_x, y = 222, 258, 262
    person(img, 'girl', girl_x, y, 'young', 'back', 'stand', 0, 'smile', 'hold_r', s=2)
    person(img, 'boy', boy_x, y, 'young', 'back', 'stand', 0, 'smile', 'hold_l', s=2)
    thread(img, d, (girl_x + 13, y - 20), (boy_x - 19, y - 20), 3, RED, glow_a=0.3)
    vig(img, 0.35, (30, 16, 40))


# ================================================================ 岔路口，红线越拉越长
def fork_pos(p, side):
    """p: 0 起点 → 1 岔口 → 2 远处；side -1 往左，+1 往右。返回 (x, y, 缩放)"""
    if p <= 1:
        y = lerp(262, 168, p); x = 240 + side * lerp(16, 8, p)
    else:
        q = p - 1
        y = lerp(168, 120, q); x = lerp(240 + side * 8, 240 + side * 118, q)
    sc = 0.3 + (y - 112) / 150 * 1.7
    return x, y, sc


def s_fork(img, d, lt, dur, T, A):
    hz = 112
    sky(img, DUSK2, 0, hz + 1)
    glow(img, 240, hz, 140, (255, 200, 150), 0.35, 40)
    pix.hills(d, hz - 6, 6, 0.02, 2.0, (120, 80, 120))
    d.rectangle([0, hz, W, H], fill=(64, 90, 66))
    road = (96, 90, 104)
    d.polygon([(150, H), (330, H), (262, 166), (218, 166)], fill=road)
    d.polygon([(218, 168), (244, 168), (148, hz), (134, hz)], fill=road)
    d.polygon([(236, 168), (262, 168), (346, hz), (332, hz)], fill=road)
    d.polygon([(240, 168), (244, 160), (330, hz), (150, hz)], fill=(70, 98, 70))
    pix.tree_round(d, 240, 150, 0.9, (70, 120, 76), (100, 150, 90), (90, 64, 50))
    for x0, y0, x1, y1 in [(150, H, 218, 166), (330, H, 262, 166)]:
        d.line([(x0, y0), (x1, y1)], fill=(190, 180, 160))
    # 两个人走到岔口，各走一边，红线越拉越长
    p = 1.8 * ease(clamp(lt / (dur - 0.2)))
    ph = wph(T, 6)
    gx, gy, gs = fork_pos(p, -1)
    bx, by, bs = fork_pos(p, 1)
    apart = clamp(p - 1)
    gh = (gx + 9 * gs, gy - 15 * gs); bh = (bx - 9 * bs, by - 15 * bs)
    th = thread(img, d, gh, bh, 6 * (1 - apart) + 1, lerpc(RED, (255, 120, 140), apart * 0.5), glow_a=0.2 + 0.3 * apart,
                wob=apart * 1.5, T=T)
    person_s(img, 'girl', gx, gy, gs, 'young', 'back', 'walk', ph, arms='hold_r')
    person_s(img, 'boy', bx, by, bs, 'young', 'back', 'walk', ph + 2, arms='hold_l')
    if apart > 0.6:                                         # 红线绷紧，中间抖出几个小火星
        mx, my = th[len(th) // 2]
        twinkle(d, int(mx), int(my), (T * 3) % 1, RED_L, 3)
    vig(img, 0.4, (30, 16, 40))


# ================================================================ 顶着风雪往前走
def s_trudge(img, d, lt, dur, T, A):
    sky(img, ((0, (20, 24, 44)), (0.7, (60, 70, 96)), (1, (100, 110, 130))), 0, 200)
    off = lt * 14
    for j in range(6):                                      # 远处一排路灯，慢慢往左退
        x = (j * 110 - off * 0.6) % (W + 110) - 40
        pix.lamp(img, d, int(x), 200, 1.0, 50, (50, 54, 72), (255, 220, 160))
    pix.hills(d, 196, 4, 0.03, 0.4, (180, 190, 210))
    d.rectangle([0, 206, W, H], fill=(220, 228, 240))
    for y in range(206, H, 8): d.line([(0, y), (W, y)], fill=(200, 210, 228))
    # 脚印
    for j in range(14):
        x = 196 - 26 - j * 22 + (off % 22)
        if x < 196 - 20: d.rectangle([x, 238 + (j % 2) * 5, x + 5, 240 + (j % 2) * 5], fill=(160, 170, 196))
    # 他弯着腰顶着风雪一步一步走，踩在拍子上差点摔一下
    k = T - last_beat(T)
    dip = 4 * math.exp(-k * 6) if k < 0.6 else 0
    ph = int(lt * 3.2) % 4
    im = pix.char_img('boy', 'old', 'side', 'walk', ph, 'sad', 'auto')
    im = im.resize((im.width * 3, im.height * 3), Image.NEAREST).rotate(-9 - dip * 1.5, resample=Image.NEAREST, expand=True, center=(45, 120))
    img.paste(im, (int(196 - im.width / 2 + 6), int(246 - im.height + 8 + dip)), im)
    for j in range(6):                                      # 围巾往后飘
        x = 200 - j * 5; y = 198 + j * 1.2 + 2 * math.sin(T * 9 + j * 2) * j / 5 + dip
        d.rectangle([x - 4, y, x, y + 2], fill=(196, 52, 64) if j % 2 else (170, 40, 54))
    pix.snow(d, T, 160, 30, (255, 255, 255), seed=2, wind=-40)
    winds(d, T * -1, 6, (230, 236, 250), 260, 20, 200, seed=4)
    vig(img, 0.45, (10, 12, 24))


# ================================================================ 夜里的路和航拍的之字形路
def s_endless(img, d, lt, dur, T, A):
    cut = 2.2
    if lt < cut:
        hz = 120
        sky(img, NIGHT, 0, hz + 1)
        stars(d, T, hz, 1.0, 160)
        glow(img, 240, hz, 80, (255, 190, 140), 0.35, 20)
        d.rectangle([0, hz, W, H], fill=(20, 22, 36))
        d.polygon([(240, hz), (0, H), (W, H)], fill=(44, 44, 56))
        cam = lt * 30
        for j in range(30):                                  # 中线往脚下跑
            z0 = (j * 4 - cam) % 120 + 0.5
            z1 = z0 + 2
            y0 = hz + 150 / z0 * 1.0; y1 = hz + 150 / z1 * 1.0
            if y0 > H: continue
            w0 = 2 * (y0 - hz) / 150 * 1.6 + 0.5
            d.polygon([(240 - w0, y0), (240 + w0, y0), (240 + w0 * 0.8, y1), (240 - w0 * 0.8, y1)], fill=(240, 220, 150))
        for j in range(10):                                  # 路边的灯杆往后掠
            z = (j * 12 - cam) % 120 + 1
            y = hz + 150 / z
            if y > H + 80: continue
            sc = (y - hz) / 150
            for side in (-1, 1):
                x = 240 + side * (60 + 300 * sc)
                hgt = 20 + 200 * sc
                d.line([(x, y), (x, y - hgt)], fill=(70, 70, 90), width=max(1, int(3 * sc)))
                glow(img, x, y - hgt, 6 + 20 * sc, (255, 220, 160), 0.5)
        # 路牌：∞
        z = 14 - lt * 7
        if z > 0.6:
            y = hz + 150 / z; sc = (y - hz) / 150
            x = 240 + 80 + 300 * sc
            d.rectangle([x, y - 60 * sc - 26 * sc, x + 2 * sc + 1, y], fill=(80, 80, 96))
            d.rectangle([x - 20 * sc, y - 92 * sc, x + 24 * sc, y - 60 * sc], fill=(40, 120, 80), outline=(230, 240, 230))
            if sc > 0.15: text(img, '∞', x + 2 * sc, y - 76 * sc, (255, 255, 255), None, scale=max(1, int(sc * 2.2)), shadow=False)
        vig(img, 0.5, (6, 6, 16))
        return
    # 航拍：一条之字形的路一直弯到天边，他是路上的一个小点
    k = lt - cut
    hz = 70
    sky(img, NIGHT, 0, hz + 1)
    stars(d, T, hz, 1.0, 80)
    glow(img, 240, hz, 140, (140, 120, 200), 0.3, 18)
    d.rectangle([0, hz, W, H], fill=(22, 24, 40))
    for j in range(40):
        r = rng(j + 60)
        x, y = r.uniform(0, W), r.uniform(hz + 4, H)
        d.point((x, y), fill=(40, 44, 64))
    cam = k * 0.25
    pts = []
    for j in range(240):
        z = j * 0.12 + cam
        sc = 1 / (1 + j * 0.06)
        y = hz + (H + 20 - hz) * sc
        x = 240 + math.sin(z * 0.9) * 260 * sc
        pts.append((x, y, sc))
    for (x0, y0, s0), (x1, y1, s1) in zip(pts, pts[1:]):
        w = max(1, int(16 * s0))
        d.line([(x0, y0), (x1, y1)], fill=(96, 92, 110), width=w)
    for (x0, y0, s0), (x1, y1, s1) in list(zip(pts, pts[1:]))[::3]:
        if s0 > 0.15: d.line([(x0, y0), (x1, y1)], fill=(230, 210, 150))
    x, y, sc = pts[18]
    person_s(img, 'boy', x, y, 1.0, 'old', 'back', 'walk', wph(T, 4))
    vig(img, 0.5, (6, 6, 16))


# ================================================================ 小星球：美好的一面和难看的一面
@lru_cache(None)
def planet_prop(kind):
    im = Image.new('RGBA', (70, 80)); d = ImageDraw.Draw(im)
    b = 79
    if kind == 'tree':
        pix.tree_round(d, 35, b, 1.3, (80, 170, 90), (130, 210, 110), (120, 80, 56))
        for j in range(8): d.point((20 + j * 4, b - 40 + (j % 3) * 6), fill=(255, 190, 210))
    elif kind == 'house':
        d.rectangle([18, b - 24, 52, b], fill=(255, 236, 210), outline=pix.OUT)
        d.polygon([(12, b - 23), (35, b - 42), (58, b - 23)], fill=(230, 100, 90), outline=pix.OUT)
        d.rectangle([30, b - 12, 38, b], fill=(140, 96, 70)); d.rectangle([22, b - 18, 28, b - 12], fill=(170, 220, 250))
        d.rectangle([44, b - 40, 48, b - 30], fill=(120, 110, 120))
    elif kind == 'flowers':
        for j in range(9): pix.flower(d, 8 + j * 6, b, [(255, 140, 180), (255, 230, 120), (180, 160, 255)][j % 3], j % 3, (70, 150, 70), 5 + (j % 3) * 2)
    elif kind == 'swing':
        d.line([(16, b), (22, b - 40), (48, b - 40), (54, b)], fill=(130, 90, 60), width=2)
        d.line([(30, b - 40), (30, b - 14)], fill=(200, 200, 200)); d.line([(40, b - 40), (40, b - 14)], fill=(200, 200, 200))
        d.rectangle([28, b - 14, 42, b - 12], fill=(170, 110, 70))
    elif kind == 'factory':
        d.rectangle([8, b - 26, 62, b], fill=(90, 86, 92), outline=pix.OUT)
        for j in range(3): d.polygon([(8 + j * 18, b - 26), (8 + j * 18, b - 36), (26 + j * 18, b - 26)], fill=(110, 104, 110), outline=pix.OUT)
        d.rectangle([48, b - 64, 56, b - 26], fill=(110, 90, 90), outline=pix.OUT)
        for j in range(4): d.rectangle([14 + j * 12, b - 16, 20 + j * 12, b - 10], fill=(200, 160, 80))
    elif kind == 'deadtree':
        bare_tree(d, 35, b, 1.1, (90, 80, 76))
    elif kind == 'trash':
        for j, (x, y, c) in enumerate([(14, 8, (120, 110, 90)), (26, 12, (90, 100, 110)), (38, 9, (130, 90, 80)), (48, 6, (100, 96, 100))]):
            d.ellipse([x - 7, b - y - 6, x + 7, b], fill=c, outline=pix.OUT)
        d.rectangle([26, b - 20, 30, b - 12], fill=(160, 170, 150))
    elif kind == 'fence':
        for x in range(8, 64, 8): d.line([(x, b), (x, b - 18)], fill=(110, 100, 100), width=2)
        for y in (b - 14, b - 7):
            for x in range(8, 62, 4): d.point((x, y + (x // 4) % 2), fill=(150, 140, 140))
    return im


PLANET = [(-0.55, 'flowers'), (-0.15, 'tree'), (0.35, 'house'), (0.75, 'swing'), (1.05, 'flowers'), (1.55, 'deadtree'), (1.9, 'factory'),
          (2.3, 'trash'), (2.7, 'fence'), (3.05, 'factory'), (3.4, 'deadtree')]


def s_world(img, d, lt, dur, T, A):
    th = lt * 0.42
    ugly = ease(span(th, 1.05, 1.85))
    fair = ((0, (110, 170, 240)), (0.6, (190, 214, 250)), (1, (255, 220, 230)))
    smog = ((0, (56, 52, 58)), (0.6, (110, 100, 92)), (1, (150, 130, 110)))
    sky(img, mix_stops(fair, smog, ugly), 0, H)
    if ugly < 1:                                          # 彩虹和太阳
        for j, c in enumerate([(240, 90, 90), (250, 170, 80), (250, 230, 100), (110, 200, 120), (100, 150, 240), (160, 110, 220)]):
            r = 200 - j * 4
            d.arc([240 - r, 230 - r, 240 + r, 230 + r], 200, 340, fill=lerpc(c, mix_stops(fair, smog, ugly)[1][1], ugly), width=4)
        glow(img, 80, 50, 40, (255, 240, 180), 0.5 * (1 - ugly)); d.ellipse([68, 38, 92, 62], fill=lerpc((255, 246, 200), (150, 140, 120), ugly))
    for j in range(5):
        r = rng(j + 30)
        x = (r.uniform(0, W) + T * 6) % (W + 80) - 40
        cloud(d, x, r.uniform(20, 90), r.uniform(1, 1.8), lerpc((255, 255, 255), (90, 84, 86), ugly), lerpc((220, 230, 246), (70, 64, 70), ugly))
    # 星球
    cx, cy, R = 240, 384, 220
    segs = 240
    for j in range(segs):
        a0 = 2 * math.pi * j / segs; a1 = 2 * math.pi * (j + 1) / segs
        wa = (a0 + math.pi / 2 + th) % (2 * math.pi)        # 世界坐标里的角度（0 在最上面）
        u = ease(span(abs(((wa + math.pi) % (2 * math.pi)) - math.pi), 1.0, 1.7))
        col = lerpc((110, 190, 100), (120, 104, 90), u)
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=col)
    d.ellipse([cx - R + 8, cy - R + 8, cx + R - 8, cy + R - 8], fill=None, outline=(255, 255, 255, 40))
    for wa, kind in PLANET:
        a = wa - th
        if abs(a) > 1.3: continue
        im = planet_prop(kind).rotate(-math.degrees(a), resample=Image.NEAREST, expand=True)
        px, py = cx + (R + 34) * math.sin(a), cy - (R + 34) * math.cos(a)
        img.paste(im, (int(px - im.width / 2), int(py - im.height / 2)), im)
    if ugly > 0:                                          # 烟囱冒烟
        for j in range(16):
            r = rng(j + 400)
            u = ((T * 0.3 + r.random()) % 1)
            x = 240 + 260 * math.sin(1.9 - th) + u * 40; y = cy - (R + 60) * math.cos(1.9 - th) - u * 80
            rr = 4 + u * 10
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=lerpc((90, 86, 90), (140, 130, 120), u))
    person(img, 'boy', 240, cy - R + 1, 'young', 'side', 'walk', wph(T, 5), 'smile' if ugly < 0.5 else 'sad', s=2)
    if ugly < 0.5: pix.petals(d, T, 20, seed=8)
    else:
        for j in range(60):
            r = rng(j + 77)
            x = (r.uniform(0, W) + T * 30) % W; y = (r.uniform(0, H) + T * 10) % H
            d.point((x, y), fill=(120, 110, 100))
    vig(img, 0.3, (20, 16, 30))


# ================================================================ 深夜的站台
def s_station(img, d, lt, dur, T, A):
    sky(img, ((0, (10, 12, 30)), (1, (36, 34, 70))), 0, 200)
    stars(d, T, 120, 0.8, 80)
    city(img, d, 150, 5, T * 2, (30, 30, 60), (200, 180, 120), 30, 80, 0.3, T)
    # 后面的铁轨和进站的列车
    d.rectangle([0, 150, W, 186], fill=(30, 30, 46))
    d.line([(0, 176), (W, 176)], fill=(110, 110, 130)); d.line([(0, 182), (W, 182)], fill=(110, 110, 130))
    tx = lerp(W + 40, -380, eout(clamp((lt - 0.2) / 2.2)))
    for car in range(3):
        x0 = tx + car * 300
        if x0 > W or x0 + 290 < 0: continue
        d.rounded_rectangle([x0, 104, x0 + 290, 178], 8, fill=(206, 214, 224), outline=pix.OUT)
        d.rectangle([x0, 160, x0 + 290, 166], fill=(196, 60, 70))
        for wx in range(int(x0) + 14, int(x0) + 280, 30):
            d.rectangle([wx, 116, wx + 20, 140], fill=(255, 226, 160))
            if (wx // 30) % 3 == 0:
                d.ellipse([wx + 6, 122, wx + 12, 128], fill=(60, 50, 60)); d.rectangle([wx + 4, 129, wx + 14, 140], fill=(60, 50, 60))
        glow(img, x0 + 145, 128, 150, (255, 220, 150), 0.12, 30)
    # 站台
    d.rectangle([0, 186, W, H], fill=(70, 66, 84))
    d.rectangle([0, 186, W, 190], fill=(230, 200, 80))
    for x in range(0, W, 24): d.line([(x, 190), (x - 20, H)], fill=(62, 58, 76))
    lx = 240
    d.rectangle([lx - 1, 120, lx + 1, 230], fill=(50, 50, 66))
    d.rectangle([lx - 12, 116, lx + 12, 120], fill=(50, 50, 66))
    tfill(img, 'polygon', [(lx - 10, 121), (lx + 10, 121), (lx + 60, 240), (lx - 60, 240)], (255, 230, 170), 0.16)
    glow(img, lx, 122, 18, (255, 230, 170), 0.6)
    d.ellipse([lx - 9, 132, lx + 9, 150], fill=(250, 250, 240), outline=pix.OUT)      # 钟
    a = T * 2.0
    d.line([(lx, 141), (lx + 6 * math.sin(a), 141 - 6 * math.cos(a))], fill=pix.OUT)
    d.line([(lx, 141), (lx + 4 * math.sin(a / 12), 141 - 4 * math.cos(a / 12))], fill=pix.OUT)
    for j in range(5):                                      # 飞蛾
        mx, my = lx + 12 * math.sin(T * 5 + j * 1.3), 124 + 6 * math.cos(T * 4 + j)
        d.point((mx, my), fill=(255, 250, 220))
    # 走过的路人
    for j in range(3):
        r = rng(j + 12)
        x = (r.uniform(0, W) + T * r.choice([-30, 30])) % (W + 60) - 30
        person_s(img, r.choice(['boy', 'girl']), x, 200, 1.5, r.choice(['old', 'young']), 'side', 'walk', wph(T + j, 6), 'neutral',
                 flip=r.random() < 0.5, tint=(44, 42, 60))
    # 长椅，两个人各坐一头，背对着
    d.rectangle([166, 214, 314, 218], fill=(150, 100, 70)); d.rectangle([166, 204, 314, 207], fill=(150, 100, 70))
    for x in (172, 306): d.rectangle([x, 218, x + 3, 236], fill=(60, 56, 70))
    person(img, 'boy', 190, 236, 'old', 'side', 'sit', 0, 'down', s=2, flip=True)
    person(img, 'girl', 290, 236, 'old', 'side', 'sit', 0, 'down', s=2)
    vig(img, 0.45, (8, 8, 20))


# ================================================================ 沙漏
def s_hourglass(img, d, lt, dur, T, A):
    sky(img, ((0, (8, 8, 24)), (1, (30, 22, 56))), 0, H)
    stars(d, T, H, 0.8, 140)
    cx, top, bot = 240, 22, 238
    mid = (top + bot) / 2
    hw = 70
    jit = round(thump(T, 0.15) * 1)

    def bulb_x(y):
        u = abs(y - mid) / (mid - top)
        return 4 + (hw - 4) * math.sin(min(1, u) * math.pi / 2) ** 0.7

    lvl = lerp(0.82, 0.12, ease(clamp(lt / dur)))            # 上面沙子的高度（占上半个瓶子的比例）
    sand_top = mid - (mid - top - 6) * lvl
    glass = (150, 190, 230)
    for y in range(top + 6, bot - 5):
        bx = bulb_x(y)
        d.line([(cx - bx, y), (cx + bx, y)], fill=(26, 30, 58))
    # 上面的沙
    for y in range(int(sand_top), int(mid)):
        bx = bulb_x(y)
        d.line([(cx - bx + 1, y), (cx + bx - 1, y)], fill=(238, 196, 110) if (y % 3) else (226, 180, 96))
    d.polygon([(cx - bulb_x(sand_top) + 2, sand_top), (cx, sand_top + 6), (cx + bulb_x(sand_top) - 2, sand_top)], fill=(26, 30, 58))
    # 落下去的沙
    for j in range(30):
        y = mid + ((T * 120 + j * 9) % (bot - 8 - mid))
        d.point((cx + (j % 3) - 1, y), fill=(250, 214, 130))
    pile = lerp(0.1, 0.7, ease(clamp(lt / dur)))
    ph = (bot - 8 - mid) * pile
    for y in range(int(bot - 8 - ph), bot - 7):
        bx = bulb_x(y)
        u = (y - (bot - 8 - ph)) / max(1, ph)
        w = bx * min(1, u * 2.5)
        d.line([(cx - w, y), (cx + w, y)], fill=(238, 196, 110) if (y % 3) else (226, 180, 96))
    # 沙面上的长椅和两个人，跟着沙一起往下沉，最后散成沙粒
    sink = clamp((lt - dur * 0.45) / (dur * 0.5))
    by = sand_top + 2 + 10 * sink
    small = Image.new('RGBA', (120, 60)); sd = ImageDraw.Draw(small)
    sd.rectangle([22, 44, 98, 46], fill=(150, 100, 70)); sd.rectangle([22, 38, 98, 40], fill=(150, 100, 70))
    sd.rectangle([26, 46, 28, 54], fill=(80, 70, 70)); sd.rectangle([92, 46, 94, 54], fill=(80, 70, 70))
    pix.person(small, 'boy', 46, 54, 'old', 'front', 'sit', 0, 'neutral')
    pix.person(small, 'girl', 74, 54, 'old', 'front', 'sit', 0, 'neutral')
    a = np.array(small)
    if sink > 0:
        cut = int(60 - sink * 60)
        a[cut:, :, 3] = 0
        m = pix.bayer(60, 120) < sink * 0.8
        a[m, 3] = 0
    small = Image.fromarray(a)
    clip = Image.new('L', (W, H), 0); ImageDraw.Draw(clip).polygon([(cx - bulb_x(y), y) for y in range(top + 6, int(mid))] +
                                                                     [(cx + bulb_x(y), y) for y in range(int(mid), top + 5, -1)], fill=255)
    layer = Image.new('RGBA', (W, H)); layer.paste(small, (int(cx - 60), int(by - 54)), small)
    img.paste(layer, (0, 0), Image.fromarray(np.minimum(np.array(clip), np.array(layer)[..., 3])))
    if sink > 0:
        for j in range(int(30 * sink)):
            r = rng(j + int(T * 20))
            d.point((cx + r.uniform(-30, 30), by - r.uniform(0, 30) * (1 - sink)), fill=(250, 220, 150))
    # 玻璃和木框
    for side in (-1, 1):
        pts = [(cx + side * bulb_x(y), y) for y in range(top + 6, bot - 5)]
        d.line(pts, fill=glass, width=2)
        d.line([(x - side * 3, y) for x, y in pts[10:60]], fill=(220, 240, 255))
    for y0 in (top, bot - 6):
        d.rounded_rectangle([cx - hw - 16, y0 + jit, cx + hw + 16, y0 + 8 + jit], 3, fill=(130, 84, 56), outline=pix.OUT)
    for x in (cx - hw - 10, cx + hw + 6):
        d.rectangle([x, top + 8, x + 4, bot - 6], fill=(110, 70, 46), outline=pix.OUT)
    glow(img, cx, mid, 60, (255, 210, 140), 0.18)
    vig(img, 0.5, (6, 6, 18))
