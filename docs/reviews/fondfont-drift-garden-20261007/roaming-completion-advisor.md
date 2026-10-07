Do not mark this complete: front-lane turning still causes prolonged stalls.

Replaying the existing tests’ sampling pattern, seed **47** leaves the dog stationary near `(3.760, 1.180)` from approximately **41.5–300 seconds**; seed **991** stalls it for approximately **238 seconds**.

In `garden-life.mjs`, the dog’s lane at `z=1.18` lacks clearance for a perpendicular capsule beside the buildings. Collision rejection prevents completing the turn, while the blocked handler merely pauses and chooses another route without providing an escape maneuver.

Fix recovery with a collision-safe maneuver into sufficient turning space. Add **per-pet progress assertions** that detect prolonged stalls. The current combined territory bounds pass because the cat keeps roaming, masking the immobilized dog.