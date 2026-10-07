"""Draw text-free planar tracking anchors for the H3 software-workspace handoff."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v6'
ASSETS.mkdir(parents=True, exist_ok=True)
for name, points in {
    'start': [(110, 86), (660, 122), (650, 772), (120, 810)],
    'end': [(104, 80), (664, 80), (664, 784), (104, 784)],
}.items():
    canvas = Image.new('RGB', (768, 864), '#f8f8f6')
    draw = ImageDraw.Draw(canvas)
    draw.polygon(points, fill='#d8d8d4')
    canvas.save(ASSETS / f'{name}-anchor.png')
