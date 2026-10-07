"""Build a clean, seamless type panorama from licensed font outlines."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / 'scripts/assets/fondfont/animation/PlayfairDisplay.ttf'
OUT = ROOT / 'public/v/fondfont/type-field-v5.svg'


def outline(path, char, x, baseline, size):
    font = TTFont(path)
    glyphs = font.getGlyphSet()
    pen = SVGPathPen(glyphs)
    glyphs[font.getBestCmap()[ord(char)]].draw(pen)
    scale = size / font['head'].unitsPerEm
    return f'<path d="{pen.getCommands()}" transform="translate({x} {baseline}) scale({scale} {-scale})"/>'


def main():
    # Elements do not touch the tile boundary, which makes repeat-x seamless.
    glyphs = [('A', 80, 290, 300), ('g', 550, 580, 330), ('R', 1080, 340, 290),
              ('a', 1460, 730, 350), ('&', 350, 980, 310)]
    paths = [outline(FONT, *g) for g in glyphs]
    paths.append(outline(FONT, 'f', 1060, 1010, 300))
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1120" viewBox="0 0 1800 1120"><g fill="none" stroke="#8c7b6b" stroke-width="18" vector-effect="non-scaling-stroke">' + ''.join(paths) + '</g></svg>\n'
    OUT.write_text(svg)
    print(OUT)


if __name__ == '__main__':
    main()
