# World Book landing page

`/world-book/` is English-only, with no language selector or redirect. The homepage
card links here and uses the current World Book name and original app icon.
The page follows CHMate's typography, grain, wordmark loader, three feature cards,
purchase section, and shared footer. The website preview adds a cinematic H3
opening before the native screens, as requested; it is separate from App Store media.

## Media

Reviewed originals are read without modification from:

`/Users/realazy/Projects/iOS/WorldABC/output/release-review-20261005/`

The internal screen videos use its native globe, reader, charts, and gallery captures,
in dark and light appearances. They retain the reviewed scene sequence,
without baked captions or decorative framing. iPhone exports at 664 × 1442 and
iPad at 900 × 1200, H.264/BT.709, 30 fps, AAC 96 kbps, fast-start MP4.
Posters use the reader at 10.7 seconds. Current videos are about 1.9 MB (iPhone) and 2.1 MB (iPad).
The iPad light-chart recording has a sparse frame timestamp after the seek point.
Each source now resets its first timestamp before resampling to 30 fps; otherwise
that segment started 2.333 seconds late and shortened the picture stream while
audio still filled the requested duration. Export checks verify each segment's
zero start time and picture duration, and final composition verifies the picture
stream duration independently of the MP4 container duration.

The fixed backdrop uses `flat-map-v1.jpg` (1600 × 800, about 363 KB), an illustrated
map at 18% opacity. The user's correction preserves the scrolling map but removes
book/page edges, binding, paper folds, relief and perspective. Built-in imagegen
edited a frame of the previously reviewed map; its result and exact edit prompt
are saved under `scripts/assets/world-book/animation/flat-map-v1.png` and
`flat-map-imagegen-prompt.txt`. The smooth watercolor illustration remains.
The edit reference is retained as `flat-map-edit-reference.png` in that directory.

One repeated background image translates horizontally with a 90-second linear
CSS transform. There is no background video decoder, canvas, animation loop in
JavaScript, animated filter or background-position repaint. A ResizeObserver
sets the repeat distance to the map's exact rendered width. The loop always
moves in one direction. The original transparent iPad bezel and alpha screen mask
reuse CHMate's device geometry; mobile shows the native screen without a bezel.

## Website cinematic preview

`preview-ipad-en-v7` is 900 × 1200; `preview-iphone-en-v7` is 664 × 1442,
matching the original native exports. Both begin with an accelerating MiniMax H3
country assembly and a globe-light reveal, then show the real globe, reader, charts and gallery.
Only the generated opening is reframed. The native recordings fill the entire
canvas without scaling, cropping, inset frames, baked captions or decorative margins.
Desktop restores the original CHMate layout: hero copy left, full native iPad
screen right with a CSS bezel. Mobile shows the original full-width iPhone screen.
Clear native reader posters keep the first and reduced-motion states legible.
The opening lasts 3.8 seconds: 0.4 seconds of anticipation, 1.2 seconds of
accelerating country collapse, 0.4 seconds of impact/settle, 1 second of presentation
and a 0.8-second globe-light reveal. Native scenes last 27.1 seconds after three
0.7-second page overlaps; the complete film is 30.1 seconds.
The map stays still during the opening, so one motion focal point owns that scene.
The upper-right platform label is omitted at the user's request.

The current artwork pair is `scripts/assets/world-book/animation/grand-assembly-first-v1.png`
and `grand-assembly-last-v1.png`, made with built-in imagegen. The first image has
widely detached country plates hovering over a continuous blue ocean core. The
last image brings those countries onto the same core, keeping the Africa/Europe
orientation and World Book's cream, mint, blush and yellow country palette.
The user rejected v5's short edge-settling event as insufficiently grand. This
revision changes the spatial assembly itself, rather than extending the old take.
A framing edit reduces the expanded country cloud to leave breathing room in the
narrow iPhone crop. The exact prompt set and references are recorded in
`grand-assembly-imagegen.json`; all named text prompts live beside the artwork.
The source motion take is `grand-assembly-h3-v1.mp4`, conditioned on both images.
Its prompt requests a continuous inward gathering with a restrained shared clockwise
drift, rigid country silhouettes, a fixed camera/light and a fully assembled endpoint.

