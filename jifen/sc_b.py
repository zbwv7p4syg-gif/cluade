"""几分之几 · 第一段副歌和第二段主歌。

她推门走进他灰色的房间，走到哪里哪里就有了颜色；她递给他一块会发光的拼图，心里八块缺的地方第一次填进去；
闭上眼睛，黑暗里也是她；晴朗的南方，单车沿着海边骑；他摔了一跤，她坐在长椅上等过一个又一个季节；
屋顶上的银河；雨里她把伞全斜给了他，水洼里他看着自己，她的脸出现在旁边；最后是几格漫画，都是她为他做的事。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
import motifs
import fx
from pix import (W, H, FONT, FONT_S, OUT, SKIN, SKIN_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, rng)
from props import dpaste, person_s, mix_stops, shots, CREAM, GOLD, GOLD_L, PINK, PINK_L
from motifs import GOLD_SKY, DUSK_SKY, DAWN_SKY, NIGHT_SKY, NOON_SKY, PLAIN_GOLD, PIECE

YY, XX = np.mgrid[0:H, 0:W]


def chair(d, x, base, flip=False):
    sg = -1 if flip else 1
    d.rectangle([x - 8, base - 16, x + 8, base - 14], fill=(130, 86, 56))
    d.rectangle([x - 8 * sg - 1, base - 34, x - 8 * sg + 1, base], fill=(120, 80, 52))
    d.rectangle([x + 7 * sg - 1, base - 14, x + 7 * sg + 1, base], fill=(120, 80, 52))


# ---------------------------------------------------------------- 7 那一天你走进了我的生命
def s_enter(img, d, lt, dur, T, amp):
    door = ease(span(lt, 0.9, 1.8))
    bloom = ease(span(lt, 5.4, 7.0))
    fx.LIGHT = ((1, -0.5), (255, 236, 190))
    dx0, dy0, dx1, dy1 = motifs.room(img, d, T, door=door, plant_bloom=bloom)
    base = 196
    fx.contact(img, 290, base, 18, 0.35)
    # 她：先站在门口的光里，然后往右走进来
    w0, w1 = 2.0, 5.0
    gx = lerp(78, 206, span(lt, w0, w1))
    steps = []
    if lt > w0:
        for k in range(int((min(lt, w1) - w0) / 0.42) + 1):
            tk = w0 + k * 0.42
            steps.append((lerp(78, 206, span(tk, w0, w1)), tk))
    for sx, tk in steps:                                      # 她踩过的地方开出小花
        f = span(lt, tk + 0.1, tk + 0.6)
        for j in range(2):
            pix.flower(d, sx - 4 + j * 9, base + 6 + j * 4, PIECE[(int(sx) + j) % 8], 0 if j else 2, h=round(3 * f), open_=f)
    chair(d, 292, base)
    # 他：坐在书桌前发呆；她进门后转过身，站起来
    if lt < 3.4: person_s(img, 'boy', 290, base - 0, 2, view='side', pose='sit', expr='down')
    elif lt < 4.4: person_s(img, 'boy', 290, base, 2, view='side', pose='sit', expr='surprised', flip=True)
    else: person_s(img, 'boy', 290, base, 2, view='side', expr='surprised' if lt < 5.3 else 'happy', flip=True)
    a = span(lt, 1.2, 1.8)
    if lt < w0: props.ghost(img, 'girl', 78, base, 2, a, view='front', expr='smile')
    elif lt < w1: person_s(img, 'girl', gx, base, 2, view='side', pose='walk', ph=pix.wph(lt, 7), expr='smile')
    else: person_s(img, 'girl', gx, base, 2, view='side', expr='happy')
    # 灰色和彩色：门口的光、她身边、她的脚印，最后整间屋子
    pts = [((dx0 + dx1) / 2, (dy0 + dy1) / 2, 60 * door)]
    if lt > 1.2: pts.append((gx, base - 40, lerp(30, 90, span(lt, 1.2, 5.5))))
    for sx, tk in steps: pts.append((sx, base, 26 + 50 * eout(span(lt, tk, tk + 1.5))))
    pts.append((gx, base - 40, 560 * ease(span(lt, 5.4, 6.8))))
    color = np.asarray(img)
    m = motifs.reveal_mask(pts)
    g = motifs.gray(color, 1) * 0.82
    img.paste(Image.fromarray(np.where(m[..., None], color, g).astype(np.uint8)))
    d = ImageDraw.Draw(img)
    if lt > 5.5:
        props.leaves(d, T, 18, wind=10, speed=14, seed=4, cols=((255, 180, 200), (255, 220, 120), (200, 230, 255)))
        for i in range(3):
            k = span(lt, 5.6 + i * 0.4, 6.6 + i * 0.4)
            if 0 < k < 1: pix.put(img, 'heart', 250 + i * 14, 120 - 30 * k, 1 + (i == 1), alpha=1 - k * 0.6)


# ---------------------------------------------------------------- 8 谢谢你 成为了我的几分之几
def _give(img, d, t, T):
    fx.LIGHT = ((1, -0.3), (255, 222, 150))
    motifs.sun_plain(img, d, T, sky=GOLD_SKY, sx=360, sy=156, sr=50, hz=180, dip=3, road=False, grass_on=True, birds=True)
    d.polygon([(0, 226), (140, 222), (340, 224), (W, 230), (W, H), (0, H)], fill=(196, 140, 70))
    fx.tex(img, (0, 222, W, H), 7, seed=31, scale=2)
    for x in range(0, W, 3):
        d.line([(x, 228 + (x * 7) % 5), (x + 1, 223 + (x * 7) % 5)], fill=(226, 176, 96))
    tfill(img, 'polygon', [(180, 228), (300, 228), (290, 236), (170, 236)], (120, 70, 40), 0.3)
    expr_b = 'surprised' if t < 2.6 else 'shy'
    person_s(img, 'boy', 206, 228, 2, view='side', expr=expr_b)
    person_s(img, 'girl', 276, 228, 2, view='side', arms='reach' if t < 2.4 else 'down', expr='happy', flip=True)
    f = span(t, 1.2, 2.6)
    px, py = lerp(254, 210, ease(f)), lerp(196, 196, f) - 26 * math.sin(math.pi * f)
    if t < 2.9:
        motifs.fly_piece(img, 0, 1.6, px, py + math.sin(T * 4) * 1.5, 1.0, glow_a=0.8, glowing=True)
    k = span(t, 2.6, 3.4)
    if 0 < k < 1:
        glow(img, 210, 200, 30 * eout(k), (255, 230, 150), 0.8 * (1 - k))
        pix.twinkle(d, 210, 198, k, (255, 255, 255), 6)
    if t > 2.8: glow(img, 210, 200, 8, (255, 220, 140), 0.4 + 0.2 * props.thump(T))
    fx.motes(img, d, T, 24, (100, 60, W, 220), (255, 236, 180), seed=8)
    fx.fg(img, T, 'grass', (90, 60, 40), (255, 200, 120), (0, 1), 3, seed=12, h=0.9)


def _pie_fill(img, d, t, T):
    pix.sky(img, ((0, (30, 24, 60)), (1, (70, 46, 90))))
    props.bokeh(img, T, 16, ((255, 200, 120), (255, 150, 170), (150, 200, 255)), seed=8, a=0.22)
    pix.stars(d, T, H, 0.5, 80, base=(40, 30, 70))
    fx.godrays(img, 190, 124, T, 14, (255, 210, 190), 0.05, spread=2 * math.pi, length=360, pulse=0.03 * props.thump(T))
    fx.motes(img, d, T, 40, (0, 0, W, H), (255, 220, 200), seed=9, drift=(2, -5))
    t_start = T - t
    lands = [b - t_start for b in props.beats_in(t_start + 0.5, t_start + 5.4)][::2][:3]
    while len(lands) < 3: lands.append(lands[-1] + 1.6 if lands else 0.6)
    cx, cy, s = 190, 124, 3.4
    cents = motifs.pie_centers(cx, cy, s)
    fill = [0] * 8; pop = [0] * 8
    n = 0
    for k, tl in enumerate(lands):
        if t >= tl:
            fill[k] = clamp((t - tl) / 0.12); pop[k] = clamp(1 - (t - tl) / 0.4); n += 1
    glow(img, cx, cy, 90, (255, 180, 170), 0.18 + 0.1 * props.thump(T))
    motifs.heart_pie(img, cx, cy, s, fill, pop=pop)
    for k, tl in enumerate(lands):                             # 飞进来的那一块
        f = (t - (tl - 0.9)) / 0.9
        if 0 <= f < 1:
            tx, ty = cents[k]
            sx, sy = W + 30, 40 + k * 50
            e = eout(f)
            x = lerp(sx, tx, e); y = lerp(sy, ty, e) - 40 * math.sin(math.pi * e)
            for q in range(4):
                qe = max(0, e - 0.05 * (q + 1))
                d.point((lerp(sx, tx, qe), lerp(sy, ty, qe) - 40 * math.sin(math.pi * qe)), fill=lerpc(PIECE[k], (40, 30, 70), q / 4))
            motifs.fly_piece(img, k, s, x, y, 1.0, glow_a=0.5)
        if 0 < t - tl < 0.5:
            tx, ty = cents[k]
            pix.twinkle(d, int(tx), int(ty), (t - tl) / 0.5, (255, 255, 255), 6)
    bounce = 0
    if n: bounce = 4 * clamp(1 - (t - lands[n - 1]) / 0.3)
    motifs.fraction(img, 380, cy - bounce, n, 8, 3, top=(255, 252, 240), bot=(255, 196, 110), line=(200, 104, 70))


def s_piece(img, d, lt, dur, T, amp):
    shots(img, lt, [(0, _give), (4.2, _pie_fill)], 0.4, T=T)


# ---------------------------------------------------------------- 9 闭上眼睛也能看见你
def lashes(img, d, k):
    """眼皮从上下合上：k=0 全开，1 全闭。边缘有一排睫毛"""
    if k <= 0: return
    h = int(ease(k) * (H / 2 + 6))
    d.rectangle([0, 0, W, h], fill=(10, 6, 18)); d.rectangle([0, H - h, W, H], fill=(10, 6, 18))
    for x in range(-4, W, 9):
        sw = 2 + (x // 9) % 3
        d.line([(x, h), (x + 3, h + 4 + sw)], fill=(10, 6, 18), width=2)
        d.line([(x + 4, H - h), (x + 7, H - h - 3 - sw)], fill=(10, 6, 18), width=2)


def _close_eyes(img, d, t, T):
    pix.sky(img, ((0, (255, 200, 170)), (1, (255, 230, 200))))
    props.bokeh(img, T, 10, ((255, 236, 200), (255, 200, 170)), seed=5, a=0.3)
    fx.godrays(img, 420, 30, T, 7, (255, 246, 220), 0.06, spread=math.pi * 0.7, center=math.pi * 0.8, length=420)
    motifs.lit_bust(img, 'boy', 240, 44, 4, 'smile' if t < 0.9 else 'closed', (1, -0.8), (255, 236, 200))
    fx.motes(img, d, T, 20, (0, 0, W, H), (255, 246, 220), seed=4)
    lashes(img, d, span(t, 1.2, 2.3))


def _see_you(img, d, t, T):
    pix.sky(img, ((0, (12, 8, 28)), (1, (26, 14, 44))))
    for i in range(5):                                         # 闭着眼看到的光斑
        r = rng(i * 9)
        x = r.uniform(60, 420) + 30 * math.sin(T * 0.3 + i); y = r.uniform(40, 220) + 20 * math.cos(T * 0.25 + i * 2)
        glow(img, x, y, r.uniform(40, 80), ((120, 80, 200), (60, 140, 180), (200, 90, 150))[i % 3], 0.18)
    a = span(t, 0.2, 1.4)
    glow(img, 240, 150, 90, (255, 214, 140), 0.5 * a + 0.12 * props.thump(T))
    fx.godrays(img, 240, 150, T, 16, (255, 220, 160), 0.05 * a, spread=2 * math.pi, length=300)
    fx.motes(img, d, T, 50, (0, 0, W, H), (255, 226, 180), seed=12, drift=(1, -3), glow_a=0.3)
    pts = []
    for i in range(14):
        ang = i / 14 * 2 * math.pi + T * 0.6
        x, y = 240 + math.cos(ang) * 64, 150 + math.sin(ang) * 30
        pix.twinkle(d, int(x), int(y), (T * 0.7 + i / 14) % 1, (255, 240, 200), 3)
    if a > 0:
        im = pix.char_img('girl', 'young', 'front', 'stand', int(T * 4) % 4, 'happy', 'wave')
        im = pix.outline(im, (255, 226, 150)).resize((32 * 3, 44 * 3), Image.NEAREST)
        dpaste(img, im, 240 - 16 * 3, 214 - 42 * 3, a)
    for i in range(3):
        k = (t * 0.5 + i / 3) % 1
        pix.put(img, 'heart', 200 + i * 40, 120 - k * 50, 1, alpha=a * (1 - k))
    lashes(img, d, 0.06 + 0.02 * math.sin(T * 2))


def s_eyes(img, d, lt, dur, T, amp):
    shots(img, lt, [(0, _close_eyes), (2.3, _see_you)], 0.3, T=T)


# ---------------------------------------------------------------- 10 晴朗的南方
def s_south(img, d, lt, dur, T, amp):
    pix.sky(img, NOON_SKY, 0, 122)
    glow(img, 420, 24, 90, (255, 252, 220), 0.7)
    d.ellipse([408, 12, 432, 36], fill=(255, 252, 230))
    fx.LIGHT = ((1, -1), (255, 250, 230))
    fx.godrays(img, 420, 24, T, 8, (255, 255, 240), 0.05, spread=math.pi * 0.6, center=math.pi * 0.75, length=300)
    for i in range(5):
        x = (i * 120 - lt * 6) % (W + 120) - 60
        fx.cumulus(d, x, 44 + (i % 2) * 22 - (i % 3) * 6, 1.6 if i % 2 == 0 else 1.1, (250, 252, 255), (255, 255, 255), (200, 218, 240),
                   (255, 255, 255), 1, seed=i)
    fx.haze(img, 120, 10, (220, 240, 255), 0.5)
    d.polygon([(300, 122), (340, 108), (372, 112), (420, 122)], fill=(100, 150, 170))
    d.polygon([(330, 122), (340, 112), (352, 114), (372, 122)], fill=(120, 168, 180))
    motifs.sea(img, d, 122, 168, lt)
    for k in range(6):                                         # 一道道往岸边推的浪
        y = 130 + k * 7
        for x in range(0, W, 2):
            if math.sin(x * 0.08 + k * 1.7 - lt * (1.5 + k * 0.3)) > 0.85: d.point((x, y + round(math.sin(x * 0.05 + lt) * 1.2)), fill=(170, 220, 240))
    for i in range(3):
        bx = (100 + i * 60 + lt * 20) % W; by = 80 + i * 10 + 4 * math.sin(T * 2 + i)
        pix.bird(d, bx, by, T, (255, 255, 255), i)
    pix.sky(img, ((0, (250, 230, 180)), (1, (236, 210, 160))), 168, 184)
    off = lt * 150
    for k in range(8):                                         # 路边的棕榈树（远一点，慢一点）
        x = (k * 90 - off * 0.6) % (W + 120) - 60
        motifs.palm(d, x, 186, 0.9 + 0.15 * (k % 2), T, lean=10 + 6 * (k % 3))
    d.rectangle([0, 184, W, 190], fill=(200, 200, 210))
    for k in range(-1, 24):
        x = (k * 24 - off) % (W + 24) - 12
        d.rectangle([x, 178, x + 2, 186], fill=(170, 170, 184))
    d.line([(0, 179), (W, 179)], fill=(220, 220, 230))
    pix.sky(img, ((0, (96, 104, 124)), (1, (80, 86, 104))), 190, 246)
    for k in range(-1, 12):
        x = (k * 48 - off) % (W + 48) - 24
        d.rectangle([x, 217, x + 22, 219], fill=(250, 246, 230))
    bump = round(props.thump(T, 0.2) * 2)
    fx.contact(img, 246, 236, 40, 0.4, (40, 40, 60), 4)
    seat, rack, head = motifs.bicycle(d, 246, 236 - bump, T, 2, roll=-lt * 9, col=(236, 90, 90))
    person_s(img, 'girl', rack[0] + 2, rack[1] + 18, 2, view='side', pose='sit', arms='hug', expr='happy')
    for k in range(4):                                         # 她的头发被风吹向后面
        hy = rack[1] - 44 + k * 3
        d.line([(rack[0] - 6, hy), (rack[0] - 16 - math.sin(T * 9 + k) * 3, hy + 2)], fill=(70, 44, 40), width=2)
    person_s(img, 'boy', seat[0] + 4, seat[1] + 18, 2, view='side', pose='sit', arms='reach', expr='happy')
    pix.sky(img, ((0, (90, 150, 80)), (1, (60, 120, 60))), 246, H)
    for k in range(-1, 16):                                    # 近处的花丛飞快地后退
        x = (k * 34 - off * 1.6) % (W + 34) - 17
        d.ellipse([x - 12, 244, x + 12, 262], fill=(70, 140, 70))
        pix.flower(d, x - 4, 250, ((255, 120, 150), (255, 220, 90), (255, 255, 255))[k % 3], 2, h=0)
        pix.flower(d, x + 5, 254, ((255, 180, 90), (230, 120, 220), (255, 120, 150))[k % 3], 0, h=0)
    for k in range(2):                                         # 离镜头最近的一片棕榈叶，一闪而过
        x = (k * 380 - off * 2.4) % (W + 400) - 200
        rib = [(x + j * 12, -6 + j * 4 + (j / 10) ** 2 * 30) for j in range(13)]
        for j, (px, py) in enumerate(rib[1:], 1):
            ln = 34 - abs(j - 5) * 3
            for sg in (-1, 1):
                d.line([(px, py), (px + sg * 6 + 4, py + ln)], fill=(28, 64, 46), width=3)
                d.line([(px, py), (px + sg * 6 + 4, py + ln)], fill=(50, 100, 70))
        d.line(rib, fill=(70, 110, 70), width=3)
    fx.motes(img, d, T, 20, (0, 0, W, 180), (255, 255, 240), seed=10, drift=(-30, 0), glow_a=0.15)


# ---------------------------------------------------------------- 11 就算犯错 你拿岁月等我
def bouquet(d, x, y):
    d.line([(x, y), (x + 3, y + 6)], fill=(70, 130, 70), width=2)
    for j, (dx, dy) in enumerate(((-2, -2), (2, -3), (0, -5), (4, -1), (-3, 1))):
        d.ellipse([x + dx - 2, y + dy - 2, x + dx + 1, y + dy + 1], fill=((255, 110, 140), (255, 210, 90), (255, 160, 200), (255, 255, 255), (230, 90, 120))[j])


def _fall(img, d, t, T):
    fx.LIGHT = ((-1, -1), (255, 250, 220))
    pix.sky(img, NOON_SKY, 0, 160)
    for i in range(4):
        fx.cumulus(d, 60 + i * 130 - t * 4, 34 + (i % 2) * 18, 1.2, (250, 252, 255), (255, 255, 255), (200, 218, 240), (255, 255, 255), -1, seed=20 + i)
    fx.mountains(img, 162, [(11, 30, 0.6, (150, 190, 200)), (12, 18, 0.55, (120, 170, 160))])
    for i in range(16):                                        # 远处一排树
        x = i * 32 + (i % 3) * 5
        pix.tree_round(d, x, 162, 0.6, (90, 150, 110), (120, 180, 120), (90, 70, 60))
    fx.haze(img, 160, 8, (220, 240, 250), 0.35)
    for i, x in enumerate((40, 140, 330, 430)):
        pix.tree_round(d, x, 166, 1.2, (70, 150, 84), (120, 196, 110))
        fx.contact(img, x, 166, 26, 0.3, (40, 80, 40), 4)
    pix.sky(img, ((0, (150, 196, 110)), (1, (120, 170, 90))), 166, 200)
    fx.tex(img, (0, 166, W, 200), 8, seed=41, scale=2)
    for x in range(0, W, 7):                                   # 灌木
        d.ellipse([x - 6, 190, x + 8, 204], fill=(80, 150, 80)); d.ellipse([x - 4, 191, x + 3, 197], fill=(120, 190, 100))
    pix.sky(img, ((0, (226, 206, 160)), (1, (206, 184, 140))), 200, H)
    fx.tex(img, (0, 200, W, H), 8, seed=42, scale=2)
    for k in range(30):
        r = rng(k)
        x, y = r.uniform(0, W), r.uniform(206, H)
        d.ellipse([x - 2, y - 1, x + 2, y + 1], fill=(190, 166, 126))
    d.ellipse([228, 214, 240, 222], fill=(140, 130, 130)); d.ellipse([230, 214, 236, 217], fill=(180, 170, 170))
    trip = 1.3
    if t < trip:
        x = lerp(90, 224, t / trip)
        fx.contact(img, x, 222, 14, 0.35)
        person_s(img, 'boy', x, 222, 2, view='side', pose='run', ph=pix.wph(t, 10), expr='happy')
        bouquet(d, x + 14, 196)
    else:
        k = t - trip
        if k < 1.1:
            im = pix.char_img('boy', 'young', 'side', 'run', 1, 'surprised').rotate(-90 * eout(k / 0.25), Image.NEAREST, expand=True)
            im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
            img.paste(im, (int(236 - im.width / 2 + 20 * eout(k / 0.25)), int(222 - im.height + 4)), im)
        else:
            person_s(img, 'boy', 262, 222, 2, view='side', pose='sit', expr='sad')
        f = clamp(k / 0.8)
        bx, by = lerp(240, 340, f), lerp(196, 214, f) - 50 * math.sin(math.pi * f)
        if f < 1: bouquet(d, bx, by)
        else:
            for j in range(9):                                 # 花散了一地
                r = rng(j)
                pix.flower(d, 330 + r.uniform(-16, 16), 216 + r.uniform(-4, 4), ((255, 110, 140), (255, 210, 90), (255, 255, 255))[j % 3], 0, h=0)
        props.shake(img, k, 4, 0.4)
        d = ImageDraw.Draw(img)
        x_k = span(k, 0.3, 0.6)
        if x_k > 0:                                            # 一个大大的红叉
            s = eback(x_k) * 16
            cx, cy = 300, 110
            glow(img, cx, cy, 30 * x_k, (255, 80, 80), 0.3)
            for w_, c in ((9, OUT), (5, (236, 60, 70))):
                d.line([(cx - s, cy - s), (cx + s, cy + s)], fill=c, width=w_)
                d.line([(cx - s, cy + s), (cx + s, cy - s)], fill=c, width=w_)
            d.line([(cx - s + 2, cy - s + 1), (cx - 2, cy - 3)], fill=(255, 160, 160), width=1)
    fx.fg(img, T, 'grass', (60, 100, 50), (255, 246, 200), (0, 1), 3, seed=14, h=0.9)


def _wait(img, d, t, T):
    arrive = 2.9
    live = min(t, arrive)
    ph = (live / 0.95) % 1
    night = 0.5 - 0.5 * math.cos(2 * math.pi * ph)
    if t > arrive: night = lerp(night, 0.0, span(t, arrive, arrive + 0.4))
    sky = mix_stops(NOON_SKY, NIGHT_SKY, night)
    if t > arrive: sky = mix_stops(sky, GOLD_SKY, span(t, arrive, arrive + 0.5))
    pix.sky(img, sky, 0, 190)
    pix.stars(d, T, 190, night, 140)
    a = ph * 2 * math.pi
    sx_, sy_ = 240 - math.cos(math.pi * (ph * 2 % 1)) * 220, 170 - math.sin(math.pi * (ph * 2 % 1)) * 140
    if t <= arrive:
        if ph < 0.5: d.ellipse([sx_ - 8, sy_ - 8, sx_ + 8, sy_ + 8], fill=(255, 236, 170))
        else: pix.moon(d, sx_, sy_, 7)
    seasons = ('summer', 'autumn', 'winter', 'spring')
    si = int(live / 0.75) % 4 if t <= arrive else 3
    season = seasons[si]
    gcol = motifs.SEASON[season]['ground']
    for k in range(7):                                         # 远处的房子，夜里亮起窗
        hx = 20 + k * 68; hh = 26 + (k * 13) % 16
        d.rectangle([hx, 190 - hh, hx + 40, 190], fill=lerpc((200, 190, 200), (50, 46, 80), night))
        d.polygon([(hx - 4, 190 - hh), (hx + 20, 190 - hh - 14), (hx + 44, 190 - hh)], fill=lerpc((180, 110, 100), (60, 40, 70), night))
        for wx in (hx + 8, hx + 26):
            d.rectangle([wx, 190 - hh + 8, wx + 5, 190 - hh + 14], fill=lerpc((150, 180, 210), (255, 214, 130), night))
    fx.haze(img, 188, 10, lerpc((230, 236, 250), (40, 40, 80), night), 0.4)
    pix.sky(img, ((0, gcol), (1, lerpc(gcol, (0, 0, 0), 0.2))), 190, H)
    fx.tex(img, (0, 190, W, H), 8, seed=51, scale=2)
    pix.darken(img, 0.35 * night, (10, 10, 40))
    d = ImageDraw.Draw(img)
    fx.contact(img, 150, 196, 40, 0.3, (30, 30, 50), 5); fx.contact(img, 200, 214, 30, 0.3, (30, 30, 50), 4)
    motifs.season_tree(d, 150, 196, 2.0, season, T)
    motifs.bench(d, 200, 214, 1)
    pix.lamp(img, d, 320, 214, on=night, h=60)
    props.clock(d, 320, 132, 9, live * 3, live * 36)
    if season == 'autumn': props.leaves(d, T, 30, seed=3)
    elif season == 'winter': pix.snow(d, T, 90, seed=2)
    elif season == 'spring': pix.petals(d, T, 30, seed=5)
    if t < arrive + 0.5:
        person_s(img, 'girl', 200, 210, 1, view='side', pose='sit', expr='smile')
    else:
        person_s(img, 'girl', 204, 214, 1, view='side', expr='happy')
    if t > arrive - 0.6:
        x = lerp(W + 20, 232, span(t, arrive - 0.6, arrive + 0.2))
        pose = 'run' if t < arrive + 0.2 else 'stand'
        person_s(img, 'boy', x, 214, 1, view='side', pose=pose, ph=pix.wph(t, 10), expr='happy', flip=True)
        fx.LIGHT = None
        k = span(t, arrive + 0.5, arrive + 1.0)
        if k > 0: pix.put(img, 'heart', 218, 168 - 6 * eout(k), 1, alpha=k)


def s_wait(img, d, lt, dur, T, amp):
    shots(img, lt, [(0, _fall), (3.3, _wait)], 0.35, T=T)


# ---------------------------------------------------------------- 12 就算停留 还有你和夜空
def s_roof(img, d, lt, dur, T, amp):
    pix.sky(img, NIGHT_SKY)
    motifs.milky_way(img, T)
    d = ImageDraw.Draw(img)
    pix.stars(d, T, H, 1.0, 200, base=(16, 16, 50))
    pix.moon(d, 70, 44, 12)
    glow(img, 70, 44, 40, (255, 250, 210), 0.3)
    for b in props.beats_in(T - lt, T - lt + dur)[1::3]:
        pix.meteor(d, T, b, 380 - (b * 37) % 200, 20 + (b * 13) % 40, -110, 56, 0.9)
    oy = 120 * (1 - ease(span(lt, 0, 2.6)))
    fx.LIGHT = ((-1, -0.6), (200, 210, 255))
    pix.city(img, d, 262 + oy, 22, 0, (20, 20, 48), (255, 214, 140), 40, 110, 0.2, T, edge=(34, 34, 70))
    pix.city(img, d, 270 + oy, 21, 0, (26, 26, 58), (255, 214, 140), 20, 70, 0.3, T, edge=(40, 40, 80))
    fx.haze(img, 262 + oy, 30, (120, 90, 140), 0.45)
    ry = 210 + oy
    for k, hx in enumerate((20, 430)):                          # 两边别人家的屋顶和天线
        hy = ry + 20 + k * 6
        d.polygon([(hx - 30, hy + 30), (hx, hy), (hx + 40, hy), (hx + 70, hy + 30)], fill=(50, 40, 64))
        d.line([(hx + 10, hy), (hx + 10, hy - 24)], fill=(90, 86, 110))
        d.line([(hx + 2, hy - 18), (hx + 18, hy - 18)], fill=(90, 86, 110)); d.line([(hx + 4, hy - 12), (hx + 16, hy - 12)], fill=(90, 86, 110))
    d.polygon([(80, ry), (420, ry), (470, H + oy), (30, H + oy)], fill=(70, 50, 70))
    for k in range(9):
        y = ry + 6 + k * 7
        d.line([(80 - k * 6, y), (420 + k * 6, y)], fill=(54, 38, 56))
    d.rectangle([76, ry - 3, 424, ry + 1], fill=(90, 66, 86))
    d.rectangle([370, ry - 28, 386, ry], fill=(90, 60, 70))
    props.smoke(img, 378, ry - 30, T, 5, col=(80, 80, 120), shade=(60, 60, 100), vx=-10, vy=-14, r1=8, seed=2, a=0.5)
    sh = (0.62, 0.62, 0.86)
    person_s(img, 'boy', 228, ry + 4, 2, view='back', pose='sit', shade=sh)
    person_s(img, 'girl', 250, ry + 6, 2, view='back', pose='sit', shade=sh)
    pix.put(img, 'heart', 240, ry - 92 + 3 * math.sin(T * 2), 1, alpha=span(lt, 3.2, 3.8))
    fx.motes(img, d, T, 26, (0, 0, W, H), (255, 240, 200), seed=13, drift=(2, -2), glow_a=0.2)


# ---------------------------------------------------------------- 13 我算什么让你无条件的为我
def _rain_walk(img, d, t, T):
    pix.sky(img, ((0, (16, 18, 44)), (1, (40, 40, 80))), 0, 214)
    off = t * 30
    pix.city(img, d, 214, 33, off * 0.4, (30, 32, 64), (255, 210, 130), 40, 120, 0.3, T, edge=(44, 46, 84))
    for k in range(-1, 6):
        x = (k * 110 - off) % (W + 110) - 40
        pix.lamp(img, d, x, 214, 1.0, 54)
    pix.rain(d, T, 0, W, 0, 214, 140, (110, 130, 190), slant=-2, ln=6)
    pix.sky(img, ((0, (40, 40, 70)), (1, (24, 24, 50))), 214, H)
    props.reflect(img, 214, 56, T, a=0.6)
    for k in range(-1, 6):                                     # 路灯照在湿地上的一长条光
        x = (k * 110 - off) % (W + 110) - 40
        glow(img, x + 1, 230, 26, (255, 214, 140), 0.35, ry=6)
        for j in range(5):
            if math.sin(T * 6 + j + k) > 0: d.line([(x - 6 + j * 3, 220 + j * 7), (x + j * 3, 220 + j * 7)], fill=(255, 220, 160))
    d = ImageDraw.Draw(img)
    fx.LIGHT = ((0.6, -1), (255, 214, 150))
    ph = pix.wph(t, 7)
    person_s(img, 'boy', 214, 214, 2, view='side', pose='walk', ph=ph, expr='down')
    person_s(img, 'girl', 252, 214, 2, view='side', pose='walk', ph=ph + 2, arms='umbrella', expr='smile')
    ux = 238
    motifs.umbrella(d, 245, 145, 34, (255, 206, 80), tilt=-0.35)
    for j in range(4):                                         # 她露在伞外面的肩膀被雨打湿
        k = (T * 3 + j / 4) % 1
        x, y = 256 + j * 2, 150 + k * 30
        d.point((x, y), fill=(170, 190, 240))
        if k > 0.8: d.point([(x - 1, 160), (x + 1, 160)], fill=(200, 220, 255))
    pix.rain(d, T + 3, 0, ux - 40, 0, H, 40, (150, 170, 220), slant=-2, ln=8, seed=3)
    pix.rain(d, T + 3, ux + 44, W, 0, H, 40, (150, 170, 220), slant=-2, ln=8, seed=4)
    props.splashes(d, T, 216, 266, 30, seed=2)
    for i in range(6):                                         # 离镜头很近、失焦的大雨滴
        r = rng(i * 3)
        y = (r.uniform(0, H) + T * 420) % (H + 60) - 30
        x = r.uniform(0, W)
        d.line([(x, y), (x - 3, y + 26)], fill=(130, 150, 210), width=3)


def _puddle(img, d, t, T):
    pix.sky(img, ((0, (40, 38, 58)), (1, (30, 28, 46))))
    fx.tex(img, (0, 0, W, H), 9, seed=61, scale=1)
    fx.tex(img, (0, 0, W, H), 5, seed=62, scale=3)
    r = rng(4)
    for _ in range(300):
        x, y = r.uniform(0, W), r.uniform(0, H)
        d.point((x, y), fill=r.choice(((52, 50, 72), (26, 24, 40), (60, 56, 80))))
    for k in range(4):                                         # 落在地上的叶子
        x, y = r.uniform(20, W - 20), r.uniform(10, H - 30)
        if ((x - 240) / 180) ** 2 + ((y - 136) / 100) ** 2 < 1: continue
        d.polygon([(x - 5, y), (x, y - 3), (x + 6, y), (x, y + 3)], fill=r.choice(((150, 100, 60), (120, 130, 60))))
    cx, cy, rx, ry = 240, 136, 170, 92
    lay = Image.new('RGB', (W, H)); ld = ImageDraw.Draw(lay)
    pix.sky(lay, ((0, (20, 24, 60)), (1, (60, 70, 120))))
    motifs.umbrella(ld, 240, 92, 120, (255, 206, 80))
    head = props.head_img('boy', 'young', 'sad' if t < 1.8 else 'closed', 4)
    lay.paste(head, (150, 96), head)
    k = span(t, 1.8, 2.4)
    if k > 0:
        gh = props.head_img('girl', 'young', 'happy', 4)
        dpaste(lay, gh, 266, 96, k)
    if t < 2.2:
        pix.text(lay, '?', 136, 84 - 3 * math.sin(T * 4), col=(255, 250, 240), scale=2)
    a = np.asarray(lay).copy()
    for y in range(H):
        sh = round(2 * math.sin(T * 4 + y * 0.3))
        if sh: a[y] = np.roll(a[y], sh, axis=0)
    a = (a * 0.75 + np.array((20, 24, 60)) * 0.25)
    m = ((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2 < 1 - pix.BAYER * 0.06
    img.paste(Image.fromarray(np.where(m[..., None], a, np.asarray(img)).astype(np.uint8)))
    d = ImageDraw.Draw(img)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=(70, 74, 104))
    d.arc([cx - rx + 4, cy - ry + 3, cx + rx - 4, cy + ry - 3], 200, 330, fill=(130, 140, 180))
    glow(img, 340, 70, 30, (255, 220, 160), 0.3)
    props.ripples(d, T, (cx - 120, cy - 60, cx + 120, cy + 60), 8, (190, 200, 240), seed=3, per=1.1, rmax=12)


def _panel_bg(img, box, top, bot):
    x0, y0, x1, y1 = box
    img.paste(pix.vgrad(x1 - x0, y1 - y0, ((0, top), (1, bot)), 4), (x0, y0))


def _panels(img, d, t, T):
    pix.sky(img, ((0, (255, 236, 214)), (1, (255, 214, 200))))
    for y in range(0, H, 6):
        for x in range((y // 6 % 2) * 3, W, 6): d.point((x, y), fill=(255, 220, 200))
    boxes = [(22, 14, 232, 116), (248, 14, 458, 116), (22, 126, 232, 228), (248, 126, 458, 228)]
    t_start = T - t
    pops = [b - t_start for b in props.beats_in(t_start + 0.05, t_start + 3.4)][:4]
    while len(pops) < 4: pops.append(pops[-1] + 0.8 if pops else 0.1)
    for i, box in enumerate(boxes):
        k = span(t, pops[i], pops[i] + 0.25)
        if k <= 0: continue
        x0, y0, x1, y1 = box
        cx, by = (x0 + x1) / 2, y1 - 12
        dy = round(10 * (1 - eback(k)))
        y0 += dy; y1 += dy; by += dy
        box = (x0, y0, x1, y1)
        if i == 0:                                             # 夏天：分他一半冰棍
            _panel_bg(img, box, (130, 200, 250), (210, 240, 255))
            d.rectangle([x0, by, x1, y1], fill=(130, 190, 100))
            d.ellipse([x1 - 34, y0 + 8, x1 - 16, y0 + 26], fill=(255, 230, 120))
            person_s(img, 'boy', cx - 26, by, 1, view='side', expr='surprised')
            person_s(img, 'girl', cx + 26, by, 1, view='side', arms='reach', expr='happy', flip=True)
            d.rectangle([cx + 8, by - 30, cx + 12, by - 22], fill=(255, 150, 90)); d.line([(cx + 10, by - 22), (cx + 10, by - 18)], fill=(220, 190, 140))
        elif i == 1:                                           # 冬天：把围巾围到他脖子上
            _panel_bg(img, box, (40, 50, 100), (90, 100, 150))
            d.rectangle([x0, by, x1, y1], fill=(236, 240, 250))
            pix.snow(d, T, 30, seed=i)
            pix.person(img, 'boy', cx - 16, by, scarf=(236, 80, 90), expr='shy')
            person_s(img, 'girl', cx + 16, by, 1, view='side', arms='reach', expr='happy', flip=True)
        elif i == 2:                                           # 他摔破了膝盖，她给他贴创可贴
            _panel_bg(img, box, (250, 220, 170), (255, 240, 210))
            d.rectangle([x0, by, x1, y1], fill=(200, 170, 120))
            motifs.bench(d, cx - 20, by, 1)
            person_s(img, 'boy', cx - 20, by - 4, 1, view='side', pose='sit', expr='sad')
            d.rectangle([cx - 15, by - 13, cx - 12, by - 11], fill=(255, 236, 200))
            person_s(img, 'girl', cx + 14, by, 1, view='side', arms='reach', expr='smile', flip=True)
            pix.put(img, 'heart', cx - 2, y0 + 20 + round(math.sin(T * 4)), 1)
        else:                                                  # 夜里提着灯给他照路
            _panel_bg(img, box, (16, 16, 44), (40, 36, 80))
            d.rectangle([x0, by, x1, y1], fill=(50, 44, 70))
            glow(img, cx + 10, by - 18, 40, (255, 210, 120), 0.4)
            tfill(img, 'polygon', [(cx + 10, by - 16), (cx - 60, by), (cx + 60, by)], (255, 220, 140), 0.25)
            person_s(img, 'boy', cx - 26, by, 1, view='side', pose='walk', ph=pix.wph(T, 6), expr='smile')
            person_s(img, 'girl', cx + 4, by, 1, view='side', pose='walk', ph=pix.wph(T, 6) + 2, arms='reach', expr='happy')
            d.rectangle([cx + 10, by - 22, cx + 14, by - 17], fill=(255, 220, 130))
        d.rectangle([x0 - 2, y0 - 2, x1 + 1, y1 + 1], outline=OUT, width=2)
        d.rectangle([x0, y0, x1 - 1, y1 - 1], outline=(255, 252, 244))
    pix.dither_fade(img, ease(span(t, 3.0, 3.5)), (255, 250, 240))


def s_for_me(img, d, lt, dur, T, amp):
    shots(img, lt, [(0, _rain_walk), (4.0, _puddle), (7.6, _panels)], 0.35, T=T)
