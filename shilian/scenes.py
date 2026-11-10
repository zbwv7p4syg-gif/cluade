"""永不失联的爱 · 分镜表。

LYRIC_SCENES 按 .lrc 里有字的句子依次排，一句一个镜头，切点就是这句的时间；写 None 表示这句不换镜头。片头从 0 秒演到第一句。
GAP_SCENES 依次用在空行后面超过 5 秒没有歌词的地方；写 None 表示不换镜头，接着演上一镜；
一组镜头里后面几个用 .at 写明从空行开始后第几秒切进来。
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
    # 第一段主歌：她躲起来发呆，他到处找
    tr(A.s_hide, 'dissolve', 0.8), tr(A.s_worry, 'black', 0.5), tr(A.s_bad, 'dissolve', 0.4), tr(A.s_weird, 'wipe', 0.5),
    tr(A.s_clouds, 'white', 0.5), tr(A.s_ground_cloud, 'dissolve', 0.5), tr(A.s_circle, 'dissolve', 0.5), tr(A.s_lean, 'dissolve', 0.6),
    # 第一段副歌：连上了，又分开
    tr(B.s_give, 'flash', 0.4), tr(B.s_cans, 'iris', 0.5), tr(B.s_sea, 'white', 0.5), tr(B.s_story, 'blocks', 0.4), tr(B.s_fate, 'dissolve', 0.5),
    tr(B.s_you, 'flash', 0.3), tr(B.s_link, 'slide', 0.5), tr(B.s_hands, 'black', 0.6), tr(B.s_booth, 'dissolve', 0.5), tr(B.s_still, 'cut'),
    # 呜 / 啊啊啊啊 + 间奏：一颗心飞过太空送到她窗前
    tr(B.s_hum, 'dissolve', 0.8), tr(B.s_inter, 'flash', 0.3),
    # 第二段主歌：等待和回头
    tr(C.s_roof, 'white', 0.6), tr(C.s_wait, 'dissolve', 0.5), tr(C.s_lonely, 'black', 0.4), tr(C.s_kid, 'iris', 0.5),
    tr(C.s_moon2, 'dissolve', 0.5), tr(C.s_crowd, 'blocks', 0.4), tr(C.s_turn, 'white', 0.5), tr(C.s_there, 'dissolve', 0.5),
    # 第二段副歌：重新连上，永不失联
    tr(D.s_call, 'flash', 0.3), tr(D.s_tower, 'iris', 0.5), tr(D.s_msgs, 'blocks', 0.4), tr(D.s_hug, 'white', 0.5), tr(D.s_cute, 'flash', 0.4),
    tr(D.s_me, 'flash', 0.3), tr(D.s_planet, 'slide', 0.5), tr(D.s_mount, 'white', 0.6), tr(D.s_believe, 'dissolve', 0.6),
    # oh oh / 啊啊啊：月亮上
    tr(D.s_float, 'white', 1.0), None,
]

tr(D.s_dawn, 'white', 1.2); tr(D.s_end, 'black', 1.0)
D.s_end.at = 11.5

GAP_SCENES = [None, None, [D.s_dawn, D.s_end]]
