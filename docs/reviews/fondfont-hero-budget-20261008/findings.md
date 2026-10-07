# FondFont hero: lossless delivery and two cats

The default scene now contains the original calico cat and a visibly charcoal-colored instance. The dog is removed from runtime and public assets; its original source remains private. Both cats share one decoded geometry/texture set and one model request, with separate morph weights, root transforms, coat materials, gait phases and navigation actors. Original eyes remain unchanged. Existing navigation actor keys retain their historical dog/cat names internally; neither rendered actor is a dog. Cat attribution and adaptation notes are updated in all seven locales.

## Download result

Cold production preview, cache disabled, German locale, counting hero GLBs, effects, sign/roof fonts, poster and the two scene JavaScript chunks; excludes installation screenshots, shared page CSS/fonts/icon and HTML. Decimal MB, response bodies rather than request headers.

| Budget | Before | After |
|---|---:|---:|
| Encoded response bodies measured in Chromium | 19,681,479 B | 9,930,460 B |
| File-size budget, assuming uncompressed JavaScript | 20,230,678 B | 10,480,177 B |

Measured response-body reduction: **49.54%**. This is a production-build preview measurement, not a deployed GitHub Pages measurement. JavaScript is HTTP-compressed by the preview server. The ~10.5 MB file budget does not depend on JavaScript HTTP compression. Seven locales vary slightly with localized posters/fonts.

Current models: main 8,068,768 B -> gzip 5,046,909 B; single cat 3,791,224 B -> gzip 3,032,692 B. The 4,987,908 B dog request is gone. Two cat instances add no second model request.

Effects: leaf 1,703,761 B -> 1,014,522 B; dust 660,406 B -> 418,826 B. `cwebp -lossless -exact -metadata all -m 6` preserves all RGBA channels, including transparent pixels. Original PNGs remain available as source evidence. Both originals and WebP have the same sRGB space and no ICC profile. Actual WebGL texture upload/readback in the browser reports **zero differing channels** for both effects (`webgl-texture-equivalence.json`). A Canvas2D round trip initially showed transparent-edge premultiplication rounding; direct GPU upload, matching Three.js's non-premultiplied texture path, resolved that distinction.

## Delivery and build

`model-bytes.mjs` requests pre-gzipped GLBs when native DecompressionStream is available. It accepts both gzip bytes and a GLB already decoded by HTTP Content-Encoding, then validates GLB magic, version and declared length before parsing. It propagates cancellation. `model-loader.ts` checks cancellation after asynchronous parsing and disposes stale parsed resources. Unsupported browsers request the original model directly; corrupt/missing compressed resources never silently trigger a second full download. Existing poster fallback remains available.

The production preview actually returns Content-Encoding:gzip for .glb.gz; the already-decoded branch is exercised by real scene loads. The browser-native manual-decompression branch was also exercised on the actual cat bytes through a synthetic Response fixture: 28.9 ms, matching source/decoded SHA-256 ef1c3974d9cf9e1cc1167ca6da00fecd6abcae37f59e4e2e2847fedc70439f8d. This is a desktop sample, not a physical-mobile decompression benchmark.

`npm run build` regenerates deterministic gzip copies from current originals before Astro builds, preventing stale compressed assets after model updates. `node scripts/prepare-fondfont-hero.mjs --images` explicitly regenerates the two lossless WebP encodings when source images change; cwebp is needed only for that maintenance command. Output sizes and source/output hashes are in `scripts/assets/fondfont/optimized/manifest.json`. No new dependency was added.

Sparse/extra-quantization trials were rejected: their raw files were mostly larger, and the default transform wrapper changed more attributes than the intended experiment. They are not shipped. No model precision, topology, UV, morph, grooming, original texture, or animation data was reduced in this release. A charcoal material shader is an intentional user-requested appearance change, separate from compression.

## Verification and practical limits

- Byte-exact gzip round trips; source hash unchanged. Pixel/profile-exact effect encodings plus direct WebGL readback.
- Gzip, HTTP-decoded payload, absent DecompressionStream, corruption, cancellation and single-request failure tests pass.
- Two-cat checks verify shared geometry and independent morph/material state. Unchanged contact thresholds pass across 4 x 120-second navigation runs, sustained left/right pivot/stop, curved forward motion and 30/120 Hz runs: maximum planted slip 1.458 mm, sole-edge error 0.584 mm, reach 0.314 m.
- Scene/forklift/garden navigation and persistent/wind-carried leaf checks pass. Original-source license and restricted-cat exclusion checks pass. Focused TypeScript check and 52-page production build pass.
- All seven complete 2560 x 854 posters were re-rendered with the two cats; no scene pre-cropping. `two-cats.png` is a development close view, `two-cats-live.webm` is 9.78 seconds of actual animated canvas capture, not a generated storyboard.
- Desktop cold baseline was initially ~1.3 s. Later system/browser contention changed timings substantially. Same-version controls under that later load: compressed median 8.014 s vs raw median 7.902 s (3 runs each), within the run-to-run spread. Do not infer an end-to-end speedup from these local samples. Byte savings are stable across every measured run. Raw control verifies both models load once from .glb when DecompressionStream is absent.
- 390 x 720 viewport emulation: canvas 585 x 378, 120-frame mean 27.92 ms, p95 41.7 ms, cold readiness 10.60 s under the later load. This is desktop Chromium emulation, **not a physical phone test**. No frame-rate or startup improvement is claimed.
- Transport preserves decoded model memory; compressed and decompressed buffers can overlap temporarily. Removing the dog and sharing cat geometry reduces duplicated animal data, but sampled JS heap is GC-sensitive and is not a reliable GPU/peak-memory measurement.

No commit, deployment or remote publication was performed. Port 4332's existing dev server is retained; the temporary 4333 preview and test tabs are closed after verification.

## Independent review disposition

Approach and transport consultations endorsed lossless-first delivery; no quantization trials were shipped. Final completion review found no blockers. Its nonblocking stale-image concern is addressed: `npm run build` now runs the existing model-byte/image-pixel/profile equivalence check after preparing transport files and before Astro. A changed PNG with a stale WebP fails CI/build until its derivative is regenerated. Physical-mobile startup testing remains a documented follow-up, with no mobile performance gain claimed.
