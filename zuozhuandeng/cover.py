"""左转灯 · 竖屏封面：雨夜的路口，他靠在打着左转灯的小车旁看手机，楼上挂着一块竖排的“左转灯”霓虹招牌。
沿用 MV 的角色、小车和画法，画在 270×480 的画布上，最近邻放大 4 倍到 1080×1920。

python3 cover.py [--lyrics 歌词.lrc] [-o build/左转灯_封面.png]
"""
import argparse, math, os, re
import numpy as np
from PIL import Image, ImageDraw

import pix

# 封面是竖屏：先把共用画布换成 270×480，再导入道具和镜头模块，让光晕、倒影、楼房这些工具都按竖屏的大小裁切
W, H = 270, 480
pix.W, pix.H = W, H
pix.BAYER = pix.bayer(H, W)
import props  # noqa: E402
from props import *  # noqa: E402,F401,F403
import sc_verse as V  # noqa: E402
from pix import put  # noqa: E402

SC = 4
HERE = os.path.dirname(os.path.abspath(__file__))
T = 0.1          # 封面定格的时刻：转向灯正好亮着
GROUND = 380     # 人行道和马路的分界


def backdrop(img, d):
    img.paste(pix.vgrad(W, GROUND, ((0, (6, 4, 22)), (0.35, (22, 14, 54)), (0.7, (52, 28, 86)), (1, (84, 44, 102))), 6), (0, 0))
    r = rng(7)
    for _ in range(150):
        x, y, b = r.uniform(0, W), r.uniform(0, 230), r.random()
        c = lerpc((50, 40, 90), (255, 250, 225), 0.3 + 0.7 * b)
        d.point((x, y), fill=c)
        if b > 0.94: d.point([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], fill=lerpc(c, (50, 40, 90), 0.5))
    pix.city(img, d, 330, 3, 0, (36, 26, 70), (130, 104, 170), 60, 160, 0.25, T, 10, 22, blink=False)
    pix.city(img, d, 356, 9, 30, (24, 18, 48), (255, 204, 120), 40, 130, 0.32, T, 12, 26, blink=False)
    # 左边近处的楼
    V.facade(img, d, -10, 104, 150, 0, 44, (30, 22, 54), (46, 36, 74), 0.45, T, ground=330)
    d.rectangle([-10, 330, 104, GROUND], fill=(44, 38, 60))
    d.rectangle([4, 338, 96, GROUND], fill=(255, 196, 120)); glow(img, 50, 360, 60, (255, 190, 110), 0.25, 24)
    for k in range(3): d.line([(4 + k * 31, 338), (4 + k * 31, GROUND)], fill=(180, 120, 70))
    # 右边挂招牌的楼
    d.rectangle([248, 0, W, GROUND], fill=(26, 20, 48)); d.line([(248, 0), (248, GROUND)], fill=(44, 34, 72))
    for y in range(12, 360, 16): d.rectangle([254, y, 262, y + 8], fill=(255, 210, 130) if (y // 16) % 3 == 0 else (16, 12, 30))


def signal(img, d):
    """左上角吊着的红绿灯：红灯亮着，旁边绿色的左转箭头也亮着"""
    d.line([(0, 132), (70, 132)], fill=(60, 56, 80), width=2)
    hx, hy = 54, 140
    d.rounded_rectangle([hx - 8, hy, hx + 8, hy + 40], 3, fill=(24, 22, 34), outline=OUT)
    for j, c in enumerate([(255, 60, 60), (255, 190, 40), (60, 230, 120)]):
        on = j == 0
        d.ellipse([hx - 5, hy + 3 + j * 12, hx + 5, hy + 13 + j * 12], fill=c if on else lerpc(c, (20, 20, 30), 0.8))
        if on: glow(img, hx, hy + 8, 22, c, 0.5)
    props.arrow(img, hx, hy + 52, 1, 1.0, col=(60, 230, 120), glow_r=10)


def neon_sign(img, d, title):
    """楼上挂着的竖排霓虹招牌：顶上的左转箭头亮着，底下的右转箭头是暗的"""
    x0, x1, y0 = 168, 244, 30
    gh = 70
    y1 = y0 + 48 + gh * len(title) + 28
    glow(img, (x0 + x1) / 2, (y0 + y1) / 2, 110, AMB, 0.22, (y1 - y0) / 2 + 40)
    for by in (y0 + 30, y1 - 30):
        d.rectangle([x1, by, 250, by + 4], fill=(60, 52, 90), outline=OUT)
    d.rectangle([x0, y0, x1, y1], fill=(16, 10, 32), outline=(64, 52, 96))
    d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], outline=(32, 24, 56))
    cx = (x0 + x1) / 2
    props.arrow(img, cx, y0 + 24, 2, 1.0, glow_r=26)
    for i, ch in enumerate(title):
        g = big_glyph(ch, 4, AMB_L, AMB, (150, 66, 18))
        top = y0 + 44 + i * gh
        glow(img, cx, top + 32, 40, (255, 200, 120), 0.25)
        img.paste(g, (int(cx - 48), int(top - 12)), g)
    props.arrow(img, cx, y1 - 16, 1, 0.0, left=False, glow_r=0)
    for bx in range(x0 + 6, x1 - 4, 10): d.point((bx, y1 - 4), fill=(255, 220, 150))


