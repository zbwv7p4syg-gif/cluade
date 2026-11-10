"""我好想你 · 第一段副歌和间奏。

副歌：在映着星空的水面上朝月亮下的"你"跑，怎么跑都够不着；手机里打好的"我好想你"一个字一个字删掉；
踮着脚去够坐在月牙上的人；回忆的拍立得绕着自己转；闭着眼流泪；举着笑脸面具走在街上；
在起雾的车窗上写"我好想你"，再一把抹掉，对着玻璃里的自己挤出一个笑。
间奏是四段暖色的回忆：海边骑车、雨夜共伞、河边烟火、樱花树下她把红围巾围到"我"脖子上，然后散成花瓣。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
from props import *          # noqa: F401,F403
from pix import (W, H, FONT, FONT_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky, stars,
                 person, wph, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, BAYER, city, put, rain)
from sc_a import scarf_tail, props_text_l, MEM_T, season_cols

CHORUS = ((0, (10, 10, 40)), (0.45, (40, 26, 96)), (0.8, (120, 50, 130)), (1, (232, 112, 150)))

pix.LOOK[('boy', 'f1')] = dict(pix.LOOK[('boy', 'young')], hair=(120, 78, 50), hair_s=(84, 52, 36), hair_l=(170, 120, 80), top=(96, 170, 124),
                               top_s=(68, 128, 96), arm=(84, 150, 110), low=(70, 70, 86), low_s=(50, 50, 66))
pix.LOOK[('girl', 'f1')] = dict(pix.LOOK[('girl', 'young')], hair=(40, 36, 52), hair_s=(24, 22, 34), hair_l=(84, 84, 116), top=(170, 130, 220),
                                top_s=(128, 94, 176), low=(170, 130, 220), low_s=(128, 94, 176), arm=(170, 130, 220), scarf=None, acc=(255, 200, 90))


# ================================================================ 我好想你 好想你（水面上的奔跑）
def s_miss1(img, d, lt, dur, T, A):
    hz = 178
    sky(img, CHORUS, 0, hz, 6)
    stars(d, T, hz, 1.0, 240, int(lt * 14), 0)
    f = clamp(lt / dur)
    mx = lerp(338, 392, f); mr = int(lerp(58, 40, f))
    glow(img, mx, 112, mr * 2.6, (255, 190, 210), 0.42); moon(d, mx, 112, mr, col=(255, 240, 226))
    for i in range(3): pix.meteor(d, lt, 0.4 + i * 1.9, 40 + i * 120, 10 + i * 12, 120, 50, life=0.8)
    d.rectangle([0, hz, W, H], fill=(22, 16, 62))
    # 月亮下面的"你"：背对着，越来越远
    gs = 2 if f < 0.55 else 1
    person(img, 'girl', mx, hz + 1, view='back', s=gs, shade=(0.62, 0.52, 0.7))
    # 往后掠的光线和花瓣
    for i in range(26):
        r = rng(i * 7)
        sp = 160 + r.random() * 260
        x = (r.uniform(0, W + 80) - lt * sp) % (W + 80) - 40; y = r.uniform(8, hz - 8)
        ln = 8 + sp * 0.06
        d.line([(x, y), (x + ln, y)], fill=lerpc((90, 70, 150), (255, 220, 240), r.random() * 0.7))
    # "我"
    x = 126 + 10 * math.sin(lt * 1.3)
    for i in range(6):                          # 往后飞的眼泪
        k = (lt * 2.2 + i / 6) % 1
        d.rectangle([x - 6 - k * 46, hz - 44 - 10 * math.sin(k * 3.14) + i % 3, x - 5 - k * 46, hz - 43 - 10 * math.sin(k * 3.14) + i % 3], fill=(170, 214, 255))
    person(img, 'boy', x, hz + 1, view='side', pose='run', ph=wph(lt, 11), expr='sad', arms='reach' if int(lt * 1.2) % 2 else 'run', s=2)
    reflect(img, hz, H - hz, T, tint=(30, 16, 70), a=0.62, amp=2.2, src_h=H - hz)
    ripples(d, T, (x - 30, hz + 3, x + 16, hz + 12), 3, (200, 170, 240), seed=1, per=0.5, rmax=14)
    for i in range(14):                         # 水面的反光
        r = rng(i * 3 + 9)
        gx = (r.uniform(0, W) - lt * 60) % W; gy = r.uniform(hz + 4, H - 30)
        if math.sin(T * 5 + i) > 0: d.line([(gx, gy), (gx + r.randint(3, 9), gy)], fill=(180, 140, 220))
    pix.petals(d, T, 18, speed=14, wind=-120, seed=4)
    vig(img, 0.4)


# ================================================================ 却不露痕迹（手机）
def s_phone(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(14, 14, 34))
    bokeh(img, T, 7, seed=8, a=0.1)
    typing = lt < 2.0 or 4.2 < lt < 5.0
    expr = 'sad' if lt < 2.9 else ('closed' if lt < 4.1 or lt > 5.2 else 'down')
    bust(img, d, 'boy', 112, 44, 4, expr)
    on = 1 - span(lt, 5.9, 6.2)
    lighting(img, [(268, 150, 230, 0.95 * on)], amb=0.2, tint=(0.25, 0.27, 0.5))
    # 手机
    x0, y0, x1, y1 = 262, 4, 420, 226
    d.rounded_rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], 13, fill=(6, 6, 14))
    d.rounded_rectangle([x0, y0, x1, y1], 12, fill=(40, 40, 58))
    sx0, sy0, sx1, sy1 = x0 + 6, y0 + 12, x1 - 6, y1 - 8
    d.rectangle([sx0, sy0, sx1, sy1], fill=lerpc((10, 10, 18), (24, 26, 42), on))
    d.rounded_rectangle([x0 + 62, y0 + 4, x0 + 96, y0 + 8], 2, fill=(14, 14, 24))
    if on > 0.5:
        d.rectangle([sx0, sy0, sx1, sy0 + 28], fill=(36, 38, 62))
        h = head_img('girl', 'young', 'smile', 1)
        d.ellipse([sx0 + 6, sy0 + 3, sx0 + 28, sy0 + 25], fill=(250, 226, 190)); img.paste(h, (sx0 + 9, sy0 + 5), h)
        text(img, '你', sx0 + 44, sy0 + 14, col=(240, 240, 250), out=None, shadow=False)
        props_text_l(img, '<', sx1 - 14, sy0 + 14, col=(150, 156, 200))
        text(img, '— 两年前 —', (sx0 + sx1) / 2, sy0 + 42, col=(120, 124, 160), out=None, font=FONT_S, shadow=False)
        d.rounded_rectangle([sx0 + 6, sy0 + 52, sx0 + 92, sy0 + 72], 6, fill=(60, 64, 96)); props_text_l(img, '到家了吗？', sx0 + 12, sy0 + 62, (230, 232, 250), FONT_S)
        d.rounded_rectangle([sx1 - 80, sy0 + 78, sx1 - 6, sy0 + 98], 6, fill=(96, 150, 230)); props_text_l(img, '到了，晚安', sx1 - 74, sy0 + 88, (250, 250, 255), FONT_S)
        d.rounded_rectangle([sx0 + 6, sy0 + 104, sx0 + 62, sy0 + 124], 6, fill=(60, 64, 96)); props_text_l(img, '晚安 :)', sx0 + 12, sy0 + 114, (230, 232, 250), FONT_S)
        text(img, '— 今天 03:07 —', (sx0 + sx1) / 2, sy0 + 142, col=(120, 124, 160), out=None, font=FONT_S, shadow=False)
        # 输入框：打出来，停一停，又一个字一个字删掉
        full = '我好想你'
        if lt < 2.9: s = full[:int(clamp((lt - 0.4) / 0.36, 0, 4))]
        elif lt < 4.0: s = full[:max(0, 4 - int((lt - 2.9) / 0.24) - 1)]
        elif lt < 5.1: s = '晚安'[:int(clamp((lt - 4.2) / 0.3, 0, 2))]
        else: s = '晚安'[:max(0, 2 - int((lt - 5.1) / 0.2) - 1)]
        iy = sy1 - 30
        d.rectangle([sx0, iy - 6, sx1, sy1], fill=(36, 38, 62))
        d.rounded_rectangle([sx0 + 6, iy, sx1 - 34, iy + 22], 8, fill=(250, 250, 255))
        props_text_l(img, s, sx0 + 12, iy + 11, (40, 36, 60))
        cx_ = sx0 + 12 + FONT.getlength(s)
        if int(T * 2.5) % 2 == 0: d.rectangle([cx_ + 1, iy + 4, cx_ + 2, iy + 18], fill=(96, 150, 230))
        hot = len(s) == 4 and 1.9 < lt < 2.9
        d.ellipse([sx1 - 28, iy, sx1 - 6, iy + 22], fill=(96, 150, 230) if hot and int(T * 4) % 2 else (70, 100, 170))
        d.polygon([(sx1 - 21, iy + 6), (sx1 - 11, iy + 11), (sx1 - 21, iy + 16)], fill=(250, 250, 255))
        if 2.9 <= lt < 4.0 or lt >= 5.1:        # 删字的时候飘走的碎字
            for i in range(6):
                k = (lt * 1.6 + i / 6) % 1
                d.point((sx0 + 20 + i * 12 + 4 * math.sin(k * 6 + i), iy - 4 - k * 26), fill=lerpc((250, 250, 255), (24, 26, 42), k))
        glow(img, (sx0 + sx1) / 2, 140, 150, (120, 150, 255), 0.1, ry=170)
    # 大拇指
    tap = 2 * (int(T * 5) % 2) if typing or 2.9 < lt < 4.0 else 0
    tx, ty = (sx1 - 16, sy1 - 14) if 1.9 < lt < 2.9 else (sx0 + 60, sy1 - 2)
    d.rounded_rectangle([tx - 9, ty + tap - 2, tx + 12, H + 20], 8, fill=pix.SKIN, outline=pix.OUT)
    d.rounded_rectangle([tx - 5, ty + tap + 1, tx + 5, ty + tap + 9], 3, fill=(255, 236, 220))
    vig(img, 0.45)


# ================================================================ 我还踮着脚思念
TEAL = ((0, (16, 22, 60)), (0.45, (36, 60, 110)), (0.8, (90, 120, 150)), (1, (236, 170, 150)))


def crescent(img, d, x, y, r, T, ghost_a=1.0):
    glow(img, x, y, r * 3, (255, 236, 180), 0.4)
    bg = img.getpixel((int(x + r * 0.5), int(max(0, y - r * 0.5))))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 240, 190))
    d.ellipse([x - r + r * 0.55, y - r - r * 0.25, x + r + r * 0.55, y + r - r * 0.25], fill=bg)
    if ghost_a > 0:
        ghost(img, 'girl', x - r * 0.25, y + r * 0.92 + 16, 2, ghost_a, view='side', pose='sit', expr='smile', flip=True)


def s_tiptoe(img, d, lt, dur, T, A):
    sky(img, TEAL, 0, H, 6)
    stars(d, T, 170, 0.8, 150)
    for i in range(3): cloud(d, (i * 200 + T * 4) % 640 - 100, 150 + i * 14, 1.6, (70, 90, 140), (56, 70, 120))
    city(img, d, 252, 5, 0, (30, 40, 86), win=(255, 214, 130), hmin=20, hmax=60, frac=0.3, T=T)
    up = thump(T, 0.5)
    bob = math.sin(lt * 1.7)
    mx, my = 356, 78 + 5 * bob - 4 * up
    crescent(img, d, mx, my, 26, T)
    # 楼顶，一摞书和一把椅子
    d.rectangle([40, 232, 330, H], fill=(28, 30, 62)); d.rectangle([36, 226, 334, 232], fill=(52, 56, 100)); d.line([(36, 226), (334, 226)], fill=(90, 96, 150))
    for px in range(50, 330, 26): d.line([(px, 206), (px, 226)], fill=(52, 56, 100))
    d.line([(40, 206), (330, 206)], fill=(52, 56, 100))
    wob = round(math.sin(lt * 5) * 1.2 * up)
    cx = 196
    d.rectangle([cx - 14 + wob, 196, cx + 14 + wob, 200], fill=(170, 120, 84)); d.rectangle([cx - 14 + wob, 170, cx - 11 + wob, 226], fill=(140, 96, 66))
    d.rectangle([cx + 11 + wob, 200, cx + 14 + wob, 226], fill=(140, 96, 66)); d.rectangle([cx - 14 + wob, 176, cx - 4 + wob, 180], fill=(140, 96, 66))
    for k, c in enumerate(((204, 90, 80), (90, 140, 190), (236, 196, 100), (120, 170, 130))):
        d.rectangle([cx - 11 + (k % 2) * 3 + wob, 192 - k * 5, cx + 11 - (k % 2) * 2 + wob, 196 - k * 5], fill=c)
        d.line([(cx - 11 + (k % 2) * 3 + wob, 196 - k * 5), (cx + 11 - (k % 2) * 2 + wob, 196 - k * 5)], fill=lerpc(c, (0, 0, 0), 0.3))
    fy = 177 - round(5 * up)
    d.rectangle([cx - 3 + wob, fy, cx - 2 + wob, 177], fill=(150, 96, 70)); d.rectangle([cx + 3 + wob, fy, cx + 4 + wob, 177], fill=(150, 96, 70))   # 踮起来的脚尖
    person(img, 'boy', cx + wob, fy, view='side', arms='up', expr='sad', s=2)
    # 指尖和月牙之间总差那么一点
    hx, hy = cx + 6 + wob, fy - 46
    tx, ty = mx - 34, my + 30
    n = 12
    for i in range(1, n):
        px = lerp(hx, tx, i / n); py = lerp(hy, ty, i / n) - 10 * math.sin(i / n * 3.14)
        if (i + int(T * 6)) % 3: d.point((px, py), fill=(255, 236, 190))
    twinkle(d, int(hx), int(hy - 4), (T * 1.2) % 1, size=3)
    for i in range(8):
        r = rng(i * 13)
        k = (T * 0.4 + r.random()) % 1
        d.point((mx - 30 + r.uniform(-20, 30), my + 40 + k * 60), fill=lerpc((255, 240, 200), (40, 60, 110), k))
    vig(img, 0.4)


# ================================================================ 我还任记忆盘旋
ORBIT_T = (MEM_T[0], 150.2, MEM_T[2], 143.6, MEM_T[1], MEM_T[3])


def s_orbit(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(20, 14, 48))
    glow(img, 240, 140, 260, (120, 70, 180), 0.35, ry=170)
    cx, cy = 240, 132
    for i in range(170):                        # 绕着转的星尘
        r = rng(i * 3 + 1)
        rad = r.uniform(30, 290); a = r.uniform(0, 6.283) + T * (0.5 + 30 / rad) * 0.5
        x = cx + math.cos(a) * rad; y = cy + math.sin(a) * rad * 0.42
        if 0 <= x < W and 0 <= y < H:
            d.point((x, y), fill=lerpc((90, 70, 150), (255, 236, 255), r.random() * (0.5 + 0.5 * math.sin(T * 3 + i))))
    items = []
    for i, T0 in enumerate(ORBIT_T):
        a = lt * 1.05 + i * 6.283 / len(ORBIT_T)
        items.append((math.sin(a), cx + 176 * math.cos(a), cy - 8 + 40 * math.sin(a), T0, i))
    a2 = -lt * 1.7
    plane = (math.sin(a2), cx + 110 * math.cos(a2), cy - 60 + 22 * math.sin(a2), math.cos(a2))

    def draw(depth, x, y, T0, i):
        if depth < 0: ph = fade_to(mini(T0, 44, 25), (30, 20, 60), 0.45)
        else: ph = mini(T0, 64, 36)
        polaroid(img, d, x, y, ph, rot=round(6 * math.sin(lt * 1.3 + i * 2)))

    def paper_plane(depth, x, y, c):
        s = 1 if depth < 0 else 2
        dr = -1 if c > 0 else 1                 # 飞的方向
        col = (160, 150, 200) if depth < 0 else (250, 248, 240)
        d.polygon([(x + dr * 8 * s, y), (x - dr * 6 * s, y - 4 * s), (x - dr * 3 * s, y), (x - dr * 6 * s, y + 3 * s)], fill=col, outline=OUT)
        for k in range(1, 6):
            d.point((x - dr * (8 + k * 5) * s, y + math.sin(k + T * 6)), fill=lerpc(col, (20, 14, 48), k / 6))

    for it in sorted(items):
        if it[0] < 0: draw(*it)
    if plane[0] < 0: paper_plane(*plane)
    glow(img, cx, cy + 20, 70, (255, 200, 220), 0.25)
    d.ellipse([cx - 34, cy + 66, cx + 34, cy + 76], fill=(14, 10, 36))
    person(img, 'boy', cx, cy + 72, view='front', expr='closed', s=3)
    for it in sorted(items):
        if it[0] >= 0: draw(*it)
    if plane[0] >= 0: paper_plane(*plane)
    vig(img, 0.45)


# ================================================================ 我还闭着眼流泪
def s_tears(img, d, lt, dur, T, A):
    sky(img, ((0, (12, 14, 40)), (0.6, (26, 32, 78)), (1, (50, 48, 104))), 0, H, 5)
    bokeh(img, T, 16, seed=3, a=0.3, rmin=8, rmax=24)
    d.rectangle([236, 0, 240, H], fill=(10, 10, 28)); d.rectangle([0, 96, W, 100], fill=(10, 10, 28))
    drops_on_glass(img, d, T, (0, 0, W, H), n=70, seed=2)
    s = 6; cx = 240; top = 6 + round(1.5 * math.sin(lt * 1.2))
    eyes = bust(img, d, 'boy', cx, top, s, 'cry')
    lighting(img, [(cx + 120, 60, 260, 0.7), (cx - 160, 40, 200, 0.35)], amb=0.42, tint=(0.3, 0.32, 0.56))
    tear, tear_l = (130, 196, 255), (220, 240, 255)
    chin = top + 21 * s
    for k, (ex, ey) in enumerate(eyes):
        side = -1 if k == 0 else 1
        grow = clamp((lt - 0.2 - k * 0.3) / 1.4)
        y0 = ey + s; y1 = lerp(y0, chin - 4, grow)
        for y in range(int(y0), int(y1)):         # 脸上的泪痕
            x = ex + side * (2 + (y - y0) * 0.16)
            d.rectangle([x, y, x + 2, y], fill=tear if (y + int(T * 20)) % 7 else tear_l)
        for j in range(3):                        # 往下淌的泪珠
            ph = (lt * 0.55 + j / 3 + k * 0.17) % 1
            if lt < 0.4 + k * 0.3: continue
            if ph < 0.6:
                y = lerp(y0, chin - 4, ph / 0.6); x = ex + side * (2 + (y - y0) * 0.16)
                d.rectangle([x - 1, y, x + 3, y + 4], fill=tear); d.rectangle([x, y + 1, x + 1, y + 2], fill=tear_l)
            else:
                kk = (ph - 0.6) / 0.4
                y = chin - 4 + kk * kk * (H - chin + 10); x = ex + side * (2 + (chin - y0) * 0.16)
                d.rectangle([x - 1, y, x + 2, y + 5], fill=tear); d.point((x, y + 1), fill=tear_l)
    rain(d, T, 0, W, 0, H, 26, (90, 110, 170), speed=260, ln=7, seed=5)
    vig(img, 0.5)


# ================================================================ 我还装作无所谓
def street(img, d, T, off, night=False):
    sky(img, DAY4, 0, H, 5)
    glow(img, 400, 40, 70, (255, 250, 200), 0.6); d.ellipse([384, 24, 416, 56], fill=(255, 250, 214))
    for i in range(4): cloud(d, (i * 170 - off * 0.1) % 660 - 120, 18 + (i * 23) % 50, 1.7, (255, 255, 255), (214, 228, 244))
    city(img, d, 196, 21, off * 0.25, (176, 196, 226), hmin=40, hmax=110)
    # 一排小店
    cols = [((250, 214, 190), (226, 96, 96)), ((206, 228, 210), (86, 150, 120)), ((250, 232, 180), (236, 150, 70)), ((214, 214, 240), (110, 120, 200))]
    wshop = 128
    for k in range(-1, 6):
        i = (k + int(off // wshop))
        x = k * wshop - (off % wshop)
        wall, awn = cols[i % 4]
        d.rectangle([x, 92, x + wshop - 6, 222], fill=wall); d.rectangle([x, 92, x + wshop - 6, 98], fill=lerpc(wall, (0, 0, 0), 0.15))
        for s_ in range(0, wshop - 6, 12):
            d.rectangle([x + s_, 128, x + s_ + 11, 140], fill=awn if (s_ // 12) % 2 else (250, 246, 236))
        d.rectangle([x, 140, x + wshop - 6, 142], fill=lerpc(awn, (0, 0, 0), 0.3))
        d.rectangle([x + 10, 150, x + 68, 204], fill=(170, 214, 236)); d.rectangle([x + 10, 150, x + 68, 204], outline=lerpc(wall, (0, 0, 0), 0.3), width=2)
        d.line([(x + 20, 196), (x + 50, 156)], fill=(220, 240, 250))
        d.rectangle([x + 84, 156, x + 108, 222], fill=lerpc(awn, (60, 40, 40), 0.5)); d.rectangle([x + 88, 162, x + 104, 186], fill=(170, 214, 236))
        d.rectangle([x + 20, 104, x + 96, 122], fill=(250, 246, 236)); d.rectangle([x + 20, 104, x + 96, 122], outline=awn)
        for fx in range(4): pix.flower(d, x + 16 + fx * 14, 212, [(255, 120, 150), (255, 210, 90), (200, 140, 255)][(fx + i) % 3], kind=fx % 3, h=5)
        d.rectangle([x + 10, 212, x + 68, 218], fill=(150, 104, 76))
    d.rectangle([0, 222, W, H], fill=(206, 200, 196)); d.rectangle([0, 222, W, 224], fill=(232, 228, 222))
    for x in range(-int(off * 1.0) % 40 - 40, W, 40): d.line([(x, 225), (x - 16, H)], fill=(186, 180, 178))
    for k in range(-1, 4):                      # 行道树
        x = k * 190 - (off * 1.0 % 190) + 150
        pix.tree_round(d, x, 228, 1.7, sway=round(math.sin(T * 1.5 + k)))


def smiley(d, x, y, r, tilt=0):
    d.ellipse([x - r - 1, y - r - 1, x + r + 1, y + r + 1], fill=OUT)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 216, 84)); d.arc([x - r, y - r, x + r, y + r], 20, 140, fill=(236, 170, 50), width=2)
    for ex in (-5, 4): d.rectangle([x + ex, y - 5, x + ex + 1, y - 1], fill=(60, 40, 40))
    d.arc([x - 7, y - 6, x + 7, y + 8], 20, 160, fill=(60, 40, 40), width=2)
    d.point([(x - 8, y + 2), (x + 8, y + 2)], fill=(255, 150, 130))


def s_mask(img, d, lt, dur, T, A):
    off = lt * 46
    street(img, d, T, off)
    for i in range(3): pix.bird(d, (60 + i * 30 + lt * 30) % 520 - 20, 50 + i * 9, T, ph=i)
    # 迎面走来的朋友
    fx = 520 - lt * 150
    person(img, 'girl', fx, 246, age='f1', view='side', pose='walk', ph=wph(lt, 7), expr='happy', arms='wave', s=2, flip=True)
    person(img, 'boy', fx + 34, 248, age='f1', view='side', pose='walk', ph=wph(lt + 0.2, 7), expr='happy', s=2, flip=True)
    if 0.3 < lt < 2.0: bubble(img, d, fx - 60, 150, fx + 30, 176, tail=(fx - 4, 190)); text(img, '最近好吗？', fx - 15, 163, col=(60, 50, 70), out=None, font=FONT_S, shadow=False)
    x, y = 190, 250
    slip = ease(span(lt, 3.0, 3.4)) * (1 - ease(span(lt, 4.3, 4.7)))       # 面具滑下来一下
    person(img, 'boy', x, y, view='side', pose='walk', ph=wph(lt, 7), expr='sad', arms='umbrella', s=2)
    if slip > 0.3:
        ty = y - 40 + (lt - 3.2) * 16
        d.rectangle([x + 9, ty, x + 10, ty + 3], fill=(120, 190, 255))
    mx, my = x + 6 + 10 * slip, y - 45 + 26 * slip
    d.line([(x + 8, y - 26), (mx, my + 10)], fill=(150, 104, 76), width=2)
    smiley(d, mx, my, 14)
    if 1.2 < lt < 2.9 or lt > 4.7:
        bubble(img, d, x - 74, 142, x + 6, 168, tail=(x - 2, 186)); text(img, '挺好的呀～', x - 34, 155, col=(60, 50, 70), out=None, font=FONT_S, shadow=False)
        for i in range(3):
            k = (lt * 0.8 + i / 3) % 1
            put(img, 'note', x + 30 + k * 30 + 4 * math.sin(k * 8), y - 60 - k * 26, 1, alpha=clamp(2 - 2 * k))
    pix.petals(d, T, 12, speed=18, wind=-30, seed=2)


# ================================================================ 我好想你 好想你 / 却欺骗自己（起雾的车窗）
FOG_D = 6.70                                    # 前一句的长度
FOG_SC = 4


@lru_cache(None)
def fog_glyphs():
    """窗上写的字：每个字一张放大 4 倍、加粗的蒙版和它的左上角"""
    s = title_str(); out = []
    wd = [int(FONT.getlength(c)) for c in s]
    total = sum(wd) * FOG_SC + (len(s) - 1) * 10
    x = W // 2 - total // 2
    for c, w_ in zip(s, wd):
        m = Image.new('L', (w_ + 2, 20)); md = ImageDraw.Draw(m); md.fontmode = '1'
        md.text((1, 1), c, font=FONT, fill=255)
        a = np.array(m) > 0
        a = a.repeat(FOG_SC, 0).repeat(FOG_SC, 1)
        b = a.copy(); b[:, 1:] |= a[:, :-1]; b[1:] |= a[:-1]; b[:, 2:] |= a[:, :-2]; b[2:] |= a[:-2]
        out.append((b, x, 66))
        x += w_ * FOG_SC + 10
    return out


def fog_scene(img, d, t, T):
    sky(img, ((0, (12, 14, 40)), (0.55, (28, 32, 84)), (1, (70, 54, 116))), 0, H, 5)
    city(img, d, 262, 12, T * 22, (20, 22, 56), win=(255, 214, 130), hmin=70, hmax=190, frac=0.42, T=T, blink=False)
    for i in range(6):                          # 路灯一盏盏掠过
        x = (i * 110 - T * 150) % 660 - 60
        glow(img, x, 120, 40, (255, 210, 140), 0.5); d.rectangle([x - 1, 120, x + 1, H], fill=(16, 16, 40))
    bokeh(img, T, 16, seed=2, a=0.36, drift=40)
    clear_bg = np.asarray(img).copy()
    fog = np.full((H, W), 0.6) + 0.06 * np.sin(XX / 37 + T * 0.4) * np.cos(YY / 23)
    wrote = np.zeros((H, W), bool)
    fx = fy = None
    per = 1.25
    for i, (m, x, y) in enumerate(fog_glyphs()):
        k = clamp((t - 0.5 - i * per) / (per * 0.86))
        if k <= 0: continue
        h_, w_ = m.shape
        yy, xx = np.mgrid[0:h_, 0:w_]
        nb = -(-h_ // 12)
        order = (np.floor(yy / 12) + xx / w_) / nb                              # 一横条一横条从上往下写
        part = m & (order <= k)
        wrote[y:y + h_, x:x + w_] |= part
        if 0 < k < 1:
            band = min(nb - 1, int(k * nb))
            fx = x + (k * nb - band) * w_; fy = y + band * 12 + 6
    # 写出来的笔画往下淌水
    drip = np.zeros((H, W), bool)
    for i in range(14):
        r = rng(i * 17 + 3)
        gi = r.randrange(4); m, x, y = fog_glyphs()[gi]
        t0 = 0.5 + gi * per + per + r.uniform(0, 2.5)
        if t > t0:
            dx = x + r.randrange(6, m.shape[1] - 6); dy = y + m.shape[0] - r.randrange(2, 20)
            ln = int(min(90, (t - t0) * r.uniform(8, 22)))
            drip[dy:dy + ln, dx:dx + 2] = True
    wiped = np.zeros((H, W))
    tw = t - FOG_D
    if tw > 0:                                   # 一把抹掉
        px = lerp(-60, W + 80, ease(span(tw, 0.5, 2.0)))
        band = np.abs(YY - (118 + 16 * np.sin(XX / 70))) < 62 + 8 * np.sin(XX / 23)
        wiped = (band & (XX < px)).astype(float)
        wrote &= ~(XX < px); drip &= ~((XX < px) & band)
        fx, fy = (px, 118 + 16 * math.sin(px / 70)) if 0.5 < tw < 2.0 else (None, None)
    refog = clamp((tw - 4.6) / 2.2) if tw > 0 else 0
    fog = np.where(wrote | drip, 0.1, fog)
    fog = fog * (1 - wiped * 0.85)
    fog = np.clip(fog + refog * 0.7 * (0.6 + 0.4 * (YY / H)), 0, 0.92)
    blend_box(img, (0, 0, W, H), (198, 208, 228), fog, levels=10)
    if tw > 1.2:                                 # 抹开的地方映出自己的脸
        lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay)
        bust(lay, ld, 'boy', 250, 64, 4, 'sad' if tw < 3.4 else 'smile')
        a = np.array(lay).astype(float)
        al = (a[..., 3] / 255) * wiped * 0.5 * span(tw, 1.2, 2.2) * (1 - refog)
        base = np.asarray(img, float)
        mix = base * (1 - al[..., None]) + (a[..., :3] * 0.8 + np.array([20, 24, 60])) * al[..., None]
        img.paste(Image.fromarray(mix.astype(np.uint8)))
        if tw > 3.4 and refog < 0.5:
            tk = (tw - 3.4)
            ty = 64 + 15 * 4 + min(40, tk * 30)
            d.rectangle([250 - 22, ty, 250 - 20, ty + 3], fill=(170, 214, 255))
    drops_on_glass(img, d, T, (0, 0, W, H), n=46, seed=7, col=(214, 226, 255))
    if fx is not None:                           # 写字的手
        tip = (fx, fy)
        if tw > 0:
            d.rounded_rectangle([fx - 16, fy - 40, fx + 18, fy + 46], 12, fill=pix.SKIN, outline=pix.OUT)
            for k in range(1, 4): d.line([(fx - 16 + k * 9, fy - 38), (fx - 16 + k * 9, fy - 8)], fill=pix.SKIN_S)
            d.polygon([(fx - 10, fy + 44), (fx + 14, fy + 44), (fx + 60, H + 10), (fx + 10, H + 10)], fill=pix.SKIN, outline=pix.OUT)
        else:
            d.polygon([(fx - 2, fy - 2), (fx + 6, fy - 1), (fx + 44, fy + 60), (fx + 30, fy + 68)], fill=pix.SKIN, outline=pix.OUT)
            d.rounded_rectangle([fx + 24, fy + 52, fx + 70, fy + 96], 10, fill=pix.SKIN, outline=pix.OUT)
            d.polygon([(fx + 40, fy + 90), (fx + 70, fy + 80), (fx + 130, H + 10), (fx + 80, H + 10)], fill=pix.SKIN, outline=pix.OUT)
            d.rectangle([fx - 1, fy - 1, fx + 3, fy + 1], fill=(255, 236, 220))
    vig(img, 0.4)


def s_fogwrite(img, d, lt, dur, T, A):
    fog_scene(img, d, lt, T)


def s_wipe(img, d, lt, dur, T, A):
    fog_scene(img, d, lt + FOG_D, T)


# ================================================================ 间奏：四段回忆
def memory_frame(img, d, T, label=''):
    """回忆的样子：暖色、边上泛白、一圈相纸白边"""
    grade(img, sat=1.08, mul=(1.04, 1.0, 0.94), add=(8, 4, 0))
    vig(img, 0.5, col=(255, 244, 226))
    d.rectangle([0, 0, W - 1, H - 1], outline=(250, 246, 236), width=5)
    d.rectangle([5, 5, W - 6, H - 6], outline=(214, 204, 190))


def bicycle(d, x, y, roll, col=(214, 80, 84)):
    """侧面的自行车，朝右；(x, y) 是两轮中间的地面"""
    for wx in (x - 24, x + 24):
        d.ellipse([wx - 12, y - 24, wx + 12, y], outline=(44, 40, 52), width=2)
        for k in range(4):
            a = roll + k * math.pi / 4
            d.line([(wx - math.cos(a) * 10, y - 12 - math.sin(a) * 10), (wx + math.cos(a) * 10, y - 12 + math.sin(a) * 10)], fill=(150, 150, 164))
        d.point((wx, y - 12), fill=(230, 230, 236))
    d.line([(x - 24, y - 12), (x - 6, y - 30), (x + 16, y - 30), (x + 2, y - 12), (x - 24, y - 12)], fill=col, width=2)
    d.line([(x + 2, y - 12), (x - 6, y - 30)], fill=col, width=2)
    d.line([(x + 24, y - 12), (x + 15, y - 36)], fill=col, width=2); d.line([(x + 10, y - 38), (x + 20, y - 36)], fill=(60, 54, 66), width=2)
    d.rectangle([x - 11, y - 34, x - 1, y - 32], fill=(60, 54, 66)); d.rectangle([x - 36, y - 28, x - 14, y - 26], fill=(110, 104, 116))
    d.line([(x - 26, y - 26), (x - 24, y - 12)], fill=(110, 104, 116))
    a = roll * 0.8
    d.line([(x + 2, y - 12), (x + 2 + math.cos(a) * 6, y - 12 + math.sin(a) * 6)], fill=(60, 54, 66), width=2)


def m_bike(img, d, lt, dur, T, A):
    off = lt * 90
    sky(img, DUSK4, 0, 170, 6)
    glow(img, 356, 150, 120, (255, 226, 160), 0.55); d.ellipse([334, 128, 378, 172], fill=(255, 240, 190))
    for i in range(5): cloud(d, (i * 150 - off * 0.05) % 680 - 120, 20 + (i * 31) % 70, 1.5 + (i % 2) * 0.6, (255, 204, 170), (240, 156, 150))
    for i in range(4): pix.bird(d, 120 + i * 16 + lt * 8, 60 + (i % 2) * 7 + i * 4, T, col=(110, 70, 100), ph=i)
    # 海
    img.paste(pix.vgrad(W, 46, ((0, (255, 190, 140)), (0.4, (220, 140, 150)), (1, (110, 110, 176))), 5), (0, 168))
    for i in range(40):
        r = rng(i)
        gx = (r.uniform(0, W) - off * 0.15) % W; gy = r.uniform(170, 212)
        if math.sin(T * 4 + i) > -0.2:
            near_sun = abs(gx - 356) < 30 + (gy - 168)
            d.line([(gx, gy), (gx + r.randint(2, 8), gy)], fill=(255, 246, 210) if near_sun else (255, 200, 190))
    for k in range(2):                           # 远处的小岛和灯塔
        x = (k * 380 - off * 0.08) % 760 - 150
        d.ellipse([x, 160, x + 110, 186], fill=(150, 96, 130)); d.rectangle([x - 4, 172, x + 116, 186], fill=(150, 96, 130))
        if k == 0: d.rectangle([x + 70, 138, x + 75, 164], fill=(250, 240, 230)); d.rectangle([x + 69, 134, x + 76, 138], fill=(214, 80, 84))
    img.paste(pix.vgrad(W, 2, ((0, (255, 240, 220)), (1, (255, 240, 220)))), (0, 212))
    d.rectangle([0, 214, W, H], fill=(108, 96, 120)); d.rectangle([0, 214, W, 216], fill=(150, 136, 150))
    for x in range(-int(off) % 44 - 44, W, 44):  # 护栏
        d.rectangle([x, 196, x + 3, 214], fill=(240, 232, 226)); d.line([(x + 3, 196), (x + 3, 214)], fill=(190, 170, 176))
    d.rectangle([0, 198, W, 201], fill=(240, 232, 226)); d.line([(0, 202), (W, 202)], fill=(190, 170, 176))
    for x in range(-int(off * 1.3) % 70 - 70, W, 70): d.rectangle([x, 250, x + 30, 252], fill=(232, 220, 190))
    # 车和两个人
    bx, by = 232 + 6 * math.sin(lt * 0.9), 246
    d.ellipse([bx - 44, by - 2, bx + 44, by + 5], fill=(84, 74, 100))
    scarf_tail(d, bx - 32, by - 40, T * 1.4, n=18)
    person(img, 'girl', bx - 28, by - 9, view='side', pose='sit', expr='happy', arms='hug', s=2)
    bicycle(d, bx, by, -off / 12)
    person(img, 'boy', bx - 4, by - 14, view='side', pose='sit', expr='happy', arms='reach', s=2)
    for i in range(4):
        k = (lt * 0.5 + i / 4) % 1
        put(img, 'heart' if i % 2 else 'note', bx - 40 - k * 70, by - 80 - k * 30 + 5 * math.sin(k * 9 + i), 1 + (i % 2), alpha=clamp(2 - 2 * k))
    for k in range(3):                           # 近处掠过的路灯
        x = (k * 260 - off * 1.6) % 780 - 150
        d.rectangle([x, 96, x + 3, H], fill=(70, 56, 84)); d.rectangle([x - 14, 92, x + 3, 96], fill=(70, 56, 84)); d.rectangle([x - 14, 96, x - 8, 99], fill=(255, 236, 170))
    pix.petals(d, T, 14, speed=14, wind=-90, seed=6, cols=[(255, 236, 200), (255, 200, 170)])
    memory_frame(img, d, T)


def umbrella(d, x, y, col=SCARF, col2=SCARF_D, r=30):
    """撑开的伞，(x, y) 是伞柄顶端"""
    d.pieslice([x - r, y - r * 0.8, x + r, y + r * 0.8], 180, 360, fill=col, outline=OUT)
    for k in (-2, -1, 0, 1, 2):
        d.line([(x, y - r * 0.8), (x + k * r / 2.6, y)], fill=col2)
    for k in range(4):
        d.pieslice([x - r + k * r / 2, y - 4, x - r + (k + 1) * r / 2, y + 4], 180, 360, fill=(22, 22, 52))
    d.line([(x, y - r * 0.8 - 3), (x, y - r * 0.8)], fill=OUT)


def rainy_street(img, d, T, off=0):
    sky(img, ((0, (10, 12, 36)), (0.6, (24, 28, 70)), (1, (54, 48, 100))), 0, H, 5)
    city(img, d, 214, 9, off * 0.3, (20, 22, 54), win=(255, 206, 120), hmin=60, hmax=150, frac=0.3, T=T)
    city(img, d, 222, 14, off * 0.6, (30, 30, 70), win=(255, 226, 150), hmin=30, hmax=80, frac=0.4, T=T, wmin=24, wmax=50)
    d.rectangle([0, 222, W, H], fill=(26, 26, 60)); d.line([(0, 222), (W, 222)], fill=(70, 70, 120))


def m_umbrella(img, d, lt, dur, T, A):
    rainy_street(img, d, T)
    lamp(img, d, 150, 222, 1.0, h=96)
    lamp(img, d, 410, 222, 1.0, h=96)
    rain(d, T, 0, W, 0, 224, 110, (120, 140, 210), speed=240, ln=6)
    x = 196 + lt * 9
    ux, uy = x + 9, 140
    tfill(img, 'polygon', [(ux - 30, uy), (ux + 30, uy), (ux + 24, 222), (ux - 36, 222)], (26, 26, 64), 0.75)     # 伞下没有雨
    d.line([(ux, uy), (ux, 188)], fill=(230, 226, 236), width=2)
    person(img, 'boy', x, 223, view='side', pose='walk', ph=wph(lt, 4), expr='happy' if lt > 2.6 else 'smile', arms='umbrella', s=2)
    person(img, 'girl', x + 24, 223, view='side', pose='walk', ph=wph(lt + 0.3, 4), expr='happy', s=2)
    umbrella(d, ux, uy, r=34)
    reflect(img, 223, H - 223, T, tint=(16, 14, 50), a=0.6, amp=1.6)
    splashes(d, T, 226, H - 4, 26, (150, 170, 230))
    for i in range(3):
        k = (lt * 0.45 + i / 3) % 1
        put(img, 'heart', ux + 6 * math.sin(k * 7 + i) + (i - 1) * 12, uy - 34 - k * 40, 1 + (i == 1), alpha=clamp(2 - 2 * k))
    memory_frame(img, d, T)


def ferris(img, d, cx, cy, r, T):
    d.line([(cx - r * 0.5, cy + r + 16), (cx, cy)], fill=(60, 56, 100), width=3); d.line([(cx + r * 0.5, cy + r + 16), (cx, cy)], fill=(60, 56, 100), width=3)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(110, 100, 170), width=2)
    d.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6], outline=(70, 64, 120))
    for k in range(10):
        a = T * 0.25 + k * math.pi / 5
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        d.line([(cx, cy), (x, y)], fill=(80, 74, 130))
        c = [(255, 120, 140), (255, 214, 110), (120, 200, 255), (170, 255, 190)][k % 4]
        glow(img, x, y + 5, 7, c, 0.5); d.rectangle([x - 3, y + 2, x + 3, y + 8], fill=c); d.rectangle([x - 2, y + 4, x + 2, y + 6], fill=(255, 250, 230))
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 236, 170))


FW_COLS = [(255, 120, 150), (255, 214, 110), (130, 210, 255), (190, 150, 255), (150, 255, 190)]


def m_fireworks(img, d, lt, dur, T, A):
    sky(img, NIGHT4, 0, 190, 6)
    stars(d, T, 150, 0.7, 120)
    city(img, d, 190, 31, 0, (24, 24, 60), win=(255, 210, 130), hmin=14, hmax=46, frac=0.35, T=T)
    ferris(img, d, 394, 120, 50, T)
    t0 = T - lt
    for i, b in enumerate(beats_in(t0 - 2.5, T + 0.6)):
        r = rng(int(b * 10))
        pix.firework(img, d, T + 0.5, b, r.uniform(60, 330), r.uniform(36, 104), FW_COLS[i % 5], r=r.uniform(26, 44), seed=i, col2=FW_COLS[(i + 2) % 5])
    d.rectangle([0, 190, W, 232], fill=(18, 18, 52))
    reflect(img, 190, 42, T, tint=(14, 12, 44), a=0.7, amp=2.5, src_h=120)
    d.ellipse([-80, 222, 560, 400], fill=(26, 44, 60)); d.ellipse([-80, 222, 560, 400], outline=(50, 80, 90))
    pix.grass(d, 232, (30, 60, 66), (60, 100, 96), T, 0, W, 4)
    fl = 0.35 * thump(T, 0.5)
    person(img, 'boy', 206, 248, view='back', pose='sit', s=2, shade=(0.6 + fl, 0.6 + fl, 0.78 + fl * 0.5))
    person(img, 'girl', 236, 248, view='back', pose='sit', s=2, shade=(0.6 + fl, 0.6 + fl, 0.78 + fl * 0.5))
    pix.fireflies(img, d, T, 8, (20, 214, 460, 250))
    memory_frame(img, d, T)


def hill_tree(img, d, T, sf=0.2, bench=True):
    """山坡上的大树和长椅（和主歌里四季飞转的那棵是同一棵）"""
    leaf, leaf_l, ground = season_cols(sf)
    pix.hills(d, 214, 10, 0.011, 1.0, lerpc(ground, (60, 80, 110), 0.45))
    d.ellipse([-60, 196, 540, 420], fill=ground); d.ellipse([-60, 196, 540, 420], outline=lerpc(ground, (255, 255, 255), 0.3))
    pix.grass(d, 204, lerpc(ground, (0, 0, 0), 0.2), lerpc(ground, (255, 255, 255), 0.25), T, 90, 400, 5)
    pix.tree_round(d, 196, 202, 3.3, leaf, leaf_l, sway=round(math.sin(T * 1.5)))
    bx0 = 244
    if bench:
        d.rectangle([bx0, 184, bx0 + 62, 187], fill=(150, 100, 70)); d.rectangle([bx0, 170, bx0 + 62, 173], fill=(150, 100, 70))
        d.rectangle([bx0, 176, bx0 + 62, 179], fill=(132, 86, 60))
        for px in (bx0 + 3, bx0 + 57): d.rectangle([px, 170, px + 2, 202], fill=(96, 64, 48))
    return bx0


def m_blossom(img, d, lt, dur, T, A):
    sky(img, DAY4, 0, H, 5)
    glow(img, 90, 50, 80, (255, 250, 210), 0.5); d.ellipse([74, 34, 106, 66], fill=(255, 250, 220))
    for i in range(4): cloud(d, (i * 170 + T * 5) % 660 - 120, 20 + (i * 29) % 60, 1.8, (255, 255, 255), (220, 230, 246))
    bx0 = hill_tree(img, d, T, 0.2)
    give = 1.9                                    # 她把围巾围到"我"脖子上
    gone = span(lt, 3.3, 5.6)                     # 然后散成花瓣
    person(img, 'boy', bx0 + 16, 203, view='side', pose='sit', expr='happy' if lt < 3.6 else ('surprised' if lt < 4.6 else 'sad'), s=2,
           scarf=SCARF if lt > give else None)
    if gone < 1:
        age = 'young' if lt < give else 'ns'
        ghost(img, 'girl', bx0 + 44, 203, 2, 1 - gone, age=age, view='side', pose='sit', expr='happy' if lt < 3.2 else 'smile', flip=True,
              arms='reach' if give - 0.5 < lt < give + 0.4 else 'auto')
    if give - 0.1 < lt < give + 0.5:
        for i in range(8): twinkle(d, bx0 + 22 + int(rng(i).uniform(-10, 14)), 150 + int(rng(i + 9).uniform(-8, 8)), (lt - give + 0.1) / 0.6, size=3)
    if gone > 0:
        for i in range(70):
            r = rng(i * 5 + 2)
            k = (lt - 3.3) * 0.9 - r.random() * 0.9
            if k <= 0 or k > 1.6: continue
            px = bx0 + 44 + r.uniform(-12, 12) + k * (30 + 70 * r.random()) + 8 * math.sin(k * 6 + i)
            py = 196 - r.uniform(0, 50) - k * (20 + 40 * r.random()) + 30 * k * k
            c = pix.PETAL_COLS[i % 3] if i % 4 else (255, 236, 170)
            d.rectangle([px, py, px + 1, py + (i % 2)], fill=c)
    pix.petals(d, T, 46, speed=24, wind=30)
    memory_frame(img, d, T)
    if lt > 4.2: grade(img, sat=1 - 0.75 * span(lt, 4.2, dur), mul=(lerp(1, 0.7, span(lt, 4.6, dur)),) * 2 + (lerp(1, 0.9, span(lt, 4.6, dur)),))


pix.LOOK[('girl', 'ns')] = dict(pix.LOOK[('girl', 'young')], scarf=None)      # 把围巾送出去以后
