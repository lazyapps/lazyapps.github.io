# Homepage copy and Press Kit style — 2026-10-10

The main-site homepage now describes what each app does. Removed the generic “small, focused / crafted / independent / since” copy from the introduction, loading text, card tags and repetitive footer FAQ. Product-page links now name the app's details instead of “Explore” or “Learn more”. The existing contact, Press Kit and privacy navigation remain available through the shared footer.

## Product copy

| App | Homepage description now covers |
| --- | --- |
| Shheep | A browser game: jump over fences, duck under bats, play a new nightly course. iOS is marked coming soon. |
| KeyHop | Switch to or launch Mac apps through ten home-row bindings; optional iCloud sync. |
| YiYan | Convert AI-tool input into natural English with explanations and examples; polish selected text or an input field. iPhone is marked beta. |
| XVDL | Download the highest-quality available MP4 from X using Safari on Mac. |
| CHMate | Read EPUB, CHM and MHT files; search chapters, highlight and annotate. |
| World Book | Country profiles, flags, rankings and a 3D globe offline; photos and regional maps available offline after download. |
| 一饭 | Fanfou timelines, mentions, direct messages, favorites and photos on iPhone/iPad. |
| FondFont | Install owned TTF/OTF/TTC files for apps supporting the iOS font library, including Pages and Keynote. |

These facts follow the existing product pages and press registry. No new capability, price, rating or availability claim was introduced. The main-page Shheep heading is now H2, matching the other seven product headings under the single H1.

## SEO

Title: `lazyapps — Apps for Mac, iPhone & iPad`. Description identifies functional categories and the browser game. HTML metadata, Open Graph/Twitter metadata and the WebSite structured-data description share the same copy. The social-image alt text describes the logo. Existing canonical, sitemap, product URLs and Organization identity are retained; no OG artwork was modified.

## Shared visual style

All Press Kit pages load the main site's `site.css` for the actual font files, system font stacks, paper background, grain, responsive container and design variables. Product colors now have a single `--app-*` source used by homepage and Press Kit cards. The hub uses colored cards, condensed app headings, 24% thumbnail corners, pill actions, desktop two-column / narrow single-column layout and the shared footer. Its single-column breakpoint matches the homepage at 720px. Product kits use the same heading family, pill buttons and rounded image containers. Hover/press feedback respects reduced motion.

Using the main stylesheet revealed that intrinsic image sizes could enlarge narrow-screen grids because its images do not shrink by default. Fixed the Press Kit image grid minimum width and allowed images to shrink within their containers. Bilingual button labels are grouped into nonbreaking spans, with a compact mobile size. Downloaded original images and ZIP contents are unchanged.

The source/style contract is documented in `docs/PRESSKIT.md`.

## Validation

- Final `npm run build` passed SEO, Shheep artifact and presskit checks: 71 pages, 70 canonical sitemap URLs, seven kits, 60 landing pages and 57 app-language folders.
- Main and Press Kit hub checked at 320, 375, 768 and 1280 pixels: no overflow or clipped description text; font stacks, background and container widths match. All seven product colors are byte-for-byte equal as computed CSS values (`browser-checks.json`). The 653px hub also uses a single column, matching the main-site breakpoint.
- Seven product kits checked at 320, 375 and 1280 pixels: no oversized image containers or buttons, all README download counts present, pill radius and shared footer present (`product-presskit-final-checks.json`). The earlier failing measurements are preserved separately as diagnosis evidence.
- KeyHop ZIP downloaded through the browser control; its bytes match the generated repository archive. Main-page browser logs contain no warnings or errors. Main-page loading overlay completes after its existing animation.
- Final desktop/mobile screenshots saved beside this note. Full-page screenshots show viewport-limited fixed-grain capture behavior, so viewport images are the preferred visual evidence.
- Temporary browser viewport override reset. `git diff --check` passed. No deployment or commit performed; unrelated work preserved.
