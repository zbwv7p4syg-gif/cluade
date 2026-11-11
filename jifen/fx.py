"""几分之几 · 质感：光照、云、远山、雾、光束、前景虚化、浮尘、贴地阴影、表面纹理，以及整帧的后期。

所有效果都保持像素画的样子：明暗和透明都用 Bayer 点阵分档，不用平滑的半透明。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import pix
from pix import W, H, OUT, clamp, lerp, lerpc, ease, eout, glow, tfill, blend_box, rng

LUMA = np.array([0.3, 0.59, 0.11], np.float32)
LIGHT = None      # 每个镜头开头设置：((lx, ly), 边缘光颜色)。lx, ly 是从人指向光源的方向


# ---------------------------------------------------------------- 体积感：点阵明暗和边缘光
def shade_arr(a, lx=-1.0, ly=-0.6, amt=0.34, rim=None, rim_a=0.9, dark=(36, 20, 58)):
    """a 是 RGBA 数组（会被改写）。按光的方向分四档压暗背光的一侧，迎光一侧的轮廓换成边缘光"""
    m = a[..., 3] > 0
    if not m.any(): return a
    h, w = m.shape
    ys, xs = np.nonzero(m)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    yy, xx = np.mgrid[0:h, 0:w]
    n = math.hypot(lx, ly) or 1
    u = (((xx - x0) / max(1, x1 - x0) - 0.5) * lx + ((yy - y0) / max(1, y1 - y0) - 0.5) * ly) / n
    k = np.clip((0.12 - u) * 1.6, 0, 1)
    q = np.floor(k * 3 + pix.bayer(h, w)) / 3 * amt
    f = q[..., None] * m[..., None]
    rgb = a[..., :3].astype(np.float32)
    a[..., :3] = (rgb * (1 - f) + np.array(dark, np.float32) * f).astype(np.uint8)
    if rim:
        sx = int(np.sign(lx)) if abs(lx) > 0.3 else 0
        sy = int(np.sign(ly)) if abs(ly) > 0.3 else 0
        r = np.zeros_like(m)
        if sx: r |= m & ~np.roll(m, -sx, 1)
        if sy: r |= m & ~np.roll(m, -sy, 0)
        rgb = a[..., :3].astype(np.float32)
        a[r, :3] = (rgb[r] * (1 - rim_a) + np.array(rim, np.float32) * rim_a).astype(np.uint8)
    return a


def shade_img(im, lx=-1.0, ly=-0.6, amt=0.34, rim=None, rim_a=0.9, dark=(36, 20, 58)):
    return Image.fromarray(shade_arr(np.array(im), lx, ly, amt, rim, rim_a, dark))


@lru_cache(maxsize=4096)
def lit_char(who, age, view, pose, ph, expr, arms, scarf, tint, flip, light, shade_mul):
    """带光照的角色精灵（已经按 flip 镜像），light = ((lx, ly), rim)"""
    im = pix.char_img(who, age, view, pose, ph % 4, expr, arms, scarf, tint)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    a = np.array(im)
    if shade_mul:
        a[..., :3] = np.clip(a[..., :3] * np.array(shade_mul), 0, 255).astype(np.uint8)
    if light:
        (lx, ly), rim = light
        shade_arr(a, lx, ly, 0.3, rim, 0.85)
    else:
        shade_arr(a, -0.8, -0.8, 0.22)
    return Image.fromarray(a)


def lit_layer(fn_draw, light=(-1, -0.5), amt=0.34, rim=None, key=(1, 2, 3), dark=(36, 20, 58)):
    """在透明层上画一样东西（fn_draw(img, d)），加明暗和边缘光后返回 RGBA 图"""
    lay = Image.new('RGB', (W, H), key); ld = ImageDraw.Draw(lay)
    fn_draw(lay, ld)
    a = np.array(lay)
    m = ~np.all(a == np.array(key, np.uint8), -1)
    rgba = np.dstack([a, (m * 255).astype(np.uint8)])
    shade_arr(rgba, light[0], light[1], amt, rim, 0.9, dark)
    return Image.fromarray(rgba)


# ---------------------------------------------------------------- 天空：云、远山、雾、光束
def cumulus(d, x, y, s, body, light, shade, rim=None, sun_dx=1, seed=0):
    """一团积云：底下暗、迎着太阳的一侧亮，边上一道亮边"""
    r = rng(seed)
    blobs = [(r.uniform(-1, 1) * 4 + k * 9 - 18, -r.uniform(0, 7) - (6 if 1 <= k <= 3 else 0), r.uniform(6, 10)) for k in range(5)]
    S = lambda v: v * s
    for bx, by, br in blobs:
        d.ellipse([x + S(bx - br), y + S(by - br) + S(2), x + S(bx + br), y + S(by + br) + S(2)], fill=shade)
    d.rectangle([x + S(-22), y + S(0), x + S(22), y + S(6)], fill=shade)
    for bx, by, br in blobs:
        d.ellipse([x + S(bx - br), y + S(by - br), x + S(bx + br), y + S(by + br) - S(2)], fill=body)
    for bx, by, br in blobs:
        hx = bx + br * 0.25 * sun_dx
        d.ellipse([x + S(hx - br * 0.6), y + S(by - br * 0.8), x + S(hx + br * 0.6), y + S(by + br * 0.1)], fill=light)
    if rim:
        for bx, by, br in blobs:
            a0, a1 = (280, 40) if sun_dx > 0 else (140, 260)
            d.arc([x + S(bx - br), y + S(by - br), x + S(bx + br), y + S(by + br) - S(2)], a0, a1, fill=rim)


def stratus(d, x, y, length, T, body, rim, seed=0, speed=3.0, below=True):
    """一条长长的薄云，被落日从下面照亮"""
    r = rng(seed)
    x = x + T * speed
    for k in range(int(length / 9)):
        cx = x + k * 9 + r.uniform(-3, 3); ry = r.uniform(1.5, 3.5) * (1 - abs(k / (length / 9) - 0.5) * 0.9); rx = r.uniform(7, 12)
        cx = (cx + 60) % (W + 160) - 60
        d.ellipse([cx - rx, y - ry, cx + rx, y + ry], fill=body)
    for k in range(int(length / 9)):
        cx = x + k * 9 + r.uniform(-3, 3); ry = r.uniform(1.5, 3.5) * (1 - abs(k / (length / 9) - 0.5) * 0.9); rx = r.uniform(7, 12)
        cx = (cx + 60) % (W + 160) - 60
        if below: d.arc([cx - rx, y - ry, cx + rx, y + ry], 20, 160, fill=rim)
        else: d.arc([cx - rx, y - ry, cx + rx, y + ry], 200, 340, fill=rim)


def sunset_clouds(img, d, T, sun_x, horizon, warm=1.0, seed=0, n=5, top=30):
    """落日附近的一组云：高处几团积云，地平线上几条被照亮的薄云"""
    body = lerpc((150, 110, 160), (120, 100, 170), 1 - warm)
    light = lerpc((255, 196, 170), (210, 190, 230), 1 - warm)
    shade = lerpc((118, 84, 140), (90, 80, 140), 1 - warm)
    rim = lerpc((255, 236, 190), (240, 230, 255), 1 - warm)
    r = rng(seed)
    for i in range(n):
        cx = (r.uniform(0, W) + T * r.uniform(1.5, 3)) % (W + 120) - 60
        cy = top + r.uniform(0, 50)
        cumulus(d, cx, cy, r.uniform(0.8, 1.4), body, light, shade, rim, 1 if sun_x > cx else -1, seed * 10 + i)
    for i in range(4):
        stratus(d, r.uniform(-40, W - 100), horizon - 16 - i * 13 - r.uniform(0, 6), r.uniform(80, 180), T,
                lerpc(body, (255, 160, 140), 0.3 * warm), rim, seed * 7 + i, speed=r.uniform(1, 2.5))


@lru_cache(None)
def _ridge(seed, base, amp, rough, col, snow=None):
    r = rng(seed)
    pts = [0.0, 0.0]
    n = 2
    vals = np.array([r.uniform(0, 1), r.uniform(0, 1)])
    for lvl in range(7):
        new = []
        for k in range(len(vals) - 1):
            new += [vals[k], (vals[k] + vals[k + 1]) / 2 + r.uniform(-1, 1) * rough ** lvl * 0.6]
        new.append(vals[-1]); vals = np.array(new)
    xs = np.linspace(0, W, len(vals))
    ys = base - (vals - vals.min()) / (vals.max() - vals.min() + 1e-6) * amp
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    poly = [(x, y) for x, y in zip(xs, ys)] + [(W, H), (0, H)]
    d.polygon(poly, fill=col + (255,))
    if snow:
        for x, y in zip(xs, ys):
            if y < base - amp * 0.75: d.line([(x, y), (x, y + 2)], fill=snow + (255,))
    # 迎光一侧的山脊亮一点
    light = lerpc(col, (255, 230, 200), 0.18)
    for k in range(len(xs) - 1):
        if ys[k + 1] < ys[k]: d.line([(xs[k], ys[k]), (xs[k + 1], ys[k + 1])], fill=light + (255,))
    return im


def mountains(img, base, layers):
    """远山：layers = [(seed, 高度, 粗糙度, 颜色), ...]，从远到近"""
    for i, (seed, amp, rough, col) in enumerate(layers):
        im = _ridge(seed, int(base), int(amp), rough, tuple(col))
        img.paste(im, (0, 0), im)


def haze(img, y, h, col, a=0.5):
    """地平线上的一层薄雾，中间最浓"""
    y0, y1 = int(max(0, y - h)), int(min(H, y + h))
    if y1 <= y0: return
    ys = np.arange(y0, y1)
    prof = np.exp(-((ys - y) / (h * 0.5)) ** 2) * a
    blend_box(img, (0, y0, W, y1), col, np.repeat(prof[:, None], W, 1), levels=6)


def godrays(img, x, y, T, n=10, col=(255, 236, 190), a=0.07, spread=math.pi, center=-math.pi / 2, length=520, width=0.05, pulse=0.0):
    """从光源射出的光束，慢慢转"""
    for k in range(n):
        ang = center - spread / 2 + spread * (k + 0.5) / n + 0.05 * math.sin(T * 0.3 + k)
        w = width * (0.6 + 0.8 * ((k * 37) % 10) / 10)
        aa = a * (0.6 + 0.4 * math.sin(T * 0.7 + k * 1.7)) + pulse
        tfill(img, 'polygon', [(x, y), (x + math.cos(ang - w) * length, y + math.sin(ang - w) * length),
                                (x + math.cos(ang + w) * length, y + math.sin(ang + w) * length)], col, aa)


def flare(img, sx, sy, a=0.25, tx=None, ty=None, col=(255, 236, 200)):
    """镜头光晕：从光源往画面中心方向排一串光圈"""
    tx = W - sx if tx is None else tx; ty = H - sy if ty is None else ty
    for i, (u, r) in enumerate(((0.3, 4), (0.45, 9), (0.6, 5), (0.8, 14), (1.0, 7))):
        glow(img, lerp(sx, tx, u), lerp(sy, ty, u), r, col, a * (0.6 + 0.4 * (i % 2)))


# ---------------------------------------------------------------- 前景虚化、浮尘、贴地阴影
def fg(img, T, kind='grass', col=(46, 30, 40), rim=(255, 200, 120), sides=(0, 1), scale=3, seed=0, h=1.0, wind=1.0):
    """画面角落里离镜头很近的东西：用 scale 倍的大像素画，暗色剪影带一点边缘光，像失焦的前景"""
    w, hh = W // scale + 2, H // scale + 2
    lay = Image.new('RGBA', (w, hh)); d = ImageDraw.Draw(lay)
    r = rng(seed)
    for side in sides:
        x0 = 0 if side == 0 else w
        sg = 1 if side == 0 else -1
        if kind in ('grass', 'wheat'):
            for k in range(16):
                bx = x0 + sg * r.uniform(-2, 42)
                bh = r.uniform(10, 34) * h * (1 - abs(bx - x0) / 60)
                lean = r.uniform(-4, 8) * sg + math.sin(T * 1.6 + k) * 1.6 * wind
                pts = [(bx + lean * (j / 6) ** 2, hh - bh * j / 6) for j in range(7)]
                c = lerpc(col, rim, 0.25 if k % 3 == 0 else 0)
                d.line(pts, fill=c + (255,), width=2 if k % 2 else 1)
                if kind == 'wheat' and k % 2 == 0:
                    tx, ty = pts[-1]
                    d.ellipse([tx - 1.5, ty - 4, tx + 1.5, ty + 1], fill=lerpc(col, rim, 0.5) + (255,))
                    d.point((tx + sg, ty - 2), fill=rim + (255,))
        elif kind == 'leaves':
            # 一簇失焦的树叶：每片叶子是一个两头尖的多边形，朝各个方向
            cx0, cy0 = (x0 + sg * 6, 2)
            d.line([(x0 - sg * 4, -4), (x0 + sg * 34, 14)], fill=lerpc(col, (0, 0, 0), 0.35) + (255,), width=2)
            for k in range(18):
                u = r.uniform(0, 1)
                bx = x0 + sg * (u * 34) + r.uniform(-4, 4)
                by = -4 + u * 18 + r.uniform(-6, 8)
                ang = r.uniform(0, 2 * math.pi) + math.sin(T * 1.1 + k) * 0.08 * wind
                ln = r.uniform(7, 12); wd = ln * 0.38
                ca, sa = math.cos(ang), math.sin(ang)
                pts = [(bx, by), (bx + ca * ln * 0.5 - sa * wd, by + sa * ln * 0.5 + ca * wd), (bx + ca * ln, by + sa * ln),
                       (bx + ca * ln * 0.5 + sa * wd, by + sa * ln * 0.5 - ca * wd)]
                c = lerpc(col, (0, 0, 0), 0.15 * (k % 3))
                d.polygon(pts, fill=c + (255,))
                d.line([pts[1], pts[2]], fill=lerpc(col, rim, 0.4) + (255,))
        elif kind == 'flowers':
            for k in range(7):
                bx = x0 + sg * r.uniform(2, 40); by = hh - r.uniform(4, 22)
                d.line([(bx, hh), (bx + math.sin(T + k) * wind, by)], fill=col + (255,))
                c = r.choice(((255, 150, 170), (255, 220, 120), (250, 250, 255)))
                d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=lerpc(c, col, 0.35) + (255,))
    big = lay.resize((w * scale, hh * scale), Image.NEAREST)
    img.paste(big, (0, 0), big)


def motes(img, d, T, n=30, box=(0, 0, W, H), col=(255, 240, 200), seed=0, drift=(4, -3), glow_a=0.25):
    """阳光里的浮尘、花粉：慢慢漂，一闪一闪"""
    x0, y0, x1, y1 = box
    for i in range(n):
        r = rng(i * 13 + seed)
        x = x0 + (r.uniform(0, x1 - x0) + T * drift[0] * r.uniform(0.5, 1.5) + 6 * math.sin(T * 0.7 + i)) % (x1 - x0)
        y = y0 + (r.uniform(0, y1 - y0) + T * drift[1] * r.uniform(0.5, 1.5) + 4 * math.cos(T * 0.6 + i * 2)) % (y1 - y0)
        b = 0.5 + 0.5 * math.sin(T * r.uniform(1.5, 3.5) + i)
        if b < 0.3: continue
        if i % 5 == 0 and glow_a > 0: glow(img, x, y, 4, col, glow_a * b)
        d.point((x, y), fill=lerpc(lerpc(col, (0, 0, 0), 0.4), col, b))
        if i % 7 == 0 and b > 0.8: d.point([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], fill=lerpc(col, (0, 0, 0), 0.3))


def contact(img, x, y, w, a=0.35, col=(30, 18, 40), h=None):
    """人或东西脚下的一小团影子"""
    h = h or max(2, w * 0.22)
    x0, y0, x1, y1 = int(x - w), int(y - h), int(x + w) + 1, int(y + h) + 1
    x0c, y0c, x1c, y1c = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1c <= x0c or y1c <= y0c: return
    yy, xx = np.mgrid[y0c:y1c, x0c:x1c]
    al = np.clip(1 - ((xx - x) / w) ** 2 - ((yy - y) / h) ** 2, 0, 1) ** 0.7 * a
    blend_box(img, (x0c, y0c, x1c, y1c), col, al, levels=5)


@lru_cache(None)
def _noise(w, h, seed, scale):
    r = np.random.default_rng(seed)
    n = r.integers(-1, 2, (h // scale + 1, w // scale + 1)).repeat(scale, 0).repeat(scale, 1)[:h, :w]
    return n.astype(np.int16)


def tex(img, box, amt=6, seed=0, scale=1):
    """给一块平的颜色加一点静态的颗粒（墙面、地面、纸）"""
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 <= x0 or y1 <= y0: return
    a = np.asarray(img.crop((x0, y0, x1, y1)), np.int16)
    n = _noise(x1 - x0, y1 - y0, seed, scale)[..., None] * amt
    img.paste(Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8)), (x0, y0))


# ---------------------------------------------------------------- 整帧的后期
YY, XX = np.mgrid[0:H, 0:W]
_VIG = np.clip(((XX - W / 2) / (W * 0.6)) ** 2 + ((YY - H / 2) / (H * 0.62)) ** 2 - 0.35, 0, 1)


def post(img, bloom=0.45, grade=1.0, vig=0.3, shadow=(30, 16, 60), warm=(1.03, 1.0, 0.95)):
    """泛光（亮处往外渗光，用点阵分档）、阴影偏紫的分离色调、暗角"""
    a = np.asarray(img).astype(np.float32)
    lum = a @ LUMA
    if bloom > 0:
        m = np.clip((lum - 150) / 105, 0, 1) ** 1.5
        src = Image.fromarray((a * m[..., None]).astype(np.uint8))
        sm = src.resize((W // 4, H // 4), Image.BOX).filter(ImageFilter.GaussianBlur(2.4))
        b = np.asarray(sm.resize((W, H), Image.BILINEAR), np.float32) * bloom
        b = np.floor(b / 10 + pix.BAYER[..., None]) * 10
        a = 255 - (255 - a) * (255 - np.clip(b, 0, 255)) / 255
        lum = a @ LUMA
    if grade > 0:
        l = (lum / 255)[..., None]
        s = (1 - l) ** 2.2 * 0.22 * grade
        a = a * (1 - s) + np.array(shadow, np.float32) * s
        hk = l ** 2 * grade
        a = a * (1 + (np.array(warm, np.float32) - 1) * hk)
    if vig > 0:
        v = np.floor(_VIG * vig * 6 + pix.BAYER) / 6
        a = a * (1 - v[..., None] * 0.9) + np.array((10, 6, 24), np.float32) * v[..., None] * 0.9
    img.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))


SC = 4
_ROW = np.array([256, 256, 250, 226], np.int32)
_COL = np.array([256, 256, 256, 244], np.int32)
_SCAN = (np.tile(_ROW, H)[:, None, None] * np.tile(_COL, W)[None, :, None]) >> 8


_GRAIN = np.random.default_rng(7).integers(-4, 5, (H * SC // 2, W * SC // 2, 1), dtype=np.int32).repeat(2, 0).repeat(2, 1)


def upscale(arr, fi):
    """最近邻放大 4 倍，每 4 行最后一行稍暗（扫描线），再叠一层固定的细颗粒，像隔着一块旧屏幕看"""
    big = np.repeat(np.repeat(arr, SC, 0), SC, 1).astype(np.int32)
    big = ((big * _SCAN) >> 8) + _GRAIN
    return np.clip(big, 0, 255).astype(np.uint8)
