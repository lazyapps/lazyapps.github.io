# Yilo · 亦言

Canonical product root: `/yilo/` (Simplified Chinese). The existing eleven other
locale suffixes are unchanged. Press Kit: `/yilo/presskit/`; downloads:
`/presskit/yilo/`. Chinese standalone name: 亦言; prose: 《亦言》. Non-Chinese: Yilo.

## Product and release evidence

The November 6 sessions **更新亦言应用图标** and **支持多目标语言学习设置**, plus the
app working tree, establish the new identity and multilingual features.
`scripts/assets/yilo/product-source.json` records source hashes and the base
commit. The identity and multilingual changes are now committed at `db2ec57`;
the selected record was captured from the running app, then exported in all
12 native UI languages from source `473a8fa`. The website
does not read that project at build time.

Public copy presents Yilo and its multilingual learning features as current.
The only rename note is “Formerly YiYan” (Chinese: “原名《绎言》（YiYan）”).
Do not describe the product as upcoming, unreleased or a development preview.
The public distribution repository is `cxa/yilo`; the private source repository
is `cxa/yilo-src`. Private source links stay out of the product website and
media downloads. The tap uses the existing `yiyan` Cask token:

```sh
brew tap cxa/yilo https://github.com/cxa/yilo
brew install --cask cxa/yilo/yiyan
```

Feature copy is shared by the product pages and Press Kit in
`src/i18n/yilo-short-copy.json`; page labels and metadata are in
`src/i18n/yilo-locales.mjs`. This replaces the historic HTML extraction generator.
The twelve UI languages are independent of selectable learning languages.
Five capture integrations remain supported, including Antigravity, as confirmed
by `HostKind.agy` and the transcript observer. The source language initially
follows the system; targets initially contain English, or Simplified Chinese
for an English source. Multiple ordered targets have no selection cap;
refinement uses the first. Chinese reading aids default to Pinyin for Simplified Chinese and Zhuyin for
Traditional Chinese, with an Off option. Pinyin sits above words; Zhuyin sits
to the right of characters. Japanese reading aids are optional and off by
default. Hiragana appears above kanji; Romaji appears above Japanese word
groups. Both are shown in the current native captures. iCloud remains opt-in;
iPhone remains TestFlight.

## Brand and media

- Native icon: snapshot of the selected C Ruby Gold `AppIcon.icon`, exported by
  Apple's `ictool`, Default, macOS, 1024px, Design Generation 27. Hashes in
  `scripts/assets/native-icons/sources.json`.
- Flat SVG and transparent symbol: original contours, native positions and
  default fills. These do not reproduce native glass or lighting.
- Open Graph: `1200 × 630`; shared Chinese 亦言 and shared Latin Yilo images.
  Both keep all brand content within the center `630 × 630`. Full and square
  outputs reviewed under `docs/reviews/yilo-20261107/`.
- App imagery: 36 native component captures, three for each of the 12 app UI
  languages. Eleven learning cards use the exact user-selected real record
  beginning “功能有更新，需重新截图”: original Chinese input, English/Japanese
  translations and learning notes remain unchanged, with Romaji readings.
  The English version uses the explicitly requested variant: English input,
  Simplified Chinese/Japanese outputs, and English learning explanations.
  The updated English card shows native Pinyin above Simplified Chinese words
  and Romaji above Japanese words. Its settings enable both reading aids.
  Its settings and language picker likewise select English as the source and
  Simplified Chinese/Japanese as learning targets. Other settings show
  English/Japanese/French targets. All preferences are isolated samples. Each
  capture uses the app's actual localization resources and native components;
  Arabic uses right-to-left layout. No raster text replacement, UI recreation
  or image resizing. Receipts include native-language checks, selected-record
  hash, renderer hash and app source hashes. The initial English window crop
  is historical evidence, outside the active catalog.
- Previously published YiYan films and screenshot receipts are historical; active pages and
  media manifests do not use them. The original historical video URLs remain
  available for existing direct links.

Rebuild on macOS with Xcode, Python Pillow/fontTools, and `rsvg-convert`:

```sh
python3 scripts/export-native-app-icons.py --product yilo
python3 scripts/prepare-presskit-vectors.py
python3 scripts/prepare-yilo-brand-web.py
python3 scripts/render-yilo-opengraph.py
python3 scripts/prepare-presskits.py
npm run build
```

