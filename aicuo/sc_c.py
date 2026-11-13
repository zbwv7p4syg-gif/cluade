"""爱错 · 第二段主歌和第二段副歌。签名都是 (img, d, lt, dur, T, A)。

深夜的书桌上摊开一本旧相册，页角卷起来，照片活了：樱花树下的野餐，暖黄的光；他捧着一颗发光的小心，
以为能一直握住，光却从指缝里漏光了；放映室里重放当初的胶片，翻到银幕背面，是她一个人守着蛋糕和蜡烛等到半夜；
镜子里的人抬手指着他，镜子碎了。副歌里他在雨夜霓虹里狂奔，追不上远处那把红伞；像素拼成的心炸成碎屑被风吹散；
清晨的海边一只白鸟起飞、盘旋、找地方落脚；老电视倒带重放海边的回忆，磁带卡住，满屏雪花，最后"无信号"。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
import motifs as M
from props import *          # noqa: F401,F403
from pix import (W, H, FONT, FONT_S, OUT, SKIN, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky,
                 stars, person, wph, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, city, lamp, BAYER)
from sc_b import umbrella, neon, RAINNIGHT

YY, XX = np.mgrid[0:H, 0:W]


# ================================================================ 回忆里的画面（相册、胶片、录像带共用）
SAKURA = ((255, 182, 200), (255, 214, 224), (240, 150, 180))


def mem_park(img, d, t):
    """樱花树下野餐：他和她坐在格子布上说笑"""
    sky(img, DAY, 0, 190, 5)
    cloud(d, 60 + t * 3, 30, 2, (255, 255, 255), (220, 232, 250))
    cloud(d, 300 + t * 2, 50, 1.6, (255, 255, 255), (220, 232, 250))
    pix.hills(d, 176, 8, 0.02, 0.5, (150, 200, 120))
    d.rectangle([0, 186, W, H], fill=(124, 186, 100))
    pix.grass(d, 186, (100, 160, 84), (150, 210, 110), t, seed=2)
    for x in range(0, W, 7):
        pix.flower(d, x + (x * 13) % 5, 200 + (x * 7) % 50, [(255, 255, 255), (255, 220, 120), (255, 170, 200)][x % 3], 0, h=0)
    # 樱花树
    d.rectangle([92, 110, 102, 196], fill=(110, 76, 66))
    d.line([(98, 140), (70, 112)], fill=(110, 76, 66), width=5); d.line([(98, 130), (130, 104)], fill=(110, 76, 66), width=5)
    for bx, by, r in [(60, 96, 30), (100, 74, 38), (140, 96, 30), (84, 120, 24), (126, 118, 24), (100, 104, 30)]:
        d.ellipse([bx - r, by - r * 0.8, bx + r, by + r * 0.8], fill=(250, 170, 196))
    for bx, by, r in [(88, 66, 18), (60, 88, 14), (130, 82, 14)]:
        d.ellipse([bx - r, by - r * 0.7, bx + r, by + r * 0.7], fill=(255, 210, 222))
    # 格子野餐布
    for i in range(8):
        for j in range(3):
            c = (236, 70, 80) if (i + j) % 2 else (255, 244, 240)
            x0 = 176 + i * 16 - j * 4; y0 = 212 + j * 7
            d.polygon([(x0, y0), (x0 + 16, y0), (x0 + 12, y0 + 7), (x0 - 4, y0 + 7)], fill=c)
    d.rectangle([288, 202, 304, 212], fill=(190, 130, 70)); d.arc([288, 194, 304, 210], 180, 360, fill=(140, 90, 50), width=2)
    person(img, 'boy', 222, 218, view='side', pose='sit', expr='happy', s=2)
    person(img, 'girl', 262, 218, view='side', pose='sit', expr='laugh' if int(t * 2) % 3 else 'happy', s=2, flip=True)
    pix.petals(d, t, 50, SAKURA, 16, 14, seed=3)
    for j in range(2): pix.butterfly(d, int(330 + 30 * math.sin(t * 0.8 + j * 2)), int(150 + 14 * math.sin(t * 1.3 + j)), t, (255, 220, 120), j)


def mem_sea(img, d, t, rev=False):
    """黄昏的沙滩：他牵着她往右走（rev=True 时倒着走）"""
    sky(img, GOLDEN, 0, 168, 6)
    glow(img, 340, 150, 110, (255, 210, 150), 0.45, 50)
    d.ellipse([320, 130, 360, 170], fill=(255, 236, 190))
    d.rectangle([0, 160, W, 200], fill=(236, 150, 130))
    for y in range(160, 200, 3):
        off = (t * 30 * (1 - 2 * rev) + y * 7) % 40
        for x in range(int(-off), W, 40):
            d.line([(x, y), (x + 14, y)], fill=(255, 196, 160))
    d.rectangle([0, 196, W, H], fill=(236, 206, 160))
    for k in range(3):                                                  # 一层层冲上来的浪
        f = ((t * 0.4 * (1 - 2 * rev) + k / 3) % 1)
        y = 196 + 10 * math.sin(f * math.pi)
        d.line([(0, y), (W, y + 2)], fill=(255, 248, 236))
    x = 120 + (t * 26 if not rev else 26 * 5 - t * 26)
    ph = wph(t, 6)
    if rev: ph = 3 - ph
    person(img, 'boy', x, 238, view='side', pose='walk', ph=ph, expr='happy', arms='hold_f', s=2)
    person(img, 'girl', x + 22, 238, view='side', pose='walk', ph=ph + 2, expr='laugh', arms='hold', s=2)
    for j in range(3): pix.bird(d, int(80 + j * 40 + t * 10), int(60 + j * 8), t, (110, 70, 80), j)


def mem_wheel(img, d, t):
    """夜里的摩天轮"""
    sky(img, ((0, (20, 18, 60)), (0.7, (70, 50, 110)), (1, (150, 90, 130))), 0, H, 5)
    stars(d, t, 150, 0.8, 80)
    cx, cy, r = 300, 100, 70
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 200, 230), width=2)
    for k in range(12):
        a = t * 0.2 + k * math.pi / 6
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        d.line([(cx, cy), (x, y)], fill=(200, 150, 200))
        d.rectangle([x - 4, y, x + 4, y + 7], fill=[(255, 120, 150), (120, 200, 255), (255, 210, 100)][k % 3])
    d.line([(cx, cy), (cx - 40, 220)], fill=(180, 140, 190), width=3); d.line([(cx, cy), (cx + 40, 220)], fill=(180, 140, 190), width=3)
    glow(img, cx, cy, 90, (255, 150, 200), 0.2)
    d.rectangle([0, 220, W, H], fill=(30, 26, 50))
    person(img, 'boy', 120, 230, view='side', pose='stand', expr='smile', arms='hold_f', s=2)
    person(img, 'girl', 142, 230, view='side', pose='stand', expr='happy', arms='hold', s=2)


@lru_cache(None)
def photo(which, w, h, t=1.3, k=0.85):
    """把一幅回忆画面缩成照片（偏暖的旧照片色）"""
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im); d.fontmode = '1'
    {'park': mem_park, 'sea': mem_sea, 'wheel': mem_wheel}[which](im, d, t)
    return props.sepia(props.shrink(im, w, h), k)


def old_film(img, T, a=8):
    """旧照片的颗粒和暖色"""
    img.paste(props.sepia(img, 0.55, (1.1, 0.95, 0.75)))
    props.grain(img, T, a)


# ================================================================ 书桌上的旧相册和樱花树下的野餐
def desk(img, d, t):
    T = t
    for y in range(0, H, 9):                                           # 木头桌面
        d.rectangle([0, y, W, y + 8], fill=(92, 60, 48) if (y // 9) % 2 else (100, 66, 52))
        d.line([(0, y + 8), (W, y + 8)], fill=(70, 44, 36))
    open_ = ease((t - 0.3) / 1.1)
    lp, rp = M.album(img, d, 240, 120, 300, 176, open_)
    if rp:
        for (x0, y0, x1, y1), shots_ in ((lp, (('park', 0), ('wheel', 1))), (rp, (('sea', 0), ('park', 1)))):
            for which, j in shots_:
                pw, ph = 100, 58
                px = (x0 + x1) / 2 - pw / 2 + (j * 10 - 5); py = y0 + 14 + j * 80
                d.rectangle([px - 4, py - 4, px + pw + 4, py + ph + 12], fill=(255, 250, 240), outline=(200, 190, 170))
                img.paste(photo(which, pw, ph), (int(px), int(py)))
                for cx_, cy_ in ((px - 4, py - 4), (px + pw - 2, py - 4)):
                    d.polygon([(cx_, cy_), (cx_ + 6, cy_), (cx_ + 3, cy_ + 4)], fill=(170, 140, 120))
        # 右页的页角一下一下卷起来
        x1, y1 = rp[2], rp[3]
        c = 10 + 8 * (0.5 + 0.5 * math.sin(t * 3))
        d.polygon([(x1, y1 - c), (x1 - c, y1), (x1, y1)], fill=(92, 60, 48))
        d.polygon([(x1, y1 - c), (x1 - c, y1), (x1 - c * 0.8, y1 - c * 0.8)], fill=(226, 214, 190))
    # 台灯的光、杯子
    glow(img, 430, 30, 180, (255, 210, 140), 0.35, 140)
    d.ellipse([420, 200, 460, 236], fill=(230, 226, 220)); d.ellipse([426, 204, 454, 226], fill=(120, 70, 50))
    d.arc([452, 208, 470, 226], 270, 90, fill=(230, 226, 220), width=3)
    for j in range(8):
        r = rng(j)
        x = 380 + r.uniform(0, 90) + 6 * math.sin(t + j); y = (r.uniform(0, 120) - t * 6) % 120 + 10
        d.point((x, y), fill=(255, 236, 190))
    z = 1 + 2 * ein((t - 2.3) / 0.75)
    props.zoom(img, z, lerp(240, 300, ease((t - 2.0) / 0.6)), lerp(120, 66, ease((t - 2.0) / 0.6)))
    vig(img, 0.5, (20, 10, 10))


def picnic(img, d, t):
    mem_park(img, d, 1.3 + t)
    old_film(img, t, 6)
    d.rectangle([0, 0, W - 1, H - 1], outline=(255, 248, 232), width=6)
    d.rectangle([6, 6, W - 7, H - 7], outline=(220, 206, 180))
    vig(img, 0.3, (80, 50, 30))


def s_album(img, d, lt, dur, T, A):
    shots(img, lt, [(0, desk), (3.05, picnic)], tr=0.3, kind='white')


# ================================================================ 手里的光从指缝漏光
def s_happiness(img, d, lt, dur, T, A):
    cool = ease((lt - 3.0) / 3.0)
    sky(img, mix_stops(((0, (120, 70, 60)), (0.5, (220, 140, 90)), (1, (255, 214, 150))),
                       ((0, (40, 40, 60)), (0.5, (90, 86, 110)), (1, (150, 146, 160))), cool), 0, H, 6)
    props.bokeh(img, T, 14, [lerpc(c, (170, 180, 210), cool) for c in (GOLD, PINK, (255, 220, 170))], seed=2, a=0.3)
    hx, hy = 240, 178 + 10 * ease((lt - 4.8) / 1.0)                  # 光漏光以后，空了的手慢慢垂下去
    life = 1 - ease((lt - 2.9) / 2.2)
    M.cupped_hands(img, d, hx, hy, 4, 0.0, shade=1 - 0.25 * cool)
    if life > 0:
        bob = 3 * math.sin(T * 2)
        glow(img, hx, hy - 20 + bob, 60 * life + 10, (255, 200, 150), 0.6 * life)
        M.heart(img, hx, hy - 20 + bob, 1.0 + 0.6 * life, thump(T, 0.4) * life)
        for j in range(6):
            a = T * 1.5 + j * 1.05
            sparkle(d, int(hx + math.cos(a) * 34 * life), int(hy - 20 + math.sin(a) * 18 * life), T + j, (255, 240, 200), 2)
    if lt > 2.7:                                                       # 光从指缝漏下去
        for j in range(30):
            r = rng(j * 3)
            k = ((lt - 2.7) * 0.9 + r.random()) % 1
            if lt - 2.7 < r.random() * 1.2: continue
            if lt > 5.6 and k < (lt - 5.6) / 0.6: continue
            x = hx + r.uniform(-3, 3) + math.sin(k * 6 + j) * 6 * k
            y = hy + 30 + k * 60
            d.point((x, y), fill=lerpc((255, 230, 180), (200, 120, 90), k))
            if j % 3 == 0: d.point((x, y - 1), fill=(255, 250, 230))
    if lt > 5.0:                                                       # 手松开，最后一点光往上飘走
        k = lt - 5.0
        twinkle(d, int(hx + 10 * math.sin(k * 2)), int(hy - 30 - k * 40), clamp(k / 1.4), (255, 240, 220), 4)
    vig(img, 0.45, (40, 20, 20))


# ================================================================ 放映室和银幕背面
def cinema(img, d, t):
    T = t
    img.paste((14, 12, 20), (0, 0, W, H))
    sx0, sy0, sx1, sy1 = 40, 18, 330, 182
    film = Image.new('RGB', (W, H)); fd = ImageDraw.Draw(film); fd.fontmode = '1'
    mem_sea(film, fd, t)
    film = props.sepia(film, 0.7)
    flick = 0.85 + 0.15 * math.sin(T * 37) * math.sin(T * 11)
    film = Image.fromarray((np.asarray(film) * flick).astype(np.uint8))
    img.paste(film.resize((sx1 - sx0, sy1 - sy0), Image.BOX), (sx0, sy0))
    d.rectangle([sx0 - 2, sy0 - 2, sx1 + 2, sy1 + 2], outline=(40, 34, 40))
    for k in range(3):                                                 # 胶片的划痕
        x = sx0 + (rng(int(T * 12) + k).random()) * (sx1 - sx0)
        d.line([(x, sy0), (x, sy1)], fill=(230, 210, 170))
    # 放映机的光束和灰尘
    px, py = 446, 40
    tfill(img, 'polygon', [(px, py - 4), (px, py + 4), (sx1, sy1), (sx1, sy0)], (255, 236, 190), 0.12)
    d.rectangle([px - 6, py - 10, px + 22, py + 10], fill=(40, 36, 44))
    d.ellipse([px - 4, py - 16, px + 8, py - 4], fill=(56, 50, 60)); d.ellipse([px + 8, py - 16, px + 20, py - 4], fill=(56, 50, 60))
    for k in range(2):
        a = T * 4 + k * 3
        d.line([(px + 2 + k * 12, py - 10), (px + 2 + k * 12 + 4 * math.cos(a), py - 10 + 4 * math.sin(a))], fill=(120, 110, 120))
    glow(img, px - 4, py, 10, (255, 236, 190), 0.6)
    for j in range(20):
        r = rng(j * 5)
        u = r.random(); v = r.uniform(-0.5, 0.5)
        x = lerp(px, sx1, u) + 6 * math.sin(T * 0.7 + j); y = lerp(py, (sy0 + sy1) / 2 + v * (sy1 - sy0) * u, 1) + 4 * math.sin(T + j)
        d.point((x, y), fill=(255, 240, 210))
    # 一排排座椅和他的背影
    for row, (y, n) in enumerate(((210, 9), (236, 10), (262, 11))):
        for k in range(n):
            x = W / 2 + (k - n / 2 + 0.5) * 48
            d.rounded_rectangle([x - 20, y - 14, x + 20, y + 30], 6, fill=(36 - row * 6, 26 - row * 4, 40 - row * 6))
    hx, hy = 240, 198
    d.ellipse([hx - 11, hy - 26, hx + 11, hy - 2], fill=(34, 30, 44))
    d.rectangle([hx - 16, hy - 6, hx + 16, hy + 12], fill=(40, 58, 106))
    d.rectangle([hx - 12, hy - 8, hx + 12, hy - 4], fill=(150, 178, 210))
    vig(img, 0.4, (0, 0, 0))


def waiting_room(img, d, t):
    """银幕背面：她一个人守着蛋糕等到半夜"""
    T = t
    img.paste((36, 34, 62), (0, 0, W, H))
    for x in range(0, W, 24): d.line([(x, 0), (x, 200)], fill=(40, 38, 68))
    # 窗外的雨夜
    wx0, wy0, wx1, wy1 = 40, 40, 190, 150
    sub = Image.new('RGB', (wx1 - wx0, wy1 - wy0)); sd = ImageDraw.Draw(sub)
    sub.paste(pix.vgrad(wx1 - wx0, wy1 - wy0, RAINNIGHT))
    for k in range(10):
        r = rng(k)
        bx = r.uniform(0, 150); bh = r.uniform(30, 80)
        sd.rectangle([bx, 110 - bh, bx + 18, 110], fill=(30, 28, 56))
        for wy in range(int(110 - bh) + 4, 108, 6):
            if r.random() < 0.5: sd.point((bx + 4 + (wy % 3) * 4, wy), fill=(255, 200, 130))
    pix.rain(sd, T, 0, 150, 0, 110, 40, (120, 130, 190), speed=240)
    img.paste(sub, (wx0, wy0))
    props.drops_on_glass(img, d, T, (wx0, wy0, wx1, wy1), 30)
    d.rectangle([wx0 - 4, wy0 - 4, wx1 + 4, wy1 + 4], outline=(90, 70, 70), width=4)
    d.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=(90, 70, 70), width=3)
    # 墙上的钟：已经过了十二点
    props.clock(d, 300, 50, 18, -0.1 + t * 0.02, 0.6 + t * 0.25)
    # 桌子、蛋糕、蜡烛
    d.rectangle([0, 200, W, H], fill=(60, 44, 52))
    d.rectangle([250, 170, 420, 176], fill=(140, 96, 70)); d.rectangle([260, 176, 266, 214], fill=(110, 74, 56))
    d.rectangle([404, 176, 410, 214], fill=(110, 74, 56))
    d.rectangle([340, 150, 380, 170], fill=(255, 236, 230)); d.rectangle([340, 150, 380, 154], fill=(255, 170, 190))
    for x in range(342, 380, 6): d.point((x, 160), fill=(226, 60, 80))
    out_at = 3.9
    burn = clamp(t / out_at)
    cy0 = 140 + 6 * burn
    d.rectangle([358, cy0, 361, 150], fill=(255, 250, 240))
    if t < out_at:
        fl = 1 + 0.5 * math.sin(T * 17)
        glow(img, 359.5, cy0 - 5, 60, (255, 190, 110), 0.4)
        d.ellipse([357, cy0 - 7 - fl, 362, cy0 - 1], fill=(255, 210, 110)); d.point((359, cy0 - 3), fill=(255, 255, 230))
    else:
        props.smoke(img, 359, cy0 - 2, t, n=5, col=(170, 166, 180), shade=None, vx=4, vy=-16, life=1.6, r0=1, r1=5, a=0.7)
        darken(img, 0.25 * clamp((t - out_at) / 0.4), (10, 8, 20))
    # 她坐在桌边，低着头看手机；手机的光
    person(img, 'girl', 300, 214, view='side', pose='sit', expr='down', arms='phone', s=2, flip=False)
    glow(img, 314, 158, 16, (170, 220, 255), 0.35 * (1 - 0.6 * clamp((t - 2.5) / 1.5)))
    vig(img, 0.5, (6, 4, 14))


def s_behind(img, d, lt, dur, T, A):
    flip = 4.3
    if abs(lt - flip) < 0.35:                                           # 银幕像一页纸那样翻过去
        k = (lt - flip) / 0.35
        src = Image.new('RGB', (W, H)); sd = ImageDraw.Draw(src); sd.fontmode = '1'
        (cinema if k < 0 else waiting_room)(src, sd, lt if k < 0 else lt - flip)
        w = max(1, int(W * abs(k)))
        img.paste((6, 4, 10), (0, 0, W, H))
        img.paste(src.resize((w, H), Image.NEAREST), ((W - w) // 2, 0))
        return
    if lt < flip: cinema(img, d, lt)
    else: waiting_room(img, d, lt - flip)


# ================================================================ 镜子
def s_mirror(img, d, lt, dur, T, A):
    img.paste((20, 16, 30), (0, 0, W, H))
    for x in range(0, W, 30): d.line([(x, 0), (x, 214)], fill=(24, 20, 36))
    d.rectangle([0, 214, W, H], fill=(36, 28, 40))
    for x in range(-40, W, 28): d.line([(x, H), (x + 40, 214)], fill=(30, 24, 34))
    crack_at = 6.4
    red = clamp((lt - crack_at) / 0.3) * (0.6 + 0.4 * math.sin(T * 5))
    # 顶上的一束光
    tfill(img, 'polygon', [(196, 0), (230, 0), (262, 220), (150, 220)], (255, 240, 220), 0.1)
    d.ellipse([150, 212, 262, 226], fill=(52, 44, 56))
    # 他的位置和姿势
    if lt < 2.5: bx, pose, arms, ex = lerp(130, 200, lt / 2.5), 'walk', 'auto', 'down'
    elif lt < 3.6: bx, pose, arms, ex = 200, 'stand', 'down', 'neutral'
    elif lt < 4.2: bx, pose, arms, ex = 200 - 10 * eout((lt - 3.6) / 0.6), 'stand', 'down', 'surprised'
    elif lt < 7.0: bx, pose, arms, ex = 190 + 18 * ease((lt - 4.4) / 1.4), 'stand', 'reach' if lt > 4.9 else 'down', 'sad'
    else: bx, pose, arms, ex = 208, 'sit', 'auto', 'down'
    # 镜子里：他的倒影，后来自己抬手指着他
    mx0, my0, mx1, my1 = 290, 60, 380, 214
    M.mirror_frame(d, mx0, my0, mx1, my1)
    refl = Image.new('RGB', (mx1 - mx0, my1 - my0), (44, 50, 74))
    rd = ImageDraw.Draw(refl)
    for k in range(0, mx1 - mx0 + my1 - my0, 14): rd.line([(k, 0), (k - 60, my1 - my0)], fill=(52, 58, 86))
    rx = 45 + (200 - bx) * 0.5                                          # 倒影在镜子里的位置：他离得越远，倒影越靠里
    r_arms = arms
    if 2.5 < lt < 6.4: r_arms = 'reach'                               # 倒影先抬起手指着他
    r_ex = 'sad' if lt > 2.9 else ex
    tmp = Image.new('RGB', (W, H)); tmp.paste(refl, (mx0, my0))
    person(tmp, 'boy', mx0 + rx, my1, view='side', pose=pose if lt > 2.5 else pose, ph=wph(lt, 5), expr=r_ex, arms=r_arms, s=2, flip=True,
           shade=(0.75, 0.8, 1.0))
    if red > 0: blend_box(tmp, (mx0, my0, mx1, my1), (200, 40, 60), np.full((my1 - my0, mx1 - mx0), 0.35 * red))
    img.paste(tmp.crop((mx0, my0, mx1, my1)), (mx0, my0))
    d.line([(mx0 + 8, my0 + 10), (mx0 + 30, my0 + 40)], fill=(150, 160, 200))
    if lt > crack_at:
        M.shards(d, (mx0, my0, mx1, my1), clamp((lt - crack_at) / 0.5), seed=4)
        for j in range(8):                                           # 掉下来的玻璃碴
            r = rng(j * 9)
            k = lt - crack_at - r.random() * 0.3
            if k < 0: continue
            x = r.uniform(mx0, mx1) - 20 * k; y = r.uniform(150, 210) + 80 * k * k
            if y < 222: d.point((x, y), fill=(220, 230, 255))
    person(img, 'boy', bx, 220, view='side', pose=pose, ph=wph(lt, 5), expr=ex, arms=arms, s=2)
    if crack_at <= lt < crack_at + 0.45: shake(img, lt - crack_at, 5, 0.45)
    if red > 0: glow(img, 335, 140, 90, (220, 40, 60), 0.2 * red)
    vig(img, 0.5, (4, 2, 10))


# ================================================================ 雨夜里狂奔，追不上那把红伞
def s_run(img, d, lt, dur, T, A):
    base = 222
    off = T * 150
    sky(img, RAINNIGHT, 0, base, 6)
    city(img, d, base - 30, 5, off * 0.15, (36, 30, 62), win=(110, 90, 150), hmin=50, hmax=130, frac=0.25, T=T)
    city(img, d, base - 6, 9, off * 0.4, (24, 20, 42), win=(255, 190, 120), hmin=30, hmax=90, frac=0.3, T=T, wmin=22, wmax=48)
    signs = [('爱', (255, 80, 130)), ('雨', (90, 220, 255)), ('酒吧', (255, 200, 90)), ('旅馆', (180, 120, 255)), ('夜', (255, 120, 90))]
    for i, (s_, col) in enumerate(signs):
        x = (i * 130 + 40 - off * 0.7) % (W + 120) - 60
        neon(img, d, x, 60 + (i % 3) * 22, s_, col, T, 0.3, i)
    d.rectangle([0, base, W, H], fill=(30, 28, 44))
    for i in range(6):
        x = (i * 110 - off) % (W + 110) - 40
        lamp(img, d, x, base, 1.0, 84)
    # 远处的红伞：一会儿出现，一会儿又走远看不见了
    ga = clamp((lt - 1.4) / 0.8) * clamp((5.6 - lt) / 1.2)
    if ga > 0:
        ux = 420 + 12 * math.sin(lt * 0.7)
        props.ghost(img, 'girl', ux, base - 2, 1, ga * 0.9, pose='walk', ph=wph(lt, 4), arms='umbrella')
        if ga > 0.2: umbrella(d, ux + 3, base - 34, 1, tilt=0.3)
    reach = 3.6 < lt < 6.2
    person(img, 'boy', 170, base - 2 - (1 if wph(lt, 12) % 2 else 0), view='side', pose='run', ph=wph(lt, 12), expr='sad',
           arms='reach' if reach else 'run', s=2)
    for j in range(5):                                                  # 脚下溅起的水
        k = ((lt * 3 + j / 5) % 1)
        d.point((170 - k * 40 - j * 3, base - 1 - math.sin(k * math.pi) * 10), fill=(170, 190, 240))
    pix.rain(d, T, 0, W, 0, base + 20, 190, (120, 130, 200), speed=360, slant=-6, ln=8)
    props.reflect(img, base + 3, H - base - 3, T, (14, 12, 40), 0.6, 1.5)
    props.splashes(d, T, base + 6, H - 4, 30, (150, 170, 230))
    vig(img, 0.4, (10, 8, 26))


# ================================================================ 像素拼成的心炸成碎屑
@lru_cache(None)
def heart_bits(s=3.6, step=3):
    im = M.heart_img(s)
    a = np.array(im)
    out = []
    r = rng(8)
    for y in range(0, a.shape[0], step):
        for x in range(0, a.shape[1], step):
            if a[y, x, 3] > 0:
                out.append((x - a.shape[1] / 2, y - a.shape[0] / 2, tuple(int(v) for v in a[y, x, :3]), r.random(), r.random()))
    return out


def s_shatter(img, d, lt, dur, T, A):
    boom = 2.65
    img.paste((12, 6, 16), (0, 0, W, H))
    k = lt - boom
    glow(img, 240, 118, 190, (170, 20, 50), (0.3 + 0.25 * thump(T, 0.35)) if k < 0 else 0.55 * clamp(1 - k / 1.5), 120)
    beat = thump(T, 0.35) if k < 0 else 0
    sc = 1 + 0.08 * beat
    for (x, y, col, r1, r2) in heart_bits():
        if k < 0:
            px, py = 240 + x * sc, 118 + y * sc
            jit = (r1 - 0.5) * 2 * clamp((lt - boom + 1.0) / 1.0)
            d.rectangle([px + jit, py, px + jit + 2, py + 2], fill=col)
            continue
        ang = math.atan2(y, x) + k * (1.4 + r1)                       # 往外炸开、绕着转，再被风往右吹
        rad = math.hypot(x, y) + (60 + 120 * r2) * eout(k / 1.2) + 30 * k
        px = 240 + math.cos(ang) * rad + 90 * max(0, k - 1.0) ** 2
        py = 118 + math.sin(ang) * rad * 0.8 + 10 * k
        if px > W + 4: continue
        if k < 0.6: d.rectangle([px, py, px + 2, py + 2], fill=lerpc((255, 255, 255), col, k / 0.6))
        else: M.leaf_bit(d, px, py, T, int(r1 * 50), cols=(col, lerpc(col, (246, 172, 60), 0.4), lerpc(col, (0, 0, 0), 0.3)))
    if 0 <= k < 0.25: pix.dither_fade(img, 1 - k / 0.25, (255, 240, 240))
    if 0 <= k < 0.4: shake(img, k, 6, 0.4)
    if k > 0.9: M.streaks(img, d, T, (0, 30, W, 220), n=int(26 * clamp((k - 0.9) / 0.5)), speed=420, seed=4, col=(255, 210, 220))
    vig(img, 0.5, (4, 2, 8))


# ================================================================ 清晨海边的白鸟
BIRD_KEYS = [(0.0, (62, 120)), (0.7, (62, 120)), (2.3, (190, 66)), (3.8, (320, 52)), (4.9, (390, 100)), (6.2, (412, 172)), (9, (412, 172))]


def bird_path(t):
    for (t0, p0), (t1, p1) in zip(BIRD_KEYS, BIRD_KEYS[1:]):
        if t0 <= t < t1:
            f = ease((t - t0) / (t1 - t0))
            return lerp(p0[0], p1[0], f), lerp(p0[1], p1[1], f)
    return BIRD_KEYS[-1][1]


def s_bird(img, d, lt, dur, T, A):
    sky(img, DAWN, 0, 172, 6)
    sy = lerp(176, 150, ease(lt / 7))
    glow(img, 300, sy, 140, (255, 200, 150), 0.5, 70)
    d.ellipse([280, sy - 20, 320, sy + 20], fill=(255, 232, 190))
    cloud(d, 40 + lt * 4, 40, 2.2, (250, 200, 200), (220, 160, 170))
    cloud(d, 330 + lt * 3, 70, 1.6, (255, 214, 200), (230, 170, 170))
    d.rectangle([0, 172, W, H], fill=(70, 80, 140))
    for y in range(172, H, 3):                                           # 海面的波纹
        off = (lt * 20 + y * 13) % 50
        for x in range(int(-off), W, 50):
            d.line([(x, y), (x + 18 + (y % 7), y)], fill=(110, 120, 180) if y % 2 else (90, 100, 160))
    for y in range(174, H, 2):                                           # 太阳在水里的倒影
        w = 22 - (y - 174) * 0.12 + 3 * math.sin(y + lt * 3)
        if w > 0: d.line([(300 - w, y), (300 + w, y)], fill=(255, 210, 170) if y % 4 else (255, 236, 200))
    M.lighthouse(img, d, 452, 172, 62, T, 0.6)
    # 码头和路灯
    d.rectangle([0, 186, 80, 190], fill=(96, 70, 60))
    for x in (8, 40, 72): d.rectangle([x, 190, x + 4, 230], fill=(70, 50, 46))
    d.rectangle([60, 126, 63, 186], fill=(50, 46, 60)); d.rectangle([54, 122, 69, 126], fill=(50, 46, 60))
    # 浮标
    bob = 2 * math.sin(lt * 2)
    d.rectangle([406, 176 + bob, 418, 190 + bob], fill=(220, 60, 60)); d.rectangle([406, 182 + bob, 418, 185 + bob], fill=(250, 240, 230))
    d.ellipse([402, 188 + bob, 422, 194 + bob], fill=(60, 60, 90))
    x, y = bird_path(lt)
    if lt < 0.7 or lt > 6.2:                                              # 停着
        yy = y + (bob if lt > 6.2 else 0)
        d.ellipse([x - 5, yy - 4, x + 4, yy + 2], fill=(250, 250, 255)); d.point((x + 5, yy - 3), fill=(250, 170, 60))
        d.point((x + 3, yy - 3), fill=(40, 40, 60)); d.line([(x - 5, yy - 1), (x - 8, yy - 3)], fill=(220, 220, 236))
    else:
        flap = 1 if lt < 4.6 else 0.3
        M.seagull(d, x, y, lt * flap, 1.4)
    vig(img, 0.3, (40, 30, 60))


# ================================================================ 老电视倒带
def footage(t, glitch=0.0, T=0.0):
    """电视里放的海边回忆，倒着放；glitch 0..1 让画面撕裂、偏色"""
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im); d.fontmode = '1'
    mem_sea(im, d, max(0.0, 5.2 - t * 1.6), rev=False)
    im = props.sepia(im, 0.35)
    a = np.asarray(im).copy()
    if glitch > 0:
        r = np.random.default_rng(int(T * 30))
        for _ in range(int(14 * glitch)):
            y0 = r.integers(0, H - 10); hh = r.integers(2, 26)
            a[y0:y0 + hh] = np.roll(a[y0:y0 + hh], int(r.integers(-60, 60) * glitch), axis=1)
        a[..., 0] = np.roll(a[..., 0], int(6 * glitch), axis=1)
        a[..., 2] = np.roll(a[..., 2], -int(6 * glitch), axis=1)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    y = int((T * 90) % H)
    d.rectangle([0, y, W, y + 6], fill=(200, 200, 210))
    return im


def rew_overlay(img, d, box, t, T):
    """录像机的屏显：倒带符号和倒着走的时间码，直接画在屏幕上（不跟着画面缩小）"""
    x0, y0, x1, y1 = box
    if int(T * 2) % 2 == 0:
        for k in range(2):
            ax = x0 + 12 + k * 9
            d.polygon([(ax + 8, y0 + 8), (ax + 8, y0 + 18), (ax, y0 + 13)], fill=(255, 255, 255))
        text(img, '倒带', x0 + 46, y0 + 13, col=(255, 255, 255), out=(0, 0, 0), font=FONT_S)
    sec = max(0, 754 - int(t * 47))
    text(img, '%d:%02d:%02d' % (sec // 3600, sec // 60 % 60, sec % 60), x1 - 34, y1 - 12, col=(255, 255, 255), out=(0, 0, 0), font=FONT_S)


def static(T, a=1.0):
    r = np.random.default_rng(int(T * 30) + 7)
    n = r.integers(0, 255, (H // 3, W // 3), dtype=np.uint8).repeat(3, 0).repeat(3, 1)
    return Image.fromarray(np.stack([n, n, n], -1))


def s_vhs(img, d, lt, dur, T, A):
    img.paste((14, 12, 22), (0, 0, W, H))
    d.rectangle([0, 214, W, H], fill=(30, 24, 30))
    tear_at, snow_at, off_at = 5.6, 8.0, 10.0
    if lt < snow_at:
        g = clamp((lt - tear_at) / 1.6)
        scr = footage(lt, g, T)
        if lt > tear_at:
            s = static(T)
            m = (np.asarray(pix.bayer(H, W)) < g * 0.6)
            scr = Image.fromarray(np.where(m[..., None], np.asarray(s), np.asarray(scr)))
    elif lt < off_at - 0.7:
        scr = static(T)
        if lt > snow_at + 0.6:                                        # 雪花退成蓝屏
            scr = Image.new('RGB', (W, H), (30, 60, 170)); sd = ImageDraw.Draw(scr); sd.fontmode = '1'
            text(scr, '无信号', W / 2, H / 2, col=(255, 255, 255), out=(10, 20, 80), scale=3)
    else:
        k = clamp((lt - off_at + 0.7) / 0.5)                          # 关机：一条横线缩成一个点
        scr = Image.new('RGB', (W, H), (8, 8, 12)); sd = ImageDraw.Draw(scr)
        hh = max(1, int(H * (1 - k) * 0.1)); ww = int(W * (1 - k * 0.9))
        if k < 1: sd.rectangle([W / 2 - ww / 2, H / 2 - hh, W / 2 + ww / 2, H / 2 + hh], fill=(220, 230, 255))
    box = M.crt(img, d, 70, 50, 270, 168, scr, on=1.0)
    if lt < tear_at + 1.2: rew_overlay(img, d, box, lt, T)
    glow_a = 0.25 if lt < off_at else 0.0
    glow(img, (box[0] + box[2]) / 2, (box[1] + box[3]) / 2, 200, (150, 170, 220), glow_a, 130)
    # 屏幕的扫描线
    if lt < off_at:
        a = np.asarray(img).copy()
        a[box[1]:box[3]:2, box[0]:box[2]] = (a[box[1]:box[3]:2, box[0]:box[2]] * 0.8).astype(np.uint8)
        img.paste(Image.fromarray(a))
    # 他坐在地上，背对着我们看电视
    person(img, 'boy', 404, 236, view='back', pose='sit', s=2, shade=(0.6, 0.6, 0.75))
    if tear_at < lt < snow_at: shake(img, (lt - tear_at) % 0.4, 2, 0.4)
    vig(img, 0.5, (0, 0, 0))
