"""爱错 · 第一段副歌和间奏。签名都是 (img, d, lt, dur, T, A)。

故事从北风换到了人：雨夜的路口，她撑着红伞，他转身走开，走了几步才回过头，愣在原地；
一颗心在黑暗里跳，裂开，心电图拉成一条直线；他在楼顶扔出一架纸飞机，纸飞机飞过城市，落进路边的水洼；
他想把大钟往回拨，指针倒转，玻璃却裂了；屏幕上跳出"是否重来？"，倒数到零也选不了"是"，最后只能读取回忆。
"""
import math
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
import motifs as M
from props import *          # noqa: F401,F403
from pix import (W, H, FONT, FONT_S, OUT, SKIN, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky,
                 stars, person, wph, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, city, lamp, BAYER)

YY, XX = np.mgrid[0:H, 0:W]
RAINNIGHT = ((0, (10, 10, 30)), (0.5, (30, 26, 62)), (1, (70, 46, 90)))


# ================================================================ 小道具
def umbrella(d, x, y, s=2, col=(214, 50, 62), col_d=(150, 30, 44), tilt=0.0):
    """红伞，(x, y) 是伞柄顶端（伞尖）"""
    r = 15 * s
    cx, cy = x + tilt * 6 * s, y + 2 * s
    d.pieslice([cx - r, cy - r * 0.55, cx + r, cy + r * 0.75], 180, 360, fill=col)
    for k in range(1, 4):
        a = math.pi * k / 4
        d.line([(cx, cy - r * 0.55 + 1), (cx - math.cos(a) * r, cy + 1)], fill=col_d)
    for k in range(5):                                             # 伞沿一段段的弧
        x0 = cx - r + k * 2 * r / 5
        d.arc([x0, cy - 2 * s, x0 + 2 * r / 5, cy + 3 * s], 0, 180, fill=col_d)
    d.line([(cx, cy - r * 0.55 - 3 * s), (cx, cy - r * 0.55)], fill=(60, 50, 60), width=max(1, s // 2))
    d.line([(cx, cy), (x, y + 18 * s)], fill=(60, 50, 60), width=max(1, s // 2))


def neon(img, d, x, y, s_, col, T, flick=0.0, seed=0):
    """竖排的霓虹招牌"""
    on = 1.0
    if flick > 0 and math.sin(T * 13 + seed * 3) + math.sin(T * 7.3 + seed) > 2 - flick * 2: on = 0.25
    w = 20; h = len(s_) * 17 + 6
    d.rectangle([x - 2, y - 2, x + w + 2, y + h + 2], fill=(26, 22, 40))
    d.rectangle([x - 1, y - 1, x + w + 1, y + h + 1], outline=lerpc((40, 30, 60), col, 0.5 * on))
    glow(img, x + w / 2, y + h / 2, max(w, h) * 0.9, col, 0.3 * on, h * 0.7)
    for i, ch in enumerate(s_):
        text(img, ch, x + w / 2, y + 11 + i * 17, col=lerpc((60, 50, 70), lerpc(col, (255, 255, 255), 0.45), on), out=None, shadow=False)


def ped_signal(d, x, base, green):
    """人行道信号灯：绿色走着的小人 / 红色站着的小人"""
    d.rectangle([x, base - 70, x + 2, base], fill=(46, 44, 56))
    d.rectangle([x - 6, base - 86, x + 8, base - 66], fill=(30, 28, 38))
    c = (90, 255, 160) if green else (255, 70, 70)
    cy = base - 76
    if green:
        d.rectangle([x, cy - 7, x + 2, cy - 5], fill=c); d.line([(x + 1, cy - 4), (x, cy + 1)], fill=c)
        d.line([(x, cy + 1), (x - 3, cy + 6)], fill=c); d.line([(x, cy + 1), (x + 3, cy + 6)], fill=c)
        d.line([(x + 1, cy - 3), (x + 4, cy)], fill=c); d.line([(x + 1, cy - 3), (x - 2, cy - 1)], fill=c)
    else:
        d.rectangle([x, cy - 7, x + 2, cy - 5], fill=c); d.rectangle([x - 1, cy - 4, x + 3, cy + 1], fill=c)
        d.line([(x, cy + 1), (x, cy + 6)], fill=c); d.line([(x + 2, cy + 1), (x + 2, cy + 6)], fill=c)


def rain_street(img, d, T, base=226, signs=True, hero_x=None):
    sky(img, RAINNIGHT, 0, base, 6)
    city(img, d, base - 26, 3, T * 2, (34, 30, 58), win=(110, 90, 140), hmin=40, hmax=110, frac=0.25, T=T)
    city(img, d, base - 8, 8, T * 4, (24, 22, 40), win=(255, 196, 120), hmin=30, hmax=80, frac=0.3, T=T, wmin=20, wmax=46)
    if signs:
        neon(img, d, 52, 100, '旅馆', (255, 90, 150), T, 0.4, 1)
        neon(img, d, 404, 86, '便利店', (90, 220, 255), T, 0.2, 2)
        neon(img, d, 330, 120, '夜', (255, 200, 90), T, 0.6, 3)
    d.rectangle([0, base, W, H], fill=(30, 30, 46))
    for k in range(9):                                              # 斑马线
        x0 = 120 + k * 26
        d.polygon([(x0, base + 2), (x0 + 14, base + 2), (x0 + 18, H), (x0 + 2, H)], fill=(78, 78, 100))
    lamp(img, d, 30, base, 1.0, 80)
    lamp(img, d, 460, base, 1.0, 80)


# ================================================================ 雨夜路口：他转身走了，又回过头
def s_crossroad(img, d, lt, dur, T, A):
    base = 226
    rain_street(img, d, T, base)
    green = lt < 1.9
    ped_signal(d, 434, base, green)
    # 她：撑红伞站在斑马线这头；最后也转身慢慢走远
    gx, gflip, gpose = 150, False, 'stand'
    if lt > 5.0:
        k = lt - 5.0
        gx, gflip, gpose = 150 - 22 * k, True, 'walk'
    person(img, 'girl', gx, base - 4, view='side', pose=gpose, ph=wph(lt, 5), expr='down', arms='umbrella', s=2, flip=gflip)
    umbrella(d, gx + (-6 if gflip else 6), base - 66, 2, tilt=-0.3 if gflip else 0.3)
    # 他：先面对着她，转身往右走开；走到一半停下，回头
    if lt < 1.4: bx, bflip, bpose, ex = 300, True, 'stand', 'sad'
    elif lt < 3.8: bx, bflip, bpose, ex = 300 + (lt - 1.4) * 42, False, 'walk', 'down'
    elif lt < 4.4: bx, bflip, bpose, ex = 300 + 2.4 * 42, False, 'stand', 'down'
    else: bx, bflip, bpose, ex = 300 + 2.4 * 42, True, 'stand', 'surprised'
    person(img, 'boy', bx, base - 4, view='side', pose=bpose, ph=wph(lt, 5), expr=ex, s=2, flip=bflip)
    if 4.4 < lt < 5.4:                                              # 回头那一下的"！"
        k = clamp((lt - 4.4) / 0.2)
        text(img, '!', bx + 2, base - 96 - 4 * eback(k), col=(255, 250, 240), alpha=k * clamp((5.4 - lt) / 0.3))
    pix.rain(d, T, 0, W, 0, base + 30, 150, (120, 130, 190), speed=300, slant=-3, ln=7)
    props.reflect(img, base + 4, H - base - 4, T, (14, 12, 40), 0.55, 1.5)
    props.splashes(d, T, base + 6, H - 4, 26, (150, 170, 230))
    vig(img, 0.4, (10, 8, 26))


# ================================================================ 心跳、裂开、心电图拉直
def ecg(d, T, y, flat_at, Tnow, col=(90, 255, 170)):
    """从右往左滚动的心电图；flat_at 之后的部分是一条直线"""
    pts = []
    speed = 120
    for x in range(0, W, 2):
        t_at = Tnow - (W - x) / speed                                # 这一点对应的时间
        v = 0.0
        if t_at < flat_at:
            k = t_at - last_beat(t_at)
            if 0 <= k < 0.25:
                v = math.sin(k / 0.25 * math.pi * 3) * (1 - k / 0.25) * 26
        pts.append((x, y - v))
    d.line(pts, fill=col)
    hx, hy = pts[-1]
    d.rectangle([hx - 1, hy - 1, hx + 1, hy + 1], fill=(220, 255, 230))


def s_heart_crack(img, d, lt, dur, T, A):
    crack0, crack1, split_at = 2.9, 3.9, 4.35
    beat = thump(T, 0.35) if lt < split_at else 0
    img.paste((14, 8, 22), (0, 0, W, H))
    glow(img, 240, 120, 200, (160, 20, 50), 0.35 + 0.25 * beat if lt < split_at else 0.2 * clamp(1 - (lt - split_at) / 1.5), 140)
    ecg(d, T, 128, T - lt + split_at, T, (90, 255, 170) if lt < split_at else (110, 140, 130))
    split = eout((lt - split_at) / 1.0) * 7 if lt > split_at else 0
    crack = clamp((lt - crack0) / (crack1 - crack0))
    drop = 14 * ease((lt - split_at - 0.6) / 1.2) if lt > split_at + 0.6 else 0
    M.heart(img, 240, 118 + drop, 3.6, beat, crack=crack if split == 0 else 0, split=split, seed=4)
    if lt > split_at:                                                 # 碎片往下掉
        for j in range(16):
            r = rng(j * 11 + 2)
            k = lt - split_at - r.random() * 0.25
            if k < 0: continue
            x = 240 + r.uniform(-10, 10) + r.uniform(-50, 50) * k
            y = 100 + r.uniform(-20, 40) + 90 * k * k
            if y < H:
                c = (226, 48, 66) if j % 3 else (255, 140, 150)
                d.rectangle([x, y, x + 1 + j % 2, y + 1 + j % 2], fill=c)
    if split_at <= lt < split_at + 0.4: shake(img, lt - split_at, 5, 0.4)
    if crack0 < lt < split_at: shake(img, (T - last_beat(T)), 1.5, 0.15)
    vig(img, 0.5, (6, 2, 10))


# ================================================================ 楼顶的纸飞机
def rooftop(img, d, t):
    T = t
    sky(img, ((0, (8, 10, 30)), (0.6, (26, 30, 70)), (1, (60, 52, 110))), 0, 200, 6)
    stars(d, T, 150, 0.8, 120)
    moon(d, 90, 50, 13)
    glow(img, 90, 50, 40, (200, 210, 255), 0.25)
    city(img, d, 210, 13, 0, (28, 30, 60), win=(120, 110, 170), hmin=30, hmax=90, frac=0.3, T=T)
    city(img, d, 214, 21, 0, (20, 20, 42), win=(255, 200, 130), hmin=20, hmax=60, frac=0.35, T=T, wmin=18, wmax=40)
    d.rectangle([0, 214, W, H], fill=(48, 46, 62))
    d.rectangle([0, 214, W, 216], fill=(80, 78, 96))
    for x in range(0, W, 16): d.rectangle([x, 196, x + 1, 214], fill=(70, 68, 86))
    d.rectangle([0, 196, W, 197], fill=(90, 88, 108))
    # 他把纸飞机扔出去
    throw = 0.8
    ph = 0 if t < throw else 1
    person(img, 'boy', 150, 214, view='side', pose='stand', arms='throw' if t < throw + 0.8 else 'down', ph=ph, expr='down' if t > 2 else 'neutral',
           s=2)
    if t < throw:
        M.plane(d, 150 - 10 + 3, 214 - 66, 1.0, -0.4)
    else:
        k = t - throw
        x, y = 166 + 160 * k, 150 - 70 * k + 14 * k * k
        ang = math.atan2(-70 + 28 * k, 160)
        M.plane(d, x, y, 1.4, ang)
        for j in range(3):
            q = (t * 2 + j / 3) % 1
            tfill(img, 'line', [(x - 20 - q * 30, y + 2 + j * 2), (x - 14 - q * 30, y + 2 + j * 2)], (230, 240, 255), (1 - q) * 0.7)
    vig(img, 0.4, (6, 6, 20))


def plane_glide(img, d, t):
    T = t
    dur = 3.6
    u = ease(t / dur)
    street = lerp(330, 228, u)                                         # 镜头跟着飞机往下降，街道从画面下方升上来
    off = 90 * t - 40 * t * t / dur
    sky(img, ((0, (8, 10, 30)), (0.6, (26, 30, 70)), (1, (60, 52, 110))), 0, H, 6)
    stars(d, T, 150, 0.6 * (1 - u), 100)
    city(img, d, street - 40, 13, off * 0.3, (28, 30, 60), win=(120, 110, 170), hmin=60, hmax=150, frac=0.3, T=T)
    city(img, d, street, 21, off * 0.7, (20, 20, 42), win=(255, 200, 130), hmin=50, hmax=130, frac=0.35, T=T, wmin=18, wmax=40)
    if street < H:
        d.rectangle([0, street, W, H], fill=(30, 30, 46))
        d.ellipse([200, street + 6, 300, street + 18], fill=(44, 46, 70))
    lamp(img, d, 330, street, 1.0, 70)
    land = 3.0
    if t < land:
        k = t / land
        x = lerp(150, 252, ease(k)); y = lerp(80, street + 9, k ** 1.6) + 5 * math.sin(t * 3) * (1 - k)
        ang = 0.15 + 0.35 * k
        M.plane(d, x, y, 1.4, ang)
    else:
        k = t - land
        x, y = 252, street + 10
        M.plane(d, x, y, 1.4, 0.05, col=(220, 222, 230), sh=(170, 176, 196))
        props.ripples(d, k, (x - 14, y - 1, x - 13, y), 1, (120, 130, 180), seed=1, per=1.0, rmax=22)
    pix.rain(d, T, 0, W, 0, H, 90, (110, 120, 180), speed=280, slant=-3, ln=6)
    vig(img, 0.4, (6, 6, 20))


def s_paper_plane(img, d, lt, dur, T, A):
    shots(img, lt, [(0, rooftop), (3.5, plane_glide)], tr=0.45)


# ================================================================ 倒转的大钟和"是否重来？"
def clock_scene(img, d, t):
    T = t
    img.paste((14, 26, 38), (0, 0, W, H))
    glow(img, 240, 112, 220, (60, 120, 130), 0.3, 160)
    for j in range(12):                                                # 背景里飘着的罗马数字
        r = rng(j * 7)
        x = (r.uniform(0, W) - t * r.uniform(4, 12)) % W
        y = r.uniform(10, 220) + 6 * math.sin(t + j)
        text(img, ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'][j], x, y, col=(50, 90, 104), out=None, shadow=False)
    stuck, crack_at = 4.6, 5.0
    if t < stuck: spin = 2 * math.pi * 0.25 * t * t
    else: spin = 2 * math.pi * 0.25 * stuck * stuck + math.sin(t * 60) * 0.06 * (t < crack_at)
    if t > crack_at + 0.15:                                             # 裂了以后指针弹回原处，照常往前走
        spin = 2 * math.pi * 0.25 * stuck * stuck * max(0, 1 - eout((t - crack_at - 0.15) / 0.35)) - (t - crack_at) * 0.3
    for gx, gy, gr, gt, gs in ((120, 70, 40, 12, 0.6), (372, 160, 52, 14, -0.45), (360, 50, 26, 9, 0.9), (96, 180, 30, 10, -0.8)):
        M.gear(d, gx, gy, gr, -spin * gs * 0.5, gt, (34, 58, 70), (24, 42, 52))
    minute = -spin; hour = 2.2 - spin / 12
    for g in range(1, 4):                                              # 倒转得太快，指针拖出残影
        if t < stuck:
            back = 2 * math.pi * 0.25 * (2 * t) * 0.05 * g
            a = minute + back
            d.line([(240, 104), (240 + math.sin(a) * 70, 104 - math.cos(a) * 70)], fill=lerpc((244, 236, 214), (170, 40, 50), 0.6 - g * 0.15),
                   width=2)
    M.big_clock(img, d, 240, 104, 86, hour, minute, T, crack=clamp((t - crack_at) / 0.6), glow_a=0.25)
    if crack_at < t < crack_at + 0.3:
        pix.dither_fade(img, 1 - (t - crack_at) / 0.3, (255, 250, 240))
    # 他在钟下面，踮着脚把钟往回推
    person(img, 'boy', 240, 238, view='back', pose='stand', arms='up', s=2)
    if crack_at < t < crack_at + 0.4: shake(img, t - crack_at, 4, 0.4)
    vig(img, 0.45, (4, 10, 16))


def big_digit(img, ch, cx, cy, scale, col):
    im = big_glyph(ch, scale, top=lerpc(col, (255, 255, 255), 0.4), bot=col, line=lerpc(col, (0, 0, 0), 0.5), out=(10, 8, 16))
    dpaste(img, im, cx - im.width / 2, cy - im.height / 2)


def continue_screen(img, d, t):
    T = t
    img.paste((6, 6, 14), (0, 0, W, H))
    d.rectangle([14, 10, W - 15, H - 34], outline=(80, 80, 120))
    d.rectangle([18, 14, W - 19, H - 38], outline=(50, 50, 80))
    big_text(img, '是否重来？', W / 2, 40, 2, top=(255, 250, 240), bot=(200, 200, 230), line=(80, 80, 120), out=(10, 8, 16))
    count0 = 0.3
    n = int((t - count0) / 0.82) if t > count0 else 0
    num = 5 - n
    if num >= 0:
        k = ((t - count0) / 0.82) % 1 if t > count0 else 0
        col = (255, 220, 120) if num > 1 else (255, 90, 90)
        big_digit(img, str(num), W / 2, 104 + 4 * (1 - eout(k / 0.2)), 5, col)
    else:
        k = t - count0 - 6 * 0.82
        jit = int(3 * math.sin(T * 50)) if k < 0.4 else 0
        big_text(img, '无法重来', W / 2 + jit, 104, 3, top=(255, 160, 160), bot=(220, 40, 60), line=(110, 10, 30), out=(10, 8, 16))
    # 选项："是"被锁住了，光标按下去只会抖一下
    blink = int(T * 3) % 2
    opts_y = 160
    text(img, '是', W / 2 - 50, opts_y, col=(110, 110, 130))
    d.line([(W / 2 - 58, opts_y - 8), (W / 2 - 42, opts_y + 8)], fill=(255, 80, 90), width=2)
    d.line([(W / 2 - 58, opts_y + 8), (W / 2 - 42, opts_y - 8)], fill=(255, 80, 90), width=2)
    text(img, '否', W / 2 + 50, opts_y, col=(240, 240, 255))
    press = [x for x in (1.2, 2.8, 4.0) if x < t]
    jx = 0
    if press and t - press[-1] < 0.3: jx = int(4 * math.sin((t - press[-1]) * 60))
    if blink or (press and t - press[-1] < 0.3):
        d.polygon([(W / 2 - 74 + jx, opts_y - 5), (W / 2 - 74 + jx, opts_y + 5), (W / 2 - 68 + jx, opts_y)], fill=(255, 250, 240))
    # 剩余生命：一颗空心
    d.polygon(pix.heart_poly(40, 30, 0.45), outline=(255, 90, 100))
    text(img, '× 0', 64, 30, col=(255, 200, 200), font=FONT_S)
    # 角落里坐着的小人
    person(img, 'boy', W / 2, 214, view='front', pose='sit', expr='sad', s=1)
    # 最后读取回忆
    if t > 5.7:
        k = clamp((t - 5.9) / 0.65)
        text(img, '读取回忆……', W / 2, 196 - 10, col=(200, 220, 255), font=FONT_S)
        d.rectangle([W / 2 - 60, 196, W / 2 + 60, 202], outline=(140, 160, 210))
        d.rectangle([W / 2 - 58, 198, W / 2 - 58 + 116 * k, 200], fill=(255, 210, 120))
    a = np.asarray(img).copy(); a[::3] = (a[::3] * 0.72).astype(np.uint8)       # 老显示器的扫描线
    img.paste(Image.fromarray(a))
    vig(img, 0.45, (0, 0, 0))


def s_rewind(img, d, lt, dur, T, A):
    shots(img, lt, [(0, clock_scene), (7.3, continue_screen)], tr=0.3)
