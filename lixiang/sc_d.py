"""理想三旬 · 第二段副歌、间奏、最后一段和片尾。签名都是 (img, d, lt, dur, T, A)。

海边的门廊上，老了的他坐在摇椅里，小黑猫在他腿上睡着；河边放走一只点着蜡烛的纸船；一个人坐在转不停的旋转木马上；
广场上弹琴唱歌，围过来的人举起手机的光，光点飘上天变成星星；雨夜的水洼里他的倒影被一滴眼泪打碎；
铁轨在海边断掉，他走到尽头，朝着日出伸出手。间奏是一卷旧胶片和散落一桌的照片，然后他和猫走回亮着灯的小屋。
最后是小屋里的热茶、窗台上的星星、跳动的烛光、合上的本子和清晨的第一缕光；那列旧铁皮火车停在原野里，慢慢爬满青苔，片名重新出现。
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
from sc_a import mountains, pole, wire, bez, title_block
from sc_b import guitar_lap

YY, XX = np.mgrid[0:H, 0:W]


def waves(d, T, y0, y1, col, col2, speed=12):
    for j in range(int((y1 - y0) / 6)):
        y = y0 + 3 + j * 6
        for k in range(8):
            x = (k * 70 + j * 23 + T * speed * (1 + j * 0.2)) % (W + 40) - 20
            d.line([(x, y), (x + 14 + j * 2, y)], fill=col if (j + k) % 2 else col2)


# ================================================================ 海边门廊的摇椅
def s_porch(img, d, lt, dur, T, A):
    f = lt / dur
    sky(img, mix_stops(GOLDEN, NIGHT, ease(f)), 0, 160, 6)
    stars(d, T, 160, ease(clamp((f - 0.4) * 2)), 200)
    sy = 150 + f * 40
    glow(img, 120, sy, 120, (255, 200, 140), 0.5 * (1 - f), 50)
    if sy < 168: d.ellipse([100, sy - 20, 140, sy + 20], fill=(255, 236, 190))
    sea = lerpc((200, 130, 120), (20, 26, 60), ease(f))
    d.rectangle([0, 160, W, 206], fill=sea)
    waves(d, T, 160, 206, lerpc(sea, (255, 230, 200), 0.3), lerpc(sea, (0, 0, 0), 0.2))
    if f < 0.8:
        for j in range(6): d.line([(110 - j * 3, 164 + j * 6), (130 + j * 3, 164 + j * 6)], fill=lerpc((255, 220, 170), sea, f + j * 0.1))
    # 灯塔：天黑以后光束扫过来
    lx = 420
    d.polygon([(lx - 6, 160), (lx + 6, 160), (lx + 3, 118), (lx - 3, 118)], fill=(230, 226, 220))
    d.rectangle([lx - 4, 112, lx + 4, 118], fill=(60, 50, 60))
    dark = clamp((f - 0.35) * 2)
    if dark > 0:
        a = T * 1.6
        bx, by = lx + math.cos(a) * 400, 115 + math.sin(a) * 40
        tfill(img, 'polygon', [(lx, 113), (bx, by - 20), (bx, by + 20)], (255, 240, 190), 0.18 * dark)
        glow(img, lx, 115, 20, (255, 240, 190), 0.8 * dark)
    # 门廊
    wood = lerpc((150, 100, 70), (60, 46, 56), ease(f))
    d.rectangle([0, 0, W, 16], fill=lerpc(wood, (0, 0, 0), 0.3))
    for x in (30, 450): d.rectangle([x, 16, x + 8, 206], fill=lerpc(wood, (0, 0, 0), 0.2))
    d.rectangle([0, 206, W, H], fill=wood)
    for x in range(0, W, 24): d.line([(x, 206), (x - 10, H)], fill=lerpc(wood, (0, 0, 0), 0.25))
    # 风铃
    sw = math.sin(T * 2) * 3
    d.line([(240, 16), (240 + sw, 30)], fill=(200, 190, 170))
    for k in range(3): d.line([(236 + k * 4 + sw, 30), (236 + k * 4 + sw * 1.4, 40 + k * 2)], fill=(220, 210, 180))
    # 摇椅、老了的他、腿上睡着的猫
    rock = math.sin(T * 1.8) * 3
    cx, base = 250 + rock, 246
    d.arc([cx - 40, base - 16, cx + 40, base + 8], 20, 160, fill=(80, 54, 40), width=3)
    d.rectangle([cx - 26, base - 34, cx + 14, base - 30], fill=(110, 74, 52))
    d.line([(cx - 26, base - 32), (cx - 34, base - 92)], fill=(110, 74, 52), width=4)
    for k in range(3): d.line([(cx - 28 - k * 2, base - 44 - k * 14), (cx - 22 - k * 2, base - 44 - k * 14)], fill=(130, 90, 64), width=2)
    d.line([(cx - 20, base - 30), (cx - 24, base - 4)], fill=(110, 74, 52), width=3); d.line([(cx + 10, base - 30), (cx + 14, base - 4)], fill=(110, 74, 52), width=3)
    shade = (1 - 0.35 * f, 1 - 0.35 * f, 1 - 0.2 * f)
    pix.person(img, 'boy', cx - 8, base - 3, age='old', view='side', pose='sit', s=3, expr='closed', shade=shade)
    cat(img, cx + 6, base - 30, 'sleep', 2, rim=(150, 120, 120), T=T)
    vig(img, 0.35, (20, 10, 30))


# ================================================================ 放走的纸船
def s_boat(img, d, lt, dur, T, A):
    sky(img, NIGHT, 0, 150, 5)
    stars(d, T, 150, 1, 180)
    moon(d, 380, 40, 12)
    city(img, d, 150, 91, 0, (30, 26, 60), (255, 200, 120), 20, 70, frac=0.4, T=T)
    d.rectangle([0, 150, W, H], fill=(14, 16, 40))
    # 纸船：船上点着一根小蜡烛，慢慢漂向对岸的灯火
    u = ease(clamp((lt - 0.4) / (dur - 0.4)))
    bxp, byp = lerp(170, 380, u), lerp(232, 168, u)
    s = 2 if u < 0.5 else 1
    bob = math.sin(T * 3) * 1.5
    glow(img, bxp, byp - 10 * s, 26 * s, (255, 200, 110), 0.5)
    paper_boat(d, bxp, byp, s, bob=bob)
    d.rectangle([bxp - 1, byp - 7 * s + bob - 4, bxp, byp - 4 * s + bob], fill=(250, 246, 230))
    fl = 1 + int(T * 12) % 2
    d.rectangle([bxp - 1, byp - 7 * s + bob - 4 - fl * s, bxp, byp - 7 * s + bob - 4], fill=(255, 200, 80))
    props.reflect(img, 150, 120, T, (14, 16, 40), 0.55, 2.0, 100)
    props.ripples(d, T, (0, 160, W, 268), 12, (70, 80, 130), per=1.8, rmax=12)
    d.ellipse([bxp - 14 * s, byp - 2, bxp + 14 * s, byp + 4], outline=(90, 100, 150))
    # 码头和他
    d.rectangle([0, 214, 150, 226], fill=(90, 66, 56)); d.rectangle([0, 226, 150, 230], fill=(60, 44, 40))
    for x in (20, 70, 120): d.rectangle([x, 226, x + 5, H], fill=(60, 44, 40))
    for x in range(0, 150, 16): d.line([(x, 214), (x, 226)], fill=(70, 50, 44))
    pix.person(img, 'boy', 120, 214, view='side', s=2, arms='reach' if lt < 1.2 else 'down', shade=(0.8, 0.8, 0.95))
    cat(img, 92, 214, 'sit', 2, rim=(110, 100, 140), T=T)
    vig(img, 0.4, (6, 6, 20))


# ================================================================ 转不停的旋转木马
def horse(d, x, y, s, col, mane, flip=False):
    k = -1 if flip else 1
    d.ellipse([x - 10 * s, y - 6 * s, x + 10 * s, y + 6 * s], fill=col)
    d.polygon([(x + k * 6 * s, y - 4 * s), (x + k * 12 * s, y - 16 * s), (x + k * 18 * s, y - 14 * s), (x + k * 12 * s, y - 2 * s)], fill=col)
    d.rectangle([min(x + k * 14 * s, x + k * 20 * s), y - 16 * s, max(x + k * 14 * s, x + k * 20 * s), y - 11 * s], fill=col)
    d.line([(x + k * 8 * s, y - 6 * s), (x + k * 12 * s, y - 16 * s)], fill=mane, width=max(1, int(2 * s)))
    for lx in (-6, -2, 4, 8):
        d.line([(x + k * lx * s, y + 4 * s), (x + k * (lx + (2 if lx > 0 else -2)) * s, y + 13 * s)], fill=col, width=max(1, int(2 * s)))
    d.line([(x - k * 10 * s, y - 2 * s), (x - k * 15 * s, y + 6 * s)], fill=mane, width=max(1, int(2 * s)))
    d.point((x + k * 16 * s, y - 14 * s), fill=OUT)


def s_carousel(img, d, lt, dur, T, A):
    sky(img, ((0, (12, 10, 30)), (1, (60, 30, 70))), 0, H, 5)
    stars(d, T, 140, 1, 120)
    props.bokeh(img, T, 10, seed=7, a=0.25)
    cx, ry, rx = 240, 186, 150
    d.rectangle([0, 214, W, H], fill=(30, 22, 40))
    # 底座和顶棚
    d.ellipse([cx - rx - 10, ry - 12, cx + rx + 10, ry + 28], fill=(120, 60, 70))
    d.ellipse([cx - rx - 10, ry - 16, cx + rx + 10, ry + 22], fill=(200, 160, 120))
    roof_y = 40
    segs = 12
    rot = T * 0.9
    for i in range(segs):
        a0 = rot + i * 2 * math.pi / segs; a1 = a0 + 2 * math.pi / segs
        if math.sin((a0 + a1) / 2) < -0.1: continue
        p0 = (cx + math.cos(a0) * (rx + 20), roof_y + 40 + math.sin(a0) * 10)
        p1 = (cx + math.cos(a1) * (rx + 20), roof_y + 40 + math.sin(a1) * 10)
        d.polygon([(cx, roof_y - 20), p0, p1], fill=(230, 70, 80) if i % 2 else (250, 240, 230))
    d.rectangle([cx - 2, roof_y - 34, cx + 2, roof_y - 20], fill=(255, 210, 90))
    d.ellipse([cx - 5, roof_y - 40, cx + 5, roof_y - 30], fill=(255, 220, 110))
    # 顶棚边上一圈闪的灯泡
    for i in range(24):
        a = rot + i * 2 * math.pi / 24
        x, y = cx + math.cos(a) * (rx + 20), roof_y + 40 + math.sin(a) * 10
        if math.sin(a) < -0.2: continue
        on = (i + int(T * 6)) % 2 == 0
        c = (255, 230, 140) if on else (150, 110, 80)
        d.rectangle([x - 1, y, x + 1, y + 2], fill=c)
        if on: glow(img, x, y + 1, 6, (255, 220, 140), 0.4)
    d.rectangle([cx - 4, roof_y + 40, cx + 4, ry], fill=(220, 190, 110))
    # 木马：后半圈先画，前半圈后画；他坐在其中一匹上
    horses = []
    for i in range(6):
        a = -rot * 1.0 + i * 2 * math.pi / 6
        x = cx + math.cos(a) * rx; depth = math.sin(a)
        y = ry - 30 + depth * 10 + math.sin(T * 4 + i) * 5
        horses.append((depth, x, y, i, a))
    for depth, x, y, i, a in sorted(horses):
        flip = math.sin(a) < 0
        s = 1.0 + 0.3 * (depth + 1) / 2
        d.line([(x, roof_y + 42 + depth * 10), (x, y + 14 * s)], fill=(230, 210, 150))
        col = [(250, 246, 240), (240, 200, 210), (200, 220, 250)][i % 3]
        if depth < 0: col = lerpc(col, (60, 40, 70), 0.4)
        horse(d, x, y, s, col, (220, 120, 70), flip=not flip)
        if i == 0:
            pix.person(img, 'boy', x - 2, y + 4, view='side', pose='sit', s=1 if depth < 0 else 2, flip=flip,
                       shade=(0.7, 0.7, 0.8) if depth < 0 else None)
    vig(img, 0.4, (10, 6, 20))


# ================================================================ 广场上弹唱，手机的光飘上天
def s_busk(img, d, lt, dur, T, A):
    sky(img, NIGHT, 0, 170, 5)
    stars(d, T, 170, 1, 220)
    city(img, d, 170, 101, 0, (36, 30, 66), (255, 210, 140), 40, 110, frac=0.3, T=T)
    d.rectangle([0, 170, W, H], fill=(64, 58, 82))
    for x in range(-40, W + 40, 40): d.line([(x, 170), (x + (x - 240) * 0.6, H)], fill=(74, 68, 92))
    pix.lamp(img, d, 316, 228, 1.0, 96)
    glow(img, 240, 200, 120, (255, 220, 160), 0.25, 50)
    # 他站在路灯下弹琴唱歌
    on = pix.pulse(T, 0.35) > 0.2
    x, y = 240, 228
    pix.person(img, 'boy', x, y, view='front', s=3, expr='laugh' if on else 'happy', arms='flowers')
    d.ellipse([x - 16, y - 38, x + 8, y - 22], fill=OUT); d.ellipse([x - 15, y - 37, x + 7, y - 23], fill=(214, 146, 78))
    d.ellipse([x - 7, y - 33, x - 1, y - 27], fill=(60, 36, 24))
    d.line([(x + 4, y - 32), (x + 34, y - 50)], fill=(110, 70, 46), width=3)
    d.rectangle([x + 32, y - 55, x + 38, y - 49], fill=(80, 50, 36))
    # 打开的琴盒和硬币
    d.rectangle([150, 232, 196, 242], fill=(60, 30, 40)); d.rectangle([153, 234, 193, 240], fill=(160, 40, 60))
    for k in range(int(lt * 2)):
        d.point((158 + (k * 7) % 32, 236 + k % 3), fill=(255, 220, 100))
    notes(img, d, T, 8, (170, 60, 330, 190), seed=21, speed=22)
    # 围过来的人，一个个变多；最后一起举起手机的光
    lift = beat_after(T - lt + 3.6) - (T - lt)
    n = min(14, 3 + int(lt * 2.4))
    for j in range(n):
        r = rng(j * 11)
        px = 40 + (j * 61) % 400 + r.uniform(-8, 8)
        if abs(px - 240) < 40: px += 80
        py = 262 + (j % 3) * 4
        props.person_s(img, ['boy', 'girl'][j % 2], px, py + 30, 3, view='back', tint=(28, 24, 44))
        k = lt - lift - j * 0.03
        if k > 0:
            hx, hy = px + 8, py - 70
            if k < 1.2:
                d.rectangle([px + 6, hy + 3, px + 9, py - 40], fill=(28, 24, 44))
                d.rectangle([hx - 2, hy - 3, hx + 2, hy + 3], fill=(240, 250, 255))
                glow(img, hx, hy, 10, (220, 240, 255), 0.5)
            else:
                u = k - 1.2
                fx = hx + math.sin(u * 2 + j) * 10; fy = hy - u * 60
                glow(img, fx, fy, 6, (255, 240, 200), 0.5)
                d.point((fx, fy), fill=(255, 255, 240))
    vig(img, 0.35, (8, 6, 20))


# ================================================================ 雨夜的水洼：倒影被一滴眼泪打碎
def s_puddle(img, d, lt, dur, T, A):
    hit = beat_after(T - lt + 1.2) - (T - lt)
    k = lt - hit
    img.paste((26, 24, 36), (0, 0, W, H))
    for j in range(140):                                     # 湿地面的碎石
        r = rng(j)
        d.point((r.uniform(0, W), r.uniform(0, H)), fill=(46, 44, 60))
    # 水洼里的倒影：夜空、路灯、他的脸（上下颠倒）
    ref = Image.new('RGB', (W, H)); rd = ImageDraw.Draw(ref)
    sky(ref, NIGHT, 0, H, 5)
    stars(rd, T, H, 1, 160)
    glow(ref, 360, 60, 60, (255, 220, 150), 0.6)
    rd.rectangle([358, 0, 362, 60], fill=(40, 36, 60))
    bust(ref, rd, 'boy', 220, 40, 4, 'sad')
    ref = ref.transpose(Image.FLIP_TOP_BOTTOM)
    a = np.asarray(ref).copy()
    amp_ = 1.0 + (0 if k < 0 else 10 * math.exp(-k * 1.2))
    for y in range(H):
        sh = int(round(amp_ * math.sin(y * 0.3 + T * 6) + (0 if k < 0 else 8 * math.exp(-k) * math.sin(y * 0.08 - k * 14))))
        if sh: a[y] = np.roll(a[y], sh, axis=0)
    if k > 0:                                                # 碎成一条条
        for y in range(0, H, 8):
            if (y // 8) % 2: a[y:y + 8] = np.roll(a[y:y + 8], int(18 * math.exp(-k * 0.8) * math.sin(y)), axis=1)
    a = np.clip(a * np.array([0.62, 0.72, 0.95]) + np.array([0, 4, 18]), 0, 255).astype(np.uint8)
    pud = ((XX - 240) / 210) ** 2 + ((YY - 140) / 112) ** 2 < 1
    out = np.asarray(img).copy(); out[pud] = a[pud]
    img.paste(Image.fromarray(out))
    d.ellipse([30, 28, 450, 252], outline=(70, 70, 96))
    props.ripples(d, T, (60, 60, 420, 220), 22, (120, 130, 180), per=0.9, rmax=10)
    # 眼泪落进水洼
    if k < 0:
        y = lerp(-20, 150, ein(clamp(lt / max(0.1, hit))))
        d.ellipse([236, y - 6, 244, y + 4], fill=(170, 210, 255)); d.polygon([(237, y - 4), (240, y - 12), (243, y - 4)], fill=(170, 210, 255))
    else:
        for j in range(3):
            rr = (k * 120 - j * 30)
            if rr > 0: d.ellipse([240 - rr, 150 - rr * 0.45, 240 + rr, 150 + rr * 0.45], outline=lerpc((220, 235, 255), (40, 40, 70), clamp(rr / 220)))
        if k < 0.4:
            for j in range(10):
                aa = j * 0.6
                d.point((240 + math.cos(aa) * k * 60, 150 - abs(math.sin(aa)) * k * 80 + k * k * 200), fill=(200, 220, 255))
    rain(d, T, 0, W + 40, -10, H, 120, (140, 150, 190), 300, -3, 7)
    vig(img, 0.45, (6, 6, 14))


# ================================================================ 铁轨在海边断掉
def s_endtrack(img, d, lt, dur, T, A):
    f = lt / dur
    sky(img, DAWN, 0, 170, 6)
    sy = 176 - f * 30
    glow(img, 420, sy, 170, (255, 210, 160), 0.6, 80)
    d.ellipse([396, sy - 24, 444, sy + 24], fill=(255, 240, 200))
    d.rectangle([0, 170, W, H], fill=(70, 70, 120))
    waves(d, T, 170, H, (110, 100, 150), (90, 90, 140), 8)
    for j in range(8): d.line([(400 - j * 6, 176 + j * 10), (440 + j * 6, 176 + j * 10)], fill=(255, 210, 170))
    # 栈桥一样的路基伸进海里，铁轨在尽头断掉
    d.polygon([(0, 206), (330, 206), (336, 216), (0, 216)], fill=(110, 90, 84))
    for x in range(10, 330, 30): d.rectangle([x, 216, x + 6, H], fill=(70, 56, 56))
    props.rails(d, 204, 0, (90, 80, 90), (110, 86, 70), x1=326)
    d.rectangle([320, 192, 330, 204], fill=(200, 60, 60)); d.rectangle([318, 190, 332, 194], fill=(240, 236, 226))
    train(img, d, 120, 204, T, cars=1, lit=0.2, seed=4, roll=0)
    props.smoke(img, 90, 152, T, n=6, col=(250, 236, 236), shade=None, vx=-10, vy=-14, life=2.6, r1=12, seed=9, a=0.6)
    # 他从车上下来，走到铁轨的尽头
    wk = clamp((lt - 0.3) / 2.6)
    px = lerp(150, 300, ease(wk))
    pix.person(img, 'boy', px, 204, view='side', pose='walk' if 0 < wk < 1 else 'stand', ph=wph(T), s=2)
    cat(img, px - 26, 204, 'walk' if 0 < wk < 1 else 'sit', 2, T=T)
    for j in range(4): pix.bird(d, (j * 90 + T * 20) % W, 60 + j * 12 + math.sin(T + j) * 4, T, (90, 70, 100), j)
    vig(img, 0.3, (40, 20, 50))


def s_exist(img, d, lt, dur, T, A):
    sky(img, DAWN, 0, 200, 6)
    glow(img, 330, 170, 260, (255, 220, 170), 0.7, 140)
    d.ellipse([280, 120, 380, 220], fill=(255, 244, 214))
    d.rectangle([0, 200, W, H], fill=(60, 50, 90))
    for j in range(5): d.line([(300 - j * 10, 206 + j * 8), (360 + j * 10, 206 + j * 8)], fill=(255, 210, 170))
    pix.person(img, 'boy', 180, 262, view='side', s=4, arms='reach', tint=(34, 24, 44))
    for j, (k, r) in enumerate([(0.3, 8), (0.55, 4), (0.8, 12)]):
        x = lerp(330, 120, k); y = lerp(170, 60, k)
        glow(img, x, y, r * 2, (255, 230, 200), 0.3)
    twinkle(d, 330, 170, (lt / dur), (255, 255, 240), 10)
    vig(img, 0.25, (60, 30, 50))


# ================================================================ 间奏：一卷旧胶片
FILM_T = [2.6, 8.5, 12.5, 21.0, 26.0, 33.0, 41.0, 50.0, 60.0, 64.0, 76.0, 88.0, 93.0, 103.0, 109.0, 122.0, 132.5, 138.0, 147.0, 152.0]


@lru_cache(None)
def film_frame(t):
    return sepia(shrink(props.SNAP(t), 160, 90), 0.45)


def s_film(img, d, lt, dur, T, A):
    img.paste((16, 12, 18), (0, 0, W, H))
    tfill(img, 'polygon', [(0, 0), (60, 0), (W, 120), (W, 200)], (255, 230, 180), 0.08)
    sy0, sy1 = 66, 196
    jit = 1 if int(T * 24) % 5 == 0 else 0
    d.rectangle([0, sy0 + jit, W, sy1 + jit], fill=(30, 22, 20))
    off = 40 + lt * 110
    fw = 176
    for x in range(int(-(off % 16)), W, 16):
        d.rectangle([x + 4, sy0 + 5 + jit, x + 11, sy0 + 11 + jit], fill=(230, 220, 200))
        d.rectangle([x + 4, sy1 - 11 + jit, x + 11, sy1 - 5 + jit], fill=(230, 220, 200))
    n0 = int(off // fw)
    for j in range(n0 - 1, n0 + 5):
        x = j * fw - off
        if x > W or x + fw < 0: continue
        fr = film_frame(FILM_T[j % len(FILM_T)])
        fl = 0.85 + 0.15 * math.sin(T * 40 + j)
        fr = Image.fromarray((np.asarray(fr) * fl).astype(np.uint8))
        img.paste(fr, (int(x + 8), sy0 + 20 + jit))
        d.rectangle([x + 7, sy0 + 19 + jit, x + 168, sy0 + 110 + jit], outline=(60, 46, 40))
    for j in range(40):
        r = rng(j + int(T * 10))
        d.point((r.uniform(0, W), r.uniform(0, H)), fill=(200, 190, 170))
    for j in range(2):
        r = rng(int(T * 8) + j * 31)
        x = r.uniform(0, W); d.line([(x, sy0), (x + r.uniform(-3, 3), sy1)], fill=(180, 170, 150))
    grain(img, T, 8)
    vig(img, 0.55, (4, 2, 6))


# ================================================================ 间奏：散落一桌的照片
PHOTO_T = [(8.5, -8), (26.0, 6), (64.0, -4), (103.0, 9), (122.0, -6), (138.0, 4)]


@lru_cache(None)
def photo_img(t):
    return shrink(props.SNAP(t), 112, 63)


def s_photos(img, d, lt, dur, T, A):
    img.paste(WOOD, (0, 0, W, H))
    for y in range(0, H, 14): d.line([(0, y + math.sin(y) * 2), (W, y)], fill=WOOD_D)
    glow(img, 240, 120, 260, (255, 220, 160), 0.3)
    drops = [0.2 + j * 0.7 for j in range(len(PHOTO_T))]
    spots = [(120, 90), (360, 80), (240, 130), (110, 190), (370, 190), (250, 210)]
    for j, ((t, rot), (x, y)) in enumerate(zip(PHOTO_T, spots)):
        k = lt - drops[j]
        if k < 0: continue
        sc = 1 + 0.4 * (1 - eout(k / 0.3)) if k < 0.3 else 1
        yy = y - (1 - eout(k / 0.3)) * 30
        ph = photo_img(t)
        if sc != 1: ph = ph.resize((int(112 * sc), int(63 * sc)), Image.NEAREST)
        d.rectangle([x - 58, yy - 36, x + 64, yy + 50], fill=(60, 36, 26))
        polaroid(img, d, x, yy, ph, f=clamp(k / 1.2), rot=rot)
    vig(img, 0.45, (30, 14, 10))


# ================================================================ 间奏：走回亮着灯的小屋
def cottage(img, d, x, base, T, door=0.0, lit=1.0):
    d.rectangle([x - 50, base - 60, x + 50, base], fill=(200, 170, 140))
    d.polygon([(x - 62, base - 58), (x, base - 104), (x + 62, base - 58)], fill=(140, 60, 60))
    d.rectangle([x + 22, base - 98, x + 32, base - 74], fill=(110, 80, 70))
    props.smoke(img, x + 27, base - 100, T, n=5, col=(170, 170, 200), shade=None, vx=-8, vy=-12, life=2.6, r1=8, seed=12, a=0.7)
    wc = lerpc((40, 40, 70), (255, 210, 130), lit)
    d.rectangle([x - 40, base - 46, x - 14, base - 22], fill=wc)
    d.line([(x - 27, base - 46), (x - 27, base - 22)], fill=(110, 80, 60)); d.line([(x - 40, base - 34), (x - 14, base - 34)], fill=(110, 80, 60))
    glow(img, x - 27, base - 34, 40, (255, 200, 120), 0.4 * lit)
    d.rectangle([x + 6, base - 44, x + 30, base], fill=(255, 220, 150) if door > 0 else (110, 70, 50))
    if door > 0:
        dw = int(24 * (1 - door))
        d.rectangle([x + 6, base - 44, x + 6 + dw, base], fill=(110, 70, 50))
        tfill(img, 'polygon', [(x + 6, base), (x + 30, base), (x + 60, base + 30), (x - 10, base + 30)], (255, 220, 150), 0.3 * door)
        glow(img, x + 18, base - 22, 50, (255, 210, 140), 0.4 * door)


def s_walkhome(img, d, lt, dur, T, A):
    stop = dur - 2.6
    u = clamp(lt / stop)
    off = 480 * (1 - (1 - u) ** 2) * stop / 2.2
    sky(img, NIGHT, 0, 200, 5)
    stars(d, T, 200, 1, 220)
    moon(d, 90, 50, 14)
    mountains(d, 190, 26, 0.012, 1.0, (30, 28, 60), off * 0.1)
    # 小镇的房子往后退
    for j in range(7):
        x = (j * 130 + 60 - off * 0.6) % (W + 260) - 130
        h = 50 + (j * 37) % 30
        d.rectangle([x, 220 - h, x + 80, 220], fill=(40, 36, 66))
        d.polygon([(x - 6, 222 - h), (x + 40, 194 - h), (x + 86, 222 - h)], fill=(50, 40, 70))
        if j % 3 != 1:
            d.rectangle([x + 14, 236 - h, x + 30, 252 - h], fill=(255, 206, 130)); glow(img, x + 22, 244 - h, 20, (255, 200, 120), 0.25)
    d.rectangle([0, 220, W, H], fill=(36, 32, 52))
    for x in range(int(-(off % 24)), W, 24): d.rectangle([x, 236, x + 12, 238], fill=(56, 50, 74))
    hx = W + 160 - u * 260                                    # 小屋最后停在画面右边
    cottage(img, d, hx, 220, T, door=ease(clamp((lt - stop - 0.6) / 0.8)))
    pix.fireflies(img, d, T, 16, (0, 120, W, 240), seed=9)
    walking = lt < stop
    px = 220 if walking else lerp(220, hx + 18, ease(clamp((lt - stop) / 1.4)))
    if lt > stop + 1.6: return vig(img, 0.4, (6, 6, 20))
    pix.person(img, 'boy', px, 230, view='side', pose='walk' if (walking or lt < stop + 1.4) else 'stand', ph=wph(T), s=2)
    cat(img, px - 28, 230, 'walk', 2, rim=(100, 96, 130), T=T)
    vig(img, 0.4, (6, 6, 20))


# ================================================================ 最后一段：小屋里
def room(img, d, T, warm=1.0, night=1.0):
    img.paste(lerpc((60, 46, 50), (120, 86, 70), warm * 0.6), (0, 0, W, H))
    for x in range(0, W, 20): d.line([(x, 0), (x, 200)], fill=lerpc((70, 54, 56), (130, 94, 76), warm * 0.6))
    d.rectangle([0, 200, W, H], fill=(90, 60, 50))


def s_tea(img, d, lt, dur, T, A):
    room(img, d, T)
    glow(img, 380, 80, 160, (255, 200, 130), 0.4)
    d.polygon([(360, 40), (400, 40), (410, 70), (350, 70)], fill=(250, 220, 160)); d.line([(380, 70), (380, 120)], fill=(70, 50, 40))
    # 糖罐
    d.rectangle([60, 150, 96, 196], fill=(200, 230, 240)); d.rectangle([58, 144, 98, 150], fill=(180, 120, 90))
    for j in range(7):
        r = rng(j)
        x, y = 64 + r.uniform(0, 24), 156 + r.uniform(0, 32)
        d.ellipse([x, y, x + 6, y + 6], fill=[(255, 120, 150), (255, 210, 90), (140, 220, 160)][j % 3])
    bust(img, d, 'boy', 240, 50, 5, 'closed' if lt > 1.0 else 'smile')
    # 双手捧着的热茶
    d.rounded_rectangle([206, 192, 274, 252], 8, fill=(240, 236, 226)); d.rectangle([206, 204, 274, 210], fill=(220, 90, 80))
    d.arc([262, 206, 290, 236], 270, 90, fill=(240, 236, 226), width=4)
    for hx in (196, 262): d.rounded_rectangle([hx, 214, hx + 20, 244], 6, fill=SKIN)
    props.smoke(img, 240, 186, T, n=6, col=(255, 250, 250), shade=None, vx=4, vy=-24, life=1.8, r0=2, r1=8, seed=13, a=0.6)
    vig(img, 0.4, (20, 10, 10))


def s_sill(img, d, lt, dur, T, A):
    img.paste((44, 34, 50), (0, 0, W, H))
    wx0, wy0, wx1, wy1 = 70, 20, 410, 190
    sky(img, NIGHT, wy0, wy1, 5)
    a = np.asarray(img).copy(); a[:, :wx0] = (44, 34, 50); a[:, wx1:] = (44, 34, 50); img.paste(Image.fromarray(a))
    stars(d, T, wy1, 1, 200)
    for j in range(16):                                       # 星星变成露珠，顺着玻璃流到窗台
        r = rng(j * 5)
        x = r.uniform(wx0 + 10, wx1 - 10)
        per = r.uniform(1.6, 2.6)
        k = ((T + r.random() * per) % per) / per
        y = wy0 + r.uniform(0, 60) + ein(k) * (wy1 - wy0)
        twinkle(d, int(x), int(wy0 + r.uniform(0, 60)), 1 - k, (255, 250, 220), 2) if k < 0.3 else None
        if k >= 0.3:
            d.ellipse([x - 1, y - 2, x + 1, y + 1], fill=(200, 220, 255))
            d.line([(x, y - 2), (x, y - 10 * k)], fill=(120, 140, 200))
    d.rectangle([wx0 - 8, wy0 - 8, wx1 + 8, wy0], fill=(110, 80, 64))
    d.line([((wx0 + wx1) // 2, wy0), ((wx0 + wx1) // 2, wy1)], fill=(110, 80, 64), width=4)
    d.rectangle([wx0 - 8, wy0, wx0, wy1], fill=(110, 80, 64)); d.rectangle([wx1, wy0, wx1 + 8, wy1], fill=(110, 80, 64))
    # 窗台：积了一小片发光的水，猫睡在上面，旁边一盆小草
    d.rectangle([wx0 - 20, wy1, wx1 + 20, wy1 + 14], fill=(150, 110, 84)); d.rectangle([wx0 - 20, wy1 + 14, wx1 + 20, wy1 + 18], fill=(110, 80, 64))
    pw = 40 + lt * 30
    d.ellipse([220 - pw, wy1 + 2, 220 + pw, wy1 + 8], fill=(150, 170, 220))
    for j in range(6): twinkle(d, int(220 - pw + j * pw / 3), wy1 + 4, (T * 0.8 + j * 0.2) % 1, (255, 255, 230), 2)
    cat(img, 340, wy1 + 2, 'sleep', 2, rim=(150, 130, 160), T=T)
    d.rectangle([110, wy1 - 18, 130, wy1], fill=(200, 110, 80))
    for j in range(5): d.line([(120, wy1 - 18), (112 + j * 4, wy1 - 34 + (j % 2) * 4)], fill=(110, 180, 90), width=2)
    vig(img, 0.4, (10, 6, 16))


def s_flicker(img, d, lt, dur, T, A):
    img.paste((40, 28, 34), (0, 0, W, H))
    fl = 0.75 + 0.25 * math.sin(T * 13) * math.sin(T * 7.3)
    cx, cy = 300, 172
    # 墙上跳动的光影，有一下拼成了一颗心
    heart_k = clamp(1 - abs(lt - dur * 0.55) / 0.9)
    for j in range(6):
        r = rng(j)
        x = 300 + r.uniform(-160, 120) + math.sin(T * (3 + j)) * 10; y = r.uniform(30, 120) + math.cos(T * (2 + j)) * 6
        glow(img, x, y, r.uniform(20, 40), (255, 180, 110), 0.18 * fl * (1 - heart_k))
    if heart_k > 0:
        hx, hy = 300, 80
        blend_box(img, (220, 20, 380, 150), (255, 170, 120), (np.asarray(heart_mask(), float) / 255) * 0.45 * heart_k * fl)
    glow(img, cx, cy - 20, 150, (255, 190, 120), 0.45 * fl)
    # 桌子、蜡烛、趴着睡着的他
    d.rectangle([0, 180, W, H], fill=(110, 72, 50)); d.rectangle([0, 180, W, 184], fill=(150, 100, 70))
    d.rectangle([cx - 4, cy - 20, cx + 4, cy + 8], fill=(250, 240, 220))
    hh = 6 + 3 * fl
    d.polygon([(cx - 3, cy - 20), (cx + 3, cy - 20), (cx, cy - 20 - hh * 2)], fill=(255, 200, 80))
    d.point((cx, cy - 24), fill=(255, 255, 220))
    d.ellipse([cx - 12, cy + 6, cx + 12, cy + 12], fill=(200, 190, 170))
    sleep = clamp((lt - 1.0) / 1.2)
    bust_y = lerp(70, 110, ease(sleep))
    bust(img, d, 'boy', 160, bust_y, 4, 'half' if sleep < 0.5 else 'closed')
    d.rectangle([90, 176, 240, 196], fill=(96, 118, 84)); d.rounded_rectangle([200, 172, 230, 190], 6, fill=SKIN)
    if sleep >= 1:
        k = (T * 0.6) % 1
        dpaste(img, pix.spr('zz', 2, tint=(255, 240, 220)), 210 + k * 20, 110 - k * 30, clamp(min(k * 4, (1 - k) * 2)))
    cat(img, 380, 182, 'sleep', 2, rim=(150, 110, 100), T=T)
    vig(img, 0.45, (10, 4, 8))


@lru_cache(None)
def heart_mask():
    m = Image.new('L', (160, 130)); md = ImageDraw.Draw(m)
    md.polygon(heart_poly(80, 66, 4.0), fill=255)
    return m


def s_close_book(img, d, lt, dur, T, A):
    img.paste((60, 40, 40), (0, 0, W, H))
    glow(img, 240, 140, 240, (255, 200, 140), 0.35)
    shut = ease(clamp((lt - 0.8) / 0.7))
    # 封面上贴着一张小火车贴纸
    d.rectangle([110, 70, 370, 220], fill=(60, 40, 30))
    d.rectangle([120, 74, 360, 214], fill=(244, 238, 220))
    for j in range(8): d.line([(140, 90 + j * 14), (340 - (j * 17) % 50, 90 + j * 14)], fill=(110, 100, 120))
    if shut > 0:
        xe = lerp(360, 120, shut)
        d.polygon([(xe, 70 - 30 * math.sin(math.pi * shut)), (360, 70), (360, 220), (xe, 220 + 10 * math.sin(math.pi * shut))], fill=(120, 60, 54))
        if shut > 0.95:
            d.rectangle([120, 70, 360, 220], fill=(120, 60, 54))
            d.rectangle([120, 70, 130, 220], fill=(90, 44, 40))
            train(img, d, 300, 160, T, cars=1, s=0.5, rust=0, people=False, roll=0)
            props.rails(d, 160, 0, (90, 80, 90), (150, 110, 90), x0=180, x1=310, gap=6)
    if lt > 1.5:                                              # 一口气叹出来
        k = (lt - 1.5) / (dur - 1.5)
        props.puff(img, 400 + k * 30, 60 - k * 10, 6 + k * 14, (250, 240, 240), 0.6 * (1 - k))
    for hx in (90, 380): d.rounded_rectangle([hx - 16, 180, hx + 16, 230], 8, fill=SKIN)
    vig(img, 0.45, (20, 8, 8))


def s_dawnlight(img, d, lt, dur, T, A):
    k = ease(clamp(lt / 1.4))
    img.paste(lerpc((50, 40, 60), (150, 120, 120), k), (0, 0, W, H))
    tfill(img, 'polygon', [(380, 0), (480, 0), (320, H), (180, H)], (255, 230, 180), 0.35 * k)
    bust(img, d, 'boy', 220, 46, 5, 'smile' if lt > 0.6 else 'neutral')
    for j in range(20):
        r = rng(j * 3)
        x = r.uniform(220, 440) + math.sin(T + j) * 4; y = (r.uniform(0, H) - T * 8) % H
        d.point((x, y), fill=(255, 240, 210))
    glow(img, 340, 100, 80, (255, 240, 200), 0.3 * k)
    vig(img, 0.3, (40, 20, 20))


# ================================================================ 原野里的旧火车爬满青苔
def meadow(img, d, T, moss, people=True, s=1.0, base=212):
    sky(img, GOLDEN, 0, base, 6)
    glow(img, 380, base - 40, 200, (255, 230, 170), 0.5, 90)
    d.ellipse([350, base - 70, 410, base - 10], fill=(255, 244, 210))
    for j in range(4):
        cloud(d, (j * 140 + T * 4) % (W + 120) - 60, 26 + (j % 2) * 30, 2.2, (255, 226, 206), (246, 180, 170), (255, 244, 236))
    mountains(d, base - 14, 30, 0.014, 0.8, (196, 140, 150))
    d.rectangle([0, base - 14, W, H], fill=(140, 170, 80))
    for k in range(10):
        y = base - 10 + k * 8
        for x in range(-(k * 7) % 11, W, 11): d.point((x, y), fill=(170, 200, 100) if (x + k) % 2 else (110, 150, 70))
    for j in range(5):                                        # 光束
        x = 300 + j * 30
        tfill(img, 'polygon', [(x, 0), (x + 14, 0), (x - 120, H), (x - 160, H)], (255, 240, 200), 0.06)


def s_moss(img, d, lt, dur, T, A):
    f = lt / dur
    moss = 0.25 + 0.75 * ease(f)
    meadow(img, d, T, moss)
    # 坍了一半的站台和褪色的站牌
    d.polygon([(250, 214), (440, 214), (448, 228), (244, 228)], fill=(150, 140, 130))
    d.rectangle([380, 150, 382, 214], fill=(110, 100, 100))
    d.polygon([(352, 138), (412, 140), (410, 154), (350, 152)], fill=(214, 206, 190))
    text(img, '无名站', 381, 146, (150, 140, 150), None, FONT_S, shadow=False)
    for j in range(int(30 * moss)):
        r = rng(j * 7)
        x = r.uniform(250, 440)
        d.ellipse([x - 4, 211, x + 4, 217], fill=[MOSS, MOSS_D, MOSS_L][j % 3])
    # 停在原野里的旧铁皮火车，慢慢爬满青苔
    train(img, d, 236, 214, T, cars=1, seed=4, roll=0, moss=moss, rust=1.0, people=False)
    for j in range(int(40 * moss)):                           # 长出来的花
        r = rng(j * 13)
        x = r.uniform(10, 470)
        pix.flower(d, x, 230 + r.uniform(0, 36), [(255, 240, 120), (255, 170, 200), (250, 250, 250)][j % 3], j % 3, h=int(4 + 6 * moss))
    pix.grass(d, 230, (110, 160, 70), (90, 140, 60), T, step=4)
    # 老了的他坐在站台边，猫趴在旁边
    pix.person(img, 'boy', 330, 228, age='old', view='side', pose='sit', s=2, flip=True, expr='smile')
    cat(img, 300, 214, 'sit', 2, T=T)
    for j in range(5):
        pix.butterfly(d, int(80 + j * 80 + 20 * math.sin(T * 1.5 + j)), int(150 + 20 * math.sin(T * 2 + j * 2)), T,
                      [(255, 255, 255), (255, 210, 120), (200, 220, 255)][j % 3], j)
    vig(img, 0.25, (100, 50, 40))


def s_outro(img, d, lt, dur, T, A):
    meadow(img, d, T, 1.0, base=226)
    train(img, d, 300, 230, T, cars=1, s=0.6, seed=4, roll=0, moss=1.0, people=False)
    pix.person(img, 'boy', 330, 236, age='old', view='side', pose='sit', s=1, flip=True)
    cat(img, 314, 230, 'sleep', 1, T=T)
    for j in range(5):
        pix.bird(d, (j * 100 + T * 18) % (W + 40) - 20, 60 + j * 10 + math.sin(T + j) * 4, T, (150, 90, 90), j)
    title_block(img, d, lt, T, cy=84, appear=0.3, step=0.35, sweep_at=2.4, sub=False)
    k = clamp((lt - 2.4) / 0.8)
    if k > 0: text(img, '— 完 —', W / 2, 132, (255, 248, 230), (90, 50, 50), FONT_S, alpha=k)
    vig(img, 0.3, (60, 30, 30))
    out = clamp((lt - (dur - 1.8)) / 1.6)
    if out > 0: dither_fade(img, ease(out), (0, 0, 0))
