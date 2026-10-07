# Local professional pet trial and clean cab roof

The two selected free source models are downloaded and actually rendered in the
Three.js hero: Autumn from Blender Studio and Paweł Wałasiewicz's Domestic cat
from BlenderKit. Source provenance, licenses, hashes and rebuild steps are in
`scripts/assets/fondfont/pets/README.md`.

The approach advisor correctly warned that exporting bones alone would discard
Autumn's cage/lattice corrections. We instead evaluated the original native rigs
in Blender and baked real 3D vertex morph poses. No pet sprite or substitute body
is used. Original UV markings and parent groom shapes are retained. Simplified
groom density/shading does not reproduce the full original Cycles appearance.

## Delivered

- Local DEV-only `?pets=studio` preview in the existing hero camera/navigation.
- Sixteen native walk poses per model, distance-driven stride, backward playback
  for reverse travel, independent lateral dog tail wag.
- Source color bake fix: removed double-multiplied paint masks; explicit source
  UV selection restores Autumn's red neckerchief.
- Actual published trial geometry is finite; original body soles stay within
  1.6 mm of the floor across all samples. The source native paw solve is tighter,
  but does not substitute for browser review.
- `hero-trial.png`, `pets-close-up.png` and `pets-walk-trial.mp4` show the actual
  local browser result. Video is an eight-second continuous browser recording,
  not the source preview or an imagegen output.
- Production cab roof uses flat red enamel and the original transparent app
  symbol alone. Removed roof marker lamps and the textured paint panel. The
  physical roof bevel remains. Active complete asset: `factory-building-v6.glb`.
- All seven production fallback posters refreshed from the full 2560×854 canvas,
  using production pets, without pre-cropping.

## Remaining gates

This trial has straight walking and wagging, not the complete previous action
set. Dedicated turns, play, sniff and potty require further native posing and
visual acceptance before replacing production. Existing production pets/actions
remain the default. The cat's free Royalty Free download does not establish
extractable public GLB rights; no cat file is emitted to `public/` or `dist/`.
The local middleware is development-only. No creator was contacted and no
publication was performed.

## Validation

`check-fondfont-studio-pets.mjs` passes for the actual compressed geometry and
material graph. Existing loading-bay, forklift tire contact, choreography,
navigation, production pet-rig, responsive sun and persistent leaf-litter checks
pass. The 52-page Astro build passes. The recorded local browser had no warnings
or errors. These checks do not certify a final animation replacement or resolve
the cat's public asset license.

Completion advisor accepted the local-trial/production-roof boundary, while
requiring explicit delivery checks. Followed: the development server listens
only on 127.0.0.1 and middleware rejects non-loopback peers; production output
contains no trial assets or trial endpoint strings. An actual production browser
visit with `?pets=studio` requested only `factory-building-v6.glb` and the existing
`garden-life-rig-v5.glb`, with no trial-model requests and no console errors.
Both production trial asset URLs return HTTP 404. The focused TypeScript check
for the new animator and integrated scene also passed.
