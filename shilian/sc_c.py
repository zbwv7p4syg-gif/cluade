"""永不失联的爱 · 第二段主歌。签名都是 (img, d, lt, dur, T, A)。

他一个人走过一起看流星的天台，回忆里的两人还坐在楼边；窗外四季飞快轮转，日历一页页撕掉；
她站在雨里，满街灰伞从身边涌过，他在想法云里担心；游乐园的回忆：棉花糖、气球和摩天轮；
两扇窗看着同一个月亮；俯瞰的人海越拉越远，变成一片海；她走远了又回头；他撑着伞站在路灯下，雨、雪、花瓣轮流落下，他一直都在。
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
from props import shots, shake, dpaste, mix_stops, thump, ghost
from pix import (W, H, FONT, FONT_S, OUT, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky, stars,
                 person, wph, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, BAYER)
from kit import NIGHT, DEEP, DUSK, DAY, GOLDEN, RAINY

YY, XX = np.mgrid[0:H, 0:W]


def s_roof(img, d, lt, dur, T, A):
    """走过陪你看流星的天台：他一个人慢慢走过楼顶，楼边坐着回忆里的两人在看流星，他走近时回忆淡去"""
    kit.night(img, d, T, NIGHT, 220)
    kit.galaxy(img, 0.6, 2, -0.3, 40)
    kit.meteors(d, T, 1.6, 3, (0, 0, W, 120))
    pix.city(img, d, 250, 31, 0, (26, 30, 74), (150, 140, 120), 60, 150, 0.15, T)
    sig.rooftop(d, -10, W + 10, 206, (30, 30, 62), (70, 70, 120), (255, 214, 140), T, True, 5)
    a = 0.65 * clamp((3.8 - lt) / 1.2) * (0.8 + 0.2 * math.sin(T * 3))
    if a > 0:
        ghost(img, 'boy', 330, 200, 2, a, view='side', pose='sit', expr='happy', flip=False)
        ghost(img, 'girl', 362, 200, 2, a, view='side', pose='sit', expr='laugh', flip=True)
        for k in range(3):
            sparkle(d, int(320 + k * 30), int(120 + 10 * math.sin(T * 2 + k)), T + k, (200, 220, 255), 2)
    hx = lerp(40, 290, eout(span(lt, 0, 4.6)))
    walking = lt < 4.4
    person(img, 'boy', hx, 206, view='side', pose='walk' if walking else 'stand', ph=wph(lt, 5), expr='down' if walking else 'sad',
           arms='auto', s=2)
    sig.can(d, 420, 202, 1, flip=True)
    vig(img, 0.45)


SEASONS = [
    dict(sky=((0, (150, 200, 250)), (1, (230, 240, 255))), ground=(120, 190, 110), tree=(255, 180, 200), fall='petal', name='春'),
    dict(sky=((0, (80, 160, 240)), (1, (200, 236, 255))), ground=(80, 170, 80), tree=(70, 160, 70), fall=None, name='夏'),
    dict(sky=((0, (240, 160, 110)), (1, (255, 220, 160))), ground=(190, 140, 70), tree=(230, 120, 50), fall='leaf', name='秋'),
    dict(sky=((0, (150, 160, 190)), (1, (220, 226, 240))), ground=(240, 244, 250), tree=(250, 250, 255), fall='snow', name='冬'),
]


def season_view(k, T, w, h):
    s = SEASONS[k % 4]
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    sky(im, s['sky'], 0, H, 4)
    if k % 4 == 1: d.ellipse([60, 20, 84, 44], fill=(255, 246, 200)); glow(im, 72, 32, 30, (255, 250, 200), 0.5)
    d.rectangle([0, h - 30, W, H], fill=s['ground'])
    d.rectangle([w * 0.6 - 3, h - 70, w * 0.6 + 3, h - 30], fill=(110, 76, 56))
    if k % 4 != 3: pix.tree_round(d, w * 0.6, h - 30, 1.6, s['tree'], lerpc(s['tree'], (255, 255, 255), 0.3), (110, 76, 56))
    else:
        d.ellipse([w * 0.6 - 24, h - 92, w * 0.6 + 24, h - 52], fill=(250, 250, 255))
    if s['fall'] == 'petal': pix.petals(d, T, 30, x1=w, y1=h)
    elif s['fall'] == 'leaf': props.leaves(d, T, 30, box=(0, -10, w, h))
    elif s['fall'] == 'snow': pix.snow(d, T, 60, y1=h)
    return im.crop((0, 0, w, h))


def s_wait(img, d, lt, dur, T, A):
    """熬过失去你漫长的等待：他坐在窗边，窗外春夏秋冬飞快地换，墙上的日历一页页撕掉，钟转个不停"""
    img.paste((70, 62, 92), (0, 0, W, H))
    for x in range(0, W, 20): d.line([(x, 0), (x, 200)], fill=(76, 68, 100))
    d.rectangle([0, 200, W, H], fill=(96, 74, 70))
    wx0, wy0, wx1, wy1 = 250, 30, 440, 170
    ph = lt / dur * 4
    k = int(ph); f = ph - k
    cur = season_view(k, T, wx1 - wx0, wy1 - wy0)
    if f > 0.75:
        nxt = season_view(k + 1, T, wx1 - wx0, wy1 - wy0)
        m = pix.bayer(cur.height, cur.width) < (f - 0.75) / 0.25
        a = np.where(m[..., None], np.asarray(nxt), np.asarray(cur)); cur = Image.fromarray(a)
    img.paste(cur, (wx0, wy0))
    d.rectangle([wx0 - 5, wy0 - 5, wx1 + 5, wy1 + 5], outline=(160, 130, 110), width=5)
    d.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=(160, 130, 110), width=3)
    d.rectangle([wx0 - 12, wy1 + 5, wx1 + 12, wy1 + 11], fill=(180, 150, 126))
    glow(img, (wx0 + wx1) / 2, (wy0 + wy1) / 2, 150, lerpc(SEASONS[k % 4]['sky'][1][1], (255, 255, 255), 0.3), 0.15)
    # 日历和钟
    day = 1 + int(lt * 9) % 30
    sig.calendar(img, d, 60, 36, day, ['三月', '七月', '十月', '一月'][k % 4], (lt * 9) % 1)
    props.clock(d, 160, 66, 24, T * 4, T * 48, rim=(150, 112, 80))
    # 桌子、手机和他
    d.rectangle([170, 222, 196, 228], fill=(120, 86, 64)); d.rectangle([172, 228, 175, 250], fill=(100, 70, 54))
    d.rectangle([192, 228, 195, 250], fill=(100, 70, 54)); d.rectangle([170, 196, 174, 222], fill=(120, 86, 64))
    d.rectangle([226, 206, 330, 212], fill=(150, 110, 80)); d.rectangle([232, 212, 238, 250], fill=(120, 86, 64))
    d.rectangle([318, 212, 324, 250], fill=(120, 86, 64))
    d.rectangle([250, 202, 262, 206], fill=(40, 40, 54))
    person(img, 'boy', 190, 246, view='side', pose='sit', expr='down', arms='lap', s=2)
    sig.bars(d, 250, 194, 0, 1)
    vig(img, 0.45)


def s_lonely(img, d, lt, dur, T, A):
    """好担心没人懂你的无奈：她一个人站在雨里，满街的灰伞从身边涌过；角落里他的想法云，满脸担心"""
    sky(img, RAINY, 0, H, 5)
    pix.city(img, d, 190, 9, lt * 5, (34, 38, 64), (200, 190, 140), 50, 140, 0.25, T)
    d.rectangle([0, 190, W, H], fill=(44, 46, 70))
    props.reflect(img, 190, 80, T, (20, 22, 40), 0.5)
    for row, (y, sp, s) in enumerate(((210, 90, 1), (262, -120, 2))):
        for k in range(8):
            x = (k * 76 + row * 40 + lt * sp) % (W + 120) - 60
            if row == 1 and abs(x - 240) < 34: continue
            im = props_gray('boy' if k % 2 else 'girl', s, sp < 0)
            dpaste(img, im, x - pix.CX * s, y - pix.FY * s)
            kit.umbrella(d, x, y - 48 * s - 4, (110, 112, 128), (84, 86, 100), 14 * s)
            d.line([(x, y - 48 * s + 9 * s - 4), (x, y - 30 * s)], fill=OUT)
        if row == 0:
            person(img, 'girl', 240, 236, view='front', pose='stand', expr='sad', arms='behind', s=2)
            pix.rain(d, T, 220, 260, 120, 236, 10, (170, 190, 240), 260, -1, 5, 6)
    kit.rain_layer(img, d, T, 150, (130, 150, 210))
    # 他的想法云
    f = eback(span(lt, 1.2, 1.6))
    if f > 0:
        kit.thought(d=d, img=img, x=90, y=56, w=70 * f, h=40 * f, T=T)
        if f > 0.8:
            hi = props.head_img('boy', expr='worried', s=2)
            dpaste(img, hi, 90 - hi.width / 2, 56 - hi.height / 2 - 4)
            kit.pop(d, 112, 44, 'sweat', T)
    vig(img, 0.5)


@lru_cache(None)
def props_gray(who, s, flip):
    im = pix.char_img(who, 'young', 'side', 'walk', 0, 'neutral', 'down')
    a = np.array(im).astype(float)
    g = a[..., :3] @ np.array([0.3, 0.59, 0.11])
    a[..., :3] = g[..., None] * 0.4 + 60
    im = Image.fromarray(a.astype(np.uint8))
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im.resize((im.width * s, im.height * s), Image.NEAREST)


def s_kid(img, d, lt, dur, T, A):
    """离开我谁还把你当小孩：游乐园的回忆，摩天轮和彩灯，他递给她一朵棉花糖，她举着气球蹦起来；最后褪成老照片"""
    sky(img, DUSK, 0, H, 6)
    stars(d, T, 120, 0.6, 100)
    kit.ferris(img, d, 340, 100, 70, T)
    # 一串彩灯
    for k in range(30):
        x = k * 17; y = 30 + 14 * math.sin(k * 0.37 + 1) ** 2
        c = ((255, 120, 150), (255, 220, 90), (120, 220, 255))[k % 3]
        if (int(T * 3) + k) % 4: d.rectangle([x, y, x + 1, y + 1], fill=c); glow(img, x, y, 4, c, 0.3)
    # 旋转木马的顶
    d.polygon([(60, 140), (150, 140), (105, 110)], fill=(240, 120, 140)); d.rectangle([60, 140, 150, 146], fill=(255, 220, 120))
    for k in range(5): d.line([(66 + k * 20, 146), (66 + k * 20, 196)], fill=(250, 230, 200))
    d.rectangle([56, 196, 154, 202], fill=(200, 90, 120))
    d.rectangle([0, 202, W, H], fill=(90, 76, 96))
    hop = abs(math.sin(lt * 4)) * 10 if lt > 1.6 else 0
    gx, gy = 280, 236 - hop
    person(img, 'boy', 230, 236, view='side', pose='stand', expr='happy', arms='reach', s=2)
    person(img, 'girl', gx, gy, view='side', pose='jump' if hop > 4 else 'stand', expr='laugh' if lt > 1.6 else 'surprised',
           arms='up' if lt > 1.6 else 'down', s=2, flip=True)
    # 棉花糖：先在他手里，再到她手里
    cx, cy = (248, 196) if lt < 1.6 else (gx - 6, gy - 72)
    d.line([(cx, cy), (cx, cy + 12)], fill=(240, 230, 210))
    for ox, oy, r in ((-4, -3, 6), (4, -4, 6), (0, -8, 6), (0, -2, 7)):
        d.ellipse([cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r], fill=(255, 180, 210))
    d.ellipse([cx - 3, cy - 12, cx + 1, cy - 8], fill=(255, 220, 236))
    bx, by = gx + 22 + 4 * math.sin(T * 1.5), gy - 120
    d.line([(gx + 4, gy - 50), (bx, by + 14)], fill=(240, 240, 250))
    d.ellipse([bx - 10, by - 12, bx + 10, by + 14], fill=(255, 210, 80)); d.ellipse([bx - 6, by - 8, bx - 2, by - 3], fill=(255, 245, 200))
    if lt > 1.8:
        for k in range(3):
            u = (lt - 1.8 - k * 0.4)
            if u > 0: sig.heart_at(img, 254 + 10 * math.sin(u * 3 + k), 160 - u * 14, 1, alpha=clamp(1 - u / 2))
    props.grain(img, T, 6)
    if lt > dur - 1.6:
        k = ease((lt - (dur - 1.6)) / 1.2)
        sp = props.sepia(img, k)
        img.paste(sp)
    vig(img, 0.55, (40, 26, 20))


def window_panel(who, T, flip, look_head, f):
    im = Image.new('RGB', (240, H)); d = ImageDraw.Draw(im)
    wall = (72, 60, 100) if who == 'boy' else (60, 76, 116)
    d.rectangle([0, 0, 240, H], fill=wall)
    wx0, wx1 = (20, 170) if not flip else (70, 220)
    sub = Image.new('RGB', (W, H)); sd = ImageDraw.Draw(sub)
    kit.night(sub, sd, T, NIGHT, 160)
    pix.city(sub, sd, 260, 7 if not flip else 11, 0, (20, 22, 54), (255, 214, 140), 40, 100, 0.25, T)
    im.paste(sub.crop((wx0 if not flip else wx0 + 240, 20, wx1 if not flip else wx1 + 240, 180)), (wx0, 20))
    d.rectangle([wx0, 20, wx1, 180], outline=(150, 120, 110), width=4)
    d.rectangle([wx0 - 8, 180, wx1 + 8, 186], fill=(170, 140, 120))
    px = 150 if not flip else 90
    person(im, who, px, 250, view='side', pose='stand', expr='smile', arms='phone', s=2, flip=flip)
    return im


def s_moon2(img, d, lt, dur, T, A):
    """我猜你一定也会想念我：左边他的窗、右边她的窗，中间同一个月亮；两人的想法云里都是对方"""
    img.paste(window_panel('boy', T, True, 'girl', 0), (0, 0))
    img.paste(window_panel('girl', T, False, 'boy', 0), (240, 0))
    d.rectangle([238, 0, 241, H], fill=(14, 12, 26))
    glow(img, 240, 70, 80, (255, 240, 200), 0.4)
    pix.moon(d, 240, 70, 26)
    f = eback(span(lt, 1.6, 2.0))
    for (x, who) in ((70, 'girl'), (410, 'boy')):
        if f > 0: _thought(img, d, x, 90, f, who, T)
    vig(img, 0.4)


def _thought(img, d, x, y, f, who, T):
    kit.thought(img, d, x, y, 60 * f, 36 * f, T)
    if f > 0.8:
        hi = props.head_img(who, expr='happy', s=2)
        dpaste(img, hi, x - hi.width / 2, y - hi.height / 2 - 4)
        sig.heart_at(img, x + 22, y - 14, 1)


HAIR = [(40, 32, 40), (72, 44, 42), (30, 26, 30), (110, 74, 50), (60, 50, 60), (150, 100, 60)]
COAT = [(90, 96, 120), (120, 110, 130), (80, 110, 120), (130, 120, 110), (100, 90, 110), (70, 80, 100)]


@lru_cache(None)
def crowd_pts():
    r = rng(8)
    pts = []
    for i in range(1400):
        x, y = r.uniform(-300, 300), r.uniform(-170, 170)
        if abs(x) < 10 and abs(y) < 10: continue
        band = int((y + 170) // 24)
        v = (1 if band % 2 else -1) * r.uniform(14, 26)
        pts.append((x, y, v, r.randrange(6), r.randrange(6)))
    return pts


def s_crowd(img, d, lt, dur, T, A):
    """也怕我失落在茫茫人海：俯瞰的人群像潮水一样流，他在正中间一动不动；镜头越拉越远，人海变成了真的海"""
    z = lerp(3.2, 0.85, ease(span(lt, 0.3, dur - 0.4)))
    sea = ease(span(lt, 2.8, dur))
    ground = lerpc((120, 116, 128), (30, 60, 120), sea)
    img.paste(ground, (0, 0, W, H))
    for k in range(0, H, int(max(4, 12 * z))):
        d.line([(0, k), (W, k)], fill=lerpc(lerpc(ground, (0, 0, 0), 0.08), (60, 110, 180), sea))
    for (x, y, v, hc, cc) in crowd_pts():
        wx = (x + v * lt + 300) % 600 - 300
        sx, sy = 240 + wx * z, 135 + y * z
        if -10 < sx < W + 10 and -10 < sy < H + 10:
            r1, r2 = 4.5 * z, 2.8 * z
            cc_ = lerpc(COAT[cc], (90, 150, 220), sea * 0.9); hh = lerpc(HAIR[hc], (200, 230, 255), sea * 0.8)
            if r1 < 1.5:
                d.point((sx, sy), fill=hh if (int(T * 3 + x) % 5) else (255, 255, 255))
            else:
                d.ellipse([sx - r1, sy - r1 * 0.7, sx + r1, sy + r1 * 0.7], fill=cc_)
                d.ellipse([sx - r2, sy - r2 - r1 * 0.35, sx + r2, sy + r2 - r1 * 0.35], fill=hh)
    # 他：暖橙色的帽衫，正中间，往外一圈圈发信号
    r1, r2 = 5.5 * z, 2.8 * z
    for j in range(3):
        u = (lt * 0.7 + j / 3) % 1
        rr = (8 + u * 50) * z
        d.ellipse([240 - rr, 135 - rr * 0.8, 240 + rr, 135 + rr * 0.8], outline=lerpc((255, 200, 140), ground, u))
    glow(img, 240, 135, 30 * z + 10, (255, 180, 120), 0.5)
    for sg in (-1, 1):                                           # 两只手
        d.rectangle([240 + sg * r1 - 1, 135 - 1, 240 + sg * r1 + max(1, z * 0.8), 135 + max(1, z * 0.8)], fill=pix.SKIN)
    d.ellipse([240 - r1 - 1, 135 - r1 * 0.7 - 1, 240 + r1 + 1, 135 + r1 * 0.7 + 1], fill=OUT)
    d.ellipse([240 - r1, 135 - r1 * 0.7, 240 + r1, 135 + r1 * 0.7], fill=sig.ORANGE)
    hy = 135 - r1 * 0.3
    d.ellipse([240 - r2 - 1.5 * z, hy - r2 + 0.5 * z, 240 + r2 + 1.5 * z, hy + r2 + 2 * z], fill=(214, 108, 62))   # 帽子
    d.ellipse([240 - r2 - 1, hy - r2 - 1, 240 + r2 + 1, hy + r2 + 1], fill=OUT)
    d.ellipse([240 - r2, hy - r2, 240 + r2, hy + r2], fill=(40, 32, 40))
    d.ellipse([240 - r2 * 0.5, hy - r2 * 0.6, 240, hy - r2 * 0.1], fill=(92, 76, 92))
    if lt > 2.4: sig.heart_at(img, 240, 135 - 12 * z - 4 * math.sin(T * 3), 1)
    if lt < 2.4: kit.pop(d, 240, 135 - 8 * z, '?', T, (255, 240, 160), span(lt, 0.6, 0.9))
    vig(img, 0.5)


def s_turn(img, d, lt, dur, T, A):
    """没关系只要你肯回头望：黄昏的长街，她往远处走，停下来回头；他在路灯下挥手，地上一道光把两人连起来"""
    sky(img, GOLDEN, 0, H, 6)
    glow(img, 400, 150, 140, (255, 210, 150), 0.45)
    d.ellipse([380, 130, 420, 170], fill=(255, 236, 190))
    pix.city(img, d, 196, 13, 0, (170, 120, 130), (255, 230, 170), 30, 80, 0.1, T, blink=False)
    d.rectangle([0, 196, W, H], fill=(150, 110, 110))
    for x in range(0, W, 40): d.line([(x, 228), (x + 20, 228)], fill=(180, 140, 130))
    for k in range(4): pix.tree_round(d, 30 + k * 130, 200, 1.0, (200, 120, 90), (240, 160, 110), (110, 70, 60))
    gx = lerp(250, 360, ease(span(lt, 0, 2.3)))
    turn = lt > 2.5
    if lt < 2.3:
        person(img, 'girl', gx, 240, view='side', pose='walk', ph=wph(lt, 5), expr='down', s=2)
    elif lt < 2.75:
        person(img, 'girl', gx, 240, view='front', pose='stand', expr='surprised', s=2)
    else:
        person(img, 'girl', gx, 240, view='side', pose='stand', expr='happy', arms='wave' if lt > 3.4 else 'down', ph=int(T * 5), s=2, flip=True)
    pix.lamp(img, d, 92, 244, 1.0, 100)
    person(img, 'boy', 110, 244, view='side', pose='stand', expr='smile', arms='wave' if lt > 2.9 else 'down', ph=int(T * 5), s=2)
    if lt > 2.9:
        f = eout(span(lt, 2.9, 4.0))
        x1 = lerp(120, gx - 10, f)
        for x in range(120, int(x1), 2):
            d.point((x, 246 + 2 * math.sin(x * 0.1 + T * 4)), fill=(255, 240, 180))
        glow(img, x1, 246, 14, (255, 220, 150), 0.6)
        for k in range(4):
            u = (lt * 0.5 + k / 4) % 1
            if u * (gx - 130) < x1 - 120: sig.heart_at(img, 120 + u * (gx - 130), 236 - 4 * math.sin(u * 6), 1)
    vig(img, 0.3)


def s_there(img, d, lt, dur, T, A):
    """会发现我一直都在：他撑着伞站在路灯下，雨、雪、花瓣轮流落下，他一直没走；最后天晴了，她从远处跑过来"""
    ph = lt / 4.6
    k = min(3, int(ph * 3))
    stops = (RAINY, ((0, (20, 24, 54)), (1, (90, 96, 140))), ((0, (40, 30, 80)), (1, (200, 140, 180))), NIGHT)[k]
    sky(img, stops, 0, H, 6)
    stars(d, T, 200, clamp((lt - 4.0) / 1), 200)
    pix.city(img, d, 206, 5, 0, (30, 32, 66), (255, 214, 140), 40, 120, 0.25, T)
    snow_g = k == 1
    d.rectangle([0, 206, W, H], fill=(230, 236, 246) if snow_g else (50, 50, 76))
    pix.lamp(img, d, 200, 236, 1.0, 120)
    person(img, 'boy', 230, 236, view='front', pose='stand', expr='happy' if lt > 4.8 else 'smile', arms='hold_l', s=2)
    if lt < 4.6:
        kit.umbrella(d, 222, 136, sig.ORANGE, (190, 90, 56), 24)
        d.line([(222, 150), (222, 190)], fill=OUT)
    if k == 0: kit.rain_layer(img, d, T, 160)
    elif k == 1: pix.snow(d, T, 140)
    elif k == 2: pix.petals(d, T, 60)
    sig.bars(d, 216, 120 - 4 * math.sin(T * 2) - (30 if lt < 4.6 else 0), 4, 2, on=sig.SIG)
    if lt > 4.6:
        u = span(lt, 4.6, dur)
        gx = lerp(W + 20, 270, eout(u))
        person(img, 'girl', gx, 236, view='side', pose='run' if u < 0.8 else 'stand', ph=wph(lt, 10), expr='laugh', s=2, flip=True,
               arms='reach' if u > 0.8 else 'auto')
        if u > 0.8:
            glow(img, 250, 180, 40, sig.HEART, 0.4)
            sig.heart_at(img, 250, 150 - 3 * math.sin(T * 4), 2)
    vig(img, 0.4)