The inspected H3 take completes convergence near 3 seconds and then holds still.
`prepare-world-book-assembly.py` now gives that active motion a nonlinear timeline:
the early setup maps to 0.4 seconds, then inward travel accelerates through a
1.2-second collapse. Offline motion-compensated interpolation retains 30 fps.
The selected prepared source is `grand-assembly-impact-v1.mkv` (48 lossless frames).
The user's latest feedback rejects the previous 6.5-second stretch as too slow;
that older pacing source stays archived. The fast version preserves visible inward
travel late in the collapse and reaches the completed globe before its impact cue.

`prepare-world-book-impact.py` builds one 0.4-second cyan closure impulse, a
0.8-second opening reveal and a gentler 0.6-second native globe theme reveal.
These are deterministic code-native grayscale/alpha layers. The reveal mask moves
outward across the globe; its background follows a delayed smooth exposure fade,
which avoids an expanding black iris around the sphere. Every mask begins exactly
black, ends exactly white, and advances monotonically at every pixel. Glow alpha
starts and ends at zero and stays on the globe's limb, away from navigation controls.
The stronger closure impulse belongs only to the artwork; native theme change
uses weaker light and has no impact impulse. There is one accent per event.
The camera pushes forward only on generated artwork from 1.1 to 1.95 seconds,
then stops before the native reveal at 3 seconds. Tablet and phone retain their
reviewed globe alignment and different final zoom factors. All native screens stay
at full original dimensions and their existing H3 page reveals remain intact.
The globe's dark/light change gets the 0.6-second reveal; reader, chart and gallery
theme changes retain their original 0.4-second fades. The user explicitly requested
both the opening handoff and native dark/light change be strengthened.
All tempo, light, impact and compositing run offline. The site still decodes one
selected H.264 movie and performs no runtime lighting or optical-flow work.
Earlier opening artwork/takes stay archived in this directory, not served.
Read every new take before selecting it; a prompt is not a visual quality check.

Generate a new take (existing video paths are refused):

```sh
python3 scripts/generate-world-book-motion.py \
  --engine '/Users/realazy/tmp/h3.c/h3' \
  --model '/Users/realazy/.cache/huggingface/hub/models--MiniMaxAI--MiniMax-H3/snapshots/42ed227ee7df40d41602854ae760620d6eb651fe' \
  --last-frame 'scripts/assets/world-book/animation/grand-assembly-last-v1.png' \
  --output 'scripts/assets/world-book/animation/grand-assembly-h3-v2.mp4'
```

Prepare pacing and light layers, export native scenes, then compose website exports
with Python, NumPy, Pillow, and ffmpeg:

```sh
python3 scripts/prepare-world-book-impact.py
python3 scripts/prepare-world-book-assembly.py \
  --source 'scripts/assets/world-book/animation/grand-assembly-h3-v1.mp4' \
  --arrival-seconds 3 \
  --output 'scripts/assets/world-book/animation/grand-assembly-impact-v1.mkv'

python3 scripts/export-world-book-media.py \
  --source-dir '/Users/realazy/Projects/iOS/WorldABC/output/release-review-20261005' \
  --transition-motion 'scripts/assets/world-book/animation/page-transition-normalized-v2.mkv' \
  --globe-effects 'scripts/assets/world-book/animation'

python3 scripts/compose-world-book-preview.py \
  --motion 'scripts/assets/world-book/animation/grand-assembly-impact-v1.mkv' \
  --music '/Users/realazy/Projects/iOS/WorldABC/output/release-review-20261005/sources/Summer-Fun.mp3'
```

The exporter reads originals, writes `public/v/world-book/`, and removes its
temporary segments automatically. Keep the reviewed source package for regeneration.

### H3 page transitions

