# FondFont campus v3: modeled buildings and truck, 2026-10-08

## Request

Reorganize the FondFont Three.js assets so they look refined and professional.
Blender models should faithfully reproduce the Codex imagegen material. Imagegen
material should be suited to modeling. Model complexity should stay balanced so
the web download stays small. Mid-task, the user added four requests: keep colors
vivid, make sure the perspective is correct (the warehouse roof looked wrong),
stay refined, and regenerate the truck's material and rebuild its model.

## What changed

- **Imagegen material made for modeling.** Codex `image_gen` (run through `codex exec`,
  see `scripts/assets/fondfont/blender-v3/imagegen/gen.sh`) produced 15 new images:
  - orthographic elevation sheets for the foundry, warehouse, truck and forklift;
  - five seamless tiles: brick, slate, corrugated cladding, asphalt and concrete;
  - four truck decals: wheel face, headlamp, tail lamp and grille;
  - two interior studies.

  The originals are byte-identical copies. `provenance.json` records the source path,
  SHA-256 and prompt file for each image.
- **Buildings are modeled.** The projected full-image paintings and their invisible
  shadow and occluder proxies are gone. `scripts/fondfont-architecture-v3.py` builds:
  - the brick foundry: recessed steel windows, limestone quoins, sills and cornice,
    four sawtooth bays with glazed lights, coped gables and a banded chimney;
  - the ivory warehouse: plum frame, canopy, dock bumpers, ribbon windows, and a
    phone roof that sits flush on the walls.

  Every surface is lit by the page sun and casts real shadows.
