# 模块 Prompt 索引

仓库根目录的 [`PROMPT.md`](../PROMPT.md) 是给最终用户复制的一键复现入口；[`00-one-shot.md`](00-one-shot.md) 保留完全相同的正文，便于与本目录的专项 Prompt 一起维护。它可以从空目录制作整款游戏，也可以接管已有项目持续修复。其余文件把同一目标拆成可独立执行的模块，适合只实现、重做或验收某一部分。

| 模块 | 用途 |
| --- | --- |
| [`00-one-shot.md`](00-one-shot.md) | 一条 Prompt 从零制作或接管整款游戏，内含自动检查与修复循环 |
| [`01-gameplay.md`](01-gameplay.md) | 核心玩法、碰撞、成长、三关与鲨鱼流程 |
| [`02-autoplay.md`](02-autoplay.md) | 水族馆观赏 AI、自动通关与手动接管 |
| [`03-art-and-characters.md`](03-art-and-characters.md) | 美术 DNA、8 组角色和六帧动画 |
| [`04-scene-depth-lighting.md`](04-scene-depth-lighting.md) | 场景物件、三层景深、焦散与头灯 |
| [`05-ui-typography-accessibility.md`](05-ui-typography-accessibility.md) | HUD、响应式 UI、字体与无障碍 |
| [`06-audio-and-feedback.md`](06-audio-and-feedback.md) | BGM、音效、粒子、受伤与成长反馈 |
| [`07-asset-pipeline.md`](07-asset-pipeline.md) | 色键、切片、锚点、验证与 contact sheet |
| [`08-build-and-offline.md`](08-build-and-offline.md) | 独立资源版、单 HTML、离线与静态托管 |
| [`09-qa-and-browser-testing.md`](09-qa-and-browser-testing.md) | 桌面/移动端、全流程与观赏模式回归 |
| [`10-readme-and-documentation.md`](10-readme-and-documentation.md) | README、许可、报告与 Prompt 文档维护 |

使用方式：复制某个文件代码块里的全部内容，作为一条 Prompt 发给 Agent。模块 Prompt 默认针对当前工作区中的《沫沫的珊瑚午餐》项目；它们会先检查现状，只修改本模块及必要的相邻接口，并要求保留其他已完成能力。

推荐顺序：汇总 Prompt → 玩法 → 观赏 AI → 美术角色 → 场景景深 → UI → 音频 → 素材流水线 → 构建 → QA → 文档。也可以单独使用任意一份做专项迭代。
