"""Shape poetic specimens from the verified real font files (uharfbuzz 0.51.0)."""
import hashlib
import json
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'scripts/assets/fondfont/animation/v10'
POEMS = {
 'zh-hans': ('明月松间照', '王维 · 山居秋暝', 'https://zh.wikisource.org/wiki/山居秋暝'),
 'zh-hant': ('明月松間照', '王維 · 山居秋暝', 'https://zh.wikisource.org/wiki/山居秋暝'),
 'ja': ('春の海', '与謝蕪村', 'https://www.city.osaka.lg.jp/miyakojima/page/0000083259.html'),
 'ko': ('진달래꽃', '김소월 · 진달래꽃', 'https://gongu.copyright.or.kr/gongu/wrt/wrt/view.do?menuNo=200019&wrtSn=9000320'),
 'en': ('Season of mists', 'John Keats · To Autumn', 'https://en.wikisource.org/wiki/The_Poetical_Works_of_John_Keats/To_Autumn'),
 'fr': ('Demain, dès l’aube', 'Victor Hugo · Les Contemplations', 'https://fr.wikisource.org/wiki/Les_Contemplations'),
 'de': ('Über allen Gipfeln', 'J. W. Goethe · Ein Gleiches', 'https://goethe-lyrik.de/wissen/90317/'),
}

def main():
 manifest = json.loads((ROOT/'scripts/assets/fondfont/animation/v9/font-manifest.json').read_text())
 collections, proofs = {}, {}
 for locale, records in manifest['locales'].items():
  phrase, attribution, url = POEMS[locale]
  collections[locale], proofs[locale] = [], []
  for record in records:
   path = ROOT / record['path']
   font = TTFont(path)
   missing = [c for c in phrase if ord(c) not in font.getBestCmap()]
   if missing: raise ValueError(f'{path}: missing {missing}')
   axes = record['variation'] or {}
   glyphset = font.getGlyphSet(location=axes)
   units = font['head'].unitsPerEm
   face = hb.Face(hb.Blob.from_file_path(str(path)))
   shaped_font = hb.Font(face)
   shaped_font.scale = (units, units)
   shaped_font.set_variations(axes)
   buf = hb.Buffer()
   buf.add_str(phrase)
   buf.guess_segment_properties()
   buf.language = {'zh-hans':'zh-cn', 'zh-hant':'zh-tw'}.get(locale, locale)
   hb.shape(shaped_font, buf, {'kern':True, 'liga':True})
   pen, bounds = SVGPathPen(glyphset), BoundsPen(glyphset)
   x, y, shaped = 0, 0, []
   scale = 1000 / units
   for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
    if info.codepoint == 0: raise ValueError(f'{path}: .notdef in shaped phrase')
    name = font.getGlyphName(info.codepoint)
    transform = (scale, 0, 0, -scale, (x+pos.x_offset)*scale, -(y+pos.y_offset)*scale)
    glyphset[name].draw(TransformPen(pen, transform))
    glyphset[name].draw(TransformPen(bounds, transform))
    shaped.append({'gid':info.codepoint, 'glyph':name, 'cluster':info.cluster, 'advance':pos.x_advance, 'offset':[pos.x_offset,pos.y_offset]})
    x += pos.x_advance
    y += pos.y_advance
   xmin, ymin, xmax, ymax = bounds.bounds
   clearance = 45
   viewbox = f'{xmin-clearance:g} {ymin-clearance:g} {xmax-xmin+2*clearance:g} {ymax-ymin+2*clearance:g}'
   d = pen.getCommands()
   result = {k:record[k] for k in ['filename','label','family','style','category','variation']}
   result.update(phrase=phrase, attribution=attribution, source=url, viewBox=viewbox, d=d)
   collections[locale].append(result)
   proofs[locale].append({'font':record['path'], 'fontSha256':record['sourceSha256'], 'phrase':phrase, 'source':url, 'attribution':attribution, 'axes':axes, 'language':buf.language, 'missingCodepoints':missing, 'shaped':shaped, 'viewBox':viewbox, 'pathSha256':hashlib.sha256(d.encode()).hexdigest()})
 (ROOT/'src/i18n/fondfont-poems.json').write_text(json.dumps(collections,ensure_ascii=False,indent=2)+'\n')
 (OUT/'poem-manifest.json').write_text(json.dumps({'shaper':'HarfBuzz via uharfbuzz 0.51.0', 'features':{'kern':True,'liga':True}, 'spellingNote':'German Ueber is normalized to Über; Korean uses the original poem title.', 'locales':proofs},ensure_ascii=False,indent=2)+'\n')
 print('21 real font instances; seven poetic specimens; no missing glyphs or .notdef')

if __name__ == '__main__': main()
