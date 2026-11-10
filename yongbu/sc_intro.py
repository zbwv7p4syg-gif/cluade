"""永不失联的爱 · 片头和前奏（0 – 38.2 秒）。

0.6 秒起，雨夜旧楼上方的片名像灯丝一样逐字亮起，旁边的信号格在找信号；镜头下摇推近那一格亮着的窗，
窗帘上两个人的影子靠在一起，灯一闪灭掉。12.9 秒音乐起来，片名在整座夜城上空炸开，信号格一格格满上，
城里的窗从那一格往外一圈圈亮起来。车灯扫过，进入退租的最后一晚。
"""
import math
import numpy as np
from PIL import Image, ImageDraw

import pix
from pix import W, H, FONT, FONT_S, clamp, lerp, lerpc, ease, eout, ein, span, glow, blend_box, rng
import props
import world as Wd
from world import FLOOR_Y

TITLE = '永不失联的爱'
TITLE_FULL = '《永不失联的爱》'
GLY = dict(top=(255, 246, 214), bot=(255, 178, 92), line=(206, 90, 60), out=(40, 20, 30))


def title_glyphs(scale):
    return [props.big_glyph(c, scale, **GLY) for c in TITLE_FULL]


def draw_title(img, cx, cy, scale, t_on, T, flick=True, drop=0.0, alpha=1.0, glow_a=0.35, burst=None):
    """片名：t_on 是每个字亮起来的时间（相对本函数的 T）。flick=True 时先像灯丝一样闪几下"""
    gl = title_glyphs(scale)
    adv = [FONT.getlength(c) * scale for c in TITLE_FULL]
    x = cx - sum(adv) / 2 - 4 * scale
    if glow_a > 0:
        n_on = sum(1 for k in t_on if T >= k)
        if n_on: glow(img, cx, cy, sum(adv) * 0.62, (255, 170, 90), glow_a * n_on / len(t_on) * alpha, ry=60 * scale / 3)
    for i, (g, a) in enumerate(zip(gl, adv)):
        k = T - t_on[i]
        if k < 0: x += a; continue
        on = 1.0
        if flick and k < 0.36:
            on = 1.0 if int(k * 28 + i * 3) % 3 != 1 else 0.25
        dy = 0
        if drop > 0 and k < 0.3: dy = -drop * (1 - eout(k / 0.3))
        props.dpaste(img, g, x, cy - g.height / 2 + dy, alpha * on)
        if burst and k < 0.5:
            d = ImageDraw.Draw(img)
            r_ = rng(i * 11)
            for j in range(10):
                ang = r_.uniform(0, 6.28); sp = r_.uniform(20, 60)
                px = x + a / 2 + math.cos(ang) * sp * k * 2; py = cy + math.sin(ang) * sp * k * 2
                d.rectangle([px, py, px + 1, py + 1], fill=lerpc((255, 250, 210), (255, 150, 80), k * 2))
        x += a
    return sum(adv)


def tall_building(t, tone=0.0, lit=1.0, others=None, extra=130):
    """在楼的上方多出 extra 像素的夜空，好做下摇"""
    b = Image.new('RGB', (W, H)); bd = ImageDraw.Draw(b)
    Wd.building(b, bd, t, tone, lit, others)
    tall = Image.new('RGB', (W, H + extra))
    top = lerpc((10, 14, 30), (150, 172, 206), tone)
    pix_sky = pix.vgrad(W, extra, ((0, (4, 6, 16)), (1, top)), 5)
    tall.paste(pix_sky, (0, 0))
    td = ImageDraw.Draw(tall)
    pix.stars(td, t, extra, 0.8, n=80)
    pix.rain(td, t, 0, W, 0, extra, 40, (90, 110, 160), speed=240, slant=-4, ln=6, seed=8)
    tall.paste(b, (0, extra))
    return tall


