# Web fonts

The 2026-11-07 optimization reduces font delivery without changing typography.
The checked-in source fonts, fallback stacks, weights, styles and `font-display:
swap` remain intact. Font generation is manual; a production build only checks
the generated assets.

## Regenerate

Requires Python 3.9+, Node/npm and the existing project dependencies. The font
tool versions are pinned in `scripts/requirements-web-fonts.txt`.

```sh
python3 -m venv .build/web-font-env
.build/web-font-env/bin/pip install -r scripts/requirements-web-fonts.txt
npx astro build
.build/web-font-env/bin/python scripts/optimize-web-fonts.py
npm run build
```

The first Astro build supplies current rendered text to the manual optimizer;
it deliberately skips the final font checks, which may reject stale subsets.
Use `--generate-only` to inspect outputs before switching CSS. Review generated
WOFF2 files, stylesheets and `scripts/assets/fonts/web-fonts.json` together.
These are production assets to include with the project change; temporary
builds, screenshots and experiments remain in ignored `.build/`.

Rerun and visually compare when fonts, page text, CSS font matching/features,
locale coverage or fontTools/Brotli versions change. New characters absent from
the original fonts still use the existing fallback stack; this process does
not add original glyph coverage. If Yilo needs new source glyphs, first run
`scripts/prepare-yilo-hand-fonts.py`, then this optimizer. Rebuild and compare
after either stage.

## Delivery and provenance

`scripts/assets/fonts/web-font-plan.json` records the original face descriptors
and CSS coverage. `web-fonts.json` records source/output hashes, byte sizes,
actual character maps, glyph counts, axes, OpenType features, hint tables,
metrics and derivative family/PostScript names. Copyright/license records stay
inside the outputs; OFL notices remain beside the originals in
`src/assets/fonts/` and `src/assets/fonts/yilo/`. Yilo's upstream sources and
licenses are also recorded in `scripts/assets/yilo/hand-font-sources.json` and
served at `/v/yilo/fonts/credits.txt`.

Each subset retains shaping closure, available features and hinting. Generation
independently verifies every output character's decomposed outline, advance,
side bearing and glyph bytecode against its source, plus the global hint
tables. Build checks verify hashes, metrics, derivative names, effective cmap
coverage, disjoint CSS ranges, descriptors and external preloads.

The original last matching face keeps ownership of overlapping code points.
Each generated `unicode-range` is the actual output cmap, restricted to the
original CSS coverage. Supported Latin-1, Latin Extended-A and combining marks
stay with the Latin core; no ASCII-only split separates those sequences.
Script-only faces have no artificial ASCII core and load only when needed.

The Yilo Han core contains supported kana/punctuation and Han text on non-CJK
product pages. The rest loads on demand. Chinese, Traditional Chinese,
Japanese and the dynamically translated Press Kit use one merged Han face:
splitting that face changed contextual punctuation rendering. All original
effective Han coverage remains available in both delivery modes.

`FontPreloads.astro` preloads the shared Sofia Latin logo face, Yilo's Latin and
appropriate Han face, the Calmon panel face (plus its Greek/Vietnamese title
face where needed), and Fondfont's whole Geist Mono face. It does not preload
script-only extensions or Calmon Pixel. Preloads use matching anonymous CORS
and fingerprinted external assets. There is no font embedding or idle precache.

## Per-font sizes

All sizes are WOFF2 bytes. “Glyphs” includes shaping/closure glyphs; “characters”
is the original cmap count. Output coverage is limited by the original CSS,
so removing unused Latin glyphs from a script file does not remove a rendered
character. Core and extended sizes are alternatives to the merged CJK file,
not files every visitor downloads together.

| Face | Before | After | Original glyphs / characters |
| --- | ---: | ---: | ---: |
| Sofia Latin variable | 40,336 | 40,336 retained | 276 / 224 |
| Sofia Latin Extended variable | 18,076 | 18,076 retained | 187 / 128 |
| Sofia Cyrillic variable | 25,332 | 25,332 retained | 171 / 106 |
| Sofia Cyrillic Extended variable | 3,384 | 3,384 retained | 25 / 12 |
| Sofia Greek 900 | 5,532 | 5,532 retained | 94 / 72 |
| Oswald Vietnamese 700 | 16,400 | 16,400 retained | 567 / 529 |
| Yilo Latin | 24,296 | core 24,292 | 220 / 137 |
| Yilo Cyrillic | 31,292 | on demand 16,304 | 189 / 184 |
| Yilo Han | 266,732 | core 39,264 + extended 177,124; merged 213,964 | 1,743 / 1,372 |
| Yilo Hangul | 91,776 | on demand 80,512 | 515 / 426 |
| Yilo Devanagari | 113,620 | on demand 99,796 | 766 / 193 |
| Yilo Arabic | 39,636 | on demand 29,460 | 506 / 174 |
| Geist Mono | 50,764 | 50,764 retained | 1,159 / 889 |
| Calmon Pixel | 5,520 | 5,520 retained | 97 / 95 |
| Calmon Panel | 11,344 | 11,344 unchanged | 344 / 343 |
| Calmon Han | 10,988 | 10,988 unchanged | 299 / 298 |

