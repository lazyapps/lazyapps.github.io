# FondFont: Blender / Three.js looping hero

Latest user direction: preserve the original continuous transport cycle, improve asset craft; use local Blender for actual spatial geometry and imagegen for all raster art/materials. Native 3D geometry and exact typesetting provide rotation, perspective and language consistency. No hand-drawn replacement images, image cutouts, sprite angle atlases, raster recoloring or collage are used by the current renderer.

## Durable deliverables

- `scripts/assets/fondfont/blender-v1/factory.blend`: editable Blender scene, packed original imagegen textures, camera and lighting for inspection.
- `scripts/build-fondfont-blender.py`: reproducible model generator. Blender axes map to Three X/Y-up/Z without runtime compensation; evaluated bevels and normals export to GLB.
- `scripts/export-fondfont-blender.py`: texture material attachment / export of existing native model. Original generated pixels retained. Normal maps are separate imagegen outputs.
- `public/v/fondfont/blender-v1/factory.glb`: 6.44 MiB, 354,686 triangles. Meshopt geometry compression preserves all named assembly pivots. Native export uses WebP image encoding, without cropping, repainting, compositing, tinting, or modifying the generated surface artwork.
- `src/lib/fondfont/blender-scene.ts`: Three renderer, native localized lettering, wheel steering/rolling, crane bridge/spreader/cable poses, physical shutter occlusion.
- `src/lib/fondfont/motion.mjs`: deterministic 32-second cycle; analytic road route and wheel path lengths, explicit supports and occluded inventory replacement.
- `public/v/fondfont/blender-v1/poster-{en,zh-hans,zh-hant,ja,ko,fr,de}.webp`: original browser canvas exports at transport time9.5; no headline, CTA or removed caption baked into fallback.

## Imagegen materials

The eight raster materials were requested as complete usable files from built-in imagegen, inspected and copied into the workspace. Their original sources, exact prompts and provenance are in:

- `scripts/assets/fondfont/blender-v1/materials.json`: brick, oak, sage steel enamel, asphalt, limestone diffuse images.
- `scripts/assets/fondfont/blender-v1/normals.json`: brick, oak, limestone OpenGL normal maps, generated from the corresponding full diffuse reference.

Full original PNGs are siblings of these records. Browser encoding is an export-format optimization only. No new texture pixels are drawn by scripts. Text on signs is live typesetting using the seven existing localized WOFF subsets. Cargo metal glyphs are mesh conversions of the earlier session's exact font contours, `src/lib/fondfont/glyphs.json`; original font provenance remains in the v15 cargo manifest. All locales share the same multilingual cargo.

## Narrative and physical contract

A foundry creates multilingual metal type. Its crane locks onto a rigid wooden pallet, lifts, traverses to the truck and lowers onto the deck. The truck drives along the front road; the second crane unloads the same pallet onto the receiving conveyor, which carries it inside the font-library warehouse. The empty truck follows the right bend, rear road and left bend back to the foundry. A fresh batch emerges from behind the foundry shutter before the next load.

The rear axle center follows the analytic stadium curve, heading follows its tangent, independent wheel rotations use the distance of each contact point, and front wheel steering follows the turn radius. All six contact points remain within the road. Cargo dimensions, bed height, receiver height, crane lifting clearance and twistlock sockets share model coordinates. The inventory reset at26.4 occurs with both physical shutters closed and both pallets inside their buildings. At32 seconds positions and poses match the start; wheel rotation continues monotonically through successive cycles.

The camera is fixed at all viewport widths. Its target uses the actual campus geometry projected into camera space, excluding freely growing plants and the independently moving truck/cargo. The projected road width matches the content container on desktop. Narrow viewports retain a centered700px virtual composition and let the webpage hide horizontal overflow. The camera no longer follows the truck.

## Page and fallbacks

Animation precedes centered headline, description and CTA. No status/caption/arrow strip; no one-shot replay control. Existing product truth and installation information preserved. Foundry and iOS library labels follow the page locale. Truck naming is restricted to the horizontal upper surfaces; vertical side-panel naming has been removed.

Animation pauses out of view / while hidden. Reduced motion, save-data, missing WebGL or model-load errors retain the localized static artwork. Model resources are disposed when a page leaves, including fonts, texture maps, geometries, materials and environment. Large scene code/model load lazily; posters remain the initial content.

## Validation

`node scripts/check-fondfont-three.mjs` checks physical supports, crane clearance, every wheel contact throughout the whole return path, closed-door replenishment, phase-boundary continuity and two-cycle wheel continuity. It also validates the compressed GLB's animation pivots, normal textures and8MiB size budget.

Standalone TypeScript check of the scene passes. Browser stills have verified loaded transport, empty right turn and rear return. Remaining final checks: all handoffs, mobile viewport, all locale layout, live two cycles, fallbacks, build and independent completion review.

