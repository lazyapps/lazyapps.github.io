# FondFont landing page

`/fondfont` negotiates the saved FondFont language, then browser languages, with
English fallback. Explicit `/fondfont/{en,zh-hans,zh-hant,ja,ko,fr,de}/` routes stay
in their selected language. Script tags take precedence over Chinese region
tags; TW/HK/MO map to Traditional Chinese when no script is given. Query strings
and fragments survive language changes. Without JavaScript, the root serves
English and all seven languages remain available as links.

The installation promise leads the page: owned fonts are installed into the iOS
font library, for use in compatible apps. Import, installation in Settings, and
use come before preview/comparison. The app cannot replace the iOS system,
keyboard, or Home Screen font. This distinction is stated in the FAQ.

## Product and media sources

The app repository is `../../iOS/iOSFontInstaller` relative to this repository.
Built-in languages are verified against its Xcode `knownRegions` and `.lproj`
folders. Feature claims follow `AppStore/Versions/260923.0/README.md` and the
actual app UI; names follow each locale’s `InfoPlist.strings`.

- Real six-second app clips: `AppStore/Preview/Remotion/public/footage`.
- Screenshots: `AppStore/Screenshots/public/screenshots/apple`.
- Archived native preview exports: `public/v/fondfont`; 900 px iPad and 540 px iPhone, silent
  H.264, 24 fps, fast start, about 12 seconds. Installation/batch selection is
  followed by the font library. No marketing soundtrack or generated UI. These
  earlier previews are preserved; they are not the current hero.
- Current static posters remain visible until playback begins. Reduced motion and
  data saving prevent autoplay; playback pauses offscreen and when the document
  is hidden. The current page has no play/pause button. Earlier manual controls
  belong to the archived preview design.
- Supporting screenshots crop the original iPad workspace above the long
  metadata list. No UI is redrawn. All seven locales use their own screenshots.
- `manifest.json` records clip source paths relative to AppStore, SHA-256, and
  export sizes.

Regenerate with:

```sh
python3 scripts/export-fondfont-media.py --source /path/to/iOSFontInstaller
python3 scripts/render-fondfont-opengraph.py
```

The image renderer needs Pillow, fontTools, `woff2_decompress`, `rsvg-convert`,
and Xcode’s Icon Composer. Original production `.icon` assets are preserved in
`scripts/assets/fondfont`. The exact front/back masks extract the symbol from a
native sRGB icon render. OG follows `OPEN_GRAPH.md`: 1200 × 630, central 630
square, paper/noise, deterministic names. English/French/German share one image;
Chinese, Japanese, and Korean use their real localized app names.

All download links and the Safari Smart App Banner use app ID `842109099`,
`pt=259198`, `ct=lazyapps-<html language>`, and `mt=8`. No app name in `ct`.

## Advisor decisions

Independent Astra/xhigh reviews were requested through the advisor skill. After
the user clarified the key pain point, the page was changed from inspection-first
to installation-first. The follow-up supported that change and flagged universal
availability wording. “Across iOS” / “随处开工” were removed from the hero. “Installed
in iOS” / “装进 iOS” describe the actual library installation; the adjacent text
explicitly limits use to compatible apps. Detailed limits stay in the FAQ.

Completion review found two issues, both fixed: the English metadata title now
says “Install your fonts in iOS”; OG regeneration no longer depends on an
ephemeral review directory. Reduced-motion/manual playback and no-JavaScript
root/locale-link behavior were also checked in the browser.

Final validation: production build passes; seven locales were checked at both
390 px and 320 px without horizontal overflow. All fourteen final silent videos
are 12 seconds. Desktop first-shot footage trims the preceding comparison
popover so installation/batch selection leads the showcase.

## Archived v4 concept: a font enters your work

This superseded direction replaced the rejected cotton specimen and large Settings
tutorial with a continuous, causal product scene. A clipped-corner font file
enters a conceptual device font library. The same named font becomes an
installed entry with a confirmation, then default document/presentation
content acquires an expressive custom serif. The installed entry remains the
shared source in the settled composition. The phone's system interface is not
the font-replacement target. This depicts installation into the iOS font library
and use in compatible apps; it does not promise replacement of iOS UI fonts.

Paired start/end product references were made with the built-in imagegen tool
and are saved as `scripts/assets/fondfont/animation/v4/{start,end}-reference.png`.
Technical 768 × 864 anchors accompany them. Final reference edit prompts are
`imagegen-start-prompt.txt` and `imagegen-end-prompt.txt`. Decorative tiny labels,
numbers and paper texture were removed from the reference. Playfair Display is
an illustrative owned font; its TTF and OFL are preserved beside the references.
The scene and typography are conceptual illustrations, not app/OS screenshots
or exact font-metric tests. Accessible descriptions in all seven languages
explicitly identify the conceptual animation. The lower installation section
still shows authentic localized FondFont installation-guide screenshots.

MiniMax H3 creates the file transfer, installation state and typography change,
conditioned on the two different anchors. The exact causal shot prompt is
`h3-prompt.txt`; commands, source hashes, seed and execution log remain beside
the raw movie. Generation uses all 50 transformer layers, all 20 fresh denoiser
evaluations and 512 × 576 internal resolution. The fixed camera and shared
object positions keep the transformation coherent. The font must become a
library entry before the content typography changes. The independent
Astra/xhigh approach review recommended precisely that relationship, rather
than an anonymous block docking as if it were hardware; this was adopted.

The web export `hero-h3-v4.mp4` is silent 768 × 864 H.264 at 24 fps with fast
start. It runs once for approximately 4.8 seconds and settles into the exact
final reference. There is no loop, replay control or play/pause button. It pauses
offscreen or when the document is hidden; completion does not restart it.
Reduced motion, data saving and JavaScript-disabled browsing use the final
static poster. Enabling reduced motion during playback restores that poster.
The old v1/v2/v3 takes remain preserved but are not used by the current page.

The page stays clean and nearly uniform: no grain, embossed typography, noisy
paper image or background-video download. A very weak broad white light moves
once for five seconds then settles. Reduced motion disables it. The movie field
is white-point normalized and merges with the page through multiply blending
and a narrow edge feather; there is no enclosing hero card.

Regenerate using preserved sources (scripts reject overwriting existing takes):

```sh
python3 scripts/generate-fondfont-motion-v4.py --engine /path/to/h3 --model /path/to/MiniMax-H3
python3 scripts/export-fondfont-motion-v4.py
```

FFmpeg retimes the H3 movement and blends into the exact final reference. No
system interface or recorded app action is fabricated as evidence. H3 jobs run
sequentially to bound GPU memory. The built-in image generation created the
references; MiniMax H3 supplies the motion.

## Shared footer and validation

All pages now render `SiteFooterBase` with the same `Contact · Privacy` navigation.
Both separators are visible: `© 2026 · Contact · Privacy`. The prior FondFont-only
privacy slot and styling are removed. The redundant independent-software
subline was removed from the common footer so its typography is uniform.
Product page language is passed explicitly; Chinese pages link to
`/privacy.zh.html`, all others to `/privacy.en.html`. Footer labels remain English,
as did Contact and the shared footer identity. The shared identity may shrink
and metadata may wrap on narrow screens.

The 52 built pages were checked for exactly one shared privacy link in the
correct language and the visible Contact/dot/Privacy ordering. A real 320 px
browser view confirms no clipping and no old playback button. The header still
matches CHMate and World Book's home dot, width/padding/root font scale and
globe; the longer Japanese name alone shrinks below 480 px to prevent collision.
Seven native FondFont languages and English fallback remain unchanged.

## Compact installation hierarchy

The page now has three sections: installation value in the hero, the complete
import/install/use workflow, and a compact FAQ. Formats and import sources are
part of the first step. Compatible app examples are part of the use step. The
workflow retains one authentic localized installation-guide screenshot. The
privacy statement is a plain paragraph; preview, glyph inspection and comparison
are three short supporting descriptions within that same section. Independent
format/app strips, the privacy card, three feature image cards, decorative section
headings and the closing slogan were removed. The header and shared footer keep
the other product pages' visual language. CHMate and World Book attribution
notices precede their shared footer, without page-specific footer alignment.

The Astra/xhigh layout consult supported consolidation and requested an explicit
compatibility boundary. Hero copy already names the iOS font library and compatible
apps in every language; use-step examples now explicitly require compatible apps.
The system-font limitation remains in the FAQ, avoiding a duplicate warning in
the hero while preserving a clear answer.

Final production build: 52 pages. All 52 shared footer navigations were checked
for Contact · Privacy ordering and the correct Chinese/English privacy URL.
All seven languages at 320 and 390 px had zero horizontal overflow, no clipped
text blocks and positive header gaps. Desktop screenshot shows the three-section
hierarchy. Browser confirms the 4.75-second H3 movie ends without a loop or
controls. Reduced-motion mode leaves the video source unloaded, uses the final
poster and disables ambient animation. The exported movie has one H.264 video
stream, no audio, 768 × 864 resolution and a 462,114-byte file size.

The final independent Astra/xhigh completion review found no material unresolved
mismatch or necessary corrections. The reviewer checked the compact hierarchy,
installation emphasis, one-pass H3 playback and the shared footer validation.

## Monospaced typography

FondFont loads Geist Mono Regular locally for format names and short mono
labels. Body copy retains the site's native sans stack. The mono family has
no extra tracking and stays at the body-copy size in the import step. This
stylesheet is imported only by FondFont. Source: vercel/geist-font commit
`10dc7658f13c38a474cde201bb09a4617267545b`; the original SIL Open Font License is stored beside
`src/assets/fonts/geist-mono-regular.woff2` as `geist-OFL.txt`.

## Archived and rejected v5: sculptural type assembly

The user rejected v4’s phone/document collage and asked to borrow World Book’s
cinematic presence and visible moving background. Its useful pattern is a decisive
H3 spatial assembly followed by actual native app footage, with one slowly moving
product-specific panorama behind the page. The rejected v4 assets stay archived.

