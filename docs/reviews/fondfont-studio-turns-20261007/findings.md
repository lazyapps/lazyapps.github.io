# Original studio pets: forward walking and supported turns — 2026-10-07

## Current preview

Ordinary local FondFont routes now use the selected original Autumn dog and
Domestic Cat by default. `pets=studio` is no longer required. The production
publication boundary is unchanged while the cat author’s web distribution
permission is unresolved; this is explicit, not an unnoticed production switch.

The original professional surfaces, UV coats and 3D parent groom remain.
Autumn’s yellow material remap, original eyes/scarf and independent tail wag
remain. No animal reference image is pasted onto a replacement body.

## Native poses and contact

`scripts/refine-fondfont-studio-turns-v3.py` extends the original saved trial
Blender files. Each mesh has 84 morphs: 20 native walk, 20 left pivot, 20 right
pivot, 2 tail, 2 head, and 20 native foot correction poses. The cat’s downloaded
still pose is reset to four-foot support before baking. Native 60-degree turn
samples include the exact stance edges; finite ±0.6 radian paw-heading poses
replace the old infinitesimal yaw correction that visibly stretched toes.

`studio-pet-locomotion.ts` advances gait only from accepted forward displacement
and absolute yaw change. World-space toe/heel/lateral anchors hold each planted
sole; timed quintic swings complete even when a turn stops. A new paw lift
always leaves at least one support foot. Three decoded sole points are fitted
jointly to the native correction basis. The body root remains upright; yaw
turning does not rotate the body up/down. A clock seek resets contact history,
preventing stretched geometry on frozen `sceneTime` previews.

Navigation translates in its facing direction, including yielding. Goals and
portal reservations allow two pets to pass without reverse walking or becoming
permanently stuck. Random territory and existing behavior selection remain.
This trial still does not have full bespoke source-rig play/sniff/potty poses;
those navigation states do not imply complete action parity.

## Evidence

- `turns-accepted.mp4`: actual 7.22-second browser walking and wag capture.
- `dog-turn-native.mp4`: actual 7.93-second browser turn, scene clock starts31s.
- Raw JPEGs and actual frame timestamps remain in corresponding frame folders.
- `accepted-frames/0020.jpg`: both original source animals in the web renderer.
- Numerical tests decode the delivered GLBs, rather than relying on source rigs.

## Validation

`check-fondfont-studio-pets.mjs` passes native walk/left/right pivots, starts/stops,
four seeds at60Hz, and seed47 at30/120Hz. Maximum planted sole slip is1.04mm;
maximum sole-edge length change2.25mm. Maximum native correction displacement
is0.338m; this is a regression bound, not an anatomical reach certificate.
Maximum normalized60Hz vertex step is23.6mm. Actual lowest source skin remains
within1.6mm of ground. Contact corrections improve turning but do not claim
motion-capture realism.

`check-fondfont-three.mjs` passes four600-second navigation histories, forward
translation, swept body/flower/building clearance and continued progress.
Territories span7.10–7.44m; no reverse walking is used. TypeScript passes.

Approach reviews: `approach-advisor.md`, `contact-diagnosis-advisor.md`.
The timed contact schedule, finite native yaw basis and final decoded-sole tests
follow those reviews. The correction basis is shared across gait phases; it is
not a new full native armature solve in the browser.


## Completion review

`completion-advisor.md` found no material blocker in inspected native truck
images, sampled professional pet turn frames, or leaf capture/rendering code.
Its limits are adopted: sampled pet contacts do not establish anatomically
correct motion in every turn; truck refinement does not equal reference-photo
parity; a complete visible leaf landing-and-carry sequence was not independently
reviewed. The final unchanged52-page Astro build and TypeScript check passed
again after the local-default change.

`../fondfont-cute-truck-20261007/hero-default-no-query.png` is the actual ordinary
German local page, URL `/fondfont/de/`, verified ready with both original trial
GLBs loaded and no query parameters. `hero-v14-studio-default.png` freezes90s;
its actual renderer reports18persistent leaves,1on the moving deck,22wakes.

The user asked whether a footer statement resolves publishing the cat. Official
Blendkit licensing FAQ was checked on2026-10-07: attribution does not remove the
requirement that distributed models not be easily extractable. No new author
permission was supplied. The local default remains active; production distribution
remains explicitly unresolved. Cat capture in `cat-turn-frames/` is a short
incomplete diagnostic, not an accepted turn-motion recording.
