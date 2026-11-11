"""几分之几 · 这首歌自己的道具。

- 压着平原的大太阳：地平线在太阳底下被压得往下凹一点，近处是金色的麦田和一条土路
- 八块拼成的心：像切饼一样分成八块，一块一块填进颜色或回忆的照片，旁边用分数记着"几分之几"
- 白球鞋：字幕下面走路的小鞋，和特写里的大鞋
- 她金色的侧脸：多边形画的侧脸特写，迎着太阳的一边镶一道金边
- 指南针、单车、棕榈树、海、房间、长椅、四季的树、雨伞、银河、对话气泡、捧着的手、黑白和彩色之间的转换
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
from pix import (W, H, FONT, FONT_S, OUT, SKIN, SKIN_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill,
                 blend_box, paste, outline, rng, heart_poly)
from props import dpaste, CREAM, GOLD, GOLD_L, PINK, PINK_L

SNAP = None        # render.py 填入：SNAP(T) 返回全片 T 秒处的画面（不含字幕）
LYRIC_T = []       # render.py 填入：每句唱词开始的时间

SUN_HI, SUN_MID, SUN_LO = (255, 246, 196), (255, 200, 104), (250, 128, 76)
PIECE = [(255, 204, 92), (255, 150, 140), (130, 204, 236), (170, 222, 140), (250, 170, 210), (196, 170, 246), (255, 232, 160),
         (255, 176, 100)]
NIGHT_SKY = ((0, (10, 10, 34)), (0.55, (28, 26, 74)), (1, (70, 52, 110)))
GOLD_SKY = ((0, (96, 110, 186)), (0.38, (228, 150, 150)), (0.72, (255, 196, 128)), (1, (255, 236, 176)))
DUSK_SKY = ((0, (40, 40, 100)), (0.45, (150, 96, 150)), (0.8, (246, 150, 120)), (1, (255, 206, 150)))
DAWN_SKY = ((0, (54, 70, 140)), (0.45, (170, 140, 190)), (0.78, (255, 186, 160)), (1, (255, 230, 180)))
NOON_SKY = ((0, (70, 150, 236)), (0.6, (130, 200, 250)), (1, (220, 244, 255)))


def charmap(rows, pal):
    h = len(rows); w = max(len(r) for r in rows)
    im = Image.new('RGBA', (w, h)); px = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.': px[x, y] = pal[ch] + (255,)
    return im


# ---------------------------------------------------------------- 白球鞋
SHOE_PAL = {'K': OUT, 'W': (252, 252, 255), 'S': (214, 216, 230), 'L': (170, 172, 190), 'G': (230, 226, 216), 'w': (246, 246, 250),
            's': SKIN, 'r': (255, 140, 120)}
MINI_SHOE = ["..KK...", ".KWLK..", "KWWWWKK", "KWWWWWK", "KGGGGGK", ".KKKKK."]
BIG_SHOE = ["...KKKK.............",
            "...KssK.............",
            "...KwwK.............",
            "..KKwwKK............",
            "..KWWWWWK...........",
            ".KWWWWWWWKK.........",
            ".KWWWWLWLWWKK.......",
            ".KWWWWWLWLWWWKK.....",
            ".KWWWWWWWWWWWWWKK...",
            "KWWWWWWWWWWWWWWWWK..",
            "KSWWWWWWWWWWWWWWWSK.",
            "KGGGGGGGGGGGGGGGGGGK",
            ".KKKKKKKKKKKKKKKKKK."]


@lru_cache(None)
def _mini_shoe():
    return charmap(MINI_SHOE, SHOE_PAL)


def mini_shoe(img, x, y, a=1.0):
    """字幕下面的小白鞋，(x, y) 是鞋底中点"""
    im = _mini_shoe()
    dpaste(img, im, x - im.width / 2, y - im.height + 1, a)


@lru_cache(None)
def big_shoe_img(s=4, flip=False):
    im = charmap(BIG_SHOE, SHOE_PAL)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im.resize((im.width * s, im.height * s), Image.NEAREST)


def big_shoe(img, d, x, y, s=4, flip=False, leg=60):
    """特写的白球鞋：(x, y) 是鞋跟底部；上面接一截小腿"""
    im = big_shoe_img(s, flip)
    lx = x + (4 * s if not flip else im.width - 7 * s)
    d.rectangle([lx - s, y - im.height - leg, lx + 3 * s, y - im.height + 2 * s], fill=OUT)
    d.rectangle([lx, y - im.height - leg, lx + 2 * s, y - im.height + 2 * s], fill=SKIN)
    d.rectangle([lx + 2 * s - max(1, s // 2), y - im.height - leg, lx + 2 * s, y - im.height + 2 * s], fill=SKIN_S)
    img.paste(im, (int(x), int(y - im.height)), im)


# ---------------------------------------------------------------- 太阳和平原
@lru_cache(None)
def sun_img(r, hi=SUN_HI, mid=SUN_MID, lo=SUN_LO, bands=0):
    """点阵渐变的太阳；bands>0 时下半部挖出几道横缝"""
    g = pix.vgrad(2 * r + 1, 2 * r + 1, ((0, hi), (0.55, mid), (1, lo)), 6)
    a = np.zeros((2 * r + 1, 2 * r + 1), np.uint8)
    yy, xx = np.mgrid[0:2 * r + 1, 0:2 * r + 1]
    inside = (xx - r) ** 2 + (yy - r) ** 2 <= r * r
    if bands:
        for k in range(bands):
            yb = int(r + r * (0.35 + 0.16 * k)); hb = 1 + k
            inside[yb:yb + hb] = False
    a[inside] = 255
    im = g.convert('RGBA'); im.putalpha(Image.fromarray(a))
    return im


def horizon_fn(hz, sx, sr, dip):
    """地平线：太阳压着的地方往下凹"""
    return lambda x: hz + dip * math.exp(-((x - sx) / (sr * 1.15)) ** 2)


@lru_cache(None)
def _plain_layer(hz, sx, sr, dip, cols, road):
    """平原那一层（RGBA）：地平线以下的点阵渐变，田垄的透视线和土路"""
    hf = horizon_fn(hz, sx, sr, dip)
    top = int(hz)
    g = np.asarray(pix.vgrad(W, H - top, tuple((p, c) for p, c in cols), 6)).copy()
    alpha = np.zeros((H - top, W), np.uint8)
    for x in range(W):
        y0 = int(round(hf(x))) - top
        alpha[max(0, y0):, x] = 255
    im = Image.fromarray(g).convert('RGBA'); im.putalpha(Image.fromarray(alpha))
    d = ImageDraw.Draw(im)
    vx, vy = sx, hz - top
    row = lerpc(cols[-1][1], (90, 50, 30), 0.25)
    for k in range(-14, 15):
        bx = vx + k * 46
        for t in np.linspace(0.04, 1, 60):
            px = lerp(vx, bx, t ** 1.0); py = lerp(vy, H - top, t)
            if 0 <= px < W and alpha[min(H - top - 1, int(py)), int(px)] and (int(py) + k) % 2 == 0:
                d.point((px, py), fill=lerpc(row, cols[0][1], 0.6 * (1 - t)) + (255,))
    if road:
        rc, rc2 = lerpc(cols[1][1], (255, 250, 230), 0.4), lerpc(cols[1][1], (255, 250, 230), 0.2)
        poly = [(vx - 1, vy + 1), (vx + 1, vy + 1), (vx + 60, H - top), (vx - 60, H - top)]
        d.polygon(poly, fill=rc + (255,))
        for k in range(12):
            t = (k / 12) ** 1.6
            y = lerp(vy + 2, H - top, t)
            hw = lerp(1, 60, t)
            d.line([(vx - hw * 0.3, y), (vx - hw * 0.1, y)], fill=rc2 + (255,))
    return im


PLAIN_GOLD = ((0, (255, 226, 150)), (0.25, (238, 186, 96)), (0.6, (208, 146, 66)), (1, (150, 96, 46)))
PLAIN_DAWN = ((0, (236, 200, 170)), (0.25, (196, 156, 120)), (0.6, (150, 116, 90)), (1, (96, 74, 64)))
PLAIN_NIGHT = ((0, (90, 70, 110)), (0.3, (60, 48, 84)), (1, (26, 22, 44)))


def sun_plain(img, d, T, sky=GOLD_SKY, sx=300, sy=150, sr=64, hz=176, dip=7, plain=PLAIN_GOLD, road=True, shimmer=True, sun_a=1.0,
              bands=0, grass_on=True, glow_a=0.55, birds=True, sun_cols=None):
    """全片的母题：压着平原的大太阳。返回地平线函数"""
    pix.sky(img, sky)
    if sun_a > 0:
        glow(img, sx, sy, sr * 2.6, SUN_MID, glow_a * sun_a, power=1.4)
        glow(img, sx, sy, sr * 1.5, SUN_HI, 0.35 * sun_a, power=1.2)
        si = sun_img(int(sr), *(sun_cols or (SUN_HI, SUN_MID, SUN_LO)), bands)
        dpaste(img, si, sx - sr, sy - sr, sun_a)
    lay = _plain_layer(int(hz), int(sx), int(sr), int(dip), tuple(plain), road)
    img.paste(lay, (0, int(hz)), lay)
    hf = horizon_fn(hz, sx, sr, dip)
    if sun_a > 0:
        # 太阳在平原上的反光
        glow(img, sx, hz + dip + 6, sr * 1.3, SUN_HI, 0.35 * sun_a, ry=10, power=1.2)
        d.line([(x, hf(x)) for x in range(int(sx - sr * 1.6), int(sx + sr * 1.6))], fill=lerpc(SUN_HI, (255, 255, 255), 0.4))
    if shimmer:
        a = np.asarray(img).copy()
        for y in range(int(hz - 6), int(hz + dip + 6)):
            sh = round(math.sin(T * 5 + y * 1.3) * 0.9)
            if sh: a[y] = np.roll(a[y], sh, axis=0)
        img.paste(Image.fromarray(a))
    if birds:
        for i in range(4):
            bx = (60 + i * 26 + T * 14) % (W + 40) - 20; by = 70 + 10 * math.sin(i * 2.1) + 3 * math.sin(T + i)
            pix.bird(d, bx, by, T, (70, 50, 70), i)
    if grass_on:
        gc = lerpc(plain[-1][1], (60, 40, 20), 0.2); gc2 = lerpc(plain[-2][1], (255, 230, 150), 0.25)
        pix.grass(d, H - 1, gc, gc2, T, step=2, seed=3, hmax=9)
        pix.grass(d, H - 14, lerpc(gc, gc2, 0.3), gc2, T + 1, step=3, seed=5, hmax=6)
    return hf


def wheat(d, x, y, h, T, col=(250, 214, 120), stem=(200, 150, 70), wind=1.0, ph=0):
    sw = math.sin(T * 2.2 + ph + x * 0.05) * 2 * wind + wind * 1.5
    tx, ty = x + sw, y - h
    d.line([(x, y), (tx, ty)], fill=stem)
    for k in range(4):
        d.point([(tx - 1 + k * sw * 0.1, ty - k), (tx + 1 + k * sw * 0.1, ty - k)], fill=col)
    d.point((tx, ty - 4), fill=col)


def seeds(img, d, T, n=24, box=(0, 0, W, H), wind=40, seed=0, col=(255, 252, 240), rise=-6):
    """蒲公英的绒毛：一个小点带一圈细毛，随风往右飘"""
    x0, y0, x1, y1 = box
    for i in range(n):
        r = rng(i * 23 + seed)
        sp = r.uniform(0.6, 1.4)
        x = x0 + (r.uniform(0, x1 - x0) + T * wind * sp) % (x1 - x0)
        y = y0 + (r.uniform(0, y1 - y0) + T * rise * sp + 6 * math.sin(T * 1.3 + i)) % (y1 - y0)
        d.point((x, y), fill=col)
        if i % 3 == 0:
            d.point([(x - 1, y - 1), (x + 1, y - 1), (x, y - 2)], fill=lerpc(col, (200, 190, 170), 0.3))


def dandelion(d, x, y, h, T, n_left=1.0, col=(255, 252, 240)):
    d.line([(x, y), (x + math.sin(T) * 0.6, y - h)], fill=(110, 150, 80))
    if n_left > 0:
        r = 3
        for k in range(int(10 * n_left)):
            a = k * 0.63
            d.point((x + math.cos(a) * r, y - h + math.sin(a) * r), fill=col)
        d.point((x, y - h), fill=(200, 190, 150))


# ---------------------------------------------------------------- 八块拼成的心
@lru_cache(None)
def _pie(s, n=8):
    w = int(34 * s) + 6; h = int(32 * s) + 6
    ox, oy = w / 2, 13 * s + 3
    m = Image.new('L', (w, h)); md = ImageDraw.Draw(m)
    md.polygon(heart_poly(ox, oy, s), fill=255)
    heart = np.array(m) > 0
    yy, xx = np.mgrid[0:h, 0:w]
    cy = oy + 2.5 * s
    ang = (np.arctan2(xx - ox, -(yy - cy)) / (2 * np.pi)) % 1
    idx = np.floor(ang * n).astype(int) % n
    edge = np.zeros_like(heart)
    edge[:, 1:] |= idx[:, 1:] != idx[:, :-1]
    edge[1:] |= idx[1:] != idx[:-1]
    edge &= heart
    ring = np.zeros_like(heart)
    ring[1:] |= heart[:-1]; ring[:-1] |= heart[1:]; ring[:, 1:] |= heart[:, :-1]; ring[:, :-1] |= heart[:, 1:]
    ring &= ~heart
    shade = np.clip((yy - (oy - 12 * s)) / (30 * s), 0, 1)
    cents = []
    for k in range(n):
        ys, xs = np.nonzero(heart & (idx == k))
        cents.append((xs.mean() if len(xs) else ox, ys.mean() if len(ys) else oy))
    return heart, idx, edge, ring, shade, (ox, oy), w, h, cents


def pie_centers(cx, cy, s, n=8):
    heart, idx, edge, ring, shade, (ox, oy), w, h, cents = _pie(round(s, 2), n)
    return [(cx - ox + x, cy - oy + y) for x, y in cents]


def heart_pie(img, cx, cy, s, fill, cols=PIECE, photos=None, empty=(36, 30, 56), line=(255, 244, 222), out=OUT, pop=None, sepia=None,
              n=8, empty_a=0.8, alpha=1.0):
    """八块拼成的心。fill[k]=0..1：第 k 块填进颜色（或照片），中间值用点阵慢慢出现；pop[k] 让这一块闪白；
    sepia[k] 让这一块褪成旧照片的颜色。(cx, cy) 是心的中心"""
    heart, idx, edge, ring, shade, (ox, oy), w, h, cents = _pie(round(s, 2), n)
    x0, y0 = int(round(cx - ox)), int(round(cy - oy))
    rgb = np.zeros((h, w, 3), float); a = np.zeros((h, w), bool)
    B = pix.bayer(h, w, x0, y0)
    for k in range(n):
        mk = heart & (idx == k)
        f = fill[k] if k < len(fill) else 0
        e = mk & (B < empty_a)
        rgb[e] = empty; a[e] = True
        dots = mk & ((np.indices((h, w)).sum(0) % 4) == 0) & ((np.indices((h, w))[0] % 2) == 0)
        rgb[dots] = lerpc(empty, line, 0.25); a[dots] = True
        if f > 0:
            on = mk & (B < f)
            if photos is not None and k < len(photos) and photos[k] is not None:
                ph = np.asarray(photos[k].resize((w, h), Image.NEAREST), float)
                rgb[on] = ph[on]
            else:
                c = np.array(cols[k % len(cols)], float)
                lo_ = c * 0.78 + np.array((30, 0, 30)) * 0.22
                sh = shade[on][:, None]
                rgb[on] = c * (1 - sh * 0.6) + lo_ * sh * 0.6
                hl = on & (shade < 0.18)
                rgb[hl] = np.minimum(255, c + 40)
            a[on] = True
            if sepia is not None and k < len(sepia) and sepia[k] > 0:
                sk = sepia[k]
                g = rgb[on] @ np.array([0.3, 0.59, 0.11])
                sp = np.stack([g * 1.08 + 18, g * 0.94 + 10, g * 0.72], -1)
                rgb[on] = rgb[on] * (1 - sk) + sp * sk
            if pop is not None and k < len(pop) and pop[k] > 0:
                rgb[on] = rgb[on] * (1 - pop[k]) + 255 * pop[k]
    rgb[edge] = line; a[edge] = True
    rgb[ring] = out; a[ring] = True
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert('RGBA')
    al = a
    if alpha < 1: al = al & (B < alpha)
    im.putalpha(Image.fromarray((al * 255).astype(np.uint8)))
    img.paste(im, (x0, y0), im)
    return [(x0 + x, y0 + y) for x, y in cents]


@lru_cache(None)
def piece_img(k, s, col=None, n=8, glowing=False):
    """单独的一块（第 k 块），返回 (RGBA, 这块在心里的中心相对图左上角的偏移)"""
    heart, idx, edge, ring, shade, (ox, oy), w, h, cents = _pie(round(s, 2), n)
    mk = heart & (idx == k)
    ys, xs = np.nonzero(mk)
    bx0, by0, bx1, by1 = xs.min() - 1, ys.min() - 1, xs.max() + 2, ys.max() + 2
    c = np.array(col or PIECE[k % len(PIECE)], float)
    rgb = np.zeros((h, w, 3)); rgb[mk] = c
    rgb[mk & (shade < 0.25)] = np.minimum(255, c + 50)
    im = Image.fromarray(rgb.astype(np.uint8)).convert('RGBA'); im.putalpha(Image.fromarray((mk * 255).astype(np.uint8)))
    im = outline(im.crop((bx0, by0, bx1, by1)), OUT if not glowing else (255, 250, 220))
    return im, (cents[k][0] - bx0, cents[k][1] - by0)


def fly_piece(img, k, s, x, y, a=1.0, col=None, glow_a=0.4, glowing=False):
    """画一块飞着的拼图块，(x, y) 是它的中心"""
    im, (cx, cy) = piece_img(k, round(s, 2), col, 8, glowing)
    if glow_a > 0: glow(img, x, y, 10 + 8 * s, col or PIECE[k % len(PIECE)], glow_a * a)
    dpaste(img, im, x - cx, y - cy, a)


def fraction(img, cx, cy, num, den, scale=2, alpha=1.0, top=(255, 252, 240), bot=(255, 206, 120), line=(196, 110, 70),
             out=(46, 26, 40), bar=None, gap=None):
    """竖着写的分数：上面 num，中间一道横线，下面 den"""
    gap = gap if gap is not None else 9 * scale
    kw = dict(top=top, bot=bot, line=line, out=out)
    props.big_text(img, str(num), cx, cy - gap, scale, alpha, **kw)
    props.big_text(img, str(den), cx, cy + gap + scale, scale, alpha, **kw)
    wbar = max(len(str(num)), len(str(den))) * 9 * scale + 6 * scale
    x0, x1 = int(cx - wbar / 2), int(cx + wbar / 2)
    y = int(cy)
    if alpha >= 1:
        ImageDraw.Draw(img).rectangle([x0 - 1, y - 1, x1 + 1, y + scale], fill=out)
        ImageDraw.Draw(img).rectangle([x0, y, x1, y + scale - 1], fill=bar or top)
    else:
        blend_box(img, (x0, y, x1, y + scale), bar or top, np.full((scale, x1 - x0), alpha))


# ---------------------------------------------------------------- 她金色的侧脸（朝右，迎着太阳）
PROF_SKIN = [(62, 14), (74, 24), (80, 38), (82, 50), (80, 56), (83, 62), (92, 74), (90, 77), (84, 79), (85, 84), (87, 87), (84, 89),
             (86, 92), (82, 96), (84, 101), (80, 106), (72, 110), (73, 146), (44, 146), (48, 104), (40, 80), (38, 50), (46, 24)]
PROF_HAIR = [(82, 40), (86, 26), (78, 10), (62, 3), (44, 5), (30, 16), (22, 38), (20, 72), (16, 110), (20, 150), (48, 150), (50, 124),
             (52, 100), (55, 74), (60, 50), (70, 40), (76, 44)]
PROF_DRESS = [(26, 146), (90, 146), (112, 172), (6, 172)]


@lru_cache(None)
def _profile(s, rim_a):
    w, h = int(120 * s), int(172 * s)
    im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im)
    S = lambda pts: [(x * s, y * s) for x, y in pts]
    gold_skin, shade_skin = (255, 214, 158), (226, 160, 118)
    hair, hair_s, hair_l = (74, 46, 42), (50, 30, 30), (150, 96, 66)
    d.polygon(S(PROF_DRESS), fill=pix.MUST)
    d.polygon(S([(26, 146), (90, 146), (96, 152), (20, 152)]), fill=(255, 250, 240))
    d.polygon(S(PROF_SKIN), fill=gold_skin)
    d.polygon(S([(73, 112), (73, 146), (44, 146), (48, 104), (60, 108)]), fill=shade_skin)
    d.polygon(S(PROF_HAIR), fill=hair)
    for k in range(6):                                          # 发丝的暗线
        x0 = 26 + k * 5
        d.line(S([(x0 + 6, 12 + k * 2), (x0 - 2, 60), (x0 - 4, 120 + k * 4)]), fill=hair_s)
    d.line(S([(64, 6), (80, 14), (84, 26)]), fill=hair_l, width=max(1, int(2 * s)))
    # 耳朵和发卡
    d.ellipse(S([(54, 64), (62, 80)]), fill=gold_skin); d.arc(S([(55, 66), (61, 78)]), 90, 270, fill=shade_skin)
    d.rectangle(S([(56, 52), (66, 56)]), fill=(255, 120, 110)); d.rectangle(S([(57, 53), (60, 55)]), fill=(255, 190, 180))
    # 眉毛、睫毛、腮红、嘴唇
    d.line(S([(70, 51), (79, 50)]), fill=hair_s, width=max(1, int(s * 1.5)))
    d.line(S([(72, 61), (80, 62)]), fill=(52, 34, 40), width=max(1, int(s * 1.5)))
    d.line(S([(80, 62), (82, 59)]), fill=(52, 34, 40))
    d.ellipse(S([(70, 74), (80, 80)]), fill=(255, 168, 140))
    d.polygon(S([(85, 84), (87, 87), (84, 89), (86, 92), (83, 92), (82, 86)]), fill=(232, 110, 104))
    a = np.array(im)
    m = a[..., 3] > 0
    # 金边：迎着太阳（右边、上边）的轮廓
    rim = m & ~np.roll(m, -1, 1) | m & ~np.roll(m, -2, 1) & (rim_a > 0.5)
    top = m & ~np.roll(m, 1, 0)
    for mm, col in ((rim, (255, 244, 190)), (top & ~rim, (255, 220, 140))):
        a[mm, :3] = (a[mm, :3] * (1 - rim_a) + np.array(col) * rim_a).astype(np.uint8)
    im = outline(Image.fromarray(a), (60, 34, 40))
    return im


def profile(img, d, x, y, s=1.0, T=0.0, rim_a=1.0, wind=1.0):
    """她的侧脸特写：(x, y) 是画像左上角。飘起来的发丝随风动"""
    im = _profile(round(s, 2), round(rim_a, 1))
    img.paste(im, (int(x), int(y)), im)
    for k in range(7):
        r = rng(k * 7)
        bx, by = x + (24 + r.uniform(-4, 8)) * s, y + (20 + k * 14) * s
        ln = (14 + r.uniform(0, 14)) * s * wind
        pts = []
        for j in range(10):
            u = j / 9
            pts.append((bx - u * ln, by + u * 6 * s + math.sin(T * 3 + k + u * 3) * 3 * s * u))
        d.line(pts, fill=(255, 210, 130) if k % 2 else (120, 76, 56))


# ---------------------------------------------------------------- 指南针
def compass(img, d, cx, cy, r, ang, T, glow_a=0.0):
    """ang 是指针方向（弧度，0 朝上，顺时针为正）"""
    if glow_a > 0: glow(img, cx, cy, r * 2, GOLD_L, glow_a)
    d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill=OUT)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(214, 164, 80))
    d.ellipse([cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3], fill=(150, 104, 50))
    d.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5], fill=(250, 240, 214))
    for k in range(16):
        a = k * math.pi / 8
        r0 = r - (11 if k % 4 == 0 else 8)
        d.line([(cx + math.sin(a) * r0, cy - math.cos(a) * r0), (cx + math.sin(a) * (r - 6), cy - math.cos(a) * (r - 6))],
               fill=(120, 90, 70))
    d.rectangle([cx - r - 3, cy - 2, cx - r + 1, cy + 2], fill=(214, 164, 80))
    d.ellipse([cx - 4, cy - r - 9, cx + 4, cy - r - 1], outline=(214, 164, 80), width=2)
    ca, sa = math.cos(ang), math.sin(ang)

    def R(px, py): return (cx + px * ca - py * sa, cy + px * sa + py * ca)
    L = r - 9
    d.polygon([R(0, -L), R(4, 0), R(-4, 0)], fill=(230, 64, 70))
    d.polygon([R(0, L), R(4, 0), R(-4, 0)], fill=(236, 236, 240))
    d.line([R(0, -L), R(0, L)], fill=OUT)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(214, 164, 80))
    d.arc([cx - r + 7, cy - r + 7, cx + r - 7, cy + r - 7], 200, 250, fill=(255, 255, 255))


def finger(d, x, y, w, h, flip=False):
    d.rounded_rectangle([x - 1, y - 1, x + w + 1, y + h + 1], max(1, w // 2), fill=OUT)
    d.rounded_rectangle([x, y, x + w, y + h], max(1, w // 2), fill=SKIN)
    d.line([(x + (1 if not flip else w - 1), y + 2), (x + (1 if not flip else w - 1), y + h - 2)], fill=SKIN_S)


# ---------------------------------------------------------------- 单车、棕榈树、海
def bicycle(d, x, y, T, s=1, roll=None, col=(232, 84, 84)):
    """侧面的单车，(x, y) 是两轮中间的地面"""
    roll = T * 8 if roll is None else roll
    S = lambda v: v * s
    rw = S(8)
    for wx in (x - S(14), x + S(14)):
        d.ellipse([wx - rw, y - 2 * rw, wx + rw, y], outline=OUT, width=max(1, int(s)))
        d.ellipse([wx - rw + 1, y - 2 * rw + 1, wx + rw - 1, y - 1], outline=(70, 70, 84))
        for k in range(3):
            a = roll + k * math.pi / 3
            d.line([(wx - math.cos(a) * (rw - 1), y - rw - math.sin(a) * (rw - 1)), (wx + math.cos(a) * (rw - 1), y - rw + math.sin(a) * (rw - 1))],
                   fill=(170, 170, 184))
    hub_r, hub_f = (x - S(14), y - rw), (x + S(14), y - rw)
    seat, crank, head = (x - S(4), y - S(20)), (x - S(1), y - rw), (x + S(10), y - S(21))
    for a_, b_ in ((hub_r, seat), (hub_r, crank), (seat, crank), (crank, head), (seat, (x + S(9), y - S(18))), (head, hub_f)):
        d.line([a_, b_], fill=col, width=max(1, int(s * 1.5)))
    d.rectangle([x - S(8), y - S(23), x - S(1), y - S(21)], fill=OUT)
    d.line([(x + S(9), y - S(25)), (x + S(13), y - S(24))], fill=OUT, width=max(1, int(s)))
    d.line([(x - S(24), y - S(17)), (x - S(11), y - S(17))], fill=(110, 110, 120), width=max(1, int(s)))      # 后座
    d.line([(x - S(20), y - S(17)), hub_r], fill=(110, 110, 120))
    pa = roll * 0.6
    d.line([(crank[0] + math.cos(pa) * S(4), crank[1] + math.sin(pa) * S(4)), (crank[0] - math.cos(pa) * S(4), crank[1] - math.sin(pa) * S(4))],
           fill=OUT)
    d.ellipse([crank[0] - 2, crank[1] - 2, crank[0] + 2, crank[1] + 2], fill=(90, 90, 100))
    return seat, (x - S(17), y - S(17)), head


def palm(d, x, base, s=1.0, T=0.0, lean=12, trunk=(150, 104, 66), trunk_d=(110, 74, 48), leaf=(60, 150, 90), leaf_d=(40, 110, 70)):
    top = (x + lean * s, base - 56 * s)
    pts = []
    for k in range(15):
        u = k / 14
        pts.append((lerp(x, top[0], u ** 1.6), lerp(base, top[1], u)))
    for k, (px, py) in enumerate(pts[:-1]):
        w_ = max(1, int((3.2 - k * 0.12) * s))
        d.ellipse([px - w_, py - w_, px + w_, py + w_], fill=trunk if k % 2 else trunk_d)
    tx, ty = pts[-1]
    sway = math.sin(T * 1.6 + x * 0.1) * 2 * s
    for k in range(7):
        a = -math.pi * 0.95 + k * math.pi * 0.95 / 6 + (0.1 if k > 3 else -0.1)
        ln = (22 + (k % 3) * 3) * s
        prev = (tx, ty)
        for j in range(1, 9):
            u = j / 8
            px = tx + math.cos(a) * ln * u + sway * u
            py = ty + math.sin(a) * ln * u * 0.7 + (u * u) * 14 * s
            d.line([prev, (px, py)], fill=leaf if k % 2 else leaf_d, width=max(1, int(2 * s)))
            if j % 2 == 0:
                d.line([(px, py), (px + math.cos(a + 1.2) * 3 * s, py + 4 * s)], fill=leaf_d)
                d.line([(px, py), (px + math.cos(a - 1.2) * 3 * s, py + 4 * s)], fill=leaf)
            prev = (px, py)
    d.ellipse([tx - 3 * s, ty - 1 * s, tx + 1 * s, ty + 3 * s], fill=(120, 80, 50))


def sea(img, d, y0, y1, T, cols=((60, 150, 210), (40, 116, 186), (30, 90, 160)), sparkle_col=(255, 255, 240), n=60, speed=10):
    pix.sky(img, tuple((i / (len(cols) - 1), c) for i, c in enumerate(cols)), y0, y1, 4)
    for i in range(n):
        r = rng(i * 13)
        y = y0 + 2 + (y1 - y0 - 3) * r.random() ** 1.4
        x = (r.uniform(0, W) - T * speed * (0.5 + (y - y0) / (y1 - y0))) % W
        ln = 2 + int(4 * (y - y0) / (y1 - y0))
        if math.sin(T * 3 + i) > -0.2:
            d.line([(x, y), (x + ln, y)], fill=sparkle_col if i % 3 == 0 else lerpc(cols[0], (255, 255, 255), 0.4))


# ---------------------------------------------------------------- 房间
def room(img, d, T, door=0.0, night=0.0, plant_bloom=1.0):
    """他的房间：左边一扇门，中间窗户和书桌，右边床和书架。door 0..1 是门开的程度。返回门洞的矩形"""
    dk = lambda c: lerpc(c, (24, 26, 56), 0.55 * night)
    pix.sky(img, ((0, dk((236, 214, 182))), (1, dk((222, 196, 160)))), 0, 196)
    for x in range(8, W, 16):
        d.line([(x, 0), (x, 195)], fill=dk((228, 204, 170)))
        for y in range(10, 190, 24): d.point((x + 8, y), fill=dk((214, 150, 140)))
    d.rectangle([0, 192, W, 197], fill=dk((150, 104, 74)))
    pix.sky(img, ((0, dk((176, 122, 82))), (1, dk((140, 94, 62)))), 197, H)
    for y in range(204, H, 9): d.line([(0, y), (W, y)], fill=dk((128, 86, 58)))
    for k in range(14):
        y = 197 + (k % 7) * 9; x = (k * 71) % W
        d.line([(x, y + 1), (x, y + 8)], fill=dk((128, 86, 58)))
    # 窗
    wx0, wy0, wx1, wy1 = 236, 46, 336, 124
    d.rectangle([wx0 - 4, wy0 - 4, wx1 + 4, wy1 + 4], fill=dk((250, 244, 230)))
    stops = ((0, lerpc((110, 180, 240), (20, 24, 70), round(night * 8) / 8)), (1, lerpc((200, 236, 255), (60, 50, 110), round(night * 8) / 8)))
    win = pix.vgrad(wx1 - wx0 + 1, wy1 - wy0 + 1, stops, 5).copy()
    wd = ImageDraw.Draw(win)
    if night < 0.5:
        pix.cloud(wd, 14 + (T * 3) % 60, 18, 1, (255, 255, 255), (220, 236, 250))
        for k in range(5): wd.rectangle([k * 22, 60, k * 22 + 16, 80], fill=(150, 186, 210))
    else:
        pix.moon(wd, 70, 22, 8)
        for k in range(12): wd.point(((k * 37) % 100, (k * 23) % 50), fill=(255, 250, 220))
    img.paste(win, (wx0, wy0))
    d.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=dk((250, 244, 230)), width=2)
    d.line([(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], fill=dk((250, 244, 230)), width=2)
    sw = math.sin(T * 1.2) * 2
    for cxs, sgn in ((wx0 - 4, -1), (wx1 + 4, 1)):
        d.polygon([(cxs, wy0 - 8), (cxs + sgn * 16, wy0 - 8), (cxs + sgn * (10 + sw), wy1 + 10), (cxs, wy1 + 10)], fill=dk((150, 196, 170)))
        d.line([(cxs + sgn * 6, wy0 - 6), (cxs + sgn * (5 + sw / 2), wy1 + 8)], fill=dk((120, 170, 146)))
    d.rectangle([wx0 - 22, wy0 - 10, wx1 + 22, wy0 - 8], fill=dk((120, 84, 60)))
    # 书桌、台灯、书
    d.rectangle([224, 150, 350, 155], fill=dk((150, 100, 64))); d.rectangle([228, 155, 232, 194], fill=dk((120, 80, 52)))
    d.rectangle([342, 155, 346, 194], fill=dk((120, 80, 52))); d.rectangle([300, 156, 342, 176], fill=dk((140, 94, 60)))
    d.rectangle([318, 164, 324, 166], fill=dk((230, 200, 130)))
    d.line([(244, 150), (244, 132), (254, 124)], fill=dk((90, 90, 110)), width=2)
    d.polygon([(250, 120), (262, 118), (262, 128)], fill=dk((230, 90, 80)))
    for k, c in enumerate(((230, 110, 90), (90, 150, 200), (250, 200, 90), (130, 190, 120))):
        d.rectangle([276 + k * 5, 136 + (k % 2) * 2, 279 + k * 5, 149], fill=dk(c))
    # 书架
    bx = 150
    d.rectangle([bx, 70, bx + 50, 194], fill=dk((140, 94, 60)))
    for k in range(4):
        y = 80 + k * 28
        d.rectangle([bx + 3, y, bx + 47, y + 24], fill=dk((96, 64, 44)))
        r = rng(k)
        x = bx + 4
        while x < bx + 44:
            w_ = r.randint(3, 6)
            c = r.choice(((230, 110, 90), (90, 150, 200), (250, 200, 90), (130, 190, 120), (200, 160, 220), (240, 236, 220)))
            hh = r.randint(14, 22)
            d.rectangle([x, y + 24 - hh, x + w_ - 1, y + 23], fill=dk(c))
            x += w_ + 1
    # 床
    d.rectangle([384, 150, 480, 192], fill=dk((120, 84, 60)))
    d.rectangle([384, 140, 480, 162], fill=dk((246, 242, 236)))
    d.rectangle([420, 136, 480, 168], fill=dk((140, 190, 220)))
    for k in range(5): d.line([(424 + k * 12, 138), (424 + k * 12, 166)], fill=dk((120, 170, 204)))
    d.rounded_rectangle([390, 130, 414, 144], 4, fill=dk((255, 252, 246)))
    d.rectangle([380, 110, 386, 192], fill=dk((120, 84, 60)))
    # 植物和挂钟
    px_ = 360
    d.polygon([(px_ - 8, 176), (px_ + 8, 176), (px_ + 6, 194), (px_ - 6, 194)], fill=dk((214, 120, 80)))
    for k in range(5):
        a = -math.pi / 2 + (k - 2) * 0.45 + math.sin(T + k) * 0.05
        d.line([(px_, 176), (px_ + math.cos(a) * 18, 176 + math.sin(a) * 18)], fill=dk((70, 150, 80)), width=2)
        if plant_bloom > 0 and k % 2 == 0:
            fx, fy = px_ + math.cos(a) * 19, 176 + math.sin(a) * 19
            r_ = 2 * plant_bloom
            d.ellipse([fx - r_, fy - r_, fx + r_, fy + r_], fill=dk((255, 150, 170)))
    props.clock(d, 196, 36, 12, T * 0.05, T * 0.6, rim=dk((150, 100, 64)))
    d.rectangle([370, 40, 410, 90], fill=dk((250, 244, 230))); d.rectangle([373, 43, 407, 87], fill=dk((255, 200, 120)))
    d.ellipse([382, 52, 398, 68], fill=dk((255, 236, 170))); d.rectangle([373, 72, 407, 87], fill=dk((220, 150, 80)))
    # 门
    dx0, dy0, dx1, dy1 = 50, 84, 106, 194
    d.rectangle([dx0 - 5, dy0 - 5, dx1 + 5, dy1], fill=dk((250, 244, 230)))
    if door > 0:
        d.rectangle([dx0, dy0, dx1, dy1], fill=(255, 250, 226))
        glow(img, (dx0 + dx1) / 2, (dy0 + dy1) / 2, 60, (255, 240, 190), 0.45 * door)
        tfill(img, 'polygon', [(dx0, dy1), (dx1, dy1), (dx1 + 90 * door, H), (dx0 + 10, H)], (255, 244, 200), 0.35 * door)
        pw = (dx1 - dx0) * (1 - door * 0.85)
        d.polygon([(dx0, dy0), (dx0 + pw, dy0 - 6 * door), (dx0 + pw, dy1 + 6 * door), (dx0, dy1)], fill=dk((170, 116, 76)))
        d.line([(dx0 + pw, dy0 - 6 * door), (dx0 + pw, dy1 + 6 * door)], fill=dk((120, 80, 52)))
    else:
        d.rectangle([dx0, dy0, dx1, dy1], fill=dk((170, 116, 76)))
        d.rectangle([dx0 + 6, dy0 + 8, dx1 - 6, dy0 + 48], outline=dk((140, 94, 60)))
        d.rectangle([dx0 + 6, dy0 + 58, dx1 - 6, dy1 - 10], outline=dk((140, 94, 60)))
        d.ellipse([dx1 - 10, dy0 + 54, dx1 - 6, dy0 + 58], fill=dk((230, 196, 110)))
    return (dx0, dy0, dx1, dy1)


# ---------------------------------------------------------------- 黑白和彩色
def gray(arr, k=1.0, tint=(1.0, 1.0, 1.06)):
    a = np.asarray(arr, float)
    g = a @ np.array([0.3, 0.59, 0.11])
    s = np.stack([g * tint[0], g * tint[1], g * tint[2]], -1) * 0.92 + 8
    return np.clip(a * (1 - k) + s * k, 0, 255)


def reveal_mask(points, ox=0, oy=0):
    """点阵边缘的彩色区域：points = [(x, y, r), ...]，在这些圆里面的像素为 True"""
    m = np.zeros((H, W), bool)
    yy, xx = np.mgrid[0:H, 0:W]
    for x, y, r in points:
        if r <= 0: continue
        m |= np.sqrt((xx - x) ** 2 + (yy - y) ** 2) / r < 1 - pix.BAYER * 0.18
    return m


LCD = np.array([(22, 40, 34), (54, 88, 62), (124, 160, 92), (204, 220, 150)], float)


def lcd(arr):
    """四个绿色的掌机屏幕"""
    g = np.asarray(arr, float) @ np.array([0.3, 0.59, 0.11]) / 255
    q = np.clip(np.floor(g * 3.6 + pix.BAYER[:g.shape[0], :g.shape[1]] * 0.6), 0, 3).astype(int)
    return LCD[q]


# ---------------------------------------------------------------- 长椅、四季的树、雨伞
def bench(d, x, base, s=1, col=(170, 116, 72), col_d=(120, 80, 50), iron=(60, 56, 70)):
    S = lambda v: v * s
    d.rectangle([x - S(26), base - S(14), x + S(26), base - S(12)], fill=col)
    d.rectangle([x - S(26), base - S(24), x + S(26), base - S(22)], fill=col)
    d.rectangle([x - S(26), base - S(20), x + S(26), base - S(18)], fill=col_d)
    for lx in (x - S(22), x + S(21)):
        d.rectangle([lx, base - S(24), lx + S(1), base], fill=iron)
    d.rectangle([x - S(26), base - S(12), x + S(26), base - S(11)], fill=col_d)


SEASON = {
    'summer': dict(leaf=(70, 158, 84), leaf_l=(110, 196, 98), ground=(120, 176, 90)),
    'autumn': dict(leaf=(226, 130, 60), leaf_l=(250, 186, 90), ground=(196, 150, 90)),
    'winter': dict(leaf=None, leaf_l=None, ground=(236, 240, 250)),
    'spring': dict(leaf=(250, 176, 200), leaf_l=(255, 222, 232), ground=(140, 196, 110)),
}


def season_tree(d, x, base, s, season, T, trunk=(110, 74, 52)):
    c = SEASON[season]
    if c['leaf']:
        pix.tree_round(d, x, base, s, c['leaf'], c['leaf_l'], trunk, sway=round(math.sin(T * 1.5)))
        if season == 'spring':
            r = rng(5)
            for k in range(20):
                px = x + r.uniform(-18, 18) * s; py = base - r.uniform(16, 42) * s
                d.point((px, py), fill=(255, 255, 255))
    else:
        d.rectangle([x - 2 * s, base - 14 * s, x + 2 * s, base], fill=trunk)
        for a, ln in ((-0.9, 22), (-0.5, 26), (0.0, 24), (0.5, 26), (0.9, 20)):
            ex, ey = x + math.sin(a) * ln * s, base - 14 * s - math.cos(a) * ln * s
            d.line([(x, base - 14 * s), (ex, ey)], fill=trunk, width=max(1, int(s)))
            d.line([(ex - 2, ey), (ex + 2, ey)], fill=(250, 252, 255))


def umbrella(d, x, y, r, col, col_s=None, tilt=0.0, edge=OUT):
    """(x, y) 是伞面下沿中点，tilt 往右为正（弧度）"""
    col_s = col_s or lerpc(col, (0, 0, 0), 0.25)
    rx, ry = r, r * 0.62
    ca, sa = math.cos(tilt), math.sin(tilt)

    def R(px, py): return (x + px * ca - py * sa, y + px * sa + py * ca)
    top = [R(rx * math.cos(a), -ry * math.sin(a)) for a in np.linspace(0, math.pi, 24)]
    scal = []
    for k in range(5):
        a0 = rx - 2 * rx * k / 5; a1 = rx - 2 * rx * (k + 1) / 5
        for u in np.linspace(0, 1, 5)[1:]:
            scal.append(R(lerp(a0, a1, u), -2.5 * math.sin(math.pi * u)))
    poly = top + scal
    d.polygon([(px + 0.5, py + 1) for px, py in poly], fill=edge)
    d.polygon(poly, fill=col)
    for k in range(1, 5):
        px = rx - 2 * rx * k / 5
        d.line([R(0, -ry), R(px, -1)], fill=col_s)
    d.line([R(0, -ry), R(0, -ry - 3)], fill=edge)
    bx, by = R(0, r * 1.1)
    d.line([R(0, -ry + 1), (bx, by)], fill=(70, 60, 70))
    d.line([(bx, by), R(-2, r * 1.1 + 2)], fill=(70, 60, 70))
    return (bx, by)


# ---------------------------------------------------------------- 银河
@lru_cache(None)
def _milky():
    yy, xx = np.mgrid[0:H, 0:W]
    dist = (yy - (H * 0.95 - xx * 0.45)) / 34
    r = np.random.default_rng(7)
    noise = r.random((H // 3 + 2, W // 3 + 2)).repeat(3, 0).repeat(3, 1)[:H, :W]
    a = np.exp(-dist ** 2) * (0.7 + 0.3 * noise)
    return a


def milky_way(img, T, a=1.0):
    m = _milky()
    blend_box(img, (0, 0, W, H), (150, 120, 210), m * 0.45 * a, levels=6)
    blend_box(img, (0, 0, W, H), (255, 220, 236), np.clip(m - 0.55, 0, 1) * 0.9 * a, levels=6)
    d = ImageDraw.Draw(img)
    r = rng(99)
    for i in range(220):
        x = r.uniform(0, W); y = r.uniform(0, H)
        if r.random() < m[int(y), int(x)] * 1.4:
            b = 0.5 + 0.5 * math.sin(T * (1 + r.random() * 2) + i)
            d.point((x, y), fill=lerpc((120, 110, 170), (255, 255, 255), b * a))


# ---------------------------------------------------------------- 对话气泡、捧着的手、问号
def bubble(img, d, x, y, w, h, tail=(0, 0), a=1.0, dots=3, T=0.0, pop=0.0):
    """对话气泡：(x, y) 是气泡中心，tail 是尾巴尖的位置；dots 是里面点点点的个数"""
    if a <= 0: return
    s = eback(clamp(a)) if a < 1 else 1.0
    w2, h2 = w * s / 2, h * s / 2
    lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay)
    ld.polygon([(x - 6 * s, y + h2 - 2), (x + 4 * s, y + h2 - 2), tail], fill=OUT)
    ld.rounded_rectangle([x - w2 - 1, y - h2 - 1, x + w2 + 1, y + h2 + 1], 6, fill=OUT)
    ld.rounded_rectangle([x - w2, y - h2, x + w2, y + h2], 6, fill=(255, 252, 244))
    ld.polygon([(x - 5 * s, y + h2 - 1), (x + 3 * s, y + h2 - 1), (tail[0] + (1 if tail[0] < x else -1), tail[1] - 2)], fill=(255, 252, 244))
    for k in range(dots):
        bob = round(math.sin(T * 6 - k) * 1.2)
        ld.rectangle([x - 10 * s + k * 10 * s, y + bob - 1, x - 8 * s + k * 10 * s, y + bob + 1], fill=OUT)
    if pop > 0:
        al = np.array(lay)[..., 3] > 0
        al &= pix.BAYER >= pop
        lay.putalpha(Image.fromarray((al * 255).astype(np.uint8)))
    img.paste(lay, (0, 0), lay)


def cupped_hands(img, d, cx, base, s=1.0, sleeve=pix.SKY_T):
    """捧着的两只手（从画面下方伸上来），返回掌心的中心"""
    S = lambda v: v * s
    for sg in (-1, 1):
        cuff = [(cx + sg * S(20), base), (cx + sg * S(64), base), (cx + sg * S(58), base - S(30)), (cx + sg * S(22), base - S(26))]
        d.polygon([(px, py + 1) for px, py in cuff], fill=OUT)
        d.polygon(cuff, fill=sleeve)
        d.line([cuff[3], cuff[2]], fill=lerpc(sleeve, (255, 255, 255), 0.4), width=2)
        palm = [(cx + sg * S(2), base - S(34)), (cx + sg * S(30), base - S(28)), (cx + sg * S(56), base - S(40)), (cx + sg * S(60), base - S(56)),
                (cx + sg * S(46), base - S(70)), (cx + sg * S(10), base - S(66)), (cx + sg * S(1), base - S(52))]
        d.polygon([(px + sg, py) for px, py in palm], fill=OUT)
        d.polygon(palm, fill=SKIN)
        for k in range(3):
            fx = cx + sg * S(16 + k * 12)
            d.line([(fx, base - S(68)), (fx + sg * S(2), base - S(58))], fill=SKIN_S)
        d.line([(cx + sg * S(8), base - S(46)), (cx + sg * S(40), base - S(44))], fill=SKIN_S)
    return (cx, base - S(60))


def old_man(img, d, x, y, view='side', pose='stand', ph=0, flip=False, s=1, cane=True, expr='smile', shade=None, alpha=1.0):
    """老了的他，拄一根拐杖"""
    props.person_s(img, 'boy', x, y, s, 'old', view, pose, ph, expr, 'down', flip, alpha, shade)
    if cane and pose != 'sit':
        cx = x + (6 if not flip else -6) * s
        d.line([(cx, y - 18 * s), (cx + (1 if not flip else -1) * s, y)], fill=(110, 74, 50), width=max(1, int(s)))
        d.line([(cx, y - 18 * s), (cx - (3 if not flip else -3) * s, y - 19 * s)], fill=(110, 74, 50), width=max(1, int(s)))


def memory(T, w=96, h=60):
    """全片 T 秒处画面的缩小版，拿来当回忆的照片"""
    return _memory(round(T, 2), w, h)


@lru_cache(None)
def _memory(T, w, h):
    return props.shrink(SNAP(T), w, h)


def stars_bg(img, d, T, a=1.0, n=200, base=(20, 20, 60)):
    pix.stars(d, T, H, a, n, base=base)
