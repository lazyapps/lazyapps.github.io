Keep the plan, but resolve initial lighting consistency before regenerating posters. Fixed seed47 matches geometry; DOM-dependent sunlight can still cause a visible color/shadow jump. Capture and live `render(0)` should share initial lighting, then transition to DOM-driven lighting after the handoff.

One lifecycle detail is missing from the briefing: the animation clock’s origin. Start it at readiness so slow imports/model loading cannot make the first visible animated frame jump ahead of the poster.

Otherwise, the proposed loading state, reduced-motion handling, fallbacks, and verification are appropriately scoped.