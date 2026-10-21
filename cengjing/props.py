"""曾经是情侣 · 道具：两人之间的红线、雨伞、纸船、风筝、孔明灯、沙漏、云朵片名、拍立得、录像带倒带和老照片的调色。

红线是全片的主线：片头它勾出一颗心，相遇时它系在两人的小指上，分头走时被越拉越长，分离时绷断，最后断掉的一截顺着河漂走。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
from pix import (W, H, FONT, FONT_S, OUT, SKIN, SKIN_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box,
                 paste, outline, text, rng, sky, stars, rain, city, lamp, with_alpha, heart_poly)

RED, RED_L, RED_D = (230, 40, 66), (255, 136, 150), (150, 20, 44)
CORAL, CORAL_S = (240, 106, 98), (198, 72, 76)
DENIM = (92, 140, 208)
PINK, PINK_L = (255, 150, 176), (255, 214, 224)
GOLD, GOLD_L = (255, 200, 92), (255, 238, 170)
CYAN = (110, 220, 255)
CREAM = (255, 246, 232)
INK = (12, 8, 26)
NIGHT = ((0, (8, 8, 28)), (0.55, (24, 22, 62)), (1, (62, 46, 104)))
SUNSET = ((0, (64, 66, 148)), (0.38, (178, 104, 160)), (0.7, (250, 150, 130)), (1, (255, 214, 150)))
STORM = ((0, (16, 14, 32)), (0.38, (40, 34, 64)), (0.7, (62, 56, 86)), (1, (86, 80, 104)))


def mix_stops(a, b, f, q=24):
    """两套天空渐变按 f 混合（f 量化成 q 档，好让渐变图能缓存）"""
    f = round(clamp(f) * q) / q
    return tuple((pa, lerpc(ca, cb, f)) for (pa, ca), (pb, cb) in zip(a, b))


# ---------------------------------------------------------------- 节拍
def beats_in(t0, t1):
    b = pix.AUDIO['beats']
    return [float(x) for x in b if t0 <= x < t1]


def last_beat(T):
    b = pix.AUDIO['beats']
    i = int(np.searchsorted(b, T, 'right')) - 1
    return float(b[i]) if i >= 0 else -9.0


def beat_after(T, n=1):
    bs = [x for x in pix.AUDIO['beats'] if x > T + 0.05]
    return float(bs[n - 1]) if len(bs) >= n else T + 1.1 * n


def bar_near(T, tol=0.6):
    b = pix.AUDIO['bars']
    if len(b) == 0: return T
    x = b[int(np.argmin(np.abs(b - T)))]
    return float(x) if abs(x - T) < tol else T


def thump(T, decay=0.25):
    """拍点上的一下心跳：1 → 0"""
    return pix.pulse(T, decay)


# ---------------------------------------------------------------- 角色（任意倍数）
def person_s(img, who, x, y, sc, age='young', view='side', pose='stand', ph=0, expr='smile', arms='auto', flip=False, alpha=1.0,
             shade=None, tint=None):
    """和 pix.person 一样，但可以按小数倍缩放（远处的人）"""
    if abs(sc - round(sc)) < 1e-3 and sc >= 1:
        pix.person(img, who, x, y, age, view, pose, ph, expr, arms, int(round(sc)), flip, None, tint, alpha, shade); return
    im = pix.char_img(who, age, view, pose, ph % 4, expr, arms, None, tint)
    if shade:
        a = np.array(im); a[..., :3] = np.clip(a[..., :3] * np.array(shade), 0, 255).astype(np.uint8); im = Image.fromarray(a)
    ax = pix.CX
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT); ax = pix.CW - 1 - pix.CX
    w, h = max(1, int(round(pix.CW * sc))), max(1, int(round(pix.CH * sc)))
    im = im.resize((w, h), Image.NEAREST)
    if alpha < 1: im = with_alpha(im, alpha)
    img.paste(im, (int(round(x - ax * sc)), int(round(y - pix.FY * sc))), im)


def hand_pos(x, y, s=1, view='side', flip=False, arms='down', who='boy'):
    """角色手的大概位置（画红线用）"""
    sh = y - 15 * s
    if view == 'side':
        dx = {'hold': -4, 'hold_f': 4, 'reach': 7}.get(arms, 1)
        dy = {'reach': 2}.get(arms, 5)
        return (x + (-dx if flip else dx) * s, sh + dy * s)
    dx = {'hold_l': -10, 'hold_r': 8}.get(arms, -6)
    return (x + dx * s, sh + 5 * s)


# ---------------------------------------------------------------- 红线
def bez(p0, p1, c, n=24):
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * c[0] + u * u * p1[0], (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * c[1] + u * u * p1[1])
            for u in (i / n for i in range(n + 1))]


def thread(img, d, p0, p1, sag=10, col=RED, w=1, glow_a=0.0, wob=0.0, T=0.0, n=None, upto=1.0):
    """两点之间垂下来的红线。wob 是抖动幅度；upto < 1 时只画前面一段（画线的动画）"""
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + sag
    if wob: mx += wob * math.sin(T * 9); my += wob * math.cos(T * 7)
    n = n or max(8, int(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / 3))
    pts = bez(p0, p1, (mx, my), n)
    pts = pts[:max(2, int(len(pts) * clamp(upto)))]
    if glow_a > 0:
        for x, y in pts[::4]: glow(img, x, y, 6, col, glow_a * 0.5)
    d.line(pts, fill=col, width=w)
    if w == 1:
        d.line([(x, y + 1) for x, y in pts], fill=lerpc(col, (0, 0, 0), 0.45))
        d.line(pts, fill=col)
    return pts


def heart(img, d, cx, cy, s, col=RED, hi=RED_L, out=OUT, glow_a=0.0):
    if glow_a > 0: glow(img, cx, cy, 30 * s, col, glow_a)
    if out: d.polygon(heart_poly(cx, cy + 0.5, s * 1.12), fill=out)
    d.polygon(heart_poly(cx, cy, s), fill=col)
    if hi and s >= 0.5:
        d.ellipse([cx - 9 * s, cy - 7 * s, cx - 5 * s, cy - 3 * s], fill=hi)


# ---------------------------------------------------------------- 雨伞
def umbrella(d, x, y, r, col, col_s=None, tilt=0.0, stick=None, open_=1.0, edge=OUT, tip=True, handle=True):
    """(x, y) 是伞骨中心（伞面下沿的中点），r 是半径；tilt 是倾斜（弧度，往右为正）"""
    col_s = col_s or lerpc(col, (0, 0, 0), 0.28)
    rx = r * (0.35 + 0.65 * open_); ry = r * 0.62
    ca, sa = math.cos(tilt), math.sin(tilt)

    def R(px, py): return (x + px * ca - py * sa, y + px * sa + py * ca)
    top = [R(rx * math.cos(a), -ry * math.sin(a)) for a in np.linspace(0, math.pi, 22)]
    scal = []
    nsc = 5
    for k in range(nsc):
        ax0 = rx - 2 * rx * k / nsc; ax1 = rx - 2 * rx * (k + 1) / nsc
        for u in np.linspace(0, 1, 5)[1:]:
            px = lerp(ax0, ax1, u); scal.append(R(px, -2.5 * math.sin(math.pi * u)))
    poly = top + scal
    d.polygon([(px + 0.5, py + 1) for px, py in poly], fill=edge)
    d.polygon(poly, fill=col)
    for k in range(1, nsc):                               # 伞骨
        px = rx - 2 * rx * k / nsc
        a = math.acos(clamp(px / rx, -1, 1))
        d.line([R(0, -ry), R(px * 0.98, -ry * math.sin(a) * 0.15 - 1)], fill=col_s)
    hx, hy = R(-rx * 0.3, -ry * 0.7)
    d.point((hx, hy), fill=lerpc(col, (255, 255, 255), 0.45))
    if tip: d.line([R(0, -ry), R(0, -ry - 3)], fill=edge)
    if handle:
        L = stick if stick is not None else r * 1.15
        bx, by = R(0, L)
        d.line([R(0, -ry + 1), (bx, by)], fill=(70, 60, 70))
        hx2, hy2 = R(-2, L + 2)
        d.line([(bx, by), (bx, by + 1), (hx2, hy2)], fill=(70, 60, 70))


# ---------------------------------------------------------------- 纸船、风筝、孔明灯、玫瑰
def paper_boat(d, x, y, s=1, col=CREAM, sh=(206, 196, 186), edge=OUT, bob=0.0):
    """(x, y) 是船底中点"""
    y = y + bob
    hull = [(x - 9 * s, y - 4 * s), (x + 9 * s, y - 4 * s), (x + 6 * s, y), (x - 6 * s, y)]
    sail = [(x - 5 * s, y - 4 * s), (x, y - 11 * s), (x + 5 * s, y - 4 * s)]
    d.polygon([(px, py + 1) for px, py in hull], fill=edge)
    d.polygon(sail, fill=sh); d.polygon([(x, y - 11 * s), (x + 5 * s, y - 4 * s), (x, y - 4 * s)], fill=col)
    d.polygon(hull, fill=col)
    d.line([(x - 6 * s, y), (x + 6 * s, y)], fill=sh)
    d.line(sail[:2], fill=edge); d.line(sail[1:], fill=edge)


def kite(d, x, y, s, T, col=RED, col2=GOLD_L, tail=True):
    """菱形风筝，(x, y) 是中心；返回拴线的点"""
    sw = math.sin(T * 3.1) * 0.15
    pts = [(x, y - 9 * s), (x + 6 * s, y - 1 * s), (x, y + 10 * s), (x - 6 * s, y - 1 * s)]
    pts = [(x + (px - x) * math.cos(sw) - (py - y) * math.sin(sw), y + (px - x) * math.sin(sw) + (py - y) * math.cos(sw)) for px, py in pts]
    d.polygon([(px + 1, py + 1) for px, py in pts], fill=OUT)
    d.polygon(pts, fill=col)
    d.polygon([pts[0], pts[1], (x, y)], fill=col2); d.polygon([pts[2], pts[3], (x, y)], fill=col2)
    d.line([pts[0], pts[2]], fill=OUT); d.line([pts[1], pts[3]], fill=OUT)
    if tail:
        tx, ty = pts[2]
        prev = (tx, ty)
        for k in range(1, 9):
            px = tx - k * 3 * s + math.sin(T * 6 + k * 0.9) * 2.5 * s; py = ty + k * 2.6 * s
            d.line([prev, (px, py)], fill=OUT); prev = (px, py)
            if k % 3 == 0: d.rectangle([px - 1, py - 1, px + 1, py + 1], fill=[RED, GOLD, PINK][k // 3 % 3])
    return pts[2]


def lantern(img, d, x, y, s=1.0, flick=1.0, col=(255, 170, 80), body=(255, 214, 150), heart_shape=False, glow_r=None):
    """孔明灯，(x, y) 是中心"""
    g = glow_r if glow_r is not None else 14 * s
    if g > 0: glow(img, x, y, g, col, 0.45 * flick)
    if heart_shape:
        heart(img, d, x, y - 2 * s, 0.45 * s, lerpc(RED, (255, 120, 110), flick * 0.5), (255, 200, 190), out=None)
        d.ellipse([x - 2 * s, y - 2 * s, x + 2 * s, y + 2 * s], fill=lerpc((255, 160, 120), (255, 250, 220), flick))
        return
    d.rounded_rectangle([x - 4 * s, y - 6 * s, x + 4 * s, y + 5 * s], max(1, int(2 * s)), fill=lerpc(col, body, flick))
    d.rectangle([x - 3 * s, y + 4 * s, x + 3 * s, y + 5 * s], fill=lerpc(col, (255, 250, 230), flick))
    if s >= 1.5: d.line([(x, y - 6 * s), (x, y + 4 * s)], fill=lerpc(col, (200, 110, 60), 0.4))


def rose(d, x, y, wilt=0.0, col=(214, 30, 60), stem=(70, 130, 70), petals=1.0, s=1):
    """玫瑰：(x, y) 是茎的底部；wilt 0..1 花头往下垂、颜色发暗"""
    c = lerpc(col, (98, 40, 50), wilt)
    st = lerpc(stem, (110, 104, 70), wilt)
    top = (x + 10 * wilt * s, y - (30 - 12 * wilt) * s)
    pts = bez((x, y), top, (x, y - 26 * s), 12)
    d.line(pts, fill=st, width=max(1, s))
    d.polygon([(x, y - 12 * s), (x - 6 * s, y - 16 * s), (x - 1, y - 14 * s)], fill=st)
    if petals <= 0: return top
    hx, hy = top
    r = 4 * s * (0.6 + 0.4 * petals)
    d.ellipse([hx - r, hy - r - 2 * s * (1 - wilt), hx + r, hy + r - 2 * s * (1 - wilt)], fill=c)
    d.arc([hx - r + 1, hy - r - 1, hx + r - 1, hy + r - 2], 200, 340, fill=lerpc(c, (255, 200, 210), 0.4))
    d.line([(hx - 1, hy - 1), (hx + 1, hy - 2)], fill=lerpc(c, (60, 10, 20), 0.5))
    return top


# ---------------------------------------------------------------- 片名
@lru_cache(None)
def big_glyph(ch, scale=3, top=(255, 255, 255), bot=PINK, line=(210, 70, 96), out=(56, 22, 50), font=None):
    font = font or FONT
    w = int(font.getlength(ch)) + 8; h = font.size + 8
    m = Image.new('L', (w, h)); md = ImageDraw.Draw(m); md.fontmode = '1'
    md.text((4, 3), ch, font=font, fill=255)
    mk = np.array(m) > 0
    a = np.zeros((h, w, 4), np.uint8)
    for y in range(h): a[y, :, :3] = lerpc(top, bot, (y - 4) / (font.size - 1))
    a[..., 3] = mk * 255
    im = outline(outline(Image.fromarray(a), line), out)
    sh = Image.new('RGBA', (w + 1, h + 1))
    shadow = np.array(im); shadow[shadow[..., 3] > 0, :3] = out
    sh.paste(Image.fromarray(shadow), (1, 1)); sh.alpha_composite(im)
    return sh.resize((sh.width * scale, sh.height * scale), Image.NEAREST)


@lru_cache(None)
def cloud_glyph(ch, scale=4):
    """云朵写成的字：笔画加粗成一团团的白云，下沿带一点粉色的阴影"""
    w = int(FONT.getlength(ch)) + 10; h = FONT.size + 10
    m = Image.new('L', (w, h)); md = ImageDraw.Draw(m); md.fontmode = '1'
    md.text((5, 4), ch, font=FONT, fill=255)
    mk = np.array(m) > 0
    fat = mk.copy()
    fat[1:] |= mk[:-1]; fat[:, 1:] |= mk[:, :-1]
    a = np.zeros((h, w, 4), np.uint8)
    a[fat] = (238, 222, 236, 255)
    a[mk] = (255, 252, 250, 255)
    lo = fat & ~np.roll(fat, -1, 0)
    a[lo] = (236, 170, 186, 255)
    im = Image.fromarray(a).resize((w * scale, h * scale), Image.NEAREST)
    return im


def title_str():
    return pix.META.get('ti') or '曾经是情侣'


def artist_str():
    return pix.META.get('ar') or ''


def title_layout(scale, gap=0):
    s = title_str()
    adv = [FONT.getlength(c) * scale + gap for c in s]
    return s, adv, sum(adv)


def big_text(img, s, cx, cy, scale, top=(255, 255, 255), bot=PINK, alpha=1.0, gap=0, line=(210, 70, 96), out=(56, 22, 50)):
    gl = [big_glyph(c, scale, top, bot, line, out) for c in s]
    adv = [FONT.getlength(c) * scale + gap for c in s]
    x = cx - sum(adv) / 2 - 4 * scale
    for g, a in zip(gl, adv):
        paste(img, g, x, cy - g.height / 2, alpha, 'lt')
        x += a


@lru_cache(None)
def glyph_pixels(s, scale):
    """片名每个像素点的位置（用来做粒子汇聚），按字分组"""
    out = []
    x = 0
    for ch in s:
        m = Image.new('L', (int(FONT.getlength(ch)) + 4, FONT.size + 4)); md = ImageDraw.Draw(m); md.fontmode = '1'
        md.text((2, 1), ch, font=FONT, fill=255)
        ys, xs = np.nonzero(np.array(m))
        out.append([(x + (px - 2) * scale, (py - 1) * scale) for px, py in zip(xs, ys)])
        x += FONT.getlength(ch) * scale
    return out, x


# ---------------------------------------------------------------- 拍立得、相框
def polaroid(img, d, cx, cy, photo, f=1.0, alpha=1.0, rot=0, frame=CREAM):
    """拍立得：photo 是 RGB 图，f 从 0 到 1 显影"""
    if alpha <= 0: return
    pw, ph = photo.size
    im = Image.new('RGBA', (pw + 8, ph + 18), frame + (255,))
    p = photo
    if f < 1:
        a = np.asarray(p, float); g = a @ np.array([0.3, 0.59, 0.11])
        dev = np.clip(f * 1.4, 0, 1)
        a = (a * dev + (g[..., None] * 0.3 + 40) * (1 - dev)) * (0.4 + 0.6 * dev)
        p = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    im.paste(p, (4, 4))
    im = outline(im, OUT)
    if rot: im = im.rotate(rot, resample=Image.NEAREST, expand=True)
    paste(img, im, cx, cy, alpha, 'cc')


def shrink(im, w, h):
    """把整帧缩成小图：按块取平均，保留像素感"""
    return im.resize((w, h), Image.BOX)


# ---------------------------------------------------------------- 调色
def sepia(im, k=1.0, warm=(1.08, 0.94, 0.74)):
    a = np.asarray(im, float)
    g = a @ np.array([0.3, 0.59, 0.11])
    s = np.stack([g * warm[0], g * warm[1], g * warm[2]], -1) + np.array([18, 10, 0])
    a = a * (1 - k) + s * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def gray_except(img, keep_mask, k=1.0, tint=(0.92, 0.95, 1.05)):
    """除 keep_mask 外的地方变灰"""
    a = np.asarray(img, float)
    g = (a @ np.array([0.3, 0.59, 0.11]))[..., None] * np.array(tint)
    out = np.where(keep_mask[..., None], a, a * (1 - k) + g * k)
    img.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)))


def grain(img, T, a=10, seed=0):
    r = np.random.default_rng(int(T * 30) * 7 + seed)
    n = r.integers(-a, a + 1, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    arr = np.asarray(img, np.int16) + n
    img.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)))


def vhs(img, T, k=1.0, seed=0):
    """录像带：横向错位的跟踪条、红蓝错色、扫描线"""
    a = np.asarray(img).copy()
    r = np.random.default_rng(int(T * 30) + seed)
    band = int((T * 140) % (H + 40)) - 20
    for y in range(max(0, band), min(H, band + 14)):
        a[y] = np.roll(a[y], int(r.integers(4, 14) * k), axis=0)
        a[y] = np.clip(a[y].astype(int) + 40, 0, 255)
    for _ in range(int(6 * k)):
        y = int(r.integers(0, H)); a[y] = np.roll(a[y], int(r.integers(-6, 7)), axis=0)
    out = a.copy()
    out[..., 0] = np.roll(a[..., 0], 2, axis=1); out[..., 2] = np.roll(a[..., 2], -2, axis=1)
    out[::2] = (out[::2].astype(int) * 0.82).astype(np.uint8)
    img.paste(Image.fromarray(out))


# ---------------------------------------------------------------- 手
def hand_blob(d, x, y, s, col=SKIN, sh=SKIN_S, fingers=4, flip=False, thumb=True):
    """手背朝外的大手（特写用）：(x, y) 是手腕中心，手指朝上"""
    k = -1 if flip else 1
    d.rounded_rectangle([x - 6 * s, y - 12 * s, x + 6 * s, y], 3 * s, fill=col)
    for i in range(fingers):
        fx = x - 5 * s + i * 3 * s
        fl = [7, 9, 8, 6][i] * s
        d.rounded_rectangle([fx, y - 12 * s - fl, fx + 2 * s, y - 10 * s], s, fill=col)
        d.line([(fx + 2 * s, y - 12 * s - fl + s), (fx + 2 * s, y - 11 * s)], fill=sh)
    if thumb:
        tx = x + k * 6 * s
        d.polygon([(tx, y - 4 * s), (tx + k * 5 * s, y - 9 * s), (tx + k * 6 * s, y - 7 * s), (tx + k * 1 * s, y - 1 * s)], fill=col)
    d.line([(x - 6 * s, y - 2 * s), (x + 6 * s, y - 2 * s)], fill=sh)


def fist_pinky(d, x, y, s, flip=False, sleeve=DENIM, col=SKIN, sh=SKIN_S):
    """侧面伸出小指的拳头（特写勾小指用）：(x, y) 是小指指尖；flip=True 时手从右边伸过来"""
    k = -1 if flip else 1
    bx = x - k * 6 * s
    d.rectangle([bx - k * 22 * s, y - 6 * s, bx - k * 9 * s, y + 9 * s] if not flip else [bx + 9 * s, y - 6 * s, bx + 22 * s, y + 9 * s], fill=sleeve)
    d.rounded_rectangle([min(bx - k * 10 * s, bx), y - 5 * s, max(bx - k * 10 * s, bx), y + 8 * s], 3 * s, fill=col)
    for j in range(3):
        fy = y - 3 * s + j * 4 * s
        d.line([(bx - k * 2 * s, fy), (bx, fy)], fill=sh)
    d.rounded_rectangle([min(bx, x), y - 1 * s, max(bx, x), y + 1 * s], s, fill=col)
    d.point((x, y), fill=sh)


# ---------------------------------------------------------------- 通用小效果
def shake(img, k, amp_, dur):
    if not 0 <= k < dur: return
    a = amp_ * (1 - k / dur)
    dx, dy = round(a * math.sin(k * 97)), round(a * math.cos(k * 71))
    if dx or dy:
        src = img.copy(); img.paste((8, 6, 20), (0, 0, W, H)); img.paste(src, (dx, dy))


@lru_cache(None)
def head_img(who, age='young', expr='smile', s=1, view='front'):
    im = pix.char_img(who, age, view, 'stand', 0, expr)
    return im.crop((pix.CX - 8, pix.FY - 31, pix.CX + 8, pix.FY - 13)).resize((16 * s, 18 * s), Image.NEAREST)


_RB = rng(5)
BURST = [(_RB.uniform(0, 2 * math.pi), _RB.uniform(60, 180), i % 4, [RED, GOLD_L, (255, 255, 255), PINK][i % 4]) for i in range(56)]


def burst(img, d, k, cx, cy, parts=BURST, life=1.2, scale=1.0):
    if not 0 <= k < life: return
    u = k / life
    for ang, sp, kind, col in parts:
        dist = (6 + sp * eout(u)) * scale
        x = cx + math.cos(ang) * dist; y = cy + math.sin(ang) * dist * 0.8 + 20 * u * u * scale
        c = lerpc(col, (30, 20, 50), u)
        if kind == 0: pix.put(img, 'heart', x, y, 1, tint=col, alpha=1 - u)
        elif kind == 1: pix.twinkle(d, int(x), int(y), 1 - u * 0.8, c, 3)
        else: d.rectangle([x, y, x + 1, y + 1], fill=c)


BOKEH_COLS = [GOLD, PINK, CYAN, (160, 130, 255), (255, 220, 170)]


def bokeh(img, T, n=14, cols=BOKEH_COLS, seed=0, a=0.3, rmin=8, rmax=22, drift=6, box=(0, 0, W, H)):
    """虚焦的光斑，慢慢漂"""
    x0, y0, x1, y1 = box
    for i in range(n):
        r = rng(i * 17 + seed)
        x = x0 + (r.uniform(0, x1 - x0) + T * drift * r.uniform(-1, 1)) % (x1 - x0)
        y = y0 + r.uniform(0, y1 - y0) + 4 * math.sin(T * 0.7 + i)
        rad = r.uniform(rmin, rmax)
        glow(img, x, y, rad, cols[i % len(cols)], a * (0.6 + 0.4 * math.sin(T * 1.3 + i * 2)), power=0.7)


def notes(img, d, T, n=10, box=(0, 0, W, H), seed=0, cols=(PINK_L, GOLD_L, (200, 230, 255)), speed=18):
    """飘起来的音符"""
    x0, y0, x1, y1 = box
    hh = y1 - y0
    for i in range(n):
        r = rng(i * 23 + seed)
        y = y1 - (T * speed * r.uniform(0.7, 1.3) + r.uniform(0, hh)) % hh
        x = x0 + r.uniform(0, x1 - x0) + 6 * math.sin(T * 1.6 + i)
        f = (y1 - y) / hh
        a = clamp(min(f * 4, (1 - f) * 3))
        pix.put(img, 'note', x, y, 1 + (i % 3 == 0), tint=cols[i % len(cols)], alpha=a)


# ---------------------------------------------------------------- 雨、倒影
def reflect(img, y0, h, t, tint=(14, 12, 40), a=0.5, amp=2.0, src_h=None):
    """水面/湿地面：把 y0 以上的画面倒过来贴到下面，每行左右抖一点，再压一层颜色"""
    src_h = src_h or h
    arr = np.asarray(img)
    top = arr[max(0, y0 - src_h):y0][::-1]
    n = min(h, len(top), H - y0)
    if n <= 0: return
    out = top[:n].copy()
    for r in range(n):
        sh = int(round(amp * math.sin(t * 3 + r * 0.7) * (0.3 + r / n)))
        if sh: out[r] = np.roll(out[r], sh, axis=0)
    under = arr[y0:y0 + n].astype(float)
    k = np.linspace(0.55, 0.15, n)[:, None, None] * a / 0.5
    al = np.clip(np.floor(k * 6 + pix.bayer(n, W, 0, y0)[..., None]) / 6, 0, 1)
    mix = under * (1 - al) + (out.astype(float) * 0.75 + np.array(tint) * 0.25) * al
    img.paste(Image.fromarray(mix.round().astype(np.uint8)), (0, y0))


def splashes(d, t, y0, y1, n, col=(150, 170, 230), seed=0, x0=0, x1=W):
    """雨点打在地上的小水花"""
    for i in range(n):
        r = rng(i * 13 + seed)
        per = 0.5 + r.random() * 0.4
        k = ((t + r.random() * per) % per) / per
        if k > 0.45: continue
        x = r.uniform(x0, x1); y = r.uniform(y0, y1)
        s = 1 + int(k * 6)
        d.point([(x - s, y), (x + s, y)], fill=col)
        if k < 0.2: d.point((x, y - 1), fill=col)


def ripples(d, t, box, n, col, seed=0, per=1.2, rmax=8):
    """水面上一圈圈扩散的涟漪"""
    x0, y0, x1, y1 = box
    for i in range(n):
        r = rng(i * 31 + seed)
        p = per * r.uniform(0.7, 1.3)
        k = ((t + r.random() * p) % p) / p
        x = r.uniform(x0, x1); y = r.uniform(y0, y1)
        rr = 1 + k * rmax
        d.ellipse([x - rr, y - rr * 0.4, x + rr, y + rr * 0.4], outline=lerpc(col, (0, 0, 0), k * 0.8))


def drops_on_glass(img, d, t, box, n=40, seed=0, col=(180, 200, 255)):
    """玻璃上的雨珠，慢慢往下滑"""
    x0, y0, x1, y1 = box
    for i in range(n):
        r = rng(i * 7 + seed)
        sp = r.uniform(4, 30)
        x = r.uniform(x0, x1); y = y0 + (r.uniform(0, y1 - y0) + t * sp) % (y1 - y0)
        d.point((x, y), fill=col)
        if sp > 18: d.line([(x, y - 3), (x, y - 1)], fill=lerpc(col, (40, 40, 80), 0.6))
        if i % 3 == 0: d.point((x + 1, y), fill=lerpc(col, (255, 255, 255), 0.5))


SNAP = None    # render.py 填入：SNAP(T) 返回全片 T 秒处的画面（不含字幕）


# ---------------------------------------------------------------- 特写的大脸（24×22 的字符画，五官按表情现画）
FACE = {
    'boy': ["........HHHHHHH.........",
            ".....HHHHHHHHHHHHH......",
            "....HHHLLLHHHHHHHHHH....",
            "...HHHLLHHHHHHHHHHHHH...",
            "..HHHHHHHHHHHHHHHHHHHH..",
            "..HHHHHHHHHHHHHHHHHHHHH.",
            ".HHHHHHHHHHHHHHHHHHHHHH.",
            ".HHHHHhHHHHhHHHHHhHHHHH.",
            ".HHHhSSSHHSSSSHHSSShHHH.",
            ".HHhSSSSSSSSSSSSSSSShHH.",
            ".HHSSSSSSSSSSSSSSSSSSHH.",
            ".HSSSSSSSSSSSSSSSSSSSSH.",
            ".hSSSSSSSSSSSSSSSSSSSSh.",
            "..SSSSSSSSSSSSSSSSSSSS..",
            "..SSSSSSSSSSSSSSSSSSSS..",
            "..SSSSSSSSSSSSSSSSSSSS..",
            "..sSSSSSSSSSSSSSSSSSSs..",
            "...SSSSSSSSSSSSSSSSSS...",
            "...sSSSSSSSSSSSSSSSSs...",
            "....sSSSSSSSSSSSSSSs....",
            ".....ssSSSSSSSSSSss.....",
            ".......ssssssssss......."],
    'girl': ["........HHHHHHHH........",
             ".....HHHHHHHHHHHHHH.....",
             "....HHHLLLHHHHHHHHHHA...",
             "...HHHLLHHHHHHHHHHHAAA..",
             "..HHHHHHHHHHHHHHHHHHAH..",
             "..HHHHHHHHHHHHHHHHHHHHH.",
             ".HHHHHHHHHHHHHHHHHHHHHH.",
             ".HHHHHHHHHHhHHHHHHHHHHH.",
             ".HHHHSSSHHSSSSSHHSSSHHH.",
             ".HHHSSSSSSSSSSSSSSSSSHH.",
             ".HHSSSSSSSSSSSSSSSSSSHH.",
             ".HHSSSSSSSSSSSSSSSSSSHH.",
             ".HHSSSSSSSSSSSSSSSSSSHH.",
             ".HHSSSSSSSSSSSSSSSSSSHH.",
             ".HHSSSSSSSSSSSSSSSSSSHH.",
             ".HHSSSSSSSSSSSSSSSSSSHH.",
             ".HHsSSSSSSSSSSSSSSSSsHH.",
             ".HHHSSSSSSSSSSSSSSSSHHH.",
             ".HHHsSSSSSSSSSSSSSSsHHH.",
             ".HHHHsSSSSSSSSSSSSsHHHH.",
             ".HHHHHssSSSSSSSSssHHHHH.",
             ".hHHHH.ssssssssss.HHHHh."],
}
FACE_EYES = ((6, 13), (16, 13))
FACE_MOUTH = (11, 18)


@lru_cache(None)
def face(who, expr='smile', s=4, age='young'):
    """特写用的大脸，返回 RGBA。expr: smile happy laugh sad closed cry surprised shy"""
    L = pix.LOOK[(who, age)]
    rows = [list(r) for r in FACE[who]]
    if who == 'girl' and age == 'old':                     # 盘起来的头发：两边不再披下来
        for y in range(9, len(rows)):
            for x in (1, 2, 21, 22):
                if rows[y][x] in 'Hh': rows[y][x] = '.'
            if y >= 16:
                for x in (3, 20):
                    if rows[y][x] in 'Hh': rows[y][x] = '.'
    pal = {'H': L['hair'], 'h': L['hair_s'], 'L': L['hair_l'], 'S': SKIN, 's': SKIN_S, 'A': L.get('acc') or L['hair']}
    w, h = 24, len(rows)
    top = 4 if who == 'girl' and age == 'old' else 0
    im = Image.new('RGBA', (w, h + top)); px = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.': px[x, y + top] = pal[ch] + (255,)
    if top:
        d0 = ImageDraw.Draw(im)
        d0.ellipse([8, 0, 15, 6], fill=L['hair']); d0.point((10, 1), fill=L['hair_l']); d0.rectangle([10, 5, 13, 5], fill=L['acc'])
    E, Wt, M, B = pix.EYE, (255, 255, 255), pix.MOUTH, pix.BLUSH

    def P(x, y, c):
        if 0 <= x < w and 0 <= y < h: px[x, y + top] = c + (255,)
    for k, (ex, ey) in enumerate(FACE_EYES):
        inner = 1 if k == 0 else -1                        # 朝鼻子那一侧
        if expr in ('happy', 'laugh'):
            P(ex - 1, ey + 1, E); P(ex, ey, E); P(ex + 1, ey, E); P(ex + 2, ey + 1, E)
        elif expr in ('closed', 'cry'):
            P(ex - 1, ey, E); P(ex, ey + 1, E); P(ex + 1, ey + 1, E); P(ex + 2, ey, E)
            P(ex + (2 if k == 0 else -1), ey - 3, L['hair_s']); P(ex + (1 if k == 0 else 0), ey - 3, L['hair_s'])
        else:
            tall = 3 if expr == 'surprised' else 2
            for yy in range(ey - (1 if expr == 'surprised' else 0), ey + tall - (1 if expr == 'surprised' else 0)):
                P(ex, yy, E); P(ex + 1, yy, E)
            P(ex + (1 if k == 0 else 0), ey - (1 if expr == 'surprised' else 0), Wt)
            if expr == 'sad':
                bx = ex + (1 if k == 0 else 0)
                P(bx - inner, ey - 3, L['hair_s']); P(bx, ey - 2, L['hair_s']) if False else P(bx + inner, ey - 4, L['hair_s'])
                P(bx, ey - 3, L['hair_s'])
    for cx in (4, 18):
        if expr in ('smile', 'happy', 'laugh', 'shy', 'cry'):
            P(cx, 16, B); P(cx + 1, 16, B)
            if expr == 'shy': P(cx, 15, B); P(cx + 1, 15, B); P(cx + 2, 16, B)
    mx, my = FACE_MOUTH
    if expr in ('smile', 'shy'):
        P(mx - 1, my, M); P(mx, my + 1, M); P(mx + 1, my + 1, M); P(mx + 2, my, M)
    elif expr in ('happy', 'laugh'):
        for x in range(mx - 1, mx + 3): P(x, my, E)
        for x in range(mx, mx + 2): P(x, my + 1, M)
        if expr == 'laugh': P(mx - 1, my + 1, M); P(mx + 2, my + 1, M); P(mx, my + 2, M); P(mx + 1, my + 2, M)
    elif expr in ('sad', 'cry'):
        P(mx, my, E); P(mx + 1, my, E); P(mx - 1, my + 1, E); P(mx + 2, my + 1, E)
    elif expr == 'surprised':
        P(mx, my, E); P(mx + 1, my, E); P(mx, my + 1, M); P(mx + 1, my + 1, M)
    else:
        P(mx, my, M); P(mx + 1, my, M)
    im = outline(im, OUT)
    return im.resize((im.width * s, im.height * s), Image.NEAREST)


def bust(img, d, who, cx, top, s=4, expr='smile', age='young', tint=None):
    """特写：头和肩膀。(cx, top) 是头顶中点；返回 (左眼, 右眼) 的屏幕坐标"""
    L = pix.LOOK[(who, age)]
    f = face(who, expr, s, age)
    off = 4 * s if who == 'girl' and age == 'old' else 0
    x0 = cx - f.width / 2
    nb = top + off + 21 * s
    shirt, shirt_s = L['top'], L['top_s']
    d.rectangle([cx - 3 * s, nb - s, cx + 3 * s, nb + 3 * s], fill=SKIN_S)
    sh_poly = [(cx - 7 * s, nb + 1 * s), (cx + 7 * s, nb + 1 * s), (cx + 15 * s, nb + 5 * s), (cx + 18 * s, nb + 10 * s), (cx + 18 * s, H + 40),
               (cx - 18 * s, H + 40), (cx - 18 * s, nb + 10 * s), (cx - 15 * s, nb + 5 * s)]
    d.polygon([(x + (1 if x > cx else -1), y - 1) for x, y in sh_poly], fill=OUT)
    d.polygon(sh_poly, fill=shirt)
    if who == 'girl' and age == 'young':
        d.ellipse([cx - 6 * s, nb + 1 * s, cx + 6 * s, nb + 6 * s], fill=L['collar'])
        d.ellipse([cx - 4 * s, nb + 1 * s, cx + 4 * s, nb + 4 * s], fill=SKIN_S)
        for hx in (cx - 12 * s, cx + 9 * s):              # 披在肩上的长发
            d.rounded_rectangle([hx, nb - 2 * s, hx + 3 * s, nb + 12 * s], s, fill=L['hair'])
    elif who == 'boy' and age == 'young':
        d.polygon([(cx - 5 * s, nb + 2 * s), (cx, nb + 7 * s), (cx + 5 * s, nb + 2 * s), (cx + 5 * s, nb + 4 * s), (cx, nb + 9 * s), (cx - 5 * s, nb + 4 * s)],
                  fill=L['collar'])
        d.line([(cx, nb + 8 * s), (cx, H)], fill=shirt_s, width=max(1, s // 2))
        for k in range(3): d.rectangle([cx + s, nb + 11 * s + k * 5 * s, cx + 2 * s, nb + 12 * s + k * 5 * s], fill=L['collar'])
    elif who == 'boy':
        d.rounded_rectangle([cx - 9 * s, nb + 1 * s, cx + 9 * s, nb + 6 * s], 2 * s, fill=L['scarf'])
        d.rectangle([cx + 3 * s, nb + 5 * s, cx + 7 * s, nb + 15 * s], fill=L['scarf'])
    else:
        d.ellipse([cx - 5 * s, nb + 1 * s, cx + 5 * s, nb + 5 * s], fill=SKIN_S)
    if tint:
        pass
    img.paste(f, (int(round(x0)), int(round(top))), f)
    return [(x0 + (ex + 0.5) * s, top + off + (ey + 2) * s) for ex, ey in FACE_EYES]
