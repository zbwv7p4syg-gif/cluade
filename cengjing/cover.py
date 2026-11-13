"""曾经是情侣 · 竖屏封面：黄昏的山坡上，他和她背对着我们站在落日两边，牵着的红线在中间断开；
天上一颗红心沿锯齿裂缝裂成两半，片名分两行落在天上，风筝挂在大树的枝头。
沿用 MV 的角色、红线和画法，画在 270×480 的画布上，最近邻放大 4 倍到 1080×1920。

python3 cover.py [--lyrics 歌词.lrc] [-o build/曾经是情侣_封面.png]
"""
import argparse, math, os, re
import numpy as np
from PIL import Image, ImageDraw

import pix

# 封面是竖屏：先把共用画布换成 270×480，再导入道具和镜头模块，让光晕、渐变这些工具都按竖屏的大小裁切
W, H = 270, 480
pix.W, pix.H = W, H
pix.BAYER = pix.bayer(H, W)
import props  # noqa: E402
from props import *  # noqa: E402,F401,F403
from pix import put, twinkle, cloud  # noqa: E402
import sc_a as A  # noqa: E402

SC = 4
HERE = os.path.dirname(os.path.abspath(__file__))
T = 2.0
HORIZON = 382
SKY = ((0, (20, 18, 58)), (0.3, (70, 54, 130)), (0.58, (190, 106, 156)), (0.8, (250, 156, 136)), (1, (255, 214, 160)))


def hill_y(x):
    return 412 + 30 * ((x - 135) / 170) ** 2


def backdrop(img, d):
    img.paste(pix.vgrad(W, HORIZON, SKY, 6), (0, 0))
    r = rng(7)
    for _ in range(110):                                     # 上半截的星星
        x, y, b = r.uniform(0, W), r.uniform(0, 190) ** 1.1 * 0.9, r.random()
        c = lerpc((60, 50, 110), (255, 250, 225), 0.3 + 0.7 * b)
        d.point((x, y), fill=c)
        if b > 0.93: d.point([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], fill=lerpc(c, (60, 50, 110), 0.5))
    pix.moon(d, 236, 30, 9, (252, 244, 214)); glow(img, 236, 30, 26, (250, 240, 210), 0.25)
    # 落日
    sx, sy = 135, HORIZON - 4
    glow(img, sx, sy, 150, (255, 190, 150), 0.42, 90)
    d.ellipse([sx - 30, sy - 30, sx + 30, sy + 30], fill=(255, 238, 200))
    for k in range(3): d.line([(sx - 26 + k * 3, sy - 10 + k * 7), (sx + 26 - k * 3, sy - 10 + k * 7)], fill=(255, 220, 168))
    for x, y, s in [(-14, 318, 1.3), (176, 300, 1.0), (60, 344, 0.9), (210, 352, 1.2)]:
        cloud(d, x, y, s, (255, 200, 200), (236, 150, 170), (255, 236, 236))
    pix.hills(d, HORIZON, 5, 0.03, 1.0, (176, 108, 150))
    pix.hills(d, HORIZON + 12, 6, 0.024, 2.4, (122, 80, 130))
    main, rim = (62, 62, 98), (255, 170, 160)
    for x in range(W):
        y = int(hill_y(x))
        d.line([(x, y), (x, H)], fill=main)
        d.point((x, y), fill=rim)
    for i, x in enumerate(range(0, W, 3)):
        y = hill_y(x); h = 2 + (i * 7) % 4
        d.line([(x, y), (x + math.sin(x * 0.1) * 0.8, y - h)], fill=rim if i % 3 else lerpc(main, rim, 0.5))
    for j in range(16):                                      # 山坡上几朵会发光的小花
        r2 = rng(j + 40)
        x = r2.uniform(6, W - 6); y = hill_y(x) + r2.uniform(14, 60)
        c = [(110, 230, 255), (255, 150, 200), (255, 220, 110)][j % 3]
        glow(img, x, y - 4, 6, c, 0.4)
        pix.flower(d, int(x), int(y), c, 0, (70, 120, 110), 4)


def tree_and_kite(img, d):
    """右边的大树，风筝挂在树枝上"""
    pix.tree_round(d, 252, hill_y(252) + 2, 2.1, (70, 66, 110), (110, 92, 140), (52, 44, 70), 0)
    tail = kite(d, 222, 334, 1.3, 0.6, RED, GOLD_L)
    d.line(bez(tail, (206, 402), (196, 372), 16), fill=(250, 236, 228))


