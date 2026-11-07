# Yilo release validation · 2026-11-07

Current product: Yilo / 亦言, canonical /yilo/ with twelve localized pages,
updated release links, native icon, learning-first copy and current Press Kit.
GitHub Pages serves immediate HTML legacy redirects, not HTTP 301 responses.

The homepage and product pages share a native pelican animation. It shows
localized input, a complete genuine native learning record, then a human
conversation using the learned expression. English input produces Simplified
Chinese with Pinyin and Japanese with Romaji. Other locales retain Chinese
input and English/Japanese outputs. Reduced motion shows the static record.

The plain Sound control sits inside the canvas at bottom right, aligned with
the learning card. It has no pill, background, border or shadow and retains a
44px target. Sound is opt-in; no Pause or Replay controls appear.

Validation completed:

- Full site build, SEO, legacy route, Press Kit, native capture and film-source
  checks pass. Strict TypeScript validation passes for the demo controller.
- Twelve locales checked at 1280×720, 390×844 and 320×480; no horizontal overflow,
  cropped native record or overflowing ending text. Hero fits the first screen.
- Final Sound placement checked on desktop, mobile, short English/Korean and
  Arabic layouts. Right alignment error stays below 0.2 CSS px. At 320×480,
  the development-only Astro toolbar can intercept the control; it is absent
  from production output. Normal mobile activation starts and stops the audio.
- Continuous pedal motion preserves fixed leg lengths and wheel direction.
  The complete ending holds for 1.5 seconds. Stable text equivalents avoid
  repeated screen-reader announcements. Offscreen animation pauses.
- Full and central-square Open Graph compositions were reviewed. Exported
  square review crops now stay under .build/yilo-opengraph-review/.
- Active v22 social films retain all twelve native records and credited music.
  Source receipts and hashes remain in scripts/assets/yilo/.

Unpublished v6–v20 films, superseded H3 sources, generation logs, one-off migration
scripts and iterative browser captures are local-only archives under .build/.
They are excluded from Git and from the public directory. Final product assets,
current reproducible source inputs, license notices and source receipts remain
versioned. Previously published YiYan media are retained for existing links.

## Press Kit and Open Graph update

Removed Desktop wallpaper from the catalog, all twelve localized READMEs,
the asset manifest and ZIP. The unused source and its receipt are local-only
archives. Current Chinese/shared Latin OG cards directly reuse the native
icon's default coral-red gradient, keeping the genuine gold symbol intact.
Both 1200×630 images and their central 630×630 crops were visually checked.
The source receipt records native gradient values, inputs, safe bounds and
output hashes. Full build and ZIP/readme verification pass. Browser checks
confirm no wallpaper download links in English or Chinese Press Kit views.

## Localized source samples

All 48 native captures now use source text and source settings matching the UI locale. English learns Simplified Chinese/Japanese; Japanese learns English/Simplified Chinese; other locales learn English/Japanese. Product and hero sample JSONs are under `scripts/assets/yilo/capture/records/` and `hero-records/`. Native exports include current speech buttons from app source `197ac0e`. Captions, web animation input, accessible text, settings, Press Kit and v22 films use the same localized samples. Desktop and portrait input boxes were checked in all 12 locales. Review captures/logs remain local in `.build/yilo-locale-fix/`.

The twelve illustration variants use their own glyph, keyword and refinement request. All ten diagrams carry the matching source locale. Hero thought words also match the native input language. The 24 desktop/mobile cases in `.build/yilo-locale-fix/web-layout-checks.json` show no input overflow or wrong-locale diagrams; German hero/feature previews are saved alongside that report.
