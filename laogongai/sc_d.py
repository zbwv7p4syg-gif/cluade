"""老公爱 · 最后一段和片尾（94.3 秒 – 结束）。

跑车 pull up、状态栏回满；寺庙前两个人默契地对动作，PERFECT 连击；一半是水一半是火里的玻璃心；
从墙后走出来不再躲；飞蛾扑火；舞台聚光灯下她在台下鼓掌；身后烧起来的热烈；巨大的橡皮擦擦不掉他；
片尾：楼顶看烟花，片名《老公爱》在霓虹里亮起来，最后一颗心收成 THE END。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
import motifs as M
import kit as K
from props import shots, shake, zoom, person_s, dpaste, big_glyph, thump, last_beat, beats_in, bokeh
from pix import (W, H, FONT, FONT_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky, stars,
                 person, wph, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, BAYER, rain, petals, firework)
from sc_a import burst_bg
from sc_b import lasers, flashes, club, _T0, T_of


# ================================================================ I pull up to，状态还可以
def s_pull_up(img, d, lt, dur, T, A):
    K.night_city(img, d, T, 0)
    K.street_lines(d, 222, 0)
    stop = 1.0
    f = eout(clamp(lt / stop))
    cx = lerp(-120, 150, f)
    hop = max(0, math.sin(clamp((lt - stop) / 0.5) * math.pi * 2)) * 10 if lt > stop else 0
    K.car(img, d, cx, 252, T, roll=f * 20, bounce=hop)
    if lt < stop: M.streaks(img, d, T, (0, 200, W, 260), n=12, speed=500, col=(255, 200, 240), seed=8, dirx=-1)
    if lt > stop + 0.6:                                           # 他从车里出来
        q = lt - stop - 0.6
        person(img, 'boy', lerp(250, 300, eout(clamp(q / 0.5))), 252, view='front' if q > 0.5 else 'side', pose='walk' if q < 0.5 else 'stand',
               ph=wph(q), expr='cool', arms='wave' if q > 0.6 else 'auto', s=3)
    # 状态栏：HP 一格格回满
    hx, hy = 300, 30
    d.rounded_rectangle([hx, hy, hx + 160, hy + 46], 6, fill=(20, 16, 34), outline=(255, 255, 255))
    text(img, '状态', hx + 22, hy + 14, col=(255, 255, 255), font=FONT_S)
    fill = clamp((lt - 0.4) / 1.6)
    for k in range(10):
        c = (90, 255, 140) if k < int(fill * 10) else (50, 50, 70)
        d.rectangle([hx + 44 + k * 11, hy + 8, hx + 52 + k * 11, hy + 20], fill=c)
    text(img, 'OK  还可以!' if fill >= 1 else f'{int(fill * 100)}%', hx + 92, hy + 33, col=(90, 255, 140) if fill >= 1 else (220, 220, 240), font=FONT_S)
    vig(img, 0.35, (10, 4, 24))


# ================================================================ temple 上默契的模拟，打着完美的配合
POSES = ['up', 'wave', 'spread', 'cross', 'hold_l', 'up']


def s_temple(img, d, lt, dur, T, A):
    sky(img, ((0, (60, 40, 110)), (0.5, (200, 100, 130)), (1, (255, 190, 140))), 0, 210, 6)
    glow(img, 240, 200, 200, (255, 200, 140), 0.35, 60)
    K.temple(img, d, 240, 214, 0.82, T)
    d.rectangle([0, 214, W, H], fill=(150, 130, 140))
    for x in range(0, W, 20): d.line([(x, 214), (x - 30, H)], fill=(130, 110, 124))
    petals(d, T, 30, [(255, 200, 220), (255, 230, 240)], 18, 20)
    k = int(lt / 0.45)
    pose = POSES[k % len(POSES)]
    jump = 4 * abs(math.sin(lt / 0.45 * math.pi))
    person(img, 'boy', 186, 246 - jump, view='front', expr='cool', arms=pose, s=3)
    person(img, 'girl', 294, 246 - jump, view='front', expr='happy', arms=pose, s=3)
    q = lt % 0.45
    if k >= 1:
        sc = 2 if q > 0.08 else 3
        K.neon(img, 'PERFECT!', 240, 24, sc, K.YEL, 1)
        text(img, f'COMBO x{k}', 240, 48, col=(255, 255, 255))
        if q < 0.12:
            twinkle(d, 186, 120, q / 0.12, (255, 255, 200), 8); twinkle(d, 294, 120, q / 0.12, (255, 255, 200), 8)
    vig(img, 0.3, (40, 10, 30))


# ================================================================ 曾被唾弃的玻璃心，身处水深火热里
def s_glass_heart(img, d, lt, dur, T, A):
    # 左边是水
    d.rectangle([0, 0, W // 2, H], fill=(20, 50, 110))
    for y in range(0, H, 8):
        pts = [(x, y + 3 * math.sin(x * 0.08 + T * 4 + y)) for x in range(0, W // 2 + 1, 4)]
        d.line(pts, fill=(60, 110, 190))
    for i in range(14):
        r = rng(i); q = (T * 0.4 + r.random()) % 1
        x, y = r.random() * W / 2, H - q * H
        d.ellipse([x - 2, y - 2, x + 2, y + 2], outline=(160, 210, 255))
    # 右边是火
    d.rectangle([W // 2, 0, W, H], fill=(70, 14, 20))
    sub = Image.new('RGB', (W, H)); sd = ImageDraw.Draw(sub)
    K.fire_wall(sub, sd, T, 120, 12, 60, 3)
    img.paste(sub.crop((W // 2, 0, W, H)), (W // 2, 0))
    K.embers(d, T, 40, 2, (W // 2, 0, W, H))
    d.line([(W // 2, 0), (W // 2, H)], fill=(255, 255, 255))
    # 玻璃心：半透明的淡青，裂缝越来越多
    crack = clamp((lt - 0.4) / 2.0)
    M.heart(img, 240, 120, 3.2, beat=thump(T, 0.3), crack=crack, col=((190, 240, 255), (240, 255, 255), (120, 180, 220)))
    glow(img, 240, 120, 90, (200, 240, 255), 0.25)
    # 扔过来的“唾弃”：倒竖的大拇指
    for j in range(5):
        r = rng(j * 3)
        t0 = 0.3 + j * 0.45
        q = lt - t0
        if q < 0 or q > 0.5: continue
        side = -1 if j % 2 else 1
        x = lerp(240 + side * 260, 240 + side * 40, q / 0.5)
        y = lerp(40 + r.random() * 160, 120, q / 0.5)
        text(img, '呸!', x, y, col=(255, 255, 255), scale=2)
        if q > 0.42: shake(img, q - 0.42, 3, 0.08)
    vig(img, 0.35, (6, 4, 16))


# ================================================================ 现在不会再去躲避了
def s_no_hide(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(24, 16, 40))
    d.rectangle([0, 230, W, H], fill=(36, 28, 52))
    out = lt > 0.55
    glow(img, 240, 150, 120, (255, 240, 200), 0.4 * (1 if out else 0.2))
    if out: tfill(img, 'polygon', [(220, 0), (260, 0), (310, 236), (170, 236)], (255, 250, 220), 0.18)
    # 墙
    d.rectangle([120, 60, 190, 236], fill=(80, 60, 100), outline=pix.OUT)
    for y in range(64, 236, 10):
        for x in range(122 + ((y // 10) % 2) * 8, 190, 16): d.rectangle([x, y, x + 13, y + 7], fill=(96, 74, 118))
    if not out:
        person(img, 'boy', 196, 236, view='side', flip=True, expr='worried', s=3)
        d.rectangle([120, 60, 186, 236], fill=(80, 60, 100))
        for y in range(64, 236, 10):
            for x in range(122 + ((y // 10) % 2) * 8, 186, 16): d.rectangle([x, y, x + min(13, 186 - x), y + 7], fill=(96, 74, 118))
    else:
        q = lt - 0.55
        x = lerp(200, 250, eout(clamp(q / 0.3)))
        person(img, 'boy', x, 236, view='front', expr='cool', arms='cross', s=3)
        if q < 0.2: shake(img, q, 3, 0.2)
        K.neon(img, 'NO MORE HIDING', 240, 30, 2, K.CYAN, 1)
    vig(img, 0.4, (6, 4, 16))


# ================================================================ not at all，像扑火的飞蛾吧
def s_moth(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(8, 4, 14))
    # 蜡烛
    d.rectangle([228, 170, 252, 250], fill=(250, 240, 220), outline=pix.OUT)
    d.line([(240, 170), (240, 162)], fill=(40, 30, 30))
    fl = 30 + (30 * clamp((lt - 0.8) / 0.2) if lt > 0.8 else 0)
    K.flame(img, d, 240, 166, fl, T)
    # 飞蛾绕圈越绕越近，最后一头扎进去
    k = clamp(lt / 0.85)
    a = lt * 9
    r = lerp(110, 0, ease(k))
    mx, my = 240 + math.cos(a) * r, 130 + math.sin(a) * r * 0.6
    if lt < 0.85: K.moth(d, mx, my, T, 2)
    else:
        q = lt - 0.85
        for j in range(16):
            aa = j / 16 * 2 * math.pi
            d.point((240 + math.cos(aa) * q * 160, 140 + math.sin(aa) * q * 100), fill=(255, 200, 100))
        if q < 0.1: pix.dither_fade(img, 1 - q / 0.1, (255, 230, 180))
    vig(img, 0.5, (2, 0, 6))


# ================================================================ 谁拯救我呢，她会欣赏我吧
def s_stage(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(20, 10, 34))
    d.rectangle([0, 0, W, 16], fill=(150, 20, 50))
    for x in range(0, W, 24): d.chord([x - 4, -10, x + 28, 24], 0, 180, fill=(180, 30, 60))
    d.rectangle([0, 0, 40, 200], fill=(150, 20, 50)); d.rectangle([W - 40, 0, W, 200], fill=(150, 20, 50))
    d.rectangle([40, 168, W - 40, 186], fill=(100, 70, 60)); d.line([(40, 168), (W - 40, 168)], fill=(160, 120, 90))
    tfill(img, 'polygon', [(220, 0), (260, 0), (300, 172), (180, 172)], (255, 250, 220), 0.22)
    glow(img, 240, 168, 70, (255, 250, 220), 0.4, 14)
    K.mic(d, 262, 110, 1.0, base=168)
    person(img, 'boy', 240, 170, view='front', expr='laugh' if lt > 1.0 else 'closed', arms='up' if lt > 1.0 else 'auto', s=3)
    # 观众剪影，她在第一排鼓掌
    for i in range(12):
        x = 20 + i * 40
        if i == 6: continue
        jump = abs(math.sin(T * 4 + i)) * 3
        person_s(img, 'boy' if i % 2 else 'girl', x, H + 12 - jump, 2, 'alt' if i % 3 else 'young', 'back', 'stand', 0, 'happy',
                 'up' if (int(T * 3) + i) % 2 else 'auto', shade=(0.2, 0.15, 0.3))
    gx = 250
    person(img, 'girl', gx, H + 14, view='back', expr='happy', arms='up' if int(T * 6) % 2 else 'cover', s=2)
    for j in range(5):
        q = (T * 0.8 + j / 5) % 1
        pix.put(img, 'heart', gx - 20 + j * 10 + 6 * math.sin(T * 3 + j), 200 - q * 60, 1, alpha=1 - q)
    if lt > 1.0: K.bubble(img, d, 330, 30, '好帅!', 'l', a=clamp((lt - 1.0) / 0.2))
    vig(img, 0.35, (6, 2, 16))


# ================================================================ 她的热烈比我想象中的还要火辣
def s_hot(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(80, 10, 20))
    K.fire_wall(img, d, T, 190 - 50 * clamp(lt / 1.5), 14, 50, 6)
    K.embers(d, T, 70, 3)
    burst = thump(T, 0.3)
    person(img, 'girl', 240, 246, view='front', expr='laugh', arms=['up', 'spread', 'wave', 'up'][int(lt * 3) % 4], ph=int(lt * 6), s=4)
    glow(img, 240, 170, 100, (255, 120, 60), 0.3 + 0.2 * burst)
    K.neon(img, 'HOT', 240, 40, 4, (255, 210, 80), 1)
    for j in range(4):                                            # 辣椒
        r = rng(j)
        x = 60 + j * 120 + 10 * math.sin(T * 2 + j)
        y = 90 + 20 * math.sin(T * 3 + j * 2)
        d.ellipse([x - 10, y - 4, x + 10, y + 6], fill=(230, 30, 40), outline=pix.OUT)
        d.line([(x + 8, y - 2), (x + 14, y - 8)], fill=(60, 160, 60), width=2)
    # 热浪：画面上下抖
    a = np.asarray(img).copy()
    for y in range(0, H, 2):
        dx = int(2 * math.sin(y * 0.15 + T * 12))
        a[y] = np.roll(a[y], dx, 0)
    img.paste(Image.fromarray(a))
    vig(img, 0.35, (40, 4, 10))


# ================================================================ I got talent，nobody 能将我抹杀
def s_talent(img, d, lt, dur, T, A):
    K.night_city(img, d, T, T * 6)
    d.rectangle([150, 200, 330, H], fill=(40, 30, 54)); d.rectangle([140, 196, 340, 204], fill=(70, 56, 90))
    person(img, 'boy', 240, 200, view='front', expr='cool', arms='spread' if lt > 1.6 else 'cross', s=3)
    glow(img, 240, 150, 70, K.YEL, 0.3 + 0.2 * thump(T, 0.3))
    # 巨大的橡皮擦从右往左擦过来：擦掉的地方变成白纸，但擦不掉他
    k = clamp((lt - 0.2) / 1.2)
    ex = lerp(W + 80, 140, ease(k))
    erased = ex if lt < 1.5 else lerp(ex, W + 40, ease(clamp((lt - 1.7) / 0.8)))     # 撞碎以后，擦掉的地方又长回来
    if k > 0:
        a = np.asarray(img).copy()
        m = np.zeros((H, W), bool); m[:, int(max(0, erased + 40)):] = True
        keep = np.zeros((H, W), bool); keep[60:205, 200:282] = True       # 他所在的地方
        m &= ~keep
        a[m] = (250, 246, 240)
        img.paste(Image.fromarray(a))
    if lt < 1.5:
        d.rounded_rectangle([ex, 60, ex + 80, 200], 8, fill=pix.OUT)
        d.rounded_rectangle([ex + 2, 62, ex + 78, 198], 7, fill=(255, 140, 180))
        d.rectangle([ex + 2, 130, ex + 78, 198], fill=(100, 160, 240))
        text(img, 'ERASE', ex + 40, 164, col=(255, 255, 255))
    else:                                                         # 橡皮擦撞上他，碎掉
        q = lt - 1.5
        for j in range(24):
            r = rng(j)
            x = 290 + r.uniform(-20, 40) + r.uniform(20, 120) * q
            y = 120 + r.uniform(-40, 60) - 80 * q + 200 * q * q
            d.rectangle([x, y, x + 4, y + 4], fill=(255, 140, 180) if j % 2 else (100, 160, 240))
        if q < 0.3: shake(img, q, 6, 0.3)
        K.neon(img, 'TALENT', 240, 34, 3, K.YEL, 1)
        twinkle(d, 240, 120, (q * 2) % 1, (255, 255, 200), 10)
    vig(img, 0.3, (10, 4, 24))


# ================================================================ 片尾：楼顶看烟花，片名亮起来
def s_outro(img, d, lt, dur, T, A):
    sky(img, K.NIGHT_SKY, 0, 210, 6)
    stars(d, T, 160, 1.0, 150)
    for i in range(10):
        t0 = 0.3 + i * 0.75
        firework(img, d, lt, t0, 60 + (i * 97) % 360, 50 + (i * 31) % 60, [K.PINK, K.CYAN, K.YEL, K.PURP][i % 4], r=34 + (i % 3) * 8, seed=i)
    pix.city(img, d, 214, 71, T * 3, (36, 22, 64), (255, 210, 140), 30, 110, 0.3, T)
    d.rectangle([0, 210, W, H], fill=(40, 28, 56)); d.rectangle([0, 206, W, 212], fill=(80, 60, 100))
    person(img, 'boy', 222, 210, view='back', expr='happy', arms='hold_r', s=3)
    person(img, 'girl', 258, 210, view='back', expr='happy', arms='hold_l', s=3)
    if lt > 2.5:
        a = clamp((lt - 2.5) / 0.6)
        K.title(img, 240, 62, 3, a, T)
    if lt > 4.0: K.pix_heart(img, 240, 168, 0.5 + 0.1 * thump(T, 0.3), alpha=clamp((lt - 4.0) / 0.4))
    vig(img, 0.35, (6, 2, 16))


def s_end(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(10, 4, 18))
    stars(d, T, H, 0.6, 120)
    a = clamp(lt / 0.8) * clamp((dur - lt) / 1.2)
    glow(img, 240, 110, 160, K.PINK, 0.35 * a, 60)
    K.title(img, 240, 100, 4, a, T, 0)
    if lt > 0.8:
        text(img, '— THE END —', 240, 176, col=(255, 210, 236), alpha=a)
    for j in range(10):
        r = rng(j)
        q = (T * 0.3 + r.random()) % 1
        pix.put(img, 'heart', r.random() * W, H - q * H, 1, alpha=a * (1 - q))


s_end.no_sub = True
