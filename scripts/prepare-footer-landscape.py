#!/usr/bin/env python3
"""Prepare the site footer landscape tile.

The imagegen source is a horizontally repeatable strip drawn on pure white. This script:
0. closes the last few pixels of the left/right seam so the tile repeats exactly;
1. bakes a multiply blend against the footer panel color, so paper-white areas
   (water, sheep, cottage walls) match the panel exactly;
2. turns the open sky into real transparency by flood-filling near-white pixels
   connected to the top edge, so the footer sun can sit *behind* the hills;
3. writes a tiny sketch of the land and its ink lines that the footer inlines as a
   placeholder until the full artwork has loaded;
4. cuts the open water at the bottom into a band that repeats vertically, so the lake can
   continue below the footer when the page is rubber-banded past its end.

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
SKETCH = ROOT / 'src/assets/img/footer-landscape-sketch.png'
WATER = ROOT / 'src/assets/img/footer-landscape-water.png'
PANEL = (0xFC, 0xF9, 0xED)  # keep in sync with --footer-panel in site-footer.css
SKY_THRESHOLD = 236  # min channel value counted as open sky
SEAM = 16  # columns blended on each side of the wrap-around seam
SKETCH_WIDTH = 480  # placeholder width; it is inlined into every page, so keep it a few KB
SKETCH_INK = (0x2F, 0x31, 0x22)  # footer ink
SKETCH_INK_STRENGTH = 0.38  # how much ink shows over the panel
WATER_COPIES = 3  # vertically stacked, horizontally shifted copies of the open-water band
WATER_OBJECT = 150  # max channel distance from the panel color that counts as an object, not a ripple


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


def write_sketch(rgba: np.ndarray) -> int:
    """Downsample the artwork into a three-color PNG: open sky, solid land in the panel color, faded ink lines.
    The land stays opaque so the sun hides behind the hills before the real artwork arrives."""
    width = SKETCH_WIDTH
    height = round(width * rgba.shape[0] / rgba.shape[1])
    shrink = lambda mask: np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).resize((width, height), Image.BOX))
    luma = rgba[..., :3] @ np.array([0.3, 0.59, 0.11], dtype=np.float32)
    land = shrink(rgba[..., 3] > 128) > 127
    ink = shrink((luma < 105) & (rgba[..., 3] > 128)) > 60
    index = np.where(ink & land, 2, np.where(land, 1, 0)).astype(np.uint8)
    faded = [round(p + (i - p) * SKETCH_INK_STRENGTH) for p, i in zip(PANEL, SKETCH_INK)]
    sketch = Image.fromarray(index, 'P')
    sketch.putpalette([0, 0, 0, *PANEL, *faded])
    sketch.info['transparency'] = bytes([0, 255, 255])
    sketch.save(SKETCH, optimize=True, bits=2)
    return SKETCH.stat().st_size


def write_water(rgba: np.ndarray) -> int:
    """Keep the rows below the last object (boat, lily pads, reflections), starting at a row of plain water,
    so the band only holds ripple lines and joins cleanly when it repeats."""
    distance = np.abs(rgba[..., :3].astype(np.int16) - np.array(PANEL)).max(axis=2)
    objects = np.flatnonzero(distance.max(axis=1) > WATER_OBJECT)
    plain = np.flatnonzero(distance.max(axis=1) <= 12)
    top = int(plain[plain > objects.max()].min())
    assert distance[-1].max() <= 12, 'the bottom row must be plain water'
    band = rgba[top:, :, :3]
    # Stack shifted copies so the ripples do not read as a regular grid when the band repeats.
    shifts = [round(band.shape[1] * k / WATER_COPIES) for k in range(WATER_COPIES)]
    Image.fromarray(np.vstack([np.roll(band, shift, axis=1) for shift in shifts])).save(WATER, optimize=True)
    return band.shape[0] * WATER_COPIES


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
    print(f'{SKETCH.relative_to(ROOT)} {write_sketch(out.astype(np.float32))} bytes')
    print(f'{WATER.relative_to(ROOT)} {write_water(out)} rows')


if __name__ == '__main__':
    main()
