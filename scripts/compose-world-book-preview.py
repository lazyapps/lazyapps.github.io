"""Compose a grand H3 assembly without scaling or cropping native app screens."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

SITE = Path(__file__).resolve().parents[1]
MEDIA = SITE / 'public/v/world-book'
ASSEMBLY_SECONDS = 1.6
SETTLE_SECONDS = .4
PRESENTATION_SECONDS = 1
REVEAL_SECONDS = .8
OPENING_SECONDS = ASSEMBLY_SECONDS + SETTLE_SECONDS + PRESENTATION_SECONDS + REVEAL_SECONDS
EFFECTS = SITE / 'scripts/assets/world-book/animation'


def ff(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *map(str, args)], check=True)


def probe(path, count_frames=False):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', *(['-count_frames'] if count_frames else []),
        '-show_streams', '-show_format', '-of', 'json', str(path)]))


def compose(device, motion, music, work, destination):
    native = MEDIA / f'screen-{device}-en.mp4'
    source = probe(native)
    screen = next(stream for stream in source['streams'] if stream['codec_type'] == 'video')
    width, height = screen['width'], screen['height']
    total = OPENING_SECONDS + float(source['format']['duration']) - REVEAL_SECONDS
    intro = work / f'intro-{device}.mp4'
    motion_video = next(stream for stream in probe(motion, count_frames=True)['streams'] if stream['codec_type'] == 'video')
    numerator, denominator = map(int, motion_video['r_frame_rate'].split('/'))
    last_frame_time = (int(motion_video['nb_read_frames']) - 1) * denominator / numerator
    # Reach the assembled endpoint before adding a separate editorial hold.
    timing = (ASSEMBLY_SECONDS - 1 / 30) / last_frame_time
    progress = 'clip((on-33)/25.5,0,1)'
    ease = f'(3*pow({progress},2)-2*pow({progress},3))'
    zoom = 1.42 if device == 'ipad' else 1.16
    # This forward move belongs to the artwork; native footage keeps every pixel.
    framing = (
        f"setpts=(PTS-STARTPTS)*{timing},fps=30,trim=duration={ASSEMBLY_SECONDS},"
        f"tpad=stop_mode=clone:stop_duration={SETTLE_SECONDS+PRESENTATION_SECONDS+REVEAL_SECONDS},"
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height}:x='(iw-ow)/2':y='(ih-oh)/2',"
        f"zoompan=z='1+{zoom-1}*{ease}':x='iw/2-iw/zoom/2':"
        f"y='ih/2-ih/zoom/2':d=1:s={width}x{height}:fps=30,setsar=1"
    )
    ff('-i', motion, '-i', EFFECTS / f'closure-impact-{device}.mkv',
       '-filter_complex_threads', 1, '-filter_complex',
       f'[0:v]{framing}[base];[1:v]setpts=PTS+1.4/TB[burst];'
       '[base][burst]overlay=eof_action=pass:repeatlast=0:format=auto[v]', '-map', '[v]',
       '-t', OPENING_SECONDS, '-an', '-c:v', 'libx264', '-threads', 2,
       '-preset', 'medium', '-crf', 20, '-pix_fmt', 'yuv420p', intro)
    output = destination / f'preview-{device}-en-v7.mp4'
    graph = (
        '[0:v]format=gbrp,split=2[openingHold][openingTail];'
        '[1:v]format=gbrp,split=2[nativeHead][nativeBody];'
        f'[openingHold]trim=duration={OPENING_SECONDS-REVEAL_SECONDS},setpts=PTS-STARTPTS[hold];'
        f'[openingTail]trim=start={OPENING_SECONDS-REVEAL_SECONDS},setpts=PTS-STARTPTS[out];'
        f'[nativeHead]trim=duration={REVEAL_SECONDS},setpts=PTS-STARTPTS[in];'
        f'[nativeBody]trim=start={REVEAL_SECONDS},setpts=PTS-STARTPTS[body];'
        '[2:v]format=gbrp[mask];[out][in][mask]maskedmerge[mixed];'
        '[mixed][3:v]overlay=shortest=1:format=auto[lit];'
        '[hold][lit][body]concat=n=3:v=1:a=0[v];'
        f'[4:a]atrim=duration={total},asetpts=PTS-STARTPTS,loudnorm=I=-23:TP=-2:LRA=9,'
        f'afade=t=in:d=0.6,afade=t=out:st={total-.8}:d=0.8[a]'
    )
    ff('-i', intro, '-i', native,
       '-i', EFFECTS / f'opening-reveal-mask-{device}.mkv',
       '-i', EFFECTS / f'opening-reveal-glow-{device}.mkv', '-ss', 15, '-i', music,
       '-filter_complex_threads', 1, '-filter_complex', graph, '-map', '[v]', '-map', '[a]', '-t', total,
       '-c:v', 'libx264', '-threads', 2, '-preset', 'medium', '-crf', 20, '-pix_fmt', 'yuv420p', '-r', 30,
       '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
       '-c:a', 'aac', '-b:a', '96k', '-ar', 48000, '-ac', 2, '-movflags', '+faststart',
       '-metadata', 'comment=Website preview: MiniMax H3 opening, followed by full-size native World Book recordings. Summer Fun by Ahjay Stelino; Mixkit Stock Music Free License.', output)
    # Initial page and reduced-motion state show a legible native reader.
    shutil.copyfile(native.with_suffix('.jpg'), output.with_suffix('.jpg'))
    info = probe(output)
    video = next(stream for stream in info['streams'] if stream['codec_type'] == 'video')
    assert (video['width'], video['height']) == (width, height)
    assert video['codec_name'] == 'h264' and video['r_frame_rate'] == '30/1'
    assert abs(float(info['format']['duration']) - total) < .1
    assert abs(float(video['duration']) - total) < .05
    output.with_suffix('.json').write_text(json.dumps({
        'dimensions': [width, height], 'duration': total,
        'h3OpeningSeconds': OPENING_SECONDS,
        'assemblySeconds': ASSEMBLY_SECONDS, 'settleSeconds': SETTLE_SECONDS,
        'presentationSeconds': PRESENTATION_SECONDS, 'openingRevealSeconds': REVEAL_SECONDS,
        'artworkFinalZoom': zoom,
        'nativeStartSeconds': OPENING_SECONDS - REVEAL_SECONDS,
        'sourceMotion': str(motion), 'actualNativeScreens': native.name,
        'nativeFraming': 'Full canvas, original aspect ratio, no scale/crop/inset/captions',
        'poster': 'Unchanged native reader poster',
        'music': 'Summer Fun by Ahjay Stelino, Mixkit Stock Music Free License',
        'motionIntent': 'Accelerating H3 country collapse, one closure impulse, then radial illumination into native footage; all effects baked offline',
    }, indent=2) + '\n')
    print(f'{output}: {width}x{height}, {output.stat().st_size / 1_000_000:.1f} MB', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--motion', required=True, type=Path)
    parser.add_argument('--music', required=True, type=Path)
    parser.add_argument('--destination', type=Path, default=MEDIA)
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        for device in ['ipad', 'iphone']:
            compose(device, args.motion.resolve(), args.music.resolve(), Path(temporary), args.destination)


if __name__ == '__main__':
    main()
