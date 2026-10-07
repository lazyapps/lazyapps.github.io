# FondFont Three.js hero · references

Research date: 2026-10-07. These are direction references, not asset sources.

- [Little Big Workshop — publisher](https://www.thqnordicmobile.com/en/games/little-big-workshop/): tabletop factory scale, a whole production chain in one legible miniature. The publisher screenshot gallery was inspected in the browser.
- [Mars First Logistics — official Steam page and release trailer](https://store.steampowered.com/app/1532200/Mars_First_Logistics/): visible mechanisms supporting awkward cargo, hydraulic/spring construction, load-dependent vehicle movement. Its official trailer and animated mechanical construction examples were inspected in the browser. Use its readable mechanical cause and effect, not its terrain or game art.
- [SnowRunner — Season 2 overview, Focus Entertainment](https://www.youtube.com/watch?v=kKXEl5GZkgk): cargo creation, material collection and deliberate transport. [Publisher gameplay overview](https://www.focus-entmt.com/en/news/gamescom-2019-focus-home-interactive-and-saber-interactives-mudrunner-sequel-snowrunner-fully-revealed-at-gamescom) verifies cargo delivery is central. Used as a vehicle/transport direction reference; no footage downloaded or embedded.

## Existing session assets

Source chat: **为 FondFont 创建落地页**, `01a10fe1-c828-7171-99e0-90e52c4dd0aa`.

- `scripts/assets/fondfont/animation/v13/foundry-start-reference.png`: original imagegen brick Type Foundry, orange flatbed and larger cream iOS factory. Reinterpreted as real 3D geometry.
- `scripts/assets/fondfont/animation/v14/paint/paint-fleet-{en,zh-hans,zh-hant,ja,ko}.png`: original imagegen localized fleet paint. The exact side panel region used by the existing compositor (209,405 to 543,443 in a 1152×720 coordinate system) is extracted as WebP and mapped to the real truck side, retaining paint/material detail.
- `scripts/assets/fondfont/animation/v15/cargo-manifest.json`: 12 real glyph outlines, including 明, g, あ, ß, 달, 愛, Ω, 永, &, Ж, 꽃, 海. Exact path strings and font family provenance are copied into `src/lib/fondfont/glyphs.json`; the shapes will be raised metal glyphs on solid type slugs.

No new generated video, third-party game footage, remote runtime fonts or game models required.
