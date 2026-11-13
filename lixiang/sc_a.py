"""理想三旬 · 片头和第一段主歌。签名都是 (img, d, lt, dur, T, A)：lt 是镜头内的时间，dur 是镜头时长，T 是全片时间，A 是这一帧的音量。

雨刚停的黄昏，一辆 30 路公交从积水里开过去，露出站牌下的他和一只小黑猫，片名落在苍白的天上。
他坐上往南开的旧铁皮火车，对面的座位空了；收音机在浓烟里响，他咳了两声；金黄的田野，断了的琴弦，
楼上窗口里戴耳机的小时候的他不见了；钟飞转，路被卷进卡带，枯叶被踩碎成一个个年份。间奏里火车开上海上的长桥，夜里一只小黑猫在他身边睡着。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
from props import *          # noqa: F401,F403  共用的颜色和道具
from pix import (W, H, FONT, FONT_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky, stars,
                 person, wph, put, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, vgrad, BAYER, bayer)

YY, XX = np.mgrid[0:H, 0:W]


def wire(d, p0, p1, sag, col):
    d.line(bez(p0, p1, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + sag), 16), fill=col)


def bez(p0, p1, c, n=24):
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * c[0] + u * u * p1[0], (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * c[1] + u * u * p1[1])
            for u in (i / n for i in range(n + 1))]


def pole(d, x, base, h, col, arm=True):
    d.rectangle([x - 1, base - h, x + 1, base], fill=col)
    if arm: d.rectangle([x - 9, base - h + 4, x + 9, base - h + 5], fill=col)


def mountains(d, base, amp, freq, ph, col, off=0.0):
    for x in range(W):
        xx = x + off
        y = base - amp * (0.6 + 0.4 * math.sin(xx * freq + ph)) * (0.7 + 0.3 * math.sin(xx * freq * 2.7 + ph * 2))
        d.line([(x, int(y)), (x, H)], fill=col)


# ================================================================ 片头：雨后的车站
TITLE_Y = 64


def title_block(img, d, lt, T, cy=TITLE_Y, appear=0.55, step=0.32, sweep_at=2.2, alpha=1.0, sub=True):
    """片名一个字一个字从上面落下来，带一点回弹；落定后一道光从左往右扫过。返回片名是否全部落定"""
    s, adv, tot = title_layout(4)
    x = W / 2 - tot / 2 - 16
    for i, (c, a) in enumerate(zip(s, adv)):
        k = (lt - appear - i * step) / 0.45
        if k <= 0: x += a; continue
        g = big_glyph(c, 4)
        dy = (1 - eback(k)) * -40
        dpaste(img, g, x, cy - g.height / 2 + dy, clamp(k * 3) * alpha)
        x += a
    sw = (lt - sweep_at) / 0.9
    if 0 < sw < 1 and alpha > 0.5:
        sx = lerp(W / 2 - tot / 2 - 40, W / 2 + tot / 2 + 40, sw)
        m = (np.abs((XX - sx) + (YY - cy) * 0.5) < 6) & (np.abs(YY - cy) < 34)
        a = np.asarray(img).copy()
        lum = a[..., 0].astype(int) + a[..., 1] + a[..., 2]
        sel = m & (lum > 520)
        a[sel] = np.minimum(255, a[sel].astype(int) + 60).astype(np.uint8)
        img.paste(Image.fromarray(a))
    if sub:
        k = clamp((lt - appear - len(s) * step - 0.2) / 0.5)
        if k > 0:
            text(img, '· 像素 MV ·', W / 2, cy + 44, (255, 246, 226), (60, 40, 60), FONT_S, alpha=k * alpha)
    return lt > appear + len(s) * step + 0.45


def street_world(img, d, T, lt, bus_x=None, rain_k=0.0, clear=1.0, hero=True, cat_on=True, wind=0.0):
    """雨刚停的黄昏街口：苍白的天、散开的云、老房子、电线杆、积水的马路"""
    sky(img, PALE, 0, 200, 6)
    # 云往两边散开，中间透出暖光
    glow(img, 300, 176, 160, (255, 214, 176), 0.45 * clear, 60)
    for i, (cx, cy, s, side) in enumerate([(40, 24, 3.2, -1), (150, 10, 2.6, -1), (260, 18, 3.0, 1), (380, 6, 3.4, 1), (90, 70, 2.0, -1),
                                           (340, 64, 2.2, 1), (210, 50, 1.6, -1)]):
        x = cx + side * clear * 60 + math.sin(T * 0.2 + i) * 4
        cloud(d, x - 40, cy, s, lerpc((120, 118, 146), (178, 168, 186), 0.3 + 0.1 * (i % 3)), lerpc((96, 94, 124), (150, 140, 164), 0.3))
    # 远处的老房子
    city(img, d, 182, 3, 0, (124, 112, 140), (255, 220, 160), 22, 62, frac=0.22 * clear + 0.05, T=T, wmin=16, wmax=30)
    city(img, d, 200, 8, 40, (92, 82, 110), (255, 206, 140), 18, 48, frac=0.3 * clear + 0.05, T=T, wmin=20, wmax=40)
    # 电线杆和电线
    pc = (52, 46, 64)
    for x in (70, 250, 430):
        pole(d, x, 204, 120, pc)
    for dy in (0, 5):
        wire(d, (-40, 92 + dy), (70, 88 + dy), 6, pc); wire(d, (70, 88 + dy), (250, 88 + dy), 14, pc)
        wire(d, (250, 88 + dy), (430, 88 + dy), 14, pc); wire(d, (430, 88 + dy), (520, 92 + dy), 6, pc)
    # 电线上挂着的水珠
    for i in range(14):
        r = rng(i * 7)
        x0 = r.uniform(80, 420)
        seg = (70, 250) if x0 < 250 else (250, 430)
        u = (x0 - seg[0]) / 180
        y0 = 88 + 14 * 2 * u * (1 - u) * 2 + (5 if i % 2 else 0)
        per = r.uniform(1.4, 2.6); k = ((T + r.random() * per) % per) / per
        if k < 0.6: d.point((x0, y0 + 1), fill=(220, 230, 250))
        else: d.point((x0, y0 + 1 + (k - 0.6) ** 2 * 900), fill=(200, 214, 244))
    # 人行道
    d.rectangle([0, 200, W, 206], fill=(110, 104, 122))
    d.line([(0, 200), (W, 200)], fill=(150, 144, 160))
    d.rectangle([0, 206, W, 208], fill=(70, 64, 82))
    # 站牌
    sx = 300
    d.rectangle([sx, 150, sx + 1, 202], fill=(70, 70, 86))
    d.rounded_rectangle([sx - 12, 140, sx + 13, 162], 3, fill=(40, 110, 120))
    d.rectangle([sx - 10, 142, sx + 11, 149], fill=(240, 236, 220))
    text(img, '30', sx + 1, 156, (255, 240, 200), None, FONT_S, shadow=False)
    pix.lamp(img, d, 150, 202, on=clamp(clear * 1.2 - 0.2), h=70)
    # 他和猫
    if hero:
        pix.person(img, 'boy', 330, 204, view='back', s=2)
        if wind > 0:                                          # 公交开过去的风吹起围巾
            fl = int(wind * 8 + math.sin(T * 14) * wind * 3)
            d.rectangle([322 - fl, 174, 326, 177], fill=MUSTARD)
            d.rectangle([322 - fl, 177, 324 - fl, 180], fill=MUSTARD_S)
    if cat_on: cat(img, 362, 204, 'sit', 2, flip=True, rim=(90, 84, 110), T=T)
    # 积水的马路
    d.rectangle([0, 208, W, H], fill=(46, 48, 66))
    if bus_x is not None:
        bus(img, d, bus_x, 240, T, s=1.5, lights=1.0)
    props.reflect(img, 208, 62, T, (30, 32, 56), 0.75, 1.5, 70)
    for i in range(7):                                        # 马路上的水洼和高光
        r = rng(i * 5 + 1)
        px, py = r.uniform(0, W), r.uniform(226, 266)
        d.line([(px, py), (px + r.uniform(12, 40), py)], fill=(130, 126, 160))
    for y in range(214, H, 9):
        x = (y * 37) % W
        d.line([(x, y), (x + 20, y)], fill=(80, 82, 110))
    if rain_k > 0:
        rain(d, T, 0, W + 40, -10, 206, int(60 * rain_k), (180, 186, 214), 260, -3, 5)
        props.ripples(d, T, (0, 214, W, 268), int(18 * rain_k), (140, 140, 180), per=0.9, rmax=7)


def s_intro(img, d, lt, dur, T, A):
    # 黑暗里落下一颗雨滴，在拍点上溅开，水波一圈圈扩散，露出雨后的街口
    hit = 0.35
    bx = (lt - 0.8) * 210 - 10              # 公交车头的位置
    wind = clamp(1 - abs(bx - 520) / 180) if bx > 300 else 0
    street_world(img, d, T, lt, bus_x=bx if bx < W + 240 else None, rain_k=clamp(1 - lt / 2.2), clear=eout(lt / 4.5),
                 wind=wind)
    # 公交开过水洼溅起的水花
    if -10 < bx < W + 230:
        for wx in (bx - 183, bx - 54):
            for j in range(12):
                r = rng(j + int(T * 20) * 3)
                k = r.random()
                px = wx - k * 26; py = 238 - math.sin(k * math.pi) * r.uniform(8, 24)
                d.rectangle([px, py, px + 1, py], fill=(200, 210, 236))
    # 鸟从电线上飞起
    for j in range(5):
        k = clamp((lt - 2.0 - j * 0.08) / 2.5)
        bx0 = 180 + j * 26
        if k <= 0:
            put(img, 'bird', bx0, 84 + (j % 2) * 5, 1, tint=(52, 46, 64))
        else:
            pix.bird(d, bx0 + k * 160 + j * 8, 84 - k * 70 - j * 4, T, (60, 54, 74), j)
    done = title_block(img, d, lt, T)
    vig(img, 0.35, (20, 16, 34))
    # 片头的雨滴和水波遮罩
    if lt < hit:
        y = lerp(-10, 200, (lt / hit) ** 1.6)
        img.paste((6, 6, 14), (0, 0, W, H))
        d.line([(240, y - 10), (240, y)], fill=(200, 210, 255))
        d.point((240, y), fill=(255, 255, 255))
        return
    k = lt - hit
    if k < 1.2:
        r = eout(k / 1.2) * 420
        a = np.asarray(img).copy()
        dist = np.sqrt((XX - 240) ** 2 + ((YY - 200) * 1.6) ** 2)
        a[dist > r] = (6, 6, 14)
        ring = (np.abs(dist - r) < 2.5)
        a[ring] = np.minimum(255, a[ring].astype(int) + 90).astype(np.uint8)
        ring2 = (np.abs(dist - r * 0.7) < 1.5) & (dist < r)
        a[ring2] = np.minimum(255, a[ring2].astype(int) + 40).astype(np.uint8)
        img.paste(Image.fromarray(a))


# ================================================================ 往南开的火车：车外 / 车里
def countryside(img, d, T, off, mood=0.0, sky_stops=None, poles=True, sign=None):
    """车窗外（或者跟拍）的原野：远山、树、电线杆往左滚动。mood 0 黄昏，1 金色"""
    stops = sky_stops or mix_stops(PALE, GOLDEN, mood)
    sky(img, stops, 0, 200, 6)
    glow(img, 360, 170, 130, (255, 214, 160), 0.4, 50)
    d.ellipse([340, 150, 380, 190], fill=lerpc((255, 236, 210), (255, 244, 200), mood))
    for i in range(4):
        x = (i * 150 - off * 0.05) % (W + 160) - 80
        cloud(d, x, 30 + (i % 2) * 26, 2.0 + (i % 3) * 0.4, lerpc((200, 180, 196), (255, 214, 196), mood), lerpc((170, 150, 176), (240, 176, 166), mood))
    mountains(d, 170, 40, 0.012, 1.0, lerpc((130, 118, 156), (190, 132, 150), mood), off * 0.1)
    mountains(d, 186, 26, 0.02, 2.0, lerpc((96, 92, 124), (150, 106, 120), mood), off * 0.25)
    d.rectangle([0, 186, W, H], fill=lerpc((88, 104, 92), (170, 150, 70), mood))
    # 田埂
    for k in range(6):
        y = 192 + k * 9
        d.line([(0, y), (W, y)], fill=lerpc((76, 92, 80), (200, 176, 70), mood) if k % 2 else lerpc((100, 118, 98), (226, 196, 80), mood))
    # 树
    for i in range(7):
        r = rng(i * 3)
        x = (i * 90 + r.uniform(0, 40) - off * 0.5) % (W + 120) - 60
        pix.tree_round(d, x, 192 + r.uniform(0, 6), 0.7 + r.random() * 0.3, lerpc((70, 92, 80), (150, 140, 60), mood),
                       lerpc((96, 120, 96), (196, 176, 80), mood), lerpc((70, 56, 56), (110, 80, 50), mood))
    if poles:
        for i in range(4):
            x = (i * 160 - off * 1.2) % (W + 160) - 60
            pole(d, x, 214, 90, lerpc((60, 56, 70), (110, 80, 60), mood))
            wire(d, (x - 160, 128), (x, 128), 10, lerpc((60, 56, 70), (110, 80, 60), mood))
    if sign is not None:
        sx = sign
        d.rectangle([sx, 170, sx + 2, 214], fill=(70, 66, 80))
        d.rectangle([sx - 16, 160, sx + 18, 180], fill=(240, 236, 220)); d.rectangle([sx - 16, 160, sx + 18, 180], outline=OUT)
        text(img, '南 →', sx + 1, 170, (200, 50, 50), None, FONT, shadow=False)


def s_south(img, d, lt, dur, T, A):
    def outside(img, d, t):
        off = T * 240
        countryside(img, d, T, off, 0.25, sign=W - ((t * 240 + 100) % 900))
        props.rails(d, 232, off * 1.4, (90, 80, 84), (110, 86, 66), rail_hi=(150, 140, 140))
        d.rectangle([0, 237, W, H], fill=(84, 74, 70))
        x = 420 + t * 12
        props.smoke(img, x - 30, 232 - 52, T, n=10, vx=-120, vy=-8, life=1.6, r1=16, seed=2)
        train(img, d, x, 232, T, cars=3, hero=(0, 2), seed=4, roll=T * 30)

    def inside(img, d, t):
        compartment(img, d, T, t, mood=0.3, her=1 - ease(t / 1.6))
    shots(img, lt, [(0, outside), (2.4, inside)], 0.35)
    vig(img, 0.3, (20, 14, 30))


def compartment(img, d, T, t, mood=0.3, her=0.0, night=0.0, table=True, hero=True, catk=0.0, cat_kind='sleep', radio_on=0.0):
    """车厢里：中间一扇大窗（外面的风景在滚），左边坐着他，右边的座位空着"""
    wall = lerpc((150, 130, 116), (40, 44, 70), night)
    img.paste(wall, (0, 0, W, H))
    # 窗外
    wx0, wy0, wx1, wy1 = 130, 34, 350, 158
    sub = Image.new('RGB', (W, H)); sd = ImageDraw.Draw(sub)
    if night > 0.5:
        sky(sub, NIGHT, 0, 200, 5)
        stars(sd, T, 200, 1, 200)
        moon(sd, 300, 70, 12)
        mountains(sd, 190, 20, 0.02, 1, (20, 22, 44), T * 30)
        sd.rectangle([0, 186, W, H], fill=(14, 16, 34))
        for i in range(5):
            x = (i * 120 - T * 160) % (W + 100) - 50
            glow(sub, x, 180, 6, (255, 220, 150), 0.6)
    else:
        countryside(sub, sd, T, T * 200, mood, poles=True)
    img.paste(sub.crop((wx0 - 60, wy0 + 30, wx1 - 60, wy1 + 30)), (wx0, wy0))
    d.rectangle([wx0 - 4, wy0 - 4, wx1 + 4, wy0 - 1], fill=lerpc((110, 92, 80), (30, 30, 50), night))
    d.rectangle([wx0 - 4, wy1 + 1, wx1 + 4, wy1 + 6], fill=lerpc((110, 92, 80), (30, 30, 50), night))
    d.rectangle([wx0 - 4, wy0, wx0 - 1, wy1], fill=lerpc((110, 92, 80), (30, 30, 50), night))
    d.rectangle([wx1 + 1, wy0, wx1 + 4, wy1], fill=lerpc((110, 92, 80), (30, 30, 50), night))
    d.line([(wx0 + (wx1 - wx0) // 2, wy0), (wx0 + (wx1 - wx0) // 2, wy1)], fill=lerpc((110, 92, 80), (30, 30, 50), night))
    # 窗帘
    cur = lerpc((176, 72, 64), (70, 40, 60), night)
    for cx in (wx0 - 10, wx1 + 2):
        d.rectangle([cx, wy0 - 6, cx + 8, wy1 + 4], fill=cur)
        for y in range(wy0 - 4, wy1 + 4, 6): d.point((cx + 4, y), fill=lerpc(cur, (0, 0, 0), 0.3))
    # 光斑：窗外的光一块块扫过车厢
    if night < 0.5:
        k = (T * 0.8) % 1
        tfill(img, 'polygon', [(wx0 + k * 300 - 150, wy1), (wx0 + k * 300 - 90, wy1), (wx0 + k * 300 - 40, H), (wx0 + k * 300 - 120, H)],
              (255, 220, 170), 0.15)
    # 小桌
    if table:
        tc = lerpc(WOOD, (50, 46, 70), night)
        d.rectangle([wx0 + 40, 168, wx1 - 40, 174], fill=tc)
        d.rectangle([wx0 + 40, 174, wx1 - 40, 176], fill=lerpc(tc, (0, 0, 0), 0.3))
        d.rectangle([W / 2 - 3, 176, W / 2 + 3, 230], fill=lerpc(tc, (0, 0, 0), 0.3))
        # 茶杯
        d.rectangle([wx0 + 70, 158, wx0 + 80, 168], fill=lerpc((240, 236, 226), (90, 96, 130), night))
        d.arc([wx0 + 77, 160, wx0 + 84, 166], 270, 90, fill=lerpc((240, 236, 226), (90, 96, 130), night))
        props.smoke(img, wx0 + 75, 156, T, n=4, col=(240, 236, 236), shade=None, vx=2, vy=-10, life=1.6, r0=1, r1=4, a=0.7 * (1 - night), seed=7)
        radio(img, d, wx1 - 76, 154, 0.45, T, on=radio_on, dial=0.6)
    # 座椅
    seat = lerpc((120, 70, 70), (50, 40, 70), night)
    seat_s = lerpc(seat, (0, 0, 0), 0.3)
    for sx, flip in ((20, False), (W - 20, True)):
        x0, x1 = (sx, sx + 90) if not flip else (sx - 90, sx)
        back = (x0, 110, x0 + 22, 240) if not flip else (x1 - 22, 110, x1, 240)
        d.rounded_rectangle(back, 6, fill=seat)
        d.rounded_rectangle([x0, 196, x1, 222], 4, fill=seat)
        d.rectangle([x0, 218, x1, 222], fill=seat_s)
    sh = (1 - 0.4 * night, 1 - 0.4 * night, 1 - 0.2 * night)
    if hero: pix.person(img, 'boy', 76, 222 + 6, view='side', pose='sit', s=3, shade=sh)
    if her > 0:
        ghost(img, 'girl', W - 76, 228, 3, her, view='side', pose='sit', flip=True)
    if her < 1:
        # 她留在座位上的黄发卡
        hx, hy = W - 70, 194
        d.rectangle([hx, hy, hx + 5, hy + 2], fill=(255, 214, 80)); d.point((hx + 1, hy - 1), fill=(255, 236, 150))
        if her < 0.6: twinkle(d, hx + 3, hy - 2, (T * 0.7) % 1, (255, 250, 210), 3)
    if catk > 0:
        cat(img, 130, 197, cat_kind, 2, flip=False, rim=(110, 104, 140), alpha=catk, T=T)
    if night > 0:
        darken(img, 0.0)


def s_radio(img, d, lt, dur, T, A):
    # 小桌上的收音机特写；窗外是车头冒出来的浓烟，烟里飘着诗一样的字和音符
    img.paste((140, 118, 104), (0, 0, W, H))
    wx0, wy0, wx1, wy1 = 40, 10, 440, 150
    sub = Image.new('RGB', (W, H)); sd = ImageDraw.Draw(sub)
    countryside(sub, sd, T, T * 220, 0.35)
    # 浓烟从窗外滚过：一条往左翻滚的烟带，只画在窗里
    for i in range(30):
        r = rng(i * 13)
        k = ((T * r.uniform(0.8, 1.1) / 2.4) + r.random()) % 1
        x = lerp(wx1 + 60, wx0 - 70, k); y = 40 + 50 + r.uniform(-34, 40) * (0.5 + k) + 8 * math.sin(T * 1.3 + i)
        rr = r.uniform(12, 26) * (0.7 + 0.7 * k)
        props.puff(sub, x, y, rr, lerpc((96, 92, 104), (196, 190, 196), r.random() * 0.8 + k * 0.2), 0.75 - 0.35 * k, (70, 66, 82))
    img.paste(sub.crop((wx0, wy0 + 40, wx1, wy1 + 40)), (wx0, wy0))
    d.rectangle([wx0 - 8, wy0 - 8, wx1 + 8, wy0 - 1], fill=(104, 84, 72))
    d.rectangle([wx0 - 8, wy1 + 1, wx1 + 8, wy1 + 10], fill=(104, 84, 72))
    d.rectangle([wx0 - 8, wy0, wx0 - 1, wy1], fill=(104, 84, 72)); d.rectangle([wx1 + 1, wy0, wx1 + 8, wy1], fill=(104, 84, 72))
    # 桌面
    d.rectangle([0, 186, W, H], fill=WOOD)
    d.rectangle([0, 186, W, 189], fill=WOOD_L)
    for y in (204, 226, 250): d.line([(0, y), (W, y)], fill=WOOD_D)
    # 收音机：指针先扫一遍，再停在一个台上
    tune = clamp(lt / 1.3)
    dial = 0.15 + 0.7 * ease(tune) + (0.04 * math.sin(lt * 18) * (1 - tune))
    on = 0.4 + 0.6 * tune
    rx, ry = 200, 148
    radio(img, d, rx, ry, 2, T, on=on, dial=dial)
    # 声波
    if tune >= 1:
        for j in range(3):
            k = ((T - 0.2) * 0.9 + j / 3) % 1
            r = 40 + k * 120
            d.arc([rx - 30 - r, ry - r * 0.8, rx - 30 + r, ry + r * 0.8], 200, 250, fill=lerpc((255, 240, 200), (140, 118, 104), k))
    # 他伸手拧旋钮
    if lt < 1.6:
        k = 1 - ease(clamp((lt - 1.0) / 0.6))
        hx, hy = rx + 58 + (1 - k) * 80, ry + 25 + (1 - k) * 30
        d.polygon([(hx + 8, hy), (W + 10, hy + 30), (W + 10, hy + 60), (hx + 6, hy + 14)], fill=(96, 118, 84))
        d.rounded_rectangle([hx - 6, hy - 2, hx + 10, hy + 12], 4, fill=SKIN)
        d.line([(hx - 6, hy + 4), (hx, hy + 4)], fill=SKIN_S)
    # 烟里飘起来的字（像诗句一样的小方块）和音符
    for j in range(7):
        r = rng(j * 29)
        k = ((T * 0.18 + r.random()) % 1)
        x = rx - 20 + r.uniform(-30, 30) + k * r.uniform(-60, 120); y = ry - 40 - k * 130
        a = clamp(min(k * 5, (1 - k) * 3)) * tune
        for c in range(r.randint(3, 6)):
            bx = x + c * 5
            dpaste(img, glyph_bit(j * 7 + c), bx, y, a)
    notes(img, d, T, 6, (rx - 70, 20, rx + 120, ry - 40), seed=3, speed=22)
    vig(img, 0.35, (30, 20, 30))


@lru_cache(None)
def glyph_bit(seed):
    """一个 4×5 的小方块"字"（随机笔画，读不出来，像远处的诗句）"""
    r = rng(seed)
    im = Image.new('RGBA', (4, 5))
    for y in range(5):
        for x in range(4):
            if r.random() < 0.5: im.putpixel((x, y), (255, 248, 230, 255))
    return im


# ================================================================ 咳嗽的特写
def s_cough(img, d, lt, dur, T, A):
    img.paste((150, 126, 112), (0, 0, W, H))
    wx0, wy0, wx1, wy1 = 250, 20, 470, 190
    sub = Image.new('RGB', (W, H)); sd = ImageDraw.Draw(sub)
    clearing = ease(clamp((lt - 2.8) / 1.6))
    countryside(sub, sd, T, T * 200, 0.35 + 0.6 * clearing)
    img.paste(sub.crop((wx0 - 100, wy0 + 20, wx1 - 100, wy1 + 20)), (wx0, wy0))
    for i in range(14):
        r = rng(i * 17 + 3)
        k = ((T * r.uniform(0.7, 1.2) / 2.6) + r.random()) % 1
        x = lerp(wx1 + 30, wx0 - 30, k); y = r.uniform(wy0, wy1 - 20)
        props.puff(img, x, y, r.uniform(12, 24), (170, 166, 176), 0.85 * (1 - clearing), (120, 116, 130))
    d.rectangle([wx0 - 6, wy0 - 6, wx1 + 6, wy0 - 1], fill=(104, 84, 72)); d.rectangle([wx0 - 6, wy1 + 1, wx1 + 6, wy1 + 8], fill=(104, 84, 72))
    d.rectangle([wx0 - 6, wy0, wx0 - 1, wy1], fill=(104, 84, 72))
    # 咳嗽：踩在两个拍点上
    coughs = [b - (T - lt) for b in beats_in(T - lt + 0.6, T - lt + 3.0)][:2] or [1.1, 2.3]
    jolt = 0; expr = 'neutral'
    for c in coughs:
        k = lt - c
        if 0 <= k < 0.45: jolt = round(3 * (1 - k / 0.45)); expr = 'cough'
    if lt > coughs[-1] + 0.8: expr = 'smile' if lt > dur - 1.6 else 'neutral'
    cx, top = 150, 36 + jolt
    bust(img, d, 'boy', cx, top, 5, expr)
    # 拳头挡在嘴前
    near = any(-0.3 <= lt - c < 0.7 for c in coughs)
    if near:
        fx, fy = cx + 24, top + 100
        d.rounded_rectangle([fx - 12, fy - 10, fx + 12, fy + 12], 5, fill=SKIN)
        for j in range(3): d.line([(fx - 10, fy - 4 + j * 5), (fx - 2, fy - 4 + j * 5)], fill=SKIN_S)
        d.polygon([(fx - 4, fy + 10), (fx + 12, fy + 10), (fx + 30, H), (fx - 20, H)], fill=(96, 118, 84))
    for c in coughs:                                          # 咳出来的小烟团
        k = lt - c
        if 0 <= k < 1.2:
            for j in range(4):
                props.puff(img, cx + 40 + k * 50 + j * 6, top + 96 - k * 16 + j * 3, 3 + k * 7, (230, 226, 230), 0.8 * (1 - k / 1.2))
    vig(img, 0.3, (30, 20, 30))


# ================================================================ 金色田野里的小火车
def s_lovely(img, d, lt, dur, T, A):
    sky(img, GOLDEN, 0, 190, 6)
    glow(img, 380, 150, 170, (255, 230, 170), 0.5, 80)
    d.ellipse([354, 124, 406, 176], fill=(255, 244, 206))
    for i, (cx, cy, s) in enumerate([(30, 30, 2.2), (170, 56, 1.6), (270, 20, 2.4)]):
        cloud(d, cx + T * 4 % 40, cy, s, (255, 222, 206), (246, 180, 170), (255, 244, 236))
    # 爱心形的小云
    hx, hy = 120 + T * 3 % 30, 40
    d.polygon(heart_poly(hx, hy, 0.9), fill=(255, 226, 222))
    mountains(d, 176, 30, 0.015, 0.3, (214, 150, 150))
    mountains(d, 190, 18, 0.025, 1.7, (186, 130, 120))
    # 油菜花田
    d.rectangle([0, 190, W, H], fill=(236, 196, 64))
    for k in range(12):
        y = 192 + k * 7
        for x in range(-(k * 5) % 9, W, 9):
            d.point((x, y), fill=(255, 232, 110) if (x + k) % 2 else (210, 168, 50))
    # 弯弯的铁路路基
    base = lambda x: 200 + 14 * math.sin(x * 0.01 + 0.6)
    for x in range(W):
        y = base(x)
        d.line([(x, y), (x, y + 6)], fill=(150, 116, 80))
        if x % 6 < 3: d.point((x, y - 1), fill=(110, 92, 80))
    d.line([(x, base(x) - 2) for x in range(0, W, 4)], fill=(90, 80, 84))
    # 小火车（远处，半大）
    tx = 120 + lt * 130
    train(img, d, tx, int(base(tx)) - 1, T, cars=3, s=0.7, hero=(0, 3), seed=4, roll=T * 30)
    props.smoke(img, tx - 21, base(tx) - 36, T, n=8, col=(255, 250, 244), shade=(240, 214, 210), vx=-60, vy=-14, life=1.6, r0=2, r1=9, seed=5)
    # 路口挥手的小孩和小狗
    for j, (px, who) in enumerate([(300, 'girl'), (318, 'boy')]):
        wave = int(T * 6) % 4
        props.person_s(img, who, px, 236, 1, age='kid', view='front', arms='wave', ph=wave, expr='laugh')
    dx = 342 + math.sin(T * 6) * 2
    d.rectangle([dx - 6, 228, dx + 4, 232], fill=(250, 240, 226)); d.rectangle([dx + 3, 224, dx + 7, 229], fill=(250, 240, 226))
    d.point((dx + 6, 225), fill=OUT); d.rectangle([dx + 4, 223, dx + 5, 224], fill=(200, 150, 110))
    d.line([(dx - 6, 228), (dx - 9 + math.sin(T * 20) * 2, 224)], fill=(250, 240, 226))
    for k in (dx - 5, dx - 2, dx + 1, dx + 3): d.line([(k, 232), (k, 235)], fill=(250, 240, 226))
    # 向日葵和蝴蝶
    for j in range(9):
        x = 20 + j * 52 + (j % 2) * 10
        pix.flower(d, x, 268, None, 3, h=22 + (j % 3) * 4)
    for j in range(4):
        pix.butterfly(d, int(80 + j * 100 + 20 * math.sin(T * 1.5 + j)), int(150 + 20 * math.sin(T * 2 + j * 2)), T, [(255, 255, 255), (255, 170, 200)][j % 2], j)
    vig(img, 0.25, (120, 60, 50))


# ================================================================ 琴弦
def s_strings(img, d, lt, dur, T, A):
    img.paste((54, 42, 50), (0, 0, W, H))
    # 斜着照进来的一束光
    tfill(img, 'polygon', [(40, 0), (130, 0), (360, H), (200, H)], (255, 220, 160), 0.18)
    d.rectangle([0, 220, W, H], fill=(70, 52, 52))
    d.line([(0, 220), (W, 220)], fill=(96, 74, 70))
    snap = beat_after(T - lt + 0.6) - (T - lt)
    k = lt - snap
    # 灰尘
    for j in range(40):
        r = rng(j * 11)
        x = r.uniform(60, 330) + 10 * math.sin(T * 0.4 + j); y = (r.uniform(0, H) - T * 6 * r.random()) % H
        if (x - 40) * H / 320 - 20 < y * 1.0 < (x - 40) * H / 200 + 40:
            d.point((x, y), fill=(255, 230, 190))
    slack = 1.0 if k < 0 else 0.0
    guitar(img, d, 250, 170, 1.4, slack=slack * 0.8, T=T, broken=2 if k >= 0 else -1)
    if 0 <= k < 0.25:
        pix.dither_fade(img, 0.5 * (1 - k / 0.25), (255, 250, 230))
    if 0 <= k < 1.0:
        hy = 170 - 1.4 * 98
        for j in range(10):
            a = j * 0.63
            r = 4 + k * 40
            d.point((250 + math.cos(a) * r, hy + math.sin(a) * r * 0.7 + k * k * 20), fill=lerpc((255, 240, 200), (54, 42, 50), k))
    props.shake(img, k, 3, 0.3)
    vig(img, 0.5, (14, 10, 18))


# ================================================================ 夜里窗口戴耳机的小孩
def s_kid(img, d, lt, dur, T, A):
    sky(img, NIGHT, 0, H, 5)
    stars(d, T, H, 1, 220)
    moon(d, 400, 46, 16)
    glow(img, 400, 46, 50, (240, 230, 200), 0.25)
    gone = beat_after(T - lt + 1.9) - (T - lt)          # 他抬头的那一拍，窗里的灯灭了
    k = lt - gone
    off = ease(clamp(k / 0.8))
    # 老楼
    bx0, bx1 = 120, 340
    d.rectangle([bx0, 40, bx1, H], fill=(52, 48, 78))
    d.rectangle([bx0 - 4, 36, bx1 + 4, 42], fill=(40, 36, 62))
    for wy in (60, 150):
        for wx in (140, 290):
            on_ = rng(wx + wy).random() < 0.5
            d.rectangle([wx, wy, wx + 30, wy + 28], fill=(255, 206, 130) if on_ else (30, 30, 56))
    # 中间那扇大窗：小时候的他戴着耳机，坐在窗台上听收音机
    wx0, wy0, wx1, wy1 = 186, 76, 274, 146
    lit = 1 - off
    d.rectangle([wx0, wy0, wx1, wy1], fill=lerpc((26, 26, 52), (255, 206, 130), lit))
    if lit > 0: glow(img, (wx0 + wx1) / 2, (wy0 + wy1) / 2, 90, (255, 200, 120), 0.3 * lit)
    d.rectangle([wx0 - 3, wy1, wx1 + 3, wy1 + 4], fill=(90, 84, 110))
    d.rectangle([wx0, wy0, wx1, wy0 + 2], fill=(40, 36, 62))
    d.line([((wx0 + wx1) // 2, wy0), ((wx0 + wx1) // 2, wy0 + 10)], fill=(40, 36, 62))
    kid_a = 1 - ease(clamp(k / 0.9))
    if kid_a > 0:
        ghost(img, 'boy', 214, wy1 + 2, 2, kid_a, age='kid', view='side', pose='sit', expr='closed')
        # 耳机
        if kid_a > 0.5:
            d.arc([202, 97, 228, 128], 180, 360, fill=(230, 70, 70))
            d.rectangle([209, 109, 214, 117], fill=(230, 70, 70))
        radio(img, d, 252, wy1 - 9, 0.35, T, on=lit, dial=0.4)
        notes(img, d, T, 8, (wx0 - 20, 0, wx1 + 60, wy0 + 20), seed=8, speed=16)
    # 楼下的路灯和他
    d.rectangle([0, 230, W, H], fill=(30, 28, 50))
    pix.lamp(img, d, 380, 232, 1.0, 60)
    walk_in = clamp(lt / 1.8)
    px = lerp(520, 410, ease(walk_in))
    if walk_in < 1: pix.person(img, 'boy', px, 234, view='side', pose='walk', ph=wph(T), flip=True, s=2)
    else: pix.person(img, 'boy', px, 234, view='back', s=2)
    cat(img, px + 30, 234, 'sit' if walk_in >= 1 else 'walk', 2, flip=True, rim=(90, 84, 120), T=T)
    vig(img, 0.4, (8, 6, 20))


# ================================================================ 时光匆匆
def s_time(img, d, lt, dur, T, A):
    f = lt / dur
    day = 0.5 + 0.5 * math.sin(lt * 9)
    sky(img, mix_stops(NIGHT, DAY, day, 12), 0, H, 5)
    stars(d, T, H, 1 - day, 160)
    # 日月绕着钟转
    a = lt * 9
    sx, sy = 240 + math.cos(a) * 200, 150 + math.sin(a) * 120
    d.ellipse([sx - 14, sy - 14, sx + 14, sy + 14], fill=(255, 236, 170))
    mx, my = 240 - math.cos(a) * 200, 150 - math.sin(a) * 120
    moon(d, mx, my, 10)
    # 飞走的日历纸
    for j in range(12):
        r = rng(j * 41)
        k = (lt * 0.8 + r.random()) % 1
        x = lerp(300, -60, k) + r.uniform(-40, 140); y = lerp(160, -40, k) + r.uniform(-30, 80)
        rot = math.sin(T * 6 + j) * 4
        d.polygon([(x, y), (x + 18, y + rot), (x + 18 - rot, y + 22 + rot), (x - rot, y + 22)], fill=(250, 246, 236))
        d.rectangle([x + 2, y + 2, x + 15, y + 6], fill=(220, 70, 60))
        d.line([(x + 4, y + 12), (x + 13, y + 12)], fill=(150, 140, 140))
    cx, cy = 240, 130
    clock(d, cx, cy, 72, lt * 3, lt * 36)
    for j in range(8):                                        # 指针扫过留下的残影
        aa = lt * 36 - j * 0.12
        d.line([(cx, cy), (cx + math.sin(aa) * 55, cy - math.cos(aa) * 55)], fill=lerpc((40, 30, 40), (250, 240, 214), 0.4 + j * 0.08))
    vig(img, 0.35, (20, 14, 30))


# ================================================================ 颠沛磨成卡带
def s_tape(img, d, lt, dur, T, A):
    img.paste((70, 50, 46), (0, 0, W, H))
    glow(img, 300, 100, 260, (255, 200, 140), 0.35, 180)
    d.rectangle([0, 210, W, H], fill=(110, 74, 54)); d.line([(0, 210), (W, 210)], fill=(150, 104, 74))
    cx, cy = 300, 140
    wound = 0.2 + 0.6 * lt / dur
    (lx, ly), (rx, ry) = cassette(img, d, cx, cy, 2, T, spin=1.6, wound=wound)
    # 一条坑坑洼洼的路从左边卷进卡带：路上的小火车、雨滴、公交、音符一个个被卷进去
    pts = []
    for i in range(80):
        u = i / 79
        x = lerp(-20, lx - 10, u)
        y = 180 + 26 * math.sin(u * 9 - T * 3) * (1 - u) + 10 * math.sin(u * 23 + T * 2) * (1 - u) * 0.5
        y = lerp(y, ly + 24, u ** 3)
        pts.append((x, y))
    d.line([(x, y + 2) for x, y in pts], fill=(50, 28, 20), width=7)
    d.line(pts, fill=(124, 78, 50), width=7)
    d.line([(x, y - 2) for x, y in pts], fill=(160, 110, 70))
    icons = ['drop', 'note', 'heart', 'star', 'bird']
    for j in range(6):
        u = (lt * 0.35 + j / 6) % 1
        i = min(79, int(u * 79))
        x, y = pts[i]
        a = clamp((1 - u) * 6)
        if j % 3 == 0:
            train(img, d, x + 16, y - 3, T, cars=1, s=0.3, people=False, rust=0, roll=T * 40)
        else:
            dpaste(img, pix.spr(icons[j % len(icons)], 2), x - 6, y - 16, a)
    vig(img, 0.4, (20, 12, 16))


# ================================================================ 枯叶踩碎成年代
LEAVES_GROUND = [(rng(i).uniform(20, 460), rng(i + 99).uniform(200, 262), i % 3) for i in range(46)]


def leaf(d, x, y, kind, s=2, curl=0.6):
    cols = [((176, 104, 48), (130, 70, 36)), ((210, 150, 60), (160, 104, 40)), ((150, 80, 50), (104, 54, 36))][kind]
    d.ellipse([x - 5 * s, y - 2 * s, x + 5 * s, y + 2 * s], fill=cols[0])
    d.arc([x - 5 * s, y - 3 * s, x + 5 * s, y + 3 * s], 200, 340, fill=cols[1])
    d.line([(x - 5 * s, y), (x + 5 * s, y)], fill=cols[1])
    if curl > 0: d.ellipse([x + 3 * s, y - 3 * s, x + 6 * s, y], fill=cols[1])


def s_leaves(img, d, lt, dur, T, A):
    sky(img, ((0, (230, 190, 140)), (1, (180, 120, 90))), 0, 200, 5)
    props.bokeh(img, T, 10, [(255, 220, 160), (255, 190, 120), (240, 160, 110)], seed=4, a=0.35, rmin=10, rmax=26)
    d.rectangle([0, 190, W, H], fill=(150, 116, 96))
    for x in range(0, W, 40): d.line([(x, 190), (x - 30, H)], fill=(130, 98, 82))
    d.line([(0, 190), (W, 190)], fill=(176, 140, 116))
    steps = [b - (T - lt) for b in beats_in(T - lt + 0.6, T - lt + dur - 0.6)][:2] or [1.2, 3.6]
    feet = [(200, steps[0]), (300, steps[1] if len(steps) > 1 else 3.6)]
    crushed = []
    for fx, st in feet:
        k = lt - st
        crushed.append((fx, k))
    for x, y, kind in LEAVES_GROUND:
        hit = any(k >= 0 and abs(x - fx) < 36 and y > 214 for fx, k in crushed)
        if not hit: leaf(d, x, y, kind)
    # 碎片飞起来，变成一个个年份
    for fx, k in crushed:
        if k < 0: continue
        for j in range(26):
            r = rng(j * 7 + fx)
            ang = r.uniform(math.pi * 1.1, math.pi * 1.9); sp = r.uniform(30, 90)
            px = fx + math.cos(ang) * sp * eout(k / 0.8); py = 236 + math.sin(ang) * sp * eout(k / 0.8) - k * 8
            if k < 1.2:
                d.rectangle([px, py, px + 1, py + 1], fill=[(176, 104, 48), (210, 150, 60), (150, 80, 50)][j % 3])
        for j in range(4):
            r = rng(j * 13 + fx)
            yr = str(r.choice([1998, 2003, 2006, 2009, 2012, 2016, 2019]))
            kk = clamp((k - 0.3 - j * 0.15) / 2.2)
            if kk <= 0: continue
            px = fx + r.uniform(-60, 60) + math.sin(T + j) * 6; py = 220 - kk * 150
            text(img, yr, px, py, lerpc((255, 246, 220), (240, 190, 130), kk), (90, 56, 40), FONT, alpha=clamp(min(kk * 5, (1 - kk) * 3)))
    # 靴子踩下来
    for fx, st in feet:
        k = lt - st
        if k < -0.5 or k > 1.6: continue
        if k < 0: y = lerp(-20, 236, ease((k + 0.5) / 0.5))
        elif k < 0.9: y = 236
        else: y = lerp(236, -40, ein((k - 0.9) / 0.7))
        d.polygon([(fx - 34, -10), (fx + 24, -10), (fx + 18, y - 52), (fx - 26, y - 52)], fill=(56, 54, 70))
        d.line([(fx + 6, -10), (fx + 4, y - 52)], fill=(44, 42, 56))
        d.polygon([(fx - 30, y - 56), (fx + 22, y - 56), (fx + 24, y - 20), (fx + 60, y - 14), (fx + 66, y - 4), (fx + 66, y), (fx - 30, y)],
                  fill=(128, 84, 56))
        d.polygon([(fx - 30, y - 56), (fx + 22, y - 56), (fx + 22, y - 50), (fx - 30, y - 50)], fill=(96, 62, 42))
        d.line([(fx + 24, y - 18), (fx + 58, y - 12)], fill=(160, 112, 76))
        d.rectangle([fx - 30, y - 5, fx + 66, y], fill=(64, 42, 32))
        for k in range(4): d.point((fx + 2 + k * 6, y - 40 + k * 6), fill=(200, 180, 150))
        if 0 <= k < 0.3: props.shake(img, k, 3, 0.3)
    leaves(d, T, 18, seed=2)
    vig(img, 0.35, (60, 30, 20))


# ================================================================ 间奏：海上的长桥 / 夜里的车厢和小黑猫
def s_bridge(img, d, lt, dur, T, A):
    f = lt / dur
    stops = mix_stops(((0, (60, 64, 120)), (0.5, (170, 120, 160)), (0.8, (240, 160, 140)), (1, (255, 206, 160))), NIGHT, ease(f))
    sky(img, stops, 0, 170, 6)
    stars(d, T, 170, ease(f), 200)
    moon(d, 380, 60 - 20 * f, 14)
    glow(img, 380, 60 - 20 * f, 60, (240, 230, 200), 0.3 * f)
    # 远处的岛和灯塔
    d.polygon([(400, 170), (430, 156), (470, 160), (490, 170)], fill=lerpc((90, 70, 100), (20, 20, 40), f))
    d.rectangle([446, 132, 451, 160], fill=lerpc((230, 220, 220), (90, 90, 110), f))
    if int(T * 1.5) % 2 == 0: glow(img, 448, 132, 18, (255, 240, 180), 0.7)
    d.rectangle([0, 170, W, H], fill=lerpc((120, 100, 140), (14, 16, 40), f))
    # 桥
    deck = 150
    bc = lerpc((60, 50, 70), (14, 12, 26), f)
    for x in range(-20, W + 40, 60):
        d.rectangle([x, deck + 4, x + 6, 172], fill=bc)
    d.rectangle([0, deck, W, deck + 5], fill=bc)
    for x in range(-30, W + 40, 30):
        d.line([(x, deck), (x + 15, deck - 22)], fill=bc); d.line([(x + 30, deck), (x + 15, deck - 22)], fill=bc)
    d.line([(0, deck - 22), (W, deck - 22)], fill=bc)
    tx = -60 + lt * 120
    train(img, d, tx, deck, T, cars=3, night=0.4 + 0.5 * f, lit=clamp(f * 2), seed=4, hero=(0, 2), roll=T * 30, headlight=clamp(f * 2))
    props.smoke(img, tx - 30, deck - 52, T, n=8, col=lerpc((220, 210, 220), (90, 88, 120), f), shade=None, vx=-70, vy=-10, life=1.8, r1=12, seed=6)
    props.reflect(img, 172, 98, T, (14, 16, 40), 0.6, 2.5, 110)
    props.ripples(d, T, (0, 190, W, 268), 12, lerpc((170, 150, 190), (60, 60, 110), f), per=2.0, rmax=12)
    vig(img, 0.35, (10, 8, 24))


def s_nightcar(img, d, lt, dur, T, A):
    # 夜里的车厢：别人都睡了，他看着窗外的海；一只小黑猫从右边走过来，在他身边蜷着睡下
    compartment(img, d, T, lt, night=1.0, her=0.0, catk=0)
    walk = clamp(lt / 1.8)
    cx = lerp(W + 20, 130, ease(walk))
    if walk < 1:
        cat(img, cx, 197, 'walk', 2, flip=True, rim=(110, 104, 140), T=T)
    elif lt < 2.4:
        cat(img, cx, 197, 'sit', 2, flip=True, rim=(110, 104, 140), T=T)
    else:
        cat(img, cx, 197, 'sleep', 2, flip=True, rim=(110, 104, 140), T=T)
    # 他低头看了一眼猫
    vig(img, 0.45, (6, 6, 20))
