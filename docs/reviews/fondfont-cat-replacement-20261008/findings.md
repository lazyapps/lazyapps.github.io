# Licensed default pets — 2026-10-08

Replaced the restricted private BlenderKit cat with the user-downloaded
**Rigged and animated Cat** by **JonasDichelle**. The supplied original license
explicitly says **CC BY 3.0 Unported**. The original source and license are
preserved unchanged with SHA-256 in `scripts/assets/fondfont/pets/calico-cat/`.
The current asset page is https://blendswap.com/blend/18519; its package uses
the legacy URL http://www.blendswap.com/blends/view/86110.

## Result and source fidelity

- Public `cat-v1.glb`: 3,791,224 bytes, four original evaluated surfaces
  (body, two eyes and original groom), 84 named native morph poses each.
- Original subdivision-1 skin and packed 1500px calico coat painting retained;
  original eye color graph evaluated with native Blender emission baking.
- 1,151 combed parent strands converted into tapered 3D geometry. Each strand
  is attached through its nearest source triangle's complete deformation frame,
  including local orientation and deformation, rather than vertex translation.
- The two obsolete dependency loops (Tail COPY_ROTATION and Spine PIVOT to
  their own child chain) are removed only in the derived source. Merely muting
  them left dependency-cycle warnings, so the derived constraints are removed.
- Native paw controls are calibrated against each actual skin sole and adapted
  to grounded walk, left/right pivot and plant-correction poses. This is an
  adaptation of the original rig; the authored Walk action is **not** exported
  unchanged. No new animal geometry or coat painting was invented.
- Autumn's v3 source export is copied byte-for-byte to public `dog-v3.glb`:
  4,987,908 bytes. Its existing yellow coat shader and independent tail wag stay.
- Professional pets now load in both development and production by default.
  No query parameter, DEV-only branch or private serving middleware is needed.
  The old BlenderKit cat remains outside public and deployed output.
- Seven complete 2560×854 WebP posters are refreshed with the same new defaults.

The original Cycles render uses dense child hair and a more complex hair shader.
The web groom remains lighter; this is not a claim of Cycles render parity.
Full bespoke sniff/play/potty poses are still not migrated to these professional
rigs. Their existing navigation remains, including broad forward-only roaming.

## Attribution

`FondFontAssetCredits.astro` supplies seven localized expandable footer credits,
with titles, authors, original sources, exact CC BY license links and modification
notice. `public/v/fondfont/pets/CREDITS.txt` supplies full derivative notices,
including the notice from Autumn's download page retained verbatim, and the
original cat license HTML is also public. No additional use restrictions or
endorsement claims are imposed on either CC BY adaptation.

## Validation

- `node scripts/check-fondfont-studio-pets.mjs`: actual decoded public meshes,
  native walk samples, left/right pivot and stop, curved forward start/stop,
  four random navigation seeds ×120 seconds at60Hz, and30/120Hz continuity.
  At least one support paw stays planted. Maximum planted slip **1.366mm**;
  maximum correction reach **330mm**; maximum sole edge distortion **0.584mm**.
  Existing5mm slip,25mm normalized frame jump,350mm reach and3mm sole distortion
  regression limits all pass without loosening thresholds.
- New cat's decoded native walk floor is **−0.870mm**, stable over20 samples;
  native IK target residual below0.0001mm. Existing dog floor remains about
  −1.59mm. No body pitching/rolling or reverse gait was added.
- `node scripts/check-fondfont-three.mjs`: source scene, forklift geometry and
  four navigation seeds ×600seconds pass. Roaming spans7.10–7.44m.
- Focused TypeScript check passes. `npm run build`: **52 pages**, success.
- `node scripts/check-fondfont-pet-release.mjs`: exact original source checksum,
  unchanged dog, original license copy, public/build asset equality, all seven
  locale credits/posters, and restricted cat absence in every deployed GLB pass.
- Actual production preview at4333 loads **dog-v3.glb** and **cat-v1.glb** with
  no query parameters and no development middleware. Footer attribution was
  expanded and inspected in German. `production-load.json` records this load.
- Browser native near-view recording: `native-pets-motion.webm`, actual9.815s,
  2560×1440, generated with canvas captureStream/MediaRecorder. `native-pets-closeview.png`
  and sampled recording views were inspected for markings, legs, shadows and
  turns. An earlier3-frame CDP screencast is not treated as motion proof.
- Both pets' decoded geometry buffers total64,827,332 bytes (~61.8MiB), before
  GPU morph textures and decoded images. Combined transfer assets8.78MB.
  Production page observed JS heap ~220.6MB (whole page, not pet-only).
- Desktop Chromium loaded at an emulated390×844 viewport, with585×378 hero
  backing canvas:120 requestAnimationFrame intervals, mean23.06ms and95th
  percentile33.40ms, scene ready (`production-mobile-timing.json`). This is a
  desktop browser observation, **not physical mobile-device benchmarking**.
  Local resource loading timings are likewise not representative network tests.

## Advisor

Approach review approved original native IK adaptation and required two fixes:
deformation-aware groom binding and decoded mixed-pose validation. Both were
implemented. Mobile hardware performance and full Cycles fur parity remain
explicit limits. See approach and completion advisor reports in this directory.

Completion review independently reran both pet checks and found no material
correctness, attribution or delivery blocker for the local production build.
No broader action parity, Cycles-fur parity or physical-mobile result is claimed.

No commit, push, deployment, account creation or paid asset acquisition performed.