This proposed opening gathered detached charcoal-and-copper serif strokes into a complete
Ag specimen. Built-in imagegen created a complete sculpture and edited it into the
matching exploded starting state, preserving the camera and materials. References
and exact prompts are stored under `scripts/assets/fondfont/animation/v5/`.
The user rejected this scene as an inappropriate copy of World Book’s mechanics.
It was never composed, exported into public v5 hero files, or integrated into the
page. Preserve the raw H3 generation and references as rejected process evidence.
Technical anchors fit the artwork into 768 × 864 without changing glyph proportions.
MiniMax H3 generates the actual assembly with all 50 transformer layers and 20 fresh
denoiser evaluations; playback retiming does not substitute for H3 motion.

The proposed native payoff was font selection followed by the actual localized installation
guide from `04-install.mp4`. All seven app languages use their own real capture.
The guide shows profile download and explains completion in Settings; these localized `04-install.mp4` clips do not
show OS completion confirmation. Separate genuine completion footage was found for v6. The native viewport stays
intact. The genuine selection view and loaded guide are selected as two shots;
the intervening sheet/loading transition is omitted. The film ends on the installation
guide rather than returning to a font browser. The independent approach review
flagged that ending on a library would weaken installation emphasis; this correction
was adopted. A focused followup accepted the honest guide payoff and required
precise wording distinguishing instructions from completed installation.

The temporary v5 background was a panorama of real licensed Playfair Display glyph outlines,
created by `scripts/prepare-fondfont-type-field.py`. It repeats seamlessly and moves
in one direction with a 75-second CSS transform. The actual repeat distance follows
viewport height through ResizeObserver. The field is quieter behind page text,
visible near the outer margins, continuously active while the page is visible, and
static in reduced-motion/data-saving modes. No grain or second video decoder.

The tightened layout keeps the shared header/footer width. Section rules start at
the content edge. Installation steps and supporting tools use identical three-column
tracks and gutters. The authentic installation screenshot is a collapsed disclosure
inside the install step. FAQ headings and questions share the hero’s left edge.
The duplicate closing App Store badge was removed. No fixed text heights or screenshot
space reservations. At 1280 px the default page height fell from 2208 to about 1450 px.
The prior completion review was superseded by direct user feedback.

Generate/export the preserved v5 source (existing movie paths are refused):

```sh
python3 scripts/generate-fondfont-motion-v5.py --engine /path/to/h3 --model /path/to/MiniMax-H3
python3 scripts/export-fondfont-motion-v5.py --source /path/to/iOSFontInstaller
python3 scripts/prepare-fondfont-type-field.py
```

All seven languages were checked at 1280, 768, 390 and 320 px. There was no
horizontal overflow or clipped text. Hero, workflow title, FAQ title and question
rows had identical left edges; every workflow/tool column had zero alignment
drift. The installation-guide disclosure opened its authentic screenshot and
closed successfully. The background transform advanced while the hero was
offscreen, confirming continuous page-wide motion rather than a short hero-only
light change.

## Archived and rejected v6: literal software handoff

The user subsequently rejected this implemented v6 direction as increasingly
absurd and asked for a creative, unforgettable idea. The native-installation
movie plus a small software-plane movement was too literal and visually empty.
It must not be treated as the accepted final creative. A neutral-white matte
correction (`v6a`) was exported but never integrated; changing that tint would
not address the rejected concept. Preserve the source and actual H3 result.

The user explicitly rejected copying World Book’s assembly mechanics. The v5
sculptural sequence was abandoned before composition or page integration.
A fresh independent Astra/xhigh advisor proposed a font-file → font-menu visual
handoff. This recommendation was followed because it explains the specific
installation benefit. The advisor’s proposed native Pages ending was unavailable;
a focused follow-up accepted an explicitly labelled conceptual editor after
real iOS installation completion. Both decisions are preserved in
`scripts/assets/fondfont/animation/v6/advisor-{direction,evidence}.md`.

A separate authentic September 19 capture supplies Bebas Neue’s file detail,
FondFont’s download instructions, Settings’ downloaded profile, Install Profile,
and Profile Installed. These are editorial excerpts from a documented continuous
take, not generated UI and not a one-tap installation claim. Immutable copies,
original paths and hashes live in `v6/native/` and `capture-provenance.json`.
The crop removes the cover display’s side status strip while retaining the app
and profile identity. The installation guide receives a slow vertical camera pan
to keep its instructions and Download Profile button legible.

MiniMax H3 generates the perspective handoff of one blank software work plane.
Repo-native tracking anchors contain no interface or letters. All 50 transformer
layers and 20 fresh denoiser evaluations are used, at 512 × 576 internal / 768 ×
864 output resolution. `generate-fondfont-motion-v6.py`, its exact prompt, full
log and generation metadata preserve the actual invocation. The plane’s corners
are tracked from H3 frames; authentic content and exact licensed glyphs are
projectively composited onto that motion. This is a spatial handoff of a font’s
identity, not a letter assembly, phone model or paper-poster collage.

The final font selector and incremental “MAKE IT YOURS.” input are an authored
**typesetting illustration**, not captured Pages or any other third-party app.
They use the actual Bebas Neue Regular font, whose family/full/PostScript names
were verified from its name table. The page’s localized illustration caption is
present before the conceptual interaction and throughout the ending. Keep that
caption whenever using this hero asset; it is essential context. Its alternative
text also distinguishes native installation excerpts from illustrative input.
The seven page languages remain supported; these particular authentic native
excerpts are in English. Localized full installation-guide disclosures remain
available in every page language.

The scrolling giant-glyph field has been replaced with sparse baseline guides,
sharing the hero’s typography workspace. `baselines-v6.svg` contains only six
horizontal guide lines and short margin ticks per 900 px repeat. One 80-second
vertical CSS transform runs continuously while visible, independently of hero
playback. The text area has reduced background contrast; there is no grain,
particle layer or extra video decoder. Reduced-motion and data-saving modes use
a static field and hero poster, with the illustration caption visible.

TTF, OTF, TTC and ZIP now have separate quiet outlined badges, using the scoped
Geist Mono font. The aligned compact layout, shared header and Contact · Privacy
footer remain in place.

Reproduce on macOS with Python/Pillow/NumPy, FFmpeg, and the local H3 engine/model:

```sh
python3 scripts/prepare-fondfont-workspace-v6.py
python3 scripts/generate-fondfont-motion-v6.py --engine /path/to/h3 --model /path/to/MiniMax-H3
python3 scripts/export-fondfont-motion-v6.py
npm run build
```

The generator and composer refuse to overwrite existing movie exports. Source
anchors, storyboard, tracked corners, licensed font, native excerpts and manifest
are preserved under `scripts/assets/fondfont/animation/v6/`.

## v7: A font drawer docks into the iOS system library

The user rejected v6's literal software handoff and asked for a memorable,
original idea that clearly emphasizes installation for the whole iOS system.
A fresh read-only Astra/xhigh consultation proposed a precision font drawer
joining a shared library. Its decisive direction is preserved in
`scripts/assets/fondfont/animation/v7/advisor-direction.md`.

The white receiving surface is explicitly labelled **iOS**. A closed charcoal
drawer carries `PlayfairDisplay.ttf`; the resource docks into that surface and
its cover retracts to reveal the organized character inventory. MiniMax H3
supplies the central motion, rather than a decorative transition between UI
captures. The camera stays fixed. The installed state remains after playback;
there is no repeating uninstall, reverse, or play/pause control.

This is conceptual editorial artwork, not native iOS UI or a faithful rendering
of an individual font's glyph coverage. The built-in image generator created
the paired reference artwork; exact prompts and selected outputs are saved in
the v7 source directory. The filename identifies an owned font resource, while
the inventory represents availability. The advisor's suggestion to composite
exact licensed glyphs was not adopted: the shot describes installation into a
system library, and does not advertise the generated inventory as an app or
font preview. Localized alternative text explicitly calls it a concept.

All seven languages put system installation in the hero headline and explain
one installation shared by compatible apps on that device. The copy names
Pages, Keynote, Word, and PowerPoint. It does not claim that fonts synchronize
automatically between devices or replace the iOS interface font. The actual
Settings installation steps remain available in the compact guide disclosure.

The continuous page background retains sparse moving baseline guides. This
keeps motion visible and relevant to a type workspace while avoiding the dense
glyph fields, grain, particles, and colored fog rejected earlier. It pauses
when the document is hidden, and is static for reduced-motion/data-saving
preferences. The hero video pauses offscreen and on document hiding.

The generation uses all 50 transformer layers and 20 fresh denoiser evaluations
at 512 × 576 internal / 768 × 864 output resolution, paired anchors, 65 requested
frames, seed 10062107. The command, prompt, model metadata, hashes, and full log
are recorded by `scripts/generate-fondfont-motion-v7.py`. The export script
adds short reference holds, slows the actual H3 motion, and applies a neutral
white matte so the artwork blends into the website's paper color.

Reproduce with the preserved anchors, local H3 engine/model, Python and FFmpeg:

```sh
python3 scripts/generate-fondfont-motion-v7.py --engine /path/to/h3 --model /path/to/MiniMax-H3
python3 scripts/export-fondfont-motion-v7.py
npm run build
```

Responsive inspection of all seven locales at 1280, 768, 390 and 320 px found no
horizontal overflow or clipped copy, and matching left edges for the hero,
workflow, FAQ heading and question list. Raw DOM measurements are preserved in
`scripts/assets/fondfont/animation/v7/qa-responsive.json`.

The actual H3 output contains 73 frames at 24 fps (3.05 s including its raw
audio stream). The final website export removes audio and contains 170 frames
at 30 fps, 768 × 864, 5.667 s, H.264, 1,147,049 bytes. `manifest.json` records
the final probe and source/output hashes. Raw and final contact sheets preserve
the inspected sequence: a rigid covered resource, retreating cover, organized
inventory revealed, and stable installed ending. Generated lettering is
illustrative and may vary slightly during motion; the fixed iOS mark and the
adjacent product statement carry the system-library meaning.

The final Astro build succeeded with 52 pages. Actual browser checks confirmed
muted autoplay, advancing playback time, no controls or loop, the installed
hold after `ended`, and continuing background movement. Reduced-motion mode
loaded only the installed poster with no movie source and no background
animation. With the installation guide opened and the hero fully offscreen,
the video paused before completion while the background continued. These
observations are saved in `v7/qa-playback.json`. The data-saving/document-hidden
branches were inspected in source; they are not represented as independently
emulated browser tests.

