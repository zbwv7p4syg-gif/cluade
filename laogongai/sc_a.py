"""老公爱 · 片头和第一段主歌（0 – 35.9 秒）。签名都是 (img, d, lt, dur, T, A)：lt 是镜头内的时间，dur 是镜头时长，T 是全片时间。

片头：黑暗里一颗像素心在跳，第一个鼓点上霓虹城市亮起来，“老 公 爱”三个大字一个接一个砸下来，周围乱弹聊天气泡（messed it around）；
然后他戴上墨镜，一道扫描光照穿她说的“爱你”，气泡翻成 LIES（see through your lies）。
主歌：拍立得一张张化成像素灰飞走、在手机上弹钢琴、楼顶分一副耳机听前奏、天平上两堆“谎”、雨夜路口、删短信、开启勿扰出门遇见新的人。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
import motifs as M
import kit as K
from props import shots, shake, zoom, person_s, dpaste, big_glyph, thump, last_beat, beats_in, polaroid, bokeh, reflect, splashes
from pix import (W, H, FONT, FONT_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky, stars,
                 person, wph, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, BAYER, rain, petals)

GOLDEN = props.GOLDEN
DAY = props.DAY


def burst_bg(img, d, T, c1, c2, cx=W / 2, cy=H / 2, n=16, spin=0.3):
    """放射状的条纹背景"""
    d.rectangle([0, 0, W, H], fill=c1)
    for i in range(n):
        a0 = 2 * math.pi * i / n + T * spin
        a1 = a0 + math.pi / n
        R = 600
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=c2)


@lru_cache(None)
def photo_two(kind=0):
    """拍立得里的两个人：粉色背景，两张笑脸挨着"""
    im = Image.new('RGB', (44, 34), [(255, 170, 200), (150, 200, 255), (255, 210, 140)][kind % 3])
    d = ImageDraw.Draw(im)
    for i in range(6): d.point((i * 7 + 3, 4 + (i % 2) * 3), fill=(255, 255, 255))
    b = props.head_img('boy', expr='happy', s=1); g = props.head_img('girl', expr='laugh' if kind != 1 else 'shy', s=1)
    im.paste(b, (5, 14), b); im.paste(g, (22, 14), g)
    pix.put(im, 'heart', 22, 9, 1)
    return im


# ================================================================ 片头
CHAT_POP = [('在吗', 'l'), ('?', 'r'), ('老公', 'l'), ('晚安♥', 'r'), ('你在哪', 'l'), ('...', 'r'), ('想你', 'l'), ('别闹', 'r'),
            ('哼', 'l'), ('爱你♥', 'r'), ('回我', 'l'), ('!!', 'r')]


def s_intro(img, d, lt, dur, T, A):
    hit = 0.6                                                     # 第一个鼓点
    drops = [hit, hit + 0.28, hit + 0.56]
    lie_at = 3.6
    if lt < hit:                                                  # 黑暗里一颗小心在跳
        d.rectangle([0, 0, W, H], fill=(4, 2, 10))
        s = 1 + (lt / hit) * 1.2 + 0.4 * math.sin(lt * 18)
        K.pix_heart(img, W / 2, H / 2, max(0.5, s * 0.5), alpha=clamp(lt / 0.3))
        glow(img, W / 2, H / 2, 40 + lt * 40, K.PINK, 0.3 * clamp(lt / 0.3))
        return
    k = lt - hit
    off = T * 14
    K.night_city(img, d, T, off)
    # 鼓点上炸开的烟花
    for i, t0 in enumerate((hit, drops[2], hit + 1.3, hit + 2.0, hit + 2.6)):
        pix.firework(img, d, lt, t0 - 0.5, [90, 390, 150, 330, 240][i], [40, 50, 30, 36, 24][i], [K.PINK, K.CYAN, K.YEL, K.PURP, K.PINK][i],
                     r=40 + 6 * (i % 2), life=1.4, seed=i)
    # 地上的人
    if lt > lie_at - 0.3:
        u = eout((lt - lie_at + 0.3) / 0.6)
        bx, gx, gy = lerp(-40, 150, u), lerp(W + 40, 334, u), 232
        cool = lt > lie_at + 0.5
        person(img, 'boy', bx, gy, view='front', expr='cool' if cool else 'smile', arms='cross' if cool else 'auto', s=3)
        if lie_at + 0.2 < lt < lie_at + 0.6:                        # 墨镜从上面掉下来
            f = (lt - lie_at - 0.2) / 0.4
            d.rectangle([bx - 13, lerp(60, 145, ein(f)), bx + 12, lerp(60, 145, ein(f)) + 4], fill=(16, 14, 24))
        person(img, 'girl', gx, gy, view='side', flip=True, expr='happy' if lt < lie_at + 1.4 else 'surprised', s=3)
        # 她的气泡：爱你 → 被扫描光照穿 → LIES
        if lt > lie_at + 0.3:
            sc_t = lt - lie_at - 0.9
            lie = sc_t > 0.5
            bw = 92
            bx0, by0 = 300, 76
            d.rounded_rectangle([bx0 - 1, by0 - 1, bx0 + bw + 1, by0 + 31], 6, fill=pix.OUT)
            d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + 30], 6, fill=(255, 255, 255) if not lie else (40, 10, 30))
            d.polygon([(bx0 + 30, by0 + 30), (bx0 + 42, by0 + 30), (bx0 + 34, by0 + 40)], fill=(255, 255, 255) if not lie else (40, 10, 30))
            if not lie:
                text(img, '老公我爱你♥', bx0 + bw / 2, by0 + 15, col=(255, 70, 150), shadow=False)
            else:
                K.neon(img, 'LIES', bx0 + bw / 2, by0 + 15, 2, (255, 60, 80), K.flicker(T, 3, 0.15))
            if sc_t > 0:                                           # 扫描光：从他的墨镜射出去，扫过气泡
                ex, ey = bx + 6, 147
                f = clamp(sc_t / 0.8)
                ty_ = lerp(by0 - 6, by0 + 36, tri_(f * 2))
                tfill(img, 'polygon', [(ex, ey - 1), (ex, ey + 2), (bx0 + bw + 6, ty_ + 4), (bx0 - 6, ty_ - 4)], (120, 255, 240), 0.35 * (1 - f * 0.6))
                d.line([(bx0 - 4, ty_), (bx0 + bw + 4, ty_)], fill=(200, 255, 250))
            if 0.45 < sc_t < 0.75: K.glitch(img, T, 1.0, 5)
    # 乱弹的聊天气泡（messed it around）
    if lt < lie_at + 0.3:
        for i, (s, side) in enumerate(CHAT_POP):
            t0 = hit + 0.15 + i * 0.22
            if lt < t0: continue
            r = rng(i * 5 + 1)
            x = r.choice([r.uniform(20, 140), r.uniform(330, 440)])
            y = r.uniform(140, 210) if i % 3 else r.uniform(18, 60)
            a = clamp((lt - t0) / 0.1) * clamp((lie_at + 0.3 - lt) / 0.3)
            dy = -4 * eback(clamp((lt - t0) / 0.2)) + 2 * math.sin(T * 3 + i)
            K.bubble(img, d, x, y + dy, s, side, (255, 255, 255) if side == 'l' else (150, 240, 160), a=a)
    # 片名：三个字一个接一个砸下来；唱到 see through your lies 时缩小挪到上面
    small = lt > lie_at
    sc = 3 if small else 4
    cy = 54 if small else 104
    if small and lt < lie_at + 0.25: cy = lerp(104, 54, eout((lt - lie_at) / 0.25))
    chars = '老公爱'
    adv = FONT.getlength('老') * sc
    x0 = W / 2 - adv * 1.5 - 4 * sc
    glow(img, W / 2, cy, 64 * sc, K.PINK, 0.35 * clamp(k / 0.3) * (0.85 + 0.15 * math.sin(T * 4)), 22 * sc)
    for i, ch in enumerate(chars):
        if lt < drops[i]: continue
        f = clamp((lt - drops[i]) / 0.16)
        g = big_glyph(ch, sc, **K.TITLE_KW)
        y = lerp(-g.height, cy - g.height / 2, ein(f))
        if f >= 1: y -= 6 * math.sin(clamp((lt - drops[i] - 0.16) / 0.25) * math.pi) * (1 - clamp((lt - drops[i] - 0.16) / 0.25))
        bob = 2 * math.sin(T * 3 + i * 1.3) if lt > drops[2] + 0.5 else 0
        img.paste(g, (int(x0 + i * adv), int(y + bob)), g)
        if f >= 1 and lt - drops[i] < 0.5:
            for j in range(8):
                a = j / 8 * 2 * math.pi
                q = (lt - drops[i] - 0.16) / 0.34
                px, py = x0 + i * adv + g.width / 2 + math.cos(a) * 40 * eout(q), cy + 30 + math.sin(a) * 18 * eout(q)
                if q < 1: d.rectangle([px, py, px + 2, py + 2], fill=K.PINK_L if j % 2 else K.YEL)
    for t0 in drops:
        if t0 <= lt < t0 + 0.4: shake(img, lt - t0 - 0.16, 5, 0.25)
    if lt < hit + 0.12: pix.dither_fade(img, 1 - (lt - hit) / 0.12, (255, 240, 250))
    # 副标题
    if hit + 1.0 < lt < lie_at:
        a = clamp((lt - hit - 1.0) / 0.4) * clamp((lie_at - lt) / 0.2)
        text(img, '· 像 素 动 画 M V ·', W / 2, 170, col=(255, 220, 240), font=FONT_S, alpha=a)
    vig(img, 0.35, (10, 4, 24))


def tri_(f): return 1 - abs(2 * (f % 1) - 1)


# ================================================================ 太小心被遗忘：拍立得化成像素灰
def s_forget(img, d, lt, dur, T, A):
    K.room(img, d, T, 1.0, wall=(48, 34, 74))
    darken(img, 0.25, (10, 6, 24))
    person(img, 'boy', 240, 226, view='front', pose='sit', expr='down', s=3)
    for i, (px, py, rot) in enumerate(((140, 80, -8), (240, 56, 4), (340, 84, 9))):
        f = clamp((lt - 0.4 - i * 0.5) / 1.6)
        ph = photo_two(i)
        pw, phh = ph.size
        im = Image.new('RGBA', (pw + 8, phh + 18), props.CREAM + (255,))
        im.paste(ph if f < 0.2 else props.sepia(ph, f), (4, 4))
        im = pix.outline(im, pix.OUT).rotate(rot, resample=Image.NEAREST, expand=True)
        a = np.array(im)
        bm = pix.bayer(a.shape[0], a.shape[1], 0, 0)
        grad = (np.arange(a.shape[1])[None, :] / a.shape[1]) * 0.5 + bm * 0.5
        a[grad < f * 1.3 - 0.15, 3] = 0                     # 从左往右一点点化掉
        bob = 2 * math.sin(T * 1.5 + i)
        img.paste(Image.fromarray(a), (int(px - a.shape[1] / 2), int(py - a.shape[0] / 2 + bob)), Image.fromarray(a))
        # 化掉的像素灰往窗外飘
        for j in range(26):
            r = rng(i * 100 + j)
            t0 = r.random() * 1.6
            q = (lt - 0.4 - i * 0.5 - t0)
            if q < 0 or q > 1.6: continue
            x = px - 20 + r.random() * 40 + q * (60 + 40 * r.random())
            y = py - 14 + r.random() * 30 - q * (30 + 20 * r.random())
            d.point((x, y), fill=lerpc((255, 220, 230), (90, 70, 120), q / 1.6))
    vig(img, 0.45, (8, 4, 20))


# ================================================================ 我还会在手机弹奏
def s_phone_piano(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(22, 14, 40))
    bokeh(img, T, 12, a=0.25)
    x0, y0, w, h = 168, 12, 144, 250
    sx0, sy0, sx1, sy1 = K.phone(img, d, x0, y0, w, h)
    K.status_bar(d, (sx0, sy0, sx1, sy1), T)
    d.rectangle([sx0, sy0 + 10, sx1, sy1], fill=(36, 20, 60))
    text(img, 'PIANO ♪', (sx0 + sx1) / 2, sy0 + 24, col=(255, 220, 240), font=FONT_S)
    # 壁纸：他们俩的小照片
    ph = photo_two(0).resize((88, 68), Image.NEAREST)
    img.paste(ph, (int((sx0 + sx1) / 2 - 44), sy0 + 36))
    d.rectangle([(sx0 + sx1) / 2 - 45, sy0 + 35, (sx0 + sx1) / 2 + 44, sy0 + 104], outline=(255, 160, 210))
    # 琴键
    ky0 = sy0 + 116
    n_hits = int(lt / 0.36)
    key = (n_hits * 3) % 8
    pressing = (lt % 0.36) < 0.16
    K.keys(d, sx0 + 4, ky0, sx1 - sx0 - 8, sy1 - ky0 - 6, 8, lit=(key,) if pressing else ())
    kw = (sx1 - sx0 - 8) / 8
    fx = sx0 + 4 + kw * (key + 0.5)
    K.finger(d, fx, ky0 + 46, 2, 1.0 if pressing else 0.0)
    # 音符从手机里飘出来
    for j in range(n_hits + 1):
        q = lt - j * 0.36
        if q < 0 or q > 1.6: continue
        r = rng(j)
        nx = sx0 + 10 + ((j * 3) % 8) * kw + q * 30 * (r.random() - 0.5) * 2
        ny = ky0 - 10 - q * 90
        K.note(img, nx, ny, j, [K.PINK, K.CYAN, K.YEL, K.PURP][j % 4], 2 if q < 1.2 else 1)
    vig(img, 0.4, (10, 4, 24))


# ================================================================ 属于我们的前奏：楼顶分一副耳机
def s_rooftop(img, d, lt, dur, T, A):
    sky(img, GOLDEN, 0, 200, 6)
    glow(img, 380, 160, 120, (255, 220, 160), 0.5)
    d.ellipse([360, 140, 400, 180], fill=(255, 236, 190))
    for i in range(4): cloud(d, (i * 140 + T * 6) % (W + 120) - 80, 30 + i * 18, 1.4 + i * 0.2, (255, 200, 180), (240, 160, 160))
    pix.city(img, d, 210, 9, T * 4, (150, 90, 130), (255, 230, 170), 40, 110, 0.2, T)
    pix.city(img, d, 222, 3, T * 8, (100, 56, 100), (255, 210, 140), 20, 70, 0.3, T)
    d.rectangle([0, 200, W, H], fill=(70, 50, 80)); d.rectangle([0, 196, W, 202], fill=(110, 84, 110))
    for x in range(0, W, 16): d.line([(x, 202), (x, H)], fill=(60, 42, 70))
    bx, gx, y = 214, 262, 198
    person(img, 'boy', bx, y, view='side', pose='sit', expr='closed', s=3)
    person(img, 'girl', gx, y, view='side', pose='sit', expr='happy', flip=True, s=3)
    # 耳机线：从两个人的耳朵垂下来，在中间并成一根
    d.line([(bx + 9, 130), (238, 170), (gx - 9, 130)], fill=(255, 255, 255))
    d.line([(238, 170), (236, 186)], fill=(255, 255, 255))
    d.rectangle([bx + 7, 128, bx + 10, 132], fill=(255, 255, 255)); d.rectangle([gx - 10, 128, gx - 7, 132], fill=(255, 255, 255))
    K.notes_rise(img, T, 238, 110, n=7, spread=120, h=100, seed=2, s=1)
    for j in range(5):
        r = rng(j + 40)
        q = (T * 0.4 + r.random()) % 1
        pix.put(img, 'heart', 238 + (r.random() - 0.5) * 80, 120 - q * 100, 1, alpha=1 - q)
    vig(img, 0.35, (60, 20, 50))


# ================================================================ 天平：我的谎话 vs 你的谎话
def s_scale(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(30, 18, 52))
    tfill(img, 'polygon', [(200, 0), (280, 0), (380, 236), (100, 236)], (255, 220, 255), 0.08)
    d.rectangle([0, 236, W, H], fill=(20, 12, 36))
    glow(img, 240, 236, 160, K.PURP, 0.2, 20)
    # 右边越堆越多
    n_r = int(clamp((lt - 0.8) / 4.0) * 14)
    n_l = 2 if lt > 0.4 else (1 if lt > 0.2 else 0)
    tilt = clamp(n_r / 10) * 1.0 - 0.0
    tilt = lerp(-0.2, tilt, clamp(lt / 1.0)) + 0.05 * math.sin(T * 6) * (1 - clamp(lt / 5))
    (lx, ly), (rx, ry) = K.balance(img, d, 240, 236, tilt, 120)
    # 两个盘子上的头像
    hb, hg = props.head_img('boy', expr='surprised', s=1), props.head_img('girl', expr='sneer' if lt > 3 else 'smile', s=1)
    for i in range(n_l):
        K.brick(img, d, lx - 6 + i * 13, ly - 6, 6, (120, 160, 255), '谎')
    for i in range(n_r):
        col = (255, 80, 140) if i % 2 else (255, 120, 170)
        row, c = divmod(i, 4)
        bx = rx - 21 + c * 14 + (row % 2) * 7
        by = ry - 7 - row * 14
        t_land = 0.8 + i * (4.0 / 14)
        f = clamp((lt - t_land + 0.25) / 0.25)
        by = lerp(-20, by, ein(f))
        K.brick(img, d, bx, by, 7, col, '谎')
    img.paste(hb.resize((32, 36), Image.NEAREST), (int(lx - 16), int(ly + 8)), hb.resize((32, 36), Image.NEAREST))
    img.paste(hg.resize((32, 36), Image.NEAREST), (int(rx - 16), int(ry + 8)), hg.resize((32, 36), Image.NEAREST))
    if n_r and abs((lt - 0.8) % (4.0 / 14)) < 0.06: shake(img, 0.0, 2, 0.2)
    # 两边的标签
    K.neon(img, '我', 70, 60, 2, K.CYAN, 1)
    K.neon(img, '你', 410, 60, 2, K.PINK, K.flicker(T, 2))
    text(img, f'x{n_l}', 70, 92, col=(200, 220, 255))
    text(img, f'x{n_r}', 410, 92, col=(255, 200, 230))
    vig(img, 0.4, (8, 4, 20))


# ================================================================ How I didn't notice before 你在哪个路口
def crossroad_side(img, d, t):
    T = t
    sky(img, ((0, (10, 10, 30)), (1, (40, 30, 70))), 0, 200, 4)
    pix.city(img, d, 200, 21, 0, (30, 24, 54), (255, 220, 150), 40, 130, 0.3, T)
    d.rectangle([0, 200, W, H], fill=(28, 24, 40))
    for x in range(10, W, 26): d.rectangle([x, 222, x + 14, 228], fill=(200, 200, 210))     # 斑马线
    K.traffic_light(img, d, 380, 210, 0 if t < 1.4 else 2, T)
    pix.lamp(img, d, 120, 210, 1.0)
    # 车灯一道道划过
    for i in range(3):
        q = (t * 1.3 + i / 3) % 1
        x = lerp(-80, W + 80, q) if i % 2 else lerp(W + 80, -80, q)
        d.rectangle([x, 236, x + 50, 240], fill=(255, 240, 180) if i % 2 else (255, 60, 60))
        glow(img, x + 25, 238, 40, (255, 230, 160) if i % 2 else (255, 80, 80), 0.3, 6)
    look = int(t * 1.6) % 2
    person(img, 'boy', 240, 226, view='side', flip=bool(look), expr='worried', s=3)
    text(img, '?', 240 + (12 if not look else -12), 112, col=(255, 240, 120), scale=2)
    rain(d, t, 0, W, 0, H, 140, (130, 140, 200), 260, -3, 6)
    splashes(d, t, 200, H, 20)
    reflect(img, 230, 40, t, a=0.4)


def crossroad_map(img, d, t):
    d.rectangle([0, 0, W, H], fill=(36, 30, 56))
    for x in range(0, W, 80): d.rectangle([x + 30, 0, x + 50, H], fill=(60, 54, 80))
    for y in range(0, H, 70): d.rectangle([0, y + 26, W, y + 44], fill=(60, 54, 80))
    for x in range(0, W, 80):
        for y in range(0, H, 70):
            d.rectangle([x + 2, y + 2, x + 26, y + 22], fill=(48, 40, 72))
            r = rng(x * 3 + y)
            if r.random() < 0.5: d.rectangle([x + 6, y + 6, x + 20, y + 18], fill=(70, 60, 100))
    # 他在一个路口转来转去，她在很远的另一个路口
    hx = [120, 120, 200, 200][int(t * 2.4) % 4]; hy = [105, 175, 175, 105][int(t * 2.4) % 4]
    gx, gy = 360, 35
    glow(img, gx, gy, 30, K.PINK, 0.5 * (0.6 + 0.4 * math.sin(t * 8)))
    pix.put(img, 'heart', gx, gy, 2)
    glow(img, hx, hy, 24, K.CYAN, 0.4)
    d.ellipse([hx - 5, hy - 5, hx + 5, hy + 5], fill=K.CYAN, outline=pix.OUT)
    for i, (qx, qy) in enumerate(((40, 105), (200, 35), (280, 175), (440, 105), (360, 245))):
        if (int(t * 3) + i) % 3: text(img, '?', qx, qy, col=(255, 240, 160))


def s_crossroad(img, d, lt, dur, T, A):
    shots(img, lt, [(0, crossroad_side), (2.2, crossroad_map)], 0.3)
    vig(img, 0.4, (6, 4, 20))


# ================================================================ 终于下定决心去删掉那些短信
MSGS = [('宝贝早安', 'l'), ('想你了', 'r'), ('在干嘛', 'l'), ('晚安♥', 'r'), ('明天见', 'l'), ('爱你', 'r'), ('笨蛋', 'l')]


def s_delete(img, d, lt, dur, T, A):
    d.rectangle([0, 0, W, H], fill=(18, 12, 32))
    bokeh(img, T, 10, a=0.2)
    sx0, sy0, sx1, sy1 = K.phone(img, d, 160, 6, 160, 258)
    d.rectangle([sx0, sy0, sx1, sy1], fill=(240, 236, 248))
    K.status_bar(d, (sx0, sy0, sx1, sy1), T)
    d.rectangle([sx0, sy0 + 10, sx1, sy0 + 26], fill=(255, 120, 180))
    text(img, '♥ 她', (sx0 + sx1) / 2, sy0 + 18, col=(255, 255, 255), font=FONT_S)
    del_at = 2.2
    for i, (s, side) in enumerate(MSGS):
        y = sy0 + 32 + i * 24
        x = sx0 + 6 if side == 'l' else sx1 - 6
        t0 = del_at + 0.15 + i * 0.22
        if lt < t0:
            K.bubble(img, d, x, y, s, side, (255, 255, 255) if side == 'l' else (150, 236, 160))
        else:
            q = lt - t0                                          # 碎成像素往下掉
            for j in range(22):
                r = rng(i * 50 + j)
                px = (x + r.uniform(0, 50)) if side == 'l' else (x - r.uniform(0, 50))
                py = y + r.uniform(0, 14) + 140 * q * q + 20 * q
                if py < sy1: d.rectangle([px, py, px + 1, py + 1], fill=(255, 255, 255) if side == 'l' else (150, 236, 160))
    # 长按 → 弹框 → 点删除
    if 0.9 < lt < del_at + 0.4:
        if lt > 1.5:
            px0, py0 = sx0 + 10, sy0 + 92
            d.rounded_rectangle([px0 - 1, py0 - 1, sx1 - 9, py0 + 61], 5, fill=pix.OUT)
            d.rounded_rectangle([px0, py0, sx1 - 10, py0 + 60], 5, fill=(255, 255, 255))
            text(img, '删除聊天记录？', (sx0 + sx1) / 2, py0 + 16, col=(40, 30, 50), font=FONT_S, shadow=False)
            d.rounded_rectangle([px0 + 8, py0 + 34, px0 + 58, py0 + 52], 3, fill=(220, 220, 230))
            d.rounded_rectangle([sx1 - 68, py0 + 34, sx1 - 18, py0 + 52], 3, fill=(255, 60, 80) if lt < del_at else (200, 30, 60))
            text(img, '取消', px0 + 33, py0 + 43, col=(60, 60, 80), font=FONT_S, shadow=False)
            text(img, '删除', sx1 - 43, py0 + 43, col=(255, 255, 255), font=FONT_S, shadow=False)
            fx, fy = sx1 - 43, py0 + 46
        else:
            fx, fy = sx0 + 40, sy0 + 108
        K.finger(d, fx, fy, 2, 1.0 if (1.0 < lt < 1.5 or del_at - 0.1 < lt < del_at + 0.1) else 0)
    if del_at - 0.05 < lt < del_at + 0.25: shake(img, lt - del_at, 3, 0.25)
    # 垃圾桶
    tx, ty = (sx0 + sx1) / 2, sy1 - 18
    if lt > del_at:
        d.rectangle([tx - 12, ty - 10, tx + 12, ty + 12], fill=(120, 120, 140), outline=pix.OUT)
        d.rectangle([tx - 15, ty - 14, tx + 15, ty - 10], fill=(150, 150, 170), outline=pix.OUT)
        for k in (-6, 0, 6): d.line([(tx + k, ty - 6), (tx + k, ty + 8)], fill=(90, 90, 110))
    if lt > 4.0:
        a = clamp((lt - 4.0) / 0.15)
        d.rounded_rectangle([tx - 36, sy0 + 120, tx + 36, sy0 + 140], 5, fill=(30, 30, 40))
        text(img, '已删除', tx, sy0 + 130, col=(255, 255, 255), font=FONT_S, alpha=a, shadow=False)
    vig(img, 0.4, (6, 4, 20))


# ================================================================ 不再打扰你，我已经开启新的邂逅
def dnd(img, d, t):
    d.rectangle([0, 0, W, H], fill=(20, 14, 36))
    sx0, sy0, sx1, sy1 = K.phone(img, d, 170, 10, 140, 250)
    d.rectangle([sx0, sy0, sx1, sy1], fill=(40, 36, 70))
    on = t > 0.8
    for i, name in enumerate(('勿扰模式', 'WiFi', '飞行')):
        y = sy0 + 30 + i * 46
        lit = (i == 0 and on)
        d.rounded_rectangle([sx0 + 10, y, sx1 - 10, y + 36], 8, fill=(150, 100, 255) if lit else (70, 64, 100))
        text(img, name, sx0 + 50, y + 18, col=(255, 255, 255), font=FONT_S)
        d.rounded_rectangle([sx1 - 44, y + 10, sx1 - 18, y + 26], 8, fill=(255, 255, 255) if lit else (110, 104, 140))
        kx = sx1 - 26 if lit else sx1 - 36
        d.ellipse([kx - 6, y + 12, kx + 6, y + 24], fill=(150, 100, 255) if lit else (230, 230, 240))
    if on:
        q = t - 0.8
        moon(d, (sx0 + sx1) / 2, sy1 - 50, 14 + 2 * math.sin(t * 4))
        d.ellipse([(sx0 + sx1) / 2 + 2, sy1 - 68, (sx0 + sx1) / 2 + 26, sy1 - 44], fill=(40, 36, 70))
        for j in range(4): twinkle(d, sx0 + 20 + j * 28, sy1 - 80 + (j % 2) * 30, (q * 2 + j * 0.3) % 1, (255, 240, 180))
    if t < 0.95: K.finger(d, sx1 - 26, sy0 + 50, 2, 1.0 if t > 0.7 else 0)


def sunny_street(img, d, t):
    off = t * 40
    sky(img, DAY, 0, 200, 5)
    for i in range(4): cloud(d, (i * 150 - off * 0.2) % (W + 120) - 80, 20 + i * 14, 1.6, (255, 255, 255), (220, 230, 245))
    # 樱花树和小店
    for i in range(7):
        x = (i * 90 - off) % (W + 120) - 60
        if i % 2:
            d.rectangle([x - 30, 120, x + 30, 200], fill=[(255, 220, 200), (200, 230, 255), (255, 240, 180)][i % 3])
            d.rectangle([x - 34, 112, x + 34, 122], fill=[(255, 120, 150), (100, 160, 240), (255, 180, 60)][i % 3])
            for k in range(-30, 34, 8): d.rectangle([x + k, 122, x + k + 3, 128], fill=(255, 255, 255))
            d.rectangle([x - 20, 140, x + 2, 170], fill=(150, 210, 255)); d.rectangle([x + 8, 150, x + 22, 200], fill=(140, 90, 70))
        else:
            pix.tree_round(d, x, 200, 1.5, (255, 170, 200), (255, 210, 225), (120, 80, 70))
    d.rectangle([0, 200, W, H], fill=(210, 200, 200)); d.line([(0, 200), (W, 200)], fill=(170, 160, 170))
    for x in range(int(-off) % 30 - 30, W, 30): d.line([(x, 200), (x - 20, H)], fill=(190, 180, 186))
    petals(d, t, 50, speed=26, wind=30)
    # 他走出来；对面走来一个女孩，差点撞上
    meet = 2.0
    bx = lerp(-30, 210, clamp(t / meet))
    walking = t < meet
    person(img, 'boy', bx, 232, view='side', pose='walk' if walking else 'stand', ph=wph(t), expr='cool', s=3)
    if t > 0.8:
        gx = lerp(W + 30, 290, clamp((t - 0.8) / (meet - 0.8)))
        person(img, 'girl', gx, 232, 'alt', view='side', pose='walk' if walking else 'stand', ph=wph(t), flip=True,
               expr='surprised' if not walking else 'smile', s=3)
    if t > meet:
        q = t - meet
        K.heart_burst(img, d, q, 250, 130, 10, 50, life=0.9)
        if q > 0.3: K.bubble(img, d, 300, 80, 'Hi~♥', 'l', a=clamp((q - 0.3) / 0.2))
        if q > 0.5: K.bubble(img, d, 210, 70, '!', 'r', (150, 236, 160), a=clamp((q - 0.5) / 0.2))


def s_new_day(img, d, lt, dur, T, A):
    shots(img, lt, [(0, dnd), (2.0, sunny_street)], 0.3, 'white')
    vig(img, 0.25, (40, 30, 60))
