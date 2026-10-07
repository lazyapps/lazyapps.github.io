"""Normalize the generated H3 reveal into an exact 21-frame compositing mask."""
import argparse
import json
from pathlib import Path
import subprocess

SECONDS = .7
FPS = 30
WIDTH, HEIGHT = 704, 1280


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    info = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(args.source)]))
    video = next(stream for stream in info['streams'] if stream['codec_type'] == 'video')
    numerator, denominator = map(float, video['r_frame_rate'].split('/'))
    last_time = (int(video['nb_frames']) - 1) / (numerator / denominator)
    # Re-time H3's accelerating reveal to settle gently at its destination.
    timing = f'acos(1-2*pow(clip((PTS-STARTPTS)*TB/{last_time},0,1),2))/PI*{SECONDS}/TB'
    graph = (
        f"setpts='{timing}',fps={FPS},"
        f'scale={WIDTH}:{HEIGHT},format=gray,lagfun=decay=1:planes=1,'
        "lut=y='clip((val-96)*255/63,0,255)',"
        'gblur=sigma=5,'
        "geq=lum='if(eq(N,0),0,if(gte(N,20),255,p(X,Y)))',setsar=1"
    )
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(args.source),
        '-vf', graph, '-t', str(SECONDS), '-an', '-c:v', 'ffv1', '-pix_fmt', 'gray', str(args.output)], check=True)
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(args.output),
        '-f', 'rawvideo', '-pix_fmt', 'gray', '-'])
    size = WIDTH * HEIGHT
    frames = [raw[index:index+size] for index in range(0, len(raw), size)]
    assert len(frames) == round(SECONDS * FPS)
    assert max(frames[0]) == 0 and min(frames[-1]) == 255
    assert all(all(right >= left for left, right in zip(previous, current))
               for previous, current in zip(frames, frames[1:]))
    stats = [{'frame': index, 'mean': sum(frame) / size,
              'featherFraction': sum(0 < pixel < 255 for pixel in frame) / size}
             for index, frame in enumerate(frames)]
    args.output.with_suffix('.json').write_text(json.dumps({
        'source': str(args.source), 'dimensions': [WIDTH, HEIGHT], 'duration': SECONDS,
        'fps': FPS, 'exactEndpoints': True, 'pixelwiseMonotonic': True,
        'retiming': timing, 'edgeFeatherSigma': 5, 'frames': stats,
    }, indent=2) + '\n')
    print(args.output)


if __name__ == '__main__':
    main()
