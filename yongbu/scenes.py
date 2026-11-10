"""永不失联的爱 · 分镜表。

SHOTS = [(开始秒数, 镜头函数), ...]，按参考剧情的时间轴排：两次开灯卡在 00:38.20 和 02:44.60，
最后一个"心"字（04:48.30）按住胸前的口袋。片头把前奏前 19.5 秒用来亮出片名，原来的前奏七镜压缩到后面。
每个镜头的 .tr 是切进来的转场：cut、dissolve、iris、wipe、blocks、slide、flash、white、black。
"""
import sc_intro as I
import sc_a as A
import sc_b as B
import sc_c as C

SNAP = None   # render.py 填入：SNAP(T) 返回全片 T 秒处的画面（不含字幕）


def tr(fn, kind, dur=0.4):
    fn.tr = kind; fn.tr_dur = dur
    return fn


def ts(s):
    m, x = s.split(':')
    return int(m) * 60 + float(x)


SHOTS = [
    # 片头和前奏
    (0.0, tr(I.s_title, 'cut')),
    (19.5, tr(I.s_01, 'black', 0.5)),
    (22.5, tr(I.s_02, 'dissolve', 0.4)),
    (25.5, tr(I.s_03, 'black', 0.4)),
    (28.3, tr(I.s_04, 'dissolve', 0.4)),
    (31.0, tr(I.s_05, 'dissolve', 0.4)),
    (33.6, tr(I.s_06, 'dissolve', 0.4)),
    (35.8, tr(I.s_07, 'dissolve', 0.4)),
    # 第一次开灯 · 住在一起的那几年
    (ts('00:38.20'), tr(A.s_08, 'cut')),
    (ts('00:42.60'), tr(A.s_09, 'white', 0.5)),
    (ts('00:46.80'), tr(A.s_10, 'dissolve', 0.4)),
    (ts('00:50.83'), tr(A.s_11, 'black', 0.4)),
    (ts('00:55.13'), tr(A.s_12, 'dissolve', 0.4)),
    (ts('01:01.40'), tr(A.s_13, 'dissolve', 0.5)),
    (ts('01:08.97'), tr(A.s_14, 'slide', 0.5)),
    (ts('01:15.60'), tr(A.s_15, 'wipe', 0.5)),
    (ts('01:21.60'), tr(A.s_16, 'dissolve', 0.4)),
    # 第一遍副歌 · 分开的周末
    (ts('01:26.33'), tr(A.s_17, 'dissolve', 0.4)),
    (ts('01:32.80'), tr(A.s_18, 'dissolve', 0.4)),
    (ts('01:39.40'), tr(A.s_19, 'dissolve', 0.4)),
    (ts('01:45.77'), tr(A.s_20, 'dissolve', 0.4)),
    (ts('01:52.10'), tr(A.s_21, 'dissolve', 0.4)),
    (ts('01:58.33'), tr(A.s_22, 'black', 0.4)),
    (ts('02:04.17'), tr(A.s_23, 'dissolve', 0.4)),
    (ts('02:10.87'), tr(A.s_24, 'dissolve', 0.4)),
    # 间奏 · 抽屉里的灯泡
    (ts('02:17.73'), tr(B.s_25, 'cut')),
    (ts('02:24.00'), tr(B.s_26, 'dissolve', 0.4)),
    (ts('02:30.30'), tr(B.s_27, 'dissolve', 0.4)),
    (ts('02:37.00'), tr(B.s_28, 'dissolve', 0.4)),
    # 第二次开灯 · 她的那一半回忆
    (ts('02:44.60'), tr(B.s_29, 'cut')),
    (ts('02:48.80'), tr(B.s_30, 'white', 0.5)),
    (ts('02:53.00'), tr(B.s_31, 'dissolve', 0.4)),
    (ts('02:57.13'), tr(B.s_32, 'cut')),
    (ts('03:01.43'), tr(B.s_33, 'dissolve', 0.4)),
    (ts('03:07.87'), tr(B.s_34, 'dissolve', 0.4)),
    (ts('03:15.23'), tr(B.s_35, 'dissolve', 0.4)),
    (ts('03:21.97'), tr(B.s_36, 'dissolve', 0.4)),
    (ts('03:28.00'), tr(B.s_37, 'black', 0.4)),
    # 后半段副歌 · 把合照收好
    (ts('03:32.63'), tr(C.s_38, 'dissolve', 0.5)),
    (ts('03:39.13'), tr(C.s_39, 'dissolve', 0.4)),
    (ts('03:45.77'), tr(C.s_40, 'dissolve', 0.4)),
    (ts('03:51.97'), tr(C.s_41, 'dissolve', 0.4)),
    (ts('03:58.17'), tr(C.s_42, 'dissolve', 0.4)),
    (ts('04:04.67'), tr(C.s_43, 'dissolve', 0.4)),
    (ts('04:09.70'), tr(C.s_44, 'dissolve', 0.4)),
    (ts('04:13.77'), tr(C.s_45, 'dissolve', 0.4)),
    (ts('04:20.23'), tr(C.s_46, 'dissolve', 0.4)),
    (ts('04:26.40'), tr(C.s_47, 'dissolve', 0.4)),
    (ts('04:32.77'), tr(C.s_48, 'dissolve', 0.4)),
    (ts('04:38.97'), tr(C.s_49, 'dissolve', 0.4)),
    (ts('04:45.60'), tr(C.s_50, 'dissolve', 0.4)),
    (ts('04:48.30'), tr(C.s_51, 'cut')),
    # 尾奏 · 窗外天亮
    (ts('04:56.97'), tr(C.s_52, 'white', 0.8)),
    (ts('05:05.00'), tr(C.s_53, 'dissolve', 0.5)),
    (ts('05:13.10'), tr(C.s_54, 'dissolve', 0.5)),
    (ts('05:21.30'), tr(C.s_55, 'dissolve', 0.6)),
]
