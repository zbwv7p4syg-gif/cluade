"""几分之几 · 第二段副歌和"离开"。

一个只有四种绿色的掌机世界，他一个人往前走，她从天上跳下来，"2P"加入，世界一下子有了颜色；
一张张拍立得飞进那颗心，每一块都换成了回忆的照片，分数从 3/8 数到 7/8；
放大的他身上缺了好多像素，金色和粉色的小方块从四面飞来一格格补上；原来是她在吹；
她在门口挥手，走进门外的光里，房间从门口开始褪成灰色；心里的回忆一块块变成旧照片的颜色，落回他胸口；
夜里窗边，她的影子靠在他胸口，跟着呼吸一亮一暗。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
import motifs
from pix import (W, H, FONT, FONT_S, OUT, SKIN, SKIN_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, rng)
from props import dpaste, person_s, mix_stops, shots, CREAM, GOLD, GOLD_L, PINK, PINK_L
from motifs import GOLD_SKY, DUSK_SKY, DAWN_SKY, NIGHT_SKY, NOON_SKY, PLAIN_GOLD, PLAIN_NIGHT, PIECE

YY, XX = np.mgrid[0:H, 0:W]
MEM_T = [19.0, 25.0, 44.5, 52.0, 74.5, 94.0, 108.0, 112.5]     # 回忆的照片取自全片这些时刻


# ---------------------------------------------------------------- 14 那一天你走进了我的生命（掌机世界）
PLAT = [(320, 156, 3), (430, 128, 2), (560, 150, 3), (690, 118, 2), (800, 146, 4), (940, 124, 2)]


def hud(img, d, x, label, n, right=False):
    pix.text(img, label, x, 14, col=(255, 252, 240), font=FONT_S, anchor='lt' if not right else 'lt')
    for k in range(n):
        pix.put(img, 'heart', x + 26 + k * 10, 21, 1)


def _world(img, d, off, T):
    pix.sky(img, ((0, (120, 190, 250)), (1, (210, 240, 255))), 0, 208)
    for i in range(4):
        x = (i * 150 - off * 0.15) % (W + 120) - 80
        pix.cloud(d, x, 26 + (i % 2) * 22, 2, (255, 255, 255), (220, 236, 250))
    for i in range(5):
        x = (i * 130 - off * 0.35) % (W + 160) - 80
        d.ellipse([x - 70, 150, x + 70, 260], fill=(110, 190, 110)); d.ellipse([x - 50, 160, x + 10, 200], fill=(140, 210, 130))
    for i in range(-1, W // 16 + 2):
        x = i * 16 - off % 16
        d.rectangle([x, 208, x + 15, H], fill=(176, 110, 60))
        d.rectangle([x, 208, x + 15, 212], fill=(90, 190, 80)); d.rectangle([x, 212, x + 15, 213], fill=(60, 150, 60))
        d.point([(x + 4, 220), (x + 11, 230), (x + 6, 244), (x + 13, 256)], fill=(140, 84, 46))
        d.line([(x, 208), (x, H)], fill=(150, 92, 50))
    for k in range(-1, 12):
        fx = (k * 53 - off) % (W + 53) - 20
        pix.flower(d, fx, 208, ((255, 120, 150), (255, 230, 90), (255, 255, 255))[k % 3], 0, h=4)
    for px, py, n in PLAT:
        x0 = px - off
        if x0 > W + 10 or x0 + n * 16 < -10: continue
        for j in range(n):
            x = x0 + j * 16
            d.rectangle([x, py, x + 15, py + 15], fill=(236, 150, 90)); d.rectangle([x, py, x + 15, py + 2], fill=(255, 196, 130))
            d.rectangle([x, py + 15, x + 15, py + 15], fill=(170, 90, 60)); d.line([(x, py), (x, py + 15)], fill=(200, 110, 70))
            if j == n // 2:
                d.rectangle([x + 2, py + 3, x + 13, py + 13], fill=(255, 220, 120))
                pix.put(img, 'heart', x + 8, py + 8, 1)
        sy = py - 14 + round(2 * math.sin(T * 4 + px))
        if px - off > 230: pix.put(img, 'star', x0 + n * 8, sy, 1)


def s_game(img, d, lt, dur, T, amp):
    off = lt * 46
    _world(img, d, off, T)
    d = ImageDraw.Draw(img)
    join = 2.9
    jump = lambda t0: math.sin(math.pi * clamp((lt - t0) / 0.5)) * 30 if t0 <= lt < t0 + 0.5 else 0
    t_start = T - lt
    hops = [b - t_start for b in props.beats_in(t_start + join + 0.6, t_start + dur)]
    hb = max([jump(h) for h in hops[::2]] + [0]); hg = max([jump(h) for h in hops[1::2]] + [0])
    person_s(img, 'boy', 160, 208 - hb, 2, view='side', pose='jump' if hb > 2 else 'walk', ph=pix.wph(lt, 6),
             expr='down' if lt < join else 'happy')
    hud(img, d, 10, '1P', 3)
    if lt > 2.1:                                               # 天上一闪，她跳下来
        k = span(lt, 2.1, 2.5)
        if lt < join: pix.twinkle(d, 230, 50, k, (255, 255, 255), 8)
        f = span(lt, 2.4, join)
        y = lerp(30, 208, ein(f)) - hg
        person_s(img, 'girl', 230, y, 2, view='side', pose='jump' if (f < 1 or hg > 2) else 'walk', ph=pix.wph(lt, 6), expr='happy')
        if lt > join:
            hud(img, d, 380, '2P', 3)
            k = lt - join
            if k < 0.5:
                for q in range(6):
                    a = q * math.pi / 5
                    d.point((230 + math.cos(a) * k * 50, 206 - math.sin(a) * k * 20), fill=(255, 255, 255))
    for h in hops:                                             # 吃到星星
        k = lt - h - 0.25
        if 0 < k < 0.5: pix.twinkle(d, 200, 150, k / 0.5, (255, 240, 120), 6)
    arr = np.asarray(img)
    r = 620 * ease(span(lt, join, join + 1.2))
    m = (XX - 230) ** 2 + (YY - 190) ** 2 < (r * (1 - 0.1 * pix.BAYER)) ** 2
    img.paste(Image.fromarray(np.where(m[..., None], arr, motifs.lcd(arr)).astype(np.uint8)))
    if lt > join and lt < join + 0.25: props.shake(img, lt - join, 3, 0.25)


# ---------------------------------------------------------------- 15 谢谢你 成为了我的几分之几（回忆拼成的心）
HC = (196, 122, 4.0)


@lru_cache(None)
def pie_photo(k):
    """第 k 块用的照片：一张回忆的画面，中心对准这一块在心里的位置"""
    cx, cy, s = HC
    heart = motifs._pie(round(s, 2), 8)
    w, h, cents = heart[6], heart[7], heart[8]
    ph = motifs.memory(MEM_T[k], 160, 90)
    can = Image.new('RGB', (w, h), (40, 30, 60))
    ccx, ccy = cents[k]
    can.paste(ph, (int(ccx - 80), int(ccy - 45)))
    return can


def photos():
    return [pie_photo(k) for k in range(8)]


def _pie_bg(img, d, T, warm=1.0):
    pix.sky(img, mix_stops(((0, (30, 24, 60)), (1, (70, 46, 90))), ((0, (90, 60, 110)), (0.6, (210, 130, 140)), (1, (255, 196, 150))), warm))
    props.bokeh(img, T, 16, ((255, 200, 120), (255, 150, 170), (150, 200, 255)), seed=8, a=0.22)


def s_memories(img, d, lt, dur, T, amp):
    _pie_bg(img, d, T)
    d = ImageDraw.Draw(img)
    cx, cy, s = HC
    cents = motifs.pie_centers(cx, cy, s)
    t_start = T - lt
    lands = [b - t_start for b in props.beats_in(t_start + 2.4, t_start + 9.4)][::2][:4]
    while len(lands) < 4: lands.append(lands[-1] + 1.6 if lands else 3)
    fill = [1, 1, 1, 0, 0, 0, 0, 0]; pop = [0] * 8
    ph = photos()
    use = [None] * 8
    # 前三块（上一段副歌填进去的颜色）先换成照片
    for k in range(3):
        f = span(lt, 0.3 + k * 0.5, 0.9 + k * 0.5)
        use[k] = ph[k] if f > 0.5 else None
        pop[k] = math.sin(math.pi * f) * 0.8
    for j, tl in enumerate(lands):
        k = 3 + j
        if lt >= tl:
            fill[k] = clamp((lt - tl) / 0.15); pop[k] = clamp(1 - (lt - tl) / 0.4); use[k] = ph[k]
    n = 3 + sum(lt >= tl for tl in lands)
    glow(img, cx, cy, 100, (255, 200, 170), 0.2 + 0.1 * props.thump(T))
    motifs.heart_pie(img, cx, cy, s, fill, photos=use, pop=pop)
    for j, tl in enumerate(lands):                             # 拍立得转着飞进来，落进那一块
        k = 3 + j
        f = (lt - (tl - 1.0)) / 1.0
        if 0 <= f < 1:
            tx, ty = cents[k]
            sx, sy = (W + 40, 30 + j * 60) if j % 2 == 0 else (-40, 40 + j * 50)
            e = eout(f)
            x, y = lerp(sx, tx, e), lerp(sy, ty, e) - 30 * math.sin(math.pi * e)
            sm = props.shrink(motifs.memory(MEM_T[k], 160, 90), 40, 24)
            props.polaroid(img, d, x, y, sm, 1.0, 1.0, rot=int((1 - e) * 200 * (1 if j % 2 else -1)) % 360)
        if 0 < lt - tl < 0.5:
            pix.twinkle(d, int(cents[k][0]), int(cents[k][1]), (lt - tl) / 0.5, (255, 255, 255), 7)
    bounce = 0
    last = [tl for tl in lands if lt >= tl]
    if last: bounce = 4 * clamp(1 - (lt - last[-1]) / 0.3)
    motifs.fraction(img, 384, cy - bounce, n, 8, 3)


# ---------------------------------------------------------------- 16 如果我又更完整一点
@lru_cache(None)
def _him_pixels():
    im = pix.char_img('boy', 'young', 'front', 'stand', 0, 'smile')
    a = np.array(im)
    ys, xs = np.nonzero(a[..., 3] > 0)
    r = rng(42)
    data = []
    for x, y in zip(xs, ys):
        if r.random() < 0.5:
            ta = r.uniform(0.3, 5.4) if r.random() > 0.07 else 99.0
            ang = r.uniform(0, 2 * math.pi)
            data.append((int(x), int(y), tuple(int(c) for c in a[y, x, :3]), ta, 240 + math.cos(ang) * 300, 130 + math.sin(ang) * 200,
                         r.choice((GOLD_L, PINK, (255, 236, 160), (255, 180, 200)))))
    return im, data


def s_complete(img, d, lt, dur, T, amp):
    pix.sky(img, ((0, (16, 14, 44)), (1, (44, 30, 74))))
    pix.stars(d, T, H, 0.7, 140)
    im, data = _him_pixels()
    S = 5
    x0, y0 = 240 - pix.CX * S, 238 - pix.FY * S
    done = sum(1 for p in data if p[3] < lt) / max(1, len(data))
    glow(img, 240, 140, 90 + 60 * done, (255, 210, 160), 0.2 + 0.35 * done)
    big = im.resize((im.width * S, im.height * S), Image.NEAREST)
    img.paste(big, (x0, y0), big)
    d = ImageDraw.Draw(img)
    for x, y, col, ta, sx, sy, gc in data:
        px, py = x0 + x * S, y0 + y * S
        if lt < ta:                                            # 还缺着的格子
            d.rectangle([px, py, px + S - 1, py + S - 1], fill=(26, 22, 54))
            d.point((px + 2, py + 2), fill=(70, 64, 120))
            f = (lt - (ta - 0.8)) / 0.8
            if 0 <= f < 1:                                     # 正飞过来的小方块
                e = eout(f)
                fx, fy = lerp(sx, px, e), lerp(sy, py, e) + math.sin(f * 7 + x) * 8 * (1 - e)
                d.point((lerp(sx, px, max(0, e - 0.08)) + 2, lerp(sy, py, max(0, e - 0.08)) + 2), fill=lerpc(gc, (30, 26, 60), 0.5))
                d.rectangle([fx, fy, fx + S - 1, fy + S - 1], fill=gc)
        elif lt < ta + 0.3:
            d.rectangle([px, py, px + S - 1, py + S - 1], fill=lerpc((255, 255, 255), col, (lt - ta) / 0.3))
    # 胸口一颗小小的心，八块里亮着七块
    motifs.heart_pie(img, 240, y0 + 30 * S, 0.7, [1] * 7 + [0], empty_a=1.0)


# ---------------------------------------------------------------- 17 也是因为你
def s_because(img, d, lt, dur, T, amp):
    pix.sky(img, ((0, (250, 180, 190)), (0.6, (255, 214, 190)), (1, (255, 236, 210))))
    props.bokeh(img, T, 12, ((255, 240, 220), (255, 200, 210)), seed=6, a=0.35)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 214, W, H], fill=(246, 196, 170))
    person_s(img, 'boy', 160, 236, 3, view='front', expr='happy')
    person_s(img, 'girl', 320, 236, 3, view='front', arms='flowers', expr='happy')
    for i in range(30):                                        # 她手心里吹出来的光点，飞向他
        k = (lt * 0.8 + i / 30) % 1
        x = lerp(316, 168, k); y = lerp(186, 170, k) - 34 * math.sin(math.pi * k) + 6 * math.sin(i * 2.3 + lt * 3)
        c = (GOLD_L, PINK, (255, 236, 160))[i % 3]
        d.rectangle([x, y, x + 1, y + 1], fill=c)
    glow(img, 160, 172, 22, (255, 220, 160), 0.5 + 0.2 * props.thump(T))
    pix.put(img, 'heart', 240, 112 - 4 * math.sin(T * 3), 2, alpha=span(lt, 0.8, 1.2))
    motifs.heart_pie(img, 240, 52, 1.4, [1] * 7 + [0], pop=[0] * 7 + [0])


# ---------------------------------------------------------------- 18 某一天你离开了我的生命
def s_leave(img, d, lt, dur, T, amp):
    door = ease(span(lt, 1.2, 1.8)) * (1 - ease(span(lt, 4.6, 5.4)))
    bloom = 1 - ease(span(lt, 2.6, 5.0))
    dx0, dy0, dx1, dy1 = motifs.room(img, d, T, door=door, plant_bloom=bloom)
    base = 196
    if lt > 3.0:
        for i in range(6):                                     # 花瓣落下来
            r = rng(i)
            k = span(lt, 3 + i * 0.25, 4.4 + i * 0.25)
            if 0 < k < 1: d.point((360 + r.uniform(-14, 14), lerp(166, 194, k)), fill=(255, 150, 170))
    person_s(img, 'boy', 290, base, 2, view='side', expr='sad', flip=True)
    if lt < 1.4:
        person_s(img, 'girl', 130, base, 2, view='side', arms='wave', ph=int(T * 5), expr='smile')
    elif lt < 2.6:
        x = lerp(130, 80, span(lt, 1.4, 2.6))
        person_s(img, 'girl', x, base, 2, view='side', pose='walk', ph=pix.wph(lt, 7), expr='smile', flip=True)
    else:
        props.ghost(img, 'girl', 80, base, 2, 1 - span(lt, 2.6, 3.3), view='back')
    color = np.asarray(img)
    r = 620 * ease(span(lt, 2.7, 5.2))
    m = ((XX - 78) ** 2 + (YY - 140) ** 2) < (r * (1 - 0.18 * pix.BAYER)) ** 2
    g = motifs.gray(color, 1) * 0.82
    img.paste(Image.fromarray(np.where(m[..., None], g, color).astype(np.uint8)))
    k = span(lt, 4.8, 5.6)
    if k > 0:                                                  # 只剩他胸口一小块还亮着
        glow(img, 290, 166, 12, (255, 210, 120), 0.6 * k)
        motifs.fly_piece(img, 0, 0.7, 290, 168, k, glow_a=0.3)


# ---------------------------------------------------------------- 19 谢谢你曾经是我的几分之几
def _sepia_heart(img, d, t, T):
    pix.sky(img, NIGHT_SKY)
    pix.stars(d, T, H, 1.0, 200)
    cx, cy, s = HC
    cy = cy + 3 * math.sin(T * 1.5)
    t_start = T - t
    turns = [b - t_start for b in props.beats_in(t_start + 0.4, t_start + 5.6)][:7]
    while len(turns) < 7: turns.append(turns[-1] + 0.8 if turns else 0.5)
    sep = [ease(span(t, tt, tt + 0.6)) for tt in turns] + [0]
    glow(img, cx, cy, 100, (255, 200, 150), 0.25)
    cents = motifs.pie_centers(cx, cy, s)
    motifs.heart_pie(img, cx, cy, s, [1] * 7 + [0], photos=photos(), sepia=sep)
    for k, tt in enumerate(turns):                             # 变旧的那一块飘出几颗金色的火星
        for q in range(5):
            u = t - tt - q * 0.12
            if 0 < u < 1.6:
                x = cents[k][0] + math.sin(q * 2 + k) * 10 + u * 6; y = cents[k][1] - u * 30
                d.point((x, y), fill=lerpc((255, 220, 140), (60, 40, 70), u / 1.6))
    motifs.fraction(img, 384, cy, 7, 8, 3, top=(255, 240, 210), bot=(220, 170, 110), line=(150, 100, 70))


def _fall_home(img, d, t, T):
    motifs.sun_plain(img, d, T, sky=NIGHT_SKY, sx=240, sy=300, sr=40, hz=176, dip=0, plain=PLAIN_NIGHT, road=True, shimmer=False,
                     sun_a=0, birds=False)
    pix.stars(d, T, 170, 1.0, 200)
    pix.moon(d, 400, 40, 10)
    f = ease(span(t, 0.4, 3.6))
    x, y = lerp(240, 240, f), lerp(60, 182, f)
    s = lerp(1.6, 0.3, f)
    if f < 1:
        glow(img, x, y, 30 * s + 6, (255, 200, 140), 0.4)
        motifs.heart_pie(img, x, y, s, [1] * 7 + [0], photos=photos() if s > 0.8 else None, sepia=[1] * 8,
                         cols=[(220, 180, 120)] * 8)
    person_s(img, 'boy', 240, 214, 2, view='back', shade=(0.7, 0.7, 0.9))
    k = span(t, 3.4, 4.4)
    if k > 0: glow(img, 240, 184, 16 + 6 * math.sin(T * 2), (255, 210, 140), 0.55 * k)


def s_once(img, d, lt, dur, T, amp):
    shots(img, lt, [(0, _sepia_heart), (5.6, _fall_home)], 0.5, T=T)


# ---------------------------------------------------------------- 20 感觉你贴着我胸口呼吸
def s_breath(img, d, lt, dur, T, amp):
    pix.sky(img, ((0, (26, 30, 66)), (1, (40, 40, 80))), 0, 204)
    wx0, wy0, wx1, wy1 = 40, 24, 196, 150
    d.rectangle([wx0 - 5, wy0 - 5, wx1 + 5, wy1 + 5], fill=(60, 60, 96))
    win = pix.vgrad(wx1 - wx0, wy1 - wy0, ((0, (14, 16, 50)), (1, (50, 50, 110))), 5).copy()
    wd = ImageDraw.Draw(win)
    pix.moon(wd, 110, 40, 16)
    for k in range(30): wd.point(((k * 53) % 156, (k * 31) % 120), fill=(255, 250, 230))
    img.paste(win, (wx0, wy0))
    glow(img, 150, 64, 40, (255, 250, 220), 0.3)
    d.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=(60, 60, 96), width=3)
    d.line([(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], fill=(60, 60, 96), width=3)
    sw = math.sin(T * 0.9) * 3
    d.polygon([(wx1 + 4, wy0 - 10), (wx1 + 24, wy0 - 10), (wx1 + 18 + sw, wy1 + 30), (wx1 + 4, wy1 + 30)], fill=(90, 80, 130))
    pix.sky(img, ((0, (50, 40, 60)), (1, (30, 26, 44))), 204, H)
    tfill(img, 'polygon', [(wx0, wy1), (wx1, wy1), (420, H), (230, H)], (190, 210, 255), 0.14)
    tfill(img, 'polygon', [(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)], (190, 210, 255), 0.05)
    d.rectangle([300, 150, W, 214], fill=(70, 60, 100)); d.rectangle([300, 140, W, 160], fill=(150, 150, 200))
    r = rng(2)
    for i in range(30):                                        # 月光里的灰尘
        x = 80 + (r.uniform(0, 200) + T * 3) % 200; y = 150 + (r.uniform(0, 110) - T * 2) % 110
        if math.sin(T * 2 + i) > 0.2: d.point((x, y), fill=(220, 230, 255))
    breath = 0.5 - 0.5 * math.cos(2 * math.pi * lt / 3.2)
    sh = (0.62, 0.66, 0.92)
    person_s(img, 'boy', 320, 236 - round(breath), 3, view='front', pose='sit', expr='closed', shade=sh)
    # 她的影子：回忆里的人，暖金色，半透明，侧身靠在他胸口
    im = pix.char_img('girl', 'young', 'side', 'sit', 0, 'closed').transpose(Image.FLIP_LEFT_RIGHT)
    arr = np.array(im).astype(float)
    arr[..., :3] = arr[..., :3] * 0.55 + np.array((255, 214, 150)) * 0.45
    im = pix.outline(Image.fromarray(arr.astype(np.uint8)), (255, 236, 180)).rotate(14, Image.NEAREST, expand=True)
    im = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
    a = (0.62 + 0.25 * breath) * span(lt, 0.2, 1.4)
    glow(img, 352, 190, 40, (255, 210, 150), 0.25 * a)
    dpaste(img, im, 352 - im.width / 2 + 6, 236 - im.height + 22 + round(breath), a)
    glow(img, 326, 184, 16 + 12 * breath, (255, 200, 140), 0.3 + 0.35 * breath)
