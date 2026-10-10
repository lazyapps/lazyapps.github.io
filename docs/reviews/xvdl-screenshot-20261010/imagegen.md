# XVDL download-button screenshot

Built-in imagegen edit, 2026-10-10. Input is the developer's attached screenshot, copied unchanged to `scripts/assets/presskit/xvdl-in-use-original.png` (1190 × 874). The edited output is `src/assets/img/xvdl-in-use.png` (1463 × 1075). The website uses the edited presentation; the Press Kit includes both original and edited files at its archive root, with distinct labels and provenance notes. This output is an annotated promotional image rather than an unmodified capture.

- Input SHA-256: `280a32832e2dd8c85e622496bac0ea6d7b9a7d6afaf6810efba0c2cd0d552385`
- Edited SHA-256: `44b7f329e60f6c85a15af4e22f217dd9bc7a796ac364fa86eca5da0cde766169`
- Built-in output: `/Users/realazy/.codex/generated_images/01a124db-3c3e-7141-9e45-f95701f9e0b3/exec-5c94ee69-db7f-4722-8b1e-a934eb3590e8.png`
- No CLI fallback or Open Graph edits.

## Prompt

Edit target: the attached original X post screenshot, 1192 x 874 pixels. Precise-object-edit for a website product demonstration. Preserve the existing screenshot's framing, aspect ratio, account avatar, all text, video frame, logo, button label, UI, proportions and detail. Do not redraw or invent any UI, no replacement typography. Make the existing gray XVDL download button at the video's upper-right corner clearly the focal point. Add only a restrained thin coral-orange (#ff6347) rounded outline 6 px outside the button, a subtle soft coral glow behind this outline, and slightly lower the contrast of the surrounding video frame to direct attention to the unchanged white download arrow and XVDL label. Keep the button's gray fill and exact white glyphs unchanged; no arrows, captions, magnification inserts, stickers or new text. Preserve the original black background and enough surrounding post context. Professional understated editorial screenshot annotation, sharp output.

The prompt's stated width was an estimate; the metadata above records the actual input and output dimensions. Imagegen changes raster details, so only the original capture is described as having unchanged pixels.

## Validation

- Regenerated the XVDL README, manifest and ZIP. Both screenshot files are shared at the ZIP root; the App language remains English. The original's SHA-256 matches the supplied attachment.
- `npm run build` passed: 71 pages, SEO checks, Shheep artifacts, all seven Press Kits and 57 App-language folders.
- Browser confirmed the two distinct Press Kit image download links, labels and metadata. Homepage image loads at its actual 1463 × 1075 dimensions. At 320/390/768px it keeps its aspect ratio with no document overflow; desktop checked at 1280px.
- `desktop.png`, `mobile.png` and `responsive.json` record the rendered result.
