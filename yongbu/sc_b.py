"""永不失联的爱 · 间奏和第二次开灯（02:17.73 – 03:32.63，第 25–37 镜）。

旧灯灭了，他拔掉插头，拉开卡住的抽屉，在旧票根下面找到用绿格布包着的备用灯泡，亲手换上；
第二次开灯，从小满的视角补齐往事：她也等过晚归的人，替他换过灯泡，把剩下的一只留在了抽屉里。
"""
import math
from PIL import Image, ImageDraw

import pix
from pix import W, H, FONT_S, clamp, lerp, lerpc, ease, eout, ein, span, glow, rng
import props
import world as Wd
from world import FLOOR_Y, LAMP, DESKY, CUPS
import sc_intro as I
from sc_a import boy, girl, PAST, FEET, INDIGO, BRICK, COAT, NAVY_SLEEVE, day_out

NOW_LIT = dict(I.NOW_ROOM, cloth_desk=True)


def rainy(im, dd, bx, t):
    Wd.outside_night(im, dd, bx, t, 1.0, seed=5)


# ---------------------------------------------------------------- 25 黑下来的房间
def s_25(img, d, lt, dur, T, a):
    """屋里只剩窗外的冷反光；他按了一次开关，等了一会，俯身拔掉插头，蓝杯里最后一缕水汽散开"""
    k = lt
    if k < 2.2:
        I.switch_shot(img, d, T, 0.0, 1.0 if 0.5 < k < 0.9 or k > 1.4 else 0.0, amb='dark')
        return
    kk = k - 2.2
    st = dict(I.NOW_ROOM, steam=clamp(1 - kk / 3.5))

    def actors(im, dd, ox):
        boy(im, 470 + ox, 'crouch' if kk > 1.2 else 'stand', 'now', flip=True, arms='low' if kk > 1.2 else 'auto', expr='down')
        # 墙上的插座和插头
        dd.rectangle([510 + ox, 176, 520 + ox, 184], fill=(230, 226, 214))
        if kk < 2.0: dd.rectangle([512 + ox, 178, 518 + ox, 182], fill=(30, 30, 34))
    Wd.room(img, T, st, cam=60, amb='dark', actors=actors, outside=rainy,
            extra_lights=[(450 - 60, 100, 120, 90, 0.25, (0.5, 0.6, 0.9))])
    Wd.zoomv(img, 1.8, 420, 140)
    pix.vig(img, 0.5)


