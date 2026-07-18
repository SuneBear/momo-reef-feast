# 《沫沫的珊瑚午餐》宣传片分镜

**Format:** 1920×1080, 30fps, 26–28 seconds  
**Audio:** 中文 TTS 旁白 + 游戏内 Frenzied Swimming 配乐 + 吃鱼/泡泡/受伤 SFX  
**VO direction:** 年轻自然的中文女声，明亮但不幼稚；语速中等，短句有呼吸，高潮句“反击时刻到了”略微加重  
**Style basis:** `DESIGN.md`  
**Rhythm:** HOOK → build → quick danger hits → PEAK → breathe → CTA hold

## Global Guardrails

- 深海蓝始终占据主要画面，橙白沫沫和金色成长反馈承担焦点。
- 每个 beat 至少包含背景水纹/颗粒、中景角色或 UI、前景气泡/文字三层。
- 像素图片保持 `image-rendering: pixelated`，严禁模糊插值和非等比拉伸。
- 字幕使用泡沫青或奶油白，置于底部低干扰的半透明深蓝胶囊内。
- 片中不模拟网页滚动；用真实游戏资产重新组织成电影化的横版水下场面。

## Asset Audit

| Asset | Type | Assign to Beat | Role |
| --- | --- | --- | --- |
| `momo_swim.png` | 6-frame sprite | 1–6 | 主角，首尾品牌锚点 |
| `lanternfish_swim.png` | 6-frame sprite | 2 | 小型猎物 |
| `butterflyfish_swim.png` | 6-frame sprite | 2, 5 | 彩色猎物与海域丰富度 |
| `sardine_swim.png` | 6-frame sprite | 2 | 快速群游猎物 |
| `shrimp_swim.png` | 6-frame sprite | 2 | 暖色猎物 |
| `puffer_pulse.png` | 6-frame sprite | 3, 4 | 危险与反击对象 |
| `jellyfish_pulse.png` | 6-frame sprite | 3, 4 | 危险与泡泡视觉 |
| `shark_boss.png` | 6-frame sprite | 3, 4 | 高潮 Boss |
| `depth_far_bed.png` | parallax layer | 1–6 | 低对比远景海床 |
| `depth_far_ridge.png` | parallax layer | 1–6 | 远景轮廓 |
| `depth_mid_bed.png` | parallax layer | 1–6 | 中景海床 |
| `depth_rock_arch.png` | transparent prop | 1, 2, 5 | 中景石拱 |
| `depth_rock_cliff.png` | transparent prop | 1–6 | 前景岩壁 |
| `depth_rock_shelf.png` | transparent prop | 2, 5 | 前景岩架 |
| `depth_rock_spires.png` | transparent prop | 3, 5 | 月光海沟尖塔 |
| `bg_coral.png`, `bg_seaweed.png`, `bg_shipwreck.png` | transparent props | 2, 5 | 海域差异 |
| `icon_star.png`, `icon_heart.png`, `icon_boost.png`, `icon_pearl.png` | UI icons | 2, 4, 5, 6 | 得分、生命、冲刺、观赏模式 |
| `dialog_panel.png`, `toast_panel.png` | UI frames | 6 / captions | 标题框与字幕承托 |
| `water-light.mp4` | video texture | 1–6 | 水面焦散，低强度 screen 混合 |
| `frenzied-swimming.ogg` | music | global | 轻快水下节奏 |
| `eat-cute-small.wav`, `eat-cute-heavy.wav`, `bubble-pop.ogg`, `player-hit.mp3` | SFX | 2–4 | 动作反馈 |

## BEAT 1 — 小鱼，大胃口（0.00–3.20s）

**VO:** “在深海里，小鱼也能有大胃口。”

**Concept:** 镜头已经在深海中缓慢前行。沫沫的探照灯先划开黑蓝海水，然后主角从左下方游进光里；“小鱼”与“大胃口”形成大小反差，第一秒就建立角色和好奇心。

**Visual:** BG 是三层蓝色海床与漂浮颗粒，焦散视频只在上半部呼吸；MG 的石拱后方有微弱鱼影；主角六帧游动从左下沿弧线进入；一束柔和锥形灯光跟随头灯；FG 气泡擦过镜头。关键词“小鱼”较小，“大胃口”以珊瑚橙放大出现。

**Techniques:** Canvas 2D 程序化气泡；SVG 路径绘制头灯光锥轮廓；逐词动效；角色沿曲线路径推进。

**Camera:** 轻微向右上漂移并推近 1→1.05；结尾加速进入下一 beat。

**Transition:** velocity-matched 向右 whip pan，角色运动方向连续。

**SFX:** 开场低频水下气泡；沫沫入光时一个柔和 shimmer。

## BEAT 2 — 追、吃、长大（3.20–8.24s）

**VO:** “跟着沫沫的探照灯，追上小鱼，冲过珊瑚，越吃越大。”

**Concept:** 横版追逐突然提速。四种猎物分层穿过珊瑚与岩架，沫沫连续加速、吞食、变大，画面像一段浓缩的真实游戏回合。

**Visual:** BG 远景平移最慢；MG 珊瑚、海草、石拱快速向左；四种猎物以不同速度穿行；沫沫从 0.75 倍逐次长到 1.18 倍，尾后出现 boost 气泡；顶部缩略成长 HUD 从 0% 填充到 62%；吃鱼时星星与分数碎片向外弹出。

**Techniques:** sprite 帧动画；Canvas 粒子尾迹；成长条 SVG/DOM 填充；数字 counter；快速硬切的三次吞食节拍。

**Camera:** 侧向 tracking，三次微弱 punch-in 对应吞食。

**Transition:** 最后一次吞食产生橙色圆形冲击波，扩张成下一幕的危险警示。

