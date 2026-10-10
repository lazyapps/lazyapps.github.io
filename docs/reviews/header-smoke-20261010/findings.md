# FondFont smoke behind the transparent header

The header was transparent, but the WebGL canvas stopped at y=64 because its sky
expansion still looked for the removed `.topbar__app img`. It fell back to only
24px of sky above the stage, clipping the smoke at the canvas boundary.

The scene now anchors its sky and leaf spawning to the shared header product
and observes the shared header for resize. Stage coordinates are measured in
document space, while product coordinates are measured within the sticky header,
so resizing while scrolled preserves the full sky.

Verified at 1280, 768, 390 and 320px: transparent header, no backdrop blur at the
top, canvas extending to the product's top minus 24px, and no horizontal overflow.
Smoke renders behind the header without moving or rescaling the road. Additional
scroll/resize/return-to-top results are in `checks.json`. Full build and the
existing four-scenario sunlight projection check passed.
