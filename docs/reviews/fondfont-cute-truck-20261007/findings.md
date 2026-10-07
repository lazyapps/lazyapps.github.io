# FondFont cute head and truck surface refinement — 2026-10-07

User rejected the primitive-looking truck compared with its imagegen reference.
The first v8 revision remained too boxy. It is retained as intermediate evidence,
not the delivered result. Production now loads `factory-truck-v11.glb` and
`garden-life-rig-v6.glb`.

## What changed

- Cab: explicit 12-section quad control cage, subdivision level 2, hollow pressed
  shell, real front/side apertures and fitted curved glazing. The editable cage
  remains in the Blender source and is excluded from web export. Window geometry
  is tessellated then projected onto the evaluated shell. The front aperture cutter
  has planar caps. Ray checks through the windshield confirm glazing followed by
  the interior/back wall, without an overlapping cab slab.
- Fine pressed wheel arches replace the retained chunky front fenders. All six
  wheels have rounded native rubber surfaces, shallow modeled tread, real metal
  dish holes, rolled lips and six lug nuts. Original rolling/steering pivots and
  the 0.435 m rolling radius remain intact.
- Clean vermilion automotive paint, narrower red bed rails, graphite gate panels,
  silver under-bed fuel tank, straps, battery box, recessed lamps and finer seams.
  Two bowed, solid lamp surfaces use the whole unchanged imagegen optic image.
  Whole-truck reference art is not used as a truck sprite.
- The original transparent cab symbol remains background-free, registered above
  the new roof. The slimmer rail carries a correspondingly smaller name label.
- The production dog has a rounded, rigged native head with the actual imagegen
  cute face UV-mapped to its front. Existing body, ears, 42 unique bones, 22 action
  clips and independent tail wag remain. This does not replace the whole dog with
  a professional fur/groom model. The separately licensed professional pet trial
  remains DEV-only, outside public/dist.

## Visual evidence and limits

- `truck-precision-reference-v7.png` (source assets folder): actual imagegen design
  board. `imagegen-sources.json` records originals and identical SHA-256 hashes.
- `truck-v8-*.png`, `truck-v9-*.png`, `truck-v10-*.png`: intermediate Blender studies.
- `truck-v11-three-quarter.png`, `truck-v11-side.png`: final native Cycles studies.
- `hero-final.png`: actual Chinese page with final model and production pet rig.
- `transport-final-live.mp4`: actual browser recording, 50.8 seconds, scene clock
  0.091–51.390, covering the complete 47.9-second loading/transport/unloading/return.
  `final-cycle-frames/times.json` preserves native frame timestamps.
- `puppy-front.png`, `puppy-three-quarter.png`, `puppy-side.png`, `puppy-web.png`:
  actual rounded head and production browser evidence.

The cab and wheels are substantially smoother and more structured than v8;
this remains a stylized web model with simplified proportions and trim, not a
claim of structural or photorealistic parity with the imagegen multi-view board. Native AgX studio lighting and webpage Neutral tone
mapping differ; the actual browser view is the delivery reference.

## Validation

- 21 original truck attachment nodes and their parents/transforms preserved;
  only the static cab paint anchor rises to 2.372 m.
- All six actual decoded tire meshes stay grounded throughout two animated loops.
- Full choreography, fork/door clearance, side gate, replenishment and two-cycle
  continuity checks pass. Forklift axle tilt remains effectively zero and tire
  soles remain within 0.17 mm of ground over two trips.
- Native dog/cat action-rig check passes 1,500 seconds; cute head remains bound to
  the original head bone. No private trial pet models are added to public assets.
- Final scene GLB is 8,018,960 bytes (7.65 MiB), below the existing 8 MiB budget.
  Export uses WebP quality 90 and meshopt, 16-bit position quantization. Source
  image pixels remain untouched; export compression is separate from source art.
- Seven full 2560×854 posters updated: en, zh-hans, zh-hant, ja, ko, fr, de.
  No pre-cropping or raster repainting; page layout handles overflow.

## Rebuild

1. Blender: `scripts/refine-fondfont-truck-surface.py` produces editable v10 base.
2. Blender: `scripts/refine-fondfont-truck-lamps.py` produces v11 with imagegen
   optic material and under-bed equipment.
3. Meshopt CLI: `meshopt factory-truck-v11-raw.glb factory-truck-v11.glb
   --quantize-position 16`. Preserve named hierarchy; do not flatten.
4. Blender: `scripts/render-fondfont-truck-study.py -- v11` renders study views.
5. Head source: `scripts/refine-fondfont-puppy-head.py`, then meshopt compression.