def street(img, d):
    d.rectangle([0, GROUND - 6, W, GROUND], fill=(70, 64, 90)); d.rectangle([0, GROUND - 2, W, GROUND], fill=(110, 104, 128))
    d.rectangle([0, GROUND, W, H], fill=(30, 28, 44))
    lamp(img, d, 112, GROUND - 6, 1.0, 96)


def boy(img, d, x, fy):
    """他：正面站着低头看手机，手机的光照在脸上"""
    pix.person(img, 'boy', x, fy, view='front', pose='stand', expr='down', arms='phone', s=4)
    glow(img, x - 2, fy - 86, 22, (150, 210, 255), 0.45)
    c = bubble(img, d, x + 30, fy - 124, 24, 20, 1.0, thought=True, tail=(1, 1))
    if c: put(img, 'heart', c[0], c[1], 1, tint=TEAL)


def mirror_sprite(img, im, x, y, a=0.3):
    """湿地面上的倒影：上下翻转、压暗、隔行去掉"""
    im = im.transpose(Image.FLIP_TOP_BOTTOM)
    arr = np.array(im)
    arr[..., :3] = (arr[..., :3] * 0.45 + np.array((20, 18, 50)) * 0.55).astype('uint8')
    arr[1::2, :, 3] = 0
    im = with_alpha(Image.fromarray(arr), a)
    img.paste(im, (int(x), int(y)), im)


def main():
    ap = argparse.ArgumentParser(description='左转灯 · 竖屏封面')
    ap.add_argument('--lyrics', help='.lrc 歌词，只用来读 [ti:] 里的歌名')
    ap.add_argument('-o', '--out', default=os.path.join(HERE, 'build', '左转灯_封面.png'))
    args = ap.parse_args()
    if args.lyrics:
        for raw in open(args.lyrics, encoding='utf-8-sig'):
            m = re.match(r'\[(ti|ar):(.*)\]', raw.strip())
            if m: pix.META[m.group(1)] = m.group(2).strip()
    title = V.title_str()

    img = Image.new('RGB', (W, H)); d = ImageDraw.Draw(img); d.fontmode = '1'
    backdrop(img, d)
    signal(img, d)
    neon_sign(img, d, title)
    street(img, d)
    sig = blink_a(T)
    # 湿马路：先把上面的画面倒映下来，再放车和人
    reflect(img, GROUND, H - GROUND, T, a=0.6, amp=1.2, src_h=H - GROUND)
    glow(img, 206, GROUND + 50, 26, AMB, 0.35, 60)
    cx, gy = 190, 436
    V.car_reflection(img, cx, gy, 2, sig)
    car(img, cx, gy, sig, 0, 2, beams=True)
    bx, bfy = 70, 450
    bim = pix.char_img('boy', 'young', 'front', 'stand', 0, 'down', 'phone')
    bim = bim.resize((bim.width * 4, bim.height * 4), Image.NEAREST)
    mirror_sprite(img, bim, bx - pix.CX * 4, bfy + 2, 0.35)
    boy(img, d, bx, bfy)
    rain(d, T, 0, W, 0, H, 140, (96, 104, 160), 260, -2, 6)
    splashes(d, T, GROUND + 6, H, 26)
    # 底部的英文片名
    pix.blend_box(img, (0, 452, W, 474), (12, 8, 26), np.full((22, W), 0.55))
    text(img, 'LEFT  TURN  SIGNAL', W / 2, 462, (255, 236, 200), (60, 24, 30), FONT_S)
    props.arrow(img, 34, 462, 1, sig, glow_r=8)
    pix.vig(img, 0.35)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    img.resize((W * SC, H * SC), Image.NEAREST).save(args.out)
    print(args.out)


if __name__ == '__main__':
    main()
