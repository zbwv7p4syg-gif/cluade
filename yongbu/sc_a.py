"""永不失联的爱 · 第一次开灯到第一遍副歌（00:38.20 – 02:17.73，第 08–24 镜）。

第一次开灯，空屋变回刚搬进来的那天：红台灯、第一张合照、关灯后的两只手、创可贴、窗外换季、灰绿行李箱；
异地的站台、错开的电话和车票；分开的周末里她还钥匙、推回蓝杯，最后一班车；回到今夜他仍倒了两杯水，旧灯泡灭了。
"""
import math
import numpy as np
from PIL import Image, ImageDraw

import pix
from pix import W, H, FONT, FONT_S, clamp, lerp, lerpc, ease, eout, ein, span, glow, blend_box, rng
import props
import world as Wd
from world import FLOOR_Y, LAMP, DESKY, CUPS
import sc_intro as I

PS = 3                       # 屋里全景人物的放大倍数
FEET = FLOOR_Y + 6
NAVY_SLEEVE = (36, 58, 96)
INDIGO = (66, 70, 150)
BRICK = (172, 74, 60)
COAT = (112, 130, 106)
PAST = dict(past=True, bed=True, marks=False, keys=0, shelf=[('books', 6), ('plant', 44)], curtain=0.25)


def boy(img, x, pose='stand', age='now', flip=False, view='side', ph=0, expr='smile', arms='auto', s=PS, y=FEET, **kw):
    pix.person(img, 'boy', x, y, age=age, view=view, pose=pose, ph=ph, expr=expr, arms=arms, s=s, flip=flip, **kw)


def girl(img, x, pose='stand', age='past', flip=False, view='side', ph=0, expr='smile', arms='auto', s=PS, y=FEET, **kw):
    pix.person(img, 'girl', x, y, age=age, view=view, pose=pose, ph=ph, expr=expr, arms=arms, s=s, flip=flip, **kw)


def day_out(tone=0.9, rain_=0.0, seed=0):
    return lambda img, d, bx, t: Wd.outside_night(img, d, bx, t, rain_, tone=tone, seed=seed)


# ---------------------------------------------------------------- 08 第一次开灯
def s_08(img, d, lt, dur, T, a):
    """拇指压下开关，旧灯泡亮起；镜头拉回全景，暖光扫过空床的压痕和对面空着的位置，他往旁边让出半步"""
    k = lt
    if k < 1.3:
        on = 0.0 if k < 0.05 else (1.0 if k > 0.22 else [0.6, 0.1, 0.9, 0.3, 1.0][int(k * 30) % 5])
        I.switch_shot(img, d, T, on, 1.0)
        return
    kk = k - 1.3
    step = ease(span(kk, 1.2, 1.8))

    def actors(im, dd, ox):
        boy(im, 470 - 14 * step + ox, flip=True, ph=pix.wph(kk) if 0 < step < 1 else 0, pose='walk' if 0 < step < 1 else 'stand',
            expr='neutral' if kk < 1.6 else 'down')
    Wd.room(img, T, I.NOW_ROOM, cam=60, amb='now', lamp_on=1.0, actors=actors)
    z = lerp(1.35, 1.0, eout(span(kk, 0, 1.6)))
    Wd.zoomv(img, z, 400, 150)
    pix.vig(img, 0.35)


# ---------------------------------------------------------------- 09 第一次搬进来
def s_09(img, d, lt, dur, T, a):
    """同一个空房构图变暖：小满抱着纸箱挪进来，把二手红台灯放到桌上；阿迟蹲在桌脚垫折纸，她用胳膊肘轻轻推他"""
    k = lt
    put = k > 1.9
    st = dict(past=True, bed=False, marks=False, keys=0, cups=[], lamp=LAMP if put else None, curtain=0.0, shelf=[],
              box_floor=150 if k > 0 else None)

    def actors(im, dd, ox):
        # 他蹲在桌脚
        nudge = math.sin(clamp((k - 2.9) / 0.5) * math.pi) if 2.9 < k < 3.4 else 0
        boy(im, 404 + ox - 3 * nudge, 'crouch', 'past', flip=False, arms='low', expr='happy' if k > 3.0 else 'smile')
        dd.rectangle([418 + ox, FEET - 6, 426 + ox, FEET - 4], fill=(240, 236, 220))          # 折纸
        # 她
        if k < 1.6:
            x = lerp(70, 470, ease(span(k, 0, 1.6)))
            girl(im, x + ox, 'walk', ph=pix.wph(k), arms='carry')
            Wd.box(dd, int(x + 12 + ox), FEET - 66, int(x + 46 + ox), FEET - 36, label=False)
            Wd.lamp_obj(dd, int(x + 30 + ox), FEET - 66, 1, 0, -1, cable=False)
        else:
            reach = k < 2.1
            girl(im, 470 + ox + (-6 * nudge), 'stand', flip=True, arms='reach' if reach else ('chest' if k > 3.4 else 'auto'),
                 expr='happy')
            if k < 1.9: Wd.lamp_obj(dd, int(450 + ox), DESKY - 6, 1, 0, -1, cable=False)
    Wd.room(img, T, st, cam=60, amb='past', lamp_on=0.0, actors=actors, outside=day_out(0.95))
    pix.vig(img, 0.25, (60, 30, 20))