Approach advisor: `quality-advisor.md`. Followed its recommendation to replace
extruded/beveled cab detailing with an editable subdivision surface and inspect
actual views before integration. A free donor was researched but no suitably
licensed, exact-style professional truck was acquired or claimed. The advisor's
suggested human approval gate was treated as review advice: the user had already
authorized reversible refinement, so visual self-review continued without an
extra approval interruption. Completion review is recorded separately.

## Completion review and latest user steering

`completion-advisor.md` inspected the v8/v11 studies and sampled actual browser
frames. It found no blocking geometry/integration defect and accepted delivery as
an improvement. Its limitation correction is adopted: larger reference glazing,
tighter roof profile and integrated fascia differ structurally, not only in
rendering realism. Its three further art-direction suggestions (roof crown and
glass area, continuous door seam, recessed fascia transitions) remain explicit
limitations; no parity claim is made.

TypeScript check with es2022/dom/dom.iterable/vite types passes. `npm run build`
passes with 52 pages. The final decoded six-wheel contact range is
-0.000006425..0.000061097 m. Browser console reported no warnings/errors.
390px responsive DOM bounds were checked (scrollWidth=390); the browser's
emulated screenshot surface scaled inconsistently, so its diagnostic image is
not treated as a verified phone capture.

The user then explicitly requested restoring `pets=studio`. Both the Chinese
and currently viewed German preview were returned to the original professional
pet trial, with the yellow Autumn fur remap and tail wag. Active review URL:
`http://127.0.0.1:4332/fondfont/de/?pets=studio`. New truck remains integrated.
`hero-studio-restored.png` is the actual restored preview. The v6 cute head is
retained as the production-compatible fallback asset; it is not the user's
chosen professional preview. Language switching already preserves query params.


## v14: reference proportions, formed fascia, and moving-bed leaf contact

The latest complete scene is `factory-truck-v14.glb`,8,068,768bytes(7.69MiB).
It supersedes v11/v13. Native source is `factory-truck-v14.blend`.
`refine-fondfont-truck-v14.py` and `fondfont-truck-cab-v12.py` build a thinner,
flatter roof and taller/wider real windshield and side apertures. The grille,
stacked lamps, wrapped bumper and door handle now fit the shell surface;
continuous thin door seams, inner arch returns and correctly faced mirrors
replace floating trim. Steering wheel spokes/hub share the tilted ring’s
transform. The original symbol is the sole cab-roof mark; side cab branding
is absent. Original imagegen reference/optics pixels are unchanged.

`refine-fondfont-truck-optics-v14.py` assigns the unchanged whole optic source
to native bowed lenses. No raster repaint, source cropping or new art synthesis
was used. `truck-v14-{reference,three-quarter,side}.png` are actual Cycles studies.
`truck-v14-web.png` is a development close camera; portal clipping is designed
for the normal hero camera, so the debug close view is not a full architecture
acceptance image. This is a substantially revised web model, not photographic
parity with the imagegen source. No paid or free donor truck was acquired.

Final mesh contact checks preserve21attachments, sixwheel pivots, steering,
moving side gate, loading clearance and full two-cycle choreography. Decoded
tire floor range remains−0.000006425..+0.000061097m. Native loading bay and
forklift checks pass. Seven full2560×854 public posters now showv14 and the
production-compatible native pet rig, without pre-cropping. Export metadata:
`posters-v14.json`. TypeScript and the52-page Astro build pass.

### Tree leaves on the flatbed

User clarified “书页” means tree leaves. The original imagegen wind-leaf
texture is reused unchanged. A fixed40Hz simulation checks actual downward
crossings of the deck plane against the moving/turning/drifting truck at the
crossing time. Only exposed deck space can capture a leaf; rails/cab and loaded
cargo footprint are excluded. A captured leaf settles in0.22s and stores its
truck-local position/heading. Rendering uses the exact frame-time truck pose,
so it stays on the bed through turns and drift. Its falling mesh is suppressed;
the later scheduled ground arrival cannot duplicate it. Grounded leaves are
never pulled upward. Ground accumulation and randomized wheel wakes remain.

`check-fondfont-leaf-litter.mjs` passes600s of accumulation/replay:119persistent
leaves,9carried in the bed,418wheel wakes,0.400m maximum ground-wake height.
All418checked wake landings move>0.3m with varied directions. Dedicated crossing
checks cover a leaf above the deck, inside/outside footprint, persistent carry,
heading rotation, no duplicates and no upward capture of ground leaves.


Completion review: `../fondfont-studio-turns-20261007/completion-advisor.md`.
No material blocker found for the local improvement; remaining reference
proportion/detail differences are acknowledged. Final actual normal-camera
page evidence: `hero-default-no-query.png`. `hero-v14-studio-default.png`
freezes90s and renderer metadata confirms1leaf carried in the bed. Final
TypeScript and52-page Astro build passed after the local studio-default edit.
