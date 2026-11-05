#!/usr/bin/env python3
"""Export the key reference copy and a renamed web-font subset from the calmon app."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(source):
    catalog_path = source / 'Sources/Localizable.xcstrings'
    catalog = json.loads(catalog_path.read_text())['strings']
    sections = [
        ('Focus · ⇧ Move', [('Column', ['←', '→']), ('Window', ['↑', '↓']), ('Desktop', ['1–9'])]),
        ('Column', [('Move Into or Out', [',', '.']), ('Width', ['-', '=']), ('Height', ['[', ']']), ('Focus Pinned', ['TAB'])]),
        ('Labels', [('Go to Window', ['A', 'S', 'D', '…']), ('Bring Below', ['⇧', 'A', '…'])]),
        ('Space Then', [('Float or Tile', ['F']), ('Full Screen', ['S']), ('Pin or Unpin', ['P']),
                        ('Join/Leave App Stack', ['J', '/', 'X']), ('Add/Remove Pin Deck', ['A', '/', 'R']),
                        ('Tile All', ['T']), ('New/Delete Desktop', ['N', '/', 'D']), ('All to Desktop', ['M', '1–9'])]),
        ('Actions', [('Settings', ['CMD', ',']), ('Exit', ['ESC'])]),
    ]
    def localized(text, language):
        return text if language == 'en' else catalog[text]['localizations'][language]['stringUnit']['value']
    data = {language: [
        {'title': localized(title, language), 'rows': [
            {'title': localized(label, language), 'keys': keys} for label, keys in rows
        ]} for title, rows in sections
    ] for language in ['en'] + sorted({language for entry in catalog.values() for language in entry.get('localizations', {})} - {'en'})}
    data_path = ROOT / 'src/components/calmon-key-panel.json'
    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    terms = [
        'Leader Mode', 'Key Panel', 'Settings', 'Keyboard', 'Gestures', 'Advanced',
        'Show after', 'Never', 'Check for Updates…', 'Layout map', 'Accessibility',
        'Device Control and Data Access', 'Allow Accessibility Access…',
        'Drag %@ to the list above, then turn on its switch to allow Accessibility access.',
        'Keep the three- or four-finger gestures enabled in System Settings > Trackpad > More Gestures.',
    ]
    terms_path = ROOT / 'src/i18n/calmon-app-terms.json'
    terms_path.write_text(json.dumps({language: {term: localized(term, language) for term in terms}
                                     for language in data}, ensure_ascii=False, indent=2) + '\n')

    text = ''.join(section['title'].upper() + ''.join(row['title'] + ''.join(row['keys']) for row in section['rows'])
                   for language in data.values() for section in language)
    shortcuts_path = ROOT / 'src/i18n/calmon-locales.mjs'
    text += subprocess.check_output([
        'node', '--input-type=module', '-e',
        "import {CALMON_LOCALES} from './src/i18n/calmon-locales.mjs'; process.stdout.write(Object.values(CALMON_LOCALES).flatMap(locale => locale.shortcuts.map(([keys]) => keys)).join(''));",
    ], cwd=ROOT, text=True)
    font_path = source / 'Sources/Fonts/ZLabsRoundPix_12px_M_CN.ttf'
    font = TTFont(font_path, recalcTimestamp=False)
    characters = set(map(ord, text)) | set(range(32, 127))
    cmap = font.getBestCmap()
    system_languages = [language for language, sections in data.items()
                        if language in ['ar', 'he', 'hi', 'th'] or any(
                            ord(char) not in cmap for section in sections
                            for char in section['title'].upper() + ''.join(row['title'] for row in section['rows']))]
    system_path = ROOT / 'src/components/calmon-key-panel-system.json'
    system_path.write_text(json.dumps(system_languages, ensure_ascii=False, indent=2) + '\n')
    characters &= cmap.keys()
    options = subset.Options()
    options.flavor = 'woff2'
    options.name_IDs = ['*']
    sub = subset.Subsetter(options=options)
    sub.populate(unicodes=characters)
    sub.subset(font)
    # Subsetting is a modification: use a new family without the original reserved names.
    for name_id, value in {1: 'calmon Panel Web', 2: 'Regular', 3: 'CalmonPanelWeb-Regular',
                           4: 'calmon Panel Web', 6: 'CalmonPanelWeb-Regular', 16: 'calmon Panel Web', 17: 'Regular'}.items():
        for record in font['name'].names:
            if record.nameID == name_id:
                font['name'].setName(value, name_id, record.platformID, record.platEncID, record.langID)
    font.flavor = 'woff2'
    output = ROOT / 'src/assets/fonts/calmon-panel.woff2'
    notices = (source / 'docs/third-party-notices.md').read_text()
    attribution = notices.split('## Z Labs RoundPix 12px\n', 1)[1].split('## Fusion Pixel 12px', 1)[0]
    attribution = attribution[attribution.index('Copyright'):].split('This Font Software', 1)[0].strip()
    license_text = notices[notices.index('SIL OPEN FONT LICENSE Version 1.1'):].split('\n## ', 1)[0].rstrip() + '\n'
    license_notice = 'calmon Panel Web is a renamed WOFF2 subset of Z Labs RoundPix 12px (Build_20260813).\nSource: https://github.com/Astro-2539/ZLabs-RoundPix-12px\n\n' + attribution + '\n\n' + license_text
    (ROOT / 'src/assets/fonts/calmon-panel-OFL.txt').write_text(license_notice)
    for name in font['name'].names:
        if name.nameID == 13:
            font['name'].setName(license_notice, 13, name.platformID, name.platEncID, name.langID)
    font.save(output)
    record = {
        'appSourceCommit': subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip(),
        'method': 'Native key reference and website UI terminology in all 38 app languages, copied from the app catalog. Original RoundPix outlines subset to WOFF2 and renamed calmon Panel Web; no raster panel artwork.',
        'inputs': {str(path.relative_to(source)): digest(path) for path in [catalog_path, font_path]},
        'websiteInputs': {str(path.relative_to(ROOT)): digest(path) for path in [shortcuts_path, ROOT / 'src/i18n/calmon-translations.mjs', *sorted((ROOT / 'src/i18n/calmon').glob('*.json'))]},
        'outputs': {str(path.relative_to(ROOT)): digest(path) for path in [data_path, system_path, output, terms_path]},
    }
    (ROOT / 'scripts/assets/calmon/key-panel-text-source.json').write_text(json.dumps(record, indent=2) + '\n')
    print(f'Key panel: {len(characters)} characters, {output.stat().st_size:,} font bytes, {len(data)} languages.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app-source', type=Path, required=True)
    main(parser.parse_args().app_source)