def broken_heart(img, d, c=(135, 268), s=2.9):
    """天上的红心沿锯齿裂缝裂成两半，裂缝里透出白光"""
    lh, rh = A.heart_halves(s, c)
    glow(img, c[0], c[1] + 6, 90, RED, 0.35)
    glow(img, c[0], c[1] + 10, 26, (255, 240, 230), 0.6, 60)
    for poly, sgn in ((lh, -1), (rh, 1)):
        ang = sgn * 0.08
        pts = []
        for x, y in poly:
            dx, dy = x - c[0], y - c[1]
            pts.append((c[0] + dx * math.cos(ang) - dy * math.sin(ang) + sgn * 7, c[1] + dx * math.sin(ang) + dy * math.cos(ang)))
        d.polygon([(x + sgn, y + 2) for x, y in pts], fill=OUT)
        d.polygon(pts, fill=RED)
        d.line(pts + pts[:1], fill=RED_D)
    for sgn in (-1, 1):                                      # 两半上的高光
        hx = c[0] + sgn * 22
        d.ellipse([hx - 6 - sgn * 4, c[1] - 26, hx + 2 - sgn * 4, c[1] - 18], fill=RED_L)
    zig = [(c[0] + x * s * 0.5, c[1] + y * s) for x, y in A.ZIG]
    d.line(zig, fill=(255, 250, 240), width=2)
    for j in range(10):                                      # 从裂缝里迸出来的火星和小心
        a = j * 0.63 + 0.3
        rr = 54 + (j % 3) * 12
        x, y = c[0] + math.cos(a) * rr, c[1] + math.sin(a) * rr * 0.9
        if j % 3 == 0: put(img, 'heart', x, y, 1, tint=[RED_L, PINK_L, (255, 255, 255)][j % 3])
        else: twinkle(d, int(x), int(y), 0.5, (255, 240, 236), 2 + j % 3)


def title(img, d):
    """片名分两行错开落在天上：上一行靠左，下一行靠右，中间一根红线连到歌手名"""
    s = title_str()
    a, b = (s[:3], s[3:]) if len(s) >= 4 else (s, '')
    sc = 4
    for line, (x0, cy, align) in ((a, (16, 68, 'l')), (b, (W - 14, 160, 'r'))):
        if not line: continue
        adv = [FONT.getlength(ch) * sc for ch in line]
        x = x0 if align == 'l' else x0 - sum(adv)
        glow(img, x + sum(adv) / 2, cy, sum(adv) / 2 + 30, (255, 200, 220), 0.25, 50)
        for ch, w in zip(line, adv):
            g = big_glyph(ch, sc)
            img.paste(g, (int(x - 4 * sc), int(cy - g.height / 2)), g)
            x += w
    # 红线：从上一行底下垂下来，绕到下一行底下，线头一颗小心
    pts = bez((22, 106), (250, 208), (56, 222), 40)
    d.line([(x, y + 1) for x, y in pts], fill=RED_D, width=2)
    d.line(pts, fill=RED, width=1)
    put(img, 'heart', 256, 208, 1)
    ar = artist_str()
    if ar: text(img, ar, 62, 156, (255, 244, 238), (56, 22, 50))


def couple(img, d):
    """他和她背对着我们站在落日两边，牵着的红线在中间断开"""
    gx, bx, fy, s = 88, 182, 410, 3
    shade = (0.82, 0.78, 0.92)
    pix.person(img, 'girl', gx, fy, view='back', pose='stand', arms='hold_r', s=s, shade=shade)
    pix.person(img, 'boy', bx, fy, view='back', pose='stand', arms='hold_l', s=s, shade=shade)
    gh, bh = (gx + 25, fy - 29), (bx - 29, fy - 29)
    for p0, end, ctl in ((gh, (129, 396), (126, 380)), (bh, (142, 400), (144, 380))):
        glow(img, end[0], end[1], 8, RED_L, 0.5)
        d.line(bez(p0, end, ctl, 14), fill=RED, width=2)
        d.point(end, fill=RED_L)
    for j in range(5): d.point((133 + (j % 3) * 2, 386 + j * 2), fill=lerpc(RED_L, (255, 240, 200), j / 5))


def main():
    ap = argparse.ArgumentParser(description='曾经是情侣 · 竖屏封面')
    ap.add_argument('--lyrics', help='.lrc 歌词，只用来读 [ti:] 和 [ar:] 里的歌名和歌手')
    ap.add_argument('-o', '--out', default=os.path.join(HERE, 'build', '曾经是情侣_封面.png'))
    args = ap.parse_args()
    if args.lyrics:
        for raw in open(args.lyrics, encoding='utf-8-sig'):
            m = re.match(r'\[(ti|ar):(.*)\]', raw.strip())
            if m: pix.META[m.group(1)] = m.group(2).strip()

    img = Image.new('RGB', (W, H)); d = ImageDraw.Draw(img); d.fontmode = '1'
    backdrop(img, d)
    tree_and_kite(img, d)
    broken_heart(img, d)
    couple(img, d)
    title(img, d)
    pix.petals(d, T, 22, speed=14, wind=20, seed=5)
    for j in range(4): pix.bird(d, 26 + j * 14, 236 + (j % 2) * 6, T, (70, 50, 90), j)
    # 底部的英文片名
    pix.blend_box(img, (0, 452, W, 474), (16, 8, 26), np.full((22, W), 0.55))
    text(img, 'WE  WERE  LOVERS  ONCE', W / 2, 462, (255, 236, 232), (60, 20, 40), FONT_S)
    put(img, 'heart', 22, 462, 1); put(img, 'heart', W - 22, 462, 1)
    pix.vig(img, 0.35, (16, 10, 30))

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    img.resize((W * SC, H * SC), Image.NEAREST).save(args.out)
    print(args.out)


if __name__ == '__main__':
    main()
