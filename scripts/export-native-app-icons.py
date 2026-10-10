"""Export full native app icons from preserved production assets, without retouching."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / 'scripts/assets/native-icons/sources.json'
ICTOOL = '/Applications/Xcode.app/Contents/Applications/Icon Composer.app/Contents/Executables/ictool'


def main():
    sources = json.loads(SOURCES.read_text())
    for slug, record in sources.items():
        source = ROOT / record['source']
        output = ROOT / record['output']
        files = sorted(path for path in source.rglob('*') if path.is_file() and not path.name.startswith('.')) if source.is_dir() else [source]
        record['sourceHashes'] = {
            str(path.relative_to(source)) if source.is_dir() else path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in files
        }
        if source.is_dir():
            subprocess.run([
                ICTOOL, str(source), '--export-image', '--output-file', str(output),
                '--platform', record['platform'], '--rendition', 'Default',
                '--width', '1024', '--height', '1024', '--scale', '1',
                '--design-generation', '27',
            ], check=True, capture_output=True)
        else:
            shutil.copyfile(source, output)
        data = output.read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n', f'{slug}: expected PNG'
        width, height = struct.unpack('>II', data[16:24])
        assert (width, height) == (1024, 1024), f'{slug}: expected full-resolution icon'
        record['outputSha256'] = hashlib.sha256(data).hexdigest()
        record['size'] = [width, height]
        record['rendition'] = 'Default'
        record['designGeneration'] = 27 if source.is_dir() else None
        print(f'{slug}: {width}×{height} · {record["method"]}')
    SOURCES.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
