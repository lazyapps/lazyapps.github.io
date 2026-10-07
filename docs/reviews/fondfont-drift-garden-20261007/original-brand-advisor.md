Geometry and truck-roof routing pass: original paths, transforms, full 1024 viewBox, and rear/front order are preserved; the roof loads the flat SVG.

One concrete violation: [FondFontPage.astro:8](/Users/realazy/Projects/Sites/lazyapps/src/components/FondFontPage.astro:8) currently imports `fondfont-web-icon.png` for both header and favicon. The exporter generates that variant with modified front translucency, shadow opacity, and gradient alpha. It is **not the unmodified production export** described in the briefing.

Route both placements to the already-generated `fondfont-icon.png` to meet the stated requirement.