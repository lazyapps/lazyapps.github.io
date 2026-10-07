"""Export the H3 installation metaphor as one short pass with a settled result."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v4'
TARGET = ROOT / 'public/v/fondfont'
SECONDS = 4.75


def run(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-n', *map(str, args)], check=True)


def main():
    source = ASSETS / 'font-enters-work-h3.mp4'
    end = ASSETS / 'end-anchor.png'
    output = TARGET / 'hero-h3-v4.mp4'
    if output.exists():
        raise SystemExit('Preserve exports; use a new version.')
    seconds = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=nw=1:nk=1', str(source)]))
    white = "lutrgb=r='min(255,val*255/250)':g='min(255,val*255/250)':b='min(255,val*255/250)'"
    run('-i', source, '-loop', '1', '-framerate', '24', '-i', end,
        '-filter_complex',
        f'[0:v]setpts={4.4/seconds}*(PTS-STARTPTS),minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,'
        f'{white},tpad=stop_mode=clone:stop_duration=1,format=yuv420p[motion];'
        f'[1:v]{white},format=yuv420p[result];'
        f'[motion][result]xfade=transition=fade:duration=0.35:offset=4.1,trim=duration={SECONDS}[out]',
        '-map', '[out]', '-t', SECONDS, '-an', '-c:v', 'libx264', '-preset', 'slow',
        '-crf', '20', '-threads', '2', '-movflags', '+faststart', output)
    run('-i', end, '-vf', white, '-frames:v', '1', '-q:v', '2', output.with_suffix('.jpg'))
    output.with_suffix('.json').write_text(json.dumps({
        'model': 'MiniMax-H3', 'referenceMode': 'Built-in imagegen paired conceptual scenes',
        'silent': True, 'sharedAcrossLocales': True, 'seconds': SECONDS,
        'playback': 'One pass, final composition held; no looping or playback controls',
        'scope': 'Conceptual font file entering iOS font library, then that installed font becoming usable in document and presentation typography. This is not an app/OS recording and does not depict system UI font replacement.',
        'sources': [{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                    for p in [source, ASSETS / 'start-anchor.png', end]],
    }, indent=2) + '\n')
    print(output)


if __name__ == '__main__':
    main()
