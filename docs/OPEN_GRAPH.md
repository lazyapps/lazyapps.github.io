# Open Graph 图片规范

- 输出 `1200 × 630` PNG，并把正中央的 `630 × 630` 视为安全区；图标、名称等核心内容必须完整落在安全区内，横向两侧只能放可被裁掉的背景。
- 构图保持简洁、含蓄，避免用功能示意或说明文案把概念讲满；没有额外要求时，只使用无底板的产品 symbol 与本地化产品名，不使用 App 图标的圆角方形容器。
- 按主体的可见边界对齐 symbol 与名称，使两者视觉等高、间距紧凑，再将组合整体居中；独立圆点等悬浮重音不计入高度。
- 保持 symbol 各部分的品牌色与不透明度一致；提取透明背景时，不得让局部笔画褪色或变浅。
- 背景必须复用网站方案：底色 `#f8f8f6`；`src/assets/img/noise.png` 以 `125 × 125` 平铺，透明度 `0.09`，依次应用 `contrast(125%) brightness(60%)`。
- 使用真实品牌资产并确定性渲染文字，不生成或近似重画 Logo、图标、产品名。
- Latin 标题与标题性短句统一使用网站 `.dsp` 字体：`Sofia Sans Extra Condensed`，字重 `900`，字距 `-0.01em`。
- 只本地化实际变化的产品名；画面与文字相同的 locale 必须共用一份 shared 资产和默认映射，不复制逐语言图片。
- 交付前同时检查完整横图和居中方形裁切，并运行项目构建。

## Shheep

Shheep 按游戏本身的可爱像素风制作，使用原版卧室、睡着的女孩与像素标题素材，替代默认的纸色背景和网站标题字体。保留 `1200 × 630` 尺寸及中央 `630 × 630` 安全区；使用 nearest-neighbor 整数倍缩放，不重画品牌资产。运行 `python3 scripts/render-shheep-opengraph.py` 可重建。

## Doze

Doze 使用当前 AppIcon.icon 中的原版 `Monogram.svg`，保留纯金色轮廓与不透明度，不带 App 图标底壳。`scripts/render-doze-opengraph.py` 同时更新透明符号及全部 12 种语言的 OG；来源、输出哈希与安全区记录在 `scripts/assets/doze/symbol-source.json` 和 `opengraph-source.json`。

## Calmon

Calmon 使用原生 `CGPath` 直接导出的方格字标，保留与 App 图标一致的六色绿色斜向光谱，不包含玻璃、光照或图标底壳。字形和位置不从位图描摹。两种网站语言共用 Calmon 字标和 `calmon-opengraph-shared.png`；名称首字母大写。运行 `python3 scripts/prepare-calmon-assets.py` 可重建，来源及安全区见 `scripts/assets/calmon/opengraph-source.json`。

## Yilo · 亦言

从当前 `AppIcon.icon` 的原版矢量层生成无底壳 symbol，保留默认柠檬金颜色与透明度；不从旧图标或位图描摹。背景按用户要求复用 App 图标默认外观中的珊瑚红线性渐变，颜色和方向直接读取 `icon.json`，替代默认纸色和纸纹，让金色 symbol 清晰可辨；不添加图标圆角方形容器。排版以除圆点外的主体可见高度对齐。简繁中文共用 `yilo-opengraph.png`（亦言），其他语言共用 `yilo-opengraph-shared.png`（Yilo）。运行 `scripts/prepare-yilo-brand-web.py` 与 `scripts/render-yilo-opengraph.py`；原始 symbol、输出哈希和几何记录见 `scripts/assets/yilo/brand-source.json`，OG 来源、背景定义、安全区和输出哈希见 `scripts/assets/yilo/opengraph-source.json`。方形裁切由脚本输出到本地审核目录；最终审核记录见 `docs/reviews/yilo-20261107/`。
