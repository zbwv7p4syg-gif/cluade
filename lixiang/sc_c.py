"""理想三旬 · 第二段主歌。签名都是 (img, d, lt, dur, T, A)。

夜里的大排档，他醉倒在一桌空酒瓶中间；人潮里一个个灰色的路人从他身边走过；篝火边几个朋友笑成一团，一拍之后各自散去；
地下车站里他上下奔跑，每一站的车都刚好开走；长路上的路牌一块块往后退，他从小孩长成了大人；
醒过来，眼前是一片干裂的土地；开满花的树下她不见了，花落光了也没有结果；诗被墨水和雨弄脏，信封上的心形火漆裂开；
最后山坡上起了大风，他松开手，信纸被吹成一群白鸟飞走。
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


# ================================================================ 大排档
def bottle(d, x, y, col=(70, 150, 90), tip=False):
    if tip:
        d.polygon([(x - 8, y - 2), (x + 8, y - 4), (x + 8, y + 2), (x - 8, y + 4)], fill=col)
        d.rectangle([x + 8, y - 2, x + 12, y + 1], fill=col); return
    d.rectangle([x - 3, y - 14, x + 3, y], fill=col)
    d.rectangle([x - 1, y - 20, x + 1, y - 14], fill=col)
    d.point((x - 2, y - 12), fill=lerpc(col, (255, 255, 255), 0.5))
    d.rectangle([x - 3, y - 9, x + 3, y - 5], fill=(240, 230, 200))


def s_drunk(img, d, lt, dur, T, A):
    sky(img, ((0, (20, 12, 30)), (1, (70, 30, 50))), 0, H, 5)
    city(img, d, 150, 61, 0, (40, 24, 46), (255, 150, 110), 40, 120, frac=0.25, T=T)
    # 霓虹招牌（只有形状，没有字）
    for j, (x, y, c) in enumerate([(60, 50, (255, 80, 130)), (380, 70, (90, 220, 255)), (250, 40, (255, 200, 80))]):
        on = (int(T * 3 + j) % 7) != 0
        if on:
            glow(img, x + 20, y + 8, 40, c, 0.35)
            d.rounded_rectangle([x, y, x + 40, y + 16], 4, outline=c)
            d.line([(x + 8, y + 8), (x + 32, y + 8)], fill=c)
    # 一串灯笼
    d.line(bez((0, 30), (W, 40), (W / 2, 70), 30), fill=(40, 30, 40))
    for j in range(7):
        x = 30 + j * 70
        y = 30 + 40 * (1 - ((x - W / 2) / (W / 2)) ** 2) * 0.8
        red_lantern(img, d, x, y, 1.2, T)
    # 地面和桌子
    d.rectangle([0, 170, W, H], fill=(64, 40, 50))
    d.rectangle([60, 160, 420, 170], fill=(220, 210, 196)); d.rectangle([60, 170, 420, 174], fill=(170, 160, 150))
    for lx in (80, 400): d.rectangle([lx, 174, lx + 3, 230], fill=(130, 126, 120))
    glow(img, 240, 150, 160, (255, 170, 100), 0.25, 60)
    # 桌上的酒瓶、竹签、碗
    for j, x in enumerate([90, 110, 330, 352, 372]): bottle(d, x, 160, [(70, 150, 90), (90, 170, 100)][j % 2])
    bottle(d, 140, 156, tip=True)
    for j in range(6): d.line([(300 + j * 3, 158), (310 + j * 4, 150)], fill=(200, 170, 120))
    d.chord([180, 150, 220, 170], 0, 180, fill=(250, 250, 250))
    # 他趴在桌上，脸红红的；旁边是朋友们模糊的背影
    sway = math.sin(T * 2) * 2
    bust(img, d, 'boy', 250 + sway, 82, 3, 'drunk')
    d.rectangle([200, 150, 300, 160], fill=(96, 118, 84))
    d.rounded_rectangle([196, 146, 214, 160], 4, fill=SKIN); d.rounded_rectangle([286, 146, 304, 160], 4, fill=SKIN)
    for j in range(5):                                        # 头上转圈的小星星
        a = T * 3 + j * 2 * math.pi / 5
        twinkle(d, int(250 + sway + math.cos(a) * 40), int(80 + math.sin(a) * 10), 0.5, (255, 240, 160), 2)
    for j, (x, who, age) in enumerate([(30, 'boy', 'f1'), (450, 'girl', 'f2')]):
        props.person_s(img, who, x, 250, 3, age=age, view='front', expr='laugh', shade=(0.6, 0.5, 0.6))
    vig(img, 0.4, (20, 6, 20))


# ================================================================ 籍籍无名：灰色的人潮
def s_nameless(img, d, lt, dur, T, A):
    sky(img, ((0, (16, 16, 34)), (1, (50, 44, 80))), 0, 190, 5)
    city(img, d, 190, 71, T * 3, (50, 46, 76), (220, 220, 240), 60, 170, frac=0.35, T=T, wmin=24, wmax=50)
    city(img, d, 196, 72, T * 6, (36, 34, 56), (200, 210, 240), 40, 120, frac=0.3, T=T, wmin=24, wmax=44)
    d.rectangle([0, 196, W, H], fill=(70, 68, 88))
    for x in range(0, W, 30): d.line([(x, 196), (x - 60, H)], fill=(80, 78, 98))
    # 人潮：灰色的路人往两个方向走，越走越快；他站在中间
    speed = 1 + 2.5 * ease(lt / dur)
    for j in range(26):
        r = rng(j * 9)
        dirn = 1 if j % 2 else -1
        y = 214 + (j % 5) * 10
        x = (r.uniform(0, W + 80) + dirn * T * 30 * speed * r.uniform(0.8, 1.2)) % (W + 80) - 40
        if abs(x - 240) < 14 and y > 230: continue
        g = 140 + (j % 4) * 20
        props.person_s(img, ['boy', 'girl'][j % 2], x, y, 2 if y > 236 else 1.5, age='young', view='side', pose='walk', ph=wph(T + j, 8),
                       flip=dirn < 0, tint=(g, g, g + 10))
    pix.person(img, 'boy', 240, 248, view='front', s=2, expr='neutral')
    cat(img, 260, 248, 'sit', 2, rim=(130, 124, 150), T=T)
    vig(img, 0.45, (10, 8, 20))


# ================================================================ 篝火边聚了又散
FRIENDS = [('boy', 'f1', 150, -1), ('girl', 'f2', 192, -1), ('boy', 'f3', 300, 1), ('girl', 'young', 342, 1)]


def fire(img, d, x, y, T, k=1.0):
    glow(img, x, y - 10, 90 * k, (255, 160, 80), 0.4 * k)
    for j in range(3):
        d.line([(x - 12 + j * 10, y), (x + 8 - j * 8, y - 4)], fill=(110, 70, 50), width=3)
    for j in range(7):
        h = (10 + 8 * math.sin(T * 9 + j * 1.7)) * k
        fx = x - 9 + j * 3
        d.polygon([(fx - 3, y - 2), (fx + 3, y - 2), (fx, y - 2 - h)], fill=[(255, 120, 60), (255, 200, 80), (255, 240, 170)][j % 3])
    for j in range(10):                                       # 火星
        u = (T * 0.8 + j / 10) % 1
        d.point((x + math.sin(j * 3 + T) * 10 * u, y - 10 - u * 60 * k), fill=lerpc((255, 220, 120), (60, 30, 40), u))


def s_party(img, d, lt, dur, T, A):
    part = beat_after(T - lt + 2.0) - (T - lt)
    k = lt - part
    sky(img, NIGHT, 0, 190, 5)
    stars(d, T, 190, 1, 200)
    # 海边的夜：远处的海和灯塔，近处是沙滩
    d.rectangle([0, 150, W, 190], fill=(24, 30, 66))
    for j in range(8): d.line([(j * 60 + (T * 10) % 60, 160 + j % 3 * 8), (j * 60 + 20 + (T * 10) % 60, 160 + j % 3 * 8)], fill=(60, 70, 120))
    d.rectangle([0, 186, W, H], fill=(84, 66, 74))
    d.line(bez((0, 60), (W, 70), (W / 2, 100), 30), fill=(50, 40, 60))
    for j in range(12):
        x = 20 + j * 40; y = 60 + 30 * (1 - ((x - W / 2) / (W / 2)) ** 2) * 1.0 + 2
        on = (int(T * 4) + j) % 3 != 0
        c = [(255, 200, 90), (255, 140, 160), (140, 220, 255)][j % 3]
        if on: glow(img, x, y, 8, c, 0.5)
        d.rectangle([x - 1, y, x + 1, y + 2], fill=c if on else (90, 80, 100))
    fk = 1.0 if k < 0 else lerp(1.0, 0.55, ease(k / 1.5))
    fire(img, d, 246, 226, T, fk)
    # 朋友们：先笑成一团，一拍之后起身各走各的，挥手告别
    for j, (who, age, x0, dirn) in enumerate(FRIENDS):
        if k < 0:
            jump = -2 if (int(T * 6) + j) % 4 == 0 else 0
            pix.person(img, who, x0, 238 + jump, age, view='front', pose='sit', s=2, expr='laugh')
        else:
            u = clamp((k - j * 0.2) / 2.2)
            if u <= 0:
                pix.person(img, who, x0, 238, age, view='front', s=2, expr='smile', arms='wave', ph=int(T * 6))
                continue
            x = x0 + dirn * (60 + u * 260)
            y = 238 - u * 30 * (j % 2)
            pix.person(img, who, x, y, age, view='side', pose='walk', ph=wph(T, 8), s=2, flip=dirn < 0,
                       arms='wave' if u < 0.3 else 'swing')
    pix.person(img, 'boy', 196, 264, view='back', pose='sit', s=2)
    if k > 0.6: cat(img, 226, 266, 'sit', 2, flip=True, rim=(140, 120, 150), T=T)
    for j in range(4):                                        # 地上的空罐
        d.rectangle([110 + j * 80, 252 + (j % 2) * 4, 114 + j * 80, 258 + (j % 2) * 4], fill=[(200, 60, 60), (80, 160, 220)][j % 2])
    vig(img, 0.35, (10, 6, 20))


# ================================================================ 地下车站：上下奔跑，车总是刚开走
def metro_train(img, d, x, y, T, col=TIN):
    train(img, d, x, y, T, cars=4, lit=1.0, seed=17, roll=x / 5, rust=0.4, night=0.2)


def s_platforms(img, d, lt, dur, T, A):
    img.paste((40, 38, 56), (0, 0, W, H))
    # 两层站台，中间一道楼梯
    for y0 in (118, 232):
        d.rectangle([0, y0, W, y0 + 8], fill=(150, 146, 160)); d.rectangle([0, y0, W, y0 + 2], fill=(236, 200, 90))
        d.rectangle([0, y0 - 90, W, y0 - 84], fill=(60, 58, 78))
        for x in range(0, W, 60): d.rectangle([x, y0 - 70, x + 30, y0 - 66], fill=(230, 240, 255))
        glow(img, W / 2, y0 - 66, 300, (200, 220, 255), 0.12, 20)
    # 站牌：每一站都打着问号
    for j, (x, y) in enumerate([(80, 50), (400, 50), (80, 164), (400, 164)]):
        d.rectangle([x - 26, y, x + 26, y + 16], fill=(40, 110, 170)); d.rectangle([x - 26, y, x + 26, y + 16], outline=(230, 230, 240))
        text(img, ['站台 ?', '站台 ?', '这一站', '下一站'][j], x, y + 8, (255, 255, 255), None, FONT_S, shadow=False)
    # 楼梯
    for s in range(14):
        sx = 200 + s * 6; sy = 232 - s * 8
        d.rectangle([sx, sy, sx + 6, sy + 8], fill=(110, 106, 124))
        d.line([(sx, sy), (sx + 6, sy)], fill=(170, 166, 180))
    # 两层的车轮流进站又开走
    for lvl, y0, ph in ((0, 118, 0.0), (1, 232, 0.5)):
        u = ((lt / 2.4) + ph) % 1
        x = lerp(-60, W + 560, u)
        metro_train(img, d, x, y0 - 2, T)
    # 他：在下层往右跑、上楼梯、在上层往左跑，又折回来
    path = [(0.0, (60, 232)), (0.22, (196, 232)), (0.42, (290, 120)), (0.62, (420, 120)), (0.72, (420, 120)), (0.95, (120, 120)), (1.0, (100, 120))]
    f = lt / dur
    for i in range(len(path) - 1):
        (fa, pa), (fb, pb) = path[i], path[i + 1]
        if fa <= f <= fb:
            u = (f - fa) / max(1e-6, fb - fa)
            x, y = lerp(pa[0], pb[0], u), lerp(pa[1], pb[1], u)
            moving = pb != pa
            flip = pb[0] < pa[0]
            break
    else:
        x, y, moving, flip = 100, 120, False, True
    pix.person(img, 'boy', x, y, view='side', pose='run' if moving else 'stand', ph=wph(T, 12), s=2, flip=flip,
               expr='worried' if not moving else 'neutral')
    if not moving:
        for j in range(3): d.point((x + 4 + j * 3, y - 64), fill=(255, 255, 255))
    vig(img, 0.35, (10, 8, 20))


# ================================================================ 漂泊是成长：一路的路牌
def signpost(img, d, x, base, txt, flip=False, col=(236, 226, 196)):
    d.rectangle([x - 1, base - 46, x + 1, base], fill=(90, 70, 60))
    pts = [(x - 26, base - 46), (x + 22, base - 46), (x + 30, base - 39), (x + 22, base - 32), (x - 26, base - 32)]
    if flip: pts = [(2 * x - px, py) for px, py in pts]
    d.polygon([(px, py + 1) for px, py in pts], fill=OUT)
    d.polygon(pts, fill=col)
    text(img, txt, x + (-2 if flip else 2), base - 39, (110, 70, 50), None, FONT_S, shadow=False)


def s_signs(img, d, lt, dur, T, A):
    sky(img, DAY, 0, 190, 6)
    for j in range(4):
        cloud(d, (j * 140 - T * 8) % (W + 100) - 50, 30 + (j % 2) * 30, 2.2, (255, 255, 255), (220, 230, 245), None)
    off = T * 70
    mountains(d, 170, 40, 0.012, 0.4, (150, 180, 200), off * 0.1)
    mountains(d, 186, 24, 0.02, 1.4, (120, 170, 120), off * 0.3)
    d.rectangle([0, 186, W, H], fill=(140, 190, 100))
    d.rectangle([0, 224, W, 246], fill=(170, 150, 120))
    for x in range(int(-(off % 40)), W, 40): d.rectangle([x, 234, x + 18, 235], fill=(240, 236, 220))
    pix.grass(d, 224, (110, 170, 80), (90, 150, 70), T, step=4)
    # 路牌一块块往后退
    labels = ['小时候', '十八岁', '远方', '南方', '三十岁', '?']
    period = W + 300
    for j in range(5):
        u = j * period / 5 + 200 - off
        x = u % period
        lap = int((u - x) / period)
        if -60 < x < W + 60:
            signpost(img, d, x, 224, labels[(j - lap * 5) % len(labels)], flip=j % 2 == 1)
    # 他一路走，从小孩长成大人
    grow = ease(clamp((lt - 1.2) / 1.6))
    age_kid = 1 - grow
    if age_kid > 0: ghost(img, 'boy', 220, 238, 2, age_kid, age='kid', view='side', pose='walk', ph=wph(T, 8))
    if grow > 0: ghost(img, 'boy', 220, 238, 2, grow, age='young', view='side', pose='walk', ph=wph(T, 8))
    cat(img, 186, 238, 'walk', 2, rim=None, T=T)
    for j in range(4): pix.butterfly(d, int(300 + j * 40 + 10 * math.sin(T * 2 + j)), int(200 + 8 * math.sin(T * 3 + j)), T, (255, 240, 120), j)
    vig(img, 0.2, (40, 60, 40))


# ================================================================ 迷醒：醒过来
def s_wake(img, d, lt, dur, T, A):
    f = lt / dur
    img.paste(lerpc((40, 30, 50), (120, 100, 110), f), (0, 0, W, H))
    tfill(img, 'polygon', [(300, 0), (400, 0), (280, H), (140, H)], (255, 230, 180), 0.12 + 0.12 * f)
    # 窗外天亮了
    d.rectangle([300, 20, 440, 120], fill=lerpc((40, 50, 90), (250, 210, 170), f))
    d.line([(370, 20), (370, 120)], fill=(80, 60, 70)); d.line([(300, 70), (440, 70)], fill=(80, 60, 70))
    d.rectangle([296, 16, 444, 124], outline=(80, 60, 70))
    expr = 'closed' if lt < 0.9 else ('half' if lt < 1.6 else 'neutral')
    bust(img, d, 'boy', 180, 40 + (0 if lt > 0.9 else 3), 5, expr)
    if lt < 1.6:
        for j in range(6):
            a = T * 4 + j * math.pi / 3
            twinkle(d, int(180 + math.cos(a) * 70), int(40 + math.sin(a) * 16), 0.5, (255, 240, 180), 3)
    # 墙上的钟：他醒来的时候，指针已经转了好多圈
    clock(d, 80, 60, 26, lt * 4, lt * 40)
    vig(img, 0.4, (20, 10, 20))


# ================================================================ 贫瘠的未来：干裂的土地
CRACKS = []
_r = rng(77)
for _ in range(40):
    x, y = _r.uniform(0, W), _r.uniform(190, H)
    pts = [(x, y)]
    for _ in range(_r.randint(3, 6)):
        x += _r.uniform(-20, 20); y += _r.uniform(-6, 8)
        pts.append((x, y))
    CRACKS.append(pts)


def s_barren(img, d, lt, dur, T, A):
    sky(img, ((0, (190, 176, 160)), (0.6, (226, 200, 170)), (1, (244, 220, 186))), 0, 186, 6)
    glow(img, 240, 80, 120, (255, 250, 230), 0.6)
    d.ellipse([224, 64, 256, 96], fill=(255, 252, 240))
    mountains(d, 186, 16, 0.02, 2.0, (180, 150, 130))
    d.rectangle([0, 186, W, H], fill=(196, 160, 120))
    for pts in CRACKS: d.line(pts, fill=(140, 104, 80))
    # 热浪：地平线上的一排像素左右抖
    a = np.asarray(img).copy()
    for y in range(176, 196):
        a[y] = np.roll(a[y], int(round(1.5 * math.sin(T * 8 + y))), axis=0)
    img.paste(Image.fromarray(a))
    # 枯树和小芽
    d.line([(100, 200), (100, 150)], fill=(90, 66, 54), width=3)
    for bx, by, ex, ey in [(100, 170, 80, 150), (100, 162, 124, 140), (100, 156, 92, 132), (124, 140, 134, 132)]:
        d.line([(bx, by), (ex, ey)], fill=(90, 66, 54), width=2)
    sx, sy = 320, 230
    d.line([(sx, sy), (sx, sy - 7)], fill=(120, 170, 80))
    d.ellipse([sx - 5, sy - 10, sx, sy - 6], fill=(140, 200, 90)); d.ellipse([sx, sy - 11, sx + 5, sy - 7], fill=(120, 180, 80))
    # 滚过去的风滚草
    tx = lerp(-30, W + 30, lt / dur); ty = 214 - abs(math.sin(lt * 5)) * 14
    for j in range(8):
        a_ = lt * 6 + j * 0.8
        d.arc([tx - 10, ty - 10, tx + 10, ty + 10], math.degrees(a_), math.degrees(a_) + 120, fill=(150, 116, 80))
    # 远处很小的他和长长的影子
    pix.person(img, 'boy', 380, 200, view='back', s=1)
    d.polygon([(376, 200), (384, 200), (440, 214), (420, 216)], fill=(170, 136, 104))
    for j in range(20):                                       # 风里的沙
        r = rng(j * 3)
        x = (r.uniform(0, W) + T * 120) % W; y = r.uniform(150, 260)
        d.line([(x, y), (x + 4, y)], fill=(230, 210, 180))
    vig(img, 0.3, (120, 80, 60))


# ================================================================ 花落光的树，她不见了
@lru_cache(None)
def blossom_spots():
    r = rng(5)
    out = []
    for _ in range(900):
        a = r.uniform(0, 2 * math.pi); rad = r.uniform(0, 1) ** 0.5
        out.append((240 + math.cos(a) * rad * 156, 86 + math.sin(a) * rad * 66, r.random(), r.randrange(3)))
    return out


def s_blossom(img, d, lt, dur, T, A):
    f = lt / dur
    sky(img, mix_stops(((0, (150, 190, 236)), (1, (236, 220, 236))), ((0, (120, 110, 150)), (1, (220, 170, 150))), f), 0, 200, 6)
    d.rectangle([0, 200, W, H], fill=lerpc((140, 190, 110), (170, 150, 100), f))
    pix.grass(d, 200, lerpc((110, 170, 80), (150, 130, 80), f), (90, 150, 70), T, step=3)
    # 树干和枝
    tr = (96, 70, 64)
    d.polygon([(226, 200), (254, 200), (248, 140), (232, 140)], fill=tr)
    for bx, by, ex, ey in [(240, 150, 150, 90), (240, 146, 330, 80), (240, 140, 240, 50), (190, 120, 120, 110), (290, 110, 370, 110),
                           (240, 100, 200, 60), (260, 96, 300, 50)]:
        d.line([(bx, by), (ex, ey)], fill=tr, width=4)
    # 花：一朵朵往下掉，最后一朵不剩，也没有果子
    cols = [(255, 190, 210), (255, 220, 230), (250, 160, 190)]
    for x, y, k, c in blossom_spots():
        if k < f * 1.4 - 0.35:
            u = (f * 1.4 - 0.35 - k) * 4
            if u > 1: continue
            x += u * 60 + math.sin(u * 8 + k * 9) * 8; y += u * 140
        d.rectangle([x, y, x + 3, y + 3], fill=cols[c])
    pix.petals(d, T, int(30 + 50 * f), seed=6, y1=H)
    # 树下两个人：她慢慢变淡，最后只剩他
    pix.person(img, 'boy', 214, 214, view='side', pose='sit', s=2)
    ghost(img, 'girl', 268, 214, 2, 1 - ease(clamp((f - 0.25) / 0.5)), view='side', pose='sit', flip=True)
    vig(img, 0.3, (60, 30, 50))


# ================================================================ 被墨点和雨弄脏的本子
def page_lines(d, x0, y0, seed, n=7, col=(70, 60, 80)):
    r = rng(seed)
    for i in range(n):
        y = y0 + i * 12
        x = x0
        while x < x0 + r.uniform(120, 150):
            ln = r.uniform(6, 18)
            pts = [(x + u, y + math.sin((x + u) * 0.6 + seed) * 1.2) for u in range(0, int(ln), 2)]
            if len(pts) > 1: d.line(pts, fill=col)
            x += ln + 4


def s_poems(img, d, lt, dur, T, A):
    img.paste((70, 52, 46), (0, 0, W, H))
    glow(img, 240, 120, 260, (255, 210, 150), 0.3)
    # 摊开的本子
    d.polygon([(60, 40), (238, 50), (238, 250), (60, 240)], fill=(250, 244, 226))
    d.polygon([(242, 50), (420, 40), (420, 240), (242, 250)], fill=(244, 238, 220))
    d.line([(240, 50), (240, 250)], fill=(190, 176, 150))
    page_lines(d, 76, 70, int(T * 0) + 3)
    page_lines(d, 258, 70, 5)
    # 墨点和雨点踩着拍子落下来，晕开一大片
    bs = [b - (T - lt) for b in beats_in(T - lt - 0.1, T - lt + dur)]
    spots = [(150, 120), (320, 170), (200, 200), (360, 100)]
    for j, b in enumerate(bs[:4]):
        k = lt - b
        if k < 0: continue
        x, y = spots[j]
        r = 6 + 22 * eout(k / 0.8)
        col = (40, 40, 80) if j % 2 == 0 else (120, 140, 170)
        props.puff(img, x, y, r, col, 0.8)
        for m in range(6):
            a = m * 1.05 + j
            props.puff(img, x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.7, r * 0.35, col, 0.7)
        if j % 2 == 1:
            d.line([(x, y), (x + 4, y + 40 * eout(k))], fill=col, width=3)
    # 翻页：最后半秒，右页翻起来
    flip = clamp((lt - (dur - 0.7)) / 0.6)
    if flip > 0:
        xe = lerp(420, 60, ease(flip))
        d.polygon([(242, 50), (xe, 40 - 20 * math.sin(math.pi * flip)), (xe, 240 - 10 * math.sin(math.pi * flip)), (242, 250)],
                  fill=(236, 230, 210))
    for j in range(16):                                       # 窗外的雨落在本子边上
        r = rng(j)
        y = (r.uniform(0, H) + T * 200) % H
        d.line([(r.uniform(0, 50), y), (r.uniform(0, 50) - 2, y + 6)], fill=(120, 130, 160))
    vig(img, 0.4, (20, 10, 10))


# ================================================================ 最疼痛的告白：裂开的火漆
def s_letter(img, d, lt, dur, T, A):
    img.paste((54, 40, 46), (0, 0, W, H))
    glow(img, 240, 130, 220, (255, 200, 150), 0.25)
    # 信封
    x0, y0, x1, y1 = 110, 60, 370, 220
    d.rectangle([x0 + 3, y0 + 4, x1 + 3, y1 + 4], fill=(30, 20, 26))
    d.rectangle([x0, y0, x1, y1], fill=(246, 236, 214))
    d.polygon([(x0, y0), (x1, y0), (240, 150)], fill=(232, 220, 196))
    d.line([(x0, y0), (240, 150), (x1, y0)], fill=(200, 186, 160))
    d.line([(x0, y1), (205, 135)], fill=(220, 208, 184)); d.line([(x1, y1), (275, 135)], fill=(220, 208, 184))
    # 心形火漆：在拍点上裂开
    crack = beat_after(T - lt + 0.8) - (T - lt)
    k = lt - crack
    cx, cy = 240, 150
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(170, 30, 44))
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(200, 46, 56))
    sep = 0 if k < 0 else eout(k / 0.5) * 5
    for side in (-1, 1):
        pts = heart_poly(cx + side * sep, cy + 2, 0.9)
        pts = [(x, y) for x, y in pts if (x - cx) * side >= -1] + [(cx + side * sep, cy + 14)]
        d.polygon(pts, fill=(150, 20, 36))
    if k >= 0:
        zig = [(cx, cy - 10), (cx + 3, cy - 5), (cx - 2, cy), (cx + 3, cy + 5), (cx - 1, cy + 10), (cx, cy + 16)]
        d.line([(x + 1, y) for x, y in zig], fill=(60, 10, 20), width=2)
        for j in range(8):
            a = j * 0.8
            px = cx + math.cos(a) * (10 + k * 60); py = cy + math.sin(a) * (10 + k * 40) + k * k * 60
            if k < 1: d.rectangle([px, py, px + 1, py + 1], fill=(200, 46, 56))
        props.shake(img, k, 3, 0.25)
    # 一滴眼泪落在信封上
    tk = (lt - 0.3) / 1.2
    if 0 < tk < 1:
        y = lerp(-10, 190, ein(tk))
        d.ellipse([300, y - 5, 306, y + 3], fill=(150, 196, 246))
    elif tk >= 1:
        props.puff(img, 303, 192, 8, (214, 206, 190), 0.8)
    vig(img, 0.45, (16, 8, 14))


# ================================================================ 风声：信纸变成白鸟飞走
def swoosh(d, x, y, ln, col):
    d.line([(x, y), (x + ln, y)], fill=col)
    d.point([(x + ln + 1, y - 1), (x + ln + 2, y - 2), (x + ln + 2, y - 3), (x + ln + 1, y - 4), (x + ln, y - 4)], fill=col)


def s_wind(img, d, lt, dur, T, A):
    sky(img, GOLDEN, 0, 200, 6)
    glow(img, 100, 150, 160, (255, 230, 170), 0.5, 80)
    for j in range(5):
        cloud(d, (j * 120 + T * 40) % (W + 140) - 70, 20 + (j % 3) * 22, 2.0, (255, 220, 200), (240, 176, 166), (255, 244, 236))
    d.polygon([(0, 210), (180, 180), (360, 196), (W, 186), (W, H), (0, H)], fill=(150, 150, 70))
    # 被风吹得一边倒的长草
    for i, x in enumerate(range(0, W, 3)):
        base = 210 - x / 180 * 30 if x < 180 else 180 + (x - 180) / 180 * 16 if x < 360 else 196 - (x - 360) / 120 * 10
        h = 8 + (i * 7) % 8
        sw = 5 + 3 * math.sin(T * 6 + x * 0.05)
        d.line([(x, base + 2), (x + sw, base - h)], fill=[(200, 190, 90), (170, 160, 70), (230, 210, 110)][i % 3])
    for j in range(10):
        r = rng(j * 3)
        x = (r.uniform(0, W) + T * 260 * r.uniform(0.8, 1.3)) % (W + 80) - 40
        swoosh(d, x, r.uniform(30, 170), r.uniform(20, 50), (255, 246, 230))
    # 他站在坡顶，围巾往右飘；手里的信纸一松开就飞走，变成白鸟
    x, y = 180, 182
    pix.person(img, 'boy', x, y, view='side', s=3, arms='reach' if lt < 1.4 else 'down', flip=False)
    fl = math.sin(T * 12) * 2
    d.polygon([(x - 6, y - 46), (x + 2, y - 46), (x + 30, y - 52 + fl), (x + 34, y - 46 + fl)], fill=MUSTARD)
    rel = 1.2
    for j in range(7):
        k = lt - rel - j * 0.12
        if k < 0:
            if j == 0: d.rectangle([x + 22, y - 36, x + 30, y - 26], fill=(250, 246, 236))
            continue
        px = x + 26 + k * 120 + j * 10; py = y - 30 - k * 50 - math.sin(k * 3 + j) * 16 - j * 6
        if k < 0.6:
            rot = math.sin(k * 10 + j) * 4
            d.polygon([(px, py), (px + 8, py + rot), (px + 8 - rot, py + 10), (px - rot, py + 10)], fill=(250, 246, 236))
        else:
            ff = int(T * 8 + j) % 2
            wing = 4 if ff else -3
            d.line([(px - 6, py + wing), (px, py), (px + 6, py + wing)], fill=(255, 255, 255), width=2)
    cat(img, 150, 184, 'sit', 2, T=T)
    vig(img, 0.25, (100, 50, 40))
