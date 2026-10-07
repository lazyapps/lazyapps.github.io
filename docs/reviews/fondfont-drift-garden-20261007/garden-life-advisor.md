Yes: **the approach and retreat make both pets skate with motionless legs.**

In `garden-life.mjs`, `pet()` updates `speed` and `distance` only during the chase. Both pets still translate **0.35 m during seconds 0–2 and 21–24**, but `gait` and `stride` remain zero. Consequently, `blender-scene.ts` holds the leg pose fixed while moving the root; paws slide across the ground. The slower approach does not solve this.

Compute locomotion speed and accumulated travel for every translating phase, then drive the leg animation from those values. For retreat, either support backward stepping or turn the pets toward their travel direction. Fix this before visual verification; it directly undermines the requested believable, grounded motion.