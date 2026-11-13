"""左转灯 · 分镜表。镜头函数分在三个文件里：sc_verse（片头、主歌、第一段副歌）、sc_rap（说唱段）、sc_end（后两段副歌、间奏和片尾）。

LYRIC_SCENES 按 .lrc 里有字的句子依次排，一句一个镜头；GAP_SCENES 依次用在空行后面超过 5 秒没有歌词的地方。
"""
import sc_verse as V
import sc_rap as R
import sc_end as E

SNAP = None   # render.py 填入：SNAP(T) 返回全片 T 秒处的画面（不含字幕）

s_intro = V.s_intro
s_intro.tr = 'cut'
V.s_plane.tr = 'flash'
V.s_cross_left.tr = 'arrow'; V.s_cross_left.tr_dur = 0.5
V.s_cross_right.tr = 'cut'
V.s_tally.tr = 'flash'; V.s_tally.tr_dur = 0.3
V.s_bus.tr = 'cut'
V.s_rewind.tr = 'cut'
V.s_errors.tr = 'cut'
V.s_mirror.tr = 'black'; V.s_mirror.tr_dur = 0.5
R.s_bar.tr = 'iris'; R.s_bar.tr_dur = 0.5; R.s_bar.tr_at = (240, 140)
for f in (R.s_puppet, R.s_chat, R.s_send, R.s_delete, R.s_hearts, R.s_plus1, R.s_plus1b, R.s_coin, R.s_notifs):
    f.tr = 'cut'
R.s_lookalike.tr = 'white'; R.s_lookalike.tr_dur = 0.35
R.s_send.tr = 'flash'
R.s_vortex.tr = 'iris'; R.s_vortex.tr_dur = 0.4
R.s_dashboard.tr = 'arrow'; R.s_dashboard.tr_dur = 0.5
R.s_cupid.tr = 'white'; R.s_cupid.tr_dur = 0.3
R.s_roundabout.tr = 'iris'; R.s_roundabout.tr_dur = 0.4
E.s_byes.tr = 'flash'
for f in (E.s_elevator, E.s_coin_in, E.s_rear_right, E.s_tally_plus, E.s_wheel_right, E.s_final_right):
    f.tr = 'cut'
E.s_film.tr = 'cut'
E.s_gameover.tr = 'wipe'; E.s_gameover.tr_dur = 0.4
E.s_rear_left.tr = 'arrow'; E.s_rear_left.tr_dur = 0.5
E.s_drive.tr = 'arrow_r'; E.s_drive.tr_dur = 0.6
E.s_bridge.tr = 'dissolve'; E.s_bridge.tr_dur = 0.8
E.s_curb.tr = 'black'; E.s_curb.tr_dur = 0.6
E.s_contrails.tr = 'white'; E.s_contrails.tr_dur = 0.4
E.s_blinker.tr = 'arrow'; E.s_blinker.tr_dur = 0.5
E.s_sunrise.tr = 'dissolve'; E.s_sunrise.tr_dur = 1.0
E.s_final_left.tr = 'white'; E.s_final_left.tr_dur = 0.5
E.s_outro.tr = 'dissolve'; E.s_outro.tr_dur = 1.0

LYRIC_SCENES = [
    V.s_plane, V.s_airport, V.s_novel, V.s_sketch, V.s_tug, V.s_hands, V.s_mirror,
    V.s_tally, V.s_bus, V.s_longing, V.s_rewind, V.s_globe, V.s_photo, V.s_errors, V.s_parallel, V.s_cross_left, V.s_cross_right,
    R.s_bar, R.s_puppet, R.s_chat, R.s_stairs, R.s_lookalike, R.s_jersey, R.s_send, R.s_toss, R.s_map, R.s_delete, R.s_digits,
    R.s_calendar, R.s_vortex, R.s_hearts, R.s_plus1, R.s_dashboard, R.s_cupid, R.s_coin, R.s_timelapse, R.s_roundabout,
    R.s_notifs, R.s_plus1b,
    E.s_byes, E.s_elevator, E.s_fog, E.s_film, E.s_thief, E.s_gift, E.s_gameover, E.s_coin_in, E.s_meteors, E.s_rear_left,
    E.s_rear_right,
    E.s_curb, E.s_letters, E.s_tally_plus, E.s_contrails, E.s_blinker, E.s_wheel_right,
    E.s_final_left, E.s_final_right,
]
GAP_SCENES = [[E.s_drive, E.s_bridge], E.s_sunrise, E.s_outro]
