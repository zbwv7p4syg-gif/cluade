"""左转灯 · 说唱段。签名都是 (img, d, lt, dur, T, A)。

他在酒吧喝多了，酒瓶长出小犄角，用提线拽着他的手拿起手机；楼梯上扶着扶手，想起今天遇到一个穿球衣的女孩很像她；
发不发消息的念头在床上翻来覆去；地图上找不到她，号码删了也记不得；日子撕掉一页又一页，人掉进一个圈里。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
from props import *          # noqa: F401,F403
from pix import person, wph, put, twinkle, sparkle, moon, cloud, darken, dither_fade, vig, vgrad, bayer
from sc_verse import (bar_near, beat_after, rain_lit, paper, court_photo, tree_top, rain_top, umbrella_top, dialog, cursor,
                      car_reflection)

# 今天遇到的那个女孩：浅一点的头发，穿红色球衣
pix.LOOK[('girl', 'other')] = dict(pix.LOOK[('girl', 'young')], hair=(150, 96, 62), hair_s=(116, 70, 46), hair_l=(190, 136, 90),
                                   top=(232, 76, 84), top_s=(186, 50, 64), low=(232, 76, 84), low_s=(186, 50, 64))


def wobble(img, amt, T, freq=0.045, speed=2.6):
    """醉意：每一行左右晃"""
    if amt <= 0: return
    a = np.asarray(img)
    out = np.empty_like(a)
    for y in range(H):
        out[y] = np.roll(a[y], int(round(amt * math.sin(y * freq + T * speed))), axis=0)
    img.paste(Image.fromarray(out))


def oshape(d, box, col, r=4, out=OUT):
    d.rounded_rectangle([box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1], r + 1, fill=out)
    d.rounded_rectangle(box, r, fill=col)


# ---------------------------------------------------------------- 坏酒瓶
def bad_bottle(img, d, x, y, t, horns=1.0, s=1, face=True):
    """一个长着小犄角和尾巴的绿酒瓶（原创的小角色），(x, y) 是瓶底中点"""
    g, gs, gl = (60, 150, 90), (40, 110, 66), (130, 210, 150)
    w = 12 * s; h = 30 * s; nk = 10 * s
    oshape(d, [x - w / 2, y - h, x + w / 2, y], g, 3 * s)
    oshape(d, [x - 3 * s, y - h - nk, x + 3 * s, y - h + 2], g, s)
    d.rectangle([x - 3 * s, y - h - nk - 3 * s, x + 3 * s, y - h - nk], fill=(200, 60, 60), outline=OUT)
    d.rectangle([x - w / 2 + s, y - h + 6 * s, x + w / 2 - s, y - h + 16 * s], fill=(250, 240, 210))
    d.line([(x - w / 2 + 2 * s, y - h + 2 * s), (x - w / 2 + 2 * s, y - 4 * s)], fill=gl, width=s)
    d.rectangle([x - w / 2 + s, y - 6 * s, x + w / 2 - s, y - s], fill=gs)
    if face:
        ey = y - h + 9 * s
        for ex in (x - 3 * s, x + 2 * s):
            d.rectangle([ex, ey, ex + s, ey + s], fill=OUT)
        d.line([(x - 3 * s, ey + 4 * s), (x, ey + 5 * s), (x + 3 * s, ey + 3 * s)], fill=OUT, width=max(1, s))
        d.line([(x - 4 * s, ey - 2 * s), (x - 2 * s, ey - s)], fill=OUT, width=max(1, s)); d.line([(x + 4 * s, ey - 2 * s), (x + 2 * s, ey - s)], fill=OUT, width=max(1, s))
    if horns > 0:
        hh = 6 * s * horns
        for sx in (-1, 1):
            bx = x + sx * 3 * s
            d.polygon([(bx - s, y - h - nk - 3 * s), (bx + s * sx * 2, y - h - nk - 3 * s - hh), (bx + s, y - h - nk - 3 * s)], fill=(220, 40, 60), outline=OUT)
        tx = x + w / 2
        pts = [(tx, y - 6 * s), (tx + 6 * s * horns, y - 4 * s + 3 * s * math.sin(t * 6)), (tx + 10 * s * horns, y - 10 * s + 2 * s * math.sin(t * 6 + 1))]
        d.line(pts, fill=(220, 40, 60), width=max(1, s))
        ex, ey = pts[-1]
        d.polygon([(ex - 2 * s, ey), (ex + 2 * s, ey - 3 * s), (ex + 2 * s, ey + 2 * s)], fill=(220, 40, 60), outline=OUT)


def bar_bg(img, d, T, lt):
    img.paste((40, 18, 36), (0, 0, W, H))
    for x in range(0, W, 16): d.line([(x, 0), (x, 180)], fill=(46, 22, 42))
    for k, y in enumerate((44, 84, 124)):                          # 酒柜
        d.rectangle([40, y + 26, 440, y + 30], fill=(90, 56, 46), outline=OUT)
        glow(img, 240, y + 18, 220, (255, 170, 90), 0.08, 14)
        r = rng(k * 5)
        x = 50
        while x < 430:
            bw = r.randint(8, 12); bh = r.randint(16, 24)
            c = r.choice([(60, 150, 90), (180, 80, 50), (120, 60, 140), (220, 180, 80), (80, 120, 200), (200, 200, 210)])
            d.rectangle([x, y + 26 - bh, x + bw, y + 26], fill=c, outline=OUT)
            d.rectangle([x + bw // 2 - 1, y + 26 - bh - 5, x + bw // 2 + 1, y + 26 - bh], fill=c, outline=OUT)
            d.line([(x + 2, y + 28 - bh), (x + 2, y + 22)], fill=lerpc(c, (255, 255, 255), 0.45))
            x += bw + r.randint(3, 7)
    pp = 0.75 + 0.25 * math.sin(T * 11) if int(T * 2.3) % 9 else 0.25
    neon_rect(img, d, [180, 8, 300, 36], PINK, pp)
    big_text(img, 'BAR', 222, 22, 1, PINK, (255, 200, 230), pp)
    x = 274
    d.rectangle([x - 6, 14, x + 4, 30], outline=lerpc((60, 30, 50), AMB, pp)); d.arc([x + 1, 17, x + 9, 26], 270, 90, fill=lerpc((60, 30, 50), AMB, pp))
    for lx in (110, 370):
        d.line([(lx, 0), (lx, 150)], fill=(30, 20, 30))
        d.polygon([(lx - 10, 150), (lx + 10, 150), (lx + 6, 142), (lx - 6, 142)], fill=AMB_D, outline=OUT)
        tfill(img, 'polygon', [(lx - 8, 151), (lx + 8, 151), (lx + 40, 200), (lx - 40, 200)], (255, 210, 140), 0.12)
        glow(img, lx, 152, 14, (255, 230, 170), 0.6)


def s_bar(img, d, lt, dur, T, A):
    """酒吧吧台前，他趴在台上，一杯啤酒滑到面前；旁边的酒瓶冲他坏笑，冒出小犄角和尾巴"""
    bar_bg(img, d, T, lt)
    for sx_ in (120, 330):                                         # 高脚凳
        d.rectangle([sx_ - 16, 214, sx_ + 16, 220], fill=(150, 40, 60), outline=OUT); d.rectangle([sx_ - 2, 220, sx_ + 2, H], fill=(90, 90, 100))
    person(img, 'boy', 180, 240, view='side', pose='sit', expr='drunk', arms='lap', s=3)
    CT = 204
    d.rectangle([0, CT, W, CT + 10], fill=(120, 74, 50), outline=OUT); d.line([(0, CT + 2), (W, CT + 2)], fill=(156, 104, 70))
    d.rectangle([0, CT + 10, W, H], fill=(70, 40, 34))
    for x in range(10, W, 30): d.line([(x, CT + 12), (x, H)], fill=(58, 32, 28))
    d.line([(186, CT - 2), (214, CT - 2)], fill=OUT, width=6); d.line([(186, CT - 2), (214, CT - 2)], fill=AMB, width=4)   # 搭在台上的胳膊
    d.ellipse([210, CT - 6, 220, CT + 1], fill=SKIN, outline=OUT)
    gx = lerp(470, 236, eout(span(lt, 0.0, 0.55)))
    gy = CT
    d.rectangle([gx - 9, gy - 26, gx + 9, gy], fill=(255, 190, 60), outline=OUT)
    d.rectangle([gx - 8, gy - 30, gx + 8, gy - 24], fill=(255, 250, 236)); d.ellipse([gx - 9, gy - 35, gx + 9, gy - 25], fill=(255, 250, 236), outline=OUT)
    for k in range(3): d.point((gx - 4 + k * 4, gy - 18 + (int(T * 8) + k * 3) % 14), fill=(255, 240, 180))
    d.arc([gx + 6, gy - 22, gx + 16, gy - 8], 270, 90, fill=OUT, width=2)
    if lt < 0.55:
        for k in range(4): d.line([(gx + 14 + k * 8, gy - 20 + k * 4), (gx + 28 + k * 14, gy - 20 + k * 4)], fill=(140, 100, 90))
    horn = ease(span(lt, 0.8, 1.0))
    if 0.8 < lt < 1.05: glow(img, 320, CT - 30, 34, (255, 80, 100), 0.6 * (1 - span(lt, 0.8, 1.05)))
    bad_bottle(img, d, 320, CT, T, horn, 2)
    if horn > 0:
        c = bubble(img, d, 346, CT - 92, 30, 16, span(lt, 1.0, 1.2), tail=(1, 1))
        if c: text(img, '嘿嘿', c[0], c[1], (180, 40, 60), None, FONT_S, shadow=False)
    for k in range(3):
        f = (lt * 1.2 + k / 3) % 1
        x = 186 + 6 * math.sin(f * 6 + k); y = 140 - f * 26
        d.ellipse([x - 1 - f * 2, y - 1 - f * 2, x + 1 + f * 2, y + 1 + f * 2], outline=lerpc((255, 255, 255), (40, 18, 36), f))
    wobble(img, 2.0, T)
    vig(img, 0.5)


def big_hand(d, x, y, s=1.0, grab=0.0, sleeve=AMB, sleeve_s=AMB_D):
    """手背朝外、指尖朝上的大手：(x, y) 是手腕中心。grab 越大手指越弯"""
    d.rectangle([x - 20 * s, y, x + 20 * s, H + 20], fill=OUT); d.rectangle([x - 19 * s, y + 1, x + 19 * s, H + 20], fill=sleeve)
    d.rectangle([x - 19 * s, y + 1, x + 19 * s, y + 7 * s], fill=sleeve_s)
    oshape(d, [x - 15 * s, y - 32 * s, x + 15 * s, y + 2], SKIN, int(8 * s))
    tips = []
    for i in range(4):
        fx = x - 14 * s + i * 7.5 * s
        L = [20, 24, 22, 17][i] * s * (1 - 0.45 * grab)
        oshape(d, [fx, y - 30 * s - L, fx + 6 * s, y - 24 * s], SKIN, int(3 * s))
        d.rectangle([fx + 1 * s, y - 30 * s - L + 2 * s, fx + 4 * s, y - 30 * s - L + 5 * s], fill=(255, 236, 228))
        tips.append((fx + 3 * s, y - 30 * s - L))
    oshape(d, [x + 12 * s, y - 22 * s, x + 26 * s - grab * 6 * s, y - 12 * s], SKIN, int(4 * s))
    for k in range(3): d.ellipse([x - 10 * s + k * 8 * s, y - 28 * s, x - 7 * s + k * 8 * s, y - 26 * s], fill=SKIN_S)
    return tips


def chat_screen(lt, typing=0.0, cursor_on=True, draft=None):
    def scr(sc, sd, w, h):
        sd.rectangle([0, 0, w, h], fill=(22, 22, 34))
        chat_header(sd, w, head_icon('girl', 'smile', 1), sc)
        sd.text((w // 2 - 20, 18), '— 4月7日 —', font=FONT_S, fill=(110, 110, 130))
        y = 34
        for k, (mine, bw, bh) in enumerate(((False, 50, 12), (True, 40, 12), (False, 64, 17), (True, 56, 12), (True, 30, 12))):
            chat_bubble(sd, w - 5 if mine else 5, y, bw, bh, mine, k * 3)
            y += bh + 6
        kb = ease(clamp(typing))
        iy = h - 18 - int(kb * 64)
        sd.rectangle([0, iy - 2, w, h], fill=(36, 36, 52))
        sd.rounded_rectangle([5, iy + 2, w - 26, iy + 14], 5, fill=(240, 240, 248))
        if draft:
            sd.text((9, iy + 1), draft, font=FONT_S, fill=(40, 40, 60))
        if cursor_on:
            cx_ = 9 + (FONT_S.getlength(draft) if draft else 0)
            sd.rectangle([cx_, iy + 4, cx_ + 1, iy + 12], fill=(60, 120, 255))
        sd.ellipse([w - 22, iy + 1, w - 6, iy + 15], fill=AMB if draft else (90, 90, 110))
        sd.polygon([(w - 17, iy + 4), (w - 9, iy + 8), (w - 17, iy + 12), (w - 15, iy + 8)], fill=(255, 255, 255))
        if kb > 0:
            ky = iy + 18
            for r_ in range(3):
                for c_ in range(10 - (r_ == 2) * 2):
                    kx = 4 + c_ * ((w - 8) / 10) + (r_ == 2) * (w - 8) / 10
                    sd.rounded_rectangle([kx, ky + r_ * 15, kx + (w - 8) / 10 - 2, ky + r_ * 15 + 12], 2, fill=(70, 70, 92))
    return scr


def s_puppet(img, d, lt, dur, T, A):
    """酒瓶悬在半空，手里攥着木偶的十字架，提线拴着他的手指，一拽一拽地让他拿起了台上的手机"""
    bar_bg(img, d, T, lt)
    darken(img, 0.45)
    d.rectangle([0, 200, W, H], fill=(120, 74, 50)); d.line([(0, 202), (W, 202)], fill=(156, 104, 70))
    lift = ease(span(lt, 0.35, 1.7))
    jerk = 4 * math.sin(lt * 14) * (1 - lift) * (lt > 0.35)
    hx, hy = 220 + jerk, lerp(250, 196, lift)
    grab = span(lt, 0.25, 0.5)
    by = lerp(70, 40, lift)
    bxr = 250 + 10 * math.sin(lt * 7) * (1 - lift)
    tilt = math.radians(-14 * math.sin(lt * 7) * (1 - lift))
    ends = [(bxr - 40 * math.cos(tilt), by - 40 * math.sin(tilt)), (bxr + 40 * math.cos(tilt), by + 40 * math.sin(tilt))]
    holding = lt > 0.5
    pxp, pyp = (hx + 4, hy - 46) if holding else (236, 210)
    def scr(sc, sd, w, h):
        sd.rectangle([0, 0, w, h], fill=(30, 30, 46))
        sd.text((w // 2 - 15, 14), '23:59', font=FONT_S, fill=(230, 230, 240))
        sd.rounded_rectangle([4, 34, w - 4, 52], 4, fill=(60, 60, 84))
        sc.paste(head_icon('girl', 'smile', 1).resize((12, 13), Image.NEAREST), (7, 37), head_icon('girl', 'smile', 1).resize((12, 13), Image.NEAREST))
        sd.rectangle([22, 40, 44, 41], fill=(220, 220, 236))
    if holding:
        tips = big_hand(d, hx, hy, 1.0, 0.0)
        phone(img, d, pxp, pyp, 34, 60, scr, on=span(lt, 0.6, 0.9))
        for i, (fx, fy) in enumerate([(hx - 18, hy - 50), (hx + 26, hy - 50), (hx + 26, hy - 38), (hx + 26, hy - 26)]):
            oshape(d, [fx - 4, fy, fx + 4, fy + 8], SKIN, 3)
        tips = [(hx - 10, hy - 34), (hx - 3, hy - 36), (hx + 5, hy - 36), (hx + 12, hy - 33)]
    else:
        phone(img, d, 236, 214, 50, 24, None)
        tips = big_hand(d, hx, hy, 1.0, grab * 0.3)
    for i, (tx, ty) in enumerate(tips):
        ex, ey = ends[0] if i < 2 else ends[1]
        ex = lerp(ends[0][0], ends[1][0], i / 3); ey = lerp(ends[0][1], ends[1][1], i / 3)
        d.line([(ex, ey + 3), (tx, ty)], fill=(230, 226, 240))
    d.line([ends[0], ends[1]], fill=(150, 100, 60), width=4)
    d.line([(bxr - 6 * math.sin(tilt), by - 14), (bxr + 6 * math.sin(tilt), by + 14)], fill=(150, 100, 60), width=4)
    bad_bottle(img, d, bxr + 20, by - 6, T, 1.0, 1)
    d.line([(bxr + 14, by - 22), (bxr + 4, by - 6)], fill=(60, 150, 90), width=2)
    wobble(img, 1.5, T)
    vig(img, 0.5)


def s_chat(img, d, lt, dur, T, A):
    """手机特写：左手拇指点开和她的对话框，聊天记录停在很久以前，键盘弹了上来"""
    sky(img, ((0, (30, 14, 34)), (1, (60, 26, 50))))
    bokeh(img, T, 14, [AMB, PINK, (255, 120, 90), (160, 100, 255)], seed=21, a=0.3, rmin=14, rmax=30)
    typing = span(lt, 0.55, 0.9)
    tap = 0.3 < lt < 0.55
    cx, cy = 240, 128
    box = phone(img, d, cx, cy, 120, 214, chat_screen(lt, typing, int(T * 3) % 2 == 0))
    # 左手：拇指从左下伸到输入框，另外三根手指扣在右边
    for k in range(3):
        oshape(d, [cx + 56, cy + 10 + k * 20, cx + 70, cy + 24 + k * 20], SKIN, 5)
    d.rectangle([cx - 140, cy + 70, cx - 60, H], fill=OUT); d.rectangle([cx - 139, cy + 71, cx - 61, H], fill=AMB)
    oshape(d, [cx - 82, cy + 40, cx - 46, H + 10], SKIN, 12)
    ty_ = cy + 82 - (64 if typing > 0.5 else 0) * ease(typing) + (2 if tap else 0)
    tx_ = lerp(cx - 52, cx - 18, span(lt, 0.1, 0.4))
    d.line([(cx - 60, cy + 70), (tx_, ty_)], fill=OUT, width=15); d.line([(cx - 60, cy + 70), (tx_, ty_)], fill=SKIN, width=13)
    d.ellipse([tx_ - 7, ty_ - 7, tx_ + 7, ty_ + 7], fill=SKIN, outline=OUT)
    d.rectangle([tx_ - 3, ty_ - 5, tx_ + 2, ty_ - 2], fill=(255, 236, 228))
    if tap:
        r = (lt - 0.3) * 60
        d.ellipse([tx_ - r, ty_ - r, tx_ + r, ty_ + r], outline=(255, 255, 255))
    wobble(img, 1.2, T)


def s_stairs(img, d, lt, dur, T, A):
    """深夜的楼梯间，他一只手扶着栏杆一步一晃地往上爬，另一只手里的手机亮着"""
    img.paste((38, 36, 54), (0, 0, W, H))
    for y in range(0, H, 20): d.line([(0, y), (W, y)], fill=(34, 32, 48))
    d.rectangle([380, 30, 420, 46], fill=(40, 170, 90), outline=OUT)
    d.ellipse([388, 33, 392, 37], fill=(255, 255, 255)); d.line([(390, 37), (392, 42)], fill=(255, 255, 255)); d.line([(390, 39), (396, 38)], fill=(255, 255, 255))
    d.line([(392, 42), (388, 44)], fill=(255, 255, 255)); d.line([(392, 42), (396, 44)], fill=(255, 255, 255)); d.polygon([(408, 35), (414, 38), (408, 41)], fill=(255, 255, 255))
    glow(img, 400, 38, 30, (80, 255, 140), 0.25)
    text(img, '3F', 60, 60, (90, 86, 110), None, scale=3, shadow=False)
    d.rectangle([140, 50, 156, 58], fill=(255, 220, 140), outline=OUT); glow(img, 148, 56, 60, (255, 220, 150), 0.3)
    sx, sy = 20, 260
    steps = []
    for i in range(30):
        x0, y0 = sx + i * 16, sy - i * 9
        steps.append((x0, y0))
        d.rectangle([x0, y0, x0 + 16, H], fill=(70, 66, 90)); d.line([(x0, y0), (x0 + 16, y0)], fill=(110, 106, 130))
        d.line([(x0, y0), (x0, y0 + 9)], fill=(50, 48, 66))
    def stair_y(x): return sy - (x - sx) / 16 * 9
    u = lt / dur
    px = lerp(150, 250, u)
    sway = 5 * math.sin(lt * 5)
    py = stair_y(px) + 1 + abs(math.sin(lt * 7)) * -2
    person(img, 'boy', px + sway * 0.4, py, view='side', pose='walk', ph=wph(lt, 5), expr='drunk', arms='reach', s=3)
    glow(img, px - 4 + sway * 0.4, py - 60, 26, (150, 200, 255), 0.35)
    rail = [(x, stair_y(x) - 48) for x in (0, W)]
    d.line(rail, fill=OUT, width=5); d.line(rail, fill=(170, 170, 186), width=3)
    for x in range(30, W, 40): d.line([(x, stair_y(x) - 46), (x, stair_y(x))], fill=(120, 120, 140), width=2)
    c = bubble(img, d, px + 20, py - 96, 28, 16, span(lt, 0.4, 0.6), tail=(1, 1))
    if c: text(img, '嗝~', c[0], c[1], (60, 40, 60), None, FONT_S, shadow=False)
    wobble(img, 2.2, T)
    vig(img, 0.55)


DAY_SKY = ((0, (120, 180, 240)), (0.7, (200, 220, 240)), (1, (255, 226, 190)))


def court_fence(img, d, y0, y1, off=0):
    for x in range(-40, W + 40, 10):
        d.line([(x - off, y0), (x - off + 30, y1)], fill=(170, 176, 186)); d.line([(x - off + 30, y0), (x - off, y1)], fill=(170, 176, 186))
    d.line([(0, y0), (W, y0)], fill=(120, 126, 140), width=2)
    for x in range(-int(off) % 80, W, 80): d.rectangle([x, y0 - 4, x + 2, y1], fill=(120, 126, 140))


def s_lookalike(img, d, lt, dur, T, A):
    """白天的球场边，一个扎马尾、穿球衣的女孩从他身边走过；他回过头，她的身影和记忆里的你叠在了一起"""
    sky(img, DAY_SKY, 0, 200)
    cloud(d, 60 - lt * 6, 30, 1.6, (255, 255, 255), (230, 236, 250)); cloud(d, 330 - lt * 4, 50, 1.2, (255, 255, 255), (230, 236, 250))
    pix.tree_round(d, 420, 160, 1.6, (80, 160, 90), (120, 200, 110))
    pix.tree_round(d, 40, 160, 1.3, (80, 160, 90), (120, 200, 110))
    d.rectangle([0, 150, W, 200], fill=(84, 150, 150))
    d.rectangle([250, 120, 254, 175], fill=(100, 100, 110)); d.rectangle([236, 112, 268, 128], fill=(250, 250, 250), outline=OUT)
    d.rectangle([244, 128, 260, 130], fill=(240, 80, 60))
    court_fence(img, d, 100, 200)
    d.rectangle([0, 200, W, H], fill=(196, 186, 176))
    for x in range(0, W, 30): d.line([(x, 200), (x - 20, H)], fill=(180, 170, 160))
    gx = lerp(470, 120, span(lt, 0, dur))
    turned = gx < 205
    person(img, 'boy', 200, 236, view='side', pose='stand', expr='surprised' if turned else 'neutral', s=3, flip=turned)
    person(img, 'girl', gx, 238, age='other', view='side', pose='walk', ph=wph(lt, 7), expr='smile', s=3, flip=True)
    ghost = math.sin(math.pi * span(lt, 0.5, 1.5))
    if ghost > 0.05:
        im = pix.char_img('girl', 'young', 'side', 'walk', wph(lt, 7), 'smile').transpose(Image.FLIP_LEFT_RIGHT)
        im = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
        a = np.array(im); a[..., 3] = (a[..., 3] * 0.55 * ghost).astype(np.uint8); a[a[..., 3] > 0, :3] = (a[a[..., 3] > 0, :3] * 0.6 + np.array(TEAL_L) * 0.4).astype(np.uint8)
        im = Image.fromarray(a)
        img.paste(im, (int(gx + 4 - (pix.CW - 1 - pix.CX) * 3), int(238 - 4 - pix.FY * 3)), im)
        for j in range(4): twinkle(d, int(gx - 20 + j * 14), int(150 + (j % 2) * 20), (lt * 2 + j / 4) % 1, (255, 255, 255), 3)
    if turned:
        text(img, '!', 200, 110 - 6 * eout(span(lt, 1.0, 1.2)), (255, 255, 255), OUT, scale=2)
    grade(img, 1.0, (1.04, 1.0, 0.92), (6, 2, 0))


def grade(img, sat, mul, add):
    pix.grade(img, sat, mul, add)


def s_jersey(img, d, lt, dur, T, A):
    """球场上她在运球，球衣的号码和你那件一模一样，球在拍点上弹起来"""
    sky(img, ((0, (255, 170, 120)), (0.7, (255, 210, 160)), (1, (255, 232, 190))), 0, 170)
    d.ellipse([360, 60, 410, 110], fill=(255, 246, 210)); glow(img, 385, 85, 60, (255, 240, 200), 0.4)
    d.rectangle([0, 130, W, 170], fill=(210, 120, 120))
    for x in range(0, W, 26): d.rectangle([x, 120 + (x * 7) % 14, x + 20, 170], fill=(196, 110, 116))
    court_fence(img, d, 70, 170, lt * 4)
    d.rectangle([0, 170, W, H], fill=(84, 150, 150)); d.line([(0, 200), (W, 196)], fill=(240, 240, 240)); d.arc([120, 180, 360, 300], 180, 360, fill=(240, 240, 240))
    gx = 230
    person(img, 'girl', gx, 252, age='other', view='front', expr='smile', s=5, arms='down')
    d.rectangle([gx - 14, 172, gx + 12, 200], fill=(232, 76, 84))
    text(img, '17', gx - 1, 186, (255, 255, 255), (150, 30, 50), FONT, scale=1)
    ph_, n = beat_phase(T)
    by = 246 - 70 * (1 - (2 * ph_ - 1) ** 2)
    bx = gx + 46
    d.ellipse([bx - 12, by - 12, bx + 12, by + 12], fill=(240, 130, 50), outline=(90, 40, 20))
    d.line([(bx - 12, by), (bx + 12, by)], fill=(90, 40, 20)); d.arc([bx - 8, by - 12, bx + 8, by + 12], 270, 90, fill=(90, 40, 20))
    if ph_ < 0.12: d.ellipse([bx - 18, 250, bx + 18, 256], outline=(240, 240, 240))
    d.line([(gx + 30, 252 - 26 * 5 + 50), (bx - 6, by - 8)], fill=OUT, width=6) if False else None
    # 右上角：记忆里那件青绿色的 17 号球衣
    f = ease(span(lt, 0.4, 0.8))
    if f > 0:
        jx, jy = 420, 60 + (1 - f) * -40
        d.polygon([(jx - 22, jy - 18), (jx - 12, jy - 22), (jx + 12, jy - 22), (jx + 22, jy - 18), (jx + 18, jy - 8), (jx + 16, jy + 26), (jx - 16, jy + 26), (jx - 18, jy - 8)],
                  fill=TEAL, outline=OUT)
        text(img, '17', jx, jy + 4, (255, 255, 255), None, FONT_S, shadow=False)
        text(img, '=', jx - 50, jy + 2, (255, 255, 255), OUT, scale=2)
        for j in range(3): twinkle(d, int(jx - 30 + j * 30), int(jy - 30 + (j % 2) * 56), (lt * 2.5 + j / 3) % 1, (255, 255, 255), 3)


def s_send(img, d, lt, dur, T, A):
    """输入框里打好了一句话，拇指在发送键上面停住，按下去又缩回来"""
    sky(img, ((0, (16, 12, 34)), (1, (40, 22, 60))))
    bokeh(img, T, 10, [AMB, (150, 200, 255)], seed=31, a=0.2)
    cx, cy = 240, 128
    phone(img, d, cx, cy, 120, 214, chat_screen(lt, 1.0, int(T * 3) % 2 == 0, '在吗？'))
    bx, by = cx + 47, cy + 27
    pulse_ = 0.5 + 0.5 * math.sin(lt * 10)
    glow(img, bx, by, 16, AMB, 0.4 * pulse_)
    hov = 10 + 8 * math.sin(lt * 4.5)
    tx_, ty_ = bx + 4, by + hov
    d.line([(cx + 110, H + 10), (tx_ + 4, ty_ + 6)], fill=OUT, width=17); d.line([(cx + 110, H + 10), (tx_ + 4, ty_ + 6)], fill=SKIN, width=15)
    d.ellipse([tx_ - 7, ty_ - 6, tx_ + 9, ty_ + 8], fill=SKIN, outline=OUT)
    d.rectangle([tx_ - 2, ty_ - 3, tx_ + 3, ty_], fill=(255, 236, 228))
    for k in range(2): put(img, 'drop', cx + 80 + k * 10, 60 + k * 8 + (lt * 14) % 6, 2)
    c = bubble(img, d, cx - 80, 70, 26, 22, span(lt, 0.2, 0.4), thought=True, tail=(1, 1))
    if c: text(img, '?', c[0], c[1], (40, 30, 48), None, shadow=False)


def s_toss(img, d, lt, dur, T, A):
    """从上往下看：他在床上翻来覆去；头顶一枚硬币翻个不停，一面是“发”的勾，一面是“不发”的叉"""
    img.paste((40, 34, 60), (0, 0, W, H))
    for x in range(0, W, 24): d.line([(x, 0), (x, H)], fill=(46, 40, 68))
    bx0, by0, bx1, by1 = 120, 40, 360, 260
    d.rectangle([bx0 - 6, by0 - 10, bx1 + 6, by1 + 4], fill=(90, 62, 50), outline=OUT)
    d.rectangle([bx0, by0, bx1, by1], fill=(232, 228, 242), outline=OUT)
    roll = math.sin(lt * 4.2)
    hx = 240 + roll * 26
    d.rounded_rectangle([200, 48, 280, 80], 8, fill=(250, 248, 255), outline=OUT)
    d.ellipse([hx - 13, 54, hx + 13, 80], fill=(36, 34, 50), outline=OUT)
    d.ellipse([hx - 8, 56, hx + 4, 64], fill=(74, 76, 106))
    blanket = [(bx0 + 4, 84), (bx1 - 4, 84), (bx1 - 4, by1 - 4), (bx0 + 4, by1 - 4)]
    d.polygon(blanket, fill=AMB, outline=OUT)
    for k in range(6):
        y = 96 + k * 26
        d.line([(bx0 + 10, y + roll * 4), (bx1 - 10, y - roll * 4)], fill=AMB_D, width=2)
    lump = 240 + roll * 30
    d.ellipse([lump - 34, 100, lump + 34, 200], fill=(255, 190, 80), outline=AMB_D)
    phx, phy = 312, 66
    d.rounded_rectangle([phx - 8, phy - 13, phx + 8, phy + 13], 3, fill=(30, 30, 44), outline=OUT)
    d.rectangle([phx - 6, phy - 10, phx + 6, phy + 10], fill=(150, 200, 255)); glow(img, phx, phy, 34, (150, 200, 255), 0.3)
    for k in range(5):                                           # 百叶窗的月光
        x0 = 40 + k * 30
        tfill(img, 'polygon', [(x0, 0), (x0 + 14, 0), (x0 + 180, H), (x0 + 166, H)], (170, 190, 255), 0.07)
    # 翻转的硬币
    cxx, cyy, r = 410, 86, 34
    th = lt * 9
    sx = abs(math.cos(th))
    face = math.cos(th) > 0
    w = max(2, r * sx)
    d.ellipse([cxx - w, cyy - r, cxx + w, cyy + r], fill=(220, 170, 50), outline=OUT)
    d.ellipse([cxx - w * 0.8, cyy - r * 0.8, cxx + w * 0.8, cyy + r * 0.8], fill=(255, 210, 80))
    if sx > 0.35:
        if face:
            d.line([(cxx - 14 * sx, cyy), (cxx - 4 * sx, cyy + 11), (cxx + 15 * sx, cyy - 12)], fill=(40, 170, 80), width=5)
        else:
            d.line([(cxx - 12 * sx, cyy - 12), (cxx + 12 * sx, cyy + 12)], fill=RED, width=5); d.line([(cxx + 12 * sx, cyy - 12), (cxx - 12 * sx, cyy + 12)], fill=RED, width=5)
    for k in range(3):
        a = th * 0.5 + k * 2.1
        twinkle(d, int(cxx + math.cos(a) * 46), int(cyy + math.sin(a) * 40), (lt * 2 + k / 3) % 1, (255, 240, 180), 3)
    vig(img, 0.5)


def map_base():
    im = Image.new('RGB', (W, H), (24, 28, 44)); d = ImageDraw.Draw(im)
    r = rng(77)
    for _ in range(60):
        x, y = r.randrange(-20, W), r.randrange(-20, H)
        d.rectangle([x, y, x + r.randint(20, 60), y + r.randint(14, 40)], fill=(32, 38, 58))
    d.polygon([(0, 180), (120, 150), (220, 190), (340, 160), (480, 200), (480, 230), (340, 190), (220, 220), (120, 180), (0, 210)], fill=(40, 70, 120))
    for x in range(0, W, 48): d.line([(x, 0), (x + 20, H)], fill=(70, 76, 100), width=3)
    for y in range(0, H, 44): d.line([(0, y), (W, y - 10)], fill=(70, 76, 100), width=3)
    d.line([(0, 60), (W, 130)], fill=(160, 140, 90), width=5)
    for (x, y) in ((60, 80), (380, 50), (300, 240)): d.ellipse([x - 26, y - 16, x + 26, y + 16], fill=(40, 90, 70))
    return im


MAP = None


def s_map(img, d, lt, dur, T, A):
    """手机地图上，他的位置在闪；雷达一圈圈扫出去，红色的定位针落下又消失，坐标的数字乱跳，找不到她在哪"""
    global MAP
    MAP = MAP or map_base()
    img.paste(MAP)
    me = (150, 120)
    for k in range(3):
        rr = ((lt * 50 + k * 40) % 120)
        d.ellipse([me[0] - rr, me[1] - rr, me[0] + rr, me[1] + rr], outline=lerpc((90, 160, 255), (24, 28, 44), rr / 120))
    a0 = lt * 3
    tfill(img, 'pieslice', [me[0] - 260, me[1] - 260, me[0] + 260, me[1] + 260], (90, 200, 255), 0.12) if False else None
    for k in range(18):
        a = a0 - k * 0.03
        d.line([me, (me[0] + math.cos(a) * 300, me[1] + math.sin(a) * 300)], fill=lerpc((90, 200, 255), (24, 28, 44), k / 18 * 0.8 + 0.2))
    glow(img, me[0], me[1], 14, (90, 160, 255), 0.6)
    d.ellipse([me[0] - 5, me[1] - 5, me[0] + 5, me[1] + 5], fill=(80, 150, 255), outline=(255, 255, 255))
    for k in range(int(lt / 0.6) + 1):
        tk = lt - k * 0.6
        if not 0 <= tk < 0.6: continue
        r = rng(k * 13)
        px, py = r.uniform(240, 450), r.uniform(50, 220)
        drop = eout(min(1, tk / 0.2))
        a = 1 - span(tk, 0.35, 0.6)
        yy = py - 30 * (1 - drop)
        tfill(img, 'ellipse', [px - 8, yy - 22, px + 8, yy - 6], RED, a)
        tfill(img, 'polygon', [(px - 6, yy - 10), (px + 6, yy - 10), (px, yy)], RED, a)
        if a > 0.5: text(img, '?', px, yy - 15, (255, 255, 255), None, FONT_S, shadow=False)
    d.rectangle([0, 0, W, 26], fill=(16, 18, 30))
    dig = ''.join('0123456789'[(int(T * 25) + i * 7) % 10] for i in range(8))
    text(img, f'N {dig[:2]}.{dig[2:5]}°  E 1{dig[5:7]}.{dig[7]}??°', 168, 13, (190, 220, 255), None, FONT_S, shadow=False)
    text(img, '她的位置：' + '？' * (1 + int(lt * 3) % 3), 400, 13, AMB_L, None, FONT_S, shadow=False)
    d.rectangle([0, 26, W, 27], fill=(60, 70, 100))


def s_delete(img, d, lt, dur, T, A):
    """联系人卡片：按下“删除”，卡片缩小着飞进垃圾桶，桶盖一合，碎成像素"""
    sky(img, ((0, (20, 18, 36)), (1, (36, 26, 56))))
    pressed = 0.35 < lt < 0.5
    k = span(lt, 0.5, 1.05)
    cx = lerp(240, 410, ease(k)); cy = lerp(110, 200, ease(k)) - 60 * math.sin(math.pi * k)
    sc = 1 - 0.85 * ease(k)
    tx, ty = 410, 214
    lid = 1 if 0.45 < lt < 1.15 else 0
    d.rectangle([tx - 18, ty - 20, tx + 18, ty + 18], fill=(110, 116, 140), outline=OUT)
    for x in range(tx - 12, tx + 13, 6): d.line([(x, ty - 16), (x, ty + 14)], fill=(80, 86, 110))
    if lid:
        d.polygon([(tx - 20, ty - 22), (tx - 14, ty - 44), (tx - 10, ty - 42), (tx - 16, ty - 22)], fill=(130, 136, 160), outline=OUT)
    else:
        d.rectangle([tx - 21, ty - 26, tx + 21, ty - 20], fill=(130, 136, 160), outline=OUT); d.rectangle([tx - 5, ty - 30, tx + 5, ty - 26], fill=(130, 136, 160), outline=OUT)
    if lt < 1.05:
        w, h = 210 * sc, 150 * sc
        card = Image.new('RGBA', (210, 150)); cd = ImageDraw.Draw(card); cd.fontmode = '1'
        cd.rounded_rectangle([0, 0, 209, 149], 10, fill=(244, 244, 250), outline=OUT)
        cd.ellipse([80, 12, 128, 60], fill=TEAL_L, outline=OUT)
        hi = head_img('girl', 'young', 'smile', 2)
        card.paste(hi, (88, 14), hi)
        cd.rectangle([70, 68, 140, 72], fill=(60, 60, 80))
        cd.text((48, 80), '●●●  ●●●●  ●●●●', font=FONT_S, fill=(100, 100, 120))
        cd.rounded_rectangle([60, 112, 150, 136], 6, fill=(200, 40, 50) if pressed else RED, outline=OUT)
        cd.text((83, 115 + (1 if pressed else 0)), '删除联系人', font=FONT_S, fill=(255, 255, 255))
        card = card.resize((max(1, int(w)), max(1, int(h))), Image.NEAREST)
        if k > 0: card = card.rotate(-200 * k, resample=Image.NEAREST, expand=True)
        paste(img, card, cx, cy, 1, 'cc')
        if lt < 0.5:
            cursor(d, lerp(330, 254, ease(span(lt, 0, 0.35))), lerp(240, 236 - 110 + 120 - 2, ease(span(lt, 0, 0.35))) - 0)
    if lt > 1.15:
        kk = lt - 1.15
        for j in range(26):
            r = rng(j)
            a = r.uniform(-math.pi, 0); sp = r.uniform(30, 90)
            x = tx + math.cos(a) * sp * kk; y = ty - 24 + math.sin(a) * sp * kk + 80 * kk * kk
            if kk < 0.6: d.rectangle([x, y, x + 2, y + 2], fill=[TEAL, (244, 244, 250), RED][j % 3])
        props.shake(img, kk, 3, 0.2)


def s_digits(img, d, lt, dur, T, A):
    """他挠着头站在中间，身边一圈号码牌，数字乱跳，越来越多变成问号"""
    sky(img, ((0, (22, 16, 44)), (1, (52, 28, 76))))
    bokeh(img, T, 8, seed=41, a=0.2)
    person(img, 'boy', 240, 214, view='front', pose='stand', expr='worried', arms='cover' if int(lt * 3) % 2 else 'down', s=3)
    for k in range(3): put(img, 'drop', 274 + k * 3, 112 + ((lt * 18 + k * 6) % 14), 2)
    slots = '1' + 'X' * 10
    n = len(slots)
    for i in range(n):
        a = -math.pi / 2 + (i - (n - 1) / 2) * 0.36 + lt * 0.25
        rx, ry = 150, 96
        x = 240 + math.sin(a + math.pi / 2) * rx * (1 if i % 2 else 1)
        x = 240 + math.cos(a) * rx; y = 132 + math.sin(a) * ry + 6 * math.sin(T * 3 + i)
        d.rounded_rectangle([x - 11, y - 13, x + 11, y + 13], 4, fill=(24, 20, 40), outline=AMB if i == 0 else (90, 80, 130))
        q = lt > 0.6 + i * 0.12
        ch = '1' if i == 0 else ('?' if q and i > 0 else '0123456789'[(int(T * 20) + i * 3) % 10])
        text(img, ch, x, y, AMB_L if i == 0 else ((255, 255, 255) if not q else PINK), None, scale=1, shadow=False)
    c = bubble(img, d, 268, 98, 24, 20, span(lt, 0.8, 1.0), thought=True, tail=(1, 1))
    if c: text(img, '?', c[0], c[1], (40, 30, 48), None, shadow=False)


def cal_page(d, x, y, w, h, num):
    d.rectangle([x, y, x + w, y + h], fill=(250, 248, 240), outline=OUT)
    d.rectangle([x, y, x + w, y + 22], fill=(220, 60, 60), outline=OUT)
    for k in range(5): d.ellipse([x + 14 + k * (w - 28) / 4 - 3, y - 4, x + 14 + k * (w - 28) / 4 + 3, y + 4], fill=(200, 200, 210), outline=OUT)
    for k in range(7): d.rectangle([x + 10 + k * (w - 20) / 7, y + h - 18, x + 14 + k * (w - 20) / 7, y + h - 14], fill=(180, 176, 190))


def s_calendar(img, d, lt, dur, T, A):
    """墙上的日历一页一页被撕下来，越撕越快，满屏都是飞走的日子"""
    img.paste((44, 38, 66), (0, 0, W, H))
    for x in range(0, W, 20): d.line([(x, 0), (x, H)], fill=(48, 42, 72))
    tfill(img, 'polygon', [(300, 0), (420, 0), (300, H), (180, H)], (255, 230, 180), 0.06)
    x, y, w, h = 180, 40, 120, 150
    tears = []
    t = 0.0; gap = 0.42
    while t < dur:
        tears.append(t); gap = max(0.05, gap * 0.78); t += gap
    nt = sum(1 for tt in tears if tt <= lt)
    num = 7 + nt
    cal_page(d, x, y, w, h, num)
    text(img, str(num), x + w / 2, y + 82, (50, 40, 60), None, scale=4, shadow=False)
    for j, tt in enumerate(tears):
        k = lt - tt
        if k < 0 or k > 1.6: continue
        r = rng(j)
        px = x + w / 2 + k * r.uniform(260, 420) * (1 if j % 3 else -0.7)
        py = y + h / 2 - 90 * k + 260 * k * k * r.uniform(0.3, 1)
        sc = max(0.2, 0.8 - 0.6 * k)
        pg = Image.new('RGBA', (w + 2, h + 2)); pd = ImageDraw.Draw(pg); pd.fontmode = '1'
        cal_page(pd, 0, 0, w, h, 7 + j)
        tw = FONT.getlength(str(7 + j))
        pd.text((w / 2 - tw / 2, 64), str(7 + j), font=FONT, fill=(40, 34, 50))
        pg = pg.resize((max(1, int((w + 2) * sc * abs(math.cos(k * r.uniform(3, 7))) + 2)), max(1, int((h + 2) * sc))), Image.NEAREST)
        pg = pg.rotate(k * r.uniform(-200, 200), resample=Image.NEAREST, expand=True)
        paste(img, pg, px, py, 1, 'cc')
    d.rectangle([x + w / 2 - 2, y - 12, x + w / 2 + 2, y - 4], fill=(120, 120, 130))


def spiral_bg(img, T, cx=240, cy=135, speed=2.4, cols=((24, 10, 44), (110, 40, 140), AMB_D, (60, 20, 90))):
    yy, xx = np.mgrid[0:H, 0:W]
    dx, dy = xx - cx, (yy - cy) * 1.2
    r = np.sqrt(dx * dx + dy * dy) + 1
    a = np.arctan2(dy, dx)
    v = (a / (2 * math.pi) * 3 + np.log(r) * 1.6 - T * speed) % 1
    k = np.clip((v * len(cols) + pix.BAYER * 0.6).astype(int), 0, len(cols) - 1) % len(cols)
    pal = np.array(cols, np.uint8)
    out = pal[k]
    fade = np.clip(1 - r / 40, 0, 1)[..., None]
    out = (out * (1 - fade) + np.array((6, 2, 14)) * fade).astype(np.uint8)
    img.paste(Image.fromarray(out))


def s_vortex(img, d, lt, dur, T, A):
    """一个旋转的漩涡，他、手机和日历页一起打着转往中间掉"""
    spiral_bg(img, T)
    items = [('boy', 0.0, 3), ('phone', 0.25, 0), ('page', 0.45, 0), ('heart', 0.15, 0), ('page', 0.6, 0)]
    for kind, off, s in items:
        u = clamp(lt / dur * 1.1 - off * 0.3)
        ang = off * 9 + lt * 4.5
        rad = (1 - ease(u)) * (150 if kind == 'boy' else 200)
        x = 240 + math.cos(ang) * rad; y = 135 + math.sin(ang) * rad * 0.8
        sc = 1 - 0.85 * u
        if kind == 'boy':
            im = pix.char_img('boy', 'young', 'front', 'jump', 0, 'surprised', 'up')
            im = im.resize((max(1, int(im.width * 3 * sc)), max(1, int(im.height * 3 * sc))), Image.NEAREST).rotate(math.degrees(lt * 5), resample=Image.NEAREST, expand=True)
            paste(img, im, x, y, 1, 'cc')
        elif kind == 'phone':
            im = Image.new('RGBA', (16, 28)); pd = ImageDraw.Draw(im); pd.rounded_rectangle([0, 0, 15, 27], 3, fill=(30, 30, 44), outline=OUT); pd.rectangle([2, 3, 13, 23], fill=(150, 200, 255))
            im = im.resize((max(1, int(32 * sc)), max(1, int(56 * sc))), Image.NEAREST).rotate(lt * 400, resample=Image.NEAREST, expand=True)
            paste(img, im, x, y, 1, 'cc')
        elif kind == 'page':
            im = Image.new('RGBA', (20, 24)); pd = ImageDraw.Draw(im); pd.rectangle([0, 0, 19, 23], fill=(250, 248, 240), outline=OUT); pd.rectangle([0, 0, 19, 5], fill=(220, 60, 60))
            im = im.resize((max(1, int(40 * sc)), max(1, int(48 * sc))), Image.NEAREST).rotate(-lt * 300 + off * 100, resample=Image.NEAREST, expand=True)
            paste(img, im, x, y, 1, 'cc')
        else:
            put(img, 'bigheart', x, y, max(1, int(3 * sc)))


def heart_grid_pos(i, cols=36, rows=18):
    r = rng(i)
    return 14 + (i % cols) * 13 + r.randint(-1, 1), 16 + (i // cols) * 12 + r.randint(-1, 1)


ORDER = sorted(range(36 * 18), key=lambda i: rng(i * 3 + 1).random())


def s_hearts(img, d, lt, dur, T, A):
    """满屏的小心一颗一颗冒出来，计数跳到一千"""
    sky(img, ((0, (40, 10, 40)), (1, (90, 24, 70))))
    n = int(len(ORDER) * span(lt, 0.0, dur * 0.85) ** 1.4)
    for j in range(n):
        i = ORDER[j]
        x, y = heart_grid_pos(i)
        col = [PINK, (255, 140, 180), AMB, (255, 90, 110)][i % 4]
        pop = (n - j) < 12
        put(img, 'heart', x, y, 2 if pop else 1, tint=col)
    cnt = int(1000 * span(lt, 0.0, dur * 0.85) ** 1.4)
    d.rounded_rectangle([170, 110, 310, 160], 10, fill=(30, 10, 30), outline=PINK)
    put(img, 'bigheart', 196, 135, 2)
    text(img, '×' + str(cnt), 262, 135, (255, 255, 255), OUT, scale=2)


def s_plus1(img, d, lt, dur, T, A):
    """所有的小心被吸到中间，合成一颗大心，右上角跳出一个“+1”"""
    sky(img, ((0, (40, 10, 40)), (1, (90, 24, 70))))
    k = span(lt, 0.0, 0.5)
    for j in range(0, len(ORDER), 3):
        i = ORDER[j]
        x, y = heart_grid_pos(i)
        e = ein(clamp(k * 1.2 - (j % 7) * 0.03))
        if e >= 1: continue
        put(img, 'heart', lerp(x, 240, e), lerp(y, 128, e), 1, tint=[PINK, (255, 140, 180), AMB, (255, 90, 110)][i % 4])
    if lt > 0.4:
        u = lt - 0.4
        s = 6 + (1 if pix.pulse(T, 0.2) > 0.5 else 0)
        glow(img, 240, 128, 80, PINK, 0.4)
        put(img, 'bigheart', 240, 128, s)
        if u < 0.15: darken(img, 0.5 * (1 - u / 0.15), (255, 240, 250))
        b = span(lt, 0.7, 0.95)
        if b > 0:
            r = 22 * eback(b)
            d.ellipse([300 - r, 80 - r, 300 + r, 80 + r], fill=AMB, outline=OUT)
            if b > 0.6: text(img, '+1', 300, 80, (255, 255, 255), OUT, scale=2)
            burst(img, d, lt - 0.7, 300, 80, life=1.0, scale=0.8)


def wheel(d, cx, cy, r, ang, col=(40, 38, 52), hi=(70, 68, 86)):
    for w_, c in ((14, OUT), (12, col)):
        d.ellipse([cx - r - w_ / 2, cy - r - w_ / 2, cx + r + w_ / 2, cy + r + w_ / 2], outline=c, width=w_)
    d.arc([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], 200, 250, fill=hi, width=2)
    for k in (90, 210, 330):
        a = math.radians(k + ang)
        d.line([(cx, cy), (cx + math.cos(a) * r, cy + math.sin(a) * r)], fill=OUT, width=10)
        d.line([(cx, cy), (cx + math.cos(a) * r, cy + math.sin(a) * r)], fill=col, width=8)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=col, outline=OUT)
    a = math.radians(ang - 90)
    d.ellipse([cx + math.cos(a) * 6 - 4, cy + math.sin(a) * 6 - 4, cx + math.cos(a) * 6 + 4, cy + math.sin(a) * 6 + 4], fill=AMB)


def steer(img, d, ang, cx=240, cy=300, r=104):
    """方向盘和握着它的两只手（10 点和 2 点的位置，跟着方向盘转）"""
    wheel(d, cx, cy, r, ang)
    for k, base in enumerate((228, 312)):
        a = math.radians(base + ang)
        hx, hy = cx + math.cos(a) * r, cy + math.sin(a) * r
        ex = cx + (-150 if k == 0 else 150)
        d.line([(hx, hy), (ex, H + 40)], fill=OUT, width=26); d.line([(hx, hy), (ex, H + 40)], fill=AMB, width=22)
        d.ellipse([hx - 13, hy - 13, hx + 13, hy + 13], fill=SKIN, outline=OUT)
        d.line([(hx - 6, hy - 4), (hx + 6, hy - 4)], fill=SKIN_S)


def s_dashboard(img, d, lt, dur, T, A):
    """驾驶座的视角：仪表盘上左转的箭头一直在闪，方向盘却往右打，挡风玻璃外的路往右拐了过去"""
    turn = ease(span(lt, 1.3, 2.4))
    vx = 240 - 170 * turn
    sky(img, ((0, (10, 8, 30)), (1, (60, 34, 92))), 0, 112)
    pix.stars(d, T, 100, 0.7, 80, ox=turn * 200)
    city(img, d, 112, 5, turn * 420 + lt * 6, (34, 26, 66), (255, 206, 120), 20, 60, 0.35, T, 10, 22)
    d.rectangle([0, 112, W, H], fill=(24, 22, 36))
    hz = 112
    for side in (-1, 1):
        pts = []
        for k in range(30):
            z = k / 29
            y = hz + (200 - hz) * z ** 1.6
            bend = 160 * turn * (1 - z) ** 2
            x = vx + side * (12 + 260 * z ** 1.6) + bend * 0.0
            pts.append((x, y))
        d.line(pts, fill=(200, 196, 190), width=2)
    for k in range(8):
        z0 = ((k + lt * 3) % 8) / 8
        z1 = z0 + 0.05
        y0 = hz + (200 - hz) * z0 ** 1.6; y1 = hz + (200 - hz) * z1 ** 1.6
        d.line([(vx, y0), (vx + (240 - vx) * z0 ** 1.6 * 0.4, y1)], fill=(240, 200, 80), width=max(1, int(z1 * 4)))
    for k in range(6):
        z = ((k * 0.17 + lt * 0.5) % 1)
        y = hz + (200 - hz) * z ** 1.6
        for side in (-1, 1):
            x = vx + side * (30 + 300 * z ** 1.6)
            d.line([(x, y), (x, y - 50 * z ** 1.6 - 4)], fill=(80, 76, 100), width=max(1, int(z * 4)))
            glow(img, x, y - 50 * z ** 1.6 - 4, 10 + 20 * z, (255, 220, 160), 0.35)
    drops_on_glass(img, d, T, (0, 0, W, 190), 60, 9)
    ph_ = beat_phase(T)[0]
    wa = math.radians(-160 + 140 * math.sin(math.pi * ph_))
    for bx0 in (130, 330):
        d.line([(bx0, 196), (bx0 + math.cos(wa) * 150, 196 + math.sin(wa) * 150)], fill=OUT, width=4)
        d.line([(bx0, 196), (bx0 + math.cos(wa) * 150, 196 + math.sin(wa) * 150)], fill=(60, 60, 70), width=2)
    d.polygon([(0, 0), (40, 0), (90, 200), (0, 200)], fill=(18, 16, 26)); d.polygon([(W, 0), (W - 40, 0), (W - 90, 200), (W, 200)], fill=(18, 16, 26))
    d.rectangle([0, 0, W, 10], fill=(18, 16, 26))
    d.polygon([(0, 174), (W, 174), (W, H), (0, H)], fill=(30, 28, 40)); d.line([(0, 174), (W, 174)], fill=(56, 54, 70), width=2)
    cx0, cy0 = 240, 194
    d.rounded_rectangle([cx0 - 96, cy0 - 20, cx0 + 96, cy0 + 20], 10, fill=(12, 12, 20), outline=(70, 68, 90))
    for gx in (cx0 - 50, cx0 + 50):
        d.ellipse([gx - 17, cy0 - 17, gx + 17, cy0 + 17], outline=(110, 200, 255))
        a = math.radians(200 + 60 * (0.5 + 0.3 * math.sin(T * 2 + gx)))
        d.line([(gx, cy0), (gx + math.cos(a) * 14, cy0 + math.sin(a) * 14)], fill=(255, 90, 80), width=2)
    sig = blink_a(T)
    props.arrow(img, cx0 - 14, cy0 - 8, 1, sig, glow_r=14)
    props.arrow(img, cx0 + 14, cy0 - 8, 1, 0.0, left=False, glow_r=0)
    text(img, '60', cx0, cy0 + 8, (150, 220, 255), None, FONT_S, shadow=False)
    steer(img, d, 95 * turn - 5 * math.sin(lt * 2) * (1 - turn))
    if sig > 0.5: text(img, '嗒', cx0 - 14, cy0 - 34, AMB_L, (60, 24, 10), FONT_S)
    if turn > 0.1:
        props.arrow(img, 420, 60, 3, 0.0, left=False, off=(220, 220, 230), glow_r=0)


def cupid(img, d, x, y, t, s=2, draw=0.0):
    """原创的小丘比特：圆脸、金色卷毛、白翅膀、粉色腰带，手里一张小弓"""
    flap = math.sin(t * 14)
    for side in (-1, 1):
        wx = x - 4 * s * side if False else x - 6 * s
        pts = [(x - 2 * s, y - 2 * s), (x - 14 * s, y - (10 + 6 * flap) * s), (x - 18 * s, y - (4 + 4 * flap) * s), (x - 12 * s, y + 2 * s)]
        if side > 0: pts = [(x + 2 * s, y - 2 * s), (x - 8 * s, y - (12 + 6 * flap) * s), (x - 14 * s, y - (8 + 5 * flap) * s), (x - 8 * s, y + 1 * s)]
        d.polygon(pts, fill=(255, 255, 255) if side > 0 else (230, 232, 250), outline=OUT)
    oshape(d, [x - 6 * s, y - 2 * s, x + 6 * s, y + 9 * s], SKIN, 4 * s)
    d.rectangle([x - 6 * s, y + 5 * s, x + 6 * s, y + 8 * s], fill=(255, 150, 190))
    for lx in (-3, 2): oshape(d, [x + lx * s, y + 8 * s, x + (lx + 3) * s, y + 13 * s], SKIN, s)
    oshape(d, [x - 7 * s, y - 15 * s, x + 7 * s, y - 2 * s], SKIN, 6 * s)
    for k in range(6): d.ellipse([x - 8 * s + k * 3 * s, y - 18 * s + (k % 2) * s, x - 4 * s + k * 3 * s, y - 13 * s + (k % 2) * s], fill=(255, 214, 90), outline=(200, 150, 50))
    d.rectangle([x + 1 * s, y - 9 * s, x + 2 * s, y - 8 * s], fill=EYE_C); d.rectangle([x + 4 * s, y - 9 * s, x + 5 * s, y - 8 * s], fill=EYE_C)
    d.rectangle([x, y - 6 * s, x + s, y - 6 * s + 1], fill=pix.BLUSH); d.rectangle([x + 5 * s, y - 6 * s, x + 6 * s, y - 6 * s + 1], fill=pix.BLUSH)
    bx = x + 12 * s
    d.arc([bx - 6 * s, y - 10 * s, bx + 6 * s, y + 10 * s], 280, 80, fill=(150, 90, 50), width=max(1, s))
    pull = 6 * s * draw
    d.line([(bx + 1 * s, y - 9 * s), (bx - pull, y), (bx + 1 * s, y + 9 * s)], fill=(240, 240, 240))
    oshape(d, [x + 4 * s, y - 1 * s, x + 9 * s, y + 3 * s], SKIN, s)
    return bx - pull, y


EYE_C = (46, 34, 48)


def heart_arrow(d, x0, y0, x1, y1):
    d.line([(x0, y0), (x1, y1)], fill=(150, 100, 60), width=2)
    ang = math.atan2(y1 - y0, x1 - x0)
    for k in (-1, 1):
        d.line([(x0, y0), (x0 - math.cos(ang + k * 0.6) * 8, y0 - math.sin(ang + k * 0.6) * 8)], fill=(255, 255, 255), width=2)


def s_cupid(img, d, lt, dur, T, A):
    """粉色的云上，一个小丘比特拉满弓，一支心形箭头的箭嗖地射出去，拖着一串闪光"""
    sky(img, ((0, (255, 170, 210)), (0.6, (255, 206, 226)), (1, (255, 236, 220))))
    for i, (cx, cy, s) in enumerate(((40, 40, 1.6), (300, 20, 1.2), (380, 170, 2.0), (60, 190, 1.8))):
        cloud(d, cx - lt * 8 * (i % 2 + 1), cy, s, (255, 255, 255), (250, 226, 240), (255, 255, 255))
    x, y = 140, 130 + 4 * math.sin(lt * 4)
    draw = ease(span(lt, 0.0, 0.6)) if lt < 0.65 else 0
    nx, ny = cupid(img, d, x, y, T, 3, draw)
    if lt < 0.65:
        heart_arrow(d, nx, ny, nx + 40, ny)
        put(img, 'heart', nx + 44, ny, 2)
    else:
        k = lt - 0.65
        ax = nx + 40 + k * 520
        for j in range(10):
            twinkle(d, int(ax - 30 - j * 26), int(ny + math.sin(j + k * 10) * 4), ((k * 3 + j / 10) % 1), (255, 255, 255), 3)
            put(img, 'heart', ax - 40 - j * 30, ny + 6 * math.sin(j * 2 + k * 8), 1, tint=(255, 120, 170), alpha=1 - j / 10)
        heart_arrow(d, ax - 40, ny, ax, ny)
        put(img, 'heart', ax + 4, ny, 2)


@lru_cache(None)
def coin_face(dark, r=56):
    s = 2 * r + 4
    im = Image.new('RGBA', (s, s)); d = ImageDraw.Draw(im)
    c, cs, cl = ((70, 40, 90), (40, 20, 60), (140, 90, 170)) if dark else ((240, 186, 60), (190, 130, 30), (255, 236, 150))
    d.ellipse([2, 2, s - 3, s - 3], fill=cs, outline=OUT)
    d.ellipse([8, 8, s - 9, s - 9], fill=c)
    d.ellipse([14, 14, s - 15, s - 15], outline=cs, width=2)
    for k in range(24):
        a = k * math.pi / 12
        d.point((s / 2 + math.cos(a) * (r - 3), s / 2 + math.sin(a) * (r - 3)), fill=cl)
    cx, cy = s / 2, s / 2 + 4
    for side in (-1, 1):
        if dark:
            pts = [(cx + side * 10, cy - 6), (cx + side * 34, cy - 22), (cx + side * 28, cy - 8), (cx + side * 36, cy - 4), (cx + side * 26, cy + 4), (cx + side * 10, cy + 2)]
        else:
            pts = [(cx + side * 10, cy - 6), (cx + side * 30, cy - 24), (cx + side * 38, cy - 12), (cx + side * 30, cy - 2), (cx + side * 10, cy + 4)]
        d.polygon(pts, fill=cl if not dark else (110, 70, 140), outline=cs)
    hc = (255, 120, 150) if not dark else (60, 30, 70)
    hp = pix.heart_poly(cx, cy, 1.1)
    d.polygon(hp, fill=hc, outline=OUT)
    if dark:
        d.line([(cx - 2, cy - 12), (cx + 3, cy - 4), (cx - 3, cy + 2), (cx + 2, cy + 10)], fill=(20, 10, 30), width=2)
        d.line([(cx - 30, cy + 22), (cx + 30, cy - 22)], fill=(30, 20, 40), width=3)
    else:
        d.ellipse([cx - 8, cy - 8, cx - 3, cy - 3], fill=(255, 220, 230))
    return im


def s_coin(img, d, lt, dur, T, A):
    """一枚大金币在聚光灯下翻转：正面是长着翅膀的心，反面是一颗裂开的黑心，最后停在反面，冒出一个问号"""
    img.paste((14, 10, 26), (0, 0, W, H))
    tfill(img, 'polygon', [(200, 0), (280, 0), (380, H), (100, H)], (255, 240, 200), 0.08)
    glow(img, 240, 120, 120, (255, 220, 160), 0.15)
    settle = 1.7
    th = lt * 11 if lt < settle else settle * 11 + (math.pi - (settle * 11) % math.pi) * ease(span(lt, settle, settle + 0.3))
    if lt >= settle:
        th0 = settle * 11
        base = math.floor(th0 / (2 * math.pi)) * 2 * math.pi + math.pi
        if base < th0: base += 2 * math.pi
        th = lerp(th0, base, ease(span(lt, settle, settle + 0.35)))
    sx = math.cos(th)
    dark = sx < 0
    face = coin_face(dark)
    w = max(4, int(face.width * abs(sx)))
    f = face.resize((w, face.height), Image.NEAREST)
    hop = 30 * math.sin(math.pi * min(1, lt / settle)) if lt < settle else 0
    if w < 20:
        d.rectangle([240 - 5, 120 - 58 - hop, 240 + 5, 120 + 58 - hop], fill=(190, 130, 30) if not dark else (40, 20, 60), outline=OUT)
    paste(img, f, 240, 120 - hop, 1, 'cc')
    d.ellipse([200, 196, 280, 206], fill=(8, 6, 16))
    if lt > settle + 0.35:
        k = lt - settle - 0.35
        glow(img, 240, 120, 90, (150, 60, 200), 0.3)
        c = bubble(img, d, 320, 80, 30, 26, span(k, 0, 0.25), tail=(1, 1))
        if c: text(img, '?', c[0], c[1], (40, 30, 48), None, shadow=False, scale=1)


def s_timelapse(img, d, lt, dur, T, A):
    """他抱着膝盖坐在床边一动不动，窗外的太阳和月亮飞快地转，地上的光斑来回扫，窗台上的小花慢慢蔫了"""
    cyc = lt * 2.2
    day = 0.5 + 0.5 * math.sin(cyc * 2 * math.pi)
    wall = lerpc((30, 26, 52), (150, 130, 150), day)
    img.paste(wall, (0, 0, W, H))
    wx0, wy0, wx1, wy1 = 250, 30, 430, 150
    skc = lerpc((14, 12, 40), (130, 190, 250), day)
    d.rectangle([wx0, wy0, wx1, wy1], fill=skc)
    a = cyc * 2 * math.pi
    sxp, syp = (wx0 + wx1) / 2 - math.cos(a - math.pi / 2) * 100, wy1 - math.sin(a - math.pi / 2) * 110 + 20
    mxp, myp = (wx0 + wx1) / 2 + math.cos(a - math.pi / 2) * 100, wy1 + math.sin(a - math.pi / 2) * 110 + 20
    if wy0 < syp < wy1 + 20: d.ellipse([sxp - 12, syp - 12, sxp + 12, syp + 12], fill=(255, 230, 120))
    if wy0 < myp < wy1 + 20: moon(d, mxp, myp, 9)
    city(img, d, wy1, 31, 0, lerpc((24, 20, 50), (110, 140, 180), day), (255, 210, 120) if day < 0.4 else None, 16, 50, 0.4, T, 10, 20)
    d.rectangle([0, 0, wx0 - 1, H], fill=wall); d.rectangle([wx1 + 1, 0, W, H], fill=wall); d.rectangle([wx0, 0, wx1, wy0 - 1], fill=wall)
    d.rectangle([wx0 - 4, wy0 - 4, wx1 + 4, wy1 + 4], outline=lerpc((60, 50, 80), (120, 100, 110), day), width=3)
    d.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=lerpc((60, 50, 80), (120, 100, 110), day), width=2)
    d.rectangle([wx0 - 8, wy1 + 4, wx1 + 8, wy1 + 9], fill=lerpc((70, 56, 80), (180, 160, 150), day), outline=OUT)
    wilt = span(lt, 0.2, dur)
    px = wx1 - 24
    d.rectangle([px - 6, wy1 - 6, px + 6, wy1 + 4], fill=(170, 90, 60), outline=OUT)
    tipx = px + 10 * wilt; tipy = wy1 - 24 + 14 * wilt
    d.line([(px, wy1 - 6), (px + 2 * wilt, wy1 - 16), (tipx, tipy)], fill=lerpc((70, 160, 70), (130, 120, 60), wilt), width=2)
    d.ellipse([tipx - 4, tipy - 4, tipx + 4, tipy + 4], fill=lerpc((255, 120, 150), (150, 110, 90), wilt), outline=OUT)
    d.rectangle([0, 190, W, H], fill=lerpc((44, 36, 60), (170, 140, 130), day))
    shift = math.cos(a) * 120
    if day > 0.2:
        tfill(img, 'polygon', [(wx0 + shift, 194), (wx1 + shift, 194), (wx1 + shift - 40, 240), (wx0 + shift - 60, 240)], (255, 240, 200), 0.25 * day)
    d.rectangle([30, 160, 200, 200], fill=lerpc((60, 50, 90), (130, 110, 150), day), outline=OUT)
    d.rectangle([30, 150, 200, 166], fill=lerpc((180, 176, 200), (240, 236, 250), day), outline=OUT)
    person(img, 'boy', 200, 230, view='side', pose='sit', expr='down', arms='lap', s=2, flip=True)
    cx_, cy_ = 120, 70
    pix_clock(d, cx_, cy_, 16, lt * 30)
    nd = int(cyc)
    for i in range(nd + 1):
        x0 = 40 + (i // 5) * 18 + (i % 5) * 3
        if i % 5 < 4: d.line([(x0, 104), (x0, 116)], fill=(220, 214, 230))
        else: d.line([(x0 - 14, 114), (x0, 106)], fill=(220, 214, 230))


def pix_clock(d, x, y, r, t):
    d.ellipse([x - r - 1, y - r - 1, x + r + 1, y + r + 1], fill=(120, 90, 70))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(250, 246, 232))
    am = t * 2 * math.pi; ah = am / 12
    d.line([(x, y), (x + math.sin(am) * (r - 3), y - math.cos(am) * (r - 3))], fill=(50, 40, 50))
    d.line([(x, y), (x + math.sin(ah) * (r - 7), y - math.cos(ah) * (r - 7))], fill=(50, 40, 50), width=2)


@lru_cache(None)
def roundabout_base():
    im = Image.new('RGB', (W, H), (40, 38, 54)); d = ImageDraw.Draw(im)
    r = rng(8)
    for _ in range(1500): d.point((r.randrange(W), r.randrange(H)), fill=(46, 44, 60))
    cx, cy = 240, 128
    for (x0, y0, x1, y1) in ((0, 0, 190, 70), (290, 0, W, 70), (0, 190, 190, H), (290, 190, W, H)):
        d.rectangle([x0, y0, x1, y1], fill=(86, 84, 102))
        d.rectangle([x0 + 10, y0 + 10, x1 - 10, y1 - 10], fill=(56, 50, 74), outline=OUT)
        for k in range(3):
            ax, ay = r.uniform(x0 + 16, x1 - 30), r.uniform(y0 + 16, max(y0 + 17, y1 - 26))
            d.rectangle([ax, ay, ax + 10, ay + 7], fill=(150, 150, 166), outline=OUT)
    d.rectangle([190, 0, 290, H], fill=(36, 34, 46)); d.rectangle([0, 70, W, 190], fill=(36, 34, 46))
    d.ellipse([cx - 110, cy - 96, cx + 110, cy + 96], fill=(36, 34, 46))
    d.ellipse([cx - 62, cy - 50, cx + 62, cy + 50], fill=(120, 118, 136))
    d.ellipse([cx - 56, cy - 44, cx + 56, cy + 44], fill=(50, 110, 70))
    for k in range(48):
        a = k * 2 * math.pi / 48
        if k % 2: d.point((cx + math.cos(a) * 86, cy + math.sin(a) * 72), fill=(220, 220, 214))
    return im


def s_roundabout(img, d, lt, dur, T, A):
    """从上往下看，他的车在环岛里一圈一圈地绕，左转灯一直闪，出口一个也没拐出去"""
    img.paste(roundabout_base())
    cx, cy = 240, 128
    tree_top(d, cx - 16, cy - 8, 16); tree_top(d, cx + 18, cy + 10, 12)
    th = lt * 4.2 - 1.0
    for k in range(40):                                        # 尾灯留下的光圈
        a = th - k * 0.09
        x, y = cx + math.cos(a) * 80, cy + math.sin(a) * 66
        d.rectangle([x, y, x + 1, y + 1], fill=lerpc(AMB, (36, 34, 46), k / 40) if k % 2 else lerpc((255, 60, 60), (36, 34, 46), k / 40))
    x, y = cx + math.cos(th) * 80, cy + math.sin(th) * 66
    ang = math.degrees(th) + 180
    car_top_at(img, x, y, ang, 1, sig_l=blink_a(T), beams=False)
    for (ax, ay, dirn) in ((240, 14, 'up'), (466, 128, 'right'), (14, 128, 'left')):
        if dirn == 'up': props.arrow(img, ax, ay, 1, 0.0, off=(150, 150, 160), glow_r=0)
        elif dirn == 'right': props.arrow(img, ax, ay, 1, 0.0, left=False, off=(150, 150, 160), glow_r=0)
        else: props.arrow(img, ax, ay, 1, 0.0, off=(150, 150, 160), glow_r=0)
    lap = int((lt * 4.2) / (2 * math.pi)) + 1
    text(img, f'LAP {lap}', 420, 30, AMB_L, OUT, FONT_S)
    rain_top(img, d, T, 60)
    vig(img, 0.5)


def s_notifs(img, d, lt, dur, T, A):
    """锁屏上的草稿通知一条接一条往下堆，每一条都是一颗没发出去的心"""
    sky(img, ((0, (20, 14, 40)), (1, (40, 24, 60))))
    def scr(sc, sd, w, h):
        ph = court_photo(w, int(w * 0.66)).resize((w, h), Image.NEAREST)
        a = np.asarray(ph, float) * 0.45
        sc.paste(Image.fromarray(a.astype(np.uint8)))
        tw = FONT.getlength('03:14') * 2
        big = Image.new('RGBA', (int(tw / 2) + 4, 20)); bd = ImageDraw.Draw(big); bd.fontmode = '1'; bd.text((2, 1), '03:14', font=FONT, fill=(255, 255, 255))
        big = big.resize((big.width * 2, big.height * 2), Image.NEAREST); sc.paste(big, (int(w / 2 - big.width / 2), 8), big)
        n = int(18 * span(lt, 0.0, dur * 0.8) ** 1.2) + 1
        for k in range(n):
            y = 56 + (n - 1 - k) * 22
            if y > h: continue
            sd.rounded_rectangle([4, y, w - 4, y + 18], 5, fill=(236, 236, 244))
            sd.ellipse([8, y + 3, 20, y + 15], fill=PINK)
            sd.rectangle([24, y + 4, 24 + 30, y + 6], fill=(60, 60, 80))
            sd.rectangle([24, y + 10, 24 + 50 - (k * 7) % 20, y + 12], fill=(140, 140, 160))
    phone(img, d, 240, 128, 120, 214, scr)
    cnt = int(1000 * span(lt, 0.0, dur * 0.8) ** 1.2)
    d.rounded_rectangle([330, 40, 450, 70], 8, fill=(30, 10, 30), outline=PINK)
    put(img, 'heart', 348, 55, 2)
    text(img, f'草稿×{cnt}', 400, 55, (255, 255, 255), OUT, FONT_S)


def s_plus1b(img, d, lt, dur, T, A):
    """还是那块手机屏幕：最上面又多了一条，右上角的红点跳成“+1”"""
    s_notifs(img, d, 1.5, 1.5, T, A)
    b = span(lt, 0.1, 0.35)
    if b > 0:
        r = 26 * eback(b)
        d.ellipse([300 - r, 40 - r, 300 + r, 40 + r], fill=AMB, outline=OUT)
        if b > 0.6: text(img, '+1', 300, 40, (255, 255, 255), OUT, scale=2)
        burst(img, d, lt - 0.1, 300, 40, life=0.9, scale=0.8)
    if lt < 0.12: darken(img, 0.4 * (1 - lt / 0.12), (255, 240, 250))
