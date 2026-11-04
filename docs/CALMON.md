# Calmon 产品页与媒体素材

- 简体中文页面 `/calmon/`，其余 37 种语言为 `/calmon/<BCP47>/`；复用站点导航、语言选择器、预加载、纸纹、字体、按钮和页脚。
- 功能、系统要求和英语界面以本地 `_vibe/pane` 的 README、`project.yml`、`Sources/CalmonApp.swift` 和 `Sources/AppJump.swift` 为依据。当前要求 macOS 26+。App 使用 String Catalog，语言集合为英语及 37 种翻译；网站和媒体文案覆盖全部 38 种语言，媒体资料中的原生面板截图逐语言对应 App 的真实本地化；页面内的按键面板以原版字体和真实文字排版，随各语言页面本地化。
- `src/i18n/calmon-release.json` 统一配置发布状态和下载入口。按照 Doze 使用稳定 Releases 页面 `https://github.com/cxa/calmon/releases`，不猜测版本号、安装包文件名或价格。当前 `upcoming`，产品页、入门步骤和底部下载指向稳定 Releases 页面；应用结构化数据不提供 `downloadUrl`。公开发布时同时核对下载、FAQ 与安装说明。
- 首屏标题在全部语言中固定为两行，优先让第二行更长；CJK 行末标点悬挂，不参与居中宽度。定位语位于顶部导航的 Calmon 字标下方。演示说明和免费下载入口位于画面下方，Beta 期间免费与系统要求保留在按钮下方。演示外侧桌面留 24px、手机留 12px；裁切区域固定在真实屏幕／固定列边界上，窗口以完整形态滑入滑出，不能按动画终点提前裁切；单侧固定时工作列贴齐固定边界，另一侧继续滚动，不在固定列旁保留邻窗窄条；双侧固定时工作列在剩余区域完整叠放；首尾完整窗口仍保留默认的 12pt 边距。
- `CalmonDesktop.astro` 与 `calmon-desktop/` 构成独立的网页桌面模型，不引用或分发 App 源码。默认 90% 滚动列；覆盖 App 堆叠、三单元纵向列、尺寸步进、固定列、浮动窗口、全屏、跨桌面移动、Pin Deck、Sky Deck 和 Max Deck。堆叠标记采用等长圆角短刻度（8 × 2 px、间隔 4 px），当前页为强调色，其余为中性灰；整组左端对齐红灯中心，切换只变颜色、不改尺寸和位置。焦点边框为连续 2 px 纯强调色，与短刻度留 2 px 间隙，不加黑色描边。原生窗口只保留标准控制，不添加窗口内操作按钮；演示操作来自前导模式、原生 ⌘` 和菜单栏右侧的播放控制。
- 自动演示先显示按键顺序，再执行同一模型的操作，说明都在桌面外。演示不包含鼠标点击、右键菜单、拖动或模拟指针；窗口跳转使用标签，浮动使用 Space F，全屏使用 Space S。堆叠切换后紧接 , / . 演示：先把 Notes 堆叠并入 Safari 列的下方，再向右拆出，恢复两列；保持焦点和成员不变，触发键在两步间持续绿色。开场移除背景 Music 浮动窗口；仅在 Sky Deck 的浮动／恢复平铺片段出现浮动窗口，其他演示保持纯平铺。以横向滚动为主，不演示默认关闭的轻扫；开场双击 ⌘ 后，先连续三次 → 向右切换，再连续三次 ← 沿原路返回起始窗口；正反方向均保持尺寸和前导模式，每个按键按演示顺序以绿色高亮，末键在功能执行与结果停留期间保持高亮。输入提示明确区分“先双击并松开 ⌘ 进入前导模式”和“前导模式已开启”；状态与窗口边框、标签共用状态，并明确提示窗口有高亮框时可连续操作，无需重复触发；中英文使用说明与开场演示均说明这一点。模式开启后，两枚 ⌘ 触发键持续绿色，跨命令步骤保留，与当前操作键同时显示；它们表示当前模式，不重复播放触发动作。演示不显示 Esc 按钮；命令后需要标签时，以新的进入模式演示开始，标签跳转后触发键熄灭。⌘` 单独标明为 macOS 快捷键。功能文案保留轻扫默认关闭、可在 Settings → Gestures 启用的说明。画面不显示“功能演示／自动播放”标题行或“无需实际操作键盘或触控板”提示；只保留模式状态、按键线索和播放控制，逐步说明仅供辅助技术读取，不在按键下显示，所有桌面输入均禁用，不监听快捷键、手势、拖动或右键。仅提供播放／暂停和从头重播控制；演示结束后通过淡出、复位、淡入自动循环，始终保留从头重播入口。手动重播会从第一步重新播放；循环过渡期间的暂停、离屏和减少动态效果设置仍有效，快速重播不能让旧过渡重启播放。方向键到头轮换复用图标／标签跳转的窗口移动动画，普通轻扫到边只回弹。导航不改变窗口宽度；窗口移动期间绿色焦点边框跟随窗口，直到实际动画结束，再按前导模式状态保留或隐藏；重新演示时先淡出，隐藏重置位移后再淡入。快速输入立即接管过渡。演示屏幕至少 35% 进入视野后播放；页面隐藏／演示离屏时暂停；减少动态效果时默认不自动播放。Hero 桌面固定为 1280 × 800，以容器宽度计算 transform scale 整体缩小，保持菜单栏、窗口、标签栏和地图的桌面排布；不做手机竖屏或标签栏换行布局。外层按 16:10 预留空间，按键提示保留页面字号；菜单栏右侧的 Calmon 图标、Wi-Fi、电池、时间与两个 pill 播放控件共用同一行，按桌面尺寸同比缩放，状态项目和播放控制之间使用固定比例的间距。窄屏正文至少 16px。
- 图标菜单的项目、顺序、分隔线和简体中文文案来自当前 App。默认栏顺序为 Pin Deck → Sky Deck → Max Deck → 桌面组 → 地图；空的 Sky／Max Deck 不占位置。地图显示屏幕、支架与屏幕外列。点击地图时，原生按键面板在标签栏上方 8pt、靠近点击位置，并限制在屏幕内；键盘入口默认居中。
- 中英文按键面板以原生五个分组、行标题和键帽组成真实 HTML，内嵌 App 原版 Z Labs RoundPix 12px 字体的改名 WOFF2 子集，不使用面板截图、canvas 或缩放图片。常规宽度双列、窄屏单列，保持可读字号。Hero 保留低对比度的 Golden Gate 桌面壁纸及精简 macOS 菜单栏，窗口只显示系统原版 App 图标和名称，省去时钟及模拟内容。网页排版不混入媒体资料的原生截图；原生截图、壁纸和图标的来源仍独立记录。
- 使用说明先介绍鼠标：标签栏图标切换、图标菜单、布局图打开可点击的按键面板。面板帮助记忆快捷键，熟悉后可在 Settings → Keyboard → Key Panel → Show after 选择 Never，只有键盘入口停止自动显示；点击布局图仍立即显示。中英文功能介绍、开始使用与 FAQ 保持一致。
- 模型检查：`node --test scripts/test-calmon-desktop.mjs`，覆盖窗口身份、堆叠／列、固定、浮动、全屏、桌面、Pin Deck、完整自动演示和边界。自动播放、暂停／继续、重播、画面输入隔离与移动布局另行在浏览器核对。首页保留原有紧凑布局示意。

