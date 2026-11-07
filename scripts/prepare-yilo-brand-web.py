"""Rasterize the current native vector layers for Yilo's transparent web symbol."""
import hashlib
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)

def main():
    source = ROOT / 'scripts/assets/presskit/vectors/yilo-flat.svg'
    svg = ET.parse(source).getroot()
    for child in list(svg):
        if child.tag == f'{{{NS}}}rect':
            svg.remove(child)
    output = ROOT / 'scripts/assets/yilo/symbol.svg'
    output.write_bytes(ET.tostring(svg, encoding='utf-8', xml_declaration=True))
    png = subprocess.check_output(['rsvg-convert', str(output)])
    from io import BytesIO
    image = Image.open(BytesIO(png)).convert('RGBA')
    visible = image.getchannel('A').getbbox()
    # The detached head is excluded from visible-height alignment with the title.
    body_svg = ET.fromstring(ET.tostring(svg))
    for child in list(body_svg):
        if child.find(f'.//{{{NS}}}circle') is not None:
            body_svg.remove(child)
    body = Image.open(BytesIO(subprocess.check_output(['rsvg-convert'], input=ET.tostring(body_svg)))).getchannel('A').getbbox()
    target = ROOT / 'src/assets/img/yilo-symbol.png'
    image.crop(visible).save(target, optimize=True)
    metadata = dict(source='scripts/assets/yilo/AppIcon.icon',
        vector='scripts/assets/yilo/symbol.svg', vectorSha256=hashlib.sha256(output.read_bytes()).hexdigest(),
        output=str(target.relative_to(ROOT)), outputSha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        visibleBounds=visible, bodyBounds=body,
        note='Original native SVG contours, layer positions and default fills; no native glass, lighting or icon container. Detached circular head excluded from title-height alignment.')
    (output.parent / 'brand-source.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print('Exported Yilo transparent symbol from native vector geometry.')

if __name__ == '__main__':
    main()
