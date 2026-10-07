"""Preserve H3 closure, lift only pre-contact housing, join identical poised frames."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v8'
PUBLIC = ROOT / 'public/v/fondfont'


def main():
    source = PUBLIC / 'hero-h3-v8.mp4'
    output = PUBLIC / 'hero-h3-v8-loop.mp4'
    if output.exists():
        raise RuntimeError('Preserve exported movies; use a new version.')
    # Stop the return source just before seating/red illumination; the installed
    # specimen layer is SVG and never runs backward or disappears.
    graph = (
        '[0:v]split=3[close][lift][hold];'
        '[close]setpts=PTS-STARTPTS[a];'
        '[lift]trim=end_frame=67,reverse,setpts=PTS-STARTPTS[b];'
        '[hold]trim=end_frame=1,loop=loop=17:size=1:start=0,setpts=N/(30*TB)[c];'
        '[a][b][c]concat=n=3:v=1:a=0[v]'
    )
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(source), '-filter_complex', graph,
                    '-map', '[v]', '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)], check=True)
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(output)]))
    (ASSETS / 'loop-manifest.json').write_text(json.dumps({
        'engine': 'MiniMax-H3',
        'source': str(source.relative_to(ROOT)),
        'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'return': 'Only the first 67 pre-contact frames reversed: rigid housing lifts; seated cartridge and SVG specimen remain. No propagation reversed.',
        'boundary': '18-frame poised hold, identical decoded source frame at start and end; original one-shot retained.',
        'probe': probe,
        'output': str(output.relative_to(ROOT)),
        'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
    }, indent=2) + '\n')
    print(output)


if __name__ == '__main__':
    main()
