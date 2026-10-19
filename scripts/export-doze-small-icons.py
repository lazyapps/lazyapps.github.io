"""Render lossless web icons at their actual display sizes from the native source."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ICTOOL = '/Applications/Xcode.app/Contents/Applications/Icon Composer.app/Contents/Executables/ictool'
registry = ROOT / 'scripts/assets/native-icons/sources.json'
records = json.loads(registry.read_text())
record = records['doze']
compact = record['compactSource']
source = ROOT / compact['source']
compact['sourceHashes'] = {
    str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in sorted(source.rglob('*')) if path.is_file()
}
renditions = []
for size in [16, 22, 28, 32]:
    for scale in [1, 2]:
        output = ROOT / f'src/assets/img/doze/icon-small-{size}-{scale}x.png'
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([ICTOOL, str(source), '--export-image', '--output-file', str(output),
                        '--platform', 'macOS', '--rendition', 'Default', '--width', str(size), '--height', str(size),
                        '--scale', str(scale), '--design-generation', '27'], check=True, capture_output=True)
        data = output.read_bytes()
        assert struct.unpack('>II', data[16:24]) == (size * scale, size * scale)
        renditions.append(dict(size=size, scale=scale, output=str(output.relative_to(ROOT)), sha256=hashlib.sha256(data).hexdigest()))
record['webRenditions'] = renditions
registry.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
print('Exported 8 lossless native icon renditions (1× and 2×).')
