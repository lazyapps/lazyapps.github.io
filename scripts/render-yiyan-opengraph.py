"""Render YiYan's three localized Open Graph assets from current genuine artwork."""
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
    symbol = Image.open(ASSETS / 'img/yiyan-symbol.png').convert('RGBA')
    geometry = json.loads((ROOT / 'scripts/assets/yiyan/brand-source.json').read_text())
    body = geometry['bodyBounds']
    visible = geometry['visibleBounds']
    body_height = body[3] - body[1]
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        # Native shaping for the actual Chinese names, never generated lettering.
        config = [dict(file=f'{code}.png', text=name, width=600, height=280, size=180,
            color=[23 / 255] * 3, bold=True, align='left', rtl=False)
            for code, name in [('zh-hans', '绎言'), ('zh-hant', '繹言')]]
        (temp / 'config.json').write_text(json.dumps(config, ensure_ascii=False))
        subprocess.run([ROOT / 'scripts/assets/yiyan/marketing-v2/render-text', temp / 'config.json', temp], check=True)
        titles = {}
        for code in ['zh-hans', 'zh-hant']:
            title = Image.open(temp / f'{code}.png').convert('RGBA')
            titles[code] = title.crop(title.getchannel('A').getbbox())

        face = instantiateVariableFont(TTFont(ASSETS / 'fonts/sofia-sans-xcond-latin.woff2'), {'wght': 900}, inplace=True)
        face.flavor = None
        face.save(temp / 'sofia-900.ttf')
        font = ImageFont.truetype(str(temp / 'sofia-900.ttf'), 220 * SCALE)
        title = Image.new('RGBA', (1600, 900))
        draw = ImageDraw.Draw(title)
        x, tracking = 0, -.01 * 220 * SCALE
        for i, char in enumerate('YIYAN'):
            draw.text((x, 0), char, font=font, fill='#171717')
            x += font.getlength(char) + tracking
            if i + 1 < len('YIYAN'):
                following = 'YIYAN'[i + 1]
                x += font.getlength(char + following) - font.getlength(char) - font.getlength(following)
        titles['shared'] = title.crop(title.getchannel('A').getbbox())

        for code, title in titles.items():
            # Native visible boundaries, equal visual heights, central square safe.
            symbol_ratio = symbol.width / body_height
            title_ratio = title.width / title.height
            gap = 22 * SCALE
            height = min(190 * SCALE, round((540 * SCALE - gap) / (symbol_ratio + title_ratio)))
            mark_height = round(height * symbol.height / body_height)
            mark = symbol.resize((round(height * symbol_ratio), mark_height), Image.Resampling.LANCZOS)
            title = title.resize((round(height * title_ratio), height), Image.Resampling.LANCZOS)
            total = mark.width + gap + title.width
            canvas = background()
            x, y = round((canvas.width - total) / 2), round((canvas.height - mark_height) / 2)
            canvas.paste(mark, (x, y), mark)
            title_y = y + round(height * (body[1] - visible[1]) / body_height)
            canvas.paste(title, (x + mark.width + gap, title_y), title)
            suffix = '' if code == 'zh-hans' else '-' + code
            result = canvas.resize((1200, 630), Image.Resampling.LANCZOS)
            result.save(ASSETS / f'img/yiyan-opengraph{suffix}.png', optimize=True)
            result.crop((285, 0, 915, 630)).save(ROOT / f'docs/reviews/yiyan-story-20261008/og-square-{code}.png')
            print(f'Updated YiYan OG {code}: centered visible brand width {total / SCALE:.1f}px')


if __name__ == '__main__':
    main()