# ---------------------------------------------------------------- 26 抽屉最里面
def drawer_cu(img, d, t, pull, beam=(150, 60), bundle_vis=1.0, tickets_slide=0.0, amb='dark', sleeve=NAVY_SLEEVE, hand_on=True,
              bundle=True, ticket_cover=0.0):
    """抽屉的低角度特写：拉开的深度 pull 0..1，抽屉里有几张旧票根，右后角一只绿格布包"""
    img.paste((40, 36, 44), (0, 0, W, H))
    d.rectangle([0, 0, W, 90], fill=Wd.DESK_L)        # 桌面下沿
    d.rectangle([0, 90, W, 100], fill=Wd.DESK_D)
    depth = int(120 * pull)
    # 抽屉盒子（俯视一点）
    x0, x1 = 90, 390
    top = 100
    d.rectangle([x0, top, x1, top + depth + 10], fill=(120, 86, 62))
    d.rectangle([x0 + 8, top, x1 - 8, top + depth], fill=(150, 112, 80))
    if depth > 30:
        # 票根
        for i in range(4):
            ox = int(lerp(0, 60 + i * 10, tickets_slide))
            tx, ty = 130 + i * 30 + ox, top + 10 + i * 6
            d.rectangle([tx, ty, tx + 46, ty + 18], fill=[(236, 214, 170), (200, 220, 236), (240, 200, 190), (236, 228, 200)][i])
            d.line([(tx + 34, ty), (tx + 34, ty + 18)], fill=(170, 150, 130))
            d.rectangle([tx + 4, ty + 4, tx + 24, ty + 6], fill=(140, 120, 110))
        if bundle and depth > 70:
            Wd.bundle(d, 340, top + 46, 3)
            if ticket_cover > 0:
                d.rectangle([316, top + 20, 362, top + 38], fill=(236, 214, 170))
    # 抽屉面板
    fy = top + depth + 10
    d.rectangle([x0 - 6, fy, x1 + 6, fy + 40], fill=Wd.DESK)
    d.rectangle([x0 - 6, fy, x1 + 6, fy + 3], fill=Wd.DESK_L)
    d.rectangle([(x0 + x1) // 2 - 12, fy + 16, (x0 + x1) // 2 + 12, fy + 22], fill=(220, 200, 150))
    if hand_on:
        Wd.hand(img, (x0 + x1) // 2 - 40, fy + 26, 4, 'grip', sleeve=sleeve, ang=-90)
    lights = []
    if beam: lights.append((beam[0], beam[1] + depth, 150, 90, 1.5, (1.0, 0.98, 0.92)))
    Wd.light(img, amb, lights)


def s_26(img, d, lt, dur, T, a):
    """他借手机手电找工具，抽屉在半途卡住；扶着桌脚再拉一次，旧票根滑到边上，露出右后角一只布包"""
    k = lt
    pull = 0.45 * ease(span(k, 0.4, 1.2))
    if k > 1.2 and k < 1.8: pull = 0.45 + 0.02 * math.sin(k * 60)       # 卡住，抖一下
    if k > 2.2: pull = lerp(0.45, 1.0, ease(span(k, 2.2, 3.4)))
    bx = lerp(150, 330, ease(span(k, 3.4, 5.6)))
    drawer_cu(img, d, T, pull, beam=(bx, 120), tickets_slide=ease(span(k, 3.0, 4.2)))
    pix.vig(img, 0.55)


# ---------------------------------------------------------------- 27 格子布里的一只灯泡
def unwrap(img, d, t, f, sleeve=NAVY_SLEEVE, beam=True, amb='dark', moon_stop=False, bulb_lit=0.0):
    """俯拍绿格布：f=0 包着，f=1 四个角都翻开，露出灯泡"""
    img.paste((70, 50, 44), (0, 0, W, H))
    cx, cy = 240, 140
    Wd.plaid(d, (cx - 90, cy - 70, cx + 90, cy + 70), 3)
    # 四个角从中间往外翻
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    for i, (sx, sy) in enumerate(corners):
        g = ease(span(f, i * 0.2, i * 0.2 + 0.35))
        tipx = lerp(cx + sx * 6, cx + sx * 90, g); tipy = lerp(cy + sy * 6, cy + sy * 70, g)
        poly = [(cx + sx * 60, cy), (cx, cy + sy * 50), (tipx, tipy)] if g < 1 else []
        if poly:
            d.polygon(poly, fill=Wd.PLAID_L if i % 2 else Wd.PLAID)
            d.line(poly + [poly[0]], fill=Wd.PLAID_D)
    if f > 0.6:
        Wd.bulb(d, cx, cy + 22, 4, bulb_lit)
        if f > 0.8:
            sp = (t * 3) % 1
            props_spark(d, cx + 10, cy - 14, sp)
    lights = [(cx, cy - 10, 170, 130, 1.4, (1.0, 0.98, 0.9))] if beam else []
    Wd.light(img, amb, lights)


def props_spark(d, x, y, p):
    r = int(2 + 6 * p)
    c = lerpc((255, 255, 240), (120, 120, 140), p)
    d.line([(x - r, y), (x + r, y)], fill=c); d.line([(x, y - r), (x, y + r)], fill=c)


def s_27(img, d, lt, dur, T, a):
    """布包用绿格棉布裹着，角上一针黄色弯月，是小满常用的那块；他翻开布角，一只完好的灯泡在手电下反光"""
    k = lt
    f = ease(span(k, 0.3, 1.6))
    unwrap(img, d, T, f)
    # 手指停在黄色缝线上
    hx = lerp(560, 352, eout(span(k, 2.0, 2.8))) if k < 4.6 else lerp(352, 560, ein(span(k, 4.6, 5.4)))
    Wd.hand(img, hx, 212, 4, 'point', flip=True, sleeve=NAVY_SLEEVE)
    if 2.8 < k < 4.6:
        glow(img, 316, 194, 14, (255, 220, 100), 0.4 + 0.2 * math.sin(k * 8))
    pix.vig(img, 0.5)


# ---------------------------------------------------------------- 28 拧上新的灯泡
def lamp_head(img, d, t, rot, bulb_in=1.0, lit=0.0, sleeve=NAVY_SLEEVE, broken=False, amb='dark', hold='pinch', patch=False):
    """台灯罩的大特写：灯罩朝上翻过来，灯泡按 rot 分段转进转出（bulb_in 0..1 拧进去的深度）"""
    img.paste((40, 44, 60), (0, 0, W, H))
    d.rectangle([0, 220, W, H], fill=Wd.DESK)
    # 灯罩（大，开口朝右上）
    cx, cy = 230, 170
    pts = [(cx - 90, cy + 40), (cx - 70, cy - 30), (cx + 30, cy - 80), (cx + 80, cy - 10), (cx - 10, cy + 60)]
    d.polygon(pts, fill=Wd.SHADE)
    d.line(pts[:3], fill=Wd.SHADE_L, width=3)
    d.polygon([(cx - 40, cy - 10), (cx + 20, cy - 50), (cx + 60, cy - 6), (cx, cy + 34)], fill=(60, 40, 40))
    d.rectangle([cx - 60, cy + 4, cx - 52, cy + 12], fill=Wd.SHADE_D)                      # 左边那处浅凹
    # 灯座口
    d.ellipse([cx + 4, cy - 30, cx + 30, cy - 4], fill=(150, 150, 156))
    by = int(lerp(cy - 70, cy - 22, bulb_in))
    step = int(rot * 8) % 4
    bulb_layer, bd = Wd.layer(80, 120)
    Wd.bulb(bd, 40, 110, 6, lit, broken)
    for k in range(3):          # 螺口的斜纹按分段旋转
        yy = 110 - 6 - k * 6 - step
        bd.line([(28, yy), (52, yy - 3)], fill=(110, 110, 118, 255), width=2)
    img.paste(bulb_layer, (cx + 17 - 40, by - 110 + 50), bulb_layer)
    Wd.hand(img, cx + 120, by - 10, 4, hold, flip=True, sleeve=sleeve, patch=patch)
    lights = []
    if lit > 0:
        lights = [(cx + 17, by - 30, 300, 220, 1.0 * lit, Wd.WARM)]
    Wd.light(img, amb, lights)
    if lit > 0: glow(img, cx + 17, by - 30, 70, (255, 230, 160), 0.6 * lit)


def s_28(img, d, lt, dur, T, a):
    """他把坏灯泡旋下来放在桌边，换上新的；插头插回插座，他把台灯扶正，把拇指放到和第一次相同的位置"""
    k = lt
    if k < 2.2:
        lamp_head(img, d, T, k * 1.5, 1 - ease(span(k, 0.2, 1.8)), broken=True)
    elif k < 4.6:
        kk = k - 2.2
        lamp_head(img, d, T, kk * 1.5, ease(span(kk, 0.3, 2.0)), broken=False)
        if kk < 0.4: pix.dither_fade(img, 1 - kk / 0.4, (20, 20, 30))
    else:
        I.switch_shot(img, d, T, 0.0, 0.0, amb='dark', dust=0.0)
    pix.vig(img, 0.45)


# ---------------------------------------------------------------- 29 第二次开灯
def s_29(img, d, lt, dur, T, a):
    """新灯亮得很稳；小满的蓝杯和绿格布都在光里。他看了看窗，暖光沿窗台展开，接到过去同一个角度的窗"""
    k = lt
    if k < 1.4:
        I.switch_shot(img, d, T, 0.0 if k < 0.04 else 1.0, 1.0, dust=0.0)
        return
    kk = k - 1.4
    st = dict(NOW_LIT, steam=0.0)

    def actors(im, dd, ox):
        boy(im, 470 + ox, 'stand', 'now', flip=True, expr='neutral')
    Wd.room(img, T, st, cam=60, amb='now', lamp_on=1.0, actors=actors, outside=rainy)
    Wd.zoomv(img, lerp(2.2, 1.6, ease(kk / 2.8)), lerp(420, 400, kk / 2.8), 120)
    if kk > 2.2: pix.dither_fade(img, (kk - 2.2) / 0.6 * 0.7, (255, 214, 150))
    pix.vig(img, 0.35)


# ---------------------------------------------------------------- 30 她也等过晚归的人
def s_30(img, d, lt, dur, T, a):
    """过去的屋里，小满坐在床靠窗的一边；阿迟值夜班，另一边的枕头压得整整齐齐。她拉开半扇窗帘，给他留着一杯水"""
    k = lt
    open_ = ease(span(k, 1.6, 2.8))
    st = dict(PAST, curtain=lerp(0.0, 0.6, open_), cups=[('amber', CUPS[0])], pillows=2, quilt=(196, 112, 96))

    def actors(im, dd, ox):
        if k < 1.6:
            girl(im, 300 + ox, 'sit', 'past', flip=False, expr='down', arms='lap')
        else:
            gx = lerp(300, 380, ease(span(k, 1.4, 2.0)))
            girl(im, gx + ox, 'walk' if k < 2.0 else 'stand', 'past', ph=pix.wph(k), arms='reachup' if 2.0 < k < 2.8 else 'auto', expr='smile')
    Wd.room(img, T, st, cam=70, amb='past_night', lamp_on=0.8, actors=actors, outside=rainy)
    Wd.zoomv(img, 1.5, 320, 140)
    pix.vig(img, 0.4)


# ---------------------------------------------------------------- 31 楼下的人影
def s_31(img, d, lt, dur, T, a):
    """小满隔着雨玻璃望见对街停靠的夜班公交，阿迟下车，走进一段没有路灯的小巷；她把红灯拖到靠窗的桌角"""
    k = lt
    if k < 1.8:
        img.paste((180, 120, 90), (0, 0, W, H))
        glow(img, 200, 110, 200, (255, 200, 140), 0.5)
        props.bust(img, d, 'girl', 220, 50, 6, 'neutral')
        # 雨玻璃盖在前面
        Wd.light(img, (0.62, 0.56, 0.62))
        props.drops_on_glass(img, d, T, (0, 0, W, H), 160, 7, col=(200, 214, 240))
        pix.rain(d, T, 0, W, 0, H, 50, (150, 160, 200), speed=200, ln=5, seed=3)
        d.rectangle([0, 0, W, 6], fill=(150, 146, 140)); d.rectangle([0, H - 6, W, H], fill=(150, 146, 140))
    else:
        kk = k - 1.8
        Wd.building(img, d, T, 0.0, ease(span(kk, 0.6, 1.4)), rain_=0.8)
        # 夜班公交停在巷口
        bx = lerp(-200, -60, eout(span(kk, 0, 0.8)))
        d.rectangle([bx, 196, bx + 150, 240], fill=(60, 120, 100)); d.rectangle([bx, 200, bx + 150, 214], fill=(230, 220, 160))
        glow(img, bx + 150, 228, 30, (255, 240, 200), 0.4)
        x = lerp(80, 200, ease(span(kk, 0.4, 2.2)))
        props.person_s(img, 'boy', x, 256, 1.5, age='past', view='side', pose='walk', ph=pix.wph(kk), expr='neutral')
    pix.vig(img, 0.4)


# ---------------------------------------------------------------- 32 旧灯先熄了一回
def s_32(img, d, lt, dur, T, a):
    """那一晚旧灯突然熄灭；小满摸黑拉开窗帘找光，从搁板上摸到一盒并排装着两只新灯泡"""
    k = lt
    f = 1.0 if k < 0.05 else 0.0
    st = dict(PAST, curtain=lerp(0.4, 0.9, ease(span(k, 0.6, 1.4))), shelf=[('books', 6), ('bulbbox', 34)], cups=[('amber', CUPS[0])])
    got = k > 2.8

    def actors(im, dd, ox):
        if k < 1.6:
            girl(im, 400 + ox, 'stand', 'past', arms='reachup' if k > 0.6 else 'auto', expr='surprised')
        else:
            girl(im, 384 + ox, 'tiptoe' if k < 2.9 else 'stand', 'past', flip=True, arms='reachup' if k < 2.9 else 'carry', expr='neutral')
            if got: Wd.bulb_box(dd, 352 + ox, FEET - 50, 1)
    if got: st['shelf'] = [('books', 6)]
    Wd.room(img, T, st, cam=70, amb='past_night', lamp_on=f, actors=actors, outside=rainy,
            extra_lights=[(400, 110, 110, 120, 0.45, (0.55, 0.65, 1.0))])
    Wd.zoomv(img, 1.7, 330, 130)
    pix.vig(img, 0.45)


# ---------------------------------------------------------------- 33 先用一只
def s_33(img, d, lt, dur, T, a):
    """她拔掉插头，用绿格布隔着手拆下旧灯泡，拧上一只新的；亮灯后把另一只包进布里；窗光重新落到湿巷里"""
    k = lt
    if k < 2.8:
        lamp_head(img, d, T, k * 1.5, ease(span(k, 0.6, 2.0)), lit=1.0 if k > 2.2 else 0.0, sleeve=BRICK, amb='past_night')
        # 隔着手的格子布
        if k < 2.2: Wd.plaid(d, (330, 60, 372, 88), 1)
    elif k < 4.8:
        kk = k - 2.8
        unwrap(img, d, T, 1 - ease(span(kk, 0.4, 1.8)), beam=False, amb='past_eve', bulb_lit=0)
        Wd.hand(img, lerp(560, 330, eout(span(kk, 0.0, 0.6))), 120, 4, 'flat', flip=True, sleeve=BRICK)
    else:
        kk = k - 4.8
        Wd.building(img, d, T, 0.0, 1.0, rain_=1.0)
    pix.vig(img, 0.4)


# ---------------------------------------------------------------- 34 她留过许多次灯
def s_34(img, d, lt, dur, T, a):
    """固定巷口：一场雨、落叶、一层薄霜。每次阿迟拐进来，都先抬头确认同一格暖窗；他进门后，她才安心缩回被窝"""
    k = lt
    seg = dur / 3
    i = min(2, int(k / seg))
    kk = k - i * seg
    if i == 1 and 0.9 < kk < 1.6:
        # 中段短切一次：屋里，她缩回被窝
        st = dict(PAST, quilt=(196, 112, 96), curtain=0.5)

        def actors(im, dd, ox):
            h = props.head_img('girl', 'past', 'smile', 1, 'front')
            im.paste(h, (226 + ox, FLOOR_Y - 48), h)
            dd.rectangle([186 + ox, FLOOR_Y - 34, 330 + ox, FLOOR_Y - 18], fill=st['quilt'])
        Wd.room(img, T, st, cam=60, amb='past_night', lamp_on=0.8, actors=actors, outside=rainy)
        Wd.zoomv(img, 2.2, 230, 150)
        return
    season = ['rain', 'leaf', 'frost'][i]
    Wd.building(img, d, T, 0.05 * i, 1.0, season=season, rain_=1.0 if i == 0 else 0, seed=i)
    x = lerp(60, 240, ease(span(kk, 0.0, 1.4)))
    look = 1.4 < kk < 2.0
    props.person_s(img, 'boy', x, 258, 1.5, age='past', view='back' if look else 'side', pose='stand' if look else 'walk', ph=pix.wph(kk),
                   expr='smile')
    if look:
        Wd.heart(d, x, 196 - 3 * math.sin(kk * 8), 0.3, (255, 200, 140), out=(60, 30, 30))
    pix.vig(img, 0.35)


# ---------------------------------------------------------------- 35 她把备用的留下
def s_35(img, d, lt, dur, T, a):
    """行李箱打开时，阿迟背过身去按紧拉杆。小满从搁板取下那包灯泡，手停在行李箱和抽屉之间，最后把布包推到抽屉右后角，纸票盖住布角"""
    k = lt
    if k < 3.6:
        took = k > 1.0
        st = dict(PAST, case=(250, 'open'), shelf=[('books', 6)] + ([] if took else [('bundle', 34)]), cups=[('amber', CUPS[0])],
                  drawer=12 if k > 2.6 else 0)

        def actors(im, dd, ox):
            boy(im, 210 + ox, 'crouch', 'past', flip=True, arms='low', expr='down')
            gx = 372 if k < 1.4 else lerp(372, 300, ease(span(k, 1.4, 2.0))) if k < 2.4 else lerp(300, 430, ease(span(k, 2.4, 3.2)))
            girl(im, gx + ox, 'tiptoe' if k < 1.0 else 'stand', 'out', flip=1.4 < k < 2.4, arms='reachup' if k < 1.0 else 'carry',
                 expr='down')
            if took: Wd.bundle(dd, int(gx + 18 + ox) if not (1.4 < k < 2.4) else int(gx - 18 + ox), FEET - 44, 1)
        Wd.room(img, T, st, cam=60, amb='past_eve', actors=actors, outside=day_out(0.7))
        Wd.zoomv(img, 1.5, 300, 140)
    else:
        kk = k - 3.6
        drawer_cu(img, d, T, 1.0, beam=None, amb='past_eve', sleeve=COAT, hand_on=kk < 1.6, ticket_cover=ease(span(kk, 1.0, 2.0)))
        if kk < 1.2:
            Wd.hand(img, lerp(500, 380, ease(kk / 1.2)), 150, 4, 'flat', flip=True, sleeve=COAT)
    pix.vig(img, 0.4)


# ---------------------------------------------------------------- 36 走之前的那一眼
def s_36(img, d, lt, dur, T, a):
    """从小满身后重看告别那天：阿迟在铁碟旁看钥匙；她等他抬眼，把箱杆放低了一次，最后先把红灯按亮，才拎箱出门"""
    k = lt
    lamp = 1.0 if k > 3.2 else 0.0
    st = dict(PAST, keys=1, door=ease(span(k, 3.8, 4.4)), hall=(180, 160, 120), cups=[('amber', CUPS[0])])

    def actors(im, dd, ox):
        boy(im, 150 + ox, 'stand', 'past', flip=True, expr='down' if k < 2.6 else 'sad')
        if k < 3.0:
            girl(im, 300 + ox, 'stand', 'out', view='back', arms='auto', expr='neutral')
            Wd.suitcase(dd, int(330 + ox), FEET, 1, handle=1.0 if not (1.2 < k < 1.8) else 0.4)
        elif k < 3.6:
            girl(im, 470 + ox, 'stand', 'out', arms='reach', expr='down')
        else:
            gx = lerp(470, 80, ease(span(k, 3.6, 5.6)))
            if gx > 70:
                girl(im, gx + ox, 'walk', 'out', flip=True, ph=pix.wph(k), arms='drag', expr='down')
                Wd.suitcase(dd, int(gx + 30 + ox), FEET, 1, handle=1.0)
    Wd.room(img, T, st, cam=20, amb='past_eve', lamp_on=lamp, actors=actors, outside=day_out(0.6))
    pix.vig(img, 0.35)


# ---------------------------------------------------------------- 37 一只坏灯泡
def s_37(img, d, lt, dur, T, a):
    """阿迟把换下来的坏灯泡放进空纸盒，手掌压平绿格布；他把台灯往小满从前挪过的窗角推过去，玻璃里的光斑也跟着动"""
    k = lt
    mv = ease(span(k, 2.2, 4.0))
    st = dict(NOW_LIT, lamp=(int(lerp(LAMP[0], LAMP[0] - 30, mv)), LAMP[1]))

    def actors(im, dd, ox):
        boy(im, 440 + ox, 'stand', 'now', arms='reach', expr='down')
        if k < 1.6:
            Wd.bulb_box(dd, 400 + ox, DESKY, 1)
            Wd.bulb(dd, 409 + ox, int(lerp(DESKY - 24, DESKY - 4, ease(k / 1.4))), 1, 0, True)
    Wd.room(img, T, st, cam=60, amb='now', lamp_on=1.0, actors=actors, outside=rainy)
    Wd.zoomv(img, 2.0, 440, 120)
    pix.vig(img, 0.4)