Sofia retains the complete `wght=1…1000` axis (default 400). Calmon Pixel retains
`wght=100…900` (400), `wdth=50…200` (100), and `ROND`, `BLED`, `JITT=0…100`
(all default 0). The other listed files are static. Feature and hint-table
inventories are in the font manifest; source and output feature lists are
recorded separately because subsetting can remove features with no remaining
glyphs. Shaping closure is retained, including for Arabic and Devanagari.

The inventory covered 81 source font files: 16 under `src/assets/fonts/` and
65 public game/3D-sign fonts. The latter remain untouched because their
dynamic content or separate 3D rendering requires their existing coverage.
The local full inventory is `.build/font-optimization/source-inventory.json`.

## Per-page measurements

Cold-cache measurements use Chrome 157 in the desktop in-app browser on macOS,
1280 × 900 CSS pixels, DPR 1, after window/font/image readiness and settling.
Dates, random values and motion were held constant for comparable captures.
Payload is `PerformanceResourceTiming.encodedBodySize`; transfer is the observed
`transferSize`, including the local browser's reported response overhead.
These are font resources only, excluding CSS/HTML, images and movie/audio.

| Page | Payload before → after (B) | Cold transfer before → after (B) | Requests | Preloads |
| --- | ---: | ---: | ---: | ---: |
| `/` | 336,884 → 109,412 | 338,084 → 110,612 | 4 → 4 | 0 → 3 |
| `/yilo/en/` | 331,364 → 103,892 | 332,264 → 104,792 | 3 → 3 | 0 → 3 |
| `/yilo/` | 331,364 → 278,592 | 332,264 → 279,492 | 3 → 3 | 0 → 3 |
| `/yilo/zh-hant/` | 331,364 → 278,592 | 332,264 → 279,492 | 3 → 3 | 0 → 3 |
| `/yilo/ja/` | 331,364 → 278,592 | 332,264 → 279,492 | 3 → 3 | 0 → 3 |
| `/yilo/ru/` | 362,656 → 120,196 | 363,856 → 121,396 | 4 → 4 | 0 → 3 |
| `/yilo/ar/` | 371,000 → 133,352 | 372,200 → 134,552 | 4 → 4 | 0 → 3 |
| `/yilo/hi/` | 444,984 → 203,688 | 446,184 → 204,888 | 4 → 4 | 0 → 3 |
| `/yilo/ko/` | 423,140 → 184,404 | 424,340 → 185,604 | 4 → 4 | 0 → 3 |
| `/yilo/de/` | 331,364 → 103,892 | 332,264 → 104,792 | 3 → 3 | 0 → 3 |
| `/yilo/presskit/#fr` | 607,688 → 504,664 | 609,788 → 506,764 | 7 → 7 | 0 → 3 |
| `/calmon/` | 68,188 → 68,188 | 69,388 → 69,388 | 4 → 4 | 0 → 2 |
| `/calmon/ru/` | 93,520 → 93,520 | 95,020 → 95,020 | 5 → 5 | 0 → 2 |
| `/calmon/el/` | 73,720 → 73,720 | 75,220 → 75,220 | 5 → 5 | 0 → 3 |
| `/calmon/vi/` | 84,588 → 84,588 | 86,088 → 86,088 | 5 → 5 | 0 → 3 |
| `/fondfont/en/` | 137,644 → 137,644 | 140,644 → 140,644 | 10 → 10 | 0 → 2 |
| `/doze/fr/` | 40,336 → 40,336 | 40,636 → 40,636 | 1 → 1 | 0 → 1 |

The old global CSS also embedded 3,384 decoded font bytes as 4,512 Base64
characters; current managed font CSS embeds zero. This is separate from the
WOFF request totals above and is not a claim of 4,512 compressed network bytes.
The Cyrillic Extended resource now loads externally only if its glyphs are used.

