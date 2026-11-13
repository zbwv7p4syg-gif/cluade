"""理想三旬 · 分镜表。

LYRIC_SCENES 按 .lrc 里有字的句子依次排，一句一个镜头；写 None 的句子不切镜头，接着上一个镜头演（片头横跨前两句）。
GAP_SCENES 依次用在空行后面超过 5 秒没有歌词的地方；一组镜头里后面几个用 .at 写明从间奏开始后第几秒切进来。
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
    None, None,                                   # 片头：雨后的街口和片名
    tr(A.s_south, 'wipe', 0.5), tr(A.s_radio, 'dissolve'), tr(A.s_cough, 'dissolve'), tr(A.s_lovely, 'white', 0.4),
    tr(A.s_strings, 'black', 0.3), tr(A.s_kid, 'dissolve', 0.5), tr(A.s_time, 'iris', 0.4), tr(A.s_tape, 'blocks', 0.4),
    tr(A.s_leaves, 'dissolve', 0.4),
    tr(B.s_age, 'dissolve', 0.6), tr(B.s_leave, 'white', 0.5), tr(B.s_pendulum, 'iris', 0.5), tr(B.s_sing, 'slide', 0.5),
    tr(B.s_tear, 'black', 0.4), tr(B.s_unreached, 'dissolve', 0.6),
    tr(C.s_drunk, 'flash'), tr(C.s_nameless, 'dissolve', 0.4), tr(C.s_party, 'iris', 0.4), tr(C.s_platforms, 'wipe', 0.4),
    tr(C.s_signs, 'white', 0.4), tr(C.s_wake, 'black', 0.4), tr(C.s_barren, 'white', 0.5), tr(C.s_blossom, 'dissolve', 0.5),
    tr(C.s_poems, 'black', 0.3), tr(C.s_letter, 'dissolve', 0.4), tr(C.s_wind, 'slide', 0.5),
    tr(D.s_porch, 'dissolve', 0.6), tr(D.s_boat, 'black', 0.4), tr(D.s_carousel, 'iris', 0.4), tr(D.s_busk, 'dissolve', 0.5),
    tr(D.s_puddle, 'black', 0.4), tr(D.s_endtrack, 'white', 0.5), tr(D.s_exist, 'flash'),
    tr(D.s_tea, 'dissolve', 0.5), tr(D.s_sill, 'dissolve', 0.4), tr(D.s_flicker, 'dissolve', 0.4), tr(D.s_close_book, 'dissolve', 0.4),
    tr(D.s_dawnlight, 'white', 0.4), tr(D.s_moss, 'white', 0.6),
]

tr(A.s_bridge, 'dissolve', 0.8); tr(A.s_nightcar, 'black', 0.5); A.s_nightcar.at = 5.84
tr(B.s_skytrack, 'black', 0.6); tr(B.s_whale, 'dissolve', 0.6); tr(B.s_moon, 'dissolve', 0.6)
B.s_whale.at = 7.0; B.s_moon.at = 11.82
tr(D.s_film, 'white', 0.6); tr(D.s_photos, 'dissolve', 0.5); tr(D.s_walkhome, 'black', 0.5)
D.s_photos.at = 6.59; D.s_walkhome.at = 11.37
tr(D.s_outro, 'dissolve', 1.0)

GAP_SCENES = [[A.s_bridge, A.s_nightcar], [B.s_skytrack, B.s_whale, B.s_moon], [D.s_film, D.s_photos, D.s_walkhome], D.s_outro]
