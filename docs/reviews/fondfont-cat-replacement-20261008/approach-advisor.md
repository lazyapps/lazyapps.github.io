Proceed with the native-rig adaptation. Muting the two documented cyclic constraints in a derived copy and grounding the original rig through its native IK is technically sound. Source faithfulness does not require preserving a broken animation cycle.

Two details need tightening:

- **Nearest-vertex attachment alone is insufficient for the groom.** It identifies an attachment point but does not capture local rotation or deformation. Preserve each strand’s attachment and orientation through the evaluated body deformation for every exported pose. Otherwise fur can slide, penetrate the skin, or keep pointing in its rest direction during turns.
- **Valid individual morph targets do not guarantee valid runtime combinations.** Native IK is nonlinear; blending baked correction poses can introduce defects absent from every isolated target. Validate the decoded GLB through the actual locomotion evaluator, including simultaneous paw corrections and walk/turn transitions.

Essential acceptance checks:

1. **Source fidelity:** compare the original and derived cat at matching poses and views. Preserve silhouette, calico markings, eyes, and groom coverage. Record constraint changes and gait modifications; keep the downloaded original untouched.
2. **Cat-specific calibration:** derive contact phases, sole markers, floor offsets, and correction ranges from this rig. Preserve the 84-target contract, but do not inherit the dog’s calibration. Confirm `body_mesh` selection and synchronized deformation of eyes and groom.
3. **Runtime motion:** retain every stated numerical threshold across decoded runtime blends, seeds, and frame rates. Include sustained left/right turns, transition boundaries, and simultaneous planted supports. Visually reject knee flips, collapsing limbs, or unnatural posture even if sole metrics pass. Rerun the unchanged dog’s checks.
4. **Rendering and cost:** inspect actual browser materials and fur, and measure decoded memory, load time, and frame time on representative mobile hardware. Groom geometry multiplied across 84 targets can become the dominant cost.
5. **Production delivery:** verify a production build loads both public pets without development middleware, all seven posters match, attribution and provenance cover both assets in every locale, and the restricted cat is absent from the deployable output.

No broader redesign is warranted. The release decision should hinge on deformation-aware groom binding and validation of the final blended runtime poses.