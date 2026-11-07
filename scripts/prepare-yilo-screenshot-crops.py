"""Measure empty native screenshot margins for website-only presentation crops.

Requires Pillow. Original PNGs and downloadable Press Kit files stay intact.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'scripts/assets/presskit/yilo'
NAMES = ('learning-record.png', 'learning-settings.png', 'language-selection.png')
PADDING = 16
crops = {}
for folder in sorted(path for path in SOURCE.iterdir() if path.is_dir()):
    for name in NAMES:
        path = folder / name
        picture = Image.open(path).convert('RGB')
        width, height = picture.size
        box = (0, 0, width, height)
        if name != 'learning-record.png':
            background = Image.new('RGB', picture.size, picture.getpixel((0, 0)))
            red, green, blue = ImageChops.difference(picture, background).split()
            mask = ImageChops.lighter(red, ImageChops.lighter(green, blue)).point(lambda value: 255 if value > 8 else 0)
            content = mask.getbbox()
            assert content, path
            box = (max(0, content[0] - PADDING), max(0, content[1] - PADDING),
                   min(width, content[2] + PADDING), min(height, content[3] + PADDING))
        crops[f'{folder.name}/{name}'] = dict(
            sourceSHA256=hashlib.sha256(path.read_bytes()).hexdigest(),
            originalWidth=width, originalHeight=height,
            x=box[0], y=box[1], width=box[2]-box[0], height=box[3]-box[1])

receipt = dict(method='Website CSS viewport only; native PNG pixels unchanged. Light-image margins use >8 RGB difference from the corner background, plus 16 source pixels of padding.', crops=crops)
(ROOT / 'scripts/assets/yilo/screenshot-crops.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(f'Measured {len(crops)} native screenshots; original PNGs unchanged.')
