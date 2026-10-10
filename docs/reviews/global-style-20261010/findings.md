# 全站风格一致性检查 · 2026-10-10

- 71 个生成页面均有一层纸纹及一个共用页脚；70 个带导航页面共用同一 `SiteHeader`，66 个语言选择器复用 `LanguagePicker`。
- 11 个页面模板接入 `SiteGrain`。保留原有静态/动态纸纹选择，装饰层统一为 aria-hidden，且不拦截交互。
- 页面的实际底色统一为 `var(--paper)`。纸纹与滚动后的 header 共用 `site.css` 中的背景资源、尺寸、强度和滤镜，不再受 FondFont 等页面正文字号覆盖影响。
- 减少动态效果时，由共用样式关闭所有纸纹动画，删除 CHMate 与 World Book 重复的纸纹规则。
- 浏览器抽查 12 类页面：主站首页、7 个 App 产品页、中英文隐私页、Press Kit 汇总与详情；26 个桌面/手机/滚动状态全部通过。抽查包含中文、繁体中文、德语及阿拉伯语。
- 1280px 视口纸纹尺寸 111.111px，390px 视口 125px，各页面一致；透明度均为 0.09，滤镜一致。所有抽查页面均无横向溢出。语言选择器的 chevron 距右侧 8px，选择器点击高度 48px。
- 顶部 header 透明；滚动后使用不透明纸色及同款纸纹，无底线及 backdrop blur。手机 Shheep 游戏层级 1000，header 1100。
- FondFont 太阳及场景、Shheep 游戏、产品配色、原版图标、语言规则与下载素材保留。
- `npm run build` 通过，包括 SEO、Shheep 产物及 Press Kit 检查（7 个产品、60 个产品入口、57 个 App 语言文件夹）。

具体结果见 `generated-pages.json` 与 `browser-checks.json`，截图覆盖桌面及手机。
