"""Render World Book's shared Open Graph image from its original symbol and site font."""
from io import BytesIO
import json
from pathlib import Path
import subprocess
import tempfile
from xml.etree import ElementTree as ET

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageChops, ImageCms, ImageDraw, ImageFont

SITE = Path(__file__).resolve().parents[1]
ASSETS = SITE / 'src/assets'
SCALE = 3
TITLE = 'WORLD BOOK'
ICON = SITE / 'scripts/assets/world-book/AppIcon.icon'
ICTOOL = '/Applications/Xcode.app/Contents/Applications/Icon Composer.app/Contents/Executables/ictool'


def render_symbol(temporary):
    rendered = Path(temporary) / 'icon.png'
    subprocess.run([
        ICTOOL, str(ICON), '--export-image', '--output-file', str(rendered),
        '--platform', 'iOS', '--rendition', 'Default', '--width', '1024',
        '--height', '1024', '--scale', '1', '--design-generation', '27',
    ], check=True, capture_output=True)
    icon = Image.open(rendered).convert('RGBA')
    if 'icc_profile' in icon.info:
        icon = ImageCms.profileToProfile(icon, ImageCms.ImageCmsProfile(BytesIO(icon.info['icc_profile'])), ImageCms.createProfile('sRGB'), outputMode='RGBA')

    namespace = 'http://www.w3.org/2000/svg'
    ET.register_namespace('', namespace)
    mask_svg = ET.Element(f'{{{namespace}}}svg', width='1024', height='1024', viewBox='0 0 1024 1024')
    document = json.loads((ICON / 'icon.json').read_text())
    # Background stars and light spill are decoration, outside the product symbol.
    for group in document['groups'][:3]:
        for layer in group['layers']:
            if layer['image-name'] in {'Ocean-Sphere.svg', 'Globe-Glow.svg', 'Globe-Land.svg'}:
                continue
            svg = ET.parse(ICON / 'Assets' / layer['image-name']).getroot()
            width, height = float(svg.get('width')), float(svg.get('height'))
            position = layer['position']
            scale = position['scale']
            dx, dy = position['translation-in-points']
            svg.set('x', str((1024 - width * scale) / 2 + dx))
            svg.set('y', str((1024 - height * scale) / 2 + dy))
            svg.set('width', str(width * scale))
            svg.set('height', str(height * scale))
            for element in svg.iter():
                if element.tag.split('}')[-1] in {'path', 'circle', 'g'}:
                    if element.get('fill') != 'none':
                        element.set('fill', 'white')
                    if element.get('stroke') and element.get('stroke') != 'none':
                        element.set('stroke', 'white')
            mask_svg.append(svg)
    mask_png = subprocess.check_output(['rsvg-convert'], input=ET.tostring(mask_svg))
    mask = Image.open(BytesIO(mask_png)).getchannel('A')
    icon.resize((256, 256), Image.Resampling.LANCZOS).save(ASSETS / 'img/world-book-icon.png', optimize=True)
    mask = ImageChops.multiply(mask, icon.getchannel('A'))
    icon.putalpha(mask)
    return icon.crop(mask.getbbox())


def main():
    typeface = TTFont(ASSETS / 'fonts/sofia-sans-xcond-latin.woff2')
    typeface = instantiateVariableFont(typeface, {'wght': 900}, inplace=True)
    typeface.flavor = None
    with tempfile.TemporaryDirectory() as temporary:
        original_symbol = render_symbol(temporary)
        original_symbol.save(ASSETS / 'img/world-book-symbol.png', optimize=True)
        font_path = Path(temporary) / 'sofia-900.ttf'
        typeface.save(font_path)
        for size in range(220, 100, -1):
            font = ImageFont.truetype(str(font_path), size * SCALE)
            bounds = font.getbbox(TITLE)
            height = bounds[3] - bounds[1]
            tracking = -.01 * size * SCALE
            text_width = font.getlength(TITLE) + tracking * (len(TITLE) - 1)
            symbol_width = round(height * original_symbol.width / original_symbol.height)
            gap = 22 * SCALE
            if symbol_width + gap + text_width <= 540 * SCALE:
                break

        canvas = Image.new('RGB', (1200 * SCALE, 630 * SCALE), '#f8f8f6')
        noise = Image.open(ASSETS / 'img/noise.png').convert('L')
        noise = noise.resize((125 * SCALE, 125 * SCALE), Image.Resampling.BICUBIC)
        noise = noise.point(lambda value: round(max(0, min(255, (value - 127.5) * 1.25 + 127.5)) * .6))
        tile = noise.convert('RGBA')
        tile.putalpha(round(255 * .09))
        for y in range(0, canvas.height, tile.height):
            for x in range(0, canvas.width, tile.width):
                canvas.paste(tile, (x, y), tile)

        symbol = original_symbol.resize((symbol_width, height), Image.Resampling.LANCZOS)
        width = symbol_width + gap + text_width
        x = round((canvas.width - width) / 2)
        y = round((canvas.height - height) / 2)
        canvas.paste(symbol, (x, y), symbol)

        draw = ImageDraw.Draw(canvas)
        cursor = x + symbol_width + gap
        for index, character in enumerate(TITLE):
            draw.text((cursor, y - bounds[1]), character, font=font, fill='#171717')
            cursor += font.getlength(character) + tracking
            if index + 1 < len(TITLE):
                following = TITLE[index + 1]
                cursor += font.getlength(character + following) - font.getlength(character) - font.getlength(following)

        result = canvas.resize((1200, 630), Image.Resampling.LANCZOS)
        output = ASSETS / 'img/world-book-opengraph.png'
        result.save(output, optimize=True)
        result.crop((285, 0, 915, 630)).save('/tmp/world-book-opengraph-square.png')
        print(f'{output}: 1200 × 630; centered brand width {width / SCALE:.1f} px')


if __name__ == '__main__':
    main()