# ---------------------------------------------------------------- 片头
def s_title(img, d, lt, dur, T, a):
    t = lt
    if t < 9.0:
        # A：雨夜旧楼，片名在上空逐字亮起
        extra = 130
        tall = tall_building(t, 0.0, 0.85 + 0.15 * math.sin(t * 3) if t < 6 else 1.0)
        td = ImageDraw.Draw(tall); td.fontmode = '1'
        on = [0.6 + 0.3 * i for i in range(len(TITLE_FULL))]
        draw_title(tall, W / 2, 62, 3, on, t, glow_a=0.4)
        # 信号格：在找信号
        bars = int(t * 3) % 5 if t < 3.6 else 4
        if t > 3.0:
            Wd.signal_icon(td, W / 2 - 16, 112, bars, 2, col=(255, 226, 150))
            pix.text(tall, '· 正在连接 ·' if t < 3.6 else '· 已连接 ·', W / 2 + 30, 106, col=(240, 220, 190), font=FONT_S, shadow=False,
                     alpha=clamp((t - 3.0) / 0.5))
        # 下摇：6.3 秒以后镜头往下摇，推向那一格窗
        f = ease(span(t, 5.6, 9.0))
        oy = lerp(0, extra, f)
        view = tall.crop((0, int(oy), W, int(oy) + H))
        z = lerp(1.0, 2.2, ein(span(t, 6.6, 9.0)))
        wx, wy = Wd.our_window()
        if z > 1.001:
            cx, cy = lerp(W / 2, wx + Wd.WIN_W / 2, f), lerp(H / 2, wy + Wd.WIN_H / 2 + extra - oy, f)
            w_, h_ = W / z, H / z
            x0 = clamp(cx - w_ / 2, 0, W - w_); y0 = clamp(cy - h_ / 2, 0, H - h_)
            view = view.crop((int(x0), int(y0), int(x0 + w_), int(y0 + h_))).resize((W, H), Image.NEAREST)
        img.paste(view)
        if t < 0.6: pix.dither_fade(img, 1 - t / 0.6)
        if t > 8.6: pix.dither_fade(img, (t - 8.6) / 0.4, (24, 16, 20))
    elif t < 12.9:
        # B：窗的特写，窗帘上两个人的影子靠在一起，然后灯灭
        k = t - 9.0
        win_close(img, d, k, t)
    else:
        title_burst(img, d, t - 12.9, t)