The native icon snapshot, generated source assets and media packages must be
committed together. Production builds need neither Xcode nor the private app.

Recapture all 36 localized native components with the current source and Xcode:

```sh
python3 scripts/capture-yilo-screenshots.py --app-source /path/to/yilo-src
python3 scripts/prepare-presskits.py
npm run build
```

The exporter snapshots the app source in a temporary Swift package, adds a
website-owned native capture executable, and builds an isolated app bundle
with the original language resources. It runs one process per UI language,
using process-local language arguments, and checks that native labels and the
resolved locale match the requested language. It does not change system or
user app preferences. Sample settings use a disposable directory; the real
learning record is read from the checked-in, user-selected record snapshot
(or the requested English example), not the user's database. The 2× PNGs keep their native pixels. Inspect exports
before regenerating the media packages. The build verifies per-language
images, dimensions, source receipts and ZIP contents. Historical English
media addresses continue to serve the current English capture.

## Legacy URLs and hosting limit

`src/content/yilo-routes.mjs` inventories all 13 legacy product pages. Astro
configuration declares status 301. Postbuild emits immediate HTML redirects
with new canonical URLs, `noindex`, and a browser redirect preserving both query
and fragment without adding a history entry. Without JavaScript the meta
refresh still reaches the matching new page. Browser parameter preservation
requires JavaScript; fragments normally survive meta refresh in browsers but
are not available to a server.

The user confirmed GitHub Pages is the managed deployment. **GitHub Pages
cannot emit custom HTTP 301 responses.** These files provide static redirects,
not HTTP 301. `_redirects` includes 301 rules for a future supporting host, but
GitHub Pages ignores that file. Actual HTTP 301 requires adding a configurable
CDN/redirect layer or changing hosting; it has not been enabled by this change.
Although response headers show Cloudflare in the request chain, no configurable
Cloudflare account or authorization to change such an account is assumed.

Postbuild copies current media to the old `/presskit/yiyan/` download addresses,
including the old ZIP, screenshot names, and Chinese social image paths, so old
shared links get current assets. New links always use `/yilo/` and
`/presskit/yilo/`. No duplicate old product page enters the sitemap.

`npm run build` runs the existing SEO/media checks and
`scripts/check-yilo-migration.mjs`, which verifies every old/new route, immediate
fallbacks, parameter/fragment handling, active links and compatibility downloads.
No deployment or app release is performed by these changes.

## Learning-first copy and hero film

Yilo is a language-learning companion. Public copy leads with learning from
one's own everyday input, understanding natural expressions through focused
explanations and examples, then reviewing and reusing them. Translation,
capture and refinement describe ways to learn. The same positioning applies
to the home card, all twelve product locales, SEO, Press Kit summaries and
READMEs, and the hero film. User-facing Chinese calls the selection “你想学的语言”
or “学习语言”; multiple selection is “同时学习多种语言”.

The current v21 downloadable film is fourteen seconds at 1280 × 608. Local MiniMax H3
animates the original pelican/bicycle anchor on clean paper. Its long bill,
throat pouch, fixed-length leg rig and webbed feet remain recognizable. No
reference illustration is copied. Model prompt, first/last anchor and receipt
are retained in `scripts/assets/yilo/marketing-v16/`. Cycle samples and loop
endpoints are reviewed in `docs/reviews/yilo-20261107/`.

The film uses a real native RecordCardView capture. All 12 UI languages are
exported from unmodified current AppKit/SwiftUI code with the app's extraLarge
text preference and a short sample input. The Chinese source is “先别大改，留点余地。”;
the natural English output is “Hold off on a sweeping rewrite; leave us some
wiggle room.” Japanese also retains its native Romaji. The English version
uses “No big rewrite yet; leave room to adjust.” as input and shows Simplified
Chinese with native Pinyin plus Japanese. Learning notes are collapsed to keep
the whole native card readable. Source PNGs are not reconstructed, retouched or
retyped; the video scales each complete image to fit, without cropping or paper
texture over the UI. The final scene shows two people reusing an expression.
Source phrases live in `src/i18n/yilo-examples.json`.

The separate 12 short native captures augment the existing 36 product-page
screenshots; the user's original selected record and English variant remain.
Capture with:

```sh
python3 scripts/capture-yilo-hero-screenshots.py --app-source /path/to/yilo-src
```

