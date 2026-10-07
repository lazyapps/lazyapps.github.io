No concrete architectural flaw in the strategy as described. Expanding the viewport upward while keeping orthographic left, right, and bottom fixed preserves the road’s page position and scale.

The main implementation trap is measurement feedback: calculate the inset from the **unchanged stage wrapper**, never from the expanded canvas’s bounding rectangle. Otherwise resize updates can oscillate or compound the inset.

Also ensure:

- `worldSpan / width` means the camera’s **horizontal frustum span per CSS pixel**.
- Ancestor overflow rules allow drawing above the stage.
- Leaf height mapping accounts for camera orientation and each leaf’s changing z; a fixed world-y emitter would drift in screen space.

Two small central plant groups and the reduced sway are consistent with the revised request.