"""永不失联的爱 · 后半段副歌和尾奏（03:32.63 – 05:27，第 38–55 镜）。

原来她也一直留着灯。他擦掉今天的杯印，踮脚揭下合照，难过一会儿，收好两只杯子；
拍下最后一盏灯，打开旧对话，却把照片留在手机里，把合照包进绿格布揣进贴近心口的口袋（04:48.30）。
天亮了，他关灯、留下两把钥匙、抱着红灯下楼；旧窗还亮着，太阳已经照进去了。片名在晨光里再出现一次。
"""
import math
from PIL import Image, ImageDraw

import pix
from pix import W, H, FONT, FONT_S, clamp, lerp, lerpc, ease, eout, ein, span, glow, rng
import props
import world as Wd
from world import FLOOR_Y, LAMP, DESKY, CUPS, PHOTO
import sc_intro as I
from sc_a import boy, girl, PAST, FEET, INDIGO, BRICK, COAT, NAVY_SLEEVE, corridor
from sc_b import NOW_LIT, rainy

LATE = dict(NOW_LIT, photo='wall')
NO_PHOTO = dict(NOW_LIT, photo='pale')


def dawn_out(tone):
    return lambda im, dd, bx, t: Wd.outside_night(im, dd, bx, t, max(0, 0.6 - tone), tone=tone, seed=5)


# ---------------------------------------------------------------- 38 原来她也一直留着灯
def s_38(img, d, lt, dur, T, a):
    """从过去他晚归的巷口仰看：楼里许多格窗都暗着，只有同一格亮着。切进窗里，他一个人站在灯后，低头把开关线理顺"""
    k = lt
    if k < 3.4:
        Wd.building(img, d, T, 0.0, 1.0, rain_=0.5)
        z = lerp(1.0, 1.5, ease(span(k, 1.0, 3.4)))
        wx, wy = Wd.our_window()
        Wd.zoomv(img, z, wx + Wd.WIN_W / 2, wy + Wd.WIN_H / 2)
    else:
        def actors(im, dd, ox):
            boy(im, 470 + ox, 'stand', 'now', flip=True, arms='low', expr='down')
        Wd.room(img, T, LATE, cam=60, amb='now', lamp_on=1.0, actors=actors, outside=rainy)
        Wd.zoomv(img, 2.0, 430, 120)
    pix.vig(img, 0.4)


# ---------------------------------------------------------------- 39 两圈杯印
def s_39(img, d, lt, dur, T, a):
    """他把杯子提起来，桌板上露出一新一旧两圈印；他拿抹布擦掉今天的水，旧印擦不掉，便把布摊平放在旁边"""
    k = lt
    I.desk(img, d)
    lift = ease(span(k, 0.2, 1.0))
    wipe = ease(span(k, 1.6, 4.4))
    # 旧印：深色，擦不掉
    d.ellipse([170, 110, 230, 170], outline=(84, 56, 42), width=4)
    # 新印：湿的，被擦掉
    if wipe < 0.95:
        r_ = rng(3)
        for ang in range(0, 360, 6):
            if ang / 360 > wipe:
                px = 260 + 30 * math.cos(math.radians(ang)); py = 150 + 30 * math.sin(math.radians(ang))
                d.rectangle([px - 1, py - 1, px + 2, py + 2], fill=(170, 150, 140))
    if lift < 1:
        I.cup_top(d, 260, int(150 - 40 * lift), 'blue', 4, 0.3)
    # 抹布（绿格布的一角放在旁边，抹布是灰白的）
    rx = lerp(360, 260, wipe) if k < 4.4 else 380
    ry = 150 + 10 * math.sin(k * 6) if 1.6 < k < 4.4 else 220
    d.rectangle([rx - 24, ry - 16, rx + 24, ry + 16], fill=(214, 210, 200)); d.rectangle([rx - 24, ry + 12, rx + 24, ry + 16], fill=(180, 176, 168))
    Wd.hand(img, rx + 30, ry, 4, 'flat', flip=True, sleeve=NAVY_SLEEVE)
    Wd.light(img, 'now', [(380, 40, 320, 260, 0.8, Wd.WARM)])
    pix.vig(img, 0.45)


