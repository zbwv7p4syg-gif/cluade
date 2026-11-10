"""我好想你 · 通用道具：节拍、点阵贴图和镜头、烟、火车、钟、片名大字、拍立得、特写的大脸、雨和倒影，
以及这支 MV 新加的：点阵明暗的灯光、任意倍数的推拉镜头、对话泡泡、心、俯视的卧室和窗。

从 aicuo/props.py 复制而来；火车窗里坐的换成了围红围巾的"你"。
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

import pix
from pix import (W, H, FONT, FONT_S, OUT, SKIN, SKIN_S, ICE, ICE_S, clamp, lerp, lerpc, ease, eout, ein, eback, span, glow,
                 tfill, blend_box, paste, outline, text, rng, sky, stars, rain, city, lamp, with_alpha, heart_poly, person)

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
                d.rectangle([hx_ - S(4), hy_ - S(4), hx_ + S(1), wy + S(9)], fill=(126, 78, 52))
                d.rectangle([hx_ - S(3), hy_ + S(3), hx_ + S(4), wy + S(11)], fill=dk((248, 204, 88)))
                d.rectangle([hx_ - S(3), hy_ + S(3), hx_ + S(4), hy_ + S(4)], fill=(222, 60, 68))
                d.ellipse([hx_ - S(3), hy_ - S(4), hx_ + S(3), hy_ + S(2)], fill=SKIN)
                d.rectangle([hx_ - S(3), hy_ - S(5), hx_ + S(2), hy_ - S(2)], fill=(126, 78, 52))
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
    return pix.META.get('ti') or '我好想你'


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


def bust(img, d, who, cx, top, s=4, expr='smile', age='young', wind=0.0, T=0.0, scarf=None):
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
        for hx in (cx - 12 * s, cx + 9 * s):
            d.rounded_rectangle([hx, nb - 2 * s, hx + 3 * s, nb + 12 * s], s, fill=L['hair'])
        d.rounded_rectangle([cx - 9 * s, nb, cx + 9 * s, nb + 6 * s], 2 * s, fill=L['scarf'])
        d.line([(cx - 8 * s, nb + 5 * s), (cx + 8 * s, nb + 5 * s)], fill=lerpc(L['scarf'], (0, 0, 0), 0.25))
        d.rectangle([cx + 3 * s, nb + 5 * s, cx + 7 * s, nb + 15 * s], fill=L['scarf'])
    else:
        d.line([(cx - 6 * s, nb + 6 * s), (cx - 2 * s, H)], fill=coat_s, width=max(1, s // 2))
        d.line([(cx + 6 * s, nb + 6 * s), (cx + 2 * s, H)], fill=coat_s, width=max(1, s // 2))
        sc_ = scarf or L.get('scarf')
        if sc_:
            sc, scs = sc_, lerpc(sc_, (0, 0, 0), 0.25)
            d.rounded_rectangle([cx - 9 * s, nb, cx + 9 * s, nb + 6 * s], 2 * s, fill=sc)
            d.line([(cx - 8 * s, nb + 5 * s), (cx + 8 * s, nb + 5 * s)], fill=scs)
            fl = wind * math.sin(T * 8) * 2 * s
            d.polygon([(cx + 3 * s, nb + 5 * s), (cx + 7 * s, nb + 5 * s), (cx + 8 * s + fl + wind * 10 * s, nb + 16 * s - wind * 6 * s),
                       (cx + 4 * s + fl + wind * 10 * s, nb + 16 * s - wind * 6 * s)], fill=sc)
            for k in range(3):
                d.point((cx + 4 * s + k * s + fl + wind * 10 * s, nb + 16 * s - wind * 6 * s), fill=scs)
    img.paste(f, (int(round(x0)), int(round(top))), f)
    return [(x0 + (ex + 0.5) * s, top + (ey + 2) * s) for ex, ey in FACE_EYES]


# ================================================================ 这支 MV 新加的道具
YY, XX = np.mgrid[0:H, 0:W]
SCARF, SCARF_D, SCARF_L = (222, 60, 68), (166, 36, 56), (255, 120, 120)
NIGHT4 = ((0, (8, 8, 28)), (0.4, (18, 18, 52)), (0.75, (34, 30, 78)), (1, (62, 46, 104)))
DAY4 = ((0, (84, 146, 222)), (0.45, (132, 186, 236)), (0.8, (190, 222, 246)), (1, (228, 240, 250)))
DUSK4 = ((0, (62, 70, 140)), (0.42, (190, 112, 136)), (0.75, (250, 162, 120)), (1, (255, 216, 150)))
DAWN4 = ((0, (40, 52, 110)), (0.5, (150, 120, 170)), (0.8, (250, 170, 150)), (1, (255, 220, 170)))


def R(d, x, y, w, h, col):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=col)


def lighting(img, lights, amb=0.2, tint=(0.24, 0.27, 0.5), levels=6, extra=None, power=1.4):
    """点阵明暗：lights = [(cx, cy, r, 强度[, ry])]，没被照到的地方乘上 tint（偏蓝的暗色）。extra 是额外的亮度图"""
    L = np.full((H, W), float(amb))
    for li in lights:
        cx, cy, r, s = li[:4]; ry = li[4] if len(li) > 4 else r
        if s <= 0: continue
        dist = np.sqrt(((XX - cx) / r) ** 2 + ((YY - cy) / ry) ** 2)
        L += s * np.clip(1 - dist, 0, 1) ** power
    if extra is not None: L = np.maximum(L, extra)
    L = np.clip(np.floor(np.clip(L, 0, 1) * levels + pix.BAYER) / levels, 0, 1)[..., None]
    a = np.asarray(img, float)
    t = np.array(tint, float)
    img.paste(Image.fromarray((a * (t + (1 - t) * L)).astype(np.uint8)))


def zoomf(img, s, cx=W / 2, cy=H / 2):
    """任意倍数放大（最近邻），用在很快的推拉镜头上"""
    if s <= 1.001: return
    w, h = W / s, H / s
    x0 = clamp(cx - w / 2, 0, W - w); y0 = clamp(cy - h / 2, 0, H - h)
    img.paste(img.resize((W, H), Image.NEAREST, box=(x0, y0, x0 + w, y0 + h)))


def bubble(img, d, x0, y0, x1, y1, tail=None, col=(252, 250, 244), out=OUT, a=1.0, r=6):
    """对话泡泡；tail=(x, y) 是尖角指向的位置"""
    if a <= 0: return
    if a < 1:
        lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay)
        bubble(lay, ld, x0, y0, x1, y1, tail, col, out, 1.0, r)
        dpaste(img, lay, 0, 0, a); return
    if tail:
        tx, ty = tail; bx = clamp(tx, x0 + r + 4, x1 - r - 4)
        by = y1 if ty > y1 else y0
        d.polygon([(bx - 5, by), (bx + 5, by), (tx, ty)], fill=col, outline=out)
    d.rounded_rectangle([x0, y0, x1, y1], r, fill=col, outline=out)
    if tail: d.line([(bx - 4, by), (bx + 4, by)], fill=col)


def thought(img, d, cx, cy, rx, ry, to=None, col=(252, 250, 244), out=OUT, a=1.0):
    """想象泡泡：一朵云，下面两个小圆点连到 to"""
    if a <= 0: return
    if a < 1:
        lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay)
        thought(lay, ld, cx, cy, rx, ry, to, col, out, 1.0)
        dpaste(img, lay, 0, 0, a); return
    blobs = [(-0.55, -0.3, 0.55), (0.1, -0.5, 0.6), (0.6, -0.15, 0.5), (0.45, 0.4, 0.5), (-0.2, 0.45, 0.55), (-0.65, 0.2, 0.45), (0, 0, 0.8)]
    for pad, c in ((1, out), (0, col)):
        for bx, by, br in blobs:
            d.ellipse([cx + bx * rx - br * rx - pad, cy + by * ry - br * ry - pad, cx + bx * rx + br * rx + pad, cy + by * ry + br * ry + pad], fill=c)
    if to:
        tx, ty = to
        for k, rr in ((0.35, 4), (0.7, 2)):
            px = lerp(cx, tx, k); py = lerp(cy + ry * (1 if ty > cy else -1), ty, k)
            d.ellipse([px - rr - 1, py - rr - 1, px + rr + 1, py + rr + 1], fill=out); d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=col)


def heart(d, cx, cy, s, col=RED, hi=RED_L, out=OUT, crack=0.0, grey=0.0, bandage=False):
    """一颗心，宽约 32·s。crack 0..1 是裂缝的长度，grey 0..1 让它失去颜色"""
    c = lerpc(col, (150, 150, 164), grey); h = lerpc(hi, (200, 200, 212), grey)
    d.polygon(heart_poly(cx, cy, s), fill=c, outline=out)
    if s >= 0.45:
        d.ellipse([cx - 11 * s, cy - 9 * s, cx - 6 * s, cy - 4 * s], fill=h)
    if s >= 0.8: d.polygon(heart_poly(cx, cy, s), outline=out)
    if crack > 0:
        pts = [(cx + 1 * s, cy - 5 * s), (cx - 4 * s, cy + 1 * s), (cx + 3 * s, cy + 5 * s), (cx - 2 * s, cy + 10 * s), (cx + 1 * s, cy + 16 * s)]
        n = crack * (len(pts) - 1)
        for i in range(len(pts) - 1):
            if n <= i: break
            f = min(1, n - i)
            a, b = pts[i], pts[i + 1]
            d.line([a, (lerp(a[0], b[0], f), lerp(a[1], b[1], f))], fill=lerpc(out, (0, 0, 0), 0.2), width=max(1, int(round(s * 1.2))))
    if bandage and s >= 0.6:
        w = 7 * s
        d.polygon([(cx - w, cy + 1 * s), (cx - w + 3 * s, cy - 2 * s), (cx + w, cy + 5 * s), (cx + w - 3 * s, cy + 8 * s)], fill=(244, 226, 196), outline=out)
        d.point((cx, cy + 3 * s), fill=(200, 170, 140))


@lru_cache(None)
def mini(T0, w=64, h=36):
    """全片 T0 秒处的画面缩成一张小图（回忆里的照片、电视里的画面）"""
    return SNAP(T0).resize((w, h), Image.BOX)


def fade_to(im, col, k):
    a = np.asarray(im, float)
    return Image.fromarray((a * (1 - k) + np.array(col, float) * k).astype(np.uint8))


# ---------------------------------------------------------------- 卧室（俯视一点的正面）
WALL, WALL_L, WALL_S = (214, 198, 190), (224, 210, 200), (176, 156, 160)
FLOOR, FLOOR_S, FLOOR_L = (176, 128, 92), (150, 104, 76), (196, 148, 108)
SHEET, SHEET_S = (240, 236, 230), (204, 200, 210)
BLANKET, BLANKET_S, BLANKET_L = (96, 128, 176), (72, 98, 146), (128, 160, 204)
WIN = (322, 20, 84, 66)                    # 窗玻璃 x, y, w, h
LAMP_AT = (282, 76)
BED = (150, 262)


def window(img, d, x, y, w, h, T, stops=NIGHT4, moon_at=None, frame=(240, 236, 228), curtain=(232, 214, 200), open_=0.6, stars_n=16,
           city_col=(24, 26, 60), sun=None):
    img.paste(pix.vgrad(w, h, tuple((p, tuple(c)) for p, c in stops), 5), (x, y))
    r = rng(x * 7 + y)
    for i in range(stars_n):
        sx, sy = x + r.randrange(w), y + r.randrange(int(h * 0.6))
        if math.sin(T * (1 + r.random() * 2) + i) > -0.3: d.point((sx, sy), fill=(230, 230, 255))
    if sun: glow(img, x + sun[0], y + sun[1], sun[2] * 3, (255, 230, 170), 0.6); d.ellipse([x + sun[0] - sun[2], y + sun[1] - sun[2], x + sun[0] + sun[2], y + sun[1] + sun[2]], fill=(255, 244, 200))
    if moon_at: pix.moon(d, x + moon_at[0], y + moon_at[1], moon_at[2])
    if city_col:
        bx = x
        while bx < x + w:
            bw = r.randint(5, 11); bh = r.randint(6, 24)
            d.rectangle([bx, y + h - bh, min(x + w - 1, bx + bw - 1), y + h], fill=city_col)
            for _ in range(2):
                if r.random() < 0.6: d.point((min(x + w - 1, bx + r.randrange(bw)), y + h - r.randrange(bh)), fill=(255, 210, 130))
            bx += bw
    d.rectangle([x - 3, y - 3, x + w + 2, y + h + 2], outline=frame, width=3)
    d.rectangle([x + w // 2 - 1, y, x + w // 2, y + h], fill=frame); d.rectangle([x, y + h // 2 - 1, x + w, y + h // 2], fill=frame)
    d.rectangle([x - 6, y + h + 3, x + w + 5, y + h + 6], fill=frame); d.line([(x - 6, y + h + 7), (x + w + 5, y + h + 7)], fill=WALL_S)
    d.rectangle([x - 12, y - 9, x + w + 11, y - 7], fill=(150, 110, 90))
    cw = int(w * (1 - open_) / 2 + 8)
    for side in (0, 1):
        cx0 = x - 9 if side == 0 else x + w + 9 - cw
        d.rectangle([cx0, y - 6, cx0 + cw, y + h + 12], fill=curtain)
        for fx in range(cx0 + 2, cx0 + cw, 4):
            d.line([(fx, y - 6), (fx + round(math.sin(T * 1.2 + fx) * 0.7), y + h + 12)], fill=lerpc(curtain, (0, 0, 0), 0.14))


@lru_cache(None)
def _moon_patch():
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).polygon([(330, 150), (400, 150), (372, 236), (286, 236)], fill=120)
    return np.asarray(m, float) / 255


def room(img, d, T, me='sit', lamp=1.0, expr='down', eyes=False, ghost_sit=0.0, ghost_lie=0.0, stops=NIGHT4, moon_on=True, scarf=True,
         day=0.0, curtain_open=0.6, sun=None, me_x=180, me_view='front', me_pose='sit', me_arms='auto', me_scarf=None, me_ph=0, me_y=209,
         me_flip=False):
    """卧室：靠墙的大床、两个床头柜、台灯、窗、衣柜、书桌、挂着红围巾的衣帽架。
    me: sit=坐在床沿 lie=躺在床的左半边 free=按 me_x/me_view/me_pose 站在屋里 none=不在。
    lamp 0..1 台灯；day 0..1 天亮的程度（片尾）。ghost_sit/ghost_lie 是"你"的影子"""
    d.rectangle([0, 0, W, 112], fill=WALL)
    for x in range(10, W, 22): d.line([(x, 0), (x, 105)], fill=WALL_L)
    d.rectangle([0, 106, W, 111], fill=(128, 92, 76)); d.line([(0, 106), (W, 106)], fill=(156, 118, 96))
    d.rectangle([0, 112, W, H], fill=FLOOR)
    for i, y in enumerate(range(112, H, 13)):
        d.line([(0, y), (W, y)], fill=FLOOR_S)
        for x in range((i * 37) % 60, W, 60): d.line([(x, y), (x, y + 12)], fill=FLOOR_S)
        for x in range((i * 23) % 90, W, 90): d.line([(x + 8, y + 5), (x + 22, y + 5)], fill=FLOOR_L)
    wx, wy, ww, wh = WIN
    window(img, d, wx, wy, ww, wh, T, stops, (58, 20, 9) if moon_on else None, open_=curtain_open, sun=sun)
    # 墙上的画和钟
    for (fx, fy, fw, fh, c) in ((100, 26, 30, 24, (250, 190, 150)), (136, 34, 18, 22, (160, 200, 230))):
        d.rectangle([fx, fy, fx + fw, fy + fh], fill=(110, 76, 60)); d.rectangle([fx + 2, fy + 2, fx + fw - 2, fy + fh - 2], fill=c)
    d.rectangle([107, 38, 111, 46], fill=(238, 230, 214)); d.rectangle([107, 34, 111, 37], fill=(40, 36, 52))          # 画里的两个人
    d.rectangle([116, 38, 120, 46], fill=(248, 204, 88)); d.rectangle([116, 33, 120, 37], fill=(126, 78, 52)); d.line([(116, 38), (120, 38)], fill=SCARF)
    clock(d, 446, 34, 11, T * 0.02 + 0.3, T * 0.25)
    # 衣柜
    d.rectangle([22, 26, 86, 116], fill=(134, 92, 66)); d.rectangle([22, 26, 86, 30], fill=(160, 114, 82))
    d.rectangle([26, 34, 53, 110], fill=(156, 110, 78)); d.rectangle([55, 34, 82, 110], fill=(156, 110, 78))
    d.rectangle([50, 68, 51, 76], fill=(226, 196, 120)); d.rectangle([57, 68, 58, 76], fill=(226, 196, 120))
    d.rectangle([22, 116, 86, 119], fill=(96, 64, 48))
    # 书桌和椅子
    d.rectangle([410, 84, 474, 96], fill=(160, 114, 82)); d.rectangle([410, 96, 474, 122], fill=(134, 92, 66))
    d.rectangle([414, 100, 440, 118], fill=(120, 82, 60)); d.point((427, 109), fill=(226, 196, 120))
    d.rectangle([418, 70, 444, 86], fill=(52, 54, 72)); d.rectangle([420, 72, 442, 84], fill=(84, 96, 130)); d.rectangle([428, 86, 434, 88], fill=(52, 54, 72))
    for k, c in enumerate(((210, 90, 80), (90, 140, 190), (236, 196, 100))): d.rectangle([452 + k * 5, 72, 455 + k * 5, 85], fill=c)
    d.rectangle([424, 124, 448, 128], fill=(90, 110, 150)); d.rectangle([426, 128, 428, 146], fill=(70, 60, 60)); d.rectangle([444, 128, 446, 146], fill=(70, 60, 60))
    d.rectangle([424, 108, 448, 124], fill=(110, 132, 176))
    # 地毯
    d.ellipse([120, 204, 292, 250], fill=(170, 86, 90)); d.ellipse([128, 208, 284, 246], fill=(196, 110, 108)); d.ellipse([150, 215, 262, 239], outline=(236, 196, 170))
    # 床头柜、闹钟、合照
    for nx in (122, 266):
        d.rectangle([nx, 90, nx + 24, 98], fill=(170, 122, 88)); d.rectangle([nx, 98, nx + 24, 122], fill=(140, 96, 70))
        d.rectangle([nx + 3, 102, nx + 21, 110], fill=(124, 84, 62)); d.point((nx + 12, 106), fill=(226, 196, 120))
        d.rectangle([nx + 3, 112, nx + 21, 119], fill=(124, 84, 62)); d.point((nx + 12, 115), fill=(226, 196, 120))
    d.rectangle([126, 82, 136, 90], fill=(210, 80, 80)); d.rectangle([128, 84, 134, 88], fill=(250, 244, 230)); d.point((131, 86), fill=(40, 30, 40))
    d.rectangle([138, 80, 144, 90], fill=(110, 76, 60)); d.rectangle([139, 81, 143, 89], fill=(250, 220, 170))
    d.point([(140, 85), (140, 86)], fill=(40, 36, 52)); d.point([(142, 85), (142, 86)], fill=(248, 204, 88)); d.point((142, 84), fill=SCARF)
    # 台灯
    lx, ly = LAMP_AT
    d.rectangle([lx - 4, 88, lx + 4, 90], fill=(120, 96, 80)); d.rectangle([lx - 1, ly + 4, lx, 88], fill=(120, 96, 80))
    shade = lerpc((150, 140, 150), (255, 238, 170), lamp)
    d.polygon([(lx - 6, ly - 8), (lx + 5, ly - 8), (lx + 9, ly + 4), (lx - 10, ly + 4)], fill=shade)
    d.line([(lx - 10, ly + 4), (lx + 9, ly + 4)], fill=lerpc(shade, (0, 0, 0), 0.2))
    # 衣帽架和红围巾
    d.rectangle([302, 50, 303, 112], fill=(110, 76, 60)); d.rectangle([296, 112, 309, 114], fill=(110, 76, 60))
    d.line([(296, 54), (309, 54)], fill=(110, 76, 60)); d.point([(296, 53), (309, 53)], fill=(110, 76, 60))
    if scarf:
        sw = round(math.sin(T * 1.1) * 0.6)
        d.rectangle([305, 54, 310, 58], fill=SCARF); d.rectangle([307, 58, 310 + sw, 84], fill=SCARF); d.rectangle([307, 84, 310 + sw, 86], fill=SCARF_D)
        d.rectangle([295, 54, 299, 72], fill=SCARF); d.rectangle([295, 72, 299, 74], fill=SCARF_D)
    # 盆栽
    d.rectangle([94, 104, 106, 118], fill=(190, 110, 80)); d.rectangle([92, 102, 108, 105], fill=(210, 130, 96))
    for k, (px, py) in enumerate(((100, 90), (94, 94), (106, 93), (97, 84), (104, 85))): d.ellipse([px - 4, py - 5, px + 4, py + 5], fill=(70, 140, 90) if k % 2 else (96, 168, 104))
    # 床
    x0, x1 = BED
    d.rectangle([x0 - 4, 78, x1 + 4, 112], fill=(128, 86, 62)); d.rectangle([x0 - 4, 78, x1 + 4, 82], fill=(160, 114, 82))
    d.rectangle([x0 + 2, 86, x1 - 2, 108], fill=(146, 100, 72))
    d.rectangle([x0, 206, x1, 210], fill=(60, 44, 44))                                           # 床底的影子
    d.rectangle([x0, 106, x1, 196], fill=SHEET); d.rectangle([x0, 106, x0 + 1, 196], fill=SHEET_S); d.rectangle([x1 - 1, 106, x1, 196], fill=SHEET_S)
    for px in (x0 + 6, x0 + 60):
        d.rounded_rectangle([px, 110, px + 46, 127], 4, fill=(252, 250, 246), outline=SHEET_S)
    d.rectangle([x0, 130, x1, 196], fill=BLANKET); d.rectangle([x0, 130, x1, 136], fill=BLANKET_L); d.line([(x0, 137), (x1, 137)], fill=BLANKET_S)
    for k in range(5): d.line([(x0 + 14 + k * 22, 146), (x0 + 10 + k * 22, 190)], fill=BLANKET_S)
    d.rectangle([x0 - 2, 196, x1 + 2, 204], fill=(128, 86, 62)); d.line([(x0 - 2, 196), (x1 + 2, 196)], fill=(160, 114, 82))
    # 拖鞋：一双穿过，一双整整齐齐
    for sx, c in ((166, (120, 150, 200)), (232, (248, 204, 88))):
        d.rectangle([sx, 212, sx + 4, 217], fill=c); d.rectangle([sx + 7, 212 + (1 if sx < 200 else 0), sx + 11, 217 + (1 if sx < 200 else 0)], fill=c)
        d.line([(sx, 212), (sx + 4, 212)], fill=lerpc(c, (255, 255, 255), 0.4)); d.line([(sx + 7, 212), (sx + 11, 212)], fill=lerpc(c, (255, 255, 255), 0.4))
    hx, hy = x0 + 21, 104
    if me == 'lie':
        d.rounded_rectangle([x0 + 10, 126, x0 + 50, 190], 8, fill=BLANKET_L, outline=BLANKET_S)
        d.rectangle([x0 + 12, 130, x0 + 48, 136], fill=lerpc(BLANKET_L, (255, 255, 255), 0.3))
        h = head_img('boy', 'young', expr, 1)
        img.paste(h, (hx, hy), h)
    elif me == 'sit':
        person(img, 'boy', me_x, me_y, view='front', pose='sit', expr=expr, arms=me_arms)
    elif me == 'edge':                         # 坐在床的右沿，脸朝台灯
        person(img, 'boy', 258, 160, view='side', pose='sit', expr=expr, arms=me_arms)
    elif me == 'free':
        person(img, 'boy', me_x, me_y, view=me_view, pose=me_pose, ph=me_ph, expr=expr, arms=me_arms, flip=me_flip, scarf=me_scarf)
    # 明暗
    extra = np.zeros((H, W)); extra[wy:wy + wh, wx:wx + ww] = 1
    extra = np.maximum(extra, _moon_patch() * (1 - day) * (1 - 0.6 * lamp))
    lights = [(wx + ww / 2, wy + wh / 2, 80, 0.45)]
    if lamp > 0: lights.append((lx, ly + 10, 230, 1.25 * lamp, 190))
    amb = lerp(lerp(0.13, 0.3, lamp), 1.0, day)
    lighting(img, lights, amb, extra=extra)
    if lamp > 0:
        glow(img, lx, ly, 26, (255, 236, 170), 0.5 * lamp)
        d.polygon([(lx - 6, ly - 8), (lx + 5, ly - 8), (lx + 9, ly + 4), (lx - 10, ly + 4)], fill=lerpc((255, 238, 170), (255, 255, 230), 0.4))
    if eyes and me == 'lie':
        d.point([(hx + 5, hy + 10), (hx + 10, hy + 10)], fill=(236, 240, 255))
    if lamp < 1 and day < 1:
        tfill(img, 'polygon', [(330, 150), (400, 150), (372, 236), (286, 236)], (150, 170, 255), 0.2 * (1 - lamp) * (1 - day))
    if ghost_sit > 0:
        glow(img, 300, 150, 26, (255, 230, 170), 0.3 * ghost_sit)
        ghost(img, 'girl', 300, 168, 1, ghost_sit * 0.85, view='side', expr='smile', flip=True)
    if ghost_lie > 0:
        g = head_img('girl', 'young', 'closed', 1)
        glow(img, x0 + 83, 150, 40, (255, 230, 170), 0.22 * ghost_lie, ry=50)
        lay = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([x0 + 64, 126, x0 + 104, 190], 8, fill=(255, 236, 190, 255), outline=(236, 200, 150, 255))
        lay.paste(g, (x0 + 75, hy), g)
        dpaste(img, lay, 0, 0, ghost_lie * 0.6)
