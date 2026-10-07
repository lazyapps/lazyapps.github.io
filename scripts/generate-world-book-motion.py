"""Generate archived World Book motion assets with the local MiniMax H3 engine."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/world-book/animation'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', required=True, type=Path)
    parser.add_argument('--model', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--prompt-file', type=Path, default=ASSETS / 'grand-assembly-h3-prompt.txt')
    parser.add_argument('--first-frame', type=Path, default=ASSETS / 'grand-assembly-first-v1.png')
    parser.add_argument('--last-frame', type=Path)
    parser.add_argument('--width', type=int, default=704)
    parser.add_argument('--height', type=int, default=1280)
    parser.add_argument('--render-width', type=int, default=352)
    parser.add_argument('--render-height', type=int, default=640)
    parser.add_argument('--seconds', type=float, default=6.5)
    parser.add_argument('--seed', type=int, default=10062030)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error('Choose a new output path; existing generated videos are preserved.')
    output.parent.mkdir(parents=True, exist_ok=True)
    engine, model = args.engine.resolve(), args.model.resolve()
    first = args.first_frame.resolve()
    prompt = args.prompt_file.read_text().strip()
    cmd = [str(engine), '-d', str(model), '-p', prompt,
           '--width', str(args.width), '--height', str(args.height),
           '--render-width', str(args.render_width), '--render-height', str(args.render_height),
           '--seconds', str(args.seconds), '--steps', '20', '--layers', '50', '--reuse', '2',
           '--seed', str(args.seed), '--first-frame', str(first), '--profile', '-o', str(output)]
    anchors = {'first': {'path': str(first), 'sha256': hashlib.sha256(first.read_bytes()).hexdigest()}}
    if args.last_frame:
        last = args.last_frame.resolve()
        cmd += ['--last-frame', str(last)]
        anchors['last'] = {'path': str(last), 'sha256': hashlib.sha256(last.read_bytes()).hexdigest()}
    output.with_suffix('.prompt.txt').write_text(prompt + '\n')
    output.with_suffix('.generation.json').write_text(json.dumps({
        'model': 'MiniMax-H3', 'engine': str(engine), 'command': cmd, 'anchors': anchors,
        'requestedSeconds': args.seconds, 'output': [args.width, args.height],
        'internal': [args.render_width, args.render_height], 'steps': 20, 'reuse': 2, 'layers': 50,
    }, indent=2) + '\n')
    with output.with_suffix('.log').open('w') as log:
        subprocess.run(cmd, cwd=engine.parent, stdout=log, stderr=subprocess.STDOUT, check=True)
    print(output)


if __name__ == '__main__':
    main()
