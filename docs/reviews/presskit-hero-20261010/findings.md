# Press Kit hero · 2026-10-10

## Final revision

The user rejected the full-width color wash. Removed it from the shared template, restored the main site's paper background, original 48px desktop bottom spacing and muted Chinese description color. Native icons retain their shell-free presentation. Updated docs/PRESSKIT.md accordingly. Build passes; rendered CHMate at 1280px and 320px has no hero pseudo-background or horizontal overflow. `paper-desktop.png` shows the current result. The notes and screenshots below document the earlier rejected treatment.

## Earlier treatment (superseded)

User requested removing the additional icon shell and extending its product-colored background across the complete hero, with integration into the page.

- Shared product Press Kit template removes icon-wrapper fill, border/shadow, corner radius and 30px/22px inner padding. Native App icon files remain intact; the larger desktop image has a 300px / 600px Astro preview, sourced from the original 1024px PNG.
- A pointer-transparent full-width background uses the existing product color blended with paper. It fades from paper at the header edge into the product color, then back to paper before the facts row. Existing page grain, typography, orange action button and shared header/footer continue to apply.
- Desktop bottom breathing room grows from 48px to 64px; mobile keeps the compact original title/icon arrangement and spacing.
- Chinese hero description is darkened relative to the product color for readability.
- docs/PRESSKIT.md records the no-extra-shell and full-hero color treatment for future products.

npm run build passes all 71 page, SEO, Shheep artifact and Press Kit checks. responsive.json checks all seven individual pages at 320/768/1280px: no document/H1 overflow; icon wrapper has zero fill, padding, radius or shadow; background width equals the viewport. Screenshots show CHMate, KeyHop and YiYan desktop, plus CHMate mobile. Original downloadable icon files and ZIPs were not modified.
