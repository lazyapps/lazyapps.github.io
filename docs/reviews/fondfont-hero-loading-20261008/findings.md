# FondFont hero first-frame placeholder and loading — 2026-10-08

Seven localized posters now use the production renderer at `sceneTime=0`, with the same roof glyph seed (47) as live pages. Cats retain randomized later behavior; their initial poses are identical. Reduced motion uses frame zero as well.

The initial light is the original 1280px full-poster export light. After the 200ms poster handoff, light blends to the responsive page sun over 600ms. Smoke and airborne leaves also fade in over that interval because their sky extent depends on viewport height. Resizing renders the current scene time again. This keeps initial scene content consistent without removing the page sun or sky effects from subsequent animation.

Loading feedback is a prominent steering-wheel loader centered over the image, with a 64px, 50%-opaque circular background and no visible text. The three-spoke wheel steers between −40° and +40° every 1.6 seconds. Its accessible label is localized in all seven languages. It appears only while the visible scene is actually loading, clears on readiness/failure, and exposes busy state. Reduced motion keeps the loader without rotation. Save-data and no-JavaScript retain the static poster without a loading indicator. The animation clock starts after readiness.

Posters are full transparent 2560×854 exports, not crops. To refresh: run `scripts/capture-fondfont-scene.mjs` at 1280×900 for every locale with `?sceneTime=0&scenePoster`, then encode the PNGs with Sharp WebP quality 80 / alpha quality 100. Keep poster light and seed synchronized with the renderer.

Validation: production build (52 pages), existing sun and scene/motion checks, desktop/mobile browser captures, held and failed model requests, reduced motion, save-data, no-JavaScript, and an ordinary live-route readiness-clock check. Browser evidence is in this directory. Raster quality varies with the renderer's existing desktop/mobile pixel-ratio budgets; matching scene content does not imply byte-identical screenshots.

Advisor: adopted the approach review's shared initial-light recommendation. The clock was already anchored to readiness and was verified with an artificially held model request. Sky-effect staging additionally addresses the observed smoke/leaf difference between the full export and the taller live canvas.

Completion advisor found no blocking correctness or scope issue. Its remaining condition was the final build and post-refinement browser checks; both passed, including the production preview. No implementation changes were needed after that review.
