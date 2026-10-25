"""爱错 · 分镜表。

LYRIC_SCENES 按 .lrc 里有字的句子依次排，一句一个镜头，切点就是这句的时间；片头从 0 秒演到第一句。
GAP_SCENES 依次用在空行后面超过 5 秒没有歌词的地方（这首歌只有片尾一处）；一组镜头里后面几个用 .at 写明从空行开始后第几秒切进来。
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
    # 第一段主歌：北风和红叶
    tr(A.s_north_wind, 'wipe', 0.5), tr(A.s_leaves_fall, 'dissolve', 0.3), tr(A.s_escape, 'dissolve', 0.4),
    tr(A.s_lonely, 'dissolve', 0.6), tr(A.s_winter, 'white', 0.6),
    # 第一段副歌和间奏
    tr(B.s_crossroad, 'black', 0.5), tr(B.s_heart_crack, 'black', 0.3), tr(B.s_paper_plane, 'dissolve', 0.4), tr(B.s_rewind, 'iris', 0.5),
    # 第二段主歌
    tr(C.s_album, 'white', 0.5), tr(C.s_happiness, 'dissolve', 0.5), tr(C.s_behind, 'black', 0.4), tr(C.s_mirror, 'black', 0.4),
    # 第二段副歌和间奏
    tr(C.s_run, 'flash', 0.4), tr(C.s_shatter, 'black', 0.3), tr(C.s_bird, 'white', 0.5), tr(C.s_vhs, 'blocks', 0.4),
    # 桥段
    tr(D.s_bench, 'black', 0.6), tr(D.s_search, 'dissolve', 0.5), tr(D.s_platform, 'dissolve', 0.5), tr(D.s_past, 'white', 0.4),
    # 最后一段副歌
    tr(D.s_storm, 'flash', 0.3), tr(D.s_face, 'cut'), tr(D.s_shout, 'flash', 0.3), tr(D.s_rise, 'dissolve', 0.4), tr(D.s_fall, 'white', 0.3),
    tr(D.s_land, 'dissolve', 0.3), tr(D.s_burst, 'cut'), tr(D.s_aurora, 'white', 0.8), tr(D.s_memory_girl, 'dissolve', 0.4),
    tr(D.s_catch, 'dissolve', 0.4), tr(D.s_release, 'dissolve', 0.4), tr(D.s_slam, 'flash', 0.2), tr(D.s_moon_leaf, 'white', 0.4),
]

tr(D.s_dawn, 'dissolve', 1.0); tr(D.s_end, 'black', 0.8)
D.s_end.at = 13.0

GAP_SCENES = [[D.s_dawn, D.s_end]]
