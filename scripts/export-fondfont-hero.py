"""Optimize the H3 installation take, hold its result, and reset the loop gently."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation'
TARGET = ROOT / 'public/v/fondfont'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    first = ASSETS / 'transfer-start-v1.png'
    last = ASSETS / 'transfer-end-v1.png'
    TARGET.mkdir(parents=True, exist_ok=True)
    output = TARGET / 'hero-install-h3-v1.mp4'
    if output.exists():
        parser.error('The published take exists. Preserve it and use a new version.')
    info = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(source)]))
    duration = float(info['format']['duration'])
    hold = 7.5 - duration
    with Image.open(last) as image:
        image.convert('RGB').save(TARGET / 'hero-install-h3-v1.jpg', quality=92, optimize=True)
    # Only the small destination label is composited exactly; H3 supplies the motion.
    with Image.open(first) as image:
        image.crop((248, 215, 368, 276)).save(ASSETS / 'ios-label-v1.png')
    graph = (
        f'[0:v]setpts=PTS-STARTPTS,fps=24,scale=640:832,setsar=1,'
        "geq=r='if(gt(g(X,Y)-r(X,Y),12),g(X,Y),r(X,Y))':"
        "g='if(gt(g(X,Y)-r(X,Y),12),g(X,Y)*0.40,g(X,Y))':"
        "b='if(gt(g(X,Y)-r(X,Y),12),g(X,Y)*0.28,b(X,Y))',format=yuv420p,"
        f'tpad=stop_mode=clone:stop_duration={hold},trim=duration=7.5[main];'
        '[1:v]fps=24,setsar=1,format=yuv420p[reset];'
        '[main][reset]xfade=transition=fade:duration=0.5:offset=7[loop];'
        '[loop][2:v]overlay=x=248:y=215:shortest=1,trim=duration=7.5,format=yuv420p[out]'
    )
    subprocess.run(['ffmpeg', '-v', 'error', '-n', '-i', str(source),
        '-loop', '1', '-framerate', '24', '-i', str(first),
        '-loop', '1', '-framerate', '24', '-i', str(ASSETS / 'ios-label-v1.png'),
        '-filter_complex', graph, '-map', '[out]', '-an', '-t', '7.5',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-threads', '2',
        '-movflags', '+faststart', str(output)], check=True)
    (TARGET / 'hero-install-h3-v1.json').write_text(json.dumps({
        'model': 'MiniMax-H3', 'duration': 7.5, 'fps': 24, 'silent': True,
        'sharedAcrossLocales': True, 'illustration': True,
        'description': 'Font-file installation in the iOS library, followed by abstract document and presentation specimens. Not an operating-system or third-party app screen.',
        'finishing': 'H3 movement; green transfer signals graded to brand vermilion; exact iOS destination label; hold completed state; 0.5-second dissolve back to the start, without reversing installation.',
        'sources': [{'path': str(path.relative_to(ROOT)),
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                    for path in [source, first, last]],
        'bytes': output.stat().st_size,
    }, ensure_ascii=False, indent=2) + '\n')
    print(output)


if __name__ == '__main__':
    main()