# ---------------------------------------------------------------- 40 这次够的是照片
def s_40(img, d, lt, dur, T, a):
    """他踮脚揭下高处的拍立得，胶带连着墙皮翘起一点；另一只手护住照片正面，慢慢放平脚跟。墙上留下一块浅色的矩形"""
    k = lt
    got = k > 2.4
    st = dict(NOW_LIT, photo='pale' if got else 'wall')

    def actors(im, dd, ox):
        tip = 0.6 < k < 3.6
        boy(im, 206 + ox, 'tiptoe' if tip else 'stand', 'now', arms='reachup' if tip else 'chest', expr='neutral' if k < 3.6 else 'down')
        if got:
            py = PHOTO[1] + 4 if k < 3.6 else FEET - 66
            dd.rectangle([214 + ox, py, 226 + ox, py + 14], fill=(244, 238, 222))
    Wd.room(img, T, st, cam=60, amb='now', lamp_on=1.0, actors=actors, outside=rainy)
    Wd.zoomv(img, 2.0, 170, 110)
    pix.vig(img, 0.4)


# ---------------------------------------------------------------- 41 那天两个人挨得很近
def s_41(img, d, lt, dur, T, a):
    """终于看见完整的拍立得：刚搬进来时两个靠着墙的人。画面短暂活过来，小满往他肩上再靠一点，又回到手里的照片"""
    k = lt
    img.paste((40, 40, 56), (0, 0, W, H))
    live = 1.4 < k < 4.4
    lean_q = 0 if not live else min(4, int(span(k, 1.6, 3.0) * 4 + 0.5))
    ph = Wd.photo_big(lean_q).resize((112 * 2, 88 * 2), Image.NEAREST)
    if not live:
        ph = props.sepia(ph, 0.25)
    pw, phh = ph.size
    x0, y0 = (W - pw) // 2, 18
    d.rectangle([x0 - 10, y0 - 10, x0 + pw + 10, y0 + phh + 40], fill=(244, 238, 222))
    d.rectangle([x0 - 11, y0 - 11, x0 + pw + 11, y0 + phh + 41], outline=(30, 26, 38))
    img.paste(ph, (x0, y0))
    if live:
        if k < 1.6 or k > 4.2: pix.dither_fade(img, 0.4, (255, 230, 190))
        glow(img, W / 2, H / 2, 260, (255, 200, 140), 0.2)
    # 拇指从她的脸边轻轻移开
    tx = lerp(330, 380, ease(span(k, 4.6, 5.8)))
    Wd.hand(img, tx + 40, 200, 4, 'grip', flip=True, sleeve=NAVY_SLEEVE)
    Wd.light(img, (0.82, 0.78, 0.82), [(W / 2, 0, 300, 260, 0.5, Wd.WARM)])
    pix.vig(img, 0.45)


# ---------------------------------------------------------------- 42 可以难过一会儿
def s_42(img, d, lt, dur, T, a):
    """他把照片举到光里，闭上眼；手在半空抖了一下，一滴泪落在自己的袖口上，纸面保持干净"""
    k = lt
    pix.sky(img, ((0, (40, 44, 64)), (1, (24, 26, 40))))
    expr = 'sad' if k < 1.4 else ('closed' if k < 4.6 else 'cry')
    props.bust(img, d, 'boy', 190, 34, 6, 'closed' if k > 1.4 else 'sad')
    # 泪
    if k > 2.2:
        f = span(k, 2.2, 3.4)
        ty = lerp(120, 236, ein(f))
        if f < 1:
            d.rectangle([222, ty, 225, ty + 6], fill=(190, 220, 255)); d.point((223, ty - 1), fill=(240, 250, 255))
        else:
            sp = span(k, 3.4, 4.0)
            d.ellipse([214 - 6 * sp, 236, 232 + 6 * sp, 242], fill=lerpc((190, 220, 255), (60, 80, 120), sp))
    # 照片举在光里，手抖一下
    sh = 2 if 1.8 < k < 2.1 else 0
    px, py = 340 + sh, 70
    d.rectangle([px - 2, py - 2, px + 60, py + 72], fill=(30, 26, 38))
    d.rectangle([px, py, px + 58, py + 70], fill=(244, 238, 222))
    img.paste(Wd.photo_big(2).resize((50, 40), Image.BOX), (px + 4, py + 4))
    Wd.hand(img, px + 20, py + 80, 4, 'grip', ang=90, sleeve=NAVY_SLEEVE)
    Wd.light(img, 'now', [(470, 40, 320, 260, 1.0, Wd.WARM)])
    glow(img, 470, 40, 80, (255, 210, 150), 0.4)
    pix.vig(img, 0.45)


