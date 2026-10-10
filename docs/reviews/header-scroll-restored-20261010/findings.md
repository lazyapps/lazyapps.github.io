# Global transparent-to-frosted header

Final rule: scrollY 0 is fully transparent, with no background or backdrop blur.
Positive scrollY applies the 78% paper tint and 16px blur. Returning to 0 removes
both. Passive, frame-coalesced scroll updates and pageshow synchronize the state.

The shared SiteHeader serves 68 generated pages: all product landing pages,
product Press Kits and the Press Kit hub. Current documentation was updated;
the persistent-frosted implementation is superseded.

Browser checks (`checks.json`) verified FondFont at 0, 40 and back to 0; the Press
Kit hub at 0 and 40; and Shheep at 0. Header z-index remains 1100, the bottom
border remains absent, and FondFont's sun and full smoke canvas remain intact.
The full build passed all 71 pages and existing SEO, game and Press Kit checks.
