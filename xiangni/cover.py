"""想你和我们以后 · 竖屏封面：沿用 MV 的像素画法、角色和红线，画在 270×480 的画布上，最近邻放大 4 倍到 1080×1920。

python3 cover.py --lyrics 歌词.lrc [-o build/想你和我们以后_封面.png]
"""
import argparse, math, os, re
from PIL import Image, ImageDraw

import pix

# 封面是竖屏：先把共用画布换成 270×480，再导入镜头模块，让光晕、红线、楼房这些工具都按竖屏的大小裁切
W, H = 270, 480
pix.W, pix.H = W, H
pix.BAYER = pix.bayer(H, W)
import scenes  # noqa: E402
from pix import FONT, OUT, lerp, lerpc, glow, tfill, twinkle, put, person, text, moon, bird, meteor, rng  # noqa: E402

SC = 4
HERE = os.path.dirname(os.path.abspath(__file__))
T = 12.3   # 封面定格的时刻：星星、窗户闪烁等跟时间有关的细节都按这一刻画


def sky_and_stars(img, d):
    img.paste(pix.vgrad(W, H, ((0, (8, 8, 32)), (0.34, (30, 22, 78)), (0.6, (92, 50, 128)), (0.78, (198, 102, 144)),
                               (1, (236, 142, 150))), 7))
    r = rng(3)
    for _ in range(190):
        x, y, b = r.uniform(0, W), r.uniform(0, 380), r.random()
        c = lerpc((60, 60, 110), (255, 252, 230), 0.35 + 0.65 * b)
        d.point((x, y), fill=c)
        if b > 0.93:
            d.point([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], fill=lerpc(c, (60, 60, 110), 0.45))
    meteor(d, 0.45, 0, 262, 26, -80, 32, 1.0)


def roof_railing(d, x0, x1, y, col=(24, 18, 44)):
    d.rectangle([x0, y - 11, x1, y - 10], fill=col)
    d.rectangle([x0, y - 5, x1, y - 4], fill=col)
    for x in range(int(x0), int(x1) + 1, 7):
        d.rectangle([x, y - 11, x + 1, y], fill=col)


def string_lights(img, d, x0, y0, x1, y1, sag=8):
    pts = [(lerp(x0, x1, i / 24), lerp(y0, y1, i / 24) + sag * math.sin(math.pi * i / 24)) for i in range(25)]
    d.line(pts, fill=(40, 30, 50))
    for i, (x, y) in enumerate(pts[1:-1:2]):
        c = [(255, 214, 110), (255, 130, 150), (140, 210, 255)][i % 3]
        d.rectangle([x - 1, y + 1, x, y + 2], fill=c)
        glow(img, x, y + 2, 6, c, 0.45)


def city(img, d):
    pix.city(img, d, 396, 41, 0, (74, 46, 112), (176, 136, 204), 30, 100, 0.3, T, 10, 22, blink=False)
    pix.city(img, d, 438, 42, 40, (40, 28, 74), (255, 210, 140), 40, 120, 0.42, T, 12, 26, blink=False)
    d.rectangle([0, 452, W, H], fill=(20, 14, 38))
    for k in range(5):
        y = 460 + (k % 3) * 5
        x = 100 + (k * 23) % 70
        c = (255, 240, 200) if k % 2 else (255, 90, 90)
        d.line([(x, y), (x + 12, y)], fill=lerpc(c, (20, 14, 38), 0.45))
        d.rectangle([x + 12, y, x + 13, y], fill=c)


def rooftops(img, d):
    # 她的楼在左，他的楼在右，和片头一样各有一扇亮着的窗
    scenes.near_building(d, -6, 356, 102, (36, 28, 66), 1)
    scenes.near_building(d, 174, 344, 102, (32, 30, 70), 7)
    d.rectangle([2, 300, 24, 342], fill=(30, 24, 56)); d.polygon([(0, 300), (26, 300), (13, 290)], fill=(30, 24, 56))
    d.rectangle([5, 342, 8, 356], fill=(30, 24, 56)); d.rectangle([18, 342, 21, 356], fill=(30, 24, 56))
    string_lights(img, d, 6, 318, 96, 330)
    ax = 258
    d.line([(ax, 344), (ax, 296)], fill=(30, 28, 62), width=2)
    d.rectangle([ax - 1, 292, ax + 1, 294], fill=(255, 80, 80)); glow(img, ax, 293, 8, (255, 80, 80), 0.55)
    d.pieslice([228, 318, 248, 338], 200, 380, fill=(52, 50, 90)); d.line([(238, 328), (238, 344)], fill=(30, 28, 62))


