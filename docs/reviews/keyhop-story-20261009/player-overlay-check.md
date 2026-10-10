# 视频内右下角按钮

按用户最新要求将播放／暂停和声音按钮放入 hero-film 内，绝对定位右下角，半透明深色底与白色图标。桌面44px，窄屏24px；手机端窄控件避开最长俄文字幕（776/1280画面宽）及上方 App 图标。视频本身不变。

检查：完整构建、SEO通过；12路由的两个按钮均位于视频 figure 内。390px 手机端和1512px桌面实测控件在画面内，无横向溢出，播放／暂停和声音切换成功。截图 player-overlay-mobile.png、player-overlay-desktop.png。临时视口、暂停与定位恢复。之前 browser-v3.json 及 completion-v3-advice.md 是外置控件时的媒体交付记录，当前页面控件检查以本文为准。
