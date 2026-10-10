# Press Kit preloader

The homepage's existing logo/progress-bar markup is now a shared `SitePreloader.astro` component. The homepage preserves its existing styles and animation scripts. PressLayout renders the same component and reuses the same GSAP, CustomEase, SplitText, ScrollTrigger, logo-reveal and site lifecycle scripts. The hub shows LAZYAPPS; each App shows its English brand name. No extra captions or marketing text were added.

PressLayout starts with no-js, enables JavaScript in the head, and sets the initial theme color to the loader's ink. Normal animation restores the page's paper background/theme color and removes the overlay at about 3.6 seconds. Its head fallback restores content after six seconds even when animation dependencies fail. Existing CSS hides the overlay without JavaScript or with reduced-motion preferences.

Validation:

- `npm run build` passed: 71 pages, SEO checks, Shheep artifacts, seven Press Kits, 60 product landings and 57 App-language folders.
- Hub: Chinese hash is applied during the loader; after exit the language/picker remain Chinese, the overlay is removed, and background/theme-color return to paper.
- All seven Apps: a single visible loader with the correct brand, normal exit in 3.7–3.8 seconds including navigation/check overhead, Spanish entry language intact. Switching to Japanese after exit works and does not recreate the loader.
- At 320px, all eight Press Kit loader wordmarks fit and pages have no document overflow.
- Homepage still exits the extracted component normally.
- With emulated reduced motion, loader is removed immediately and traditional Chinese content remains active.
- With JavaScript disabled, no-js remains, the overlay is hidden, static English content is accessible, and the inactive language picker stays hidden.
- With GSAP and site lifecycle scripts blocked, the head fallback removes the overlay after six seconds and restores paper/theme color while preserving traditional Chinese presentation. All temporary browser emulation and request blocks were reset, and the QA tab was closed.

`checks.json` contains the browser measurements. `hub-animation.png` and `xvdl-animation.png` show frames during playback; `no-js.png` shows the accessible static fallback. The shared component and existing browser checks settle the integration without an additional advisor consultation.

Language-picker refinement: reduced the shared LanguagePicker's end padding from 16px to 8px to bring the chevron closer to the field's edge. Other native-select spacing is unchanged. language-chevron.json checks all 17 presentation languages at 320/1280px: the arrow's gap is 8px in the picker's actual computed direction, hit area remains at least 48 × 48px, and no page overflows. The header intentionally stays LTR even for Arabic presentation. language-chevron.png shows the focused English control. Full build passed after this refinement.
