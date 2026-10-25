"""爱错 · 像素 MV：在 480×270 的画布上逐帧绘制，用 ffmpeg 最近邻放大 4 倍到 1920×1080，分块并行编码后合成音乐。

从 lixiang/render.py 改来：字幕下面是一道风，一片心形小红叶跟着演唱进度被吹向右边；括号里的和声用冰蓝色单独排一行，
整句都是和声时就放在主字幕的位置。唱完以后字幕只多停两秒，长间奏里不会一直挂着。

python3 render.py 歌曲.mp3 --lyrics 歌词.lrc [--stills 3,60,140]
"""
import argparse, math, multiprocessing, os, re, shutil, subprocess
import numpy as np
from PIL import Image, ImageDraw

import pix
from pix import W, H, FPS, FONT, clamp, eout, ease, lerp, lerpc
import props
import motifs
import scenes

SC = 4
HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, 'build')
LINES = []; SCHED = []
DUR = 0.0; NFR = 0


# ---------------------------------------------------------------- 音频分析
def analyse(song):
    """每帧音量；动态规划跟踪节拍，再用和声变化最大的相位定出小节线"""
    sr, hop, n = 22050, 256, 2048
    pcm = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', song, '-ac', '1', '-ar', str(sr), '-f', 's16le', '-']),
                        np.int16).astype(np.float32) / 32768
    spf = sr / FPS
    pcm_p = np.pad(pcm, (0, max(0, int((NFR + 1) * spf) - len(pcm))))
    rms = np.array([np.sqrt(np.mean(pcm_p[int(i * spf):int((i + 1) * spf)] ** 2) + 1e-9) for i in range(NFR)])
    pix.AUDIO['amp'] = np.clip(rms / (np.percentile(rms, 95) + 1e-9), 0, 1)

    fr = (len(pcm) - n) // hop
    win = np.hanning(n)
    S = np.abs(np.array([np.fft.rfft(pcm[i * hop:i * hop + n] * win) for i in range(fr)]))
    freqs = np.fft.rfftfreq(n, 1 / sr)
    edges = np.geomspace(60, 8000, 41)
    B = np.stack([S[:, (freqs >= edges[j]) & (freqs < edges[j + 1])].sum(1) for j in range(40)], 1)
    on = np.concatenate([[0], np.maximum(0, np.diff(np.log1p(B * 20), axis=0)).sum(1)])
    on = np.maximum(on - np.convolve(on, np.ones(64) / 64, 'same'), 0); on /= on.std() + 1e-9
    fps = sr / hop

    # 先用自相关找节拍周期（40–90 BPM 之间），再做动态规划
    seg = on[:int(min(len(on), 240 * fps))]
    ac = np.correlate(seg, seg, 'full')[len(seg) - 1:]
    lags = np.arange(len(ac))
    lo, hi = int(fps * 60 / 90), int(fps * 60 / 40)
    period = lo + int(np.argmax(ac[lo:hi]))
    score = on.copy(); back = -np.ones(len(on), int)
    for i in range(len(on)):
        a, b = max(0, i - 2 * period), i - period // 2
        if b <= 0: continue
        prev = np.arange(a, b)
        pen = -100 * np.log((i - prev) / period) ** 2
        j = int(np.argmax(score[prev] + pen))
        score[i] = on[i] + score[prev][j] + pen[j]; back[i] = prev[j]
    i = int(np.argmax(score[-2 * period:])) + len(on) - 2 * period
    beats = []
    while i >= 0: beats.append(i); i = back[i]
    beats = np.array(beats[::-1]) / fps
    pix.AUDIO['beats'] = beats

    pc = np.round(12 * np.log2(np.maximum(freqs, 1) / 440)) % 12
    band = (freqs > 80) & (freqs < 2000)
    C = np.stack([S[:, band & (pc == k)].sum(1) for k in range(12)], 1)
    C /= C.sum(1, keepdims=True) + 1e-9

    def chroma(t0, t1):
        a, b = max(0, int(t0 * fps)), min(len(C), int(t1 * fps))
        return C[a:b].mean(0) if b > a else np.zeros(12)
    hc = np.array([np.abs(chroma(t, t + 0.6) - chroma(t - 0.6, t)).sum() for t in beats])
    ph = max(range(4), key=lambda p: hc[p::4].mean())
    pix.AUDIO['bars'] = beats[ph::4]


