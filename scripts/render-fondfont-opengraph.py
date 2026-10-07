"""Render exact FondFont icon/symbol and localized Open Graph assets."""
from io import BytesIO
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from xml.etree import ElementTree as ET
from PIL import Image, ImageCms, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

SITE = Path(__file__).resolve().parents[1]
ASSETS = SITE / 'src/assets'
ICON = SITE / 'scripts/assets/fondfont/AppIcon.icon'
ICTOOL = '/Applications/Xcode.app/Contents/Applications/Icon Composer.app/Contents/Executables/ictool'
SCALE = 3


def symbol(temporary):
    rendered = Path(temporary) / 'icon.png'
    subprocess.run([ICTOOL, str(ICON), '--export-image', '--output-file', str(rendered), '--platform', 'iOS', '--rendition', 'Default', '--width', '1024', '--height', '1024', '--scale', '1', '--design-generation', '27'], check=True, capture_output=True)
    icon = Image.open(rendered).convert('RGBA')
    if 'icc_profile' in icon.info:
        icon = ImageCms.profileToProfile(icon, ImageCms.ImageCmsProfile(BytesIO(icon.info['icc_profile'])), ImageCms.createProfile('sRGB'), outputMode='RGBA')
    icon.resize((256, 256), Image.Resampling.LANCZOS).save(ASSETS / 'img/fondfont-icon.png', optimize=True)
    ns = 'http://www.w3.org/2000/svg'
    ET.register_namespace('', ns)
    mask = ET.Element(f'{{{ns}}}svg', width='1024', height='1024', viewBox='0 0 1024 1024')
    # Original masks already contain the production transforms; no shape redraw.
    for name in ['Bodoni-ff-Back.svg', 'Bodoni-ff-Front.svg']:
        original = ET.parse(ICON / 'Assets' / name).getroot()
        mask.extend(list(original))
    pixels = Image.open(BytesIO(subprocess.check_output(['rsvg-convert'], input=ET.tostring(mask)))).getchannel('A')
    icon.putalpha(pixels)
    result = icon.crop(pixels.getbbox())
    result.save(ASSETS / 'img/fondfont-symbol.png', optimize=True)
    return result


def main():
    font_temp = tempfile.TemporaryDirectory()
    compressed = Path(font_temp.name) / 'sofia.woff2'
    shutil.copyfile(ASSETS / 'fonts/sofia-sans-xcond-latin.woff2', compressed)
    subprocess.run(['woff2_decompress', str(compressed)], check=True)
    face = TTFont(compressed.with_suffix('.ttf'))
    face = instantiateVariableFont(face, {'wght': 900}, inplace=True)
    face.flavor = None
    with tempfile.TemporaryDirectory() as temporary:
        mark = symbol(temporary)
        latin = Path(temporary) / 'sofia.ttf'
        face.save(latin)
        japanese = next(Path('/System/Library/Fonts').glob('* W6.ttc'))
        names = [('shared', 'FONDFONT', latin), ('zh-hans', '爱装字体', Path('/System/Library/Fonts/STHeiti Medium.ttc')),
                 ('zh-hant', '愛裝字體', Path('/System/Library/Fonts/STHeiti Medium.ttc')),
                 ('ja', 'フォンドフォント', japanese), ('ko', '폰드폰트', Path('/System/Library/Fonts/AppleSDGothicNeo.ttc'))]
        for code, title, font_path in names:
            for size in range(180, 50, -1):
                font = ImageFont.truetype(str(font_path), size * SCALE)
                bounds = font.getbbox(title)
                height = bounds[3] - bounds[1]
                tracking = -.01 * size * SCALE if code == 'shared' else 0
                width = font.getlength(title) + tracking * (len(title)-1)
                mark_width = round(height * mark.width / mark.height)
                gap = 20 * SCALE
                if mark_width + gap + width <= 550 * SCALE:
                    break
            canvas = Image.new('RGB', (1200*SCALE, 630*SCALE), '#f8f8f6')
            noise = Image.open(ASSETS / 'img/noise.png').convert('L').resize((125*SCALE, 125*SCALE))
            noise = noise.point(lambda v: round(max(0, min(255, (v-127.5)*1.25+127.5))*.6)).convert('RGBA')
            noise.putalpha(round(255*.09))
            for y in range(0, canvas.height, noise.height):
                for x in range(0, canvas.width, noise.width):
                    canvas.paste(noise, (x,y), noise)
            x = round((canvas.width-mark_width-gap-width)/2)
            y = round((canvas.height-height)/2)
            resized = mark.resize((mark_width,height), Image.Resampling.LANCZOS)
            canvas.paste(resized, (x,y), resized)
            draw = ImageDraw.Draw(canvas)
            cursor = x+mark_width+gap
            if code != 'shared':
                draw.text((cursor,y-bounds[1]), title, font=font, fill='#171717')
            else:
                for i,char in enumerate(title):
                    draw.text((cursor,y-bounds[1]), char, font=font, fill='#171717')
                    cursor += font.getlength(char)+tracking
                    if i+1<len(title):
                        next_char=title[i+1]
                        cursor += font.getlength(char+next_char)-font.getlength(char)-font.getlength(next_char)
            result=canvas.resize((1200,630),Image.Resampling.LANCZOS)
            result.save(ASSETS / f'img/fondfont-opengraph-{code}.png', optimize=True)
            print(code, title)
    font_temp.cleanup()

if __name__=='__main__':
    main()
