"""Render Yilo's two shared Open Graph assets from current genuine artwork."""
import json
import hashlib
from io import BytesIO
from pathlib import Path
import subprocess
import tempfile

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'src/assets'
SCALE = 3


def background(fill):
    start, stop = fill['orientation']['start'], fill['orientation']['stop']
    stops = []
    for index, value in enumerate(fill['linear-gradient']):
        assert value.startswith('srgb:')
        red, green, blue, alpha = map(float, value.removeprefix('srgb:').split(','))
        color = f'rgb({red * 100}%,{green * 100}%,{blue * 100}%)'
        stops.append(f'<stop offset="{index}" stop-color="{color}" stop-opacity="{alpha}"/>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{1200 * SCALE}" height="{630 * SCALE}" viewBox="0 0 1200 630">
      <defs><linearGradient id="app-background" x1="{start['x'] * 1200}" y1="{start['y'] * 630}" x2="{stop['x'] * 1200}" y2="{stop['y'] * 630}" gradientUnits="userSpaceOnUse">{''.join(stops)}</linearGradient></defs>
      <rect width="1200" height="630" fill="url(#app-background)"/>
    </svg>'''
    return Image.open(BytesIO(subprocess.check_output(['rsvg-convert'], input=svg.encode()))).convert('RGB')


def main():
    icon_source = ROOT / 'scripts/assets/yilo/AppIcon.icon/icon.json'
    icon = json.loads(icon_source.read_text())
    fill = next(item['value'] for item in icon['fill-specializations'] if 'appearance' not in item)
    symbol = Image.open(ASSETS / 'img/yilo-symbol.png').convert('RGBA')
    geometry = json.loads((ROOT / 'scripts/assets/yilo/brand-source.json').read_text())
    body = geometry['bodyBounds']
    visible = geometry['visibleBounds']
    body_height = body[3] - body[1]
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        # Native shaping for the actual Chinese names, never generated lettering.
        config = [dict(file=f'{code}.png', text=name, width=600, height=280, size=180,
            color=[23 / 255] * 3, bold=True, align='left', rtl=False)
            for code, name in [('zh-hans', '亦言')]]
        (temp / 'config.json').write_text(json.dumps(config, ensure_ascii=False))
        subprocess.run(['swiftc', str(ROOT / 'scripts/render-yiyan-text.swift'), '-o', str(temp / 'render-text')], check=True)
        subprocess.run([temp / 'render-text', temp / 'config.json', temp], check=True)
        titles = {}
        for code in ['zh-hans']:
            title = Image.open(temp / f'{code}.png').convert('RGBA')
            titles[code] = title.crop(title.getchannel('A').getbbox())

        face = instantiateVariableFont(TTFont(ASSETS / 'fonts/sofia-sans-xcond-latin.woff2'), {'wght': 900}, inplace=True)
        face.flavor = None
        face.save(temp / 'sofia-900.ttf')
        font = ImageFont.truetype(str(temp / 'sofia-900.ttf'), 220 * SCALE)
        title = Image.new('RGBA', (1600, 900))
        draw = ImageDraw.Draw(title)
        x, tracking = 0, -.01 * 220 * SCALE
        for i, char in enumerate('Yilo'):
            draw.text((x, 0), char, font=font, fill='#171717')
            x += font.getlength(char) + tracking
            if i + 1 < len('Yilo'):
                following = 'Yilo'[i + 1]
                x += font.getlength(char + following) - font.getlength(char) - font.getlength(following)
        titles['shared'] = title.crop(title.getchannel('A').getbbox())

        cards = []
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
            canvas = background(fill)
            x, y = round((canvas.width - total) / 2), round((canvas.height - mark_height) / 2)
            canvas.paste(mark, (x, y), mark)
            title_y = y + round(height * (body[1] - visible[1]) / body_height)
            canvas.paste(title, (x + mark.width + gap, title_y), title)
            suffix = '' if code == 'zh-hans' else '-' + code
            result = canvas.resize((1200, 630), Image.Resampling.LANCZOS)
            output = ASSETS / f'img/yilo-opengraph{suffix}.png'
            result.save(output, optimize=True)
            cards.append(dict(language='zh-Hans' if code == 'zh-hans' else 'shared',
                output=str(output.relative_to(ROOT)), sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                contentBounds=[x / SCALE, y / SCALE, total / SCALE, max(mark_height, title_y - y + title.height) / SCALE]))
            review = ROOT / '.build/yilo-opengraph-review'
            review.mkdir(parents=True, exist_ok=True)
            result.crop((285, 0, 915, 630)).save(review / f'og-square-{code}.png')
            print(f'Updated Yilo OG {code}: centered visible brand width {total / SCALE:.1f}px')
        sources = [icon_source, ROOT / 'scripts/assets/yilo/brand-source.json', ASSETS / 'img/yilo-symbol.png',
            ASSETS / 'fonts/sofia-sans-xcond-latin.woff2', ROOT / 'scripts/render-yiyan-text.swift', Path(__file__)]
        receipt = dict(size=[1200, 630], safeRect=[285, 0, 630, 630], background=fill,
            sources={str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}, cards=cards)
        (ROOT / 'scripts/assets/yilo/opengraph-source.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
