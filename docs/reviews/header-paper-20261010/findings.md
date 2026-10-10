# Header matching the page background

The shared header's scrolled background now uses `var(--paper)` directly with
full opacity, replacing the 78% transparent color mix. ScrollY 0 remains fully
transparent; positive scrollY retains the existing blur and layer behavior.

Pages with the shared body grain use the same noise asset, size, opacity and
filter on the scrolled header. Pages without grain retain a plain paper
background. The solid base prevents underlying content from showing through;
the grain overlay does not change the game's texture or layer order.

Browser checks confirmed an opaque rgb(248,248,246) matching the page, transparent
background and no blur at 0, and identical header/page grain properties on
Shheep. `npm run build` passed all 71 pages and existing checks. Evidence is in
`checks.json` and `shheep-scrolled.png`.
