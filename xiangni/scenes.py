"""想你和我们以后 · 镜头函数。签名都是 (img, d, lt, dur, T, A)：lt 是镜头内的时间，dur 是镜头时长，T 是全片时间，A 是这一帧的音量。

故事：她（穿黄色）和他（穿蓝色）住在同一座城市的两头，各自加班。副歌是两人老了以后的日子，间奏是年轻时的回忆，
桥段是她一个人的日常，最后她坐夜车去见他，两人牵着手一路变老，日落时前面的画面一张张印成照片飞上天。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
from pix import (W, H, FONT, FONT_S, OUT, clamp, lerp, lerpc, ease, eout, ein, eback, span, tri, rng, sky, glow, tfill, darken,
                 blend_box, dither_fade, vig, grade, put, paste, person, wph, text, stars, sparkle, twinkle, meteor, moon, cloud,
                 hills, hill_y, rain, snow, petals, fireflies, butterfly, bird, heart_poly, firework, tree_round, flower, grass,
                 city, lamp, pulse, amp, spr, with_alpha, outline, char_img, CX, FY, CW, CH)

SNAP = None   # render.py 填入：SNAP(T) 返回全片 T 秒处的画面（不含字幕）

YEL, YEL_S, YEL_L = (255, 206, 72), (226, 150, 48), (255, 240, 160)
BLU, BLU_S, BLU_L = (92, 140, 230), (62, 98, 182), (170, 206, 255)
CREAM = (255, 246, 228)


# ---------------------------------------------------------------- 共用道具
@lru_cache(None)
def heart_halves(r):
    """一颗心沿锯齿裂缝分成两半：左半黄色（她），右半蓝色（他）。返回 (左, 右, 整颗)"""
    s = int(r * 2.6) + 6
    yy, xx = np.mgrid[0:s, 0:s]
    u = (xx - s / 2 + 0.5) / r; v = -(yy - s / 2 + 0.5) / r + 0.2
    inside = (u * u + v * v - 1) ** 3 - u * u * v ** 3 < 0
    zig = 0.09 * np.abs((v * 4.5) % 2 - 1) - 0.045
    left = inside & (u < zig)
    out = []
    for part, (c, cs, cl) in ((left, (YEL, YEL_S, YEL_L)), (inside & ~left, (BLU, BLU_S, BLU_L))):
        a = np.zeros((s, s, 4), np.uint8)
        a[part] = c + (255,)
        a[part & (v < -0.45 + 0.25 * np.abs(u))] = cs + (255,)
        hl = ((np.abs(u) - 0.48) ** 2 + (v - 0.6) ** 2 < 0.05) & part
        a[hl] = cl + (255,)
        a[((np.abs(u) - 0.55) ** 2 + (v - 0.68) ** 2 < 0.008) & part] = (255, 255, 255, 255)
        out.append(outline(Image.fromarray(a), CREAM))
    whole = Image.alpha_composite(out[0], out[1])
    return out[0], out[1], whole


def heart_at(img, x, y, r, which=2, alpha=1.0):
    r = max(2, int(round(r)))
    paste(img, heart_halves(r)[which], x, y, alpha, 'cc')


@lru_cache(None)
def title_glyph(ch, scale=3, top=(255, 246, 186), bot=(255, 140, 172), line=(150, 56, 120), out=(30, 16, 46)):
    w = int(FONT.getlength(ch)) + 8; h = FONT.size + 8
    m = Image.new('L', (w, h)); md = ImageDraw.Draw(m); md.fontmode = '1'
    md.text((4, 3), ch, font=FONT, fill=255)
    mk = np.array(m) > 0
    a = np.zeros((h, w, 4), np.uint8)
    for y in range(h): a[y, :, :3] = lerpc(top, bot, (y - 4) / 15)
    a[..., 3] = mk * 255
    im = outline(outline(Image.fromarray(a), line), out)
    sh = Image.new('RGBA', (w + 1, h + 1))
    shadow = np.array(im); shadow[shadow[..., 3] > 0, :3] = out
    sh.paste(Image.fromarray(shadow), (1, 1)); sh.alpha_composite(im)
    return sh.resize((sh.width * scale, sh.height * scale), Image.NEAREST)


def title(img, s, cx, cy, scale, lt, t_in=0.0, stagger=0.07, shine=None, drop=True):
    gl = [title_glyph(c, scale) for c in s]
    adv = [FONT.getlength(c) * scale for c in s]
    x = cx - sum(adv) / 2 - 4 * scale
    for i, (g, a) in enumerate(zip(gl, adv)):
        k = lt - t_in - i * stagger
        if k >= 0:
            dy = -40 * (1 - eback(k / 0.35)) if drop else 0
            if shine is not None and -0.15 < shine - i / len(s) < 0.15:
                g = g.copy(); arr = np.array(g); m = arr[..., 3] > 0
                arr[m, :3] = np.minimum(255, arr[m, :3].astype(int) + 70).astype(np.uint8); g = Image.fromarray(arr)
            img.paste(g, (int(x), int(cy - g.height / 2 + dy)), g)
        x += a


_RB = rng(5)
BURST = [(_RB.uniform(0, 2 * math.pi), _RB.uniform(70, 200), i % 4, [YEL, BLU, (255, 255, 255), (255, 150, 190)][i % 4]) for i in range(64)]


def burst(img, d, k, cx, cy, parts=BURST, life=1.3, scale=1.0):
    if not 0 <= k < life: return
    u = k / life
    for ang, sp, kind, col in parts:
        dist = (8 + sp * eout(u)) * scale
        x = cx + math.cos(ang) * dist; y = cy + math.sin(ang) * dist * 0.75 + 24 * u * u * scale
        c = lerpc(col, (30, 20, 60), u)
        if kind == 0: put(img, 'heart', x, y, 1, tint=col, alpha=1 - u)
        elif kind == 1: twinkle(d, int(x), int(y), 1 - u * 0.8, c, 3)
        else: d.rectangle([x, y, x + 1, y + 1], fill=c)


def shake(img, k, amp_, dur):
    if not 0 <= k < dur: return
    a = amp_ * (1 - k / dur)
    dx, dy = round(a * math.sin(k * 97)), round(a * math.cos(k * 71))
    if dx or dy:
        src = img.copy(); img.paste((8, 6, 20), (0, 0, W, H)); img.paste(src, (dx, dy))


def bubble(img, d, x, y, w, h, f, thought=False, tail=(0, 1), col=(255, 255, 255), edge=OUT):
    """对话泡泡。(x, y) 是尾巴尖，f 从 0 到 1 弹出来。返回泡泡内容区域的中心"""
    if f <= 0: return None
    s = eback(f)
    bw, bh = max(2, w * s), max(2, h * s)
    cx = x + tail[0] * 6 * s; cy = y - 8 * s - bh / 2
    box = [cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2]
    if thought:
        for k, (dx, dy, r) in enumerate([(0, -3, 1.5), (tail[0] * 3, -7, 2.5)]):
            rr = r * s
            d.ellipse([x + dx * s - rr - 1, y + dy * s - rr - 1, x + dx * s + rr + 1, y + dy * s + rr + 1], fill=edge)
            d.ellipse([x + dx * s - rr, y + dy * s - rr, x + dx * s + rr, y + dy * s + rr], fill=col)
        d.rounded_rectangle([box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1], radius=int(min(bw, bh) / 2), fill=edge)
        d.rounded_rectangle(box, radius=int(min(bw, bh) / 2 - 1), fill=col)
    else:
        tp = [(x, y), (cx - 3 * s + tail[0] * 2, cy + bh / 2 - 1), (cx + 3 * s + tail[0] * 2, cy + bh / 2 - 1)]
        d.rounded_rectangle([box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1], radius=4, fill=edge)
        d.polygon([(x, y + 1), (tp[1][0] - 1, tp[1][1]), (tp[2][0] + 1, tp[2][1])], fill=edge)
        d.rounded_rectangle(box, radius=3, fill=col)
        d.polygon(tp, fill=col)
    return (cx, cy) if f >= 0.6 else None


@lru_cache(None)
def head_img(who, age='young', expr='smile', s=1, view='front'):
    im = char_img(who, age, view, 'stand', 0, expr)
    return im.crop((CX - 8, FY - 31, CX + 8, FY - 15)).resize((16 * s, 16 * s), Image.NEAREST)


def steam(img, d, x, y, t, n=3, h=22, col=(240, 240, 250), a=0.5, spread=4):
    for i in range(n):
        f = (t * 0.6 + i / n) % 1
        sx = x + (i - (n - 1) / 2) * spread + 2 * math.sin(t * 2 + i * 2 + f * 5)
        sy = y - f * h
        tfill(img, 'ellipse', [sx - 2, sy - 2, sx + 2, sy + 1], col, a * math.sin(math.pi * f))


def clock_face(d, x, y, r, t, speed=1.0, face=(250, 246, 232), rim=(120, 90, 70)):
    d.ellipse([x - r - 1, y - r - 1, x + r + 1, y + r + 1], fill=rim)
    d.ellipse([x - r, y - r, x + r, y + r], fill=face)
    for k in range(12):
        a = k * math.pi / 6
        d.point((x + math.cos(a) * (r - 2), y + math.sin(a) * (r - 2)), fill=(150, 140, 130))
    am = t * speed * 2 * math.pi / 6; ah = am / 12 + 1.0
    d.line([(x, y), (x + math.sin(am) * (r - 2), y - math.cos(am) * (r - 2))], fill=(50, 40, 50))
    d.line([(x, y), (x + math.sin(ah) * (r - 5), y - math.cos(ah) * (r - 5))], fill=(50, 40, 50), width=2)
    d.point((x, y), fill=(220, 60, 60))


def bar_at(n, default):
    """开场按前奏的小节线走：0.63s 第一个和弦，之后每小节约 3.9 秒"""
    b = [x for x in pix.AUDIO['bars'] if x > 0.2]
    return b[n] if n < len(b) and abs(b[n] - default) < 1.0 else default


def beats_in(t0, t1):
    b = pix.AUDIO['beats']
    return [x for x in b if t0 <= x < t1]


# ---------------------------------------------------------------- 片头用到的夜景
WIN_A, WIN_B = (98, 150), (384, 138)    # 片头两扇亮起的窗；第一句的分屏从这两扇窗展开


def city_night(img, d, sy, T, lt, dim=0.0):
    """片头最后的夜景，按最终取景设计，sy 是整体下移量"""
    city(img, d, 196 + sy, 21, T * 2, (44, 34, 84), (120, 100, 170), 50, 120, 0.3, T, edge=(56, 44, 100))
    city(img, d, 204 + sy, 22, T * 5, (30, 22, 60), lerpc((255, 214, 130), (60, 50, 90), dim), 30, 90, 0.4, T)
    # 高架桥和夜班电车
    by = 178 + sy
    d.rectangle([0, by, W, by + 4], fill=(24, 18, 46))
    for x in range(10, W, 38): d.rectangle([x, by + 4, x + 3, by + 26], fill=(24, 18, 46))
    tx = (lt - 9.4) * 70
    if -300 < tx < W + 60:
        for k in range(3):
            x0 = W - tx + k * 66
            d.rectangle([x0, by - 12, x0 + 62, by - 1], fill=(70, 70, 110))
            for wx in range(int(x0) + 4, int(x0) + 58, 8): d.rectangle([wx, by - 9, wx + 4, by - 6], fill=(255, 236, 160))
        glow(img, W - tx - 2, by - 6, 10, (255, 250, 200), 0.6)
    # 两栋公寓
    for (x0, x1, top, col, wx, wy, lit, side) in ((24, 150, 86, (36, 28, 64), *WIN_A, YEL, 0), (330, 462, 70, (32, 30, 66), *WIN_B, BLU_L, 1)):
        d.rectangle([x0, top + sy, x1, H + 200], fill=col)
        d.rectangle([x0, top + sy, x1, top + 3 + sy], fill=lerpc(col, (90, 80, 140), 0.5))
        rr = rng(x0)
        for yy in range(top + 10, H, 14):
            for xx in range(x0 + 8, x1 - 8, 14):
                if (xx, yy) == (wx - 4, wy - 5): continue
                on = rr.random() < 0.35 * (1 - dim)
                d.rectangle([xx, yy + sy, xx + 7, yy + 9 + sy], fill=(250, 210, 130) if on else (22, 18, 44))
    d.rectangle([0, 214 + sy, W, H + 200], fill=(18, 14, 36))
    for k in range(6):      # 路上的车灯
        f = (lt * 0.35 + k / 6) % 1
        x = lerp(-30, W + 30, f) if k % 2 else lerp(W + 30, -30, f)
        y = 226 + sy + (k % 2) * 10
        c = (255, 240, 200) if k % 2 else (255, 90, 90)
        d.line([(x, y), (x - 14 if k % 2 else x + 14, y)], fill=lerpc(c, (18, 14, 36), 0.5))
        d.rectangle([x - 1, y, x + 1, y], fill=c)


def lit_window(img, d, x, y, col, k, who):
    """一扇亮着的窗，窗里有个小小的剪影在低头看手机"""
    g = 0.5 + 0.2 * pulse(k, 0.5)
    glow(img, x, y, 22, col, 0.45 * g)
    d.rectangle([x - 4, y - 5, x + 3, y + 4], fill=col)
    sil = char_img(who, 'adult', 'side', 'stand', 0, 'down', 'phone', None, (30, 22, 52))
    sil = sil.crop((CX - 8, FY - 30, CX + 8, FY - 16))
    if who == 'boy': sil = sil.transpose(Image.FLIP_LEFT_RIGHT)
    sil = sil.resize((8, 7), Image.NEAREST)
    img.paste(sil, (int(x) - 4, int(y) - 2), sil)


# ---------------------------------------------------------------- 片头：她小指上的红线飞过整座城市，系在他的小指上
HAND = [
    "...........ss.....",
    "..........sSSs....",
    "..........SSSs....",
    "........RRSSSsRR..",
    ".......R.RRRRRR.R.",
    "........RRSrSsRR..",
    ".........r.SSsr...",
    "..........SSSs....",
    "...ss.ss..SSSs....",
    "..sSSsSSssSSSs....",
    "..SSSSSSSSSSSs....",
    ".sSSkSSkSSkSSs....",
    ".SSSSSSSSSSSSs....",
    "sSSSSSSSSSSSSs....",
    "sSSSSSSSSSSSs.....",
    "sSSSSSSSSSSSs.....",
    ".sSSSSSSSSSSs.....",
    "..sSSSSSSSSs......",
    "..yYYYYYYYYYy.....",
    ".yYYYYYYYYYYYy....",
    ".YYYYYYYYYYYYY....",
    ".YYYYYYYYYYYYY....",
]
HAND_KNOT = (17, 4)        # 红线从蝴蝶结右边那个环伸出去
HS = 8                     # 特写放大倍数


@lru_cache(None)
def hand_img(sleeve, sleeve_s, flip=False):
    pal = {'S': pix.SKIN, 's': pix.SKIN_S, 'k': (214, 160, 132), 'R': (232, 52, 72), 'r': (168, 30, 52), 'Y': sleeve, 'y': sleeve_s}
    w = max(len(r) for r in HAND); h = len(HAND)
    im = Image.new('RGBA', (w + 2, h + 2)); px = im.load()
    for y, r in enumerate(HAND):
        for x, ch in enumerate(r):
            if ch != '.': px[x + 1, y + 1] = pal[ch] + (255,)
    im = outline(im, OUT)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im.resize((im.width * HS, im.height * HS), Image.NEAREST)


def knot_xy(hx, hy, flip):
    c = HAND_KNOT[0] + 1; wpad = max(len(r) for r in HAND) + 2
    x = hx + (c + 1) * HS if not flip else hx + (wpad - 1 - c) * HS
    return x, hy + (HAND_KNOT[1] + 1.5) * HS


def arc_len(pts):
    out = [0.0]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]): out.append(out[-1] + math.hypot(x1 - x0, y1 - y0))
    return out


def point_at(pts, cum, u):
    s = u * cum[-1]
    i = max(0, min(len(pts) - 2, int(np.searchsorted(cum, s)) - 1))
    seg = max(1e-6, cum[i + 1] - cum[i]); f = (s - cum[i]) / seg
    return lerp(pts[i][0], pts[i + 1][0], f), lerp(pts[i][1], pts[i + 1][1], f)


def red_thread(img, d, pts, a=1.0, w=2, glow_a=0.28, pulses=()):
    """红线：pts 是屏幕坐标的折线；pulses = [(沿线位置 0..1, 亮度), ...] 是沿线跑的亮光"""
    if len(pts) < 2 or a <= 0: return
    pts = [(float(x), float(y)) for x, y in pts]
    m = Image.new('L', (W, H)); md = ImageDraw.Draw(m)
    md.line(pts, fill=int(255 * glow_a), width=w + 6, joint='curve')
    md2 = Image.new('L', (W, H)); ImageDraw.Draw(md2).line(pts, fill=255, width=w, joint='curve')
    if a < 1:
        m = Image.fromarray((np.array(m) * (BAYER_A < a)).astype(np.uint8))
        md2 = Image.fromarray(((np.array(md2) > 0) & (BAYER_A < a)).astype(np.uint8) * 255)
    img.paste((255, 70, 104), (0, 0, W, H), m)
    img.paste((224, 40, 64), (0, 0, W, H), md2)
    if a >= 1: d.line([(x, y - 1) for x, y in pts], fill=(255, 132, 150), width=1)
    if pulses:
        cum = arc_len(pts)
        for u, b in pulses:
            if not 0 <= u <= 1 or b <= 0: continue
            x, y = point_at(pts, cum, u)
            glow(img, x, y, 16, (255, 214, 200), 0.65 * b)
            d.rectangle([x - 1, y - 1, x + 1, y + 1], fill=(255, 250, 240))


BAYER_A = pix.BAYER


def bokeh_bg(img, d, T, warm=True):
    top, bot = ((22, 14, 44), (58, 32, 80)) if warm else ((14, 16, 46), (36, 34, 86))
    sky(img, ((0, top), (1, bot)), 0, H)
    for i in range(14):
        r = rng(i + 200)
        x = (r.uniform(0, W) + T * r.uniform(-8, 8)) % (W + 60) - 30
        y = r.uniform(10, H - 10) + 5 * math.sin(T * 0.7 + i)
        glow(img, x, y, r.uniform(16, 40), r.choice([(255, 170, 120), (255, 120, 160), (150, 170, 255), (255, 220, 150)]), 0.3)
    stars(d, T, H, 0.6, 60)


def closeup(img, d, lt, T, who, pluck_t, arrive=False):
    """小指特写。她的手在左边，红线往右飞出画面；他的手在右边，红线从左边飞进来"""
    girl = who == 'girl'
    bokeh_bg(img, d, T, girl)
    hand = hand_img(YEL, YEL_S) if girl else hand_img(BLU, BLU_S, True)
    fl = 2 * math.sin(T * 2.2)
    hx = 52 if girl else W - 52 - hand.width
    hy = 100 + fl
    ax, ay = knot_xy(hx, hy, not girl)
    k = lt - pluck_t
    tremble = 1 + 3 * clamp(1 - abs(k) / 0.4) if k < 0.4 else 1
    n = 60
    pts = []
    for i in range(n + 1):
        f = i / n
        x = lerp(ax, W + 20, f) if girl else lerp(-20, ax, f)
        dist = abs(x - ax)
        y = ay - dist * 0.2 + tremble * 2.2 * math.sin(dist * 0.06 - T * 7) * min(1, dist / 40)
        pts.append((x, y))
    pulses = []
    if 0 <= k < 0.5:
        u = k / 0.35
        pulses = [(u if girl else 1 - u, 1.0)] if not arrive else [(clamp(k / 0.3), 1.0)]
    red_thread(img, d, pts, 1.0, 3, 0.3, pulses)
    img.paste(hand, (int(hx), int(hy)), hand)
    glow(img, ax, ay, 18, (255, 120, 140), 0.25 + 0.25 * clamp(1 - abs(k) / 0.5))
    for i in range(8):
        f = (T * 0.3 + i / 8) % 1
        x = hx + 80 + 40 * math.sin(i * 2.1 + T); y = hy + 30 - f * 130
        twinkle(d, int(x), int(y), f, (255, 230, 236), 2)
    if arrive and k > 0.3:
        f = clamp((k - 0.3) / 0.6)
        put(img, 'heart', ax + 4, ay - 14 - 20 * f, 2 if f < 0.2 else 1, alpha=1 - f * 0.5)


def catmull(ctrl, n=8):
    P = [ctrl[0]] + list(ctrl) + [ctrl[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - e) * t * t + (-a + 3 * b - 3 * c + e) * t ** 3)
                             for a, b, c, e in zip(p0, p1, p2, p3)))
    out.append(tuple(ctrl[-1]))
    return out


@lru_cache(None)
def flight_path():
    """红线在城市里走的路线（近景坐标）：出她的窗、翻过楼顶、贴着电线、越过大桥、在月亮前绕一个心形的圈，再进他的窗"""
    ctrl = [(150, 164), (232, 126), (330, 70), (430, 94), (520, 150), (610, 130), (700, 114), (820, 106), (900, 94), (962, 92)]
    heart = [(1010 + x * 1.5, 66 + y * 1.5) for x, y in (pix.HEART_PTS[32:] + pix.HEART_PTS[:33])][::3]
    ctrl += heart + [(1070, 118), (1170, 130), (1280, 140), (1376, 146)]
    return catmull(ctrl, 8)


@lru_cache(None)
def path_y_table():
    pts = flight_path()
    xs = np.array([p[0] for p in pts]); ys = np.array([p[1] for p in pts])
    out = np.full(1800, 130.0)
    for x in range(1800):
        m = np.abs(xs - x) < 70
        if m.any(): out[x] = ys[m].mean()
    return out


def mono_spline(keys, t):
    """单调三次插值（Fritsch–Carlson），镜头位置不会来回晃"""
    ts = [k[0] for k in keys]; vs = [k[1] for k in keys]
    if t <= ts[0]: return vs[0]
    n = len(ts)
    sec = [(vs[i + 1] - vs[i]) / (ts[i + 1] - ts[i]) for i in range(n - 1)]
    m = [0.0] + [0.0 if sec[i - 1] * sec[i] <= 0 else 2 / (1 / sec[i - 1] + 1 / sec[i]) for i in range(1, n - 1)] + [sec[-1]]
    if t >= ts[-1]: return vs[-1] + m[-1] * (t - ts[-1])
    i = max(j for j in range(n - 1) if ts[j] <= t)
    h = ts[i + 1] - ts[i]; u = (t - ts[i]) / h
    return ((2 * u ** 3 - 3 * u ** 2 + 1) * vs[i] + (u ** 3 - 2 * u ** 2 + u) * h * m[i]
            + (-2 * u ** 3 + 3 * u ** 2) * vs[i + 1] + (u ** 3 - u ** 2) * h * m[i + 1])


FLIGHT_BLD = [(40, 150, 112, (36, 28, 66), 1), (226, 100, 150, (40, 32, 74), 2), (336, 96, 74, (32, 28, 64), 3),
              (980, 90, 178, (40, 32, 72), 4), (1088, 100, 100, (34, 28, 66), 5), (1210, 70, 140, (40, 34, 76), 6),
              (1300, 160, 106, (32, 30, 70), 7)]
WIN_COLS = [(255, 214, 130), (255, 236, 180), (200, 220, 255), (255, 190, 150)]


def near_building(d, x, y, w, col, seed, cam=None):
    """近景的楼。cam 不为空时，镜头中心已经经过的窗户会一扇扇亮起来"""
    if x > W + 4 or x + w < -4: return
    d.rectangle([x, y, x + w, H + 80], fill=col)
    d.rectangle([x, y, x + w, y + 2], fill=lerpc(col, (120, 110, 170), 0.5))
    rr = rng(seed)
    for wy in range(int(y) + 9, H + 40, 14):
        for wx in range(int(x) + 6, int(x + w) - 8, 13):
            on = rr.random() < 0.38
            c = rr.choice(WIN_COLS)
            late = rr.random()
            if cam is not None and not on and late < 0.55 and wx < 240 - 60 * late: on = True
            if wx < -10 or wx > W + 10: continue
            d.rectangle([wx, wy, wx + 7, wy + 9], fill=c if on else (24, 20, 48))
            if on and rr.random() < 0.35:
                d.ellipse([wx + 2, wy + 3, wx + 5, wy + 6], fill=lerpc(c, (40, 24, 50), 0.75))
                d.rectangle([wx + 1, wy + 6, wx + 6, wy + 9], fill=lerpc(c, (40, 24, 50), 0.75))


def flight(img, d, t, T, keys, b1, b2, b3):
    cam = mono_spline(keys, t)
    vel = (mono_spline(keys, t + 1 / 30) - cam) * 30
    cy = (path_y_table()[int(clamp(cam + 240, 0, 1799))] - 130) * 0.45
    sk = pix.vgrad(W, H + 120, ((0, (8, 8, 30)), (0.5, (30, 22, 74)), (0.8, (84, 48, 120)), (1, (170, 90, 136))), 6)
    oy = int(clamp(60 + cy * 0.25, 0, 120))
    img.paste(sk.crop((0, oy, W, oy + H)))
    stars(d, T, H, 1, 220, int(cam * 0.06), int(cy * 0.1))
    mx, my = 468 - cam * 0.3, 54 - cy * 0.3
    glow(img, mx, my, 86, (255, 230, 210), 0.35 + 0.2 * pulse(T, 0.5))
    moon(d, mx, my, 38, (255, 246, 214))
    meteor(d, t, 1.0, 420, 10, -160, 50, 0.7)
    city(img, d, 190 - cy * 0.35, 31, cam * 0.25, (46, 36, 88), (130, 110, 180), 50, 96, 0.3, T)
    city(img, d, 212 - cy * 0.6, 32, cam * 0.5, (30, 24, 62), (255, 210, 130), 40, 94, 0.4, T)

    def X(x): return x - cam

    def Y(y): return y - cy
    # 桥下的河、街道
    d.rectangle([0, Y(234), W, H + 80], fill=(18, 14, 36))
    rx0, rx1 = X(600), X(980)
    d.rectangle([rx0, Y(234), rx1, H + 80], fill=(20, 26, 62))
    for k in range(14):
        wy = Y(240 + k * 3)
        xx = rx0 + (k * 37 + t * 20) % max(1, rx1 - rx0)
        d.line([(xx, wy), (xx + 8, wy)], fill=(110, 110, 170))
    for k in range(8):
        f = (t * 0.5 + k / 8) % 1
        x = lerp(-40, 1500, f) if k % 2 else lerp(1500, -40, f)
        if 600 < x < 980: continue
        y = Y(244 + (k % 2) * 8)
        c = (255, 240, 200) if k % 2 else (255, 90, 90)
        d.line([(X(x), y), (X(x) - 14 if k % 2 else X(x) + 14, y)], fill=lerpc(c, (18, 14, 36), 0.5))
    for x0, w, top, col, seed in FLIGHT_BLD:
        near_building(d, X(x0), Y(top), w, col, seed, cam)
    # 楼顶的水塔和天线
    wx = X(260); d.rectangle([wx, Y(128), wx + 18, Y(146)], fill=(40, 32, 74)); d.rectangle([wx + 2, Y(146), wx + 4, Y(150)], fill=(40, 32, 74))
    d.rectangle([wx + 14, Y(146), wx + 16, Y(150)], fill=(40, 32, 74)); d.polygon([(wx - 2, Y(128)), (wx + 20, Y(128)), (wx + 9, Y(120))], fill=(40, 32, 74))
    ax_ = X(384); d.line([(ax_, Y(74)), (ax_, Y(44))], fill=(32, 28, 64), width=2)
    if math.sin(T * 4) > 0: d.rectangle([ax_ - 1, Y(43), ax_ + 1, Y(45)], fill=(255, 80, 80)); glow(img, ax_, Y(42), 6, (255, 80, 80), 0.5)
    # 她和他的窗
    for (px, py), col, who in (((150, 164), (255, 214, 120), 'girl'), ((1376, 146), (150, 196, 255), 'boy')):
        if -20 < X(px) < W + 20: lit_window(img, d, X(px), Y(py), col, T, who)
    # 电线杆、电线和鸽子
    for px in (470, 650):
        d.rectangle([X(px) - 1, Y(116), X(px) + 1, Y(236)], fill=(28, 22, 50)); d.rectangle([X(px) - 6, Y(118), X(px) + 6, Y(120)], fill=(28, 22, 50))
    wire = [(X(x), Y(120 + 16 * (1 - ((x - 560) / 90) ** 2))) for x in range(470, 651, 6)]
    d.line(wire, fill=(28, 22, 50))
    for i, px in enumerate((500, 524, 548, 582, 606)):
        py = 120 + 16 * (1 - ((px - 560) / 90) ** 2) - 3
        k = t - (b1 + i * 0.05)
        if k < 0:
            d.ellipse([X(px) - 3, Y(py) - 2, X(px) + 3, Y(py) + 2], fill=(150, 150, 176)); d.rectangle([X(px) + 2, Y(py) - 4, X(px) + 4, Y(py) - 2], fill=(130, 130, 160))
        else:
            bird(d, int(X(px) - k * (40 + i * 12)), int(Y(py) - k * (90 + i * 10)), T, (190, 190, 214), i)
    # 大桥和列车
    if X(980) > -20 and X(600) < W + 20:
        d.rectangle([X(600), Y(176), X(980), Y(182)], fill=(40, 34, 70))
        d.line([(X(600), Y(160)), (X(980), Y(160))], fill=(40, 34, 70), width=2)
        for k in range(0, 380, 20):
            d.line([(X(600 + k), Y(176)), (X(610 + k), Y(160)), (X(620 + k), Y(176))], fill=(40, 34, 70))
        for px in (700, 800, 900): d.rectangle([X(px) - 3, Y(182), X(px) + 3, Y(240)], fill=(34, 28, 60))
        head = 1060 - (t - (b2 - 0.4)) * 620
        for k in range(5):
            cx0 = head + k * 48
            if X(cx0) > W + 10 or X(cx0 + 46) < -10: continue
            d.rectangle([X(cx0), Y(162), X(cx0 + 45), Y(175)], fill=(200, 206, 220))
            d.rectangle([X(cx0), Y(171), X(cx0 + 45), Y(172)], fill=(236, 120, 90))
            for wx2 in range(int(X(cx0)) + 4, int(X(cx0)) + 42, 8): d.rectangle([wx2, Y(165), wx2 + 4, Y(168)], fill=(255, 236, 170))
        if -60 < X(head) < W + 60: glow(img, X(head), Y(170), 18, (255, 250, 210), 0.5)
    # 霓虹爱心招牌
    nx, ny = X(1138), Y(128)
    if -40 < nx < W + 40:
        on = t > b3 + 0.25 and (t > b3 + 0.55 or int(t * 20) % 2)
        d.rectangle([nx - 16, ny - 13, nx + 16, ny + 13], fill=(30, 24, 50))
        put(img, 'bigheart', nx, ny, 2, tint=(255, 110, 170) if on else (90, 50, 80))
        if on: glow(img, nx, ny, 34, (255, 110, 170), 0.4)
    # 红线
    pts = [(X(x), Y(y)) for x, y in flight_path() if -40 < X(x) < W + 40]
    lead = []
    if pts:
        cum = arc_len(pts)
        lead = [((t * 0.9 + j / 3) % 1, 0.7) for j in range(3)]
    red_thread(img, d, pts, 1.0, 2, 0.3, lead)
    hx, hy = X(1010), Y(66)
    if abs(t - b3) < 0.6:
        f = 1 - abs(t - b3) / 0.6
        glow(img, hx, hy, 40, (255, 150, 170), 0.35 * f)
        twinkle(d, int(hx + 26), int(hy - 22), (t - b3 + 0.6) / 1.2, (255, 255, 240), 4)
    # 前景和速度线
    for i in range(6):
        fx = i * 300 + 160 - cam * 1.6
        if -60 < fx < W + 60:
            for bx, by, r in ((0, 0, 22), (-18, 8, 16), (20, 6, 18)):
                d.ellipse([fx + bx - r, Y(258) + by - r, fx + bx + r, Y(258) + by + r], fill=(12, 8, 26))
    if vel > 220:
        rr = rng(int(t * 30))
        for i in range(int((vel - 220) / 25)):
            y = rr.uniform(8, H - 8); x = rr.uniform(-20, W)
            d.line([(x, y), (x + vel * 0.07, y)], fill=(210, 200, 250))


def s_intro(img, d, lt, dur, T, A):
    h0, h1, h2, h3 = bar_at(0, 0.63), bar_at(1, 4.54), bar_at(2, 8.48), bar_at(3, 12.4)
    q = (h1 - h0) / 4
    b1, b2, b3 = h0 + q, h0 + 2 * q, h0 + 3 * q
    go = h0 + 0.15
    keys = [(go, 0.0), (b1, 230.0), (b2, 520.0), (b3 - 0.3, 730.0), (b3 + 0.3, 812.0), (h1, 1060.0)]
    wide_t = h1 + 0.56
    if lt < go:
        closeup(img, d, lt, T, 'girl', h0)
    elif lt < h1:
        flight(img, d, lt, T, keys, b1, b2, b3)
        if lt - go < 0.2:
            rr = rng(int(lt * 30))
            for i in range(26):
                y = rr.uniform(0, H); x = rr.uniform(-40, W)
                d.line([(x, y), (x + 60, y)], fill=(255, 236, 240))
    elif lt < wide_t:
        closeup(img, d, lt, T, 'boy', h1, True)
    else:
        intro_wide(img, d, lt, dur, T, h1, h2, h3, wide_t)
    for t0, a0, dd in ((h0, 0.85, 0.18), (h1, 0.6, 0.15), (wide_t, 0.5, 0.2)):
        if 0 <= lt - t0 < dd: darken(img, a0 * (1 - (lt - t0) / dd), (255, 250, 240))
    shake(img, lt - h0, 4, 0.35)
    shake(img, lt - h1, 2, 0.2)


def intro_wide(img, d, lt, dur, T, h1, h2, h3, t_in):
    sk = pix.vgrad(W, H, ((0, (6, 6, 26)), (0.45, (26, 18, 68)), (0.78, (78, 44, 118)), (1, (168, 86, 132))), 6)
    img.paste(sk)
    stars(d, T, H, 1, 220)
    glow(img, 436, 28, 34, (255, 230, 200), 0.3)
    moon(d, 436, 28, 12)
    for t0, x0, y0, dx, dy in [(h2 + 1.6, 470, 30, -150, 46), (h3 + 0.6, 260, 8, -140, 50), (h3 + 2.4, 160, 14, 110, 40)]:
        meteor(d, lt, t0, x0, y0, dx, dy, 0.8)
    dim = ease(span(lt, h3 + 0.5, dur - 0.8)) * 0.9
    city_night(img, d, 0, T, lt, dim)
    for (wx, wy), col, who in ((WIN_A, (255, 214, 120), 'girl'), (WIN_B, (150, 196, 255), 'boy')):
        lit_window(img, d, wx, wy, col, T, who)
    p0, c, p2 = (WIN_A[0] + 5, WIN_A[1] - 4), (240, 64), (WIN_B[0] - 5, WIN_B[1] - 4)

    def bz(u): return ((1 - u) ** 2 * p0[0] + 2 * u * (1 - u) * c[0] + u * u * p2[0], (1 - u) ** 2 * p0[1] + 2 * u * (1 - u) * c[1] + u * u * p2[1])
    pts = [bz(i / 80) for i in range(81)]
    merge = h1 + 2 * (h2 - h1) / 4
    fade = 1 - span(lt, h3 + 0.9, h3 + 2.4)
    pulses = []
    for t0 in (h2 - 0.98, h2 - 0.61, h2 - 0.28):
        k = (lt - t0) / 0.45
        if 0 <= k < 1: pulses.append((k, 1 - k * 0.5))
    if lt < t_in + 0.5: pulses.append((clamp((lt - t_in) / 0.5), 1.0))
    red_thread(img, d, pts, fade, 2, 0.3, pulses)
    ax, ay = bz(0.5)
    if lt < merge:
        f = ease(span(lt, t_in + 0.25, merge))
        for k, u in ((0, lerp(0, 0.5, f)), (1, lerp(1, 0.5, f))):
            x, y = bz(u)
            heart_at(img, x, y, lerp(5, 13, f), k)
            glow(img, x, y, 14, YEL if k == 0 else BLU_L, 0.35)
            for j in range(5):
                uj = (lerp(0, 0.5, max(0, f - j * 0.03)) if k == 0 else lerp(1, 0.5, max(0, f - j * 0.03)))
                tx, ty = bz(uj)
                d.point((tx, ty - 3), fill=YEL_L if k == 0 else BLU_L)
    elif lt < h3:
        k = lt - merge
        r = 15 + 2 * pulse(T, 0.3)
        glow(img, ax, ay, 46, (255, 170, 200), 0.4 + 0.15 * pulse(T, 0.5))
        heart_at(img, ax, ay, r)
        if k < 0.5:
            rr_ = 10 + k * 300
            d.ellipse([ax - rr_, ay - rr_ * 0.6, ax + rr_, ay + rr_ * 0.6], outline=lerpc((255, 255, 255), (120, 60, 140), k / 0.5), width=2)
        burst(img, d, k, ax, ay, BURST, 1.4)
        if k < 0.15: darken(img, 0.55 * (1 - k / 0.15), (255, 250, 240))
    else:
        f = ease(span(lt, h3, h3 + 1.2))
        for k, u in ((0, lerp(0.5, 0, f)), (1, lerp(0.5, 1, f))):
            if f >= 1: break
            x, y = bz(u)
            heart_at(img, x - (1 - f) * (3 if k == 0 else -3) * (f < 0.15), y, lerp(13, 4, f), k)
        if 0 < lt - h3 - 1.2 < 0.6:
            for (wx, wy), col in ((WIN_A, YEL), (WIN_B, BLU_L)):
                rr_ = 4 + (lt - h3 - 1.2) * 60
                d.ellipse([wx - rr_, wy - rr_ * 0.7, wx + rr_, wy + rr_ * 0.7], outline=col)
    ti = pix.META.get('ti', '')
    if ti and lt < h3:
        lay = Image.new('RGBA', (W, H))
        title(lay, ti, 240, 38, 3, lt, t_in + 0.1, 0.07, ((lt - t_in - 1.6) / 0.9) if t_in + 1.6 < lt < t_in + 2.8 else None)
        ar = pix.META.get('ar', '')
        if ar and lt > t_in + 0.9:
            n = min(len(ar), int((lt - t_in - 0.9) / 0.08) + 1)
            text(lay, ar[:n], 240, 74, (236, 226, 255), (40, 24, 70))
        out = span(lt, h3 - 0.9, h3 - 0.1)
        if out > 0:
            a = np.array(lay); a[..., 3] = np.where(BAYER_A < out, 0, a[..., 3]); lay = Image.fromarray(a)
        img.paste(lay, (0, 0), lay)


# ---------------------------------------------------------------- 第 1 句：分屏，两个人都在加班
def office_half(lt, T, who, busy, look):
    """左右分屏的一半，按“人朝右”画；他的那一半画完后左右翻转"""
    im = Image.new('RGB', (240, H)); d = ImageDraw.Draw(im)
    girl = who == 'girl'
    wall = ((60, 48, 96), (40, 32, 72)) if girl else ((42, 54, 96), (28, 34, 66))
    im.paste(pix.vgrad(240, 214, ((0, wall[1]), (1, wall[0])), 4), (0, 0))
    for x in range(8, 240, 16): d.line([(x, 0), (x, 213)], fill=lerpc(wall[0], (0, 0, 0), 0.08))
    # 窗外的夜景
    d.rectangle([14, 26, 92, 110], fill=(96, 70, 54))
    d.rectangle([18, 30, 88, 106], fill=(14, 14, 44))
    for x, y, p, k in pix.STARS[:30]:
        if math.sin(T * 2 + p) > 0: d.point((18 + x % 70, 30 + y % 40), fill=(220, 220, 255))
    moon(d, 72, 46 - 3 * math.sin(T * 0.1), 6)
    city(im, d, 106, 40 + girl, T * 1.5, (40, 34, 78), (255, 210, 120), 10, 40, 0.4, T, 6, 12)
    d.rectangle([53, 30, 54, 106], fill=(96, 70, 54)); d.rectangle([18, 67, 88, 68], fill=(96, 70, 54))
    # 钟和书架
    clock_face(d, 140, 42, 12, T if not busy else T * 14, 1.0)
    d.rectangle([108, 76, 196, 78], fill=(110, 80, 60))
    rr = rng(3 if girl else 4)
    x = 110
    while x < 192:
        bw = rr.randint(3, 6); bh = rr.randint(10, 16)
        d.rectangle([x, 76 - bh, x + bw - 1, 75], fill=rr.choice([(220, 90, 90), (90, 160, 210), (240, 200, 90), (120, 190, 120), (200, 140, 220)]))
        x += bw + (1 if rr.random() < 0.3 else 0)
    # 地板
    d.rectangle([0, 214, 240, H], fill=(120, 84, 66) if girl else (92, 80, 84))
    for y in range(218, H, 8): d.line([(0, y), (240, y)], fill=(104, 72, 58) if girl else (78, 68, 74))
    # 椅子
    d.rectangle([118, 199, 148, 202], fill=(70, 60, 80)); d.rectangle([114, 156, 120, 202], fill=(80, 70, 92))
    d.rectangle([131, 203, 134, 212], fill=(60, 52, 70)); d.rectangle([122, 212, 144, 213], fill=(60, 52, 70))
    # 人
    typing = busy or lt < 0.4
    arms = 'type' if typing else 'phone'
    ph = int(T * (14 if busy else 6)) % 2 if typing else 0
    expr = 'worried' if busy else ('smile' if look < 0.5 else 'blush')
    person(im, who, 136, 214, 'adult', 'side', 'sit', ph, expr, arms, 2)
    # 桌子、显示器、台灯、杯子、文件
    d.rectangle([96, 186, 230, 190], fill=(150, 104, 72)); d.rectangle([96, 190, 230, 192], fill=(116, 78, 54))
    d.rectangle([100, 192, 104, 214], fill=(116, 78, 54)); d.rectangle([222, 192, 226, 214], fill=(116, 78, 54))
    d.rectangle([186, 176, 192, 186], fill=(60, 60, 76))
    d.rectangle([166, 136, 214, 178], fill=(50, 50, 66))
    scr = (255, 120, 120) if busy and int(T * 4) % 2 else ((200, 232, 255) if girl else (190, 220, 255))
    d.rectangle([169, 139, 211, 175], fill=lerpc(scr, (60, 70, 110), 0.35))
    for k in range(7):
        ln = (k * 37 + int(T * (20 if busy else 3))) % 30
        d.line([(172, 142 + k * 5), (172 + ln, 142 + k * 5)], fill=lerpc(scr, (255, 255, 255), 0.4))
    glow(im, 190, 157, 40, scr, 0.18)
    d.rectangle([152, 184, 172, 185], fill=(220, 220, 230))
    if girl:
        lx = 104
        d.rectangle([lx, 182, lx + 10, 185], fill=(80, 70, 70)); d.line([(lx + 5, 182), (lx + 1, 162), (lx + 10, 152)], fill=(80, 70, 70), width=2)
        d.polygon([(lx + 6, 150), (lx + 18, 150), (lx + 22, 158), (lx + 2, 158)], fill=(240, 196, 80))
        tfill(im, 'polygon', [(lx + 2, 158), (lx + 22, 158), (lx + 50, 186), (lx - 14, 186)], (255, 220, 140), 0.18)
        glow(im, lx + 12, 158, 26, (255, 220, 140), 0.35)
        d.rectangle([150, 178, 156, 185], fill=(240, 240, 240)); d.rectangle([156, 180, 158, 183], fill=(240, 240, 240))
        if not busy: steam(im, d, 153, 176, T, 2, 16)
        for k in range(3): d.rectangle([170 + k * 8, 136, 175 + k * 8, 140], fill=(255, 236, 110))   # 便利贴
    else:
        d.rectangle([104, 176, 112, 185], fill=(120, 170, 220)); d.rectangle([104, 174, 112, 175], fill=(230, 230, 240))
        for k, x in enumerate((200, 210, 218)):    # 越摞越多的咖啡杯
            if k < 1 + int(busy * 3): d.rectangle([x, 178, x + 5, 185], fill=(240, 236, 226)); d.rectangle([x, 178, x + 5, 179], fill=(120, 80, 60))
        for k in range(5 if busy else 2):
            bx = 40 + k * 23 + (k * 7) % 5; by = 222 + (k * 5) % 9
            d.ellipse([bx, by, bx + 7, by + 6], fill=(236, 236, 240)); d.point((bx + 3, by + 2), fill=(190, 190, 200))
        d.rectangle([20, 176, 30, 214], fill=(110, 80, 70))
        for k in range(4): d.ellipse([12 + k * 5, 150 - (k % 2) * 6, 26 + k * 5, 170 - (k % 2) * 6], fill=(70, 150, 90))
    stack = 3 + int(busy * min(9, (lt - 3.2) * 3))
    for k in range(stack):
        y = 185 - k * 2
        d.rectangle([224 - 26 + (k % 2), y - 1, 224 - 6 + (k % 2), y], fill=(246, 244, 236) if k % 2 else (226, 224, 214))
    return im


def s_busy(img, d, lt, dur, T, A):
    split = 3.2
    busy = lt > split
    look = span(lt, 0.4, 1.0)
    left = office_half(lt, T, 'girl', busy, look)
    right = office_half(lt, T, 'boy', busy, look).transpose(Image.FLIP_LEFT_RIGHT)
    img.paste(left, (0, 0)); img.paste(right, (240, 0))
    # 想念的泡泡：她头上是他，他头上是她
    if not busy:
        f = span(lt, 0.9, 1.4)
        for x, other, tail in ((150, 'boy', 1), (330, 'girl', -1)):
            c = bubble(img, d, x, 152, 48, 34, f, thought=True, tail=(tail, 1))
            if c:
                hi = head_img(other, 'adult', 'smile', 2)
                img.paste(hi, (int(c[0] - 22), int(c[1] - 16)), hi)
                put(img, 'heart', c[0] + 12, c[1] - 6 + 2 * math.sin(lt * 5), 1)
        for x in (166, 316):
            glow(img, x, 140, 10, (200, 230, 255), 0.4)
    else:
        k = lt - split
        if k < 0.35:
            for x in (150, 330): burst(img, d, k, x, 118, BURST[::4], 0.35, 0.3)
        for i in range(10):     # 新邮件一封封飞进屏幕
            t0 = split + 0.1 + i * 0.32
            f = (lt - t0) / 0.6
            if 0 <= f < 1:
                for sx, tx in ((60 + i * 17 % 90, 190), (420 - i * 17 % 90, 290)):
                    x = lerp(sx, tx, ein(f)); y = lerp(-10, 156, ein(f))
                    put(img, 'mail', x, y)
        for x in (150, 330):
            if int(lt * 3) % 2: text(img, '!', x + 12, 104, (255, 90, 90), OUT, scale=2)
            pix.put(img, 'drop', x - 14, 128 + (lt * 20) % 8)
    # 中间的墙：两半心各在一边
    d.rectangle([238, 0, 241, H], fill=(24, 18, 40)); d.line([(239, 0), (239, H)], fill=(90, 80, 130))
    p = pulse(T, 0.4)
    heart_at(img, 232 - p, 60, 9 + p, 0); heart_at(img, 248 + p, 60, 9 + p, 1)
    vig(img, 0.3)


s_busy.tr = 'windows'; s_busy.tr_dur = 0.7; s_busy.tr_at = (WIN_A, WIN_B)


# ---------------------------------------------------------------- 第 2 句：想象里一起吃火锅
def lantern(img, d, x, y, t, i, col=(226, 60, 60)):
    sw = 2 * math.sin(t * 1.6 + i)
    d.line([(x, y - 14), (x + sw, y)], fill=(60, 40, 40))
    cx = x + sw
    d.ellipse([cx - 7, y, cx + 7, y + 14], fill=col)
    d.rectangle([cx - 4, y - 1, cx + 3, y + 1], fill=(250, 200, 80)); d.rectangle([cx - 4, y + 13, cx + 3, y + 15], fill=(250, 200, 80))
    d.line([(cx - 3, y + 2), (cx - 3, y + 12)], fill=lerpc(col, (255, 200, 150), 0.4))
    d.line([(cx, y + 16), (cx, y + 20)], fill=(250, 200, 80))
    glow(img, cx, y + 7, 22, (255, 140, 90), 0.3)


def s_hotpot(img, d, lt, dur, T, A):
    sky(img, ((0, (16, 14, 44)), (1, (54, 34, 76))), 0, 110)
    stars(d, T, 60, 0.8, 60)
    # 远处的小吃摊
    for i, (x0, w, col, sign) in enumerate([(-6, 110, (200, 70, 70), '烧烤'), (112, 96, (220, 150, 60), '甜品'), (318, 104, (90, 150, 200), '面馆'), (430, 70, (200, 90, 140), '')]):
        d.rectangle([x0, 84, x0 + w, 168], fill=(70, 50, 70))
        d.rectangle([x0 + 4, 104, x0 + w - 4, 160], fill=(250, 196, 120))
        for k in range(0, w, 10):
            d.rectangle([x0 + k, 84, x0 + k + 4, 96], fill=col); d.rectangle([x0 + k + 5, 84, x0 + k + 9, 96], fill=(250, 240, 230))
        d.polygon([(x0, 96), (x0 + w, 96), (x0 + w - 2, 99), (x0 + 2, 99)], fill=lerpc(col, (0, 0, 0), 0.2))
        if sign: text(img, sign, x0 + w / 2, 76, (255, 250, 230), (120, 40, 40), FONT_S)
        for k in range(3):
            px = x0 + 14 + k * (w - 20) / 3
            person(img, 'girl' if (i + k) % 2 else 'boy', px, 168, 'adult', 'side', 'stand', 0, 'smile', 'down', 1, flip=k % 2 == 1, tint=(110, 76, 90))
        glow(img, x0 + w / 2, 130, 60, (255, 190, 120), 0.18)
    # 串灯和灯笼
    for i in range(0, W, 6):
        y = 20 + 10 * math.sin(math.pi * (i % 160) / 160)
        d.point((i, y), fill=(60, 50, 60))
        if i % 18 == 0:
            on = (i // 18 + int(T * 2)) % 3 != 0 or pulse(T, 0.3) > 0.5
            c = [(255, 120, 120), (255, 220, 110), (130, 220, 255), (190, 255, 150)][(i // 18) % 4]
            d.rectangle([i - 1, y + 1, i + 1, y + 3], fill=c if on else lerpc(c, (40, 30, 50), 0.6))
            if on: glow(img, i, y + 2, 6, c, 0.4)
    for i, x in enumerate((40, 150, 330, 440)): lantern(img, d, x, 44 + (i % 2) * 8, T, i)
    blend_box(img, (0, 64, W, 176), (40, 24, 60), np.full((112, W), 0.3))    # 远景压暗，突出前景
    # 地面、两个人、桌子
    d.rectangle([0, 168, W, H], fill=(70, 52, 60))
    for x in range(0, W, 24): d.line([(x, 168), (x - 30, H)], fill=(62, 46, 54))
    ph = int(T * 3) % 2
    talk = int(lt / 0.98) % 2
    person(img, 'girl', 120, 227, 'adult', 'side', 'sit', ph, 'laugh' if talk == 0 else 'happy', 'eat', 3)
    person(img, 'boy', 360, 227, 'adult', 'side', 'sit', 1 - ph, 'laugh' if talk == 1 else 'happy', 'eat', 3, flip=True)
    for x, sgn, k in ((120, 1, ph), (360, -1, 1 - ph)):          # 筷子伸向锅里
        hx = x + sgn * 16; hy = 227 - 39 - 3 * k
        d.line([(hx, hy), (hx + sgn * 34, hy - 4 + 6 * k)], fill=(214, 172, 120))
        d.line([(hx, hy + 2), (hx + sgn * 34, hy - 1 + 6 * k)], fill=(190, 150, 100))
    d.rectangle([56, 194, 424, 198], fill=(240, 234, 224))
    for x in range(56, 424, 10):
        for y in range(198, 240, 10):
            d.rectangle([x, y, x + 9, y + 9], fill=(214, 70, 70) if (x // 10 + y // 10) % 2 else (250, 242, 234))
    d.line([(56, 198), (424, 198)], fill=(200, 190, 180))
    # 鸳鸯锅：她那边是红汤，他那边是清汤
    d.ellipse([174, 182, 306, 202], fill=(130, 76, 52))
    d.rectangle([174, 166, 306, 192], fill=(160, 98, 64))
    for x in range(180, 304, 9): d.line([(x, 168), (x, 190)], fill=(176, 112, 74))
    d.ellipse([174, 154, 306, 178], fill=(124, 72, 50))
    d.pieslice([180, 157, 300, 175], 90, 270, fill=(216, 62, 40))
    d.pieslice([180, 157, 300, 175], 270, 90, fill=(244, 206, 120))
    d.line([(240, 157), (240, 175)], fill=(250, 230, 190), width=2)
    for k in range(10):
        f = (lt * 1.5 + k * 0.37) % 1
        bx = 188 + (k * 23) % 104; by = 164 + (k * 7) % 7
        r = 1 + 2 * f
        d.ellipse([bx - r, by - r * 0.6, bx + r, by + r * 0.6], outline=(255, 150, 110) if bx < 240 else (255, 240, 200))
    for k in range(6):
        fx = 192 + k * 17 + int(2 * math.sin(lt * 2 + k)); fy = 162 + (k % 2) * 6
        d.rectangle([fx, fy, fx + 5, fy + 2], fill=[(250, 220, 210), (110, 190, 90), (240, 236, 200)][k % 3])
    d.rectangle([166, 164, 174, 169], fill=(124, 72, 50)); d.rectangle([306, 164, 314, 169], fill=(124, 72, 50))
    steam(img, d, 222, 150, T, 4, 64, (255, 240, 236), 0.5, 10)
    steam(img, d, 258, 150, T + 0.5, 4, 64, (255, 250, 246), 0.5, 10)
    # 盘子和饮料
    for x, food in ((76, (250, 190, 190)), (136, (120, 200, 100)), (344, (250, 236, 190)), (404, (250, 170, 170))):
        d.ellipse([x - 16, 189, x + 16, 197], fill=(250, 250, 250)); d.ellipse([x - 11, 188, x + 11, 193], fill=food)
    for x, c in ((160, (255, 170, 60)), (320, (255, 120, 130))):
        d.rectangle([x - 4, 172, x + 4, 193], fill=lerpc(c, (255, 255, 255), 0.35)); d.rectangle([x - 3, 177, x + 3, 192], fill=c)
        d.line([(x + 1, 172), (x + 5, 164)], fill=(255, 255, 255))
    # 聊天的泡泡
    lines = [('♥', 'girl'), ('哈哈', 'boy'), ('♪', 'girl'), ('好吃', 'boy'), ('!', 'girl'), ('嗯嗯', 'boy'), ('♥', 'girl'), ('♥', 'boy')]
    k = int(lt / 0.98)
    if k < len(lines):
        s, who = lines[k]
        f = clamp((lt - k * 0.98) / 0.25)
        x = 150 if who == 'girl' else 330
        c = bubble(img, d, x, 134, 34, 20, f, tail=(1 if who == 'girl' else -1, 1))
        if c:
            if s == '♥': put(img, 'heart', c[0], c[1], 1)
            elif s == '♪': put(img, 'note', c[0], c[1], 1)
            else: text(img, s, c[0], c[1], (60, 40, 60), None, FONT_S, shadow=False)
    # 梦一样的粉色边框
    vig(img, 0.45, (120, 60, 110))
    for i in range(14):
        a = i / 14 * 2 * math.pi + lt * 0.3
        x = 240 + math.cos(a) * 250; y = 135 + math.sin(a) * 150
        twinkle(d, int(clamp(x, 4, 476)), int(clamp(y, 4, 266)), (lt * 0.8 + i * 0.3) % 1, (255, 220, 240), 3)


s_hotpot.tr = 'iris'; s_hotpot.tr_dur = 0.8; s_hotpot.tr_at = (150, 130)


# ---------------------------------------------------------------- 第 3 句：地铁站，隔着轨道错过
def train_img(cars=3, stripe=(80, 190, 180), lit=True, h=84):
    """地铁列车，车头朝左。h 是整车高度（含车轮）。返回 RGBA"""
    cw = 150
    im = Image.new('RGBA', (cars * cw + 10, h)); d = ImageDraw.Draw(im)
    for k in range(cars):
        x0 = k * cw
        d.rounded_rectangle([x0 + 2, 2, x0 + cw - 2, h - 6], radius=6 if k == 0 else 2, fill=(206, 212, 222))
        d.rectangle([x0 + 2, h - 30, x0 + cw - 2, h - 24], fill=stripe)
        d.rectangle([x0 + 2, h - 23, x0 + cw - 2, h - 20], fill=(170, 176, 190))
        for j, wx in enumerate(range(x0 + 14, x0 + cw - 20, 30)):
            d.rectangle([wx, h - 70, wx + 18, h - 44], fill=(40, 50, 80))
            if lit: d.rectangle([wx + 1, h - 69, wx + 17, h - 62], fill=(150, 170, 200))
            rr = rng(k * 10 + j)
            if rr.random() < 0.7:
                hx = wx + 4 + rr.randint(0, 8)
                d.ellipse([hx, h - 60, hx + 6, h - 53], fill=(60, 60, 90)); d.rectangle([hx - 1, h - 53, hx + 7, h - 44], fill=(60, 60, 90))
        dx = cw // 2 - 12
        d.rectangle([x0 + dx, h - 74, x0 + dx + 22, h - 10], fill=(180, 186, 198)); d.line([(x0 + dx + 11, h - 74), (x0 + dx + 11, h - 10)], fill=(120, 126, 140))
        d.rectangle([x0 + dx + 3, h - 68, x0 + dx + 9, h - 48], fill=(40, 50, 80)); d.rectangle([x0 + dx + 13, h - 68, x0 + dx + 19, h - 48], fill=(40, 50, 80))
        for wx in (x0 + 18, x0 + cw - 30):
            d.ellipse([wx, h - 12, wx + 12, h], fill=(50, 50, 60))
    d.rectangle([0, h - 74, 10, h - 40], fill=(40, 50, 80))
    d.rectangle([2, h - 18, 8, h - 14], fill=(255, 250, 200))
    return im


TRAIN = None


def s_subway(img, d, lt, dur, T, A):
    global TRAIN
    if TRAIN is None: TRAIN = train_img(3, h=98)
    # 墙面瓷砖、广告和电子钟
    d.rectangle([0, 0, W, 140], fill=(160, 178, 186))
    for y in range(0, 140, 8): d.line([(0, y), (W, y)], fill=(146, 164, 172))
    for x in range(0, W, 12): d.line([(x, 0), (x, 140)], fill=(150, 168, 176))
    d.rectangle([0, 0, W, 10], fill=(60, 64, 80))
    for x in range(20, W, 80):
        d.rectangle([x, 10, x + 50, 13], fill=(240, 250, 255)); glow(img, x + 25, 13, 30, (220, 240, 255), 0.25)
    d.rectangle([0, 58, W, 64], fill=(250, 200, 70))
    d.rectangle([180, 22, 300, 46], fill=(40, 70, 140))
    text(img, '← 1号线 →', 240, 34, (255, 255, 255), None, FONT_S, shadow=False)
    for x0, art in ((40, 0), (360, 1)):
        d.rectangle([x0, 74, x0 + 60, 126], fill=(250, 248, 240)); d.rectangle([x0 + 3, 77, x0 + 57, 123], fill=(255, 190, 200) if art == 0 else (170, 210, 250))
        if art == 0: heart_at(img, x0 + 30, 98, 9)
        else: moon(d, x0 + 30, 96, 10); stars(d, T, 0, 0)
    d.rectangle([214, 70, 266, 88], fill=(30, 30, 40))
    hh = 23; mm = 8 + int(lt / 2.5)
    text(img, f'{hh}:{mm:02d}', 240, 79, (255, 120, 90), None, FONT_S, shadow=False)
    # 对面站台
    d.rectangle([0, 0, W, 10], fill=(60, 64, 80))
    d.rectangle([0, 140, W, 168], fill=(176, 172, 168)); d.rectangle([0, 165, W, 168], fill=(250, 210, 70))
    tx_head = None
    arrive, stop, leave = 2.5, 3.2, 5.3
    if lt < arrive: tx = None
    elif lt < stop: tx = lerp(W + 10, 20, eout((lt - arrive) / (stop - arrive)))
    elif lt < leave: tx = 20
    else: tx = 20 - ein(min(1, (lt - leave) / 1.6)) * 560
    gone = lt > 4.0
    rr = rng(9)
    for k in range(6):
        px = (k * 83 + 30) % W
        if abs(px - 330) < 30: continue
        person(img, 'girl' if k % 2 else 'boy', px, 166, 'adult', 'front' if k % 3 else 'side', 'stand', 0, 'smile', 'phone' if k % 2 else 'down', 2,
               flip=k % 2 == 0, tint=(130, 132, 150))
    if not gone:
        person(img, 'boy', 330, 166, 'adult', 'front', 'stand', 0, 'down', 'phone', 2)
        glow(img, 330, 134, 8, (190, 230, 255), 0.5)
    # 轨道
    d.rectangle([0, 168, W, 202], fill=(46, 44, 52))
    for x in range(0, W, 14): d.rectangle([x, 193, x + 8, 197], fill=(80, 70, 66))
    d.line([(0, 191), (W, 191)], fill=(150, 150, 160)); d.line([(0, 198), (W, 198)], fill=(150, 150, 160))
    if tx is not None:
        img.paste(TRAIN, (int(tx), 100), TRAIN)
        if lt < stop or lt > leave:
            for k in range(8):
                y = 110 + k * 10
                x = tx + TRAIN.width + 6 + (k * 23) % 40
                d.line([(x, y), (x + 30, y)], fill=(230, 236, 246))
        glow(img, tx + 4, 182, 16, (255, 250, 200), 0.5)
    # 这边站台
    d.rectangle([0, 202, W, H], fill=(196, 192, 186))
    d.rectangle([0, 202, W, 208], fill=(250, 210, 70))
    for x in range(0, W, 6): d.point((x + 2, 205), fill=(220, 180, 60))
    for y in range(214, H, 14): d.line([(0, y), (W, y)], fill=(182, 178, 172))
    # 匆匆走过的人
    for k in range(4):
        sp = 70 + k * 30
        x = (k * 131 + lt * sp * (1 if k % 2 else -1)) % (W + 120) - 60
        person(img, 'boy' if k % 2 else 'girl', x, 224, 'adult', 'side', 'walk', wph(lt + k, 10), 'neutral', 'auto', 2, flip=k % 2 == 0,
               tint=(96, 92, 122), alpha=0.85)
    look_up = 1.6 < lt < 2.7
    expr = 'surprised' if look_up else ('sad' if lt > 6.2 else 'down')
    person(img, 'girl', 110, 238, 'adult', 'side', 'stand', 0, expr, 'down' if look_up or lt > 6.2 else 'phone', 3)
    if not look_up and lt <= 6.2: glow(img, 126, 165, 10, (190, 230, 255), 0.5)
    vig(img, 0.25, (20, 30, 50))


# ---------------------------------------------------------------- 第 4 句：月亮下面跑向对方，拥抱
def s_hug(img, d, lt, dur, T, A):
    sky(img, ((0, (10, 8, 40)), (0.6, (44, 28, 96)), (1, (110, 64, 140))), 0, 200)
    stars(d, T, 190, 1, 200)
    mx, my = 240, 150
    glow(img, mx, my, 130, (255, 220, 230), 0.35 + 0.1 * pulse(T, 0.5))
    moon(d, mx, my, 64, (255, 246, 214))
    for i, (cx, cy, s) in enumerate([(30, 60, 2), (300, 40, 1), (380, 96, 2)]):
        cloud(d, int((cx + lt * 6) % 540 - 60), cy, s, (70, 50, 120), (56, 40, 100))
    hills(d, 200, 6, 0.02, 1, (40, 26, 70))
    d.rectangle([0, 212, W, H], fill=(30, 20, 56))
    for i in range(70):
        x = (i * 47) % W; y = 204 + (i * 13) % 50
        flower(d, x, y, [(255, 150, 190), (255, 230, 120), (180, 160, 255)][i % 3], 0, (50, 90, 80), 2)
    meet = 2.0
    f = eout(lt / meet)
    gx = lerp(-20, 228, f); bx = lerp(500, 252, f)
    sil = (34, 22, 56)
    if lt < meet:
        ph = wph(lt, 12)
        for who, x, fl in (('girl', gx, False), ('boy', bx, True)):
            person(img, who, x, 214, 'young', 'side', 'run', ph, 'happy', 'auto', 2, flip=fl)
    else:
        k = lt - meet
        lean = min(1, k / 0.3) * 2
        person(img, 'boy', 252 - lean, 214, 'young', 'side', 'stand', 0, 'closed', 'hug', 2, flip=True, tint=sil)
        person(img, 'girl', 228 + lean, 214, 'young', 'side', 'stand', 0, 'closed', 'hug', 2, tint=sil)
        if k < 0.4:
            for s in (-1, 1): d.ellipse([240 + s * 22 - 6, 208, 240 + s * 22 + 6, 214], outline=(255, 230, 240))
        # 两半心从两人头上升起，在上方合成一颗
        mf = span(k, 0.6, 1.8)
        if mf < 1:
            y = lerp(160, 96, eout(mf))
            heart_at(img, lerp(224, 236, ease(mf)), y, 8 + 4 * mf, 0); heart_at(img, lerp(256, 244, ease(mf)), y, 8 + 4 * mf, 1)
        else:
            r = 12 + 2 * pulse(T, 0.4)
            glow(img, 240, 96, 30, (255, 200, 220), 0.4)
            heart_at(img, 240, 96, r)
            if k - 1.8 < 0.6: burst(img, d, k - 1.8, 240, 96, BURST[::2], 0.9, 0.5)
        if k > 1.0: put(img, 'heart', 240, 160 - (k * 12 % 20), 1, alpha=1 - (k * 12 % 20) / 20)
    petals(d, T, 50, speed=18, wind=24)
    fireflies(img, d, T, 14, (0, 170, W, 230))
    vig(img, 0.35)


# ---------------------------------------------------------------- 第 5 句：四格漫画，再变成星空和时光快进
def panel_ferris(im, d, t, w, h):
    sky(im, ((0, (60, 40, 110)), (1, (250, 150, 120))), 0, h) if False else im.paste(pix.vgrad(w, h, ((0, (70, 46, 120)), (1, (250, 150, 130))), 4))
    cx, cy, r = w * 0.6, h * 0.5, h * 0.36
    d.line([(cx, cy), (cx - 16, h)], fill=(250, 240, 230), width=2); d.line([(cx, cy), (cx + 16, h)], fill=(250, 240, 230), width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(250, 240, 230))
    for k in range(8):
        a = t * 0.3 + k * math.pi / 4
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        d.line([(cx, cy), (x, y)], fill=(240, 220, 220))
        col = [(255, 120, 140), (120, 200, 255), (255, 220, 100), (150, 230, 140)][k % 4]
        d.rectangle([x - 4, y, x + 4, y + 7], fill=col)
        if k == 0:
            d.rectangle([x - 3, y + 1, x + 3, y + 4], fill=(255, 240, 200))
            d.point((x - 1, y + 2), fill=(126, 76, 50)); d.point((x + 1, y + 2), fill=(52, 54, 82))
            put(im, 'heart', x, y - 6, 1)
    d.rectangle([0, h - 8, w, h], fill=(50, 34, 70))


def panel_aquarium(im, d, t, w, h):
    im.paste(pix.vgrad(w, h, ((0, (30, 90, 160)), (1, (10, 30, 80))), 4))
    for k in range(6):
        x = (k * 37 + t * (10 + k * 3)) % (w + 20) - 10; y = 14 + k * 13
        col = [(255, 160, 80), (255, 230, 90), (120, 230, 255)][k % 3]
        d.ellipse([x, y, x + 8, y + 4], fill=col); d.polygon([(x, y + 2), (x - 4, y - 1), (x - 4, y + 5)], fill=col)
    for k in range(3):
        x = 30 + k * 60; y = 30 + 8 * math.sin(t * 1.5 + k)
        d.pieslice([x - 6, y - 5, x + 6, y + 5], 180, 360, fill=(240, 180, 255))
        for j in range(4): d.line([(x - 4 + j * 3, y), (x - 4 + j * 3 + math.sin(t * 3 + j), y + 8)], fill=(220, 160, 240))
    for k in range(6):
        f = (t * 0.5 + k / 6) % 1
        d.point((10 + k * 37, h - f * h), fill=(200, 240, 255))
    person(im, 'girl', w * 0.42, h, 'young', 'back', 'stand', 0, 'smile', 'hold_r', 1, tint=(20, 30, 60))
    person(im, 'boy', w * 0.42 + 18, h, 'young', 'back', 'stand', 0, 'smile', 'hold_l', 1, tint=(20, 30, 60))


def panel_cook(im, d, t, w, h):
    im.paste(pix.vgrad(w, h, ((0, (255, 236, 200)), (1, (250, 210, 170))), 4))
    for x in range(0, w, 12):
        for y in range(0, h - 30, 12): d.rectangle([x, y, x + 11, y + 11], outline=(240, 220, 190))
    d.rectangle([0, h - 30, w, h - 26], fill=(180, 130, 90)); d.rectangle([0, h - 26, w, h], fill=(150, 100, 70))
    d.rectangle([w // 2 - 14, h - 40, w // 2 + 14, h - 30], fill=(90, 90, 100))
    d.ellipse([w // 2 - 10, h - 44, w // 2 + 10, h - 37], fill=(250, 250, 240)); d.ellipse([w // 2 - 4, h - 42, w // 2 + 4, h - 38], fill=(255, 200, 60))
    steam(im, d, w // 2, h - 46, t, 3, 18)
    person(im, 'girl', w // 2 - 30, h - 4, 'adult', 'side', 'stand', 0, 'happy', 'reach', 1)
    person(im, 'boy', w // 2 + 30, h - 4, 'adult', 'side', 'stand', 0, 'laugh', 'down', 1, flip=True)
    put(im, 'heart', w // 2, h - 60 - 3 * math.sin(t * 4), 1)


def panel_camp(im, d, t, w, h):
    im.paste(pix.vgrad(w, h, ((0, (10, 10, 40)), (1, (40, 40, 90))), 4))
    for x, y, p, k in pix.STARS[:60]:
        if math.sin(t * 2 + p) > -0.3: d.point((x % w, y % (h - 30)), fill=(240, 240, 255))
    meteor(d, t % 3, 0.5, w - 20, 6, -60, 24, 0.7)
    d.rectangle([0, h - 20, w, h], fill=(30, 40, 40))
    d.polygon([(28, h - 20), (52, h - 52), (76, h - 20)], fill=(240, 150, 80)); d.polygon([(46, h - 20), (52, h - 40), (58, h - 20)], fill=(120, 60, 40))
    fx = w * 0.62
    for k in range(3):
        fl = 3 + 2 * math.sin(t * 9 + k * 2)
        d.polygon([(fx - 4 + k * 4, h - 20), (fx - 2 + k * 4, h - 26 - fl), (fx + k * 4, h - 20)], fill=[(255, 120, 60), (255, 210, 80), (255, 150, 60)][k])
    glow(im, fx + 4, h - 24, 30, (255, 160, 80), 0.35)
    person(im, 'girl', fx - 20, h - 18, 'young', 'side', 'sit', 0, 'happy', 'auto', 1)
    person(im, 'boy', fx + 28, h - 18, 'young', 'side', 'sit', 0, 'happy', 'auto', 1, flip=True)


PANELS = [panel_ferris, panel_aquarium, panel_cook, panel_camp]
PANEL_BOX = [(14, 10, 234, 114), (246, 10, 466, 114), (14, 122, 234, 226), (246, 122, 466, 226)]


def hilltop(img, d, lt, T, night, season, age, star_heart=0.0, trails=0.0):
    """山顶上一棵树，两人背对镜头坐着看天。night：0 白天到 1 夜里；season 0..4 春夏秋冬再到春"""
    day = ((0, (110, 170, 240)), (1, (230, 220, 250)))
    nt = ((0, (6, 8, 30)), (0.7, (34, 26, 80)), (1, (90, 56, 120)))
    stops = tuple((p, lerpc(c1, c2, night)) for (p, c1), (_, c2) in zip(((0, day[0][1]), (0.7, lerpc(day[0][1], day[1][1], 0.7)), (1, day[1][1])), nt))
    sky(img, stops, 0, 210, 6)
    if night > 0.3:
        stars(d, T, 205, (night - 0.3) / 0.7, 240)
        # 银河
        for i in range(90):
            r = rng(i)
            x = r.uniform(0, W); y = 40 + x * 0.25 + r.gauss(0, 10)
            d.point((x, y), fill=lerpc((40, 30, 90), (230, 220, 255), (night - 0.3) * r.random()))
    if trails > 0:
        for i, (x, y, p, k) in enumerate(pix.STARS[:80]):
            r0 = math.hypot(x - 240, y - 230)
            a0 = math.atan2(y - 230, x - 240)
            d.arc([240 - r0, 230 - r0, 240 + r0, 230 + r0], math.degrees(a0), math.degrees(a0) + 40 * trails, fill=(200, 200, 255))
    if star_heart > 0:
        pts = [(240 + x * 4.2, 74 + y * 4.0) for x, y in pix.HEART_PTS[::4]]
        n = len(pts)
        m = star_heart * n
        for i in range(n):
            if i < m:
                x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % n]
                if i + 1 <= m: d.line([(x0, y0), (x1, y1)], fill=(150, 160, 230))
            x, y = pts[i]
            if i <= m: twinkle(d, int(x), int(y), 0.5, (255, 250, 220), 2)
    hills(d, 196, 5, 0.012, 0.5, lerpc((90, 150, 110), (26, 22, 50), night))
    leaf = [(255, 180, 210), (80, 170, 90), (230, 130, 60), (240, 246, 255), (255, 180, 210)]
    s0 = int(season) % 5; s1 = min(4, s0 + 1); sf = season - int(season)
    col = lerpc(leaf[s0], leaf[s1], sf)
    col = lerpc(col, (30, 24, 56), night * 0.8)
    d.polygon([(130, 270), (220, 176), (330, 180), (420, 270)], fill=lerpc((110, 170, 100), (34, 28, 64), night))
    tree_round(d, 300, 180, 1.6, col, lerpc(col, (255, 255, 255), 0.25), lerpc((112, 74, 50), (30, 24, 50), night))
    tint = lerpc((60, 50, 80), (24, 18, 44), night) if night > 0.5 else None
    for who, x, arms in (('girl', 236, 'hold_r'), ('boy', 254, 'hold_l')):
        person(img, who, x, 186, age, 'back', 'sit', 0, 'smile', 'down', 1, tint=tint)


def s_more(img, d, lt, dur, T, A):
    panels_end = 4.0
    if lt < panels_end + 0.8:
        bg = pix.vgrad(W, H, ((0, (255, 226, 230)), (1, (255, 240, 214))), 4)
        img.paste(bg)
        for i in range(30):
            twinkle(d, (i * 71) % W, (i * 43) % H, (lt * 0.7 + i * 0.13) % 1, (255, 255, 255), 2)
        starts = [0.05, 0.8, 1.55, 2.3]
        for k, (fn, box, t0) in enumerate(zip(PANELS, PANEL_BOX, starts)):
            f = (lt - t0) / 0.35
            if f < 0: continue
            x0, y0, x1, y1 = box
            w, h = x1 - x0, y1 - y0
            sub = Image.new('RGB', (w, h)); sd = ImageDraw.Draw(sub); sd.fontmode = '1'
            fn(sub, sd, T, w, h)
            fly = clamp((lt - panels_end - k * 0.12) / 0.55)
            if fly > 0:     # 漫画格往上飞，缩成星星
                s = 1 - ein(fly) * 0.95
                sub = sub.resize((max(1, int(w * s)), max(1, int(h * s))), Image.NEAREST)
                tx, ty = [(150, 40), (330, 36), (200, 64), (290, 70)][k]
                cx = lerp((x0 + x1) / 2, tx, ein(fly)); cy = lerp((y0 + y1) / 2, ty, ein(fly))
                img.paste(sub, (int(cx - sub.width / 2), int(cy - sub.height / 2)))
                continue
            off = (1 - eback(f)) * (-300 if k % 2 == 0 else 300)
            d.rectangle([x0 - 3 + off, y0 - 3, x1 + 2 + off, y1 + 2], fill=(40, 30, 50))
            d.rectangle([x0 - 2 + off, y0 - 2, x1 + 1 + off, y1 + 1], fill=(255, 255, 255))
            img.paste(sub, (int(x0 + off), y0))
        if lt > panels_end:
            a = ease((lt - panels_end) / 0.8)
            hill = Image.new('RGB', (W, H)); hd = ImageDraw.Draw(hill)
            hilltop(hill, hd, lt, T, 1.0, 0, 'young')
            img.paste(Image.blend(img, hill, a))
        return
    k = lt - panels_end
    lapse = 10.4
    if lt < lapse:
        hilltop(img, d, lt, T, 1.0, 0, 'young', ease((lt - panels_end - 0.6) / 3.5))
        e = span(lt, 7.5, 10.4)
        for i in range(int(3 + 14 * e)):
            t0 = (i * 0.37) % 1.2
            x0 = 100 + (i * 97) % 380
            meteor(d, (lt * (1 + e)) % 1.2, t0, x0, 6 + (i * 13) % 50, -120, 50, 0.6)
        return
    # 时光快进：天色昼夜轮转，树换季节，两个人慢慢变老
    f = (lt - lapse) / max(0.1, dur - lapse)
    cyc = f * 3.0
    night = 0.5 + 0.5 * math.cos(cyc * 2 * math.pi)
    hilltop(img, d, lt, T, night, f * 4, 'old' if f > 0.55 else 'young', 0, min(1, f * 3) * night)
    clock_face(d, 240, 70, 22, lt * 40, 1, (255, 252, 240), (200, 170, 120))
    if 0.5 < f < 0.65:
        for i in range(6): twinkle(d, 230 + i * 6, 160 - (i % 2) * 8, (f - 0.5) / 0.15, (255, 255, 230), 3)
    if f > 0.75: darken(img, ease((f - 0.75) / 0.25), (255, 250, 240))


# ---------------------------------------------------------------- 第 6 句：以后，老了以后一起在河边散步
FLOWER_COLS = [(255, 120, 150), (255, 220, 90), (190, 140, 255), (255, 160, 90), (255, 250, 250), (255, 100, 110), (140, 200, 255)]


def walk_pair(img, x, y, age, t, s=2, rate=5, expr=('laugh', 'happy'), moving=True, scarf=(None, None)):
    """两人朝右走、手牵手。前面是她（hold 往后伸手），后面是他（hold_f 往前伸手）"""
    ph = wph(t, rate) if moving else 0
    pose = 'walk' if moving else 'stand'
    person(img, 'boy', x - 8 * s, y, age, 'side', pose, (ph + 2) % 4, expr[1], 'hold_f', s, scarf=scarf[1])
    person(img, 'girl', x, y, age, 'side', pose, ph, expr[0], 'hold', s, scarf=scarf[0])


def willow(d, x, base, t, s=1.0):
    d.rectangle([x - 2 * s, base - 44 * s, x + 2 * s, base], fill=(104, 76, 56))
    d.line([(x, base - 30 * s), (x - 10 * s, base - 44 * s)], fill=(104, 76, 56), width=2)
    d.ellipse([x - 28 * s, base - 66 * s, x + 28 * s, base - 38 * s], fill=(118, 172, 84))
    d.ellipse([x - 20 * s, base - 64 * s, x + 6 * s, base - 50 * s], fill=(150, 200, 104))
    for i in range(18):
        fx = x - 26 * s + i * 3 * s
        ln = (18 + (i * 7) % 16) * s
        sw = 2.5 * math.sin(t * 1.4 + i * 0.5)
        d.line([(fx, base - 46 * s), (fx + sw, base - 46 * s + ln)], fill=(118, 172, 84) if i % 2 else (96, 150, 70))


def water(img, d, y0, y1, t, top, bot, n=50, sun_x=None, seed=0):
    sky(img, ((0, top), (1, bot)), y0, y1, 4)
    for i in range(n):
        r = rng(i + seed * 100)
        x = (r.uniform(0, W) + t * r.uniform(-6, 6)) % W
        y = r.uniform(y0 + 2, y1 - 2)
        if math.sin(t * 2.5 + i * 1.3) > 0.3:
            d.line([(x, y), (x + r.randint(2, 6), y)], fill=lerpc(bot, (255, 255, 255), 0.7))
    if sun_x is not None:
        for k in range(10):
            yy = y0 + 2 + k * 3
            w = (12 - k) + 3 * math.sin(t * 3 + k)
            if w > 0: d.line([(sun_x - w, yy), (sun_x + w, yy)], fill=(255, 244, 210))


def duck(d, x, y, t, col=(250, 250, 245)):
    b = int(math.sin(t * 3 + x * 0.1) > 0)
    d.ellipse([x - 5, y - 3 + b, x + 4, y + 2 + b], fill=col)
    d.ellipse([x + 1, y - 7 + b, x + 6, y - 2 + b], fill=col)
    d.point((x + 4, y - 5 + b), fill=(40, 30, 40)); d.rectangle([x + 6, y - 4 + b, x + 8, y - 3 + b], fill=(250, 160, 60))
    d.line([(x - 8, y + 3), (x - 15, y + 3)], fill=(220, 236, 250))


def talk(img, d, lt, seq, xs, y, step=1.3, w=28):
    """轮流冒出的对话泡泡。seq = [(内容, 'girl'/'boy'), ...]，xs = {'girl': 尾巴x, 'boy': 尾巴x}"""
    k = int(lt / step)
    if k >= len(seq): return
    s_, who = seq[k]
    f = clamp((lt - k * step) / 0.25) * clamp((step - (lt - k * step)) / 0.15)
    c = bubble(img, d, xs[who], y, w, 18, f, tail=(1 if xs[who] > 240 else -1, 1))
    if c:
        if s_ == '♥': put(img, 'heart', c[0], c[1], 1)
        elif s_ == '♪': put(img, 'note', c[0], c[1], 1)
        else: text(img, s_, c[0], c[1], (60, 40, 60), None, FONT_S, shadow=False)


def s_stroll(img, d, lt, dur, T, A):
    off = lt * 24
    sky(img, ((0, (112, 168, 232)), (0.7, (248, 212, 184)), (1, (255, 228, 196))), 0, 152)
    glow(img, 392, 58, 70, (255, 240, 200), 0.55)
    d.ellipse([378, 44, 406, 72], fill=(255, 248, 220))
    for i, (cx, cy, s) in enumerate([(30, 26, 2), (220, 54, 1), (330, 20, 2), (470, 60, 1)]):
        cloud(d, int((cx - off * 0.1 + lt * 2) % 600 - 70), cy, s, (255, 252, 246), (244, 224, 216))
    hills(d, 140, 7, 0.014, off * 0.004, (160, 176, 206))
    hills(d, 148, 5, 0.022, off * 0.008 + 2, (136, 166, 150))
    bx = 120 - off * 0.25
    d.arc([bx - 50, 128, bx + 50, 188], 180, 360, fill=(196, 190, 200), width=5)
    d.rectangle([bx - 58, 130, bx + 58, 134], fill=(196, 190, 200))
    water(img, d, 152, 196, T, (176, 206, 236), (120, 170, 214), 60, 392)
    for k in range(2):
        duck(d, int((300 + k * 26 - off * 0.7 - lt * 6) % 560 - 40), 176 + k * 7, T + k)
    d.rectangle([0, 194, W, 202], fill=(110, 170, 90))
    for i in range(50):
        flower(d, (i * 23 - off) % (W + 20) - 10, 200, FLOWER_COLS[i % len(FLOWER_COLS)], i % 2, (80, 140, 70), 3)
    d.rectangle([0, 202, W, 240], fill=(220, 204, 178))
    for i in range(14):
        x = (i * 40 - off) % (W + 80) - 40
        d.line([(x, 202), (x - 8, 240)], fill=(200, 184, 158))
    d.line([(0, 221), (W, 221)], fill=(206, 190, 164))
    d.rectangle([0, 240, W, H], fill=(96, 156, 84))
    for i in range(4):
        willow(d, (i * 170 + 60 - off) % 680 - 100, 202, T + i, 1.4)
    walk_pair(img, 252, 230, 'old', lt, 2, 5)
    talk(img, d, lt, [('♪', 'girl'), ('哈哈', 'boy'), ('♥', 'girl'), ('嗯', 'boy'), ('♪', 'girl')], {'girl': 262, 'boy': 228}, 170)
    for i in range(3):
        bird(d, int((lt * 30 + i * 60) % 560 - 40), 40 + i * 9 + int(4 * math.sin(lt * 2 + i)), T, (90, 80, 100), i)
    petals(d, T, 12, wind=10)


s_stroll.tr = 'white'; s_stroll.tr_dur = 0.6


# ---------------------------------------------------------------- 第 7 句：公园长椅，两个褐色调的回忆泡泡
def sepia(im, dark=(74, 48, 34), light=(255, 238, 204)):
    a = np.asarray(im.convert('RGB'), float)
    g = np.clip((a @ np.array([0.3, 0.59, 0.11])) / 255 * 1.08, 0, 1)[..., None]
    return Image.fromarray((np.array(dark) * (1 - g) + np.array(light) * g).astype(np.uint8))


def memory_bubble(img, d, cx, cy, w, h, f, content, tail_to):
    """褐色调的回忆泡泡，content(w, h) 画出里面的小画面"""
    if f <= 0: return
    tx, ty = tail_to
    for k, r in enumerate((2, 3, 5)):
        if f > 0.15 + k * 0.12:
            u = 0.22 + k * 0.2
            px = lerp(tx, cx, u); py = lerp(ty, cy + h / 2, u)
            d.ellipse([px - r - 1, py - r - 1, px + r + 1, py + r + 1], fill=OUT); d.ellipse([px - r, py - r, px + r, py + r], fill=(255, 248, 232))
    s = eback(clamp((f - 0.35) / 0.65))
    bw, bh = int(w * s), int(h * s)
    if bw < 6 or bh < 6: return
    sub = sepia(content(w, h)).resize((bw, bh), Image.NEAREST)
    mask = Image.new('L', (bw, bh)); ImageDraw.Draw(mask).ellipse([0, 0, bw - 1, bh - 1], fill=255)
    d.ellipse([cx - bw / 2 - 3, cy - bh / 2 - 3, cx + bw / 2 + 2, cy + bh / 2 + 2], fill=OUT)
    d.ellipse([cx - bw / 2 - 2, cy - bh / 2 - 2, cx + bw / 2 + 1, cy + bh / 2 + 1], fill=(255, 248, 232))
    img.paste(sub, (int(cx - bw / 2), int(cy - bh / 2)), mask)


def mem_stubborn(t):
    def draw(w, h):
        im = Image.new('RGB', (w, h)); d = ImageDraw.Draw(im); d.fontmode = '1'
        im.paste(pix.vgrad(w, h, ((0, (196, 214, 240)), (1, (240, 240, 230))), 3))
        d.rectangle([0, h - 22, w, h], fill=(170, 200, 140))
        cloud(d, 20, 14, 1, (250, 250, 255))
        turned = int(t * 1.25) % 2 == 1
        if turned: person(im, 'girl', w // 2, h - 14, 'young', 'side', 'stand', 0, 'closed', 'down', 2, flip=True)
        else: person(im, 'girl', w // 2, h - 14, 'young', 'front', 'stand', 0, 'pout', 'cross', 2)
        put(im, 'anger', w // 2 + 18, h - 70 + int(math.sin(t * 8)), 2, tint=(220, 50, 60))
        text(im, '哼!', w // 2 - 34, h - 66, (200, 60, 60), (255, 255, 255), FONT_S)
        for k in range(3):
            x = w // 2 - 30 + k * 4 + int(2 * math.sin(t * 9 + k))
            d.line([(x, h - 40 + k * 3), (x + 4, h - 42 + k * 3)], fill=(90, 90, 110))
        return im
    return draw


def mem_anxious(t):
    def draw(w, h):
        im = Image.new('RGB', (w, h)); d = ImageDraw.Draw(im); d.fontmode = '1'
        im.paste(pix.vgrad(w, h, ((0, (230, 214, 236)), (1, (244, 236, 226))), 3))
        d.rectangle([0, h - 22, w, h], fill=(170, 200, 140))
        fid = (1 if int(t * 5) % 2 else -1)
        person(im, 'boy', w // 2 + fid, h - 14, 'young', 'front', 'stand', 0, 'worried', 'behind', 2)
        bx, by = w // 2 + 16 + fid, h - 46
        d.line([(bx - 2, by + 4), (bx - 4, by + 12)], fill=(70, 150, 70))
        for dx, dy, c in ((0, 0, (255, 110, 150)), (3, -2, (255, 220, 100)), (-2, -3, (255, 160, 200)), (2, 2, (250, 250, 250))):
            d.rectangle([bx + dx - 1, by + dy - 1, bx + dx + 1, by + dy + 1], fill=c)
        put(im, 'drop', w // 2 - 18, h - 64 + (t * 14) % 6)
        put(im, 'drop', w // 2 + 20, h - 70 + (t * 14 + 3) % 6)
        put(im, 'heart', w // 2 - 30, h - 60, 2 if int(t * 5) % 2 else 1)
        return im
    return draw


def bench_front(d, x0, x1, seat_y, col=(176, 116, 74), col2=(140, 88, 58), iron=(62, 58, 72)):
    for k in range(3):
        d.rectangle([x0, seat_y - 26 + k * 7, x1, seat_y - 22 + k * 7], fill=col if k % 2 == 0 else col2)
    d.rectangle([x0 + 4, seat_y - 28, x0 + 7, seat_y], fill=iron); d.rectangle([x1 - 7, seat_y - 28, x1 - 4, seat_y], fill=iron)
    d.rectangle([x0 - 3, seat_y, x1 + 3, seat_y + 4], fill=col); d.rectangle([x0 - 3, seat_y + 4, x1 + 3, seat_y + 6], fill=col2)
    d.rectangle([x0 + 2, seat_y + 6, x0 + 5, seat_y + 18], fill=iron); d.rectangle([x1 - 5, seat_y + 6, x1 - 2, seat_y + 18], fill=iron)


def park(img, d, T, sun=(80, 74)):
    sky(img, ((0, (140, 182, 232)), (0.8, (255, 220, 192)), (1, (255, 236, 210))), 0, 176)
    glow(img, sun[0], sun[1], 60, (255, 236, 200), 0.5)
    d.ellipse([sun[0] - 13, sun[1] - 13, sun[0] + 13, sun[1] + 13], fill=(255, 248, 220))
    for i, (cx, cy, s) in enumerate([(150, 24, 2), (330, 40, 1)]):
        cloud(d, int((cx + T * 2) % 560 - 60), cy, s, (255, 252, 248), (240, 226, 226))
    city(img, d, 176, 61, 0, (206, 196, 214), None, 20, 50, blink=False)
    d.rectangle([0, 176, W, H], fill=(112, 176, 96))
    for i in range(80):
        x = (i * 37) % W; y = 180 + (i * 29) % 80
        d.line([(x, y), (x + 1, y - 2)], fill=(96, 158, 84))
    d.polygon([(150, 270), (210, 214), (270, 214), (330, 270)], fill=(222, 206, 176))
    tree_round(d, 70, 200, 2.6, (70, 150, 84), (100, 182, 100))
    tree_round(d, 420, 196, 2.3, (70, 150, 84), (100, 182, 100))
    lamp(img, d, 336, 214, 0, 60)


def s_bench(img, d, lt, dur, T, A):
    park(img, d, T)
    bench_front(d, 196, 284, 196)
    talking = lt < 6.3
    mouth = 'laugh' if talking and int(lt * 6) % 2 else ('happy' if talking else 'laugh')
    arms = 'wave' if talking and 2.0 < lt < 3.2 else 'lap'
    person(img, 'girl', 222, 214, 'old', 'front', 'sit', wph(lt, 6), mouth, arms, 2)
    person(img, 'boy', 258, 214, 'old', 'front', 'sit', 0, 'happy' if lt < 6.3 else 'laugh', 'lap', 2)
    for k in range(3):     # 地上啄食的鸽子
        px = 120 + k * 26 + int(4 * math.sin(lt * 0.7 + k)); py = 236 + (k % 2) * 6
        peck = int(lt * 3 + k) % 3 == 0
        d.ellipse([px - 4, py - 3, px + 3, py + 1], fill=(150, 150, 166))
        d.rectangle([px + 2, py - 5 + (2 if peck else 0), px + 4, py - 3 + (2 if peck else 0)], fill=(120, 120, 140))
    memory_bubble(img, d, 126, 78, 164, 108, span(lt, 1.0, 1.6), mem_stubborn(lt), (220, 160))
    memory_bubble(img, d, 354, 78, 164, 108, span(lt, 4.0, 4.6), mem_anxious(lt), (260, 160))
    if lt > 6.3:
        for i in range(4):
            f = ((lt - 6.3) * 0.6 + i / 4) % 1
            put(img, 'note', 220 + i * 14 + 4 * math.sin(lt * 3 + i), 168 - f * 40, 1, alpha=1 - f)


# ---------------------------------------------------------------- 第 8 句：玫瑰拱门前抱在一起，再牵手走进花园
def gazebo(d, x, base, col=(250, 248, 240), shade=(214, 210, 200)):
    d.rectangle([x - 26, base - 10, x + 26, base], fill=shade)
    for px in (x - 22, x - 8, x + 6, x + 20): d.rectangle([px, base - 40, px + 3, base - 10], fill=col)
    d.rectangle([x - 28, base - 44, x + 28, base - 40], fill=col)
    d.pieslice([x - 28, base - 70, x + 28, base - 22], 180, 360, fill=col)
    d.rectangle([x - 1, base - 76, x + 1, base - 70], fill=shade)


def fountain(img, d, x, base, t):
    d.ellipse([x - 32, base - 8, x + 32, base + 4], fill=(206, 206, 216))
    d.ellipse([x - 28, base - 7, x + 28, base + 1], fill=(130, 190, 232))
    d.rectangle([x - 3, base - 26, x + 3, base - 4], fill=(214, 214, 224))
    d.ellipse([x - 12, base - 30, x + 12, base - 24], fill=(214, 214, 224))
    for j in range(10):
        f = (j / 10 + t * 1.2) % 1
        for side in (-1, 1):
            px = x + side * 24 * f; py = base - 32 - 12 * f + 26 * f * f
            d.point((px, py), fill=(220, 240, 255) if j % 2 else (160, 210, 250))
        d.point((x, base - 32 - 12 * f), fill=(230, 245, 255))


def rose_arch(d, cx, base, w=70, h=104):
    lat = (250, 248, 240)
    for px in (cx - w // 2, cx + w // 2 - 5):
        d.rectangle([px, base - h + w // 2, px + 5, base], fill=lat)
        for y in range(base - h + w // 2, base - 4, 6): d.line([(px, y), (px + 5, y + 5)], fill=(218, 214, 204))
    d.arc([cx - w // 2, base - h, cx + w // 2, base - h + w], 180, 360, fill=lat, width=5)
    r = rng(77)
    for i in range(110):
        if r.random() < 0.55:
            a = math.pi + r.random() * math.pi
            px = cx + math.cos(a) * (w / 2 - 2) + r.uniform(-4, 4); py = base - h + w / 2 + math.sin(a) * (w / 2 - 2) + r.uniform(-4, 4)
        else:
            px = cx + r.choice((-1, 1)) * (w / 2 - 2) + r.uniform(-5, 5); py = r.uniform(base - h + w / 2, base - 6)
        if r.random() < 0.55:
            d.rectangle([px - 1, py - 1, px + 1, py + 1], fill=(70, 150, 80) if r.random() < 0.5 else (104, 184, 92))
        else:
            c = r.choice([(255, 110, 140), (255, 160, 190), (240, 80, 100), (255, 240, 240)])
            d.rectangle([px - 1, py - 1, px + 2, py + 2], fill=c); d.point((px, py), fill=lerpc(c, (255, 255, 255), 0.5))


def picket(d, off, y=200, col=(250, 250, 246), shade=(214, 212, 206)):
    d.rectangle([0, y - 14, W, y - 12], fill=shade); d.rectangle([0, y - 6, W, y - 4], fill=shade)
    for i in range(-1, W // 8 + 2):
        x = i * 8 - int(off) % 8
        d.rectangle([x, y - 18, x + 4, y], fill=col); d.point((x + 2, y - 19), fill=col)


GARDEN_DAY = ((0, (126, 182, 240)), (0.75, (236, 226, 236)), (1, (255, 236, 214)))


def garden(img, d, off, t, stops=GARDEN_DAY, arch_x=None, fence=False, sun=(404, 50), bench_x=None):
    """那片花园：树篱、凉亭、喷泉、花圃、玫瑰拱门和小路。off 是镜头往右走过的距离"""
    sky(img, stops, 0, 152)
    if sun:
        glow(img, sun[0], sun[1], 64, (255, 240, 210), 0.5)
        d.ellipse([sun[0] - 13, sun[1] - 13, sun[0] + 13, sun[1] + 13], fill=(255, 248, 224))
    for i, (cx, cy, s) in enumerate([(40, 24, 2), (260, 46, 1), (380, 16, 2)]):
        cloud(d, int((cx - off * 0.05 + t * 2) % 580 - 60), cy, s, (255, 252, 248), (236, 228, 234))
    for i in range(5):
        x = (i * 130 + 40 - off * 0.3) % 650 - 60
        d.ellipse([x - 9, 74, x + 9, 140], fill=(44, 104, 70)); d.ellipse([x - 5, 78, x + 3, 112], fill=(64, 130, 84))
    for i in range(13):
        x = (i * 52 - off * 0.35) % 676 - 72
        d.ellipse([x, 108, x + 62, 152], fill=(58, 122, 78)); d.ellipse([x + 8, 112, x + 40, 130], fill=(78, 146, 92))
    d.rectangle([0, 132, W, 152], fill=(58, 122, 78))
    gx = 380 - off * 0.45
    if -60 < gx < W + 60: gazebo(d, gx, 152)
    fx = 120 - off * 0.55
    if -50 < fx < W + 50: fountain(img, d, fx, 168, t)
    d.rectangle([0, 152, W, 202], fill=(88, 162, 88))
    for i in range(180):
        r = rng(i * 7 + 3)
        y = 156 + (i * 37 % 43)
        par = 0.55 + (y - 152) / 48 * 0.45
        x = (r.uniform(0, 1000) - off * par) % 1000 - 40
        if -4 < x < W + 4: flower(d, x, y, FLOWER_COLS[i % len(FLOWER_COLS)], i % 3, (64, 136, 66), 3 + (y - 152) // 14)
    if bench_x is not None:
        bx = bench_x - off * 0.8
        bench_front(d, bx - 40, bx + 40, 186, (250, 250, 246), (220, 220, 214), (90, 90, 100))
    if arch_x is not None:
        ax = arch_x - off * 0.8
        if -60 < ax < W + 60: rose_arch(d, ax, 202)
    if fence: picket(d, off, 204)
    d.rectangle([0, 202, W, 240], fill=(230, 214, 186))
    for i in range(36):
        x = (i * 37 - off) % (W + 40) - 20; y = 206 + (i * 13) % 30
        d.ellipse([x, y, x + 5, y + 3], fill=(212, 194, 166))
    d.rectangle([0, 200, W, 202], fill=(176, 156, 126)); d.rectangle([0, 240, W, 242], fill=(176, 156, 126))
    d.rectangle([0, 242, W, H], fill=(82, 154, 84))
    for i in range(54):
        x = (i * 29 - off * 1.2) % (W + 30) - 15
        flower(d, x, 268, FLOWER_COLS[(i * 3) % len(FLOWER_COLS)], i % 3, (60, 130, 60), 9 + i % 6)


def s_garden(img, d, lt, dur, T, A):
    hug_end, stop_t = 2.2, 5.0
    off = clamp(lt - hug_end, 0, stop_t - hug_end) * 34
    garden(img, d, off, T, arch_x=240)
    if lt < hug_end:
        lean = min(1, lt / 0.4) * 2
        person(img, 'boy', 254 - lean, 228, 'old', 'side', 'stand', 0, 'closed', 'hug', 2, flip=True)
        person(img, 'girl', 226 + lean, 228, 'old', 'side', 'stand', 0, 'closed', 'hug', 2)
        if lt > 0.6:
            f = (lt - 0.6) / 1.6
            put(img, 'heart', 240, 166 - 20 * f, 2 if f < 0.2 else 1, alpha=1 - f * 0.7)
    elif lt < stop_t:
        walk_pair(img, 252, 228, 'old', lt, 2, 5, ('happy', 'happy'))
    else:
        k = lt - stop_t
        person(img, 'boy', 226, 228, 'old', 'side', 'stand', 0, 'happy', 'down', 2)
        person(img, 'girl', 258, 228, 'old', 'side', 'stand', 0, 'happy' if k < 1 else 'laugh', 'down', 2, flip=True)
        for i in range(10):
            a = i / 10 * 2 * math.pi + k * 1.6
            r = 30 + 6 * math.sin(k * 3 + i)
            d.rectangle([242 + math.cos(a) * r, 196 + math.sin(a) * r * 0.5, 243 + math.cos(a) * r, 197 + math.sin(a) * r * 0.5],
                        fill=PETAL_COLS[i % 3])
    for i in range(4):
        butterfly(d, int(80 + i * 100 + 20 * math.sin(T * 0.8 + i)), int(150 + 20 * math.sin(T * 1.3 + i * 2)), T, FLOWER_COLS[i], i)
    petals(d, T, 26, speed=16, wind=18)
    tfill(img, 'polygon', [(300, 0), (360, 0), (200, 270), (140, 270)], (255, 250, 220), 0.08)
    tfill(img, 'polygon', [(400, 0), (430, 0), (300, 270), (270, 270)], (255, 250, 220), 0.06)


PETAL_COLS = pix.PETAL_COLS


# ---------------------------------------------------------------- 第 9 句：左边下雨、右边出太阳的两半画面
def rain_world(t):
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    im.paste(pix.vgrad(W, 204, ((0, (68, 80, 110)), (1, (124, 136, 162))), 4))
    for i, (cx, cy) in enumerate([(-30, 14), (80, 34), (180, 8), (290, 30), (400, 12)]):
        cloud(d, int(cx + t * 3), cy, 2, (98, 106, 132), (82, 90, 114))
    city(im, d, 204, 71, 0, (90, 100, 124), (160, 170, 150), 20, 70, 0.2, t, blink=False)
    d.rectangle([0, 204, W, H], fill=(72, 84, 104))
    for k in range(7):
        f = (t * 0.7 + k * 0.29) % 1
        px = 20 + k * 31; r = 2 + f * 10
        d.ellipse([px - r, 224 + (k % 3) * 9 - r * 0.25, px + r, 224 + (k % 3) * 9 + r * 0.25], outline=lerpc((170, 190, 220), (72, 84, 104), f))
    rain(d, t, 0, W, 0, 236, 150, (168, 186, 226), 260, -5)
    return im


def sun_world(t):
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    im.paste(pix.vgrad(W, 204, ((0, (255, 214, 120)), (0.6, (255, 236, 170)), (1, (255, 248, 214))), 5))
    sx, sy = 410, 52
    for k in range(12):
        a = t * 0.4 + k * math.pi / 6
        tfill(im, 'polygon', [(sx, sy), (sx + math.cos(a - 0.1) * 300, sy + math.sin(a - 0.1) * 300),
                              (sx + math.cos(a + 0.1) * 300, sy + math.sin(a + 0.1) * 300)], (255, 250, 220), 0.25)
    glow(im, sx, sy, 50, (255, 250, 220), 0.6)
    d.ellipse([sx - 21, sy - 21, sx + 21, sy + 21], fill=(255, 200, 70))
    d.ellipse([sx - 16, sy - 16, sx + 16, sy + 16], fill=(255, 236, 140))
    d.ellipse([sx - 9, sy - 12, sx + 3, sy - 2], fill=(255, 250, 220))
    for i, (cx, cy) in enumerate([(260, 30), (330, 70)]): cloud(d, int(cx + t * 4) % 520 - 40, cy, 1, (255, 255, 255), (255, 240, 220))
    d.rectangle([0, 204, W, H], fill=(140, 200, 96))
    for i in range(60):
        x = (i * 37) % W; y = 208 + (i * 23) % 60
        d.line([(x, y), (x + 1, y - 3)], fill=(120, 186, 84))
    for i in range(9):
        x = 250 + i * 27 + (i % 2) * 6
        sway = int(round(math.sin(t * 2 + i)))
        flower(d, x + sway, 214 + (i % 3) * 4, (255, 210, 60), 3, (80, 150, 60), 22 + (i % 3) * 6)
    for i in range(3): butterfly(d, int(290 + i * 60 + 18 * math.sin(t + i)), int(120 + 14 * math.sin(t * 1.7 + i)), t, (255, 150, 190), i)
    return im


def s_sunrain(img, d, lt, dur, T, A):
    rw, sw = rain_world(T), sun_world(T)
    reach, spread = 4.6, 5.3
    xb = 240 - eout(span(lt, spread, spread + 1.1)) * 260
    zig = np.abs((np.arange(H) // 6) % 2 * 2 - 1) * 3
    left = np.arange(W)[None, :] < (xb + zig[:, None])
    a = np.where(left[..., None], np.asarray(rw), np.asarray(sw))
    if lt < 3.0:
        a = np.where(left[..., None], a, (a * 0.72).astype(np.uint8))
    img.paste(Image.fromarray(a.astype(np.uint8)))
    if -10 < xb < W:
        for y in range(0, H, 2):
            d.point((xb + zig[y], y), fill=(255, 255, 240))
        glow(img, xb, 135, 24, (255, 250, 220), 0.3, 140)
    # 他：头顶一朵自己的小雨云
    cleared = lt > spread + 0.5
    bexpr = 'sad' if lt < spread + 0.4 else ('surprised' if lt < spread + 0.9 else 'happy')
    person(img, 'boy', 120, 230, 'young', 'front', 'stand', 0, bexpr, 'flowers', 3)
    d.rectangle([110, 186, 129, 194], fill=(60, 80, 140)); d.rectangle([110, 186, 129, 187], fill=(230, 230, 240))
    ca = 1 - span(lt, spread + 0.4, spread + 1.0)
    if ca > 0:
        cy = 120 + 2 * math.sin(lt * 2)
        for bx_, by_, r_, c_ in ((104, 12, 9, (70, 74, 98)), (119, 6, 12, (70, 74, 98)), (135, 11, 9, (70, 74, 98)),
                                 (104, 11, 8, (96, 100, 128)), (119, 5, 11, (96, 100, 128)), (135, 10, 8, (96, 100, 128)), (116, 1, 6, (124, 128, 156))):
            tfill(img, 'ellipse', [bx_ - r_, cy + by_ - r_, bx_ + r_, cy + by_ + r_], c_, ca)
        tfill(img, 'rectangle', [97, cy + 13, 143, cy + 20], (84, 88, 114), ca)
        if int(lt * 2.5) % 5 == 0 and ca > 0.5:
            d.line([(122, cy + 22), (118, cy + 30), (123, cy + 30), (119, cy + 38)], fill=(255, 240, 150))
        for k in range(10):
            f = (lt * 2.2 + k * 0.1) % 1
            x = 98 + (k * 7) % 46
            if ca > 0.3: d.line([(x, cy + 22 + f * 40), (x - 1, cy + 26 + f * 40)], fill=(190, 210, 250))
    if cleared:   # 彩虹
        g = ease(span(lt, spread + 0.6, spread + 1.4))
        cols = [(255, 90, 90), (255, 170, 70), (255, 230, 90), (110, 210, 110), (90, 160, 255), (170, 120, 240)]
        for i, c in enumerate(cols):
            r = 92 - i * 4
            d.arc([150 - r, 200 - r, 150 + r, 200 + r], 180, 180 + 180 * g, fill=c, width=4)
    # 她：先在阳光里挥手，再走过来伸手拉他
    if lt < reach:
        person(img, 'girl', 360, 230, 'young', 'front', 'stand', wph(lt, 6), 'happy', 'wave' if lt > 3.0 else 'down', 3)
        if lt > 3.0:
            for i in range(6): twinkle(d, 330 + i * 12, 150 + (i % 2) * 14, (lt * 1.5 + i * 0.2) % 1, (255, 255, 240), 3)
    elif lt < spread:
        x = lerp(360, 236, ease(span(lt, reach, spread)))
        person(img, 'girl', x, 230, 'young', 'side', 'walk', wph(lt, 8), 'happy', 'auto', 3, flip=True)
    else:
        person(img, 'girl', 214, 230, 'young', 'side', 'stand', 0, 'happy', 'reach' if lt < spread + 1.2 else 'down', 3, flip=True)
    if lt > spread + 1.0:
        for i in range(8):
            twinkle(d, 80 + i * 22, 130 + (i % 3) * 20, (lt * 1.2 + i * 0.17) % 1, (255, 255, 240), 3)


# ---------------------------------------------------------------- 第 10 句：啊——花一圈圈开，镜头抬到天上
@lru_cache(None)
def field_flowers():
    r = rng(17); out = []
    for i in range(420):
        y = 150 + (r.random() ** 1.6) * 118
        x = r.uniform(-10, W + 10)
        out.append((x, y, FLOWER_COLS[i % len(FLOWER_COLS)], i % 3, math.hypot((x - 240) * 0.6, (y - 200) * 1.6)))
    return sorted(out, key=lambda f: f[1])


def s_bloom(img, d, lt, dur, T, A):
    tilt = ease(span(lt, 3.2, dur - 0.3))
    oy = tilt * 210
    sk = pix.vgrad(W, H + 210, ((0, (96, 152, 232)), (0.45, (186, 204, 244)), (0.72, (255, 214, 176)), (1, (255, 196, 150))), 6)
    img.paste(sk.crop((0, int(210 - oy), W, int(210 - oy) + H)))
    for i, (cx, cy, s) in enumerate([(30, -130, 2), (250, -90, 2), (380, -170, 1), (120, -40, 1)]):
        cloud(d, int((cx + T * 3) % 560 - 60), cy + oy, s, (255, 252, 248), (236, 226, 236))
    sun_y = 120 + oy
    glow(img, 360, sun_y, 80, (255, 230, 180), 0.55)
    d.ellipse([344, sun_y - 16, 376, sun_y + 16], fill=(255, 244, 210))
    hills(d, 150 + oy, 5, 0.012, 2, (170, 170, 200))
    d.rectangle([0, 152 + oy, W, H + 300], fill=(120, 176, 96))
    wave = lt * 140
    for x, y, c, kind, dist in field_flowers():
        yy = y + oy
        if yy > H + 10: continue
        sz = 0.4 + (y - 150) / 118 * 1.6
        h = int(2 + 6 * sz)
        if dist < wave:
            flower(d, x, yy, c, kind if sz > 0.8 else 0, (70, 140, 66), h)
        else:
            d.line([(x, yy), (x, yy - h + 2)], fill=(70, 140, 66))
            d.point((x, yy - h + 1), fill=(110, 170, 90))
    person(img, 'girl', 232, 200 + oy, 'old', 'front', 'stand', 0, 'happy', 'hold_r', 1)
    person(img, 'boy', 250, 200 + oy, 'old', 'front', 'stand', 0, 'happy', 'hold_l', 1)
    r0 = wave
    if r0 < 400:
        d.ellipse([240 - r0 / 0.6, 200 + oy - r0 / 1.6, 240 + r0 / 0.6, 200 + oy + r0 / 1.6], outline=(255, 250, 220))
    for i in range(60):
        r = rng(i * 13)
        f = (lt * (0.18 + r.random() * 0.2) + r.random()) % 1
        x = r.uniform(0, W) + 20 * math.sin(lt + i)
        y = 260 + oy - f * (300 + oy)
        d.rectangle([x, y, x + 1, y + 1], fill=FLOWER_COLS[i % len(FLOWER_COLS)])
    for i in range(5):
        bird(d, int((lt * 26 + i * 50) % 560 - 40), int(-80 + oy + i * 12), T, (90, 80, 110), i)
    if lt > dur - 1.0: darken(img, ease((lt - dur + 1.0) / 1.0), (255, 244, 222))


# ---------------------------------------------------------------- 间奏：年轻时的回忆，像一卷旧胶片
def film(img, d, T, warm=1.0):
    grade(img, 0.6, (1.04, 0.97, 0.86), (12, 6, -4))
    r = rng(int(T * 30))
    for i in range(90):
        d.point((r.randrange(W), r.randrange(H)), fill=(255, 246, 226) if i % 3 else (60, 44, 34))
    if r.random() < 0.35:
        x = r.randrange(W); d.line([(x, 0), (x + r.randint(-3, 3), H)], fill=(236, 226, 206))
    if r.random() < 0.12: darken(img, 0.06)
    for y0 in (0, H - 14):
        d.rectangle([0, y0, W, y0 + 13], fill=(22, 18, 16))
        off = int(T * 40) % 24
        for x in range(-off, W + 24, 24):
            d.rounded_rectangle([x + 6, y0 + 4, x + 15, y0 + 9], radius=2, fill=(222, 212, 192))
    vig(img, 0.5, (40, 26, 20))


def umbrella(d, x, y, w=30, col=YEL, shade=YEL_S):
    """伞面中心底边在 (x, y)"""
    d.pieslice([x - w, y - w * 0.7, x + w, y + w * 0.7], 180, 360, fill=col)
    for k in range(1, 4):
        d.line([(x, y - w * 0.7), (x - w + k * w / 2, y)], fill=shade)
    for k in range(4):
        d.arc([x - w + k * w / 2, y - 3, x - w + (k + 1) * w / 2, y + 3], 0, 180, fill=shade)
    d.rectangle([x - 1, y - w * 0.7 - 3, x, y - w * 0.7], fill=shade)


def s_umbrella(img, d, lt, dur, T, A):
    sky(img, ((0, (60, 70, 100)), (1, (110, 116, 146))), 0, 170)
    for i, (x0, w, h, sign) in enumerate([(-10, 90, 110, (255, 196, 120)), (86, 70, 80, (255, 220, 160)), (330, 100, 120, (180, 220, 255)), (436, 60, 90, None)]):
        d.rectangle([x0, 170 - h, x0 + w, 200], fill=(70, 74, 100))
        for yy in range(170 - h + 8, 190, 12):
            for xx in range(x0 + 6, x0 + w - 8, 12):
                d.rectangle([xx, yy, xx + 6, yy + 7], fill=(250, 214, 150) if (xx + yy) % 3 else (60, 62, 86))
        if sign:
            d.rectangle([x0 + 8, 176, x0 + w - 8, 196], fill=sign)
            glow(img, x0 + w / 2, 186, 40, sign, 0.3)
    d.rectangle([0, 200, W, H], fill=(64, 70, 92))
    for i, (x0, w, c) in enumerate([(-10, 90, (255, 196, 120)), (86, 70, (255, 220, 160)), (330, 100, (180, 220, 255))]):
        for k in range(10):
            xx = x0 + 10 + k * w / 10
            d.line([(xx, 204 + (k % 3) * 3), (xx, 230 + (k * 7) % 20)], fill=lerpc(c, (64, 70, 92), 0.55))
    # 公交站牌
    d.rectangle([396, 120, 398, 226], fill=(90, 96, 110))
    d.ellipse([386, 108, 408, 130], fill=(70, 130, 210)); d.ellipse([389, 111, 405, 127], fill=(240, 246, 255))
    d.rectangle([392, 116, 402, 122], fill=(70, 130, 210)); d.point([(394, 123), (400, 123)], fill=(40, 40, 50))
    rain(d, T, 0, W, 0, 240, 170, (176, 192, 230), 280, -5)
    for k in range(8):
        f = (lt * 1.3 + k * 0.17) % 1
        px = 30 + k * 57; r = 2 + f * 9
        d.ellipse([px - r, 236 + (k % 3) * 8 - r * 0.25, px + r, 236 + (k % 3) * 8 + r * 0.25], outline=lerpc((190, 206, 236), (64, 70, 92), f))
    if lt < 1.6 and int(lt * 10) in (8, 9): darken(img, 0.3, (230, 236, 255))
    arrive, cover, leave = 6.0, 6.2, 8.4
    if lt < arrive:
        bx = 300
        person(img, 'boy', bx, 228, 'young', 'front', 'stand', 0, 'sad', 'down', 2)
        for k in range(3):
            f = (lt * 3 + k / 3) % 1
            d.point((bx - 8 + k * 7, 172 - 6 * math.sin(math.pi * f)), fill=(220, 230, 255))
        if lt > 2.8:
            gx = lerp(-30, 262, span(lt, 2.8, arrive))
            person(img, 'girl', gx, 228, 'young', 'side', 'walk', wph(lt, 7), 'smile', 'umbrella', 2)
            umbrella(d, gx + 6, 168, 26)
    elif lt < leave:
        k = lt - arrive
        ux = lerp(268, 282, ease(k / 0.4)); uw = lerp(26, 34, ease(k / 0.4))
        person(img, 'boy', 300, 228, 'young', 'side' if k > 0.5 else 'front', 'stand', 0,
               'surprised' if k < 1.1 else 'shy', 'down', 2, flip=True)
        person(img, 'girl', 262, 228, 'young', 'side', 'stand', 0, 'happy', 'umbrella', 2)
        umbrella(d, ux, 164, uw)
        if k > 1.3:
            f = (k - 1.3) / 1.2
            if f < 1: put(img, 'heart', 282, 150 - 14 * f, 1 if f > 0.2 else 2, alpha=1 - f * 0.6)
    else:
        k = lt - leave
        x = 262 + k * 26
        walk_pair(img, x + 34, 228, 'young', lt, 2, 6, ('happy', 'shy'))
        umbrella(d, x + 22, 164, 34)
    film(img, d, T)


s_umbrella.tr = 'white'; s_umbrella.tr_dur = 0.8


def bicycle(d, bx, gy, t, col=(110, 200, 180)):
    rot = t * 12
    for wx in (bx - 20, bx + 22):
        d.ellipse([wx - 11, gy - 21, wx + 11, gy + 1], outline=(50, 50, 60), width=2)
        for k in range(4):
            a = rot + k * math.pi / 4
            d.line([(wx - math.cos(a) * 9, gy - 10 - math.sin(a) * 9), (wx + math.cos(a) * 9, gy - 10 + math.sin(a) * 9)], fill=(170, 170, 180))
        d.point((wx, gy - 10), fill=(60, 60, 70))
    d.line([(bx - 20, gy - 10), (bx - 4, gy - 10), (bx - 8, gy - 26), (bx - 20, gy - 10)], fill=col, width=2)
    d.line([(bx - 4, gy - 10), (bx + 16, gy - 28), (bx - 8, gy - 26)], fill=col, width=2)
    d.line([(bx + 16, gy - 28), (bx + 22, gy - 10)], fill=col, width=2)
    d.line([(bx + 14, gy - 33), (bx + 17, gy - 28)], fill=(60, 60, 70), width=2)
    d.rectangle([bx + 11, gy - 35, bx + 17, gy - 34], fill=(60, 60, 70))
    d.rectangle([bx - 12, gy - 29, bx - 4, gy - 27], fill=(60, 50, 50))
    d.rectangle([bx - 30, gy - 24, bx - 12, gy - 22], fill=(96, 96, 108))
    a = t * 6
    d.line([(bx - 4, gy - 10), (bx - 4 + math.cos(a) * 5, gy - 10 + math.sin(a) * 5)], fill=(60, 60, 70), width=2)


def s_bike(img, d, lt, dur, T, A):
    off = lt * 140
    sky(img, ((0, (60, 140, 236)), (0.8, (150, 206, 250)), (1, (206, 236, 255))), 0, 126)
    glow(img, 90, 40, 60, (255, 255, 230), 0.5)
    d.ellipse([78, 28, 102, 52], fill=(255, 252, 230))
    for i, (cx, cy, s) in enumerate([(160, 30, 3), (360, 18, 2), (520, 44, 2)]):
        x = int((cx - off * 0.04) % 680 - 120)
        cloud(d, x, cy, s, (255, 255, 255), (214, 232, 250), (255, 255, 255))
    for i in range(4): bird(d, int((300 + i * 30 - lt * 20) % 520), 50 + (i % 2) * 8, T, (60, 70, 90), i)
    d.rectangle([0, 126, W, 176], fill=(46, 120, 196))
    sky(img, ((0, (70, 150, 214)), (1, (40, 110, 190))), 126, 176, 3)
    for i in range(40):
        r = rng(i)
        x = (r.uniform(0, W + 40) - off * 0.08) % (W + 40) - 20; y = r.uniform(130, 172)
        if math.sin(T * 3 + i) > 0.2: d.line([(x, y), (x + 3, y)], fill=(220, 240, 255))
    lx = (430 - off * 0.05) % 640 - 80
    d.polygon([(lx - 40, 126), (lx + 50, 126), (lx + 30, 112), (lx - 20, 108)], fill=(110, 130, 110))
    d.rectangle([lx, 82, lx + 8, 110], fill=(250, 250, 250)); d.rectangle([lx, 90, lx + 8, 94], fill=(230, 80, 80))
    d.rectangle([lx - 1, 78, lx + 9, 82], fill=(230, 80, 80))
    sx = (200 - off * 0.1) % 600 - 60
    d.polygon([(sx, 150), (sx + 14, 150), (sx + 7, 132)], fill=(255, 255, 255)); d.rectangle([sx - 2, 150, sx + 16, 153], fill=(200, 90, 70))
    d.rectangle([0, 176, W, 182], fill=(236, 220, 180))
    for i in range(W // 30 + 2):
        x = i * 30 - int(off * 0.9) % 30
        d.rectangle([x, 176, x + 3, 196], fill=(250, 250, 250))
    d.rectangle([0, 182, W, 186], fill=(250, 250, 250))
    d.rectangle([0, 196, W, 238], fill=(110, 110, 124))
    for i in range(W // 40 + 2):
        x = i * 40 - int(off) % 40
        d.rectangle([x, 216, x + 20, 217], fill=(240, 240, 230))
    bx, gy = 238, 232
    bob = int(math.sin(lt * 14) > 0.6)
    person(img, 'girl', bx - 20, gy - 6 - bob, 'young', 'side', 'sit', 0, 'happy' if 2.6 < lt < 5.0 else 'laugh',
           'up' if 2.6 < lt < 5.0 else 'hug', 2)
    bicycle(d, bx, gy - bob, T)
    person(img, 'boy', bx - 4, gy - 11 - bob, 'young', 'side', 'sit', 0, 'happy', 'reach', 2)
    for k in range(6):
        y = 150 + k * 10
        x = (k * 61 - off * 1.5) % (W + 60) - 30
        d.line([(x, y), (x + 22, y)], fill=(255, 255, 255))
    d.rectangle([0, 238, W, H], fill=(120, 170, 90))
    for i in range(40):
        x = (i * 23 - off * 1.4) % (W + 20) - 10
        flower(d, x, 262, FLOWER_COLS[i % len(FLOWER_COLS)], i % 3, (70, 140, 60), 6 + i % 5)
    film(img, d, T)


def reflect(img, y0, h, t, tint=(14, 20, 50), a=0.45, amp=2.0):
    arr = np.asarray(img).copy()
    src = arr[y0 - h:y0][::-1]
    out = np.empty_like(src)
    for i in range(h):
        out[i] = np.roll(src[i], int(round(amp * math.sin(t * 3 + i * 0.7) * (0.3 + i / h))), axis=0)
    arr[y0:y0 + h] = (out * (1 - a) + np.array(tint) * a).astype(np.uint8)
    img.paste(Image.fromarray(arr))


def s_festival(img, d, lt, dur, T, A):
    sky(img, ((0, (8, 8, 30)), (0.7, (30, 24, 70)), (1, (60, 40, 96))), 0, 146)
    stars(d, T, 140, 0.7)
    moon(d, 70, 30, 9)
    city(img, d, 146, 51, 0, (32, 26, 60), (255, 200, 120), 8, 30, 0.5, T, 8, 18)
    px = 372
    for k in range(4):
        w = 22 - k * 4; y = 146 - 12 - k * 11
        d.rectangle([px - w // 2 + 3, y, px + w // 2 - 3, y + 11], fill=(32, 26, 60))
        d.polygon([(px - w // 2 - 4, y + 2), (px + w // 2 + 4, y + 2), (px + w // 2 - 2, y - 3), (px - w // 2 + 2, y - 3)], fill=(32, 26, 60))
    for i in range(0, W, 8):
        y = 136 + 3 * math.sin(i * 0.05)
        d.point((i, y), fill=(255, 200, 120) if (i // 8) % 2 else (255, 130, 110))
    t0 = T - lt
    flash_c = None
    for j, b in enumerate(beats_in(t0 - 0.6, t0 + dur)):
        for m in range(2 if j % 2 == 0 else 1):
            r = rng(j * 3 + m + 40)
            c = r.choice([(255, 110, 140), (255, 210, 90), (120, 200, 255), (190, 140, 255), (140, 240, 160)])
            firework(img, d, T, b - 0.5 + m * 0.18, r.uniform(70, 410), r.uniform(26, 84), c, r.uniform(30, 46), 1.6, 32, j * 3 + m)
            if 0 <= T - (b + m * 0.18) < 0.3: flash_c = c
    reflect(img, 146, 64, T)
    d.polygon([(0, 210), (120, 196), (300, 200), (W, 214), (W, H), (0, H)], fill=(24, 34, 40))
    for i in range(80):
        x = (i * 37) % W; y = 214 + (i * 17) % 50
        d.line([(x, y), (x + 1, y - 3)], fill=(40, 56, 60))
    lean = ease(span(lt, 3.0, 3.6))
    person(img, 'boy', 248, 232, 'young', 'back', 'sit', 0, 'smile', 'down', 2)
    person(img, 'girl', 222 + lean * 3, 232 + lean, 'young', 'back', 'sit', 0, 'smile', 'down', 2)
    if lt > 3.8:
        f = ((lt - 3.8) * 0.5) % 1
        put(img, 'heart', 236, 166 - f * 30, 1, alpha=1 - f)
    fireflies(img, d, T, 10, (0, 196, W, 250))
    if flash_c: darken(img, 0.08, flash_c)
    film(img, d, T)


TRAIN2 = None


def s_farewell(img, d, lt, dur, T, A):
    global TRAIN2
    if TRAIN2 is None: TRAIN2 = train_img(3, (236, 120, 90))
    sky(img, ((0, (92, 72, 144)), (0.55, (240, 140, 120)), (1, (255, 210, 150))), 0, 196)
    glow(img, 330, 150, 80, (255, 200, 140), 0.5)
    d.ellipse([306, 126, 354, 174], fill=(255, 220, 160))
    city(img, d, 172, 81, 0, (120, 80, 120), None, 20, 60, blink=False)
    for i in range(6):
        x = 30 + i * 84
        d.rectangle([x - 2, 150, x + 2, 190], fill=(110, 70, 70))
        for j in range(5):
            r = rng(i * 10 + j)
            cx = x + r.uniform(-22, 22); cy = 140 + r.uniform(-14, 8)
            d.ellipse([cx - 14, cy - 10, cx + 14, cy + 10], fill=(255, 176, 200) if j % 2 else (250, 150, 180))
    d.rectangle([0, 188, W, 198], fill=(80, 70, 80))
    move = 2.2
    tx = 10 - ein(span(lt, move, move + 3.6)) * 760
    img.paste(TRAIN2, (int(tx), 106), TRAIN2)
    wx = int(tx) + 150 + 14 + 4 * 30
    if -30 < wx < W:
        d.rectangle([wx, 120, wx + 18, 146], fill=(255, 226, 190))
        hi = head_img('girl', 'young', 'smile' if lt < move + 0.6 else 'sad')
        img.paste(hi, (wx + 1, 124), hi)
        wv = int(lt * 6) % 2
        d.rectangle([wx + 14, 128 - wv * 2, wx + 16, 131 - wv * 2], fill=pix.SKIN)
    if lt > move: petals(d, T, int(20 + 30 * span(lt, move, move + 2)), speed=20, wind=-90, seed=3)
    d.rectangle([0, 198, W, H], fill=(206, 196, 186))
    d.rectangle([0, 198, W, 204], fill=(250, 210, 70))
    for y in range(214, H, 14): d.line([(0, y), (W, y)], fill=(192, 182, 172))
    if lt < move + 0.4:
        person(img, 'boy', 300, 238, 'young', 'back', 'stand', wph(lt, 6), 'smile', 'wave', 2)
    elif lt < move + 2.2:
        x = lerp(300, 170, ease(span(lt, move + 0.4, move + 2.2)))
        person(img, 'boy', x, 238, 'young', 'side', 'run', wph(lt, 12), 'sad', 'auto', 2, flip=True)
    else:
        person(img, 'boy', 170, 238, 'young', 'side', 'stand', wph(lt, 6), 'sad', 'wave' if lt < move + 3.4 else 'down', 2, flip=True)
    film(img, d, T)
    if lt > dur - 0.6: darken(img, ease((lt - dur + 0.6) / 0.6), (255, 250, 240))


# ---------------------------------------------------------------- 第 11 句：秋天的银杏街
GINKGO = [(255, 214, 70), (248, 186, 48), (255, 232, 120), (236, 166, 40)]


def ginkgo_tree(d, x, base, s=1.0, seed=0):
    d.rectangle([x - 2 * s, base - 40 * s, x + 2 * s, base], fill=(112, 80, 60))
    d.line([(x, base - 30 * s), (x + 8 * s, base - 42 * s)], fill=(112, 80, 60), width=2)
    for k, (bx, by, r) in enumerate([(0, -56, 20), (-14, -44, 14), (14, -46, 14), (-6, -70, 13), (8, -66, 12)]):
        d.ellipse([x + (bx - r) * s, base + (by - r) * s, x + (bx + r) * s, base + (by + r) * s], fill=GINKGO[k % 2])
    r = rng(seed)
    for k in range(40):
        a = r.random() * 2 * math.pi; rr = r.random() ** 0.5 * 24
        d.point((x + math.cos(a) * rr * s, base - 56 * s + math.sin(a) * rr * s * 0.9), fill=GINKGO[2 + k % 2])


def shopfront(img, d, x0, w, base, name, col, light=(255, 222, 156)):
    d.rectangle([x0, base - 96, x0 + w, base], fill=(180, 128, 100))
    for y in range(base - 92, base, 6): d.line([(x0, y), (x0 + w, y)], fill=(166, 116, 90))
    d.rectangle([x0 + 8, base - 54, x0 + w - 8, base - 6], fill=light)
    d.line([(x0 + w // 2, base - 54), (x0 + w // 2, base - 6)], fill=(150, 110, 90))
    glow(img, x0 + w / 2, base - 30, 40, light, 0.2)
    for k in range(0, w, 10):
        d.polygon([(x0 + k, base - 70), (x0 + k + 10, base - 70), (x0 + k + 10, base - 60), (x0 + k + 5, base - 57), (x0 + k, base - 60)],
                  fill=col if (k // 10) % 2 == 0 else (250, 244, 236))
    d.rectangle([x0 + 10, base - 90, x0 + w - 10, base - 76], fill=(70, 50, 44))
    text(img, name, x0 + w / 2, base - 83, (255, 240, 210), None, FONT_S, shadow=False)


def s_ginkgo(img, d, lt, dur, T, A):
    stop0, stop1 = 2.3, 4.1
    wt = lt if lt < stop0 else (stop0 if lt < stop1 else lt - (stop1 - stop0))
    off = wt * 26
    moving = not (stop0 <= lt < stop1)
    sky(img, ((0, (150, 190, 236)), (0.8, (250, 226, 196)), (1, (255, 236, 210))), 0, 120)
    for i, (cx, cy, s) in enumerate([(60, 16, 2), (300, 30, 1)]):
        cloud(d, int((cx + T * 2) % 560 - 60), cy, s, (255, 252, 248), (240, 226, 222))
    shops = [('咖啡', (200, 70, 60)), ('面包', (230, 160, 60)), ('书店', (70, 120, 170)), ('花店', (220, 110, 150))]
    for i in range(7):
        x0 = (i * 116 - off * 0.6) % 812 - 120
        shopfront(img, d, x0, 104, 198, *shops[i % 4])
    for k in range(3):     # 墙头上散步的猫
        pass
    cx_cat = (300 - off * 0.6 + lt * 8) % 812 - 120
    d.ellipse([cx_cat - 5, 98, cx_cat + 5, 104], fill=(240, 150, 70)); d.ellipse([cx_cat + 3, 94, cx_cat + 9, 100], fill=(240, 150, 70))
    d.point([(cx_cat + 4, 93), (cx_cat + 8, 93)], fill=(240, 150, 70)); d.line([(cx_cat - 5, 100), (cx_cat - 9, 94 + int(2 * math.sin(lt * 4)))], fill=(240, 150, 70))
    d.rectangle([0, 198, W, 242], fill=(216, 202, 182))
    for i in range(W // 24 + 2):
        x = i * 24 - int(off) % 24
        d.line([(x, 198), (x - 6, 242)], fill=(200, 186, 166))
    r = rng(5)
    for i in range(140):
        x = (r.uniform(0, 900) - off) % 900 - 40; y = r.uniform(200, 240)
        d.point((x, y), fill=GINKGO[i % 4])
        if i % 3 == 0: d.point((x + 1, y), fill=GINKGO[(i + 1) % 4])
    cart = 360 - off
    if -60 < cart < W + 60:     # 烤红薯摊
        d.rectangle([cart - 22, 206, cart + 22, 214], fill=(150, 90, 60))
        d.ellipse([cart - 14, 182, cart + 14, 210], fill=(90, 90, 100)); d.rectangle([cart - 4, 170, cart + 4, 184], fill=(70, 70, 80))
        for wx in (cart - 16, cart + 16): d.ellipse([wx - 5, 210, wx + 5, 220], fill=(60, 50, 50))
        steam(img, d, cart, 168, T, 3, 30, (255, 250, 246), 0.5, 5)
        d.rectangle([cart - 30, 160, cart - 28, 210], fill=(110, 80, 60)); d.rectangle([cart - 40, 156, cart - 18, 160], fill=(200, 70, 60))
        person(img, 'boy', cart + 30, 230, 'adult', 'front', 'stand', 0, 'happy', 'down', 2, tint=(150, 124, 120))
    for i in range(4):
        ginkgo_tree(d, (i * 160 + 80 - off) % 640 - 80, 202, 1.5, i)
    walk_pair(img, 236, 232, 'old', lt, 2, 5, ('happy', 'happy'), moving)
    if lt > stop0 + 0.9:
        d.ellipse([238, 208, 245, 213], fill=(170, 90, 60)); d.ellipse([239, 208, 244, 211], fill=(250, 170, 80))
        steam(img, d, 241, 206, T, 2, 12, (255, 255, 255), 0.4, 3)
        if lt < stop1: put(img, 'heart', 236, 160 - (lt - stop0) * 6, 1)
    d.rectangle([0, 242, W, H], fill=(120, 116, 124))
    petals(d, T, 60, GINKGO, speed=22, wind=24, seed=2)


s_ginkgo.tr = 'flash'; s_ginkgo.tr_dur = 0.5


# ---------------------------------------------------------------- 第 12 句：在家翻相册
def living_room(img, d, T):
    sky(img, ((0, (126, 92, 82)), (1, (92, 64, 62))), 0, 212)
    for y in range(8, 212, 16):
        for x in range(8 + (y // 16) % 2 * 8, W, 16): d.point((x, y), fill=(136, 102, 92))
    d.rectangle([36, 36, 146, 136], fill=(96, 66, 56))
    d.rectangle([42, 42, 140, 130], fill=(30, 36, 84))
    stars(d, T, 0, 0)
    for x, y, p, k in pix.STARS[:24]:
        if math.sin(T * 2 + p) > 0: d.point((42 + x % 98, 42 + y % 60), fill=(230, 230, 255))
    moon(d, 116, 64, 9)
    city(img, d, 130, 91, 0, (50, 50, 96), (255, 220, 140), 10, 40, 0.4, T, 6, 12)
    d.rectangle([90, 42, 92, 130], fill=(96, 66, 56)); d.rectangle([42, 84, 140, 86], fill=(96, 66, 56))
    for x0 in (28, 138):
        d.rectangle([x0, 30, x0 + 14, 146], fill=(186, 70, 70))
        for y in range(32, 146, 6): d.line([(x0 + 4, y), (x0 + 4, y + 3)], fill=(160, 56, 60))
    d.rectangle([24, 26, 156, 30], fill=(120, 84, 60))
    for i, (fx, fy, c) in enumerate([(206, 52, (255, 200, 200)), (238, 46, (200, 220, 255)), (270, 56, (255, 236, 180))]):
        d.rectangle([fx - 12, fy - 10, fx + 12, fy + 10], fill=(150, 110, 80)); d.rectangle([fx - 10, fy - 8, fx + 10, fy + 8], fill=c)
        put(img, 'heart', fx, fy, 1) if i == 1 else None
    d.rectangle([370, 52, 452, 212], fill=(120, 84, 60))
    for k, y in enumerate((60, 96, 132, 168)):
        d.rectangle([374, y + 32, 448, y + 34], fill=(96, 64, 46))
        rr = rng(k + 20); x = 376
        while x < 444:
            bw = rr.randint(3, 6); bh = rr.randint(20, 30)
            d.rectangle([x, y + 32 - bh, x + bw - 1, y + 31], fill=rr.choice([(200, 90, 90), (90, 150, 200), (230, 190, 90), (110, 170, 110), (190, 130, 200)]))
            x += bw
    lx = 330
    d.rectangle([lx - 1, 90, lx + 1, 212], fill=(80, 64, 60)); d.rectangle([lx - 8, 210, lx + 8, 212], fill=(80, 64, 60))
    d.polygon([(lx - 14, 92), (lx + 14, 92), (lx + 9, 74), (lx - 9, 74)], fill=(250, 220, 160))
    glow(img, lx, 92, 70, (255, 214, 150), 0.35)
    d.rectangle([0, 212, W, H], fill=(140, 96, 70))
    for y in range(218, H, 9): d.line([(0, y), (W, y)], fill=(124, 84, 62))
    d.ellipse([140, 230, 340, 268], fill=(186, 90, 80)); d.ellipse([156, 236, 324, 262], fill=(206, 120, 96))


def sofa_front(d, x0, x1, top, seat, col=(120, 150, 120), shade=(96, 124, 98)):
    d.rounded_rectangle([x0, top, x1, seat + 4], radius=8, fill=col)
    d.rectangle([x0 + 10, seat - 4, x1 - 10, seat + 6], fill=shade)
    d.rounded_rectangle([x0 - 10, seat - 14, x0 + 12, seat + 22], radius=6, fill=col)
    d.rounded_rectangle([x1 - 12, seat - 14, x1 + 10, seat + 22], radius=6, fill=col)
    d.rectangle([x0 + 8, seat + 6, x1 - 8, seat + 22], fill=col)
    d.rectangle([x0 - 6, seat + 22, x0 - 2, seat + 28], fill=(80, 60, 50)); d.rectangle([x1 + 2, seat + 22, x1 + 6, seat + 28], fill=(80, 60, 50))


def page_img(kind, t, w=176, h=180):
    im = Image.new('RGB', (w, h)); d = ImageDraw.Draw(im); d.fontmode = '1'
    im.paste(pix.vgrad(w, h, ((0, (252, 244, 226)), (1, (240, 228, 204))), 3))
    if kind in ('stubborn', 'anxious'):
        ph = sepia((mem_stubborn if kind == 'stubborn' else mem_anxious)(t)(124, 86))
    else:
        ph = snap_photo({'umbrella': 104.6, 'bike': 109.4}[kind], 124, 86)
    x0, y0 = (w - 124) // 2, 22
    d.rectangle([x0 - 5, y0 - 5, x0 + 128, y0 + 98], fill=(255, 255, 252)); d.rectangle([x0 - 5, y0 + 99, x0 + 128, y0 + 100], fill=(210, 200, 186))
    im.paste(ph, (x0, y0))
    for cx, cy, dx, dy in ((x0 - 5, y0 - 5, 1, 1), (x0 + 128, y0 - 5, -1, 1), (x0 - 5, y0 + 98, 1, -1), (x0 + 128, y0 + 98, -1, -1)):
        d.polygon([(cx, cy), (cx + 8 * dx, cy), (cx, cy + 8 * dy)], fill=(70, 50, 44))
    for k in range(3):
        y = 132 + k * 10
        d.line([(30, y), (30 + 30 + (k * 37) % 80, y)], fill=(150, 130, 120))
    put(im, 'heart', w - 26, 146, 2) if kind in ('stubborn', 'umbrella') else put(im, 'star', w - 28, 148, 2)
    return im


@lru_cache(None)
def snap_photo(T0, w, h):
    """全片 T0 秒处画面的缩略图，当照片用"""
    if SNAP is None: return Image.new('RGB', (w, h), (200, 190, 170))
    im = SNAP(T0)
    return im.crop((0, 14, W, H - 14)).resize((w, h), Image.BOX)


def hand(d, x, y, sleeve, point=False, flip=False):
    s = -1 if flip else 1
    d.rectangle([x - 8, y, x + 8, y + 40], fill=sleeve)
    d.ellipse([x - 7, y - 10, x + 7, y + 4], fill=pix.SKIN)
    if point: d.rectangle([x - 1, y - 20, x + 2, y - 8], fill=pix.SKIN); d.point((x, y - 20), fill=pix.SKIN_S)
    d.line([(x - 7, y - 3), (x - 7, y + 2)], fill=pix.SKIN_S)


def s_album(img, d, lt, dur, T, A):
    wide = 2.4
    if lt < wide:
        living_room(img, d, T)
        sofa_front(d, 150, 330, 150, 196)
        person(img, 'girl', 222, 214, 'old', 'front', 'sit', 0, 'laugh' if int(lt * 3) % 2 else 'happy', 'lap', 2)
        person(img, 'boy', 258, 214, 'old', 'front', 'sit', 0, 'happy', 'lap', 2)
        d.polygon([(206, 200), (240, 196), (274, 200), (274, 208), (240, 205), (206, 208)], fill=(250, 240, 220))
        d.line([(240, 196), (240, 205)], fill=(200, 180, 160))
        d.rectangle([206, 207, 274, 209], fill=(170, 80, 70))
        cx, cy = 92, 248
        b = int(math.sin(T * 2) > 0)
        d.ellipse([cx - 12, cy - 6 - b, cx + 12, cy + 4], fill=(240, 160, 80)); d.ellipse([cx + 6, cy - 9, cx + 15, cy - 1], fill=(240, 160, 80))
        d.point([(cx + 8, cy - 10), (cx + 13, cy - 10)], fill=(240, 160, 80)); d.line([(cx + 9, cy - 5), (cx + 10, cy - 5)], fill=(90, 50, 40))
        d.arc([cx - 18, cy - 8, cx + 2, cy + 6], 90, 200, fill=(240, 160, 80), width=2)
        for i, x in enumerate((356, 372)):
            d.rectangle([x - 4, 190, x + 4, 200], fill=(250, 250, 246)); steam(img, d, x, 188, T + i, 2, 14)
        d.rectangle([346, 200, 384, 204], fill=(120, 84, 60)); d.rectangle([350, 204, 354, 222], fill=(120, 84, 60)); d.rectangle([376, 204, 380, 222], fill=(120, 84, 60))
        vig(img, 0.4, (40, 20, 20))
        return
    k = lt - wide
    d.rectangle([0, 0, W, H], fill=(96, 62, 50))
    for y in range(0, H, 10): d.line([(0, y), (W, y + 4)], fill=(88, 56, 46))
    glow(img, 240, 120, 260, (255, 210, 150), 0.25)
    flip0, flip1 = 2.8, 3.6
    f = span(k, flip0, flip1)
    P1L, P1R = page_img('stubborn', T), page_img('anxious', T)
    P2L, P2R = page_img('umbrella', T), page_img('bike', T)
    pw, ph_ = P1L.width, P1L.height
    lx, rx, ty = 240 - pw, 240, 40
    d.rectangle([lx - 8, ty - 6, rx + pw + 8, ty + ph_ + 8], fill=(150, 60, 56))
    for k2 in range(3):
        d.line([(lx - 4 + k2, ty + ph_ + 2 + k2), (rx + pw + 4 - k2, ty + ph_ + 2 + k2)], fill=(230, 220, 200))
    img.paste(P1L if f < 1 else P2L, (lx, ty))
    img.paste(P2R if f > 0 else P1R, (rx, ty))
    if 0 < f < 1:
        c = math.cos(math.pi * f)
        w = max(1, int(abs(c) * pw))
        pg = (P1R if c > 0 else P2L).resize((w, ph_), Image.NEAREST)
        x = rx if c > 0 else rx - w
        img.paste(pg, (x, ty - int(10 * math.sin(math.pi * f))))
        tfill(img, 'rectangle', [x, ty, x + w, ty + ph_], (60, 40, 30), 0.25 * (1 - abs(c)))
    tfill(img, 'rectangle', [236, ty, 244, ty + ph_], (90, 60, 40), 0.4)
    if k < 1.3:
        hand(d, 150 + int(4 * math.sin(k * 6)), 160 + int(20 * (1 - eout(k / 0.4))), (246, 216, 132), True)
    elif k < flip0 - 0.2:
        hand(d, 330 + int(4 * math.sin(k * 6)), 160 + int(20 * (1 - eout((k - 1.3) / 0.4))), (106, 130, 176), True)
    elif k < flip1 + 0.3:
        hx = lerp(420, 200, ease(span(k, flip0, flip1)))
        hand(d, hx, 150, (106, 130, 176))
    else:
        put(img, 'heart', 240, 30 - ((k - flip1) * 10) % 20, 1)
    vig(img, 0.45, (40, 20, 16))


# ---------------------------------------------------------------- 第 13 句：夜里的花园，萤火虫聚成一颗心
def s_fireflies(img, d, lt, dur, T, A):
    garden(img, d, 0, T, GARDEN_DAY, arch_x=240, sun=None)
    grade(img, 0.5, (0.3, 0.34, 0.66), (2, 4, 18))
    lean = min(1, lt / 0.4) * 2
    glow(img, 240, 200, 50, (255, 200, 140), 0.3)
    person(img, 'boy', 254 - lean, 228, 'old', 'side', 'stand', 0, 'closed', 'hug', 2, flip=True, shade=(0.62, 0.6, 0.78))
    person(img, 'girl', 226 + lean, 228, 'old', 'side', 'stand', 0, 'closed', 'hug', 2, shade=(0.66, 0.62, 0.74))
    stars(d, T, 104, 0.9)
    glow(img, 84, 40, 40, (220, 230, 255), 0.3)
    moon(d, 84, 40, 13, (240, 240, 220))
    for i, x in enumerate((36, 136, 344, 444)):
        d.rectangle([x, 196, x + 1, 232], fill=(40, 40, 60))
        d.rectangle([x - 3, 188, x + 4, 196], fill=(255, 200, 120))
        glow(img, x, 192, 30, (255, 190, 110), 0.45 + 0.1 * math.sin(T * 3 + i))
    r = rng(4)
    for i in range(36):
        x = r.uniform(0, W); y = r.uniform(158, 198)
        tw = 0.5 + 0.5 * math.sin(T * 2 + i)
        d.point((x, y), fill=lerpc((120, 130, 170), (250, 250, 255), tw))
    glow(img, 240, 196, 60, (255, 200, 140), 0.25)
    n = 48
    g_in = 1.2; g_full = 3.0; g_out = 5.2
    for i in range(n):
        rr = rng(i * 17)
        wx = rr.uniform(0, W) + 14 * math.sin(T * 0.5 + i); wy = rr.uniform(60, 230) + 8 * math.sin(T * 0.7 + i * 1.3)
        hx, hy = pix.HEART_PTS[(i * 64) // n]
        hx = 240 + hx * 3.2; hy = 104 + hy * 3.0
        g = ease(span(lt, g_in + (i % 10) * 0.05, g_full + (i % 10) * 0.05))
        up = ease(span(lt, g_out, dur))
        x = lerp(wx, hx, g); y = lerp(wy, hy, g) - up * (60 + (i % 7) * 10)
        if up > 0: x += math.sin(i) * 40 * up
        b = 0.6 + 0.4 * math.sin(T * 3 + i)
        glow(img, x, y, 7, (255, 236, 130), 0.55 * b)
        d.rectangle([int(x), int(y), int(x) + 1, int(y) + 1], fill=lerpc((200, 190, 90), (255, 252, 210), b))
    if g_full + 0.5 < lt < g_out:
        glow(img, 240, 112, 60, (255, 230, 150), 0.18 + 0.08 * pulse(T, 0.4))


# ---------------------------------------------------------------- 第 14 句：水里的倒影变回了当年的少年和女孩
def koi(d, x, y, a, col):
    dx, dy = math.cos(a), math.sin(a)
    for k in range(5):
        d.ellipse([x - dx * k * 2 - 2, y - dy * k * 2 - 1, x - dx * k * 2 + 2, y - dy * k * 2 + 1], fill=col if k % 2 == 0 else (250, 250, 250))
    tx, ty = x - dx * 11, y - dy * 11
    d.polygon([(tx, ty), (tx - dx * 4 - dy * 3, ty - dy * 4 + dx * 3), (tx - dx * 4 + dy * 3, ty - dy * 4 - dx * 3)], fill=col)


def s_pond(img, d, lt, dur, T, A):
    sky(img, ((0, (86, 78, 150)), (0.6, (236, 150, 162)), (1, (255, 204, 164))), 0, 150)
    glow(img, 392, 134, 60, (255, 200, 160), 0.5)
    d.pieslice([370, 112, 414, 156], 180, 360, fill=(255, 226, 180))
    hills(d, 138, 5, 0.02, 1, (130, 100, 150))
    for i in range(5):
        x = 40 + i * 100
        d.ellipse([x - 20, 104, x + 20, 146], fill=(96, 80, 130)); d.ellipse([x - 12, 96, x + 16, 130], fill=(110, 92, 144))
    d.rectangle([0, 140, W, 152], fill=(96, 140, 96))
    for i in range(24):
        x = (i * 23) % W
        if 150 < x < 330: continue
        d.line([(x, 150), (x + 1, 136 + (i * 7) % 8)], fill=(80, 120, 80)); d.rectangle([x, 134 + (i * 7) % 8, x + 1, 138 + (i * 7) % 8], fill=(150, 110, 80))
    young_k = span(lt, 2.6, 3.6)
    old_expr = 'down' if lt < 5.4 else 'happy'
    person(img, 'girl', 226, 152, 'old', 'front', 'stand', 0, old_expr, 'hold_r', 2)
    person(img, 'boy', 262, 152, 'old', 'front', 'stand', 0, old_expr, 'hold_l', 2)
    reflect(img, 152, 118, T, (40, 30, 90), 0.4, 1.5)
    if young_k > 0:
        lay = Image.new('RGBA', (W, 60))
        wv = 'wave' if lt > 4.2 else 'down'
        person(lay, 'girl', 226, 58, 'young', 'front', 'stand', wph(lt, 5), 'happy', wv if wv == 'down' else 'wave', 2)
        person(lay, 'boy', 262, 58, 'young', 'front', 'stand', wph(lt + 0.5, 5), 'happy', 'down', 2)
        a = np.array(lay.transpose(Image.FLIP_TOP_BOTTOM))
        for i in range(a.shape[0]):
            a[i] = np.roll(a[i], int(round(1.5 * math.sin(T * 3 + i * 0.7) * (0.3 + i / 118))), axis=0)
        rgb = a[..., :3].astype(float) * 0.62 + np.array((40, 30, 90)) * 0.38
        a[..., :3] = rgb.astype(np.uint8)
        m = (a[..., 3] > 0) & (pix.bayer(60, W) < young_k)
        a[..., 3] = m * 255
        lay = Image.fromarray(a)
        img.paste(lay, (0, 154), lay)
    if 2.4 < lt < 4.0:
        rr = (lt - 2.4) * 120
        d.ellipse([244 - rr, 178 - rr * 0.25, 244 + rr, 178 + rr * 0.25], outline=(255, 250, 230))
        for i in range(8): twinkle(d, 200 + i * 12, 170 + (i % 3) * 10, ((lt - 2.4) * 1.5 + i * 0.1) % 1, (255, 255, 240), 3)
    for i, (px, py, r) in enumerate([(60, 200, 12), (110, 236, 9), (400, 212, 13), (346, 250, 8), (450, 246, 10)]):
        d.ellipse([px - r, py - r * 0.4, px + r, py + r * 0.4], fill=(70, 130, 80)); d.pieslice([px - r, py - r * 0.4, px + r, py + r * 0.4], 300, 330, fill=(50, 100, 70))
        if i in (0, 2):
            d.polygon([(px - 3, py - 1), (px, py - 6), (px + 3, py - 1)], fill=(255, 170, 200)); d.point((px, py - 3), fill=(255, 230, 240))
    for i in range(3):
        a_ = T * 0.5 + i * 2.1
        koi(d, 240 + math.cos(a_) * (140 - i * 30), 220 + math.sin(a_) * 22, a_ + math.pi / 2, [(250, 120, 50), (240, 240, 240), (230, 70, 60)][i])
    for i in range(3):
        f = (lt * 0.4 + i / 3) % 1
        x, y = [(140, 200), (330, 230), (200, 254)][i]; r = 2 + f * 16
        d.ellipse([x - r, y - r * 0.3, x + r, y + r * 0.3], outline=lerpc((200, 180, 230), (90, 70, 130), f))
    if lt > 5.4:
        put(img, 'heart', 244, 96 - ((lt - 5.4) * 12) % 24, 1, alpha=1 - ((lt - 5.4) * 12 % 24) / 24)


# ---------------------------------------------------------------- 第 15–16 句：她一个人走过花园，长椅上的画面慢慢褪色
GARDEN_DIM = ((0, (160, 186, 222)), (0.75, (226, 228, 236)), (1, (240, 238, 232)))


def s_alone(img, d, lt, dur, T, A):
    off = 300 + lt * 26
    garden(img, d, off, T, GARDEN_DIM, fence=True, sun=None, bench_x=760)
    cx = W + 40 - lt * 64
    person(img, 'boy', cx + 16, 230, 'young', 'side', 'walk', wph(lt, 6), 'happy', 'hold_f', 2, flip=True, tint=(214, 210, 226), alpha=0.8)
    person(img, 'girl', cx, 230, 'young', 'side', 'walk', wph(lt + 0.3, 6), 'happy', 'hold', 2, flip=True, tint=(214, 210, 226), alpha=0.8)
    grade(img, 0.55, (0.98, 0.98, 1.02))
    person(img, 'girl', 220, 230, 'adult', 'side', 'walk', wph(lt, 5), 'down', 'auto', 2)
    petals(d, T, 14, speed=12, wind=8)


def s_emptybench(img, d, lt, dur, T, A):
    garden(img, d, 420, T, GARDEN_DIM, sun=None)
    bench_front(d, 160, 320, 198, (250, 250, 246), (220, 220, 214), (90, 90, 100))
    sat = 1 - 0.88 * ease(span(lt, 0.2, 2.4))
    ga = span(lt, 0.9, 1.6) * (1 - span(lt, 2.6, 3.6))
    if ga > 0:
        ghost = char_img('boy', 'adult', 'front', 'sit', 0, 'smile', 'lap', None, (250, 250, 255))
        g = ghost.resize((CW * 2, CH * 2), Image.NEAREST)
        a = np.array(g); m = (a[..., 3] > 0) & (pix.bayer(a.shape[0], a.shape[1]) < ga * 0.7)
        a[..., 3] = m * 255
        g = Image.fromarray(a)
        img.paste(g, (int(270 - CX * 2), int(216 - FY * 2)), g)
    if lt > 2.6:
        for i in range(30):
            rr = rng(i)
            f = (lt - 2.6) / 1.4
            x = 262 + rr.uniform(-14, 14) + math.sin(i + lt * 2) * 4; y = 196 - rr.uniform(0, 50) - f * 40 * (0.5 + rr.random())
            if f < 1 and rr.random() > f: d.point((x, y), fill=(255, 255, 255))
    grade(img, sat)
    person(img, 'girl', 196, 216, 'adult', 'front' if lt < 2.4 else 'side', 'sit', 0, 'sad' if lt < 2.4 else 'down', 'lap', 2)
    py = lerp(-6, 196, ease(span(lt, 0.0, dur)))
    px = 250 + 18 * math.sin(lt * 1.6)
    d.rectangle([px, py, px + 1, py + 1], fill=(255, 180, 200)); d.point((px + 2, py), fill=(255, 210, 220))
    vig(img, 0.4, (30, 30, 40))


# ---------------------------------------------------------------- 第 17–18 句：一个人在家看电视里的爱情片，沙发另一半空着
def tv_movie(t, w, h):
    im = Image.new('RGB', (w, h)); d = ImageDraw.Draw(im)
    im.paste(pix.vgrad(w, h, ((0, (30, 20, 76)), (0.7, (150, 80, 140)), (1, (240, 140, 150))), 4))
    for i in range(20): d.point(((i * 37) % w, (i * 23) % (h // 2)), fill=(240, 240, 255))
    mx, my, mr = w // 2, h // 2 - 4, h // 3
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(255, 240, 210))
    d.rectangle([0, h - 14, w, h], fill=(30, 20, 40))
    d.arc([10, h - 30, w - 10, h + 10], 180, 360, fill=(30, 20, 40), width=3)
    f = clamp(t / 1.8)
    sil = (34, 20, 44)
    person(im, 'girl', lerp(10, mx - 7, eout(f)), h - 14, 'young', 'side', 'walk' if f < 1 else 'stand', wph(t, 8), 'smile', 'auto' if f < 1 else 'hug', 1, tint=sil)
    person(im, 'boy', lerp(w - 10, mx + 7, eout(f)), h - 14, 'young', 'side', 'walk' if f < 1 else 'stand', wph(t, 8), 'smile', 'auto' if f < 1 else 'hug', 1, flip=True, tint=sil)
    if t > 2.0:
        k = t - 2.0
        put(im, 'heart', mx, h - 46 - k * 6, 1, alpha=clamp(1 - k / 2))
        for i in range(5): twinkle(d, 10 + i * (w - 20) // 4, 10 + (i % 2) * 8, (k + i * 0.2) % 1, (255, 255, 240), 2)
    return im


def s_movie(img, d, lt, dur, T, A):
    sky(img, ((0, (18, 20, 48)), (1, (30, 30, 66))), 0, 200)
    d.rectangle([26, 40, 120, 150], fill=(40, 40, 70)); d.rectangle([30, 44, 116, 146], fill=(14, 18, 44))
    for i in range(8):
        r = rng(i)
        glow(img, 30 + r.uniform(0, 86), 60 + r.uniform(0, 80), 8, r.choice([(255, 200, 120), (255, 120, 120), (150, 200, 255)]), 0.4)
    rain(d, T, 30, 116, 44, 146, 30, (110, 130, 180), 160, -2, 4)
    d.rectangle([72, 44, 74, 146], fill=(40, 40, 70))
    d.rectangle([0, 200, W, H], fill=(40, 34, 56))
    d.rectangle([236, 196, 420, 226], fill=(80, 58, 50)); d.rectangle([236, 196, 420, 199], fill=(100, 74, 62))
    d.rectangle([250, 104, 406, 194], fill=(20, 20, 26))
    mv = tv_movie(lt, 146, 80)
    img.paste(mv, (255, 109))
    bright = np.asarray(mv).mean() / 255
    glow(img, 328, 150, 200, (170, 190, 255), 0.18 + 0.25 * bright, 140)
    d.rectangle([316, 194, 340, 198], fill=(20, 20, 26))
    person(img, 'girl', 150, 246, 'adult', 'back', 'sit', 0, 'smile', 'down', 3, shade=(0.7, 0.74, 1.0))
    glow(img, 150, 190, 40, (150, 170, 255), 0.2)
    d.rounded_rectangle([50, 210, 300, 270], radius=10, fill=(70, 66, 110))
    d.rounded_rectangle([36, 196, 64, 270], radius=8, fill=(80, 76, 120)); d.rounded_rectangle([286, 196, 314, 270], radius=8, fill=(80, 76, 120))
    d.line([(176, 214), (176, 270)], fill=(60, 56, 96))
    for k in range(5):
        d.rectangle([62 + k * 4, 196, 65 + k * 4, 214], fill=(230, 60, 60) if k % 2 else (250, 246, 240))
    for k in range(6): d.ellipse([60 + k * 4, 190 - (k % 2) * 3, 66 + k * 4, 196 - (k % 2) * 3], fill=(255, 240, 200))
    tfill(img, 'rectangle', [0, 0, W, H], (120, 140, 220), 0.06 + 0.06 * math.sin(lt * 9) ** 2)
    vig(img, 0.5, (6, 6, 20))


def s_emptyseat(img, d, lt, dur, T, A):
    cam = ease(span(lt, 0.4, 3.0)) * 170
    def X(x): return x - cam
    sky(img, ((0, (22, 24, 54)), (1, (34, 34, 70))), 0, 214)
    d.rectangle([X(250), 30, X(420), 130], fill=(44, 44, 76)); d.rectangle([X(254), 34, X(416), 126], fill=(12, 16, 40))
    for i in range(10):
        r = rng(i + 50)
        glow(img, X(256 + r.uniform(0, 156)), 50 + r.uniform(0, 70), 9, r.choice([(255, 200, 120), (255, 120, 120), (150, 200, 255)]), 0.35)
    rain(d, T, int(X(254)), int(X(416)), 34, 126, 40, (110, 130, 180), 160, -2, 4)
    d.rectangle([X(334), 34, X(336), 126], fill=(44, 44, 76))
    d.rectangle([X(560), 54, X(600), 84], fill=(120, 90, 70)); d.rectangle([X(563), 57, X(597), 81], fill=(255, 210, 200))
    heart_at(img, X(580), 69, 7)
    d.rectangle([0, 214, W, H], fill=(44, 38, 60))
    sofa_front(d, X(60), X(460), 150, 202, (90, 96, 150), (74, 80, 130))
    person(img, 'girl', X(124), 220, 'adult', 'front', 'sit', 0, 'sad' if lt < 3.2 else 'down', 'flowers', 2)
    d.rounded_rectangle([X(112), 186, X(136), 206], radius=4, fill=(240, 150, 170))
    d.rounded_rectangle([X(330), 170, X(360), 200], radius=5, fill=(120, 170, 230))
    d.rectangle([X(500), 180, X(560), 184], fill=(110, 80, 60)); d.rectangle([X(526), 184, X(534), 226], fill=(110, 80, 60))
    for i, x in enumerate((X(512), X(540))):
        d.rectangle([x - 5, 168, x + 5, 180], fill=(250, 250, 246) if i == 0 else (170, 200, 240))
        d.rectangle([x + 5, 171, x + 7, 176], fill=(250, 250, 246) if i == 0 else (170, 200, 240))
    d.rectangle([X(484), 140, X(510), 168], fill=(140, 100, 70)); d.rectangle([X(487), 143, X(507), 165], fill=(255, 230, 180))
    hi = head_img('boy', 'young', 'smile'); img.paste(hi, (int(X(489)), 145), hi)
    flick = 0.5 + 0.5 * math.sin(lt * 7) * math.sin(lt * 3.1)
    tfill(img, 'rectangle', [0, 0, W, H], (140, 170, 255), 0.07 + 0.06 * flick)
    if lt > 3.2:
        f = (lt - 3.2) / 1.2
        if f < 1: d.point((X(128) + 3, 182 + f * 8), fill=(180, 220, 255))
    vig(img, 0.5, (6, 6, 20))


# ---------------------------------------------------------------- 第 19 句：画面按节拍一格分成两格、四格、十六格
BUSY_KINDS = ['type', 'phone', 'run', 'papers', 'clock', 'noodle', 'sleep', 'crowd']


def busy_panel(w, h, kind, who, t):
    im = Image.new('RGB', (w, h)); d = ImageDraw.Draw(im); d.fontmode = '1'
    warm = who == 'girl'
    base = (250, 206, 120) if warm else (140, 176, 236)
    im.paste(pix.vgrad(w, h, ((0, lerpc(base, (255, 255, 255), 0.35)), (1, base)), 3))
    s = max(1, min(3, h // 46))
    gy = h - max(3, h // 9)
    d.rectangle([0, gy, w, h], fill=lerpc(base, (0, 0, 0), 0.3))
    cx = w // 2
    if kind in ('type', 'noodle', 'sleep'):
        person(im, who, cx - 6 * s, gy, 'adult', 'side', 'sit', int(t * 14) % 2, 'closed' if kind == 'sleep' else 'worried',
               'type' if kind != 'sleep' else 'lap', s)
        d.rectangle([cx - 2 * s, gy - 12 * s, cx + 22 * s, gy - 10 * s], fill=(140, 100, 70))
        d.rectangle([cx + 8 * s, gy - 26 * s, cx + 20 * s, gy - 14 * s], fill=(50, 50, 66))
        d.rectangle([cx + 9 * s, gy - 25 * s, cx + 19 * s, gy - 15 * s], fill=(255, 120, 120) if int(t * 4) % 2 else (200, 230, 255))
        if kind == 'noodle':
            d.rectangle([cx + 1 * s, gy - 16 * s, cx + 5 * s, gy - 12 * s], fill=(250, 250, 240)); steam(im, d, cx + 3 * s, gy - 17 * s, t, 2, 8 * s)
        if kind == 'sleep':
            for k in range(3):
                f = (t * 0.8 + k / 3) % 1
                text(im, 'z', cx - 2 * s + f * 10 * s, gy - 30 * s - f * 12 * s, (255, 255, 255), (40, 40, 90), FONT_S, 1 - f)
    elif kind == 'phone':
        x = cx + int(math.sin(t * 5) * 10 * s)
        person(im, who, x, gy, 'adult', 'side', 'walk', wph(t, 10), 'surprised', 'phone', s, flip=math.cos(t * 5) < 0)
        text(im, '!!', x + 12 * s, gy - 34 * s, (255, 80, 80), OUT, FONT_S)
    elif kind == 'run':
        person(im, who, cx, gy, 'adult', 'side', 'run', wph(t, 14), 'worried', 'auto', s)
        for k in range(4):
            y = gy - (6 + k * 6) * s
            x = (cx - 20 * s - (t * 200 + k * 30) % (30 * s))
            d.line([(x, y), (x + 10 * s, y)], fill=(255, 255, 255))
    elif kind == 'papers':
        person(im, who, cx, gy, 'adult', 'front', 'stand', 0, 'surprised', 'up', s)
        for k in range(8):
            a = t * 3 + k * 0.8
            px = cx + math.cos(a) * 18 * s; py = gy - 20 * s + math.sin(a * 1.3) * 12 * s
            d.rectangle([px, py, px + 4 * s, py + 3 * s], fill=(255, 255, 250), outline=(180, 180, 190))
    elif kind == 'clock':
        clock_face(d, cx + 10 * s, gy - 22 * s, 12 * s, t * 30, 1)
        person(im, who, cx - 16 * s, gy, 'adult', 'front', 'stand', 0, 'surprised', 'cover', s)
    elif kind == 'crowd':
        for k in range(6):
            person(im, 'boy' if k % 2 else 'girl', cx - 24 * s + k * 10 * s, gy, 'adult', 'front', 'stand', 0, 'neutral', 'phone', s, tint=lerpc(base, (40, 40, 60), 0.6))
        person(im, who, cx + int(math.sin(t * 9)), gy, 'adult', 'front', 'stand', 0, 'worried', 'phone', s)
    return im


def s_grid(img, d, lt, dur, T, A):
    levels = [(0.0, 1, 1), (0.95, 2, 1), (1.92, 2, 2), (2.88, 4, 2), (3.3, 4, 4)]
    lv = max(i for i, (t0, _, _) in enumerate(levels) if lt >= t0)
    t0, cols, rows = levels[lv]
    pw, ph_ = W // cols, H // rows
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            kind = BUSY_KINDS[(i * 3 + lv * 5) % len(BUSY_KINDS)]
            who = 'girl' if (r + c) % 2 == 0 else 'boy'
            pnl = busy_panel(pw - 2, ph_ - 2, kind, who, T + i * 0.37)
            img.paste(pnl, (c * pw + 1, r * ph_ + 1))
    for c in range(1, cols): d.rectangle([c * pw - 1, 0, c * pw, H], fill=(30, 20, 40))
    for r in range(1, rows): d.rectangle([0, r * ph_ - 1, W, r * ph_], fill=(30, 20, 40))
    k = lt - t0
    if k < 0.12: darken(img, 0.6 * (1 - k / 0.12), (255, 255, 255))
    if k < 0.2:
        a = np.asarray(img).copy()
        for y in range(0, H, 6):
            a[y:y + 6] = np.roll(a[y:y + 6], int(8 * math.sin(y * 13 + lt * 50) * (1 - k / 0.2)), axis=1)
        img.paste(Image.fromarray(a))
    if lv >= 3: darken(img, 0.12 * (int(lt * 8) % 2), (255, 40, 60))


s_grid.tr = 'cut'


# ---------------------------------------------------------------- 第 20 句：整座城市停住了，像素聚成一个问号
@lru_cache(None)
def glyph_pts(ch, scale):
    im = pix.text_img(ch, (255, 255, 255), None, None, False)
    a = np.array(im)[..., 3] > 0
    ys, xs = np.nonzero(a)
    pts = []
    for x, y in zip(xs, ys):
        for dy in range(scale):
            for dx in range(scale):
                if (dx + dy) % 2 == 0: pts.append((x * scale + dx - im.width * scale / 2, y * scale + dy - im.height * scale / 2))
    return pts


def s_freeze(img, d, lt, dur, T, A):
    sky(img, ((0, (150, 170, 200)), (1, (210, 214, 224))), 0, 160)
    city(img, d, 160, 101, 0, (120, 126, 146), (200, 210, 230), 40, 110, 0.3, 0, blink=False)
    d.rectangle([370, 40, 410, 160], fill=(140, 130, 140)); d.polygon([(366, 40), (414, 40), (390, 18)], fill=(120, 110, 120))
    clock_face(d, 390, 64, 13, 3.3, 1)
    d.rectangle([0, 160, W, H], fill=(110, 110, 120))
    for i in range(10): d.rectangle([60 + i * 38, 196, 84 + i * 38, 232], fill=(230, 230, 230))
    r = rng(8)
    for k in range(16):
        x = r.uniform(10, W - 10); y = r.choice((178, 186, 240, 252, 262))
        if abs(x - 240) < 30 and y > 220: continue
        person(img, r.choice(('girl', 'boy')), x, y, 'adult', 'side', 'walk', r.randrange(4), 'neutral', r.choice(('auto', 'phone')),
               2 if y > 200 else 1, flip=r.random() < 0.5)
    for k in range(12):
        x = r.uniform(0, W); y = r.uniform(30, 150)
        d.rectangle([x, y, x + 4, y + 3], fill=(250, 250, 250))
    grade(img, 0.0, (0.95, 0.97, 1.02))
    look = int(lt * 2.4)
    person(img, 'girl', 240, 238, 'adult', 'side' if look < 3 else 'front', 'stand', 0, 'surprised' if look < 3 else 'sad', 'down', 2,
           flip=look % 2 == 1)
    pts = glyph_pts('?', 5)
    g = ease(span(lt, 0.5, 1.5))
    for i, (px, py) in enumerate(pts):
        rr = rng(i)
        sx, sy = rr.uniform(-240, 240), rr.uniform(-150, 150)
        x = 240 + lerp(sx, px, g); y = 104 + lerp(sy, py, g)
        d.rectangle([x, y, x + 1, y + 1], fill=lerpc((120, 120, 140), (255, 214, 80), g))
    if g >= 1:
        glow(img, 240, 104, 60, (255, 230, 150), 0.35)


s_freeze.tr = 'cut'


# ---------------------------------------------------------------- 第 21 句：两条扶梯交错而过，画面沿对角线裂开
def escalator(img, d, x0, y0, x1, y1, t, dirn, col=(168, 172, 188)):
    d.polygon([(x0, y0), (x1, y1), (x1, y1 + 18), (x0, y0 + 18)], fill=(120, 124, 140))
    d.polygon([(x0, y0), (x1, y1), (x1, y1 + 6), (x0, y0 + 6)], fill=col)
    n = 30
    for k in range(n):
        f = ((k / n) + t * 0.06 * dirn) % 1
        x = lerp(x0, x1, f); y = lerp(y0, y1, f)
        d.line([(x, y), (x, y + 5)], fill=(130, 134, 150))
    tfill(img, 'polygon', [(x0, y0 - 22), (x1, y1 - 22), (x1, y1), (x0, y0)], (200, 230, 250), 0.25)
    d.line([(x0, y0 - 22), (x1, y1 - 22)], fill=(40, 44, 60), width=3)


def s_escalator(img, d, lt, dur, T, A):
    sky(img, ((0, (40, 46, 80)), (1, (90, 96, 140))), 0, H)
    for x in range(0, W, 40): d.line([(x, 0), (x, H)], fill=(70, 78, 120))
    for y in range(0, H, 30): d.line([(0, y), (W, y)], fill=(70, 78, 120))
    for i, (bx, by, bw, bh) in enumerate([(30, 20, 110, 60), (340, 14, 120, 64)]):
        d.rectangle([bx, by, bx + bw, by + bh], fill=(20, 20, 30))
        if i == 0:
            for k in range(5):
                hgt = int((k + 1) * 9 * (0.6 + 0.4 * math.sin(T * 2 + k)))
                d.rectangle([bx + 10 + k * 20, by + bh - 6 - hgt, bx + 22 + k * 20, by + bh - 6], fill=(255, 210, 90))
            d.line([(bx + 8, by + bh - 10), (bx + bw - 8, by + 10)], fill=(255, 120, 120), width=2)
        else:
            clock_face(d, bx + 30, by + 32, 20, T * 6, 1)
            text(img, '加油!', bx + 86, by + 32, (255, 255, 255), (200, 60, 60), FONT)
        glow(img, bx + bw / 2, by + bh / 2, 80, (150, 180, 255), 0.15)
    for k in range(5):
        y = 70 + k * 40
        person(img, 'boy' if k % 2 else 'girl', (k * 97 + T * 40 * (1 if k % 2 else -1)) % (W + 40) - 20, y, 'adult', 'side', 'walk', wph(T + k, 8),
               'neutral', 'phone', 1, flip=k % 2 == 0, tint=(90, 96, 140))
    def pos(f, up):
        if up: return lerp(30, 450, f), lerp(250, 70, f)
        return lerp(30, 450, f), lerp(70, 250, f)
    cross = 2.4
    def prog(t):
        return 0.5 + (t - cross) * 0.11 + 0.04 * math.tanh((t - cross) * 2.5)
    escalator(img, d, 30, 250, 450, 70, T, 1)
    fa = prog(lt)
    gx, gy = pos(fa, True)
    person(img, 'girl', gx, gy + 2, 'adult', 'side', 'stand', 0, 'down', 'phone', 2)
    escalator(img, d, 30, 70, 450, 250, T, -1, (176, 180, 196))
    fb = prog(lt)
    bx, by = pos(fb, False)
    person(img, 'boy', bx, by + 2, 'adult', 'side', 'stand', 0, 'down', 'phone', 2)
    if abs(lt - cross) < 0.6:
        k = 1 - abs(lt - cross) / 0.6
        r = 20 + (1 - k) * 40
        d.ellipse([240 - r, 150 - r * 0.7, 240 + r, 150 + r * 0.7], outline=lerpc((80, 80, 120), (255, 230, 240), k))
        heart_at(img, 232, 112, 5, 0, k); heart_at(img, 248, 112, 5, 1, k)
    if lt > 3.9:
        f = ease(span(lt, 3.9, dur))
        a = np.asarray(img).copy()
        yy, xx = np.mgrid[0:H, 0:W]
        upper = (yy - 160) < (xx - 240) * -0.43
        sh = int(10 * f)
        out = np.zeros_like(a)
        out[:] = (20, 16, 30)
        ua = np.roll(np.roll(a, -sh, 0), -sh, 1); la = np.roll(np.roll(a, sh, 0), sh, 1)
        out[upper] = ua[upper]; out[~upper] = la[~upper]
        img.paste(Image.fromarray(out))
        for x in range(0, W, 2):
            y = 160 - (x - 240) * 0.43
            d.point((x, y + (2 if (x // 6) % 2 else -2)), fill=(255, 255, 255))


s_escalator.tr = 'cut'


# ---------------------------------------------------------------- 空档：她停下来，给他打电话
@lru_cache(None)
def wallpaper(w, h):
    if SNAP is None: return Image.new('RGB', (w, h), (200, 190, 170))
    return SNAP(104.6).crop((222, 20, 332, 240)).resize((w, h), Image.NEAREST)


def s_call(img, d, lt, dur, T, A):
    stop = 3.4
    if lt < stop:
        sky(img, ((0, (10, 12, 40)), (1, (60, 40, 90))), 0, 200)
        stars(d, T, 80, 0.6)
        city(img, d, 176, 111, T * 2, (40, 34, 80), (255, 210, 130), 40, 130, 0.45, T)
        d.rectangle([0, 176, W, 214], fill=(30, 26, 50))
        for k in range(8):
            f = (lt * 0.8 + k / 8) % 1
            x = lerp(-40, W + 40, f) if k % 2 else lerp(W + 40, -40, f)
            c = (255, 240, 200) if k % 2 else (255, 80, 80)
            d.line([(x, 196 + (k % 3) * 4), (x - 30 if k % 2 else x + 30, 196 + (k % 3) * 4)], fill=c)
        d.rectangle([0, 214, W, H], fill=(70, 66, 90))
        for k in range(5):
            sp = 120 + k * 30
            x = (k * 151 + lt * sp * (1 if k % 2 else -1)) % (W + 80) - 40
            person(img, 'boy' if k % 2 else 'girl', x, 254, 'adult', 'side', 'walk', wph(lt + k, 12), 'neutral', 'phone', 3,
                   flip=k % 2 == 0, tint=(100, 96, 130), alpha=0.55)
        ph = lt > 0.9
        person(img, 'girl', 240, 256, 'adult', 'side', 'stand', 0, 'down' if ph else 'neutral', 'phone' if ph else 'down', 3)
        if ph: glow(img, 258, 184, 14, (200, 230, 255), 0.55)
        d.rectangle([0, 212, W, 214], fill=(140, 140, 170))
        for x in range(0, W, 16): d.rectangle([x, 214, x + 1, 240], fill=(120, 120, 150))
        d.rectangle([0, 238, W, 240], fill=(140, 140, 170))
        darken(img, 0.25 * span(lt, 2.2, stop), (0, 0, 0))
        return
    k = lt - stop
    sky(img, ((0, (16, 14, 40)), (1, (40, 26, 60))), 0, H)
    for i in range(14):
        r = rng(i + 7)
        glow(img, r.uniform(0, W), r.uniform(0, H), r.uniform(20, 40), r.choice([(255, 180, 120), (255, 120, 150), (120, 160, 255)]), 0.25)
    d.rounded_rectangle([176, 10, 304, 266], radius=16, fill=(30, 30, 40))
    d.rounded_rectangle([178, 12, 302, 264], radius=15, fill=(54, 54, 70))
    sx0, sy0, sx1, sy1 = 186, 30, 294, 246
    sw, sh = sx1 - sx0, sy1 - sy0
    scr = wallpaper(sw, sh).copy()
    sd = ImageDraw.Draw(scr); sd.fontmode = '1'
    if k < 1.0:
        text(scr, '23:41', sw / 2, 34, (255, 255, 255), (60, 40, 50), FONT, scale=2)
        if k > 0.6:
            slide = int(ease((k - 0.6) / 0.4) * sh)
            scr2 = Image.new('RGB', (sw, sh), (36, 40, 70)); scr2.paste(scr.crop((0, slide, sw, sh)), (0, 0)); scr = scr2
    else:
        dark = Image.new('RGB', (sw, sh), (30, 32, 60))
        scr = Image.blend(scr, dark, 0.7)
        sd = ImageDraw.Draw(scr); sd.fontmode = '1'
        av = head_img('boy', 'adult', 'smile' if k < 3.9 else 'happy', 4)
        ax, ay = sw // 2, 70
        calling = k < 3.9
        if calling:
            for j in range(3):
                f = ((k * 0.8) + j / 3) % 1
                r = 34 + f * 30
                sd.ellipse([ax - r, ay - r, ax + r, ay + r], outline=lerpc((200, 220, 255), (30, 32, 60), f))
        bounce = 0 if calling else int(4 * abs(math.sin((k - 3.9) * 6)) * max(0, 1 - (k - 3.9)))
        sd.ellipse([ax - 33, ay - 33 - bounce, ax + 33, ay + 33 - bounce], fill=(250, 220, 230))
        scr.paste(av, (ax - 32, ay - 34 - bounce), av)
        if calling:
            n = int(k * 3) % 4
            text(scr, '·' * n if n else ' ', sw / 2, 128, (255, 255, 255), None, FONT, shadow=False)
            sd.ellipse([sw / 2 - 14, sh - 44, sw / 2 + 14, sh - 16], fill=(230, 70, 70))
        else:
            sec = int((k - 3.9) + 1)
            text(scr, f'00:{sec:02d}', sw / 2, 128, (255, 255, 255), None, FONT_S, shadow=False)
            for j in range(9):
                hgt = 3 + int(10 * abs(math.sin(T * 9 + j * 1.3)))
                sd.rectangle([sw / 2 - 36 + j * 8, 152 - hgt, sw / 2 - 32 + j * 8, 152 + hgt], fill=(150, 230, 180))
            sd.ellipse([sw / 2 - 14, sh - 44, sw / 2 + 14, sh - 16], fill=(230, 70, 70))
        if k < 1.6:
            sd.ellipse([sw / 2 - 14, sh - 44, sw / 2 + 14, sh - 16], fill=(80, 200, 110))
            put(scr, 'heart', sw / 2, sh - 30, 1, tint=(255, 255, 255))
            if k > 1.2:
                f = (k - 1.2) / 0.4
                sd.ellipse([sw / 2 - 14 - f * 16, sh - 44 - f * 16, sw / 2 + 14 + f * 16, sh - 16 + f * 16], outline=(255, 255, 255))
    img.paste(scr, (sx0, sy0))
    d.rounded_rectangle([226, 18, 254, 22], radius=2, fill=(20, 20, 26))
    thumb_y = 236 if 1.0 < k < 1.6 else 262
    d.ellipse([256, thumb_y - 4, 290, thumb_y + 30], fill=pix.SKIN); d.ellipse([256, thumb_y - 4, 290, thumb_y + 6], fill=lerpc(pix.SKIN, (255, 255, 255), 0.2))
    d.rounded_rectangle([150, 150, 184, 260], radius=12, fill=pix.SKIN)
    for j in range(3): d.line([(170, 170 + j * 24), (184, 170 + j * 24)], fill=pix.SKIN_S)
    if k > 3.9:
        for j in range(6):
            f = ((k - 3.9) * 0.7 + j / 6) % 1
            put(img, 'heart', 240 + math.sin(j * 2 + k * 2) * 60, 120 - f * 110, 1, alpha=1 - f)
        glow(img, 240, 138, 120, (255, 200, 220), 0.12)


# ---------------------------------------------------------------- 第 22 句：同一个月亮下面，两扇窗在打电话
def window_room(who, flip, ww, wh, lit, curtain, t):
    """窗户里面：暖光的房间和打电话的人，画在窗户大小的小图里"""
    im = Image.new('RGB', (ww, wh)); d = ImageDraw.Draw(im)
    im.paste(pix.vgrad(ww, wh, ((0, lerpc(lit, (255, 255, 255), 0.3)), (1, lit)), 3))
    person(im, who, ww // 2, wh + 12, 'adult', 'side', 'stand', 0, 'happy' if int(t * 0.7) % 2 else 'laugh', 'phone', 1, flip=flip)
    d.rectangle([0, 0, 4, wh], fill=curtain); d.rectangle([ww - 5, 0, ww, wh], fill=curtain)
    d.line([(ww // 2, 0), (ww // 2, 2)], fill=curtain)
    return im


def apartment(img, d, x0, x1, top, win, who, flip, lit, curtain, T, col=(34, 30, 70)):
    d.rectangle([x0, top, x1, H], fill=col)
    d.rectangle([x0, top, x1, top + 3], fill=lerpc(col, (110, 100, 160), 0.5))
    rr = rng(x0)
    for yy in range(top + 8, H, 13):
        for xx in range(x0 + 6, x1 - 8, 12):
            d.rectangle([xx, yy, xx + 6, yy + 8], fill=(250, 210, 130) if rr.random() < 0.25 else (24, 20, 48))
    wx, wy, ww, wh = win
    glow(img, wx + ww / 2, wy + wh / 2, 60, lit, 0.45)
    d.rectangle([wx - 3, wy - 3, wx + ww + 2, wy + wh + 4], fill=(70, 60, 90))
    img.paste(window_room(who, flip, ww, wh, lit, curtain, T), (wx, wy))
    d.rectangle([wx - 5, wy + wh, wx + ww + 4, wy + wh + 3], fill=(96, 86, 120))


def s_moon(img, d, lt, dur, T, A):
    sky(img, ((0, (6, 8, 32)), (0.6, (26, 22, 70)), (1, (64, 40, 104))), 0, 210)
    stars(d, T, 200, 1, 240)
    mx, my = 240, 66
    glow(img, mx, my, 110, (230, 230, 255), 0.35 + 0.08 * pulse(T, 0.6))
    moon(d, mx, my, 40, (252, 248, 222))
    for i in range(3):
        cx = (T * 6 + i * 190) % 640 - 120
        tfill(img, 'ellipse', [cx, 50 + i * 22, cx + 130, 56 + i * 22], (70, 60, 110), 0.3)
    meteor(d, lt, 4.2, 430, 20, -120, 46, 0.8)
    for k in range(3):
        y = 186 + k * 6
        d.polygon([(150 + k * 10, 210), (200 + k * 8, y - 14 + k * 3), (250 - k * 6, 210)], fill=(40, 32, 80))
        d.polygon([(220 + k * 12, 210), (280 - k * 4, y - 10), (330 - k * 6, 210)], fill=(46, 36, 88))
    d.rectangle([150, 208, 330, H], fill=(18, 20, 52))
    for k in range(10):
        y = 212 + k * 5
        w = 12 - k + 3 * math.sin(T * 3 + k)
        if w > 0: d.line([(mx - w + 3 * math.sin(T * 2 + k), y), (mx + w + 3 * math.sin(T * 2 + k), y)], fill=lerpc((210, 210, 245), (18, 20, 52), k / 12))
    apartment(img, d, 24, 160, 116, (70, 146, 40, 32), 'girl', False, (255, 214, 130), (240, 190, 70), T)
    apartment(img, d, 322, 456, 104, (372, 134, 40, 32), 'boy', True, (176, 206, 255), (90, 130, 210), T, (30, 30, 72))
    p0, p1, p2 = (100, 148), (240, 10), (380, 136)
    g = eout(span(lt, 0.3, 1.8))
    n = 60
    for i in range(int(n * g)):
        u = i / n
        x = (1 - u) ** 2 * p0[0] + 2 * u * (1 - u) * p1[0] + u * u * p2[0]
        y = (1 - u) ** 2 * p0[1] + 2 * u * (1 - u) * p1[1] + u * u * p2[1]
        c = lerpc((255, 220, 150), (170, 210, 255), u)
        if i % 2 == 0: d.rectangle([x, y, x + 1, y + 1], fill=c)
        if i % 6 == 0: glow(img, x, y, 6, c, 0.35)
    if g >= 1:
        for j in range(4):
            u = ((lt * 0.35 + j / 4) % 1)
            if j % 2: u = 1 - u
            x = (1 - u) ** 2 * p0[0] + 2 * u * (1 - u) * p1[0] + u * u * p2[0]
            y = (1 - u) ** 2 * p0[1] + 2 * u * (1 - u) * p1[1] + u * u * p2[1]
            put(img, 'heart', x, y, 1, tint=YEL if j % 2 == 0 else BLU_L)
    vig(img, 0.35)


s_moon.tr = 'iris'; s_moon.tr_dur = 0.8; s_moon.tr_at = (240, 140)


# ---------------------------------------------------------------- 第 23 句：雪地里打雪仗
def pine(d, x, base, s=1.0):
    d.rectangle([x - 2 * s, base - 8 * s, x + 2 * s, base], fill=(100, 72, 56))
    for k in range(3):
        w = (16 - k * 4) * s; y = base - (8 + k * 12) * s
        d.polygon([(x - w, y), (x + w, y), (x, y - 16 * s)], fill=(46, 100, 80))
        d.polygon([(x - w * 0.6, y - 6 * s), (x + w * 0.5, y - 5 * s), (x, y - 16 * s)], fill=(250, 252, 255))


def snowman(d, x, base, head=True, hx=0, hy=0):
    d.ellipse([x - 16, base - 28, x + 16, base], fill=(250, 252, 255)); d.arc([x - 16, base - 28, x + 16, base], 20, 160, fill=(200, 214, 236), width=2)
    d.ellipse([x - 11, base - 46, x + 11, base - 24], fill=(250, 252, 255))
    for k in range(3): d.point((x, base - 40 + k * 5), fill=(50, 50, 60))
    d.line([(x - 10, base - 36), (x - 22, base - 44)], fill=(110, 80, 60)); d.line([(x + 10, base - 36), (x + 22, base - 46)], fill=(110, 80, 60))
    hxc, hyc = x + hx, base - 54 + hy
    if head:
        d.ellipse([hxc - 8, hyc - 8, hxc + 8, hyc + 8], fill=(250, 252, 255))
        d.point([(hxc - 3, hyc - 2), (hxc + 3, hyc - 2)], fill=(40, 40, 50))
        d.polygon([(hxc, hyc), (hxc + 8, hyc + 1), (hxc, hyc + 2)], fill=(255, 140, 40))
    d.rectangle([x - 11, base - 48, x + 11, base - 45], fill=(220, 70, 80)); d.rectangle([x + 6, base - 46, x + 9, base - 38], fill=(220, 70, 80))


def snowball_path(t, t0, t1, p0, p1, peak=30):
    f = span(t, t0, t1)
    if not t0 <= t <= t1: return None
    return lerp(p0[0], p1[0], f), lerp(p0[1], p1[1], f) - peak * math.sin(math.pi * f)


def splat(d, k, x, y, n=14):
    if not 0 <= k < 0.5: return
    for i in range(n):
        a = i / n * 2 * math.pi
        r = 3 + k * 40
        d.rectangle([x + math.cos(a) * r, y + math.sin(a) * r * 0.7 + k * k * 30, x + math.cos(a) * r + 1, y + math.sin(a) * r * 0.7 + k * k * 30 + 1],
                    fill=(255, 255, 255), outline=(190, 204, 230) if i % 3 == 0 else None)


def s_snow(img, d, lt, dur, T, A):
    sky(img, ((0, (170, 190, 220)), (1, (226, 232, 244))), 0, 170)
    hills(d, 168, 6, 0.016, 1, (214, 224, 240))
    for i, x in enumerate((24, 70, 400, 446)): pine(d, x, 190 + (i % 2) * 6, 1.6)
    d.rectangle([0, 186, W, H], fill=(246, 248, 254))
    for i in range(30):
        x = (i * 41) % W; y = 192 + (i * 17) % 60
        d.line([(x, y), (x + 8, y)], fill=(222, 230, 246))
    for i, (hx, hw, hh, col) in enumerate([(122, 40, 26, (200, 120, 100)), (168, 30, 20, (120, 150, 190)), (292, 44, 28, (220, 180, 110)), (342, 34, 22, (160, 120, 150))]):
        base = 188
        d.rectangle([hx, base - hh, hx + hw, base], fill=col)
        d.polygon([(hx - 4, base - hh + 1), (hx + hw + 4, base - hh + 1), (hx + hw / 2, base - hh - 14)], fill=(250, 252, 255))
        d.rectangle([hx + 6, base - hh + 7, hx + 12, base - hh + 13], fill=(255, 220, 140)); glow(img, hx + 9, base - hh + 10, 10, (255, 210, 130), 0.35)
        d.rectangle([hx + hw - 10, base - hh - 10, hx + hw - 6, base - hh - 2], fill=lerpc(col, (0, 0, 0), 0.2))
        steam(img, d, hx + hw - 8, base - hh - 12, T + i, 2, 16, (240, 240, 250), 0.5, 3)
    lamp(img, d, 240, 200, 0.6, 50)
    d.rectangle([236, 148, 245, 150], fill=(250, 252, 255))
    sm_hit = 4.0
    if lt < sm_hit: snowman(d, 60, 232)
    else:
        k = lt - sm_hit
        hx = 30 * min(1, k / 0.6) ; hy = -30 * math.sin(math.pi * min(1, k / 0.6)) + 46 * min(1, k / 0.6)
        snowman(d, 60, 232, True, hx - 26, hy)
        splat(d, k, 60, 178)
    sc = (BLU, YEL)
    gx, bx = 150, 330
    # 她先扔
    g_arms, g_ph, g_expr, g_pose, g_y = 'down', 0, 'happy', 'stand', 230
    b_arms, b_ph, b_expr = 'down', 0, 'happy'
    if 0.5 < lt < 1.4: g_arms, g_ph = 'throw', (0 if lt < 1.0 else 1)
    if 1.6 < lt < 2.6: g_expr = 'laugh'; b_expr = 'closed'
    if 2.5 < lt < 3.4: b_arms, b_ph = 'throw', (0 if lt < 3.0 else 1)
    if 3.2 < lt < 3.9: g_pose = 'jump'; g_y = 230 - 10 * math.sin(math.pi * span(lt, 3.2, 3.9)); g_expr = 'surprised'
    if lt > 4.1: g_expr = b_expr = 'laugh'
    hit_x = 2 * ease(span(lt, 1.6, 1.8)) * (1 - span(lt, 2.2, 2.6))
    walk = span(lt, 5.4, 6.8)
    bxx = lerp(bx + hit_x * 3, 196, ease(walk))
    if 5.4 < lt < 6.8:
        person(img, 'boy', bxx, 230, 'adult', 'side', 'walk', wph(lt, 8), 'laugh', 'auto', 2, flip=True, scarf=sc[1])
    else:
        person(img, 'boy', bxx, 230, 'adult', 'side', 'stand', b_ph, b_expr if lt < 1.6 or lt > 1.75 else 'surprised', b_arms, 2,
               flip=True, scarf=sc[1])
    person(img, 'girl', gx, g_y, 'adult', 'side', g_pose, g_ph, g_expr, g_arms, 2, scarf=sc[0])
    p = snowball_path(lt, 1.0, 1.6, (gx + 12, 190), (bx - 4, 190), 26)
    if p: d.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(255, 255, 255), outline=(170, 184, 216))
    splat(d, lt - 1.6, bx - 6, 190, 20)
    if 1.6 < lt < 2.5:
        for k in range(5): d.point((bx - 8 + k * 2, 186 + (k % 2) * 3), fill=(255, 255, 255))
        for k in range(3): twinkle(d, bx - 10 + k * 10, 172 - (k % 2) * 6, ((lt - 1.6) * 2 + k * 0.3) % 1, (255, 230, 120), 2)
    p = snowball_path(lt, 3.0, 4.0, (bx - 14, 190), (64, 178), 34)
    if p: d.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(255, 255, 255), outline=(170, 184, 216))
    if lt > 6.8:
        f = ((lt - 6.8) * 0.6) % 1
        put(img, 'heart', 174, 168 - f * 24, 1 if f > 0.15 else 2, alpha=1 - f)
    for x0, t0 in ((gx + 14, 0.0), (bxx - 14, 0.6)):
        f = ((lt + t0) % 1.4) / 1.4
        if f < 0.5: tfill(img, 'ellipse', [x0 - 2 + f * 6, 184 - f * 8, x0 + 3 + f * 6, 188 - f * 8], (255, 255, 255), 0.7 * (1 - f * 2))
    snow(d, T, 160, 20, (255, 255, 255), H, 5, 8)
    put(img, 'bird', 60, 200, 1, tint=(220, 70, 60)) if lt > 5 else None


# ---------------------------------------------------------------- 第 24 句：坐夜车去见他，在起雾的窗上画一颗心
def s_train(img, d, lt, dur, T, A):
    arrive = span(lt, 6.4, dur)
    sky(img, ((0, (8, 10, 34)), (1, lerpc((40, 30, 80), (120, 70, 110), arrive))), 0, H)
    stars(d, T, 120, 0.8)
    moon(d, 400, 34, 12)
    off = lt * 60
    city(img, d, 170, 131, off * 0.3, (30, 28, 66), (255, 214, 140), 20, 90, 0.3 + 0.3 * arrive, T)
    city(img, d, 200, 132, off * 1.2, (22, 18, 48), (255, 200, 120), 30, 110, 0.4 + 0.3 * arrive, T)
    for i in range(6):
        x = (i * 110 - off * 6) % 660 - 80
        d.rectangle([x, 40, x + 3, 240], fill=(20, 16, 36))
        d.line([(x - 40, 44), (x + 40, 44)], fill=(20, 16, 36))
        glow(img, x, 44, 20, (255, 220, 160), 0.3)
    bob = int(math.sin(lt * 9) > 0.7)
    ty = 74 + bob
    d.rounded_rectangle([-20, ty, W + 20, ty + 160], radius=10, fill=(200, 206, 216))
    d.rectangle([-20, ty + 120, W + 20, ty + 128], fill=(236, 120, 90))
    d.rectangle([-20, ty + 129, W + 20, ty + 132], fill=(160, 166, 180))
    for x0 in (20, 380):
        d.rounded_rectangle([x0, ty + 18, x0 + 80, ty + 100], radius=8, fill=(255, 226, 180))
        for k in range(2):
            person(img, 'boy' if k else 'girl', x0 + 20 + k * 38, ty + 120, 'adult', 'side', 'sit', 0, 'closed', 'lap', 2, flip=k == 1, tint=(150, 120, 110))
        d.rounded_rectangle([x0 - 2, ty + 16, x0 + 82, ty + 102], radius=9, outline=(150, 156, 170), width=3)
    wx0, wy0, wx1, wy1 = 140, ty + 14, 340, ty + 106
    room = Image.new('RGB', (wx1 - wx0, wy1 - wy0)); rd = ImageDraw.Draw(room)
    room.paste(pix.vgrad(room.width, room.height, ((0, (255, 236, 200)), (1, (240, 200, 150))), 3))
    rd.rounded_rectangle([22, 36, 52, 120], radius=6, fill=(70, 120, 130))
    expr = 'smile' if lt < 2.6 else ('blush' if lt < 5.6 else 'happy')
    arms = 'reach' if 3.4 < lt < 5.0 else ('phone' if lt > 6.0 else 'lap')
    person(room, 'girl', 66, 118, 'adult', 'side', 'sit', 0, expr, arms, 3)
    if lt > 6.0: glow(room, 94, 40, 10, (200, 230, 255), 0.6)
    img.paste(room, (wx0, wy0))
    fog = span(lt, 2.6, 3.2) * (1 - span(lt, dur - 1.2, dur))
    if fog > 0:
        tfill(img, 'ellipse', [222, ty + 22, 306, ty + 86], (240, 244, 250), 0.45 * fog)
        g = span(lt, 3.4, 5.0)
        pts = [(264 + x * 1.5, ty + 54 + y * 1.4) for x, y in pix.HEART_PTS]
        n = int(len(pts) * g)
        for (x0, y0), (x1, y1) in zip(pts[:n], pts[1:n + 1]):
            d.line([(x0, y0), (x1, y1)], fill=(255, 236, 244), width=2)
        if g >= 1: glow(img, 264, ty + 54, 26, (255, 200, 220), 0.25)
    d.rounded_rectangle([wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 3], radius=10, outline=(140, 146, 160), width=4)
    tfill(img, 'polygon', [(wx0 + 20, wy0), (wx0 + 50, wy0), (wx0 + 10, wy1), (wx0 - 20, wy1)], (255, 255, 255), 0.12)
    d.rectangle([0, ty + 160, W, H], fill=(40, 36, 46))
    for x in range(0, W, 12): d.rectangle([x - int(off * 8) % 12, ty + 166, x + 6 - int(off * 8) % 12, ty + 170], fill=(80, 72, 70))
    for i in range(4):
        x = 30 + i * 128 + 6 * math.sin(lt * 3 + i)
        d.ellipse([x - 7, ty + 150, x + 7, ty + 164], fill=(54, 54, 64))
        if int(lt * 14 + i) % 9 == 0: twinkle(d, int(x + 8), ty + 162, 0.5, (255, 220, 120), 2)
    if arrive > 0:
        for i in range(4):
            x = (i * 140 - lt * 300) % 600 - 60
            tfill(img, 'rectangle', [x, 0, x + 30, H], (255, 240, 200), 0.12 * arrive)


# ---------------------------------------------------------------- 第 25 句：车站重逢，再转成两张大侧脸的特写
@lru_cache(None)
def portrait(who, eye='open', blush=0, mouth='smile', look=0):
    """大特写的侧脸（朝右），120×150。blush 取 0..4 档"""
    im = Image.new('RGBA', (120, 150)); d = ImageDraw.Draw(im)
    girl = who == 'girl'
    L = pix.LOOK[(who, 'adult')]
    hair, hair_s, hair_l = L['hair'], L['hair_s'], L['hair_l']
    skin, skin_s = pix.SKIN, pix.SKIN_S
    coat, coat_s = L['top'], L['top_s']
    scarf = BLU if girl else YEL
    d.polygon([(6, 150), (114, 150), (106, 132), (88, 122), (32, 122), (14, 132)], fill=coat)
    d.line([(60, 128), (60, 150)], fill=coat_s)
    if girl:
        d.ellipse([12, 18, 84, 100], fill=hair)
        d.rounded_rectangle([14, 56, 60, 132], radius=14, fill=hair)
        d.line([(24, 70), (22, 124)], fill=hair_s, width=2); d.line([(40, 80), (38, 128)], fill=hair_s, width=2)
    else:
        d.ellipse([18, 16, 86, 94], fill=hair)
    d.rectangle([56, 94, 74, 118], fill=skin_s)
    d.ellipse([36, 34, 100, 108], fill=skin)
    d.polygon([(86, 40), (100, 58), (106, 72), (100, 77), (102, 84), (99, 91), (96, 100), (84, 108), (64, 108), (60, 70)], fill=skin)
    if not girl:
        d.ellipse([50, 62, 62, 82], fill=skin); d.arc([52, 65, 60, 79], 100, 260, fill=skin_s, width=2)
    d.ellipse([22, 10, 100, 62], fill=hair)
    if girl:
        d.polygon([(60, 28), (104, 46), (101, 62), (95, 55), (91, 64), (85, 55), (79, 62), (73, 52), (60, 52)], fill=hair)
        d.polygon([(38, 44), (54, 50), (50, 104), (40, 98)], fill=hair)
        d.arc([30, 16, 92, 60], 200, 280, fill=hair_l, width=3)
        put(im, 'star', 60, 40, 2, tint=(255, 228, 80))
    else:
        for sx, sy in ((26, 26), (38, 10), (54, 4), (70, 6), (86, 14), (98, 26)):
            d.polygon([(sx - 9, sy + 14), (sx, sy - 4), (sx + 9, sy + 14)], fill=hair)
        d.polygon([(62, 30), (106, 50), (102, 62), (96, 54), (92, 64), (86, 54), (80, 60), (74, 50), (62, 50)], fill=hair)
        d.polygon([(40, 44), (52, 48), (50, 66), (42, 64)], fill=hair)
        d.arc([30, 14, 90, 56], 200, 270, fill=hair_l, width=3)
    d.line([(78, 54), (95, 56)], fill=hair_s, width=2)
    ex, ey = 86, 70
    iris = (126, 72, 50) if girl else (52, 62, 116)
    if eye == 'open':
        d.ellipse([ex - 8, ey - 8, ex + 6, ey + 9], fill=(255, 255, 255))
        d.ellipse([ex - 6 + look, ey - 7, ex + 4 + look, ey + 8], fill=iris)
        d.ellipse([ex - 4 + look, ey - 3, ex + 2 + look, ey + 5], fill=lerpc(iris, (0, 0, 0), 0.5))
        d.rectangle([ex - 3 + look, ey - 5, ex - 1 + look, ey - 3], fill=(255, 255, 255))
        d.rectangle([ex + 1 + look, ey + 3, ex + 2 + look, ey + 4], fill=(255, 255, 255))
        if blush >= 3:
            put(im, 'heart', ex - 1 + look, ey + 1, 1, tint=(255, 120, 160))
        d.line([(ex - 9, ey - 8), (ex + 7, ey - 9)], fill=pix.EYE, width=2)
        d.line([(ex + 6, ey - 9), (ex + 9, ey - 12)], fill=pix.EYE, width=1)
        d.line([(ex - 6, ey + 9), (ex + 4, ey + 9)], fill=lerpc(pix.EYE, skin, 0.5))
    elif eye == 'happy':
        d.arc([ex - 8, ey - 2, ex + 8, ey + 10], 200, 340, fill=pix.EYE, width=2)
    elif eye == 'closed':
        d.arc([ex - 8, ey - 10, ex + 8, ey + 4], 25, 155, fill=pix.EYE, width=2)
    elif eye == 'shy':
        d.line([(ex - 7, ey - 5), (ex + 3, ey), (ex - 7, ey + 5)], fill=pix.EYE, width=2)
    if blush > 0:
        b = Image.new('L', (120, 150)); bd = ImageDraw.Draw(b)
        r = 8 + blush * 2
        bd.ellipse([82 - r, 86 - r * 0.45, 82 + r, 86 + r * 0.45], fill=255)
        m = np.array(b) > 0
        m &= pix.bayer(150, 120) < 0.25 + blush * 0.18
        a = np.array(im); a[m & (a[..., 3] > 0)] = (246, 130, 140, 255); im = Image.fromarray(a); d = ImageDraw.Draw(im)
        if blush >= 3:
            for k in range(3): d.line([(76 + k * 5, 90), (79 + k * 5, 84)], fill=(220, 90, 110))
    mx, my = 99, 89
    if mouth == 'smile': d.line([(mx - 5, my), (mx - 1, my + 1)], fill=pix.MOUTH, width=1); d.point((mx, my), fill=pix.MOUTH)
    elif mouth == 'open': d.pieslice([mx - 7, my - 3, mx + 1, my + 6], 0, 180, fill=(170, 56, 70)); d.line([(mx - 6, my + 1), (mx, my + 1)], fill=(250, 250, 250))
    elif mouth == 'wobble': d.line([(mx - 6, my), (mx - 4, my - 1), (mx - 2, my + 1), (mx, my)], fill=pix.MOUTH)
    else: d.line([(mx - 5, my), (mx, my)], fill=(180, 110, 110))
    d.rounded_rectangle([30, 110, 92, 130], radius=8, fill=scarf)
    d.rectangle([38, 124, 50, 148], fill=scarf)
    for k in range(3): d.line([(38, 128 + k * 6), (50, 128 + k * 6)], fill=lerpc(scarf, (255, 255, 255), 0.4))
    return outline(im, OUT)


def s_gaze(img, d, lt, dur, T, A):
    cut = 3.0
    if lt < cut:
        sky(img, ((0, (12, 14, 44)), (1, (54, 40, 92))), 0, 200)
        stars(d, T, 120, 0.6)
        d.rectangle([20, 100, 200, 200], fill=(70, 60, 96)); d.rectangle([20, 92, 200, 100], fill=(96, 84, 126))
        text(img, '站', 110, 112, (255, 240, 200), (70, 50, 40), FONT)
        d.rectangle([84, 140, 136, 200], fill=(255, 226, 170)); glow(img, 110, 170, 50, (255, 220, 160), 0.4)
        d.rectangle([380, 70, 384, 210], fill=(60, 56, 80)); clock_face(d, 382, 62, 14, 21.5, 1)
        lamp(img, d, 300, 214, 1.0, 76)
        tx, tb = 430, 214
        d.polygon([(tx - 22, tb), (tx + 22, tb), (tx, tb - 70)], fill=(40, 90, 70))
        for i in range(14):
            r = rng(i)
            yy = tb - r.uniform(4, 64); half = (tb - yy) * 22 / 70
            x = tx + r.uniform(-half, half)
            c = [(255, 220, 100), (255, 120, 140), (140, 200, 255)][i % 3]
            if math.sin(T * 3 + i) > -0.3: d.point((x, yy), fill=c); glow(img, x, yy, 4, c, 0.4)
        d.rectangle([0, 200, W, H], fill=(230, 232, 244))
        for i in range(20): d.line([((i * 47) % W, 210 + (i * 13) % 50), ((i * 47) % W + 10, 210 + (i * 13) % 50)], fill=(206, 210, 230))
        seen = lt > 1.8
        gx = lerp(110, 216, ease(span(lt, 0.0, 1.8)))
        if not seen:
            person(img, 'girl', gx, 232, 'adult', 'side', 'walk', wph(lt, 7), 'smile', 'auto', 2, scarf=BLU)
        else:
            person(img, 'girl', gx, 232, 'adult', 'side', 'stand', 0, 'surprised' if lt < 2.3 else 'happy', 'down', 2, scarf=BLU)
        person(img, 'boy', 290, 232, 'adult', 'side' if seen else 'front', 'stand', 0, 'surprised' if 1.8 < lt < 2.3 else 'happy',
               'flowers', 2, flip=True, scarf=YEL)
        bx = 276 if seen else 290
        for dx, c in ((-3, (255, 110, 150)), (0, (255, 220, 100)), (3, (255, 160, 200))):
            d.rectangle([bx + dx - 1, 198, bx + dx + 1, 200], fill=c)
        if seen:
            put(img, 'heart', 252, 172 - (lt - 1.8) * 10, 2 if lt < 2.0 else 1)
        snow(d, T, 120, 16, (255, 255, 255), H, 9, 6)
        return
    k = lt - cut
    sky(img, ((0, (20, 20, 56)), (1, (70, 44, 100))), 0, H)
    for i in range(16):
        r = rng(i + 30)
        x = (r.uniform(0, W) + T * r.uniform(-4, 4)) % W; y = r.uniform(0, H)
        glow(img, x, y, r.uniform(14, 34), r.choice([(255, 170, 200), (255, 220, 140), (150, 180, 255)]), 0.28)
    blush = int(min(4, k / 1.1))
    if k < 2.4: eye, mouth, look, apart = 'open', 'smile', 0, 0
    elif k < 4.4: eye, mouth, look, apart = 'open', 'smile', 1, 0
    elif k < 6.4: eye, mouth, look, apart = ('shy' if int(k * 2) % 3 else 'closed'), 'wobble', 0, ease(span(k, 4.4, 4.8)) * 10
    else: eye, mouth, look, apart = 'happy', 'open', 0, 10 * (1 - ease(span(k, 6.4, 7.0)))
    gl = portrait('girl', eye, blush, mouth, look)
    bl = portrait('boy', eye, blush, mouth, look).transpose(Image.FLIP_LEFT_RIGHT)
    bob = int(round(math.sin(T * 2)))
    img.paste(gl, (int(118 - apart), 76 + bob), gl)
    img.paste(bl, (int(242 + apart), 76 - bob), bl)
    if 2.0 < k < 4.4:
        p = pulse(T, 0.5)
        heart_at(img, 240, 136, 8 + 3 * p)
        r = 14 + 20 * (1 - p)
        d.ellipse([240 - r, 136 - r, 240 + r, 136 + r], outline=lerpc((255, 200, 220), (70, 44, 100), 1 - p))
    if 4.4 < k < 6.6:
        for side, x0 in ((-1, 150), (1, 330)):
            for j in range(3):
                f = ((k - 4.4) * 0.8 + j / 3) % 1
                tfill(img, 'ellipse', [x0 + side * 6 - 6 + f * side * 10, 70 - f * 40, x0 + side * 6 + 6 + f * side * 10, 80 - f * 40],
                      (255, 255, 255), 0.6 * (1 - f))
        put(img, 'drop', 120 - apart, 84 + (k * 10) % 6); put(img, 'drop', 360 + apart, 84 + (k * 10 + 3) % 6)
    if k > 6.4:
        for j in range(10):
            f = ((k - 6.4) * 0.5 + j / 10) % 1
            put(img, 'heart', 240 + math.sin(j * 1.7 + k) * 70, 220 - f * 200, 1 if j % 3 else 2, alpha=1 - f)
    snow(d, T, 70, 12, (255, 255, 255), H, 11, 4)
    if k < 0.15: darken(img, 0.7 * (1 - k / 0.15), (255, 250, 245))


# ---------------------------------------------------------------- 第 26 句：啊——手牵手一直走，一路走到老
SEASON_LEAF = [(255, 184, 210), (84, 170, 92), (236, 140, 60), (246, 248, 255), (255, 184, 210)]
SEASON_FALL = [PETAL_COLS, [(160, 230, 120), (255, 250, 180)], [(240, 150, 60), (250, 200, 80), (220, 100, 50)], [(255, 255, 255)], PETAL_COLS]


def s_lifetime(img, d, lt, dur, T, A):
    hit, still = 6.1, 11.2
    season = clamp(lt / still) * 4
    s0 = min(4, int(season)); s1 = min(4, s0 + 1); sf = season - int(season)
    golden = ease(span(lt, hit - 0.2, hit + 1.2))
    top = lerpc((110, 166, 236), (120, 90, 170), golden); mid = lerpc((200, 220, 246), (255, 160, 130), golden)
    bot = lerpc((255, 240, 220), (255, 214, 150), golden)
    sky(img, ((0, top), (0.75, mid), (1, bot)), 0, 122, 6)
    sun_y = 112 - 4 * golden
    glow(img, 240, sun_y, 90 + 60 * pulse(T, 0.8) * golden, (255, 236, 190), 0.6)
    d.ellipse([224, sun_y - 16, 256, sun_y + 16], fill=(255, 248, 220))
    k = lt - hit
    if 0 <= k < 1.2:
        for j in range(16):
            a = j * math.pi / 8 + k * 0.4
            tfill(img, 'polygon', [(240, sun_y), (240 + math.cos(a - 0.06) * 400, sun_y + math.sin(a - 0.06) * 400),
                                   (240 + math.cos(a + 0.06) * 400, sun_y + math.sin(a + 0.06) * 400)], (255, 250, 220), 0.35 * (1 - k / 1.2))
    for i, (cx, cy, s) in enumerate([(40, 30, 2), (300, 20, 2), (400, 60, 1)]):
        cloud(d, int((cx + lt * 3) % 560 - 60), cy, s, lerpc((255, 255, 255), (255, 200, 190), golden), lerpc((230, 230, 240), (230, 150, 160), golden))
    grass_c = lerpc(lerpc((120, 180, 96), (110, 170, 90), sf), (236, 240, 250), 1 if s0 == 3 else 0)
    if s0 == 3: grass_c = lerpc((236, 240, 250), (120, 180, 96), sf)
    elif s0 == 2: grass_c = lerpc((170, 160, 80), (236, 240, 250), sf)
    elif s0 == 1: grass_c = lerpc((110, 170, 90), (170, 160, 80), sf)
    d.rectangle([0, 120, W, H], fill=grass_c)
    d.polygon([(236, 120), (244, 120), (430, H), (50, H)], fill=(196, 180, 150))
    walking = lt < still
    speed = 0.55 if walking else 0.55 * max(0, 1 - (lt - still) / 0.8)
    travel = lt * 0.55 if walking else still * 0.55 + (0.55 * 0.8 / 2 if lt > still + 0.8 else 0.55 * (lt - still) * (1 - (lt - still) / 1.6))
    for i in range(12):
        z = (i * 0.75 + 10 - travel * 2.2) % 9 + 0.6
        y = 120 + 150 / z * 0.95
        if y > H: continue
        for side in (-1, 1):
            x = 240 + side * (150 + 30 * (i % 2)) / z
            s = 1.8 / z
            leaf = lerpc(SEASON_LEAF[s0], SEASON_LEAF[s1], sf)
            tree_round(d, x, y, s, leaf, lerpc(leaf, (255, 255, 255), 0.3))
    for i in range(14):
        z = (i * 0.6 + 10 - travel * 2.2) % 8.4 + 0.6
        y0 = 120 + 150 / z * 0.95; y1 = 120 + 150 / (z - 0.15) * 0.95 if z > 0.75 else H
        w = 3 / z
        d.polygon([(240 - w, y0), (240 + w, y0), (240 + w * 1.2, min(H, y1)), (240 - w * 1.2, min(H, y1))], fill=(250, 246, 236))
    fall = SEASON_FALL[s0]
    petals(d, T * (1 if walking else 0.3), 50, fall, speed=16 if s0 != 3 else 20, wind=12, seed=s0)
    age = 'young' if lt < 3.6 else ('adult' if lt < 7.6 else 'old')
    for tchg in (3.6, 7.6):
        if 0 <= lt - tchg < 0.6:
            for j in range(10): twinkle(d, 220 + (j * 7) % 44, 170 + (j * 11) % 56, (lt - tchg) / 0.6 + j * 0.05, (255, 255, 230), 3)
    if walking:
        ph = wph(lt, 4)
        person(img, 'girl', 228, 238, age, 'back', 'walk', ph, 'smile', 'hold_r', 2)
        person(img, 'boy', 264, 238, age, 'back', 'walk', (ph + 2) % 4, 'smile', 'hold_l', 2)
    else:
        q = lt - still
        person(img, 'girl', 230, 238, age, 'side', 'stand', 0, 'happy', 'hold', 2)
        person(img, 'boy', 256, 238, age, 'side', 'stand', 0, 'happy', 'hold', 2, flip=True)
        if q > 0.6:
            f = clamp((q - 0.6) / 1.4)
            put(img, 'heart', 243, 176 - f * 20, 2 if f < 0.2 else 1, alpha=1 - f * 0.5)
        darken(img, 0.15 * ease(q / 2.5), (255, 230, 200))


# ---------------------------------------------------------------- 第 27 句：日落的山坡，前面的画面印成拍立得飞上天
PRINTS = [(28.0, 'hotpot'), (43.8, 'hug'), (62.0, 'stroll'), (84.6, 'sunrain'), (104.6, 'umbrella'), (110.0, 'bike'), (150.2, 'fireflies'), (228.6, 'gaze')]
PRINT_POS = [(58, 40), (150, 26), (240, 20), (330, 26), (422, 40), (104, 100), (240, 92), (376, 100)]


def sunset_hill(img, d, T, dusk=0.0):
    sky(img, ((0, lerpc((76, 50, 120), (24, 18, 60), dusk)), (0.45, lerpc((214, 96, 140), (90, 50, 110), dusk)),
              (0.8, lerpc((255, 150, 100), (170, 90, 120), dusk)), (1, lerpc((255, 214, 130), (230, 140, 120), dusk))), 0, 172, 6)
    if dusk > 0.3: stars(d, T, 110, (dusk - 0.3) / 0.7)
    sy_ = 168 + 30 * dusk
    glow(img, 330, sy_, 110, (255, 190, 120), 0.6 * (1 - dusk * 0.7))
    d.ellipse([300, sy_ - 30, 360, sy_ + 30], fill=lerpc((255, 220, 150), (255, 150, 110), dusk))
    for i, (cx, cy, s) in enumerate([(30, 70, 2), (170, 46, 3), (380, 80, 2)]):
        x = int((cx + T * 2) % 600 - 70)
        cloud(d, x, cy, s, lerpc((255, 170, 150), (120, 70, 120), dusk), lerpc((170, 90, 130), (70, 40, 90), dusk))
    d.rectangle([0, 172, W, 214], fill=lerpc((236, 130, 110), (80, 50, 100), dusk))
    for k in range(10):
        y = 174 + k * 4
        w = 34 - k * 2 + 4 * math.sin(T * 2 + k)
        if w > 0: d.line([(330 - w, y), (330 + w, y)], fill=lerpc((255, 220, 160), (200, 130, 130), dusk))
    sil = lerpc((60, 30, 60), (20, 12, 30), dusk)
    d.polygon([(0, 214), (90, 196), (200, 200), (320, 214), (W, 226), (W, H), (0, H)], fill=sil)
    tx = 66
    d.rectangle([tx - 3, 150, tx + 3, 204], fill=sil)
    for bx, by, r in ((tx - 18, 146, 16), (tx + 14, 140, 18), (tx - 2, 126, 20), (tx + 26, 156, 12)):
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=sil)
    d.rectangle([186, 218, 262, 222], fill=sil); d.rectangle([190, 222, 194, 232], fill=sil); d.rectangle([254, 222, 258, 232], fill=sil)
    person(img, 'girl', 214, 232, 'old', 'back', 'sit', 0, 'smile', 'down', 2, tint=sil)
    person(img, 'boy', 238, 232, 'old', 'back', 'sit', 0, 'smile', 'down', 2, tint=sil)
    for i in range(4): bird(d, int((T * 18 + i * 40) % 560 - 40), 120 + i * 6, T, sil, i)


def polaroid(img, d, x, y, ph, dev, alpha=1.0):
    w, h = ph.width, ph.height
    card = Image.new('RGB', (w + 8, h + 14), (252, 250, 244))
    dv = Image.blend(Image.new('RGB', (w, h), (252, 250, 244)), ph, clamp(dev))
    card.paste(dv, (4, 4))
    cd = ImageDraw.Draw(card); cd.rectangle([0, 0, w + 7, h + 13], outline=(200, 190, 176))
    if alpha < 1:
        m = Image.fromarray(((pix.bayer(card.height, card.width) < alpha) * 255).astype(np.uint8))
        img.paste(card, (int(x - card.width / 2), int(y - card.height / 2)), m)
    else:
        img.paste(card, (int(x - card.width / 2), int(y - card.height / 2)))


def s_prints(img, d, lt, dur, T, A):
    sunset_hill(img, d, T)
    step = 1.02
    for i, ((t0, name), (px, py)) in enumerate(zip(PRINTS, PRINT_POS)):
        k = lt - 0.3 - i * step
        if k < 0: continue
        ph = snap_photo(t0, 64, 36)
        fly = ease(span(k, 0.0, 0.9))
        x = lerp(330, px, fly); y = lerp(160, py, fly) - 14 * math.sin(math.pi * fly)
        if fly < 1:
            for j in range(6):
                u = max(0, fly - j * 0.04)
                tx = lerp(330, px, ease(u)); ty = lerp(160, py, ease(u)) - 14 * math.sin(math.pi * ease(u))
                d.point((tx, ty), fill=(255, 240, 210))
        if k < 0.25:
            glow(img, 330, 160, 30, (255, 255, 230), 0.6 * (1 - k / 0.25))
        polaroid(img, d, x, y + math.sin(T * 1.5 + i) * 1.5, ph, span(k, 0.5, 1.5))
        if 0.9 < k < 1.4: twinkle(d, int(px + 30), int(py - 16), (k - 0.9) / 0.5, (255, 255, 240), 3)


def s_outro(img, d, lt, dur, T, A):
    dusk = ease(span(lt, 0.0, 3.0))
    sunset_hill(img, d, T, dusk)
    fade_p = 1 - ease(span(lt, 0.0, 2.0))
    for i, ((t0, name), (px, py)) in enumerate(zip(PRINTS, PRINT_POS)):
        if fade_p > 0: polaroid(img, d, px, py + math.sin(T * 1.5 + i) * 1.5 - (1 - fade_p) * 20, snap_photo(t0, 64, 36), 1, fade_p)
    merge = 0.8
    if lt < merge:
        f = ease(lt / merge)
        y = lerp(196, 120, f)
        heart_at(img, lerp(214, 236, f), y, lerp(5, 12, f), 0); heart_at(img, lerp(238, 244, f), y, lerp(5, 12, f), 1)
    else:
        k = lt - merge
        y = 120 - 30 * ease(min(1, k / 2.5))
        glow(img, 240, y, 50 + 10 * pulse(T, 0.6), (255, 210, 220), 0.5)
        heart_at(img, 240, y, 16 + (2 if k < 0.2 else 0))
        burst(img, d, k, 240, y, BURST, 1.4, 0.8)
        if k < 0.15: darken(img, 0.5 * (1 - k / 0.15), (255, 250, 240))
    ti = pix.META.get('ti', '')
    if ti and lt > 1.6:
        title(img, ti, 240, 160, 2, lt, 1.6, 0.09)
        ar = pix.META.get('ar', '')
        if ar and lt > 2.8: text(img, ar, 240, 192, (236, 226, 255), (40, 24, 70), alpha=ease(span(lt, 2.8, 3.6)))
    if lt > dur - 2.4: dither_fade(img, ease((lt - dur + 2.4) / 2.0), (0, 0, 0))


LYRIC_SCENES = [s_busy, s_hotpot, s_subway, s_hug, s_more, s_stroll, s_bench, s_garden, s_sunrain, s_bloom,
                s_ginkgo, s_album, s_fireflies, s_pond, s_alone, s_emptybench, s_movie, s_emptyseat, s_grid, s_freeze, s_escalator,
                s_moon, s_snow, s_train, s_gaze, s_lifetime, s_prints]
GAP_SCENES = [[s_umbrella, s_bike, s_festival, s_farewell], s_call, s_outro]
