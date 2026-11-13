"""左转灯 · 片头、主歌和第一段副歌。签名都是 (img, d, lt, dur, T, A)：lt 是镜头内的时间，dur 是镜头时长，T 是全片时间，A 是这一帧的音量。

故事：他（琥珀色卫衣）开着一辆奶白色的小车，雨夜停在路口，左转灯一直在闪。她（青绿色球衣）已经离开。
回忆像飞机一样降落在没有信号的地方，他把谎话写成小说，和她拉扯着不肯松手，在镜子里看见了自己讨厌的样子。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
import props
from props import *          # noqa: F401,F403  共用的颜色和道具
from pix import person, wph, put, twinkle, sparkle, hills, moon, cloud, darken, dither_fade, grade, vig, vgrad, BAYER, bayer


def title_str():
    return pix.META.get('ti') or '左转灯'


def bar_near(t, tol=0.45):
    """离 t 最近的小节线（误差太大时就用 t）"""
    b = pix.AUDIO['bars']
    if len(b) == 0: return t
    x = b[int(np.argmin(np.abs(b - t)))]
    return float(x) if abs(x - t) < tol else t


def beat_after(t, n=1):
    bs = [x for x in pix.AUDIO['beats'] if x > t + 0.05]
    return float(bs[n - 1]) if len(bs) >= n else t + 0.9 * n


def rain_lit(d, T, n, cx, cy, r, on, dim=(34, 30, 64), lit=AMB_L, speed=260, seed=0, box=(0, 0, W, H)):
    """雨丝：离光源越近越亮"""
    x0, y0, x1, y1 = box
    sp = y1 - y0; wid = x1 - x0
    for i in range(n):
        ph = ((i * 37 + seed * 13) % 97) / 97
        y = y0 + (T * speed * (0.85 + (i % 3) * 0.1) + ph * sp) % sp
        x = x0 + ((i * 73 + seed * 31) % wid) - 3 * (y - y0) / sp * 4
        k = max(0.0, 1 - math.hypot(x - cx, y - cy) / r) * on
        d.line([(x, y), (x - 1, y + 6)], fill=lerpc(dim, lit, k))


# ================================================================ 片头
INTRO_SKY = ((0, (6, 4, 22)), (0.3, (24, 14, 56)), (0.62, (54, 28, 86)), (1, (70, 40, 96)))


def facade(img, d, x0, x1, roof, cam, seed, col, edge, frac=0.45, T=0.0, ground=690):
    """一栋楼的正面：roof 是楼顶的世界坐标，cam 是镜头往下摇的距离。地面层另画"""
    top = roof - cam; bot = 740 - cam
    if bot < 0 or top > H: return
    d.rectangle([x0, max(-2, top), x1, min(H + 2, bot)], fill=col)
    if -4 < top < H: d.rectangle([x0 - 2, top - 3, x1 + 2, top], fill=edge)
    r = rng(seed)
    cols = list(range(x0 + 6, x1 - 8, 14))
    for row, wy in enumerate(range(roof + 12, ground - 10, 16)):
        sy = wy - cam
        states = [r.random() for _ in cols]
        if not -12 < sy < H: continue
        for k, (wx, s) in enumerate(zip(cols, states)):
            if s < frac:
                c = (255, 208, 120) if s < frac * 0.7 else (140, 196, 255)
                d.rectangle([wx, sy, wx + 7, sy + 8], fill=c)
                d.rectangle([wx, sy + 7, wx + 7, sy + 8], fill=lerpc(c, (0, 0, 0), 0.25))
                if (row * 7 + k * 3 + seed) % 11 == 0:                 # 窗里有人
                    d.ellipse([wx + 2, sy + 2, wx + 5, sy + 5], fill=lerpc(c, (20, 10, 30), 0.7))
                    d.rectangle([wx + 1, sy + 6, wx + 6, sy + 8], fill=lerpc(c, (20, 10, 30), 0.7))
                elif (row * 5 + k + seed) % 13 == 0:                   # 窗台上的盆栽
                    d.rectangle([wx + 1, sy + 6, wx + 3, sy + 8], fill=(60, 40, 40)); d.point([(wx + 2, sy + 4), (wx + 1, sy + 5), (wx + 3, sy + 5)], fill=(60, 120, 70))
            else:
                d.rectangle([wx, sy, wx + 7, sy + 8], fill=lerpc(col, (0, 0, 0), 0.35))
            d.line([(wx - 1, sy + 9), (wx + 8, sy + 9)], fill=edge)


def intro_title_layout(scale=4):
    s = title_str()
    pts, wtot = glyph_pixels(s, scale)
    x0 = 240 - wtot / 2
    return s, pts, x0


def intro_world(img, d, T, lt, cam, tb):
    """片头的整座楼：楼顶的霓虹招牌、楼面、地面层的便利店和马路。cam 是镜头往下摇的距离（0 到 540）"""
    img.paste(vgrad(W, 810, INTRO_SKY, 6).crop((0, int(cam), W, int(cam) + H)), (0, 0))
    for x, y, p, k in pix.STARS[:150]:
        sy = y * 0.75 - cam * 0.4
        if 0 <= sy < 200:
            b = 0.5 + 0.5 * math.sin(T * (1.5 + k * 2.5) + p)
            if b > 0.2: d.point((x, sy), fill=lerpc((40, 30, 80), (255, 250, 220), b))
    # 远处的城市
    city(img, d, 300 - cam * 0.35, 3, T * 1.5, (34, 24, 66), (120, 96, 160), 50, 130, 0.25, T, 10, 24)
    city(img, d, 330 - cam * 0.55, 9, T * 3, (24, 18, 48), (255, 200, 120), 40, 110, 0.3, T)
    # 两边的楼和中间这栋
    facade(img, d, -10, 124, 330, cam, 41, (26, 20, 48), (40, 32, 66), 0.42, T)
    facade(img, d, 358, 490, 380, cam, 43, (30, 22, 52), (44, 34, 70), 0.4, T)
    facade(img, d, 132, 350, 250, cam, 42, (34, 26, 60), (52, 40, 82), 0.48, T)
    # 楼顶：水箱、天线、招牌的架子
    ry = 250 - cam
    if ry > -120:
        d.rectangle([150, ry - 26, 176, ry - 3], fill=(44, 36, 70)); d.ellipse([150, ry - 31, 176, ry - 22], fill=(56, 46, 86))
        for k in range(4): d.line([(152 + k * 7, ry - 3), (152 + k * 7, ry)], fill=(30, 24, 50))
        d.line([(330, ry - 3), (330, ry - 44)], fill=(60, 52, 90))
        if math.sin(T * 3) > 0: d.rectangle([329, ry - 46, 331, ry - 45], fill=(255, 70, 70)); glow(img, 330, ry - 45, 6, (255, 60, 60), 0.5)
        fy0, fy1 = 56 - cam, 196 - cam
        for lx in (104, 200, 280, 376):
            d.line([(lx, fy1), (lx, ry - 2)], fill=(52, 44, 78), width=2)
            for yy in range(int(fy1), int(ry), 8): d.line([(lx, yy), (lx + (8 if lx < 352 else -8), yy + 8)], fill=(42, 36, 66))
        d.rectangle([88, fy0, 392, fy1], fill=(18, 12, 34), outline=(56, 46, 86))
        d.rectangle([90, fy0 + 2, 390, fy1 - 2], outline=(30, 24, 52))
        for bx in range(100, 390, 30): d.point((bx, fy1 - 4), fill=(255, 220, 150))
    # 地面层（世界坐标 690–740）
    gy = 690 - cam
    if gy < H + 10:
        d.rectangle([132, gy, 350, gy + 50], fill=(30, 24, 54))
        d.rectangle([150, gy + 14, 332, gy + 50], fill=(200, 236, 240))                  # 便利店的玻璃门面
        for k in range(4):
            sx = 160 + k * 44
            d.rectangle([sx, gy + 22, sx + 30, gy + 23], fill=(130, 160, 180)); d.rectangle([sx, gy + 32, sx + 30, gy + 33], fill=(130, 160, 180))
            for j in range(6): d.rectangle([sx + j * 5, gy + 18, sx + j * 5 + 3, gy + 21], fill=[(255, 120, 120), (255, 210, 90), (120, 200, 255)][(j + k) % 3])
        for k in range(150, 333, 46): d.line([(k, gy + 14), (k, gy + 50)], fill=(150, 180, 190))
        d.rectangle([140, gy + 2, 342, gy + 12], fill=TEAL_S)
        text(img, '24H', 241, gy + 7, TEAL_L, (10, 40, 40), FONT_S, shadow=False)
        glow(img, 241, gy + 34, 110, (190, 240, 255), 0.22, 30)
        d.rectangle([-10, gy + 4, 124, gy + 50], fill=(46, 40, 60))                       # 左边拉下卷帘门的店
        for yy in range(int(gy) + 8, int(gy) + 50, 3): d.line([(4, yy), (118, yy)], fill=(62, 56, 78))
        d.rectangle([358, gy + 8, 490, gy + 50], fill=(60, 34, 34))                       # 右边的面馆
        d.rectangle([372, gy + 20, 470, gy + 50], fill=(255, 196, 120))
        for lx in (380, 460):
            d.ellipse([lx - 5, gy + 6, lx + 5, gy + 18], fill=(230, 60, 60)); glow(img, lx, gy + 12, 12, (255, 90, 80), 0.4)
        glow(img, 420, gy + 36, 60, (255, 190, 110), 0.2, 20)
        sw = 740 - cam
        d.rectangle([0, sw, W, sw + 5], fill=(70, 64, 90)); d.rectangle([0, sw + 5, W, sw + 7], fill=(110, 104, 128))
        d.rectangle([0, sw + 8, W, H + 600], fill=(30, 28, 44))
        for x in range(-20, W, 48): d.rectangle([x + int(-T * 0) % 48, sw + 40, x + 24, sw + 41], fill=(150, 146, 140))


def intro_neon(img, d, T, lt, cam, glyph_lock, sub_t, arrow_t):
    """招牌上的片名：拍点上锁定的大字，失灵似的闪一下；左边的箭头跟着拍子亮，右边的箭头一直是暗的"""
    s, pts, x0 = intro_title_layout(4)
    cy = 116 - cam
    if cy < -80: return
    lit_any = [lt >= t for t in glyph_lock]
    if any(lit_any): glow(img, 240, cy, 150, AMB, 0.22 * sum(lit_any) / 3, 60)
    adv = [FONT.getlength(c) * 4 for c in s]
    gx = x0
    for i, ch in enumerate(s):
        if lt >= glyph_lock[i]:
            on = 1.0
            if i == len(s) - 1:                                  # 最后一个字像接触不良的霓虹灯管
                k = lt - (glyph_lock[-1] + 2.1)
                if 0 <= k < 0.55 and int(k * 22) % 3 != 0: on = 0.0
            g = big_glyph(ch, 4, AMB_L, AMB, (150, 66, 18)) if on else big_glyph(ch, 4, (90, 60, 50), (70, 46, 40), (40, 30, 34))
            k = lt - glyph_lock[i]
            img.paste(g, (int(gx - 4 * 4 + 2), int(cy - 52 + 2 - (3 if k < 0.08 else 0))), g)
            if k < 0.3: glow(img, gx + adv[i] / 2, cy - 4, 46, (255, 250, 220), 0.6 * (1 - k / 0.3))
        gx += adv[i]
    if lt >= arrow_t:
        props.arrow(img, 112, cy - 4, 2, blink_a(T))
        props.arrow(img, 368, cy - 4, 2, 0.0, left=False, glow_r=0)
    if lt >= sub_t:
        sub = 'LEFT  TURN  SIGNAL'
        n = int((lt - sub_t) / 0.04)
        text(img, sub[:n], 240, cy + 46, (255, 236, 200), (60, 24, 30), FONT_S)


def intro_particles(img, d, lt, glyph_lock):
    s, pts, x0 = intro_title_layout(4)
    for gi, plist in enumerate(pts):
        tl = glyph_lock[gi]; ts = tl - 1.05
        if not ts <= lt < tl: continue
        for j, (px, py) in enumerate(plist[::1]):
            r = rng(gi * 1000 + j)
            delay = r.uniform(0, 0.35)
            u = clamp((lt - ts - delay) / (tl - ts - delay))
            if u <= 0: continue
            sx, sy = W - 30 + r.uniform(0, 120), r.uniform(10, 250)
            tx, ty = x0 + px - 4 + 2, 116 - 52 + 2 + 3 * 4 + py + 3
            e = ease(u)
            x = lerp(sx, tx, e); y = lerp(sy, ty, e) - math.sin(math.pi * e) * r.uniform(-30, 30)
            e2 = ease(max(0, u - 0.08))
            x2 = lerp(sx, tx, e2); y2 = lerp(sy, ty, e2) - math.sin(math.pi * e2) * r.uniform(-30, 30)
            col = AMB_L if j % 3 else (255, 255, 255)
            d.line([(x2, y2), (x, y)], fill=lerpc((120, 60, 30), col, 0.6))
            d.rectangle([x, y, x + 3, y + 3], fill=col)


def s_intro(img, d, lt, dur, T, A):
    tb1, tb2, tb3, tb4, tb5 = (bar_near(x) for x in (1.13, 4.77, 8.42, 12.05, 15.69))
    locks = [beat_after(tb2, 1), beat_after(tb2, 2), beat_after(tb2, 3)]
    cam_a, cam_b = tb3 + 1.6, tb4 + 0.35
    cam = 540 * ease(span(lt, cam_a, cam_b))
    if lt < tb2:
        # ---- 黑暗里只有一个转向灯在跟着拍子闪，每闪一下变大一点，旁边蹦出“嗒”
        img.paste((6, 4, 14), (0, 0, W, H))
        on = blink_a(T)
        nb = len(beats_in(0, T + 0.01))
        s = int(clamp(3 + nb * 0.6, 3, 6))
        glow(img, 240, 210, 140, AMB, 0.16 * on, 22)
        rain_lit(d, T, 150, 240, 120, 170, on)
        d.line([(0, 206), (W, 206)], fill=lerpc((14, 12, 26), (90, 60, 40), on))
        props.arrow(img, 240, 120, s, on, glow_r=20 * s)
        for k, b in enumerate(beats_in(0, T + 0.01)):
            u = (T - b) / 0.5
            if 0 <= u < 1:
                x = 240 + (-1 if k % 2 else 1) * (40 + 8 * s)
                text(img, '嗒', x, 100 - 16 * eout(u), AMB_L, (60, 24, 10), alpha=1 - u * u, scale=2)
        if lt > tb2 - 0.9:                                   # 最后一拍前箭头往后缩，准备冲出去
            u = span(lt, tb2 - 0.9, tb2)
            glow(img, 240, 120, 30 + 60 * u, (255, 240, 200), 0.3 * u)
        return
    # ---- 片名：箭头冲向左边留下一道光，光点从右边飞来拼成片名，拍点上一个字一个字锁定
    intro_world(img, d, T, lt, cam, tb4)
    intro_neon(img, d, T, lt, cam, locks, locks[-1] + 0.5, locks[0])
    if lt < locks[-1]: intro_particles(img, d, lt, locks)
    k = lt - tb2
    if k < 0.5:
        x = lerp(240, -80, ein(k / 0.5))
        d.rectangle([x, 117, 240, 122], fill=AMB_L); glow(img, (x + 240) / 2, 120, 160, AMB, 0.4 * (1 - k / 0.5), 10)
        props.arrow(img, x, 120, 6, 1.0)
        if k < 0.12: darken(img, 0.6 * (1 - k / 0.12), (255, 240, 210))
    for tl in locks:
        props.shake(img, lt - tl, 3, 0.2)
    rain(d, T, 0, W, 0, H, 110, (80, 80, 132), 280, -3, 6)
    # ---- 镜头摇到街上：小车开进来停在红灯前，左转灯一直在闪
    if cam > 300:
        street(img, d, T, lt, cam, tb4, tb5)


def street(img, d, T, lt, cam, tb4, tb5):
    sw = 740 - cam
    # 红绿灯
    px = 430
    d.rectangle([px, sw - 150, px + 2, sw], fill=(60, 56, 80))
    d.rectangle([px - 34, sw - 150, px + 2, sw - 148], fill=(60, 56, 80))
    hx, hy = px - 40, sw - 158
    d.rounded_rectangle([hx - 8, hy, hx + 8, hy + 40], 3, fill=(24, 22, 34), outline=OUT)
    green = lt >= tb5
    for j, c in enumerate([(255, 60, 60), (255, 190, 40), (60, 230, 120)]):
        on = (j == 0 and not green) or (j == 2 and green)
        d.ellipse([hx - 5, hy + 3 + j * 12, hx + 5, hy + 13 + j * 12], fill=c if on else lerpc(c, (20, 20, 30), 0.8))
        if on: glow(img, hx, hy + 8 + j * 12, 22, c, 0.5)
    if green:
        props.arrow(img, hx, hy + 52, 1, 1.0, col=(60, 230, 120), glow_r=10)
    lamp(img, d, 60, sw, 1.0, 66)
    lamp(img, d, 300, sw, 1.0, 66)
    # 小车：减速开进来，停在停车线前
    u = span(lt, tb4 - 0.2, tb4 + 1.7)
    x = lerp(-90, 250, eout(u))
    gy = sw + 52
    reflect(img, int(sw + 8), H - int(sw + 8), T, a=0.55, amp=1.5)
    car_reflection(img, x, gy, 2, blink_a(T))
    car(img, x, gy, blink_a(T), int(x / 6), 2, brake=u >= 1)
    splashes(d, T, sw + 10, H, 30)
    if u >= 1 and blink(T) and beat_phase(T)[0] < 0.2:
        text(img, '嗒', x - 70, gy - 50 - 8 * beat_phase(T)[0] * 5, AMB_L, (60, 24, 10), FONT_S)


def car_reflection(img, x, gy, s, sig, flip=False, a=0.35):
    """湿路面上车子的倒影：上下翻转、压暗、隔行抖动"""
    im = car_side(int(sig > 0.5), 0, True, False, CAR, CAR_S, driver='boy')
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = im.resize((im.width * s, im.height * s), Image.NEAREST).transpose(Image.FLIP_TOP_BOTTOM)
    arr = np.array(im)
    arr[..., :3] = (arr[..., :3] * 0.45 + np.array((20, 18, 50)) * 0.55).astype(np.uint8)
    arr[1::2, :, 3] = 0
    im = Image.fromarray(arr)
    paste(img, im, x, gy + 2 * s, a, 'lt' if False else 'cc') if False else img.paste(im, (int(x - im.width / 2), int(gy + 2 * s)), with_alpha(im, a))
    if sig > 0.3:
        glow(img, x + (27 if not flip else -27) * s, gy + 10 * s, 8 * s, AMB, 0.35 * sig)


# ================================================================ 主歌
@lru_cache(None)
def plane_img():
    """侧面的客机，机头朝左，76×26"""
    im = Image.new('RGBA', (78, 28)); d = ImageDraw.Draw(im)
    d.polygon([(60, 12), (66, 1), (73, 1), (74, 12)], fill=(220, 222, 236))         # 尾翼
    d.polygon([(66, 3), (72, 3), (72, 9), (64, 9)], fill=AMB)
    d.rounded_rectangle([4, 10, 74, 19], 5, fill=(240, 242, 250))
    d.rectangle([10, 16, 72, 19], fill=(200, 204, 222))
    d.polygon([(4, 14), (8, 10), (14, 10), (14, 14)], fill=(240, 242, 250))
    d.polygon([(6, 12), (10, 11), (12, 13)], fill=(50, 70, 110))                      # 驾驶舱
    for x in range(16, 62, 4): d.rectangle([x, 13, x + 1, 14], fill=(255, 220, 140))
    d.polygon([(30, 17), (48, 17), (56, 26), (50, 26)], fill=(200, 204, 222))         # 机翼
    d.rounded_rectangle([34, 19, 44, 23], 2, fill=(170, 174, 196))                    # 发动机
    d.polygon([(64, 14), (74, 13), (77, 15), (68, 16)], fill=(200, 204, 222))
    return outline(im, OUT)


def nosignal(img, d, x, y, T):
    for k in range(4):
        h = 3 + k * 2
        d.rectangle([x + k * 4, y - h, x + k * 4 + 2, y], outline=(130, 126, 150))
    if int(T * 4) % 2 == 0:
        d.line([(x + 16, y - 8), (x + 22, y - 2)], fill=RED, width=2); d.line([(x + 22, y - 8), (x + 16, y - 2)], fill=RED, width=2)
    text(img, '无服务', x - 26, y - 4, (220, 216, 236), OUT, FONT_S)


def mini_photo(d, x, y, k, flip):
    """一张飘落的小照片，flip 是翻转的程度（-1..1）"""
    w = max(1, int(round(3 * abs(flip))))
    d.rectangle([x - w, y - 4, x + w, y + 4], fill=CREAM if flip > 0 else (220, 210, 196))
    if flip > 0 and w >= 2:
        c = [AMB, TEAL, PINK, (140, 120, 255)][k % 4]
        d.rectangle([x - w + 1, y - 3, x + w - 1, y + 1], fill=c)


def s_plane(img, d, lt, dur, T, A):
    """回忆像一架夜航的飞机，降落在荒野里一条没有信号的跑道上，一路掉下小照片"""
    sky(img, ((0, (10, 8, 30)), (0.6, (40, 26, 78)), (1, (112, 60, 112))), 0, 192)
    pix.stars(d, T, 160, 0.9, 160)
    moon(d, 70, 46, 12); glow(img, 70, 46, 40, (250, 240, 200), 0.22)
    for i, (cx, cy, s) in enumerate([(120, 70, 1.2), (300, 40, 1.6), (420, 96, 1.0)]):
        cloud(d, (cx - lt * 10 * (i + 1)) % 560 - 60, cy, s, (54, 40, 92), (44, 32, 78))
    hills(d, 184, 5, 0.025, 1.0, (32, 24, 56))
    hills(d, 190, 3, 0.05, 3.0, (24, 18, 42))
    d.rectangle([0, 192, W, H], fill=(18, 16, 32))
    d.rectangle([0, 197, 410, 206], fill=(50, 48, 66))
    for x in range(30, 400, 22): d.rectangle([x, 201, x + 10, 201], fill=(200, 200, 190))
    for x in range(70, 90, 4): d.rectangle([x, 198, x + 1, 205], fill=(220, 220, 210))
    for i, x in enumerate(range(4, 410, 14)):
        c = AMB if i % 2 else (255, 250, 230)
        d.point([(x, 196), (x, 207)], fill=c)
    run = int(T * 14) % 6                                       # 引进灯：一串亮光朝跑道跑过去
    for j in range(6):
        x = 470 - j * 10
        on = j == run
        d.rectangle([x, 201, x + 1, 202], fill=(255, 255, 255) if on else (90, 90, 110))
        if on: glow(img, x, 201, 8, (255, 255, 240), 0.6)
    # 没有信号的信号塔
    tx = 440
    d.line([(tx - 8, 196), (tx, 120)], fill=(70, 62, 96)); d.line([(tx + 8, 196), (tx, 120)], fill=(70, 62, 96))
    for yy in range(130, 196, 10): d.line([(tx - (yy - 120) / 76 * 8, yy), (tx + (yy - 120) / 76 * 8, yy)], fill=(56, 50, 80))
    if blink(T): d.rectangle([tx - 1, 117, tx + 1, 119], fill=(255, 70, 70)); glow(img, tx, 118, 8, (255, 60, 60), 0.5)
    for k in range(3):
        r = 10 + k * 7
        for a in range(-60, 61, 12):
            if (a // 12 + k) % 2 == 0:
                aa = math.radians(a - 90)
                d.point((tx + 6 + r * math.cos(aa + math.pi / 2), 120 + r * math.sin(aa + math.pi / 2) * 0.9), fill=(100, 90, 130))
    d.line([(tx + 10, 108), (tx + 26, 124)], fill=RED, width=2); d.line([(tx + 26, 108), (tx + 10, 124)], fill=RED, width=2)
    # 飞机
    def P(f):
        f = clamp(f)
        return lerp(560, 205, f), lerp(48, 190, f ** 1.15)
    f = lt / dur
    x, y = P(f)
    x2, y2 = P(f + 0.02)
    ang = math.degrees(math.atan2(y2 - y, x - x2))
    tfill(img, 'polygon', [(x - 34, y + 6), (x - 30, y + 10), (x - 150, y + 80), (x - 170, y + 40)], (255, 246, 210), 0.14)
    glow(img, x - 34, y + 6, 12, (255, 250, 230), 0.6)
    pl = plane_img().rotate(ang * 0.8, resample=Image.NEAREST, expand=True)
    paste(img, pl, x, y, 1, 'cc')
    if blink(T): glow(img, x + 34, y - 10, 7, (255, 60, 60), 0.7); d.point((x + 34, y - 10), fill=(255, 120, 120))
    if beat_phase(T)[0] < 0.12: glow(img, x + 4, y + 14, 9, (255, 255, 255), 0.8)
    # 掉下来的小照片
    for k in range(int(lt / 0.11) + 1):
        ts = k * 0.11; age = lt - ts
        if age < 0 or age > 3.2: continue
        bx, by = P(ts / dur)
        r = rng(k * 7)
        px_ = bx + 30 + age * r.uniform(4, 16) + 5 * math.sin(age * 3 + k)
        py_ = by + 4 + age * 16 + age * age * 7
        if py_ > 194: continue
        mini_photo(d, px_, py_, k, math.sin(age * r.uniform(3, 6) + k))
    nosignal(img, d, 430, 22, T)


def chair_row(d, x0, n, y, col=(56, 104, 180), col_s=(40, 76, 140)):
    for i in range(n):
        x = x0 + i * 12
        d.rectangle([x, y, x + 10, y + 9], fill=col)
        d.rectangle([x, y + 9, x + 10, y + 12], fill=col_s)
        d.rectangle([x + 1, y + 1, x + 9, y + 2], fill=lerpc(col, (255, 255, 255), 0.25))
    d.rectangle([x0, y + 13, x0 + n * 12 - 2, y + 14], fill=(90, 90, 110))
    for x in (x0 + 2, x0 + n * 12 - 6): d.rectangle([x, y + 15, x + 1, y + 20], fill=(90, 90, 110))


def flap_board(img, d, x, y, T, lt, rows):
    d.rectangle([x, y, x + 164, y + 10 + 12 * len(rows)], fill=(14, 12, 20), outline=(70, 66, 90))
    for r, (s, col) in enumerate(rows):
        for c, ch in enumerate(s):
            settle = 0.25 + r * 0.35 + c * 0.05
            cx = x + 6 + c * 10; cy = y + 6 + r * 12
            d.rectangle([cx - 1, cy - 1, cx + 7, cy + 9], fill=(30, 28, 40))
            d.line([(cx - 1, cy + 4), (cx + 7, cy + 4)], fill=(8, 8, 12))
            if lt < settle:
                ch = 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789'[int(T * 30 + r * 7 + c * 3) % 33]
            if ch != ' ':
                if col == RED and lt > settle and int(T * 3) % 2: continue
                d.text((cx, cy - 2), ch, font=FONT_S, fill=col)


def s_airport(img, d, lt, dur, T, A):
    """空无一人的机场：大玻璃窗外停着刚降落的飞机，一颗小小的心穿过入境的安检门"""
    ox = lt * 7
    d.rectangle([0, 0, W, 26], fill=(18, 16, 30))
    for x in range(-40, W + 40, 60): d.rectangle([x - ox % 60, 8, x - ox % 60 + 30, 10], fill=(220, 230, 255)); glow(img, x - ox % 60 + 15, 12, 18, (200, 220, 255), 0.18)
    # 窗外
    sky(img, ((0, (12, 12, 34)), (1, (52, 36, 90))), 26, 150)
    pix.stars(d, T, 100, 0.6, 60)
    city(img, d, 130, 5, ox * 0.3, (32, 26, 60), (120, 100, 160), 10, 34, 0.3, T, 10, 22)
    d.rectangle([0, 130, W, 150], fill=(26, 24, 40))
    for x in range(0, W, 9): d.point((x - int(ox * 0.6) % 9, 136), fill=AMB if (x // 9) % 2 else (240, 240, 230))
    pl = plane_img().resize((156, 56), Image.NEAREST)
    paste(img, pl, 260 - ox * 0.6, 136, 1, 'cb')
    if blink(T): glow(img, 260 - ox * 0.6 + 66, 100, 8, (255, 60, 60), 0.6)
    d.polygon([(330 - ox * 0.6, 110), (380 - ox * 0.6, 106), (380 - ox * 0.6, 118), (330 - ox * 0.6, 120)], fill=(70, 66, 90))  # 登机桥
    for x in range(-50, W + 60, 52):
        xx = x - int(ox) % 52
        d.rectangle([xx, 26, xx + 3, 150], fill=(40, 38, 58))
    d.rectangle([0, 86, W, 88], fill=(40, 38, 58))
    d.rectangle([0, 150, W, 172], fill=(44, 40, 64))
    d.rectangle([0, 172, W, H], fill=(56, 52, 80))
    for x in range(-60, W + 60, 40): d.line([(x - int(ox * 1.3) % 40, 172), (x - int(ox * 1.3) % 40 - 60, H)], fill=(50, 46, 72))
    reflect(img, 172, 98, T, (20, 18, 40), a=0.5, amp=0.4, src_h=146)
    # 指示牌和航班屏
    sx = 70 - ox * 0.4
    d.line([(sx + 20, 26), (sx + 20, 34)], fill=(80, 80, 100)); d.line([(sx + 110, 26), (sx + 110, 34)], fill=(80, 80, 100))
    d.rectangle([sx, 34, sx + 132, 54], fill=(255, 204, 40), outline=OUT)
    text(img, '入境 ARRIVALS →', sx + 66, 44, (24, 20, 26), None, FONT_S, shadow=False)
    flap_board(img, d, 296 - ox * 0.4, 32, T, lt, [('LT404 23:55', AMB), ('ZZ118 00:20', AMB), ('MS099 LATE', AMB), ('NO SIGNAL', RED)])
    # 座椅
    chair_row(d, 10 - ox * 1.3, 9, 192); chair_row(d, 300 - ox * 1.3, 10, 192); chair_row(d, 560 - ox * 1.3, 8, 192)
    # 安检门
    gx = 360 - ox * 1.1
    passed = lt > 2.0
    d.rectangle([gx - 22, 132, gx - 18, 222], fill=(150, 150, 168)); d.rectangle([gx + 18, 132, gx + 22, 222], fill=(150, 150, 168))
    d.rectangle([gx - 22, 126, gx + 22, 133], fill=(170, 170, 186), outline=OUT)
    gc = (60, 230, 120) if passed else (255, 60, 60)
    d.rectangle([gx - 3, 128, gx + 3, 131], fill=gc); glow(img, gx, 130, 16, gc, 0.5)
    if 2.0 < lt < 2.6:
        r = (lt - 2.0) * 60
        d.ellipse([gx - r, 176 - r * 0.6, gx + r, 176 + r * 0.6], outline=lerpc((60, 230, 120), (56, 52, 80), (lt - 2.0) / 0.6))
    # 一颗心蹦蹦跳跳穿过安检门
    hx = lerp(150, 470, ease(span(lt, 0.4, 3.4)))
    hy = 200 - abs(math.sin(lt * 5)) * 18
    glow(img, hx, hy, 14, (255, 120, 150), 0.5)
    put(img, 'bigheart', hx, hy, 1)
    # 他
    person(img, 'boy', 86 - ox * 1.3, 232, view='side', pose='stand', expr='down', s=2)
    d.rounded_rectangle([108 - ox * 1.3, 206, 124 - ox * 1.3, 232], 2, fill=AMB_D, outline=OUT)
    d.rectangle([113 - ox * 1.3, 200, 119 - ox * 1.3, 206], outline=OUT)
    d.rectangle([110 - ox * 1.3, 216, 122 - ox * 1.3, 217], fill=AMB)


def s_novel(img, d, lt, dur, T, A):
    """深夜的书桌：手机里冒出来的谎话飘进本子变成一行行字，他接着往下写；最后本子合上成了一本书，冒出一个问号"""
    img.paste((26, 22, 46), (0, 0, W, 150))
    wx0, wy0, wx1, wy1 = 286, 16, 452, 128
    sky(img, ((0, (12, 10, 30)), (1, (60, 34, 92))), wy0, wy1)
    img.paste((26, 22, 46), (0, 0, wx0, 150)); img.paste((26, 22, 46), (wx1, 0, W, 150)); img.paste((26, 22, 46), (wx0, 0, wx1, wy0)); img.paste((26, 22, 46), (wx0, wy1, wx1, 150))
    city(img, d, wy1, 17, lt * 3, (36, 26, 66), (255, 206, 120), 20, 60, 0.35, T, 8, 18)
    img.paste((26, 22, 46), (0, 0, wx0, 150)); img.paste((26, 22, 46), (wx1, 0, W, 150))
    rain(d, T, wx0, wx1, wy0, wy1, 50, (110, 120, 170), 240, -2, 4)
    drops_on_glass(img, d, T, (wx0, wy0, wx1, wy1), 30)
    d.rectangle([wx0 - 4, wy0 - 4, wx1 + 4, wy1 + 4], outline=(60, 50, 80), width=3)
    d.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=(60, 50, 80), width=2)
    for x in range(20, 270, 28): d.line([(x, 0), (x, 150)], fill=(30, 26, 52))
    # 桌面
    d.rectangle([0, 150, W, 158], fill=(86, 56, 42)); d.rectangle([0, 158, W, H], fill=(112, 74, 54))
    for y in range(170, H, 16): d.line([(0, y), (W, y)], fill=(100, 64, 46))
    # 台灯
    d.ellipse([46, 160, 90, 170], fill=(60, 56, 80)); d.line([(68, 164), (84, 104)], fill=(80, 76, 100), width=3)
    d.line([(84, 104), (118, 80)], fill=(80, 76, 100), width=3)
    d.polygon([(108, 74), (132, 70), (140, 92), (118, 96)], fill=AMB_D, outline=OUT)
    tfill(img, 'polygon', [(122, 92), (140, 90), (300, 240), (110, 250)], (255, 220, 150), 0.16)
    glow(img, 210, 200, 130, (255, 210, 140), 0.25, 50)
    glow(img, 130, 90, 14, (255, 240, 200), 0.7)
    # 咖啡杯和纸团
    d.rectangle([350, 166, 366, 184], fill=(236, 232, 226), outline=OUT); d.arc([362, 170, 372, 180], 270, 90, fill=OUT)
    pix.pix_steam = None
    for i in range(3):
        f = (lt * 0.6 + i / 3) % 1
        tfill(img, 'ellipse', [356 + 3 * math.sin(lt * 2 + i * 2) - 2, 160 - f * 20 - 2, 356 + 3 * math.sin(lt * 2 + i * 2) + 2, 160 - f * 20 + 1],
              (240, 240, 250), 0.4 * math.sin(math.pi * f))
    for bx, by in ((396, 214), (420, 230), (440, 206)):
        d.ellipse([bx - 8, by - 7, bx + 8, by + 7], fill=(236, 232, 224), outline=OUT)
        d.line([(bx - 4, by - 2), (bx + 2, by + 1)], fill=(180, 176, 170)); d.line([(bx + 1, by - 4), (bx - 1, by + 3)], fill=(180, 176, 170))
    # 手机
    def scr(sc, sd, w, h):
        sd.rectangle([0, 0, w, h], fill=(30, 30, 46))
        for k in range(3):
            chat_bubble(sd, 3 if k % 2 else w - 3, 4 + k * 13, 22, 9, k % 2 == 0, k)
    phone(img, d, 48, 214, 30, 50, scr, rot=12)
    close = span(lt, dur - 1.25, dur - 0.75)
    # 本子
    bx0, bx1, by0, by1 = 150, 330, 170, 236
    mid = 240
    if close < 1:
        d.polygon([(bx0, by0 + 2), (mid, by0), (mid, by1), (bx0 - 4, by1 + 2)], fill=(250, 244, 226), outline=OUT)
        rw = (bx1 - mid) * math.cos(math.pi * close)
        if rw >= 0: d.polygon([(mid, by0), (mid + rw, by0 + 2), (mid + rw + 4 * (rw > 0), by1 + 2), (mid, by1)], fill=(250, 244, 226), outline=OUT)
        for k in range(8):
            y = by0 + 8 + k * 7
            d.line([(bx0 + 6, y), (mid - 6, y)], fill=(200, 210, 230))
            if rw > 20: d.line([(mid + 6, y), (mid + rw - 6, y)], fill=(200, 210, 230))
        d.line([(mid, by0), (mid, by1)], fill=(200, 190, 170))
        # 左页：飘过来的泡泡变成的字
        nl = int(lt / 0.42)
        for k in range(min(8, nl)):
            scribble(d, bx0 + 8, by0 + 7 + k * 7, mid - bx0 - 18, (90, 80, 110), 30 + k)
        for k in range(nl, nl + 2):
            u = (lt - k * 0.42 + 0.84) / 0.84
            if 0 < u < 1 and k < 8:
                sx_, sy_ = 60, 196
                tx, ty = bx0 + 40, by0 + 7 + k * 7
                x = lerp(sx_, tx, ease(u)); y = lerp(sy_, ty, ease(u)) - 50 * math.sin(math.pi * u)
                chat_bubble(d, x, y - 4, 20, 8, False, k, 1.0)
        # 右页：他正在写
        if rw > 30:
            wl = lt / 0.5
            for k in range(min(8, int(wl))):
                scribble(d, mid + 8, by0 + 7 + k * 7, min(rw - 18, 70), (60, 50, 90), 60 + k)
            k = int(wl)
            if k < 8:
                frac = wl - k
                px_, py_ = mid + 8 + frac * min(rw - 18, 70), by0 + 7 + k * 7
                scribble(d, mid + 8, py_, max(1, frac * min(rw - 18, 70)), (60, 50, 90), 60 + k)
                d.line([(px_, py_), (px_ + 12, py_ - 20)], fill=(30, 40, 90), width=3)
                d.line([(px_ + 8, py_ - 14), (px_ + 12, py_ - 20)], fill=AMB, width=2)
                d.line([(px_ + 22, py_ - 4), (px_ + 120, py_ + 70)], fill=OUT, width=20)
                d.line([(px_ + 22, py_ - 4), (px_ + 120, py_ + 70)], fill=AMB, width=16)
                d.line([(px_ + 26, py_ - 12), (px_ + 124, py_ + 62)], fill=AMB_L, width=2)
                d.line([(px_ + 20, py_ - 6), (px_ + 32, py_ + 3)], fill=AMB_D, width=16)
                d.ellipse([px_ + 2, py_ - 16, px_ + 22, py_ + 2], fill=SKIN, outline=OUT)
                d.line([(px_ + 6, py_ - 4), (px_ + 12, py_ - 1)], fill=SKIN_S)
    else:
        k = lt - (dur - 0.75)
        y0 = by0 - 6 * math.sin(min(1, k / 0.25) * math.pi)
        d.rectangle([bx0 + 2, y0, mid + 2, by1], fill=AMB_D, outline=OUT)
        d.rectangle([bx0 + 6, y0 + 4, mid - 2, by1 - 4], fill=AMB)
        d.rectangle([bx0 + 6, y0 + 4, bx0 + 10, by1 - 4], fill=AMB_D)
        put(img, 'bigheart', (bx0 + mid) / 2 + 4, y0 + 24, 1)
        text(img, '?', (bx0 + mid) / 2 + 4, y0 + 46, CREAM, OUT)
        c = bubble(img, d, mid + 20, by0 - 10, 24, 22, span(k, 0.15, 0.4), tail=(1, 1))
        if c: text(img, '?', c[0], c[1], (40, 30, 48), None, shadow=False)


@lru_cache(None)
def sketch_layers(scale=7):
    """他的大头像：彩色版本和描边（铅笔线）版本"""
    head = head_img('boy', 'young', 'neutral', 1)
    col = head.resize((16 * scale, 16 * scale), Image.NEAREST)
    a = np.array(col); al = a[..., 3] > 0
    rgb = a[..., :3].astype(int)
    key = rgb[..., 0] * 65536 + rgb[..., 1] * 256 + rgb[..., 2]
    key[~al] = -1
    edge = np.zeros_like(al)
    edge[:, 1:] |= key[:, 1:] != key[:, :-1]; edge[1:, :] |= key[1:, :] != key[:-1, :]
    hair = (rgb[..., 0] < 80) & al
    hatch = hair & (((np.arange(al.shape[1])[None, :] + np.arange(al.shape[0])[:, None]) % 6) == 0)
    ys, xs = np.nonzero(edge | hatch)
    cy, cx = al.shape[0] / 2, al.shape[1] / 2
    inner = (ys > al.shape[0] * 0.45) & (np.abs(xs - cx) < al.shape[1] * 0.38) & ~hatch[ys, xs]
    order = np.argsort(np.where(inner, 10, 0) + np.where(hatch[ys, xs], 5, 0) + (np.arctan2(ys - cy, xs - cx) + math.pi) / (2 * math.pi))
    return col, xs[order], ys[order]


def pencil(img, d, x, y):
    d.polygon([(x, y), (x + 5, y - 3), (x + 3, y - 6)], fill=(60, 60, 70))
    d.polygon([(x + 3, y - 6), (x + 5, y - 3), (x + 10, y - 8), (x + 8, y - 11)], fill=(240, 206, 160))
    d.polygon([(x + 8, y - 11), (x + 10, y - 8), (x + 54, y - 52), (x + 52, y - 55)], fill=(255, 206, 60))
    d.line([(x + 9, y - 10), (x + 53, y - 54)], fill=(255, 236, 140))
    d.polygon([(x + 52, y - 55), (x + 54, y - 52), (x + 58, y - 56), (x + 56, y - 59)], fill=(190, 190, 200))
    d.polygon([(x + 56, y - 59), (x + 58, y - 56), (x + 63, y - 61), (x + 61, y - 64)], fill=(255, 140, 160))


def paper(img, d, T, seed=3):
    img.paste((246, 238, 220), (0, 0, W, H))
    r = rng(seed)
    for _ in range(500): d.point((r.randrange(W), r.randrange(H)), fill=(232, 222, 202))
    for x in range(30, W, 30):
        d.ellipse([x - 5, 4, x + 5, 14], outline=(120, 120, 136), width=2)


def s_sketch(img, d, lt, dur, T, A):
    """素描本上，铅笔一笔一笔画出他的样子，画完上了色，画里的他眨眨眼，冒出一个问号"""
    paper(img, d, T)
    g = (96, 90, 104)
    for (x, y) in ((70, 60), (410, 200), (90, 210)): put(img, 'heart', x, y, 2, tint=(220, 150, 160))
    props.arrow(img, 400, 62, 2, 0.0, off=(170, 160, 170), glow_r=0)
    for k in range(4): scribble(d, 340, 110 + k * 8, 90, (190, 182, 186), 90 + k)
    col, xs, ys = sketch_layers(7)
    ox, oy = 240 - col.width // 2, 128 - col.height // 2
    n = len(xs)
    u = span(lt, 0.05, 1.9)
    m = int(n * u)
    if m: d.point(list(zip((xs[:m] + ox).tolist(), (ys[:m] + oy).tolist())), fill=g)
    if u > 0.55: d.arc([ox - 18, oy + col.height - 10, ox + col.width + 18, oy + col.height + 70], 200, 200 + 140 * span(u, 0.55, 0.9), fill=g, width=2)
    fill = span(lt, 1.95, 2.35)
    if fill > 0:
        a = np.array(col); m2 = (pix.bayer(col.height, col.width) < fill * 0.9) & (a[..., 3] > 0)
        a[~m2, 3] = 0
        if lt > 2.6 and lt % 1.2 < 0.15:
            a2 = np.array(head_img('boy', 'young', 'closed', 1).resize(col.size, Image.NEAREST)); a2[~m2, 3] = 0; a = a2
        im = Image.fromarray(a); img.paste(im, (ox, oy), im)
    if m and u < 1:
        pencil(img, d, int(xs[m - 1] + ox), int(ys[m - 1] + oy))
    else:
        pencil(img, d, 380 + int(4 * math.sin(lt * 3)), 230)
    c = bubble(img, d, ox + col.width + 4, oy + 30, 26, 24, span(lt, 2.4, 2.7), tail=(1, 1))
    if c: text(img, '?', c[0], c[1], (40, 30, 48), None, shadow=False, scale=1)
    if lt > 2.5: put(img, 'drop', ox + col.width - 6, oy + 26 + (lt - 2.5) * 10, 2)


def street_bg(img, d, T, lt, ground=200, off=0.0, lamps=(90, 390), wet=True):
    night_city(img, d, T, ground, off)
    d.rectangle([0, ground, W, H], fill=(40, 36, 60))
    for x in range(-int(off) % 24 - 24, W, 24): d.line([(x, ground), (x - 30, H)], fill=(34, 30, 52))
    for lx in lamps: lamp(img, d, lx - off % 600 if off else lx, ground, 1.0, 60)
    if wet: reflect(img, ground, H - ground, T, a=0.5)
    rain(d, T, 0, W, 0, H, 90, (90, 96, 150), 260, -3, 5)
    splashes(d, T, ground + 4, H, 18)


def s_tug(img, d, lt, dur, T, A):
    """雨夜街上两人背对背往两边走，手却还牵着，胳膊越拉越长，头上一颗心被扯得扁扁的"""
    street_bg(img, d, T, lt)
    tug = math.sin(lt * 5) * 3
    bx, gx_, fy = 196 + tug * 0.5, 284 + tug * 0.5, 230
    person(img, 'boy', bx, fy, view='side', pose='walk', ph=wph(lt, 7), expr='sad', arms='pull', s=2, flip=True)
    person(img, 'girl', gx_, fy, view='side', pose='walk', ph=wph(lt + 0.3, 7), expr='sad', arms='pull', s=2)
    hb = (bx + (pix.CX - (pix.CX - 7)) * 2, fy + (27 - 40) * 2)
    hg = (gx_ + (pix.CX - 7 - pix.CX) * 2, fy + (27 - 40) * 2)
    mx = 240 + tug; my = hb[1] + 1
    for (hx, hy), c in ((hb, AMB), (hg, SKIN)):
        d.line([(hx, hy), (mx, my)], fill=OUT, width=5); d.line([(hx, hy), (mx, my)], fill=c, width=3)
    d.rounded_rectangle([mx - 4, my - 4, mx + 4, my + 4], 2, fill=SKIN, outline=OUT)
    for k, (x, y) in enumerate(((bx - 14, fy - 2), (gx_ + 14, fy - 2))):
        f = (lt * 3 + k * 0.5) % 1
        d.point((x + (-1 if k == 0 else 1) * f * 10, y - f * 4), fill=(150, 140, 170))
    sq = 1 + 0.5 * (0.5 + 0.5 * math.sin(lt * 5))
    h = put_heart_stretch(img, mx, 150, sq)
    if lt > 1.6:
        for k in range(3):
            pix.put(img, 'drop', bx - 6 + k * 4, fy - 62 - (lt * 20 + k * 7) % 12, 1)


def put_heart_stretch(img, x, y, sx):
    im = pix.spr('bigheart', 2)
    im = im.resize((int(im.width * sx), int(im.height / max(1, sx * 0.8))), Image.NEAREST)
    paste(img, im, x, y, 1, 'cc')
    if sx > 1.35:
        d = ImageDraw.Draw(img)
        d.line([(x, y - im.height / 2 + 2), (x - 2, y), (x + 2, y + 3), (x, y + im.height / 2 - 2)], fill=(90, 30, 50))


def s_hands(img, d, lt, dur, T, A):
    """两只手的特写：他的手指扣住她的手。她往外抽了一点，他的手还紧紧拉着；背景是雨里的光斑和心跳线"""
    sky(img, ((0, (16, 12, 38)), (1, (44, 24, 70))))
    bokeh(img, T, 16, seed=3, a=0.28)
    # 心电图
    pts = []
    for x in range(0, W, 2):
        tx = T - (W - x) / 140
        b = last_beat(tx)
        k = tx - b
        v = 0
        if 0 <= k < 0.06: v = -18 * k / 0.06
        elif 0.06 <= k < 0.12: v = -18 + 30 * (k - 0.06) / 0.06
        elif 0.12 <= k < 0.18: v = 12 - 12 * (k - 0.12) / 0.06
        pts.append((x, 70 + v))
    d.line(pts, fill=(170, 60, 120), width=1)
    glow(img, W - 2, pts[-1][1], 10, PINK, 0.6)
    p = pix.pulse(T, 0.25)
    pull = 12 * ease(span(lt, 1.2, 2.8))
    HER, HER_S = (255, 228, 210), (238, 190, 170)
    def oshape(box, col, r=4):
        d.rounded_rectangle([box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1], r + 1, fill=OUT)
        d.rounded_rectangle(box, r, fill=col)
    # 她的胳膊、腕带和手背（从右边伸过来）
    ox = pull
    oshape([300 + ox, 126, 500, 176], HER, 8); d.line([(302 + ox, 170), (500, 170)], fill=HER_S)
    oshape([292 + ox, 122, 312 + ox, 180], (250, 250, 252), 2); d.rectangle([293 + ox, 146, 311 + ox, 154], fill=TEAL)
    oshape([250 + ox * 0.6, 116, 298 + ox, 184], HER, 12)
    # 他的袖子和手背（从左边伸过来）
    d.rectangle([-4, 116, 182, 190], fill=OUT); d.rectangle([-4, 118, 180, 188], fill=AMB)
    for x in range(20, 176, 34): d.line([(x, 122), (x + 10, 184)], fill=AMB_D)
    d.rectangle([164, 114, 188, 192], fill=OUT); d.rectangle([166, 116, 186, 190], fill=AMB_D)
    oshape([180, 114, 232, 186], SKIN, 12)
    for k in range(3): d.ellipse([214, 124 + k * 20, 220, 128 + k * 20], fill=SKIN_S)
    # 手指交错：他的手指往右搭在她手背上，她的手指往左搭在他手背上，指甲涂着青绿色
    grip = int(round(p * 2))
    for k in range(8):
        y = 116 + k * 8.6
        if k % 2 == 0:
            x0, x1 = 222, 284 + ox * 0.5 - grip
            oshape([x0, y, x1, y + 7], SKIN, 3)
            d.rectangle([x1 - 5, y + 2, x1 - 2, y + 4], fill=(255, 238, 230))
            d.line([(x1 - 12, y + 1), (x1 - 12, y + 6)], fill=SKIN_S)
        else:
            x0, x1 = 196 + ox * 0.3 + grip, 262 + ox * 0.6
            oshape([x0, y, x1, y + 7], HER, 3)
            d.rectangle([x0 + 2, y + 2, x0 + 5, y + 4], fill=TEAL)
            d.line([(x0 + 12, y + 1), (x0 + 12, y + 6)], fill=HER_S)
    # 他的拇指压在最上面
    oshape([206, 104, 250, 116], SKIN, 5); d.rectangle([243, 107, 246, 110], fill=(255, 238, 230))
    glow(img, 240, 150, 70 + 10 * p, (255, 170, 190), 0.1 + 0.16 * p)
    rain(d, T, 0, W, 0, H, 70, (140, 150, 210), 240, -2, 5)
    for i in range(10):                                         # 雨点打在手上
        r = rng(i * 5)
        per = 0.7 + r.random() * 0.5
        k = ((T + r.random() * per) % per) / per
        if k < 0.3:
            x = r.uniform(190, 300); y = 108 + r.uniform(0, 8)
            s = int(k * 14)
            d.point([(x - s, y - s * 0.6), (x + s, y - s * 0.6), (x, y - s)], fill=(190, 210, 255))


def bathroom_wall(img, d, x0, y0, x1, y1, col=(44, 62, 74), grout=(32, 46, 58)):
    d.rectangle([x0, y0, x1, y1], fill=col)
    for x in range(x0, x1, 14): d.line([(x, y0), (x, y1)], fill=grout)
    for y in range(y0, y1, 14): d.line([(x0, y), (x1, y)], fill=grout)


def s_mirror(img, d, lt, dur, T, A):
    """深夜的洗手间：镜子里的他先是一样的，然后画面开始故障，变成了一个阴着脸、红眼睛的他。他吓得往后一缩，镜子裂开"""
    flick = 1.0
    for a, b in ((0.6, 0.72), (0.8, 0.86), (2.2, 2.3), (3.3, 3.6)):
        if a < lt < b: flick = 0.35
    bathroom_wall(img, d, 0, 0, W, H)
    darken(img, 0.35 * (1 - flick) + 0.15)
    mx0, my0, mx1, my1 = 190, 24, 380, 194
    # 镜子里的世界
    mw, mh = mx1 - mx0, my1 - my0
    mi = Image.new('RGB', (mw, mh)); md = ImageDraw.Draw(mi)
    mi.paste((34, 48, 60), (0, 0, mw, mh))
    for x in range(0, mw, 14): md.line([(x, 0), (x, mh)], fill=(26, 38, 50))
    md.rectangle([14, 30, 60, mh], fill=(70, 56, 64)); md.rectangle([18, 34, 56, mh], fill=(84, 66, 74)); md.point((50, 100), fill=AMB)
    md.rectangle([120, 50, 150, 120], fill=(150, 170, 190)); md.rectangle([124, 54, 146, 116], fill=(170, 190, 210))
    evil = lt > 3.4
    gl = span(lt, 2.4, 3.6)
    if evil:
        pix.glow(mi, mw / 2 - 10, 110, 80, (150, 20, 60), 0.5) if False else None
        sub = Image.new('RGB', (W, H)); sub.paste(mi, (0, 0))
        glow(sub, mw / 2 - 10, 120, 80, (160, 30, 70), 0.45)
        mi = sub.crop((0, 0, mw, mh)); md = ImageDraw.Draw(mi)
    who_age = 'dark' if evil else 'young'
    bob = int(math.sin(lt * 2) > 0.7)
    big = pix.char_img('boy', who_age, 'front', 'stand', 0, 'sneer' if evil else ('sad' if lt > 1.6 else 'neutral'), 'down')
    big = big.resize((big.width * 4, big.height * 4), Image.NEAREST)
    mi.paste(big, (int(mw / 2 - 10 - pix.CX * 4), int(196 - pix.FY * 4 + bob)), big)
    if evil:
        for ex in (mw / 2 - 10 - 10, mw / 2 - 10 + 10): glow(mi, ex, 196 - pix.FY * 4 + 28 * 1 + 2 + bob + 4, 6, (255, 40, 60), 0.6)
    arr = np.array(mi)
    if 0 < gl < 1 or (evil and lt < 4.0):
        r = rng(int(T * 24))
        g2 = gl if gl < 1 else 1 - span(lt, 3.4, 4.0)
        for _ in range(int(14 * g2) + 2):
            y = r.randrange(mh); h = r.randint(2, 10); sh = r.randint(-12, 12)
            arr[y:y + h] = np.roll(arr[y:y + h], sh, axis=1)
        arr[..., 0] = np.roll(arr[..., 0], int(4 * g2), axis=1)
        arr[..., 2] = np.roll(arr[..., 2], -int(4 * g2), axis=1)
    arr = (arr.astype(float) * (0.55 + 0.45 * flick) * np.array([0.85, 0.95, 1.05])).clip(0, 255).astype(np.uint8)
    mi = Image.fromarray(arr)
    mask = Image.new('L', (mw, mh), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, mw - 1, mh - 1], 10, fill=255)
    img.paste(mi, (mx0, my0), mask)
    d.rounded_rectangle([mx0 - 4, my0 - 4, mx1 + 4, my1 + 4], 12, outline=(190, 196, 206), width=3)
    d.rounded_rectangle([mx0 - 5, my0 - 5, mx1 + 5, my1 + 5], 13, outline=OUT)
    for k in range(3): d.line([(mx0 + 10 + k * 6, my0 + 8), (mx0 + 4 + k * 6, my0 + 22)], fill=(150, 170, 190))
    # 镜子裂开
    crack = span(lt, 4.9, 5.6)
    if crack > 0:
        cx, cy = mx0 + 120, my0 + 66
        r = rng(9)
        for k in range(9):
            a = k * 2 * math.pi / 9 + r.uniform(-0.2, 0.2)
            L = r.uniform(50, 110) * ease(crack)
            pts = [(cx, cy)]
            for j in range(1, 5):
                pts.append((cx + math.cos(a + r.uniform(-0.25, 0.25)) * L * j / 4, cy + math.sin(a + r.uniform(-0.25, 0.25)) * L * j / 4))
            pts = [(clamp(x, mx0, mx1), clamp(y, my0, my1)) for x, y in pts]
            d.line(pts, fill=(230, 240, 250))
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], outline=(230, 240, 250))
        props.shake(img, lt - 4.9, 4, 0.3)
    # 灯管、洗手台
    d.rectangle([228, 8, 342, 13], fill=lerpc((90, 100, 110), (230, 255, 250), flick), outline=OUT)
    if flick > 0.5: glow(img, 285, 12, 90, (210, 255, 240), 0.25, 20)
    d.rectangle([150, 200, 430, 214], fill=(70, 84, 100), outline=OUT)
    d.ellipse([236, 196, 334, 212], fill=(236, 240, 246), outline=OUT); d.ellipse([250, 199, 320, 208], fill=(200, 210, 222))
    d.rectangle([282, 186, 288, 198], fill=(180, 186, 200), outline=OUT); d.rectangle([282, 186, 300, 190], fill=(180, 186, 200), outline=OUT)
    # 背对镜头的他
    jump = -8 * ease(span(lt, 3.45, 3.6)) * (1 - span(lt, 4.2, 4.8))
    person(img, 'boy', 120 + jump, 300 + jump * 0.3, view='back', pose='stand', s=4)
    if 3.45 < lt < 4.6:
        text(img, '!', 150 + jump, 160, (255, 255, 255), OUT, scale=2)
    vig(img, 0.5)


# ================================================================ 第一段副歌
def s_tally(img, d, lt, dur, T, A):
    """一面墙上用粉笔画满了“正”字一样的记号，越画越快，角上的计数一路跳到一千"""
    img.paste((32, 34, 50), (0, 0, W, H))
    for y in range(0, H, 9):
        off = 0 if (y // 9) % 2 else 9
        for x in range(-off, W, 18): d.rectangle([x, y, x + 17, y + 8], outline=(28, 30, 44))
    glow(img, 240, 120, 260, (90, 80, 140), 0.18, 160)
    total = int(1000 * span(lt, 0.0, 1.55) ** 1.6)
    cols = 20
    for i in range(total):
        g, st = divmod(i, 5)
        gc, gr = g % cols, g // cols
        x0 = 26 + gc * 22; y0 = 34 + gr * 19
        r = rng(i)
        col = AMB if i >= total - 6 else (232, 228, 214)
        if st < 4:
            x = x0 + st * 3 + r.randint(-1, 0)
            d.line([(x, y0 + r.randint(0, 1)), (x + r.randint(-1, 1), y0 + 13)], fill=col)
        else:
            d.line([(x0 - 2, y0 + 10), (x0 + 13, y0 + 2)], fill=col)
    done = total >= 1000
    d.rectangle([182, 4, 298, 28], fill=(18, 14, 30), outline=AMB if done else (80, 70, 110))
    text(img, '×' + str(total).rjust(4, '0'), 240, 16, AMB_L if done else (236, 230, 220), OUT)
    if total >= 1000:
        k = lt - 1.55
        props.shake(img, k, 3, 0.25)
        burst(img, d, k, 240, 16, life=0.8, scale=0.6)


def bus_img():
    im = Image.new('RGBA', (300, 70)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 4, 299, 62], 6, fill=(56, 96, 170))
    d.rectangle([0, 4, 299, 30], fill=(236, 236, 240))
    for k in range(9):
        x = 18 + k * 30
        d.rectangle([x, 9, x + 24, 27], fill=(255, 214, 140))
        if k % 3 != 1: d.ellipse([x + 8, 13, x + 15, 20], fill=(150, 110, 80)); d.rectangle([x + 6, 20, x + 17, 27], fill=(150, 110, 80))
    d.rectangle([286, 8, 298, 40], fill=(44, 64, 104))
    d.rectangle([250, 34, 270, 60], fill=(44, 64, 104))
    d.rectangle([4, 6, 40, 8], fill=AMB)
    for wx in (50, 240): d.ellipse([wx - 12, 50, wx + 12, 70], fill=(26, 24, 34)); d.ellipse([wx - 6, 56, wx + 6, 66], fill=(140, 140, 150))
    d.rectangle([292, 44, 299, 50], fill=(255, 250, 220))
    return outline(im, OUT)


BUS = None


def s_bus(img, d, lt, dur, T, A):
    """马路对面的她低着头；一辆公交车从中间呼啸而过，车开走以后，路灯下已经没有她了"""
    global BUS
    BUS = BUS or bus_img()
    night_city(img, d, T, 118, 0)
    d.rectangle([0, 104, W, 150], fill=(34, 28, 56))
    for k, (x, c) in enumerate(((40, (255, 120, 140)), (150, (120, 220, 255)), (380, (255, 210, 120)))):
        d.rectangle([x, 108, x + 70, 140], fill=lerpc(c, (30, 20, 40), 0.55)); d.rectangle([x + 4, 112, x + 66, 118], fill=c)
        glow(img, x + 35, 125, 40, c, 0.15)
    d.rectangle([0, 140, W, 150], fill=(70, 64, 92))
    lamp(img, d, 328, 150, 1.0, 52)
    gone = lt > 1.02
    if not gone or lt < 1.25:
        a = 1.0 if not gone else 1 - span(lt, 1.02, 1.25)
        person(img, 'girl', 318, 150, view='front', expr='sad', s=2, alpha=a)
    sx = 150
    d.rectangle([sx, 70, sx + 2, 150], fill=(60, 56, 80))
    d.rectangle([sx - 6, 70, sx + 8, 90], fill=(20, 18, 30), outline=OUT)
    d.rectangle([sx - 1, 74, sx + 2, 77], fill=RED); d.rectangle([sx - 2, 78, sx + 3, 84], fill=RED); glow(img, sx, 80, 10, RED, 0.4)
    d.rectangle([0, 150, W, 212], fill=(36, 34, 52))
    for y in range(156, 206, 10): d.rectangle([190, y, 290, y + 4], fill=(200, 200, 206))
    reflect(img, 150, 62, T, a=0.45, src_h=46)
    bx = lerp(-330, 800, span(lt, 0.42, 1.4))
    if -310 < bx < W + 10:
        for k in range(8):
            y = 160 + k * 6
            d.line([(bx - 40 - k * 9, y), (bx - 4, y)], fill=(90, 100, 150))
        paste(img, BUS, bx, 212, 1, 'lt' if False else 'cb')
        glow(img, bx + 150, 192, 22, (255, 250, 220), 0.5)
    d.rectangle([0, 212, W, H], fill=(48, 44, 66))
    person(img, 'boy', 170, 300, view='back', s=3)
    rain(d, T, 0, W, 0, H, 80, (100, 110, 160), 260, -3, 5)


def s_longing(img, d, lt, dur, T, A):
    """深夜的卧室，他坐在床边，椅背上还挂着她的球衣；脑袋上一个接一个冒出装着她的泡泡"""
    img.paste((36, 30, 62), (0, 0, W, H))
    for x in range(0, W, 22): d.line([(x, 0), (x, 190)], fill=(40, 34, 70))
    wx0, wy0, wx1, wy1 = 270, 26, 440, 140
    sky(img, ((0, (10, 8, 28)), (1, (58, 32, 90))), wy0, wy1)
    img.paste((36, 30, 62), (0, 0, wx0, wy1)); img.paste((36, 30, 62), (wx1, 0, W, wy1)); img.paste((36, 30, 62), (wx0, 0, wx1, wy0))
    city(img, d, wy1, 23, lt * 2, (30, 24, 60), (255, 206, 120), 20, 70, 0.35, T, 8, 20)
    img.paste((36, 30, 62), (0, 0, wx0, wy1)); img.paste((36, 30, 62), (wx1, 0, W, wy1))
    rain(d, T, wx0, wx1, wy0, wy1, 40, (110, 120, 170), 240, -2, 4)
    drops_on_glass(img, d, T, (wx0, wy0, wx1, wy1), 26, 4)
    d.rectangle([wx0 - 4, wy0 - 4, wx1 + 4, wy1 + 4], outline=(70, 60, 96), width=3)
    d.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=(70, 60, 96), width=2)
    d.polygon([(wx1 + 2, wy0 - 6), (wx1 + 26, wy0 - 6), (wx1 + 20, 190), (wx1 + 4, 190)], fill=(90, 60, 110))
    tfill(img, 'polygon', [(wx0, wy1), (wx1, wy1), (wx1 - 30, 230), (wx0 - 80, 230)], (150, 170, 255), 0.08)
    d.rectangle([0, 190, W, H], fill=(52, 40, 66))
    # 床
    d.rectangle([20, 176, 236, 214], fill=(70, 60, 100), outline=OUT)
    d.rectangle([20, 166, 236, 182], fill=(230, 226, 240), outline=OUT)
    d.rectangle([24, 156, 70, 170], fill=(250, 248, 255), outline=OUT)
    d.polygon([(100, 168), (236, 168), (236, 196), (90, 196)], fill=AMB_D, outline=OUT)
    # 挂着她球衣的椅子
    cx = 400
    d.rectangle([cx - 20, 150, cx - 17, 228], fill=(120, 80, 60), outline=OUT); d.rectangle([cx - 20, 196, cx + 22, 200], fill=(120, 80, 60), outline=OUT)
    d.rectangle([cx + 19, 196, cx + 22, 228], fill=(120, 80, 60))
    d.polygon([(cx - 30, 154), (cx - 22, 150), (cx - 12, 150), (cx - 4, 154), (cx - 6, 162), (cx - 8, 192), (cx - 28, 192), (cx - 30, 162)],
              fill=TEAL, outline=OUT)
    d.rectangle([cx - 28, 188, cx - 8, 191], fill=(255, 255, 255))
    text(img, '17', cx - 17, 172, (255, 255, 255), None, FONT_S, shadow=False)
    person(img, 'boy', 200, 214, view='side', pose='sit', expr='sad', s=2)
    # 泡泡
    bs = beats_in(T - lt - 0.01, T + 0.01)
    times = [T - lt + 0.05] + bs + [b + 0.45 for b in bs]
    for i, tb in enumerate(sorted(times)):
        k = T - tb
        if k < 0 or k > 2.2: continue
        r = rng(i * 3)
        x = 214 + k * r.uniform(-40, 30) + 6 * math.sin(k * 3 + i)
        y = 150 - k * 52
        a = 1 - span(k, 1.6, 2.2)
        sc = eback(min(1, k / 0.3))
        rr = 14 * sc
        tfill(img, 'ellipse', [x - rr - 1, y - rr * 0.85 - 1, x + rr + 1, y + rr * 0.85 + 1], OUT, a)
        tfill(img, 'ellipse', [x - rr, y - rr * 0.85, x + rr, y + rr * 0.85], (255, 252, 246), a)
        if sc > 0.7: paste(img, head_img('girl', 'young', 'smile' if i % 2 else 'happy', 1), x, y + 1, a, 'cc')
    vig(img, 0.4)


def crt(img, d, box, frame, T, mode, label):
    """老电视：frame 是要放进屏幕的画面"""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    src = frame.crop((60, 0, 420, 270)).resize((w, h), Image.BOX)
    a = np.array(src).astype(float)
    a[::2] *= 0.78
    r = rng(int(T * 30))
    if mode == 'rew':
        for _ in range(6):
            y = r.randrange(h); hh = r.randint(1, 4)
            a[y:y + hh] = np.roll(a[y:y + hh], r.randint(-30, 30), axis=1) * 0.6 + 90
        band = int((T * 140) % (h + 20)) - 10
        a[max(0, band):max(0, band + 6)] = a[max(0, band):max(0, band + 6)] * 0.4 + 140
    a = a * np.array([0.95, 1.0, 1.08])
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    mask = Image.new('L', (w, h), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], 12, fill=255)
    img.paste(im, (x0, y0), mask)
    text(img, label, x0 + 30, y0 + 12, (255, 255, 255), (20, 20, 40), FONT_S)


def s_rewind(img, d, lt, dur, T, A):
    """老电视里一遍遍倒带、重放刚才那一幕：公交车开过，她不见了"""
    img.paste((14, 10, 26), (0, 0, W, H))
    d.rectangle([0, 200, W, H], fill=(24, 18, 36))
    d.rectangle([110, 196, 370, 230], fill=(70, 50, 44), outline=OUT); d.rectangle([116, 204, 364, 222], fill=(56, 40, 36))
    tx0, ty0, tx1, ty1 = 140, 44, 340, 198
    glow(img, 230, 120, 220, (130, 170, 255), 0.22, 140)
    d.line([(220, 44), (190, 12)], fill=(150, 150, 160), width=2); d.line([(250, 44), (290, 10)], fill=(150, 150, 160), width=2)
    d.rounded_rectangle([tx0, ty0, tx1, ty1], 14, fill=(176, 166, 150), outline=OUT)
    d.rounded_rectangle([tx0 + 6, ty0 + 6, tx1 - 6, ty1 - 6], 12, fill=(150, 140, 126))
    rew = lt < 0.6
    ts = (47.8 - (lt / 0.6) * 1.55) if rew else (46.25 + (lt - 0.6) * 1.5)
    frame = props.SNAP(ts) if props.SNAP else Image.new('RGB', (W, H))
    crt(img, d, (tx0 + 14, ty0 + 14, tx1 - 46, ty1 - 14), frame, T, 'rew' if rew else 'play', '◀◀ REW' if rew else '▶ PLAY')
    for k in range(2): d.ellipse([tx1 - 36, ty0 + 24 + k * 30, tx1 - 16, ty0 + 44 + k * 30], fill=(110, 100, 90), outline=OUT)
    for k in range(5): d.line([(tx1 - 36, ty0 + 96 + k * 8), (tx1 - 16, ty0 + 96 + k * 8)], fill=(110, 100, 90))
    person(img, 'boy', 240, 268, view='back', pose='sit', s=3, tint=(10, 8, 18))
    if not rew:
        u = (lt - 0.6) / 0.9
        if int(T * 4) % 2: text(img, 'REPLAY ×∞', 400, 40, AMB_L, OUT, FONT_S)


def s_globe(img, d, lt, dur, T, A):
    """她抱着一个水晶球跑开；他身后的整座城市一栋一栋被吸进了球里，四周越来越黑"""
    sky(img, NIGHT, 0, 226)
    pix.stars(d, T, 150, 0.9, 140)
    city(img, d, 212, 3, 0, (40, 30, 76), (150, 120, 190), 60, 150, 0.3, T, 12, 24)
    city(img, d, 220, 7, 0, (28, 20, 56), (255, 210, 120), 40, 120, 0.42, T)
    sweep = lerp(-20, W + 20, ease(span(lt, 0.15, 1.9)))
    if sweep > 0:
        img.paste(vgrad(W, 226, tuple((p, tuple(c)) for p, c in NIGHT), 5).crop((0, 0, int(sweep), 226)), (0, 0))
        darken(img, 0.0)
    gxp = lerp(330, 420, span(lt, 0, dur))
    gy = 186
    absorbed = 0
    for i in range(170):
        r = rng(i * 11)
        ox, oy = r.uniform(0, W), r.uniform(70, 210)
        te = 0.15 + 1.75 * ease_inv((ox + 20) / (W + 40))
        u = (lt - te) / 0.6
        if u >= 1: absorbed += 1
        if not 0 <= u < 1: continue
        e = ease(u)
        cxm, cym = (ox + gxp) / 2, min(oy, gy) - 60
        x = (1 - e) ** 2 * ox + 2 * (1 - e) * e * cxm + e * e * (gxp + 12)
        y = (1 - e) ** 2 * oy + 2 * (1 - e) * e * cym + e * e * (gy - 26)
        d.rectangle([x, y, x + 1, y + 1], fill=(255, 214, 130) if i % 3 else (255, 255, 230))
    d.rectangle([0, 226, W, H], fill=(36, 32, 54))
    lamp(img, d, 250, 226, 1 - span(lt, 0.9, 1.1), 60)
    darken(img, 0.35 * span(lt, 0.3, 2.0))
    person(img, 'boy', 140, 240, view='side', pose='stand', expr='surprised', arms='reach', s=2)
    person(img, 'girl', gxp, 240, view='side', pose='run', ph=wph(lt, 10), expr='smile', s=2)
    gcx, gcy = gxp + 14, gy - 22
    glow(img, gcx, gcy, 30 + absorbed * 0.15, (255, 210, 140), 0.3 + absorbed / 400)
    d.ellipse([gcx - 13, gcy - 13, gcx + 13, gcy + 13], fill=(30, 28, 60), outline=(220, 236, 255))
    mini = int(absorbed / 170 * 8)
    for k in range(mini):
        hh = 3 + (k * 7) % 9
        d.rectangle([gcx - 10 + k * 3, gcy + 8 - hh, gcx - 8 + k * 3, gcy + 8], fill=(60, 50, 100))
        d.point((gcx - 9 + k * 3, gcy + 6 - hh // 2), fill=(255, 214, 130))
    d.arc([gcx - 10, gcy - 10, gcx + 6, gcy + 6], 200, 250, fill=(255, 255, 255))
    d.rectangle([gcx - 10, gcy + 12, gcx + 10, gcy + 17], fill=(120, 80, 60), outline=OUT)
    vig(img, 0.5)


def ease_inv(f):
    return clamp(f)


@lru_cache(None)
def court_photo(w=150, h=100):
    """他们俩在黄昏的球场上的合照"""
    im = Image.new('RGB', (w, h)); d = ImageDraw.Draw(im)
    st = ((0, (255, 140, 120)), (0.6, (255, 196, 140)), (1, (255, 226, 170)))
    im.paste(vgrad(w, 70, st, 4), (0, 0))
    d.ellipse([100, 40, 130, 70], fill=(255, 244, 200))
    d.rectangle([0, 52, w, 70], fill=(200, 110, 110))
    for x in range(0, w, 12): d.rectangle([x, 46 + (x * 7) % 9, x + 9, 70], fill=(190, 104, 112))
    d.rectangle([0, 70, w, h], fill=(90, 140, 150))
    d.line([(0, 80), (w, 76)], fill=(240, 240, 240)); d.arc([30, 70, 120, 110], 180, 360, fill=(240, 240, 240))
    d.rectangle([130, 20, 132, 76], fill=(80, 80, 90)); d.rectangle([118, 16, 144, 30], fill=(250, 250, 250), outline=(80, 80, 90))
    d.rectangle([124, 30, 138, 31], fill=(240, 80, 60)); d.line([(125, 31), (128, 38), (131, 31), (134, 38), (137, 31)], fill=(250, 250, 250))
    person(im, 'boy', 54, 92, view='front', expr='laugh', arms='wave', s=2) if False else None
    for who, x, expr, arms in (('boy', 52, 'laugh', 'wave'), ('girl', 88, 'happy', 'down')):
        c = pix.char_img(who, 'young', 'front', 'stand', 1, expr, arms).resize((60, 84), Image.NEAREST)
        im.paste(c, (x - 30, 96 - 80), c)
    d.ellipse([92, 66, 102, 76], fill=(240, 130, 50), outline=(100, 50, 30)); d.line([(92, 71), (102, 71)], fill=(100, 50, 30))
    return im


@lru_cache(None)
def polaroid_img(w=150, h=100):
    ph = court_photo(w, h)
    im = Image.new('RGBA', (w + 10, h + 26), CREAM + (255,))
    im.paste(ph, (5, 5))
    dd = ImageDraw.Draw(im)
    pix_heart = pix.spr('heart', 1, tint=(240, 90, 120))
    im.paste(pix_heart, (w - 6, h + 12), pix_heart)
    dd.line([(14, h + 15), (60, h + 15)], fill=(150, 140, 150))
    return outline(im, OUT)


def tear_x(y, w):
    return w / 2 + 3 * (1 if (y // 5) % 2 else -1) + 2 * math.sin(y * 0.5)


def s_photo(img, d, lt, dur, T, A):
    """他拿着一张两人在球场的合照，想还给她又不知道怎么还；“算了”，照片从中间撕开，有她的那一半飘走了"""
    sky(img, ((0, (14, 10, 34)), (1, (50, 28, 76))))
    bokeh(img, T, 18, seed=8, a=0.3)
    rain(d, T, 0, W, 0, H, 60, (100, 110, 170), 230, -2, 5)
    pol = polaroid_img()
    pw, ph = pol.size
    cx, cy = 240, 118 + 2 * math.sin(lt * 1.5)
    t_tear0, t_tear1 = 1.6, 2.35
    p = span(lt, t_tear0, t_tear1)
    a = np.array(pol)
    xs = np.arange(pw)[None, :]
    tx = np.array([tear_x(y, pw) for y in range(ph)])[:, None]
    lm = xs < tx
    left = a.copy(); left[~lm] = 0
    right = a.copy(); right[lm] = 0
    yf = p * ph
    torn = (np.arange(ph) < yf)[:, None]
    for half in (left, right):                                   # 撕开的地方露出纸芯的白边
        m = half[..., 3] > 0
        e = m & ~(np.roll(m, 1, 1) & np.roll(m, -1, 1))
        half[e & (np.abs(xs - tx) < 2) & torn] = (220, 210, 196, 255)
    def opened(half, sgn):
        out = np.zeros((ph, pw + 40, 4), np.uint8)
        for y in range(ph):
            g = int(max(0, yf - y) * 0.12) if p < 1 else int(ph * 0.12 * 0 + (yf - y) * 0.12 if yf - y > 0 else 0)
            out[y, 20 + sgn * g:20 + sgn * g + pw] = half[y]
        return Image.fromarray(out)
    L = opened(left, -1); R = opened(right, 1)
    k = max(0.0, lt - t_tear1)
    paste(img, L, cx - 4 * ease(min(1, k)), cy, 1, 'cc')
    if k < 2.2:
        rx = cx + 120 * ein(min(1, k / 2.0)) + 10 * k
        ry = cy - 70 * ease(min(1, k / 2.0))
        Rr = R.rotate(-25 * ease(min(1, k / 1.6)), resample=Image.NEAREST, expand=True)
        sc = 1 - 0.55 * ease(min(1, k / 2.0))
        Rr = Rr.resize((max(1, int(Rr.width * sc)), max(1, int(Rr.height * sc))), Image.NEAREST)
        al = 1 - span(k, 1.5, 2.2)
        paste(img, Rr, rx, ry, al, 'cc')
        if k > 0.6:
            for j in range(6):
                twinkle(d, int(rx + math.cos(j + k * 3) * 30), int(ry + math.sin(j * 2 + k * 2) * 20), ((k * 1.5 + j / 6) % 1), (255, 240, 200), 3)
    # 他的两只手（右手在撕完以后垂下去）
    for side in (-1, 1):
        drop = 0 if side < 0 else 90 * ein(span(lt, t_tear1 + 0.3, t_tear1 + 1.0))
        out_ = side * 10 * p
        hx = cx + side * (pw / 2 - 6) + out_ - (4 * ease(min(1, k)) if side < 0 else 0)
        hy = cy + ph / 2 - 6 + drop
        d.rectangle([hx - 12, hy + 6, hx + 12, H + 10], fill=OUT); d.rectangle([hx - 10, hy + 8, hx + 10, H + 10], fill=AMB)
        d.rounded_rectangle([hx - 9, hy - 8, hx + 9, hy + 12], 5, fill=OUT); d.rounded_rectangle([hx - 8, hy - 7, hx + 8, hy + 11], 4, fill=SKIN)
        d.rounded_rectangle([hx - 4 - side * 2, hy - 14, hx + 4 - side * 2, hy - 2], 3, fill=OUT); d.rounded_rectangle([hx - 3 - side * 2, hy - 13, hx + 3 - side * 2, hy - 3], 2, fill=SKIN)
    if lt < t_tear0:
        c = bubble(img, d, 380, 70, 26, 22, span(lt, 0.3, 0.6), thought=True, tail=(-1, 1))
        if c: text(img, '?', c[0], c[1], (40, 30, 48), None, shadow=False)
    if t_tear0 <= lt < t_tear1 + 0.1:
        props.shake(img, lt - t_tear0, 2, t_tear1 - t_tear0)


def dialog(img, d, x, y, w, h, title_, body, buttons=('确定',), pressed=-1, big=False, title_col=(40, 60, 160)):
    d.rectangle([x, y, x + w, y + h], fill=(196, 196, 204))
    d.line([(x, y), (x + w, y)], fill=(255, 255, 255)); d.line([(x, y), (x, y + h)], fill=(255, 255, 255))
    d.line([(x + w, y), (x + w, y + h)], fill=(70, 70, 80)); d.line([(x, y + h), (x + w, y + h)], fill=(70, 70, 80))
    d.rectangle([x + 2, y + 2, x + w - 2, y + 14], fill=title_col)
    d.rectangle([x + w // 2, y + 2, x + w - 2, y + 14], fill=lerpc(title_col, (255, 255, 255), 0.25))
    d.text((x + 5, y + 1), title_, font=FONT_S, fill=(255, 255, 255))
    d.rectangle([x + w - 13, y + 4, x + w - 4, y + 12], fill=(196, 196, 204)); d.line([(x + w - 11, y + 5), (x + w - 6, y + 11)], fill=(0, 0, 0)); d.line([(x + w - 6, y + 5), (x + w - 11, y + 11)], fill=(0, 0, 0))
    r = 8 if not big else 11
    ix, iy = x + 8 + r, y + 18 + r
    d.ellipse([ix - r, iy - r, ix + r, iy + r], fill=(220, 40, 40), outline=(120, 10, 10))
    d.line([(ix - r / 2.5, iy - r / 2.5), (ix + r / 2.5, iy + r / 2.5)], fill=(255, 255, 255), width=2)
    d.line([(ix + r / 2.5, iy - r / 2.5), (ix - r / 2.5, iy + r / 2.5)], fill=(255, 255, 255), width=2)
    d.text((ix + r + 6, iy - 7), body, font=FONT_S if not big else FONT, fill=(0, 0, 0))
    bw = 34 if not big else 50
    for i, b in enumerate(buttons):
        bx = x + w / 2 - (len(buttons) * (bw + 8) - 8) / 2 + i * (bw + 8); by = y + h - (16 if not big else 22)
        bh = 12 if not big else 16
        pr = i == pressed
        d.rectangle([bx, by, bx + bw, by + bh], fill=(196, 196, 204), outline=(0, 0, 0))
        d.line([(bx + 1, by + 1), (bx + bw - 1, by + 1)], fill=(120, 120, 130) if pr else (255, 255, 255))
        d.text((bx + bw / 2 - FONT_S.getlength(b) / 2 + (1 if pr else 0), by + (1 if not big else 3) + (1 if pr else 0) - 1), b, font=FONT_S, fill=(0, 0, 0))
        if i == 0: d.rectangle([bx + 2, by + 2, bx + bw - 2, by + bh - 2], outline=(80, 80, 90))
    return


def cursor(d, x, y, pressed=False):
    pts = [(0, 0), (0, 13), (3, 10), (6, 16), (8, 15), (5, 9), (9, 9)]
    d.polygon([(x + a, y + b) for a, b in pts], fill=(255, 255, 255), outline=(0, 0, 0))


def desktop(img, d, T):
    img.paste((40, 112, 124), (0, 0, W, H))
    for y in range(0, H, 2):
        for x in range((y // 2) % 2, W, 4): d.point((x, y), fill=(36, 104, 116))
    for i, (x, y) in enumerate(((22, 20), (22, 62), (22, 104))):
        if i < 2:
            d.rectangle([x - 10, y - 6, x + 10, y + 8], fill=(240, 200, 80), outline=OUT); d.rectangle([x - 10, y - 9, x - 2, y - 6], fill=(240, 200, 80), outline=OUT)
        else:
            d.rectangle([x - 8, y - 8, x + 8, y + 10], fill=(200, 210, 220), outline=OUT); d.line([(x - 5, y - 4), (x - 5, y + 7)], fill=(120, 130, 140)); d.line([(x, y - 4), (x, y + 7)], fill=(120, 130, 140)); d.line([(x + 5, y - 4), (x + 5, y + 7)], fill=(120, 130, 140))
        d.rectangle([x - 14, y + 13, x + 14, y + 15], fill=(255, 255, 255))
    d.rectangle([0, 258, W, H], fill=(196, 196, 204)); d.line([(0, 258), (W, 258)], fill=(255, 255, 255))
    d.rectangle([3, 260, 40, 268], fill=(196, 196, 204), outline=(0, 0, 0))
    props.arrow(img, 21, 264, 1, blink_a(T), glow_r=0)
    d.rectangle([430, 260, 476, 268], outline=(120, 120, 130))
    d.text((436, 257), '23:59', font=FONT_S, fill=(0, 0, 0))


def s_errors(img, d, lt, dur, T, A):
    """复古电脑桌面：报错窗口一个叠一个，数到一千；最后跳出一个大窗口“再来一次？”，两个按钮都是“是”，光标点了下去"""
    desktop(img, d, T)
    N = 46
    t_end = 2.05
    for i in range(N):
        ti = t_end * (i / N) ** 0.55
        if lt < ti: break
        x = 60 + (i * 14) % 260; y = 20 + (i * 9) % 150 + (i // 18) * 4
        n = int(1000 * (i + 1) / N)
        dialog(img, d, x, y, 150, 58, '错误', f'第 {n} 次', ('确定',))
    if lt > 2.15:
        darken(img, 0.35 * span(lt, 2.15, 2.4))
        f = span(lt, 2.15, 2.5)
        if f > 0:
            s = eback(f)
            w, h = int(250 * s), int(110 * s)
            if w > 40 and h > 30:
                clicked = lt > 3.05
                cnt = '×1001' if clicked else '×1000'
                dialog(img, d, 240 - w // 2, 120 - h // 2, w, h, '错误 ' + cnt, '再来一次？', ('是', '是'), 0 if 3.0 < lt < 3.15 else -1, big=True,
                       title_col=(170, 30, 40))
        cx = lerp(430, 196, ease(span(lt, 2.4, 2.95))); cy = lerp(240, 156, ease(span(lt, 2.4, 2.95)))
        cursor(d, cx, cy)
        if lt > 3.05:
            k = lt - 3.05
            burst(img, d, k, 240, 120, life=1.0, scale=0.9)
            props.shake(img, k, 4, 0.3)
            for j in range(int(k / 0.08)):
                dialog(img, d, 30 + (j * 37) % 330, 16 + (j * 23) % 160, 150, 58, '错误', '第 1001 次', ('确定',))


def project(X, Z, hc=34, yh=104, f=260):
    return 240 + X * f / Z, yh + hc * f / Z


def s_parallel(img, d, lt, dur, T, A):
    """霓虹网格的大地上两条平行线，一条琥珀色是他，一条青绿色是她，本来永远不会相交；然后它们弯过来，拧成一股，交点上一下下爆出火花"""
    sky(img, ((0, (8, 4, 24)), (0.7, (50, 20, 80)), (1, (150, 50, 120))), 0, 105)
    pix.stars(d, T, 80, 1.0, 150)
    sx, sy, sr = 240, 92, 46
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 120, 100))
    for k in range(sr * 2):
        yy = sy - sr + k
        c = lerpc((255, 220, 120), (255, 70, 140), k / (sr * 2))
        hw = math.sqrt(max(0, sr * sr - (yy - sy) ** 2))
        if yy > sy - 4 and (yy - sy) % 6 < 2 + (yy - sy) // 10: continue
        d.line([(sx - hw, yy), (sx + hw, yy)], fill=c)
    glow(img, sx, sy, 110, (255, 90, 150), 0.3)
    for i, (base, amp, fr, ph, col) in enumerate(((104, 14, 0.04, 1, (60, 24, 90)), (104, 8, 0.07, 4, (40, 16, 64)))):
        for x in range(W):
            if abs(x - 240) < 60 and i == 0: continue
            y = base - abs(amp * math.sin(x * fr + ph)) - (abs(x - 240) > 60) * 4
            d.line([(x, y), (x, base)], fill=col)
    d.rectangle([0, 104, W, H], fill=(16, 6, 30))
    for X in range(-400, 401, 40):
        p0 = project(X, 6); p1 = project(X, 900)
        d.line([p0, p1], fill=(110, 30, 110))
    off = (T * 90) % 30
    for k in range(30):
        Z = 6 + k * 30 - off
        if Z < 6: continue
        _, y = project(0, Z)
        d.line([(0, y), (W, y)], fill=lerpc((110, 30, 110), (16, 6, 30), min(1, Z / 700)))
    b = ease(span(lt, 1.7, 2.6))
    def X_of(Z, sgn):
        return sgn * 14 - sgn * b * 30 * math.sin(Z * 0.035 - T * 3)
    Zs = np.geomspace(5, 1200, 160)
    for sgn, col in ((-1, AMB), (1, TEAL)):
        pts = [project(X_of(Z, sgn), Z) for Z in Zs]
        d.line(pts, fill=lerpc(col, (255, 255, 255), 0.4), width=3)
        d.line(pts, fill=col, width=1)
        for k in range(3):
            Zp = 5 + ((T * 110 + k * 240) % 700)
            x, y = project(X_of(Zp, sgn), Zp)
            glow(img, x, y, 10, col, 0.7); d.rectangle([x - 1, y - 1, x + 1, y + 1], fill=(255, 255, 255))
    if b > 0.3:
        for j in range(len(Zs) - 1):
            Za, Zb = Zs[j], Zs[j + 1]
            da = X_of(Za, -1) - X_of(Za, 1); db = X_of(Zb, -1) - X_of(Zb, 1)
            if da * db < 0 and Za < 300:
                x, y = project(X_of(Za, 1), Za)
                pp = pix.pulse(T, 0.4)
                glow(img, x, y, 20 + 30 / Za * 20, (255, 255, 230), 0.6 * b)
                twinkle(d, int(x), int(y), 0.5 + 0.3 * pp, (255, 255, 255), 5)
                if Za < 40: put(img, 'heart', x, y - 12, 2)
    # 左上角的符号：∥ 变成 ×
    if b < 0.5:
        d.line([(30, 30), (24, 48)], fill=(230, 230, 240), width=2); d.line([(38, 30), (32, 48)], fill=(230, 230, 240), width=2)
    else:
        d.line([(24, 30), (40, 48)], fill=AMB_L, width=2); d.line([(40, 30), (24, 48)], fill=TEAL_L, width=2)


# ---------------------------------------------------------------- 俯视的十字路口
WORLD_W = 1200


def umbrella_top(d, x, y, r, col):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col, outline=OUT)
    for a in range(0, 360, 60):
        d.line([(x, y), (x + math.cos(math.radians(a)) * r, y + math.sin(math.radians(a)) * r)], fill=lerpc(col, (0, 0, 0), 0.25))
    d.point((x, y), fill=(255, 255, 255))


def tree_top(d, x, y, r=10):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(30, 70, 60), outline=OUT)
    d.ellipse([x - r + 3, y - r + 2, x + 2, y + 1], fill=(48, 100, 80))


WORLD_H, CAMY = 340, 50


@lru_cache(None)
def topdown_base():
    """俯视的城区底图（不含灯光和雨），1200×340；镜头往下偏 CAMY，让停在路口的车落在字幕上方"""
    H = WORLD_H
    im = Image.new('RGB', (WORLD_W, H)); d = ImageDraw.Draw(im)
    im.paste((40, 38, 54), (0, 0, WORLD_W, H))
    r = rng(4)
    for _ in range(2500): d.point((r.randrange(WORLD_W), r.randrange(H)), fill=(46, 44, 60))
    rx0, rx1, ry0, ry1 = 180, 300, 70, 190
    blocks = [(0, 0, rx0 - 14, ry0 - 14), (rx1 + 14, 0, WORLD_W, ry0 - 14), (0, ry1 + 14, rx0 - 14, H), (rx1 + 14, ry1 + 14, WORLD_W, H)]
    for bi, (x0, y0, x1, y1) in enumerate(blocks):
        d.rectangle([x0 - 14 if x0 else x0, y0 - 14 if y0 else y0, x1 + 14, y1 + 14], fill=(86, 84, 102))
        for x in range(int(x0) - 14, int(x1) + 14, 8): d.line([(x, y0 - 14), (x, y1 + 14)], fill=(78, 76, 94))
        d.rectangle([x0 - 14 if x0 else x0, y0 - 14 if y0 else y0, x1 + 14, y1 + 14], outline=(120, 118, 136))
        x = x0 + 4
        while x < x1 - 20:
            bw = r.randint(50, 110); bw = min(bw, int(x1 - x - 4))
            if bw < 30: break
            by0, by1 = y0 + 4, y1 - 4
            col = r.choice([(54, 50, 74), (62, 54, 70), (48, 56, 72), (70, 60, 64)])
            d.rectangle([x, by0, x + bw, by1], fill=col, outline=OUT)
            d.rectangle([x + 2, by0 + 2, x + bw - 2, by0 + 4], fill=lerpc(col, (255, 255, 255), 0.12))
            for _ in range(r.randint(1, 4)):
                ax, ay = r.uniform(x + 6, x + bw - 14), r.uniform(by0 + 6, max(by0 + 7, by1 - 14))
                d.rectangle([ax, ay, ax + 8, ay + 6], fill=(150, 150, 166), outline=OUT); d.line([(ax + 2, ay + 3), (ax + 6, ay + 3)], fill=(110, 110, 120))
            if r.random() < 0.5:
                sx_, sy_ = r.uniform(x + 6, x + bw - 20), r.uniform(by0 + 6, max(by0 + 7, by1 - 16))
                d.rectangle([sx_, sy_, sx_ + 14, sy_ + 10], fill=(255, 214, 140), outline=OUT)
            if r.random() < 0.3:
                ex, ey = r.uniform(x + 10, x + bw - 10), r.uniform(by0 + 10, max(by0 + 11, by1 - 10))
                d.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=(110, 110, 130), outline=OUT)
            x += bw + r.randint(4, 10)
    # 一栋楼顶上有个篮球场
    d.rectangle([60, 206, 160, 262], fill=(60, 150, 140), outline=OUT)
    d.rectangle([64, 210, 156, 258], outline=(240, 240, 240)); d.line([(110, 210), (110, 258)], fill=(240, 240, 240)); d.ellipse([102, 226, 118, 242], outline=(240, 240, 240))
    # 马路
    d.rectangle([rx0, 0, rx1, H], fill=(36, 34, 46)); d.rectangle([0, ry0, WORLD_W, ry1], fill=(36, 34, 46))
    for y in list(range(0, ry0 - 16, 14)) + list(range(ry1 + 18, H, 14)):
        d.rectangle([209, y, 210, y + 7], fill=(200, 200, 196)); d.rectangle([269, y, 270, y + 7], fill=(200, 200, 196))
    d.rectangle([238, 0, 239, ry0 - 16], fill=(240, 196, 60)); d.rectangle([241, 0, 242, ry0 - 16], fill=(240, 196, 60))
    d.rectangle([238, ry1 + 18, 239, H], fill=(240, 196, 60)); d.rectangle([241, ry1 + 18, 242, H], fill=(240, 196, 60))
    for x in list(range(0, rx0 - 16, 14)) + list(range(rx1 + 18, WORLD_W, 14)):
        d.rectangle([x, 99, x + 7, 100], fill=(200, 200, 196)); d.rectangle([x, 159, x + 7, 160], fill=(200, 200, 196))
    d.rectangle([0, 128, rx0 - 16, 129], fill=(240, 196, 60)); d.rectangle([0, 131, rx0 - 16, 132], fill=(240, 196, 60))
    d.rectangle([rx1 + 18, 128, WORLD_W, 129], fill=(240, 196, 60)); d.rectangle([rx1 + 18, 131, WORLD_W, 132], fill=(240, 196, 60))
    # 斑马线和停车线
    for x in range(rx0 + 4, rx1 - 4, 9):
        d.rectangle([x, ry1 + 4, x + 5, ry1 + 14], fill=(220, 220, 214)); d.rectangle([x, ry0 - 14, x + 5, ry0 - 4], fill=(220, 220, 214))
    for y in range(ry0 + 4, ry1 - 4, 9):
        d.rectangle([rx0 - 14, y, rx0 - 4, y + 5], fill=(220, 220, 214)); d.rectangle([rx1 + 4, y, rx1 + 14, y + 5], fill=(220, 220, 214))
    d.rectangle([241, ry1 + 16, rx1, ry1 + 17], fill=(240, 240, 236))
    # 左转车道上的箭头
    ax, ay = 255, 236
    d.rectangle([ax - 1, ay - 4, ax + 1, ay + 14], fill=(220, 220, 214))
    d.line([(ax, ay - 4), (ax - 8, ay - 4)], fill=(220, 220, 214), width=3)
    d.polygon([(ax - 13, ay - 4), (ax - 8, ay - 9), (ax - 8, ay + 1)], fill=(220, 220, 214))
    ax = 285
    d.rectangle([ax - 1, ay - 8, ax + 1, ay + 14], fill=(220, 220, 214)); d.polygon([(ax - 4, ay - 8), (ax + 4, ay - 8), (ax, ay - 13)], fill=(220, 220, 214))
    for (tx, ty) in ((rx0 - 26, ry0 - 26), (rx1 + 26, ry0 - 26), (rx0 - 26, ry1 + 26), (rx1 + 26, ry1 + 26), (rx0 - 26, 230), (rx1 + 26, 240)):
        tree_top(d, tx, ty)
    for x in range(380, WORLD_W, 90):
        tree_top(d, x, ry1 + 24, 9); tree_top(d, x + 40, ry0 - 24, 9)
    # 酒吧（在右边远处）和门口的停车位
    bx0 = 860
    d.rectangle([bx0, ry1 + 30, bx0 + 170, H], fill=(70, 36, 66), outline=OUT)
    d.rectangle([bx0 + 6, ry1 + 34, bx0 + 164, ry1 + 38], fill=(110, 60, 100))
    for k in range(4): d.rectangle([bx0 - 20 + k * 30, ry1 + 2, bx0 - 20 + k * 30 + 1, ry1 + 13], fill=(220, 220, 214))
    return im


def topdown_frame(img, d, T, cam_x, phase_lt):
    base = topdown_base()
    cx = int(clamp(cam_x, 0, WORLD_W - W))
    img.paste(base.crop((cx, CAMY, cx + W, CAMY + H)), (0, 0))
    return cx


def topdown_lights(img, d, T, cx, green_ns):
    for (lx, ly) in ((170, 60), (310, 60), (170, 200), (310, 200), (480, 200), (640, 60), (800, 200)):
        x = lx - cx
        if -40 < x < W + 40: glow(img, x, ly - CAMY, 40, (255, 220, 160), 0.22)
    for (sx, sy, ns) in ((168, 208, True), (312, 52, True), (168, 52, False), (312, 208, False)):
        x = sx - cx; sy -= CAMY
        if not -10 < x < W + 10: continue
        on_green = green_ns if ns else not green_ns
        d.rectangle([x - 4, sy - 9, x + 4, sy + 9], fill=(24, 22, 32), outline=OUT)
        for j, c in enumerate([(255, 60, 60), (255, 190, 40), (60, 230, 120)]):
            on = (j == 2) == on_green and j != 1
            d.rectangle([x - 2, sy - 7 + j * 5, x + 2, sy - 4 + j * 5], fill=c if on else lerpc(c, (20, 20, 30), 0.75))
            if on: glow(img, x, sy - 5 + j * 5, 10, c, 0.45)
    bx = 945 - cx
    if -120 < bx < W + 120:
        pp = 0.75 + 0.25 * math.sin(T * 9) if int(T * 3) % 7 else 0.3
        by = 234 - CAMY + 20
        neon_rect(img, d, [bx - 60, by - 20, bx + 60, by + 20], PINK, pp)
        big_text(img, 'BAR', bx - 8, by, 1, PINK, (255, 200, 230), pp)
        x = bx + 38
        d.rectangle([x - 6, by - 8, x + 4, by + 8], outline=lerpc((60, 30, 50), AMB, pp)); d.arc([x + 1, by - 5, x + 9, by + 4], 270, 90, fill=lerpc((60, 30, 50), AMB, pp))
        d.rectangle([x - 5, by - 4, x + 3, by + 7], fill=lerpc((60, 30, 50), AMB_L, pp * 0.8))


def rain_top(img, d, T, n=90, seed=2):
    for i in range(n):
        r = rng(i * 3 + seed)
        per = 0.6 + r.random() * 0.4
        k = ((T + r.random() * per) % per) / per
        x, y = r.uniform(0, W), r.uniform(0, H)
        if k < 0.5:
            rr = 1 + k * 8
            d.ellipse([x - rr, y - rr * 0.7, x + rr, y + rr * 0.7], outline=(100, 110, 150))
        d.line([(x + 30 * (1 - k) - 6, y - 40 * (1 - k)), (x + 30 * (1 - k) - 8, y - 40 * (1 - k) + 3)], fill=(150, 160, 210))


def walkers(img, d, T, cx):
    for i, col in enumerate((PINK, CYAN, (255, 214, 80), (160, 120, 255))):
        r = rng(i * 9)
        u = ((T * 0.12 + r.random()) % 1)
        x = lerp(176, 304, u) if i % 2 else lerp(304, 176, u)
        y = 52 + r.uniform(-4, 4) - CAMY
        umbrella_top(d, x - cx, y, 6, col)


def s_cross_left(img, d, lt, dur, T, A):
    """俯视雨夜的十字路口：他的车开进左转车道，停在停车线前，左转灯跟着节拍一下一下地闪"""
    cx = topdown_frame(img, d, T, 0, lt)
    topdown_lights(img, d, T, cx, False)
    walkers(img, d, T, cx)
    ox = lerp(-80, 560, span(lt, 0.4, 2.4))                       # 东西向开过一辆出租车
    car_top_at(img, ox, 115 - CAMY, 90, 2, body=(255, 206, 70), body_s=(214, 160, 40))
    u = span(lt, 0, 1.2)
    y = lerp(330, 246, eout(u))
    sig = blink_a(T)
    car_top_at(img, 255, y - CAMY, 0, 2, sig_l=sig, brake=u >= 0.95)
    rain_top(img, d, T)
    props.arrow(img, 40, 110, 4, sig)
    if sig > 0.5:
        text(img, '嗒', 40, 72, AMB_L, (60, 24, 10), FONT_S)
    vig(img, 0.45)


def s_cross_right(img, d, lt, dur, T, A):
    """绿灯亮了，可是打着左转灯的车却往右拐了进去；镜头跟着车往右，一直开到路边一间亮着霓虹的酒吧门口"""
    R, ccx, ccy = 55, 310, 206
    t_go, t_turn = 0.15, 1.35
    if lt < t_go:
        x, y, ang = 255, 246, 0
    elif lt < t_go + 0.35:
        u = (lt - t_go) / 0.35
        x, y, ang = 255, lerp(246, 206, ein(u) * 0.5 + u * 0.5), 0
    elif lt < t_turn:
        u = ease((lt - t_go - 0.35) / (t_turn - t_go - 0.35))
        th = u * math.pi / 2
        x, y, ang = ccx - R * math.cos(th), ccy - R * math.sin(th), math.degrees(th)
    else:
        u = clamp((lt - t_turn) / 3.2)
        dist = 640 * (0.5 * u + 0.5 * ease(u))
        x, y, ang = ccx + dist, ccy - R, 90
        if dist > 560:
            pk = ease(span(dist, 560, 640))
            y = lerp(ccy - R, 212, pk); ang = 90 + 36 * math.sin(pk * math.pi)
    cam = clamp(x - 240, 0, 700) if lt > t_turn else 0
    cam = lerp(0, cam, ease(span(lt, t_turn - 0.2, t_turn + 1.0)))
    cx = topdown_frame(img, d, T, cam, lt)
    topdown_lights(img, d, T, cx, True)
    walkers(img, d, T, cx)
    sig = blink_a(T)
    parked = lt > t_turn + 3.1
    car_top_at(img, x - cx, y - CAMY, ang, 2, sig_l=sig, brake=parked)
    if t_go + 0.35 < lt < t_turn + 0.6:                             # 拐弯时地上的水痕
        for j in range(8):
            th = (j / 8) * math.pi / 2 * ease((lt - t_go - 0.35) / (t_turn - t_go - 0.35))
            d.point((ccx - (R + 6) * math.cos(th) - cx, ccy - (R + 6) * math.sin(th) - CAMY), fill=(90, 96, 130))
    rain_top(img, d, T)
    props.arrow(img, 40, 110, 4, sig)
    if lt > t_go + 0.3:
        f = span(lt, t_go + 0.3, t_go + 0.6) * (1 - span(lt, t_turn + 1.6, t_turn + 2.2))
        if f > 0:
            props.arrow(img, 440, 110, 4, 0.0, left=False, off=(200, 200, 210), glow_r=0)
            text(img, '?!', 440, 78, (255, 255, 255), OUT, alpha=f, scale=2)
    vig(img, 0.45)
