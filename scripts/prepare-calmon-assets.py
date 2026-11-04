"""Render calmon media from original native assets. Native capture needs --app-source and Xcode."""
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/calmon'
ICON = ROOT / 'scripts/assets/native-icons/calmon/AppIcon.icon'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture_native(source, panels_only=False):
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        executable = temp / 'Capture.app/Contents/MacOS/capture'
        executable.parent.mkdir(parents=True)
        resources = temp / 'Capture.app/Contents/Resources'
        resources.mkdir()
        fonts = sorted((source / 'Sources/Fonts').glob('*'))
        for font in fonts:
            shutil.copyfile(font, resources / font.name)
        app_resources = source / 'build/Build/Products/Debug/calmon-dev.app/Contents/Resources'
        shutil.copyfile(app_resources / 'Assets.car', resources / 'Assets.car')
        for localization in app_resources.glob('*.lproj'):
            shutil.copytree(localization, resources / localization.name)
        (temp / 'Capture.app/Contents/Info.plist').write_text('<?xml version="1.0"?><plist version="1.0"><dict><key>CFBundleExecutable</key><string>capture</string><key>CFBundleIdentifier</key><string>com.lazyapps.calmon-media</string></dict></plist>')
        framework = source / 'build/Build/Products/Debug'
        files = sorted((source / 'Sources').glob('*.swift'))
        copied = []
        for path in files:
            target = temp / path.name
            target.write_text(path.read_text().replace('@main\n', ''))
            copied.append(str(target))
        shutil.copyfile(ASSETS / 'capture-leader.swift', temp / 'main.swift')
        subprocess.run(['xcrun', 'clang', '-c', str(source / 'Sources/PrivateAPIs.m'), '-o', str(temp / 'native.o')], check=True)
        sdk = subprocess.check_output(['xcrun', '--sdk', 'macosx', '--show-sdk-path'], text=True).strip()
        developer = Path(subprocess.check_output(['xcode-select', '-p'], text=True).strip())
        plugins = developer / 'Platforms/MacOSX.platform/Developer/usr/lib/swift/host/plugins'
        subprocess.run(['xcrun', '--sdk', 'macosx', 'swiftc', '-sdk', sdk, '-plugin-path', str(plugins), '-swift-version', '6', '-import-objc-header', str(source / 'Sources/calmon-Bridging-Header.h'),
                        '-F', str(framework), '-framework', 'Sparkle', '-Xlinker', '-rpath', '-Xlinker', str(framework),
                        *copied, str(temp / 'main.swift'), str(temp / 'native.o'), '-o', str(executable)], check=True)
        output = ROOT / 'scripts/assets/presskit/calmon-leader-keys.png'
        languages = json.loads((ROOT / 'src/content/presskit-supported-languages.json').read_text())['calmon']['tags']
        captures = []
        for language in languages:
            target = output if language == 'en' else ROOT / f'scripts/assets/presskit/calmon-leader-keys-{language}.png'
            subprocess.run([str(executable), str(target), str(resources / 'Tiny5.ttf'),
                            '-AppleLanguages', f'({language})'], check=True)
            captures.append({'source': str(target.relative_to(ROOT)), 'sha256': digest(target),
                             'contentLanguage': language, 'type': 'native',
                             'operation': 'Native LeaderHelpView rendered with the app localization and default commands. Original PNG pixels retained.',
                             'originalSource': str(source / 'Sources/AppJump.swift')})
        record = {'checkedOn': datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat(),
                  'appSourceCommit': subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip(),
                  'captures': captures,
                  'inputHashes': {str(path.relative_to(source)): digest(path) for path in files + fonts + [source / 'Sources/Localizable.xcstrings']},
                  'captureScriptSha256': digest(ASSETS / 'capture-leader.swift')}
        (ASSETS / 'capture-source.json').write_text(json.dumps(record, indent=2) + '\n')
        records = ROOT / 'scripts/assets/presskit/screenshot-sources.json'
        data = json.loads(records.read_text())
        data['calmon'] = {key: record[key] for key in ['checkedOn', 'appSourceCommit', 'captures']}
        # The media catalog stores one file per byte-identical image, using its last locale record.
        data['calmon']['captures'] = list({item['sha256']: item for item in captures}.values())
        records.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        print(f'Exported {len(captures)} localized native panels.')
        if panels_only:
            return
        hero = ROOT / 'src/assets/img/calmon-onboarding'
        hero.mkdir(exist_ok=True)
        for language in ['en', 'zh-Hans']:
            target = output if language == 'en' else temp / 'leader-zh-Hans.png'
            subprocess.run([str(executable), str(target), str(resources / 'Tiny5.ttf'),
                            str(hero / f'key-panel-{language}.png'), str(hero / 'symbols.png'),
                            '-AppleLanguages', f'({language})'], check=True)
            geometry = json.loads((hero / f'key-panel-{language}.json').read_text())
            for variant, metrics in geometry.items():
                rows = {}
                for region in metrics['regions']:
                    rows.setdefault((region['section'], region['row']), []).append(region)
                metrics['rows'] = []
                metrics['headers'] = []
                for (section, row), regions in rows.items():
                    caps = [r for r in regions if not r['title']]
                    origin = min(r['rect'][0] for r in metrics['regions'] if r['section'] in ([0, 1, 2] if section < 3 else [3, 4]) and r['title'])
                    if section == 3:
                        for region in regions:
                            if region['action'] == 'space':
                                region['action'] = {0: 'float', 1: 'full', 2: 'pin', 5: 'tile-all', 7: 'send-menu'}.get(row, region['action'])
                    metrics['rows'].append({'section': section, 'row': row, 'rect': [origin, caps[0]['rect'][1], min(r['rect'][0] for r in caps) - origin - 10, caps[0]['rect'][3]]})
                    if row == 0:
                        right = max(r['rect'][0] + r['rect'][2] for r in metrics['regions'] if r['section'] == section)
                        metrics['headers'].append({'section': section, 'rect': [origin, caps[0]['rect'][1] - 27, right - origin, 21]})
                stem = f'key-panel-{language}-{variant}'
                atlas = Image.open(hero / f'{stem}.png').convert('RGBA')
                for index, region in enumerate(metrics['regions']):
                    lit = hero / f'{stem}-lit-{index}.png'
                    if not lit.exists():
                        continue
                    x, y, w, h = region['rect']
                    box = tuple(round(v * 2) for v in (x, y, x + w, y + h))
                    image = Image.open(lit).convert('RGBA')
                    atlas.paste(image.crop(box), box[:2])
                    lit.unlink()
                atlas.save(hero / f'{stem}-lit.png', optimize=True)
            (hero / f'key-panel-{language}.json').write_text(json.dumps(geometry, ensure_ascii=False, indent=2) + '\n')
        wallpaper = source / 'Sources/Assets.xcassets/OnboardingDesktop.imageset/GoldenGateSunset.jpg'
        Image.open(wallpaper).convert('RGB').resize((1600, 900), Image.Resampling.LANCZOS).save(hero / 'desktop.jpg', quality=88, optimize=True)
        (ASSETS / 'onboarding-source.json').write_text(json.dumps({
            'checkedOn': datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat(),
            'method': 'Web choreography follows calmon onboarding. Key panels rendered by native OnboardingKeyPanel in English and Simplified Chinese; Deck marks rendered by native TabVisualMetrics.drawMark at 48 pt and 2×; symbols exported from the same SF Symbols used by the native scene. Desktop uses the app onboarding wallpaper, resized for the web. These assets do not contain app source.',
            'wallpaperSource': str(wallpaper), 'wallpaperSourceSha256': digest(wallpaper),
            'nativeSceneSourceSha256': digest(source / 'Sources/OnboardingView.swift'),
            'outputs': {str(path.relative_to(ROOT)): digest(path) for path in sorted(hero.iterdir()) if path.is_file()}
        }, ensure_ascii=False, indent=2) + '\n')


