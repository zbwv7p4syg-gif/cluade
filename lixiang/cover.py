"""理想三旬 · 竖屏封面：雨后的黄昏，太阳正落进海里，旧铁皮火车亮着窗从海上的长桥开过；
站台的积水映着晚霞，他背着吉他、围着被风吹起的黄围巾，和小黑猫一起背对着我们看火车开远。
片名分两行落在天上，下面一段小铁轨上跑着一辆小火车。
沿用 MV 的角色、火车和画法，画在 270×480 的画布上，最近邻放大 4 倍到 1080×1920。

python3 cover.py [--lyrics 歌词.lrc] [-o build/理想三旬_封面.png]
"""
import argparse, math, os, re
import numpy as np
from PIL import Image, ImageDraw

import pix

# 封面是竖屏：先把共用画布换成 270×480，再导入道具模块，让光晕、渐变、倒影这些工具都按竖屏的大小裁切
W, H = 270, 480
pix.W, pix.H = W, H
pix.BAYER = pix.bayer(H, W)
import props  # noqa: E402
from props import *  # noqa: E402,F401,F403
from pix import put, twinkle, cloud  # noqa: E402

SC = 4
HERE = os.path.dirname(os.path.abspath(__file__))
T = 1.3
HORIZON = 264
DECK = 338
SKY = ((0, (16, 16, 50)), (0.3, (62, 54, 120)), (0.55, (176, 110, 156)), (0.8, (248, 160, 132)), (1, (255, 222, 170)))


def backdrop(img, d):
    img.paste(pix.vgrad(W, HORIZON, SKY, 6), (0, 0))
    r = rng(3)
    for _ in range(120):                                     # 上半截的星星
        x, y, b = r.uniform(0, W), r.uniform(0, 170) ** 1.08 * 0.85, r.random()
        c = lerpc((60, 54, 110), (255, 250, 226), 0.3 + 0.7 * b)
        d.point((x, y), fill=c)
        if b > 0.93: d.point([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], fill=lerpc(c, (60, 54, 110), 0.5))
    pix.moon(d, 240, 30, 9, (252, 244, 214)); glow(img, 240, 30, 26, (250, 240, 210), 0.25)
    pix.meteor(d, 0.45, 0, 150, 14, -90, 40)
    pix.meteor(d, 0.6, 0, 120, 190, -70, 30, n=12)
    # 落日一半沉进海里
    sx, sy = 132, HORIZON
    glow(img, sx, sy, 170, (255, 196, 150), 0.45, 100)
    d.ellipse([sx - 28, sy - 28, sx + 28, sy + 28], fill=(255, 238, 202))
    for k in range(3): d.line([(sx - 24 + k * 3, sy - 12 + k * 6), (sx + 24 - k * 3, sy - 12 + k * 6)], fill=(255, 220, 170))
    for x, y, s in [(-30, 214, 1.3), (196, 206, 1.2), (206, 240, 0.8), (-6, 242, 0.8)]:
        cloud(d, x, y, s, (255, 204, 196), (236, 150, 160), (255, 238, 232))
    # 海
    d.rectangle([0, HORIZON, W, 384], fill=(150, 104, 140))
    for j in range(14):
        y = HORIZON + 3 + j * 6
        for k in range(5):
            x = (k * 66 + j * 29) % (W + 30) - 15
            d.line([(x, y), (x + 10 + j, y)], fill=(176, 126, 160) if (j + k) % 2 else (128, 88, 126))
    for j in range(9):                                       # 太阳在海上的倒影
        y = HORIZON + 3 + j * 5
        w = 26 - j * 2 + (j % 2) * 4
        d.line([(sx - w, y), (sx + w, y)], fill=lerpc((255, 230, 190), (220, 150, 150), j / 9))


def bridge_and_train(img, d):
    bc = (60, 42, 70)
    for x in range(-10, W + 40, 46):
        d.rectangle([x, DECK + 4, x + 5, 384], fill=bc)
    d.rectangle([0, DECK, W, DECK + 5], fill=bc)
    for x in range(-20, W + 30, 24):
        d.line([(x, DECK), (x + 12, DECK - 18)], fill=bc); d.line([(x + 24, DECK), (x + 12, DECK - 18)], fill=bc)
    d.line([(0, DECK - 18), (W, DECK - 18)], fill=bc)
    props.smoke(img, 172, DECK - 52, T, n=9, col=(250, 226, 226), shade=(220, 170, 186), vx=-80, vy=-12, life=1.8, r1=13, seed=4)
    train(img, d, 200, DECK, T, cars=2, lit=0.85, seed=4, roll=1.2, headlight=0.9, night=0.15, hero=(0, 4))


def platform(img, d):
    top = 384
    d.rectangle([0, top, W, H], fill=(70, 62, 86))
    d.rectangle([0, top, W, top + 3], fill=(236, 200, 96))
    for x in range(0, W, 10): d.point((x + 3, top + 1), fill=(196, 160, 70))
    props.reflect(img, top + 4, 92, T, (40, 34, 60), 0.7, 1.2, 90)
    for i in range(10):                                      # 积水上的高光
        r = rng(i * 5)
        x, y = r.uniform(0, W), r.uniform(top + 12, H - 30)
        d.line([(x, y), (x + r.uniform(10, 30), y)], fill=(170, 150, 186))
    props.ripples(d, T, (0, top + 10, W, H - 30), 8, (180, 160, 200), per=1.4, rmax=7)
    # 右边的路灯和站牌
    pix.lamp(img, d, 254, top + 2, 1.0, 100)
    d.rectangle([232, top - 56, 234, top + 2], fill=(70, 66, 90))
    d.rectangle([212, top - 70, 256, top - 54], fill=(236, 236, 226)); d.rectangle([212, top - 70, 256, top - 54], outline=OUT)
    text(img, '无名站', 234, top - 62, (40, 60, 120), None, FONT_S, shadow=False)


