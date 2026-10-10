# App-language press kits — 2026-10-10

This refinement supersedes the earlier two-language README convention recorded in `findings.md`.

Seven product ZIPs now contain 57 app-language folders: CHMate 15, FondFont 7, KeyHop 10, YiYan 12, Shheep 11, World Book 1, XVDL 1. Every folder contains a localized `README.md` and any language-specific images. Shared assets are stored once directly at the ZIP root, beside the language folders and manifest; README links use relative paths. There is no product-name wrapper folder.

Language coverage follows primary main-app resources recorded in `src/content/presskit-supported-languages.json`, rather than marketing-page languages or widget localizations. KeyHop includes Italian and excludes marketing-only Arabic, Hindi and Russian. World Book and XVDL have English kits. Committed snapshots and archived source images keep builds independent of private app projects.

## Advisor decisions

- Astra xhigh approved the interpretation, actual app-language coverage, root shared assets, deduplication and source-language labeling. Followed these recommendations in the catalog, generation script, docs and build checker.
- Astra medium completion review found no must-fix blockers. It independently confirmed all 57 language entries, archive structure and README references, and sampled localized descriptions of shared English captures and title imagery. Direct checks agree; no additional changes were necessary.

## Validation

- `npm run build` passed: 71 pages, 70 canonical sitemap URLs; SEO, game artifacts and seven-product/60-landing-page/57-language presskit checks passed.
- Every ZIP passed CRC verification. Archive members match generated files exactly, shared content is deduplicated, original image bytes and dimensions match sources, and every Markdown asset reference resolves within its archive.
- All seven pages checked at 1280 and 375 CSS pixels: no horizontal overflow or broken visible images. README download counts match each app language count (`language-browser-checks.json`).
- KeyHop Italian disclosure expands with localized copy. Its Markdown and ZIP downloaded through browser controls; downloaded bytes match repository files. The viewport override was reset after testing.
- `docs/PRESSKIT.md` and the root AGENTS pointer make this contract part of adding and updating product pages. Build checks enforce coverage, root shared files, deduplication and relative references.
- `git diff --check` passed. Existing unrelated changes remain preserved. No deployment or commit was made.
