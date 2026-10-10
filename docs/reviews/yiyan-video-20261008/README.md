# 《绎言》落地页视频 v2

25 秒无声短片：照常与 AI 助手工作 → 同一句话的自然英语 → 真实学习笔记 → 自己的表达积累 → 品牌与本地保存。

## 画面与事实来源

- MiniMax H3 在本机生成两个新纸张镜头；50 层、20 步、reuse 1。参考场景由内置 imagegen 制作。
- 英文例子和重点笔记来自站点原有的真实学习记录截图；每个语言版本使用相应的原有截图。
- 动态纸张是学习积累的视觉比喻。文字使用 macOS 系统排版；没有用生成文字冒充应用界面。
- 原请求照常发送，英文结果稍后出现。记录默认保存在本机；没有宣称翻译离线或不产生模型费用。
- 12 个语言版本共用新 H3 镜头，分别排版文字并导出 MP4 和对应海报。旧 v1 文件保留。

## 本地制作

源素材和中间文件保存在 `scripts/assets/yiyan/marketing-v2/`，由 Git 忽略；成片位于 `public/v/yiyan/hero-<locale>-v2.mp4`，海报为同名 `.jpg`。

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swiftc scripts/render-yiyan-text.swift -o scripts/assets/yiyan/marketing-v2/render-text
/opt/homebrew/bin/python3 scripts/generate-yiyan-marketing-v2.py prompt-notebook
/opt/homebrew/bin/python3 scripts/generate-yiyan-marketing-v2.py phrase-collection
/opt/homebrew/bin/python3 scripts/compose-yiyan-marketing-v2.py --text-only
/opt/homebrew/bin/python3 scripts/compose-yiyan-marketing-v2.py
npm run build
```

生成与导出脚本拒绝覆盖已有视频。新一轮制作需使用新的版本目录和文件名。Python 需要 Pillow 和 NumPy；H3 需要用户已安装的本地引擎与模型。

Advisor 创意方向审阅见 `approach-advice.md`，采纳记录见 `decisions.md`。检查结果见 `validation.json`。

## 验证

12 个视频均为 25 秒、1280×720、24 fps、H.264、yuv420p、600 帧、无音轨，并通过完整解码与 faststart 检查。每个视频约 1.8 MB，合计约 22 MB。12 个海报与视频匹配，构建后的页面和媒体文件已逐一核对。`npm run build`、SEO 检查与站点已有检查通过。中文落地页在浏览器中实际播放成功。

最终独立审阅见 `completion-advice.md`：可交付用户审阅，无实质阻碍。中文已检查手机及桌面布局，英文已检查实际播放；预览后已恢复默认视口。提示词见 [prompt-set.md](prompt-set.md)。
