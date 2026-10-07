"""Generate new paper and installation motion with the local MiniMax H3 model."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v2'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine',required=True,type=Path)
    parser.add_argument('--model',required=True,type=Path)
    parser.add_argument('--scene',required=True,choices=['hero','paper'])
    args = parser.parse_args()
    hero = args.scene == 'hero'
    first = ASSETS / ('hero-start.png' if hero else 'paper-anchor.png')
    last = ASSETS / ('hero-end.png' if hero else 'paper-anchor.png')
    prompt_file = ASSETS / f'{args.scene}-prompt.txt'
    output = ASSETS / f'{args.scene}-h3.mp4'
    if output.exists():
        parser.error('Preserve existing takes; choose a new scene version.')
    prompt = prompt_file.read_text().strip()
    engine = args.engine.resolve()
    command = [str(engine),'-d',str(args.model.resolve()),'-p',prompt,
        '--width',str(704 if hero else 768),'--height',str(832 if hero else 960),
        '--render-width',str(352 if hero else 256),'--render-height',str(416 if hero else 320),
        '--seconds',str(4.4 if hero else 3.2),'--steps','20','--layers','50','--reuse','2',
        '--ssd-streaming','--seed',str(10062072 if hero else 10062073),
        '--first-frame',str(first),'--last-frame',str(last),'--profile','-o',str(output)]
    output.with_suffix('.generation.json').write_text(json.dumps({
        'model':'MiniMax-H3','command':command,
        'sources':[{'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
                   for path in [first,last,prompt_file]],
        'screenPolicy':'Reserved stationary screen; only authentic recordings are composited here.' if hero else 'Decorative full-page paper illumination.',
    },indent=2)+'\n')
    with output.with_suffix('.log').open('w') as log:
        subprocess.run(command,cwd=engine.parent,stdout=log,stderr=subprocess.STDOUT,check=True)
    print(output)


if __name__ == '__main__':
    main()
