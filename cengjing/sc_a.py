"""曾经是情侣 · 片头和第一段主歌。签名都是 (img, d, lt, dur, T, A)：lt 是镜头内的时间，dur 是镜头时长，T 是全片时间，A 是这一帧的音量。

黄昏的山坡上，他和她背对着我们坐在大树下放风筝。片头一根红线在黑暗里勾出一颗心，心裂成两半，片名落在天上；
风把片名吹成云带走，天空撕开一道口子，雨落下来，只剩他一个人站在树下。雨水在地上汇成小溪，再汇成一条河，一只纸船顺流漂走。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
from props import *          # noqa: F401,F403  共用的颜色和道具
from pix import (W, H, FONT, FONT_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky, stars,
                 person, wph, put, twinkle, sparkle, hills, moon, cloud, darken, dither_fade, grade, vig, vgrad, BAYER, bayer)


def dpaste(img, im, x, y, a=1.0, ox=0):
    """按 Bayer 点阵的透明度贴图（像素风的半透明）"""
    if a <= 0: return
    if a < 1:
        arr = np.array(im)
        arr[pix.bayer(im.height, im.width, int(x) + ox, int(y)) >= a, 3] = 0
        im = Image.fromarray(arr)
    img.paste(im, (int(round(x)), int(round(y))), im)


def swoosh(d, x, y, ln, col, curl=True):
    """一道风：横线，尾巴打个卷"""
    d.line([(x, y), (x + ln, y)], fill=col)
    if curl:
        d.point([(x + ln + 1, y - 1), (x + ln + 2, y - 2), (x + ln + 2, y - 3), (x + ln + 1, y - 4), (x + ln, y - 4), (x + ln - 1, y - 3)], fill=col)


def winds(d, T, n, col, speed=320, y0=20, y1=230, seed=0, ln=(20, 60)):
    for i in range(n):
        r = rng(i * 41 + seed)
        per = (W + 160) / (speed * r.uniform(0.8, 1.3))
        k = ((T + r.random() * per) % per) / per
        x = -100 + k * (W + 160)
        y = r.uniform(y0, y1) + 4 * math.sin(T * 3 + i)
        swoosh(d, x, y, r.uniform(*ln), col, curl=i % 2 == 0)


# ================================================================ 黄昏的山坡
def hill_y(x):
    return 232 + 34 * ((x - 232) / 250) ** 2


GIRL_X, BOY_X = 214, 252
KITE_BASE = (408, 52)


def kite_xy(T, wind=0.0):
    return (KITE_BASE[0] + 10 * math.sin(T * 0.9) + wind * 40 + wind * 8 * math.sin(T * 7),
            KITE_BASE[1] + 6 * math.cos(T * 1.3) - wind * 10)


def hill_world(img, d, T, mood=0.0, wind=0.0, couple='sit', kite_on=True, clouds_x=0.0, girl=True, boy=True, sun=True):
    """黄昏（mood=0）到暴风雨（mood=1）的山坡。wind 0..1 让草、树和风筝摆得更厉害"""
    stops = mix_stops(SUNSET, STORM, mood)
    sky(img, stops, 0, 240)
    if sun and mood < 0.98:
        sx, sy = 240, 190
        glow(img, sx, sy, 120, (255, 190, 150), 0.38 * (1 - mood), 70)
        d.ellipse([sx - 24, sy - 24, sx + 24, sy + 24], fill=lerpc((255, 238, 200), stops[-1][1], mood))
        for k in range(3): d.line([(sx - 20 + k * 3, sy - 8 + k * 6), (sx + 20 - k * 3, sy - 8 + k * 6)], fill=lerpc((255, 222, 170), stops[-1][1], mood))
    # 远处的云
    for i, (cx, cy, s) in enumerate([(30, 120, 1.6), (170, 140, 1.2), (300, 116, 1.8), (420, 146, 1.3), (520, 128, 1.5)]):
        x = (cx + clouds_x * (0.6 + 0.2 * i) + T * 3) % (W + 120) - 60
        cloud(d, x, cy, s, lerpc((255, 196, 196), (70, 64, 92), mood), lerpc((236, 150, 166), (54, 50, 76), mood))
    pix.hills(d, 194, 5, 0.018, 1.0, lerpc((176, 108, 150), (42, 38, 62), mood))
    pix.hills(d, 208, 7, 0.013, 2.4, lerpc((122, 80, 130), (32, 30, 50), mood))
    main = lerpc((62, 62, 98), (24, 26, 38), mood)
    rim = lerpc((255, 170, 160), (60, 62, 84), mood)
    for x in range(W):
        y = int(hill_y(x))
        d.line([(x, y), (x, H)], fill=main)
        d.point((x, y), fill=rim)
    # 草：随风摆
    for i, x in enumerate(range(0, W, 3)):
        h = 2 + (i * 7) % 4
        sw = math.sin(T * (2 + wind * 6) + x * 0.08) * (0.6 + wind * 2.4) + wind * 2
        y = hill_y(x)
        d.line([(x, y), (x + sw, y - h)], fill=rim if i % 3 else lerpc(main, rim, 0.5))
    # 大树
    sway = math.sin(T * (1.2 + wind * 4)) * (1 + wind * 3)
    pix.tree_round(d, 388, hill_y(388) + 2, 2.3, lerpc((70, 66, 110), (28, 30, 46), mood), lerpc((110, 92, 140), (40, 42, 62), mood),
                   lerpc((52, 44, 70), (22, 22, 32), mood), sway)
    # 风筝和线
    if kite_on:
        kx, ky = kite_xy(T, wind)
        tail = kite(d, kx, ky, 1.4, T * (1 + wind * 2), RED, GOLD_L)
        hx, hy = BOY_X + 9, hill_y(BOY_X) - 30
        if boy: d.line(bez((hx, hy), tail, ((hx + tail[0]) / 2 + 20, (hy + tail[1]) / 2 + 26), 30), fill=lerpc((255, 240, 230), (150, 150, 170), mood))
    # 两个人
    shade = (1 - 0.45 * mood, 1 - 0.45 * mood, 1 - 0.3 * mood)
    if couple == 'sit':
        if girl: person(img, 'girl', GIRL_X, hill_y(GIRL_X) + 14, view='back', pose='sit', s=2, shade=shade)
        if boy: person(img, 'boy', BOY_X, hill_y(BOY_X) + 14, view='back', pose='sit', s=2, shade=shade)
    elif couple == 'stand':
        if girl: person(img, 'girl', GIRL_X, hill_y(GIRL_X) + 2, view='back', s=2, shade=shade)
        if boy: person(img, 'boy', BOY_X, hill_y(BOY_X) + 2, view='back', s=2, shade=shade)


# ================================================================ 片头
HEART_C, HEART_S = (240, 112), 3.4


YY, XX = np.mgrid[0:H, 0:W]


def hpt(a, s=HEART_S, c=HEART_C):
    return (c[0] + 16 * math.sin(a) ** 3 * s, c[1] - (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) * s)


ZIG = [(0, -5), (2, -2), (-2, 1), (2, 4), (-1, 7), (2, 10), (-1, 13), (1, 15), (0, 17)]


def heart_halves(s, c):
    """沿着锯齿裂缝分开的左右两半心"""
    right = [hpt(a, s, c) for a in np.linspace(0, math.pi, 40)]
    left = [hpt(a, s, c) for a in np.linspace(math.pi, 2 * math.pi, 40)]
    zig = [(c[0] + x * s * 0.5, c[1] + y * s) for x, y in ZIG]
    return left + zig, right + zig[::-1]


def title_glyph_pos(scale=4, cx=240):
    s, adv, tot = title_layout(scale)
    x = cx - tot / 2 - 4 * scale
    out = []
    for c, a in zip(s, adv):
        out.append((c, x, a)); x += a
    return out


TITLE_Y = 88


def draw_title(img, d, T, state, scale=4, cy=TITLE_Y):
    """state(i) 返回 (显现 0..1, 下落位移, 透明度)"""
    for i, (c, x, a) in enumerate(title_glyph_pos(scale)):
        f, dy, al = state(i)
        if f <= 0 or al <= 0: continue
        g = big_glyph(c, scale)
        dpaste(img, g, x, cy - g.height / 2 + dy, min(al, 1.0))


def s_intro(img, d, lt, dur, T, A):
    b = beats_in(0, 4.0)
    b1 = b[0] if b else 0.34; b2 = b[1] if len(b) > 1 else 1.25; b3 = b[2] if len(b) > 2 else 2.36; b4 = b[3] if len(b) > 3 else 3.49
    # 背景：先全黑，心画完后山坡从点阵里浮出来
    reveal = ease(span(lt, b2 + 0.1, b3 - 0.05))
    img.paste((8, 6, 18), (0, 0, W, H))
    if reveal > 0:
        world = Image.new('RGB', (W, H)); hill_world(world, ImageDraw.Draw(world), T, 0.0)
        r = reveal * 330
        m = ((XX - HEART_C[0]) ** 2 + (YY - HEART_C[1]) ** 2) ** 0.5 < r - BAYER * 18
        img.paste(Image.fromarray(np.where(m[..., None], np.asarray(world), np.asarray(img))))
        if reveal < 1:
            ring = np.abs(((XX - HEART_C[0]) ** 2 + (YY - HEART_C[1]) ** 2) ** 0.5 - r) < 2
            a = np.asarray(img).copy(); a[ring] = RED_L; img.paste(Image.fromarray(a))
    for i in range(30):                         # 黑暗里飘着的微尘
        r = rng(i)
        x = (r.uniform(0, W) + T * r.uniform(-6, 6)) % W; y = (r.uniform(0, H) - T * r.uniform(2, 8)) % H
        if (1 - reveal) > 0.3: d.point((x, y), fill=lerpc((40, 30, 60), (160, 120, 150), 0.5 + 0.5 * math.sin(T * 3 + i)))
    c = HEART_C
    if lt < b3:
        # 红线从心尖上分两路描出一颗心
        f = ease(span(lt, b1, b2))
        if lt < b1:
            k = clamp(lt / b1)
            glow(img, *hpt(0), 10, RED, 0.6 * k); d.rectangle([hpt(0)[0] - 1, hpt(0)[1] - 1, hpt(0)[0], hpt(0)[1]], fill=lerpc((40, 10, 20), RED_L, k))
        else:
            s = HEART_S * (1 + 0.08 * thump(T, 0.3) * (lt > b2))
            n = 60
            ra = [hpt(math.pi * f * j / n, s) for j in range(n + 1)]
            la = [hpt(-math.pi * f * j / n, s) for j in range(n + 1)]
            if lt >= b2:                              # 描完了：心填上红色，跟着拍子跳
                k = lt - b2
                glow(img, c[0], c[1] + 6, 120, RED, 0.35 + 0.25 * thump(T, 0.35))
                d.polygon([hpt(a, s * 1.06) for a in np.linspace(0, 2 * math.pi, 80)], fill=pix.OUT)
                d.polygon([hpt(a, s) for a in np.linspace(0, 2 * math.pi, 80)], fill=lerpc((255, 230, 230), RED, clamp(k / 0.25)))
                d.ellipse([c[0] - 34 * s / HEART_S * 1.0, c[1] - 26, c[0] - 18, c[1] - 12], fill=RED_L)
            for pts in (ra, la):
                d.line(pts, fill=RED, width=3)
                d.line(pts, fill=RED_L)
                if lt < b2:
                    hx, hy = pts[-1]
                    glow(img, hx, hy, 14, RED_L, 0.7)
                    twinkle(d, int(hx), int(hy), 0.5, (255, 240, 240), 4)
                    for j in range(1, 6):                 # 线头后面掉下的小火星
                        px, py = pts[max(0, len(pts) - 1 - j * 3)]
                        d.point((px + math.sin(T * 30 + j) * 2, py + j), fill=lerpc(RED_L, (40, 10, 20), j / 6))
    else:
        # 心裂成两半，往两边飞开
        k = lt - b3
        lh, rh = heart_halves(HEART_S, c)
        if k < 0.12:
            d.polygon([hpt(a) for a in np.linspace(0, 2 * math.pi, 80)], fill=RED)
            d.line([(c[0] + x * HEART_S * 0.5, c[1] + y * HEART_S) for x, y in ZIG], fill=(255, 255, 255), width=2)
            glow(img, c[0], c[1], 90, (255, 240, 240), 0.8)
        else:
            u = ease(clamp((k - 0.12) / 0.75))
            for poly, sgn in ((lh, -1), (rh, 1)):
                ang = sgn * 0.5 * u
                ox, oy = sgn * 190 * u, 50 * u * u
                pts = []
                for x, y in poly:
                    dx, dy = x - c[0], y - c[1]
                    pts.append((c[0] + dx * math.cos(ang) - dy * math.sin(ang) + ox, c[1] + dx * math.sin(ang) + dy * math.cos(ang) + oy))
                if u < 1:
                    d.polygon([(x + 1, y + 1) for x, y in pts], fill=pix.OUT)
                    d.polygon(pts, fill=lerpc(RED, RED_D, u))
            burst(img, d, k, c[0], c[1], life=1.3, scale=1.1)
        # 片名一个字一个字落下来
        def st(i):
            t0 = b3 + 0.08 + i * 0.13
            f = clamp((lt - t0) / 0.32)
            return f, -26 * (1 - eback(f)), f * 3
        draw_title(img, d, T, st)
        for i, (ch, x, a) in enumerate(title_glyph_pos()):
            t0 = b3 + 0.08 + i * 0.13 + 0.32
            if 0 <= lt - t0 < 0.4:
                glow(img, x + 4 * 4 + a / 2, TITLE_Y, 40, (255, 250, 240), 0.6 * (1 - (lt - t0) / 0.4))
                twinkle(d, int(x + a), int(TITLE_Y - 30), (lt - t0) / 0.4, (255, 255, 255), 5)
        # 歌手和下面的红线
        if lt > b4 - 0.1:
            f = ease(span(lt, b4 - 0.1, b4 + 0.5))
            x0, x1 = 120, lerp(120, 360, f)
            d.line([(x0, TITLE_Y + 40), (x1, TITLE_Y + 40)], fill=RED)
            d.line([(x0, TITLE_Y + 41), (x1, TITLE_Y + 41)], fill=RED_D)
            put(img, 'heart', x1 + 4, TITLE_Y + 40, 1)
            ar = artist_str()
            if ar: text(img, ar, 240, TITLE_Y + 58, (255, 240, 236), (56, 22, 50), alpha=f)


s_intro.no_sub = True


# ================================================================ 起风：片名变成云被吹走
def s_wind(img, d, lt, dur, T, A):
    w = ease(span(lt, 0.4, 1.6)) * (0.8 + 0.2 * math.sin(T * 2))
    hill_world(img, d, T, 0.0, wind=w, clouds_x=lt * lt * 18)
    # 片名一个字一个字变成云，被风吹走
    for i, (c, x, a) in enumerate(title_glyph_pos()):
        ts = 0.9 + i * 0.38
        g = big_glyph(c, 4)
        gy = TITLE_Y - g.height / 2
        k = lt - ts
        if k < 0:
            dpaste(img, g, x + math.sin(T * 9 + i) * w * 0.8, gy)
            continue
        cg = cloud_glyph(c, 4)
        mo = clamp(k / 0.45)
        dx = 260 * ein(clamp(k / 2.2)) + 30 * k
        if mo < 1: dpaste(img, g, x + dx, gy, 1 - mo)
        dpaste(img, cg, x + dx - 6, gy - 4 + 4 * math.sin(k * 3), mo * clamp(1 - (k - 1.6) / 0.8))
        if k < 0.6:
            for j in range(6):
                r = rng(i * 10 + j)
                px = x + a / 2 + 10 + r.uniform(-24, 24) + k * 60; py = TITLE_Y + r.uniform(-24, 24)
                d.point((px, py), fill=(255, 250, 250))
    # 一道道风，飘过的花瓣和鸟
    winds(d, T, int(4 + 10 * w), (255, 236, 236), 360, 20, 220)
    pix.petals(d, T, int(30 * w), speed=14, wind=160, seed=3)
    for j in range(5):
        bx = (T * 50 + j * 26) % (W + 60) - 30; by = 150 + j * 6 - (j % 2) * 10 + 4 * math.sin(T * 2 + j)
        pix.bird(d, int(bx), int(by), T, (70, 50, 80), j)
    # 云：大团的云被风推着往右跑
    for i in range(4):
        r = rng(i + 7)
        x = -140 + (lt * r.uniform(70, 110) + r.uniform(-60, 200)) % (W + 280)
        y = r.uniform(20, 70)
        cloud(d, x, y, r.uniform(1.4, 2.2), (255, 220, 222), (238, 170, 184), (255, 246, 246))


# ================================================================ 乌云和天上的裂口
def rift_edges(lt, cx=240, y0=4, y1=168, n=40):
    """裂口的左右边缘（锯齿），宽度随时间张开"""
    w = 66 * ease(span(lt, 2.7, 5.6)) + 4 * eout(span(lt, 1.6, 2.7))
    L, R = [], []
    for j in range(n + 1):
        u = j / n
        y = lerp(y0, y1, u)
        jag = ((j * 37) % 7 - 3) * 1.6
        base = cx + 6 * math.sin(u * 5)
        half = w * math.sin(math.pi * u) ** 0.8
        L.append((base - half + jag * (0.4 + half / 40), y)); R.append((base + half + jag * 0.6 * (0.4 + half / 40), y))
    return L, R


def bolt(d, x0, y0, x1, y1, seed, col=(255, 255, 255), n=8):
    r = rng(seed)
    pts = [(x0, y0)]
    for j in range(1, n):
        u = j / n
        pts.append((lerp(x0, x1, u) + r.uniform(-14, 14), lerp(y0, y1, u)))
    pts.append((x1, y1))
    d.line(pts, fill=(200, 210, 255), width=3); d.line(pts, fill=col)
    return pts


def s_rift(img, d, lt, dur, T, A):
    mood = ease(span(lt, 0.0, 2.2))
    stand = lt > 2.4
    hill_world(img, d, T, mood, wind=0.6 + 0.3 * mood, couple='stand' if stand else 'sit', kite_on=lt < 2.6,
               clouds_x=60 + lt * 30)
    # 乌云从两边压过来
    for i in range(7):
        r = rng(i * 3 + 1)
        side = -1 if i % 2 else 1
        x = 240 + side * (420 - 300 * ease(span(lt, 0.2 + i * 0.1, 2.6 + i * 0.1))) + r.uniform(-60, 60) - 30 * 2
        y = r.uniform(-10, 70)
        s = r.uniform(2.4, 3.6)
        cloud(d, x - 14 * s, y, s, (44, 40, 66), (32, 28, 50), (70, 66, 98))
    # 裂缝和裂口
    if lt > 1.5:
        L, R = rift_edges(lt)
        w = ease(span(lt, 2.7, 5.6))
        if w > 0:
            poly = L + R[::-1]
            glow(img, 240, 80, 120 + 60 * w, (255, 236, 200), 0.3 + 0.35 * w, 110)
            d.polygon(poly, fill=(30, 14, 56))
            # 裂口里面：另一片星空
            m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(poly, fill=255)
            inner = Image.new('RGB', (W, H), (34, 16, 64)); di = ImageDraw.Draw(inner)
            for j in range(6):
                glow(inner, 240 + 20 * math.sin(T + j), 30 + j * 20, 30, [(140, 90, 255), (255, 120, 180), (110, 200, 255)][j % 3], 0.5)
            stars(di, T * 2, H, 1.0, 200, ox=int(T * 20), base=(40, 20, 80))
            img.paste(inner, (0, 0), m)
            for pts in (L, R):
                d.line(pts, fill=(255, 246, 220), width=2)
                d.line([(x + (2 if pts is R else -2), y) for x, y in pts], fill=(255, 200, 150))
            # 光柱照到山坡上的两个人
            tfill(img, 'polygon', [(226, 150), (256, 150), (300, 250), (170, 250)], (255, 236, 200), 0.18 * w)
            # 碎掉的天空碎片往外飞
            for j in range(18):
                r = rng(j + 50)
                k = (lt * 0.8 + r.random()) % 1
                side = -1 if j % 2 else 1
                y = r.uniform(20, 140)
                x = 240 + side * (8 + w * 40 + k * 120)
                d.rectangle([x, y - k * 20, x + 2, y - k * 20 + 2], fill=lerpc((200, 150, 200), (60, 50, 90), k))
        else:
            f = eout(span(lt, 1.5, 2.6))
            n = int(len(L) * f)
            pts = [((a[0] + b[0]) / 2, a[1]) for a, b in zip(L[:n + 1], R[:n + 1])]
            if len(pts) > 1:
                glow(img, 240, 70, 60, (255, 240, 220), 0.4)
                d.line(pts, fill=(255, 250, 230), width=2)
    # 闪电踩在拍子上
    for bt in beats_in(T - 0.25, T + 0.01):
        k = T - bt
        if lt > 2.6 and k < 0.25:
            seed = int(bt * 10)
            r = rng(seed)
            bolt(d, 240 + r.uniform(-20, 20), 120, r.choice([60, 120, 360, 420]) + r.uniform(-30, 30), r.uniform(170, 220), seed)
            if k < 0.08: pix.blend_box(img, (0, 0, W, H), (240, 236, 255), np.full((H, W), 0.45))
    if lt > 2.7: shake(img, lt - 2.7, 3, 0.6)


# ================================================================ 雨里只剩他一个人
RAIN_SKY = ((0, (20, 22, 40)), (0.5, (44, 52, 80)), (1, (70, 80, 106)))


def s_rain(img, d, lt, dur, T, A):
    cut = 3.3
    if lt < cut:
        # 远景：雨里的山坡，只剩他一个人站在树下
        hill_world(img, d, T, 1.0, wind=0.5, couple='stand', kite_on=False, girl=False, sun=False)
        L, R = rift_edges(9.0)
        heal = ease(span(lt, 0, 2.5))
        mid = [((a[0] + b[0]) / 2, a[1]) for a, b in zip(L, R)]
        d.line(mid, fill=lerpc((255, 240, 220), (70, 66, 96), heal), width=2)     # 裂口合上，只剩一道疤
        pix.rain(d, T, 0, W + 40, -10, H, 260, (120, 136, 180), 360, -6, 7, 1)
        pix.rain(d, T, 0, W + 40, -10, H, 140, (170, 184, 220), 460, -8, 9, 2)
        props.splashes(d, T, 236, 268, 40, (150, 166, 210))
        # 她原来坐的地方掉着一根红线
        d.line([(GIRL_X - 8, hill_y(GIRL_X) + 1), (GIRL_X + 4, hill_y(GIRL_X) + 2), (GIRL_X + 10, hill_y(GIRL_X))], fill=RED)
        darken(img, 0.15 * (1 - lt / cut), (10, 10, 30))
    else:
        # 特写：雨水顺着他的脸往下流
        k = lt - cut
        sky(img, RAIN_SKY)
        props.bokeh(img, T, 16, [(90, 110, 170), (140, 120, 190), (80, 140, 170)], 4, 0.3, 10, 26, 4)
        pix.rain(d, T, 0, W + 40, -10, H, 120, (70, 84, 120), 300, -5, 6, 3)
        z = 7
        top = 30 + 2 * math.sin(k * 0.8)
        (lx, ly), (rx, ry) = bust(img, d, 'boy', 240, top, z, 'cry' if (k % 2.6) < 2.0 else 'sad')
        # 眼角流下来的泪和脸上的雨水
        for j in range(4):
            r = rng(j + 90)
            per = r.uniform(1.4, 2.2)
            u = ((k + r.random() * per) % per) / per
            ex = [lx, rx, lx - 3 * z, rx + 3 * z][j] + r.uniform(-2, 2)
            ey0 = ly + z
            ey = ey0 + u * 6 * z
            if u < 0.85:
                if j < 2: d.line([(ex, ey0), (ex, ey)], fill=(176, 204, 240), width=2)
                d.rectangle([ex - 2, ey, ex + 2, ey + 5], fill=(190, 218, 255)); d.point((ex - 1, ey + 1), fill=(255, 255, 255))
        # 前景几颗大雨点慢慢落下
        for j in range(7):
            r = rng(j + 120)
            per = r.uniform(1.4, 2.2)
            u = ((k + r.random() * per) % per) / per
            x = r.uniform(20, 460); y = -20 + u * (H + 40)
            s = r.choice([2, 3])
            put(img, 'drop', x, y, s, tint=(170, 196, 246), alpha=0.85)
            d.point((x - s // 2, y - s), fill=(255, 255, 255))
        grade(img, 0.75, (0.92, 0.96, 1.08))
    vig(img, 0.45, (8, 8, 24))


# ================================================================ 俯视：雨水汇成小溪
@lru_cache(None)
def stream_net():
    """从画面上方很多源头往下汇到一条主干的水系：返回 [(点列, 粗细, 开始时间)]"""
    segs = []

    def grow(x, y, ang, depth, seed):
        r = rng(seed)
        ln = 22 + depth * 9
        pts = [(x, y)]
        a = ang
        for j in range(8):
            a += r.uniform(-0.35, 0.35)
            x += math.sin(a) * ln / 8; y -= math.cos(a) * ln / 8
            pts.append((x, y))
        segs.append((pts, depth, seed))
        if depth > 0:
            grow(x, y, ang - r.uniform(0.45, 0.85), depth - 1, seed * 2 + 1)
            grow(x, y, ang + r.uniform(0.45, 0.85), depth - 1, seed * 2 + 2)
    grow(240, 290, 0.0, 5, 1)
    return segs


def s_streams(img, d, lt, dur, T, A):
    # 俯视的泥地：小石子、落叶，雨点打出一个个小坑
    img.paste((58, 50, 52), (0, 0, W, H))
    for i in range(260):
        r = rng(i + 300)
        x, y = r.uniform(0, W), r.uniform(0, H)
        c = r.choice([(74, 64, 64), (46, 40, 44), (86, 78, 74), (66, 74, 60)])
        d.rectangle([x, y, x + r.randint(1, 3), y + r.randint(1, 2)], fill=c)
    for i in range(14):
        r = rng(i + 500)
        x, y = r.uniform(0, W), r.uniform(0, H)
        d.polygon([(x, y), (x + 4, y - 2), (x + 7, y + 1), (x + 3, y + 3)], fill=r.choice([(160, 120, 70), (196, 150, 80), (120, 140, 70)]))
    # 水从细枝流到主干
    segs = stream_net()
    fill_t = lambda depth: 0.1 + depth * 0.42
    for pts, depth, seed in sorted(segs, key=lambda s: s[1]):
        t0 = fill_t(depth)
        f = clamp((lt - t0) / 0.45)
        if f <= 0: continue
        wd = 1 + depth * 1.1 + (2 if depth == 5 else 0)
        rev = pts[::-1]                              # 水从上游往下游流
        n = max(2, int(len(rev) * f))
        part = rev[:n]
        d.line([(x, y + 1) for x, y in part], fill=(34, 40, 60), width=int(wd + 2))
        d.line(part, fill=(70, 120, 190), width=int(wd + 1))
        d.line(part, fill=(110, 170, 236), width=max(1, int(wd - 1)))
        for j in range(len(part) - 1):               # 水面上流动的亮点
            if (j + int(T * 12)) % 4 == 0:
                x, y = part[j]
                d.point((x, y), fill=(220, 240, 255))
        if f < 1:
            x, y = part[-1]; glow(img, x, y, 6, (150, 200, 255), 0.6)
    # 源头的雨点
    for i in range(50):
        r = rng(i + 700)
        per = r.uniform(0.5, 0.9)
        k = ((T + r.random() * per) % per) / per
        x, y = r.uniform(0, W), r.uniform(0, H)
        rr = 1 + k * 5
        d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=lerpc((180, 200, 240), (58, 50, 52), k))
    # 主干上漂来一只纸船
    main = [p for p, dep, s in segs if dep == 5][0][::-1]
    f = clamp((lt - 2.3) / 1.4)
    if f > 0:
        x, y = main[min(len(main) - 1, int(f * (len(main) - 1)))]
        paper_boat(d, x, y + 4, 1, bob=math.sin(T * 5))
    vig(img, 0.5, (16, 12, 20))


# ================================================================ 雨后的大河和纸船
DUSK = ((0, (30, 34, 80)), (0.45, (92, 82, 140)), (0.8, (220, 140, 150)), (1, (255, 196, 160)))


def s_river(img, d, lt, dur, T, A):
    hz = 112
    sky(img, DUSK, 0, hz + 1)
    stars(d, T, 60, 0.6, 60)
    moon(d, 360, 40, 9); glow(img, 360, 40, 30, (255, 240, 210), 0.3)
    for i, (cx, cy, s) in enumerate([(40, 64, 1.4), (200, 78, 1.0), (330, 70, 1.6)]):
        cloud(d, (cx + T * 4) % (W + 80) - 40, cy, s, (196, 136, 170), (164, 110, 150))
    pix.hills(d, hz - 6, 4, 0.02, 0.4, (84, 70, 120))
    pix.hills(d, hz, 3, 0.03, 2.0, (60, 56, 96))
    cam = lt * 9
    skyarr = np.asarray(img)
    for y in range(hz, H):
        sc = (y - hz) / (H - hz)
        z = 30 / max(0.04, sc) + cam
        cx = 240 + (math.sin(z * 0.045) * 150 + math.sin(z * 0.017 + 1) * 60) * sc - math.sin(cam * 0.045) * 150 * sc * 0.0
        hw = 6 + 190 * sc
        bank = lerpc((64, 58, 96), (30, 46, 50), sc)
        d.line([(0, y), (W, y)], fill=bank)
        ry = max(0, min(hz - 1, 2 * hz - y))
        wc = tuple(int(v) for v in skyarr[ry, int(clamp(cx, 0, W - 1))])
        wc = lerpc(wc, (40, 50, 96), 0.25 + 0.2 * sc)
        d.line([(cx - hw, y), (cx + hw, y)], fill=wc)
        # 波光
        if (int(z * 2) + y) % 5 == 0:
            for k in range(3):
                px = cx + math.sin(z * 0.7 + k * 2.1 + T) * hw * 0.8
                d.line([(px, y), (px + 2 + 6 * sc, y)], fill=lerpc(wc, (255, 236, 220), 0.5))
        # 岸边的草和芦苇
        if (int(z) % 6 == 0) and sc > 0.1:
            for sx in (cx - hw - 3, cx + hw + 3):
                hgt = int(3 + 10 * sc)
                d.line([(sx, y), (sx + math.sin(T * 2 + z) * 1.5, y - hgt)], fill=(70, 90, 70))
                d.point((sx, y - hgt), fill=(150, 130, 90))
    # 雾
    pix.blend_box(img, (0, hz - 4, W, hz + 26), (200, 170, 200), np.tile(np.linspace(0.45, 0, 30)[:, None], (1, W)))
    # 纸船
    y = 226
    sc = (y - hz) / (H - hz); z = 30 / sc + cam
    bx = 240 + (math.sin(z * 0.045) * 150 + math.sin(z * 0.017 + 1) * 60) * sc
    for k in range(4):
        rr = 6 + ((T * 12 + k * 6) % 24)
        d.arc([bx - rr, y - rr * 0.3, bx + rr, y + rr * 0.3], 0, 180, fill=lerpc((200, 210, 255), (60, 70, 120), rr / 30))
    paper_boat(d, bx, y, 2, bob=math.sin(T * 3) * 1.5)
    d.line([(bx - 4, y - 14), (bx + 4, y - 14)], fill=RED)        # 船帆上系着一截红线
    pix.fireflies(img, d, T, 14, (0, hz + 10, W, H), (255, 236, 150), 5)
    vig(img, 0.4, (14, 10, 30))