# ---------------------------------------------------------------- 10 第一张合照
def s_10(img, d, lt, dur, T, a):
    """两人坐在还没铺床垫的墙边，开定时快门；最后一瞬小满靠过来，闪光一跳，定格成墙上那张照片"""
    k = lt
    lean = ease(span(k, 2.6, 3.0))
    st = dict(past=True, bed=False, marks=False, keys=0, cups=[], photo=None, curtain=0.0, shelf=[])

    def actors(im, dd, ox):
        boy(im, 232 + ox, 'sit', 'past', view='front', expr='happy' if lean > 0.5 else 'smile')
        girl(im, 262 - 6 * lean + ox, 'sit', view='front', expr='happy')
        Wd.cup(dd, 286 + ox, FEET - 2, 'blue', 2, handle=-1)
        Wd.cup(dd, 206 + ox, FEET - 2, 'amber', 2, handle=1)
        # 纸箱上的相机，定时灯一闪一闪
        Wd.box(dd, 316 + ox, FEET - 34, 352 + ox, FEET + 4, label=False)
        dd.rectangle([322 + ox, FEET - 50, 346 + ox, FEET - 34], fill=(40, 40, 48))
        dd.ellipse([328 + ox, FEET - 47, 340 + ox, FEET - 37], fill=(90, 100, 130))
        if int(k * (4 if k < 2 else 10)) % 2 == 0 and k < 3.0:
            dd.rectangle([342 + ox, FEET - 49, 344 + ox, FEET - 47], fill=(255, 60, 60))
    Wd.room(img, T, st, cam=60, amb='past', actors=actors, outside=day_out(0.9))
    Wd.zoomv(img, 1.8, 250, 150)
    if 3.0 <= k < 3.07: img.paste((255, 252, 240), (0, 0, W, H))
    if k > 3.1:
        # 定格：白边慢慢框上来，成了一张拍立得
        f = ease(span(k, 3.1, 3.7))
        b = int(lerp(0, 22, f))
        d.rectangle([0, 0, W, b], fill=(244, 238, 222)); d.rectangle([0, H - int(b * 2.2), W, H], fill=(244, 238, 222))
        d.rectangle([0, 0, b, H], fill=(244, 238, 222)); d.rectangle([W - b, 0, W, H], fill=(244, 238, 222))
    pix.vig(img, 0.25, (60, 30, 20))


# ---------------------------------------------------------------- 11 关灯之后
def s_11(img, d, lt, dur, T, a):
    """他关灯躺下；暗里她用脚碰碰他，他从被子下伸手摸到她的手；窗外一格车光让两只手短暂可见"""
    k = lt
    on = 1.0 if k < 0.35 else 0.0
    st = dict(PAST, quilt=(196, 112, 96))
    hold = ease(span(k, 1.4, 2.6))

    def actors(im, dd, ox):
        # 两个人躺在床上：枕头上两颗头，被子盖到下巴
        for who, hx, ex in (('boy', 196, 'closed'), ('girl', 222, 'closed' if k < 1.0 else 'smile')):
            h = props.head_img(who, 'past' if who == 'boy' else 'past', ex, 1, 'front')
            im.paste(h, (hx + ox, FLOOR_Y - 50), h)
        dd.rectangle([180 + ox, FLOOR_Y - 34, 330 + ox, FLOOR_Y - 18], fill=st['quilt'])
        dd.rectangle([180 + ox, FLOOR_Y - 34, 330 + ox, FLOOR_Y - 32], fill=(226, 160, 140))
        # 被子里的脚碰了一下
        bump = 2 if 0.6 < k < 0.9 else 0
        dd.rectangle([300 + ox, FLOOR_Y - 36 - bump, 310 + ox, FLOOR_Y - 34], fill=st['quilt'])
        # 两只手在被沿上慢慢碰到一起
        hx1 = lerp(198, 214, hold); hx2 = lerp(234, 218, hold)
        dd.rectangle([hx1 + ox, FLOOR_Y - 36, hx1 + 5 + ox, FLOOR_Y - 33], fill=pix.SKIN)
        dd.rectangle([hx2 + ox, FLOOR_Y - 36, hx2 + 5 + ox, FLOOR_Y - 33], fill=pix.SKIN)
        dd.point((hx1 - 1 + ox, FLOOR_Y - 34), fill=pix.PATCH)
    sweep = span(k, 2.2, 3.4)
    lights = []
    if 0 < sweep < 1:
        lights.append((lerp(500, 120, sweep) - 60, FLOOR_Y - 40, 40, 70, 0.55, (0.8, 0.86, 1.0)))
    Wd.room(img, T, st, cam=60, amb='past_night' if on == 0 else 'past_eve', lamp_on=on, actors=actors, extra_lights=lights,
            outside=lambda im, dd, bx, t: Wd.outside_night(im, dd, bx, t, 0.4, seed=2))
    Wd.zoomv(img, 2.0, 210, 150)
    pix.vig(img, 0.45)


