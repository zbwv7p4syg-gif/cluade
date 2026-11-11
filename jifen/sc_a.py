"""几分之几 · 片头和第一段主歌。

片头：黑暗里一个像素像光标一样随拍子闪，拉成一道横线；四面八方飞来的小方块在横线上下各拼出一个"几"，
成了一个分数"几分之几"。横线一直拉到画面两边，变成地平线：上面亮起黎明的天空，下面铺开金色的平原，
太阳从横线后面升起来，两个"几"挪上天空，中间落下"分""之"，拼成横排的片名。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
import motifs
import fx
from pix import (W, H, FONT, FONT_S, OUT, SKIN, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, rng, tri)
from props import dpaste, person_s, mix_stops, shots, CREAM, GOLD, GOLD_L, PINK, PINK_L
from motifs import GOLD_SKY, DUSK_SKY, DAWN_SKY, NIGHT_SKY, NOON_SKY, PLAIN_GOLD, PLAIN_DAWN

YY, XX = np.mgrid[0:H, 0:W]
TITLE_KW = dict(top=(255, 252, 240), bot=(255, 196, 110), line=(200, 104, 70), out=(46, 26, 40))
BAR = (255, 240, 200)


@lru_cache(None)
def glyph_blocks(ch, scale, cx, cy):
    """和 props.big_text 摆法一致：这个字每个点阵像素在屏幕上的左上角和颜色"""
    w = int(FONT.getlength(ch)) + 8; h = FONT.size + 8
    m = Image.new('L', (w, h)); md = ImageDraw.Draw(m); md.fontmode = '1'
    md.text((4, 3), ch, font=FONT, fill=255)
    ys, xs = np.nonzero(np.array(m))
    x0 = cx - FONT.getlength(ch) * scale / 2 - 4 * scale
    y0 = cy - (h + 1) * scale / 2
    out = []
    for px, py in zip(xs, ys):
        out.append((x0 + px * scale, y0 + py * scale, lerpc(TITLE_KW['top'], TITLE_KW['bot'], (py - 4) / (FONT.size - 1))))
    return out


def blocks_fly(img, d, ch, scale, cx, cy, lt, t0, t1, seed, from_='top', fly=0.9):
    """小方块从画面外飞来拼成一个字：每块在 t0..t1 之间随机出发，飞 fly 秒到位。全部到位后返回 True"""
    bl = glyph_blocks(ch, scale, cx, cy)
    r = rng(seed)
    done = True
    for i, (tx, ty, col) in enumerate(bl):
        st = lerp(t0, t1, r.random())
        sx = r.uniform(-40, W + 40); sy = -20 - r.uniform(0, 60) if from_ == 'top' else H + 20 + r.uniform(0, 60)
        if r.random() < 0.3: sx = -30 if r.random() < 0.5 else W + 30; sy = r.uniform(0, H)
        f = (lt - st) / fly
        if f < 0: done = False; continue
        if f < 1:
            done = False
            e = eout(f)
            x = lerp(sx, tx, e) + math.sin(f * 9 + i) * 10 * (1 - e)
            y = lerp(sy, ty, e)
            c = lerpc((255, 255, 255), col, f)
            for k in range(3):                                   # 一小段拖尾
                q = max(0, e - 0.04 * (k + 1))
                qx, qy = lerp(sx, tx, q), lerp(sy, ty, q)
                d.point((qx + scale / 2, qy + scale / 2), fill=lerpc(col, (20, 18, 40), 0.4 + k * 0.2))
            d.rectangle([x, y, x + scale - 1, y + scale - 1], fill=c)
        else:
            flash = clamp(1 - (f - 1) * 4)
            d.rectangle([tx, ty, tx + scale - 1, ty + scale - 1], fill=lerpc(col, (255, 255, 255), flash))
    return done


def dark_bg(img, d, T, a=1.0, grid=0.0):
    pix.sky(img, ((0, (6, 6, 20)), (0.6, (14, 12, 36)), (1, (26, 18, 46))))
    if grid > 0:                                               # 方格纸：像算分数的草稿纸
        g = grid * (0.6 + 0.4 * props.thump(T, 0.5))
        c = lerpc((14, 12, 36), (60, 56, 110), g)
        for x in range(W // 2 % 16, W, 16):
            for y in range(0, H, 2): d.point((x, y), fill=c)
        for y in range(150 % 16, H, 16):
            for x in range(0, W, 2): d.point((x, y), fill=c)
    pix.stars(d, T, H, 0.6 * a, 120, base=(14, 12, 36))
    if a > 0:
        for i, (x, y, rr, c) in enumerate(((90, 60, 150, (70, 40, 120)), (400, 210, 170, (40, 60, 130)), (260, 20, 120, (110, 50, 110)))):
            glow(img, x + 14 * math.sin(T * 0.15 + i), y, rr, c, 0.3 * a, ry=rr * 0.6, power=1.0)
        # 方格纸上用粉笔写的一个个分数，淡淡地往上漂
        r = rng(77)
        for i in range(16):
            num, den = r.choice(('1', '2', '3', '5', '7', '?')), r.choice(('2', '3', '4', '8', '?'))
            x = r.uniform(20, W - 20); y = (r.uniform(0, H + 40) - T * r.uniform(2, 5)) % (H + 40) - 20
            if abs(x - W / 2) < 90 and 80 < y < 220: continue
            al = a * (0.18 + 0.14 * math.sin(T * 0.8 + i))
            c = (150, 140, 210)
            pix.text(img, num, x, y - 8, col=c, out=None, font=FONT_S, alpha=al, shadow=False)
            blend_box(img, (int(x - 5), int(y), int(x + 5), int(y) + 1), c, np.full((1, 10), al * 1.6))
            pix.text(img, den, x, y + 8, col=c, out=None, font=FONT_S, alpha=al, shadow=False)
        fx.motes(img, d, T, 30, (0, 0, W, H), (200, 190, 255), seed=31, drift=(1, -3), glow_a=0.15 * a)


def s_intro(img, d, lt, dur, T, amp):
    bar_y = 150
    # ---- 天亮以后的世界（横线拉开之后）
    open_ = span(lt, 10.25, 11.5)
    by = lerp(bar_y, 176, ease(span(lt, 10.4, 12.0)))
    world = None
    if lt >= 10.25:
        world = Image.new('RGB', (W, H)); wd = ImageDraw.Draw(world)
        sky = mix_stops(DAWN_SKY, GOLD_SKY, span(lt, 11, 16.5))
        sun_y = lerp(by + 80, 158, eout(span(lt, 10.8, 16.5)))
        motifs.sun_plain(world, wd, T, sky=sky, sx=300, sy=sun_y, sr=64, hz=int(round(by)), dip=int(round(6 * span(lt, 12, 15))),
                         birds=lt > 12.5)
        dark_bg(img, d, T, 1, 1 - span(lt, 10.25, 11))
        r = eout(span(lt, 10.7, 12.8)) * 230
        m = np.abs(YY - by) < r * (1 - 0.25 * pix.BAYER)
        img.paste(Image.fromarray(np.where(m[..., None], np.asarray(world), np.asarray(img))))
        d = ImageDraw.Draw(img); d.fontmode = '1'
    else:
        dark_bg(img, d, T, span(lt, 0, 3), span(lt, 0.2, 2.6))
        k = lt - 2.76                                          # 光标拉成横线的一刻，一圈光往外散
        if 0 < k < 0.8:
            r = 10 + k * 260
            d.ellipse([W / 2 - r, bar_y - r * 0.35, W / 2 + r, bar_y + r * 0.35], outline=lerpc(BAR, (14, 12, 36), k / 0.8))

    # ---- 光标和分数线
    if lt < 2.76:
        on = lt > 0.16 and (props.thump(T, 0.5) > 0.05 or lt > 2.3)
        if on:
            glow(img, W / 2, bar_y, 10, BAR, 0.5)
            d.rectangle([W / 2 - 1, bar_y - 1, W / 2 + 1, bar_y + 1], fill=BAR)
    else:
        half = lerp(2, 62, eback(span(lt, 2.76, 3.5)))
        if lt >= 10.25: half = lerp(62, W / 2 + 10, ein(open_) if open_ < 1 else 1)
        pulse = props.thump(T, 0.35)
        ba = 1 - span(lt, 11.9, 12.6)
        if ba > 0:
            glow(img, W / 2, by, half + 16, BAR, (0.25 + 0.25 * pulse) * ba, ry=10)
            bi = Image.new('RGBA', (int(2 * half) + 3, 5), (46, 26, 40, 255))
            ImageDraw.Draw(bi).rectangle([1, 1, int(2 * half) + 1, 3], fill=lerpc(BAR, (255, 255, 255), pulse))
            dpaste(img, bi, W / 2 - half - 1, by - 2, ba)

    # ---- 两个"几"：分子从上面飞来，分母从下面飞来
    num_c, den_c = (W / 2, bar_y - 30), (W / 2, bar_y + 35)
    title_y = 58
    cxs = [W / 2 - 72, W / 2 - 24, W / 2 + 24, W / 2 + 72]
    if lt < 10.4:
        ok1 = blocks_fly(img, d, '几', 3, *num_c, lt, 3.6, 5.9, 1, 'top')
        ok2 = blocks_fly(img, d, '几', 3, *den_c, lt, 6.98, 8.9, 2, 'bottom')
        for ok, (cx, cy), t_ok in ((ok1, num_c, 6.9), (ok2, den_c, 9.9)):
            if ok:
                k = span(lt, t_ok, t_ok + 0.4)
                props.big_text(img, '几', cx, cy, 3, k, **TITLE_KW)
        for i in range(6):                                    # 拼字时周围闪的小星
            t0 = 3.8 + i * 1.05
            pix.twinkle(d, W / 2 + (-70 if i % 2 else 66) + i * 3, bar_y + (-50 if i < 3 else 40) + i * 4, (lt - t0) / 0.6, GOLD_L, 4)
    else:
        f = ease(span(lt, 10.4, 11.9))
        props.big_text(img, '几', lerp(num_c[0], cxs[0], f), lerp(num_c[1], title_y, f) - 14 * math.sin(math.pi * f), 3, 1, **TITLE_KW)
        props.big_text(img, '几', lerp(den_c[0], cxs[3], f), lerp(den_c[1], title_y, f) - 30 * math.sin(math.pi * f), 3, 1, **TITLE_KW)
        for j, (ch, tb) in enumerate((('分', 11.94), ('之', 12.77))):
            k = span(lt, tb - 0.35, tb)
            if k > 0:
                props.big_text(img, ch, cxs[1 + j], lerp(title_y - 40, title_y, eback(k)), 3, clamp(k * 2), **TITLE_KW)
            if lt > tb: pix.twinkle(d, int(cxs[1 + j]) + 18, title_y - 22, (lt - tb) / 0.5, (255, 255, 255), 5)
        ar = props.artist_str()
        if ar: pix.text(img, ar, W / 2, title_y + 38, col=(255, 246, 226), alpha=span(lt, 13.3, 13.9))
    # ---- 片名被风吹散成金色的小点
    if lt > 14.9:
        f = span(lt, 14.9, 16.5)
        bg = world
        mask = pix.BAYER < ease(f) * 1.1 - (XX / W) * 0.3
        mask &= (YY < 140)
        img.paste(Image.fromarray(np.where(mask[..., None], np.asarray(bg), np.asarray(img))))
        d = ImageDraw.Draw(img)
        r = rng(3)
        for i in range(140):
            x0 = r.uniform(W / 2 - 100, W / 2 + 100); y0 = r.uniform(title_y - 24, title_y + 24)
            st = 14.9 + (x0 - (W / 2 - 100)) / 200 * 0.9
            k = lt - st
            if k <= 0: continue
            x = x0 + k * 70 + 6 * math.sin(k * 4 + i); y = y0 - k * 22 + 4 * math.sin(k * 3 + i * 1.3)
            if k < 1.4: d.point((x, y), fill=lerpc(GOLD_L, (255, 200, 120), k / 1.4))


s_intro.no_sub = True


# ---------------------------------------------------------------- 1 记得那天 太阳压着平原
def s_sun(img, d, lt, dur, T, amp):
    dip = int(round(6 + 7 * ease(span(lt, 0.4, 4.5))))
    sy = 168 + 4 * ease(span(lt, 0.4, 4.5))
    fx.LIGHT = ((0.2, -1), (255, 226, 160))
    hf = motifs.sun_plain(img, d, T, sx=290, sy=sy, sr=78, hz=176, dip=dip, glow_a=0.6)
    for x, s_ in ((60, 0.9), (96, 0.6)):
        pix.tree_round(d, x, hf(x) + 1, s_, (130, 84, 70), (160, 104, 80), (100, 64, 56))
    # 他背对着我们站在土路上，影子拖向镜头
    tfill(img, 'polygon', [(282, 230), (298, 230), (318, H), (262, H)], (110, 64, 40), 0.45)
    person_s(img, 'boy', 290, 230, 2, view='back', shade=(0.86, 0.8, 0.82))
    for i in range(0, W, 6):
        motifs.wheat(d, i + 3 * math.sin(i), H - 1 - (i % 4) * 3, 16 + (i * 7) % 9, T, wind=0.8, ph=i)
    fx.motes(img, d, T, 34, (0, 60, W, 240), (255, 236, 180), seed=1, drift=(5, -2))
    fx.fg(img, T, 'wheat', (70, 40, 34), (255, 200, 120), (0, 1), 3, seed=2, h=1.2)
    # 回忆的样子：开头是旧照片的颜色，四角暗下来，慢慢变成彩色
    k = 1 - ease(span(lt, 0.3, 1.8))
    if k > 0:
        img.paste(props.sepia(img, k))
        pix.vig(img, 0.9 * k, (40, 24, 20))


# ---------------------------------------------------------------- 2 风慢慢吹 没有人掉眼泪
def _fence(img, d, t, T):
    fx.LIGHT = ((-1, -0.4), (255, 222, 150))
    motifs.sun_plain(img, d, T, sky=GOLD_SKY, sx=110, sy=150, sr=40, hz=168, dip=2, road=False, grass_on=False, birds=False)
    pix.hills(d, 214, 6, 0.012, 1.0, (190, 160, 70))
    pix.hills(d, 222, 5, 0.02, 2.0, (150, 140, 60))
    # 风吹草浪：一道道亮一点的草往右边跑
    for x in range(0, W, 2):
        wave = math.sin(x * 0.045 - T * 3.2)
        h = 5 + 3 * wave
        lean = 2 + 2 * (wave > 0.3)
        c = (210, 196, 100) if wave > 0.5 else (170, 160, 72)
        d.line([(x, H), (x + lean, H - 12 - h)], fill=c)
        if x % 6 == 0: d.line([(x + 1, H), (x + 1 + lean, H - 20 - h)], fill=lerpc(c, (255, 240, 160), 0.3))
    # 木栅栏和坐在上面的四个人
    rail = 192
    for x in range(110, 400, 28):
        d.rectangle([x, rail - 6, x + 3, 228], fill=(120, 80, 56)); d.point((x + 1, rail - 6), fill=(170, 120, 80))
    d.rectangle([104, rail, 404, rail + 3], fill=(150, 100, 66)); d.rectangle([104, rail + 14, 404, rail + 16], fill=(130, 86, 58))
    who = [('boy', 'f1', 160, 'laugh'), ('boy', 'young', 212, 'happy'), ('girl', 'f2', 264, 'laugh'), ('boy', 'f3', 316, 'smile')]
    for i, (w_, age, x, ex) in enumerate(who):
        bob = round(props.thump(T + i * 0.12, 0.3) * 2)
        person_s(img, w_, x, rail + 18 - bob, 2, age, view='front', pose='sit', expr=ex)
    # 右边一棵离镜头很近的大树，叶子被夕阳照亮一边
    d.rectangle([446, 60, 462, H], fill=(70, 46, 40)); d.line([(447, 60), (447, H)], fill=(160, 104, 70))
    for bx, by, br in ((430, 40, 34), (470, 20, 36), (400, 10, 26), (460, 70, 28)):
        sw = math.sin(T * 1.2 + bx) * 1.5
        d.ellipse([bx - br + sw, by - br, bx + br + sw, by + br], fill=(60, 96, 60))
    for bx, by, br in ((430, 40, 34), (470, 20, 36), (400, 10, 26), (460, 70, 28)):
        sw = math.sin(T * 1.2 + bx) * 1.5
        d.ellipse([bx - br + sw, by - br, bx - br * 0.2 + sw, by + br * 0.4], fill=(170, 170, 80))
        d.arc([bx - br + sw, by - br, bx + br + sw, by + br], 150, 230, fill=(255, 214, 120))
    motifs.seeds(img, d, T, 26, (0, 40, W, 200), wind=34, seed=4)
    fx.motes(img, d, T, 24, (0, 40, 300, 220), (255, 236, 180), seed=2)
    fx.fg(img, T, 'grass', (60, 70, 40), (255, 210, 120), (0,), 3, seed=4, h=1.1)


def _wind_face(img, d, t, T):
    pix.sky(img, GOLD_SKY)
    glow(img, 400, 150, 160, motifs.SUN_MID, 0.6)
    glow(img, 400, 150, 60, motifs.SUN_HI, 0.5)
    props.bokeh(img, T, 10, (GOLD_L, (255, 200, 150), (255, 236, 200)), seed=3, a=0.25)
    fx.godrays(img, 400, 150, T, 8, (255, 236, 190), 0.06, spread=math.pi * 0.9, center=math.pi, length=380)
    eyes = motifs.lit_bust(img, 'boy', 236, 52, 4, 'happy', (1, -0.4), (255, 222, 150))
    # 风把头发吹得一翘一翘
    for k in range(5):
        bx, by = 200 + k * 9, 52 + (k % 2) * 3
        sw = math.sin(T * 6 + k) * 3
        d.line([(bx, by + 4), (bx + 8 + sw, by - 4 - k % 3)], fill=(38, 32, 42), width=3)
    motifs.seeds(img, d, T, 20, (0, 0, W, 230), wind=40, seed=9)
    # 一朵蒲公英绒毛从他脸颊边飘过——没有眼泪
    k = span(t, 0.8, 2.6)
    if 0 < k < 1:
        x = lerp(150, 330, k); y = eyes[0][1] + 18 + 8 * math.sin(k * 6)
        d.point((x, y), fill=(255, 255, 255)); d.point([(x - 1, y - 1), (x + 1, y - 1), (x, y - 2)], fill=(240, 236, 220))
        if 0.35 < k < 0.6: pix.twinkle(d, int(eyes[0][0]), int(eyes[0][1] + 12), (k - 0.35) / 0.25, (255, 255, 255), 3)
    fx.fg(img, T, 'leaves', (40, 60, 44), (255, 210, 130), (0,), 3, seed=6)


def s_wind(img, d, lt, dur, T, amp):
    shots(img, lt, [(0, _fence), (3.3, _wind_face)], 0.4, T=T)


# ---------------------------------------------------------------- 3 一切好美 好到我可以不用说话
@lru_cache(None)
def _meadow():
    im = Image.new('RGB', (W + 40, H + 40), (132, 176, 82)); d = ImageDraw.Draw(im)
    r = rng(12)
    for _ in range(2400):
        x, y = r.uniform(0, W + 40), r.uniform(0, H + 40)
        c = r.choice(((112, 158, 70), (150, 192, 92), (176, 206, 104), (120, 166, 74)))
        d.line([(x, y), (x + r.uniform(-1, 1), y - r.uniform(2, 4))], fill=c)
    for _ in range(90):
        x, y = r.uniform(0, W + 40), r.uniform(0, H + 40)
        pix.flower(d, x, y, r.choice(((255, 255, 255), (255, 214, 90), (255, 170, 190), (200, 180, 255))), r.choice((0, 0, 2)), h=0)
    return im


def _lying(img, d, t, T):
    ox, oy = 20 - t * 4, 20 - t * 2
    img.paste(_meadow().crop((int(-ox + 20), int(-oy + 20), int(-ox + 20) + W, int(-oy + 20) + H)))
    pix.grade(img, mul=(1.06, 0.98, 0.86), add=(16, 6, -6))
    # 他躺在草地上（从正上方往下看），两手张开
    fx.LIGHT = ((-0.8, -1), (255, 236, 180))
    fx.contact(img, 242, 190, 26, 0.3, (40, 60, 30), 6)
    person_s(img, 'boy', 240, 190, 2, view='front', arms='spread', expr='closed')
    for i in range(14):                                        # 树叶缝里漏下来的光斑
        r = rng(i * 5)
        cx = (r.uniform(0, W) + t * 3) % W; cy = r.uniform(0, H)
        rr = r.uniform(6, 14) * (0.85 + 0.15 * math.sin(T * 1.5 + i))
        glow(img, cx, cy, rr, (255, 246, 200), 0.3, ry=rr * 0.6, power=0.6)
    pix.petals(d, T, 26, seed=3, wind=16, speed=14)
    for i in range(3):
        pix.butterfly(d, int(120 + i * 110 + 20 * math.sin(T + i)), int(60 + i * 40 + 10 * math.cos(T * 1.3 + i)), T, ((255, 200, 120), (255, 170, 200), (200, 220, 255))[i], i)
    fx.fg(img, T, 'flowers', (60, 110, 50), (255, 240, 180), (0, 1), 3, seed=8)


def _hill_sunset(img, d, t, T, sky=GOLD_SKY):
    motifs.sun_plain(img, d, T, sky=sky, sx=380, sy=160, sr=46, hz=176, dip=3, road=False, grass_on=False, birds=True)
    d.polygon([(0, 196), (60, 186), (160, 184), (260, 200), (330, 228), (W, 240), (W, H), (0, H)], fill=(150, 108, 64))
    d.polygon([(0, 204), (80, 196), (170, 196), (250, 214), (W, 252), (W, H), (0, H)], fill=(120, 86, 54))
    for x in range(0, W, 3):
        y = 196 if x < 160 else 196 + (x - 160) * 0.18
        d.line([(x, y + 6), (x + 1, y + 2)], fill=(176, 130, 70))


def _speechless(img, d, t, T):
    fx.LIGHT = ((1, -0.3), (255, 222, 150))
    _hill_sunset(img, d, t, T)
    expr = 'surprised' if 0.6 < t < 2.4 else 'smile'
    person_s(img, 'boy', 140, 194, 2, view='side', pose='sit', expr=expr)
    a = span(t, 0.6, 0.9)
    pop = span(t, 2.6, 3.1)
    if a > 0 and pop < 1:
        motifs.bubble(img, d, 176, 112, 52, 26, (156, 150), a, 3, T, pop)
    for i in range(5):                                         # 气泡化成往上飘的小光点
        k = t - 2.7 - i * 0.12
        if k > 0:
            x = 170 + i * 6 + 10 * math.sin(k * 2 + i); y = 112 - k * 22
            pix.glow(img, x, y, 5, GOLD_L, 0.5 * clamp(1 - k / 2.5))
            d.point((x, y), fill=(255, 250, 200))
    pix.fireflies(img, d, T, 8, (200, 150, 470, 230), seed=2)
    fx.motes(img, d, T, 20, (180, 80, W, 220), (255, 236, 180), seed=5)
    fx.fg(img, T, 'grass', (80, 50, 40), (255, 200, 120), (1,), 3, seed=9, h=1.2)


def _dusk(img, d, t, T):
    f = span(t, 0, 3.0)
    pix.sky(img, mix_stops(DUSK_SKY, NIGHT_SKY, f))
    pix.stars(d, T, 190, span(t, 0.6, 3.4), 200)
    motifs.milky_way(img, T, 0.5 * span(t, 1.0, 3.8)); d = ImageDraw.Draw(img)
    glow(img, 380, 190, 120, (255, 150, 120), 0.4 * (1 - f))
    fx.mountains(img, 200, [(4, 40, 0.6, lerpc((90, 70, 110), (30, 28, 60), f)), (6, 22, 0.55, lerpc((70, 50, 80), (22, 20, 46), f))])
    for i in range(18):                                        # 远处小镇的灯
        r = rng(i)
        x = 230 + r.uniform(0, 240); y = 196 + r.uniform(0, 6) + (x - 230) * 0.05
        if math.sin(T * 0.8 + i) > -0.6: d.point((x, y), fill=lerpc((120, 90, 80), (255, 210, 140), span(t, 0.5, 2)))
    d.polygon([(0, 196), (60, 186), (160, 184), (260, 200), (330, 228), (W, 240), (W, H), (0, H)], fill=lerpc((90, 60, 60), (24, 20, 40), f))
    person_s(img, 'boy', 140, 194, 1, view='side', pose='sit', expr='smile', shade=(0.3, 0.3, 0.45))
    if t > 1.6: pix.meteor(d, t, 1.8, 360, 30, -120, 60, 1.0)
    pix.fireflies(img, d, T, 10, (0, 150, 300, 240), seed=6)
    k = span(t, 3.2, 4.8)
    if k > 0:                                                  # 右边慢慢亮起一点金光
        glow(img, W + 6, 150, 120 * k, motifs.SUN_MID, 0.6 * k)
        glow(img, W - 2, 150, 30 * k, motifs.SUN_HI, 0.7 * k)


def s_beautiful(img, d, lt, dur, T, amp):
    shots(img, lt, [(0, _lying), (4.3, _speechless), (8.4, _dusk)], 0.5, T=T)


# ---------------------------------------------------------------- 4 金色的侧脸 踩着全白球鞋
def _profile(img, d, t, T):
    pix.sky(img, ((0, (150, 110, 160)), (0.5, (250, 170, 120)), (1, (255, 214, 150))))
    glow(img, 440, 100, 220, motifs.SUN_MID, 0.75)
    glow(img, 440, 100, 70, motifs.SUN_HI, 0.85)
    for i in range(5):                                         # 镜头光晕
        u = 0.25 + i * 0.16
        x, y = lerp(440, 60, u), lerp(100, 230, u)
        glow(img, x, y, 6 + i * 3, (255, 236, 190), 0.22)
    props.bokeh(img, T, 12, ((255, 236, 180), (255, 200, 140), (255, 250, 220)), seed=7, a=0.22, rmin=4, rmax=12)
    fx.godrays(img, 440, 100, T, 9, (255, 240, 200), 0.07, spread=math.pi * 0.8, center=math.pi * 0.85, length=460)
    motifs.profile(img, d, 150 + t * 3, 2, 1.3, T, 1.0)
    fx.motes(img, d, T, 50, (0, 0, W, H), (255, 246, 210), seed=3, drift=(6, -4), glow_a=0.3)
    fx.fg(img, T, 'leaves', (44, 56, 44), (255, 200, 140), (0,), 3, seed=3)


def _shoes(img, d, t, T):
    pix.sky(img, ((0, (240, 190, 110)), (0.5, (220, 170, 90)), (1, (200, 150, 80))), 0, 150)
    props.bokeh(img, T, 10, ((255, 230, 160), (255, 210, 120)), seed=2, a=0.3, box=(0, 0, W, 150))
    pix.sky(img, ((0, (232, 200, 140)), (1, (210, 170, 110))), 150, H)
    fx.tex(img, (0, 150, W, H), 7, seed=21, scale=2)
    glow(img, 470, 10, 160, (255, 236, 170), 0.5)
    period = 0.836
    step = 70
    v = step / (period / 2)
    off = t * v
    for k in range(-1, 12):                                     # 小石子和草
        x = (k * 47 - off) % (W + 60) - 30
        d.rectangle([x, 214 + (k % 3) * 9, x + 3, 216 + (k % 3) * 9], fill=(180, 140, 96))
        pix.grass(d, 152, (150, 150, 70), (190, 180, 90), T, x0=int(x), x1=int(x) + 20, seed=k, hmax=6)
    d.line([(0, 152), (W, 152)], fill=(196, 160, 100))
    base = 206
    cx = 240
    step = 110
    for j in sorted(range(2), key=lambda j: ((t / period) + j * 0.5) % 1 >= 0.5):
        p = ((t / period) + j * 0.5) % 1
        if p < 0.5:
            x = cx + step / 2 - (p / 0.5) * step; lift = 0
        else:
            u = (p - 0.5) / 0.5
            x = cx - step / 2 + u * step; lift = math.sin(math.pi * u) * 16
        if p < 0.06:                                            # 落地扬起一点金色的尘
            for q in range(5):
                d.point((x - 10 - q * 4, base - 2 - q % 2 - p * 60), fill=(255, 230, 170))
        far = ((t / period) + j * 0.5) % 1 >= 0.5
        fx.contact(img, x, base + 1, 44 - lift, 0.45 * (1 - lift / 30), (120, 80, 50), 5)
        motifs.big_shoe(img, d, x - 40, base - lift - (8 if far else 0), 4, False, leg=200)
        if p < 0.5 and int(T * 6 + j) % 3 == 0:
            pix.twinkle(d, int(x + 6), int(base - 40), (T * 3 + j) % 1, (255, 255, 255), 4)
    # 裙摆的下沿
    sw = math.sin(t / period * math.pi * 2) * 4
    d.polygon([(150 + sw, 0), (330 + sw, 0), (322 - sw, 36), (296, 42), (270, 36), (240, 44), (210, 36), (184, 42), (158 + sw, 36)], fill=pix.MUST)
    d.line([(158 + sw, 36), (184, 42), (210, 36), (240, 44), (270, 36), (296, 42), (322 - sw, 36)], fill=pix.MUST_S, width=2)
    fx.motes(img, d, T, 26, (0, 0, W, 200), (255, 240, 200), seed=7)
    fx.fg(img, T, 'grass', (110, 90, 50), (255, 220, 140), (0, 1), 4, seed=5, h=0.8)


def s_golden(img, d, lt, dur, T, amp):
    shots(img, lt, [(0, _profile), (3.4, _shoes)], 0.35, T=T)


# ---------------------------------------------------------------- 5 风继续吹 世界继续作业
def s_world(img, d, lt, dur, T, amp):
    fx.LIGHT = ((-1, -0.7), (255, 246, 220))
    pix.sky(img, NOON_SKY)
    for i in range(6):                                         # 云飞快地跑（延时摄影）
        x = (i * 120 - lt * 90) % (W + 160) - 120
        pix.cloud(d, x, 20 + (i % 3) * 22, 2 if i % 2 else 1, (255, 255, 255), (220, 232, 246))
    pix.hills(d, 140, 8, 0.01, 0.5, (150, 196, 150))
    for i, x in enumerate((60, 120, 410)):                     # 风车转得飞快
        by = 136 + 4 * math.sin(x * 0.01 + 0.5)
        d.line([(x, by), (x, by - 34)], fill=(240, 244, 250), width=2)
        a0 = lt * 9 + i
        for k in range(3):
            a = a0 + k * 2.094
            d.line([(x, by - 34), (x + math.cos(a) * 16, by - 34 + math.sin(a) * 16)], fill=(250, 252, 255), width=2)
        d.ellipse([x - 2, by - 36, x + 2, by - 32], fill=(200, 204, 214))
    pix.city(img, d, 182, 4, 0, (170, 180, 206), (250, 240, 200), 30, 70, 0.2, T, edge=(150, 160, 190))
    # 钟楼：指针转得飞快
    d.rectangle([186, 70, 222, 182], fill=(206, 186, 160)); d.polygon([(182, 72), (204, 44), (226, 72)], fill=(170, 90, 80))
    props.clock(d, 204, 96, 13, lt * 4, lt * 48)
    # 高架桥上的电车来回穿过
    d.rectangle([0, 150, W, 154], fill=(120, 120, 140))
    for x in range(0, W, 40): d.rectangle([x + 10, 154, x + 14, 182], fill=(120, 120, 140))
    tx = (lt * 520) % (W + 400) - 100
    props.train(img, d, tx, 150, T, cars=2, s=0.5, people=True, rust=0)
    # 街上
    pix.sky(img, ((0, (190, 186, 196)), (1, (150, 146, 160))), 182, H)
    for x in range(-20, W, 40): d.rectangle([x + (lt * 0) % 40, 206, x + 20, 207], fill=(236, 230, 210))
    # 路人和单车：带残影飞快地经过
    for i in range(12):
        r = rng(i * 5)
        sp = r.choice((-1, 1)) * r.uniform(160, 260)
        x = (r.uniform(0, W + 80) + lt * sp) % (W + 80) - 40
        y = 214 + (i % 3) * 8
        who = r.choice(('boy', 'girl')); age = r.choice(('f1', 'f3')) if who == 'boy' else 'f2'
        for k in range(3, 0, -1):
            props.ghost(img, who, x - sp * 0.03 * k, y, 1, 0.5 - k * 0.12, age, 'side', 'walk', 'smile', sp < 0, ph=int(T * 10 + i))
        person_s(img, who, x, y, 1, age, 'side', 'walk', int(T * 10 + i), 'smile', flip=sp < 0)
    for i in range(2):
        bx = (i * 260 + lt * 300) % (W + 120) - 60
        motifs.bicycle(d, bx, 252, T * 3, 1)
    # 只有他和她一动不动，影子跟着太阳转
    ang = lerp(-0.9, 0.9, lt / dur)
    for x in (196, 284):
        tfill(img, 'polygon', [(x - 6, 236), (x + 6, 236), (x + 6 + 60 * math.sin(ang), 244), (x - 6 + 60 * math.sin(ang), 244)], (60, 56, 80), 0.35)
    fx.contact(img, 196, 236, 16, 0.4); fx.contact(img, 284, 236, 16, 0.4)
    person_s(img, 'boy', 196, 236, 2, view='side', expr='smile')
    person_s(img, 'girl', 284, 236, 2, view='side', expr='smile', flip=True)
    props.leaves(d, T, 20, wind=120, speed=30, seed=2, cols=((120, 190, 90), (170, 210, 110)))
    k = span(lt, 4.6, 5.2)
    if k > 0: pix.put(img, 'heart', 240, 172 - 6 * eout(k), 2, alpha=k)


# ---------------------------------------------------------------- 6 那么确定 我知道那就是你
def _compass(img, d, t, T):
    pix.sky(img, ((0, (60, 50, 90)), (1, (120, 90, 120))))
    props.bokeh(img, T, 18, ((255, 200, 120), (255, 160, 140), (140, 200, 255), (255, 236, 180)), seed=11, a=0.35, rmin=10, rmax=26)
    lock = 1.9
    spin = lambda u: u * 18 + 3 * math.sin(u * 13)
    a0 = spin(lock - 0.6)
    target = math.pi / 2 + 2 * math.pi * (math.floor((a0 - math.pi / 2) / (2 * math.pi)) + 2)
    if t < lock - 0.6: ang = spin(t)
    elif t < lock: ang = lerp(a0, target, eout((t - (lock - 0.6)) / 0.6))
    else:
        k = t - lock
        ang = target + 0.35 * math.exp(-k * 5) * math.sin(k * 25)
    cx, cy = 240, 120
    motifs.compass(img, d, cx, cy, 58, ang, T, glow_a=0.35 * span(t, lock, lock + 0.2) * (1 - span(t, lock + 0.2, lock + 1.2)))
    # 捏着罗盘的两只手：有明暗，下面露出天蓝色的袖口
    def hands(l, ld):
        for k in range(3):
            motifs.finger(ld, cx - 72, cy - 10 + k * 13, 16, 10)
            motifs.finger(ld, cx + 58, cy - 6 + k * 13, 16, 10, True)
        ld.polygon([(cx - 97, cy - 19), (cx - 69, cy - 23), (cx - 65, H), (cx - 121, H)], fill=OUT)
        ld.polygon([(cx - 96, cy - 18), (cx - 70, cy - 22), (cx - 66, H), (cx - 120, H)], fill=SKIN)
        ld.polygon([(cx + 97, cy - 15), (cx + 71, cy - 19), (cx + 69, H), (cx + 125, H)], fill=OUT)
        ld.polygon([(cx + 96, cy - 14), (cx + 72, cy - 18), (cx + 70, H), (cx + 124, H)], fill=SKIN)
        for sg in (-1, 1):
            ld.polygon([(cx + sg * 64, 220), (cx + sg * 128, 220), (cx + sg * 132, H), (cx + sg * 62, H)], fill=pix.SKY_T)
            ld.line([(cx + sg * 64, 220), (cx + sg * 128, 220)], fill=(200, 230, 250), width=2)
    lay = fx.lit_layer(hands, (0.4, -1), 0.3, (255, 236, 200))
    img.paste(lay, (0, 0), lay)
    if t > lock:                                               # 锁定的一圈波纹
        k = t - lock
        r = 58 + k * 70
        if k < 0.7: d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=lerpc((255, 250, 220), (120, 90, 120), k / 0.7), width=2)
        pix.twinkle(d, cx + 46, cy, k / 0.5, (255, 255, 255), 6)


def _crowd(img, d, t, T):
    pan = -200 * ease(span(t, 0, 1.4))
    pix.sky(img, ((0, (210, 214, 226)), (1, (236, 230, 220))), 0, 170)
    pix.city(img, d, 170, 9, -pan * 0.3, (200, 200, 214), None, 40, 110, 0, T, edge=(190, 190, 206))
    pix.sky(img, ((0, (200, 196, 200)), (1, (176, 170, 180))), 170, H)
    gx = 440 + pan
    for i in range(12):
        r = rng(i * 3 + 1)
        sp = r.choice((-1, 1)) * r.uniform(20, 40)
        x = r.uniform(0, 700) + pan + t * sp
        if abs(x - gx) < 44: continue
        y = 210 + (i % 4) * 7
        who = r.choice(('boy', 'girl')); age = r.choice(('f1', 'f3')) if who == 'boy' else 'f2'
        person_s(img, who, x, y, 2, age, 'side', 'walk', int(T * 6 + i), 'smile', flip=sp < 0)
    arr = motifs.gray(np.asarray(img), 0.85)
    img.paste(Image.fromarray(arr.astype(np.uint8)))
    d = ImageDraw.Draw(img)
    glow(img, gx, 190, 70, (255, 220, 140), 0.7 + 0.2 * props.thump(T))
    turned = t > 1.9
    person_s(img, 'girl', gx, 230, 2, view='front' if turned else 'back', expr='smile' if t < 2.6 else 'happy')
    if turned:
        k = span(t, 2.4, 2.8)
        pix.put(img, 'heart', gx, 150 - 6 * eout(k), 2, alpha=k)
    for i in range(6):
        pix.twinkle(d, int(gx + math.cos(i + T) * 30), int(190 + math.sin(i * 2 + T) * 30), (T * 0.8 + i / 6) % 1, (255, 240, 200), 3)


def _heartbeat(img, d, t, T):
    pix.sky(img, ((0, (255, 170, 190)), (1, (255, 214, 220))))
    cx, cy = 240, 130
    for k in range(24):                                        # 漫画里的放射线
        a = k * math.pi / 12 + t * 0.2
        d.polygon([(cx, cy), (cx + math.cos(a) * 400, cy + math.sin(a) * 400), (cx + math.cos(a + 0.08) * 400, cy + math.sin(a + 0.08) * 400)],
                  fill=(255, 196, 206))
    motifs.lit_bust(img, 'boy', 240, 40, 4, 'surprised' if t < 1.2 else 'smile', (-0.6, -1), (255, 240, 240))
    for ex in (196, 284):
        blend_box(img, (ex - 8, 120, ex + 8, 126), pix.BLUSH, np.full((6, 16), 0.7))
    beat = props.thump(T, 0.3)
    grow = ein(span(t, 3.3, 4.1))
    s = 1.1 + 0.35 * beat + grow * 14
    hy = lerp(200, cy, grow)
    glow(img, 240, hy, 40 * s, (255, 120, 150), 0.4)
    d.polygon(heart_scale(240, hy, s * 1.1), fill=OUT)
    d.polygon(heart_scale(240, hy, s), fill=(240, 70, 100))
    if s < 4: d.ellipse([240 - 9 * s, hy - 7 * s, 240 - 5 * s, hy - 3 * s], fill=(255, 190, 200))


def heart_scale(cx, cy, s):
    return pix.heart_poly(cx, cy, s)


def s_sure(img, d, lt, dur, T, amp):
    shots(img, lt, [(0, _compass), (3.4, _crowd), (6.9, _heartbeat)], 0.35, T=T)
