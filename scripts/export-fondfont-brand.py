"""Export the production AppIcon and a flat print using its exact vector masks."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from copy import deepcopy
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'scripts/assets/fondfont/AppIcon.icon'
IMAGES = ROOT / 'src/assets/img'
PUBLIC = ROOT / 'public/v/fondfont/blender-v2'
ICTOOL = '/Applications/Xcode.app/Contents/Applications/Icon Composer.app/Contents/Executables/ictool'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def flat_color(stops):
    # Flatten the production Display P3 gradient in linear light, then map to sRGB.
    def linear(v):
        return v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4

    colors = [[linear(float(v)) for v in stop.split(':')[1].split(',')[:3]] for stop in stops]
    r, g, b = [sum(c[i] for c in colors) / len(colors) for i in range(3)]
    rgb = [1.224745 * r - .224904 * g, -.042058 * r + 1.042081 * g,
           -.019642 * r - .078655 * g + 1.098537 * b]
    def encoded(v):
        v = min(1, max(0, v))
        return round(255 * (12.92 * v if v <= .0031308 else 1.055 * v ** (1 / 2.4) - .055))
    return '#' + ''.join(f'{encoded(v):02x}' for v in rgb)


def main():
    config = json.loads((SOURCE / 'icon.json').read_text())
    ground = flat_color(config['fill-specializations'][0]['value']['linear-gradient'])
    red_group = next(g for g in config['groups'] if g['name'] == '01 · Vivid red glass')
    red_layer = next(l for l in red_group['layers'] if l['image-name'] == 'Bodoni-ff-Back.svg')
    red = flat_color(red_layer['fill-specializations'][0]['value']['linear-gradient'])
    svg = ET.Element(f'{{{NS}}}svg', width='1024', height='1024', viewBox='0 0 1024 1024')
    ET.SubElement(svg, f'{{{NS}}}rect', width='1024', height='1024', fill=ground)
    masks = {}
    for name, color in [('Bodoni-ff-Back.svg', red), ('Bodoni-ff-Front.svg', '#ffffff')]:
        source = SOURCE / 'Assets' / name
        original = ET.parse(source).getroot()
        group = ET.SubElement(svg, f'{{{NS}}}g', fill=color)
        # Keep every original path coordinate and production transform unchanged.
        for node in original:
            if node.tag != f'{{{NS}}}title':
                for path in node.iter(f'{{{NS}}}path'):
                    path.set('fill', color)
                group.append(node)
        masks[name] = hashlib.sha256(source.read_bytes()).hexdigest()
    vector = ET.tostring(svg, encoding='utf-8', xml_declaration=True)
    (IMAGES / 'fondfont-web-icon.svg').write_bytes(vector)
    (PUBLIC / 'cab-appicon-flat-v2.svg').write_bytes(vector)
    paint = deepcopy(svg)
    paint.remove(paint.find(f'{{{NS}}}rect'))
    for node in paint.iter():
        if 'fill' in node.attrib:
            node.set('fill', '#fff6e9')
    (PUBLIC / 'cab-symbol-paint-v3.svg').write_bytes(ET.tostring(paint, encoding='utf-8', xml_declaration=True))
    subprocess.run([ICTOOL, str(SOURCE), '--export-image', '--output-file',
                    str(IMAGES / 'fondfont-icon.png'), '--platform', 'iOS',
                    '--rendition', 'Default', '--width', '256', '--height', '256',
                    '--scale', '1', '--design-generation', '27'], check=True)
    # A small-size web rendition changes native material contrast, never the masks.
    with tempfile.TemporaryDirectory(prefix='fondfont-web-icon-') as temporary:
        web_source = Path(temporary) / 'AppIcon.icon'
        shutil.copytree(SOURCE, web_source)
        web = json.loads((web_source / 'icon.json').read_text())
        front = next(g for g in web['groups'] if g['name'] == '02 · Clear glass')
        front['translucency']['value'] = .12
        front['shadow']['opacity'] = .16
        layer = next(l for l in front['layers'] if l['image-name'] == 'Bodoni-ff-Front.svg')
        layer['fill-specializations'][0]['value']['linear-gradient'] = [
            'display-p3:1.00000,1.00000,1.00000,0.55000',
            'display-p3:1.00000,1.00000,1.00000,0.35000',
        ]
        (web_source / 'icon.json').write_text(json.dumps(web))
        subprocess.run([ICTOOL, str(web_source), '--export-image', '--output-file',
                        str(IMAGES / 'fondfont-web-icon.png'), '--platform', 'iOS',
                        '--rendition', 'Default', '--width', '256', '--height', '256',
                        '--scale', '1', '--design-generation', '27'], check=True)
    (SOURCE.parent / 'brand-source.json').write_text(json.dumps({
        'source': 'AppIcon.icon', 'sourceConfigSha256': hashlib.sha256((SOURCE / 'icon.json').read_bytes()).hexdigest(),
        'originalMasksSha256': masks,
        'originalExport': 'fondfont-icon.png: unmodified Icon Composer Default iOS export, 256px, generation 27',
        'headerAndFavicon': 'fondfont-web-icon.png: same original masks and native renderer, brighter front material for web',
        'webMaterialAdjustments': {'frontWhiteAlpha': [.55, .35], 'frontTranslucency': .12, 'frontShadowOpacity': .16},
        'flat': {'ground': ground, 'rear': red, 'front': '#ffffff',
                 'geometry': 'Original full 1024 canvas, original paths and transforms, rear then front',
                 'materials': 'Opaque flat colors; no glass, gradient, reflections or generated artwork'},
        'cabPaint': {'asset': 'cab-symbol-paint-v3.svg', 'fill': '#fff6e9',
                     'background': 'transparent', 'geometry': 'Same original masks, transforms and full canvas; no background rectangle'},
    }, indent=2) + '\n')


if __name__ == '__main__':
    main()