def win_close(img, d, k, t):
    """从窗外看那一格窗：暖色窗帘上两个人影慢慢靠到一起；灯闪一下熄灭"""
    wall = (40, 44, 62)
    img.paste(wall, (0, 0, W, H))
    for y in range(4, H, 9): d.line([(0, y), (W, y)], fill=(34, 38, 54))
    x0, y0, x1, y1 = 120, 26, 360, 236
    lit = 1.0
    if k > 2.7: lit = [1, 0.2, 1, 0.1, 0.6, 0][min(5, int((k - 2.7) * 14))]
    if k > 3.15: lit = 0.0
    cur = lerpc((50, 40, 50), (246, 196, 128), lit)
    d.rectangle([x0 - 8, y0 - 8, x1 + 8, y1 + 8], fill=(26, 28, 40))
    d.rectangle([x0, y0, x1, y1], fill=cur)
    for x in range(x0, x1, 10): d.line([(x, y0), (x, y1)], fill=lerpc(cur, (150, 90, 60), 0.25))
    if lit > 0:
        glow(img, (x0 + x1) / 2, (y0 + y1) / 2, 200, (255, 180, 100), 0.35 * lit)
    # 两个人影：坐着，肩膀慢慢碰到一起
    if lit > 0.05:
        lean = ease(span(k, 0.6, 2.2))
        sh = lerpc(cur, (60, 30, 30), 0.75)
        props.person_s(img, 'boy', 210 + 6 * lean, 228, 4, age='past', view='side', pose='sit', tint=sh)
        props.person_s(img, 'girl', 280 - 8 * lean, 228, 4, age='past', view='side', pose='sit', tint=sh, flip=True)
        if lean > 0.95:
            Wd.heart(d, 246, 92 - 4 * math.sin(k * 3), 0.5, lerpc(cur, (255, 236, 200), 0.6))
    # 窗框十字
    fc = (36, 38, 54)
    d.rectangle([(x0 + x1) // 2 - 3, y0, (x0 + x1) // 2 + 3, y1], fill=fc)
    d.rectangle([x0, (y0 + y1) // 2 - 3, x1, (y0 + y1) // 2 + 3], fill=fc)
    d.rectangle([x0 - 14, y1 + 8, x1 + 14, y1 + 16], fill=(70, 74, 92))
    # 玻璃上的雨
    props.drops_on_glass(img, d, t, (x0, y0, x1, y1), 50, 3, col=lerpc((150, 170, 210), (255, 236, 200), lit * 0.6))
    pix.rain(d, t, 0, W, 0, H, 90, (90, 110, 160), speed=260, slant=-4, ln=7, seed=2)
    if k < 0.4: pix.dither_fade(img, 1 - k / 0.4, (24, 16, 20))
    if k > 3.2: pix.dither_fade(img, clamp((k - 3.2) / 0.5) * 0.92, (6, 8, 16))


CITY_WINS = None


def title_burst(img, d, k, t):
    """音乐起来：整座夜城，片名炸开，信号格满上，窗户从那一格往外一圈圈亮起来"""
    # 天空和远城
    props_sky = ((0, (6, 8, 24)), (0.55, (24, 26, 64)), (1, (70, 50, 96)))
    pix.sky(img, props_sky)
    pix.stars(d, t, 200, 1.0, n=180)
    props.bokeh(img, t, 10, a=0.18, box=(0, 0, W, 160))
    wave = k * 160                    # 一圈圈亮起来的半径
    ox, oy = 240, 190
    # 三层城市，越近越大
    for layer, (base, seed, col, hmin, hmax, wmin, wmax) in enumerate([(205, 31, (24, 26, 52), 40, 110, 12, 26),
                                                                       (232, 17, (18, 18, 40), 30, 90, 18, 34),
                                                                       (262, 5, (12, 12, 28), 20, 60, 24, 44)]):
        off = t * (2 + layer * 3)
        lay, total = pix.skyline(seed, W, hmin, hmax, wmin, wmax)
        for bx, bw, bh, roof, ws in lay:
            x = int((bx - off) % total) - 10
            if x > W + 10: x -= total
            if x + bw < -2 or x > W + 2: continue
            top = base - bh
            d.rectangle([x, top, x + bw - 1, base], fill=col)
            rr = rng(ws)
            for wy in range(top + 4, base - 3, 6):
                for wx in range(x + 2, x + bw - 2, 5):
                    if rr.random() < 0.5:
                        dist = math.hypot(wx - ox, (wy - oy) * 1.6)
                        if dist < wave:
                            c = (255, 206, 120) if rr.random() < 0.8 else (170, 210, 255)
                            fresh = clamp(1 - (wave - dist) / 30)
                            d.rectangle([wx, wy, wx + 1 + (layer == 2), wy + 1 + (layer == 2)], fill=lerpc(c, (255, 255, 240), fresh))
    # 中间那栋旧楼的那一格窗
    d.rectangle([228, 150, 252, 262], fill=(16, 16, 34))
    d.rectangle([234, 176, 246, 188], fill=(255, 200, 110))
    glow(img, 240, 182, 40 + 8 * math.sin(k * 4), (255, 190, 110), 0.5)
    # 冲击波的一圈光
    if wave < 600:
        r = wave
        for a_ in range(0, 360, 3):
            px = ox + math.cos(math.radians(a_)) * r; py = oy + math.sin(math.radians(a_)) * r / 1.6
            if 0 <= px < W and 0 <= py < H and (a_ // 3) % 2 == 0:
                d.point((px, py), fill=lerpc((255, 230, 170), (40, 30, 60), clamp(k / 3)))
    # 片名
    on = [0.0 + 0.09 * i for i in range(len(TITLE_FULL))]
    width = draw_title(img, W / 2, 74 - 2 * math.sin(t * 1.6), 3, on, k, flick=False, drop=30, glow_a=0.55, burst=True)
    # 信号格一格格满上，旁边一颗跳动的心
    bars = min(4, int(k / 0.45) + 1)
    sy = 122
    Wd.signal_icon(d, W / 2 - 34, sy, bars, 2, col=(255, 230, 160), dim=(70, 60, 90))
    hb = 1 + 0.25 * max(0, math.sin(k * 6.5)) ** 8
    Wd.heart(d, W / 2 + 22, sy - 7, 0.42 * hb, (255, 110, 120), out=(60, 20, 40))
    if k > 1.6:
        pix.text(img, '灯 一 直 亮 着  ·  爱 从 未 断 线', W / 2, 146, col=(250, 230, 200), font=FONT_S, shadow=False,
                 alpha=clamp((k - 1.6) / 0.6), out=(30, 20, 40))
    # 闪白
    if k < 0.25: pix.dither_fade(img, 1 - k / 0.25, (255, 246, 226))
    # 收尾：片名化作光点往上飘，车灯扫过
    if k > 4.6:
        f = clamp((k - 4.6) / 0.9)
        pix.dither_fade(img, f * 0.9, (16, 18, 34))
        r_ = rng(5)
        for j in range(80):
            px = r_.uniform(W / 2 - width / 2, W / 2 + width / 2); py = 74 + r_.uniform(-20, 20) - f * r_.uniform(40, 120)
            if r_.random() < 1 - f * 0.6: d.point((px, py), fill=(255, 220, 160))


s_title.no_sub = True


# ---------------------------------------------------------------- 前奏
NOW_ROOM = dict(box_under=False, keys=1, cups=[('amber', Wd.CUPS[0]), ('blue', Wd.CUPS[1] + 22)])


def car_sweep(img, x, w=60, a=0.55, slant=0.5):
    """车灯从墙上扫过的一道亮带（点阵分档）"""
    yy, xx = np.mgrid[0:H, 0:W]
    c = x + (yy - H / 2) * slant
    v = np.clip(1 - np.abs(xx - c) / w, 0, 1)
    blend_box(img, (0, 0, W, H), (230, 230, 210), a * v ** 1.2)


def s_01(img, d, lt, dur, T, a):
    """空房里的两道影子：车灯扫过，暖色一拍里两个人的影子靠在一起；车灯移开，冷墙上只剩他拎着纸箱的影子，他走进来"""
    k = lt
    sweep = lerp(-120, 620, span(k, 0.0, 1.6))
    warm = 0.25 < k < 0.95
    st = dict(NOW_ROOM, door=1.0 if k > 1.0 else 0.0, hall=(120, 110, 80))
    if warm:
        st = dict(past=True, bed=False, marks=False, keys=1, cups=[('amber', Wd.CUPS[0]), ('blue', Wd.CUPS[1])])

    def actors(im, dd, ox):
        if warm:   # 墙上两道人影碰肩
            sh = (150, 104, 80)
            props.person_s(im, 'boy', 230 + ox, FLOOR_Y + 2, 2, age='past', view='side', pose='sitfloor', tint=sh)
            props.person_s(im, 'girl', 262 + ox, FLOOR_Y + 2, 2, age='past', view='side', pose='sitfloor', tint=sh, flip=True)
        elif k > 1.0:
            x = lerp(80, 170, ease(span(k, 1.0, dur)))
            ph = pix.wph(k, 8) if k < dur - 0.2 else 0
            pix.person(im, 'boy', x + ox, FLOOR_Y + 6, age='now', view='side', pose='walk', ph=ph, arms='carry', s=2, expr='down')
            Wd.box(dd, int(x + ox + 8), FLOOR_Y - 40, int(x + ox + 34), FLOOR_Y - 18, label=False)
            # 墙上的影子
            props.ghost(im, 'boy', x + ox + 30, FLOOR_Y - 2, 2, 0.35, age='now', pose='walk', ph=ph, arms='carry', tint=(30, 34, 54))
    Wd.room(img, T, st, cam=60, amb='past' if warm else 'dark', actors=actors)
    if not warm: car_sweep(img, sweep, 70, 0.5)
    else: car_sweep(img, sweep, 70, 0.3)
    pix.vig(img, 0.4)


def s_02(img, d, lt, dur, T, a):
    """最后一只纸箱：他蹲下把箱子放到窗边桌下；镜头从纸箱沿地板移到桌脚，红台灯和两只杯子还在桌上"""
    k = lt
    put = span(k, 0.4, 1.4)
    st = dict(NOW_ROOM, box_under=put >= 1)

    def actors(im, dd, ox):
        pose = 'crouch' if 0.3 < k < 1.8 else 'stand'
        pix.person(im, 'boy', 360 + ox, FLOOR_Y + 6, age='now', view='side', pose=pose, arms='low' if pose == 'crouch' else 'auto', s=2,
                   expr='down')
        if put < 1:
            bx = int(lerp(380, 398, put)) + ox
            Wd.box(dd, bx, int(lerp(FLOOR_Y - 34, 168, put)), bx + 42, int(lerp(FLOOR_Y - 34, 168, put)) + 28)
    cam = lerp(40, 80, ease(k / dur))
    Wd.room(img, T, st, cam=cam, amb='now', actors=actors)
    pix.vig(img, 0.4)


def s_03(img, d, lt, dur, T, a):
    """一把已经交回的钥匙：门边铁碟的特写，他的手把挂蓝线的钥匙转正，蓝线晃一下停住"""
    k = lt
    pix.sky(img, ((0, (40, 44, 64)), (1, (26, 30, 46))))
    # 矮台台面
    d.rectangle([0, 170, W, H], fill=(62, 46, 44))
    d.rectangle([0, 166, W, 172], fill=(84, 62, 54))
    for y in range(180, H, 12): d.line([(0, y), (W, y)], fill=(54, 40, 40))
    # 门框
    d.rectangle([0, 0, 70, 170], fill=(120, 104, 96)); d.rectangle([60, 0, 70, 170], fill=(150, 136, 126))
    turn = ease(span(k, 0.9, 1.5))
    swing = (k - 1.5) * 9 if k > 1.5 else 0
    sw_amp = math.exp(-max(0, k - 1.5) * 2.2) if k > 1.5 else 0
    s = 4
    cx, cy = 250, 186
    rw, rh = 15 * s, 4 * s
    d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh + s], fill=(56, 58, 68))
    d.ellipse([cx - rw + s, cy - rh + s, cx + rw - s, cy + rh - s], fill=(96, 98, 110))
    d.ellipse([cx - rw + 3 * s, cy - rh + 2 * s, cx + rw - 3 * s, cy + rh - 2 * s], fill=(84, 86, 98))
    Wd.key(d, cx - 6 * s, cy, 'hers', s // 2 + 1, lerp(0.9, 0.0, turn), swing * sw_amp)
    # 手指伸进来转钥匙
    hx = lerp(560, 330, eout(span(k, 0.3, 0.9))) if k < 1.8 else lerp(330, 560, ein(span(k, 1.8, 2.6)))
    Wd.hand(img, hx, cy - 22, 4, 'point', flip=True, sleeve=(36, 58, 96))
    Wd.light(img, (0.62, 0.68, 0.9))
    pix.vig(img, 0.5)


def s_04(img, d, lt, dur, T, a):
    """墙上的一小格：手电光照到高处的拍立得，纸胶带翘起一角，他把它按平，照片里只露出半张笑脸"""
    k = lt
    wall = (150, 140, 128)
    img.paste(wall, (0, 0, W, H))
    for x in range(10, W, 46): d.line([(x, 0), (x, H)], fill=(140, 130, 118))
    z = lerp(1.0, 1.12, k / dur)
    cx, cy = 240, 130
    pw, ph = 96, 112
    x0, y0 = cx - pw // 2, cy - ph // 2
    d.rectangle([x0 - 2, y0 - 2, x0 + pw + 2, y0 + ph + 2], fill=(40, 36, 44))
    d.rectangle([x0, y0, x0 + pw, y0 + ph], fill=(244, 238, 222))
    big = Wd.photo_big(0)
    crop = big.crop((40, 20, 112, 88)).resize((pw - 12, ph - 30), Image.NEAREST)
    img.paste(crop, (x0 + 6, y0 + 6))
    # 照片下沿被墙影盖住，只露半张脸
    d.rectangle([x0 + 6, y0 + 6, x0 + 30, y0 + ph - 24], fill=(196, 170, 140))
    lift = 1 - ease(span(k, 1.0, 1.6))
    tx0, ty0 = cx - 16, y0 - 8
    d.polygon([(tx0, ty0), (tx0 + 32, ty0), (tx0 + 32, ty0 + 12 - 6 * lift), (tx0, ty0 + 12)], fill=(236, 224, 170))
    if lift > 0.05: d.polygon([(tx0 + 20, ty0 + 12 - 6 * lift), (tx0 + 32, ty0 + 12 - 6 * lift), (tx0 + 32, ty0 + 2 - 8 * lift)], fill=(206, 194, 140))
    hx = lerp(560, cx + 40, eout(span(k, 0.5, 1.0))) if k < 1.9 else lerp(cx + 40, 560, ein(span(k, 1.9, 2.6)))
    Wd.hand(img, hx, ty0 + 6, 4, 'flat', flip=True, sleeve=(36, 58, 96))
    # 手电光圈
    fx = lerp(140, cx, ease(span(k, 0, 0.8))); fy = lerp(200, cy - 6, ease(span(k, 0, 0.8)))
    Wd.light(img, 'dark', [(fx, fy, 110, 100, 1.4, (1.0, 0.98, 0.9))])
    props.zoom(img, 1) if z < 1 else None
    pix.vig(img, 0.55)


def s_05(img, d, lt, dur, T, a):
    """两只杯子：俯拍桌面，他把蓝杯挪到琥珀杯旁，把两只杯柄转成同一个方向"""
    k = lt
    desk(img, d)
    s = 4
    move = ease(span(k, 0.3, 1.2))
    turn = span(k, 1.4, 1.9)
    bx = lerp(330, 270, move)
    cup_top(d, 200, 140, 'amber', s, 0.0)
    cup_top(d, bx, 140, 'blue', s, lerp(math.pi * 0.8, 0.0, ease(turn)))
    # 手
    hx = bx + 50 if k < 2.1 else lerp(bx + 50, 600, ein(span(k, 2.1, 2.6)))
    hx = lerp(600, bx + 50, eout(span(k, 0, 0.3))) if k < 0.3 else hx
    Wd.hand(img, hx, 150, 4, 'pinch', flip=True, sleeve=(36, 58, 96))
    # 桌角的灯线伸向窗边
    d.line([(W, 230), (400, 236), (300, 262), (290, H)], fill=(24, 24, 28), width=3)
    Wd.light(img, 'now')
    pix.vig(img, 0.5)


def desk(img, d, col=Wd.DESK):
    img.paste(col, (0, 0, W, H))
    r_ = rng(2)
    for y in range(0, H, 22):
        d.line([(0, y), (W, y)], fill=lerpc(col, (0, 0, 0), 0.18))
        for _ in range(3):
            x = r_.randint(0, W); d.line([(x, y + 6), (x + r_.randint(20, 60), y + 6)], fill=lerpc(col, (255, 255, 255), 0.08))


def cup_top(d, x, y, kind, s=4, ang=0.0, steam=0.0, t=0.0, water=False):
    """俯视的杯子：一个圆环加一个杯柄；ang 是杯柄的方向（0 朝右）"""
    c, cd, cl = (Wd.CUPB, Wd.CUPB_D, Wd.CUPB_L) if kind == 'blue' else (Wd.CUPA, Wd.CUPA_D, Wd.CUPA_L)
    r = 6 * s
    hx, hy = x + math.cos(ang) * (r + 3 * s), y + math.sin(ang) * (r + 3 * s)
    d.ellipse([hx - 3 * s, hy - 3 * s, hx + 3 * s, hy + 3 * s], fill=cd)
    d.ellipse([hx - s, hy - s, hx + s, hy + s], fill=lerpc(cd, (0, 0, 0), 0.4))
    d.ellipse([x - r - s, y - r + s, x + r + s, y + r + 2 * s], fill=lerpc(cd, (0, 0, 0), 0.4))
    d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    d.ellipse([x - r + 2 * s, y - r + 2 * s, x + r - 2 * s, y + r - 2 * s], fill=(120, 150, 170) if water else lerpc(cd, (0, 0, 0), 0.3))
    if water: d.ellipse([x - r + 3 * s, y - r + 3 * s, x - r + 5 * s, y - r + 5 * s], fill=(220, 236, 250))
    d.arc([x - r, y - r, x + r, y + r], 200, 260, fill=cl, width=s)
    if kind == 'blue':
        d.rectangle([x - 2 * s, y - r, x + s, y - r + s], fill=(30, 26, 30))


def s_06(img, d, lt, dur, T, a):
    """摸到灯线：窗玻璃上雨珠往下淌，他顺着灯线摸到黑色线控开关，拇指停在拨片上，楼下车光从他脸上过去"""
    k = lt
    # 玻璃和窗外
    Wd.outside_night(img, d, (0, 0, W, H), T, 1.0, seed=4)
    props.drops_on_glass(img, d, T, (0, 0, W, H), 120, 5)
    # 玻璃上他的倒影：侧脸（半透明）
    f = props.face('boy', 'down', 4)
    props.dpaste(img, f, 320, 40, 0.18)
    # 近景：灯线和开关、手
    d.line([(0, 200), (120, 196), (200, 206), (W, 220)], fill=(20, 20, 24), width=4)
    sx = 260
    d.rounded_rectangle([sx - 28, 194, sx + 28, 222], 6, fill=(24, 24, 28))
    d.rectangle([sx - 8, 198, sx + 8, 204], fill=(60, 60, 66))
    hx = lerp(-60, sx - 30, eout(span(k, 0.2, 1.4)))
    Wd.hand(img, hx, 212, 4, 'grip', sleeve=(36, 58, 96))
    sweep = lerp(-200, 700, span(k, 1.2, 2.1))
    Wd.light(img, (0.5, 0.56, 0.78))
    car_sweep(img, sweep, 50, 0.4, 0.2)
    pix.vig(img, 0.5)


SW = (170, 206)       # 开关特写里开关的中心
LAMP_CU = (392, 262)  # 开关特写里台灯底座


def switch_shot(img, d, t, on=0.0, thumb=0.0, sleeve=(36, 58, 96), wipe=0.0, amb='now', bulb_state='old', extra=None, dust=1.0,
                outside_tone=0.0):
    """开关特写（两次开灯、换完灯泡、最后关灯都用这个机位）：左边是线控开关和手，右上是大大的红灯罩"""
    pix.sky(img, ((0, (66, 72, 96)), (1, (46, 50, 70))))
    for x in range(0, 250, 40): d.line([(x, 0), (x, 228)], fill=(60, 66, 88))
    # 窗在背景右上
    d.rectangle([250, 0, 260, 150], fill=(150, 146, 140)); d.rectangle([250, 70, W, 78], fill=(150, 146, 140))
    d.rectangle([250, 150, W, 158], fill=(170, 166, 160))
    Wd.outside_night(img, d, (260, 0, W, 70), t, 1.0 - outside_tone, seed=6, tone=outside_tone)
    Wd.outside_night(img, d, (260, 78, W, 150), t, 1.0 - outside_tone, seed=7, tone=outside_tone)
    # 桌面
    d.rectangle([0, 230, W, H], fill=Wd.DESK)
    d.rectangle([0, 226, W, 232], fill=Wd.DESK_L)
    lx, ly = LAMP_CU
    tip = Wd.lamp_obj(d, lx, ly, 5, on, -1, cable=False)
    if dust > 0:
        for i in range(14):
            r_ = rng(i)
            px = r_.uniform(300, 360); py = r_.uniform(96, 130)
            if px - 300 > wipe * 70: d.point((px, py), fill=(206, 186, 176))
    # 灯线到开关
    d.line([(lx - 36, ly - 6), (300, ly - 14), (SW[0] + 34, SW[1])], fill=(20, 20, 24), width=4)
    d.line([(SW[0] - 34, SW[1]), (40, 214), (0, 212)], fill=(20, 20, 24), width=4)
    sx, sy = SW
    d.rounded_rectangle([sx - 34, sy - 15, sx + 34, sy + 15], 7, fill=(20, 20, 24))
    d.rounded_rectangle([sx - 32, sy - 14, sx + 32, sy - 10], 4, fill=(50, 50, 58))
    slider = lerp(-9, 9, on if thumb >= 1 else 0)
    d.rectangle([sx - 11 + slider, sy - 7, sx + 3 + slider, sy + 2], fill=(76, 76, 84))
    d.rectangle([sx - 11 + slider, sy - 7, sx + 3 + slider, sy - 6], fill=(110, 110, 120))
    if extra: extra(img, d)
    Wd.hand(img, sx - 30, sy + 8 + (2 if thumb >= 1 else 0), 4, 'press' if thumb >= 1 else 'grip', sleeve=sleeve)
    lights = []
    if on > 0:
        lights = [(tip[0], tip[1], 320, 240, 1.1 * on, Wd.WARM), (tip[0], tip[1], 100, 80, 0.8 * on, Wd.WARM)]
    Wd.light(img, amb, lights, [((int(tip[0]), int(tip[1]), 8, int(tip[0]) - 80, 140, H, 4), 0.6 * on, Wd.WARM)] if on > 0 else [])
    if on > 0:
        glow(img, tip[0], tip[1], 70, (255, 220, 150), 0.6 * on)
        d.ellipse([tip[0] - 12, tip[1] - 8, tip[0] + 12, tip[1] + 6], fill=lerpc((120, 90, 60), (255, 252, 230), on))
    pix.vig(img, 0.45)
    return tip


def s_07(img, d, lt, dur, T, a):
    """还像从前那样：他把台灯转向窗边，用袖口擦掉灯罩边的一圈灰，右手重新握住开关，停住"""
    k = lt
    wipe = ease(span(k, 0.3, 1.3))
    switch_shot(img, d, T, 0.0, 0.0, wipe=wipe, extra=lambda im, dd: Wd.hand(im, lerp(290, 370, wipe), 116, 4, 'flat', sleeve=(36, 58, 96))
                if k < 1.5 else None)
