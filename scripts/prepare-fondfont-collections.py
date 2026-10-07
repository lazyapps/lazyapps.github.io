"""Verify three distinct real typefaces per locale; extract identical usable specimens."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import urllib.parse
import urllib.request
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v9'
FONTS = ASSETS / 'fonts'
GOOGLE = '7085eb89a950e85db5b166b7a58d414544b4140c'
base_spec = importlib.util.spec_from_file_location('original_specimens', ROOT / 'scripts/prepare-fondfont-specimens.py')
base = importlib.util.module_from_spec(base_spec)
base_spec.loader.exec_module(base)
EXTRAS = {
 'zh-hans': [('notosanssc','NotoSansSC[wght].ttf','Noto Sans SC','sans'), ('mashanzheng','MaShanZheng-Regular.ttf','马善政毛笔楷体','handwriting')],
 'zh-hant': [('notosanstc','NotoSansTC[wght].ttf','Noto Sans TC','sans'), ('lxgwwenkaitc','LXGWWenKaiTC-Regular.ttf','霞鶩文楷 TC','handwriting')],
 'ja': [('notosansjp','NotoSansJP[wght].ttf','Noto Sans JP','sans'), ('yujisyuku','YujiSyuku-Regular.ttf','佑字 肅','handwriting')],
 'ko': [('notosanskr','NotoSansKR[wght].ttf','Noto Sans KR','sans'), ('nanumpenscript','NanumPenScript-Regular.ttf','나눔손글씨 펜','handwriting')],
 'en': [('inter','Inter[opsz,wght].ttf','Inter','sans'), ('allura','Allura-Regular.ttf','Allura','handwriting')],
 'fr': [('inter','Inter[opsz,wght].ttf','Inter','sans'), ('allura','Allura-Regular.ttf','Allura','handwriting')],
 'de': [('ebgaramond','EBGaramond[wght].ttf','EB Garamond','serif'), ('allura','Allura-Regular.ttf','Allura','handwriting')],
}


def download(item):
 family, filename = item
 target = FONTS / filename
 relative = f'google/fonts/{GOOGLE}/ofl/{family}/{filename}'
 url = 'https://raw.githubusercontent.com/' + urllib.parse.quote(relative, safe='/')
 if not target.exists():
  with urllib.request.urlopen(url, timeout=90) as response:
   target.write_bytes(response.read())
 return {'path':str(target.relative_to(ROOT)), 'url':url, 'sha256':hashlib.sha256(target.read_bytes()).hexdigest(), 'bytes':target.stat().st_size}


def specimen(path, chars, label, category):
 font = TTFont(path)
 cmap = font.getBestCmap()
 missing = [c for c in chars if ord(c) not in cmap]
 if missing: raise ValueError(f'{path.name}: missing {missing}')
 axes = {axis.axisTag:(400 if axis.axisTag=='wght' else 14 if axis.axisTag=='opsz' else axis.defaultValue) for axis in font['fvar'].axes} if 'fvar' in font else None
 glyphset = font.getGlyphSet(location=axes)
 scale = 1000 / font['head'].unitsPerEm
 glyphs, bounds = [], []
 for c in chars:
  name = cmap[ord(c)]; glyph = glyphset[name]
  transform = (scale,0,0,-scale,(1000-glyph.width*scale)/2,0)
  pen = SVGPathPen(glyphset); glyph.draw(TransformPen(pen,transform)); d=pen.getCommands()
  bb=BoundsPen(glyphset); glyph.draw(TransformPen(bb,transform)); bounds.append(bb.bounds)
  glyphs.append({'char':c,'name':name,'d':d,'pathSha256':hashlib.sha256(d.encode()).hexdigest()})
 ymin=min(b[1] for b in bounds)-35; ymax=max(b[3] for b in bounds)+35
 record={'filename':path.name,'label':label,'family':font['name'].getDebugName(1),'style':font['name'].getDebugName(2),'version':font['name'].getDebugName(5),'category':category,'variation':axes,'viewBox':f'0 {ymin:g} 1000 {ymax-ymin:g}','glyphs':glyphs}
 proof={k:v for k,v in record.items() if k!='glyphs'} | {'path':str(path.relative_to(ROOT)),'sourceSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'missingCodepoints':missing,'glyphs':[{k:v for k,v in g.items() if k!='d'} for g in glyphs]}
 return record,proof


def main():
 FONTS.mkdir(parents=True,exist_ok=True)
 items={(f,n) for choices in EXTRAS.values() for f,n,_,_ in choices}
 # Reuse existing pinned EB Garamond without storing a duplicate.
 items.discard(('ebgaramond','EBGaramond[wght].ttf'))
 downloads=list(items)
 def task(item):
  f,n=item
  if n.endswith('-OFL.txt'):
   target=FONTS/n
   url=f'https://raw.githubusercontent.com/google/fonts/{GOOGLE}/ofl/{f}/OFL.txt'
   if not target.exists(): target.write_bytes(urllib.request.urlopen(url,timeout=90).read())
   return {'path':str(target.relative_to(ROOT)),'url':url,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size}
  return download(item)
 downloads += [(f,f'{f}-OFL.txt') for f in sorted({f for f,_ in items})]
 with ThreadPoolExecutor(max_workers=5) as pool: sources=list(pool.map(task,downloads))
 collection,proofs={},{}
 for locale, (filename,_,chars,label,_) in base.SPECS.items():
  oldpath=base.FONTS/filename
  records=[]; verified=[]
  record,proof=specimen(oldpath,chars,label,'sans' if locale=='de' else 'serif')
  records.append(record); verified.append(proof)
  for f,n,l,cat in EXTRAS[locale]:
   path=base.FONTS/n if n=='EBGaramond[wght].ttf' else FONTS/n
   record,proof=specimen(path,chars,l,cat); records.append(record); verified.append(proof)
  collection[locale]=records; proofs[locale]=verified
 target=ROOT/'src/i18n/fondfont-collections.json'
 target.write_text(json.dumps(collection,ensure_ascii=False,indent=2)+'\n')
 (ASSETS/'font-manifest.json').write_text(json.dumps({'strategy':'Three real families per locale using identical representative characters. One chosen font retains exact identity from imported file to system library and both documents. No generated or synthetic glyphs.','sources':sources,'locales':proofs},ensure_ascii=False,indent=2)+'\n')
 print(f'{len(collection)} locales, {sum(len(r) for r in collection.values())} real families, {sum(len(f["glyphs"]) for r in collection.values() for f in r)} verified paths')


if __name__=='__main__': main()
