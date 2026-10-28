"""Export Doze's six native menu bar appearances as transparent PNGs and SVGs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/doze'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--project', type=Path, help='Import Sources/StatusIcon.swift from the native app repository first')
args = parser.parse_args()
snapshot = ASSETS / 'StatusIcon.swift'
record_path = ASSETS / 'menubar-source.json'
record = json.loads(record_path.read_text())
if args.project:
    shutil.copyfile(args.project / 'Sources/StatusIcon.swift', snapshot)
    record['commit'] = subprocess.check_output(['git', '-C', str(args.project), 'rev-parse', 'HEAD'], text=True).strip()
record['sourceSnapshot'] = str(snapshot.relative_to(ROOT))
record['sourceSha256'] = hashlib.sha256(snapshot.read_bytes()).hexdigest()

with tempfile.TemporaryDirectory(prefix='doze-menubar-') as directory:
    executable = Path(directory) / 'export-menubar'
    export_source = Path(directory) / 'StatusIcon.swift'
    export_source.write_text(snapshot.read_text() + '\nextension StatusIcon {\n    static func vectorPathForExport(smiling: Bool) -> CGPath { monogram(smiling: smiling) }\n}\n')
    subprocess.run(['xcrun', 'swiftc', str(export_source), str(ASSETS / 'export-menubar.swift'), '-o', str(executable)], check=True)
    subprocess.run([str(executable), str(ROOT / record['output'])], check=True)

record['outputSha256'] = hashlib.sha256((ROOT / record['output']).read_bytes()).hexdigest()
record['note'] = 'Six original native template appearances at 2× (44 × 40 pixels, 22 × 20 points). Black glyphs on transparency; manually paused variants preserve native 45% opacity. Media variants have a centered circular play marker. Active, dimmed and attention share the same appearance. Keep Computer Awake changes the eyes. macOS adapts template color for dark menu bars. Companion system symbols are not Press Kit assets.'
record['variants'] = []
for key, state, awake, filename in [
    ('active', 'active', False, 'doze-menubar.png'),
    ('keepAwake', 'active', True, 'doze-menubar-keep-awake.png'),
    ('paused', 'paused', False, 'doze-menubar-paused.png'),
    ('pausedKeepAwake', 'paused', True, 'doze-menubar-paused-keep-awake.png'),
    ('media', 'media', False, 'doze-menubar-media.png'),
    ('mediaKeepAwake', 'media', True, 'doze-menubar-media-keep-awake.png'),
]:
    source = ROOT / 'src/assets/img' / filename
    data = source.read_bytes()
    vector = source.with_suffix('.svg')
    record['variants'].append(dict(key=key, state=state, keepAwake=awake,
        equivalentStates=['active', 'dimmed', 'attention'] if state == 'active' else [state],
        output=str(source.relative_to(ROOT)), sha256=hashlib.sha256(data).hexdigest(),
        size=list(struct.unpack('>II', data[16:24])), scale=2,
        svgOutput=str(vector.relative_to(ROOT)), svgSha256=hashlib.sha256(vector.read_bytes()).hexdigest()))
for symbol in record['systemSymbols']:
    symbol['sha256'] = hashlib.sha256((ROOT / symbol['output']).read_bytes()).hexdigest()
record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print('Exported 6 native menu bar appearances as 2× PNGs and exact-path SVGs; hashes recorded.')
