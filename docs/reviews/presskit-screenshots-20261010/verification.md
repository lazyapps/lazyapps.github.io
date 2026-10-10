# Press Kit screenshots — 2026-10-10

Reviewed all 7 products and recorded 29 screenshot sources in `scripts/assets/presskit/screenshot-sources.json`.

- FondFont: replaced all 7 October 7 selection captures with today’s canonical native captures. All copies match the app-source files byte for byte.
- KeyHop: built current source as Debug. Captured isolated native preview with ten example bindings, default Option Leader, and app-key-map settings. Native JPEG 3456 × 2168 is shared. The Dev title and preview status are explicitly described. Normal user defaults and the previously running KeyHop Dev process were preserved; only the temporary capture process was closed.
- YiYan: removed obsolete August localized shots from downloadable kits. The two October 8 developer-supplied native originals are shared in English, with actual language identified in each of the 12 localized READMEs. Both files match original provenance SHA-256 values.
- CHMate: replaced 900 × 1200 compressed previews with 15 original 2064 × 2752 native localized captures. Italian uses its native reading capture of Pinocchio; the source note no longer incorrectly attributes all reading material to Alice.
- World Book: freshly captured the installed current 261010.0 (470) iPad app, with top navigation, at native 2064 × 2752. Original simulator view was restored to Countries afterwards. Argent services were stopped for this one device only.
- XVDL: current October 10 original and developer-requested edited presentation retained, clearly distinguished.
- Shheep: current title-screen export matches the native game project’s web preview byte for byte; explicitly labelled as a title screen.

Regenerated all 7 ZIPs and 57 localized README.md files. No obsolete localized YiYan screenshot downloads, CHMate JPEG downloads, or old KeyHop screenshot downloads remain. Shared files remain at archive root. Original source bytes match public and archived images.

`npm run build` passed: 71 pages, 60 app landing pages, 57 app-language folders, all source-review hashes, asset dimensions, ZIP contents, relative README links, language/hash rules, SEO and Shheep artifact checks.

Browser checks at 1280 × 900 confirmed updated CHMate, KeyHop, YiYan and World Book images load at recorded native dimensions. FondFont English and 390 × 844 Simplified Chinese both load today’s native image without horizontal overflow. French YiYan notes correctly identify shared English UI and Chinese example writing. Screenshot evidence and browser receipts are saved in this directory. Temporary QA tab closed and viewport override reset.

The freshness snapshot records an actual source review; it does not automatically know about future changes in private apps. The Press Kit update rule now requires a new review when UI changes, and the build rejects source changes without matching review metadata.
