#!/usr/bin/env python3
"""Prepare the site footer landscape tile.

The imagegen source is a horizontally repeatable strip drawn on pure white. This script:
0. closes the last few pixels of the left/right seam so the tile repeats exactly;
1. bakes a multiply blend against the footer panel color, so paper-white areas
   (water, sheep, cottage walls) match the panel exactly;
2. turns the open sky into real transparency by flood-filling near-white pixels
   connected to the top edge, so the footer sun can sit *behind* the hills.

Usage: python3 scripts/prepare-footer-landscape.py
Requires numpy and Pillow.
"""
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'scripts/assets/footer/landscape-source.png'
OUTPUT = ROOT / 'src/assets/img/footer-landscape.png'
PANEL = (0xFC, 0xF9, 0xED)  # keep in sync with --footer-panel in site-footer.css
SKY_THRESHOLD = 236  # min channel value counted as open sky
SEAM = 16  # columns blended on each side of the wrap-around seam


def close_seam(rgb: np.ndarray) -> np.ndarray:
    """Blend mirrored columns around the wrap seam so column 0 == column w-1."""
    out = rgb.copy()
    w = rgb.shape[1]
    for k in range(SEAM):
        weight = 0.5 * (1 - k / SEAM)
        left, right = rgb[:, k], rgb[:, w - 1 - k]
        out[:, k] = (1 - weight) * left + weight * right
        out[:, w - 1 - k] = (1 - weight) * right + weight * left
    return out


def sky_mask(rgb: np.ndarray) -> np.ndarray:
    """Near-white pixels 4-connected to the top edge."""
    h, w, _ = rgb.shape
    light = rgb.min(axis=2) >= SKY_THRESHOLD
    sky = np.zeros((h, w), dtype=bool)
    queue = deque((0, x) for x in range(w) if light[0, x])
    for _, x in queue:
        sky[0, x] = True
    while queue:
        y, x = queue.popleft()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < h and 0 <= nx < w and light[ny, nx] and not sky[ny, nx]:
                sky[ny, nx] = True
                queue.append((ny, nx))
    return sky


def main() -> None:
    src = Image.open(SOURCE).convert('RGB')
    rgb = close_seam(np.asarray(src, dtype=np.float32))

    # Snap paper-white noise to pure white before blending.
    whiteness = rgb.min(axis=2, keepdims=True)
    rgb = np.where(whiteness >= 246, 255.0, rgb)

    sky = sky_mask(rgb.astype(np.uint8))
    # Soft 1px edge: blur the opaque mask slightly, keep the interior solid.
    opaque = Image.fromarray(((~sky) * 255).astype(np.uint8))
    alpha = np.asarray(opaque.filter(ImageFilter.GaussianBlur(0.6)), dtype=np.float32)
    alpha = np.maximum(alpha, (~sky) * 255.0)

    baked = rgb * (np.array(PANEL, dtype=np.float32) / 255.0)
    out = np.dstack([baked, alpha]).round().clip(0, 255).astype(np.uint8)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out, 'RGBA').save(OUTPUT, optimize=True)
    print(f'{OUTPUT.relative_to(ROOT)} {src.width}x{src.height}, sky {sky.mean():.1%}')


if __name__ == '__main__':
    main()
