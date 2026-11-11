"""几分之几 · 桥段、最后一段和片尾。

天明的平原，两个人牵着手看日出；那个画面变成一张照片越退越远，他怎么跑也追不上，照片在鼓点上碎成满天的像素；
碎片在他手心里聚成缺了的那一块；车站，她坐的火车开走了，他追到站台尽头；长椅上日夜和四季飞快地转，他一点点变老；
最后回到片头那片被太阳压着的平原，年轻的两个人的影子牵着手走向太阳，他手里那一块升上天变成一颗星。
片尾：太阳落下去，只剩一道地平线，它缩回片头那道分数线，两个"几"再拼一次，然后碎掉，只剩一个像素闪两下。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
import motifs
import sc_a
from pix import (W, H, FONT, FONT_S, OUT, SKIN, SKIN_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, rng)
from props import dpaste, person_s, mix_stops, shots, CREAM, GOLD, GOLD_L, PINK, PINK_L
from motifs import GOLD_SKY, DUSK_SKY, DAWN_SKY, NIGHT_SKY, NOON_SKY, PLAIN_GOLD, PLAIN_DAWN, PLAIN_NIGHT, PIECE

YY, XX = np.mgrid[0:H, 0:W]


# ---------------------------------------------------------------- 21 在那一个回不去的天明
def _dawn(img, d, t, T):
    sy = lerp(206, 150, eout(span(t, 0, 5)))
    sky = mix_stops(DAWN_SKY, GOLD_SKY, span(t, 1, 6) * 0.5)
    motifs.sun_plain(img, d, T, sky=sky, sx=300, sy=sy, sr=60, hz=176, dip=4, plain=PLAIN_DAWN, glow_a=0.5)
    for k in range(10):                                        # 太阳的光芒，跟着拍子一亮
        a = -math.pi + k * math.pi / 9 + t * 0.03
        b = props.thump(T, 0.5)
        tfill(img, 'polygon', [(300, sy), (300 + math.cos(a - 0.04) * 400, sy + math.sin(a - 0.04) * 400),
                                (300 + math.cos(a + 0.04) * 400, sy + math.sin(a + 0.04) * 400)], (255, 236, 190), 0.06 + 0.06 * b)
    sh = (0.8, 0.76, 0.84)
    person_s(img, 'boy', 228, 232, 2, view='back', arms='hold_r', shade=sh)
    person_s(img, 'girl', 254, 232, 2, view='back', arms='hold_l', shade=sh)


@lru_cache(None)
def dawn_still(w, h):
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    _dawn(im, d, 4.0, 177.0)
    return im.resize((w, h), Image.BOX)


def _void(img, d, T, k=1.0):
    pix.sky(img, ((0, (10, 8, 26)), (1, (34, 22, 50))))
    r = rng(1)
    for i in range(40):                                        # 速度线
        y = r.uniform(10, 230); sp = r.uniform(200, 400)
        x = (r.uniform(0, W) - T * sp) % (W + 80) - 40
        d.line([(x, y), (x + 20 + sp * 0.06, y)], fill=lerpc((40, 30, 70), (120, 100, 160), r.random() * k))


def _chase(img, d, t, T):
    _void(img, d, T)
    sc = lerp(0.6, 0.22, ease(span(t, 0, 5)))
    pw, ph = int(W * sc), int(H * sc)
    cx, cy = lerp(300, 340, span(t, 0, 5)), lerp(110, 96, span(t, 0, 5))
    glow(img, cx, cy, pw * 0.9, (255, 200, 150), 0.3)
    props.polaroid(img, d, cx, cy, dawn_still(pw, ph))
    t_start = T - t
    for b in props.beats_in(t_start, t_start + 5.2):           # 每个拍子从照片里飞出一把碎片
        k = T - b
        if 0 <= k < 1.2:
            r = rng(int(b * 100))
            for i in range(14):
                vx, vy = -r.uniform(180, 320), r.uniform(-60, 80)
                x, y = cx + vx * k, cy + vy * k
                c = r.choice(((255, 200, 140), (255, 230, 180), (200, 150, 190), (150, 140, 200)))
                d.rectangle([x, y, x + 2, y + 2], fill=lerpc(c, (20, 16, 40), k / 1.2))
    d.line([(0, 232), (W, 232)], fill=(60, 50, 90))
    person_s(img, 'boy', 150, 232, 2, view='side', pose='run', ph=pix.wph(t, 11), expr='sad', arms='reach' if t > 3.5 else 'auto')


def _shatter(img, d, t, T):
    _void(img, d, T, 0.4)
    t_start = T - t
    bs = props.beats_in(t_start + 0.5, t_start + 2)
    tb = (bs[0] - t_start) if bs else 0.8
    sc = 0.22
    pw, ph = int(W * sc), int(H * sc)
    cx, cy = 340, 96
    still = dawn_still(pw, ph)
    if t < tb:
        props.polaroid(img, d, cx, cy, still)
        k = span(t, tb - 0.5, tb)
        for j in range(int(k * 6)):                            # 先裂开几道缝
            r = rng(j)
            x0 = cx + r.uniform(-20, 20); y0 = cy + r.uniform(-10, 10)
            d.line([(x0, y0), (x0 + r.uniform(-14, 14), y0 + r.uniform(-12, 12))], fill=(255, 255, 255))
        person_s(img, 'boy', 200, 232, 2, view='side', expr='sad', arms='reach')
    else:
        k = t - tb
        arr = np.asarray(still)
        r = rng(9)
        for y in range(0, ph, 3):
            for x in range(0, pw, 3):
                c = tuple(int(v) for v in arr[min(ph - 1, y + 1), min(pw - 1, x + 1)])
                sx, sy = cx - pw / 2 + x, cy - ph / 2 + y
                ang = math.atan2(sy - cy, sx - cx) + r.uniform(-0.6, 0.6)
                sp = r.uniform(60, 220)
                burst = 1 - math.exp(-k * 3)
                px = sx + math.cos(ang) * sp * burst / 3
                py = sy + math.sin(ang) * sp * burst / 3
                # 慢慢被吸进围着他转的一圈
                orb = ease(span(k, 1.0, 3.6))
                a2 = r.uniform(0, 2 * math.pi) + k * r.uniform(0.6, 1.4)
                rad = r.uniform(30, 90)
                ox, oy = 200 + math.cos(a2) * rad * 1.6, 170 + math.sin(a2) * rad * 0.6
                px, py = lerp(px, ox, orb), lerp(py, oy, orb)
                d.rectangle([px, py, px + 2, py + 2], fill=c)
        if k < 0.25: props.shake(img, k, 6, 0.25); d = ImageDraw.Draw(img)
        if k < 0.2: pix.blend_box(img, (0, 0, W, H), (255, 250, 240), np.full((H, W), 0.8 * (1 - k / 0.2)))
        person_s(img, 'boy', 200, 232, 2, view='side', pose='sit' if k > 1.2 else 'stand', expr='sad')


def s_dawn(img, d, lt, dur, T, amp):
    shots(img, lt, [(0, _dawn), (5.0, _chase), (10.0, _shatter)], 0.4, T=T)


# ---------------------------------------------------------------- 22 我的 几分之几
def s_mine(img, d, lt, dur, T, amp):
    pix.sky(img, ((0, (12, 10, 30)), (1, (40, 26, 56))))
    pix.stars(d, T, H, 0.5, 100)
    tx, ty = 240, 118
    form = 2.4
    r = rng(9)
    for i in range(160):
        a0 = r.uniform(0, 2 * math.pi); rad = r.uniform(40, 200)
        c = r.choice(((255, 200, 140), (255, 230, 180), (200, 150, 190), (150, 140, 200), (255, 170, 160)))
        f = ease(span(lt, 0, form - r.uniform(0, 0.5)))
        a = a0 + lt * 1.2 + f * 3
        rr = rad * (1 - f)
        x, y = tx + math.cos(a) * rr * 1.4, ty + math.sin(a) * rr * 0.7
        if f < 1: d.rectangle([x, y, x + 1, y + 1], fill=c)
    k = span(lt, form - 0.4, form)
    glow(img, tx, ty, 50 * k + 10, (255, 220, 160), 0.6 * k)
    if lt > form:
        u = lt - form
        y = lerp(ty, 176, ease(span(u, 0.4, 1.4)))
        b = props.thump(T, 0.4)
        glow(img, tx, y, 30 + 10 * b, (255, 210, 150), 0.5 + 0.2 * b)
        motifs.fly_piece(img, 7, 3.0, tx, y, 1.0, col=(255, 214, 160), glow_a=0.3, glowing=True)
        if u < 0.5: pix.twinkle(d, tx, ty, u / 0.5, (255, 255, 255), 10)
        for i in range(6):
            pix.twinkle(d, int(tx + math.cos(i + T) * 26), int(y + math.sin(i * 2 + T) * 16), (T * 0.9 + i / 6) % 1, (255, 240, 200), 3)
    motifs.cupped_hands(img, d, 240, H + 16, 1.25)


# ---------------------------------------------------------------- 23 你终于还是离开我的生命
def s_station(img, d, lt, dur, T, amp):
    night = span(lt, 0, dur) * 0.6
    pix.sky(img, mix_stops(DUSK_SKY, NIGHT_SKY, night), 0, 212)
    pix.stars(d, T, 150, night, 120)
    pix.city(img, d, 190, 51, 0, lerpc((120, 80, 110), (40, 36, 70), night), (255, 210, 140), 20, 70, 0.25, T, edge=None)
    go = 1.4
    x = 470 + (0.5 * 60 * (lt - go) ** 2 if lt > go else 0)
    props.rails(d, 214, x, rail_hi=(160, 150, 160))
    props.train(img, d, x, 214, T, cars=3, s=1, night=night, lit=0.7, hero=(0, 2), people=True, headlight=0.8)
    hx = x - 92 - 4 - 112 + 9 + 2 * 17 + 5
    if hx < W + 10:                                            # 她在车窗里挥手
        wv = round(math.sin(T * 10) * 2)
        d.rectangle([hx + 5 + wv, 168, hx + 6 + wv, 170], fill=SKIN)
    props.smoke(img, x - 30, 160, T, 7, vx=-60 - (lt - go) * 30 if lt > go else -20, vy=-10, seed=3, a=0.8)
    # 站台：顶棚、柱子、黄线
    d.rectangle([0, 214, W, H], fill=(150, 146, 156)); d.rectangle([0, 214, W, 218], fill=(196, 190, 196))
    for xx in range(0, W, 8): d.rectangle([xx, 220, xx + 4, 221], fill=(250, 210, 80))
    d.rectangle([0, 0, W, 10], fill=(70, 60, 80)); d.rectangle([0, 10, W, 13], fill=(100, 86, 104))
    for px in (40, 200, 360):
        d.rectangle([px, 13, px + 5, 214], fill=(90, 80, 100))
    for px in (120, 280, 440):
        on = span(lt, 4.6, 5.2)
        d.rectangle([px - 6, 13, px + 6, 18], fill=lerpc((120, 120, 130), (255, 236, 180), on))
        if on > 0:
            glow(img, px, 18, 24, (255, 236, 180), 0.5 * on)
            tfill(img, 'polygon', [(px - 6, 18), (px + 6, 18), (px + 30, 240), (px - 30, 240)], (255, 236, 180), 0.08 * on)
    d.rectangle([452, 196, 456, 236], fill=(80, 70, 90)); d.rectangle([440, 186, 468, 198], fill=(240, 236, 220))
    if lt < 1.6:
        person_s(img, 'boy', 250, 236, 2, view='side', arms='wave', ph=int(T * 5), expr='sad')
    elif lt < 4.2:
        xb = lerp(250, 420, ease(span(lt, 1.6, 4.2)))
        person_s(img, 'boy', xb, 236, 2, view='side', pose='run', ph=pix.wph(lt, 11), expr='sad')
    else:
        person_s(img, 'boy', 420, 236, 2, view='side', arms='reach' if lt < 5.6 else 'down', expr='sad')


# ---------------------------------------------------------------- 24 留下每天都在变老的我
CAL = [str(n) for n in range(1, 32)]


def s_aging(img, d, lt, dur, T, amp):
    stop = 6.0
    live = min(lt, stop)
    ph = (live / 0.55) % 1
    night = 0.5 - 0.5 * math.cos(2 * math.pi * ph)
    if lt > stop - 0.4: night *= 1 - span(lt, stop - 0.4, stop)
    seasons = ('summer', 'autumn', 'winter', 'spring', 'summer')
    season = seasons[min(4, int(live / 1.3))]
    sky = mix_stops(GOLD_SKY if lt > stop - 0.4 else NOON_SKY, NIGHT_SKY, night)
    pix.sky(img, sky, 0, 176)
    pix.stars(d, T, 176, night, 140)
    u = math.pi * (ph * 2 % 1)
    sx_, sy_ = 240 - math.cos(u) * 230, 170 - math.sin(u) * 130
    if lt < stop - 0.4:
        if ph < 0.5: d.ellipse([sx_ - 8, sy_ - 8, sx_ + 8, sy_ + 8], fill=(255, 236, 170))
        else: pix.moon(d, sx_, sy_, 7)
    gcol = motifs.SEASON[season]['ground']
    pix.hills(d, 176, 4, 0.01, 1.2, lerpc(gcol, (90, 110, 140), 0.3))
    pix.sky(img, ((0, gcol), (1, lerpc(gcol, (0, 0, 0), 0.25))), 186, H)
    pix.darken(img, 0.4 * night, (10, 10, 40))
    d = ImageDraw.Draw(img)
    motifs.season_tree(d, 150, 222, lerp(1.6, 2.4, lt / dur), season, T)
    motifs.bench(d, 262, 226, 1)
    if season == 'autumn': props.leaves(d, T, 30, seed=3)
    elif season == 'winter': pix.snow(d, T, 90, seed=2)
    elif season == 'spring': pix.petals(d, T, 30, seed=5)
    old = span(lt, 2.4, 3.6)
    props.ghost(img, 'boy', 262, 222, 2, 1.0 if old < 1 else 0, 'young', 'side', 'sit', 'smile')
    if old > 0: props.ghost(img, 'boy', 262, 222, 2, old, 'old', 'side', 'sit', 'smile')
    if lt > 4.2:                                               # 拐杖靠在长椅边
        d.line([(286, 196), (290, 226)], fill=(110, 74, 50), width=2); d.line([(286, 196), (282, 194)], fill=(110, 74, 50), width=2)
    # 右上角的日历一页页往下撕
    cx, cy = 410, 50
    n = int(live / 0.16)
    d.rectangle([cx - 24, cy - 26, cx + 24, cy + 28], fill=OUT)
    d.rectangle([cx - 23, cy - 25, cx + 23, cy + 27], fill=(255, 252, 244)); d.rectangle([cx - 23, cy - 25, cx + 23, cy - 14], fill=(226, 80, 80))
    props.big_text(img, CAL[n % 31], cx, cy + 8, 2, top=(60, 50, 70), bot=(40, 30, 50), line=(255, 252, 244), out=(255, 252, 244))
    if lt < stop:
        k = (live / 0.16) % 1
        px, py = cx + k * 40, cy + k * k * 90
        d.polygon([(px - 18, py - 12), (px + 18, py - 14 + k * 8), (px + 16, py + 20), (px - 20, py + 18)], fill=(250, 246, 236))


# ---------------------------------------------------------------- 25 请记得我曾经 爱过
def s_remember(img, d, lt, dur, T, amp, sun_drop=0.0, sky=None):
    hf = motifs.sun_plain(img, d, T, sky=sky or GOLD_SKY, sx=290, sy=172 + sun_drop, sr=78, hz=176, dip=12, glow_a=0.6 * (1 - span(sun_drop, 0, 80)),
                          sun_a=1 - span(sun_drop, 60, 100))
    for x, s_ in ((60, 0.9), (96, 0.6)):
        pix.tree_round(d, x, hf(x) + 1, s_, (130, 84, 70), (160, 104, 80), (100, 64, 56))
    # 年轻时的两个人，牵着手沿着土路走向太阳，越走越小、越来越淡
    f = span(lt, 0.4, 5.2)
    if 0 < f < 1:
        y = lerp(226, 184, ease(f)); sc = lerp(1.6, 0.5, ease(f)); gap = 13 * sc
        cx = lerp(312, 290, ease(f))
        a = 0.75 * (1 - span(f, 0.75, 1)) * span(f, 0, 0.15)
        for who, dx, arms in (('boy', -gap, 'hold_r'), ('girl', gap, 'hold_l')):
            im = pix.char_img(who, 'young', 'back', 'walk', pix.wph(lt, 6), 'smile', arms)
            arr = np.array(im).astype(float); arr[..., :3] = arr[..., :3] * 0.6 + np.array((255, 226, 170)) * 0.4
            im = Image.fromarray(arr.astype(np.uint8))
            im = im.resize((max(1, round(pix.CW * sc)), max(1, round(pix.CH * sc))), Image.NEAREST)
            dpaste(img, im, cx + dx - pix.CX * sc, y - pix.FY * sc, a)
    tfill(img, 'polygon', [(242, 232), (258, 232), (270, H), (222, H)], (110, 64, 40), 0.45)
    motifs.old_man(img, d, 250, 232, view='back', s=2, shade=(0.86, 0.8, 0.82))
    for i in range(0, W, 6):
        motifs.wheat(d, i + 3 * math.sin(i), H - 1 - (i % 4) * 3, 16 + (i * 7) % 9, T, wind=0.8, ph=i)
    # 他手里那一块升上天，变成一颗星
    k = span(lt, 3.6, 5.6)
    if k > 0:
        x, y = lerp(250, 330, ease(k)), lerp(192, 40, ease(k))
        if k < 1:
            motifs.fly_piece(img, 7, 1.0, x, y, 1.0, col=(255, 214, 160), glow_a=0.4, glowing=True)
        else:
            glow(img, x, y, 10, (255, 240, 200), 0.6)
            pix.twinkle(d, int(x), int(y), 0.5, (255, 255, 240), 4 + round(props.thump(T, 0.6) * 2))
    elif lt > 0.5:
        glow(img, 250, 188, 10, (255, 214, 160), 0.5)


def star_pos():
    return 330, 40


# ---------------------------------------------------------------- 片尾
def s_end(img, d, lt, dur, T, amp):
    BAR = sc_a.BAR
    k = span(lt, 3.2, 4.6)
    if lt < 4.6:
        drop = ease(span(lt, 0, 3.6)) * 100
        sky = mix_stops(mix_stops(GOLD_SKY, DUSK_SKY, span(lt, 0, 1.8)), NIGHT_SKY, span(lt, 1.8, 3.6))
        s_remember(img, d, 9.0, dur, T, amp, sun_drop=drop, sky=sky)
        d = ImageDraw.Draw(img)
        pix.stars(d, T, 170, span(lt, 1.5, 3.5), 160)
        pix.dither_fade(img, k, (6, 6, 20))                    # 世界暗下去，只剩一道地平线
    else:
        sc_a.dark_bg(img, d, T, 1 - span(lt, 8.6, 9.6))
    by = lerp(176, 150, ease(span(lt, 4.6, 5.6)))
    half = lerp(W / 2 + 10, 62, ease(span(lt, 4.4, 5.6)))
    if lt > 8.6: half = lerp(62, 1, ein(span(lt, 8.6, 9.2)))
    if lt > 3.2:
        on = lt < 9.2 or (lt < 10.1 and int((lt - 9.2) / 0.3) % 2 == 0)
        if on:
            glow(img, W / 2, by, half + 14, BAR, 0.35 * k, ry=10)
            d.rectangle([W / 2 - half - 1, by - 2, W / 2 + half + 1, by + 2], fill=(46, 26, 40))
            d.rectangle([W / 2 - half, by - 1, W / 2 + half, by + 1], fill=BAR)
    sx, sy = star_pos()
    if 3.2 < lt < 8.6: pix.twinkle(d, sx, sy, 0.5, (255, 255, 240), 3)
    # 两个"几"再拼一次，然后碎掉往下掉
    if 5.0 < lt < 9.6:
        num_c, den_c = (W / 2, 150 - 30), (W / 2, 150 + 35)
        brk = 8.2
        if lt < brk:
            ok1 = sc_a.blocks_fly(img, d, '几', 3, *num_c, lt, 5.0, 5.7, 11, 'top', 0.6)
            ok2 = sc_a.blocks_fly(img, d, '几', 3, *den_c, lt, 5.3, 6.0, 12, 'bottom', 0.6)
            if ok1 and ok2:
                kk = span(lt, 6.6, 6.9)
                props.big_text(img, '几', *num_c, 3, kk, **sc_a.TITLE_KW)
                props.big_text(img, '几', *den_c, 3, kk, **sc_a.TITLE_KW)
            ar = props.artist_str()
            a = span(lt, 6.6, 7.1)
            if a > 0:
                pix.text(img, f'{ar}《{props.title_str()}》' if ar else props.title_str(), W / 2, 232, col=(236, 226, 214), font=FONT_S, alpha=a)
        else:
            r = rng(5)
            for cx, cy in (num_c, den_c):
                for (bx, by_, col) in sc_a.glyph_blocks('几', 3, cx, cy):
                    u = lt - brk - r.uniform(0, 0.4)
                    if u < 0: d.rectangle([bx, by_, bx + 2, by_ + 2], fill=col); continue
                    yy = by_ + 160 * u * u; xx = bx + r.uniform(-20, 20) * u
                    if yy < H: d.rectangle([xx, yy, xx + 2, yy + 2], fill=lerpc(col, (20, 16, 40), clamp(u)))


s_end.no_sub = True
