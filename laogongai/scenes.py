"""老公爱 · 分镜表。

LYRIC_SCENES 按 .lrc 里有字的句子依次排，一句一个镜头，切点就是这句的时间；None 表示这一句还在前一个镜头里（片头演到第三句）。
GAP_SCENES 用在空行后面超过 5 秒没有歌词的地方（这首歌只有片尾一处）；一组镜头里后面几个用 .at 写明从空行开始后第几秒切进来。
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
    # 片头：messed it around / see through your lies
    None, None,
    # 第一段主歌
    tr(A.s_forget, 'black', 0.4), tr(A.s_phone_piano, 'iris', 0.4), tr(A.s_rooftop, 'white', 0.4), tr(A.s_scale, 'wipe', 0.4),
    tr(A.s_crossroad, 'black', 0.4), tr(A.s_delete, 'blocks', 0.4), tr(A.s_new_day, 'dissolve', 0.4),
    # 预副歌
    tr(B.s_jeans, 'flash', 0.3), tr(B.s_crew, 'flash', 0.25), tr(B.s_party_think, 'slide', 0.3), tr(B.s_dark_night, 'black', 0.4),
    tr(B.s_hold_hand, 'white', 0.4), tr(B.s_memories, 'dissolve', 0.3), tr(B.s_burst_in, 'blocks', 0.3),
    # 第二段
    tr(B.s_letter_found, 'iris', 0.4), tr(B.s_brand, 'dissolve', 0.3), tr(B.s_voice, 'wipe', 0.4),
    tr(C.s_autotune, 'black', 0.3), tr(C.s_letters, 'dissolve', 0.3), tr(C.s_anxiety, 'dissolve', 0.3), tr(C.s_out_of_control, 'flash', 0.25),
    tr(C.s_flex, 'flash', 0.25), tr(C.s_escape, 'slide', 0.3), tr(C.s_search_city, 'iris', 0.4), tr(C.s_ignore, 'wipe', 0.4),
    tr(C.s_silly, 'blocks', 0.3), tr(C.s_beat_drop, 'black', 0.3),
    # 最后一段
    tr(D.s_pull_up, 'flash', 0.3), tr(D.s_temple, 'wipe', 0.4), tr(D.s_glass_heart, 'black', 0.3), tr(D.s_no_hide, 'dissolve', 0.25),
    tr(D.s_moth, 'black', 0.2), tr(D.s_stage, 'flash', 0.25), tr(D.s_hot, 'flash', 0.25), tr(D.s_talent, 'slide', 0.3),
]

tr(D.s_outro, 'white', 0.8); tr(D.s_end, 'black', 1.0)
D.s_end.at = 10.0

GAP_SCENES = [[D.s_outro, D.s_end]]
