#!/usr/bin/env python3
"""Manually regenerate web fonts from the current exported native key-panel data.

Requires scripts/requirements-web-fonts.txt. Export changed native panel content
with prepare-calmon-assets.py first; this script never rewrites panel copy.
"""
import argparse
import importlib
import json
import subprocess
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont

optimizer = importlib.import_module('optimize-web-fonts')
ROOT = Path(__file__).resolve().parents[1]
SYSTEM_LANGUAGES = {'ar', 'he', 'hi', 'th'}


def main(source):
    data_path = ROOT / 'src/components/calmon-key-panel.json'
    data = json.loads(data_path.read_text())
    font_path = source / 'Sources/Fonts/ZLabsRoundPix_12px_M_CN.ttf'
    cmap = TTFont(font_path).getBestCmap()
    labels = {language: ''.join(section['title'].upper() + ''.join(row['title'] for row in section['rows'])
                               for section in sections) for language, sections in data.items()}
    system_languages = sorted(language for language, text in labels.items()
                              if language in SYSTEM_LANGUAGES or not set(map(ord, text)) <= cmap.keys())
    system_path = ROOT / 'src/components/calmon-key-panel-system.json'
    system_path.write_text(json.dumps(system_languages, ensure_ascii=False, indent=2) + '\n')
    shortcuts = subprocess.check_output([
        'node', '--input-type=module', '-e',
        "import {CALMON_LOCALES} from './src/i18n/calmon-locales.mjs'; process.stdout.write(Object.values(CALMON_LOCALES).flatMap(locale => locale.shortcuts.map(([keys]) => keys.toUpperCase())).join(''));",
    ], cwd=ROOT, text=True)
    key_text = shortcuts + ''.join(''.join(row['keys']) for sections in data.values()
                                  for section in sections for row in section['rows'])
    pixel_text = ''.join(text for language, text in labels.items() if language not in system_languages)
    # Retain supported Latin-1/Extended-A even when current copy does not use it.
    # Keycap symbols and punctuation belong to the preloaded core in every locale.
    common = set(range(0x20, 0x7F)) | set(range(0x2000, 0x2070)) | {0xA0, 0xB7} | set(map(ord, key_text))
    characters = (common | set(range(0xA0, 0x180)) | set(map(ord, pixel_text))) & cmap.keys()
    latin = (characters - common) & set(range(0xA0, 0x180))
    cyrillic = (characters - common) & set(range(0x400, 0x530))
    chunks = [('core', characters & common), ('latin', latin), ('cyrillic', cyrillic),
              ('extended', characters - common - latin - cyrillic)]
    notices = (source / 'docs/third-party-notices.md').read_text()
    attribution = notices.split('## Z Labs RoundPix 12px\n', 1)[1].split('## Fusion Pixel 12px', 1)[0]
    attribution = attribution[attribution.index('Copyright'):].split('This Font Software', 1)[0].strip()
    license_text = notices[notices.index('SIL OPEN FONT LICENSE Version 1.1'):].split('\n## ', 1)[0].rstrip() + '\n'
    license_notice = 'calmon Panel Web is a renamed WOFF2 subset of Z Labs RoundPix 12px (Build_20260813).\nSource: https://github.com/Astro-2539/ZLabs-RoundPix-12px\n\n' + attribution + '\n\n' + license_text
    license_path = ROOT / 'src/assets/fonts/calmon-panel-OFL.txt'
    license_path.write_text(license_notice)
    outputs, rules, union = [], [], set()
    for kind, points in chunks:
        font = TTFont(font_path, recalcTimestamp=False)
        options = subset.Options()
        options.flavor = 'woff2'
        options.name_IDs = ['*']
        options.hinting = True
        options.layout_features = ['*']
        sub = subset.Subsetter(options=options)
        sub.populate(unicodes=points)
        sub.subset(font)
        for record in font['name'].names:
            names = {1: 'calmon Panel Web', 2: 'Regular', 3: 'CalmonPanelWeb-Regular',
                     4: 'calmon Panel Web', 6: 'CalmonPanelWeb-Regular', 16: 'calmon Panel Web',
                     17: 'Regular', 13: license_notice}
            if record.nameID in names:
                record.string = names[record.nameID].encode(record.getEncoding())
        font.flavor = 'woff2'
        output = ROOT / f'src/assets/fonts/calmon-panel-{kind}.woff2'
        font.save(output)
        actual = set(TTFont(output).getBestCmap())
        assert actual == points and not union & actual, f'{kind}: unexpected or overlapping cmap'
        union |= actual
        record = dict(file=str(output.relative_to(ROOT)), kind=kind, **optimizer.inspect(output),
                      verification=optimizer.verify_outlines(font_path, output))
        outputs.append(record)
        rules.append('@font-face{font-family:"calmon Panel";'
                     f'src:url("../fonts/{output.name}?no-inline") format("woff2");'
                     f'font-style:normal;font-weight:400;font-display:swap;unicode-range:{record["unicodeRange"]}}}')
    assert union == characters
    css_path = ROOT / 'src/assets/s/calmon-panel-fonts.css'
    css_path.write_text('/* Generated manually by scripts/prepare-calmon-key-panel.py. */\n' + '\n'.join(rules) + '\n')
    record = {
        'appSourceCommit': subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip(),
        'method': 'Current exported native panel labels and rendered shortcut keycaps; supported Latin-1/Extended-A and common punctuation retained. Disjoint core/extended WOFF2 subsets preserve outlines, advances, hinting, system-language fallbacks, and font-display.',
        'inputs': {str(font_path.relative_to(source)): optimizer.digest(font_path)},
        'source': optimizer.inspect(font_path),
        'websiteInputs': {str(path.relative_to(ROOT)): optimizer.digest(path) for path in
                          [data_path, ROOT / 'src/i18n/calmon-locales.mjs', ROOT / 'src/i18n/calmon-translations.mjs',
                           *sorted((ROOT / 'src/i18n/calmon').glob('*.json'))]},
        'outputs': {str(path.relative_to(ROOT)): optimizer.digest(path) for path in
                    [system_path, css_path, license_path, *(ROOT / item['file'] for item in outputs)]},
        'fonts': outputs,
    }
    (ROOT / 'scripts/assets/calmon/key-panel-text-source.json').write_text(json.dumps(record, indent=2) + '\n')
    print(f'Key panel: {len(characters)} supported characters, {len(data)} languages; ' +
          ', '.join(f"{item['kind']} {item['bytes']:,} bytes" for item in outputs) + '.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app-source', type=Path, required=True)
    main(parser.parse_args().app_source.resolve())
