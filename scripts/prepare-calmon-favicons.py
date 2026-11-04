"""Build small, pixel-aligned Calmon icons for light and dark browser chrome."""
import hashlib
import json
from pathlib import Path
import struct
import xml.etree.ElementTree as ET

from PIL import Image, ImageCms, ImageColor, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'scripts/assets/native-icons/calmon'
OUTPUT = ROOT / 'src/assets/img/calmon-favicon'
BANDS = SOURCE / 'AppIcon.icon/Assets/ColorBands.svg'
profile = bytearray(ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes())
profile[24:36] = struct.pack('>6H', 2000, 1, 1, 0, 0, 0)
PROFILE = bytes(profile)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stripes(size):
    image = Image.new('RGBA', (size, size))
    for shape in ET.parse(BANDS).getroot():
        color = ImageColor.getrgb(shape.attrib['fill'])
        if shape.tag.endswith('rect'):
            ImageDraw.Draw(image).rectangle((0, 0, size, size), fill=(*color, 255))
        else:
            points = [tuple(float(value) * size / 1024 - .5 for value in pair.split(','))
                      for pair in shape.attrib['points'].split()]
            ImageDraw.Draw(image).polygon(points, fill=(*color, 255))
    return image


def render(size, dark):
    scale = size // 16
    suffix = '' if scale == 1 else '@2x'
    source = SOURCE / f'MenuBarIcon.imageset/MenuBarIcon{suffix}.png'
    native = Image.open(source).getchannel('A')
    mask = Image.new('L', (size, size))
    # Keep each letter on whole pixels, with a 2 px gutter and 2 px outer inset.
    for row in range(2):
        for column in range(2):
            x, y = (3 + 9 * column) * scale, (3 + 9 * row) * scale
            letter = native.crop((x, y, x + 7 * scale, y + 7 * scale))
            letter = letter.resize((5 * scale, 5 * scale), Image.Resampling.NEAREST)
            mask.paste(letter, ((2 + 7 * column) * scale, (2 + 7 * row) * scale))
    field = Image.new('L', (size, size))
    ImageDraw.Draw(field).rounded_rectangle((0, 0, size - 1, size - 1), radius=3 * scale, fill=255)
    image = Image.new('RGBA', (size, size), (0, 0, 0, 255)) if dark else stripes(size)
    face = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    if dark:
        face.paste(stripes(12 * scale), (2 * scale, 2 * scale))
    image.paste(face, (0, 0), mask)
    image.putalpha(field)
    image.putdata([pixel if pixel[3] else (0, 0, 0, 0) for pixel in image.getdata()])
    path = OUTPUT / f'favicon{"-dark" if dark else ""}-{size}.png'
    image.save(path, icc_profile=PROFILE, optimize=True)
    assert image.getbbox() == (0, 0, size, size)
    assert image.getpixel((size // 2, size // 2))[:3] == ((0, 0, 0) if dark else stripes(size).getpixel((size // 2, size // 2))[:3])
    assert any(pixel[:3] == ((0, 255, 51) if dark else (255, 255, 255)) for pixel in image.getdata())
    assert Image.open(path).info['icc_profile'] == PROFILE
    return source, path


def pack_ico(images, dark):
    payloads = [path.read_bytes() for path in images]
    directory = bytearray(struct.pack('<HHH', 0, 1, len(images)))
    offset = 6 + 16 * len(images)
    for size, data in zip((16, 32), payloads):
        directory.extend(struct.pack('<BBBBHHII', size, size, 0, 0, 1, 32, len(data), offset))
        offset += len(data)
    ico = OUTPUT / f'favicon{"-dark" if dark else ""}.ico'
    ico.write_bytes(directory + b''.join(payloads))
    return ico


def main():
    OUTPUT.mkdir(exist_ok=True)
    sources, outputs = set(), []
    for dark in (False, True):
        images = []
        for size in (16, 32):
            source, path = render(size, dark)
            sources.add(source)
            images.append(path)
        outputs.extend([*images, pack_ico(images, dark)])
    record = {
        'method': 'Native rounded menu bar letters mapped per cell to whole pixels: 2 px outer inset, 2 px gutters at 16 px. Light: original six green diagonal bands behind white letters. Dark: pure black behind the same bands clipped to the letters, matching the App icon. Explicit sRGB PNGs; ICOs contain exact PNG bytes.',
        'inputs': {str(path.relative_to(ROOT)): digest(path) for path in sorted([*sources, BANDS])},
        'outputs': {str(path.relative_to(ROOT)): digest(path) for path in outputs},
    }
    (ROOT / 'scripts/assets/calmon/favicon-source.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Calmon favicons: light/dark, 16/32 px, vivid sRGB, lossless ICO.')


if __name__ == '__main__':
    main()
