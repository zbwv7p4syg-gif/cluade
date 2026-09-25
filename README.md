# Opus 5.5 × CapCut：30 秒一镜到底动画

成片：[`build/opus55_capcut.mp4`](build/opus55_capcut.mp4)，规格为 1920×1080、30fps、H.264 + AAC，时长 30 秒，可以直接发布到 X。

| 文件 | 作用 |
| --- | --- |
| `index.html` | 动画本体。Canvas 画面完全由时间 `t` 决定。在浏览器中打开后点击 ▶ 即可带音乐播放 |
| `music.py` | 原创器乐配乐，用 numpy/scipy 纯合成生成。不使用任何采样或本地音频，输出 `build/music.wav` |
| `render.mjs` | 用 Playwright 逐帧渲染，再由 ffmpeg 与配乐合成 MP4 |
| `assets/` | Fredoka 字体（SIL Open Font License） |

## 重新生成

```bash
pip install numpy scipy imageio-ffmpeg
python3 music.py      # -> build/music.wav
node render.mjs       # -> build/opus55_capcut.mp4
```

## 节拍与分镜（120 BPM，每拍 0.5 秒，全片无剪切）

| 时间 | 内容 |
| --- | --- |
| 0–2s | 特写：Opus 5.5 弹出登场并打招呼，随后镜头拉远，露出剪辑界面 |
| 2–4s | 五段素材从媒体库依次飞入时间线，每拍落下一段 |
| 4–8s | 小桥段：一段 3 分钟的“Loading…”素材把 Opus 看困了。“咔嚓”两刀剪掉后，Opus 一脚把它踢飞 |
| 8–12s | 缺口自动合拢，三个转场（旋转、滑动、故障）按拍嵌入 |
| 12–14s | 小桥段：Opus 打了个喷嚏，误触“✨RANDOM✨”特效，全屏彩虹乱闪；紧接着磁带停转，画面冻结成灰色，一副像素墨镜缓缓落下…… |
| 14–20s | Drop 进入，“…keeping it 😎”。按拍逐词添加字幕 “POV: my cat can SKATE”，再用 Beat Sync 把片段吸附到节拍点 |
| 20–24s | Opus 站在播放头上冲浪，一路滑过整条时间线 |
| 24–27s | 导出。进度卡在 99% 时 Opus 一脚踩下去，瞬间 100%，随后发布到 X，点赞数一路飙升 |
| 27–30s | Opus 自豪地展示成片，并以“Opus 5.5”的身份和观众挥手告别 |
