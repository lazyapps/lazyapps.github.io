"""Pace the inspected H3 convergence and interpolate it offline to 30 fps."""
import argparse
import json
import math
from pathlib import Path
import subprocess

ASSEMBLY_SECONDS = 1.6
FPS = 30


def probe(path):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(path)]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--arrival-seconds', type=float, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = next(s for s in probe(args.source)['streams'] if s['codec_type'] == 'video')
    numerator, denominator = map(int, source['r_frame_rate'].split('/'))
    source_fps = numerator / denominator
    last_arrival_frame = (math.ceil(args.arrival_seconds * source_fps) - 1) / source_fps
    end = ASSEMBLY_SECONDS - 1 / FPS
    # Preserve a short anticipation, then accelerate the active inward travel.
    time = '(PTS-STARTPTS)*TB'
    pace = (f'if(lte({time},1),{time}*0.4,'
            f'if(lte({time},2.7),0.4+1.05*pow(({time}-1)/1.7,0.75),'
            f'1.45+({end}-1.45)*({time}-2.7)/({last_arrival_frame}-2.7)))')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        'ffmpeg', '-v', 'error', '-y', '-i', str(args.source), '-filter_threads', '4',
        '-vf', f'trim=duration={args.arrival_seconds},setpts=\'{pace}/TB\','
        'tpad=stop_mode=clone:stop_duration=0.5,'
        f'minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,'
        f'trim=duration={ASSEMBLY_SECONDS}',
        '-an', '-c:v', 'ffv1', '-threads', '2', str(args.output),
    ], check=True)
    result = next(s for s in probe(args.output)['streams'] if s['codec_type'] == 'video')
    frames = int(subprocess.check_output([
        'ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
        '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', str(args.output)]))
    assert frames == round(ASSEMBLY_SECONDS * FPS)
    assert (result['width'], result['height']) == (source['width'], source['height'])
    assert result['r_frame_rate'] == f'{FPS}/1'
    assert float(result['start_time']) == 0
    args.output.with_suffix('.json').write_text(json.dumps({
        'sourceH3': str(args.source), 'inspectedArrivalSeconds': args.arrival_seconds,
        'assemblySeconds': ASSEMBLY_SECONDS, 'frames': frames, 'fps': FPS,
        'interpolation': 'Offline motion-compensated optical flow; no browser effect',
        'editorialChange': '0.4 second anticipation, accelerating country travel, decisive arrival; omit generated static tail',
    }, indent=2) + '\n')
    print(args.output)


if __name__ == '__main__':
    main()
