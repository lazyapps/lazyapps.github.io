"""Generate original YiYan paper scenes using the installed local MiniMax H3."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/yiyan/marketing-v2'

PROMPTS = {
    'prompt-notebook': '''A premium editorial product film in a warm ivory paper studio. Preserve this exact scene, camera framing, paper textures, coral notebook spine, and clean empty left 42 percent. The large horizontal blank ivory message card above the notebook glides steadily to the right and slightly upward, continuing its own uninterrupted journey. At the same time the two smaller peach paper strips gently descend in graceful curved trajectories and settle neatly onto the open notebook pages. The notebook remains stationary and physically coherent. Subtle page edges lift and settle in the warm breeze. Camera makes a slow subtle forward dolly, only about three percent; objects remain entirely in the right half. Clear independent movement of the original card and the learning strips below. Beautiful soft amber lighting slowly sweeps over the tactile ivory paper. Elegant deliberate motion with inertia and realistic contact shadows. No oscillation, no ping-pong, no reverse movement. No new objects, no people, no screens, no typography, no letters, no symbols, no arrows, no logos, no watermarks. Left side stays absolutely empty and light for exact separately composited typography. No cuts or flashes. Silent.''',
    'phrase-collection': '''A premium editorial product film of a personal learning collection, preserve this exact warm ivory paper scene. The blank cream cards softly fan apart in one smooth progressive sequence, each moving a small distance sideways like a beautifully organized personal phrase library. Thin coral paper tabs become visible along the edges. The lower notebook stays firmly on the surface. A single top sheet gently turns and settles; physically plausible paper movement and realistic soft contact shadows. The camera slowly moves forward and slightly to the right, a graceful continuous five degree arc, while keeping the entire collection within the right 58 percent. Warm sunrise light grazes tactile layered paper edges. No new objects, no human, no text, no typography, no glyphs, no numbers, no symbols, no interface, no devices. Keep the empty ivory LEFT 42 percent pristine for later exact text. Smooth inertia, no looping oscillation, no cuts, no flashing, no glitter. Silent.''',
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scene', choices=PROMPTS)
    parser.add_argument('--engine', type=Path, default=Path('/Users/realazy/tmp/h3.c/h3'))
    parser.add_argument('--model', type=Path, default=Path('/Users/realazy/.cache/huggingface/hub/models--MiniMaxAI--MiniMax-H3/snapshots/42ed227ee7df40d41602854ae760620d6eb651fe'))
    args = parser.parse_args()
    anchor = ASSETS / f'{args.scene}-anchor.png'
    output = ASSETS / f'{args.scene}-h3.mp4'
    if output.exists():
        parser.error('Preserve previous generations; choose a new version.')
    prompt = PROMPTS[args.scene]
    command = [str(args.engine), '-d', str(args.model), '-p', prompt,
               '--width', '1280', '--height', '704', '--render-width', '640',
               '--render-height', '352', '--frames', '65', '--steps', '20',
               '--layers', '50', '--reuse', '1', '--ssd-streaming',
               '--seed', '10082201' if args.scene == 'prompt-notebook' else '10082202',
               '--first-frame', str(anchor), '--profile', '-o', str(output)]
    output.with_suffix('.prompt.txt').write_text(prompt + '\n')
    output.with_suffix('.generation.json').write_text(json.dumps({
        'model': 'MiniMax-H3', 'mode': 'local Apple Silicon inference',
        'command': command, 'anchor': str(anchor.relative_to(ROOT)),
        'anchorSHA256': hashlib.sha256(anchor.read_bytes()).hexdigest(),
        'scope': 'Original paper motion; exact typography and authentic app screenshots composited separately.',
    }, indent=2) + '\n')
    with output.with_suffix('.log').open('w') as log:
        subprocess.run(command, cwd=args.engine.parent, stdout=log, stderr=subprocess.STDOUT, check=True)
    print(output, flush=True)

if __name__ == '__main__':
    main()
