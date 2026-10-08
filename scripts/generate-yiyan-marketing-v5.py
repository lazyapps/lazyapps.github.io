"""Animate the agent-robot comedy anchors with the installed local MiniMax H3."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'scripts/assets/yiyan/marketing-v5'
PROMPTS = {
    'robots': """An original charming high-craft stylized 3D clay/vinyl animated film. Preserve the exact fictional adult woman at left, her dark bob, navy shirt, cream trousers, and ALL FIVE distinctive robot agents in the first frame, in their exact left-to-right positions: multicolor pixel-shaped Pi robot, coral starburst Claude robot, black and ivory knotted-head Codex robot, black square OpenCode robot, floating rainbow arch Antigravity robot. They are having a friendly conversation. The woman gently turns her open right palm toward the robots and gives one small conversational nod, her relaxed mouth moving very subtly. The five little robots listen with small asynchronous head tilts and friendly blinks; Pi makes a small hand gesture, Claude's sunburst stays rigid and recognizable, Codex's knot stays geometrically coherent, OpenCode gives a small nod, Antigravity bobs vertically only a few centimeters. Small grounded physical movements, warm comedic personalities. Keep every character's silhouette, material, color, position and identity consistent. Preserve five robots exactly, no extra or missing characters. Keep the upper quarter clear and the floor uncluttered. Stable locked camera with an almost imperceptible slow forward drift. No cuts, no new objects, no generated text, no captions, no symbols, no speech bubbles, no logos added. Do not morph the robot heads. No extra hands, no broken fingers, no flicker. Silent.""",
    'trump-chat': """An unmistakably fictional high-craft 3D clay/vinyl comedy. Preserve this exact adult East Asian woman with dark bob, navy casual shirt, cream outfit at the left, and this recognizable CARTOON CARICATURE of Donald Trump with golden swept hair, exaggerated expressive eyebrows, navy suit, white shirt and red tie at the right. They are chatting face to face in a generic warm ivory studio, not a political event. The woman makes one small confident open-palm conversational gesture and a subtle friendly speaking expression. Cartoon Trump listens, then gives one small approving nod and a restrained warm smile. No broad gestures, no handshakes, no raising arms. Keep hands naturally visible and anatomically stable, faces coherent, exactly two adult people. Fixed calm medium two-shot, warm light, tactile clay material, playful conversational chemistry. No new objects, no additional characters, no flags, no seals, no podium, no campaign signs, no text or letters, no captions, no speech bubbles. No lip-sync attempt, no imitation audio. Silent.""",
    'win': """An unmistakably fictional high-craft 3D clay/vinyl animated comedy celebration. Preserve the exact two adult characters in this reference image: the East Asian woman with dark bob and navy shirt on left, recognizable cartoon caricature Donald Trump with golden swept hair, navy suit and red tie on right. BOTH are ALREADY giving clear single thumbs-up toward the camera, and must keep these hands and thumbs stable throughout the whole shot. They share a cheerful warm grin, give a very small synchronized confident nod and gently lean forward by a few centimeters, keeping a playful victorious pose. Trump's golden hair, eyebrows, face and tie stay consistent. Exactly two hands visible in thumbs-up, no duplicated fingers or fused hands. Keep all hands firmly shaped and stationary in their gesture. Soft celebratory studio lighting, warm ivory clay-film set. Camera very slowly pushes forward two percent. Leave upper third clear for composited punchline, no new objects, no other people, no flags, no political props, no text, no captions, no speech bubbles, no watermark. Silent.""",
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
        '--seed', str(10082501 + list(PROMPTS).index(scene)), '--first-frame', str(anchor),
        '--profile', '-o', str(output)]
    output.with_suffix('.prompt.txt').write_text(PROMPTS[scene] + '\n')
    output.with_suffix('.generation.json').write_text(json.dumps(dict(model='MiniMax-H3',
        mode='local Apple Silicon inference', command=command, anchor=str(anchor.relative_to(ROOT)),
        anchorSHA256=hashlib.sha256(anchor.read_bytes()).hexdigest(),
        scope='Fictional animated parody; true brand badges and editorial idiomatic-English feedback composited separately.'), indent=2) + '\n')
    with output.with_suffix('.log').open('w') as log:
        subprocess.run(command, cwd=engine.parent, stdout=log, stderr=subprocess.STDOUT, check=True)
    print(output, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scene', choices=[*PROMPTS, 'all'])
    args = parser.parse_args()
    for scene in PROMPTS if args.scene == 'all' else [args.scene]:
        generate(scene)
