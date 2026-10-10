# Product copy and Press Kit completion · 2026-10-10

## Delivered

- Functional landing copy and SEO synchronized across seven products / 60 landing entries. YiYan's actual short-copy rendering and its generator are both updated. Application names, availability, quantities, real platform limitations and existing official links retained.
- All 57 App-supported language folders contain Markdown README.md; seven ZIPs put language folders and shared original images directly at root, with byte-hash deduplication. Product-copy changes and native icons regenerated into all packages.
- Shared SiteHeader across product templates and PressLayout. Product pages retain their language picker. Individual Press Kit headers have a right-aligned return-to-all link, per the later user request; the hub has no extra header navigation.
- Hub matches homepage typography, paper, grain, product colors and pill controls. Rebuilt large PRESS KITS hero; removed decorative labels and language counts.
- Individual Press Kit hierarchy: native icon and ZIP download, compact product facts, one language's product description and image gallery, usage and contact. Native select switches description, README and images together; language hash links work. HTML details provide access without JavaScript; single-language pages omit the unnecessary selector.
- Image captions group title with the download button, preserve original dimensions and provenance notes. Image previews contain the complete image; native icons have no second CSS mask. Interactive download controls have at least 40px hit areas, primary controls at least 48px, visible keyboard focus, restrained press feedback and reduced-motion support.
- PressKitClosing is mounted once by PressLayout, shared by the hub and all seven individual pages. Contact typography, email pill, spacing and focus behavior are identical. Product pages pass their name for the optional, initially collapsed usage instructions. SiteFooterBase remains the common main-site footer.
- Eight homepage icons, including Yifan, now use native App assets. Seven Press Kits use full native icons. Icon Composer assets are exported with Apple's ictool at Default 1024×1024; XVDL is a byte-identical copy of its original 512@2x AppIcon. Asset snapshots, production project commit and source/output SHA256 live in scripts/assets/native-icons/sources.json. Export script is reproducible with Xcode; site builds need only committed snapshots and outputs. Astro serves web-sized WebP previews while downloads retain the full original PNG.
- docs/PRESSKIT.md and AGENTS.md encode the new-product/update requirements, language folders, original icon quality, shared header/footer and reusable closing component.

## Independent review

Read approach-advice.md and completion-advice.md. The completion advisor found two substantive omissions, both fixed before final build: World Book explicitly uses archived, non-live CIA World Factbook data, with different reference years and no CIA affiliation; every KeyHop App language includes Apple silicon/macOS 26+ requirements, including the dedicated Italian media copy. Native asset quality and final UI were verified directly from original resources and rendered pages; no further material uncertainty required another consult.

## Validation

- Final npm run build passes: 71 pages, 70 canonical sitemap URLs, reciprocal hreflang, metadata/application description consistency, internal links, Shheep artifact isolation and Press Kit contracts (7 products / 60 landing entries / 57 App-language folders).
- check-presskits.mjs verifies native icon snapshots and exported PNG hashes, exact 1024×1024 dimensions, language coverage, README relative references, asset bytes, shared-root deduplication and ZIP member bytes/structure.
- Original copy review: all 60 landing routes at 320px, 27 representative responsive checks and 14 previous Press Kit checks; see existing JSON reports.
- New layout: all seven individual Press Kits at 320/768/1280px: 21 checks, no page or H1 overflow, one shared header, English initially active, optimized native icon previews, no broken visible images. See polished-kit-responsive.json.
- All 57 actual select changes at 320px: one visible panel, selected language and language tag agree, matching README href, proper Arabic RTL direction, images present, no overflow. See polished-kit-languages.json. Also tested direct #language-zh-Hans navigation.
- Shared closing: hub plus seven individual pages at 320/768/1280px: 24 checks. Exactly one closing and one main-site footer; correct optional usage/back-link presence; matching heading/button styles by viewport and 48px email control. See polished-closing.json.
- Browser downloads: CHMate full ZIP and Chinese README match the generated files byte-for-byte. See polished-downloads.json.
- Keyboard Tab from the native language selector focuses the matching README link, with 2px orange outline / 4px offset. Usage disclosure opens normally. Browser console contains no warnings or errors.
- Homepage icon DOM: all eight use WebP previews, square dimensions, complete native art and no CSS crop; desktop has no horizontal overflow.
- Saved updated hub, individual-page and shared-closing desktop/mobile screenshots. Browser viewport reset after checks.

No commit, push or deployment was requested or performed. Existing unrelated analytics/video work was preserved.
