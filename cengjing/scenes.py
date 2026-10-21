"""曾经是情侣 · 分镜表。

LYRIC_SCENES 按 .lrc 里有字的句子依次排，一句一个镜头；GAP_SCENES 依次用在空行后面超过 5 秒没有歌词的地方。
"""
import sc_a as A
import sc_b as B
import sc_c as C
import sc_d as D

SNAP = None   # render.py 填入：SNAP(T) 返回全片 T 秒处的画面（不含字幕）

s_intro = A.s_intro
s_intro.tr = 'cut'
A.s_wind.tr = 'cut'
A.s_rift.tr = 'cut'
A.s_rain.tr = 'dissolve'; A.s_rain.tr_dur = 0.5
A.s_streams.tr = 'iris'; A.s_streams.tr_dur = 0.5
A.s_river.tr = 'dissolve'; A.s_river.tr_dur = 0.6

B.s_years.tr = 'white'; B.s_years.tr_dur = 0.5
B.s_dreamfield.tr = 'dissolve'; B.s_dreamfield.tr_dur = 0.6
B.s_till.tr = 'thread'; B.s_till.tr_dur = 0.5
B.s_hope.tr = 'dissolve'; B.s_hope.tr_dur = 0.4
B.s_smile.tr = 'white'; B.s_smile.tr_dur = 0.3
B.s_road.tr = 'dissolve'; B.s_road.tr_dur = 0.6
B.s_fork.tr = 'cut'
B.s_trudge.tr = 'black'; B.s_trudge.tr_dur = 0.4
B.s_endless.tr = 'dissolve'; B.s_endless.tr_dur = 0.4
B.s_world.tr = 'iris'; B.s_world.tr_dur = 0.6
B.s_station.tr = 'black'; B.s_station.tr_dur = 0.5
B.s_hourglass.tr = 'dissolve'; B.s_hourglass.tr_dur = 0.6
C.s_rewind.tr = 'cut'
C.s_meet.tr = 'white'; C.s_meet.tr_dur = 0.4
C.s_apart.tr = 'black'; C.s_apart.tr_dur = 0.4
C.s_change.tr = 'iris'; C.s_change.tr_dur = 0.4
C.s_dash.tr = 'wipe'; C.s_dash.tr_dur = 0.4
C.s_crash.tr = 'flash'
C.s_lock.tr = 'white'; C.s_lock.tr_dur = 0.4
C.s_film.tr = 'black'; C.s_film.tr_dur = 0.3
C.s_deep.tr = 'dissolve'; C.s_deep.tr_dur = 0.5
C.s_wilt.tr = 'black'; C.s_wilt.tr_dur = 0.4
C.s_forget.tr = 'dissolve'; C.s_forget.tr_dur = 0.6
C.s_appear.tr = 'cut'
D.s_nana1.tr = 'flash'
D.s_couple.tr = 'white'; D.s_couple.tr_dur = 0.4
D.s_nana2.tr = 'iris'; D.s_nana2.tr_dur = 0.5
D.s_tomorrow.tr = 'dissolve'; D.s_tomorrow.tr_dur = 0.6
D.s_nana3.tr = 'black'; D.s_nana3.tr_dur = 0.4
D.s_heart.tr = 'dissolve'; D.s_heart.tr_dur = 0.6
D.s_unrelated.tr = 'dissolve'; D.s_unrelated.tr_dur = 0.6
D.s_outro.tr = 'dissolve'; D.s_outro.tr_dur = 1.0

LYRIC_SCENES = [
    A.s_wind, A.s_rift, A.s_rain, A.s_streams, A.s_river,
    B.s_years, B.s_dreamfield, B.s_till, B.s_hope, B.s_smile, B.s_road, B.s_fork, B.s_trudge, B.s_endless, B.s_world, B.s_station,
    B.s_hourglass,
    C.s_rewind, C.s_meet, C.s_apart, C.s_change, C.s_dash, C.s_crash, C.s_lock, C.s_film, C.s_deep, C.s_wilt, C.s_forget, C.s_appear,
    D.s_nana1, D.s_couple, D.s_nana2, D.s_tomorrow, D.s_nana3, D.s_heart, D.s_unrelated,
]
GAP_SCENES = [D.s_outro]
