Yes. **Ground-plane bearing plus elevation is the appropriate correction for the stated stylized requirement.** Keep the DirectionalLight: it produces one shared shadow direction, while a PointLight introduces unwanted divergence.

Let \(g=(g_x,0,g_z)\) be the DOM sun center unprojected onto \(Y=0\), and set the light to \((g_x,18,g_z)\), targeting the origin. A point at height \(h\) above its ground base casts the ground offset

\[
\Delta=(-hg_x/18,\;0,\;-hg_z/18).
\]

For the orthographic screen projection \(P\),

\[
P(\text{shadow})-P(\text{base})
=-\frac{h}{18}\,[P(g)-P(0)].
\]

Since \(P(g)\) equals the DOM sun center, this guarantees the desired opposite screen bearing **relative to the projected scene-center ground anchor**.

The acceptance test should directly measure the rendered requirement:

- Define \(d=P(0)-\text{sunDOM}\), using one consistent coordinate system.
- For a shadow landmark corresponding to a known elevated point, measure \(v=\text{shadowScreen}-\text{groundBaseScreen}\). Use that point’s vertical ground base, never its elevated position or an arbitrary silhouette centroid.
- Require \(v\cdot d>0\) and a small angular error between \(v\) and \(d\).
- For this upper-left sun layout, explicitly require \(v_x>0\) and \(v_y>0\) in DOM coordinates: **right and down**. That catches the previous upward-shadow bug.
- Across objects and supported viewports, require the same normalized shadow direction, recalculated from the shared anchor.

This is a coherent **stylized screen-bearing constraint**, not a claim that a finite physical light projects onto the icon. Elevation intentionally changes the light’s own projection. Also, do not require every object’s shadow to point exactly away from its individual base-to-icon vector: those vectors differ, whereas directional-light shadows remain parallel.