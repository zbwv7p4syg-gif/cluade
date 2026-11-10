"""我好想你 · 第二段主歌和第二段副歌。同样的歌词换一组画面：

餐桌上的吊灯亮起来，对面的椅子上浮出"你"；剖开的大房子里每间都亮着灯却只有一个人；灯一间间熄掉，镜头拉远，
一模一样的房子铺满画面；地铁里灰色的人群和胸口裂开的心；沿着河往前走，路牌上的岁数越来越大、头发越来越白；
码头上小船开远，夜里灯塔扫过空空的海；老电视里的回忆变成雪花，人在沙发上睡着；灰掉的心坐着纸船漂进雾里。
副歌：对着日出的群山喊，回声一层层弹回来；沙滩上写的字被浪抹平；人潮里踮脚张望，远处一闪而过的红围巾；
旋转木马上她的影子一圈圈转回来；雨夜的路灯下闭着眼，身边浮出撑伞的人又散掉；咖啡馆里笑着说"挺好的"，头顶却是一朵雨云。
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
from sc_a import scarf_tail, props_text_l, MEM_T, season_cols, day_cycle
from sc_b import rainy_street, umbrella, ferris

pix.SPR['horse'] = ["...........YW..", "..........YWWW.", ".........YYWKWW", "Y.......YYWWWWW", "YY...RRRRWWW...", "YYWWWRRRRWWW...",
                    ".YWWWWRRWWWW...", "..WWWWWWWWWW...", "..WWW....WWW...", "..WW......WW...", ".WW......WW....", ".K.......K....."]


def gperson(img, who, x, y, s=2, col=(120, 128, 156), k=0.82, flip=False, **kw):
    """灰色的路人：保留明暗，去掉颜色"""
    im = pix.char_img(who, kw.get('age', 'young'), kw.get('view', 'side'), kw.get('pose', 'stand'), kw.get('ph', 0) % 4, kw.get('expr', 'neutral'),
                      kw.get('arms', 'auto'))
    a = np.array(im).astype(float)
    g = a[..., :3] @ np.array([0.3, 0.59, 0.11])
    a[..., :3] = (g[..., None] / 255 * 0.7 + 0.3) * np.array(col) * k + a[..., :3] * (1 - k) * 0.5
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    ax = pix.CX
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT); ax = pix.CW - 1 - pix.CX
    if s != 1: im = im.resize((int(pix.CW * s), int(pix.CH * s)), Image.NEAREST)
    img.paste(im, (int(round(x - ax * s)), int(round(y - pix.FY * s))), im)


# ================================================================ 开了灯 眼前的模样（餐桌）
def s_table(img, d, lt, dur, T, A):
    on = 1.0 if lt > 0.12 and not 0.22 < lt < 0.28 else 0.0
    ga = ease(span(lt, 0.7, 1.5)) * (1 - ease(span(lt, 2.7, 3.7)))
    d.rectangle([0, 0, W, 150], fill=(222, 206, 184)); d.rectangle([0, 150, W, 208], fill=(186, 150, 124)); d.line([(0, 150), (W, 150)], fill=(150, 116, 96))
    for x in range(0, W, 30): d.line([(x, 152), (x, 206)], fill=(170, 134, 110))
    d.rectangle([0, 208, W, H], fill=(140, 98, 72))
    for x in range(0, W, 48): d.line([(x, 208), (x - 20, H)], fill=(120, 82, 62))
    window(img, d, 40, 40, 70, 72, T, moon_at=(48, 18, 8))
    # 架子、冰箱、钟
    for sy in (58, 96):
        d.rectangle([330, sy, 400, sy + 3], fill=(150, 104, 76))
        for k in range(5):
            c = [(236, 196, 100), (120, 170, 190), (226, 120, 110), (250, 246, 236), (150, 190, 130)][(k + sy) % 5]
            d.rectangle([336 + k * 13, sy - 12 + (k % 2) * 3, 344 + k * 13, sy - 1], fill=c)
    d.rectangle([414, 70, 462, 208], fill=(214, 224, 230)); d.rectangle([414, 70, 462, 72], fill=(240, 246, 250)); d.line([(414, 120), (462, 120)], fill=(170, 180, 190))
    d.rectangle([418, 92, 420, 110], fill=(150, 160, 170)); d.rectangle([418, 130, 420, 160], fill=(150, 160, 170))
    d.rectangle([436, 84, 446, 92], fill=(255, 150, 160)); put(img, 'heart', 441, 100, 1)
    clock(d, 266, 40, 12, T * 0.02 + 1.2, T * 0.25)
    # 两把椅子
    for cx, sgn in ((150, 1), (330, -1)):
        d.rectangle([cx - 14, 188, cx + 14, 192], fill=(170, 120, 84))
        d.rectangle([cx - 14 * sgn - (2 if sgn > 0 else 0), 150, cx - 14 * sgn + (2 if sgn < 0 else 0), 208], fill=(140, 96, 66))
        d.rectangle([cx + 12 * sgn - 1, 192, cx + 12 * sgn + 1, 208], fill=(140, 96, 66))
        d.rectangle([min(cx - 14 * sgn, cx - 10 * sgn), 156, max(cx - 14 * sgn, cx - 10 * sgn), 160], fill=(140, 96, 66))
    person(img, 'boy', 156, 209, view='side', pose='sit', expr='surprised' if 0.9 < lt < 1.9 else ('sad' if lt > 2.6 else 'neutral'), arms='eat', ph=int(lt * 2), s=2)
    # 桌子：一边一副碗筷
    d.rectangle([176, 168, 304, 173], fill=(190, 138, 96)); d.rectangle([176, 173, 304, 176], fill=(150, 104, 76))
    for lx in (182, 294): d.rectangle([lx, 176, lx + 4, 208], fill=(150, 104, 76))
    for k in range(8): d.rectangle([180 + k * 16, 165, 187 + k * 16, 167], fill=(226, 96, 96) if k % 2 else (250, 246, 236))
    for bx, used in ((204, True), (276, False)):
        d.pieslice([bx - 9, 152, bx + 9, 170], 0, 180, fill=(250, 246, 236), outline=OUT); d.rectangle([bx - 9, 160, bx + 9, 161], fill=(120, 170, 200))
        d.line([(bx + 13, 164), (bx + 23, 164)], fill=(150, 104, 76)); d.line([(bx + 13, 166), (bx + 23, 166)], fill=(150, 104, 76))
        if used:
            d.rectangle([bx - 7, 157, bx + 7, 160], fill=(255, 250, 240))
            for k in range(3):
                kk = (T * 0.5 + k / 3) % 1
                d.point((bx - 4 + k * 4 + 2 * math.sin(kk * 6 + k), 154 - kk * 16), fill=lerpc((250, 250, 250), (200, 186, 170), kk))
    d.rectangle([238, 152, 243, 166], fill=(130, 190, 210)); pix.flower(d, 240, 152, (255, 130, 150), kind=2, h=7)
    # 吊灯
    d.line([(240, 0), (240, 52)], fill=(60, 54, 60)); sh = lerpc((120, 110, 120), (255, 236, 170), on)
    d.polygon([(230, 52), (250, 52), (262, 70), (218, 70)], fill=sh, outline=OUT)
    lighting(img, [(240, 110, 250, 1.25 * on, 190), (75, 76, 70, 0.4)], amb=0.14)
    if on:
        glow(img, 240, 72, 34, (255, 236, 170), 0.6); tfill(img, 'polygon', [(220, 70), (260, 70), (360, 208), (120, 208)], (255, 236, 170), 0.07)
    if ga > 0:
        glow(img, 326, 170, 40, (255, 230, 170), 0.3 * ga)
        ghost(img, 'girl', 324, 209, 2, ga * 0.85, view='side', pose='sit', expr='happy', flip=True, arms='eat', ph=int(lt * 2))
    if lt > 2.7:
        for i in range(30):
            r = rng(i * 11)
            k = lt - 2.7 - r.random() * 0.6
            if k <= 0 or k > 1.2: continue
            d.point((324 + r.uniform(-12, 12) + 6 * math.sin(k * 5 + i), 196 - r.uniform(0, 50) - k * 30), fill=lerpc((255, 240, 190), (120, 100, 90), k / 1.2))
    vig(img, 0.4)


# ================================================================ 偌大的房 寂寞的床 / 关了灯 全都一个样（剖开的房子）
HX0, HX1, HY0, HY1, HYM = 96, 384, 74, 214, 142
ROOMS = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]            # (列, 层)；(2, 0) 是卧室
ROOM_COL = [(214, 204, 226), (206, 226, 222), (226, 214, 200), (230, 214, 190), (214, 222, 204), (232, 220, 200)]
OFF_ORDER = [3, 4, 5, 0, 1, 2]                                        # 熄灯的顺序，卧室最后


def room_box(i):
    c, r = ROOMS[i]; w = (HX1 - HX0) // 3
    y0 = HY0 if r == 0 else HYM + 2
    return HX0 + c * w + 2, y0 + 2, HX0 + (c + 1) * w - 2, (HYM if r == 0 else HY1) - 2


def house(img, d, T, lit, me_expr='neutral'):
    """lit：六间房各自亮不亮（0..1）"""
    sky(img, NIGHT4, 0, H, 6)
    stars(d, T, 190, 1.0, 200)
    glow(img, 60, 50, 60, (180, 190, 255), 0.3); moon(d, 60, 50, 16)
    pix.hills(d, 206, 12, 0.012, 0.3, (26, 30, 66))
    d.rectangle([0, 216, W, H], fill=(22, 30, 54)); d.line([(0, 216), (W, 216)], fill=(40, 56, 80))
    pix.grass(d, 218, (30, 44, 66), (50, 70, 90), T, 0, W, 4)
    for tx, s_ in ((36, 1.5), (440, 1.8)): pix.tree_round(d, tx, 218, s_, leaf=(30, 60, 76), leaf_l=(44, 82, 92), trunk=(40, 36, 56))
    for fx in range(0, 90, 10): d.rectangle([fx, 204, fx + 5, 216], fill=(70, 76, 110))
    for fx in range(392, W, 10): d.rectangle([fx, 204, fx + 5, 216], fill=(70, 76, 110))
    d.rectangle([420, 190, 436, 200], fill=(150, 50, 60)); d.rectangle([427, 200, 429, 216], fill=(60, 50, 60))      # 那只红信箱
    # 屋顶和烟囱
    d.rectangle([320, 26, 338, 60], fill=(110, 70, 70)); d.rectangle([317, 24, 341, 29], fill=(140, 90, 86))
    d.polygon([(HX0 - 16, HY0), (HX1 + 16, HY0), (HX1 - 40, 30), (HX0 + 40, 30)], fill=(96, 60, 76))
    for y in range(34, HY0, 8): d.line([(HX0 + 40 - (y - 30) * 1.25, y), (HX1 - 40 + (y - 30) * 1.25, y)], fill=(76, 46, 62))
    d.rectangle([HX0 - 3, HY0, HX1 + 3, HY1 + 2], fill=(70, 50, 60))
    for i in range(6):
        x0, y0, x1, y1 = room_box(i)
        wall = ROOM_COL[i]
        d.rectangle([x0, y0, x1, y1], fill=wall); d.rectangle([x0, y1 - 5, x1, y1], fill=(150, 110, 84))
        d.rectangle([x0, y1 - 8, x1, y1 - 6], fill=lerpc(wall, (0, 0, 0), 0.18))
        cx = (x0 + x1) // 2
        d.line([(cx, y0), (cx, y0 + 6)], fill=(70, 60, 70)); d.polygon([(cx - 5, y0 + 6), (cx + 5, y0 + 6), (cx + 7, y0 + 11), (cx - 7, y0 + 11)], fill=(250, 236, 180))
        fy = y1 - 6
        if i == 0:      # 书房
            d.rectangle([x0 + 4, fy - 44, x0 + 30, fy], fill=(130, 90, 66))
            for sy in range(fy - 40, fy - 4, 10):
                d.rectangle([x0 + 6, sy, x0 + 28, sy + 7], fill=(96, 64, 50))
                for k in range(5): d.rectangle([x0 + 7 + k * 4, sy + 1, x0 + 9 + k * 4, sy + 7], fill=[(210, 90, 80), (90, 140, 190), (236, 196, 100), (140, 190, 140)][(k + sy) % 4])
            d.rectangle([x0 + 44, fy - 20, x0 + 84, fy - 17], fill=(170, 120, 84)); d.rectangle([x0 + 46, fy - 17, x0 + 48, fy], fill=(140, 96, 66)); d.rectangle([x0 + 80, fy - 17, x0 + 82, fy], fill=(140, 96, 66))
            d.rectangle([x0 + 54, fy - 34, x0 + 72, fy - 21], fill=(52, 54, 72)); d.rectangle([x0 + 56, fy - 32, x0 + 70, fy - 23], fill=(120, 150, 200))
        elif i == 1:    # 浴室
            for ty in range(y0 + 14, fy, 8): d.line([(x0, ty), (x1, ty)], fill=lerpc(wall, (255, 255, 255), 0.4))
            d.rounded_rectangle([x0 + 10, fy - 20, x0 + 62, fy], 6, fill=(250, 250, 252), outline=(170, 180, 190))
            d.rectangle([x0 + 12, fy - 16, x0 + 60, fy - 12], fill=(170, 214, 236))
            d.rectangle([x0 + 70, fy - 46, x0 + 86, fy - 26], fill=(190, 226, 240)); d.rectangle([x0 + 70, fy - 46, x0 + 86, fy - 26], outline=(250, 250, 252))
            d.rectangle([x0 + 70, fy - 18, x0 + 86, fy - 14], fill=(250, 250, 252)); d.rectangle([x0 + 76, fy - 14, x0 + 80, fy], fill=(230, 232, 240))
            for k, c in enumerate(((120, 170, 230), (248, 204, 88))): d.rectangle([x0 + 72 + k * 5, fy - 24, x0 + 73 + k * 5, fy - 18], fill=c)      # 两把牙刷
        elif i == 2:    # 卧室
            d.rectangle([x1 - 30, y0 + 16, x1 - 8, y0 + 36], fill=(26, 28, 70)); d.rectangle([x1 - 30, y0 + 16, x1 - 8, y0 + 36], outline=(250, 250, 252))
            d.point((x1 - 16, y0 + 22), fill=(255, 250, 220))
            d.rectangle([x0 + 8, fy - 26, x0 + 12, fy], fill=(130, 90, 66)); d.rectangle([x0 + 12, fy - 12, x0 + 70, fy - 4], fill=(240, 236, 230))
            d.rectangle([x0 + 12, fy - 4, x0 + 72, fy], fill=(130, 90, 66)); d.rectangle([x0 + 28, fy - 14, x0 + 70, fy - 5], fill=(96, 128, 176))
            d.rounded_rectangle([x0 + 13, fy - 17, x0 + 25, fy - 12], 2, fill=(252, 250, 246))
            h = head_img('boy', 'young', 'closed' if me_expr == 'closed' else 'neutral', 1, 'side')
            img.paste(h, (x0 + 13, fy - 30), h)
            d.rectangle([x0 + 28, fy - 16, x0 + 50, fy - 12], fill=(128, 160, 204))
            d.rectangle([x0 + 76, fy - 12, x0 + 86, fy], fill=(140, 96, 70)); d.rectangle([x0 + 79, fy - 20, x0 + 83, fy - 12], fill=(250, 236, 180))
        elif i == 3:    # 客厅
            d.rounded_rectangle([x0 + 8, fy - 22, x0 + 56, fy], 4, fill=(110, 140, 180)); d.rectangle([x0 + 12, fy - 14, x0 + 52, fy - 8], fill=(140, 170, 206))
            for k in range(2): d.rectangle([x0 + 14 + k * 24, fy - 20, x0 + 30 + k * 24, fy - 13], fill=[(248, 204, 88), (226, 120, 110)][k])
            d.rectangle([x0 + 66, fy - 12, x0 + 88, fy], fill=(120, 84, 62)); d.rectangle([x0 + 64, fy - 30, x0 + 90, fy - 12], fill=(40, 40, 56))
            d.rectangle([x0 + 66, fy - 28, x0 + 88, fy - 14], fill=(70, 90, 130))
            d.rectangle([x0 + 22, y0 + 16, x0 + 42, y0 + 30], fill=(110, 76, 60)); d.rectangle([x0 + 24, y0 + 18, x0 + 40, y0 + 28], fill=(250, 200, 160))
        elif i == 4:    # 楼梯和门
            for k in range(9): d.rectangle([x0 + 4 + k * 6, y0 + 6 + k * 6, x0 + 60, y0 + 9 + k * 6], fill=(170, 124, 90))
            for k in range(0, 9, 2): d.line([(x0 + 5 + k * 6, y0 - 6 + k * 6), (x0 + 5 + k * 6, y0 + 6 + k * 6)], fill=(120, 84, 62))
            d.line([(x0 + 4, y0 - 6), (x0 + 54, y0 + 44)], fill=(120, 84, 62))
            d.rectangle([x1 - 26, fy - 40, x1 - 6, fy], fill=(150, 90, 70)); d.point((x1 - 22, fy - 20), fill=(250, 220, 120))
            d.rectangle([x1 - 30, fy - 3, x1 - 2, fy], fill=(200, 96, 96))
        else:           # 厨房
            d.rectangle([x0 + 6, fy - 16, x0 + 50, fy], fill=(226, 230, 236)); d.rectangle([x0 + 6, fy - 18, x0 + 50, fy - 16], fill=(170, 120, 84))
            d.rectangle([x0 + 6, fy - 46, x0 + 50, fy - 34], fill=(200, 150, 110))
            d.rectangle([x0 + 22, fy - 22, x0 + 32, fy - 18], fill=(96, 104, 120)); d.rectangle([x0 + 38, fy - 26, x0 + 44, fy - 18], fill=(226, 120, 110))
            d.rectangle([x0 + 62, fy - 52, x0 + 86, fy], fill=(214, 224, 230)); d.line([(x0 + 62, fy - 30), (x0 + 86, fy - 30)], fill=(170, 180, 190))
            d.rectangle([x0 + 65, fy - 46, x0 + 66, fy - 36], fill=(150, 160, 170))
        k = clamp(lit[i])
        if k < 1: tfill(img, 'rectangle', [x0, y0, x1, y1], (12, 14, 44), 0.8 * (1 - k))
        if k > 0: glow(img, cx, y0 + 12, 44, (255, 236, 170), 0.4 * k)
    d.rectangle([HX0 - 3, HYM - 1, HX1 + 3, HYM + 1], fill=(70, 50, 60))
    d.rectangle([HX0 - 8, HY1 + 2, HX1 + 8, HY1 + 6], fill=(60, 54, 70))


def s_house(img, d, lt, dur, T, A):
    house(img, d, T, [1] * 6)
    e = ease(span(lt, 0.5, 5.2))
    zoomf(img, lerp(3.2, 1, e), lerp(338, 240, e), lerp(110, 135, e))
    vig(img, 0.3 + 0.2 * e)


def s_same(img, d, lt, dur, T, A):
    lit = [1 - clamp((lt - 0.15 - OFF_ORDER.index(i) * 0.24) / 0.06) for i in range(6)]
    house(img, d, T, lit, me_expr='closed' if lt > 2 else 'neutral')
    t0 = 1.75
    if lt > t0:                                 # 镜头越拉越远：一模一样的房子铺满画面
        s = lerp(1, 0.2, ease(span(lt, t0, dur + 0.3)))
        w, h = max(8, int(round(W * s))), max(5, int(round(H * s)))
        tile = img.resize((w, h), Image.BOX)
        ox = (W - w) // 2; oy = (H - h) // 2
        for ty in range(oy % h - h, H, h):
            for tx in range(ox % w - w, W, w):
                img.paste(tile, (tx, ty))
    vig(img, 0.5)


# ================================================================ 心里的伤 无法分享（地铁）
def s_subway(img, d, lt, dur, T, A):
    jit = 1 if int(T * 9) % 7 == 0 else 0
    d.rectangle([0, 0, W, H], fill=(196, 204, 214))
    d.rectangle([0, 0, W, 34], fill=(226, 230, 236)); d.rectangle([0, 34, W, 37], fill=(150, 158, 172))
    for x in range(30, W, 120): d.rectangle([x, 8, x + 60, 13], fill=(255, 255, 244)); glow(img, x + 30, 12, 40, (255, 255, 240), 0.3)
    # 车窗：隧道里一闪一闪的灯
    for wx in (20, 300):
        d.rectangle([wx, 64, wx + 160, 136], fill=(14, 14, 30))
        for i in range(6):
            lx = wx + (i * 53 - T * 520) % 200 - 20
            if wx < lx < wx + 150: d.rectangle([lx, 92, lx + 16, 94], fill=(255, 226, 150)); d.rectangle([lx - 20, 93, lx, 93], fill=(140, 120, 90))
        d.rectangle([wx, 64, wx + 160, 136], outline=(150, 158, 172), width=3); d.rectangle([wx + 78, 64, wx + 81, 136], fill=(150, 158, 172))
    d.rectangle([196, 44, 284, 214], fill=(176, 186, 200)); d.rectangle([239, 44, 241, 214], fill=(130, 138, 152))
    for dx in (204, 248): d.rectangle([dx, 62, dx + 28, 124], fill=(14, 14, 30)); d.rectangle([dx, 62, dx + 28, 124], outline=(130, 138, 152))
    for k, c in enumerate(((236, 150, 150), (150, 200, 236), (240, 220, 150), (170, 220, 170))):
        d.rectangle([24 + k * 40, 42, 58 + k * 40, 58], fill=c) if k < 4 else None
        d.rectangle([304 + k * 40, 42, 338 + k * 40, 58], fill=c)
    # 座椅和地板
    for sx in (0, 290):
        d.rectangle([sx, 160, sx + 190, 190], fill=(70, 150, 150)); d.rectangle([sx, 160, sx + 190, 164], fill=(100, 180, 176)); d.rectangle([sx, 190, sx + 190, 214], fill=(56, 110, 116))
    d.rectangle([0, 214, W, H], fill=(128, 132, 150)); d.rectangle([0, 214, W, 216], fill=(156, 160, 176))
    for x in range(0, W, 24): d.point((x + 6, 240), fill=(110, 114, 132))
    # 扶手和吊环
    d.rectangle([0, 46 + jit, W, 48 + jit], fill=(210, 214, 224))
    for x in range(16, W, 44):
        sw = round(3 * math.sin(T * 3 + x))
        d.line([(x, 48 + jit), (x + sw, 66 + jit)], fill=(120, 126, 140)); d.ellipse([x + sw - 4, 66 + jit, x + sw + 4, 76 + jit], outline=(240, 240, 246), width=2)
    # 坐着的人：都低头看手机
    for i, (x, who) in enumerate(((36, 'girl'), (84, 'boy'), (140, 'girl'), (330, 'boy'), (386, 'girl'), (440, 'boy'))):
        gperson(img, who, x, 216 + jit, 2, view='front', pose='sit', expr='down', arms='phone')
        glow(img, x, 180 + jit, 12, (170, 210, 255), 0.35 + 0.1 * math.sin(T * 3 + i))
    gperson(img, 'boy', 110, 244 + jit, 2, view='side', expr='down', arms='phone', col=(104, 112, 140))
    gperson(img, 'girl', 372, 246 + jit, 2, view='side', expr='down', arms='phone', flip=True, col=(104, 112, 140))
    # "我"和胸口的那颗心
    x, y = 240, 246 + jit
    pl = thump(T, 0.3)
    person(img, 'boy', x, y, view='front', expr='closed' if lt > 4.6 else 'sad', arms='up' if False else 'down', s=2)
    d.rectangle([x + 17, 48, x + 19, y], fill=(214, 218, 228)); d.line([(x + 17, 48), (x + 17, y)], fill=(160, 166, 180))            # 扶着的立杆
    d.line([(x + 10, y - 30), (x + 17, y - 38)], fill=pix.LOOK[('boy', 'young')]['arm'], width=3); d.rectangle([x + 16, y - 41, x + 20, y - 37], fill=pix.SKIN)
    glow(img, x, y - 22, 22 + 5 * pl, (255, 90, 110), 0.5 + 0.2 * pl)
    for b in beats_in(T - 1.0, T + 0.01):
        k = (T - b) / 1.0; rr = 8 + 40 * k
        d.ellipse([x - rr, y - 22 - rr * 0.8, x + rr, y - 22 + rr * 0.8], outline=lerpc((255, 110, 130), (150, 150, 170), k))
    heart(d, x, y - 24, 0.42 + 0.05 * pl, crack=1.0)
    a = eback(span(lt, 0.8, 1.1)) * (1 - span(lt, 4.2, 4.8))
    if a > 0.05:
        bubble(img, d, x + 26, 112, x + 100, 144, tail=(x + 14, 170), a=clamp(a))
        if a > 0.9:
            n = int((lt - 1.1) / 0.4) % 4 if lt < 3.4 else 0
            for k in range(n): d.ellipse([x + 44 + k * 14, 124, x + 50 + k * 14, 130], fill=(90, 80, 100))
            if lt >= 3.4: d.line([(x + 40, 120), (x + 86, 136)], fill=(200, 70, 80), width=2); d.line([(x + 86, 120), (x + 40, 136)], fill=(200, 70, 80), width=2)
    grade(img, sat=0.9)
    vig(img, 0.4)


# ================================================================ 生命 随年月流去 随白发老去（沿着河往前走）
def s_river(img, d, lt, dur, T, A):
    f = clamp(lt / dur)
    st, night = day_cycle(0.15 + lt * 0.5)
    sky(img, st, 0, 150, 5)
    if night > 0: stars(d, T, 120, night, 120)
    a = ((0.15 + lt * 0.5) % 1) * 2 * math.pi
    sx, sy = 240 - 220 * math.cos(a), 150 - 130 * math.sin(a)
    if sy < 150: glow(img, sx, sy, 36, (255, 230, 160), 0.5); d.ellipse([sx - 11, sy - 11, sx + 11, sy + 11], fill=(255, 244, 190))
    mx, my = 240 + 220 * math.cos(a), 150 + 130 * math.sin(a)
    if my < 150: moon(d, mx, my, 9)
    off = lt * 70
    sf = f * 4
    leaf, leaf_l, ground = season_cols(sf)
    dk = lambda c: lerpc(c, (20, 24, 60), 0.5 * night)
    pix.hills(d, 138, 12, 0.012, off * 0.004, dk(lerpc(ground, (90, 110, 150), 0.5)))
    d.rectangle([0, 146, W, 156], fill=dk(lerpc(ground, (60, 80, 110), 0.25)))
    for k in range(-1, 6):                      # 对岸的树
        x = k * 110 - (off * 0.4 % 110)
        if sf < 3.2: pix.tree_round(d, x + 30, 152, 1.0 + (k % 2) * 0.3, dk(leaf), dk(leaf_l), trunk=dk((112, 74, 50)))
        else: d.line([(x + 30, 152), (x + 30, 132)], fill=dk((112, 74, 50)), width=2); d.line([(x + 30, 140), (x + 38, 128)], fill=dk((112, 74, 50))); d.line([(x + 30, 138), (x + 23, 128)], fill=dk((112, 74, 50)))
    # 河：往身后流
    img.paste(pix.vgrad(W, 46, ((0, dk((120, 176, 220))), (1, dk((70, 120, 190)))), 4), (0, 156))
    for i in range(46):
        r = rng(i * 3)
        x = (r.uniform(0, W + 60) - lt * (150 + 90 * r.random())) % (W + 60) - 30; y = r.uniform(159, 199)
        d.line([(x, y), (x + r.randint(6, 18), y)], fill=dk((190, 224, 250)))
    for i in range(7):                          # 漂走的日历纸、叶子和钟
        r = rng(i * 7 + 1)
        x = (r.uniform(0, W + 80) - lt * 190) % (W + 80) - 40; y = r.uniform(164, 194) + math.sin(T * 3 + i)
        if i == 0:
            clock(d, x, y - 4, 7, T * 2, T * 9)
        elif i % 2:
            d.rectangle([x, y - 4, x + 8, y + 3], fill=(250, 246, 236)); d.rectangle([x, y - 4, x + 8, y - 2], fill=(214, 70, 76)); d.point((x + 4, y + 1), fill=(60, 50, 70))
        else: d.rectangle([x, y, x + 3, y + 1], fill=leaf_l)
        d.line([(x - 3, y + 4), (x + 12, y + 4)], fill=dk((210, 236, 255)))
    # 这边的岸和路
    d.rectangle([0, 202, W, H], fill=dk(ground)); d.rectangle([0, 202, W, 204], fill=dk(lerpc(ground, (255, 255, 255), 0.3)))
    d.rectangle([0, 226, W, 250], fill=dk((206, 190, 160))); d.line([(0, 226), (W, 226)], fill=dk((226, 214, 190)))
    pix.grass(d, 208, dk(lerpc(ground, (0, 0, 0), 0.2)), dk(lerpc(ground, (255, 255, 255), 0.25)), T, 0, W, 4)
    for k in range(-1, 5):                      # 路牌上的岁数
        n = int((off + 240) // 170) + k - 1
        x = n * 170 - off + 240
        age_n = 20 + n * 8
        if 20 <= age_n <= 90 and -30 < x < W + 30:
            d.rectangle([x - 1, 196, x + 1, 226], fill=dk((120, 100, 90)))
            d.rectangle([x - 12, 180, x + 12, 196], fill=dk((250, 246, 236))); d.rectangle([x - 12, 180, x + 12, 196], outline=dk((120, 100, 90)))
            text(img, str(age_n), x, 188, col=dk((90, 70, 80)), out=None, font=FONT_S, shadow=False)
    age = ['young', 'young', 'a1', 'a2', 'a3', 'a4', 'a5', 'a5'][min(7, int(f * 7.6))]
    rate = lerp(8, 4, f)
    px, py = 240, 240
    d.ellipse([px - 14, py - 2, px + 14, py + 3], fill=dk(lerpc((206, 190, 160), (0, 0, 0), 0.25)))
    if f > 0.6: d.line([(px + 16, py), (px + 12, py - 26)], fill=(110, 76, 60), width=2)       # 拐杖
    person(img, 'boy', px, py, age=age, view='side', pose='walk', ph=int(lt * rate), expr='closed' if f > 0.7 else 'sad', s=2,
           shade=(1 - 0.35 * night, 1 - 0.35 * night, 1 - 0.15 * night) if night > 0 else None)
    if sf < 1.1: pix.petals(d, T, 30, speed=22, wind=-60)
    elif 1.9 < sf < 3.1: leaves(d, T, 34, speed=30, wind=-70)
    elif sf >= 3.1: pix.snow(d, T, 140, speed=30, wind=-8)


# ================================================================ 随着你离去 快乐渺无音讯（码头）
def pier(d, y=206, x1=262, night=0.0):
    c = lambda col: lerpc(col, (16, 18, 46), 0.6 * night)
    for px in range(10, x1, 42): d.rectangle([px, y, px + 4, H], fill=c((96, 64, 48)))
    d.rectangle([0, y - 6, x1, y], fill=c((170, 120, 84))); d.line([(0, y - 6), (x1, y - 6)], fill=c((204, 150, 106)))
    for px in range(0, x1, 14): d.line([(px, y - 5), (px, y)], fill=c((130, 90, 66)))
    d.rectangle([x1 - 5, y - 20, x1 - 1, y], fill=c((96, 64, 48)))


def dock_leave(img, d, t):
    sky(img, DUSK4, 0, 170, 6)
    glow(img, 380, 160, 110, (255, 226, 160), 0.55); d.ellipse([360, 142, 400, 182], fill=(255, 240, 190))
    for i in range(4): cloud(d, (i * 160 + t * 5) % 660 - 120, 22 + (i * 31) % 60, 1.7, (255, 204, 170), (240, 156, 150))
    img.paste(pix.vgrad(W, 102, ((0, (255, 190, 140)), (0.3, (214, 136, 150)), (1, (80, 88, 160))), 6), (0, 168))
    for i in range(50):
        r = rng(i)
        gx = r.uniform(0, W); gy = r.uniform(170, 264)
        if math.sin(t * 4 + i) > 0: d.line([(gx, gy), (gx + r.randint(2, 9), gy)], fill=(255, 240, 210) if abs(gx - 380) < 26 + (gy - 168) * 0.4 else (236, 180, 190))
    # 小船越开越远
    k = ease(clamp(t / 3.6))
    bx, by = lerp(300, 372, k), lerp(204, 174, k); s = lerp(1.5, 0.3, k)
    d.polygon([(bx - 22 * s, by - 6 * s), (bx + 24 * s, by - 6 * s), (bx + 17 * s, by), (bx - 17 * s, by)], fill=(250, 246, 236), outline=OUT)
    d.rectangle([bx - 8 * s, by - 14 * s, bx + 6 * s, by - 6 * s], fill=(120, 170, 200)); d.line([(bx + 2 * s, by - 14 * s), (bx + 2 * s, by - 30 * s)], fill=OUT)
    d.polygon([(bx + 2 * s, by - 30 * s), (bx + 2 * s, by - 18 * s), (bx + 14 * s, by - 18 * s)], fill=(226, 96, 96))
    if s > 0.7: person_s(img, 'girl', bx - 14 * s, by - 5 * s, s * 0.9, view='side', arms='wave', ph=int(t * 6), flip=True)
    else: d.rectangle([bx - 14 * s - 1, by - 14 * s, bx - 14 * s + 1, by - 6 * s], fill=(248, 204, 88)); d.point((bx - 14 * s, by - 14 * s), fill=SCARF)
    for i in range(5): d.line([(bx - 24 * s - i * 9 * s, by + 1 + i * 0.5), (bx - 30 * s - i * 9 * s, by + 1 + i * 0.5)], fill=(255, 250, 240))
    for i in range(4): pix.bird(d, 150 + i * 20 + t * 10, 70 + (i % 2) * 8 + i * 5, t, col=(110, 70, 100), ph=i)
    pier(d)
    person(img, 'boy', 236, 201, view='side', arms='wave' if t < 2.4 else 'down', ph=int(t * 6), expr='sad', s=2)


def dock_wait(img, d, t):
    sky(img, NIGHT4, 0, 170, 6); stars(d, t, 168, 1.0, 200)
    moon(d, 96, 46, 12); glow(img, 96, 46, 44, (180, 190, 255), 0.3)
    img.paste(pix.vgrad(W, 102, ((0, (40, 44, 110)), (1, (14, 16, 50))), 6), (0, 168))
    for i in range(40):
        r = rng(i + 3)
        gx = r.uniform(0, W); gy = r.uniform(172, 264)
        if math.sin(t * 3 + i) > 0.2: d.line([(gx, gy), (gx + r.randint(2, 8), gy)], fill=(90, 100, 180))
    # 灯塔的光一圈圈扫过空空的海
    lx, ly = 430, 104
    d.polygon([(400, 176), (W, 176), (W, 196), (388, 196)], fill=(20, 22, 50))
    d.polygon([(lx - 9, 176), (lx + 9, 176), (lx + 6, ly + 8), (lx - 6, ly + 8)], fill=(214, 214, 226)); d.rectangle([lx - 7, 136, lx + 7, 148], fill=(190, 70, 80))
    d.rectangle([lx - 7, ly, lx + 7, ly + 8], fill=(255, 240, 180)); d.polygon([(lx - 9, ly), (lx + 9, ly), (lx, ly - 9)], fill=(190, 70, 80))
    a = math.sin(t * 0.9) * 0.5
    ex, ey = lx - 460 * math.cos(a), ly + 460 * math.sin(a) + 40
    tfill(img, 'polygon', [(lx, ly + 4), (ex, ey - 46), (ex, ey + 46)], (255, 244, 200), 0.16)
    glow(img, lx, ly + 4, 22, (255, 240, 180), 0.6)
    bx = 320 + 6 * math.sin(t * 0.8); by = 214 + 2 * math.sin(t * 1.7)                     # 漂回来的空瓶子
    d.rounded_rectangle([bx - 8, by - 3, bx + 5, by + 3], 2, fill=(150, 210, 200), outline=(60, 90, 100)); d.rectangle([bx + 5, by - 1, bx + 9, by + 1], fill=(150, 210, 200))
    d.rectangle([bx + 9, by - 2, bx + 11, by + 2], fill=(170, 120, 84)); ripples(d, t, (bx - 14, by + 3, bx + 14, by + 6), 2, (120, 130, 200), seed=2, rmax=10)
    pier(d, night=1.0)
    d.rectangle([222, 188, 228, 200], fill=(255, 220, 130)); d.rectangle([221, 186, 229, 188], fill=(60, 50, 60)); glow(img, 225, 194, 30, (255, 210, 130), 0.4)
    person(img, 'boy', 250, 218, view='side', pose='sit', expr='down', s=2, shade=(0.7, 0.68, 0.84))
    vig(img, 0.45)


def s_dock(img, d, lt, dur, T, A):
    shots(img, lt, [(0, dock_leave), (3.6, dock_wait)], tr=0.6)


# ================================================================ 随往事淡去 随梦境睡去（老电视）
def s_tv(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, 190], fill=(196, 186, 190)); d.rectangle([0, 190, W, H], fill=(150, 108, 80))
    for x in range(0, W, 26): d.line([(x, 0), (x, 184)], fill=(206, 196, 198))
    d.rectangle([0, 184, W, 190], fill=(128, 92, 76))
    window(img, d, 30, 34, 70, 70, T, moon_at=(20, 20, 8))
    for (fx, fy, c) in ((150, 40, (250, 190, 150)), (186, 52, (160, 200, 230)), (156, 78, (250, 220, 170))):
        d.rectangle([fx, fy, fx + 26, fy + 22], fill=(110, 76, 60)); d.rectangle([fx + 2, fy + 2, fx + 24, fy + 20], fill=c)
    d.ellipse([70, 214, 400, 262], fill=(170, 86, 90)); d.ellipse([84, 220, 386, 256], fill=(196, 110, 108))
    # 沙发
    d.rounded_rectangle([88, 128, 232, 214], 8, fill=(96, 128, 176)); d.rounded_rectangle([98, 164, 240, 214], 6, fill=(120, 152, 200))
    d.rounded_rectangle([78, 150, 104, 216], 8, fill=(84, 112, 160)); d.rectangle([100, 214, 106, 222], fill=(70, 50, 50)); d.rectangle([226, 214, 232, 222], fill=(70, 50, 50))
    d.rounded_rectangle([112, 140, 148, 168], 4, fill=(248, 204, 88)); d.line([(112, 154), (148, 154)], fill=(212, 154, 58))
    sleep = lt > 3.9
    person(img, 'boy', 190, 222, view='side', pose='sit', expr='closed' if sleep else ('down' if lt > 2.6 else 'sad'), s=2)
    d.rectangle([250, 196, 284, 200], fill=(170, 120, 84)); d.rectangle([254, 200, 257, 222], fill=(140, 96, 66)); d.rectangle([277, 200, 280, 222], fill=(140, 96, 66))
    d.rectangle([262, 188, 272, 196], fill=(250, 246, 236)); d.rectangle([272, 190, 275, 194], fill=(250, 246, 236))
    # 电视
    tx0, ty0, tx1, ty1 = 322, 108, 422, 184
    d.rectangle([310, 184, 434, 222], fill=(128, 88, 64)); d.rectangle([310, 184, 434, 188], fill=(160, 114, 82))
    d.line([(350, 108), (334, 84)], fill=(90, 90, 100), width=2); d.line([(392, 108), (410, 84)], fill=(90, 90, 100), width=2)
    d.rounded_rectangle([tx0 - 6, ty0 - 6, tx1 + 20, ty1 + 6], 6, fill=(90, 70, 66), outline=OUT)
    for k in range(2): d.ellipse([tx1 + 6, ty0 + 6 + k * 16, tx1 + 16, ty0 + 16 + k * 16], fill=(60, 50, 50), outline=(200, 190, 170))
    sw, sh_ = tx1 - tx0, ty1 - ty0
    off_k = span(lt, 4.7, 5.2)
    noise = ease(span(lt, 1.0, 4.0))
    scr = mini(MEM_T[int(lt / 1.1) % 4], sw, sh_)
    a = np.asarray(scr, float)
    r = np.random.default_rng(int(T * 15))
    sn = r.integers(40, 235, (sh_ // 2 + 1, sw // 2 + 1)).repeat(2, 0).repeat(2, 1)[:sh_, :sw].astype(float)
    g = a @ np.array([0.3, 0.59, 0.11])
    a = a * (1 - noise * 0.7) + g[..., None] * noise * 0.7
    m = (r.random((sh_, sw)) < noise * 0.95)[..., None]
    a = np.where(m, sn[..., None] * np.array([0.9, 0.95, 1.0]), a)
    roll = int(T * 40) % sh_
    a[roll:roll + 3] = a[roll:roll + 3] * 0.5 + 100
    scr = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    d.rectangle([tx0, ty0, tx1, ty1], fill=(10, 10, 16))
    if off_k <= 0: img.paste(scr, (tx0, ty0))
    elif off_k < 1:
        hh = max(1, int(sh_ * (1 - off_k) ** 2)); ww = max(2, int(sw * (1 - max(0, off_k - 0.6) / 0.4)))
        d.rectangle([tx0 + sw / 2 - ww / 2, ty0 + sh_ / 2 - hh / 2, tx0 + sw / 2 + ww / 2, ty0 + sh_ / 2 + hh / 2], fill=(240, 246, 255))
    elif lt < 5.5: d.point((tx0 + sw // 2, ty0 + sh_ // 2), fill=(240, 246, 255))
    fl = (0.75 + 0.25 * math.sin(T * 23) * math.sin(T * 7)) * (1 - off_k)
    lighting(img, [(372, 146, 240, 1.0 * fl, 170), (65, 70, 70, 0.4)], amb=0.14)
    if off_k < 1: glow(img, 372, 146, 90, (170, 200, 255), 0.22 * fl)
    if off_k <= 0: img.paste(scr, (tx0, ty0)); d.rectangle([tx0, ty0, tx1, ty1], outline=(30, 30, 40))
    if sleep:
        for i in range(3):
            k = ((lt - 3.9) * 0.5 + i / 3) % 1
            put(img, 'zz', 200 + k * 26 + 3 * math.sin(k * 9), 150 - k * 34, 2 if i == 0 else 1, alpha=clamp(2 - 2.2 * k))
    vig(img, 0.45)


# ================================================================ 随麻痹的心逐渐远去（纸船）
def s_boat(img, d, lt, dur, T, A):
    f = clamp(lt / dur)
    sky(img, ((0, (150, 160, 186)), (0.5, (190, 196, 210)), (1, (226, 226, 230))), 0, 150, 5)
    d.ellipse([330, 96, 366, 132], fill=(244, 240, 232)); glow(img, 348, 114, 70, (255, 250, 240), 0.5)
    pix.hills(d, 140, 16, 0.01, 0.8, (160, 170, 190)); pix.hills(d, 150, 8, 0.02, 2.2, (136, 148, 172))
    img.paste(pix.vgrad(W, 90, ((0, (190, 200, 216)), (1, (120, 140, 176))), 5), (0, 152))
    for i in range(36):
        r = rng(i * 3 + 5)
        x = (r.uniform(0, W + 40) + lt * 30) % (W + 40) - 20; y = r.uniform(156, 240)
        d.line([(x, y), (x + r.randint(5, 16), y)], fill=(214, 222, 236))
    # 纸船和船上灰掉的心
    k = ease(f)
    bx = lerp(170, 404, k); by = lerp(226, 168, k) + 2 * math.sin(lt * 2.4); s = lerp(2.6, 0.5, k)
    ripples(d, T, (bx - 20 * s, by, bx + 20 * s, by + 4), 3, (230, 236, 246), seed=4, rmax=12 * s)
    heart(d, bx, by - 13 * s, 0.34 * s, grey=clamp(0.3 + f * 1.4), crack=1.0)
    d.polygon([(bx - 16 * s, by - 7 * s), (bx + 16 * s, by - 7 * s), (bx + 9 * s, by), (bx - 9 * s, by)], fill=(250, 248, 240), outline=OUT)
    d.polygon([(bx - 16 * s, by - 7 * s), (bx - 4 * s, by - 7 * s), (bx - 9 * s, by)], fill=(214, 210, 206))
    # 岸
    d.polygon([(0, 214), (120, 226), (170, 250), (150, H), (0, H)], fill=(110, 126, 120)); d.line([(0, 214), (120, 226), (170, 250)], fill=(150, 166, 156))
    for i in range(9):
        x = 16 + i * 15; hgt = 22 + (i * 7) % 16
        d.line([(x, 232 + i), (x + round(2 * math.sin(T * 1.5 + i)), 232 + i - hgt)], fill=(84, 100, 96), width=2)
        d.rectangle([x - 1 + round(2 * math.sin(T * 1.5 + i)), 226 + i - hgt, x + 1 + round(2 * math.sin(T * 1.5 + i)), 234 + i - hgt], fill=(120, 96, 80))
    person(img, 'boy', 96, 244, view='back', s=2)
    for i in range(5):                          # 一层层的雾
        x = (i * 130 + lt * (10 + i * 4)) % 700 - 160
        tfill(img, 'ellipse', [x, 140 + i * 16, x + 260, 164 + i * 16], (236, 238, 244), 0.3 + 0.35 * f)
    grade(img, sat=1 - 0.6 * f)
    vig(img, 0.3, col=(230, 232, 240))


# ================================================================ 我好想你 好想你（对着群山喊）
def s_shout(img, d, lt, dur, T, A):
    sky(img, DAWN4, 0, H, 6)
    sy = lerp(176, 132, ease(clamp(lt / dur)))
    glow(img, 330, sy, 140, (255, 236, 180), 0.6)
    for k in range(12):                         # 光芒
        a = k * math.pi / 6 + T * 0.1
        tfill(img, 'polygon', [(330, sy), (330 + math.cos(a) * 400, sy + math.sin(a) * 400), (330 + math.cos(a + 0.12) * 400, sy + math.sin(a + 0.12) * 400)],
              (255, 240, 200), 0.1)
    d.ellipse([306, sy - 24, 354, sy + 24], fill=(255, 246, 214))
    for i in range(4): cloud(d, (i * 170 + T * 4) % 680 - 120, 26 + (i * 23) % 50, 1.6, (255, 214, 200), (236, 170, 180))
    ridges = [(176, 34, 0.010, 0.4, (176, 150, 190)), (198, 30, 0.014, 2.0, (140, 122, 172)), (220, 24, 0.02, 4.1, (104, 96, 150))]
    for i, (b, a_, fq, ph_, c) in enumerate(ridges):
        pix.hills(d, b, a_, fq, ph_, c)
        tfill(img, 'rectangle', [0, b + 8, W, b + 22], (255, 230, 226), 0.35)             # 山间的雾
    # 崖顶
    d.polygon([(0, 150), (70, 146), (118, 152), (134, 170), (126, 210), (150, H), (0, H)], fill=(70, 66, 110))
    d.line([(0, 150), (70, 146), (118, 152), (134, 170)], fill=(120, 110, 160)); pix.grass(d, 148, (60, 90, 96), (110, 150, 130), T, 6, 110, 4)
    px, py = 98, 150
    yell = (lt % 2.2) < 1.3
    person(img, 'boy', px, py, view='side', expr='laugh' if yell else 'closed', arms='reach' if yell else 'down', s=2)
    mx, my = px + 16, py - 40
    for j in range(3):                          # 一声声喊出去，越远越小
        k = (lt - j * 2.2) / 2.6
        if not 0 < k < 1: continue
        for q in range(3):
            rr = 14 + 60 * k + q * 9
            d.arc([mx - rr, my - rr, mx + rr, my + rr], -32, 32, fill=lerpc((255, 250, 240), (236, 180, 190), k))
        x = mx + 124 + 180 * eout(k); y = my - 14 - 30 * k
        sc = 3 if k < 0.3 else (2 if k < 0.62 else 1)
        text(img, title_str(), x, y, col=(255, 252, 240), out=(150, 70, 110), scale=sc, alpha=clamp(2.4 - 2.6 * k))
    for j, (ex, ey, s) in enumerate(((350, 196, '好想你…'), (228, 214, '想你…'), (420, 176, '你…'))):      # 回声
        k = (lt - 1.6 - j * 1.4) / 1.8
        if 0 < k < 1: text(img, s, ex, ey - 12 * k, col=(255, 240, 236), out=(120, 90, 150), font=FONT_S, alpha=math.sin(k * 3.14))
    for i in range(7):
        k = lt * 0.5 + i * 0.13
        pix.bird(d, 180 + i * 22 + k * 40, 120 - k * 26 + (i % 3) * 9, T, col=(90, 70, 120), ph=i)
    vig(img, 0.3)


# ================================================================ 却不露痕迹（沙滩上的字）
@lru_cache(None)
def sand_text():
    s = title_str(); sc = 3
    w = int(FONT.getlength(s)) + 4
    m = Image.new('L', (w, 20)); md = ImageDraw.Draw(m); md.fontmode = '1'; md.text((2, 1), s, font=FONT, fill=255)
    return (np.array(m) > 0).repeat(sc, 0).repeat(sc, 1)


def s_sand(img, d, lt, dur, T, A):
    SAND, SAND_D, SAND_L, WET, CARVE = (238, 216, 172), (196, 166, 124), (250, 236, 200), (206, 180, 140), (160, 124, 90)
    d.rectangle([0, 0, W, H], fill=SAND)
    r0 = rng(3)
    for i in range(260):
        x, y = r0.randrange(W), r0.randrange(40, H)
        d.point((x, y), fill=SAND_D if i % 3 else SAND_L)
    for i in range(7):                          # 贝壳和海星
        x, y = r0.randrange(20, W - 20), r0.randrange(180, H - 30)
        if i % 2: d.ellipse([x - 3, y - 2, x + 3, y + 2], fill=(255, 236, 226), outline=(214, 170, 160))
        else: d.point([(x, y), (x - 2, y), (x + 2, y), (x, y - 2), (x - 1, y + 2), (x + 1, y + 2)], fill=(250, 150, 120))
    # 浪：涌上来盖过字，再退回去
    t_in, tp, t_out = 1.7, 3.5, 5.6             # 浪开始涌上来、到最高、退回去
    wave = lambda t: 56 + 4 * math.sin(t * 2.2) + 152 * math.sin(clamp((t - t_in) / (t_out - t_in)) * math.pi) ** 1.2
    reach = wave(lt); peak = wave(min(lt, tp)) if lt > t_in else 0
    front = reach + 6 * np.sin(XX[0] / 31 + T * 1.3) + 4 * np.sin(XX[0] / 13 - T * 2)
    pfront = peak + 6 * np.sin(XX[0] / 31 + min(T, T - lt + tp) * 1.3) + 4 * np.sin(XX[0] / 13)
    wet = (YY < pfront[None, :]) & (YY >= front[None, :])
    dry = 1 - 0.7 * span(lt, tp, dur)
    blend_box(img, (0, 0, W, H), WET, wet * 0.75 * dry, levels=4)
    # 脚印和字：浪到过的地方就没有了
    m = sand_text(); th, tw = m.shape
    tx0, ty0 = W // 2 - tw // 2, 118
    keep = np.zeros((H, W), bool); keep[ty0:ty0 + th, tx0:tx0 + tw] = m
    foot = np.zeros((H, W), bool)
    for i in range(9):
        fx = 60 + i * 9; fy = 236 - i * 9 + (i % 2) * 6
        foot[fy:fy + 3, fx:fx + 5] = True
    alive = YY >= pfront[None, :] + 3
    a = np.asarray(img).copy()
    hi = np.zeros((H, W), bool); hi[1:, 1:] = (keep & alive)[:-1, :-1]
    a[hi & ~keep] = SAND_L
    a[foot & alive] = SAND_D; a[keep & alive] = CARVE
    img.paste(Image.fromarray(a))
    water = YY < front[None, :]
    depth = np.clip((front[None, :] - YY) / 60, 0, 1)
    blend_box(img, (0, 0, W, H), (96, 186, 214), water * (0.55 + 0.4 * depth), levels=8)
    blend_box(img, (0, 0, W, H), (40, 120, 180), water * depth * 0.6, levels=6)
    for x in range(0, W, 2):                    # 浪花
        fy = front[x]
        d.rectangle([x, fy - 3, x + 1, fy], fill=(255, 255, 255))
        if (x // 2 + int(T * 6)) % 5 == 0: d.point((x, fy + 3), fill=(255, 255, 255))
        if (x // 2) % 7 == 0: d.rectangle([x, fy - 12 - 3 * math.sin(x + T * 3), x + 2, fy - 11 - 3 * math.sin(x + T * 3)], fill=(214, 240, 250))
    for i in range(20):
        r = rng(i * 9)
        x = r.uniform(0, W); y = r.uniform(0, max(2, reach - 20))
        if math.sin(T * 3 + i) > 0.3: d.line([(x, y), (x + r.randint(4, 12), y)], fill=(170, 226, 240))
    # "我"和手里的树枝
    px, py = 60 + 4 * span(lt, 2.0, 3.0) * 0, 262
    d.ellipse([px - 14, py - 3, px + 14, py + 3], fill=SAND_D)
    d.line([(px + 12, py - 26), (px + 30, py - 2)], fill=(120, 84, 60), width=2)
    person(img, 'boy', px, py, view='side', expr='down' if lt > 2.2 else 'sad', arms='hold_f', s=2)
    for i in range(3): pix.bird(d, 300 + i * 26 + lt * 12, 16 + i * 6, T, col=(250, 250, 255), ph=i)


# ================================================================ 我还踮着脚思念（人潮）
def s_crowd(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(206, 210, 222))
    for x in range(0, W, 60): d.rectangle([x + 22, 0, x + 40, 60], fill=(240, 244, 250)); glow(img, x + 31, 30, 50, (255, 255, 250), 0.25)
    d.rectangle([0, 60, W, 64], fill=(150, 158, 176))
    # 大钟和发车牌
    d.rectangle([150, 70, 330, 122], fill=(30, 32, 50)); d.rectangle([150, 70, 330, 122], outline=(110, 116, 140), width=2)
    for k in range(4):
        d.rectangle([158, 78 + k * 10, 250, 84 + k * 10], fill=(255, 190, 80) if (k + int(T * 1.5)) % 4 else (40, 44, 66))
        d.rectangle([258, 78 + k * 10, 322, 84 + k * 10], fill=(120, 220, 160))
    clock(d, 390, 92, 20, T * 0.05 + 2, T * 0.6)
    for px in (60, 440): d.rectangle([px - 12, 64, px + 12, 214], fill=(176, 182, 198)); d.rectangle([px - 12, 64, px - 9, 214], fill=(196, 202, 216))
    d.rectangle([0, 150, W, 214], fill=(186, 192, 208)); d.line([(0, 150), (W, 150)], fill=(150, 158, 176))
    d.rectangle([0, 214, W, H], fill=(150, 154, 172)); d.rectangle([0, 214, W, 216], fill=(176, 180, 196))
    for x in range(0, W, 40): d.line([(x, 216), (x - 30, H)], fill=(136, 140, 158))
    # 远处的人流；里面有一个围红围巾的人，一闪就不见了
    gx = 300 + lt * 16
    ga = ease(span(lt, 1.3, 1.8)) * (1 - ease(span(lt, 3.5, 3.9)))
    for i in range(16):
        r = rng(i * 7)
        sp = (12 + r.random() * 22) * (1 if i % 2 else -1)
        x = (r.uniform(0, W + 60) + lt * sp) % (W + 60) - 30
        if i == 8 and ga > 0: ghost(img, 'girl', gx, 204, 1, ga, view='side', pose='walk', ph=wph(lt, 6))
        gperson(img, 'boy' if i % 3 else 'girl', x, 202 + (i % 3) * 3, 1, view='side', pose='walk', ph=wph(lt + i, 6), flip=sp < 0, col=(150, 156, 180))
    if ga > 0.5: glow(img, gx, 190, 16, (255, 220, 150), 0.35)
    # 中间的人流
    for i in range(7):
        r = rng(i * 5 + 3)
        sp = (30 + r.random() * 40) * (1 if i % 2 else -1)
        x = (r.uniform(0, W + 120) + lt * sp) % (W + 120) - 60
        if abs(x - 236) < 26: continue
        gperson(img, 'girl' if i % 3 == 0 else 'boy', x, 244 + (i % 2) * 6, 2, view='side', pose='walk', ph=wph(lt + i * 0.3, 7), flip=sp < 0, col=(120, 126, 154))
    # "我"：踮着脚往远处找
    up = round(4 * abs(math.sin(lt * 3.2)))
    x, y = 236, 250
    d.rectangle([x - 6, y - up, x - 4, y], fill=(150, 96, 70)); d.rectangle([x + 2, y - up, x + 4, y], fill=(150, 96, 70))
    person(img, 'boy', x, y - up, view='back', arms='wave' if 1.6 < lt < 3.6 else 'down', ph=int(lt * 8), s=2)
    if 1.5 < lt < 2.3: text(img, '！', x + 22, y - 74 - up, col=(255, 90, 100), out=(255, 255, 255))
    if lt > 4.0: text(img, '…', x + 24, y - 72, col=(90, 96, 130), out=(255, 255, 255))
    # 最前面掠过的人影
    for i in range(3):
        r = rng(i * 11 + 1)
        sp = (150 + r.random() * 90) * (1 if i % 2 else -1)
        x = (r.uniform(0, W + 400) + lt * sp) % (W + 400) - 200
        person(img, 'boy' if i % 2 else 'girl', x, 330, view='side', pose='walk', ph=wph(lt + i, 6), s=4, flip=sp < 0, tint=(60, 62, 86))
    grade(img, sat=0.85)
    vig(img, 0.4)


# ================================================================ 我还任记忆盘旋（旋转木马）
def s_carousel(img, d, lt, dur, T, A):
    sky(img, ((0, (12, 10, 40)), (0.6, (40, 26, 90)), (1, (110, 56, 130))), 0, H, 6)
    stars(d, T, 120, 0.8, 120)
    bokeh(img, T, 10, seed=6, a=0.2, box=(0, 100, W, 220))
    ferris(img, d, 60, 150, 44, T)
    d.rectangle([0, 224, W, H], fill=(36, 28, 70)); d.line([(0, 224), (W, 224)], fill=(80, 60, 120))
    for i in range(14):                         # 一串彩灯
        x = i * 38 - 6; y = 22 + 10 * math.sin(i * 0.9)
        c = [(255, 120, 140), (255, 214, 110), (120, 200, 255)][i % 3]
        on = (i + int(T * 3)) % 3 != 0
        if on: glow(img, x, y, 8, c, 0.5)
        d.rectangle([x - 1, y - 1, x + 1, y + 1], fill=c if on else lerpc(c, (20, 20, 50), 0.6))
    cx = 262
    # 底座和中柱
    d.ellipse([cx - 150, 204, cx + 150, 240], fill=(110, 60, 100)); d.ellipse([cx - 150, 198, cx + 150, 232], fill=(214, 120, 150))
    d.ellipse([cx - 138, 202, cx + 138, 228], fill=(236, 150, 170))
    horses = []
    for i in range(6):
        a = lt * 0.85 + i * math.pi / 3
        horses.append((math.sin(a), cx + 118 * math.cos(a), 214 + 9 * math.sin(a), i, math.cos(a)))

    def horse(depth, x, y, i, c):
        bobv = round(7 * math.sin(lt * 3 + i * 2.1))
        s = 2
        d.line([(x, 84), (x, y)], fill=(255, 226, 150) if depth >= 0 else (170, 140, 110), width=2)
        tint = None if depth >= 0 else (150, 120, 170)
        flip = c > 0                              # 朝转动的方向
        im = pix.spr('horse', s, flip, tint)
        hy = y - 30 + bobv
        img.paste(im, (int(x - im.width / 2), int(hy)), im)
        if i == 0:                                # 她的影子骑在这匹马上
            if depth >= 0: glow(img, x, hy - 8, 30, (255, 226, 160), 0.4)
            ghost(img, 'girl', x - (4 if flip else -4), hy + 26, 2, 0.8 if depth >= 0 else 0.4, view='side', pose='sit', expr='happy', flip=flip)

    for h in sorted(horses):
        if h[0] < 0: horse(*h)
    d.rectangle([cx - 20, 84, cx + 20, 214], fill=(250, 226, 200)); d.rectangle([cx - 20, 84, cx - 14, 214], fill=(226, 190, 170))
    for k in range(4): d.rectangle([cx - 10, 96 + k * 28, cx + 10, 114 + k * 28], fill=(170, 214, 240)); d.line([(cx - 8, 112 + k * 28), (cx + 6, 98 + k * 28)], fill=(230, 244, 255))
    for h in sorted(horses):
        if h[0] >= 0: horse(*h)
    # 顶棚
    d.polygon([(cx - 156, 84), (cx + 156, 84), (cx + 40, 34), (cx - 40, 34)], fill=(226, 96, 120))
    for k in range(-5, 6, 2): d.polygon([(cx + k * 28, 84), (cx + (k + 1) * 28, 84), (cx + (k + 1) * 7.2, 34), (cx + k * 7.2, 34)], fill=(250, 240, 226))
    d.polygon([(cx - 40, 34), (cx + 40, 34), (cx, 14)], fill=(226, 96, 120)); d.rectangle([cx - 1, 4, cx + 1, 14], fill=(255, 226, 150)); put(img, 'star', cx, 4, 1)
    for k in range(13):
        x = cx - 156 + k * 26
        d.pieslice([x - 13, 76, x + 13, 98], 0, 180, fill=(250, 240, 226) if k % 2 else (226, 96, 120))
        on = (k + int(T * 4)) % 2
        if on: glow(img, x, 98, 7, (255, 236, 150), 0.6)
        d.rectangle([x - 1, 96, x + 1, 99], fill=(255, 244, 180) if on else (150, 120, 90))
    glow(img, cx, 150, 190, (255, 200, 170), 0.16, ry=110)
    person(img, 'boy', 96, 262, view='back', s=2, shade=(0.8, 0.74, 0.9))
    for i in range(5):
        k = (lt * 0.4 + i / 5) % 1
        put(img, 'note', cx - 150 + i * 70 + 8 * math.sin(k * 7 + i), 190 - k * 60, 1, tint=(255, 220, 240), alpha=clamp(2 - 2 * k))
    vig(img, 0.45)


# ================================================================ 我还闭着眼流泪（雨夜的路灯下）
def s_rain(img, d, lt, dur, T, A):
    rainy_street(img, d, T)
    lamp(img, d, 150, 222, 1.0, h=110)
    ga = ease(span(lt, 1.7, 2.5)) * (1 - ease(span(lt, 4.2, 5.2)))
    x = 226
    rain(d, T, 0, W, 0, 224, 150, (120, 140, 210), speed=280, ln=7)
    ux, uy = x + 16, 112
    if ga > 0.05:                               # 身边浮出撑伞的人，雨停了一会儿
        tfill(img, 'polygon', [(ux - 38, uy), (ux + 38, uy), (ux + 30, 222), (ux - 46, 222)], (24, 26, 62), 0.8 * ga)
    person(img, 'boy', x, 224, view='front', expr='closed', s=3)
    for k, ex in enumerate((x - 9, x + 6)):       # 脸上的泪
        ph = (lt * 0.6 + k * 0.4) % 1
        d.rectangle([ex, 224 - 62, ex + 1, 224 - 62 + 8 * min(1, ph * 3)], fill=(150, 200, 255))
        d.rectangle([ex, 224 - 54 + ph * 26, ex + 1, 224 - 52 + ph * 26], fill=(190, 226, 255))
    if ga > 0.05:
        lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay)
        ld.line([(ux + 14, uy), (ux + 14, 180)], fill=(230, 226, 236), width=2)
        person(lay, 'girl', x + 40, 224, view='side', expr='smile', arms='umbrella', s=3, flip=True)
        umbrella(ld, ux, uy, r=42)
        glow(img, ux + 10, 170, 70, (255, 226, 170), 0.22 * ga)
        dpaste(img, lay, 0, 0, ga * 0.8)
    reflect(img, 224, H - 224, T, tint=(16, 14, 50), a=0.6, amp=1.6)
    splashes(d, T, 226, H - 4, 34, (150, 170, 230))
    if ga < 0.3:                                # 没有伞的时候，雨点打在头上肩上
        for i in range(5):
            k = (T * 3 + i / 5) % 1
            if k < 0.4: d.point([(x - 14 + i * 7 - 2, 224 - 86 - 2), (x - 14 + i * 7 + 2, 224 - 86 - 2)], fill=(190, 210, 255))
    vig(img, 0.45)


# ================================================================ 我还装作无所谓（咖啡馆）
def s_cafe(img, d, lt, dur, T, A):
    alone = ease(span(lt, 6.6, 7.6))            # 歌词唱完以后，周围暗下来，只剩自己
    # 大窗外的街
    d.rectangle([0, 0, W, H], fill=(170, 214, 240)); city(img, d, 140, 41, T * 4, (150, 190, 226), hmin=30, hmax=80)
    for box in ((0, 0, W, 26), (0, 26, 60, 150), (300, 26, W, 150), (0, 140, W, 150)): d.rectangle(box, fill=(236, 214, 186))
    d.rectangle([0, 150, W, H], fill=(196, 150, 116)); d.line([(0, 150), (W, 150)], fill=(160, 116, 90))
    d.rectangle([60, 26, 300, 140], outline=(120, 84, 62), width=4); d.rectangle([178, 26, 181, 140], fill=(120, 84, 62))
    d.rectangle([54, 140, 306, 146], fill=(140, 98, 72))
    d.rectangle([60, 26, 300, 44], fill=(226, 96, 96))
    for k in range(12): d.pieslice([60 + k * 20, 34, 80 + k * 20, 54], 0, 180, fill=(226, 96, 96) if k % 2 else (250, 240, 226))
    # 菜单板、吊灯、绿植
    d.rectangle([340, 34, 440, 110], fill=(50, 70, 66)); d.rectangle([340, 34, 440, 110], outline=(150, 104, 76), width=3)
    text(img, 'MENU', 390, 48, col=(250, 246, 236), out=None, font=FONT_S, shadow=False)
    for k in range(4): d.line([(352, 62 + k * 11), (352 + 40 + (k * 17) % 30, 62 + k * 11)], fill=(214, 226, 214)); d.line([(418, 62 + k * 11), (428, 62 + k * 11)], fill=(255, 220, 140))
    for lx in (120, 240, 360):
        d.line([(lx, 0), (lx, 14)], fill=(70, 60, 60)); d.polygon([(lx - 8, 14), (lx + 8, 14), (lx + 12, 24), (lx - 12, 24)], fill=(255, 226, 150)); glow(img, lx, 26, 30, (255, 236, 170), 0.4)
    d.rectangle([14, 110, 36, 150], fill=(190, 110, 80))
    for k, (px, py) in enumerate(((25, 96), (16, 102), (34, 100), (22, 86), (30, 88))): d.ellipse([px - 6, py - 8, px + 6, py + 8], fill=(70, 140, 90) if k % 2 else (96, 168, 104))
    # 两个朋友和"我"
    laugh = lt < 6.4
    person(img, 'girl', 110, 262, age='f1', view='side', pose='sit', expr='laugh' if laugh and int(lt * 3) % 3 else 'happy', arms='eat', ph=int(lt * 2), s=3)
    person(img, 'boy', 372, 262, age='f1', view='side', pose='sit', expr='laugh' if laugh and int(lt * 3 + 1) % 3 else 'happy', arms='eat', ph=int(lt * 2 + 1), s=3, flip=True)
    me_expr = 'laugh' if lt < 5.6 and int(lt * 2.5) % 4 else ('happy' if lt < 6.4 else ('neutral' if lt < 7.2 else 'sad'))
    person(img, 'boy', 240, 250, view='front', pose='sit', expr=me_expr, arms='lap', s=3)
    # 桌子、咖啡和蛋糕
    d.rounded_rectangle([130, 204, 350, 216], 4, fill=(170, 120, 84), outline=OUT); d.rectangle([232, 216, 248, H], fill=(140, 96, 66))
    for cxp in (170, 240, 312):
        d.rectangle([cxp - 7, 192, cxp + 7, 204], fill=(250, 246, 236)); d.rectangle([cxp - 7, 192, cxp + 7, 194], fill=(150, 96, 70)); d.arc([cxp + 4, 194, cxp + 12, 202], -90, 90, fill=(250, 246, 236), width=2)
        for k in range(2):
            kk = (T * 0.5 + k / 2 + cxp) % 1
            d.point((cxp - 2 + k * 4 + 2 * math.sin(kk * 6), 188 - kk * 14), fill=lerpc((255, 255, 255), (236, 214, 186), kk))
    d.polygon([(196, 204), (216, 204), (214, 194), (198, 196)], fill=(255, 236, 200)); d.rectangle([198, 193, 214, 195], fill=(255, 150, 170)); d.point((206, 191), fill=(226, 60, 70))
    # 泡泡：嘴上说的和心里想的
    if 0.3 < lt < 2.4: bubble(img, d, 60, 96, 150, 124, tail=(118, 150)); text(img, '最近怎么样？', 105, 110, col=(60, 50, 70), out=None, font=FONT_S, shadow=False)
    if 3.4 < lt < 5.4: bubble(img, d, 340, 104, 420, 132, tail=(366, 156)); text(img, '哈哈哈哈', 380, 118, col=(60, 50, 70), out=None, font=FONT_S, shadow=False)
    if 1.6 < lt < 6.2:
        bubble(img, d, 196, 122, 296, 150, tail=(246, 166)); text(img, '我？挺好的呀', 246, 136, col=(60, 50, 70), out=None, font=FONT_S, shadow=False)
    if alone > 0:
        lighting(img, [(240, 190, 120, 1.2)], amb=1 - 0.8 * alone, tint=(0.2, 0.22, 0.42))
    ta = ease(span(lt, 2.2, 3.0))
    if ta > 0:
        cy = 60 - 6 * alone
        thought(img, d, 240, cy, 70, 40, to=(262, 150), col=(214, 220, 236), a=ta)
        if ta > 0.9:
            cloud(d, 216, cy - 26, 1.4, (120, 126, 150), (90, 96, 124))
            rain(d, T, 214, 262, int(cy - 8), int(cy + 26), 9, (120, 170, 240), speed=60, ln=3, slant=-1)
            person(img, 'boy', 232, cy + 30, view='front', expr='sad')
            ghost(img, 'girl', 262, cy + 30, 1, 0.4 + 0.4 * alone, view='back')
    vig(img, 0.35 + 0.3 * alone)