# ---------------------------------------------------------------- 43 这次没急着擦
def s_43(img, d, lt, dur, T, a):
    """远处邻居开窗收衣，阿迟习惯性点点头，嘴角刚抬起又放下；他拉开半扇帘，在没人看他的窗边站了一会；天色从墨蓝过渡到灰蓝"""
    k = lt
    tone = lerp(0.0, 0.3, k / dur)
    top = lerpc((14, 20, 40), (90, 110, 150), tone / 0.3)
    pix.sky(img, ((0, top), (1, lerpc(top, (150, 160, 190), 0.4))))
    # 对面的楼和那扇开着的窗
    d.rectangle([40, 30, 400, H], fill=lerpc((30, 34, 54), (80, 88, 110), tone / 0.3))
    for wx in range(60, 400, 70):
        for wy in range(50, H, 70):
            d.rectangle([wx, wy, wx + 40, wy + 44], fill=lerpc((24, 28, 44), (110, 120, 140), tone / 0.3))
    nwx, nwy = 200, 120
    d.rectangle([nwx, nwy, nwx + 40, nwy + 44], fill=(236, 210, 150))
    open_ = ease(span(k, 0.4, 1.2))
    d.rectangle([nwx + 40 - int(18 * open_), nwy, nwx + 40, nwy + 44], fill=(150, 160, 180))
    d.line([(nwx - 30, nwy + 6), (nwx + 70, nwy + 6)], fill=(120, 120, 130))
    for i, c in enumerate([(230, 120, 110), (120, 170, 220), (240, 240, 230)]):
        if i >= int(span(k, 1.4, 3.4) * 3):
            d.rectangle([nwx - 24 + i * 22, nwy + 7, nwx - 10 + i * 22, nwy + 24], fill=c)
    props.person_s(img, 'girl', nwx + 20, nwy + 46, 1.0, age='past', view='front', pose='stand', arms='up' if k < 3.4 else 'auto',
                   tint=(60, 50, 60))
    # 近景：窗框、窗帘，他的半身轮廓（背对着我们）
    d.rectangle([0, 0, 40, H], fill=(150, 146, 140)); d.rectangle([W - 40, 0, W, H], fill=(150, 146, 140))
    cur = lerp(0, 120, ease(span(k, 3.8, 5.2)))
    d.rectangle([W - 40 - 140 + int(cur), 0, W - 40, H], fill=(196, 182, 160))
    for x in range(W - 180 + int(cur), W - 40, 6): d.line([(x, 0), (x, H)], fill=(176, 162, 140))
    nod = 3 if 2.0 < k < 2.4 else 0
    props.person_s(img, 'boy', 150, H + 70 + nod, 6, age='now', view='back', pose='stand', tint=(26, 30, 44))
    Wd.light(img, (0.8, 0.84, 0.96))
    pix.vig(img, 0.4)


