The HTML-caption approach is within scope, and 15px is a sensible increase at a 350px film width. **I would change the fixed 32px spacing assumption before committing.**

Two lines at the proposed settings need **48.5px including padding**. Existing scene whitespace makes that plausible, but `width − 112px` gets narrow on smaller phones; Russian copy such as “Каждому приложению — своё место.” may require three lines. That would push an absolutely positioned caption back over the keys.

Reserve mobile caption space based on the **tallest of the four localized captions at the current width**, keeping that height stable throughout playback. Four overlapping CSS-grid items, with inactive captions hidden but retaining layout, can accomplish this without measurement JavaScript. Reserve the controls’ full width, inset, and a visible gap. Keep the desktop overlay geometry.

Also, **export one shared clean video and poster**: the compositor’s only locale-dependent visuals are the captions being removed. Twelve identical exports add unnecessary work and assets.

Before committing, check:

- All four captions in all 12 languages at a **320px viewport**, accounting for page gutters; repeat with enlarged text. Inspect Russian wrapping, Arabic direction, and Hindi/CJK font rendering.
- **640px and 641px**, plus desktop, for abrupt sizing changes and caption/control collisions.
- Initial poster, blocked autoplay/reduced motion, pause/resume, and **5s, 10s, 12.7s, and loop restart**. Caption state must follow media time, including after seeking.
- Clean posters and videos together, so no baked caption remains underneath HTML text.

This keeps the change focused while removing the fragile assumption that every translation always fits two lines.