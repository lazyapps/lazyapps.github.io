"""Export silent, localized website previews from FondFont's real app footage."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from PIL import Image

SITE = Path(__file__).resolve().parents[1]
LOCALES = {'en': 'en-US', 'zh-hans': 'zh-Hans', 'zh-hant': 'zh-Hant',
           'ja': 'ja', 'ko': 'ko', 'fr': 'fr-FR', 'de': 'de-DE'}


def run(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *map(str, args)], check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True, help='FondFont app repository')
    args = parser.parse_args()
    source = args.source.resolve() / 'AppStore'
    target = SITE / 'public/v/fondfont'
    target.mkdir(parents=True, exist_ok=True)
    manifest = {'sourceProject': 'FondFont / iOSFontInstaller', 'assets': []}
    for locale, store in LOCALES.items():
        for device, width in [('ipad', 900), ('iphone', 540)]:
            footage = source / 'Preview/Remotion/public/footage' / device / store
            install = '04-select.mp4' if device == 'ipad' else '04-install.mp4'
            clips = [footage / f for f in [install, '01-library.mp4']]
            with tempfile.TemporaryDirectory() as temporary:
                listing = Path(temporary) / 'clips.txt'
                listing.write_text(''.join(f"file '{p}'\n" for p in clips))
                output = target / f'preview-{device}-{locale}.mp4'
                # The iPad capture starts by closing the preceding comparison popover.
                # Begin directly on batch selection, then hold the library at the end.
                cut = 2.5 if device == 'ipad' else 0
                run('-f', 'concat', '-safe', '0', '-i', listing, '-an', '-vf', f'trim=start={cut},setpts=PTS-STARTPTS,scale={width}:-2,fps=24,tpad=stop_mode=clone:stop_duration={cut}', '-t', '12',
                    '-c:v', 'libx264', '-threads', '2', '-preset', 'slow', '-crf', '24',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', output)
            screenshot = source / 'Screenshots/public/screenshots/apple' / device / store / '04.png'
            image = Image.open(screenshot).convert('RGB')
            image.thumbnail((width, 1600), Image.Resampling.LANCZOS)
            image.save(target / f'preview-{device}-{locale}.jpg', quality=88, optimize=True)
            manifest['assets'].append({'output': output.name, 'bytes': output.stat().st_size,
                'sources': [{'file': str(p.relative_to(source)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in clips]})
        for name, shot in [('waterfall', '02.png'), ('glyphs', '03.png'), ('compare', '05.png')]:
            image = Image.open(source / 'Screenshots/public/screenshots/apple/ipad' / store / shot).convert('RGB')
            # Keep the real app's header and active workspace; omit the long metadata below.
            image = image.crop((0, 0, image.width, min(image.height, round(image.width * .83))))
            image.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
            image.save(target / f'{name}-{locale}.jpg', quality=88, optimize=True)
        guide = source / 'Preview/Remotion/public/footage/iphone' / store / '04-install.mp4'
        run('-ss', '3', '-i', guide, '-frames:v', '1', '-vf', 'scale=540:-2',
            target / f'install-guide-{locale}.jpg')
        manifest['assets'].append({'output': f'install-guide-{locale}.jpg',
            'source': str(guide.relative_to(source)), 'timeSeconds': 3,
            'sha256': hashlib.sha256(guide.read_bytes()).hexdigest()})
        print(f'exported {locale}', flush=True)
    (target / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