## 原版资源

原版 Icon Composer 工程保存在 `scripts/assets/native-icons/calmon/AppIcon.icon`，导出记录位于共用 `scripts/assets/native-icons/sources.json`。重新导出：

```sh
python3 scripts/export-native-app-icons.py --product calmon
```

OG 与 SVG 使用原生 CGPath 导出的方格字形轮廓、位置和六色绿色光谱，去掉玻璃、光照及底壳。字标显示为 Calmon。产品名在所有网站语言中不变，共用一张 1200 × 630 PNG；遵守 `docs/OPEN_GRAPH.md` 的纸纹、字体和中央安全区。重新生成只需要已提交的素材：

```sh
python3 scripts/prepare-calmon-assets.py
```

该脚本依赖 Pillow、fonttools、brotli 和项目 Node 环境。OG 来源和安全区记录在 `scripts/assets/calmon/opengraph-source.json`，SVG 来源记录在 `scripts/assets/presskit/vector-sources.json`。

原生按键面板从当前 AppKit `LeaderHelpView` 和默认命令导出，使用 App 自带的 Tiny5 和两款面板像素字体。捕获程序只离屏渲染视图，不运行 calmon 的窗口管理器，不启动 AppDelegate，不操作用户的窗口。可选重新捕获需要本地 App 源码和 Xcode：

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer python3 scripts/prepare-calmon-assets.py --app-source /path/to/calmon
```

代码、校验哈希和导出上下文保存在 `scripts/assets/calmon/`，共用截图来源清单记录 PNG 原始像素和英语界面。网站构建不读取私有项目，不依赖 Xcode 或 Python。

更新后生成 Press Kit 并运行完整构建：

```sh
python3 scripts/prepare-presskits.py
npm run build
```

## 本轮同步

图标使用已确认的 H 绢雾材质和绿色光谱；亮色为白字和彩色背景，暗色为纯黑背景与完整六色字形。App 名称统一显示 Calmon；路径、bundle ID 和命令保留小写 calmon。首页卡片、按钮、快捷键、焦点反馈和 OG 使用相同绿色方向。菜单栏使用原生 2× 模板，图形为 16pt，保留 22pt 画布。资料包同时提供亮暗 App 图标、菜单栏模板、平面 SVG、原生按键面板与 OG。旧 `/pane/`、`/pane/en/` 和媒体页跳转到新地址。

Hero 根据标题与控件的实际高度限制演示宽度，保持 16:10 桌面比例，确保外部说明和 CTA 完整留在首屏；标题始终为两行。定位语放在顶部标题栏的 Calmon 下方，左对齐，与 44px 图标等高；手机标题栏分两行，避免挤压语言菜单。

Hero 的下载按钮统一使用「免费下载」及对应 38 种语言译文。演示下方的控件区按演示容器宽度布局：超过 600px 时，演示说明靠演示左缘，下载按钮靠演示右缘，两者顶部对齐；兼容性说明保留在按钮下方，间距 8px；超过 800px 时组间至少留 48px，601–800px 时至少留 24px；不超过 600px 时，CTA 换到下一行，间距扩大为 32px，两组均居中。CTA 保留兼容性说明，不使用独立底带或卡片。桌面标题使用 48–88px，中文使用 40–80px；手机中文标题使用 32–48px。38 种语言的标题均固定为两行，以各语言的自然断句为基础，优先让第二行比第一行长；每行独立按页面中线居中。CJK 行末标点悬挂，不计入行宽及居中计算，完整标点仍保留在可访问名称中。最长一行超出可用宽度时，按真实文字宽度等比收小标题字号，不再折成第三行。页面根据标题、导航、控件区和上下留白的实际高度调整 16:10 演示宽度；控件区换行后再次计算，窗口缩放与字体加载完成后重新适配，演示说明及完整 CTA 区保持首屏可见。矮手机中演示画面可以进一步缩小，说明与 CTA 仍使用页面宽度，避免控件随画面变窄而反复换行。手机的首屏最小高度最多为 640px，较高屏幕提前露出后续内容；内容不足时均衡分配上下留白，超出时自然撑开。功能区与 Hero 保留正常区块间距。

顶部 Calmon 字标右上方使用小号 Beta 角标，产品名与定位语仍保留原来的字号和对齐。

## 面板文字与字体

`CalmonKeyPanel.astro` 用原生五个分组、行标题和键帽组成真实 HTML；38 种语言文案从 App 的 String Catalog 提取，原生 Z Labs RoundPix 12px 字体按实际字符生成按需 WOFF2 子集，并按 OFL 要求改名为 calmon Panel Web。字体与许可证放在 `src/assets/fonts/calmon-panel*`，来源及哈希位于 `scripts/assets/calmon/key-panel-text-source.json`。面板不使用 img、canvas、截图背景或整体缩放；文本可选择和由辅助技术读取。快捷键列表的键位也使用同一字体、18px 字号及键帽大写形式；字体子集覆盖支持的字符；缺少完整字形或需要连写的语言整段使用系统字体，键帽保留原版像素字体。常规宽度双列，窄屏单列，保持字号。媒体下载中的原生截图继续独立保留，网页面板不冒充原生截图。

```sh
python3 scripts/prepare-calmon-key-panel.py --app-source /path/to/calmon
```

### 功能配图

`CalmonFeatureArt.astro` 为六项功能提供局部动态示意，复用原生系统 App 图标。图示统一 140px 高、最多 280px 宽，去除容器左内边距。Pin / Sky / Max Deck 标识由 `capture-leader.swift` 直接调用 App 的 `TabVisualMetrics.drawMark`，以 48 pt 设置、2× 分辨率输出；用 46×31px 窗口裁去原图透明边距，保留原生像素网格并对齐可见左缘。

功能标题与正文统一间隔 8px；中等宽度图文并排时，标题行只占文字所需高度，额外留白留在正文下方。

滚动示意窗口高 124px，左右箭头悬浮于窗口内底部，不占图示高度；外层仍为 140px，与横排其他图示的标题保持对齐。

标题与正文不动，图内分别演示：窗口等宽左右移动、堆叠页切换、固定列旁滚动、加入 Pin Deck、Sky / Max Deck 图标进入，以及标签依次高亮。每轮 8–9 秒，动作之间停留；滚动窗口始终保持尺寸，边缘由视口实际裁切，不画假窄窗。与入门图示共用 `calmon-illustration-motion.ts`：等待加载遮罩结束，75% 可见时循环，离屏或页面隐藏时停止；减少动态效果时显示完整静态结果。配图不叠纸纹，不作为 App 截图进入媒体下载包。

Pin Deck、Sky / Max Deck、标签三张图统一使用 140px 高的浅色画幅，避免孤立的小图标显得过轻。前景居中，两行 Sky / Max Deck 图标上下各留 18px；Pin Deck 图标为 48px，标签 App 图标为 40px，桌面数字对齐 App 图标的视觉中心。Sky / Max Deck 各展示两个图标，保留原生标记的像素尺寸。

正文布局图使用原生 `map-normal.png`，只调整图标的行内垂直位置，文字保持正文基线。标题栏副标题为 A scrolling tiling WM。

## Favicon

产品页中英文与 Calmon Press Kit 共用 `CalmonFavicon.astro`，通过 `prefers-color-scheme` 选择亮暗版本。亮色版以原版六色绿色斜条纹为背景，字母为白色；暗色版沿用 App icon 的纯黑背景与彩色条纹字母。背景圆角，保留完整色带，不加玻璃或阴影。网页大图与媒体包继续使用原版 App 图标。

专用 16px、32px PNG 复用原生菜单栏圆润轮廓，逐字映射到整数像素，不插值混色。16px 下四周留 2px，CALM 占 12×12px，字母间留 2px，32px 按比例翻倍。颜色明确嵌入 sRGB；亮暗 ICO 分别直接封装对应 PNG 的原始字节。运行 `python3 scripts/prepare-calmon-favicons.py` 重建；脚本核对颜色、尺寸与 ICC，来源及输出哈希记录在 `scripts/assets/calmon/favicon-source.json`。

## 开始使用图示

`CalmonSetupArt.astro` 的三张静态底图分别说明移入「应用程序」、打开辅助功能开关，以及布局图打开按键面板。区块标题「开始使用 / GETTING STARTED」始终横排。使用 1、2、3 圆形编号与细连线串起流程。1024px 起为横向三步：各步骤标题竖排于编号下方，文字的视觉中心对齐编号；图示与说明位于右侧，三张画幅顶端及正文基线一致。较窄窗口和手机使用左侧编号的纵向步骤，步骤标题横排，图文左缘对齐。第三步仍绘制连线，横向延伸至末列右缘，纵向延伸至最后一步底部。

三张图示使用相同的 224×104px 浅绿色圆角画幅、12px 内边距与淡黑色内描边。画幅紧接标题、左缘对齐，图形组合在画幅内居中，避免开关示意视觉上过轻。32px App 图标与安装图的 40px 图标平衡视觉重量；开关行与按键面板均为 176px 宽。标签栏图标使用 28px，Finder 补偿原图 2.625px 的透明留白，布局图连线对齐图标可见中心。辅助功能不重复显示标签，原生图标置于步骤标题右侧。

动效参考 [Aave GHO](https://aave.com/gho) 的局部图形变化：标题与说明静止，等待加载遮罩消失，图示至少 75% 可见后开始。以 6 秒为一轮，箭头前移、开关打开、按键面板淡入，结果停留后柔和复位。离开视野或切换到后台时停止，`prefers-reduced-motion` 下始终显示静态结果。示意图不要求点击，也不作为 App 截图加入媒体资料包。原版文件夹与 SF Symbols 的导出脚本、来源哈希见 `scripts/assets/calmon/export-setup-art.swift` 和 `setup-art-source.json`。

页面内容顺序：Hero → 功能列表 → Getting Started → 鼠标与快捷键说明 → FAQ → 发布与反馈。

FAQ 内容左缘与其他区块一致；1240px 起，标题竖排放在内容左侧，间隔 28px。较窄窗口将标题横排置顶，避免挤占内容宽度或超出屏幕。常用按键区与模式说明间隔 28px，小标题与首行按键间隔 8px。

下载 CTA 最小宽度 160px，Hero、入门步骤和底部均指向公开 Releases。入门下载以行内 pill 强调；底部下载独立一行、左对齐。反馈框以 Beta 免费为标题，邀请到 X 反馈，整块背景为 imagegen 生成的正向手绘米白明信片、绿色邮票，纸张铺满四边，正文独立置于上层，明信片底图固定，左下角的独立透明叶片图层以茎部为轴做 5.5 秒轻摇循环；离屏、后台及减少动态效果时停止。页脚不再显示年份。

入门步骤下方说明 Calmon 不显示 Dock 图标，并内嵌原生菜单栏图标，提示从菜单栏找到 App。

## 38 种语言与字体

网站语言以 `presskit-supported-languages.json` 的 App 快照为准。`calmon-locales.mjs` 保留中英标题，`src/i18n/calmon/*.json` 提供其余 36 种语言的完整正文、演示和控件文案；地区版本有独立入口。产品页与 Calmon 资料页各提供 38 种语言，资料包包含 38 个 README；原生面板截图逐语言对应 App 的真实本地化，语言选择、预览与下载保持一致。共用媒体汇总页继续保持原有 17 种界面语言。

阿拉伯语、希伯来语正文与按键面板 RTL；桌面演示本身保持实际窗口方向，其容器独立居中。连写文字的步骤与 FAQ 标题保持横排。功能标题用短文案；1280px 桌面和 375px 手机的 38 种语言均检查单行、无横向溢出和演示居中。较长的区块标题允许自然换行，常规行高 1.15，CJK 1.28，连写文字 1.35。

越南语标题用 Oswald 700，保持窄体厚重风格且覆盖全部声调字符。希腊语保留 Sofia Sans Extra Condensed，补充原字体希腊字形；采用独立 CSS family，避免静态 900 字面干扰其他语言的变量字体匹配。希伯来语、泰语、阿拉伯语、印地语采用系统对应文字字体。字体来源为 Google Fonts 官方 CSS 服务及 Google Fonts OFL 许可，文件、源 URL 和哈希见 `scripts/assets/calmon/website-fonts.json`。

完整演示移除新建空桌面的停顿，改为把窗口移到已有桌面；每一步都保留可见窗口。原生全屏期间，右上角全部状态项目和播放控制随菜单栏隐藏，退出后恢复。模型检查包含空桌面回归用例。

验证：`node scripts/check-calmon-locales.mjs`、`node --test scripts/test-calmon-desktop.mjs`、`npm run build`。

## Localized panel previews

The product page keeps semantic text and provides a language selector beside the panel title. Press Kit uses original native PNGs for all 38 app languages, with matching preview and download links. Rebuild only these PNGs with `python3 scripts/prepare-calmon-assets.py --app-source /path/to/calmon-src --panels-only`, then regenerate the press kits. Byte-identical regional images share an archive file. Native Dark icon previews use the Dark export, independently of the current website theme.
