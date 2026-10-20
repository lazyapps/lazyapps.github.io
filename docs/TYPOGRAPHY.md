# 国际化字体与行高

`src/assets/s/site.css` 按实际使用的字体族维护 `--leading-display`（展示标题）与 `--leading-body`（默认正文）。产品页、存档页、隐私页和 Press Kit 共用这组规则。段落、表单、按钮及小字号说明可以保留适合自身用途的显式行高。

全站页面唯一的 h1（Hero 大标题）统一居中；正文、下载说明和各章节标题保留各自的布局对齐。

| 语言／字体 | 展示标题 | 默认正文 |
| --- | --- | --- |
| Latin · Sofia Sans Extra Condensed | 1 | 1.65 |
| 德／西／法／葡／意／荷文 · Sofia（含变音符号） | 1.08 | 1.65 |
| 土耳其文 · Sofia（大写 İ） | 1.14 | 1.65 |
| 俄文 · Sofia Sans Extra Condensed Cyrillic | 1.06 | 1.65 |
| 简繁中文 · PingFang／系统中文字体 | 1.12 | 1.75 |
| 日文 · Hiragino Sans／Yu Gothic | 1.14 | 1.8 |
| 韩文 · Apple SD Gothic Neo／系统韩文字体 | 1.12 | 1.7 |
| 阿拉伯文 · SF Arabic／Geeza Pro | 1.36 | 1.8 |
| 印地文 · Kohinoor Devanagari／Devanagari Sangam MN | 1.42 | 1.75 |

行高使用无单位数值，随字号变化。Arabic 与 Devanagari 保留变音符号、上标与下伸部的空间。Press Kit 汇总页的 Latin 海报标题保留原来的紧凑比例；土耳其文大写 İ 及其他字系使用各自的展示标题行高。

不要用全局 `:lang(...) { line-height: ... }` 给全部后代直接赋正文行高。`:lang()` 会同时匹配标题内部的 span、br 和标点，导致标题明明设置了紧凑行高，内部行盒仍被正文行高撑开。正文默认行高通过 body 继承；标题的内联节点和换行继承所属标题的行高。

显式 `lang` 是字体与行高变量的边界：先恢复 Latin 默认值，再按实际语言设置字体与行高。这样中文、阿拉伯文页面中的英文品牌名，以及 Press Kit 中与页面语言不同的素材语言，都能使用对应字体，避免继承外层字系的字体配置。

Doze、FondFont 的分行 span、KeyHop 的短语组合与 Press Kit 标题不再各自写通用固定行高，统一继承相应语言的标题节奏。CJK 行尾悬挂逗号继续保持零宽，不影响文字居中。

语言选择器保留 48px 点击区；透明原生 select 使用 `overflow:hidden`，避免长选项文本在 WebKit 中撑出页面宽度。
