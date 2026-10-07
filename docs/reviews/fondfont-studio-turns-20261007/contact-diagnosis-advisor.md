**Use the world-space swing planner, but also replace the current sole correction. The planner alone cannot fix both failures. Do not rephase the banks for reversal.**

The current checkout reproduces **8.93 mm planted slip and 60.2 mm frame jumps**, rather than the briefing’s 92 mm. At the worst reversal, the dog’s toe–heel distance stretches from **26.46 mm to 38.92 mm**. The solver holds the center and heading while deforming the sole. This is not primarily a smoothing problem.

The minimum robust design is:

1. **Explicit per-foot stance, swing and settling states.** Keep stance anchors fixed in world space. At lift-off, capture the final corrected sole pose and velocity. Plan the entire swing to a reachable, ground-aligned native touchdown pose, with continuous position and velocity and zero world velocity at landing. Reversal must retarget from the current trajectory state, never restart it or switch endpoints abruptly.

2. **Finish airborne steps when stopping.** Replace the `.04` activity threshold that instantly grounds feet with a timed landing, initially around 250 ms. This timer must advance while locomotion phase is stopped. Keep supporting feet anchored; permit native body motion within leg reach. Fade toward rest only as contact constraints allow.

3. **Use native corrections that represent finite sole rotation.** The existing rest-pose XYZ plus single yaw morph is insufficient for reliable large-angle correction. Add native yaw samples conditioned on the underlying leg pose, then solve all three sole markers together with bounded weights. Keep corrections local to the legs and preserve the native gait elsewhere. Merely changing the current center/heading solver to least squares reduces error but does not remove the deformation. **A robust solution therefore needs a correction-basis bake extension, not just runtime smoothing.**

Keep gait phase monotonically forward, driven by accepted forward travel plus absolute yaw travel. Never reverse playback to accommodate a turn. Separately assert that navigation displacement projected onto body heading is nonnegative within numerical tolerance.

Validate against the **final decoded mesh**, with these acceptance criteria:

- Every planted marker stays within the existing **5 mm** limit of its original touchdown anchor throughout stance; target tighter margins. Never relatch anchors to conceal drift.
- Check ground penetration, sole edge lengths and leg reach alongside contact error. A stationary center with a stretching paw fails.
- Measure swing position and velocity continuity at lift-off, reversal, landing and stopping. Retain the 25 mm/frame guard at 60 Hz, but also use time-normalized velocity/acceleration checks and repeat at 30/60/120 Hz.
- Sweep starts, stops and immediate left/right reversals across the full gait cycle, including stopping and restarting during swing. Report separate maxima and offending frames per scenario.
- Visually inspect native leg shape, support changes and body motion. Passing three-marker tests alone cannot establish natural movement.