A final independent Astra/xhigh completion review accepted v7 without material
corrections after inspecting source, desktop/mobile captures, final motion
frames, responsive/playback records, H3 hashes and the published product
description. Its self-contained brief and result are preserved in
`v7/advisor-completion-brief.md` and `v7/advisor-completion.md`.
The verdict was followed because it agrees with the actual browser observations
and the compatible-app scope stated beside the animation. All 52 built pages
also passed the shared Contact · Privacy order and localized privacy-link check.

## v8 — complete library press, exact localized specimens, continuous glyph rain

The active page uses `hero-h3-v8-loop.mp4`; v7 and v8's original one-shot export
are retained as historical sources. The user's latest instructions supersede
v7's crop, generated lettering, rising baselines, and one-shot recommendation.

Paired complete object references were generated with the built-in image tool.
MiniMax H3 supplies the actual closure: all 50 layers, 20 fresh evaluations,
512 × 448 internal / 768 × 672 output, seed 10062108. Logs, command, model
metadata and source hashes are preserved in `scripts/assets/fondfont/animation/v8`.
The silhouette and ground shadow remain complete; anchors only trim empty studio
margins, and the website uses no perimeter mask. This is conceptual editorial
artwork depicting an iOS system library, not an actual device or native interface.

The 8.2-second loop closes, holds, and lifts the upper housing to its poised
position. Only the pre-contact physical motion is reversed; the later seam pulse
is not reversed. Exact specimens stay on the fixed front window. An 18-frame
poised hold joins matching source frames; compressed first/last frames differ
by mean absolute RGB value 0.456 out of 255. The export contains 246 frames at
30 fps, no audio, H.264, 487,045 bytes. `loop-manifest.json` records the probe,
source and final hashes; `loop-contact.jpg` records the inspected progression.
The poster remains the closed state for reduced-motion/data-saving preferences.

Hero and background paths are extracted from the same actual pinned font file,
verified using its name/style/version tables, cmap entries and path hashes:

| Language | File | Specimens |
| --- | --- | --- |
| Simplified Chinese | SourceHanSerifSC-Regular.otf | 永字体 |
| Traditional Chinese | SourceHanSerifTC-Regular.otf | 永字體 |
| Japanese | SourceHanSerif-Regular.otf | あ永カ |
| Korean | SourceHanSerifK-Regular.otf | 한글봄 |
| English | LibreBaskerville[wght].ttf, weight 400 | Ag& |
| French | EBGaramond[wght].ttf, weight 400 | éœç |
| German | DINish-Regular.otf | Äöß |

