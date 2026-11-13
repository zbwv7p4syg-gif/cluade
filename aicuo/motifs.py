"""爱错 · 这首歌自己的道具：北风精灵、心形红叶、会被吹秃的树、会裂开的大心、纸飞机、捧着的手、镜子、相册、
老电视、雪地里的小屋、极光、闪电和大钟。

北风是一团冰蓝色的云，有眼睛、会鼓起腮帮子吹气；红叶是一片心形的叶子，代表"她"。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
from pix import (W, H, OUT, SKIN, SKIN_S, clamp, lerp, lerpc, ease, eout, glow, tfill, blend_box, outline, rng)
from props import dpaste, puff, RED, RED_L, RED_D, CREAM, GOLD, GOLD_L

SNAP = None

# ---------------------------------------------------------------- 北风精灵
WIND_BODY, WIND_SHADE, WIND_LIGHT, WIND_OUT = (222, 236, 252), (160, 190, 228), (255, 255, 255), (60, 78, 128)
WIND_BLOBS = [(-13, 3, 8), (-4, -5, 11), (7, -4, 10), (14, 3, 8), (2, 6, 10), (-9, 8, 7), (10, 8, 7)]


@lru_cache(None)
def wind_img(mood='look', s=1.0, ph=0, look=(1, 0), tail=True):
    """北风，朝右。mood: look 睁眼 / blow 鼓腮吹气 / sad 难过 / cry 闭眼流泪 / calm 闭眼微笑 / roar 张嘴怒吼。
    返回 (RGBA 图, 身体中心在图里的坐标)"""
    pad = int(30 * s) + 4
    w, h = int(70 * s) + pad * 2, int(44 * s) + pad
    cx, cy = w // 2 + int(6 * s), h // 2
    im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im)
    wob = [math.sin(ph * math.pi / 4 + k * 1.3) * 0.8 for k in range(len(WIND_BLOBS))]
    blobs = list(WIND_BLOBS)
    if mood in ('blow',): blobs.append((19, 4, 6))                      # 鼓起来的腮帮子
    if mood == 'roar': blobs.append((18, 2, 7))
    # 尾巴：身后卷起两道风
    if tail:
        for j, (amp_, ln, off) in enumerate(((5, 30, 0), (3, 22, 6))):
            pts = []
            for k in range(ln):
                u = k / ln
                x = cx - 14 * s - k * 1.2 * s
                y = cy + (2 + off) * s + math.sin(u * 5 + ph * math.pi / 4 + j) * amp_ * s * (1 - u * 0.4)
                pts.append((x, y))
            for k in range(len(pts) - 1):
                wd = max(1, int(round((3.5 - 3 * k / len(pts)) * s * (0.8 if j else 1))))
                d.line([pts[k], pts[k + 1]], fill=WIND_SHADE if k > len(pts) * 0.6 else WIND_BODY, width=wd)
            ex, ey = pts[-1]
            d.ellipse([ex - 2 * s, ey - 2 * s, ex + 1 * s, ey + 1 * s], outline=WIND_SHADE)
    for (bx, by, r), wv in zip(blobs, wob + [0, 0]):
        r = (r + wv) * s
        d.ellipse([cx + bx * s - r, cy + by * s - r + 2 * s, cx + bx * s + r, cy + by * s + r + 2 * s], fill=WIND_SHADE)
    for (bx, by, r), wv in zip(blobs, wob + [0, 0]):
        r = (r + wv) * s
        d.ellipse([cx + bx * s - r, cy + by * s - r, cx + bx * s + r, cy + by * s + r - 1], fill=WIND_BODY)
    for bx, by, r in WIND_BLOBS[1:3]:                                     # 头顶的高光
        d.arc([cx + (bx - r * 0.6) * s, cy + (by - r * 0.7) * s, cx + (bx + r * 0.3) * s, cy + (by + r * 0.2) * s], 190, 280,
              fill=WIND_LIGHT, width=max(1, int(s)))
    im = outline(im, WIND_OUT)
    d = ImageDraw.Draw(im)
    E, Wt = (30, 34, 60), (255, 255, 255)
    eyes = [(cx + 5 * s, cy - 1 * s), (cx + 13 * s, cy - 1 * s)]
    ew, eh = max(2, round(2 * s)), max(3, round(3 * s))
    blush = (250, 176, 196)
    for k, (ex, ey) in enumerate(eyes):
        if mood in ('look', 'sad', 'roar'):
            d.rectangle([ex - ew + 1, ey - eh + 1, ex + ew - 1, ey + eh - 1], fill=Wt)
            pxo, pyo = look[0] * max(1, round(s * 0.8)), look[1] * max(1, round(s * 0.8))
            d.rectangle([ex - ew // 2 + pxo, ey - eh // 2 + pyo, ex + (ew - 1) // 2 + pxo, ey + (eh - 1) // 2 + pyo], fill=E)
            if mood == 'sad':                                              # 往下耷拉的眉毛
                bx0 = ex - ew - s; bx1 = ex + ew + s
                if k == 0: d.line([(bx0, ey - eh - 1 * s), (bx1, ey - eh - 2.5 * s)], fill=E, width=max(1, int(s * 0.8)))
                else: d.line([(bx0, ey - eh - 2.5 * s), (bx1, ey - eh - 1 * s)], fill=E, width=max(1, int(s * 0.8)))
            if mood == 'roar':
                if k == 0: d.line([(ex - ew - s, ey - eh - 2.5 * s), (ex + ew, ey - eh - 0.5 * s)], fill=E, width=max(1, int(s)))
                else: d.line([(ex - ew, ey - eh - 0.5 * s), (ex + ew + s, ey - eh - 2.5 * s)], fill=E, width=max(1, int(s)))
        elif mood == 'blow':                                               # 使劲吹：> <
            if k == 0: d.line([(ex - ew, ey - eh + 1), (ex + ew - 1, ey), (ex - ew, ey + eh - 1)], fill=E, width=max(1, int(s * 0.8)))
            else: d.line([(ex + ew, ey - eh + 1), (ex - ew + 1, ey), (ex + ew, ey + eh - 1)], fill=E, width=max(1, int(s * 0.8)))
        else:                                                              # 闭眼：cry 是往下弯，calm 是往上弯
            if mood == 'cry': d.arc([ex - ew - s, ey - eh, ex + ew + s, ey + eh], 200, 340, fill=E, width=max(1, int(s * 0.8)))
            else: d.arc([ex - ew - s, ey - eh, ex + ew + s, ey + eh], 20, 160, fill=E, width=max(1, int(s * 0.8)))
    if mood in ('look', 'calm', 'blow'):
        for bx in (cx + 2 * s, cx + 17 * s):
            d.rectangle([bx - s, cy + 3 * s, bx + s, cy + 4 * s], fill=blush)
    mx, my = cx + 9 * s, cy + 5 * s
    if mood == 'blow':
        mx = cx + 24 * s; my = cy + 4 * s
        d.ellipse([mx - 2 * s, my - 2 * s, mx + 1.5 * s, my + 2 * s], fill=E)
    elif mood == 'roar':
        d.ellipse([mx - 4 * s, my - 2 * s, mx + 4 * s, my + 5 * s], fill=E)
        d.rectangle([mx - 2 * s, my + 2.5 * s, mx + 2 * s, my + 4 * s], fill=(200, 80, 100))
    elif mood in ('sad', 'cry'):
        d.arc([mx - 3 * s, my, mx + 3 * s, my + 4 * s], 200, 340, fill=E, width=max(1, int(s * 0.7)))
    elif mood == 'calm':
        d.arc([mx - 2 * s, my - 2 * s, mx + 2 * s, my + 1.5 * s], 20, 160, fill=E, width=max(1, int(s * 0.7)))
    else:
        d.rectangle([mx - s, my, mx + s, my + s * 0.8], fill=E)
    return im, (cx, cy)


def wind(img, x, y, s=1.0, T=0.0, mood='look', look=(1, 0), flip=False, alpha=1.0, tail=True, tears=0.0):
    """把北风放在 (x, y)（身体中心）。flip=True 朝左。tears>0 时眼角往下掉泪珠"""
    ph = int(T * 6) % 8
    s = round(s * 4) / 4
    im, (cx, cy) = wind_img(mood, s, ph, tuple(look), tail)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT); cx = im.width - 1 - cx
    bob = math.sin(T * 2.2) * 1.5 * s
    dpaste(img, im, x - cx, y - cy + bob, alpha)
    if tears > 0:
        d = ImageDraw.Draw(img)
        sg = -1 if flip else 1
        for k, ex in enumerate((5, 13)):
            for j in range(3):
                f = (T * 1.3 + j / 3 + k * 0.17) % 1
                tx = x + sg * ex * s + sg * f * 3 * s; ty = y + bob + 2 * s + f * 26 * s
                if f < tears:
                    d.rectangle([tx, ty, tx + max(1, s * 0.8), ty + max(1, s * 1.4)], fill=(150, 200, 255) if j % 2 else (200, 230, 255))


def streaks(img, d, T, box, n=24, speed=260, col=(230, 240, 255), seed=0, ln=(18, 46), curl=0.3, a=1.0, dirx=1):
    """风：一道道从左往右（dirx=-1 时从右往左）飞过去的白线，偶尔打个卷"""
    x0, y0, x1, y1 = box
    wid = x1 - x0 + 120
    for i in range(n):
        r = rng(i * 41 + seed)
        L = r.uniform(*ln); sp = speed * r.uniform(0.7, 1.3)
        y = r.uniform(y0, y1)
        x = x0 - 60 + (r.uniform(0, wid) + T * sp) % wid
        if dirx < 0: x = x1 + x0 - x
        k = r.random()
        c = lerpc(col, (120, 140, 190), 0.5 * k)
        pts = [(x - dirx * u * L, y + math.sin(u * 3 + T * 3 + i) * 1.5) for u in np.linspace(0, 1, 8)]
        if a >= 1: d.line(pts, fill=c)
        else: tfill(img, 'line', pts, c, a)
        if k < curl:                                                       # 头上打个小卷
            hx, hy = pts[0]
            cr = 3 + (i % 3)
            ang0 = (T * 8 + i) % 6.28
            arc = [(hx + dirx * cr * math.sin(ang0 + u * 5), hy - cr + cr * math.cos(ang0 + u * 5)) for u in np.linspace(0, 1, 10)]
            if a >= 1: d.line(arc, fill=c)
            else: tfill(img, 'line', arc, c, a)


# ---------------------------------------------------------------- 心形红叶（她）
LEAF = ["..RR...RR..",
        ".RLRR.RRRR.",
        "RLLRRRRRRRR",
        "RLRRRVRRRRR",
        "RRRRRVRRRRD",
        ".RRRRVRRRD.",
        "..RRRVRRD..",
        "...RRVRD...",
        "....RVD....",
        ".....s.....",
        ".....s....."]
LEAF_PAL = {'R': (220, 50, 62), 'L': (255, 132, 120), 'V': (150, 26, 44), 'D': (176, 34, 52), 's': (120, 64, 44)}


@lru_cache(None)
def leaf_img(s=1, squash=8, rot=0, glow_=False):
    """心形红叶。squash 0..8：横向压扁的程度（8 为不压，翻面时变小），rot 是旋转角（度）"""
    h = len(LEAF); w = len(LEAF[0])
    im = Image.new('RGBA', (w, h)); px = im.load()
    for y, row in enumerate(LEAF):
        for x, ch in enumerate(row):
            if ch != '.': px[x, y] = LEAF_PAL[ch] + (255,)
    im = outline(im, (90, 18, 34))
    if s != 1: im = im.resize((im.width * s, im.height * s), Image.NEAREST)
    nw = max(2, round(im.width * abs(squash) / 8))
    if nw != im.width:
        im = im.resize((nw, im.height), Image.NEAREST)
        if squash < 0: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if rot: im = im.rotate(rot, resample=Image.NEAREST, expand=True)
    return im


def leaf(img, x, y, s=1, T=0.0, spin=1.0, rot=None, alpha=1.0, ph=0.0):
    """在 (x, y)（中心）放一片红叶。spin 控制翻转快慢；rot 不给时随时间轻轻摆"""
    sq = int(round(8 * math.cos(T * 4 * spin + ph))) if spin else 8
    if sq == 0: sq = 1
    r = rot if rot is not None else 25 * math.sin(T * 2.3 * max(spin, 0.3) + ph)
    im = leaf_img(s, sq, int(round(r / 15)) * 15)
    dpaste(img, im, x - im.width / 2, y - im.height / 2, alpha)


MINI = None


def mini_leaf(img, x, y, T, alpha=1.0):
    """字幕下面的小红叶：5×5，翻着飘"""
    global MINI
    if MINI is None:
        rows = [".R.R.", "RLRRR", "RRRRR", ".RRR.", "..R.."]
        frames = []
        for k in range(3):
            im = Image.new('RGBA', (5, 5)); px = im.load()
            for yy, row in enumerate(rows):
                for xx, ch in enumerate(row):
                    if ch != '.': px[xx, yy] = LEAF_PAL[ch] + (255,)
            if k == 1: im = im.resize((3, 5), Image.NEAREST)
            if k == 2: im = im.rotate(-90, resample=Image.NEAREST)
            frames.append(outline(im, (70, 16, 30)))
        MINI = frames
    im = MINI[[0, 1, 0, 2][int(T * 6) % 4]]
    dpaste(img, im, x - im.width / 2, y - im.height / 2, alpha)


LEAF_COLS = ((220, 50, 62), (236, 110, 60), (246, 172, 60), (196, 44, 56), (250, 140, 80))


def leaf_bit(d, x, y, t, i, cols=LEAF_COLS):
    """小树叶粒子：2×2 / 2×1 / 1×1 轮换"""
    c = cols[i % len(cols)]
    f = int(t * 6 + i) % 3
    if f == 0: d.rectangle([x, y, x + 1, y + 1], fill=c); d.point((x, y), fill=lerpc(c, (255, 255, 255), 0.35))
    elif f == 1: d.rectangle([x, y, x + 1, y], fill=c)
    else: d.point((x, y), fill=c)


# ---------------------------------------------------------------- 树
@lru_cache(None)
def tree_shape(seed, h, depth=6, spread=0.5):
    """一棵枝杈分明的树：返回枝条 [(父节点, 长度, 角度, 粗细, 层级)] 和树叶挂点（枝梢）"""
    r = rng(seed)
    segs = []                                                              # (parent, length, angle, width, depth)

    def grow(parent, ln, ang, wd, dep):
        idx = len(segs)
        segs.append((parent, ln, ang, wd, dep))
        if dep >= depth: return
        kids = 2 if r.random() < 0.7 or dep < 1 else 3
        for k in range(kids):
            a = ang + (k - (kids - 1) / 2) * spread * r.uniform(0.8, 1.25) + r.uniform(-0.12, 0.12)
            a = lerp(a, -math.pi / 2, 0.18)                               # 枝条往上长，树冠圆一些
            grow(idx, ln * r.uniform(0.7, 0.82), a, max(1, wd * 0.68), dep + 1)
    grow(-1, h * 0.3, -math.pi / 2 + r.uniform(-0.05, 0.05), max(2, h / 16), 0)
    tips = [i for i, s in enumerate(segs) if s[4] >= depth - 1]
    leaves = []
    for i in tips:
        for k in range(5):
            leaves.append((i, r.uniform(-7, 7), r.uniform(-7, 5), r.randrange(len(LEAF_COLS)), r.random()))
    return segs, leaves


def tree_nodes(segs, x, base, sway, T, gust=0.0):
    """按风吹的弯曲算出每段枝条的端点"""
    pts = []
    for i, (p, ln, ang, wd, dep) in enumerate(segs):
        x0, y0, a0 = (x, base, 0.0) if p < 0 else pts[p][2:5]
        bend = sway * 0.012 * dep + gust * math.sin(T * 9 + dep * 1.7 + i * 0.3) * 0.012 * dep
        a = ang + a0 + bend
        x1, y1 = x0 + math.cos(a) * ln, y0 + math.sin(a) * ln
        pts.append((x0, y0, x1, y1, a - ang))
    return pts


def tree(img, d, x, base, h, T, seed=3, sway=0.0, gust=0.0, leaf_on=None, bark=(70, 48, 44), bark_d=(44, 30, 32), snow=0.0,
         leaf_cols=LEAF_COLS, shade=1.0, depth=6, spread=0.5, bud=0.0):
    """画树。leaf_on(i, 叶子信息) 返回 False 的叶子不画；snow 0..1 让枝条积雪；bud 0..1 在枝梢冒出新芽。返回叶子的屏幕坐标"""
    segs, leaves = tree_shape(seed, h, depth, spread)
    pts = tree_nodes(segs, x, base, sway, T, gust)
    bk = lerpc((0, 0, 0), bark, shade); bkd = lerpc((0, 0, 0), bark_d, shade)
    for (p, ln, ang, wd, dep), (x0, y0, x1, y1, _) in zip(segs, pts):
        w = max(1, int(round(wd)))
        d.line([(x0, y0), (x1, y1)], fill=bk, width=w)
        if w >= 3: d.line([(x0 + 1, y0), (x1 + 1, y1)], fill=bkd, width=max(1, w // 3))
        if snow > 0 and dep < 6:
            sn = lerpc((0, 0, 0), (240, 246, 255), shade)
            if abs(math.cos(ang)) > 0.35 or dep > 2:
                n = int(snow * 6)
                for k in range(n):
                    u = (k + 0.5) / max(1, n)
                    d.point((lerp(x0, x1, u), lerp(y0, y1, u) - w / 2 - 1), fill=sn)
    if bud > 0:                                                            # 一根枝梢上冒出的新芽
        bc = lerpc((0, 0, 0), (120, 210, 110), shade)
        tips = [i for i, s_ in enumerate(segs) if s_[4] == depth]
        tipx, tipy = pts[tips[len(tips) // 3]][2:4]
        r_ = 1 + int(bud * 2)
        d.ellipse([tipx - r_, tipy - r_ - 1, tipx + r_, tipy + r_ - 1], fill=bc)
        if bud > 0.6: d.point((tipx - 1, tipy - r_ - 1), fill=lerpc((0, 0, 0), (190, 250, 170), shade))
    out = []
    for j, (i, dx, dy, ci, rnd) in enumerate(leaves):
        lx, ly = pts[i][2] + dx, pts[i][3] + dy
        out.append((lx, ly))
        if leaf_on is not None and not leaf_on(j, rnd): continue
        c = lerpc((0, 0, 0), leaf_cols[ci % len(leaf_cols)], shade)
        jig = int(round(math.sin(T * 7 + j) * gust * 1.2))
        d.rectangle([lx + jig, ly, lx + jig + 2, ly + 1], fill=c)
        d.point((lx + jig + 1, ly - 1), fill=c)
        if rnd < 0.3: d.point((lx + jig, ly), fill=lerpc(c, (255, 255, 255), 0.3))
    return out


# ---------------------------------------------------------------- 大心
@lru_cache(None)
def heart_img(s=4, col=(226, 48, 66), hi=(255, 140, 150), lo=(150, 22, 46)):
    """像素大心：带高光和暗边，返回 RGBA，心尖朝下。心形曲线 x 在 ±16、y 在 -12..17 之间（乘 s）"""
    w_, h_ = int(34 * s) + 8, int(31 * s) + 8
    im = Image.new('RGBA', (w_, h_)); d = ImageDraw.Draw(im)
    cx, cy = w_ / 2, h_ / 2 - 2.5 * s
    d.polygon(pix.heart_poly(cx, cy, s), fill=lo)
    d.polygon(pix.heart_poly(cx - 0.6 * s, cy - 0.8 * s, s * 0.9), fill=col)
    d.polygon(pix.heart_poly(cx - 7 * s, cy - 4 * s, s * 0.3), fill=hi)
    d.rectangle([cx - 10 * s, cy - 7 * s, cx - 8.6 * s, cy - 5.6 * s], fill=(255, 236, 240))
    return outline(im, (60, 10, 26))


def heart(img, cx, cy, s=4, beat=0.0, crack=0.0, split=0.0, seed=1, col=None, alpha=1.0, tilt=0.0):
    """在 (cx, cy) 画一颗大心。beat 让它随拍子鼓一下；crack 0..1 让一道裂缝从上往下长；split 是两半分开的像素数"""
    k = s * (1 + 0.08 * beat)
    k = round(k * 8) / 8
    im = heart_img(k) if col is None else heart_img(k, *col)
    if crack <= 0 and split <= 0:
        dpaste(img, im, cx - im.width / 2, cy - im.height / 2, alpha); return
    # 裂缝：从心口凹处一路锯齿往下到心尖
    r = rng(seed)
    w_, h_ = im.size
    top = (w_ / 2, h_ / 2 - k * 7.5); bot = (w_ / 2, h_ / 2 + k * 14.5)
    zz = [top]
    n = 7
    for i in range(1, n):
        u = i / n
        zz.append((lerp(top[0], bot[0], u) + (k * 2.2 if i % 2 else -k * 2.2) * r.uniform(0.6, 1.2), lerp(top[1], bot[1], u)))
    zz.append(bot)
    if split > 0:
        left = Image.new('L', im.size, 0); ImageDraw.Draw(left).polygon([(0, 0)] + [(x, y) for x, y in zz] + [(0, h_), (0, 0)], fill=255)
        L = Image.new('RGBA', im.size); L.paste(im, (0, 0), left)
        R = im.copy(); R.putalpha(Image.fromarray(np.minimum(np.array(im.getchannel('A')), 255 - np.array(left))))
        L = L.rotate(split * 1.5 + tilt, resample=Image.NEAREST, center=bot)
        R = R.rotate(-split * 1.5 - tilt, resample=Image.NEAREST, center=bot)
        dpaste(img, L, cx - w_ / 2 - split, cy - h_ / 2 + split * 0.3, alpha)
        dpaste(img, R, cx - w_ / 2 + split, cy - h_ / 2 + split * 0.3, alpha)
        return
    dpaste(img, im, cx - w_ / 2, cy - h_ / 2, alpha)
    d = ImageDraw.Draw(img)
    m = int(len(zz) * clamp(crack) + 0.999)
    pts = [(cx - w_ / 2 + x, cy - h_ / 2 + y) for x, y in zz[:max(2, m)]]
    if crack < 1 and m >= 2:                                             # 正在长的那一截只画一部分
        f = (clamp(crack) * (len(zz) - 1)) % 1 or 1
        (ax, ay), (bx, by) = pts[-2], pts[-1]
        pts[-1] = (lerp(ax, bx, f), lerp(ay, by, f))
    d.line(pts, fill=(40, 6, 20), width=max(1, int(k * 0.6)))
    d.line([(x + 1, y) for x, y in pts], fill=(255, 190, 200), width=1)


# ---------------------------------------------------------------- 纸飞机
def plane(d, x, y, s=1.0, ang=0.0, col=(250, 248, 240), sh=(196, 200, 214), edge=OUT):
    """纸飞机，(x, y) 是机头，ang 是飞行方向（弧度，0 朝右，正值朝下）"""
    ca, sa = math.cos(ang), math.sin(ang)

    def P(u, v): return (x + (u * ca - v * sa) * s, y + (u * sa + v * ca) * s)
    body = [P(0, 0), P(-16, -6), P(-12, 0)]
    wing = [P(0, 0), P(-12, 0), P(-15, 5)]
    d.polygon([(px + 1, py + 1) for px, py in body + wing], fill=edge)
    d.polygon(body, fill=col); d.polygon(wing, fill=sh)
    d.line([P(0, 0), P(-12, 0)], fill=edge)


# ---------------------------------------------------------------- 捧着的两只手（正面略俯视）
def cupped_hands(img, d, cx, cy, s=3, open_=0.0, shade=1.0, tilt=0.0):
    """两只手掌心朝上合成一个碗，(cx, cy) 是碗心。open_ 0..1 让两只手往两边分开、往外翻"""
    sh = lambda c: lerpc((0, 0, 0), c, shade)
    sk, sk_l, sk_d, sk_dd = sh(SKIN), sh((255, 232, 210)), sh(SKIN_S), sh((180, 120, 104))
    sl, sl_d = sh((58, 82, 140)), sh((40, 58, 106))
    sep = open_ * 14 * s
    for side in (-1, 1):
        ox = cx + side * sep
        dy = open_ * 4 * s
        lay = Image.new('L', (W, H), 0); ld = ImageDraw.Draw(lay)
        ld.rectangle([ox if side > 0 else 0, 0, W if side > 0 else ox, H], fill=255)
        part = Image.new('RGBA', (W, H)); pd = ImageDraw.Draw(part)
        # 袖口和手腕
        pd.polygon([(ox + side * 6 * s, cy + 6 * s + dy), (ox + side * 15 * s, cy + 3 * s + dy), (ox + side * 22 * s, H + 4), (ox + side * 6 * s, H + 4)], fill=sl)
        pd.line([(ox + side * 15 * s, cy + 3 * s + dy), (ox + side * 22 * s, H + 4)], fill=sl_d, width=max(1, s))
        pd.rectangle([ox + (0 if side > 0 else -12 * s), cy + 7 * s + dy, ox + (12 * s if side > 0 else 0), cy + 10 * s + dy], fill=sk_d)
        # 手的外沿（碗底）
        pd.ellipse([ox - 16 * s, cy - 5 * s + dy, ox + 16 * s, cy + 9 * s + dy], fill=sk)
        # 远处的一排指尖
        for k in range(4):
            fx = ox + side * (3.5 + k * 3.2) * s
            fy = cy - (6.5 - abs(k - 1.5) * 0.6) * s + dy + open_ * k * 1.5 * s
            pd.ellipse([fx - 1.8 * s, fy - 2.2 * s, fx + 1.8 * s, fy + 2.4 * s], fill=sk_d if k % 2 else sk)
        # 掌心
        pd.ellipse([ox - 13 * s, cy - 5 * s + dy, ox + 13 * s, cy + 4 * s + dy], fill=sk_l)
        pd.ellipse([ox - 10 * s, cy - 2 * s + dy, ox + 10 * s, cy + 4 * s + dy], fill=sk)
        pd.arc([ox - 9 * s, cy - 3 * s + dy, ox + 9 * s, cy + 3 * s + dy], 20, 160, fill=sk_d)
        # 大拇指搭在外沿
        tx = ox + side * 14 * s
        pd.ellipse([tx - 2.2 * s, cy - 4.5 * s + dy, tx + 2.2 * s, cy + 3 * s + dy], fill=sk)
        pd.line([(tx - side * 1.5 * s, cy - 2 * s + dy), (tx - side * 1.5 * s, cy + 2 * s + dy)], fill=sk_d)
        part = outline(part, OUT)
        img.paste(part, (0, 0), Image.fromarray(np.minimum(np.array(part.getchannel('A')), np.array(lay))))
    if open_ < 0.05:
        d.line([(cx, cy - 1 * s), (cx, cy + 8 * s)], fill=sk_dd)


# ---------------------------------------------------------------- 雪地里的小屋
def house(img, d, x, base, w, h, T, lit=1.0, seed=0, snow=True, people=0, wall=(110, 84, 92), roof=(70, 52, 76)):
    """有暖光窗户的小屋，(x, base) 是左下角。people>0 时窗里有一家人的剪影"""
    d.rectangle([x, base - h, x + w, base], fill=wall)
    d.polygon([(x - 4, base - h), (x + w / 2, base - h - h * 0.7), (x + w + 4, base - h)], fill=roof)
    if snow:
        d.polygon([(x - 4, base - h), (x + w / 2, base - h - h * 0.7), (x + w + 4, base - h), (x + w + 2, base - h + 2), (x + w / 2, base - h - h * 0.7 + 3),
                   (x - 2, base - h + 2)], fill=(236, 242, 255))
    d.rectangle([x + w * 0.62, base - h - h * 0.6, x + w * 0.62 + 4, base - h - h * 0.25], fill=lerpc(roof, (0, 0, 0), 0.3))
    wx0, wy0, wx1, wy1 = x + w * 0.18, base - h * 0.72, x + w * 0.52, base - h * 0.3
    wc = lerpc((60, 60, 90), (255, 206, 120), lit)
    d.rectangle([wx0, wy0, wx1, wy1], fill=wc)
    if people and lit > 0.3:
        r = rng(seed)
        for k in range(people):
            px = lerp(wx0 + 3, wx1 - 3, (k + 0.5) / people) + math.sin(T * 1.5 + k * 2) * 0.6
            ph = r.choice([5, 6, 4])
            sil = lerpc(wc, (60, 36, 40), 0.75)
            d.ellipse([px - 1.5, wy1 - ph - 4, px + 1.5, wy1 - ph - 1], fill=sil)
            d.rectangle([px - 2, wy1 - ph, px + 2, wy1], fill=sil)
    d.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=lerpc(wall, (0, 0, 0), 0.3))
    d.line([(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], fill=lerpc(wall, (0, 0, 0), 0.3))
    d.rectangle([x + w * 0.66, base - h * 0.62, x + w * 0.86, base], fill=lerpc(wall, (0, 0, 0), 0.35))
    if lit > 0: glow(img, (wx0 + wx1) / 2, (wy0 + wy1) / 2, w * 0.7, (255, 190, 110), 0.3 * lit)


# ---------------------------------------------------------------- 极光
def aurora(img, T, y0=20, y1=120, a=0.5, cols=((90, 255, 190), (120, 200, 255), (200, 130, 255)), seed=0):
    """几条竖向的光幕，左右飘动"""
    for k, col in enumerate(cols):
        base = lerp(y0, y1, 0.3 + 0.2 * k)
        xs = np.arange(W)
        yc = base + 14 * np.sin(xs * 0.012 + T * 0.35 + k * 1.7 + seed) + 6 * np.sin(xs * 0.031 - T * 0.5 + k)
        hgt = 26 + 12 * np.sin(xs * 0.02 + T * 0.4 + k * 2)
        yy = np.arange(int(y0) - 30, int(y1) + 20)[:, None]
        f = np.clip(1 - (yc[None, :] - yy) / hgt[None, :], 0, 1) * (yy < yc[None, :] + 2)
        f = f ** 1.6 * (0.6 + 0.4 * np.sin(xs * 0.05 + T * 0.8 + k)[None, :]) ** 2
        ya = max(0, int(y0) - 30)
        f = f[ya - (int(y0) - 30):]
        y_b = min(H, ya + f.shape[0])
        blend_box(img, (0, ya, W, y_b), col, a * f[:y_b - ya], levels=6)


# ---------------------------------------------------------------- 闪电
def lightning(d, x0, y0, y1, seed, col=(240, 236, 255), width=2, branches=2):
    r = rng(seed)
    pts = [(x0, y0)]
    x, y = x0, y0
    while y < y1:
        y += r.uniform(8, 16); x += r.uniform(-12, 12)
        pts.append((x, y))
    d.line(pts, fill=col, width=width)
    for b in range(branches):
        i = r.randrange(1, max(2, len(pts) - 1))
        bx, by = pts[i]
        bp = [(bx, by)]
        for _ in range(3):
            bx += r.uniform(-14, 14); by += r.uniform(6, 12); bp.append((bx, by))
        d.line(bp, fill=col, width=1)


# ---------------------------------------------------------------- 大钟（带齿轮）
def gear(d, cx, cy, r, ang, teeth, col, hub):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    for k in range(teeth):
        a = ang + k * 2 * math.pi / teeth
        x, y = cx + math.cos(a) * (r + 2), cy + math.sin(a) * (r + 2)
        d.rectangle([x - 2, y - 2, x + 2, y + 2], fill=col)
    d.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45], fill=hub)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=col)


def big_clock(img, d, cx, cy, r, hour, minute, T, crack=0.0, glow_a=0.0, face=(244, 236, 214), rim=(150, 112, 60), seed=5):
    """罗马数字的大钟面，crack 0..1 让玻璃从中间裂开"""
    if glow_a > 0: glow(img, cx, cy, r * 1.6, (255, 220, 160), glow_a)
    d.ellipse([cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6], fill=OUT)
    d.ellipse([cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5], fill=rim)
    d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill=lerpc(rim, (255, 230, 170), 0.35))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=face)
    ink = (60, 44, 46)
    for k in range(60):
        a = k * math.pi / 30
        r0 = r - (9 if k % 5 == 0 else 5)
        if k % 5 == 0:
            d.line([(cx + math.sin(a) * r0, cy - math.cos(a) * r0), (cx + math.sin(a) * (r - 3), cy - math.cos(a) * (r - 3))], fill=ink, width=2)
        else:
            d.point((cx + math.sin(a) * (r - 4), cy - math.cos(a) * (r - 4)), fill=lerpc(face, ink, 0.6))
    for k, num in enumerate(['XII', 'III', 'VI', 'IX']):
        a = k * math.pi / 2
        pix.text(img, num, cx + math.sin(a) * (r - 20), cy - math.cos(a) * (r - 20), col=ink, out=None, font=pix.FONT_S, shadow=False)
    hw = max(2, int(r / 14))
    d.line([(cx, cy), (cx + math.sin(hour) * r * 0.5, cy - math.cos(hour) * r * 0.5)], fill=ink, width=hw + 1)
    d.line([(cx - math.sin(minute) * r * 0.12, cy + math.cos(minute) * r * 0.12), (cx + math.sin(minute) * r * 0.82, cy - math.cos(minute) * r * 0.82)],
           fill=(170, 40, 50), width=hw)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(170, 40, 50))
    d.arc([cx - r * 0.8, cy - r * 0.85, cx + r * 0.1, cy - r * 0.05], 200, 250, fill=(255, 255, 255), width=2)
    if crack > 0:
        rr = rng(seed)
        for b in range(7):
            a = b * 2 * math.pi / 7 + rr.uniform(-0.3, 0.3)
            pts = [(cx + rr.uniform(-3, 3), cy + rr.uniform(-3, 3))]
            ln = r * clamp(crack * 1.4 - b * 0.06)
            steps = 5
            for i in range(1, steps + 1):
                u = ln * i / steps
                a2 = a + rr.uniform(-0.25, 0.25)
                pts.append((cx + math.cos(a2) * u, cy + math.sin(a2) * u))
            if ln > 2:
                d.line(pts, fill=(40, 40, 60), width=1)
                d.line([(x + 1, y) for x, y in pts], fill=(255, 255, 255), width=1)
        if crack > 0.5:
            for i in range(int(6 * crack)):
                a = rr.uniform(0, 6.28); u = rr.uniform(0.2, 0.9) * r
                d.line([(cx + math.cos(a) * u, cy + math.sin(a) * u), (cx + math.cos(a + 0.4) * u, cy + math.sin(a + 0.4) * u)], fill=(60, 60, 80))


# ---------------------------------------------------------------- 镜子、相册、老电视、长椅、灯塔
def mirror_frame(d, x0, y0, x1, y1, col=(176, 132, 70), col_d=(116, 82, 44)):
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 5], fill=OUT)
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], fill=col)
    d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=col_d)
    d.pieslice([x0 - 4, y0 - 18, x1 + 4, y0 + 10], 180, 360, fill=OUT)
    d.pieslice([x0 - 3, y0 - 17, x1 + 3, y0 + 9], 180, 360, fill=col)
    d.ellipse([(x0 + x1) / 2 - 3, y0 - 14, (x0 + x1) / 2 + 3, y0 - 8], fill=(220, 60, 70))


def shards(d, box, f, seed=9, col=(255, 255, 255), dark=(30, 30, 50)):
    """玻璃裂纹：从一点往外放射，f 0..1 控制长度"""
    x0, y0, x1, y1 = box
    r = rng(seed)
    cx, cy = lerp(x0, x1, r.uniform(0.4, 0.6)), lerp(y0, y1, r.uniform(0.3, 0.45))
    L = max(x1 - x0, y1 - y0)
    for b in range(9):
        a = b * 2 * math.pi / 9 + r.uniform(-0.2, 0.2)
        pts = [(cx, cy)]
        for i in range(1, 6):
            u = L * clamp(f * 1.3) * i / 5
            a2 = a + r.uniform(-0.2, 0.2)
            pts.append((min(x1, max(x0, cx + math.cos(a2) * u)), min(y1, max(y0, cy + math.sin(a2) * u))))
        d.line(pts, fill=dark); d.line([(x + 1, y) for x, y in pts], fill=col)
    if f > 0.4:
        for ring in (0.25, 0.5):
            rr_ = L * ring * clamp((f - 0.4) * 2)
            d.arc([cx - rr_, cy - rr_, cx + rr_, cy + rr_], r.uniform(0, 360), r.uniform(0, 360) + 140, fill=col)


def bench(d, x, base, w=60, col=(140, 92, 60), col_d=(96, 60, 42), leg=(50, 44, 52)):
    """公园长椅，(x, base) 是左下角"""
    for lx in (x + 4, x + w - 6):
        d.rectangle([lx, base - 12, lx + 2, base], fill=leg)
    d.rectangle([x, base - 14, x + w, base - 12], fill=col)
    d.rectangle([x, base - 12, x + w, base - 11], fill=col_d)
    for k in range(3):
        d.rectangle([x, base - 30 + k * 5, x + w, base - 28 + k * 5], fill=col if k % 2 == 0 else lerpc(col, col_d, 0.4))
    for lx in (x + 4, x + w - 6):
        d.rectangle([lx, base - 31, lx + 2, base - 14], fill=leg)


def crt(img, d, x, y, w, h, screen=None, on=1.0, body=(70, 66, 78), body_d=(46, 42, 54)):
    """老电视，(x, y) 是左上角；screen 是要放进屏幕里的 RGB 图（会缩放到屏幕大小）"""
    d.rounded_rectangle([x - 2, y - 2, x + w + 2, y + h + 2], 6, fill=OUT)
    d.rounded_rectangle([x, y, x + w, y + h], 6, fill=body)
    sx0, sy0, sx1, sy1 = x + 8, y + 8, x + w - 30, y + h - 8
    d.rounded_rectangle([sx0 - 2, sy0 - 2, sx1 + 2, sy1 + 2], 5, fill=body_d)
    if screen is not None:
        sc = screen.resize((sx1 - sx0, sy1 - sy0), Image.NEAREST)
        mask = Image.new('L', sc.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, sc.width - 1, sc.height - 1], 4, fill=255)
        img.paste(sc, (sx0, sy0), mask)
    else:
        d.rounded_rectangle([sx0, sy0, sx1, sy1], 4, fill=(20, 24, 30))
    for k in range(2):
        kx, ky = x + w - 16, y + 18 + k * 18
        d.ellipse([kx - 6, ky - 6, kx + 6, ky + 6], fill=body_d)
        d.line([(kx, ky), (kx + 4 * math.cos(k * 2 + 1), ky + 4 * math.sin(k * 2 + 1))], fill=(170, 170, 180))
    for k in range(4): d.line([(x + w - 24, y + h - 26 + k * 4), (x + w - 8, y + h - 26 + k * 4)], fill=body_d)
    d.point((x + w - 16, y + h - 8), fill=(255, 80, 80) if on > 0.5 else (90, 40, 40))
    d.line([(x + w * 0.4, y - 2), (x + w * 0.25, y - 22)], fill=(150, 150, 160))
    d.line([(x + w * 0.5, y - 2), (x + w * 0.62, y - 24)], fill=(150, 150, 160))
    return (sx0, sy0, sx1, sy1)


def lighthouse(img, d, x, base, h, T, on=1.0):
    w0, w1 = h * 0.16, h * 0.1
    for k in range(5):
        y0 = base - h * k / 5; y1 = base - h * (k + 1) / 5
        a0 = lerp(w0, w1, k / 5); a1 = lerp(w0, w1, (k + 1) / 5)
        d.polygon([(x - a0, y0), (x + a0, y0), (x + a1, y1), (x - a1, y1)], fill=(236, 232, 226) if k % 2 == 0 else (200, 60, 64))
    top = base - h
    d.rectangle([x - w1 - 2, top - 2, x + w1 + 2, top], fill=(50, 46, 56))
    d.rectangle([x - w1 + 1, top - 10, x + w1 - 1, top - 2], fill=lerpc((90, 90, 110), (255, 240, 180), on))
    d.polygon([(x - w1 - 2, top - 10), (x + w1 + 2, top - 10), (x, top - 18)], fill=(170, 50, 56))
    if on > 0:
        glow(img, x, top - 6, 18, (255, 240, 180), 0.5 * on)
        a = T * 1.2
        for sgn in (1, -1):
            dx = math.cos(a) * sgn
            if dx > 0.05:
                L = 260 * dx
                tfill(img, 'polygon', [(x, top - 8), (x + sgn * L, top - 30), (x + sgn * L, top + 14), (x, top - 4)], (255, 240, 190), 0.16 * dx * on)
            elif dx < -0.05:
                L = 260 * -dx
                tfill(img, 'polygon', [(x, top - 8), (x - sgn * L, top - 30), (x - sgn * L, top + 14), (x, top - 4)], (255, 240, 190), 0.16 * -dx * on)


def seagull(d, x, y, t, s=1, col=(250, 250, 255), edge=(70, 70, 90), ph=0):
    """白鸟（侧面）：翅膀上下扇"""
    f = math.sin(t * 9 + ph)
    wy = -4 * f * s
    d.polygon([(x - 6 * s, y), (x + 5 * s, y - 1 * s), (x + 7 * s, y + 1 * s), (x - 4 * s, y + 2 * s)], fill=col)
    d.polygon([(x - 1 * s, y), (x - 6 * s, y + wy - 3 * s), (x + 3 * s, y)], fill=col)
    d.line([(x - 1 * s, y), (x - 6 * s, y + wy - 3 * s), (x + 3 * s, y)], fill=edge)
    d.point((x + 5 * s, y), fill=edge)
    d.point((x + 7 * s, y + 1 * s), fill=(250, 170, 60))


def album(img, d, cx, cy, w, h, open_=1.0, cover=(150, 50, 60), page=(250, 242, 222)):
    """摊开的相册（俯视略斜），返回左右两页的矩形"""
    pw = w / 2
    d.rectangle([cx - pw - 4, cy - h / 2 - 4, cx + pw * lerp(-1, 1, open_) + 4, cy + h / 2 + 4], fill=cover)
    d.rectangle([cx - pw - 4, cy - h / 2 - 4, cx + pw * lerp(-1, 1, open_) + 4, cy + h / 2 + 4], outline=OUT)
    lp = (cx - pw, cy - h / 2, cx - 1, cy + h / 2)
    d.rectangle(lp, fill=page)
    rp = None
    if open_ > 0:
        x1 = cx + pw * lerp(-1, 1, open_)
        if open_ < 0.5:
            d.polygon([(cx, cy - h / 2), (x1, cy - h / 2 - 6 * math.sin(open_ * math.pi)), (x1, cy + h / 2 - 6 * math.sin(open_ * math.pi)),
                       (cx, cy + h / 2)], fill=cover)
        else:
            rp = (cx + 1, cy - h / 2, x1, cy + h / 2)
            d.rectangle(rp, fill=page)
    for k in range(4):
        d.line([(cx - 1 + k * 0.2, cy - h / 2), (cx - 1, cy + h / 2)], fill=lerpc(page, (0, 0, 0), 0.25 - k * 0.05))
    return lp, rp
