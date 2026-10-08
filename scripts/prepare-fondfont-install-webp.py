"""Web copies of the genuine installation-guide captures.

The page shows each capture at most 280 CSS px wide (420 px in the zoom viewer), so
it ships 600 px and 1000 px WebP derivatives of the unchanged 1206x2622 Argent PNGs
in scripts/assets/fondfont/install-capture-20261007/. Only scaling and encoding are
applied: no crop, retouch or generated UI.
"""
from pathlib import Path
import hashlib, json, subprocess, tempfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / 'scripts/assets/fondfont/install-capture-20261007'
OUT = ROOT / 'public/v/fondfont/install'
MANIFEST = ROOT / 'scripts/assets/fondfont/install-screenshots.json'
WIDTHS = {600: 82, 1000: 84}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads(MANIFEST.read_text())
manifest['processing'] = ('Unchanged original native PNG captures, scaled (Lanczos) and encoded as WebP for the web '
                          'at 600 and 1000 px wide. No retouch, crop, or generated UI.')
for record in manifest['records']:
    source = ROOT / record['source']
    assert sha(source) == record['sha256'], f'{source} changed'
    image = Image.open(source).convert('RGB')
    outputs = []
    for width, quality in WIDTHS.items():
        height = round(image.height * width / image.width)
        target = OUT / record['locale'] / f"{record['step']}-{width}.webp"
        with tempfile.TemporaryDirectory() as tmp:
            png = Path(tmp) / 'shot.png'
            image.resize((width, height), Image.LANCZOS).save(png)
            subprocess.run(['cwebp', '-quiet', '-q', str(quality), '-m', '6', '-sharp_yuv', str(png), '-o', str(target)], check=True)
        outputs.append({'path': str(target.relative_to(ROOT)), 'width': width, 'height': height, 'bytes': target.stat().st_size, 'sha256': sha(target)})
    record['output'] = outputs
    old = OUT / record['locale'] / f"{record['step']}.png"
    if old.exists():
        old.unlink()
MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
total = sum(o['bytes'] for r in manifest['records'] for o in r['output'] if o['width'] == 600)
print(len(manifest['records']), 'captures;', total // 1024, 'KiB for all 600 px copies')
