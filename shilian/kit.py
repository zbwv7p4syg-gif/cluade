"""永不失联的爱 · 镜头里常用的布景：夜空和银河、弯月、城市、躺着/斜着/站在星球上的人、摩天轮、流星雨、花田。"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
from pix import (W, H, OUT, SKIN, clamp, lerp, lerpc, ease, eout, glow, tfill, blend_box, rng, sky, stars, person, wph)
from props import dpaste

NIGHT = ((0, (6, 8, 30)), (0.55, (20, 24, 70)), (1, (52, 50, 112)))
DEEP = ((0, (2, 2, 14)), (0.6, (10, 12, 40)), (1, (26, 24, 70)))
DUSK = ((0, (40, 46, 110)), (0.45, (120, 96, 170)), (0.78, (240, 140, 140)), (1, (255, 196, 140)))
DAY = ((0, (90, 160, 236)), (0.6, (150, 206, 246)), (1, (226, 242, 252)))
GOLDEN = ((0, (82, 100, 168)), (0.42, (226, 150, 132)), (0.75, (255, 198, 138)), (1, (255, 232, 176)))
RAINY = ((0, (20, 24, 44)), (0.6, (40, 46, 72)), (1, (64, 70, 96)))
DAWN = ((0, (40, 52, 120)), (0.5, (150, 120, 180)), (0.8, (255, 170, 150)), (1, (255, 226, 170)))


def night(img, d, T, stops=NIGHT, n=200, a=1.0, y1=H):
    sky(img, stops, 0, H, 6)
    stars(d, T, y1, a, n)


@lru_cache(None)
def galaxy_layer(seed=1, ang=-0.35, width=46, cols=((150, 120, 255), (120, 200, 255), (255, 170, 220))):
    """一条斜着的银河：带状的光雾加上密密的星点，返回 RGBA"""
    r = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W]
    ca, sa = math.cos(ang), math.sin(ang)
    v = -(xx - W / 2) * sa + (yy - H / 2) * ca
    u = (xx - W / 2) * ca + (yy - H / 2) * sa
    wv = width * (1 + 0.3 * np.sin(u * 0.02 + 1) + 0.2 * np.sin(u * 0.05))
    band = np.exp(-(v / wv) ** 2 * 2.2)
    noise = (np.sin(u * 0.07 + v * 0.11) + np.sin(u * 0.031 - v * 0.17 + 2) + np.sin(u * 0.13 + v * 0.05 + 4)) / 3
    fog = np.clip(band * (0.55 + 0.45 * noise), 0, 1)
    q = np.floor(fog * 5 + pix.bayer(H, W)) / 5
    a = np.zeros((H, W, 4), np.uint8)
    hue = (np.sin(u * 0.01) + 1) / 2
    c0, c1, c2 = (np.array(c, float) for c in cols)
    col = np.where(hue[..., None] < 0.5, c0 + (c1 - c0) * (hue[..., None] * 2), c1 + (c2 - c1) * ((hue[..., None] - 0.5) * 2))
    a[..., :3] = col.astype(np.uint8)
    a[..., 3] = (np.clip(q * 0.45, 0, 1) * 255).astype(np.uint8)
    dots = (r.random((H, W)) < band * 0.09)
    a[dots, :3] = 255; a[dots, 3] = 255
    return Image.fromarray(a)


def galaxy(img, a=1.0, seed=1, ang=-0.35, width=46):
    lay = galaxy_layer(seed, ang, width)
    if a < 1:
        arr = np.array(lay); arr[..., 3] = (arr[..., 3] * a).astype(np.uint8); lay = Image.fromarray(arr)
    img.paste(lay, (0, 0), lay)


def crescent(img, d, cx, cy, r, col=(255, 240, 190), off=(0.42, -0.22), glow_a=0.35):
    """弯月：一个圆减去偏移的圆"""
    if glow_a: glow(img, cx, cy, r * 2.4, (255, 230, 170), glow_a)
    x0, y0, x1, y1 = int(cx - r - 1), int(cy - r - 1), int(cx + r + 2), int(cy + r + 2)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    m = ((xx - cx) ** 2 + (yy - cy) ** 2 <= r * r) & ((xx - cx - off[0] * r * 1.6) ** 2 + (yy - cy - off[1] * r * 1.6) ** 2 > (r * 0.92) ** 2)
    edge = m & ~(((xx - cx) ** 2 + (yy - cy) ** 2 <= (r - 1.5) ** 2) & ((xx - cx - off[0] * r * 1.6) ** 2 + (yy - cy - off[1] * r * 1.6) ** 2 > (r * 0.92 + 1.5) ** 2))
    mm = Image.fromarray((m * 255).astype(np.uint8))
    img.paste(col, (x0, y0), mm)
    img.paste(lerpc(col, (220, 170, 90), 0.5), (x0, y0), Image.fromarray((edge * 255).astype(np.uint8)))


def meteors(d, T, rate=1.0, seed=0, box=(0, 0, W, 140), life=0.8, ang=0.5, ln=90):
    """一阵流星雨：大约每秒 rate 颗"""
    x0, y0, x1, y1 = box
    n = int(T * rate)
    for k in range(max(0, n - 3), n + 1):
        r = rng(k * 97 + seed)
        t0 = (k + r.random()) / rate
        sx, sy = r.uniform(x0 + 40, x1 + 60), r.uniform(y0 - 10, y1 * 0.6)
        pix.meteor(d, T, t0, sx, sy, -ln * math.cos(ang) * r.uniform(0.8, 1.3), ln * math.sin(ang) * r.uniform(0.8, 1.3), life)


# ---------------------------------------------------------------- 人：躺着、斜着、站在球面上
def person_rot(img, who, x, y, ang, s=1, view='side', pose='stand', ph=0, expr='smile', arms='auto', flip=False, alpha=1.0, shade=None,
               pivot='foot'):
    """把人绕脚底（pivot='foot'）或身体中心（'mid'）转 ang 度（逆时针为正）"""
    im = pix.char_img(who, 'young', view, pose, ph % 4, expr, arms)
    ax, ay = pix.CX, pix.FY
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT); ax = pix.CW - 1 - pix.CX
    if shade:
        a = np.array(im); a[..., :3] = np.clip(a[..., :3] * np.array(shade), 0, 255).astype(np.uint8); im = Image.fromarray(a)
    if pivot == 'mid': ay = pix.FY - 14
    if s != 1: im = im.resize((im.width * s, im.height * s), Image.NEAREST); ax, ay = ax * s, ay * s
    pad = max(im.size)
    can = Image.new('RGBA', (pad * 2, pad * 2))
    can.paste(im, (int(pad - ax), int(pad - ay)))
    can = can.rotate(ang, resample=Image.NEAREST)
    dpaste(img, can, x - pad, y - pad, alpha)


def lying(img, who, x, y, s=1, expr='smile', arms='down', flip=False, alpha=1.0, shade=None):
    """仰面躺着：头朝左（flip 头朝右），(x, y) 是身体中点贴地处"""
    person_rot(img, who, x + (14 if not flip else -14) * s, y, -90 if not flip else 90, s, 'front', 'stand', 0, expr, arms, False,
               alpha, shade)


def on_sphere(img, who, cx, cy, r, ang, s=1, **kw):
    """站在球面上：ang 是从正上方顺时针的角度（度）"""
    a = math.radians(ang)
    x, y = cx + math.sin(a) * r, cy - math.cos(a) * r
    person_rot(img, who, x, y, -ang, s, **kw)


# ---------------------------------------------------------------- 城市、花田、摩天轮
def town(img, d, T, base=230, off=0.0, far=(30, 34, 80), near=(18, 20, 50), win=(255, 214, 140), frac=0.3, blink=True):
    pix.city(img, d, base - 18, 31, off * 0.4, far, lerpc(win, far, 0.4), 40, 110, frac * 0.6, T, blink=blink)
    pix.city(img, d, base, 7, off, near, win, 30, 80, frac, T, blink=blink)


def flowers(d, T, y0, y1, n=80, seed=0, cols=((255, 150, 180), (255, 220, 120), (250, 250, 255), (190, 160, 255)), stem=(70, 150, 70)):
    r = rng(seed)
    pts = sorted([(r.uniform(y0, y1), r.uniform(-4, W + 4), r.randrange(len(cols)), r.randrange(3)) for _ in range(n)])
    for y, x, c, k in pts:
        sw = math.sin(T * 2 + x * 0.05) * 0.8
        pix.flower(d, x + sw, y, cols[c], k, stem, h=int(3 + (y - y0) / max(1, y1 - y0) * 5))


def ferris(img, d, cx, cy, r, T, lit=1.0, col=(240, 236, 250), cabin=((255, 120, 150), (120, 200, 255), (255, 210, 90))):
    d.line([(cx, cy), (cx - r * 0.6, cy + r * 1.25)], fill=col, width=2)
    d.line([(cx, cy), (cx + r * 0.6, cy + r * 1.25)], fill=col, width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=2)
    d.ellipse([cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3], outline=col)
    n = 10
    for k in range(n):
        a = T * 0.25 + k * 2 * math.pi / n
        px, py = cx + math.cos(a) * r, cy + math.sin(a) * r
        d.line([(cx, cy), (px, py)], fill=col)
        c = cabin[k % len(cabin)]
        d.rectangle([px - 3, py + 1, px + 3, py + 7], fill=c)
        d.rectangle([px - 2, py + 2, px + 2, py + 4], fill=lerpc(c, (255, 255, 230), 0.6 * lit))
        if lit and (int(T * 4) + k) % 3 == 0: d.point((px, py), fill=(255, 255, 200))
    if lit: glow(img, cx, cy, r * 1.3, (255, 200, 230), 0.15 * lit)


def heart_constellation(img, d, cx, cy, s, f, T, col=(255, 236, 250), line=(150, 170, 255), n=16):
    """星星连成的心：f 0..1 依次点亮、连线"""
    pts = pix.heart_poly(cx, cy, s)[::64 // n]
    k = f * n
    for i in range(n):
        if i + 1 <= k:
            a, b = pts[i], pts[(i + 1) % n]
            u = clamp(k - i)
            d.line([a, (lerp(a[0], b[0], u), lerp(a[1], b[1], u))], fill=line)
    for i, (x, y) in enumerate(pts):
        if i <= k:
            glow(img, x, y, 6, (200, 210, 255), 0.4)
            pix.sparkle(d, int(x), int(y), T + i, col, 2)


def rain_layer(img, d, T, n=160, col=(150, 170, 220), slant=-3, seed=0, a=1.0):
    pix.rain(d, T, -20, W + 20, -10, H, int(n * a), col, 300, slant, 6, seed)


def thought(img, d, x, y, w, h, T, col=(250, 250, 255)):
    """想法云：一团椭圆加两颗小泡泡（往左下）"""
    for (ox, oy, rr) in ((-w * 0.3, h * 0.1, h * 0.5), (0, -h * 0.15, h * 0.6), (w * 0.3, h * 0.1, h * 0.5)):
        d.ellipse([x + ox - rr - 1, y + oy - rr - 1, x + ox + rr + 1, y + oy + rr + 1], fill=OUT)
    for (ox, oy, rr) in ((-w * 0.3, h * 0.1, h * 0.5), (0, -h * 0.15, h * 0.6), (w * 0.3, h * 0.1, h * 0.5)):
        d.ellipse([x + ox - rr, y + oy - rr, x + ox + rr, y + oy + rr], fill=col)
    d.ellipse([x - w / 2, y - h / 2, x + w / 2, y + h / 2], fill=col)
    for k, (bx, by, br) in enumerate(((x - w * 0.45, y + h * 0.75, 4), (x - w * 0.6, y + h * 1.05, 2))):
        d.ellipse([bx - br - 1, by - br - 1, bx + br + 1, by + br + 1], fill=OUT)
        d.ellipse([bx - br, by - br, bx + br, by + br], fill=col)


def pop(d, x, y, mark, T, col=(255, 230, 90), f=1.0):
    """头顶冒出的符号：! ? ♪ … 汗滴"""
    if f <= 0: return
    k = pix.eback(clamp(f * 2))
    yy = y - 4 * k
    if mark == '!':
        d.rectangle([x - 1, yy - 8, x + 1, yy - 3], fill=OUT); d.rectangle([x, yy - 7, x, yy - 4], fill=col); d.point((x, yy - 1), fill=col)
    elif mark == '?':
        d.text((x - 3, yy - 12), '?', font=pix.FONT, fill=col)
    elif mark == 'sweat':
        d.polygon([(x, yy - 6), (x - 2, yy - 2), (x + 2, yy - 2)], fill=(150, 210, 255)); d.ellipse([x - 2, yy - 4, x + 2, yy], fill=(150, 210, 255))
    elif mark == '...':
        for k_ in range(3): d.rectangle([x - 5 + k_ * 4, yy - 3, x - 4 + k_ * 4, yy - 2], fill=col)


def umbrella(d, x, y, col=(240, 132, 74), col_d=(190, 90, 56), r=18):
    """撑开的伞：(x, y) 是伞柄顶端（伞尖），伞面朝下张开"""
    d.pieslice([x - r - 1, y - 1, x + r + 1, y + r * 1.2 + 1], 180, 360, fill=OUT)
    d.pieslice([x - r, y, x + r, y + r * 1.2], 180, 360, fill=col)
    for k in range(-2, 3):
        d.line([(x, y), (x + k * r / 2.5, y + r * 0.6)], fill=col_d)
    for k in range(5):
        xx = x - r + k * r / 2
        d.arc([xx, y + r * 0.6 - 3, xx + r / 2, y + r * 0.6 + 3], 0, 180, fill=col_d)
    d.line([(x, y - 3), (x, y)], fill=OUT)