# ---------------------------------------------------------------- 12 谁也没多说
def s_12(img, d, lt, dur, T, a):
    """她晚班回来，袖口湿了，手指上有一道浅口子；他把蓝杯推过去，给她缠一圈创可贴；她用那只手轻轻按住他的手背"""
    k = lt
    I.desk(img, d, (150, 106, 76))
    # 蓝杯被推过去
    push = ease(span(k, 0.2, 1.0))
    I.cup_top(d, lerp(120, 170, push), 70, 'blue', 3, 0.3, water=True)
    # 她的手从右边伸来，袖口滴水
    hx, hy = 300, 150
    press = ease(span(k, 3.6, 4.6))
    Wd.hand(img, hx + 40 - 20 * press, hy + 10 - 30 * press if k > 3.6 else hy + 10, 4, 'flat', flip=True, sleeve=BRICK)
    if k < 3.6:
        for i in range(4):
            ph = (k * 1.2 + i / 4) % 1
            d.rectangle([hx + 100 + i * 6, hy + 30 + ph * 60, hx + 101 + i * 6, hy + 33 + ph * 60], fill=(170, 200, 240))
        # 指尖的浅口子
        d.line([(hx - 8, hy + 6), (hx - 2, hy + 4)], fill=(210, 80, 80))
    # 他的手拿着创可贴缠过去
    wrap = ease(span(k, 1.2, 3.2))
    gx = lerp(-40, hx - 60, eout(span(k, 0.9, 1.6)))
    Wd.hand(img, gx, hy + 30, 4, 'pinch', sleeve=INDIGO, patch=True)
    if wrap > 0:
        bw = int(14 * wrap)
        d.rectangle([hx - 14, hy + 2, hx - 14 + bw, hy + 9], fill=(236, 206, 160))
        if wrap > 0.6:
            for x in range(hx - 12, hx - 2, 3): d.point((x, hy + 5), fill=(200, 160, 120))
    Wd.light(img, 'past_eve', [(240, 120, 260, 180, 0.35, Wd.WARM)])
    pix.vig(img, 0.45)


# ---------------------------------------------------------------- 13 窗外换季
def s_13(img, d, lt, dur, T, a):
    """同一个窗台从初夏雨线变成秋叶和冬霜；桌上的东西慢慢多起来，两只杯一直挨着；最后角落多出一只灰绿行李箱"""
    k = lt
    season = 0 if k < 2.5 else (1 if k < 5.0 else 2)
    clutter = lerp(0.2, 1.0, k / dur)
    case_ = k > 6.4
    st = dict(PAST, cups=[('amber', CUPS[0]), ('blue', CUPS[1])], clutter=clutter, curtain=0.4,
              case=(372, 'stand') if case_ else None, tickets=0)

    def outside(im, dd, bx, t):
        if season == 0:
            Wd.outside_night(im, dd, bx, t, 1.2, tone=0.7, seed=1)
        elif season == 1:
            Wd.outside_night(im, dd, bx, t, 0.0, tone=0.95, seed=1)
            x0, y0, x1, y1 = bx
            for i in range(14):
                r_ = rng(i)
                px = x0 + (r_.uniform(0, x1 - x0) + t * 20) % (x1 - x0); py = y0 + (r_.uniform(0, y1 - y0) + t * 26) % (y1 - y0)
                dd.rectangle([px, py, px + 2, py + 1], fill=[(214, 140, 60), (190, 96, 50), (236, 186, 90)][i % 3])
        else:
            Wd.outside_night(im, dd, bx, t, 0.0, tone=0.75, seed=1)
            x0, y0, x1, y1 = bx
            for i in range(30):
                r_ = rng(i + 50)
                px = x0 + r_.uniform(0, x1 - x0); py = y0 + (r_.uniform(0, y1 - y0) + t * 8) % (y1 - y0)
                dd.point((px, py), fill=(240, 244, 255))
            for x in range(x0, x1, 2):          # 玻璃边上的霜
                dd.point((x, y1 - 2 - (x * 7) % 4), fill=(226, 236, 250))
                dd.point((x, y0 + 1 + (x * 5) % 3), fill=(226, 236, 250))
    amb = ['past', 'past_eve', 'past'][season]
    Wd.room(img, T, st, cam=60, amb=amb, lamp_on=0.4 if season == 1 else 0.0, outside=outside)
    Wd.zoomv(img, 2.0, 392, 112)
    # 换季的遮挡：一只鸟、一阵叶子从镜头前掠过
    for tt in (2.5, 5.0):
        f = (k - tt + 0.3) / 0.6
        if 0 < f < 1:
            bx = lerp(-40, W + 40, f)
            d.polygon([(bx - 30, 100), (bx, 80), (bx + 30, 100), (bx, 92)], fill=(40, 34, 40))
    pix.vig(img, 0.3, (50, 30, 30))


# ---------------------------------------------------------------- 14 先去那座城
TRAIN_S = 2
TRAIN_BASE = Wd.PLAT_Y + 4


