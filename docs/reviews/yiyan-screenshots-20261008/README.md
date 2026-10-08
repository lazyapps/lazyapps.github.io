# Updated user-supplied YiYan screenshots

Replaced `src/assets/img/yiyan-showcase.png` with the provided October 8 learning-record window and `src/assets/img/yiyan-showcase-detail.png` with the provided follow-up conversation window. Both are byte-identical copies of the original PNGs, with original resolution and alpha preserved. Sources, hashes and exact built assets are recorded in `source-provenance.json`.

The existing screenshot container now displays the learning record followed by the follow-up window. All twelve locales share these authentic current UI screenshots and have localized accessible descriptions. Removed obsolete localized-image imports; the older localized source images are retained. The hero video remains unchanged and its image fallback also uses the new learning-record screenshot.

Original page CSS is byte-identical to the pre-update component. Existing section order, typography, cards, colors and screenshot container styling remain unchanged. The one additional image is content inside the existing container. Previous screenshots/component are preserved in the ignored `marketing-v5/revisions/04-screenshots/` archive.

Validation: `npm run build` and existing SEO/artifact checks passed. Both new hashed assets appear in all twelve built pages and match the source hashes exactly. Browser confirmed both images loaded at 2048×1344 /1984×1328, displayed proportionally at 1052px wide. Saved actual page previews: `page-preview.jpg` and `follow-up-preview.jpg`. No deployment or product-code changes.
