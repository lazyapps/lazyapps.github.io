"""Draw the typography-transfer anchors for the FondFont MiniMax H3 hero."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parent / 'assets/fondfont/animation'
SCALE = 2
SIZE = (640, 832)
FONT = ASSETS / 'PlayfairDisplay.ttf'


def anchor(installed):
    image = Image.new('RGB', tuple(n * SCALE for n in SIZE), '#252324')
    draw = ImageDraw.Draw(image)

    def rect(box, fill, radius=14, outline=None, width=1):
        draw.rounded_rectangle(tuple(n * SCALE for n in box), radius=radius * SCALE,
                               fill=fill, outline=outline, width=width * SCALE)

    def line(points, fill, width=1):
        draw.line([(x * SCALE, y * SCALE) for x, y in points], fill=fill,
                  width=width * SCALE, joint='curve')

    def glyph(x, y, size, fill='#252324'):
        font = ImageFont.truetype(str(FONT), size * SCALE)
        draw.text((x * SCALE, y * SCALE), 'Aa', font=font, fill=fill, anchor='mm')

    # Abstract document and presentation specimens: no third-party app interface.
    for box in [(420, 104, 598, 326), (410, 579, 606, 720)]:
        rect((box[0] + 6, box[1] + 8, box[2] + 6, box[3] + 8), '#181718')
        rect(box, '#e9e7df', 5)
    if installed:
        glyph(509, 170, 54)
        glyph(508, 626, 48)
    for y, width in [(222, 125), (235, 108), (248, 125), (261, 84), (280, 125)]:
        line([(447, y), (447 + width, y)], '#c7c3b8', 3)
    line([(434, 680), (493, 680)], '#c83f2a', 4)
    line([(504, 680), (579, 680)], '#c7c3b8', 4)

    # A stable, central library enclosure. It is an illustration, never fake UI.
    rect((167, 289, 455, 557), '#161516', 24)
    rect((161, 278, 449, 546), '#343132', 24, '#575152', 1)
    rect((182, 300, 428, 524), '#1d1b1c', 14)
    line([(195, 491), (415, 491)], '#777065', 2)
    if installed:
        rect((217, 319, 394, 478), '#f0ede3', 9)
        glyph(306, 384, 85)
        rect((373, 457, 416, 500), '#c83f2a', 22)
        line([(385, 478), (392, 485), (405, 470)], '#f8f8f6', 3)
    else:
        rect((34, 334, 178, 486), '#161516', 9)
        rect((28, 326, 172, 478), '#f0ede3', 9)
        glyph(100, 390, 76)
    # Technical conduits communicate transfer without decorative microcopy.
    line([(100, 494), (100, 581), (305, 581), (305, 548)], '#615a52', 2)
    line([(450, 399), (509, 399), (509, 327)], '#615a52', 2)
    line([(450, 450), (508, 450), (508, 578)], '#615a52', 2)
    # The only visible label names the installation destination.
    font = ImageFont.truetype('/System/Library/Fonts/SFNS.ttf', 29 * SCALE)
    draw.text((305 * SCALE, 247 * SCALE), 'iOS', font=font, fill='#f0ede3', anchor='mm')
    return image.resize(SIZE, Image.Resampling.LANCZOS)


if __name__ == '__main__':
    ASSETS.mkdir(parents=True, exist_ok=True)
    for name, installed in [('transfer-start-v1.png', False), ('transfer-end-v1.png', True)]:
        output = ASSETS / name
        if output.exists():
            raise FileExistsError(output)
        anchor(installed).save(output)
