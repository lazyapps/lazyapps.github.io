"""Extract exact localized specimen outlines from pinned original font files."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request

from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v8'
FONTS = ASSETS / 'fonts'
ADOBE = '7889f11bf31170b5d092a083b357c8c8130f89e0'
GOOGLE = '7085eb89a950e85db5b166b7a58d414544b4140c'
DINISH = 'a5f3b2a3b932336225815bf9005e3b72cc3de71c'
RAW = 'https://raw.githubusercontent.com/'
SPECS = {
    'en': ('LibreBaskerville[wght].ttf', f'google/fonts/{GOOGLE}/ofl/librebaskerville/LibreBaskerville[wght].ttf', 'Ag&', 'Libre Baskerville', 400),
    'zh-hans': ('SourceHanSerifSC-Regular.otf', f'adobe-fonts/source-han-serif/{ADOBE}/OTF/SimplifiedChinese/SourceHanSerifSC-Regular.otf', '永字体', '思源宋体', None),
    'zh-hant': ('SourceHanSerifTC-Regular.otf', f'adobe-fonts/source-han-serif/{ADOBE}/OTF/TraditionalChinese/SourceHanSerifTC-Regular.otf', '永字體', '思源宋體', None),
    'ja': ('SourceHanSerif-Regular.otf', f'adobe-fonts/source-han-serif/{ADOBE}/OTF/Japanese/SourceHanSerif-Regular.otf', 'あ永カ', '源ノ明朝', None),
    'ko': ('SourceHanSerifK-Regular.otf', f'adobe-fonts/source-han-serif/{ADOBE}/OTF/Korean/SourceHanSerifK-Regular.otf', '한글봄', '본명조', None),
    'fr': ('EBGaramond[wght].ttf', f'google/fonts/{GOOGLE}/ofl/ebgaramond/EBGaramond[wght].ttf', 'éœç', 'EB Garamond', 400),
    'de': ('DINish-Regular.otf', f'playbeing/dinish/{DINISH}/fonts/otf/DINish/DINish-Regular.otf', 'Äöß', 'DINish', None),
}
LICENSES = {
    'SourceHanSerif-LICENSE.txt': f'adobe-fonts/source-han-serif/{ADOBE}/LICENSE.txt',
    'LibreBaskerville-OFL.txt': f'google/fonts/{GOOGLE}/ofl/librebaskerville/OFL.txt',
    'EBGaramond-OFL.txt': f'google/fonts/{GOOGLE}/ofl/ebgaramond/OFL.txt',
    'DINish-OFL.txt': f'playbeing/dinish/{DINISH}/OFL.txt',
}


def fetch(item):
    name, relative = item
    target = FONTS / name
    url = RAW + urllib.parse.quote(relative, safe='/')
    if not target.exists():
        with urllib.request.urlopen(url, timeout=90) as response:
            target.write_bytes(response.read())
    return {'file': name, 'source': url, 'bytes': target.stat().st_size,
            'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}


def main():
    FONTS.mkdir(parents=True, exist_ok=True)
    downloads = {spec[0]: spec[1] for spec in SPECS.values()} | LICENSES
    with ThreadPoolExecutor(max_workers=5) as pool:
        records = list(pool.map(fetch, downloads.items()))
    data = {}
    verification = {}
    for locale, (filename, _, chars, label, weight) in SPECS.items():
        font = TTFont(FONTS / filename)
        cmap = font.getBestCmap()
        missing = [char for char in chars if ord(char) not in cmap]
        if missing:
            raise ValueError(f'{filename} does not contain {missing}')
        axes = {'wght': weight} if weight else None
        glyph_set = font.getGlyphSet(location=axes)
        scale = 1000 / font['head'].unitsPerEm
        glyphs = []
        bounds = []
        for char in chars:
            name = cmap[ord(char)]
            glyph = glyph_set[name]
            pen = SVGPathPen(glyph_set)
            # Uniform scaling and a y-axis flip preserve the exact contour.
            dx = (1000 - glyph.width * scale) / 2
            glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, dx, 0)))
            path = pen.getCommands()
            bb = BoundsPen(glyph_set)
            glyph.draw(TransformPen(bb, (scale, 0, 0, -scale, dx, 0)))
            bounds.append(bb.bounds)
            glyphs.append({'char': char, 'name': name, 'd': path,
                           'pathSha256': hashlib.sha256(path.encode()).hexdigest()})
        ymin = min(b[1] for b in bounds) - 35
        ymax = max(b[3] for b in bounds) + 35
        viewbox = f'0 {ymin:g} 1000 {ymax-ymin:g}'
        data[locale] = {'filename': filename, 'family': font['name'].getDebugName(1),
                        'label': label, 'viewBox': viewbox, 'glyphs': glyphs}
        verification[locale] = {
            'filename': filename, 'family': font['name'].getDebugName(1),
            'fullName': font['name'].getDebugName(4), 'postScriptName': font['name'].getDebugName(6),
            'version': font['name'].getDebugName(5), 'style': font['name'].getDebugName(2),
            'weightClass': font['OS/2'].usWeightClass, 'variationLocation': axes,
            'sourceSha256': hashlib.sha256((FONTS / filename).read_bytes()).hexdigest(),
            'missingCodepoints': missing, 'viewBox': viewbox,
            'glyphs': [{k: v for k, v in glyph.items() if k != 'd'} for glyph in glyphs],
        }
    target = ROOT / 'src/i18n/fondfont-specimens.json'
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    (ASSETS / 'font-manifest.json').write_text(json.dumps({
        'strategy': 'One real selected font per locale. Hero and background use the identical verified outlines. H3 generates no specimen glyphs.',
        'sources': records, 'locales': verification,
    }, ensure_ascii=False, indent=2) + '\n')
    print(f'Validated {len(data)} locales / {sum(len(v["glyphs"]) for v in data.values())} real glyphs: {target}')


if __name__ == '__main__':
    main()
