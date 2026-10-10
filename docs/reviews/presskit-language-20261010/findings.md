# Press Kit language · 2026-10-10

The user requested single-language Press Kit presentation, retaining the shared language selector, inheriting entrance language, and using JS with language hashes at the existing paths.

Final steering: fragments use only the language code, e.g. #zh-Hans, #en and #ja. All current entries, selector values, back/card/footer links and README references use this form. Previously shared #language-* fragments still resolve and normalize to the short form without navigation. The original navigation.json and responsive.json describe verification before this shortening; hash-navigation.json records the final short-hash behavior.

Final name refinement: FondFont, KeyHop and YiYan use middle-dot bilingual names in both Chinese scripts. The shared catalog supplies hero, card, material heading and README names. Labels stay on one line with responsive type sizing. bilingual-names.json checks all four affected pages (hub plus three products), two Chinese scripts and 320/390/768/1280px (32 cases), with no name overflow or wrapping. fondfont-name-mobile.png shows the final presentation.

Final icon refinement: removed the hub hero's colored icon shells and product-list icon backing, including wrapper padding, shadow and radius. Original App icon PNGs and native transparency remain intact. icon-frames.json verifies all 14 icon wrappers at 320/768/1280px: transparent background, no border/shadow/padding/radius, all images loaded and no page overflow. hub-native-icons.png is the current hub preview. Full build passes after this change.

Implemented a separate 17-language presentation lookup and shared hash-mode LanguagePicker. The page now switches header labels, hero/product summary, platform/status/official links, material panel, usage/contact/footer, document language/direction and title together. Static English and expandable material panels remain available without JavaScript. Removed bilingual duplication and repeated material introductions; original native icons and paper hero remain intact.

Resolution: valid explicit hash, saved Press Kit choice, browser preferences, English. Chinese regions, case and regional tags are matched consistently. Language selection uses pushState with back/forward restoration; initial language hashes are normalized with replaceState. Panels use materials-* IDs so language state does not cause fragment scrolling. #main keeps the selected language and normal skip navigation.

All 60 product landing footer entries carry their actual page language. English home, World Book and XVDL entries explicitly pass English, overriding saved preferences. Hub cards, back links, Press Kit footer links and all 57 README Press Kit links carry the chosen language. Product website links use existing translated routes; KeyHop Italian correctly returns to its English marketing page.

Page presentation and actual App download support remain independent. The 57 App-language folders and original image files remain unchanged. KeyHop Arabic/Russian/Hindi use existing marketing copy with explicitly identified English materials; Italian uses its existing Italian README. World Book/XVDL retain incoming presentation languages while English fallback copy/material blocks have lang=en and dir=ltr. ZIPs were regenerated only to include the README language hashes.

Advisor review: followed its recommendation to use the same 17-language presentation picker everywhere, avoid referrer inference, separate presentation from the download catalog, replace fragment-target panel IDs, and update the visible picker/footer language state. No additional review was needed after deterministic and browser checks settled the identified risks.

Validation:

- npm run build: 71 pages; SEO, Shheep artifacts, Press Kit language tests and download contracts passed. No new routes.
- check-presskit-language.mjs: entry precedence, Chinese/Portuguese/case normalization, malformed and ordinary anchors, universal presentation options, KeyHop Arabic/Italian and unchanged App-language coverage.
- Built-page checker: every landing entry passes its document language, one shared hash picker per Press Kit, presentation data completeness, real product destinations, README hashes and unchanged ZIP/file contracts.
- responsive.json: all 136 combinations of eight pages × 17 languages at 320px, plus Chinese/French/Arabic across all eight pages at 768/1280px (184 total). No document/title overflow or header overlap; narrow checks also verify visible panel, summary, picker and footer language state.
- navigation.json: French landing → French Press Kit starts at scrollY=0 with French README/website; Chinese selection → back/forward restoration; #main retains Chinese; Arabic hub → World Book retains Arabic UI with English copy/materials; KeyHop Arabic and Italian; English World Book entry overrides previously selected Arabic.
- Native browser download of the final Chinese FondFont README starts with “爱装字体 · FondFont” and uses #zh-Hans in its Press Kit URL. Browser console warnings/errors empty. Chinese CHMate download was also verified earlier before shortening the hash.

Screenshots: chmate-zh-desktop.png, hub-zh-mobile.png and keyhop-ar-mobile.png.

Title spacing refinement: the global :lang rules applied body leading to every localized inline span and br, overriding the heading's inherited rhythm. Shared PressLayout now makes inline heading elements inherit line-height and letter-spacing while preserving specialized App-name styles. Chinese/Japanese/Korean hub leading is correctly 1.05 instead of 1.85; Arabic/Hindi is correctly 1.05 instead of 1.8; English remains unchanged. title-spacing.json records seven-language measurements before/after, 14 narrow/tablet checks and 28 product checks (seven Apps × English/traditional Chinese × 320/1280px), with no overflow or subtitle inheritance failures. Full build passed. hub-title-spacing.png shows the corrected traditional Chinese heading.

Hub title dot: wrapped the final title line and accent dot in one inline-block with white-space:nowrap, preventing the dot from becoming a separate line in every presentation language. dot-nowrap.json verifies all 17 languages at 320/390/650/768/900/1280px (102 checks), with the dot on the text's line and no title/document overflow. Full build passed. hub-dot-nowrap.png shows the Spanish title.

App title dots: the shared product template now binds the final word and accent dot with U+2060, using normal word breaking instead of overflow-wrap:anywhere. Earlier words in longer localized titles remain free to wrap. app-dot-nowrap.json covers all seven App pages × 17 presentation languages × 320/390/650/768/900/1280px (714 checks): every dot stays on the final text character's line, every title remains within its column, and no document overflows. The initial CHMate sample also passed 68 checks before this preventive guard. Full build passed. app-dot-nowrap-fr-mobile.png shows the French CHMate title on mobile. docs/PRESSKIT.md records the rule for all titles and future Apps.