**SFX:** 三次轻吃鱼声，最后一次用重吃鱼声；冲刺水流声短促抬升。

## BEAT 3 — 危险来袭（8.24–12.85s）

**VO:** “刺豚、水母，还有每片海域的鲨鱼王，都在等你。”

**Concept:** 节奏变成三个快速危险镜头。刺豚鼓起、水母压下、鲨鱼王从深蓝阴影中占据半幅画面，危险逐级升级但仍保持可爱可读。

**Visual:** 三个 1 秒左右的空间切换：紫色刺豚在警告三角前 pulse；粉色水母伴随泡泡群从顶部垂落；蓝灰鲨鱼王穿过尖塔，牙齿被一束斜光点亮。沫沫每次都在画面另一端急转躲避；泡泡心从三颗闪到两颗但不真正破裂。

**Techniques:** CSS 3D 卡片式空间切换；角色帧动画；警告 SVG 描边；Canvas 泡泡；percussive kinetic labels“刺豚 / 水母 / 鲨鱼王”。

**Camera:** 两次 hard cut，鲨鱼镜头用 zoom-through 进入。

**Transition:** 鲨鱼冲向镜头，深蓝轮廓遮满画面；切入成长金光。

**SFX:** 泡泡 pop、短促受伤提示、鲨鱼出现的低音 impact。

## BEAT 4 — 百分之百反击（12.85–15.79s）

**VO:** “长到百分之百——反击时刻到了。”

**Concept:** 全片能量峰值。成长条从 62% 冲到 100%，沫沫被金色能量包裹，随后反向冲向鲨鱼；“100%”成为画面中的巨大图形而不是普通 HUD 数字。

**Visual:** BG 暂时压暗；MG 金色成长条横贯画面，62→100 快速计数；沫沫 scale 1.18→1.42 并出现金色描边；icon_boost 和星星环绕；鲨鱼在右侧迎面而来；撞击点爆出珊瑚橙/泡沫青像素碎片。“反击”二字在撞击后 STAMP 进来。

**Techniques:** counter animation；Canvas 能量粒子；逐字 STAMP typography；SVG 放射线；audio-reactive 轻微脉冲。

**Camera:** 先锁定成长条，随后快速向右追随沫沫；撞击瞬间 3 帧轻震。

**Transition:** 爆炸粒子变成三枚圆形海域窗口。

**SFX:** 升级三音上行、重吞食声、短 impact 后半拍静音。

## BEAT 5 — 三片海域，两种玩法（15.79–20.51s）

**VO:** “三片海域，手动冒险，或者交给沫沫自己巡游。”

**Concept:** 高潮后给观众一次清晰浏览。三个海域像并列的水下舷窗展开，同时展示手动冲刺和珍珠观赏模式，传达内容量与轻松体验。

**Visual:** 左、中、右三枚贝壳边框窗口依次 CASCADE：珊瑚暖湾用暖蓝珊瑚，幽蓝沉船道出现沉船和水母，月光海沟使用靛蓝尖塔与鲨鱼影。前景是一只小型沫沫在三窗之间游过；底部左侧出现 boost 图标和“手动冒险”，右侧 pearl 图标和“水族馆观赏”；三颗泡泡心在顶部轻轻弹动。

**Techniques:** CSS 3D 舷窗 cascade；parallax inside panels；SVG 连接航线 draw-on；角色 motion path；图标弹性动效。

**Camera:** 稳定的宽景，最后缓慢向中间窗口推近。

**Transition:** 中间窗口扩张为全屏深蓝，贝壳边缘成为片尾框。

**SFX:** 三个柔和 shell clicks；珍珠图标落下时一个清亮 chime。

## BEAT 6 — 品牌与 CTA（20.51–26.00s；旁白结束于 24.26s）

**VO:** “《沫沫的珊瑚午餐》。现在，开饭啦！”

**Concept:** 情绪收束但画面仍有生命。沫沫绕标题游一小圈，探照灯扫过“珊瑚午餐”，CTA 像游戏里的按钮一样落位；最后保留约一秒让观众读完。

**Visual:** BG 是最深的 `#021239` 加低速焦散与远景海床；MG 使用贝壳对话框轮廓承托中文标题，第二行珊瑚橙；沫沫从标题后方游到右下；星星和小气泡形成克制的环；CTA“开饭啦！”使用黄橙胶囊按钮；英文 kicker 只作为小型辅助。

**Techniques:** 贝壳框 SVG/CSS draw-on；逐词标题 settle；角色 motion path；Canvas 气泡；CTA pulse 与轻微音频响应。

**Camera:** 从窗口扩张后继续 1.04→1 的安定回拉，最后一秒完全稳定。

**Transition OUT:** 末帧保持 0.8–1 秒，再淡到深海蓝。

**SFX:** 标题落位的温暖 chime；CTA 一个软弹 click；音乐收在完整和弦。

## Caption Direction

- 使用 `transcript.json` 的真实词级时间；每次显示一小句或 6–12 个汉字。
- 高亮当前短语为奶油白，其余为泡沫青；胶囊底色 `rgba(2,18,57,.76)`。
- 避开 HUD、成长条和 CTA，默认位于底部 84px 安全区上方。

## Production Architecture

```text
momo-reef-feast-trailer/
├── index.html
├── DESIGN.md
├── SCRIPT.md
├── STORYBOARD.md
├── narration.wav
├── transcript.json
├── capture/
├── assets/
│   ├── images/
│   ├── audio/
│   └── media/
├── compositions/
│   ├── beat-1-hook.html
│   ├── beat-2-grow.html
│   ├── beat-3-danger.html
│   ├── beat-4-power.html
│   ├── beat-5-zones.html
│   ├── beat-6-cta.html
│   └── captions.html
├── snapshots/
└── renders/
```