No duplicate font URLs were requested on the 17 measured pages. English and
German Yilo loaded only Sofia Latin, Yilo Latin and Han core; Cyrillic, Arabic,
Devanagari and Hangul extensions appeared only on relevant pages. CJK pages
loaded the merged Han file rather than both split files. Warm-cache reloads
of English and Chinese Yilo reported **0 transferred font bytes** before and
after, while retaining their respective decoded/encoded resource sizes. Thus
cached body size is not being counted as a new transfer. Local-server overhead
and production cache/CDN headers may differ.

## Visual checks and retained alternatives

All 32 desktop PNG comparisons and three 390 × 844 mobile comparisons have
**zero changed pixels**. Desktop coverage includes the 17 measured pages,
feature/code details and a stress fixture: 700/900 display weights, italic/bold
handwriting, Latin accents, combining marks, code, Chinese/Japanese punctuation,
Arabic diacritics and Devanagari conjuncts. Noncomposable Greek `α̃` and Cyrillic
`Б́` combinations are included. Mobile covers English/Chinese Yilo and Calmon.

Early environment differences in dates, random demo state, scrolling and
screenshot scale were normalized before final comparisons. Font regressions
were fixed by keeping the original behavior:

- Restricting Sofia's weight axis changed logo/title strokes. Keep the entire
  original range, at about 15 KB over that smaller trial.
- Splitting Geist changed combining accents (254 pixels in the stress fixture).
  Keep the original file, costing 19,592 bytes over the English-only trial.
- Pinning Calmon Pixel axes and preloading that result changed the compact home
  demo (21,761 pixels). Keep the original file and natural CSS loading; this
  costs 3,672 bytes over the trial. Repeated baseline and trial captures were
  independently stable before this comparison.
- Splitting the CJK face changed contextual punctuation. The merged face costs
  174,700 bytes over the core alone, while saving 52,768 bytes versus the source.

These comparisons establish equality in this browser/environment, not across
all browsers or operating systems. No original system-font CJK rendering or
native screenshot typography was changed. General dynamic input beyond the
original cmap remains a fallback case.

Local evidence is under `.build/font-optimization/`: `final-before.json`,
`final-after.json`, `cache-results.json`, `final-pixel-diff.json`,
`mobile-pixel-diff.json` and matching PNG directories. To compare a new matched
capture set, install Pillow 11.3.0 in the review environment and run:

```sh
.build/web-font-env/bin/python scripts/compare-font-screenshots.py BEFORE AFTER --output .build/font-diff.json
```

For reproducible captures, build the same content before/after; use the same
browser, viewport, DPR, locale and scroll position. Fix dates/random demo state,
set reduced motion, disable animation/transition/caret in both review copies,
wait for window load, `document.fonts.ready`, visible image decoding and four
animation frames. Capture lossless PNGs at explicit viewport size and the
actual settled scroll offset. Review any changed pixels before accepting.
Do not inject these review settings into production pages.

## Subsequent localized-source update

The measurements above describe the font-optimization snapshot before the
localized screenshot-source correction. That correction adds a few supported
characters for the new Japanese, Korean and Arabic animated inputs and localized
captions. `prepare-yilo-hand-fonts.py` now retains the previous source cmap when
adding characters, so regeneration does not drop earlier supported glyphs.
Source and optimized receipts were regenerated; the font manifest contains the
current sizes. The earlier zero-diff comparisons concern identical content,
not the deliberately changed examples.

## Calmon key-panel refresh after shortcut changes

The later 2026-11-07 panel refresh replaces the obsolete hard-coded exporter with
an optimizer that reads the current checked-in `calmon-key-panel.json`. It never
rewrites panel rows or app terminology. The old subset lacked characters in the
new Display and Two-Digit Desktop rows: Japanese `ィレ桁`, Simplified Chinese
`两位号器数显示编`, and Traditional Chinese `位兩器數示編號顯`.
These now use the intended original pixel glyphs rather than per-character system
fallback. No copy, font size, spacing, weight, fallback stack or display policy
changed. Native app fonts and Press Kit screenshots are unaffected.

Regenerate manually after exporting current native panel content, or after
changing panel translations, shortcut legends, fonts, matching CSS or tool versions:

```sh
python3 -m venv .build/calmon-assets-venv
.build/calmon-assets-venv/bin/pip install -r scripts/requirements-web-fonts.txt
.build/calmon-assets-venv/bin/python scripts/prepare-calmon-key-panel.py --app-source /path/to/calmon
npm run build
```

