"""Agent-robot comedy: multilingual input → English feedback → reuse → win-win.

Fictional stylized animation, not real Trump footage or an endorsement.
All three character shots are animated locally with MiniMax H3. Brand assets,
speech bubbles and native-shaped typography are composited separately.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/yiyan/marketing-v5'
PUBLIC = ROOT / 'public/v/yiyan'
REVIEW = ROOT / 'docs/reviews/yiyan-agents-20261008'
COPY_PATH = ROOT / 'src/i18n/yiyan-agent-film-copy.json'
COPY = json.loads(COPY_PATH.read_text())
W, H, FPS, SECONDS = 1280, 720, 24, 14
INK, PAPER, CORAL = (42, 37, 33), (255, 252, 245), (176, 66, 39)
SECONDARY = (94, 82, 72)
PHRASE = 'Sounds like a win-win.'
INPUTS = ['这样对我们都好。', 'お互いにメリットがあるね。', 'Así ganamos los dos.', 'Good for both of us.']
SCENES = [('robots', 7), ('trump-chat', 3), ('win', 4)]
AGENTS = [('pi', 'Pi'), ('claude', 'Claude Code'), ('codex', 'Codex'), ('opencode', 'OpenCode'), ('antigravity', 'Antigravity')]


def run(args):
    subprocess.run([str(a) for a in args], check=True)


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))


def smooth(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)


def vertical_ink(im):
    bounds = im.getchannel('A').getbbox()
    return im.crop((0, bounds[1], im.width, bounds[3]))


def text_config():
    entries = []
    for locale, c in COPY.items():
        def add(key, text, width, height, size, color=INK, bold=False, center=True, english=False):
            entries.append(dict(file=f'{locale}-{key}.png', text=text, width=width, height=height,
                size=size, color=[v / 255 for v in color], bold=bold,
                align='center' if center else 'left', rtl=locale == 'ar' and not english))
        add('input', c['input'], 1152, 66, 46, bold=True)
        add('feedback', f"{c['brand']} · {c['feedback']}", 710, 48, 26, SECONDARY, center=False)
        add('english', PHRASE, 748, 84, 52, bold=True, center=False, english=True)
        add('lesson', c['lesson'], 748, 48, 26, SECONDARY, center=False)
        add('closing', c['closing'], 800, 48, 26, bold=True)
        add('fiction', c['fiction'], 300, 34, 20, PAPER)
        add('punch', c['punch'], 840, 110, 84, CORAL, bold=True)
        add('brand', c['brand'], 160, 48, 30, bold=True, center=False, english=True)
        for i, text in enumerate(INPUTS):
            add(f'source-{i}', text, 370, 62, 32, center=False, english=True)
        for i, (_, name) in enumerate(AGENTS):
            add(f'agent-{i}', name, 138, 48, 24, center=False, english=True)
    config = ASSETS / 'text-config.json'
    config.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n')
    run([ROOT / 'scripts/assets/yiyan/marketing-v2/render-text', config, ASSETS / 'text'])


def make_plates():
    for scene, seconds in SCENES:
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
        self.logos = [Image.open(ASSETS / f'brand/{name}.png').convert('RGBA') for name, _ in AGENTS]
        self.anchors = [Image.open(ASSETS / f'{s}-anchor.png').convert('RGB').resize((W, H), Image.Resampling.LANCZOS) for s, _ in SCENES]

    def layer(self, canvas, key, xy, alpha=1, scale=1):
        if alpha <= 0:
            return
        im = self.layers[key]
        if scale != 1:
            im = im.resize((round(im.width * scale), round(im.height * scale)), Image.Resampling.LANCZOS)
        if alpha < 1:
            im = im.copy()
            im.putalpha(im.getchannel('A').point(lambda n: round(n * alpha)))
        canvas.paste(im, (round(xy[0]), round(xy[1])), im)

    def background(self, index, t):
        if self.plates is None:
            return self.anchors[index].copy()
        frames = self.plates[index]
        return Image.fromarray(frames[min(len(frames) - 1, round(t * FPS))]).copy()

    def chip(self, canvas, key, x, y, alpha=1, width=390, height=68):
        if alpha <= 0:
            return
        panel = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(panel)
        draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=20, fill=(*PAPER, 246), outline=(100, 77, 57, 42), width=1)
        # Center visible glyphs, excluding native font ascender/descender padding.
        im = vertical_ink(self.layers[key])
        im.thumbnail((width - 20, height - 16), Image.Resampling.LANCZOS)
        panel.alpha_composite(im, ((width - im.width) // 2, (height - im.height) // 2))
        if alpha < 1:
            panel.putalpha(panel.getchannel('A').point(lambda n: round(n * alpha)))
        canvas.paste(panel, (round(x), round(y)), panel)

    def english_card(self, canvas, x, y, scale=1, alpha=1, tail_target=None):
        if alpha <= 0:
            return
        card = Image.new('RGBA', (810, 190), (0, 0, 0, 0))
        icon = self.icon.resize((32, 32), Image.Resampling.LANCZOS)
        header, english, lesson = [vertical_ink(self.layers[key]) for key in ['feedback', 'english', 'lesson']]
        header_height = max(icon.height, header.height)
        content_height = header_height + 20 + english.height + 20 + lesson.height
        top = round(91 - content_height / 2)
        card.alpha_composite(icon, (750 if self.locale == 'ar' else 28, top + (header_height - icon.height) // 2))
        card.alpha_composite(header, (28 if self.locale == 'ar' else 70, top + (header_height - header.height) // 2))
        english_y = top + header_height + 20
        card.alpha_composite(english, (28, english_y))
        card.alpha_composite(lesson, (28, english_y + english.height + 20))

        # One silhouette makes the tail and body share a continuous fill/border.
        padding, supersample = 48, 2
        size = (810 + padding * 2, 190 + padding * 2)
        mask = Image.new('L', (size[0] * supersample, size[1] * supersample))
        d = ImageDraw.Draw(mask)
        rect = tuple((n + padding) * supersample for n in (1, 1, 808, 181))
        d.rounded_rectangle(rect, radius=24 * supersample, fill=255)
        if tail_target:
            tx, ty = (tail_target[0] - x) / scale, (tail_target[1] - y) / scale
            base_x = min(746, max(64, tx))
            top = ty < 1
            edge_y = 1 if top else 181
            dx, dy = tx - base_x, ty - edge_y
            length = math.hypot(dx, dy)
            tip = (base_x + dx / length * 32, edge_y + dy / length * 32)
            overlap_y = edge_y + (2 if top else -2)
            points = [(base_x - 16, overlap_y), (base_x + 16, overlap_y), tip]
            d.polygon([((px + padding) * supersample, (py + padding) * supersample) for px, py in points], fill=255)
        mask = mask.resize(size, Image.Resampling.LANCZOS)
        surface = Image.new('RGBA', size, (*PAPER, 0))
        surface.putalpha(mask.point(lambda n: round(n * 252 / 255)))
        edge = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(5)))
        stroke = Image.new('RGBA', size, (*CORAL, 0))
        stroke.putalpha(edge.point(lambda n: round(n * 110 / 255)))
        surface = Image.alpha_composite(surface, stroke)
        surface.alpha_composite(card, (padding, padding))
        card = surface
        if scale != 1:
            card = card.resize((round(size[0] * scale), round(size[1] * scale)), Image.Resampling.LANCZOS)
        if alpha < 1:
            card.putalpha(card.getchannel('A').point(lambda n: round(n * alpha)))
        canvas.paste(card, (round(x - padding * scale), round(y - padding * scale)), card)

    def robot_labels(self, canvas):
        wash = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(wash)
        for y in range(570, H):
            draw.line((0, y, W, y), fill=(*PAPER, round(min(1, (y - 570) / 70) * 235)))
        canvas.paste(wash, (0, 0), wash)
        for i, center in enumerate([395, 580, 765, 950, 1140]):
            self.layer(canvas, f'agent-{i}', (center - 53, 605))
            # Marks and names share one baseline on a quiet backdrop.
            logo = self.logos[i].copy()
            logo.thumbnail((28, 28), Image.Resampling.LANCZOS)
            canvas.paste(logo, (center - 88, 611), logo)

    def frame(self, t):
        if t < 7:
            im = self.background(0, t)
            self.robot_labels(im)
            a = 1 - smooth((t - 3.9) / .4)
            self.layer(im, 'input', (64, 13), a)
            for i, (x, y) in enumerate([(390, 86), (814, 86), (390, 160), (814, 160)]):
                self.chip(im, f'source-{i}', x, y, smooth((t - .15 - .18 * i) / .25) * a)
            if t >= 3.9:
                a = smooth((t - 3.9) / .35)
                self.chip(im, 'source-0', 400, 28, a, 390, 58)
                self.chip(im, 'source-2', 814, 28, a, 390, 58)
                self.english_card(im, 400, 96 + 12 * (1 - a), alpha=a)
        elif t < 10:
            im = self.background(1, t - 7)
            a = smooth((t - 7) / .3)
            self.english_card(im, 400 - 355 * a, 96 + 414 * a,
                              tail_target=(440, 300) if a >= .98 else None)
        else:
            im = self.background(2, t - 10)
            gradient = np.zeros((H, W, 4), dtype=np.uint8)
            gradient[:, :, :3] = PAPER
            gradient[:, :, 3] = (np.clip((np.arange(H) - 545) / 80, 0, 1) * 248).astype(np.uint8)[:, None]
            im = Image.alpha_composite(im.convert('RGBA'), Image.fromarray(gradient)).convert('RGB')
            a = smooth((t - 10) / .25)
            self.english_card(im, 45 + 255 * a, 510 - 474 * a, scale=1 - .16 * a,
                              tail_target=(450, 350) if a >= .98 else None)
            b = smooth((t - 10.25) / .35)
            self.layer(im, 'punch', (220, 574 + 12 * (1 - b)), b)
            icon = self.icon.resize((48, 48), Image.Resampling.LANCZOS)
            im.paste(icon, (48, 44), icon)
            self.layer(im, 'brand', (108, 49), b)
            self.layer(im, 'closing', (240, 662), b)
        # Knockout watermark: no button, border or panel behind the disclosure.
        watermark = self.layers['fiction']
        watermark = watermark.crop(watermark.getchannel('A').getbbox())
        shadow = Image.new('RGBA', watermark.size, (*INK, 0))
        shadow.putalpha(watermark.getchannel('A').point(lambda n: round(n * .8)))
        label = Image.new('RGBA', (watermark.width + 8, watermark.height + 8))
        label.alpha_composite(shadow, (4, 5))
        label = label.filter(ImageFilter.GaussianBlur(1))
        watermark = watermark.copy()
        watermark.putalpha(watermark.getchannel('A').point(lambda n: round(n * .94)))
        label.alpha_composite(watermark, (4, 4))
        label = label.crop(label.getchannel('A').getbbox())
        margin = 20
        im.paste(label, (W - margin - label.width, H - margin - label.height), label)
        return im


def export(locale, plates):
    film = Film(locale, plates)
    silent = ASSETS / 'silent'
    silent.mkdir(exist_ok=True)
    output, poster = silent / f'hero-{locale}-v5.mp4', PUBLIC / f'hero-{locale}-v5.jpg'
    if output.exists():
        raise RuntimeError(f'Preserve previous export: {output}')
    process = subprocess.Popen(['ffmpeg', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
        '-s', f'{W}x{H}', '-framerate', str(FPS), '-i', '-', '-an', '-c:v', 'libx264',
        '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
        '-metadata', 'title=YiYan — Sounds like a win-win', '-metadata',
        'comment=AI-animated fictional parody. Original character motion generated locally with MiniMax H3. Editorial language examples; no real Trump footage, voice or endorsement.', str(output)], stdin=subprocess.PIPE)
    try:
        for f in range(FPS * SECONDS):
            process.stdin.write(film.frame(f / FPS).tobytes())
        process.stdin.close()
        if process.wait():
            raise RuntimeError('FFmpeg failed')
    except BaseException:
        process.kill()
        raise
    film.frame(2.2).save(poster, quality=91, optimize=True)
    sources = [ASSETS / f'{s}-h3.mp4' for s, _ in SCENES]
    sources += [COPY_PATH, Path(__file__), ROOT / 'scripts/generate-yiyan-marketing-v5.py', ROOT / 'src/assets/img/yiyan-icon.png']
    manifest = dict(locale=locale, seconds=SECONDS, model='MiniMax-H3', mode='original local fictional 3D comedy',
        timeline={'multilingual_input': [0, 4], 'idiomatic_feedback': [4, 7], 'reuse_with_cartoon_trump': [7, 10], 'two_thumbs_up_punchline': [10, 14]},
        dialogue={'inputs': INPUTS, 'english': PHRASE, 'type': 'editorial fictional examples'},
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
        folder = REVIEW / 'frames'
        folder.mkdir(exist_ok=True)
        for locale in locales:
            film = Film(locale)
            for t in [2.2, 5, 8.5, 12]:
                film.frame(t).save(folder / f'{locale}-{t}.jpg', quality=92)
    else:
        make_plates()
        plates = [read_plate(ASSETS / f'{s}-plate.mp4') for s, _ in SCENES]
        for locale in locales:
            export(locale, plates)
