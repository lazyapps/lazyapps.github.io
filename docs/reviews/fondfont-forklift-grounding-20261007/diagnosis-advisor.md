**Prioritize contact-shadow rendering before rebuilding the forklift.** The strongest diagnosis is that the renderer removes the visual evidence of tire contact; the exported wheels are not substantially elevated or misoriented.

Measured facts:

- I decoded the published GLB’s actual tire vertices and sampled the animation every 25 ms. Tire bottoms remain approximately **−0.02 to +1.20 mm around `y=0`**. This goes beyond the existing center-radius test.
- The shadow catcher sits at **`y=-0.025`**, leaving roughly **25–26 mm beneath the tires**. Its opacity is only **0.13**, while the directional shadow uses **VSM radius 20** across the entire campus.
- In the supplied screenshot, the forklift’s tires have no clearly readable, attached contact patches. The frontal view makes the long forks more prominent than the wheel footprints.

**Inference:** that weak, diffuse contact is the primary airborne cue. The small geometric gap contributes, but cannot alone explain the appearance. Fast motion likely amplifies it: the two cited moves reach calculated peak speeds of **4.82 and 4.0 m/s**. Their perceptual effect cannot be established from this still.

The minimal coherent correction is to bring the catcher just below the tire contact plane and tighten and strengthen the forklift’s **live Three.js shadows**, with sufficiently small blur and bias that dark contact remains attached to the visible tire bottoms at the actual page size. Keep the current geometry, materials, and transfer clearances for this first correction. Require the stationary empty forklift to read as grounded before adjusting travel timing.

I disagree with making a full native Blender v4 the first intervention. **Blender lighting and rendered shadows do not survive this export:** the build explicitly disables light export, and `blender-scene.ts` supplies the runtime lighting. Better tread and a convincing Blender render can therefore reproduce the same failure in the browser. Use the new reference’s tire-to-floor contact as the acceptance target; address that rendering defect first.