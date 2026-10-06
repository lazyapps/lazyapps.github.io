# CHMate landing page media

`/chmate/` contains Simplified Chinese, with 14 other languages on lowercase
subroutes such as `/chmate/en/`, `/chmate/zh-hant/`, `/chmate/pt/` and `/chmate/pt-br/`.
The root selects the saved `chmate.locale`, then browser languages, then English.
Explicit language routes do not redirect. Switching languages preserves query and
hash. Portuguese uses `pt`; Brazilian Portuguese uses `pt-BR`.

The page uses the same logo reveal loader as KeyHop, with the CHMate wordmark.
Foreground playback waits for the shared loader's content handoff. Reduced motion
skips the loader and leaves the preview paused; without JavaScript, the loader is
hidden and the native video has manual controls. The shared scripts restore the
paper theme color after the reveal, with the same six-second fallback as KeyHop.

## Open Graph

All locales share `src/assets/img/chmate-opengraph-shared.png`, 1200 × 630.
CHMate's product name does not change between locales. The symbol and wordmark
fit inside the central 630 × 630 safe area, on the site's paper and grain.

Run `python3 scripts/render-chmate-opengraph.py` with Pillow, fontTools,
`rsvg-convert`, and Xcode's Icon Composer `ictool` installed. The script renders
the unchanged original `AppIcon.icon` archived in `scripts/assets/chmate/` with
the Default appearance and design generation 27. It removes the icon container
using the original vector layers and their recorded positions as an alpha mask;
the book keeps the renderer's original colors, lighting, and opaque interiors.
The wordmark uses the site's Sofia Sans Extra Condensed at weight 900.
A square proof is written to `/tmp/chmate-opengraph-square.png`.

## Independent layers

The page no longer embeds the rectangular App Store composition or fades its
edges. It combines three original layers:

- **Backdrop:** the original 14-second `assets/daylight-loop.mp4`, 320 × 576,
  projected into a 56-second sweep before export. Landscape (640 × 360) and
  portrait (320 × 576) versions keep the original light movement and include a
  complete out-and-back sweep. The page selects by viewport aspect ratio and
  displays one fixed video behind all content, exactly matching the viewport.
  There is no oversized video plane, CSS translation, or animation of its bounds.
  The diagonal light enters and leaves the viewport instead of staying in the
  top-right corner. A paper wash keeps it subtle;
  the main site's grain remains above the page. Secondary text is darker to maintain contrast.
- **Device:** at least 768 px, the original transparent iPad bezel PNG,
  2300 × 3000, with no extra card, border, or blurred edge. Narrow layouts show
  the native iPhone video without a device frame.
- **Screen:** localized native captures, exported without the baked background,
  titles, or closing card. Screen position follows the bezel's original geometry:
  iPhone `(72, 69, 1206, 2622)`; iPad `(118, 124, 2064, 2752)`. An alpha mask
  generated from the original grayscale screen mask clips only the actual screen
  opening. The bezel does not intercept pointer input.

There are 15 complete localized screen sets: en, zh-Hans, zh-Hant, es, pt-BR,
pt, fr, de, ja, ko, ar, it, id, nl and tr. Turkish now uses its own native captures.

## Export

Originals live outside this repository in:

`/Users/realazy/Projects/iOS/CHMate Neue/AppPreview/`

Native captures are in `raw/locales/{locale}/` and `raw/ipad/locales/{locale}/`.
The iPhone bezel and grayscale masks are in `assets/`; the iPad bezel is in the
sibling `AppStoreScreenshots/public/` directory.

Reproduce the exports with Python, Pillow and ffmpeg:

```sh
python3 scripts/export-chmate-media.py \
  --source-dir '/Users/realazy/Projects/iOS/CHMate Neue/AppPreview'
```

Use `--locales en tr` to refresh selected languages. The exporter reads originals
without modifying them, checks manifest hashes, and writes `public/v/chmate/`:

- `screen-{iphone|ipad}-{lowercase-locale}-v2.mp4` and `.jpg`
- `bezel-{iphone|ipad}-v2.png`
- `screen-mask-{iphone|ipad}-v2.png` (luminance converted to alpha)
- `daylight-{landscape|portrait}-v3.mp4` and `.jpg`