- **The warehouse roof overhang was reduced** (the user flagged the roof perspective; see `before-warehouse-roof-overhang.png` and `after-warehouse-roof.png`, pending the user's confirmation). The earlier slab overhung the walls by 18 cm
  at each side and was 28 cm thick. It read as a floating lid
  (`before-warehouse-roof-overhang.png`). It now follows the building outline with
  a 6 cm overhang and a 20 cm titanium band. `PhoneScreenGlyph` moved down with the
  screen.
- **The truck was rebuilt.** `scripts/fondfont-truck-v3.py` follows
  `truck-orthographic-v1.png`:
  - a cab-over cab with a front wheel arch and black arch liner;
  - a raked windshield, door window and shut lines, mirrors on arms;
  - a grille, headlamps and bumper with fog and indicator lamps;
  - a ladder chassis, a silver fuel tank on the road-facing side, and tandem mudguards;
  - three-section dropsides in charcoal with red frames, hinges and latches, plus
    the headboard and tailgate.

  All six wheels share one symmetric 48-segment wheel mesh with the imagegen wheel
  face. Rig pivots, the 0.435 m wheel radius, the 1.07 m deck, the gate hinge and
  all 21 attachment empties are unchanged.
- **Directory cleanup.** 16 retired GLBs/PNGs (about 93 MB) moved from `public/v/fondfont/blender-v2/` to the local `scripts/assets/fondfont/blender-v2/retired-public/`, so they are no longer deployed. The truck attachment baseline is snapshotted in `scripts/check-fondfont-truck-attachments.json`.
- **Colors stay vivid.** The paint is signal red with a clearcoat, the enamel is
  saturated plum, and the brick uses the imagegen albedo unmodified apart from
  resizing.
- **Perspective is consistent.** One orthographic camera now sees only real
  geometry. No painted perspective remains anywhere in the scene.

## Size budget

| | before (v14) | after (v3) |
| --- | --- | --- |
| Scene GLB | 7.69 MiB | 2.47 MiB |
| Gzip transfer | 5.0 MB | 1.42 MB |
| Embedded images | 3.14 MiB | 0.47 MiB |
| Triangles (instanced count) | ~1.17 M | ~0.37 M |

Where the savings came from:

- Legacy native pets were removed. The runtime discarded them, but they were
  still downloaded.
- Identical meshes are now shared: type-sort columns, drains, forklift bodies and wheels.
- Type-sort glyph geometry was lightened by planar dissolve plus 45% decimation.
- Butterfly and garden meshes were simplified.
- Tileable 512 px textures replace 1254 px paintings, and normal maps were dropped.

The interior backdrop studies are not shipped. From the fixed camera at 33° the
doorhead sight line meets the bay floor about 2.5 m inside the door, so the bay's
back wall at 4.4 m is never visible.

## Verification

All of the following passed:

- `check-fondfont-three.mjs`, `-truck-rig.mjs` (tyre contact −0.004 to +0.93 mm),
  `-stacker-rig.mjs`, `-loading-bay.mjs` (rewritten for the modeled sawtooth bays),
  `-leaf-litter.mjs`, `-page-sun.mjs`, `-hero-assets.mjs`, `-pet-release.mjs`,
  `-studio-pets.mjs` and `-model-transport.mjs`.
- `npm run build`: 52 pages.

TypeScript shows only the two errors that already existed in the local prototype
folders. Seven 2560×854 posters were refreshed at scene time 12.8, just before a final 1 cm trim of the hidden-side mudguards. At poster scale that trim is under a pixel. Browser
evidence is in this folder, captured as full-resolution canvas reads. A 375 px
mobile view was checked visually.

## Rebuild

```sh
python3 scripts/prepare-fondfont-textures-v3.py
blender -b --python scripts/build-fondfont-campus-v3.py
scripts/compress-fondfont-campus-v3.sh
```

## Limits

- The scene is a stylized web miniature, not a photoreal match of the imagegen sheets.
- The forklift keeps its existing native model; it was already real geometry.
- The truck interior is opaque smoked glazing; seats are not modeled.

## Follow-up: perspective lens (reverse-perspective fix)

The user reported that both roofs looked wrong: far edges appeared as large as or
larger than near edges. The cause was the orthographic camera. It renders parallel
edges at equal length, which the eye reads as reverse perspective.

- **New lens.** `src/lib/fondfont/campus-camera.ts` replaces the orthographic camera
  with a physical perspective lens. The lens keeps the same 33° view axis, sits
  52 m from the framing target, and its vertical field of view is solved per viewport
  (13–17° in the tested layouts), so it behaves as a long lens without fisheye.
- **Framing.** The field of view is solved so that the projected outer curb exactly
  matches the page's road width. Measured: 1020/1020 px on desktop and 350/350 px
  on mobile.
- **Sky above the scene.** The header sky inset uses a vertical lens shift
  (`setViewOffset`), so the lens itself never moves.
- **Updated for the perspective lens:**
  - Page sun: the ray through the icon pixel now meets the ground.
  - Loading bays: each fragment traces its own line of sight through the door plane.
  - Chimney smoke: the volume is ray-marched along a per-pixel view ray.
  - Leaf spawn line and smoke blur: both use the lens projection.
- **Results.** Roofs and the road now foreshorten naturally, with near parts larger
  and far parts smaller (`orthographic-vs-perspective-roof.png`). The inner side
  walls of both buildings become visible.
- **Checks.** The sun check now runs against the production lens; parallel sunlight
  converges slightly in perspective, with minimum bearing agreement 0.9976. The
  loading-bay check verifies the per-fragment sight line. All other checks and
  the 52-page build pass.
- **Posters.** All seven posters were re-rendered through the perspective lens with
  headless Chrome (`scripts/capture-fondfont-scene.mjs`).

## Rule: the page sun is the light source on every width

The small sun at the top left of the page is the scene's only directional light.
`syncSun()` re-solves the light whenever the sun icon, the canvas or the top bar
changes size, and on every rendered frame.

To verify, one live page was resized in place in headless Chrome, without
reloading, through 1440 → 1180 → 960 → 768 → 560 → 390 → 1440 px
(`sun-resize-perspective.json`, `sun-resize-perspective.jpg`). At every width:

- the light's ground bearing projects onto the sun icon to within 0.02 px;
- the screen direction of the shadows equals the direction from the icon to the
  scene (agreement 1.0);
- returning to 1440 px restores the identical light position.

`check-fondfont-page-sun.mjs` covers four layouts with the production perspective lens.

## Warehouse roof and drifting multi-typeface glyphs

- **The roof reads as a roof.** The phone slab now has eaves: 28 cm at the ends,
  25 cm at the front and 20 cm at the back. Its titanium band is 26 cm deep and casts
  an eave shadow on the facade. The sign and canopy moved down to stay below the
  line of sight past the eave.
- **Twelve classic glyphs per locale** are laid flat on the screen
  (`src/lib/fondfont/roof-glyphs.ts`), for example 永字爱书风和美文道光山水,
  あいろはアカ永字の書和夢, 한글봄가나다꽃빛사랑별길, and A Q a g ß ä ö ü & for German.
  The previous version showed three fixed characters.
- **Brownian drift.** Each glyph wanders within its own cell. Its offset, rotation and
  scale are sums of sinusoids whose amplitude falls as 1/frequency (the Brownian
  spectrum). Because the motion is a pure function of time, posters, reduced motion
  and resumed playback all reproduce exactly. Cells are clamped so a glyph's ink
  never leaves the screen or covers the camera island.
- **Many typefaces, none fixed.** Each locale has a pool of 5–7 licensed typefaces
  in contrasting styles: serif, script, rounded, brush, handwriting, mono and
  display. `prepare-fondfont-roof-fonts.py` admits a typeface only if it covers all
  twelve glyphs, subsets it to WOFF (36–60 KB per locale) and publishes its licence
  in `/v/fondfont/fonts/licenses/`. The runtime loads only the current locale's pool.

  Every glyph changes typeface on its own 6–11 s rhythm, cross-fading over 1.2 s.
  It never repeats the same typeface twice in a row and cycles through the whole
  pool. Glyph placement, the two red accents and the typeface order change on every
  visit; poster and shot modes use seed 47. Each typeface is normalised to the same
  ink extent, so small-on-body fonts read at an equal size.
- **Verification.** `check-fondfont-roof-glyphs.mjs` covers:
  - every locale has twelve glyphs and at least five distinct typefaces, with all
    font and licence files published;
  - a typeface never repeats consecutively and each glyph visits the whole pool
    (2,139 checked changes);
  - over 600 s, glyph ink stays inside the screen;
  - motion is deterministic, calm (at most 7 mm per 0.1 s) and keeps wandering;
  - layouts differ between seeds.

  All other checks and the 52-page build pass. Seven posters were refreshed. The
  former single-font `roof-*.woff` files are retired from public.

## Download budget pass (cat, leaf, dust, install screenshots, icon)

Measured as cold transfer from the production build: headless Chrome with the cache
disabled, summing each request's encoded bytes, over the whole page including the
installation guide.

| Page | Before | After |
| --- | --- | --- |
| zh-hans desktop, 1440 px | 9.59 MB | 3.47 MB |
| en mobile, 390 px | 7.17 MB | 3.52 MB |

| Asset | Before | After | How |
| --- | --- | --- | --- |
| Scene model (gzip) | 4,929 KB | 1,391 KB | Modeled campus v3 (above) |
| Calico cat (gzip) | 2,962 KB | 1,314 KB | `cat-v2.glb`; see below |
| Falling leaf sprite | 991 KB | 11 KB | 256×384 lossy WebP with alpha, premultiplied resampling |
| Drift dust sprite | 409 KB | 30 KB | 768×384 lossy WebP with alpha |
| Installation screenshots (4 per locale) | ~2,750 KB | ~115 KB | 600 px WebP inline, 1000 px WebP for zoom |
| Header icon + favicon | 2×174 KB | 4 KB + 7 KB | 128 px WebP header, 64 px PNG favicon |

**`cat-v2.glb`** (`scripts/build-fondfont-calico-cat.py`) bakes the original cage
without subdivision: the body has 1,652 vertices instead of 8,678, and each eye 507
instead of 2,356. It also keeps every other combed parent strand: 576 of 1,151, a
little thicker to compensate. All 84 morph targets, paw markers and the groom
binding are regenerated from the native rig, and paw contact error stays at the
0.0001 mm level. A 5× close-up shows a smooth silhouette, coat pattern, eyes and
whiskers.

**Sprites.** The leaf and dust sprites derive from the retired v1 originals via
`scripts/prepare-fondfont-effects-v2.py`. The byte-exact lossless check was replaced
by size, alpha and fidelity checks: alpha error under 3/255 against a Lanczos resize
of the original.

**Installation screenshots.** The captures remain the genuine Argent PNGs (in
`install-capture-20261007/`); `scripts/prepare-fondfont-install-webp.py` only
scales and encodes them. `install-screenshots.json` records every web copy.

**Retired files.** `cat-v1`, the v1 sprites and the install PNGs are no longer in
`public/`.

**Roof glyph spacing.** A live load showed neighbouring glyphs touching. Drift and
size are now bounded so that neighbours can never overlap; the check asserts a
positive gap over 600 s for two seeds (minimum 8.7 cm).
