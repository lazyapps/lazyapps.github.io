"""Animate the original lifestyle anchors with the installed local MiniMax H3."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/yiyan/marketing-v4'
PROMPTS = {
    'work': '''Cinematic candid lifestyle film, preserve the exact woman, navy cotton overshirt, hands, laptop, coral ceramic cup, room and composition in this first frame. Real natural human movement: she casually types a short sentence on the keyboard with small alternating finger motions, then her right hand relaxes briefly while her left hand stays near the keys. Her shoulders gently breathe and a few dark hair strands shift almost imperceptibly. The laptop remains solid and stationary, with no readable screen content. The coral cup stays firmly on the desk. Warm afternoon daylight, quiet focused mood, natural skin and cloth textures. Camera makes a very slow subtle forward dolly of about two percent, without any tilt. One continuous restrained candid shot, grounded physical realism. Keep exactly two hands and five fingers on each, no extra fingers, no distorted wrists, no duplicated arms. No new objects, no additional people, no face reveal, no text, no subtitles, no symbols, no logos, no magical effects, no cuts, no speed ramp, no flicker. Silent.''',
    'cafe': '''Cinematic candid lifestyle film, preserve the exact two adult women, café, navy cotton overshirt, canvas tote, cups and warm morning light in this first frame. This is a natural friendly goodbye after a conversation. The navy-shirt woman on the right gently tightens her grip on the canvas bag strap, lifts the bag a few centimeters from her lap and shifts her shoulders slightly forward as if preparing to leave. She looks warmly at her friend and gives a small relaxed parting nod; her smile is subtle and genuine, never exaggerated. The friend on the left responds with one small acknowledging nod. Keep both seated and keep the main woman's mouth relaxed, without trying to lip sync. Two quiet human actions, clear communication and real everyday confidence. The camera makes a very subtle three-degree rightward arc with steady framing. Natural breathing, realistic cloth and hair motion, shallow photographic depth of field. Cups and table stay firmly in place. Anatomically stable hands, coherent faces and consistent identities. No extra people, no new objects, no standing up, no broad waving, no exaggerated expression, no text, no letters, no logos, no subtitles, no magical effects, no cuts, no flashing. Silent.''',
}


def generate(scene):
    engine = Path('/Users/realazy/tmp/h3.c/h3')
    model = Path('/Users/realazy/.cache/huggingface/hub/models--MiniMaxAI--MiniMax-H3/snapshots/42ed227ee7df40d41602854ae760620d6eb651fe')
    anchor = ASSETS / f'{scene}-anchor.png'
    output = ASSETS / f'{scene}-h3.mp4'
    if output.exists():
        raise RuntimeError(f'Preserve earlier generations: {output}')
    command = [str(engine), '-d', str(model), '-p', PROMPTS[scene],
        '--width', '1280', '--height', '704', '--render-width', '640', '--render-height', '352',
        '--frames', '65', '--steps', '20', '--layers', '50', '--reuse', '2', '--ssd-streaming',
        '--seed', '10082401' if scene == 'work' else '10082402', '--first-frame', str(anchor),
        '--profile', '-o', str(output)]
    output.with_suffix('.prompt.txt').write_text(PROMPTS[scene] + '\n')
    output.with_suffix('.generation.json').write_text(json.dumps(dict(model='MiniMax-H3',
        mode='local Apple Silicon inference', command=command, anchor=str(anchor.relative_to(ROOT)),
        anchorSHA256=hashlib.sha256(anchor.read_bytes()).hexdigest(),
        scope='Original lifestyle footage; editorial subtitles and genuine brand composited separately.'), indent=2) + '\n')
    with output.with_suffix('.log').open('w') as log:
        subprocess.run(command, cwd=engine.parent, stdout=log, stderr=subprocess.STDOUT, check=True)
    print(output, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scene', choices=[*PROMPTS, 'all'])
    args = parser.parse_args()
    for scene in PROMPTS if args.scene == 'all' else [args.scene]:
        generate(scene)