The licensed original remains in the app's `Sources/Fonts/` with its notices.
The website retains the renamed font's OFL notice alongside its generated files.
`scripts/assets/calmon/key-panel-text-source.json` records original/output bytes,
glyphs, exact cmaps, axes, features, hinting, metrics, names, outline verification
and input/output hashes. The original RoundPix source has 13,302 glyphs / 13,301
characters, no variable axes, no GSUB/GPOS features and no hint tables. All output
outlines, advances and available hinting match that source. Supported Latin-1 and
Latin Extended-A remain available. Arabic, Hebrew, Hindi, Thai and other existing
system-text languages keep their previous rendering. Repeated generation produces
identical bytes and leaves panel data and app terminology intact.

Only the ASCII/keycap/punctuation core is preloaded. Other subsets have exact,
non-overlapping `unicode-range` rules and load only for matching characters;
separating Cyrillic from CJK avoids making Russian readers download Han glyphs.
The generated stylesheet contains all panel faces with no intervening fallback
face. Font requests stay external, fingerprinted and use matching anonymous CORS.
Build checks reject stale panel/translation inputs, changed font bytes, overlapping
ranges or preloaded extensions. Builds do not run the generator.

| Panel face | WOFF2 bytes | Glyphs / characters | Loading |
| --- | ---: | ---: | --- |
| Old combined subset | 11,344 | 344 / 343 | Every product page |
| Core | 5,264 | 162 / 161 | Preloaded |
| Latin extension | 4,664 | 111 / 110 | On demand |
| Cyrillic extension | 3,604 | 51 / 50 | On demand |
| CJK extension | 8,716 | 122 / 121 | On demand |

The English panel saves 6,080 bytes (53.6%); German saves 1,416 bytes and Russian
saves 2,476 bytes. Japanese and Chinese now cost 13,980 panel bytes, 2,636 bytes
more than the incomplete old subset, with one extra request. A single corrected
all-coverage reference is 11,312 bytes; splitting costs CJK pages 2,668 bytes versus
that reference in exchange for smaller downloads on the other 34 languages.
Averaging one panel visit per supported language gives 8,089 bytes, versus 11,344
before. This is an illustrative equal-locale average, not a traffic-weighted claim.

Cold-cache measurements below include **all page fonts**, in Chromium
153.0.8010.12, macOS, 1280 × 900, DPR 1. `encodedBodySize` is payload;
`transferSize` is measured transfer including local response overhead.

| Page | Payload before → after (B) | Transfer before → after (B) | Requests | Preloads |
| --- | ---: | ---: | ---: | ---: |
| `/calmon/` | 68,188 → 62,108 | 69,388 → 63,308 | 4 → 4 | 2 → 2 |
| `/calmon/de/` | 68,188 → 66,772 | 69,388 → 68,272 | 4 → 5 | 2 → 2 |
| `/calmon/ru/` | 93,520 → 91,044 | 95,020 → 92,844 | 5 → 6 | 2 → 2 |
| `/calmon/ja/` | 68,188 → 70,824 | 69,388 → 72,324 | 4 → 5 | 2 → 2 |
| `/calmon/zh-Hans/` | 68,188 → 70,824 | 69,388 → 72,324 | 4 → 5 | 2 → 2 |
| `/calmon/ar/` | 57,200 → 51,120 | 58,100 → 52,020 | 3 → 3 | 2 → 2 |
| `/calmon/vi/` | 84,588 → 78,508 | 86,088 → 80,008 | 5 → 5 | 3 → 3 |

All 38 cold-cache pages requested each font URL once; extension loading followed
actual characters, and no panel extension was preloaded. Warm visits to English,
Simplified Chinese and Russian transferred zero font bytes while retaining their
encoded resource sizes. Production cache/CDN headers can differ.

Visual coverage includes all 38 panels, plus whole keyboard sections and
390 × 844 mobile views for English, German, Polish, Vietnamese, Arabic, Japanese,
Simplified Chinese and Traditional Chinese: 54 matched frames. Comparing with the
old font gives 44 unchanged frames; the other 10 differ only at the four languages'
newly covered panel glyphs. With the corrected single-file reference, all 38
panels match exactly. Four wider/mobile comparison frames initially differed due
to sticky headers/skip links and their composited noise backdrop during scrolling;
recapturing the affected English, Traditional Chinese and Arabic views with fixed
and sticky overlays hidden in both review copies produced zero changed pixels.
All 54 frame comparisons are therefore accounted for, including nine clean
recaptures. This verifies this browser/environment, not every platform.

Full `npm run build`, font checks, locale checks and deterministic regeneration
passed. Local evidence, capture scripts, exact rerun parameters, cold/warm request
records, original font inventory and lossless screenshots remain under ignored
`.build/calmon-panel-font-review/`. Use the existing
`scripts/compare-font-screenshots.py` for matched capture sets.
