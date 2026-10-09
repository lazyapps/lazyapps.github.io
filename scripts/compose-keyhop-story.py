"""Compose the local H3 fox performance into a shared 15-second story film.

Native CoreText prop labels, genuine app icons on fictional toy props, and a
credited CC BY 4.0 comedy score. No generated macOS UI. Music is Kevin MacLeod’s Monkeys Spinning Monkeys.
Use --stills for the draft board; final exports always use decoded H3 footage.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/keyhop/story-v1'
PUBLIC = ROOT / 'public/v/keyhop'
REVIEW = ROOT / 'docs/reviews/keyhop-story-20261009'
COPY = json.loads((ROOT / 'src/i18n/keyhop-film-copy.json').read_text())
W, H, FPS, SECONDS = 1280, 720, 24, 15
VERSION = 4
SCENES = ['chase', 'hop', 'flow']
APPS = ['safari', 'mail', 'notes', 'messages', 'calendar', 'chrome', 'xcode', 'figma', 'telegram', 'vlc']
NAMES = ['Safari', 'Mail', 'Notes', 'Messages', 'Calendar', 'Chrome', 'Xcode', 'Figma', 'Telegram', 'VLC']
TARGET = 2
KEYS = ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';']
INK = (51, 37, 67)
TEXT_SIZES = {}


def run(args):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True, text=True)


def smooth(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path]).stdout)


def render_text():
    entries = []
    for i, key in enumerate(KEYS):
        entries.append(dict(file=f'key-{i}.png', text=key, width=64, height=48, size=28,
            color=[v / 255 for v in INK], bold=True, align='center', rtl=False))
    for i, name in enumerate(NAMES[:3]):
        entries.append(dict(file=f'app-{i}.png', text=name, width=150, height=40, size=23,
            color=[v / 255 for v in INK], bold=True, align='center', rtl=False))
    entries.append(dict(file='brand.png', text='KeyHop', width=180, height=56, size=34,
        color=[v / 255 for v in INK], bold=True, align='left', rtl=False))
    config = ASSETS / 'text-config.json'
    TEXT_SIZES.update({e['file']: (e['width'], e['height']) for e in entries})
    config.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n')
    # Build from the durable CoreText source; no dependency on another product's binary.
    binary = ASSETS / 'render-text'
    if not binary.exists():
        run(['swiftc', ROOT / 'scripts/render-yiyan-text.swift', '-o', binary])
    run([binary, config, ASSETS / 'text'])


def ink(path):
    im = Image.open(path).convert('RGBA')
    # NSImage's bitmap is Retina-sized on this host; compose in logical pixels.
    im = im.resize(TEXT_SIZES[path.name], Image.Resampling.LANCZOS)
    return im.crop(im.getchannel('A').getbbox())


def soundtrack():
    source = ASSETS / 'music/Monkeys-Spinning-Monkeys.mp3'
    output = ASSETS / 'music/monkeys-15s.wav'
    if not output.exists():
        run(['ffmpeg', '-v', 'error', '-i', source, '-t', str(SECONDS), '-af',
            'loudnorm=I=-22:TP=-2:LRA=9,afade=t=in:st=0:d=0.15,afade=t=out:st=14.3:d=0.7',
            '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s24le', output])
    return output


def plates():
    frames = []
    for scene in SCENES:
        source, output = ASSETS / f'{scene}-h3.mp4', ASSETS / f'{scene}-plate.mp4'
        if not output.exists():
            duration = float(probe(source)['format']['duration'])
            run(['ffmpeg', '-v', 'error', '-filter_threads', '2', '-threads', '2', '-i', source, '-an', '-vf',
                f'setpts={5 / duration}*(PTS-STARTPTS),scale=640:360:flags=lanczos,minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,scale={W}:{H}:flags=lanczos,tpad=stop_mode=clone:stop_duration=1,trim=duration=5,setpts=PTS-STARTPTS',
                '-t', '5', '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p', output])
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(output), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
        frames.append(np.frombuffer(raw, dtype=np.uint8).reshape(-1, H, W, 3))
    return frames


class Film:
    def __init__(self, locale, footage=None):
        self.locale, self.footage = locale, footage
        self.brand = ink(ASSETS / 'text/brand.png')
        self.icon = Image.open(ROOT / 'src/assets/img/keyhop-symbol.png').convert('RGBA')
        self.apps = [Image.open(ROOT / f'src/assets/img/keyhop/apps/{a}.png').convert('RGBA') for a in APPS]
        self.key_text = [ink(ASSETS / 'text' / f'key-{i}.png') for i in range(10)]
        self.app_text = [ink(ASSETS / 'text' / f'app-{i}.png') for i in range(3)]
        self.anchors = [Image.open(ASSETS / f'{s}-anchor.png').convert('RGB').resize((W, H), Image.Resampling.LANCZOS) for s in SCENES]
        self.cards = [self.card(i) for i in range(3)]
        self.keys = [self.key(i) for i in range(10)]

    def card(self, i):
        im = Image.new('RGBA', (180, 202))
        shadow = Image.new('RGBA', im.size)
        d = ImageDraw.Draw(shadow)
        d.rounded_rectangle((12, 18, 169, 189), radius=28, fill=(62, 31, 73, 65))
        im = shadow.filter(ImageFilter.GaussianBlur(7))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((8, 8, 171, 183), radius=28, fill=(222, 207, 228, 255))
        d.rounded_rectangle((8, 2, 171, 174), radius=28, fill=(255, 250, 242, 255),
            outline=(222, 173, 54, 255) if i == TARGET else (209, 194, 216, 255), width=4 if i == TARGET else 2)
        icon = self.apps[i].resize((96, 96), Image.Resampling.LANCZOS)
        im.alpha_composite(icon, (42, 24))
        label = self.app_text[i]
        im.alpha_composite(label, ((180-label.width)//2, 133))
        return im

    def key(self, i):
        im = Image.new('RGBA', (102, 128))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((6, 17, 96, 119), radius=18, fill=(84, 56, 100, 40))
        im = im.filter(ImageFilter.GaussianBlur(4))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((5, 12, 96, 111), radius=18, fill=(217, 191, 227, 255))
        d.rounded_rectangle((5, 3, 96, 100), radius=18, fill=(255, 249, 237, 255),
            outline=(223, 170, 37, 255) if i == TARGET else (195, 165, 213, 255), width=3 if i == TARGET else 1)
        icon = self.apps[i].resize((58, 58), Image.Resampling.LANCZOS)
        im.alpha_composite(icon, (22, 11))
        key = self.key_text[i]
        im.alpha_composite(key, ((102-key.width)//2, 72))
        return im

    def paste(self, canvas, im, xy, alpha=1):
        if alpha < 1:
            im = im.copy(); im.putalpha(im.getchannel('A').point(lambda a: round(a * alpha)))
        canvas.paste(im, (round(xy[0]), round(xy[1])), im)

    def frame(self, t):
        scene = min(2, int(t // 5)); local = t - scene * 5
        if self.footage is None:
            canvas = self.anchors[scene].copy()
        else:
            f = self.footage[scene]
            canvas = Image.fromarray(f[min(len(f)-1, round(local * FPS))]).copy()
        if scene == 0:
            # App order changes only between switching attempts, in two short swaps.
            slots = [1., 2., 0.]
            if local >= 1.6:
                p = smooth((local-1.6)/.26)
                slots = [1-p, 2-p, 2*p]
            if local >= 3.15:
                p = smooth((local-3.15)/.26)
                slots = [0., 1+p, 2-p]
            for i, slot in enumerate(slots):
                x = 738 + slot * 174
                y = 350 + (math.sin(local*6) * 3 if i == TARGET else 0)
                self.paste(canvas, self.cards[i], (x, y))
            # Small wanted-app thought bubble makes the same target unmistakable.
            bubble = Image.new('RGBA', (80, 92))
            d = ImageDraw.Draw(bubble)
            d.rounded_rectangle((3, 2, 76, 73), radius=22, fill=(255, 252, 244, 250), outline=(223,170,37,255), width=2)
            d.ellipse((62, 77, 73, 88), fill=(255, 252, 244, 245))
            bubble.alpha_composite(self.apps[TARGET].resize((52,52), Image.Resampling.LANCZOS), (14, 12))
            self.paste(canvas, bubble, (265, 205), 1-smooth((local-1)/.3))
        elif scene == 1:
            # Notes stays on D, directly under the actual H3 landing position.
            for i in range(10):
                self.paste(canvas, self.keys[i], (225 + i*99, 480))
            if .7 < local < 2.7:
                ring = Image.new('RGBA', (142, 156))
                d = ImageDraw.Draw(ring)
                d.rounded_rectangle((8, 5, 132, 139), radius=26,
                    outline=(246, 187, 45, round(150 * math.sin((local-.7)/2*math.pi))), width=4)
                self.paste(canvas, ring, (205 + TARGET*99, 469))
        # Persistent, restrained authentic product signature.
        icon = self.icon.copy(); icon.thumbnail((36, 36), Image.Resampling.LANCZOS)
        brand = self.brand
        self.paste(canvas, icon, (36, 32))
        self.paste(canvas, brand, (48+icon.width, 33))
        return canvas


def contact_sheet(film, output):
    times = [.8, 2.4, 4.1, 5.4, 6.5, 8.8, 10.8, 12.2, 14.1]
    sheet = Image.new('RGB', (960, 540))
    for i, t in enumerate(times):
        sheet.paste(film.frame(t).resize((320,180), Image.Resampling.LANCZOS), ((i%3)*320, (i//3)*180))
    sheet.save(output)


def export(locale, footage, audio):
    film = Film(locale, footage)
    output = PUBLIC / f'hero-v{VERSION}.mp4'
    if output.exists():
        raise RuntimeError(f'Preserve prior export: {output}')
    log = (ASSETS / f'{locale}-v{VERSION}-encode.log').open('w')
    process = subprocess.Popen(['ffmpeg', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
        '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', str(audio),
        '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264', '-threads', '4', '-preset', 'fast', '-crf', '21',
        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-t', str(SECONDS), '-movflags', '+faststart',
        '-metadata', 'comment=Original fictional fox story; local MiniMax H3 animation, imagegen first-frame art, native app icons and typography, Music: Monkeys Spinning Monkeys by Kevin MacLeod (incompetech.com), CC BY 4.0 https://creativecommons.org/licenses/by/4.0/ . Edited: 15-second excerpt, fades and volume adjustment. No app UI recording.',
        str(output)], stdin=subprocess.PIPE, stdout=log, stderr=log)
    try:
        for frame in range(FPS*SECONDS):
            process.stdin.write(film.frame(frame/FPS).tobytes())
        process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError(f'Encoder failed; inspect {locale}-encode.log')
    finally:
        log.close()
    # Poster and review board come from the encoded film, including its true H3 frame.
    run(['ffmpeg', '-v', 'error', '-ss', '0.8', '-i', output, '-frames:v', '1', '-q:v', '2', PUBLIC / f'hero-v{VERSION}.jpg'])
    contact_sheet(film, REVIEW / f'{locale}-v{VERSION}-contact.jpg')
    info = probe(output)
    video = next(s for s in info['streams'] if s['codec_type'] == 'video')
    audio_info = next(s for s in info['streams'] if s['codec_type'] == 'audio')
    assert (video['width'],video['height'],video['codec_name'],video['pix_fmt'],int(video['nb_frames'])) == (1280,720,'h264','yuv420p',360)
    assert audio_info['codec_name'] == 'aac' and abs(float(info['format']['duration'])-15)<.05
    run(['ffmpeg', '-v', 'error', '-i', output, '-f', 'null', '-'])
    print(output, flush=True)
    return dict(locale='shared', path=str(output.relative_to(ROOT)), bytes=output.stat().st_size,
        sha256=digest(output), posterSHA256=digest(PUBLIC / f'hero-v{VERSION}.jpg'), probe=info)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stills', action='store_true')
    parser.add_argument('--locale', choices=list(COPY))
    args = parser.parse_args()
    PUBLIC.mkdir(parents=True, exist_ok=True)
    render_text()
    if args.stills:
        contact_sheet(Film(args.locale or 'zh-hans'), REVIEW / f'draft-board-v{VERSION}.jpg')
    else:
        footage, audio = plates(), soundtrack()
        # Captions now live on the page; the clean picture and score are shared.
        records = [export('zh-hans', footage, audio)]
        intervals = [('chase', '00:00.000', '00:05.000'), ('hop', '00:05.000', '00:10.000'),
                     ('flow', '00:10.000', '00:12.700'), ('tagline', '00:12.700', '00:15.000')]
        for locale, copy in COPY.items():
            cues = ['WEBVTT']
            for key, start, end in intervals:
                cues.append(f'{key}\n{start} --> {end}\n{copy[key]}')
            (PUBLIC / f'captions-{locale}-v{VERSION}.vtt').write_text('\n\n'.join(cues) + '\n')
        (REVIEW / (f'validation-v{VERSION}.json' if not args.locale else f'validation-{args.locale}-v{VERSION}.json')).write_text(json.dumps(dict(
            model='MiniMax-H3', inference='local', soundtrackSHA256=digest(audio),
            music=dict(title='Monkeys Spinning Monkeys', artist='Kevin MacLeod', license='CC BY 4.0',
                source='https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400011',
                licenseURL='https://creativecommons.org/licenses/by/4.0/',
                originalSHA256=digest(ASSETS / 'music/Monkeys-Spinning-Monkeys.mp3'),
                edit='15-second opening excerpt; -22 LUFS normalization and fades'),
            sources=[dict(scene=s, sha256=digest(ASSETS / f'{s}-h3.mp4')) for s in SCENES],
            outputs=records), ensure_ascii=False, indent=2)+'\n')
