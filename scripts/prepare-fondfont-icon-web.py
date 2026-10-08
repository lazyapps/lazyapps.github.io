"""Small web derivatives of the native FondFont header icon (fondfont-web-icon.png, 256 px).

The header shows it at 32 CSS px and the favicon needs at most 64 px, so ship a 128 px
WebP (2x/4x displays) and a 64 px PNG favicon. Scaling and encoding only.
"""
from pathlib import Path
import subprocess, tempfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src/assets/img/fondfont-web-icon.png'
icon = Image.open(SRC).convert('RGBA').convert('RGBa')
with tempfile.TemporaryDirectory() as tmp:
    png = Path(tmp) / 'icon.png'
    icon.resize((128, 128), Image.LANCZOS).convert('RGBA').save(png)
    subprocess.run(['cwebp', '-quiet', '-q', '92', '-alpha_q', '100', '-m', '6', str(png), '-o', str(ROOT / 'src/assets/img/fondfont-web-icon-128.webp')], check=True)
icon.resize((64, 64), Image.LANCZOS).convert('RGBA').save(ROOT / 'src/assets/img/fondfont-web-icon-64.png', optimize=True)
for name in ['fondfont-web-icon-128.webp', 'fondfont-web-icon-64.png']:
    print(name, (ROOT / 'src/assets/img' / name).stat().st_size, 'bytes')
