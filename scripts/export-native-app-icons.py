"""Export full native app icons from preserved production assets, without retouching."""
import argparse
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--product', choices=sources, help='Export only this product')
    args = parser.parse_args()
    for slug, record in sources.items():
        if args.product and slug != args.product:
            continue
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
        if slug == 'calmon':
            dark_output = ROOT / 'src/assets/img/calmon-icon-dark.png'
            subprocess.run([ICTOOL, str(source), '--export-image', '--output-file', str(dark_output),
                            '--platform', 'macOS', '--rendition', 'Dark', '--width', '1024',
                            '--height', '1024', '--scale', '1', '--design-generation', '27'],
                           check=True, capture_output=True)
            record['webRenditions'] = [{'output': str(dark_output.relative_to(ROOT)),
                'sha256': hashlib.sha256(dark_output.read_bytes()).hexdigest(),
                'size': 1024, 'scale': 1, 'rendition': 'Dark'}]
            menu_source = source.parent / 'MenuBarIcon.imageset/MenuBarIcon@2x.png'
            menu_output = ROOT / 'scripts/assets/presskit/calmon-menubar.png'
            shutil.copyfile(menu_source, menu_output)
            record['menuBar'] = {'source': str(menu_source.relative_to(ROOT)),
                'output': str(menu_output.relative_to(ROOT)), 'size': [44, 44], 'points': [22, 22], 'markPoints': [16, 16],
                'sha256': hashlib.sha256(menu_output.read_bytes()).hexdigest()}
        print(f'{slug}: {width}×{height} · {record["method"]}')
    SOURCES.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