def render_brand():
    # Exported from the app's actual CGPath contours, not redrawn or traced from a bitmap.
    source = ROOT / 'scripts/assets/native-icons/calmon/lettering.svg'
    vector = ROOT / 'scripts/assets/presskit/vectors/calmon-lettering.svg'
    shutil.copyfile(source, vector)
    inputs = {str(source.relative_to(ROOT)): digest(source)}
    for path in sorted(ICON.rglob('*')):
        if path.is_file():
            inputs[str(path.relative_to(ROOT))] = digest(path)
    vectors = ROOT / 'scripts/assets/presskit/vector-sources.json'
    records = json.loads(vectors.read_text())
    records['calmon'] = [{'output': str(vector.relative_to(ROOT)), 'sha256': digest(vector), 'inputs': inputs,
        'method': 'Exact native rounded CGPath contours exported by render-icon-lettering.swift, with the same six green diagonal bands as the current icon. No raster tracing or embedded bitmap; native glass, lighting and backing omitted.'}]
    vectors.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        subprocess.run(['node', '--input-type=module', '-e', "import sharp from 'sharp'; await sharp(process.argv[1]).resize({height:500}).png().toFile(process.argv[2]);", str(vector), str(temp / 'symbol.png')], cwd=ROOT, check=True)
        mark = Image.open(temp / 'symbol.png').convert('RGBA')
        mark = mark.crop(mark.getchannel('A').getbbox())
        font = instantiateVariableFont(TTFont(ROOT / 'src/assets/fonts/sofia-sans-xcond-latin.woff2'), {'wght': 900}, inplace=True)
        font.flavor = None
        font.save(temp / 'sofia.ttf')
        face = ImageFont.truetype(str(temp / 'sofia.ttf'), 500)
        title = Image.new('RGBA', (2000, 650))
        draw = ImageDraw.Draw(title)
        x = 0
        for letter in 'Calmon':
            draw.text((x, 0), letter, font=face, fill='#171717')
            x += face.getlength(letter) - 5
        title = title.crop(title.getchannel('A').getbbox())
        scale, gap = 3, 24 * 3
        height = round((540 * scale - gap) / (mark.width / mark.height + title.width / title.height))
        mark = mark.resize((round(height * mark.width / mark.height), height), Image.Resampling.LANCZOS)
        title = title.resize((round(height * title.width / title.height), height), Image.Resampling.LANCZOS)
        canvas = Image.new('RGB', (1200 * scale, 630 * scale), '#f8f8f6')
        noise = Image.open(ROOT / 'src/assets/img/noise.png').convert('L').resize((125 * scale, 125 * scale), Image.Resampling.BICUBIC)
        noise = noise.point(lambda value: round(max(0, min(255, (value - 127.5) * 1.25 + 127.5)) * .6)).convert('RGBA')
        noise.putalpha(round(255 * .09))
        for y in range(0, canvas.height, noise.height):
            for x in range(0, canvas.width, noise.width):
                canvas.paste(noise, (x, y), noise)
        width = mark.width + gap + title.width
        x, y = round((canvas.width - width) / 2), round((canvas.height - height) / 2)
        canvas.paste(mark, (x, y), mark)
        canvas.paste(title, (x + mark.width + gap, y), title)
        output = ROOT / 'src/assets/img/calmon-opengraph-shared.png'
        canvas.resize((1200, 630), Image.Resampling.LANCZOS).save(output, optimize=True)
        bounds = [round(x / scale), round(y / scale), round(width / scale), round(height / scale)]
        assert bounds[0] >= 285 and bounds[0] + bounds[2] <= 915
        (ASSETS / 'opengraph-source.json').write_text(json.dumps({'symbolSource': str(vector.relative_to(ROOT)), 'symbolSha256': digest(vector),
            'output': str(output.relative_to(ROOT)), 'sha256': digest(output), 'size': [1200, 630], 'safeRect': [285, 0, 630, 630],
            'contentBounds': bounds, 'languages': ['en', 'zh-Hans'], 'method': 'Native letter contours plus website Sofia Sans Extra Condensed 900; shared unchanged brand name.'}, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app-source', type=Path)
    parser.add_argument('--panels-only', action='store_true')
    args = parser.parse_args()
    if args.app_source:
        capture_native(args.app_source, args.panels_only)
    if not args.panels_only:
        render_brand()