`page-transition-h3-v1.mp4` is a reusable grayscale H3 reveal: a gently curved
edge moves from left to right, taking the mask from black to white. H3 is
conditioned on code-native monochrome endpoint images, with its exact prompt
and receipt beside the take. `prepare-world-book-transition.py` produces a
21-frame, 0.7-second lossless mask; it narrows and softens the edge, re-times
the generated acceleration so the reveal settles gently, enforces monotonic
progress and exact black/white endpoints, and records frame statistics.
The exporter uses the H3 mask to composite actual outgoing and incoming native
clips, without generating or deforming app text and charts. The narrow feather
blends the real clips locally during each page reveal. Reader, chart and gallery theme changes
retain their ordinary 0.4-second dissolve; the globe uses its new light reveal. One mask is reused for three page
changes and both devices; all effects are baked into the same foreground MP4,
with no added browser decoder or runtime transition effect.
The final normalized mask reaches exact opaque endpoints and advances monotonically
at every pixel. Its largest blended region is about 5.6% of the canvas, confined
to the moving edge rather than overlapping both pages across the whole screen.

```sh
python3 scripts/generate-world-book-motion.py \
  --engine '/Users/realazy/tmp/h3.c/h3' \
  --model '/Users/realazy/.cache/huggingface/hub/models--MiniMaxAI--MiniMax-H3/snapshots/42ed227ee7df40d41602854ae760620d6eb651fe' \
  --prompt-file 'scripts/assets/world-book/animation/page-transition-h3-prompt.txt' \
  --first-frame 'scripts/assets/world-book/animation/page-transition-first.png' \
  --last-frame 'scripts/assets/world-book/animation/page-transition-last.png' \
  --seconds 2 --seed 10062028 \
  --output 'scripts/assets/world-book/animation/page-transition-h3-v2.mp4'
python3 scripts/prepare-world-book-transition.py \
  --source 'scripts/assets/world-book/animation/page-transition-h3-v1.mp4' \
  --output 'scripts/assets/world-book/animation/page-transition-normalized-v2.mkv'
```

## Playback and downloads

At least 768 px loads iPad; narrower viewports load iPhone. Only the selected
preview source loads initially. Resizing preserves the playback position and an
intentional pause. Foreground autoplay waits for the shared loader to be removed, rather than
starting at the earlier content-theme handoff. This keeps the opening visible
from its first frame; the loading observer disconnects after the handoff. The backdrop
follows actual foreground playback and pauses when buffering, paused, offscreen,
or hidden. Reduced motion and browser Save-Data prevent autoplay and initial MP4
downloads; manual foreground playback remains available. Reduced motion disables
the map and grain animations. Save-Data keeps the map still even during manual
playback. Without JavaScript, the appropriate native-ratio preview has controls,
the map remains still and the loader is hidden. Keyboard focus and fullscreen use
the same behavior as CHMate.

Apple's unchanged English badge is shared with CHMate. CTA links and the Safari
Smart App Banner use app ID **412637620**, provider token **259198**, and campaign
**lazyapps-en**, matching the user's preferred English-page attribution. World Book is a paid, one-time purchase: no free-app
claims, subscriptions, or in-app purchase wording inherited from CHMate.

Country text, flags, rankings, locator maps, and the globe work offline. Photos
and regional maps require an initial download. Data is archived, not live; figures
may refer to different years. The footer identifies the app as an independent
reader, not affiliated with or endorsed by the CIA.

## Branding and credits

The unchanged original `AppIcon.icon` is archived under `scripts/assets/world-book/`.
`scripts/render-world-book-opengraph.py` uses Icon Composer's Default rendering,
the original globe/book silhouette, and Sofia Sans Extra Condensed at weight 900.
It excludes decorative stars/light spill from the alpha mask without changing
the renderer's symbol colors or making the globe transparent. The silhouette mask
is intersected with Icon Composer's alpha so the book's clipped outer edges stay
transparent instead of exposing black pixels. It writes the full
app icon, extracted symbol, and 1200 × 630 Open Graph image. The centered symbol
and wordmark fit within the 630 × 630 safe square. Paper and noise match
`docs/OPEN_GRAPH.md`. The square proof is `/tmp/world-book-opengraph-square.png`.

```sh
python3 scripts/render-world-book-opengraph.py
```

Dependencies match CHMate's renderer: Pillow, fontTools with Brotli, `rsvg-convert`,
and Xcode Icon Composer's `ictool`.

