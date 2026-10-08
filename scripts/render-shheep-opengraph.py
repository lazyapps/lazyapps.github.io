"""Compose Shheep's social card from the game's original pixel art."""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ROOT / 'public/shheep/assets/sprites'
OUTPUT = ROOT / 'public/shheep/opengraph.png'


def sprite(name, scale):
    image = Image.open(SPRITES / f'{name}.png').convert('RGBA')
    return image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)


def main():
    room = sprite('room', 4)
    left = (room.width - 1200) // 2
    top = room.height - 630
    card = room.crop((left, top, left + 1200, top + 630))
    # Keep the original wordmark and sleeping girl inside the central square crop.
    for name, scale, y in [('title_bubble', 4, 98), ('title', 3, 83), ('bed_sleep', 3, 338)]:
        image = sprite(name, scale)
        x = (card.width - image.width) // 2
        assert x >= 285 and x + image.width <= 915
        assert y >= 0 and y + image.height <= 630
        card.alpha_composite(image, (x, y))
    card.convert('RGB').save(OUTPUT, optimize=True)
    print(f'{OUTPUT}: 1200 × 630; original game sprites, nearest-neighbor scaling.')


if __name__ == '__main__':
    main()
