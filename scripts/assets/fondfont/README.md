# FondFont production sources

The repository contains the website, reviewed public web assets, build/animation
scripts, review reports and selected previews. Full Blender scenes, downloaded
character packages, intermediate GLBs, source videos and frame caches remain
local and are ignored. No local files are deleted by this arrangement.

`AppIcon.icon` and `brand-source.json` retain the original brand geometry and
export provenance. `pets/calico-cat/provenance.json` and its original license
identify the source of the public CC BY 3.0 cat; full attribution accompanies
`public/v/fondfont/pets/cat-v1.glb`. The retired BlenderKit trial cat is local
only and must not be published as an extractable model.

`optimized/manifest.json` records hashes and sizes of the lossless web assets.
`npm run build` needs only committed public GLBs/PNGs/WebP, regenerates gzip
copies, verifies byte/pixel/profile equivalence, then builds the Astro site.
The Blender export scripts and original-source checksum checks require the
corresponding local production sources. Regenerating lossless effect images
also requires cwebp: `node scripts/prepare-fondfont-hero.mjs --images`.

Font license texts accompany the public subsets in
`public/v/fondfont/fonts/licenses/`.