Music is “Summer Fun” by Ahjay Stelino, under the Mixkit Stock Music Free License,
with an edited excerpt, fades, and volume adjustment. Credits appear in the footer.
The backdrop is a flat edit of the previously reviewed imagegen map artwork.
Source license records are retained in `scripts/assets/world-book/licenses/`.

## Review and release

Primary product evidence: WorldABC's `docs/releases/2026-10-05/app-store-description.txt`
and `submission-result.md`. The captures represent version 261006.0 (456), which
was awaiting review at the time of implementation. This task prepares local files
only. Before publishing them, confirm the represented release is available.

The Astra/xhigh approach consult supported the CHMate structure and accurate
purchase/offline copy; its release-version recommendation is followed by keeping
this change local. The first completion consult approved the native-screen version.
The animation-direction consult recommended putting H3 directly in the preview
opening, then yielding to the real interface. A later user correction restores
the original native proportions and CHMate layout so app details remain readable.
The focused proportion consult endorsed this correction, recommending exact rendered
screen dimensions and clear native posters; those recommendations are followed.
Consultation records: `/tmp/lazyapps-world-book-20261006/` and
`/tmp/lazyapps-world-book-motion-20261006/` and
`/tmp/lazyapps-world-book-proportion-20261006/`.

Final checks: project build and whitespace checks pass. Chromium verifies widths
320/390/768/1440, correct preview selection, no overflow or JavaScript errors,
native aspect ratios and rendered dimensions matching CHMate, map-only background,
pause across resize, offscreen pause, reduced-motion/manual playback without an
initial MP4 download, and both no-JS variants.
Save-Data checks also confirm click-to-play and hidden-tab pause/resume. An
eight-second Chromium desktop playback sample recorded 0.176 seconds of main-thread
task time, including 0.008 seconds of script time and 0.00023 seconds of layout
time. This is a local sample, not a guarantee for every device or a measurement
of GPU/video-decoder memory. No background video is requested; only the selected
foreground MP4 loads. The build retains no superseded preview v2/v3/v4/v5/v6 movies or book-backdrop
MP4 assets.
Use `npm run preview -- --host 127.0.0.1 --port 4330` for local review. Python's
basic HTTP server did not support the byte ranges needed for the seek check;
Astro's native preview returns HTTP 206 and the unchanged check passes there.
The focused Astra/xhigh completion follow-up confirmed the original serving issue
is resolved. The proportion correction's focused Astra/xhigh completion review
approved local handoff with no material blocker; it specifically limits performance
claims to the measured Chromium sample.

The latest opening consult supported an expressive sculptural globe after the user
rejected the literal app-like opening. Its recommendation to keep continuous blue
ocean and lift only selected country edges is followed. The motion prompt omits
an orbit and moving light sweep; a quiet forward move is retained as a supporting
camera gesture. The selected take is inspected in both native portrait crops.
The H3 transition consult's narrow-feather and exact-endpoint recommendations are
implemented by the normalized 0.7-second mask. Current records are under
`/tmp/lazyapps-world-book-opening-20261006/`.

The v5 previews pass a fresh 1440/390 Chromium check: native dimensions, 29.7-second
container duration, seeking through every page change, selected-device downloads,
no overflow or script errors, and reduced-motion manual playback with no initial
MP4 request. Both final picture streams last 29.666667 seconds (one 30 fps frame
less than the audio/container). Opening crop contact sheets and browser screenshots
are saved in the current review directory. No extra browser effect or decoder was
added for the new opening or H3 page changes.

The latest Astra/xhigh completion review (`completion-v5-review.md` in the current
review directory) found no material blocker to local handoff. It verified the
opening crops, native proportions, confined transition feather, loader-removal
gate and resource model. It identifies the opening dissolve's briefly doubled
outlines and stronger generated forward move as polish opportunities. The selected
expressive take is retained for local visual review; it is not described as exact
fixed-camera compliance. The full native screen geometry remains unchanged.

