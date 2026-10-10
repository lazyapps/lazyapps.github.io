# Persistent frosted header

The shared header now applies its 78% paper tint and 16px backdrop blur directly
in CSS at all scroll positions. Removed the obsolete scroll listener and state
class toggle. Updated the current Press Kit and FondFont header documentation.

Browser checks confirmed the same background and blur at the top and after
scrolling; a 390px viewport retained the blur with no horizontal overflow. The
header stays at z-index 1100 without a bottom border, and FondFont retains its
sun. `npm run build` passed all 71 pages and existing SEO, game and Press Kit checks.
