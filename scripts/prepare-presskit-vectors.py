"""Prepare genuine SVG artwork from preserved vectors and exact pixel geometry."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'scripts/assets/presskit/vectors'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
SOURCES = json.loads((ROOT / 'scripts/assets/native-icons/sources.json').read_text())
records = {}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(slug, filename, content, inputs, method):
    output = OUT / filename
    output.write_bytes(content)
    records.setdefault(slug, []).append(dict(output=str(output.relative_to(ROOT)), sha256=digest(output),
        inputs={str(path.relative_to(ROOT)): digest(path) for path in inputs}, method=method))


def color(value):
    space, channels = value.split(':')
    numbers = [float(v) for v in channels.split(',')]
    if 'gray' in space:
        rgb, alpha = numbers[:1] * 3, numbers[1]
    else:
        rgb, alpha = numbers[:3], numbers[3]
    if space == 'display-p3':
        r, g, b = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
        rgb = [1.224745 * r - .224904 * g, -.042058 * r + 1.042081 * g, -.019642 * r - .078655 * g + 1.098537 * b]
        rgb = [12.92 * v if v <= .0031308 else 1.055 * v ** (1 / 2.4) - .055 for v in rgb]
    return '#' + ''.join(f'{round(min(1, max(0, v)) * 255):02x}' for v in rgb), alpha


def default_value(document, key):
    return next((v['value'] for v in document.get(key + '-specializations', []) if not v.get('appearance')), document.get(key))


def paint(svg, value, identifier):
    if 'solid' in value:
        fill, alpha = color(value['solid'])
        return fill, alpha
    stops = value.get('linear-gradient')
    if not stops:
        stops = [value['automatic-gradient']] * 2
    orientation = value.get('orientation', {'start': {'x': .5, 'y': 0}, 'stop': {'x': .5, 'y': 1}})
    gradient = ET.SubElement(svg, f'{{{NS}}}linearGradient', id=identifier,
        x1=str(orientation['start']['x']), y1=str(orientation['start']['y']),
        x2=str(orientation['stop']['x']), y2=str(orientation['stop']['y']))
    for index, stop in enumerate(stops):
        fill, alpha = color(stop)
        ET.SubElement(gradient, f'{{{NS}}}stop', offset=str(index / max(1, len(stops) - 1)),
            attrib={'stop-color': fill, 'stop-opacity': str(alpha)})
    return f'url(#{identifier})', 1


def flat_icon(slug):
    source = ROOT / SOURCES[slug]['source']
    config = source / 'icon.json'
    document = json.loads(config.read_text())
    svg = ET.Element(f'{{{NS}}}svg', width='1024', height='1024', viewBox='0 0 1024 1024')
    fill, alpha = paint(svg, default_value(document, 'fill'), 'canvas')
    ET.SubElement(svg, f'{{{NS}}}rect', width='1024', height='1024', fill=fill, opacity=str(alpha))
    inputs = [config]
    for gi, group in enumerate(reversed(document['groups'])):
        for li, layer in enumerate(reversed(group['layers'])):
            if default_value(layer, 'hidden'):
                continue
            filename = default_value(layer, 'image-name')
            path = source / 'Assets' / filename
            original = deepcopy(ET.parse(path).getroot())
            inputs.append(path)
            prefix = f'g{gi}l{li}-'
            identifiers = {node.get('id'): prefix + node.get('id') for node in original.iter() if node.get('id')}
            for node in original.iter():
                for key, value in list(node.attrib.items()):
                    if key == 'id':
                        node.set(key, identifiers[value])
                    else:
                        node.set(key, re.sub(r'url\(#([^\)]+)\)', lambda m: f'url(#{identifiers[m[1]]})', value))
            x, y, width, height = [float(v) for v in original.get('viewBox').replace(',', ' ').split()]
            position = layer.get('position', {})
            tx, ty = position.get('translation-in-points', [0, 0])
            scale = position.get('scale', 1)
            wrapper = ET.SubElement(svg, f'{{{NS}}}g', transform=f'translate({512 + tx} {512 + ty}) scale({scale}) translate({-x - width / 2} {-y - height / 2})')
            fill_value = default_value(layer, 'fill')
            if fill_value:
                fill, alpha = paint(svg, fill_value, prefix + 'fill')
                for node in original.iter():
                    if node.tag.rsplit('}', 1)[-1] in {'defs', 'linearGradient', 'radialGradient', 'stop'}:
                        continue
                    for key in ['fill', 'stroke']:
                        if node.get(key) and node.get(key) != 'none':
                            node.set(key, fill)
                original.set('fill', fill)
                wrapper.set('opacity', str(alpha))
            original.tag = f'{{{NS}}}g'
            for key in ['width', 'height', 'viewBox']:
                original.attrib.pop(key, None)
            wrapper.append(original)
    save(slug, f'{slug}-flat.svg', ET.tostring(svg, encoding='utf-8', xml_declaration=True), inputs,
        'Flat SVG composition of the original vector layers, native positions, scales and default fills. Native glass, refraction, lighting, shadows and platform icon masks are not reproduced. The native PNG remains the complete rendered app icon.')


def pixel_wordmark():
    source = ROOT / 'public/shheep/assets/sprites/title.png'
    image = Image.open(source).convert('RGBA')
    width, height = image.size
    svg = ET.Element(f'{{{NS}}}svg', width=str(width), height=str(height), viewBox=f'0 0 {width} {height}', attrib={'shape-rendering': 'crispEdges'})
    paths = {}
    for y in range(height):
        x = 0
        while x < width:
            rgba = image.getpixel((x, y))
            end = x + 1
            while end < width and image.getpixel((end, y)) == rgba:
                end += 1
            if rgba[3]:
                paths.setdefault(rgba, []).append(f'M{x} {y}h{end-x}v1H{x}z')
            x = end
    for (r, g, b, alpha), segments in paths.items():
        ET.SubElement(svg, f'{{{NS}}}path', fill=f'#{r:02x}{g:02x}{b:02x}', opacity=str(alpha / 255), d=''.join(segments))
    save('shheep', 'shheep-wordmark.svg', ET.tostring(svg, encoding='utf-8', xml_declaration=True), [source],
        'Lossless pixel-to-vector conversion: each original horizontal run becomes a filled vector path; all RGBA values, transparency, canvas and pixel edges are preserved. No tracing, smoothing or embedded raster image.')


OUT.mkdir(parents=True, exist_ok=True)
for slug in ['chmate', 'world-book', 'yiyan']:
    flat_icon(slug)
for slug, source, filename, method in [
    ('fondfont', 'src/assets/img/fondfont-web-icon.svg', 'fondfont-flat.svg', 'Existing flat artwork using the original Bodoni vector masks, authored transforms and documented flat print colors; native glass effects are not reproduced.'),
    ('xvdl', 'scripts/assets/native-icons/xvdl/icon.svg', 'xvdl-icon.svg', 'Original extension icon SVG, byte-for-byte. Scalable vector artwork; the original native app icon PNG is retained separately.'),
    ('doze', 'scripts/assets/native-icons/doze/AppIcon.icon/Assets/Monogram.svg', 'doze-symbol.svg', 'Original native gold monogram SVG, byte-for-byte.'),
]:
    path = ROOT / source
    save(slug, filename, path.read_bytes(), [path], method)
pixel_wordmark()
for item in json.loads((ROOT / 'scripts/assets/doze/menubar-source.json').read_text())['variants']:
    path = ROOT / item['svgOutput']
    save('doze', path.name, path.read_bytes(), [path, ROOT / 'scripts/assets/doze/StatusIcon.swift'],
        'Exact native CGPath elements serialized as SVG, with the original placement, scale, vertical axis conversion and paused opacity. No raster image or tracing.')
(OUT.parent / 'vector-sources.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
print(f'Prepared {sum(len(items) for items in records.values())} genuine SVG assets across {len(records)} Press Kits.')
