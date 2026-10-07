"""Export reviewed World Book native screens and flat illustrated map background."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


SITE = Path(__file__).resolve().parents[1]
SCENES = [('globe', 6), ('reader', 7), ('charts', 10), ('gallery', 6.2)]
FADE = .4
PAGE_TRANSITION = .7
GLOBE_REVEAL = .6


def ff(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *map(str, args)], check=True)


def check_video(path, seconds):
    info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error',
        '-select_streams', 'v:0', '-show_entries', 'stream=duration,start_time,nb_frames',
        '-of', 'json', str(path)]))['streams'][0]
    assert abs(float(info['start_time'])) < .001, (path, info)
    assert abs(float(info['duration']) - seconds) < .05, (path, info)


def export_screen(source, destination, device, work, transition_motion, globe_effects):
    width = 900 if device == 'ipad' else 664
    encoding = ['-an', '-c:v', 'libx264', '-threads', 2, '-preset', 'fast', '-crf', 23, '-pix_fmt', 'yuv420p']
    for index, (scene, duration) in enumerate(SCENES):
        theme_transition = GLOBE_REVEAL if scene == 'globe' and globe_effects else FADE
        half = (duration + theme_transition) / 2
        for theme in ['dark', 'light']:
            capture = source / 'sources' / theme / f'{device}-{scene}'
            if scene in ['reader', 'gallery']:
                inputs = ['-loop', 1, '-framerate', 30, '-i', capture.with_suffix('.png')]
            else:
                start = (2 if scene == 'globe' else 4) if device == 'ipad' else 0
                inputs = ['-ss', start, '-i', capture.with_suffix('.mov')]
            ff(*inputs, '-vf', f'setpts=PTS-STARTPTS,fps=30,scale={width}:-2:flags=lanczos,setsar=1,tpad=stop_mode=clone:stop_duration={half}',
               '-t', half, *encoding, work / f'{index}-{theme}.mp4')
            check_video(work / f'{index}-{theme}.mp4', half)
        if scene == 'globe' and globe_effects:
            graph = (
                '[0:v]format=gbrp,split=2[darkHold][darkTail];'
                '[1:v]format=gbrp,split=2[lightHead][lightHold];'
                f'[darkHold]trim=duration={half-theme_transition},setpts=PTS-STARTPTS[d];'
                f'[darkTail]trim=start={half-theme_transition},setpts=PTS-STARTPTS[out];'
                f'[lightHead]trim=duration={theme_transition},setpts=PTS-STARTPTS[in];'
                f'[lightHold]trim=start={theme_transition},setpts=PTS-STARTPTS[l];'
                '[2:v]format=gbrp[mask];[out][in][mask]maskedmerge[mixed];'
                '[mixed][3:v]overlay=shortest=1:format=auto[lit];'
                '[d][lit][l]concat=n=3:v=1:a=0[v]'
            )
            ff('-i', work / f'{index}-dark.mp4', '-i', work / f'{index}-light.mp4',
               '-i', globe_effects / f'theme-reveal-mask-{device}.mkv',
               '-i', globe_effects / f'theme-reveal-glow-{device}.mkv',
               '-filter_complex_threads', 1, '-filter_complex', graph, '-map', '[v]',
               '-t', duration, *encoding, work / f'{index}.mp4')
        else:
            ff('-i', work / f'{index}-dark.mp4', '-i', work / f'{index}-light.mp4',
               '-filter_complex_threads', 1, '-filter_complex',
               f'[0:v][1:v]xfade=transition=fade:duration={FADE}:offset={half-FADE}',
               '-t', duration, *encoding, work / f'{index}.mp4')
        check_video(work / f'{index}.mp4', duration)
    inputs = []
    for index in range(4):
        inputs += ['-i', work / f'{index}.mp4']
    filters = []
    if transition_motion:
        inputs += ['-i', transition_motion]
        height = 1200 if device == 'ipad' else 1442
        filters.append(f'[4:v]scale={width}:{height},format=gbrp,split=3[mask0][mask1][mask2]')
        sequence = []
        for index, (_, seconds) in enumerate(SCENES):
            parts = ([f'head{index}'] if index else []) + [f'body{index}'] + ([f'tail{index}'] if index < 3 else [])
            filters.append(f'[{index}:v]format=gbrp,split={len(parts)}' + ''.join(f'[{part}]' for part in parts))
            start = PAGE_TRANSITION if index else 0
            end = seconds - PAGE_TRANSITION if index < 3 else seconds
            filters.append(f'[body{index}]trim=start={start}:end={end},setpts=PTS-STARTPTS[hold{index}]')
            if index:
                filters.append(f'[head{index}]trim=duration={PAGE_TRANSITION},setpts=PTS-STARTPTS[in{index}]')
            if index < 3:
                filters.append(f'[tail{index}]trim=start={seconds-PAGE_TRANSITION}:end={seconds},setpts=PTS-STARTPTS[out{index}]')
            sequence += [f'[hold{index}]'] + ([f'[transition{index}]'] if index < 3 else [])
        for index in range(3):
            filters.append(f'[out{index}][in{index+1}][mask{index}]maskedmerge[transition{index}]')
        filters.append(''.join(sequence) + 'concat=n=7:v=1:a=0[native]')
        previous = 'native'
        total = sum(seconds for _, seconds in SCENES) - 3 * PAGE_TRANSITION
        audio_index = 5
    else:
        previous = '0:v'
        start = 0
        for index in range(1, 4):
            start += SCENES[index-1][1] - FADE
            filters.append(f'[{previous}][{index}:v]xfade=transition=fade:duration={FADE}:offset={start}[cut{index}]')
            previous = f'cut{index}'
        total = sum(seconds for _, seconds in SCENES) - 3 * FADE
        audio_index = 4
    filters.append(f'[{audio_index}:a]atrim=duration={total},asetpts=PTS-STARTPTS,loudnorm=I=-23:TP=-2:LRA=9,afade=t=in:d=0.4,afade=t=out:st={total-.8}:d=0.8[a]')
    output = destination / f'screen-{device}-en.mp4'
    ff(*inputs, '-ss', 15, '-i', source / 'sources/Summer-Fun.mp3',
       '-filter_complex_threads', 1, '-filter_complex', ';'.join(filters), '-map', f'[{previous}]', '-map', '[a]',
       '-t', total, '-c:v', 'libx264', '-threads', 2, '-preset', 'medium', '-crf', 23,
       '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
       '-c:a', 'aac', '-b:a', '96k', '-ar', 48000, '-ac', 2, '-movflags', '+faststart',
       '-metadata', 'comment=Summer Fun by Ahjay Stelino; Mixkit Stock Music Free License. Edited excerpt with fades and volume adjustment.', output)
    check_video(output, total)
    ff('-ss', 10.7, '-i', output, '-frames:v', 1, '-q:v', 2, output.with_suffix('.jpg'))
    print(f'{output}: {output.stat().st_size / 1_000_000:.1f} MB', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True, type=Path)
    parser.add_argument('--background-only', action='store_true')
    parser.add_argument('--transition-motion', type=Path, help='Normalized H3 reveal matte; omitted for original dissolve exports')
    parser.add_argument('--globe-effects', type=Path, help='Offline radial illumination layers for the globe theme change')
    parser.add_argument('--destination', type=Path, default=SITE / 'public/v/world-book')
    args = parser.parse_args()
    source = args.source_dir.resolve()
    destination = args.destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    for layer in ['bezel-ipad', 'screen-mask-ipad']:
        shutil.copyfile(SITE / f'public/v/chmate/{layer}-v2.png', destination / f'{layer}.png')
    ff('-i', SITE / 'scripts/assets/world-book/animation/flat-map-v1.png',
       '-vf', 'scale=1600:800', '-q:v', 3, destination / 'flat-map-v1.jpg')
    if args.background_only:
        return
    for device in ['iphone', 'ipad']:
        with tempfile.TemporaryDirectory() as temporary:
            export_screen(source, destination, device, Path(temporary), args.transition_motion, args.globe_effects)


if __name__ == '__main__':
    main()
