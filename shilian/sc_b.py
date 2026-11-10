"""永不失联的爱 · 第一段副歌和间奏。签名都是 (img, d, lt, dur, T, A)。

副歌：一颗心发出满格信号；两座楼顶的传声筒终于两头都有人；纸船载着两人驶过星辰大海，星星鲸鱼跃过头顶；
故事书里盖上"不改"的章；红线和星座把两人连在一起；她的特写；卫星把两个房间连起来。
然后是分开：牵着的手一根根手指松开，两人在雨里各自走开；他在电话亭里一遍遍打给她；
"我还在"——雨停了，月亮出来，一颗发光的心落进他手里。间奏：这颗心穿过云层、卫星和月亮，一路飞到她的窗前，"已送达"。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
import kit
import sig
import motifs as M
import sc_a
from props import shots, shake, dpaste, mix_stops, thump
from pix import (W, H, FONT, FONT_S, OUT, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky, stars,
                 person, wph, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, BAYER)
from kit import NIGHT, DEEP, DUSK, DAY, GOLDEN, RAINY

YY, XX = np.mgrid[0:H, 0:W]


def rays(img, cx, cy, T, col, a=0.25, n=14, spin=0.3):
    ang = np.arctan2(YY - cy, XX - cx) + T * spin
    m = (np.sin(ang * n) > 0.55).astype(float)
    blend_box(img, (0, 0, W, H), col, m * a, levels=4)


# ================================================================ 副歌一
def s_give(img, d, lt, dur, T, A):
    """你给我：一颗大心在拍子上跳，往外发出一圈圈信号，下面的信号格一格格满上"""
    img.paste((20, 10, 40), (0, 0, W, H))
    rays(img, 240, 120, T, (70, 30, 90), 0.6)
    k = thump(T, 0.3)
    for j in range(4):
        u = (lt * 0.9 + j / 4) % 1
        r = 40 + u * 220
        d.ellipse([240 - r, 120 - r, 240 + r, 120 + r], outline=lerpc(sig.SIG, (20, 10, 40), u))
    glow(img, 240, 120, 110, sig.HEART, 0.45 + 0.3 * k)
    M.heart(img, 240, 120, 3 + 0.3 * eback(span(lt, 0, 0.4)), beat=k, col=(sig.HEART, sig.HEART_L, sig.HEART_D))
    lv = 4 * span(lt, 0.1, 1.3)
    sig.bars(d, 222, 236, lv, 3, on=sig.SIG, off=(70, 50, 90))
    for j in range(6):
        a = j * math.pi / 3 + T
        sparkle(d, int(240 + math.cos(a) * 90), int(120 + math.sin(a) * 70), T + j, (255, 230, 250), 2)


def s_cans(img, d, lt, dur, T, A):
    """这一辈子都不想失联的爱：两座楼顶，这回线的两头都有人，线发着光，小心来回跑"""
    sc_a.rooftops(img, d, T, lt + 6, 0, True, 0)
    p0, p1 = (110 + 13 + 12, 190 - 52), (380 - 13 - 12, 200 - 52)
    pts = sig.string_pts(p0, p1, 26, 60)
    for k in range(3):
        u = 1 - ((lt * 0.45 + k / 3 + 0.17) % 1)
        x, y = pts[int(u * 60)]
        glow(img, x, y, 12, sig.SIG, 0.4); sig.heart_at(img, x, y - 1, 1, col=(150, 230, 255))
    for k in range(6):
        u = (lt * 0.3 + k / 6) % 1
        x = 160 + k * 30 + 6 * math.sin(T * 2 + k); y = 140 - u * 120
        sig.heart_at(img, x, y, 1, alpha=clamp(1 - u) * clamp(u * 5))
    for x in (110, 380):
        sig.bars(d, x - 10, 104 + (10 if x > 200 else 0), 4, 2, on=sig.SIG)


def s_sea(img, d, lt, dur, T, A):
    """相信爱的征途就是星辰大海：纸船载着两人驶过倒映着银河的海，星星鲸鱼从头顶跃过"""
    hz = 150
    sky(img, DEEP, 0, hz, 6)
    stars(d, T, hz, 1, 220)
    kit.galaxy(img, 1.0, 3, -0.2, 40)
    kit.meteors(d, T, 1.4, 5, (0, 0, W, 90))
    # 鲸鱼从右往左跃过
    u = span(lt, 0.6, 4.6)
    if 0 < u < 1:
        wx = lerp(W + 70, -70, u); wy = hz - 10 - math.sin(u * math.pi) * 110
        sig.whale(img, d, wx, wy, 2, T, flip=True)
        for j in range(6):
            sparkle(d, int(wx + 50 + j * 14), int(wy + 10 + 6 * math.sin(j + T * 3)), T + j, (200, 230, 255), 2)
    d.rectangle([0, hz, W, H], fill=(16, 18, 56))
    props.reflect(img, hz, H - hz, T, (10, 12, 40), 0.7, 2.5)
    for k in range(40):
        r = rng(k)
        x = (r.uniform(0, W) - T * 12 * r.uniform(0.5, 1.2)) % W
        y = hz + 4 + r.random() ** 1.5 * (H - hz)
        d.line([(x, y), (x + 3 + (y - hz) / 12, y)], fill=(90, 110, 190) if k % 3 else (160, 190, 255))
    # 纸船
    bx, by = 230, 218 + 2 * math.sin(T * 1.6)
    rock = 0.05 * math.sin(T * 1.6)
    sig.boat(d, bx, by, 3.2, rock)
    person(img, 'boy', bx - 38, by - 16, view='side', pose='stand', expr='happy', arms='wave', ph=int(T * 4), s=2, flip=True)
    person(img, 'girl', bx + 36, by - 16, view='side', pose='stand', expr='laugh', arms='reach', s=2, flip=True)
    hull = [(bx - 58, by - 23), (bx + 58, by - 23), (bx + 38, by), (bx - 38, by)]
    d.polygon(hull, fill=(250, 248, 240)); d.line(hull + [hull[0]], fill=OUT); d.line([(bx - 45, by - 13), (bx + 45, by - 13)], fill=(200, 204, 220))
    for k in range(3):
        f = (T * 0.7 + k / 3) % 1
        d.line([(bx + 60 + f * 60, by - 2 + k), (bx + 70 + f * 80, by - 2 + k)], fill=lerpc((200, 220, 255), (16, 18, 56), f))
    vig(img, 0.3)


STORY_TXT = '我们的故事 永远不会改写'


def s_story(img, d, lt, dur, T, A):
    """美好剧情不会更改：一本故事书翻开，画着两人相遇和牵手，笔写下一行字，盖上一个红色的"不改"印章"""
    img.paste((120, 82, 60), (0, 0, W, H))
    for y in range(0, H, 14): d.line([(0, y), (W, y + 6)], fill=(132, 92, 66))
    glow(img, 240, 120, 260, (255, 220, 160), 0.35)
    op = ease(span(lt, 0.0, 0.7))
    lp, rp = M.album(img, d, 240, 128, 360, 196, op, cover=(70, 110, 170))
    # 左页：月下相遇
    x0, y0, x1, y1 = [int(v) for v in lp]
    pnl = (x0 + 12, y0 + 12, x1 - 12, y1 - 40)
    d.rectangle(pnl, fill=(30, 34, 80)); d.rectangle(pnl, outline=(60, 50, 60))
    for k in range(18):
        r = rng(k); d.point((r.uniform(pnl[0] + 2, pnl[2] - 2), r.uniform(pnl[1] + 2, pnl[3] - 40)), fill=(255, 250, 220))
    d.ellipse([pnl[2] - 30, pnl[1] + 8, pnl[2] - 14, pnl[1] + 24], fill=(255, 240, 190))
    d.rectangle([pnl[0] + 1, pnl[3] - 20, pnl[2] - 1, pnl[3] - 1], fill=(50, 90, 70))
    person(img, 'boy', (pnl[0] + pnl[2]) / 2 - 18, pnl[3] - 12, view='side', expr='surprised')
    person(img, 'girl', (pnl[0] + pnl[2]) / 2 + 18, pnl[3] - 12, view='side', expr='shy', flip=True)
    sig.heart_at(img, (pnl[0] + pnl[2]) / 2, pnl[3] - 64 - 3 * math.sin(T * 3), 1)
    sig.pix_text(d, '第一章 · 遇见', x0 + 40, y1 - 32, (90, 70, 70))
    if rp and rp[2] - rp[0] > 80:
        x0, y0, x1, y1 = [int(v) for v in rp]
        pnl = (x0 + 12, y0 + 12, x1 - 12, y1 - 40)
        d.rectangle(pnl, fill=(255, 200, 150)); d.rectangle(pnl, outline=(60, 50, 60))
        d.ellipse([pnl[0] + 20, pnl[3] - 40, pnl[0] + 60, pnl[3]], fill=(255, 236, 170))
        d.rectangle([pnl[0] + 1, pnl[3] - 20, pnl[2] - 1, pnl[3] - 1], fill=(120, 170, 90))
        cx = (pnl[0] + pnl[2]) / 2
        person(img, 'boy', cx - 7, pnl[3] - 12, view='side', arms='hold', expr='happy')
        person(img, 'girl', cx + 7, pnl[3] - 12, view='side', arms='hold', expr='happy', flip=True)
        sig.pix_text(d, '第二章 · 永远', x0 + 40, y1 - 32, (90, 70, 70))
        # 写字
        n = int(len(STORY_TXT) * span(lt, 1.0, 2.8))
        sig.pix_text(d, STORY_TXT[:n], x0 + 14, y1 - 18, (60, 50, 90))
        if 1.0 < lt < 3.0:
            px = x0 + 14 + FONT_S.getlength(STORY_TXT[:n]); py = y1 - 14
            d.line([(px, py), (px + 14, py - 22)], fill=(40, 30, 50), width=3)
            d.line([(px + 1, py - 1), (px + 13, py - 21)], fill=(240, 200, 90))
    # 盖章
    st = 3.2
    if lt > st - 0.35:
        f = clamp((lt - (st - 0.35)) / 0.35)
        sc = lerp(3.0, 1.0, ein(f))
        im = stamp_img()
        im = im.resize((int(im.width * sc), int(im.height * sc)), Image.NEAREST)
        dpaste(img, im, 330 - im.width / 2, 150 - im.height / 2, 0.5 + 0.5 * f)
        if lt > st:
            shake(img, lt - st, 4, 0.4)
            if lt - st < 0.4:
                for j in range(8):
                    a = j * math.pi / 4; rr = 40 + (lt - st) * 100
                    d.point((330 + math.cos(a) * rr, 150 + math.sin(a) * rr), fill=(220, 60, 60))
    vig(img, 0.4)


@lru_cache(None)
def stamp_img():
    im = Image.new('RGBA', (60, 40)); d = ImageDraw.Draw(im); d.fontmode = '1'
    red = (214, 50, 56)
    d.rounded_rectangle([1, 1, 58, 38], 6, outline=red, width=3)
    d.text((10, 10), '不改', font=FONT, fill=red)
    im = im.resize((120, 80), Image.NEAREST)
    a = np.array(im)
    r = np.random.default_rng(3).random(a.shape[:2])
    a[(r < 0.12) & (a[..., 3] > 0), 3] = 0
    return Image.fromarray(a).rotate(-12, resample=Image.NEAREST, expand=True)


def s_fate(img, d, lt, dur, T, A):
    """是命运最好的安排：两座小山上各站一人，一根红线从他的小指连到她的小指；天上他的橙色星座和她的蓝色星座靠拢，拼成一颗心"""
    kit.night(img, d, T, NIGHT, 220)
    kit.galaxy(img, 0.6, 5, 0.3, 36)
    f = ease(span(lt, 0.3, 3.2))
    for side, col in ((-1, (255, 180, 110)), (1, (130, 210, 255))):
        cx = 240 + side * lerp(130, 0, f); cy = 80
        pts = [(cx + side * x, cy + y) for x, y in ((-20, -10), (-6, -24), (10, -12), (4, 8), (-14, 14))]
        if f < 0.95:
            d.line(pts + [pts[0]], fill=lerpc(col, (20, 24, 70), 0.5))
            for x, y in pts:
                glow(img, x, y, 6, col, 0.4); sparkle(d, int(x), int(y), T + x, col, 2)
    if f > 0.9:
        kit.heart_constellation(img, d, 240, 80, 3.2, span(lt, 3.0, 4.6), T)
    kit.meteors(d, T, 1.0, 9)
    # 两座小山
    d.ellipse([-80, 196, 200, 330], fill=(30, 40, 70)); d.ellipse([280, 200, 560, 330], fill=(30, 40, 70))
    d.rectangle([0, 246, W, H], fill=(24, 30, 58))
    person(img, 'boy', 110, 202, view='side', expr='smile', arms='reach', s=2)
    person(img, 'girl', 372, 206, view='side', expr='smile', arms='reach', s=2, flip=True)
    # 红线：从他的手到她的手，中间绕一个心形的圈
    a, b = (128, 162), (354, 166)
    n = int(80 * span(lt, 0.2, 2.2))
    pts = []
    for i in range(81):
        u = i / 80
        x = lerp(a[0], b[0], u); y = lerp(a[1], b[1], u) + 26 * math.sin(u * math.pi) + 3 * math.sin(u * 14 + T * 3)
        pts.append((x, y))
    if n > 1:
        for i in range(0, n, 5): glow(img, pts[i][0], pts[i][1], 6, (255, 80, 100), 0.3)
        d.line(pts[:n], fill=(255, 70, 90), width=1)
    if lt > 2.3:
        hx, hy = pts[40]
        k = eback(span(lt, 2.3, 2.7))
        sig.heart_at(img, hx, hy + 6, max(1, int(round(2 * k))), col=(255, 70, 90))
        glow(img, hx, hy + 6, 24, (255, 80, 100), 0.5 * k)
    vig(img, 0.35)


def s_you(img, d, lt, dur, T, A):
    """你是我：她的特写，粉色的光斑，眨眼笑"""
    sky(img, ((0, (255, 190, 210)), (1, (255, 230, 220))), 0, H, 4)
    rays(img, 240, 90, T, (255, 240, 245), 0.35, 12, 0.2)
    props.bokeh(img, T, 14, seed=4, a=0.35)
    expr = 'closed' if 0.9 < lt < 1.05 else ('happy' if lt > 1.05 else 'smile')
    props.bust(img, d, 'girl', 240, 40 - eout(span(lt, 0, 0.5)) * 6, 6, expr)
    for j in range(5):
        a = j * 1.26 + T * 0.6
        twinkle(d, int(240 + math.cos(a) * 110), int(110 + math.sin(a) * 70), (T * 0.9 + j * 0.2) % 1, (255, 255, 255), 4)
    sig.heart_at(img, 330, 70 - 4 * math.sin(T * 3), 2)


def room(img, d, box, T, who, wall, light, flip=False, rainy=False):
    """一个小房间的剖面：窗、台灯和拿着手机的人"""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=wall)
    wx0 = x0 + 14 if not flip else x1 - 70
    d.rectangle([wx0, y0 + 30, wx0 + 56, y0 + 100], fill=(16, 18, 50))
    for k in range(10):
        r = rng(k + (7 if flip else 0)); d.point((wx0 + r.uniform(2, 54), y0 + 32 + r.uniform(0, 60)), fill=(255, 250, 220))
    d.rectangle([wx0, y0 + 30, wx0 + 56, y0 + 100], outline=(140, 110, 100), width=3)
    d.line([(wx0 + 28, y0 + 30), (wx0 + 28, y0 + 100)], fill=(140, 110, 100), width=2)
    d.rectangle([x0, y1 - 44, x1, y1], fill=lerpc(wall, (0, 0, 0), 0.3))
    glow(img, (x0 + x1) / 2, y1 - 70, 70, light, 0.3)
    cx = (x0 + x1) / 2 + (14 if not flip else -14)
    person(img, who, cx, y1 - 30, view='front', pose='sit', expr='happy', arms='phone', s=2)
    glow(img, cx, y1 - 66, 16, (200, 236, 255), 0.6)
    return (cx, y1 - 66)


def s_link(img, d, lt, dur, T, A):
    """这一辈子都不想失联的爱：画面分成三栏，左边他的房间、右边她的房间，中间的太空里一颗卫星把两边的信号连起来"""
    img.paste((4, 4, 16), (0, 0, W, H))
    stars(d, T, H, 1, 200)
    pa = room(img, d, (0, 0, 160, H), T, 'boy', (70, 60, 100), (255, 200, 140))
    pb = room(img, d, (320, 0, W, H), T, 'girl', (60, 80, 120), (200, 220, 255), True)
    # 中间：地球的弧和卫星
    d.ellipse([90, 220, 390, 520], fill=(40, 90, 170)); d.arc([90, 220, 390, 520], 200, 340, fill=(140, 200, 255), width=2)
    glow(img, 240, 230, 160, (100, 170, 255), 0.25, ry=30)
    sx, sy = 240 + 30 * math.sin(T * 0.4), 70 + 6 * math.sin(T * 0.9)
    sig.satellite(d, sx, sy, 1.6, 0.15 * math.sin(T * 0.6), T=T)
    glow(img, sx, sy, 30, sig.SIG, 0.3)
    for (ax, ay), back in ((pa, False), (pb, True)):
        n = 18
        for i in range(n):
            u = i / n
            x, y = lerp(ax, sx, u), lerp(ay, sy, u)
            if (i + int(T * 10) * (1 if not back else -1)) % 3 == 0: d.point((x, y), fill=sig.SIG)
        for k in range(2):
            u = (lt * 0.7 + k / 2) % 1
            if back: u = 1 - u
            x, y = (lerp(ax, sx, u), lerp(ay, sy, u)) if not back else (lerp(sx, ax, 1 - u), lerp(sy, ay, 1 - u))
            sig.heart_at(img, x, y, 1, col=sig.HEART if not back else (150, 230, 255))
    d.rectangle([158, 0, 161, H], fill=(10, 10, 20)); d.rectangle([319, 0, 322, H], fill=(10, 10, 20))
    sig.bubble(img, d, 60, 140, '晚安', f=span(lt, 0.8, 1.1))
    sig.bubble(img, d, 420, 140, '明天见', mine=True, f=span(lt, 1.8, 2.1))
    sig.bars(d, 8, 18, 4, 2); sig.bars(d, 452, 18, 4, 2)


def s_hands(img, d, lt, dur, T, A):
    """何苦残忍逼我把手轻轻放开：雨里牵着的两只手，手指一根根松开；然后两人在雨里各自撑伞走开"""
    def close(img, d, t):
        sky(img, RAINY, 0, H, 5)
        glow(img, 240, 130, 200, (110, 130, 200), 0.25)
        sep = ease(span(t, 2.6, 3.6)) * 70
        sig.hands(img, d, 240, 140, 3, sep, span(t, 0.6, 2.6), T, shade=0.85)
        kit.rain_layer(img, d, T, 140, (140, 160, 220))
        if t > 3.0:
            dy = (t - 3.0) * 120
            d.ellipse([238, 150 + dy, 242, 156 + dy], fill=(200, 220, 255))
        vig(img, 0.5)

    def wide(img, d, t):
        sky(img, RAINY, 0, H, 5)
        pix.city(img, d, 200, 12, 0, (34, 38, 64), (200, 190, 140), 40, 120, 0.2, T)
        d.rectangle([0, 200, W, H], fill=(40, 44, 66))
        props.reflect(img, 200, 70, T, (20, 22, 40), 0.6)
        hx, gx = 230 - t * 30, 250 + t * 30
        person(img, 'boy', hx, 236, view='side', pose='walk', ph=wph(t, 5), expr='sad', arms='umbrella', s=2, flip=True)
        kit.umbrella(d, hx - 6, 136, (240, 132, 74), (190, 90, 56), 22)
        d.line([(hx - 6, 149), (hx - 6, 186)], fill=OUT)
        person(img, 'girl', gx, 236, view='side', pose='walk', ph=wph(t, 5) + 2, expr='sad', arms='umbrella', s=2)
        kit.umbrella(d, gx + 6, 136, (124, 186, 236), (84, 138, 196), 22)
        d.line([(gx + 6, 149), (gx + 6, 186)], fill=OUT)
        kit.rain_layer(img, d, T, 180, (130, 150, 210))
        props.splashes(d, T, 230, 268, 30)
        vig(img, 0.5)
    shots(img, lt, [(0, close), (3.5, wide)], 0.4)


def s_booth(img, d, lt, dur, T, A):
    """请快回来想听你说：夜雨里一座亮着灯的电话亭，他在里面打电话；手机屏幕上"正在呼叫"，信号一格格掉下去"""
    def wide(img, d, t):
        sky(img, RAINY, 0, H, 5)
        pix.city(img, d, 200, 5, 0, (28, 30, 56), (220, 200, 150), 50, 140, 0.2, T)
        d.rectangle([0, 214, W, H], fill=(34, 36, 58))
        pix.lamp(img, d, 120, 216, 1.0, 100)
        g = sig.booth(img, d, 280, 216, T, 1.0)
        person(img, 'boy', 280, 210, view='side', pose='stand', expr='sad', arms='phone', s=1)
        blend_box(img, (int(g[0]), int(g[1]), int(g[2]), int(g[3])), (180, 210, 240), np.full((int(g[3]) - int(g[1]), int(g[2]) - int(g[0])), 0.25))
        props.reflect(img, 216, 54, T, (20, 20, 40), 0.6)
        kit.rain_layer(img, d, T, 200, (130, 150, 210))
        for k in range(3):
            u = (t * 0.8 + k / 3) % 1
            r = 10 + u * 60
            d.arc([284 - r, 170 - r, 284 + r, 170 + r], 290, 340, fill=lerpc(sig.SIG, (30, 30, 60), u))
        vig(img, 0.5)

    def screen(img, d, t):
        img.paste((10, 10, 24), (0, 0, W, H))
        box = sig.phone(img, d, 170, 20, 140, 230, scr=(24, 30, 60))
        sx0, sy0, sx1, sy1 = box
        cx = (sx0 + sx1) / 2
        lv = max(0, 3 - t * 1.2)
        sig.bars(d, sx1 - 14, sy0 + 9, lv, 1, on=(230, 236, 255))
        sig.pix_text(d, '23:47', sx0 + 2, sy0 + 1, (230, 236, 255))
        d.ellipse([cx - 22, sy0 + 40, cx + 22, sy0 + 84], fill=(255, 200, 220))
        sig.heart_at(img, cx, sy0 + 62, 3)
        sig.pix_text(d, '她', cx - 6, sy0 + 92, (255, 255, 255), 16)
        sig.pix_text(d, '正在呼叫' + '.' * (int(t * 3) % 4), cx - 26, sy0 + 114, (170, 190, 230))
        for k in range(3):
            u = (t * 0.9 + k / 3) % 1
            r = 26 + u * 40
            d.ellipse([cx - r, sy0 + 62 - r, cx + r, sy0 + 62 + r], outline=lerpc((140, 160, 220), (24, 30, 60), u))
        d.ellipse([cx - 14, sy1 - 40, cx + 14, sy1 - 12], fill=(230, 60, 70))
        d.rectangle([cx - 8, sy1 - 27, cx + 8, sy1 - 24], fill=(255, 255, 255))
        props.drops_on_glass(img, d, T, (sx0, sy0, sx1, sy1), 30, 5)
        if int(t * 2) % 2 == 0: text(img, '嘟——', 380, 120, col=(200, 210, 240), font=FONT)
    shots(img, lt, [(0, wide), (2.4, screen)], 0.35)


def s_still(img, d, lt, dur, T, A):
    """说你还在耶：屏幕亮了，"我还在"；雨停了，云散开，月亮出来，一颗发光的心从天上落进他手里"""
    def screen(img, d, t):
        img.paste((10, 10, 24), (0, 0, W, H))
        glow(img, 240, 135, 200, (150, 200, 255), 0.3 * clamp(t / 0.5))
        box = sig.phone(img, d, 170, 20, 140, 230, scr=lerpc((24, 30, 60), (40, 50, 100), clamp(t / 0.5)))
        sx0, sy0, sx1, sy1 = box
        sig.bars(d, sx1 - 14, sy0 + 9, 4 * span(t, 0.2, 1.0), 1, on=(230, 236, 255))
        sig.pix_text(d, '23:48', sx0 + 2, sy0 + 1, (230, 236, 255))
        sig.pix_text(d, '她', (sx0 + sx1) / 2 - 6, sy0 + 15, (255, 255, 255))
        d.line([(sx0, sy0 + 30), (sx1, sy0 + 30)], fill=(50, 56, 90))
        sig.bubble(img, d, sx1 - 6, sy0 + 40, '回来吧', mine=True)
        if t < 0.8: sig.typing(d, sx0 + 6, sy0 + 66, T)
        else:
            sig.bubble(img, d, sx0 + 6, sy0 + 66, '我还在', f=span(t, 0.8, 1.1), size=16)
            if t > 1.1:
                sig.heart_at(img, sx0 + 84, sy0 + 76, 2)
                for j in range(6):
                    a = j * math.pi / 3 + t
                    sparkle(d, int(sx0 + 84 + math.cos(a) * 18), int(sy0 + 76 + math.sin(a) * 14), T + j, (255, 220, 240), 2)

    def wide(img, d, t):
        clear = ease(span(t, 0.0, 3.0))
        sky(img, mix_stops(RAINY, NIGHT, clear), 0, H, 6)
        stars(d, T, 200, clear, 220)
        pix.moon(d, 360, 60, 16)
        glow(img, 360, 60, 50, (220, 220, 255), 0.4 * clear)
        for k in range(4):                                      # 云往两边散开
            side = -1 if k % 2 else 1
            cx_ = 240 + side * (40 + k * 30) + side * clear * 260
            cloud(d, cx_ - 60, 30 + k * 18, 3, (60, 64, 90), (44, 46, 70))
        pix.city(img, d, 200, 5, 0, (28, 30, 56), (220, 200, 150), 50, 140, 0.2 + 0.2 * clear, T)
        d.rectangle([0, 214, W, H], fill=(34, 36, 58))
        sig.booth(img, d, 330, 216, T, 1.0)
        props.reflect(img, 216, 54, T, (20, 20, 40), 0.6)
        kit.rain_layer(img, d, T, 200, (130, 150, 210), a=1 - clear)
        hx = lerp(330, 250, ease(span(t, 0.3, 1.8)))
        walking = 0.3 < t < 1.8
        catch = span(t, 2.4, 4.6)
        person(img, 'boy', hx, 214, view='side' if walking else 'front', pose='walk' if walking else 'stand', ph=wph(t, 6),
               expr='surprised' if catch < 0.9 else 'happy', arms='flowers' if catch > 0.95 else ('up' if catch > 0 else 'auto'), s=2,
               flip=walking)
        hy = lerp(-20, 168, ease(catch))
        if t > 2.2:
            glow(img, hx, hy, 40, sig.HEART, 0.5)
            sig.heart_at(img, hx, hy, 2)
            for j in range(8):
                u = (T * 0.8 + j / 8) % 1
                d.point((hx + 10 * math.sin(j * 2 + T), hy - 10 - u * 40), fill=lerpc((255, 220, 240), (30, 30, 60), u))
        if catch >= 1:
            kit.heart_constellation(img, d, 240, 80, 3, span(t, 4.8, 6.4), T)
        vig(img, 0.4)
    shots(img, lt, [(0, screen), (2.2, wide)], 0.5, 'white')


def s_hum(img, d, lt, dur, T, A):
    """呜：他躺在楼顶上看天，星星鲸鱼慢慢游过头顶，极光飘着"""
    kit.night(img, d, T, DEEP, 240)
    M.aurora(img, T, 20, 110, 0.4)
    u = span(lt, 0, dur)
    sig.whale(img, d, lerp(-60, W + 60, u), 80 + 10 * math.sin(lt), 3, T)
    sig.rooftop(d, -10, W + 10, 230, (26, 26, 56), (60, 60, 110), None, T, True, 4)
    kit.lying(img, 'boy', 200, 228, 2, 'smile')
    sig.can(d, 260, 222, 1)
    for j in range(5):
        pix.meteor(d, lt, 0.6 + j * 0.9, 300 + j * 30, 10 + j * 8, -90, 50, 0.8)


def s_inter(img, d, lt, dur, T, A):
    """啊啊啊啊 + 间奏：一颗发光的心从城市飞上天，穿过云层、卫星和星球，绕过月亮，再一路落到她的窗前——已送达"""
    def rise(img, d, t):
        u = ease(clamp(t / 3.6))
        sky(img, mix_stops(NIGHT, DEEP, u), 0, H, 6)
        stars(d, T, H, 0.4 + 0.6 * u, 220)
        oy = u * 420
        sc_city_y = 250 + oy
        if sc_city_y < H + 140:
            pix.city(img, d, sc_city_y, 7, 0, (20, 22, 54), (255, 214, 140), 60, 160, 0.3, T)
        for k in range(6):
            r = rng(k)
            cy = (r.uniform(-200, 200) + oy * (1.2 + 0.2 * k)) - 60
            if -40 < cy < H + 40: cloud(d, r.uniform(-40, 420), cy, 3 + k % 2, (90, 96, 150), (70, 74, 120))
        hy = 200 - 80 * u
        heart_fly(img, d, 240, hy, T)

    def space(img, d, t):
        img.paste((2, 2, 14), (0, 0, W, H))
        for k in range(70):                                     # 星星往后飞：从中间往外的光线
            r = rng(k)
            a = r.uniform(0, 6.28); sp = r.uniform(0.3, 1)
            f = (t * 0.6 * sp + r.random()) % 1
            r0, r1 = 20 + f ** 2 * 300, 20 + (f + 0.04) ** 2 * 300
            d.line([(240 + math.cos(a) * r0, 135 + math.sin(a) * r0), (240 + math.cos(a) * r1, 135 + math.sin(a) * r1)],
                   fill=lerpc((40, 50, 100), (220, 230, 255), f))
        kit.galaxy(img, 0.5, 8, 0.6, 30)
        sx = lerp(520, -60, t / 4.5)
        sig.planet(img, d, sx, 70, 34, T, ground=(240, 170, 120), ground_d=(200, 120, 90), sea=(150, 110, 200), ring=(255, 220, 160))
        sig.satellite(d, lerp(-40, 520, t / 3.5), 200, 1.4, 0.3, T=T)
        sig.planet(img, d, lerp(600, 300, t / 4.5), 220, 18, T, ground=(150, 220, 200), sea=(70, 120, 200))
        heart_fly(img, d, 240, 135, T)

    def orbit(img, d, t):
        img.paste((2, 2, 14), (0, 0, W, H))
        stars(d, T, H, 1, 240)
        mx, my = 240, 135
        glow(img, mx, my, 150, (240, 230, 200), 0.3)
        d.ellipse([mx - 70, my - 70, mx + 70, my + 70], fill=(240, 236, 214))
        for cx_, cy_, cr in ((-25, -20, 14), (22, 18, 10), (10, -38, 7), (-12, 34, 8), (35, -8, 6)):
            d.ellipse([mx + cx_ - cr, my + cy_ - cr, mx + cx_ + cr, my + cy_ + cr], fill=(214, 206, 186))
        a = -math.pi / 2 + t * 2.0
        hx, hy = mx + math.cos(a) * 100, my + math.sin(a) * 50
        behind = math.sin(a) < 0 and abs(math.cos(a)) < 0.7
        for j in range(12):
            aa = a - j * 0.08
            d.point((mx + math.cos(aa) * 100, my + math.sin(aa) * 50), fill=lerpc(sig.HEART, (2, 2, 14), j / 12))
        if not behind: heart_fly(img, d, hx, hy, T)
        if t > 2.0:
            f = (t - 2.0) / 0.5
            if f < 1: pix.dither_fade(img, 1 - abs(1 - 2 * f), (255, 250, 255))

    def arrive(img, d, t):
        kit.night(img, d, T, NIGHT, 200)
        pix.moon(d, 80, 50, 12)
        # 她家的楼：中间一扇亮着的窗
        pix.city(img, d, 270, 3, 0, (24, 26, 60), (255, 214, 140), 60, 140, 0.2, T)
        d.rectangle([150, 60, 330, H], fill=(46, 44, 86)); d.rectangle([150, 60, 330, 66], fill=(70, 66, 120))
        wx0, wy0, wx1, wy1 = 190, 110, 290, 200
        d.rectangle([wx0, wy0, wx1, wy1], fill=(255, 220, 160))
        glow(img, 240, 155, 110, (255, 210, 150), 0.35)
        person(img, 'girl', 240, 206, view='front', pose='stand', expr='surprised' if t < 1.6 else 'laugh', arms='phone' if t < 1.6 else 'up', s=2)
        d.rectangle([wx0, wy0, wx1, wy1], outline=(120, 90, 80), width=4)
        d.line([(240, wy0), (240, wy1)], fill=(120, 90, 80), width=2)
        d.rectangle([wx0 - 8, wy1, wx1 + 8, wy1 + 6], fill=(150, 120, 100))
        u = ease(span(t, 0.0, 1.4))
        hx, hy = lerp(420, 240, u), lerp(-20, 120, u)
        if t < 1.6: heart_fly(img, d, hx, hy, T)
        if t > 1.4:
            f = span(t, 1.4, 1.8)
            sig.bubble(img, d, 300, 92, '已送达', f=f, col=(150, 236, 140))
            for j in range(10):
                a = j * math.pi / 5 + t
                rr = 30 + (t - 1.4) * 60
                if rr < 140: sig.heart_at(img, 240 + math.cos(a) * rr, 140 + math.sin(a) * rr * 0.6, 1, alpha=clamp(1 - (t - 1.4) / 2))
        vig(img, 0.35)
    shots(img, lt, [(0, rise), (3.6, space), (8.0, orbit), (10.6, arrive)], 0.4)


def heart_fly(img, d, x, y, T):
    glow(img, x, y, 36, sig.HEART, 0.55)
    for j in range(10):
        d.point((x + 6 * math.sin(j * 1.7 + T * 4), y + 8 + j * 3), fill=lerpc((255, 200, 220), (40, 30, 70), j / 10))
    sig.heart_at(img, x, y, 2 + int(thump(T, 0.2) > 0.5))
    sig.wifi(img, d, x, y - 10, 1, T * 0.8)
