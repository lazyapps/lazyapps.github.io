# Header scroll and FondFont sun

- Shared `SiteHeader`: transparent at scrollY 0, no bottom border; sticky at top with a full-width paper tint and 16px backdrop blur only when scrolled. Passive scroll updates are coalesced with requestAnimationFrame; pageshow restores the correct state after history navigation.
- FondFont uses `homeMark="sun"`: original red 10px core and 32px ray SVG, 24-second rotation, hover scale, visibility pause, reduced-motion support, and `data-nav-sun` for the existing scene lighting.
- Generated output: 68 pages share the header. The sun appears on all seven FondFont locales and its root page; Press Kit retains the shared wordmark.
- Browser checks: 1280px Press Kit and FondFont top/scroll states; FondFont return to top removes the blur; 390px FondFont and 320px French product Press Kit have no horizontal overflow. Scrolled headers stay at y=0 with zero bottom border.
- `npm run build` passed: 71 pages, SEO, game artifacts, seven Press Kits and their language rules. `node scripts/check-fondfont-page-sun.mjs` passed all four projection scenarios.

See `checks.json`, `generated-pages.json`, and the adjacent screenshots.
