# Shheep deployment artifacts

The game source, build tools, tests and native fixtures are maintained outside this public repository. This repository contains only the exported game wrapper (`src/components/ShheepGame.astro`), hashed obfuscated JavaScript and minified CSS (`public/shheep/game/`), and the runtime art/audio/font assets. The landing page remains editable here.

Do not edit the generated game wrapper or bundle. Build and test in the private web project, then run its export command against this checkout. The ordinary site build needs no access to private sources or obfuscation tools.

The exported JavaScript uses identifier renaming, encoded string tables, control-flow transformations and injected dead code, with no source maps or development handle. Obfuscation increases inspection cost; it cannot prevent extraction of browser code or art assets. No debugger traps or domain locks are used.

The game uses a stable 600-unit course and local browser records. Game Center rankings, challenges and invitations remain iOS-only.

## Local recording mode

Start `npm run dev`, then run `npm run record:shheep` in another terminal. This opens `http://127.0.0.1:4321/shheep/?record=1` in a temporary Chrome profile with audible autoplay allowed. To use another port, run `python3 scripts/open-world-book-recording.py --url http://127.0.0.1:PORT/shheep/`.

`?record=1` waits for the shared page preload animation to finish and the game assets to load, then runs one 20-second sequence: the five-second opening, automatic gameplay, a natural obstacle collision after controls are released at 14 seconds, and the complete wake animation. At 20 seconds it freezes the ending and stops music; reload to record again. Recording scores and sound changes stay in memory. It skips coaching and hides the cursor and Astro toolbar. Leaving the viewport or tab pauses the active recording clock; returning resumes it. Manual pause still works.

This mode requires the private web project and its installed dependencies. The dev middleware builds its recording entry on request, using `../../_vibe/shheep/web` relative to this repository by default; set `SHHEEP_WEB_DIR` to override the location. The recording URL and private bundle are served only by local dev. Production builds and preview use the ordinary exported game, even with `?record=1`.

Opening the URL directly also starts autoplay, but an ordinary browser may block music until a user gesture. The recording launcher enables audible autoplay only for its temporary Chrome session.

## Landing page and social sharing

The landing page renders its title, description, canonical URL, OG/Twitter tags, app metadata and explanatory content as static HTML. The site build includes `/shheep/` in the canonical sitemap and checks its `WebApplication` data, including the `GameApplication` category.

The native app is coming soon. The download badge, native app metadata and Safari Smart App Banner are commented out in `src/pages/shheep.astro`, ready to restore at launch. The saved App Store URL uses World Book's campaign parameters: `pt=259198&ct=lazyapps-en&mt=8`. The current CTA is an App Store badge labeled “Coming soon on the App Store” without a link, and search/social descriptions reflect the launch status.

The page is English-only. The game's eleven selectable languages do not translate the landing page; localized SEO would require separate translated URLs and reciprocal hreflang links. See [Google's multilingual site guidance](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites).

Structured data currently describes the playable browser game without inventing prices, ratings or reviews. It does not meet all requirements for Google's software-app rich result, which also requires offer and review/rating information. See [Google's software-app structured data requirements](https://developers.google.com/search/docs/appearance/structured-data/software-app).

`public/shheep/opengraph.png` uses the original bedroom, sleeping girl and pixel wordmark. Rebuild with `python3 scripts/render-shheep-opengraph.py`; inspect both the 1200 × 630 image and its central 630 × 630 crop. This game-specific style is documented in `docs/OPEN_GRAPH.md`.

Browser checks covered 1280px desktop, 390px and 320px mobile layouts, game startup, license expansion, keyboard skip navigation, reduced-motion content visibility, missing images and console errors. With JavaScript disabled, the explanatory content, launch status and license links remain available. The canvas game requires JavaScript and visual interaction; these checks do not establish full screen-reader accessibility or real-user Core Web Vitals.

The exported game JavaScript is approximately 780 KB uncompressed (263 KB gzip); changes to its loading behavior or game accessibility belong in the private web project, followed by a fresh export.
