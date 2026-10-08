"""Export current YiYan native artwork for the website, without redrawing it."""
from io import BytesIO
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from xml.etree import ElementTree as ET

from PIL import Image, ImageChops, ImageCms

ROOT = Path(__file__).resolve().parents[1]
ICON = ROOT / 'scripts/assets/yiyan/AppIcon.icon'
OUT = ROOT / 'src/assets/img'
ICTOOL = '/Applications/Xcode.app/Contents/Applications/Icon Composer.app/Contents/Executables/ictool'


def main():
    with tempfile.TemporaryDirectory() as temporary:
        native = Path(temporary) / 'native.png'
        subprocess.run([ICTOOL, str(ICON), '--export-image', '--output-file', str(native),
            '--platform', 'macOS', '--rendition', 'Default', '--width', '1024', '--height', '1024', '--scale', '1'],
            check=True, capture_output=True)
        icon = Image.open(native).convert('RGBA')
        if 'icc_profile' in icon.info:
            icon = ImageCms.profileToProfile(icon, ImageCms.ImageCmsProfile(BytesIO(icon.info['icc_profile'])),
                ImageCms.createProfile('sRGB'), outputMode='RGBA')
        icon.resize((512, 512), Image.Resampling.LANCZOS).save(OUT / 'yiyan-icon.png', optimize=True)

        # The exact four SVG silhouettes mask native-rendered pixels. Background
        # and external glow are excluded; glass color inside each shape is intact.
        namespace = 'http://www.w3.org/2000/svg'
        ET.register_namespace('', namespace)
        mask_svg = ET.Element(f'{{{namespace}}}svg', width='1024', height='1024', viewBox='0 0 1024 1024')
        body_svg = ET.Element(f'{{{namespace}}}svg', width='1024', height='1024', viewBox='0 0 1024 1024')
        document = json.loads((ICON / 'icon.json').read_text())
        for group in document['groups']:
            for layer in group['layers']:
                if layer.get('image-name') not in {'10-sun.svg', '20-long-stroke.svg', '30-short-stroke.svg', '40-mouth.svg'}:
                    continue
                svg = ET.parse(ICON / 'Assets' / layer['image-name']).getroot()
                for child in svg:
                    mask_svg.append(child)
                    if layer['image-name'] != '10-sun.svg':
                        body_svg.append(child)
        raster = subprocess.check_output(['rsvg-convert'], input=ET.tostring(mask_svg))
        mask = Image.open(BytesIO(raster)).getchannel('A')
        mask = ImageChops.multiply(mask, icon.getchannel('A'))
        icon.putalpha(mask)
        icon.crop(mask.getbbox()).save(OUT / 'yiyan-symbol.png', optimize=True)
        body_raster = subprocess.check_output(['rsvg-convert'], input=ET.tostring(body_svg))
        body_bounds = Image.open(BytesIO(body_raster)).getchannel('A').getbbox()
        metadata = dict(source='AppIcon.icon', documentSHA256=hashlib.sha256((ICON / 'icon.json').read_bytes()).hexdigest(),
            visibleBounds=mask.getbbox(), bodyBounds=body_bounds,
            note='Native glass pixels in exact authored silhouettes; the sun is excluded from text-height alignment.')
        (ICON.parent / 'brand-source.json').write_text(json.dumps(metadata, indent=2) + '\n')
        print('Updated native YiYan app icon and transparent product symbol.')


if __name__ == '__main__':
    main()
