"""Derive web-sized campus textures from the unchanged v3 imagegen originals.

Tiles are resized to 512 px. Where a tile's wrap seam is measurably worse than
its interior pixel variation, the seam is removed with a wrap-around cross-fade
(the tile is offset by half, and a feathered band from the unshifted tile covers
the new central seam). Interior backdrops are resized to 1024 px wide.
Provenance (originals, SHA-256, operations) is written to textures/manifest.json.
"""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'scripts/assets/fondfont/blender-v3/imagegen'
OUT = ROOT / 'scripts/assets/fondfont/blender-v3/textures'
OUT.mkdir(parents=True, exist_ok=True)

TILES = {'brick': 'tex-brick-v1.png', 'slate': 'tex-slate-v1.png', 'cladding': 'tex-cladding-v1.png',
         'asphalt': 'tex-asphalt-v1.png', 'concrete': 'tex-concrete-v1.png'}
DECALS = {'truck-wheel-face': ('truck-wheel-face-v1.png', (512, 512)), 'truck-headlamp': ('truck-headlamp-v1.png', (512, 256)),
          'truck-taillight': ('truck-taillight-v1.png', (256, 128)), 'truck-grille': ('truck-grille-v1.png', (512, 170))}
BACKDROPS = {'foundry-interior': 'foundry-interior-v1.png', 'warehouse-interior': 'warehouse-interior-v1.png'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seam_ratio(a, axis):
    """Edge-to-edge difference relative to the typical neighbouring-pixel difference."""
    if axis == 0:
        edge = np.abs(a[0] - a[-1]).mean()
        inner = np.abs(np.diff(a, axis=0)).mean()
    else:
        edge = np.abs(a[:, 0] - a[:, -1]).mean()
        inner = np.abs(np.diff(a, axis=1)).mean()
    return float(edge / max(inner, 1e-6))


def heal(a, axis, band=.12):
    """Shift by half so the wrap seam sits centrally, then feather the original over it."""
    n = a.shape[axis]
    shifted = np.roll(a, n // 2, axis=axis)
    w = int(n * band)
    t = np.zeros(n)
    centre = n // 2
    ramp = np.clip(1 - np.abs(np.arange(n) - centre) / w, 0, 1)
    t = ramp * ramp * (3 - 2 * ramp)
    shape = [1, 1, 1]
    shape[axis] = n
    t = t.reshape(shape)
    return shifted * (1 - t) + a * t


manifest = []
for key, name in TILES.items():
    src = SRC / name
    a = np.asarray(Image.open(src).convert('RGB'), dtype=np.float64)
    ops = []
    for axis, label in ((0, 'vertical'), (1, 'horizontal')):
        r = seam_ratio(a, axis)
        if r > 1.6:
            a = heal(a, axis)
            ops.append(f'{label} wrap seam healed (edge/inner ratio {r:.2f} -> {seam_ratio(a, axis):.2f})')
    image = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((512, 512), Image.LANCZOS)
    out = OUT / f'{key}.png'
    image.save(out)
    manifest.append({'texture': out.name, 'original': name, 'original_sha256': sha(src), 'size': [512, 512],
                     'operations': ops + ['Lanczos resize to 512 px'], 'sha256': sha(out)})
for key, name in BACKDROPS.items():
    src = SRC / name
    image = Image.open(src).convert('RGB')
    image = image.resize((1024, round(1024 * image.height / image.width)), Image.LANCZOS)
    out = OUT / f'{key}.png'
    image.save(out)
    manifest.append({'texture': out.name, 'original': name, 'original_sha256': sha(src), 'size': list(image.size),
                     'operations': ['Lanczos resize to 1024 px wide'], 'sha256': sha(out)})
for key, (name, size) in DECALS.items():
    src = SRC / name
    out = OUT / f'{key}.png'
    Image.open(src).convert('RGB').resize(size, Image.LANCZOS).save(out)
    manifest.append({'texture': out.name, 'original': name, 'original_sha256': sha(src), 'size': list(size),
                     'operations': [f'Lanczos resize to {size[0]}x{size[1]} px'], 'sha256': sha(out)})
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
for m in manifest:
    print(m['texture'], m['operations'])