def load(song, lyrics):
    global DUR, NFR
    for raw in open(lyrics, encoding='utf-8-sig'):
        raw = raw.strip()
        m = re.match(r'\[(ti|ar):(.*)\]', raw)
        if m: pix.META[m.group(1)] = m.group(2).strip(); continue
        for m in re.finditer(r'\[(\d+):(\d+(?:\.\d+)?)\]', raw):
            LINES.append((int(m.group(1)) * 60 + float(m.group(2)), re.sub(r'\[[^\]]*\]', '', raw).strip()))
    LINES.sort()
    DUR = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', song]))
    NFR = int(DUR * FPS)
    analyse(song)

    # 每句唱词一个镜头；空行后面超过 5 秒没有歌词，就依次用作间奏、空档和片尾。
    # 间奏是一组镜头，从间奏里第一个小节线开始按小节平分。
    bars = pix.AUDIO['bars']
    SCHED.append((0.0, scenes.s_intro))
    k = 0; gaps = list(scenes.GAP_SCENES)
    for i, (t, txt) in enumerate(LINES):
        nxt = LINES[i + 1][0] if i + 1 < len(LINES) else DUR
        if txt:
            fn = scenes.LYRIC_SCENES[k % len(scenes.LYRIC_SCENES)]; k += 1
            if fn is not None: SCHED.append((t, fn))
        elif nxt - t > 5 and gaps:
            g = gaps.pop(0)
            if not isinstance(g, (list, tuple)): g = [g]
            inside = [b for b in bars if t + 1 < b < nxt - 1]
            base = inside[0] if inside else t
            cuts = [t]
            for j in range(1, len(g)):
                if hasattr(g[j], 'at'):                       # 镜头自己写了从间奏开始后第几秒切进来
                    cuts.append(t + g[j].at); continue
                ideal = base + (nxt - base) * j / len(g)
                cuts.append(min(inside, key=lambda b: abs(b - ideal)) if inside else ideal)
            SCHED.extend(zip(cuts, g))
    SCHED.append((DUR, None))
    scenes.SNAP = snapshot; props.SNAP = snapshot; motifs.SNAP = snapshot


# ---------------------------------------------------------------- 合成
DISSOLVE = pix.BAYER        # 逐像素的 Bayer 点阵溶解
YY, XX = np.mgrid[0:H, 0:W]


def scene_at(T):
    for i in range(len(SCHED) - 1):
        if SCHED[i][0] <= T < SCHED[i + 1][0]:
            return i
    return len(SCHED) - 2


def draw_scene(i, T):
    t0, fn = SCHED[i]
    img = Image.new('RGB', (W, H)); d = ImageDraw.Draw(img); d.fontmode = '1'
    fn(img, d, T - t0, SCHED[i + 1][0] - t0, T, pix.amp(T))
    return img


def snapshot(T):
    return draw_scene(scene_at(T), T)


