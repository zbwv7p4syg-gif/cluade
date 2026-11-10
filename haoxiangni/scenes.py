"""我好想你 · 分镜表。

LYRIC_SCENES 按 .lrc 里有字的句子依次排，一句一个镜头，切点就是这句的时间；片头从 0 秒演到第一句。
GAP_SCENES 依次用在空行后面超过 5 秒没有歌词的地方：第一处是间奏的四段回忆，第二处是片尾。
一组镜头里写了 .at 的，从空行开始后第几秒切进来；没写的按小节线平分。
每个镜头的 .tr 是切进来的转场：cut、dissolve、iris、wipe、blocks、slide、flash、white、black。
"""
import sc_a as A
import sc_b as B
import sc_c as C
import sc_d as D

SNAP = None   # render.py 填入：SNAP(T) 返回全片 T 秒处的画面（不含字幕）

s_intro = A.s_intro
s_intro.tr = 'cut'


def tr(fn, kind, dur=0.4):
    fn.tr = kind; fn.tr_dur = dur
    return fn


LYRIC_SCENES = [
    # 第一段主歌
    tr(A.s_lamp_on, 'cut'), tr(A.s_big_room, 'dissolve', 0.5), tr(A.s_lamp_off, 'cut'), tr(A.s_wound, 'dissolve', 0.5),
    tr(A.s_years, 'white', 0.5), tr(A.s_leave, 'dissolve', 0.5), tr(A.s_fade, 'dissolve', 0.5), tr(A.s_numb, 'dissolve', 0.5),
    # 第一段副歌
    tr(B.s_miss1, 'flash', 0.5), tr(B.s_phone, 'black', 0.4), tr(B.s_tiptoe, 'dissolve', 0.5), tr(B.s_orbit, 'dissolve', 0.5),
    tr(B.s_tears, 'dissolve', 0.5), tr(B.s_mask, 'white', 0.4), tr(B.s_fogwrite, 'black', 0.5), tr(B.s_wipe, 'cut'),
    # 第二段主歌
    tr(C.s_table, 'black', 0.5), tr(C.s_house, 'dissolve', 0.5), tr(C.s_same, 'cut'), tr(C.s_subway, 'slide', 0.5),
    tr(C.s_river, 'white', 0.5), tr(C.s_dock, 'dissolve', 0.5), tr(C.s_tv, 'dissolve', 0.5), tr(C.s_boat, 'dissolve', 0.5),
    # 第二段副歌
    tr(C.s_shout, 'flash', 0.5), tr(C.s_sand, 'wipe', 0.5), tr(C.s_crowd, 'dissolve', 0.5), tr(C.s_carousel, 'dissolve', 0.5),
    tr(C.s_rain, 'dissolve', 0.5), tr(C.s_cafe, 'white', 0.4),
    # 最后一段
    tr(D.s_run, 'flash', 0.5), tr(D.s_mirror, 'black', 0.4), tr(D.s_letter, 'dissolve', 0.5), tr(D.s_secret, 'dissolve', 0.5),
    tr(D.s_inner1, 'iris', 0.7), tr(D.s_inner2, 'cut'), tr(D.s_inner3, 'cut'), tr(D.s_heart, 'flash', 0.5),
]
D.s_inner1.tr_at = (346, 160)

tr(B.m_bike, 'white', 0.8); tr(B.m_umbrella, 'slide', 0.6); tr(B.m_fireworks, 'slide', 0.6); tr(B.m_blossom, 'white', 0.6)
tr(D.s_dawn, 'cut'); tr(D.s_end, 'white', 0.8)
D.s_end.at = 12.16                               # 片尾第二个镜头从 309.13 秒的小节线切进来

GAP_SCENES = [[B.m_bike, B.m_umbrella, B.m_fireworks, B.m_blossom], [D.s_dawn, D.s_end]]
