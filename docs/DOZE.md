# Doze 产品页与素材

产品路径 `/doze/` 为简体中文，其他语言共用 `src/pages/doze/[locale].astro`。英语为 hreflang 的 `x-default`。名称、语言标签、路径及方向统一在 `src/i18n/doze-locales.mjs`；完整产品文案位于 `doze-copy.json`，同时用于 Press Kit。

## 发布状态

产品页及 Press Kit 的主 CTA 始终指向公开 Releases 页面。已核实的 `downloadUrl` 用于应用结构化数据。

`src/i18n/doze-release.json` 是产品页、首页及 Press Kit 的共同状态来源。当前已核实首发版本 `261019.0`（2026-10-20 按用户要求覆盖定稿）（macOS 13.0+）和实际 DMG 附件，产品页、首页及 Press Kit 显示正式下载。首发准备期间只显示准备中与发布页入口，不在应用结构化数据中声明下载地址。

公开发行仓库为 `cxa/doze`，源码仓库为私有 `cxa/doze-src`。公开仓库不是开源代码入口。只有核实已发布 Release 的实际 DMG 附件、版本与最低系统要求后，才能将状态改成 `published` 并填写 `version`、`downloadUrl` 及核对日期；随后重新生成资料包并构建。

## 原版素材

- App 图标：`scripts/assets/native-icons/doze/AppIcon.icon`；由 Icon Composer 导出 Default 1024px PNG。源文件与导出哈希见 `scripts/assets/native-icons/sources.json`。
- 透明符号：原版 Icon Composer 工程内的光学图案，保存为 `src/assets/img/doze-symbol.png`，保留完整透明画布。
- 截图：`scripts/assets/presskit/doze-panel-<locale>-<theme>.png`。12 种真实界面语言各含日、夜两张，均为原生 Retina 截图，未缩放或修饰。来源记录见 `scripts/assets/presskit/screenshot-sources.json`。
- 截图在隔离副本中使用 App 当前的 `ControlPanelView`、`SkyView`、`Localization`、`IdleDelay`、Resources 和原版插画导出。捕捉工具为 `scripts/assets/doze/capture-panels.swift`，预览沿用原生 popover 的水平安全区；`capture-source.json` 保存核对时源码提交及工作区精确文件哈希。使用独立临时 App，不构建或写入主 App 项目，不更改其运行状态。原生视图中的 Core Animation 图层需要窗口截图，不能以 `cacheDisplay` 代替。
- 菜单栏图标：使用 `scripts/assets/doze/export-menubar.swift` 配合源项目 `Sources/StatusIcon.swift` 导出原生 2× 模板图，按原比例显示，图标高度为 20pt，来源和导出哈希见 `menubar-source.json`。菜单栏的 Apple、Wi-Fi、电池图标从 macOS SF Symbols 原生导出。网页补充菜单栏、选中背景与 popover 箭头；原生面板截图保持原样。
- 网站构建只读取已保存的素材和快照，不依赖 Xcode 或私有项目。

## 更新

产品源位于 `/Users/realazy/Projects/_vibe/doze/src`。名称与支持语言以 `docs/COPY.md`、`Resources/*/InfoPlist.strings`、`Localizable.strings` 为准。产品行为以 README 和当前代码为准；不要将调暗描述成保证关屏，不承诺所有外接显示器或所有自动化工具都兼容。

源项目更新界面、图标或本地化后，重新核对并替换原版素材，同步来源记录、语言快照与网站文案。截取时记录准确的源码版本与未提交改动哈希，不能将核对日期当作拍摄日期或已发布版本。

产品文案简洁说明：离开后调暗屏幕，配合可选的“保持电脑唤醒”，避免自动关屏和屏保打断 computer use。不另加锁屏说明，不用破折号解释术语。首页、12 种产品页语言、SEO 描述及媒体资料保持相同表述。

```sh
python3 scripts/export-native-app-icons.py
# Python 环境需要 Pillow、fonttools、brotli，文字由 macOS AppKit 确定性渲染。
python3 scripts/render-doze-opengraph.py --review-dir /tmp/doze-og-review
python3 scripts/prepare-presskits.py
npm run build
```

分享图使用原版透明符号与对应语言的实际应用名。Latin 使用主站 Sofia Sans Extra Condensed 900，其他文字通过 AppKit 排版。所有核心内容保持在 1200 × 630 图像中央的 630 × 630 安全区内；需同时查看横图与方形裁切。

## Hero 展示

Hero 沿用绎言等产品页的通栏标题、宽幅主视觉与下方介绍结构，继续使用主站字体和组件。演示区的日夜切换位于菜单栏；窗体保持原生截图比例并使用独立投影。背景日月、山丘是 App 原版插画，仅用于网站布景，不是 App 壁纸功能，且不合成到下载的原生截图中。原版插画快照见 `scripts/assets/doze/scene-source.json`。菜单栏图标按导出 PNG 元数据自动保留 2× 尺寸比例，当前原生画布为 22 × 20pt。

导航小图标使用 App 项目中的 `Assets/WebIconCompact.icon`。这个小尺寸版本保留蓝底、金色「眯」和闭眼，使用清晰的 SVG 笔画、较浅的立体高光，并为眼形留出间隙，避免完整光学材质的细密反光在缩小后混在一起。原版快照位于 `scripts/assets/native-icons/doze/WebIconCompact.icon`，来源和文件哈希记录在 `compactSource`。使用 `python3 scripts/export-doze-small-icons.py` 从 Icon Composer 直接按 16、22、28、32、48、80pt 及 1×/2× 渲染。导航在桌面选择 28/56px、窄屏选择 22/44px 的原生无损 PNG，避免 1024px 母图缩放后再经有损 WebP 压缩。favicon 同样选择原生 16/32px 图。完整 PNG 下载及媒体资料保持 1024px，所有小尺寸导出记录在 native-icons/sources.json 的 webRenditions，并纳入构建的哈希与尺寸校验。

Day／Night 位于模拟菜单栏最右侧，使用 28px 高的分段控件，在 36px 菜单栏中上下各留 4px。选中项使用实色背景，切换时同步原生日夜截图。菜单栏图标使用当前源代码的 active、keepAwake=false 状态，与演示面板中关闭的保持唤醒开关对应。

2026-10-20：首发定稿更新全部 24 张日夜原生截图。保持唤醒的两条圆点说明、40pt 液态玻璃主按钮、无背景退出按钮和 96pt 底部留白与当前 App 一致；图中语言与来源哈希同步更新。旧的 261019.1 预览发行将撤下，产品页和资料包统一使用 261019.0。

首页 Doze 卡片与其他带界面的产品共用通栏网格，使用完整日间原生截图和 WebIconCompact 的 80/160px 无损版本。所有首页卡片的标题区统一为左侧图标、右侧名称与平台标签，图标按名称的大写字高、标签行高及间距计算尺寸，使两侧视觉等高。截图展示区复用子页面 Hero 的浅色天空、太阳及日间山丘插画作为背景，原生截图保持独立。产品页主视觉下的介绍与下载操作分为两组，桌面并排，窄屏顺序排列。下载区不附加系统及显示器说明、发布状态或版本文字。

功能卡片色相取自原版插图：太阳约 94°、日间山丘约 114°。卡片使用调浅后的日光黄与灰绿；首页及 Press Kit 的 Doze 产品底色共用 `--app-doze:oklch(0.93 0.03 105)`，沿用 App 日间界面的浅暖灰绿，呼应原生面板与山丘。图标保留原版蓝金配色。颜色均在 sRGB 范围内，正文对比度超过 7:1。
