"""永不失联的爱 · 第二段副歌、尾声和片尾。签名都是 (img, d, lt, dur, T, A)。

她打来电话；海边的灯塔射出心形的光，越过海面照到对岸的她；聊天气泡按拍子一条条跳出来，背后是心电图；
花田里两人跑向对方抱在一起；她站在转动的地球顶上，满天烟花；他的特写；一颗小星球上，一根线绕过星球连着两个人；
一架带着心的纸飞机越过千山；山顶的银河下他把一颗发光的心交给她，满天流星连成一颗心。
尾声两人并肩坐在月亮上；天亮了，两人牵着手走在楼顶上；片尾星星再拼出片名，信号满格。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
import kit
import sig
import motifs as M
import sc_a
import sc_b
from props import shots, shake, dpaste, mix_stops, thump
from pix import (W, H, FONT, FONT_S, OUT, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky, stars,
                 person, wph, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, BAYER)
from kit import NIGHT, DEEP, DUSK, DAY, GOLDEN, RAINY, DAWN

YY, XX = np.mgrid[0:H, 0:W]


def s_call(img, d, lt, dur, T, A):
    """你给我：她打来了电话，手机嗡嗡震，绿色的接听键一闪一闪，然后接通"""
    img.paste((14, 10, 30), (0, 0, W, H))
    sc_b.rays(img, 240, 135, T, (40, 30, 70), 0.6)
    acc = lt > 1.15
    dx = round(2 * math.sin(lt * 70)) if not acc else 0
    box = sig.phone(img, d, 172 + dx, 18, 136, 234, scr=(40, 70, 60) if acc else (30, 30, 70))
    sx0, sy0, sx1, sy1 = box
    cx = (sx0 + sx1) / 2
    sig.bars(d, sx1 - 14, sy0 + 9, 4, 1, on=(230, 236, 255))
    d.ellipse([cx - 24, sy0 + 36, cx + 24, sy0 + 84], fill=(190, 226, 255))
    sig.heart_at(img, cx, sy0 + 60, 3)
    sig.pix_text(d, '她', cx - 8, sy0 + 92, (255, 255, 255), 16)
    sig.pix_text(d, '通话中 00:01' if acc else '来电…', cx - (34 if acc else 16), sy0 + 114, (200, 255, 210) if acc else (200, 210, 240))
    if not acc:
        k = thump(T, 0.3)
        r = 14 + 3 * k
        glow(img, cx + 34, sy1 - 30, 26, (90, 230, 120), 0.5)
        d.ellipse([cx + 34 - r, sy1 - 30 - r, cx + 34 + r, sy1 - 30 + r], fill=(70, 210, 100))
        d.ellipse([cx - 34 - 14, sy1 - 44, cx - 34 + 14, sy1 - 16], fill=(230, 70, 80))
        for j in range(3):
            u = (lt * 2 + j / 3) % 1
            d.arc([172 - 10 - u * 30, 60, 172 + 10 + u * 30, 200], 120, 240, fill=lerpc((200, 220, 255), (14, 10, 30), u))
            d.arc([308 - 10 - u * 30, 60, 308 + 10 + u * 30, 200], 300, 420, fill=lerpc((200, 220, 255), (14, 10, 30), u))
    else:
        f = span(lt, 1.15, 1.5)
        for j in range(12):
            a = j * math.pi / 6
            rr = 40 + f * 140
            sig.heart_at(img, cx + math.cos(a) * rr, 130 + math.sin(a) * rr * 0.8, 1, alpha=1 - f * 0.5)


def heart_beam(img, d, x, y, ang, L, a, T):
    """从 (x, y) 往 ang 方向打出去的一束光，光里漂着小心"""
    ca, sa = math.cos(ang), math.sin(ang)
    w0, w1 = 4, 40
    poly = [(x - sa * w0, y + ca * w0), (x + ca * L - sa * w1, y + sa * L + ca * w1), (x + ca * L + sa * w1, y + sa * L - ca * w1),
            (x + sa * w0, y - ca * w0)]
    tfill(img, 'polygon', poly, (255, 210, 220), 0.22 * a)
    for k in range(5):
        u = (T * 0.5 + k / 5) % 1
        sig.heart_at(img, x + ca * L * u, y + sa * L * u + 6 * math.sin(T * 3 + k), 1, alpha=a)


def s_tower(img, d, lt, dur, T, A):
    """这一辈子都不想失联的爱：海边的灯塔，他站在下面，灯塔射出一束心形的光越过夜海，照到对岸挥手的她"""
    hz = 170
    kit.night(img, d, T, NIGHT, 200)
    kit.galaxy(img, 0.5, 6, -0.15, 34)
    d.rectangle([0, hz, W, H], fill=(14, 20, 56))
    for k in range(50):
        r = rng(k)
        x = (r.uniform(0, W) + T * 6 * r.uniform(-1, 1)) % W; y = hz + 3 + r.random() ** 1.6 * (H - hz)
        d.line([(x, y), (x + 4, y)], fill=(40, 60, 120) if k % 3 else (90, 120, 200))
    # 对岸的小岛和她
    d.ellipse([360, hz - 14, 500, hz + 18], fill=(24, 30, 50))
    person(img, 'girl', 420, hz - 6, view='side', pose='stand', expr='laugh', arms='wave', ph=int(T * 5), s=1, flip=True)
    # 悬崖、灯塔和他
    d.polygon([(0, 150), (90, 148), (130, 180), (150, H), (0, H)], fill=(36, 34, 60))
    M.lighthouse(img, d, 60, 150, 90, T, on=0.0)
    ang = lerp(-0.35, 0.05, ease(span(lt, 0, 1.6))) + 0.03 * math.sin(T)
    glow(img, 60, 54, 30, (255, 220, 230), 0.6)
    heart_beam(img, d, 60, 54, ang, 380, clamp(lt / 0.5), T)
    if lt > 1.6:
        glow(img, 420, hz - 30, 30, (255, 200, 220), 0.4)
    person(img, 'boy', 104, 168, view='side', pose='stand', expr='happy', arms='wave', ph=int(T * 5), s=2)
    vig(img, 0.35)


MSGS = [('早安', False), ('早～想你', True), ('今天的云像一只猫', False), ('我看见了！', True), ('下班一起吃饭？', False),
        ('好呀', True), ('晚安', False), ('明天见', True), ('一直都在', False)]


def s_msgs(img, d, lt, dur, T, A):
    """你的每条讯息都是心跳节拍：手机里的聊天气泡踩着拍子一条条跳出来，背后的心电图跟着拍子跳"""
    img.paste((16, 10, 34), (0, 0, W, H))
    t0 = T - lt
    bs = [b for b in props.beats_in(t0 - 3, t0 + dur + 1)]
    # 心电图：拍点从右往左滚
    bx = [W - 60 - (T - b) * 110 for b in bs]
    pts = [(x, 135 + sig.ecg_y(x, bx, 40, 16)) for x in range(0, W, 2)]
    for x, y in pts[::4]: glow(img, x, y, 8, sig.HEART, 0.18)
    d.line(pts, fill=(255, 110, 140), width=2)
    k = thump(T, 0.3)
    for side in (-1, 1):
        sig.heart_at(img, 240 + side * 150, 135, 3 + int(k > 0.5), alpha=0.9)
    # 手机
    box = sig.phone(img, d, 164, 10, 152, 250, scr=(236, 238, 246), light=False)
    sx0, sy0, sx1, sy1 = box
    d.rectangle([sx0, sy0, sx1, sy0 + 26], fill=(250, 250, 252))
    sig.pix_text(d, '她', (sx0 + sx1) / 2 - 6, sy0 + 8, (40, 40, 50))
    sig.heart_at(img, (sx0 + sx1) / 2 + 12, sy0 + 15, 1)
    sig.bars(d, sx1 - 14, sy0 + 7, 4, 1, on=(40, 40, 50))
    shown = [b for b in bs if t0 <= b <= T]
    n = len(shown)
    y = sy1 - 44
    for i in range(n - 1, max(-1, n - 8), -1):
        msg, mine = MSGS[i % len(MSGS)]
        f = span(T, shown[i], shown[i] + 0.2)
        if mine: sig.bubble(img, d, sx1 - 6, y, msg, True, f)
        else: sig.bubble(img, d, sx0 + 6, y, msg, False, f)
        y -= 26
        if y < sy0 + 30: break
    d.rectangle([sx0, sy0 + 26, sx1, sy0 + 27], fill=(220, 222, 232))


def s_hug(img, d, lt, dur, T, A):
    """每秒都想拥你入怀：黄昏的花田，两人从两边跑过来抱在一起，花瓣和心一起炸开"""
    sky(img, GOLDEN, 0, H, 6)
    glow(img, 240, 190, 200, (255, 210, 150), 0.45)
    d.ellipse([210, 160, 270, 220], fill=(255, 234, 186))
    pix.hills(d, 196, 8, 0.015, 0.5, (210, 150, 130))
    d.rectangle([0, 206, W, H], fill=(120, 160, 90))
    kit.flowers(d, T, 210, 270, 120, 6)
    meet = 2.2
    u = ease(span(lt, 0, meet))
    if lt < meet:
        person(img, 'boy', lerp(40, 222, u), 246, view='side', pose='run', ph=wph(lt, 10), expr='laugh', s=2)
        person(img, 'girl', lerp(440, 258, u), 246, view='side', pose='run', ph=wph(lt, 10) + 2, expr='laugh', s=2, flip=True)
    else:
        b = props.thump(T, 0.3)
        person(img, 'boy', 228, 246, view='side', pose='stand', expr='closed', arms='hug', s=2)
        person(img, 'girl', 250, 246, view='side', pose='stand', expr='closed', arms='hug', s=2, flip=True)
        f = lt - meet
        glow(img, 240, 190, 60, sig.HEART, 0.4 + 0.2 * b)
        for j in range(16):
            a = j * math.pi / 8
            rr = 10 + f * 90
            if rr < 240:
                c = ((255, 160, 190), (255, 230, 140), (255, 255, 255))[j % 3]
                d.rectangle([240 + math.cos(a) * rr, 180 + math.sin(a) * rr * 0.7, 241 + math.cos(a) * rr, 181 + math.sin(a) * rr * 0.7], fill=c)
        sig.heart_at(img, 240, 140 - 4 * math.sin(T * 3), 2 + int(b > 0.5))
    pix.petals(d, T, 50, wind=50)
    vig(img, 0.3)


def s_cute(img, d, lt, dur, T, A):
    """全世界你最可爱：她站在转动的地球顶上挥手，四面的小人举起心，满天烟花踩着拍子炸开"""
    kit.night(img, d, T, DEEP, 220)
    t0 = T - lt
    cols = [(255, 120, 160), (255, 220, 100), (120, 220, 255), (200, 140, 255)]
    for i, b in enumerate(props.beats_in(t0 - 1.5, T)):
        r = rng(int(b * 100))
        pix.firework(img, d, T, b - 0.5, r.uniform(60, 420), r.uniform(40, 110), cols[i % 4], r=30, seed=i)
    cx, cy, R = 240, 330, 140
    sig.globe(img, d, cx, cy, R, T, 0.5)
    for k, ang in enumerate((-60, -40, 40, 60, -75, 75)):
        kit.on_sphere(img, 'boy' if k % 2 else 'girl', cx, cy, R, ang, 1, view='front', expr='happy', arms='up' if int(T * 3 + k) % 2 else 'spread')
        a = math.radians(ang)
        sig.heart_at(img, cx + math.sin(a) * (R + 50), cy - math.cos(a) * (R + 50), 1)
    kit.on_sphere(img, 'girl', cx, cy, R, 0, 2, view='front', expr='laugh', arms='wave', ph=int(T * 5))
    # 他举着牌子
    kit.on_sphere(img, 'boy', cx, cy, R, -22, 2, view='front', expr='happy', arms='up')
    sx, sy = 160, 118
    d.line([(sx - 14, sy + 14), (sx - 14, sy + 40)], fill=(150, 110, 80), width=2)
    d.rectangle([sx - 44, sy - 6, sx + 16, sy + 16], fill=OUT)
    d.rectangle([sx - 43, sy - 5, sx + 15, sy + 15], fill=(255, 250, 240))
    sig.pix_text(d, '最可爱!', sx - 39, sy - 2, (230, 60, 90))
    for k in range(30):
        r = rng(k)
        x = (r.uniform(0, W) + 20 * math.sin(T + k)) % W; y = (r.uniform(0, H) + T * 40 * r.uniform(0.5, 1)) % H
        d.rectangle([x, y, x + 1, y + (k % 2)], fill=cols[k % 4])


def s_me(img, d, lt, dur, T, A):
    """你是我：他的特写，暖橙色的光，脸红"""
    sky(img, ((0, (255, 170, 110)), (1, (255, 226, 180))), 0, H, 4)
    sc_b.rays(img, 240, 90, T, (255, 236, 200), 0.35, 12, -0.2)
    props.bokeh(img, T, 14, seed=7, a=0.35)
    props.bust(img, d, 'boy', 240, 40 - eout(span(lt, 0, 0.5)) * 6, 6, 'happy')
    for x in (196, 270): d.rectangle([x, 136, x + 10, 140], fill=pix.BLUSH)
    sig.heart_at(img, 160, 80 - 4 * math.sin(T * 3), 2)


def s_planet(img, d, lt, dur, T, A):
    """这一辈子都不想失联的爱：一颗小星球上，他和她站在两边，一根发光的线绕过星球顶上连着两只罐子"""
    img.paste((4, 4, 18), (0, 0, W, H))
    stars(d, T, H, 1, 240)
    kit.galaxy(img, 0.7, 9, 0.5, 34)
    cx, cy, R = 240, 190, 74
    a = T * 0.7
    mx, my = cx + math.cos(a) * 170, cy - 30 + math.sin(a) * 40
    if math.sin(a) < 0: sig.planet(img, d, mx, my, 12, T, ground=(220, 220, 230), ground_d=(180, 180, 200), sea=(200, 200, 214))
    sig.planet(img, d, cx, cy, R, T, spin=0.15)
    if math.sin(a) >= 0: sig.planet(img, d, mx, my, 12, T, ground=(220, 220, 230), ground_d=(180, 180, 200), sea=(200, 200, 214))
    kit.on_sphere(img, 'boy', cx, cy, R, -40, 2, view='side', expr='happy', arms='phone')
    kit.on_sphere(img, 'girl', cx, cy, R, 40, 2, view='side', expr='happy', arms='phone', flip=True)
    p0 = (cx + math.sin(math.radians(-40)) * (R + 56) + 14, cy - math.cos(math.radians(-40)) * (R + 56))
    p1 = (cx + math.sin(math.radians(40)) * (R + 56) - 14, cy - math.cos(math.radians(40)) * (R + 56))
    pts = sig.string_pts(p0, p1, -50, 60)
    for i in range(0, 61, 5): glow(img, pts[i][0], pts[i][1], 7, sig.SIG, 0.35)
    d.line(pts, fill=(250, 240, 220))
    for k in range(3):
        u = (lt * 0.5 + k / 3) % 1
        x, y = pts[int(u * 60)]
        sig.heart_at(img, x, y, 1)
    sig.satellite(d, 90 + 10 * math.sin(T), 60, 1.2, 0.4, T=T)
    pix.meteor(d, lt, 1.0, 460, 20, -160, 90, 1.0); pix.meteor(d, lt, 3.0, 400, 10, -120, 70, 0.9)


def s_mount(img, d, lt, dur, T, A):
    """就算你的呼吸远在千山之外：天快亮了，层层叠叠的山往后退，一架带着心的纸飞机越过一座座山，飞向最远的山顶上的她"""
    u = lt / dur
    sky(img, DAWN, 0, H, 6)
    stars(d, T, 80, 1 - u, 100)
    sy = lerp(230, 150, ease(u))
    glow(img, 400, sy, 120, (255, 220, 170), 0.5)
    d.ellipse([380, sy - 20, 420, sy + 20], fill=(255, 240, 200))
    off = lt * 30
    sig.mountains(d, 190, 80, 0.006, 0.2, (150, 120, 170), (240, 230, 250), off * 0.3)
    sig.mountains(d, 210, 70, 0.009, 0.6, (110, 90, 140), (220, 210, 240), off * 0.6)
    # 最远处的山顶上的她（在第二层山之后、近处山之前）
    gx = lerp(560, 410, ease(span(lt, 0, dur)))
    sig.mountains(d, 236, 60, 0.013, 0.1, (70, 60, 100), None, off * 1.0)
    d.polygon([(gx - 60, 240), (gx, 196), (gx + 60, 240)], fill=(60, 52, 90))
    person(img, 'girl', gx, 198, view='side', pose='stand', expr='happy' if lt > 3.5 else 'smile', arms='reach' if lt > 3.4 else 'down', s=1, flip=True)
    sig.mountains(d, 262, 40, 0.02, 0.8, (40, 34, 64), None, off * 1.6)
    # 纸飞机
    f = ease(span(lt, 0.2, dur - 0.5))
    px = lerp(-20, gx - 10, f); py = lerp(170, 186, f) - 50 * math.sin(f * math.pi)
    ang = 0.15 * math.cos(f * math.pi) - 0.1
    for j in range(10):
        fj = clamp(f - j * 0.012)
        tx = lerp(-20, gx - 10, fj); ty = lerp(170, 186, fj) - 50 * math.sin(fj * math.pi)
        d.point((tx - 14, ty - 2), fill=lerpc((255, 240, 250), (150, 120, 170), j / 10))
    M.plane(d, px, py, 1.4, ang)
    sig.heart_at(img, px - 12, py - 8, 1)
    glow(img, px - 8, py - 4, 16, (255, 230, 240), 0.4)
    for k in range(4):
        sp = (lt * 0.8 + k / 4) % 1
        props.puff(img, lerp(20, 60, sp), 230 - sp * 20, 2 + sp * 4, (250, 250, 255), (1 - sp) * 0.6)


def s_believe(img, d, lt, dur, T, A):
    """请你相信我给的爱值得你爱：银河下的山顶，他把一颗发光的心交给她；两人的特写；镜头拉远，满天流星连成一颗大心，信号满格"""
    def hill(img, d, t):
        kit.night(img, d, T, DEEP, 240)
        kit.galaxy(img, 1.0, 11, -0.4, 44)
        kit.meteors(d, T, 1.2, 13)
        d.ellipse([60, 200, 420, 360], fill=(26, 34, 64)); d.rectangle([0, 250, W, H], fill=(20, 26, 50))
        give = ease(span(t, 0.6, 2.4))
        person(img, 'boy', 212, 210, view='side', pose='stand', expr='smile', arms='reach', s=2)
        person(img, 'girl', 268, 210, view='side', pose='stand', expr='happy' if give > 0.9 else 'surprised', arms='reach' if give > 0.6 else 'down',
               s=2, flip=True)
        hx, hy = lerp(232, 246, give), 168 - 12 * math.sin(give * math.pi)
        r = 30 + 12 * thump(T, 0.3) + give * 20
        glow(img, hx, hy, r, sig.HEART, 0.6)
        sig.heart_at(img, hx, hy, 2)
        for j in range(8):
            a = j * math.pi / 4 + T
            sparkle(d, int(hx + math.cos(a) * (14 + give * 10)), int(hy + math.sin(a) * (12 + give * 8)), T + j, (255, 230, 240), 2)

    def faces(img, d, t):
        sky(img, ((0, (40, 30, 90)), (1, (160, 110, 180))), 0, H, 5)
        stars(d, T, H, 1, 160)
        props.bokeh(img, T, 12, seed=11, a=0.3)
        props.bust(img, d, 'boy', 150, 52, 5, 'happy')
        props.bust(img, d, 'girl', 330, 52, 5, 'closed' if 0.8 < t < 1.0 else 'happy')
        k = thump(T, 0.3)
        sig.heart_at(img, 240, 90 - 4 * math.sin(T * 3), 3 + int(k > 0.5))
        glow(img, 240, 90, 40, sig.HEART, 0.4)

    def wide(img, d, t):
        kit.night(img, d, T, DEEP, 240)
        kit.galaxy(img, 0.9, 11, -0.4, 44)
        kit.meteors(d, T, 3.0, 17, (0, 0, W, 160), 0.7)
        kit.heart_constellation(img, d, 240, 76, 4.2, span(t, 0.2, 2.6), T, n=24)
        if t > 2.6:
            glow(img, 240, 80, 110, sig.HEART, 0.25 * clamp((t - 2.6) / 0.6))
            sig.bars(d, 222, 150, 4 * span(t, 2.6, 3.4), 3, on=sig.SIG)
        d.ellipse([160, 236, 320, 300], fill=(26, 34, 64)); d.rectangle([0, 262, W, H], fill=(20, 26, 50))
        person(img, 'boy', 234, 240, view='side', arms='hold', expr='happy')
        person(img, 'girl', 246, 240, view='side', arms='hold', expr='happy', flip=True)
        sig.heart_at(img, 240, 192, 1)
    shots(img, lt, [(0, hill), (4.0, faces), (7.8, wide)], 0.5)


def s_float(img, d, lt, dur, T, A):
    """oh oh / 啊啊啊：两人并肩坐在弯月上晃着腿，星星鲸鱼从下面游过，月亮下是一片云海"""
    kit.night(img, d, T, DEEP, 240)
    kit.galaxy(img, 0.8, 4, -0.3, 40)
    u = span(lt, 0, dur)
    sig.whale(img, d, lerp(W + 80, -80, u), 200 + 10 * math.sin(lt), 2.5, T, flip=True)
    for k in range(7):
        r = rng(k)
        cloud(d, (r.uniform(-60, W) - T * 6 * (0.5 + r.random())) % (W + 120) - 80, 220 + r.uniform(0, 40), 3, (70, 70, 130), (54, 54, 104))
    my = 120 + 4 * math.sin(T * 0.8)
    kit.crescent(img, d, 240, my, 56, (255, 236, 186), (0.5, -0.25))
    person(img, 'boy', 214, my + 40, view='side', pose='sit', expr='happy', arms='lap', s=2, flip=True)
    person(img, 'girl', 238, my + 40, view='side', pose='sit', expr='closed', arms='lap', s=2, flip=True)
    sig.heart_at(img, 226, my - 30 - 3 * math.sin(T * 2), 1)
    for k in range(6):
        twinkle(d, int(150 + k * 40), int(40 + (k * 23) % 60), (T * 0.5 + k * 0.19) % 1, (255, 250, 220), 4)
    kit.meteors(d, T, 0.7, 21)


def s_dawn(img, d, lt, dur, T, A):
    """天亮了：两座楼顶之间还牵着那根线，两人手牵手走在楼顶上，太阳升起来，鸟飞过，信号满格"""
    u = span(lt, 0, dur)
    sky(img, mix_stops(DAWN, kit.DAY, ease(u)), 0, H, 6)
    stars(d, T, 100, clamp(1 - u * 3), 100)
    sy = lerp(210, 70, ease(u))
    glow(img, 360, sy, 160, (255, 230, 170), 0.5)
    d.ellipse([336, sy - 24, 384, sy + 24], fill=(255, 244, 200))
    for k in range(5): pix.bird(d, int(lerp(-20, 500, (lt * 0.06 + k * 0.08) % 1)), int(70 + k * 6 + 4 * math.sin(T + k)), T, (90, 80, 110), k)
    pix.city(img, d, 252, 31, 0, (160, 150, 190), (255, 240, 200), 60, 150, 0.1, T, blink=False)
    pix.city(img, d, 262, 7, 0, (120, 110, 160), (255, 236, 190), 40, 110, 0.12, T, blink=False)
    sig.rooftop(d, -10, 170, 190, (100, 92, 140), (150, 140, 190), None, T, True, 1)
    sig.rooftop(d, 330, 490, 200, (100, 92, 140), (150, 140, 190), None, T, False, 2)
    p0 = sig.can(d, 120, 186, 1); p1 = sig.can(d, 370, 196, 1, flip=True)
    sig.string(img, d, p0, p1, 26, T, col=(250, 240, 220), glow_a=0.3)
    x = lerp(400, 446, ease(span(lt, 0.5, 4.0)))
    walking = 0.5 < lt < 4.0
    person(img, 'boy', x - 12, 200, view='side' if walking else 'back', pose='walk' if walking else 'stand', ph=wph(lt, 5), arms='hold', expr='happy', s=1)
    person(img, 'girl', x + 2, 200, view='side' if walking else 'back', pose='walk' if walking else 'stand', ph=wph(lt, 5) + 2, arms='hold', expr='happy', s=1)
    # 右上角的状态栏
    d.rounded_rectangle([352, 10, 470, 30], 6, fill=(255, 255, 255))
    sig.bars(d, 360, 25, 4, 1, on=(60, 180, 110))
    sig.pix_text(d, '已连接', 376, 13, (60, 60, 80))
    sig.heart_at(img, 456, 20, 1)
    vig(img, 0.25)


def s_end(img, d, lt, dur, T, A):
    """片尾：夜空里星星再拼出片名，下面一颗跳动的心和满格的信号，最后慢慢黑下来"""
    kit.night(img, d, T, NIGHT, 220)
    kit.galaxy(img, 0.8)
    cells, box = sc_a.title_cells()
    bx0, by0, bx1, by1 = box
    glow(img, W / 2, sc_a.TITLE_CY, 220, (90, 140, 255), 0.25 * clamp(lt / 2), 70)
    for (cx, cy, col, u, r, sx, sy) in cells:
        arrive = 0.3 + u * 1.6 + r * 0.5
        f = clamp(lt / arrive) if arrive > 0 else 1
        fe = ease(f)
        x, y = lerp(sx, cx, fe), lerp(sy, cy, fe)
        tw = 0.75 + 0.25 * math.sin(T * 4 + r * 30)
        c = lerpc((40, 50, 110), col, tw if f >= 1 else fe)
        if f >= 1: d.rectangle([x, y, x + sc_a.TS - 2, y + sc_a.TS - 2], fill=c)
        else: d.point((x, y), fill=c)
    a = clamp((lt - 2.4) / 0.8)
    if a > 0:
        ar = props.artist_str()
        if ar: text(img, ar, W / 2, by1 + 20, col=(236, 240, 255), alpha=a)
        k = thump(T, 0.3)
        sig.heart_at(img, W / 2 - 30, by1 + 46, 2 + int(k > 0.5), alpha=a)
        sig.bars(d, W / 2 - 6, by1 + 52, 4, 2, on=sig.SIG)
        text(img, '信号满格 · 永不失联', W / 2, by1 + 74, col=(170, 210, 255), font=FONT_S, alpha=a, shadow=False)
    kit.meteors(d, T, 0.6, 31)
    fade = clamp((lt - (dur - 3.0)) / 2.6)
    if fade > 0: dither_fade(img, fade)