def hero(img, d):
    """他背着吉他、围巾被风吹向右边；小黑猫坐在旁边"""
    x, fy, s = 92, 450, 4
    # 背上的吉他：斜着从右肩伸到左下
    d.ellipse([x - 44, fy - 70, x - 8, fy - 34], fill=OUT)
    d.ellipse([x - 43, fy - 69, x - 9, fy - 35], fill=(214, 146, 78))
    d.ellipse([x - 32, fy - 58, x - 20, fy - 46], fill=(60, 36, 24))
    d.line([(x - 14, fy - 64), (x + 26, fy - 128)], fill=(110, 70, 46), width=6)
    d.polygon([(x + 22, fy - 126), (x + 34, fy - 134), (x + 38, fy - 128), (x + 28, fy - 120)], fill=(80, 50, 36))
    pix.person(img, 'boy', x, fy, view='back', s=s, shade=(0.92, 0.88, 0.98))
    # 被风吹起来的围巾
    sy = fy - 4 * 16
    d.polygon([(x + 4, sy - 2), (x + 12, sy - 2), (x + 46, sy - 14), (x + 52, sy - 6), (x + 44, sy - 4)], fill=MUSTARD)
    d.line([(x + 14, sy - 3), (x + 46, sy - 12)], fill=MUSTARD_S)
    for k in range(3): d.point((x + 50 + k, sy - 9 + k * 2), fill=MUSTARD_S)
    cat(img, 148, fy, 'sit', 3, rim=(150, 130, 170))


def title(img, d):
    """片名分两行错开落在天上：上一行靠左，下一行靠右；下面一段小铁轨，跑着一辆小火车"""
    s = title_str()
    a, b = (s[:2], s[2:]) if len(s) >= 4 else (s, '')
    sc = 4
    for line, (x0, cy, align) in ((a, (18, 70, 'l')), (b, (W - 16, 146, 'r'))):
        if not line: continue
        adv = [FONT.getlength(ch) * sc for ch in line]
        x = x0 if align == 'l' else x0 - sum(adv)
        glow(img, x + sum(adv) / 2, cy, sum(adv) / 2 + 34, (255, 210, 170), 0.22, 54)
        for ch, w in zip(line, adv):
            g = big_glyph(ch, sc)
            img.paste(g, (int(x - 4 * sc), int(cy - g.height / 2)), g)
            x += w
    # 小铁轨从上一行底下斜着连到下一行底下，一辆小火车开在上面
    p0, p1 = (20, 116), (252, 194)
    pts = [(lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u) + 22 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 60)]
    for i in range(0, len(pts) - 1, 2):
        (xa, ya), (xb, yb) = pts[i], pts[i + 1]
        d.line([(xa, ya + 2), (xa + 1, ya + 3)], fill=(120, 96, 90))
    d.line(pts, fill=(236, 226, 214))
    u = 0.3
    tx, ty = lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u) + 22 * math.sin(math.pi * u)
    train(img, d, tx + 26, ty, T, cars=1, s=0.25, rust=0, people=False, roll=0)
    for j in range(3):
        props.puff(img, tx - 4 - j * 7, ty - 16 - j * 4, 2 + j, (250, 246, 250), 0.9 - j * 0.2)
    ar = artist_str()
    if ar: text(img, ar, 70, 166, (255, 246, 236), (56, 30, 50))


def main():
    ap = argparse.ArgumentParser(description='理想三旬 · 竖屏封面')
    ap.add_argument('--lyrics', help='.lrc 歌词，只用来读 [ti:] 和 [ar:] 里的歌名和歌手')
    ap.add_argument('-o', '--out', default=os.path.join(HERE, 'build', '理想三旬_封面.png'))
    args = ap.parse_args()
    if args.lyrics:
        for raw in open(args.lyrics, encoding='utf-8-sig'):
            m = re.match(r'\[(ti|ar):(.*)\]', raw.strip())
            if m: pix.META[m.group(1)] = m.group(2).strip()

    img = Image.new('RGB', (W, H)); d = ImageDraw.Draw(img); d.fontmode = '1'
    backdrop(img, d)
    bridge_and_train(img, d)
    platform(img, d)
    hero(img, d)
    title(img, d)
    for j in range(5): pix.bird(d, 160 + j * 15, 226 + (j % 2) * 6, T, (90, 60, 100), j)
    # 底部的小字
    pix.blend_box(img, (0, 456, W, 476), (16, 10, 26), np.full((20, W), 0.55))
    text(img, '· 像素 MV ·', W / 2, 465, (255, 240, 220), (60, 30, 40), FONT_S)
    pix.vig(img, 0.35, (16, 10, 30))

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    img.resize((W * SC, H * SC), Image.NEAREST).save(args.out)
    print(args.out)


if __name__ == '__main__':
    main()
