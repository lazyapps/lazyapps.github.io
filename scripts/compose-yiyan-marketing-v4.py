"""A 12-second lifestyle story: your own words, used again in life.

The dialogue is editorial campaign copy, not an actual app screenshot or model
result. Original local MiniMax H3 footage supplies all live-action movement.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/yiyan/marketing-v4'
PUBLIC = ROOT / 'public/v/yiyan'
COPY_PATH = ROOT / 'src/i18n/yiyan-story-copy.json'
COPY = json.loads(COPY_PATH.read_text())
W, H, FPS, SECONDS = 1280, 720, 24, 12
INK, PAPER, CORAL = (42, 37, 33), (250, 245, 237), (176, 66, 39)


def run(command):
    subprocess.run([str(v) for v in command], check=True)


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))


def smooth(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)


def text_config():
    entries = []
    for locale, c in COPY.items():
        def add(key, text, width, height, size, color, center=True, bold=False, english=False):
            entries.append(dict(file=f'{locale}-{key}.png', text=text, width=width, height=height,
                size=size, color=[v / 255 for v in color], bold=bold,
                align='center' if center else 'left', rtl=locale == 'ar' and not english))
        add('before', c['before'], 600, 56, 28, (255, 255, 255), center=False)
        add('after', c['after'], 600, 56, 28, (255, 255, 255), center=False)
        add('quote', c['quote'], 1136, 100, 49, (255, 255, 255), bold=True)
        add('english', 'Let’s pick this up tomorrow.', 1136, 100, 53, (255, 255, 255), bold=True, english=True)
        add('brand', c['brand'], 1120, 118, 86, INK, bold=True, english=True)
        add('closing', c['closing'], 1120, 184, 56, INK, bold=True)
        add('url', 'lazyapps.com/yiyan', 1120, 52, 27, CORAL, english=True)
    config = ASSETS / 'text-config.json'
    config.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n')
    run([ROOT / 'scripts/assets/yiyan/marketing-v2/render-text', config, ASSETS / 'text'])


def make_plates():
    for scene, seconds in [('work', 4.25), ('cafe', 4.75)]:
        raw, output = ASSETS / f'{scene}-h3.mp4', ASSETS / f'{scene}-plate.mp4'
        if output.exists():
            continue
        duration = float(probe(raw)['format']['duration'])
        run(['ffmpeg', '-v', 'error', '-i', raw, '-an', '-vf',
            f'setpts={seconds / duration}*(PTS-STARTPTS),scale={W}:{H}:flags=lanczos,minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,tpad=stop_mode=clone:stop_duration=1,trim=duration={seconds},setpts=PTS-STARTPTS',
            '-t', str(seconds), '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p', output])


def read_plate(path):
    data = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    return np.frombuffer(data, dtype=np.uint8).reshape(-1, H, W, 3)


class Film:
    def __init__(self, locale, plates=None):
        self.locale, self.plates = locale, plates
        self.layers = {}
        for e in json.loads((ASSETS / 'text-config.json').read_text()):
            if e['file'].startswith(locale + '-'):
                key = e['file'][len(locale) + 1:-4]
                self.layers[key] = Image.open(ASSETS / 'text' / e['file']).convert('RGBA').resize(
                    (e['width'], e['height']), Image.Resampling.LANCZOS)
        self.icon = Image.open(ROOT / 'src/assets/img/yiyan-icon.png').convert('RGBA')
        self.anchors = [Image.open(ASSETS / f'{s}-anchor.png').convert('RGB').resize((W, H), Image.Resampling.LANCZOS) for s in ['work', 'cafe']]
        gradient = np.zeros((H, W, 4), dtype=np.uint8)
        # Subtitles have a quiet photographic scrim, not a box or interface card.
        y = np.arange(H)
        gradient[:, :, 3] = np.maximum(np.clip((y - 395) / 325, 0, 1) * 175,
                                      np.clip((160 - y) / 160, 0, 1) * 58).astype(np.uint8)[:, None]
        self.scrim = Image.fromarray(gradient)

    def layer(self, canvas, key, xy, alpha=1, lift=0):
        if alpha <= 0:
            return
        im = self.layers[key]
        if alpha < 1:
            im = im.copy()
            im.putalpha(im.getchannel('A').point(lambda n: round(n * alpha)))
        canvas.paste(im, (round(xy[0]), round(xy[1] + lift)), im)

    def live(self, index, t):
        if self.plates is None:
            im = self.anchors[index].copy()
        else:
            frames = self.plates[index]
            im = Image.fromarray(frames[min(len(frames) - 1, round(t * FPS))]).copy()
        im = Image.alpha_composite(im.convert('RGBA'), self.scrim).convert('RGB')
        self.layer(im, 'before' if index == 0 else 'after', (62 if self.locale != 'ar' else 618, 43))
        self.layer(im, 'quote' if index == 0 else 'english', (72, 558), smooth((t - .15) / .35))
        return im

    def end(self, t):
        im = Image.new('RGB', (W, H), PAPER)
        a = smooth(t / .35)
        icon = self.icon.resize((100, 100), Image.Resampling.LANCZOS)
        if a < 1:
            icon.putalpha(icon.getchannel('A').point(lambda n: round(n * a)))
        im.paste(icon, (590, 90), icon)
        self.layer(im, 'brand', (80, 226), a)
        self.layer(im, 'closing', (80, 378), a, 12 * (1 - a))
        self.layer(im, 'url', (80, 621), a)
        return im

    def frame(self, t):
        if t < 4.25:
            return self.live(0, t)
        if t < 9:
            return self.live(1, t - 4.25)
        im = self.end(t - 9)
        if t < 9.2:
            im = Image.blend(self.live(1, 4.74), im, smooth((t - 9) / .2))
        return im


def export(locale, plates):
    film = Film(locale, plates)
    # The finishing script adds licensed music to these preserved silent renders.
    (ASSETS / 'silent').mkdir(exist_ok=True)
    output, poster = ASSETS / 'silent' / f'hero-{locale}-v4.mp4', PUBLIC / f'hero-{locale}-v4.jpg'
    if output.exists():
        raise RuntimeError(f'Preserve previous export: {output}')
    process = subprocess.Popen(['ffmpeg', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
        '-s', f'{W}x{H}', '-framerate', str(FPS), '-i', '-', '-an', '-c:v', 'libx264',
        '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
        '-metadata', 'title=YiYan — your words today, your English tomorrow', '-metadata',
        'comment=Original lifestyle footage animated locally with MiniMax H3. Editorial dialogue and authentic YiYan brand, not an app demo.', str(output)], stdin=subprocess.PIPE)
    try:
        for f in range(FPS * SECONDS):
            process.stdin.write(film.frame(f / FPS).tobytes())
        process.stdin.close()
        if process.wait():
            raise RuntimeError('FFmpeg failed')
    except BaseException:
        process.kill()
        raise
    film.frame(1).save(poster, quality=91, optimize=True)
    sources = [ASSETS / f'{s}-h3.mp4' for s in ['work', 'cafe']]
    sources += [COPY_PATH, Path(__file__), ROOT / 'scripts/generate-yiyan-marketing-v4.py', ROOT / 'scripts/render-yiyan-text.swift']
    manifest = dict(locale=locale, seconds=SECONDS, model='MiniMax-H3', mode='original local lifestyle generation',
        timeline={'yesterday_work': [0, 4.25], 'today_goodbye': [4.25, 9], 'brand': [9, 12]},
        dialogue={'source': COPY[locale]['quote'], 'english': 'Let’s pick this up tomorrow.', 'type': 'editorial fictional narrative'},
        sources=[dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources],
        outputs=[dict(path=str(p.relative_to(ROOT)), bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [output, poster]], probe=probe(output))
    (ASSETS / f'manifest-{locale}.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(output, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--locale', choices=COPY)
    parser.add_argument('--review-frames', action='store_true')
    args = parser.parse_args()
    text_config()
    locales = [args.locale] if args.locale else COPY
    if args.review_frames:
        folder = ROOT / 'docs/reviews/yiyan-story-20261008/frames'
        folder.mkdir(exist_ok=True)
        for locale in locales:
            film = Film(locale)
            for t in [1, 5, 10]:
                film.frame(t).save(folder / f'{locale}-{t}.jpg', quality=92)
    else:
        make_plates()
        plates = [read_plate(ASSETS / f'{s}-plate.mp4') for s in ['work', 'cafe']]
        for locale in locales:
            export(locale, plates)
