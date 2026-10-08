"""Licensed font pools for the drifting specimen glyphs on the phone roof.

Each locale has twelve classic glyphs and a pool of open-source typefaces in contrasting
styles (serif, script, rounded, brush, mono...). A typeface joins a pool only if it covers
all twelve glyphs. Each is subset to exactly those glyphs (WOFF). The runtime reads
src/lib/fondfont/roof-fonts.json, and every distributed font's licence is copied
beside the public font licences.
"""
from pathlib import Path
import hashlib, json, shutil
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'scripts/assets/fondfont'
APP = ROOT.parent.parent / 'iOS/iOSFontInstaller/AppStore'
V8, V9, LIC = A / 'animation/v8/fonts', A / 'animation/v9/fonts', A / 'install-capture-20261007/licenses'
FIX = APP / 'Captures/Fixtures'
OUT = ROOT / 'public/v/fondfont/blender-v3/roof'
LICENCES = ROOT / 'public/v/fondfont/fonts/licenses'

# (font file, display name, licence file)
LATIN = [
    (V8 / 'EBGaramond[wght].ttf', 'EB Garamond', LIC / 'EBGaramond[wght]-OFL.txt'),
    (V8 / 'LibreBaskerville[wght].ttf', 'Libre Baskerville', LIC / 'LibreBaskerville[wght]-OFL.txt'),
    (A / 'animation/v4/PlayfairDisplay.ttf', 'Playfair Display', LIC / 'PlayfairDisplay-Variable-OFL.txt'),
    (V9 / 'Allura-Regular.ttf', 'Allura', LIC / 'Allura-Regular-OFL.txt'),
    (V8 / 'DINish-Regular.otf', 'DINish', LIC / 'DINish-Regular-OFL.txt'),
    (APP / 'Screenshots/public/fonts/IBMPlexMono-Regular.ttf', 'IBM Plex Mono', LIC / 'IBMPlexMono-Regular-OFL.txt'),
    (A / 'animation/BebasNeue-Regular.ttf', 'Bebas Neue', LIC / 'BebasNeue-Regular-OFL.txt'),
]
POOLS = {
    'en': ('A Q R a g e k & ? fi ß ft', LATIN),
    'fr': ('A Q a g é ç è à ô œ Œ &', LATIN),
    'de': ('A Q a g ß ä ö ü Ä Ö Ü &', LATIN),
    'zh-hans': ('永 字 爱 书 风 和 美 文 道 光 山 水', [
        (V8 / 'SourceHanSerifSC-Regular.otf', 'Source Han Serif SC', LIC / 'SourceHanSerifSC-Regular-OFL.txt'),
        (V9 / 'MaShanZheng-Regular.ttf', 'Ma Shan Zheng', LIC / 'MaShanZheng-Regular-OFL.txt'),
        (FIX / 'cjk-fonts/zh-Hans/ZCOOLKuaiLe-Regular.ttf', 'ZCOOL KuaiLe', LIC / 'ZCOOLKuaiLe-Regular-OFL.txt'),
        (FIX / 'cjk-fonts/zh-Hans/WDXLLubrifontSC-Regular.ttf', 'WDXL Lubrifont SC', LIC / 'WDXLLubrifontSC-Regular-OFL.txt'),
        (V9 / 'NotoSansSC[wght].ttf', 'Noto Sans SC', V9 / 'notosanssc-OFL.txt'),
        (V9 / 'LXGWWenKaiTC-Regular.ttf', 'LXGW WenKai TC', LIC / 'LXGWWenKaiTC-Regular-OFL.txt'),
    ]),
    'zh-hant': ('永 龍 字 書 體 愛 風 雲 和 美 道 鶴', [
        (V8 / 'SourceHanSerifTC-Regular.otf', 'Source Han Serif TC', LIC / 'SourceHanSerifTC-Regular-OFL.txt'),
        (V9 / 'LXGWWenKaiTC-Regular.ttf', 'LXGW WenKai TC', LIC / 'LXGWWenKaiTC-Regular-OFL.txt'),
        (FIX / 'cjk-fonts/zh-Hant/Huninn-Regular.ttf', 'Huninn', LIC / 'Huninn-Regular-OFL.txt'),
        (FIX / 'cjk-fonts/zh-Hant/Iansui-Regular.ttf', 'Iansui', LIC / 'Iansui-Regular-OFL.txt'),
        (V9 / 'NotoSansTC[wght].ttf', 'Noto Sans TC', V9 / 'notosanstc-OFL.txt'),
    ]),
    'ja': ('あ い ろ は ア カ 永 字 の 書 和 夢', [
        (V8 / 'SourceHanSerif-Regular.otf', 'Source Han Serif', LIC / 'SourceHanSerif-Regular-OFL.txt'),
        (V9 / 'YujiSyuku-Regular.ttf', 'Yuji Syuku', V9 / 'yujisyuku-OFL.txt'),
        (FIX / 'cjk-fonts/ja/KosugiMaru-Regular.ttf', 'Kosugi Maru', LIC / 'KosugiMaru-Regular-Apache-2.0.txt'),
        (FIX / 'cjk-fonts/ja/MPLUSRounded1c-Regular.ttf', 'M PLUS Rounded 1c', LIC / 'MPLUSRounded1c-Regular-license-metadata.pb'),
        (FIX / 'cjk-fonts/ja/ZenMaruGothic-Bold.ttf', 'Zen Maru Gothic', LIC / 'ZenMaruGothic-Bold-OFL.txt'),
        (V9 / 'NotoSansJP[wght].ttf', 'Noto Sans JP', V9 / 'notosansjp-OFL.txt'),
    ]),
    'ko': ('한 글 봄 가 나 다 꽃 빛 사 랑 별 길', [
        (V8 / 'SourceHanSerifK-Regular.otf', 'Source Han Serif K', LIC / 'SourceHanSerifK-Regular-OFL.txt'),
        (V9 / 'NanumPenScript-Regular.ttf', 'Nanum Pen Script', V9 / 'nanumpenscript-OFL.txt'),
        (FIX / 'cjk-fonts/ko/Jua-Regular.ttf', 'Jua', LIC / 'Jua-Regular-OFL.txt'),
        (FIX / 'cjk-fonts/ko/Dongle-Regular.ttf', 'Dongle', LIC / 'Dongle-Regular-OFL.txt'),
        (FIX / 'cjk-fonts/ko/Sunflower-Medium.ttf', 'Sunflower', LIC / 'Sunflower-Medium-OFL.txt'),
        (V9 / 'NotoSansKR[wght].ttf', 'Noto Sans KR', V9 / 'notosanskr-OFL.txt'),
    ]),
}

OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob('*.woff'):
    old.unlink()
manifest = {}
for locale, (text, pool) in POOLS.items():
    glyphs = text.split(' ')
    fonts = []
    for path, name, licence in pool:
        font = TTFont(path)
        cmap = font.getBestCmap()
        if not all(ord(c) in cmap for c in text.replace(' ', '')):
            print(f'{locale}: {name} skipped (missing glyphs)')
            continue
        options = subset.Options()
        options.flavor = 'woff'
        sub = subset.Subsetter(options=options)
        sub.populate(text=text)
        sub.subset(font)
        font.flavor = 'woff'
        file = f'{locale}-{len(fonts)}.woff'
        font.save(OUT / file)
        shutil.copyfile(licence, LICENCES / licence.name)
        fonts.append({'file': file, 'name': name, 'source': path.name, 'license': f'/v/fondfont/fonts/licenses/{licence.name}',
                      'sourceSHA256': hashlib.sha256(path.read_bytes()).hexdigest()})
    assert len(fonts) >= 4, f'{locale} needs a varied font pool'
    manifest[locale] = {'glyphs': glyphs, 'fonts': fonts}
(ROOT / 'src/lib/fondfont/roof-fonts.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + '\n')
for locale, entry in manifest.items():
    print(locale, len(entry['fonts']), 'fonts:', ', '.join(f['name'] for f in entry['fonts']))