def her_in_window(img, d, win, expr='smile', knock=0.0, hand_up=0.0, flip=False):
    """车窗里的她：半身，玻璃反光在前面"""
    x0, y0, x1, y1 = [int(v) for v in win]
    lay, ld = Wd.layer(x1 - x0, y1 - y0)
    ld.rectangle([0, 0, x1 - x0, y1 - y0], fill=(198, 186, 160, 255))
    props.bust(lay, ld, 'girl', (x1 - x0) // 2, 10, 2, expr)
    if knock > 0 or hand_up > 0:
        hy = (y1 - y0) - 18 - int(14 * max(knock, hand_up))
        ld.rectangle([(x1 - x0) // 2 + 18, hy, (x1 - x0) // 2 + 26, hy + 10], fill=pix.SKIN + (255,))
        ld.rectangle([(x1 - x0) // 2 + 18, hy + 10, (x1 - x0) // 2 + 26, y1 - y0], fill=COAT + (255,))
    img.paste(lay, (x0, y0), lay)
    d.line([(x0 + 6, y1 - 4), (x0 + 26, y0 + 4)], fill=(236, 240, 250))
    d.line([(x0 + 12, y1 - 4), (x0 + 30, y0 + 10)], fill=(220, 226, 236))


def s_14(img, d, lt, dur, T, a):
    """小满带着灰绿箱去外地工作；阿迟从帆布袋里举起蓝杯示意替她留着，她隔着车窗用指节敲两下，笑着挥手；列车从左往右开走，他跟着走两步"""
    k = lt
    Wd.platform(img, d, T, 0.2)
    go = ein(span(k, 3.4, dur)) * 600
    tx = -60 + go

    def inside(im, dd, wins):
        if len(wins) > 1:
            w = wins[1]
            kn = 0
            for tt in (1.6, 1.95):
                if 0 < k - tt < 0.18: kn = 1
            her_in_window(im, dd, w, 'happy', knock=kn, hand_up=0.6 if 2.2 < k < 3.4 else 0)
    Wd.train_car(img, d, tx, TRAIN_BASE, T, TRAIN_S, inside, lit=0.3, cars=2)
    # 站台上的他：举起蓝杯
    walk = span(k, 3.6, 4.6)
    x = 300 + 26 * ease(walk)
    lift = ease(span(k, 0.5, 1.2))
    pix.person(img, 'boy', x, H - 6, age='past', view='side', pose='walk' if 0 < walk < 1 else 'stand', ph=pix.wph(k),
               arms='reachup' if lift > 0.5 and k < 3.4 else 'auto', s=3, flip=True, expr='smile')
    if lift > 0.5 and k < 3.4:
        Wd.cup(d, int(x - 14), H - 6 - 104, 'blue', 2, handle=-1)
    # 帆布袋
    d.rectangle([x + 4, H - 60, x + 18, H - 40], fill=(214, 200, 170)); d.line([(x + 6, H - 60), (x + 4, H - 80)], fill=(180, 166, 140))
    Wd.light(img, (0.92, 0.9, 0.96))
    pix.vig(img, 0.3)


# ---------------------------------------------------------------- 15 屏幕两头
def mini_room(img, d, box, t, warm=True, who='boy', state='sit', phone_on=0.0, badge=0.0):
    x0, y0, x1, y1 = box
    wall = (70, 74, 100) if not warm else (90, 72, 76)
    d.rectangle(box, fill=wall)
    d.rectangle([x0, y1 - 40, x1, y1], fill=(60, 50, 52) if warm else (54, 58, 74))
    # 窗
    wx = x0 + (150 if who == 'boy' else 30)
    d.rectangle([wx, y0 + 30, wx + 60, y0 + 100], fill=(150, 146, 140))
    Wd.outside_night(img, d, (wx + 3, y0 + 33, wx + 58, y0 + 98), t, 0.5, seed=9 if who == 'boy' else 13)
    # 桌子
    dx0 = x0 + 40
    d.rectangle([dx0, y1 - 74, dx0 + 150, y1 - 68], fill=Wd.DESK_L)
    d.rectangle([dx0 + 6, y1 - 68, dx0 + 10, y1 - 30], fill=Wd.DESK_D); d.rectangle([dx0 + 140, y1 - 68, dx0 + 144, y1 - 30], fill=Wd.DESK_D)
    if who == 'boy':
        Wd.lamp_obj(d, dx0 + 130, y1 - 74, 1, 1.0, -1)
    else:
        d.rectangle([dx0 + 120, y1 - 98, dx0 + 124, y1 - 74], fill=(200, 200, 210))     # 宿舍的冷白台灯
        d.polygon([(dx0 + 110, y1 - 98), (dx0 + 130, y1 - 98), (dx0 + 126, y1 - 104), (dx0 + 114, y1 - 104)], fill=(220, 224, 230))
    # 人
    sleep = state == 'sleep'
    px = dx0 + 60
    if sleep:
        h = props.head_img(who, 'past' if who == 'boy' else 'out', 'closed', 1, 'side')
        if who == 'girl': h = h.transpose(Image.FLIP_LEFT_RIGHT)
        pix.person(img, who, px, y1 - 44, age='past' if who == 'boy' else 'out', view='side', pose='sit', arms='lap', s=2,
                   flip=who == 'girl', expr='closed')
        d.rectangle([px - 18, y1 - 82, px + 18, y1 - 76], fill=INDIGO if who == 'boy' else COAT)
        img.paste(h, (int(px - 8), y1 - 96), h)
        for i in range(3):
            zz = (t * 0.8 + i / 3) % 1
            pix.text(img, 'z', px + 14 + zz * 10, y1 - 100 - zz * 20, col=(220, 220, 250), font=FONT_S, shadow=False, alpha=1 - zz)
    else:
        pix.person(img, who, px, y1 - 44, age='past' if who == 'boy' else 'out', view='side', pose='sit',
                   arms='phone' if phone_on > 0 else 'lap', s=2, flip=who == 'girl', expr='smile' if phone_on > 0 else 'neutral')
    if badge > 0 and who == 'girl':
        bx = px - 4 - 30 * badge
        d.line([(px - 2, y1 - 92), (bx, y1 - 80)], fill=(60, 120, 200))
        d.rectangle([bx - 4, y1 - 80, bx + 4, y1 - 70], fill=(240, 240, 250)); d.rectangle([bx - 3, y1 - 78, bx + 3, y1 - 76], fill=(60, 120, 200))
    # 桌上的手机
    if phone_on > 0 or sleep:
        ph_x = dx0 + 96
        c = lerpc((30, 30, 40), (170, 220, 255), phone_on)
        d.rectangle([ph_x, y1 - 77, ph_x + 10, y1 - 74], fill=c)
        if phone_on > 0:
            glow(img, ph_x + 5, y1 - 80, 30, (150, 210, 255), 0.4 * phone_on)
            # 来电的气泡：头像圆点和话筒
            bx, by = ph_x - 10, y1 - 128 - 3 * math.sin(t * 6)
            d.rounded_rectangle([bx, by, bx + 32, by + 18], 5, fill=(250, 250, 255))
            d.polygon([(bx + 12, by + 18), (bx + 18, by + 18), (bx + 14, by + 24)], fill=(250, 250, 255))
            d.ellipse([bx + 4, by + 4, bx + 13, by + 13], fill=BRICK if who == 'boy' else INDIGO)
            d.rectangle([bx + 18, by + 6, bx + 27, by + 11], fill=(80, 200, 110))


def s_15(img, d, lt, dur, T, a):
    """左右分屏：一边小满在外地宿舍摘下工牌，一边阿迟的手机在旧桌上亮起；他接起时她已经睡着。隔一晚，轮到他靠在灯下睡过去"""
    k = lt
    first = k < 3.0
    L = (0, 0, 238, H); R = (242, 0, W, H)
    if first:
        mini_room(img, d, L, T, False, 'girl', 'sit' if k < 1.4 else 'sleep', 0.0, badge=ease(span(k, 0.2, 1.0)))
        mini_room(img, d, R, T, True, 'boy', 'sit', phone_on=1.0 if 1.4 < k < 2.8 else 0.0)
    else:
        mini_room(img, d, L, T, False, 'girl', 'sit', phone_on=1.0 if k < 5.6 else 0.0)
        mini_room(img, d, R, T, True, 'boy', 'sleep')
    Wd.light(img, (0.62, 0.62, 0.8))
    d.rectangle([238, 0, 242, H], fill=(12, 12, 20))
    pix.text(img, '那 座 城', 119, 14, col=(220, 226, 240), font=FONT_S, shadow=False)
    pix.text(img, '旧 屋', 361, 14, col=(250, 226, 200), font=FONT_S, shadow=False)
    pix.vig(img, 0.35)


# ---------------------------------------------------------------- 16 熄掉的来电
def s_16(img, d, lt, dur, T, a):
    """桌上叠着几张车票，旁边那杯水没动过；他等通话屏幕暗下去，抬头时玻璃反光变成站台的玻璃"""
    k = lt
    st = dict(PAST, tickets=5, cups=[('amber', CUPS[0])], phone_desk=True, curtain=0.5)

    def post(im, dd, ox):
        glow_ = 1 - span(k, 0.6, 2.6)
        if glow_ > 0:
            dd.rectangle([420 + ox, DESKY - 3, 432 + ox, DESKY - 1], fill=lerpc((30, 30, 40), (170, 220, 255), glow_))
            glow(im, 426 + ox, DESKY - 4, 26, (150, 210, 255), 0.5 * glow_)

    def actors(im, dd, ox):
        boy(im, 380 + ox, 'sit', 'past', expr='down' if k < 2.8 else 'neutral', arms='lap')
    Wd.room(img, T, st, cam=60, amb='past_night', lamp_on=0.7, actors=actors, post=post,
            outside=lambda im, dd, bx, t: Wd.outside_night(im, dd, bx, t, 1.0, seed=5))
    Wd.zoomv(img, 2.0, 400, 128)
    # 抬头时，玻璃上的一道反光扫过去（接下一镜的车窗）
    f = span(k, 3.4, dur)
    if f > 0:
        I.car_sweep(img, lerp(-100, 600, f), 40, 0.6, 0.6)
    pix.vig(img, 0.4)


# ---------------------------------------------------------------- 17 等到她回来
def s_17(img, d, lt, dur, T, a):
    """小满在车门边出现，还是那只灰绿箱；他先抬起手想接她，又改去接箱杆；她松开手时两个人都望向了箱子"""
    k = lt
    Wd.platform(img, d, T, 0.5)
    Wd.train_car(img, d, -140, TRAIN_BASE, T, TRAIN_S, None, lit=0.4, cars=2)
    # 她从车门走出
    gx = lerp(250, 228, ease(span(k, 0, 1.2)))
    handover = ease(span(k, 2.4, 3.4))
    girl(img, gx, 'stand', 'out', flip=False, arms='drag' if handover < 1 else 'auto', y=H - 6, expr='smile' if k < 3.8 else 'down')
    cx_ = lerp(gx - 30, 300, handover)
    Wd.suitcase(d, int(cx_), H - 6, 2, handle=1.0)
    bx = 340
    up = ease(span(k, 0.8, 1.4)) * (1 - ease(span(k, 1.8, 2.4)))
    pix.person(img, 'boy', bx, H - 6, age='past', view='side', pose='stand', arms='knock' if up > 0.5 else ('reach' if handover > 0 else 'auto'),
               s=3, flip=True, expr='smile' if k < 3.8 else 'down')
    Wd.light(img, (0.96, 0.86, 0.84))
    z = lerp(1.0, 1.15, k / dur)
    Wd.zoomv(img, z, 290, 190)
    pix.vig(img, 0.3)


# ---------------------------------------------------------------- 18 她收走衣服
def s_18(img, d, lt, dur, T, a):
    """小满把抽屉旁的一叠衣服放进行李箱；阿迟蹲下压紧一处松动的拉杆，起身时看见她把挂蓝线的钥匙放进门边铁碟"""
    k = lt
    key_down = k > 4.4
    st = dict(PAST, keys=1 if key_down else 0, case=(300, 'open') if k < 3.0 else (300, 'handle'), cups=[('amber', CUPS[0]), ('blue', CUPS[1])])

    def actors(im, dd, ox):
        if k < 3.0:
            carry = (k % 1.5) < 0.75
            gx = lerp(420, 330, (k % 1.5) / 0.75) if carry else lerp(330, 420, (k % 1.5 - 0.75) / 0.75)
            girl(im, gx + ox, 'walk', 'out', flip=carry, ph=pix.wph(k), arms='carry' if carry else 'auto', expr='down')
            if carry: dd.rectangle([gx - 22 + ox, FEET - 50, gx - 4 + ox, FEET - 42], fill=(230, 210, 180))
            boy(im, 260 + ox, 'crouch', 'past', arms='low', expr='down')
        else:
            gx = lerp(330, 150, ease(span(k, 3.0, 4.2)))
            girl(im, gx + ox, 'walk' if k < 4.2 else 'stand', 'out', flip=True, ph=pix.wph(k), arms='reach' if 4.2 < k < 4.8 else 'auto',
                 expr='down')
            boy(im, 260 + ox, 'stand' if k > 3.6 else 'crouch', 'past', flip=k > 4.0, expr='down')
    pan = ease(span(k, 3.4, 5.2))
    Wd.room(img, T, st, cam=lerp(120, 30, pan), amb='past_eve', actors=actors, outside=day_out(0.85))
    if k > 4.6:
        Wd.zoomv(img, lerp(1, 2, ease(span(k, 4.6, 5.8))), 124 - 30, 160)
    pix.vig(img, 0.3)


# ---------------------------------------------------------------- 19 踮脚够那只杯
def s_19(img, d, lt, dur, T, a):
    """阿迟踮脚从高搁板取下蓝杯，递到她打开的行李箱旁；她接过杯子摩挲缺口，又把杯子轻轻推回他面前"""
    k = lt
    if k < 3.0:
        got = k > 1.4
        st = dict(PAST, shelf=[('books', 6)] + ([] if got else [('cup', 30)]), case=(300, 'open'), cups=[('amber', CUPS[0])])

        def actors(im, dd, ox):
            tip = 0.3 < k < 1.8
            boy(im, 362 + ox, 'tiptoe' if tip else 'stand', 'past', arms='reachup' if tip else ('reach' if k > 2.0 else 'auto'),
                expr='neutral')
            if got:
                cx_ = 384 + ox if k < 1.8 else 380 + ox
                cy_ = Wd.SHELF[2] + 4 if k < 1.8 else FEET - 40
                Wd.cup(dd, cx_, cy_, 'blue', 1)
            girl(im, 250 + ox, 'crouch', 'out', arms='low', expr='down')
        Wd.room(img, T, st, cam=80, amb='past_eve', actors=actors, outside=day_out(0.8))
        Wd.zoomv(img, 1.6, 330, 140)
    else:
        kk = k - 3.0
        I.desk(img, d, (124, 88, 66))
        push = ease(span(kk, 1.8, 2.8))
        cx_ = lerp(260, 200, push)
        Wd.hand(img, cx_ + 60, 150, 4, 'pinch', flip=True, sleeve=COAT)
        Wd.cup(d, int(cx_), 168, 'blue', 6, handle=1)
        rub = int(kk * 6) % 2 if kk < 1.6 else 0
        Wd.hand(img, cx_ - 70 - 40 * push, 150 + rub * 2, 4, 'open', sleeve=INDIGO, patch=True)
        Wd.light(img, 'past_eve', [(240, 120, 260, 180, 0.3, Wd.WARM)])
    pix.vig(img, 0.35)


# ---------------------------------------------------------------- 20 第一次和最后一次
def s_20(img, d, lt, dur, T, a):
    """铁碟里她的钥匙一转，切到刚搬来那天两人一起握着带蓝线的钥匙开门（暖色一瞬），切回来时他的手停在碟边"""
    k = lt
    if 2.0 < k < 3.3:
        # 暖色回忆：门锁的特写，两只手握着同一把钥匙
        img.paste((214, 160, 118), (0, 0, W, H))
        d.rectangle([0, 0, 300, H], fill=(196, 140, 100))
        for y in range(0, H, 30): d.line([(0, y), (300, y)], fill=(180, 124, 88))
        d.rectangle([150, 120, 190, 170], fill=(220, 196, 120)); d.ellipse([162, 134, 178, 150], fill=(60, 50, 40))
        Wd.key(d, 230, 142, 'hers', 3, math.pi, (k - 2) * 6)
        Wd.hand(img, 270, 150, 4, 'pinch', flip=True, sleeve=BRICK)
        Wd.hand(img, 300, 172, 4, 'grip', flip=True, sleeve=INDIGO, patch=True)
        pix.vig(img, 0.3, (90, 50, 30))
        if k < 2.12 or k > 3.18: pix.dither_fade(img, 0.6, (255, 240, 220))
        return
    pix.sky(img, ((0, (50, 46, 60)), (1, (34, 30, 42))))
    d.rectangle([0, 170, W, H], fill=(70, 50, 46)); d.rectangle([0, 166, W, 172], fill=(92, 68, 56))
    d.rectangle([0, 0, 70, 170], fill=(130, 110, 98))
    s = 4; cx, cy = 250, 186
    rw, rh = 15 * s, 4 * s
    d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh + s], fill=(56, 58, 68))
    d.ellipse([cx - rw + s, cy - rh + s, cx + rw - s, cy + rh - s], fill=(96, 98, 110))
    d.ellipse([cx - rw + 3 * s, cy - rh + 2 * s, cx + rw - 3 * s, cy + rh - 2 * s], fill=(84, 86, 98))
    turn = ease(span(k, 0.4, 1.4))
    Wd.key(d, cx - 6 * s, cy, 'hers', 3, lerp(0.0, math.pi, turn), (k - 0.4) * 5 * math.exp(-max(0, k - 1.4)))
    if k > 3.3:
        Wd.hand(img, lerp(560, 340, eout(span(k, 3.3, 4.2))), cy - 18, 4, 'open', flip=True, sleeve=INDIGO, patch=True)
    Wd.light(img, 'past_eve')
    pix.vig(img, 0.5)


# ---------------------------------------------------------------- 21 最后一班车
def s_21(img, d, lt, dur, T, a):
    """同一处站台：小满抬手碰玻璃，阿迟也抬手，手心停在几厘米外；车门合上，她的手滑出画面。他闭眼，再睁眼时站台空了"""
    k = lt
    Wd.platform(img, d, T, 0.9)
    go = ein(span(k, 2.6, 4.6)) * 700
    tx = -40 + go
    empty = k > 5.0

    def inside(im, dd, wins):
        if len(wins) > 1:
            her_in_window(im, dd, wins[1], 'sad', hand_up=1.0 if k > 0.4 else ease(k / 0.4))
    if not empty:
        Wd.train_car(img, d, tx, TRAIN_BASE, T, TRAIN_S, inside, lit=0.6, cars=2)
    up = ease(span(k, 0.6, 1.4))
    pix.person(img, 'boy', 330, H - 6, age='past', view='side', pose='stand', arms='knock' if up > 0.4 and k < 3.0 else 'auto',
               s=3, flip=True, expr='sad' if k < 4.4 else ('closed' if k < 5.0 else 'down'))
    Wd.light(img, (0.98, 0.78, 0.72))
    if 4.6 < k < 5.0: pix.dither_fade(img, 0.85, (10, 8, 14))
    pix.vig(img, 0.35)


# ---------------------------------------------------------------- 22 点一下头
def corridor(img, d, t, door_open=1.0, amb=(0.7, 0.66, 0.66), lamp_col=(255, 220, 160)):
    """楼道：左边是那扇门，右边往下的楼梯，顶上一盏感应灯"""
    img.paste((150, 140, 128), (0, 0, W, H))
    d.rectangle([0, 214, W, H], fill=(110, 100, 94))
    for y in range(220, H, 10): d.line([(0, y), (W, y)], fill=(96, 88, 84))
    d.rectangle([0, 200, W, 214], fill=(120, 110, 102))
    # 门
    d.rectangle([90, 50, 200, 214], fill=(226, 218, 204))
    d.rectangle([96, 56, 194, 214], fill=(40, 36, 40))
    dw = int(98 * door_open)
    d.rectangle([96, 56, 194 - dw, 214], fill=(170, 128, 96))
    if dw > 0: d.polygon([(194 - dw, 56), (194 - dw + 12, 48), (194 - dw + 12, 222), (194 - dw, 214)], fill=(150, 112, 86))
    # 楼梯往下
    for i in range(8):
        y = 214 + i * 8
        d.rectangle([300 + i * 18, y, W, y + 8], fill=(130, 122, 116) if i % 2 else (120, 112, 106))
    d.line([(300, 180), (W, 250)], fill=(90, 84, 80), width=3)
    # 感应灯
    d.ellipse([230, 10, 250, 20], fill=lamp_col)
    return dw


def s_22(img, d, lt, dur, T, a):
    """回楼时邻居抱着菜袋出来，阿迟扶着门、笑着点头；邻居走远后，他才从门框上慢慢把手松开"""
    k = lt
    corridor(img, d, T, 0.7)
    nx = lerp(220, 520, ease(span(k, 0.6, 3.6)))
    Wd.neighbor(img, nx, 236, 3, pix.wph(k), flip=False)
    nod = 1 if 1.0 < k < 1.4 else 0
    release = span(k, 4.2, 5.4)
    pix.person(img, 'boy', 210, 236 + nod, age='past', view='side', pose='stand', arms='reach' if release < 0.6 else 'auto', s=3,
               flip=True, expr='smile' if k < 2.4 else ('neutral' if k < 3.6 else 'down'))
    Wd.light(img, (0.8, 0.74, 0.72), [(240, 16, 240, 200, 0.4, Wd.WARM)])
    glow(img, 240, 16, 30, (255, 220, 160), 0.6)
    pix.vig(img, 0.4)


# ---------------------------------------------------------------- 23 顺手倒了两杯
def s_23(img, d, lt, dur, T, a):
    """回到今夜：现在的空屋里，他仍把热水倒进两只杯子，把蓝杯推到小满以前坐的那一侧，水汽从空位前升起来"""
    k = lt
    if k < 3.2:
        I.desk(img, d)
        I.cup_top(d, 190, 140, 'amber', 4, 0.0, water=k > 1.2)
        I.cup_top(d, 290, 140, 'blue', 4, 0.0, water=k > 2.4)
        px = 190 if k < 1.6 else 290
        pour = (0.4 < k < 1.2) or (1.8 < k < 2.6)
        # 水壶（俯视）从右上伸进来
        kx = px + 60
        d.ellipse([kx - 10, 60, kx + 50, 120], fill=(200, 204, 214)); d.ellipse([kx, 70, kx + 40, 110], fill=(170, 176, 190))
        d.rectangle([kx - 40, 86, kx - 8, 94], fill=(190, 194, 204))
        if pour:
            for i in range(12): d.point((px + (i % 3) - 1, 96 + i * 3), fill=(220, 236, 250))
        for x_ in (190, 290):
            if (x_ == 190 and k > 1.2) or (x_ == 290 and k > 2.4):
                I.cup_top(d, x_, 140, 'amber' if x_ == 190 else 'blue', 4, 0.0, water=True)
                for i in range(4):
                    ph = (T * 0.7 + i / 4) % 1
                    d.rectangle([x_ - 8 + i * 5, 130 - ph * 50, x_ - 6 + i * 5, 132 - ph * 50], fill=lerpc((210, 214, 220), (130, 120, 110), ph))
        Wd.light(img, 'now', [(400, 40, 300, 240, 0.7, Wd.WARM)])
    else:
        kk = k - 3.2
        push = ease(span(kk, 0.2, 1.2))
        st = dict(I.NOW_ROOM, cups=[('amber', CUPS[0]), ('blue', int(lerp(CUPS[1], CUPS[1] + 22, push)))], steam=1.0)

        def actors(im, dd, ox):
            boy(im, 420 + ox, 'stand', 'now', flip=False, arms='reach' if kk < 1.4 else 'auto', expr='down')
        Wd.room(img, T, st, cam=60, amb='now', lamp_on=1.0, actors=actors)
        Wd.zoomv(img, 2.0, 410, 120)
    pix.vig(img, 0.4)


# ---------------------------------------------------------------- 24 等不到水汽散完
def s_24(img, d, lt, dur, T, a):
    """他把蓝杯拉回来一点，又放回去；旧灯泡闪一下，他抬头，手想去扶灯，光先灭了"""
    k = lt
    f = 1.0
    if k > 3.6: f = [1, 0.3, 1, 0.5, 1, 1, 0.2][min(6, int((k - 3.6) * 10))]
    if k > dur - 0.35: f = 0.0
    tilt = ease(span(k, 1.8, 4.0))
    st = dict(I.NOW_ROOM, steam=1.0, cups=[('amber', CUPS[0]), ('blue', CUPS[1] + 22 - int(6 * math.sin(clamp(k / 1.6) * math.pi)))])

    def actors(im, dd, ox):
        boy(im, 440 + ox, 'stand', 'now', flip=False, arms='reach' if (k < 1.6 or k > 5.0) else 'auto',
            expr='down' if k < 3.6 else 'surprised')
    Wd.room(img, T, st, cam=60, amb='now', lamp_on=f, actors=actors)
    Wd.zoomv(img, 2.4, lerp(420, 450, tilt), lerp(150, 116, tilt))
    pix.vig(img, 0.45)
