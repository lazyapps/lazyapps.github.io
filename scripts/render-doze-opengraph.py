"""Render localized Doze social cards from original transparent artwork and real type."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'src/assets'
SCALE = 3


def background():
    canvas = Image.new('RGB', (1200 * SCALE, 630 * SCALE), '#f8f8f6')
    noise = Image.open(ASSETS / 'img/noise.png').convert('L').resize((125 * SCALE, 125 * SCALE), Image.Resampling.BICUBIC)
    noise = noise.point(lambda v: round(max(0, min(255, (v - 127.5) * 1.25 + 127.5)) * .6))
    tile = noise.convert('RGBA')
    tile.putalpha(round(255 * .09))
    for y in range(0, canvas.height, tile.height):
        for x in range(0, canvas.width, tile.width):
            canvas.paste(tile, (x, y), tile)
    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review-dir', type=Path)
    args = parser.parse_args()
    if args.review_dir:
        args.review_dir.mkdir(parents=True, exist_ok=True)
    locales = json.loads(subprocess.check_output(['node', '--input-type=module', '-e',
        "import {DOZE_LOCALES} from './src/i18n/doze-locales.mjs'; process.stdout.write(JSON.stringify(Object.values(DOZE_LOCALES)))"], cwd=ROOT, text=True))
    symbol = Image.open(ASSETS / 'img/doze-symbol.png').convert('RGBA')
    symbol = symbol.crop(symbol.getchannel('A').getbbox())
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        native = [dict(file=f"{t['htmlLang']}.png", text=t['name'], width=2000, height=500,
            size=240, color=[23 / 255] * 3, bold=True, align='left', rtl=t['htmlDir'] == 'rtl')
            for t in locales if t['htmlLang'] not in ['en', 'es', 'pt-BR', 'fr', 'de']]
        (temp / 'config.json').write_text(json.dumps(native, ensure_ascii=False))
        subprocess.run(['xcrun', 'swift', str(ROOT / 'scripts/render-yiyan-text.swift'), str(temp / 'config.json'), str(temp)], check=True)
        face = instantiateVariableFont(TTFont(ASSETS / 'fonts/sofia-sans-xcond-latin.woff2'), {'wght': 900}, inplace=True)
        face.flavor = None
        face.save(temp / 'sofia-900.ttf')
        font = ImageFont.truetype(str(temp / 'sofia-900.ttf'), 220 * SCALE)
        for t in locales:
            if t['htmlLang'] in ['en', 'es', 'pt-BR', 'fr', 'de']:
                title = Image.new('RGBA', (6000, 1000))
                draw = ImageDraw.Draw(title)
                text, x = t['name'].upper(), 10
                for i, char in enumerate(text):
                    draw.text((x, 0), char, font=font, fill='#171717')
                    x += font.getlength(char) - .01 * 220 * SCALE
                    if i + 1 < len(text):
                        following = text[i + 1]
                        x += font.getlength(char + following) - font.getlength(char) - font.getlength(following)
            else:
                title = Image.open(temp / f"{t['htmlLang']}.png").convert('RGBA')
            title = title.crop(title.getchannel('A').getbbox())
            gap = 20 * SCALE
            height = min(175 * SCALE, round((540 * SCALE - gap) / (symbol.width / symbol.height + title.width / title.height)))
            mark = symbol.resize((round(height * symbol.width / symbol.height), height), Image.Resampling.LANCZOS)
            title = title.resize((round(height * title.width / title.height), height), Image.Resampling.LANCZOS)
            total = mark.width + gap + title.width
            assert total <= 541 * SCALE
            canvas = background()
            x, y = round((canvas.width - total) / 2), round((canvas.height - height) / 2)
            canvas.paste(mark, (x, y), mark)
            canvas.paste(title, (x + mark.width + gap, y), title)
            result = canvas.resize((1200, 630), Image.Resampling.LANCZOS)
            result.save(ASSETS / 'img' / t['ogAsset'], optimize=True)
            if args.review_dir:
                result.crop((285, 0, 915, 630)).save(args.review_dir / f"og-square-{t['code'] or 'zh-hans'}.png")
            print(t['htmlLang'], t['name'], 'safe width', round(total / SCALE))


if __name__ == '__main__':
    main()
