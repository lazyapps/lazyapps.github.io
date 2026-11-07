"""Fetch official OFL fonts and build compact, renamed web-only Yilo subsets."""
from pathlib import Path
import hashlib,json,re,urllib.request
from concurrent.futures import ThreadPoolExecutor
from fontTools import subset
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.build/yilo-fonts';CACHE.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'src/assets/fonts/yilo';OUT.mkdir(parents=True,exist_ok=True)
text='Yilo 亦言 Lazyapps Taking it easy since 2009 Mac iPhone iPad Studio Support Privacy Press Kit Homebrew Download '
for p in ['src/i18n/yilo-art-copy.json','src/i18n/yilo-short-copy.json','src/i18n/yilo-hero-copy.json','src/i18n/yilo-locales.mjs','src/i18n/yilo-examples.json','src/i18n/yilo-demo-copy.json','src/content/presskit-glossary.json','src/components/YiloDemo.astro','src/components/YiloFeatureIllustration.astro','src/components/YiloDetailIllustration.astro']:
 text+=(ROOT/p).read_text()
requested=set(map(ord,text))
FONTS=[
('latin','Patrick Hand','https://raw.githubusercontent.com/google/fonts/main/ofl/patrickhand/PatrickHand-Regular.ttf','https://raw.githubusercontent.com/google/fonts/main/ofl/patrickhand/OFL.txt'),
('cyrillic','Neucha','https://raw.githubusercontent.com/google/fonts/main/ofl/neucha/Neucha.ttf','https://raw.githubusercontent.com/google/fonts/main/ofl/neucha/OFL.txt'),
('han','LXGW WenKai','https://github.com/lxgw/LxgwWenKai/releases/download/v1.530/LXGWWenKai-Medium.ttf','https://raw.githubusercontent.com/lxgw/LxgwWenKai/main/OFL.txt'),
('deva','Kalam','https://raw.githubusercontent.com/google/fonts/main/ofl/kalam/Kalam-Regular.ttf','https://raw.githubusercontent.com/google/fonts/main/ofl/kalam/OFL.txt'),
('hangul','Nanum Pen Script','https://raw.githubusercontent.com/google/fonts/main/ofl/nanumpenscript/NanumPenScript-Regular.ttf','https://raw.githubusercontent.com/google/fonts/main/ofl/nanumpenscript/OFL.txt'),
('arabic','Aref Ruqaa','https://raw.githubusercontent.com/google/fonts/main/ofl/arefruqaa/ArefRuqaa-Regular.ttf','https://raw.githubusercontent.com/google/fonts/main/ofl/arefruqaa/OFL.txt')]
sha=lambda b:hashlib.sha256(b).hexdigest()
def download(item):
 key,name,url,license_url=item
 src=CACHE/('patrick.ttf' if key=='latin' else 'neucha.ttf' if key=='cyrillic' else f'{key}.ttf')
 if not src.exists():src.write_bytes(urllib.request.urlopen(url,timeout=60).read())
 license=(OUT/f'{key}-OFL.txt')
 if not license.exists():license.write_bytes(urllib.request.urlopen(license_url,timeout=30).read())
 font=TTFont(src,recalcTimestamp=False)
 coverage=set(font.getBestCmap())
 target=OUT/f'{key}.woff2'
 previous=set(TTFont(target).getBestCmap()) if target.exists() else set()
 chars=(requested|previous)&coverage
 options=subset.Options();options.name_IDs=['*'];options.name_legacy=True;options.name_languages=['*'];options.layout_features=['*']
 sub=subset.Subsetter(options=options);sub.populate(unicodes=chars);sub.subset(font)
 family='Yilo Hand '+key.title()
 for entry in font['name'].names:
  if entry.nameID in [1,4,6,16]:
   value=family.replace(' ','') if entry.nameID==6 else family
   entry.string=value.encode(entry.getEncoding(),errors='replace')
 font.flavor='woff2';target=OUT/f'{key}.woff2';font.save(target)
 print(name,target.stat().st_size,'bytes',flush=True)
 return dict(family=name,cssFamily=family,sourceUrl=url,sourceSHA256=sha(src.read_bytes()),licenseUrl=license_url,
  license=str(license.relative_to(ROOT)),output=str(target.relative_to(ROOT)),sha256=sha(target.read_bytes()),glyphs=len(font.getBestCmap()),
  method='Original outlines retained; subset to Yilo page characters, renamed to avoid reserved font names, WOFF2 for local web delivery only.')
with ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(download,FONTS))
(ROOT/'scripts/assets/yilo/hand-font-sources.json').write_text(json.dumps(dict(checkedOn='2026-11-07',fonts=results),ensure_ascii=False,indent=2)+'\n')

public=ROOT/'public/v/yilo/fonts';public.mkdir(parents=True,exist_ok=True)
notices=[]
for item in results:
 license=ROOT/item['license'];(public/license.name).write_bytes(license.read_bytes())
 notices.append('\n\n'.join([item['family'],item['sourceUrl'],item['licenseUrl'],'Web-only subset; renamed, original outlines retained.',license.read_text()]))
(public/'credits.txt').write_text('\n\n'.join(notices)+'\n')
