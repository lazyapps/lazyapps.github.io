# Hero completion — 2026-10-07

Resumed the hero after the installation carousel work. The existing imagegen
architecture, flat identity, exposed metal type and native Blender model remain
in use. All eight recorded imagegen source hashes still match their manifest.

## Final changes

- Replaced the frontal forklift approach with a shallow alignment curve outside
  the building eave. The front axle follows its tangent; cargo follows the rigid
  overhang, and the rear wheels steer. Loading and unloading reverse the same
  maneuver.
- Separated exit, raising, alignment, lowering, release and withdrawal timings.
  The cycle is now 41.2 seconds. The warehouse opens only after arrival at 15.3
  seconds; replenishment remains hidden behind both closed shutters.
- Matched the road to the content container at every viewport, including
  fractional CSS widths. Mobile now shows both turns of the loop. Planting
  extends naturally beyond it and webpage overflow handles the edges.
- Re-exported all seven localized posters as complete 2560 × 854 native frames
  at 13.1 seconds. The mobile field has a 180 px minimum height.

The first review suspected a vertical side-panel name. Isolating AO and the bed
label, plus the GLB anchors/materials, established that the visible wood is the
horizontal deck; that decal belongs there. The final independent advisor
accepted this evidence and found no remaining delivery blocker in the current
desktop poses/choreography. Its optional contrast suggestions were not used to
expand the scope. Mobile framing was then directly checked at all breakpoints.

## Validation and evidence

- `node scripts/check-fondfont-three.mjs`: 10 ms physical sampling, complete
  forklift body/jamb clearance, support/release, front-axle tangent, six-wheel
  road contact with drift, independent doors and two-cycle continuity pass.
- TypeScript check passes. Astro builds all 52 pages.
- `resume-responsive.json`: 28 locale/viewport combinations pass road/container
  alignment, font loading and zero page overflow.
- `resume-fallback.json`: all seven 320 px reduced-motion posters pass.
- `resume-production.json`: all seven production scenes initialize; no warnings
  or errors in the final browser check.
- `resume-two-loops.webm`: 83.4 seconds of live canvas recording, with animation
  time advancing by 83.4 seconds. It includes two complete cycles and their
  boundary. The background is filled only for the review recording; production
  still uses transparent rendering over the page.
- `hero-complete-loop.mp4`: one complete cycle, H.264, 1280 × 420, approximately
  1.19 MB. This is a review recording, not a production replacement video.
- `hero-final-desktop.png` and `hero-final-mobile.png`: final page evidence.

Production preview: <http://127.0.0.1:4331/fondfont/zh-hans/>.
