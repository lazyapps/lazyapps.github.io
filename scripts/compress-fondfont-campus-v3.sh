#!/bin/zsh
# Compress the raw v3 Blender export for the web. Node names are preserved
# (no flatten/join/instance); meshopt with 16-bit positions.
set -e
ROOT=${0:A:h:h}
GT=${GLTF_TRANSFORM:-npx -y @gltf-transform/cli@4.5.1}
V3=$ROOT/scripts/assets/fondfont/blender-v3
eval $GT dedup $V3/campus-v3-raw.glb $V3/campus-v3-dedup.glb
eval $GT meshopt $V3/campus-v3-dedup.glb $ROOT/public/v/fondfont/blender-v3/campus-v3.glb --quantize-position 16 --quantize-texcoord 14
node $ROOT/scripts/prepare-fondfont-hero.mjs