The v6 approach consult explicitly follows the latest request for broad detached
country plates and a longer convergence. It recommends actual-phone crop margins,
a consistent ocean core, restrained shared clockwise travel, and an editorial
hold added after the generated arrival. The frame pair and compositor follow
those recommendations. Motion runs with a fixed generated camera; the separate
baked camera push gives the assembled globe a larger final presentation. The
current consult and verification directory is
`/tmp/lazyapps-world-book-assembly-20261006/`.

The v6 source H3 take is 704 × 1280, 158 frames at 24 fps (6.583333 seconds).
Inspection found early convergence followed by a long generated static tail;
that observation determines the 3-second arrival cut in the pacing script.
The normalized assembly verifies 195 frames at 30 fps and a zero start timestamp.
Final H.264 picture streams last 34.866667 seconds, one 30 fps frame shorter than
the 34.9-second audio/container. Crop contacts verify the visible detached plates,
the actual gradual gathering, full assembled silhouette and preserved native UI.
Centering the artwork's forward move, without a vertical pan, improves tablet
alignment at the dissolve. Offline interpolation and camera framing add no browser
runtime work or extra decoder. The v6 movie sizes were 4,499,295 bytes (iPhone)
and 5,197,089 bytes (iPad).

The final v6 Chromium checks pass at 1440/390: the selected device movie is the
only foreground source, loader removal precedes playback, native dimensions and
34.9-second duration match, all page changes seek correctly, and there is no
horizontal overflow or script error. Reduced motion performs no initial MP4
request and supports manual play. The map stays still through the opening and
resumes after native footage begins. Project build, script parsing, JSON metadata
and whitespace checks pass; superseded v5 media are absent from public and dist.

The v6 Astra/xhigh completion review (`completion-review.md` in the current review
directory) finds no material blocker to local handoff. It confirms the wider plate
gathering, complete final globe, both crop margins, original native screen framing
and unchanged single-video resource model. It treats the restrained initial buildup
and the dissolve's briefly doubled outlines as optional polish. The deliberate
buildup and current dissolve are retained for local visual review. Static frame
checks establish progression and framing; they do not fully prove perceived optical
flow smoothness during continuous playback. The local review makes no publication
approval claim.


### v7 impact and illumination verification

The user rejected the slow v6 buildup and requested both the opening handoff
and native globe theme transition be strengthened. The v7 approach review in
`/tmp/lazyapps-world-book-impact-20261006/approach-review.md` recommends a 3.8-second
opening: 1.6 seconds of accelerated H3 convergence, 0.4 seconds of settling,
1 second of presentation and a 0.8-second reveal. It recommends stopping
the artwork camera move before the reveal and keeping native illumination weaker
than the opening. Those recommendations are implemented; the genuine H3 take is
re-timed offline rather than generated again.

The radial reveal replaces the globe first; a delayed exposure fade brings in
the surrounding native background and controls. This avoids the first trial's
large circular iris extending beyond the planet. Gray masks reach exact 0/255
endpoints and advance monotonically at every pixel. Closure and illumination
alpha layers start and end at zero; native theme illumination peaks below the
opening illumination. Only generated opening artwork receives the camera push.

Both final H.264 picture streams and their containers last 30.1 seconds.
The iPad export is 900 × 1200 and 3,660,130 bytes; iPhone is 664 × 1442 and
3,231,483 bytes. The complete native app canvas keeps its original aspect ratio.
Chromium checks pass at 1440/390: loader removal precedes autoplay, only the
selected device movie loads, all transitions seek, layout has no horizontal
overflow or script errors, and reduced motion waits for manual play.
The map remains still through the 3.8-second opening and then scrolls in one
direction during playback. These are local functional and frame checks,
not a universal browser/GPU performance benchmark.

A light seam at the tablet screen's left edge came from complementary
antialiased screen/frame masks exposing the page background. A black backing
extends one CSS pixel under the frame on each side, filling the seam without
changing the video's size or position. The backing is disabled on the frameless
phone layout. Before/after desktop screenshots verify the seam is removed.
Superseded v6 website exports are removed; source takes remain archived.


A short-screen intro-focus/temporary-fit/return-top experiment was implemented
and locally checked, then removed at the user’s explicit request. The page now
enters normally at its existing scroll position, with no special short-screen
scrolling, intro transform or return arrow. The faster v7 movie and frame-seam
correction remain.

