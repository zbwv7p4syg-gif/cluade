"""我好想你 · 最后一段副歌和片尾。

在夜里的街上跑，回忆里的两个人一幕幕从身边掠过；镜子里的自己在哭，就用红笔在镜子上画一个笑、写上"我很好"；
台灯下把"我好想你"写满一张纸；把信折成一颗纸星星，放进装满星星的玻璃罐，盖上盖子，贴着"秘密"；
星星飘起来，"你"的影子出现在面前，伸手快要碰到的时候化成光，流进胸口；最后是一颗大大的心，里面是樱花树下的两个人。
片尾：天亮了，关掉台灯，取下衣帽架上的红围巾围好，走到山坡上那棵树下；片名再出现一次。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
from props import *          # noqa: F401,F403
from pix import (W, H, FONT, FONT_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky, stars,
                 person, wph, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, BAYER, city, put, rain)
from sc_a import scarf_tail, props_text_l, MEM_T
from sc_b import CHORUS, bicycle, umbrella, hill_tree

STAR_COLS = [(255, 214, 110), (255, 150, 170), (150, 210, 255), (190, 160, 255), (170, 240, 190), (255, 250, 236)]


def paper_star(d, x, y, r, col, rot=0.0, out=None):
    pts = []
    for k in range(10):
        a = rot - math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.5
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    d.polygon(pts, fill=col, outline=out or lerpc(col, (60, 30, 60), 0.5))
    if r >= 4: d.point((x - r * 0.2, y - r * 0.2), fill=lerpc(col, (255, 255, 255), 0.7))


# ================================================================ 我好想你 好想你（在夜里跑）
def s_run(img, d, lt, dur, T, A):
    off = lt * 240
    sky(img, CHORUS, 0, 226, 6)
    stars(d, T, 200, 1.0, 220, int(lt * 10), 0)
    glow(img, 390, 60, 90, (255, 190, 210), 0.4); moon(d, 390, 60, 26, col=(255, 240, 226))
    city(img, d, 226, 3, off * 0.12, (44, 30, 96), win=(255, 214, 130), hmin=40, hmax=120, frac=0.3, T=T)
    city(img, d, 226, 9, off * 0.3, (26, 20, 66), win=(255, 190, 120), hmin=20, hmax=70, frac=0.3, T=T, wmin=22, wmax=46)
    d.rectangle([0, 226, W, H], fill=(30, 24, 70)); d.line([(0, 226), (W, 226)], fill=(90, 70, 140))
    for x in range(-int(off) % 60 - 60, W, 60): d.rectangle([x, 252, x + 26, 254], fill=(120, 100, 170))
    # 掠过去的回忆：共伞、骑车、长椅上的两个人
    for k, kind in enumerate(('umbrella', 'bike', 'bench')):
        wx = 520 + k * 430 - off * 0.62
        if not -90 < wx < W + 90: continue
        lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay)
        if kind == 'umbrella':
            ld.line([(wx + 9, 140), (wx + 9, 190)], fill=(230, 226, 236), width=2)
            person(lay, 'boy', wx, 226, view='side', expr='happy', arms='umbrella', s=2); person(lay, 'girl', wx + 24, 226, view='side', expr='happy', s=2)
            umbrella(ld, wx + 9, 140, r=34)
        elif kind == 'bike':
            person(lay, 'girl', wx - 28, 217, view='side', pose='sit', expr='happy', arms='hug', s=2)
            bicycle(ld, wx, 226, -T * 8)
            person(lay, 'boy', wx - 4, 212, view='side', pose='sit', expr='happy', arms='reach', s=2)
        else:
            ld.rectangle([wx - 30, 206, wx + 32, 209], fill=(150, 100, 70)); ld.rectangle([wx - 30, 192, wx + 32, 195], fill=(150, 100, 70))
            for px in (wx - 27, wx + 27): ld.rectangle([px, 192, px + 2, 226], fill=(96, 64, 48))
            person(lay, 'boy', wx - 14, 226, view='side', pose='sit', expr='happy', s=2); person(lay, 'girl', wx + 14, 226, view='side', pose='sit', expr='happy', s=2, flip=True)
        glow(img, wx, 190, 70, (255, 220, 170), 0.3)
        dpaste(img, lay, 0, 0, 0.62)
        for i in range(8):
            r = rng(i * 7 + k)
            kk = (T * 0.8 + r.random()) % 1
            d.point((wx + r.uniform(-34, 34), 210 - kk * 80), fill=lerpc((255, 240, 200), (60, 40, 110), kk))
    for i in range(24):                         # 速度线
        r = rng(i * 5 + 2)
        sp = 300 + 400 * r.random()
        x = (r.uniform(0, W + 100) - lt * sp) % (W + 100) - 50; y = r.uniform(20, 250)
        d.line([(x, y), (x + 10 + sp * 0.05, y)], fill=lerpc((90, 70, 150), (255, 226, 240), r.random() * 0.6))
    for k in range(3):                          # 近处掠过的路灯
        x = (k * 300 - off * 1.4) % 900 - 150
        d.rectangle([x, 70, x + 4, H], fill=(18, 14, 46)); d.rectangle([x - 18, 66, x + 4, 70], fill=(18, 14, 46)); d.rectangle([x - 18, 70, x - 10, 73], fill=(255, 236, 170))
        glow(img, x - 14, 74, 30, (255, 226, 160), 0.5)
    x = 150 + 8 * math.sin(lt * 1.6)
    for i in range(7):
        k = (lt * 2.4 + i / 7) % 1
        d.rectangle([x - 8 - k * 60, 180 - 12 * math.sin(k * 3.14) + i % 3 * 2, x - 6 - k * 60, 181 - 12 * math.sin(k * 3.14) + i % 3 * 2], fill=(170, 214, 255))
    d.ellipse([x - 16, 224, x + 16, 230], fill=(18, 14, 46))
    person(img, 'boy', x, 227 - (1 if int(lt * 12) % 2 else 0), view='side', pose='run', ph=wph(lt, 13), expr='sad', s=2)
    pix.petals(d, T, 20, speed=14, wind=-200, seed=4)
    vig(img, 0.45)


# ================================================================ 却欺骗自己（镜子）
def s_mirror(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(170, 206, 204))
    for x in range(0, W, 24): d.line([(x, 0), (x, H)], fill=(196, 226, 222))
    for y in range(0, H, 24): d.line([(0, y), (W, y)], fill=(196, 226, 222))
    d.rectangle([0, 214, W, H], fill=(236, 240, 240)); d.rectangle([0, 214, W, 218], fill=(250, 252, 252)); d.line([(0, 219), (W, 219)], fill=(190, 200, 204))
    # 杯子里两把牙刷、水龙头
    d.rectangle([70, 190, 90, 214], fill=(250, 250, 252)); d.rectangle([70, 190, 90, 192], fill=(200, 210, 214))
    d.line([(76, 190), (72, 166)], fill=(120, 170, 230), width=2); d.rectangle([69, 162, 74, 168], fill=(240, 244, 250))
    d.line([(84, 190), (90, 168)], fill=(248, 204, 88), width=2); d.rectangle([88, 164, 93, 170], fill=(240, 244, 250))
    d.rectangle([396, 196, 404, 214], fill=(190, 200, 210)); d.rectangle([380, 192, 404, 198], fill=(190, 200, 210)); d.rectangle([380, 198, 384, 202], fill=(160, 170, 184))
    k = (T * 0.8) % 1
    d.rectangle([381, 202 + k * 10, 382, 204 + k * 10], fill=(150, 200, 250))
    # 镜子和镜子里的自己
    mx0, my0, mx1, my1 = 128, 14, 352, 196
    d.rounded_rectangle([mx0 - 7, my0 - 7, mx1 + 7, my1 + 7], 12, fill=OUT); d.rounded_rectangle([mx0 - 6, my0 - 6, mx1 + 6, my1 + 6], 11, fill=(236, 200, 130))
    d.rounded_rectangle([mx0, my0, mx1, my1], 6, fill=(120, 150, 170))
    lay = Image.new('RGB', (W, H), (120, 150, 170)); ld = ImageDraw.Draw(lay)
    for x in range(0, W, 24): ld.line([(x, 0), (x, H)], fill=(136, 166, 184))
    for y in range(4, H, 24): ld.line([(0, y), (W, y)], fill=(136, 166, 184))
    cx, top = 240, 46
    eyes = bust(lay, ld, 'boy', cx, top, 4, 'cry')
    for kk, (ex, ey) in enumerate(eyes):
        side = -1 if kk == 0 else 1
        for y in range(int(ey + 4), top + 21 * 4 - 6):
            x = ex + side * (2 + (y - ey) * 0.15)
            ld.rectangle([x, y, x + 1, y], fill=(130, 196, 255) if (y + int(T * 16)) % 6 else (220, 240, 255))
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rounded_rectangle([mx0, my0, mx1, my1], 6, fill=255)
    img.paste(lay, (0, 0), m)
    d.line([(mx0 + 14, my0 + 60), (mx0 + 60, my0 + 12)], fill=(190, 214, 226), width=3); d.line([(mx0 + 30, my0 + 66), (mx0 + 52, my0 + 44)], fill=(190, 214, 226), width=2)
    # 用红笔在镜子上画一个笑，再写上"我很好"
    red = (226, 50, 70)
    f = span(lt, 0.9, 2.2)
    scx, scy, sr = cx + 1, top + 62, 20
    hx = hy = None
    if f > 0:
        a0, a1 = 160, 160 - 140 * f
        d.arc([scx - sr, scy - sr, scx + sr, scy + sr], a1, a0, fill=red, width=3)
        hx, hy = scx + math.cos(math.radians(a1)) * sr, scy + math.sin(math.radians(a1)) * sr
        if f >= 1: d.line([(scx - sr - 2, scy + 2), (scx - sr + 2, scy + 8)], fill=red, width=2); d.line([(scx + sr + 2, scy + 2), (scx + sr - 2, scy + 8)], fill=red, width=2)
    s = '我很好'
    n = int(clamp((lt - 2.7) / 0.5, 0, 3))
    for i in range(n): text(img, s[i], mx0 + 32, my0 + 46 + i * 36, col=red, out=None, scale=2, shadow=False)
    if 2.7 < lt < 4.2: hx, hy = mx0 + 38 + 6 * math.sin(lt * 14), my0 + 46 + ((lt - 2.7) / 0.5) * 36
    if lt > 4.5:
        for i in range(4): twinkle(d, int(mx0 + 30 + rng(i).uniform(0, 190)), int(my0 + 20 + rng(i + 5).uniform(0, 150)), ((lt - 4.5) * 0.8 + i * 0.25) % 1, size=4)
    # 镜子外面的后脑勺和举着笔的手
    d.ellipse([196, 196, 284, 300], fill=pix.LOOK[('boy', 'young')]['hair'], outline=OUT); d.ellipse([214, 204, 244, 222], fill=pix.LOOK[('boy', 'young')]['hair_l'])
    d.rounded_rectangle([150, 250, 330, 300], 20, fill=pix.LOOK[('boy', 'young')]['top'], outline=OUT)
    if hx is not None:
        d.line([(hx, hy), (hx + 12, hy + 16)], fill=red, width=4); d.line([(hx + 12, hy + 16), (hx + 16, hy + 22)], fill=(250, 250, 250), width=4)
        d.rounded_rectangle([hx + 8, hy + 12, hx + 28, hy + 34], 6, fill=pix.SKIN, outline=OUT)
        d.line([(hx + 22, hy + 30), (300, 270)], fill=pix.LOOK[('boy', 'young')]['arm'], width=14)
    vig(img, 0.35)


# ================================================================ 我好想你 好想你（写信）
def s_letter(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(150, 104, 76))
    for y in range(0, H, 22):
        d.line([(0, y), (W, y)], fill=(130, 88, 64))
        for x in range((y * 3) % 80, W, 80): d.line([(x + 10, y + 9), (x + 44, y + 9)], fill=(166, 118, 86))
    # 桌上的东西：合照、杯子、揉掉的纸团、那条红围巾
    d.rectangle([20, 20, 78, 88], fill=(110, 76, 60), outline=OUT); d.rectangle([25, 25, 73, 83], fill=(250, 226, 190))
    person(img, 'boy', 40, 82, view='front', expr='happy'); person(img, 'girl', 60, 82, view='front', expr='happy')
    d.ellipse([400, 26, 446, 72], fill=(236, 240, 244), outline=OUT); d.ellipse([408, 34, 438, 64], fill=(110, 70, 50)); d.rectangle([444, 42, 456, 54], fill=(236, 240, 244), outline=OUT)
    for i, (bx, by) in enumerate(((398, 150), (430, 190), (384, 214), (446, 236), (60, 220), (34, 180))):
        d.ellipse([bx - 11, by - 9, bx + 11, by + 9], fill=(240, 236, 226), outline=(170, 160, 150))
        d.line([(bx - 6, by - 2), (bx + 2, by + 4)], fill=(190, 180, 170)); d.line([(bx - 1, by - 6), (bx + 6, by)], fill=(190, 180, 170))
    for i in range(22):
        sx = 372 + i * 5; sy = 100 + 7 * math.sin(i * 0.5)
        d.rectangle([sx, sy, sx + 5, sy + 13], fill=SCARF if i % 4 else SCARF_D)
    for k in range(4): d.line([(482, 102 + k * 4), (476, 104 + k * 4)], fill=SCARF_D)
    # 信纸
    px0, py0, px1, py1 = 112, 16, 344, 262
    d.rectangle([px0 + 4, py0 + 4, px1 + 4, py1 + 4], fill=(110, 76, 56))
    d.rectangle([px0, py0, px1, py1], fill=(252, 248, 236)); d.rectangle([px0, py0, px1, py1], outline=(200, 190, 170))
    for y in range(py0 + 38, py1 - 8, 26): d.line([(px0 + 12, y), (px1 - 12, y)], fill=(214, 220, 236))
    d.line([(px0 + 26, py0), (px0 + 26, py1)], fill=(246, 190, 190))
    ink = (50, 60, 120)
    s = title_str()
    per_row, rate = 3, 0.092
    n = int(lt / rate)
    cw = int(FONT.getlength(s)) + 12
    cur = None
    for i in range(min(n, 9 * per_row * len(s))):
        row, k = divmod(i, per_row * len(s))
        rep_, ci = divmod(k, len(s))
        x = px0 + 36 + rep_ * cw + int(FONT.getlength(s[:ci])); y = py0 + 28 + row * 26
        if y > py1 - 14: break
        props_text_l(img, s[ci], x + 3, y, ink)
        cur = (x + 16, y + 4)
    for j, (t0, bx, by) in enumerate(((1.6, 196, 96), (3.1, 262, 150), (4.4, 170, 176), (5.2, 290, 70))):    # 眼泪把字洇开
        k = lt - t0
        if k < 0: continue
        if k < 0.25:
            y = lerp(-10, by, k / 0.25); d.rectangle([bx - 1, y - 4, bx + 1, y], fill=(150, 200, 255))
        else:
            rr = min(11, 3 + (k - 0.25) * 18)
            a = np.asarray(img.crop((bx - 14, by - 14, bx + 14, by + 14)), float)
            yy, xx = np.mgrid[-14:14, -14:14]
            msk = (xx * xx + yy * yy) < rr * rr
            blur = (a + np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1) + np.roll(a, 2, 1) + np.roll(a, -2, 0)) / 7
            a[msk] = blur[msk] * 0.94 + np.array([190, 204, 236]) * 0.06
            img.paste(Image.fromarray(a.astype(np.uint8)), (bx - 14, by - 14))
            d.ellipse([bx - rr, by - rr, bx + rr, by + rr], outline=(206, 214, 236))
    lighting(img, [(150, 40, 330, 1.15, 260)], amb=0.2, tint=(0.3, 0.26, 0.42))
    glow(img, 96, 10, 90, (255, 236, 170), 0.5)
    d.polygon([(60, -6), (130, -6), (118, 22), (72, 22)], fill=(255, 244, 200), outline=OUT)
    if cur:                                      # 握笔的手
        hx, hy = cur[0] + 2 * math.sin(lt * 30), cur[1] + 2 * math.cos(lt * 23)
        d.line([(hx, hy), (hx + 26, hy + 34)], fill=(60, 70, 130), width=4); d.line([(hx, hy), (hx + 3, hy + 4)], fill=(30, 30, 50), width=2)
        d.rounded_rectangle([hx + 8, hy + 12, hx + 46, hy + 44], 10, fill=pix.SKIN, outline=OUT)
        for k in range(3): d.line([(hx + 14 + k * 8, hy + 16), (hx + 20 + k * 8, hy + 28)], fill=pix.SKIN_S)
        d.polygon([(hx + 30, hy + 36), (hx + 48, hy + 26), (hx + 130, hy + 130), (hx + 90, hy + 150)], fill=pix.LOOK[('boy', 'young')]['top'], outline=OUT)
    vig(img, 0.45)


# ================================================================ 就当作秘密（玻璃罐）
JAR = (292, 96, 400, 222)


@lru_cache(None)
def jar_stars(n=120):
    r = rng(8); out = []
    x0, y0, x1, y1 = JAR
    for i in range(n):
        lv = i / n
        out.append((r.uniform(x0 + 12, x1 - 12), y1 - 8 - lv * 78 - r.uniform(0, 8), r.choice(STAR_COLS), r.uniform(0, 6.28), r.random()))
    return out


def jar(img, d, T, lid=1.0, glow_a=0.5, label=1.0, n=120):
    x0, y0, x1, y1 = JAR
    glow(img, (x0 + x1) / 2, (y0 + y1) / 2 + 10, 110, (255, 226, 150), glow_a * (0.8 + 0.2 * math.sin(T * 2)))
    tfill(img, 'rounded_rectangle', [x0, y0 + 14, x1, y1], (200, 230, 240), 0.25)
    for (sx, sy, c, rot, k) in jar_stars()[:n]:
        tw = 0.6 + 0.4 * math.sin(T * (1.5 + k * 2) + rot)
        paper_star(d, sx, sy, 6, lerpc(lerpc(c, (60, 50, 90), 0.35), c, tw), rot + 0.2 * math.sin(T + k * 6))
    d.rounded_rectangle([x0, y0 + 14, x1, y1], 14, outline=(214, 240, 250), width=2)
    d.rectangle([x0 + 16, y0, x1 - 16, y0 + 16], outline=(214, 240, 250), width=2)
    d.line([(x0 + 8, y0 + 34), (x0 + 8, y1 - 30)], fill=(250, 255, 255), width=2); d.line([(x0 + 14, y0 + 30), (x0 + 14, y0 + 50)], fill=(250, 255, 255))
    ly = y0 - 12 - 60 * (1 - lid)
    d.rounded_rectangle([x0 + 12, ly, x1 - 12, ly + 14], 3, fill=(190, 140, 96), outline=OUT)
    for k in range(5): d.point((x0 + 22 + k * 16, ly + 5 + (k % 2) * 4), fill=(150, 104, 70))
    if label > 0:
        cx = (x0 + x1) // 2
        d.line([(x0 + 14, y0 + 8), (x1 - 14, y0 + 8)], fill=SCARF, width=2)
        d.polygon([(cx - 22, y0 + 26), (cx + 22, y0 + 26), (cx + 22, y0 + 46), (cx - 22, y0 + 46)], fill=(250, 240, 214), outline=OUT)
        d.line([(cx, y0 + 9), (cx, y0 + 26)], fill=SCARF)
        text(img, '秘密', cx, y0 + 36, col=(150, 60, 70), out=None, font=FONT_S, shadow=False, alpha=label)


def s_secret(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(52, 44, 84))
    for x in range(0, W, 26): d.line([(x, 0), (x, 222)], fill=(58, 50, 92))
    window(img, d, 44, 30, 76, 76, T, moon_at=(54, 20, 9), curtain=(120, 110, 160), frame=(150, 140, 190))
    # 架子上别的罐子：每一颗星星都是一句没说出口的话
    d.rectangle([180, 70, 280, 74], fill=(110, 80, 90))
    for k in range(3):
        jx = 190 + k * 30
        d.rounded_rectangle([jx, 44, jx + 22, 70], 5, outline=(170, 200, 220)); d.rectangle([jx + 4, 40, jx + 18, 44], fill=(150, 110, 80))
        for q in range(7): paper_star(d, jx + 5 + (q * 5) % 14, 66 - (q * 3) % 16, 3, STAR_COLS[(q + k) % 6])
        glow(img, jx + 11, 58, 16, (255, 226, 150), 0.25)
    d.rectangle([0, 222, W, H], fill=(120, 84, 70)); d.rectangle([0, 222, W, 226], fill=(160, 114, 90))
    fold = ease(span(lt, 0.2, 1.5))             # 信纸折成一颗星
    fly = ease(span(lt, 1.9, 3.0))              # 放进罐子
    lid = ease(span(lt, 3.3, 4.0))
    px, py = 150, 262
    jar(img, d, T, lid=lid, glow_a=0.35 + 0.3 * lid, label=span(lt, 4.3, 4.8), n=118 + (2 if fly >= 1 else 0))
    person(img, 'boy', px, py, view='side', expr='closed' if lt > 4.4 else ('sad' if lt < 1.9 else 'down'), arms='reach' if lt < 3.2 else 'down', s=3)
    hx, hy = px + 28, py - 42
    if fly < 1:
        x0, y0, x1, y1 = JAR
        sx = lerp(hx, (x0 + x1) / 2, fly); sy = lerp(hy, y0 + 40, fly) - 70 * math.sin(fly * math.pi)
        if fold < 1:
            w = lerp(26, 6, fold); h = lerp(34, 6, fold)
            d.rectangle([sx - w / 2, sy - h / 2, sx + w / 2, sy + h / 2], fill=(252, 248, 236), outline=OUT)
            if fold < 0.5:
                for k in range(3): d.line([(sx - w / 2 + 3, sy - h / 2 + 5 + k * 7), (sx + w / 2 - 3, sy - h / 2 + 5 + k * 7)], fill=(50, 60, 120))
            for k in range(int(fold * 3) + 1): d.line([(sx - w / 2, sy - h / 2 + k * h / 3), (sx + w / 2, sy - h / 2 + k * h / 3)], fill=(190, 180, 170))
        else:
            glow(img, sx, sy, 16, (255, 220, 130), 0.6)
            paper_star(d, sx, sy, 8, (255, 214, 110), lt * 5)
            twinkle(d, int(sx), int(sy), (lt * 2) % 1, size=5)
            for k in range(1, 6): d.point((lerp(hx, sx, 1 - k * 0.06), sy + k * 2 + math.sin(k + lt * 9) * 2), fill=lerpc((255, 240, 180), (52, 44, 84), k / 6))
    if 3.9 < lt < 4.5:
        for i in range(8):
            a = i * 0.785; rr = 20 + 60 * (lt - 3.9)
            d.point((346 + math.cos(a) * rr, 90 + math.sin(a) * rr * 0.5), fill=(255, 250, 220))
    if lt > 4.4:
        d.rectangle([px + 15, py - 62, px + 17, py - 48], fill=pix.SKIN, outline=pix.OUT)       # 嘘
        text(img, '嘘…', px + 46, py - 84, col=(240, 236, 255), font=FONT_S, alpha=span(lt, 4.5, 4.9))
    lighting(img, [(346, 160, 190, 0.95), (82, 68, 80, 0.4)], amb=0.3, tint=(0.34, 0.32, 0.56))
    vig(img, 0.45)


# ================================================================ 我好想你 / 好想你 / 就深藏在 / 心
D1, D2, D3 = 3.60, 3.03, 2.70                   # 前三句的长度
ME_X, YOU_X, GY = 184, 296, 214


def inner_bg(img, d, T, k=0.0):
    sky(img, ((0, (10, 8, 34)), (0.5, (30, 18, 70)), (0.85, (70, 30, 96)), (1, (120, 50, 110))), 0, H, 6)
    glow(img, 240, 150, 240, (150, 80, 190), 0.25, ry=150)
    stars(d, T, H, 0.8, 200)
    for i in range(46):                          # 从罐子里飘出来的纸星星
        r = rng(i * 13 + 5)
        ph = (T * (0.05 + 0.06 * r.random()) + r.random()) % 1
        x = r.uniform(0, W) + 16 * math.sin(T * 0.6 + i); y = H + 10 - ph * (H + 30)
        paper_star(d, x, y, 3 + (i % 3), lerpc(STAR_COLS[i % 6], (30, 18, 70), 0.3 + 0.3 * r.random()), T * (0.5 + r.random()) + i)
    d.ellipse([60, GY - 8, 420, GY + 40], fill=(24, 14, 56)); d.ellipse([90, GY - 4, 390, GY + 30], outline=(90, 60, 140))


def inner(img, d, t, T):
    """最后四句连成一场戏。t 从"我好想你"那一句开始算"""
    inner_bg(img, d, T)
    t2, t3 = D1, D1 + D2
    appear = ease(span(t, 0.5, 2.6))
    melt = ease(span(t, t3 + 0.1, t3 + 2.2))
    # "你"
    ga = appear * (1 - melt)
    if ga > 0:
        glow(img, YOU_X, GY - 50, 70, (255, 226, 170), 0.35 * ga)
        ghost(img, 'girl', YOU_X, GY, 3, 0.25 + 0.65 * ga if appear > 0.2 else ga, view='side', expr='happy' if t > t2 else 'smile', flip=True,
              arms='reach' if t > t2 + 0.4 else 'auto')
    # "我"
    if t < t3 + 1.2:
        expr = 'closed' if t < 1.8 else ('surprised' if t < 2.8 else ('sad' if t < t2 + 1.2 else 'smile'))
        person(img, 'boy', ME_X, GY, view='side', expr=expr, arms='reach' if t > t2 + 0.6 else 'auto', s=3)
        if t > t2 + 1.2:
            k = ((t - t2 - 1.2) * 0.9) % 1
            d.rectangle([ME_X + 9, GY - 60 + k * 22, ME_X + 10, GY - 57 + k * 22], fill=(170, 214, 255))
    else:
        person(img, 'boy', ME_X, GY, view='front', expr='closed', arms='cross', s=3)
    # 指尖之间
    if t2 + 0.8 < t < t3 + 0.3:
        fx = (ME_X + 24 + YOU_X - 24) / 2; fy = GY - 38
        glow(img, fx, fy, 20 + 6 * math.sin(T * 6), (255, 240, 200), 0.6)
        twinkle(d, int(fx), int(fy), (T * 1.5) % 1, size=6)
        for i in range(6): d.point((fx + 16 * math.cos(T * 3 + i), fy + 10 * math.sin(T * 3 + i)), fill=(255, 236, 200))
    # 化成光，流进胸口
    hx, hy = ME_X + (3 if t < t3 + 1.2 else 0), GY - 36
    if melt > 0:
        for i in range(110):
            r = rng(i * 7 + 3)
            k = (t - t3 - 0.1) / 1.5 - r.random() * 0.8
            if k <= 0 or k >= 1: continue
            sx = YOU_X + r.uniform(-18, 18); sy = GY - r.uniform(6, 110)
            e = ease(k)
            x = lerp(sx, hx, e) + 20 * math.sin(k * 3.14) * math.sin(i); y = lerp(sy, hy, e) - 34 * math.sin(k * 3.14) * r.random()
            c = [(255, 236, 170), (255, 170, 190), SCARF_L, (255, 255, 240)][i % 4]
            d.rectangle([x, y, x + (i % 2), y + (i % 2)], fill=c)
        hk = ease(span(t, t3 + 0.6, t3 + 2.4))
        pl = thump(T, 0.3)
        glow(img, hx, hy, 20 + 30 * hk + 6 * pl, (255, 110, 140), 0.3 + 0.4 * hk)
        heart(d, hx, hy - 2, 0.2 + 0.4 * hk + 0.05 * pl)


def s_inner1(img, d, lt, dur, T, A): inner(img, d, lt, T); vig(img, 0.45)
def s_inner2(img, d, lt, dur, T, A): inner(img, d, lt + D1, T); vig(img, 0.45)
def s_inner3(img, d, lt, dur, T, A): inner(img, d, lt + D1 + D2, T); vig(img, 0.45)


def heart_world(T):
    """心里面装着的那一幕：樱花树下的两个人"""
    w = Image.new('RGB', (W, H)); wd = ImageDraw.Draw(w)
    sky(w, DAY4, 0, H, 5)
    glow(w, 300, 70, 70, (255, 250, 210), 0.5); wd.ellipse([286, 56, 314, 84], fill=(255, 250, 220))
    for i in range(3): cloud(wd, (i * 150 + T * 4) % 420 + 60, 60 + (i * 23) % 30, 1.3, (255, 255, 255), (220, 230, 246))
    bx0 = hill_tree(w, wd, T, 0.2)
    person(w, 'boy', bx0 + 16, 203, view='side', pose='sit', expr='happy', s=2)
    person(w, 'girl', bx0 + 44, 203, view='side', pose='sit', expr='happy', s=2, flip=True)
    pix.petals(wd, T, 60, speed=22, wind=26)
    grade(w, sat=1.1, mul=(1.05, 1.0, 0.95), add=(8, 4, 0))
    return w


def s_heart(img, d, lt, dur, T, A):
    inner_bg(img, d, T)
    grow = eback(span(lt, 0.0, 0.9))
    shrink = ease(span(lt, dur - 2.2, dur - 0.2))
    pl = thump(T, 0.4)
    s = lerp(0.6, 5.6, grow) * (1 + 0.035 * pl)
    s = lerp(s, 0.7, shrink)
    cx, cy = 240, lerp(118, 140, shrink)
    for b in beats_in(T - 1.6, T + 0.01):        # 一圈圈心形的光
        k = (T - b) / 1.6
        d.line(heart_poly(cx, cy, s * (1 + 0.5 * k)) + [heart_poly(cx, cy, s * (1 + 0.5 * k))[0]], fill=lerpc((255, 150, 170), (40, 20, 70), k))
    glow(img, cx, cy + 3 * s, 34 * s + 20, (255, 110, 150), 0.4 + 0.15 * pl, ry=30 * s + 16)
    pts = heart_poly(cx, cy, s)
    if s > 1.6:
        m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
        world = heart_world(T)
        sh = Image.new('RGB', (W, H)); sh.paste(world, (-12, -22))
        img.paste(sh, (0, 0), m)
        d.line(pts + [pts[0]], fill=(255, 236, 240), width=2)
        for k, (w_, c) in enumerate(((9, (120, 20, 56)), (7, (226, 60, 90)), (3, (255, 150, 170)))):
            d.line(heart_poly(cx, cy, s * (1 + 0.012 * (3 - k))) + [heart_poly(cx, cy, s * (1 + 0.012 * (3 - k)))[0]], fill=c, width=w_)
        d.arc([cx - 15 * s, cy - 11.5 * s, cx - 5 * s, cy - 3 * s], 170, 280, fill=(255, 236, 240), width=3)
        # 一把小锁
        lk = span(lt, 1.6, 2.0)
        lx, ly = cx + 9 * s, cy + 9.5 * s
        d.arc([lx - 7, ly - 16 - 5 * (1 - lk), lx + 7, ly + 2 - 5 * (1 - lk)], 180, 360, fill=(255, 226, 130), width=3)
        d.rounded_rectangle([lx - 10, ly - 6, lx + 10, ly + 10], 3, fill=(255, 206, 90), outline=OUT); d.rectangle([lx - 1, ly - 1, lx + 1, ly + 5], fill=OUT)
        if 1.9 < lt < 2.5: twinkle(d, int(lx), int(ly), (lt - 1.9) / 0.6, size=7)
    else:
        heart(d, cx, cy, s)
    for i in range(7):                           # 绕着心转的星星
        a = T * 0.5 + i * 0.9
        rr = 22 * s + 26
        if s > 1.6: paper_star(d, cx + math.cos(a) * rr, cy + 12 + math.sin(a) * rr * 0.55, 4 + i % 3, STAR_COLS[i % 6], T + i)
    vig(img, 0.45)


# ================================================================ 片尾
def s_dawn(img, d, lt, dur, T, A):
    day = ease(span(lt, 0.5, 8.0))
    st = mix_stops(NIGHT4, DAWN4, span(lt, 0.3, 4.5)) if lt < 4.5 else mix_stops(DAWN4, DAY4, span(lt, 4.5, 10.5))
    lamp_on = 1.0 if lt < 4.2 else 0.0
    took = lt > 7.4
    # "我"：站在窗前看天亮 → 关灯 → 取下红围巾围好 → 往门口走
    if lt < 3.2: kw = dict(me_x=352, me_y=146, me_view='back')
    elif lt < 4.6:
        k = span(lt, 3.2, 4.1); kw = dict(me_x=lerp(352, 300, k), me_y=lerp(146, 134, k), me_view='side', me_pose='walk' if k < 1 else 'stand',
                                          me_ph=wph(lt, 7), me_flip=True, me_arms='reach' if k >= 1 else 'auto')
    elif lt < 7.4:
        k = span(lt, 4.8, 5.8); kw = dict(me_x=lerp(300, 316, k), me_y=lerp(134, 126, k), me_view='side' if k < 1 else 'back', me_pose='walk' if k < 1 else 'stand',
                                          me_ph=wph(lt, 7), me_arms='up' if 6.2 < lt else 'auto')
    else:
        k = span(lt, 8.6, 12.0); kw = dict(me_x=lerp(316, 300, k), me_y=lerp(126, 290, k), me_view='front', me_pose='walk' if k > 0 else 'stand',
                                           me_ph=wph(lt, 7), me_scarf=SCARF)
    room(img, d, T, me='free', lamp=lamp_on, expr='smile' if lt > 7.4 else 'neutral', stops=st, moon_on=lt < 2.4, scarf=not took, day=day * 0.92,
         curtain_open=0.75, sun=(40, int(lerp(74, 30, span(lt, 2.5, 9))), 7) if lt > 2.5 else None, **kw)
    if day > 0.2:                                # 照进来的晨光
        tfill(img, 'polygon', [(330, 88), (404, 88), (372, 236), (240, 236)], (255, 226, 160), 0.22 * day)
        for i in range(18):
            r = rng(i * 5)
            x = r.uniform(270, 400) + 6 * math.sin(T * 0.5 + i); y = (r.uniform(90, 230) - T * 3 * r.random()) % 140 + 90
            if math.sin(T * 2 + i) > 0: d.point((x, y), fill=(255, 244, 210))
    if 7.4 < lt < 8.2:
        for i in range(6): twinkle(d, 316 + int(rng(i).uniform(-14, 14)), 104 + int(rng(i + 4).uniform(-16, 16)), (lt - 7.4) / 0.8, size=4)
    e = ease(span(lt, 8.2, 11.0))
    zoomf(img, lerp(2, 1, e), lerp(326, 240, e), lerp(108, 135, e))
    vig(img, 0.3)
    if lt < 0.8: dither_fade(img, 1 - lt / 0.8, (255, 230, 236))


def s_end(img, d, lt, dur, T, A):
    up = ease(span(lt, 3.2, 6.0))                # 镜头抬向天空
    oy = int(124 * up)
    sky(img, mix_stops(DAWN4, DAY4, span(lt, 0, 7)), 0, H, 6)
    sx, sy = 372, 150 - 40 * span(lt, 0, 8) + oy
    glow(img, sx, sy, 120, (255, 240, 190), 0.55); d.ellipse([sx - 20, sy - 20, sx + 20, sy + 20], fill=(255, 250, 220))
    for i in range(5): cloud(d, (i * 150 + T * 5) % 700 - 120, 20 + (i * 37) % 80 + oy * 0.5, 1.6 + (i % 2) * 0.5, (255, 244, 236), (250, 206, 200))
    for i in range(6): pix.bird(d, (80 + i * 26 + lt * 22) % 560 - 40, 80 - lt * 3 + (i % 3) * 9 + oy * 0.7, T, col=(120, 90, 130), ph=i)
    lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay)
    city(lay, ld, 222, 3, 0, (150, 170, 214), hmin=20, hmax=66)
    bx0 = hill_tree(lay, ld, T, 0.2)
    k = span(lt, 0.2, 2.6)
    px = lerp(40, bx0 + 16, k)
    if k < 1:
        scarf_tail(ld, px, 203 - 31 + (lerp(246, 203, k) - 203), T, n=10)
        person(lay, 'boy', px, lerp(232, 203, k), view='side', pose='walk', ph=wph(lt, 7), expr='smile', s=2, scarf=SCARF)
    else:
        scarf_tail(ld, bx0 + 16, 172, T, n=10)
        person(lay, 'boy', bx0 + 16, 203, view='side', pose='sit', expr='closed' if lt > 3.6 else 'smile', s=2, scarf=SCARF)
    img.paste(lay, (0, oy), lay)
    pix.petals(d, T, 50, speed=22, wind=30)
    ga = span(lt, 2.8, 3.4) * (1 - span(lt, 4.2, 5.2))                    # 身边的位置，风里好像有人坐了一下
    if ga > 0: ghost(img, 'girl', bx0 + 44, 203 + oy, 2, 0.5 * ga, age='ns', view='side', pose='sit', expr='happy', flip=True)
    ta = span(lt, 4.9, 6.2)
    if ta > 0:
        glow(img, 240, 84, 210, (255, 150, 180), 0.2 * ta, ry=80)
        big_text(img, title_str(), W / 2, 84, 4, alpha=ta, gap=10, top=(255, 255, 250), bot=(255, 176, 196), line=(232, 64, 116), out=(90, 30, 80))
        a2 = span(lt, 6.3, 7.0)
        if a2 > 0:
            ar = artist_str()
            text(img, ar, W / 2, 142, col=(150, 44, 92), out=(255, 250, 250), alpha=a2, shadow=False)
            wd = FONT.getlength(ar) / 2 + 12
            for s_ in (-1, 1):
                d.line([(W / 2 + s_ * wd, 142), (W / 2 + s_ * (wd + 26 * a2), 142)], fill=(190, 80, 120))
                put(img, 'heart', W / 2 + s_ * (wd + 34), 142 + round(thump(T, 0.3) * -2), 1, alpha=a2)
            text(img, '· 像 素 M V ·', W / 2, 164, col=(150, 80, 120), out=(255, 250, 250), font=FONT_S, shadow=False, alpha=span(lt, 6.9, 7.6))
        for i in range(5):
            r = rng(i * 7 + int(lt / 0.7 + i * 0.37))
            twinkle(d, int(r.uniform(80, 400)), int(r.uniform(40, 124)), ((lt + i * 0.37) / 0.7) % 1, size=4)
    vig(img, 0.25)
    out = span(lt, 9.6, 12.4)                    # 音乐淡出，画面也暗下去，只剩一颗心
    if out > 0: dither_fade(img, ease(out), (10, 8, 26))
    if out > 0.5:
        ha = span(lt, 11.0, 12.2) * (1 - span(lt, 15.6, 17.2))
        pl = thump(T, 0.35) if lt < 13.5 else max(0, 1 - ((lt - 13.5) % 1.2) / 0.35)
        if ha > 0:
            glow(img, 240, 132, 36 + 8 * pl, (255, 100, 130), 0.4 * ha)
            put(img, 'bigheart', 240, 130, 2 + (1 if pl > 0.6 else 0), alpha=ha)
