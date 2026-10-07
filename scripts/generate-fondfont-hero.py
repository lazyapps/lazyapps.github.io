"""Generate a preserved MiniMax H3 font-installation take with exact anchors."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', required=True, type=Path)
    parser.add_argument('--model', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error('Use a new output path to preserve earlier generations.')
    output.parent.mkdir(parents=True, exist_ok=True)
    prompt_file = ASSETS / 'transfer-h3-v1-prompt.txt'
    prompt = prompt_file.read_text().strip()
    first, last = [ASSETS / f'transfer-{state}-v1.png' for state in ['start', 'end']]
    engine = args.engine.resolve()
    command = [str(engine), '-d', str(args.model.resolve()), '-p', prompt,
               '--width', '640', '--height', '832', '--render-width', '320', '--render-height', '416',
               '--seconds', '4.4', '--steps', '20', '--layers', '50', '--reuse', '2',
               '--ssd-streaming', '--seed', '10062061', '--first-frame', str(first),
               '--last-frame', str(last), '--profile', '-o', str(output)]
    output.with_suffix('.generation.json').write_text(json.dumps({
        'model': 'MiniMax-H3', 'command': command,
        'sources': [{'path': str(path.relative_to(ROOT)),
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                    for path in [first, last, prompt_file]],
        'semantics': 'Font file → completed iOS installation → abstract document and presentation specimens',
    }, indent=2) + '\n')
    with output.with_suffix('.log').open('w') as log:
        subprocess.run(command, cwd=engine.parent, stdout=log, stderr=subprocess.STDOUT, check=True)
    print(output)


if __name__ == '__main__':
    main()
