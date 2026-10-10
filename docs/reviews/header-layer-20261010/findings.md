# Header above the embedded Shheep game

The exported game uses z-index 1000 inline and 10000 when expanded. The shared
header used 100, letting the inline game paint over it during scrolling.

The shared header now uses 1100. The global page loader uses 10001 so loading
still covers the header on every page. Focused skip links use 1101 to remain
visible and operable above the header. The layer order is recorded in PRESSKIT.md.
Generated game artifacts remain unchanged.

Browser verification (`checks.json`):
- Desktop game overlapped the header from y=-7.4 through y=668.6; hit testing at
  the home link, product and language control returned header elements on top.
- Mobile header retains z-index 1100 and has no horizontal overflow.
- Expanded game retained z-index 10000; the close button was on top and closing
  successfully restored inline mode.
- Focused skip link had z-index 1101 and was the top hit target.
- Active preloader had z-index 10001 and covered the header.

`npm run build` passed all 71 pages, SEO, exported game artifact and Press Kit
checks. See `shheep-header.png` for the overlapping game and header.
