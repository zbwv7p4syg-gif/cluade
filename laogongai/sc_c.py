"""老公爱 · 第二段说唱（68.0 – 94.3 秒）。

录音棚里关掉 autotune、她的心是个猜不透的迷宫；台灯下揉了一地的情书；焦虑的乌云和心电图；高速上失控的跑车；
霓虹都市里 flexing；硬币雨里逃离；俯瞰整座城市找她；她挽着他，对路过的人瞧都不瞧；戳她气鼓鼓的脸；打碟台上 beat drop。
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
                 person, wph, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, BAYER, rain, petals)
from sc_a import burst_bg
from sc_b import lasers, flashes, club, _T0, T_of


# ================================================================ 不再打开 autotune，你的心我猜不懂
def studio(img, d, t):
    T = T_of(t)
    d.rectangle([0, 0, W, H], fill=(40, 30, 50))
    for x in range(0, W, 16):                                    # 吸音棉
        for y in range(0, 200, 16):
            d.polygon([(x, y), (x + 16, y), (x + 8, y + 16)], fill=(56, 44, 70) if (x // 16 + y // 16) % 2 else (48, 38, 60))
    d.rectangle([0, 200, W, H], fill=(30, 24, 40))
    # 机架上的效果器
    d.rectangle([110, 60, 370, 190], fill=(24, 22, 30), outline=pix.OUT)
    off = t > 0.9
    d.rectangle([124, 74, 356, 128], fill=(60, 60, 76), outline=(100, 100, 120))
    K.neon(img, 'AUTO-TUNE', 220, 100, 2, (120, 255, 160) if not off else (80, 80, 90), 0.0 if off else 1.0)
    # 开关
    sx, sy = 330, 100
    d.rounded_rectangle([sx - 14, sy - 8, sx + 14, sy + 8], 8, fill=(30, 30, 40))
    kx = sx + (8 if not off else -8)
    d.ellipse([kx - 7, sy - 7, kx + 7, sy + 7], fill=(255, 255, 255))
    d.ellipse([sx - 20, 140, sx - 12, 148], fill=(80, 255, 120) if not off else (255, 50, 60))
    text(img, 'ON' if not off else 'OFF', sx, 160, col=(80, 255, 120) if not off else (255, 80, 90))
    # 推子和电平表
    for i in range(8):
        lv = 0 if off else abs(math.sin(T * 6 + i)) * 8
        for k in range(int(lv)): d.rectangle([130 + i * 18, 180 - k * 5, 140 + i * 18, 183 - k * 5], fill=K.CYAN if k < 6 else (255, 80, 80))
    if t < 0.95: K.finger(d, sx - 4, sy + 6, 2, 1.0 if t > 0.7 else 0)
    if 0.9 < t < 1.1: K.glitch(img, T, 1.2, 9)


def heart_maze(img, d, t):
    T = T_of(t)
    d.rectangle([0, 0, W, H], fill=(30, 14, 40))
    cx, cy = 240, 124
    s = 5.6
    K.pix_heart(img, cx, cy, s, (255, 90, 160), (255, 190, 220), (170, 40, 110))
    # 心里面画一个迷宫
    r = rng(4)
    for gx in range(-12, 13):
        for gy in range(-9, 12):
            x, y = cx + gx * 8, cy + gy * 8
            if not inside_heart((x - cx) / s, (y - cy) / s): continue
            if r.random() < 0.5: d.line([(x, y), (x + 8, y)], fill=(120, 20, 70), width=2)
            else: d.line([(x, y), (x, y + 8)], fill=(120, 20, 70), width=2)
    # 一个小小的他在迷宫里打转
    k = (t * 1.2) % 1
    px, py = cx - 30 + 60 * math.sin(k * 2 * math.pi), cy + 10 * math.cos(k * 4 * math.pi)
    person(img, 'boy', px, py + 10, view='side', pose='walk', ph=wph(t), flip=math.cos(k * 2 * math.pi) < 0, expr='worried')
    for j in range(6):
        a = j / 6 * 2 * math.pi + T
        text(img, '?', cx + math.cos(a) * 150, cy + math.sin(a) * 90, col=(255, 240, 140), scale=2 if j % 2 else 1)


def inside_heart(x, y):
    # 心形隐式方程，心尖朝下：(x² + y² − 1)³ − x² y³ < 0（y 向上为正）
    x, y = x / 15, -(y - 2) / 15
    return (x * x + y * y - 1) ** 3 - x * x * y ** 3 < 0


def s_autotune(img, d, lt, dur, T, A):
    _T0[0] = T - lt
    shots(img, lt, [(0, studio), (1.45, heart_maze)], 0.2)
    vig(img, 0.4, (6, 4, 16))


# ================================================================ wrote her love letter，苦想好几封
def s_letters(img, d, lt, dur, T, A):
    K.room(img, d, T, 1.0, (44, 30, 70), window=True)
    darken(img, 0.35, (8, 4, 20))
    top = K.desk(img, d, 140, 226, 170)
    person(img, 'boy', 200, 226, view='side', pose='sit', arms='type', expr='worried' if int(lt * 2) % 2 else 'down', s=3)
    K.letter(d, 222, top - 6, 40, 6, 1, f=1)
    # 揉成团的纸一个个往后扔，越堆越多
    n = int(lt / 0.32)
    for i in range(n + 1):
        q = lt - i * 0.32
        r = rng(i)
        tx, ty = 60 + r.uniform(-30, 40), 222 - (i // 3) * 6 - r.uniform(0, 4)
        if q < 0: continue
        if q < 0.4:
            f = q / 0.4
            x = lerp(196, tx, f); y = lerp(150, ty, f) - 50 * math.sin(f * math.pi)
        else: x, y = tx, ty
        d.ellipse([x - 5, y - 5, x + 5, y + 4], fill=(250, 246, 236), outline=(150, 140, 150))
        d.line([(x - 2, y - 2), (x + 2, y)], fill=(190, 180, 190))
    text(img, f'x{n + 1}', 60, 160, col=(255, 230, 160), scale=2)
    for j in range(3):
        K.pix_heart(img, 240 + j * 20, 100 - (lt * 20 + j * 10) % 40, 0.25, alpha=0.8)
    vig(img, 0.45, (6, 4, 16))


# ================================================================ 患得患失，feel lonely，患了焦虑症
def s_anxiety(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(36, 34, 46))
    d.rectangle([0, 224, W, H], fill=(26, 24, 34))
    glow(img, 240, 230, 100, (120, 120, 160), 0.3, 16)
    person(img, 'boy', 240, 230, view='front', pose='sit', expr='sad', arms='lap', s=3)
    # 头顶一团乱麻似的乌云，下雨
    cx, cy = 240, 70
    for k in range(40):
        a = k * 0.7 + T * 3
        r = 24 + 14 * math.sin(k * 1.3 + T * 2)
        d.line([(cx + math.cos(a) * r, cy + math.sin(a) * r * 0.5), (cx + math.cos(a + 0.8) * r, cy + math.sin(a + 0.8) * r * 0.5)],
               fill=(70, 66, 90), width=2)
    rain(d, T, 200, 280, 90, 230, 30, (120, 140, 200), 200, 0, 4)
    # 心电图：横穿屏幕，拍子上猛跳
    pts = []
    for x in range(0, W, 2):
        q = (x / W * 4 + lt * 2) % 1
        y = 150
        if 0.4 < q < 0.46: y -= 28 * math.sin((q - 0.4) / 0.06 * math.pi)
        elif 0.46 < q < 0.5: y += 16 * math.sin((q - 0.46) / 0.04 * math.pi)
        pts.append((x, y + 2 * math.sin(x * 0.7 + T * 20) * thump(T, 0.3)))
    d.line(pts, fill=(255, 80, 120), width=2)
    for j, (s, x, y) in enumerate((('?', 120, 60), ('!', 360, 80), ('...', 100, 120), ('?', 380, 40))):
        if (int(T * 3) + j) % 2: text(img, s, x, y, col=(200, 200, 230), scale=2)
    K.neon(img, 'LONELY', 400, 200, 1, K.CYAN, K.flicker(T, 7, 0.2))
    grade(img, 0.6)
    vig(img, 0.5, (6, 4, 16))


# ================================================================ 我早就停不下来了，也快要失控
def s_out_of_control(img, d, lt, dur, T, A):
    off = T * 500
    sky(img, K.NIGHT_SKY, 0, 180, 6)
    pix.city(img, d, 180, 51, off * 0.1, (40, 24, 70), (255, 200, 140), 40, 120, 0.3, T)
    d.rectangle([0, 180, W, H], fill=(30, 26, 40))
    for x in range(int(-off) % 60 - 60, W, 60): d.rectangle([x, 222, x + 30, 225], fill=(255, 220, 120))
    for x in range(int(-off * 1.3) % 80 - 80, W, 80): d.rectangle([x, 184, x + 4, 200], fill=(200, 200, 220))      # 护栏
    d.line([(0, 200), (W, 200)], fill=(200, 200, 220))
    M.streaks(img, d, T, (0, 100, W, 260), n=30, speed=900, col=(255, 230, 255), seed=4, dirx=-1)
    wob = 4 * math.sin(T * 30) * clamp(lt / 2)
    K.car(img, d, 160 + wob, 246, T, roll=T * 30, bounce=abs(math.sin(T * 20)) * 2)
    # 速度表：指针一路甩进红区
    gx, gy, r = 400, 70, 36
    d.ellipse([gx - r - 2, gy - r - 2, gx + r + 2, gy + r + 2], fill=pix.OUT)
    d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=(30, 26, 40))
    d.arc([gx - r + 4, gy - r + 4, gx + r - 4, gy + r - 4], 140, 330, fill=(200, 200, 220), width=3)
    d.arc([gx - r + 4, gy - r + 4, gx + r - 4, gy + r - 4], 330, 400, fill=(255, 50, 60), width=3)
    a = math.radians(lerp(140, 395, ease(clamp(lt / 1.6))) + 6 * math.sin(T * 40) * clamp(lt - 1.4))
    d.line([(gx, gy), (gx + math.cos(a) * (r - 6), gy + math.sin(a) * (r - 6))], fill=(255, 80, 80), width=2)
    text(img, 'MAX', gx, gy + 18, col=(255, 80, 80), font=FONT_S)
    shake(img, (T * 7) % 0.2, 1 + 3 * clamp(lt / 2), 0.2)
    K.glitch(img, T, clamp((lt - 1.2) / 0.8) * 0.9, 3)
    vig(img, 0.4, (6, 4, 16))


# ================================================================ flexing 都市的霓虹，all be cuz show off u
def s_flex(img, d, lt, dur, T, A):
    K.night_city(img, d, T, T * 8)
    # 巨幅广告牌上是她
    bx0, by0 = 300, 30
    d.rectangle([bx0 - 3, by0 - 3, bx0 + 143, by0 + 93], fill=(20, 16, 30))
    d.rectangle([bx0, by0, bx0 + 140, by0 + 90], fill=(255, 140, 200))
    for i in range(0, 140, 10): d.line([(bx0 + i, by0), (bx0 + i - 20, by0 + 90)], fill=(255, 160, 210))
    hb = props.face('girl', 'happy', 3)
    img.paste(hb, (int(bx0 + 34), int(by0 + 6)), hb)
    K.neon(img, 'U ♥', bx0 + 116, by0 + 74, 1, (255, 255, 255), 1, small=True, glow_r=10)
    flashes(img, d, T, 6, 1, (0, 120, W, 220))
    person(img, 'boy', 180, 238, view='front', expr='cool', arms='cross', s=4)
    for j in range(6):                                          # 链子在闪
        sparkle(d, 168 + j * 5, 128 + (j % 3), T * 3 + j, (255, 250, 200), 2)
    K.neon(img, 'FLEX', 70, 60, 3, K.YEL, K.flicker(T, 11))
    vig(img, 0.35, (10, 4, 24))


# ================================================================ pay me back，don't be worry，再着急的逃离
def coin(d, x, y, t, s=1):
    w = abs(math.cos(t * 8)) * 5 * s + 1
    d.ellipse([x - w, y - 5 * s, x + w, y + 5 * s], fill=(255, 210, 60), outline=(180, 120, 30))
    if w > 3: d.line([(x, y - 2 * s), (x, y + 2 * s)], fill=(200, 140, 30))


def s_escape(img, d, lt, dur, T, A):
    off = lt * 220
    d.rectangle([0, 0, W, H], fill=(24, 16, 36))
    for i in range(-1, 8):                                       # 小巷两边的砖墙和门
        x = i * 80 - off % 80
        d.rectangle([x, 20, x + 76, 210], fill=(60, 36, 50))
        for y in range(24, 210, 8):
            for xx in range(int(x) + ((y // 8) % 2) * 6, int(x) + 76, 12): d.rectangle([xx, y, xx + 10, y + 6], fill=(74, 44, 60))
        if i % 2: d.rectangle([x + 20, 120, x + 50, 210], fill=(30, 20, 30)); glow(img, x + 35, 110, 18, (255, 200, 120), 0.4)
    K.neon(img, 'PAY ME BACK', 300 - off * 0.2, 60, 2, K.YEL, K.flicker(T, 5))
    d.rectangle([0, 210, W, H], fill=(36, 28, 44))
    for i in range(40):                                          # 硬币雨
        r = rng(i)
        x = (r.random() * W * 1.3 - off * 0.3) % W
        y = (lt * (140 + 60 * r.random()) + r.random() * 280) % 280 - 10
        coin(d, x, y, T + i)
    person(img, 'boy', 260, 236, view='side', pose='run', ph=wph(lt, 12), expr='laugh', s=3)
    for j in range(3): coin(d, 230 - j * 16, 170 + j * 8 + 4 * math.sin(T * 9 + j), T + j * 2, 1)
    vig(img, 0.4, (6, 4, 16))


# ================================================================ 一味地错到底，不停寻找 in the whole city
def s_search_city(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(20, 14, 34))
    pan = lt * 30
    for gx in range(-1, 9):
        for gy in range(-1, 6):
            x, y = gx * 64 - pan % 64, gy * 56 - (pan * 0.5) % 56
            r = rng(int(gx + pan // 64) * 31 + int(gy + (pan * 0.5) // 56) * 7)
            d.rectangle([x + 6, y + 6, x + 52, y + 44], fill=(40 + r.randrange(20), 28, 70 + r.randrange(20)))
            for k in range(6):
                if r.random() < 0.5: d.rectangle([x + 10 + k * 7, y + 10, x + 13 + k * 7, y + 13], fill=(255, 210, 120))
            if r.random() < 0.3: K.neon(img, '♥', x + 40, y + 30, 1, K.PINK, K.flicker(T, gx * 7 + gy), small=True, glow_r=8)
    # 探照灯扫来扫去
    sx, sy = 240 + 160 * math.sin(T * 1.6), 140 + 70 * math.sin(T * 2.3 + 1)
    pix.blend_box(img, (0, 0, W, H), (0, 0, 10), np.full((H, W), 0.45))
    glow(img, sx, sy, 60, (255, 255, 220), 0.55)
    d.ellipse([sx - 50, sy - 50, sx + 50, sy + 50], outline=(255, 255, 200))
    person(img, 'boy', sx, sy + 20, view='front', pose='walk', ph=wph(lt), expr='worried', s=1)
    # 一个闪着的粉色小点（她）总在探照灯外面
    hx, hy = sx + 120 * math.cos(T * 1.2), sy - 60 * math.sin(T * 1.7)
    hx, hy = hx % W, max(20, min(H - 40, hy))
    if int(T * 4) % 2: pix.put(img, 'heart', hx, hy, 2)
    K.neon(img, 'WHOLE CITY', 240, 24, 2, K.CYAN, 1)
    vig(img, 0.4, (4, 2, 12))


# ================================================================ she's only own me，她根本瞧都不瞧你
def s_ignore(img, d, lt, dur, T, A):
    sky(img, ((0, (60, 110, 200)), (0.7, (150, 190, 240)), (1, (220, 230, 250))), 0, 200, 5)
    pix.city(img, d, 200, 61, lt * 10, (130, 150, 200), (240, 240, 255), 30, 90, 0.2, T)
    d.rectangle([0, 200, W, H], fill=(190, 186, 196)); d.line([(0, 200), (W, 200)], fill=(150, 146, 160))
    # 路人（他）捧着花站在左边招手
    rx = 120
    sad = lt > 1.4
    person(img, 'boy', rx, 236, 'rival', view='side', expr='sad' if sad else 'smile', arms='down' if sad else 'wave', ph=int(lt * 6), s=3)
    fx, fy = rx + 14, 156 + (10 if sad else 0)
    d.line([(fx, fy), (fx + (6 if sad else 2), fy - 14 + (8 if sad else 0))], fill=(60, 140, 60), width=2)
    for k in range(3):
        c = (255, 80, 120) if not sad else (150, 110, 120)
        d.ellipse([fx - 4 + k * 4 + (6 if sad else 0), fy - 20 + (12 if sad else 0), fx + k * 4 + (6 if sad else 0), fy - 16 + (12 if sad else 0)], fill=c)
    if sad:
        cloud(d, rx - 24, 60, 1.6, (120, 120, 140), (90, 90, 110))
        rain(d, T, rx - 22, rx + 24, 80, 236, 14, (140, 160, 220), 180, 0, 4)
    # 她挽着他从右往左走过，下巴一抬
    u = clamp(lt / 3.0)
    x = lerp(W + 40, 200, eout(u))
    person(img, 'boy', x, 236, view='side', pose='walk', ph=wph(lt), flip=True, expr='cool', arms='hold', s=3)
    person(img, 'girl', x + 30, 236, view='side', pose='walk', ph=wph(lt) + 2, flip=True, expr='closed', arms='hold_f', s=3)
    if lt > 1.0: K.bubble(img, d, x + 40, 84, '哼~', 'l', a=clamp((lt - 1.0) / 0.2))
    if lt > 0.6: K.neon(img, 'ONLY ME', 380, 30, 2, K.PINK, 1)
    vig(img, 0.25, (40, 40, 80))


# ================================================================ wow babe～ I hope u don't be silly
def s_silly(img, d, lt, dur, T, A):
    burst_bg(img, d, T, (255, 200, 225), (255, 220, 236), 240, 110, 20, 0.2)
    expr = 'neutral' if lt < 0.9 else ('laugh' if lt > 1.4 else 'surprised')
    props.bust(img, d, 'girl', 240, 30, 5, 'sad' if lt < 0.9 else expr, T=T)
    if lt < 0.9:                                                  # 气鼓鼓：脸颊鼓起来
        for cx in (240 - 44, 240 + 40):
            d.ellipse([cx - 6, 112, cx + 6, 122], fill=(255, 150, 160))
        text(img, '哼!', 330, 40, col=(255, 80, 120), scale=2)
    # 手指戳过来
    fx = lerp(W + 40, 288, eout(clamp((lt - 0.5) / 0.4)))
    fy = 118
    if lt > 0.5:
        d.rounded_rectangle([fx, fy - 6, fx + 120, fy + 6], 6, fill=pix.OUT)
        d.rounded_rectangle([fx + 1, fy - 5, fx + 120, fy + 5], 5, fill=pix.SKIN)
        d.rectangle([fx + 2, fy - 3, fx + 8, fy + 3], fill=(255, 236, 226))
    if lt > 0.9:
        q = lt - 0.9
        K.heart_burst(img, d, q, 280, 118, 10, 60, K.PINK, 0.8)
        K.neon(img, 'silly~', 120, 50, 2, K.PINK, 1)
        if q < 0.2: shake(img, q, 3, 0.2)
    vig(img, 0.2, (200, 100, 150))


# ================================================================ I beat drop this melody
def s_beat_drop(img, d, lt, dur, T, A):
    drop = 0.55
    dropped = lt > drop
    club(img, d, T, crowd=dropped)
    if dropped: lasers(img, d, T * 2, 9, 0, a=0.45, seed=3)
    # 打碟台
    d.rectangle([90, 176, 390, 240], fill=(26, 22, 36), outline=pix.OUT)
    K.neon(img, 'DJ', 240, 222, 2, K.PINK, 1)
    person(img, 'boy', 240, 190, view='front', expr='cool', arms='flowers' if not dropped else 'up', s=3)
    d.rectangle([90, 176, 390, 196], fill=(36, 32, 50), outline=pix.OUT)
    K.turntable(d, 140, 186, 9, T)
    K.turntable(d, 340, 186, 9, -T)
    b = thump(T, 0.3)
    K.pads(img, d, 196, 180, 4, 3, lambda i, j: (1.0 if dropped and (i + j + int(T * 6)) % 3 == 0 else 0.2) * (0.5 + 0.5 * b))
    K.speaker(img, d, 14, 110, 60, 120, b if dropped else 0)
    K.speaker(img, d, 406, 110, 60, 120, b if dropped else 0)
    if dropped:
        q = lt - drop
        for k in range(3):                                       # 冲击波
            r = (q * 400 + k * 80) % 480
            d.ellipse([240 - r, 120 - r * 0.6, 240 + r, 120 + r * 0.6], outline=lerpc(K.CYAN, (16, 8, 30), r / 480), width=2)
        if q < 0.12: pix.dither_fade(img, 1 - q / 0.12, (255, 240, 255))
        if q < 0.4: shake(img, q, 6, 0.4)
        K.neon(img, 'DROP!', 240, 50, 3, K.YEL, 1)
    else:
        text(img, '3 2 1 ...', 240, 50, col=(255, 255, 255), scale=2, alpha=clamp(lt / 0.2))
    vig(img, 0.35, (6, 2, 16))
