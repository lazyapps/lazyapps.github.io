# Focused completion check: slogan and visual framing

Read-only review of these two recent changes only; the larger architectural refinement remains separate work. Do not pronounce the whole visual production complete or assess unrelated website changes.

Latest human requests:
1. Copy the exact sentence structure of Nongfu Spring’s Chinese slogan: “我们不生产字体，我们只是字体的搬运工。” Other languages should be idiomatic within a font courier metaphor.
2. The 3D loop is angled: compensate for its projected visual position so it looks centered in the webpage. Previous requirements: road extremities align with the content-container edges; plants extend outside naturally; narrow viewports clip through webpage overflow, not cropped source images.

Implemented:
- src/i18n/fondfont-locales.mjs: exact simplified/traditional Chinese structure, five locally idiomatic headline pairs from slogan-advice.md. Supporting paragraphs state users bring existing font files. Mobile Japanese/Korean can wrap naturally in FondFontPage.astro.
- src/lib/fondfont/blender-scene.ts: computes actual projected bounds of static Architecture geometry, omitting Garden and independent moving truck/cargo. Translates orthographic camera and target equally in the camera’s right/up plane by bounds center, preserving camera orientation. Uses analytical projected stadium-road width, including curb, to match content width. Min virtual width700 on mobile and webpage clips overflow. Removed mobile truck-following camera pan. ResizeObserver observes full-viewport stage and content host, including when content max-width stays fixed.
- Seven native full-canvas WebP posters re-exported using that same renderer at sceneTime9.5 (no image processing or pre-cropping).
- src/components/FondFontFactoryScene.astro: accessible descriptions distinguish independent foundry from delivery service.

Evidence: slogan-mobile-qa.json (all seven locales,320px, no horizontal heading overflow), framing-qa.json (1280/1440/1920/390; stage matches viewport and road width matches desktop content), slogan-build.log (52 pages built), existing scripts/check-fondfont-three.mjs physical checks pass.

One decision-focused question: do these implementation changes contain any material correctness or responsive framing issue that should block completion of the slogan/centering requests? Inspect the actual code and evidence, report only actionable issues in this scope. In particular verify camera-space translation and road-width calculation. No edit/delegation.
