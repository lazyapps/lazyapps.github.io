"""Compare matching lossless browser font-review frames (requires Pillow)."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageChops

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('before', type=Path)
parser.add_argument('after', type=Path)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
names = {path.name for path in args.before.glob('*.png')}
assert names and names == {path.name for path in args.after.glob('*.png')}, 'Frame lists must match'
rows = []
for name in sorted(names):
    before = Image.open(args.before / name).convert('RGB')
    after = Image.open(args.after / name).convert('RGB')
    assert before.size == after.size, f'{name}: viewport changed'
    red, green, blue = ImageChops.difference(before, after).split()
    mask = ImageChops.lighter(red, ImageChops.lighter(green, blue))
    rows.append(dict(frame=name, changedPixels=before.width * before.height - mask.histogram()[0], bounds=mask.getbbox()))
report = json.dumps(dict(frames=len(rows), differences=rows), indent=2) + '\n'
if args.output:
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report)
else:
    print(report, end='')
raise SystemExit(any(row['changedPixels'] for row in rows))
