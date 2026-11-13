"""曾经是情侣 · 第一段副歌。

录像带倒回到最开始；樱花和小雨的街口，他把伞举到她头顶，红线第一次系上两人的小指；
两只手越拉越远，红线绷断；灰色的人群里两人擦肩而过，谁也没看谁。
她在镜子前一次次换了样子；他抱着花在雨夜里一路狂奔，闯红灯、撞穿一堵堵砖墙；
桥上的同心锁咔哒锁上，钥匙扔进河里；故事变成一格格胶片；锁沉进越来越深的水里；
窗台上的玫瑰等不及枯萎；合照从边缘一点点碎成粉末；就在快忘干净的时候，雨夜的人群里她不经意地出现，雨停在了半空。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
from props import *          # noqa: F401,F403
from pix import (W, H, FONT, FONT_S, OUT, SKIN, SKIN_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng,
                 sky, stars, person, wph, put, twinkle, sparkle, hills, moon, cloud, darken, dither_fade, grade, vig, vgrad, BAYER, bayer)
from sc_a import dpaste, winds, hill_world
from sc_b import canvas

YY, XX = np.mgrid[0:H, 0:W]


# ================================================================ 录像带倒带
def s_rewind(img, d, lt, dur, T, A):
    stop = dur - 0.45
    f = clamp(lt / stop)
    src = lerp(88.6, 6.2, ein(f) * 0.35 + ease(f) * 0.65)
    im = props.SNAP(src)
    img.paste(sepia(im, 0.3 + 0.5 * f))
    if lt < stop:
        vhs(img, T, 1.0)
        d = ImageDraw.Draw(img); d.fontmode = '1'
        if int(lt * 4) % 2 == 0: text(img, '◀◀ REW', 52, 22, (255, 255, 255), (20, 20, 40))
        m, s = divmod(int(src), 60)
        text(img, f'00:{m:02d}:{s:02d}', W - 56, 22, (255, 255, 255), (20, 20, 40))
        for j in range(3):                                   # 倒带时的白色噪点
            r = rng(int(T * 30) * 3 + j)
            y = r.uniform(0, H)
            d.line([(0, y), (W, y + r.uniform(-2, 2))], fill=(220, 220, 230))
    else:
        k = lt - stop
        text(img, '▶ PLAY', 52, 22, (255, 255, 255), (20, 20, 40))
        pix.dither_fade(img, (1 - k / 0.45) * 0.6, (255, 246, 230))


s_rewind.no_sub = False


# ================================================================ 雨中的街口，第一次系上红线
def s_meet(img, d, lt, dur, T, A):
    sky(img, ((0, (150, 180, 222)), (1, (250, 220, 226))), 0, 170)
    # 街边的小店
    for j, (x0, w, c, roof) in enumerate([(-20, 120, (250, 226, 206), (210, 120, 120)), (104, 110, (230, 236, 220), (110, 150, 130)),
                                         (218, 140, (250, 236, 196), (200, 150, 90)), (362, 140, (240, 222, 230), (180, 110, 140))]):
        d.rectangle([x0, 70, x0 + w, 196], fill=c, outline=lerpc(c, (0, 0, 0), 0.3))
        d.rectangle([x0 + 10, 120, x0 + w - 10, 190], fill=(200, 226, 236))
        d.line([(x0 + w // 2, 120), (x0 + w // 2, 190)], fill=lerpc(c, (0, 0, 0), 0.3))
        d.rectangle([x0 + 6, 80, x0 + w - 6, 98], fill=lerpc(c, roof, 0.3))
        for k in range(0, w - 10, 12):                       # 条纹遮阳棚
            d.polygon([(x0 + k, 100), (x0 + k + 6, 100), (x0 + k + 8, 114), (x0 + k + 2, 114)], fill=roof if (k // 12) % 2 == 0 else (255, 250, 246))
    d.rectangle([0, 196, W, H], fill=(150, 146, 160))
    for x in range(0, W, 30): d.line([(x, 196), (x - 14, H)], fill=(140, 136, 150))
    props.reflect(img, 196, 74, T, (110, 110, 140), 0.45, 1.2, 74)
    # 左边一棵樱花树
    d.rectangle([28, 80, 36, 210], fill=(110, 76, 66))
    for bx, by, r in [(32, 70, 30), (8, 90, 22), (60, 86, 24), (20, 50, 20), (52, 52, 20)]:
        d.ellipse([bx - r, by - r * 0.8, bx + r, by + r * 0.8], fill=(255, 196, 214))
        d.ellipse([bx - r * 0.6, by - r * 0.7, bx + r * 0.2, by - r * 0.1], fill=(255, 226, 236))
    pix.rain(d, T, 0, W + 40, -10, H, 60, (190, 200, 230), 240, -3, 5, 4)
    pix.petals(d, T, 30, speed=16, wind=24, seed=2)
    props.splashes(d, T, 200, 266, 18, (220, 226, 246))
    # 他打着伞走进来，停在她身边，把伞往她那边偏
    gx = 360
    stop_t = 1.6
    bx = lerp(-30, 320, ease(clamp(lt / stop_t)))
    walking = lt < stop_t
    share = ease(span(lt, stop_t + 0.1, stop_t + 0.8))
    expr_g = 'neutral' if lt < stop_t + 0.2 else ('surprised' if lt < stop_t + 0.9 else 'shy')
    girl_side = lt > stop_t + 0.2
    if girl_side: person(img, 'girl', gx, 252, 'young', 'side', 'stand', 0, expr_g, 'hold_f' if lt > 2.6 else 'down', s=2, flip=True)
    else: person(img, 'girl', gx, 252, 'young', 'front', 'stand', 0, expr_g, 'behind', s=2)
    person(img, 'boy', bx, 252, 'young', 'side', 'walk' if walking else 'stand', wph(T, 7), 'smile' if lt > 2.0 else 'neutral',
           'umbrella' if share < 0.5 else 'reach', s=2)
    ux = lerp(bx + 6, (bx + gx) / 2 + 6, share)
    uy = lerp(196, 190, share)
    umbrella(d, ux, uy, 40, (60, 86, 150), tilt=0.25 * share, stick=34)
    if lt > 2.6:                                            # 两人的小指之间系上红线
        f = ease(span(lt, 2.6, 3.4))
        p0, p1 = (bx + 14, 232), (gx - 14, 232)
        thread(img, d, p0, p1, 5, RED, glow_a=0.6, upto=f)
        if f >= 1:
            k = lt - 3.4
            hy = 214 - 30 * eout(clamp(k / 0.8))
            heart(img, d, (bx + gx) / 2, hy, 0.5 + 0.15 * thump(T), RED, RED_L, glow_a=0.4)
            for j in range(5): twinkle(d, int((bx + gx) / 2 + 22 * math.cos(j * 1.3 + k * 2)), int(hy + 14 * math.sin(j * 1.7 + k * 2)), (k * 1.5 + j * 0.2) % 1, (255, 240, 240), 3)
    img.paste(sepia(img, 0.12))
    grain(img, T, 5)
    vig(img, 0.45, (60, 40, 40))


# ================================================================ 红线绷断，人群里擦肩而过
def pinky_hand(d, tip, side, sleeve, s=3):
    """侧面握拳、伸出小指的手；side=-1 手从左边伸过来，(x, y) 是小指尖"""
    x, y = tip
    k = side
    fx = x + k * 5 * s                                       # 小指根部
    d.rounded_rectangle([min(fx, x), y - s, max(fx, x), y + s], s, fill=SKIN, outline=OUT)
    fist = [min(fx, fx + k * 15 * s), y - 3 * s, max(fx, fx + k * 15 * s), y + 12 * s]
    d.rounded_rectangle([fist[0] - 1, fist[1] - 1, fist[2] + 1, fist[3] + 1], 4 * s, fill=OUT)
    d.rounded_rectangle(fist, 4 * s, fill=SKIN)
    for j in range(3):                                       # 弯起来的三根手指
        yy = y + (1.5 + j * 3.2) * s
        d.line([(fx + k * s, yy), (fx + k * 5 * s, yy)], fill=SKIN_S)
    d.line([(fx + k * 9 * s, y - 2 * s), (fx + k * 12 * s, y + 4 * s)], fill=SKIN_S)        # 拇指
    cuff = fx + k * 15 * s
    d.rectangle([min(cuff, cuff + k * 70 * s), y - 6 * s, max(cuff, cuff + k * 70 * s), y + 15 * s], fill=sleeve)
    d.rectangle([min(cuff, cuff + k * 3 * s), y - 6 * s, max(cuff, cuff + k * 3 * s), y + 15 * s], fill=lerpc(sleeve, (255, 255, 255), 0.35))


def s_apart(img, d, lt, dur, T, A):
    cut = 3.2
    if lt < cut:
        sky(img, ((0, (20, 14, 30)), (1, (50, 30, 50))), 0, H)
        props.bokeh(img, T, 12, [(255, 120, 140), (255, 200, 160), (160, 120, 200)], 3, 0.25, 14, 30, 3)
        bs = [b for b in beats_in(T - lt + 1.6, T - lt + 2.6)]
        snap = (bs[0] - (T - lt)) if bs else 2.0
        pull = ease(span(lt, 0.3, snap)) * 90 + (min(30, (lt - snap) * 300) if lt > snap else 0)
        tremble = (math.sin(T * 60) * 1.5 if lt > snap - 0.6 and lt < snap else 0)
        lx, rx = 228 - pull, 252 + pull
        cy = 140 + tremble
        pinky_hand(d, (lx, cy), -1, CORAL)
        pinky_hand(d, (rx, cy), 1, DENIM)
        if lt < snap:
            thread(img, d, (lx, cy), (rx, cy), max(0.0, 8 - pull * 0.1), RED, w=3, glow_a=0.3 + 0.4 * (pull / 90), wob=tremble)
            d.ellipse([lx - 4, cy - 4, lx + 4, cy + 4], outline=RED); d.ellipse([rx - 4, cy - 4, rx + 4, cy + 4], outline=RED)
        else:
            k = lt - snap
            mid = 240
            for side, x0 in ((-1, lx), (1, rx)):          # 断开的两截往回弹，再垂下去
                end = (mid + side * (6 + 60 * eout(clamp(k / 0.4))), cy + 50 * ein(clamp(k / 1.0)))
                ctl = ((x0 + end[0]) / 2, cy - 30 * math.exp(-k * 4) * math.sin(k * 20))
                d.line(bez((x0, cy), end, ctl, 20), fill=RED, width=3)
            if k < 0.12:
                pix.blend_box(img, (0, 0, W, H), (255, 250, 250), np.full((H, W), 0.7 * (1 - k / 0.12)))
            burst(img, d, k, mid, cy, life=1.0, scale=0.8)
            props.shake(img, k, 6, 0.4)
        vig(img, 0.5, (8, 4, 12))
        return
    # 灰色的街，人来人往；只有他们两个有颜色，擦肩而过，谁也没看谁
    k = lt - cut
    rest = dur - cut
    sky(img, ((0, (150, 156, 170)), (1, (200, 204, 210))), 0, 180)
    pix.city(img, d, 170, 21, 0, (120, 124, 136), (170, 174, 186), 40, 110, 0.3, T, blink=False)
    d.rectangle([0, 170, W, H], fill=(150, 150, 158))
    d.rectangle([0, 214, W, 218], fill=(120, 120, 128))
    for j in range(16):                                     # 灰色的人群，往两边走
        r = rng(j + 200)
        dirn = 1 if j % 2 else -1
        sp = r.uniform(30, 50)
        x = (r.uniform(0, W + 80) + dirn * T * sp) % (W + 80) - 40
        y = r.choice([200, 208, 216])
        person_s(img, r.choice(['boy', 'girl']), x, y, 1.6, r.choice(['young', 'old']), 'side', 'walk', wph(T + j * 0.3, 7), 'neutral',
                 flip=dirn < 0, tint=lerpc((96, 96, 106), (130, 130, 140), r.random()))
    u = clamp(k / rest)
    slow = u + 0.08 * math.sin(math.pi * u * 2) * 0                  # 交错的那一刻放慢
    bx = lerp(-30, 520, ease(slow) * 0.5 + slow * 0.5)
    gx = lerp(520, -30, ease(slow) * 0.5 + slow * 0.5)
    person(img, 'girl', gx, 234, 'old', 'side', 'walk', wph(T, 6), 'neutral', s=2, flip=True)
    person(img, 'boy', bx, 238, 'old', 'side', 'walk', wph(T + 0.2, 6), 'neutral', s=2)
    if abs(bx - gx) < 40:                                   # 擦肩时空气里一丝红光
        glow(img, (bx + gx) / 2, 200, 40, RED_L, 0.3 * (1 - abs(bx - gx) / 40))
    vig(img, 0.35, (40, 40, 50))


# ================================================================ 镜子前换装
for key, kw in {('girl', 'v1'): dict(top=(250, 250, 246), top_s=(220, 216, 210), low=(52, 60, 100), low_s=(40, 44, 76), long=False, bun=True,
                                     arm=(250, 250, 246)),
                ('girl', 'v2'): dict(top=(44, 40, 52), top_s=(30, 26, 38), low=(44, 40, 52), low_s=(30, 26, 38), arm=(44, 40, 52),
                                     hair=(150, 90, 70), hair_s=(110, 60, 50), hair_l=(200, 140, 110)),
                ('girl', 'v3'): dict(top=(170, 130, 230), top_s=(130, 96, 190), low=(170, 130, 230), low_s=(130, 96, 190), long=False,
                                     tail=True, acc=(255, 255, 255))}.items():
    L = dict(pix.LOOK[('girl', 'young')]); L.update(kw); pix.LOOK[key] = L


def poof(img, d, x, y, k, s=1.0):
    if not 0 <= k < 0.5: return
    u = k / 0.5
    for j in range(10):
        a = j * 0.63
        r = (8 + 26 * eout(u)) * s
        cx, cy = x + math.cos(a) * r, y + math.sin(a) * r * 0.8
        rr = (10 - 8 * u) * s
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=lerpc((255, 255, 255), (240, 220, 240), u))


def s_change(img, d, lt, dur, T, A):
    img.paste((246, 222, 222), (0, 0, W, H))
    for x in range(0, W, 16): d.line([(x, 0), (x, 200)], fill=(240, 212, 214))       # 墙纸
    for x in range(8, W, 32):
        for y in range(14, 200, 32): put(img, 'heart', x, y, 1, tint=(250, 196, 204))
    d.rectangle([0, 200, W, H], fill=(200, 160, 140))
    for x in range(0, W, 40): d.line([(x, 200), (x - 30, H)], fill=(186, 146, 128))
    # 大镜子：镜子里一直是原来的她
    mx0, mx1, my0, my1 = 290, 410, 40, 240
    d.rounded_rectangle([mx0 - 8, my0 - 8, mx1 + 8, my1 + 6], 30, fill=(210, 170, 90), outline=OUT)
    d.rounded_rectangle([mx0, my0, mx1, my1], 26, fill=(200, 226, 236))
    for j in range(3): d.line([(mx0 + 20 + j * 10, my0 + 30), (mx0 + 50 + j * 10, my0 + 4)], fill=(236, 248, 252), width=2)
    person(img, 'girl', 350, 236, 'young', 'front', 'stand', 0, 'smile', s=3, shade=(0.85, 0.9, 1.0))
    # 她跟着拍子一次次变样子
    bs = beats_in(T - lt, T - lt + dur)
    looks = ['young', 'v1', 'v2', 'v3']
    n = len([b for b in bs if b <= T])
    look = looks[min(n, 3)]
    person(img, 'girl', 160, 248, look, 'front', 'stand', 0, 'shy' if n % 2 else 'smile', 'auto', s=3)
    for b in bs:
        k = T - b
        if 0 <= k < 0.5:
            poof(img, d, 160, 190, k, 1.4)
            for j in range(6): twinkle(d, int(160 + 50 * math.cos(j)), int(180 + 40 * math.sin(j)), k * 2, (255, 255, 255), 5)
    vig(img, 0.3, (80, 40, 60))


# ================================================================ 雨夜里一路狂奔
def bouquet(d, x, y, s=2):
    d.polygon([(x - 3 * s, y - 2 * s), (x + 3 * s, y - 2 * s), (x + s, y + 5 * s), (x - s, y + 5 * s)], fill=(250, 240, 220), outline=OUT)
    for j, (dx, dy, c) in enumerate([(-2, -4, (230, 50, 80)), (1, -5, (255, 120, 150)), (3, -3, (230, 50, 80)), (-1, -2, (255, 200, 210)), (0, -7, (230, 50, 80))]):
        d.ellipse([x + dx * s - s * 1.4, y + dy * s - s * 1.4, x + dx * s + s * 1.4, y + dy * s + s * 1.4], fill=c)


def s_dash(img, d, lt, dur, T, A):
    off = lt * 260
    sky(img, ((0, (10, 10, 30)), (1, (40, 30, 70))), 0, 200)
    pix.city(img, d, 170, 3, off * 0.15, (34, 28, 66), (130, 110, 170), 50, 130, 0.3, T, 10, 24)
    pix.city(img, d, 196, 9, off * 0.4, (24, 20, 46), (255, 210, 130), 40, 110, 0.35, T)
    d.rectangle([0, 196, W, H], fill=(30, 30, 46))
    for x in range(int(-(off % 60)), W, 60): d.rectangle([x, 230, x + 30, 232], fill=(200, 196, 180))
    # 路灯和红灯往后掠
    for j in range(4):
        x = (j * 170 - off) % (W + 170) - 60
        pix.lamp(img, d, int(x), 210, 1.0, 56, (60, 60, 80), (255, 220, 150))
    tlx = W + 40 - (lt - 1.2) * 260
    if -40 < tlx < W + 40:
        d.rectangle([tlx, 120, tlx + 3, 214], fill=(70, 70, 86))
        d.rounded_rectangle([tlx - 8, 96, tlx + 11, 136], 3, fill=(40, 40, 50), outline=OUT)
        d.ellipse([tlx - 4, 100, tlx + 7, 111], fill=(255, 60, 60)); glow(img, tlx + 1.5, 105, 18, (255, 60, 60), 0.7)
        d.ellipse([tlx - 4, 112, tlx + 7, 123], fill=(60, 50, 40)); d.ellipse([tlx - 4, 124, tlx + 7, 135], fill=(40, 60, 50))
    props.reflect(img, 214, 56, T, (16, 14, 40), 0.5, 2.0, 60)
    ph = wph(T, 12)
    x, y = 210 + 6 * math.sin(lt * 2), 236
    person(img, 'boy', x, y, 'young', 'side', 'run', ph, 'happy', 'reach', s=2)
    bouquet(d, x + 22, y - 32, 2)
    if ph in (0, 2):                                         # 踩水
        for j in range(6):
            d.point((x - 4 - j * 3, y - 2 - (j % 3) * 2), fill=(170, 190, 240))
    for j in range(12):                                      # 速度线
        r = rng(j + 40)
        yy = r.uniform(30, 260); xx = (r.uniform(0, W) - off * 1.6) % W
        d.line([(xx, yy), (xx + 30, yy)], fill=(120, 120, 170))
    pix.rain(d, T, 0, W + 80, -10, H, 160, (130, 140, 200), 380, -14, 9, 5)
    vig(img, 0.4, (6, 6, 20))


# ================================================================ 一堵堵砖墙踩着拍子撞穿
def s_crash(img, d, lt, dur, T, A):
    sp = 170
    off = lt * sp
    sky(img, ((0, (40, 24, 80)), (0.6, (120, 60, 120)), (1, (250, 140, 120))), 0, 210)
    for j in range(5):
        x = (j * 130 - off * 0.3) % (W + 130) - 60
        cloud(d, x, 40 + (j % 3) * 22, 1.4, (255, 190, 200), (230, 150, 170))
    pix.hills(d, 200, 10, 0.02, off * 0.002, (90, 50, 110))
    d.rectangle([0, 214, W, H], fill=(110, 76, 70))
    for x in range(int(-(off % 24)), W, 24):                 # 地砖
        d.rectangle([x, 214, x + 22, 222], fill=(170, 116, 90), outline=(90, 56, 50))
    px = 190
    bs = beats_in(T - lt + 0.3, T - lt + dur - 0.6)
    for b in bs:
        wx = px + 16 + (b - T) * sp
        if wx > W + 40: continue
        k = T - b
        if k < 0:
            for row in range(8):                              # 还没撞的墙
                for col in range(3):
                    bx = wx + col * 9 - (4 if row % 2 else 0); by = 214 - (row + 1) * 9
                    d.rectangle([bx, by, bx + 8, by + 8], fill=(196, 90, 70), outline=(110, 50, 44))
        else:
            for row in range(8):                              # 撞飞的砖
                for col in range(3):
                    r = rng(int(b * 100) + row * 3 + col)
                    vx, vy = r.uniform(60, 220), r.uniform(-200, -40)
                    bx = wx + col * 9 + vx * k; by = 214 - (row + 1) * 9 + vy * k + 500 * k * k
                    if by > H: continue
                    d.rectangle([bx, by, bx + 7, by + 7], fill=(196, 90, 70), outline=(110, 50, 44))
            if k < 0.35:
                burst(img, d, k, wx, 170, life=0.6, scale=0.6)
                tfill(img, 'polygon', [(wx + 20 * math.cos(a) * (1 if j % 2 else 0.5), 170 + 20 * math.sin(a) * (1 if j % 2 else 0.5)) for j, a in
                                       enumerate(np.linspace(0, 2 * math.pi, 16, endpoint=False))], (255, 250, 200), 0.8 * (1 - k / 0.35))
    # 他：一直往前冲，最后跳起来把花举高
    jump = clamp((lt - (dur - 0.9)) / 0.9)
    jy = -60 * math.sin(math.pi * jump) if jump > 0 else 0
    pose = 'jump' if jump > 0 else 'run'
    person(img, 'boy', px, 214 + jy, 'young', 'side', pose, wph(T, 12), 'happy', 'up' if jump > 0 else 'reach', s=2)
    bouquet(d, px + (6 if jump > 0 else 22), 214 + jy - (88 if jump > 0 else 32), 2)
    if jump > 0:
        for j in range(8): twinkle(d, int(px + 40 * math.cos(j * 0.8 + lt)), int(214 + jy - 80 + 30 * math.sin(j * 0.8 + lt)), (lt * 2 + j * 0.1) % 1, GOLD_L, 4)
    # 左上角的心形血条：撞一次掉一点，可他一直在笑
    hits = len([b for b in bs if b <= T])
    for j in range(5):
        on = j < 5 - min(4, hits // 1)
        put(img, 'heart', 20 + j * 12, 18, 1, tint=RED if on else (90, 60, 80))
    for b in bs: props.shake(img, T - b, 4, 0.25)
    vig(img, 0.3, (30, 10, 30))


# ================================================================ 同心锁
def heart_lock(img, d, cx, cy, s, closed=1.0, glow_a=0.0, col=RED):
    """心形的锁，(cx, cy) 是锁身中心；closed 0..1 锁梁落下"""
    lift = (1 - closed) * 14 * s
    d.arc([cx - 9 * s, cy - 24 * s - lift, cx + 9 * s, cy - 6 * s - lift], 180, 360, fill=(190, 196, 210), width=max(2, int(3 * s)))
    d.line([(cx - 9 * s, cy - 15 * s - lift), (cx - 9 * s, cy - 6 * s - lift * 0.4)], fill=(190, 196, 210), width=max(2, int(3 * s)))
    d.line([(cx + 9 * s, cy - 15 * s - lift), (cx + 9 * s, cy - 8 * s)], fill=(190, 196, 210), width=max(2, int(3 * s)))
    heart(img, d, cx, cy + 2 * s, 0.9 * s, col, RED_L, glow_a=glow_a)
    d.ellipse([cx - 2 * s, cy + 2 * s, cx + 2 * s, cy + 6 * s], fill=(90, 20, 30)); d.rectangle([cx - s * 0.6, cy + 5 * s, cx + s * 0.6, cy + 9 * s], fill=(90, 20, 30))


def s_lock(img, d, lt, dur, T, A):
    sky(img, ((0, (90, 80, 160)), (0.5, (240, 150, 140)), (1, (255, 210, 150))), 0, 150)
    glow(img, 360, 140, 80, (255, 220, 160), 0.5); d.ellipse([340, 120, 380, 160], fill=(255, 240, 200))
    d.rectangle([0, 150, W, H], fill=(70, 80, 130))
    for y in range(152, H, 4):
        for x in range(int((y * 7 + T * 20) % 30) - 30, W, 30):
            d.line([(x, y), (x + 8, y)], fill=(255, 200, 160) if abs(x - 360) < 60 else (110, 120, 170))
    # 栏杆和挂满的锁
    d.rectangle([0, 60, W, 66], fill=(60, 50, 60)); d.rectangle([0, 170, W, 176], fill=(60, 50, 60))
    for x in range(10, W, 40): d.rectangle([x, 60, x + 4, 176], fill=(60, 50, 60))
    for y in (100, 136):
        d.line([(0, y), (W, y)], fill=(90, 84, 96), width=2)
    for j in range(22):
        r = rng(j + 3)
        x = r.uniform(10, 470); y = r.choice([100, 136])
        if abs(x - 240) < 40: continue
        c = r.choice([(230, 190, 80), (170, 180, 200), (120, 180, 220), (230, 120, 150)])
        d.arc([x - 4, y - 3, x + 4, y + 7], 180, 360, fill=(150, 150, 160), width=2)
        d.rounded_rectangle([x - 5, y + 3, x + 5, y + 13], 2, fill=c, outline=OUT)
    # 中间这把：拍子上咔哒锁上
    bs = beats_in(T - lt + 0.2, T - lt + dur)
    click = (bs[0] - (T - lt)) if bs else 1.0
    closed = 1.0 if lt >= click else 0.0
    k = lt - click
    heart_lock(img, d, 240, 132 - (3 if 0 <= k < 0.08 else 0), 2.2, closed, 0.35 if lt >= click else 0.0)
    d.line([(222, 100), (258, 100)], fill=(90, 84, 96), width=2)
    if 0 <= k < 0.5:
        for j in range(8): twinkle(d, int(240 + 46 * math.cos(j * 0.785)), int(120 + 40 * math.sin(j * 0.785)), k * 2, (255, 250, 220), 6)
        text(img, '咔', 300, 80, (255, 255, 255), (60, 20, 40), scale=2, alpha=1 - k / 0.5)
    # 钥匙扔进河里
    kt = click + 0.5
    if lt > kt:
        u = (lt - kt) / 1.4
        if u < 1:
            kx = lerp(260, 420, u); ky = 140 - 110 * math.sin(math.pi * u * 0.9) + 120 * u * u
            a = u * 8
            d.ellipse([kx - 4, ky - 4, kx + 4, ky + 4], outline=(255, 220, 120), width=2)
            d.line([(kx + 3 * math.cos(a), ky + 3 * math.sin(a)), (kx + 14 * math.cos(a), ky + 14 * math.sin(a))], fill=(255, 220, 120), width=2)
        else:
            w = (lt - kt - 1.4)
            for j in range(3):
                rr = (w - j * 0.2) * 40
                if rr > 0: d.ellipse([420 - rr, 250 - rr * 0.25, 420 + rr, 250 + rr * 0.25], outline=lerpc((255, 255, 255), (70, 80, 130), clamp(rr / 60)))
            if w < 0.3:
                for j in range(8): d.point((420 + (j - 4) * 3, 248 - (j % 3) * 6 * (1 - w / 0.3)), fill=(220, 236, 255))
    vig(img, 0.35, (40, 20, 40))


# ================================================================ 胶片
FILM_T = [6.5, 15.5, 21.0, 31.0, 44.0, 49.0, 56.6, 62.0, 64.5, 77.0, 83.0, 94.8, 108.0, 113.6, 119.6]


@lru_cache(None)
def film_frame(t):
    return shrink(props.SNAP(t), 112, 63)


def s_film(img, d, lt, dur, T, A):
    img.paste((16, 12, 18), (0, 0, W, H))
    tfill(img, 'polygon', [(0, 0), (60, 0), (W, 120), (W, 200)], (255, 230, 180), 0.08)
    sy0, sy1 = 66, 196
    jit = 1 if int(T * 24) % 5 == 0 else 0
    d.rectangle([0, sy0 + jit, W, sy1 + jit], fill=(30, 22, 20))
    off = 40 + lt * 90
    fw = 124
    for x in range(int(-(off % 16)), W, 16):
        d.rectangle([x + 4, sy0 + 5 + jit, x + 11, sy0 + 11 + jit], fill=(230, 220, 200))
        d.rectangle([x + 4, sy1 - 11 + jit, x + 11, sy1 - 5 + jit], fill=(230, 220, 200))
    n0 = int(off // fw)
    for j in range(n0 - 1, n0 + 6):
        x = j * fw - off
        if x > W or x + fw < 0: continue
        t = FILM_T[j % len(FILM_T)]
        fr = sepia(film_frame(t), 0.55)
        fl = 0.85 + 0.15 * math.sin(T * 40 + j)
        fr = Image.fromarray((np.asarray(fr) * fl).astype(np.uint8))
        img.paste(fr, (int(x + 6), sy0 + 33 + jit))
        d.rectangle([x + 5, sy0 + 32 + jit, x + 118, sy0 + 96 + jit], outline=(60, 46, 40))
        text(img, str(j % len(FILM_T) + 1), x + 112, sy0 + 26 + jit, (250, 200, 120), None, FONT_S, shadow=False)
    # 灰尘和划痕
    for j in range(40):
        r = rng(j + int(T * 10))
        d.point((r.uniform(0, W), r.uniform(0, H)), fill=(200, 190, 170))
    for j in range(2):
        r = rng(int(T * 8) + j * 31)
        x = r.uniform(0, W); d.line([(x, sy0), (x + r.uniform(-3, 3), sy1)], fill=(180, 170, 150))
    grain(img, T, 8)
    vig(img, 0.55, (4, 2, 6))


# ================================================================ 锁沉进越来越深的水里
def s_deep(img, d, lt, dur, T, A):
    f = clamp(lt / dur)
    top = lerpc((50, 120, 180), (8, 14, 46), f)
    bot = lerpc((20, 60, 120), (2, 4, 18), f)
    sky(img, ((0, top), (1, bot)), 0, H, 6)
    for j in range(5):                                       # 越来越淡的光柱
        x = 80 + j * 90 + 20 * math.sin(T * 0.5 + j)
        tfill(img, 'polygon', [(x - 10, 0), (x + 10, 0), (x + 50, H), (x + 10, H)], (180, 220, 255), 0.12 * (1 - f))
    off = lt * 60
    for j in range(8):                                       # 两边的水草往上退
        x = 20 + (j % 2) * 440 + (j // 2) * 8 * (1 if j % 2 == 0 else -1)
        y = (H + 60 - (off + j * 70) % (H + 120))
        for k in range(10):
            d.line([(x + 4 * math.sin(T * 2 + k * 0.5), y + k * 6), (x + 4 * math.sin(T * 2 + k * 0.5 + 0.5), y + k * 6 + 6)], fill=lerpc((40, 120, 90), (10, 30, 40), f), width=3)
    for j in range(5):                                       # 鱼的影子
        r = rng(j + 8)
        x = (r.uniform(0, W) + T * r.uniform(20, 40) * (1 if j % 2 else -1)) % (W + 40) - 20
        y = (r.uniform(0, H) - off * 0.6) % H
        c = lerpc((30, 70, 110), (6, 10, 30), f)
        d.ellipse([x - 6, y - 2, x + 6, y + 2], fill=c); d.polygon([(x + (6 if j % 2 == 0 else -6), y), (x + (10 if j % 2 == 0 else -10), y - 3), (x + (10 if j % 2 == 0 else -10), y + 3)], fill=c)
    for j in range(30):                                      # 气泡往上冒
        r = rng(j + 90)
        x = r.uniform(0, W) + 3 * math.sin(T * 3 + j)
        y = (r.uniform(0, H) - T * r.uniform(30, 70)) % H
        rr = r.choice([1, 1, 2, 3])
        d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=lerpc((200, 230, 255), (60, 80, 120), f))
    # 锁：越往深处越亮
    cy = 120 + 6 * math.sin(T * 1.3)
    glow(img, 240, cy, 50 + 50 * f, RED, 0.3 + 0.4 * f)
    heart_lock(img, d, 240 + 4 * math.sin(T * 0.9), cy, 1.6, 1.0, 0.2 + 0.3 * f)
    # 深度计
    d.rectangle([446, 30, 452, 230], fill=(20, 30, 60), outline=(120, 160, 220))
    my = lerp(34, 226, f)
    d.rectangle([440, my - 2, 458, my + 2], fill=RED_L)
    depth = int(10 + 990 * f ** 2)
    text(img, f'-{depth}m', 410, my, (200, 230, 255), (10, 20, 40), FONT_S)
    vig(img, 0.5, (2, 4, 12))


# ================================================================ 窗台上枯萎的玫瑰
def s_wilt(img, d, lt, dur, T, A):
    f = clamp(lt / (dur - 0.3))
    img.paste((214, 196, 186), (0, 0, W, H))
    for y in range(0, 190, 10): d.line([(0, y), (W, y)], fill=(206, 186, 178))
    # 窗外日夜飞转
    wx0, wy0, wx1, wy1 = 40, 30, 200, 170
    dp = lt * 1.6
    day = 0.5 + 0.5 * math.cos(2 * math.pi * dp)
    win = Image.new('RGB', (W, H)); wd = ImageDraw.Draw(win)
    sky(win, mix_stops(((0, (10, 12, 40)), (1, (40, 40, 90))), ((0, (110, 170, 240)), (1, (220, 236, 250))), day), 0, H)
    stars(wd, T, H, 1 - day, 80)
    a = 2 * math.pi * dp
    sx, sy = 120 - 90 * math.sin(a), 150 - 110 * math.cos(a)
    wd.ellipse([sx - 10, sy - 10, sx + 10, sy + 10], fill=(255, 240, 170))
    mx, my = 120 + 90 * math.sin(a), 150 + 110 * math.cos(a)
    moon(wd, mx, my, 8)
    pix.city(win, wd, 170, 11, 0, lerpc((40, 40, 70), (120, 130, 160), day), (255, 220, 140) if day < 0.5 else None, 20, 60, 0.3, T)
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rectangle([wx0, wy0, wx1, wy1], fill=255)
    img.paste(win, (0, 0), m)
    d.rectangle([wx0, wy0, wx1, wy1], outline=(150, 110, 90), width=4)
    d.line([(120, wy0), (120, wy1)], fill=(150, 110, 90), width=3); d.line([(wx0, 100), (wx1, 100)], fill=(150, 110, 90), width=3)
    # 窗台、花瓶和玫瑰
    d.rectangle([0, 190, W, 204], fill=(240, 230, 220), outline=OUT)
    d.rectangle([0, 204, W, H], fill=(170, 140, 130))
    vx = 290
    d.polygon([(vx - 12, 190), (vx + 12, 190), (vx + 8, 150), (vx + 12, 140), (vx - 12, 140), (vx - 8, 150)], fill=(150, 200, 220), outline=OUT)
    d.line([(vx - 6, 148), (vx - 6, 186)], fill=(210, 240, 250))
    bs = beats_in(T - lt, T + 0.01)
    fallen = len(bs)
    top = rose(d, vx, 146, f, s=2, petals=1 - f * 0.4)
    for j, b in enumerate(bs):                               # 每拍掉一片花瓣
        k = T - b
        r = rng(j + 5)
        u = clamp(k / 1.0)
        px = lerp(top[0], top[0] + r.uniform(-40, 40), u); py = lerp(top[1], 192 - j % 3, eout(u))
        c = lerpc((214, 30, 60), (98, 40, 50), f)
        d.rectangle([px, py, px + 3, py + 1], fill=c)
    # 墙上的钟飞快地转
    cx, cy = 400, 80
    d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(250, 246, 236), outline=OUT, width=2)
    for j in range(12):
        a = j * math.pi / 6
        d.point((cx + 25 * math.sin(a), cy - 25 * math.cos(a)), fill=OUT)
    a1 = lt * 12; a2 = lt * 1.0
    d.line([(cx, cy), (cx + 22 * math.sin(a1), cy - 22 * math.cos(a1))], fill=OUT, width=2)
    d.line([(cx, cy), (cx + 14 * math.sin(a2), cy - 14 * math.cos(a2))], fill=RED, width=3)
    for j in range(20):                                      # 飘着的灰尘
        r = rng(j + 61)
        d.point(((r.uniform(0, W) + T * 4) % W, (r.uniform(0, 190) + 3 * math.sin(T + j))), fill=(240, 230, 210))
    grade(img, 1 - 0.5 * f, (1, 1 - 0.05 * f, 1 - 0.1 * f))
    vig(img, 0.4 + 0.2 * f, (40, 30, 30))


# ================================================================ 合照从边上碎掉
PH_W, PH_H = 220, 124


@lru_cache(None)
def couple_photo():
    im = props.SNAP(9.6).crop((60, 110, 420, 270)).resize((PH_W, int(PH_W * 160 / 360)), Image.BOX)
    full = Image.new('RGB', (PH_W, PH_H), (240, 200, 180))
    full.paste(im.crop((0, 0, PH_W, min(PH_H, im.height))), (0, PH_H - min(PH_H, im.height)))
    if im.height < PH_H:
        top = props.SNAP(9.6).crop((60, 10, 420, 110)).resize((PH_W, PH_H - im.height), Image.BOX)
        full.paste(top, (0, 0))
    return full


@lru_cache(None)
def photo_card():
    """拍立得：RGBA 图和每个像素到边缘的"距离"（带一点噪声，碎得不整齐）"""
    ph = couple_photo()
    w, h = PH_W + 12, PH_H + 30
    card = Image.new('RGBA', (w, h), CREAM + (255,))
    card.paste(ph, (6, 6))
    cd = ImageDraw.Draw(card)
    cd.text((w // 2 - 20, PH_H + 9), '♥', font=FONT, fill=RED)
    card = pix.outline(card, OUT).crop((0, 0, w, h))
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy)) / (min(w, h) / 2)
    noise = np.random.default_rng(3).random((h // 3 + 1, w // 3 + 1)).repeat(3, 0).repeat(3, 1)[:h, :w]
    return card, np.clip(dist + noise * 0.12, 0, 1)


def draw_eroded(img, d, e, T, cx=240, cy=120):
    card, dist = photo_card()
    a = np.array(card)
    gone = dist < e
    a[gone, 3] = 0
    im = Image.fromarray(a)
    x0, y0 = int(cx - card.width / 2), int(cy - card.height / 2)
    img.paste(im, (x0, y0), im)
    # 碎掉的像素变成粉末往右上飘
    if e > 0:
        r = np.random.default_rng(5)
        ys, xs = np.nonzero(gone & (dist > e - 0.35))
        if len(xs):
            pick = r.choice(len(xs), min(len(xs), 260), replace=False)
            src = np.array(card)
            for i in pick:
                x, y = xs[i], ys[i]
                k = (e - dist[y, x]) / 0.35
                ox = k * 160 + 10 * math.sin(T * 2 + i); oy = -k * 90 + 6 * math.cos(T * 3 + i)
                c = tuple(int(v) for v in src[y, x, :3])
                if k < 0.9:
                    d.point((x0 + x + ox, y0 + y + oy), fill=lerpc(c, (20, 14, 30), k))


def s_forget(img, d, lt, dur, T, A):
    sky(img, ((0, (16, 12, 30)), (1, (36, 26, 50))), 0, H)
    props.bokeh(img, T, 10, [(140, 100, 180), (220, 140, 160)], 9, 0.18, 12, 28, 3)
    e = 0.82 * ease(clamp(lt / (dur - 0.3))) ** 0.9
    draw_eroded(img, d, e, T, 240, 118 + 2 * math.sin(T))
    vig(img, 0.5, (6, 4, 12))


# ================================================================ 雨夜路口的红伞，雨停在半空
def s_appear(img, d, lt, dur, T, A):
    back = 0.9
    if lt < back:                                            # 粉末飞回来，照片重新拼好
        sky(img, ((0, (16, 12, 30)), (1, (36, 26, 50))), 0, H)
        e = 0.82 * (1 - ease(lt / back))
        draw_eroded(img, d, e, T, 240, 118)
        if lt > back - 0.25: pix.dither_fade(img, (lt - back + 0.25) / 0.25, (255, 250, 245))
        return
    k = lt - back
    freeze = 2.1
    Tr = T if k < freeze else (T - k + freeze + (k - freeze) * 0.03)     # 雨和人群停在半空
    sky(img, ((0, (12, 10, 34)), (1, (40, 30, 70))), 0, 190)
    pix.city(img, d, 170, 5, 0, (30, 24, 60), (255, 200, 120), 40, 120, 0.35, T)
    for j, (x, c) in enumerate([(60, (255, 90, 158)), (200, (96, 222, 255)), (390, (255, 200, 80))]):
        d.rectangle([x, 100, x + 50, 116], outline=c, width=2); glow(img, x + 25, 108, 40, c, 0.25)
    d.rectangle([0, 190, W, H], fill=(36, 34, 52))
    for x in range(10, W, 36): d.rectangle([x, 200, x + 20, 232], fill=(220, 220, 230))       # 斑马线
    props.reflect(img, 190, 80, T, (14, 12, 36), 0.5, 1.5, 80)
    # 灰色的伞海
    for j in range(10):
        r = rng(j + 300)
        dirn = 1 if j % 2 else -1
        x = (r.uniform(0, W + 80) + dirn * Tr * r.uniform(24, 40)) % (W + 80) - 40
        if 300 < x < 360: x += 70
        y = r.choice([214, 228, 244])
        person_s(img, r.choice(['boy', 'girl']), x, y, 2, 'old', 'side', 'walk', wph(Tr + j * 0.3, 6), 'neutral', flip=dirn < 0, tint=(70, 70, 86))
        umbrella(d, x, y - 76, 26, (78, 78, 96), stick=24)
    # 她：人群里一把红伞停下来，伞往后一抬
    gx, gy = 330, 246
    lift = ease(span(k, 0.9, 1.8))
    person(img, 'girl', gx, gy, 'old', 'front', 'stand', 0, 'surprised' if k > 1.8 else 'neutral', 'umbrella', s=2)
    umbrella(d, gx + 2, gy - 84 - 14 * lift, 28, (232, 70, 80), tilt=-0.6 * lift, stick=24)
    # 他
    person(img, 'boy', 120, 250, 'old', 'side', 'stand', 0, 'surprised' if k > freeze else 'neutral', 'umbrella', s=2)
    umbrella(d, 126, 166, 28, (60, 86, 150), stick=24)
    pix.rain(d, Tr, 0, W + 40, -10, H, 220, (110, 120, 170), 360, -5, 7, 6)
    if k > freeze:                                           # 时间停住：别的都暗下去，只剩两个人
        u = ease(span(k, freeze, freeze + 0.6))
        keep = ((XX - 120) ** 2 / 50 ** 2 + (YY - 200) ** 2 / 90 ** 2 < 1) | ((XX - gx) ** 2 / 50 ** 2 + (YY - 190) ** 2 / 100 ** 2 < 1)
        gray_except(img, keep, 0.8 * u)
        darken(img, 0.0)
        glow(img, gx, 190, 70, (255, 200, 200), 0.3 * u)
        glow(img, 120, 200, 60, (200, 210, 255), 0.25 * u)
        hb = thump(T, 0.4)
        if hb > 0:
            d.ellipse([gx - 60 * (1 - hb) - 20, 190 - 50 * (1 - hb) - 16, gx + 60 * (1 - hb) + 20, 190 + 50 * (1 - hb) + 16], outline=lerpc(RED_L, (40, 30, 60), 1 - hb))
        for j in range(3):
            put(img, 'heart', gx + 18 + j * 8, 140 - j * 10 - (k - freeze) * 10, 1, alpha=u)
    vig(img, 0.45, (6, 4, 16))
