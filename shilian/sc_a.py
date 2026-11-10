"""永不失联的爱 · 片头和第一段主歌。签名都是 (img, d, lt, dur, T, A)：lt 是镜头内的时间，dur 是镜头时长，T 是全片时间，A 是这一帧的音量。

片头：黑暗里一部手机找不到信号，"亲爱的，你在哪？"发不出去；手机发出一圈信号，照亮夜里的两座楼顶，
他拿着传声筒，线的那头却没有人；线上的小心飞上天空，满天星星聚成片名，星星鲸鱼游过，片名化成流星雨落下来。
第一段主歌：他在黄昏的楼顶找她，她一个人坐在月亮上发呆；雨夜房间里她头顶一团乱麻；墙上的影子变成怪物；
灰色人群里只有他俩是彩色的；形状各异的云；落到地上的小云；他绕着路灯打转；她靠上他的肩膀。
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
from props import title_str, artist_str, shots, shake, dpaste, mix_stops
from pix import (W, H, FONT, FONT_S, OUT, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow, tfill, blend_box, text, rng, sky, stars,
                 person, wph, twinkle, sparkle, moon, cloud, darken, dither_fade, grade, vig, BAYER)
from kit import NIGHT, DEEP, DUSK, DAY, GOLDEN

YY, XX = np.mgrid[0:H, 0:W]


# ================================================================ 片头
TS = 4
TITLE_CY = 104


@lru_cache(None)
def title_cells():
    """片名拆成一格一格的星星：[(x, y, 颜色, 横向位置 0..1, 随机数, 起点 x, 起点 y)]"""
    s = title_str()
    ims = [props.big_glyph(c, 1, top=(255, 255, 255), bot=(130, 214, 255), line=(70, 120, 220), out=(20, 30, 90)) for c in s]
    adv = [int(FONT.getlength(c)) for c in s]
    tw = sum(adv) + ims[-1].width - adv[-1]
    th = max(im.height for im in ims)
    ox = W / 2 - tw * TS / 2; oy = TITLE_CY - th * TS / 2
    cells = []
    x = 0
    r = rng(5)
    for im, a in zip(ims, adv):
        arr = np.array(im)
        for py in range(arr.shape[0]):
            for px in range(arr.shape[1]):
                if arr[py, px, 3] > 0:
                    sx, sy = pix.STARS[r.randrange(len(pix.STARS))][:2]
                    cells.append((ox + (x + px) * TS, oy + py * TS, tuple(int(v) for v in arr[py, px, :3]), (x + px) / tw, r.random(),
                                  sx + r.uniform(-30, 30), sy * 0.6 + r.uniform(-20, 20)))
        x += a
    return cells, (ox, oy, ox + tw * TS, oy + th * TS)


def static(d, box, T, n=60, col=(90, 100, 140)):
    x0, y0, x1, y1 = box
    r = rng(int(T * 20))
    for _ in range(n):
        d.point((r.uniform(x0, x1), r.uniform(y0, y1)), fill=col)


def intro_phone(img, d, lt):
    """片头第一段：黑暗里的手机，没有信号"""
    img.paste((4, 4, 12), (0, 0, W, H))
    stars(d, lt, H, 0.25 * clamp(lt / 2), 80)
    a = eout(lt / 0.6)
    k = props.thump(lt, 0.2) if lt > 2.4 else 0
    px, py = 170 + (round(math.sin(lt * 80)) if 2.2 < lt < 3.0 else 0), 26
    box = sig.phone(img, d, px, py, 140, 218, scr=(18, 22, 46))
    sx0, sy0, sx1, sy1 = box
    sig.pix_text(d, '23:10', sx0 + 2, sy0 + 1, (230, 236, 255))
    sig.bars(d, sx1 - 14, sy0 + 9, (int(lt * 4) % 5) * 0.99 if lt < 2.4 else 0, 1, on=(140, 150, 190), off=(60, 64, 90))
    d.line([(sx0, sy0 + 14), (sx1, sy0 + 14)], fill=(50, 56, 90))
    sig.pix_text(d, '她', (sx0 + sx1) / 2 - 6, sy0 + 15, (255, 255, 255))
    sig.heart_at(img, (sx0 + sx1) / 2 + 10, sy0 + 22, 1)
    d.line([(sx0, sy0 + 30), (sx1, sy0 + 30)], fill=(50, 56, 90))
    sig.bubble(img, d, sx1 - 6, sy0 + 40, '亲爱的，你在哪？', mine=True, f=span(lt, 0.5, 0.8))
    sig.bubble(img, d, sx1 - 6, sy0 + 64, '想听你说话', mine=True, f=span(lt, 1.0, 1.3))
    if lt > 1.5:
        cx, cy = sx1 - 92, sy0 + 72
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(230, 60, 70)); d.rectangle([cx, cy - 2, cx, cy], fill=(255, 255, 255))
        d.point((cx, cy + 2), fill=(255, 255, 255))
        sig.pix_text(d, '未送达', sx1 - 40, sy0 + 86, (230, 110, 120))
    # 底部：信号搜索中
    r_ = 6
    cx, cy = (sx0 + sx1) / 2, sy1 - 34
    for k_ in range(8):
        aa = lt * 6 + k_ * math.pi / 4
        c = lerpc((40, 44, 80), (200, 220, 255), (k_ / 8))
        d.point((cx + math.cos(aa) * r_, cy + math.sin(aa) * r_), fill=c)
    sig.pix_text(d, '信号搜索中' + '.' * (int(lt * 3) % 4), sx0 + 12, sy1 - 22, (150, 160, 200))
    static(d, box, lt, 30, (60, 70, 110))
    if a < 1: pix.dither_fade(img, 1 - a)


def rooftops(img, d, T, lt, oy=0.0, she=False, lift=0.0):
    """两座楼顶：左边是他，右边的楼顶上只躺着一只传声筒（she=True 时她在）"""
    gx = 12 * math.sin(T * 0.15)
    kit.night(img, d, T, NIGHT, 220)
    kit.galaxy(img, 0.5 * clamp(oy / 120 + 0.3))
    pix.moon(d, 392, 56 + oy * 0.6, 14); glow(img, 392, 56 + oy * 0.6, 40, (200, 210, 255), 0.25)
    frac = 0.08 + 0.3 * clamp((lt - 3.0) / 5)
    pix.city(img, d, 252 + oy, 31, gx * 0.3, (26, 30, 74), (150, 140, 120), 60, 150, frac * 0.6, T)
    pix.city(img, d, 262 + oy, 7, gx * 0.6, (16, 18, 48), (255, 214, 140), 40, 110, frac, T)
    sig.rooftop(d, -10, 170, 190 + oy, (30, 30, 62), (70, 70, 120), (255, 214, 140), T, True, 1)
    sig.rooftop(d, 330, 490, 200 + oy, (30, 30, 62), (70, 70, 120), (255, 214, 140), T, False, 2)
    # 他：站在左边楼顶，拿着罐子贴在耳边
    hx, hy = 110, 190 + oy
    person(img, 'boy', hx, hy, view='side', pose='stand', expr='down' if lt < 6.5 else 'smile', arms='phone', s=2)
    p0 = sig.can(d, hx + 13, hy - 52, 1, flip=False)
    if she:
        sx_, sy_ = 380, 200 + oy
        person(img, 'girl', sx_, sy_, view='side', pose='stand', expr='smile', arms='phone', s=2, flip=True)
        p1 = sig.can(d, sx_ - 13, sy_ - 52, 1, flip=True)
    else:
        p1 = sig.can(d, 370, 196 + oy, 1, flip=True)
    if lift > 0:                                                # 线的那头离开罐子，飘上天空
        p1 = (lerp(p1[0], 300, ease(lift)), lerp(p1[1], -40, ease(lift)))
    pul = [((lt * 0.45 + k / 3) % 1) for k in range(3)] if lt > 3.4 else []
    sig.string(img, d, p0, p1, 26 * (1 - lift), T, glow_a=0.4 + 0.6 * lift, pulses=pul)
    if not she and lift <= 0 and lt > 4.6:
        kit.pop(d, 372, 186 + oy, '?', T, (255, 240, 140), span(lt, 4.6, 5.0))


def intro_title(img, d, lt, T):
    """星星聚成片名、鲸鱼游过、片名化成流星雨"""
    cells, box = title_cells()
    bx0, by0, bx1, by1 = box
    gather0 = 11.33
    formed = 14.09
    fall0 = 19.9
    if formed - 0.4 < lt < fall0 + 1.5:
        a = clamp((lt - formed + 0.4) / 0.6) * clamp((fall0 + 1.5 - lt) / 1.5)
        glow(img, W / 2, TITLE_CY, 220, (90, 140, 255), 0.28 * a * (0.85 + 0.15 * math.sin(T * 3)), 70)
    if 15.0 < lt < 21.5:                                         # 星星鲸鱼从片名后面游过
        u = (lt - 15.0) / 6.5
        sig.whale(img, d, lerp(-80, W + 80, u), 60 + 14 * math.sin(u * 6), 2, T, alpha=clamp(u * 6) * clamp((1 - u) * 6))
    fl = clamp(1 - (lt - formed) / 0.4) if lt > formed else 0
    for (cx, cy, col, u, r, sx, sy) in cells:
        arrive = gather0 + 0.4 + u * 1.7 + r * 0.5
        depart = gather0 - 1.4 + r * 1.2
        if lt < depart:
            continue
        if lt < arrive:
            f = (lt - depart) / (arrive - depart)
            fe = ease(f)
            mx, my = (sx + cx) / 2 + 80 * math.sin(r * 6.28), min(sy, cy) - 40 - 40 * r
            x = (1 - fe) ** 2 * sx + 2 * (1 - fe) * fe * mx + fe * fe * cx
            y = (1 - fe) ** 2 * sy + 2 * (1 - fe) * fe * my + fe * fe * cy
            c = lerpc((150, 160, 220), col, fe)
            d.point((x, y), fill=c)
            if f > 0.1 and r < 0.35:
                fp = ease(f - 0.025)
                xp = (1 - fp) ** 2 * sx + 2 * (1 - fp) * fp * mx + fp * fp * cx
                yp = (1 - fp) ** 2 * sy + 2 * (1 - fp) * fp * my + fp * fp * cy
                d.line([(xp, yp), (x, y)], fill=lerpc((30, 36, 90), c, 0.35))
            continue
        fall = lt - (fall0 + u * 1.0 + r * 0.6)
        if fall > 0:
            vx = -30 - 40 * r
            x, y = cx + vx * fall, cy + 40 * fall + 160 * fall * fall
            if y > H + 10: continue
            d.line([(x, y), (x - vx * 0.06, y - (40 + 320 * fall) * 0.06)], fill=lerpc(col, (60, 70, 140), 0.4))
            d.rectangle([x, y, x + 1, y + 1], fill=col)
            continue
        tw = 0.75 + 0.25 * math.sin(T * 4 + r * 30)
        c = lerpc(col, (255, 255, 255), fl * 0.8)
        c = lerpc((40, 50, 110), c, tw)
        d.rectangle([cx, cy, cx + TS - 2, cy + TS - 2], fill=c)
        if r < 0.05 and tw > 0.95: twinkle(d, int(cx + 1), int(cy + 1), (T * 1.3 + r * 7) % 1, (255, 255, 255), 3)
    if lt > formed + 0.5:
        a = clamp((lt - formed - 0.5) / 0.8) * clamp((fall0 + 0.6 - lt) / 0.6)
        ar = artist_str()
        if ar: text(img, ar, W / 2, by1 + 22, col=(236, 240, 255), alpha=a)
        text(img, '· 像 素 M V ·', W / 2, by1 + 42, col=(170, 190, 240), font=FONT_S, alpha=a, shadow=False)
    if lt > formed:                                              # 拍点上的流星
        for b in props.beats_in(formed, min(lt, fall0)):
            k = int(b * 10)
            r_ = rng(k)
            pix.meteor(d, lt, b, r_.uniform(200, 470), r_.uniform(0, 40), -110, 70, 0.7)


def s_intro(img, d, lt, dur, T, A):
    tilt0, tilt1 = 8.73, 11.0
    if lt < 3.03:
        intro_phone(img, d, lt)
        return
    oy = ease(span(lt, tilt0, tilt1)) * 300
    lift = ease(span(lt, 6.6, 9.4))
    if oy < 290:
        rooftops(img, d, T, lt, oy, False, lift)
    else:
        kit.night(img, d, T, NIGHT, 220)
        kit.galaxy(img, 0.85)
    if lt > tilt0:
        intro_title(img, d, lt, T)
    if lt > 9.0 and lt < 12.5:                                   # 飘上天的小心变成星星
        for k in range(10):
            u = clamp((lt - 9.0 - k * 0.15) / 1.6)
            if 0 < u < 1:
                x = 300 + 60 * math.sin(k * 2.3) * u; y = lerp(H, 30 + k * 7, eout(u))
                sig.heart_at(img, x, y, 1, alpha=1 - u * 0.6)
                glow(img, x, y, 10, sig.HEART, 0.4 * (1 - u))
    # 片头开始的一圈信号：从手机的位置扩出去
    if lt < 3.9:
        f = (lt - 3.03) / 0.87
        r = eout(f) * 330
        m = (XX - 240) ** 2 + (YY - 120) ** 2 > r * r
        if m.any():
            arr = np.asarray(img).copy(); arr[m] = (4, 4, 12)
            img.paste(Image.fromarray(arr))
        dd = ImageDraw.Draw(img)
        for k in range(3):
            rr = r - k * 8
            if rr > 0: dd.ellipse([240 - rr, 120 - rr, 240 + rr, 120 + rr], outline=lerpc(sig.SIG, (4, 4, 12), k / 3))


# ================================================================ 第一段主歌
def s_hide(img, d, lt, dur, T, A):
    """亲爱的你躲在哪里发呆：他在黄昏的楼顶上找；镜头往上摇，她一个人抱着膝盖坐在弯月上"""
    oy = ease(span(lt, 2.0, 3.6)) * 210
    sky(img, DUSK, 0, H, 6)
    stars(d, T, 150, clamp(oy / 210) * 0.8, 120)
    cloud(d, 40 + T * 3 % 500 - 60, 130 + oy * 0.5, 2, (250, 190, 190), (220, 150, 170))
    cloud(d, 330 - T * 2 % 500, 160 + oy * 0.5, 1.5, (250, 200, 200), (226, 160, 176))
    # 弯月和她
    my = -120 + oy
    if my > -60:
        kit.crescent(img, d, 300, my, 46, (255, 236, 186), (0.5, -0.25))
        person(img, 'girl', 282, my + 34, view='side', pose='sit', expr='down', arms='lap', s=2, flip=True)
        kit.pop(d, 270, my - 6, '...', T, (255, 250, 230))
        for k in range(5):
            twinkle(d, int(240 + k * 30), int(my - 30 + (k * 17) % 50), (T * 0.6 + k * 0.23) % 1, (255, 250, 220), 3)
    # 城市和他
    by = 270 + oy
    pix.city(img, d, by - 60, 31, T * 4, (92, 70, 120), (255, 214, 160), 60, 140, 0.2, T)
    pix.city(img, d, by - 30, 7, T * 8, (58, 42, 86), (255, 214, 140), 40, 100, 0.25, T)
    sig.rooftop(d, -10, W + 10, by - 40, (44, 34, 70), (96, 76, 130), None, T, True, 3)
    hx = 60 + lt * 26
    if by - 40 < H + 60:
        person(img, 'boy', hx, by - 40, view='side', pose='walk', ph=wph(lt, 6), expr='worried', arms='phone', s=2)
        sig.bubble(img, d, hx + 10, by - 128, '你在哪？', f=span(lt, 0.4, 0.7))
        sig.bars(d, hx - 22, by - 112, 1 if int(T * 3) % 2 else 0, 2, on=(255, 240, 200), off=(110, 90, 130))
        kit.pop(d, hx + 2, by - 98, '?', T, (255, 240, 160), span(lt, 1.2, 1.5))
    vig(img, 0.35)


SCRIBBLE = None


def scribble_pts():
    global SCRIBBLE
    if SCRIBBLE is None:
        r = rng(4); pts = []; x, y = 0.0, 0.0
        for _ in range(120):
            x += r.uniform(-6, 6); y += r.uniform(-3, 3)
            x = max(-26, min(26, x)); y = max(-10, min(10, y))
            pts.append((x, y))
        SCRIBBLE = pts
    return SCRIBBLE


def s_worry(img, d, lt, dur, T, A):
    """有什么心事还无法释怀：雨夜的房间，她抱着膝盖坐在床上，头顶一团乱麻在下小雨；手机亮了也没看"""
    img.paste((44, 40, 80), (0, 0, W, H))
    for x in range(0, W, 16): d.line([(x, 0), (x, 190)], fill=(50, 46, 88))
    d.rectangle([0, 190, W, H], fill=(70, 52, 70))
    for x in range(0, W, 24): d.line([(x, 190), (x - 30, H)], fill=(80, 60, 80))
    # 窗外：夜雨里的城市
    wx0, wy0, wx1, wy1 = 40, 36, 190, 150
    win = Image.new('RGB', (wx1 - wx0, wy1 - wy0)); wd = ImageDraw.Draw(win)
    win.paste(kit.NIGHT[1][1], (0, 0, win.width, win.height))
    sub = Image.new('RGB', (W, H)); sd = ImageDraw.Draw(sub)
    sky(sub, kit.RAINY); pix.city(sub, sd, 230, 7, 0, (22, 24, 50), (255, 214, 140), 60, 160, 0.3, T)
    pix.rain(sd, T, 0, W, 0, H, 140, (120, 140, 190), 260, -2, 6, 3)
    img.paste(sub.crop((120, 100, 120 + win.width, 100 + win.height)), (wx0, wy0))
    props.drops_on_glass(img, d, T, (wx0, wy0, wx1, wy1), 40, 2)
    d.rectangle([wx0 - 4, wy0 - 4, wx1 + 4, wy1 + 4], outline=(150, 120, 110), width=4)
    d.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=(150, 120, 110), width=3)
    d.line([(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], fill=(150, 120, 110), width=3)
    d.rectangle([wx0 - 10, wy1 + 4, wx1 + 10, wy1 + 9], fill=(170, 140, 120))
    # 床
    d.rectangle([230, 170, 470, 230], fill=(220, 210, 236)); d.rectangle([230, 170, 470, 176], fill=(250, 246, 255))
    d.rectangle([230, 200, 470, 240], fill=(130, 150, 210)); d.rectangle([226, 140, 236, 240], fill=(150, 110, 90))
    # 台灯
    glow(img, 210, 150, 60, (255, 200, 140), 0.25)
    d.rectangle([196, 170, 224, 230], fill=(120, 90, 80)); d.polygon([(200, 140), (220, 140), (226, 156), (194, 156)], fill=(255, 220, 160))
    # 她
    sx = 330
    person(img, 'girl', sx, 206, view='front', pose='sit', expr='sad', arms='lap', s=2)
    # 头顶的一团乱麻
    cx, cy = sx, 92 + 3 * math.sin(T * 2)
    for ox, oy_, r in ((-26, 4, 14), (0, -6, 20), (24, 2, 15)):
        d.ellipse([cx + ox - r - 1, cy + oy_ - r - 1, cx + ox + r + 1, cy + oy_ + r + 1], fill=(30, 26, 44))
    for ox, oy_, r in ((-26, 4, 14), (0, -6, 20), (24, 2, 15)):
        d.ellipse([cx + ox - r, cy + oy_ - r, cx + ox + r, cy + oy_ + r], fill=(90, 84, 116))
    pts = scribble_pts()
    ang = T * 0.8
    m = int(len(pts) * clamp(0.3 + lt / 3))
    d.line([(cx + x * 1.3 * math.cos(ang * 0.2) - y * 0.2, cy - 2 + y * 1.2 + x * 0.1 * math.sin(ang)) for x, y in pts[:m]], fill=(24, 20, 36))
    pix.rain(d, T, cx - 26, cx + 26, cy + 14, 128, 14, (150, 180, 240), 120, 0, 3, 5)
    # 手机在床上亮了
    if lt > 1.8:
        b = 0.5 + 0.5 * math.sin(T * 12)
        px_ = 400 + (1 if int(T * 20) % 2 and lt < 3 else 0)
        d.rectangle([px_, 194, px_ + 10, 200], fill=(40, 40, 54))
        d.rectangle([px_ + 1, 195, px_ + 9, 199], fill=lerpc((90, 110, 160), (200, 236, 255), b))
        glow(img, px_ + 5, 196, 16, (180, 220, 255), 0.4 * b)
        sig.bubble(img, d, 398, 160, '在吗？', f=span(lt, 2.0, 2.3))
    vig(img, 0.45)


def shadow_of(who, s, view='side', pose='walk', ph=0, flip=False):
    im = pix.char_img(who, 'young', view, pose, ph % 4, 'smile', 'swing')
    a = np.array(im); m = a[..., 3] > 0
    a[m, :3] = (26, 18, 36)
    im = Image.fromarray(a)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im.resize((im.width * s, im.height * s), Image.NEAREST)


def s_bad(img, d, lt, dur, T, A):
    """我们总把人生想得太坏：夜里走在墙边，路灯把两人的影子投在墙上，影子越长越大，长出角、獠牙和红眼睛"""
    off = lt * 30
    img.paste((150, 108, 92), (0, 0, W, 200))
    for y in range(0, 200, 8):
        for x in range(-((int(off) + (y // 8) * 8) % 16), W, 16):
            d.rectangle([x, y, x + 14, y + 6], fill=(170, 124, 102))
    glow(img, 60, 60, 260, (255, 220, 150), 0.35)
    d.rectangle([0, 200, W, H], fill=(54, 44, 60)); d.line([(0, 200), (W, 200)], fill=(90, 70, 80))
    for x in range(-int(off * 1.0) % 40, W, 40): d.line([(x, 236), (x + 18, 236)], fill=(90, 80, 96))
    grow = ease(span(lt, 0.4, 4.2))
    s = 2 + int(round(grow * 3))
    for who, x in (('boy', 196 - grow * 40), ('girl', 336 + grow * 30)):
        sh = shadow_of(who, s, ph=wph(lt, 6))
        top = 206 + 2 * s - pix.FY * s
        dpaste(img, sh, x - pix.CX * s, top, 0.8)
        hx, hy = x + 1 * s, 206 + 2 * s - 22 * s
        if grow > 0.3:
            g = clamp((grow - 0.3) / 0.4)
            for sg in (-1, 1):
                d.polygon([(hx + sg * 2 * s, hy - 5 * s), (hx + sg * (5 + 3 * g) * s, hy - (9 + 5 * g) * s), (hx + sg * 5 * s, hy - 4 * s)],
                          fill=(26, 18, 36))
        if grow > 0.55:
            g = clamp((grow - 0.55) / 0.3)
            for ex in (-1, 3):
                d.rectangle([hx + ex * s, hy, hx + ex * s + s - 1, hy + s - 1], fill=lerpc((26, 18, 36), (255, 60, 60), g))
            for k in range(3):
                tx = hx - 1 * s + k * 2 * s
                d.polygon([(tx, hy + 3 * s), (tx + s, hy + 5 * s), (tx + 2 * s, hy + 3 * s)], fill=lerpc((26, 18, 36), (240, 230, 220), g))
    # 路灯
    pix.lamp(img, d, 20, 230, 1.0, 120)
    # 两个人
    expr = 'smile' if lt < 2.0 else 'worried'
    person(img, 'boy', 250, 232, view='side', pose='walk', ph=wph(lt, 6), expr=expr, s=2)
    person(img, 'girl', 290, 232, view='side', pose='walk', ph=wph(lt, 6) + 2, expr=expr, s=2)
    if lt > 3.4:
        kit.pop(d, 298, 146, 'sweat', T, f=span(lt, 3.4, 3.7)); kit.pop(d, 254, 146, '!', T, f=span(lt, 3.6, 3.9))
    darken(img, 0.2 * grow)
    vig(img, 0.5)


@lru_cache(None)
def gray_img(who, view, pose, ph, expr, arms, flip, s):
    im = pix.char_img(who, 'young', view, pose, ph, expr, arms)
    a = np.array(im).astype(float)
    g = a[..., :3] @ np.array([0.3, 0.59, 0.11])
    a[..., :3] = (g[..., None] * 0.55 + 70)
    im = Image.fromarray(a.astype(np.uint8))
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im.resize((im.width * s, im.height * s), Image.NEAREST)


def s_weird(img, d, lt, dur, T, A):
    """像旁人不允许我们的怪：灰色的人群齐步往右走，只有他俩是彩色的，一个蹦一个跳往左走；路人纷纷回头冒出问号"""
    img.paste((150, 152, 160), (0, 0, W, H))
    pix.city(img, d, 190, 12, lt * 6, (120, 122, 132), (170, 172, 180), 50, 140, 0.4, T, blink=False)
    d.rectangle([0, 190, W, H], fill=(110, 112, 120)); d.line([(0, 190), (W, 190)], fill=(90, 92, 100))
    for x in range(-int(lt * 40) % 30, W, 30): d.line([(x, 215), (x + 14, 215)], fill=(130, 132, 140))
    # 灰色人群（两排）
    for row, (y, s, sp) in enumerate(((186, 1, 30), (250, 2, 40))):
        for k in range(10):
            x = (k * 62 + row * 30 + lt * sp) % (W + 80) - 40
            look = lt > 1.6 + k * 0.12 and abs(x - 250) < 140
            im = gray_img('girl' if (k + row) % 3 == 0 else 'boy', 'front' if look else 'side', 'stand' if look else 'walk',
                          0 if look else wph(lt + k * 0.3, 6), 'sneer' if look else 'neutral', 'cross' if look else 'swing', False, s)
            dpaste(img, im, x - pix.CX * s, y - pix.FY * s)
            if look and row == 1: kit.pop(d, x, y - 84, '?!'[k % 2], T, (240, 240, 250), span(lt, 1.6 + k * 0.12, 2.0 + k * 0.12))
            if row == 1 and k == 3 and x > 200: pass
        if row == 0:
            # 他俩：在两排人中间，往左走，她蹦蹦跳跳牵着一只心形气球，他跳舞
            bx = 300 - lt * 14
            jump = abs(math.sin(lt * 5)) * 8
            gx, gy = bx + 34, 222 - jump
            person(img, 'girl', gx, gy, view='side', pose='jump' if jump > 3 else 'stand', expr='laugh', arms='up', s=2, flip=True)
            hx = gx - 6 + 10 * math.sin(T * 1.5); hy = 110 + 4 * math.sin(T * 2)
            d.line([(gx - 4, gy - 46), (hx, hy + 12)], fill=(250, 250, 250))
            sig.heart_at(img, hx, hy, 3)
            person(img, 'boy', bx - 20, 222, view='front', pose='stand', expr='happy', arms='up' if int(lt * 4) % 2 else 'spread', s=2)
            for k in range(3):
                pix.sparkle(d, int(bx - 40 + k * 40), int(130 + 20 * math.sin(T * 3 + k)), T + k, (255, 236, 120), 2)
    vig(img, 0.3)


def s_clouds(img, d, lt, dur, T, A):
    """每一片与众不同的云彩：两人躺在山坡上看云，天上飘过心、猫、鲸鱼、星星、兔子、音符形状的云"""
    sky(img, DAY, 0, H, 5)
    glow(img, 420, 40, 60, (255, 250, 210), 0.5); d.ellipse([408, 28, 432, 52], fill=(255, 250, 220))
    kinds = ['heart', 'cat', 'whale', 'star', 'rabbit', 'note']
    for k, kind in enumerate(kinds):
        x = (k * 120 + lt * 22 + 30) % 720 - 100
        y = 46 + (k * 41) % 100 + 4 * math.sin(T + k)
        sig.shape_cloud(img, kind, x, y, 5 if k % 2 == 0 else 4)
    for k in range(3): pix.bird(d, int(100 + k * 14 + lt * 20), int(70 + k * 5), T, (60, 70, 100), k)
    # 山坡
    d.ellipse([-120, 190, 600, 420], fill=(110, 190, 100))
    d.ellipse([-120, 190, 600, 420], outline=(150, 214, 120), width=2)
    kit.flowers(d, T, 205, 268, 70, 3)
    pix.grass(d, 260, (80, 160, 80), (130, 200, 110), T, 0, W, 3, 1, 5)
    kit.lying(img, 'boy', 210, 228, 2, 'smile')
    kit.lying(img, 'girl', 300, 226, 2, 'happy')
    if lt > 1.0:
        kit.pop(d, 318, 186, '!', T, f=span(lt, 1.0, 1.3))
    if lt > 2.6:
        sig.heart_at(img, 272, 180 - (lt - 2.6) * 12, 2, alpha=clamp(1 - (lt - 2.6) / 2.5))


def s_ground_cloud(img, d, lt, dur, T, A):
    """都需要找到天空去存在吗：一朵小猫云从天上落下来，停在她身边，给一朵花苞下雨，花开了"""
    sky(img, GOLDEN, 0, H, 6)
    glow(img, 120, 170, 120, (255, 220, 160), 0.45)
    d.ellipse([90, 140, 150, 200], fill=(255, 236, 190))
    pix.hills(d, 200, 10, 0.012, 1.0, (150, 140, 110))
    d.rectangle([0, 210, W, H], fill=(140, 170, 90))
    pix.hills(d, 214, 6, 0.02, 2.0, (120, 160, 80))
    kit.flowers(d, T, 222, 268, 50, 9, cols=((255, 200, 120), (255, 160, 170), (250, 250, 240)))
    # 星星拼成的大问号
    qa = clamp(lt / 1.5) * 0.7
    for i, (qx, qy) in enumerate([(0, 2), (1, 0), (2, 0), (3, 0), (4, 1), (4, 2), (3, 3), (2, 4), (2, 5), (2, 7)]):
        if i > lt * 5: continue
        x_, y_ = 360 + qx * 12, 22 + qy * 12
        glow(img, x_, y_, 8, (255, 255, 230), 0.5 * qa)
        pix.sparkle(d, int(x_), int(y_), T + i, lerpc((255, 230, 180), (255, 255, 255), qa), 3)
    # 小猫云落下来
    u = eout(span(lt, 0.0, 2.6))
    cx, cy = lerp(300, 300, u), lerp(-30, 160, u) + 3 * math.sin(T * 2.5)
    sig.shape_cloud(img, 'cat', cx, cy, 5)
    # 花苞和雨
    fx, fy = 300, 238
    if lt > 2.4:
        pix.rain(d, T, cx - 18, cx + 18, cy + 22, fy - 16, 14, (150, 200, 255), 80, 0, 3, 2)
    bloom = ease(span(lt, 3.0, 4.2))
    d.line([(fx, fy), (fx, fy - 10 - 8 * bloom)], fill=(70, 150, 70), width=2)
    d.rectangle([fx - 4, fy - 6, fx - 1, fy - 4], fill=(90, 170, 80)); d.rectangle([fx + 2, fy - 8, fx + 5, fy - 6], fill=(90, 170, 80))
    py = fy - 10 - 8 * bloom
    if bloom < 0.3:
        d.ellipse([fx - 3, py - 6, fx + 3, py + 1], fill=(240, 120, 150))
    else:
        r = 3 + 6 * bloom
        for k in range(6):
            a = k * math.pi / 3 + T * 0.3
            d.ellipse([fx + math.cos(a) * r * 0.8 - 3, py + math.sin(a) * r * 0.8 - 3, fx + math.cos(a) * r * 0.8 + 3, py + math.sin(a) * r * 0.8 + 3],
                      fill=(255, 140, 170))
        d.ellipse([fx - 3, py - 3, fx + 3, py + 3], fill=(255, 220, 100))
        if bloom > 0.9: glow(img, fx, py, 24, (255, 200, 220), 0.4)
    # 她坐在旁边看
    person(img, 'girl', 352, 246, view='side', pose='sit', expr='happy' if bloom > 0.5 else 'surprised', arms='lap', s=2, flip=True)
    if bloom > 0.6: sig.heart_at(img, 344, 150 - (lt - 4) * 8, 1)


def s_circle(img, d, lt, dur, T, A):
    """我们都习惯了原地徘徊：他绕着路灯一圈圈地走，地上踩出一圈脚印；天色飞快地从白天换到夜里，天上的大钟转个不停"""
    ph = lt / dur
    stops = mix_stops(kit.DUSK, kit.NIGHT, ease(ph * 1.4)) if ph < 0.7 else mix_stops(kit.NIGHT, kit.DEEP, (ph - 0.7) / 0.3)
    sky(img, stops, 0, H, 6)
    stars(d, T, 180, clamp(ph * 2 - 0.4), 160)
    # 太阳落下、月亮升起
    sa = lerp(-0.4, 1.4, ph)
    pix.moon(d, 240 + math.cos(sa * math.pi) * 200, 200 - math.sin(sa * math.pi) * 150, 12)
    props.clock(d, 240, 70, 34, T * 3.0, T * 36.0, rim=(150, 120, 200), face=(60, 56, 110), hand=(220, 220, 255))
    glow(img, 240, 70, 60, (180, 160, 255), 0.15)
    pix.city(img, d, 196, 4, 0, (40, 40, 80), (255, 214, 140), 30, 90, 0.3 * ph, T)
    d.rectangle([0, 196, W, H], fill=(70, 64, 92))
    # 地上的脚印
    cx, cy, rx, ry = 240, 228, 90, 18
    for k in range(40):
        a = k / 40 * 2 * math.pi
        if (a / (2 * math.pi)) < (lt * 0.3) % 1 or lt > 3.3:
            d.rectangle([cx + rx * math.sin(a), cy + ry * math.cos(a), cx + rx * math.sin(a) + 1, cy + ry * math.cos(a)], fill=(110, 104, 140))
    th = lt * 2.1
    hx, hy = cx + rx * math.sin(th), cy + ry * math.cos(th)
    front = math.cos(th) > 0
    vx = math.cos(th)
    if not front:
        person(img, 'boy', hx, hy, view='side', pose='walk', ph=wph(lt, 7), expr='down', s=2, flip=vx < 0)
    pix.lamp(img, d, cx, cy + 4, clamp(ph * 2), 110)
    if front:
        person(img, 'boy', hx, hy, view='side', pose='walk', ph=wph(lt, 7), expr='down', s=2, flip=vx < 0)
    vig(img, 0.45)


def s_lean(img, d, lt, dur, T, A):
    """却无法习惯被依赖：黄昏的河边长椅，她把头靠到他肩上，他吓了一跳、脸红冒汗，然后慢慢放松，冒出一颗心"""
    sky(img, GOLDEN, 0, 190, 6)
    glow(img, 240, 170, 140, (255, 200, 140), 0.5)
    d.ellipse([214, 146, 266, 198], fill=(255, 226, 170))
    pix.city(img, d, 182, 21, 0, (150, 100, 120), (255, 220, 160), 20, 60, 0.1, T, blink=False)
    d.rectangle([0, 182, W, 214], fill=(200, 140, 140))
    for k in range(12):
        y = 186 + k * 2.5
        x0 = 240 - 30 + 6 * math.sin(T * 2 + k)
        d.line([(x0 - k * 3, y), (x0 + 60 + k * 3, y)], fill=(255, 210, 160) if k % 2 == 0 else (240, 180, 150))
    d.rectangle([0, 214, W, H], fill=(110, 130, 80))
    pix.grass(d, 216, (90, 120, 70), (140, 160, 90), T, 0, W, 3, 2, 4)
    for k in range(3): pix.bird(d, int(60 + k * 16 + lt * 12), int(80 - k * 4), T, (90, 60, 80), k)
    M.bench(d, 190, 258, 100, (120, 80, 60), (90, 56, 40))
    lean = ease(span(lt, 1.0, 2.0))
    person(img, 'boy', 222, 246, view='front', pose='sit',
           expr='surprised' if 1.8 < lt < 3.4 else ('closed' if lt >= 3.4 else 'smile'), arms='lap', s=2)
    kit.person_rot(img, 'girl', 256 - 4 * lean, 246, 14 * lean, 2, view='front', pose='sit', expr='closed' if lean > 0.5 else 'smile', arms='lap')
    if 1.8 < lt < 3.4:
        kit.pop(d, 212, 160, '!', T, f=span(lt, 1.8, 2.0)); kit.pop(d, 236, 172, 'sweat', T, f=span(lt, 2.0, 2.3))
        for k in range(2): d.point((214 + k * 9, 182), fill=pix.BLUSH)
    if lt > 3.6:
        for k in range(3):
            u = (lt - 3.6 - k * 0.5)
            if u > 0: sig.heart_at(img, 236 + 8 * math.sin(u * 3 + k), 150 - u * 16, 1 + (k == 0), alpha=clamp(1 - u / 2.5))
    vig(img, 0.35)