Use `--background-only` to regenerate just the daylight sweep. The earlier
`daylight-v2` source files remain available for comparison. The v3 export removes
a continuously transformed video layer. It did not resolve the reported Chrome
top-edge strip by itself. Native Chrome at 2398 CSS px wide and DPR 2 reproduced
the extra four bright rows while the fixed backdrop used `inset: -4px`.
Changing only that inset to `0` removed the four-row strip in the same window;
24 subsequent native frames passed the same brightness comparison. Keep the
video bounds at the viewport; negative overscan is implicated, while the exact
Chrome compositing mechanism remains unconfirmed. The browser's own thin
toolbar separator is outside page CSS. The user also confirmed that opening
the page in a fresh Chrome tab no longer shows the strip.

Screen exports retain the original native editing: intro 0–7 seconds, reading to
17 seconds (horizontal/vertical for CJK), 6.3 seconds of paper themes, then a
3-second hold. Total 26.3 seconds. Music, fades and volume adjustment are retained;
HTML supplies the headline and brand instead of baked video artwork. Posters
show the reading scene at 9 seconds. iPhone is 664 × 1444; iPad is 900 × 1200.
H.264 CRF 23, 30 fps, BT.709, AAC 96 kbps, fast-start MP4; roughly 2–3.7 MB each.

## Responsive playback

Below 768 px the page loads iPhone; at least 768 px it loads iPad. Crossing that
breakpoint updates the screen, poster, bezel visibility and physical mask while
retaining playback position and a deliberate pause. In the narrow stacked
layout, the native iPhone video fills the same content width as the copy at its
intrinsic aspect ratio. It has no bezel, rounded mask, or gutter offsets.
Desktop iPad geometry and its height limit stay unchanged.
Only the selected screen source loads; the bezel loads for iPad layouts only.
Root redirects avoid attaching
sources before navigation. Without JavaScript the localized iPad has manual
controls and the backdrop stays on its poster.

Background playback follows the foreground's actual playing, buffering and pause
state, including the exported sweep. Both pause when the hero leaves view or the document is hidden. Reduced
motion prevents automatic playback and backdrop downloads; the foreground can
still be played manually. Native controls remain inside the screen opening;
fullscreen shows the screen-only video without the bezel or clipping. Keyboard
focus is visible around the figure.

## Credits and App Store badges

Keep the public music credit: “Solace” by Scott Buckley,
[source](https://www.scottbuckley.com.au/library/solace/),
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), with the excerpt,
fades and volume adjustment noted.

The black App Store badges are Apple's unmodified localized SVGs from the
[marketing tools](https://toolbox.marketingtools.apple.com/). The download endpoint
is `/api/v2/badges/download-on-the-app-store/black/{badgeLocale}?releaseDate=1280620800`.
English uses `en-us`; Arabic uses `ar-ar`. Other filenames retain endpoint locales.
Badges render at 48 px high with intrinsic proportions and 12 px clear space.
When the hero copy column is narrower than 400 px, the same official SVG renders
at its original 40 px height with 10 px clear space. The adjacent notes use 13 px
type and a smaller gap. Localized notes are shortened to two non-wrapping lines:
free reading and a one-time purchase. Full purchase details remain below.
The CTA and Smart App Banner point to the free app, ID **335157929**.

## App Store campaign attribution

All localized download links reuse provider token **259198**, obtained from the
Campaign Link generated in App Store Connect. Each page uses campaign token
`lazyapps-{htmlLang}`, with the HTML language tag lowercased. For example, English
uses `https://apps.apple.com/app/apple-store/id335157929?pt=259198&ct=lazyapps-en&mt=8`;
Simplified Chinese uses `lazyapps-zh-hans`, Traditional Chinese `lazyapps-zh-hant`,
and Brazilian Portuguese `lazyapps-pt-br`.
The shared page component supplies the same page-specific parameters through the
Smart App Banner's `affiliate-data`. Attribution identifies the page language at
the time of download-link navigation, not the user's device language or territory.

Campaign metrics appear in Analytics → Acquisition → Campaigns after at least
24 hours and first-time downloads from five individual users for each campaign.
Each metric also requires a minimum of five within the selected date range.
Merely generating a link does not create a campaign row. Apple supports reusing
the provider token and changing only the campaign token; there is no need to
generate each localized link separately in App Store Connect.
See Apple's [Campaign links](https://developer.apple.com/help/app-store-connect-analytics/acquisition/campaign-links/).
Build output verifies the links and banner metadata; actual banner behavior and
download attribution require Safari on an Apple device and subsequent analytics.
