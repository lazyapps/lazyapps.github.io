"""Full-sampling, higher-resolution H3 material motion for the FondFont hero."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v3'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine',required=True,type=Path)
    parser.add_argument('--model',required=True,type=Path)
    args = parser.parse_args()
    output = ASSETS / 'paper-material-h3.mp4'
    if output.exists():
        parser.error('Preserve previous generations; use a new version.')
    anchor = ASSETS / 'paper-anchor.png'
    prompt_file = ASSETS / 'h3-prompt.txt'
    engine = args.engine.resolve()
    command = [str(engine),'-d',str(args.model.resolve()),'-p',prompt_file.read_text().strip(),
        '--width','768','--height','864','--render-width','512','--render-height','576',
        '--frames','53','--steps','20','--layers','50','--reuse','1',
        '--ssd-streaming','--seed','10062083','--first-frame',str(anchor),
        '--last-frame',str(anchor),'--profile','-o',str(output)]
    output.with_suffix('.generation.json').write_text(json.dumps({
        'model':'MiniMax-H3','command':command,'requestedFrames':53,
        'quality':'All 50 transformer blocks, all 20 denoiser evaluations; 512x576 internal, not a 352x416 draft.',
        'reference':'Imagegen product photograph; no generated device or UI.',
        'sources':[{'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
                   for path in [anchor,prompt_file]],
    },indent=2)+'\n')
    with output.with_suffix('.log').open('w') as log:
        subprocess.run(command,cwd=engine.parent,stdout=log,stderr=subprocess.STDOUT,check=True)
    print(output)


if __name__ == '__main__':
    main()
