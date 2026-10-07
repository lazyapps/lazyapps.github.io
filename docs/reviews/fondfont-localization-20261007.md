# FondFont localization review — 2026-10-07

Reviewed the current FondFont page and installation guide in all seven locales:
English, Simplified Chinese, Traditional Chinese (Taiwan baseline), Japanese,
Korean, French and German. Changes are limited to `src/i18n/fondfont-locales.mjs`
and `src/i18n/fondfont-install.mjs`. The factory scene's visible labels and alt
text were reviewed and retained.

## Corrections

- Traditional Chinese retains Apple's 字體 / 描述檔 / 檔案 terminology; uses
  iCloud 雲碟 and the app's 字體系列 field name. Device-local generation is
  expressed as 在裝置上產生. Directional copy uses 畫面下方 / 首頁上方.
- Simplified Chinese uses iCloud 云盘 and 隔空投送.
- All installation headings explicitly qualify supported/compatible apps.
- All seven pending-profile notes describe automatic deletion if installation
  is not completed within eight minutes of download.
- Japanese Settings instruction now names プロファイルがダウンロードされました.
- Korean prose uses 프로필 and the Settings entry 프로필이 다운로드됨. The
  app's literal custom button 프로파일 다운로드 remains unchanged when quoted.
- English profile creation/unsigned wording, French closing copy, and German
  Schriftfamilie, download verbs and articles were improved.
- Repetitive close/reopen paragraphs were condensed in each locale.

## Evidence and deliberate exceptions

Apple's localized installation instructions:
[English](https://support.apple.com/en-us/102400),
[Simplified Chinese](https://support.apple.com/zh-cn/102400),
[Traditional Chinese](https://support.apple.com/zh-tw/102400),
[Japanese](https://support.apple.com/ja-jp/102400),
[Korean](https://support.apple.com/ko-kr/102400),
[French](https://support.apple.com/fr-fr/102400),
[German](https://support.apple.com/de-de/102400).

Apple localizes [iCloud 雲碟](https://support.apple.com/zh-tw/118443),
[iCloud 云盘](https://support.apple.com/zh-cn/118443) and
[隔空投送](https://support.apple.com/zh-cn/119857).
Apple Taiwan's font feature is named
[字體](https://support.apple.com/zh-tw/guide/iphone/iphb2517689c/ios).

Actual app labels were checked against the sibling iOS app's localized strings
and the preserved native capture assets under
`scripts/assets/fondfont/install-capture-20261007/`:

- Literal `Edit`, French/German `Inst.`, Traditional Chinese `打開設定` and
  Korean `프로파일 다운로드` are preserved to match the current app.
- Japanese and Korean system download overlays independently confirm the
  corrected system labels. The app-authored instructions behind those overlays
  still contain older wording; this website task does not modify the iOS app
  or retouch its screenshots.
- German `de/permission.ax.json` confirms the actual system button `Zulassen`.
  Keep that website instruction even though the app's own help says `Erlauben`.
- 字體列表 and Simplified Chinese 字族 remain valid terms; optional stylistic
  replacements are not treated as errors.

An independent read-only advisor reviewed all seven locales before the broad
edits. The suggested system corrections and natural-language improvements were
accepted. Optional replacements of valid terminology were not adopted wholesale.
Its German permission uncertainty was resolved using the native capture above.

## Validation

- `node --check` passed for both edited modules.
- `npm run build` passed: 52 routes, including all seven FondFont locale routes.
  The existing Three.js chunk-size warning remains unrelated to copy changes.
- An ad hoc Node check verified unchanged locale schemas, route/product metadata,
  four installation steps per language, action counts, screenshot paths, quoted
  app buttons, and corrected Japanese/Korean system labels.
- All seven generated HTML pages contain their updated heading and deletion note.
