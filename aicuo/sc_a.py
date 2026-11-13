"""爱错 · 片头和第一段主歌。签名都是 (img, d, lt, dur, T, A)：lt 是镜头内的时间，dur 是镜头时长，T 是全片时间，A 是这一帧的音量。

黑暗里落下一片心形红叶，一阵风把它卷走，满天的叶子飞回来拼成片名；片名裂开，北风鼓起腮帮子把它吹散。
然后是北风的故事：黄昏的山坡上北风使劲吹，满树红叶被吹落，那片心形的叶子松开枝头逃走了；
叶子没了消息，北风在空荡荡的原野上找它，最后一个人坐在山顶；冬天来了，北风在亮着暖灯的窗外徘徊，没人开门，
它在结冰的湖边抱着秃树哭，眼泪落下来变成雪。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
import motifs as M
from props import *          # noqa: F401,F403  共用的颜色和道具
from pix import (W, H, FONT, FONT_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky, stars,
                 person, wph, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, BAYER)

YY, XX = np.mgrid[0:H, 0:W]

DUSK = ((0, (46, 44, 88)), (0.45, (112, 84, 128)), (0.78, (206, 120, 120)), (1, (244, 172, 128)))
STORM = ((0, (44, 46, 76)), (0.5, (92, 86, 120)), (0.85, (170, 132, 146)), (1, (206, 160, 150)))
NIGHT_W = ((0, (6, 8, 26)), (0.55, (18, 24, 60)), (1, (44, 48, 96)))
SNOWNIGHT = ((0, (12, 16, 40)), (0.6, (30, 40, 80)), (1, (66, 78, 124)))


def ridge(d, base, amp, freq, ph, col, off=0.0, x0=0, x1=W):
    """起伏的山脊线，下面填满"""
    for x in range(x0, x1):
        xx = x + off
        y = base - amp * (0.6 + 0.4 * math.sin(xx * freq + ph)) * (0.7 + 0.3 * math.sin(xx * freq * 2.7 + ph * 2))
        d.line([(x, int(y)), (x, H)], fill=col)


def hill(d, cx, top, w, col, col2=None):
    """一座圆圆的山坡，(cx, top) 是坡顶"""
    d.ellipse([cx - w, top, cx + w, top + w * 0.9], fill=col)
    if col2: d.arc([cx - w, top, cx + w, top + w * 0.9], 200, 280, fill=col2, width=2)


def drift_clouds(d, T, speed, cols, y0=20, n=5, seed=0, s0=1.6):
    for i in range(n):
        r = rng(i * 13 + seed)
        s = s0 + r.random() * 1.2
        x = (r.uniform(0, W + 200) + T * speed * (0.6 + 0.4 * r.random())) % (W + 200) - 120
        cloud(d, x, y0 + r.uniform(0, 60), s, cols[0], cols[1])


# ================================================================ 片头：红叶、片名、北风
TS = 6                                         # 片名每个像素放大成 6×6 的方块
TITLE_CY = 100


@lru_cache(None)
def title_cells():
    """片名拆成一格一格：[(屏幕 x, 屏幕 y, 颜色, 横向位置 0..1, 随机数)]"""
    s = title_str()
    ims = [big_glyph(c, 1, top=(255, 150, 150), bot=(214, 40, 62), line=(120, 18, 40), out=(34, 8, 24)) for c in s]
    adv = [int(FONT.getlength(c)) for c in s]
    tw = sum(adv) + ims[-1].width - adv[-1]
    th = max(im.height for im in ims)
    ox = W / 2 - tw * TS / 2; oy = TITLE_CY - th * TS / 2
    cells = []
    x = 0
    r = rng(5)
    for im, a in zip(ims, adv):
        arr = np.array(im)
        for py in range(arr.shape[0]):
            for px in range(arr.shape[1]):
                if arr[py, px, 3] > 0:
                    cells.append((ox + (x + px) * TS, oy + py * TS, tuple(int(v) for v in arr[py, px, :3]), (x + px) / tw, r.random()))
        x += a
    return cells, (ox, oy, ox + tw * TS, oy + th * TS)


def crack_x(y, box):
    """片名裂缝在 y 高度的横坐标（锯齿形，从左上斜到右下）"""
    x0, y0, x1, y1 = box
    u = clamp((y - y0) / (y1 - y0))
    zig = 7 * (1 if int(u * 8) % 2 else -1) * (0.5 + abs((u * 8) % 1 - 0.5))
    return lerp(x0 + (x1 - x0) * 0.44, x0 + (x1 - x0) * 0.58, u) + zig


def intro_sky(img, d, T, k):
    """片头的夜空：k 0..1 从全黑亮起来"""
    sky(img, NIGHT_W, 0, H, 6)
    stars(d, T, 200, k, 160)
    if k > 0:
        moon(d, 402, 52, 15)
        glow(img, 402, 52, 46, (200, 210, 255), 0.25 * k)
    ridge(d, 232, 30, 0.013, 0.5, lerpc((0, 0, 0), (26, 30, 58), k))
    ridge(d, 248, 22, 0.02, 2.2, lerpc((0, 0, 0), (16, 18, 38), k))
    M.tree(img, d, 404, 236, 70, T, seed=11, sway=0.5 * math.sin(T), leaf_on=lambda j, r: False, bark=(10, 12, 28), bark_d=(10, 12, 28))
    if k < 1: dither_fade(img, 1 - k, (0, 0, 0))


def s_intro(img, d, lt, dur, T, A):
    cells, box = title_cells()
    bx0, by0, bx1, by1 = box
    gust = 2.69                                                   # 第一阵风：把落下来的那片红叶卷走
    formed = 6.76                                                 # 片名在这一小节线上拼好
    crack_at, split_at = 8.5, 10.08
    blow_at = 11.7
    intro_sky(img, d, T, eout((lt - 0.2) / 2.4))
    # 一道淡淡的光柱照着落下来的红叶
    if lt < gust + 0.4:
        a = clamp(lt / 0.6) * clamp((gust + 0.4 - lt) / 0.4)
        tfill(img, 'polygon', [(222, 0), (258, 0), (290, 200), (190, 200)], (200, 210, 255), 0.07 * a)
    # 风
    if gust - 0.2 < lt < 6.0:
        M.streaks(img, d, T, (0, 30, W, 220), n=int(30 * clamp((lt - gust + 0.2) / 0.3) * clamp((6.0 - lt) / 1.5)), speed=420, seed=3)
    if lt > blow_at - 0.5:
        M.streaks(img, d, T, (0, 40, W, 200), n=int(34 * clamp((lt - blow_at + 0.5) / 0.4)), speed=460, seed=7)
    # 那一片心形红叶：慢慢落下，被风卷走
    if lt < gust + 0.8:
        if lt < gust:
            u = clamp((lt - 0.15) / (gust - 0.15))
            lx, ly = 240 + 18 * math.sin(lt * 2.2), lerp(-14, 118, eout(u))
        else:
            k = lt - gust
            lx, ly = 240 + 18 * math.sin(gust * 2.2) + 600 * k * k + 60 * k, 118 - 50 * k
        M.leaf(img, lx, ly, 2, T, spin=0.4 if lt < gust else 2.0)
        if lt < gust: glow(img, lx, ly, 18, (255, 120, 110), 0.25)
    # 叶子飞进来拼成片名，拼好后裂开，被北风吹散
    split = eout((lt - split_at) / 0.25) * 3 if lt > split_at else 0
    flash = clamp(1 - (lt - formed) / 0.5) if lt > formed else 0
    if lt > formed - 0.3 and lt < blow_at + 2:
        glow(img, W / 2, TITLE_CY, 170, (255, 70, 90), 0.28 * clamp((lt - formed + 0.3) / 0.6) * (0.85 + 0.15 * math.sin(T * 3)) *
             clamp((blow_at + 1.4 - lt) / 1.4), 80)
    for (cx, cy, col, u, r) in cells:
        arrive = 3.2 + u * 3.0 + r * 0.45
        depart = max(gust + 0.05 + r * 0.5, arrive - 1.3 - r * 0.8)
        leave = blow_at + 0.1 + u * 1.3 + r * 0.35
        right = cx + TS / 2 > crack_x(cy, box)
        sx, sy = (split if right else -split), (split * 0.6 if right else -split * 0.6)
        if lt < depart: continue
        if lt < arrive:                                          # 在路上：贝塞尔曲线加一个旋涡
            f = (lt - depart) / (arrive - depart)
            fe = ease(f)
            rr = rng(int(r * 1e6))
            p0 = (-14 - rr.random() * 80, 30 + rr.random() * 190)
            c = (lerp(p0[0], cx, 0.6) + (rr.random() - 0.5) * 140, min(p0[1], cy) - 30 - rr.random() * 90)
            x = (1 - fe) ** 2 * p0[0] + 2 * (1 - fe) * fe * c[0] + fe * fe * cx
            y = (1 - fe) ** 2 * p0[1] + 2 * (1 - fe) * fe * c[1] + fe * fe * cy
            sw = 16 * (1 - fe)
            x += sw * math.cos(rr.random() * 6 + f * 7); y += sw * math.sin(rr.random() * 6 + f * 7)
            if f < 0.82: M.leaf_bit(d, x, y, T, int(r * 97))
            else:
                g = (f - 0.82) / 0.18
                sz = lerp(2, TS, g)
                d.rectangle([x, y, x + sz - 1, y + sz - 1], fill=lerpc(M.LEAF_COLS[int(r * 97) % 5], col, g))
            continue
        if lt < leave:
            k = lt - arrive
            c2 = lerpc((255, 255, 255), col, clamp(k / 0.25))
            if flash > 0: c2 = lerpc(c2, (255, 240, 240), flash * 0.6)
            d.rectangle([cx + sx, cy + sy, cx + sx + TS - 1, cy + sy + TS - 1], fill=c2)
            continue
        k = lt - leave                                           # 被吹走：往右上方翻滚着飞走，越来越小
        rr = rng(int(r * 1e6) + 1)
        x = cx + sx + 230 * k * k + 60 * k + 10 * math.sin(k * 6 + r * 9)
        y = cy + sy - 40 * k * rr.random() + 18 * math.sin(k * 5 + r * 7)
        if x > W + 4: continue
        sz = max(1, round(lerp(TS, 2, clamp(k / 0.45))))
        if sz > 2: d.rectangle([x, y, x + sz - 1, y + sz - 1], fill=col)
        else: M.leaf_bit(d, x, y, T, int(r * 97))
    # 裂缝：一道发亮的锯齿从上往下长，然后两半错开
    if crack_at < lt < blow_at + 0.4:
        f = clamp((lt - crack_at) / 1.2)
        pts = []
        for i in range(25):
            y = lerp(by0 - 6, by1 + 6, i / 24)
            if (i / 24) > f: break
            pts.append((crack_x(y, box), y))
        if len(pts) > 1:
            if split <= 0:
                d.line(pts, fill=(255, 250, 240), width=2)
                glow(img, pts[-1][0], pts[-1][1], 14, (255, 220, 200), 0.5)
            else:
                d.line([(x - split + 1, y - split * 0.6) for x, y in pts], fill=(255, 210, 200))
                d.line([(x + split - 1, y + split * 0.6) for x, y in pts], fill=(255, 210, 200))
        # 裂开时掉下来的碎块
        if lt > split_at:
            for j in range(10):
                rr = rng(j * 7 + 3)
                k = lt - split_at - rr.random() * 0.3
                if k < 0: continue
                y0 = lerp(by0, by1, rr.random())
                x = crack_x(y0, box) + rr.uniform(-4, 4) + rr.uniform(-20, 20) * k
                y = y0 + 160 * k * k
                if y < H: d.rectangle([x, y, x + 2, y + 2], fill=(214, 40, 62) if j % 2 else (255, 150, 150))
    if split_at - 0.02 < lt < split_at + 0.35: shake(img, lt - split_at, 4, 0.35)
    if formed <= lt < formed + 0.3: shake(img, lt - formed, 3, 0.3)
    # 歌手名
    if formed + 0.5 < lt < blow_at + 0.6:
        a = clamp((lt - formed - 0.5) / 0.6) * clamp((blow_at + 0.6 - lt) / 0.5)
        artist = artist_str()
        if artist: text(img, artist, W / 2, by1 + 14, col=(236, 226, 255), alpha=a)
        text(img, '像 素 动 画 M V', W / 2, by1 + 34, col=(170, 160, 210), font=FONT_S, alpha=a * 0.9)
    # 北风从左边飘进来，深吸一口气，鼓起腮帮子吹
    if lt > 9.6:
        k = lt - 9.6
        wx = lerp(-70, 78, eout(k / 1.6)) + (lt > blow_at) * -6 * math.sin(clamp(lt - blow_at) * math.pi)
        mood = 'look' if lt < blow_at - 0.6 else ('calm' if lt < blow_at else 'blow')
        sc = 2 + (0.25 if blow_at - 0.6 < lt < blow_at else 0)
        M.wind(img, wx, 140, sc, T, mood, look=(1, 0) if lt < 10.9 else (1, -1))
    vig(img, 0.4, (6, 6, 20))


# ================================================================ 黄昏山坡上的大风：北风使劲吹
def windy_hill(img, d, T, lt, sway, gust, leaf_on=None, tree_x=336, tree_h=150, wind_mood='blow', wind_x=86, wind_s=2.0, n_streak=36,
               tree_snow=0.0):
    sky(img, STORM, 0, 200, 6)
    glow(img, 380, 186, 140, (255, 170, 130), 0.3, 50)
    drift_clouds(d, T, 70, ((132, 112, 146), (104, 88, 124)), y0=14, n=6, seed=2)
    ridge(d, 196, 34, 0.016, 1.2, (84, 74, 110), T * 6)
    ridge(d, 214, 20, 0.024, 0.4, (66, 60, 92), T * 12)
    hill(d, 330, 196, 260, (74, 76, 70))
    d.rectangle([0, 230, W, H], fill=(64, 66, 62))
    # 被吹弯的草
    for i, x in enumerate(range(0, W, 3)):
        top = 230 if x < 70 or x > 590 else min(230, 196 + (x - 330) ** 2 / 300)
        h = 3 + (i * 7) % 5
        bend = 3 + 2 * math.sin(T * 9 + x * 0.15) * gust
        d.line([(x, top + 1), (x + bend, top - h + 1)], fill=(96, 104, 84) if i % 3 else (120, 126, 96))
    out = M.tree(img, d, tree_x, 200, tree_h, T, seed=3, sway=sway, gust=gust, leaf_on=leaf_on, snow=tree_snow, spread=0.62)
    M.streaks(img, d, T, (0, 20, W, 230), n=n_streak, speed=360, seed=1)
    if wind_mood: M.wind(img, wind_x, 66, wind_s, T, wind_mood)
    return out


def s_north_wind(img, d, lt, dur, T, A):
    gust = 1 + 0.5 * math.sin(T * 1.7) + 0.6 * thump(T, 0.5)
    sway = 2.2 + 0.8 * math.sin(T * 2.2) + 1.0 * thump(T, 0.5)
    out = windy_hill(img, d, T, lt, sway, gust, leaf_on=lambda j, r: r > 0.06 * lt)
    # 已经被扯下来的几片
    for j, (lx, ly) in enumerate(out):
        r = rng(j).random()
        if r > 0.06 * lt: continue
        k = lt - r / 0.06
        M.leaf_bit(d, lx + 140 * k + 20 * k * k, ly - 10 * k + 12 * math.sin(k * 5 + j), T, j)
    shake(img, (T - last_beat(T)), 1.5, 0.2)
    vig(img, 0.35, (20, 16, 40))


# ================================================================ 近处的树冠：叶子一片片被扯走
def s_leaves_fall(img, d, lt, dur, T, A):
    gust = 1.6 + 0.6 * thump(T, 0.5)
    sway = 2.6 + 0.8 * math.sin(T * 2.5)
    frac = lambda t: 0.08 + 0.85 * ease(t / 2.4)

    def on(j, r): return r > frac(lt)
    sky(img, STORM, 0, H, 6)
    drift_clouds(d, T, 110, ((140, 120, 152), (110, 94, 130)), y0=6, n=5, seed=4, s0=2.4)
    out = M.tree(img, d, 250, 360, 330, T, seed=3, sway=sway, gust=gust, leaf_on=on, spread=0.62)
    # 每片叶子在 frac 越过它的随机数时离开枝头，往右飞走
    for j, (lx, ly) in enumerate(out):
        r = rng(j).random()
        if r > frac(lt): continue
        t0 = 0.0
        if r > frac(0):                                              # 反解出离开的时间
            lo, hi = 0.0, lt
            for _ in range(12):
                mid = (lo + hi) / 2
                if frac(mid) < r: lo = mid
                else: hi = mid
            t0 = hi
        k = lt - t0 + (0.6 * r if r <= frac(0) else 0)
        x = lx + 160 * k + 50 * k * k + 10 * math.sin(k * 6 + j)
        y = ly - 20 * k + 40 * k * k * (r - 0.4) + 8 * math.sin(k * 4 + j * 0.7)
        if -4 < x < W + 4 and -4 < y < H: M.leaf_bit(d, x, y, T, j)
    M.streaks(img, d, T, (0, 0, W, H), n=40, speed=480, seed=5, ln=(24, 60))
    M.wind(img, 56, 54, 1.5, T, 'blow')
    vig(img, 0.35, (20, 16, 40))


# ================================================================ 心形的叶子松开枝头，飞过原野
def escape_twig(img, d, t):
    T = t
    sky(img, STORM, 0, H, 6)
    drift_clouds(d, T, 90, ((150, 128, 158), (120, 102, 138)), y0=150, n=4, seed=9, s0=3)
    # 一根粗枝从左上伸进来，枝梢挂着那片心形的叶子
    sw = 2 * math.sin(T * 6) * clamp(t / 1.5)
    pts = [(-10, 40), (90, 62), (180, 78 + sw * 0.3), (250, 92 + sw)]
    d.line(pts, fill=(60, 42, 40), width=9)
    d.line([(x, y + 3) for x, y in pts], fill=(40, 28, 30), width=3)
    d.line([(120, 70), (160, 40), (176, 30)], fill=(60, 42, 40), width=4)
    d.line([(200, 84), (226, 120)], fill=(60, 42, 40), width=3)
    tip = (250, 92 + sw)
    let_go = 2.0
    if t < let_go:
        shiver = math.sin(t * (14 + 30 * t)) * (4 + 10 * t)
        M.leaf(img, tip[0] + 2 + shiver * 0.3, tip[1] + 22, 4, T, spin=0, rot=shiver)
        d.line([tip, (tip[0] + 2 + shiver * 0.3, tip[1] + 6)], fill=(110, 64, 44), width=2)
    else:
        k = t - let_go
        twinkle(d, tip[0] + 2, tip[1] + 6, k / 0.3, (255, 255, 255), 6)
        M.leaf(img, tip[0] + 2 + 180 * k + 160 * k * k, tip[1] + 22 - 60 * k, 4, T, spin=1.6)
    M.streaks(img, d, T, (0, 0, W, H), n=22, speed=420, seed=8)
    vig(img, 0.4, (20, 16, 40))


def escape_flight(img, d, t):
    T = t
    off = t * 160
    sky(img, DUSK, 0, 210, 6)
    sx, sy = 400, lerp(160, 150, t / 4)
    glow(img, sx, sy, 120, (255, 190, 140), 0.45, 60)
    d.ellipse([sx - 18, sy - 18, sx + 18, sy + 18], fill=(255, 226, 180))
    drift_clouds(d, T, -30, ((214, 150, 160), (186, 120, 140)), y0=20, n=5, seed=6)
    ridge(d, 176, 40, 0.011, 0.3, (126, 96, 136), off * 0.1)
    ridge(d, 192, 26, 0.02, 1.6, (100, 80, 118), off * 0.3)
    d.rectangle([0, 196, W, H], fill=(96, 92, 92))
    # 一条河
    for y in range(204, 214):
        d.line([(0, y), (W, y)], fill=(200, 150, 160) if y % 3 else (240, 190, 170))
    ridge(d, 238, 10, 0.03, 0.9, (70, 72, 70), off * 0.8)
    for i in range(26):                                              # 近处一闪而过的草丛
        x = (i * 23 - off * 1.4) % (W + 60) - 30
        h = 8 + (i * 7) % 12
        for k in range(-2, 3):
            d.line([(x + k * 2, H), (x + k * 3 + 4, H - h + abs(k) * 2)], fill=(54, 50, 56) if k % 2 else (70, 64, 70))
    # 红叶飞着，越飞越远；身上一闪一闪地透出她奔跑的影子
    k = clamp(t / 4.3)
    lx = lerp(150, 330, ease(k)) + 10 * math.sin(t * 3)
    ly = lerp(120, 96, k) + 14 * math.sin(t * 2.1)
    s = 3 if k < 0.45 else (2 if k < 0.8 else 1)
    gh = clamp((t - 0.8) / 0.6) * clamp((3.4 - t) / 0.6) * 0.7
    if gh > 0:                                                        # 淡粉色的剪影，在叶子前面跑
        glow(img, lx + 26, ly + 4, 34, (255, 170, 170), 0.25 * gh)
        props.ghost(img, 'girl', lx + 26, ly + 30, 2, gh, pose='run', ph=wph(t, 10), tint=(255, 196, 196))
    M.leaf(img, lx, ly, s, T, spin=1.3)
    for j in range(3):                                                # 叶子身后的风
        q = (t * 1.5 + j / 3) % 1
        tfill(img, 'line', [(lx - 14 - q * 40, ly - 4 + j * 4), (lx - 4 - q * 40, ly - 4 + j * 4)], (255, 240, 240), (1 - q) * 0.8)
    vig(img, 0.3, (40, 20, 40))


def s_escape(img, d, lt, dur, T, A):
    shots(img, lt, [(0, escape_twig), (2.3, escape_flight)], tr=0.4)


# ================================================================ 空荡荡的原野：北风找不到叶子，一个人坐在山顶
def lonely_field(img, d, t, dusk=0.0):
    T = t
    sk = mix_stops(DUSK, ((0, (24, 26, 62)), (0.45, (62, 52, 96)), (0.78, (150, 92, 112)), (1, (210, 130, 110))), dusk)
    sky(img, sk, 0, 210, 6)
    stars(d, T, 120, dusk * 0.6, 60)
    ridge(d, 186, 30, 0.012, 2.0, lerpc((116, 92, 130), (60, 54, 96), dusk))
    d.rectangle([0, 200, W, H], fill=lerpc((110, 96, 92), (60, 58, 72), dusk))
    for i in range(70):
        r = rng(i * 3 + 1)
        x, y = r.uniform(0, W), r.uniform(204, 270)
        d.point((x, y), fill=lerpc((150, 80, 66), (90, 50, 56), dusk) if i % 3 else lerpc((180, 120, 80), (110, 80, 70), dusk))
    hill(d, 120, 186, 150, lerpc((96, 86, 84), (52, 52, 68), dusk))
    M.tree(img, d, 112, 190, 110, T, seed=3, sway=0.6 * math.sin(T), leaf_on=lambda j, r: False, spread=0.62,
           bark=lerpc((60, 44, 44), (30, 28, 44), dusk), bark_d=lerpc((40, 28, 32), (24, 20, 36), dusk))


def lonely_search(img, d, t):
    lonely_field(img, d, t, 0.2 * t / 4.6)
    # 北风从右边飘进来，这边看看那边看看；头上冒出一个问号
    x = lerp(420, 270, eout(t / 2.0)) - 40 * ease((t - 2.4) / 1.6)
    look = (-1, 0) if (t % 2.2) < 1.1 else (1, -1)
    M.wind(img, x, 104 + 4 * math.sin(t * 2), 1.5, t, 'look', look=look, flip=True)
    if 1.0 < t < 4.0:
        k = clamp((t - 1.0) / 0.25)
        text(img, '?', x + 6, 66 - 4 * eback(k), col=(255, 250, 240), alpha=k * clamp((4.0 - t) / 0.3))
    # 树上什么都没有，只剩一片叶子形状的空位（一圈虚线）
    if t > 2.6:
        a = clamp((t - 2.6) / 0.6)
        for i in range(16):
            ang = i / 16 * 6.28 + t
            if i % 2: d.point((150 + math.cos(ang) * 7, 108 + math.sin(ang) * 7), fill=lerpc((140, 120, 140), (255, 240, 240), a))


def lonely_sit(img, d, t):
    lonely_field(img, d, 4.6 + t, clamp(0.25 + t / 4.4))
    moon(d, 380, lerp(150, 110, t / 4.4), 12)
    # 北风缩成一小团，坐在空空的树梢下，叹了一口气
    M.wind(img, 160, 168, 1.0, t, 'sad', look=(0, 1), flip=True, tail=False)
    k = (t - 1.6) / 1.6
    if 0 < k < 1:
        for j in range(3):
            props.puff(img, 140 - k * 30 - j * 6, 166 - j * 2, 2 + k * 3, (220, 232, 250), (1 - k) * 0.7)
    vig(img, 0.45, (10, 10, 30))


def s_lonely(img, d, lt, dur, T, A):
    shots(img, lt, [(0, lonely_search), (4.6, lonely_sit)], tr=0.6)


# ================================================================ 冬天：窗外徘徊的北风，结冰的湖边
def village(img, d, t):
    T = t
    sky(img, SNOWNIGHT, 0, 190, 6)
    stars(d, T, 120, 0.7, 90)
    ridge(d, 170, 26, 0.012, 0.8, (60, 70, 110))
    d.rectangle([0, 186, W, H], fill=(214, 224, 244))
    for x in range(0, W):
        y = 186 + 3 * math.sin(x * 0.04) + 2 * math.sin(x * 0.11)
        d.line([(x, y), (x, 192)], fill=(214, 224, 244))
    for i, (hx, hw, hh, ppl) in enumerate([(40, 60, 44, 3), (160, 70, 50, 4), (290, 56, 40, 2), (390, 64, 46, 3)]):
        M.house(img, d, hx, 196, hw, hh, T, lit=1, seed=i, people=ppl)
    # 北风从右往左飘过一扇扇窗，在第二扇窗前停下来往里看，哈出的气糊在玻璃上
    stop = 2.2
    x = lerp(470, 214, eout(t / stop)) if t < stop + 1.2 else lerp(214, -60, ein((t - stop - 1.2) / 1.6))
    M.wind(img, x, 150 + 3 * math.sin(t * 2), 1.25, t, 'look' if t < stop + 0.6 else 'sad', look=(-1, 0), flip=True)
    if stop < t < stop + 1.2:
        k = (t - stop) / 1.2
        props.puff(img, 186, 160, 3 + 6 * k, (240, 246, 255), 0.6 * (1 - k))
    pix.snow(d, T, n=170, speed=24, wind=10)
    vig(img, 0.4, (8, 10, 30))


def frozen_lake(img, d, t):
    T = t
    sky(img, NIGHT_W, 0, 180, 6)
    stars(d, T, 170, 1, 140)
    moon(d, 330, 54, 18)
    glow(img, 330, 54, 60, (200, 214, 255), 0.3)
    ridge(d, 160, 24, 0.014, 0.4, (36, 44, 84))
    d.rectangle([0, 170, W, H], fill=(140, 160, 206))
    for y in range(170, H, 3):                                        # 冰面的反光
        d.line([(0, y), (W, y)], fill=(156, 176, 220) if (y // 3) % 2 else (130, 150, 198))
    for y in range(176, 250, 3):                                      # 月亮在冰上的倒影
        k = (y - 176) / 74
        wd = 10 - 6 * k + 2 * math.sin(y * 0.7 + T * 2)
        d.line([(330 - wd, y), (330 + wd, y)], fill=lerpc((236, 240, 255), (170, 186, 230), k))
    d.polygon([(0, 186), (150, 170), (210, 176), (230, 200), (0, 214)], fill=(220, 230, 248))
    M.tree(img, d, 120, 186, 130, T, seed=3, sway=0.4 * math.sin(T), leaf_on=lambda j, r: False, snow=1.0, spread=0.62,
           bark=(52, 46, 66), bark_d=(36, 32, 52))
    # 北风蜷在树下哭，眼泪落下来变成雪花
    M.wind(img, 196, 196, 1.25, t, 'cry', flip=True, tail=False, tears=1.0)
    for j in range(16):
        r = rng(j * 5)
        k = (t * 0.35 + r.random()) % 1
        x = 196 + r.uniform(-20, 20) + math.sin(k * 6 + j) * 8
        y = 186 - k * 120
        if k > 0.15:
            pix.twinkle(d, x, y, 0.5, (230, 240, 255), 1 + (j % 2))
    pix.snow(d, T, n=110, speed=16, wind=4)
    props.zoom(img, lerp(1.25, 1.0, ease(t / 4.4)), 220, 160)
    vig(img, 0.45, (6, 8, 26))


def s_winter(img, d, lt, dur, T, A):
    shots(img, lt, [(0, village), (4.8, frozen_lake)], tr=0.6)
