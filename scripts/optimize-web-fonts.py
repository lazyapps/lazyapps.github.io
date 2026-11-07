"""Manually subset current web fonts without changing their CSS matching behavior.

Requires fontTools[woff] and an existing site build. Run after content/CSS/font
changes, then rebuild and compare the rendered output. Source fonts stay intact.
"""
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'scripts/assets/fonts/web-font-plan.json'
OUT = ROOT / 'src/assets/fonts/optimized'
MANIFEST = ROOT / 'scripts/assets/fonts/web-fonts.json'
COMMON = set(range(0x250)) | set(range(0x300, 0x370)) | set(range(0x1E00, 0x1F00)) | set(range(0x2000, 0x2070)) | {0x20AC}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ranges(points):
    runs = []
    for point in sorted(points):
        if runs and point == runs[-1][1] + 1:
            runs[-1][1] = point
        else:
            runs.append([point, point])
    return ','.join(f'U+{a:04X}' + (f'-{b:04X}' if a != b else '') for a, b in runs)


def declared_points(value, cmap):
    if not value:
        return set(cmap)
    points = set()
    for item in value.split(','):
        match = re.fullmatch(r'U\+([0-9A-Fa-f]+)(?:-([0-9A-Fa-f]+))?', item.strip())
        start, end = int(match[1], 16), int(match[2] or match[1], 16)
        points.update(point for point in cmap if start <= point <= end)
    return points


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.characters = set()

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'template', 'noscript'):
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'template', 'noscript'):
            self.hidden -= 1

    def handle_data(self, text):
        if not self.hidden:
            self.characters.update(map(ord, text))


def rename(font, family, variant):
    derivative = f'Lazyapps Web {family} {variant}'
    postscript = re.sub('[^A-Za-z0-9-]', '', derivative)
    for name in font['name'].names:
        if name.nameID in (1, 4, 16, 21):
            name.string = derivative.encode(name.getEncoding(), errors='replace')
        elif name.nameID in (3, 6, 25):
            name.string = postscript.encode(name.getEncoding(), errors='replace')
    if 'fvar' in font:
        for instance in font['fvar'].instances:
            identifier = instance.postscriptNameID
            if identifier == 0xFFFF:
                continue
            style = font['name'].getDebugName(instance.subfamilyNameID) or 'Regular'
            for name in font['name'].names:
                if name.nameID == identifier:
                    name.string = f'{postscript}-{style}'.replace(' ', '').encode(name.getEncoding(), errors='replace')


def inspect(path):
    font = TTFont(path)
    return dict(bytes=path.stat().st_size, glyphs=len(font.getGlyphOrder()),
        characters=len(font.getBestCmap()), unicodeRange=ranges(font.getBestCmap()),
        axes={a.axisTag: [a.minValue, a.defaultValue, a.maxValue] for a in font['fvar'].axes} if 'fvar' in font else {},
        features={table: sorted({record.FeatureTag for record in font[table].table.FeatureList.FeatureRecord})
                  for table in ('GSUB', 'GPOS') if table in font and font[table].table.FeatureList},
        hinting=[table for table in ('fpgm', 'prep', 'cvt ', 'gasp') if table in font],
        hintTables={table: hashlib.sha256(font.getTableData(table)).hexdigest() for table in ('fpgm', 'prep', 'cvt ', 'gasp') if table in font},
        metrics=dict(unitsPerEm=font['head'].unitsPerEm, ascent=font['hhea'].ascent,
                     descent=font['hhea'].descent, lineGap=font['hhea'].lineGap,
                     typoAscent=font['OS/2'].sTypoAscender, typoDescent=font['OS/2'].sTypoDescender,
                     typoLineGap=font['OS/2'].sTypoLineGap),
        familyNames=sorted({record.toUnicode() for record in font['name'].names if record.nameID in (1, 4, 6, 16, 21, 25)}),
        sha256=digest(path))


def verify_outlines(source, target):
    original, output = TTFont(source), TTFont(target)
    before, after = original.getGlyphSet(), output.getGlyphSet()
    cmap = original.getBestCmap()
    hints = 0
    for point, glyph in output.getBestCmap().items():
        left, right = DecomposingRecordingPen(before), DecomposingRecordingPen(after)
        before[cmap[point]].draw(left)
        after[glyph].draw(right)
        assert left.value == right.value, f'{target.name}: outline changed for U+{point:04X}'
        assert original['hmtx'][cmap[point]] == output['hmtx'][glyph], f'{target.name}: glyph metrics changed'
        source_glyph, target_glyph = original['glyf'][cmap[point]], output['glyf'][glyph]
        if hasattr(source_glyph, 'program'):
            assert source_glyph.program.getBytecode() == target_glyph.program.getBytecode(), f'{target.name}: glyph hints changed'
            hints += 1
    for table in ('fpgm', 'prep', 'cvt ', 'gasp'):
        if table in original:
            assert original.getTableData(table) == output.getTableData(table), f'{target.name}: {table} changed'
    return dict(outlines=len(output.getBestCmap()), glyphHints=hints, globalHintTablesUnchanged=True)


