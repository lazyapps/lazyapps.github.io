"""Prepare stable press downloads and deterministic ZIPs from reviewed local assets."""
from pathlib import Path
import struct
import hashlib
import json
import shutil
import subprocess
import posixpath
import zipfile

ROOT = Path(__file__).resolve().parents[1]
KITS = json.loads(subprocess.check_output(['node', str(ROOT / 'scripts/print-presskit-catalog.mjs')], text=True))
CONTACT = 'lazyapps.feedback@gmail.com'

def image_size(data):
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        width, height = struct.unpack('>II', data[16:24])
        return width, height, 'PNG'
    if data.startswith(b'\xff\xd8'):
        i = 2
        while i < len(data):
            assert data[i] == 255, 'Invalid JPEG marker'
            while data[i] == 255:
                i += 1
            marker = data[i]
            i += 1
            length = int.from_bytes(data[i:i+2], 'big')
            if marker in (0xC0, 0xC1, 0xC2):
                height, width = struct.unpack('>HH', data[i+3:i+7])
                return width, height, 'JPEG'
            i += length
    raise ValueError('Press assets must be PNG or JPEG')

for kit in KITS:
    out = ROOT / 'public/presskit' / kit['slug']
    out.mkdir(parents=True, exist_ok=True)
    previous = out / 'manifest.json'
    if previous.exists():
        data = json.loads(previous.read_text())
        old_files = data if isinstance(data, list) else data['files']
        for entry in old_files:
            old = out / entry.get('path', entry.get('filename'))
            assert out in old.parents, 'Unsafe generated path'
            old.unlink(missing_ok=True)
        if isinstance(data, dict):
            for tag in data['languages']:
                (out / tag / 'README.md').unlink(missing_ok=True)
    for filename in ['README.en.md', 'README.zh-Hans.md', 'README.txt']:
        (out / filename).unlink(missing_ok=True)
    files = []
    for asset in kit['files']:
        source = ROOT / asset['source']
        dest = out / asset['path']
        assert out in dest.parents and source.is_file(), f'Invalid asset: {asset}'
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        width, height, fmt = image_size(source.read_bytes())
        files.append(dict(path=asset['path'], contentLanguage=asset['contentLanguage'], width=width, height=height, format=fmt,
                          bytes=dest.stat().st_size, sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
    readmes = []
    for locale in kit['locales']:
        tag = locale['tag']
        headings = locale['headings']
        website = 'https://lazyapps.com' + locale['website']
        press = f"https://lazyapps.com/{kit['slug']}/presskit/#{tag}"
        lines = [f"# {locale['name']} — {headings[0]}", '',
                 f"- {headings[1]}: [{website}]({website})",
                 f"- {headings[2]}: [{press}]({press})",
                 f"- {headings[3]}: {locale['platform']}", f"- {headings[4]}: {locale['availability']}",
                 f"- {headings[5]}: [{CONTACT}](mailto:{CONTACT})", '',
                 f"## {headings[6]}", '', locale['summary'], '', locale['description'], '',
                 f"## {headings[7]}", '']
        for link in locale['links']:
            url = ('https://lazyapps.com' if link['url'].startswith('/') else '') + link['url']
            lines += [f"- [{link['label']}]({url})"]
        lines += ['', f"## {headings[8]}", '']
        for asset in locale['assets']:
            metadata = next(f for f in files if f['path'] == asset['path'])
            relative = posixpath.relpath(asset['path'], tag)
            lines += [f"### {asset['label']}", '', f"[{asset['filename']}]({relative})", '',
                      f"{metadata['width']} × {metadata['height']} · {metadata['format']}", '',
                      asset['note'], '']
        lines += [f"## {headings[9]}", '', locale['usage'], '']
        filename = f'{tag}/README.md'
        dest = out / filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text('\n'.join(lines), encoding='utf-8')
        readmes.append(filename)
    manifest = dict(languages=[locale['tag'] for locale in kit['locales']], files=files)
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    archive = out / (kit['slug'] + '-presskit.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for filename in ['manifest.json'] + sorted(readmes + [f['path'] for f in files]):
            info = zipfile.ZipInfo(filename, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, (out / filename).read_bytes(), compresslevel=9)
    print(f"presskit: {kit['slug']} · {len(readmes)} languages · {len(files)} unique assets · {archive.stat().st_size:,} bytes")
