# KeyHop hero：灵感追车记

当前网页交付使用共享 **v4** 清洁视频与响应式字幕，15秒、1280×720、24fps。三幕全部使用本地 MiniMax H3 生成狐狸动作：追着变化的 App 扑空两次、固定键位上一跃到位、回到桌前继续写。首帧由内置 imagegen 制作；真实 App 图标及键位道具由合成脚本添加。音乐是 Kevin MacLeod 的 Monkeys Spinning Monkeys，CC BY4.0，署名与编辑说明保留在与CHMate一致的页尾位置、影片元数据和公开music-credits.txt。

按用户最终要求：手机端字幕15px，四条本地化字幕以重叠CSS-grid保留最长字幕所需高度，避免切换字幕时跳动。窄屏允许换行，使用画面底部20px留白并按需延伸；app图标与键位不被覆盖。桌面保持44/1280画面宽的文字比例。播放与声音按钮在视频内右下角，字幕为它们预留宽度。Native VTT提供无JS字幕，JS通过cuechange/timeupdate/seeked同步HTML字幕并隐藏原生字幕，避免重复。

「看看这个小故事」已移除。可交互键盘示意动画位于「把常用 App 放在手边」卡片内。默认静音循环、离屏暂停、保留手动暂停、尊重减少动态效果设置。

## 当前文件与证据

- 页面：src/components/KeyHopPage.astro
- 12语言字幕／无障碍文案：src/i18n/keyhop-film-copy.json
- 共享视频与封面：public/v/keyhop/hero-v4.mp4、hero-v4.jpg
- 原生字幕：public/v/keyhop/captions-*-v4.vtt
- 本地生成／合成：scripts/generate-keyhop-story.py、scripts/compose-keyhop-story.py
- 首帧、本地H3原片、实际命令、种子、日志：scripts/assets/keyhop/story-v1/
- 媒体规格、完整解码与SHA-256：validation-v4.json
- 12构建路由检查：routes-v4.json；字幕轨检查：tracks-v4.json
- 240个字幕边界检查：caption-geometry-v4.json（320/390/640/641视口，320px另测双倍文字）
- 分幕切换、暂停寻址及循环起点：caption-timing-v4.json
- 英文手机截图：responsive-caption-mobile-en.png
- 完整构建与SEO：build-responsive-captions-final.log
- 创意／提示词与授权：prompt-set.md、music-license.md

较早v1/v2导出移入私有素材目录，v3保留供既有成片链接使用。v3的烧录字幕、外置控件等旧检查属于制作历史；当前字幕和页面行为以v4证据为准。