def thread_and_hearts(img, d):
    hand_g, hand_b = (90, 306), (184, 294)
    cx, cy, k = 135, 222, 2.4
    loop = [(cx + x * k, cy + y * k) for x, y in (pix.HEART_PTS[32:] + pix.HEART_PTS[:33])][::3]
    ctrl = [hand_g, (102, 292), (120, 278)] + loop + [(150, 278), (168, 286), hand_b]
    pts = scenes.catmull(ctrl, 8)
    glow(img, cx, cy + 6, 70, (255, 120, 150), 0.3)
    scenes.red_thread(img, d, pts, 1.0, 3, 0.34, [(0.08, 0.9), (0.5, 0.7), (0.93, 0.9)])
    glow(img, cx, cy + 10, 26, (255, 210, 200), 0.45)
    scenes.heart_at(img, cx, cy + 10, 15)
    for x, y, f in ((100, 206, 0.55), (172, 198, 0.45), (150, 172, 0.6), (90, 252, 0.4), (186, 256, 0.5)):
        twinkle(d, x, y, f, (255, 250, 230), 4)


def characters(img, d):
    person(img, 'girl', 58, 356, 'adult', 'side', 'stand', 0, 'happy', 'reach', 4, scarf=scenes.BLU)
    person(img, 'boy', 212, 344, 'adult', 'side', 'stand', 0, 'happy', 'reach', 4, flip=True, scarf=scenes.YEL)
    roof_railing(d, -6, 96, 356)
    roof_railing(d, 174, 276, 344)
    for i, (x, y, s) in enumerate(((60, 236, 1), (210, 222, 1), (122, 286, 1), (150, 300, 1))):
        put(img, 'heart', x, y, s, tint=[(255, 150, 180), (255, 120, 160)][i % 2])


def titles(img, d, ti, ar):
    lines = [ti] if len(ti) <= 5 else [ti[:len(ti) // 2], ti[len(ti) // 2:]]
    glow(img, W / 2, 84, 150, (60, 20, 80), 0.45, 70)
    for i, line in enumerate(lines):
        scenes.title(img, line, W / 2, 60 + i * 52 - (26 if len(lines) == 1 else 0), 3, 99.0)
    if ar:
        y = 60 + len(lines) * 52 - 18
        w = FONT.getlength(ar)
        put(img, 'note', W / 2 - w / 2 - 12, y, 1, tint=(255, 220, 240))
        text(img, ar, W / 2 + 4, y, (240, 230, 255), (40, 24, 70))
    tag = '像素动画 MV'
    tw = FONT.getlength(tag) + 22
    tfill(img, 'rectangle', [W / 2 - tw / 2, 440, W / 2 + tw / 2, 462], (20, 12, 40), 0.75)
    d.rectangle([W / 2 - tw / 2, 440, W / 2 + tw / 2, 462], outline=(255, 130, 170))
    d.rectangle([W / 2 - tw / 2 + 2, 442, W / 2 + tw / 2 - 2, 460], outline=(120, 50, 100))
    text(img, tag, W / 2, 451, (255, 236, 244), (60, 20, 60))


def draw_cover(ti, ar):
    img = Image.new('RGB', (W, H)); d = ImageDraw.Draw(img); d.fontmode = '1'
    sky_and_stars(img, d)
    mx, my = 135, 228
    glow(img, mx, my, 165, (255, 222, 214), 0.5)
    moon(d, mx, my, 70, (255, 246, 216))
    for x0, y0, w in ((152, 266, 90), (58, 280, 70)):
        tfill(img, 'ellipse', [x0, y0, x0 + w, y0 + 7], (120, 70, 140), 0.45)
    for i, (x, y) in enumerate(((176, 186), (188, 178), (200, 188))):
        bird(d, x, y, i * 0.4, (60, 40, 80), i)
    city(img, d)
    rooftops(img, d)
    thread_and_hearts(img, d)
    characters(img, d)
    titles(img, d, ti, ar)
    pix.vig(img, 0.3)
    return img


def main():
    ap = argparse.ArgumentParser(description='想你和我们以后 · 竖屏封面')
    ap.add_argument('--lyrics', required=True, help='MV 用的 .lrc，从里面的 [ti:] 和 [ar:] 读歌名和歌手')
    ap.add_argument('-o', '--out', default=os.path.join(HERE, 'build', '想你和我们以后_封面.png'))
    args = ap.parse_args()
    meta = {}
    for raw in open(args.lyrics, encoding='utf-8-sig'):
        m = re.match(r'\[(ti|ar):(.*)\]', raw.strip())
        if m: meta[m.group(1)] = m.group(2).strip()
    img = draw_cover(meta.get('ti', ''), meta.get('ar', ''))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    img.resize((W * SC, H * SC), Image.NEAREST).save(args.out)
    print(args.out)


if __name__ == '__main__':
    main()
