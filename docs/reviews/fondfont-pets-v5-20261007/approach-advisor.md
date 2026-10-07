The quaternion order is correct: transforming world up by the inverse parent world quaternion gives a parent-space axis, so **premultiplying** the bone’s base quaternion applies the intended world-up wag.

**One critical correction: explicitly enforce fresh world transforms and root-to-tip application.**

Use this sequence:

1. Restore every tail bone’s cached base quaternion.
2. Update the animation mixer.
3. Cache **all** resulting base quaternions before applying any overlay.
4. Refresh the rig’s world transforms.
5. Apply overlays from base to tip. Refresh each changed bone’s world transform before calculating its child’s axis.

Each axis calculation must use the parent’s **current-frame quaternion, including its already-applied wag**. Using stale transforms—or precomputing every axis before applying the parent overlays—can introduce unwanted pitch/roll components despite the otherwise correct quaternion math.

This assumes the bone hierarchy has uniform scale and no shear; inverse world quaternion alone cannot compensate for those distortions.