The fixture is `scripts/assets/yilo/capture/YiloHeroCapture.swift`. Each image
has an independent native locale, fixture, sample-record and app-source receipt
in `scripts/assets/yilo/hero-native-source.json` and the shared Press Kit
screenshot provenance. Copies under `video/yilo-hero/public/records/` must match
those original PNGs byte for byte. Press Kit distributes the complete originals.

The large playful title stays in HTML above the full-width film. Chinese keeps
“边蹬边学”; English reads “Pick up a language while you’re vibe coding.” Second lines are longer
where the title has two lines. The hero uses natural height and keeps the complete
film visible on the first screen when geometry allows. The movie has 32px more
headroom and 48px more bottom road than v15. The road fills the bottom edge;
there is no lower-left icon/name, large backdrop, dotted connector, internal
large title or explanatory caption. A small three-dot thought bubble supplies
gentle motion above the pelican. The page header retains the genuine brand.
The former software name appears only in page copy.

Music is “Fluffing a Duck” by Kevin MacLeod (122 BPM), under CC BY 4.0. The
14-second excerpt uses background loudness and brief fades; tempo is unchanged.
Source, licensing URL and hashes are in `scripts/assets/yilo/audio/source.json`.
Rebuild with `python3 scripts/prepare-yilo-hero-music.py`. Retain attribution
from `/v/yilo/music-credits.txt` when sharing. Previous film music credits stay
available at `/v/yilo/music-credits-v16.txt` and in old MP4 metadata.

`python3 scripts/render-yilo-line-hero.py` renders the 336-frame, 24fps H.264
limited-range BT.709 yuv420p movies with credited AAC 48kHz stereo. The active
version, native screenshot/music receipts, rendered outcome copy and all input
and output hashes are recorded in `scripts/assets/yilo/hero-video-source.json`.
Press Kit movie downloads use that source. Whole-site builds require
all 12 locales to finish the active version; old movie URLs are retained.
Production builds need neither H3, Remotion nor the private app source.

The web hero uses the native animation described below. Its outcome heading
sits above the introduction and downloads; the section is centered. Copy
stresses learning natural rewrites or translations, then using that phrasing
in conversations with people.

## Plain-language copy

The 12 locales use short sentences, one topic per paragraph and consistent
feature names, adapted from ASD-STE100. English descriptive sentences use at
most 25 words. Other languages follow natural local phrasing. Optional notes,
AI service calls, capture scope and platform conditions remain explicit.
Press Kit keeps the same paragraphs and shows its introduction once. The hero title is an explicit playful exception to the plain-language style.
Native record content is preserved. Validation summary: `docs/reviews/yilo-20261107/`.

## Illustrated detail section

The product page uses four open blocks: AI tools, storage/sync, typing/refinement,
and learning languages/readings. Each shows one short paragraph, with secondary
operational details in a native disclosure. AI-service processing and required
Accessibility permission stay visible. All 12 locales share this structure;
Press Kit descriptions retain the same brief and complete supporting facts.
`YiloDetailIllustration.astro` uses the hero's muted straight/cross hatching.
Each diagram animates once on entry after the page loader, then rests. Reduced
motion displays the final static state. Text can wrap naturally; no fixed copy
heights or line clamps. Language-picker contents have equal 10px horizontal
padding, a 44px target and a rounded keyboard-focus outline.


## Page illustration style and typography

The product pages and Yilo Press Kit retain the shared site navigation, paper,
buttons, footer landscape and company wordmark. The six feature groups are
compact, and the four explanatory diagrams use the hero's original colored
hatching. The human learning outcome stays visible as a centered heading above the concise
introduction and download buttons; its former two-person illustration is
removed. All six feature groups have original hatched diagrams for capture,
multiple languages, learning notes, refinement, saved records and iPhone sync.
The ten page diagrams share one viewport observer, play a brief motion once
and remain static with reduced motion. Actual app screenshots remain byte-identical.

Yilo uses locally hosted handwritten web fonts: upright Patrick Hand for Latin, Neucha for Cyrillic,
LXGW WenKai for Chinese/Japanese, Kalam for Devanagari, Nanum Pen Script for
Hangul and Aref Ruqaa for Arabic. The company wordmark and code remain in their
shared site faces; native screenshots retain real app typography. All are OFL
fonts from their official repositories. Web-only subsets are renamed, preserve
original outlines, and include copyright/license notices. Sources and hashes:
`scripts/assets/yilo/hand-font-sources.json`. Rebuild with the existing asset
venv's Python and `scripts/prepare-yilo-hand-fonts.py`. Complete notices are
served at `/v/yilo/fonts/credits.txt`. Production builds use the checked-in
WOFF2 files and do not fetch fonts. The checked copy has complete letter/mark
coverage across all 12 locales.

