"""几分之几 · 分镜表。

LYRIC_SCENES 按 .lrc 里有字的句子依次排，一句一个镜头，切点就是这句的时间；片头从 0 秒演到第一句。
GAP_SCENES 依次用在空行后面超过 5 秒没有歌词的地方（这首歌只有片尾一处）。
每个镜头的 .tr 是切进来的转场：cut、dissolve、iris、wipe、blocks、slide、pie、flash、white、black。
"""
import sc_a as A
import sc_b as B
import sc_c as C
import sc_d as D

SNAP = None

s_intro = A.s_intro
s_intro.tr = 'cut'


def tr(fn, kind, dur=0.4):
    fn.tr = kind; fn.tr_dur = dur
    return fn


LYRIC_SCENES = [
    tr(A.s_sun, 'dissolve', 0.8), tr(A.s_wind, 'dissolve', 0.4), tr(A.s_beautiful, 'dissolve', 0.5),
    tr(A.s_golden, 'flash', 0.4), tr(A.s_world, 'wipe', 0.4), tr(A.s_sure, 'dissolve', 0.4),
    tr(B.s_enter, 'white', 0.5), tr(B.s_piece, 'dissolve', 0.4), tr(B.s_eyes, 'dissolve', 0.4), tr(B.s_south, 'white', 0.4),
    tr(B.s_wait, 'slide', 0.4), tr(B.s_roof, 'black', 0.5), tr(B.s_for_me, 'dissolve', 0.5),
    tr(C.s_game, 'white', 0.5), tr(C.s_memories, 'blocks', 0.4), tr(C.s_complete, 'dissolve', 0.4), tr(C.s_because, 'flash', 0.3),
    tr(C.s_leave, 'dissolve', 0.4), tr(C.s_once, 'dissolve', 0.5), tr(C.s_breath, 'black', 0.5),
    tr(D.s_dawn, 'white', 0.6), tr(D.s_mine, 'dissolve', 0.4), tr(D.s_station, 'dissolve', 0.5), tr(D.s_aging, 'dissolve', 0.4),
    tr(D.s_remember, 'white', 0.6),
]

tr(D.s_end, 'cut')
GAP_SCENES = [[D.s_end]]
