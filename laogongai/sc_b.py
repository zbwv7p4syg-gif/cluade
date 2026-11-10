"""老公爱 · 预副歌和第二段（35.9 – 68.0 秒）。

新牛仔裤走秀、兄弟们、派对上甩掉想她的念头、压下来的黑夜和胸口跳得发烫的心、拉住手、上锁的回忆胶片、
翻得飞快的日历和破门而入的她、抽屉里的信、胸口的心形烙印、传不到她耳朵里的声音。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
import motifs as M
import kit as K
from props import shots, shake, zoom, person_s, dpaste, big_glyph, thump, last_beat, beats_in, bokeh, puff
from pix import (W, H, FONT, FONT_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky, stars,
                 person, wph, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, BAYER, rain, petals)
from sc_a import burst_bg, photo_two


def lasers(img, d, T, n=6, y0=0, cols=(K.PINK, K.CYAN, K.PURP, K.YEL), a=0.35, seed=0):
    for i in range(n):
        x0 = (i + 0.5) * W / n
        ang = math.pi / 2 + 0.7 * math.sin(T * (1.2 + 0.3 * i) + i * 1.7 + seed)
        x1, y1 = x0 + math.cos(ang) * 400, y0 + math.sin(ang) * 400
        tfill(img, 'line', [(x0, y0), (x1, y1)], cols[i % len(cols)], a, 2)


def flashes(img, d, T, n=6, seed=0, box=(0, 40, W, 200)):
    """相机闪光灯"""
    for i in range(n):
        r = rng(int(T * 5) * 17 + i + seed)
        if r.random() < 0.35:
            x, y = r.uniform(box[0], box[2]), r.uniform(box[1], box[3])
            glow(img, x, y, 22, (255, 255, 255), 0.6)
            twinkle(d, int(x), int(y), 0.5, (255, 255, 255), 5)


# ================================================================ 诶 Baggy new jeans
def s_jeans(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(30, 16, 50))
    for i in range(12):                                          # T 台两边的灯
        x = 20 + i * 40
        d.rectangle([x, 200, x + 4, 204], fill=K.YEL if (int(T * 8) + i) % 2 else (120, 100, 40))
    d.polygon([(170, 270), (310, 270), (270, 150), (210, 150)], fill=(60, 40, 80))
    tfill(img, 'polygon', [(200, 0), (280, 0), (330, 270), (150, 270)], (255, 230, 255), 0.12)
    flashes(img, d, T, 8, 3, (0, 30, W, 200))
    s = 6
    y = 268 + (2 if int(lt * 8) % 2 else 0)
    person(img, 'boy', 240, y, view='front', pose='walk', ph=wph(lt, 8), expr='cool', s=s)
    # 牛仔裤上的吊牌和闪光
    tx, ty = 268, 205
    d.line([(tx, ty), (tx + 8, ty + 10 + 2 * math.sin(T * 9))], fill=(255, 255, 255))
    d.rectangle([tx + 4, ty + 10 + 2 * math.sin(T * 9), tx + 30, ty + 22 + 2 * math.sin(T * 9)], fill=K.YEL, outline=pix.OUT)
    text(img, 'NEW', tx + 17, ty + 16 + 2 * math.sin(T * 9), col=(40, 20, 40), font=FONT_S, shadow=False)
    for j in range(5):
        sparkle(d, 200 + j * 20, 200 + (j * 13) % 50, T + j, (255, 255, 255), 3)
    K.neon(img, 'BAGGY', 90, 60, 2, K.CYAN, K.flicker(T, 1))
    K.neon(img, 'JEANS', 390, 60, 2, K.PINK, K.flicker(T, 2))
    vig(img, 0.35, (10, 4, 24))


# ================================================================ I got fellowness.
def s_crew(img, d, lt, dur, T, A):
    burst_bg(img, d, T, (120, 60, 200), (150, 90, 230), W / 2, 140, 18, 0.5)
    glow(img, W / 2, 140, 160, (255, 220, 255), 0.35)
    bump = lt > 0.7
    y = 236
    person(img, 'boy', 150, y, 'alt', view='front', expr='happy', arms='up' if bump else 'cross', s=3)
    person(img, 'boy', 330, y, 'alt2', view='front', expr='laugh', arms='up' if bump else 'cross', s=3)
    person(img, 'boy', 240, y - 6 * eback(clamp((lt - 0.7) / 0.2)) if bump else y, view='front', expr='cool', arms='up' if bump else 'cross', s=3)
    if bump:
        q = lt - 0.7
        twinkle(d, 240, 98, clamp(q / 0.4), (255, 255, 255), 10)
        K.heart_burst(img, d, q, 240, 100, 12, 90, K.YEL, 0.7)
        if q < 0.25: shake(img, q, 4, 0.25)
    K.neon(img, 'BROTHERS', 240, 30, 2, K.YEL, 1)
    vig(img, 0.3, (40, 10, 60))


# ================================================================ 有点怀念，但 I don't wanna 想到你
def club(img, d, T, crowd=True):
    d.rectangle([0, 0, W, H], fill=(16, 8, 30))
    lasers(img, d, T, 7, 0, a=0.3)
    d.rectangle([0, 210, W, H], fill=(30, 16, 50))
    for i in range(0, W, 30):
        for j in range(210, H, 15):
            c = [K.PINK, K.CYAN, K.PURP, K.YEL][(i // 30 + j // 15 + int(T * 4)) % 4]
            d.rectangle([i, j, i + 28, j + 13], fill=lerpc((30, 16, 50), c, 0.35))
    glow(img, 240, 20, 60, (255, 255, 255), 0.3)
    d.ellipse([228, 8, 252, 32], fill=(200, 200, 220))           # 迪斯科球
    for k in range(6): d.line([(228, 12 + k * 4), (252, 12 + k * 4)], fill=(120, 120, 150))
    if crowd:
        for i in range(10):
            r = rng(i)
            x = 20 + i * 48 + r.randrange(-8, 8)
            jump = abs(math.sin(T * 5 + i)) * 4
            person_s(img, 'boy' if i % 2 else 'girl', x, 214 - jump, 1.6, 'alt' if i % 3 else 'young', 'front', 'stand', 0,
                     'happy', 'up' if (int(T * 3) + i) % 2 else 'wave', shade=(0.35, 0.3, 0.5))


def s_party_think(img, d, lt, dur, T, A):
    club(img, d, T)
    swat = 2.0
    shake_head = swat - 0.6 < lt < swat + 0.4
    hx = 240 + (3 * math.sin(lt * 40) if shake_head else 0)
    person(img, 'boy', hx, 238, view='front', expr='closed' if shake_head else 'smile', arms='up' if lt > swat else 'auto', s=3)
    # 想她的气泡：慢慢鼓起来 → 被他一挥手打破 → 又冒出一个小的
    def thought(x, y, s, a):
        for k, (dx, dy, r) in enumerate(((-18, 40, 3), (-10, 28, 5))):
            d.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=(255, 255, 255))
        d.ellipse([x - 34 * s, y - 24 * s, x + 34 * s, y + 24 * s], fill=(255, 255, 255), outline=pix.OUT)
        hg = props.head_img('girl', expr='happy', s=2)
        if s > 0.6: img.paste(hg, (int(x - 16), int(y - 18)), hg)
    if lt < swat:
        s = eback(clamp((lt - 0.3) / 0.5))
        if s > 0: thought(300, 84, s, 1)
    elif lt < swat + 0.4:
        q = (lt - swat) / 0.4
        for j in range(14):
            a = j / 14 * 2 * math.pi
            d.rectangle([300 + math.cos(a) * 50 * q, 84 + math.sin(a) * 34 * q, 300 + math.cos(a) * 50 * q + 3, 84 + math.sin(a) * 34 * q + 3],
                        fill=(255, 255, 255))
        text(img, 'NO!', 160, 90, col=(255, 80, 120), scale=2)
    elif lt > swat + 1.2:
        s = 0.7 * eback(clamp((lt - swat - 1.2) / 0.4))
        thought(320, 90, s, 1)
        text(img, '...', 240, 110, col=(255, 255, 255))
    vig(img, 0.35, (6, 2, 16))


# ================================================================ 想到你，就好比压抑的黑夜，我遏制不住内心的冲动
def heavy_night(img, d, t):
    sky(img, ((0, (4, 4, 14)), (1, (24, 18, 44))), 0, H, 4)
    press = ease(clamp(t / 3.0))
    for i in range(7):                                             # 压下来的乌云
        x = i * 76 - 30 + 6 * math.sin(t + i)
        y = lerp(-40, 40, press) + (i % 2) * 14
        cloud(d, x, y, 3.0, (40, 36, 60), (28, 24, 44))
    if lerp(-40, 60, press) > 0: d.rectangle([0, 0, W, int(lerp(-40, 60, press))], fill=(28, 24, 44))
    d.rectangle([0, 230, W, H], fill=(10, 8, 20))
    person(img, 'boy', 240, 236, view='front', expr='sad' if t < 2.2 else 'surprised', arms='auto', s=3)
    # 胸口的心越跳越亮
    b = thump(T_of(t), 0.35)
    k = clamp(t / 3.0)
    glow(img, 240, 168, 30 + 50 * k + 20 * b, K.PINK, 0.3 + 0.4 * k)
    K.pix_heart(img, 240, 166, 0.35 + 0.15 * k + 0.1 * b)
    if t > 2.4:
        for i in range(3):
            M.lightning(d, 80 + i * 160 + 30 * math.sin(i), 20, 160, int(t * 6) + i, (255, 200, 240))


_T0 = [0.0]


def T_of(t): return _T0[0] + t


def run_night(img, d, t):
    off = t * 300
    K.night_city(img, d, T_of(t), off, 222)
    K.street_lines(d, 222, off * 1.5)
    M.streaks(img, d, T_of(t), (0, 60, W, 230), n=26, speed=700, col=(255, 200, 240), seed=2, dirx=-1)
    person(img, 'boy', 220, 238, view='side', pose='run', ph=wph(t, 12), expr='surprised', s=3)
    glow(img, 230, 170, 60, K.PINK, 0.4)
    for j in range(8):
        q = (t * 2 + j / 8) % 1
        pix.put(img, 'heart', 200 - q * 180, 160 + 10 * math.sin(j * 2 + t * 6), 1, alpha=1 - q)


def s_dark_night(img, d, lt, dur, T, A):
    _T0[0] = T - lt
    shots(img, lt, [(0, heavy_night), (3.3, run_night)], 0.2, 'white')
    if 3.3 <= lt < 3.6: shake(img, lt - 3.3, 5, 0.3)
    vig(img, 0.45, (4, 2, 12))


# ================================================================ Girl don't you say，拉住我的手
def s_hold_hand(img, d, lt, dur, T, A):
    sky(img, ((0, (255, 170, 210)), (0.6, (255, 210, 230)), (1, (255, 240, 240))), 0, H, 6)
    bokeh(img, T, 16, cols=[(255, 255, 255), K.PINK_L, (255, 230, 180)], a=0.35)
    d.rectangle([0, 240, W, H], fill=(240, 170, 200))
    meet = 1.0
    u = eout(clamp(lt / meet))
    bx, gx = lerp(150, 214, u), lerp(330, 266, u)
    person(img, 'boy', bx, 244, view='side', expr='smile' if lt < meet else 'happy', arms='reach', s=4)
    person(img, 'girl', gx, 244, view='side', flip=True, expr='shy' if lt < meet else 'happy', arms='reach', s=4)
    if lt > meet:
        q = lt - meet
        K.heart_burst(img, d, q, 240, 160, 14, 80, K.PINK, 0.9)
        glow(img, 240, 176, 40, (255, 255, 255), 0.5 * (1 - clamp(q / 0.6)))
        K.pix_heart(img, 240, 80 - 6 * math.sin(T * 4), 1.0 + 0.15 * thump(T, 0.3))
    vig(img, 0.25, (200, 80, 140))


# ================================================================ 曾经经历的一切，我希望你不懂：回忆胶片被锁起来
@lru_cache(None)
def memory_frame(i):
    im = Image.new('RGB', (64, 44))
    d = ImageDraw.Draw(im)
    kinds = [((255, 190, 140), (255, 230, 170)), ((60, 40, 100), (120, 80, 160)), ((150, 210, 255), (230, 250, 255)), ((40, 30, 60), (90, 50, 110)),
             ((255, 160, 200), (255, 220, 235))]
    a, b = kinds[i % 5]
    for y in range(44): d.line([(0, y), (64, y)], fill=lerpc(a, b, y / 44))
    d.rectangle([0, 34, 64, 44], fill=lerpc(a, (0, 0, 0), 0.4))
    sub = Image.new('RGBA', (64, 44))
    pix.person(sub, 'boy', 22, 38, view='side', expr='happy')
    pix.person(sub, 'girl', 42, 38, view='side', flip=True, expr='happy' if i % 2 else 'laugh')
    im.paste(sub, (0, 0), sub)
    if i % 2: pix.put(im, 'heart', 32, 8)
    else: moon(d, 52, 9, 4)
    return im


def s_memories(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(24, 16, 40))
    lock_at = 1.6
    gray = clamp((lt - lock_at) / 0.4)
    y0 = 70
    d.rectangle([0, y0, W, y0 + 76], fill=(20, 18, 24))
    off = (lt * 60) % 80
    for i in range(-1, 8):
        x = i * 80 - off + (0 if lt < lock_at else 0)
        for h in range(0, 80, 10):
            d.rectangle([x + h + 2, y0 + 4, x + h + 6, y0 + 8], fill=(220, 220, 220)); d.rectangle([x + h + 2, y0 + 68, x + h + 6, y0 + 72], fill=(220, 220, 220))
        im = memory_frame((i + int((lt * 60) // 80)) % 5)
        if gray > 0: im = props.sepia(im, gray, (0.8, 0.8, 0.85))
        img.paste(im, (int(x + 8), y0 + 16))
    # 锁链和大锁
    if lt > lock_at - 0.3:
        f = clamp((lt - lock_at + 0.3) / 0.3)
        ly = lerp(-60, 108, ein(f))
        if f >= 1:
            for x in range(0, W, 10): d.ellipse([x, 104, x + 12, 112], outline=(170, 170, 190), width=2)
        d.rounded_rectangle([212, ly - 34, 268, ly + 30], 8, fill=pix.OUT)
        d.arc([220, ly - 60, 260, ly - 10], 180, 360, fill=(180, 180, 200), width=6)
        d.rounded_rectangle([214, ly - 32, 266, ly + 28], 7, fill=(255, 200, 80))
        d.rectangle([214, ly - 6, 266, ly - 2], fill=(220, 160, 50))
        d.ellipse([235, ly + 2, 245, ly + 12], fill=(60, 40, 30)); d.rectangle([238, ly + 10, 242, ly + 20], fill=(60, 40, 30))
        if f >= 1 and lt - lock_at < 0.3:
            shake(img, lt - lock_at, 4, 0.3)
            text(img, '咔!', 300, 60, col=(255, 240, 160), scale=2)
    vig(img, 0.4, (6, 4, 16))


# ================================================================ 在一起的时间不算很多，不小心你闯进，不怕这次爱错
def calendar(img, d, t):
    d.rectangle([0, 0, W, H], fill=(60, 40, 100))
    for i in range(0, W, 20): d.line([(i, 0), (i, H)], fill=(66, 46, 108))
    page = int(t * 5) + 1
    cx, cy = 240, 128
    d.rectangle([cx - 70, cy - 80, cx + 70, cy + 80], fill=pix.OUT)
    d.rectangle([cx - 68, cy - 78, cx + 68, cy + 78], fill=(255, 255, 255))
    d.rectangle([cx - 68, cy - 78, cx + 68, cy - 46], fill=(255, 80, 120))
    text(img, '我们在一起', cx, cy - 62, col=(255, 255, 255), font=FONT_S)
    big = big_glyph(str(min(page, 7)), 5, top=(80, 70, 100), bot=(40, 30, 60), line=(40, 30, 60), out=(255, 255, 255))
    img.paste(big, (int(cx - big.width / 2), int(cy - 40)), big)
    text(img, '第     天', cx, cy + 62, col=(80, 70, 100), font=FONT_S, shadow=False)
    q = (t * 5) % 1                                              # 翻走的那一页
    if page < 8:
        h = 156 * (1 - q)
        d.rectangle([cx - 68, cy - 78, cx + 68, cy - 78 + h * 0.2], fill=(240, 236, 246))
    for k in range(2): d.rectangle([cx - 40 + k * 70, cy - 86, cx - 30 + k * 70, cy - 72], fill=(120, 120, 140), outline=pix.OUT)


def burst_door(img, d, t):
    K.room(img, d, 0, 1.0, (70, 46, 100), window=False)
    dx = 300
    open_ = eout(clamp(t / 0.25))
    d.rectangle([dx - 2, 70, dx + 72, 200], fill=(40, 26, 30))
    glow(img, dx + 35, 135, 80, (255, 220, 240), 0.6 * open_)
    d.rectangle([dx, 72, dx + 70, 200], fill=(255, 240, 250) if open_ > 0 else (140, 90, 60))
    w = int(70 * (1 - open_))
    if w > 2:
        d.rectangle([dx, 72, dx + w, 200], fill=(140, 90, 60)); d.ellipse([dx + w - 10, 136, dx + w - 5, 141], fill=(255, 210, 80))
    else:
        d.polygon([(dx, 72), (dx - 20, 62), (dx - 20, 210), (dx, 200)], fill=(140, 90, 60))
    if t > 0.15:
        q = t - 0.15
        gx = lerp(dx + 35, 250, eout(clamp(q / 0.5)))
        gy = 210 - 30 * math.sin(clamp(q / 0.5) * math.pi)
        person(img, 'girl', gx, gy, view='side', flip=True, pose='jump' if q < 0.5 else 'stand', expr='laugh', arms='up', s=3)
    person(img, 'boy', 120, 214, view='side', expr='surprised' if t < 0.8 else 'happy', s=3)
    if t < 0.3: shake(img, t, 5, 0.3)
    for j in range(8):
        r = rng(j); q = (t * 0.8 + r.random()) % 1
        pix.put(img, 'heart', dx + 35 + (r.random() - 0.5) * 120, 200 - q * 160, 1, alpha=1 - q)


def no_fear(img, d, t):
    burst_bg(img, d, t, (255, 120, 170), (255, 150, 190), W / 2, 120, 20, 0.3)
    b = thump(T_of(t), 0.3)
    K.pix_heart(img, 240, 112, 3.4 + 0.3 * b)
    person(img, 'boy', 214, 236, view='side', arms='hug', expr='happy', s=3)
    person(img, 'girl', 262, 236, view='side', flip=True, arms='hug', expr='laugh', s=3)
    # “爱错？” 被划掉，换成 “不怕！”
    if t < 0.9:
        K.neon(img, '爱错?', 240, 50, 2, (255, 255, 255), 1)
        if t > 0.45:
            f = clamp((t - 0.45) / 0.25)
            d.line([(196, 50), (lerp(196, 286, f), 50)], fill=(255, 40, 80), width=4)
    else:
        q = t - 0.9
        sc = 3 if q > 0.15 else 4
        K.neon(img, '不怕!', 240, 46, sc, (255, 255, 120), 1)
        if q < 0.3: shake(img, q, 4, 0.3)
    petals(d, t, 30, [(255, 255, 255), K.PINK_L], 30, 20)


def s_burst_in(img, d, lt, dur, T, A):
    _T0[0] = T - lt
    shots(img, lt, [(0, calendar), (1.75, burst_door), (3.5, no_fear)], 0.2)
    vig(img, 0.25, (40, 10, 40))


# ================================================================ Baby I found 你写的信
def s_letter_found(img, d, lt, dur, T, A):
    K.room(img, d, T, 1.0, (54, 36, 84))
    darken(img, 0.3, (10, 6, 24))
    # 打开的抽屉
    d.rectangle([60, 150, 200, 214], fill=(120, 80, 54), outline=pix.OUT)
    d.rectangle([66, 140, 194, 156], fill=(150, 100, 64), outline=pix.OUT)
    person(img, 'boy', 330, 226, view='side', flip=True, expr='surprised', arms='reach', s=3)
    f = eout(clamp((lt - 0.3) / 0.8))
    ex, ey = lerp(130, 220, f), lerp(150, 92, f)
    for k in range(12):                                          # 光芒
        a = k / 12 * 2 * math.pi + T * 0.6
        tfill(img, 'polygon', [(ex, ey), (ex + math.cos(a) * 120, ey + math.sin(a) * 120), (ex + math.cos(a + 0.15) * 120, ey + math.sin(a + 0.15) * 120)],
              (255, 230, 170), 0.12 * f)
    glow(img, ex, ey, 60, (255, 220, 160), 0.5 * f)
    K.envelope(img, d, ex, ey, 54 + 20 * f, 36 + 12 * f, clamp((lt - 1.2) / 0.5))
    for j in range(6): twinkle(d, int(ex - 50 + j * 20), int(ey - 40 + (j % 2) * 70), (T * 1.5 + j * 0.3) % 1, (255, 250, 200))
    vig(img, 0.45, (6, 4, 16))


# ================================================================ Can't see 你留给我的烙印
def s_brand(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(28, 18, 44))
    bokeh(img, T, 10, cols=[K.PINK, (255, 200, 120)], a=0.25)
    props.bust(img, d, 'boy', 300, 40, 4, 'sad' if lt < 1.2 else 'closed', T=T)
    # 胸口烙下的心：烧得发红、冒烟
    hx, hy = 300, 196
    b = thump(T, 0.4)
    glow(img, hx, hy, 40 + 10 * b, (255, 80, 60), 0.5)
    for s, c in ((1.3, (120, 20, 30)), (1.05, (255, 90, 60)), (0.75, (255, 200, 120))):
        d.polygon(pix.heart_poly(hx, hy, s * (1 + 0.05 * b)), fill=c)
    d.polygon(pix.heart_poly(hx, hy, 0.48), fill=(150, 30, 40))
    props.smoke(img, hx, hy - 10, T, n=6, vx=0, vy=-30, r0=2, r1=10, a=0.7)
    # 左边那封信：字是糊的，看不清
    K.letter(d, 40, 60, 110, 150, 9, f=1.0, seed=3)
    blur = Image.fromarray(np.asarray(img.crop((40, 60, 151, 211)))).resize((28, 38), Image.BOX).resize((111, 151), Image.NEAREST)
    img.paste(blur, (40, 60))
    text(img, '?', 95, 135, col=(255, 120, 160), scale=3)
    vig(img, 0.4, (6, 4, 16))


# ================================================================ 可惜你忘记我的声音
def s_voice(img, d, lt, dur, T, A):
    sky(img, ((0, (40, 30, 70)), (1, (90, 60, 120))), 0, 220, 5)
    pix.city(img, d, 220, 33, T * 3, (60, 40, 90), (200, 170, 255), 30, 100, 0.2, T)
    d.rectangle([0, 220, W, H], fill=(36, 26, 54))
    K.mic(d, 120, 140, 1.2, base=232)
    person(img, 'boy', 96, 232, view='side', expr='laugh', arms='reach', s=3)
    gx = lerp(360, 470, clamp(lt / 3.0))
    person(img, 'girl', gx, 232, view='back', pose='walk', ph=wph(lt, 5), expr='neutral', s=3)
    # 她戴着耳机
    d.arc([gx - 14, 112, gx + 12, 138], 180, 360, fill=(40, 40, 60), width=3)
    d.rectangle([gx - 16, 124, gx - 11, 134], fill=(255, 120, 180)); d.rectangle([gx + 9, 124, gx + 14, 134], fill=(255, 120, 180))
    # 声波一圈圈飞过去，越飞越灰，到她身后就散了
    for j in range(8):
        q = (lt * 0.9 + j / 8) % 1
        x = lerp(140, gx - 20, q)
        r = 10 + q * 40
        c = lerpc(K.CYAN, (90, 80, 110), q)
        if q < 0.92:
            d.arc([x - r * 0.4, 140 - r, x + r * 0.4, 140 + r], 300, 60, fill=c, width=2)
        if j % 2 == 0: K.note(img, x, 140 - r * 0.6, j, c)
    if lt > 1.6: text(img, '...', gx, 98, col=(200, 200, 220))
    vig(img, 0.35, (10, 6, 20))
