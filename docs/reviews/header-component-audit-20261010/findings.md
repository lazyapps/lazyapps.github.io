# One shared header

Audited the user's exact URL, `http://127.0.0.1:4322/chmate/`, and its English
entry. Both already used SiteHeader; the reported translucency was not
reproduced after scrolling in the current build: the background was
rgb(248,248,246) with opacity 1. The component still had a redundant 16px
backdrop blur, which is now removed for all consumers.

ScrollY 0 remains transparent by design, so CHMate's own background video can
appear behind the navigation there. Positive scrollY uses fully opaque page
paper plus the shared grain. The background video's existing opacity is
unchanged; it is independent of the header.

Privacy pages were the remaining independent navigation implementations. Both
now use SiteHeader, preserving their content and language links. Removed unused
old navigation rules from KeyHop and Shheep. Updated the current shared-header
and FondFont documentation.

The build's readPages inventory contains 71 generated site pages. All 70 pages
with navigation have exactly one header with the same Astro component scope;
no old topbar markup remains. The homepage has no separate navigation header.
Public standalone demo/export HTML is excluded using the existing site-page
inventory. See `generated-pages.json`.

Browser checks confirmed CHMate at positive scrollY with opacity 1 and no blur,
at scrollY 0 with transparent background, and the same states on the migrated
Chinese privacy page. Full build, SEO, game artifact and Press Kit checks passed.
