"""15-second edit using existing local MiniMax H3 footage and genuine YiYan UI."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('previous_edit', ROOT / 'scripts/compose-yiyan-marketing-v2.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
ASSETS = ROOT / 'scripts/assets/yiyan/marketing-v3'
OLD = base.ASSETS
PUBLIC = base.PUBLIC
COPY_PATH = ROOT / 'src/i18n/yiyan-short-copy.json'
COPY = json.loads(COPY_PATH.read_text())
W, H, FPS, SECONDS = 1280, 720, 24, 15


def text_config():
    ASSETS.mkdir(parents=True, exist_ok=True)
    entries = []
    for locale, c in COPY.items():
        def add(key, text, width, height, size, color=base.INK, bold=False):
            entries.append(dict(file=f'{locale}-{key}.png', text=text, width=width, height=height,
                                size=size, color=[n / 255 for n in color], bold=bold,
                                align='left', rtl=locale == 'ar'))
        for i in range(3):
            add(f'title{i}', c['video'][i], 1156, 90, 60, bold=True)
            add(f'terms{i}', c['terms'][i], 1156 if i < 2 else 820,
                54 if i < 2 else 170, 30 if i < 2 else 43, base.MUTED)
        add('sync', c['sync'], 1156, 60, 28, base.ACCENT)
    config = ASSETS / 'text-config.json'
    config.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n')
    base.run([OLD / 'render-text', config, ASSETS / 'text'])


class Film(base.Film):
    def __init__(self, locale, plates=None):
        super().__init__(locale, plates)
        entries = json.loads((ASSETS / 'text-config.json').read_text())
        for e in entries:
            if not e['file'].startswith(locale + '-'):
                continue
            key = e['file'][len(locale) + 1:-4]
            self.layers[key] = Image.open(ASSETS / 'text' / e['file']).convert('RGBA').resize(
                (e['width'], e['height']), Image.Resampling.LANCZOS)

    def scene(self, index, t):
        im = self.paper(0 if index == 0 else 1, t) if index != 1 else Image.new('RGB', (W, H), base.PAPER)
        if index == 0:
            # A light wash keeps the genuine H3 motion visible behind the exact example.
            im = Image.blend(im, Image.new('RGB', (W, H), base.PAPER), .45)
        self.brand(im)
        self.layer(im, f'title{index}', (62, 112))
        if index == 0:
            self.layer(im, 'terms0', (62, 202))
            d = ImageDraw.Draw(im)
            d.rounded_rectangle((62, 282, 1218, 590), radius=22, fill=(255, 253, 249))
            self.layer(im, 'original-label', (80, 291))
            self.layer(im, 'original', (80, 341))
            d.line((80, 430, 1198, 430), fill=(217, 199, 183), width=2)
            a = base.smooth((t - .35) / .35)
            self.layer(im, 'natural-label', (80, 436), a)
            self.layer(im, 'natural', (80, 484), a)
            self.layer(im, 'alongside', (80, 624))
        elif index == 1:
            self.layer(im, 'terms1', (62, 196))
            shot = self.screenshot.resize((1016, 441), Image.Resampling.LANCZOS)
            im.paste(shot, (132, 251))
        else:
            # These are editorial feature labels, not fabricated iPhone UI.
            panel = Image.new('RGBA', (W, H))
            d = ImageDraw.Draw(panel)
            d.rounded_rectangle((42, 245, 930, 467), radius=22, fill=(255, 250, 243, 235))
            im = Image.alpha_composite(im.convert('RGBA'), panel).convert('RGB')
            self.layer(im, 'terms2', (62, 266))
            self.layer(im, 'sync', (62, 535))
            self.layer(im, 'url', (80, 625))
        return im

    def frame(self, t):
        index = min(2, int(t // 5))
        local = t - index * 5
        im = self.scene(index, local)
        if index and local < .2:
            im = Image.blend(self.scene(index - 1, 4.99), im, base.smooth(local / .2))
        d = ImageDraw.Draw(im)
        d.rectangle((62, 704, 1218, 707), fill=(226, 212, 196))
        d.rectangle((62, 704, 62 + round(1156 * t / SECONDS), 707), fill=base.ACCENT)
        return im


def export(locale, plates):
    output = PUBLIC / f'hero-{locale}-v3.mp4'
    if output.exists():
        raise RuntimeError(f'Preserve previous export: {output}')
    film = Film(locale, plates)
    process = subprocess.Popen(['ffmpeg', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
        '-s', f'{W}x{H}', '-framerate', str(FPS), '-i', '-', '-an', '-c:v', 'libx264',
        '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
        '-metadata', 'title=YiYan — write, learn, review', '-metadata',
        'comment=15-second edit of locally generated MiniMax H3 footage; authentic YiYan record and native shaped typography.', str(output)], stdin=subprocess.PIPE)
    try:
        for f in range(FPS * SECONDS):
            process.stdin.write(film.frame(f / FPS).tobytes())
        process.stdin.close()
        if process.wait():
            raise RuntimeError('FFmpeg failed')
    except BaseException:
        process.kill()
        raise
    film.frame(1).save(PUBLIC / f'hero-{locale}-v3.jpg', quality=90, optimize=True)
    sources = [OLD / f'{s}-h3.mp4' for s in ['prompt-notebook', 'phrase-collection']]
    sources += [COPY_PATH, Path(__file__), film.screenshot_path]
    manifest = dict(locale=locale, seconds=SECONDS, fps=FPS, model='MiniMax-H3',
        mode='short edit reusing previous local H3 generation',
        chapters={'refine': [0, 5], 'notes_and_Mac_followup': [5, 10], 'iPhone_review': [10, 15]},
        sources=[dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources],
        probe=base.probe(output))
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
        folder = ROOT / 'docs/reviews/yiyan-short-20261008/frames'
        folder.mkdir(exist_ok=True)
        for locale in locales:
            film = Film(locale)
            for t in [1, 6, 11]:
                film.frame(t).save(folder / f'{locale}-{t}.jpg', quality=92)
    else:
        plates = [base.read_plate(OLD / f'{s}-plate.mp4') for s in ['prompt-notebook', 'phrase-collection']]
        for locale in locales:
            export(locale, plates)