# ---------------------------------------------------------------- 44 喝完自己的那杯
def s_44(img, d, lt, dur, T, a):
    """阿迟坐回地板，双手捂住琥珀杯，慢慢喝一口；桌上的蓝杯还在，水汽已经散尽"""
    k = lt
    st = dict(NO_PHOTO, cups=[('blue', CUPS[1] + 22)])

    def actors(im, dd, ox):
        boy(im, 360 + ox, 'sitfloor', 'now', arms='carry', expr='closed' if 0.6 < k < 1.6 else 'down')
        up = ease(span(k, 0.3, 0.8)) * (1 - ease(span(k, 1.6, 2.0)))
        Wd.cup(dd, int(380 + ox), int(FEET - 40 - 10 * up), 'amber', 2)
    Wd.room(img, T, st, cam=60, amb='now', lamp_on=1.0, actors=actors, outside=dawn_out(0.1))
    Wd.zoomv(img, 1.8, 380, 150)
    pix.vig(img, 0.4)


# ---------------------------------------------------------------- 45 把两只杯子都带走
def s_45(img, d, lt, dur, T, a):
    """他倒掉蓝杯里凉掉的水，把两只杯子分别用旧报纸包好，塞进箱子不同的格子；合上半边箱盖，给台灯留出位置"""
    k = lt
    img.paste((60, 46, 40), (0, 0, W, H))
    # 俯视的纸箱，中间一道隔板
    bx0, by0, bx1, by1 = 120, 50, 360, 230
    d.rectangle([bx0 - 8, by0 - 8, bx1 + 8, by1 + 8], fill=Wd.CARD)
    d.rectangle([bx0, by0, bx1, by1], fill=Wd.CARD_D)
    d.rectangle([(bx0 + bx1) // 2 - 3, by0, (bx0 + bx1) // 2 + 3, by1], fill=Wd.CARD)
    d.rectangle([bx0, (by0 + by1) // 2 - 3, (bx0 + bx1) // 2, (by0 + by1) // 2 + 3], fill=Wd.CARD)

    def newspaper(cx, cy, r):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(222, 218, 204))
        for y in range(int(cy - r + 4), int(cy + r - 2), 4):
            d.line([(cx - r + 6, y), (cx + r - 6, y)], fill=(160, 156, 150))
        d.line([(cx - r, cy), (cx + r * 0.6, cy - r * 0.6)], fill=(190, 186, 176))
    if k < 1.4:
        # 倒掉的水
        I.cup_top(d, 420, 120, 'blue', 4, 1.0, water=k < 0.8)
        if 0.3 < k < 1.1:
            for i in range(8): d.point((440 + (i % 2), 150 + i * 6 + (k * 40) % 6), fill=(190, 220, 250))
    a1 = ease(span(k, 1.4, 2.6)); a2 = ease(span(k, 2.8, 4.0))
    if a1 > 0: newspaper(lerp(430, 180, a1), lerp(120, 95, a1), 32)
    if a2 > 0: newspaper(lerp(430, 180, a2), lerp(120, 185, a2), 32)
    lid = ease(span(k, 4.6, 5.8))
    if lid > 0:
        d.polygon([(bx0 - 8, by0 - 8), (bx0 - 8 + 130 * lid, by0 - 20 * lid), (bx0 - 8 + 130 * lid, by1 + 20 * lid), (bx0 - 8, by1 + 8)],
                  fill=lerpc(Wd.CARD, (230, 200, 150), 0.2))
    hx = 470 if k < 4.4 else lerp(470, 600, span(k, 4.4, 5.0))
    Wd.hand(img, hx, 200, 4, 'pinch', flip=True, sleeve=NAVY_SLEEVE)
    Wd.light(img, 'now', [(420, 30, 300, 240, 0.8, Wd.WARM)])
    pix.vig(img, 0.45)


# ---------------------------------------------------------------- 46 最后一次往外看
def s_46(img, d, lt, dur, T, a):
    """门外有人走过，阿迟下意识去开门，楼道里只剩一小段晃动的光；他站住，等人影走远，轻轻把门合到留一道缝"""
    k = lt
    op = ease(span(k, 0.8, 1.6)) * (1 - 0.85 * ease(span(k, 3.6, 5.2)))
    hall = lerpc((60, 56, 50), (200, 176, 120), 0.6 + 0.4 * math.sin(k * 9) if k < 3 else 0.3)
    st = dict(NO_PHOTO, door=op, hall=hall)

    def actors(im, dd, ox):
        boy(im, 128 + ox, 'stand', 'now', flip=True, arms='reach' if k < 5.4 else 'auto', expr='surprised' if 1.4 < k < 2.2 else 'down')
    Wd.room(img, T, st, cam=10, amb='now', lamp_on=1.0, actors=actors, outside=dawn_out(0.15))
    Wd.zoomv(img, 2.0, 100, 130)
    pix.vig(img, 0.45)


# ---------------------------------------------------------------- 47 一张没有发出去的照片
def lamp_thumb():
    im = Image.new('RGB', (40, 30), (40, 40, 60)); d = ImageDraw.Draw(im)
    d.rectangle([0, 22, 40, 30], fill=Wd.DESK)
    Wd.lamp_obj(d, 26, 24, 1, 1.0, -1, cable=False)
    d.ellipse([8, 8, 22, 22], outline=(255, 210, 140))
    return im


def s_47(img, d, lt, dur, T, a):
    """他用手机拍下最后一盏灯，把照片选进他们的旧对话；发送图标亮起，拇指悬在上方，迟迟没有落下"""
    k = lt
    img.paste((30, 30, 44), (0, 0, W, H))
    glow(img, 360, 60, 160, (255, 190, 110), 0.3)
    th = lamp_thumb().resize((60, 45), Image.NEAREST)
    if k < 1.4:
        # 取景：屏幕上是那盏灯，快门一闪
        sc = Wd.phone(img, d, 240, 140, 2, 'off', T)
        x0, y0, x1, y1 = [int(v) for v in sc]
        big = lamp_thumb().resize((x1 - x0, int((x1 - x0) * 0.75)), Image.NEAREST)
        img.paste(big, (x0, y0 + 40))
        if 0.9 < k < 1.0: d.rectangle(sc, fill=(255, 255, 255))
    else:
        Wd.phone(img, d, 240, 140, 2, 'chat', T, 1.0, thumb=th if k > 2.0 else None, send_on=1.0 if k > 2.6 else 0.0)
    # 拇指悬在发送键上方，抖一抖
    hover = 2 * math.sin(k * 5) if k > 2.6 else 0
    Wd.hand(img, 330, 248 + hover - (20 if k > 2.6 else 0), 4, 'grip', ang=40, sleeve=NAVY_SLEEVE)
    pix.vig(img, 0.45)


# ---------------------------------------------------------------- 48 把话留在这里
def s_48(img, d, lt, dur, T, a):
    """他退出发送界面，缩略图回到相册，锁上手机倒扣在桌上；窗玻璃倒映出一盏红灯和他的半张脸"""
    k = lt
    if k < 2.4:
        img.paste((30, 30, 44), (0, 0, W, H))
        glow_ = 1 - ease(span(k, 1.4, 2.2))
        Wd.phone(img, d, 240, 140, 2, 'album' if k > 0.6 else 'chat', T, glow_, thumb=lamp_thumb().resize((60, 45), Image.NEAREST),
                 send_on=0.0, items=[] if k > 0.6 else None)
        Wd.hand(img, 330, 228, 4, 'grip', ang=40, sleeve=NAVY_SLEEVE)
        pix.vig(img, 0.45)
    else:
        # 窗玻璃里的倒影
        tone = 0.2
        Wd.outside_night(img, d, (0, 0, W, H), T, 0.3, seed=11, tone=tone)
        f = props.face('boy', 'down', 6)
        props.dpaste(img, f, 250, 20, 0.35)
        lay, ld = Wd.layer(140, 150)
        Wd.lamp_obj(ld, 80, 140, 4, 1.0, -1, cable=False)
        props.dpaste(img, lay, 40, 100, 0.55)
        glow(img, 70, 160, 50, (255, 190, 110), 0.35)
        d.rectangle([0, H - 30, W, H], fill=(70, 60, 56))
        d.rectangle([300, H - 36, 340, H - 30], fill=(20, 20, 28))        # 倒扣的手机
        pix.vig(img, 0.4)


# ---------------------------------------------------------------- 49 再看一眼那块地板
def s_49(img, d, lt, dur, T, a):
    """他蹲到墙边，把手放在拍立得里小满曾经坐的位置；后半句响起时，他抬头看见现在只有自己，手慢慢收回"""
    k = lt
    look = k > 3.6                    # 04:42.57

    def actors(im, dd, ox):
        if not look:
            props.ghost(im, 'girl', 262 + ox, FEET, 3, 0.25 * (1 - span(k, 2.6, 3.6)), age='past', view='front', pose='sit', expr='happy')
        boy(im, 228 + ox, 'crouch', 'now', arms='low' if k < 4.6 else 'auto', expr='down' if not look else 'sad')
    Wd.room(img, T, NO_PHOTO, cam=60, amb=Wd.amb_mix('now', 'pre_dawn', 0.2), lamp_on=1.0, actors=actors, outside=dawn_out(0.2))
    Wd.zoomv(img, 1.9, 250, 150)
    pix.vig(img, 0.4)


# ---------------------------------------------------------------- 50 布包换了内容
def s_50(img, d, lt, dur, T, a):
    """他把取下来的照片放在绿格布上，沿旧折痕折起；布角的黄色弯月仍留在外面"""
    k = lt
    img.paste((70, 56, 50), (0, 0, W, H))
    cx, cy = 240, 140
    Wd.plaid(d, (cx - 90, cy - 70, cx + 90, cy + 70), 3)
    fold = ease(span(k, 0.6, 2.4))
    if fold < 0.5:
        d.rectangle([cx - 30, cy - 36, cx + 30, cy + 36], fill=(244, 238, 222))
        img.paste(Wd.photo_big(2).resize((52, 42), Image.BOX), (cx - 26, cy - 32))
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    for i, (sx, sy) in enumerate(corners):
        g = ease(span(fold, i * 0.2, i * 0.2 + 0.4))
        if g <= 0: continue
        tipx = lerp(cx + sx * 90, cx + sx * 4, g); tipy = lerp(cy + sy * 70, cy + sy * 4, g)
        poly = [(cx + sx * 64, cy), (cx, cy + sy * 54), (tipx, tipy)]
        d.polygon(poly, fill=Wd.PLAID_L if i % 2 else Wd.PLAID)
        d.line(poly + [poly[0]], fill=Wd.PLAID_D)
    Wd.moon_glyph(d, cx + 66, cy + 50, 3)
    Wd.light(img, Wd.amb_mix('now', 'pre_dawn', 0.4), [(380, 20, 300, 260, 0.7, Wd.WARM)])
    pix.vig(img, 0.4)


# ---------------------------------------------------------------- 51 藏在贴近心口的地方
def s_51(img, d, lt, dur, T, a):
    """阿迟把折好的布包塞进外套内袋，手掌在口袋外压一下；镜头缓慢退远，窗框上的灰蓝一点点变成清晨的粉金"""
    k = lt
    tone = ease(span(k, 1.0, dur))

    def actors(im, dd, ox):
        boy(im, 300 + ox, 'stand', 'now', view='front', arms='chest', expr='closed' if 0.2 < k < 3.0 else 'smile')
    z = lerp(3.0, 1.0, ease(span(k, 0.8, dur - 0.6)))
    Wd.room(img, T, NO_PHOTO, cam=60, amb=Wd.amb_mix('pre_dawn', 'dawn', tone), lamp_on=lerp(1.0, 0.5, tone), actors=actors,
            outside=dawn_out(lerp(0.3, 1.0, tone)))
    Wd.zoomv(img, z, 240, lerp(140, 135, ease(k / dur)))
    if k < 2.4:
        # 胸前口袋处一点暖光：揣好了
        glow(img, W / 2 - 4, H / 2 + 10, 40, (255, 210, 150), 0.35 * (1 - k / 2.4)) if z > 2.5 else None
    pix.vig(img, 0.35)


# ---------------------------------------------------------------- 52 够亮了
def s_52(img, d, lt, dur, T, a):
    """天亮后，他关灯、拔插头，把线卷好；日光落在灯刚才照过的位置。他把台灯放进纸箱，把自己的钥匙放进铁碟"""
    k = lt
    if k < 2.0:
        I.switch_shot(img, d, T, 1.0 if k < 0.9 else 0.0, 1.0, amb='dawn', dust=0.0, outside_tone=1.0)
        return
    if k < 5.4:
        kk = k - 2.0
        st = dict(NO_PHOTO, cups=[], lamp=LAMP if kk < 1.6 else None, cloth_desk=False, box_floor=420)

        def actors(im, dd, ox):
            boy(im, 470 + ox, 'stand' if kk < 1.2 else 'crouch', 'now', flip=True, arms='carry' if 1.2 < kk < 2.4 else 'auto', expr='smile')
            if 1.6 < kk < 2.6:
                Wd.lamp_obj(dd, int(lerp(450, 422, span(kk, 1.6, 2.6)) + ox), int(lerp(DESKY, 172, span(kk, 1.6, 2.6))), 1, 0, -1, cable=False)
            if kk > 2.6:
                dd.polygon([(412 + ox, 162), (420 + ox, 150), (428 + ox, 162)], fill=Wd.SHADE)
        Wd.room(img, T, st, cam=60, amb='dawn', actors=actors, outside=dawn_out(1.0),
                extra_lights=[(380, 170, 130, 60, 0.35, (1.2, 1.0, 0.8))])
        Wd.zoomv(img, 1.6, 400, 140)
    else:
        kk = k - 5.4
        dish_two(img, d, kk, T)
    pix.vig(img, 0.3)


def dish_two(img, d, k, T):
    """铁碟特写：他把自己的黄铜钥匙放到她那把旁边"""
    pix.sky(img, ((0, (190, 176, 168)), (1, (150, 136, 128))))
    d.rectangle([0, 170, W, H], fill=(120, 90, 74)); d.rectangle([0, 166, W, 172], fill=(150, 116, 92))
    d.rectangle([0, 0, 70, 170], fill=(200, 186, 170))
    s = 4; cx, cy = 250, 186
    rw, rh = 15 * s, 4 * s
    d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh + s], fill=(80, 82, 94))
    d.ellipse([cx - rw + s, cy - rh + s, cx + rw - s, cy + rh - s], fill=(140, 142, 154))
    d.ellipse([cx - rw + 3 * s, cy - rh + 2 * s, cx + rw - 3 * s, cy + rh - 2 * s], fill=(124, 126, 138))
    Wd.key(d, cx - 6 * s, cy, 'hers', 3, 0.0, 0)
    drop = ease(span(k, 0.3, 1.0))
    Wd.key(d, cx + 5 * s, int(lerp(cy - 60, cy - 2, drop)), 'his', 3, 0.3)
    if k < 1.6:
        Wd.hand(img, lerp(420, 560, span(k, 1.0, 1.6)), cy - 70, 4, 'open', flip=True, sleeve=NAVY_SLEEVE)
    Wd.light(img, 'dawn', [(380, 0, 300, 260, 0.4, (1.2, 1.0, 0.8))])


# ---------------------------------------------------------------- 53 两把钥匙都留在门内
def s_53(img, d, lt, dur, T, a):
    """他抱箱跨过门槛，回头确认铁碟，拉上门；下楼时纸箱上露出红灯罩一小角，自然光一阶一阶照亮台阶"""
    k = lt
    close = ease(span(k, 2.0, 3.2))
    corridor(img, d, T, 1.0 - close, lamp_col=(220, 220, 210))
    x = 150 if k < 3.4 else lerp(150, 520, ease(span(k, 3.4, dur)))
    y = 236 if x < 300 else 236 + (x - 300) * 0.44
    pix.person(img, 'boy', x, y, age='now', view='side', pose='walk' if k > 3.4 else 'stand', ph=pix.wph(k), arms='carry', s=3,
               flip=1.0 < k < 2.0, expr='smile')
    bx = x + (14 if not (1.0 < k < 2.0) else -46)
    Wd.box(d, int(bx), int(y - 70), int(bx + 34), int(y - 44), label=False)
    d.polygon([(bx + 10, y - 70), (bx + 18, y - 80), (bx + 26, y - 70)], fill=Wd.SHADE)
    # 一阶一阶亮起来的晨光
    sun = span(k, 3.0, dur)
    Wd.light(img, Wd.amb_mix((0.7, 0.68, 0.7), 'dawn', sun), [(W, 120, 260, 200, 0.6 * sun, (1.2, 1.0, 0.75))])
    pix.vig(img, 0.3)


# ---------------------------------------------------------------- 54 走到街上
def s_54(img, d, lt, dur, T, a):
    """阿迟从楼道口走到清晨的街上，扶稳红灯罩，在原先总会回头的巷口停一下，抬眼看了一次旧窗，继续往前"""
    k = lt
    Wd.building(img, d, T, 1.0, 0.0, rain_=0.0, empty_ours=True, sun=ease(span(k, 0, 3)), wet=0)
    x = lerp(240, 400, ease(span(k, 0.0, 3.0))) if k < 5.0 else lerp(400, 560, ease(span(k, 5.0, dur)))
    look = 3.0 < k < 5.0
    sc = lerp(1.6, 2.6, ease(span(k, 0.0, dur)))
    y = lerp(250, 290, ease(span(k, 0, dur)))
    props.person_s(img, 'boy', x, y, sc, age='now', view='back' if look else 'side', pose='stand' if look else 'walk', ph=pix.wph(k),
                   arms='carry', expr='smile')
    if not look:
        Wd.box(d, int(x + 6 * sc / 2), int(y - 30 * sc), int(x + 22 * sc), int(y - 18 * sc), label=False)
        d.polygon([(x + 10 * sc, y - 30 * sc), (x + 14 * sc, y - 34 * sc), (x + 18 * sc, y - 30 * sc)], fill=Wd.SHADE)
    pix.vig(img, 0.25)


# ---------------------------------------------------------------- 55 最后一格窗
def s_55(img, d, lt, dur, T, a):
    """镜头留在旧屋外：红灯的位置空了，晨光穿过旧窗，照亮玻璃边缘；阿迟从画面下方走出去，窗帘轻动，片名在晨光里再出现一次"""
    k = lt
    Wd.building(img, d, T, 1.0, 0.0, rain_=0.0, empty_ours=True, sun=1.0, wet=0)
    wx, wy = Wd.our_window()
    # 窗帘轻动
    sway = 2 * math.sin(k * 1.6)
    d.rectangle([wx + 1, wy + 1, wx + 7 + sway, wy + Wd.WIN_H - 1], fill=(236, 214, 180))
    glow(img, wx + Wd.WIN_W / 2, wy + Wd.WIN_H / 2, 46, (255, 222, 160), 0.5)
    if k < 3.6:
        props.person_s(img, 'boy', lerp(300, 330, k / 3.6), lerp(270, 330, ease(k / 3.6)), 3, age='now', view='back', pose='walk',
                       ph=pix.wph(k), arms='carry')
    if k > 2.0:
        al = ease(span(k, 2.0, 3.4))
        I.draw_title(img, W / 2, 40, 2, [2.0 + 0.12 * i for i in range(len(I.TITLE_FULL))], k, flick=False, alpha=al, glow_a=0.3)
    if k > dur - 1.2: pix.dither_fade(img, (k - (dur - 1.2)) / 1.2 * 0.6, (255, 236, 210))
    pix.vig(img, 0.25)
