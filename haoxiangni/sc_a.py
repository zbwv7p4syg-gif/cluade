"""我好想你 · 片头和第一段主歌。签名都是 (img, d, lt, dur, T, A)：lt 是镜头内的时间，dur 是镜头时长，T 是全片时间，A 是这一帧的音量。

片头：夜里的楼顶，"我"围着那条红围巾坐在楼沿上，从手心放出一点光；光升进夜空，在音乐进来的那一拍炸开，
满天的星屑飞回来拼成片名；片名散成星屑落进城里，镜头落回一扇没开灯的窗。
主歌：开灯（眼前浮出"你"的样子）、偌大的房和半边空着的床、关灯（每一夜都一个样）、说不出口的伤、
树下长椅上四季飞转头发变白、站台上列车开走和空信箱、褪色的拍立得和梦、变灰飘远的心。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
from props import *          # noqa: F401,F403
from pix import (W, H, FONT, FONT_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky, stars,
                 person, wph, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, BAYER, city, put)

# ================================================================ 片头
TS = 5                                         # 片名每个像素放大成 5×5 的方块
TITLE_CY = 100
BURST = 12.69                                  # 音乐进来的小节线
RELEASE = 22.19
ROOM_AT = 28.53


@lru_cache(None)
def title_cells():
    """片名拆成一格一格：[(屏幕 x, 屏幕 y, 颜色, 横向位置 0..1, 纵向位置 0..1, 随机数, 随机数)]"""
    s = title_str()
    ims = [big_glyph(c, 1, top=(255, 255, 250), bot=(255, 176, 196), line=(232, 64, 116), out=(58, 14, 52)) for c in s]
    adv = [int(FONT.getlength(c)) + 3 for c in s]
    tw = sum(adv) + ims[-1].width - adv[-1]
    th = max(im.height for im in ims)
    ox = W / 2 - tw * TS / 2; oy = TITLE_CY - th * TS / 2
    cells = []; x = 0; r = rng(5)
    for im, a in zip(ims, adv):
        arr = np.array(im)
        for py in range(arr.shape[0]):
            for px in range(arr.shape[1]):
                if arr[py, px, 3] > 0:
                    cells.append((ox + (x + px) * TS, oy + py * TS, tuple(int(v) for v in arr[py, px, :3]), (x + px) / tw, py / th, r.random(), r.random()))
        x += a
    return cells


def roof_bg(img, d, T, oy):
    """夜空、月亮、远处的城和近处的楼顶。oy 是镜头往上抬的像素数（地面上的东西往下移）"""
    sky(img, NIGHT4, 0, H, 6)
    stars(d, T, H, 1.0, 240, 0, -int(oy * 0.6))
    mx, my = 352, 70 + oy
    if my < H + 90:
        glow(img, mx, my, 84, (170, 186, 255), 0.32); moon(d, mx, my, 30)
        for i, (cx, cy, w) in enumerate(((296, 92, 60), (372, 58, 44), (326, 48, 30))):
            x = cx + 8 * math.sin(T * 0.1 + i)
            tfill(img, 'rectangle', [x, cy + oy, x + w, cy + oy + 2], (200, 206, 255), 0.25)
    city(img, d, 240 + oy, 3, 0, (36, 38, 84), win=(255, 214, 130), hmin=28, hmax=84, frac=0.32, T=T)
    city(img, d, 268 + oy, 7, 30, (22, 22, 54), win=(255, 186, 110), hmin=18, hmax=52, frac=0.22, T=T)
    ry = 226 + oy
    d.rectangle([0, ry, 216, H + 300], fill=(24, 22, 48))
    d.rectangle([0, ry - 6, 220, ry], fill=(46, 44, 84)); d.line([(0, ry - 6), (220, ry - 6)], fill=(84, 84, 140))
    d.rectangle([28, ry - 56, 70, ry - 26], fill=(34, 32, 66)); d.polygon([(24, ry - 56), (74, ry - 56), (49, ry - 68)], fill=(40, 38, 76))
    for lx in (32, 64): d.line([(lx, ry - 26), (lx, ry - 6)], fill=(34, 32, 66), width=2)
    d.line([(28, ry - 44), (70, ry - 44)], fill=(52, 50, 96))
    d.line([(110, ry - 6), (110, ry - 50)], fill=(40, 38, 76)); d.line([(102, ry - 44), (118, ry - 44)], fill=(40, 38, 76))
    d.line([(105, ry - 36), (115, ry - 36)], fill=(40, 38, 76))
    d.rectangle([134, ry - 20, 158, ry - 6], fill=(38, 36, 72)); d.ellipse([140, ry - 18, 152, ry - 8], outline=(60, 58, 104))
    return ry


def scarf_tail(d, x, y, T, n=16, s=2, flip=False):
    """被风吹起来的红围巾"""
    for i in range(n):
        px = x - (8 + i * 2) * (-1 if flip else 1) * s / 2
        py = y + 2 * math.sin(T * 4 - i * 0.55) * (i / n) * s / 2 + i * 0.25
        d.rectangle([px, py, px + s - 1, py + s], fill=SCARF if i < n - 4 else SCARF_D)


def light_pos(lt, oy):
    """片头那点光的屏幕坐标"""
    f = span(lt, 3.24, BURST - 0.25)
    wx = lerp(234, 240, f) + 14 * math.sin(f * 10) * (1 - f)
    wy = lerp(198, TITLE_CY - 130, ease(f))
    return wx, wy + oy


def intro_roof(img, d, lt):
    T = lt
    if lt < RELEASE: oy = 130 * ease(span(lt, 5.5, 12.0))
    else: oy = 130 * (1 - ease(span(lt, RELEASE + 0.4, RELEASE + 4.6)))
    ry = roof_bg(img, d, T, oy)
    # 流星
    pix.meteor(d, lt, 1.2, 60, 20, 150, 60, life=0.8)
    for i, b in enumerate(beats_in(BURST + 1, RELEASE + 3)):
        if i % 2 == 0:
            r = rng(i * 3 + 1)
            pix.meteor(d, lt, b, r.uniform(20, 380), r.uniform(0, 60), r.uniform(60, 110), r.uniform(30, 60), life=0.7)
    # 坐在楼沿上的"我"
    x, y = 210, ry - 6 + 18
    hold = 1.4 < lt < 4.4
    scarf_tail(d, x, y - 31, T)
    person(img, 'boy', x, y, view='side', pose='sit', expr='closed' if lt > BURST + 2 else 'sad', arms='reach' if hold else 'lap', s=2, scarf=SCARF)
    # 手心里的光，升进夜空
    if 1.4 < lt < 3.24:
        k = span(lt, 1.4, 3.0)
        glow(img, 228, y - 26, 6 + 10 * k, (255, 200, 170), 0.6 * k); put(img, 'heart', 228, y - 27, 1)
    elif 3.24 <= lt < BURST:
        f = span(lt, 3.24, BURST - 0.25)
        for k in range(1, 14):
            px, py = light_pos(lt - k * 0.07, oy)
            if lt - k * 0.07 > 3.24 and (k + int(lt * 20)) % 2 == 0:
                d.point((px + math.sin(k * 2.1 + lt * 3) * 2, py), fill=lerpc((255, 236, 200), (90, 70, 140), k / 14))
        px, py = light_pos(lt, oy)
        glow(img, px, py, 16 + 10 * f + 3 * math.sin(lt * 6), (255, 190, 170), 0.55 + 0.3 * f)
        put(img, 'heart', px, py, 2 if f > 0.6 else 1)
        twinkle(d, int(px), int(py), (lt * 1.6) % 1, size=3 + int(4 * f))
    # 片名
    cells = title_cells()
    if lt >= BURST:
        k = lt - BURST
        cx, cy = W / 2, TITLE_CY
        if k < 1.2:
            rr = 320 * eout(k / 1.2)
            d.ellipse([cx - rr, cy - rr * 0.7, cx + rr, cy + rr * 0.7], outline=lerpc((255, 240, 230), (60, 50, 120), k / 1.2))
        if lt < RELEASE + 2.5:
            pl = thump(lt, 0.35) if lt > BURST + 2.6 else 0
            ga = clamp(k / 2.5) * (1 - span(lt, RELEASE, RELEASE + 1.2))
            glow(img, cx, cy + oy - 130, 230, (255, 110, 160), (0.2 + 0.1 * pl) * ga, ry=96)
        for (tx, ty, col, u, v, r1, r2) in cells:
            ty += oy - 130
            f = ease(span(k, r1 * 0.35, 1.5 + u * 0.9 + r2 * 0.3))
            size = TS
            if f < 1:
                a = r1 * 6.283; rad = 90 + 150 * r2
                mx_, my_ = cx + math.cos(a) * rad * 1.5, cy + math.sin(a) * rad
                x_ = (1 - f) ** 2 * cx + 2 * f * (1 - f) * mx_ + f * f * tx
                y_ = (1 - f) ** 2 * cy + 2 * f * (1 - f) * my_ + f * f * ty
                c = lerpc((255, 250, 236), col, f ** 2)
                size = 2 + int(3 * f)
            else:
                x_, y_, c = tx, ty, col
                if lt >= RELEASE:
                    kk = lt - RELEASE - (r1 * 1.3 + (1 - v) * 0.7)
                    if kk > 0:
                        y_ = ty + 30 * kk + 70 * kk * kk
                        x_ = tx + 7 * math.sin(kk * 3 + r2 * 6.283)
                        c = lerpc(col, (255, 240, 226), clamp(kk * 2))
                        size = max(1, TS - int(kk * 8))
                        if kk > 0.6 and (int(lt * 12) + int(r2 * 9)) % 3 == 0: continue
                        if y_ > H: continue
            d.rectangle([x_, y_, x_ + (size - 1), y_ + (size - 1)], fill=c)
        # 字上的闪光、歌手
        if BURST + 2.6 < lt < RELEASE:
            for i in range(5):
                r = rng(i * 7 + int(lt / 0.7 + i * 0.37))
                twinkle(d, int(r.uniform(70, 410)), int(r.uniform(50, 150)), ((lt + i * 0.37) / 0.7) % 1, size=4)
            a = span(lt, 15.85, 16.6) * (1 - span(lt, RELEASE - 0.5, RELEASE))
            if a > 0:
                ar = artist_str()
                text(img, ar, W / 2, 178, col=(240, 230, 255), alpha=a)
                wd = FONT.getlength(ar) / 2 + 12
                for sx in (-1, 1):
                    d.line([(W / 2 + sx * wd, 178), (W / 2 + sx * (wd + 26 * a), 178)], fill=(200, 170, 230))
                    put(img, 'heart', W / 2 + sx * (wd + 34), 178 + round(thump(lt, 0.3) * -2), 1, alpha=a)
        if k < 0.6: blend_box(img, (0, 0, W, H), (255, 244, 236), np.full((H, W), (1 - k / 0.6) ** 2))
    # 一开场左下角先报上歌名
    ca = span(lt, 0.5, 1.1) * (1 - span(lt, 5.0, 5.8))
    if ca > 0:
        x0 = 22 - round(10 * (1 - eout(span(lt, 0.5, 1.1))))
        tfill(img, 'rectangle', [x0 - 6, 196, x0 + 158, 258], (10, 8, 30), 0.5 * ca)
        d.rectangle([x0 - 6, 196, x0 - 4, 258], fill=lerpc((10, 8, 30), SCARF, ca))
        put(img, 'heart', x0 + 8, 216 - round(2 * thump(lt, 0.3)), 2, alpha=ca)
        im = pix.text_img(title_str(), (255, 250, 240)); im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
        dpaste(img, im, x0 + 14, 194, ca)
        dpaste(img, pix.text_img(artist_str(), (214, 206, 240), pix.TXT_OUT, FONT_S), x0 + 20, 238, ca)
    if lt < 0.6: dither_fade(img, 1 - eout(lt / 0.6))


def intro_room(img, d, t):
    # 按小节线切三次，一次比一次近：整间屋子 → 床边 → 月光里的人
    z = 1 if t < 31.66 - ROOM_AT else (2 if t < 34.82 - ROOM_AT else 3)
    blink = int(t * 30) % 96 < 5
    room(img, d, t, me='edge', lamp=0.0, expr='closed' if blink else ('down' if t < 8.0 else 'neutral'), me_arms='reach' if t > 9.3 else 'auto')
    for i in range(26):                         # 月光里飘着的微尘
        r = rng(i * 7 + 2)
        k = (t * (0.04 + 0.05 * r.random()) + r.random()) % 1
        x = lerp(330, 286, k) + r.uniform(0, 70); y = 150 + k * 86
        if math.sin(t * 2 + i) > 0: d.point((x + 3 * math.sin(t + i), y), fill=(200, 210, 255))
    if z == 2: zoom(img, 2, 232, 118)
    elif z == 3: zoom(img, 3, 262, 128)
    vig(img, 0.5)


def s_intro(img, d, lt, dur, T, A):
    shots(img, lt, [(0, intro_roof), (ROOM_AT, intro_room)], tr=1.2)


# ================================================================ 开了灯 眼前的模样
def s_lamp_on(img, d, lt, dur, T, A):
    on = 1.0 if lt > 0.1 and not 0.2 < lt < 0.26 else 0.0
    ga = ease(span(lt, 0.7, 1.6)) * (1 - ease(span(lt, 3.1, 4.2)))
    room(img, d, T, me='edge', lamp=on, expr='surprised' if 0.9 < lt < 2.0 else ('sad' if lt > 2 else 'neutral'), ghost_sit=ga,
         me_arms='reach' if lt < 0.5 else 'auto')
    if lt > 3.0:                               # "你"的样子散成光点
        for i in range(26):
            r = rng(i * 11)
            k = lt - 3.0 - r.random() * 0.6
            if k <= 0 or k > 1.2: continue
            px = 300 + r.uniform(-8, 8) + 6 * math.sin(k * 5 + i); py = 166 - r.uniform(0, 28) - k * 26
            d.point((px, py), fill=lerpc((255, 240, 190), (120, 100, 90), k / 1.2))
    zoom(img, 2, 236, 118)
    if 0.1 < lt < 0.5:
        for a in range(6):
            an = a * 1.047 + 0.3; r0, r1 = 26 + 40 * (lt - 0.1), 34 + 50 * (lt - 0.1)
            d.line([(332 + math.cos(an) * r0, 36 + math.sin(an) * r0), (332 + math.cos(an) * r1, 36 + math.sin(an) * r1)], fill=(255, 244, 200))


# ================================================================ 偌大的房 寂寞的床
def s_big_room(img, d, lt, dur, T, A):
    gl = ease(span(lt, 3.4, 4.6)) * (1 - ease(span(lt, 5.6, 7.2)))
    room(img, d, T, me='lie', lamp=1.0, expr='neutral' if lt < 5.2 else 'down', ghost_lie=gl)
    e = ease(span(lt, 0.4, 3.0))
    zoomf(img, lerp(2, 1, e), lerp(236, 240, e), lerp(118, 135, e))
    vig(img, 0.3 + 0.25 * span(lt, 1, 4))


# ================================================================ 关了灯 全都一个样
NIGHTS = ['周一', '周二', '周三', '周四', '周五', '周六']


def s_lamp_off(img, d, lt, dur, T, A):
    room(img, d, T, me='lie', lamp=1.0 if lt < 0.3 else 0.0, expr='neutral', eyes=int(T * 0.7) % 4 != 0)
    t0 = 1.5
    if lt > t0:
        small = img.resize((150, 84), Image.BOX)
        img.paste((8, 8, 22), (0, 0, W, H))
        for i in range(6):
            a = lt - t0 - i * 0.38
            if a < 0: continue
            x = 9 + (i % 3) * 156; y = 34 + (i // 3) * 104 + round(6 * (1 - eout(a / 0.2)))
            img.paste(small, (x, y))
            d.rectangle([x - 1, y - 1, x + 150, y + 84], outline=(86, 92, 150))
            d.rectangle([x - 1, y - 15, x + 30, y - 1], fill=(86, 92, 150))
            text(img, NIGHTS[i], x + 15, y - 8, col=(230, 232, 255), out=None, font=FONT_S, shadow=False)
            put(img, 'zz', x + 138, y + 10 + round(math.sin(T * 2 + i)), 1, alpha=0.7)


# ================================================================ 心里的伤 无法分享
def s_wound(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(16, 16, 40))
    # 身后暗着的房间：窗和月光
    d.rectangle([330, 20, 440, 130], fill=(30, 34, 80)); d.rectangle([384, 20, 386, 130], fill=(16, 16, 40)); d.rectangle([330, 74, 440, 76], fill=(16, 16, 40))
    moon(d, 410, 48, 10)
    bokeh(img, T, 8, seed=4, a=0.12, box=(0, 0, W, 180))
    cx = 150
    expr = 'closed' if lt > 4.6 else 'sad'
    bust(img, d, 'boy', cx, 34, 4, expr)
    pl = thump(T, 0.3)
    hy = 214
    lighting(img, [(cx, hy, 120, 0.75 + 0.25 * pl), (385, 75, 120, 0.5)], amb=0.3, tint=(0.3, 0.3, 0.52))
    glow(img, cx, hy, 46 + 8 * pl, (255, 90, 100), 0.4 + 0.2 * pl)
    for i, b in enumerate(beats_in(T - 1.2, T + 0.01)):       # 每跳一下荡开一圈
        k = (T - b) / 1.2; rr = 20 + 50 * k
        d.ellipse([cx - rr, hy - rr * 0.8, cx + rr, hy + rr * 0.8], outline=lerpc((255, 120, 130), (40, 30, 60), k))
    heart(d, cx, hy - 4, 1.25 + 0.1 * pl, crack=span(lt, 0.2, 1.4), bandage=True)
    # 话到嘴边，又咽回去
    a = eback(span(lt, 0.9, 1.2)) * (1 - span(lt, 4.6, 5.3))
    if a > 0.05:
        bx0, by0 = 252, 96
        bubble(img, d, bx0, by0, bx0 + 150, by0 + 46, tail=(240, 164), a=clamp(a))
        if a > 0.9:
            if lt < 3.3:
                s = '其实我……'[:max(0, int((lt - 1.3) / 0.22))]
                props_text_l(img, s, bx0 + 16, by0 + 23)
                if 2.7 < lt: d.line([(bx0 + 14, by0 + 24), (bx0 + 14 + 100 * span(lt, 2.7, 3.1), by0 + 24)], fill=(200, 70, 80), width=2)
            else:
                s = '没事。'[:max(0, int((lt - 3.4) / 0.2) + 1)]
                props_text_l(img, s, bx0 + 16, by0 + 23)
    if lt > 4.8:                               # 一滴泪
        k = (lt - 4.8)
        ty = 34 + 15 * 4 + min(60, k * 50)
        d.rectangle([cx - 5 * 4 - 4, ty, cx - 5 * 4 - 2, ty + 3], fill=(150, 200, 255))
    vig(img, 0.5)


def props_text_l(img, s, x, y, col=(60, 50, 70), font=None):
    """泡泡里的字：靠左、不描边"""
    if not s: return
    im = pix.text_img(s, col, None, font, False)
    img.paste(im, (int(x) - 3, int(y) - im.height // 2), im)


# ================================================================ 生命 随年月流去 随白发老去
LEAF = [((255, 170, 196), (255, 214, 226)), ((64, 150, 84), (98, 186, 96)), ((222, 120, 50), (246, 180, 74)), ((214, 222, 238), (250, 250, 255)),
        ((214, 222, 238), (250, 250, 255))]
GROUND = [(124, 186, 116), (84, 160, 92), (196, 164, 96), (232, 236, 246), (232, 236, 246)]


def day_cycle(p):
    """一天里的天空：p 0..1（0 清晨，0.25 正午，0.5 黄昏，0.75 深夜），返回 (渐变, 夜的程度)"""
    seq = [DAWN4, DAY4, DAY4, DUSK4, NIGHT4, NIGHT4, NIGHT4, DAWN4]
    k = (p % 1) * 8; i = int(k) % 8
    st = mix_stops(seq[i], seq[(i + 1) % 8], k - int(k), 12)
    night = clamp(1 - abs(((p % 1) - 0.72) / 0.24)) if 0.48 < (p % 1) < 0.96 else 0
    return st, night


def season_cols(sf):
    i = int(clamp(sf, 0, 3.999)); f = ease(clamp((sf - i - 0.6) / 0.4))
    return lerpc(LEAF[i][0], LEAF[i + 1][0], f), lerpc(LEAF[i][1], LEAF[i + 1][1], f), lerpc(GROUND[i], GROUND[i + 1], f)


def calendar(img, d, x, y, n, T, col=(214, 70, 76)):
    d.rectangle([x - 1, y - 1, x + 35, y + 41], fill=OUT)
    d.rectangle([x, y, x + 34, y + 40], fill=(250, 246, 236)); d.rectangle([x, y, x + 34, y + 9], fill=col)
    for hx in (x + 8, x + 26): d.rectangle([hx, y - 3, hx + 1, y + 2], fill=(90, 90, 100))
    text(img, str(n), x + 17, y + 25, col=(60, 50, 70), out=None, shadow=False)


def s_years(img, d, lt, dur, T, A):
    f = clamp(lt / dur)
    p = 0.2 + lt * 0.62
    st, night = day_cycle(p)
    sky(img, st, 0, H, 5)
    if night > 0: stars(d, T, 170, night, 140)
    # 太阳和月亮画着弧线飞过
    a = (p % 1) * 2 * math.pi
    sx, sy = 240 - 230 * math.cos(a), 210 - 190 * math.sin(a)
    if sy < 215:
        glow(img, sx, sy, 40, (255, 230, 160), 0.5); d.ellipse([sx - 12, sy - 12, sx + 12, sy + 12], fill=(255, 244, 190))
    mx, my = 240 + 230 * math.cos(a), 210 + 190 * math.sin(a)
    if my < 215: glow(img, mx, my, 30, (190, 200, 255), 0.35); moon(d, mx, my, 10)
    sf = f * 4.0
    leaf, leaf_l, ground = season_cols(sf)
    lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay)
    pix.hills(ld, 214, 10, 0.011, 1.0, lerpc(ground, (60, 80, 110), 0.45))
    ld.ellipse([-60, 196, 540, 420], fill=ground)
    ld.ellipse([-60, 196, 540, 420], outline=lerpc(ground, (255, 255, 255), 0.3))
    pix.grass(ld, 204, lerpc(ground, (0, 0, 0), 0.2), lerpc(ground, (255, 255, 255), 0.25), T, 90, 400, 5)
    bare = clamp((sf - 3.1) / 0.5)
    if bare < 1: pix.tree_round(ld, 196, 202, 3.3, leaf, leaf_l, sway=round(math.sin(T * 1.5)))
    else:
        ld.rectangle([190, 156, 202, 202], fill=(112, 74, 50))
        for bx, by in ((-30, -60), (26, -66), (-4, -92), (-44, -30), (40, -34)):
            ld.line([(196, 160), (196 + bx, 160 + by)], fill=(112, 74, 50), width=3)
            ld.line([(196 + bx * 0.6, 160 + by * 0.6), (196 + bx * 0.6 + by * 0.3, 160 + by * 0.9)], fill=(112, 74, 50), width=2)
            ld.line([(196 + bx - 4, 158 + by), (196 + bx + 5, 158 + by)], fill=(250, 250, 255), width=2)
    # 长椅
    bx0 = 244
    ld.rectangle([bx0, 184, bx0 + 62, 187], fill=(150, 100, 70)); ld.rectangle([bx0, 170, bx0 + 62, 173], fill=(150, 100, 70))
    ld.rectangle([bx0, 176, bx0 + 62, 179], fill=(132, 86, 60))
    for px in (bx0 + 3, bx0 + 57): ld.rectangle([px, 170, px + 2, 202], fill=(96, 64, 48))
    if sf > 3.2: ld.rectangle([bx0 + 30, 182, bx0 + 62, 184], fill=(250, 250, 255))
    age = ['young', 'young', 'a1', 'a2', 'a3', 'a4', 'a5', 'a5'][min(7, int(f * 7.4))]
    person(lay, 'boy', bx0 + 16, 203, age=age, view='side', pose='sit', expr='closed' if f > 0.55 else 'sad', s=2)
    if night > 0:
        arr = np.array(lay); m = 1 - 0.6 * night
        arr[..., :3] = (arr[..., :3] * np.array([m, m, min(1, m + 0.2 * night)])).astype(np.uint8); lay = Image.fromarray(arr)
    img.paste(lay, (0, 0), lay)
    # 身边的位置：一开始"你"还在，很快就淡掉了
    ga = 1 - span(lt, 0.2, 1.3)
    if ga > 0: ghost(img, 'girl', bx0 + 42, 203, 2, ga, view='side', pose='sit', expr='smile', flip=True)
    if sf < 1.1: pix.petals(d, T, 40, speed=26, wind=34)
    elif 1.9 < sf < 3.1: leaves(d, T, 44, speed=34, wind=50)
    elif sf >= 3.1: pix.snow(d, T, 150, speed=30)
    calendar(img, d, 22, 20, int(lt * 16) % 31 + 1, T)
    for i in range(6):                         # 撕下来飞走的日历纸
        k = ((lt * 2.4 + i / 6) % 1)
        px = 40 + k * 150; py = 44 - 50 * k + 90 * k * k + 6 * math.sin(k * 12 + i)
        if int(k * 10 + i) % 2: d.rectangle([px, py, px + 7, py + 5], fill=(250, 246, 236))
        else: d.polygon([(px, py), (px + 7, py + 2), (px + 6, py + 6), (px - 1, py + 4)], fill=(232, 226, 214))


# ================================================================ 随着你离去 快乐渺无音讯
def platform(img, d, t):
    sky(img, DUSK4, 0, H, 5)
    glow(img, 380, 150, 90, (255, 220, 150), 0.5); d.ellipse([362, 136, 398, 172], fill=(255, 236, 180))
    for i in range(4): cloud(d, (i * 150 + t * 6) % 620 - 100, 30 + i * 22 % 60, 1.6, (255, 196, 160), (236, 150, 140))
    pix.hills(d, 176, 16, 0.012, 0.4, (150, 96, 120)); pix.hills(d, 196, 10, 0.02, 2.0, (112, 72, 104))
    base = 222
    d.rectangle([0, base - 8, W, base + 8], fill=(86, 66, 84))
    rails(d, base, 0, col=(60, 50, 60), sleeper=(110, 84, 78))
    x = 462 + 20 * t + 46 * t * t
    train(img, d, x, base, t, cars=3, night=0.15, lit=0.7, hero=(0, 3), rust=0.3, roll=x / 5)
    smoke(img, x - 30, base - 56, t, n=7, vx=-60 - 30 * t, vy=-16, r1=16)
    # 站台
    d.rectangle([0, 232, W, H], fill=(150, 140, 150)); d.rectangle([0, 232, W, 235], fill=(250, 214, 110)); d.rectangle([0, 236, W, 238], fill=(120, 110, 124))
    for px in range(-20, W, 48): d.line([(px, 239), (px - 14, H)], fill=(132, 122, 136))
    for px in (70, 410):
        d.rectangle([px, 120, px + 5, 232], fill=(70, 62, 84)); d.rectangle([px - 30, 112, px + 36, 120], fill=(86, 76, 100))
    d.rectangle([40, 112, 446, 116], fill=(70, 62, 84))
    d.rectangle([222, 124, 262, 140], fill=(60, 80, 120)); d.rectangle([222, 124, 262, 140], outline=(230, 230, 240))
    text(img, '再见', 242, 132, col=(240, 240, 250), out=None, font=FONT_S, shadow=False)
    d.line([(232, 116), (232, 124)], fill=(70, 62, 84)); d.line([(252, 116), (252, 124)], fill=(70, 62, 84))
    # "我"：先站着，再追出去几步
    if t < 1.1: person(img, 'boy', 236, 262, view='back', arms='wave', ph=int(t * 8), s=2)
    else:
        k = span(t, 1.1, 2.7); px = 236 + 96 * eout(k)
        if k < 1: person(img, 'boy', px, 262, view='side', pose='run', ph=wph(t, 10), expr='sad', s=2)
        else: person(img, 'boy', px, 262, view='side', arms='reach', expr='sad', s=2)
    leaves(d, t, 14, speed=30, wind=90 + 60 * t, seed=3)


def mailbox(img, d, t):
    sky(img, PALE, 0, H, 5)
    for i in range(3): cloud(d, (i * 190 + t * 5) % 620 - 100, 24 + i * 26, 1.8, (200, 196, 212), (170, 166, 190))
    pix.hills(d, 190, 12, 0.014, 1.2, (150, 150, 170))
    d.rectangle([0, 214, W, H], fill=(136, 150, 130)); d.rectangle([0, 214, W, 216], fill=(160, 176, 150))
    for fx in range(0, W, 18):                 # 木栅栏
        d.rectangle([fx, 170, fx + 9, 214], fill=(226, 218, 206)); d.polygon([(fx, 170), (fx + 9, 170), (fx + 4, 163)], fill=(226, 218, 206))
        d.line([(fx + 9, 170), (fx + 9, 214)], fill=(190, 180, 176))
    d.rectangle([0, 182, W, 185], fill=(204, 194, 186)); d.rectangle([0, 200, W, 203], fill=(204, 194, 186))
    # 信箱
    mx, my = 300, 132
    d.rectangle([mx + 22, my + 30, mx + 28, 224], fill=(110, 80, 64))
    d.rounded_rectangle([mx - 1, my - 1, mx + 57, my + 35], 12, fill=OUT)
    d.rounded_rectangle([mx, my, mx + 56, my + 34], 11, fill=(206, 70, 70)); d.rectangle([mx, my + 22, mx + 56, my + 34], fill=(206, 70, 70))
    d.rectangle([mx + 2, my + 30, mx + 54, my + 33], fill=(160, 46, 56))
    d.rounded_rectangle([mx + 3, my + 4, mx + 30, my + 30], 8, fill=(26, 18, 30)); d.rectangle([mx + 3, my + 20, mx + 30, my + 30], fill=(26, 18, 30))
    d.polygon([(mx + 3, my + 31), (mx + 30, my + 31), (mx + 24, my + 46), (mx - 6, my + 46)], fill=(170, 52, 60), outline=OUT)  # 开着的小门
    for a in range(4):                         # 蜘蛛网
        d.line([(mx + 3, my + 5), (mx + 6 + a * 7, my + 28 - a * 6)], fill=(150, 150, 170))
    d.arc([mx - 5, my - 3, mx + 15, my + 17], 10, 80, fill=(150, 150, 170)); d.arc([mx - 12, my - 10, mx + 24, my + 26], 10, 80, fill=(150, 150, 170))
    sp = my + 16 + round(3 * math.sin(t * 2)); d.line([(mx + 22, my + 5), (mx + 22, sp)], fill=(150, 150, 170)); d.rectangle([mx + 21, sp, mx + 23, sp + 2], fill=(40, 34, 50))
    d.rectangle([mx + 44, my - 12, mx + 46, my + 6], fill=(240, 236, 226)); d.rectangle([mx + 46, my + 2, mx + 54, my + 6], fill=(240, 220, 120))
    person(img, 'boy', 236, 226, view='side', expr='down' if t > 0.8 else 'sad', s=2)
    a = eback(span(t, 0.9, 1.2))
    if a > 0.1:
        bubble(img, d, 180, 110, 248, 144, tail=(232, 164), a=clamp(a))
        if a > 0.9:
            d.rectangle([192, 121, 207, 132], fill=(60, 50, 70)); put(img, 'mail', 200, 127, 2); text(img, '× 0', 228, 127, col=(60, 50, 70), out=None, shadow=False)
    leaves(d, t, 10, speed=22, wind=26, seed=9)
    grade(img, sat=0.75)


def s_leave(img, d, lt, dur, T, A):
    shots(img, lt, [(0, platform), (3.5, mailbox)], tr=0.45)


# ================================================================ 随往事淡去 随梦境睡去
MEM_T = (141.6, 148.6, 154.9, 160.2)           # 间奏里四段回忆的时间，用来取照片


def photos(img, d, t):
    d.rectangle([0, 0, W, H], fill=(58, 44, 60))
    for y in range(0, H, 18): d.line([(0, y), (W, y)], fill=(66, 50, 68))
    glow(img, 240, 120, 260, (255, 200, 150), 0.18, ry=150)
    pts = [(x, 46 + 16 * math.sin(x / W * math.pi)) for x in range(0, W + 1, 8)]
    d.line(pts, fill=(200, 180, 160))
    for i in range(12):                        # 串灯
        x = 20 + i * 40; y = 46 + 16 * math.sin(x / W * math.pi) + 3
        on = 0.5 + 0.5 * math.sin(t * 3 + i * 1.7)
        glow(img, x, y, 7, (255, 220, 140), 0.4 * on); d.rectangle([x - 1, y - 1, x, y + 1], fill=lerpc((150, 120, 90), (255, 240, 180), on))
    for i, T0 in enumerate(MEM_T[:3]):
        k = ease(span(t, 0.5 + i * 0.35, 2.3 + i * 0.3))
        cx = 96 + i * 144; cy = 138 + 6 * math.sin(i * 2.2) + 2 * math.sin(t * 1.4 + i)
        ph = fade_to(mini(T0, 96, 54), (244, 236, 216), 0.93 * k)
        d.line([(cx, 46 + 16 * math.sin(cx / W * math.pi)), (cx, cy - 44)], fill=(200, 180, 160))
        polaroid(img, d, cx, cy, ph, rot=(-4, 3, -2)[i])
        d.rectangle([cx - 3, cy - 50, cx + 2, cy - 40], fill=(214, 150, 96))


def dream(img, d, t):
    room(img, d, t, me='lie', lamp=0.0, expr='closed')
    zoom(img, 2, 190, 128)
    hx, hy = 164, 92                           # 放大以后枕头上那颗头的位置
    a = eout(span(t, 0.2, 0.9)) * (1 - span(t, 2.6, 3.3))
    cy = 64 - 10 * span(t, 0.2, 3.2)
    thought(img, d, 300, cy, 84, 46, to=(hx + 30, hy - 6), a=a)
    if a > 0.9:
        ph = fade_to(mini(MEM_T[3], 112, 63), (252, 250, 244), 0.25 + 0.6 * span(t, 1.6, 2.8))
        m = Image.new('L', (112, 63), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, 111, 62], 16, fill=255)
        img.paste(ph, (300 - 56, int(cy) - 31), m)
    for i in range(3):
        k = (t * 0.5 + i / 3) % 1
        put(img, 'zz', hx + 14 + k * 26 + 3 * math.sin(k * 9), hy - 18 - k * 30, 2 if i == 0 else 1, alpha=clamp(2 - 2.2 * k))
    vig(img, 0.5)


def s_fade(img, d, lt, dur, T, A):
    shots(img, lt, [(0, photos), (3.0, dream)], tr=0.5)


# ================================================================ 随麻痹的心逐渐远去
def s_numb(img, d, lt, dur, T, A):
    f = clamp(lt / dur)
    sky(img, PALE, 0, H, 5)
    glow(img, 400, 210, 150, (255, 214, 180), 0.35)
    for i in range(6):
        r = rng(i * 5 + 2)
        cloud(d, (r.uniform(0, 600) + T * (5 + i)) % 640 - 120, 20 + i * 30, 1.4 + r.random(), (214, 206, 216), (176, 170, 196))
    for i in range(5): pix.bird(d, 300 + i * 14 + lt * 14, 60 + (i % 2) * 8 - lt * 3 + i * 3, T, ph=i)
    pix.hills(d, 232, 14, 0.012, 0.6, (120, 124, 150))
    d.ellipse([-80, 226, 300, 400], fill=(84, 96, 110)); d.ellipse([-80, 226, 300, 400], outline=(120, 134, 144))
    pix.grass(d, 232, (64, 76, 92), (110, 124, 136), T, 30, 200, 4)
    px, py = 108, 236
    person(img, 'boy', px, py, view='back', arms='wave' if lt < 1.6 else 'down', ph=1, s=2)
    # 心：越飘越远，越来越灰
    k = ease(f)
    hx = lerp(150, 410, k) + 8 * math.sin(lt * 1.6); hy = lerp(150, 34, eout(f)) + 3 * math.sin(lt * 2.3)
    s = lerp(1.5, 0.22, eout(f))
    g = span(lt, 0.3, 2.6)
    pts = [(hx + 3 * math.sin(lt * 3 + i * 0.7) * (i / 8), hy + 17 * s + i * 5 * s) for i in range(9)]
    d.line(pts, fill=(236, 232, 240))
    if lt < 0.5: d.line([pts[-1], (px + 12, py - 44)], fill=(236, 232, 240))
    if g < 0.6: glow(img, hx, hy, 40 * s, (255, 120, 130), 0.35 * (1 - g / 0.6))
    heart(d, hx, hy, s, grey=g, crack=span(lt, 1.2, 3.0))
    grade(img, sat=1 - 0.5 * f)
