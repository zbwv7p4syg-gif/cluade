"""爱错 · 竖屏封面：下雪的夜里挂着极光，片名由一格格红色像素拼成，中间裂开一道发亮的缝；
山坡上一棵积雪的秃树，她穿红大衣站在树下背对着我们；北风缩在半空，难过地看着一片心形红叶被吹向她；
近处的他伸手想去够那片叶子。
沿用 MV 的角色、北风、红叶和画法，画在 270×480 的画布上，最近邻放大 4 倍到 1080×1920。

python3 cover.py [--lyrics 歌词.lrc] [-o build/爱错_封面.png]
"""
import argparse, math, os, re
import numpy as np
from PIL import Image, ImageDraw

import pix

# 封面是竖屏：先把共用画布换成 270×480，再导入别的模块，让光晕、渐变、极光这些工具都按竖屏的大小裁切
W, H = 270, 480
pix.W, pix.H = W, H
pix.BAYER = pix.bayer(H, W)
import props  # noqa: E402
import motifs as M  # noqa: E402
import sc_a  # noqa: E402
from props import *  # noqa: E402,F401,F403
from pix import twinkle  # noqa: E402

SC = 4
HERE = os.path.dirname(os.path.abspath(__file__))
T = 1.3
GROUND = 372
SKY = ((0, (6, 8, 26)), (0.35, (18, 24, 62)), (0.75, (44, 50, 100)), (1, (86, 84, 136)))


def backdrop(img, d):
    img.paste(pix.vgrad(W, GROUND, SKY, 6), (0, 0))
    M.aurora(img, 0.8, 10, 150, 0.6)
    r = rng(3)
    for _ in range(140):                                     # 星星
        x, y, b = r.uniform(0, W), r.uniform(0, 330), r.random()
        c = lerpc((50, 56, 110), (255, 250, 232), 0.3 + 0.7 * b)
        d.point((x, y), fill=c)
        if b > 0.94: d.point([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], fill=lerpc(c, (50, 56, 110), 0.5))
    pix.moon(d, 222, 214, 13, (250, 244, 218)); glow(img, 222, 214, 40, (210, 220, 255), 0.3)
    sc_a.ridge(d, 342, 26, 0.03, 0.4, (40, 50, 96))
    sc_a.ridge(d, 360, 16, 0.05, 2.0, (60, 70, 120))


def hillside(img, d):
    """右边的雪坡和秃树，树下站着她"""
    sc_a.hill(d, 236, 318, 120, (210, 222, 246))
    M.tree(img, d, 214, 326, 150, T, seed=3, sway=0.3, leaf_on=lambda j, r: False, snow=1.0, spread=0.62, bark=(52, 46, 66), bark_d=(36, 32, 52))
    glow(img, 196, 304, 22, (255, 170, 170), 0.3)
    pix.person(img, 'girl', 196, 330, view='back', pose='stand', s=1)
    # 近处的雪地
    for x in range(W):
        y = GROUND + 4 * math.sin(x * 0.03 + 1) + 2 * math.sin(x * 0.09)
        d.line([(x, y), (x, H)], fill=(220, 228, 248))
        d.point((x, y), fill=(250, 252, 255))
    for i in range(30):
        r = rng(i * 3)
        x, y = r.uniform(0, W), r.uniform(GROUND + 8, H - 24)
        d.line([(x, y), (x + r.uniform(6, 18), y)], fill=(180, 192, 226))


def wind_and_leaf(img, d):
    """北风在半空难过地看着；一道风把心形红叶从他手边吹向她"""
    M.wind(img, 66, 254, 1.5, T, 'sad', look=(1, 1), tail=True)
    pts = [(96 + u * 96, 352 - u * 70 - 18 * math.sin(u * math.pi)) for u in np.linspace(0, 1, 30)]
    for k in range(len(pts) - 1):
        if k % 3 != 2: d.line([pts[k], pts[k + 1]], fill=lerpc((150, 170, 220), (230, 240, 255), k / len(pts)))
    lx, ly = 150, 306
    glow(img, lx, ly, 30, (255, 120, 120), 0.45)
    M.leaf(img, lx, ly, 3, 0, spin=0, rot=-30)
    for j in range(3):
        tfill(img, 'line', [(lx - 30 - j * 10, ly + 10 + j * 5), (lx - 18 - j * 10, ly + 8 + j * 5)], (240, 246, 255), 0.8 - j * 0.2)
    twinkle(d, 172, 292, 0.5, (255, 240, 240), 3)


def hero(img, d):
    """他站在近处的雪地里，伸手去够那片叶子"""
    pix.person(img, 'boy', 74, 452, view='side', pose='stand', expr='sad', arms='reach', s=3)


def title(img, d):
    """片名和 MV 片头一样由一格格像素方块拼成，中间一道发亮的裂缝把两半错开"""
    cells, box = sc_a.title_cells()
    bx0, by0, bx1, by1 = box
    split = 2
    glow(img, W / 2, sc_a.TITLE_CY, 150, (255, 70, 90), 0.3, 80)
    for (cx, cy, col, u, r) in cells:
        right = cx + sc_a.TS / 2 > sc_a.crack_x(cy, box)
        sx, sy = (split, split * 0.6) if right else (-split, -split * 0.6)
        d.rectangle([cx + sx, cy + sy, cx + sx + sc_a.TS - 1, cy + sy + sc_a.TS - 1], fill=col)
    pts = [(sc_a.crack_x(y, box), y) for y in np.linspace(by0 - 6, by1 + 6, 25)]
    d.line([(x - split + 1, y - split * 0.6) for x, y in pts], fill=(255, 220, 210))
    d.line([(x + split - 1, y + split * 0.6) for x, y in pts], fill=(255, 220, 210))
    for j in range(8):                                       # 裂开时掉下来的碎块
        r = rng(j * 7 + 3)
        y0 = lerp(by0, by1, r.random())
        x = sc_a.crack_x(y0, box) + r.uniform(-10, 10)
        y = y0 + r.uniform(10, 40)
        d.rectangle([x, y, x + 2, y + 2], fill=(214, 40, 62) if j % 2 else (255, 150, 150))
    ar = artist_str()
    if ar: text(img, ar, W / 2, by1 + 16, (240, 232, 255), (30, 20, 50))


def main():
    ap = argparse.ArgumentParser(description='爱错 · 竖屏封面')
    ap.add_argument('--lyrics', help='.lrc 歌词，只用来读 [ti:] 和 [ar:] 里的歌名和歌手')
    ap.add_argument('-o', '--out', default=os.path.join(HERE, 'build', '爱错_封面.png'))
    args = ap.parse_args()
    if args.lyrics:
        for raw in open(args.lyrics, encoding='utf-8-sig'):
            m = re.match(r'\[(ti|ar):(.*)\]', raw.strip())
            if m: pix.META[m.group(1)] = m.group(2).strip()

    img = Image.new('RGB', (W, H)); d = ImageDraw.Draw(img); d.fontmode = '1'
    backdrop(img, d)
    hillside(img, d)
    wind_and_leaf(img, d)
    hero(img, d)
    title(img, d)
    pix.snow(d, T, n=90, speed=12, wind=3, y1=H)
    # 底部的小字
    pix.blend_box(img, (0, 458, W, 478), (10, 10, 26), np.full((20, W), 0.55))
    text(img, '· 像素 MV ·', W / 2, 467, (255, 240, 240), (60, 20, 40), FONT_S)
    pix.vig(img, 0.35, (6, 8, 24))

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    img.resize((W * SC, H * SC), Image.NEAREST).save(args.out)
    print(args.out)


if __name__ == '__main__':
    main()
