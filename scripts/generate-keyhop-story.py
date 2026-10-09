"""Animate the original KeyHop fox comedy with the installed LOCAL MiniMax H3.

First-frame art: built-in imagegen. App/keyboard graphics are composed separately.
Generations are never overwritten; command, seed, model path and hashes are saved.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/keyhop/story-v1'
ENGINE = Path('/Users/realazy/tmp/h3.c/h3')
MODEL = Path('/Users/realazy/.cache/huggingface/hub/models--MiniMaxAI--MiniMax-H3/snapshots/42ed227ee7df40d41602854ae760620d6eb651fe')
PROMPTS = {
    'chase': '''An original charming lively handmade miniature clay animated comedy. Preserve this EXACT orange fox, cream muzzle, cream tail tip, thick purple knitted sweater, ears, eyes, proportions and warm ivory lavender studio. One continuous locked-camera shot. The fox eagerly tries to reach something just to its right: makes one little quick step right and reaches with its right paw, misses, recoils with a funny disappointed eyebrow expression, then makes a second short reaching attempt a little farther right and misses again. Two readable comic near misses, a small frustrated foot stamp at the end. The orange tail swishes with the motion, ears tilt and eyes are expressive. The tiny golden idea spark above the fox stays gently glowing and follows its head throughout, never disappears. Small grounded lively movements, no running offscreen, keep the fox within the middle half. Keep all foreground below its feet empty for later app props. The set and low platform stay rigid, no objects move. No cuts, no new characters, no new props, no text, no letters, no symbols, no app UI. Exactly one fox, two arms, two legs, one tail, stable coherent anatomy. Do not turn it into a dog. Silent.''',
    'hop': '''A delightful original handmade miniature clay stop-motion style comedy. Preserve this exact orange fox with cream muzzle and tail tip and thick purple knitted sweater in this warm ivory lavender studio. The fox spots its destination TO THE LEFT, gives a tiny confident pleased smile, crouches and performs ONE joyful small sideways hop to the LEFT about one body-width. Both feet lift briefly and land together, knees flex gently on landing, then the fox settles in a proud happy pose looking left. Its fluffy tail follows with one playful bounce. The glowing little golden idea spark stays alive above its head and moves with it. Clear anticipation, airborne hop and satisfying grounded landing. Keep fox face, sweater and proportions stable, no body morphing, no extra limbs, no disappearing ears, exactly one tail. Lock camera, static stage, keep bottom foreground empty for composited keyboard props. No cuts, no additional characters, no new objects, no text, no letters, no symbols, no app UI. Silent.''',
    'flow': '''A lively warm original miniature clay animated film. Preserve this exact orange fox in the thick purple knitted sweater, cream muzzle and tail tip, the solid little ivory desk, small lavender laptop, coral mug and golden idea spark, and warm ivory lavender studio. The fox happily continues its OWN work: looks down at the laptop and makes small alternating paw taps typing, then pauses a beat, looks up toward camera with a wonderfully relieved proud grin and a small pleased nod. Its tail gives one gentle satisfied wag behind the chair. The golden idea spark above its head remains gently glowing throughout, never materializes from nothing. Exactly one fox with two paws and two legs, stable laptop, cup and desk, no morphing anatomy. Fixed camera with barely perceptible slow forward drift, no cuts, no new props, no additional people, no magical transformations, no text or generated letters on the laptop, no labels, no logos. Silent.''',
}


def generate(scene):
    anchor = ASSETS / f'{scene}-anchor.png'
    output = ASSETS / f'{scene}-h3.mp4'
    if output.exists():
        raise RuntimeError(f'Preserve existing generation: {output}')
    command = [str(ENGINE), '-d', str(MODEL), '-p', PROMPTS[scene],
        '--width', '1280', '--height', '704', '--render-width', '640', '--render-height', '352',
        '--frames', '65', '--steps', '20', '--layers', '50', '--reuse', '2', '--ssd-streaming',
        '--seed', str(10092601 + list(PROMPTS).index(scene)), '--first-frame', str(anchor),
        '--profile', '-o', str(output)]
    output.with_suffix('.prompt.txt').write_text(PROMPTS[scene] + '\n')
    output.with_suffix('.generation.json').write_text(json.dumps(dict(
        model='MiniMax-H3', mode='local Apple Silicon inference', command=command,
        anchor=str(anchor.relative_to(ROOT)), anchorSHA256=hashlib.sha256(anchor.read_bytes()).hexdigest(),
        scope='Original fictional fox comedy. Authentic app icons and exact home-row tiles composed separately.'), indent=2) + '\n')
    print(f'Generating {scene} locally', flush=True)
    with output.with_suffix('.log').open('w') as log:
        subprocess.run(command, cwd=ENGINE.parent, stdout=log, stderr=subprocess.STDOUT, check=True)
    print(output, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scene', choices=[*PROMPTS, 'all'])
    args = parser.parse_args()
    for scene in PROMPTS if args.scene == 'all' else [args.scene]:
        generate(scene)
