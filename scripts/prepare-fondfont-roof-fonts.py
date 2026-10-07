"""Licensed classic typefaces for locale-specific iPhone roof glyphs."""
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
FONTS=ROOT/'scripts/assets/fondfont/animation/v8/fonts'
GLYPHS={
    'en':('EBGaramond[wght].ttf','Ag Qq &'),
    'zh-hans':('SourceHanSerifSC-Regular.otf','永 字 爱'),
    'zh-hant':('SourceHanSerifTC-Regular.otf','永 龍 字'),
    'ja':('SourceHanSerif-Regular.otf','あ ア 永'),
    'ko':('SourceHanSerifK-Regular.otf','한 글 봄'),
    'fr':('EBGaramond[wght].ttf','Ag Œœ é'),
    'de':('LibreBaskerville[wght].ttf','Ag ß Ää'),
}
for code,(file,text) in GLYPHS.items():
    font=TTFont(FONTS/file);assert all(ord(c) in font.getBestCmap() for c in text),code
    options=subset.Options();options.flavor='woff';sub=subset.Subsetter(options=options);sub.populate(text=text);sub.subset(font)
    font.flavor='woff';font.save(ROOT/f'public/v/fondfont/blender-v2/roof-{code}.woff')
print('Seven classic glyph font subsets verified.')
