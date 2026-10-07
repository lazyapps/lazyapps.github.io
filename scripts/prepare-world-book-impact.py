"""Bake globe impact and radial light reveals into reusable lossless video layers."""
import argparse
import json
from pathlib import Path
import subprocess

import numpy as np

FPS = 30


def smooth(value):
    return value * value * (3 - 2 * value)


def write_movie(path, width, height, pixels, frames):
    process = subprocess.Popen([
        'ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', pixels,
        '-s', f'{width}x{height}', '-r', str(FPS), '-i', 'pipe:0',
        '-an', '-c:v', 'ffv1', '-threads', '2', '-pix_fmt', 'gray' if pixels == 'gray' else 'bgra',
        str(path),
    ], stdin=subprocess.PIPE)
    for frame in frames:
        process.stdin.write(frame.astype(np.uint8).tobytes())
    process.stdin.close()
    assert process.wait() == 0


def rgba(alpha, color):
    result = np.empty((*alpha.shape, 4), dtype=np.uint8)
    result[:, :, :3] = color
    result[:, :, 3] = np.rint(np.clip(alpha, 0, 1) * 255).astype(np.uint8)
    return result


def export_reveal(destination, device, radius, width, height, label, seconds, strength):
    frames = round(seconds * FPS)
    globe = width * .39
    globe_weight = np.clip((globe - radius) / (width * .025) + .5, 0, 1)
    masks, glows = [], []
    previous = np.zeros((height, width), dtype=np.uint8)
    for index in range(frames):
        p = index / (frames - 1)
        front = globe * smooth(min(p / .82, 1))
        planet = np.clip((front - radius) / (width * .018) + .5, 0, 1)
        backdrop = smooth(np.clip((p - .4) / .6, 0, 1))
        # Light travels across the sphere; the surrounding UI fades without an iris hole.
        mask = np.rint((globe_weight * planet + (1 - globe_weight) * backdrop) * 255).astype(np.uint8)
        if index == 0:
            mask.fill(0)
        elif index == frames - 1:
            mask.fill(255)
        assert np.all(mask >= previous)
        previous = mask
        # Keep the light on the globe's limb, away from native navigation controls.
        limb = np.exp(-np.square((radius - width * .35) / (width * .055)))
        edge = np.exp(-np.square((radius - front) / (width * .014)))
        alpha = strength * edge * limb * np.sin(np.pi * p)
        if index in [0, frames - 1]:
            alpha.fill(0)
        masks.append(mask)
        glows.append(rgba(alpha, (220, 249, 255)))
    write_movie(destination / f'{label}-mask-{device}.mkv', width, height, 'gray', masks)
    write_movie(destination / f'{label}-glow-{device}.mkv', width, height, 'rgba', glows)
    return {'frames': frames, 'seconds': seconds, 'maskEndpoints': [0, 255],
            'monotonicEveryPixel': True, 'glowEndpointsAlpha': [0, 0],
            'maximumGlowAlpha': max(int(frame[:, :, 3].max()) for frame in glows)}


def export_device(destination, device, width, height):
    y, x = np.mgrid[:height, :width]
    radius = np.hypot(x - (width - 1) / 2, y - (height - 1) / 2)
    frames = []
    for index in range(12):
        p = index / 11
        front = width * (.27 + .19 * (1 - (1 - p) ** 3))
        envelope = np.sin(np.pi * p)
        ring = .86 * np.exp(-np.square((radius - front) / (width * .012))) * envelope ** .65
        bloom = .22 * np.exp(-np.square(radius / (width * .26))) * envelope ** 2
        alpha = ring + bloom
        if index in [0, 11]:
            alpha.fill(0)
        frames.append(rgba(alpha, (145, 226, 255)))
    write_movie(destination / f'closure-impact-{device}.mkv', width, height, 'rgba', frames)
    stats = {
        'dimensions': [width, height], 'fps': FPS,
        'closure': {'frames': 12, 'seconds': .4, 'alphaEndpoints': [0, 0],
                    'maximumAlpha': max(int(frame[:, :, 3].max()) for frame in frames)},
        'openingReveal': export_reveal(destination, device, radius, width, height, 'opening-reveal', .8, .32),
        'themeReveal': export_reveal(destination, device, radius, width, height, 'theme-reveal', .6, .18),
        'runtime': 'All layers baked into the one selected foreground H.264 movie',
    }
    (destination / f'impact-{device}.json').write_text(json.dumps(stats, indent=2) + '\n')
    print(device, stats, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, default=Path(__file__).resolve().parent / 'assets/world-book/animation')
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    export_device(args.destination, 'ipad', 900, 1200)
    export_device(args.destination, 'iphone', 664, 1442)


if __name__ == '__main__':
    main()