def render_face(face, path, points):
    base = ROOT / ('src/components/calmon-desktop' if face['group'] == 'pixel' else 'src/assets/s')
    relative = Path(os.path.relpath(path, base))
    # This string is inserted into the existing asset stylesheet directory.
    return (f'@font-face{{font-family:"{face["family"]}";font-style:{face["style"]};'
            f'font-weight:{face["weight"]};font-display:{face["display"]};'
            f'src:url("{relative}?no-inline") format("woff2");unicode-range:{ranges(points)}}}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate-only', action='store_true', help='Inspect outputs before switching CSS')
    args = parser.parse_args()
    faces = json.loads(PLAN.read_text())['faces']
    reader = VisibleText()
    tags = json.loads((ROOT / 'src/content/presskit-supported-languages.json').read_text())['yilo']['tags']
    for tag in tags:
        if not tag.startswith(('zh', 'ja')):
            reader.feed((ROOT / f'dist/yilo/{tag.lower()}/index.html').read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    for path in OUT.glob('*.woff2'):
        path.unlink()

    # The last matching @font-face owned an overlapping code point before this
    # change. Preserve that ownership while making the new ranges disjoint.
    later = defaultdict(set)
    for face in reversed(faces):
        cmap = TTFont(ROOT / face['source']).getBestCmap()
        points = declared_points(face['unicodeRange'], cmap)
        key = (face['family'], face['style'], face['weight'])
        face['points'] = points - later[key]
        later[key].update(points)

    sheets = defaultdict(list)
    records = []
    for face in faces:
        source = ROOT / face['source']
        original = inspect(source)
        points = face['points']
        record = {key: value for key, value in face.items() if key != 'points'}
        record.update(sourceSHA256=digest(source), original=original, effectiveUnicodeRange=ranges(points), outputs=[])
        if face['retain']:
            sheets[face['group']].append(render_face(face, source, points))
            record['outputs'].append(dict(file=face['source'], kind='retained', **original))
            records.append(record)
            continue
        core = points & COMMON if len(points & set(range(0x20, 0x7F))) >= 26 else set()
        if face['id'] == 'yilo-han':
            core |= points & (reader.characters | set(range(0x3000, 0x3100)) | set(range(0xFF00, 0xFFF0)))
        chunks = [('core', core), ('extended', points - core)]
        if face['id'] == 'yilo-han':
            chunks.append(('merged', points))
        cmap_union = set()
        for kind, characters in chunks:
            if not characters:
                continue
            font = TTFont(source, recalcTimestamp=False)
            options = subset.Options()
            options.name_IDs = ['*']
            options.name_legacy = True
            options.name_languages = ['*']
            options.layout_features = ['*']
            options.hinting = True
            options.notdef_outline = True
            options.no_subset_tables += ['meta']
            sub = subset.Subsetter(options=options)
            sub.populate(unicodes=characters)
            sub.subset(font)
            rename(font, face['family'], kind)
            font.flavor = 'woff2'
            target = OUT / f'{face["id"]}-{kind}.woff2'
            font.save(target)
            actual = set(TTFont(target).getBestCmap())
            assert actual == characters, f'{face["id"]}/{kind}: changed character coverage'
            if kind != 'merged':
                assert not cmap_union & actual, 'Core and extended subsets must not overlap'
                cmap_union |= actual
            result = inspect(target)
            result['verification'] = verify_outlines(source, target)
            item = dict(file=str(target.relative_to(ROOT)), kind=kind, **result)
            if kind == 'merged':
                record['merged'] = item
            else:
                record['outputs'].append(item)
                sheets[face['group']].append(render_face(face, target, actual))
        assert cmap_union == points, f'{face["id"]}: lost supported characters'
        records.append(record)
        print(face['id'], original['bytes'], '->', sum(item['bytes'] for item in record['outputs']),
              [(item['kind'], item['bytes']) for item in record['outputs']], flush=True)

    report = dict(command='python3 scripts/optimize-web-fonts.py',
        policy='Original sources, variable ranges, whole monospace face and fallback stacks retained. Exact effective cmap ownership; shaping closure and hinting retained. Supported Latin-1/Extended-A/combining marks stay with Latin cores. Common non-CJK-page Han/Kana core; merged CJK face preserves contextual punctuation. Script-only faces have no ASCII core. No core embedding or idle precaching.',
        sources={str(PLAN.relative_to(ROOT)): digest(PLAN), str(Path(__file__).relative_to(ROOT)): digest(Path(__file__))}, fonts=records)
    MANIFEST.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    if args.generate_only:
        return
    replacements = [('src/assets/s/site.css', ':root {', 'site'),
                    ('src/assets/s/fondfont-fonts.css', 'body {', 'fondfont')]
    for name, marker, group in replacements:
        path = ROOT / name
        _, separator, remainder = path.read_text().partition(marker)
        assert separator, name
        path.write_text('/* Generated by scripts/optimize-web-fonts.py; sources and licenses retained. */\n' + '\n'.join(sheets[group]) + '\n\n' + separator + remainder)
    hand = ROOT / 'src/assets/s/yilo-hand.css'
    base = ROOT / 'src/assets/s/yilo-hand-base.css'
    if not base.exists():
        _, separator, remainder = hand.read_text().partition(':root[data-yilo]')
        assert separator
        base.write_text(separator + remainder)
    prefix = '/* Generated by scripts/optimize-web-fonts.py. */\n@import "./yilo-hand-base.css";\n'
    hand.write_text(prefix + '\n'.join(sheets['yilo']) + '\n')
    merged_rules = []
    for face, record in zip(faces, records):
        if face['group'] != 'yilo':
            continue
        for item in [record['merged']] if 'merged' in record else record['outputs']:
            path = ROOT / item['file']
            merged_rules.append(render_face(face, path, TTFont(path).getBestCmap()))
    (ROOT / 'src/assets/s/yilo-hand-cjk.css').write_text(prefix + '\n'.join(merged_rules) + '\n')
    pixel = ROOT / 'src/components/calmon-desktop/desktop.css'
    pixel.write_text(re.sub(r'@font-face\{font-family:(?:"calmon Pixel"|calmon Pixel);[^}]+\}', '\n'.join(sheets['pixel']), pixel.read_text(), count=1))


if __name__ == '__main__':
    main()