def tr_mask(kind, f, fn):
    """转场遮罩：True 的地方显示新镜头"""
    if kind == 'iris':
        cx, cy = getattr(fn, 'tr_at', (W / 2, H / 2))
        r = eout(f) * 300
        return (XX - cx) ** 2 + (YY - cy) ** 2 < r * r
    if kind == 'blocks':     # 一格格的方块按随机顺序翻过来
        g = (np.floor(YY / 30) * 17 + np.floor(XX / 30) * 7) % 23 / 23
        return g < f
    if kind == 'wipe':
        g = ((XX // 6) * 6 + (YY // 6) * 3) / (W + H / 2)
        return g + DISSOLVE * 0.15 < f * 1.15
    if kind == 'slide':      # 斜着从左往右扫过去
        x = lerp(-60, W + 60, ease(f))
        return XX + (YY - H / 2) * 0.25 < x
    return DISSOLVE < f


def split_line(txt):
    """拆出括号里的和声：返回 (主唱, 和声)。整句都在括号里时只有和声"""
    back = '  '.join(m.strip() for m in re.findall(r'[（(]([^）)]*)[）)]', txt))
    main = re.sub(r'\s+', ' ', re.sub(r'[（(][^）)]*[）)]', ' ', txt)).strip()
    return main, back


def sing_time(txt, dur):
    n = len([c for c in txt if c.strip()])
    return max(0.6, min(dur - 0.35, 0.42 * n + 0.6))


def show_time(txt, dur):
    """字幕挂多久：唱完后再停两秒，但不超过下一句开始"""
    return min(dur, sing_time(txt, dur) + 2.2)


def sub_line(img, d, txt, lt, dur, T, y, base, hi, leaf=True):
    """一行字幕：逐字浮上来，再按估计的演唱进度从左到右由 base 变成 hi；下面一道风，一片小红叶跟着进度往右飘。
    这一行结束前 0.3 秒用点阵淡出"""
    chars = list(txt)
    ws = [FONT.getlength(c) for c in chars]
    total = sum(ws)
    x0 = W / 2 - total / 2
    out = clamp((lt - (dur - 0.3)) / 0.3)
    if out >= 1: return
    span_ = clamp(lt / 0.35)
    if span_ > 0:
        x_a, x_b = int(x0 - 26), int(x0 + total + 26)
        xs = np.arange(x_a, x_b)
        edge = np.clip(np.minimum(xs - x_a, x_b - 1 - xs) / 16, 0, 1)
        ys = np.arange(y - 13, y + 16)
        vy = np.clip(1 - np.abs(ys - y - 1) / 14, 0, 1) ** 0.6
        a = 0.5 * span_ * (1 - out) * vy[:, None] * edge[None, :]
        pix.blend_box(img, (max(0, x_a), y - 13, min(W, x_b), y + 16), (10, 10, 26), a[:, max(0, -x_a):a.shape[1] - max(0, x_b - W)])
    n = len([c for c in chars if c.strip()])
    sing = sing_time(txt, dur + 2.2)
    prog = clamp((lt - 0.1) / sing)
    if leaf:
        # 一道风：虚线从左往右铺开；小红叶跟着进度往右飘，身后拖两小段风
        ry = y + 12
        lx0, lx1 = x0 - 8, x0 - 8 + (total + 16) * eout(clamp(lt / 0.4))
        if lx1 > lx0 + 2:
            for sx in range(int(lx0), int(lx1), 3):
                if (sx // 3 + int(T * 12)) % 4: d.point((sx, ry), fill=lerpc((90, 110, 160), (200, 220, 240), 0.5 * (1 - out)))
            tx = lerp(x0 - 8, x0 + total - 2, eout(prog))
            bob = round(1.5 * math.sin(T * 7))
            motifs.mini_leaf(img, tx, ry - 3 + bob, T, 1 - out)
            if prog < 1:
                for j in range(2):
                    k = (T * 1.6 + j / 2) % 1
                    wx = tx - 6 - k * 14
                    pix.tfill(img, 'line', [(wx, ry - 4 + j * 3), (wx + 5, ry - 4 + j * 3)], (230, 240, 255), (1 - k) * (1 - out) * 0.9)
    # 先贴所有字的描边和投影，再贴字本身，免得后一个字的描边压住前一个字（比如 O 被压成 C）
    x = x0; k_ch = 0; layers = []
    for i, ch in enumerate(chars):
        k = lt - i * 0.04
        if k < 0: break
        if ch.strip():
            dy = round(4 * (1 - eout(k / 0.25))) if k < 0.25 else 0
            fill = clamp(prog * n - k_ch)
            col = lerpc(base, hi, fill)
            ims = [pix.text_img(ch, pix.TXT_OUT), pix.text_img(ch, col, None, None, False)]
            if k < 0.25 or out > 0:
                m = pix.bayer(ims[0].height, ims[0].width, int(x), y) > clamp(k / 0.25) * (1 - out)
                for j, im in enumerate(ims):
                    a = np.array(im); a[m[:a.shape[0], :a.shape[1]], 3] = 0; ims[j] = Image.fromarray(a)
            layers.append((ims, (int(round(x)) - 3, y - 10 + dy)))
            k_ch += 1
        x += ws[i]
    for j in range(2):
        for ims, pos in layers: img.paste(ims[j], pos, ims[j])


MAIN = ((255, 250, 240), (255, 132, 140))      # 主唱：米白 → 叶子红
ECHO = ((180, 210, 240), (236, 248, 255))      # 和声：冰蓝 → 亮白


def subtitle(img, d, txt, lt, dur, T, y=248):
    main, back = split_line(txt)
    dur = show_time(txt, dur)
    if main:
        sub_line(img, d, main, lt, dur, T, y, *MAIN)
        if back: sub_line(img, d, back, lt - 0.15, dur - 0.15, T, y - 22, *ECHO, leaf=False)
    elif back:
        sub_line(img, d, back, lt, dur, T, y, *ECHO)


def lyric_at(T):
    cur = None
    for i, (t, txt) in enumerate(LINES):
        if t <= T: cur = i
    if cur is None or not LINES[cur][1]: return None
    nxt = LINES[cur + 1][0] if cur + 1 < len(LINES) else DUR
    return LINES[cur][1], T - LINES[cur][0], nxt - LINES[cur][0]


def frame(fi):
    T = fi / FPS
    i = scene_at(T)
    t0, fn = SCHED[i]
    img = draw_scene(i, T)
    lt = T - t0
    kind = getattr(fn, 'tr', 'dissolve'); td = getattr(fn, 'tr_dur', 0.4)
    if i > 0 and lt < td and kind != 'cut':
        f = lt / td
        if kind == 'flash':
            pix.blend_box(img, (0, 0, W, H), (255, 252, 240), np.full((H, W), (1 - f) ** 2))
        elif kind in ('white', 'black'):
            pix.dither_fade(img, 1 - ease(f), (255, 250, 240) if kind == 'white' else (0, 0, 0))
        else:
            prev = draw_scene(i - 1, T)
            m = tr_mask(kind, f, fn)
            img = Image.fromarray(np.where(m[..., None], np.asarray(img), np.asarray(prev)))
    d = ImageDraw.Draw(img); d.fontmode = '1'
    ly = lyric_at(T)
    if ly and not getattr(fn, 'no_sub', False): subtitle(img, d, *ly, T, getattr(fn, 'sub_y', 248))
    return np.asarray(img)


def render_chunk(job):
    lo, hi, path = job
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-vf', f'scale={W * SC}:{H * SC}:flags=neighbor,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium',
                          '-tune', 'animation', '-crf', '20', '-threads', '2', path], stdin=subprocess.PIPE)
    for fi in range(lo, hi):
        p.stdin.write(np.ascontiguousarray(frame(fi)).tobytes())
    p.stdin.close()
    if p.wait(): raise RuntimeError(f'ffmpeg failed on frames {lo}-{hi}')
    return path


def main():
    ap = argparse.ArgumentParser(description='爱错 · 像素 MV')
    ap.add_argument('song', help='歌曲音频，例如 爱错.mp3')
    ap.add_argument('--lyrics', required=True, help='对应的 .lrc 歌词')
    ap.add_argument('-o', '--out', default=os.path.join(BUILD, '爱错_像素MV.mp4'))
    ap.add_argument('--jobs', type=int, default=min(4, os.cpu_count() or 1), help='并行渲染的进程数')
    ap.add_argument('--stills', help='只抽帧检查：逗号分隔的秒数，输出到 build/stills/')
    ap.add_argument('--range', help='只渲染一段，例如 0,20（秒），输出无声的预览')
    args = ap.parse_args()
    load(args.song, args.lyrics)

    if args.stills:
        out = os.path.join(BUILD, 'stills'); os.makedirs(out, exist_ok=True)
        for t in map(float, args.stills.split(',')):
            path = os.path.join(out, f'{t:07.2f}.png')
            Image.fromarray(frame(int(round(t * FPS)))).resize((W * 2, H * 2), Image.NEAREST).save(path)
            print(path)
        return

    lo_t, hi_t = (map(float, args.range.split(','))) if args.range else (0, DUR)
    f0, f1 = int(lo_t * FPS), min(NFR, int(hi_t * FPS))
    # fork 出来的进程直接继承分析好的音频；每个进程编码一段连续的帧，最后不重新编码直接拼接
    parts = os.path.join(BUILD, 'parts'); os.makedirs(parts, exist_ok=True)
    step = -(-(f1 - f0) // args.jobs)
    jobs = [(lo, min(lo + step, f1), os.path.join(parts, f'part{n}.mp4')) for n, lo in enumerate(range(f0, f1, step))]
    with multiprocessing.get_context('fork').Pool(len(jobs)) as pool:
        paths = pool.map(render_chunk, jobs)
    listing = os.path.join(parts, 'list.txt')
    with open(listing, 'w') as f:
        f.writelines(f"file '{p}'\n" for p in paths)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    if args.range:
        out = os.path.join(BUILD, f'preview_{int(lo_t)}_{int(hi_t)}.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', listing, '-ss', str(lo_t), '-t', str(hi_t - lo_t),
                        '-i', args.song, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', out], check=True)
    else:
        out = args.out
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', listing, '-i', args.song,
                        '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                        '-movflags', '+faststart', out], check=True)
    shutil.rmtree(parts)
    print(out)


if __name__ == '__main__':
    main()
