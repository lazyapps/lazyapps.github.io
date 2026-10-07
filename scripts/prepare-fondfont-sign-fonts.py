"""Subset the existing licensed project fonts for the actual localized 3D labels."""
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scripts/assets/fondfont/animation/v9/fonts'
OUT=ROOT/'public/v/fondfont/blender-v2'
LABELS={
    'en':('Inter[opsz,wght].ttf','FONT LIBRARYType FoundryFondFont'),
    'zh-hans':('NotoSansSC[wght].ttf','字体库铸字工厂爱装字体'),
    'zh-hant':('NotoSansTC[wght].ttf','字體庫鑄字工廠愛裝字體'),
    'ja':('NotoSansJP[wght].ttf','フォントライブラリ活字鋳造所フォンドフォント'),
    'ko':('NotoSansKR[wght].ttf','폰트 보관함활자 주조소폰드폰트'),
    'fr':('Inter[opsz,wght].ttf','BIBLIOTHÈQUE DE POLICESFonderie de caractèresFondFont'),
    'de':('Inter[opsz,wght].ttf','SCHRIFTBIBLIOTHEKSchriftgießereiFondFont'),
}
for code,(file,text) in LABELS.items():
    text+=' iOS';font=TTFont(SOURCE/file);options=subset.Options();options.flavor='woff'
    sub=subset.Subsetter(options=options);sub.populate(text=text);sub.subset(font)
    font.flavor='woff';font.save(OUT/f'sign-{code}.woff')
    assert all(c.isspace() or ord(c) in font.getBestCmap() for c in text),code
print('All seven localized label subsets contain every required character.')