For an English HTML heading-only revision, `python3 scripts/render-yilo-line-hero.py --retitle-only` updates all movie title metadata and receipts without re-encoding picture or audio.

The v20 exports remove the two wheel support diagonals using the shared
road-row cleanup in `scripts/lib/yilo_wheel_supports.py`. The raw H3 output is
preserved. Normal renders and the v19 export upgrade use the same filter.
HTML headings above and below the video omit terminal sentence marks; the
example text inside the movie is unchanged.

v21 holds the complete ending composition for the final 1.5 seconds (frames
300–335), without fading the illustration or learning outcome to blank paper.
The shared `src/timing.json` drives a Remotion Freeze for all 12 languages.
The movie remains 14 seconds long; the existing audio fade is unchanged.

Below the download actions, feature copy, usage conditions and installation
content render visibly by default. They do not use the shared scroll-reveal
hiding/stagger machinery. The six illustrations retain their independent,
once-only motion and reduced-motion behavior.

The homepage and all 12 Yilo product pages share `YiloDemo.astro`, an SVG
animation driven by `yilo-demo/controller.ts`. The illustration uses a fixed-
length two-leg pedaling rig, localized input, each language's genuine native
record PNG, and a conversation scene. English uses English input and Chinese
with Pinyin plus Japanese with Romaji; other versions retain Chinese input and
English/Japanese output. Homepage presentation is compact; product-page titles
stay above the illustration and the complete hero fits the first viewport.

The animation runs only while visible, freezes its final composition, and
loops without an empty frame. There are no Pause or Replay buttons. Reduced
motion and no JavaScript provide a complete static learning view. Sound is
opt-in through a localized Sound button; `scripts/prepare-yilo-web-music.py`
prepares credited AAC audio from the existing processed soundtrack. It pauses
offscreen. The compact homepage displays attribution when audio is enabled;
product pages retain their existing music credits. `web-music-source.json`
records the input and output hashes. Build checks preserve native screenshot
bytes and matching locales, prohibit embedded hero movies and Pause/Replay,
and verify the web soundtrack. Downloadable films remain in the Press Kit.

The polished web composition slightly enlarges the pelican around its tire
contact point. Portrait product pages use a 760×820 composition: pelican and
input above a complete, larger native record. Landscape and compact homepage
cards retain the 1280×608 composition. Both frames add a 48-unit breathing
margin on every edge (856×948 portrait, 1376×704 landscape); the road still
fills the bottom. Sound sits inside the canvas at the bottom right, aligned
with the native learning card's right edge. The control uses a plain icon and
text, without a background, border or pill. Portrait road height includes clearance
below the complete native record. The available first-screen height
accounts for each localized title, including short
320×480 viewports; no native screenshot is cropped or stretched.

Input exits by 8 SVG units before the record enters over 440 ms. The settled
record remains readable until 9.25 seconds. Ending people, bubble, phrase and
outcome enter in semantic groups about 100 ms apart; a small listener nod and
free-hand gesture follow the phrase. The complete outcome is visible by
10.62 seconds, with all illustration motion held from 12.5 to 14 seconds.
The pedal clock stays continuous across narrative loops. Brief blinks,
thought dots, laptop lines and the typing caret supply restrained detail.

The Sound control keeps a 44px hit target, a 0.96 press scale and interruptible
icon crossfades. Compact music credit space is reserved to prevent a layout
jump. Reduced motion disables interactive transitions and keeps the complete
learning record. A stable text equivalent includes source, translations,
Pinyin and Romaji; the animated SVG is hidden from assistive technology so
loops do not repeatedly announce the lesson. Review evidence and responsive
checks: `docs/reviews/yilo-20261107/`.

## Repository hygiene

Keep current product assets, the v21 downloadable films, reproducible render inputs,
licenses and source receipts in Git. Unpublished v6–v20 films, obsolete generation
inputs, logs and iterative review captures are archived locally under `.build/`
and excluded from Git. The concise release review is `docs/reviews/yilo-20261107/`.
Previously published YiYan media remain available for existing links.