The Astra/xhigh completion review (`completion-review.md` in the v7 review folder)
finds no material blocker for the local movie/seam handoff. It directly verifies
final stream dimensions/durations, offline effects, one-video playback and the
seam correction. Its short-screen experiment findings are historical: that UI
was removed after the user cancelled it, and normal entry is checked separately.
The generated/native globe's differing geography/style during the brief reveal
remains optional polish, accepted for this local creative preview. Frame and
local Chromium checks do not prove every browser/GPU or continuous-motion quality.

## Recording without a mouse

Recording mode is available only in `astro dev` on `localhost`, `127.0.0.1` or
`[::1]`. Production builds and `astro preview` ignore `record=1` and keep ordinary
playback, controls and cursor behavior.

Open `/world-book/?record=1` on that local dev server. After the wordmark loader finishes, the selected
preview automatically starts from the beginning with sound. Astro's development
toolbar, the page cursor and native video controls are hidden only on this URL.
No Space shortcut is bound. Refresh the page for another take; Escape pauses.
The movie loops automatically, including in recording mode.
Keep the page focused and the preview in view; hidden/offscreen pauses remain.
For mobile recording, position the preview before capturing it. The original
phone/tablet movie and aspect ratio remain unchanged.

The browser must permit autoplay with sound. This query does not bypass browser
media permissions and does not silently fall back to muted recording. If audible
autoplay is blocked, allow it for this site in the recording browser and reload;
Synthetic JavaScript events do not grant that permission. Recording explicitly preloads
only the selected movie even with SaveData/reduced-motion enabled. Ordinary URLs
keep muted autoplay, native controls, looping and their accessibility/data
preferences. Capturing system audio remains the recorder's job.

The earlier recording version waited for Space; the user subsequently requested
automatic entry playback. Its keyboard-triggered QA is historical. Current checks
cover audible recording autoplay when permitted, ordinary muted playback and the
development toolbar being hidden only in recording mode.

For a recording browser that needs no interaction or persistent settings change:

```sh
python3 scripts/open-world-book-recording.py
```

This macOS helper starts installed Google Chrome in a separate temporary profile,
using Chrome's documented `--autoplay-policy=no-user-gesture-required` flag and an
app window without its address bar. It opens the local recording URL directly.
Close/quit this temporary Chrome session after recording; the helper removes its
profile when Chrome exits. The normal Chrome profile/settings are untouched.
The local Astro dev server must already be running (default port 4330). An
alternate loopback URL can be given with `--url`; the helper adds `record=1` and
rejects remote hosts. Use the recorder's start delay and capture
system audio. The in-app browser was observed to block unmuted entry playback;
that browser's restriction cannot be overridden by this page's query string.

Current verification: build passes; allowed recording entry starts unmuted without
input, hides the real Astro dev-toolbar, and keeps ordinary URLs unchanged.
Headless Chromium did not reproduce the in-app browser's autoplay rejection even
with restrictive flags, so the rejection branch is checked with an explicit
NotAllowedError stub instead; the actual in-app blocked state is observed through
CUA. This distinguishes policy observation from deterministic error-path testing.
A full installed, headful Chrome helper run independently confirms unmuted playback
without input and hidden controls, then Browser.close/Chrome exit confirms the
temporary profile is deleted. The optional remote-debugging transport was added by
a test-only executable wrapper, not the production helper. The focused Astra
review found no design blocker; its QA/lifecycle gaps are resolved by these checks.
Records: `/tmp/lazyapps-world-book-record-auto-20261007/` and the corresponding
`/tmp/lazyapps-world-book-record-auto-qa-20261007.*` files. Quit the temporary Chrome
session if closing its app window leaves it running; cleanup waits for process exit.

Local-only verification: the build passes; browser checks confirm local dev
recording enables audible autoplay and hides the toolbar, ordinary dev URLs keep
normal playback, and the production build served by `astro preview` ignores
`record=1`. Space neither starts nor restarts playback. The helper rejects remote
URLs. Records: `/tmp/lazyapps-world-book-record-dev-only-*-20261007.*`.
