"""Web-sized leaf and dust sprites (v2) from the unchanged imagegen v1 originals.

Sizes follow the largest on-screen use (leaves about 50 device px, dust about 320).
Resampling is done on premultiplied alpha so leaf edges do not darken. Output is
lossy WebP with alpha. Originals stay in scripts/assets/fondfont/blender-v2/retired-public/.
"""
from pathlib import Path
import subprocess, tempfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'scripts/assets/fondfont/blender-v2/retired-public'
OUT = ROOT / 'public/v/fondfont/blender-v2'
SIZES = {'wind-leaf': (256, 384), 'drift-dust': (768, 384)}
for name, size in SIZES.items():
    image = Image.open(SRC / f'{name}-v1.png').convert('RGBA').convert('RGBa').resize(size, Image.LANCZOS).convert('RGBA')
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / 'sprite.png'
        image.save(png)
        subprocess.run(['cwebp', '-quiet', '-q', '86', '-alpha_q', '95', '-m', '6', str(png), '-o', str(OUT / f'{name}-v2.webp')], check=True)
    print(name, size, (OUT / f'{name}-v2.webp').stat().st_size, 'bytes')
