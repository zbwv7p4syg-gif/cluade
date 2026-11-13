"""爱错 · 通用道具：节拍、点阵贴图和镜头、烟、火车、钟、片名大字、拍立得、特写的大脸，以及雨、倒影和调色。

从 lixiang/props.py 复制而来，去掉了用不上的公交、收音机、卡带、吉他和小黑猫；火车窗里坐的换成了她。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
from pix import (W, H, FONT, FONT_S, OUT, SKIN, SKIN_S, ICE, ICE_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow,
                 tfill, blend_box, paste, outline, text, rng, sky, stars, rain, city, lamp, with_alpha, heart_poly)

CREAM = (250, 242, 222)
INK = (12, 10, 22)
GOLD, GOLD_L = (255, 200, 92), (255, 238, 170)
AMBER = (255, 176, 90)
PINK, PINK_L = (255, 150, 176), (255, 214, 224)
RED, RED_L, RED_D = (226, 60, 70), (255, 140, 140), (150, 30, 44)
CYAN = (110, 220, 255)
RUST, RUST_D, RUST_L = (168, 96, 56), (118, 62, 40), (204, 132, 80)
TIN, TIN_S, TIN_L = (84, 128, 102), (58, 92, 74), (128, 170, 138)      # 旧铁皮的绿
MOSS, MOSS_D, MOSS_L = (98, 150, 70), (60, 104, 52), (160, 204, 98)
WOOD, WOOD_D, WOOD_L = (150, 96, 62), (108, 66, 44), (190, 132, 84)

PALE = ((0, (84, 90, 126)), (0.45, (156, 152, 176)), (0.78, (214, 192, 190)), (1, (242, 218, 198)))     # 暮色苍白
GOLDEN = ((0, (82, 100, 168)), (0.42, (226, 150, 132)), (0.75, (255, 198, 138)), (1, (255, 232, 176)))
NIGHT = ((0, (8, 8, 28)), (0.55, (24, 22, 62)), (1, (62, 46, 104)))
DAWN = ((0, (40, 52, 110)), (0.5, (150, 120, 170)), (0.8, (250, 170, 150)), (1, (255, 220, 170)))
DAY = ((0, (96, 156, 226)), (0.6, (156, 204, 240)), (1, (226, 240, 250)))


def mix_stops(a, b, f, q=24):
    """两套天空渐变按 f 混合（f 量化成 q 档，好让渐变图能缓存）"""
    f = round(clamp(f) * q) / q
    return tuple((pa, lerpc(ca, cb, f)) for (pa, ca), (pb, cb) in zip(a, b))


# ---------------------------------------------------------------- 节拍
def beats_in(t0, t1):
    b = pix.AUDIO['beats']
    return [float(x) for x in b if t0 <= x < t1]


def last_beat(T):
    b = pix.AUDIO['beats']
    i = int(np.searchsorted(b, T, 'right')) - 1
    return float(b[i]) if i >= 0 else -9.0


def beat_after(T, n=1):
    bs = [x for x in pix.AUDIO['beats'] if x > T + 0.05]
    return float(bs[n - 1]) if len(bs) >= n else T + 1.2 * n


def thump(T, decay=0.25):
    """拍点上的一下：1 → 0"""
    return pix.pulse(T, decay)


# ---------------------------------------------------------------- 贴图和镜头
def dpaste(img, im, x, y, a=1.0, ox=0):
    """按 Bayer 点阵的透明度贴图（像素风的半透明）"""
    if a <= 0: return
    if a < 1:
        arr = np.array(im)
        arr[pix.bayer(im.height, im.width, int(x) + ox, int(y)) >= a, 3] = 0
        im = Image.fromarray(arr)
    img.paste(im, (int(round(x)), int(round(y))), im)


def shots(img, lt, parts, tr=0.35, kind='dissolve'):
    """一个镜头里再分几小段：parts = [(开始时间, 画法), ...]，画法签名 f(img, d, t)，t 是这一小段内的时间。
    换段时用 Bayer 点阵溶解 tr 秒"""
    k = max(i for i, (t0, _) in enumerate(parts) if lt >= t0 or i == 0)
    t0, fn = parts[k]
    d = ImageDraw.Draw(img); d.fontmode = '1'
    fn(img, d, lt - t0)
    if k > 0 and lt - t0 < tr:
        prev = Image.new('RGB', (W, H)); pd = ImageDraw.Draw(prev); pd.fontmode = '1'
        p0, pf = parts[k - 1]
        pf(prev, pd, lt - p0)
        f = (lt - t0) / tr
        if kind == 'white':
            pix.dither_fade(img, 1 - ease(f), (255, 250, 240)); return
        m = pix.BAYER >= ease(f)
        a = np.asarray(img).copy(); a[m] = np.asarray(prev)[m]
        img.paste(Image.fromarray(a))


def shake(img, k, amp_, dur):
    if not 0 <= k < dur: return
    a = amp_ * (1 - k / dur)
    dx, dy = round(a * math.sin(k * 97)), round(a * math.cos(k * 71))
    if dx or dy:
        src = img.copy(); img.paste((8, 6, 20), (0, 0, W, H)); img.paste(src, (dx, dy))


def zoom(img, s, cx=W / 2, cy=H / 2):
    """整数倍放大画面的一部分（最近邻，保持像素感）"""
    if s <= 1: return
    w, h = W / s, H / s
    box = (int(round(cx - w / 2)), int(round(cy - h / 2)))
    box = (max(0, min(W - int(w), box[0])), max(0, min(H - int(h), box[1])))
    crop = img.crop((box[0], box[1], box[0] + int(w), box[1] + int(h)))
    img.paste(crop.resize((W, H), Image.NEAREST))


# ---------------------------------------------------------------- 角色（任意倍数）
def person_s(img, who, x, y, sc, age='young', view='side', pose='stand', ph=0, expr='smile', arms='auto', flip=False, alpha=1.0,
             shade=None, tint=None):
    """和 pix.person 一样，但可以按小数倍缩放（远处的人）"""
    if abs(sc - round(sc)) < 1e-3 and sc >= 1:
        pix.person(img, who, x, y, age, view, pose, ph, expr, arms, int(round(sc)), flip, None, tint, alpha, shade); return
    im = pix.char_img(who, age, view, pose, ph % 4, expr, arms, None, tint)
    if shade:
        a = np.array(im); a[..., :3] = np.clip(a[..., :3] * np.array(shade), 0, 255).astype(np.uint8); im = Image.fromarray(a)
    ax = pix.CX
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT); ax = pix.CW - 1 - pix.CX
    w, h = max(1, int(round(pix.CW * sc))), max(1, int(round(pix.CH * sc)))
    im = im.resize((w, h), Image.NEAREST)
    if alpha < 1: im = with_alpha(im, alpha)
    img.paste(im, (int(round(x - ax * sc)), int(round(y - pix.FY * sc))), im)


def ghost(img, who, x, y, s, a, age='young', view='side', pose='stand', expr='smile', flip=False, tint=None, ph=0, arms='auto'):
    """点阵半透明的人（回忆、消失）"""
    if a <= 0: return
    im = pix.char_img(who, age, view, pose, ph % 4, expr, arms, None, tint)
    ax = pix.CX
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT); ax = pix.CW - 1 - pix.CX
    if s != 1: im = im.resize((pix.CW * s, pix.CH * s), Image.NEAREST)
    dpaste(img, im, x - ax * s, y - pix.FY * s, a)


def head_img(who, age='young', expr='smile', s=1, view='front'):
    im = pix.char_img(who, age, view, 'stand', 0, expr)
    return im.crop((pix.CX - 8, pix.FY - 31, pix.CX + 8, pix.FY - 13)).resize((16 * s, 18 * s), Image.NEAREST)


# ---------------------------------------------------------------- 烟
def puff(img, x, y, r, col, a=1.0, shade=None):
    """一团点阵半透明的烟"""
    if a <= 0 or r < 0.6: return
    x0, y0 = max(0, int(x - r - 1)), max(0, int(y - r - 1))
    x1, y1 = min(W, int(x + r) + 2), min(H, int(y + r) + 2)
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    inside = ((xx - x) ** 2 + (yy - y) ** 2) < r * r
    blend_box(img, (x0, y0, x1, y1), col, inside * a, levels=6)
    if shade:
        low = inside & (((xx - x + r * 0.2) ** 2 + (yy - y + r * 0.35) ** 2) > (r * 0.92) ** 2)
        blend_box(img, (x0, y0, x1, y1), shade, low * a * 0.8, levels=6)


def smoke(img, x, y, T, n=8, col=(214, 210, 214), shade=(160, 156, 170), vx=-50, vy=-12, life=2.4, r0=2.5, r1=14, seed=0, a=1.0,
          wob=4):
    """从 (x, y) 冒出来、往 (vx, vy) 方向飘、越飘越大越淡的烟"""
    for i in range(n):
        r_ = rng(i * 19 + seed)
        ph = ((T / life) + i / n + r_.random() * 0.05) % 1
        px = x + vx * ph * life + wob * math.sin(T * 1.7 + i * 2.1) * ph
        py = y + vy * ph * life + wob * 0.6 * math.cos(T * 1.3 + i) * ph
        rr = lerp(r0, r1, ph ** 0.7) * r_.uniform(0.8, 1.15)
        puff(img, px, py, rr, col, a * clamp((1 - ph) * 1.4) * clamp(ph * 12), shade)


# ---------------------------------------------------------------- 铁轨
def rails(d, y, off, col=(70, 60, 64), sleeper=(96, 74, 60), x0=0, x1=W, gap=10, rail_hi=None):
    """侧面看的铁轨：一排枕木和一根钢轨；off 是滚动量"""
    for x in range(int(x0 - (off % gap)), int(x1), gap):
        d.rectangle([x, y + 1, x + 5, y + 3], fill=sleeper)
    d.line([(x0, y), (x1, y)], fill=col)
    if rail_hi: d.line([(x0, y - 1), (x1, y - 1)], fill=rail_hi)
    d.line([(x0, y + 4), (x1, y + 4)], fill=lerpc(sleeper, (0, 0, 0), 0.4))


# ---------------------------------------------------------------- 旧铁皮火车（侧面，车头朝右）
def wheel(d, x, y, r, ph, col=(44, 38, 46), hub=(150, 140, 140)):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    if r >= 3:
        d.ellipse([x - r + 1, y - r + 1, x + r - 1, y + r - 1], outline=lerpc(col, hub, 0.5))
        for k in range(2):
            a = ph + k * math.pi / 2
            d.line([(x - math.cos(a) * (r - 1), y - math.sin(a) * (r - 1)), (x + math.cos(a) * (r - 1), y + math.sin(a) * (r - 1))],
                   fill=lerpc(col, hub, 0.6))
    d.point((x, y), fill=hub)


CAR_L, LOCO_L = 112, 92


def train_len(cars, s=1, loco=True):
    return (LOCO_L * loco + cars * (CAR_L + 4)) * s


def train(img, d, x, base, T, cars=3, s=1, night=0.0, lit=0.0, seed=0, loco=True, people=True, roll=None, moss=0.0, hero=None,
          body=TIN, body_s=TIN_S, body_l=TIN_L, rust=1.0, tint_win=None, empty_seat=None, headlight=None):
    """x 是车头最前端，base 是轨道（车轮底）的高度。night 让车身变暗，lit 点亮车窗。
    hero=(车厢号, 窗号) 那扇窗里坐着他；moss 0..1 让车身爬满青苔。返回 [(窗中心x, 窗中心y), ...]"""
    S = lambda v: v * s
    roll = (x / S(4.5)) if roll is None else roll
    dk = lambda c: lerpc(c, (18, 18, 40), 0.55 * night)
    top, bot = base - S(50), base - S(10)
    wins = []
    cream, cream_d = dk((236, 224, 190)), dk((196, 180, 150))
    under = dk((40, 36, 44))
    rr = rng(seed)
    xc = x
    if loco:
        x0 = x - S(LOCO_L)
        # 车头：后面是驾驶室，前面是低一点的引擎盖和圆鼻子
        cab1 = x0 + S(36)
        d.rectangle([x0, top, cab1, bot], fill=dk(body))
        d.rectangle([x0, top, cab1, top + S(3)], fill=dk(body_s))
        d.rectangle([x0 - S(2), top - S(3), cab1 + S(2), top], fill=dk(body_s))
        d.rectangle([cab1, top + S(14), x - S(14), bot], fill=dk(body))
        d.rectangle([cab1, top + S(14), x - S(14), top + S(16)], fill=dk(body_l))
        d.pieslice([x - S(28), top + S(14), x, bot + S(14)], 270, 360, fill=dk(body))
        d.rectangle([x - S(14), top + S(28), x, bot], fill=dk(body))
        # 烟囱
        cx = x - S(30)
        d.rectangle([cx - S(4), top + S(2), cx + S(4), top + S(14)], fill=dk((52, 48, 56)))
        d.rectangle([cx - S(6), top, cx + S(6), top + S(3)], fill=dk((66, 60, 70)))
        # 驾驶室窗
        wx0, wy0 = x0 + S(8), top + S(8)
        wc = lerpc(dk((170, 200, 210)), (255, 212, 140), lit)
        d.rectangle([wx0, wy0, wx0 + S(20), wy0 + S(13)], fill=wc)
        if lit > 0.3: glow(img, wx0 + S(10), wy0 + S(6), S(18), (255, 200, 120), 0.25 * lit)
        else: d.line([(wx0 + S(3), wy0 + S(12)), (wx0 + S(12), wy0 + S(1))], fill=lerpc(wc, (255, 255, 255), 0.4))
        # 腰线、铆钉、锈
        d.rectangle([x0, top + S(26), x - S(4), top + S(29)], fill=cream)
        d.rectangle([x0, top + S(29), x - S(4), top + S(29)], fill=cream_d)
        for k in range(int(S(LOCO_L) // S(7))):
            px = x0 + S(3) + k * S(7)
            if px < x - S(8): d.point((px, bot - S(3)), fill=dk(body_l))
        if rust > 0:
            for _ in range(5):
                rx_, ry_ = rr.uniform(x0 + S(4), x - S(20)), rr.uniform(top + S(31), bot - S(4))
                d.rectangle([rx_, ry_, rx_ + S(rr.randint(2, 5)), ry_ + S(rr.randint(1, 3))], fill=dk(RUST if rr.random() < 0.6 else RUST_D))
        # 排障器和车灯
        d.polygon([(x - S(2), bot), (x + S(6), base - S(2)), (x - S(10), base - S(2))], fill=dk((60, 54, 60)))
        hx, hy = x - S(4), top + S(21)
        hl = night if headlight is None else headlight
        d.ellipse([hx - S(3), hy - S(3), hx + S(3), hy + S(3)], fill=lerpc((230, 220, 180), (255, 250, 220), hl))
        if hl > 0.05:
            glow(img, hx, hy, S(20), (255, 236, 170), 0.55 * hl)
            tfill(img, 'polygon', [(hx, hy - S(2)), (hx + S(130), hy - S(18)), (hx + S(130), hy + S(26)), (hx, hy + S(2))], (255, 236, 170),
                  0.13 * hl)
        d.rectangle([x0, bot, x - S(4), bot + S(4)], fill=under)
        for wx in (x0 + S(14), x0 + S(30), x - S(36), x - S(20)):
            wheel(d, wx, base - S(5), S(5), roll)
        xc = x0 - S(4)
        d.rectangle([xc, bot - S(6), xc + S(4), bot - S(3)], fill=under)
    for c in range(cars):
        x1c = xc; x0c = xc - S(CAR_L)
        if x1c < -10 or x0c > W + 10:
            xc = x0c - S(4); continue
        d.rectangle([x0c, top + S(2), x1c, bot], fill=dk(body))
        d.rounded_rectangle([x0c - S(1), top - S(2), x1c + S(1), top + S(4)], max(1, int(S(3))), fill=dk(body_s))
        d.rectangle([x0c, top + S(26), x1c, top + S(29)], fill=cream)
        d.rectangle([x0c, top + S(29), x1c, top + S(29)], fill=cream_d)
        for k in range(6):
            wx = x0c + S(9) + k * S(17); wy = top + S(9)
            wcen = (wx + S(5.5), wy + S(5.5))
            wins.append(wcen)
            if tint_win: wc = tint_win
            else: wc = lerpc(dk((172, 204, 214)), (255, 214, 140), lit)
            d.rectangle([wx, wy, wx + S(11), wy + S(11)], fill=wc)
            d.rectangle([wx, wy, wx + S(11), wy], fill=dk(body_s))
            is_hero = hero is not None and hero == (c, k)
            r2 = rng(seed * 100 + c * 10 + k)
            if is_hero:
                # 她：侧脸朝外、披长发、红大衣
                hx_, hy_ = wx + S(5), wy + S(6)
                d.rectangle([hx_ - S(4), hy_ - S(4), hx_ + S(1), wy + S(9)], fill=(58, 36, 40))
                d.rectangle([hx_ - S(3), hy_ + S(3), hx_ + S(4), wy + S(11)], fill=dk((214, 62, 70)))
                d.ellipse([hx_ - S(3), hy_ - S(4), hx_ + S(3), hy_ + S(2)], fill=SKIN)
                d.rectangle([hx_ - S(3), hy_ - S(5), hx_ + S(2), hy_ - S(2)], fill=(58, 36, 40))
                d.point((hx_ + S(2), hy_ - S(1)), fill=pix.EYE)
            elif people and r2.random() < 0.45 and not (empty_seat and empty_seat == (c, k)):
                hx_, hy_ = wx + S(r2.uniform(3, 8)), wy + S(6)
                sil = lerpc(wc, (30, 26, 40), 0.75)
                d.ellipse([hx_ - S(2.5), hy_ - S(3), hx_ + S(2.5), hy_ + S(2)], fill=sil)
                d.rectangle([hx_ - S(4), hy_ + S(2), hx_ + S(4), wy + S(11)], fill=sil)
            if lit < 0.3: d.line([(wx + S(2), wy + S(10)), (wx + S(9), wy + S(2))], fill=lerpc(wc, (255, 255, 255), 0.35))
            if lit > 0.4 and S(1) >= 0.9: glow(img, wcen[0], wcen[1] + S(2), S(10), (255, 200, 120), 0.12 * lit)
        for k in range(int(S(CAR_L) // S(7))):
            d.point((x0c + S(3) + k * S(7), bot - S(3)), fill=dk(body_l))
            d.point((x0c + S(3) + k * S(7), top + S(5)), fill=dk(body_l))
        if rust > 0:
            for _ in range(6):
                rx_, ry_ = rr.uniform(x0c + S(4), x1c - S(8)), rr.uniform(top + S(31), bot - S(4))
                d.rectangle([rx_, ry_, rx_ + S(rr.randint(2, 6)), ry_ + S(rr.randint(1, 3))], fill=dk(RUST if rr.random() < 0.6 else RUST_D))
            for _ in range(2):
                rx_ = rr.uniform(x0c + S(4), x1c - S(8))
                d.line([(rx_, top + S(30)), (rx_ + S(1), bot - S(2))], fill=dk(RUST_D))
        d.rectangle([x0c + S(4), bot, x1c - S(4), bot + S(4)], fill=under)
        for bx in (x0c + S(20), x1c - S(20)):
            d.rectangle([bx - S(10), bot + S(2), bx + S(10), bot + S(5)], fill=lerpc(under, (0, 0, 0), 0.3))
            wheel(d, bx - S(6), base - S(5), S(5), roll)
            wheel(d, bx + S(6), base - S(5), S(5), roll)
        if moss > 0:
            mr = rng(seed * 7 + c)
            for k in range(int(40 * moss)):
                mx = mr.uniform(x0c, x1c); my = top - S(2) + mr.uniform(0, S(5))
                d.ellipse([mx - S(3), my - S(2), mx + S(3), my + S(2)], fill=MOSS if k % 3 else MOSS_D)
            for k in range(int(30 * moss)):
                mx = mr.uniform(x0c, x1c); my = bot - mr.uniform(0, S(14)) * moss
                d.ellipse([mx - S(3), my - S(2), mx + S(3), my + S(3)], fill=[MOSS, MOSS_D, MOSS_L][k % 3])
            for k in range(int(8 * moss)):                    # 垂下来的藤
                mx = mr.uniform(x0c + S(6), x1c - S(6)); ln = mr.uniform(S(6), S(22)) * moss
                d.line([(mx, top), (mx + math.sin(T + k) * 0.6, top + ln)], fill=MOSS_D)
                d.point((mx, top + ln * 0.6), fill=MOSS_L)
        xc = x0c - S(4)
        if c < cars - 1: d.rectangle([xc, bot - S(6), xc + S(4), bot - S(3)], fill=under)
    return wins


# ---------------------------------------------------------------- 30 路公交（侧面，车头朝右）
# ---------------------------------------------------------------- 收音机、卡带、吉他
def clock(d, cx, cy, r, hour, minute, rim=(120, 84, 50), face=(250, 240, 214), hand=(40, 30, 40), ticks=True):
    """钟面：hour/minute 是指针角度（弧度，0 朝上，顺时针）"""
    d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill=OUT)
    d.ellipse([cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1], fill=rim)
    d.ellipse([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2], fill=face)
    if ticks:
        for k in range(12):
            a = k * math.pi / 6
            r0 = r - (6 if k % 3 == 0 else 4)
            d.line([(cx + math.sin(a) * r0, cy - math.cos(a) * r0), (cx + math.sin(a) * (r - 3), cy - math.cos(a) * (r - 3))], fill=hand)
    d.line([(cx, cy), (cx + math.sin(hour) * r * 0.5, cy - math.cos(hour) * r * 0.5)], fill=hand, width=max(1, int(r / 14)))
    d.line([(cx, cy), (cx + math.sin(minute) * r * 0.8, cy - math.cos(minute) * r * 0.8)], fill=hand, width=max(1, int(r / 22)))
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(200, 60, 50))


# ---------------------------------------------------------------- 纸船、灯笼
# ---------------------------------------------------------------- 片名
@lru_cache(None)
def big_glyph(ch, scale=3, top=(255, 252, 240), bot=(255, 196, 120), line=(196, 96, 70), out=(46, 26, 40), font=None):
    font = font or FONT
    w = int(font.getlength(ch)) + 8; h = font.size + 8
    m = Image.new('L', (w, h)); md = ImageDraw.Draw(m); md.fontmode = '1'
    md.text((4, 3), ch, font=font, fill=255)
    mk = np.array(m) > 0
    a = np.zeros((h, w, 4), np.uint8)
    for y in range(h): a[y, :, :3] = lerpc(top, bot, (y - 4) / (font.size - 1))
    a[..., 3] = mk * 255
    im = outline(outline(Image.fromarray(a), line), out)
    sh = Image.new('RGBA', (w + 1, h + 1))
    shadow = np.array(im); shadow[shadow[..., 3] > 0, :3] = out
    sh.paste(Image.fromarray(shadow), (1, 1)); sh.alpha_composite(im)
    return sh.resize((sh.width * scale, sh.height * scale), Image.NEAREST)


def title_str():
    return pix.META.get('ti') or '爱错'


def artist_str():
    return pix.META.get('ar') or ''


def title_layout(scale, gap=0):
    s = title_str()
    adv = [FONT.getlength(c) * scale + gap for c in s]
    return s, adv, sum(adv)


def big_text(img, s, cx, cy, scale, alpha=1.0, gap=0, **kw):
    gl = [big_glyph(c, scale, **kw) for c in s]
    adv = [FONT.getlength(c) * scale + gap for c in s]
    x = cx - sum(adv) / 2 - 4 * scale
    for g, a in zip(gl, adv):
        dpaste(img, g, x, cy - g.height / 2, alpha)
        x += a


# ---------------------------------------------------------------- 拍立得、调色
def polaroid(img, d, cx, cy, photo, f=1.0, alpha=1.0, rot=0, frame=CREAM):
    """拍立得：photo 是 RGB 图，f 从 0 到 1 显影"""
    if alpha <= 0: return
    pw, ph = photo.size
    im = Image.new('RGBA', (pw + 8, ph + 18), frame + (255,))
    p = photo
    if f < 1:
        a = np.asarray(p, float); g = a @ np.array([0.3, 0.59, 0.11])
        dev = np.clip(f * 1.4, 0, 1)
        a = (a * dev + (g[..., None] * 0.3 + 40) * (1 - dev)) * (0.4 + 0.6 * dev)
        p = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    im.paste(p, (4, 4))
    im = outline(im, OUT)
    if rot: im = im.rotate(rot, resample=Image.NEAREST, expand=True)
    paste(img, im, cx, cy, alpha, 'cc')


def shrink(im, w, h):
    """把整帧缩成小图：按块取平均，保留像素感"""
    return im.resize((w, h), Image.BOX)


def sepia(im, k=1.0, warm=(1.08, 0.94, 0.74)):
    a = np.asarray(im, float)
    g = a @ np.array([0.3, 0.59, 0.11])
    s = np.stack([g * warm[0], g * warm[1], g * warm[2]], -1) + np.array([18, 10, 0])
    a = a * (1 - k) + s * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def grain(img, T, a=10, seed=0):
    r = np.random.default_rng(int(T * 30) * 7 + seed)
    n = r.integers(-a, a + 1, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    arr = np.asarray(img, np.int16) + n
    img.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)))


# ---------------------------------------------------------------- 粒子
BOKEH_COLS = [GOLD, PINK, CYAN, (160, 130, 255), (255, 220, 170)]


def bokeh(img, T, n=14, cols=BOKEH_COLS, seed=0, a=0.3, rmin=8, rmax=22, drift=6, box=(0, 0, W, H)):
    """虚焦的光斑，慢慢漂"""
    x0, y0, x1, y1 = box
    for i in range(n):
        r = rng(i * 17 + seed)
        x = x0 + (r.uniform(0, x1 - x0) + T * drift * r.uniform(-1, 1)) % (x1 - x0)
        y = y0 + r.uniform(0, y1 - y0) + 4 * math.sin(T * 0.7 + i)
        rad = r.uniform(rmin, rmax)
        glow(img, x, y, rad, cols[i % len(cols)], a * (0.6 + 0.4 * math.sin(T * 1.3 + i * 2)), power=0.7)


def leaves(d, t, n=30, speed=24, wind=40, seed=0, cols=((214, 140, 60), (190, 96, 50), (236, 186, 90)), box=(0, -10, W, H)):
    pix.petals(d, t, n, cols, speed, wind, box[0], box[2], box[1], box[3], seed)


# ---------------------------------------------------------------- 雨、倒影
def reflect(img, y0, h, t, tint=(14, 12, 40), a=0.5, amp=2.0, src_h=None):
    """水面/湿地面：把 y0 以上的画面倒过来贴到下面，每行左右抖一点，再压一层颜色"""
    src_h = src_h or h
    arr = np.asarray(img)
    top = arr[max(0, y0 - src_h):y0][::-1]
    n = min(h, len(top), H - y0)
    if n <= 0: return
    out = top[:n].copy()
    for r in range(n):
        sh = int(round(amp * math.sin(t * 3 + r * 0.7) * (0.3 + r / n)))
        if sh: out[r] = np.roll(out[r], sh, axis=0)
    under = arr[y0:y0 + n].astype(float)
    k = np.linspace(0.55, 0.15, n)[:, None, None] * a / 0.5
    al = np.clip(np.floor(k * 6 + pix.bayer(n, W, 0, y0)[..., None]) / 6, 0, 1)
    mix = under * (1 - al) + (out.astype(float) * 0.75 + np.array(tint) * 0.25) * al
    img.paste(Image.fromarray(mix.round().astype(np.uint8)), (0, y0))


def splashes(d, t, y0, y1, n, col=(150, 170, 230), seed=0, x0=0, x1=W):
    """雨点打在地上的小水花"""
    for i in range(n):
        r = rng(i * 13 + seed)
        per = 0.5 + r.random() * 0.4
        k = ((t + r.random() * per) % per) / per
        if k > 0.45: continue
        x = r.uniform(x0, x1); y = r.uniform(y0, y1)
        s = 1 + int(k * 6)
        d.point([(x - s, y), (x + s, y)], fill=col)
        if k < 0.2: d.point((x, y - 1), fill=col)


def ripples(d, t, box, n, col, seed=0, per=1.2, rmax=8):
    """水面上一圈圈扩散的涟漪"""
    x0, y0, x1, y1 = box
    for i in range(n):
        r = rng(i * 31 + seed)
        p = per * r.uniform(0.7, 1.3)
        k = ((t + r.random() * p) % p) / p
        x = r.uniform(x0, x1); y = r.uniform(y0, y1)
        rr = 1 + k * rmax
        d.ellipse([x - rr, y - rr * 0.4, x + rr, y + rr * 0.4], outline=lerpc(col, (0, 0, 0), k * 0.8))


def drops_on_glass(img, d, t, box, n=40, seed=0, col=(180, 200, 255)):
    """玻璃上的雨珠，慢慢往下滑"""
    x0, y0, x1, y1 = box
    for i in range(n):
        r = rng(i * 7 + seed)
        sp = r.uniform(4, 30)
        x = r.uniform(x0, x1); y = y0 + (r.uniform(0, y1 - y0) + t * sp) % (y1 - y0)
        d.point((x, y), fill=col)
        if sp > 18: d.line([(x, y - 3), (x, y - 1)], fill=lerpc(col, (40, 40, 80), 0.6))
        if i % 3 == 0: d.point((x + 1, y), fill=lerpc(col, (255, 255, 255), 0.5))


SNAP = None    # render.py 填入：SNAP(T) 返回全片 T 秒处的画面（不含字幕）


# ---------------------------------------------------------------- 特写的大脸（24×22 的字符画，五官按表情现画）
FACE = {
    'boy': ["......H.HHHHH.H.........",
            ".....HHHHHHHHHHHHH......",
            "....HHHLLLHHHHHHHHHH....",
            "...HHHLLHHHHHHHHHHHHH...",
            "..HHHHHHHHHHHHHHHHHHHH..",
            "..HHHHHHHHHHHHHHHHHHHHH.",
            ".HHHHHHHHHHHHHHHHHHHHHH.",
            ".HHHHHhHHHHhHHHHHhHHHHH.",
            ".HHHhSSSHHSSSSHHSSShHHH.",
            ".HHhSSSSSSSSSSSSSSSShHH.",
            ".HHSSSSSSSSSSSSSSSSSSHH.",
            ".HSSSSSSSSSSSSSSSSSSSSH.",
            ".hSSSSSSSSSSSSSSSSSSSSh.",
            "..SSSSSSSSSSSSSSSSSSSS..",
            "..SSSSSSSSSSSSSSSSSSSS..",
            "..SSSSSSSSSSSSSSSSSSSS..",
            "..sSSSSSSSSSSSSSSSSSSs..",
            "...SSSSSSSSSSSSSSSSSS...",
            "...sSSSSSSSSSSSSSSSSs...",
            "....sSSSSSSSSSSSSSSs....",
            ".....ssSSSSSSSSSSss.....",
            ".......ssssssssss......."],
    'girl': ["........HHHHHHHH........",
             ".....HHHHHHHHHHHHHH.....",
             "....HHHLLLHHHHHHHHHHA...",
             "...HHHLLHHHHHHHHHHHAAA..",
             "..HHHHHHHHHHHHHHHHHHAH..",
             "..HHHHHHHHHHHHHHHHHHHHH.",
             ".HHHHHHHHHHHHHHHHHHHHHH.",
             ".HHHHHHHHHHhHHHHHHHHHHH.",
             ".HHHHSSSHHSSSSSHHSSSHHH.",
             ".HHHSSSSSSSSSSSSSSSSSHH.",
             ".HHSSSSSSSSSSSSSSSSSSHH.",
             ".HHSSSSSSSSSSSSSSSSSSHH.",
             ".HHSSSSSSSSSSSSSSSSSSHH.",
             ".HHSSSSSSSSSSSSSSSSSSHH.",
             ".HHSSSSSSSSSSSSSSSSSSHH.",
             ".HHSSSSSSSSSSSSSSSSSSHH.",
             ".HHsSSSSSSSSSSSSSSSSsHH.",
             ".HHHSSSSSSSSSSSSSSSSHHH.",
             ".HHHsSSSSSSSSSSSSSSsHHH.",
             ".HHHHsSSSSSSSSSSSSsHHHH.",
             ".HHHHHssSSSSSSSSssHHHHH.",
             ".hHHHH.ssssssssss.HHHHh."],
}
FACE_EYES = ((6, 13), (16, 13))
FACE_MOUTH = (11, 18)


@lru_cache(None)
def face(who, expr='smile', s=4, age='young'):
    """特写用的大脸，返回 RGBA。expr: smile happy laugh sad closed cry surprised neutral sing cough drunk half"""
    L = pix.LOOK[(who, age)]
    rows = [list(r) for r in FACE[who]]
    pal = {'H': L['hair'], 'h': L['hair_s'], 'L': L['hair_l'], 'S': SKIN, 's': SKIN_S, 'A': L.get('acc') or L['hair']}
    w, h = 24, len(rows)
    im = Image.new('RGBA', (w, h)); px = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.': px[x, y] = pal[ch] + (255,)
    E, Wt, M, B = pix.EYE, (255, 255, 255), pix.MOUTH, pix.BLUSH

    def P(x, y, c):
        if 0 <= x < w and 0 <= y < h: px[x, y] = c + (255,)
    for k, (ex, ey) in enumerate(FACE_EYES):
        inner = 1 if k == 0 else -1
        if expr in ('happy', 'laugh', 'sing'):
            P(ex - 1, ey + 1, E); P(ex, ey, E); P(ex + 1, ey, E); P(ex + 2, ey + 1, E)
        elif expr in ('closed', 'cry', 'cough', 'drunk'):
            P(ex - 1, ey, E); P(ex, ey + 1, E); P(ex + 1, ey + 1, E); P(ex + 2, ey, E)
            if expr == 'cough': P(ex + (2 if k == 0 else -1), ey - 2, L['hair_s']); P(ex + (1 if k == 0 else 0), ey - 3, L['hair_s'])
        elif expr == 'half':                                   # 半睁的眼
            P(ex - 1, ey, E); P(ex, ey, E); P(ex + 1, ey, E); P(ex + 2, ey, E); P(ex, ey + 1, E); P(ex + 1, ey + 1, E)
        else:
            tall = 3 if expr == 'surprised' else 2
            for yy in range(ey - (1 if expr == 'surprised' else 0), ey + tall - (1 if expr == 'surprised' else 0)):
                P(ex, yy, E); P(ex + 1, yy, E)
            P(ex + (1 if k == 0 else 0), ey - (1 if expr == 'surprised' else 0), Wt)
            if expr == 'sad':
                bx = ex + (1 if k == 0 else 0)
                P(bx + inner, ey - 4, L['hair_s']); P(bx, ey - 3, L['hair_s'])
    for cx in (4, 18):
        if expr in ('smile', 'happy', 'laugh', 'cry', 'sing', 'drunk'):
            P(cx, 16, B); P(cx + 1, 16, B)
            if expr == 'drunk': P(cx, 15, B); P(cx + 1, 15, B); P(cx + 2, 16, B); P(cx - 1, 16, B)
    mx, my = FACE_MOUTH
    if expr in ('smile', 'half'):
        P(mx - 1, my, M); P(mx, my + 1, M); P(mx + 1, my + 1, M); P(mx + 2, my, M)
    elif expr in ('happy', 'laugh'):
        for x in range(mx - 1, mx + 3): P(x, my, E)
        for x in range(mx, mx + 2): P(x, my + 1, M)
        if expr == 'laugh': P(mx - 1, my + 1, M); P(mx + 2, my + 1, M); P(mx, my + 2, M); P(mx + 1, my + 2, M)
    elif expr == 'sing':
        P(mx, my, E); P(mx + 1, my, E); P(mx - 1, my + 1, E); P(mx + 2, my + 1, E); P(mx, my + 1, M); P(mx + 1, my + 1, M)
        P(mx, my + 2, E); P(mx + 1, my + 2, E)
    elif expr in ('sad', 'cry'):
        P(mx, my, E); P(mx + 1, my, E); P(mx - 1, my + 1, E); P(mx + 2, my + 1, E)
    elif expr == 'surprised':
        P(mx, my, E); P(mx + 1, my, E); P(mx, my + 1, M); P(mx + 1, my + 1, M)
    elif expr == 'cough':
        P(mx, my, E); P(mx + 1, my, E); P(mx - 1, my + 1, E); P(mx + 2, my + 1, E); P(mx, my + 1, (90, 40, 50)); P(mx + 1, my + 1, (90, 40, 50))
    elif expr == 'drunk':
        P(mx - 1, my, M); P(mx, my + 1, M); P(mx + 1, my + 1, M); P(mx + 2, my, M); P(mx + 3, my - 1, M)
    else:
        P(mx, my, M); P(mx + 1, my, M)
    im = outline(im, OUT)
    return im.resize((im.width * s, im.height * s), Image.NEAREST)


def bust(img, d, who, cx, top, s=4, expr='smile', age='young', wind=0.0, T=0.0):
    """特写：头和肩膀。(cx, top) 是头顶中点；返回 (左眼, 右眼) 的屏幕坐标"""
    L = pix.LOOK[(who, age)]
    f = face(who, expr, s, age)
    x0 = cx - f.width / 2
    nb = top + 21 * s
    coat, coat_s = L['top'], L['top_s']
    d.rectangle([cx - 3 * s, nb - s, cx + 3 * s, nb + 3 * s], fill=SKIN_S)
    sh_poly = [(cx - 7 * s, nb + 1 * s), (cx + 7 * s, nb + 1 * s), (cx + 15 * s, nb + 5 * s), (cx + 18 * s, nb + 10 * s), (cx + 18 * s, H + 40),
               (cx - 18 * s, H + 40), (cx - 18 * s, nb + 10 * s), (cx - 15 * s, nb + 5 * s)]
    d.polygon([(x + (1 if x > cx else -1), y - 1) for x, y in sh_poly], fill=OUT)
    d.polygon(sh_poly, fill=coat)
    if who == 'girl':
        d.ellipse([cx - 6 * s, nb + 1 * s, cx + 6 * s, nb + 6 * s], fill=L['collar'])
        d.ellipse([cx - 4 * s, nb + 1 * s, cx + 4 * s, nb + 4 * s], fill=SKIN_S)
        for hx in (cx - 12 * s, cx + 9 * s):
            d.rounded_rectangle([hx, nb - 2 * s, hx + 3 * s, nb + 12 * s], s, fill=L['hair'])
    else:
        d.line([(cx - 6 * s, nb + 6 * s), (cx - 2 * s, H)], fill=coat_s, width=max(1, s // 2))
        d.line([(cx + 6 * s, nb + 6 * s), (cx + 2 * s, H)], fill=coat_s, width=max(1, s // 2))
        if L.get('scarf'):
            sc, scs = L['scarf'], ICE_S
            d.rounded_rectangle([cx - 9 * s, nb, cx + 9 * s, nb + 6 * s], 2 * s, fill=sc)
            d.line([(cx - 8 * s, nb + 5 * s), (cx + 8 * s, nb + 5 * s)], fill=scs)
            fl = wind * math.sin(T * 8) * 2 * s
            d.polygon([(cx + 3 * s, nb + 5 * s), (cx + 7 * s, nb + 5 * s), (cx + 8 * s + fl + wind * 10 * s, nb + 16 * s - wind * 6 * s),
                       (cx + 4 * s + fl + wind * 10 * s, nb + 16 * s - wind * 6 * s)], fill=sc)
            for k in range(3):
                d.point((cx + 4 * s + k * s + fl + wind * 10 * s, nb + 16 * s - wind * 6 * s), fill=scs)
    img.paste(f, (int(round(x0)), int(round(top))), f)
    return [(x0 + (ex + 0.5) * s, top + (ey + 2) * s) for ex, ey in FACE_EYES]
