# 我眼中的世界 · The World Through My Eyes

成片：[`build/clawd_world.mp4`](build/clawd_world.mp4)，规格为 1920×1080、30fps、H.264 + AAC，时长 48 秒。

主角是 Clawd（Claude Code 的吉祥物）。造型比例参考了 [JohnHeibel/PDoomVideo](https://github.com/JohnHeibel/PDoomVideo) 的 `src/clawd.js`：10×6 的方块身体、四条短腿、两只竖条眼睛。我把它移植成了扁平卡通画法。

| 文件 | 作用 |
| --- | --- |
| `index.html` | 动画本体，画面完全由时间 `t` 决定。浏览器打开后点击 ▶ 即可带音乐播放 |
| `music.py` | 原创器乐配乐，D 大调、120 BPM，纯合成生成，不使用任何采样或音频文件 |
| `render.mjs` | 逐帧渲染并用 ffmpeg 合成 MP4 |
| `assets/` | 中文字体子集（ZCOOL KuaiLe、Noto Sans SC，均为 SIL OFL 许可） |

```bash
cd world
python3 music.py   # -> build/music.wav
node render.mjs    # -> build/clawd_world.mp4
```

## 八个章节（每章 6 秒）

| 时间 | 章节 | 内容 | 转场 |
| --- | --- | --- | --- |
| 0–6s | 醒来 | 终端里敲下 `show me the world`，闪烁的光标一分为二，变成 Clawd 的眼睛 | 镜头钻进它的眼睛 |
| 6–12s | 文字之城 | 文字雨落下，用字符堆成的城市拔地而起；Clawd 走在一句多语言“hello world”铺成的路上，接住一个发光的“光”字 | 文字升空化作星星，圆形转场打开 |
| 12–18s | 问题 | 地球自转，世界各地亮起的问题（中、英、西、日）飘向 Clawd 举着的灯笼 | Clawd 纵身跳进大海，水花转场 |
| 18–24s | 知识之海 | 代码符号组成的鱼群、写着公式的水母、像蝠鲼一样扇动的书本、柱状图珊瑚，还有一头由神经网络连线构成的鲸 | 鲸鱼跃出海面 |
| 24–30s | 连接 | Clawd 骑着鲸鱼穿越星空，星星按拍连成星座：音乐、想法、爱、猫、生命、梦想 | 彗星撞击，白光转场 |
| 30–36s | 蝴蝶 | 一只只 bug 从笔记本里爬出来，被魔法棒一点就变成蝴蝶；花朵随字开放 | 蝴蝶群扫过画面 |
| 36–42s | 桥 | 蝴蝶衔来写着 `if`、`for`、`=>` 的代码积木，搭成一座桥，让说“你好！”和“Hello!”的两个人相遇 | 镜头从 Clawd 的眼睛里拉出来，原来我们一直在透过它的眼睛看世界 |
| 42–48s | 尾声 | 日出的山坡上聚齐了前面出现过的角色，Clawd 说出最后一句话，并挥手告别 | 只剩两只眼睛，化作终端光标，和开头首尾呼应 |