Regional CJK forms use [Adobe Source Han Serif](https://github.com/adobe-fonts/source-han-serif),
with Chinese Song, Japanese Mincho and Korean Myeongjo styles. Latin sources are
[Libre Baskerville](https://github.com/google/fonts/tree/main/ofl/librebaskerville),
[EB Garamond](https://github.com/google/fonts/tree/main/ofl/ebgaramond), and
[DINish](https://github.com/playbeing/dinish); DINish is a DIN-style adaptation,
not a claim of official DIN standard conformance. Full fonts and OFL licenses
are archived in v8/fonts, not loaded as large website font files.
`font-manifest.json` records the pinned commits, hashes, names and coverage.
`prepare-fondfont-specimens.py` reproduces the SVG paths without fallback fonts
or generated lettering. The actual filename is visible beside the specimen.

The user's final background direction is a quiet glyph rainfall. All former
contour fields and connecting lines were removed. Fourteen desktop / eight mobile
slots repeat the three authentic localized glyphs, predominantly in the outer
thirds of the viewport. Warm ink at .08–.125 opacity, 30–42-second linear falls,
under 24px sideways drift and under 6° rotation keep the movement restrained.
There is no softness, fog or grain. Negative phases populate the first paint;
boundary fades hide the reset. Local masks protect the hero copy and the object/installed specimen. Background
motion is independent of the hero; it pauses on document hiding/data saving,
and becomes static for reduced motion. The hero pauses when fully offscreen.
No play/pause control is added.

Two non-wrapping headline spans use locale-appropriate container-relative sizes.
Their line height explicitly inherits from the heading to avoid the site's
body span style adding excess space. English uses a smaller bound for its long
second line. Seven locales at 1280, 768, 390 and 320px are recorded in
`qa-rain-responsive.json`; the final browser playback/reduced-motion observations
are recorded separately in `qa-rain-playback.json`.

The read-only Astra/xhigh direction consults are preserved as `advisor-direction.md`,
`advisor-loop.md` and `advisor-rain.md`. The explicit user loop requirement takes
precedence over the earlier one-shot direction. The rain review's larger,
recognizable contours and local reading mask were adopted to avoid an
invisible effect from compounded attenuation.

Reproduce:

```sh
python3 scripts/prepare-fondfont-specimens.py
python3 scripts/generate-fondfont-motion-v8.py --engine /path/to/h3 --model /path/to/MiniMax-H3
python3 scripts/export-fondfont-motion-v8.py
python3 scripts/export-fondfont-motion-v8-loop.py
npm run build
```

The exporters preserve existing outputs and require a new version to regenerate.

Final visual polish also excludes falling glyphs from the object silhouette area,
so the iOS mark and installed specimen remain unobstructed. This is a local
object mask, not broad attenuation of the page background.

Final independent Astra/xhigh review accepted v8 without material corrections.
It inspected the current desktop/mobile screenshots and motion contact sheet,
checked media/source hashes, independently regenerated all 21 glyph paths with
zero mismatches, and checked the 28 saved responsive records. Its result is
preserved as `v8/advisor-completion.md`. The review was adopted because these
checks agree with the live browser observations and the compatible-app wording.
Cross-browser subjective quality and saveData/document-hidden emulation are not
claimed; the latter branches were inspected in source.

## Later direction experiments (v9 / v10)

The user subsequently rejected the v8 visual and the v9 shared-library diagram,
selected the proposed SVG-led third direction, and requested meaningful poetry.
The current experimental page uses `FondFontTypeScene.astro` and
`fondfont-poems.json`: seven localized poetic specimens, each in three verified
real fonts. `prepare-fondfont-poems.py` uses HarfBuzz kerning/ligatures and actual
font outlines; provenance and shaped glyph IDs are in v10/poem-manifest.json.
All 28 saved v10 responsive checks preserve two heading lines without horizontal
overflow. The 9-second SVG loop is authored motion, not H3 output.

The actual full-model H3 blank-document generation and exported movie exist in
v9, but are not used in this third-direction SVG experiment. Previous assets and
consults are preserved. Do not attribute the current animated typography to H3.

The user then rejected v10's explanatory tone and requested case research.
`v10/reference-study.md` records primary examples, browser observations,
playback limits and a proposed playful glyph choreography. This is research for
the next design decision, not a claim that the current hero was accepted.

## v11 two comparison films

The user requested one video each based on the Plastique and F37 case studies,
then specifically asked for a more distinctive font than system typography.
Current comparison exports are `concept-playground-brush-v11.mp4` and
`concept-poetry-brush-v11.mp4`. Both use actual MaShanZheng-Regular.ttf outlines
for 王维「明月松间照」 and both compatible-app examples. Formats and filenames
match the TTF source. Original serif drafts are preserved but are not in the
comparison player. Neither study replaces the current production hero.

Real MiniMax-H3 generated the ball/rail and moon/pine motion with all 50 layers,
20 denoise passes and reuse1; exact font actors/labels are composited separately.
Both exports are 12 seconds, 1152×720, 30fps, silent, with a whole-scene loop reset.
The shared font-library status and simultaneous Pages/Keynote use remain visible
at the ending. They are conceptual compositions, not native app screen recordings.
The comparison is at `/v/fondfont/compare-v11.html`.

Source images, imagegen/H3 prompts, commands, logs, source/output hashes,
font coverage, actual H3 motion sheets and video checks are archived under v11.
See `scripts/assets/fondfont/animation/v11/README.md` for prompt links and commands.

## v12 — theatrical continuation studies

The user accepted both v11 openings and rejected their status/card ending as an
installation manual. Both comparison films keep the first 6.3 seconds and then
continue the glyph theatre: **抢戏的「照」** (a chase and oversized poem portrait)
and **倒影出走** (the moon's reflection escapes and becomes the foreground poem).
The proposal for a poem ring splitting into multiple layouts was rejected by a
fresh advisor consult as another functional diagram. No app cards or installation
steps remain. One line states iOS installation and compatible-app use.

- `public/v/fondfont/compare-v12.html`
- `public/v/fondfont/concept-playground-brush-v12.mp4`
- `public/v/fondfont/concept-poetry-brush-v12b.mp4`
- `scripts/compose-fondfont-comparison-v12.py`
- `scripts/assets/fondfont/animation/v12/README.md`

These 14-second 1152×720 loops reuse the genuine MiniMax-H3 physical openings;
new real MaShanZheng glyph choreography is native SVG compositing. No fresh H3
run is implied. All v11 deliverables remain available, and these studies do not
replace the production landing hero before a direction is chosen.

The poetry handoff was then strengthened after completion review: one whole
reflected glyph turns upright from its exact centre instead of crossfading in
a second copy. The initial v12 movie and source are preserved; v12b is the
selected comparison export.

## v14 — Type Foundry freight loop

User-selected new story replaces the abstract font playground: a miniature Type Foundry casts assorted multilingual metal type, gathers it onto a FondFont truck, transports and unloads into a larger iOS factory, then finishes with a localized marketing line. 18-second looping film, entire shapes visible, no player controls.

Actual full MiniMax-H3 v13 truck motion is reused as the physical plate; no claim that H3 made native glyphs or branding. Built-in imagegen designed five naturally painted localized truck names. User requested common truck fleet typography: bold upright industrial sans/block characters, solid ivory mask-and-spray paint on orange steel. The first serif paint proposal remains archived. Cargo is identical across all locales, using exact outlines from eight real fonts on differently sized/angled metal slugs. Only the carrier brand and end wording localize; unknown languages fall back to English.

Sources, exact imagegen prompts, H3 provenance, font contour manifest, independent advisor notes and validation: `scripts/assets/fondfont/animation/v14/`. Renderer: `scripts/compose-fondfont-factory-v14.py`. Movies/posters: `public/v/fondfont/concept-factory-{locale}-v14.mp4` and `factory-{locale}-v14.jpg`. Review: `/v/fondfont/factory-v14.html`. Integrated into FondFont hero with reduced-motion/static poster and offscreen pause; existing headline, header, footer, formats and installation details retained.

## v15 — Imagegen materials for supported handling and wheel rolling

User accepted v14 truck travel, then requested natural loading/unloading, natural type-slug cargo, imagegen materials and repaired wheel motion. Built-in imagegen generated genuine transparent rigid robot components, a physical twelve-piece metal-type pallet, a full circular commercial wheel, and a compact horizontal support assembly. Originals and exact prompts are in `scripts/assets/fondfont/animation/v15/`; previous v14 paint variants are reused unchanged.

Photographic blank metal faces receive the same exact 12 glyph contours from 8 real font families. Both loaders use fixed-length articulated links and independently level support pads. Cargo lands behind the actual bed wall, stops before support withdrawal, then remains the same rigid loaded pallet during accepted full MiniMax-H3 travel. Unloading recedes into the open bay onto a photographic support, then passes behind the actual foreground cab/jamb; visible cargo never dissolves. Rigid wheels rotate by observed horizontal displacement divided by radius, with circular geometry and ground contact preserved.

Renderer: `scripts/compose-fondfont-factory-v15.py`; technical atlas extraction/pivot calibration: `v15/prepare.py` and `sprite-layout.json`. All photo material creation uses built-in imagegen, not procedural replacement art. Native code only animates component transforms, exact glyph contours, occlusion and rolling over the genuine H3 physical plate. Seven localized movies/posters and English fallback retain existing header/footer, two-line headline and no visible controls. Verification/provenance and review notes are durable in v15.

## v16 — Actual H3 loading and unloading preview

User rejected v15 handling and explicitly required MiniMax H3 to guide motion. Actual H3 FL2VA generations now supply the loading and unloading actions, using the full original checkpoint, 50 layers, 20 steps and reuse=1. Prior imagegen hardware and cargo provide dimensionally consistent still anchors. No native cargo easing or per-frame robot IK is used in the handling clips. The first generated unloading shot left the receiver hidden and looked unsupported; a second H3 generation uses a visible receiver beside the cabin. The loading clip's idle receiver area uses a feathered static layout replacement for continuity, preserving H3 loading machinery/cargo pixels.

Accepted truck travel comes from the v14 physical plate; native overlays retain painted truck naming, destination labels, repaired circular wheels and wording. The 20-second Chinese film completes delivery, shows the empty return and uses a whole-scene dissolve for the next shipment. Movie: `public/v/fondfont/concept-factory-zh-hans-v16.mp4`; poster: `factory-zh-hans-v16.jpg`. 600 frames, 30fps, full decode passed, loop endpoint error 0.953/255. Exact H3 commands, prompts, generation logs, source/output hashes, discarded attempts, final contact sheets and actual-image advisor review are in `scripts/assets/fondfont/animation/v16/`.

This iteration is a finished-film preview, per the user's request to see the film first. The main landing remains on v14; no v16 site integration or additional localized v16 exports are claimed.

## Current hero — native Blender / Three.js transport loop

The historical film and gantry prototypes above are superseded. The editable native
scene is `scripts/assets/fondfont/blender-v2/factory.blend`, built by
`scripts/build-fondfont-blender.py`, `scripts/fondfont-model-details.py` and
`scripts/fondfont-stacker-model.py`. The Meshopt web model is
`public/v/fondfont/blender-v2/factory.glb` (6.39 MiB). Runtime:
`src/lib/fondfont/blender-scene.ts`, analytic 41.2-second motion in `motion.mjs`.

The industrial foundry has authentic sawtooth roofs, gridded windows, chimney
and a casting aisle. The warehouse has corrugated steel, a structural portal,
bumpers and organized pallet racks. Both use full unchanged imagegen artwork
mapped through one registered orthographic projection onto roof, facade,
portal floor and recessed interior surfaces. Chinese foundry signage is exact
“铸字工厂”; the foundry has no FondFont identity. Source images, prompt chains,
SHA-256 and superseded references are recorded in
`scripts/assets/fondfont/blender-v2/industrial-forklift-imagegen.json` and
`industrial-forklift-prompts.json`. No raster crop, repaint or cleanup is used.

The rejected overhead racks, conveyors and closed shipping boxes are removed.
Two native seated counterbalance forklifts have a substantial rear ballast,
larger front wheels, operator bay, seat, steering wheel, open overhead guard,
nested I-beam mast, hydraulic cylinder, carriage and paired long forks. The
construction reference was generated by imagegen, informed by official Crown
FC and Toyota counterbalance product material. It is not a flat forklift sprite.
Cargo is three stacked open oak type trays: 54 independent cast metal sorts,
raised glyph contours on visible faces, recessed tray bottoms and securing
straps. Type outlines come from licensed project fonts. Existing original
imagegen oak/enamel surfaces are reused without painting them.

Cargo is carried close to the floor before lifting outside the eave, placed on
the truck, transported, picked up at the destination, lowered outside its eave,
and driven inside. Forks lower 70 mm after contact before withdrawal, clearing
the bed and floor. The loading sideboard hinges open for fork access and returns
to its upright position during travel; both sides of the truck remain complete.
The warehouse shutter stays closed until truck arrival at 15.3 seconds, opens
before its forklift exits, and closes after delivery. Factory and warehouse doors
operate independently. Inventory replenishment occurs behind closed shutters.
The final approach includes a shallow curve outside the portal to reveal the
forklift chassis. Its front axle follows the path tangent; the pallet follows
its rigid 1.2 m overhang and the rear wheels steer through the curve. Departure,
withdrawal, lowering and entry are timed separately. The longer cycle gives
these actions room to read at the actual webpage scale.

The cab roof now uses `cab-appicon-flat-v2.svg`, composed from the exact
production `AppIcon.icon/Assets/Bodoni-ff-Back.svg` and `Bodoni-ff-Front.svg`
paths and transforms. The earlier imagegen interpretation is superseded.
Opaque red/white flat paint replaces the glass materials, while the original
full canvas, letter proportions and unified front crossbar remain unchanged.
App naming appears only on the horizontal bed and near name rail. The integrated
phone roof uses imagegen's blank glass, then live classic glyphs: English Ag Qq &
(EB Garamond), Simplified Chinese 永 字 爱 (Source Han Serif SC), Traditional Chinese
永 龍 字 (Source Han Serif TC), Japanese あ ア 永 (Source Han Serif), Korean 한 글 봄 (Source Han
Serif K), French Ag Œœ é (EB Garamond), German Ag ß Ää (Libre Baskerville). Fonts are
licensed project originals, subset with `scripts/prepare-fondfont-roof-fonts.py`.

Only the empty return has restrained corner drift (maximum 0.13 radians),
steering correction and short-lived imagegen dust sprites. Dust is excluded
from ambient-occlusion rendering so invisible sprite quads cannot produce
rectangular artifacts. The truck remains on the stadium road; wheel motion is
continuous through the loop. Garden includes grasses, leaves, clover, daisies and
pink flowers. There is no land slab; a transparent shadow receiver blends with
the webpage background.

The fixed camera has zero yaw and centers projected architecture bounds.
Curb-inclusive road width matches the content container at every viewport. Plants grow
beyond it and narrow viewports clip through webpage overflow. All seven static
posters are whole native canvas exports at transport time 13.1 seconds, not mobile crops. Minimum mobile scene
height is 180 px; mobile retains the entire road loop instead of enlarging it
to a 700 px field and clipping both turns. Reduced motion/data saving retain the localized poster. Sign
font subsets cover every translated label.

Physical checks: `node scripts/check-fondfont-three.mjs` samples supports,
mast/eave/portal clearance, fork withdrawal, closed-shutter tine clearance,
closed-sideboard clearance, arrival-triggered doors, six-wheel road contact
including drift, hidden replenishment, whole forklift body/jamb clearance,
front-axle rolling direction and two-cycle continuity. TypeScript
checks and the Astro production build verify integration.

Reference sources: [Crown FC](https://www.crown.com/en-us/forklifts/electric-counterbalance-forklifts/fc-sit-down-counterbalanced-truck.html),
[Toyota counterbalance specifications](https://www.toyotaforklift.com/content/dam/tmh/marketing/es/pdf/product-spec-brochures/2021_Counter-Balanced%20Stacker_Comprehensive_Digital.pdf),
[Toyota Center Rider demonstration](https://www.toyotaforklift.com/resource-library/video-library/toyota-center-rider-stacker).


## Current installation guide — localized, genuine app screenshots

`FondFontInstallGuide.astro` replaces the old overview cards with four manually
selected steps: choose fonts, download the profile, open Settings, review and
install. The top tab row supports arrow keys, Home and End. Horizontal overflow
uses native scroll snapping. There is no autoplay or bottom step navigation.
Inactive panels are inert and hidden from accessibility; without JavaScript all
four panels remain readable in order. Visible mobile tab labels also supply the
accessible names.

In the side-by-side layout, screenshot right edges share the tab row border's
right edge. The active underline spans the complete tab and lies on that border.
Step numbers stay inside each tab's padding. Screenshots are 280 px wide on
desktop and 240 px on tablets; explicit grid columns keep the gap to the copy
at 48 px / 32 px. Caption text is right-aligned to the corner's starting point,
inset by the screenshot radius (36 px / 31 px). In the stacked layout, both the
210 px screenshot and its caption are centered in the card, with centered caption
text. Seven locales at 320, 390, 768 and 1280 px passed DOM checks for these
relationships and page overflow. Production screenshots in the review directory
show the result.

The genuine iPhone 17 / iOS 27.0 captures use the latest local app source built
on 2026-10-07, commit `182d46a`, version 260923.0. No app code was changed. A
dedicated capture simulator contains nine open-source font families per locale;
three static families are selected for a readable profile. Most fonts use SIL
OFL 1.1; Japanese Kosugi Maru uses Apache 2.0. M PLUS Rounded 1c's Google Fonts
metadata records OFL. Exact sources, license evidence and SHA-256 are retained
in `scripts/assets/fondfont/install-capture-20261007/`.

All four displayed states per locale are unchanged, full-resolution Argent
PNGs, 1206 × 2622. The system status bar is set before capture to 9:41, full
network and 100% battery; iOS displays the clock as 09:41. No raster clock patch,
crop, resize, generated UI or retouch is used. Captures stop before final profile
installation. `scripts/capture-fondfont-install.py` documents the process. The
site copies are recorded in `scripts/assets/fondfont/install-screenshots.json`.

Procedure copy applies ASD-STE100 Issue 9 section 5 principles: imperative
actions, one instruction per sentence, short sentences, conditions before
actions and informational notes kept separate. Other languages follow those
clarity principles in natural local wording; this is not formal STE dictionary
certification. UI names match the actual current app, including literal Edit
and abbreviated Inst. in French/German. German iOS permission reads Zulassen.
The guide separates downloading from installation in Settings and explains the
8-minute pending-profile expiry near that handoff. Compatible-app qualification
remains beside the installation guide.

Independent final advisor review found a mobile visible-label/accessibility-name
mismatch; the overriding aria-label and aria-hidden were removed. It found no
other must-fix issue in the supplied hero and installation proofs. Subsequent
user-directed alignment and bottom-navigation removals were checked directly.
Native touch injection is unavailable in the in-app browser; keyboard navigation,
tab clicks, scroll position, responsive geometry, reduced motion and no-JS
reading were checked.

Primary references: [Apple profile installation](https://support.apple.com/en-ie/102400),
[Apple screenshot dimensions](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications),
[ASD-STE100 Issue 9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf).
The clock presentation is the user's requested convention, not a claim that
Apple mandates 9:41 for every submission.


### Forklift silhouette correction — 2026-10-07

Supersedes the earlier forklift rendering and review recording. The user found
that bright fork/mast strips looked like descending lightsabers. The new imagegen
four-view construction reference is retained unchanged at
`scripts/assets/fondfont/blender-v2/sit-down-forklift-reference-v2.png`; exact
built-in generation prompt, original path and SHA-256 are in
`docs/reviews/fondfont-forklift-20261007/imagegen-reference.json`.
No raster extraction, recoloring or scene cropping was performed.

Native Blender changes: dark matte graphite mast channels, forged graphite
L-shaped forks, thicker connected carriage and load backrest, guide rollers.
The tips end at local z=2.10 m, inside the pallet front z=2.16 m, rather than
protruding to2.42 m. Existing imagegen body enamel maps are reused intact.
Truck sideboard folds fully down by180 degrees instead of forming a shelf.

Animation: minimum transfer pallet height1.19 m over the1.07 m deck (12 cm
clearance, formerly61 cm). The31-degree source transfer pose lasts2 seconds;
warehouse withdrawal takes1.5 seconds through the corresponding curve. The
vehicle carries low on exit/home sections, raises only after clearing the eave,
and lowers only once the complete pallet has cleared the truck footprint.
The read-only advisor's suggestion of low turning adjacent to the truck was
adapted because that trajectory would intersect the deck. Every10 ms, the
checker now includes the oriented pallet's full footprint in addition to the
existing fork support, mast/body portal clearance and loop continuity checks.

Sources: `scripts/fondfont-stacker-model.py`, `scripts/build-fondfont-blender.py`,
`src/lib/fondfont/motion.mjs`, `src/lib/fondfont/blender-scene.ts`.
Visual evidence and consultations are in
`docs/reviews/fondfont-forklift-20261007/`.

### Native drift and natural planting — 2026-10-07

The stronger empty-return drift reaches19.5 degrees of body slip. A rear-axle
pivot keeps the vehicle connected to its road path, and the front wheels
countersteer. Low, fading puffs reuse the complete original imagegen dust map.
The road check includes every corner of all six tire contact patches against
the actual1.8m asphalt half-width, rather than checking wheel centers alone.

Three new botanical communities were drawn by the built-in imagegen tool:
white daisies/buttercups, pink cosmos/geranium, and blue flax/violet salvia.
Each full original PNG is retained unchanged; exact prompts, source paths,
project paths and SHA-256 hashes are in
`scripts/assets/fondfont/blender-v2/meadow-whole-imagegen.json`.
The former hand-assembled stem/leaf/petal geometry has been removed.
Native Blender uses full-image UVs, no extracted components or raster cropping.

Following the user's feedback about tidy placement and plants over a chimney,
planting now forms unequal, staggered communities with deliberate gaps along
the front and outer sides of the road. The central area behind the buildings
is left clear. The design follows the long, informal mixed drifts shown in
[RHS prairie planting](https://www.rhs.org.uk/garden-design/prairie-planting-creation-maintenance)
and the soft swathes around paths in
[Piet Oudolf: Open Field](https://www.hauserwirth.com/hauser-wirth-exhibitions/5109-piet-oudolf-open-field/).
The RHS garden photograph was inspected directly.

Each complete plant community is carried by a24x10 native Blender grid.
The vertex shader pins its root edge and bends its upper foliage with a slow
breeze, spatial phase differences, and finer flutter. Exported glTF UVs were
checked directly: bottom V=1, top V=0, matching the shader's(1-V)^2 root mask.
Six sparse leaves reuse the existing complete imagegen leaf, with a slightly
curved native mesh, varied periods/trajectories and fluttering rotations.
They fall independently of the truck's41.2-second loop and fade before respawn.
All textures retain their full image; native geometry and shaders provide motion.

The checker conservatively projects complete plant rectangles, including
maximum wind displacement, against both buildings' full visible bounds and
chimney. All are separated. A120-second leaf simulation verifies finite poses,
above-ground positions and invisible respawns. TypeScript and the physical
motion/clearance checks pass. Compressed GLB is7.91MiB. Final browser proofs,
continuous recording and advisor reviews are retained in
`docs/reviews/fondfont-drift-garden-20261007/`.

Final completion advisor found no material defect in the supplied composition,
root mask, drift or leaf lifecycle. Its remaining evidence request was addressed
by the43-second continuous browser recording and390x844 mobile screenshot.
All seven full-scene localized posters were refreshed to2560x854; the52-page
production build passed, and production browser rendering reported no errors
or warnings. See `verification.json` beside the final evidence.

### Native garden and Blender pet animation — current version, 2026-10-07

This version supersedes the perimeter planting/image-card implementation above.
All roadside planting is removed. Fourteen actual daisies/cosmos and basal
leaves form one denser, asymmetric native patch between the buildings.
`scripts/fondfont-botanical-model.py` builds closed curved petals, pollen,
connected swept stems, leaves and grass. Rooted wind displacement is at most
5.5 mm with a slow breeze. The complete original imagegen construction boards
remain unchanged; prompts and provenance are in
`scripts/assets/fondfont/blender-v2/native-botanical-imagegen.json` and
`garden-life-native-imagegen.json`. They are modeling references, never display
cards. No botanical, animal or butterfly materials contain raster textures.

The full editable scene is `scripts/assets/fondfont/blender-v2/factory.blend`.
Chimney smoke is a soft, denser 3D noise volume with the same prevailing +X
wind as falling leaves. The canvas extends up to the header without moving or
rescaling the road. Leaves therefore begin above the app logo. A soft masked
backdrop blur follows the plume across the header and resets on scene disposal.

For the user's walking/turning feedback, pets now use real skinned armatures
built in Blender, replacing the earlier rigid-joint runtime animation.
`scripts/build-fondfont-pet-rig.py` produces the editable
`scripts/assets/fondfont/blender-v2/garden-life-rig.blend` and raw glTF.
The compressed runtime `public/v/fondfont/blender-v2/garden-life-rig.glb` has
2 skins, 40 bones and 22 NLA animation clips: forward/back walk, left/right
sidestep, left/right quarter-turn, idle, play, sniff and left/right urination
for each species. The dog lifts a hind leg; the cat crouches at the inner
front corners of either building, then resumes roaming. Native
clips bake planted-paw digitigrade IK, alternating foot support, small body weight
shifts and head anticipation. Walking stance lasts 68% of the cycle; each
quarter-turn has 12 small alternating paw placements. The animal surfaces are
native geometry and materials based on the unchanged imagegen reference.

`src/lib/fondfont/pet-animation.ts` removes native root-motion tracks, samples
walks from actual traveled distance and their exported stride metadata, and
samples pivot clips from actual angular progress. Navigation controls the
root, while Blender controls the articulated body. Idle/walk/turn poses blend over 180 ms with persistent turn phases.
No incremental body rotation overlays remain: sniffing is a native clip and
head gaze restores its animated quaternion before each overlay, preventing
Three mixer pose caching from accumulating rotations and flipping the body.
The native animation file is about 1.01 MiB; combined scene/model payload is
about 7.88 MiB, before localized fonts and the existing image maps.

The larger territory includes both front clearings and the passage behind the
flowers. `garden-life.mjs` uses seeded fixed-step behavior rather than a short
repeating path: sniffing, observing, roaming, following and occasional play.
Front destinations and rear waypoints vary within clear space, and either
direction around the flower patch is chosen randomly. Urination visits are
occasional and choose between both building corners. Velocity ramps smoothly
through direction changes; waiting pets clear corridor exits instead of
blocking them, and yielding searches feasible directions before moving.
Live instances have a fresh seed; frozen posters use seed 47. Whole oriented
capsules avoid buildings, the flower patch, loading bays, asphalt and each
other. Narrow rear circulation is reserved, and front turning/exit maneuvers
have right-of-way and safe side/back recovery. The approach draws on the
[Nintendo nintendogs + cats developer interview](https://www.nintendo.com/en-gb/Iwata-Asks/Iwata-Asks-Nintendo-3DS/Vol-4-nintendogs-cats/2-Adding-Kittens-Doubled-the-Work/2-Adding-Kittens-Doubled-the-Work-204778.html):
dogs approach more readily; cats spend longer observing before approaching.

Verification now tests exported motion rather than mirrored animation formulas.
`node scripts/check-fondfont-pet-rig.mjs` checks actual glTF bone world positions:
maximum supporting-paw movement is 0.65 mm per sample and bone ground-height error
is 0.54 mm. Actual supporting skin surfaces have 0.26–0.74 mm ground clearance. Integrated native poses run at 60 Hz for 1500 simulated seconds:
body up-axis stays above 0.9928, paw displacement remains within a bound
scaled to speed/turn rate, and the maximum observed per-frame displacement
is 47.32 mm during fast walking. These are continuity checks, not proof of
perfect foot contact during every blended transition.
`node scripts/check-fondfont-three.mjs` checks four 600-second randomized runs,
whole-body collision clearance and independent progress of BOTH pets in every
45-second window. All four explore a 7.74–8.01 m front span and reach the rear.
Seven 2560×854 localized posters are refreshed. Current evidence is saved in
`docs/reviews/fondfont-drift-garden-20261007/` under `native-pets-roaming-potty-*`, `native-pets-*-potty.png` and
`native-pet-rig-posters.json`; older screenshots document superseded versions.

Completion-review resolutions: `native-pets-followup-advisor.md` reproduced
three action bugs. Potty destinations are now exempt from ordinary same-node
redirection, intentional stillness resets blockage, and play excludes potty
and alignment. Regression checks assert corner distance and complete 5.4 s
actions. Alignment that yields away returns to its corner; if a front path or
alignment fails to advance a waypoint for 10 s, it defers the visit and replans.
Turn priority persists through retreat, and the waiting actor holds position.
These changes also prevent a slow yielding livelock that distance-only progress
checks initially missed. The final four-seed navigation check runs 2400 s;
actual bone continuity/upright checks run 1500 s. Type checking and the Astro
production build pass. The final browser film is 27.8 s of continuous live
rendering; the factory/warehouse action screenshots use seed 47 at 65.9/188.9 s.

### Production logo fidelity — 2026-10-07

The original 256px Default iOS export from Icon Composer design generation 27
is preserved as `fondfont-icon.png`. After the user requested brighter web
contrast, the header and favicon use `fondfont-web-icon.png`, exported by
the same native renderer from identical masks with brighter front material. `scripts/export-fondfont-brand.py`
exports both PNGs and composes the flat roof SVG from production vector masks.
The local `scripts/assets/fondfont/AppIcon.icon` directory was checked byte
for byte against `../../iOS/iOSFontInstaller/iOSFontInstaller/AppIcon.icon`.
The flat variant changes fills only: opaque white front, production red and
plum gradients flattened in linear light and mapped from P3 to sRGB. Path
coordinates, original group matrices, layer order and 1024px canvas are
preserved exactly; no font reconstruction or imagegen redraw is involved.
Provenance and source SHA-256 are in `scripts/assets/fondfont/brand-source.json`.
Regenerate these placements with `python3 scripts/export-fondfont-brand.py`.
The old approximate hand-drawn SVG and generated roof mark are no longer used.

Web contrast follows the user's later clarification: front white alpha is
0.55–0.35, native translucency 0.12 and shadow opacity 0.16. Native specular
edges/reflections and every original contour remain intact; no bitmap edits
or shape strokes are added. The read-only advisor confirmed exact paths,
matrices and roof routing. Its request to use the untouched header export
reflects the earlier briefing; the user subsequently authorized web brightness
and edge-contrast adjustments, so the brighter native rendition is intentional.


### Anatomical legs, forklift steering and persistent leaf litter — 2026-10-07

Imagegen produced the unchanged anatomy and slow-walk construction board
`pet-leg-anatomy-reference-v2.png`; the exact prompt and source are retained
in `pet-leg-anatomy-imagegen.json`. Blender builds the actual continuous torso,
shoulder/thigh, tapered lower limb, wrist/hock, metatarsal, paw and toe surfaces.
Each pet has 20 bones. Neutral standing poses are baked into skin geometry and
armature rest matrices, then all 22 clips are retargeted to that rest pose.
This reduces the creases caused by bending the earlier straight-leg bind pose.
The runtime uses standard linear skinning; Blender's volume preservation is
used only when baking the neutral geometry. The enlarged native mesh study is
`pet-anatomy-native-study.png`; it is an actual Blender render, not a raster edit.

Forklift rear wheels now steer about world vertical before rolling about their
local axle (`YXZ`). The former `XYZ` order tilted the steering axis as the wheel
spun. `stacker-animation.ts` owns the same transforms used by runtime and the
regression checker. `node scripts/check-fondfont-stacker-rig.mjs` loads the real
exported Blender hierarchy and checks all eight wheels over two complete trips:
axles remain horizontal and wheels stay on the ground, within numerical noise.

`nature.mjs` now settles each falling leaf gently into its final flat pose.
`leaf-litter.mjs` adds a permanent record on touchdown, independently of the
truck's repeating loop. The unchanged imagegen leaf texture is displayed on
curved 3D meshes. Ground instances grow in capacity as needed and do not fade,
respawn or remove older leaves. Their height clears the actual asphalt, lane
paint and curb surfaces. Wheel paths are swept each 25 ms; nearby leaves receive
an outward impulse with a per-kick random side angle, speed and spin. They tumble,
decelerate and settle at their new position. All 291 checked landings move at
least 0.3 m; measured displacements span 0.353–1.492 m in varied directions.
Prevailing wind remains +X, consistent with chimney smoke. Remote leaves stay
still. `node scripts/check-fondfont-leaf-litter.mjs` runs 600 seconds: 119 retained
leaves, 291 wheel wakes, maximum absolute height 0.366 m. It also checks unique
arrival IDs, monotonic retention, remote stillness, cadence independence and
backward replay. No new raster asset was drawn or processed for the effect.


Final evidence: `random-leaf-wake-final.png` shows the final wheel wake.
`anatomy-leaf-wake-final.png` and `anatomy-litter-mobile-final.png` show the
same scene before the last random landing adjustment; `anatomy-litter-final.mp4`
records the full scene before the final random kick adjustment. The later
`random-leaf-wake-final.mp4` records the final random displacement at 26–42.6 s
using the actual browser animation, not offline interpolation. The DEV-only
`sceneStart` parameter starts a seeded continuous preview at a chosen time;
production ignores it. The completion advisor (`anatomy-litter-completion-advisor.md`)
found no material defect and reproduced the updated 291-wake result. Its metric
correction is incorporated above. Frame samples and contact tests provide
limited evidence of appearance, not a guarantee of ideal animation at every blend.


### Forklift perspective/pose follow-up and symbol-only cab paint — 2026-10-07

The user correctly rejected the earlier wheel-only fix as a solution to the
whole forklift's visual perspective. The focused visual advisor found no
separate camera or model-axis error, but a repeatable 28–31° skew during loaded
transfers, aggravated by chassis occlusion. The path and timing are rebuilt:
small <=8.53° alignment turns occur with the pallet low; loading, pickup and
raised withdrawal stay square to the truck. Unloading reverses fully clear,
lowers first, then turns home. The front axle still follows its heading, rather
than clamping yaw on the old sideways path. The empty source forklift pauses
outside until the truck passes, making its ground connection readable, then
returns and closes before the warehouse opens.

The native model is refined from the existing unchanged imagegen four-view
reference. The old 1.24m full-width chassis hid most tire sidewalls. The new
1.04m chassis, narrower side pods, real curved wheel arches and 1.20m wheel
track expose them. Fork spacing is reduced from1.04m to0.68m. Solid telescopic
fork sleeves and native sliding tips retract to1.05m exposed length when
empty and extend by0.35m before carrying or transferring loads. No forklift
sprite, pre-cropped scene or manually edited bitmap is used.

`scripts/build-fondfont-forklift-rig.py` builds the standalone editable
`forklift-rig-v3.blend`, then integrates it into the versioned complete
`factory-forklift-v3.blend`. The runtime loads only the complete
`public/v/fondfont/blender-v2/factory-forklift-v3.glb`, avoiding duplicate model
or texture downloads. The old complete model is retained as an earlier version.
The actual hierarchy checker now loads the active complete model, verifies
native extension transforms and all eight wheel contacts; physical motion
checks cover the wider exposed tires, portal clearance, low-only turns,
straight high transfers and fully extended loaded forks.

Cab roof now uses `cab-symbol-paint-v3.svg`: exact original AppIcon vector paths
and transforms, flat warm-white paint only, transparent outside the symbol.
There is no background rectangle or icon tile. The full original vector canvas
is preserved; the artwork is neither cropped nor redrawn. Native truck lighting
still shades the paint. Header icon remains the previously authorized native
web-contrast rendition. `brand-source.json` records the separate cab treatment.

Review and actual browser evidence are in
`docs/reviews/fondfont-forklift-perspective-20261007/`.


Completion evidence: `after-empty-forklift-and-symbol.png`,
`after-approach.png`, `after-unload.png`, and `after-mobile.png` are actual
browser screenshots of the final complete native model. The 27.84-second
`final-forklift-and-symbol.mp4` records466 browser frames from loading through
warehouse delivery. All7full-scene localized posters were refreshed at2560×854.
TypeScript, native hierarchy/contact/reach checks, physical movement and
2400-second pet navigation checks passed. The52-page production build passed.
The completion advisor found no presentation-blocking defect; its requested
claim boundary is followed: this removes skewed high transfers and improves
vehicle readability, without claiming mathematically perfect painted-art
perspective or complete chassis visibility in every loaded frame.


### Forklift grounding and consistent campus sunlight — 2026-10-07

The user rejected the v3 visual as airborne despite the previous pivot/radius
checks. Those checks did not establish rendered ground contact. The focused
advisor measured actual published tire vertices and identified the weak
contact-shadow rendering as the primary lead. Its recommendation to fix the
runtime renderer was followed. Blender refinement is supplementary, not the
explanation for fixing a renderer defect.

- Built-in imagegen supplied an unchanged front/side grounding reference:
  `scripts/assets/fondfont/blender-v2/forklift-grounding-reference-v4.png`.
  Full prompt, inputs, original path and SHA-256 are recorded in
  `docs/reviews/fondfont-forklift-grounding-20261007/imagegen-reference.json`.
- Editable `forklift-rig-v4.blend` and complete `factory-forklift-v4.blend`
  retain the original complete imagegen material images. Native tire profiles
  now have continuous shoulder rings, recessed chevron tread and hub lugs.
  Front/rear radii are 0.30/0.24m. The main chassis stops behind the front
  tires; a narrow differential housing exposes their front silhouettes.
- Runtime uses the compressed complete `factory-forklift-v4.glb` (6.97MiB).
  A single directional source anchored to the measured DOM navigation sun casts all
  building, truck, forklift, botanical and pet shadows. Opposing directional
  fill and local warehouse/foundry point lights were removed. Broad room
  environment plus non-directional hemisphere supply soft ambient fill.
- PCF shadows replace the radius-20 VSM wash. Map size is 2048 desktop/1024
  narrow screens, radius 3, normal bias 1mm. The transparent shadow catcher
  is at y=1mm, above the painted interior floor at y=0, with opacity 0.34.
  Both buildings' existing alpha-tested depth proxies cast into this same
  receiver. No independently painted drop shadow or floor bitmap was added.
  Building art remains the original imagegen projection, not a claim of fully
  sculpted architectural geometry or perfectly relit source pixels.
- Source reverse lasts 2.6s instead of 1.2s; warehouse exit lasts 2.4s instead
  of 0.7s. Warehouse approach/withdrawal/return have deliberate travel timing.
  The complete cycle is 47.9s. Empty source reversal follows a shallow S path
  (under 14 degrees), exposing the tire sidewall briefly. Raised load transfer
  stays square. Each wheel accumulates signed travel at its own axle, including
  rear-steering arcs; independent fork lift cannot spin a stationary wheel.
- `check-fondfont-stacker-rig.mjs` now decodes actual meshopt tire vertices
  and transforms them with the production animator across two trips. Their
  lowest vertices range -0.027..+0.169mm around the floor. This tests geometry,
  not visual beauty; browser screenshots and continuous capture are separate
  evidence. Mast, pallet, closed sideboard, portal and two-cycle continuity
  checks also pass.

Evidence is in `docs/reviews/fondfont-forklift-grounding-20261007/`, including
full-page empty-return/building shadows, loaded transfer and mobile views.
Seven complete localized posters were refreshed at 2560x854, time 12.8s.
The source symbol-only cab paint, persistent falling leaf behavior, pets and
native planting are preserved. Loaded cargo and the parked truck still hide
parts of the forklift from this frontal camera; the change does not promise
full wheel visibility in every frame.

The final lighting anchor follows the user's subsequent clarification: the
red navigation sun itself is the source. `page-sun.ts` unprojects its measured
DOM center along the orthographic camera ray to the sky plane. `syncSun()`
updates the one shared directional source after camera framing, on observed
layout changes and when the sun/canvas rectangles change during rendering.
It does not retain the earlier fixed (-10,18,10) position. No additional
opposing lights were reintroduced. Actual same-page resizes at768/390/1440px
show changed world light positions and projected source/icon agreement within
floating-point error; see `sun-resize.json`. Direction tests cover all four
responsive layouts and the same light rays for architecture and moving objects.
Reduced-motion mode now renders one static native scene and keeps responsive
lighting, without starting an animation loop. Save-data mode retains the poster.


Final browser evidence records 633 frames over27.87 seconds, scene clock
9.292..37.420, covering empty return, warehouse exit, pickup, lowering and
warehouse entry. `forklift-and-page-sun-live.mp4` is encoded from those actual
browser frames with their original timestamps. The completion advisor found
no material blocker in DOM sun anchoring, shared cast direction, grounding or
reduced motion. Its limits are retained: projected building artwork still has
baked shading and conspicuous proxy silhouettes; small views and loaded-truck
occlusion can limit wheel-contact readability. The implementation improves
contact and responsive live shadows without claiming perfect naturalism or
dynamic relighting of every source-art pixel. Shadow maps were reduced to2K/1K
with matching world-space filter width before the final 633-frame capture;
they resize with the page and are disposed with the scene.

### Correct ground-shadow bearing after refresh — 2026-10-07

A fresh reload confirmed the user's objection: the earlier light still cast
building shadows toward the upper right while the navigation sun sat upper
left. This was not a stale browser. The old test measured an elevated object's
top-to-shadow vector, which can point down-right while its ground-base-to-shadow
extension points up-right. Its source-projection agreement was insufficient.

`pageSunPosition()` now unprojects the DOM sun to the ground plane first, then
elevates the resulting ground bearing. All objects still share parallel
sunlight. This is a deliberate screen-bearing convention for this miniature
web scene; it does not claim that an elevated finite light's camera projection
coincides with the icon. The focused advisor confirmed this distinction and
the base-to-shadow acceptance criterion; its advice was followed.

The regression test first failed on the previous renderer: the1280px case
extended+86.83px right and43.91px UP from a3m object's ground base. It now checks
actual base-to-shadow direction, positive right/down components, and alignment
with the scene-center-to-DOM-sun bearing across four responsive layouts.
Actual browser same-page resizes at390/768/1440px confirm positive right/down
extensions. Evidence and the preserved failing regression are in
`docs/reviews/fondfont-sun-direction-20261007/`. Seven full posters were refreshed
again to replace the incorrect shadow direction at first paint.

### Physical loading bays and corrected roof shadows — 2026-10-07

Active scene: `public/v/fondfont/blender-v2/factory-building-v5.glb` (7.01 MiB), saved Blender source `scripts/assets/fondfont/blender-v2/factory-building-v5.blend`. Rebuild with `scripts/build-fondfont-building-volume.py`, then meshopt compression. The focused builder starts from the integrated v4 scene; forklift geometry, native garden and original imagegen image files remain intact.

The prior portal back wall was assigned Z=-4.4 while preserving a camera projection that placed its lower edge about 2.5m below ground. Artwork floors covered only a shallow strip near the sill. This made native Y=0 forklift movement look like vertical movement through the interior. Native continuous floors now reach the full bay depth, with native wall/jamb/ceiling surfaces and untouched imagegen floor/back-wall UVs. `loading-bay.ts` bounds interior, forklift and load visibility with the actual orthographic doorhead sight plane. Materials are cloned, so truck and unrelated scene materials are unaffected. The doorway sight clip is a main-pass illustration/native-model integration technique, not a claim of complete sculpted exterior architecture. Shadow depth shaders deliberately do not inherit this camera-specific clipping.

Original alpha facade depth proxies no longer cast the building silhouette. Closed Blender pier/header, chimney, phone-roof and four sawtooth roof volumes cast it. Each sawtooth rises on the right as in the imagegen reference; the former horizontal alpha roof silhouette produced misleading triangular ground shadows. Casters write neither main-pass color nor depth. The actual sun-bearing light remains shared across buildings, vehicles and pets.

Evidence: `docs/reviews/fondfont-building-volume-20261007/warehouse-entry-exit.mp4` is a continuous 21.86s browser capture, not a synthesized storyboard. Desktop phase samples, before comparisons and a native 390px screenshot are in the same folder. All seven full 2560×854 posters were refreshed without pre-cropping. The focused advisor's alignment concern was addressed using the shared ground plane and actual exported sill metadata. Completion review noted potential jamb leakage and shadow clipping: the existing swept doorway-clearance checks keep vehicles/load within the opening, and only beauty materials receive the camera clip.

Validation: `check-fondfont-loading-bay.mjs` decodes published Blender floors and sawtooth vertices; checks floor/sill registration, roof slope handedness and production material installation. Existing native tire/contact, choreography/door clearance, garden/pet and responsive sun-bearing checks passed, as did TypeScript and the 52-page Astro build.

### Cat/dog sculpt and independent tail wag — 2026-10-07

Imagegen supplied modeling reference images, not the native animal meshes. Earlier primitive-based interpretation did not reproduce the original reference quality. A new unchanged built-in imagegen board is saved at `scripts/assets/fondfont/blender-v2/pet-sculpt-reference-v3.png`; exact prompt, source and SHA-256 are in `docs/reviews/fondfont-pets-v5-20261007/imagegen-reference.json`.

Active pet asset is now `public/v/fondfont/blender-v2/garden-life-rig-v5.glb` (2.43 MiB); source `scripts/assets/fondfont/blender-v2/garden-life-rig-v5.blend`. The earlier armature asset is preserved. Models have revised puppy muzzle/drop ears/chest, distinct feline face/green iris/tabby coat, native vertex-color coat transitions, closed short groomed mesh strands, less compressed hind standing anatomy and smooth shoulder/joint weights. These remain native miniature sculpts rather than photoreal replicas of the imagegen board. No animal picture is pasted into the scene.

The dog tail is a backward soft curve with three deforming bones. Runtime tail motion has continuous phase and smoothed mood amplitude/rate, plus increasing tip delay. It restores unmodified clip bases, updates the mixer, caches all new bases, refreshes world transforms, and applies world-up rotations root-to-tip with each parent refreshed before its child. This follows the advisor's explicit correction and prevents yaw-dependent pitch/roll or accumulated overlays. The root/body does not rotate for wagging. Native tail tip vertices span 0.252m laterally and only 0.00293m vertically in an idle test. Applied/uniform bone ancestor scale is verified. Navigation's rear capsule increased by 6cm to cover the revised backward tail.

Evidence: `docs/reviews/fondfont-pets-v5-20261007/pet-native-study.png` is an actual Blender close view; `hero-after.png` is the refreshed website; `pets-tail-live.mp4` records 9.93s of actual full-page runtime. Seven complete 2560×854 posters were refreshed with the new rig. The imagegen reference is not presented as a rendered model result.

Validation: published rig has two skins, 42 bones and 22 clips. Actual supporting paw skin contact remained within 0.7mm of ground; planted-paw slip under 0.8mm. Production animation passed 1500s across four seeds, upright bodies and bounded transitions. Four 600s navigation runs retained broad roaming, play and potty behavior. TypeScript and the 52-page Astro build passed. Existing native forklift entry/exit, roof-volume shadows and responsive sun direction corrections remain active.

### Original professional pet trial and plain cab roof — 2026-10-07

The selected Autumn (Blender Studio, CC BY 4.0) and Domestic cat (Paweł
Wałasiewicz / BlenderKit, free Royalty Free) original Blender models are now
available in a local DEV-only `?pets=studio` trial. They are real source meshes,
UV markings and combed parent groom, evaluated through their native Blender rigs
to 16 walk morphs and two additive tail offsets. Walking cadence follows signed
distance; the dog wags its tail sideways. Exported soles stay within 1.6 mm of
ground. Full Cycles child-hair/shader appearance and dedicated turn/play/sniff/
potty poses are not claimed. Production retains the previous complete action rig.

Sources, attribution, licensing boundary and rebuild instructions are in
`scripts/assets/fondfont/pets/README.md`. The cat remains local because free
download does not establish extractable public GLB rights. Vite serves the two
private GLBs only during development; production builds do not copy them.
Actual browser stills, walking video, acceptance limits and advisor reviews are
in `docs/reviews/fondfont-pet-trial-20261007/`.

Active complete scene is now `public/v/fondfont/blender-v2/factory-building-v6.glb`;
Blender source is `scripts/assets/fondfont/blender-v2/factory-building-v6.blend`.
`scripts/refine-fondfont-cab-roof.py` assigns uniform flat red enamel to the cab
roof and removes marker lamp dots. The original transparent symbol is unchanged,
with no printed background. Meshopt compression preserves named hierarchy.
All seven full 2560×854 production posters were refreshed for the clean roof.

### Cute face and rebuilt truck surfaces — 2026-10-07

Current complete scene supersedes v6/v8 with
`public/v/fondfont/blender-v2/factory-truck-v11.glb` (7.65 MiB). Production pets use
`garden-life-rig-v6.glb`: rounded native dog head with the actual imagegen cute
face, retaining existing ears/body, bones and complete action rig. The local
professional pet trial and its licensing boundary remain unchanged.

The truck cab now uses an explicit editable quad cage and subdivision surface,
with fitted curved glazing, real apertures, thin wheel arches, native tire tread
and through-hole steel wheels. Original wheel pivots, rolling radius, moving
side gate and all 21 truck attachments remain. Graphite panels, finer red rails,
fuel tank and battery box add under-bed depth. Solid bowed headlights use a new
whole imagegen optic image. Its original PNG and the original truck/cute-face
images are preserved unchanged; SHA-256 provenance is in
`docs/reviews/fondfont-cute-truck-20261007/imagegen-sources.json`.

The original transparent cab symbol remains the only roof mark, aligned above
the new roof; it has no painted background. All seven full-canvas posters now
show v11 and the production v6 pet rig. Native studies, actual browser evidence,
50.8-second complete-loop recording, rebuild and acceptance limits are in
`docs/reviews/fondfont-cute-truck-20261007/findings.md`. This is a web model
refinement; it does not claim photorealistic equivalence to the imagegen board.

Latest review selection remains `?pets=studio` after the user's explicit request
to restore it. Current German and Chinese browser previews use the original
professional pet models (yellow Autumn fur and original cat), alongside the new
v11 truck. The native v6 cute head remains the production-compatible fallback;
it does not supersede the user's chosen professional trial. Locale navigation
preserves the studio query. Public posters continue to use the production rig,
in accordance with the private cat asset's licensing boundary.


### Latest reference truck, supported studio turns, and carried leaves — 2026-10-07

Current complete scene is `factory-truck-v14.glb`(7.69MiB), with native
`factory-truck-v14.blend`. Larger real glazing, thinner roof, formed/recessed
fascia, fitted handles/mirrors and inner wheel arches supersedev11. Original
imagegen design/optic sources and cab symbol remain unchanged. All21rig
attachments and sixwheel contacts pass the two-cycle checks. Seven complete
2560×854 public posters are refreshed. No claim of photorealistic source parity.

Ordinary local FondFont routes now default to the selected original studio
pets; the query parameter is unnecessary. Their84native morphs include left/
right pivots and finite paw-heading corrections. Runtime keeps planted soles
anchored, completes swing steps at stops, advances gait only forward and resets
contact on time seeks. Yellow Autumn fur and tail wag remain. The cat model
continues to stay outside public/dist pending web distribution permission;
production posters/builds still use the native compatible rig. Current details,
real browser recordings and acceptance limits:
`docs/reviews/fondfont-studio-turns-20261007/findings.md`.

Falling tree leaves now collide with exposed moving truck-bed space, settle,
and retain local position/heading while transported. Captured leaves are not
also drawn falling or duplicated on the ground. Ground accumulation and
randomized displaced wheel wakes remain. A600s deterministic check covers
119leaves,9bed captures and418wheel wakes. Details and reference truck evidence:
`docs/reviews/fondfont-cute-truck-20261007/findings.md`.
## Licensed professional pets as production default — 2026-10-08

The downloaded JonasDichelle **Rigged and animated Cat** replaces the restricted
BlenderKit cat. Source package confirms **CC BY 3.0**. Original source/license
and checksums are in `scripts/assets/fondfont/pets/calico-cat/`; its native rig,
original skin/coat/eyes and1,151 groom strands are converted by
`scripts/build-fondfont-calico-cat.py`. Groom orientation follows evaluated
triangle frames. Native IK is adapted for84 grounded walk/turn/plant/head/tail
poses; the authored Walk clip is not exported unchanged.

Default public assets: `/v/fondfont/pets/cat-v1.glb` and `dog-v3.glb` (Autumn,
CC BY4.0, existing yellow coat and tail wag). Both production and development
load these without `pets=studio`. Old restricted cat files stay out of public.
Localized footer attribution, full public derivative notices and original cat
license accompany the assets. Seven2560×854 posters were updated. No publishing
or commit was performed. See `docs/reviews/fondfont-cat-replacement-20261008/findings.md`
for browser evidence, exact checks and remaining fur/mobile-performance limits.

## 2026-10-08 — lossless hero transport and two cats

Default animals are now the original CC BY 3.0 calico cat and a charcoal-coated
instance. They share one GLB/geometry/texture download while retaining separate
morph weights, poses and routes. Eyes retain the original material. Autumn is
retired from the public runtime/assets; original source remains private. All
seven locale credits and complete 2560x854 posters are updated.

Models are served as pre-gzipped copies with native browser decompression, or
original GLBs when DecompressionStream is absent. HTTP-decoded responses are
also accepted; failed compressed loads never redownload a raw model. Build
regenerates gzip copies automatically. Effect PNGs have lossless/exact WebP
encodings, verified byte-for-byte after RGBA decode and channel-for-channel
through actual WebGL texture upload. No new raster artwork or geometry loss.

Measured cold production-preview hero response bodies: 19.68 MB -> 9.93 MB
(-49.54%), excluding installation screenshots/shared page resources. File-size
budget if JavaScript is not HTTP-compressed: 20.23 MB -> 10.48 MB. This is not
a deployed CDN measurement or a speed/frame-rate claim. Details, raw controls,
mobile emulation limits and motion evidence are in
`docs/reviews/fondfont-hero-budget-20261008/findings.md`.

## 2026-10-08 — campus v3: modeled buildings and truck from modeling-grade imagegen

The hero scene now loads `public/v/fondfont/blender-v3/campus-v3.glb` (2.47 MiB,
1.42 MB gzip; previously 7.69 MiB / 5.0 MB). The projected full-image building
paintings and their shadow/occluder proxies are replaced by real models built from
new Codex imagegen orthographic sheets. One orthographic camera now sees only real
geometry, so building, vehicle and shadow perspective agree.

- Imagegen sources, made for modeling: elevation and blueprint sheets
  (foundry, warehouse, truck, forklift), seamless tiles (brick, slate, cladding,
  asphalt, concrete) and truck decals (wheel face, headlamp, tail lamp, grille).
  Originals, prompts and SHA-256 are in
  `scripts/assets/fondfont/blender-v3/imagegen/provenance.json`. Web tiles come
  from `scripts/prepare-fondfont-textures-v3.py`; that step resizes and repairs
  wrap seams only.
- Buildings: `scripts/fondfont-architecture-v3.py`. The phone roof sits flush on
  the warehouse with a 6 cm overhang.
- Truck: `scripts/fondfont-truck-v3.py`, rebuilt against the blueprint. All rig
  pivots, the wheel radius, the deck height, the gate hinge and the label anchors
  are unchanged. Six wheels share one mesh.
- Assembly and size budget: `scripts/build-fondfont-campus-v3.py`, then
  `scripts/compress-fondfont-campus-v3.sh` (gltf-transform dedup and meshopt;
  node names are preserved).
- The two legacy native pets are no longer shipped in the scene GLB. The runtime
  already replaced them with the licensed studio pets.

- Sixteen retired GLB and PNG files (about 93 MB) moved out of `public/v/fondfont/blender-v2/`
  to the local `scripts/assets/fondfont/blender-v2/retired-public/`, so they are no longer
  deployed. The truck attachment baseline lives in
  `scripts/check-fondfont-truck-attachments.json`.

- The camera is now a physical perspective lens (`src/lib/fondfont/campus-camera.ts`):
  the same 33° view axis, 52 m from the target, with a vertical field of view solved per viewport (13–17° in the tested layouts).
  The orthographic view had produced reverse-perspective roofs. The field of view
  is solved so the projected curb matches the page road width. The page sun, the
  loading-bay sight clip and the smoke ray-march all trace real per-pixel rays.

- Warehouse roof: the phone slab has 20–28 cm eaves and a 26 cm titanium band. The
  screen carries twelve classic glyphs for the current locale
  (`src/lib/fondfont/roof-glyphs.ts`). Each glyph drifts with deterministic Brownian
  motion and cycles through a pool of 5–7 licensed typefaces with cross-fades. The
  pools are listed in `src/lib/fondfont/roof-fonts.json` and built by
  `scripts/prepare-fondfont-roof-fonts.py`, which checks glyph coverage, subsets the
  fonts and publishes their licences. The check is `scripts/check-fondfont-roof-glyphs.mjs`.

- Download budget: cold page transfer is 3.47 MB (zh-hans desktop) and 3.52 MB
  (en mobile), down from 9.59 MB and 7.17 MB. The changes:
  - `cat-v2.glb`: unsubdivided cage, half the groom strands, all 84 morphs kept;
  - web-sized lossy leaf and dust sprites (`prepare-fondfont-effects-v2.py`);
  - WebP installation captures, 600 px and 1000 px (`prepare-fondfont-install-webp.py`);
  - small header and favicon icons (`prepare-fondfont-icon-web.py`).

Evidence, checks and size table: `docs/reviews/fondfont-campus-v3-20261008/findings.md`.

### First-frame posters and loading — 2026-10-08

Seven localized posters now show frame zero with the live roof glyph seed (47).
The initial light is shared with the poster, then blends to the responsive page
sun after the 200ms handoff; viewport-dependent smoke and leaves fade in with it.
Reduced motion also uses frame zero. Visible scene initialization shows a prominent
centered loader without visible text, cleared on readiness or failure. Save-data and
no-JavaScript keep the poster without a spinner. Export settings and browser
evidence: `docs/reviews/fondfont-hero-loading-20261008/findings.md`.
