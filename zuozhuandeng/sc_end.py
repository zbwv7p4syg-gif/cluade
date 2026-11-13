"""左转灯 · 第二、三段副歌，两段间奏和片尾。签名都是 (img, d, lt, dur, T, A)。

第二段副歌换一套画面：满屏的“再见”、电梯门合上、起雾的窗上画心、胶片里循环的回忆、她把他的房间搬空、
送她半盒回忆、街机的 GAME OVER 和再投一枚硬币、两颗流星交叉、车尾的左转灯。
间奏是一段夜里的高架和桥上的停留；第三段副歌在雨里的路边；最后天亮了，他在路口打着左转灯，往右开向日出。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
from props import *          # noqa: F401,F403
from pix import person, wph, put, twinkle, sparkle, moon, cloud, darken, dither_fade, vig, vgrad, bayer, hills
from sc_verse import (bar_near, beat_after, street_bg, car_reflection, polaroid_img, court_photo, plane_img, title_str, intro_title_layout)
from sc_rap import oshape, steer, wheel, wobble


# ================================================================ 第二段副歌
def s_byes(img, d, lt, dur, T, A):
    """他站在中间，身边一个接一个弹出写着“再见”的对话泡泡，越来越密，计数跳到一千"""
    sky(img, ((0, (20, 12, 40)), (1, (60, 26, 70))))
    bokeh(img, T, 10, seed=51, a=0.2)
    n = int(60 * span(lt, 0, dur * 0.9) ** 1.3) + 1
    for i in range(n):
        r = rng(i * 7)
        a = r.uniform(0, 2 * math.pi); rad = r.uniform(70, 230)
        x = 240 + math.cos(a) * rad; y = 120 + math.sin(a) * rad * 0.5
        tb = dur * 0.9 * ((i + 1) / 60) ** (1 / 1.3)
        f = span(lt, tb, tb + 0.15)
        old = 1 - span(lt, tb + 0.6, tb + 1.2) * 0.6
        c = bubble(img, d, x, y, 34, 16, f, tail=(1 if x < 240 else -1, 1), col=lerpc((120, 100, 140), (255, 255, 255), old))
        if c: text(img, '再见', c[0], c[1], (60, 40, 70), None, FONT_S, shadow=False)
    person(img, 'boy', 240, 214, view='front', expr='sad', s=3)
    cnt = int(1000 * span(lt, 0, dur * 0.9) ** 1.3)
    d.rectangle([186, 4, 294, 26], fill=(18, 14, 30), outline=AMB if cnt >= 1000 else (80, 70, 110))
    text(img, '×' + str(cnt).rjust(4, '0'), 240, 15, AMB_L if cnt >= 1000 else (236, 230, 220), OUT)


def s_elevator(img, d, lt, dur, T, A):
    """电梯里的她低着头，电梯门从两边合上，门缝的光变成一条线，楼层数字往上跳"""
    img.paste((54, 50, 70), (0, 0, W, H))
    for x in range(0, W, 30): d.line([(x, 0), (x, H)], fill=(60, 56, 78))
    d.rectangle([0, 214, W, H], fill=(70, 64, 80))
    ex0, ex1, ey0, ey1 = 150, 330, 30, 214
    d.rectangle([ex0 - 10, ey0 - 10, ex1 + 10, ey1], fill=(150, 150, 166), outline=OUT)
    d.rectangle([ex0, ey0, ex1, ey1], fill=(220, 200, 150))
    for x in range(ex0 + 10, ex1, 20): d.line([(x, ey0), (x, ey1)], fill=(200, 180, 130))
    glow(img, 240, ey0 + 10, 90, (255, 240, 200), 0.4, 20)
    d.rectangle([ex0, ey1 - 30, ex1, ey1], fill=(170, 150, 120))
    person(img, 'girl', 240, ey1 - 4, view='front', expr='sad', s=3)
    close = ease(span(lt, 0.25, 1.1))
    half = (ex1 - ex0) / 2
    for side in (-1, 1):
        if side < 0: x0, x1 = ex0, ex0 + half * close
        else: x0, x1 = ex1 - half * close, ex1
        if x1 - x0 < 1: continue
        d.rectangle([x0, ey0, x1, ey1], fill=(176, 180, 196), outline=OUT)
        d.line([(x0 + 3, ey0 + 4), (x0 + 3, ey1 - 4)], fill=(210, 214, 228))
    if 0.9 < close < 1:
        glow(img, 240, (ey0 + ey1) / 2, 30, (255, 240, 200), 0.6, 100)
    d.rectangle([220, 8, 260, 24], fill=(16, 14, 24), outline=OUT)
    fl = 1 + int(max(0, lt - 1.1) * 6)
    text(img, ('▲' if lt > 1.1 else '') + str(fl), 240, 16, (255, 120, 80), None, FONT_S, shadow=False)
    d.rectangle([348, 110, 362, 140], fill=(150, 150, 166), outline=OUT)
    d.ellipse([351, 113, 359, 121], fill=(255, 200, 80) if lt < 1.1 else (90, 90, 100)); d.ellipse([351, 127, 359, 135], fill=(90, 90, 100))
    person(img, 'boy', 120, 330, view='back', s=4)
    vig(img, 0.45)


def s_fog(img, d, lt, dur, T, A):
    """起雾的车窗上，他用手指画了一颗心，心形擦开的地方露出外面下雨的夜城"""
    night_city(img, d, T, 230, lt * 3)
    rain(d, T, 0, W, 0, H, 70, (110, 120, 170), 240, -2, 5)
    fog = Image.new('L', (W, H), 175)
    fd = ImageDraw.Draw(fog)
    prog = ease(span(lt, 0.15, 1.5))
    pts = pix.heart_poly(240, 128, 5.2)
    n = int(len(pts) * prog)
    if n > 1:
        fd.line(pts[:n], fill=0, width=9)
        fd.ellipse([pts[n - 1][0] - 5, pts[n - 1][1] - 5, pts[n - 1][0] + 5, pts[n - 1][1] + 5], fill=0)
    if prog >= 1:
        inner = span(lt, 1.5, 1.9)
        if inner > 0: fd.polygon(pix.heart_poly(240, 128, 5.0 * ease(inner)), fill=0)
    a = np.asarray(fog, float) / 255
    al = np.clip(np.floor(a * 6 + pix.BAYER) / 6, 0, 1)[..., None]
    arr = np.asarray(img, float) * (1 - al * 0.8) + np.array((150, 160, 190)) * al * 0.8
    img.paste(Image.fromarray(arr.astype(np.uint8)))
    drops_on_glass(img, d, T, (0, 0, W, H), 50, 13, (200, 210, 240))
    if 0 < prog < 1:
        x, y = pts[n - 1]
        d.line([(x + 16, y + 26), (x + 150, H + 40)], fill=OUT, width=24); d.line([(x + 16, y + 26), (x + 150, H + 40)], fill=AMB, width=20)
        d.ellipse([x + 2, y + 8, x + 26, y + 32], fill=SKIN, outline=OUT)
        d.line([(x + 1, y + 1), (x + 8, y + 12)], fill=OUT, width=7); d.line([(x + 1, y + 1), (x + 8, y + 12)], fill=SKIN, width=5)
    if prog >= 1 and lt > 1.6:
        glow(img, 240, 128, 60, (255, 200, 140), 0.15)


SNAP_TIMES = [21.0, 31.6, 35.2, 46.6, 52.9, 55.0, 64.9, 67.6, 82.7, 99.0]


@lru_cache(None)
def snap_thumb(t, w, h):
    if not props.SNAP: return Image.new('RGB', (w, h), (40, 30, 60))
    return shrink(props.SNAP(t), w, h)


def film_frame(t, w=96, h=54):
    return snap_thumb(t, w, h)


def s_film(img, d, lt, dur, T, A):
    """放映机的光里，一条胶片不停地往左走，每一格都是前面出现过的画面，一遍又一遍"""
    img.paste((12, 10, 20), (0, 0, W, H))
    tfill(img, 'polygon', [(470, 60), (470, 200), (0, 250), (0, 10)], (255, 240, 200), 0.06)
    y0 = 70
    d.rectangle([0, y0, W, y0 + 90], fill=(26, 22, 20))
    fw = 110
    off = (lt * 220) % (fw * len(SNAP_TIMES))
    for k in range(-1, 6):
        idx = int((off // fw) + k) % len(SNAP_TIMES)
        x = k * fw - off % fw + 8
        fr = film_frame(SNAP_TIMES[idx], 96, 54)
        a = np.asarray(fr, float)
        g = a @ np.array([0.3, 0.59, 0.11])
        a = a * 0.75 + np.array((40, 24, 10)) * 0.25 + (g[..., None] - a) * 0.2
        img.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), (int(x), y0 + 18))
        d.rectangle([x - 1, y0 + 17, x + 96, y0 + 72], outline=(60, 50, 40))
    for x in range(-int(lt * 220) % 14, W, 14):
        d.rectangle([x, y0 + 5, x + 6, y0 + 11], fill=(12, 10, 20)); d.rectangle([x, y0 + 79, x + 6, y0 + 85], fill=(12, 10, 20))
    for _ in range(6):
        r = rng(int(T * 24) * 7 + _)
        x = r.uniform(0, W); d.line([(x, 0), (x, H)], fill=(60, 56, 50))
    d.ellipse([400, 180, 470, 250], fill=(40, 36, 50), outline=OUT); d.ellipse([340, 190, 400, 250], fill=(40, 36, 50), outline=OUT)
    for cxx, cyy, r in ((435, 215, 30), (370, 220, 26)):
        a = lt * 8
        for k in range(3):
            d.line([(cxx, cyy), (cxx + math.cos(a + k * 2.1) * r * 0.8, cyy + math.sin(a + k * 2.1) * r * 0.8)], fill=(90, 86, 100), width=2)
    text(img, 'REPLAY ×∞', 80, 200, AMB_L if int(T * 3) % 2 else AMB_D, OUT, FONT_S)


ROOM_ITEMS = [('lamp', 70, 150), ('plant', 130, 196), ('clock', 200, 70), ('poster', 300, 80), ('guitar', 380, 170), ('mug', 250, 182), ('ball', 420, 214)]


def room_item(img, d, kind, x, y, s=1.0):
    if kind == 'lamp':
        d.rectangle([x - 1, y, x + 1, y + 50 * s], fill=(80, 76, 100)); d.polygon([(x - 10 * s, y), (x + 10 * s, y), (x + 6 * s, y - 12 * s), (x - 6 * s, y - 12 * s)], fill=AMB, outline=OUT)
    elif kind == 'plant':
        d.rectangle([x - 7 * s, y - 10 * s, x + 7 * s, y], fill=(170, 90, 60), outline=OUT)
        for k in range(5): d.ellipse([x - 8 * s + k * 3 * s, y - 24 * s + (k % 2) * 4 * s, x - 2 * s + k * 3 * s, y - 12 * s], fill=(70, 160, 80), outline=OUT)
    elif kind == 'clock':
        d.ellipse([x - 12 * s, y - 12 * s, x + 12 * s, y + 12 * s], fill=(250, 246, 232), outline=OUT); d.line([(x, y), (x, y - 8 * s)], fill=OUT); d.line([(x, y), (x + 6 * s, y)], fill=OUT)
    elif kind == 'poster':
        d.rectangle([x - 18 * s, y - 24 * s, x + 18 * s, y + 24 * s], fill=TEAL, outline=OUT)
        d.ellipse([x - 9 * s, y - 14 * s, x + 9 * s, y + 4 * s], fill=(240, 130, 50), outline=OUT); d.line([(x - 9 * s, y - 5 * s), (x + 9 * s, y - 5 * s)], fill=OUT)
    elif kind == 'guitar':
        d.line([(x, y - 40 * s), (x, y - 10 * s)], fill=(110, 70, 40), width=max(1, int(3 * s)))
        d.ellipse([x - 10 * s, y - 16 * s, x + 10 * s, y + 4 * s], fill=(200, 120, 60), outline=OUT); d.ellipse([x - 12 * s, y - 2 * s, x + 12 * s, y + 18 * s], fill=(200, 120, 60), outline=OUT)
        d.ellipse([x - 3 * s, y - 2 * s, x + 3 * s, y + 4 * s], fill=OUT)
    elif kind == 'mug':
        d.rectangle([x - 6 * s, y - 10 * s, x + 6 * s, y], fill=(250, 250, 250), outline=OUT); put(img, 'heart', x, y - 5 * s, 1)
    elif kind == 'ball':
        d.ellipse([x - 9 * s, y - 9 * s, x + 9 * s, y + 9 * s], fill=(240, 130, 50), outline=OUT); d.line([(x - 9 * s, y), (x + 9 * s, y)], fill=OUT)


def s_thief(img, d, lt, dur, T, A):
    """她背着一个大口袋踮着脚溜出他的房间，台灯、盆栽、钟、海报、吉他一件件飞进袋子，房间空了，只剩他站着发愣"""
    img.paste((70, 56, 90), (0, 0, W, H))
    for x in range(0, W, 24): d.line([(x, 0), (x, 214)], fill=(76, 62, 98))
    d.rectangle([0, 214, W, H], fill=(96, 70, 60))
    for x in range(0, W, 40): d.line([(x, 214), (x - 30, H)], fill=(84, 60, 52))
    d.rectangle([20, 40, 120, 120], fill=(30, 26, 60), outline=OUT)
    pix.stars(d, T, 120, 0.6, 30)
    d.rectangle([20, 40, 120, 120], outline=(120, 100, 130), width=3)
    sx_, sy_ = lerp(400, 470, span(lt, 1.6, dur)), 196
    for i, (kind, x, y) in enumerate(ROOM_ITEMS):
        t0 = 0.45 + i * 0.24
        u = span(lt, t0, t0 + 0.45)
        if u >= 1: continue
        e = ein(u)
        px = lerp(x, sx_, e); py = lerp(y, sy_ - 10, e) - 50 * math.sin(math.pi * e)
        room_item(img, d, kind, px, py, 1 - 0.7 * e)
    person(img, 'boy', 210, 236, view='front', expr='surprised' if lt > 0.6 else 'neutral', s=3)
    gx = lerp(360, 470, span(lt, 1.6, dur))
    bag = 14 + 4 * min(len(ROOM_ITEMS), int(max(0, lt - 0.45) / 0.24))
    person(img, 'girl', gx, 236, view='side', pose='walk', ph=wph(lt, 4), expr='happy', s=3)
    d.ellipse([gx + 6 - bag * 0.4, 236 - 70 - bag, gx + 6 + bag * 1.1, 236 - 70 + bag * 0.6], fill=(200, 180, 140), outline=OUT)
    d.line([(gx + 6, 236 - 70 - bag * 0.5), (gx + 2, 236 - 60)], fill=(150, 120, 90), width=2)
    if lt > 1.9:
        c = bubble(img, d, 230, 140, 26, 22, span(lt, 1.9, 2.1), tail=(1, 1))
        if c: text(img, '?', c[0], c[1], (40, 30, 48), None, shadow=False)
    vig(img, 0.4)


ORB_ICONS = ['heart', 'ball', 'car', 'plane', 'star', 'note', 'ball', 'heart']


def orb(img, d, x, y, r, kind, a=1.0):
    glow(img, x, y, r * 2.2, (255, 220, 160), 0.35 * a)
    tfill(img, 'ellipse', [x - r, y - r, x + r, y + r], (255, 246, 220), 0.55 * a)
    if a < 0.4: return
    if kind == 'heart': put(img, 'heart', x, y, 1)
    elif kind == 'star': put(img, 'star', x, y, 1)
    elif kind == 'note': put(img, 'note', x, y, 1)
    elif kind == 'ball': d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(240, 130, 50))
    elif kind == 'car': d.rectangle([x - 4, y - 1, x + 4, y + 2], fill=CAR, outline=OUT)
    elif kind == 'plane': d.line([(x - 4, y), (x + 4, y)], fill=(250, 250, 255), width=2); d.line([(x, y - 3), (x + 1, y + 3)], fill=(250, 250, 255))


def s_gift(img, d, lt, dur, T, A):
    """路灯下，他捧着一个礼物盒打开，里面一颗颗装着回忆的小光球，一半飘去她那边，一半留在盒子里"""
    street_bg(img, d, T, lt, ground=214, lamps=(240,))
    person(img, 'boy', 150, 238, view='side', pose='stand', expr='smile', arms='reach', s=3)
    person(img, 'girl', 380, 238, view='side', pose='stand', expr='sad', arms='reach' if lt > 2.2 else 'down', s=3, flip=True)
    bx, by = 186, 172
    lid = ease(span(lt, 0.3, 0.8))
    d.rectangle([bx - 14, by - 10, bx + 14, by + 10], fill=AMB, outline=OUT); d.rectangle([bx - 2, by - 10, bx + 2, by + 10], fill=TEAL)
    lx = bx - 14 - 6 * lid; ly = by - 14 - 20 * lid
    d.polygon([(lx, ly + 4), (lx + 30, ly + 4 - 10 * lid), (lx + 30, ly - 10 * lid), (lx, ly)], fill=AMB_L, outline=OUT)
    if lid > 0.5: glow(img, bx, by - 14, 30, (255, 230, 170), 0.5 * lid)
    for i in range(8):
        go = i % 2 == 0
        t0 = 0.8 + i * 0.22
        u = span(lt, t0, t0 + 1.4)
        if lt < t0: continue
        if go:
            e = ease(u)
            x = lerp(bx, 360, e); y = lerp(by - 20, 150, e) - 70 * math.sin(math.pi * e)
        else:
            e = ease(min(1, u * 1.6))
            x = bx + (i - 3.5) * 5; y = by - 20 - 18 * e
        orb(img, d, x, y + 2 * math.sin(T * 3 + i), 6, ORB_ICONS[i])


def arcade(img, d, T, lt, screen_fn, coin=None):
    img.paste((14, 10, 26), (0, 0, W, H))
    glow(img, 240, 110, 200, (120, 80, 255), 0.18, 120)
    d.polygon([(120, 0), (360, 0), (380, 40), (100, 40)], fill=(150, 40, 110), outline=OUT)
    big_text(img, 'ARCADE', 240, 20, 1, AMB)
    d.rectangle([110, 40, 370, 270], fill=(60, 30, 90), outline=OUT)
    d.rectangle([130, 50, 350, 196], fill=(20, 20, 26), outline=OUT)
    sc = Image.new('RGB', (210, 136), (8, 6, 20)); sd = ImageDraw.Draw(sc); sd.fontmode = '1'
    screen_fn(sc, sd)
    a = np.asarray(sc, float); a[::2] *= 0.8
    img.paste(Image.fromarray(a.astype(np.uint8)), (135, 55))
    glow(img, 240, 123, 120, (150, 200, 255), 0.12, 70)
    d.rectangle([110, 196, 370, 230], fill=(90, 50, 130), outline=OUT)
    for x, c in ((170, RED), (200, (60, 160, 255)), (280, AMB), (310, (60, 220, 120))):
        d.ellipse([x - 8, 206, x + 8, 220], fill=c, outline=OUT)
    d.rectangle([230, 204, 238, 222], fill=(40, 40, 50)); d.ellipse([226, 198, 242, 210], fill=RED, outline=OUT)
    d.rectangle([220, 236, 260, 262], fill=(40, 30, 50), outline=OUT)
    d.rectangle([238, 242, 242, 256], fill=AMB if int(T * 4) % 2 else AMB_D)


def s_gameover(img, d, lt, dur, T, A):
    """街机屏幕上大大的 GAME OVER，下面的“继续？”在倒数，左上角记着已经输了一千次"""
    def scr(sc, sd):
        k = span(lt, 0, 0.3)
        y = lerp(-20, 40, eback(k))
        g = Image.new('L', (90, 16)); gd = ImageDraw.Draw(g); gd.fontmode = '1'; gd.text((2, 0), 'GAME OVER', font=FONT, fill=255)
        g = g.resize((180, 32), Image.NEAREST)
        sc.paste((255, 70, 90), (15, int(y)), g)
        cnt = 10 - int(lt * 3)
        if int(T * 3) % 2: sd.text((60, 86), f'CONTINUE? {max(0, cnt)}', font=FONT_S, fill=(255, 255, 255))
        sd.text((6, 4), '×1000', font=FONT_S, fill=AMB)
        sd.text((150, 4), 'HI 0', font=FONT_S, fill=(150, 150, 170))
        for k2 in range(5):
            sd.rectangle([20 + k2 * 36, 118, 40 + k2 * 36, 124], fill=(60, 50, 90))
    arcade(img, d, T, lt, scr)
    person(img, 'boy', 240, 360, view='back', s=4, tint=(10, 8, 18))


def s_coin_in(img, d, lt, dur, T, A):
    """再投一枚硬币：硬币翻着跳进投币口，屏幕上跳出“CREDIT 1”和“×1001 READY?”"""
    inserted = lt > 0.55
    def scr(sc, sd):
        if not inserted:
            if int(T * 4) % 2: sd.text((62, 60), 'INSERT COIN', font=FONT_S, fill=AMB_L)
            sd.text((6, 4), '×1000', font=FONT_S, fill=AMB)
        else:
            k = lt - 0.55
            sd.text((70, 36), 'CREDIT 1', font=FONT_S, fill=(120, 255, 160))
            if k > 0.3:
                g = Image.new('L', (100, 16)); gd = ImageDraw.Draw(g); gd.fontmode = '1'; gd.text((2, 0), '×1001', font=FONT, fill=255)
                g = g.resize((200, 32), Image.NEAREST)
                sc.paste(AMB if int(T * 6) % 2 else AMB_L, (40, 62), g)
            if k > 0.7: sd.text((76, 104), 'READY?', font=FONT_S, fill=(255, 255, 255))
            sd.text((6, 4), '×1001', font=FONT_S, fill=AMB)
    arcade(img, d, T, lt, scr)
    if not inserted:
        u = span(lt, 0.0, 0.55)
        x = lerp(330, 240, ease(u)); y = lerp(150, 236, ease(u)) - 40 * math.sin(math.pi * u)
        w = max(2, int(12 * abs(math.cos(lt * 14))))
        d.ellipse([x - w, y - 12, x + w, y + 12], fill=(250, 200, 70), outline=OUT)
        oshape(d, [x + 4, y + 4, x + 30, y + 22], SKIN, 6)
        d.rectangle([x + 22, y + 10, x + 70, y + 40], fill=AMB, outline=OUT)
    else:
        k = lt - 0.55
        burst(img, d, k, 240, 123, life=1.0, scale=0.9)
        if k < 0.12: darken(img, 0.5 * (1 - k / 0.12), (255, 250, 230))


def rooftop(d, x0, x1, y, col, edge):
    d.rectangle([x0, y, x1, H], fill=col); d.rectangle([x0 - 2, y - 3, x1 + 2, y], fill=edge)
    for x in range(x0 + 6, x1 - 6, 14):
        for yy in range(y + 10, H, 16):
            d.rectangle([x, yy, x + 6, yy + 8], fill=(255, 210, 120) if (x * 7 + yy) % 5 == 0 else lerpc(col, (0, 0, 0), 0.3))


def s_meteors(img, d, lt, dur, T, A):
    """他和她站在相隔很远的两座楼顶上；两颗流星一颗琥珀色、一颗青绿色，平行着划过，然后拐弯交叉，在夜空里画出一颗心"""
    sky(img, ((0, (8, 6, 26)), (0.6, (30, 18, 64)), (1, (80, 40, 100))))
    pix.stars(d, T, 200, 1.0, 220)
    city(img, d, 230, 41, 0, (30, 22, 58), (200, 160, 220), 30, 90, 0.2, T, 10, 22)
    rooftop(d, 20, 150, 190, (24, 18, 44), (40, 32, 66))
    rooftop(d, 340, 470, 200, (24, 18, 44), (40, 32, 66))
    person(img, 'boy', 90, 190, view='side', pose='stand', expr='surprised', s=2)
    person(img, 'girl', 400, 200, view='side', pose='stand', expr='surprised', s=2, flip=True)
    hp = pix.heart_poly(240, 104, 3.6)
    def path(u, side):
        """两颗流星：先平行飞，再分别沿着心的左右两半绕下来，在心尖交汇"""
        if u < 0.4:
            k = u / 0.4
            return lerp(-40, 240, k) if side < 0 else lerp(520, 240, k), 30 + (0 if side < 0 else 14) + k * 10
        k = (u - 0.4) / 0.6
        n = len(hp)
        idx = int(k * (n / 2 - 1))
        p = hp[idx] if side > 0 else hp[(n - idx) % n]
        return p
    u = span(lt, 0.1, dur - 0.5)
    for side, col in ((-1, AMB), (1, TEAL)):
        if u > 0.4:
            trail = [path(uu, side) for uu in np.linspace(0.4, u, 60)]
            d.line(trail, fill=lerpc(col, (30, 18, 64), 0.45), width=1)
    for side, col in ((-1, AMB), (1, TEAL)):
        for j in range(26):
            uu = max(0, u - j * 0.012)
            x, y = path(uu, side)
            c = lerpc(col, (30, 18, 60), j / 26)
            d.rectangle([x, y, x + (1 if j else 2), y + (1 if j else 2)], fill=c)
        x, y = path(u, side)
        glow(img, x, y, 12, col, 0.6)
    if u > 0.98:
        k = lt - (0.1 + (dur - 0.6))
        tip = hp[len(hp) // 2]
        glow(img, tip[0], tip[1], 40, (255, 240, 220), 0.6)
        burst(img, d, k, tip[0], tip[1], life=1.0, scale=0.6)


def rear_street(img, d, T, lt, green=False, light_y=40):
    night_city(img, d, T, 150, 0, star_n=80)
    d.rectangle([0, 150, W, H], fill=(34, 32, 48))
    for k in range(10):
        z = k / 10
        y = 150 + 120 * z ** 1.5
        d.line([(240 - 20 - 300 * z ** 1.5, y), (240 - 18 - 300 * z ** 1.5, y + 4)], fill=(200, 200, 196))
    for y_ in range(156, 172, 4): d.line([(150, y_), (330, y_)], fill=(200, 200, 196)) if (y_ // 4) % 2 else None
    d.line([(240, 150), (240, 270)], fill=(240, 196, 60), width=1)
    for x_, h_ in ((60, 90), (420, 90)):
        lamp(img, d, x_, 150, 1.0, h_)
    d.line([(150, 0), (150, light_y + 4)], fill=(60, 56, 80), width=2)
    d.line([(150, light_y + 4), (330, light_y + 4)], fill=(60, 56, 80), width=2)
    hx = 300
    d.rounded_rectangle([hx - 26, light_y - 8, hx + 26, light_y + 8], 3, fill=(24, 22, 34), outline=OUT)
    for j, c in enumerate([(255, 60, 60), (255, 190, 40), (60, 230, 120)]):
        on = (j == 0 and not green)
        d.ellipse([hx - 22 + j * 15, light_y - 5, hx - 12 + j * 15, light_y + 5], fill=c if on else lerpc(c, (20, 20, 30), 0.8))
        if on: glow(img, hx - 17 + j * 15, light_y, 18, c, 0.5)
    if green:
        props.arrow(img, hx + 40, light_y, 1, 1.0, col=(60, 230, 120), glow_r=12)
    reflect(img, 150, 120, T, a=0.5)
    rain(d, T, 0, W, 0, H, 90, (100, 110, 160), 260, -2, 5)
    splashes(d, T, 160, H, 24)


def s_rear_left(img, d, lt, dur, T, A):
    """从车后面看：雨夜的路口，他的车停在红灯前，车尾左边的转向灯跟着节拍一亮一灭，照亮了湿漉漉的地面"""
    rear_street(img, d, T, lt, green=lt > dur - 0.6)
    sig = blink_a(T)
    if sig > 0.1:
        glow(img, 170, 236, 70, AMB, 0.25 * sig, 18)
    car_rear(img, 240, 236, 4, sig, True)
    if sig > 0.5: text(img, '嗒', 150, 110, AMB_L, (60, 24, 10), FONT_S)
    vig(img, 0.4)


def s_rear_right(img, d, lt, dur, T, A):
    """绿灯，车子往右一拐开远了，左转灯还在闪"""
    rear_street(img, d, T, lt, green=True)
    u = ease(span(lt, 0.1, dur))
    x = lerp(240, 420, u); y = lerp(236, 176, u)
    s = max(1, int(round(lerp(4, 1.6, u))))
    car_rear(img, x, y, s, blink_a(T), False, tilt=-14 * math.sin(math.pi * min(1, u * 1.4)))
    vig(img, 0.4)


# ================================================================ 间奏
MEMORIES = [21.0, 35.2, 55.0, 82.7, 64.9, 107.8]


def s_drive(img, d, lt, dur, T, A):
    """间奏：夜里的高架桥上，他一个人开着车往右走，城市从身边滑过，回忆一张张印成拍立得从路上飘上天"""
    off = lt * 160
    night_city(img, d, T, 170, off * 0.5, moon_xy=(400, 40))
    d.rectangle([0, 170, W, 186], fill=(54, 50, 72))
    for x in range(-int(off) % 30, W, 30): d.rectangle([x, 174, x + 2, 186], fill=(80, 76, 100))
    d.rectangle([0, 186, W, 200], fill=(40, 38, 56))
    for x in range(-int(off * 1.0) % 40, W, 40): d.rectangle([x, 192, x + 20, 193], fill=(200, 200, 196))
    d.rectangle([0, 200, W, 206], fill=(70, 66, 90))
    for x in range(-int(off) % 120, W + 120, 120):
        d.rectangle([x + 40, 206, x + 56, H], fill=(46, 42, 62))
    d.rectangle([0, 206, W, H], fill=(18, 14, 34)) if False else None
    for x in range(-int(off * 1.4) % 90, W, 90):
        lx = x + 30
        d.line([(lx, 186), (lx, 128)], fill=(80, 76, 100), width=2); d.line([(lx, 128), (lx + 14, 128)], fill=(80, 76, 100), width=2)
        glow(img, lx + 14, 130, 22, (255, 220, 160), 0.4); d.rectangle([lx + 10, 128, lx + 18, 130], fill=(255, 240, 200))
    sig = blink_a(T)
    car(img, 200, 198, 0, int(lt * 30), 2, beams=True)
    for k, t0 in enumerate(MEMORIES):
        start = 0.2 + k * 1.0
        u = (lt - start) / 3.0
        if not 0 <= u < 1: continue
        x = 140 + k * 50 + 30 * math.sin(u * 3 + k) - u * 60
        y = lerp(180, 30, ease(u))
        a = 1 - span(u, 0.8, 1.0)
        ph = snap_thumb(t0, 64, 36)
        polaroid(img, d, x, y, ph, span(u, 0.0, 0.4), a, rot=int(8 * math.sin(k * 2 + u * 3)))
    vig(img, 0.4)


def s_bridge(img, d, lt, dur, T, A):
    """车停在桥上打着双闪，他靠着栏杆看江面上城市的倒影，拿出手机看了看，又放回口袋"""
    sky(img, ((0, (10, 8, 30)), (0.6, (34, 22, 70)), (1, (90, 46, 104))), 0, 150)
    pix.stars(d, T, 110, 0.9, 140)
    moon(d, 90, 40, 13); glow(img, 90, 40, 40, (250, 240, 200), 0.25)
    city(img, d, 150, 51, lt * 2, (36, 28, 70), (255, 206, 120), 30, 100, 0.35, T, 10, 22)
    d.rectangle([0, 150, W, 200], fill=(20, 22, 52))
    reflect(img, 150, 50, T, (10, 14, 40), a=0.7, amp=2.5)
    d.line([(76, 152), (104, 200)], fill=(220, 214, 180)) if False else None
    for k in range(14):
        y = 152 + k * 3.5
        w_ = 6 + k
        d.line([(90 - w_, y), (90 + w_, y)], fill=lerpc((250, 240, 200), (20, 22, 52), 0.4 + k / 20)) if k % 2 == 0 else None
    d.rectangle([0, 200, W, H], fill=(56, 52, 72))
    d.rectangle([0, 200, W, 204], fill=(90, 86, 110))
    sig = blink_a(T)
    car(img, 360, 236, sig, 0, 2, lights=False, beams=False, brake=True)
    if sig > 0.3:
        glow(img, 360 - 56, 220, 18, AMB, 0.5 * sig); glow(img, 360 + 54, 220, 18, AMB, 0.5 * sig)
    person(img, 'boy', 200, 236, view='side', pose='stand', expr='down', arms='phone' if 1.0 < lt < 2.8 else 'down', s=3, flip=True)
    if 1.0 < lt < 2.8: glow(img, 186, 170, 20, (150, 200, 255), 0.4)
    d.line([(0, 190), (W, 190)], fill=(150, 150, 170), width=3)
    for x in range(10, W, 24): d.line([(x, 190), (x, 236)], fill=(110, 110, 130), width=2)
    d.line([(0, 214), (W, 214)], fill=(110, 110, 130), width=2)
    rain(d, T, 0, W, 0, H, 50, (110, 120, 170), 220, -2, 5)
    vig(img, 0.45)


# ================================================================ 第三段副歌
def s_curb(img, d, lt, dur, T, A):
    """雨里的路边，他坐在路灯下的马路牙子上，旁边停着的车还在闪；身边一个个“再见”的泡泡慢慢淡掉，被雨打散"""
    street_bg(img, d, T, lt, ground=200, lamps=(150,))
    sig = blink_a(T)
    car(img, 360, 246, sig, 0, 2, lights=False, beams=False)
    person(img, 'boy', 190, 226, view='side', pose='sit', expr='down', arms='lap', s=3)
    for i in range(8):
        t0 = 0.3 + i * 0.5
        k = lt - t0
        if k < 0 or k > 2.4: continue
        r = rng(i * 3)
        x = 190 + r.uniform(-120, 120); y = 120 + r.uniform(-60, 40) - k * 10
        a = 1 - span(k, 1.2, 2.4)
        f = span(k, 0, 0.2)
        if a <= 0.05: continue
        c = bubble(img, d, x, y, 34, 16, f, tail=(1 if x < 190 else -1, 1), col=lerpc((80, 80, 110), (230, 230, 240), a))
        if c and a > 0.3: text(img, '再见', c[0], c[1], lerpc((80, 80, 110), (60, 40, 70), a), None, FONT_S, shadow=False)
    vig(img, 0.5)


def s_letters(img, d, lt, dur, T, A):
    """台灯下他写了一封信又揉成一团，扔到身后已经堆成小山的纸团上；角上的数字从一千跳成一千零一"""
    img.paste((28, 24, 48), (0, 0, W, H))
    glow(img, 140, 120, 200, (255, 210, 140), 0.25, 140)
    d.rectangle([0, 190, W, H], fill=(52, 40, 56))
    r = rng(5)
    for i in range(70):
        x = 330 + r.gauss(0, 50); y = 250 - abs(r.gauss(0, 1)) * 40 - (60 - abs(x - 330)) * 0.6 * (abs(x - 330) < 60)
        rr = r.randint(6, 10)
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=lerpc((236, 232, 224), (190, 186, 180), r.random()), outline=OUT)
        d.line([(x - rr / 2, y - 2), (x + rr / 3, y + 1)], fill=(170, 166, 160))
    d.rectangle([40, 186, 250, 196], fill=(120, 80, 56), outline=OUT); d.rectangle([60, 196, 70, H], fill=(100, 66, 46)); d.rectangle([220, 196, 230, H], fill=(100, 66, 46))
    d.polygon([(70, 120), (90, 116), (96, 132), (76, 136)], fill=AMB_D, outline=OUT); d.line([(80, 134), (66, 186)], fill=(80, 76, 100), width=2)
    tfill(img, 'polygon', [(84, 134), (96, 132), (180, 186), (80, 186)], (255, 220, 150), 0.18)
    person(img, 'boy', 180, 236, view='side', pose='sit', expr='sad', arms='type', s=3, flip=True)
    k_throw = span(lt, 0.7, 1.3)
    if k_throw <= 0:
        d.rectangle([110, 180, 150, 186], fill=(250, 246, 230), outline=OUT)
        for j in range(3): d.line([(114, 182), (114 + 30 * span(lt, j * 0.2, j * 0.2 + 0.2), 182)], fill=(120, 110, 130))
    elif k_throw < 1:
        x = lerp(160, 330, k_throw); y = lerp(150, 200, k_throw) - 80 * math.sin(math.pi * k_throw)
        d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(250, 246, 230), outline=OUT)
    else:
        d.ellipse([322, 184, 338, 200], fill=(255, 250, 236), outline=AMB)
    plus = lt > 1.4
    d.rectangle([370, 10, 470, 34], fill=(18, 14, 30), outline=AMB if plus else (80, 70, 110))
    text(img, '×1001' if plus else '×1000', 420, 22, AMB_L if plus else (236, 230, 220), OUT)
    if plus: burst(img, d, lt - 1.4, 420, 22, life=0.9, scale=0.5)


def flap_digit(img, d, x, y, ch_old, ch_new, k, w=28, h=40):
    """翻页数字：k 从 0 到 1 翻过去"""
    def card(ch, top, bottom):
        im = Image.new('RGB', (w, h), (30, 26, 40)); cd = ImageDraw.Draw(im); cd.fontmode = '1'
        g = Image.new('L', (12, 16)); gd = ImageDraw.Draw(g); gd.fontmode = '1'; gd.text((1, -1), ch, font=FONT, fill=255)
        g = g.resize((24, 32), Image.NEAREST); im.paste(AMB_L, (2, 4), g)
        return im
    a, b = card(ch_old, 1, 1), card(ch_new, 1, 1)
    img.paste(b.crop((0, 0, w, h // 2)), (x, y))
    img.paste(a.crop((0, h // 2, w, h)), (x, y + h // 2))
    if k < 0.5:
        hh = int(h / 2 * (1 - 2 * k))
        if hh > 0: img.paste(a.crop((0, 0, w, h // 2)).resize((w, hh), Image.NEAREST), (x, y + h // 2 - hh))
    else:
        hh = int(h / 2 * (2 * k - 1))
        if hh > 0: img.paste(b.crop((0, h // 2, w, h)).resize((w, hh), Image.NEAREST), (x, y + h // 2))
    d.line([(x, y + h // 2), (x + w, y + h // 2)], fill=(10, 8, 16))
    d.rectangle([x - 1, y - 1, x + w, y + h], outline=OUT)


def s_tally_plus(img, d, lt, dur, T, A):
    """满墙的记号旁边，一只手拿着粉笔又添上一道；上面的翻页计数从 1000 翻到 1001"""
    img.paste((32, 34, 50), (0, 0, W, H))
    for y in range(0, H, 9):
        off = 0 if (y // 9) % 2 else 9
        for x in range(-off, W, 18): d.rectangle([x, y, x + 17, y + 8], outline=(28, 30, 44))
    for i in range(400):
        g, st = divmod(i, 5)
        x0 = 20 + (g % 20) * 22; y0 = 96 + (g // 20) * 22
        if y0 > 230: break
        r = rng(i)
        if st < 4:
            x = x0 + st * 3; d.line([(x, y0 + r.randint(0, 1)), (x, y0 + 13)], fill=(200, 196, 186))
        else:
            d.line([(x0 - 2, y0 + 10), (x0 + 13, y0 + 2)], fill=(200, 196, 186))
    u = span(lt, 0.2, 0.8)
    x0, y0 = 390, 186
    if u > 0:
        d.line([(x0, y0), (x0 + 1, y0 + 30 * u)], fill=AMB, width=2)
    hx, hy = x0 + 4, y0 + 30 * u
    d.rectangle([hx - 2, hy - 14, hx + 2, hy], fill=(250, 250, 240), outline=OUT)
    oshape(d, [hx - 4, hy - 6, hx + 18, hy + 14], SKIN, 6)
    d.line([(hx + 14, hy + 8), (hx + 80, hy + 70)], fill=OUT, width=20); d.line([(hx + 14, hy + 8), (hx + 80, hy + 70)], fill=AMB, width=16)
    k = span(lt, 0.9, 1.3)
    olds, news = '1000', '1001'
    for i in range(4):
        kk = k if olds[i] != news[i] else 1
        flap_digit(img, d, 182 + i * 30, 20, olds[i], news[i], kk)
    if lt > 1.3: burst(img, d, lt - 1.3, 240, 40, life=0.8, scale=0.6)


def contrail_plane(img, d, x, y, ang, s=1):
    pl = plane_img()
    if s != 1: pl = pl.resize((pl.width * s // 2, pl.height * s // 2), Image.NEAREST)
    paste(img, pl.rotate(ang, resample=Image.NEAREST, expand=True), x, y, 1, 'cc')


def s_contrails(img, d, lt, dur, T, A):
    """天快亮了，两架飞机拉出两道平行的白线，后来一架拐了个弯，两道航迹在天上交成一个叉"""
    sky(img, ((0, (40, 50, 110)), (0.55, (190, 140, 170)), (1, (255, 200, 160))))
    pix.stars(d, T, 60, 0.4, 40)
    for i, (cx, cy, s) in enumerate(((30, 150, 2.0), (300, 170, 2.4), (180, 200, 1.6))):
        cloud(d, cx - lt * 6, cy, s, (250, 210, 210), (230, 180, 190))
    hills(d, 236, 6, 0.02, 2.0, (70, 60, 100))
    u = span(lt, 0, dur)
    pa = lambda k: (lerp(-40, 520, k), 60)
    def pb(k):
        if k < 0.4: return lerp(520, 300, k / 0.4), 100
        kk = (k - 0.4) / 0.6
        return lerp(300, -40, kk), 100 - 120 * kk + 30 * math.sin(kk * 3)
    for f, col in ((pa, (255, 255, 255)), (pb, (255, 240, 230))):
        pts = [f(k) for k in np.linspace(max(0, u - 0.7), u, 40)]
        for j in range(len(pts) - 1):
            w_ = 1 + int(j / len(pts) * 3)
            d.line([pts[j], pts[j + 1]], fill=lerpc((200, 190, 220), col, j / len(pts)), width=w_)
    xa, ya = pa(u); xb, yb = pb(u)
    paste(img, plane_img().transpose(Image.FLIP_LEFT_RIGHT), xa, ya, 1, 'cc')
    xb2, yb2 = pb(min(1, u + 0.01))
    paste(img, plane_img().rotate(math.degrees(math.atan2(yb2 - yb, xb - xb2)) if xb != xb2 else 0, resample=Image.NEAREST, expand=True), xb, yb, 1, 'cc')
    if u > 0.55:
        for k_ in np.linspace(0.45, u, 30):
            x, y = pb(k_)
            if abs(y - 60) < 3 and x < xa:
                glow(img, x, 60, 30, (255, 255, 230), 0.6)
                twinkle(d, int(x), 60, (lt * 2) % 1, (255, 255, 255), 5)
                break


def s_blinker(img, d, lt, dur, T, A):
    """转向灯的特写：雨珠挂在琥珀色的灯罩上，灯一亮，最大的那颗水珠里映出她小小的身影"""
    sky(img, ((0, (16, 12, 34)), (1, (40, 24, 60))))
    bokeh(img, T, 18, [AMB, PINK, (150, 200, 255), (255, 220, 160)], seed=61, a=0.32, rmin=16, rmax=34)
    d.polygon([(0, 70), (W, 40), (W, H), (0, H)], fill=CAR_S)
    d.polygon([(0, 80), (W, 52), (W, H), (0, H)], fill=CAR)
    d.line([(0, 80), (W, 52)], fill=CAR_L, width=3)
    for x in range(0, W, 3):
        if (x // 3) % 7 == 0: d.point((x, 82 + (W - x) * 0.06), fill=(255, 255, 255))
    on = blink_a(T)
    cx, cy = 230, 160
    d.rounded_rectangle([cx - 150, cy - 64, cx + 150, cy + 64], 26, fill=(70, 66, 80), outline=OUT)
    lens = lerpc((150, 90, 40), (255, 190, 70), on)
    d.rounded_rectangle([cx - 140, cy - 56, cx + 140, cy + 56], 22, fill=lens)
    for x in range(cx - 136, cx + 136, 12):
        for y in range(cy - 52, cy + 52, 12):
            d.rectangle([x, y, x + 10, y + 10], outline=lerpc(lens, (255, 255, 255) if on > 0.5 else (90, 50, 20), 0.35))
    if on > 0.1:
        glow(img, cx, cy, 200, AMB, 0.45 * on, 120)
        glow(img, cx - 30, cy - 10, 60, (255, 250, 220), 0.6 * on)
    r = rng(3)
    for i in range(18):
        x, y = cx + r.uniform(-130, 130), cy + r.uniform(-50, 50) + (lt * r.uniform(2, 10)) % 20
        rr = r.randint(2, 5)
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=lerpc(lens, (255, 255, 255), 0.3), outline=lerpc(lens, (80, 40, 10), 0.5))
        d.point((x - rr / 2, y - rr / 2), fill=(255, 255, 255))
    bx, by, br = cx + 70, cy + 12, 22
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=lerpc(lens, (255, 255, 255), 0.25), outline=lerpc(lens, (80, 40, 10), 0.6))
    d.arc([bx - br + 4, by - br + 4, bx + br - 4, by + br - 4], 200, 260, fill=(255, 255, 255), width=2)
    if on > 0.5:
        g = pix.char_img('girl', 'young', 'front', 'stand', 0, 'smile')
        g = g.resize((g.width, g.height), Image.NEAREST)
        a = np.array(g); a[..., 3] = (a[..., 3] * 0.85).astype(np.uint8); g = Image.fromarray(a)
        paste(img, g, bx, by + 14, 1, 'cb')
    rain(d, T, 0, W, 0, H, 50, (180, 190, 230), 260, -2, 6)
    if on > 0.5: text(img, '嗒', 420, 50, AMB_L, (60, 24, 10), scale=2)


def s_wheel_right(img, d, lt, dur, T, A):
    """方向盘的特写：两只手一把往右打到底，窗外的灯拉成了线"""
    sky(img, ((0, (12, 10, 30)), (1, (40, 24, 60))))
    sp = ease(span(lt, 0.1, 0.9))
    for i in range(30):
        r = rng(i * 5)
        y = r.uniform(10, 200)
        x = (r.uniform(0, W) - lt * 900 * (0.3 + sp)) % (W + 100) - 50
        L = 20 + 120 * sp
        d.line([(x, y), (x + L, y)], fill=[AMB, (255, 220, 160), PINK, (150, 200, 255)][i % 4])
    d.rectangle([0, 190, W, H], fill=(30, 28, 40))
    props.arrow(img, 60, 214, 2, blink_a(T))
    props.arrow(img, 420, 214, 2, 0.0, left=False, glow_r=0)
    steer(img, d, 130 * sp, 240, 250, 120)
    if sp > 0.5:
        for k in range(3):
            a = math.radians(-60 + k * 20)
            d.arc([240 - 150, 250 - 150, 240 + 150, 250 + 150], -80 + k * 6, -40 + k * 6, fill=(255, 255, 255))


# ================================================================ 天亮
DAWN = ((0, (40, 46, 110)), (0.45, (170, 110, 160)), (0.75, (255, 160, 140)), (1, (255, 214, 160)))


def dawn_sky(img, d, k, y1=150):
    night = ((0, (10, 8, 30)), (0.6, (34, 22, 70)), (1, (90, 46, 104)))
    stops = tuple((p, lerpc(c1, c2, k)) for (p, c1), (_, c2) in zip(night, ((0, (40, 46, 110)), (0.6, (200, 130, 150)), (1, (255, 200, 150)))))
    sky(img, stops, 0, y1)


def s_sunrise(img, d, lt, dur, T, A):
    """间奏：天慢慢亮了。他的车在空旷的公路上往前开，两条车道线一直伸到地平线，在太阳升起的地方交到一起"""
    k = ease(span(lt, 0, dur * 0.8))
    dawn_sky(img, d, k, 130)
    pix.stars(d, T, 110, 1 - k, 160)
    sy = lerp(150, 96, k)
    if sy < 135:
        rr = 30
        d.ellipse([240 - rr, sy - rr, 240 + rr, sy + rr], fill=(255, 236, 170))
        glow(img, 240, sy, 120, (255, 200, 140), 0.45 * k)
    hills(d, 130, 6, 0.03, 1.0, lerpc((30, 22, 60), (130, 90, 120), k))
    hills(d, 134, 4, 0.05, 3.0, lerpc((24, 18, 46), (110, 70, 100), k))
    d.rectangle([0, 134, W, H], fill=lerpc((26, 22, 40), (90, 70, 90), k))
    for side in (-1, 1):
        d.polygon([(240, 134), (240 + side * 4, 134), (240 + side * 330, H), (240 + side * 300, H)], fill=lerpc((200, 200, 196), (255, 240, 220), k))
    d.polygon([(240, 134), (240 - 240, H), (240 + 240, H)], fill=lerpc((36, 32, 48), (100, 84, 100), k)) if False else None
    for j in range(10):
        z = ((j + lt * 2.4) % 10) / 10
        y0 = 134 + (H - 134) * z ** 2; y1 = 134 + (H - 134) * min(1, (z + 0.04)) ** 2
        d.polygon([(240 - 1 - 4 * z, y0), (240 + 1 + 4 * z, y0), (240 + 1 + 4 * (z + 0.04), y1), (240 - 1 - 4 * (z + 0.04), y1)], fill=(240, 200, 80))
    for j in range(6):
        z = ((j + lt * 0.9) % 6) / 6
        y = 134 + (H - 134) * z ** 2
        for side in (-1, 1):
            x = 240 + side * (20 + 360 * z ** 2)
            d.line([(x, y), (x, y - 4 - 70 * z ** 2)], fill=lerpc((50, 46, 70), (120, 100, 110), k), width=max(1, int(z * 4)))
    twinkle(d, 240, 134, (lt * 0.8) % 1, (255, 255, 255), 6)
    glow(img, 240, 134, 20, (255, 255, 230), 0.5)
    bob = round(math.sin(lt * 9))
    car_rear(img, 240, 236 + bob, 3, 0.0, False)
    for b_ in range(4):
        bx = (lt * 30 + b_ * 60) % 520 - 20
        pix.bird(d, int(bx), int(60 + b_ * 9 + 3 * math.sin(lt * 2 + b_)), lt, lerpc((40, 30, 60), (80, 60, 90), k), b_)


def junction(img, d, T, lt, k_dawn):
    """天亮时的丁字路口，从车后面看：路的尽头横着一条路。左边通向她家（篮球架、亮着灯的窗），右边通往日出"""
    dawn_sky(img, d, k_dawn, 160)
    sx_, sy_ = 400, lerp(170, 112, k_dawn)
    d.ellipse([sx_ - 24, sy_ - 24, sx_ + 24, sy_ + 24], fill=(255, 236, 170)); glow(img, sx_, sy_, 110, (255, 200, 140), 0.45)
    hills(d, 152, 7, 0.02, 2.0, lerpc((40, 30, 70), (150, 100, 120), k_dawn))
    ground = lerpc((40, 36, 56), (126, 104, 112), k_dawn)
    road = lerpc((34, 32, 48), (92, 80, 96), k_dawn)
    d.rectangle([0, 158, W, H], fill=ground)
    hx = 76
    d.polygon([(hx - 44, 120), (hx, 92), (hx + 44, 120)], fill=(150, 70, 70), outline=OUT)
    d.rectangle([hx - 38, 120, hx + 38, 164], fill=(230, 214, 190), outline=OUT)
    d.rectangle([hx - 24, 130, hx - 6, 146], fill=(255, 214, 140), outline=OUT); glow(img, hx - 15, 138, 26, (255, 210, 140), 0.5)
    d.line([(hx - 15, 130), (hx - 15, 146)], fill=OUT); d.line([(hx - 24, 138), (hx - 6, 138)], fill=OUT)
    d.rectangle([hx + 10, 140, hx + 24, 164], fill=(120, 80, 60), outline=OUT)
    paste(img, pix.spr('heart', 1, tint=TEAL_L), hx - 15, 122 - 2 * math.sin(T * 3), 1, 'cc')
    d.rectangle([hx + 56, 96, hx + 58, 164], fill=(110, 110, 120)); d.rectangle([hx + 46, 90, hx + 68, 102], fill=(250, 250, 250), outline=OUT)
    d.rectangle([hx + 50, 102, hx + 64, 104], fill=(240, 80, 60))
    d.rectangle([0, 164, W, 190], fill=road)
    for x in range(0, W, 30): d.rectangle([x, 176, x + 14, 177], fill=(230, 226, 210))
    d.polygon([(196, 190), (284, 190), (420, H), (60, H)], fill=road)
    d.line([(196, 190), (60, H)], fill=(230, 226, 210), width=2); d.line([(284, 190), (420, H)], fill=(230, 226, 210), width=2)
    d.rectangle([150, 198, 330, 201], fill=(240, 236, 220))
    for j in range(4):
        y0 = 210 + j * 18
        d.rectangle([239, y0, 241, y0 + 8], fill=(240, 200, 80))
    px = 330
    d.rectangle([px, 96, px + 2, 164], fill=(110, 110, 130))
    d.polygon([(px - 40, 100), (px - 4, 100), (px - 4, 114), (px - 40, 114), (px - 48, 107)], fill=(40, 120, 80), outline=OUT)
    put(img, 'heart', px - 24, 107, 1, tint=(255, 255, 255))
    d.polygon([(px + 6, 118), (px + 42, 118), (px + 50, 125), (px + 42, 132), (px + 6, 132)], fill=(40, 120, 80), outline=OUT)
    d.ellipse([px + 20, 121, px + 26, 127], fill=(255, 230, 120))


def s_final_left(img, d, lt, dur, T, A):
    """天亮了，他的车开到丁字路口停下：左边通向她家，窗户还亮着；右边通往日出。左转灯一下一下地闪"""
    k = 0.5 + 0.2 * span(lt, 0, dur)
    junction(img, d, T, lt, k)
    u = eout(span(lt, 0, 1.4))
    y = lerp(330, 262, u)
    sig = blink_a(T)
    if sig > 0.1: glow(img, 170, 250, 60, AMB, 0.22 * sig, 16)
    car_rear(img, 240, y, 3, sig, u >= 1)
    if u >= 1 and sig > 0.5:
        text(img, '嗒', 150, 150, AMB_L, (60, 24, 10), FONT_S)
    if lt > 2.0:
        c = bubble(img, d, 200, 150, 26, 20, span(lt, 2.0, 2.3), thought=True, tail=(-1, 1))
        if c: put(img, 'heart', c[0], c[1], 1, tint=TEAL)


def s_final_right(img, d, lt, dur, T, A):
    """他还是往右转了，开向日出；左转灯闪了最后一下，“咔”地灭了"""
    k = 0.7 + 0.15 * span(lt, 0, dur)
    junction(img, d, T, lt, k)
    u = ease(span(lt, 0.15, dur))
    x = lerp(240, 470, u); y = lerp(262, 182, u)
    s_ = max(1, int(round(lerp(3, 1.2, u))))
    off = lt > 0.9
    sig = 0.0 if off else blink_a(T)
    car_rear(img, x, y, s_, sig, False, tilt=-16 * math.sin(math.pi * min(1, u * 1.3)))
    if 0.85 < lt < 1.15:
        text(img, '咔', x - 60, y - 70, (255, 255, 255), OUT, FONT_S)


def s_outro(img, d, lt, dur, T, A):
    """片尾：车子变成路尽头的一个小点开进日出里，片名重新亮起来，箭头最后闪了几下，熄灭，淡出"""
    k = 1.0
    dawn_sky(img, d, 1.0, 130)
    sy = 92 - 10 * span(lt, 0, dur)
    d.ellipse([240 - 34, sy - 34, 240 + 34, sy + 34], fill=(255, 240, 180))
    glow(img, 240, sy, 160, (255, 210, 150), 0.5)
    hills(d, 130, 6, 0.03, 1.0, (130, 90, 120))
    hills(d, 134, 4, 0.05, 3.0, (110, 70, 100))
    d.rectangle([0, 134, W, H], fill=(96, 74, 92))
    for side in (-1, 1):
        d.polygon([(240, 134), (240 + side * 4, 134), (240 + side * 330, H), (240 + side * 300, H)], fill=(255, 236, 214))
    for j in range(10):
        z = ((j + lt * 1.0) % 10) / 10
        y0 = 134 + (H - 134) * z ** 2; y1 = 134 + (H - 134) * min(1, (z + 0.04)) ** 2
        d.polygon([(240 - 1 - 4 * z, y0), (240 + 1 + 4 * z, y0), (240 + 1 + 4 * (z + 0.04), y1), (240 - 1 - 4 * (z + 0.04), y1)], fill=(240, 200, 80))
    u = ease(span(lt, 0, 3.0))
    s = max(1, int(round(lerp(3, 1, u))))
    y = lerp(236, 140, u)
    if u < 1: car_rear(img, 240, y, s, 0.0, False)
    else: d.rectangle([239, 138, 241, 140], fill=(60, 40, 60))
    if lt > 2.2:
        s_, pts, x0 = intro_title_layout(3)
        a = ease(span(lt, 2.2, 3.0))
        adv = [FONT.getlength(c) * 3 for c in s_]
        gx = 240 - sum(adv) / 2
        for i, ch in enumerate(s_):
            g = big_glyph(ch, 3, AMB_L, AMB, (150, 66, 18))
            paste(img, g, gx - 12 + 2, 40 - 30, a, 'lt')
            gx += adv[i]
        nb = len(beats_in(T - lt + 3.0, T + 0.01))
        on = blink_a(T) if nb <= 4 else 0.0
        props.arrow(img, 240 - sum(adv) / 2 - 22, 40 + 2, 2, on * a, glow_r=18)
        props.arrow(img, 240 + sum(adv) / 2 + 22, 40 + 2, 2, 0.0, left=False, glow_r=0) if a > 0.5 else None
    if lt > dur - 2.2:
        dither_fade(img, ease((lt - dur + 2.2) / 2.0), (0, 0, 0))
