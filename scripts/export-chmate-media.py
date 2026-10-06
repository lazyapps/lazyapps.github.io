"""Export native CHMate screens and independent backdrop/device layers."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from PIL import Image

SITE = Path(__file__).resolve().parents[1]
LOCALES = ['en', 'zh-Hans', 'zh-Hant', 'es', 'pt-BR', 'pt', 'fr', 'de', 'ja', 'ko', 'ar', 'it', 'id', 'nl', 'tr']
DURATION = 26.3
CREDIT = 'Solace by Scott Buckley, CC BY 4.0. Excerpt edited, faded and volume-adjusted.'


def run(*args):
    subprocess.run([str(arg) for arg in args], check=True)


def export_backdrop(source, destination):
    for shape, width, height in [('landscape', 640, 360), ('portrait', 320, 576)]:
        output = destination / f'daylight-{shape}-v3.mp4'
        graph = (
            f'fps=30,scale={width}:{height * 2}:force_original_aspect_ratio=increase,'
            f'crop={width}:{height * 2},'
            f'crop={width}:{height}:0:(in_h-out_h)*(0.5+0.5*cos(2*PI*t/56)),'
            'setsar=1,format=yuv420p'
        )
        run('ffmpeg', '-v', 'error', '-y', '-stream_loop', '-1',
            '-i', source / 'assets/daylight-loop.mp4', '-t', '56', '-an', '-vf', graph,
            '-c:v', 'libx264', '-threads', '2', '-preset', 'medium', '-crf', '23',
            '-movflags', '+faststart', output)
        run('ffmpeg', '-v', 'error', '-y', '-i', output,
            '-frames:v', '1', '-q:v', '2', output.with_suffix('.jpg'))


def export_screen(source, destination, locale, device):
    raw = source / ('raw/ipad/locales' if device == 'ipad' else 'raw/locales') / locale
    manifest = json.loads((raw / 'manifest.json').read_text())
    assert not manifest.get('capturePending'), f'Incomplete capture: {raw}'
    assert manifest['locale'] == locale
    segments = [('intro.mp4', 0, 7)]
    if locale in {'ja', 'zh-Hans', 'zh-Hant'}:
        segments += [('horizontal.mp4', 0, 4.3), ('vertical.mp4', 0, 4.3)]
    else:
        segments += [('horizontal.mp4', 0, 5), ('horizontal.mp4', 5, 10)]
    for clip in {clip for clip, _, _ in segments} | {'themes.mp4'}:
        assert hashlib.sha256((raw / clip).read_bytes()).hexdigest() == manifest['clips'][clip], f'Changed capture: {raw / clip}'
    width = 900 if device == 'ipad' else 664
    hold = 17 - sum(end - start for _, start, end in segments)
    graph = ''.join(f'[{i}:v]trim={start}:{end},setpts=PTS-STARTPTS[c{i}];' for i, (_, start, end) in enumerate(segments))
    graph += (
        f'[c0][c1][c2]concat=n=3:v=1:a=0,fps=30,tpad=stop_mode=clone:stop_duration={hold},trim=duration=17[reading];'
        '[3:v]trim=duration=6.3,setpts=PTS-STARTPTS[themes];'
        '[reading][themes]concat=n=2:v=1:a=0,tpad=stop_mode=clone:stop_duration=3,'
        f'scale={width}:-2:flags=lanczos:in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709,setsar=1,format=yuv420p[v];'
        '[4:a]atrim=duration=26.3,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1.5,afade=t=out:st=23.3:d=3,loudnorm=I=-23:TP=-2:LRA=7[a]'
    )
    inputs = []
    for clip, _, _ in segments:
        inputs += ['-i', raw / clip]
    output = destination / f'screen-{device}-{locale.lower()}-v2.mp4'
    run('ffmpeg', '-v', 'error', '-y', '-filter_complex_threads', '2', *inputs,
        '-i', raw / 'themes.mp4', '-ss', '35', '-i', source / 'assets/sb_solace.mp3',
        '-filter_complex', graph, '-map', '[v]', '-map', '[a]', '-t', DURATION,
        '-c:v', 'libx264', '-threads', '2', '-preset', 'medium', '-crf', '23', '-r', '30',
        '-color_range', 'tv', '-colorspace', 'bt709', '-color_trc', 'bt709', '-color_primaries', 'bt709',
        '-c:a', 'aac', '-b:a', '96k', '-ar', '48000', '-ac', '2',
        '-movflags', '+faststart', '-metadata', f'comment={CREDIT}', output)
    run('ffmpeg', '-v', 'error', '-y', '-ss', '9', '-i', output,
        '-frames:v', '1', '-q:v', '2', output.with_suffix('.jpg'))
    print(f'{device} {locale}: {output.stat().st_size / 1_000_000:.1f} MB', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True, type=Path, help='CHMate Neue/AppPreview directory (read only)')
    parser.add_argument('--locales', nargs='+', choices=LOCALES, default=LOCALES)
    parser.add_argument('--background-only', action='store_true')
    args = parser.parse_args()
    source = args.source_dir.resolve()
    destination = SITE / 'public/v/chmate'
    destination.mkdir(parents=True, exist_ok=True)
    export_backdrop(source, destination)
    if args.background_only:
        return
    shutil.copyfile(source / 'assets/daylight-loop.mp4', destination / 'daylight-v2.mp4')
    run('ffmpeg', '-v', 'error', '-y', '-ss', '3', '-i', destination / 'daylight-v2.mp4',
        '-frames:v', '1', '-q:v', '2', destination / 'daylight-v2.jpg')
    for device, bezel, source_mask in [
        ('iphone', source / 'assets/iphone-18-pro-black-portrait.png', source / 'assets/review-bezel-mask-iPhone-en.png'),
        ('ipad', source.parent / 'AppStoreScreenshots/public/ipad-pro-m5-13-space-black-portrait.png', source / 'assets/review-bezel-mask-iPad-en.png'),
    ]:
        shutil.copyfile(bezel, destination / f'bezel-{device}-v2.png')
        with Image.open(source_mask) as mask:
            alpha_mask = Image.new('RGBA', mask.size, 'white')
            alpha_mask.putalpha(mask.convert('L'))
            alpha_mask.save(destination / f'screen-mask-{device}-v2.png', optimize=True)
    jobs = [(source, destination, locale, device) for locale in args.locales for device in ['iphone', 'ipad']]
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda job: export_screen(*job), jobs))


if __name__ == '__main__':
    main()
