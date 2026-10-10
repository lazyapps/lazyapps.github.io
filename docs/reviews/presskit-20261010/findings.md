# Press kits — 2026-10-10

Delivered seven product kits at `/<product>/presskit/` and a `/presskit/` hub. All 60 existing product landing pages (including language variants and the FondFont alias) link to the corresponding kit. Images, bilingual descriptions, current availability, official links, media contact and ZIP downloads are included.

User follow-up: README documents are separate Markdown files, `README.en.md` and `README.zh-Hans.md`. Each uses its own language for product name, prose, link labels, platform/release status and asset notes. Both files are separately downloadable and included in each ZIP. The obsolete README.txt is removed. `docs/PRESSKIT.md` makes this convention explicit for new products.

## Advisor decisions

- Approach consult: Astra xhigh approved a shared bilingual kit per product. Followed advice to label title-screen/native still/promotional assets accurately, distinguish TestFlight/coming-soon platforms, preserve third-party rights in context, discover products from independent application metadata, and retain general SEO while classifying product landing routes exactly. No newly generated art, soundtrack or raw font/model assets included.
- Existing app icons and imagery are reused without changing bytes. FondFont originals and World Book native frame are archived with source notes so preparation requires no private project. CHMate's reading still retains the Lewis Carroll / John Tenniel / Standard Ebooks attribution. Example third-party app imagery is kept in its screenshot context.
- Completion consult: Astra medium found no must-fix blocker and independently passed the presskit checker for seven products / 60 landing pages. The subsequent Markdown split is a mechanical refinement verified directly by the updated checker and browser.
- Deployment pipeline is Node-only. Download preparation therefore runs explicitly using a Python standard-library script; generated assets and ZIPs are durable repository files. Build validation detects drift without adding runtime dependencies.

## Validation

- Final `npm run build`: 71 pages built, 70 canonical sitemap URLs; SEO, game artifact integrity and presskit checks passed.
- Presskit check verifies product discovery/coverage, all locale footer entries, index/return links, per-language README Markdown content/download links, original source bytes, actual PNG/JPEG dimensions, hashes, exact decompressed ZIP members and archive/source equality. It rejects obsolete README.txt.
- Browser: all seven kits checked at 375 and 1280 CSS pixels; no horizontal overflow and one ZIP link each (`browser-checks.json`). Desktop and phone screenshots reviewed. FondFont ZIP successfully downloaded through the visible control; decompressed archive checks subsequently verified final regenerated files.
- Follow-up browser check confirms both Markdown download links; local hub left open for review.
- `git diff --check` passed. Existing unrelated untracked files were preserved. No deployment or Git commit made.