Latest framing requirement: keep the complete scene/model and full-frame source imagery; do not prepare device-specific cropped assets. Desktop overview and all static exports use the complete campus. Narrow-screen framing is computed live by the webpage's Three camera, without editing or cropping any source image.

2026-10-07 framing revision: ResizeObserver now observes the full-viewport stage as well as the content container, including resizing above the container's maximum width. Seven whole-canvas v2 posters were re-exported from the actual Three renderer at9.5 seconds,2560×854. Their CSS sizing uses the export's1052/1280 projected road-width ratio, preserving the same container alignment and center for static fallbacks. Overflow is clipped by the webpage, without modifying raster source content. Checks recorded in framing-qa.json and framing-poster-qa.json.

Latest slogan: “我们不生产字体，我们只是字体的搬运工。” Chinese retains the sentence structure explicitly requested by the human; other locales use idiomatic delivery language. Supporting paragraphs describe font files the user already has. Focused localization advice and decision are in slogan-advice.md and slogan-decision.md.

Actual continuous browser playback reached94.937 seconds (nearly three complete32-second cycles), with the scene ready and no horizontal overflow. Conveyor support was extended into both buildings; archive cabinets moved clear of the receiving pallet. Both source generator and editable Blender model retain these physical fixes.

## Final refinement validation

The current v2 native scene adds true arched openings to a taller terracotta foundry, integrates the foundry fascia into the entrance, and removes all foundry identity anchors. Rounded library walls share the iPhone roof’s perimeter, with a consistent0.16m overhang and no separate coping; the building moves0.15m rearward to clear crane tracks, and archive cabinets remain inside its shallower interior. Actual supplied icon is flush on the cab roof; generated monochrome attempts with stray pixels were rejected without manual cleanup. New complete imagegen clover/pink-petal/terracotta originals and architectural reference have durable prompts/provenance.

The idle spreader parks at4.4m below the beam so its front locks do not obscure the foundry name. Supported lift/dock poses and locking phases remain unchanged and physical checks pass. Planting is excluded from the ambient-occlusion normal override to avoid rectangular alpha-card halos; native alpha-tested leaf/petal geometry remains in the beauty/shadow render.

Final model:6.50MiB. TypeScript check, physical checks and all seven localized font coverage assertions pass. Astro builds52 pages. Actual live scene reached151.662 seconds, ready and visible, covering four complete32-second cycles. Final pose snapshots cover5.7,14.3,20,25 and28.5 seconds. Initial reduced-motion load at320px has poster opacity1, no ready canvas, and document width320; emulated preference-change events were not considered evidence because this browser backend did not dispatch the existing media-query listener. The standards-based listener remains in the implementation. Final independent review found no delivery blockers; `final-native-review.md` explicitly assessed actual renders, not the generated reference.

## Horizontal loop + imagegen library, 2026-10-07

Latest user direction supersedes the diagonal/native-block presentation. Camera yaw is now zero; front and rear road sections are horizontal, and the analytical road span still equals the page content width. The app's cab roof now uses imagegen's flat scarlet/ivory linked ff graphic on plum, with a matte print material.

Imagegen directly redrew the complete font-library architecture at the horizontal camera angle. Its original full RGBA image is stored unchanged as `scripts/assets/fondfont/blender-v2/library-horizontal-v1.png`. Blender maps the same world-to-image projection across roof, facade, recessed archive backing and ground-level loading floor. Native animated shutter/conveyor/crane/cargo retain depth. No source crop, repaint, raster cleanup or image compositing was performed. The original full-image UV range is retained, including alpha margins; webpage overflow handles scene clipping.

Advisor `horizontal-advice.md` supports this integration provided artwork, opening, shutter and disappearance boundary share one locked projection. Source landmarks and native geometry use that projection. The receiving pallet stops at z=-0.85 inside the new recessed interior, before its archive wall. All seven localized fascia labels remain native typography. Raster provenance and exact built-in imagegen prompts are recorded in `scripts/assets/fondfont/blender-v2/horizontal-imagegen.json`.

Horizontal revision validation: model6.32MiB; standalone TypeScript, physical supports/clearance/continuity and52-page Astro build pass. Browser pose proofs cover5.7,14.3,20.5,21 and25 seconds. Seven full-canvas localized posters were re-exported from the new actual renderer. Framing metrics at320/390/767/1280/1440/1920 show zero document overflow and exact desktop road/content alignment; reduced-motion initial load at320 uses the new localized poster with opacity1 and no ready canvas. The backend's raw screenshot did not accurately represent its emulated mobile viewport, so that screenshot was discarded and no mobile screenshot proof is claimed. Independent `horizontal-final-review.md` inspected the six actual browser stills, fallback and source and found no material delivery blocker. Final production preview without Astro's dev toolbar: `horizontal-production.png`.
