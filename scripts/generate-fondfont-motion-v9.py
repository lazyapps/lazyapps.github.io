"""Generate the two-document shared font-library scene with genuine MiniMax H3."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/fondfont/animation/v9'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', required=True, type=Path)
    parser.add_argument('--model', required=True, type=Path)
    args = parser.parse_args()
    movie = ASSETS / 'shared-documents-h3.mp4'
    if movie.exists():
        parser.error('Preserve generations; use a new version.')
    start, end = [ASSETS / f'{state}-anchor.png' for state in ['start', 'end']]
    prompt = ASSETS / 'h3-prompt.txt'
    engine = args.engine.resolve()
    command = [str(engine), '-d', str(args.model.resolve()), '-p', prompt.read_text().strip(),
        '--width', '768', '--height', '480', '--render-width', '512', '--render-height', '320',
        '--frames', '65', '--steps', '20', '--layers', '50', '--reuse', '1', '--ssd-streaming',
        '--seed', '10062109', '--first-frame', str(start), '--last-frame', str(end),
        '--profile', '-o', str(movie)]
    movie.with_suffix('.generation.json').write_text(json.dumps({
        'model': 'MiniMax-H3', 'command': command, 'requestedFrames': 65,
        'referenceMode': 'Built-in imagegen full-sheet paired anchors, two blank document planes',
        'glyphStrategy': 'Exact glyph outlines from three real selected families per locale; deterministic install/library and document typography',
        'sources': [{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                    for p in [start, end, prompt]],
    }, indent=2) + '\n')
    with movie.with_suffix('.log').open('w') as log:
        subprocess.run(command, cwd=engine.parent, stdout=log, stderr=subprocess.STDOUT, check=True)
    print(movie)


if __name__ == '__main__':
    main()
